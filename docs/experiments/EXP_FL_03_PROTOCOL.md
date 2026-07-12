# EXP-FL-03 — Frozen Protocol: multi-seed causal replication + adversarial re-audit

Status: **FROZEN before any run.** Preregistered by `RUN-20260710-2300-EXPFL03`. Purpose: try to KILL the
EXP-FL-02 diagnostic survivors. A positive that does not survive this is dead.

## FROZEN SUBJECTS (no additions, replacements, ranking, or visual selection)
Laws **{2, 16, 40, 59}** exactly as carried by D-026. Mechanism, core law params, throughput params, field stack,
detector, tracker, phenotype, P, M and ALL thresholds are FROZEN and unchanged (P>0.8, M<0.5). No composite score.

## SEEDS
**12 UNSEEN causal seeds per law: 9601-9612** (screening 8001-8003; hold-out 9001-9005; EXP-FL-02 causal 9501 —
none reused). 4 laws x 12 seeds = 48 causal units. Seeds with no candidate structure at enrollment are **CENSORED
and reported**, never dropped.

## MATCHED BRANCHES (frozen, from an IDENTICAL pre-intervention state)
CONTROL (no change) / SHAM (identical displacement pipeline with zero displacement -> must equal CONTROL
bit-for-bit) / PERTURBED (displace the candidate structure's mass by the frozen DELTA=(20,20) cells) / PLACEBO
(displace a matched non-candidate mass region by the same DELTA).

## EXPLICIT DENOMINATOR AND TIME WINDOW (applies to EVERY reported percentage)
Post-intervention horizon = **150 steps** at the frozen snapshot cadence **10** -> **N_POST = 15 post-intervention
snapshots**, excluding t=0. "frac_new_organized" = (# of those 15 snapshots in which a detected entity within
SITE_RADIUS=12 cells of the NEW site has P > 0.8 vs the frozen pre-intervention phenotype phi*) / 15.
"frac_old_organized" is the same with denominator 15 at the OLD site. No other denominator is used anywhere.

## AUDITED SUCCESS (ALL must hold; strictly stricter than EXP-FL-02)
1. ENROLLED (a candidate structure of size >= 3*min_cells exists after warmup).
2. SHAM == CONTROL bit-for-bit.
3. RE-ESTABLISHED: frac_new_organized > 0.5 (i.e. > 7.5 of 15 snapshots).
4. EXCEEDS PLACEBO: frac_new_organized(PERTURBED) - frac_new_organized(PLACEBO) > 0.25 (corrected criterion, kept).
5. NOT OCCUPANCY: frac_old_organized(PERTURBED) <= 0.5 (the old site does not regenerate the phenotype).
6. **CONTINUED TURNOVER (NEW):** the re-established new-site structure must KEEP exchanging constituents in the
   post-window: the frozen field M between its own post-intervention observations, at the frozen lags, must drop
   below the frozen threshold 0.5 at least once. A structure that re-establishes and then FREEZES (a lump that
   stops turning over) is classified **frozen_lump** and is NOT an audited success. This is the criterion that
   killed CORE V0 law 52 and it is applied here in full.

## CLASSIFICATION (mutually exclusive, per enrolled unit)
`destroyed_or_no_reestablishment` | `placebo_failure` | `occupancy_alias` | `frozen_lump` | `AUDITED`.

## REPORTING (mandatory, per law)
enrollment count; censored seeds; audited successes; alias-compatible (occupancy) cases; placebo failures;
frozen-lump failures; destroyed; effect size = audited / enrolled with a **Wilson 95% confidence interval**;
plus the CONTROL and PLACEBO fractions for contrast.

## CADENCE / TRACKER SENSITIVITY (preregistered)
For every AUDITED unit, re-run the causal unit at snapshot cadence **5** and **20** (denominators 30 and 7
respectively, stated explicitly) and with tracker distance scaled x0.8 and x1.2. An audited success that does not
survive these observer perturbations is an OBSERVER ARTEFACT and is withdrawn.

## ADVERSARIAL INDEPENDENT RE-AUDIT
A hostile-reviewer pass, journaled separately, must attempt to explain any surviving audited success WITHOUT
constituent-carried organization (trivial coherence, weak placebo, enrollment bias, denominator inflation, site
radius, displacement into empty space, reservoir bookkeeping). Objections are recorded whether or not they change
the verdict.

## DECISION
- Audited successes survive multi-seed replication AND sensitivity AND adversarial audit -> the survivors become
  REPLICATED CAUSAL CANDIDATES (still not a "discovery"; independent verification remains required).
- Otherwise -> the EXP-FL-02 positive is WITHDRAWN or downgraded, and that is reported plainly.

## FALSIFIERS
F1 audited rate collapses on unseen seeds. F2 successes are frozen lumps (no continued turnover). F3 placebo
explains them. F4 occupancy alias. F5 observer (cadence/tracker) artefact.
