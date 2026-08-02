# Stage-B formation versus conditional maintenance estimands

## Status

**Definitions frozen; numerical estimates unavailable because the developmental autopsy is `AUDIT_INVALID`.**

The accepted Stage-B gate combined two distinct future estimands:

1. **A — formation from a neutral initial condition:** the original-world fraction forming any detected component,
   reported for all 64 worlds and descriptively by IC class and LawSpec/IC stratum.
2. **B — maintenance conditional on formation:** among original worlds in which a component formed, the nested
   progression through bounded activity, persistence, turnover, prefix-candidate status, stable candidate episode and
   terminal persistence. Track-level rows are diagnostic only and never replace the original-world denominator.

The plan also froze cumulative formation by detector frame, opportunity flags for the persistence and post-turnover
horizons, and full numerator/denominator reporting. Soup/compact rows sharing a nominal replicate index were explicitly
not treated as matched random-number pairs. Four worlds per LawSpec/IC were descriptive and never a precise
probability estimate.

## Why no estimates appear

Both raw-only implementations stopped on the same lifecycle inconsistency: a reconstructed representative track ends
before frame 159 without an explicit `DISSOLUTION` event. Under the frozen protocol this precedes every developmental
outcome and selects `AUDIT_INVALID`. No closed world-transition table exists, so denominators, trajectories and
candidate episodes cannot be partially salvaged or computed from a surviving subset.

The conceptual A/B distinction remains useful for future design, but this audit supplies no numerical evidence about
either estimand and cannot motivate selection of L005, L006 or any individual candidate world. The accepted
`DEV_FEASIBILITY_FAIL` disposition remains unchanged. Human review is the only next action.
