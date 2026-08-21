# DOTC01 — THE ORGANISER TIMESCALE

Formulas frozen before any developmental distribution was read: `True`.

## Constituent lifetime

| | B1 | B2 |
|---|---|---|
| muY | 9.261187281287937e-05 | 1e-08 |
| e-folding, steps | 10797.251615563411 | 99999998.99752407 |
| exact discrete mean | 10796.751623277094 | 99999999.0 |
| exact discrete median | 7484 | 69314717 |
| P(decay by 1000) | 0.08845668147700536 | 9.999950100425536e-06 |
| P(decay by 2500) | 0.2066893579825705 | 2.4999687753268773e-05 |
| P(decay by 5000) | 0.37065822526189385 | 4.9998750522028956e-05 |
| P(decay by 11000) | 0.6389640630003623 | 0.00010999395132438305 |

## Local Y-birth hazard

Exact per cell per step: `P(no Y birth) = (1 - min(1, kY*nX*nY))^cand`, `cand = min(nSY, free)`.

| | B1 | B2 |
|---|---|---|
| mean of world means | 8.6805e-05 | 7.0632e-05 |
| median of world medians | 0.0000e+00 | 0.0000e+00 |
| max observed | 1.2804e-03 | 1.2058e-03 |
| P(>=1 local Y birth by 1000) | 0.0699 | 0.0622 |
| P(>=1 local Y birth by 2500) | 0.1509 | 0.1465 |
| P(>=1 local Y birth by 5000) | 0.2362 | 0.2750 |
| P(>=1 local Y birth by 11000) | 0.3239 | 0.4885 |

The linearisation `kY*Q` is an upper bound on the exact hazard and is never substituted for it.

## Complete-turnover time

An exact discrete-time absorbing chain driven step by step by each world's realised hazard sequence.
No mean replaces a time-dependent hazard.

| | B1 | B2 |
|---|---|---|
| P(complete turnover by 1000) | 0.00575 | 0.00000 |
| P(complete turnover by 2500) | 0.02629 | 0.00000 |
| P(complete turnover by 5000) | 0.06495 | 0.00001 |
| P(complete turnover by 11000) | 0.11664 | 0.00006 |
| median / q80 / q90 | None / None / None | None / None / None |
| P(extinct before turnover) | 0.25524 | 0.00008 |

`None` means the quantile is not reached inside the 11000-step horizon.

**The hold is event-based, not a clock.** The criterion is that the centre keeps its local X organising
function through at least one complete constituent turnover. The horizon exists only to bound the
observation, and it is not lengthened beyond 11000.

## The one approximation, stated

> after the actual first birth a world's recorded environment is that of a two-constituent centre. Using that recorded sequence inside the hypothetical single-constituent branch is the one approximation in this calculation. Because the per-step hazards are of order 1e-4, the induced error on the reported probabilities is far below the sampling error of a 44-world developmental set, and the direction is to slightly OVERSTATE the birth rate in the single-constituent branch.
