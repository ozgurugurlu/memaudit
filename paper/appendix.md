# Supplementary appendix

Özgür Uğurlu

This appendix gives the methods and aggregate results behind the four research questions. Table I1 maps descriptive study names to study codes. GLM abbreviates GLM-5.3-Flash.

<a id="appendix-a"></a>

## A. Evidence detectability and audit scope

The question-blind audit fits a histogram gradient-boosting classifier to 31 typography, format, length and lexical features (K.2), without questions, evidence identifiers or timestamps. Five-fold cross-validation keeps conversations, users or hosts together. Test rows whose unit text occurs in training are excluded; pools need both classes after exclusion. Detectability AUROC is the unweighted mean of within-pool AUROCs. The 95% intervals use 2,000 group-bootstrap resamples of saved predictions, conditional on the fitted models. BEAM uses contradiction-resolution and knowledge-update labels only.

**Table A1. Question-blind detectability in the audited populations.** Counts give pools before exclusion and those retaining both classes. Intervals are conditional 95% group-bootstrap intervals. BEAM 1M has 35 source conversations and 31 eligible ones.

| Setting | Evidence unit | Pools before exclusions → scored | Detectability AUROC (macro within-pool) [95% interval] |
|---|---|---:|---|
| STALE | Session | 400 → 400 | 1.000 [1.000, 1.000] |
| LoCoMo-Plus | Turn | 401 → 393 | .995 [.991, .997] |
| LongMemEval-S | Session | 470 → 379 | .783 [.763, .803] |
| BEAM 100K | User turn | 20 → 20 | .609 [.562, .656] |
| BEAM 500K | User turn | 35 → 35 | .604 [.572, .637] |
| BEAM 1M | User turn | 35 (31 eligible) → 31 | .622 [.586, .656] |
| HaluMem-Medium | Prefix session | 2,639 → 2,598 | .611 [.594, .627] |
| PersonaMem-v2 | User message | 8 → 8 | .597 [.554, .636] |
| LoCoMo | Session | 1,536 → 1,536 | .518 [.496, .537] |

For STALE, the character U+2019 identifies all 800 evidence sessions and none of the 19,200 distractor sessions. Duplicate exclusion removes 10,540 distractor rows; Table A1's AUROC describes the retained rows. LongMemEval-S scores .752 [.732, .769] on all 470 pools when duplicates are instead purged from training. BEAM 1M excludes four conversations with nonmonotonic or duplicated message identifiers. PersonaMem-v2 uses eight cached histories whose selection from 200 personas was not recorded.

<a id="appendix-b"></a>

## B. Reader interventions

Each ladder arm supplies the full history and question. Pointer notes name sessions and instruct the reader to prefer newer information when statements conflict. The artifact pointer identifies the evidence pair using U+2019 before typography is normalized out of the reader's history; retrieval pointers use the question. Thus the intervention supplies the cue's retrieval result, not the visible character itself.

### B.1. Original ladder (S10b)

The original test uses 100 STALE scenarios and 300 probes with GLM-5.3-Flash as reader and judge. Accuracy is 63.7% for plain reading, 83.0% with the generic instruction, 86.0% with hybrid-5, 98.0% with the artifact pointer and 100.0% with the answer-revealing oracle note. The artifact-minus-hybrid difference is +12.0 points [95% interval +8.0, +16.0], Holm p = $5.7 \times 10^{-10}$. The rule requires an estimate ≥5, lower bound >0 and adjusted McNemar p < .05. Generic instructions raise false-premise accuracy from 28.0% to 79.0%. The two pointers differ in session count as well as identity.

<a id="appendix-b2"></a>

### B.2. Three-reader ladder (S10c)

The same 100 scenarios were reused for Gemini 3.8 Flash, Gemini 3.5 Flash-Lite and a fresh GLM anchor. Nine arms include one-, two- and five-session notes, with 35, 46 and 79 tokens. The four primary artifact-minus-five-session contrasts are +14.0 and +7.0 points for Gemini 3.8 Flash, and +19.0 and +17.3 for Flash-Lite (hybrid, then dense). All are supported under Holm adjustment; all but Gemini 3.8 Flash versus dense-5 have adjusted lower bounds above +5. The estimator averages paired probe differences within scenarios, then scenarios equally. It uses 10,000 bootstrap resamples, 10,000 sign flips and 98.75% Bonferroni per-contrast intervals.

