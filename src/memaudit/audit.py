"""Grouped CPU audit, explicit full/filtered populations, and numeric-only replay."""
from __future__ import annotations

import json
import re
from pathlib import Path
import numpy as np

from . import features as F
from .schema import AuditSet, unit_hash
from .stats import auc, cluster_mean_ci, expected_tied_hit, random_hit
from .provenance import file_info

RAW_VARIANTS = ("all", "only_typography", "only_format", "only_length", "only_lexical", "drop_typography", "drop_format", "drop_length", "drop_lexical", "position_only")
FIXED_VARIANTS = ("all", "only_typography", "only_format", "only_length", "only_lexical")


def _adapter_metadata(meta):
    """Keep verified input digests and numeric adapter counters, never free text."""
    result = {}
    for key, value in meta.items():
        if key == "inputs":
            if not isinstance(value, list): raise ValueError("input provenance must be a list")
            for entry in value:
                if set(entry) != {"sha256", "bytes"} or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) or type(entry["bytes"]) is not int or entry["bytes"] < 0:
                    raise ValueError("invalid input provenance")
            result[key] = value
        elif re.fullmatch(r"[a-z][a-z0-9_]{0,63}", key) and type(value) in (int, bool):
            result[key] = value
    return result


def feature_matrix(dataset: AuditSet, level: str = "raw") -> np.ndarray:
    dataset.validate()
    return np.asarray([F.unit_features([(r, F.apply_fix(t, level)) for r, t in u.turns], u.user_role) for u in dataset.units], dtype=float)


def variant_columns(variant: str) -> list[int]:
    if variant == "all":
        return list(range(len(F.FEATURE_NAMES)))
    kind, group = variant.split("_", 1)
    cols = F.GROUP_INDEX[group]
    if kind == "only":
        return cols
    if kind == "drop":
        return [i for i in range(len(F.FEATURE_NAMES)) if i not in cols]
    raise ValueError("unknown feature variant")


def oof_scores(X, y, groups, hashes, *, folds: int = 5, seed: int = 0) -> dict:
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.model_selection import GroupKFold
    from threadpoolctl import threadpool_limits
    X, y, groups, hashes = np.asarray(X, float), np.asarray(y), np.asarray(groups), np.asarray(hashes)
    n = len(y)
    if X.ndim != 2 or X.shape[0] != n or groups.shape != (n,) or hashes.shape != (n,) or not np.isfinite(X).all() or not np.isin(y, [0, 1]).all():
        raise ValueError("invalid CV arrays")
    count = len(np.unique(groups))
    if count < 2 or folds < 2:
        raise ValueError("grouped CV requires at least two groups and folds")
    score = np.full(n, np.nan); duplicate = np.zeros(n, bool); fold = np.full(n, -1)
    for j, (tr, te) in enumerate(GroupKFold(n_splits=min(folds, count)).split(X, y, groups)):
        fold[te] = j
        duplicate[te] = np.isin(hashes[te], hashes[tr])
        if len(np.unique(y[tr])) == 1:
            score[te] = float(y[tr].mean())
        else:
            with threadpool_limits(limits=1):
                model = HistGradientBoostingClassifier(max_iter=200, learning_rate=.05, max_depth=4,
                    l2_regularization=1., early_stopping=False, random_state=seed)
                model.fit(X[tr], y[tr]); score[te] = model.predict_proba(X[te])[:, 1]
    return {"full": score, "filtered": np.where(duplicate, np.nan, score), "duplicate": duplicate, "fold": fold}


