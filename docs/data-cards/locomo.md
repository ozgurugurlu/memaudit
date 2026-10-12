# LoCoMo — `locomo`

| Field | Recorded value |
| --- | --- |
| Upstream | [snap-research/locomo](https://github.com/snap-research/locomo) |
| File revision | `cbfbc1dba6bc53d00625212a0f22d55ffee7c1fc`, recorded as the last change to the file |
| File | `data/locomo10.json` |
| SHA-256 | `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4` |
| Recorded size | 2,805,274 bytes |
| Licence evidence | Local upstream `LICENSE.txt`: Attribution-NonCommercial 4.0 International |
| Metadata source | Recorded adapter constants and upstream licence |

A conversation's sessions are units shared across its question pools. Each
evidence-bearing question forms a ranking pool over those sessions; the whole
conversation is the CV group. Do not make each question an independent fold.
The first session's first speaker defines the unit's user role for role-split
length features.

Category-5 questions are excluded. Evidence dialogue IDs are mapped to session
IDs, including the source-compatible extra-colon form `D:2:1` as well as
`D2:1`. Unresolved evidence is counted; questions with no mapped evidence are
excluded. The adapter does not expose question text to the classifier.

The pinned file describes ten conversations. A large number of question rows
does not increase the number of independent conversations. Shared sessions,
pool definitions, evidence repair, and exclusions must match before calling a
result a historical reproduction.

No conversations or upstream reader prompts are included. Per-question outcome
matrices remain private local inputs unless separately cleared for release.

Development assistance: see [PROVENANCE](../../PROVENANCE.md).
