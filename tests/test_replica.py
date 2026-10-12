import copy
from itertools import combinations
import math

import numpy as np
import pytest

from memaudit.replica import (apply_thresholds, fact_jaccard, oracle_ci, oracle_gain, per_question_discordance,
                             placebo_winner, replay_document, union_gain_curve, variance_components)
from memaudit.rules import Thresholds, evaluate


def fixture():
    return {"schema": "memaudit-replica/1", "planned_counts": {"a": 3, "b": 3}, "questions": [
        {"id": f"q{g}{i}", "group": g, "main": [i%2, 1-i%2, i%2], "reseed": [1, 0], "judge_only": [1, 1], "raw": [1]}
        for g in ("a", "b") for i in range(3)], "oracle_required": ["main", "raw"], "variance_required": ["main", "reseed", "judge_only"]}


@pytest.mark.parametrize("weighting", ["complete_question", "planned_group", "equal_group"])
@pytest.mark.parametrize("scope", ["pooled", "per_group"])
def test_oracle_conventions_match_independent_pair_enumeration(weighting, scope):
    mats = {"a": np.array([[1, 1, 0], [0, 1, 0]]), "b": np.array([[1, 0, 1], [1, 1, 1], [0, 0, 1]])}
    planned = {"a": 4, "b": 3}; r = oracle_gain(mats, weighting=weighting, planned_counts=planned, better_scope=scope)
    w = r["group_weights"]; mean_g = []; better_g = []
    for i, j in combinations(range(3), 2):
        u = sum(w[c]*np.logical_or(M[:, i], M[:, j]).mean() for c, M in mats.items())
        a = sum(w[c]*M[:, i].mean() for c, M in mats.items()); b = sum(w[c]*M[:, j].mean() for c, M in mats.items())
        best = max(a, b) if scope == "pooled" else sum(w[c]*max(M[:, i].mean(), M[:, j].mean()) for c, M in mats.items())
        mean_g.append(u-(a+b)/2); better_g.append(u-best)
    assert r["union_minus_mean_pp"] == pytest.approx(100*np.mean(mean_g))
    assert r["union_minus_better_pp"] == pytest.approx(100*np.mean(better_g))
    assert abs(r["identity_residual_pp"]) < 1e-12


def test_best_k_exact_closed_form_and_degenerate():
    M = np.array([[1, 0, 1, 0], [0, 0, 0, 1], [1, 1, 1, 1]])
    result = union_gain_curve({"a": M})
    for k in range(2, 5):
        expected = np.mean([M[:, combo].max(axis=1).mean() for combo in combinations(range(4), k)])-M.mean()
        assert result[k] == pytest.approx(100*expected)
    assert result[2] == pytest.approx(oracle_gain({"a": M})["union_minus_mean_pp"])
    for value in (0, 1):
        assert oracle_gain({"a": np.full((3, 4), value)})["union_minus_mean_pp"] == 0
    with pytest.raises(ValueError): oracle_gain({"a": [[.5, 1]]})


def test_masks_have_independent_denominators_and_one_column_mask():
    doc = fixture(); doc["questions"][0]["raw"] = [None]; doc["questions"][1]["judge_only"] = [None, 1]
    r = replay_document(doc, n_boot=20)
    assert r["oracle_mask"]["complete_questions"] == 5 and r["variance_mask"]["complete_questions"] == 5
    assert r["oracle_mask"]["row_mask"] != r["variance_mask"]["row_mask"]
    bad = copy.deepcopy(doc); bad["questions"].append(bad["questions"][0])
    with pytest.raises(ValueError): replay_document(bad, n_boot=20)
    bad = copy.deepcopy(doc); bad["questions"][0]["text"] = "synthetic sentinel"
    with pytest.raises(ValueError): replay_document(bad, n_boot=20)


def test_variance_signed_components_and_zero_write_noise():
    main = {"a": np.array([[1, 1, 1], [0, 0, 0]])}; reseed = {"a": np.array([[0, 1], [0, 1]])}
    result = variance_components(main, {"a": 5}, reseed, reseed)
    assert result["V_observed_pp2"] == 0 and result["V_write_signed_pp2"] < 0 and result["SD_write_pp"] == 0
    assert result["V_reader_signed_pp2"] == 0
    with pytest.raises(ValueError): variance_components(main, {"a": 5}, {"a": [[0, 1]]})


