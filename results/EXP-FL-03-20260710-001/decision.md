# EXP-FL-03 — Decision: the EXP-FL-02 positive is WITHDRAWN

Protocol @14c3a97 (frozen before any run). RUN-20260710-2300-EXPFL03. Model: claude-opus-4-8 (lock lifted).
Laws {2,16,40,59}, mechanism, P/M and all thresholds FROZEN. No additions, replacements, ranking or visual selection.

## DENOMINATORS AND TIME WINDOW (explicit)
Post-intervention horizon 150 steps. At the frozen cadence 10 -> **15 post-intervention snapshots**: every
"frac_organized" is out of 15. In the sensitivity runs the denominator is stated per setting: cadence 5 -> 30;
cadence 20 -> **8** (150 is not divisible by 20; stated, not rounded).

## RESULTS — 4 laws x 12 UNSEEN causal seeds (9601-9612) = 48 units
| law | seeds | enrolled | censored | AUDITED | frozen_lump | placebo_fail | occupancy | destroyed | audited/enrolled [Wilson 95% CI] |
|---|---|---|---|---|---|---|---|---|---|
| 2  | 12 | 12 | 0 | 1 | 9  | 0 | 0 | 2 | 0.083 [0.015, 0.354] |
| 16 | 12 | 12 | 0 | 0 | 12 | 0 | 0 | 0 | 0.000 [0.000, 0.243] |
| 40 | 12 | 12 | 0 | 1 | 8  | 0 | 0 | 3 | 0.083 [0.015, 0.354] |
| 59 | 12 | 10 | 2 | 0 | 1  | 0 | 0 | 9 | 0.000 [0.000, 0.278] |
**POOLED: enrolled 46, censored 2, AUDITED 2/46 = 0.043 [0.012, 0.145].** SHAM == CONTROL bit-for-bit in ALL units.
EXP-FL-02 reported 4/4 of these laws audited on ONE seed (9501).

## OBSERVER SENSITIVITY (preregistered)
Both surviving audited units FAIL: law 2/9611 -> frozen_lump (cadence 5), destroyed (cadence 20);
law 40/9610 -> destroyed (cadence 5), frozen_lump (cadence 20). Both survive tracker x0.8/x1.2.
**0/2 survive cadence perturbation -> observer artefact (F5).**

## NET RESULT: **0 audited successes survive the full frozen protocol.**

## Why it died (dominant failure mode)
**frozen_lump = 30/46 (65%)**: the displaced structure DOES re-establish at the new site, DOES exceed the placebo,
and the old site does NOT regenerate -- but it then **STOPS exchanging constituents**. That is trivial
translation-covariance of a coherent lump, exactly the failure that killed CORE V0 law 52. Without the
continued-turnover requirement this run would have reported ~32/46 "successes" and been WRONG.
Falsifiers F1 (non-replication), F2 (frozen lumps) and F5 (observer artefact) are all CONFIRMED.
placebo_failure = 0 and occupancy_alias = 0: the positive did not die from a weak control, it died from reality.

## DECISION
**EXP-FL-03 NEGATIVE. The EXP-FL-02 diagnostic survivors {2,16,40,59} are WITHDRAWN (D-027).** Nothing is promoted.
The reservoir-exchange mechanism does reach the turnover regime (a real screening/hold-out result) but does NOT
produce organization that is simultaneously persistent, constituent-carried under displacement, and CONTINUING to
turn over. No threshold, metric, mechanism or law was changed to reach this conclusion.

## RECOMMENDATION (per the standing instruction)
STOP adding mechanisms to the closed, globally mass-conservative Flow-Lenia system. A globally conservative
active/reservoir exchange yields turnover WITHOUT sustained constituent-carried individuality. The next honest step
is a genuinely **open-system / reaction-diffusion substrate** with true sources and sinks and non-equilibrium
driving (not a closed conservative field), preregistered under this same falsifiable protocol.
