"""Replica estimators with separate oracle conventions and metric-specific masks."""
from __future__ import annotations

from collections import Counter
from itertools import combinations
import math
import re
import numpy as np

from .provenance import pinned_json, file_info


def _binary(M):
    M = np.asarray(M, float)
    if M.ndim != 2 or M.shape[0] < 1 or M.shape[1] < 2 or not np.isin(M, [0., 1.]).all():
        raise ValueError("nonempty binary matrix with at least two replicates required")
    return M


def _mats(mats):
    if not mats: raise ValueError("at least one group required")
    out = {str(c): _binary(M) for c, M in mats.items()}
    if len({M.shape[1] for M in out.values()}) != 1: raise ValueError("replicate counts must agree across groups")
    return out


def _weights(mats, weighting, planned_counts=None):
    if weighting == "complete_question": counts = {c: len(M) for c, M in mats.items()}
    elif weighting == "planned_group":
        if planned_counts is None or set(planned_counts) != set(mats) or any(planned_counts[c] < len(mats[c]) for c in mats):
            raise ValueError("planned counts must cover exactly the groups and exceed complete counts")
        counts = planned_counts
    elif weighting == "equal_group": counts = {c: 1 for c in mats}
    else: raise ValueError("unknown weighting")
    total = sum(counts.values())
    if total <= 0: raise ValueError("positive population required")
    return {c: n/total for c, n in counts.items()}


def per_question_discordance(matrix):
    M = _binary(matrix); k = M.sum(axis=1); K = M.shape[1]
    return k*(K-k)/math.comb(K, 2)


def oracle_gain(mats, *, weighting="complete_question", planned_counts=None, better_scope="pooled") -> dict:
    """Pairwise union minus mean, and union minus better *aggregate* replica.

    The better-replica choice is global for each pair by default. An explicitly
    requested per_group scope chooses the better replica separately per group.
    Neither statistic describes an implementable answer selector.
    """
    mats = _mats(mats); w = _weights(mats, weighting, planned_counts); K = next(iter(mats.values())).shape[1]
    if better_scope not in ("pooled", "per_group"): raise ValueError("invalid better-replica scope")
    pairs = []; better = []
    for i, j in combinations(range(K), 2):
        a = sum(w[c]*M[:, i].mean() for c, M in mats.items())
        b = sum(w[c]*M[:, j].mean() for c, M in mats.items())
        union = sum(w[c]*np.maximum(M[:, i], M[:, j]).mean() for c, M in mats.items())
        base = max(a, b) if better_scope == "pooled" else sum(w[c]*max(M[:, i].mean(), M[:, j].mean()) for c, M in mats.items())
        pairs.append(union-(a+b)/2); better.append(union-base)
    d = sum(w[c]*per_question_discordance(M).mean() for c, M in mats.items())
    return {"union_minus_mean_pp": 100*float(np.mean(pairs)), "union_minus_better_pp": 100*float(np.mean(better)),
            "correctness_discordance": float(d), "identity_residual_pp": 100*float(np.mean(pairs))-50*float(d),
            "n_questions": sum(len(M) for M in mats.values()), "n_groups": len(mats), "n_replicates": K,
            "n_replica_pairs": math.comb(K, 2), "weighting": weighting, "group_weights": w, "better_scope": better_scope,
            "per_group": {c: {"complete_questions": len(M), "union_minus_mean_pp": 50*float(per_question_discordance(M).mean())} for c, M in mats.items()}}


def oracle_ci(mats, *, n_boot=2000, seed=0, weighting="complete_question", planned_counts=None) -> dict:
    mats = _mats(mats)
    if n_boot < 2: raise ValueError("at least two bootstrap samples required")
    rng = np.random.default_rng(seed)
    def stat(mm):
        weights = _weights(mm, weighting, planned_counts)
        return 50*float(sum(weights[c]*per_question_discordance(M).mean() for c, M in mm.items()))
    vals = np.array([stat({c: M[rng.integers(len(M), size=len(M))] for c, M in mats.items()}) for _ in range(n_boot)])
    K = next(iter(mats.values())).shape[1]; se_store = None
    if K >= 3:
        leave = np.array([stat({c: np.delete(M, s, axis=1) for c, M in mats.items()}) for s in range(K)])
        se_store = float(np.sqrt((K-1)/K * ((leave-leave.mean())**2).sum()))
    se_q = float(vals.std(ddof=1)); se = math.hypot(se_q, se_store or 0); estimate = stat(mats)
    return {"question_bootstrap_ci95_pp": np.quantile(vals, [.025, .975]).tolist(), "question_se_pp": se_q,
            "store_jackknife_se_pp": se_store, "combined_normal_ci95_pp": [estimate-1.96*se, estimate+1.96*se],
            "scope": "within observed groups, question bootstrap plus delete-one-store jackknife; not population-group inference",
            "store_component_unavailable": K < 3}


