# Final independent editorial review

Date: 5 September 2026. Reviewer role: editorial novelty, scientific interest and claim calibration. Final status: **PASS_FOR_AUTHOR_REVIEW — E01–E05 CLOSED**. No reproducible fatal or major editorial finding remains open in the reviewed claim set. This disposition concerns the bounded article, not external peer review, journal acceptance, or the validation of a flagship claim.

## Reviewed versions and checks

| Artifact | SHA-256 |
|---|---|
| MANUSCRIPT.md | `fd69819c4766a4dd24f86cdb53c3ea797e6f81092efe270c6c4bfc457fb2ec71` |
| SUPPLEMENT.md | `2f31e6a92dea2b999ef7626ec5ee7bfef0e6d984b5047a04e888cb438d4c5778` |
| MANUSCRIPT_RESOLVED.md | `1cafd6abbe715f1142b7fb0ce9adcde3b864da9cde014f75947349434d7ade08` |
| SUPPLEMENT_RESOLVED.md | `3e314d8b901ab332d3a3194f029b59226398dfd24857e498899c7658232a47ce` |
| CLAIM_EVIDENCE_MATRIX.csv | `5b019c30c0f20dede5a6fcae31ba7bfb5707c9f169648cd3b3556d7b6ee10461` |
| results/SUMMARY.json | `c7610232acf9f441d0f6b4d8a037ba8fc478a26f7a3bdf075b1d124e3c1a0267` |

I re-read the resolved manuscript, the relevant revised Supplement sections and all 25 claim-matrix rows. All listed evidence paths exist. Both PDFs have resolved numeric values and references numbered 1–8, including the added primary cross-validation reference. The manuscript has eight pages and the Supplement nine. I inspected the manuscript's rendered first page and the actual protocol schematic visually: the title, abstract and figure text are readable, with no observed clipping or invented spatial snapshot. The separate clean reviewer owns the complete page-by-page release inspection; this reviewer does not claim to have visually inspected every page.

`FINAL_EDITORIAL_CHECK.json` records the PDF byte hashes and extracted-text hashes as well as the source hashes above. The extracted text hashes are `cec711ad66cf233dc3c439723d480117871a929a45f0e27327e90d7c8e61d647` for the manuscript and `830ab419678b78fced456777d5e56655e8032bd8607916fa52a9db6e463c5d4f` for the Supplement. This separates the reviewed scientific text from any later deterministic metadata-only PDF rebuild.

## Finding dispositions

| Finding | Disposition | Evidence for closure |
|---|---|---|
| E01, major, headline/claim identity | CLOSED — corrected | The title now begins “Testing causal memory expression and local predictive advantage”. The abstract explicitly calls the work a computational assay case study and states that the result is causal expression of the manipulated field, conditional on admissibility. Results 3.2 explicitly rejects the inference that erasure plus decoding identifies mediation of the assigned history; erasure also removes non-history-specific components. The discussion limits mechanism novelty and universal construct interpretation. |
| E02, major, missing uptake scale | CLOSED — corrected | Results 3.2 reports intact uptake 3.0081 and mean fractional reduction 5.57%, calculated for each target and averaged within then across worlds; world means range 3.92–6.97%. This matches the independent 0.05566694599240233 calculation. Claim C10 explicitly labels the summary descriptive and distinguishes it from the ratio of means. The absolute effect remains primary. |
| E03, minor, full ablation diagnostic | CLOSED — corrected | Supplement S4 and its control table report exactly zero own-erasure contrast for all 63 retained targets under full readout ablation. The text labels it expected when memory has no physical readout and refuses to interpret it as history-specific persistence or an independent maintenance mechanism. Claim C09 preserves that qualification. |
| E04, minor, workflow schematic | CLOSED — corrected | Figure S2 shows initialization/selection, two nutrient phases and settling, material marking, turnover monitoring with writing active, then separate decoder and causal branches. Its caption identifies it as a schematic. The figure also preserves the 50-world accounting and joint-validity restriction. No spatial observations were invented. |
| E05, minor, primary methods citation | CLOSED — corrected | Reference [8] is Bengio and Grandvalet (2004), JMLR 5, 1089–1105, with the publisher link. Methods 2.4 cites it for the general cross-validation uncertainty problem and explicitly says the exact magnitude or direction of miscoverage in this dataset is unknown. |

No finding was closed merely because the desired final outcome required closure. Each closure above follows a specific observable change. The original first-round review remains unchanged.

## Final scientific and editorial judgment

The article is a defensible, focused computational assay case study. It reports a nonzero, conditional erasure effect in a designed physical readout after a decline in own-marked material; it reports a predictive association and the procedural failure of a stronger conjunction while explaining why those results do not identify local ownership absence or history-specific causal maintenance. Its source-level copying identities and explicit handling of inference limits provide a useful interpretive lesson for similar model studies.

The correction process improves presentation and evidence accounting, not the intrinsic scope of the discovery. Mechanistic novelty remains limited by designed copying/readout and continued writing; access uncertainty remains uncalibrated for the intended generalization claim. My indicative scientific-strength judgment therefore remains approximately **13/20**, with no claim that this subjective score measures acceptance probability. A flagship claim is not supported. A specialist submission can be considered on the bounded contribution without starting another experiment simply to prolong the project.

The scope-based journal advice in the first review remains applicable: Artificial Life is the closest thematic fit, BioSystems is plausible if the conceptual biological connection is made explicit, and Theory in Biosciences would impose a stronger conceptual-novelty hurdle. These are editorial inferences from official publisher scopes, not invitations or assurances.

## Scope of completion

Editorial review is complete. No source-model change, physical trajectory rerun, new simulated world, commit or push was performed by this reviewer. Final clean reproducibility and complete PDF visual verification remain the responsibility of their assigned reviewer and the release owner. No further editorial action is required unless the scientific text, numerical values or claim boundaries change.
