# Datasheet for memaudit outputs


memaudit produces measurement reports about benchmark files that the user supplies. This datasheet describes those
**outputs**; the package itself contains no benchmark data. The inputs are described by the
[data cards](docs/data-cards/README.md).

## Motivation and intended use

Outputs let benchmark maintainers and authors check, before relying on a benchmark: whether annotated evidence can be
told apart without the question, whether wrong questions retrieve it above fair chance, what trivial forgetting policies
score, and how much repeated runs of one pipeline disagree. They support statements about a benchmark file under stated
unit, label, pool and grouping definitions.

They are **not** intended to rank benchmarks or memory systems, to claim that a system exploits a cue, that a published
score is inflated, or that a benchmark is free of other cues. They are not evidence of answer correctness.

## Composition: what each report contains

| Report (`schema`) | Command | Fields |
| --- | --- | --- |
| `memaudit-audit-report/1` | `audit run`, `audit report` | Per variant and population (`full_population`, `duplicate_filtered`): row, pool, group, positive and masked counts; pooled AUROC; macro within-pool AUROC and hit@1/5/10 with cluster-bootstrap `lo`/`hi`, `n`, `n_clusters`; random hit expectations; fix verdicts; univariate signed AUROC per feature name; input hashes and byte sizes; adapter counters (numbers and booleans only) |
| optional `--save` archive (`.npz`) | `audit run` | Numeric arrays only: binary labels, integer pool/group/fold codes, duplicate mask, out-of-fold scores, the 31 raw feature values per row; metadata restricted to an allowlist. Pickle is disabled on load |
| `memaudit-marker/1` | `audit marker` | Marker code points (`U+2019` form, never the text), marked and total counts per class, exact-evidence pools, ranking metrics |
| `memaudit-qi-report/1` | `qi run` | Settings; sample and exclusion counts; peer exclusion counts; per k: QI, uniform, turn-weighted and placebo rates, QI on supported items, support count, true-question hit, eight prior rates; per null and scale: estimate, 95% interval (wider-of, t, bootstrap), item and cluster counts; placebo support share; K3 feature AUROCs; best prior name and rate; input hashes and sizes; encoder name, version and model-file hashes for the hybrid |
| `memaudit-nulls/1` | `baselines nulls` | Per policy and template family: public pass counts, derivable/must-keep counts, preservation counts or `unknown`; parameters; pinned source hashes |
| `memaudit-replica-report/1` | `replica replay` | Masks, oracle gains in percentage points, uncertainty, variance components, best-of-k, placebo, optional fact-set Jaccard summaries, rule outcomes; input hash |
| `memaudit-ledger/1` rows | client wrappers, `replica rehearse` | Typed metadata per attempt: identifiers, timestamps, counters, cache and billing flags, hashes; no prompt or response text |

Undefined statistics are written as JSON `null`, never `NaN`.

## Privacy: identifiers and numbers only

- **No text by construction.** Report builders take only counts, statistics, hashes and identifiers. Question, unit,
  evidence and fact text are used in memory and are not written.
- **Output scan.** `qi run` refuses to return a report in which any string equals or contains a question or unit text of
  20 or more characters (`memaudit.qi.assert_text_free`). Audit metadata pass a strict field allowlist; adapter free text
  is dropped. Saved archives hold numeric arrays only.
- **Errors.** Every CLI failure exits with status 2 and a fixed message; input text, file paths and offending values are
  never echoed. The optional-dependency message is fixed text.
- **Repository scan.** `scripts/hygiene_scan.py --root .` (run by `make ci` and CI) reports counts only for home-directory
  paths, internal hosts, key-shaped strings, environment files, data/model artefacts, pasted benchmark-schema keys and,
  with `--corpus`, 10-word overlaps with local benchmark files. It never prints a match.
- **What can still be sensitive.** Item, unit and group identifiers come from the benchmark and can be meaningful;
  per-row numeric arrays (`--save`) and replica outcome matrices are per-question data. Treat them as you would the
  benchmark; do not publish them without the benchmark's terms allowing it. The scan is a bounded check, not proof
  against paraphrase or every secret format.

## Collection and processing

Outputs are computed locally on CPU from files named on the command line, each checked against a full SHA-256 pin
(recorded in the report with its byte size). Randomness is seeded from registered salts or the documented `--seed`;
the QI path and the replays are deterministic, and the audit re-fits a classifier whose last digits can vary with the
scikit-learn version.

## Distribution and licensing of outputs

This release distributes **code, documentation, synthetic examples, and aggregate statistics only**.
It includes no benchmark conversations, raw model or judge outputs, converted benchmark files,
per-item outcomes, fact labels, prediction archives, or model weights. Users obtain each input
from its upstream publisher under its own terms. Apache-2.0 covers this project's code and
documentation; it grants no rights to benchmark data or benchmark-derived artifacts.

The table records the research project's public-metadata observations as of 2026-10-04,
with uncertainty preserved. It is not a new licence grant or a clearance determination.
Upstream references and input identities are in the [data cards](docs/data-cards/README.md).

| Benchmark | Recorded terms | Data-use caveat |
| --- | --- | --- |
| STALE | CC BY 4.0 in the study configuration; not independently verified | Attribute the dataset; obtain files upstream |
| LongMemEval-S | Repository MIT | ShareGPT filler has no verified data licence; FastChat's Apache-2.0 covers code, not those conversations. UltraChat declares MIT with research/education intended-use language. Exact filler snapshots remain unverified |
| LoCoMo | CC BY-NC 4.0 | Non-commercial research statistics only; no conversation redistribution here |
| LoCoMo-Plus | No licence found in the recorded checkout | Local exploratory statistics only; host conversations retain LoCoMo's terms |
| BEAM | CC BY-SA 4.0 | Attribution and share-alike conditions apply to adapted data; none is shipped |
| HaluMem | CC BY-NC-ND 4.0 | Statistics only; no original, converted, or derived data is shipped |
| PersonaMem-v2 | Dataset card CC BY 4.0 | PersonaHub upstream declares CC BY-NC-SA 4.0, research-only use, and generating-model conditions; the declarations are not reconciled |
| ForgetEval (Lethe) | MIT for repository/benchmark in recorded metadata | User-supplied pinned source executes locally; preserve upstream notices when copying it |
| MemoryAgentBench | MIT in recorded repository and dataset card | Listed for context; no memaudit command uses it |
| MemOps | MIT in recorded metadata | Listed for context; no memaudit command uses it |

The memaudit licence does not override input-data terms. Optional numeric archives
and per-question outcome matrices are outside the public release even when they
contain no dialogue text. See [the licensing statement](LICENSING.md).

## Maintenance

Report schemas carry a version string; a breaking change bumps it and is listed in [CHANGELOG.md](CHANGELOG.md).
Problems with a benchmark's construction should go to its maintainers first (see the release checklist).
