# PROTOCOL_DEVIATIONS

## D1 — vacuous oracle written and then repaired (self-defect, mine)

The first pass of the gauge oracle contained three predicates of the form
`if ip(v_i,v_j) != e*e*ip(v_i,v_j)` and `if bip([p],[p]) != bip([p],[p])`. Each compares an
expression to itself and passes on arbitrary input. This is precisely the defect this programme
line condemned in ETCMNFC and again in EEFCA, and I reproduced it.

Repair: `gimb_oracle_v2.py` supersedes that block. Every test now applies a real exchange of the
two scored regions to the underlying `delta_A`/`delta_B` bytes, recomputes each invariant from the
exchanged data, and is accompanied by a negative control that fires. Both source states are kept.

## D2 — wrong object in the Q0E reconstruction test, corrected before use

My first Q0E tested rank-one-ness of the **arm Gram** `P[i][j] = <v_i,v_j>`, which is a contraction
of the block outer product and has rank `min(n_arms, T)`, not 1. It returned false, correctly, for
the wrong reason. The handoff's object is the outer product of the **concatenated** block vector,
which is rank one by construction. Corrected and re-run on every founder; the exact rank-one
identity `M[k][r]M[r][l] = M[k][l]M[r][r]` now holds for all founders, the global sign flip leaves
the object identical, and flipping a single arm changes it.

## D3 — a whole-block distance is undefined across roles

BASIS founders carry four arms (two carriers, +0.50, +0.25); LOCKED founders carry three. A
whole-block quotient distance between founders with different arm signatures is not defined. Pairs
are formed within a role only. Recorded because a naive implementation would have silently
truncated to the shorter block.

## D4 — stratum sub-gates computed after the disposition was already fixed

`FOUNDER_STRATUM_QUOTIENT_STATUS` was forced to `NUMERICALLY_UNRESOLVED` by the
absolute-materiality gate. The leave-one-ancestry-out suite, the maximum-single-cluster share and
the LOCKED transfer of the frozen axis were computed anyway and are reported, because a reader is
entitled to know that every *other* sub-gate passes. They cannot and do not change the
disposition: the gates are conjunctive.

## D5 — the three named raw sources were not sufficient

The handoff named `FSCMA00_LOCKED_RAW_CELL_SCORES.json`, `fscma_probe_raw.json` and
`wsfscrp_q01.json`. The time-resolved LOCKED **carrier** curves are in none of them; they live in
`FSCMA00/fscma_locked_carrier.json`, in the same committed tree. Located by committed provenance
and bound by blob object id, as instructed. No engine was run to reconstruct anything.

## No other deviations

Engine starts: 0, asserted equal before and after Phase 1. No push, no PR, no workflow trigger.
Tommy's checkout was not moved, checked out, merged or modified. No parent output was overwritten.
