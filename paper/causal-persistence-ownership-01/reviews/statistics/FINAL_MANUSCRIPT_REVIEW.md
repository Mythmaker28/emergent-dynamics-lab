# Final manuscript review — independent statistical reviewer

Reviewer: statistical subagent of Astra; 2026-09-05. This is one distinct internal AI review. It is not external human peer review or a new-data replication.

**Final status: PASS — STATISTICALLY DEFENSIBLE FOR AUTHOR AND EXTERNAL EXPERT REVIEW WITH THE DISCLOSED LIMITS.** All three factual wording corrections are verified in the resolved texts, and the added scale/full-ablation results have been independently checked from raw outputs. No unresolved statistical finding remains within this review's scope. This judgment does not convert the historical fold bands into calibrated confidence intervals or establish absent ownership.

**Status at first pass: PASS SUBJECT TO THREE SMALL FACTUAL TEXT CORRECTIONS.** No new numerical or inferential fatal was found in the new article. The major statistical findings from the initial review are addressed by narrowing the claim and distinguishing frozen procedural bands from validated inferential coverage. The remaining wording findings below do not require new data or a new simulation. A resolution addendum will record the final disposition after their correction is verified.

## Evidence reviewed

Read the complete new `MANUSCRIPT.md` and `SUPPLEMENT.md`, `scripts/analyze.py`, the generated numeric substitutions, `SUMMARY.json`, and all four primary CSV tables. Placeholder substitution is an intended build step, not an unresolved scientific defect. I did not infer a favorable judgment from the earlier claim ledger.

`verify_final_tables.py` independently loads article-local raw inputs, checks all 222 manifest entries, and reconstructs seven-scope predictions and losses using the separate prediction-matrix implementation. It also compares each per-world causal contrast directly with the recorded intervention outputs, checks all 50 eligibility rows against raw fields, and verifies every reported one-sided sign probability. It imports no simulator or project package. Exact hashes of the versions tested are recorded in `FINAL_NUMERICAL_CHECK.json`.

Reproduce from the article directory:

```console
python reviews/statistics/verify_final_tables.py
```

Verified 50 cohort rows, 21 world rows, 63 target prediction rows and seven scopes including P and Gf. Maximum absolute differences: predictions 6.94e-17; fold losses 7.55e-15; per-world causal contrasts 0; reported summary values 9.99e-16. No new worlds were generated. The new article's one-sided sign value for 21/21 positive own effects is 4.76837e-7; the initial review's two-sided value was 9.53674e-7. Both are correct for their stated alternatives; this is not a numerical conflict.

## Individually verified dispositions

| ID | Finding | Final-text verification | Disposition |
|---|---|---|---|
| ST-01 | Failed local-exclusion gate was overread as absence of ownership | Abstract, Results 3.3 and Discussion explicitly preserve compatibility with an L advantage and reject an absence/equivalence conclusion; the archived Outcome B wording is distinguished from the paper's interpretation | RESOLVED |
| ST-02 | Overlapping training sets invalidate unqualified independent-fold coverage | Methods 2.4, Table 1, Figure 3 and Supplement S5.3 consistently label descriptive fold bands and state unestablished generalization coverage; deletion/jackknife results are diagnostic only | RESOLVED AS A CLAIM LIMIT; historical design not retroactively repaired |
| ST-03 | Permutation arithmetic vs unsupported randomization interpretation | Methods 2.2/2.4 and Supplement S2.4/S5.3 disclose same-seed stream reuse, conditional exchangeability assumptions and absence of an exact randomized history-causality claim; 1/1001 is reported at its Monte Carlo resolution | RESOLVED AS A CLAIM LIMIT |
| ST-04 | 21 valid worlds are a selected subset, not the 50-world population effect | Results 3.1 and Supplement S3.3 give 17 initially ineligible, 11 SPLIT, 1 LOST, 21 deep/valid; no additional deep assay exclusion is asserted; three targets remain clustered within each world | RESOLVED |
| ST-05 | Fixed masks are branch-specific; uptake is directly engineered | Methods 2.1/2.3, Results 3.2 and Supplement S4 explicitly state post-relaxation mask selection within each branch, designed uptake coupling and limitations of geometric control | RESOLVED |
| ST-06 | Scope comparisons depend on representations and learning rule | Methods 2.4, Figure 3 and Supplement S5 identify unequal dimensions, retained target-body fields in E/Gm, and absence of a universal or information-theoretic ownership test | RESOLVED |
| ST-07 | Residual attenuation gate treats an estimated comparator as fixed | Frozen rule is preserved; paired 0.5×own−residual added with world-level uncertainty and an explicit post hoc label; nonzero residual acknowledged | RESOLVED |
| ST-08 | Same-data reconstruction must not be sold as independent experiments | Methods 2.5, Results 3.4, author-assistance statement and Supplement distinguish independent calculations, internal AI review and no new simulations/external validation | RESOLVED |

## Three new factual wording findings

