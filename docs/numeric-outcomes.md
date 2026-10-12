# Numeric replica outcomes: `memaudit-replica/1`

`memaudit replica replay` consumes a user-supplied JSON file with a full SHA-256
pin. The file contains identifiers and binary correctness outcomes, not
questions, facts, prompts, answers, or judge explanations. The CLI does not
produce these labels or verify their truth.

## Top-level fields

| Field | Required | Contract |
| --- | --- | --- |
| `schema` | Yes | Exactly `memaudit-replica/1` |
| `questions` | Yes | Nonempty list of aligned question rows |
| `planned_counts` | Yes | Positive integer counts keyed by exactly the groups appearing in the rows; each at least the number of supplied rows in that group |
| `oracle_required` | No | Required complete blocks for the oracle mask; default `["main"]` |
| `variance_required` | No | Required complete blocks for the variance mask; omission disables variance and placebo reports |
| `weighting` | No | `complete_question` (default), `planned_group`, or `equal_group` |
| `better_scope` | No | `pooled` (default) or `per_group` |
| `thresholds` | No | Explicit rule configuration; omitted means no rules; `{}` deliberately selects historical constants |
| `jaccard_tau` | No | Fact-matching threshold in [0,1], default 0.5; used with the separately pinned fact-set input |

Other fields are rejected. Keep reader/judge/model IDs, extraction method,
generation settings, dates, and provenance in a separate protocol record;
free-form attribution metadata is not a supported extra field in this schema.
The source JSON hash ties that record to the replayed population.

## Question rows and replicate alignment

Each row has a unique string `id`, a string `group`, and zero or more of the
outcome arrays `main`, `reseed`, `judge_only`, and `raw`. Use short non-content
identifiers. Each supplied array has at least one entry; entries are 0, 1, or
JSON `null` (booleans are also accepted as binary values). A block's width must
be constant wherever that block appears, across all groups.

| Block | Meaning in a registered replica study | Minimum when used for statistics |
| --- | --- | --- |
| `main` | One score per independently constructed memory-store replica | Two draws |
| `reseed` | Reader and judge redraws on the declared fixed store | Two draws |
| `judge_only` | Judge redraws on the declared fixed answer | Two draws; requires `reseed` for variance decomposition |
| `raw` | Optional reference scores used to restrict completeness | One draw is sufficient for a mask-only reference |

Column k of `main` must identify the same store replica for every question and
group. Do not reorder successful draws independently per question. Reseed and
judge-only blocks may have widths different from main and each other; their
columns must still have the declared experimental meaning. The format checks
shape and binary values, not the independence or nesting of those experiments.

Every required-block list must include `main` and may name only the four known
blocks. A row is complete for a metric when every required block is present
and has no null. A planned group with no complete rows is rejected instead of
silently dropping that group. All-null or missing outcomes stay unavailable;
do not turn missing stores, responses, or scores into zeros.

The report separately records planned questions, input rows, complete rows,
excluded input rows, omitted planned rows, complete counts by group, and a
positional `row_mask` for each metric. This lets a private exporter inspect the
exact population without putting question text in the report.

For the historical S11 protocol, the oracle mask requires
`["main", "reseed", "raw"]`, while variance requires
`["main", "reseed", "judge_only"]`. A historical test reproduction targets
692 planned questions, 671 oracle-complete questions, and 675 variance-complete
questions. These are historical reference counts, not evidence that an arbitrary
export satisfies the protocol.

## Weighting and output fields

`complete_question` weights each group by its complete-row count;
`planned_group` uses planned counts; `equal_group` assigns equal group weights.
Variance always uses planned-group weights independently of the oracle
weighting choice. Missingness remains conditional under every choice.

The main report schema is `memaudit-replica-report/1`:

- `oracle` names `union_minus_mean_pp`, `union_minus_better_pp`, correctness
  discordance, the identity residual, pair count, weights, and better scope.
- `oracle_ci` reports a within-group question bootstrap, delete-one-store
  jackknife SE when available, and their combined normal interval.
- `best_of_k_oracle_gain_pp` reports gains over the mean single-replica
  accuracy for each k from 2 through the number of main replicas.
- `variance` and `variance_mask` are present only when requested.
- `placebo` is a Gaussian simulation using observed aggregate SD, with
  inclusive and strict tail probabilities; it is not a real search run.
- `jaccard` is present only when separate fact sets are supplied.
- `rules` is present only when a threshold object is supplied.
- `input` and optional `facts_input` report verified digests and byte sizes.

