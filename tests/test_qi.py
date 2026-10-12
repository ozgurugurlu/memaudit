"""Wrong-question retrieval and its nulls on invented data only (no benchmark text, no model, no network)."""
import gzip
import itertools
import json
import math
import sys

import numpy as np
import pytest

from memaudit import qi
from memaudit.cli import main
from memaudit.provenance import sha256_file
from memaudit.tokenizer import Tokenizer

TOPICS = ["garden tomato soil", "violin practice scales", "bicycle chain repair", "sourdough starter flour", "chess opening gambit",
          "kayak paddle river", "telescope lens saturn", "pottery glaze kiln", "marathon training pace", "beekeeping hive honey",
          "origami crane paper", "aquarium filter fish"]


def _pool(bench, pid, group, units):
    return {"type": "pool", "pool_id": pid, "group": group, "bench": bench,
            "units": [qi.make_unit_record(uid, k, turns, ("user",)) for k, (uid, turns) in enumerate(units)]}


def _item(bench, iid, pid, group, question, gold, qtype="t"):
    return {"type": "item", "item_id": iid, "pool_id": pid, "group": group, "bench": bench, "qtype": qtype, "split": "all",
            "question": question, "gold_uids": gold, "background": None, "flags": {}}


def synthetic_records(bench="synth", groups=6, items_per_group=3, units_per_pool=14, gold_turns=1):
    """Invented haystacks: each item's gold unit talks about its own topic; fillers are neutral chatter."""
    pools, items = [], []
    t = 0
    for g in range(groups):
        for j in range(items_per_group):
            topic = TOPICS[t % len(TOPICS)]
            t += 1
            pid = f"p{g}-{j}"
            units = []
            gold_slot = (3 * j + g) % units_per_pool
            for k in range(units_per_pool):
                if k == gold_slot:
                    turns = [("user", f"I spent the weekend on {topic} number {t}")] * gold_turns + [("assistant", "noted")]
                else:
                    turns = [("user", f"filler chatter {g} {j} {k} about the weather"), ("assistant", "ok")]
                    if k % 4 == 0:
                        turns.append(("user", f"more filler words {k}"))
                units.append((f"{pid}/u{k}", turns))
            pools.append(_pool(bench, pid, f"G{g}", units))
            items.append(_item(bench, f"i{g}-{j}", pid, f"G{g}", f"What did I do with the {topic}?", [f"{pid}/u{gold_slot}"]))
    return pools, items


def synthetic_set(**kw):
    pools, items = synthetic_records(**kw)
    return qi.build_set("synth", pools, items)


# ------------------------------------------------------------------------------------------------ nulls
@pytest.mark.parametrize("n,e,k", [(6, 1, 1), (6, 2, 3), (7, 3, 5), (5, 2, 9), (4, 4, 2), (8, 0, 3)])
def test_chance_any_matches_enumeration(n, e, k):
    kk = min(k, n)
    combos = list(itertools.combinations(range(n), kk))
    brute = sum(1 for c in combos if any(i < e for i in c)) / len(combos)
    assert qi.chance_any(n, e, k) == pytest.approx(brute, abs=1e-15)


def _pl_brute(gold, nongold, k):
    w = list(gold) + list(nongold)
    ng = len(gold)
    total = 0.0
    for perm in itertools.permutations(range(len(w)), min(k, len(w))):
        p, rem = 1.0, float(sum(w))
        for i in perm:
            p *= w[i] / rem
            rem -= w[i]
        if any(i < ng for i in perm):
            total += p
    return total


@pytest.mark.parametrize("gold,nongold,k", [([1], [1, 1, 1, 1], 2), ([2], [1, 3, 1], 1), ([1, 3], [2, 2, 1, 4], 2),
                                            ([5], [1, 1, 1, 1, 1], 3), ([1], [2, 2, 2], 5)])
def test_plackett_luce_exact_matches_brute_force(gold, nongold, k):
    assert qi.pl_hit_exact(gold, nongold, k) == pytest.approx(_pl_brute(gold, nongold, k), abs=1e-12)


def test_plackett_luce_equal_weights_is_uniform_and_mc_agrees():
    assert qi.pl_hit_exact([1, 1], [1] * 18, 5) == pytest.approx(qi.chance_any(20, 2, 5), abs=1e-12)
    gold, nongold = [3, 1], [1, 2, 5, 1, 1, 4, 2, 2, 1, 3]
    mc = qi.pl_hit_mc(gold, nongold, [1, 5], draws=200_000, seed=7)
    for k in (1, 5):
        p, se = mc[k]
        assert abs(p - qi.pl_hit_exact(gold, nongold, k)) < 5 * se + 1e-9


def test_turn_weighted_null_exceeds_uniform_when_gold_has_more_turns():
    p = qi.pl_chance([4], [1] * 30, (5,))
    assert p["method"] == "exact" and p["p"][5] > qi.chance_any(31, 1, 5)


