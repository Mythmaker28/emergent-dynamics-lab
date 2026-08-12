# MCM01_FINAL_REPORT — `MINCORE-CLOUD-MAINTENANCE-01`

```
DISPOSITION                MINCORE_CLOUD_MAINTENANCE_FAIL
SCOPE OF THE FAILURE       NOT LOCAL. It closes the current model family under the frozen
                           thresholds, for a structural reason: the feed rule is a one-way
                           ratchet on total occupancy.
METHODS_CORE_HASH          0ad009794f7297df289f8e28e65f8518135539a0013c6403eae0d49f7cfd2813
SCIENTIFIC RUNS USED       10 of 26 capped: 2 cost probes, 8 calibration, 0 confirmation,
                           0 control, 0 invalid
H3_STATUS                  NOT_TESTED
PROTOCOL VIOLATIONS        none. One frozen-gate specification defect recorded append-only
                           (C-1); it did not affect the decision and the gate never ran.
```

---

## 1. Byte integrity

Both inherited manifests were re-verified before anything was reused.

| manifest | files | mismatches |
|---|---|---|
| `MTW01_SHA256SUMS` (19 files + bundle) | 20 | **0** |
| `MINCORE_SHA256SUMS` (11 files + bundle) | 12 | **0** |

```
MINCORE_BYTES = INDEPENDENTLY_VERIFIED    MTW01_BYTES = INDEPENDENTLY_VERIFIED
```

## 2. Parent, commits, branch, bundle

| item | value |
|---|---|
| parent of the MTW01 series | `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77` — confirmed, and confirmed **not** an ancestor of `origin/main` (`f382dbf0…`) |
| MTW01 commits | `2b8d20c` (freeze) → `85ba2d8` (results), both recovered from the bundle and byte-identical |
| MTW01 bundle | `22f6bbfac8c0aef94d2b437b00806623d7f6fc7f773996eb0f474f5494cb5ed2` — verified, `git bundle verify` clean, refetched into a fresh clone |
| this mission's branch | `codex/mincore-cloud-maintenance-01`, from the same exact parent |

`kinetics.py` is byte-identical to `MTW01/code/mtw.py`
(`d6b9e24daefd9a9ddd42780fa24da444a344a2773bb7836a8e168e44f026c4c4`), which carries the MINCORE
kinetics unchanged. Verified by a unit test, not asserted.

## 3. `c_X`: the exact definition

`_react` computes `cand_X = min(n[SX], max(free,0))`, `free = CAP − occupancy`, then draws
`births_X ~ Binomial(cand_X, min(1, kX·nX·nY))`.

```
c_X(t) := cand_X evaluated at the organiser's cell, at the reaction sub-step of step t
```

It is literally the `n` parameter of the binomial draw the engine is about to make at the only
cell where body molecules can be created. Integer, per step, strictly local to one cell. It
depends on the free capacity by construction, on the X density through `free`, on the resource
transport that refills the cell, and on nothing else. It does **not** depend on `kX` or `kY`,
because `cand` is computed before the probability is applied.

## 4. Method of measurement

Priority 1 of the required order was achievable, so nothing below it was used. A `RecWorld`
subclasses the frozen engine and overrides `_react` and `_decay` **only to read** the state
immediately before and after each sub-step. It draws no random number and writes no field.

**Proof that the instrumentation does not change the law:** two worlds, same seed, one with the
recorder and one without, have **identical state hashes after 250 steps**. This is a unit test,
not an assertion.

A **certified upper bound** was also derived: a perfectly absorbing cell in a field fed at rate
`phi` toward `S0` draws `c_X ≤ S0/G_S(0)`, with `G_S(0)` the lattice Green's function of the
resource walk at survival `1−phi`, by convergent quadrature. The linearised feed, the neglect of
exclusion and the perfect sink all make it an upper bound, so the gate is never flattered.

## 5. Result of the measurement

`c_X` was measured exactly, at four points, on two calibration seeds each — 8 starts, the full
class cap. The measurement succeeded: the disposition is **not** `MINCORE_CX_UNRESOLVED`.

| point (`muX`, `phi`, `ell_X`) | `c_X` certified | `c_X` median | `c_X` mean | `A = c_X·G(0)` certified | `A` from the mean | measured/certified |
|---|---|---|---|---|---|---|
| 0.004, 0.20, 2.5 | 0.818 | **0.000** | 0.386–0.561 | 8.02 | 3.79–5.50 | 0.47 |
| 0.004, 0.40, 2.5 | 1.370 | **0.000** | 0.345–0.354 | 13.44 | 3.38–3.47 | 0.25 |
| 0.004, 0.40, 3.0 | 1.440 | **0.000** | 0.337–0.434 | 10.57 | 2.47–3.19 | 0.23 |
| 0.002, 0.10, 2.5 | 0.423 | **0.000** | 0.226–0.241 | 8.15 | 4.35–4.65 | 0.53 |

