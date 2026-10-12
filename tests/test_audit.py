import copy
import json
from dataclasses import replace

import numpy as np
import pytest

from memaudit.audit import feature_matrix, marker_report, oof_scores, replay, report_arrays, run_audit, summarize
from memaudit.features import apply_fix, unit_features
from memaudit.provenance import sha256_file
from memaudit.schema import AuditRow, AuditSet, Unit, unit_hash
from memaudit.stats import auc, expected_tied_hit, random_hit


def planted(groups=6, n=40):
    units, rows = [], []
    for g in range(groups):
        for i in range(n):
            y = i % 2
            # After F1 every within-pool positive/negative pair has identical features.
            text = f"Synthetic unit {g} {i//2} can" + ("’" if y else "'") + "t wait."
            units.append(Unit(f"u{g}-{i}", (("user", text),), rel_pos=i/(n-1), n_units=n))
            rows.append(AuditRow(f"p{g}", len(units)-1, y, f"g{g}"))
    return AuditSet("synthetic", units, rows)


def test_features_reject_query_fields_and_ignore_metadata_ids_positions_labels():
    ds = planted(); base = feature_matrix(ds)
    with pytest.raises(ValueError): Unit.from_dict({"uid": "x", "turns": [], "question": "synthetic probe"})
    mutated = copy.deepcopy(ds)
    mutated.meta["question"] = "synthetic sentinel"
    mutated.units = [replace(u, uid="renamed-"+u.uid, rel_pos=1-u.rel_pos) for u in ds.units]
    mutated.rows = [replace(r, label=1-r.label) for r in ds.rows]
    np.testing.assert_array_equal(base, feature_matrix(mutated))
    assert unit_hash(ds.units[0]) == unit_hash(mutated.units[0])


def test_group_and_pool_guard_and_duplicate_ids():
    ds = planted(); ds.rows[1] = replace(ds.rows[1], group="other")
    with pytest.raises(ValueError): ds.validate()
    ds = planted(); ds.rows.append(ds.rows[0])
    with pytest.raises(ValueError): ds.validate()
    ds = planted(); ds.units[1] = replace(ds.units[1], uid=ds.units[0].uid)
    with pytest.raises(ValueError): ds.validate()


def test_group_cv_masks_duplicates_and_keeps_full_population():
    X = np.arange(12).reshape(6, 2); y = np.array([1, 0, 1, 0, 1, 0])
    out = oof_scores(X, y, [0, 0, 1, 1, 2, 2], ["a", "shared", "b", "shared", "c", "shared"], folds=3)
    assert out["duplicate"].tolist() == [False, True, False, True, False, True]
    assert np.isfinite(out["full"]).all() and np.isnan(out["filtered"])[1::2].all()
    assert all(out["fold"][i] == out["fold"][i+1] for i in (0, 2, 4))


def test_one_class_training_and_invalid_cv():
    result = oof_scores([[0], [1], [2], [3]], [0, 0, 1, 1], [0, 0, 1, 1], list("abcd"), folds=2)
    np.testing.assert_array_equal(result["full"], [1, 1, 0, 0])
    with pytest.raises(ValueError): oof_scores([[0], [1]], [0, 1], [0, 0], list("ab"))


def test_audit_run_replay_fixes_and_determinism(tmp_path):
    ds = planted(); archive = tmp_path/"synthetic.npz"
    a = run_audit(ds, variants=("all", "position_only"), n_boot=50, save=archive)
    b = replay(archive, sha256_file(archive), n_boot=50)
    del b["replay_input"]
    assert a == b
    assert a["variants"]["raw__all"]["full_population"]["auroc_macro"]["mean"] > .95
    assert a["fixes"]["full_population"]["F1"]["verdict"] == "removed"
    c = run_audit(ds, levels=("raw",), variants=("all",), n_boot=50)
    assert a["variants"]["raw__all"] == c["variants"]["raw__all"]
    assert a["variants"]["F1__all"]["full_population"]["auroc_macro"]["mean"] == pytest.approx(.5)
    with np.load(archive, allow_pickle=False) as z:
        arrays = {k: z[k] for k in z.files if k != "meta"}; meta = json.loads(str(z["meta"]))
    with pytest.raises(ValueError): report_arrays(arrays, {**meta, "raw_text": "synthetic sentinel"})


def test_reporting_denominators_degenerate_pools_and_ties():
    r = summarize([0, 0, 1, 1, 2, 2], [0, 0, 1, 1, 2, 2], [1, 0, 1, 0, 1, 1], [.5, .5, np.nan, np.nan, .5, .5], n_boot=50)
    assert r["population_rows"] == 6 and r["rows_with_scores"] == 4 and r["metric_rows"] == 2
    assert r["pools_without_scores"] == 1 and r["pools_single_class_after_mask"] == 1
    assert r["hit@1"]["mean"] == .5 and r["auroc_macro"]["lo"] is None
    assert auc([0, 1], [2, 2]) == .5 and np.isnan(auc([1, 1], [2, 3]))


@pytest.mark.parametrize("n", [2, 4, 6])
def test_tied_hits_match_exhaustive_permutation(n):
    from itertools import combinations
    y = [1, 0] + [0]*(n-2)
    for k in range(1, n+2):
        expected = np.mean([any(y[i] for i in choice) for choice in combinations(range(n), min(k, n))])
        assert expected_tied_hit(y, np.ones(n), k) == pytest.approx(expected)
        assert random_hit(n, 1, k) == pytest.approx(expected)


def test_normalization_idempotent_and_marker_roles():
    text = "**Synthetic** ’ test\u00a0 • line"
    for level in ("F1", "F2"):
        assert apply_fix(apply_fix(text, level), level) == apply_fix(text, level)
    ds = AuditSet("synthetic", [Unit("a", (("assistant", "marker ’"),)), Unit("b", (("user", "plain"),))], [AuditRow("p", 0, 1, "g"), AuditRow("p", 1, 0, "g")])
    assert marker_report(ds)["exact_evidence_pools"] == 1
    assert marker_report(ds, user_only=True)["positive_marked"] == 0