def union_gain_curve(mats, *, weighting="complete_question", planned_counts=None):
    mats = _mats(mats); w = _weights(mats, weighting, planned_counts); K = next(iter(mats.values())).shape[1]
    base = sum(w[c]*M.mean() for c, M in mats.items()); result = {}
    for size in range(2, K+1):
        union = 0.
        for c, M in mats.items():
            failures = K-M.sum(axis=1).astype(int)
            union += w[c]*np.mean([1-math.comb(int(f), size)/math.comb(K, size) if f >= size else 1. for f in failures])
        result[size] = 100*float(union-base)
    return result


def variance_components(main, planned_counts, reseed=None, judge_only=None) -> dict:
    main = _mats(main); w = _weights(main, "planned_group", planned_counts)
    def check(other):
        other = _mats(other)
        if set(main) != set(other) or any(len(main[c]) != len(other[c]) for c in main):
            raise ValueError("variance blocks must use the same aligned complete questions")
        return other
    obs = {c: float(np.var(M.mean(axis=0), ddof=1)) for c, M in main.items()}
    vobs = sum(w[c]**2*v for c, v in obs.items())
    out = {"V_observed_pp2": 1e4*vobs, "SD_observed_pp": 100*math.sqrt(vobs),
           "observed_by_group_pp2": {c: 1e4*v for c, v in obs.items()}, "group_weights": w,
           "n_questions": sum(len(M) for M in main.values()),
           "assumptions": "nested exchangeable replicates; question-independent conditional reader/judge draws; components are model-based, not causal shares"}
    def qvar(mats):
        result = 0.
        for c, M in mats.items():
            R = M.shape[1]; k = M.sum(axis=1)
            result += w[c]**2 * np.sum(k*(R-k)/(R*(R-1))) / len(M)**2
        return float(result)
    if judge_only is not None and reseed is None: raise ValueError("judge component requires reader+judge reseeds")
    if reseed is not None:
        reseed = check(reseed); rj = qvar(reseed)
        rj_aggregate = sum(w[c]**2*float(np.var(M.mean(axis=0), ddof=1)) for c, M in reseed.items())
        out.update(V_reader_judge_pp2=1e4*rj, V_write_signed_pp2=1e4*(vobs-rj), SD_write_pp=100*math.sqrt(max(0, vobs-rj)),
                   V_reader_judge_aggregate_pp2=1e4*rj_aggregate, V_write_aggregate_signed_pp2=1e4*(vobs-rj_aggregate))
        if judge_only is not None:
            j = qvar(check(judge_only)); out.update(V_judge_pp2=1e4*j, V_reader_signed_pp2=1e4*(rj-j))
    return out


def placebo_winner(sigma_pp, *, n_arms=20, n_resamples=10000, threshold_pp=2., seed=0):
    if not np.isfinite(sigma_pp) or sigma_pp < 0 or n_arms < 1 or n_resamples < 1:
        raise ValueError("invalid Gaussian simulation parameters")
    rng = np.random.default_rng(seed); d = np.empty(n_resamples)
    for start in range(0, n_resamples, 1000):
        stop = min(start+1000, n_resamples); z = rng.normal(0, sigma_pp, (stop-start, n_arms+1))
        d[start:stop] = z[:, 1:].max(axis=1)-z[:, 0]
    return {"kind": "Gaussian simulation; no measured optimization campaign", "sigma_pp": sigma_pp, "n_arms": n_arms,
            "n_resamples": n_resamples, "threshold_pp": threshold_pp, "P_ge": float((d >= threshold_pp).mean()),
            "P_gt": float((d > threshold_pp).mean()), "mean_gain_pp": float(d.mean())}


