# ARCHITECTURE_HEAD_V4_SPEC.md

**Preregistered before any V4 result.** Replaces the **RETIRED** V3 head (D-058). V3 is preserved unchanged and is
never patched.

## What V3 died of

1. **The intervention's validity was phase-sensitive.** Clearing a component's box clips an in-flight glider at some
   strike phases and leaves a block. **6 of 60 phases (2, 3, 5, 32, 33, 35)** made *every* intervention on the
   development circuit unusable. The head correctly abstained — and so could not identify the architecture at 10% of
   phases.
2. **The "independent" null generator was biased** (`sorted(set(...))[:n]` — sort and truncate), so it structurally
   could not draw phases above 23 and never saw the bad ones.
3. **`A_TAU` could not resolve a delay edit on a gated path.** The evaluator saw the gate→output delay move
   184 → 164; the head reported **185.5 in both**.

Failure 3 *was the D-056 repair*. V3 made timing phase-invariant by taking the **median over all 60 strike phases**.
For an edge whose onset is gated by a **periodic arrival**, that marginal is invariant to exactly the quantity it
exists to measure.

> **The cure for a nuisance parameter is not always to integrate it out.**
> **Integrating it out can integrate out the signal along with the nuisance.**

## The three conceptual changes

### 1. Validity is PHASE-RESOLVED, not per-component

Every `(component, strike-phase)` pair is graded **independently**: VALID / CONFOUNDED / MISSING. The graph is built
from the valid pairs. A phase at which the probe misbehaves now costs **that phase**, not the whole circuit.

Preregistered coverage: a component is **resolved** if ≥ 50% of the cycle's strike phases are VALID for it; a
circuit is **complete** if every component is resolved, every live output has a valid source, and every suppressed
output a valid inhibitor.

### 2. Timing is a phase-resolved PROFILE, made invariant by a GROUP QUOTIENT — never by averaging

For each edge *e*, record the full response profile **τ_e(φ)** over all strike phases, together with the binary
**validity mask** v(φ).

A **global phase shift by φ₀ acts on the data as a common cyclic rotation of *every* profile and of the validity
mask** — settling `φ₀` extra steps and striking at `p` is identical to striking the base circuit at `(φ₀+p) mod T`.

So invariance is obtained by **quotienting by that group action**:

> canonical form = **min over φ₀ ∈ [0,T)** of the concatenation, in an isomorphism-invariant edge order, of every
> profile and the validity mask, all rotated by the **same** φ₀.

This is invariant to the phase origin **by symmetry, not by averaging**. And a **relative** timing change — one
edge's profile shifting while the others do not — **is not a group element**, so no common rotation can undo it and
it **survives**. That is precisely the signal V3 destroyed.

The bad phases are no longer poison: they live in the validity mask, which rotates with everything else and is part
of the signature.

### 3. The null generator is rebuilt, with an executable uniformity assertion

`gt_nulls2` draws phase origins **without sorting or truncating**, and asserts coverage of the full cycle (each
quantile of `[0,T)` is represented). The old bias is not inherited.

## Unchanged, and binding

`A_TOPO` (nodes, directed edges, excitatory/inhibitory role, redundancy, component→component dependency, **modulo
isomorphism**; **no delays, no geometry**) · `A_TAU` (timing only, compared **only after the topology matches**) ·
`G` (layout; auxiliary; **never composited; G is not identity**). Causally **inert** components are excluded from
`A_TOPO` — decoration is not architecture. Interventions remain **whole-component** (a fragment mutilates rather
than removes). `S`, `F`, `L`, `M` are preserved exactly.

## Must-pass / must-fail, restarting certification from scratch

The two cases that killed V3 are now **must-pass**:

- **strike phase 33** (and every other phase) must yield a resolved architecture;
- a **delay edit on a GATED path** must give `A_TOPO = SAME`, `A_TAU = DIFFERENT`.

Plus: pure phase shift → all SAME · translation → all SAME · spacing → `G` only · delay edit on an ungated path →
`A_TAU` only · edge/node added → `A_TOPO` · inert decoration & decoy → no `A_TOPO` movement · under-coverage →
`INDETERMINATE`. Every verdict must fire. Every perfect score carries a non-vacuity assertion.