`c_X` is a small intermittent integer: its median is exactly 0 and it is at or above 1 in only
19 % to 40 % of steps. The full required distribution is stored per arm: min, 5th and 25th
percentiles, median, mean, max, value at formation, value before collapse, fraction of steps with
`c_X·G(0) > 1`, longest consecutive run above 1, and the mean organiser-cell occupancy `u`.

Two things follow immediately. First, the certified transport bound over-predicts the realised
`c_X` by a factor 1.9 to 4.3 — it is an upper bound and it behaves like one. Second, and against
the design intuition, **the ratio gets worse as `phi` rises**: 0.53 at `phi = 0.10` down to 0.23
at `phi = 0.40`. Raising the feed does not raise `c_X`; section 7 explains why.

## 6. `1519` versus `190`, resolved

Both numbers are the same quantity — the left-hand side of the window non-emptiness condition at
the frozen MINCORE point — under two conventions for the separation time.

```
tau = Delta^2 / D_Y          (the convention of the first MTW01 evaluation)   ->  1518.6
tau = Delta^2 / (8 * D_Y)    (the exact 2D first passage)                     ->   189.8
ratio                                                                          ->     8.0000
with the corrected D_eff = q(1-q)                                              ->   180.4
```

The ratio is exactly **8**, the first-passage correction and nothing else. `1519` appeared only in
an intermediate console evaluation of MTW01 and is superseded; the MTW01 final report already
quotes the corrected value. **The traceable final value is 180.4.** In every convention the
window at the frozen MINCORE point is empty by two to three orders of magnitude, so no
conclusion depends on the choice.

Three further inherited claims were corrected in passing (`D = p_hop/4` → `D_eff = q(1−q)`;
`cand_X ≤ S0` is false, the exact cap is 7; `Q_max = 27` → **28**), and one diagnosis was
reversed: **the MTW01 design point was supercritical**, `c_X·G(0) = 2.53`. Full list and reasons
in `MCM01_APPEND_ONLY_CORRECTIONS.md` C-2.

## 7. State of the constraints, and the mechanism

Three constraints had to hold together. Two of them are in **direct opposition**, and that is the
finding.

**The material constraint is not what was written.** `n[SX]` is not bounded by `S0` — `_diffuse`
accepts `min(movers, dest_free)`, capped by free capacity, not by `S0`. The exact bound is
`c_X ≤ 7` and hence `N_X ≤ 7/muX` per organiser.

**The dynamic constraint is exactly classified.** `A = c_X·G(0)` is the mean offspring number of a
lone body molecule sitting with the organiser. It is **necessary and sufficient** for
supercriticality of the linearisation about `N_X = 0`; **necessary but not sufficient** for
persistence, because the source saturates at `cand_X` once `nX ≥ 1`, capping the quasi-stationary
population at `c_X/muX`; it is **local, linearised**, rests on a Poisson closure and on the
free-walk `G(0)`, and ignoring exclusion makes particles more mobile, so the computed `G(0)` is a
**lower** bound and the test is conservative. It is not merely heuristic.

**The mechanism: the feed rule is a one-way ratchet on total occupancy.** Let
`O = Σ (nX+nY+nSX+nSY+nWX+nWY)`. Then, exactly:

```
_diffuse   conserves every species count            O unchanged
_react     converts one resource unit into one product unit    O unchanged
_decay     X -> WX, Y -> WY                          O unchanged
_feed      adds  a = Binomial(min(max(S0-n,0), free), phi)     O up
_outflow   removes o = Binomial(n[W], omega)                   O down
=>  O(t+1) - O(t) = a(t) - o(t)     EXACTLY
```

This identity was verified on the raw series of all eight arms with **residual exactly 0**, as
was the material balance `ΔN_X = births − deaths`.

`O` has exactly one source and one sink. The sink is fed only by decay of X and Y, which exist
only because resources were converted, and conversion requires `cand = min(n[res], free) > 0`,
hence `free > 0`. The source is strictly positive in expectation whenever any cell holds fewer
than `S0` resource units and has free capacity — and diffusion keeps producing such cells,
because a binomial exchange between neighbours has positive variance at every step. So `O` rises
until `free = 0` everywhere, at which point `cand ≡ 0`, no reaction can fire, the body cloud
decays away, the waste drains, and the state *"every cell filled with resource, no body
molecules, no production"* is reached — where `a = 0` and `o = 0`. **It is absorbing.**

