# EXP03A-DENSITY-COREV0-20260710-001 — Decision

Protocol (frozen, preregistered): `docs/experiments/EXP03A_DENSITY_PROTOCOL.md` @3406ef0. Mechanism @3406ef0.
Executed by RUN-20260710-1850-EXP03A. Model: claude-opus-4-8 (Fable 5 lock explicitly lifted by the user).

## OBSERVED

- Matched screen: 64 Halton laws x {OFF=CORE V0, ON=+density preference} x seeds {7001,7002,7003} x cadences
  {10,30,60}. 384 runs. Frozen P/M observers, no recalibration, no composite score.
- Differential validity check: the OFF condition reproduces CORE V0 — descriptive r(P,M)=0.7328 (CORE V0 baseline
  0.733162; EXP02 0.731581) and OFF screening-permits laws {17,52}, with law 52 a known CORE V0 survivor.
- Adding density preference (ON) shifts the distribution DOWNWARD, not upward:
  mean P 0.8528 -> 0.7893 (-0.064); mean M 0.8363 -> 0.7942 (-0.042); probe fraction 0.0163 -> 0.0094 (-0.007);
  long tracks 2293 -> 2042; right-censored tracks 15227 -> 20511; mean turnover 0.221 -> 0.238.
- Screening-permitted laws (>=2/3 eligible seeds, frozen gate): OFF = 2 ({17,52}); **ON = 0**.

## Five levels (kept distinct)

1. DISTRIBUTIONAL SHIFT: present but NEGATIVE — density preference lowers P and M and shortens/censors tracks
   (descriptive only; not a candidate).
2. SCREENING SIGNAL: **none** under ON (0 permitted laws vs 2 for CORE V0).
3. FRESH-SEED RECURRENCE: not evaluated (no ON candidate to hold out).
4. ALIAS REJECTION: not applicable.
5. CAUSAL RE-ESTABLISHMENT: not applicable.

## INFERRED

- An isolated comfortable-neighbour density-preference mechanism does NOT enrich the high-P/low-M regime relative
  to CORE V0; on this pre-declared screen it depletes it (more censoring, shorter tracks, lower P). This is
  consistent with PASS B's "reduced mobility / homeostatic settling" reducing coherent persistence rather than
  producing turnover-individuality. No densification-driven enrichment was observed.

## HYPOTHESIS

- Density homeostasis alone regularises local crowding and slightly disperses/settles structure, reducing the
  rare high-P/low-M coincidences CORE V0 already produces. Enrichment of turnover-individuality, if it exists in
  this substrate family, is more likely to require orbital/transverse interaction (EXP03-B) or the combination
  (EXP03-C).

## WHAT WOULD FALSIFY THIS?

- A different pre-declared density parameterisation or gate (not lowered post hoc) under which ON yields more
  screening-permitted laws than OFF with genuine turnover (not densification/rigidity/occupancy). Not observed here.

## DECISION (frozen rule §DECISION)

**EXP03-A SCREEN = NEGATIVE.** No (law, ON) earned screening permission; density preference did not enrich the
candidate regime versus CORE V0. Document and advance to **EXP03-B** (CORE V0 + orbital/transverse interaction
only) per the charter. No fresh-seed hold-out is triggered. Thresholds unchanged; no composite score; laws 0/52
remain closed and were not reopened (their appearance here is only the OFF=CORE V0 control reproducing prior behaviour).