def summarize(pools, groups, labels, scores, *, ks=(1, 5, 10), n_boot=2000, seed=0) -> dict:
    p, g, y, s = np.asarray(pools), np.asarray(groups), np.asarray(labels), np.asarray(scores, float)
    if y.ndim != 1 or any(a.shape != y.shape for a in (p, g, s)) or not np.isin(y, [0, 1]).all() or np.isinf(s).any():
        raise ValueError("invalid report arrays")
    if any(k < 1 for k in ks):
        raise ValueError("hit@k requires positive k")
    valid = np.isfinite(s); metrics = {"auroc_macro": []}
    metrics.update({f"hit@{k}": [] for k in ks}); random = {k: [] for k in ks}
    clusters = []; n_metric_rows = 0; lost = 0; one_class = 0
    for pool in np.unique(p):
        base = p == pool
        if len(np.unique(g[base])) != 1:
            raise ValueError("ranking pool crosses CV groups")
        mask = base & valid
        if not mask.any():
            lost += 1; continue
        yy, ss = y[mask], s[mask]; e = int(yy.sum())
        if e == 0 or e == len(yy):
            one_class += 1; continue
        clusters.append(g[mask][0]); n_metric_rows += len(yy)
        metrics["auroc_macro"].append(auc(yy, ss))
        for k in ks:
            metrics[f"hit@{k}"].append(expected_tied_hit(yy, ss, k))
            random[k].append(random_hit(len(yy), e, k))
    result = {
        "population_rows": len(y), "population_positives": int(y.sum()), "population_pools": len(np.unique(p)),
        "population_groups": len(np.unique(g)), "rows_with_scores": int(valid.sum()),
        "positive_rows_with_scores": int(y[valid].sum()), "masked_rows": int((~valid).sum()),
        "masked_positives": int(y[~valid].sum()), "metric_rows": n_metric_rows, "metric_pools": len(clusters),
        "pools_without_scores": lost, "pools_single_class_after_mask": one_class,
        "auroc_pooled": auc(y[valid], s[valid]) if valid.any() else None,
        "tie_policy": "uniform random order within tied scores, analytically averaged",
        "ci_scope": "cluster resampling conditional on fitted predictions; excludes training variability",
    }
    for key, values in metrics.items():
        result[key] = cluster_mean_ci(values, clusters, n_boot=n_boot, seed=seed)
    for k in ks:
        result[f"hit@{k}"]["random"] = float(np.mean(random[k])) if random[k] else None
    return result


def report_arrays(arrays: dict, meta: dict, *, n_boot: int = 2000) -> dict:
    if meta.get("schema") != "memaudit-audit/1":
        raise ValueError("unsupported audit replay schema")
    allowed_meta = {"schema", "name", "seed", "folds", "feature_names", "levels", "variants", "adapter", "full_population_caveat"}
    if set(meta)-allowed_meta or not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", meta.get("name", "")):
        raise ValueError("invalid audit metadata fields")
    if meta.get("feature_names") != F.FEATURE_NAMES or type(meta.get("seed")) is not int or type(meta.get("folds")) is not int:
        raise ValueError("invalid audit feature metadata")
    if not set(meta.get("levels", [])) <= {"raw", "F1", "F2"}:
        raise ValueError("invalid audit levels")
    v = meta.get("variants")
    if v != "registered raw/fixed groups" and (not isinstance(v, list) or not set(v) <= set(RAW_VARIANTS)):
        raise ValueError("invalid variant metadata")
    meta = {k: v for k, v in meta.items() if k != "full_population_caveat"}
    meta["adapter"] = _adapter_metadata(meta.get("adapter", {}))
    y, p, g = (arrays[k] for k in ("label", "pool", "group"))
    for key in ("pool", "group"):
        if arrays[key].dtype.kind not in "iu" or (arrays[key] < 0).any():
            raise ValueError("replay uses nonnegative numeric pool/group codes")
    allowed_arrays = {"label", "pool", "group", "duplicate", "fold", "X_raw"}
    if any(k not in allowed_arrays and not re.fullmatch(r"score__(raw|F1|F2)__(all|position_only|(?:only|drop)_(?:typography|format|length|lexical))", k) for k in arrays):
        raise ValueError("unknown replay array")
    if arrays["duplicate"].dtype.kind != "b" or arrays["fold"].dtype.kind not in "iu" or (arrays["fold"] < 0).any():
        raise ValueError("invalid duplicate mask or fold assignments")
    duplicate = arrays["duplicate"]
    if duplicate.shape != y.shape or arrays["fold"].shape != y.shape:
        raise ValueError("mask/fold lengths do not match population")
    for c in np.unique(g):
        if len(np.unique(arrays["fold"][g == c])) != 1:
            raise ValueError("CV group crosses folds")
    out = {"schema": "memaudit-audit-report/1", "meta": meta, "variants": {},
           "duplicate_rows": int(duplicate.sum()), "duplicate_positive_rows": int(y[duplicate].sum())}
    for key, s in arrays.items():
        if not key.startswith("score__"):
            continue
        if not np.isfinite(s).all():
            raise ValueError("full-population OOF predictions must be finite")
        out["variants"][key[7:]] = {
            "full_population": summarize(p, g, y, s, n_boot=n_boot, seed=meta["seed"]),
            "duplicate_filtered": summarize(p, g, y, np.where(duplicate, np.nan, s), n_boot=n_boot, seed=meta["seed"]),
        }
    if not out["variants"]:
        raise ValueError("replay has no predictions")
    if "X_raw" in arrays:
        X = arrays["X_raw"]
        if X.shape != (len(y), len(F.FEATURE_NAMES)) or not np.isfinite(X).all():
            raise ValueError("invalid univariate feature arrays")
        eligible = [p == pool for pool in np.unique(p) if 0 < y[p == pool].sum() < (p == pool).sum()]
        out["univariate_raw"] = {name: float(np.mean([auc(y[m], X[m, j]) for m in eligible])) if eligible else None for j, name in enumerate(F.FEATURE_NAMES)}
        out["univariate_population"] = "all rows in full-population pools with both classes; signed diagnostic AUROCs"
    out["fixes"] = {}
    for population in ("full_population", "duplicate_filtered"):
        raw = out["variants"].get("raw__all", {}).get(population, {}).get("auroc_macro", {}).get("mean")
        fixes = {}
        for level in ("F1", "F2"):
            fixed = out["variants"].get(level+"__all", {}).get(population, {}).get("auroc_macro", {}).get("mean")
            verdict = "undefined" if raw is None or fixed is None else "removed" if fixed <= .55 else "reduced" if fixed-.5 <= .5*(raw-.5) else "persists"
            fixes[level] = {"residual_auroc_macro": fixed, "verdict": verdict}
        out["fixes"][population] = fixes
    return out


