# PARENT_APPEND_ONLY_GAUGE_CORRIGENDUM

    WSFSCRP00_DISPOSITION_REWRITTEN = false
    FSCMA00_DISPOSITION_REWRITTEN   = false
    FSCMA00_H2_STATUS_IN_GIMB00     = REPORTED_PARENT_LABEL_REQUIRING_GAUGE_INVARIANT_QUALIFICATION

Nothing below rewrites a parent. This is an appended qualification.

## The qualification

Both parents computed cross-founder rank statements in a channel serialization that is not fixed by
construction. The serialization sorts site-id lists, which depends on blob shape, and in this panel
it is aliased with history assignment through seed parity. FSCMA00 already showed the numerical
verdict changes under an admissible relabelling. GIMB00 settles what the invariant content is.

## What GIMB00 adds, and what it does not

**Does not:** GIMB00 does not certify that the parents were "wrong", and does not declare the
physical structure to be rank two. FSCMA00 established non-invariance of the old verdict; that is a
statement about the coordinate, not about the dimension.

**Does:** in the exact quotient under the one-swap-per-founder group,

* the certified global optimum over all 32 linked swap assignments is **unique** and is the same
  assignment `[64002, 64006, 64010]` for k = 0, 1 and 2. The FSCMA00 orientation is therefore
  no longer a heuristic: it is the exhaustively certified optimum of a properly posed objective.
* because one assignment is simultaneously optimal at every k, the `R_k` here really are nested and
  `L1`, `L2` do coincide with leading eigenvalues of one fixed matrix. The handoff's warning that
  they need not be singular values remains correct in general; it is moot on this panel, and that
  is proved rather than assumed.
* `QUOTIENT_INCREMENT_RATIO = 0.3423`,
  `QUOTIENT_SECOND_SHARE = 0.1035`. Relative gates QDIM2 and QDIM3
  both pass.
* the one-affine-family gate **fails** (`R1/R0 = 0.1169` against
  0.05), and the two-dimensional gate **passes**
  (`R2/R0 = 0.0134`, worst cell 0.0359).
* that two-dimensional structure **transfers to CARRIER_LOCKED without refitting**
  (aggregate 0.0195, worst cell 0.0487).

## The limit that governs everything

`ABSOLUTE_MATERIALITY_STATUS = NOT_AVAILABLE`. The inherited threshold is a weighted **L1**
quantity; the quotient is weighted **L2**. The only rigorous propagation constant is
`1/sqrt(min_h w_h) = sqrt(18)`, and it reverses **12 of 36** cells the
parents themselves accepted as material -- precisely the twelve CARRIER_1 matched-transposition
cells, whose `||z||/eta_z` lands in [0.610,
0.749]. A bound that unmakes the parents' own accepted responses
is not a compatible restatement of their threshold, and the handoff forbids improvising a tighter
constant.

Consequence, applied without negotiation: **relative structure only, no material claim, and
`PHASE2_LICENSE = NO`.**

## Correction to a sentence in the FSCMA00 report

FSCMA00 described the second gauged carrier mode as "a founder main effect ... not an
operator-discriminating mode". The nested sector attribution here gives
`P_PLUS = 0.4451`, `P_MINUS = 0.5549` -> **MIXED**, stable across every
co-optimal representative. The second mode is not purely common. That sentence is qualified, not
deleted.

FSCMA00 also reported the environmental response as 97-99 % common mode. That figure was the raw
sum-share of the response and is correct as such. The quantity that governs the *relation to the
carrier family* is the sector split of the **off-carrier residual**, which is
`F_PLUS = 0.8848` on ENV_PROBE and 0.8898 on
ENV_LOCKED -- below the 0.95 needed for a common-only label. The invariant label is therefore
`OPERATOR_SPECIFIC_MIXED_EXTENSION`, which is a **smaller and more precise** claim than
"a second mode".
