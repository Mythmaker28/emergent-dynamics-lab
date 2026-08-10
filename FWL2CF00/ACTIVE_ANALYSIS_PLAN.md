# FWL2CF00 — complete active-analysis plan (frozen before any fresh outcome)

## Order of operations, each gated by a committed lock

1. **Pre-execution commit (this one).** Provenance, master freeze, binding manifest, tested
   production and reference scorers, the non-vacuous oracle report, the sham reconstruction lock
   and this plan. Zero fresh outcome of any kind.
2. **16 canonical SHAM_0 replays**, one fresh process each, output paths predeclared and
   non-existent, overwrite forbidden. Independent-process disk readback that rebuilds the reader
   series from persisted raw `rho` bytes rather than trusting the just-written values.
3. **Canonical sham series lock + active panel lock**, committed. Zero active outcome present.
4. **32 active continuations** (16 descendants x 2 frozen carrier arms), opaque ids, fresh process
   each, `START_ENTER` fsynced before each launch so a launch consumes the continuation even if
   the child dies first. The acquisition driver never computes or prints a score.
5. **Raw-only commit** with the raw panel lock and an independent readback, before any factor
   label is decoded and before any scientific score exists.
6. **Analysis commit**: decode labels, score exactly, run the exhaustive gauge oracle, apply the
   gates in the frozen order, write reports.

## Scoring, exactly as frozen

`delta = X[INT] - X[SHAM_0_REPLAY]` per channel and scored time; never the t0 value, never a
historical parent response, never a second sham. `M2^2 = sum_h w_h (delta_A^2 + delta_B^2)`,
checked against `||u||^2 + ||v||^2`. All reader arithmetic stays in exact `Fraction`; the
`ETA_ORACLE_L2 = 0` bound is claimed only for that exact path and never for a float `np.sum`.

## Gate order

1. **Cell materiality**, exact squares, equality is failure, 32 of 32 required.
2. **Fresh quotient**, only on `PASS_32_OF_32`: `R0` exactly for all 32768 linked swaps;
   `R1`, `R2` exhaustively in float with a Weyl / backward-stability bound and exact certification
   of the argmin and every near-tie. Gates `QDIM0..QDIM3` plus the direct one-family reconstruction
   over every co-optimal `M1`.
3. **Stratum transfer** — already declared `NOT_EVALUABLE_FROM_COMMITTED_PARENT_OBJECT` in the
   master freeze, because GIMB00 serialised only scalar summaries of `psi_plus` / `Psi_minus` and
   rebuilding them would require reopening and refitting historical active rows.
4. **Factorial attribution of the parent stratum** — `NOT_REACHED`, following (3).

## What is still evaluated, and under which label

The predeclared fresh G1 x H3 factor objects are computed and reported under
`FRESH_FACTOR_EFFECT_NOT_PARENT_STRATUM_EXPLANATION` only:

* PLUS sector (common, response units): geometry contrast averaged over allocation, unoriented
  allocation sensitivity, geometry modulation of that sensitivity, and the predeclared
  operator-difference contrasts. Floor: `TAU_CONTRAST(c) = sum_i |c_i| TAU_i` from the locked
  per-descendant `TAU`, with normalised `c`.
* MINUS sector (differential, response^2 and response^4 objects): computed as shape diagnostics
  and labelled `TRANSFORMED_BOUND_NOT_QUALIFIED`, because the parent propagation certificate
  records `PROJECTIVE_EMBEDDING_BOUND = NOT_AVAILABLE` and `H3_K_BOUND = NOT_AVAILABLE`.

`KAPPA_TWO_ARM = 1/sqrt(2)` (equal-arm normalised block) is fixed here, paired with the smaller
floor `TAU_d0 + TAU_d1`; the normalised block is never combined with the enlarged bound.

## Allocation-label gauge

The neutral H3 member names `0` and `1` carry no physical sign and are not anchored across
geometry. Every H3 object and disposition must be invariant under all `2^8` independent
allocation-member exchanges, one per (ancestry block, geometry) pair.

## Independent units

`n = 4` upstream ancestry blocks. 16 descendants, 32 active rows, 2 arms, 2 channels, 10 times and
all sites are repeated conditions. With four blocks the smallest attainable two-sided sign-flip
p-value is `2/16 = 0.125`, so `P_LESS_THAN_0_05_POPULATION_CLAIM = IMPOSSIBLE_AND_NOT_REQUIRED`.
