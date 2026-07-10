# Research Charter

## Current question

Can automatically sampled local laws produce mesoscopic entities whose organization persists under progressive constituent turnover and may later recover after a controlled perturbation?

Working phrase: **persistent dynamical individuality under constituent turnover**.

This phrase is a target for operationalization, not a conclusion.

## Out of scope

No current experiment claims consciousness, AGI, a universal definition of life, autopoiesis, philosophical identity, or a proto-organism. A visually appealing pattern is not evidence.

## Current substrate and causal ladder

1. `CORE V0`: asymmetric attraction/repulsion, short-range collision repulsion, finite range, damping, periodic boundary.
2. `EXP02`: low-discrepancy regime map, 300–500 laws, three screening seeds per law.
3. `EXP03-A`: add density preference only.
4. `EXP03-B`: add orbital/transverse interaction only.
5. `EXP03-C`: add both density preference and orbital interaction.

Mutation, neighbor-induced type changes, and particle recycling remain disabled to preserve causal separation.

## Primary observables

For an auditable lineage at lag `tau`:

- `M(tau)`: Jaccard overlap of diagnostic constituent-ID sets.
- `Phi(E,t)`: ID-independent dimensionless descriptor vector defined in `docs/CORE_V0_PROTOCOL.md`.
- `P(tau) = exp(-RMS(Phi_t - Phi_t+tau))`.

The joint distribution `(P,M)` is retained. No composite identity or memory score is authorized. The quadrant `P>0.8, M<0.5` is only an initial exploratory probe.

## Falsifiability rules

- A trivial baseline or null can invalidate an apparent discovery.
- A tracker-induced candidate is a measurement artefact until controls show otherwise.
- A static motif traversed by new particles is a required high-P/low-M false positive.
- A signal that disappears under frozen fresh-seed hold-out is negative.
- A negative result stays negative; thresholds are not loosened to manufacture candidates.
- Absence before the fixed horizon is right-censored, not proof of impossibility.

## Historical source status

The old repository is read-only. Local commit `9992e6c5149537add3802d1805e8f2c82548442b` was located and audited outside its dirty checkout. Its 19 tests passed in an isolated extraction. Its archived 7,079-row CSV independently yields Pearson `0.675724` and zero rows in the initial `P>0.8, M<0.5` probe. The historical simulation itself was **not** independently rerun, so this remains an audited historical artefact set, not the current baseline.