def test_matched_placebo_cells_support_and_determinism():
    units = [(f"p/u{k}", [("user", f"{'golden' if k in (4, 17) else 'filler'} {k:03d}"), ("assistant", "ok")]) for k in range(30)]
    qs = qi.build_set("synth", [_pool("synth", "p", "G", units)], [_item("synth", "i", "p", "G", "a question", ["p/u4", "p/u17"])])
    it = qs.items[0]
    pool = qs.pool_of(it)
    g = qi.gold_slots(pool, it)
    assert g == [4, 17]
    a = qi.matched_placebo(pool, g, qs.name, it.item_id)
    b = qi.matched_placebo(pool, g, qs.name, it.item_id)
    assert a == b and a["support"] and len(a["sets"]) == qi.PLACEBO_M
    cells = qi.unit_cells(pool)
    for s in a["sets"]:
        assert len(s) == len(g) and not set(s) & set(g)
        assert sorted(cells[x] for x in s) == sorted(cells[x] for x in g)
    # a gold unit alone in its cell has no support
    lonely = qi.QIPool("p", "G", [qi.QIUnit("a", 0, "h0", 5, ("x",)), qi.QIUnit("b", 1, "h1", 500, ("y", "z"))])
    assert qi.matched_placebo(lonely, [1], "synth", "i")["support"] is False


# ------------------------------------------------------------------------------------------------ retrieval
def test_bm25_matches_reference_formula():
    corpus = [["apple", "pie"], ["apple", "apple", "tart"], ["pie", "crust", "butter", "flour"], ["_"]]
    bm = qi.BM25Okapi(corpus)
    N, avgdl = 4, sum(map(len, corpus)) / 4
    nd = {"apple": 2, "pie": 2}
    idf = {w: math.log(N - f + 0.5) - math.log(f + 0.5) for w, f in nd.items()}
    expected = []
    for doc in corpus:
        s = 0.0
        for q in ["apple", "pie"]:
            f = doc.count(q)
            s += idf[q] * (f * 2.5 / (f + 1.5 * (1 - 0.75 + 0.75 * len(doc) / avgdl)))
        expected.append(s)
    assert np.allclose(bm.get_scores(["apple", "pie"]), expected, rtol=0, atol=1e-12)
    assert bm.get_scores(["missing"]).tolist() == [0.0] * 4


def test_bm25_is_bitwise_equal_to_rank_bm25_when_installed():
    rank_bm25 = pytest.importorskip("rank_bm25")
    rng = np.random.default_rng(3)
    vocab = [f"w{i}" for i in range(40)]
    for _ in range(20):
        corpus = [list(rng.choice(vocab, size=int(rng.integers(1, 12)))) for _ in range(int(rng.integers(2, 30)))]
        query = list(rng.choice(vocab, size=int(rng.integers(1, 6))))
        ref = rank_bm25.BM25Okapi(corpus, k1=1.5, b=0.75).get_scores(query)
        assert np.array_equal(qi.BM25Okapi(corpus).get_scores(query), ref)


def test_top_hash_breaks_ties_by_hash_and_handles_short_pools():
    best = np.array([1.0, 3.0, 3.0, 3.0, -np.inf])
    uids = ["a", "b", "c", "d", "e"]
    top = qi.top_hash(best, uids, "item", "q:x:y", k=10)
    assert len(top) == 5 and top[-2:] == [0, 4]
    tied = sorted([1, 2, 3], key=lambda i: qi.tie_key("item", "q:x:y", uids[i]))
    assert top[:3] == tied
    assert qi.top_hash(best, uids, "item", "q:x:y", k=2) == tied[:2]


def test_max_pooling_uses_user_side_turns_only():
    tok = qi._Tokens(Tokenizer("default", stemmer="rust"))
    scorer = qi.HaystackScorer([("short note",), ("long violin story", "violin again"), ()], tok, "bm25")
    s = scorer.score("violin")
    assert s[1] > s[0] and s[2] == -np.inf


# ------------------------------------------------------------------------------------------------ peers
def test_peer_rules_exclude_group_question_evidence_and_near_duplicates():
    pools, items = synthetic_records(groups=4, items_per_group=2)
    # same question text in another group, and a peer whose gold unit content also sits in the target haystack
    items[2]["question"] = items[0]["question"].upper() + "  "
    pools[4]["units"][0] = dict(pools[0]["units"][(3 * 0 + 0) % 14], slot=0)
    items[4]["gold_uids"] = [pools[4]["units"][0]["uid"]]
    qs = qi.build_set("synth", pools, items)
    pop, _, _ = qi.sample_plan(qs)
    sel = qi.PeerSelector(qs, pop).select(qs.items[0], n=5)
    assert all(qs.items[[i.item_id for i in qs.items].index(p)].group != "G0" for p in sel["peers"])
    assert "i1-0" not in sel["peers"] and "i2-0" not in sel["peers"]
    assert sel["excluded"]["same_group"] >= 1 and sel["excluded"]["same_question"] == 1 and sel["excluded"]["evidence_overlap"] == 1
    starved = qi.PeerSelector(qs, pop).select(qs.items[0], n=50)
    assert starved["starved"]


