# TCA-01 — Tracker-Continuity Incident Report

Trigger: on `--preset turnover` (seed 38501, viewer 6891ef8) the red tracked-entity overlay teleported between
blobs, with a simultaneous h2 time-series jump and red at both horizontal edges.

## TRACKER INCIDENT VERDICT: PASS WITH CORRECTION — H1 SURVIVES CONTINUITY-SAFE TRACKING
The teleport is a **largest-component RESELECTION** artefact shared by the viewer AND every analysis script;
it does NOT invalidate the load-bearing h1 result, because h1 is a globally-imposed coordinate and is robust
to tracker choice, and a continuity-safe longitudinal tracker corroborates it (0.99, 100% survival).

## Diagnosis (seed 38501, event-by-event)
- Selection rule everywhere: `largest(st) = max(entities, key=size)` — the largest connected component is
  RESELECTED each frame (sc_iom/sc_mcm/dmm01/h2cert/smc01/wd01 all call it). This is reselection, not tracking.
- 5 hard SWITCH events (steps 80,270,620,640,650): centroid jumps 19-32 cells, mask overlap 0.0 with the prior
  entity; std(m-) and M jump at exactly those frames. M becomes non-monotonic near the end (0.233->0.257->0.209->0.240).
- Detection is periodic-safe (`_label_periodic`, `circular_centroid`). Pure whole-world translation (incl.
  boundary-straddling) leaves size/mean-m/std(m-) BIT-INVARIANT (only display centroid moves) -> "red at both
  edges" is one correctly-detected periodic-straddling entity, NOT a wrap bug.

## Tracker sensitivity (deep turnover, 14 histories x2 seeds)
h1 decoded from: largest-each-frame 0.96 | 2nd-largest blob 0.98 | longitudinal track 0.99 -> **h1 is a GLOBAL
dose coordinate, tracker-independent.** Longitudinal survival to M~0.21: 28/28 (100%); mean M(longitudinal)=0.21.

## Outcome classification
A periodic display artefact: RULED OUT as primary (features translation-invariant). B viewer-only: partly (the
viewer teleports). C scientific reassignment: CONFIRMED (analysis also reselects) BUT the h1 conclusion is
robust and longitudinal-safe. D split/merge undefined: NO (100% longitudinal survival here). E mixed: the
teleport = reselection + a correctly-wrapping straddling entity. => PASS WITH CORRECTION (Outcome C-pass).

## CLAIM-IMPACT TABLE
| Claim | Status | Note |
|---|---|---|
| h1 prospectively decodable | UNAFFECTED | tracker-independent (largest=2nd=longitudinal) |
| h1 deep-turnover survival (0.93 @ M~0.21) | UNAFFECTED / QUALIFIED | robust to tracker; longitudinal tracker gives 0.99, 100% survival. Re-word: h1 is a GLOBAL cumulative-experience memory decodable from viable entities, corroborated by longitudinal tracking — not an individual-specific claim |
| h1 causal / transplant | UNAFFECTED | transplant uses a common erased body; not entity-tracking-dependent |
| old-material fraction M | QUALIFIED | non-monotonic under largest-reselection; continuous & ~0.21 under longitudinal tracking |
| viability "48/48" | QUALIFIED | meant "a viable component existed"; longitudinal survival 100% (28/28) in the sensitivity sample corroborates it |
| h2 turnover failure | UNAFFECTED | h2 also global; population decode; single-trajectory h2 jump = viewer reselection artefact |
| entity size continuity | QUALIFIED | size ~stable but hides which blob under largest-reselection |
| frame-free distributional decode | UNAFFECTED | does not exploit entity switches (tracker-independent decode) |
| INDIVIDUAL continuity / individuation | ALREADY NEGATIVE | audit reconfirms: memory is global/organizational, not individual — consistent with the prior individuation FAIL |

## Corrections shipped
- Viewer default is now **longitudinal** tracking (`--preset story`, `--track longitudinal`): follows ONE
  entity by periodic max-overlap and shows **TRACK LOST** rather than teleporting; `--track largest` retained
  for audit. Event labels shown. New story movie + contact sheet exported.
- Manuscript wording to update (already in errata E5): h1 = one-dimensional causal *organizational-state*
  memory of GLOBAL cumulative experience, corroborated by longitudinal tracking; not individual continuity.

## PAPER-READINESS: RESTORED — ONE-DIMENSIONAL POSITIVE WITH NEGATIVE BOUNDARY
No load-bearing claim invalidated. Required wording corrections are in the errata ledger + this report.
Optional cheap follow-up: a sealed-family (38xxx) longitudinal re-confirmation (dev-family longitudinal already 0.99).
