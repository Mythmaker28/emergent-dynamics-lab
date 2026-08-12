```
MISSION       OCCUPANCY-RATCHET-REPAIR-01
DISPOSITION   ADDITIVE_LAWSPEC_CLOSED_REPAIR_FAIL
```

The additive LawSpec is closed within an explicit and narrower scope than MCM01 stated. The
selected repair **removes the occupancy ratchet exactly** and raises the maintained body
population by roughly an order of magnitude, but it does **not** meet the frozen maintenance
criterion, because it uncovers a second, independent obstruction that the ratchet had been
masking: with capacity restored, nothing in the model localises the body cloud.

---

## 1. Provenance and self-contained checkout

The inherited repository was a **blobless promisor clone**: 392 of 2229 objects reachable from
HEAD were missing — **0** of them in the `f3921a4..HEAD` range, which is exactly why MCM01's
packfile check passed and could not see the deficiency. The remote is readable
(`git ls-remote` succeeds; only push is refused), so the filter was removed and
`git fetch --refetch` materialised everything.

A second finding, recorded because it will recur: **git 2.43 bundles do not carry the shallow
boundary.** A bundle produced from a shallow clone verifies as prerequisite-free and then fails
to clone — *"Failed to traverse parents of commit f3921a4d… remote did not send all necessary
objects"*. The artefact is therefore a gzipped **bare shallow repository**, and the readback is a
real one, offline, with lazy fetch disabled and no remote configured:

```
missing objects after repair   0        git fsck --full   clean
HEAD                           506272af6815466ca2a25d299281acc8643f94f0
tree hash                      4c00ff607cd0cd60532881b80680438e70b40275  = the live repository
tracked files 1243   remotes 0   promisor none
MCM01 tests executed from that offline clone: ALL_PASS = True
PROVENANCE_STATUS = SELF_CONTAINED_OFFLINE_READBACK_PASS
```

## 2. Parent, HEAD, branch, commits

| item | value |
|---|---|
| verified MCM01 HEAD | `506272af6815466ca2a25d299281acc8643f94f0` |
| its parent chain | `506272a → 258177a → f3921a4d…` |
| `f3921a4` an ancestor of `origin/main`? | no (`origin/main = f382dbf0…`) |
| ORR01 branch | `codex/occupancy-ratchet-repair-01`, from the verified MCM01 HEAD |
| commits | five, split at the analytical / implementation / freeze / results / report boundaries |
| `kinetics.py` | byte-identical to the frozen MTW01 engine, `d6b9e24d…f026c4c4`, verified by unit test |

## 3. Is the additive LawSpec closed?

`CURRENT_ADDITIVE_LAWSPEC = SCOPE_LIMITED`. The enumerator used below reproduces the engine's
one-step kernel exactly — exact rational kernel over 18 successors, total mass
`1.000000000000`, worst deviation from 40 000 engine samples 0.0058. Of the four claims the
mission was asked to test, **MCM01 overstated three**.

| claim | verdict |
|---|---|
| occupancy rises monotonically | **no.** `O(t+1) − O(t) = add − out`, and `out > 0` whenever waste exists. Monotone only in the resource-only sub-dynamics. |
| convergence to zero free capacity | **no, in general.** The chain is absorbed into a **no-room** configuration. On an exact two-cell ring started at the protocol's own initial condition, `P(no room) = 1` but `P(both cells full) = 0`, the resource settling at **2.5×** its set-point with free capacity still present. On `L = 36` the no-room state does sit at capacity — a large-system property, not a theorem. |
| inevitable extinction of `X` when `muX > 0` | **true, and useless as a discriminator.** `n_X = 0` is invariant and reachable from **all 84** enumerated states, so extinction is a.s. and in a.s. finite time under the additive LawSpec **and under every repair of it**. Every maintenance claim in this project is therefore about a quasi-stationary level over a stated window, never about eternity. |
| impossibility of maintenance | **not implied.** What is implied is the pinning identity below. |

**What is exactly closed.** The feed is additive and drives occupancy strictly above its own
set-point until no room remains; and at stationarity

