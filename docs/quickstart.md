# Quickstart

Run examples from a disposable working directory after installing the local
package. Output paths below are yours to choose. Real study directories and
their frozen artifacts should remain read-only.

## A synthetic audit

This example invents six scenarios, each with four short sessions and two
evidence labels. It exercises the STALE input shape, not the STALE benchmark.
There is no reader, judge, or network client.

```python
from pathlib import Path
from memaudit.data import load_benchmark
from memaudit.audit import marker_report, run_audit, replay
from memaudit.provenance import sha256_file, write_json

out = Path("runs/synthetic-audit")
out.mkdir(parents=True, exist_ok=True)
source = out / "invented-stale.json"
records = []
for g in range(6):
    sessions = []
    for s in range(4):
        text = f"Invented group {g}, session {s}: a note."
        if s in (1, 3):
            text += " It’s synthetic."
        sessions.append([{"role": "user", "content": text}])
    records.append({"uid": f"synthetic-{g}", "haystack_session": sessions,
                    "relevant_session_index": [1, 3]})
write_json(source, records)
pin = sha256_file(source)
dataset = load_benchmark("stale", source, pin)
write_json(out / "marker.json", marker_report(dataset))
archive = out / "predictions.npz"
report = run_audit(dataset, levels=("raw",), variants=("all", "position_only"),
                   folds=3, seed=0, n_boot=100, save=archive)
write_json(out / "report.json", report)
write_json(out / "replayed.json", replay(archive, sha256_file(archive), n_boot=100))
print("input sha256:", pin)
print("archive sha256:", sha256_file(archive))
```

The deliberately small example is a plumbing demonstration; do not interpret
its fitted AUROC as a benchmark result or a power analysis. The default audit
runs more variants and normalization levels than this short example.

The equivalent CLI form uses the complete digest printed above. Replace
`FULL_SHA256` with that digest, not an abbreviated hash:

```sh
memaudit audit run --benchmark stale --path runs/synthetic-audit/invented-stale.json --sha256 FULL_SHA256 --levels raw --variants all position_only --folds 3 --seed 0 --n-boot 100 --save runs/cli-predictions.npz --output runs/cli-audit.json
memaudit audit marker --benchmark stale --path runs/synthetic-audit/invented-stale.json --sha256 FULL_SHA256 --output runs/cli-marker.json
```

`audit report` takes the archive's hash, not the original input's hash:

```sh
memaudit audit report --path runs/synthetic-audit/predictions.npz --sha256 ARCHIVE_SHA256 --n-boot 100 --output runs/cli-replay.json
```

Computing a new hash of a file you just generated establishes local identity.
For a benchmark reproduction, obtain the expected digest from the protocol or
verified source record before the run; merely hashing whatever file happens to
be present does not verify its upstream identity.

## A synthetic numeric replica replay

All values below are invented. `null` denotes unavailable correctness, not a
failure scored zero. The different required blocks deliberately produce
different oracle and variance masks.

```python
from pathlib import Path
from memaudit.provenance import sha256_file, write_json
from memaudit.replica import replay

source = Path("runs/invented-outcomes.json")
document = {
    "schema": "memaudit-replica/1",
    "planned_counts": {"group-a": 3},
    "weighting": "complete_question",
    "better_scope": "pooled",
    "oracle_required": ["main", "raw"],
    "variance_required": ["main", "reseed", "judge_only"],
    "questions": [
        {"id": "q1", "group": "group-a", "main": [1, 0, 1],
         "raw": [1], "reseed": [1, 1, 0], "judge_only": [1, 0, 1]},
        {"id": "q2", "group": "group-a", "main": [0, 1, 0],
         "raw": [None], "reseed": [0, 1, 1], "judge_only": [0, 0, 1]},
        {"id": "q3", "group": "group-a", "main": [1, 1, 0],
         "raw": [1], "reseed": [1, None, 0], "judge_only": [1, 1, 0]},
    ],
}
write_json(source, document)
write_json("runs/invented-replica-report.json",
           replay(source, sha256_file(source), n_boot=100, seed=0))
print(sha256_file(source))
```

Or invoke the CLI on the created file:

