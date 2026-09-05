# Internal adversarial review ledger

**FINAL: four role reviews PASS; no reproducible fatal or major finding remains open against the delivered claim set.**

These are four distinct computational reviewer roles within one language-model-assisted workflow. They are not external human peer review, independent experimental observations or a blinded randomized evaluation. Initial critiques are preserved; final reports identify the exact texts examined. The integrator did not require a preferred scientific outcome from reviewers.

## Reviews and evidence

| Role | Initial evidence | Final evidence |
|---|---|---|
| Hostile statistician | `reviews/statistics/STATISTICAL_REVIEW.md` | `FINAL_MANUSCRIPT_REVIEW.md`, `FINAL_NUMERICAL_CHECK.json` in the same folder |
| Complex systems / artificial life | `reviews/complex_systems/INITIAL_REVIEW.md` | `FINAL_MANUSCRIPT_REVIEW.md`, `FINAL_SOURCE_CONSTRUCT_CHECK.json` in the same folder |
| Clean-copy reproducibility | `reviews/reproducibility/CLEAN_REPRO_REVIEW.md` | Final addendum and timestamped `CLEAN_REPRO_CHECK_*.json` in the same folder |
| Editorial novelty / overclaim | `reviews/editorial/INITIAL_EDITORIAL_REVIEW.md` | `FINAL_EDITORIAL_REVIEW.md` in the same folder |

## Individually addressed scientific findings

| IDs | Issue | Actual correction / disposition |
|---|---|---|
| ST-01, CS01, E01 | Gate failure was overread as absent ownership or a positive dissociation | New title explicitly says Testing; abstract/results/discussion say the criterion is unmet, preserve positive comparator estimates and reject absence/equivalence. Archived outcome strings remain historical labels. |
| ST-02, E05 | Independent-fold confidence interpretation | Bands labelled descriptive throughout; overlapping training dependence and unestablished coverage explicit; Bengio/Grandvalet primary reference added. No replacement calibrated interval invented. |
| ST-03, CS11 | Same seed stream and unproven permutation exchangeability | Initialization/amplitude RNG reuse stated; permutation remains a diagnostic, not exact randomized evidence or identified causal mediation of history. Quantitative impact is unknown. |
| ST-04, CS09 | Conditional population and post-intervention validity definition | All50 worlds accounted for;17 initial exclusions,11 splits,1 lost; no extra exclusion among21 reaching deep. Three targets remain clustered per world. |
| ST-05, CS05 | Designed uptake readout and branch-specific masks | Copying/readout equations and limitations placed in main methods; masks are explicitly fixed only within each branch after relaxation. |
| ST-06, CS03 | Finite unequal access representations; E/Gm body overlap | Exact feature counts and memory-only masking described; no exclusively external-observer claim or universal uniqueness metric. |
| ST-07 | Estimated intact effect treated as fixed in the frozen collapse gate | Frozen arithmetic preserved and a separate post hoc paired half-own-minus-residual contrast added, with world-level interval. |
| ST-08 | Same-data calculation conflated with experiments | All reconstruction/review sections distinguish implementations on identical observations from new-seed replication and external validation. |
| CS02 | Wrong FitzHugh-Nagumo label / model parameters | Actual symmetric mutual-inhibition equations, split-step sequence and beta0.10 override documented;29 values generated from source. |
| CS04, FM-01, FR01 | Material denominator and new-material interpretation | Abstract and methods define current own-marked mass/current total target mass; unmarked remainder is not called newly synthesized; residual own material remains positive. |
| CS05 | Passive copy and “templating” overstated as maintenance mechanism | Growth/removal identities and exact Laplacian/4 reduction supplied. Ongoing writing, direct readout and lack of unique maintenance identification explicit. |
| CS06, CS07, CS08 | Historical CCRA competing-risk/total-effect/composite overclaims | Historical sources preserved. Contemporary Supplement/provenance reject universal hazard nonidentifiability and universal invalidity of total tracking duration; composite remains retrospective with30/41 duration tiebreaks. Not pooled into B. |
| CS10 | Internal chronology obscured novelty and close antecedents | Main article organized by scientific questions; recovery history moved to provenance/Supplement; primary turnover-memory and information-partition references added. |
| FM-02 | Claimed saved coefficients absent | Text now accurately promises predictions, losses and settings; no fabricated coefficient artifact. |
| FM-03 | Missing positive-L-skill condition | Both definitions now include the explicit positive lower skill-band constituent of G_LOCAL_EXCLUSION. |
| FR02 | Discrete alive masking / numerical floor incompletely specified | Supplement explicitly recomputes concentrations with max(rho,epsilon) and zeros u/v outside alive before the Laplacian. |
| FR03 | Apparent tracking continuity during history writing | Supplement states nearest-component association after writing and start of bijective tracking at material marking. |
| E02 | Absolute effect lacked functional scale | Mean intact uptake and precisely defined descriptive mean of target-then-world relative reductions added; independently checked. Absolute contrast stays primary. |
| E03 | Full readout ablation omitted | Supplement/table disclose all63 own contrasts exactly zero, explicitly expected by construction and diagnostic. |
| E04 | Protocol difficult to reconstruct visually | Source-faithful workflow schematic added, with marking, active writing during turnover and separate erasure/decoding branches; no invented spatial snapshot. |