```
phi * E[R] = muX*N_X + muY*N_Y        R = total room = SUM min(max(S0-n,0), free)
```

so the room the system can hold is pinned to **the body's own death flux**, itself bounded by the
conversion flux, itself bounded by `cand_X ≤ 7` per organiser cell.

**A new exact scope statement.** On a **single cell** the same additive feed stops exactly at
`S0` (exact stationary mean `1.000000000`); with two coupled cells it reaches `2.500000000`;
with an occupancy-conserving feed on the same chain it stays exactly at `1.000000000`. The
ratchet is a property of **additivity together with transport**, and of neither alone.

**What is absorbing.** Exhaustive over 84 states: of the 56 full-occupancy states, **10 are
absorbing and 46 are not**. An explicit cycle is exhibited — a full state carrying waste loses a
unit through the outflow, capacity re-opens, the feed refills it.

**Was an internal search still justified?** No, and that was decided before any change was made:
the pinning identity is exact, MCM01's 72-point scan found criticality and fill time in direct
opposition, and the two corrections above make the closure *narrower*, not the family more
promising. The repair was therefore built as a separate versioned LawSpec, leaving every
inherited artefact intact.

## 4. Exact hypotheses of that closure

Finite lattice; finite per-cell capacity `CAP`; a strictly positive additive feed `phi > 0`
toward a set-point `S0 < CAP`; no matching outflow on the resources; `muX > 0`; birth
probabilities carrying the factor `nX·nY`, so `cand = 0` shuts every reaction down; at least two
coupled cells (the single-cell case is a proved exception); the protocol's own initial condition,
every cell at `S0`. The two-cell and one-cell results are exact rational computations; the
`L = 36` behaviour is the large-system extension, supported by MCM01's residual-zero bookkeeping
and reproduced here in every additive arm.

## 5. and 6. The criticality criterion, revised

```
CRITICALITY_STATUS = NOT_VALID  for the configuration actually used
```

At `kX = 1` — what MTW01 and MCM01 ran — `p_X = min(1, kX·nX·nY)` saturates at `n_X ≥ 1`. With
capacity not binding, the birth law is **identical** for `n_X = 1` and `n_X = 2`. The low-density
map is a **step**, not a linear operator: there is no linearisation about `n_X = 0` and no
branching multiplier. At `kX = 0.1` the map *is* exactly linear (`E[births] = 0.2000000000` and
`0.4000000000`, ratio `2.0000000000`), but its coefficients `cand_X` and `n_Y` are themselves
random and endogenous, so the growth rate is the **top Lyapunov exponent of a product of random
operators** and the mean-field scalar is its annealed approximation — `APPROXIMATE` there, never
exact.

```
MTW01 "the point was supercritical"  ->  BY_PREVIOUS_MEAN_FIELD_CRITERION_ONLY
```

**Retained diagnostic:** the drift balance `E[dN_X | state] = E[births] − muX·N_X`, with accepted
births and deaths **read from the field** step by step, whose zero gives the quasi-stationary
level `N* = E[births]/muX`; plus the realised persistence over the declared window.
`c_X·G(0)` survives only as one of nine gate conditions, in the mean form corrected by MCM01
addendum C-1, never as the outcome.

## 7. and 8. and 9. The repairs, and the one selected

| id | change | occupancy | admissible |
|---|---|---|---|
| R0 `ADDITIVE_LEGACY` | none; the negative control | unconditional source | no |
| R1 `REPLACEMENT_FEED_KEEP_OUTFLOW` | feed becomes a swap, `omega` kept | `E[dO] = −out ≤ 0`: the lattice **drains** | no |
| **R2 `BALANCED_EXCHANGE`** | feed **and** outflow replaced by one exchange operator | `E[dO] = 0` **exactly**, cell by cell | **yes** |
| R2b `POOL_INCLUDES_BODY` | as R2 but X is exchangeable | exact | no — removes body directly; run as a control |
| R3 `RESERVOIR_BOUNDARY` | a source region only | exact | no — two operators, a new geometry parameter |

