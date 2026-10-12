# Offline reproduction record

This record reports historical aggregate measurements on the identified local
candidate, with portable instructions for repeating them. No private input or
output artifact is distributed.

## Artifact identity and scope

The first installed wheel was `memaudit-0.1.0rc1-py3-none-any.whl`, SHA-256
`8303649e8e8e7dfddca84e0e910104d75c767a253cc01cec5024ac5d09a7129b`.
Its installed offline suite completed **86 tests in 31.53 seconds**. The
scientific measurements below were run through that installed package in a
separate working directory, using the local Python 3.12 environment on macOS.
These observations do not establish support for other platforms/interpreters.

These historical checks are distinct from current release-artifact verification.
Final wheel/sdist digests are recorded externally so the package does not embed
its own archive hashes. The source was subsequently extended; the current
release must pass its own source and installed-wheel test suites.

## STALE: detection and classifier replay

Input: `T1_T2_400_FULL.json`, **305,908,212 bytes**, SHA-256
`5f3ec375179e20e2e94469e018189188f34e2e7e5f21cbecbd99fcfa648c1876`.

| Completed check | Observed result |
| --- | --- |
| All-role U+2019 marker | 800/800 evidence sessions; 0/19,200 distractors |
| Marker selects the exact evidence set | 400/400 pools |
| Fresh raw/all classifier, grouped five-fold CV, seed 0 | Full-population macro AUROC **1.0**; duplicate-filtered macro AUROC **1.0** |
| Fitted populations | 20,000 full rows; 10,540 masked rows; 9,460 filtered rows; 400 filtered pools |
| Fit plus requested local operation timing | 36.030098125105724 seconds, one observed run; not a performance guarantee |
| Saved prediction report replay | Matched the fitted report |

Numeric prediction archives are not bundled. Pin any locally produced archive before replaying it.

Only `raw` / `all` was freshly fitted in this check. It does not establish
reproduction of every F1/F2 variant or all nine real adapter populations.
Marker counting alone would not have established the classifier result.
Full and filtered populations retain the different interpretations described
in [the protocol](protocol.md); neither establishes native-system exploitation.

To repeat after installing your chosen local wheel, run from a disposable
directory outside the source checkout, substituting your own input path:

```sh
memaudit audit marker --benchmark stale --path /path/to/T1_T2_400_FULL.json --sha256 5f3ec375179e20e2e94469e018189188f34e2e7e5f21cbecbd99fcfa648c1876 --output runs/stale-marker.json
memaudit audit run --benchmark stale --path /path/to/T1_T2_400_FULL.json --sha256 5f3ec375179e20e2e94469e018189188f34e2e7e5f21cbecbd99fcfa648c1876 --levels raw --variants all --folds 5 --seed 0 --n-boot 2000 --save runs/stale.npz --output runs/stale-fit.json
memaudit audit report --path runs/stale.npz --sha256 FULL_SHA256_OF_YOUR_ARCHIVE --n-boot 2000 --output runs/stale-replay.json
```

The [quickstart](quickstart.md) shows local hash computation and clean
installation. Input hashes should come from the source/protocol record;
hashing an arbitrary downloaded file does not establish its identity.

## ForgetEval: four deterministic policies

The completed run executed the reviewed Lethe sources associated with
revision `b6053b7bdacc78a91b9ea4bb25f32edad278c495`, using 200 templates per
family, seed 42, four distractors, and English. Source pins were:

```json
{
  "bench/forgeteval/generate.py": "39072bea33402e5cbf66a6c1101504a337ab9f5f3bd90d5402afc7727c4516a8",
  "bench/forgeteval/adversarial_generated.py": "aefa73df027a947a0535cb0c47d66d64010a124cdc1fad2c3985fa59bf5cb5a8",
  "bench/forgeteval/adversarial.py": "cfdf125aba5b90975634ce48bdf0f078397a72a1cc9dd1aa5bb59ab067c322d3"
}
```

| Policy | Template public pass | Adversarial public pass | Template collateral-aware pass |
| --- | ---: | ---: | ---: |
| `store-nothing` | 350/1,000 | 96/385 | 0/1,000 |
| `wipe-plus-replacement` | 750/1,000 | 231/385 | 0/1,000 |
| `keep-all` | 0/1,000 | 1/385 | 0/1,000 |
| `oracle-target`, CPU BM25 | 996/1,000 | 328/385 | 996/1,000 |

All policies reported zero native execution errors. This run supplied no
independent adversarial fact labels: preservation is **unknown for all 385
adversarial cases**, not a measured zero pass rate. Template preservation
uses the strict construction rule.