def fact_jaccard(a, b, *, tau=.5, tokenizer=None) -> dict:
    """Session-constrained greedy one-to-one matching; no semantic claim.

    Default tokens use the registered lowercase, stop-worded Rust Snowball
    tokenizer (CPU package dependency, no model download).
    tau=1 uses normalized exact-string multiset intersection.
    """
    if set(a) != set(b) or not 0 <= tau <= 1: raise ValueError("same session keys and tau in [0,1] required")
    from .tokenizer import Tokenizer
    token = tokenizer or Tokenizer()
    matched = na = nb = 0
    for session in a:
        aa, bb = a[session], b[session]; na += len(aa); nb += len(bb)
        if tau == 1:
            norm = lambda s: " ".join(re.sub(r"[^\w\s]", " ", s.lower()).split())
            matched += sum((Counter(map(norm, aa)) & Counter(map(norm, bb))).values()); continue
        sa, sb = [set(token(s)) for s in aa], [set(token(s)) for s in bb]; candidates = []
        for i, x in enumerate(sa):
            for j, y in enumerate(sb):
                sim = len(x&y)/len(x|y) if x|y else 1.
                if sim >= tau: candidates.append((-sim, i, j))
        used_a, used_b = set(), set()
        for _, i, j in sorted(candidates):
            if i not in used_a and j not in used_b:
                used_a.add(i); used_b.add(j); matched += 1
    return {"matched": matched, "n_a": na, "n_b": nb, "jaccard": matched/(na+nb-matched) if na+nb-matched else 1.}


def apply_thresholds(card, thresholds) -> dict:
    """Caller-declared descriptive thresholds; historical rules are not defaults."""
    from .rules import validate_card
    card = validate_card(card, {"SD_write_pp": None, "J_median": 1, "union_minus_mean_pp": 50, "P_gt": 1})
    needed = {"sd_dead_max", "j_dead_min", "gain_dead_below_pp", "placebo_dead_below"}
    if set(thresholds) != needed: raise ValueError("all explicit thresholds are required")
    if any(type(v) not in (int, float) or not np.isfinite(v) or v < 0 for v in thresholds.values()) or thresholds["j_dead_min"] > 1 or thresholds["placebo_dead_below"] > 1:
        raise ValueError("invalid thresholds")
    def known(*keys): return all(card.get(k) is not None and np.isfinite(card[k]) for k in keys)
    fired = {"write": (card["SD_write_pp"] <= thresholds["sd_dead_max"] and card["J_median"] >= thresholds["j_dead_min"]) if known("SD_write_pp", "J_median") else None,
             "gain": (card["union_minus_mean_pp"] < thresholds["gain_dead_below_pp"]-1e-12) if known("union_minus_mean_pp") else None,
             "placebo": (card["P_gt"] < thresholds["placebo_dead_below"]) if known("P_gt") else None}
    return {"status": "STOP" if any(fired.values()) else "NOT_EVALUABLE" if None in fired.values() else "PASS", "fired": fired, "thresholds": thresholds}