Selected by a rule frozen before any run and computed **from structure alone**: admissible first;
then fewest engine operators modified; then smallest new operator by AST node count; then
alphabetical. Ranking `R2 → R0 → R1 → R2b → R3`. The mechanism is named correctly throughout:
a **balanced chemostat / reservoir exchange**, in which matter enters only by displacing matter
that leaves. It is not a free feed. The repair introduces **no new parameter**: the exchange
reuses `phi` as its rate and `S0` as its set-point, so no calibration block was run or needed.

## 10. Invariants of the new LawSpec

Proved by test, not asserted — 24 tests, 4 mutations, 2232 of 8000 bounded score-blind steps,
**0 starts consumed**:

```
LEGACY IDENTITY   v2 in v1 mode is the inherited engine, identical state hash at every one of
                  300 steps; the legacy path delegates to K.World._feed_and_outflow
OCCUPANCY         exact conservation at every step, max |dO| = 0 over 400 steps, and cell by cell
MATERIAL BALANCE  dN_X = births - deaths, residual 0
BALANCED FLUX     flux in = flux out, 36395 units exchanged, never unequal
CONTRAST          the additive control on the same seed goes O: 2443 -> 5643, +131 %, in 400 steps
EDGE CASES        empty pool -> no-op; empty source cell; full cell; one and two organisers;
                  deterministic under a fixed seed
NO BODY REMOVAL   displaced units SX 9419, SY 9364, WX 41, X 0, Y 0; the declared washout control
                  does remove X, as specified
NO FEEDBACK       AST: the exchange operator reads no N_X, Q, c_X, success or classification and
                  indexes only declared species fields
```

**The gate exists in two independent implementations** — a streaming one that runs during an arm
and an array one that recomputes from the raw series afterwards. They agreed on 14 declared edge
cases, on 108 exhaustive small traces, on the **eight historical MCM01 arms** (all classified
`OCCUPANCY_RATCHET`), and on **every one of the 22 arms of this mission**.
`PROTOCOL_ADVERSARIAL_AUDIT = PASS`.

## 11. and 12. Freeze and budget

```
METHODS_CORE_HASH = 1cfdb1925f8720b21baff94d68f1ffc03d37042733e174de7920b3a3b949a84d
budget, enforced per class:  cost_probe 2   confirmation 12   control 8
seeds: confirmation 5001-5006, control 7001-7002, disjoint
horizon 10250 steps = 1250 formation + 9000 maintenance
```

The maintenance window is justified against three timescales: the additive control's measured
saturation time (about 1300–2500 steps) — 3.6 to 6.9 windows; the body turnover `1/muX = 250` —
36 turnovers; the local mixing time `ell_X²/D_X ≈ 132` — 68 mixing times.

## 13. Starts consumed

| class | cap | used |
|---|---|---|
| `cost_probe` (on the manifold `n[Y] == 0`, no information extractable) | 2 | **2** |
| `confirmation` (6 paired seeds × 2 arms) | 12 | **12** |
| `control` | 8 | **8** |
| invalid | — | **0** |
| synthetic tests, not starts | 8000 steps | 2232, 0 starts |

Consolidated across the four processes and cross-checked against the arm records on disk:
**22 starts, consistent**.

## 14. The additive control

Six seeds, six times the same result, and it is unambiguous:

```
classification            OCCUPANCY_RATCHET, 6 of 6
occupancy drift           1.6222 to 1.6275
final occupancy           20736 = CAP * L^2 exactly: the lattice is completely full
body population, window mean   0.0 to 16.5
```

The control reproduces the mechanism it was meant to reproduce, in the very conditions in which
the repair is evaluated.

## 15. to 18. The repaired LawSpec

```
occupancy drift  0.00000 on all six seeds, exactly constant, standard deviation 0.0
```

The ratchet is removed exactly, not approximately. Free capacity at the organiser stays at
**8.96 to 9.17** instead of collapsing. The body population over the maintenance window rises
from the additive arm's 0–16.5 to **63.3–123.6**. And yet **0 of 6** seeds reach
`MAINTENANCE_ACHIEVED`.

## 19. Per seed