Wipe clears all facts on every mutation and stores the replacement on
supersede. Store-nothing never stores the replacement. The first two public
rows and template wipe's collateral-aware result reproduce the specified
historical controls. The oracle row is the observed **CPU BM25** result; it
does not reproduce historical hybrid OracleTarget retrieval. The Python API
can accept a caller-declared, pinned alternative ranker, whose method must be
reported separately; injection does not establish equivalence to the old
hybrid by itself. See [protocol](protocol.md) for that contract.

Save the three-pin JSON object locally, obtain its full digest, and run:

```sh
memaudit baselines nulls --lethe-root /path/to/reviewed-lethe --pins /path/to/lethe-pins.json --pins-sha256 FULL_SHA256_OF_PIN_MANIFEST --output runs/nulls.json
```

The command executes user-supplied Python sources after pin checks; source
review and input identity are both required. The data card and quickstart
describe optional private labels. No case source or label set is bundled.

## Private S11 numeric replay

The historical replay used private numeric correctness labels that are not distributed.

| First-wheel replay quantity | Observed value |
| --- | ---: |
| Planned questions | 692 |
| Oracle-complete questions | 671 |
| Variance-complete questions | 675 |
| Main replicas / unordered pairs | 10 / 45 |
| Correctness-label discordance | 0.16247723132969036 |
| Union minus pair mean, percentage points | 8.123861566484516 |
| Union minus better aggregate replica, percentage points | 7.411823149528067 |
| SD_W, percentage points | 1.0369499557588446 |
| Mean-gain combined normal 95% interval, percentage points | [7.183892315177978, 9.063830817791057] |
| Mean-gain question-bootstrap 95% interval, percentage points | [7.30572114588508, 8.908759728431859] |
| Question bootstrap SE, percentage points | 0.40229913566138703 |
| Delete-one-store jackknife SE, percentage points | 0.2610530363294834 |

The oracle mask requires `main`, `reseed`, and `raw`; variance requires
`main`, `reseed`, and `judge_only`. Oracle weighting is `complete_question`
with pooled better-replica choice. Variance uses planned-group weights.
Intervals condition on the four observed conversations and these masks;
they do not estimate a population of new conversations or causal components.
This reuses recorded correctness labels and does not rerun the memory pipeline,
reader, or judge. No fact-set Jaccard reproduction is claimed by this run.

A new numeric exporter must enforce the alignment and missingness contract in
[numeric outcomes](numeric-outcomes.md). These aggregate observations do not
independently validate every underlying store, label, or extraction stage.

With your own authorized numeric export:

```sh
memaudit replica replay --path /path/to/private-outcomes.json --sha256 FULL_SHA256_OF_OUTCOMES --n-boot 2000 --seed 0 --output runs/replica.json
```

The first-wheel CI values above are specific to its documented resampling.
Do not replace them with a historically rounded interval from a different
implementation and call that an exact replay. The later source snapshot's
changed replay code requires the final installed check recorded externally.

## Derived arithmetic, not system recreation

The portable `examples/aggregate_arithmetic.py` uses only reported aggregate
numeric inputs:

- `446 / 1986 * 100 = 22.4572%` to four decimals. It is a count/scorer
  arithmetic illustration; applying it as an overall score assumes the other
  1,540 items score zero. It is not actual non-category-5 scoring.
- `4.940584 / 7.668630 * 100 = 64.4259%` to four decimals, using the reported
  six-decimal gain-column and total-gain inputs consistently. Replacing the
  total with its rounded value 7.7 gives `64.1634%` and is a different
  rounding calculation.

The gain share is a descriptive composition of reported columns. Neither
calculation recreates a published memory system or attributes gain causally.
The example's execution in the final installed environment belongs in the
final build report; its existence alone is not that execution evidence.

## Input metadata and retained evidence

The supplemental metadata-only pass pinned one HaluMem file, the PersonaMem
CSV and eight original cached histories, and all three raw BEAM Parquet
files: **13 files, 182,909,427 bytes**. Five local SHA-256/size pairs match
official LFS metadata; eight history size/Git-blob SHA-1 pairs match official
Git metadata, with separate local SHA-256 values recorded. No corpus was
decoded or downloaded for that pass. The cards distinguish the revision
observed during metadata checking from an unknown original acquisition
revision. This verifies input identity metadata, not nine-adapter numerical
parity or semantic correctness.

Input metadata and aggregate reproduction summaries are provided here; private logs,
prediction archives, outcome matrices, and raw data are excluded. See
[PROVENANCE](../PROVENANCE.md) for development assistance and component origins.
