# Development provenance

Author and copyright holder: **Özgür Uğurlu**. Code and documentation are
licensed under [Apache-2.0](LICENSE); see [NOTICE](NOTICE).

| Component | Development origin and scope |
| --- | --- |
| `src/memaudit/clients/`, `lock.py`, `splits.py` | Shared client, ledger, cap, lock and split infrastructure adapted from the research implementation |
| `schema.py`, `data.py`, `features.py`, `audit.py`, `stats.py` | Research implementations adapted to a local, question-blind package API with input hashes and numeric output constraints |
| `nulls.py`, `tokenizer.py` | Local deterministic controls and registered tokenization; Lethe's executable source is supplied separately by the user |
| `replica.py`, `rules.py` | Numeric replay estimators, masks, uncertainty calculations, and interpretation rules adapted from the research implementation |
| `qi.py`, `dense.py` | Wrong-question retrieval and fair nulls; optional local hybrid encoding; BM25 arithmetic follows rank-bm25 0.2.2 without vendoring that package |
| `scripts/hygiene_scan.py`, tests and examples | Release checks and invented fixtures; the protected-file test uses an in-memory path so it tests detection without creating or opening a protected file |

The public release contains no model-service client, benchmark download helper,
private study report, benchmark conversation, or historical per-item model output.
Examples use invented text; reported reproduction numbers are aggregates.

Deterministic split and sampling salts are retained for reproducibility. They are
algorithm constants rather than network addresses or local paths.
Dependency notices and the exact `py-rust-stemmers` license evidence are in the
[third-party inventory](docs/third-party-inventory.md). The full text of LICENSE
was downloaded from its publisher.