| seed | classification | occ. drift | `N_X` window mean | free@org | mean `c_X·G(0)` | fraction ≥ `N_KEEP` | longest excursion | condition(s) that failed |
|---|---|---|---|---|---|---|---|---|
| 5001 | `ORGANISATION_LOST` | 0.00000 | 113.9 | 9.17 | 6.85 | 1.000 | 0 | main component carries the mass |
| 5002 | `TRANSIENT_FORMATION` | 0.00000 | 123.6 | — | — | — | — | formation never detected |
| 5003 | `BOUNDARY_ARTEFACT` | 0.00000 | 110.2 | 9.05 | 8.28 | 0.954 | 416 | excursion, main component, wrap-around |
| 5004 | `TRANSIENT_FORMATION` | 0.00000 | 118.6 | — | — | — | — | formation never detected |
| 5005 | `MATERIAL_COLLAPSE` | 0.00000 | 63.3 | 9.02 | 15.66 | 0.627 | 3359 | extinction, fraction, excursion, main component |
| 5006 | `BOUNDARY_ARTEFACT` | 0.00000 | 121.5 | 8.96 | 6.63 | 1.000 | 0 | wrap-around |

The pattern is consistent across seeds and it is not about abundance. Five of the six failures
are **spatial**: the cloud fragments (the main contact component holds 82 of 114 molecules, with
four components and 17 escapees at the last sample), or it spans more than half the torus, or it
never holds a dense enough core for the fifty consecutive steps that formation requires. One seed
(5005) is a genuine collapse. Meanwhile `mean(c_X)·G(0)` sits between **6.6 and 15.7**, far above
1, and the fraction of steps above `N_KEEP` is 1.000 on two seeds.

## 20. Controls

| control | prediction | result |
|---|---|---|
| `NO_ORGANISER_V2` | `NO_FORMATION` | `N_X = 0` throughout, both seeds. The invariant manifold holds exactly. |
| `SHAM_REINSERT` — occupancy conserved exactly, but the operator puts back precisely what it took | `MATERIAL_COLLAPSE` | `N_X` peaks at 45–57 then reaches **0**. Conserving occupancy is **not** what does the work: renewing the medium is. |
| `NO_EXCHANGE_AT_ALL`, `phi = 0` | `MATERIAL_COLLAPSE` | identical, peaks 45–57, final 0. |
| `WASHOUT_POOL_INCLUDES_BODY` | none declared | `N_X` peaks at **7** and reaches 0. Excluding the body from the exchangeable pool is **load-bearing**: a chemostat that also washes out biomass kills this body outright. |

No boundary or domain artefact explains the additive control's behaviour; two repaired seeds
failed *on* the wrap-around condition, which is the artefact check doing its job rather than an
artefact being missed.

## 21. Exact scientific scope

Established: the additive feed drives occupancy above its own set-point until no room remains,
under the hypotheses of section 4, with the single-cell exception proved; the room at stationarity
is pinned to the body's death flux; a balanced exchange operator removes that ratchet **exactly**,
verified as a zero occupancy drift on every arm; renewal, not occupancy conservation, is what
sustains the body, isolated by the sham; and the exclusion of the body from the exchangeable pool
is load-bearing.

Not established, and not claimed: that a body cloud can be maintained in this model family under
the frozen criterion. Not tested at all: H3, the timescale window, reconstruction, reproduction,
heritability, individuality. No result under the new LawSpec is merged with any MINCORE or MTW01
result.

## 22. Next scientific eligibility

`MINCORE-TIMESCALE-WINDOW-02` is **not** eligible: a window mission needs a localised cluster that
can separate into two, and the repaired body is abundant but delocalised.

The next obstruction is now named and it is the one MTW01 declared as a caveat and never tested:
**the model has no cohesive interaction.** With capacity exhausted the cloud could not exist; with
capacity restored it exists and disperses. The candidate repairs are of a different kind from this
one — a short-range attraction between body molecules, a reduced hop rate inside occupied
neighbourhoods, or a birth rule that places the product adjacent to its catalyst rather than in
the same cell — and each is a change to the *reaction and transport* rules, not to the feed. One
of them, chosen the same way as here, is the next mission.

---