## Reproduction and rendering findings

| ID | Problem found | Corrective action and final test |
|---|---|---|
| CRR-01 | Vera font rendered Greek as boxes | Included four DejaVu font faces, their license and byte hashes; builder asserts used-glyph coverage; independent cmap/PDF-font check and all-page inspection. |
| CRR-02 | Narrow Construction column in S5.1 | Dedicated8/57/12/23-percent widths; table visually rechecked. |
| CRR-03 | Figure1 title near neighbouring ylabel | Shorter panel titles; figure visually rechecked. |
| CRR-04 | Outputs lagged edited sources | Complete master rebuild and fresh relocated-copy comparison. A second-round metadata-only PDF mismatch exposed ReportLab's template invariant override; invariant=1 now set on SimpleDocTemplate. |
| CRR-05 | Initial reproduction manifest omitted reviewer outputs | Final `RELEASE_MANIFEST.json` inventories reviewer scripts, reports and JSON along with scientific/document outputs; clean reviewer hash inventories retained. |

The integrator also repaired explicit UTF-8/LF serialization for newly authored output JSON/CSV to keep Git and filesystem bytes consistent. Historical `data/` and `source_model/` bytes are protected with scoped `.gitattributes` and were not normalized. An early Git whitespace check failed after CRLF output generation; the diagnostic was noisy and the PowerShell sequence still committed the already authorized audit content. A follow-up normalization commit preserves that history rather than rewriting it. This was a serialization/command-sequencing fault, not a numerical correction.

## September findings and the integrator's own erratum

All28 findings are preserved and adjudicated individually in repository `audit/edl-flagship-01/september4_adjudication/FINDINGS_28_MATRIX.csv`. Four initial fatal defects have observable corrections; F5 was addressed by an executed reanalysis but not an exhaustive proof that all further experiments lack value. F8/F9/F24/F28 remain partial in the historical C manuscript. Their missing original evidence or overstrong claims are not silently declared repaired and are not adopted by the delivered B article. See `DATA_PROVENANCE.md` for their exact scope.

The separate auditor found and the integrator accepted a new error in the preceding Astra cost calculation:12 triggered seeds did not execute branches. The corrected two-arm accounting yields38 pairs at the512 crossing (index789), not36 at760. The code, regenerated audit JSON, active matrix and report erratum changed; the incorrect original commit remains recoverable. This correction does not turn the41-pair OMLDCT acquisition into compliance with its frozen ceiling.

CRR-06 (PDF metadata determinism), separately numbered in the final clean review, is also closed: the final relocated build reproduces both PDF byte hashes. The final check inventories25 compared outputs; all25 match.

## Scientific limits retained after closure

Closed findings mean the reported calculations and claims now match their scope. They do not mean the original design acquires calibrated decoder coverage, independently randomized histories, fully replaced material, a common cross-branch mask, a unique maintenance mechanism or external validity. Those are explicit limits. The no-flagship judgment remains an editorial assessment of limited mechanistic novelty and incomplete local-access inference, not a new statistical terminal.