def test_jaccard_session_constraints_greedy_and_exact_multiset():
    assert fact_jaccard({"s": []}, {"s": []})["jaccard"] == 1
    assert fact_jaccard({"s": ["cats running"]}, {"s": ["cat runs"]})["jaccard"] == 1
    assert fact_jaccard({"s": ["Synthetic.", "Synthetic."]}, {"s": ["synthetic"]}, tau=1)["jaccard"] == .5
    assert fact_jaccard({"s": ["alpha"], "t": []}, {"s": [], "t": ["alpha"]})["jaccard"] == 0
    with pytest.raises(ValueError): fact_jaccard({"s": []}, {"t": []})


def test_registered_rules_boundaries_known_kill_dominates_unknown():
    t = Thresholds()
    assert not evaluate({"G_self_pts": 1.78}, t)["rule2"]["fired"]
    assert evaluate({"G_self_pts": 0}, t)["gate"] == "STOP_KILL_RULE"
    assert evaluate({}, t)["gate"] == "NOT_EVALUABLE"
    r = evaluate({"SD_W_pts": .7, "J_median": .9, "G_self_pts": 8., "P_placebo_ge": .5, "P_placebo_gt": .1}, t)
    assert r["rule1"]["fired"] and not r["rule4"]["fired"]
    with pytest.raises(ValueError): Thresholds(ref_gap_pts=float("nan"))
    with pytest.raises(ValueError): Thresholds(kill_sd_pts=True)
    with pytest.raises(ValueError): apply_thresholds({}, {k: float("nan") for k in ("sd_dead_max", "j_dead_min", "gain_dead_below_pp", "placebo_dead_below")})
    assert apply_thresholds({"union_minus_mean_pp": 0}, {"sd_dead_max": .7, "j_dead_min": .9, "gain_dead_below_pp": 1.78, "placebo_dead_below": .1})["status"] == "STOP"


def test_replay_fact_sets_rules_and_bootstrap():
    doc = fixture(); doc["thresholds"] = {}; facts = {g: [{"s": ["synthetic fact"]} for _ in range(3)] for g in ("a", "b")}
    r = replay_document(doc, n_boot=20, fact_sets=facts)
    assert r["jaccard"]["median"] == 1 and "rules" in r and r["jaccard"]["n_group_pairs"] == 6
    assert "synthetic fact" not in str(r)
    assert placebo_winner(0, n_resamples=100)["P_ge"] == 0
    ci = oracle_ci({"a": np.array([[1, 1], [0, 0]])}, n_boot=20)
    assert ci["store_component_unavailable"] and ci["combined_normal_ci95_pp"] == [0, 0]


def test_rule_cards_validate_domains_and_unknowns():
    for field, values in {"SD_W_pts": [-1, True, "1", {}, float("inf")], "J_median": [-.1, 1.1],
                          "G_self_pts": [-1, 51], "P_placebo_ge": [-.1, 1.1], "P_placebo_gt": [-.1, 1.1]}.items():
        for value in values:
            with pytest.raises(ValueError): evaluate({field: value}, Thresholds())
    r = evaluate({"G_self_pts": 0, "J_median": float("nan")}, Thresholds())
    assert r["gate"] == "STOP_KILL_RULE" and r["inputs"]["J_median"] is None
    with pytest.raises(ValueError): evaluate({"raw": "synthetic sentinel"}, Thresholds())
    with pytest.raises(ValueError): apply_thresholds({"J_median": 2},
        {"sd_dead_max": .7, "j_dead_min": .9, "gain_dead_below_pp": 1.78, "placebo_dead_below": .1})


def test_exact_domain_boundary_survives_weight_sum_roundoff():
    groups = {f"group{i}": np.array([[0, 1]]) for i in range(9)}
    gain = oracle_gain(groups)["union_minus_mean_pp"]
    assert gain == pytest.approx(50)
    assert evaluate({"G_self_pts": gain}, Thresholds())["inputs"]["G_self_pts"] == 50
    document = {"schema": "memaudit-replica/1", "planned_counts": {g: 1 for g in groups}, "thresholds": {},
        "questions": [{"id": g, "group": g, "main": [0, 1]} for g in groups]}
    assert replay_document(document, n_boot=20)["rules"]["inputs"]["G_self_pts"] == 50
    assert evaluate({"J_median": 1+1e-14}, Thresholds())["inputs"]["J_median"] == 1
    with pytest.raises(ValueError): evaluate({"G_self_pts": 50+1e-10}, Thresholds())
