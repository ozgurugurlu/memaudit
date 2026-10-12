# Measurement protocols

This page describes the implemented CPU v0.1 behavior. Record input hashes,
package/dependency versions, grouping, masks, estimands, and all changed
protocol choices with each analysis. Historical numbers are comparison targets
only until reproduced by the installed artifact on the exact intended inputs.

## Audit

### Units, pools, and groups

`Unit` contains only `uid`, `turns`, `user_role`, `rel_pos`, and `n_units`.
`turns` is a sequence of `(role, text)` pairs. `AuditRow(pool, unit, label,
group, rel_pos=None, n_units=None)` refers to a unit index and a binary evidence
label. `AuditSet(name, units, rows, meta={})` validates unique unit IDs, valid
indices, and one CV group per shared unit and per ranking pool. A unit cannot
appear twice in one pool. A pool is the candidate set for one ranking task;
the CV group is the larger independent unit held together across folds.

The 31 style features consume only one unit's turns and role assignment.
Questions, labels, IDs, timestamps, neighboring units, and position do not
enter this feature vector. Position is a separate two-feature probe. This is
a structural input restriction, not a semantic guarantee about supplied text,
label construction, near duplicates, templates, or source generators.

| Feature group | Names |
| --- | --- |
| Typography (7) | `curly_apos`, `curly_quote`, `dash_typo`, `ellipsis`, `nonascii`, `emoji`, `straight_apos` |
| Format (10) | `md_bold`, `md_header`, `md_bullet`, `code_fence`, `newline`, `url`, `paren`, `colon`, `question`, `exclaim` |
| Length (6) | `log_chars`, `n_turns`, `user_mean_chars`, `other_mean_chars`, `max_turn_chars`, `user_char_share` |
| Lexical style (8) | `mean_word_len`, `ttr`, `digit_rate`, `upper_rate`, `first_person`, `second_person`, `contraction`, `mean_sent_len` |

Most punctuation counts are per 1,000 characters. Lexical token features use
the typography-normalized text; character-case features retain case. The
position probe uses relative position and `log1p(n_units)` only. Row-level
position overrides unit-level position, which matters when a shared LoCoMo
host turn occupies different positions after cue insertion.

`raw` leaves text unchanged. `F1` maps typographic punctuation and spaces,
applies NFC, and collapses horizontal-space runs. `F2` adds removal of the
implemented Markdown markers. These are deterministic text transformations,
not semantic editing or guarantees of meaning preservation.

The default raw variants are `all`, `only_typography`, `only_format`,
`only_length`, `only_lexical`, the corresponding four `drop_*` variants, and
`position_only`. F1 and F2 each run `all` and the four `only_*` variants.
`--variants` overrides this set; `position_only` is skipped outside `raw`.

### Fitting and exact duplicates

The classifier is `HistGradientBoostingClassifier`: 200 iterations, learning
rate 0.05, maximum depth 4, L2 regularization 1, no early stopping, seed 0 by
default. `GroupKFold` uses five folds by default, reduced to the number of
groups if fewer than five are supplied; at least two groups are required.
A single-class training fold returns its constant label mean. Each fit limits
threadpool use to one thread. Package and scikit-learn versions can affect
reproduction and must be recorded.

Exact duplicates are SHA-256 hashes of the canonical JSON role/text sequence
before F1/F2 normalization. IDs, question text, and position are omitted.
A held-out row is flagged when its hash occurs in any training row.

- `full_population` scores every row with the fitted out-of-fold classifier,
  including rows with exact training duplicates.
- `duplicate_filtered` masks those held-out duplicate rows after fitting.
  It uses the same fits. It does not remove duplicate training rows or create a
  full-pool estimate trained without overlapping text.

Report rows, positives, pools, groups, masked counts, pools with no remaining
scores, and pools left with a single class. A filtered population can change
both the retrieval task and its random baseline. Do not relabel a historical
train-side-deduplicated full-pool sensitivity as this implementation's
`full_population` result.

### Metrics and uncertainty

Primary AUROC is the unweighted mean of within-pool AUROCs for evaluable
two-class pools. Pooled AUROC is reported separately. Hit@1/5/10 means finding
**at least one** labeled unit, not all evidence or a correct answer. Tied
scores use the analytic expectation under uniformly random order within a
tie. The historical audit used one seeded tie ordering, so exact hit rates
can differ even with identical scores.

