# DOTC01 — THE ORGANISER-LEVEL DAUGHTER OBJECT

## Why the old object was not enough

Recomputed from raw FMRT01 bytes: 22 triggered blocks, every one with exactly 2 Y-occupied cells at
maturation, one per centre. The selective intervention removes [1] Y and the global one removes [2].
A single constituent survives the old 250-step window with probability 0.977112 analytically and did so in
20 of 22 observed cases.

```
OLD_DAUGHTER_OBJECT = SINGLE_Y_PARTICLE_WITH_LOCAL_X_FUNCTION
VERDICT             = VALID_LOCAL_SOURCE__INSUFFICIENT_ORGANISER_LEVEL_IDENTITY
```

> the old object is a real, causally efficacious local X source: FMRT01's GLOBAL_OFF arm produced exactly zero X births in the daughter disc while the SELECTIVE arm produced a median of 110. What it does not carry is an identity that could survive replacement of its material, because it has only one constituent.

---

## The new object

no parent-child assignment between Y molecules is invented, asserted or required. The engine keeps no Y tracker and DOTC01 does not create one.

**Centre.** a time-indexed connected component of Y-occupied cells under the frozen centre rule — toroidal single-linkage over Y-occupied cells with adjacency distance <= CORE_R, `CORE_R = 5.0`.

**Identity across steps.** a component at step t+1 continues a component at step t when it is the unique nearest component by toroidal centroid distance in both directions and that distance does not exceed CORE_R. A step at which the match is not mutually unique ENDS the identity interval; it is never resolved by preference.

*so that a fission or a merger terminates an identity interval instead of being absorbed into it.*

**FUNCTIONAL_CONTINUITY_ACROSS_CONSTITUENT_TURNOVER** holds on an interval only if all six conditions hold:

1. C remains spatially coherent under the frozen centre rule at every step in [t0,t1]
2. N_Y_C(t) >= 1 at every step in [t0,t1] — the component never becomes empty
3. at least one constituent-Y REMOVAL event is recorded inside C during [t0,t1]
4. at least one accepted constituent-Y BIRTH is recorded inside C during [t0,t1]
5. centre identity survives those material changes under the persistent spatial matching above
6. the local X organising function remains active across the turnover (see §5)

> a static two-particle centre has more material but has demonstrated no organisational persistence through turnover; a single Y that survives a long time has demonstrated no material replacement. The criterion is the EVENT PAIR inside one continuous identity interval, not a count.

### Removal

a Y decay event recorded inside C (the ydeath ledger)

for a one-cell component the component travels with its own Y, so a hop can never remove that Y from its own component. Once a component has two or more constituents, a constituent moving beyond CORE_R produces a SECOND component: that is centre fission, i.e. centre creation, which §9 requires be kept distinct from turnover. Emigration is therefore counted separately and never as turnover.

### Birth is always inside the centre — structurally

a structural consequence of the frozen law, not an assumption: the Y birth branch of _react_core draws births with probability min(1, kY*nX*nY), which is zero at any cell with nY = 0. Every Y birth is therefore co-located with an existing constituent and is inside that constituent's component by construction.

---

## The turnover event

**COMPLETE_TURNOVER** requires: the component remains nonempty throughout the identity interval; at least one Y removal recorded inside C; at least one accepted Y birth recorded inside C; both events lie inside ONE continuous centre-identity interval.

| Ordering | Admissible |
|---|---|
| BIRTH_THEN_DEATH | True — the centre first grows to at least two constituents and then loses one, so it is never empty |
| DEATH_THEN_BIRTH | ONLY IF N_Y_C >= 2 BEFORE THE DEATH |

**Theorem.** if N_Y_C = 1 and that constituent decays then N_Y_C = 0 and condition 2 fails at that step, ending the identity interval. A centre that begins the interval with one constituent can therefore reach COMPLETE_TURNOVER only through BIRTH_THEN_DEATH. This is a theorem about the frozen law and the definition, not an empirical claim.

every FMRT01 daughter begins with exactly one constituent, so at B1 the ONLY route to complete turnover is a local Y birth followed by a local Y removal.

**PARTIAL_TURNOVER** — an identity interval containing a birth inside C or a removal inside C, but not both. **NO_TURNOVER** — an identity interval containing neither.

---

## Functional continuity

Primary observable: **accepted new X births inside the daughter-centred local functional domain**.

inherited X cannot create a birth event. FMRT01's causal lesson, established with a matched no-source arm, is that local production is diagnostic where absolute local stock is not: the GLOBAL_OFF arm produced exactly zero X births inside the daughter disc in 22 of 22 blocks.

No world-total quantity may enter. MRFA01 classified FMRT01's criterion D as WORLD_SCALE_CRITERION_MISAPPLIED_TO_LOCAL_DAUGHTER because its reference scaled with the whole lattice. No world-total quantity enters this criterion.

No operator-derived floor is transportable: MRFA01 §8 established SINGLE_CENTRE_OPERATOR_NOT_TRANSPORTABLE_TO_DAUGHTER_CONTEXT: only the unblocked kernel is exact, the capacity-constrained operator carries empirical error with no certified bound, and its own r80 = 8.544 exceeds the CORE_R = 5.0 measurement radius. No qualified local floor can therefore be derived, and none is invented.

```
FUNCTIONAL_CONTINUITY_MEASURE = ACTIVE_LOCAL_X_PRODUCTION
```

across the identity interval containing the turnover event pair, the centre records at least one accepted X birth inside its local domain on both sides of the removal event. Zero is the only threshold used, and zero is not a choice: it is the value the matched no-source control takes.
