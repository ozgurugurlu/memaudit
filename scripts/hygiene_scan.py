#!/usr/bin/env python3
"""Release-hygiene scan for the memaudit repository (stdlib only; never prints matched text).

Checks every file under the repository root (skipping VCS, caches, virtual environments and build output):

  home_path        absolute home-directory paths (macOS, Linux, Windows forms)
  internal_host    internal host names: hashed fragments (no plaintext in the repo; contiguous or assembled from
                   quoted pieces), reserved internal TLDs, private IPv4 literals
  key_shape        key-shaped strings (provider key prefixes, bearer tokens, private-key blocks, key assignments)
  env_file         any file named .env or *.env (reported by name only)
  data_file        data / model artefacts (.parquet, .npz, .npy, .joblib, .pkl, .arrow, .sqlite, large .json/.jsonl/.csv)
  dialogue_schema  benchmark dialogue-schema keys inside non-code files (a sign of pasted benchmark records)
  corpus_overlap   (only with --corpus) 10-word shingles shared with user-supplied benchmark files

Output: aggregate counts only; callers can inspect relative finding locations without matched text.
Exit status 1 if anything is found, 0 otherwise.
"""
from __future__ import annotations

import argparse
import bisect
from collections import deque
import hashlib
import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache", "build", "dist", "runs", ".mypy_cache"}
SKIP_SUFFIXES = (".egg-info",)
TEXT_SUFFIXES = {".py", ".md", ".txt", ".toml", ".cfg", ".ini", ".yml", ".yaml", ".json", ".jsonl", ".csv", ".sh", ".cff", ".rst", ""}
CODE_SUFFIXES = {".py", ".sh", ".toml"}
DATA_SUFFIXES = {".parquet", ".npz", ".npy", ".joblib", ".pkl", ".pickle", ".arrow", ".feather", ".sqlite", ".db", ".h5"}
LARGE_TEXT_BYTES = 50_000
LARGE_TEXT_SUFFIXES = {".json", ".jsonl", ".csv"}

# Patterns are assembled from pieces so that this file does not match itself.
_U = "Us" + "ers"
HOME_PATH = re.compile("/" + _U + r"/[A-Za-z0-9._-]+|/home/[a-z_][a-z0-9_-]*/|\b[A-Za-z]:\\{1,2}" + _U + r"\\{1,2}")
PRIVATE_IP = re.compile(r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b")
INTERNAL_TLD = re.compile(r"\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:internal|corp|intranet|lan)\b", re.I)
# (length, sha256 of the lower-cased fragment): internal host-name fragments named by the OSS plan, kept out of the repo in plain text.
HASHED_HOST_FRAGMENTS = {(11, "962208261b20a30a353c00b6dd1aa34c12221caa51f07954ade0f95b4f96b7c3")}
KEY_SHAPES = [
    re.compile("s" + r"k-[A-Za-z0-9_\-]{16,}"),
    re.compile("AI" + r"za[0-9A-Za-z_\-]{20,}"),
    re.compile(r"(?:gh" + r"p|gho|ghs|github_pat)_[A-Za-z0-9_]{20,}"),
    re.compile("xo" + r"x[abprs]-[A-Za-z0-9\-]{10,}"),
    re.compile("AK" + r"IA[0-9A-Z]{16}"),
    re.compile("-----BEGIN " + r"(?:RSA |EC |OPENSSH |)PRIVATE KEY-----"),
    re.compile(r"(?i)bear" + r"er\s+[A-Za-z0-9._\-~+/=]{20,}"),
    re.compile(r"""(?i)(?:api[-_]?key|secret|passw(?:or)?d|access[-_]?token)\s*[:=]\s*['"][A-Za-z0-9/+_\-.]{16,}['"]"""),
]
DIALOGUE_KEYS = re.compile(r'"(?:dia_id|haystack_sessions|haystack_session_ids|speaker_a|speaker_b|session_\d+_date_time|blip_caption|answer_session_ids)"\s*:')
WORD = re.compile(r"[a-z0-9']+")
SHINGLE = 10


def protected(path: Path) -> bool:
    name = path.name.lower()
    return name == ".env" or name.endswith(".env") or name.startswith(".env.") or path.suffix.lower() in {".key", ".pem"} or bool(re.search(r"(^|[._-])(credentials?|secrets?|tokens?)([._-]|$)", name))


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.endswith(SKIP_SUFFIXES)]
        for fn in filenames:
            yield Path(dirpath) / fn


# string-concatenation seams
# ("a" + "b", "a" "b", "a" \ newline "b", either quote style) are removed before a second hashed pass, so a fragment
# assembled from pieces in source code is detected as well as a contiguous one.
_SEAM = re.compile(r"""["']\s*(?:\+|\\)?\s*["']""")


def _without_seams(text: str) -> tuple[str, list[tuple[int, int]]]:
    """Text with concatenation seams removed, plus (compact_start, original_start) segment starts for mapping back."""
    parts, segs, pos, cpos = [], [], 0, 0
    for m in _SEAM.finditer(text):
        segs.append((cpos, pos))
        parts.append(text[pos:m.start()])
        cpos += m.start() - pos
        pos = m.end()
    segs.append((cpos, pos))
    parts.append(text[pos:])
    return "".join(parts), segs