For a pool of N candidates with E positives, the exact random hit@k is
`1 - choose(N-E, min(k,N)) / choose(N, min(k,N))`, with impossible all-negative
draws assigned probability zero. Reported random rates average over the same
evaluable pools as the corresponding hit metric.

Intervals resample CV groups with replacement (2,000 draws, seed 0 by
default), retaining each selected group's pools. They condition on fitted
predictions and exclude training variability. Fewer than two contributing
groups yield unavailable interval endpoints. A [1,1] conditional interval is
not a guarantee about a new corpus or generator.

The F1/F2 summary labels a residual macro AUROC at most 0.55 `removed`; otherwise
it is `reduced` if excess above 0.5 is at most half the raw excess, and
`persists` otherwise. Missing prerequisites yield `undefined`. These labels
refer to the registered detectability threshold, not the disappearance of
every possible construction cue. Feature-group ablations are not univariate
feature-importance estimates.

When raw features are available, `univariate_raw` separately reports each
feature's mean within-pool AUROC over the full two-class pools. These are
direction-sensitive diagnostics: a value below 0.5 indicates the inverse
direction and is not automatically reflected above 0.5. They are not held-out
feature selection or a causal importance analysis.

Saved `memaudit-audit/1` NPZ archives contain numeric pool/group codes, labels,
folds, duplicate flags, scores, raw feature arrays when the raw level is included, and
restricted JSON metadata. They contain no
unit text or serialized model. Replay disables pickle. Input digests and byte
counts survive; arbitrary free-text metadata does not. These local arrays still
encode per-row labels and predictions: absence of conversation text is not
permission to publish them.

## Wrong-question retrieval (QI)

`memaudit qi run` ranks each sampled
item's units with ten wrong questions from other groups and compares any-gold@k with uniform, turn-weighted
(Plackett-Luce) and matched-placebo nulls on the kappa scale. The registered rules, the item-file contract and the
report fields are in [REPRODUCE-PAPER.md](REPRODUCE-PAPER.md). Interpretation limits: a row is one retriever stack and
one unit definition; a query-blind feature with AUROC >= .90 makes the turn-weighted kappa uninterpretable (only the
placebo estimand remains, and only with at least 80% placebo support); a strong query-blind prior shows that gold
differs on a feature, not that a retriever's wrong-question hits come from it; nothing here says a memory system uses
a cue or that a published score is inflated.

## Null policies and preservation

Every case gets a fresh `NullPolicy`. The native public scorer runs first;
preservation queries inspect that same final memory state.

| Policy | Initial writes | Supersede | Release/purge | Recall |
| --- | --- | --- | --- | --- |
| `store-nothing` | Ignore | Ignore replacement | No-op | Empty |
| `wipe-plus-replacement` | Append | Clear everything, then append new statement | Clear everything, on every mutation | Insertion order |
| `keep-all` | Append | Append replacement, retaining old facts | No-op | Insertion order |
| `oracle-target` | Append | Delete whole facts matching any forbidden phrase, then append replacement | Delete facts matching forbidden phrases | CPU BM25 |

The oracle receives `must_not_contain` from the case. It is an oracle control,
not a deployable selector. Deletion is case-insensitive whole-phrase matching
with word boundaries. Its retrieval uses lowercase word tokens, BM25
`k1=1.5`, `b=0.75`, and stable insertion-order ties. This intentionally differs
from the historical hybrid retrieval adapter; its recall results are not an
exact replay of that adapter.

For a locally reviewed alternative retrieval method, the Python API accepts
`NullPolicy("oracle-target", recall_ranker=fn, recall_provenance=...)`, or
`evaluate_lethe(..., oracle_ranker=fn, oracle_ranker_provenance=...)`. The
callable receives `(tuple(active_fact_texts), query)` and returns a full
permutation of integer fact indices. Duplicate, missing, out-of-range,
boolean, and noninteger indices are rejected; the callback cannot substitute
fabricated recall text. Provenance must contain exactly a short `method`
identifier and lowercase 64-hex `sha256`. These are caller-declared source
metadata, not a verified model identity. A source-compatible cached hybrid
ranker can be provided this way without adding a downloader to memaudit;
the caller remains responsible for the injected function's behavior. The CLI
continues to use CPU BM25 and exposes no ranker plugin-loading flag.