**FM-01 — Abstract denominator wording (minor but scientifically material).** The first text reviewed says “each of three targets retained at most one quarter of the material marked in its own initial mask.” This can read as the retained fraction of the initial marked mass. The stored quantity actually divides current own-marked mass by current total target mass. The Methods correctly define it, so only the abstract sentence needs correction. Suggested wording: “material bearing each target's own initial-mask label contributed at most one quarter of its current mass.” Do not call the complementary fraction necessarily newly synthesized material; the new text correctly rejects that interpretation elsewhere.

**FM-02 — Unsupported claim that all fitted coefficients are retained (minor artifact-description error).** Methods 2.5 says supplementary tables retain “all coefficients.” `scripts/analyze.py` calculates fold coefficients transiently but saves predictions, losses, world contrasts and cohort accounting, not the fold coefficient arrays. The text can say “all reported parameter settings, predictions, excluded-world reasons and sensitivity settings” or the coefficients can actually be saved. Predictions/losses are sufficient for the current numerical claims, so this is not a reproducibility blocker once wording matches the package.

**FM-03 — One constituent of the historical local-exclusion rule is omitted (minor procedural-description error).** Methods 2.4 and Supplement S5.3 describe the four comparator lower bounds, but the executable `G_LOCAL_EXCLUSION` also requires a positive lower band for L's own skill (`L_information_lower_gt_zero`). Add that requirement to the two textual definitions. It passed in this dataset, so the omission does not change the reported failed conjunction. The within-world permutation gate is a different condition and does not stand in for this explicit test.

## Residual scientific limitations, not hidden failures

The conditional sample size remains 21 worlds. Finite deterministic seed runs are interpreted as model-world observations under a sampling assumption; the Supplement now states that assumption for world t intervals. Decoder coverage and exact randomization are not established, and the text no longer pretends otherwise. Erasure identifies a response to the manipulated field within this architecture; it does not isolate historical writing as the unique source of that effect. Source algebra makes passive copying plausible, but does not separately identify it from ongoing writing or other field dynamics. No equivalence or absent-ownership claim can be restored by the post hoc sensitivities.

Within those boundaries the revised article is statistically defensible for author and outside expert review. The judgment does not certify novelty, physical realism, journal acceptance or a universal criterion of individuality. Those are distinct questions.

## Verified final resolution — 2026-09-05, 03:22 Europe/Paris

FM-01 is **RESOLVED**: the resolved abstract now says that material carrying each target's own initial-mask label contributes at most one quarter of its **current mass**. FM-02 is **RESOLVED**: Methods 2.5 promises predictions, losses, excluded-world reasons and reported sensitivity settings, without claiming absent coefficient arrays. FM-03 is **RESOLVED**: both Methods 2.4 and Supplement S5.3 now include the positive lower band for L's own skill as well as the four comparator advantages.

The revised Results 3.2 also explicitly states that decoding and erasure together do not identify mediation of the assigned history: erasure removes non-history-specific field components as well. This appropriately closes a potential inferential shortcut. World t assumptions, conditional feasibility, same-seed reuse, branch-specific masks and post hoc labels remain visible in the resolved text.

I extended the independent table check to the newly reported scale and full-ablation control. Mean intact uptake is **3.0080940789**. The mean of target fractional own reductions, averaged first within world and then across worlds, is **0.0556669460**, correctly reported as **5.57%**. This is not the ratio of grand mean contrasts. All **63 target-level own-erasure contrasts under full readout ablation are exactly zero**. The Supplement describes that as an expected diagnostic and does not mistake it for absent history dependence or a maintenance mechanism. The zero-vector sign probability is a noninformative convention, not a new significance claim. Updated checks passed; no original data or generating code changed.

The 25-row `CLAIM_EVIDENCE_MATRIX.csv` is consistent with the resolved statistical claims. In particular, conditional causal/predictive/arithmetical/procedural status labels for C01–C17 do not upgrade limited evidence to absent ownership, randomized history causality or new-data replication. C21/C22 distinguish documentary order and same-data reconstruction; C24 remains explicitly NOT_ESTABLISHED. Claims about model algebra and novelty remain within the separately documented source/literature reviews; this statistical review does not certify novelty by numerical agreement.

Resolved-text hashes (SHA-256):

| Artifact | SHA-256 |
|---|---|
| MANUSCRIPT_RESOLVED.md | `1cafd6abbe715f1142b7fb0ce9adcde3b864da9cde014f75947349434d7ade08` |
| SUPPLEMENT_RESOLVED.md | `3e314d8b901ab332d3a3194f029b59226398dfd24857e498899c7658232a47ce` |
| scripts/analyze.py | `75d89b26783ec211cd9e7d57c3f91ef4482b8a105884013f50db433501331c1a` |
| results/SUMMARY.json | `c7610232acf9f441d0f6b4d8a037ba8fc478a26f7a3bdf075b1d124e3c1a0267` |
| CLAIM_EVIDENCE_MATRIX.csv | `5b019c30c0f20dede5a6fcae31ba7bfb5707c9f169648cd3b3556d7b6ee10461` |

The machine-readable check also binds the editable unresolved-text sources. PDF rendering quality is the separate document-review responsibility; this PASS concerns the reviewed resolved scientific text and numerical artifacts. No further confirmation or new experiment is required for this review disposition.