### B.3. Joint cue removal for a plain reader (S18)

S18 tests a plain Gemini 3.8 Flash reader at temperature 1.0 and default thinking on the same 100 scenarios. RAW retains original typography and full timestamps; DECUE normalizes typography and removes clock time while retaining dates. Both use user-only histories and identical normalized probes. DECUE equals the earlier plain prompt. Each probe has two draws per arm, scheduled ABBA with balanced starting arm. GPT-6.1 Sol at medium reasoning judges all 1,200 reads in 400 calls.

RAW minus DECUE is +1.33 points [−1.17, +3.83], sign-flip p = .362. A scenario bootstrap with 10,000 resamples supplies the 95% interval. Practical equality requires this interval inside [−5, +5]; the result meets that rule. This is interval inclusion, not TOST. All 300 probes are complete. Validation is inherited from S17 Part B. The two cues were removed together, in the non-official user-only layout.

### B.4. Four-vendor matched-pointer ladder (S19)

S19 adds two-session hybrid and dense pointers with the artifact pointer's same 46-token note, while retaining five-session comparators. The nine arms also include plain, generic, oracle and gold-pair-plus-three. GLM-5.3-Flash, Gemini 3.8 Flash, GPT-6.1 Sol and Muse Spark 1.3 (standard tier) run at temperature 1.0 and vendor-specific “high” reasoning. GPT-6.1 Sol at medium reasoning judges all readers, including its own family.

Byte-identical requests share one read: 2,375 distinct reads per reader for 2,700 nominal outcomes. Scenario blocks follow an 18-row Williams design. A reader needs ≥98% valid outcomes among the 2,400 non-gold-pair-plus-three units, with terminal reads scored incorrect. The primary family has 16 scenario-mean contrasts, 100,000 bootstrap resamples and 10,000 sign flips. Holm-adjusted p < .05, estimate ≥5 and lower bound >0 define support; the stronger result requires a lower bound >5. Intervals are 99.69% Bonferroni per-contrast intervals, targeting nominal 95% family coverage.

### B.5. Gemini successor and completed contrasts (S19b)

Three S19 readers completed; Gemini's stopped run was replaced only in the family display by its separately specified S19b run. That run uses fresh reads and its own passing validation, with the same split and arms. Table B1 joins its four decisions with the twelve unchanged S19 decisions. All completed contrasts have permutation p = 1/10,001 and Holm p = .0016. All eight matched two-session contrasts have adjusted lower bounds above +5. Both two-session retrieval-pointer arms score below the generic instruction for every completed reader.

**Table B1. Completed primary contrasts.** Artifact pointer minus comparator, percentage points, 100 scenarios and 300 probes each. Intervals are 99.69% Bonferroni per-contrast intervals. All contrasts meet the support rule in B.4; the eight two-session comparisons have adjusted lower bounds above +5.

| Reader | Comparator | Difference | Adjusted interval |
| --- | --- | ---: | --- |
| GLM-5.3-Flash | Hybrid-2 | +21.0 | [+13.3, +29.0] |
| GLM-5.3-Flash | Dense-2 | +19.0 | [+11.7, +26.7] |
| GLM-5.3-Flash | Hybrid-5 | +12.0 | [+5.3, +19.0] |
| GLM-5.3-Flash | Dense-5 | +11.0 | [+4.3, +18.3] |
| Gemini 3.8 Flash (S19b) | Hybrid-2 | +21.0 | [+14.0, +28.7] |
| Gemini 3.8 Flash (S19b) | Dense-2 | +18.0 | [+11.3, +25.3] |
| Gemini 3.8 Flash (S19b) | Hybrid-5 | +12.7 | [+6.7, +19.3] |
| Gemini 3.8 Flash (S19b) | Dense-5 | +9.0 | [+4.0, +14.7] |
| GPT-6.1 Sol | Hybrid-2 | +19.0 | [+11.7, +27.0] |
| GPT-6.1 Sol | Dense-2 | +16.7 | [+10.0, +24.0] |
| GPT-6.1 Sol | Hybrid-5 | +10.7 | [+5.3, +17.0] |
| GPT-6.1 Sol | Dense-5 | +10.3 | [+5.0, +16.7] |
| Muse Spark 1.3 | Hybrid-2 | +15.7 | [+9.0, +23.0] |
| Muse Spark 1.3 | Dense-2 | +13.0 | [+6.7, +20.3] |
| Muse Spark 1.3 | Hybrid-5 | +8.7 | [+4.0, +14.0] |
| Muse Spark 1.3 | Dense-5 | +7.3 | [+3.0, +12.7] |


