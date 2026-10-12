# LongMemEval-S — `lme_s`

| Field | Recorded value |
| --- | --- |
| Dataset upstream | [xiaowu0162/longmemeval-cleaned](https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned) |
| Code upstream | [xiaowu0162/LongMemEval](https://github.com/xiaowu0162/LongMemEval) |
| Dataset revision | `98d7416c24c778c2fee6e6f3006e7a073259d48f` |
| File | `longmemeval_s_cleaned.json` |
| SHA-256 | `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442` |
| Recorded size | 277,383,467 bytes |
| Licence evidence | MIT in the local LongMemEval code checkout; source records also label the benchmark MIT |
| Metadata source | Recorded adapter constants and upstream LongMemEval `LICENSE` |

The adapter reads `question_id`, `answer_session_ids`, `haystack_session_ids`,
and `haystack_sessions`. Sessions are units. Each question's haystack is a
pool and CV group. IDs ending in `_abs` and records with no evidence sessions
are excluded. Evidence IDs must occur exactly once among the supplied session
IDs, and session-ID and session arrays must align.

Session role/content turns are consumed; question and answer text are not
classifier inputs. This setting is the S cleaned file, not the separate
oracle-only file or an arbitrary LongMemEval subset.

Question-level grouping does not remove cross-haystack duplicate sessions.
The audit reports both full scores and held-out duplicate filtering, with
positive losses and unevaluable pools counted. Historical full-pool
train-side-deduplication sensitivities are a different fitting procedure from
the package's full-population result.

No data or official prompts are bundled. Local source licence evidence is
recorded without claiming a fresh review of every upstream artifact's terms.

Development assistance: see [PROVENANCE](../../PROVENANCE.md).