The data show exactly this, at every point, from the first step:

| | start | end |
|---|---|---|
| mean SX per cell | 3.0 | 7.79 – 7.99 |
| mean SY per cell | 3.0 | 7.95 – 7.99 |
| free capacity per cell | 9.9 | 0.04 – 0.23 |
| free capacity at the organiser | 1.5 – 1.9 (first block) | 0.04 – 0.24 (last block) |
| `c_X` at the organiser | 0.35 – 1.02 | 0.04 – 0.13 |
| sustainable `N_X` = births/`muX` | 141 – 195 | 0 – 48 |
| realised `N_X` | rises to 113 – 132 | 4 – 42 |

The two resources converge to `CAP/2 = 8` per cell each and fill the lattice exactly. There is no
"formation phase then collapse phase": free capacity declines **monotonically from step 1**, the
sustainable population declines with it, and `N_X` rises to meet its own falling ceiling and then
follows it down. The figure `mcm01_ratchet.png` shows this, together with the final fields: a
compact but starved cloud around the organiser, on a uniformly saturated lattice.

The feed rate law confirms the mechanism quantitatively. `E[add]` per cell, **divided by `phi`**,
plotted against the free capacity per cell, **collapses onto one curve** across `phi = 0.1, 0.2,
0.4` (spread max/min = 2.6, concentrated in the sparsest bins). That is the signature of
`add = Binomial(room, phi)` and of nothing else.

This is also why raising `phi` backfires. A larger `phi` raises `n[SX]` but fills the lattice
faster, and `c_X = min(n[SX], free)` is limited by **`free`**, not by `n[SX]`: at the organiser
the measured `n[SX]` is 1.24 to 4.70 while `free` is 0.13 to 0.34. The binding term is capacity,
and the species that consumes it most is `SY`, which at `kY = 0` has **no sink at all** and rises
to 7.1–8.2 units per cell.

## 8. The selected point, and the rule that selected it

The frozen rule: *among the points satisfying every analytic constraint, take the minimum
predicted `T_run`; break ties by the ascending lexicographic order of `(muX, phi, ell_X, rho_Y)`.*
It was applied to the 40-point grid before any run: 8 points admissible, the four cheapest
entering calibration in that order. After calibration the **same rule** was re-applied with the
measured `c_X`.

```
survivors under the frozen rule (declared median pooling)  :  0 of 4
survivors under the alternative mean pooling               :  0 of 4
=> sequential stopping rule item 3 fires: STOP
```

**No point was selected.** The conclusion is invariant to the pooling choice, which matters
because the median of an intermittent integer is a poor statistic — a defect recorded in C-1.

## 9. The frozen budget, and 10. what was actually spent

| class | cap | used | what for |
|---|---|---|---|
| `cost_probe` | 2 | **2** | timing on the manifold `n[Y] == 0`, where both birth probabilities are identically zero, so no information about maintenance can be extracted |
| `calibration` | 8 | **8** | 4 points × 2 seeds, in the frozen order |
| `confirmation` | 6 | **0** | blocked by sequential rule 3 |
| `control` | 10 | **0** | blocked by sequential rule 7 (controls require ≥ 3 confirmation seeds) |
| invalid runs | — | **0** | |
| synthetic tests | not a start | 501 steps of 6000 | 24 tests, 10 mutations, harness ledger asserts 0 starts |

Ledger sequence consistency: verified by the guard's own audit. Seeds: calibration (1001, 1002),
confirmation (2001–2006, unused), control (3001+, unused) — disjoint by construction.

Measured cost: 1.63 ms per step at `L = 36`. Projected worst case for the whole mission, every
start of every class: 195 s. Actual: 39 s of calibration.

## 11. Formation, and 12. maintenance

**Formation succeeded everywhere.** All eight calibration arms formed a cloud, at steps 68 to
450, reaching `N_X = 113` to `132` and an organiser-cell occupancy `u = 3.0` to `7.7`.

**Maintenance was not achieved and was not measured by the frozen gate.** The mission stopped
before the confirmation block, so the persistence gate was never applied to real data. What the
calibration arms show — with the caveat that calibration arms can never be counted as
confirmation — is a monotone decline of the sustainable population from the first block onward,
ending at `N_X = 4` to `42` from peaks of 113 to 132.

## 13. Per seed

