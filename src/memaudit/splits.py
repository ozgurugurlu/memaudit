"""Deterministic splits, stratified sampling and grouping utilities.

Splits are *hash rules in code*, so no id lists ever need to ship.

Uniform rule (used by the workbench harness, S1 and S11)::

    u = int.from_bytes(sha256(f"{salt}:{key}")[:8], 'big') / 2**64        # uniform in [0, 1)
    split = 'dev' if u < dev_fraction else 'test'

Rank rule (used by S10 for STALE and LoCoMo-Plus)::

    order keys by sha256(prefix + key) (hex digest, ascending); the first n_dev are dev, the next n_test are test

Split by the *episode* (scenario, conversation, host, author), never by question, when questions of one episode share
entities; pass the episode id as ``key``. Tune on dev only; evaluate test once.

Salts are part of a protocol: changing one invalidates every pre-registration that cites it. ``LEGACY_SALTS`` lists
the values the audited studies used, so a reproduction can name them explicitly.
"""
from __future__ import annotations

import hashlib
from typing import Any, Callable, Hashable, Iterable, Mapping, Sequence, TypeVar

import numpy as np

T = TypeVar("T")

SPLIT_VERSION = "split-v1"
DEFAULT_DEV_FRACTION = 0.3

# Salts / prefixes of the audited studies (identifiers, not secrets). Keep them byte-identical.
LEGACY_SALTS: Mapping[str, str] = {
    "harness_uniform": "jevlab-wave2-split-v1",     # uniform rule, workbench harness default (which studies used it: WP-replica verifies for S11)
    "s1_forgeteval": "wave2-S1-null-baselines",     # uniform rule, ForgetEval case ids, dev fraction 0.3
    "s10_stale_rank": "wave2-stale:",                # rank rule prefix, STALE scenarios
    "s10_locomoplus_rank": "wave2-locomoplus:",      # rank rule prefix, LoCoMo-Plus item index
}


