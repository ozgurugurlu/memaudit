# ForgetEval / Lethe — null baselines

| Field | Recorded value |
| --- | --- |
| Upstream | [deeplethe/lethe](https://github.com/deeplethe/lethe) |
| Historical checkout revision | `b6053b7bdacc78a91b9ea4bb25f32edad278c495` |
| Executed local files | `bench/forgeteval/generate.py`, `bench/forgeteval/adversarial_generated.py`, `bench/forgeteval/adversarial.py` |
| SHA-256 | Exactly these three files need full hashes in a separately pinned JSON manifest |
| Licence evidence | Local upstream `LICENSE`: MIT, copyright notice names the Lethe authors, 2026 |
| Metadata source | Recorded checkout revision; local Lethe `LICENSE`; current `memaudit/nulls.py` |

This is the input to `baselines nulls`, not an audit adapter. The public scorer
and case generator execute from the user's reviewed checkout. The package
ships none of those files or their case text. It verifies source bytes before
execution, uses temporary isolated modules, and avoids bytecode writes beside
the supplied source. A digest authenticates identity with a trusted source
record, not the safety of unknown Python code.

The CLI generates templates at 200 per family, seed 42, four distractors,
English, and takes adversarial cases from the pinned source's
`ADVERSARIAL_TESTS`. The historical target population is 1,000 template and
385 adversarial cases. Check actual case counts and native errors in each
report; the stored revision string does not replace content pins.

Four policies run independently per case. The default oracle-target recall is
CPU BM25, which differs from the original hybrid; the [protocol](../protocol.md)
states mutation and preservation semantics. Optional independent fact-label
files require their own pins. Missing, inconsistent, or uncertain adversarial
labels make preservation unknown and do not change the native public score.

No model or generative callback is required. Public passes alone do not show
that unrelated memory survived, nor do these controls rerun a published memory
system. See the [quickstart](../quickstart.md) for manifest and label shapes.

Development assistance: see [PROVENANCE](../../PROVENANCE.md).