def run_audit(dataset: AuditSet, *, levels=("raw", "F1", "F2"), variants=None,
              folds=5, seed=0, n_boot=2000, save: str | Path | None = None) -> dict:
    dataset.validate()
    ui = np.array([r.unit for r in dataset.rows]); y = np.array([r.label for r in dataset.rows])
    p = np.unique([r.pool for r in dataset.rows], return_inverse=True)[1]
    g = np.unique([r.group for r in dataset.rows], return_inverse=True)[1]
    h = np.array([unit_hash(dataset.units[i]) for i in ui])
    pos = np.array([F.position_features(r.rel_pos if r.rel_pos is not None else dataset.units[r.unit].rel_pos,
                     r.n_units if r.n_units is not None else dataset.units[r.unit].n_units) for r in dataset.rows])
    arrays = {"pool": p, "group": g, "label": y}
    meta = {"schema": "memaudit-audit/1", "name": dataset.name, "seed": seed,
            "folds": min(folds, len(np.unique(g))), "feature_names": F.FEATURE_NAMES,
            "levels": list(levels), "variants": list(variants) if variants is not None else "registered raw/fixed groups", "adapter": _adapter_metadata(dataset.meta),
            "full_population_caveat": "contains cross-group exact duplicates; report beside filtered estimates"}
    for level in levels:
        X = feature_matrix(dataset, level)[ui]
        if level == "raw": arrays["X_raw"] = X
        for variant in (variants if variants is not None else RAW_VARIANTS if level == "raw" else FIXED_VARIANTS):
            if variant == "position_only" and level != "raw":
                continue
            cols = pos if variant == "position_only" else X[:, variant_columns(variant)]
            result = oof_scores(cols, y, g, h, folds=folds, seed=seed)
            arrays[f"score__{level}__{variant}"] = result["full"]
            arrays["duplicate"], arrays["fold"] = result["duplicate"], result["fold"]
    report = report_arrays(arrays, meta, n_boot=n_boot)
    if save is not None:
        Path(save).parent.mkdir(parents=True, exist_ok=True)
        with Path(save).open("wb") as f:
            np.savez_compressed(f, meta=json.dumps(meta), **arrays)
    return report


def replay(path: str | Path, expected_sha256: str, *, n_boot=2000) -> dict:
    pin = file_info(path, expected_sha256)
    with np.load(path, allow_pickle=False) as z:
        arrays = {k: z[k] for k in z.files if k != "meta"}; meta = json.loads(str(z["meta"]))
    result = report_arrays(arrays, meta, n_boot=n_boot)
    result["replay_input"] = pin
    return result


def marker_report(dataset: AuditSet, marker: str = "\u2019", *, user_only=False) -> dict:
    """Full-population descriptive marker counts; no fitting or answer generation."""
    dataset.validate()
    if not marker:
        raise ValueError("marker must be nonempty")
    flags = [any(marker in t for r, t in u.turns if not user_only or r == u.user_role) for u in dataset.units]
    y = np.array([r.label for r in dataset.rows]); s = np.array([flags[r.unit] for r in dataset.rows], float)
    p = np.array([r.pool for r in dataset.rows]); g = np.array([r.group for r in dataset.rows])
    exact = sum(np.array_equal(s[p == pool].astype(int), y[p == pool]) for pool in np.unique(p))
    return {"schema": "memaudit-marker/1", "input": _adapter_metadata(dataset.meta).get("inputs"), "marker_codepoints": [f"U+{ord(c):04X}" for c in marker],
            "roles": "user only" if user_only else "all", "positive_marked": int(s[y == 1].sum()), "positive_total": int(y.sum()),
            "negative_marked": int(s[y == 0].sum()), "negative_total": int((y == 0).sum()),
            "exact_evidence_pools": int(exact), "total_pools": len(np.unique(p)),
            "report": summarize(p, g, y, s)}
