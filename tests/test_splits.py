import hashlib
from collections import Counter

import numpy as np
import pytest

from memaudit.splits import (LEGACY_SALTS, allocate, assert_disjoint_groups, assign_splits, group_codes, hash_group_folds,
                           hash_rank, hash_unit, rank_split, split_of, stratified_sample)


def _independent_u(key: str, salt: str) -> float:
    h = hashlib.sha256((salt + ":" + key).encode()).hexdigest()
    return int(h[:16], 16) / 2.0 ** 64


@pytest.mark.parametrize("key", ["conv-26", "case-001", "a", "ü-ñ"])
def test_hash_unit_matches_the_written_rule(key):
    for salt in LEGACY_SALTS.values():
        assert hash_unit(key, salt) == pytest.approx(_independent_u(key, salt), abs=0, rel=1e-15)


def test_split_of_is_deterministic_and_respects_fraction():
    keys = [f"k{i}" for i in range(4000)]
    sp = [split_of(k, salt="s") for k in keys]
    assert sp == [split_of(k, salt="s") for k in keys]
    frac = sp.count("dev") / len(sp)
    assert 0.27 < frac < 0.33
    assert all(split_of(k, salt="s", dev_fraction=0.0) == "test" for k in keys[:50])
    assert all(split_of(k, salt="s", dev_fraction=1.0) == "dev" for k in keys[:50])
    with pytest.raises(ValueError):
        split_of("x", salt="s", dev_fraction=1.5)


def test_assign_splits_keeps_episodes_together():
    items = [(f"ep{e}", f"q{e}-{j}") for e in range(30) for j in range(7)]
    sp = assign_splits(items, key=lambda it: it[0], item_id=lambda it: it[1], salt="s")
    by_ep: dict = {}
    for ep, qid in items:
        by_ep.setdefault(ep, set()).add(sp[qid])
    assert all(len(v) == 1 for v in by_ep.values())
    with pytest.raises(ValueError, match="duplicate"):
        assign_splits(items + items[:1], key=lambda it: it[0], item_id=lambda it: it[1], salt="s")


def test_rank_split_matches_the_written_rule():
    keys = [f"uid{i}" for i in range(50)]
    prefix = LEGACY_SALTS["s10_stale_rank"]
    ref = sorted(keys, key=lambda k: hashlib.sha256((prefix + k).encode()).hexdigest())
    assert hash_rank(keys, prefix) == ref
    sp = rank_split(keys, prefix, 10, 25)
    assert Counter(sp.values()) == {"dev": 10, "test": 25, "reserve": 15}
    assert [k for k in ref[:10]] == [k for k in ref if sp[k] == "dev"]
    with pytest.raises(ValueError):
        rank_split(keys, prefix, 40, 20)
    with pytest.raises(ValueError):
        hash_rank(["a", "a"], prefix)


def test_allocate_sums_caps_and_is_deterministic():
    sizes = {"a": 5, "b": 50, "c": 1, "d": 44}
    for n in (0, 1, 7, 33, 99, 100):
        q = allocate(sizes, n)
        assert sum(q.values()) == n and all(q[k] <= sizes[k] for k in sizes)
        assert q == allocate(dict(reversed(list(sizes.items()))), n)
    q = allocate(sizes, 40, how="equal")
    assert q["c"] == 1 and q["a"] == 5 and sum(q.values()) == 40
    with pytest.raises(ValueError):
        allocate(sizes, 101)


def test_stratified_sample_is_deterministic_and_ordered():
    items = [{"id": f"i{i}", "s": i % 3} for i in range(90)]
    a = stratified_sample(items, 12, item_id=lambda x: x["id"], stratum=lambda x: x["s"], seed=1)
    b = stratified_sample(items, 12, item_id=lambda x: x["id"], stratum=lambda x: x["s"], seed=1)
    c = stratified_sample(items, 12, item_id=lambda x: x["id"], stratum=lambda x: x["s"], seed=2)
    assert a == b and a != c and len(a) == 12
    assert Counter(x["s"] for x in a) == {0: 4, 1: 4, 2: 4}
    assert [items.index(x) for x in a] == sorted(items.index(x) for x in a)


def test_group_utilities():
    g = ["b", "a", "b", "c", "a"]
    np.testing.assert_array_equal(group_codes(g), [1, 0, 1, 2, 0])
    folds = hash_group_folds([f"g{i % 13}" for i in range(200)], 5)
    assert folds.min() >= 0 and folds.max() <= 4
    for i in range(13):
        assert len(set(folds[[j for j in range(200) if j % 13 == i]].tolist())) == 1
    assert_disjoint_groups(["a", "b"], ["c"])
    with pytest.raises(ValueError, match="both train and test"):
        assert_disjoint_groups(["a", "b"], ["b"])
    with pytest.raises(ValueError):
        hash_group_folds(["a"], 1)
