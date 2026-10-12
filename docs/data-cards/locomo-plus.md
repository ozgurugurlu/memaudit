# LoCoMo-Plus — `locomo_plus`

| Field | Recorded value |
| --- | --- |
| Upstream | [xjtuleeyf/Locomo-Plus](https://github.com/xjtuleeyf/Locomo-Plus) |
| Code/data checkout revision | `059f4e3d38f7f1f96765e8e2cb7de3097551bffb` |
| Inputs | `data/locomo_plus.json` and ordered `data/locomo10.json` hosts |
| Cue-file SHA-256 | `af2fc6e5e0e88735e28d8dd1ef474b718861a73beb21779809e3b9e1a4fe3d23` at the checkout revision above (measured in the 2026-10-03 adapter-parity check; matches its tracked Git blob). A user-supplied full pin remains mandatory |
| Host SHA-256 | `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4` for the recorded shared LoCoMo file |
| Sizes | Measured from both pinned inputs at runtime |
| Licence status | No licence file recorded for the LoCoMo-Plus checkout; host data retain their separate LoCoMo terms |
| Metadata source | Recorded adapter constants and upstream licence review |

Both `--hosts-path` and `--hosts-sha256` are required. Item i uses host
`i % number_of_supplied_hosts`, so preserve upstream host order. A host
conversation is the CV group; an inserted-cue item is a pool; individual turns
are units. All turns use the adapter's `user` role for feature extraction.

The adapter takes A:/B: lines from the cue dialogue and inserts them into the
host timeline using the recorded time-gap construction. Gap units use 7 days
per week, 30 per month, and 365 per year. The trigger query is excluded. Cue
turns are positive; other host turns are negative under this label definition.

Host turns are shared across pools, but position features are computed from
their position in the **current** inserted-cue pool. This corrects the
historical first-occurrence position reuse; do not claim byte-for-byte
reproduction of that older position-only result. Style features continue to
use the shared turn text only.

High AUROC can coexist with materially lower top-one cue retrieval. Hit@k
means any cue turn, not all cue turns or successful answering. Neither cue
dialogues nor unlicensed upstream prompts are copied into this package.
Unresolved data terms remain unresolved despite local hash verification.

Development assistance: see [PROVENANCE](../../PROVENANCE.md).

cue-file hash recorded; the same two
files feed `memaudit qi run --benchmark locomo_plus` (one turn per unit, both speakers score, gold = cue turns, question
= trigger-query A/B lines, group = host conversation).
