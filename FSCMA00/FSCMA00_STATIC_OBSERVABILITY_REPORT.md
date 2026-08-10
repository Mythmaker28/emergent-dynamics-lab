# FSCMA00 -- static structural-observability audit

**Zero engine starts.** Nothing in this phase called `engine.step()`. The dynamics were audited by
parsing the engine source, which is a statement about *all* states; the operators were audited by
applying them to checkpoint bytes and diffing. A probe would have told us about one state.

## A. Is a fixed grid-index mask correctly called *Eulerian*?

Criterion: the time-stepping must never re-index the lattice -- neighbour access only by literal
unit offsets, no index-permuting call, no spatial fancy indexing, and no state field rebound to a
permuted copy of itself.

| module | np.roll calls | all shifts literal, abs 1 | permuting calls | spatial re-index | rebinds |
|---|---|---|---|---|---|
| `engine.py` | 12 | True | 0 | 0 | 0 |
| `ppai_engine.py` | 15 | True | 0 | 0 | 0 |

**VERDICT: EULERIAN_FIXED_INDEX_FRAME_CONFIRMED.** The word *Eulerian* is licensed.

Scope caveat, which matters more than the verdict: Eulerian means the control region is fixed in the lattice frame and material flows through it. It does NOT mean the region follows the material that occupied it at t0. q_A(t) is the density integrated over a fixed spatial window, not the fate of the initial material. Any sentence that reads the endpoint as 'what happened to component A' is a Lagrangian reading and is not licensed by this design.

state_cross and reciprocal_cross DO permute lattice indices, but they are applied once at t0 as interventions on the CONTENTS. They are not part of the time-stepping and therefore do not move the frame. The audit above deliberately covers the engine modules only.

## B. One-step dependency matrix, derived from the AST

Def-use reachability over `PPAIEngine.step`; loops iterated to a fixed point, branches unioned.
Sound over-approximation: a listed dependency may be spurious, an **absent** one is provably
unreachable in one step.

| output | one-step input dependencies |
|---|---|
| `rho` | `N`, `U`, `V`, `c`, `rho` |
| `U` | `N`, `U`, `V`, `c`, `rho` |
| `V` | `N`, `U`, `V`, `c`, `rho` |
| `c` | `Mf`, `N`, `U`, `V`, `c`, `rho` |
| `N` | `Mf`, `N`, `U`, `V`, `c`, `rho` |
| `C` | `C`, `N`, `U`, `V`, `c`, `rho` |
| `uptake` | `N`, `U`, `V`, `c`, `rho` |
| `Mf` | `Mf`, `N`, `U`, `V`, `c`, `rho` |

The decisive line: **`rho` depends on `N` in one step (True) and on
`Mf` in one step (False)**. The carrier's only exit is
`z = newm[0] -> kappa(z) -> the face permeability of c and N`, updated at the end of the step, so
`rho` first sees it on the next step.

the earliest scored time is native step 40 (physical 4.0). The order difference above governs steps 1-2 and is NOT directly observable on the scored grid. It is reported as a mechanism, not as a prediction.

## C. Per-operator static audit, 6 BASIS founders

| operator | touch set | consistent | no alias/cache | domain C1+C2 | exact sum preserved | delta support |
|---|---|---|---|---|---|---|
| `S1_matched_transposition` | ['Mf'] | True | True | True | {'Mf': True} | {'Mf': 'subset of A u B'} |
| `S2a_intensive_reflection` | ['Mf'] | True | True | False | {'Mf': False} | {'Mf': 'wide'} |
| `S2b_extensive_reflection` | ['Mf'] | True | True | False | {'Mf': True} | {'Mf': 'wide'} |
| `S2c_total_ablation` | ['Mf'] | True | True | True | {'Mf': False} | {'Mf': 'wide'} |
| `ENV_primary_N_plus_0.50_N0` | ['N'] | True | True | True | {'N': False} | {'N': 'global'} |
| `ENV_secondary_N_plus_0.25_N0` | ['N'] | True | True | True | {'N': False} | {'N': 'global'} |

Intensive and extensive reflection both breach the declared joint domain (see the provenance
audit). Non-conservation of the carrier sum for intensive reflection and total ablation is by
construction, not a defect: those operators conserve the intensive multiset, or nothing.

## D. Intervention input span

Two disjoint native input blocks: **['Mf']** for every
carrier operator, **['N']** for every
environmental operator. **VERDICT: INTERVENTION_INPUT_SPAN_SUFFICIENT.**

Distinctness is proved three ways, not asserted:

1. Every carrier operator perturbs Mf and nothing else, on every BASIS founder (measured bytewise above). Every environmental operator perturbs N and nothing else.
2. The two blocks are therefore disjoint at t0 as SETS OF PERTURBED FIELDS.
3. They are also distinct DYNAMICALLY, not just nominally: by the one-step dependency matrix, rho depends on N within a single step (growth) but not on Mf. Mf's only exit is z = newm[0] -> kappa(z) -> the face permeability of c and N. A carrier perturbation is a multiplicative TRANSPORT-COEFFICIENT perturbation; an environmental perturbation is an additive SOURCE perturbation.
4. Budget asymmetry, which is the sharpest of the three: every carrier operator leaves the nutrient field bit-identical, so it changes the total nutrient budget by exactly zero. The environmental operator adds +amp*N0 at every one of the 4096 sites, so it changes the budget by exactly amp*N0*L^2 > 0. Growth converts N into rho. The environmental operator therefore INJECTS matter into the scored channels; no carrier operator can.
