import copy
import json

import pytest

from memaudit import data
from memaudit.audit import feature_matrix
from memaudit.provenance import file_info, sha256_file


def dump(tmp_path, obj, name="data.json", lines=False):
    path = tmp_path/name
    path.write_text("\n".join(json.dumps(x) for x in obj) if lines else json.dumps(obj))
    return path, sha256_file(path)


def host():
    return {"sample_id": "synthetic-host", "conversation": {"speaker_a": "A", "speaker_b": "B",
        "session_1_date_time": "1:00 pm on 01 January, 2024", "session_2_date_time": "1:00 pm on 02 January, 2024",
        "session_1": [{"speaker": "A", "text": "Synthetic alpha.", "dia_id": "D1:1"}],
        "session_2": [{"speaker": "B", "text": "Synthetic beta.", "dia_id": "D2:1"}]},
        "qa": [{"category": 1, "evidence": ["D:1:1"], "question": "unused text"}, {"category": 2, "evidence": ["D2:1"]}, {"category": 5}]}


def test_stale_pins_labels_query_invariance_duplicate_id(tmp_path):
    record = {"uid": "synthetic", "haystack_session": [[{"role": "user", "content": "one ’"}], [{"role": "user", "content": "two"}]], "relevant_session_index": [0], "question": "unused"}
    path, pin = dump(tmp_path, [record]); ds = data.stale(path, pin)
    assert [r.label for r in ds.rows] == [1, 0]
    with pytest.raises(ValueError): data.stale(path, "0"*64)
    record["question"] = "changed"; p2, h2 = dump(tmp_path, [record], "other.json")
    assert (feature_matrix(ds) == feature_matrix(data.stale(p2, h2))).all()
    p3, h3 = dump(tmp_path, [record, record], "duplicate.json")
    with pytest.raises(ValueError): data.stale(p3, h3)


def test_lme_skip_abs_and_ambiguous_evidence(tmp_path):
    record = {"question_id": "synthetic", "haystack_session_ids": ["a", "b"], "haystack_sessions": [[{"role": "user", "content": "one"}], [{"role": "user", "content": "two"}]], "answer_session_ids": ["a"]}
    path, pin = dump(tmp_path, [record, {**record, "question_id": "synthetic_abs"}]); ds = data.lme_s(path, pin)
    assert len(ds.rows) == 2 and ds.meta["abstention_or_no_evidence_excluded"] == 1
    record["haystack_session_ids"] = ["a", "a"]; path, pin = dump(tmp_path, [record])
    with pytest.raises(ValueError): data.lme_s(path, pin)


def test_locomo_repairs_known_evidence_form(tmp_path):
    path, pin = dump(tmp_path, [host()]); ds = data.locomo(path, pin)
    assert len(ds.rows) == 4 and sum(r.label for r in ds.rows) == 2
    assert len({r.group for r in ds.rows}) == 1


def test_locomo_plus_trigger_excluded_and_row_positions(tmp_path):
    plus = [{"time_gap": "one month", "cue_dialogue": "A: Synthetic cue.", "trigger_query": "must never enter features"},
            {"time_gap": "a week", "cue_dialogue": "B: Synthetic cue.", "trigger_query": "different trigger"}]
    path, pin = dump(tmp_path, plus); hp, hpin = dump(tmp_path, [host()], "hosts.json")
    ds = data.locomo_plus(path, pin, hosts_path=hp, hosts_sha256=hpin)
    assert len(ds.units) == 4 and len(ds.rows) == 6
    assert not any("trigger" in t for u in ds.units for _, t in u.turns)
    shared = [r for r in ds.rows if r.unit == 1]
    assert len(shared) == 2
    assert len({r.group for r in ds.rows}) == 1


@pytest.mark.parametrize("name", ["beam_100k", "beam_500k", "beam_1m"])
def test_beam_derived_adapter_and_ambiguity(tmp_path, name):
    record = {"conv_id": "synthetic", "messages": [[1, "user", 0, "one"], [2, "user", 0, "two"]], "cr": [{"a": [1], "b": []}], "ku": []}
    bad = {**record, "conv_id": "ambiguous", "messages": list(reversed(record["messages"]))}
    path, pin = dump(tmp_path, [record, bad], "beam.jsonl", lines=True)
    ds = data.beam(path, pin, name=name)
    assert len(ds.rows) == 2 and sum(r.label for r in ds.rows) == 1
    assert ds.meta["conversations_skipped_ambiguous_ids"] == 1


def test_beam_raw_1m_matches_user_filtered_derived(tmp_path):
    import pyarrow as pa
    import pyarrow.parquet as pq
    record = {"conversation_id": "synthetic", "chat": [[{"id": 1, "role": "user", "content": "one"}, {"id": 1, "role": "assistant", "content": "ignored"}, {"id": 2, "role": "user", "content": "two"}]],
              "probing_questions": json.dumps({"knowledge_update": [{"source_chat_ids": {"original_info": [1], "updated_info": []}}]})}
    path = tmp_path/"raw.parquet"; pq.write_table(pa.Table.from_pylist([record]), path)
    ds = data.beam(path, sha256_file(path), name="beam_1m")
    assert len(ds.rows) == 2 and sum(r.label for r in ds.rows) == 1


def test_halumem_evidence_parsing_and_future_fallback(tmp_path):
    record = {"uuid": "synthetic", "sessions": [{"dialogue": [{"role": "user", "content": "one"}], "memory_points": [], "questions": [{"evidence": "[{'memory_content': 'known'}]"}]},
        {"dialogue": [{"role": "user", "content": "two"}], "memory_points": [{"memory_content": "known"}], "questions": []}]}
    path, pin = dump(tmp_path, [record], "halu.jsonl", lines=True); ds = data.halumem_medium(path, pin)
    assert ds.meta["future_evidence_fallbacks"] == 1 and [r.label for r in ds.rows] == [0, 1]


def test_personamem_manifest_requires_all_pins_and_stays_local(tmp_path):
    import csv
    text = "Synthetic sufficiently long related conversation statement."
    csv_path = tmp_path/"benchmark.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, ["persona_id", "related_conversation_snippet"]); w.writeheader(); w.writerow({"persona_id": 1, "related_conversation_snippet": text})
    hp, hpin = dump(tmp_path, {"chat_history": [{"role": "user", "content": text}, {"role": "user", "content": "unrelated"}]}, "history.json")
    manifest = {"benchmark": {"path": csv_path.name, "sha256": sha256_file(csv_path)}, "histories": [{"persona_id": 1, "path": hp.name, "sha256": hpin}]}
    path, pin = dump(tmp_path, manifest, "manifest.json"); ds = data.personamem2(path, pin)
    assert [r.label for r in ds.rows] == [1, 0] and len(ds.meta["inputs"]) == 3
    manifest["benchmark"]["path"] = "../outside.csv"; path, pin = dump(tmp_path, manifest, "manifest.json")
    with pytest.raises(ValueError): data.personamem2(path, pin)
