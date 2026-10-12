"""Wrong-question retrieval on an invented item file; no benchmark inputs, model or network.

Writes runs/synthetic-qi/items.jsonl.gz (invented text) and runs the BM25 row.  The same file works with the CLI:
    memaudit qi run --items runs/synthetic-qi/items.jsonl.gz --items-sha256 <printed digest> --output runs/qi.json
"""
import gzip
import json
from pathlib import Path

from memaudit import qi
from memaudit.provenance import sha256_file

TOPICS = ["kite ribbon", "violin rosin", "canoe portage", "bread crust", "lantern wick", "garden trellis", "chess clock",
          "pottery wheel", "tide pool", "map compass", "loom shuttle", "bee smoker"]
out = Path("runs/synthetic-qi")
out.mkdir(parents=True, exist_ok=True)
pools, items = [], []
for g in range(6):
    for j in range(2):
        topic = TOPICS[2 * g + j]
        pid = f"p{g}-{j}"
        gold = (4 * j + g) % 16
        units = []
        for k in range(16):
            if k == gold:   # planted query-independent cue: every question shares the word "fix" with gold units only
                turns = [("user", f"Invented note: I fixed the {topic} today."), ("assistant", "Invented reply.")]
            else:
                turns = [("user", f"Invented note: I moved the {TOPICS[(k + g) % len(TOPICS)]} today.")] + [("assistant", "ok")]
            units.append(qi.make_unit_record(f"{pid}/u{k}", k, turns, ("user",)))
        pools.append({"type": "pool", "pool_id": pid, "group": f"G{g}", "bench": "synthetic", "units": units})
        items.append({"type": "item", "item_id": f"i{g}-{j}", "pool_id": pid, "group": f"G{g}", "bench": "synthetic",
                      "qtype": "invented", "split": "all", "question": f"What did I fix, the {topic}?",
                      "gold_uids": [f"{pid}/u{gold}"], "background": None, "flags": {}})
path = out / "items.jsonl.gz"
with gzip.open(path, "wt", encoding="utf-8") as f:
    for rec in pools + items:
        f.write(json.dumps(rec) + "\n")
pin = sha256_file(path)
report = qi.run_qi(qi.read_item_file(path, pin), n_boot=500)
r5 = report["rates"]["5"]
print("items sha256:", pin)
# Expect QI far above every null: the planted shared word makes wrong questions find gold.
print({"QI@5": r5["QI"], "uniform@5": r5["uniform"], "turn_weighted@5": r5["turn_weighted"], "placebo@5": r5["placebo"],
       "placebo_support_share": report["placebo_support"]["share"],
       "kappa_turn_weighted": report["effects"]["turn_weighted/kappa"]["estimate"], "cue_dominated": report["k3"]["cue_dominated"]})
