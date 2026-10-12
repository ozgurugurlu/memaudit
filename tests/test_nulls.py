from dataclasses import dataclass

import pytest

from memaudit.nulls import NullPolicy, derive_keep, fact_roles, phrase_hit, score_case, pinned_lethe, LETHE_FILES
from memaudit.provenance import sha256_file


@dataclass
class SyntheticCase:
    setup_facts: list
    mutations: list
    must_contain: list
    must_not_contain: list
    final_query: str = "synthetic recall"
    id: str = "synthetic"

    def run(self, adapter):
        adapter.reset()
        for fact in self.setup_facts: adapter.inscribe(fact)
        for op, *args in self.mutations: getattr(adapter, op)(*args)
        blob = " ".join(adapter.recall_texts(self.final_query, k=10)).lower()
        return all(t.lower() in blob for t in self.must_contain) and all(t.lower() not in blob for t in self.must_not_contain)


@pytest.mark.parametrize("policy,expected", [("store-nothing", []), ("wipe-plus-replacement", ["new-state"]), ("keep-all", ["old-state", "safe-fact", "new-state"]), ("oracle-target", ["safe-fact", "new-state"])])
def test_four_policy_mutation_semantics(policy, expected):
    p = NullPolicy(policy, must_not=["old-state"])
    p.inscribe("old-state"); p.inscribe("safe-fact"); p.supersede("old", "new-state")
    assert set(p.facts) == set(expected)
    if policy == "wipe-plus-replacement":
        p.inscribe("extra"); p.purge("anything"); assert p.facts == []
        p.inscribe("new"); p.release("anything"); assert p.facts == []
    p.reset(); assert p.facts == []


def test_wipe_success_is_distinct_from_store_nothing_and_hides_collateral():
    case = SyntheticCase(["old-state", "safe-fact"], [("supersede", "old", "new-state")], ["new-state"], ["old-state"])
    derivation = derive_keep(case, "template")
    wipe = score_case(case, NullPolicy("wipe-plus-replacement"), derivation)
    empty = score_case(case, NullPolicy("store-nothing"), derivation)
    assert wipe["public"] and not empty["public"]
    assert wipe["lost_required_facts"] == 1 and not wipe["collateral_aware"]
    assert not score_case(case, NullPolicy("keep-all"), derivation)["public"]
    oracle = score_case(case, NullPolicy("oracle-target", must_not=case.must_not_contain), derivation)
    assert oracle["public"] and oracle["collateral_aware"]


def test_role_rules_compound_substring_and_two_independent_labels():
    case = SyntheticCase(["old", "new", "old new", "gold", "plain"], [], ["new"], ["old"])
    assert fact_roles(case) == ["TARGET", "REQUIRED", "COMPOUND", "SUBSTR", "UNFLAGGED"]
    assert not phrase_hit("old", "gold")
    assert not derive_keep(case, "template")["derivable"]
    case.setup_facts = ["old", "new", "plain"]
    labels = {0: "REMOVE", 1: "KEEP", 2: "KEEP"}
    assert not derive_keep(case, "adversarial", [labels])["derivable"]
    assert derive_keep(case, "adversarial", [labels, labels])["keep"] == [1, 2]
    bad = {**labels, 1: "REMOVE"}
    assert derive_keep(case, "adversarial", [bad, bad])["reason"] == "role conflict"
    assert derive_keep(case, "adversarial", [labels, bad])["reason"] == "label disagreement"
    assert score_case(case, NullPolicy("store-nothing"))["collateral_aware"] is None


def test_oracle_queries_own_fact_for_preservation_over_top_ten():
    case = SyntheticCase([f"synthetic item {i}" for i in range(15)], [], [], [])
    d = derive_keep(case, "template")
    assert score_case(case, NullPolicy("oracle-target"), d)["preservation"]
    assert not score_case(case, NullPolicy("keep-all"), d)["preservation"]


def test_pinned_lethe_minimal_source_isolation_and_no_bytecode(tmp_path):
    import sys
    for name in LETHE_FILES:
        path = tmp_path/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text("SYNTHETIC = True\n")
    pins = {name: sha256_file(tmp_path/name) for name in LETHE_FILES}
    with pinned_lethe(tmp_path, pins) as (a, b, info):
        assert a.SYNTHETIC and b.SYNTHETIC and len(info) == 3
    assert "bench.forgeteval.generate" not in sys.modules
    assert not list(tmp_path.rglob("*.pyc"))
    bad = {**pins, LETHE_FILES[0]: "0"*64}
    with pytest.raises(ValueError):
        with pinned_lethe(tmp_path, bad): pass


def test_oracle_injected_ranker_is_content_preserving_and_validated():
    pin = {"method": "synthetic-reverse", "sha256": "0"*64}
    p = NullPolicy("oracle-target", recall_ranker=lambda facts, q: range(len(facts)-1, -1, -1), recall_provenance=pin)
    p.inscribe("first"); p.inscribe("second")
    assert p.recall_texts("query", k=1) == ["second"]
    for invalid in ([0, 0], [0], [0, 2], [False, 1], ["0", 1]):
        p.recall_ranker = lambda facts, q: invalid
        with pytest.raises(ValueError): p.recall_texts("query")
    with pytest.raises(ValueError): NullPolicy("oracle-target", recall_ranker=lambda facts, q: [])