def _hits_in(low: str) -> list[int]:
    hits = []
    for length, digest in HASHED_HOST_FRAGMENTS:
        for i in range(0, max(0, len(low) - length + 1)):
            if hashlib.sha256(low[i:i + length].encode("utf-8", "surrogatepass")).hexdigest() == digest:
                hits.append(i)
    return hits


def hashed_fragment_hits(text: str) -> list[int]:
    """Offsets where a hashed fragment occurs, contiguous or split by string-concatenation seams."""
    hits = set(_hits_in(text.lower()))
    compact, segs = _without_seams(text)
    if len(segs) > 1:
        starts = [c for c, _ in segs]
        for i in _hits_in(compact.lower()):
            k = bisect.bisect_right(starts, i) - 1
            hits.add(segs[k][1] + (i - segs[k][0]))
    return sorted(hits)


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def shingles(text: str) -> set[int]:
    # Apostrophes may occur inside words; apostrophe-only runs are not words.
    w = [word for word in WORD.findall(text.lower()) if word.strip("'")]
    return {hash(tuple(w[i:i + SHINGLE])) for i in range(len(w) - SHINGLE + 1)}


def corpus_overlap(repo_texts: dict[Path, str], corpus: list[Path]) -> dict[Path, int]:
    index: dict[int, set[Path]] = {}
    for p, t in repo_texts.items():
        for h in shingles(t):
            index.setdefault(h, set()).add(p)
    found: dict[Path, int] = {}
    for c in corpus:
        if not c.is_file():
            raise ValueError("corpus overlap accepts explicit files only")
        files = [c]
        for f in files:
            if protected(f):
                raise ValueError("protected files cannot be overlap inputs")
            # Stream explicit corpus files: memory is bounded by the repository
            # index and input chunk, not by benchmark size. Only matching hashes
            # are retained, never corpus text or nonmatching corpus shingles.
            seen = set()
            with f.open(encoding="utf-8", errors="ignore") as stream:
                window = deque(maxlen=SHINGLE)
                carry = ""
                while True:
                    chunk = stream.read(65536)
                    if not chunk:
                        words = WORD.findall(carry.lower())
                    else:
                        block = carry + chunk.lower()
                        matches = list(WORD.finditer(block))
                        carry = ""
                        if matches and matches[-1].end() == len(block):
                            carry = matches.pop().group()
                        words = [m.group() for m in matches]
                    for word in words:
                        if not word.strip("'"):
                            continue
                        window.append(word)
                        if len(window) == SHINGLE:
                            h = hash(tuple(window))
                            if h in index:
                                seen.add(h)
                    if not chunk:
                        break
            for h in seen:
                for p in index[h]:
                    found[p] = found.get(p, 0) + 1
    return found


def scan(root: Path, corpus: list[Path]) -> list[tuple[str, str, int]]:
    findings: list[tuple[str, str, int]] = []
    self_path = Path(__file__).resolve()
    deny = []
    texts: dict[Path, str] = {}
    for f in iter_files(root):
        rel = f.relative_to(root).as_posix()
        name = f.name
        if f.is_symlink():
            findings.append(("symlink", rel, 0))
            continue
        if protected(f):
            findings.append(("protected_file", rel, 0))
            continue
        suf = f.suffix.lower()
        size = f.stat().st_size
        if suf in DATA_SUFFIXES or (suf in LARGE_TEXT_SUFFIXES and size > LARGE_TEXT_BYTES):
            findings.append(("data_file", rel, 0))
        if suf not in TEXT_SUFFIXES or size > 5_000_000:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(("binary_in_text_slot", rel, 0))
            continue
        texts[f] = text
        is_self = f.resolve() == self_path
        for m in HOME_PATH.finditer(text):
            findings.append(("home_path", rel, line_of(text, m.start())))
        if not is_self:
            for off in hashed_fragment_hits(text):
                findings.append(("internal_host", rel, line_of(text, off)))
        for pat in (PRIVATE_IP, INTERNAL_TLD, *deny):
            for m in pat.finditer(text):
                findings.append(("internal_host", rel, line_of(text, m.start())))
        for pat in KEY_SHAPES:
            for m in pat.finditer(text):
                findings.append(("key_shape", rel, line_of(text, m.start())))
        if suf not in CODE_SUFFIXES:
            for m in DIALOGUE_KEYS.finditer(text):
                findings.append(("dialogue_schema", rel, line_of(text, m.start())))
    if corpus:
        for p, n in sorted(corpus_overlap(texts, corpus).items()):
            findings.append(("corpus_overlap", f"{p.relative_to(root).as_posix()} ({n} shared {SHINGLE}-word shingles)", 0))
    return findings


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--corpus", type=Path, nargs="*", default=[],
                    help="explicit benchmark files to compare locally (no content is printed)")
    args = ap.parse_args(argv)
    root = args.root.resolve()
    findings = scan(root, [c.resolve() for c in args.corpus])
    # Findings stay in memory for callers; terminal output is aggregate-only.
    counts: dict[str, int] = {}
    for check, _, _ in findings:
        counts[check] = counts.get(check, 0) + 1
    n_files = sum(1 for _ in iter_files(root))
    print(f"hygiene: {n_files} files scanned, {len(findings)} finding(s) {counts if counts else ''}".rstrip())
    print(f"hygiene: corpus overlap check {'ran on ' + str(len(args.corpus)) + ' path(s)' if args.corpus else 'not run (no --corpus)'}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