GLM-5.3-Flash rejudging retains positive artifact-pointer contrasts against every comparator for the completed readers. Gemini's secondary estimates are +20.33, +15.33, +12.67 and +8.33 points against hybrid-2, dense-2, hybrid-5 and dense-5. These are descriptive and do not replace the binding decisions.

<a id="appendix-c"></a>

## C. Replicas and judge sensitivity

<a id="appendix-c1"></a>

### C.1. Replica study (S11)

S11 rebuilds a bespoke GLM-5.3-Flash fact store ten times from each conversation (K.7). Extraction temperature is .7; reading and judging use temperature 0. The test has four LoCoMo conversations and 692 questions, with 6,901 valid judged answers out of 6,920 planned. There are 680 questions with all ten replica labels. Oracle gain uses 671 questions complete for the extra-reader and raw-turn controls; the variance model uses 675, and the zero-temperature control 677.

For binary labels, oracle union gain over the pair mean is exactly half pairwise disagreement: $G_{\mathrm{mean}}=d/2$ in points when d is percent. Intervals resample questions and replicas conditional on the four conversations. The oracle selects on correctness labels and measures coverage across builds.

**Table C1. Replica results.** The variance model uses extra reader/judge passes on one designated store; the zero-temperature control has three stores.

| Quantity | Result |
|---|---|
| Pairwise label disagreement | 16.25% |
| Oracle gain over pair mean | 8.12 points [7.18, 9.07] |
| Oracle gain over better member | 7.41 points |
| Write-run accuracy SD, net of reader/judge noise | 1.04 points [0.65, 1.39] |
| Median fact-set Jaccard | .701 |
| Oracle gain at requested zero extraction temperature | 8.27 points |
| Judge-free containment gain | 4.54 points |

<a id="appendix-c2"></a>

<a id="appendix-c4"></a>

### C.2. Second judge on pointer answers (S17 Parts B and B2)

GPT-6.1 Sol passes validation on S10c's 87-item packet and rejudges 2,700 pointer outcomes. The four primary contrasts remain supported: +12.67 and +7.67 points for Gemini 3.8 Flash, +17.33 and +16.33 for Flash-Lite, against hybrid-5 and dense-5 respectively. It uses S10c's estimator and 98.75% intervals. Model family and temperature change together; this is a sensitivity analysis on the same answers.

<a id="appendix-d"></a>

## D. Counterfactual retrieval

S15a replaces distractors while fixing questions, evidence, session counts, positions and dates. ORIG-N is the normalized original history; CF-SOURCE uses evidence sessions from other scenarios on STALE and simulated sessions from other questions on LongMemEval-S. CF-STYLE rewrites distractors and falls back to original text for failed rewrites. The primary outcome is hybrid all-gold@5. A three-test Holm family uses the wider of a 10,000-draw cluster-bootstrap and cluster-mean t interval. Positive effects require adjusted lower bound >0 and estimate ≥5; the equivalence margin is ±3. Partial manipulations keep p = 1 slots and exploratory contrasts.

**Table D1. Retrieval replacement contrasts.** ORIG-N minus replacement, points. STALE uses 400 scenarios and 1,200 probes; LongMemEval-S uses 470 questions. The STALE source-swap contrast is positive; the style-rewrite and LongMemEval-S contrasts remain exploratory because their manipulation checks are partial.

| Replacement | Difference | Holm-level interval |
| --- | ---: | --- |
| STALE CF-SOURCE | +12.58 | [+9.64, +15.53] |
| STALE CF-STYLE | −0.25 | [−1.67, +1.17] |
| LongMemEval-S CF-SOURCE | +1.06 | [−0.37, +2.55] |


The manipulation check requires question-blind AUROC ≤ .60 and upper 95% bound ≤ .65. STALE CF-SOURCE passes at .513 [.492, .536]; CF-STYLE and LongMemEval-S CF-SOURCE fail at 1.000 [.999, 1.000] and .666 [.642, .691]. Replacement also increases hard negatives by +2.62 per probe [+2.24, +2.99], so the recall change mixes cue alteration with harder interference. A planned end-to-end stage (S15b) stopped under its budget-forecast rule before any end-to-end call. Its successor (S15c) ran RAG and mem0 end-to-end tests of source-swap distractors; both are invalid, because judge failures left a primary cell of each below the 98% completeness rule, so they give no effect estimate.