def hash_unit(key: str, salt: str) -> float:
    """Deterministic uniform number in [0, 1) from ``sha256(f"{salt}:{key}")``."""
    digest = hashlib.sha256(f"{salt}:{key}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / float(1 << 64)


def split_of(key: str, *, salt: str, dev_fraction: float = DEFAULT_DEV_FRACTION) -> str:
    """``'dev'`` or ``'test'`` for one key under the uniform rule."""
    if not 0.0 <= dev_fraction <= 1.0:
        raise ValueError(f"dev_fraction must be in [0, 1], got {dev_fraction}")
    return "dev" if hash_unit(str(key), salt) < dev_fraction else "test"


def assign_splits(items: Iterable[T], *, key: Callable[[T], str], salt: str,
                  dev_fraction: float = DEFAULT_DEV_FRACTION, item_id: Callable[[T], Hashable] | None = None) -> dict:
    """``{item_id(item): 'dev'|'test'}`` where the split is decided by ``key(item)`` (e.g. the episode id).

    ``item_id`` defaults to ``key`` (one row per episode). All items sharing a key land on the same side."""
    ident = item_id or key
    out: dict = {}
    for it in items:
        iid = ident(it)
        if iid in out:
            raise ValueError(f"duplicate item id {iid!r}")
        out[iid] = split_of(key(it), salt=salt, dev_fraction=dev_fraction)
    return out


def hash_rank(keys: Iterable[str], prefix: str) -> list[str]:
    """Keys ordered by ``sha256(prefix + key)`` hex digest (ties impossible for distinct keys)."""
    ks = [str(k) for k in keys]
    if len(set(ks)) != len(ks):
        raise ValueError("hash_rank needs distinct keys")
    return sorted(ks, key=lambda k: hashlib.sha256((prefix + k).encode("utf-8")).hexdigest())


def rank_split(keys: Iterable[str], prefix: str, n_dev: int, n_test: int) -> dict[str, str]:
    """``{key: 'dev'|'test'|'reserve'}`` under the rank rule (first ``n_dev``, next ``n_test``, the rest reserve)."""
    ranked = hash_rank(keys, prefix)
    if n_dev < 0 or n_test < 0 or n_dev + n_test > len(ranked):
        raise ValueError(f"cannot take {n_dev} dev + {n_test} test from {len(ranked)} keys")
    out = {}
    for i, k in enumerate(ranked):
        out[k] = "dev" if i < n_dev else "test" if i < n_dev + n_test else "reserve"
    return out


def allocate(sizes: dict[Any, int], n: int, *, how: str = "proportional") -> dict[Any, int]:
    """Split ``n`` draws over strata with the given sizes.

    Largest-remainder apportionment, capped at each stratum's size; draws that a capped stratum cannot take are
    re-distributed over the strata that still have room. ``how='proportional'`` weights strata by size, ``'equal'``
    gives every stratum the same weight. Raises ``ValueError`` if ``n`` exceeds the total (no silent truncation).
    Deterministic (ties broken by ``repr(key)``).
    """
    if how not in ("proportional", "equal"):
        raise ValueError(f"how must be 'proportional' or 'equal', got {how!r}")
    if n < 0:
        raise ValueError("n must be >= 0")
    if any(not isinstance(v, int) or v < 0 for v in sizes.values()):
        raise ValueError("stratum sizes must be nonnegative integers")
    total = sum(sizes.values())
    if n > total:
        raise ValueError(f"cannot sample {n} items from {total}")
    keys = sorted(sizes, key=repr)
    quota = {k: 0 for k in keys}
    remaining = n
    while remaining > 0:
        active = [k for k in keys if quota[k] < sizes[k]]
        weight = {k: (sizes[k] if how == "proportional" else 1) for k in active}
        wsum = float(sum(weight.values()))
        raw = {k: remaining * weight[k] / wsum for k in active}
        add = {k: min(int(raw[k]), sizes[k] - quota[k]) for k in active}
        leftover = remaining - sum(add.values())
        for k in sorted(active, key=lambda k: (-(raw[k] - int(raw[k])), repr(k))):
            if leftover == 0:
                break
            if quota[k] + add[k] < sizes[k]:
                add[k] += 1
                leftover -= 1
        for k in active:
            quota[k] += add[k]
        remaining = n - sum(quota.values())
    return quota


def stratified_sample(items: Sequence[T], n: int, *, item_id: Callable[[T], str],
                      stratum: Callable[[T], Hashable] | None = None, seed: int = 0,
                      allocation: str = "proportional") -> list[T]:
    """Deterministic stratified sample of ``n`` items, returned in input order.

    Within every stratum items are ordered by ``hash_unit(item_id, f"sample:{seed}")`` and the first ``quota`` are taken."""
    if len({item_id(it) for it in items}) != len(items):
        raise ValueError("duplicate sample IDs")
    strata: dict[Hashable, list[T]] = {}
    for it in items:
        strata.setdefault("all" if stratum is None else stratum(it), []).append(it)
    quota = allocate({k: len(v) for k, v in strata.items()}, n, how=allocation)
    chosen: set[str] = set()
    for k, members in strata.items():
        ranked = sorted(members, key=lambda it: hash_unit(item_id(it), f"sample:{seed}"))
        chosen.update(item_id(it) for it in ranked[: quota[k]])
    return [it for it in items if item_id(it) in chosen]


# --------------------------------------------------------------------------------------------------- grouping
def group_codes(values: Sequence[Hashable]) -> np.ndarray:
    """Integer codes of ``values`` in sorted order of the distinct values (``np.unique(..., return_inverse=True)``).

    Same convention as the S10 audit, so GroupKFold folds computed from these codes reproduce the study."""
    _, inv = np.unique(np.asarray(values), return_inverse=True)
    return inv.astype(np.int64)


def hash_group_folds(groups: Sequence[Hashable], k: int, *, salt: str = "memaudit-folds-v1") -> np.ndarray:
    """Fold index in ``[0, k)`` per row, decided by a hash of the row's group (whole groups stay together).

    Order-independent and stable when rows are added. Note: the S10 audit used scikit-learn's ``GroupKFold``
    (size-balanced folds); reproductions of S10 numbers must use that, not this function."""
    if k < 2:
        raise ValueError("k must be >= 2")
    return np.array([min(k - 1, int(hash_unit(str(g), salt) * k)) for g in groups], dtype=np.int64)


def assert_disjoint_groups(train_groups: Iterable[Hashable], test_groups: Iterable[Hashable]) -> None:
    """Raise ``ValueError`` if any group occurs on both sides (leakage across a grouped split)."""
    shared = set(train_groups) & set(test_groups)
    if shared:
        sample = sorted(map(str, shared))[:5]
        raise ValueError(f"{len(shared)} group(s) occur in both train and test, e.g. {sample}")
