# EXP-RD-03 — DECISION: CANDIDATE RETAINED (no promotion). Gray-Scott NOT retired.

Protocol: docs/experiments/EXP_RD_03_PROTOCOL.md (SHA 9c3aba3798c946b7b28f99c1a4f36f0078f77baf), frozen at 280a1e8
before any result was produced. No threshold changed. No composite score. No law ranked, replaced or visually
selected. No post-hoc halo tuning (support radii follow from each law's own Du, F).

## Part A — observer-ONLY sensitivity: RESOLVED
Fixed physics, fixed pre-intervention state, fixed `t*` = 400, fixed branches; only the OFFLINE observation
cadence {25,50,100} and readout site radius {0.8,1.0,1.2} vary (9 settings). sham==control in 6/6.

**4/6 of the EXP-RD-02 provisional successes are AUDITED in all 9 observer settings.**
Corrected EXP-RD-02 rate: **4/90 = 4.4 % [Wilson 1.7 %, 10.9 %]**.
The 2 fragile units — (1,12007), (7,12007) — sit exactly on the frozen `frac_new > 0.5` line (0.47, 0.50 at
cadence 25: finer sampling includes more of the recovery transient). Recorded as observer-fragile. Threshold unchanged.

The invalid RD-02 test had reported 0/6. It was wrong in both directions of its own logic.

## Part B — causal-boundary nested support sweep: BOUNDARY HYPOTHESIS REFUTED
9 frozen laws x 4 unseen seeds (13001–13004) = 36 units; 0 censored; sham==control bit-for-bit 36/36; n_post = 15.
U, V and all passive temporal cohorts translated together inside each support.

| support | radius | AUDITED | Wilson 95% |
|---|---|---|---|
| S0 detected mask | 0 | 5/36 = 13.9 % | [6.1 %, 28.7 %] |
| S1 mask + small halo | 2 | 3/36 = 8.3 % | [2.9 %, 21.8 %] |
| S2 ≈ 1 diffusion length | ceil(ell) | 1/36 = 2.8 % | [0.5 %, 14.2 %] |
| S3 ≈ 2 diffusion lengths | ceil(2·ell) | 4/36 = 11.1 % | [4.4 %, 25.3 %] |

**Broadening the support does not improve re-establishment; all four intervals overlap.** Therefore:
- the 75–83 % "destroyed" outcomes are **NOT** an entity-boundary artefact;
- re-establishment is **NOT** niche/site-carried — carrying the U-depletion field and the RD halo does not help.
The frozen "requires a broad niche → REJECT" branch does not apply. The frozen "no support succeeds → retire" branch
does not apply.

## Additional falsifier (not preregistered; run because it could have killed everything): AMBIENT-SPOT NULL
Gray-Scott spots are near-identical and self-replicating, so a phenotype-matching spot could appear at the target
site **by itself**. PLACEBO controls for *displacing something*; it never asked this. Scored the CONTROL branch
(nothing displaced) at the target site for the 5 observer-robust units:

| unit | CONTROL frac_new | PERTURBED frac_new | difference |
|---|---|---|---|
| (11,12003) | 0.00 | 1.00 | +1.00 |
| (14,12001) | 0.00 | 0.60 | +0.60 |
| (14,12006) | 0.00 | 0.87 | +0.87 |
| (14,12008) | 0.00 | 0.93 | +0.93 |
| (14,13002) | 0.00 | 0.73 | +0.73 |

**The ambient alias does not fire (0.00 in 5/5).** Nothing phenotype-matching grows at the destination unless the
structure is actually put there.

## Combined result over ALL unseen causal seeds (RD-02 n=90 + RD-03B n=36 = 126)
**Observer-robust, compact-support causal re-establishment with continued constituent turnover:
5/126 = 4.0 % [Wilson 1.7 %, 9.0 %].**
Units: (11,12003), (14,12001), (14,12006), (14,12008), (14,13002).
**Law 14 supplies 4 of the 5, replicating across two independent unseen seed batches.**

Each of the five simultaneously satisfies: SHAM ≡ CONTROL bit-for-bit; re-establishment at the new site;
exceeds PLACEBO by > 0.25; no old-site regeneration; continued temporal-cohort turnover (not a frozen lump);
AUDITED under all 9 offline observer settings; and CONTROL grows nothing at the destination.

## VERDICT
**RETAIN AS CANDIDATE — NO PROMOTION.** Gray-Scott is NOT retired.

This is the first candidate in the project to survive the full adversarial battery. It is also only 4 % against a
~80 % destruction base rate, on 126 units, and **the pipeline's own false-positive rate has never been measured.**
A 4 % positive rate is not distinguishable from a 4 % pipeline artefact rate until that rate is measured. That
measurement — not further celebration — is the next required step (EXP-RD-04).
