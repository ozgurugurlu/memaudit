# PersonaMem-v2 — `personamem2`

| Field | Recorded value |
| --- | --- |
| Inputs | `benchmark_text.csv` and explicitly selected persona-history JSON files |
| Dataset upstream | [bowen-upenn/PersonaMem-v2](https://huggingface.co/datasets/bowen-upenn/PersonaMem-v2) |
| Observed dataset revision | `ed956dea41521fc4499acbc63f966e0fd3c053ba` (metadata checked 2026-10-03) |
| CSV last-change revision | `76e580fbb41ae32fe59a222c467338ce77cd6f5a`, reported by official file metadata |
| History last-change revisions | `3525e6553db46cf9ff51e11c7aec300ac2763180` for persona 513; `d23274ab390348b05ccfa4299f43c73f37657310` for the other seven listed histories |
| Licence evidence | CC BY 4.0 in the previous local note; official dataset card tag `cc-by-4.0` observed 2026-10-03 |
| Metadata sources | Original audit adapter's sorted `hist32/*.json` selection; local filename inventory and streaming hashes; official Hugging Face repository/file metadata |

## Local-reference input pins

The original cached subset contains precisely the eight histories below.
The local CSV name `benchmark_text.csv` corresponds to upstream
`benchmark/text/benchmark.csv`; local `hist32/` history basenames correspond
to upstream `data/chat_history_32k/` basenames. These are file identifiers,
not per-question outcomes.

| Local input | Bytes | SHA-256 |
| --- | ---: | --- |
| `benchmark_text.csv` | 42,426,457 | `95f2a8a324aab7baf2af937feae12731369e2abf7cad5ab3e170594cb25a3e52` |
| `hist32/chat_history_250913_163134_persona411.json` | 177,221 | `21d92442f8343d9c80df64eac96e532ab57f286517961892b082f587e2067fa4` |
| `hist32/chat_history_250913_163134_persona513.json` | 168,381 | `4d56fdd4f2df3ec9d8f3ac01205f2adcc3b95f91deabe916155408bc7137794b` |
| `hist32/chat_history_250913_163134_persona521.json` | 181,118 | `c0527d65a7f4c5688294f41482f3c9a64784077ad48ee09befa41dfedc0205e9` |
| `hist32/chat_history_250913_163134_persona626.json` | 180,361 | `45b270520bed0a87d66ec1a1f62a9466e9ef8ae552ae45b7c276e664a59116d0` |
| `hist32/chat_history_250913_163134_persona660.json` | 176,645 | `b93dfcd1704847b904f6b649bf455bbc58d749fc503529be602b67b86ec16784` |
| `hist32/chat_history_250913_163134_persona678.json` | 181,527 | `3cf8bf44d67415948933b91ad55ccc82d241ccd6d8565460ae002f8f564a0ce8` |
| `hist32/chat_history_250913_163134_persona737.json` | 181,347 | `007f5584269bf496a7313ec7dd4ad7d5f27e0887dec29d8bbb11d19b3ed6dba7` |
| `hist32/chat_history_250913_163134_persona740.json` | 182,440 | `edd68f856da7e784dbb164589777283f4efca1a865e0e4135d399f2da7fd7dd9` |

The CSV's hash and size match official LFS metadata for
[the benchmark CSV at the observed revision](https://huggingface.co/datasets/bowen-upenn/PersonaMem-v2/blob/ed956dea41521fc4499acbc63f966e0fd3c053ba/benchmark/text/benchmark.csv).
Each history's local size and Git blob SHA-1 match the official Git object
metadata at that revision; its SHA-256 above was independently computed from
local bytes. The [revision's file tree](https://huggingface.co/datasets/bowen-upenn/PersonaMem-v2/tree/ed956dea41521fc4499acbc63f966e0fd3c053ba/data/chat_history_32k)
identifies the corresponding history directory. No CSV/history text was
decoded or semantically inspected, and no corpus bytes were downloaded.
The original cache acquisition revision is not asserted. The licence tag
is direct source metadata rather than an independent rights determination.

## Input manifest and adapter

The CLI `--path` points to a JSON manifest, not a directory to scan:

```json
{
  "benchmark": {"path": "benchmark_text.csv", "sha256": "FULL_CSV_SHA256"},
  "histories": [
    {"persona_id": 42, "path": "histories/persona42.json", "sha256": "FULL_HISTORY_SHA256"}
  ]
}
```

The example persona is invented and its hash strings are placeholders.
`--sha256` pins the manifest itself. Paths are relative to the manifest's
directory; absolute paths, parent traversal, and symlink escapes are rejected.
Duplicate history persona IDs are rejected. Include at least two independent
personas to fit a grouped audit.

The CSV must provide `persona_id` and `related_conversation_snippet`. Histories
provide `chat_history` role/content turns. User messages are units; the
persona is both pool and CV group. Non-user snippets are ignored. Normalized
snippets at least 20 characters long mark a user message positive when either
the snippet contains the message or the message contains the snippet, with
the corresponding minimum-length constraint on the message.

This containment rule is a label heuristic, not exhaustive semantic evidence.
The original audit used eight cached personas; the manifest makes the chosen
subset explicit instead of implying coverage of the complete upstream
benchmark. Changing the supplied histories changes the population. Do not
infer broad benchmark performance from this limited label/subset protocol.

No CSV, history JSON, source snippet, or derived outcome matrix is bundled.
The manifest still needs its own full hash in addition to the child-file
pins. A newly selected history subset or different CSV bytes defines a
changed population and requires its own recorded input identity.

Development assistance: see [PROVENANCE](../../PROVENANCE.md).
