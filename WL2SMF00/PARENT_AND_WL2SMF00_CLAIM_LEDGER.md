# PARENT_AND_WL2SMF00_CLAIM_LEDGER (append-only)

| # | claim | status | evidence |
|---|---|---|---|
| W1 | The chain `e912a10 -> f81daf9 -> f9e1e39 -> f65851c -> 0d92b61` is direct-parent at every arrow. | ESTABLISHED | device `rev-parse`; blob ids recomputed from local bytes, 6/6 |
| W2 | Materiality and numerical detectability are separated, not merged. | ESTABLISHED | `ETA_ORACLE_L2 = 0` on all 16 descendants, so the threshold is set by a scientific floor everywhere |
| W3 | The scoring path is exactly arithmetic-free of error. | ESTABLISHED (proof + 2 controls) | Fraction reader, exact subtraction, bit-exact npz reload; a float64 path differs on the same input |
| W4 | The oracle suite is non-vacuous. | ESTABLISHED | 14 groups pass, 12 negative controls fire, AST audit rejects an injected self-comparing predicate |
| W5 | `M2` alone cannot validate the gauge scope; the whole-descendant block invariant can. | ESTABLISHED | a per-time swap leaves `M2` unchanged and changes the block invariant |
| W6 | History route is `H3` (complementary allocation orbit); `H1` and `H2` are ineligible. | ESTABLISHED | `apply_dual_history` is lockstep with identical global forcing; no pre-designated physical anchor exists |
| W7 | Geometry route is `G1`: the upstream RNG precursor is geometry-independent. | ESTABLISHED | `seed_state` hashes identically under both geometry settings; geometry enters only via the blob mask |
| W8 | The refactored constructor is semantics-preserving. | ESTABLISHED | both old parity branches reproduced byte-for-byte against committed checkpoint hashes |
| W9 | A complete 16-descendant, 4-block G1 panel exists and is sealed. | ESTABLISHED | 4/4 blocks accepted, 16/16 admissible, panel lock written before the first sham |
| W10 | Every descendant has two byte-identical shams over the full horizon. | ESTABLISHED | 16/16, including the terminal state hash |
| W11 | Every descendant has one finite, positive, sealed threshold. | ESTABLISHED | 16/16; range 7.2618e-04 .. 1.2667e-03 |
| W12 | Production and independent reference agree everywhere. | ESTABLISHED | 40 random fixtures plus all 16 descendants; a control confirms the reference catches a wrong value |
| W13 | The modal, contrast and quotient-pair propagations are proved, not cited. | ESTABLISHED | isometry, contractive centering, contractive projection, then `L2 <= R1 <= R0 <= E_TAU` |
| W14 | The modal gate strictly implies the total gate. | ESTABLISHED, LIMITING | `L2 <= R0` always, so the two gates are nested; a passing panel needs `R0 > 20 * E_TAU` at share 0.05 |
| W15 | In NEAR geometry the two complementary allocations have systematically different sham drift. | ESTABLISHED (sham-only) | `TAU_DYNAMIC` a0 vs a1 separates in all four NEAR blocks; a purely baseline observation, no response claim |
| W16 | Zero active outcome was generated or opened. | ESTABLISHED | start ledger: 2 setup + 16 construction + 32 sham = 50 of 64; dependency audit shows the threshold pipeline cannot reach an active array |
| W17 | No parent disposition was reclassified. | BY CONSTRUCTION | append-only ledger; no historical active row was loaded by any code path |

## Explicitly NOT claimed

* Not claimed: that the historical carrier structure, environmental extension or founder stratum is
  absolutely material. All three are `NOT_TESTED` and remain so.
* Not claimed: that the old twelve reversed cells now pass. They were not scored under this rule
  and may not be.
* Not claimed: any geometry, history or allocation **response** effect. W15 is a sham drift
  observation about untreated trajectories.
* Not claimed: life, agency, identity, memory, provenance, bath, curvature, multiscale structure,
  universal dimension, population generalisation or independent confirmation.
* The sealed numeric thresholds are valid **only** for this exact reader, masks, normalizer,
  weights, checkpoint, horizon, LawSpec and descendant panel. The formula may inform later designs;
  the numbers do not transfer to other founders.
