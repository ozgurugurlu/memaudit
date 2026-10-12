# BEAM — `beam_100k`, `beam_500k`, `beam_1m`

| Field | Recorded value |
| --- | --- |
| Source reference | [BEAM, arXiv:2510.27246](https://arxiv.org/abs/2510.27246), identifier recorded in the original adapter |
| Dataset upstream | [Mohammadta/BEAM](https://huggingface.co/datasets/Mohammadta/BEAM) |
| Observed dataset revision | `3205395e897e7318c7b094ef4e6047b9b82dbb03` (metadata checked 2026-10-03) |
| Raw files' last-change revision | `8b4ddc477010c07a852752fe2f27a2722755ff2b`, reported for all three files by the official metadata API |
| Raw inputs | `100K.parquet`, `500K.parquet`, `1M.parquet`, one setting per file |
| Licence evidence | CC BY-SA 4.0 in the original adapter/review; official dataset card tag `cc-by-sa-4.0` observed 2026-10-03 |
| Metadata sources | Original audit adapter and conversion records; current memaudit adapter; local streaming hashes and official file metadata |

## Local-reference input pins

| Setting / local filename | Bytes | SHA-256 |
| --- | ---: | --- |
| `beam_100k` / `100K.parquet` | 5,429,768 | `c0519be25907005ba873c927c50877471d550873039d96c041554d0075a78ace` |
| `beam_500k` / `500K.parquet` | 33,956,263 | `af05921c979355038e1761b7cde3d2dd713200dd3071b278de0200f6c7f30122` |
| `beam_1m` / `1M.parquet` | 66,156,374 | `41b5acbbb55a586b1305514ef9d9fb03365d9b3331b598a1c2dd7603d93ef533` |

All three raw files are present locally. Streaming SHA-256 checks read bytes
without loading Parquet or inspecting conversations. The digests also match
the older conversion manifest's `source_sha256` values and the official
LFS hash/size metadata for upstream `data/100K-00000-of-00001.parquet`,
`data/500K-00000-of-00001.parquet`, and `data/1M-00000-of-00001.parquet`.
The [upstream upload record](https://huggingface.co/datasets/Mohammadta/BEAM/commit/8b4ddc477010c07a852752fe2f27a2722755ff2b)
records these file pointers; their metadata was checked again at the observed
repository revision. No corpus bytes were downloaded. This confirms recorded
object identity, not the original cache acquisition revision or semantic
correctness. The licence tag remains source metadata, not a new legal review.

The raw Parquet path needs the `parquet` extra and reads `chat`,
`probing_questions`, and `conversation_id`. It does not require the research
workbench's derived JSONL. The conversation is both pool and CV group; user
messages are units. Positive labels are the union of released source-message
IDs for contradiction-resolution and knowledge-update probes. Evidence for
other task categories is not labeled positive by this particular audit.

For 100K and 500K, strict increasing message-ID validation runs over all
messages before selecting user units. For 1M, only user messages enter this
validation, matching the historical conversion scope. Conversations with
non-increasing IDs are excluded and counted. Record exclusions by setting.

The alternate local JSONL form uses `conv_id`, `messages`, `cr`, and `ku`.
Each message is `[message_id, role, session_index, text]`; CR/KU rows supply
ID arrays `a` and `b`. JSONL for 1M must already reflect the historical
user-only conversion. A manually created all-role 1M JSONL is not equivalent
to that route. Any derived input needs its own content pin and source record.

These three settings describe different populations; do not pool them or
replace a setting merely because its file is available. The observed upstream
revision is not an instruction to fetch a latest revision, and it does not
replace the explicit input digest. No Parquet, derived JSONL, or conversation
text is shipped.

Development assistance: see [PROVENANCE](../../PROVENANCE.md).