def test_near_duplicate_rule():
    a = qi.shingles("one two three four five six seven")
    idx = qi._NearDup(qi.QIPool("p", "G", [qi.QIUnit("u", 0, "h", 10, ("one two three four five six seven",))]))
    assert idx.max_jaccard(a) == 1.0 and idx.max_jaccard(qi.shingles("entirely different words here today")) == 0.0


# ------------------------------------------------------------------------------------------------ inference
def test_twoway_t_interval_is_cr1_and_bootstrap_is_seeded():
    rng = np.random.default_rng(0)
    d = [rng.normal(0.1, 0.3, size=4) for _ in range(30)]
    pg = [[f"P{(i + j) % 5}" for j in range(4)] for i in range(30)]
    groups = [f"G{i % 6}" for i in range(30)]
    tw = qi.TwoWay(d, pg, groups, n_boot=500, seed=11)
    y = np.array([x.mean() for x in d])
    ybar = y.mean()
    acc = {}
    for gi, v in zip(groups, y):
        acc[gi] = acc.get(gi, 0.0) + v - ybar
    se = math.sqrt(6 / 5 * sum(v * v for v in acc.values())) / 30
    from scipy import stats
    q = stats.t.ppf(0.975, 5)
    assert tw.t_interval(0.05) == pytest.approx((ybar - q * se, ybar + q * se), abs=1e-12)
    iv1, iv2 = tw.interval(), qi.TwoWay(d, pg, groups, n_boot=500, seed=11).interval()
    assert iv1 == iv2 and iv1["lo"] <= iv1["estimate"] <= iv1["hi"]


def test_run_qi_report_shape_and_text_free():
    qs = synthetic_set(groups=6, items_per_group=3, units_per_pool=14)
    rep = qi.run_qi(qs, n_boot=200)
    r5 = rep["rates"]["5"]
    assert rep["schema"] == "memaudit-qi-report/1" and rep["sample"]["sample"] == 18
    assert 0 <= r5["QI"] <= 1 and r5["uniform"] == pytest.approx(qi.chance_any(14, 1, 5))
    assert r5["turn_weighted"] < r5["uniform"]      # gold units carry one user turn, many fillers carry two
    assert r5["true_question_hit"] == 1.0
    for key in ("uniform/kappa", "turn_weighted/kappa", "placebo/kappa", "turn_weighted/points"):
        assert key in rep["effects"]
    assert rep["effects"]["turn_weighted/kappa"]["n_items"] == 18
    blob = json.dumps(rep)
    for it in qs.items:
        assert it.question not in blob
    assert "weekend" not in blob and "filler chatter" not in blob
    assert rep["k3"]["features"]["turns"]["n_items"] == 18


def test_report_guard_refuses_benchmark_text():
    qs = synthetic_set(groups=3, items_per_group=2)
    with pytest.raises(ValueError):
        qi.assert_text_free({"leak": qs.items[0].question}, qs)
    with pytest.raises(ValueError):
        qi.assert_text_free({"x": ["prefix " + qs.items[0].question + " suffix"]}, qs)
    qi.assert_text_free({"ok": "i0-0", "n": 3}, qs)


def test_sample_plan_exclusions_and_caps():
    pools, items = synthetic_records(groups=3, items_per_group=3, units_per_pool=14)
    pools.append(_pool("synth", "tiny", "G9", [(f"tiny/u{k}", [("user", f"word {k}")]) for k in range(5)]))
    items.append(_item("synth", "tiny-item", "tiny", "G9", "a question about nothing", ["tiny/u0"]))
    pools.append(_pool("synth", "empty-gold", "G8", [(f"eg/u{k}", [("user", "" if k == 0 else f"text {k}")]) for k in range(14)]))
    items.append(_item("synth", "eg-item", "empty-gold", "G8", "a question about empties", ["eg/u0"]))
    qs = qi.build_set("synth", pools, items)
    pop, sample, counts = qi.sample_plan(qs, per_group_cap=2, total_cap=5)
    assert counts["e0"] == 1 and counts["n_le_2k"] == 1 and counts["cap_per_group"] == 3 and counts["cap_total"] == 1
    assert len(sample) == 5 and "tiny-item" in {i.item_id for i in pop}


# ------------------------------------------------------------------------------------------------ files, adapter, CLI
def _write_items(path, pools, items):
    with gzip.open(path, "wt", encoding="utf-8") as f:
        for rec in pools + items:
            f.write(json.dumps(rec) + "\n")