def replay_document(document, *, n_boot=2000, seed=0, fact_sets=None) -> dict:
    allowed = {"schema", "questions", "planned_counts", "oracle_required", "variance_required", "weighting", "better_scope", "thresholds", "jaccard_tau"}
    if set(document)-allowed or document.get("schema") != "memaudit-replica/1": raise ValueError("unsupported replica schema or fields")
    rows = document["questions"]; fields = ("main", "reseed", "judge_only", "raw"); seen = set(); widths = {}
    if not rows: raise ValueError("empty question population")
    for row in rows:
        if set(row)-{"id", "group", *fields}: raise ValueError("replica rows must contain IDs and numeric outcomes only")
        if not isinstance(row.get("id"), str) or not isinstance(row.get("group"), str): raise ValueError("string question/group IDs required")
        if row["id"] in seen: raise ValueError("duplicate question ID")
        seen.add(row["id"])
        for field in fields:
            if field not in row: continue
            values = row[field]
            if not isinstance(values, list) or len(values) < 1 or any(v is not None and (type(v) not in (int, bool) or v not in (0, 1)) for v in values): raise ValueError("binary values or nulls required")
            if widths.setdefault(field, len(values)) != len(values): raise ValueError("inconsistent replicate widths")
    planned = document["planned_counts"]; groups = sorted({r["group"] for r in rows})
    if set(planned) != set(groups) or any(not isinstance(n, int) or n < 1 for n in planned.values()): raise ValueError("invalid planned population")
    if any(planned[g] < sum(r["group"] == g for r in rows) for g in groups): raise ValueError("observed rows exceed planned group count")
    def align(required):
        if not required or "main" not in required or set(required)-set(fields): raise ValueError("mask must require main and known blocks")
        mask = [all(field in r and all(v is not None for v in r[field]) for field in required) for r in rows]
        selected = [r for r, ok in zip(rows, mask) if ok]
        if any(not any(r["group"] == g for r in selected) for g in groups): raise ValueError("a planned group has no complete questions under this mask")
        mats = {field: {g: np.asarray([r[field] for r in selected if r["group"] == g], float) for g in groups} for field in required}
        return mats, {"required_blocks": list(required), "planned_questions": sum(planned.values()), "input_rows": len(rows),
                      "complete_questions": len(selected), "excluded_input_rows": len(rows)-len(selected),
                      "missing_planned_rows": sum(planned.values())-len(rows), "complete_by_group": {g: sum(r["group"] == g for r in selected) for g in groups},
                      "row_mask": mask}
    oracle_required = document.get("oracle_required", ["main"]); mats, mask = align(oracle_required)
    weighting = document.get("weighting", "complete_question")
    result = {"schema": "memaudit-replica-report/1", "oracle_mask": mask,
              "oracle": oracle_gain(mats["main"], weighting=weighting, planned_counts=planned, better_scope=document.get("better_scope", "pooled")),
              "oracle_ci": oracle_ci(mats["main"], n_boot=n_boot, seed=seed, weighting=weighting, planned_counts=planned),
              "best_of_k_oracle_gain_pp": union_gain_curve(mats["main"], weighting=weighting, planned_counts=planned),
              "limits": "correctness labels, not answer-string or true-answer disagreement; observed groups and masks condition every estimate"}
    required = document.get("variance_required")
    from .rules import Thresholds, evaluate
    thresholds = Thresholds(**document["thresholds"]) if "thresholds" in document else None
    if required:
        blocks, vm = align(required); result["variance_mask"] = vm
        result["variance"] = variance_components(blocks["main"], planned, blocks.get("reseed"), blocks.get("judge_only"))
        result["placebo"] = placebo_winner(result["variance"]["SD_observed_pp"], seed=seed,
            n_arms=thresholds.n_placebo if thresholds else 20, threshold_pp=thresholds.kill_placebo_pts if thresholds else 2.)
    if fact_sets is not None:
        if set(fact_sets) != set(groups): raise ValueError("fact sets must cover the outcome groups")
        values = []; tau = document.get("jaccard_tau", .5)
        for group in groups:
            stores = fact_sets[group]
            if not isinstance(stores, list) or len(stores) != widths["main"]: raise ValueError("fact stores must match main replicate count")
            for store in stores:
                if not isinstance(store, dict) or any(not isinstance(v, list) or any(not isinstance(t, str) for t in v) for v in store.values()):
                    raise ValueError("fact stores require session-to-fact-list mappings")
            values.extend(fact_jaccard(a, b, tau=tau)["jaccard"] for a, b in combinations(stores, 2))
        from .tokenizer import Tokenizer
        result["jaccard"] = {"median": float(np.median(values)), "mean": float(np.mean(values)), "n_group_pairs": len(values), "tau": tau, "tokenizer": Tokenizer().describe(),
                             "scope": "equal group-pair weighting; greedy session-constrained lexical matching, not semantic fact identity"}
    if thresholds:
        result["rules"] = evaluate({"SD_W_pts": result.get("variance", {}).get("SD_write_pp"),
            "J_median": result.get("jaccard", {}).get("median"), "G_self_pts": result["oracle"]["union_minus_mean_pp"],
            "P_placebo_ge": result.get("placebo", {}).get("P_ge"), "P_placebo_gt": result.get("placebo", {}).get("P_gt")}, thresholds)
    return result


def replay(path, expected_sha256, *, n_boot=2000, seed=0, facts_path=None, facts_sha256=None):
    if (facts_path is None) != (facts_sha256 is None): raise ValueError("fact sets require a path and hash pin together")
    facts = pinned_json(facts_path, facts_sha256) if facts_path is not None else None
    document = pinned_json(path, expected_sha256); result = replay_document(document, n_boot=n_boot, seed=seed, fact_sets=facts)
    result["input"] = file_info(path, expected_sha256)
    if facts_path is not None: result["facts_input"] = file_info(facts_path, facts_sha256)
    return result