Percentage-point fields end in `_pp`, squared-point variances in `_pp2`;
discordance, Jaccard, and probabilities are fractions. Do not compare a
fraction directly with a percentage-point threshold. JSON serialization turns
undefined non-finite statistics into `null`.

## Explicit thresholds

`memaudit.rules.Thresholds` validates rule parameters and
`memaudit.rules.evaluate(card, thresholds)` evaluates the rules independently.
Within replay, supplying `"thresholds": {}` is an explicit request for the
following historical S11 constants, not a universal scientific default:

| Parameter | Historical value |
| --- | ---: |
| `ref_gap_pts` | 8.9 |
| `kill_sd_pts` | 0.7 |
| `kill_jaccard` | 0.9 |
| `kill_self_frac` | 0.2 |
| `kill_placebo_pts` | 2.0 |
| `kill_placebo_frac` | 0.1 |
| `claim_sd_pts` | 2.0 |
| `claim_jaccard` | 0.6 |
| `claim_self_frac` | 0.5 |
| `claim_placebo_frac` | 0.5 |
| `n_placebo` | 20 |

Fields provided in the object override the corresponding defaults; spell out
all fields in a new preregistration to make that choice unambiguous. Rule 1
stops when SD_W is at most `kill_sd_pts` and Jaccard at least `kill_jaccard`.
Rule 2 stops when mean-reference gain is below `kill_self_frac * ref_gap_pts`
(with the implementation's 1e-9 tolerance). Rule 4 stops when the strict
placebo exceedance probability is below `kill_placebo_frac`. Support decisions
also use the explicit claim thresholds. There is no implemented rule 3.

An evaluable stop yields `STOP_KILL_RULE` even if another rule is unknown.
If no stop fires but a required metric is unavailable, the gate is
`NOT_EVALUABLE`; otherwise it is `PASS`. Inputs and thresholds accompany the
decision. PASS means these rules did not stop this supplied card; it is not
proof of causality, external validity, or successful reproduction.

The frozen reference of 8.9 points is retained as a decision constant.
Historical comparisons require matching the mean/better convention, population,
mask, weighting, reader, and judge separately. It must not be silently used as
a same-convention external denominator.

## Optional private fact sets

Pass `--facts-path FILE --facts-sha256 FULL_SHA256` together. The separate JSON
maps every outcome group to a list of store mappings. The list length equals
the main replica count; each store maps session IDs to lists of fact strings.
For example, all text below is invented:

```json
{
  "group-a": [
    {"session-1": ["A synthetic red object."]},
    {"session-1": ["A synthetic blue object."]}
  ]
}
```

Each compared pair must have exactly the same session keys. Empty sessions
should therefore be represented by empty lists, not omitted keys. Pairwise
results are aggregated with equal group-pair weight, independent of oracle
weights. At tau<1, ties in greedy token matching break by fact indices. At
tau=1, the metric is normalized exact-string multiset matching. Empty-empty
store comparisons score 1.

The default tokenizer uses Unicode word tokens excluding underscores,
lowercasing, a fixed English stopword set, and Rust Snowball English stemming.
Its description, stopword count, and stopword hash are reported. These facts
are user-owned private inputs and are never included in the report; they do
not belong in a distributable reproduction fixture.

## Export checklist

Before replaying a real study, verify the following in the local exporter:

1. Freeze question IDs, group membership, planned counts, replica order, and
   required block lists from the registered protocol.
2. Check every expected store and draw, including failed or missing extraction,
   reader, and judge stages. Preserve missingness as null or missing blocks.
3. Align all blocks by ID. Reject duplicates or contradictory labels rather
   than taking the last encountered record.
4. Record pipeline, reader, judge, label metric, and any manual adjudication
   outside the numeric schema; preserve the numeric input's hash there.
5. Inspect both complete-case masks and their denominators before interpreting
   any metric. Reproduce a historical number only with its own mask and weights.
6. Keep outcome matrices and fact sets outside the package distribution.
   Numeric-only does not itself establish release permission.

Development assistance: see [PROVENANCE](../PROVENANCE.md).

Rule cards accept numeric domain values: nonnegative SD, oracle mean gain
from 0 to 50 percentage points, and Jaccard/probabilities from 0 to 1.
`None` and NaN mean unknown; booleans, arbitrary text, infinity, and values
outside these domains are rejected. Only a 1e-12 boundary tolerance is
clipped to the bound to accommodate floating point summation.
