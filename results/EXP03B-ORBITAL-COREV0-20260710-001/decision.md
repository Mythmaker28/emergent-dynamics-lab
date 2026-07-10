# EXP03B-ORBITAL-COREV0-20260710-001 — Decision

Protocol (frozen, preregistered): `docs/experiments/EXP03B_ORBITAL_PROTOCOL.md` @a788500. Mechanism @a788500.
Executed by RUN-20260710-1930-EXP03B. Model: claude-opus-4-8 (Fable 5 lock lifted by the user).

## OBSERVED
- Matched screen: 64 Halton laws x {OFF=CORE V0, ON=+orbital} x seeds {7001,7002,7003} x cadences {10,30,60} (384 runs).
- Differential validity: OFF reproduces CORE V0 exactly — r(P,M)=0.7328; permits {17,52} (52 known survivor); |circ|=0.103.
- ON injects circulation (mean |internal circulation| 0.103 -> 0.640, ~6x) confirming the transverse mechanism.
- ON drives pervasive mixing: mean M 0.836 -> 0.324 (turnover 0.221 -> 0.686), mean P 0.853 -> 0.617, long tracks
  2293 -> 563, right-censored tracks 15227 -> 47048.
- RAW probe fraction rises slightly (0.0163 -> 0.0239) — but the frozen clean-long cross-cadence GATE yields
  **0 screening-permitted laws (ON) vs 2 (OFF)**.

## Five levels (kept distinct)
1. DISTRIBUTIONAL SHIFT: large — circulation up, M/turnover strongly shifted, P down, tracks short-lived; raw
   probe fraction up. Descriptive only.
2. SCREENING SIGNAL: **none** (ON 0 permitted vs OFF 2). The raw probe increase does NOT survive the robust
   clean-long cross-cadence gate; it is the pervasive-low-M / look-alike regime PASS B warned about.
3. FRESH-SEED RECURRENCE / 4. ALIAS REJECTION / 5. CAUSAL RE-ESTABLISHMENT: not applicable.

## INFERRED
- Orbital interaction alone does not enrich the ROBUST high-P/low-M candidate regime versus CORE V0. It increases
  circulation and turnover so much that structures become short-lived and chaotic (more raw probe coincidences,
  zero clean-long cross-cadence candidates). Consistent with PASS B (mixing / vortex churn), not turnover-individuality.

## HYPOTHESIS
- Sustained turnover-individuality, if reachable in this substrate, may require the COMBINATION of a stabilising
  density-preference term with orbital circulation (EXP03-C), where homeostatic density could bound the mixing
  that orbital alone produces.

## WHAT WOULD FALSIFY THIS?
- A pre-declared orbital parameterisation (not lowered post hoc) under which ON yields more screening-permitted
  laws than OFF with genuine, robust turnover. Not observed.

## DECISION (frozen rule)
**EXP03-B SCREEN = NEGATIVE.** Advance to **EXP03-C** (CORE V0 + density preference + orbital interaction). No
hold-out triggered; thresholds unchanged; no composite; laws 0/52 not reopened (OFF = CORE V0 control only).
