"""Optional hybrid retriever: import guard, RRF fusion and encode order, with a deterministic fake encoder.

The real FastEmbed smoke test runs only when fastembed is importable AND MEMAUDIT_BGE_MODEL_PATH names an existing local
model directory; it never downloads.  CI runs without either, so the guard and fake-encoder paths are what CI covers."""
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import rankdata

from memaudit import dense, qi
from memaudit.tokenizer import Tokenizer



def synthetic_set(groups=4, items_per_group=2, units_per_pool=14):
    """Invented haystacks (kept local: the suite also runs with --import-mode=importlib)."""
    topics = ["kite festival ribbon", "violin bow rosin", "canoe portage trail", "bread crust oven", "lantern wick oil"]
    pools, items, t = [], [], 0
    for g in range(groups):
        for j in range(items_per_group):
            topic = topics[t % len(topics)]
            t += 1
            pid, gold_slot = f"p{g}-{j}", (2 * j + g) % units_per_pool
            units = []
            for k in range(units_per_pool):
                turns = [("user", f"I tried {topic} item {t}")] if k == gold_slot else [("user", f"neutral filler {g} {j} {k}")]
                units.append(qi.make_unit_record(f"{pid}/u{k}", k, turns, ("user",)))
            pools.append({"type": "pool", "pool_id": pid, "group": f"G{g}", "bench": "synth", "units": units})
            items.append({"type": "item", "item_id": f"i{g}-{j}", "pool_id": pid, "group": f"G{g}", "bench": "synth", "qtype": "t",
                          "split": "all", "question": f"What about the {topic} {t}?", "gold_uids": [f"{pid}/u{gold_slot}"],
                          "background": None, "flags": {}})
    return qi.build_set("synth", pools, items)


class FakeEncoder:
    """Deterministic bag-of-words hashing encoder; records each batch it receives."""

    def __init__(self, dim=16):
        self.dim, self.batches = dim, []

    def embed(self, texts):
        self.batches.append(list(texts))
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, t in enumerate(texts):
            for w in t.lower().split():
                out[i, int(hashlib.sha256(w.encode()).hexdigest(), 16) % self.dim] += 1.0
            out[i, 0] += 0.01
        return out


def test_guard_raises_fixed_message_when_fastembed_missing(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "fastembed", None)
    assert dense.fastembed_available() is False
    with pytest.raises(dense.OptionalDependencyError) as e:
        dense.require_fastembed()
    assert str(e.value) == dense.MISSING_FASTEMBED
    with pytest.raises(dense.OptionalDependencyError):
        dense.FastEmbedEncoder(tmp_path)


def test_bm25_default_never_imports_fastembed(monkeypatch):
    monkeypatch.setitem(sys.modules, "fastembed", None)
    rep = qi.run_qi(synthetic_set(groups=6, items_per_group=2), n_boot=50)
    assert rep["settings"]["retriever"] == "bm25" and rep["settings"]["hybrid"] is None
    assert rep["peers"]["starved_items"] == 0 and 0 <= rep["rates"]["5"]["QI"] <= 1


def test_hybrid_requires_an_encoder():
    with pytest.raises(ValueError):
        qi.run_qi(synthetic_set(groups=3, items_per_group=2), retriever="hybrid", n_boot=50)


def test_vector_cache_encode_order_and_batches():
    enc = FakeEncoder()
    cache = dense.VectorCache(enc, batch=3)
    texts = ["bb", "a", "cccc", "a", "dd", "e"]
    cache.encode_pass(texts, "")
    flat = [t for b in enc.batches for t in b]
    assert flat == dense.pass_order(texts) and all(len(b) <= 3 for b in enc.batches)
    assert [len(t) for t in flat] == sorted(len(t) for t in flat)
    n_calls = len(enc.batches)
    v = cache.vectors(["a", "dd"], "")
    assert len(enc.batches) == n_calls and v.shape == (2, 16)
    assert np.allclose(np.linalg.norm(v, axis=1), 1.0)
    cache.vectors(["zz"], "pre: ")
    assert enc.batches[-1] == ["pre: zz"]


def test_hybrid_scores_are_rrf_of_bm25_and_dense_then_max_pooled():
    enc = FakeEncoder()
    cache = dense.VectorCache(enc)
    tok = qi._Tokens(Tokenizer("default", stemmer="rust"))
    units = [("kite flying day", "rain"), ("violin lesson",), ("kite string", "kite tail kite"), ()]
    hy = qi.HaystackScorer(units, tok, "hybrid", cache.vectors, "q: ", "")
    bm = qi.HaystackScorer(units, tok, "bm25")
    query = "kite tail"
    turns = [t for u in units for t in u]
    sess = [i for i, u in enumerate(units) for _ in u]
    b = bm.bm.get_scores(tok(query))
    d = cache.vectors(turns, "") @ cache.vectors([query], "q: ")[0]
    fused = 1.0 / (60 + rankdata(-b, method="average")) + 1.0 / (60 + rankdata(-d.astype(float), method="average"))
    expected = np.full(4, -np.inf)
    for s, v in zip(sess, fused):
        expected[s] = max(expected[s], v)
    assert np.allclose(hy.score(query), expected, rtol=0, atol=1e-15)
    assert hy.score(query)[3] == -np.inf


def test_run_qi_hybrid_with_fake_encoder_is_deterministic():
    qs = synthetic_set(groups=6, items_per_group=2)
    r1 = qi.run_qi(qs, retriever="hybrid", encoder=FakeEncoder(), n_boot=100)
    assert r1["peers"]["starved_items"] == 0 and r1["rates"]["5"]["true_question_hit"] >= 0.75
    r2 = qi.run_qi(qs, retriever="hybrid", encoder=FakeEncoder(), n_boot=100)
    assert json.dumps(r1["rates"], sort_keys=True) == json.dumps(r2["rates"], sort_keys=True) and r1["settings"]["hybrid"]["name"] == "s16-hybrid"
    assert r1["settings"]["hybrid"]["query_prefix"].startswith("Represent this sentence")


def test_s16_hybrid_config_is_complete():
    cfg = dense.S16_HYBRID
    assert cfg["dense_model"] == "BAAI/bge-small-en-v1.5" and cfg["doc_prefix"] == "" and cfg["embedding_dim"] == 384
    assert "c=60" in cfg["fusion"] and "maximum" in cfg["pooling"] and "user-side" in cfg["text"]


@pytest.mark.skipif(not dense.fastembed_available() or not os.environ.get("MEMAUDIT_BGE_MODEL_PATH")
                    or not Path(os.environ.get("MEMAUDIT_BGE_MODEL_PATH", "")).is_dir(),
                    reason="optional: needs fastembed and a local bge-small-en-v1.5 ONNX directory")
def test_real_fastembed_smoke():
    enc = dense.FastEmbedEncoder(os.environ["MEMAUDIT_BGE_MODEL_PATH"])
    v = dense.normalise(enc.embed(["an invented sentence about kites", "another invented line"]))
    assert v.shape == (2, 384) and np.allclose(np.linalg.norm(v, axis=1), 1.0, atol=1e-5)
    assert enc.describe()["backend"] == "fastembed"
