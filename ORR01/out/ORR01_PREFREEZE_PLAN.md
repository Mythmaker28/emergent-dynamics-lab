# ORR01_PREFREEZE_PLAN — `OCCUPANCY-RATCHET-REPAIR-01`

Written and hashed **before the first confirmation start**. Two cost probes on the manifold
`n[Y] == 0`, where both birth probabilities are identically zero, are the only engine advances
that precede it, together with the bounded score-blind harness.

---

## 0. Provenance, closed first

The inherited repository was a **blobless promisor clone**: 392 objects reachable from HEAD were
missing, though **0** were missing in the `f3921a4..HEAD` range. The remote is readable
(`git ls-remote` succeeds; only push is refused), so the filter was removed and
`git fetch --refetch` materialised everything: **0 missing objects**, `fsck` clean.

A bundle cannot carry a shallow boundary in git 2.43: a bundle produced from a shallow clone
verifies as prerequisite-free and then fails to clone —
*"Failed to traverse parents of commit f3921a4d… remote did not send all necessary objects"*.
Reproduced and recorded. The artefact is therefore a **gzipped bare shallow repository**
(35.7 MB, sha256 `4183e942…d37e30`), and the readback is a real one:

```
extract, git clone the bare repo with GIT_NO_LAZY_FETCH=1 and no network, check out 506272a
HEAD            506272af6815466ca2a25d299281acc8643f94f0
tree hash       4c00ff607cd0cd60532881b80680438e70b40275   identical to the live repository
tracked files   1243        missing objects 0        remotes 0        promisor none
MCM01 tests run from that offline clone: ALL_PASS = True
PROVENANCE_STATUS = SELF_CONTAINED_OFFLINE_READBACK_PASS
```

---

## 1. Question A: what the additive LawSpec actually implies

The enumerator used below reproduces the engine's one-step kernel exactly (differential check:
exact rational kernel over 18 successors, mass 1.000000000000, worst deviation from 40 000
engine samples 0.0058). Four claims were tested separately, and **MCM01 overstated three of
them**.

**The exact identity.** `_diffuse` conserves every species count, `_react` converts one resource
unit into one product unit, `_decay` moves X to waste: all three leave occupancy unchanged. Only
the feed and the outflow change it, so

```
O(t+1) - O(t) = add(t) - out(t)          exactly, one source and one sink
```

and stationarity of the non-waste occupancy gives the sharper statement

```
phi * E[R] = muX*N_X + muY*N_Y           R = total room = SUM min(max(S0-n,0), free)
```

The room the system can hold at stationarity is proportional to **the body's own death flux**,
itself bounded by the conversion flux, itself bounded by `cand_X ≤ 7` per organiser cell.

**Proposition 1 — saturation.** Exact stationary law of the same feed and diffusion rule on a
two-cell ring, started at the protocol's own initial condition (every cell at `S0`), 25 states,
exact rational kernel:

| | mean resource per cell | |
|---|---|---|
| additive feed, two coupled cells | **2.500000000** | 2.5× the set-point `S0 = 1` |
| occupancy-conserving feed, same chain | **1.000000000** | exactly the conserved initial mass |
| additive feed, a single cell | **1.000000000** | exactly `S0` |

So the ratchet is a property of **additivity together with transport**, and of neither alone. It
is *not* monotone convergence to zero free capacity: `P(no room anywhere) = 1` but
`P(both cells full) = 0`. What the chain converges to is a **no-room configuration**, which on a
large lattice sits near capacity and on a small one need not.

**Proposition 2 — what is absorbing.** Exhaustive over the 84 states of a one-cell system with
all six species: of the 56 states at full occupancy, **10 are absorbing and 46 are not**. Every
full state carrying waste or a body molecule re-opens capacity, and an explicit two-step cycle is
exhibited: `(0,0,0,0,0,3) → (0,0,0,0,0,2)` (occupancy 2, capacity re-opened) `→ (0,0,0,1,0,2)`
(full again). The absorbing full states are exactly those with no waste and no body molecule.
**MCM01's "the full state is absorbing" holds only on that sub-space.**