```sh
memaudit replica replay --path runs/invented-outcomes.json --sha256 FULL_SHA256 --n-boot 100 --seed 0 --output runs/replica-report.json
memaudit replica rehearse --ledger runs/fake-ledger.jsonl --output runs/fake-report.json
```

The rehearsal uses `FakeClient`; it does not rerun a historical experiment. A
ledger path is required and rows are appended. Use a new path for an isolated
example. See the [numeric schema](numeric-outcomes.md) before exporting real
study outcomes or adding decision thresholds.

## Four null policies on a local Lethe checkout

Supply a reviewed checkout, plus a JSON object naming exactly these three
files and their independently recorded SHA-256 digests:

```json
{
  "bench/forgeteval/generate.py": "FULL_SHA256_FOR_GENERATE",
  "bench/forgeteval/adversarial_generated.py": "FULL_SHA256_FOR_GENERATED_CASES",
  "bench/forgeteval/adversarial.py": "FULL_SHA256_FOR_ADVERSARIAL"
}
```

The strings above are placeholders and will be rejected until replaced by full
64-character hexadecimal digests. Pin the JSON manifest itself as well:

```sh
memaudit baselines nulls --lethe-root /path/to/reviewed-lethe --pins /path/to/lethe-pins.json --pins-sha256 MANIFEST_SHA256 --output runs/nulls.json
```

The CLI uses 200 cases per template family, seed 42, four distractors, and
English. It imports no scorer from an installed package with the same name:
the three supplied source files are executed temporarily without bytecode
writes beside them. Start a fresh Python process if `bench` modules are already
loaded. See the [Lethe card](data-cards/forgeteval.md).

Optional adversarial preservation labels remain private local inputs:

```sh
memaudit baselines nulls --lethe-root /path/to/reviewed-lethe --pins /path/to/lethe-pins.json --pins-sha256 MANIFEST_SHA256 --labels /path/to/rater-a.json /path/to/rater-b.json --labels-sha256 RATER_A_SHA256 RATER_B_SHA256 --output runs/nulls-with-preservation.json
```

Each label file maps case IDs to fact-index maps, for example the invented
`{"synthetic-case": {"0": "KEEP", "1": "REMOVE"}}`. Every setup-fact index must
be covered. Do not copy benchmark fact text into these files. Agreement and
role constraints are checked; naming two files does not establish that their
raters are independent. Unknown preservation is reported separately.

## Wrong-question retrieval on an invented item file


`examples/synthetic_qi.py` writes an invented item file in the [item-file contract](REPRODUCE-PAPER.md#item-file-contract---items-file---items-sha256-hash)
and runs the BM25 row; it prints the file's digest. The CLI form:

```sh
python examples/synthetic_qi.py
memaudit qi run --items runs/synthetic-qi/items.jsonl.gz --items-sha256 FULL_SHA256 --n-boot 2000 --output runs/qi.json
```

With the optional extra (`pip install '.[hybrid]'`) and a local bge-small-en-v1.5 ONNX directory, add
`--retriever hybrid --model-path /path/to/model`. Read `rates`, `effects`, `placebo_support` and `k3` as described in
[REPRODUCE-PAPER.md](REPRODUCE-PAPER.md#report-fields). Twelve invented items are a plumbing check, not a power analysis.

## Other benchmark inputs

`--benchmark` accepts `stale`, `lme_s`, `locomo`, `locomo_plus`, `beam_100k`,
`beam_500k`, `beam_1m`, `halumem_medium`, and `personamem2`.

LoCoMo-Plus also requires `--hosts-path` and `--hosts-sha256`. PersonaMem-v2
takes a pinned manifest rather than a directory; its exact shape is in the
[data card](data-cards/personamem2.md). For raw BEAM Parquet install the local
package with `pip install '.[parquet]'`. No command fetches any dataset.

All commands accept `--output`; otherwise the report is printed as JSON.
Invalid inputs exit with status 2 and a sanitized diagnostic. Undefined JSON
statistics are `null`. A successful command is not, on its own, evidence that
the chosen input, labels, population, or scientific claim is appropriate.

Development assistance: see [PROVENANCE](../PROVENANCE.md).
