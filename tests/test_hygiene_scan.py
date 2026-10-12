"""The hygiene scanner finds planted problems (all assembled at run time) and prints no matched text."""
# the hashed host-fragment check is
# tested with an obviously synthetic string patched into the hash set; no real fragment is built or stored here.
import hashlib
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "hygiene_scan.py"


def _load():
    spec = importlib.util.spec_from_file_location("hygiene_scan", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_scanner_finds_planted_issues(tmp_path, capsys, monkeypatch):
    hs = _load()
    home = "/" + "Users" + "/someone/project"
    key = "s" + "k-" + "Q" * 24
    ip = "192." + "168.1.20"
    (tmp_path / "a.md").write_text(f"see {home}\nip {ip}\n")
    (tmp_path / "b.py").write_text(f'TOKEN = "{key}"\n')
    (tmp_path / "arr.npz").write_bytes(b"\x00")
    (tmp_path / "rec.json").write_text('{"dia_id": "D1:1"}')
    (tmp_path / "clean.py").write_text("x = 1\n")
    # A virtual protected path tests detection without creating or opening it.
    class ProtectedFixture:
        name = ".env"
        suffix = ""

        def relative_to(self, root):
            assert root == tmp_path
            return Path(self.name)

        def is_symlink(self):
            return False

        def stat(self):
            raise AssertionError("protected fixture must be rejected before stat")

        def read_text(self, *args, **kwargs):
            raise AssertionError("protected fixture must never be opened")

    original_iter_files = hs.iter_files

    def fixture_files(root):
        yield from original_iter_files(root)
        if root == tmp_path:
            yield ProtectedFixture()

    monkeypatch.setattr(hs, "iter_files", fixture_files)
    found = hs.scan(tmp_path, [])
    kinds = {(k, r.split(":")[0]) for k, r, _ in found}
    assert ("home_path", "a.md") in kinds
    assert ("internal_host", "a.md") in kinds
    assert ("key_shape", "b.py") in kinds
    assert ("protected_file", ".env") in kinds
    assert ("data_file", "arr.npz") in kinds
    assert ("dialogue_schema", "rec.json") in kinds
    assert not any(r.startswith("clean.py") for _, r, _ in found)
    assert hs.main(["--root", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert key not in out and home not in out


def test_corpus_overlap_reports_counts_only(tmp_path, capsys):
    hs = _load()
    repo = tmp_path / "repo"
    repo.mkdir()
    sentence = "memaudit synthetic shingle probe alpha bravo charlie delta echo foxtrot golf hotel india juliet"
    (repo / "doc.md").write_text(f"intro {sentence} outro\n")
    corpus = tmp_path / "corpus.txt"
    corpus.write_text(f"prefix {sentence} suffix")
    found = hs.scan(repo, [corpus])
    assert any(k == "corpus_overlap" and r.startswith("doc.md") for k, r, _ in found)
    hs.main(["--root", str(repo), "--corpus", str(corpus)])
    assert "alpha bravo charlie" not in capsys.readouterr().out


def test_repository_itself_is_clean():
    hs = _load()
    found = hs.scan(SCRIPT.parents[1], [])
    assert found == [], [(k, r, n) for k, r, n in found]


def test_overlap_stream_preserves_tokens_across_chunk_edges(tmp_path):
    hs = _load()
    repo = tmp_path/"repo"; repo.mkdir()
    sentence = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen"
    (repo/"sample.md").write_text(sentence)
    corpus = tmp_path/"input.txt"
    corpus.write_text("!"*65531 + sentence)
    assert hs.corpus_overlap({repo/"sample.md": sentence}, [corpus])[repo/"sample.md"] == len(hs.shingles(sentence))


def test_punctuation_only_is_not_a_word_overlap(tmp_path):
    hs = _load()
    punctuation = "' " * (hs.SHINGLE + 5)
    corpus = tmp_path / "punctuation.txt"
    corpus.write_text(punctuation)
    assert hs.shingles(punctuation) == set()
    assert hs.corpus_overlap({tmp_path / "mapping.py": punctuation}, [corpus]) == {}


def test_real_overlap_survives_punctuation_and_chunk_boundary(tmp_path):
    hs = _load()
    words = ["synthetic", "review", "checks", "don't", "lose", "real", "word", "matches", "across", "quoted", "chunks"]
    sentence = " ".join(words)
    separated = " ' '' ' ".join(words)
    corpus = tmp_path / "words.txt"
    corpus.write_text("!" * 65531 + separated)
    candidate = tmp_path / "candidate.md"
    assert hs.shingles(separated) == hs.shingles(sentence)
    assert hs.corpus_overlap({candidate: sentence}, [corpus])[candidate] == len(hs.shingles(sentence))


SYNTHETIC_HOST = "example-internal-host"


def test_hashed_fragment_detects_synthetic_string_split_or_joined(tmp_path, capsys, monkeypatch):
    hs = _load()
    digest = hashlib.sha256(SYNTHETIC_HOST.encode()).hexdigest()
    monkeypatch.setattr(hs, "HASHED_HOST_FRAGMENTS", {(len(SYNTHETIC_HOST), digest)})
    (tmp_path / "joined.md").write_text(f"intro\nhost x.{SYNTHETIC_HOST}.example\n")
    (tmp_path / "upper.md").write_text(SYNTHETIC_HOST.upper() + "\n")
    (tmp_path / "plus.py").write_text('HOST = "example-" + "internal-host"\n')
    (tmp_path / "quotes.py").write_text("HOST = 'example-int' + 'ernal-host'\n")
    (tmp_path / "implicit.py").write_text('HOST = (\n    "example-"\n    "internal-host"\n)\n')
    (tmp_path / "continued.py").write_text('HOST = "example-internal" \\\n    "-host"\n')
    (tmp_path / "spaced.md").write_text("example internal host\n")
    (tmp_path / "partial.py").write_text('A = "example-internal"\nB = 1\n')
    found = hs.scan(tmp_path, [])
    hits = {(r, n) for k, r, n in found if k == "internal_host"}
    assert ("joined.md", 2) in hits
    assert ("upper.md", 1) in hits
    assert ("plus.py", 1) in hits
    assert ("quotes.py", 1) in hits
    assert ("implicit.py", 2) in hits
    assert ("continued.py", 1) in hits
    assert {r for r, _ in hits} == {"joined.md", "upper.md", "plus.py", "quotes.py", "implicit.py", "continued.py"}
    assert hs.main(["--root", str(tmp_path)]) == 1
    assert SYNTHETIC_HOST not in capsys.readouterr().out.lower()


def test_real_fragment_set_is_hash_only_and_unpatched():
    hs = _load()
    assert hs.HASHED_HOST_FRAGMENTS
    for length, digest in hs.HASHED_HOST_FRAGMENTS:
        assert isinstance(length, int) and len(digest) == 64 and int(digest, 16) >= 0
    assert hs.hashed_fragment_hits(SYNTHETIC_HOST) == []