**Proposition 3 — extinction.** `n_X = 0` is invariant and reachable from **all 84** states, so
on a finite lattice the body goes extinct with probability 1 and in a.s. finite time — **for the
additive LawSpec and for every repair of it alike**. Extinction is therefore not a discriminator:
eternal maintenance is not available in this model class, only a quasi-stationary level and a
persistence time, and every claim below is over a stated window.

```
CURRENT_ADDITIVE_LAWSPEC = SCOPE_LIMITED
closed        the feed is additive and drives occupancy strictly above its own set-point until
              no room remains; the stationary room is pinned to the body's death flux over phi
not closed    monotone occupancy; convergence to zero free capacity in general; the full state
              being absorbing; "inevitable extinction" as a property of THIS LawSpec
```

**Is an internal search still justified?** No, and this is decided here, before any change. The
pinning identity is exact and involves no free parameter beyond `phi`; MCM01's 72-point scan
found the criticality requirement and the fill time in direct opposition; and the two exact
overstatements above make the closure *narrower*, not the family *more promising*. The repair is
therefore built as a **separate, versioned LawSpec**, leaving every inherited artefact intact.

---

## 2. Question A bis: the criticality criterion, revised

Exact, on a one-cell system with capacity not binding:

| regime | result | status |
|---|---|---|
| `kX = 1` (what MTW01 and MCM01 actually ran) | the birth law is **identical** for `n_X = 1` and `n_X = 2` at the same `cand_X`: `p_X = min(1, kX·nX·nY)` saturates at `n_X ≥ 1`, so the low-density map is a **step**, not a linear operator | `SCALAR_CRITICALITY = NOT_VALID` |
| `kX = 0.1` | `E[births]` is exactly linear in `n_X` (0.2000000000 and 0.4000000000, ratio 2.0000000000); the coefficients `cand_X` and `n_Y` are themselves random and endogenous, so the growth rate is the **top Lyapunov exponent of a product of random operators**, and the mean-field scalar is its annealed approximation | `SCALAR_CRITICALITY = APPROXIMATE` |

```
CRITICALITY_STATUS = NOT_VALID for the configuration used
MTW01 "supercritical"  ->  BY_PREVIOUS_MEAN_FIELD_CRITERION_ONLY
retained diagnostic: the drift balance E[dN_X | state] = E[births] - muX*N_X, with accepted
births and deaths READ FROM THE FIELD step by step, whose zero gives the quasi-stationary level
N* = E[births]/muX; and the realised persistence over the declared window.
```

`c_X·G(0)` survives only as a descriptive statistic: the expected offspring number of a **single**
body molecule in a **frozen** environment. It is retained inside the gate in the form corrected
by MCM01 addendum C-1 — a mean over the window, never a per-step test — and it is one of nine
conditions, not the outcome.

---

## 3. Question B: the candidate repairs, compared before any run

| id | what it changes | occupancy | admissible |
|---|---|---|---|
| **R0** `ADDITIVE_LEGACY` | nothing; the negative control | `E[dO] = add − out`, unconditional source | no (it *is* the defect) |
| **R1** `REPLACEMENT_FEED_KEEP_OUTFLOW` | the feed becomes a swap, `omega` kept | `E[dO] = −out ≤ 0`: the lattice **drains**. The up-ratchet is replaced by a down-drain | no |
| **R2** `BALANCED_EXCHANGE` | feed **and** outflow replaced by one exchange operator: every unit inserted displaces one unit drawn uniformly without replacement from the cell's exchangeable pool | `E[dO] = 0` **exactly**, cell by cell, step by step | **yes** |
| **R2b** `EXCHANGE_POOL_INCLUDES_BODY` | as R2, but X is in the pool | exact | no — it removes body molecules directly, adding an effective death term: a second change, not a smaller one. Run as a **declared control** |
| **R3** `RESERVOIR_BOUNDARY` | a designated source region exchanges with a reservoir, no bulk feed | exact | no — two operators, a new geometry parameter, and a spatial gradient this question does not need |

**Selection rule, frozen and computed from structure alone**: keep only candidates that conserve
occupancy exactly, carry no outcome feedback, remove no body molecule directly and preserve a
legacy mode; among those take the fewest engine operators modified, then the smallest new
operator by AST node count, then alphabetical order. Ranking:
`R2 → R0 → R1 → R2b → R3`. **Selected: R2_BALANCED_EXCHANGE**, one operator modified.

