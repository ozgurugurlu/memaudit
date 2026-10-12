"""Wrong-question retrieval (query independence, QI) with fair nulls: the S16-style atlas row for one item file.

For every sampled item, ten wrong questions taken from items of OTHER groups rank the item's haystack units; the outcome
is any gold unit in the top k.  The rate is compared with three nulls computed per item:

* uniform chance          1 - C(n-e, k)/C(n, k) over the n non-empty units (e of them gold);
* turn-weighted chance    Plackett-Luce top-k with weight = number of non-empty scoring turns of a unit.  Max-pooling over
                          turns favours units with more turns under ANY query, so this is the primary null;
* matched placebo         20 placebo gold sets drawn from non-gold units in the same (user-char decile, turn-count
                          decile, position tercile) cells, scored under the same wrong-question rankings.  An item has
                          support only when every cell holds at least as many non-gold as gold units; a row needs at least
                          80% supported items before its placebo value describes the row.

The effect is kappa = (QI - null)/(1 - null) per item, averaged over items, with the wider of a two-way (target group x
peer group) cluster bootstrap and a CR1 cluster t interval.  A query-blind feature scan (K3) labels a row cue-dominated
when one feature separates gold with within-haystack AUROC >= .90; the turn-weighted kappa of such a row is then not
interpretable.  Rules, salts and constants follow the S16 registration so that a public item file reproduces its row.

Inputs are explicit local files with full SHA-256 pins.  Questions and unit text are used in memory only; reports carry
identifiers, hashes, counts and statistics.  Nothing here downloads, calls a model service or writes benchmark text.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import lru_cache
from math import comb
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence

import numpy as np

from .features import sanitize_text
from .provenance import file_info

# --------------------------------------------------------------------------------------------------- registered constants
SCHEMA_ITEMS = "memaudit-qi-items/1"
SCHEMA_REPORT = "memaudit-qi-report/1"
K_PRIMARY = 5
K_ALL = (1, 5, 10)
TOPN_STORE = 10
N_WRONG = 10
MIN_N_EXCLUSIVE = 2 * K_PRIMARY          # items with n <= 2k non-empty units are not sampled
SALT_SEL = "S16-sel|"
SALT_QI = "S16-qi|"
SALT_TIE = "S16-tie|"
SALT_BOOT = "S16-boot|"
SALT_PL = "S16-pl|"
SALT_PLACEBO = "S16-placebo|"
PL_EXACT_MAX_SEQ = 200_000
PL_MC_DRAWS = 100_000
PLACEBO_M = 20
PLACEBO_CHAR_BINS = 10
PLACEBO_TURN_BINS = 10
PLACEBO_POS_BINS = 3
COMMON_SUPPORT_MIN = 0.80
DEGENERATE_NULL_EPS = 1e-12
BM25_K1 = 1.5
BM25_B = 0.75
BM25_EPSILON = 0.25
BM25_EMPTY_TOKEN = "_"
SHINGLE_N = 5
NEAR_DUP_JACCARD = 0.80
LEAK_FEATURES = ("chars", "turns", "position", "non_ascii", "typo_markers")
K3_AUROC = 0.90
TYPO_MARKERS = ("’", "‘", "“", "”", "–", "—", "…")
ALPHA = 0.05
N_BOOT = 10_000
MARGIN_KAPPA = 0.03
RRF_C = 60
RETRIEVERS = ("bm25", "hybrid")
_INVISIBLE = re.compile(r"[\s​‌‍⁠﻿️]+")
_ID = re.compile(r"^[A-Za-z0-9_.:/|+\-=#@~]{1,200}$")
_WORD = re.compile(r"\w+")

POOL_KEYS = {"type", "pool_id", "group", "bench", "units"}
UNIT_KEYS = {"uid", "slot", "text_sha256", "n_chars_user", "n_turns_user_nonempty", "turn_texts_user", "turn_texts_all"}
ITEM_KEYS = {"type", "item_id", "pool_id", "group", "bench", "qtype", "split", "question", "gold_uids", "background", "flags"}


def h(*parts: str) -> str:
    return hashlib.sha256("".join(parts).encode("utf-8")).hexdigest()


def seed_of(*parts: str) -> int:
    return int(h(*parts)[:16], 16)


def _canonical(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def raw_nonempty(text: str) -> bool:
    return bool(_INVISIBLE.sub("", str(text)))


def question_hash(question: str) -> str:
    return hashlib.sha256(" ".join(sanitize_text(question).lower().split()).encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------------------------------- data model
@dataclass(frozen=True)
class QIUnit:
    uid: str
    slot: int
    text_sha256: str
    n_chars: int                       # raw user-side characters (converter field)
    turns: tuple[str, ...]             # F1-normalised non-empty scoring turns
    raw_user: tuple[str, ...] = field(repr=False, default=())

    @property
    def nonempty(self) -> bool:
        return bool(self.turns)


@dataclass
class QIPool:
    pool_id: str
    group: str
    units: list[QIUnit]

    @property
    def nonempty_slots(self) -> list[int]:
        return [u.slot for u in self.units if u.nonempty]


@dataclass
class QIItem:
    item_id: str
    pool_id: str
    group: str
    qtype: str | None
    split: str | None
    question: str = field(repr=False)
    gold_uids: list[str] = field(default_factory=list)
    flags: dict = field(default_factory=dict)


@dataclass
class QISet:
    name: str                          # bench name; enters every registered salt
    family: str                        # selection-hash family
    pools: dict[str, QIPool]
    items: list[QIItem]
    meta: dict = field(default_factory=dict)

    def pool_of(self, it: QIItem) -> QIPool:
        return self.pools[it.pool_id]


def make_unit_record(uid: str, slot: int, turns: Sequence[tuple[str, str]], user_side: Iterable[str] | None) -> dict:
    """Contract unit record; ``user_side`` = roles whose text is scoring text (None = every role)."""
    roles = None if user_side is None else set(user_side)
    all_texts = [str(t) for _, t in turns]
    user_texts = [str(t) for r, t in turns if roles is None or r in roles]
    return {"uid": str(uid), "slot": int(slot), "text_sha256": hashlib.sha256(_canonical(all_texts).encode("utf-8")).hexdigest(),
            "n_chars_user": int(sum(len(t) for t in user_texts)),
            "n_turns_user_nonempty": int(sum(1 for t in user_texts if raw_nonempty(t))),
            "turn_texts_user": user_texts, "turn_texts_all": all_texts}


def _to_unit(rec: Mapping) -> QIUnit:
    turns = tuple(s for s in (sanitize_text(str(t)) for t in rec["turn_texts_user"] or []) if s.strip())
    return QIUnit(str(rec["uid"]), int(rec["slot"]), str(rec["text_sha256"]), int(rec["n_chars_user"]), turns,
                  tuple(str(t) for t in rec["turn_texts_user"]))


def build_set(name: str, pools: Sequence[Mapping], items: Sequence[Mapping], *, family: str | None = None,
              meta: Mapping | None = None) -> QISet:
    """Validate contract records (ids only in error messages) and build the engine view."""
    if not _ID.match(name):
        raise ValueError("bench name must be an identifier")
    by_id: dict[str, QIPool] = {}
    for p in pools:
        if set(p) != POOL_KEYS or p["type"] != "pool":
            raise ValueError("pool record keys differ from the item-file contract")
        if p["pool_id"] in by_id:
            raise ValueError("duplicate pool id")
        uids = [u["uid"] for u in p["units"]]
        if len(set(uids)) != len(uids):
            raise ValueError("duplicate unit id within a pool")
        for k, u in enumerate(p["units"]):
            if set(u) != UNIT_KEYS or u["slot"] != k:
                raise ValueError("unit record keys or slots differ from the item-file contract")
            if not all(isinstance(t, str) for t in u["turn_texts_user"]) or not all(isinstance(t, str) for t in u["turn_texts_all"]):
                raise ValueError("turn texts must be strings")
        by_id[str(p["pool_id"])] = QIPool(str(p["pool_id"]), str(p["group"]), [_to_unit(u) for u in p["units"]])
    out_items, seen = [], set()
    for it in items:
        if set(it) != ITEM_KEYS or it["type"] != "item":
            raise ValueError("item record keys differ from the item-file contract")
        if it["item_id"] in seen:
            raise ValueError("duplicate item id")
        seen.add(it["item_id"])
        pool = by_id.get(str(it["pool_id"]))
        if pool is None or pool.group != str(it["group"]):
            raise ValueError("item references a missing pool or another group")
        if not it["gold_uids"] or not set(it["gold_uids"]) <= {u.uid for u in pool.units}:
            raise ValueError("item gold is empty or outside its pool")
        if not isinstance(it["question"], str) or not it["question"].strip():
            raise ValueError("item question is empty")
        out_items.append(QIItem(str(it["item_id"]), str(it["pool_id"]), str(it["group"]),
                                None if it["qtype"] is None else str(it["qtype"]), None if it["split"] is None else str(it["split"]),
                                it["question"], [str(g) for g in dict.fromkeys(it["gold_uids"])], dict(it.get("flags") or {})))
    for x in list(pools) + list(items):
        if x["bench"] != name:
            raise ValueError("records name another bench")
    return QISet(name, family or name, by_id, out_items, dict(meta or {}))


def read_item_file(path: str | Path, expected_sha256: str) -> QISet:
    """Pinned JSONL item file (gzip or plain): pool records, then item records, one bench (the S16 interface contract)."""
    pin = file_info(path, expected_sha256)
    opener = gzip.open if Path(path).suffix == ".gz" else open
    pools, items = [], []
    with opener(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rec = json.loads(line)
                (pools if rec.get("type") == "pool" else items).append(rec)
    names = {r.get("bench") for r in pools + items}
    if len(names) != 1:
        raise ValueError("an item file holds exactly one bench")
    name = str(names.pop())
    return build_set(name, pools, items, meta={"inputs": [pin], "adapter": "item file"})


# --------------------------------------------------------------------------------------------------- LoCoMo-Plus adapter
_NUMBERS = dict(zip("one two three four five six seven eight nine ten eleven twelve".split(), range(1, 13)))
_GAP = re.compile(r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|a|an)\s*(weeks?|months?|years?)\b")


def _gap_days(text: str) -> int:
    m = _GAP.search(str(text).lower())
    if not m:
        return 0
    n, unit = m.groups()
    count = int(n) if n.isdigit() else _NUMBERS.get(n, 1)
    return count * (7 if unit.startswith("week") else 30 if unit.startswith("month") else 365)


def _labelled(text: str) -> list[str]:
    return [line.strip()[2:].strip() for line in str(text).splitlines() if line.strip().startswith(("A:", "B:"))]


def locomo_plus_items(path, expected_sha256, *, hosts_path, hosts_sha256) -> QISet:
    """LoCoMo-Plus items with the audit adapter's host stitching (host = item index modulo host count, cue dated after the
    last host session by 7 - gap days, stable date sort).  Unit = one turn, both speakers score; gold = cue turns;
    question = the trigger-query A/B lines joined by one space; group = host conversation."""
    pin = file_info(path, expected_sha256)
    hpin = file_info(hosts_path, hosts_sha256)
    plus = json.loads(Path(path).read_text(encoding="utf-8"))
    hosts = json.loads(Path(hosts_path).read_text(encoding="utf-8"))
    if not isinstance(plus, list) or not isinstance(hosts, list) or not hosts:
        raise ValueError("LoCoMo-Plus needs a list of items and host conversations in upstream order")
    pools, items = [], []
    excluded = Counter()
    for i, rec in enumerate(plus):
        host = hosts[i % len(hosts)]
        group = str(host["sample_id"])
        conv = host["conversation"]
        nums = sorted(int(m[1]) for k in conv if (m := re.fullmatch(r"session_(\d+)", k)))
        events = []
        for n in nums:
            dt = datetime.strptime(conv[f"session_{n}_date_time"], "%I:%M %p on %d %B, %Y")
            events.append((dt, False, f"{group}/s{n}", [str(t["text"]) for t in conv[f"session_{n}"]]))
        cue = _labelled(rec["cue_dialogue"])
        if not cue:
            raise ValueError("cue dialogue has no A/B turns")
        events.append((events[-1][0] + timedelta(days=7 - _gap_days(rec["time_gap"])), True, f"cue{i}", cue))
        events.sort(key=lambda x: x[0])
        flat = [(f"{key}/t{j}", text, is_cue) for _, is_cue, key, turns in events for j, text in enumerate(turns)]
        trig = " ".join(_labelled(rec["trigger_query"]))
        if not trig.strip():
            excluded["empty_trigger"] += 1
            continue
        units = [make_unit_record(uid, k, [("speaker", text)], None) for k, (uid, text, _) in enumerate(flat)]
        gold = [uid for uid, _, is_cue in flat if is_cue]
        nonempty = {u["uid"] for u in units if u["n_turns_user_nonempty"] > 0}
        if not set(gold) & nonempty:
            excluded["cue_without_text"] += 1
            continue
        pid = f"lp{i}"
        pools.append({"type": "pool", "pool_id": pid, "group": group, "bench": "locomo_plus", "units": units})
        items.append({"type": "item", "item_id": pid, "pool_id": pid, "group": group, "bench": "locomo_plus",
                      "qtype": str(rec.get("relation_type", "unknown")), "split": "all", "question": trig,
                      "gold_uids": list(dict.fromkeys(gold)), "background": None, "flags": {}})
    return build_set("locomo_plus", pools, items, meta={"inputs": [pin, hpin], "adapter": "locomo_plus",
                                                       "excluded": dict(excluded)})


QI_BENCHMARKS = {"locomo_plus": locomo_plus_items}


# --------------------------------------------------------------------------------------------------- population and sample
def gold_slots(pool: QIPool, it: QIItem) -> list[int]:
    g = set(it.gold_uids)
    return sorted(u.slot for u in pool.units if u.uid in g and u.nonempty)


def sel_hash(family: str, key: str) -> str:
    return h(SALT_SEL, family, "|", key)


def sample_plan(qs: QISet, *, per_group_cap: int | None = None, total_cap: int | None = None) -> tuple[list[QIItem], list[QIItem], dict]:
    """(peer population = every item with e >= 1, sample, counts).  The sample drops n <= 2k, is ordered by the
    registered selection hash and is then capped per group and overall (no caps by default)."""
    pop, counts = [], {"items_total": len(qs.items), "e0": 0, "n_le_2k": 0, "cap_per_group": 0, "cap_total": 0}
    for it in qs.items:
        if not gold_slots(qs.pool_of(it), it):
            counts["e0"] += 1
            continue
        pop.append(it)
    kept = []
    for it in pop:
        if len(qs.pool_of(it).nonempty_slots) <= MIN_N_EXCLUSIVE:
            counts["n_le_2k"] += 1
            continue
        kept.append(it)
    kept.sort(key=lambda it: (sel_hash(qs.family, str(it.flags.get("base_item_id") or it.item_id)), it.item_id))
    taken, per = [], defaultdict(int)
    for it in kept:
        if per_group_cap is not None and per[it.group] >= per_group_cap:
            counts["cap_per_group"] += 1
            continue
        per[it.group] += 1
        taken.append(it)
    if total_cap is not None and len(taken) > total_cap:
        counts["cap_total"] = len(taken) - total_cap
        taken = taken[:total_cap]
    counts["sample"] = len(taken)
    counts["peer_population"] = len(pop)
    return pop, taken, counts


# --------------------------------------------------------------------------------------------------- nulls
def chance_any(n: int, e: int, k: int = K_PRIMARY) -> float:
    if min(n, e, k) < 0 or e > n:
        raise ValueError("need 0 <= e <= n and k >= 0")
    k = min(k, n)
    total = comb(n, k)
    return (total - comb(n - e, k)) / total


def _classes(weights: Sequence[int]) -> tuple[tuple[int, int], ...]:
    c = Counter(int(w) for w in weights)
    if any(w <= 0 for w in c):
        raise ValueError("Plackett-Luce weights must be positive integers")
    return tuple(sorted(c.items()))


def pl_states_bound(nongold_weights: Sequence[int], k: int) -> int:
    d = len(set(int(w) for w in nongold_weights))
    return comb(k + d, d)


def pl_hit_exact(gold_weights: Sequence[int], nongold_weights: Sequence[int], k: int) -> float:
    """Exact P(any gold in the first k Plackett-Luce draws), memoised over non-gold weight classes."""
    wg = sum(int(w) for w in gold_weights)
    if wg <= 0:
        return 0.0
    cls = _classes(nongold_weights) if nongold_weights else ()
    values = tuple(w for w, _ in cls)

    @lru_cache(maxsize=None)
    def miss(counts: tuple[int, ...], depth: int) -> float:
        if depth == 0:
            return 1.0
        rem = sum(v * m for v, m in zip(values, counts))
        if rem == 0:
            return 0.0
        tot = wg + rem
        acc = 0.0
        for j, (v, m) in enumerate(zip(values, counts)):
            if m:
                acc += (v * m / tot) * miss(counts[:j] + (m - 1,) + counts[j + 1:], depth - 1)
        return acc

    return 1.0 - miss(tuple(m for _, m in cls), int(k))


def pl_hit_mc(gold_weights: Sequence[int], nongold_weights: Sequence[int], ks: Sequence[int], *, draws: int = PL_MC_DRAWS,
              seed: int = 0) -> dict:
    """Exponential-race Monte Carlo of the Plackett-Luce top-k any-gold hit; {k: (p, se)}."""
    wg = float(sum(int(w) for w in gold_weights))
    if wg <= 0:
        return {int(k): (0.0, 0.0) for k in ks}
    rng = np.random.default_rng(seed)
    t = rng.exponential(1.0 / wg, size=draws)
    before = np.zeros(draws, dtype=np.int64)
    for w, m in _classes(nongold_weights) if nongold_weights else ():
        before += rng.binomial(m, -np.expm1(-w * t))
    out = {}
    for k in ks:
        p = float((before < int(k)).mean())
        out[int(k)] = (p, float(np.sqrt(max(p * (1 - p), 0.0) / draws)))
    return out


def pl_chance(gold_weights: Sequence[int], nongold_weights: Sequence[int], ks: Sequence[int] = K_ALL, *, seed: int = 0) -> dict:
    if all(pl_states_bound(nongold_weights, int(k)) <= PL_EXACT_MAX_SEQ for k in ks):
        return {"method": "exact", "p": {int(k): pl_hit_exact(gold_weights, nongold_weights, int(k)) for k in ks}}
    mc = pl_hit_mc(gold_weights, nongold_weights, ks, seed=seed)
    return {"method": "mc", "p": {k: v[0] for k, v in mc.items()}}


def _bins(values: Sequence[float], n_bins: int) -> list[int]:
    n = len(values)
    first: dict = {}
    for i, v in enumerate(sorted(values)):
        first.setdefault(v, i)
    return [min(n_bins - 1, (n_bins * first[v]) // n) for v in values]


def unit_cells(pool: QIPool) -> dict[int, tuple[int, int, int]]:
    live = [u for u in pool.units if u.nonempty]
    if not live:
        return {}
    cb = _bins([u.n_chars for u in live], PLACEBO_CHAR_BINS)
    tb = _bins([len(u.turns) for u in live], PLACEBO_TURN_BINS)
    n = len(live)
    return {u.slot: (cb[i], tb[i], min(PLACEBO_POS_BINS - 1, (PLACEBO_POS_BINS * i) // n)) for i, u in enumerate(live)}


def matched_placebo(pool: QIPool, gold: Sequence[int], bench: str, item_id: str, m: int = PLACEBO_M) -> dict:
    cells = unit_cells(pool)
    gold = sorted(set(gold))
    gset = set(gold)
    if not gold or not gset <= set(cells):
        raise ValueError("gold slots must be non-empty units of the pool")
    uid = {u.slot: u.uid for u in pool.units}
    by_cell: dict[tuple, list[int]] = {}
    for s, c in cells.items():
        if s not in gset:
            by_cell.setdefault(c, []).append(s)
    need = Counter(cells[g] for g in gold)
    short = sum(1 for c, k in need.items() if len(by_cell.get(c, [])) < k)
    if short:
        return {"support": False, "sets": None, "short_cells": short}
    gorder = sorted(gold, key=lambda g: (h(SALT_PLACEBO, bench, "|", item_id, "|gold|", uid[g]), g))
    sets = []
    for j in range(m):
        used: set[int] = set()
        chosen = []
        for g in gorder:
            cands = sorted(by_cell[cells[g]], key=lambda s: (h(SALT_PLACEBO, bench, "|", item_id, "|", str(j), "|", uid[s]), s))
            pick = next(s for s in cands if s not in used)
            used.add(pick)
            chosen.append(pick)
        sets.append(sorted(chosen))
    return {"support": True, "sets": sets, "short_cells": 0}


# --------------------------------------------------------------------------------------------------- peers
def shingles(text: str, n: int = SHINGLE_N) -> frozenset:
    words = _WORD.findall(sanitize_text(text).lower())
    if not words:
        return frozenset()
    if len(words) < n:
        return frozenset([tuple(words)])
    return frozenset(tuple(words[i:i + n]) for i in range(len(words) - n + 1))


class _NearDup:
    def __init__(self, pool: QIPool):
        self.sizes: list[int] = []
        self.inv: dict[tuple, list[int]] = defaultdict(list)
        for u in pool.units:
            s = shingles("\n".join(u.turns)) if u.nonempty else frozenset()
            j = len(self.sizes)
            self.sizes.append(len(s))
            for sh in s:
                self.inv[sh].append(j)

    def max_jaccard(self, s: frozenset) -> float:
        if not s:
            return 0.0
        cnt: dict[int, int] = defaultdict(int)
        for sh in s:
            for j in self.inv.get(sh, ()):
                cnt[j] += 1
        return max((c / (len(s) + self.sizes[j] - c) for j, c in cnt.items()), default=0.0)


class PeerSelector:
    """Wrong-question peers: the eligible population ordered by sha256(SALT_QI + bench|target|peer); a candidate is skipped
    when it shares the target's group, its normalised question, an evidence unit's content hash with the target
    haystack, or a near-duplicate (5-word-shingle Jaccard >= .8) evidence unit; the first ``n`` remaining are taken."""

    def __init__(self, qs: QISet, population: Sequence[QIItem]):
        self.qs, self.pop = qs, list(population)
        self.qh = {it.item_id: question_hash(it.question) for it in self.pop}
        self._gold: dict[str, tuple[set, list]] = {}
        self._pool_hashes: dict[str, set] = {}
        self._ndx: dict[str, _NearDup] = {}

    def _gold_of(self, it: QIItem):
        if it.item_id not in self._gold:
            g = set(it.gold_uids)
            units = [u for u in self.qs.pool_of(it).units if u.uid in g]
            self._gold[it.item_id] = ({u.text_sha256 for u in units}, [shingles("\n".join(u.turns)) for u in units if u.nonempty])
        return self._gold[it.item_id]

    def select(self, target: QIItem, n: int = N_WRONG) -> dict:
        counts = {"same_group": 0, "same_question": 0, "evidence_overlap": 0, "near_duplicate": 0}
        order = sorted((p for p in self.pop if p.item_id != target.item_id),
                       key=lambda p: (h(SALT_QI, self.qs.name, "|", target.item_id, "|", p.item_id), p.item_id))
        tq = question_hash(target.question)
        if target.pool_id not in self._pool_hashes:
            self._pool_hashes[target.pool_id] = {u.text_sha256 for u in self.qs.pools[target.pool_id].units}
        thashes = self._pool_hashes[target.pool_id]
        chosen = []
        for p in order:
            if len(chosen) >= n:
                break
            if p.group == target.group:
                counts["same_group"] += 1
                continue
            if self.qh[p.item_id] == tq:
                counts["same_question"] += 1
                continue
            gh, gsh = self._gold_of(p)
            if gh & thashes:
                counts["evidence_overlap"] += 1
                continue
            if target.pool_id not in self._ndx:
                self._ndx[target.pool_id] = _NearDup(self.qs.pools[target.pool_id])
            if any(self._ndx[target.pool_id].max_jaccard(s) >= NEAR_DUP_JACCARD for s in gsh):
                counts["near_duplicate"] += 1
                continue
            chosen.append(p.item_id)
        return {"peers": chosen, "starved": len(chosen) < n, "excluded": counts}


# --------------------------------------------------------------------------------------------------- retrieval
class BM25Okapi:
    """BM25 Okapi with the rank-bm25 0.2.2 formulas and floating-point order (idf floor epsilon x mean idf)."""

    def __init__(self, corpus: Sequence[Sequence[str]], k1: float = BM25_K1, b: float = BM25_B, epsilon: float = BM25_EPSILON):
        self.k1, self.b, self.epsilon = k1, b, epsilon
        self.corpus_size = len(corpus)
        if not self.corpus_size:
            raise ValueError("BM25 needs at least one document")
        nd: dict[str, int] = {}
        doc_len, num_doc = [], 0
        self.postings: dict[str, tuple[list[int], list[int]]] = {}
        for i, doc in enumerate(corpus):
            doc_len.append(len(doc))
            num_doc += len(doc)
            freqs: dict[str, int] = {}
            for w in doc:
                freqs[w] = freqs.get(w, 0) + 1
            for w, f in freqs.items():
                nd[w] = nd.get(w, 0) + 1
                ids, fs = self.postings.setdefault(w, ([], []))
                ids.append(i)
                fs.append(f)
        self.doc_len = np.array(doc_len)
        self.avgdl = num_doc / self.corpus_size
        self.idf: dict[str, float] = {}
        idf_sum, negative = 0, []
        for w, freq in nd.items():
            idf = math.log(self.corpus_size - freq + 0.5) - math.log(freq + 0.5)
            self.idf[w] = idf
            idf_sum += idf
            if idf < 0:
                negative.append(w)
        self.average_idf = idf_sum / len(self.idf) if self.idf else 0.0
        eps = self.epsilon * self.average_idf
        for w in negative:
            self.idf[w] = eps

    def get_scores(self, query: Sequence[str]) -> np.ndarray:
        score = np.zeros(self.corpus_size)
        for q in query:
            q_freq = np.zeros(self.corpus_size, dtype=np.int64)
            post = self.postings.get(q)
            if post is not None:
                q_freq[post[0]] = post[1]
            score += (self.idf.get(q) or 0) * (q_freq * (self.k1 + 1) /
                                               (q_freq + self.k1 * (1 - self.b + self.b * self.doc_len / self.avgdl)))
        return score


class _Tokens:
    def __init__(self, tokenizer):
        self.tok = tokenizer
        self._cache: dict[str, list[str]] = {}

    def __call__(self, text: str) -> list[str]:
        t = self._cache.get(text)
        if t is None:
            t = self._cache[text] = list(self.tok(text)) or [BM25_EMPTY_TOKEN]
        return t


class HaystackScorer:
    """Turn-level scores max-pooled per unit; empty units score -inf.  ``vectors`` is required for the hybrid retriever."""

    def __init__(self, unit_turns: Sequence[Sequence[str]], tokens: Callable[[str], list[str]], retriever: str,
                 vectors: Callable[[Sequence[str], str], np.ndarray] | None = None, query_prefix: str = "", doc_prefix: str = ""):
        if retriever not in RETRIEVERS:
            raise ValueError("unknown retriever")
        self.n, self.retriever, self.tokens = len(unit_turns), retriever, tokens
        self.turns, sess = [], []
        for i, ts in enumerate(unit_turns):
            for t in ts:
                if t.strip():
                    self.turns.append(t)
                    sess.append(i)
        self.sess_of = np.asarray(sess, dtype=np.int64)
        self.bm = BM25Okapi([tokens(t) for t in self.turns]) if self.turns else None
        self.D = None
        self.vectors, self.query_prefix = vectors, query_prefix
        if self.turns and retriever == "hybrid":
            if vectors is None:
                raise ValueError("the hybrid retriever needs an encoder")
            D = np.asarray(vectors(self.turns, doc_prefix), dtype=np.float32)
            if D.shape[0] != len(self.turns) or not np.isfinite(D).all():
                raise ValueError("turn vectors do not match the haystack turns")
            self.D = D

    def score(self, query: str) -> np.ndarray:
        best = np.full(self.n, -np.inf)
        if not self.turns:
            return best
        turn = np.asarray(self.bm.get_scores(self.tokens(query)), dtype=float)
        if self.retriever == "hybrid":
            from scipy.stats import rankdata
            qv = np.asarray(self.vectors([query], self.query_prefix)[0], dtype=np.float32)
            dense = (self.D @ qv).astype(float)
            turn = 1.0 / (RRF_C + rankdata(-turn, method="average")) + 1.0 / (RRF_C + rankdata(-dense, method="average"))
        if not np.isfinite(turn).all():
            raise ValueError("retriever produced non-finite scores")
        np.maximum.at(best, self.sess_of, turn)
        return best


def tie_key(item_id: str, query_id: str, uid: str) -> str:
    return h(SALT_TIE, item_id, "|", query_id, "|", uid)


def top_hash(best: np.ndarray, uids: Sequence[str], item_id: str, query_id: str, k: int = TOPN_STORE) -> list[int]:
    """Top-k slots under (-score, sha256(SALT_TIE + item|query|uid)); every unit tied at the cutoff enters the tie sort."""
    n = best.size
    kk = min(k, n)
    if kk == 0:
        return []
    thr = np.partition(best, n - kk)[n - kk]
    cand = np.flatnonzero(best >= thr).tolist()
    return sorted(cand, key=lambda i: (-best[i], tie_key(item_id, query_id, uids[i])))[:kk]


def qid_of(bench: str, item_id: str) -> str:
    return f"q:{bench}:{item_id}"


# --------------------------------------------------------------------------------------------------- query-blind controls
def units_features(pool: QIPool) -> dict[str, list]:
    feats: dict[str, list] = {k: [] for k in ("chars", "turns", "mean_turn_len", "position", "non_ascii", "typo_markers")}
    pos = 0
    for u in pool.units:
        if not u.nonempty:
            for k in feats:
                feats[k].append(None)
            continue
        raw = "".join(u.raw_user)
        feats["chars"].append(u.n_chars)
        feats["turns"].append(len(u.turns))
        feats["mean_turn_len"].append(u.n_chars / len(u.turns))
        feats["position"].append(pos)
        feats["non_ascii"].append(sum(1 for ch in raw if ord(ch) > 127))
        feats["typo_markers"].append(sum(raw.count(m) for m in TYPO_MARKERS))
        pos += 1
    return feats


def _auroc(pos: Sequence[float], neg: Sequence[float]) -> float:
    from scipy.stats import rankdata
    pos, neg = list(pos), list(neg)
    if not pos or not neg:
        return float("nan")
    r = rankdata(pos + neg, method="average")
    return (float(np.sum(r[:len(pos)])) - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def leak_scan(qs: QISet, items: Sequence[QIItem]) -> dict:
    """K3: item-mean within-haystack AUROC (gold vs non-gold non-empty units) of each query-blind feature."""
    per: dict[str, list[float]] = {f: [] for f in LEAK_FEATURES}
    for it in items:
        pool = qs.pool_of(it)
        feats, g = units_features(pool), set(gold_slots(pool, it))
        for f in LEAK_FEATURES:
            vals = feats[f]
            a = _auroc([v for s, v in enumerate(vals) if v is not None and s in g],
                       [v for s, v in enumerate(vals) if v is not None and s not in g])
            if math.isfinite(a):
                per[f].append(a)
    res = {}
    for f in LEAK_FEATURES:
        m = float(np.mean(per[f])) if per[f] else float("nan")
        res[f] = {"mean_auroc": m, "decision_value": max(m, 1 - m) if per[f] else float("nan"), "n_items": len(per[f])}
    vals = [r["decision_value"] for r in res.values() if math.isfinite(r["decision_value"])]
    return {"features": res, "max_decision_value": max(vals) if vals else float("nan"),
            "cue_dominated": bool(vals) and max(vals) >= K3_AUROC, "threshold": K3_AUROC}


PRIOR_NAMES = tuple(f"{f}_{d}" for f in ("chars", "turns", "mean_turn_len", "pos") for d in ("desc", "asc"))
_PRIOR_FEATURE = {"chars": "chars", "turns": "turns", "mean_turn_len": "mean_turn_len", "pos": "position"}


def prior_tops(pool: QIPool, item_id: str, k: int = TOPN_STORE) -> dict[str, list[int]]:
    feats, uids, out = units_features(pool), [u.uid for u in pool.units], {}
    for name in PRIOR_NAMES:
        f, d = name.rsplit("_", 1)
        vals = feats[_PRIOR_FEATURE[f]]
        sign = -1.0 if d == "desc" else 1.0
        key = [(0, sign * v) if v is not None else (1, 0.0) for v in vals]
        out[name] = sorted(range(len(vals)), key=lambda i: (key[i], tie_key(item_id, f"prior:{name}", uids[i])))[:min(k, len(vals))]
    return out


# --------------------------------------------------------------------------------------------------- inference
class TwoWay:
    """Item-mean estimate of pair values; two-way (target group x peer group) cluster bootstrap and CR1 cluster t.

    Items weigh equally within a stratum and strata weigh equally.  A bootstrap replicate draws multinomial weights for
    target groups (within strata) and for peer groups jointly; the reported interval is the wider of the two intervals."""

    def __init__(self, d_pairs, peer_groups, groups, strata=None, *, n_boot: int = N_BOOT, seed: int = 0):
        self.n = len(d_pairs)
        self.groups = list(groups)
        self.strata = list(strata) if strata is not None else [None] * self.n
        self.n_boot, self.seed, self.n_boot_dropped = int(n_boot), int(seed), 0
        m = np.asarray([len(d) for d in d_pairs], dtype=np.int64)
        self._vals = np.concatenate([np.asarray(d, dtype=float) for d in d_pairs]) if self.n else np.zeros(0)
        self._item_of = np.repeat(np.arange(self.n), m)
        self._w = np.repeat(1.0 / np.maximum(m, 1), m)
        pg_flat = [g for pgs in peer_groups for g in pgs]
        if len(pg_flat) != self._vals.size:
            raise ValueError("peer groups must align with pair values")
        self._pg_levels = sorted(set(pg_flat), key=str)
        pidx = {g: j for j, g in enumerate(self._pg_levels)}
        self._pg = np.asarray([pidx[g] for g in pg_flat], dtype=np.int64)
        sums = np.bincount(self._item_of, weights=self._vals, minlength=self.n) if self.n else np.zeros(0)
        self.item_vals = np.where(m > 0, sums / np.maximum(m, 1), np.nan)
        self.finite = bool(self.n) and bool(np.isfinite(self.item_vals).all())
        self.levels = sorted(set(self.strata), key=str)
        self._sidx = [np.asarray([i for i in range(self.n) if self.strata[i] == s], dtype=np.int64) for s in self.levels]
        self._st = None
        self._stats = None

    def _stratum_stats(self):
        if self._st is None:
            out = []
            for idx in self._sidx:
                x = self.item_vals[idx]
                ybar = float(x.mean())
                acc: dict = defaultdict(float)
                for i in idx.tolist():
                    acc[self.groups[i]] += float(self.item_vals[i]) - ybar
                g = len(acc)
                se = math.sqrt(g / (g - 1) * sum(v * v for v in acc.values())) / x.size if g >= 2 else float("nan")
                out.append((ybar, float(se), g))
            self._st = out
        return self._st

    @property
    def est(self) -> float:
        return float(np.mean([s[0] for s in self._stratum_stats()])) if self.finite else float("nan")

    def t_interval(self, alpha: float) -> tuple[float, float]:
        from scipy import stats as sps
        if not self.finite:
            return float("nan"), float("nan")
        st = self._stratum_stats()
        S = len(st)
        est = float(np.mean([s[0] for s in st]))
        if any(not math.isfinite(s[1]) for s in st):
            return float("nan"), float("nan")
        a = [s[1] ** 2 / S ** 2 for s in st]
        se = math.sqrt(sum(a))
        if S == 1:
            df = st[0][2] - 1
        else:
            den = sum(ai ** 2 / (s[2] - 1) for ai, s in zip(a, st))
            df = (sum(a) ** 2 / den) if den > 0 else float(sum(s[2] - 1 for s in st))
        if se == 0:
            return est, est
        q = float(sps.t.ppf(1 - alpha / 2, df))
        return est - q * se, est + q * se

    def boot_stats(self) -> np.ndarray:
        if self._stats is not None:
            return self._stats
        if not self.finite:
            self._stats = np.full(0, np.nan)
            return self._stats
        Gp, B = len(self._pg_levels), self.n_boot
        rng = np.random.default_rng(self.seed)
        Wp = rng.multinomial(Gp, np.full(Gp, 1.0 / Gp), size=B).astype(float)
        item_stratum = np.empty(self.n, dtype=np.int64)
        for si, idx in enumerate(self._sidx):
            item_stratum[idx] = si
        pair_stratum = item_stratum[self._item_of]
        per = []
        for si, idx in enumerate(self._sidx):
            tg = sorted({self.groups[i] for i in idx.tolist()}, key=str)
            tpos = {g: j for j, g in enumerate(tg)}
            item_t = np.full(self.n, -1, dtype=np.int64)
            for i in idx.tolist():
                item_t[i] = tpos[self.groups[i]]
            sel = pair_stratum == si
            cell = item_t[self._item_of[sel]] * Gp + self._pg[sel]
            S = np.bincount(cell, weights=self._vals[sel] * self._w[sel], minlength=len(tg) * Gp).reshape(len(tg), Gp)
            N = np.bincount(cell, weights=self._w[sel], minlength=len(tg) * Gp).reshape(len(tg), Gp)
            Wt = rng.multinomial(len(tg), np.full(len(tg), 1.0 / len(tg)), size=B).astype(float)
            with np.errstate(invalid="ignore", divide="ignore"):
                per.append(((Wt @ S) * Wp).sum(axis=1) / ((Wt @ N) * Wp).sum(axis=1))
        stats = np.mean(np.vstack(per), axis=0)
        self.n_boot_dropped = int((~np.isfinite(stats)).sum())
        self._stats = stats[np.isfinite(stats)]
        return self._stats

    def interval(self, alpha: float = ALPHA) -> dict:
        est, t_iv = self.est, self.t_interval(alpha)
        s = self.boot_stats()
        b_iv = (float("nan"), float("nan"))
        if s.size >= 2 and len(set(self.groups)) >= 2:
            lo, hi = np.quantile(s, [alpha / 2, 1 - alpha / 2])
            b_iv = (float(lo), float(hi))
        vals = (est,) + tuple(t_iv) + b_iv
        if not all(math.isfinite(v) for v in vals):
            return {"estimate": est, "t": list(t_iv), "bootstrap": list(b_iv), "lo": float("nan"), "hi": float("nan")}
        return {"estimate": est, "t": list(t_iv), "bootstrap": list(b_iv), "lo": min(t_iv[0], b_iv[0]), "hi": max(t_iv[1], b_iv[1])}


def _pair_values(rows, *, null: str, k: int, scale: str):
    d, pg, groups, strata, qi, nulls = [], [], [], [], [], []
    counts = {"starved": 0, "degenerate_null": 0, "no_support": 0}
    for r in rows:
        if r["starved"]:
            counts["starved"] += 1
            continue
        hits = np.asarray([int(bool(set(t[:k]) & set(r["gold"]))) for t in r["wrong_tops"]], dtype=float)
        if null == "placebo":
            if not r["placebo_support"]:
                counts["no_support"] += 1
                continue
            base = np.asarray([sum(1 for s in r["placebo_sets"] if set(t[:k]).intersection(s)) / len(r["placebo_sets"])
                               for t in r["wrong_tops"]], dtype=float)
            nv = float(base.mean())
        else:
            nv = float(r["uniform" if null == "uniform" else "turn_weighted"][k])
            base = np.full(hits.size, nv)
        if scale == "kappa":
            if 1.0 - nv <= DEGENERATE_NULL_EPS:
                counts["degenerate_null"] += 1
                continue
            vals = (hits - base) / (1.0 - nv)
        else:
            vals = 100.0 * (hits - base)
        d.append(vals)
        pg.append(r["peer_groups"])
        groups.append(r["group"])
        strata.append(r.get("stratum"))
        qi.append(float(hits.mean()))
        nulls.append(nv)
    return {"d": d, "peer_groups": pg, "groups": groups, "strata": strata, "counts": counts,
            "qi_mean": float(np.mean(qi)) if qi else float("nan"), "null_mean": float(np.mean(nulls)) if nulls else float("nan")}


def _mean(xs) -> float:
    xs = [x for x in xs if x is not None and math.isfinite(x)]
    return float(np.mean(xs)) if xs else float("nan")


# --------------------------------------------------------------------------------------------------- driver
def make_encoder_vectors(encoder, qs: QISet, sample: Sequence[QIItem], queries: Iterable[str], *, query_prefix: str,
                         doc_prefix: str):
    """Encode every scoring turn of the sampled haystacks, then every query, in the registered pass order."""
    from .dense import VectorCache
    cache = VectorCache(encoder)
    docs = [t for pid in sorted({it.pool_id for it in sample}) for u in qs.pools[pid].units for t in u.turns]
    cache.encode_pass(docs, doc_prefix)
    cache.encode_pass(sorted(set(queries)), query_prefix)
    return cache


def run_qi(qs: QISet, *, retriever: str = "bm25", tokenizer=None, encoder=None, k: int = K_PRIMARY, ks: Sequence[int] = K_ALL,
           n_wrong: int = N_WRONG, n_boot: int = N_BOOT, per_group_cap: int | None = None, total_cap: int | None = None,
           stratify_split: bool = False, encoder_description: Mapping | None = None) -> dict:
    """One atlas row: QI any-gold@k against uniform, turn-weighted and matched-placebo nulls, kappa with intervals."""
    from .dense import S16_HYBRID
    if retriever not in RETRIEVERS:
        raise ValueError("unknown retriever")
    if retriever == "hybrid" and encoder is None:
        raise ValueError("the hybrid retriever needs an encoder")
    ks = tuple(sorted(set(int(x) for x in ks) | {int(k)}))
    if any(x < 1 or x > TOPN_STORE for x in ks) or n_wrong < 1:
        raise ValueError("k must lie in 1..10 and n_wrong must be positive")
    if tokenizer is None:
        from .tokenizer import Tokenizer
        tokenizer = Tokenizer("default", stemmer="rust")
    tokens = _Tokens(tokenizer)
    b = qs.name
    pop, sample, counts = sample_plan(qs, per_group_cap=per_group_cap, total_cap=total_cap)
    if len(sample) < 2:
        raise ValueError("fewer than two sampled items")
    selector = PeerSelector(qs, pop)
    by_id = {it.item_id: it for it in pop}
    qtext = {qid_of(b, it.item_id): sanitize_text(it.question) for it in pop}
    excluded = Counter()
    rows = []
    for it in sample:
        pool = qs.pool_of(it)
        g = gold_slots(pool, it)
        live = [u for u in pool.units if u.nonempty]
        gset = set(g)
        gw = [len(u.turns) for u in live if u.slot in gset]
        nw = [len(u.turns) for u in live if u.slot not in gset]
        pl = pl_chance(gw, nw, ks, seed=seed_of(SALT_PL, b, "|", it.item_id))
        mp = matched_placebo(pool, g, b, it.item_id)
        sel = selector.select(it, n_wrong)
        excluded.update(sel["excluded"])
        rows.append({"item_id": it.item_id, "pool_id": it.pool_id, "group": it.group,
                     "stratum": it.split if stratify_split else None, "n": len(live), "e": len(g), "gold": g,
                     "uniform": {x: chance_any(len(live), len(g), x) for x in ks}, "turn_weighted": pl["p"],
                     "pl_method": pl["method"], "placebo_support": mp["support"], "placebo_sets": mp["sets"],
                     "starved": sel["starved"], "wrong": sel["peers"], "peer_groups": [by_id[p].group for p in sel["peers"]],
                     "priors": prior_tops(pool, it.item_id)})
    vec = None
    if retriever == "hybrid":
        needed = [qtext[qid_of(b, r["item_id"])] for r in rows] + [qtext[qid_of(b, p)] for r in rows for p in r["wrong"]]
        cache = make_encoder_vectors(encoder, qs, sample, needed, query_prefix=S16_HYBRID["query_prefix"],
                                     doc_prefix=S16_HYBRID["doc_prefix"])
        vec = cache.vectors
    by_pool: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_pool[r["pool_id"]].append(r)
    for pid in sorted(by_pool):
        pool = qs.pools[pid]
        uids = [u.uid for u in pool.units]
        scorer = HaystackScorer([u.turns for u in pool.units], tokens, retriever, vec, S16_HYBRID["query_prefix"],
                                S16_HYBRID["doc_prefix"])
        score_cache: dict[str, np.ndarray] = {}
        for r in by_pool[pid]:
            tops = {}
            for qid in [qid_of(b, r["item_id"])] + [qid_of(b, p) for p in r["wrong"]]:
                text = qtext[qid]
                if text not in score_cache:
                    score_cache[text] = scorer.score(text)
                tops[qid] = top_hash(score_cache[text], uids, r["item_id"], qid)
            r["true_top"] = tops[qid_of(b, r["item_id"])]
            r["wrong_tops"] = [tops[qid_of(b, p)] for p in r["wrong"]]
    ok = [r for r in rows if not r["starved"]]
    sup = [r for r in ok if r["placebo_support"]]

    def hit(top, gold, kk):
        return int(bool(set(top[:kk]) & set(gold)))

    rates = {}
    for kk in ks:
        rates[str(kk)] = {
            "QI": _mean([np.mean([hit(t, r["gold"], kk) for t in r["wrong_tops"]]) for r in ok]),
            "uniform": _mean([r["uniform"][kk] for r in ok]),
            "turn_weighted": _mean([r["turn_weighted"][kk] for r in ok]),
            "placebo": _mean([np.mean([sum(1 for s in r["placebo_sets"] if set(t[:kk]).intersection(s)) / len(r["placebo_sets"])
                                       for t in r["wrong_tops"]]) for r in sup]),
            "QI_on_support": _mean([np.mean([hit(t, r["gold"], kk) for t in r["wrong_tops"]]) for r in sup]),
            "n_support": len(sup), "true_question_hit": _mean([hit(r["true_top"], r["gold"], kk) for r in ok]),
            "priors": {name: _mean([hit(r["priors"][name], r["gold"], kk) for r in ok]) for name in PRIOR_NAMES},
        }
    seed = seed_of(SALT_BOOT, b)
    effects = {}
    for null in ("uniform", "turn_weighted", "placebo"):
        for scale in ("kappa", "points"):
            p = _pair_values(rows, null=null, k=k, scale=scale)
            entry = {"n_items": len(p["d"]), "n_clusters": len(set(p["groups"])), "excluded": p["counts"],
                     "qi_mean": p["qi_mean"], "null_mean": p["null_mean"]}
            if len(p["d"]) >= 2 and len(set(p["groups"])) >= 2:
                tw = TwoWay(p["d"], p["peer_groups"], p["groups"], p["strata"] if stratify_split else None, n_boot=n_boot, seed=seed)
                iv = tw.interval(ALPHA)
                entry.update(estimate=iv["estimate"], ci95=[iv["lo"], iv["hi"]], ci95_t=iv["t"], ci95_bootstrap=iv["bootstrap"],
                             bootstrap_dropped=tw.n_boot_dropped)
                if scale == "kappa":
                    entry["inside_margin_0_03_at_95"] = bool(math.isfinite(iv["lo"]) and -MARGIN_KAPPA < iv["lo"] and iv["hi"] < MARGIN_KAPPA)
            else:
                entry.update(estimate=float("nan"), ci95=[float("nan"), float("nan")])
            effects[f"{null}/{scale}"] = entry
    share = len(sup) / len(ok) if ok else 0.0
    scan = leak_scan(qs, sample)
    prior_k = rates[str(k)]["priors"]
    finite_priors = {n: v for n, v in prior_k.items() if math.isfinite(v)}
    report = {
        "schema": SCHEMA_REPORT, "bench": b, "inputs": qs.meta.get("inputs", []),
        "settings": {"retriever": retriever, "k": k, "ks": list(ks), "n_wrong": n_wrong, "n_boot": n_boot, "alpha": ALPHA,
                     "per_group_cap": per_group_cap, "total_cap": total_cap, "stratify_split": stratify_split,
                     "tokenizer": tokenizer.describe() if hasattr(tokenizer, "describe") else "caller supplied",
                     "bm25": {"k1": BM25_K1, "b": BM25_B, "epsilon": BM25_EPSILON},
                     "text": "user-side turns after F1 normalisation; maximum turn score per unit",
                     "ties": "sha256(S16-tie| item | query | unit) ascending",
                     "hybrid": dict(S16_HYBRID) if retriever == "hybrid" else None,
                     "encoder": dict(encoder_description) if encoder_description else None},
        "sample": counts, "adapter_exclusions": qs.meta.get("excluded", {}),
        "peers": {"starved_items": sum(1 for r in rows if r["starved"]), "excluded_candidates": dict(excluded)},
        "turn_weighted_method": dict(Counter(r["pl_method"] for r in rows)),
        "rates": rates, "effects": effects,
        "placebo_support": {"n_support": len(sup), "denominator": len(ok), "share": share,
                            "row_supported": share >= COMMON_SUPPORT_MIN, "threshold": COMMON_SUPPORT_MIN},
        "k3": scan,
        "best_query_blind_prior": {"k": k, "name": max(finite_priors, key=finite_priors.get) if finite_priors else None,
                                   "any_gold": max(finite_priors.values()) if finite_priors else float("nan"),
                                   "note": "selected maximum over eight registered priors; descriptive only"},
        "interpretation": {"turn_weighted_kappa_interpretable": not scan["cue_dominated"],
                           "placebo_describes_row": share >= COMMON_SUPPORT_MIN,
                           "scope": "one retriever stack and unit definition; not a statement about any memory system"},
    }
    assert_text_free(report, qs)
    return report


def assert_text_free(report, qs: QISet, min_len: int = 20) -> None:
    """Refuse a report that contains any question or unit text of at least ``min_len`` characters (exact or substring)."""
    texts = {it.question.strip() for it in qs.items} | {sanitize_text(it.question).strip() for it in qs.items}
    texts |= {t.strip() for p in qs.pools.values() for u in p.units for t in (u.turns + u.raw_user)}
    long_texts = [t for t in texts if len(t) >= min_len]
    exact = set(long_texts)
    strings: list[str] = []

    def walk(x):
        if isinstance(x, str):
            strings.append(x)
        elif isinstance(x, Mapping):
            for key, v in x.items():
                strings.append(str(key))
                walk(v)
        elif isinstance(x, (list, tuple)):
            for v in x:
                walk(v)

    walk(report)
    for s in strings:
        if s.strip() in exact or (len(s) >= min_len and any(t in s for t in long_texts)):
            raise ValueError("report would contain benchmark text")
