# R8 — three separately-fireable identity gates (frozen 2026-07-12, D-041)

**Gate order (binding): R7 localization → R8-A → R8-B → R8-C → GATE-0 → law map.**
No R8 metric may be used on a substrate until it has passed **synthetic must-pass AND must-fail** unit cases
(`tests/test_r8_gates.py`, 10 cases, all passing). Four times this session I wrote a criterion that could not fire.
This file exists so that cannot happen again.

**FORBIDDEN identity features, everywhere in R8:** absolute position, total mass, absolute orientation, tracker ID.
Phenotypes must be invariant to translation and rotation before they reach these gates.

## R8-A — diversity
Under the **same global law and environment**, the mean phenotype distance **between** entities must exceed the mean
phenotype drift **within** an entity over time, by a frozen factor **MARGIN_A = 2.0**.
*Must-pass:* three entities with distinct stable phenotypes. *Must-fail:* interchangeable entities (Gray-Scott /
chemotaxis); and entities that differ but wander more than they differ.

## R8-B — predictive identity
A **frozen 1-NN rule whose prototypes are fitted on EARLY states only** must re-identify the same entity at later
times and on held-out trajectories, **despite constituent turnover**. Pass requires accuracy > chance + 0.25.
*Must-pass:* distinct entities re-identified after turnover (modelled as noise plus a drift common to all entities).
*Must-fail:* interchangeable entities (accuracy ≈ chance); entities that start distinct and relax to a common
attractor (identity not predictive).

## R8-C — causal identity
**PRIMARY OUTCOME = identity-specific recovery, NOT entity presence.** A recovered entity counts as *the source*
only if its phenotype is nearer to the **source** prototype than to any other entity's prototype. Intact displaced
cargo must recover **source identity** at a rate exceeding organization-destroyed scrambled cargo by
**MARGIN_C = 0.25**. A scrambled cargo that reconstructs a perfectly good *generic* entity of a *different* identity
counts as a **failure to recover identity** — that is exactly the discrimination this gate exists to make, and the
one whose absence produced the Gray-Scott false positive.
*Must-pass:* intact recovers its own phenotype; scrambled recovers somebody else's (presence identical, identity
not). *Must-fail:* single-attractor substrate — intact and scrambled recover "the source" at the same rate.
*Explicit guard:* an arm that always produces an entity of the **wrong** identity must score **zero** identity
recovery.