A deliberate style fusion adds twice the out-of-fold classifier probability to the hybrid-score percentile. It raises STALE ORIG-N all-gold@5 from 65.75% to 99.75% (+34.00 points), but lowers LongMemEval-S from 90.85% to 86.17% (−4.68).

<a id="appendix-e"></a>

## E. Wrong-question retrieval with fair nulls (S16)

### E.1. Protocol and estimands

S16 queries each target with ten eligible wrong questions in a fixed hash order from a different group, excluding evidence overlap and duplicate questions/evidence. Hybrid retrieval scores user-side turns and takes the maximum within each unit. QI is mean any-gold@5 over wrong questions. Uniform chance samples units equally; the turn-weighted null samples by nonempty turn count. A random-score null applies the same maximum pooling to independent turn scores. Twenty placebo gold sets match non-gold units on character-length decile, turn-count decile and position tercile.

CE = (QI − null)/(1 − null) is calculated per item before averaging. Family P uses the turn-weighted null; family S uses matched placebos. BEAM weights its three splits equally. Intervals take the wider of a 10,000-draw target/peer-group bootstrap and CR1 cluster-robust t interval, with separate Holm families. Positive effects require lower bound >0 and CE ≥.05; equivalence requires interval inclusion strictly within ±.03. A query-blind single-feature AUROC ≥.90 marks cue dominance. Placebo inference requires support on ≥80% of eligible items; failed support keeps p = 1 and no verdict.

**Table E1. Atlas populations and fair nulls.** Rates are hybrid any-gold@5 percentages. The inferential families include HaluMem prefix and BEAM; other rows are descriptive, exploratory or reference. Supported QI and placebo share exactly the support subset; below 80% support they do not describe the full row.

| Population / unit | N | QI | Turn-weighted null | Supported QI / placebo | Support |
| --- | ---: | ---: | ---: | --- | --- |
| HaluMem-Medium / prefix session | 1,200 | 15.82 | 17.99 | 9.96 / 10.58 | 250/1,200 |
| BEAM / round | 1,537 | 4.44 | 4.84 | 4.30 / 4.74 | 1,518/1,537 |
| MemOps / round | 403 | 27.97 | 6.32 | 27.51 / 18.98 | 390/403 |
| MemOps / session | 403 | 68.96 | 32.52 | 57.78 / 38.28 | 45/403 |
| HaluMem-Medium / full-history session | 1,200 | 7.71 | 8.11 | 7.51 / 6.91 | 453/1,200 |
| LoCoMo / session | 1,158 | 24.75 | 24.35 | 24.14 / 20.83 | 133/1,158 |
| LoCoMo / citation sensitivity | 1,158 | 25.02 | 24.35 | 24.89 / 21.65 | 133/1,158 |
| LoCoMo-Plus / turn | 401 | 2.99 | 1.67 | 2.99 / 1.15 | 401/401 |
| STALE / session | 1,200 | 41.40 | 14.98 | 41.18 / 16.62 | 756/1,200 |
| LongMemEval-S / session | 470 | 22.04 | 21.06 | 19.77 / 22.57 | 176/470 |
| LongMemEval-S / round | 467 | 5.61 | 3.84 | 5.61 / 5.11 | 467/467 |


### E.2. Family decisions and interpretation

MemOps-round fails admission at character AUROC .976, leaving two members per family. HaluMem is cue-dominated by position (AUROC .968) and its placebo support is only 20.8%, so it yields no interpretable primary conclusion. BEAM meets the ±.03 equivalence rule on both nulls: CE −.004 [−.014, .006] against turn-weighted chance and −.007 [−.020, .006] against placebo, with 1,518 of 1,537 items supported. These are Holm-level 97.5% intervals.

LongMemEval-S gives exploratory CE .011 [−.017, .041]; HaluMem's full-history sensitivity gives −.005 [−.015, .006]. STALE's matched-subset CE is .272 [.231, .314] on 756 of 1,200 items. These comparisons concern the specified retrieval stack and supported populations.

<a id="appendix-f"></a>

## F. Secondary grading