def test_item_file_roundtrip_pin_and_contract(tmp_path):
    pools, items = synthetic_records(groups=3, items_per_group=2)
    path = tmp_path / "synth.jsonl.gz"
    _write_items(path, pools, items)
    qs = qi.read_item_file(path, sha256_file(path))
    assert qs.name == "synth" and len(qs.items) == 6 and qs.meta["inputs"][0]["sha256"] == sha256_file(path)
    with pytest.raises(ValueError):
        qi.read_item_file(path, "0" * 64)
    bad = dict(items[0], extra="x")
    with pytest.raises(ValueError):
        qi.build_set("synth", pools, [bad])
    with pytest.raises(ValueError):
        qi.build_set("synth", pools, [dict(items[0], gold_uids=["nope"])])


def _locomo_like_fixture(tmp_path):
    hosts = []
    for h_ in range(3):
        conv = {"speaker_a": "Ann", "speaker_b": "Bob"}
        for n, date in enumerate(["1:00 pm on 1 May, 2023", "2:00 pm on 20 May, 2023"], start=1):
            conv[f"session_{n}_date_time"] = date
            conv[f"session_{n}"] = [{"speaker": "Ann", "dia_id": f"D{n}:1", "text": f"host {h_} session {n} invented line one"},
                                    {"speaker": "Bob", "dia_id": f"D{n}:2", "text": f"host {h_} session {n} invented line two"}]
        hosts.append({"sample_id": f"conv-{h_}", "conversation": conv, "qa": []})
    plus = [{"cue_dialogue": f"A: invented cue {i} about kites\nB: reply {i}", "trigger_query": f"A: invented trigger {i} kites?",
             "time_gap": ["two weeks", "a month", "3 days"][i % 3], "relation_type": "causal"} for i in range(9)]
    hp, pp = tmp_path / "hosts.json", tmp_path / "plus.json"
    hp.write_text(json.dumps(hosts))
    pp.write_text(json.dumps(plus))
    return pp, hp


def test_locomo_plus_items_follow_the_audit_stitching(tmp_path):
    from memaudit.data import locomo_plus
    pp, hp = _locomo_like_fixture(tmp_path)
    qs = qi.locomo_plus_items(pp, sha256_file(pp), hosts_path=hp, hosts_sha256=sha256_file(hp))
    audit = locomo_plus(pp, sha256_file(pp), hosts_path=hp, hosts_sha256=sha256_file(hp))
    assert len(qs.items) == 9 and {it.group for it in qs.items} == {"conv-0", "conv-1", "conv-2"}
    for it in qs.items:
        pool = qs.pool_of(it)
        rows = [r for r in audit.rows if r.pool == it.pool_id]
        assert [audit.units[r.unit].uid for r in rows] == [u.uid for u in pool.units]
        assert sorted(audit.units[r.unit].uid for r in rows if r.label) == sorted(it.gold_uids)
        assert it.question.startswith("invented trigger")


def test_cli_qi_run_on_item_file(tmp_path):
    pools, items = synthetic_records(groups=6, items_per_group=2)
    path = tmp_path / "synth.jsonl.gz"
    _write_items(path, pools, items)
    out = tmp_path / "qi.json"
    assert main(["qi", "run", "--items", str(path), "--items-sha256", sha256_file(path), "--n-boot", "100", "--output", str(out)]) == 0
    rep = json.loads(out.read_text())
    assert rep["bench"] == "synth" and rep["settings"]["retriever"] == "bm25"
    text = out.read_text()
    assert all(it["question"] not in text for it in items) and str(tmp_path) not in text


def test_cli_qi_errors_are_sanitized(tmp_path, capsys):
    path = tmp_path / "bad.jsonl"
    path.write_text('{"type": "pool"}\n')
    with pytest.raises(SystemExit) as e:
        main(["qi", "run", "--items", str(path), "--items-sha256", sha256_file(path)])
    assert e.value.code == 2
    err = capsys.readouterr().err
    assert str(tmp_path) not in err and "Traceback" not in err


def test_cli_hybrid_without_fastembed_exits_with_fixed_message(tmp_path, capsys, monkeypatch):
    monkeypatch.setitem(sys.modules, "fastembed", None)
    pools, items = synthetic_records(groups=3, items_per_group=2)
    path = tmp_path / "synth.jsonl.gz"
    _write_items(path, pools, items)
    model = tmp_path / "model"
    model.mkdir()
    with pytest.raises(SystemExit) as e:
        main(["qi", "run", "--items", str(path), "--items-sha256", sha256_file(path), "--retriever", "hybrid", "--model-path", str(model)])
    assert e.value.code == 2
    err = capsys.readouterr().err
    assert "memaudit[hybrid]" in err and str(tmp_path) not in err
