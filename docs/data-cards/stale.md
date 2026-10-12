# STALE — `stale`

| Field | Recorded value |
| --- | --- |
| Upstream | [STALEproj/STALE](https://huggingface.co/datasets/STALEproj/STALE) |
| Dataset revision | `617c51dc200b5ab09970834144c7e51c77959af0` |
| File | `T1_T2_400_FULL.json` |
| SHA-256 | `5f3ec375179e20e2e94469e018189188f34e2e7e5f21cbecbd99fcfa648c1876` |
| Size | Not recorded in the consulted constants; measured from the pinned input at runtime |
| Data licence | CC BY 4.0 as recorded in the study configuration; not independently verified here |
| Separate code licence | MIT in the local STALE code checkout; this is not itself evidence of dataset terms |
| Metadata source | Recorded evaluation input revision and checksum; local STALE code `LICENSE` |

Each record supplies `uid`, `haystack_session`, and
`relevant_session_index`. Each session contains role/content turns. A session
is one unit, all sessions of a scenario form a ranking pool, and scenarios
are CV groups. Evidence indices must be nonempty and within the session range.
The question and reader-probe fields are not consumed by the style features.

The historical full corpus has 400 scenarios. Its reported descriptive marker
target is U+2019 in 800/800 evidence sessions and 0/19,200 distractors, selecting
exactly the gold sessions in 400/400 scenarios when all roles are considered.
This is a historical target, not a fresh package validation claim. The marker
command's default scans all roles; `--user-only` is a different measurement.

Exact duplicate filtering removed 10,540 negative rows in the reviewed
historical audit. It changes candidate-pool sizes and random hit expectations.
Report the runtime full and filtered populations explicitly, and do not infer
the behavior of a native memory system from marker detection.

No corpus, official prompt, or trained detector is bundled. The recorded
revision remains descriptive metadata; the actual command requires the local
file's expected hash. Other bytes define a different input.

Development assistance: see [PROVENANCE](../../PROVENANCE.md).
