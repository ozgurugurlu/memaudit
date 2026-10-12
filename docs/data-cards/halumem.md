# HaluMem-Medium — `halumem_medium`

| Field | Recorded value |
| --- | --- |
| File | `HaluMem-Medium.jsonl` |
| Dataset upstream | [IAAR-Shanghai/HaluMem](https://huggingface.co/datasets/IAAR-Shanghai/HaluMem) |
| Observed dataset revision | `cb04336aa1b732d4b24f5186c552456b4099806e` (metadata checked 2026-10-03) |
| File's last-change revision | `6c4dbab7af7e773615efff2a62ec249866c0351a`, reported by the official metadata API |
| Local-reference SHA-256 | `486fbc130a5c8781a2af27ffa508a1d7855245137aa449c193ac4d29c45634e7` |
| Local-reference size | 33,511,525 bytes |
| Licence evidence | CC BY-NC-ND 4.0 in the prior local review; official dataset card tag `cc-by-nc-nd-4.0` observed 2026-10-03 |
| Metadata sources | Original audit configuration and adapter identify the local input; streaming local hashing and official Hugging Face repository/file metadata identify its bytes |

The local reference bytes were hashed without decoding or parsing corpus
content. Hash and size match the official LFS object metadata for
[the file at the observed revision](https://huggingface.co/datasets/IAAR-Shanghai/HaluMem/blob/cb04336aa1b732d4b24f5186c552456b4099806e/HaluMem-Medium.jsonl).
No dataset bytes were downloaded in this check. The observed repository
revision is not asserted to be the revision originally used to acquire the
local cache; the content digest is the reproducible input pin. The licence
tag is source metadata, not an independent determination of all usage rights.

Each JSONL record represents a user `uuid` with sessions. Sessions are units;
the user is the CV group. The adapter maps question evidence to normalized
`memory_content` values from session `memory_points`. Normalization lowercases
and collapses whitespace. It is textual matching, not a semantic resolution
of evidence annotations.

Matches at or before the question's session are preferred. When evidence has
only later matches, the adapter retains those and increments
`future_evidence_fallbacks`. Each pool ends at the later of the question
session and the last matched evidence session. Questions without mapped
evidence produce no pool; unmapped evidence entries are counted. The candidate
pool is therefore neither always the full history nor always causal.

This pool-end rule can create a strong position effect. A full-history or
strictly causal analysis is a different protocol and must be named as such.
Questions and memory-point text supply labels/matching, not style features;
the feature units consume session dialogue only.

The prior workbench adapter did not enforce a hash; the local-reference pin
above now identifies the supplied file explicitly. Use this full digest when
reproducing that input, and record another digest as a changed input. Neither
original nor converted data is bundled.

Development assistance: see [PROVENANCE](../../PROVENANCE.md).
