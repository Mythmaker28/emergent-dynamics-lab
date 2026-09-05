# Independent editorial review, first round

Reviewer role: editorial novelty, scientific interest and claim calibration. Date: 5 September 2026. This is an internal language-model-assisted review, not external peer review. The reviewer read the manuscript and supplement before examining other reviewers' conclusions; the bibliography metadata was consulted for positioning, not as an authority for the present verdict. No target conclusion or required score was adopted.

## Material reviewed

- `MANUSCRIPT.md`, SHA-256 `30cf7d657caa949c51b05b17e5c18a02d6d31811957e9bfdc158568c83310a4b`.
- `SUPPLEMENT.md`, SHA-256 `2023a44e9fc8debd24ace00f18c2e24c03f90c6cc021ed43c972baacf64962a2`.
- `results/SUMMARY.json`, SHA-256 `6bf0b4a9e6f3ab140bed88f810426e83ce4cab8d3536220edf48787a9a1dba30`.
- Primary analysis source, cohort table, source-model description and raw deep-assay output for all 21 valid worlds. `editorial_scale_check.py` independently supplies descriptive effect-size context from the raw outputs; it imports no engine.
- Publisher scope pages and a targeted primary statistical-methods reference, linked below. This was not an exhaustive priority review. Numeric substitutions were understood to be intentional generated values, not missing results.

The release claim matrix and final PDFs were not yet available at the first read. Their final consistency remains a second-round check, not an allegation that the scientific inputs are missing.

## Editorial assessment

The article has a defensible narrow contribution: a prospectively specified intervention/access assay applied to a fully accounted conditional population, accompanied by unusually explicit limits on what its measurements establish. Its strongest numerical finding is a positive effect of erasing a designed memory field at a low own-marked-material fraction. The local-superiority conjunction is procedurally unmet; this is not a calibrated demonstration that the local representation lacks an advantage. The manuscript generally respects that distinction.

Mechanistic novelty is modest. Passive copying preserves an intensive concentration algebraically, the uptake channel explicitly reads that concentration, and writing remains active. The analysis does not show that a particular historical memory content survives independently of those operations. Nor does the failed, uncalibrated predictive gate establish a separation theorem or an empirical absence of ownership. A complete data chain is valuable scientific practice, but reproducibility by itself is not a new mechanism or a sufficient reason to advertise a flagship result.

I would consider a focused computational case study or methodological research article for a specialist readership after the two major presentation issues below are resolved. I would not present it as discovery of autonomous memory maintenance, a general test of individuality, or a conclusive negative result about ownership. Limited novelty remains a judgment about venue ambition; it is not repaired by appending a different experiment or by replacing honest uncertainty with a sharper claim.

## Findings

### E01 — Major: headline and article identity need to name the test, not imply two established phenomena

**Location:** manuscript title, abstract ending, and introduction's contribution paragraph.

**Evidence:** The title is “Causal persistence and local predictive advantage after material turnover in a spatial model.” The full local-advantage requirement was not established. In addition, causal erasure at the deep snapshot does not identify preservation of the same historical content across the intervening period, because writing remains active and assigned-history causality is not established. The body explains these limitations well, but a title is independently read and indexed. Its conjunction can be mistaken for a claim that both named phenomena have been demonstrated. The broad opening and “Research article” label also obscure that the publishable contribution is a worked assay case with limits on identification.

**Minimal correction:** Put testing/assay explicitly in the title, or name the directly measured erasure effect. For example, “Testing causal erasure effects and local predictive access after a decline in marked material.” In the abstract and contribution sentence, say that this is a computational assay case study rather than a validated general assay of memory ownership. Do not claim that the failed gate demonstrates the physical absence of a local advantage. No new simulation is required to close this finding.

**Closure criterion:** The title, abstract and contribution statement can stand alone without implying identified temporal retention of historical content, a positive full superiority result, or universal construct validation.

### E02 — Major: the primary causal effect lacks an interpretable uptake scale

**Location:** abstract and Results 3.2; primary causal table.

**Evidence:** A reduction of 0.164845 integrated units is reported with uncertainty, but the paper does not supply intact uptake or a defined relative reduction. A reader cannot tell whether this is a numerically tiny perturbation or a material fraction of the measured function. The raw intact outcomes are available. Independent extraction gives mean intact uptake 3.0080940788548407 and mean own-erasure contrast 0.16484499065801111. Their ratio is 0.05480047709171596, or 5.48005%. The mean of within-target ratios, averaged within world and then across worlds, is instead 0.05566694599240233. These are different summaries and must not be interchanged.

**Minimal correction:** Add intact uptake and a clearly labelled descriptive ratio of means (approximately 5.48%) near the primary effect, preferably generated by the main script. Preserve the original absolute effect as the primary estimand. No new significance test, gate, or unverified biological functional threshold is needed.

**Closure criterion:** The paper identifies the denominator and arithmetic of the relative description, labels it descriptive, and agrees with released raw-data calculations.

### E03 — Minor: report the already recorded full readout ablation diagnostic

