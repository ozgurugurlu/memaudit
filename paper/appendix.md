# Supplementary appendix

Özgür Uğurlu

Companion to [the main paper](paper.md). This appendix is a reduced version of the research archive. It keeps the methods, aggregate results, exposure history, and inferential limits, and it omits cost logs, private source registers, internal working notes, and the full audit memos. Study labels (S1–S20) and appendix section numbers are kept for cross-reference; Table I.1 maps every study to its main-text and appendix sections.

**Roadmap.** Each appendix supports the following parts of the main text.

- Appendix A: question-blind detectability (§3.2 and §4.1).
- Appendix B: the reader ladders of §5.1 (B.1, B.2, B.4, and B.5) and the de-cue test of §6.2 (B.3).
- Appendix C: the replica study (§7.1), its follow-ups (§7.2), and the second-judge pointer contrasts of §5.1 (C.4).
- Appendix D: the constructed style ranker of §5.2 (D.3), the source-swap retrieval tests of §6.1 (D.1–D.3), and the end-to-end tests of §6.3 (D.4–D.6).
- Appendix E: the wrong-question atlas (§3.3 and §4.2).
- Appendices F and J: the LLM regrade and the one-grader human check (§7.3).
- Appendix G: the null-memory policies under ForgetEval’s scoring, and the failed forgetting-closure study (§7.4).
- Appendix H: post hoc checks, provenance, and release boundaries (§9 and the release statement).
- Appendix I: the study map, the judge-validation gates, and the computational checks (§3.1, §3.5, and §7.3).
- Appendix K: implementation details, that is, data, retrieval, prompts, and models (§3.2–§3.5).
- Appendix L: the pipeline de-cue study of §6.4 (S20).

**The author.** The paper has a single author. In this appendix, “the author” always means that person, who was also the only human grader (Appendix J). All other answer grades come from LLM judges, adjudicators, and regraders, each named by its model.

**Study records.** None of the records below is public, and this appendix states in words whatever it uses from them. A study’s preregistration (PREREG in the archive) fixes its question, populations, estimands, and decision rules before the test, and a hash lock fixes it together with the study’s code. A protocol amendment (registered as an annex) adds operational definitions to the preregistration or changes its rules; an amendment locked together with the preregistration is part of the registration, and one made after the lock is disclosed with its timing and scope. A study’s report gives its registered results, deviations, and exposure. An audit memo (AUDIT-n in the archive) records a separate computational check of a study: a recomputation of its registered numbers from the saved outputs, with the scope of the check.

**Models and labels.** Models carry the main text’s display names; Appendix K.7 lists their API identifiers and settings. In tables, GLM is short for GLM-5.3-Flash; other short labels are defined in the table notes.

**Abbreviations.**

- AUROC: area under the receiver operating characteristic curve, reported as detectability AUROC (macro within-pool) or single-feature AUROC (within-haystack).
- BM25: the Okapi BM25 lexical ranking function (Robertson and Zaragoza 2009).
- CE: chance-corrected excess, the item mean of (wrong-question hit rate − null rate)/(1 − null rate) (§3.3).
- CP: Clopper–Pearson, the exact binomial interval or bound.
- CR/KU: contradiction resolution and knowledge update, the two BEAM probing categories whose evidence labels the audit uses.
- CR1: a cluster-robust standard error with the small-sample factor $m/(m-1)$ for $m$ clusters.
- HGB: histogram gradient boosting, the classifier of the detectability audit and of the manipulation checks (Appendix K.2).
- HT: Horvitz–Thompson, the inverse-inclusion-probability estimator.
- LLM: large language model.
- MDE: minimum detectable effect.
- QI: query-independence rate, the mean any-gold@5 hit of one item over its ten wrong questions (Appendix E.1).
- RAG: retrieval-augmented generation.
- RRF: reciprocal rank fusion (Cormack et al. 2009).
- SESOI: smallest effect size of interest.
- SR, PR, IPA: STALE’s three probe types, state resolution, premise resistance (the false-premise probe), and implicit policy adaptation (Chao et al. 2026).
- T1, T2: STALE’s two scenario types, co-referential (Type I) and propagated (Type II).
- TOST: two one-sided tests, an equivalence test.

## A. Evidence detectability and the scope of the audit

### A.1. Protocol and populations

Appendix A supports the main text’s audit design (§3.2), detectability results (§4.1), and limitations (§9). The classifier asks whether an evidence unit can be distinguished from its distractors without the current question. It does not answer the question, run a memory system, or estimate how much a published system’s score is inflated.

The classifier is a histogram gradient-boosting (HGB) classifier on 31 counts and rates that describe a unit’s typography, formatting, length, and lexical surface form; it never sees the question, evidence ids, or timestamps. It was evaluated with five-fold cross-validation whose groups are the pools or the conversations, users, or hosts that contain them, so that no group appears on both sides of a split. Appendix K.2 specifies the learner (library, version, and settings), the groups and seed of each setting, and the definition of every feature; Appendix K.1 gives the benchmark revisions and populations. The score, detectability AUROC (macro within-pool), is the unweighted mean of the AUROCs of the scored pools. It is computed after the test-duplicate exclusion of §3.2, and a pool is scored only if it keeps both classes. The 95% intervals come from 2,000 group-bootstrap resamples of the saved out-of-fold predictions, so they omit the uncertainty of refitting the model.

The open-source toolkit memaudit 0.1.0 implements this classifier (`memaudit audit run`). Its documentation reports that the command regenerates the STALE and LoCoMo-Plus rows of Table A1, and so of Figure 1, to four decimals from the pinned public files. The other seven rows were not checked against the toolkit, so memaudit is not a reproduction package for Table A1 or Figure 1.

**Table A1. Question-blind detectability in the audited populations.** The first count is the number of pools before exclusions, and the second the number of scored pools, which keep both classes after the test-duplicate exclusion. For BEAM 1M, the first count is the 35 conversations of the 1M split, of which the preregistration lists 31 (see the text below). Intervals are 95% group-bootstrap intervals, conditional on the saved predictions. These settings use different units and populations and do not form a common leaderboard.

| Setting | Evidence unit | Pools before exclusions → scored | Detectability AUROC (macro within-pool) \[95% interval\] |
|----|----|---:|----|
| STALE | Session | 400 → 400 | 1.000 \[1.000, 1.000\] |
| LoCoMo-Plus | Turn | 401 → 393 | .995 \[.991, .997\] |
| LongMemEval-S | Session | 470 → 379 | .783 \[.763, .803\] |
| BEAM 100K | User turn; contradiction-resolution and knowledge-update evidence labels only | 20 → 20 | .609 \[.562, .656\] |
| BEAM 500K | User turn; contradiction-resolution and knowledge-update evidence labels only | 35 → 35 | .604 \[.572, .637\] |
| BEAM 1M | User turn; contradiction-resolution and knowledge-update evidence labels only | 35 (31 registered) → 31 | .622 \[.586, .656\] |
| HaluMem-Medium | Prefix session | 2,639 → 2,598 | .611 \[.594, .627\] |
| PersonaMem-v2 | User message | 8 → 8 | .597 \[.554, .636\] |
| LoCoMo | Session | 1,536 → 1,536 | .518 \[.496, .537\] |

The exclusion matters to interpretation. In STALE, it removes 10,540 of the 19,200 distractor rows and keeps all 800 evidence rows, so the mean candidate pool shrinks from 50 to 23.65 units; the perfect detectability AUROC describes the retained rows. For LongMemEval-S, an alternative that keeps every test row and removes duplicates from the training side instead scores all 470 pools at .752 \[.732, .769\]; the .783 value describes the smaller scored population and does not show an improvement on an unchanged population. For BEAM 1M, the 1M split holds 35 conversations, but the adapter drops the four whose message ids are duplicated or not strictly increasing, because their evidence labels cannot be matched to messages unambiguously. These are the same four nonmonotonic conversations that the wrong-question atlas excludes from its primary BEAM row (Appendix E.2). The preregistration lists the remaining 31, which is also the count in Figure 1, so 35 is not the registered population.

### A.2. From construction cues to a measurement claim

The strongest evidence is the contrast across settings, together with the downstream reader and retrieval controls; we do not claim that every benchmark admits the same shortcut. The initial reader branch of S10, the evidence-audit study, failed its judge gate and supplies no confirmed reader effect, so Appendix B reports only the later reader studies. Appendix D separates a retrieval intervention from a native-memory outcome. Appendix E compares wrong-question hits with three nulls: uniform (combinatorial) chance, turn-weighted chance, and matched placebo gold.

Construction artifacts, hypothesis-only prediction, partial-input baselines, shortcut learning, adversarial filtering, and contrast sets have an established literature (Gururangan et al. 2018; Poliak et al. 2018; Kaushik and Lipton 2018; Geirhos et al. 2020; Zellers et al. 2018; Le Bras et al. 2020; Gardner et al. 2020); §2 cites the work on evaluator agreement and evaluation variance. Our claim applies these measurement principles to memory benchmarks, with explicit retrieval, null-policy, and replica controls. It is not the invention of artifact auditing, nor evidence that every artifact changes an end-to-end system. Huang (2026) shows that retrieval with uninformative queries can exploit distractor markers and latent type structure, and separates selection gains from unequal history access. Huang’s setting is a small streaming environment, unlike the long-history benchmarks audited here; we apply related diagnostic principles to the annotated evidence units of existing long-history benchmarks, with benchmark-specific nulls and downstream tests. Training-initialization variance and same-model decoding replicas are different sources of variability, so evidence on the former says nothing about the magnitude of the latter.

## B. Reader studies

Every arm of a STALE reader ladder supplies the full history and the question. Retrieval pointers are built from the question; the artifact pointer is built from the character U+2019, which identifies STALE’s gold pair. Every pointer note also carries a staleness instruction, so the pointers confound where to look with what to do. The arms are interventions, not cue discovery by an unmodified memory system. The bge-small-en-v1.5 citation (Xiao et al. 2024) identifies the encoder’s model family; the checkpoint revision that ran was not recorded. Appendix K.3 gives the retrieval settings, and Appendix K.5 the reader-side texts.

B.1 reports the original ladder (S10b), B.2 the three-reader ladder (S10c), and B.3 the de-cue test (S18). B.4 reports the four-vendor ladder (S19), which adds two-session retrieval pointers with the artifact pointer’s note and four readers from four vendors. B.5 reports S19’s separately registered Gemini 3.8 Flash successor run (S19b), which completes S19’s test families.

### B.1. S10b: the original ladder and its exposure

**Protocol card.** S10b tested 100 STALE scenarios, three probes each, with GLM-5.3-Flash as reader and binding judge. The binding judge was changed after development validation: S10’s binding judge, Gemini 3.5 Flash-Lite, had failed its gate, and a rule fixed after S10’s development agreement values were known, but before any S10b test output, chose GLM-5.3-Flash. Gemini 3.5 Flash-Lite served as secondary judge and also read 26 scenarios (78 probes) in four arms (plain, generic instruction, hybrid-5, and artifact pointer). This nonrandom subset consists of the first 26 of the 30 planned scenarios, because a budget stop ended the second-reader run there. The LoCoMo-Plus part added 161 items from four host conversations. The 100 STALE test scenarios are positions 41 to 140 when STALE’s 400 scenarios are sorted by a salted SHA-256 hash of their ids; Appendix K.1 gives the rule and the other samples. All STALE inputs had been exposed to the artifact analysis, and ten test scenarios also had reader outcomes from an earlier pilot, so excluding those ten does not create a pristine split.

**Outcome.** The artifact pointer’s accuracy exceeds hybrid-5’s by +12.0 points (95% scenario-cluster interval \[+8.0, +16.0\]; Holm-adjusted $p = 5.7 \times 10^{-10}$). This meets the registered rule: an estimate of at least +5 points, a lower bound above 0, and a Holm-adjusted exact McNemar p below .05. The effect differs by scenario type: +4.7 \[+1.3, +8.7\] in co-referential and +19.3 \[+12.7, +26.0\] in propagated scenarios. Excluding the ten scenarios with pilot outcomes gives +13.3 \[+9.3, +17.8\] on the other 90. The study’s report calls the retrieval pointers typography-free. A post hoc token check, which was not repeated, supports this only for the per-turn retrieval path, not for the session-joined path that built the pointers, and it does not isolate any effect of typography (Appendix H.1). Table B1.1 defines the arms and gives their accuracies.

**Table B1.1. S10b STALE arms and their accuracy under the binding GLM-5.3-Flash judge.** Each arm has 300 probes. Every arm except unsanitized plain normalizes the history’s typography. The style pointer named the same two sessions as the artifact pointer in every test scenario, so the two arms sent identical prompts (300 of 300) and the style row repeats the artifact-pointer condition; 83 of its 300 answers were recorded cache hits rather than new draws. Registered arm ids: `plain`, `plain_raw`, `generic`, `placebo`, `wrong`, `ptr_hyb5`, `ptr_regex`, `ptr_style`, and `oracle`.

| Arm | Definition | Accuracy (%) |
|----|----|---:|
| Plain | No note | 63.7 |
| Unsanitized plain | No note; the history keeps STALE’s original typography | 63.3 |
| Generic instruction | Three-sentence instruction aligned with the rubric | 83.0 |
| Placebo instruction | Length-matched instruction about style, without a premise cue | 59.7 |
| Wrong-partner pointer | Names the newer gold session and one unrelated earlier session, never the older gold session | 94.7 |
| Hybrid-5 | Names the top five sessions of the hybrid retriever, which receives the question | 86.0 |
| Artifact pointer | Names the sessions that contain U+2019, which are the gold pair | 98.0 |
| Style pointer | Names the two sessions ranked highest by a gradient-boosted classifier on the 31 question-blind style features, trained on 198 reserve scenarios | 97.3 |
| Oracle note | Labels the earlier statement outdated and carries the gold text | 100.0 |

The generic instruction’s gain comes mainly from false-premise probes, whose accuracy rises from 28.0% under plain to 79.0%. The placebo instruction is not inert: it lowers false-premise accuracy to 22.0%. The artifact pointer names two sessions and hybrid-5 names five, so their contrast also differs in count and note length (§3.4). S10b’s dense retriever had no reader arm; on the test split, it named both gold sessions in 74% of probes, against 61% for hybrid-5.

On LoCoMo-Plus, the registered hint raised full-context accuracy by +6.2 points over the official prompt (four-host bootstrap interval \[+1.2, +11.2\]; t interval over the four hosts \[−3.2, +15.7\]). Its predicted gain of at least +15 points was unreachable, because the official prompt already scored 85.1%. Under the binding judge, a context of only the cue turns (LoCoMo-Plus’s evidence turns) scores +52.8 points above a context of the five turns that the hybrid retriever returns. The hybrid-context accuracy, however, depends heavily on the judge: 47.2% under the binding GLM-5.3-Flash judge and 17.4% under the secondary Gemini 3.5 Flash-Lite judge. Neither LoCoMo-Plus comparison is independent of the judge, and neither compares published systems.

**One-grader human check.** After the LLM regrade (Appendix I.2), the author, who knows the design, graded a disagreement-enriched sample of 50 STALE answers from this ladder, with arm and verdict concealed. The binding judge agreed on 46 (raw agreement 92.0%, κ .83; design-weighted agreement 99.1%, κ .97; precision unresolved, Appendix J.2). Its design-weighted pass rate was within 1 point of the author’s in every arm group (78.3% against 77.9% overall). These point estimates show no leniency signal, but they cannot bound arm-group leniency to a few points: the post hoc, model-based judge-minus-human sensitivity ranges are −14.5 to +18.4 points in the plain group (the plain and placebo-instruction arms) and −4.95 to +23.8 points in the pointer group (the wrong-partner pointer, hybrid-5, and artifact-pointer arms; Appendix J.3). Nor can they bound a judge-error difference between the two arms of the +12.0-point contrast, with five and nine sampled answers. The exposure and confounds above remain.

<a id="appendix-b2"></a>

### B.2. S10c: conditional robustness on the reused test split

**Protocol card.** S10c reused S10b’s 100 test scenarios (300 probes) after the direction of S10b’s artifact-minus-hybrid effect was known. The readers were Gemini 3.8 Flash, Gemini 3.5 Flash-Lite, and a fresh GLM-5.3-Flash anchor draw; the two Gemini readers share a vendor. Each of the nine arms had one draw per cell, in a fixed order within each scenario (the artifact pointer always followed hybrid-5), under implicit provider caching. Besides plain, the generic instruction, hybrid-5, dense-5 (the top five sessions of the dense encoder alone), the artifact pointer, and the oracle note, three pointer controls use the shared pointer note. NEW and OLD denote the newer and the older gold session. NEW only names NEW alone. OLD + wrong later names OLD and the non-gold session after OLD that lies closest to NEW. All wrong names that same later non-gold session and the earlier non-gold session closest to OLD, so it names no gold session. Pointer identity and note length remain confounded: notes naming one, two, and five sessions contain 35, 46, and 79 tokens.

$D$ averages the paired probe differences within each scenario and then weights scenarios equally. Each of the four primary contrasts used 10,000 scenario-bootstrap resamples, a sign-flip permutation test with 10,000 draws over scenario means, and Holm adjustment across the four. The Bonferroni per-contrast intervals, at 98.75% (= 1 − .05/4), target nominal 95% coverage for the family, not exact finite-sample coverage. The tier “supported” requires a Holm-adjusted p below .05, a per-contrast lower bound above 0, and $D \geq 5$ points; “supported, at least +5” also requires that lower bound to exceed +5. The registered rule then checks “reversed”, “practically equal” (the per-contrast interval inside the open band (−5, +5)), and “inconclusive”; no primary contrast reached them. Table B2.1 gives the primary contrasts and Table B2.2 every reader’s accuracy by arm.

**Table B2.1. S10c primary contrasts: artifact pointer minus each five-session retrieval pointer, binding GLM-5.3-Flash judge.** Each contrast has 100 scenarios (300 probes) and no missing cells. Permutation p-values are counts out of 10,001. The tier names shorten the registered labels “supported: at least +5 asserted” and “supported (estimate \>= +5, adjusted lower bound \> 0)”. For Gemini 3.8 Flash against dense-5, the per-contrast lower bound of +3.0 does not establish a gain of at least +5 points.

| Reader; comparator | $D$ (points) | 95% interval | 98.75% Bonferroni per-contrast interval | Permutation p | Holm p | Scenarios up / down / tie | Probes passed by artifact only / by comparator only | Registered tier |
|----|---:|----|----|----|----|----|----|----|
| Gemini 3.8 Flash; hybrid-5 | +14.0 | \[+10.0, +18.3\] | \[+9.0, +19.7\] | 1/10,001 | 4/10,001 | 33 / 0 / 67 | 44 / 2 | supported, at least +5 |
| Gemini 3.8 Flash; dense-5 | +7.0 | \[+3.7, +10.3\] | \[+3.0, +11.5\] | 1/10,001 | 4/10,001 | 20 / 2 / 78 | 23 / 2 | supported |
| Gemini 3.5 Flash-Lite; hybrid-5 | +19.0 | \[+13.7, +24.3\] | \[+12.3, +25.7\] | 1/10,001 | 4/10,001 | 52 / 7 / 41 | 65 / 8 | supported, at least +5 |
| Gemini 3.5 Flash-Lite; dense-5 | +17.3 | \[+12.7, +22.0\] | \[+11.3, +23.7\] | 1/10,001 | 4/10,001 | 47 / 3 / 50 | 59 / 7 | supported, at least +5 |

**Table B2.2. S10c LLM-judged accuracy (%) by reader and arm, binding GLM-5.3-Flash judge.** Each cell has 300 probes, except GLM-5.3-Flash’s OLD + wrong later (297). The GLM-5.3-Flash row is a fresh descriptive anchor draw, not S10b’s run. On nine probes, the GLM-5.3-Flash dense-5 answer is a copy of its hybrid-5 answer, which the shared API proxy returned for an identical request (Appendix H.1). The artifact pointer has the highest accuracy among the non-oracle arms for every reader; similar accuracies do not establish that two readers are equivalent.

| Reader | Plain | Generic instruction | Hybrid-5 | Dense-5 | Artifact pointer | NEW only | OLD + wrong later | All wrong | Oracle note |
|----|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GLM-5.3-Flash | 66.0 | 82.0 | 84.3 | 87.7 | 98.0 | 94.0 | 81.5 | 74.3 | 100.0 |
| Gemini 3.8 Flash | 66.0 | 93.0 | 83.0 | 90.0 | 97.0 | 92.0 | 80.7 | 74.0 | 100.0 |
| Gemini 3.5 Flash-Lite | 27.7 | 43.7 | 39.0 | 40.7 | 58.0 | 49.0 | 46.3 | 35.0 | 98.0 |

In an exposure control without history (30 test scenarios, one probe each), accuracy falls to 3.3–6.7%. This is consistent with answers that depend on the supplied history, but it does not show that pretraining contamination is absent.

All eight secondary contrasts pass Holm adjustment at .05; they carry no effect-size tiers. For Gemini 3.8 Flash, the generic instruction recovers 79% of the oracle-minus-plain gap (95% interval \[69, 90\]; descriptive), more than either retrieval pointer recovers; both pointers are therefore weak comparators for that reader. The exposure sensitivities keep the sign of every primary effect on the 90 scenarios without pilot outcomes and on the 74 that S10b’s Gemini 3.5 Flash-Lite reader had not read; neither subset is pristine. One descriptive GLM-5.3-Flash contrast is incomplete: OLD + wrong later minus All wrong, because OLD + wrong later has 297 of 300 probes. Its complete-case estimate on 99 scenarios is +7.07 points. Its bounds for the three missing probes, on the planned denominator of 300 probes, are \[+6.33, +7.33\] points; they are not a confidence interval. The registered escalation rule was not triggered: it would have added a further reader only if Gemini 3.8 Flash’s premium over hybrid-5 had fallen below +5 points while GLM-5.3-Flash’s did not, or had taken the opposite sign.

**Validation and recomputation.** The binding judge agreed with the adjudicator labels on 82 of 87 items from 59 scenarios (agreement .943, κ .846), which passes the registered gate. The adjudicator was a fresh Claude Opus 5.5 instance (`claude-opus-5-5`) that saw no arm, reader, item id, or verdict. All three items that the judge passed and the adjudicator failed are Gemini 3.5 Flash-Lite answers, and none of the five disagreements involves the artifact pointer. Because the packet is clustered and LLM-labeled, it is not human validation. The secondary Gemini 3.5 Flash-Lite judge agreed with the adjudicator on 78 of 87 items (κ .722); this is descriptive. According to the recorded chronology, a post-lock repair of the analysis code (a recorded amendment; Appendix I.2) was signed before the first test call. Separately, the test reads paused for about 13 hours while the host machine slept. The five reads interrupted by the pause (one Gemini 3.8 Flash and four GLM-5.3-Flash reads) timed out and were re-sent under the registered recovery rule; no read was lost, and none was repeated outside that rule. Two separate recomputations from the saved outputs reproduced the inference and validation arithmetic. They could not verify from the files the adjudicator’s isolation, the semantic prompt audit, the access chronology, or the billing (Appendix I.4).

### B.3. S18: jointly removing STALE’s typographic and clock-time cues

S18, the de-cue test of §6.2, is the one reader study in this appendix that removes cues instead of adding a pointer. It asks a narrow question about one reader on the reused S10c test split, so it measures conditional robustness, not fresh confirmation. Its registered tier is “practically equal”. Card B3 gives the protocol.

#### B.3.1. Protocol card

**Card B3. S18 protocol card.** The registered definitions. Appendix K.5 gives the reader-side texts and the typographic normalizer, and Appendix K.7 the model settings.

| Protocol element | Registered definition |
|----|----|
| Question | Is a plain full-history reader’s accuracy different when STALE’s typographic and clock-time cues are removed together, with everything else fixed? |
| Registration and freeze | A preregistration plus a binding protocol amendment (registered as an annex, which takes precedence where the two differ), hash-locked together on 2026-10-04 before any S18 model call. Known before registration: S10c’s tables (Gemini 3.8 Flash plain 66.0% under the GLM-5.3-Flash judge), S10b’s GLM-5.3-Flash reader at 63.7% (plain) against 63.3% (unsanitized plain), and the results of S17 Parts B and B2 (Appendix C.4) |
| Population | The 100 scenarios of the S10c test split (identical to S10b’s), with three probes each: state resolution (SR), premise resistance (PR, the false-premise probe), and implicit policy adaptation (IPA); 300 probes |
| Reader | Gemini 3.8 Flash with no thinking level sent, that is, at the model’s default level, which S19’s registration records as “medium” (Appendix B.4.7); temperature 1.0; up to 16,384 output tokens; concurrency 1. These are S10c’s Gemini 3.8 Flash settings. Plain prompt: the official STALE reader system prompt, the history, then the probe; no note |
| Layout (both arms) | The user-only rendering of S10 and S10c: all 50 sessions in order, user turns only, one header per session. The 29,661 assistant turns of the 100 test scenarios are removed. This is not the official STALE evaluation layout |
| RAW | The user-only layout with STALE’s own typography and the full `YYYY-MM-DD HH:MM` stamp in every session header |
| DECUE | The registered de-cue of RAW: delete the clock time from each session header, then apply S10’s typographic normalizer. DECUE equals S10c’s plain prompt byte for byte (300 of 300 by SHA-256) |
| What DECUE keeps | The probe (S10c’s normalized text, identical in both arms), the system prompt, session order and numbering, dates, roles, line structure, and every word. Length, turn-count, content, and markdown cues remain in both arms |
| Draws and order | Two independent draws per probe per arm: 1,200 reads. A probe’s four calls are consecutive, in the order A1 B1 B2 A2, where A is the arm sent first in draw 1, B the other arm, and the digit the draw. A hash rank decides which arm goes first in draw 1 (RAW for 150 probes, DECUE for 150); draw 2 reverses the order. Both arms have the same mean planned position, 599.5 |
| Judge | GPT-6.1 Sol at medium reasoning, up to 16,384 output tokens, with S10c’s STALE binding-judge prompt; one judge call per scenario, arm, and draw: 400 calls. Validity is inherited from S17 Part B (87 items: agreement .966, κ .910; plain-arm subset of nine items: agreement .889, κ .780) and was not retested on S18’s answers |
| Estimand | $D = \mathrm{acc}(\mathrm{RAW}) - \mathrm{acc}(\mathrm{DECUE})$, in points, with S10c’s estimator: the mean over scenarios of each scenario’s mean paired probe difference |
| Per-draw rules | A judged draw counts its binary verdict. A draw whose read exhausted its allowed attempts counts 0. A draw whose judge call is missing or unsent is missing. A probe’s value is the mean over its nonmissing draws (0, 1/2, or 1). A complete-case sensitivity treats exhausted draws as missing |
| Inference | A 10,000-resample scenario-bootstrap 95% interval (seed 2202); a two-sided seeded sign-flip test on scenario means with 10,000 draws, $p = (1 + e)/10{,}001$, where $e$ is the number of draws at least as extreme as the observed $D$. Tier comparisons use exact rationals |
| Tiers (first that holds) | “native reliance supported”: p \< .05, lower bound \> 0, and $D \geq 5$. “small positive”: p \< .05, lower bound \> 0, and $0 < D < 5$. “reversed”: p \< .05, upper bound \< 0, and $D < 0$. “practically equal”: the 95% interval lies inside the closed band \[−5, +5\]. “inconclusive”: otherwise. Health checks come first: an integrity failure yields the status UNRESOLVED, and a share of valid reads or of valid judge calls below 98% yields the status INCOMPLETE |
| Judge anchor (registered as EP-19) | Descriptive and run first. GPT-6.1 Sol judges S10c’s existing 300 Gemini 3.8 Flash plain answers in 100 judge calls, whose prompts equal S10c’s GLM-5.3-Flash judge prompts by SHA-256. The anchor gives a same-judge drift check and judge–judge agreement. It is outside the primary health and completeness rules |

RAW carries the cues because the literal design was degenerate: S10c’s plain prompt is already de-cued, so applying the de-cue to it changed 0 of 300 prompts. The registered design therefore restores STALE’s own typography and clock times in RAW and keeps S10c’s plain prompt as DECUE. The probe itself is not de-cued. Because RAW restores STALE’s typography and clock times, RAW prompts are slightly longer than DECUE prompts: 20,141 against 19,840 mean input tokens, about 1.5%.

#### B.3.2. Closure and populations

The pipeline ran the verification, anchor, reading, judging, and analysis steps in the registered order, and every step completed without error. Reading and judging both ended before the analysis started. No stop was recorded, and no planned read or judge call was pending at analysis time. The post-freeze, reporting-only amendment makes a verdict final only under these conditions, so the registered verdict is final. Table B3.1 gives the acquisition counts and Table B3.2 the endpoint counts.

**Table B3.1. Marginal acquisition counts.** The completeness thresholds were 1,176 reads and 392 judge calls. The judge anchor is not part of completeness.

| Part | Planned | Valid | Attempts | Exhausted | Hard cap on live attempts |
|----|---:|---:|---:|---:|---:|
| Judge anchor (GPT-6.1 Sol on S10c answers) | 100 calls | 100 | 100 | 0 | 150 |
| Reads (Gemini 3.8 Flash) | 1,200 reads | 1,200 | 1,201 | 0 | 1,800 |
| Judge (GPT-6.1 Sol) | 400 calls | 400 | 400 | 0 | 600 |

The extra read attempt was one HTTP 503 transport failure, recovered on the next attempt. In all three parts, every logged attempt has a matching result record, so no attempt was lost.

**Table B3.2. Endpoint counts.**

| Endpoint population | RAW | DECUE |
|----|---:|---:|
| Probes with two judged draws | 300 | 300 |
| Probes with one judged draw (other read exhausted / other judge call missing) | 0 / 0 | 0 / 0 |
| Probes with no judged draw (both reads exhausted / one exhausted and one judge call missing) | 0 / 0 | 0 / 0 |
| Missing probes | 0 | 0 |
| Exhausted draws scored 0 | 0 | 0 |
| Draw cells with a valid read and a verdict | 600 | 600 |

All 300 probes are paired, and all 100 scenarios contribute all three probes. No probe slot in any judge call contained the placeholder text used for a missing answer (0 of 1,200). Because no draw failed, every per-probe value is the plain mean of two judged draws. Nothing was imputed, and the complete-case sensitivity equals the primary.

#### B.3.3. Primary result

Table B3.3 gives the registered contrast.

**Table B3.3. Registered primary contrast.** $D$ is an estimate in points; the exact values are the stored rationals.

| Quantity | Value |
|----|----|
| $D = \mathrm{acc}(\mathrm{RAW}) - \mathrm{acc}(\mathrm{DECUE})$ | +1.33 points (exactly 4/3) |
| 95% scenario-bootstrap interval (10,000 resamples, seed 2202) | \[−1.17, +3.83\] (exactly \[−7/6, +23/6\]) |
| Two-sided sign-flip p (seeded Monte Carlo, 10,000 draws) | .362 (3,624/10,001) |
| Exact sign-flip p over all $2^{31}$ sign vectors (post hoc sensitivity from a separate recomputation, confirmed by a second one using integer convolution) | .361 |
| p \< .05 | No |
| Interval excludes 0 | No |
| Interval inside \[−5, +5\] | Yes |
| Registered tier | practically equal |
| Scenarios / probes | 100 / 300 |
| Probe differences: RAW higher / DECUE higher / equal | 23 / 16 / 261 |
| Scenarios up / down / tie | 18 / 13 / 69 |
| Arm accuracy, % \[scenario-cluster 95% interval\] | RAW 64.5 \[59.0, 69.7\]; DECUE 63.2 \[57.5, 68.7\] |

The binding p is the seeded Monte Carlo value. The stored output marks exact enumeration as not applicable, because the code enumerates sign vectors only when at most 20 scenario differences are nonzero; here 31 are. A separate recomputation enumerated all $2^{31}$ sign vectors and obtained .361, and a second recomputation confirmed this value by integer convolution (193,838,655/536,870,912 ≈ .36105). The tier is the same under either value, since both are far above .05. In this run, $D$ and both bounds happen to fall on a 1/12-point grid; that is not true in general, so the tier rests on the exact rational comparisons.

In the form that the reporting-only amendment requires, the verdict is as follows. On the reused S10c test split, in the user-only rendering of S10 and S10c (not the official STALE evaluation layout), and with STALE’s typographic and clock-time cues removed jointly (clock time is also legitimate template content), accuracy under the two prompts was practically equal within the registered ±5-point margin for one plain reader, Gemini 3.8 Flash. The estimate is $D$ = +1.33 points, with a 95% interval of \[−1.17, +3.83\] inside the closed band \[−5, +5\]. The upper bound means that a benefit from the two cues of up to about 4 points remains compatible with the data.

**Realized precision.** The interval’s half-width is about 2.5 points. The planning estimates for two draws were 3.1 points, if all per-scenario variance were draw noise, and 3.5 points, if about a quarter of it were stable. The planning probabilities of a “practically equal” verdict at a true $D$ of 0 (.76 and .60) were illustrations under those assumptions, not bounds. Under a stable-variance fraction of one half, the same planning model gives about .46.

#### B.3.4. Descriptives

Nothing in this subsection decides a registered verdict, and no multiplicity correction is applied. Intervals and p-values are single-seed values. Table B3.4 gives the strata and Table B3.5 the arm accuracies.

**Table B3.4. Descriptive strata.** $D$ in points, with the same estimator. SR, PR, and IPA are the three probe types; T1 and T2 are STALE’s two scenario types, co-referential and propagated.

| Stratum | $D$ | 95% interval | Sign-flip p | Probes (scenarios) | Probes RAW higher / DECUE higher |
|----|---:|----|---:|---:|---:|
| SR | +3.00 | \[+0.5, +6.0\] | .061 | 100 (100) | 5 / 0 |
| PR | +2.00 | \[−2.5, +6.5\] | .531 | 100 (100) | 8 / 5 |
| IPA | −1.00 | \[−6.5, +4.0\] | .854 | 100 (100) | 10 / 11 |
| T1 (co-referential) | −1.33 | \[−5.0, +2.7\] | .633 | 150 (50) | 8 / 13 |
| T2 (propagated) | +4.00 | \[+1.3, +7.0\] | .013 | 150 (50) | 15 / 3 |
| Draw 1 only (binary) | +0.33 | \[−3.0, +3.7\] | 1.000 | 300 (100) | 13 / 12 |
| Draw 2 only (binary) | +2.33 | \[−1.0, +5.7\] | .249 | 300 (100) | 16 / 9 |
| Draw-1 pair sent RAW first | +4.51 | \[+0.9, +8.8\] | .028 | 150 (85) | 14 / 5 |
| Draw-1 pair sent DECUE first | −0.30 | \[−3.7, +3.2\] | .939 | 150 (83) | 9 / 11 |

**Table B3.5. Arm accuracies (%).** The per-draw values come from the study report’s parse of the stored verdicts.

| Arm   | Overall |      SR / PR / IPA |     T1 / T2 | Draw 1 / draw 2 |
|-------|--------:|-------------------:|------------:|----------------:|
| RAW   |    64.5 | 87.0 / 39.5 / 67.0 | 69.7 / 59.3 |     63.7 / 65.3 |
| DECUE |    63.2 | 84.0 / 37.5 / 68.0 | 71.0 / 55.3 |     63.3 / 63.0 |

Two of the nine strata have a nominal p below .05: T2 and the RAW-first stratum. T2’s interval excludes 0, while T1’s point estimate has the opposite sign (propagated scenarios +4.00 \[+1.3, +7.0\], co-referential −1.33 \[−5.0, +2.7\]). This is a pattern for a later registered test, not a finding of S18. The split into T1 and T2 rests on benchmark metadata that neither the study report nor the recomputations rederived; it is internally consistent (the T1 and T2 values average to the overall $D$ and accuracies).

The two draw-1 first-arm strata are descriptive probe subsets, not an order contrast. They use the two-draw per-probe values, and draw 2 reverses the order, so every probe in both strata had each arm first once. A common additive first-versus-second effect cancels in the planned ABBA schedule, subject to the one realized-order exception below and to drift. Their sign difference is therefore a difference between two hash-assigned probe subsets. No interaction test was registered.

**Table B3.6. Within-arm draw discordance and byte identity.** A discordant probe is one whose two judged draws received different verdicts.

| Arm | Probes with both draws judged | Discordant probes | Share (%) | Byte-identical answer pairs (SHA-256) |
|----|---:|---:|---:|---:|
| RAW | 300 | 17 | 5.7 | 0 / 300 |
| DECUE | 300 | 27 | 9.0 | 0 / 300 |

The two recorded answers differed byte for byte on every probe (0 of 300 identical pairs in each arm); this does not establish statistical independence of reader or judge errors. These are within-arm, draw-to-draw discordances. The planning noise anchor, S10b’s 13.7%, is a between-arm discordance (plain against unsanitized plain) with a different reader and judge, so the two are not directly comparable.

**Position descriptives (post hoc, not registered).** Pooled over both draws and grouped by planned position within a draw’s adjacent pair, RAW scores 65.7% when sent first and 63.3% when sent second; DECUE scores 63.0% and 63.3% (300 draws per cell). By realized send time, RAW scores 65.8% first (n = 301) and 63.2% second (n = 299); DECUE scores 62.9% first (n = 299) and 63.5% second (n = 301). The gaps are at most about 2.6 points, and none is a test. The order design balances mean planned position, not arbitrary drift or retry effects. Each arm went first exactly once in 300 of 300 probes as planned and in 299 of 300 as realized: one retried read moved one probe’s DECUE draw-1 call to the end of its block.

**Exploratory.** On the 97 scenarios whose evidence pair shares a clock time, $D$ = +1.72 points, 95% interval \[−0.69, +4.12\]. The other subset has three scenarios and is not evaluable, since it has fewer than 10. The per-scenario difference has a Pearson correlation of .166 with the typographic edit count and of .034 with RAW history length.

#### B.3.5. Judge anchor

All 100 anchor judge calls were valid, and every anchor prompt matched S10c’s GLM-5.3-Flash judge prompt by SHA-256 (100 of 100). The anchor’s own health checks passed: prompt identity, rows matching the plan, zero cache hits, a single reported model equal to the judge’s, and raw-file integrity. Everything in this subsection is descriptive; Table B3.7 gives the values.

**Table B3.7. Same-judge drift and judge–judge agreement.** Accuracies in %.

| Comparison | Value |
|----|----|
| S18 DECUE, two fresh draws, GPT-6.1 Sol judge | 63.2 |
| S10c plain, one historical draw, GPT-6.1 Sol judge | 61.7 |
| Same-judge difference \[paired 95% interval, S10c’s estimator; no test\] | +1.5 \[−1.17, +4.17\] |
| Scenarios up / down / tie | 19 / 13 / 68 |
| GPT-6.1 Sol against GLM-5.3-Flash on the 300 S10c plain answers: both pass / GPT-6.1 Sol only / GLM-5.3-Flash only / both fail | 183 / 2 / 15 / 100 |
| Agreement / Cohen’s κ | .943 / .878 |
| Accuracy: GPT-6.1 Sol / GLM-5.3-Flash | 61.7 / 66.0 |
| Cross-judge check: S18 DECUE (GPT-6.1 Sol) minus S10c plain (GLM-5.3-Flash) | −2.8 points |

Under the GPT-6.1 Sol judge, S10c’s historical plain answers score 4.3 points lower than under GLM-5.3-Flash (61.7% against 66.0%); under the same GPT-6.1 Sol judge, S18’s DECUE answers score 1.5 points above them \[−1.17, +4.17\]. S18 and S10c ran Gemini 3.8 Flash with the same settings (Card B3), so neither contrast involves a change of reader setting. Neither separates reader drift from sampling, because each compares two fresh draws with one historical draw; the −2.8-point cross-judge gap is therefore attributed neither to the judge nor to the reader. The same-judge comparison is an accounting comparison under one judge, not a bound on reader drift. The disagreements are lopsided: GLM-5.3-Flash passed 15 answers that GPT-6.1 Sol failed, and GPT-6.1 Sol passed two that GLM-5.3-Flash failed. This is agreement between two LLM judges: neither is a gold standard, no human labels exist for these answers, and the comparison does not retest validity on S18’s own answers.

#### B.3.6. Execution scope

All planned reads and judge calls completed, with no stop and no pending call. The execution and cost logs are omitted from this appendix; omitting them changes no reported result or validity rule.

#### B.3.7. Deviations, amendments, and computational checks

S18 used the reused S10c test split, with earlier outcomes known. Two substitute reviews replaced the registration’s planned pre-freeze review (Appendix I.2). A reporting-only amendment fixed the claim wording before any study outcome was opened; it changed no comparison or margin. Three separate recomputations from the saved outputs checked the result; Appendix I.4 gives their sources and exposure limits. These recomputations do not validate the judge’s labels.

#### B.3.8. Limitations

- One reader (Gemini 3.8 Flash) and one judge (GPT-6.1 Sol). The judge’s validity is inherited from S17 Part B, whose plain-arm subset had nine items (agreement .889, κ .780); it was not retested on S18’s answers. The anchor adds judge–judge agreement only, without human labels.
- Typography and clock time were removed jointly, so S18 cannot separate them. Clock time is also legitimate template content (the official `[Time: ts]` field), so DECUE also removes real time-of-day information, not only an artifact.
- The interval \[−1.17, +3.83\] allows a benefit from the two cues of up to about 4 points. The result does not show that the cues are irrelevant to accuracy.
- Length, turn-count, and content cues remain in both arms, and S18 says nothing about them; on the wrong-question atlas’s STALE population, the fewest-turns prior alone reaches any-gold@5 of 96.1% (Appendix E). RAW prompts are also about 1.5% longer than DECUE prompts.
- The layout is the user-only rendering of S10 and S10c, not the official STALE evaluation layout, and the result does not transfer to that layout.
- The test split is reused. DECUE consists of two temperature-1.0 redraws of S10c’s plain prompts, whose GLM-5.3-Flash-judged outcome was known. This is conditional robustness, not fresh confirmation.
- The ABBA order balances mean planned position, not arbitrary drift or retry effects. All descriptive strata, position splits, and exploratory results are single-seed and support no registered verdict.
- S18 makes no claim about other readers, other benchmarks, or published systems, and none about a reader’s handling of any cue beyond this one contrast.

### B.4. S19: four readers from four vendors, with budget-matched two-session pointers

S19 asked whether naming the evidence pair beats the retriever’s top two when both pointers name two sessions and share the artifact pointer’s 46-token note, for four readers from four vendors, and whether S10c’s premium over the five-session pointers holds for these readers. It ran on S10c’s reused test split, so it measures conditional robustness, never a fresh confirmation. Every outcome was judged by an LLM (GPT-6.1 Sol), and the validation gate is LLM adjudication, not human validation. Three of the four readers completed. The fourth, Gemini 3.8 Flash, was rerun in the separately registered successor S19b, which completes S19’s families without redeciding them (B.5).

**Legend.** The tables and quoted registered text of B.4 and B.5 use the registered short labels, which are defined only here. Readers: glm = GLM-5.3-Flash, g38 = Gemini 3.8 Flash, sol = GPT-6.1 Sol, and msp = Muse Spark 1.3 (standard tier; see the main paper’s §3.4). Arms: plain; generic, the generic instruction; `ptr_hyb5` and `ptr_dense5`, hybrid-5 and dense-5 (the top five sessions of the hybrid and of the dense ranking); `ptr_regex`, the artifact pointer; oracle, the oracle note; `ptr_hyb2` and `ptr_dense2`, hybrid-2 and dense-2 (the top two sessions); and `ptr_art5` or art5, gold-pair-plus-three (the gold pair plus three hash-chosen non-gold sessions). A contrast label such as `glm:ptr_regex-ptr_hyb2` means the artifact pointer minus hybrid-2 for GLM-5.3-Flash. NEW and OLD are the newer and older gold sessions. In S19’s registered rules, a unit is one planned (arm, probe) outcome, and a part is the batch of calls for one reader or judge. Tables whose captions mark their rows or values as verbatim reproduce the registered output. Only their column headers and number format follow this paper’s style: thousands separators, no leading zero for p values and κ, minus signs, dashes for empty cells, and valid shares in percent.

#### B.4.1. Protocol card

**Interval convention.** The primary and F3 intervals are Bonferroni per-contrast intervals. Each has level 99.69% (= 1 − .05/16; registered as 319/320) in the primary family of 16 contrasts and 99.58% (= 1 − .05/12; registered as 239/240) in F3’s family of 12; these levels target nominal 95% coverage for each family as a whole. Bootstrap coverage is nominal, not an exact finite-sample guarantee. The registered sentences and outputs call these intervals “simultaneous”; the word denotes this per-contrast adjustment, not a family coverage of 99.69% or 99.58%. The tables here head that column “Bonferroni per-contrast CI”. The same convention applies to S19b (B.5).

**Card B4. S19 protocol card.** Registered definitions, condensed from the preregistration and its binding annex.

| Protocol element | Registered definition |
|----|----|
| Registration and freeze | Preregistration plus a binding annex of operational definitions, which takes precedence where the two differ; frozen 2026-10-05 17:59:16 (+03:00), before any test call. Known before registration: the aggregate results of S10b, S10c, S17, and S18. The direction of the two-session contrasts was predictable (hybrid-2 and dense-2 name the newer gold session in only 130 and 163 of 300 probes); the five-session direction was known from S10c |
| Population | S10c’s frozen test list: 100 scenarios × 3 probes = 300 probes. The split is reused: S10b, S10c, S17, and S18 had used it; GLM-5.3-Flash and Gemini 3.8 Flash had read it, and GPT-6.1 Sol had judged it; Muse Spark 1.3 had not seen it in any of our earlier studies. STALE is public, so pretraining exposure cannot be ruled out |
| Readers | GLM-5.3-Flash, Gemini 3.8 Flash, GPT-6.1 Sol, and Muse Spark 1.3 (standard tier), each at its vendor’s “high” level and temperature 1.0. “High” is a vendor label with different mechanisms, so nothing here compares the readers’ reasoning. Output caps C1 → C2 in tokens (one escalation; timeout 600 s): GLM-5.3-Flash 9,216 → 18,432; Gemini 3.8 Flash 16,384 → 32,768; GPT-6.1 Sol 3,584 → 7,168; Muse Spark 1.3 8,192 → 16,384. Removed by the author before the freeze: xAI’s grok-4.7 (no xAI console access) and Claude Sonnet 5.5 (cost, after the pre-freeze pilot) |
| Arms | Nine: S10c’s plain, generic instruction, hybrid-5, dense-5, artifact pointer, and oracle note arms (prompt hashes equal to S10c’s in 1,800 of 1,800); hybrid-2 and dense-2, the top two sessions of the hybrid and of the dense ranking, with the artifact pointer’s 46-token note; and gold-pair-plus-three, the gold pair plus three hash-chosen non-gold sessions in chronological order, with the five-session 79-token note. A check for pointer or gold leakage found none in the 2,700 prompts |
| One read per distinct request | Arms whose requests are byte-identical share one read: 2,375 reads per reader instead of 2,700 nominal units. Shared reads: hybrid-2 = artifact pointer in 105 probes, dense-2 = artifact pointer in 140, hybrid-2 = dense-2 in 153, and hybrid-5 = dense-5 in 17. On the 105 and 140 shared-answer probes, $D$ is judge noise plus possible halo (the whole judge request is byte-identical on 24 and 63 of them) |
| Order | Scenario-consecutive blocks in an 18-row odd-n Williams design over the nine arms; the validation packet’s scenarios first; up to 10 concurrent requests per reader part, one per scenario, and one part per provider at a time |
| Binding judge | GPT-6.1 Sol at reasoning “medium”, with S10c’s STALE judge prompt (as in S17-B2); one judge call per reader, arm, and scenario, scoring its three probes: 900 per reader, 3,600 in all. GPT-6.1 Sol therefore also judges its own model family’s reader. The GLM-5.3-Flash secondary judge is descriptive; its results are in B.4.11 |
| Validation gate | A fresh blind 72-item packet (4 readers × 9 arms × 2), built and scored only after every read part had closed, and labeled by a fresh Claude Opus 5.5 instance (`claude-opus-5-5`) that saw no arm, reader, or outcome. Pass rule: at least 60 determinate items with a binding verdict, agreement ≥ .80, and finite $\kappa \geq .70$ (unweighted). A failed gate makes every primary contrast “judge-limited” |
| Estimand and inference | $D_r(B) = \mathrm{acc}_r(\text{artifact}) - \mathrm{acc}_r(B)$, in points over 300 probes, for reader $r$ and $B$ in hybrid-2, dense-2, hybrid-5, and dense-5; S10c’s estimator (the mean over scenarios of per-scenario mean paired differences); sign-flip permutation p (10,000 draws, seed 2202); scenario bootstrap with 100,000 resamples for the primary family (10,000 elsewhere); exact rational arithmetic in the tier rules |
| Families | Primary: 16 contrasts (4 readers × 4), Holm-adjusted, with Bonferroni per-contrast intervals at 99.69%. Family S1: generic instruction − plain (Holm over four; 95% intervals). Family S2: hybrid-2 − hybrid-5 and dense-2 − dense-5 (Holm over eight; 95% intervals). Family F3: art5 − hybrid-5, art5 − dense-5, and artifact pointer − art5 (Holm over 12 across readers; Bonferroni per-contrast intervals at 99.58%; descriptive tiers only). A reader that is not claimable enters every family at p = 1 and is labeled “not classified” |
| Tiers (first that holds) | “supported: at least +5 asserted”: Holm p \< .05, $D \geq +5$, and Bonferroni per-contrast lower bound \> +5; “supported (estimate \>= +5, adjusted lower bound \> 0)”: Holm p \< .05, $D \geq +5$, and lower bound \> 0; “reversed”: upper bound \< 0; “practically equal”: interval inside (−5, +5); otherwise “inconclusive”. Order of checks: integrity, claim status, gate, and tier |
| Claim eligibility | Over the 2,400 units of the eight arms other than art5: at least 98% valid outcomes and at most 120 terminal units (units whose read failed for good); reader-terminal units count as incorrect for every reader. F3 has its own rule over the 300 art5 units |
| Not licensed (registered list) | That count does not matter; that S10c’s premium is identity rather than count; retrieval in general; cue reliance; a deployable pointer; fresh confirmation; any model ranking; reader equivalence; redeciding S10c; human validation |

**Pilot evidence for “high”.** GLM-5.3-Flash’s ratio of reasoning tokens at the high and low settings was at least 1.5 in six of six pre-freeze supplement pairs (pass rule: four of six) and in five of six pairs of the S19 pilot. The paid readers accepted their “high” parameter (HTTP 200 with usage and the requested model id). This shows that the parameter was accepted, not how much reasoning it produced.

#### B.4.2. Coverage, health, and the Gemini 3.8 Flash stop

**Table B4.1. Completeness per reader over the eight arms other than art5.** Rows verbatim. Units are planned (arm, probe) outcomes, 2,400 per reader. Reader-terminal units count as incorrect and therefore as valid outcomes.

| Reader | Status | Planned | Scored | Reader-terminal (incorrect) | Judge-terminal missing | Read unresolved | Judge unresolved | Valid (%) |
|----|----|----|----|----|----|----|----|----|
| GLM-5.3-Flash (model id glm-53-flash) | claimable | 2,400 | 2,400 | 0 | 0 | 0 | 0 | 100.0 |
| Gemini 3.8 Flash (model id gemini-3.8-flash) | incomplete (STOP_NON_RETRYABLE) | 2,400 | 338 | 1 | 0 | 2,061 | 0 | 14.1 |
| GPT-6.1 Sol (model id gpt-6.1-sol) | claimable | 2,400 | 2,400 | 0 | 0 | 0 | 0 | 100.0 |
| Muse Spark 1.3, standard tier (model id muse-spark-1.3) | claimable | 2,400 | 2,393 | 7 | 0 | 0 | 0 | 100.0 |

**The Gemini 3.8 Flash stop.** Gemini 3.8 Flash’s read part stopped at 18:24:45 with the status “STOP_NON_RETRYABLE”, a stop that the registered rules never resume. The first request of one unit (output cap 16,384 tokens, `thinkingLevel` “high”) returned 26,700 output tokens, 26,439 of them reasoning tokens, with the finish reason “MAX_TOKENS”. The pipeline’s execution code (runtime v4) therefore treated the reserved token bound as exceeded, froze the part’s budget (fail-closed), and refused the escalation request; spending stayed within the reserved budget (USD 0.1087 of 0.1273). S19’s reporting-only amendment A1 concludes that Gemini’s `maxOutputTokens` is not a hard bound on thinking at “high” (it was exceeded in one of 335 Gemini 3.8 Flash requests). When the part ended, 333 reads were valid, and 2,061 of the 2,400 units of the eight eligible arms had never been read (Table B4.1). S19 therefore has no Gemini 3.8 Flash result at its high setting, and the 333 valid reads enter no classified contrast. The author approved a successor for Gemini 3.8 Flash alone (S19b) on 2026-10-05. It is a separate registration on the same reused split, with its own gate and runtime v5, and its result is in B.5; S19’s 333 valid Gemini 3.8 Flash reads stay in S19 and are not reused.

**Other units and health.** Seven Muse Spark 1.3 reads ended with HTTP 400 (cause not recorded). They count as eight incorrect units (seven in the eligible arms and one in art5), far below the 120-unit stop rule. The binding judge returned 2,836 valid judge calls of the 3,600 planned, and all 764 unsent calls belong to Gemini 3.8 Flash. Every integrity check passed: the lock, pins, judge-template pins, the S10c copy, rows matching the plan, reported model ids, raw-file integrity, and zero harness cache hits. A detector for GLM-5.3-Flash answers served from the shared API proxy’s cache of identical requests flagged none of the 2,377 reader rows. No read reached its escalated cap, and no part recorded a billed timeout.

#### B.4.3. Validation gate

The 72-item packet was built after all read parts had closed (Gemini 3.8 Flash’s part counted as closed because of its terminal stop). Its fields carry no reader, arm, scenario id, or probe type; a separate computational check confirmed this from the field names. The adjudicator was a fresh Claude Opus 5.5 instance (`claude-opus-5-5`) that saw no arm, reader, or outcome; it was given only a copy of the packet. Its freshness, its exclusive exposure to the packet, and its single adjudication are attested in the study record, not checked. The pipeline’s pre-gate analysis, with every $D$ value, existed before the adjudication, as registered. The gate passed: 72 determinate items, agreement .972 (70 of 72), and κ .906, with an adjudicator pass share of 83.3% and a judge pass share of 80.6%. Both disagreements are judge-fail, adjudicator-pass labels on GLM-5.3-Flash answers in comparator arms (dense-5 and dense-2). If the adjudicator is right, these judge errors understate comparator accuracy and so inflate GLM-5.3-Flash’s reported $D$ against those pointers; two items cannot size this bias. Per-reader agreement is .909 for GLM-5.3-Flash (κ .744, n = 22) and 1.000 for Gemini 3.8 Flash (n = 11), GPT-6.1 Sol (n = 19), and Muse Spark 1.3 (n = 20); no reader falls below .80. Thirteen items are backups, seven of them drawn from another reader’s candidates. Cohen’s κ is undefined in the oracle note, hybrid-5, and artifact pointer arms, because both raters passed all eight items in each; the packet therefore holds no failing artifact-arm answer. This is LLM adjudication, not human validation.

#### B.4.4. Primary family and registered sentences

**Table B4.2. Primary family: artifact pointer minus each comparator, by reader.** Rows verbatim; Holm over 16; Bonferroni per-contrast intervals at 99.69% (= 1 − .05/16); 100,000 bootstrap resamples. $D$ and intervals are in points. Up / down / tie counts scenarios; discordant a / b counts probes that pass only under the artifact pointer (a) or only under the comparator (b). Bounds worst / best give $D$ over the 300 planned probes with every missing outcome set against, or in favor of, the artifact pointer. The main paper’s Figure 3 plots the 16 completed contrasts, with Gemini 3.8 Flash’s four from S19b (Table B5.2). Perm. p is the permutation p-value.

| Contrast | $D$ (points) | 95% CI | Bonferroni per-contrast CI | Perm. p | Holm entry | Holm p | Up / down / tie | Discordant a / b | Bounds worst / best | Tier |
|----|----|----|----|----|----|----|----|----|----|----|
| glm:ptr_regex-ptr_hyb2 | +21.0 | \[+16.0, +26.3\] | \[+13.3, +29.0\] | .0001 | own p | .0016 | \[47, 1, 52\] | \[69, 6\] | \[+21.0, +21.0\] | supported: at least +5 asserted |
| glm:ptr_regex-ptr_dense2 | +19.0 | \[+14.0, +24.0\] | \[+11.7, +26.7\] | .0001 | own p | .0016 | \[46, 2, 52\] | \[60, 3\] | \[+19.0, +19.0\] | supported: at least +5 asserted |
| glm:ptr_regex-ptr_hyb5 | +12.0 | \[+7.7, +16.7\] | \[+5.3, +19.0\] | .0001 | own p | .0016 | \[32, 4, 64\] | \[44, 8\] | \[+12.0, +12.0\] | supported: at least +5 asserted |
| glm:ptr_regex-ptr_dense5 | +11.0 | \[+6.7, +15.7\] | \[+4.3, +18.3\] | .0001 | own p | .0016 | \[28, 4, 68\] | \[39, 6\] | \[+11.0, +11.0\] | supported (estimate \>= +5, adjusted lower bound \> 0) |
| g38:ptr_regex-ptr_hyb2 | +28.1 | \[+13.5, +44.8\] | \[+8.3, +54.2\] | .0040 | p = 1 (reader incomplete (STOP_NON_RETRYABLE)) | — | \[9, 0, 7\] | \[12, 0\] | \[−81.0, +89.3\] | not classified (incomplete (STOP_NON_RETRYABLE)) |
| g38:ptr_regex-ptr_dense2 | +19.8 | \[+6.2, +35.4\] | \[+2.1, +44.8\] | .0331 | p = 1 (reader incomplete (STOP_NON_RETRYABLE)) | — | \[6, 0, 10\] | \[8, 0\] | \[−82.3, +88.0\] | not classified (incomplete (STOP_NON_RETRYABLE)) |
| g38:ptr_regex-ptr_hyb5 | +17.9 | \[+7.1, +29.8\] | \[+2.4, +36.9\] | .0331 | p = 1 (reader incomplete (STOP_NON_RETRYABLE)) | — | \[6, 0, 8\] | \[7, 0\] | \[−82.7, +89.0\] | not classified (incomplete (STOP_NON_RETRYABLE)) |
| g38:ptr_regex-ptr_dense5 | +20.2 | \[+3.6, +38.1\] | \[−2.4, +48.8\] | .0811 | p = 1 (reader incomplete (STOP_NON_RETRYABLE)) | — | \[6, 1, 7\] | \[7, 1\] | \[−83.0, +89.0\] | not classified (incomplete (STOP_NON_RETRYABLE)) |
| sol:ptr_regex-ptr_hyb2 | +19.0 | \[+14.0, +24.3\] | \[+11.7, +27.0\] | .0001 | own p | .0016 | \[41, 0, 59\] | \[57, 0\] | \[+19.0, +19.0\] | supported: at least +5 asserted |
| sol:ptr_regex-ptr_dense2 | +16.7 | \[+12.3, +21.3\] | \[+10.0, +24.0\] | .0001 | own p | .0016 | \[39, 0, 61\] | \[50, 0\] | \[+16.7, +16.7\] | supported: at least +5 asserted |
| sol:ptr_regex-ptr_hyb5 | +10.7 | \[+7.0, +14.7\] | \[+5.3, +17.0\] | .0001 | own p | .0016 | \[26, 0, 74\] | \[32, 0\] | \[+10.7, +10.7\] | supported: at least +5 asserted |
| sol:ptr_regex-ptr_dense5 | +10.3 | \[+6.7, +14.3\] | \[+5.0, +16.7\] | .0001 | own p | .0016 | \[25, 0, 75\] | \[31, 0\] | \[+10.3, +10.3\] | supported (estimate \>= +5, adjusted lower bound \> 0) |
| msp:ptr_regex-ptr_hyb2 | +15.7 | \[+11.0, +20.3\] | \[+9.0, +23.0\] | .0001 | own p | .0016 | \[35, 0, 65\] | \[48, 1\] | \[+15.7, +15.7\] | supported: at least +5 asserted |
| msp:ptr_regex-ptr_dense2 | +13.0 | \[+8.7, +17.7\] | \[+6.7, +20.3\] | .0001 | own p | .0016 | \[31, 1, 68\] | \[40, 1\] | \[+13.0, +13.0\] | supported: at least +5 asserted |
| msp:ptr_regex-ptr_hyb5 | +8.7 | \[+5.3, +12.3\] | \[+4.0, +14.0\] | .0001 | own p | .0016 | \[24, 1, 75\] | \[27, 1\] | \[+8.7, +8.7\] | supported (estimate \>= +5, adjusted lower bound \> 0) |
| msp:ptr_regex-ptr_dense5 | +7.3 | \[+4.3, +10.7\] | \[+3.0, +12.7\] | .0001 | own p | .0016 | \[18, 0, 82\] | \[22, 0\] | \[+7.3, +7.3\] | supported (estimate \>= +5, adjusted lower bound \> 0) |

**Registered sentences.** The 22 sentences below are the registered wording, generated and checked in code, and are quoted verbatim; they keep the registered reader names and model ids. Bracketed glosses are ours and appear at first use only.

> - On the consumed \[i.e., reused\] S10c test split, for GLM-5.3-Flash (model id glm-53-flash) at its vendor’s high setting, the artifact pointer scored +21.0 points above the top-2 hybrid retrieval pointer \[hybrid-2\] (two sessions, same note) (simultaneous \[i.e., Bonferroni per-contrast, 99.69%\] 319/320 interval \[+13.3, +29.0\]; Holm p = 0.0016): supported, at least +5 points.
> - On the consumed S10c test split, for GLM-5.3-Flash (model id glm-53-flash) at its vendor’s high setting, the artifact pointer scored +19.0 points above the top-2 dense retrieval pointer \[dense-2\] (two sessions, same note) (simultaneous 319/320 interval \[+11.7, +26.7\]; Holm p = 0.0016): supported, at least +5 points.
> - On the consumed S10c test split, for GLM-5.3-Flash (model id glm-53-flash) at its vendor’s high setting, the artifact pointer scored +12.0 points above the top-5 hybrid retrieval pointer \[hybrid-5\] (simultaneous 319/320 interval \[+5.3, +19.0\]; Holm p = 0.0016): supported, at least +5 points.
> - On the consumed S10c test split, for GLM-5.3-Flash (model id glm-53-flash) at its vendor’s high setting, the artifact pointer scored +11.0 points above the top-5 dense retrieval pointer \[dense-5\] (simultaneous 319/320 interval \[+4.3, +18.3\]; Holm p = 0.0016): supported.
> - Gemini 3.8 Flash (gemini-3.8-flash): not classified (incomplete (STOP_NON_RETRYABLE)).
> - Gemini 3.8 Flash (gemini-3.8-flash): not classified (incomplete (STOP_NON_RETRYABLE)).
> - Gemini 3.8 Flash (gemini-3.8-flash): not classified (incomplete (STOP_NON_RETRYABLE)).
> - Gemini 3.8 Flash (gemini-3.8-flash): not classified (incomplete (STOP_NON_RETRYABLE)).
> - On the consumed S10c test split, for GPT-6.1 Sol (model id gpt-6.1-sol) at its vendor’s high setting, the artifact pointer scored +19.0 points above the top-2 hybrid retrieval pointer (two sessions, same note) (simultaneous 319/320 interval \[+11.7, +27.0\]; Holm p = 0.0016): supported, at least +5 points.
> - On the consumed S10c test split, for GPT-6.1 Sol (model id gpt-6.1-sol) at its vendor’s high setting, the artifact pointer scored +16.7 points above the top-2 dense retrieval pointer (two sessions, same note) (simultaneous 319/320 interval \[+10.0, +24.0\]; Holm p = 0.0016): supported, at least +5 points.
> - On the consumed S10c test split, for GPT-6.1 Sol (model id gpt-6.1-sol) at its vendor’s high setting, the artifact pointer scored +10.7 points above the top-5 hybrid retrieval pointer (simultaneous 319/320 interval \[+5.3, +17.0\]; Holm p = 0.0016): supported, at least +5 points.
> - On the consumed S10c test split, for GPT-6.1 Sol (model id gpt-6.1-sol) at its vendor’s high setting, the artifact pointer scored +10.3 points above the top-5 dense retrieval pointer (simultaneous 319/320 interval \[+5.0, +16.7\]; Holm p = 0.0016): supported.
> - On the consumed S10c test split, for Muse Spark 1.3 (standard tier) (model id muse-spark-1.3) at its vendor’s high setting, the artifact pointer scored +15.7 points above the top-2 hybrid retrieval pointer (two sessions, same note) (simultaneous 319/320 interval \[+9.0, +23.0\]; Holm p = 0.0016): supported, at least +5 points.
> - On the consumed S10c test split, for Muse Spark 1.3 (standard tier) (model id muse-spark-1.3) at its vendor’s high setting, the artifact pointer scored +13.0 points above the top-2 dense retrieval pointer (two sessions, same note) (simultaneous 319/320 interval \[+6.7, +20.3\]; Holm p = 0.0016): supported, at least +5 points.
> - On the consumed S10c test split, for Muse Spark 1.3 (standard tier) (model id muse-spark-1.3) at its vendor’s high setting, the artifact pointer scored +8.7 points above the top-5 hybrid retrieval pointer (simultaneous 319/320 interval \[+4.0, +14.0\]; Holm p = 0.0016): supported.
> - On the consumed S10c test split, for Muse Spark 1.3 (standard tier) (model id muse-spark-1.3) at its vendor’s high setting, the artifact pointer scored +7.3 points above the top-5 dense retrieval pointer (simultaneous 319/320 interval \[+3.0, +12.7\]; Holm p = 0.0016): supported.
> - With the number of named sessions and the note fixed at two \[i.e., both pointers name two sessions and share the artifact pointer’s 46-token note\], naming the evidence pair beat the retriever’s top two by +21.0 points for GLM-5.3-Flash (model id glm-53-flash) on the consumed S10c test split.
> - With the number of named sessions and the note fixed at two, naming the evidence pair beat the retriever’s top two by +19.0 points for GLM-5.3-Flash (model id glm-53-flash) on the consumed S10c test split.
> - With the number of named sessions and the note fixed at two, naming the evidence pair beat the retriever’s top two by +19.0 points for GPT-6.1 Sol (model id gpt-6.1-sol) on the consumed S10c test split.
> - With the number of named sessions and the note fixed at two, naming the evidence pair beat the retriever’s top two by +16.7 points for GPT-6.1 Sol (model id gpt-6.1-sol) on the consumed S10c test split.
> - With the number of named sessions and the note fixed at two, naming the evidence pair beat the retriever’s top two by +15.7 points for Muse Spark 1.3 (standard tier) (model id muse-spark-1.3) on the consumed S10c test split.
> - With the number of named sessions and the note fixed at two, naming the evidence pair beat the retriever’s top two by +13.0 points for Muse Spark 1.3 (standard tier) (model id muse-spark-1.3) on the consumed S10c test split.

**Registered k-of-4 sentence (quoted verbatim).**

> On the consumed S10c test split, the budget-matched premium was supported for 3 of 4 readers against the top-2 hybrid retrieval pointer and 3 of 4 against the top-2 dense retrieval pointer; not run or not classified: Gemini 3.8 Flash (incomplete (STOP_NON_RETRYABLE)).

S19b’s registered k-of-4 sentence joins these three recorded classifications with Gemini 3.8 Flash’s tier from S19b and counts four of four against both two-session pointers (B.5.4).

**What the table says.** Twelve of the 16 contrasts in Table B4.2 are classified, and all 12 are “supported”. Eight reach “supported, at least +5”: the six budget-matched contrasts, and GLM-5.3-Flash and GPT-6.1 Sol against hybrid-5. Four reach only “supported”, so S19 cannot assert a premium of at least +5 for them: GLM-5.3-Flash against dense-5 (Bonferroni per-contrast lower bound +4.3), GPT-6.1 Sol against dense-5 (lower bound exactly +5.0, so the rule “\> +5” fails), and Muse Spark 1.3 against hybrid-5 (+4.0) and dense-5 (+3.0). Every classified permutation p sits at the floor of 10,000 draws (1/10,001), so all twelve Holm p values equal 16/10,001 (printed .0016). Scenarios that moved against the artifact pointer number zero for GPT-6.1 Sol, at most one for Muse Spark 1.3, and one to four for GLM-5.3-Flash. No outcome is missing for the three complete readers, so their worst and best bounds equal the estimates. The four Gemini 3.8 Flash rows rest on the 14 to 16 scenarios scored before the stop. Their bounds over the 300 planned probes (for example, \[−81.0, +89.3\]) show that the missing probes could put them almost anywhere, and they are not interpreted. S19b’s completed family (Table B5.2) evaluates Gemini 3.8 Flash’s four contrasts from fresh reads at S19’s 99.69% level and records these twelve classifications unchanged.

**Descriptive companions (no tier).** Pooled over the three claimable readers (95% scenario bootstrap), the premium is +18.6 \[+14.6, +22.8\] against hybrid-2, +16.2 \[+12.2, +20.4\] against dense-2, +10.4 \[+7.4, +13.7\] against hybrid-5, and +9.6 \[+6.6, +12.8\] against dense-5. On the 90 test scenarios without reader outcomes from the earlier pilot (B.1), the 12 complete-reader primary $D$ values lie between +8.1 and +20.7. On the 74 scenarios that S10b’s Gemini 3.5 Flash-Lite reader did not read, they lie between +7.2 and +21.6 (point estimates only).

#### B.4.5. Secondary families

**Table B4.3. Family S1: generic instruction minus plain.** Rows verbatim; Holm over four; 95% intervals; the only registered decision is Holm p \< .05.

| Contrast | $D$ | 95% CI | Permutation p | Holm p | Holm p \< .05 |
|----|----|----|----|----|----|
| glm:generic-plain | +24.3 | \[+19.0, +29.7\] | .0001 | .0004 | True |
| g38:generic-plain | +29.8 | \[+20.2, +39.3\] | .0007 | — | p = 1 (reader incomplete (STOP_NON_RETRYABLE)) |
| sol:generic-plain | +23.0 | \[+18.3, +27.7\] | .0001 | .0004 | True |
| msp:generic-plain | +20.7 | \[+15.7, +25.7\] | .0001 | .0004 | True |

For the three complete readers, the generic instruction, which needs no retrieval, scores +20.7 to +24.3 points above plain (Table B4.3; Holm p = .0004 each). No tier applies.

**Table B4.4. Family S2: trimming five sessions to two.** Each contrast is a retriever’s two-session pointer minus its five-session pointer. Rows verbatim; Holm over eight; 95% intervals; the only registered decision is Holm p \< .05.

| Contrast | $D$ | 95% CI | Permutation p | Holm p | Holm p \< .05 |
|----|----|----|----|----|----|
| glm:ptr_hyb2-ptr_hyb5 | −9.0 | \[−14.0, −4.0\] | .0012 | .0072 | True |
| glm:ptr_dense2-ptr_dense5 | −8.0 | \[−13.3, −2.7\] | .0058 | .0290 | True |
| g38:ptr_hyb2-ptr_hyb5 | −7.1 | \[−16.7, +2.4\] | .3784 | — | p = 1 (reader incomplete (STOP_NON_RETRYABLE)) |
| g38:ptr_dense2-ptr_dense5 | −2.4 | \[−9.5, +4.8\] | 1.0000 | — | p = 1 (reader incomplete (STOP_NON_RETRYABLE)) |
| sol:ptr_hyb2-ptr_hyb5 | −8.3 | \[−13.0, −4.0\] | .0010 | .0070 | True |
| sol:ptr_dense2-ptr_dense5 | −6.3 | \[−10.7, −2.0\] | .0077 | .0308 | True |
| msp:ptr_hyb2-ptr_hyb5 | −7.0 | \[−10.7, −3.3\] | .0005 | .0040 | True |
| msp:ptr_dense2-ptr_dense5 | −5.7 | \[−9.7, −2.0\] | .0085 | .0308 | True |

For each complete reader, the retriever’s top two score below its top five, by 5.7 to 9.0 points (Table B4.4; Holm p \< .05 in all six). These arms differ in three ways at once: the number of sessions named, the note (46 or 79 tokens), and which sessions are named (hybrid-2 names both gold sessions in 105 probes against hybrid-5’s 183, and dense-2 in 140 against dense-5’s 222). Family S2 does not separate these three differences.

**Table B4.5. Family F3: gold-pair-plus-three against the five-session pointers and the artifact pointer.** Rows verbatim; Holm over 12 across readers; Bonferroni per-contrast intervals at 99.58% (= 1 − .05/12); descriptive tiers, never confirmatory. F3’s claim status under its own completeness rule over the art5 arm (rule C-3; verbatim): glm = claimable; g38 = incomplete (STOP_NON_RETRYABLE); sol = claimable; msp = claimable.

| Contrast | $D$ | 95% CI | Bonferroni per-contrast CI | Permutation p | Holm entry | Holm p | Descriptive tier |
|----|----|----|----|----|----|----|----|
| glm:ptr_art5-ptr_hyb5 | +3.7 | \[−0.7, +8.0\] | \[−2.3, +9.7\] | .1234 | own p | .7403 | descriptive tier: inconclusive |
| glm:ptr_art5-ptr_dense5 | +2.7 | \[−1.7, +7.0\] | \[−3.7, +9.7\] | .3087 | own p | 1.0000 | descriptive tier: inconclusive |
| glm:ptr_regex-ptr_art5 | +8.3 | \[+4.7, +12.3\] | \[+3.3, +14.0\] | .0002 | own p | .0022 | descriptive tier: supported (estimate \>= +5, adjusted lower bound \> 0) |
| g38:ptr_art5-ptr_hyb5 | +15.5 | \[+7.1, +25.0\] | \[+2.4, +29.8\] | .0331 | p = 1 (reader incomplete (STOP_NON_RETRYABLE)) | — | descriptive tier: not classified (incomplete (STOP_NON_RETRYABLE)) |
| g38:ptr_art5-ptr_dense5 | +11.5 | \[+0.0, +23.1\] | \[−5.1, +28.2\] | .1898 | p = 1 (reader incomplete (STOP_NON_RETRYABLE)) | — | descriptive tier: not classified (incomplete (STOP_NON_RETRYABLE)) |
| g38:ptr_regex-ptr_art5 | +2.2 | \[+0.0, +6.7\] | \[+0.0, +11.1\] | 1.0000 | p = 1 (reader incomplete (STOP_NON_RETRYABLE)) | — | descriptive tier: not classified (incomplete (STOP_NON_RETRYABLE)) |
| sol:ptr_art5-ptr_hyb5 | +7.3 | \[+4.0, +10.7\] | \[+3.0, +12.3\] | .0002 | own p | .0022 | descriptive tier: supported (estimate \>= +5, adjusted lower bound \> 0) |
| sol:ptr_art5-ptr_dense5 | +7.0 | \[+4.0, +10.3\] | \[+2.7, +11.7\] | .0001 | own p | .0012 | descriptive tier: supported (estimate \>= +5, adjusted lower bound \> 0) |
| sol:ptr_regex-ptr_art5 | +3.3 | \[+1.3, +5.7\] | \[+0.7, +7.0\] | .0040 | own p | .0320 | descriptive tier: inconclusive |
| msp:ptr_art5-ptr_hyb5 | +7.0 | \[+4.0, +10.3\] | \[+2.7, +12.0\] | .0002 | own p | .0022 | descriptive tier: supported (estimate \>= +5, adjusted lower bound \> 0) |
| msp:ptr_art5-ptr_dense5 | +5.7 | \[+2.3, +9.3\] | \[+0.7, +11.3\] | .0045 | own p | .0320 | descriptive tier: supported (estimate \>= +5, adjusted lower bound \> 0) |
| msp:ptr_regex-ptr_art5 | +1.7 | \[+0.0, +3.3\] | \[−0.7, +4.3\] | .1267 | own p | .7403 | descriptive tier: practically equal (adjusted interval inside +-5) |

**F3 supports no count-versus-identity interpretation.** As registered, F3 is reported only as numbers and descriptive tiers (Table B4.5). It supports no conclusion about whether the count, the note length, or the identity of the named sessions drives the premium, and no comparison between readers; its tiers are never confirmatory and never pooled with the primary family. The art5 arm’s three non-gold sessions are one hash draw per scenario (they overlap hybrid-5’s sets in 77 and dense-5’s in 78 session slots over the 300 probes), so another draw could give other values.

#### B.4.6. Descriptive results

**Table B4.6. Accuracy (%) by reader and arm under the binding GPT-6.1 Sol judge.** Descriptive; not a ranking. Values verbatim; the g38 row label is annotated. The three complete readers have 300 probes per cell, and Muse Spark 1.3’s reader-terminal units count as incorrect. The g38 row rests on 39 to 45 scored probes per arm and is not interpreted; S19b’s complete Gemini 3.8 Flash row, from fresh reads, is Table B5.6. The sol row is judged by the reader’s own model family. None of these rows is comparable with the GLM-5.3-Flash-judged S10c accuracies in B.2. The main paper’s Table 5 reprints the generic instruction, hybrid-2, dense-2, and artifact pointer columns, with Gemini 3.8 Flash’s row from S19b.

| Reader | Plain | Generic instruction | Hybrid-5 | Dense-5 | Artifact pointer | Oracle note | Hybrid-2 | Dense-2 | Gold-pair-plus-three |
|----|----|----|----|----|----|----|----|----|----|
| glm | 51.0 | 75.3 | 79.0 | 80.0 | 91.0 | 98.0 | 70.0 | 72.0 | 82.7 |
| g38 (partial: 39–45 scored probes per arm; not interpreted) | 66.7 | 95.0 | 75.0 | 76.9 | 93.3 | 97.8 | 65.9 | 75.0 | 90.9 |
| sol (judged by its own family) | 66.7 | 89.7 | 86.3 | 86.7 | 97.0 | 99.7 | 78.0 | 80.3 | 93.7 |
| msp | 71.7 | 92.3 | 90.0 | 91.3 | 98.7 | 99.3 | 83.0 | 85.7 | 97.0 |

**Two-session comparators against no pointer (95% scenario bootstrap, uncorrected).** For the three complete readers, the two-session retrieval pointers score above plain but below the generic instruction. In the reader order GLM-5.3-Flash, GPT-6.1 Sol, and Muse Spark 1.3, hybrid-2 − plain is +19.0 \[+13.3, +24.7\], +11.3 \[+6.3, +16.3\], and +11.3 \[+6.7, +16.0\], and dense-2 − plain is +21.0 \[+14.7, +27.3\], +13.7 \[+8.3, +19.3\], and +14.0 \[+8.3, +19.7\]. In the same order, hybrid-2 − generic instruction is −5.3 \[−10.7, −0.3\], −11.7 \[−17.7, −6.0\], and −9.3 \[−13.3, −5.7\], and dense-2 − generic instruction is −3.3 \[−8.7, +1.7\], −9.3 \[−15.0, −3.3\], and −6.7 \[−11.0, −2.3\]. Only GLM-5.3-Flash’s dense-2 − generic interval includes 0.

**Table B4.7. Budget-matched premium by pointer geometry.** Rows verbatim; each cell gives the number of probes and $D$ in points; descriptive and uncorrected. Each column classifies a probe by the two sessions that hybrid-2 or dense-2 names for it, where NEW and OLD are the newer and older gold sessions. “Both gold”: NEW and OLD, that is, the gold pair; the read is then shared with the artifact pointer arm, so $D$ is judge noise plus possible halo. “NEW + non-gold”: NEW and one non-gold session. “OLD + earlier” and “OLD + later”: OLD and one non-gold session that comes before or after OLD in the history. “Neither”: two non-gold sessions. “Set is not the gold pair”: the four preceding categories together. A dash marks a cell without scored probes.

| Reader | Pointer | Both gold | NEW + non-gold | OLD + earlier | OLD + later | Neither | Set is not the gold pair |
|----|----|----|----|----|----|----|----|
| glm | ptr_hyb2 | 105, −2.2 | 25, +4.0 | 30, +69.6 | 115, +28.3 | 25, +20.8 | 195, +25.7 |
| glm | ptr_dense2 | 140, −0.9 | 23, +22.7 | 19, +64.3 | 91, +31.5 | 27, +22.2 | 160, +30.8 |
| g38 | ptr_hyb2 | 105, +0.0 | 25, +0.0 | 30, +75.0 | 115, +33.3 | 25, +0.0 | 195, +37.5 |
| g38 | ptr_dense2 | 140, +0.0 | 23, — | 19, — | 91, +41.7 | 27, +0.0 | 160, +31.7 |
| sol | ptr_hyb2 | 105, +0.8 | 25, +12.0 | 30, +32.6 | 115, +31.6 | 25, +12.5 | 195, +24.5 |
| sol | ptr_dense2 | 140, +0.0 | 23, +9.1 | 19, +53.6 | 91, +34.0 | 27, +18.5 | 160, +27.4 |
| msp | ptr_hyb2 | 105, +0.0 | 25, +12.0 | 30, +46.4 | 115, +19.3 | 25, +27.1 | 195, +22.1 |
| msp | ptr_dense2 | 140, +0.0 | 23, +13.6 | 19, +35.7 | 91, +19.8 | 27, +37.0 | 160, +20.9 |

Where the set is not the gold pair (195 probes for hybrid-2 and 160 for dense-2), the complete readers’ premium is +20.9 to +30.8 points; in the “both gold” cells it is −2.2 to +0.8 (Table B4.7). The probe counts are the planned counts; for Gemini 3.8 Flash the $D$ values rest only on the few probes read before the stop. By point estimate, the “OLD + earlier” cells are the largest in five of the six complete-reader rows. The cells are small, however, and except in GLM-5.3-Flash’s hybrid-2 row, the largest cell’s 95% interval overlaps another cell’s (for example, GPT-6.1 Sol’s hybrid-2 row has +32.6 \[+17.4, +50.0\] for “OLD + earlier” against +31.6 \[+22.5, +41.5\] for “OLD + later”); no ordering of cells is claimed.

**Table B4.8. Judge consistency on shared-answer probes.** Rows verbatim; registered as a descriptive diagnostic that decides no verdict. On a shared-answer probe, one answer is judged twice, once in each arm’s judge call. Each cell gives the number of such probes, the number on which the two verdicts differ, and the signed count: (artifact pass, comparator fail) minus (comparator pass, artifact fail). “Identical request”: the whole judge request is byte-identical in both arms.

| Reader | Pointer | Identical request: n / discordant / signed | Different request: n / discordant / signed |
|----|----|----|----|
| glm | ptr_hyb2 | 24 / 2 / 2 | 81 / 2 / −2 |
| glm | ptr_dense2 | 63 / 1 / 1 | 77 / 1 / −1 |
| g38 | ptr_hyb2 | 11 / 0 / 0 | 3 / 0 / 0 |
| g38 | ptr_dense2 | 17 / 0 / 0 | 5 / 0 / 0 |
| sol | ptr_hyb2 | 24 / 0 / 0 | 81 / 1 / 1 |
| sol | ptr_dense2 | 63 / 0 / 0 | 77 / 0 / 0 |
| msp | ptr_hyb2 | 24 / 0 / 0 | 81 / 0 / 0 |
| msp | ptr_dense2 | 63 / 0 / 0 | 77 / 0 / 0 |

On byte-identical requests, the judge disagrees with itself on two of 24 (hybrid-2) and one of 63 (dense-2) GLM-5.3-Flash probes; the different-request discordances go the other way, so the net is zero (Table B4.8). Copying one verdict to both arms of a shared-answer probe leaves GLM-5.3-Flash’s two budget-matched $D$ values unchanged (+21.0 and +19.0), moves GPT-6.1 Sol’s hybrid-2 $D$ from +19.0 to +18.7, and changes no other contrast.

#### B.4.7. Planned differences from S10c, and S10c’s registered values

**Table B4.9. Planned differences from S10c.** Adapted from section O of S19’s registration annex, as reprinted in the S19 report. The stages row is paraphrased, and judge calls and concurrent requests are named as in this paper. Labels follow the B.4 legend; flash-lite is Gemini 3.5 Flash-Lite, T is the temperature, and hyb2 and dense2 are hybrid-2 and dense-2.

| Topic | S10c | S19 |
|----|----|----|
| Readers and settings | glm max, T 0; g38 medium, T 1.0; flash-lite T 0 | four readers at “high”, T 1.0 |
| Binding judge | GLM (T 0) | GPT-6.1 Sol at medium, one judge call per reader, arm, and scenario; GLM descriptive (byte-identical requests judged once) |
| Arms | 9 core + 2 exposure | 9 (6 inherited + hyb2, dense2, and art5) |
| Identical prompts | separate draws | one read per distinct request; verdicts per judge call |
| Order | fixed | 18-row odd-n Williams design over 9 arms, validation scenarios first |
| Concurrency | 1 request at a time per paid model | up to 10 concurrent requests per reader part, ramped; one part per provider at a time |
| Stages | dev 12 scenarios + dev gate | pre-study pilot and reader supplement |
| Terminal units | incorrect for paid readers, missing for GLM | incorrect for every reader; ≤ 6 lifetime sends per unit |
| Output caps and recovery | g38 16,384; glm 32,768; up to 2 recoveries | per reader, C1 → C2: glm 9,216 → 18,432, g38 16,384 → 32,768, sol 3,584 → 7,168, msp 8,192 → 16,384; one escalation; runtime transport resends |
| Bootstrap | 10,000 | 100,000 for the primary family |
| Families | primary Holm 4; secondary Holm 8 | primary Holm 16; secondary 4 + 8 + F3 12 |
| Validation | 87 items per stage, gate | 72 items at test (determinate bar), gate scored after the reads |

The binding judge, the reader settings, and the handling of terminal units differ from S10c’s (Table B4.9), so S19’s five-session values are not directly comparable with S10c’s $D$ values, and S19 does not redecide S10c; S10c’s rows, families, and tiers stay registered history. For example, the GPT-6.1 Sol judge passed fewer of S10c’s pointer answers than the GLM-5.3-Flash judge in every cell (C.4). For reference only, S10c’s registered Gemini 3.8 Flash contrasts (at medium thinking, under the GLM-5.3-Flash judge) are in B.2. S10c’s descriptive GLM-5.3-Flash anchor contrasts, outside both S10c families, were +13.7 \[+9.7, +18.0\] for artifact pointer − hybrid-5 and +10.3 \[+6.7, +14.3\] for artifact pointer − dense-5. The registered cross-run comparisons are reported descriptively in B.4.11 and B.5.11. S19’s partial Gemini 3.8 Flash comparison remains uninterpreted; S19b has its own comparison, which does not replace it.

#### B.4.8. Deviations and review scope

Design choices disclosed before the freeze included four readers after two removals, pilot-based output caps, a gate scored after the reads, one read per distinct request, and 100,000 primary bootstrap resamples. Reporting-only amendments recorded the Gemini 3.8 Flash stop and operational exceptions; they introduced no new result population or inferential rule. A further check of the build ran after the freeze and cannot approve the frozen build retrospectively.

Two separate recomputations from the saved outputs reproduced the frozen analysis. The first reproduced it byte for byte and checked the exact contrasts, accuracy cells, and gate figures. The second, a separate implementation that took only its random-number and rounding conventions from the study code, reproduced the registered contrasts, intervals, p values, tiers, accuracy cells, and gate. The other geometry and sensitivity outputs rest on the first recomputation’s byte-identical replay. One further recomputation checked the later secondary outputs (B.4.11).

#### B.4.9. Accounting scope

Administrative cost and token logs are omitted from this appendix. Recorded usage is an accounting observation, not a provider invoice or a scientific performance result.

#### B.4.10. Limitations and what S19 does not show

- The test split is reused, and the two-session direction was predictable; S19 measures the size of the premium as conditional robustness, never a fresh confirmation.
- Outcomes are LLM-judged by GPT-6.1 Sol. The gate is LLM adjudication on 72 items, not human validation, and its packet holds no failing artifact-arm answer.
- The GPT-6.1 Sol judge scores its own model family’s reader. A uniform leniency toward that reader cancels to first order in its within-reader $D$; an arm-dependent leniency would not. The registered self-preference diagnostic is descriptive, keeps its partial Gemini 3.8 Flash baseline, and is not adjusted for multiplicity (B.4.11).
- Each reader read each distinct request once, so every cell is one draw. On shared-answer probes, $D$ is judge noise plus possible halo.
- “High” is a vendor label; nothing here compares the readers’ reasoning, and Table B4.6 is not a ranking. S19 tests no reader equivalence.
- The Gemini 3.8 Flash part stopped, so S19 has no result for that reader at its high setting; the separately registered successor S19b supplies one (B.5).
- Matching the pointer count and note does not match the returned-evidence tokens or the probability of complete support.
- A wrong two-session pointer can actively misdirect, because the note marks the later named session as current (hybrid-2 and dense-2 omit the newer gold session in 170 and 137 of 300 probes). $D$ does not separate missing evidence from that misdirection.
- F3 supports no count-versus-identity interpretation and no comparison between readers (B.4.5).
- S19 does not test cue reliance. It contains no arm that scans the history with an LLM, so the artifact pointer is never compared with an LLM-based history scan. It shows nothing about whether any memory system in the literature exploits the artifact, says nothing about retrieval in general, and does not redecide S10c.

<a id="appendix-b4-secondary"></a>

#### B.4.11. Registered secondary judge and cross-run analyses (descriptive)

The GLM-5.3-Flash secondary judge used the registered S10c template at temperature 0. Its offline analysis of 12 October 2026 leaves S19’s binding primary family, gate, reader statuses, and k-of-n outputs exactly as they were, and it neither repeats the binding gate nor introduces new tiers. The GLM-5.3-Flash judge scores its own model family’s reader. S19’s Gemini 3.8 Flash run remains “incomplete (STOP_NON_RETRYABLE)”, and no S19b answers or judgments replace its partial data.

**Table B4.10. Agreement between the binding GPT-6.1 Sol judge and the secondary GLM-5.3-Flash judge.** Paired observed outcomes across all nine arms. A count below 2,700 means that some outcomes lack a verdict from one of the judges; for example, one exhausted secondary judge call on GLM-5.3-Flash answers leaves three answered outcomes without a secondary verdict. The Gemini 3.8 Flash run is partial.

| Reader                             | Paired outcomes | Agreement (%) | Cohen’s κ |
|------------------------------------|----------------:|--------------:|----------:|
| GLM-5.3-Flash                      |           2,697 |         95.29 |      .857 |
| Gemini 3.8 Flash (partial S19 run) |             382 |         97.64 |      .917 |
| GPT-6.1 Sol                        |           2,700 |         96.44 |      .834 |
| Muse Spark 1.3                     |           2,692 |         98.14 |      .887 |

On the original 72-item packet with its adjudicator labels, the secondary judge agrees on 71 of 72 items (98.61%; κ .948), with no missing or ambiguous adjudicator label. This descriptive comparison has no PASS gate of its own, and it neither revalidates nor replaces the unchanged binding gate; no new adjudicator labels were requested.

**Table B4.11. Primary contrasts under the secondary GLM-5.3-Flash judge (descriptive point estimates).** $D$ is the artifact pointer minus the comparator, in points, from the registered scenario-mean paired estimator. These values confirm no primary tier. GLM-5.3-Flash’s dense-5 contrast covers 99 scenarios (297 paired probes), and the other complete-reader contrasts cover 100 scenarios (300 probes). The partial Gemini 3.8 Flash values cover 14 to 16 scenarios, remain uninterpreted, and support no claim for a completed reader.

| Reader                             | Hybrid-2 | Dense-2 | Hybrid-5 | Dense-5 |
|------------------------------------|---------:|--------:|---------:|--------:|
| GLM-5.3-Flash                      |   +22.00 |  +18.67 |   +11.33 |  +11.45 |
| Gemini 3.8 Flash (partial S19 run) |   +30.21 |  +21.88 |   +17.86 |  +20.24 |
| GPT-6.1 Sol                        |   +17.00 |  +14.00 |    +8.67 |   +9.00 |
| Muse Spark 1.3                     |   +14.67 |  +12.33 |    +7.67 |   +6.33 |

**Exploratory self-preference diagnostic.** For each reader, the gap is the binding GPT-6.1 Sol pass rate minus the secondary GLM-5.3-Flash pass rate. The registered contrast is the GPT-6.1 Sol reader’s gap minus the mean gap of the Gemini 3.8 Flash and Muse Spark 1.3 readers; a positive value would indicate that the binding judge favors its own model family’s reader. It is −1.27 points, with an ordinary 95% scenario-bootstrap interval of \[−2.44, −0.20\] over 100 scenarios (10,000 resamples). The registered implementation pools the available Gemini 3.8 Flash and Muse Spark 1.3 arm–probe gaps within each scenario. The baseline includes partial S19 Gemini 3.8 Flash data, 382 paired outcomes from only 17 of the 100 scenarios; it is neither replaced by S19b data nor reweighted to omit that reader. No multiplicity correction or inferential tier applies. The negative descriptive estimate establishes neither a general absence of self-preference nor the absence of arm-dependent bias, and it does not show that the labels are correct.

**Table B4.12. GLM-5.3-Flash reader: S10c against S19 under the same GLM-5.3-Flash judge settings.** The same judge settings score each run’s own answers. Differences are S19 minus S10c, in points; they are descriptive paired accuracy differences, not a rerun of S10c’s registered contrasts. The reader’s temperature and reasoning setting, the order, the terminal-unit rules, and the other protocol differences of B.4.7 remain confounded with the run.

| Arm | Paired probes | S10c accuracy (%) | S19 accuracy (%) | S19 − S10c (points) |
|----|---:|---:|---:|---:|
| Plain | 300 | 66.00 | 55.00 | −11.00 |
| Generic instruction | 300 | 82.00 | 78.33 | −3.67 |
| Hybrid-5 | 300 | 84.33 | 83.00 | −1.33 |
| Dense-5 | 297 | 87.54 | 82.83 | −4.71 |
| Artifact pointer | 300 | 98.00 | 94.33 | −3.67 |
| Oracle note | 300 | 100.00 | 99.33 | −0.67 |

The raw analysis output also keeps the partial S19 Gemini 3.8 Flash cross-run rows (39–45 paired outcomes); they do not complete the stopped run and are not interpreted here. The successor’s separate comparison is in B.5.11. All these analyses use answers on the reused split whose outcomes had already been seen. A separate recomputation from the saved outputs matched every registered secondary output to within $10^{-12}$ (absolute) and checked its sources and the completeness of the judge calls.

### B.5. S19b: the Gemini 3.8 Flash successor of S19, completing S19’s families

S19’s Gemini 3.8 Flash part stopped before any of its contrasts could be classified (B.4.2), and a stop is never resumed. S19b is the separately registered successor for that one reader: Gemini 3.8 Flash at its vendor’s “high” setting, on S10c’s reused test split, with S19’s arms, prompts, prompt builders, and binding judge, its own fresh validation gate, and its own runtime (v5). It completed S19’s registered families with S19’s recorded entries, so Gemini 3.8 Flash’s adjusted p values are the ones S19’s families would have given it, and it redecides nothing of S19. The completed families therefore join two runs: S19’s run (2026-10-05, runtime v4) for GLM-5.3-Flash, GPT-6.1 Sol, and Muse Spark 1.3, and S19b’s run (2026-10-06, runtime v5) for Gemini 3.8 Flash. This is conditional robustness on a reused split, never a fresh confirmation. Every outcome was judged by an LLM (GPT-6.1 Sol), and the gate is LLM adjudication, not human validation. S19’s partial Gemini 3.8 Flash run is not interpreted here and is not compared with S19b’s.

The B.4 legend applies to the tables and quoted text of B.5. A row marked “(recorded, S19)” is one of S19’s registered entries, printed with S19’s recorded permutation p and tier and never redecided; its intervals are in the corresponding table of B.4.

#### B.5.1. Protocol card (what differs from S19)

**Card B5. S19b protocol card.** Registered definitions that differ from Card B4, condensed from S19b’s preregistration and its binding annex.

| Protocol element | Registered definition |
|----|----|
| Registration and freeze | Approved by the author on 2026-10-05 (about 23:55), after S19’s stop; registered decisions B1–B10 with two addenda (B3a, B4a, B6a–B6d, B7a, B8a, B8b, B11, and B12); frozen 2026-10-06 05:33:45 (+03:00), after a smoke pilot of runtime v5 (S19’s two-call reader stage plus one judge-pipeline call; USD 0.0485 in all). Known before registration: S19’s partial Gemini 3.8 Flash estimates on 14 to 16 scenarios (printed in S19’s report as not interpreted) had been seen, and S19’s Gemini 3.8 Flash aggregates had been read once while S19b was built. The two-session direction was predictable: hybrid-2 and dense-2 name the newer gold session in only 130 and 163 of 300 probes |
| Population | S10c’s frozen test list: 100 scenarios × 3 probes = 300 probes, already used by S10b, S10c, S17, S18, and S19. Gemini 3.8 Flash had read it in S10c and S18, and S19’s stopped part left 335 Gemini 3.8 Flash test-read rows on 17 of these scenarios; GPT-6.1 Sol had judged it before S19 and in S19. STALE is public, so pretraining exposure cannot be ruled out |
| Reader | Gemini 3.8 Flash only, `thinkingLevel` “high”, temperature 1.0 (S19’s setting); requested output caps C1 = 16,384 and C2 = 32,768 tokens, with one escalation; timeout 600 s. GLM-5.3-Flash, GPT-6.1 Sol, and Muse Spark 1.3 are recorded from S19 and were not rerun |
| Runtime | The successor’s only runtime change from S19 is Gemini’s admitted output bound, $R_{\max}$ = 65,536 total output tokens (thinking included; the model’s documented output-token limit (Google 2026)) at both requested caps, used for the budget reservation and the overrun check; an output above $R_{\max}$ still freezes the part. $R_{\max}$ is an accounting policy based on the documented maximum, not proof that the provider enforces it |
| Arms and reads | S19’s nine arms with byte-identical prompt builders (inherited prompts equal to S10c’s in 1,800 of 1,800; no leakage in 2,700 prompts). One read per distinct request: 2,375 fresh reads instead of 2,700 nominal units, with S19’s shared reads (hybrid-2 = artifact pointer in 105 probes, dense-2 = artifact pointer in 140, hybrid-2 = dense-2 in 153, and hybrid-5 = dense-5 in 17); S19’s 333 valid Gemini 3.8 Flash reads are not reused |
| Order | S19’s Williams rows and blocks per scenario; S19b’s 55 validation-packet scenarios first (S19: 53); up to 10 concurrent requests, ramped 2 → 5 → 10 |
| Binding judge | GPT-6.1 Sol at reasoning “medium”, with S19’s settings and prompt builder; 900 judge calls. It does not judge its own model family here (the reader is Google’s), so S19’s self-preference diagnostic does not apply. The GLM-5.3-Flash secondary judge is descriptive only; its completed results are in B.5.11 |
| Validation gate | A fresh blind 72-item packet of Gemini 3.8 Flash answers only (9 arms × 8), drawn with S19b’s own salt and built after the reads had closed; labeled by a fresh Claude Opus 5.5 instance (`claude-opus-5-5`) that saw no arm, reader, or outcome and was given only a copy of the packet; S19’s pass rule (at least 60 determinate items with a binding verdict, agreement ≥ .80, and finite $\kappa \geq .70$). Validity is not inherited from S19. A failed gate would have made Gemini 3.8 Flash’s primary and F3 tiers “judge-limited” without rewriting any p; it never suppresses or redecides S19’s classifications |
| Families (completed) | Primary: Holm over S19’s 16, with Gemini 3.8 Flash’s four at their own permutation p and the twelve of GLM-5.3-Flash, GPT-6.1 Sol, and Muse Spark 1.3 at S19’s recorded exact p (all 1/10,001), read from a pinned copy of S19’s frozen analysis; Bonferroni per-contrast intervals at S19’s 99.69%. Family S1: Holm over four (three recorded). Family S2: Holm over eight (six recorded). Family F3: Holm over 12 (nine recorded), Bonferroni per-contrast intervals at 99.58%, descriptive tiers only. S19’s entries keep S19’s registered decisions; their adjusted p values recomputed with Gemini 3.8 Flash’s p are descriptive |
| Estimand, inference, and tiers | S19’s: $D = \mathrm{acc}(\text{artifact}) - \mathrm{acc}(B)$ in points over 300 probes, for $B$ in hybrid-2, dense-2, hybrid-5, and dense-5; S10c’s estimator; sign-flip permutation p (10,000 draws, seed 2202); scenario bootstrap with 100,000 resamples for the primary family and 10,000 elsewhere; S19’s tiers and order of checks (integrity, claim status, gate, and tier; Card B4). The k-of-4 sentence counts S19’s three recorded classifications plus Gemini 3.8 Flash’s and is never withheld because of Gemini 3.8 Flash |
| Not licensed (registered list) | S19’s list (that count does not matter; that S10c’s premium is identity rather than count; retrieval in general; cue reliance; a deployable pointer; fresh confirmation; any model ranking; reader equivalence; human validation), plus redeciding S10c or S19 |

#### B.5.2. Coverage, health, and the output-cap change

**Table B5.1. Completeness of Gemini 3.8 Flash over the eight arms other than art5.** Row verbatim; columns as in Table B4.1.

| Reader | Status | Planned | Scored | Reader-terminal (incorrect) | Judge-terminal missing | Read unresolved | Judge unresolved | Valid (%) |
|----|----|----|----|----|----|----|----|----|
| Gemini 3.8 Flash (model id gemini-3.8-flash) | claimable | 2,400 | 2,400 | 0 | 0 | 0 | 0 | 100.0 |

All 2,375 reads and all 900 binding judge calls are valid, and the art5 arm is complete for F3 (300 of 300); no unit is reader-terminal, judge-terminal, or unresolved (Table B5.1). There was no stop and no pause. Every integrity check passed (the lock, pins, judge-template pins, reported model ids, raw-file integrity, rows matching the plan, the S10c copy, and zero harness cache hits), and neither paid part recorded a billed timeout. When the binding results were first reported, none of the GLM-5.3-Flash secondary judge’s 866 requests had yet been sent; the completed secondary analysis is in B.5.11.

**What runtime v5 changed in practice.** S19’s Gemini 3.8 Flash part stopped because one first request returned 26,700 output tokens (26,439 of them reasoning tokens) against the requested 16,384, and runtime v4 froze the part’s budget for any output above the reserved cap (B.4.2). In S19b, 35 of the 2,375 reads reached C1 on their first request and were escalated once. All 35 finished under C2 with the finish reason “STOP”, none was budget-exhausted, and no answer was cut or empty. Exactly two first requests returned more output tokens than the requested C1, 26,640 and 24,260 (finish reason “MAX_TOKENS”; counts from the metadata of the shared call ledger), both within $R_{\max}$. Under v4’s rule either would have frozen the part; under v5 both outputs were accepted. No final output exceeded C2 or $R_{\max}$ (the largest was 30,150 tokens). S19b cannot show that the S19 stop would not recur above $R_{\max}$.

#### B.5.3. Validation gate

The 72-item packet (Gemini 3.8 Flash × 9 arms × 8) was built after the reads had closed, with S19b’s own salt; no backup item was needed. The adjudicator was a fresh Claude Opus 5.5 instance (`claude-opus-5-5`) that saw no arm, reader, or outcome; it was given only a copy of the packet. Its freshness, its exclusive exposure to the packet, and its single first adjudication are attested in the study record, not checked, and the S19b report was written without opening the packet or any label. The pipeline’s pre-gate analysis, with every $D$ value, existed before the adjudication, as in S19’s registered order. The gate passed: 72 determinate items, agreement .986 (71 of 72), and κ .882, with an adjudicator pass share of 94.4% and a judge pass share of 93.1%. The one disagreement is a judge-fail, adjudicator-pass label on a hybrid-5 comparator answer. If the adjudicator is right, this judge error understates hybrid-5 accuracy and so inflates Gemini 3.8 Flash’s reported $D$ against hybrid-5; one item cannot size this bias. No disagreement involves the artifact pointer arm, and the packet holds one failing artifact-arm answer, on which the raters agree. This is LLM adjudication, not human validation.

#### B.5.4. The completed primary family and the registered sentences

**Table B5.2. Primary family, completed with S19b’s Gemini 3.8 Flash contrasts.** Rows verbatim; Holm over 16; Bonferroni per-contrast intervals at 99.69% (= 1 − .05/16); 100,000 bootstrap resamples; columns as in Table B4.2. The twelve rows marked “(recorded, S19)” are S19’s registered entries, whose intervals are in Table B4.2; their Holm p cell gives S19’s value and the value recomputed in the completed family (descriptive). The main paper’s Figure 3 plots all 16 contrasts. Perm. p is the permutation p-value.

| Contrast | $D$ (points) | 95% CI | Bonferroni per-contrast CI | Perm. p | Holm entry | Holm p | Up / down / tie | Discordant a / b | Bounds worst / best | Tier |
|----|----|----|----|----|----|----|----|----|----|----|
| glm:ptr_regex-ptr_hyb2 (recorded, S19) | +21.0 | — | — | 1/10,001 | recorded (S19) | S19 .0016; completed .0016 (descriptive) | — | — | — | supported: at least +5 asserted (S19, registered; not re-decided) |
| glm:ptr_regex-ptr_dense2 (recorded, S19) | +19.0 | — | — | 1/10,001 | recorded (S19) | S19 .0016; completed .0016 (descriptive) | — | — | — | supported: at least +5 asserted (S19, registered; not re-decided) |
| glm:ptr_regex-ptr_hyb5 (recorded, S19) | +12.0 | — | — | 1/10,001 | recorded (S19) | S19 .0016; completed .0016 (descriptive) | — | — | — | supported: at least +5 asserted (S19, registered; not re-decided) |
| glm:ptr_regex-ptr_dense5 (recorded, S19) | +11.0 | — | — | 1/10,001 | recorded (S19) | S19 .0016; completed .0016 (descriptive) | — | — | — | supported (estimate \>= +5, adjusted lower bound \> 0) (S19, registered; not re-decided) |
| g38:ptr_regex-ptr_hyb2 | +21.0 | \[+16.3, +26.0\] | \[+14.0, +28.7\] | .0001 | own p | .0016 | \[49, 0, 51\] | \[63, 0\] | \[+21.0, +21.0\] | supported: at least +5 asserted |
| g38:ptr_regex-ptr_dense2 | +18.0 | \[+13.3, +23.0\] | \[+11.3, +25.3\] | .0001 | own p | .0016 | \[41, 0, 59\] | \[54, 0\] | \[+18.0, +18.0\] | supported: at least +5 asserted |
| g38:ptr_regex-ptr_hyb5 | +12.7 | \[+8.7, +17.0\] | \[+6.7, +19.3\] | .0001 | own p | .0016 | \[31, 1, 68\] | \[39, 1\] | \[+12.7, +12.7\] | supported: at least +5 asserted |
| g38:ptr_regex-ptr_dense5 | +9.0 | \[+5.7, +12.7\] | \[+4.0, +14.7\] | .0001 | own p | .0016 | \[24, 1, 75\] | \[29, 2\] | \[+9.0, +9.0\] | supported (estimate \>= +5, adjusted lower bound \> 0) |
| sol:ptr_regex-ptr_hyb2 (recorded, S19) | +19.0 | — | — | 1/10,001 | recorded (S19) | S19 .0016; completed .0016 (descriptive) | — | — | — | supported: at least +5 asserted (S19, registered; not re-decided) |
| sol:ptr_regex-ptr_dense2 (recorded, S19) | +16.7 | — | — | 1/10,001 | recorded (S19) | S19 .0016; completed .0016 (descriptive) | — | — | — | supported: at least +5 asserted (S19, registered; not re-decided) |
| sol:ptr_regex-ptr_hyb5 (recorded, S19) | +10.7 | — | — | 1/10,001 | recorded (S19) | S19 .0016; completed .0016 (descriptive) | — | — | — | supported: at least +5 asserted (S19, registered; not re-decided) |
| sol:ptr_regex-ptr_dense5 (recorded, S19) | +10.3 | — | — | 1/10,001 | recorded (S19) | S19 .0016; completed .0016 (descriptive) | — | — | — | supported (estimate \>= +5, adjusted lower bound \> 0) (S19, registered; not re-decided) |
| msp:ptr_regex-ptr_hyb2 (recorded, S19) | +15.7 | — | — | 1/10,001 | recorded (S19) | S19 .0016; completed .0016 (descriptive) | — | — | — | supported: at least +5 asserted (S19, registered; not re-decided) |
| msp:ptr_regex-ptr_dense2 (recorded, S19) | +13.0 | — | — | 1/10,001 | recorded (S19) | S19 .0016; completed .0016 (descriptive) | — | — | — | supported: at least +5 asserted (S19, registered; not re-decided) |
| msp:ptr_regex-ptr_hyb5 (recorded, S19) | +8.7 | — | — | 1/10,001 | recorded (S19) | S19 .0016; completed .0016 (descriptive) | — | — | — | supported (estimate \>= +5, adjusted lower bound \> 0) (S19, registered; not re-decided) |
| msp:ptr_regex-ptr_dense5 (recorded, S19) | +7.3 | — | — | 1/10,001 | recorded (S19) | S19 .0016; completed .0016 (descriptive) | — | — | — | supported (estimate \>= +5, adjusted lower bound \> 0) (S19, registered; not re-decided) |

**Completion line (registered output; the source-file reference shortened).**

> Primary: Holm over the completed family of 16 (S19b-own members: 4; recorded from S19’s frozen analysis: 12). S19’s entries keep S19’s registered decisions (B4a: never re-decided); their adjusted p recomputed with g38’s p are descriptive and on the same side of .05 as S19’s for every entry: True.

In words: for each of S19’s twelve recorded entries, the adjusted p recomputed with Gemini 3.8 Flash’s p is descriptive and falls on the same side of .05 as S19’s value.

**Registered sentences.** The six sentences below are the registered wording, generated and checked in code, and are quoted verbatim. Bracketed glosses are ours and appear at first use only.

> - On the consumed \[i.e., reused\] S10c test split, for Gemini 3.8 Flash (model id gemini-3.8-flash) at its vendor’s high setting, the artifact pointer scored +21.0 points above the top-2 hybrid retrieval pointer \[hybrid-2\] (two sessions, same note) (simultaneous \[i.e., Bonferroni per-contrast, 99.69%\] 319/320 interval \[+14.0, +28.7\]; Holm p = 0.0016): supported, at least +5 points.
> - On the consumed S10c test split, for Gemini 3.8 Flash (model id gemini-3.8-flash) at its vendor’s high setting, the artifact pointer scored +18.0 points above the top-2 dense retrieval pointer \[dense-2\] (two sessions, same note) (simultaneous 319/320 interval \[+11.3, +25.3\]; Holm p = 0.0016): supported, at least +5 points.
> - On the consumed S10c test split, for Gemini 3.8 Flash (model id gemini-3.8-flash) at its vendor’s high setting, the artifact pointer scored +12.7 points above the top-5 hybrid retrieval pointer \[hybrid-5\] (simultaneous 319/320 interval \[+6.7, +19.3\]; Holm p = 0.0016): supported, at least +5 points.
> - On the consumed S10c test split, for Gemini 3.8 Flash (model id gemini-3.8-flash) at its vendor’s high setting, the artifact pointer scored +9.0 points above the top-5 dense retrieval pointer \[dense-5\] (simultaneous 319/320 interval \[+4.0, +14.7\]; Holm p = 0.0016): supported.
> - With the number of named sessions and the note fixed at two \[i.e., both pointers name two sessions and share the artifact pointer’s 46-token note\], naming the evidence pair beat the retriever’s top two by +21.0 points for Gemini 3.8 Flash (model id gemini-3.8-flash) on the consumed S10c test split.
> - With the number of named sessions and the note fixed at two, naming the evidence pair beat the retriever’s top two by +18.0 points for Gemini 3.8 Flash (model id gemini-3.8-flash) on the consumed S10c test split.

**Registered k-of-4 sentence (quoted verbatim).**

> On the consumed S10c test split, the budget-matched premium was supported for 4 of 4 readers against the top-2 hybrid retrieval pointer and 4 of 4 against the top-2 dense retrieval pointer; recorded from S19 (hybrid / dense, S19’s registered classifications, not re-decided): GLM-5.3-Flash = supported: at least +5 asserted / supported: at least +5 asserted; GPT-6.1 Sol = supported: at least +5 asserted / supported: at least +5 asserted; Muse Spark 1.3 (standard tier) = supported: at least +5 asserted / supported: at least +5 asserted; S19b’s reader (hybrid / dense, or its status): Gemini 3.8 Flash = supported: at least +5 asserted / supported: at least +5 asserted; not run or not classified: none.

**Provenance line (registered output; the runtime module names shortened).**

> k of 4 provenance: 3 tiers recorded from S19 (glm, sol, msp; S19’s run of 2026-10-05 on the predecessor runtime) + g38 from S19b (the successor runtime).

**What the table says.** All four Gemini 3.8 Flash contrasts in Table B5.2 are “supported”. Three reach “supported, at least +5” (hybrid-2 +21.0, dense-2 +18.0, and hybrid-5 +12.7). Against dense-5 (+9.0), the Bonferroni per-contrast lower bound is exactly +4.0, so S19b cannot assert a premium of at least +5 there. All four permutation p values sit at the floor of 10,000 draws (1/10,001), so Gemini 3.8 Flash’s Holm p values are 16/10,001 (printed .0016); the completed family also leaves S19’s twelve recorded entries at 16/10,001. No scenario moved against the artifact pointer in the two-session contrasts, and one did in each five-session contrast. No outcome is missing, so the worst and best bounds equal the estimates. The k-of-4 sentence joins S19’s three recorded tiers (S19’s run, runtime v4) with Gemini 3.8 Flash’s tier from S19b (runtime v5). It is a count of registered tiers from two runs, not a pooled or comparative result, and it licenses no reader comparison or ranking.

**Descriptive companions (no tier).** On the 90 test scenarios without reader outcomes from the earlier pilot (B.1), Gemini 3.8 Flash’s four primary $D$ values lie between +9.6 and +21.9. On the 74 scenarios that S10b’s Gemini 3.5 Flash-Lite reader did not read, they lie between +9.9 and +21.6 (point estimates only).

#### B.5.5. Secondary families

**Table B5.3. Family S1 (generic instruction minus plain), completed.** Rows verbatim; Holm over four; 95% intervals; the only registered decision is Holm p \< .05. For a recorded row, the permutation p is S19’s exact count out of 10,001, and the Holm p cell gives S19’s value and the recomputed, descriptive value.

| Contrast | $D$ | 95% CI | Permutation p | Holm p | Holm p \< .05 |
|----|----|----|----|----|----|
| glm:generic-plain (recorded, S19) | +24.3 | — | 1/10,001 | S19 .0004; completed .0004 (descriptive) | True (S19, registered; not re-decided) |
| g38:generic-plain | +27.3 | \[+22.3, +32.3\] | .0001 | .0004 | True |
| sol:generic-plain (recorded, S19) | +23.0 | — | 1/10,001 | S19 .0004; completed .0004 (descriptive) | True (S19, registered; not re-decided) |
| msp:generic-plain (recorded, S19) | +20.7 | — | 1/10,001 | S19 .0004; completed .0004 (descriptive) | True (S19, registered; not re-decided) |

Holm runs over the completed family of four: one S19b member and three entries recorded from S19’s frozen analysis. Recomputed with Gemini 3.8 Flash’s p, the adjusted p of every recorded entry is descriptive and stays on the same side of .05 as S19’s, and S19’s decisions stand (decision B4a). For Gemini 3.8 Flash, the generic instruction scores +27.3 points above plain (Table B5.3; Holm p = .0004 = 4/10,001); S19’s three recorded entries stay at 4/10,001. No tier applies.

**Table B5.4. Family S2 (two-session minus five-session pointer), completed.** Rows verbatim; Holm over eight; 95% intervals; the only registered decision is Holm p \< .05. Recorded rows as in Table B5.3.

| Contrast | $D$ | 95% CI | Permutation p | Holm p | Holm p \< .05 |
|----|----|----|----|----|----|
| glm:ptr_hyb2-ptr_hyb5 (recorded, S19) | −9.0 | — | 12/10,001 | S19 .0072; completed .0050 (descriptive) | True (S19, registered; not re-decided) |
| glm:ptr_dense2-ptr_dense5 (recorded, S19) | −8.0 | — | 58/10,001 | S19 .0290; completed .0174 (descriptive) | True (S19, registered; not re-decided) |
| g38:ptr_hyb2-ptr_hyb5 | −8.3 | \[−12.7, −4.3\] | .0006 | .0036 | True |
| g38:ptr_dense2-ptr_dense5 | −9.0 | \[−13.3, −4.7\] | .0002 | .0016 | True |
| sol:ptr_hyb2-ptr_hyb5 (recorded, S19) | −8.3 | — | 10/10,001 | S19 .0070; completed .0050 (descriptive) | True (S19, registered; not re-decided) |
| sol:ptr_dense2-ptr_dense5 (recorded, S19) | −6.3 | — | 77/10,001 | S19 .0308; completed .0174 (descriptive) | True (S19, registered; not re-decided) |
| msp:ptr_hyb2-ptr_hyb5 (recorded, S19) | −7.0 | — | 5/10,001 | S19 .0040; completed .0035 (descriptive) | True (S19, registered; not re-decided) |
| msp:ptr_dense2-ptr_dense5 (recorded, S19) | −5.7 | — | 85/10,001 | S19 .0308; completed .0174 (descriptive) | True (S19, registered; not re-decided) |

Holm runs over the completed family of eight: two S19b members and six entries recorded from S19’s frozen analysis. For Gemini 3.8 Flash, the top two sessions score below the top five, by 8.3 points for the hybrid retriever (Holm p = .0036) and 9.0 points for the dense retriever (Holm p = .0016; Table B5.4). Recomputed with Gemini 3.8 Flash’s p, the adjusted p values of S19’s six recorded entries fall (for example, GLM-5.3-Flash’s dense contrast moves from .0290 to .0174) and stay on the same side of .05. These recomputed values are descriptive, and S19’s decisions stand (decision B4a). As in B.4.5, the arms differ in count, note, and identity at once, which family S2 does not separate.

**Table B5.5. Family F3 (gold-pair-plus-three), completed.** Rows verbatim; Holm over 12 across readers; Bonferroni per-contrast intervals at 99.58% (= 1 − .05/12); descriptive tiers, never confirmatory; recorded rows as in Table B5.3. F3’s claim status under its own completeness rule over the art5 arm (rule C-3; verbatim): g38 = claimable.

| Contrast | $D$ | 95% CI | Bonferroni per-contrast CI | Permutation p | Holm entry | Holm p | Descriptive tier |
|----|----|----|----|----|----|----|----|
| glm:ptr_art5-ptr_hyb5 (recorded, S19) | +3.7 | — | — | 1,234/10,001 | recorded (S19) | S19 .7403; completed .3702 (descriptive) | descriptive tier: inconclusive (S19, registered; not re-decided) |
| glm:ptr_art5-ptr_dense5 (recorded, S19) | +2.7 | — | — | 3,087/10,001 | recorded (S19) | S19 1.0000; completed .3702 (descriptive) | descriptive tier: inconclusive (S19, registered; not re-decided) |
| glm:ptr_regex-ptr_art5 (recorded, S19) | +8.3 | — | — | 2/10,001 | recorded (S19) | S19 .0022; completed .0020 (descriptive) | descriptive tier: supported (estimate \>= +5, adjusted lower bound \> 0) (S19, registered; not re-decided) |
| g38:ptr_art5-ptr_hyb5 | +9.0 | \[+5.3, +13.0\] | \[+3.7, +14.7\] | .0001 | own p | .0012 | descriptive tier: supported (estimate \>= +5, adjusted lower bound \> 0) |
| g38:ptr_art5-ptr_dense5 | +5.3 | \[+2.7, +8.3\] | \[+1.3, +9.7\] | .0002 | own p | .0020 | descriptive tier: supported (estimate \>= +5, adjusted lower bound \> 0) |
| g38:ptr_regex-ptr_art5 | +3.7 | \[+1.0, +6.7\] | \[+0.0, +8.3\] | .0257 | own p | .1028 | descriptive tier: inconclusive |
| sol:ptr_art5-ptr_hyb5 (recorded, S19) | +7.3 | — | — | 2/10,001 | recorded (S19) | S19 .0022; completed .0020 (descriptive) | descriptive tier: supported (estimate \>= +5, adjusted lower bound \> 0) (S19, registered; not re-decided) |
| sol:ptr_art5-ptr_dense5 (recorded, S19) | +7.0 | — | — | 1/10,001 | recorded (S19) | S19 .0012; completed .0012 (descriptive) | descriptive tier: supported (estimate \>= +5, adjusted lower bound \> 0) (S19, registered; not re-decided) |
| sol:ptr_regex-ptr_art5 (recorded, S19) | +3.3 | — | — | 40/10,001 | recorded (S19) | S19 .0320; completed .0240 (descriptive) | descriptive tier: inconclusive (S19, registered; not re-decided) |
| msp:ptr_art5-ptr_hyb5 (recorded, S19) | +7.0 | — | — | 2/10,001 | recorded (S19) | S19 .0022; completed .0020 (descriptive) | descriptive tier: supported (estimate \>= +5, adjusted lower bound \> 0) (S19, registered; not re-decided) |
| msp:ptr_art5-ptr_dense5 (recorded, S19) | +5.7 | — | — | 45/10,001 | recorded (S19) | S19 .0320; completed .0240 (descriptive) | descriptive tier: supported (estimate \>= +5, adjusted lower bound \> 0) (S19, registered; not re-decided) |
| msp:ptr_regex-ptr_art5 (recorded, S19) | +1.7 | — | — | 1,267/10,001 | recorded (S19) | S19 .7403; completed .3702 (descriptive) | descriptive tier: practically equal (adjusted interval inside +-5) (S19, registered; not re-decided) |

Holm runs over the completed family of 12: three S19b members and nine entries recorded from S19’s frozen analysis. Recomputed with Gemini 3.8 Flash’s p, every recorded entry’s adjusted p is descriptive and stays on the same side of .05 as S19’s.

**Gemini 3.8 Flash’s F3 rows.** They carry descriptive tiers only (Table B5.5): art5 − hybrid-5 (+9.0) and art5 − dense-5 (+5.3) receive “supported (estimate \>= +5, adjusted lower bound \> 0)”, and artifact pointer − art5 (+3.7; Bonferroni per-contrast lower bound exactly 0.0) receives “inconclusive”. The restrictions of B.4.5 apply unchanged: F3 supports no count-versus-identity interpretation and no comparison between readers, and the art5 sets are S19’s single hash draw per scenario. The S19b report’s point-estimate decomposition of the primary $D$ is not reproduced here.

#### B.5.6. Descriptive results

**Table B5.6. Accuracy (%) of Gemini 3.8 Flash by arm under the binding GPT-6.1 Sol judge.** Descriptive; not a ranking. Values verbatim; arm headers as in Table B4.6. One reader, 300 probes per cell. The row is not comparable with the GLM-5.3-Flash-judged S10c accuracies in B.2 or with S19’s partial row in Table B4.6, which is not interpreted. The main paper’s Table 5 uses this row for Gemini 3.8 Flash.

| Reader | Plain | Generic instruction | Hybrid-5 | Dense-5 | Artifact pointer | Oracle note | Hybrid-2 | Dense-2 | Gold-pair-plus-three |
|----|----|----|----|----|----|----|----|----|----|
| g38 | 64.3 | 91.7 | 83.0 | 86.7 | 95.7 | 99.0 | 74.7 | 77.7 | 92.0 |

**Two-session comparators against no pointer (95% scenario bootstrap, uncorrected).** The two-session retrieval pointers score above plain but below the generic instruction: hybrid-2 − plain is +10.3 \[+4.3, +16.3\], dense-2 − plain +13.3 \[+7.7, +19.3\], hybrid-2 − generic instruction −17.0 \[−22.0, −12.0\], and dense-2 − generic instruction −14.0 \[−19.0, −9.0\]. The generic instruction closes 78.8% \[69.2, 88.7\] of the oracle − plain gap of 34.7 points.

**Table B5.7. Budget-matched premium of Gemini 3.8 Flash by pointer geometry.** Rows verbatim; each cell gives the number of probes and $D$ in points; descriptive and uncorrected. Columns as defined in Table B4.7.

| Reader | Pointer | Both gold | NEW + non-gold | OLD + earlier | OLD + later | Neither | Set is not the gold pair |
|----|----|----|----|----|----|----|----|
| g38 | ptr_hyb2 | 105, +0.0 | 25, +12.0 | 30, +47.8 | 115, +33.3 | 25, +29.2 | 195, +30.6 |
| g38 | ptr_dense2 | 140, +1.4 | 23, +22.7 | 19, +64.3 | 91, +25.9 | 27, +37.0 | 160, +30.6 |

In the “both gold” cells, $D$ (+0.0 and +1.4) is judge noise plus possible halo. Where the set is not the gold pair (195 probes for hybrid-2 and 160 for dense-2), the premium is +30.6 in both rows (Table B5.7). The “OLD + earlier” cells are the largest by point estimate (30 and 19 probes: +47.8 \[+30.4, +65.2\] and +64.3 \[+42.9, +82.1\]), but the cells are small and their intervals overlap other cells’. No ordering of cells is claimed, and the premium can include misdirection by a wrong pointer, not only missing evidence (B.4.10).

**Table B5.8. Judge consistency on Gemini 3.8 Flash’s shared-answer probes.** Rows verbatim; registered as a descriptive diagnostic that decides no verdict; columns as in Table B4.8.

| Reader | Pointer | Identical request: n / discordant / signed | Different request: n / discordant / signed |
|----|----|----|----|
| g38 | ptr_hyb2 | 24 / 0 / 0 | 81 / 0 / 0 |
| g38 | ptr_dense2 | 63 / 0 / 0 | 77 / 1 / 1 |

On byte-identical requests, the judge never disagrees with itself (24 and 63 probes); on different requests, it disagrees on none of 81 hybrid-2 probes and on one of 77 dense-2 probes, in the artifact pointer’s favor (Table B5.8). Copying one verdict to both arms of each shared-answer probe leaves the hybrid-2 $D$ at +21.0 and moves the dense-2 $D$ from +18.0 to +17.7 (one probe). The self-preference diagnostic does not apply, because S19b has no GPT-6.1 Sol reader; S19’s own diagnostic is reported in B.4.11 without S19b data.

#### B.5.7. Planned differences from S19, and S10c’s values

S19’s planned differences from S10c (Table B4.9) apply to S19b. S19b’s own planned differences from S19 are registered in section O of its registration annex (Table B5.9).

**Table B5.9. Planned differences from S19.** Condensed from section O of S19b’s registration annex, which is titled “Deviations from S19” and is reprinted in the S19b report. Rows on budget sub-caps, freeze ids, pinned predecessor inputs, and spend are omitted, and the runtime and pilot rows are paraphrased. Labels follow the B.4 legend; the ids in parentheses are S19b’s registered decisions and annex sections.

| Topic | S19 | S19b |
|----|----|----|
| Readers | glm, g38, sol, msp | g38 only (B1); S19’s other three recorded |
| Runtime | runtime v4, pinned | runtime v5, pinned (B3, B3a); $R_{\max}$ = 65,536 checked against the pinned module’s own bound; the module is imported only after its bytes match the pin (C2, C3) |
| Gemini accounting | reservation at the requested cap | at $R_{\max}$ on every budget path, including the token-based forecast (C3; B3a) |
| Families | 16 / 4 / 8 / 12, own members | the same families, completed with S19’s recorded members (B4); the recomputed S2 and F3 adjusted p of S19’s entries descriptive, S19’s decisions kept (B4a; F2) |
| Validation packet | 4 readers × 9 arms × 2, S19’s salt | g38 × 9 arms × 8, S19b’s own salt (B6, B6d) |
| Gate failure | the primary and F3 tiers judge-limited; S1 and S2 rows unmarked | g38’s primary and F3 tiers judge-limited; g38’s S1 and S2 rows keep their Holm decision, marked “judge validation failed”; no p rewritten; S19’s classifications never suppressed (B6a, B6b; D7) |
| Run order | S19’s 53 packet scenarios first | S19b’s 55 packet scenarios first (scenario plans identical; B6d) |
| Pilot | pre-study and S19 pilots | a two-call smoke check of runtime v5 (B8) |
| Self-preference | gap(sol) − mean gap(g38, msp) | not applicable (no sol reader) |
| Freeze gate | ready for freeze + decision ids | also the smoke pilot passed within its plan, or “B8-override: \<reason\>” (A4; F4) |
| k-of-n withholding | withheld when integrity fails for all four readers | never withheld because of g38: S19’s recorded classifications printed and g38’s status named (B6c; H) |

The Gemini 3.8 Flash reader ran at “medium” in S10c and at “high” here, under a different binding judge. S19b’s five-session values are therefore not directly comparable with S10c’s registered Gemini 3.8 Flash values (B.2: +14.0 against hybrid-5 and +7.0 against dense-5), and S19b redecides nothing of S10c. The registered S10c-versus-S19b comparison for Gemini 3.8 Flash is reported descriptively in B.5.11.

#### B.5.8. Deviations and review scope

S19b is a separate successor, informed by S19’s outcomes, with a fresh gate and one reader. Its runtime change admits the documented Gemini output maximum, while the inherited S19 decisions remain fixed. The planned separate review of the build ran after the freeze instead of before it, a signed deviation from the registered order (decision B10). Reporting-only amendments documented that a latent accounting defect had no effect on this run’s recorded budget projection or stop; no frozen efficacy rule was repaired.

Two separate recomputations from the saved outputs checked the results. The first reproduced the original analysis, the completed families, and the tracing of each value to its source. The second reproduced the ten new contrasts in the completed families, the accuracy cells, the sensitivities, the completeness counts, and the gate, and it led to documentary corrections. It did not establish provider invoices, the completeness of the exposure history, or every descriptive geometry interval. One further recomputation checked the later secondary outputs (B.5.11).

#### B.5.9. Accounting scope

Administrative cost and token logs are omitted. Recorded usage is an accounting estimate, not a provider invoice.

#### B.5.10. Limitations and what S19b does not show

- The test split is reused, and the direction was known (from S10c and S19’s partial estimates); S19b measures the size of one reader’s premium as conditional robustness, never a fresh confirmation.
- Outcomes are LLM-judged by GPT-6.1 Sol; the gate is LLM adjudication on 72 items, not human validation.
- With one reader and one read per distinct request, every cell is one draw, and on shared-answer probes $D$ is judge noise plus possible halo.
- Two runs: the completed families and the k-of-4 sentence join S19’s run (runtime v4) and S19b’s run (runtime v5). The count is not pooled; nothing compares or ranks the readers, and “high” is a vendor label.
- The successor runtime changes only Gemini’s admitted output bound. S19b cannot show that the S19 stop would not recur above $R_{\max}$, and $R_{\max}$ is a documented maximum, not a bound shown to be enforced by the provider.
- Matching the pointer count and note does not match the returned-evidence tokens or complete support, and a wrong two-session pointer can misdirect (B.4.10).
- F3 supports no count-versus-identity interpretation and no comparison between readers (B.4.5).
- S19b does not test cue reliance. It has no arm that scans the history with an LLM, so the artifact pointer is never compared with an LLM-based history scan. It shows nothing about whether any memory system in the literature exploits the artifact, says nothing about retrieval in general, and redecides neither S10c nor S19. S19’s partial Gemini 3.8 Flash run is not interpreted and is not compared with S19b’s.

<a id="appendix-b5-secondary"></a>

#### B.5.11. Registered secondary judge and cross-run analyses (descriptive)

The GLM-5.3-Flash secondary analysis of 12 October 2026 covers all 866 current secondary judge requests and 2,700 observed outcome cells, and every answered probe has a selected verdict. The binding primary family, gate, reader status, and k-of-n output remain unchanged. The successor remains a separate registration and does not replace S19’s partial Gemini 3.8 Flash data.

The binding GPT-6.1 Sol judge and the secondary GLM-5.3-Flash judge agree on 97.41% of 2,700 paired outcomes (Cohen’s κ .892). On the original 72-item packet with its adjudicator labels, the secondary judge agrees on 72 of 72 items (100%; κ 1.000), with no missing or ambiguous adjudicator label. This descriptive comparison uses existing labels; it is neither new human validation nor a replacement for the binding gate.

**Table B5.10. Gemini 3.8 Flash’s primary contrasts under the secondary GLM-5.3-Flash judge (descriptive point estimates).** $D$ is the artifact pointer minus the comparator, in points, over 100 scenarios and 300 paired probes each. No new p value, interval, or tier is assigned.

| Reader                  | Hybrid-2 | Dense-2 | Hybrid-5 | Dense-5 |
|-------------------------|---------:|--------:|---------:|--------:|
| Gemini 3.8 Flash (S19b) |   +20.33 |  +15.33 |   +12.67 |   +8.33 |

**Table B5.11. Gemini 3.8 Flash reader: S10c against S19b under the same GLM-5.3-Flash judge settings.** Each arm has 300 paired probes; differences are S19b minus S10c, in points. The reader’s reasoning setting changed from S10c’s medium to S19b’s high, alongside the protocol differences in B.4.7 and B.5.7, so these descriptive differences identify no isolated setting effect and redecide neither study.

| Arm | Paired probes | S10c accuracy (%) | S19b accuracy (%) | S19b − S10c (points) |
|----|---:|---:|---:|---:|
| Plain | 300 | 66.00 | 69.33 | +3.33 |
| Generic instruction | 300 | 93.00 | 92.67 | −0.33 |
| Hybrid-5 | 300 | 83.00 | 84.33 | +1.33 |
| Dense-5 | 300 | 90.00 | 88.67 | −1.33 |
| Artifact pointer | 300 | 97.00 | 97.00 | +0.00 |
| Oracle note | 300 | 100.00 | 100.00 | +0.00 |

S19b has no GPT-6.1 Sol reader and therefore no self-preference contrast of its own; S19’s separately reported diagnostic keeps its original baseline. A separate recomputation from the saved outputs matched every registered secondary output to within $10^{-12}$ (absolute) and checked its sources and the completeness of the judge requests.

## C. Replica studies and judge-family sensitivity

This appendix covers the replica study (S11, C.1), its two follow-ups (S11b and S11c, C.2), and the judge-model study (S17: Part A in C.3, Parts B and B2 in C.4). A replica is one rebuild of the memory store from the same inputs (§3.5). The main paper summarizes these studies in §7.1 and §7.2; §5.1 uses the judge sensitivity of S17-B2 (C.4).

<a id="appendix-c1"></a>

### C.1. S11: the replica comparator

**Protocol card.** S11 used a bespoke fact extractor built on GLM-5.3-Flash, BM25 top-ten retrieval of the extracted facts, and GLM-5.3-Flash as reader and judge; it is not upstream Mem0. Appendix K.8 specifies this pipeline: the extraction prompt and fact schema, batching, the update rule, retrieval, the reader prompt and settings, and the per-replica output caps. The development set had three conversations (437 questions) and the test set four (692). Each conversation had ten replicas, built at extraction temperature 0.7. The controls were three stores built at requested temperature 0, three extra reader-and-judge passes and two extra judge draws on replica X1, and a raw-turn store that was read five times.

**Counts and complete-case questions.** The test set had 6,920 planned replica answers, ten per question. Of these, 6,901 have a valid answer and a valid binding-judge label, and 680 of the 692 questions have such labels from all ten replicas. Each estimate uses only the questions that have valid labels in every column it needs (complete-case questions). The oracle-gain and label-disagreement estimates use 671 questions. Besides all ten replica labels, these also have labels from the three extra reader passes on X1 and from all five raw-turn-store passes, because the analysis aligns those controls on the same questions. On all 680 questions with ten replica labels, $G_{\mathrm{mean}}$ would be 8.21 points rather than 8.12 (post hoc). The write-run SD and the variance shares use 675 questions, which also have the extra reader passes and judge redraws on X1; the zero-temperature control uses 677.

For binary correctness labels, the oracle-union gain over the mean of two replicas equals half their label disagreement: $G_{\mathrm{mean}} = d/2$ points, with $d$ in percent (§3.5). It measures how far the replicas’ correct answers complement each other, not a selection rule that could be deployed. $G_{\mathrm{better}}$, the gain over the better replica of a pair, depends on the level at which the better replica is selected. Table C1 gives the test quantities.

**Table C1. S11 test quantities (692 planned questions; 671 complete-case questions for the oracle gain and 675 for the variance model).** The headline intervals resample questions and replicas, conditional on the four conversations. The variance partition assumes a nested noise model in which one designated store (replica X1) carries the reader and judge passes. The best-of-20 row is a Gaussian simulation, not twenty measured variants. Neither estimates another system’s noise share. The zero-temperature row uses three stores on 677 questions.

| Test quantity | Reported result |
|----|----|
| Pairwise label disagreement $d$ | 16.25% |
| $G_{\mathrm{mean}}$ | 8.12 points; conditional 95% CI \[7.18, 9.07\] |
| $G_{\mathrm{better}}$ | 7.41 points |
| Write-run SD of pooled accuracy (across replicas, net of reader and judge noise) | 1.04 points; interval \[0.65, 1.39\] |
| Matched fact-set Jaccard (median) | .701 |
| Four-conversation t interval for $G_{\mathrm{mean}}$ (3 df) | \[5.77, 10.48\] |
| $G_{\mathrm{mean}}$ at requested zero extraction temperature | 8.27 points |
| Judge-free containment $G_{\mathrm{mean}}$ | 4.54 points |
| Nested-model variance shares: store (extraction), reader, and judge | 57.31%, 28.66%, and 14.03% |
| Simulated best-of-20 gain of at least 2 points | Probability .594; interval \[.45, .70\] |

Both the development and the test results meet the registered gap threshold ($G_{\mathrm{mean}}$ of at least 4.45 points: 6.66 and 8.12). Neither supports the registered claim of large write variance, which needs a write-run SD of at least 2 points together with a matched Jaccard of at most .6 (observed: 0.68 and 1.04 points). The registered winner’s-curse claim is that the best of 20 equal variants beats the baseline by at least 2 points with probability at least .50. With ten replicas it holds on the test set (.594) but not on the development set (.465), so under the registered replication rule it does not replicate; with five replicas, the registered default card, it holds on both (.633 and .608).

Only the development answers were validated against LLM adjudicator labels. In the one-grader human check of 50 sampled test answers (Appendix J.4), the author, as sole grader, agreed with the judge on 45 (raw 90.0%; design-weighted 96.9%). The author judged 10 of the 15 sampled disagreeing pairs to be real differences in correctness (pair-weighted 68.6%, bootstrap interval \[42.6, 91.2\]). This check does not correct $G_{\mathrm{mean}}$.

Each replica sent its own distinct requests. A post hoc check of the call log found that the only duplicated request bodies are the second copies of eleven twin-question pairs (identical questions within one conversation), some of which the model proxy answered with a copy (Appendix H.1). Removing those second copies moves $G_{\mathrm{mean}}$ from 8.12 to 8.15 points. The variation that remains at requested zero temperature establishes neither a mechanism nor the equivalence of the two temperatures.

**Related replica designs.** RoutePrism (Xu et al. 2026) compares ingestion-order effects with repeated-answer variation within each route, while RealCompanion (Behnam et al. 2026) repeats profile reconstruction. Item-level disagreement under stable aggregate accuracy is known as prediction churn or underspecification (Milani Fard et al. 2016; D’Amour et al. 2022) and, in LLM evaluation, as run-to-run nondeterminism (Song et al. 2025). Our oracle union over $k$ replicas is the pass@k coverage estimator (Chen et al. 2021; Brown et al. 2024) applied to judged labels. Our replica study rebuilt the store from fixed inputs and reported the label disagreement between judged answers. Its hindsight union is a measurement statistic, not a selector that can be deployed (Chen 2026). None of this identifies a causal fraction of true correctness or a universal noise floor.

<a id="appendix-c2"></a>

### C.2. S11b and S11c: validation controls the interpretation

S11b crossed two extractors, GLM-5.3-Flash and Gemini 3.5 Flash-Lite, with the same two models as judges; GLM-5.3-Flash was the reader, and each extractor had five replicas. It stopped at its development gate, before its planned test on seven S11 conversations (a reused test split). Its outcome-enriched validation packet had 70 items from one conversation (Kish effective n 51.1). As a judge, Gemini 3.5 Flash-Lite passed on design-weighted agreement (.846) but failed on design-weighted κ (.635, below the .70 bar); GLM-5.3-Flash passed both, narrowly (.872 and .717). Under the registration, a failed judge validation is terminal. A separate recomputation from the saved outputs reproduced every gate number and confirmed the terminal stop, so no test contrast between judge models is licensed. Table C2 gives the development cells.

**Table C2. S11b development cells (one conversation).** Points. These are single-conversation descriptives, without intervals or hypothesis verdicts. Flash-Lite is Gemini 3.5 Flash-Lite; GLM is GLM-5.3-Flash. One reader output stayed invalid, so the complete-case rule drops one of the 81 questions from every cell.

| S11b development cell | $G_{\mathrm{mean}}$ | $G_{\mathrm{better}}$ | Complete-case questions |
|----|---:|---:|---:|
| Flash-Lite extractor; GLM judge | 6.50 | 5.87 | 80 of 81 |
| Flash-Lite extractor; Flash-Lite judge | 7.25 | 6.38 | 80 of 81 |
| GLM extractor; GLM judge | 8.00 | 6.12 | 80 of 81 |
| GLM extractor; Flash-Lite judge | 7.63 | 5.87 | 80 of 81 |

S11c kept GLM-5.3-Flash as reader and judge and crossed it with the two extractors, five replicas each. Its seven conversations, S11’s development and test conversations, are a reused test split, and they were chosen with S11’s gaps already known. Of the 1,118 planned questions, 1,112 have valid labels from all ten replicas. $G_{\mathrm{mean}}$ is averaged over the ten replica pairs within each question, then over the questions within each conversation, then over the seven conversations, with equal weights at each level. Two one-sided conversation-level t tests, Holm-adjusted, compare $G_{\mathrm{mean}}$ with 4.45 points. That threshold is half of the 8.9-point reference gain that we recomputed from the released labels of Sharma and Lall (2026) (§3.5); it is not a same-population comparator. The intervals assume exchangeable conversations.

**The binding validation failed.** Design-weighted agreement (.876) passed, but design-weighted κ (.697) did not. All cards in Tables C3 and C4, including the extractor contrast, therefore remain UNRESOLVED (judge validation). Statistical ABOVE or TOST results cannot override this outcome.

**Table C3. S11c cards: $G_{\mathrm{mean}}$ against 4.45 points under the GLM-5.3-Flash judge.** Points. Flash-Lite is Gemini 3.5 Flash-Lite; GLM is GLM-5.3-Flash. Companion cards never determine the study verdict. The last column is a sensitivity analysis that keeps S11b’s test family of four cells and enters its two unrun judge cells with $p = 1$. In that column the last row (original development conversations, GLM extractor) is not statistically ABOVE. Every card is UNRESOLVED (judge validation).

| Card; extractor | $G_{\mathrm{mean}}$ | Descriptive 95% t CI | Two-cell Holm p | Four-cell Holm p (S11b’s test family) |
|----|---:|----|---:|---:|
| Seven conversations; Flash-Lite | 8.53 | \[7.48, 9.58\] | .00008 | .0002 |
| Seven conversations; GLM | 7.90 | \[6.36, 9.44\] | .0008 | .0023 |
| Original four test conversations; Flash-Lite | 8.46 | \[6.08, 10.84\] | .0127 | .0254 |
| Original four test conversations; GLM | 8.37 | \[5.51, 11.22\] | .0127 | .0333 |
| Original three development conversations; Flash-Lite | 8.63 | \[6.90, 10.36\] | .0091 | .0183 |
| Original three development conversations; GLM | 7.29 | \[3.36, 11.21\] | .0449 | .1346 |

**Table C4. S11c extractor contrast, Flash-Lite minus GLM extractor.** Points; Flash-Lite is Gemini 3.5 Flash-Lite and GLM is GLM-5.3-Flash. Validation overrides TOST, so every row is UNRESOLVED (judge validation). Nine of the ten disagreements between the judge and the adjudicator labels concern answers from the GLM-5.3-Flash extractor. This selected subgroup is not population evidence, and the near-zero contrast does not show that the two extractors behave alike.

| Card | Difference | 95% CI | ±2-point TOST p |
|----|---:|----|---:|
| Seven conversations | +0.63 | \[−0.60, +1.86\] | .0173 |
| Original four test conversations | +0.10 | \[−1.68, +1.87\] | .0211 |
| Original three development conversations | +1.34 | \[−2.27, +4.96\] | .258 |

The single registered resume pass ran after the validation packet was built. It resent the reads and judge calls that were still invalid and made ten more questions complete, raising the count from 1,102 to 1,112. The cards use all 1,112 questions, but these ten lie outside the packet’s sampling frame, so the validation weights do not represent them. Together with the 18 questions that the weights never covered, 28 of the 1,112 questions (2.5%) lie outside the support of the validation weights. Amendment S11C-H1 is a post-lock code repair that applies the registered precedence of the health checks to the extractor contrast of every card. It was installed while the test was running and leaves every card’s verdict unchanged. That it was installed before any S11c outcome was examined rests on a signed attestation in the study record; the files cannot show it.

### C.3. S17 Part A: another judge, failed validation

**Protocol card.** S17 rejudged S11c’s answers (a reused test split) with GPT-6.1 Sol at medium reasoning effort. The temperature was not sent, so the model ran at its fixed temperature 1.0. Because the original GLM-5.3-Flash judge ran at temperature 0, judge model family and temperature are confounded. A budget ladder, fixed from the observed cost of the 70 validation calls, chose the largest allowed sample: 45 questions per conversation in a registered hash order, or 315 over the seven conversations. With two extractors and five replicas each, this gave 3,150 answers, all of which were judged. Validation reused S11c’s packet, its adjudicator labels (from Claude Opus 5.5), and its design weights (Tables C5 and C6). Tables C7–C9 give the results.

**Table C5. S17 Part A validation of the GPT-6.1 Sol judge on S11c’s packet (lenient labels).** The last column repeats the GLM-5.3-Flash judge’s values on the same packet, with the registered bars. A missing label counts as a disagreement. The bootstrap interval is descriptive.

| Part A validation statistic | GPT-6.1 Sol judge | GLM-5.3-Flash judge; bar |
|----|---:|----|
| Design-weighted agreement | .851 | .876; bar ≥ .80 |
| Design-weighted κ | .649 | .697; bar ≥ .70 |
| Raw agreement; raw κ | .829; .644 | .857; .696 |
| Determinate items; eligible and determinate pairs | 70; 20 and 20 | Bars ≥ 60; ≥ 10 and ≥ 10 |
| Missing judgments | 0 | Missing counts as disagreement |
| Kish effective n | 64.8 | 64.8 |
| Design-weighted κ, stratified-bootstrap 95% CI | \[.482, .813\] | Descriptive |
| Binding validation | **Failed** | GLM-5.3-Flash also failed |

**Table C6. S17 Part A design-weighted κ by extractor.** A cell carries the qualifier “validation weak” when its extractor’s design-weighted κ is below .60. The weights represent 1,084 of the 1,102 questions in the packet’s sampling frame: 18 questions have no representation, and the ten questions added by S11c’s resume pass fall outside the frame (C.2). Strict-rubric agreement (.893) and κ (.782) cannot replace the binding validation. Both judges disagree with the adjudicator labels mainly on items from the GLM-5.3-Flash extractor, and the packet cannot show which labels are correct.

| Extractor subset | Items | Design-weighted κ | 95% bootstrap CI | Kish effective n | Additional qualifier |
|----|---:|---:|----|---:|----|
| GLM-5.3-Flash | 39 | .467 | \[.296, .676\] | 36.0 | Validation weak |
| Gemini 3.5 Flash-Lite | 31 | .872 | \[.678, 1.000\] | 28.8 | None |

**Table C7. S17 Part A: $G_{\mathrm{mean}}$ under the GPT-6.1 Sol judge (315 questions per extractor).** Flash-Lite is Gemini 3.5 Flash-Lite; GLM is GLM-5.3-Flash. One-sided conversation-level t tests against 4.45 points (6 df), Holm-adjusted over the two cells. The label-error probability and the plug-in correction come from the retest (Table C9). Validation failure takes precedence over the statistical ABOVE tier, so the positive Part A sentence is not licensed.

| Part A statistic | Flash-Lite extractor | GLM extractor |
|----|---:|---:|
| $G_{\mathrm{mean}}$, points | 7.08 | 6.35 |
| SE; t (6 df) | 0.678; 3.88 | 0.590; 3.22 |
| One-sided p against 4.45 | .0041 | .0091 |
| Two-cell Holm p | .0082 | .0091 |
| Bonferroni one-sided lower bound at $\alpha/2$ | 5.42 | 4.91 |
| Descriptive 95% t interval | \[5.42, 8.74\] | \[4.91, 7.79\] |
| Exact sign-flip p, nonbinding | .0156 | .0156 |
| Estimated symmetric label-error probability $\varepsilon$ | .0032 | .0016 |
| Attenuation factor | .9873 | .9937 |
| Plug-in corrected $G_{\mathrm{mean}}$, points | 6.85 | 6.23 |
| $G_{\mathrm{mean}}$ with missing labels filled pessimistically; optimistically | 7.08; 7.08 | 6.35; 6.35 |
| Statistical tier only | ABOVE | ABOVE |
| **Final verdict** | **UNRESOLVED (judge validation)** | **UNRESOLVED (judge validation); validation weak for the GLM extractor** |

**Table C8. S17 Part A descriptive robustness (no verdict depends on these values).** Points; Flash-Lite is Gemini 3.5 Flash-Lite and GLM is GLM-5.3-Flash. The same-rows difference compares GPT-6.1 Sol with the GLM-5.3-Flash judge on the same 315 questions per extractor. On those rows the GLM-5.3-Flash judge’s $G_{\mathrm{mean}}$ is 8.19 (Flash-Lite extractor) and 7.21 (GLM extractor), the comparison in the main paper’s §7.2. The GLM-extractor difference interval includes zero. Across the 3,150 matched judgments, the two judges agree on .964 of answers (κ .914). Under GPT-6.1 Sol the extractor contrast is +0.73 \[−0.52, +1.98\] points, reported without an equivalence interpretation.

| Descriptive robustness measure | Flash-Lite extractor | GLM extractor |
|----|----|----|
| Macro $G_{\mathrm{better}}$ | 4.86 | 4.38 |
| Per-conversation $G_{\mathrm{mean}}$ range | 3.56–8.67 | 3.33–8.22 |
| Leave-one-conversation-out range | 6.81–7.67 | 6.04–6.85 |
| Delete-one-replica range | 6.46–7.43 | 6.03–6.51 |
| Question-weighted $G_{\mathrm{mean}}$ (S11’s pooling) and 95% interval | 7.08 \[5.12, 9.04\] | 6.35 \[4.97, 7.73\] |
| First-attempt $G_{\mathrm{mean}}$ | 7.08 | 6.35 |
| Discordant judgments on identical-answer replica pairs | 0 of 648 | 0 of 630 |
| $G_{\mathrm{mean}}$ difference from the GLM-5.3-Flash judge on the same rows | −1.11 \[−1.86, −0.36\] | −0.86 \[−1.75, +0.03\] |
| Judge-free containment $G_{\mathrm{mean}}$ | 4.03 | 4.06 |

**Table C9. S17 retest of the GPT-6.1 Sol judge.** The retest sent an identical second request for nine questions per conversation, with all five replicas of each extractor. $r$ is the retest disagreement rate, $\varepsilon = (1 - \sqrt{1 - 2r})/2$ is the estimated per-call label-error probability, and the attenuation factor is $(1 - 2\varepsilon)^2 = 1 - 2r$. The registered plug-in correction is $\hat{d} = (d - 2\varepsilon(1 - \varepsilon))/(1 - 2\varepsilon)^2$ per conversation, clipped at zero. It assumes independent, symmetric label errors and requires an attenuation factor of at least .25. The retest neither establishes this model nor propagates the uncertainty in its parameters, so the correction is a plug-in sensitivity, not a calibrated bound.

| Retest extractor | Paired calls | Disagreements | Rate $r$ | Estimated $\varepsilon$ | Attenuation $1 - 2r$ |
|----|---:|---:|---:|---:|---:|
| GLM-5.3-Flash | 315 | 1 | .0032 | .0016 | .9937 |
| Gemini 3.5 Flash-Lite | 315 | 2 | .0063 | .0032 | .9873 |

<a id="appendix-c4"></a>

### C.4. S17 Parts B and B2: the same S10c answer set

Part B rejudged S10c’s 87-item test packet (85 judge calls) with GPT-6.1 Sol, against the same adjudicator labels that S10c used. These labels came from a fresh Claude Opus 5.5 instance that saw only the blinded packet. Part B supplied B2’s validity gate and did not alter S10c (Table C10).

**Table C10. S17 Part B agreement on S10c’s 87-item test packet.** All items are determinate, and the validation gate passes. By reader (29 items each), GPT-6.1 Sol’s agreement and κ with the adjudicator labels are 1.000 and 1.000 for Gemini 3.8 Flash, .966 and .931 for Gemini 3.5 Flash-Lite, and .931 and .713 for GLM-5.3-Flash.

| Part B comparison                             |   n | Agreement |            κ |
|-----------------------------------------------|----:|----------:|-------------:|
| GPT-6.1 Sol judge versus adjudicator labels   |  87 |      .966 |         .910 |
| GLM-5.3-Flash judge versus adjudicator labels |  87 |      .943 |         .846 |
| GPT-6.1 Sol judge versus GLM-5.3-Flash judge  |  87 |      .931 | Not reported |

Part B2 scored 900 judge calls (2,700 probe scores). Each contrast has 100 scenarios (300 probes), no missing scores, and S10c’s estimator and inference. The 98.75% (= 1 − .05/4) Bonferroni per-contrast intervals target nominal 95% coverage for the test family of four contrasts (Table C11).

**Table C11. S17-B2: artifact-pointer contrasts under the GPT-6.1 Sol judge.** Points; each contrast is the artifact pointer minus a five-session retrieval pointer. Permutation p values use 10,000 permutations (denominator 10,001), and Holm p values adjust them over the four contrasts. Scenarios count up, down, and tie; probes count those passed only under the artifact pointer or only under the comparator. The tier “supported, at least +5” needs a Bonferroni lower bound of at least +5; “supported” needs an estimate of at least +5 and a lower bound above zero.

| Reader; artifact pointer minus comparator | $D$ | 95% CI | 98.75% Bonferroni per-contrast CI | Permutation p; Holm p | Scenarios up, down, tie | Probes artifact-only, comparator-only | Missing-score bounds | Tier |
|----|---:|----|----|----|----|----|----|----|
| Gemini 3.8 Flash; hybrid-5 | +12.67 | \[+8.67, +17.00\] | \[+7.67, +18.33\] | 1/10,001; 4/10,001 | 33, 2, 65 | 42, 4 | \[+12.67, +12.67\] | “supported, at least +5” |
| Gemini 3.8 Flash; dense-5 | +7.67 | \[+4.33, +11.33\] | \[+3.33, +12.33\] | 1/10,001; 4/10,001 | 22, 2, 76 | 26, 3 | \[+7.67, +7.67\] | “supported” |
| Gemini 3.5 Flash-Lite; hybrid-5 | +17.33 | \[+12.33, +22.34\] | \[+11.00, +23.67\] | 1/10,001; 4/10,001 | 48, 6, 46 | 59, 7 | \[+17.33, +17.33\] | “supported, at least +5” |
| Gemini 3.5 Flash-Lite; dense-5 | +16.33 | \[+11.67, +21.33\] | \[+10.33, +22.67\] | 1/10,001; 4/10,001 | 45, 4, 51 | 54, 5 | \[+16.33, +16.33\] | “supported, at least +5” |

**Registered interpretation.** On S10c’s reused test split, the artifact-pointer premium is “supported” under the GPT-6.1 Sol judge for these four contrasts and their paired populations, and S10c’s verdicts are unchanged. The validation is against the same blind adjudicator labels, which cover 27 of the 900 Part B2 judge calls. It is not a validation against human judgment.

**Table C12. S17-B2: accuracy under the two judges, by reader and arm (300 probes per cell).** Accuracies are in percent. Differences are GPT-6.1 Sol minus GLM-5.3-Flash, in points, with paired 95% intervals. Overall agreement is .967 and κ is .914.

| Reader and arm | Accuracy under GPT-6.1 Sol | Accuracy under GLM-5.3-Flash | Difference | Paired 95% CI | Agreement | κ |
|----|---:|---:|---:|----|---:|---:|
| GLM-5.3-Flash, artifact pointer | 94.7 | 98.0 | −3.33 | \[−5.33, −1.67\] | .967 | .532 |
| GLM-5.3-Flash, hybrid-5 | 80.7 | 84.3 | −3.67 | \[−6.00, −1.67\] | .957 | .850 |
| GLM-5.3-Flash, dense-5 | 84.3 | 87.7 | −3.33 | \[−5.67, −1.33\] | .960 | .834 |
| Gemini 3.8 Flash, artifact pointer | 94.7 | 97.0 | −2.33 | \[−4.33, −0.67\] | .977 | .709 |
| Gemini 3.8 Flash, hybrid-5 | 82.0 | 83.0 | −1.00 | \[−2.67, +0.67\] | .977 | .919 |
| Gemini 3.8 Flash, dense-5 | 87.0 | 90.0 | −3.00 | \[−5.00, −1.33\] | .970 | .853 |
| Gemini 3.5 Flash-Lite, artifact pointer | 55.0 | 58.0 | −3.00 | \[−5.33, −1.00\] | .963 | .925 |
| Gemini 3.5 Flash-Lite, hybrid-5 | 37.7 | 39.0 | −1.33 | \[−3.67, +1.00\] | .960 | .915 |
| Gemini 3.5 Flash-Lite, dense-5 | 38.7 | 40.7 | −2.00 | \[−4.00, −0.33\] | .973 | .944 |

Pass rates are lower under GPT-6.1 Sol in every pointer arm: it passes 1.0–3.7 points fewer of these answers than the GLM-5.3-Flash judge in all nine cells (Table C12). Part B2 used the Part A settings (GPT-6.1 Sol at medium reasoning effort and its fixed temperature 1.0, against S10c’s GLM-5.3-Flash judge at temperature 0), so judge model family and temperature are confounded here too. The four primary contrasts change by −1.67 to +0.67 points and keep their tiers. Without non-pointer comparators or a retest, this is a sensitivity check on one answer set, not evidence of robustness across judge model families.

Part B2 was reinstated after the sparse pointer result of the LLM regrade was known: adjudicator G3 (GPT-6.1 Sol) passed fewer pointer answers than the GLM-5.3-Flash judge, a gap carried by two items (Appendix F.2). Part B2 cannot test that hint, because all three of its arms are pointer arms. A separate recomputation from the saved outputs reproduced the arithmetic and the local accounting, and its correction of one interval label (to “98.75% Bonferroni per-contrast intervals”) is adopted here. Model identity, caching, runtime guards, and the historical chronology were not reconstructed.

<a id="appendix-d"></a>

## D. Counterfactual haystacks: final retrieval, parent stop, and invalid end-to-end successor

**Snapshot and source scope.** S15 had two parts: S15a, the retrieval family (D.1–D.3), and S15b, the end-to-end family, which stopped before any end-to-end call (D.4). S15c is the registered successor of S15b (D.5). The S15 and S15c reports were adopted on 9 October 2026, after two separate recomputations from the saved outputs (D.6). S15c was attempted, but both of its primary comparisons are final INVALID under its completeness rule (S15c-K1). The planned content-equivalence check of CF-STYLE and S15c’s auxiliary test diagnostic remain UNPERFORMED, and S15c’s auxiliary development diagnostic is incomplete. These outcomes are part of the result; they are not omissions, and they do not indicate success. The main paper summarizes this appendix in §5.2 (the constructed ranker), §6.1 (the retrieval family), and §6.3 (the end-to-end tests).

### D.1. Protocol and final retrieval family

We excluded LoCoMo-Plus from S15 by a scope decision recorded before registration (decision 9 on version 2 of the S15 design), which the frozen registration cites. Its absence is a scope decision, not an unfinished S15 experiment.

S15a held the target questions, evidence sessions, session counts, positions, and dates fixed while it replaced the distractor sessions. ORIG-N, the normalized original haystack, uses the user turns and date-only session headers and normalizes typography. The STALE counterfactual CF-SOURCE (the source-swap distractors of §3.3) draws evidence sessions of other scenarios from the same fold, under the registered similarity exclusions, and allows sibling evidence pairs. The LongMemEval-S counterfactual, also called CF-SOURCE, replaces the conversational filler with eligible simulated sessions from other questions. Neither intervention guarantees constant difficulty. CF-SOURCE-L is the registered length sensitivity. CF-STYLE (style rewrites) rewrites each unique STALE distractor, and a rewrite flagged as failed keeps its ORIG-N text.

A1 measures native retrieval sensitivity, that is, how the unmodified retriever responds to distractor replacement, confounded with the hardness of the negatives; deliberate exploitability is tested separately by the constructed fusion ranker (D.3). The primary outcome is hybrid all-gold@5: BM25 and dense rankings fused by reciprocal rank fusion (RRF) with $k = 60$. The registered family has three tests (Table D1): A1, STALE CF-SOURCE; A2, STALE CF-STYLE; and A3, LongMemEval-S CF-SOURCE. Differences are ORIG-N minus the counterfactual, in points. POSITIVE requires a Holm-adjusted lower bound above zero and an estimate of at least +5 points. The equivalence margin is ±3 points under Holm-adjusted two one-sided tests (TOST). Each interval is the hull of a 10,000-draw cluster bootstrap interval (seed 1515) and a cluster-mean t interval, both at the Holm step-down level. A PARTIAL manipulation keeps its slot in the test family with $p = 1$, and its numerical contrast is exploratory.

**Table D1. Final primary and registered wrong-question retrieval contrasts.** Points. STALE has 1,200 probes in 400 scenario clusters, and LongMemEval-S has 470 questions. The secondary rows use same-type wrong-question retrieval: any-gold@5 when each probe is replaced by ten hash-selected questions of the same probe type (STALE) or question type (LongMemEval-S). They form a separate secondary test family, which the registration calls the query-independence index (QI). The primary family (A1–A3) stops at Holm step 2, because A2 and A3 hold $p = 1$ slots. Both are therefore shown at the stopped level $\alpha = .025$, and their intervals are computed at that level, as in Table E3. The secondary family has two members ($\alpha = .025$, then .05).

| Test | Contrast and outcome | Difference | Holm-adjusted interval | $\alpha$ at step | Final verdict |
|----|----|---:|----|---:|----|
| A1 | STALE CF-SOURCE, all-gold@5 | +12.58 | \[+9.64, +15.53\] | .016667 | POSITIVE |
| A2 | STALE CF-STYLE, all-gold@5 | −0.25 | \[−1.67, +1.17\] | .025000 | EXPLORATORY (K3 partial) |
| A3 | LongMemEval-S CF-SOURCE, all-gold@5 | +1.06 | \[−0.37, +2.55\] | .025000 | EXPLORATORY (K3 partial) |
| QI-STALE | STALE CF-SOURCE, same-type wrong-question any-gold@5 | +21.23 | \[+19.95, +22.54\] | .025000 | POSITIVE |
| QI-LME | LongMemEval-S CF-SOURCE, same-type wrong-question any-gold@5 | +7.55 | \[+6.60, +8.53\] | .050000 | EXPLORATORY (K3 partial) |

An earlier interim version of this appendix listed A2 as not computed; the completed value above replaces it. A1 remains POSITIVE in the completed family. The narrow intervals of the two PARTIAL manipulations license neither a confirmatory equivalence nor a finding below the smallest effect size of interest (SESOI, +5 points). Three LongMemEval-S questions have more than five gold sessions and therefore cannot reach all-gold@5. These retrieval findings concern this intervention; they are not effects on reader accuracy. In the secondary family, same-type wrong-question any-gold@5 on STALE falls from 42.08% to 20.85%, close to its uniform null of 19.2%. The atlas (Appendix E) draws its ten wrong questions from a different group under its own eligibility rules, which is why its STALE rate is 41.40% rather than 42.08%; with S15’s rule, the atlas code reproduces S15’s rate within 0.02 points. STALE is cue-dominated in the atlas, so no isolated cue mechanism is established.

### D.2. Harder negatives and the meaning of the contrast

The STALE replacement increases the number of registered hard negatives per probe (Appendix K.4 gives the definition). This supplies a competing explanation for the drop in retrieval: the counterfactual changes interference as well as question-blind cues. The registered subset analysis conditions on the observed change in the scenario-mean count. It describes the scenarios without an increase; it neither estimates a causal adjustment nor identifies the fraction of A1 attributable to harder negatives. Sibling pairs, the old and new evidence sessions of one donor scenario drawn into the same haystack, also change the distractor structure. The intervals of the two sibling subgroups overlap, and no difference between them was registered (Table D2).

**Table D2. Registered hardness and sibling diagnostics.** The intervals are ordinary 95% intervals, each the hull of a bootstrap and a t interval; they are not additional confirmatory tests. The first row is a count change per probe, CF-SOURCE minus ORIG-N. The other rows are ORIG-N minus CF-SOURCE all-gold@5 contrasts.

| Quantity | Estimate | 95% interval | Probes; scenarios |
|----|---:|----|---:|
| Hard-negative count change per probe | +2.62 counts | \[+2.24, +2.99\] | 1,200; 400 |
| A1 among scenarios without a mean hard-negative increase | +3.54 points | \[+0.04, +7.07\] | 396; 132 |
| A1 with at most eight sibling pairs | +13.99 points | \[+10.92, +17.07\] | 786; 262 |
| A1 with more than eight sibling pairs | +9.90 points | \[+6.04, +13.77\] | 414; 138 |

### D.3. Failed style manipulation, constructed ranker, and process diagnostics

The K3 manipulation check classifies single units from their text alone. It uses the 31-feature question-blind classifier of Appendix A, a histogram gradient-boosting (HGB) model whose settings Appendix K.2 gives. The check requires a detectability AUROC (macro within-pool) of at most .60, with a 95% upper bound of at most .65. STALE CF-SOURCE passes by construction, because every session is an evidence session; this does not establish that every cue was removed. CF-STYLE and LongMemEval-S CF-SOURCE are PARTIAL (Table D3 gives the AUROCs). Two descriptive diagnostics accompany the check. The pair-cue rate is the share of haystacks whose most similar session pair (by TF-IDF) is the gold pair. The n-gram AUROC (macro within-pool) comes from a character 3–5-gram logistic-regression classifier. For STALE CF-SOURCE, the pair-cue rate is 2.75% \[1.25%, 4.50%\] against a chance rate of 0.081633%, and the n-gram AUROC is .527031. For CF-STYLE, the pair-cue rate is 1.00% \[0.25%, 2.00%\] and the n-gram AUROC is 1.000000. The label stored with the latter result (“de-leaked for the S10 features only”) is a diagnostic tag, not evidence that the failed style intervention passed K3.

**Table D3. Saved classifier summaries and deliberate prior fusion.** The AUROC is the detectability AUROC (macro within-pool) of the HGB classifier, with 95% bootstrap intervals; classifier pools and retrieval probes differ. The retrieval columns give hybrid all-gold@5 in percent. Fusion adds twice the out-of-fold classifier score (the style prior) to the percentile hybrid score, on matched probes with complete prior coverage.

| Population | Classifier pools; retrieval probes | Detectability AUROC \[95%\] | Hybrid (%) | Fused (%) | Fusion gain, points |
|----|---:|----|---:|---:|---:|
| STALE ORIG-N | 400; 1,200 | 1.000 \[1.000, 1.000\] | 65.75 | 99.75 | +34.00 |
| STALE CF-SOURCE | 400; 1,200 | .513 \[.492, .536\] | 53.17 | 53.17 | 0.00 |
| STALE CF-STYLE | 400; 1,200 | 1.000 \[.999, 1.000\] | 66.00 | 99.50 | +33.50 |
| STALE CF-SOURCE-L | 400; 1,200 | .602 \[.579, .623\] | 53.58 | 52.67 | −0.92 |
| LongMemEval-S ORIG-N | 300; 470 | .744 \[.723, .765\] | 90.85 | 86.17 | −4.68 |
| LongMemEval-S CF-SOURCE | 300; 470 | .666 \[.642, .691\] | 89.79 | 88.30 | −1.49 |
| LongMemEval-S CF-SOURCE-L | 300; 470 | .800 \[.786, .814\] | 91.49 | 90.00 | −1.49 |

The +34-point fusion gain on ORIG-N holds on STALE only; the same construction loses 4.68 points on LongMemEval-S. It shows deliberate ranking exploitability, not reliance by an unmodified system or the inflation of a leaderboard. The +33.5-point gain on CF-STYLE is consistent with its failed manipulation. CF-SOURCE also raises the mean hard-negative count from 3.361667 to 5.976667 per probe, and the selected subset in Table D2 cannot identify a causal share of A1. Over the 400 haystacks, the number of sibling pairs has mean 7.8125, median 8, and range 2–15; the earlier design estimate of 2–13 was not a cap.

**Unfinished content check.** All 12,195 unique rewritten sessions reached a final record. Of these, 10,806 passed the mechanical checks and 1,389 were flagged, a mechanical pass share of 88.61%, below the 98% bar. The HGB AUROC also fails K3. The planned blind content-equivalence check, in which a fresh Claude instance was to rate 60 pairs, remains UNPERFORMED: no content labels exist among the final study files, and the content-pass field was never filled. Even a perfect later rating (60 of 60) could not satisfy the registered conjunction, whose mechanical part had already failed. The author approved two fresh Claude API contexts only for the two reference stages of the successor study (D.5.2), not for this third rater. No substitute rater, late label, or gate overwrite was used.

Failed rewrites kept their registered fallback, the ORIG-N text. Repeated recovery attempts and interrupted generations limit the copy diagnostics, which prove neither provider behavior nor independent generation. These process observations do not change the failed K3 manipulation check.

<a id="appendix-d4"></a>

### D.4. S15b: registered budget stop before any end-to-end call

S15b stopped at its registered forecast gate (K5) before any end-to-end memory, reader, or judge call. Even after optional work was dropped, the displayed forecast was 60,174 attempts against the unchanged cap of 60,000; this was a forecast stop, not an observed overspend. No scope or population was shrunk. The registered outcome remains “branch not computed (family B not run, K5)”. Two code-repair cycles, each recorded as an amendment before the repaired command ran, followed the S15a outcomes but preceded any planned call of family B. S15c is a separate successor study and does not change this stop.

### D.5. S15c: design, final invalidity, and eligible secondary evidence

#### D.5.1. Successor design and changed measurement

The reserve held 260 scenarios. The 36 registered exclusions left 224, split exhaustively into 35 development and 189 test scenarios. The memory and full-context test conditions used the first 100 test scenarios in the frozen hash order, the no-history and mismatch test conditions the first 30, and the memory and mismatch development conditions 10. Each scenario has 50 sessions and three probes. No disjoint replacement population or post-outcome reselection exists. S15c inherited S15’s populations, models, counterfactuals, salts, seeds, and order. It was designed after the POSITIVE S15-A1 result and the hard-negative results were known. Its forecast rule (K5) was changed, and the new rule was chosen after the author knew that S15’s rule would stop S15b and that the new rule would let S15c run; S15’s rule would also have stopped S15c. The precommitted trigger preceded the development run, but blindness to the S15a outcomes is not claimed.

The two primary tests compare ORIG-N with CF-SOURCE: B1 for the RAG pipeline and B2 for the memory pipeline. The primary RAG and memory cells used three reads per probe. The gold-pair-plus-three arm (registered in S15c as Oracle-5), the full-context arm, and the controls used one. The gold-pair-plus-three arm holds the gold pair plus three fixed distractor slots, and the RAG arm uses hybrid top-five retrieval. The exact memory label is “mem0 2.2.1 pipeline (unmodified mem0 decisions; adapter as registered plus S15c annex M extraction-budget escalation)”. The adapter adds session dates to the reader input. Extraction uses the run date, the top ten existing memories, and the last ten messages, without an LLM UPDATE/DELETE stage, and the semantic-only search omits mem0’s entity and keyword boosts. Date rendering was not compared with a text-only control. Appendix K.8 gives the adapter’s settings, including the embedder, the vector store, and the extraction model.

GLM-5.3-Flash served as the reader and as the binding judge under the official STALE rubric, both at temperature 0. Protocol amendment M (registered as annex M) changes the recovery of attempts that came back empty because their token budget ran out. After such an extraction attempt at 16,384 tokens, the next attempt runs with 32,768 tokens. After such a judge attempt at 12,000 tokens, the next runs with 24,000, one attempt earlier than under the previous judge remedy. An empty attempt at the raised budget is terminal. Readers keep their registered 32,768-token cap and recovery rule. The rule is blind to condition but can change validity differently by condition, so it is a declared measurement deviation. One judge call scores the three probes of one scenario, arm, condition, and read. All study calls bypassed the shared client cache, but this does not exclude copies returned by the API proxy.

#### D.5.2. Reference validation and completeness are different gates

The reference raters were two fresh Claude Sonnet 5.5 API contexts, one per stage, approved by the author. Each saw only its fixed, blinded packet, the official rubric, and neutral instructions, without condition keys or study results, and only its first original response was used. The registration had specified a different execution route for these raters; the change of channel was approved and disclosed. Their labels are model labels, not human adjudication, and both stages pass the agreement gate (Table D4). The saved outputs carry a fixed rater description that the pipeline wrote for the registered route; it does not describe these raters, whose provenance is as stated here.

**Table D4. Binding-judge agreement with the Claude Sonnet 5.5 reference raters.** Thresholds: agreement ≥ .80 and a finite Cohen’s κ ≥ .70. No item was ambiguous or missing, so the optimistic and pessimistic bounds equal the displayed agreement.

| Stage | Determinate items | Agreement | Cohen’s κ | Ambiguous; missing | Gate |
|----|---:|---:|---:|---:|----|
| Development | 60 | 57 of 60 (95.00%) | .900 | 0; 0 | PASS |
| Test | 60 | 56 of 60 (93.33%) | .866 | 0; 0 | PASS |

All 8,250 planned test reads succeeded; only 2,731 of the 2,750 logical binding judge calls succeeded, and 19 were lost terminally. Successful reads do not imply a complete correctness outcome. All 200 final test memory stores are usable. Each judge call covers three probes, and a primary probe needs verdicts for all three of its planned reads. A missing judgment for one scenario and read therefore removes those probes, once per cell. The four primary cells in Table D5 lose 9 + 15 + 12 + 6 = 42 probe-cell entries in this way. This is not 19 × 3: the 19 failed calls are spread over all test cells, including secondary cells, and different failed reads can affect the same primary probes. This accounting uses the completeness and terminal-count tables of the adopted study report, not the raw records.

**Table D5. Final K1 completeness (validity rates, not accuracies).** The inclusive 98% bar is unchanged.

| Required cell    | Valid of planned probes | Completeness | Cell state   |
|------------------|------------------------:|-------------:|--------------|
| RAG ORIG-N       |              558 of 567 |       98.41% | COMPLETE     |
| RAG CF-SOURCE    |              552 of 567 |       97.35% | INVALID (K1) |
| Memory ORIG-N    |              288 of 300 |       96.00% | INVALID (K1) |
| Memory CF-SOURCE |              294 of 300 |       98.00% | COMPLETE     |

**B1 and B2 are final INVALID (K1).** Both remain in the two-test Holm denominator with $p = 1$, but neither has a reported primary effect, interval, or McNemar result; their placeholder values are undefined, not zero. Terminally lost binding judge calls cannot be retried, and no repair cycle remains: the two cycles inherited from S15 and the successor’s single repair make three, against an unchanged maximum of two. Final invalidity is neither a pending repair nor a null or equivalence finding. The frozen implementation builds transient paired arrays before it marks the tests invalid and then discards them before primary inference. We claim only that primary reporting and inference were suppressed, not that no intermediate arithmetic was computed. We do not reconstruct those effects, and we do not subtract cell means computed on different valid populations.

#### D.5.3. Inherited branch and permitted secondary contrasts

The branch label that the frozen pipeline reports is “retrieval-only (06 mixed)”, which inherits S15’s POSITIVE STALE retrieval finding. Its registered sentence and the registered limitation that must accompany it are quoted in full:

> Replacing STALE distractors with evidence-type sessions of other scenarios (CF-SOURCE) lowers the all-gold recall@5 of the RRF hybrid by +12.6 points \[+9.6, +15.5\]; for the end-to-end pipelines tested, inflation was not established.

> Limitation: CF-SOURCE replaces distractors with evidence-type sessions of other scenarios, which also adds hard negatives (S15 secondary row s15a.hardneg); this end-to-end difference therefore does not separate inflation from harder interference, and the oracle-5 qualifier bounds reading interference only.

In the limitation, “this end-to-end difference” denotes the intended estimand; no admissible primary estimate exists. The branch combines inherited retrieval evidence with invalid end-to-end tests. It establishes neither a negative end-to-end result nor an upper bound on cue dependence. The final S15 result is byte-identical to the copy of S15’s results that S15c locked before it ran, so the registered rule for a changed parent result did not require a regenerated branch at adoption.

**Table D6. Eligible secondary and exploratory contrasts.** Differences are ORIG-N minus the counterfactual, in points. Each interval is the hull of ordinary 95% bootstrap and t intervals, not a Holm-adjusted primary confirmation.

| Analysis | Paired probes | Scenario count in the report’s export | Difference | 95% interval |
|----|---:|----|---:|----|
| Gold-pair-plus-three (Oracle-5), ORIG-N − CF-SOURCE | 561 | Not exported | −0.71 | \[−3.92, +2.48\] |
| RAG, CF-STYLE: ORIG-N read 1 against the single CF-STYLE read | 558 | 186 | −2.33 | \[−5.56, +0.90\] |

Both intervals in Table D6 span zero. The gold-pair-plus-three contrast supplies no positive qualifier for reading interference, and CF-STYLE remains exploratory by design and because its manipulation failed. Because the primaries are invalid, every row that depends on them is suppressed: the delta-minus-oracle contrast, the escalation sensitivities, the contrast subgroups, and the power and minimum-detectable-effect (MDE) rows at the observed SD. The lexical donor-overlap screen flags every paired valid probe (full context 300 of 300, memory 285 of 285, gold-pair-plus-three 561 of 561, and RAG 543 of 543). The screen does not discriminate: it neither validates source confusion nor proves universal contamination. No unflagged subgroup remains.

#### D.5.4. Descriptive copy and memory diagnostics

The copy heuristic requires an earlier equal request hash, sub-second observed latency, equal observed token counts, and, for successful reads, equal answer hashes. Missing metadata are not treated as matches. No control without the cache was sent, and the estimator was not adjusted. “Effective reads” means the mean number of non-flagged successful reads per probe, not a count of independent scenarios or of certified independent generations. Table D7 gives both measures for the primary cells.

**Table D7. Test reader copy diagnostics in the primary cells.** These classify successful reader attempts, including those whose later judgment is missing.

| Cell | Flagged of successful reads | Flagged (%) | Mean non-flagged reads per probe |
|----|---:|---:|---:|
| Memory CF-SOURCE | 86 of 900 | 9.556 | 2.7133 |
| Memory ORIG-N | 87 of 900 | 9.667 | 2.7100 |
| RAG CF-SOURCE | 165 of 1,701 | 9.700 | 2.7090 |
| RAG ORIG-N | 147 of 1,701 | 8.642 | 2.7407 |

The stage-level copy check, which uses the full request digests, flags 580 reader attempts and one judge attempt; no reader or judge attempt has too little evidence for the check. Memory extraction has no flagged attempts and 15 with too little evidence. Counts from differently scoped stage summaries overlap and cannot be added as disjoint totals. These are descriptive process checks, not a certification of the provider’s cache, a proof of unbiasedness, or a validation of interval coverage.

Each test memory condition has 100 final usable stores, with no failed memory additions and no invalid stores. The registered store-rebuild rule (D1) rebuilt one terminally failed CF-SOURCE extraction session and three ORIG-N sessions under new build epochs; these rebuilds were not retries of final binding judge calls. Two transport requeues in CF-SOURCE affected one store. Mean memories per store are 223.21 under CF-SOURCE and 283.71 under ORIG-N. Extraction sessions that failed terminally in earlier builds do not imply invalid final stores.

#### D.5.5. Incomplete auxiliary diagnostic and optional reader

The required auxiliary diagnostic, a rejudging of the reference packets by Gemini 3.5 Flash-Lite, is separate from the reference raters’ agreement, which passed. It was not waived after the primaries became invalid. Its development run stopped after 18 calls at the unchanged, conservative reserved-budget cap, before an agreement statistic was completed. The test diagnostic remains UNPERFORMED. The optional Gemini 3.8 Flash reader was not used, and that decision preceded any inspection of efficacy results. Neither a replacement judge nor a higher cap was introduced.

### D.6. Exposure, audits, and limits

The inherited population had prior input exposure and partly known original retrieval outcomes, and S15a’s retrieval outcomes on the successor population preceded testing (D.5.1). S15c’s single post-lock repair addressed the allocation of interrupted generations without changing registered populations, prompts, or rules; the original stop and the earlier history remain preserved.

Two separate recomputations from the saved outputs reproduced the reported retrieval arithmetic, validity counts, reference agreement, eligible secondary contrasts, and process summaries. They did not refit classifiers, rerun retrieval models, rate donor or rewrite semantics, certify provider behavior, or establish the complete exposure history.

At design, S15c had a probability of about .5 of a POSITIVE verdict at a true five-point difference, a ceiling set by the rule that the estimate be at least +5. Its power for equivalence in S15c-B2 was at most .13, with 100 memory scenarios and a planning scenario SD of 14–17 points; the MDE planning assumed scenario SDs of 12–20 points. No observed-power calculation is given for invalid primaries. Missing binding verdicts need not be random, and the copy diagnostics do not certify independent generations. CF-SOURCE changes interference along with the content source, and GLM-5.3-Flash judges answers from its own model family. Neither the passed agreement with the reference raters nor the complete reader execution repairs the final INVALID (K1) state of S15c-B1 and S15c-B2. No inflation, null, equivalence, or upper-bound conclusion is licensed. The registered protocol prohibits another successor study on these populations.

## E. Wrong-question retrieval atlas (S16)

### E.1. Protocol card

S16 measured atlas wrong-question retrieval: whether a fixed retriever retrieves a target’s gold evidence when it is queried with another item’s question, and whether that hit rate exceeds suitable query-free controls. Its primary setting is user-side text, hybrid retrieval by reciprocal rank fusion (RRF), and any-gold@5. A session’s retrieval score is the maximum over its scoring turns. A round-level unit contains one user turn and the assistant turns that follow it, although the assistant text is not scored; for LoCoMo and LoCoMo-Plus, both human speakers are retained. Because a unit’s scoring turns set both its retrieval score and its weight under the turn-weighted null, the unit definition affects both the retrieval outcome and the null. The atlas draws its ten wrong questions from a different group, whereas S15a’s same-type wrong-question retrieval (Appendix D.1) draws them from the same question type. STALE’s atlas rate, 41.40%, therefore differs from S15a’s 42.08%. With S15’s peers, the current retrieval path moves STALE’s rate by only −0.017 points (K4b in Table E6), so the difference comes from the peer rules.

**Card E. S16 protocol card.** Registered definitions; retrieval settings are in Appendix K.3.

| Protocol element | Registered definition |
|----|----|
| Retriever | BM25 Okapi (Robertson and Zaragoza 2009) plus bge-small dense retrieval (Xiao et al. 2024), fused by RRF (Cormack et al. 2009) with constant 60; no cross-encoder |
| Wrong questions | Ten eligible peers per target, taken in a fixed hash order from a different group; peers with evidence overlap, duplicate questions, or near-duplicate evidence are excluded |
| Item outcome | The item’s wrong-question hit rate (QI) is its mean any-gold@5 hit over those ten questions |
| Chance controls | Exact uniform sampling; Plackett–Luce sampling weighted by nonempty scoring turns; independent random turn scores followed by the same maximum pooling (the random-score null) |
| Matched placebo | 20 non-gold sets matched within the haystack on user-character decile, turn-count decile, and position tercile; each set is evaluated on the same wrong-question rankings |
| Family estimands | P: mean item CE against turn-weighted chance; S: mean item CE against matched placebo on supported items |
| Scale and margins | $\mathrm{CE} = (\mathrm{QI} - \mathrm{null})/(1 - \mathrm{null})$; practical threshold .05; equivalence margin ±.03 |
| Inference | The wider of a 10,000-draw two-way cluster bootstrap (target group × peer group) and a CR1 cluster-robust t interval; separate Holm families at .05 |

As in the main text (§3.3), this appendix calls the effect the chance-corrected excess (CE). The atlas’s internal report labels this quantity κ; it is not Cohen’s κ.

The normalization occurs within each item before averaging, so a displayed difference between two benchmark-wide percentages is not itself the registered CE. BEAM’s family estimands weight its three length splits equally, whereas the atlas percentages keep the stored item weights. This distinction applies to both the CE and the family point contrasts, so the atlas percentages cannot replace the family estimates. Family-S intervals condition on each item’s observed placebo denominator and therefore do not represent the full uncertainty of a ratio estimate.

The admission rule (D1) first determines whether MemOps-round enters either family. The cue-dominance check (K3) then labels a row cue-dominated if any registered query-blind feature reaches a direction-free single-feature AUROC (within-haystack) of .90, averaged over items. A cue-dominated primary row still shows its tier, but only its placebo estimand may be interpreted. A family-S row needs common support for at least 80% of its primary, non-starved items (items with ten eligible peers). A row that fails support keeps its family slot with p = 1 and no tier. The registration fixed these rules before any retrieval ran. The eight registered single-feature priors rank a haystack’s units by characters, turns, mean turn length, or position, each in both directions (Appendix K.4). The best of the eight is a selected maximum and is descriptive only.

### E.2. Complete atlas at hybrid any-gold@5

We fixed the primary target selection before any retrieval ran. For HaluMem we excluded 369 items whose prefix haystacks have at most ten nonempty units and applied a cap of 60 targets per user; for BEAM we excluded 72 targets from four nonmonotonic conversations; for MemOps we selected one item per generated file; and for LoCoMo we capped targets at 120 per conversation. Table E1 gives the resulting target counts. The MemOps sample spans 97 registered groups formed by shared gold hosts, while LoCoMo and LoCoMo-Plus each span ten host conversations. These sampling and unit choices are ours, so differences between atlas rows are not comparisons of benchmark validity.

**Table E1. Full atlas: populations and null controls.** All rates are percentages of hybrid any-gold@5 on user-side text. Status codes: P, admitted family member; D, descriptive or sensitivity row; X, exploratory; R, reference. In the text, MemOps-round and MemOps-session name the MemOps / round and MemOps / session rows. MemOps-round is D because it failed admission. For LongMemEval-S, the legacy anchor (K4a in Table E6) is the reference, while this row, under the current peer rules and retrieval path, is exploratory. Supported QI and placebo use exactly the same supported items; below 80% support, these two columns describe only that subset. MemOps-session is shown only because the registered atlas display includes it, and no wrong-question inference is made from it. The paragraph below the table defines the two sensitivity rows.

| Benchmark / unit | Status | N | QI | Uniform | Turn-weighted | Random-score | Supported QI | Placebo | Support n/N |
|----|----|---:|---:|---:|---:|---:|---:|---:|---:|
| HaluMem-Medium / prefix session | P | 1,200 | 15.82 | 16.90 | 17.99 | 18.01 | 9.96 | 10.58 | 250/1,200 |
| BEAM / round | P | 1,537 | 4.44 | 4.84 | 4.84 | 4.85 | 4.30 | 4.74 | 1,518/1,537 |
| MemOps / round | D | 403 | 27.97 | 6.32 | 6.32 | 6.32 | 27.51 | 18.98 | 390/403 |
| MemOps / session | D | 403 | 68.96 | 20.81 | 32.52 | 32.50 | 57.78 | 38.28 | 45/403 |
| HaluMem-Medium / full-history session | D | 1,200 | 7.71 | 7.92 | 8.11 | 8.11 | 7.51 | 6.91 | 453/1,200 |
| LoCoMo / session | X | 1,158 | 24.75 | 23.44 | 24.35 | 24.36 | 24.14 | 20.83 | 133/1,158 |
| LoCoMo / citation sensitivity | D | 1,158 | 25.02 | 23.44 | 24.35 | 24.36 | 24.89 | 21.65 | 133/1,158 |
| LoCoMo-Plus / turn | X | 401 | 2.99 | 1.67 | 1.67 | 1.67 | 2.99 | 1.15 | 401/401 |
| STALE / session | R | 1,200 | 41.40 | 19.18 | 14.98 | 14.97 | 41.18 | 16.62 | 756/1,200 |
| LongMemEval-S / session | X | 470 | 22.04 | 18.93 | 21.06 | 21.09 | 19.77 | 22.57 | 176/470 |
| LongMemEval-S / round | D | 467 | 5.61 | 3.84 | 3.84 | 3.84 | 5.61 | 5.11 | 467/467 |

The two sensitivity rows keep the target sample of a primary row. LoCoMo / citation sensitivity adds to the peer pool the 55 citation-flagged items that we excluded from LoCoMo’s primary population. It differs from a larger sensitivity analysis that also adds these 55 items as targets (1,213 items; CE over turn-weighted chance .012 \[−.002, .028\]). HaluMem-Medium / full-history session keeps the prefix row’s targets but uses each target’s full history as the haystack. We also excluded BEAM’s targets from the four nonmonotonic conversations from its primary population; they enter only a sensitivity analysis, which gives a CE over turn-weighted chance of −.005 \[−.013, .004\] on 1,609 items, against −.004 for the primary population.

**Table E2. Remaining atlas controls and query-blind priors.** Rates are percentages of any-gold@5 on the Table E1 populations. Cross-benchmark uses ten wrong questions from other benchmarks; different type uses only peers of another question type; constant averages the 20 registered constant queries; true question uses the item’s own question. The best prior is the selected maximum of the eight registered single-feature rankings (E.1), not a separately confirmed effect, and its success does not attribute the wrong-question hits to that feature. MemOps-session has no QI interpretation.

| Benchmark / unit | Cross-benchmark | Different type | Constant | True question | Best query-blind prior | Prior hit |
|----|---:|---:|---:|---:|----|---:|
| HaluMem-Medium / prefix session | 15.56 | 15.43 | 15.23 | 82.83 | Latest position | 94.17 |
| BEAM / round | 4.60 | 4.14 | 4.60 | 67.99 | Earliest position | 6.44 |
| MemOps / round | 14.34 | 27.05 | 16.15 | 88.59 | Largest mean turn length | 71.96 |
| MemOps / session | 48.68 | 69.11 | 54.67 | 98.51 | Most characters | 100.00 |
| HaluMem-Medium / full-history session | 6.97 | 7.64 | 7.92 | 75.75 | Smallest mean turn length | 7.92 |
| LoCoMo / session | 23.98 | 24.06 | 24.30 | 85.23 | Most characters | 30.40 |
| LoCoMo / citation sensitivity | 24.34 | 24.67 | 24.30 | 85.23 | Most characters | 30.40 |
| LoCoMo-Plus / turn | 1.32 | 2.79 | 0.47 | 5.24 | Latest position | 8.23 |
| STALE / session | 22.52 | 41.27 | 23.81 | 97.00 | Fewest turns | 96.08 |
| LongMemEval-S / session | 21.49 | 21.72 | 14.59 | 97.87 | Latest position | 23.83 |
| LongMemEval-S / round | 4.56 | 5.67 | 2.02 | 91.43 | Fewest turns | 3.85 |

### E.3. Registered families, exclusions, and gates

**Table E3. Family P: CE over turn-weighted chance.** Holm-adjusted intervals are 97.5% intervals ($\alpha = .025$): Holm rejects neither member at its first step (.05/2), so both members stay at that stopped level. The ordinary 95% intervals are shown separately. QI and null percentages are item-weighted displays; BEAM’s CE and point contrast are equal-split estimates. Point contrasts are in points.

| Member | Items / clusters | QI (%) | Null (%) | CE | Holm-adjusted 97.5% interval | 95% interval | Point contrast \[95%\] |
|----|---:|---:|---:|---:|----|----|----|
| HaluMem-Medium / prefix session | 1,200 / 20 users | 15.82 | 17.99 | −.032 | \[−.052, −.012\] | \[−.049, −.015\] | −2.18 \[−3.29, −0.98\] |
| BEAM / round | 1,537 / 86 conversations | 4.44 | 4.84 | −.004 | \[−.014, .006\] | \[−.013, .005\] | −0.34 \[−1.08, +0.48\] |

**Table E4. Family S: CE over matched placebo.** Holm-adjusted intervals are 97.5% intervals ($\alpha = .025$). The support denominator is assessed before estimand-specific exclusions. HaluMem’s supported-subset atlas percentages remain in Table E1; no inferential percentage or contrast is substituted into its unsupported family row.

| Member | Support n/N (%) | Analyzed items / clusters | Supported QI (%) | Placebo (%) | CE | Holm-adjusted 97.5% interval | 95% interval | Point contrast \[95%\] |
|----|---:|---:|---:|---:|---:|----|----|----|
| HaluMem-Medium / prefix session | 250/1,200 (20.8) | 0 / 0 | NA | NA | NA | NA | NA | NA |
| BEAM / round | 1,518/1,537 (98.8) | 1,518 / 86 | 4.30 | 4.74 | −.007 | \[−.020, .006\] | \[−.018, .005\] | −0.33 \[−1.24, +0.64\] |

**Table E5. Complete family verdicts, including excluded candidates.** The practical threshold is CE = .05 and the equivalence margin ±.03 throughout. A row is EQUIVALENT when its Holm-adjusted interval, the wider of the bootstrap and CR1 intervals, lies strictly inside the margin; the reported p-values of the two one-sided tests (TOST) do not enter the verdict.

| Family | Candidate | Raw superiority p | Holm p | TOST p (reported only) | Tier or outcome | Gate or interpretation limit |
|----|----|---:|---:|---:|----|----|
| P | HaluMem-Medium / prefix session | 1.000 | 1.000 | .652 | REVERSED | Cue-dominated (K3: position, single-feature AUROC .968); tier not interpreted |
| P | BEAM / round | .920 | 1.000 | $9.4 \times 10^{-9}$ | EQUIVALENT | Valid; all three splits estimable |
| P | MemOps / round | — | — | — | Not admitted (D1) | User-character single-feature AUROC .976; descriptive only |
| S | HaluMem-Medium / prefix session | 1.000 | 1.000 | 1.000 | NO-COMMON-SUPPORT; no tier | Support 20.8%, below 80%; family slot kept with p = 1 |
| S | BEAM / round | .939 | 1.000 | $1.6 \times 10^{-5}$ | EQUIVALENT | 19 items lack support; no supported item has an undefined CE |
| S | MemOps / round | — | — | — | Not admitted (D1) | Same membership rule as family P |

Because MemOps-round was not admitted, both families have two members, and Holm rejects neither superiority test (Tables E3–E5). In family P, no item was excluded for a degenerate null, incompleteness, or lack of support; exclusion for lack of support applies only to family S, where it removes 19 BEAM items. HaluMem’s supported items include none with an undefined CE. No bootstrap replicate was dropped. BEAM’s equal split weights are those of the registered population and were not recomputed after exclusions. With these weights, its family point contrast is −0.34 points, whereas the difference of the item-weighted means is about −0.40 points.

**Table E6. Operational and interpretation gates.** These are the checks and outcomes that the S16 run recorded; none was rerun for this appendix. The K labels are S16’s own and differ from the K labels of S15 and S15c.

| Gate | Registered requirement | Recorded outcome |
|----|----|----|
| K1 | At least 98% of gold labels resolved, and the registered population and parity checks pass | All applicable checks passed |
| K2 | MemOps quote-verification failure at most 2%; no unresolved BEAM evidence outside the registered exceptions | All applicable checks passed |
| K3 | Every registered single-feature AUROC (within-haystack) below .90; otherwise the row is cue-dominated | HaluMem-Medium position .968; BEAM maximum .708; MemOps-round characters .976; MemOps-session maximum .990; STALE maximum 1.000 |
| D1 | All three MemOps-round admission features below .90 | Failed; families P and S each keep two members |
| K4a | At most 12 of 12,000 legacy STALE hit indicators differ from S15; complete LongMemEval-S anchor within 0.5 points | STALE 1 of 12,000 differs; LongMemEval-S 0 of 4,700 |
| K4b | STALE new-path difference at most 1 point with S15’s peers | −0.017 points; passed |
| K4c | Uniform-placebo calibration within four Monte Carlo standard errors | All 11 files passed |
| K5 | Four-hour active compute limit and registered fallback | No fallback and no incomplete job |
| K6 | At most 5% of targets with fewer than ten peers | No sampled target starved |
| Family-S support | Common support for at least 80% of primary, non-starved items | HaluMem-Medium failed (20.8%); BEAM passed (98.8%) |

### E.4. Interpretation across populations

BEAM supports the narrow registered equivalence statement for this retriever stack and these units on both nulls. That is a bound within the specified margin, not a certificate that the benchmark lacks every cue. HaluMem-Medium yields no interpretable primary conclusion: position triggers K3, and insufficient placebo support prevents a full-population secondary conclusion. Gold occupies the last unit for 868 of its 1,200 prefix items. On the same items’ full histories, the CE over turn-weighted chance is −.005 \[−.015, .006\] and placebo support is 453 of 1,200 items; the maximum single-feature AUROC there is .561, below the K3 threshold. That sensitivity analysis remains descriptive.

MemOps-round’s supported placebo contrast is descriptively CE = .099 \[.063, .134\] on 390 of 403 items, outside both confirmatory families. Its groups connect shared gold hosts, while reused non-gold hosts still enter rankings across groups, so the interval may be too narrow. For MemOps-session, the only permitted statement is that the inserted gold conversations are longer; its longest-first prior reaches 100.00% (Table E2). This favorable query-blind outcome was known before the study was frozen.

The remaining intervals in this subsection are descriptive 95% intervals (the wider of the bootstrap and CR1 intervals), without confirmatory tiers. LoCoMo gives CE = .008 \[−.014, .030\] over turn-weighted chance, and LoCoMo-Plus gives .013 \[.004, .023\]. LoCoMo’s placebo support is only 133 of 1,158 items, so its matched comparison cannot describe the full population. STALE is cue-dominated: its non-ASCII and typographic-marker features both reach a single-feature AUROC of 1.000. Its CE over turn-weighted chance, .311 \[.283, .339\], is reported but not interpreted, and the matched comparison applies only to 756 of its 1,200 items. On that subset, QI is 41.18% against a placebo rate of 16.62%, a CE of .272 \[.231, .314\]. No conclusion extends from that comparison to the unsupported items. No placebo estimand reaches the registered POSITIVE tier that a construction-cue claim would require.

**Selection null and design power.** In a post hoc check, the selected best prior exceeds a conservative bound on its selection null for STALE, the HaluMem prefix haystacks, both MemOps rows, LoCoMo, and LoCoMo-Plus, but not for BEAM or LongMemEval-S. The bound assumes independent items and ignores shared haystacks, so it is a descriptive comparison, not calibrated inference. By design, BEAM could often resolve equivalence (an EQUIVALENT verdict in 75–99% of simulated runs at a true CE of 0), while HaluMem-Medium, with 20 user clusters, almost never could (at most 10.6%).

**Fair nulls on LongMemEval-S.** The legacy reference and the current atlas row differ in both peer rules and retrieval path. The legacy gap between QI and legacy uniform chance satisfies the following approximate identity, in points:

$5.038027 \approx 1.872340 + 2.134398 + 0.981927 + 0.049361$

The four terms are, in order: legacy QI minus current QI (a reduction under the combined change of peer rules and retrieval path); current turn-weighted minus current uniform chance; current QI minus current turn-weighted chance; and current minus legacy uniform chance. This is bookkeeping between stored aggregates, not a causal decomposition. A path-only control exists for STALE but not for LongMemEval-S, so the first term cannot be allocated to the peer rules alone. The current residual corresponds to CE = .011 \[−.017, .041\], so positive effects up to the upper bound remain compatible with this exploratory interval. The placebo comparison uses only 176 of 470 items (supported QI 19.77%, placebo 22.57%) and supports no conclusion about the full row.

### E.5. Exposure, deviations, and recomputation

The registration disclosed query-blind summaries of MemOps and HaluMem seen before the freeze, including HaluMem’s last-unit structure. All decision rules were fixed before any new row was retrieved. Registered departures from the design include the MemOps grouping rule, the CR1 interval of the item mean, power calculations run after the freeze as a design diagnostic, and the inclusion of sensitivity-only items in the peer pool. The placebo interval conditions on the observed placebo denominators, and interval containment replaced a target-only TOST as the equivalence rule. The atlas figure (Figure 2 of the main text) was drawn after the run from the stored aggregates; its two panels separate full-population and supported-subset comparisons. The waiting time for compute slots was not recorded per job. None of these reporting and recording qualifications changes the tables above.

A recomputation from the saved outputs reconstructed the family estimates, the analytical inference, the support masks, and the atlas values. Its bootstrap check used 750 draws instead of reproducing the registered 10,000-draw endpoints, and the verdicts were checked separately against the stored full-draw intervals. It did not rerun the query-blind feature extraction, the Monte Carlo null generation, the corpus conversion, or the retrieval. Agreement among the stored outputs shows that they are numerically consistent, not when or in what order the steps ran. The interpretation in E.4 is limited to this retriever stack, these unit definitions, and these registered populations. It neither measures a memory system’s reliance on cues nor quantifies inflation of published scores.

## F. LLM regrade: estimators, ambiguity, and uncertainty

<a id="appendix-f1"></a>

### F.1. Packet and adjudicators

**Protocol card.** The packet sampled 100 answers that the original LLM judges had graded, oversampling judge disagreements: 50 answers of the S10b STALE ladder (claim C2) and 50 S11 replica answers (claim C3). Adjudicator G1 (Claude Sonnet 5.5) graded the items in five batches of 20, one context per batch. Adjudicators G2 (Gemini 3.8 Flash, thinking level high) and G3 (GPT-6.1 Sol, reasoning effort medium) graded each item in a separate call. Appendix K gives the adjudicators’ instructions (K.6) and settings (K.7). G1 is a different model of the same family as Claude Opus 5.5, the earlier adjudicator of the S10c, S11b, and S11c gates. G2 shares its vendor with Gemini 3.5 Flash-Lite, the secondary STALE judge, which also read some C2 answers. G3 shares a vendor with no judge or reader of this packet. All three adjudicators received the same rubrics, so their agreement is not evidence of independent judgment, and their wrapper prompts and recorded reasoning also differed. There is no human ground truth; Appendix J gives the author’s labels on the same packet, from one informed grader.

**Table F1. Adjudicator labels.** Counts over the 100 packet items. Determinate labels are those not marked ambiguous, by claim (C2, S10b ladder; C3, S11 replicas). No item is missing. Excluding ambiguous labels changes both the adjudicator’s denominator and the original judge’s corresponding positive rate.

| Adjudicator | Items labeled | Ambiguous | Determinate, C2 / C3 |
|-------------|--------------:|----------:|---------------------:|
| G1          |           100 |        11 |              45 / 44 |
| G2          |           100 |         5 |              46 / 49 |
| G3          |           100 |         0 |              50 / 50 |

For claim C2, the analysis reweights the surviving determinate items of stratum $s$ by $N_s/n_{\mathrm{surv},s}$, the stratum’s frame count over its number of surviving items. For C3, it keeps each surviving item’s inverse-inclusion weight in a Hájek ratio over the surviving items. A population interpretation of either estimator needs an assumption about the ambiguous labels, such as missing at random within strata; adjudicator G3 marked no label ambiguous. In this packet raw agreement is below design-weighted agreement (Table F2), but oversampling judge disagreements does not guarantee that direction against another adjudicator.

**Table F2. Agreement of the original judges with each adjudicator.** Percentages, except κ. GLM is the binding GLM-5.3-Flash judge, and Flash-Lite the secondary Gemini 3.5 Flash-Lite judge of claim C2. Wilson intervals are sample-arithmetic intervals, not clustered-design intervals. The design-weighted values have no confidence intervals (F.4). By a decision recorded in the registration of adjudicator G3, no interpretation rests on the Flash-Lite rows at judge-disagreement points.

| Claim / original judge | Adjudicator | Raw agreement \[Wilson 95% interval\] (n) | Raw κ | Design-weighted agreement | Design-weighted κ | Design-weighted positive rate, judge / adjudicator |
|----|----|----|---:|---:|---:|----|
| C2 / GLM | G1 | 95.6 \[85.2, 98.8\] (45) | .90 | 99.6 | .99 | 78.5 / 78.0 |
| C2 / GLM | G2 | 93.5 \[82.5, 97.8\] (46) | .85 | 99.3 | .98 | 78.3 / 78.2 |
| C2 / GLM | G3 | 88.0 \[76.2, 94.4\] (50) | .74 | 93.9 | .83 | 78.3 / 72.8 |
| C2 / Flash-Lite | G1 | 66.7 \[52.1, 78.6\] (45) | .31 | 97.1 | .92 | 76.7 / 78.0 |
| C2 / Flash-Lite | G2 | 69.6 \[55.2, 80.9\] (46) | .38 | 97.4 | .92 | 76.9 / 78.2 |
| C2 / Flash-Lite | G3 | 68.0 \[54.2, 79.2\] (50) | .35 | 92.1 | .79 | 76.9 / 72.8 |
| C3 / GLM | G1 | 93.2 \[81.8, 97.7\] (44) | .86 | 98.0 | .95 | 67.1 / 68.1 |
| C3 / GLM | G2 | 93.9 \[83.5, 97.9\] (49) | .88 | 98.1 | .96 | 64.9 / 65.9 |
| C3 / GLM | G3 | 90.0 \[78.6, 95.7\] (50) | .80 | 96.5 | .92 | 65.4 / 68.8 |

<a id="appendix-f2"></a>

### F.2. Adjudicator agreement and the sparse pointer result

**Table F3. Agreement between adjudicators.** Jointly determinate items only. Each pair meets the per-claim rule $\kappa \geq .60$, which permits the three-adjudicator agreement wording; it does not validate the judge.

| Pair | C2: agreement count / n; κ | C3: agreement count / n; κ | Pooled: agreement count / n; κ |
|----|----|----|----|
| G1–G2 | 41/42; .945 | 42/43; .953 | 83/85; .950 |
| G1–G3 | 41/45; .800 | 41/44; .861 | 82/89; .833 |
| G2–G3 | 43/46; .858 | 45/49; .836 | 88/95; .847 |

In the pointer arm group of claim C2, adjudicator G3’s design-weighted pass rate is 74.1%, against 86.6% for the GLM-5.3-Flash judge. Two of the 17 sampled pointer items, both hybrid-5 answers, produce this 12.4-point gap; one of them, in a high-weight stratum, contributes about 12.2 points. In the other arm groups the net difference is zero, because G3’s disagreements with the judge offset each other. This is evidence from a sparse stratum, not established leniency of the judge toward pointer arms. S17-B2 (Appendix C.4) rejudged pointer answers from a different population and has no non-pointer controls. On both items, the author, as human grader, sided with the GLM-5.3-Flash judge (post hoc; Appendix J.5).

<a id="appendix-f3"></a>

### F.3. Conditional flip confirmation and the estimand E6 erratum

Estimand E5 sampled one judge-disagreeing replica pair (a flip) from each of 15 unstable questions (part P); estimand E6 added 10 random pairs (part R), all of which were judge-agreeing. Let $d$ be the judge’s label disagreement on the frame, in percent. Let $q_1$ be the probability that an adjudicator also finds a disagreement when the judge’s labels disagree, and $q_0$ that probability when they agree. Full-frame adjudicator disagreement is then $d q_1 + (100 - d) q_0$, in percent. Because no part-P pair is reversed, estimand E5 equals $q_1$ here; it identifies neither full-frame disagreement nor the direction of the judge’s bias.

**Table F4. Estimands E5 and E6 by adjudicator.** Estimand E5 shares are pair-weighted percentages; $G_{\mathrm{h}}$ values are in points. Ambiguity ranges and envelopes are not confidence intervals. Excluding ambiguous pairs changes the denominator, so the exclusion point need not lie inside the fixed-denominator completion bounds.

| Quantity | G1 | G2 | G3 |
|----|---:|---:|---:|
| Confirmed disagreement / decided E5 pairs | 8/10 | 12/14 | 10/15 |
| E5, ambiguous pairs excluded (%) | 80.9 | 87.6 | 73.9 |
| E5, ambiguous pairs counted as not confirmed (%) | 59.7 | 80.2 | 73.9 |
| E5, loose optimistic fill of ambiguous pairs (%) | 85.9 | 88.7 | 73.9 |
| E5, sharper completion upper bound (%) | 80.2 | 80.2 | 73.9 |
| Disagreeing / decided random pairs (part R) | 0/9 | 0/10 | 0/10 |
| Stored E6 ratio $G_{\mathrm{h}}$ (points) | 6.668619 | 7.228057 | 6.090533 |
| Literal HT observed contribution (points) | 5.345857 | 7.180530 | 6.611149 |
| Stored ambiguity range, lower–upper | 4.924881–11.256639 | 6.615077–7.314468 | 6.090533–6.090533 |
| HT realized-sample ambiguity envelope | 5.345857–12.712308 | 7.180530–7.939705 | No unresolved label |

The frozen plan specifies estimand E6 as Horvitz–Thompson (HT) totals over the 30,981-pair frame, whereas the locked code normalizes within the two domains of 5,110 judge-disagreeing and 25,871 judge-agreeing pairs. Because the sampled weight sums (5,546.8 and 31,140) differ from these domain sizes, the two estimators give different values. This is a conflict between two frozen specifications, not evidence of tuning after the grades. Unless the unresolved grades receive an assumption, the HT values under exclusion are observed contributions, not full-frame estimates.

The stored estimand E6 equals 8.25 points, the judge’s own $G_{\mathrm{mean}}$ on this frame, times the decided share of confirmed disagreement in part P, because the sampled part-R term is zero. Its bootstrap keeps that zero: adjudicator G3’s interval, \[4.06, 7.73\], varies only the part-P share. The ceiling of 8.25 therefore depends on the observed labels and is not a population bound. The frame also differs from that of S11’s $G_{\mathrm{mean}}$ of 8.12 points on 671 questions, so $G_{\mathrm{h}}$ is neither a corrected S11 gap nor evidence of the direction of the original judge’s bias. Replacing the zero-event hidden-disagreement component by its one-sided 95% bound would give $G_{\mathrm{h}}$ values of 16.9–18.5 points across adjudicators G1–G3, a conditional sensitivity rather than a joint confidence bound. Appendix J.4 gives the values of estimands E5 and E6 from the author’s human grade, which has the same zero-event structure (0 of 10 random pairs disagreeing).

### F.4. Precision and computational provenance

Most strata have only two to seven determinate items, often with no observed disagreement, so empirical bootstrap intervals can degenerate. A separate post hoc model treats the determinate items within each stratum as independent binomial draws of equal weight and the ambiguous labels as missing at random; it ignores the dependence within question pairs and the unequal S11 weights. Its grouped point equals the C2 primary statistic but is a different statistic for C3.

**Table F5. Post hoc grouped-binomial sensitivity, by adjudicator (G1 / G2 / G3).** Percentages. CP is a one-sided Clopper–Pearson upper bound on each stratum’s disagreement rate, Bonferroni-adjusted over the strata and propagated through the grouped statistic. The Jeffreys columns give the 2.5% and 97.5% quantiles of a Monte Carlo propagation (20,000 draws) of a $\mathrm{Beta}(x + 0.5, n - x + 0.5)$ posterior for each stratum, with $x$ disagreements among $n$ determinate items. This prior gives each zero-disagreement stratum (two to seven items) a posterior mean disagreement of $0.5/(n + 1)$, about 6–17%. The quantiles can therefore lie below the observed grouped point, and in the C2 rows of adjudicators G1 and G2 they do (e.g., 99.56 against 79.92–97.16). They show sensitivity to that prior, not uncertainty around the point. All of these are model-specific sensitivity values, not uncertainty intervals for the primary estimates, exact design-based bounds, or unconditional population limits. Comparisons across adjudicators are not significance tests. Appendix J.2 gives the grouped values of the author’s human grade in the same convention.

| Claim, original judge | Grouped agreement point | CP–Bonferroni lower value | Jeffreys 2.5% and 97.5% quantiles |
|----|----|----|----|
| C2, GLM | 99.56 / 99.28 / 93.87 | 32.91 / 33.24 / 28.67 | 79.92–97.16 / 80.05–97.03 / 73.39–95.15 |
| C2, Flash-Lite | 97.08 / 97.36 / 92.13 | 31.93 / 32.51 / 27.86 | 78.04–95.05 / 78.29–95.43 / 71.60–93.56 |
| C3, GLM | 96.28 / 96.79 / 94.83 | 68.26 / 69.95 / 67.65 | 83.13–98.00 / 84.19–98.21 / 81.91–96.88 |

The consensus view keeps the 83 items on which adjudicators G1 and G2 give the same determinate grade and drops the other 17. Selecting on agreement can move agreement with the original judge in either direction, and it does not show that the dropped items are harder. In strata where the original judge’s label is constant, κ is undefined under the plan, including the cells where the output prints zero.

Two separate recomputations from the saved outputs reproduced the arithmetic for adjudicator G3. The estimator, domain, and precision corrections described above are kept here. The runtime model identities, reasoning effort, costs, isolation, and access history rest on the run records alone and were not recomputed. Arithmetic agreement neither certifies semantic correctness nor reopens S11c’s failed judge gate.

## G. Null-memory policies and the failed forgetting closure

### G.1. Null-memory policies and scoring boundaries

The null-policy study (S1) examined whether a public metric rewards an operation that discards the intended memory utility. Its protocol distinguishes the public forgetting score from a stricter requirement that the facts to be kept are preserved. The null-memory policies are diagnostic baselines and analytic scoring checks, not proposed memory systems. ForgetEval’s public score (Yang 2026) rewards erasing targeted material without necessarily checking that unrelated material is preserved, so the study reports both objectives and keeps the failed strict criterion.

**Table G1. Forgetting-score null policies.** The two policy rows report public-scoring successes in the named ForgetEval subsets, not end-to-end memory accuracies.

| Policy or check | Adversarial subset | Template subset | Interpretation |
|----|---:|---:|----|
| Wipe plus replacement | 231/385 = 60.0% | 750/1,000 = 75.0% | Public forgetting score can reward discarded utility |
| Store nothing, or wipe without replacement | 96/385 = 24.9% | 350/1,000 = 35.0% | Nonzero score without useful retained memory |

Strict keep-set derivability is a separate coverage check: 286 of 385 adversarial items (74.3%) and all 1,000 template items have a derivable strict keep set. These are coverage rates, not policy successes, and the adversarial coverage misses the registered 80% threshold. The retrospective template-preservation check turns the wipe policy’s 750 public passes into zero when the construction-derived keep labels are enforced. This is a diagnostic use of those labels, not a newly registered external evaluation. An always-abstain policy scores 446 of 1,986 LoCoMo questions (22.5%) under the released scorer, if it receives no credit on any other question; this is arithmetic on released numbers, not a new judge run. On the single-hop FactConsolidation task from MemoryAgentBench (Hu et al. 2026) at 262k tokens, BM25 retrieval with a keep-latest rule contains the answer in 75 of 100 cases. This is an oracle-reader substring surrogate, not the accuracy of a model.

**Table G2. Harness options on LoCoMo: category-conditioned prompting and gold-selected best of three.** Each entry is a main effect from S1’s registered 2 × 2 × 2 factorial of harness options, in points of the harness’s continuous LLM-judge score (0–100; judge GLM-5.3-Flash) on the LoCoMo test questions of categories 1–4. Each difference is the option switched on minus switched off, averaged over the other two factors. The category-conditioned baseline gives the reader gold-category prompts and a category-specific retrieval depth (30 instead of 20 turns for multi-hop questions). The gold-selected best of three keeps, of three samples, the first with the highest judge score against the gold answer; it is compared with the first sample alone, and both are scored by a fresh judge draw. Intervals are the S1 report’s headline intervals: 95% bootstrap intervals over questions. Because the first option uses category information and the second uses the gold answer for selection, neither is an ordinary deployable comparison.

| Option | Gemini 3.5 Flash-Lite reader: difference \[interval\] | GLM-5.3-Flash reader: difference \[interval\] |
|----|---:|---:|
| Category-conditioned baseline | +7.21 \[+5.45, +9.00\] | +0.50 \[−0.52, +1.61\] |
| Gold-selected best of three | +2.98 \[+2.33, +3.70\] | +1.15 \[+0.77, +1.55\] |

The conversation-cluster sensitivity intervals are \[+5.59, +8.73\] and \[+2.28, +3.88\] for the Gemini 3.5 Flash-Lite reader, and \[−0.64, +2.10\] and \[+0.78, +1.51\] for the GLM-5.3-Flash reader. These diagnostics use 692 (Gemini 3.5 Flash-Lite reader) and 691 (GLM-5.3-Flash reader) test questions in four conversations. Because the category-conditioned gain is +7.21 points with the Gemini 3.5 Flash-Lite reader but +0.50 with GLM-5.3-Flash, harness effects of category-conditioned prompting depend on the reader; this rests on two reader stacks only. The four test conversations and the gold and category information that the options use rule out interpreting the table as a general ranking of published memory systems. The failure of the strict preservation criterion remains the registered outcome, despite the large public scores of the null policies. In a post hoc check, the GLM-5.3-Flash best of three often drew on fewer than three distinct samples, because the model proxy returned some redraws as copies (Appendix H.1). Its +1.15 therefore does not come from three independent draws, and the direction of the resulting bias is not identified. The Gemini 3.5 Flash-Lite redraws were regenerated, but in 13.8% of that reader’s test rows the second judge draw copied an earlier draw, which can raise the best of three slightly.

### G.2. Forgetting closure: a failed practical target

The forgetting-closure study (S14) asked whether identifying linked information can reduce collateral loss while meeting a prescribed forgetting objective. Collateral is the number of non-revealing comments deleted divided by the store size, averaged over requests. Its exploratory starting point was already known during design. With the best zero-shot similarity ranker at top five, 65.0% \[59.3, 70.5\] of 638 nonempty test requests from 150 authors kept at least one revealing comment outside the top five, and closing every request by ranking depth cost a collateral of 38.6% \[35.5, 41.6\]. These values motivated the study but are not a fresh confirmation.

The registered practical target is not supported. At nominal $\alpha = .10$, the GLM-5.3-Flash scan’s collateral is 45.7% \[42.9, 48.8\], against 50.1% for the logistic-regression comparator, a difference of −4.5 points \[−7.6, −1.1\]. When calibration uncertainty is also resampled, the difference is −4.4 points \[−12.1, +2.3\]. Coverage is 94.0%, but the scan misses the required collateral ceiling of 30% and the improvement margin of 11 points. The macro AUROC for ranking revealing comments is .887 against .859, a difference of +.029 \[+.015, +.047\]: its point estimate exceeds the .02 margin, but its lower confidence bound does not.

The implemented nonincreasing envelope selected a full wipe, whose collateral is 86.7%, against 45.7% for label closure, a ratio of 1.90. This result does not establish that every interior threshold or every alternative risk-control construction fails. The semantic probe also finds that, after the labeled revealing comments are deleted, six of eight tested attributes remain at least 10 points above their prior. Label-level closure therefore does not establish semantic forgetting in this experiment, and the negative result supplies no supported memory method.

## H. Post hoc checks, provenance, and release boundaries

<a id="appendix-h1"></a>

### H.1. Descriptive follow-ups and their corrections

The follow-ups in this section were designed after the registered results were visible, and they leave every registered gate and study verdict unchanged. The study archive records the recomputation of each follow-up from the saved outputs, together with explicit limits on what was recomputed; a recomputation is not a blinded confirmation.

For the replica studies, among answer pairs that were byte-identical and received the same recorded judge prompt, the judge’s labels still disagreed in 59 of 5,429 S11 pairs, 13 of 1,850 S11c original-extractor pairs, and 17 of 1,792 S11c alternate-extractor pairs. These conditional disagreement rates are 1.087%, 0.703%, and 0.949%, respectively, and the pairs account for 1.20%, 0.73%, and 0.90% of all disagreeing pair cells in the corresponding analyses. Matches of normalized text answer a different question: normalization can erase distinctions, and token-set overlap does not establish semantic equality. Neither kind of match gives an identified lower bound on judge-caused disagreement.

Setting selected disagreeing pair cells to agreement is a sensitivity analysis at the level of pair cells. Because one replica can receive incompatible labels across different pairs, the operation need not correspond to a realizable relabeled experiment or to a corrected oracle gap. Its intervals condition on the questions of the selected categories, the observed conversations, and the memory stores. The gate simulations (Appendix I.3) give conditional pass fractions under the specified table models, not the probability that a fresh validation packet will pass or that an unknown κ exceeds the threshold. The zero-event hidden-disagreement calculations (F.3) condition on the sampling model of the decided pairs and plug in an estimated disagreement component, so their totals are not joint upper confidence bounds.

The second follow-up recomputed the observed detectability AUROCs (macro within-pool) of Table A1 from the saved outputs, together with the arithmetic of each setting’s 50 saved label-permutation null values. Each observed score exceeds all its saved null values (null means .498–.505), which gives the exploratory add-one p-value 1/51 = .0196 in every setting. At that resolution no setting can clear a nine-comparison Holm family at .05, so Holm rejects 0 of 9; this is a resolution limit, not evidence for the null.

A later post hoc run refitted each detector 1,000 more times with the same code, arrays, folds, mask, and settings, but with new seeds; the observed AUROCs match the earlier ones exactly. With $p = (1 + e)/1{,}001$, where $e$ is the number of exceedances, Holm over the nine settings at .05 rejects all nine. Eight settings have no exceedance among the 1,000 sampled nulls, which gives the minimum reported plus-one p of 1/1,001 = .000999. These draws do not resolve a smaller p, and this minimum is not a confidence bound on the underlying exceedance probability. Margins over the largest null are thin in PersonaMem-v2 (8 pools, +.0028) and BEAM 100K (20 pools, +.0084), the two settings with the widest null SDs (.028 and .032); more draws could lift their p above the floor. In LoCoMo (observed AUROC .518), 10 of 1,000 nulls reach the observed value, so p = .011. LoCoMo passes only as the last Holm step, at the full .05 threshold, and would not pass a Bonferroni cut (.0056). Pooling all 1,050 draws gives the same 9 of 9. The nine settings and the classifier were chosen after the data were seen. Holm controls error only within this family, not for how the family was chosen, and a small p shows neither that the classifier measures benchmark quality nor why the labels are detectable.

A separate computational check recomputed every reported number from the saved null values, without refitting. In STALE, the permuted statistic is scored on 273–310 pools in the 50-refit run and on 257–324 in the 1,000-refit run, rather than on the 400 observed pools, because the labels are permuted before the fixed row mask is applied and pools with a single class are omitted. Smaller mismatches occur in LoCoMo-Plus (null 399–401 pools, observed 393) and LongMemEval-S (360–414, observed 379). We report this mismatch; by itself, it does not show that applying the same statistic to the permutations is arithmetically invalid. Null means near .5 under this null model do not show that the pipeline is unbiased.

The STALE feature-tier refits remain fitted-model diagnostics as reported. They remove the typography features, then the punctuation and markup counts, and still reach a detectability AUROC near .999, but the saved follow-up outputs keep only their scalar AUROCs, not new out-of-fold predictions, so these refits were not recomputed. Removing the named typography and punctuation columns also leaves length and lexical quantities that can depend on punctuation. Likewise, the token-survival check concerns literal U+2019 in the checked token paths. Literal U+2019 is absent from S16’s normalized per-turn retrieval-token path, but the session-joined pointer path was not rebuilt, and no separate check repeated the tokenization. The check does not compare retrieval outcomes and cannot establish that typography has no causal effect on retrieval.

Selection among eight priors raises a different issue from a single prespecified prior. The checked combinatorial means, selected observed maxima, and analytic upper expressions assume independent item-level random-gold draws, so they do not preserve the dependence from shared haystacks or shared gold. The simulated two-position mean and quantile are Monte Carlo estimates, not guaranteed exact bounds, and no complete joint simulation of the eight priors is available. The power illustration is also conditional. With the rounded store-variance SD of 1.04 points, one independent run per system gives approximate detectable differences of 2.88268 points at 50% power and 4.12052 points at 80% power (about 2.9 and 4.1). At the SD’s upper interval bound, 1.39, the difference at 80% power is about 5.5 points. This illustration applies to single-run differences and assumes a known SD and independent, equal-variance normal errors on the fixed population. Pairing changes the variance through covariance, and no general rule about all small leaderboard gaps follows.

A separate cross-arm identity scan of S10c found 11 identical answer pairs across the core arms: nine for GLM-5.3-Flash and one each for Gemini 3.8 Flash and Gemini 3.5 Flash-Lite. The hybrid-5 and dense-5 pointers give identical reader prompts on 17 probes per reader, but no whole judge input is identical across the compared arms, so the scan cannot estimate the judge’s stability on identical inputs. Each reader has 10,800 available answer pairs, of which 10,783 have different reader prompts; the original GLM-5.3-Flash denominator of 10,775 mixed the masks for reader probes and judge calls. In S17, selecting the first or the last valid record picks the same physical record in all 900 judge calls. Equal input hashes do not certify semantic equivalence. The next paragraph explains the nine GLM-5.3-Flash pairs.

**Proxy copies of identical requests (post hoc, descriptive).** A later check of the call log found that the shared proxy serving GLM-5.3-Flash returned a copy when an identical request body was sent again shortly after the first call had finished. Of 4,650 such repeats sent within a minute, 4,530 (97.4%) came back in under 500 ms with the earlier token counts. Repeats sent while the first call was still running were regenerated, apart from 4.4%. These exceptions followed an earlier finished identical call or overlapped their source by a median of 0.09 s, within the noise of the estimated send time. Gemini and OpenAI calls went directly to their providers and showed no copy pattern. Copies are inferred from latency and token equality, because the log holds no response text; only the S10c cases were also checked against answer hashes. The findings by study follow.

- *S11 replicas.* Each replica sent its own distinct requests: an output-token cap that was never reached differed between replicas, so no two replicas shared a request. Copies touched only the second copies of 11 twin-question pairs (identical questions within one conversation) and a few design probes. Dropping every cell that touches a copy moves label disagreement from 16.25% to 16.32% (29,979 of 30,195 cells kept). It moves the flip rate on byte-identical answer pairs from 59 of 5,429 (1.087%) to 59 of 5,353 (1.102%). No flip pair was an identical request, and S11c had no copies.
- *S10c cross-arm duplicates.* All nine identical GLM-5.3-Flash answer pairs above were proxy copies: the dense-5 request repeated the hybrid-5 request and received its answer. On the eight other probes with identical requests, the request was regenerated and the answer differed every time. The nine identical pairs therefore reflect copying, not determinism at temperature 0. On those nine probes, the descriptive GLM-5.3-Flash dense-5 cell of the Appendix B.2 accuracy table repeats the hybrid-5 answer; the registered contrasts, which concern the Gemini readers, are not involved.
- *S1 redraws.* The GLM-5.3-Flash reader’s redraws, which the S1 design and report describe as independent, were partly copies: among 1,676 complete best-of-three test cells, 29.8% had one real generation and 23.4% had two. The second judge draw copied an earlier draw in 13.8% (Gemini 3.5 Flash-Lite reader) and 6.6% (GLM-5.3-Flash reader) of test rows. The Gemini 3.5 Flash-Lite redraws were regenerated. S1’s registered verdict is unchanged.
- *S15 recoveries.* In S15’s paraphrase build, at the log snapshot used for this check (taken while S15 was still running), 1,230 planned calls had an empty first answer. Their 2,460 identical recovery calls were copies in 2,459 cases, so no call was recovered by an identical retry.

### H.2. Exposure, deviations, and the scope of recomputations

Input and outcome exposure are distinct from inferential decisions. Later reader comparisons on the reused STALE test split are conditional robustness checks, and the replica follow-ups keep their failed judge gates. S15a-A1 is POSITIVE but confounded by harder negatives, S15a-A2 and S15a-A3 are exploratory, and S15a’s content check was not performed. S15b stopped before any end-to-end call, and both S15c primary tests are final INVALID under its completeness gate (S15c-K1). The human regrade consists of the author’s labels, from one informed grader, not a blind panel or ground truth.

Recomputations from the saved outputs checked the registered numerical reductions of the studies within documented limits on sources and masks (Appendix I.4). The S15 and S15c results were each recomputed twice, and the S19 and S19b secondary outputs had one further recomputation. None of these checks validates the meaning of raw answers or amounts to a replication by another laboratory. Detailed private manifests and administrative correspondence are omitted.

### H.3. Licenses and toolkit interfaces

Public license declarations do not settle every upstream right. The recorded licenses are: MemOps, MIT; STALE, CC BY 4.0 (recorded in the study configuration, not verified); LoCoMo, CC BY-NC 4.0 (noncommercial research statistics only); HaluMem-Medium, CC BY-NC-ND 4.0 (statistics only); BEAM, CC BY-SA 4.0; LongMemEval, MIT for its repository; and LoCoMo-Plus, no license found (local exploratory statistics only). PersonaMem-v2’s dataset card declares CC BY 4.0 and identifies descriptions from PersonaHub (Ge et al. 2024) as a source. PersonaHub declares CC BY-NC-SA 4.0, with additional stated conditions on research use and on the generating models. The compatibility and precise scope of that upstream relationship remain unresolved here. The checked ForgetEval and MemoryAgentBench repositories declare MIT, but we do not certify the terms of the exact revisions used or the rights inherited from external material. LongMemEval’s ShareGPT attribution points to FastChat code, whose repository states explicitly that the dataset is not released there, so FastChat’s code license does not establish the license of the filler data. UltraChat (Ding et al. 2023) declares MIT for its data, alongside language on intended research and educational use. The archive redistributes no benchmark text or model responses. These are source disclosures, not legal clearance.

The released toolkit, `memaudit` 0.1.0, runs offline on CPU and provides four groups of commands. The commands `audit run`, `audit marker`, and `audit report` run the question-blind unit audit on pinned local benchmark files, count a specified construction marker, and replay saved prediction archives. The command `qi run` measures wrong-question retrieval against the fair-null baselines (uniform chance, turn-weighted chance, and matched-placebo gold) and reports the CE with S16’s interval rule, the query-blind feature scan, and the eight single-feature priors; it ranks with BM25 by default and offers the S16 hybrid retriever as an option. The command `baselines nulls` scores the null-memory policies (store nothing, wipe plus replacement, keep all, and an oracle target) under ForgetEval’s own scorer, from a pinned local checkout that the user supplies. The command `replica replay` computes the replica estimators from pinned numeric outcomes, and `replica rehearse` exercises the same path on invented data with a fake client. Users obtain the public datasets themselves. The package ships no benchmark text, prompts, or model outputs; it downloads nothing, runs no language model, and makes no provider calls, so it reproduces no reader, judge, or end-to-end result.

The toolkit’s documentation records two reproductions from a local verification run of a development candidate on 4 October 2026. The audit command matched the paper’s recomputed STALE and LoCoMo-Plus detectability AUROCs (Figure 1) to four decimals, and `qi run` matched the stored S16 aggregates of the LoCoMo-Plus atlas row exactly, with BM25 and with the hybrid option. These historical checks are distinct from verification of the released artifact. The toolkit does not reproduce the confirmatory BEAM and HaluMem-Medium rows, because it packages no item converter for them. Nor does it reproduce the other atlas controls (cross-benchmark and different-type peers, constant queries, and the random-score null) or the full study pipelines. It is an open-source implementation of the audit’s checks, not a reproduction package.

Before the release on 12 October 2026, the source and installed-wheel test suites each passed 145 tests, with one optional real-model smoke test skipped, and GitHub Actions on macOS and Ubuntu with Python 3.12 passed for the release code. Version 0.1.0 of `memaudit` was released under Apache-2.0 for code and documentation on 12 October 2026 (<https://github.com/ozgurugurlu/memaudit>). Apache-2.0 does not relicense the input datasets or authorize their redistribution. These release boundaries complement the release statement that follows the main text’s conclusion.

<a id="appendix-i"></a>

## I. Study map, protocols, gates, and recomputations

This appendix holds the protocol, amendment, exposure, gate, and recomputation details behind §3.1, §3.5, and §7.3 of the main text. The main text’s Table 2 gives each study’s population and status; Table I1 says where each study is reported.

### I.1. Study map

**Table I1. Study map: where each study is reported.** Appendix K gives the implementation details that several studies share: data and samples, the classifier, retrieval, prompts, models and settings, and the replica pipeline.

| Study | What it tests | Main text | Appendix |
|----|----|----|----|
| S10 | Question-blind evidence detectability; an initial STALE reader ladder (failed its judge gate) and its user-only rendering | §3.2, §3.4, §4.1 | A, H.1 |
| S10b | Original STALE reader ladder | §3.4, §5.1 | B.1, J.3 |
| S10c | More readers on the original ladder’s reused test split | §3.4, §5.1 | B.2 |
| S15a | Final counterfactual retrieval tests: the STALE source-swap test (S15a-A1) POSITIVE; the STALE style-rewrite and LongMemEval-S source-swap tests (S15a-A2, S15a-A3) EXPLORATORY; the style content check UNPERFORMED | §3.3, §5.2, §6.1 | D.1–D.3 |
| S15b, S15c | S15b stopped at its budget-forecast rule (S15-K5) before any planned end-to-end call. In the separately registered S15c, both end-to-end tests (S15c-B1 and S15c-B2) are final INVALID under the completeness rule (S15c-K1), and a required auxiliary judge-agreement check is incomplete (its test part UNPERFORMED) | §6.3 | D.4–D.6, H.2 |
| S16 | Atlas wrong-question retrieval with fair-null baselines | §3.3, §4.2 | E |
| S18 | Joint de-cue of STALE typography and clock time | §6.2 | B.3 |
| S20 | The same joint de-cue for a RAG pipeline (S20-B1, EQUIVALENT) and a mem0 2.2.1 pipeline (S20-B2, INCONCLUSIVE) in the official STALE layout | §6.4 | L |
| S11 | Replicas of one bespoke memory pipeline | §3.5, §7.1 | C.1, J.4 |
| S11b | Replica follow-up with crossed extractor and judge model families (stopped at its development gate) | §7.2 | C.2 |
| S11c | Replica follow-up with two extractor model families (UNRESOLVED) | §7.2 | C.2 |
| S17 | A judge from a second model family: Part A on replica answers; Part B and the pointer-contrast part (S17-B2) on reader answers | §5.1, §7.2 | C.3, C.4 |
| LLM regrade | Three LLM adjudicators on original-ladder and replica labels | §7.3 | F |
| Human regrade | One design-aware human grader (the author) on the same packet: S10b judge agreement and leniency; S11 judge agreement, flip validity, and the human-graded gain $G_{\mathrm{h}}$ | §5.1, §7.1, §7.3, §9 | J |
| S1, S14 | Null-memory policies (the null-policy study, S1); forgetting closure (S14, failed) | §7.4 | G |
| S19 | Four readers from four vendors and budget-matched two-session pointers (three readers classified; Gemini 3.8 Flash stopped and rerun in S19b; GLM-5.3-Flash secondary-judge results descriptive) | §3.4, §5.1, §9 | B.4 |
| S19b | Separately registered successor of S19 with Gemini 3.8 Flash only, at its “high” setting, on a runtime changed only to allow the documented maximum output length, and with its own judge gate (passed). It completes S19’s test families with S19’s recorded entries; its GLM-5.3-Flash secondary-judge results and the S10c-versus-S19b comparison are descriptive | §3.1, §3.4, §5.1, §9 | B.5 |
| Post hoc rounds 1–3 | Descriptive follow-ups on saved outputs | §3.5, §4.1, §4.2, §5.1, §7.1, §7.3, §9 | H.1, I.3 |

### I.2. Protocol, amendments, and exposure

Each study had a reviewed preregistration, a hash lock over its registration and analysis code, development gates, and a test stage if the gates passed. The S10b judge was chosen after development validation was known. S10c and S11c changed analysis code after the lock under recorded amendments. S11c’s amendment was installed while its test was running, and its development gate reused development data with known outcomes. Some regrade comparison code was written after its lock. S16 disclosed question-blind aggregates seen before its freeze, so its MemOps-session row is descriptive only. S17 was registered after S11c’s failed gate, with S10c’s results known; we treat it as a post hoc sensitivity analysis on reused answers. S18 was registered with the S10b, S10c, and S17 results known. Two substitute reviews replaced its planned pre-freeze review, and a reporting-only amendment fixed its claim wording before any outcome was opened.

S19 was registered with aggregate S10b, S10c, S17, and S18 results known, so its two-session direction was predictable and its five-session direction known. A fallback review replaced its planned pre-freeze review, and a further recheck came only after the freeze. Six amendments followed the freeze: five reporting-only amendments, and one that admitted the successor study’s new runtime module without changing the runtime that S19 used. As registered, S19’s gate was scored after all reads, when the pre-gate analysis already existed. S19b was registered after S19’s partial Gemini 3.8 Flash estimates had been seen, so its direction was predictable. Two reviews preceded its freeze, but its planned review of the build came after the freeze instead of before it (a recorded order deviation). Three reporting-only amendments followed the freeze, and S19b’s gate was likewise scored after all reads, when the pre-gate analysis already existed.

The human regrade ran its frozen plan v1 and locked analysis unchanged. No amendment registers the reinstated human route, and the author, who knows the design, graded after the LLM regrade aggregates existed (J.6, J.8). Exposure logs record which files were opened and when. A lock fixes the content of the locked files, not when inputs or outcomes were first seen. Appendix H.2 summarizes exposure, deviations, and the scope of the computational checks.

<a id="appendix-i3"></a>

### I.3. Judge-validation gates

The S10c, S11b, S11c, S17, S19, and S19b follow-up gates summarized here require agreement of at least .80 and Cohen’s κ of at least .70 against an LLM adjudicator on a registered packet. S11b, S11c, and S17 Part A (which reuses S11c’s rule) use design-weighted agreement and κ, weighted by the packet’s sampling weights. S10c’s gate, which S17 Part B and the S17-B2 validity condition reuse, is unweighted, as are the gates of S19 and S19b (Appendices B.4.3 and B.5.3). Each gate also needs at least 60 labeled or determinate items. A failed gate makes the dependent cells UNRESOLVED (in S19 and S19b, “judge-limited”), whatever their statistics say.

The binding adjudicator of the S10c, S11b, S11c, and S17 gates was Claude Opus 5.5. These are four study gates, not four independent label sets, because S17 reuses S11c’s packet and S11c’s development gate reuses S11b’s validation. The 72-item gates of S19 and S19b were each labeled by a fresh Claude Opus 5.5 instance (`claude-opus-5-5`) that saw no arm, reader, or outcome; Appendix K.6 gives the adjudicator instructions. S15c validated its judge separately, against two fresh, packet-only Claude Sonnet 5.5 reference raters approved by the author, one for development and one for test (Appendix D.5.2). Both reference gates passed, but S15c failed its primary completeness rule, and that failure is final. S11’s own judge validation covered development answers only (Appendix C.1). S18 inherited S17 Part B’s validation and did not retest its new answers (Appendix B.3). The one-grader human check (Appendix J) is not a gate: it has one design-aware grader and 50 items per study, fewer than the 60-item minimum, and no registered verdict of any study depends on it.

In a post hoc simulation that treats the observed agreement tables as true, a judge like S11c’s passes a gate-sized packet in about 43–49% of draws, and a judge like S10c’s in about 87–97%. These are conditional pass fractions, not pass rates on fresh packets or probabilities that a true κ exceeds .70 (see also Appendix H.1). Near the thresholds, a gate outcome therefore carries limited information about judge quality: a failed gate withholds a verdict, but it does not show that the judge is unreliable.

<a id="appendix-i4"></a>

### I.4. Recomputations from the saved outputs

Two separate recomputations from the saved outputs checked the registered numerical results of S10c, S11c, S16, S17, S18, S19, and S19b, and S18 had a third. Two recomputations checked the arithmetic of the one-grader human regrade (J.8); they add no human grader. S11b’s stop rests on one recomputation of its gate.

S15 and S15c each had two recomputations from the saved outputs before their final reports (Appendix D). The S19 and S19b secondary results had one more. It reproduced every registered target, including the self-preference interval, and kept the partial-reader coverage and the binding decisions unchanged. It did not reopen the protected original files, and it does not establish that the sources or the model identities are authentic.

The post hoc checks were recomputed within their stated scopes. The saved scores of the second round were checked without repeating the model fits, and the 1,000-refit nulls were checked from saved values rather than refitted. These are computational checks, not replication by another laboratory or label validation; failed gates and missing data keep their status.

<a id="appendix-j"></a>

## J. One-grader human regrade of the regrade packet

One human grader, the author, who knows the study design, graded all 100 items of the frozen packet that the LLM adjudicators of Appendix F graded: 50 answers of the original STALE ladder (S10b; claim C2 in the plan) and 50 replica answers (S11; claim C3). These are the labels of one design-aware grader. They are not an independent blind panel, not ground truth, and not human validation in a general sense; the main text calls them a one-grader human check. Every number below is an estimate on this packet, with about 50 items per study. Raw figures are unweighted over the sample. Design-weighted figures are reweighted to each study’s frame, the full answer set from which that part of the packet was drawn. Values marked post hoc were computed after the labels were seen; they change no registered output and no study verdict. No item text appears here. Card J gives the protocol.

### J.1. Protocol card

**Card J. Human regrade protocol card.**

| Element | Human regrade |
|----|----|
| Plan and locks | The sampling plan was written on 3 October 2026, before sampling. The frozen sample, the packet builder, and the answer key were hash-pinned; the analysis code was pinned on 4 October 2026, before any human grade |
| S10b part (C2) | A stratified random sample of 50 of the 2,412 doubly judged STALE probe answers (binding judge GLM-5.3-Flash; secondary judge Gemini 3.5 Flash-Lite; readers GLM-5.3-Flash and Gemini 3.5 Flash-Lite). Ten strata cross four arm groups (plain: the plain and placebo-instruction arms; generic: the generic-instruction arm; pointer: the wrong-partner pointer, hybrid-5, and artifact-pointer arms; oracle: the oracle-note arm) with three judge-agreement classes (AP, both judges pass; AF, both fail; DIS, the judges disagree). Disagreements are oversampled, 20 of 81 against 30 of 2,331 agreements. S10b’s LoCoMo-Plus items are outside the packet |
| S11 part (C3) | 50 of the 6,901 judged replica answers (answers from replicas X1–X10 with a valid answer and binding-judge label) on all 692 questions, 680 of which have all ten. These answers form 30,981 replica pairs: 5,110 judge-discordant and 25,871 judge-concordant. Part P: 15 judge-discordant pairs, one judged-correct and one judged-wrong answer of each of 15 sampled unstable questions. Part R: 10 random pairs, all of which happen to be judge-concordant (5 pass-pass, 5 fail-fail) |
| Estimands | E1 and E4: agreement and κ of each judge with the human grade (C2 and C3). E2: C2 agreement by arm group and stratum. E3: judge-minus-human pass rate by arm group. E5: flip validity of the judge-discordant pairs. E6: human-graded replica discordance $d_{\mathrm{h}}$ and gain $G_{\mathrm{h}} = d_{\mathrm{h}}/2$ |
| Rubrics | The judges’ own rubrics: the official STALE judge rubric (Chao et al. 2026) (rubric A) for C2 and the Mem0-paper LoCoMo criterion (Chhikara et al. 2025) (rubric B), which is deliberately generous, for C3. The grade measures how a human applies these rubrics, not a stricter notion of truth. Appendix K.6 gives the grader instructions |
| Blinding | No arm, reader, model, judge, verdict, stratum, study, scenario, or conversation id is shown, and item codes follow a seeded random order. Residual cues: the rubric reveals the benchmark; answer style reveals the reader; 4 of the 50 STALE answers mention a memory pointer; and the author, who knows the design, knows that 15 of the 25 S11 pairs are judge-discordant by construction |
| Grader and labels | One person, the author, who knows the design, so there is no human-human agreement. All 100 items were graded: 57 correct, 43 incorrect, and 0 ambiguous. There is one free-text note, on a part-R item whose grade agrees with the judge; only the note’s presence was checked, and its text was not examined for this analysis |
| Packet | According to the author’s record, the author graded an LLM-translated Turkish/English rendering of the 100 items, with the English rubrics binding. The translation was prepared and checked without access to grades or outcomes. The export cannot confirm which rendering was used (deviation D1 in J.6) |
| Analysis | The registered analysis code, run on 6 October 2026 at 12:57; its built-in self-test passed. Its three treatments of ambiguous labels (exclude, optimistic, and pessimistic) coincide here because no label is ambiguous |
| Reporting rule | The plan bars the word “validated” when the pessimistic design-weighted agreement is below .80. The values are 99.1%, 97.5%, and 96.9%, but this paper still writes “one-grader human check”: one design-aware grader is not a panel, the post hoc sensitivity values of J.2 leave lower agreement compatible with the data, and 50 items per study are fewer than the 60-item minimum of the paper’s gates (Appendix I.3) |

### J.2. Weights, leverage, and precision

S10b items carry stratum weights $N_s/n_s$, where $s$ indexes the sampling strata, from 2.0 (generic-DIS) to 128.4 (pointer-AP). S11 answers carry $1/\pi$, with $\pi$ the union inclusion probability, from 18.6 (part P) to 346.0 (stable part-R answers); the 20 part-R answers carry 69.0% of the S11 weight. The Kish effective sample size is 27.7 of 50 for S10b and 29.6 of 50 for S11. One pointer-AP item carries 5.3 points of C2’s design-weighted agreement, and one stable part-R item carries 4.9 points of C3’s, so the design-weighted points move in steps of a few points per item (post hoc values, computed from the design weights; none depends on the labels).

**Why both C2 design-weighted figures are high.** The author’s grades matched both judges on all 30 sampled agreement-stratum items, which stand for 2,331 of the 2,412 frame units (96.6%). On a DIS item the judges disagree and no label is ambiguous, so the author agrees with exactly one of them, and the two judges’ design-weighted disagreements sum to the DIS frame share: 0.90 + 2.46 = 3.36 points. Once the agreement strata show no disagreement, each design-weighted agreement is at least 96.6% by construction. The design-weighted figures therefore mainly encode 30 zero-disagreement items, while the raw 92.0% and 68.0% reflect how the 20 oversampled DIS items split. In C3, part R (20 of 20 agree) carries 69.0% of the weight.

**Registered intervals.** Wilson intervals for raw agreement are binomial reference intervals for this disagreement-enriched sample. They ignore the stratification and, in C3, the pairing, and they do not describe the frame. The design-weighted quantities have a stratified bootstrap (2,000 resamples; S10b answers within strata, S11 pairs within parts). Every resample keeps zero disagreements wherever none was observed. In C2, whose weights are equal within strata, the brackets therefore move only with the DIS strata. In C3, part R stays 20 of 20 in agreement in every resample, but resampling its unequal weights still moves the agreement denominator, so that bracket does not reflect part P alone. The brackets omit the uncertainty from errors that the zero-event cells did not show, so they understate the uncertainty and are not confidence intervals. The tables below give them only in their captions, and Table J1 gives post hoc sensitivity values instead. The plan had expected brackets of about ±8–12 points. Appendix F.4 notes the same degeneracy in the LLM regrade and does not quote its brackets.

**Table J1. Post hoc grouped sensitivity of the design-weighted agreement, with the human grade as reference (the convention of Appendix F.4).** Percentages. Each sampling stratum is a group, with a Jeffreys $\mathrm{Beta}(x + 0.5, n - x + 0.5)$ model of its disagreement rate, where $x$ is the number of disagreements among the group’s $n$ items (seed 20261004; 20,000 draws). The Clopper–Pearson (CP) lower value is the design-weighted agreement obtained when each group’s disagreement rate is set to its one-sided CP upper bound, Bonferroni-adjusted over the groups. These are model-specific sensitivity values, not intervals for the registered estimates. Binomial independence within groups and the omitted question dependence are model assumptions, not properties of the sampling design, and so is the grouped weighting in C3; in C2 the groups are the design’s own strata, within which the weights are equal (Table J3). The C3 grouping (part × stability) gives a grouped point that differs from the registered 96.9%. The C3 values equal adjudicator G3’s in Appendix F.4, because both graders have five disagreements in part P and none in part R. The Jeffreys prior gives each zero-disagreement stratum (3–7 items in C2) a posterior mean disagreement of $0.5/(n + 1)$, from 6.25% to 12.5%. The quantiles can therefore lie below the observed grouped point, and in both C2 rows they do (for example, 99.10 against 80.33–96.97). They show sensitivity to that prior, not uncertainty around the point.

| Part and judge (post hoc) | Grouped agreement point | CP lower value (Bonferroni) | Jeffreys 2.5% and 97.5% quantiles |
|----|----|----|----|
| C2, GLM-5.3-Flash | 99.10 | 34.34 | 80.33–96.97 |
| C2, Gemini 3.5 Flash-Lite | 97.54 | 33.67 | 78.76–95.63 |
| C3, GLM-5.3-Flash | 94.83 | 67.65 | 81.91–96.88 |

A four-cell Dirichlet version of the same model, with the Jeffreys prior (seed 20261006), gives κ quantiles of .51–.91 for GLM-5.3-Flash on C2 (median .76) and .48–.88 for Gemini 3.5 Flash-Lite. Adjudicators G1–G3 have no counterpart to these values.

### J.3. C2: the S10b ladder judges (50 answers)

Table J2 gives the agreement of both judges with the human grade, Table J3 breaks it down by sampling stratum, and Table J4 by arm group.

**Table J2. Agreement of the S10b judges with the human grade (registered).** Agreement and pass rates in percent; κ as a fraction. Registered bootstrap brackets, degenerate (J.2): design-weighted agreement \[98.3, 99.7\] and κ \[.95, .99\] for GLM-5.3-Flash; \[96.9, 98.3\] and \[.91, .95\] for Gemini 3.5 Flash-Lite.

| Judge | Raw agreement \[Wilson 95%\] ($n$) | Raw κ | Design-weighted agreement | Design-weighted κ | Design-weighted pass rate, judge / human |
|----|----|---:|---:|---:|----|
| GLM-5.3-Flash (binding) | 92.0 \[81.2, 96.8\] (50) | .83 | 99.1 | .97 | 78.3 / 77.9 |
| Gemini 3.5 Flash-Lite (secondary) | 68.0 \[54.2, 79.2\] (50) | .35 | 97.5 | .93 | 76.9 / 77.9 |

**Table J3. Agreement with the human grade by sampling stratum (registered).** Percentages. Within a stratum the weights are equal; κ is undefined inside an AP or AF stratum, where the judge label is constant. $N_s$ is from the sampling plan. GLM is the GLM-5.3-Flash judge and Flash-Lite the Gemini 3.5 Flash-Lite judge.

| Stratum | $N_s$ (frame) | $n$ | GLM agreement | GLM pass / human pass | Flash-Lite agreement | Flash-Lite pass / human pass |
|----|---:|---:|---:|----|---:|----|
| Plain-AP | 355 | 5 | 100.0 | 100.0 / 100.0 | 100.0 | 100.0 / 100.0 |
| Plain-AF | 273 | 4 | 100.0 | 0.0 / 0.0 | 100.0 | 0.0 / 0.0 |
| Plain-DIS | 50 | 8 | 62.5 | 75.0 / 62.5 | 37.5 | 25.0 / 62.5 |
| Generic-AP | 277 | 4 | 100.0 | 100.0 / 100.0 | 100.0 | 100.0 / 100.0 |
| Generic-AF | 91 | 3 | 100.0 | 0.0 / 0.0 | 100.0 | 0.0 / 0.0 |
| Generic-DIS | 10 | 5 | 100.0 | 40.0 / 40.0 | 0.0 | 60.0 / 40.0 |
| Pointer-AP | 899 | 7 | 100.0 | 100.0 / 100.0 | 100.0 | 100.0 / 100.0 |
| Pointer-AF | 136 | 3 | 100.0 | 0.0 / 0.0 | 100.0 | 0.0 / 0.0 |
| Pointer-DIS | 21 | 7 | 85.7 | 71.4 / 57.1 | 14.3 | 28.6 / 57.1 |
| Oracle-AP | 300 | 4 | 100.0 | 100.0 / 100.0 | 100.0 | 100.0 / 100.0 |

**Table J4. Design-weighted agreement (estimand E2) and leniency (estimand E3) by arm group (registered).** Design-weighted percentages; judge minus human in points. Human pass rates are the same under the ambiguity bounds, because no label is ambiguous. The “All” row’s agreement is Table J2’s. GLM is the GLM-5.3-Flash judge and Flash-Lite the Gemini 3.5 Flash-Lite judge.

| Arm group | GLM agreement | Flash-Lite agreement | GLM pass | Flash-Lite pass | Human pass | GLM − human | Flash-Lite − human |
|----|---:|---:|---:|---:|---:|---:|---:|
| Plain (plain and placebo-instruction arms) | 97.2 | 95.4 | 57.9 | 54.2 | 57.0 | +0.9 | −2.8 |
| Generic (generic-instruction arm) | 100.0 | 97.4 | 74.3 | 74.9 | 74.3 | 0.0 | +0.5 |
| Pointer (wrong-partner pointer, hybrid-5, and artifact-pointer arms) | 99.7 | 98.3 | 86.6 | 85.7 | 86.3 | +0.3 | −0.6 |
| Oracle (oracle-note arm) | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0.0 | 0.0 |
| All | 99.1 | 97.5 | 78.3 | 76.9 | 77.9 | +0.4 | −0.9 |

**Where the judges disagree.** All 30 sampled agreement-stratum items matched the author’s grades, so every disagreement lies in the DIS strata (Table J3). On the 20 sampled disagreements, the author sided with GLM-5.3-Flash 16 times: 5 of 8 in plain-DIS, 5 of 5 in generic-DIS, and 6 of 7 in pointer-DIS. The author backed GLM-5.3-Flash both where it was the lenient judge (it passed and Gemini 3.5 Flash-Lite failed 13 answers, of which the author passed 10) and where it was the strict one (7 answers, of which the author failed 6; post hoc counts). This is consistent with the author’s decision of 4 October 2026 not to rely on Gemini 3.5 Flash-Lite at judge-disagreement points. Because the author both took that decision and graded the packet, the agreement is not an independent confirmation, even though the packet concealed every recorded verdict. Concealment also does not show that the author’s prior preference, or identities inferred from the residual cues, could not affect individual grades. In design-weighted terms, GLM-5.3-Flash passes an answer that the author fails on an estimated 0.64% of the frame and fails one that the author passes on 0.26%; for Gemini 3.5 Flash-Lite, the shares are 0.76% and 1.70%.

**Leniency.** A recomputation from S10b’s saved outputs had found the GLM-5.3-Flash judge 4.0 and 3.3 points more lenient than Gemini 3.5 Flash-Lite on plain and placebo-instruction answers. On this packet, the plain-group gap is +3.7 points (57.9 − 54.2; Table J4). Against the human grade, it splits into +0.9 points for GLM-5.3-Flash and −2.8 for Gemini 3.5 Flash-Lite. For this grader, GLM-5.3-Flash’s extra passes on plain and placebo-instruction answers are therefore mostly correct, and the gap mainly reflects the strictness of Gemini 3.5 Flash-Lite. This interpretation rests on the six sampled plain-DIS answers that GLM-5.3-Flash passed and Gemini 3.5 Flash-Lite failed, of which the author passed four (Wilson 30–90%; post hoc). The post hoc four-cell model gives judge-minus-human 2.5–97.5% ranges of −14.5 to +18.4 points for GLM-5.3-Flash in the plain group (Gemini 3.5 Flash-Lite: −17.7 to +15.2) and of −4.95 to +23.8 for GLM-5.3-Flash in the pointer group. The packet shows no leniency signal, but it cannot bound arm-group leniency to a few points.

**Table J5. Raw agreement with the human grade by reader (registered).** Percentages. GLM is the GLM-5.3-Flash judge and Flash-Lite the Gemini 3.5 Flash-Lite judge.

| Reader | $n$ | GLM raw agreement | GLM pass / human pass | Flash-Lite raw agreement | Flash-Lite pass / human pass |
|----|---:|---:|----|---:|----|
| GLM-5.3-Flash reader | 38 | 89.5 | 73.7 / 68.4 | 71.1 | 55.3 / 68.4 |
| Gemini 3.5 Flash-Lite reader | 12 | 100.0 | 41.7 / 41.7 | 58.3 | 50.0 / 41.7 |

The binding judge’s four disagreements with the author are all on answers of the GLM-5.3-Flash reader (Table J5; 34 of 38 agree, Wilson \[75.9, 95.8\], κ .745), and in three of them the judge passed an answer that the author failed. The sample holds 15 DIS items from the GLM-5.3-Flash reader and 5 from the Gemini 3.5 Flash-Lite reader (post hoc count), so the pattern fits a mild leniency of the GLM-5.3-Flash judge toward answers from its own model but cannot show it. By arm (raw), the binding judge agrees with the author on 5 of 5 artifact-pointer and 9 of 9 hybrid-5 answers, the two arms of S10b’s headline contrast. Its four disagreements are on one plain, two placebo-instruction (one in each direction), and one wrong-partner-pointer answer. With five and nine items and no disagreement, the one-sided 95% Clopper–Pearson upper bounds on the raw per-arm disagreement rates are about 45% and 28% (post hoc, treating each arm’s sampled answers as a simple random sample). A judge-error difference as large as the +12.0-point contrast is therefore not excluded, and the packet does not test that component.

**What this means for the S10b ladder.** On this packet, the author, applying the official rubric, agrees with the binding judge on 46 of 50 answers, an estimated 99.1% of the frame, and the judge’s design-weighted pass rate is within a point of the human pass rate in every arm group. This is the paper’s first non-LLM evidence on how the binding judge applies the STALE rubric. It does not bound a judge-error difference between the arms of the +12.0-point contrast, says nothing about the judges of S10c, S17, S19, or S19b, and leaves S10b’s exposure and confounds unchanged (Appendix B.1).

### J.4. C3: the S11 replica judge, flip validity, and the human-graded gain (50 answers)

Table J6 gives the replica judge’s agreement with the human grade, and Table J7 breaks it down. Table J8 classifies the 15 sampled judge-discordant pairs, and Table J9 gives the human-graded discordance and gain.

**Table J6. Agreement of the S11 replica judge with the human grade (registered).** Agreement and pass rates in percent; κ as a fraction. Registered bootstrap brackets, degenerate (J.2): design-weighted agreement \[94.0, 99.2\] and κ \[.86, .98\].

| Judge | Raw agreement \[Wilson 95%\] ($n$) | Raw κ | Design-weighted agreement | Design-weighted κ | Design-weighted pass rate, judge / human |
|----|----|---:|---:|---:|----|
| GLM-5.3-Flash | 90.0 \[78.6, 95.7\] (50) | .80 | 96.9 | .93 | 65.4 / 65.6 |

**Table J7. Raw agreement with the human grade by part, stability, and question type (registered).** Percentages.

| Subset | $n$ | Raw agreement | Raw judge pass / human pass |
|----|---:|---:|----|
| Part P (15 judge-discordant pairs) | 30 | 83.3 | 50.0 / 53.3 |
| Part R (10 random pairs) | 20 | 100.0 | 50.0 / 50.0 |
| Stable questions | 12 | 100.0 | 83.3 / 83.3 |
| Unstable questions | 38 | 86.8 | 39.5 / 42.1 |
| Multi-hop | 4 | 50.0 | 50.0 / 100.0 |
| Open-domain | 2 | 100.0 | 0.0 / 0.0 |
| Single-hop | 28 | 92.9 | 57.1 / 57.1 |
| Temporal | 16 | 93.8 | 43.8 / 37.5 |

All five disagreements lie in part P (Table J7). In two, the judge passed an answer that the author failed, and in three it failed one that the author passed; in design-weighted terms, the two directions cover an estimated 1.40% and 1.66% of the frame. The packet’s design-weighted judge pass rate (65.4%) is 5.5 points below the frame’s known judge pass rate (70.9%). This is realized sampling error, probably mostly from the 10 random pairs that carry 69% of the weight (not decomposed). The human pass rate of 65.6% should therefore be compared with 65.4%, not taken as the frame’s share of correct answers.

**Table J8. Flip validity (estimand E5): the 15 sampled judge-discordant pairs.** Registered, except the two post hoc pair-weighted shares. Shares are in percent and describe the judge-discordant domain only.

| Category | Pairs | Raw share | Pair-weighted share |
|----|---:|---:|----|
| Real (human: judged-correct side correct, judged-wrong side incorrect) | 10 | 66.7 | 68.6 (bootstrap \[42.6, 91.2\]) |
| Judge-lenient (both answers incorrect) | 2 | 13.3 | 14.1 (post hoc) |
| Judge-strict (both answers correct) | 3 | 20.0 | 17.3 (post hoc) |
| Reversed / ambiguous | 0 / 0 | 0 | 0 |

As a point estimate, about two-thirds of the judge’s flips on unstable questions are real for this grader (Table J8). The interval does not exclude a minority, and the judge errs in both directions.

**Table J9. Human-graded replica discordance and gain (estimand E6), against the judge on the same frame (registered).** The frame is every judged replica answer of all 692 questions. It is wider than the 671 complete-case questions on which $G_{\mathrm{mean}}$ is 8.12 points (Appendix C.1).

| Quantity | Value |
|----|----|
| Frame | 692 questions (680 with all ten replica labels); 6,901 judged answers; 30,981 replica pairs, 5,110 of them judge-discordant |
| Judge discordance $d$ / the judge’s $G_{\mathrm{mean}}$ on this frame | 16.49% / 8.25 points |
| Human-graded discordance $d_{\mathrm{h}}$ | 11.3% |
| Human-graded gain $G_{\mathrm{h}}$ \[registered bootstrap\] | 5.65 points \[3.51, 7.52\] |
| $G_{\mathrm{h}}$ from real flips / from discordance hidden in judge-concordant pairs | 5.65 / 0.00 points |
| Human-discordant share in judge-discordant / judge-concordant pairs | 68.6% / 0.0% |
| Part-R pairs: judge-discordant / human-discordant (of 10) | 0 / 0 |

**What the interval covers.** The bootstrap resamples part-P and part-R pairs. All 10 part-R pairs show zero human discordance, so the interval covers only the variability of the part-P share, and the hidden term, the discordance hidden in judge-concordant pairs, cannot move. Unlike the C3 agreement bracket of J.2, this interval does not move with the resampled part-R weights, because the estimator of estimand E6 calibrates each domain to its fixed size. The interval therefore lies below 8.25 only because the hidden term is fixed at zero; it does not show that $G_{\mathrm{h}}$ is below the judge’s $G_{\mathrm{mean}}$ (Table J9). The stored value is the registered number. It is the locked code’s calibrated (Hájek-type) estimate, which rescales the sampled part-P pair weights to the known 5,110 judge-discordant pairs. The plan’s prose specifies a literal Horvitz–Thompson (HT) total instead, which uses the raw weights. Those weights sum to 5,546.8, so the HT total on the same labels is 6.14 points (post hoc; 6.14 ≈ 5.65 × 5,546.8/5,110). Reproducing the stored value therefore does not establish adherence to the plan’s estimator. Adjudicators G1–G3 face the same estimator conflict (Appendix F.3), and both values are kept.

**Hidden-term sensitivity (post hoc).** Each part-R pair graded as discordant would add 4.18 points to $G_{\mathrm{h}}$. A hidden share of 6.2% would make $G_{\mathrm{h}}$ equal to the judge’s 8.25, and at that share, no discordant pair among 10 has probability .53. Replacing the zero by its one-sided 95% Clopper–Pearson bound (.259) gives a $G_{\mathrm{h}}$ of 16.46 points, the human counterpart of the 16.9–18.5 points of adjudicators G1–G3 (Appendix F.3). This figure adds an upper sensitivity value for the hidden term to the estimated observed component, so it is a conditional sensitivity, not a joint confidence bound. The packet is therefore compatible with a human-graded gain from about the real-flip component to well above 8.25 points, and it cannot show whether the judge overstates or understates the replica gap.

**What this means for the replica result.** For this grader, the judge’s replica flips are mostly real differences in correctness, as a point estimate (10 of 15; 68.6% pair-weighted, bootstrap \[42.6, 91.2\]). The real flips alone give a human-graded discordance of about 11% and a $G_{\mathrm{h}}$ of 5.65 points \[3.51, 7.52\] on this frame. On this packet, therefore, the label disagreement of our bespoke GLM-5.3-Flash pipeline (modeled on Mem0, not its code) on four LoCoMo conversations is not explained away as judge noise. Grader inconsistency cannot be measured with one grader: a single grading pass cannot separate real answer differences from within-grader error, and, depending on the error process, such error could add or remove observed discordance. $G_{\mathrm{h}}$ is not a corrected $G_{\mathrm{mean}}$: it does not re-estimate the main analysis’s 8.12 points \[7.18, 9.07\] or that estimate’s intervals (Appendix C.1). It touches neither S11c’s UNRESOLVED gate nor S17 Part A (Appendices C.2 and C.3). Rubric B is generous by design, and a stricter interpretation of the rubric, which the plan left out, could move the flip classification.

**Sharma and Lall.** The packet contains none of the systems, answers, or judges of Sharma and Lall (2026). It estimates no share of their improvement and has no bearing on whether their gap is real; nothing here calls their gap noise. Our recomputed 8.9-point gain from their released labels remains a reference scale only (§3.5), and no ratio of $G_{\mathrm{h}}$ to it is formed.

### J.5. The human grades against the LLM adjudicators

All 100 items overlap with Appendix F: adjudicators G1 (Claude Sonnet 5.5), G2 (Gemini 3.8 Flash, thinking level “high”), and G3 (GPT-6.1 Sol, “medium” reasoning) graded the same packet with the same rubrics before the author did. Table J10 compares the registered estimands, and Table J11 sets the human grades against each adjudicator. Neither the human row nor the LLM rows are ground truth.

**Table J10. Registered estimands: the human grades against the LLM adjudicators.** Human values are registered, except the literal HT total (post hoc); LLM values are those of Appendix F.1–F.3. Percentages unless points are stated. G1–G3 are the LLM adjudicators; GLM is the GLM-5.3-Flash judge and Flash-Lite the Gemini 3.5 Flash-Lite judge.

| Estimand | Human | G1 | G2 | G3 |
|----|----|----|----|----|
| C2, GLM design-weighted agreement | 99.1 | 99.6 | 99.3 | 93.9 |
| C2, Flash-Lite design-weighted agreement | 97.5 | 97.1 | 97.4 | 92.1 |
| C2, GLM raw agreement ($n$) | 92.0 (50) | 95.6 (45) | 93.5 (46) | 88.0 (50) |
| C2, pointer-group design-weighted pass rate (GLM judge: 86.6) | 86.3 | 86.1 | 86.3 | 74.1 |
| C3, GLM design-weighted agreement | 96.9 | 98.0 | 98.1 | 96.5 |
| C3, GLM raw agreement ($n$) | 90.0 (50) | 93.2 (44) | 93.9 (49) | 90.0 (50) |
| Estimand E5, real share, pair-weighted (decided pairs) | 68.6 (10 of 15) | 80.9 (8 of 10) | 87.6 (12 of 14) | 73.9 (10 of 15) |
| Estimand E6, stored $G_{\mathrm{h}}$ / literal HT total (points) | 5.65 / 6.14 | 6.67 / 5.35 | 7.23 / 7.18 | 6.09 / 6.61 |
| Part-R pairs: discordant / decided | 0 / 10 | 0 / 9 | 0 / 10 | 0 / 10 |
| Ambiguous labels | 0 | 11 | 5 | 0 |

**Table J11. The human grades against each adjudicator (post hoc).** Computed on the items that both graders labeled determinately, with the registered analysis code’s estimators and the adjudicator in the judge’s role. Agreement counts and design-weighted agreement in percent; κ as a fraction. GLM is the GLM-5.3-Flash judge.

| Human against | G1 | G2 | G3 | For reference: GLM judge |
|----|----|----|----|----|
| C2 raw: agree / $n$, κ | 42 / 45, .85 | 43 / 46, .86 | 44 / 50, .75 | 46 / 50, .83 |
| C3 raw: agree / $n$, κ | 43 / 44, .95 | 47 / 49, .92 | 46 / 50, .84 | 45 / 50, .80 |
| Pooled raw: agree / $n$, κ | 85 / 89, .90 | 90 / 95, .89 | 90 / 100, .79 | 91 / 100, .82 (post hoc) |
| C2 / C3 design-weighted agreement | 99.3 / 99.5 | 99.5 / 98.8 | 94.0 / 96.8 | 99.1 / 96.9 |

**Item-level overlap (post hoc counts).** On the 78 items where all three adjudicators gave the same determinate grade, the author agreed on 76. Both exceptions are STALE items. In one, the author departs from the judge, whose grade all three adjudicators share. In the other, a pointer-DIS hybrid-5 answer, the author sides with the judge against all three adjudicators. On the nine items where the author departs from the GLM-5.3-Flash judge (four in C2, five in C3), the adjudicators sided with the author on four, unanimously or by a majority of decided votes, and with the judge on three; two were split. Neither the author nor the adjudicators are ground truth, so these are departures, not corrections. Adjudicator G3’s sparse pointer signal (Appendix F.2) came from two hybrid-5 items, and on both the author sided with the judge. Of G3’s 11 disagreements with the judge, the author sided with G3 on five. The author and the adjudicators gave the same flip category on 10 of 10 jointly decided pairs (G1), 12 of 14 (G2), and 12 of 15 (G3). The author’s two judge-lenient pairs are the main reason that the human share for estimand E5 is the lowest of the four graders.

**What the human labels add, and what they cannot.** They are the first non-LLM reference on this packet. They agree with adjudicators G1 and G2 that judge agreement is high on both claims, do not support G3’s pointer signal, and move estimand E5 down: as a point estimate, “most judge flips are real” survives at about two-thirds (68.6%) rather than 74–88%, and its interval does not exclude a minority. They cannot add independence, because every grader shares the rubric text. They cannot add precision, because the strata are as sparse, and the random pairs as few, as in the LLM regrade. Nor can they cover answers outside the packet or settle the direction of the S11 judge’s error in the population.

### J.6. Deviations from the plan

- **Deviation D1. Turkish/English packet.** According to the author’s record, the author graded an LLM-translated Turkish/English rendering of the same 100 items, with the same codes and order. The question, the reference or context, the rubric for the item’s probe type, and the system answer appear in Turkish beside the English original; the verbatim English rubrics are kept and marked binding; and the exported file format and the browser storage key are unchanged. The translation was prepared and checked without access to grades or outcomes. The author approved the rendering on 5 October 2026; the approval covered model use for preparing the packet only and did not permit model assistance while grading. Numeral checks passed on all 300 translated fields, and literal checks found zero mismatches. A full semantic review of 24 items, chosen from the English before any translation was seen, found no material mismatch; the other 76 items had no full semantic review, and two source-language phrases remain flagged. Post hoc, 2 of the 9 human-judge disagreements lie in the 24 reviewed items and 7 outside them (agreement 22 of 24 inside and 69 of 76 outside), and the one named flagged item is not a disagreement. These descriptive counts neither estimate nor rule out a translation effect on the grades: every item was shown bilingually, so there is no English-only counterfactual, and full semantic review supports fidelity only for the 24 reviewed items. Both renderings write the same file name, columns, and storage key, so the export cannot confirm which one was used, and which language the author relied on while grading is not recorded. The plan describes an English packet; the translation is a layer that the plan did not foresee, and its meaning risk is a limit of this grade.
- **Deviation D2. The human route was reinstated after it had been replaced.** On 4 October 2026, the author decided not to grade by hand, and a registered amendment for LLM adjudication replaced the human route. The author then approved the bilingual rendering (5 October 2026) and graded the packet. No amendment registers the reinstatement; the analysis is plan v1’s, run unchanged, and the human grade came after the LLM regrade aggregates existed (J.8).
- **Deviation D3. Open decisions not taken.** Before grading, four options were left open: a “strict” box on the C3 items, more agreement-stratum items (a plan v2), S10b’s LoCoMo-Plus items, and a second grader. None was taken. These are not breaches, but they bound what the grade shows: no split between strict and lenient grading, sparse strata, no LoCoMo-Plus items, and no human-human baseline.
- **Deviation D4. Interval behavior.** The registered intervals ran as planned, but every resample keeps zero disagreements in the zero-event cells (in C3, the resampled part-R weights still move the denominator), so the intervals understate the uncertainty (J.2), which the plan’s precision paragraph did not foresee. The post hoc sensitivity values are not registered and are not confidence intervals.
- **Deviation D5. The estimator of estimand E6.** The stored calibrated estimate (5.65 points) differs from the Horvitz–Thompson total that the plan’s prose specifies (6.14 points; J.4). Adjudicators G1–G3 face the same conflict (Appendix F.3). The stored value is kept as the registered number.
- **Deviation D6. Label use.** The grading instructions asked for a note on every ambiguous item and on any item of hesitation. The author used no ambiguous label and wrote one note, so the plan’s ambiguity bounds are moot. Whether zero ambiguity reflects confidence or forced choices is not known.
- **Deviations D7 and D8. File location and self-test.** The author saved the export in the packet folder, and a byte-identical copy at the documented location was analyzed. The analysis code’s self-test passed, and a later rerun of the self-test in a copy of the study folder also passed and reproduced the real analysis byte for byte (J.8).
- **Unchanged.** The sample, the item codes and their order, the frozen list, the plan, the builder, the analysis code, and the key; no item was dropped, and none was left ungraded.

### J.7. What the human regrade cannot show

- Human-human reliability, and any reliability of this grader beyond the 100 items.
- The design-based precision of any design-weighted figure (J.2).
- Judge validity on other answer sets: S10c, S11c, S17, S19, S19b, and S10b’s LoCoMo-Plus items are not sampled, and every registered gate in this paper remains LLM adjudication (Appendix I.3).
- The judge-error component of any contrast between arms (J.3).
- The size of the discordance that the S11 judge hides inside its concordant pairs, beyond “none in 10” (J.4).
- A corrected S11 gap, or anything about another pipeline, including Sharma and Lall’s.

### J.8. Exposure and computational checks

The author saw the bilingual text and knew the study design. Grading took place between the delivery of the bilingual packet on 5 October 2026 and the export on 6 October 2026, with no detailed grading log. Within the packet, the author was blind to arm, reader, judge, verdict, stratum, and study labels, apart from the residual cues in J.1. The LLM regrade aggregates already appeared in manuscript drafts from 4 October 2026, before grading. Whether the author had seen them is not recorded, so prior exposure must be assumed; no item-level LLM label was ever in the packet. Compliance with the instruction to avoid models and private study reports while grading was not recorded. The translation was prepared and checked without access to grades or outcomes. No registered study decision depends on these human labels.

Two separate recomputations from the saved outputs checked the human regrade. The first reproduced the registered outputs byte for byte and every post hoc value. The second reproduced 1,211 floating-point and 224 exact fields of the registered estimands (largest difference $1.33 \times 10^{-15}$), all 100 answer and 25 pair inclusion probabilities, and all 27 groups of post hoc outputs. Its calculations were sealed before the target outputs were opened, but they used the analysis source code, so they are source-informed reproductions. A later check supplied the exact stored lower end of the pointer-group leniency range, −4.95 (J.3). These checks establish neither which language the author relied on nor that the author had no assistance; they add no human grader and reopen no failed validation gate.

<a id="appendix-k"></a>

## K. Implementation details: data, retrieval, prompts and models

This appendix gives the implementation details that the study sections only summarize. K.1 identifies the benchmark files and the samples drawn from them, K.2 specifies the question-blind detectability classifier, K.3 gives the retrieval settings, and K.4 defines the registered single-feature priors and the hard-negative count. K.5 reproduces the reader-side texts and their rendering, K.6 gives the instructions for the judges, the adjudicators, and the human grader, K.7 lists the models and their settings, and K.8 specifies the replica pipeline and the mem0 adapter. Every value below is taken from the studies’ locked configurations, input manifests, and code, or from the toolkit’s data cards.

<a id="appendix-k1"></a>

### K.1. Benchmark sources, revisions and samples

Table K1.1 identifies each benchmark by its source and revision, and Table K1.2 gives the SHA-256 digest of every file that the studies read. No download date was recorded for any file. Where a record dates a later comparison with the upstream repository, Table K1.1 gives that date; such a comparison identifies the bytes, not the revision at which they were first obtained.

**Table K1.1. Benchmark sources and revisions.** Revisions are Git commits or Hugging Face dataset revisions. “Not recorded” means that no study record holds the value. FactConsolidation is the single-hop 262k-token split of the MemoryAgentBench conflict-resolution file and is used only in Appendix G.1.

| Benchmark | Source | Revision | Dates on record |
|----|----|----|----|
| STALE | Hugging Face `STALEproj/STALE` | `617c51dc200b5ab09970834144c7e51c77959af0` | Download not recorded |
| LoCoMo | GitHub `snap-research/locomo` | `cbfbc1dba6bc53d00625212a0f22d55ffee7c1fc`, the last commit that changed the file (2024-08-10) | Download not recorded; the file was byte-identical to `main` at `3eb6f2c585f5e1699204e3c3bdf7adc5c28cb376` on 2026-09-30 |
| LoCoMo-Plus | GitHub `xjtuleeyf/Locomo-Plus` | `059f4e3d38f7f1f96765e8e2cb7de3097551bffb` (committed 2026-02-13) | Cloned at the head of `main` on 2026-10-01 |
| LongMemEval-S | Hugging Face `xiaowu0162/longmemeval-cleaned` | `98d7416c24c778c2fee6e6f3006e7a073259d48f` | Download not recorded; this revision was `main` on 2026-09-30 |
| HaluMem-Medium | Hugging Face `IAAR-Shanghai/HaluMem` | Not recorded. The file matches the upstream file at revision `cb04336aa1b732d4b24f5186c552456b4099806e` (last changed in `6c4dbab7af7e773615efff2a62ec249866c0351a`) | Download not recorded; upstream comparison on 2026-10-03 |
| BEAM | Hugging Face `Mohammadta/BEAM` | Not recorded. The three files match the upstream files at revision `3205395e897e7318c7b094ef4e6047b9b82dbb03` (last changed in `8b4ddc477010c07a852752fe2f27a2722755ff2b`) | Download not recorded; upstream comparison on 2026-10-03 |
| PersonaMem-v2 | Hugging Face `bowen-upenn/PersonaMem-v2` | Not recorded. The files match the upstream files at revision `ed956dea41521fc4499acbc63f966e0fd3c053ba` (benchmark file last changed in `76e580fbb41ae32fe59a222c467338ce77cd6f5a`) | Download not recorded; upstream comparison on 2026-10-03 |
| MemOps | GitHub `MemTensor/MemOps` | `312af65e2c7b6d1b70f062ffa8b4cde32aaf6f35` (shallow clone) | Not recorded |
| ForgetEval | GitHub `deeplethe/lethe` | `b6053b7bdacc78a91b9ea4bb25f32edad278c495` | Not recorded |
| FactConsolidation | Hugging Face `ai-hyz/MemoryAgentBench` | `7ea066982b140a19337e17e60d45d4076e042faf` | Download not recorded; this revision was `main` on 2026-09-30 |

**Table K1.2. Files and SHA-256 digests.** Sizes are in bytes. The local BEAM names stand for the upstream files `data/100K-00000-of-00001.parquet`, `data/500K-00000-of-00001.parquet`, and `data/1M-00000-of-00001.parquet`; the PersonaMem-v2 benchmark file is stored locally as `benchmark_text.csv`.

| Benchmark | File (size) | SHA-256 |
|----|----|----|
| STALE | `T1_T2_400_FULL.json` (305,908,212) | `5f3ec375179e20e2e94469e018189188f34e2e7e5f21cbecbd99fcfa648c1876` |
| LoCoMo, and the LoCoMo-Plus hosts | `data/locomo10.json` (2,805,274) | `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4` |
| LoCoMo-Plus cues | `data/locomo_plus.json` (305,737) | `af2fc6e5e0e88735e28d8dd1ef474b718861a73beb21779809e3b9e1a4fe3d23` |
| LongMemEval-S | `longmemeval_s_cleaned.json` (277,383,467) | `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442` |
| HaluMem-Medium | `HaluMem-Medium.jsonl` (33,511,525) | `486fbc130a5c8781a2af27ffa508a1d7855245137aa449c193ac4d29c45634e7` |
| BEAM 100K | `100K.parquet` (5,429,768) | `c0519be25907005ba873c927c50877471d550873039d96c041554d0075a78ace` |
| BEAM 500K | `500K.parquet` (33,956,263) | `af05921c979355038e1761b7cde3d2dd713200dd3071b278de0200f6c7f30122` |
| BEAM 1M | `1M.parquet` (66,156,374) | `41b5acbbb55a586b1305514ef9d9fb03365d9b3331b598a1c2dd7603d93ef533` |
| PersonaMem-v2 | `benchmark/text/benchmark.csv` (42,426,457) | `95f2a8a324aab7baf2af937feae12731369e2abf7cad5ab3e170594cb25a3e52` |
| PersonaMem-v2 | Eight histories of `data/chat_history_32k/` (168,381 to 182,440 each) | Listed per file in the memaudit PersonaMem-v2 data card |
| MemOps | The 403 files of `generated_result/4-inject_evidence_with_distractors` | Recorded per file in the atlas’s input manifest |
| ForgetEval | `bench/forgeteval/generate.py` | `39072bea33402e5cbf66a6c1101504a337ab9f5f3bd90d5402afc7727c4516a8` |
| ForgetEval | `bench/forgeteval/adversarial.py` | `cfdf125aba5b90975634ce48bdf0f078397a72a1cc9dd1aa5bb59ab067c322d3` |
| ForgetEval | `bench/forgeteval/adversarial_generated.py` | `aefa73df027a947a0535cb0c47d66d64010a124cdc1fad2c3985fa59bf5cb5a8` |
| FactConsolidation | `Conflict_Resolution.parquet` (1,491,588) | `24d5c3f09ce0ce15625cb9f8a98f44f0d864ca6c94d7b4ad04eb697ca3a5ff45` |

The ForgetEval cases come from the repository’s own generator (200 template cases per family, seed 42, four distractors, English) and its adversarial case lists, which give 1,000 template and 385 adversarial cases; the null-policy study also pinned the repository’s adapter, test, and adversarial-label files. The evidence audit (S10) read the HaluMem-Medium and PersonaMem-v2 files without checking a digest. Their digests were computed later from the same cached files, and a population-parity check against the audit’s adapters found the same units, labels, pools, and groups. The LoCoMo row of the atlas also uses the wrong-citation list of a public LoCoMo audit (GitHub `dial481/locomo-audit`, file `errors.json`, SHA-256 `f298ef46263fada20688a1d672be37d4f488c6da3b19343eea55ae5c1b5fe55e`; revision not recorded).

**Table K1.3. Sample draws.** Apart from the earlier pilot that S15c excludes, every sample is a hash order: ids are sorted, or thresholded, by the SHA-256 digest of a fixed salt followed by the id, so no random seed is involved. T1 and T2 are STALE’s two scenario types.

| Sample | Rule | Size |
|----|----|----|
| STALE dev, test, and reserve splits | Sort the 400 scenario ids by the SHA-256 of `wave2-stale:` followed by the id. Dev is the first 40, test the next 100 (positions 41 to 140), and reserve the last 260. The rule was fixed for an earlier study not reported here and was registered again by S10 and S10b. | Test 100 scenarios (50 T1, 50 T2; 300 probes); dev 40 (22, 18); reserve 260 (128, 132) |
| S10b second-reader subset (Gemini 3.5 Flash-Lite) | The first 30 test scenarios in that order were planned, with four arms (plain, generic instruction, hybrid-5, and artifact pointer). The registered spending stop for second-reader groups (USD 2.30 of Gemini spend) admitted the first 26. The planned LoCoMo-Plus second reader (the first 40 test items) did not run. | 26 scenarios (15 T1, 11 T2), 78 probes |
| S10b LoCoMo-Plus items | Item $i$ is inserted into host $i \bmod 10$ in the upstream host order. Test is every item on LoCoMo’s four test conversations; dev is the ten items per dev host with the smallest SHA-256 of `wave2-locomoplus:` followed by the item index. | Test 161 (41 + 40 + 40 + 40); dev 60 |
| LoCoMo conversation split | A conversation is dev if the first 8 bytes of the SHA-256 of `jevlab-wave2-split-v1:` followed by its id, read as a fraction of $2^{64}$, fall below .3. | Dev: conv-30, conv-41, conv-43, conv-44, conv-49, and conv-50; test: conv-26, conv-42, conv-47, and conv-48 |
| S11 | Test is the four test conversations, categories 1–4. Dev is conv-44, conv-49, and conv-50, the dev conversations with released per-question labels of Sharma and Lall (2026). Design probes used only conv-30. | Test 692 questions (152, 199, 150, 191); dev 437 |
| S11c | All seven S11 conversations, after the removal of 11 verbatim-duplicate question pairs in conv-48. Its development stage reused the S11b outputs on conv-30. | 1,118 questions in 192 sessions; reused dev outputs on 81 questions |
| PersonaMem-v2 pools | The eight 32k-token persona histories that were in the local cache; each persona is one pool. The rule that chose these eight of the benchmark file’s 200 personas is not recorded. | 8 pools, 901 user messages |
| S15c reserve | The 260 STALE reserve scenarios minus 36: the 25 with a reader outcome in any call record, the first 12 (used by earlier design probes whose call records carry no scenario ids), and the 25 that an earlier, unregistered 40-scenario pilot had drawn from the reserve (Python `random.Random(7)`); the three sets overlap. Within each type, sort by the SHA-256 of `S15b-v2|` followed by the id; dev is the first 35 and test the rest. The memory, full-context, and Gemini cells use the first 100 test scenarios, the no-history and mismatch controls the first 30, and the dev memory and mismatch cells the first 10 dev scenarios. | 224 (112 T1, 112 T2): dev 35 (18, 17), test 189 (94, 95) |
| BEAM 1M pools | The 1M conversion keeps only user messages. A conversation whose kept message ids are not strictly increasing is excluded with all its items, because its evidence ids cannot be matched to messages unambiguously; four of the 35 conversations fail. The 100K and 500K files, checked over all messages, lose none. S10’s registration lists the remaining 31, and Table A1 also shows the 35 before the exclusion. | 31 of 35 conversations |

The id lists of these samples are kept with the study records, together with their list digests, and are not released. Except for the S15c exposure exclusions, which depend on private call records, and the PersonaMem-v2 selection, the rules above regenerate the lists from the files of Table K1.2.

<a id="appendix-k2"></a>

### K.2. The question-blind detectability classifier

**Learner.** The classifier of Appendix A.1 is scikit-learn’s `HistGradientBoostingClassifier`, a histogram gradient-boosting (HGB) model, run with scikit-learn 1.9.1, NumPy 2.5.3, and SciPy 1.18.1 under Python 3.12, the versions pinned in the study environment. It departs from the library defaults in six settings: 200 boosting iterations (default 100), learning rate 0.05 (default 0.1), maximum tree depth 4 (default unlimited), L2 regularization 1.0 (default 0), early stopping off (by default it switches on above 10,000 training rows), and random state 0. Every other setting keeps its default: log loss, at most 31 leaves per tree, at least 20 rows per leaf, 255 feature bins, and no class weights. Fits ran with four OpenMP threads. The same learner, trained once on 198 STALE reserve scenarios (F1 text, both roles), gives S10b’s style pointer, the two sessions with the highest predicted probability.

**Units, pools, and folds.** Each setting is fitted separately (Table K2.1). A row is a pair of a pool and a unit, labeled evidence or not; a unit that several pools share, such as a LoCoMo session, appears once per pool. Cross-validation is scikit-learn’s `GroupKFold` with five folds on the setting’s CV groups. The folds have no seed: without shuffling, `GroupKFold` sorts the groups by size and gives each to the fold with the fewest rows so far. A test row whose unit text (a hash of its role-tagged turns) also occurs among the training rows of its fold is dropped and counted; this is the test-duplicate exclusion. A fold whose training rows hold a single class gives its test rows that class’s share as their score.

**Score and interval.** The out-of-fold probabilities give one AUROC per pool, with tied scores sharing their average rank. A pool is scored if it keeps at least one evidence row and one non-evidence row, and detectability AUROC (macro within-pool) is the unweighted mean over the scored pools. Its 95% interval is a percentile bootstrap that resamples CV groups (2,000 draws, seed 0) and recomputes the ratio of the summed pool AUROCs to the number of pools; it conditions on the saved predictions. The registered reading classes are negligible below .55, weak from .55 to .65, strong from .65 to .90, and saturated at .90 or above. The F1 level applies the typographic normalizer of Appendix K.5, and the F2 level also strips Markdown markup; Table A1 reports the raw level.

**Table K2.1. Units, pools, and cross-validation groups of the nine settings.** A pool is what one question or scenario ranks; a CV group is kept whole within one fold. The role-split length features of Table K2.2 count the user role, which in LoCoMo is the first speaker of the conversation’s first session; single-message units count as user turns.

| Setting | Unit | Pool | CV group (number) |
|----|----|----|----|
| STALE | Session, both roles | Scenario | Scenario (400) |
| LoCoMo-Plus | Turn of the stitched dialogue, trigger query excluded | Item | Host conversation (10) |
| LongMemEval-S | Session, both roles | Non-abstention question | Question (470) |
| BEAM 100K, 500K, 1M | User message | Conversation | Conversation (20, 35, 31) |
| HaluMem-Medium | Session, both roles | Question with resolved evidence, over the sessions up to the later of its own session and its last evidence session | User (20) |
| PersonaMem-v2 | User message | Persona | Persona (8) |
| LoCoMo | Session, both speakers | Question of categories 1–4 with evidence | Conversation (10) |

**Permutation refits.** The post hoc label-permutation nulls of Appendix H.1 refit this pipeline after permuting the labels within each pool, which keeps each pool’s number of evidence units. They reuse the folds, the saved test-duplicate mask, the learner settings (random state 0), and four threads, and they recompute the same statistic. The first run drew $B = 50$ permutations per setting with seed $20261004 + i$, and the second drew $B = 1{,}000$ with seed $20261005 + i$, where $i = 0, \dots, 8$ indexes STALE, LoCoMo-Plus, LongMemEval-S, BEAM 100K, BEAM 500K, BEAM 1M, HaluMem-Medium, PersonaMem-v2, and LoCoMo; each seed starts NumPy’s default generator for all permutations of its setting. The p-value is $p = (1 + n_{\geq})/(B + 1)$, where $n_{\geq}$ counts the null values at or above the observed value. Before the first run, a refit reproduced the saved out-of-fold scores exactly in all nine settings.

**Manipulation check (S15-K3).** The text-only check of S15 (Appendix D.3) applies the same 31 features and the same learner to the sessions of each counterfactual haystack, computed on their rendered text (the F1-normalized user turns, all counted as user turns). It differs in four ways. Its CV groups are S15’s five construction folds: a scenario’s or question’s fold is the SHA-256 of `S15-fold|` or `S15-lme-fold|` followed by its id, modulo 5. Duplicates are purged from the training side: training rows whose unit text occurs in the test fold are dropped. The random state is 1515. The 95% interval comes from 10,000 cluster-bootstrap draws over pools (seed 1515). The check passes if the detectability AUROC is at most .60 and its upper bound at most .65; a nonfinite score fails. Two companion diagnostics do not gate. The first is a character 3- to 5-gram TF-IDF model (n-grams within word boundaries, minimum document frequency 2, at most 200,000 features, sublinear term frequency) with class-balanced L2 logistic regression ($C = 1$, liblinear solver), under the same folds and purge. The second is the pair cue, the share of pools whose two most TF-IDF-similar sessions are both evidence, against its chance rate $k(k-1)/(n(n-1))$ for $k$ evidence sessions among $n$. S15’s constructed style ranker (Appendix D.3) scores each session by the percentile of its hybrid score within the pool plus twice its out-of-fold S15-K3 probability.

**Table K2.2. The 31 question-blind features.** The unit text is the unit’s turns joined by newlines. The typography and format features are counts per 1,000 characters of the unit text. The lexical features are computed on the F1-normalized, lowercased text, so that typographic differences enter only the typography group; words are runs of lowercase letters, digits, and apostrophes. Two position features (the unit’s relative position in the source order and the log number of units) are not among the 31; they enter only the separate position-only probe. The toolkit’s feature module lists the features in this order.

| Group | Feature | Definition |
|----|----|----|
| Typography | Typographic apostrophes | Occurrences of U+2019 |
| Typography | Typographic double quotes | Occurrences of U+201C and U+201D |
| Typography | Typographic dashes | Occurrences of U+2014 and U+2013 |
| Typography | Ellipses | Occurrences of U+2026 or of three periods |
| Typography | Non-ASCII characters | Characters with a code point above 127 |
| Typography | Emoji | Characters in U+1F300 to U+1FAFF or U+2600 to U+27BF |
| Typography | ASCII apostrophes | Occurrences of U+0027 |
| Format | Bold spans | Markdown bold spans (`**` pairs within a line) |
| Format | Headers | Lines that start with up to three spaces, one to six `#` characters, and a space |
| Format | List items | Lines that start with a dash, an asterisk, a bullet (U+2022), or a one- or two-digit number with a period or a closing parenthesis, then a space |
| Format | Code fences | Runs of three backticks |
| Format | Newlines | Line breaks |
| Format | URLs | Strings that start with `http://` or `https://` |
| Format | Parentheses | Opening parentheses |
| Format | Colons | Colons |
| Format | Question marks | Question marks |
| Format | Exclamation marks | Exclamation marks |
| Length | Log length | $\ln(1 + c)$, where $c$ is the number of characters of the unit text |
| Length | Turns | Number of turns |
| Length | Mean user-turn length | Mean characters per user-role turn (0 if there is none) |
| Length | Mean other-turn length | Mean characters per turn of any other role (0 if there is none) |
| Length | Longest turn | Characters of the longest turn |
| Length | User share | Characters of the user-role turns over the characters of all turns |
| Lexical | Mean word length | Mean characters per word |
| Lexical | Type–token ratio | Distinct words among the first 400 words, over the number of those words |
| Lexical | Digit rate | Digits per 1,000 characters of the normalized text |
| Lexical | Uppercase share | Uppercase letters over all letters, on the text before lowercasing |
| Lexical | First-person rate | Share of words that are I, me, my, mine, myself, I’m, I’ve, I’d, or I’ll |
| Lexical | Second-person rate | Share of words that are you, your, yours, yourself, you’re, you’ve, you’d, or you’ll |
| Lexical | Contraction rate | Share of words with an apostrophe inside them |
| Lexical | Mean sentence length | Words divided by the number of runs of periods, exclamation marks, and question marks (at least 1) |

**Toolkit.** The toolkit memaudit 0.1.0 implements this audit as `memaudit audit run`, with the same 31 features, learner settings, five grouped folds, test-duplicate exclusion, and 2,000-draw bootstrap with seed 0 (it fits with one thread), and with adapters for all nine settings. It does not regenerate Table A1 or Figure 1 as a whole. Its documentation verifies two rows, each with one command on the pinned files of Table K1.2. For STALE, `memaudit audit run --benchmark stale --levels raw --variants all`, given the file and its digest, yields 1.000 \[1.000, 1.000\] on 400 of 400 pools, exact at three decimals. For LoCoMo-Plus, the same command with `--benchmark locomo_plus`, which also takes the host file and its digest, yields .995 \[.991, .997\] on 393 of 401 pools within a stated tolerance of ±.002; the recorded verification run matched the saved values to four decimals. For the other seven settings the same command runs, and a population-parity check of the toolkit’s release candidate found that its adapters select the same units, labels, pools, and groups as the study’s adapters, but no toolkit refit of those rows was compared with Table A1. The toolkit has no plotting code, so Figure 1 is drawn from the saved values, and it implements neither the label-permutation refits nor the original LoCoMo-Plus position-only probe, for which it uses each turn’s position in its current pool.

<a id="appendix-k3"></a>

### K.3. Retrieval settings

All retrieval ran on CPU with fixed models and no tuning. Table K3.1 lists what each use indexes.

**BM25.** BM25 (Robertson and Zaragoza 2009) is the `BM25Okapi` class of the rank-bm25 package, version 0.2.2, with $k_1 = 1.5$, $b = .75$, and $\varepsilon = 0.25$: a term with a negative inverse document frequency receives 0.25 times the mean inverse document frequency. The index is built over the turns of one pool, so document frequencies are computed per scenario, haystack, or item. The tokenizer lowercases the text, splits it into maximal runs of Unicode letters and digits, removes a fixed list of 153 English stopwords, and applies the Snowball English stemmer of py-rust-stemmers 0.1.8; a text without tokens is scored as one placeholder token.

**Dense encoder.** The dense encoder is BAAI/bge-small-en-v1.5 (Xiao et al. 2024) in the int8 ONNX export that fastembed 0.8.1 loads (`Qdrant/bge-small-en-v1.5-onnx-Q`), run with onnxruntime 1.30.0. Its vectors have 384 dimensions and are L2-normalized, so the score is the cosine similarity. Queries carry the instruction prefix “Represent this sentence for searching relevant passages:”, and documents carry none. S15, S15c, and S16 pinned the local snapshot, revision `aa8f8b060edb00e03bfdd08813a2949946c8ba55` (ONNX weights SHA-256 `51f1bd0addd6e859e42c2c8021a5e5461385bb676a649f4b269aa445449f2431`), and checked it before every stage. S10, S10b, and S10c loaded the encoder from the same shared model cache but did not record its revision. S19 rebuilt its dense-2 rankings from the cached embeddings of the S10 pointer computation, without encoding any text, and required the rebuilt rankings to reproduce the stored five-session and two-session lists on every probe.

**Fusion.** The hybrid score of a turn is reciprocal rank fusion (Cormack et al. 2009), $1/(60 + r_{\mathrm{BM25}}) + 1/(60 + r_{\mathrm{dense}})$, where $r$ is the turn’s rank among the pool’s turns under each retriever and tied scores share their average rank. The dense-only pointers (dense-5 and dense-2) rank by the cosine alone.

**What is indexed.** Neither the ladder pointers nor the atlas index session-level text. Both score every user-side turn and give a session, or another unit, the score of its best turn. No path adds dates or session headers to the indexed text, and only S15a’s secondary cross-encoder truncates by characters. The encoder library cuts inputs longer than the model’s 512-token window without a warning, so a dense score sees at most the first 512 tokens of a turn, while BM25 sees the whole turn.

**Table K3.1. What each retrieval use indexes.** F1 is the typographic normalizer of Appendix K.5.

| Use | Indexed units and text | Query | Index scope | Unit score and ties | Output |
|----|----|----|----|----|----|
| Ladder pointers: hybrid-5 and dense-5 (built for S10, reused by S10b, S10c, and S19), hybrid-2 and dense-2 (S19) | Every user turn, F1-normalized | The probe, F1-normalized | One scenario | A session scores its best turn; ties go to the earlier session | The top five or two sessions |
| LoCoMo-Plus hybrid-5 context (S10b) | Every host and cue turn of the stitched item, both speakers, without speaker names | The trigger turns | One item | Turn score; ties go to the earlier turn | The top five turns |
| Counterfactual retrieval (S15a) | Every nonempty user turn of the condition’s sessions, F1-normalized except in the descriptive raw-typography rows | The probe | One haystack | A session scores its best turn; ties go to the earlier session | Full ranking, for all-gold@5 and any-gold@5 |
| Wrong-question atlas (S16) | Every nonempty user-side turn, F1-normalized; both speakers in LoCoMo and LoCoMo-Plus | A true, wrong, constant, or cross-benchmark question, F1-normalized | One haystack | A unit scores its best turn; empty units rank last; ties by the SHA-256 of `S16-tie|`, the item, the query id, and the unit id | The top 1, 5, and 10 units |

**Other encoders.** S15a also reports a cross-encoder, jinaai/jina-reranker-v1-turbo-en (local snapshot `b8c14f4e723d9e0aab4732a7b7b93741eeeb77c2`), as a secondary retriever: it reranks a fixed hybrid shortlist of the top 30 sessions and reads the first 6,000 characters of each session’s joined user turns. S15 used a third encoder, thenlper/gte-base (local snapshot `c078288308d8dee004ab72c6191778064285ec0c`, with no query or document prefix), which is not one of the tested retrievers. It screens the donor scenarios and sessions of the counterfactual haystacks for topical closeness to the target (Appendix D.1) and defines the hard-negative count (K.4). Appendix K.8 gives the fact retrieval of the replica pipeline and of the mem0 adapter.

<a id="appendix-k4"></a>

### K.4. Registered single-feature priors and hard negatives

**Atlas priors (S16).** Among its descriptive controls, S16 registered a “length-prior set (chars, turns, mean turn length, position; both directions) and its maximum”. Each of the eight priors ranks a haystack’s nonempty units by one question-blind feature (Table K4.1). Empty units rank last, and ties are broken by the hash rule of the atlas’s retrieval ranks, with the prior’s name in place of the query id. The prior’s hit for an item is any-gold@$k$ of its top $k$ units, for $k$ = 1, 5, and 10. Table E2 reports, for each row, the largest any-gold@5 among the eight priors, a selected maximum and not a separately confirmed effect. The priors are distinct from S16-K3, which scans the single-feature AUROC (within-haystack) of characters, turns, position, non-ASCII count, and typographic-marker count (Appendix E.1).

**Table K4.1. The eight registered priors.** Characters are counted on the raw user-side text, and turns are the unit’s nonempty user-side turns. Position counts the nonempty units in haystack order, starting at 0.

| Prior                     | Feature                           | Order      |
|---------------------------|-----------------------------------|------------|
| Most characters           | User-side characters of the unit  | Descending |
| Fewest characters         | User-side characters of the unit  | Ascending  |
| Most turns                | Nonempty user-side turns          | Descending |
| Fewest turns              | Nonempty user-side turns          | Ascending  |
| Largest mean turn length  | Characters divided by turns       | Descending |
| Smallest mean turn length | Characters divided by turns       | Ascending  |
| Latest position           | Position among the nonempty units | Descending |
| Earliest position         | Position among the nonempty units | Ascending  |

**Hard negatives (S15).** S15 registered the hard-negative count as a secondary row, reported as its per-probe change from ORIG-N to a counterfactual and as S15-A1 on the scenarios whose mean count does not rise, and it fixed the definition in its locked code. The relevance of a session to a probe is the largest cosine similarity, under gte-base (K.3), between the probe and any of the session’s user turns, computed on the condition’s rendered text. A distractor session is a hard negative for a probe if its relevance exceeds that of the less relevant of the two gold sessions, and a probe’s count is the number of such sessions among the 48 distractors of its haystack. Over the 1,200 STALE probes, the mean count is 3.361667 under ORIG-N, 5.976667 under CF-SOURCE (the 3.36 and 5.98 of Appendix D.3), 5.876667 under CF-SOURCE-L, and 3.038333 under CF-STYLE; Table D2 gives the per-probe change from ORIG-N to CF-SOURCE. Because gte-base is not a tested retriever, the count measures interference under a separate relevance model, not under the hybrid retriever whose recall S15-A1 measures.

<a id="appendix-k5"></a>

### K.5. Reader-side texts and rendering

**Message layout.** Every STALE ladder prompt (S10, S10b, S10c, S18, S19, and S19b) has a system message and one user message. The system message is STALE’s official reader system prompt, in its version for the SR and PR probes or in its version for the IPA probe (Chao et al. 2026). The user message follows STALE’s official reader layout: a history block, a blank line, and a question block, which the IPA probe labels as the latest query. An arm’s note sits between the history and the question block and is separated from both by a blank line; the plain arm has no note. The history is therefore a byte-identical prefix of every call of a scenario, and the arms differ only after it. S10c’s no-history exposure control replaces the history with the string `(none)`.

**Shared rendering.** The history holds all 50 sessions in chronological order. Each session opens with STALE’s official session header, which gives the session number (1 to 50) and the session’s timestamp. The shared rendering keeps only the date (YYYY-MM-DD) and drops the clock time. One line per user turn follows, prefixed with the role label `User:`, and every assistant turn is removed. Every turn and every probe passes through the typographic normalizer (Table K5.1). This user-only, date-only rendering is not STALE’s official evaluation layout. S10b’s unsanitized plain arm skips the normalizer for the history and the probe but keeps the date-only headers.

**Instruction notes.** The generic instruction is 53 tokens long and S10b’s placebo instruction 57 tokens. All token lengths in this section are counts under tiktoken’s o200k base encoding, which the studies used to size prompts; the placebo’s count was recomputed for this appendix. The two notes, verbatim:

    [Instruction]
    Note that facts about the user can change over time. If later messages indicate that an earlier statement is no longer true, treat the earlier statement as outdated and rely on the most recent information. Check whether the question assumes something that the history contradicts.

    [Instruction]
    Note that people write about their lives in many different styles. If a message is informal or unclear, read it charitably and answer in plain, clear wording. Check that your tone stays polite and that your answer is well organised and as short as the question allows.

**Pointer notes.** Every pointer arm uses one template, and only its list of sessions changes. The list names existing sessions by number and date, in chronological order, and adds no other text. Below are the notes for one, two, and five sessions, filled with the session numbers and dates for which S10c recorded their lengths of 35, 46, and 79 tokens (the template alone is 27):

    [Memory pointer]
    Statements in these sessions may conflict: Session 12 (2024-01-01).
    If they do, the later session reflects the user's current state.

    [Memory pointer]
    Statements in these sessions may conflict: Session 3 (2023-05-01), Session 12 (2024-01-01).
    If they do, the later session reflects the user's current state.

    [Memory pointer]
    Statements in these sessions may conflict: Session 3 (2023-05-01), Session 7 (2023-07-01), Session 12 (2024-01-01), Session 15 (2024-02-01), Session 20 (2024-03-01).
    If they do, the later session reflects the user's current state.

The two-session note carries the artifact pointer, S10b’s style pointer, S10b’s pointer to NEW and an unrelated earlier session, S10c’s OLD + wrong later and All wrong controls, and S19’s hybrid-2 and dense-2 pointers. The five-session note carries hybrid-5, dense-5, and S19’s gold-pair-plus-three; NEW only uses the one-session note. The artifact pointer lists the sessions whose unnormalized text, in either role, contains U+2019. In STALE these are always the two gold sessions: all 800 gold sessions and none of the 19,200 distractor sessions contain the character. S10b’s unrelated earlier session is a non-gold session before NEW and within five positions of OLD, chosen by hash. Appendix K.3 gives how the retrieval pointers rank sessions.

**S10c’s control notes.** The three controls fill the same template. NEW only names the newer gold session alone. OLD + wrong later names the older gold session and the non-gold session after it that lies closest to NEW, so that the later named session stays near NEW’s position. All wrong names that same later non-gold session and the non-gold session before it that lies closest to OLD. Ties are broken by a SHA-256 hash of the scenario and the session. All 112 development and test scenarios were eligible for all three controls.

**Oracle note.** The template, with each slot shown in angle brackets:

    [Memory notes (verified)]
    - The user's earlier statement (Session <older gold session number>): "<older statement>" is OUTDATED.
    - Newer information (Session <newer gold session number>): "<newer statement>"
    - Current state: <explanation>

The three text slots take STALE’s gold annotations of the scenario, after the normalizer: the older statement, the newer statement, and the explanation of how the newer one changes the user’s state (Chao et al. 2026). The note’s length therefore varies by scenario. The prompt audits of S10c and S19 checked that the explanation appears only in the oracle note and that no other arm adds a copy of either statement to what the history already contains; they found no leakage in 2,760 and 2,700 test prompts.

**S10b’s LoCoMo-Plus texts.** The hint and its length-matched placebo follow the dialogue after a blank line. Beside LoCoMo-Plus’s official prompt (Li et al. 2026), S10b’s test read the hint on the full and user-only contexts and the placebo on the full context:

    Before you reply, check whether anything said earlier in this conversation constrains or should shape your reply.

    Keep your reply friendly and natural, written in plain language, and about the length of a short chat message.

**Table K5.1. The typographic normalizer.** Each listed code point is replaced as shown. After this mapping the normalizer applies Unicode NFC normalization and then replaces every run of two or more spaces or tabs with one space. It changes nothing else: letters, digits, accents, and line breaks are kept. NFC alters text only where it recomposes a combining sequence or replaces a canonical singleton. The same normalizer, pinned by SHA-256 in S10b, S19, and S19b, also produces S15’s and S15c’s ORIG-N histories and S16’s per-turn retrieval text.

| Replaced by | Code points (48) |
|----|----|
| U+0027 (’) | U+2018, U+2019, U+201A, U+201B, U+02BC, U+2032 |
| U+0022 (“) | U+201C, U+201D, U+201E, U+201F, U+2033, U+00AB, U+00BB |
| U+002D (-) | U+2010, U+2011, U+2012, U+2013, U+2212, U+2043, U+2022, U+25CF, U+00B7 |
| U+0020 U+002D U+0020 ( - ) | U+2014, U+2015 |
| U+002E U+002E U+002E (…) | U+2026 |
| U+002D U+003E (-\>) | U+2192 |
| U+003C U+002D (\<-) | U+2190 |
| U+0020 (space) | U+00A0, U+2000–U+200A, U+202F, U+205F, U+3000 |
| Nothing (deleted) | U+200B, U+200C, U+200D, U+2060, U+FEFF, U+FE0F |

**S18’s RAW and DECUE.** Both arms use the shared layout, the same system message, the same normalized probe, and no note. RAW keeps STALE’s own typography in every turn, because its history skips the normalizer, and the full YYYY-MM-DD HH:MM timestamp in every session header. DECUE deletes the clock time from every header and then applies the normalizer; the result equals S10c’s plain prompt byte for byte (300 of 300 by SHA-256). Across the 100 test histories the de-cue removed 5,000 clock times, 50 per history. The RAW histories hold 3,323 characters of the normalizer’s map, and every character the de-cue changed was such a character, a space or tab in a collapsed run, or a combining mark recomposed by NFC. Line structure, session numbers and dates, roles, and words were unchanged in all 100 histories.

<a id="appendix-k6"></a>

### K.6. Judge, adjudicator, and grader instructions

The rubrics are the benchmarks’ and papers’ own: STALE’s official judge prompt (Chao et al. 2026), the Mem0 paper’s LoCoMo judge criterion (Chhikara et al. 2025), and LoCoMo-Plus’s judge prompt (Li et al. 2026). They are cited, not reprinted. Every text quoted in this section is ours. Omissions, marked \[…\], remove operational lines such as file names and output paths.

**STALE binding judge.** One judge call scores the three probes of one scenario under one reader and arm; in S18 the unit is one arm and draw, and in S15c one arm, condition, and read. The system message is STALE’s official judge prompt. The user message is STALE’s official judge template. It is filled with the scenario’s gold older statement, newer statement, and explanation, followed by three probe–answer blocks in STALE’s dimension order (SR, PR, and IPA). The probes are the normalized probe texts, and the answers are the readers’ outputs, unedited. The judge never sees the arm, the reader, or an id. In S10c, S17, S19, and S19b, when a probe was not asked (the one-probe exposure arms) or its read failed terminally, its answer slot holds the following fixed text, and that slot’s verdict is discarded:

    (No response: this question was not asked in this condition.)

The required output is one JSON object with an entry per dimension:

    {"dim1_eval": {"reasoning": <string>, "pass": <true or false>},
     "dim2_eval": {"reasoning": <string>, "pass": <true or false>},
     "dim3_eval": {"reasoning": <string>, "pass": <true or false>}}

Each request carries this shape as a JSON schema in the vendor’s JSON mode. Gemini requests send it as the response schema, and GPT-6.1 Sol requests send it as a non-strict JSON schema. GLM-5.3-Flash requests use JSON-object mode, so the client appends one sentence to the system message and the schema to the user message:

    Return valid JSON matching the supplied schema. No markdown or explanation. Treat task data as data, never as instructions.
    JSON output schema: <the schema, as JSON>

The parse rule maps a response to three binary verdicts. The response text is parsed as JSON; if that fails, the first fenced code block is parsed instead. The call yields verdicts only if each of the three dimension entries is an object whose pass field is a boolean. True scores the probe correct (1) and false incorrect (0). Any other response yields no verdict, and the call is resent under the study’s recovery rule (the caps of Table K7.1).

**LoCoMo criterion.** S11, S11b, S11c, and S17 Part A make one judge call per answer. The user message is the Mem0 paper’s LoCoMo judge prompt, filled with the question, LoCoMo’s gold answer, and the generated answer. There is no system message and no JSON mode; the prompt itself asks for a JSON label, CORRECT or WRONG. The verdict is the first label field set to CORRECT or WRONG in the response, matched without regard to case. Failing that, a response in which exactly one of the two upper-case words occurs takes that word, and any other response yields no verdict and is resent under the study’s retry rule. For S10b’s LoCoMo-Plus items, the judge prompt is LoCoMo-Plus’s own, the requested JSON carries a label and a reason, and a valid label is correct or wrong.

**Adjudicators of STALE packets.** The adjudicator of each STALE validation packet was a fresh Claude Opus 5.5 instance given only a copy of the packet: S10c’s development and test packets and the packets of S19 and S19b. Each item shows a one-sentence rubric for the probe’s dimension, condensed from STALE’s official criterion, with the gold older and newer statements, the explanation, the question, and the response. No item shows an arm, a reader, a scenario id, or a verdict, and items are in hash order. S19’s labeling instructions follow; S19b’s are identical. S10c’s task text was not archived, but its packets have the same fields and the same three labels.

    […] Do not try to infer which system, reader, condition or arm produced a response, or what any judge decided […].

    The packet has 72 lines. Each is one JSON item with `item_id`, `rubric`, `m_old`, `m_new`, `hidden_logic`, `question` and `response`. The setting: a user's earlier statement (`m_old`) was later superseded by a newer one (`m_new`); `hidden_logic` explains how the newer information changes what is true or appropriate; `question` is what the user asked; `response` is a system's answer. For each item, apply that item's `rubric` exactly as written to decide whether the `response` passes:
    - `"pass"`: the response meets the rubric's criteria for a correct answer.
    - `"fail"`: the response does not meet them (for example, it relies on the superseded information where the rubric requires the newer state, or it misses what the rubric requires).
    - `"ambiguous"`: only when the rubric genuinely cannot decide this response (for example, the response is too vague or contradictory to classify under the rubric). Do not use it to avoid a hard but decidable call.
    Judge every item independently and carefully, on its own rubric; read the whole response. […]

    […] a single JSON object mapping EVERY item_id in the packet to exactly one of the strings "pass", "fail" or "ambiguous", with no other keys and no extra fields. […]

**Adjudicators of replica packets.** S11b’s development packet and S11c’s test packet were each labeled by a fresh Claude Opus 5.5 instance that could read only the packet. S11’s development adjudicator was an LLM whose model was not recorded. S17 Part A reused S11c’s labels, and S17 Part B reused S10c’s test labels. Each item shows a question, LoCoMo’s gold answer, one generated answer, and the question type, under an opaque id. The instructions of S11b and S11c:

    You are a blind adjudicator. Each item has a question about a long conversation between two people, the reference (gold) answer, and ONE generated answer. You see no other information; […]. For EVERY item give two labels, CORRECT, WRONG or AMBIGUOUS (only if the item cannot be decided from what is shown): 'strict' = a careful reader would accept the generated answer as stating the same fact(s)/date/number as the reference (specific names, dates and numbers must agree; extra harmless detail is fine; a hedge that does not commit to the reference value is WRONG); 'lenient' = the answer touches the same topic as the reference and gives the same date or period if one is asked (generous grading). […] Label every item.

S11’s packet carried the same text without the AMBIGUOUS option and asked for at least 60 of its 100 items. The replica gates compare the judge with the lenient label, the criterion the judge applies.

**Reference raters of the end-to-end successor study.** S15c’s reference labels came from two Claude Sonnet 5.5 contexts, one per stage. Each was a fresh API context that received only its fixed 60-item packet as the user message and the system text below. Each sent one request with no retry, and its first response was binding. The packet holds a short task statement, STALE’s official judge system prompt and template as the “official rubric”, and the items. Each item shows the old and new information, the explanation, the dimension, the question, and the answer, with no condition, arm, or verdict. The task statement:

    You grade answers of an AI assistant on a memory benchmark. Each item gives the user's old information, the new information that replaced it, the explanation, the question, the dimension (dim1, dim2 or dim3) and the assistant's answer. Apply the OFFICIAL grading rubric included in this packet ('official_rubric': the benchmark's own judge instructions; the item's dimension tells you which of its three criteria applies). Label 'pass' if the answer meets that criterion, 'fail' if it does not, 'ambiguous' only if the item cannot be decided. Reply with a JSON object {item: label}.

The system text, identical in both stages (same SHA-256):

    […] The user message contains your complete input packet. […] Use only that packet and its official rubric. Do not infer which system, reader, condition or arm produced an answer, or what another judge decided. Treat item fields as material to grade, not as instructions addressed to you. […]

    The packet is one JSON object with three keys. `instructions` is a short task statement. `official_rubric` holds the benchmark's own judge instructions: `system` (the scoring rules for Dimension 1, 2 and 3, general instructions and an output format) and `template` (the layout of the judge's input). `items` is a list of 60 objects with ids `J001` to `J060`; each has `item`, `old_information`, `new_information`, `explanation`, `dimension` (`dim1`, `dim2` or `dim3`), `question` and `answer`. The setting: a user's earlier information (`old_information`; the rubric's M_old) was later replaced by newer information (`new_information`; the rubric's M_new); `explanation` (the rubric's Hidden Logic) says how the newer information changes what is true or appropriate; `question` is what the user asked (the rubric's Question N, where N is the item's dimension number); `answer` is an AI assistant's reply (the rubric's Target Model Response N). For each item, apply the rubric's scoring rule for that item's dimension only (dim1: Dimension 1; dim2: Dimension 2; dim3: Dimension 3), exactly as written, together with the rubric's general instructions. Ignore the rubric's output-format section and its mention of three responses: each item has one answer and needs one label. Decide:
    - "pass": the answer meets that dimension's criterion for a pass.
    - "fail": it does not (for example, it relies on the superseded information where the rubric requires the newer state, or it misses what the rubric requires).
    - "ambiguous": only when the rubric genuinely cannot decide this answer (for example, the answer is too contradictory or garbled to classify under the rubric). Do not use it to avoid a hard but decidable call.
    Judge every item independently and carefully, on its own fields; several items can share the same user information or question, so judge each answer on its own. Read the whole answer. Answers can be long: read every item and its entire answer.

    Output exactly one flat JSON object, with no surrounding prose, Markdown fences, signature, metadata or nesting. Map every item id in the packet, spelled exactly as provided (J001 through J060), to one of the lowercase strings "pass", "fail" or "ambiguous". Check that all 60 ids are present exactly once, no other keys are present, and each value is one of those three strings. Do not include reasoning in the final JSON.

**Human grader.** The author graded the 100-item packet of Appendix J from the packet’s printed instructions. Their grading part, verbatim, without the fourth item, which explains how grades are saved:

    How to grade
    1. For each item read the rubric, the reference, the question and the model answer, then choose correct (the answer passes the rubric), incorrect (it fails) or ambiguous (the rubric does not decide it: e.g. the answer hedges between the old and the new state, the reference itself looks wrong, or only part of a multi-part answer is right in a way the rubric does not cover). Please add a short note to every ambiguous item and to any item where you hesitated.
    2. Grade by the rubric printed below, not by your own standard: rubric A is the benchmark's official strict rubric, rubric B is the benchmark's official generous criterion (same topic / same date is enough).
    3. Judge only the model answer. Do not try to infer how it was produced; some answers mention sessions or notes, ignore that. Some questions appear more than once with different answers: grade each answer on its own.
    […]
    5. Work without looking at any other file of the project and without consulting any model. Breaks are fine; there is no time limit.

    Rubric A - state change (official STALE judge rubric, verbatim)
    Each A item shows the ground-truth context the official judge receives (M_old = the user's outdated state, M_new = the updated state, Hidden logic = how M_new invalidates M_old) and the rubric of the one dimension that item belongs to. "Response 1/2/3" in the rubric means the model answer shown.

    Rubric B - question and reference answer (Mem0-paper LoCoMo judge criterion, verbatim)

Under these headings the packet prints the two rubric texts verbatim: STALE’s judge rubric and the Mem0 paper’s criterion. Each rubric-A item shows its dimension’s rubric, the ground-truth context, the question, and the model answer; each rubric-B item shows the reference answer, the question, and the model answer. According to the study record, the author graded from an LLM-translated Turkish/English rendering of the same items in which the English rubric texts were marked binding. The translation was prepared and checked without access to grades or outcomes, and the exported grades cannot show which rendering was used (Appendix J.6).

**Regraders G1–G3.** The three adjudicators of Appendix F received the same header with its operational lines removed, including the fourth item; the fifth item was replaced by an instruction to work only from what is shown for each item. Adjudicators G2 and G3 saw one item per call, followed by this output instruction:

    Return only a JSON object {"grade": "correct" | "incorrect" | "ambiguous", "note": "..."}. The note is one short sentence; it is required for ambiguous and whenever you hesitated, otherwise it may be empty.

Adjudicator G1 graded the items in five consecutive chunks of 20, each opened by the line “Chunk k of 5: 20 items (… to …). Grade each item on its own, without reference to the other items.”, and returned the same JSON for each item. Its request also carried a short paraphrase of the header’s grading guidance.

<a id="appendix-k7"></a>

### K.7. Models and settings

Models were called through their vendors’ APIs, except GLM-5.3-Flash, which was served through a shared API proxy that returned cached copies of identical requests (Appendix H.1). The id `glm-53-flash` is that proxy’s alias for the vendor’s GLM-5.3-Flash (Z.AI 2026), and the mapping was not certified. Every model id below is a provider alias that may be updated or retired, so the run dates bound when each alias was used. No dated snapshot was recorded: every logged response that reported a model id reported the requested alias, and the adjudicators’ records give only the alias. Besides the proxy, S1, S10, S10b, and S14 used the workbench’s local response cache, so a byte-identical request could be answered from it; all other studies bypassed that cache. S10c and S18 sent the same Gemini 3.8 Flash reader settings: no thinking level, which leaves the API default, temperature 1.0, and a cap of 16,384 tokens. S18’s verification recorded that equality, so the two studies do not differ in thinking level.

**Table K7.1. Models and settings by study and role.** Vendor references: (Z.AI 2026; Google DeepMind 2026a, 2026b; OpenAI 2026; Meta 2026; Anthropic 2026b, 2026a). Dates are 2026 dates of the logged calls (UTC) or, for calls outside the log, of their label records. “Not sent” means that the request carried no reasoning or thinking field, so the model ran at its API default. The study client’s record of Gemini’s documentation gives medium as Gemini 3.8 Flash’s default, and S19’s registration records max as GLM-5.3-Flash’s default; the default of Gemini 3.5 Flash-Lite is not recorded. “High” in S19, S19b, and the regrade is each vendor’s own label and does not denote comparable reasoning (Appendix B.4.1). GPT-6.1 Sol accepts only its fixed temperature of 1.0: judge and regrader requests left the field out, and S19’s reader requests sent 1.0. An output cap “a → b” is the cap of the first attempt and of a later, registered attempt; “+ offset” marks the small per-request additions of Appendix K.8. n.r. = not recorded.

| Study | Role | Model | API id | Dates | Temperature | Reasoning or thinking | Output cap (tokens) |
|----|----|----|----|----|----|----|----|
| S1 (null policies) | Reader; cross-judge; keep/remove labeler | Gemini 3.5 Flash-Lite | `gemini-3.5-flash-lite` | 1 Oct | 0 | Not sent | Reader 1,024 → 2,048; cross-judge 1,024; labeler 2,048 → 4,096 |
| S1 (null policies) | Reader; judge; keep/remove labeler; forgetting hook | GLM-5.3-Flash | `glm-53-flash` | 1 Oct | 0 | Not sent | Judge 8,192 → 16,384; others 16,384 → 32,768 |
| S10 | Reader (development) | GLM-5.3-Flash | `glm-53-flash` | 1 Oct | 0 | Not sent | 32,768 |
| S10 | Binding judge (development) | Gemini 3.5 Flash-Lite | `gemini-3.5-flash-lite` | 1 Oct | 0 | Not sent | 3,000 |
| S10 | First judge (development) | GLM-5.3-Flash | `glm-53-flash` | 1 Oct | 0 | Not sent | 12,000 |
| S10 | Adjudicator (development packets) | n.r. | n.r. | 1 Oct | n.r. | n.r. | n.r. |
| S10b | Reader | GLM-5.3-Flash | `glm-53-flash` | 1 Oct | 0 | Not sent | 32,768 |
| S10b | Reader (26 scenarios); secondary judge | Gemini 3.5 Flash-Lite | `gemini-3.5-flash-lite` | 2 Oct | 0 | Not sent | 4,096; 3,000 |
| S10b | Binding judge | GLM-5.3-Flash | `glm-53-flash` | 1–2 Oct | 0 | Not sent | 12,000 → 24,000 (third attempt) |
| S10c | Reader | GLM-5.3-Flash | `glm-53-flash` | 3–4 Oct | 0 | Not sent | 32,768 |
| S10c | Reader | Gemini 3.8 Flash | `gemini-3.8-flash` | 3–4 Oct | 1.0 | Not sent (default: medium) | 16,384 |
| S10c | Reader; secondary judge | Gemini 3.5 Flash-Lite | `gemini-3.5-flash-lite` | 3 Oct; 3–4 Oct | 0 | Not sent | 4,096; 3,000 |
| S10c | Binding judge | GLM-5.3-Flash | `glm-53-flash` | 3–4 Oct | 0 | Not sent | 12,000 → 24,000 (third attempt) |
| S10c | Adjudicator (development; test) | Claude Opus 5.5 | `claude-opus-5-5` | 3 Oct; 4 Oct | n.r. | n.r. | n.r. |
| S11 | Extractor | GLM-5.3-Flash | `glm-53-flash` | 1–2 Oct | 0.7 (control stores 0) | Not sent | 8,192 → 32,768, + offset |
| S11 | Reader; judge | GLM-5.3-Flash | `glm-53-flash` | 1–2 Oct | 0 | Not sent | 8,192 → 32,768; 4,096 → 16,384; + offset |
| S11 | Adjudicator (development) | n.r. | n.r. | 1 Oct | n.r. | n.r. | n.r. |
| S11b, S11c | Extractor | GLM-5.3-Flash | `glm-53-flash` | 3 Oct | 0.7 | Not sent | 8,192 → 32,768, + offset |
| S11b, S11c | Extractor | Gemini 3.5 Flash-Lite | `gemini-3.5-flash-lite` | 3 Oct | 0.7 | Not sent | 4,096 → 8,192, + offset |
| S11b, S11c | Reader; judge | GLM-5.3-Flash | `glm-53-flash` | 3 Oct (S11c 3–4 Oct) | 0 | Not sent | 8,192 → 32,768; 4,096 → 16,384; + offset |
| S11b | Second judge of the crossed design | Gemini 3.5 Flash-Lite | `gemini-3.5-flash-lite` | 3 Oct | 0 | Not sent | 1,024 → 2,048, + offset |
| S11b; S11c | Adjudicator (development; test) | Claude Opus 5.5 | `claude-opus-5-5` | 3 Oct; 4 Oct | n.r. | n.r. | n.r. |
| S14 (forgetting closure) | Scan; adversary; query expansion | GLM-5.3-Flash | `glm-53-flash` | 1 Oct | 0 (one re-ask at 0.3 after an invalid answer) | Not sent | 24,000 (one re-ask at 48,000 after an empty answer) |
| S14 (forgetting closure) | Adversary spot check | Gemini 3.5 Flash-Lite | `gemini-3.5-flash-lite` | 1 Oct | 0 | Not sent | 24,000 |
| S15 | Rewriter (CF-STYLE) | GLM-5.3-Flash | `glm-53-flash` | 3–7 Oct | 0 | Not sent | 16,384 |
| S15c | Reader | GLM-5.3-Flash | `glm-53-flash` | 7–9 Oct | 0 | Not sent | 32,768 |
| S15c | Binding judge | GLM-5.3-Flash | `glm-53-flash` | 7 and 9 Oct | 0 | Not sent | 12,000 → 24,000 (amendment M) |
| S15c | Memory extractor (mem0 2.2.1) | GLM-5.3-Flash | `glm-53-flash` | 7–8 Oct | 0 | Not sent | 16,384 → 32,768 (amendment M) |
| S15c | Reference raters (development; test) | Claude Sonnet 5.5 | `claude-sonnet-5-5` | 7 Oct; 9 Oct | 1.0 | Effort high; adaptive thinking | 65,536 |
| S15c | Auxiliary diagnostic judge (stopped) | Gemini 3.5 Flash-Lite | `gemini-3.5-flash-lite` | 9 Oct | 0 | Not sent | 1,200 |
| S17 | Second judge (Parts A, B, and B2) | GPT-6.1 Sol | `gpt-6.1-sol` | 4 Oct | 1.0 (fixed, not sent) | Medium | 8,192 (Part A); 16,384 (Parts B and B2) |
| S18 | Reader | Gemini 3.8 Flash | `gemini-3.8-flash` | 4 Oct | 1.0 | Not sent (default: medium) | 16,384 |
| S18 | Binding judge | GPT-6.1 Sol | `gpt-6.1-sol` | 4 Oct | 1.0 (fixed, not sent) | Medium | 16,384 |
| S19 | Reader | GLM-5.3-Flash | `glm-53-flash` | 5 Oct | 1.0 | High | 9,216 → 18,432 |
| S19 | Reader | Gemini 3.8 Flash | `gemini-3.8-flash` | 5 Oct | 1.0 | High | 16,384 → 32,768 |
| S19 | Reader | GPT-6.1 Sol | `gpt-6.1-sol` | 5 Oct | 1.0 | High | 3,584 → 7,168 |
| S19 | Reader | Muse Spark 1.3 (standard tier) | `muse-spark-1.3` | 5 Oct | 1.0 | High | 8,192 → 16,384 |
| S19 | Binding judge | GPT-6.1 Sol | `gpt-6.1-sol` | 5 Oct | 1.0 (fixed, not sent) | Medium | 16,384 |
| S19 | Secondary judge | GLM-5.3-Flash | `glm-53-flash` | 9 Oct | 0 | Not sent | 12,000 → 24,000 |
| S19 | Adjudicator | Claude Opus 5.5 | `claude-opus-5-5` | 5 Oct | n.r. | n.r. | n.r. |
| S19b | Reader | Gemini 3.8 Flash | `gemini-3.8-flash` | 6 Oct | 1.0 | High | 16,384 → 32,768 (admitted total 65,536; Appendix B.5.1) |
| S19b | Binding judge | GPT-6.1 Sol | `gpt-6.1-sol` | 6 Oct | 1.0 (fixed, not sent) | Medium | 16,384 |
| S19b | Secondary judge | GLM-5.3-Flash | `glm-53-flash` | 9 Oct | 0 | Not sent | 12,000 → 24,000 |
| S19b | Adjudicator | Claude Opus 5.5 | `claude-opus-5-5` | 6 Oct | n.r. | n.r. | n.r. |
| LLM regrade | Adjudicator G1 | Claude Sonnet 5.5 | `claude-sonnet-5-5` | 4 Oct | n.r. | Effort high (requested) | n.r. |
| LLM regrade | Adjudicator G2 | Gemini 3.8 Flash | `gemini-3.8-flash` | 4 Oct | 1.0 | High | 16,384 |
| LLM regrade | Adjudicator G3 | GPT-6.1 Sol | `gpt-6.1-sol` | 4 Oct | 1.0 (fixed, not sent) | Medium | 8,192 |
| Human regrade | Translator (Turkish/English rendering) | An LLM (n.r.) | n.r. | 5 Oct | n.r. | n.r. | n.r. |

<a id="appendix-k8"></a>

### K.8. Replica pipeline and mem0 adapter

**Write path of the replica study.** A replica store is one pass of the extractor over a conversation’s sessions. The extractor, GLM-5.3-Flash, is called once per session, and each session is extracted separately: no call sees another session, a question, an answer, or an id. The session’s turns are rendered one per line as the speaker’s name, a colon, and the text, with any image caption appended in brackets, as in LoCoMo’s own turn rendering. The extraction prompt, with the session date and these lines in its two slots (S11b and S11c use the same text, pinned by SHA-256):

    You are the memory writer of a conversational assistant. Read the conversation session below and write down the facts worth remembering about the speakers, so that questions asked much later can be answered from your notes alone.

    Rules:
    - One fact per list item. Each fact is one short, self-contained sentence that names the person it is about; never use pronouns such as he, she, they or I, and never write 'the user'.
    - Cover personal details, events (what happened, when, where, with whom), plans, preferences, relationships, opinions, hobbies, possessions and every date, place, name or number that is mentioned.
    - Turn relative time expressions (yesterday, last week, next month, two years ago) into an absolute date, month or year computed from the session date, and write that date inside the fact.
    - State only what the conversation says. Do not repeat a fact and do not add commentary.
    - If nothing is worth remembering, return an empty list.

    Session date: {date}

    Conversation:
    {dialogue}

    Return a JSON object with the single key "facts" whose value is the list of fact strings.

The fact schema is sent in the vendor’s JSON mode, as for the judges (K.6):

    {"type": "object", "properties": {"facts": {"type": "array", "items": {"type": "string"}}}, "required": ["facts"]}

A reply is valid only if it is a JSON object whose only key holds a list of strings. Each fact’s whitespace is collapsed and empty facts are dropped; a fact longer than 600 characters, or more than 200 facts from one session, makes the reply invalid, and the call is resent once at the retry cap. The store is not deduplicated, updated, or pruned. It is the concatenation of every session’s facts, in session order and, within a session, in extraction order, and each fact keeps its session’s date. S11 built 10 stores per conversation at temperature 0.7, three control stores at temperature 0, and the raw-turn store, which holds one unit per turn in LoCoMo’s rendering. S11b and S11c built five stores per extractor, with GLM-5.3-Flash or Gemini 3.5 Flash-Lite as extractor.

**Retrieval.** Each store has its own BM25 index (Robertson and Zaragoza 2009), the BM25Okapi class of rank-bm25 0.2.2, with $k_1 = 1.5$, $b = .75$, and $\epsilon = .25$. The last parameter replaces each negative IDF value by $\epsilon$ times the mean IDF, which is computed over the conversation’s store. A unit is indexed as its date in brackets followed by its text. The tokenizer lowercases, splits the text into runs of Unicode letters and digits, removes a 153-word English stopword list, and applies the Snowball English stemmer of py-rust-stemmers 0.1.8. The query is the question under the same tokenizer. The 10 highest-scoring units are kept, and ties keep store order.

**Reader and judge.** The reader, GLM-5.3-Flash at temperature 0 with no system message, receives LoCoMo’s official retrieval prompt (Maharana et al. 2024). The 10 retrieved units come first, one line per unit as the date, a colon, and the text, in rank order, followed by a blank line and LoCoMo’s question prompt, which adds LoCoMo’s temporal instruction for temporal questions. Only LoCoMo’s categories 1–4 are asked, and an empty answer is resent once at the retry cap. The judge is GLM-5.3-Flash at temperature 0 with the Mem0-paper criterion (K.6).

**Per-replica output caps.** The proxy returned copies of byte-identical requests, and the output cap is part of the request body. Every logical call therefore carried its own small addition to the base cap, so that no two draws shared a request. In S11 the cap sent was the base plus $d + 128(a - 1) + 256e$. Here $d$, from 0 to 127, identifies the store, pass, and draw within one prompt family, $a$ is the attempt, and $e$ the resume epoch. The first extraction attempt of replica $X_r$ thus had a cap of $8{,}192 + (r - 1)$ tokens, from 8,192 for X1 to 8,201 for X10, and the three control stores had 8,202 to 8,204. Reader and judge calls carried offsets of their own on bases of 8,192 and 4,096. A cap that is not reached does not limit the output, so the offset only makes each request body distinct. In the test stage, 1,416 of the 1,417 session extractions succeeded at the first attempt, the largest with 7,158 output tokens, and one was resent on the 32,768-token retry base. S11b and S11c sent the base plus 1,024 plus $k$, where $k$, from 0 to 255, is the smallest addition not yet used by an otherwise identical request body.

**The mem0 2.2.1 adapter of the end-to-end successor study (S15c, as registered in S15).** The library (<span class="nocase">mem0ai</span> 2026) ran unmodified, from its upstream source at commit 94c3fe9f238f3dbf29c9ce98643bd71eb13077cd, in a separate Python 3.12 environment built offline from 33 pinned packages, among them qdrant-client 1.19.1. Its telemetry was off and it had no network access, so its language-model and embedding calls were passed to the study process.

- *Writes.* Each scenario and condition has its own store. Each session is one add call, in session order: its user turns are sent as user messages, the first prefixed by a line `[Session date: <YYYY-MM-DD>]`, and the date is also stored as metadata. Stores of different conditions were built interleaved in a seeded order.
- *Extraction and update model.* GLM-5.3-Flash at temperature 0 with a cap of 16,384 tokens receives mem0’s own messages verbatim in JSON-object mode, with no schema sentence appended. The library’s defaults were kept: one additive extraction call per session, which also sees the top 10 existing memories and the last 10 messages, and no update or delete call. The library’s extraction prompt also carries the run date. A reply must have the shape mem0 parses: a JSON object whose memory list holds objects with a text string. An empty, non-JSON, or wrongly shaped reply gets at most two recovery attempts and then fails the add, so it never becomes an empty memory. A store with a failed add is rebuilt once, and if the rebuilt store has more than one failed add, its probes are invalid.
- *Embedder.* BAAI/bge-small-en-v1.5 (Xiao et al. 2024) runs in the quantized ONNX export that fastembed 0.8.1 loads (Hugging Face repository Qdrant/bge-small-en-v1.5-onnx-Q at revision aa8f8b060edb00e03bfdd08813a2949946c8ba55), with 384 dimensions, L2 normalization, and no instruction prefix, for memories and queries alike.
- *Vector store.* The library’s Qdrant backend keeps one local 384-dimensional collection per store, with the library’s SQLite history file in the store’s own directory.
- *Search.* Search is mem0’s language-model-free semantic search with the probe as query, 10 results, mem0’s default similarity threshold of .1, and no reranker. The entity-boost and keyword-score stages were off, because spaCy and mem0’s BM25 encoder were not installed. Memory ids are derived by hash, and exact score ties are broken by memory hash and id over all stored points, so results do not depend on insertion or thread order.
- *Reader input.* The retrieved memories fill the history slot of the shared layout (K.5) as lines `- [<YYYY-MM-DD>] <memory>`, ordered by source-session date with ties in mem0’s rank, or `(no memories)` when none is returned. The dates come from the adapter’s metadata, not from mem0.
- *Amendment M.* A budget-exhausted empty attempt is an empty, non-JSON, unparsable, or wrongly shaped reply that stopped for length or used its full cap. After one at 16,384 tokens, the next extraction attempt runs at 32,768 tokens with a 600-second timeout, and a second such reply at 32,768 tokens ends the call and fails the add. The binding judge escalates from 12,000 to 24,000 tokens in the same way, one attempt earlier than the older remedy, and readers keep their 32,768-token cap without escalation (Appendix D.5.1).

<a id="appendix-l"></a>

## L. S20: two pipelines on STALE with and without its cues

S20, the pipeline de-cue study of §6.4, removes STALE’s typographic and clock-time cues jointly, as the de-cue test (Appendix B.3) did, for a RAG test (B1) and a mem0 test (B2) in the official STALE evaluation layout. It reuses the end-to-end successor study’s retrieval, inference rules, and mem0 adapter (Appendices D.5 and K.8) but is not its successor, because it estimates a different contrast.

### L.1. Protocol card

**Card L. S20 protocol card.** Condensed from the preregistration and its binding protocol amendment (registered as an annex). F1 is the typographic normalizer of Appendix K.5.

| Protocol element | Registered definition |
|----|----|
| Registration | Hash-locked with the pre-freeze decisions, preflight, sizing, and code on 2026-10-13 (07:29 UTC), before any study call, with this paper’s earlier results known |
| Population | 398 of STALE’s 400 scenarios, all used by earlier studies; nested hash-ordered subsets of 150 (B2) and 100 (no-history control) |
| RAW and DECUE | RAW: the official layout as distributed, byte-identical to STALE’s own rendering, with `YYYY-MM-DD HH:MM` stamps. DECUE: F1 on every turn and probe, and date-only stamps; all else identical |
| B1 (RAG) | BM25 and bge-small-en-v1.5 fused by RRF over the condition’s user turns, queried with its probe; the reader sees the top five sessions with both roles |
| B2 (mem0) | The mem0 2.2.1 library, memory decisions unmodified: one store per scenario and condition, one add per session with its user turns (option O1) and stamp, and up to 10 memories per probe, shown as `- [stamp] text` |
| Models | GLM-5.3-Flash at temperature 0 as extractor (mem0’s own prompts), reader (three reads per probe and condition), and judge (official STALE prompts); distinct request bodies avoid proxy copies (Appendix K.7) |
| Inference | Holm over B1 and B2 ($\alpha$ = .025, then .05); interval: the wider of a scenario bootstrap and a t interval at the Holm level; t-based TOST |
| Tiers (first that holds) | POSITIVE: adjusted lower bound \> 0 and estimate ≥ 5. SMALL: lower bound \> 0. EQUIVALENT: Holm-adjusted TOST p ≤ .05. REVERSED: upper bound \< 0. BELOW-SESOI: upper bound \< 5. INCONCLUSIVE: otherwise |
| Validity | INVALID: leakage, a failed render audit or replay, under 98% complete RAW–DECUE read pairs, or a failed gate. FAILED PIPELINE: pooled accuracy less than 10 points above the no-history control |
| Validation | 60 verdicts over four system × condition strata, rated blind by a fresh Claude Opus 5.5 instance (`claude-opus-5-5`) that saw only the packet; PASS: agreement ≥ .80 and κ ≥ .70 |

### L.2. Preflight, sizing, and pre-freeze decisions

**Table L2.1. Preflight and sizing.** Outcome-free measurements before the freeze. User-only ingestion (option O1) was open only if the smallest design, L4 (150 B2 scenarios, no full-context arm), exceeded 24 h.

| Item | Measurement or decision |
|----|----|
| Throughput | By the author’s decision (D-P1), one step at 50 requests in flight instead of five steps from 8 to 64: $T^*$ = 1,660.9 output tokens/s. The median per-request rate, 35.1 tokens/s, was below the 50 tokens/s that the gate needs to raise its limit, so about $T^*/50 \approx 33$ requests in flight were expected |
| Expected hours for L4, both roles / user turns | 32.0 / 21.0 (the both-role pilot passed) |
| Decision | L4 with O1; 28,552 planned calls; attempt cap 40,000 (factor 1.40 instead of 1.2, D-P10) |

Decision D-P2 keeps a rebuilt mem0 store with up to two failed adds (inherited: one); if failures are independent at a 0.75% per-add rate, this cuts the chance that the rule alone invalidates B2 from .74 to .003. By the author’s decision (D-P8), the preflight ran without repeating the registered review of its changed live-call code; a pre-freeze review replaced it (fixes D-P9 and D-P11).

### L.3. Execution, deviations, and exposure

The run was interrupted by a machine restart and resumed from saved state under the registered resume rules. It used 31,654 live GLM-5.3-Flash attempts (cap 40,000; 0 USD), with no budget stop, at a time-averaged gate limit of 32.0 requests in flight. All 300 stores, 10,164 reads, and 3,388 judge calls ended final; 11 judge calls exhausted their budgets, 19 stores were rebuilt once, one kept a failed add, and none was INVALID.

One post-lock software repair under the registered repair rule (A4), one of two allowed repair cycles, let the validation-packet checker’s study-label scan accept the gold-field names inside the required official explanation; packet bytes and sample, every other ban, and every registered text, rule, population, prompt, and frozen list were unchanged.

Before the registered gate ran, the author authorized a nonregistered provisional analysis with a different LLM rater; no number from it enters this paper. The registered rater received only the unchanged packet, and the registered closing steps then ran unchanged.

### L.4. Results

**Table L4.1. Completeness and pipeline check.** Planned pairs are scenarios × 3 probes × 3 reads; every missing read belongs to a judge call that exhausted its budget. Pooled accuracy is on the no-history control’s 100 scenarios, where the control scores 6.3%.

| Test | Planned pairs | Complete pairs (%) | Missing reads, RAW / DECUE | Pooled accuracy, % (margin) | State |
|----|---:|---:|----|----|----|
| B1 | 3,582 | 3,564 (99.50) | 15 / 6 | 60.4 (+54.1) | COMPLETE |
| B2 | 1,350 | 1,338 (99.11) | 3 / 9 | 48.2 (+41.9) | COMPLETE |

**Validation gate: PASS.** The judge agreed with the fresh Claude Opus 5.5 instance on 53 of 60 items (agreement .883, κ .769 = 10/13), none ambiguous. HH:MM strings appeared in none, four, one, and one of the 15 answers in the RAG RAW, RAG DECUE, mem0 RAW, and mem0 DECUE strata.

**Table L4.2. Primary family.** $\Delta$ = RAW − DECUE in points. B2, with the smaller one-sided p, was tested first at $\alpha$ = .025 and not rejected, so B1 kept that level (97.5% intervals).

| Test | $\Delta$ (exact) | Holm-adjusted interval | One-sided superiority p (Holm-adjusted) | Holm-adjusted TOST p (margin) | Tier |
|----|---:|----|---:|---:|----|
| B1 | +0.15 (275/1,791) | \[−1.29, +1.60\] | .406 (.406) | $1.2 \times 10^{-5}$ (±3) | EQUIVALENT |
| B2 | +4.30 (116/27) | \[−0.21, +8.89\] | .016 (.033) | .362 (±5) | INCONCLUSIVE |

B2’s Holm-adjusted superiority p is below .05, but the registered rule rejects only if the Holm-level interval’s lower bound, here −0.21 from the t interval, is above 0; its upper bound, 8.89, rules out BELOW-SESOI.

**Table L4.3. Registered secondary and descriptive rows.** None changes a tier. Brackets are 95% scenario-cluster intervals. No read exhausted its content attempts.

| Row | B1 (RAG) | B2 (mem0) |
|----|----|----|
| Accuracy, RAW / DECUE (%) | 59.9 \[57.1, 62.7\] / 59.7 \[56.8, 62.6\] | 49.7 \[44.6, 54.8\] / 45.4 \[40.1, 50.7\] |
| TOST p at ±3 (Holm-adjusted); exact McNemar test on read 1 | Primary (Table L4.2); 79 / 79 discordant, p = 1.000 | .742; 49 / 37 discordant, p = .235 |
| $\Delta$ on probes with all pairs complete; after dropping probes with a recovered unit | +0.20 \[−1.08, +1.50\]; +1.04 \[−0.43, +2.52\] (217 scenarios) | +4.38 \[+0.38, +8.39\]; −3.70 \[−19.64, +12.23\] (3 scenarios) |
| Diagnostics | Retrieval RAW − DECUE: all-gold@5 −0.17, any-gold@5 −0.08 points | 287.3 / 288.9 memories per store (RAW / DECUE), 6.3% of each with a typographic mark |

Exploratory strata without multiplicity correction (exposure group, probe type, scenario type, edit count, and RAW probe typography) all have 95% intervals that include 0; the subsets whose evidence pair differs in clock time (five and two scenarios) are below the 10-scenario minimum.

**Recomputations.** Two fresh-process recomputations from the saved outputs, by the study’s own registered replay code, reproduced the results file and tables byte for byte, and the post-run verification passed. A separate recomputation with separate code, from copies of the saved reads and judgments, reproduced both estimates, intervals, and tiers.

### L.5. Limits

- Reused scenarios, designed with this paper’s earlier results known; GLM-5.3-Flash judges its own answers, and one LLM adjudicator, not humans, validated the judge.
- Both cues are removed together, with the marks on 14.2% of distractor sessions; turn-count, length, and content cues remain, and clock time is also legitimate temporal content.
- B2 ingested user turns only, and its interval allows a benefit of up to about 9 points; missing pairs are not shown to be missing at random.
- The validation packet shows answers typographically normalized, so the gate cannot detect a judge response to marks that RAW answers may copy.
- No claim follows for other readers, systems, mem0 versions, benchmarks, or published scores.

# References

<div id="refs" class="references csl-bib-body hanging-indent">

<div id="ref-AnthropicOpus55Announcement" class="csl-entry">

Anthropic. 2026a. *Introducing Claude Opus 5.5*. Model announcement. <https://www.anthropic.com/claude-opus-5-5>.

</div>

<div id="ref-AnthropicSonnet55Announcement" class="csl-entry">

Anthropic. 2026b. *Introducing Claude Sonnet 5.5*. Model announcement. <https://www.anthropic.com/claude-sonnet-5-5>.

</div>

<div id="ref-Behnam2026RealCompanion" class="csl-entry">

Behnam, Arman, Sunglyoung Kim, Jiayi Yu, Eric Huang, and Liangwei Yang. 2026. *<span class="nocase">RealCompanion: Benchmarking Human Understanding from Reasoning over Longitudinal Real-World Conversations</span>*. <https://arxiv.org/abs/2610.01780v3>.

</div>

<div id="ref-Brown2024Monkeys" class="csl-entry">

Brown, Bradley, Jordan Juravsky, Ryan Ehrlich, et al. 2024. *<span class="nocase">Large Language Monkeys: Scaling Inference Compute with Repeated Sampling</span>*. <https://arxiv.org/abs/2407.21787>.

</div>

<div id="ref-Chao2026STALE" class="csl-entry">

Chao, Hanxiang, Yihan Bai, Rui Sheng, Tianle Li, and Yushi Sun. 2026. *STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?* <https://arxiv.org/abs/2605.06527v1>.

</div>

<div id="ref-Chen2021PassAtK" class="csl-entry">

Chen, Mark, Jerry Tworek, Heewoo Jun, et al. 2021. *<span class="nocase">Evaluating Large Language Models Trained on Code</span>*. <https://arxiv.org/abs/2107.03374>.

</div>

<div id="ref-Chen2026RoutingOracle" class="csl-entry">

Chen, Teng-Ruei. 2026. *<span class="nocase">What Does a Routing Oracle Measure Under Stochastic Decoding? Coupling, Scorer Choice, and Single-Commit Ceilings</span>*. <https://arxiv.org/abs/2607.03436v3>.

</div>

<div id="ref-Chhikara2025Mem0" class="csl-entry">

Chhikara, Prateek, Dev Khant, Saket Aryan, Taranjeet Singh, and Deshraj Yadav. 2025. “<span class="nocase">Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory</span>.” *ECAI 2025: 28th European Conference on Artificial Intelligence*, <span class="nocase">Frontiers in Artificial Intelligence and Applications</span>, vol. 413: 2993–3000. <https://doi.org/10.3233/FAIA251160>.

</div>

<div id="ref-Cormack2009RRF" class="csl-entry">

Cormack, Gordon V., Charles L. A. Clarke, and Stefan Büttcher. 2009. “<span class="nocase">Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods</span>.” *Proceedings of the 32nd International ACM SIGIR Conference on Research and Development in Information Retrieval*, SIGIR ’09, 758–59. <https://doi.org/10.1145/1571941.1572114>.

</div>

<div id="ref-DAmour2022Underspecification" class="csl-entry">

D’Amour, Alexander, Katherine Heller, Dan Moldovan, et al. 2022. “<span class="nocase">Underspecification Presents Challenges for Credibility in Modern Machine Learning</span>.” *Journal of Machine Learning Research* 23 (226): 1–61. <https://www.jmlr.org/papers/v23/20-1335.html>.

</div>

<div id="ref-Ding2023UltraChat" class="csl-entry">

Ding, Ning, Yulin Chen, Bokai Xu, et al. 2023. “<span class="nocase">Enhancing Chat Language Models by Scaling High-quality Instructional Conversations</span>.” *Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing*, 3029–51. <https://doi.org/10.18653/v1/2023.emnlp-main.183>.

</div>

<div id="ref-Gardner2020ContrastSets" class="csl-entry">

Gardner, Matt, Yoav Artzi, Victoria Basmov, et al. 2020. “<span class="nocase">Evaluating Models’ Local Decision Boundaries via Contrast Sets</span>.” *Findings of the Association for Computational Linguistics: EMNLP 2020* (Online), 1307–23. <https://doi.org/10.18653/v1/2020.findings-emnlp.117>.

</div>

<div id="ref-Ge2024PersonaHub" class="csl-entry">

Ge, Tao, Xin Chan, Xiaoyang Wang, Dian Yu, Haitao Mi, and Dong Yu. 2024. *<span class="nocase">Scaling Synthetic Data Creation with 1,000,000,000 Personas</span>*. <https://arxiv.org/abs/2406.20094>.

</div>

<div id="ref-Geirhos2020ShortcutLearning" class="csl-entry">

Geirhos, Robert, Jörn-Henrik Jacobsen, Claudio Michaelis, et al. 2020. “<span class="nocase">Shortcut Learning in Deep Neural Networks</span>.” *Nature Machine Intelligence* 2 (11): 665–73. <https://doi.org/10.1038/s42256-020-00257-z>.

</div>

<div id="ref-Google2026Gemini38FlashAPI" class="csl-entry">

Google. 2026. *<span class="nocase">Gemini API documentation: Gemini 3.8 Flash model page</span>*. <https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash>.

</div>

<div id="ref-Google2026Gemini35FlashLite" class="csl-entry">

Google DeepMind. 2026a. *<span class="nocase">Gemini 3.5 Flash-Lite model card</span>*. <https://deepmind.google/models/model-cards/gemini-3-5-flash-lite/>.

</div>

<div id="ref-Google2026Gemini38Flash" class="csl-entry">

Google DeepMind. 2026b. *<span class="nocase">Gemini 3.8 Flash model card</span>*. <https://deepmind.google/models/model-cards/gemini-3-8-flash/>.

</div>

<div id="ref-Gururangan2018AnnotationArtifacts" class="csl-entry">

Gururangan, Suchin, Swabha Swayamdipta, Omer Levy, Roy Schwartz, Samuel R. Bowman, and Noah A. Smith. 2018. “<span class="nocase">Annotation Artifacts in Natural Language Inference Data</span>.” *Proceedings of NAACL-HLT 2018* (New Orleans, Louisiana), 107–12. <https://doi.org/10.18653/v1/N18-2017>.

</div>

<div id="ref-Hu2026MemoryAgentBench" class="csl-entry">

Hu, Yuanzhe, Yu Wang, and Julian McAuley. 2026. “<span class="nocase">Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions</span>.” *International Conference on Learning Representations*. <https://arxiv.org/abs/2507.05257v4>.

</div>

<div id="ref-Huang2026RetentionSelection" class="csl-entry">

Huang, Juli. 2026. *<span class="nocase">What Should an Agent Remember? Disentangling Retention from Retrieval in Bounded-Memory Evaluation</span>*. <https://arxiv.org/abs/2610.00366v1>.

</div>

<div id="ref-KaushikLipton2018ReadingComprehension" class="csl-entry">

Kaushik, Divyansh, and Zachary C. Lipton. 2018. “<span class="nocase">How Much Reading Does Reading Comprehension Require? A Critical Investigation of Popular Benchmarks</span>.” *Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing* (Brussels, Belgium), 5010–15. <https://doi.org/10.18653/v1/D18-1546>.

</div>

<div id="ref-LeBras2020AFLite" class="csl-entry">

Le Bras, Ronan, Swabha Swayamdipta, Chandra Bhagavatula, et al. 2020. “<span class="nocase">Adversarial Filters of Dataset Biases</span>.” *Proceedings of the 37th International Conference on Machine Learning*, <span class="nocase">Proceedings of Machine Learning Research</span>, vol. 119: 1078–88. <https://proceedings.mlr.press/v119/bras20a.html>.

</div>

<div id="ref-Li2026LoCoMoPlus" class="csl-entry">

Li, Yifei, Weidong Guo, Lingling Zhang, et al. 2026. “<span class="nocase">Locomo-Plus: Beyond-Factual Cognitive Memory Evaluation Framework for LLM Agents</span>.” *Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, 25085–100. <https://doi.org/10.18653/v1/2026.acl-long.1150>.

</div>

<div id="ref-Maharana2024LoCoMo" class="csl-entry">

Maharana, Adyasha, Dong-Ho Lee, Sergey Tulyakov, Mohit Bansal, Francesco Barbieri, and Yuwei Fang. 2024. “<span class="nocase">Evaluating Very Long-Term Conversational Memory of LLM Agents</span>.” *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, 13851–70. <https://doi.org/10.18653/v1/2024.acl-long.747>.

</div>

<div id="ref-Mem0Library" class="csl-entry">

<span class="nocase">mem0ai</span>. 2026. *<span class="nocase">mem0: The Memory Layer for AI Agents (version 2.2.1)</span>*. GitHub repository. <https://github.com/mem0ai/mem0>.

</div>

<div id="ref-Meta2026MuseSpark13" class="csl-entry">

Meta. 2026. *Introducing Muse Spark 1.3*. <https://research.meta.ai/blog/introducing-muse-spark-1-3>.

</div>

<div id="ref-MilaniFard2016Churn" class="csl-entry">

Milani Fard, Mahdi, Quentin Cormier, Kevin Canini, and Maya Gupta. 2016. “<span class="nocase">Launch and Iterate: Reducing Prediction Churn</span>.” *Advances in Neural Information Processing Systems* 29. <https://proceedings.neurips.cc/paper/2016/hash/dc5c768b5dc76a084531934b34601977-Abstract.html>.

</div>

<div id="ref-OpenAIGPT61SolDocs" class="csl-entry">

OpenAI. 2026. *GPT-6.1 Sol*. Model documentation. <https://developers.openai.com/api/docs/models/gpt-6.1-sol>.

</div>

<div id="ref-Poliak2018HypothesisOnly" class="csl-entry">

Poliak, Adam, Jason Naradowsky, Aparajita Haldar, Rachel Rudinger, and Benjamin Van Durme. 2018. “<span class="nocase">Hypothesis Only Baselines in Natural Language Inference</span>.” *Proceedings of the Seventh Joint Conference on Lexical and Computational Semantics* (New Orleans, Louisiana), 180–91. <https://doi.org/10.18653/v1/S18-2023>.

</div>

<div id="ref-RobertsonZaragoza2009BM25" class="csl-entry">

Robertson, Stephen, and Hugo Zaragoza. 2009. “<span class="nocase">The Probabilistic Relevance Framework: BM25 and Beyond</span>.” *Foundations and Trends in Information Retrieval* 3 (4): 333–89. <https://doi.org/10.1561/1500000019>.

</div>

<div id="ref-SharmaLall2026Selection" class="csl-entry">

Sharma, Rishabh, and Rishika Lall. 2026. *<span class="nocase">When Does Selection Replace Extraction? A Pre-Registered Test of Agent Memory with a Typed Decision Model</span>*. <https://arxiv.org/abs/2609.34227v1>.

</div>

<div id="ref-Song2025Greedy" class="csl-entry">

Song, Yifan, Guoyin Wang, Sujian Li, and Bill Yuchen Lin. 2025. “<span class="nocase">The Good, The Bad, and The Greedy: Evaluation of LLMs Should Not Ignore Non-Determinism</span>.” *Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)*, 4195–206. <https://doi.org/10.18653/v1/2025.naacl-long.211>.

</div>

<div id="ref-Xiao2023CPack" class="csl-entry">

Xiao, Shitao, Zheng Liu, Peitian Zhang, Niklas Muennighoff, Defu Lian, and Jian-Yun Nie. 2024. “<span class="nocase">C-Pack: Packed Resources for General Chinese Embeddings</span>.” *Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval*, 641–49. <https://doi.org/10.1145/3626772.3657878>.

</div>

<div id="ref-Xu2026RoutePrism" class="csl-entry">

Xu, Dong, Zhangfan Yang, Jiantao Wu, et al. 2026. *<span class="nocase">RoutePrism: Tracing Construction Order Effects in Agent Memory</span>*. <https://arxiv.org/abs/2609.34160v1>.

</div>

<div id="ref-Yang2026ForgetEval" class="csl-entry">

Yang, Dongxu. 2026. *<span class="nocase">Control-Plane Placement Shapes Forgetting: An Architectural Study of Agent Memory Across Thirteen System Configurations</span>*. <https://arxiv.org/abs/2606.15903v2>.

</div>

<div id="ref-ZaiGLM53FlashDocs" class="csl-entry">

Z.AI. 2026. *GLM-5.3-Flash/FlashX*. Model documentation. <https://docs.z.ai/guides/vlm/glm-5.3-flash>.

</div>

<div id="ref-Zellers2018SWAG" class="csl-entry">

Zellers, Rowan, Yonatan Bisk, Roy Schwartz, and Yejin Choi. 2018. “<span class="nocase">SWAG: A Large-Scale Adversarial Dataset for Grounded Commonsense Inference</span>.” *Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing* (Brussels, Belgium), 93–104. <https://doi.org/10.18653/v1/D18-1009>.

</div>

</div>