| point | seed | formed at | `N_X` mean over the window | `u` | `c_X` mean | `A` from the mean |
|---|---|---|---|---|---|---|
| 0.004 / 0.20 / 2.5 | 1001 | 135 | 78 | 3.78 | 0.561 | 5.50 |
| 0.004 / 0.20 / 2.5 | 1002 | 450 | 65 | 3.03 | 0.386 | 3.79 |
| 0.004 / 0.40 / 2.5 | 1001 | 153 | 83 | 5.60 | 0.345 | 3.38 |
| 0.004 / 0.40 / 2.5 | 1002 | 99 | 82 | 5.31 | 0.354 | 3.47 |
| 0.004 / 0.40 / 3.0 | 1001 | 68 | 79 | 3.37 | 0.434 | 3.19 |
| 0.004 / 0.40 / 3.0 | 1002 | 226 | 73 | 4.32 | 0.337 | 2.47 |
| 0.002 / 0.10 / 2.5 | 1001 | 141 | 98 | 7.23 | 0.241 | 4.65 |
| 0.002 / 0.10 / 2.5 | 1002 | 150 | 106 | 7.74 | 0.226 | 4.35 |

Seed-to-seed spread is modest and never straddles the threshold: the largest `A` observed
anywhere is 5.50, against the frozen requirement of 8.

## 14. Artefacts

None found, and two were specifically excluded. **Boundary:** the domain is a torus, the
component analysis wraps, and the final clouds have extent far below `L/2`; no wrap-around
contact occurred. **Instrumentation:** proven not to change the law by state-hash equality.
**Arithmetic:** the occupancy identity and the material balance both close with residual exactly
0 on all eight arms. The one defect found is in the frozen gate's *form* (C-1) and it did not
touch the decision.

## 15. Exact scope of the result

A 72-point scan over `muX ∈ [5·10⁻⁴, 0.016]`, `phi ∈ [0.01, 0.40]`, `ell_X ∈ {2.5, 3.0}`,
combining the **certified** criticality with the **measured and phi-collapsed** fill law, finds:

```
points satisfying the certified criticality AND outliving the ratchet by a factor 3 :  0 of 72
best fill margin among points with A_certified >= 8                                 :  0.303
best A_certified among points that outlive the ratchet                              :  2.62
```

The two requirements pull in opposite directions: criticality wants a strong feed, and a strong
feed fills the lattice. **The failure is therefore not local to the tested point; it closes the
family under the frozen thresholds.**

What is exact, and what is not, stated separately:

```
EXACT       O(t+1) - O(t) = a(t) - o(t), with one source and one sink
EXACT       the full state (free = 0 everywhere, no waste) is absorbing: a = 0, o = 0, cand = 0
EXACT       the sink requires free > 0 to exist at all, so it cannot outrun the source
EXACT       c_X <= 7 at CAP = 16 ; Q_max = 28 ; D_eff = q(1-q)
CERTIFIED   c_X <= S0/G_S(0) by convergent quadrature, an upper bound
MEASURED    the fill rate law E[add] = phi * g(free), collapsed across three values of phi
NOT PROVEN  that no parameter point whatsoever escapes; the scan is a grid, and the fill law is
            calibrated, not derived
```

## 16. Next scientific eligibility

A `MINCORE-TIMESCALE-WINDOW-02` is **not** eligible. The body cloud does not persist, so there is
nothing to divide. Nor is a further parameter search inside the family worth a budget: the
obstruction is the feed rule itself.

The obstruction is precise and so is the class of repairs. Occupancy needs a sink that does not
depend on the reaction. Candidates, each a **structural modification of the LawSpec** and
therefore outside the current family:

1. give the resources their own outflow, `omega_S`, so `O` has a sink independent of conversion;
2. make the feed a *replacement* (`n[s] ← S0`) rather than an addition, removing the ratchet at
   its root;
3. exclude the unconsumed resource from the occupancy that defines `free`, so it stops competing
   for capacity;
4. decouple `cand` from `free`, making the reaction resource-limited rather than capacity-limited.

Option 2 is the smallest change that removes the mechanism exactly, and option 1 the smallest
that leaves the feed rule intact. Either would need its own mission, its own freeze, and a
re-derivation of `c_X` and of the window, since both depend on `free`.

---

## 17. The six questions

1. **Does `c_X` finally have an auditable definition and measurement?** Yes. It is
   `min(n[SX], free)` at the organiser's cell at the reaction sub-step — the binomial `n` of the
   engine's own draw — read by an instrumentation proven not to change the law, with a certified
   upper bound alongside.
2. **Is `c_X·G(0) > 1` satisfied over a relevant duration?** In the sense that decides
   persistence: `A` is between 2.5 and 5.5, above 1 but **below the frozen threshold of 8** at
   every point; and it declines throughout the run rather than holding.
