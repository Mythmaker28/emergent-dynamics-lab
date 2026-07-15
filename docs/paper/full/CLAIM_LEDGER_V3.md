# Claim ledger V3 -- claim / evidence / uncertainty / authorized wording

Evidence classes: **OBSERVED** (deterministic, reproducible in-run); **ESTABLISHED** (statistically, with a
CI supporting the direction and threshold); **NOT CERTIFIED** (a pre-specified gate was not met with a CI
that excludes the null/threshold -- i.e. underpowered or inconclusive, *not* a demonstrated absence);
**INFERRED** (supported but with wide/overlapping CIs); **SPECULATIVE** (hypothesis, no decisive test).

No claim in this paper is in a "FALSIFIED" class: the one candidate for falsification (h2 deep-turnover
retention) is **NOT CERTIFIED**, because its CI spans the threshold.

| # | Claim | Evidence | Key statistic (95% CI) | Class | Authorized wording |
|---|-------|----------|------------------------|-------|--------------------|
| 1 | The engineered memory field m=(m1,m2) is written by local experience and is bounded, distributed, inheritable | OBSERVED (Eq. mem; construction) | deterministic | OBSERVED | "an engineered, experience-written organizational-memory field" |
| 2 | The cumulative-dose coordinate h1 is decodable from internal memory structure | ESTABLISHED | initial R^2=0.92 [0.86,0.99]; deep R^2=0.98 [0.97,1.00] | ESTABLISHED | "h1 is reliably decodable, including after deep turnover" |
| 3 | h1 survives deep material turnover (primary result) | ESTABLISHED, untouched hold-out | deep R^2=0.98 [0.97,1.00] at M~0.19; 36/36 track survival | ESTABLISHED | "the primary quantitative result: h1 is retained through deep turnover" |
| 4 | Memory is *necessary* for the h1 decode | OBSERVED (erase / readout-ablate) | erased & inert = -0.19 (deterministic collapse) | OBSERVED/ESTABLISHED | "memory is necessary: erasure or readout ablation destroys the decode" |
| 5 | Transplanting stored memory into a common erased body *reinstates* h1 (sufficiency) | INFERRED | transplant h1=0.61 [-0.69,0.87] | NOT CERTIFIED (magnitude) | "transplant reinstates h1 in the point estimate, but the effect size is uncertain (CI crosses 0)" |
| 6 | In-place causal response along h1 | INFERRED | in-place h1=0.50 [-1.39,0.92] | NOT CERTIFIED | "an in-place response consistent with h1, not statistically resolved" |
| 7 | Memory outperforms body size+mass as the carrier of h1 | INFERRED | 0.93 vs 0.64, CIs overlap | INFERRED (suggestive) | "suggestive that memory carries more than size/mass; CIs overlap" |
| 8 | Two storage coordinates (h1,h2) are present at rest after the C1c writing correction | ESTABLISHED (storage, prospective) | prospective storage h1=0.94, h2=0.94/0.96; sigma2/1=0.28 | ESTABLISHED (storage only) | "C1c stores two prospectively-decodable coordinates" |
| 9 | The order coordinate h2 is *causally expressed* (not just stored) | tested | transplant h2=-0.04; in-place h2=0.30 (<0.50) | NOT CERTIFIED | "h2 is stored but its causal expression is not established; response stays ~1-D" |
| 10 | h2 *survives deep turnover* (kill-switch) | tested, underpowered | deep h2 point 0.34 [-0.89,0.87] (spans 0.50), n=12 | NOT CERTIFIED | "h2 deep-turnover retention is not established (CI spans the threshold); this is a power limitation, not a demonstrated absence" |
| 11 | Mechanism of h2 non-persistence (why order does not carry through turnover) | tested, no causal ID | smoothing ablations negligible; dispersion grows | SPECULATIVE | "the mechanism is indeterminate; growth-injected dispersion / inter-family variance / no bistable protection are hypotheses" |
| 12 | The causal response is effectively ~1-D | OBSERVED | response eff-dim ~1.0-1.1 | OBSERVED | "the causally expressed memory is approximately one-dimensional" |
| 13 | The longitudinal tracker does not fabricate continuity (post-incident) | OBSERVED (unit tests) | translation-invariant; h1 tracker-independent 0.96/0.98/0.99 | OBSERVED | "continuity is tracker-independent; the earlier per-frame selection artefact was corrected" |
| 14 | The whole ladder was preregistered as one plan | -- | -- | RETRACTED WORDING | (do not claim) use: "sequential experiments, each frozen before its prospective family, executed once" |

## One-paragraph honest summary
A global, cumulative-dose memory coordinate (h1) is **decodable, necessary, and retained through deep
material turnover** (deep R^2 = 0.98, CI [0.97, 1.00]) -- the load-bearing result. Its **transplantable
sufficiency is directionally supported but not statistically resolved** (0.61, CI [-0.69, 0.87]). A second,
temporal-order coordinate (h2) is **stored** but its **causal expression and its survival through deep
turnover are not established** (deep 0.34, CI [-0.89, 0.87] spanning the 0.50 threshold, n = 12); this is a
**limit of statistical power**, and the **mechanism is left indeterminate**. Nothing here is claimed as
falsified.