Strict preservation first classifies each setup fact: `TARGET` contains a
forbidden whole phrase, `REQUIRED` contains a required substring, `COMPOUND`
contains both, `SUBSTR` has only a forbidden substring collision, and
`UNFLAGGED` meets none. Compound cases are not derivable.

For templates, every non-TARGET setup fact must survive under the construction
rule. For adversarial cases, at least two caller-supplied complete label maps
must agree on KEEP/REMOVE for every fact, with TARGET=REMOVE and REQUIRED=KEEP.
Missing labels, unsure values, disagreement, or role conflict make preservation
unknown. Label independence is an external protocol requirement; the file
schema cannot establish it.

A required fact is retained when its normalized text is contained in at least
one recall result at k=10. `collateral_aware` requires both the public pass and
zero lost required facts. Aggregate numerators use only evaluable cases;
`n_preservation_unknown` is separate and must not be treated as zero failures.

The reviewed historical targets for the pinned Lethe population are wipe
231/385 adversarial and 750/1000 template public passes; store-nothing 96/385
and 350/1000; template wipe collateral-aware 0/1000. They are historical targets,
not fresh RC results in this document. Strict historical keep-set derivability
was 1286/1385; relaxed sensitivities 1323–1325/1385 used different rules. This
implementation applies the strict rule and does not silently substitute a
relaxed fraction or overturn a frozen failed threshold verdict.

## Replica outcomes

The [outcome schema](numeric-outcomes.md) defines aligned question rows, replicate
columns, planned counts, and metric-specific masks. For a pair of binary-label
replicas, compute correctness union `max(A,B)` and compare it separately with:

1. the mean of the two replica accuracies (`union_minus_mean_pp`), and
2. the better aggregate accuracy (`union_minus_better_pp`).

Results average over all unordered replicate pairs. The default better
replica is chosen over the pooled weighted population; `better_scope=per_group`
chooses it separately in each group. State this scope with the result.
Mean-reference gain in percentage points equals 50 times the fraction of
discordant binary labels, without an independence assumption. Do not compare
that gain with an external better-system denominator.

Oracle weights may be proportional to complete questions, proportional to
planned questions per group, or equal across observed groups. The reported
group weights are part of the estimand. Planned weighting retains the planned
population's group proportions while using each group's complete cases; it
does not impute missing outcomes.

The gain interval resamples questions within observed groups and adds a
delete-one-store jackknife component in quadrature for its normal interval.
The store component is unavailable with fewer than three replicas. It does
not sample a new population of conversations. Best-of-k averages correctness
unions over all k-subsets analytically and subtracts mean single-replica
accuracy; it assumes an oracle with correctness labels.

Variance uses planned-group weights and a separately aligned complete-case
mask. Main replicas estimate variance across aggregate scores. Reader/judge
reseeds and judge-only redraws supply nested components; signed differences
are retained while `SD_write_pp` uses the square root of the nonnegative
write component. Conditional independence and exchangeability assumptions
limit interpretation. Negative components and alternative aggregate reseed
estimates remain visible; these are not causal percentages.

The placebo report simulates independent Gaussian arm scores with the
observed aggregate SD, compares the best of 20 candidate arms with one
baseline by default, and reports both strict and inclusive exceedance
probabilities over 10,000 seeded draws. It is a model-based simulation, not
an observed optimization campaign.

Fact Jaccard uses separately supplied private fact text, session-constrained
greedy one-to-one matching, and the registered lowercase, stop-worded English
Rust Snowball tokenizer at default threshold 0.5. Matching ties are resolved
by fact indices. At threshold 1, normalized exact-string multiset intersection
replaces token matching. Empty-empty comparisons score 1. Report the tokenizer
description and stopword hash. This measures lexical matching, not semantic
fact identity; alternate tokenizers do not reproduce a historical Jaccard by
name alone.

Decision thresholds are optional and explicit. Omitting `thresholds` emits no
rule decision; including `{}` deliberately selects the historical S11 rule
constants. Each rule evaluates independently: an available stop takes
precedence over another rule's unknown input. The historical 8.9-point
reference is a frozen decision constant, not a matched-population comparison
denominator. Do not revise frozen rules after seeing results.

Development assistance: see [PROVENANCE](../PROVENANCE.md).