Three model adjudicators regrade a sample of 50 original-ladder and 50 replica answers: Claude Sonnet 5.5, Gemini 3.8 Flash and GPT-6.1 Sol. They receive the studies' correctness rubrics and blinded answers. Their labels provide agreement comparisons with the original judges; the binding study labels remain unchanged.

<a id="appendix-g"></a>

## G. Scoring with null policies

### G.1. Null policies (S1)

ForgetEval's public rule rewards targeted deletion without requiring preservation of unrelated memory. Wipe-plus-replacement passes 231/385 adversarial cases (60.0%) and 750/1,000 template cases (75.0%); storing nothing passes 96/385 (24.9%) and 350/1,000 (35.0%). A strict keep-set can be derived for 286/385 adversarial cases (74.3%), below the required 80% coverage. In a retrospective template check, enforcing construction-derived keep labels reduces the wipe policy's 750 passes to zero.

<a id="appendix-h"></a>

## H. Licenses and release boundaries

Public license declarations do not settle every upstream right. The recorded licenses are: MemOps, MIT; STALE, CC BY 4.0 (recorded in the study configuration, not verified); LoCoMo, CC BY-NC 4.0 (noncommercial research statistics only); HaluMem-Medium, CC BY-NC-ND 4.0 (statistics only); BEAM, CC BY-SA 4.0; LongMemEval, MIT for its repository; and LoCoMo-Plus, no license found (local exploratory statistics only). PersonaMem-v2's dataset card declares CC BY 4.0 and identifies descriptions from PersonaHub [@Ge2024PersonaHub] as a source. PersonaHub declares CC BY-NC-SA 4.0, with additional stated conditions on research use and on the generating models. The compatibility and precise scope of that upstream relationship remain unresolved here. The checked ForgetEval and MemoryAgentBench repositories declare MIT, but we do not certify the terms of the exact revisions used or the rights inherited from external material. LongMemEval's ShareGPT attribution points to FastChat code, whose repository states explicitly that the dataset is not released there, so FastChat's code license does not establish the license of the filler data. UltraChat [@Ding2023UltraChat] declares MIT for its data, alongside language on intended research and educational use. The archive redistributes no benchmark text or model responses. These are source disclosures, not legal clearance.

`memaudit` 0.1.0 is an Apache-2.0 offline CPU toolkit for unit auditing, wrong-question retrieval with fair nulls, ForgetEval null policies and numeric replica replay. It runs no language model. Users supply benchmark files; the distribution excludes benchmark text, raw responses and per-item outcomes. Documented checks reproduce selected STALE and LoCoMo-Plus measurements, rather than the full experiment suite. The code license does not relicense input datasets.

<a id="appendix-i"></a>

## I. Study map, pre-specification and validation

### I.1. Study map

**Table I1. Study map.** Codes identify the underlying experiments.

| Study | Code | Result/status | Appendix |
|---|---|---|---|
| Evidence audit | S10 | Descriptive detectability | A |
| Wrong-question atlas | S16 | BEAM equivalent; other rows scoped | E |
| Original / three-reader ladders | S10b / S10c | Supported pointer contrasts | B.1–B.2 |
| Four-vendor ladder / Gemini successor | S19 / S19b | Four readers supported | B.4–B.5 |
| Plain-reader cue removal | S18 | Practical equality, ±5 | B.3 |
| Counterfactual retrieval | S15a | STALE source-swap positive; other manipulations partial | D |
| End-to-end replacement / successor | S15b / S15c | Stopped by budget rule / invalid (completeness) | D |
| Pipeline cue removal | S20 | RAG equivalent ±3; mem0 inconclusive | L |
| mem0 extension | S21 | Equivalent ±5; pool descriptive | L.3 |
| Replica study | S11 | Item disagreement with stable totals | C.1 |
| Replica follow-ups | S11b / S11c | Stopped at development / unresolved (judge failed validation) | C |
| Second judge | S17 | Pointer contrasts supported; Part A unresolved (judge failed validation) | C.2 |
| LLM regrade / author check | Regrade | Sample agreement checks | F, J |
| Null policies | S1 | Public-score passes; strict coverage fails | G |

### I.2. Exposure and amendments

Later reader studies reuse the original STALE test split with its outcomes known. The mem0 extension was designed after the first subset's estimate was seen and uses the complementary scenarios, which had prior RAG outcomes.

<a id="appendix-i3"></a>

### I.3. Judge validation

