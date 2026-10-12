# Licensing and data-use statement

## Code and documentation

memaudit 0.1.0 code and documentation are licensed under **Apache-2.0**.
The author and copyright holder is **Özgür Uğurlu**.

[LICENSE](LICENSE) was downloaded unchanged from the
[Apache Software Foundation](https://www.apache.org/licenses/LICENSE-2.0.txt) on
2026-10-12; SHA-256 `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`.
[NOTICE](NOTICE) carries the copyright notice. Package metadata declares
`license = "Apache-2.0"` and `license-files = ["LICENSE", "NOTICE"]`.
The `Private :: Do Not Upload` classifier remains: package-index publication is not part of this release.

Third-party dependencies keep their licences and are not bundled. The
[`py-rust-stemmers` licence evidence](docs/third-party-inventory.md#py-rust-stemmers-018-licence-evidence)
resolves the earlier missing-metadata item using its exact source distribution.

## Data: statistics and code only

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

The output [datasheet](DATASHEET.md) distinguishes aggregate reports from optional
numeric archives and user-supplied outcome matrices. Those per-row artifacts must
remain local unless their separate terms permit redistribution.
