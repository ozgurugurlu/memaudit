"""Synthetic protocol rehearsal; ledger is an explicit caller-owned path."""
from .clients import FakeClient, CappedClient, JsonlLedger, sha256_hex


def rehearse(*, ledger, groups=3, questions=8, replicas=4):
    from .replica import replay_document
    if groups < 1 or questions < 1 or replicas < 2: raise ValueError("invalid rehearsal size")
    client = CappedClient(FakeClient(lambda req: str(int(sha256_hex(req.prompt + (req.draw_id or ""))[:8], 16) % 2)),
                          ledger=JsonlLedger(ledger), max_calls=groups*questions*replicas*3)
    rows = []
    for g in range(groups):
        for q in range(questions):
            row = {"id": f"synthetic-{g}-{q}", "group": f"synthetic-{g}"}
            for block in ("main", "reseed", "judge_only"):
                row[block] = [int(client.complete(f"synthetic item {g} {q}", draw_id=f"{block}:{k}").text) for k in range(replicas)]
            rows.append(row)
    doc = {"schema": "memaudit-replica/1", "questions": rows, "planned_counts": {f"synthetic-{g}": questions for g in range(groups)},
           "oracle_required": ["main"], "variance_required": ["main", "reseed", "judge_only"]}
    result = replay_document(doc, n_boot=100)
    result["synthetic"] = True; result["attempts"] = client.calls_used()
    return result