3. **Does the cloud maintain itself?** No. It forms at every point, reaches 113–132 body
   molecules, and then declines monotonically with its own falling sustainable level.
4. **Is there a pre-registered point satisfying window, material and maintenance constraints
   together?** No. 0 of 4 calibrated points survive the frozen rule; 0 of 72 scanned points
   satisfy criticality and outlive the ratchet.
5. **Is any point robust enough to authorise a window mission?** No.
6. **Must one conclude that the current family cannot achieve maintenance without structural
   modification or prohibitive cost?** Yes, under the frozen thresholds — and for an identified,
   exactly verified reason rather than a budget one. Cost was never the obstacle: the whole
   mission ran in 39 seconds.

---

```
GOOD_NEWS
c_X now has an exact, local, auditable definition and a measurement that provably does not
perturb the law, together with a certified upper bound that predicted the MTW01 population to
33.5 against 35 recorded, with no free parameter. The failure mode is no longer a mystery: the
feed rule is a one-way ratchet on total occupancy, the identity O(t+1)-O(t) = a - o closes with
residual exactly 0 on all eight arms, and the full-lattice state is absorbing. Body clouds do
form, reliably, at every point tested. The 1519 versus 190 divergence is resolved exactly: a
factor 8, the two-dimensional first-passage correction.

LESS_GOOD_NEWS
The cloud is not maintained, at any of the four calibrated points, and the frozen rule selected
no point at all. Four claims inherited from MTW01 were wrong and had to be corrected, including
one diagnosis that was backwards: the MTW01 point was supercritical, not subcritical. One frozen
gate of this mission was itself malformed - a pointwise test on an intermittent integer whose
median is 0 - and although it did not touch the decision, it is the second mission running in
which a gate had to be corrected after the fact. Confirmation and control blocks were never run,
so 16 of 26 capped starts are unspent and the persistence gate has still never been exercised on
real data.

WHAT_IT_CHANGES
The obstruction moves from the parameters to the LawSpec. No amount of tuning inside the current
family will maintain a body cloud, because the feed adds occupancy unconditionally while the only
sink runs through a reaction that free capacity switches off. This also supersedes the MTW01
diagnosis: what killed that cloud was not subcriticality but the same ratchet, seen earlier and
misread. It very probably also explains the MINCORE stop labelled "fills the domain" - which,
if so, was the lattice filling with resource, not a cluster growing.

NEXT_SCIENTIFIC_ELIGIBILITY
A window mission is not eligible, and neither is a further parameter search. The next eligible
step is a single, minimal, declared structural modification giving occupancy a sink independent
of the reaction - the smallest being a feed that replaces rather than adds - followed by a
re-derivation of c_X and of the window, both of which depend on free capacity.

H3_STATUS
NOT_TESTED

SCIENTIFIC_RUNS_USED
10 of 26 capped. cost probe 2 of 2 (manifold n[Y] == 0, no information about maintenance),
calibration 8 of 8, confirmation 0 of 6, control 0 of 10, invalid 0.
Synthetic tests are not starts: 501 bounded score-blind steps of a 6000 cap, 24 tests,
10 mutations, harness ledger asserts 0 starts consumed.

PROTOCOL_VIOLATIONS
NONE. One specification defect in a frozen gate is recorded append-only as C-1: the criticality
condition was transcribed as a per-step test although it is derived as a statement about a mean.
It did not affect the decision - both poolings give 0 survivors - and the gate never ran on real
data. It is corrected forward, not retroactively; no frozen byte was edited.

TOMMY_ACTION_REQUIRED
One bounded visual check, and only because it is genuinely cheaper and more reliable than any
audit chain I can run. In the MINCORE run that stopped with FIRST_SOURCE_CLUSTER_TOUCHES_WALL_OR
_FILLS_DOMAIN, the saved output is a single descriptor with no time series, so I cannot tell
whether "filling the domain" meant the cluster growing or the lattice filling with resource.
If you still have a video, an animation or any frame sequence of that run:

  does the whole lattice go uniformly dense - including far from the cluster - or does a dense
  cluster grow on an otherwise sparse lattice?

The attached figure mcm01_ratchet.png shows what the first case looks like here: the right-hand
column is the free capacity, saturated everywhere, while the body cloud in the middle column is
small and centred on the organiser. A yes to "uniformly dense everywhere" would confirm that
MINCORE, MTW01 and MCM01 all stopped for the same single reason; a no would mean MINCORE failed
differently and that would need its own line of work. Either answer is useful; no other action
is required, and nothing about Git, branches, commits or bundles needs anything from you.
```
