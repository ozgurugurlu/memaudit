<div align="center">

# memaudit

### Finding the Evidence Without the Question: Auditing Agent-Memory Benchmarks

**Can a benchmark's evidence be found without the question? Audit it before you trust the score.**

[![Paper](https://img.shields.io/badge/Paper-PDF-b31b1b)](paper/memaudit-paper.pdf)
[![Paper (Markdown)](https://img.shields.io/badge/Paper-Markdown-555555)](paper/paper.md)
[![License](https://img.shields.io/badge/License-Apache--2.0-blue)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB)](pyproject.toml)
[![Version](https://img.shields.io/badge/version-0.1.0-informational)](CHANGELOG.md)
[![CI](https://github.com/ozgurugurlu/memaudit/actions/workflows/ci.yml/badge.svg)](https://github.com/ozgurugurlu/memaudit/actions/workflows/ci.yml)

[Key findings](#key-findings) · [What it does](#what-memaudit-does) · [Install](#install) · [Quickstart](#quickstart-on-the-bundled-synthetic-examples) · [Reproductions](#reproductions-with-public-benchmark-data) · [Paper](paper/README.md) · [Data and licensing](#data-and-licensing) · [Citation](#citation)

</div>

Offline CPU tools that audit agent-memory benchmarks without running a memory system: can evidence be found without the
question, does retrieval with the *wrong* question still find it, what do trivial forgetting policies score, and how much do
repeated runs of one pipeline disagree.

**Version 0.1.0.** Author: **Özgür Uğurlu**. Code and documentation: [Apache-2.0](LICENSE).

## Key findings

From the accompanying paper ([PDF](paper/memaudit-paper.pdf), [Markdown](paper/paper.md)):

- **Evidence can be found without the question in some benchmarks.** On STALE, the character U+2019 marks all 800
  evidence sessions and none of 19,200 distractors, so one rule recovers both evidence sessions in all 400 scenarios.
  Question-blind classifiers reach an AUROC of 1.000 on STALE and .995 on LoCoMo-Plus and are weaker elsewhere. On BEAM,
  retrieval with another item's question is equivalent to chance under fair nulls.
- **The cue would pay if used.** Naming STALE's cue-identified pair improves judged accuracy by 13–21 points over notes
  naming two retrieved sessions, for four readers from four vendors. Those comparator notes themselves score below a
  generic instruction.
- **Item-level labels are unstable.** Rebuilds of one memory pipeline disagree on about 16% of judged labels, while
  run-level accuracy varies by about one point.
- **Scoring rules matter.** ForgetEval's public score can reward a policy that wipes memory.
- **The tested systems show no large benefit from the cues.** Removing typography and clock times together leaves a
  plain reader, a hybrid RAG pipeline and a mem0 pipeline within their pre-specified practical bounds; the intervals
  exclude a net benefit larger than about 3.8, 1.6 and 1.4 points.

We do not estimate inflation in published scores; see the paper's limitations.

## What memaudit does

| Measurement | Command | What it reports |
| --- | --- | --- |
| Question-blind unit audit | `memaudit audit run` / `marker` / `report` | 31 style features per unit (never the question, ids or labels), grouped 5-fold cross-validation, macro within-pool AUROC with cluster-bootstrap intervals, on the full population and after removing test rows whose exact text also occurs in training |
| Wrong-question retrieval with fair nulls | `memaudit qi run` | For each item, ten questions from *other* groups rank its units (BM25 by default; the S16 hybrid as an option); any-gold@k against uniform chance, turn-weighted (Plackett–Luce) chance and matched-placebo gold; chance-corrected excess CE = (QI − null)/(1 − null), reported in the `kappa` output field with the wider of a two-way cluster bootstrap and a CR1 t interval; a query-blind feature scan that labels a row cue-dominated; best query-blind prior |
| Null forgetting policies | `memaudit baselines nulls` | Store-nothing, wipe-plus-replacement, keep-all and oracle-target under the native ForgetEval scorer from your own pinned Lethe checkout, with preservation where labels allow |
| Replica replay | `memaudit replica replay` / `rehearse` | Gain of the union of repeated runs over their mean and over the better run, metric-specific masks, nested variance, best-of-k, placebo; `rehearse` is an invented FakeClient run |

Every input is a local file named on the command line with its full SHA-256. Reports contain identifiers, hashes, counts
and statistics; see [DATASHEET.md](DATASHEET.md).

## What memaudit does not do

- **It ships no benchmark data**, prompts, model outputs, judge outputs, trained models or per-question outcome matrices,
  and it downloads nothing. You obtain public benchmark files yourself and pass them with their hashes.
- **No language model runs.** There is no reader, judge, extractor or provider client; the only client is an invented
  `FakeClient`. End-to-end QA accuracy, reader ladders and judge results are therefore not reproduced here.
- **Detectability is not exploitation.** A high audit AUROC shows that annotated evidence differs in style from other
  units under that pool, label and grouping definition. It does not show that a memory system uses the cue, that a
  published score is inflated, or why the cue exists. Wrong-question retrieval above a null holds for one retriever stack
  and one unit definition only.
- The audit's question-free schema cannot prove that text you supply is semantically independent of a question.

## Install

Python 3.12 (`requires-python >= 3.12`), the only version verified with the real dependencies. Python 3.11 support
is not claimed: it needs a green CI run on 3.11 with the real `py-rust-stemmers` wheel first. From a checkout, in a
fresh environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install .                  # core: numpy, scipy, scikit-learn, threadpoolctl, py-rust-stemmers
.venv/bin/python -m pip install '.[parquet]'       # optional: raw BEAM Parquet input
.venv/bin/python -m pip install '.[hybrid]'        # optional: fastembed, for the S16 hybrid retriever
.venv/bin/memaudit --help
```

Offline: on a connected machine run `pip wheel '.[hybrid,parquet]' -w wheelhouse` (drop extras you do not need); this
builds the memaudit wheel and collects every dependency wheel. Copy `wheelhouse/` and install with
`pip install --no-index --find-links wheelhouse 'memaudit[hybrid]'`. After installation no command uses the network. The hybrid retriever needs a local copy of the `Qdrant/bge-small-en-v1.5-onnx-Q` model directory, passed with
`--model-path`; memaudit never fetches it (`HF_HUB_OFFLINE=1`, `local_files_only=True`).

## Quickstart on the bundled synthetic examples

All example text is invented. Run from the repository root (examples write under `runs/`):

```sh
python examples/synthetic_audit.py          # style audit: a planted typographic cue is detected, then removed by F1
python examples/synthetic_qi.py             # wrong-question retrieval: a planted shared word lifts QI far above every null
python examples/synthetic_nulls.py          # the four forgetting policies on invented facts
python examples/replica_rehearsal.py runs   # FakeClient rehearsal and replica replay (no model service)
memaudit qi run --items runs/synthetic-qi/items.jsonl.gz --items-sha256 <digest printed by synthetic_qi.py> --output runs/qi.json
```

[docs/quickstart.md](docs/quickstart.md) has the same flows step by step, including the CLI forms and the pinned Lethe
command.

## Reproductions with public benchmark data

Each command below is one command once the public files are on disk. Download them yourself from the upstream sources in
[docs/data-cards/](docs/data-cards/README.md); do not commit them. The hashes are those of the files used for the paper;
a file with other bytes is a different input and the command refuses it.

| File | Upstream | SHA-256 |
| --- | --- | --- |
| `T1_T2_400_FULL.json` | Hugging Face `STALEproj/STALE`, revision `617c51dc200b5ab09970834144c7e51c77959af0` | `5f3ec375179e20e2e94469e018189188f34e2e7e5f21cbecbd99fcfa648c1876` |
| `data/locomo_plus.json` | GitHub `xjtuleeyf/Locomo-Plus`, commit `059f4e3d38f7f1f96765e8e2cb7de3097551bffb` | `af2fc6e5e0e88735e28d8dd1ef474b718861a73beb21779809e3b9e1a4fe3d23` |
| `data/locomo10.json` (hosts, upstream order) | The same Locomo-Plus commit (LoCoMo conversations from `snap-research/locomo`; check the hash if you take them from there) | `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4` |

The reproductions below identify the measurements by method and dataset; paper numbering can vary by version.

### (a) Question-blind AUROC

```sh
memaudit audit run --benchmark stale --path T1_T2_400_FULL.json \
  --sha256 5f3ec375179e20e2e94469e018189188f34e2e7e5f21cbecbd99fcfa648c1876 \
  --levels raw --variants all --output stale-audit.json

memaudit audit run --benchmark locomo_plus --path locomo_plus.json \
  --sha256 af2fc6e5e0e88735e28d8dd1ef474b718861a73beb21779809e3b9e1a4fe3d23 \
  --hosts-path locomo10.json --hosts-sha256 79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4 \
  --levels raw --variants all --output locomo_plus-audit.json
```

Read `variants.raw__all.duplicate_filtered.auroc_macro` (`mean`, `lo`, `hi`) and `metric_pools`. Expected (macro within-pool AUROC after the test-duplicate exclusion; 95% group bootstrap, 2,000 draws, seed 0):

| Setting | Expected AUROC [95% interval] | Scored pools | Tolerance |
| --- | --- | --- | --- |
| STALE | 1.000 [1.000, 1.000] | 400 of 400 (9,460 scored rows, 10,540 masked) | exact at three decimals |
| LoCoMo-Plus | 0.995 [0.991, 0.997] | 393 of 401 | ±0.002 on the mean and each endpoint |

The local verification run (2026-10-04) gave STALE 1.000 [1.000, 1.000] and LoCoMo-Plus 0.9947 [0.9911, 0.9973],
identical at four decimals to the paper's recomputed values (largest difference 1.3e-5). The classifier is re-fitted,
so other scikit-learn versions can move the later decimals. Not reproduced by this command: the F1/F2 fixes and ablations of the paper's appendix (drop
`--levels/--variants` to run them), the seven other audit settings (same command with their `--benchmark`), and the
historical LoCoMo-Plus position-only probe (memaudit uses current-pool positions).

### (b) Wrong-question retrieval with fair nulls (LoCoMo-Plus)

```sh
# BM25 (default; no optional dependency)
memaudit qi run --benchmark locomo_plus --path locomo_plus.json \
  --sha256 af2fc6e5e0e88735e28d8dd1ef474b718861a73beb21779809e3b9e1a4fe3d23 \
  --hosts-path locomo10.json --hosts-sha256 79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4 \
  --output locomo_plus-qi-bm25.json

# S16 hybrid (BM25 + bge-small-en-v1.5, RRF; needs '.[hybrid]' and a local model directory)
memaudit qi run --benchmark locomo_plus --path locomo_plus.json \
  --sha256 af2fc6e5e0e88735e28d8dd1ef474b718861a73beb21779809e3b9e1a4fe3d23 \
  --hosts-path locomo10.json --hosts-sha256 79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4 \
  --retriever hybrid --model-path /path/to/bge-small-en-v1.5-onnx-Q --output locomo_plus-qi-hybrid.json
```

Read `rates["5"]` (`QI`, `uniform`, `turn_weighted`, `placebo`, `n_support`), `effects` (`turn_weighted/kappa`,
`placebo/kappa`: `estimate`, `ci95`), `placebo_support`, `k3` and `best_query_blind_prior`. Expected (401 items, 10 host
conversations, any-gold@5, ten wrong questions per item):

| Retriever | QI | Uniform | Turn-weighted | Matched placebo (support) | kappa, turn-weighted [95%] | kappa, placebo [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| BM25 | 4.51% | 1.67% | 1.67% | 1.54% (401/401) | not in the paper | not in the paper |
| Hybrid (paper) | 2.99% | 1.67% | 1.67% | 1.15% (401/401) | 0.013 [0.004, 0.023] | 0.019 [0.009, 0.029] |

Also expected: no item starved of wrong questions (421 same-host candidates skipped); query-blind scan maximum 0.692
(characters), so the row is **not** cue-dominated; best query-blind prior `pos_desc` (last units first) 8.23%. Turn-weighted
chance equals uniform chance here because every unit is one turn. The paper's sentence is "LoCoMo-Plus is slightly above
its null (kappa = 0.013 [0.004, 0.023])"; the row is exploratory and carries no registered tier.

Tolerance: BM25 is deterministic and should match exactly at the printed precision. The hybrid depends on ONNX
runtime arithmetic; allow ±0.2 percentage points on each rate and ±0.005 on kappa and its endpoints, and report anything
larger as a discrepancy. In the local verification run both retrievers matched the stored S16 aggregates exactly (all
rates at k = 1, 5, 10 and every hybrid kappa estimate and interval endpoint), with FastEmbed 0.8.1 on macOS arm64.

Not reproduced here: the confirmatory BEAM and HaluMem-Medium rows and their Holm-adjusted tiers (memaudit packages no
BEAM or HaluMem item converter; an S16-contract item file can be passed with `--items`), the cross-benchmark and
different-type peers, constant queries, the random-score null, the similarity strata, and anything involving a language
model. See [docs/REPRODUCE-PAPER.md](docs/REPRODUCE-PAPER.md) for the item-file contract, the full output fields and the
verification record.

## Data and licensing

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

See [LICENSING.md](LICENSING.md) and [DATASHEET.md](DATASHEET.md) for scope and output handling.

## Documentation

- [Quickstart](docs/quickstart.md), [paper reproductions and item-file contract](docs/REPRODUCE-PAPER.md)
- [Audit, null and replica protocols](docs/protocol.md), [numeric replica schema](docs/numeric-outcomes.md),
  [fake client, ledger, caps, locks and splits](docs/clients.md)
- [Data cards for nine audit settings](docs/data-cards/README.md), [licence status](docs/licences.md),
  [LICENSING.md](LICENSING.md), [NOTICE](NOTICE), [PROVENANCE](PROVENANCE.md),
  [third-party inventory](docs/third-party-inventory.md)
- [Output datasheet](DATASHEET.md), [change log](CHANGELOG.md), [citation metadata](CITATION.cff),
  [historical reproduction scope](docs/REPRODUCTION.md)

## Development

```sh
make test        # offline test suite (invented data only)
make ci          # tests, hygiene scan, offline sdist/wheel build, wheel import, CLI and examples, tests against the wheel
```

`.github/workflows/ci.yml` runs the same suite on Linux and macOS for Python 3.12 when GitHub Actions runs on the repository. Python
3.11 is not in the matrix; add it (and lower `requires-python`) only after a green 3.11 run with the real
`py-rust-stemmers` wheel.

## Citation

```bibtex
@misc{ugurlu2026memaudit,
  title        = {Finding the Evidence Without the Question: Auditing Agent-Memory Benchmarks},
  author       = {U{\u{g}}urlu, {\"O}zg{\"u}r},
  year         = {2026},
  howpublished = {\url{https://github.com/ozgurugurlu/memaudit}},
  note         = {Paper and memaudit 0.1.0 toolkit}
}
```

Machine-readable citation metadata is in [CITATION.cff](CITATION.cff).
