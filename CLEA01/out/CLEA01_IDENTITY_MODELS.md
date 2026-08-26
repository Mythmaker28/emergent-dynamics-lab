# CLEA01 — THE THREE IDENTITY MODELS

Frozen before any pair outcome was read.

## The physics these rules rest on

The frozen within-step order is `diffuse X → diffuse Y → diffuse SX → diffuse SY → react → decay →
feed and outflow`, and a cell row is written **after** the whole step.

**Transport.** `_diffuse` applies `NEI = ((1,0),(-1,0),(1,1),(-1,1))` *sequentially* inside one step,
each pass moving a binomial subset of the current occupancy at most once. Net displacement is a
subset sum of the four unit vectors with the opposing pair cancelling, so the reachable set is
exactly **{−1,0,1}² — the toroidal Moore neighbourhood including self**. A rule built on the von
Neumann 4-neighbourhood would under-count sources and therefore **over-claim** certainty.

The checker verified this three ways: analytically from three engine sources, empirically on 4000
randomised single-cell trials (maximum Chebyshev displacement 1, zero mass escaping Moore-1, all
nine displacements observed), and against the archives (zero invariant violations over ~700,000
rows).

**Births are cell-local.** `_react_core` computes `pair = nX * nY` elementwise. A Y birth *and* an X
birth at cell *d* both require `nY(d) > 0` at react time. The ancestor is a single cell, not a
neighbourhood.

## Model A — LOCKED_SPATIAL_DAUGHTER

The original daughter component, continuing only under the frozen mutual-unique rule at `CORE_R`.
Split, merge, tie, ambiguity or emptiness terminate it. Already qualified in OMLDCT02; CLEA01
computes nothing new for it.

## Model B — AMBIENT_POPULATION

All Y-organising components after the intervention. A **negative specificity control**, not an
acceptable reproduction object. It is the maximal object — the hardest thing to be specific against.

## Model C — DISTRIBUTED_CAUSAL_LINEAGE

Rooted in the locked daughter cells at `t_m`, taken verbatim from the fork ledger — the only seeding
information it receives.

```
S(d, t+1) = { c : c is Y-occupied on row t, toroidal Chebyshev distance to d ≤ 1 }

CERTAIN(t+1)  : d occupied, S(d) non-empty, and S(d) ⊆ CERTAIN(t)
POSSIBLE(t+1) : d occupied, and S(d) ∩ POSSIBLE(t) ≠ ∅
```

The bracket **is** the set-valued causal relation: the ∀ and ∃ quantifiers over the same source
relation. No weight, no threshold, no tuned parameter. A split does not terminate it. A merge with a
non-lineage branch makes a cell POSSIBLE but not CERTAIN — provenance from every contributor,
expressed as a bracket rather than an invented genealogy.

**CERTAIN is provably sound** (established by the checker, not by me): because the kernel is exactly
the reachable set, membership implies all of a cell's Y mass descends from the root. It can
under-claim; it can never over-claim.

Model C reads no online component ID, no identity ID, no verdict, no label, and no future outcome.
