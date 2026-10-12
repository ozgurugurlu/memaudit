# Change log

## 0.1.0 — 2026-10-12

- First public release of the offline CPU toolkit: question-blind evidence audits,
  wrong-question retrieval against fair nulls, deterministic forgetting-policy
  controls, and numeric replica estimators.
- Wrong-question retrieval includes BM25 by default and an optional local hybrid
  retriever. No model service or model download is included.
- Apache-2.0 code/documentation license, official license text, named author and
  copyright holder, citation metadata, and statistics-and-code-only data statement.
- Resolved the `py-rust-stemmers` license metadata gap using the MIT LICENSE in
  the exact 0.1.8 source distribution from PyPI.
- Removed private review references from public documentation.
- Corpus-overlap checks require word tokens to contain a letter or digit;
  punctuation-only runs no longer count as shared prose. Streamed matches and
  contractions remain covered by focused synthetic tests.
- The hygiene test now simulates a protected file in memory and asserts that the
  scanner reports its name without reading it. No protected file is created.
- Python 3.12 remains the verified interpreter; package-index upload is disabled
  by the `Private :: Do Not Upload` classifier. GitHub Actions runs the offline
  suite on Linux and macOS.

## Earlier development candidates

The 2026-10-03 candidate introduced the audit, null-policy, replica, client/ledger,
locking, split, schema, and data-card functionality. The 2026-10-04 candidate added
wrong-question retrieval, the optional hybrid extra, the offline CI runner,
portable reproduction instructions, and synthetic hygiene coverage.
Historical aggregate reproduction checks are described in docs/REPRODUCTION.md
and docs/REPRODUCE-PAPER.md; they are distinct from release-artifact verification.
