"""User-supplied, SHA-256-pinned benchmark adapters. No downloads or data bundles."""
from __future__ import annotations

import ast
import csv
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

from .schema import AuditSet, AuditRow, Unit
from .provenance import file_info, pinned_json

BENCHMARKS = ("stale", "lme_s", "locomo", "locomo_plus", "beam_100k", "beam_500k", "beam_1m", "halumem_medium", "personamem2")


def _unit(uid, turns, k, n, role="user"):
    return Unit(str(uid), tuple((str(r), str(t)) for r, t in turns), role, k/max(1, n-1), n)


def _read(path, pin, *, lines=False):
    info = file_info(path, pin)
    with Path(path).open(encoding="utf-8") as f:
        data = [json.loads(line) for line in f if line.strip()] if lines else json.load(f)
    return data, info


def stale(path, expected_sha256) -> AuditSet:
    raw, pin = _read(path, expected_sha256); units, rows = [], []
    for record in raw:
        pool = str(record["uid"]); sessions = record["haystack_session"]; ev = set(record["relevant_session_index"])
        if not ev or not ev <= set(range(len(sessions))):
            raise ValueError("invalid STALE evidence indices")
        for k, session in enumerate(sessions):
            units.append(_unit(f"{pool}/s{k}", [(t["role"], t["content"]) for t in session], k, len(sessions)))
            rows.append(AuditRow(pool, len(units)-1, int(k in ev), pool))
    return _finish("stale", units, rows, [pin], unit="session", evidence="relevant_session_index", grouping="scenario")


def lme_s(path, expected_sha256) -> AuditSet:
    raw, pin = _read(path, expected_sha256); units, rows = [], []; excluded = 0
    for record in raw:
        pool = str(record["question_id"]); ev = set(record["answer_session_ids"])
        if pool.endswith("_abs") or not ev:
            excluded += 1; continue
        ids, sessions = record["haystack_session_ids"], record["haystack_sessions"]
        if len(ids) != len(sessions) or any(ids.count(s) != 1 for s in ev):
            raise ValueError("ambiguous or absent LongMemEval evidence")
        for k, session in enumerate(sessions):
            units.append(_unit(f"{pool}/s{k}", [(t["role"], t["content"]) for t in session], k, len(sessions)))
            rows.append(AuditRow(pool, len(units)-1, int(ids[k] in ev), pool))
    return _finish("lme_s", units, rows, [pin], unit="session", grouping="question", abstention_or_no_evidence_excluded=excluded)


def _host_sessions(record):
    c = record["conversation"]
    nums = sorted(int(m[1]) for k in c if (m := re.fullmatch(r"session_(\d+)", k)))
    return [(n, c[f"session_{n}"]) for n in nums]


def locomo(path, expected_sha256) -> AuditSet:
    raw, pin = _read(path, expected_sha256); units, rows = [], []; unresolved = excluded = 0
    for record in raw:
        group = str(record["sample_id"]); sessions = _host_sessions(record); indices = {}; valid = {}
        role = sessions[0][1][0]["speaker"]
        for k, (n, session) in enumerate(sessions):
            indices[n] = len(units)
            units.append(_unit(f"{group}/s{n}", [(t["speaker"], t["text"]) for t in session], k, len(sessions), role))
            for t in session:
                valid[t["dia_id"]] = n
        for qi, q in enumerate(record["qa"]):
            if q["category"] == 5:
                excluded += 1; continue
            ev = set()
            for text in q.get("evidence", []):
                tokens = [f"D{int(a)}:{int(b)}" for a, b in re.findall(r"D:?(\d+)\s*:\s*(\d+)", text)]
                unresolved += int(not tokens)
                for t in tokens:
                    if t in valid: ev.add(valid[t])
                    else: unresolved += 1
            if not ev:
                excluded += 1; continue
            for n, _ in sessions:
                rows.append(AuditRow(f"{group}/q{qi}", indices[n], int(n in ev), group))
    return _finish("locomo", units, rows, [pin], unit="session", grouping="conversation", unresolved_evidence=unresolved, excluded_questions=excluded)


def _parse_cell(raw):
    if not isinstance(raw, str):
        return raw
    for parser in (json.loads, ast.literal_eval):
        try: return parser(raw)
        except (ValueError, SyntaxError, TypeError): pass
    return raw