The checks below require at least 60 determinate items, agreement ≥.80 and finite κ ≥.70 against model reference labels. All listed comparisons meet these criteria. The judges of the extractor follow-up (S11c) and of the second-judge study's Part A failed validation, so those results are unresolved. S11's original validation covered development only; S18 inherits S17 Part B. Table I2 gives the validation for the reader and pipeline comparisons.

**Table I2. Judge-validation summary.** Reference labels are from Claude Opus 5.5. Agreement is on each study's own packet.

| Study / judge | Items | Agreement | κ |
| --- | ---: | ---: | ---: |
| S10c / GLM | 87 | .943 | .846 |
| S17 B / GPT-6.1 Sol | 87 | .966 | .910 |
| S19 / GPT-6.1 Sol | 72 | .972 | .906 |
| S19b / GPT-6.1 Sol | 72 | .986 | .882 |
| S20 / GLM | 60 | .883 | .769 |
| S21 / GLM | 60 | .950 | .900 |


<a id="appendix-j"></a>

## J. The author's sanity check

As a sanity check, the author graded 50 selected original-ladder answers and 50 replica answers using the studies' rubrics, aware of the design but with condition, model and judge labels hidden. The GLM judge agreed on 46 of 50 ladder answers and 45 of 50 replica answers. Among 15 sampled replica pairs with disagreeing judge labels, ten were real correctness differences, two had both answers incorrect and three had both correct. The sample deliberately included disagreements, so these counts describe the selected answers rather than a population error rate.

<a id="appendix-k"></a>

## K. Shared implementation methods

<a id="appendix-k1"></a>

### K.1. Inputs and sampling

The common STALE split uses a fixed deterministic order of all 400 scenario identifiers: first 40 development, next 100 test, last 260 reserve. Test contains 50 scenarios of each type. Replica tests use LoCoMo categories 1–4 in four conversations. S20's nested and S21's complementary populations are given in L. Benchmark sources are the public releases cited in the main text; the audit's unit and exclusion rules are reported in A and E.

<a id="appendix-k2"></a>

### K.2. Detectability classifier

The HGB learner uses 200 iterations, learning rate .05, maximum depth 4, L2 regularization 1.0, early stopping off and random state 0. It uses log loss, at most 31 leaves, at least 20 rows per leaf, 255 bins and no class weights. GroupKFold is unshuffled; the group-bootstrap interval uses seed 0.

The 31 features comprise typography counts (apostrophes, quotes, dashes, ellipses, non-ASCII and emoji), format counts (Markdown, newlines, URLs and punctuation), length/role summaries and lexical rates (word/sentence length, type–token ratio, digits, uppercase, pronouns and contractions). Typography/format counts are per 1,000 characters; lexical features use normalized lowercase text. Position is excluded and tested separately. The released toolkit specifies the features. The counterfactual manipulation check instead groups by construction fold, purges training-side duplicates and uses random state 1515 with 10,000 pool-bootstrap draws.

<a id="appendix-k3"></a>

### K.3. Retrieval

BM25 uses $k_1=1.5$, $b=.75$ and negative-IDF replacement factor .25, indexed within each haystack. Its tokenizer lowercases Unicode letter/digit runs, removes 153 English stopwords and applies Snowball stemming. Dense retrieval uses normalized 384-dimensional bge-small-en-v1.5 embeddings with the retrieval query prefix and cosine similarity; it sees at most 512 tokens per turn. Hybrid scores sum $1/(60+r)$ across BM25 and dense ranks, averaging tied ranks. Session scores are their best user-turn scores; dates and headers are not indexed. Ladder ties prefer earlier sessions, whereas atlas ties use a fixed hash. Earlier ladder runs did not record the exact dense-encoder revision.

<a id="appendix-k4"></a>

### K.4. Query-blind priors and hard negatives

Eight query-blind priors rank by user characters, turn count, mean turn length or position, in either direction; the selected maximum is descriptive. In S15, a hard negative is a distractor whose best gte-base probe–turn similarity exceeds that of the less relevant gold session.

<a id="appendix-k5"></a>

### K.5. Rendering and notes

Ladders retain all 50 sessions but show only user turns with date-only headers. The typographic normalizer maps specified punctuation and spacing to ASCII, removes invisible characters, applies Unicode NFC and collapses repeated spaces/tabs. Letters, accents, digits and line breaks remain.

