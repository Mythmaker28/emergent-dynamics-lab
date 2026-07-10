# EXP03C-COMBINED-COREV0-20260710-001 — Decision

Protocol (frozen, preregistered): `docs/experiments/EXP03C_COMBINED_PROTOCOL.md` @ed06075. Executed by
RUN-20260710-1945-EXP03C. Model: claude-opus-4-8 (Fable 5 lock lifted by the user).

## OBSERVED
- Matched screen: 64 Halton laws x {OFF=CORE V0, ON=density+orbital} x seeds {7001,7002,7003} x cadences {10,30,60}.
- OFF reproduces CORE V0 (r(P,M)=0.7328; permits {17,52}; |circ|=0.103).
- ON (both mechanisms) injects the most circulation of the ladder (|circ| 0.103 -> 1.012) but still drives mixing:
  mean P 0.853 -> 0.588, mean M 0.836 -> 0.427 (turnover 0.221 -> 0.583), long tracks 2293 -> 513, censoring
  15227 -> 39625, and the RAW probe fraction DROPS (0.0163 -> 0.0059). **Screening-permitted laws: OFF 2, ON 0.**

## Five levels (kept distinct)
1. DISTRIBUTIONAL SHIFT: large (circulation up, P/M down, tracks short); descriptive only.
2. SCREENING SIGNAL: none (ON 0 permitted vs OFF 2).
3-5. FRESH-SEED RECURRENCE / ALIAS REJECTION / CAUSAL RE-ESTABLISHMENT: not applicable.

## INFERRED
- The D-019 hypothesis — that density homeostasis might bound orbital mixing to yield candidates — is FALSIFIED.
  The combination does not rescue robust high-P/low-M candidates; it remains mixing/depletion-dominated.

## Particle Dynamics causal ladder — outcome
- CORE V0: closed CASE A (D-017); survivors {0,52} occupancy/look-alike-compatible, no turnover-individuality.
- EXP03-A density: NEGATIVE (D-018) — depletes the regime.
- EXP03-B orbital: NEGATIVE (D-019) — injects circulation/turnover but 0 robust candidates.
- EXP03-C density+orbital: NEGATIVE (this decision) — no synergy.
Across the full preregistered ladder, no CORE V0 / density / orbital law family produced audited
constituent-turnover individuality under the frozen falsifiable protocol.

## WHAT WOULD FALSIFY THIS?
- A pre-declared (not post-hoc) parameterisation of the combined mechanism under which ON yields more
  screening-permitted laws than OFF with robust, audited turnover. Not observed.

## DECISION (frozen rule)
**EXP03-C SCREEN = NEGATIVE.** The Particle Dynamics causal ladder is exhausted for this question. A **Particle
Dynamics substrate decision / kill-switch evaluation** is now due per the charter (do not switch substrate without
the documented kill-switch review). Thresholds unchanged; no composite; laws 0/52 not reopened.