**Location:** Methods 2.3 and Supplement S4.

**Evidence:** The text distinguishes uptake-channel ablation from a separately recorded full ablation, but never states the latter's result. In the 63 retained targets, the recorded tracked own-erasure contrasts under full readout ablation are exactly zero in floating-point arithmetic; maximum absolute contrast is 0.0 in `EDITORIAL_SCALE_CHECK.json`. This is an informative implementation sanity check and reinforces the designed-channel interpretation. Its omission is not proof of selective reporting, but supplying it makes the control battery more transparent.

**Minimal correction:** Add one supplementary sentence or a diagnostic table row, explicitly outside the frozen primary causal gate. Explain that zero effect when both physical readouts are disabled is expected by construction and does not validate history-specific persistence.

### E04 — Minor: the central workflow is hard to reconstruct visually

**Location:** Methods 2.2–2.4 and Figures 1–3.

**Evidence:** Readers must assemble several distinct stages from prose: target selection, two history phases, settling and marking, turnover monitoring, branch-specific probe, and separate feature prediction. Figure 1 accounts for populations but does not show this design. With no representative spatial state shown, the geometry and timing are especially abstract.

**Minimal correction:** A compact schematic of stages and timing would improve reuse. It should mark the point at which tracers are initialized, the continuing writing during turnover, and the split between erasure outputs and decoder features. A faithful schematic is sufficient; do not invent a representative world image or imply that unreleased spatial snapshots exist. This is an editorial improvement that can be declined with a concise rationale if space is constrained.

### E05 — Minor: give a primary methods citation for the cross-validation uncertainty caveat

**Location:** Methods 2.4 or Supplement S5.3.

**Evidence:** The manuscript correctly warns about dependence among losses from overlapping training folds, but this central methodological boundary currently lacks a cited source. It is a well-established issue rather than a novel defect discovered only in this dataset. Bengio and Grandvalet's primary analysis provides a suitable general reference: *No Unbiased Estimator of the Variance of K-Fold Cross-Validation*, JMLR 5, 1089–1105 (2004), [publisher article](https://www.jmlr.org/papers/v5/grandvalet04a.html). Their general theorem should not be paraphrased as a proof of the exact magnitude or direction of miscoverage in this particular 21-world analysis.

**Minimal correction:** Add the citation at the existing caveat with its scope kept general. No new uncertainty method is required to close this bibliographic finding.

## Strengths and non-findings

The text does not equate 63 targets with 63 independent replicates. All 50 worlds are accounted for, and assay conditioning is explicit. It does not call the unmarked remainder newly synthesized material. It accurately distinguishes an in-branch fixed mask from identical masks across interventions. It does not call a permutation diagnostic exact randomized evidence, does not call overlapping-fold bands calibrated confidence intervals, and does not infer equivalence or absence from inclusion of zero. Designed copying/readout and ongoing writing are disclosed prominently. Same-data recomputation, source documentation and new physical execution are distinguished. These are substantive reasons not to issue an additional fatal or major finding on those points.

I found no fatal scientific contradiction in the reviewed claim set. The two major findings above concern whether readers can accurately understand the paper's principal result and scope. The absence of a fatal contradiction does not establish high novelty or predict journal acceptance.

## Calibrated journal advice

These are scope-based possibilities, not estimates of acceptance probability, invitations, or confirmation that a particular article type will be accepted.

1. **Artificial Life:** strongest thematic fit for a computational study of life-like organization and the interpretation of such systems. The specific hurdle is a reusable conceptual or methodological contribution beyond careful reanalysis of one custom model. Position as a worked assay case, with the passive-copying reference and construct boundaries central. [Official submission scope](https://direct.mit.edu/artl/pages/submission-guidelines), publisher search extract inspected; direct page retrieval returned 403.
2. **BioSystems:** plausible for operational information/organization questions linked to a computational model. The biological-conceptual connection must be explicit, without claiming a biological mechanism. [Publisher scope](https://shop.elsevier.com/journals/biosystems/0303-2647). Its separately advertised 2026 information special issue is invitation-only; no eligibility for that issue is implied.
3. **Theory in Biosciences:** conceptually adjacent but a more demanding fit here. Its official scope emphasizes new concepts and strong conceptual background and warns that routine model analysis without additional conceptual value is insufficient. The paper would need to persuade an editor that separating intervention evidence from an operational access requirement offers more than a dataset-specific caution. [Official aims and scope](https://link.springer.com/journal/12064/aims-and-scope).

A flagship venue claim is not supported by this evidence. My qualitative scientific-strength assessment is approximately **13/20 before final release checks**: useful and careful specialized case study, limited mechanism/construct novelty and imprecise access inference. This is an editorial judgment, not a quantitative score derived from a validated instrument. Addressing E01–E05 improves clarity and completeness; it does not automatically transform the underlying discovery into a broader one.

## Next review

Re-read resolved manuscript, supplement, claim matrix and final PDF text after corrections. Close findings by reference to actual changes or explicit factual dispositions. Retain this first review unchanged; record final dispositions in a separate review file.
