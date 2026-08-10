# FSCMA00 -- mode arbitration report

## What was asked, and why the question had to change

The handoff asked me to arbitrate between H1 (one affine 1-D response family transfers across the
carrier repertoire and the +0.5 environmental operator) and H2 (the carrier repertoire is limited
and the environmental operator adds a mode). Both were framed as useful, neither as a failure.

That framing rested on the parent's finding `RANK_ONE_FIXED_SUPPORT_RESPONSE`. I confirmed the
parent's arithmetic exactly -- and then found that the premise does not survive gauge fixing.

## Finding 1 -- the parent's rank-one result is a labelling artefact

The endpoint pair is unordered and canonicalised by sorted site-id lists. That rule is
deterministic but physically arbitrary: it does not link founder to founder. And it is confounded.
`make_founder` assigns `(HIST_H, HIST_L)` on even seeds and `(HIST_L, HIST_H)` on odd seeds, while
the frozen queue makes even seeds FAR and odd seeds NEAR. **Geometry class, history order and
channel label are one axis, not three.**

Fixing that gauge -- by two rules that agree, one of them the handoff's own -- changes the picture:

| quantity | parent frame (ungauged) | gauged frame |
|---|---|---|
| sigma2 / sigma1 | 0.1196 (certified exactly) | 0.3424 |
| lambda2 / trace | 0.0140 -- the gate that **failed** | 0.1035 -- the same gate **passes** |
| lambda1 / trace | 0.9767 | 0.8831 |
| per-cell OFF at k=1 | 0.094 .. 0.266 | 0.194 .. 0.525 |

The response was never rank one. Roughly nine tenths of the leading mode in the parent's frame is
the FAR/NEAR label flip, not dynamics.

## Finding 2 -- H1 is refuted on the carrier repertoire alone

In the gauged frame the affine family `mu + a*phi1` fails its own BASIS tube gate:
`O_BASIS = 0.1169` against a 0.05 threshold, and every
one of the 12 cells exceeds the 0.10 per-cell threshold. On the outcome-unseen LOCKED panel the
same family leaves `OFF_max = 0.5460` at k = 1.

**CARRIER_REPERTOIRE_INTERNAL_DIMENSION_AT_LEAST_2.** The two gauged carrier modes are interpretable: the
first separates the two sentinels (an operator axis), the second separates the two founder strata
identically for both operators (a founder main effect carried by the confound, not an
operator-discriminating mode).

## Finding 3 -- H2 is confirmed on held-out founders

| metric | BASIS | LOCKED (outcome-unseen) |
|---|---|---|
| environmental OFF vs carrier family, k=1 | 0.9991 | 0.9987 |
| environmental OFF vs carrier family, k=4 | 0.1456 | 0.1500 |
| carrier common-mode share | <= 0.1457 | <= 0.1336 |
| environmental common-mode share | >= 0.9687 | >= 0.9710 |

Stability of the environmental direction:

* `cos(BASIS env, LOCKED env) = 0.999765`
* `cos(dose +0.50, dose +0.25) = 0.999613`
* `cos(env, carrier leading mode) = 0.0893` -- about
  84.9 degrees, near orthogonal.

**H2_SECOND_MODE_CONFIRMED_HELD_OUT.**

## Learnability

A predictor fitted on BASIS alone -- the BASIS mean response of the same operator -- reaches a
median exact weighted L1 of 0.0276 of the
operator-agnostic baseline on LOCKED cells, improving in **every** cell. Per arm:
{'CARRIER_1': 0.0276, 'CARRIER_2': 0.017, 'ENV_PRIMARY': 0.0646}. The mode structure
transfers; it is not a per-founder curiosity.

## What does NOT transfer, stated plainly

`J_ENV` at k = 1 is 0.9548: the *direction* of the environmental
mode transfers almost perfectly (cosine 0.9998), but the fine founder-to-founder variation *within*
the environmental arm is not captured by one BASIS-fitted deviation direction. The claim is about
the mode, not about founder-level fine structure.

## A refuted prediction, reported because it was made

P3 predicted that LOCKED orientation would follow seed parity exactly, since parity drives the
history/geometry confound. **It failed on 1 of 6**: founder 64007 (odd, NEAR) required a swap, with
a decisive cosine of -0.9162 -- not a
borderline call. The canonical label depends on the lexicographically smallest site id, which
depends on blob *shape*, not only on which half-plane a body sits in. So the label is even less
trustworthy than the parity story implied. This strengthens the case for gauge fixing rather than
weakening it, but it is a refutation of something I wrote down in advance and it is recorded as one.

## Scope

* Single substrate, single LawSpec, one checkpoint time, one horizon, 12 founders total.
* `CONFIRMATORY_OR_POPULATION_CLAIM = false`. This is a developmental result on a fixed dev panel.
* The LOCKED panel is outcome-unseen but feature-exposed: its checkpoints and masks were generated
  and hashed by the parent.
* `INDEPENDENT_REVIEW = NOT_PERFORMED`. Single executor, sequential, internal procedural locking.
