# T6′ CONTRADICTION AUDIT

## The apparent contradiction
Prior report claimed both (1) all-amplifying contamination can put every corrected channel above the true
response, and (2) the interval [min|v_i|, max|v_i|] covered q 40/40 in every tested regime.

## Resolution: NOT contradictory — the 40/40 regimes all had a CLEAN reference
Instrumenting all 40 trials per regime (consolidation, seeds 100–139):

| regime | clean references present | bracket covers |
|---|---|---|
| clean (0,0,0) | 3 | 40/40 |
| differential attenuating | 2 | 40/40 |
| differential amplifying | 2 | 40/40 |
| two contaminated, mixed sign | 1 | 40/40 |

Every 40/40 regime had **≥1 clean reference**. The 40/40 test never included a no-clean-reference case, so it
never probed the failure direction.

## The boundary (no clean reference, 40 seeds each)
| regime (0 clean) | bracket covers | position vs q |
|---|---|---|
| all attenuating | 7/40 | 33/40 **below** q — valid LOWER bound |
| all amplifying | 5/40 | 35/40 **above** q — FALSE lower bound (valid UPPER bound) |
| common-mode, c<0 | 12/40 | 28/40 above q |

## Conclusion
The bracket theorem holds **iff a clean anchor exists** (T6-C). With no clean reference, {|v_i|} lies on one side
of |q|, and which side is set by `sign(α_i κ_i)`: attenuation → lower bound, amplification → upper bound. The
historical "lower bound" silently assumed attenuation. No coding error in the 40/40 result — it was correct but
scoped to the clean-anchor case, which was never stated. Documented, not repaired.