Generic notes remind the reader that facts change and questions may contain outdated premises. Pointer notes list session numbers and dates in chronological order and say that the later session reflects the current state if statements conflict. Oracle notes additionally supply the gold earlier/newer statements and explanation. S18 keeps probes identical between arms. S20/S21 use official session-and-role rendering, normalizing turns and probes only in DECUE.

<a id="appendix-k7"></a>

<a id="appendix-k6"></a>

### K.6. Judges and model settings

STALE judges use the official correctness rubric and gold old/new states. Replica judges use the Mem0-paper LoCoMo criterion. GLM-5.3-Flash generally runs at requested temperature 0, except replica extraction (.7) and the four-vendor ladder (1.0). GPT-6.1 Sol judging uses medium reasoning and fixed temperature 1.0. Gemini 3.8 Flash uses default thinking for S10c/S18 and high for S19/S19b. Reference grading uses only the blinded study packet and rubric.

<a id="appendix-k8"></a>

### K.7. Replica and mem0 adapters

The bespoke replica extractor processes one session and date at a time, returning JSON fact strings. Stores concatenate facts without deduplication, updating or pruning; each fact retains its date. More than 200 facts or a fact longer than 600 characters invalidates extraction. A store-specific BM25 index returns ten dated facts to the official LoCoMo retrieval prompt.

The mem0 experiments use library 2.2.1 with its decisions unchanged under the specified adapter. Each scenario/condition has a separate store, with one add per session's user turns and its stamp in text/metadata. Extraction uses mem0's own prompts, run date, top ten existing memories and last ten messages, without an added UPDATE/DELETE stage. A local Qdrant store holds normalized 384-dimensional bge-small vectors without instruction prefixes. Search returns up to ten memories at threshold .1, reranking off and entity/keyword boosts disabled. Reader inputs display the adapter's stamps. The user-only ingestion and adapter delimit the tested configuration.

<a id="appendix-l"></a>

## L. Pipeline cue removal (S20 and S21)

### L.1. Pipeline design and rules

S20 compares STALE's original typography and full timestamps with normalization and date-only stamps in the official layout. RAG uses 398 scenarios; mem0 uses a nested 150; no-history controls use 100. RAG indexes each condition's user turns and shows five retrieved sessions with both roles. The mem0 adapter is K.7's. GLM extracts, reads and judges at temperature 0, with three reads per probe/condition and identical gold judge fields across conditions.

The paired scenario-mean difference is RAW minus DECUE. The two-test Holm family uses the wider bootstrap/t interval at its current level and t-based TOST. Directional support requires the adjusted interval to exclude zero; equivalence requires adjusted TOST p ≤.05, at ±3 for RAG and ±5 for mem0. Validity requires ≥98% complete paired reads, passing label validation and accuracy at least ten points above no history.

### L.2. S20 primary results


RAG has 3,564/3,582 complete read pairs (99.50%), mem0 1,338/1,350 (99.11%). Their pooled accuracy on the control's 100 scenarios is 60.4% and 48.2%, versus 6.3% without history.

**Table L1. Pipeline cue-removal results.** RAW minus DECUE, percentage points. S20 uses Holm-level 97.5% intervals; S21 uses the wider unadjusted 95% bootstrap/t interval. RAG and the mem0 extension meet their stated equivalence bounds; the first mem0 subset is inconclusive and the combined result is descriptive.

| Test | Scenarios | Difference [interval] | TOST p (margin) |
| --- | ---: | --- | ---: |
| S20 RAG | 398 | +0.15 [−1.29, +1.60] | $1.2 \times 10^{-5}$ (±3; adjusted) |
| S20 mem0 | 150 | +4.30 [−0.21, +8.89] | .362 (±5; adjusted) |
| S21 mem0 | 248 | −1.46 [−4.33, +1.42] | .008 (±5) |
| Combined mem0 | 398 | +0.71 [−1.62, +3.06] | .027 (±3) |


<a id="appendix-l6"></a>

### L.3. mem0 extension (S21)

S21 tests the remaining 248 scenarios using the same adapter and intervention. It has one primary test at α=.05, t-based TOST at ±5 and the wider bootstrap/t interval. Of 2,232 read pairs, 2,226 are complete (99.73%). On 50 control scenarios, pooled mem0 accuracy is 45.33% versus 4.67% without history; validation passes.

The extension meets ±5 equivalence but not ±3 (TOST p=.146). For the pooled comparison, the t-based TOST gives p=.027, while the wider displayed interval extends to +3.06.