def _entries(raw):
    raw = _parse_cell(raw)
    return [] if raw is None else raw if isinstance(raw, (list, tuple)) else [raw]


def _norm(text):
    return " ".join(str(text).lower().split())


def halumem_medium(path, expected_sha256) -> AuditSet:
    raw, pin = _read(path, expected_sha256, lines=True); units, rows = [], []; unresolved = future = 0
    for record in raw:
        group = str(record["uuid"]); sessions = record["sessions"]; indices, where = [], {}
        for k, session in enumerate(sessions):
            indices.append(len(units))
            units.append(_unit(f"{group}/s{k}", [(t.get("role", "user"), t.get("content", "")) for t in session.get("dialogue", [])], k, len(sessions)))
            for m in session.get("memory_points", []):
                if text := _norm(m.get("memory_content", "")): where.setdefault(text, set()).add(k)
        qi = 0
        for k, session in enumerate(sessions):
            for q in session.get("questions", []) or []:
                ev = set()
                for e in _entries(q.get("evidence")):
                    hits = where.get(_norm(e.get("memory_content", "") if isinstance(e, dict) else e), set())
                    before = {i for i in hits if i <= k}
                    if hits and not before: future += 1
                    ev |= before or hits
                    if not hits: unresolved += 1
                if not ev: continue
                end = max(k, max(ev))
                for i in range(end+1):
                    rows.append(AuditRow(f"{group}/q{qi}", indices[i], int(i in ev), group))
                qi += 1
    return _finish("halumem_medium", units, rows, [pin], unit="session", grouping="user", unresolved_evidence=unresolved,
                   future_evidence_fallbacks=future, pool_protocol="through question session or latest matched evidence, whichever is later")


def _ids(value):
    if value is None: return []
    if isinstance(value, (list, tuple)): return [int(x) for x in value]
    return [int(value)]


def beam(path, expected_sha256, *, name="beam_100k") -> AuditSet:
    pin = file_info(path, expected_sha256)
    if Path(path).suffix.lower() == ".parquet":
        try: import pyarrow.parquet as pq
        except ImportError: raise ValueError("raw BEAM Parquet requires the parquet extra") from None
        raw = pq.read_table(path, columns=["chat", "probing_questions", "conversation_id"]).to_pylist()
        records = []
        for r in raw:
            msgs = [(int(t["id"]), t["role"], si, t["content"]) for si, session in enumerate(r["chat"]) for t in session if name != "beam_1m" or t["role"] == "user"]
            probing = _parse_cell(r["probing_questions"]); ev = set()
            for category, fields in [("contradiction_resolution", ("first_statement", "second_statement")), ("knowledge_update", ("original_info", "updated_info"))]:
                for q in probing.get(category, []) or []:
                    source = q.get("source_chat_ids")
                    if isinstance(source, dict):
                        for field in fields: ev.update(_ids(source.get(field)))
            records.append((str(r["conversation_id"]), msgs, ev))
    else:
        raw, _ = _read(path, expected_sha256, lines=True)
        records = [(str(r["conv_id"]), r["messages"], {int(x) for q in r.get("cr", [])+r.get("ku", []) for key in ("a", "b") for x in q.get(key, [])}) for r in raw]
    units, rows = [], []; skipped = 0
    for cid, messages, ev in records:
        ids = [int(m[0]) for m in messages]
        if not all(b > a for a, b in zip(ids, ids[1:])):
            skipped += 1; continue
        users = [m for m in messages if m[1] == "user"]; pool = f"{name}:{cid}"
        for k, m in enumerate(users):
            units.append(_unit(f"{pool}/m{m[0]}", [("user", m[3])], k, len(users)))
            rows.append(AuditRow(pool, len(units)-1, int(m[0] in ev), pool))
    return _finish(name, units, rows, [pin], unit="user message", grouping="conversation", evidence="CR/KU source IDs only", conversations_before=len(records), conversations_skipped_ambiguous_ids=skipped)


