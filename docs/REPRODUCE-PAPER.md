# Paper reproductions, the QI item-file contract and the verification record


The two one-command reproductions and their expected numbers are in the [README](../README.md#reproductions-with-public-benchmark-data).
This page documents the wrong-question (QI) method as implemented, the item-file contract for other benchmarks, the
report fields, and the local verification run that checked the expected numbers. No benchmark text, converted data or
per-item output is included here or in the package.

## Wrong-question retrieval as implemented (`memaudit qi run`)

The rules and constants follow the S16 registration, so that a public item file reproduces its atlas row.

1. **Units and text.** A haystack is an ordered list of units (a turn, round or session, as the adapter defines). A unit's
   scoring text is its user-side turns after F1 typography normalisation; turns empty after normalisation are dropped and
   a unit without a scoring turn is empty. `n` counts non-empty units; `e` counts non-empty gold units.
2. **Sample.** Items with `e = 0` are excluded; every remaining item is a possible wrong-question donor. Items with
   `n <= 2k` (10) are not sampled. The sample is ordered by `sha256("S16-sel|" + bench + "|" + item_id)`; optional
   `--per-group-cap` and `--total-cap` follow that order (LoCoMo-Plus uses no cap).
3. **Wrong questions.** Candidates are ordered by `sha256("S16-qi|" + bench + "|" + target + "|" + peer)`. A candidate is
   skipped if it shares the target's group, its normalised question, a gold unit whose content hash occurs in the target
   haystack, or a gold unit with 5-word-shingle Jaccard >= 0.8 to any target unit. The first ten remaining are used; an
   item with fewer is starved and excluded from every estimate (counted in `peers.starved_items`).
4. **Retrieval.** BM25 Okapi (k1 1.5, b 0.75, idf floor 0.25 x mean idf; rank-bm25 0.2.2 arithmetic, tested bit-for-bit)
   over turns with the registered tokenizer; or the optional hybrid: per-turn reciprocal-rank fusion (c = 60,
   average-rank ties) of BM25 and bge-small-en-v1.5 cosine (query instruction prefix, no document prefix). Unit score =
   maximum turn score; empty units rank last; ties are broken by `sha256("S16-tie|" + item + "|" + query_id + "|" + uid)`.
5. **Outcome.** Any gold unit in the top k (k = 1, 5, 10 reported; k = 5 primary).
6. **Nulls, per item.** Uniform: `1 - C(n-e, k)/C(n, k)`. Turn-weighted: Plackett-Luce top-k with unit weight = number of
   scoring turns (exact recursion when its state bound is at most 200,000, else 100,000 seeded Monte-Carlo draws).
   Matched placebo: 20 sets of non-gold units drawn, for each gold unit, from its (user-character decile, turn-count
   decile, position tercile) cell, without repeats inside a set; an item has support only if every cell holds at least as
   many non-gold as gold units. The placebo value describes a row only when at least 80% of its items have support.
7. **Effect.** Per pair, `kappa = (hit - null)/(1 - null)` (the placebo pair uses that ranking's placebo hit rate); item
   value = mean over its wrong questions; estimate = mean over items. `points` is `100 x (hit - null)`. Interval: the wider
   of a two-way (target group x peer group) multinomial cluster bootstrap (10,000 draws, seed from
   `sha256("S16-boot|" + bench)`) and a CR1 cluster t interval of the item mean. `--stratify-split` gives equal weight to
   the strata named by the item `split` field (the S16 BEAM rule).
8. **Query-blind checks.** K3: for characters, turns, position, non-ASCII count and typographic-marker count, the item-mean
   within-haystack AUROC of gold versus non-gold units; `max(A, 1 - A) >= 0.90` labels the row cue-dominated, and its
   turn-weighted kappa is then reported but not interpretable. Priors: eight rankings by one query-blind feature (both
   directions); the best is a selected maximum and descriptive only.

`inside_margin_0_03_at_95` states whether the 95% interval lies strictly inside ±0.03. It is descriptive: the S16
confirmatory tiers used Holm-adjusted levels over a registered family, which this single-row command does not apply.

## Item-file contract (`--items FILE --items-sha256 HASH`)

JSON lines, optionally gzip-compressed (`.gz`), one benchmark per file: all pool records, then all item records.

```json
{"type": "pool", "pool_id": "p1", "group": "g1", "bench": "mybench",
 "units": [{"uid": "p1/u0", "slot": 0, "text_sha256": "<sha256 of the canonical JSON list of all turn texts>",
            "n_chars_user": 18, "n_turns_user_nonempty": 1,
            "turn_texts_user": ["invented user turn"], "turn_texts_all": ["invented user turn", "invented reply"]}]}
{"type": "item", "item_id": "i1", "pool_id": "p1", "group": "g1", "bench": "mybench", "qtype": "any", "split": "all",
 "question": "invented question?", "gold_uids": ["p1/u0"], "background": null, "flags": {}}
```

Keys must be exactly these; slots run 0..n-1; gold uids must belong to the pool; the bench name enters every salt.
`memaudit.qi.make_unit_record(uid, slot, [(role, text), ...], user_roles)` builds a unit record. This is the S16
interface contract, so an item file written by an S16 converter can be passed as is; memaudit itself packages only the
LoCoMo-Plus converter (`--benchmark locomo_plus`). An item file contains benchmark text: keep it local, never commit it.

## Report fields

`rates[k]`: `QI`, `uniform`, `turn_weighted`, `placebo` and `QI_on_support` (placebo is compared with QI on the same
supported items), `n_support`, `true_question_hit`, `priors`. `effects["<null>/<scale>"]` for null in uniform,
turn_weighted, placebo and scale in kappa, points: `estimate`, `ci95`, `ci95_t`, `ci95_bootstrap`, `n_items`,
`n_clusters`, `excluded`. Also `sample`, `peers`, `placebo_support`, `k3`, `best_query_blind_prior`, `interpretation`,
`inputs` (hash and size of each input) and `settings`. Before writing, `run_qi` refuses any report string that equals or
contains a question or unit text of 20 or more characters.

## Local verification record (2026-10-04)

Environment: macOS arm64, CPython 3.12.12, numpy 2.5.3, scipy 1.18.1, scikit-learn 1.9.1, py-rust-stemmers 0.1.8,
FastEmbed 0.8.1 with onnxruntime 1.30.0, one thread. Inputs were the three pinned files in the README table (hashes checked by the commands). Outputs were
aggregate JSON only and are not packaged.

| Check | Result | Reference |
| --- | --- | --- |
| STALE audit, raw/all, duplicate-filtered | 1.000 [1.000, 1.000]; 400 pools; 9,460 scored and 10,540 masked rows; 34 s | Figure 1; recomputed 1.000000 [1.000000, 1.000000] |
| LoCoMo-Plus audit, raw/all, duplicate-filtered | 0.994658 [0.991055, 0.997264]; 393 of 401 pools; 26 s | Figure 1; recomputed 0.994664 [0.991068, 0.997268] |
| LoCoMo-Plus QI, BM25 | QI / uniform / turn-weighted / placebo / QI on support / true-question hit at k = 1, 5, 10: zero difference from the stored S16 aggregates; 10 s | S16 atlas, BM25 rows |
| LoCoMo-Plus QI, hybrid | all rates at k = 1, 5, 10 and the uniform, turn-weighted and placebo kappa and points estimates and 95% endpoints: zero difference from the stored S16 aggregates; 60 s | S16 atlas hybrid rows and Section 5.1 |
| Peers, K3, priors | 0 starved, 421 same-host skips; K3 maximum 0.692 (characters), not cue-dominated; best prior `pos_desc` 8.23% | S16 Sections 3 and 4 |

The audit fits a classifier again, so its fourth decimal can move with the scikit-learn version; the QI path fits nothing.
The hybrid matched exactly here even though memaudit encodes only the texts of this one row, whereas the S16 run shared
a vector cache across benchmarks; a different ONNX runtime or CPU may still move individual rankings, hence the stated
tolerance. The comparison read only the stored aggregate files of the earlier studies; no per-item output was copied.