The mechanism is named correctly throughout: it is a **balanced chemostat / reservoir exchange**,
not a free feed. Matter enters only by displacing matter that leaves.

---

## 4. The new LawSpec, and what is proved about it

`LAWSPEC_V2_EXCHANGE` replaces `_feed_and_outflow` with `_exchange`. The same `phi` is the rate
and the same `S0` is the set-point: **the repair introduces no new parameter.** The exchangeable
pool is `{SX, SY, WX, WY}` — medium and waste, not body — which is what a chemostat exchanges;
the control `WASHOUT_POOL_INCLUDES_BODY` removes that exclusion so the result cannot rest on it.

Proved, not asserted (`code/tests_orr.py`, 24 tests, 4 mutations, 2232 of 8000 bounded steps,
**0 starts**):

```
LEGACY IDENTITY     v2 in v1 mode is the inherited engine, identical state hash at every one of
                    300 steps; the legacy path delegates to K.World._feed_and_outflow, it is not
                    a copy
OCCUPANCY           v2 conserves total occupancy EXACTLY at every step (max |dO| = 0 over 400
                    steps) and cell by cell; the standard deviation of O over a run is 0.0
MATERIAL BALANCE    dN_X = births - deaths exactly, residual 0
BALANCED FLUX       flux in = flux out, 36395 units exchanged, never unequal
CONTRAST            under the same seed and parameters the additive control goes O: 2443 -> 5643
                    (+131 %) in 400 steps
EDGE CASES          empty pool -> no-op; empty source cell -> nothing inserted; full cell ->
                    still exact; one organiser and two organisers -> exact; deterministic under
                    a fixed seed
NO BODY REMOVAL     with the declared pool, units displaced are SX 9419, SY 9364, WX 41, X 0,
                    Y 0; the declared washout control does remove X, as specified
NO OUTCOME FEEDBACK AST: `_exchange` reads no N_X, Q, c_X, success or classification, and
                    indexes only declared species fields
```

---

## 5. The gate, in two independent implementations

Two missions in a row needed a gate corrected after the freeze. The answer is redundancy, not a
cleverer gate. `RuntimeGate` is a **streaming** implementation that sees one step at a time and
keeps counters only; `posthoc_gate` is an **array** implementation that recomputes everything
from the raw series after the fact. Every arm runs both and records agreement; a disagreement is
a protocol failure and stops the mission.

```
PROTOCOL_ADVERSARIAL_AUDIT = PASS
14 declared edge cases, all agreeing, including: c_X intermittent with median 0 but positive
mean (MAINTENANCE_ACHIEVED); c_X intermittent with too small a mean (MATERIAL_COLLAPSE);
a temporary dip (pass) against a long dip (TRANSIENT_FORMATION); disappearance then
reappearance (MATERIAL_COLLAPSE); a second organiser appearing at the evaluated instant (pass,
the ordering defect cannot recur); local saturation, global saturation with a death re-opening a
place, and a uniformly dense lattice (all OCCUPANCY_RATCHET); wrap-around contact
(BOUNDARY_ARTEFACT); N_X = 0 (NO_FORMATION)
108 exhaustive small traces, 0 disagreements
the 8 historical MCM01 arms, 0 disagreements, all classified OCCUPANCY_RATCHET
```

Nine hard conditions, all required, over the whole window `[t_form, t_form + T_MAINT)`:
never `N_X = 0`; at least one organiser at every step (**never "exactly one"**); fraction of
steps with `N_X ≥ N_KEEP` at least 0.95; longest **consecutive** excursion below `N_KEEP` at most
`1/muX`; `mean(c_X)·G(0) > 1`; mean free capacity at the organiser at least `FREE_MIN`;
occupancy drift at most `OCC_TOL`; a main component carrying at least `N_KEEP/2` at every
sample; no wrap-around contact. Classification is exhaustive and mutually exclusive over
`NO_FORMATION, TRANSIENT_FORMATION, MAINTENANCE_ACHIEVED, MATERIAL_COLLAPSE, ORGANISATION_LOST,
BOUNDARY_ARTEFACT, OCCUPANCY_RATCHET, PROTOCOL_VIOLATION, ENGINE_ERROR, UNCLASSIFIABLE`.