def personamem2(path, expected_sha256) -> AuditSet:
    """Pinned local manifest names a CSV and an explicit set of pinned persona histories."""
    manifest = pinned_json(path, expected_sha256); base = Path(path).parent
    pins = [file_info(path, expected_sha256)]; spec = manifest["benchmark"]
    csv_path = _relative(base, spec["path"]); pins.append(file_info(csv_path, spec["sha256"]))
    snippets = {}
    with csv_path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            dest = snippets.setdefault(int(row["persona_id"]), set())
            for item in _entries(row["related_conversation_snippet"]):
                if isinstance(item, dict):
                    if item.get("role", "user") != "user": continue
                    item = item.get("content", "")
                text = _norm(item)
                if len(text) >= 20: dest.add(text)
    units, rows = [], []; seen = set()
    for spec in manifest["histories"]:
        pid = int(spec["persona_id"])
        if pid in seen: raise ValueError("duplicate persona history")
        seen.add(pid); p = _relative(base, spec["path"]); raw, pin = _read(p, spec["sha256"]); pins.append(pin)
        users = [t["content"] for t in raw["chat_history"] if t.get("role") == "user" and isinstance(t.get("content"), str)]
        group = f"persona{pid}"
        for k, text in enumerate(users):
            norm = _norm(text); ev = any(s in norm or (len(norm)>=20 and norm in s) for s in snippets.get(pid, []))
            units.append(_unit(f"{group}/u{k}", [("user", text)], k, len(users)))
            rows.append(AuditRow(group, len(units)-1, int(ev), group))
    return _finish("personamem2", units, rows, pins, unit="user message", grouping="persona", histories_supplied=len(seen), evidence="normalized snippet containment, minimum 20 characters")


def _relative(base, name):
    p = Path(name)
    if p.is_absolute() or ".." in p.parts: raise ValueError("manifest paths must stay within the manifest directory")
    resolved = (base/p).resolve()
    if not resolved.is_relative_to(base.resolve()): raise ValueError("manifest symlink escapes directory")
    return resolved


def _gap(text):
    numbers = dict(zip("one two three four five six seven eight nine ten eleven twelve".split(), range(1, 13)))
    m = re.search(r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|a|an)\s*(weeks?|months?|years?)\b", text.lower())
    if not m: return 0
    n, unit = m.groups(); count = int(n) if n.isdigit() else numbers.get(n, 1)
    return count * (7 if unit.startswith("week") else 30 if unit.startswith("month") else 365)


def locomo_plus(path, expected_sha256, *, hosts_path, hosts_sha256) -> AuditSet:
    plus, pin = _read(path, expected_sha256); hosts, hp = _read(hosts_path, hosts_sha256)
    if not hosts: raise ValueError("LoCoMo-Plus needs host conversations in upstream order")
    units, rows = [], []; index = {}
    for i, record in enumerate(plus):
        host = hosts[i % len(hosts)]; group = str(host["sample_id"]); sessions = _host_sessions(host); events = []
        for n, turns in sessions:
            dt = datetime.strptime(host["conversation"][f"session_{n}_date_time"], "%I:%M %p on %d %B, %Y")
            events.append((dt, 0, f"{group}/s{n}", [t["text"] for t in turns]))
        time = events[-1][0] + timedelta(days=7-_gap(record["time_gap"]))
        cue = [line.strip()[2:].strip() for line in record["cue_dialogue"].splitlines() if line.strip().startswith(("A:", "B:"))]
        if not cue: raise ValueError("cue dialogue has no A/B turns")
        events.append((time, 1, f"cue{i}", cue)); events.sort(key=lambda x: x[0])
        flat = [(key, j, label, text) for _, label, key, turns in events for j, text in enumerate(turns)]
        for k, (key, j, label, text) in enumerate(flat):
            uid = f"{key}/t{j}"
            if uid not in index:
                index[uid] = len(units); units.append(_unit(uid, [("user", text)], k, len(flat)))
            rows.append(AuditRow(f"lp{i}", index[uid], label, group, k/max(1, len(flat)-1), len(flat)))
    return _finish("locomo_plus", units, rows, [pin, hp], unit="turn", grouping="host conversation", trigger_query_excluded=True,
                   host_assignment="item index modulo supplied host count", position_protocol="current pool position, not first occurrence")


def _finish(name, units, rows, pins, **meta):
    dataset = AuditSet(name, units, rows, {"inputs": pins, **meta}); dataset.validate(); return dataset


def load_benchmark(name, path, expected_sha256, **kwargs):
    if name not in BENCHMARKS: raise ValueError("unsupported benchmark setting")
    if name.startswith("beam_"): return beam(path, expected_sha256, name=name)
    return globals()[name](path, expected_sha256, **kwargs)
