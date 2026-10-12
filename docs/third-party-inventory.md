# Third-party inventory

Development assistance: see [PROVENANCE](../PROVENANCE.md). This is an observed local install
inventory, not a licence clearance or a promise that another platform resolves
the same versions. Dependencies were installed separately from the official
Python package index/cache; their code, wheels, models, and data are not
vendored in this distribution. Preserve each dependency's own notices when
redistributing its binaries.

## Verified local runtime and check environment

| Distribution | Installed version | Licence metadata observed in installed distribution | Role |
| --- | --- | --- | --- |
| `numpy` | `2.5.3` | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | Core runtime |
| `scipy` | `1.18.1` | BSD License | Core runtime |
| `scikit-learn` | `1.9.1` | BSD-3-Clause | Core runtime |
| `threadpoolctl` | `3.7.0` | BSD-3-Clause | Core runtime |
| `py_rust_stemmers` | `0.1.8` | MIT LICENSE in exact PyPI source distribution; metadata fields absent (evidence below) | Core runtime |
| `pyarrow` | `25.0.1` | Apache-2.0 | Optional Parquet adapter |
| `pytest` | `9.1.1` | MIT | Test/build dependency or its dependency |
| `build` | `1.6.1` | MIT | Test/build dependency or its dependency |
| `joblib` | `1.6.0` | BSD-3-Clause | Transitive runtime |
| `cloudpickle` | `3.1.2` | BSD License classifier | Transitive runtime |
| `narwhals` | `2.26.0` | MIT | Transitive runtime |
| `packaging` | `26.3` | Apache-2.0 OR BSD-2-Clause | Test/build dependency or its dependency |
| `pluggy` | `1.6.0` | MIT License | Test/build dependency or its dependency |
| `iniconfig` | `2.3.0` | MIT | Test/build dependency or its dependency |
| `Pygments` | `2.21.0` | BSD-2-Clause | Test/build dependency or its dependency |
| `pyproject_hooks` | `1.3.3` | MIT | Test/build dependency or its dependency |

`snowballstemmer>=3` is an optional alternative tokenizer backend. It was not
installed in the verified environment; default tokenization uses the tested
`py-rust-stemmers` backend. Build tooling used setuptools 84.0.0 and wheel
0.48.0 (both report MIT expressions); their own and transitive notices apply if those dependencies are redistributed.

Licence expressions/classifiers are package-maintainer metadata. Compiled
scientific wheels may carry additional bundled-library notices beyond a top
level expression; SciPy in particular reports a BSD classifier alongside a
long notice. No exhaustive transitive binary-licence audit is claimed.

## Optional `hybrid` extra and test-only comparisons

Observed in the local environment used
for the hybrid verification run (macOS arm64, CPython 3.12.12); installed metadata only, not a clearance.

| Distribution | Installed version | Licence metadata observed | Role |
| --- | --- | --- | --- |
| `fastembed` | `0.8.1` | Apache-2.0 | Optional `hybrid` extra (S16 dense encoder) |
| `onnxruntime` | `1.30.0` | MIT License | Transitive (fastembed) |
| `tokenizers` | `0.23.2` | Apache Software License classifier | Transitive (fastembed) |
| `huggingface-hub` | `1.33.0` | Apache-2.0 | Transitive (fastembed); memaudit sets offline mode and never downloads |
| `loguru` | `0.7.3` | MIT License classifier | Transitive (fastembed) |
| `mmh3` | `5.3.0` | MIT License | Transitive (fastembed) |
| `pillow` | `12.3.0` | MIT-CMU | Transitive (fastembed) |
| `requests` | `2.34.2` | Apache-2.0 | Transitive (fastembed) |
| `tqdm` | `4.70.1` | MPL-2.0 AND MIT | Transitive (fastembed) |
| `rank-bm25` | `0.2.2` | "Apache2.0" (free text) | Not a dependency; the BM25 equality test uses it only when present |

The bge-small-en-v1.5 ONNX model (`Qdrant/bge-small-en-v1.5-onnx-Q`) is never shipped or downloaded by memaudit; users
supply it and its terms apply. `py-rust-stemmers` is also a FastEmbed dependency; its MIT licence is evidenced below.

## py-rust-stemmers 0.1.8 licence evidence

Checked 2026-10-12. The [maintainer's PyPI release page](https://pypi.org/project/py-rust-stemmers/0.1.8/)
identifies the project licence as MIT. The exact published
[source distribution](https://files.pythonhosted.org/packages/6b/c1/9763f9fb1cd73f9c317a83feeed6e0d4af320c6bbddab47b4a94f3a47d0c/py_rust_stemmers-0.1.8.tar.gz)
contains an MIT `LICENSE`, with copyright 2024 qdrant.

- Source distribution SHA-256: `6b0f6f48bc54d607aed802de872fcd5a71bae969a6760976dc78ce55e8eaf3da`.
- Included LICENSE SHA-256: `f79ad92c0936186de30f349d55f5e4162845793661e5f8b4d07e8734a92fed6a` (1,063 bytes).
- The PyPI metadata licence field and licence classifier are absent. That is a metadata omission;
  the licence conclusion above comes from the licence file in the exact versioned distribution.
- This resolves the earlier top-level package-licence question. It does not assert an exhaustive
  audit of every Rust dependency or compiled wheel. No dependency source or binary is bundled here.

## Reused source and runtime source loading

Development roles and component origins are documented in [PROVENANCE](../PROVENANCE.md).
Scientific adapters, normalization, estimators, decision rules, and fixed tokenization
were adapted from the author's research code. Deterministic constants are retained.
Lethe's pinned executable files are loaded from the user's checkout and are not copied
into either distribution; their notices and data terms apply separately.

The [data cards](data-cards/README.md) and [licensing statement](../LICENSING.md)
record benchmark terms. No benchmark data, raw model output, historical outcome matrix,
hosted client, credential reader, or checkpoint is included.