---

## 6. The experiment

**The point is fixed analytically and there is no calibration block**: `L = 36, CAP = 16, S0 = 3,
phi = 0.20, omega = 0.05, muX = 0.004, muY = 0, kX = 1, kY = 0, p_hop_X = p_hop_Y = 0.1026`.
It is the analytic winner of the MCM01 frozen rule, reused unchanged so the additive control
reproduces a configuration already measured, and the repair adds no parameter to choose.

**Pairing.** Each seed is run in **both** arms with the same seed and the same initial condition,
and both arms draw the feed or the exchange from a **second** RNG stream, so diffusion, reaction
and decay consume the first stream identically until the states diverge. This changes no rate
and no distribution.

**Horizons.** `T_FORM_MAX = 1250 = 5/muX`; `T_MAINT = 9000`; horizon 10250 steps. The
maintenance window is justified against three timescales: the additive control's measured
saturation time at `phi = 0.20` (about 1300–2500 steps in MCM01) — 3.6 to 6.9 windows; the body
turnover `1/muX = 250` — 36 turnovers; and the local mixing time `ell_X²/D_X ≈ 132` steps — 68
mixing times. A window too short to separate a transient from a maintained cloud is excluded by
construction.

**Budget**, enforced per class by `guard.py`: `cost_probe 2` (spent), `confirmation 12`
(6 paired seeds × 2 arms), `control 8`. Seeds: confirmation `5001…5006`, control `7001, 7002`,
disjoint. Measured cost: 2.72 ms per step for v1, 3.23 for v2; worst case for all 20 remaining
arms, **663 s**.

**Controls**, declared with their predictions: `NO_ORGANISER_V2` (predicted `NO_FORMATION`);
`WASHOUT_POOL_INCLUDES_BODY` (no prediction — it tests the one modelling choice the repair
makes); `SHAM_REINSERT`, which conserves occupancy exactly but puts back precisely what it took
and therefore renews nothing (predicted `MATERIAL_COLLAPSE`, isolating renewal from mere
conservation); `NO_EXCHANGE_AT_ALL` with `phi = 0` (predicted `MATERIAL_COLLAPSE`).

**Sequential rule, frozen.** Stop if: provenance is not self-contained; the closure is
indeterminate; no admissible repair exists; v2 fails an invariance test; the two gate
implementations disagree anywhere; the additive control does not reproduce the ratchet on the
first paired seed; the repair does not remove the ratchet on the first paired seed; no cloud
forms in the repaired arm over the first two seeds; all repaired clouds collapse over the first
three seeds; any logging defect or ledger divergence. Controls run only if at least three
confirmation pairs were executed.

**Success, frozen:** at least **5 of 6** repaired seeds `MAINTENANCE_ACHIEVED` **and** at least
**5 of 6** additive control seeds **not** `MAINTENANCE_ACHIEVED`.

**Disposition rule, frozen.** If the success criterion is met:
`ADDITIVE_LAWSPEC_CLOSED_REPAIR_QUALIFIED`, with `CURRENT_ADDITIVE_LAWSPEC = SCOPE_LIMITED`
reported alongside, since the closure is explicit but narrower than MCM01 stated. If it is not
met but the closure and the repair are sound: `ADDITIVE_LAWSPEC_CLOSED_REPAIR_FAIL`. If the
repair turns out to need a controller, a body injection or a privilege:
`REPAIR_NOT_PRINCIPLED`. The audit dispositions override everything.

---

## 7. What will not be claimed

No reproduction, no reconstruction of identity, no hereditary memory, no individuality, no life,
no confirmation of H3, no global confirmation of Kamimura–Kaneko, no general autonomous
organisation. Permitted: the closure of an additive LawSpec within a defined scope; the removal
of an occupancy ratchet; the establishment of an input–output flux regime; the maintenance of a
cloud over a defined window; the measurement of a growth rate or operator; and the eligibility or
otherwise of a future window mission. **Results obtained under the new LawSpec are never merged
retroactively with MINCORE or MTW01 results.**

```
H3_STATUS = NOT_TESTED, unconditionally, whatever the outcome.
```