```
GOOD_NEWS
The occupancy ratchet is gone, exactly and not approximately: occupancy drift 0.00000 on all six
repaired seeds and on all eight repaired controls, against 1.62 on all six additive seeds, whose
lattice fills to 20736 = CAP*L^2 precisely. The body population over the same window rises from
0-16.5 to 63.3-123.6 and free capacity at the organiser holds at 9.0 instead of collapsing. The
repair is one operator, introduces no new parameter, reuses phi and S0, carries no outcome
feedback, and leaves a legacy mode that reproduces the inherited engine state for state over 300
steps. The controls are clean: the sham that conserves occupancy but renews nothing collapses, so
renewal is doing the work. Provenance is now genuinely closed, with an offline clone, an exact
tree hash and the MCM01 tests running from it. The gate exists twice and the two implementations
agreed on 22 arms, 108 traces, 14 edge cases and the 8 historical arms.

LESS_GOOD_NEWS
Zero of six repaired seeds meet the frozen maintenance criterion, so the repair FAILS as
specified. Removing the first obstruction revealed a second one underneath: the body is abundant
but not localised - it fragments, or spans half the torus, or never holds a dense enough core for
formation to be declared. Three MCM01 statements about the ratchet were overstated and are
corrected here, and "supercritical" is downgraded to a mean-field criterion only. One of my own
sequential rules was implemented more strictly than it was written, and although it was
conservative and could not change the disposition, that is the third mission running in which a
protocol detail had to be corrected after the fact.

CURRENT_ADDITIVE_LAWSPEC
SCOPE_LIMITED

REPAIR_STATUS
FAIL

CRITICALITY_STATUS
NOT_VALID

WHAT_IT_CHANGES
The obstruction moves again, and this time it moves off the feed rule. It is now established that
occupancy conservation is achievable with one operator and no new parameter, and that it is not
sufficient: what limits the body in this family is no longer matter but cohesion. It is also
established that the ratchet, the object of the last two missions, was masking that fact - which
is why MCM01's diagnosis was right about the mechanism and wrong to conclude that removing it
would be enough.

NEXT_SCIENTIFIC_ELIGIBILITY
MTW02 is NOT eligible. The next eligible step is a single minimal, declared change to the
reaction or transport rule that gives the body a cohesive length scale, selected by the same kind
of structural rule used here, with the balanced exchange kept as the feed.

H3_STATUS
NOT_TESTED

SCIENTIFIC_RUNS_USED
22 of 22 capped: cost probe 2 of 2 (manifold n[Y] == 0, no information extractable), confirmation
12 of 12 (6 paired seeds x 2 arms), control 8 of 8, invalid 0. Synthetic tests are not starts:
2232 bounded score-blind steps of an 8000 cap, 24 tests, 4 mutations, 0 starts consumed by the
harness. Consolidated across four processes and cross-checked against the arm records on disk.

PROTOCOL_VIOLATIONS
One, recorded append-only as C-5. The coded form of sequential rule 9 read "no repaired arm
passed" where the written rule reads "all formed clouds collapse"; the clouds had not collapsed,
so the run stopped after three pairs instead of six. The coded rule is strictly more conservative
and cannot inflate a positive result, and the disposition was already determined (5 of 6 is
unreachable from 0 of 3). The written protocol was then completed in full - the remaining three
pairs and all eight controls - and the six-pair result is what is reported. No frozen byte was
edited.

PROVENANCE_STATUS
SELF_CONTAINED_OFFLINE_READBACK_PASS

TOMMY_ACTION_REQUIRED
NONE. The historical visual question from the previous report is recorded as
MINCORE_HISTORICAL_SPATIAL_FAILURE = UNRESOLVED, visual classification NO_VISUAL_DATA: no video,
animation or frame sequence of that run exists anywhere in the workspace or the repository. It is
not blocking and it did not delay anything. If a recording ever does turn up, the one question
worth asking of it is still whether the whole lattice went uniformly dense or a dense cluster
grew on a sparse background - but the ORR01 gate, applied post hoc, already classifies all eight
historical MCM01 arms as OCCUPANCY_RATCHET, which points the same way without needing it.
```
