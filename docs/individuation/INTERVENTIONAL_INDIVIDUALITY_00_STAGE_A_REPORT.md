# INTERVENTIONAL-INDIVIDUALITY-00 — Stage A

## Disposition

**STAGE_A_QUALIFIED — MECHANICAL CODE-ONLY QUALIFICATION FOR HUMAN REVIEW.**

This disposition qualifies only the minimal lattice-bond update, its admissible domain, conservative ledgers,
energy/work identities, deterministic fixtures, and fixed-face coefficient hooks. It establishes no entity,
boundary persistence, memory, history dependence, causal access structure, individuality, autonomy, reproduction,
or scientific response. It does not authorize Stage B, a law search, a seed, a scientific world, regime discovery,
V5/03G modification, merge, or PR.

## Repository boundary

The implementation resides in the generic `emergent-dynamics-lab` repository. Although the primary checkout has a
historical folder name, `pyproject.toml` names the package `emergent-dynamics-lab`, the README title is *Emergent
Dynamics Lab*, and `origin` is `https://github.com/Mythmaker28/emergent-dynamics-lab.git`. A bounded sibling check
found no competing generic checkout. The dirty primary checkout was not modified. An isolated sparse worktree and
branch were created at exact accepted design commit `44d91f0f66473b9f907618556020929656ca862f`.

The attached human mission and every input admitted to the Stage-A implementation and qualification are hash-bound
in the source allowlist. No `results/`, checkpoint, historical outcome, analyzer, prospective namespace, or new
Stage-A scientific run was initiated. A repository-wide regression command was nevertheless run after the focused tests; it
traversed pre-existing seeded/scientific unit-test fixtures outside this mission's synthetic-only allowlist. That is
an evidence-firewall deviation, is recorded below, and contributes no evidence or inference to this qualification.

## Frozen implementation

The exact field/equation registry is committed beside this report. The physical state is only:

- `m[y,x]`: bounded mobile matter in `[0,m_max]`;
- `n[y,x]`: bounded resource and explicit bond fuel in `[0,n_max]`;
- `b[axis,y,x]`: structural bond fraction in `[0,1]` on each positive-y and positive-x face;
- `step`: the scheduler clock.

There is no size parameter, organism class, membrane class/mask, inside bit, component target, tracker, identity ID,
history field, genome, fitness, reproduction function, ownership variable, or scientific response. `b` has only
structural semantics in Stage A. The new human clarification does not predeclare it as memory and also does not
architecturally prohibit separately revalidated future evidence from finding a structural history carrier.

All faces use exactly the same local equations. The bond cue is the product of the two endpoint matter fractions
and their minimum resource fraction; tension is endpoint matter contrast. Neither reads topology, closure,
perimeter, target size, a threshold class, or a detector. The resource permeability remains nonzero at full bond
through the frozen leak floor. Matter conductance reaches zero at full bond. These are mechanics, not entity
criteria.

## Conservative face algebra

For each canonical face from `x` to its positive neighbour `y`, the engine stores one natural matter value and one
resource value:

```text
F_m[x->y] = kappa_m (1-b_xy) m_x (1-m_y/m_max) exp[(A_y-A_x)/2]
J_m[xy]   = F_m[x->y] - F_m[y->x] = -J_m[yx]

p_n(b)    = p_floor + (1-p_floor)(1-b)
J_n[xy]   = D_n p_n(b_xy) (n_x-n_y) = -J_n[yx].
```

The exact stored float contributes `-dt*J` at the canonical source and `+dt*J` at the neighbour. No destination
recalculation, global normalization, reference uptake, world mean, nonlocal correction, or one-sided repair exists.
The independent scalar loop and vectorized path satisfy the repository criterion
`abs(error) <= 1e-12 + 1e-10*abs(reference)` on heterogeneous fixtures.

## Positivity and timestep proof

No output is clipped. Input states outside the compact domain and specifications above the representable frozen
timestep limit are rejected before update.

For matter, four outgoing directed propensities are each bounded by
`kappa_m*m_x*exp(A_span/2)`, and four incoming propensities are each bounded by
`kappa_m*(m_max-m_x)*exp(A_span/2)`. Therefore both nonnegativity and capacity follow from:

```text
dt <= 1 / [4 kappa_m exp(A_span/2)],
A_span = theta_m*m_max + theta_n*n_max.
```

For resource, four outward diffusive contributions are bounded by `4 D_n n_x`. Gross formation on each incident
face is at most `k_on*dt*n_x/n_max`; each endpoint pays half of four faces. Therefore:

```text
dt <= 1 / [4 D_n + 2 epsilon_b k_on/n_max].
```

The default analytic limits are `3.032653298563167` for matter and `1.8181818181818181` for resource/bond fuel.
The accepted representable limit is the one-ULP predecessor `1.818181818181818`; the default `dt=0.05` is safely
inside it. The focused suite tests the limit directly and exhausts all 256 binary `m/n` corner states on a 2×2
torus. Independent red-team stress additionally checked all 26,244 ternary/four-bond-pattern states under the
combined analytic timestep limit without a domain violation. A separate binary-corner scan covered three limiting
parameter regimes.

## Bond energy and work ledger

With `r_on=k_on*Psi`, `r_off=k_off+k_tension*T`, and `r=r_on+r_off`, the exact relaxation is expressed as gross
events:

```text
g_form    = (1-b) (r_on/r)  [1-exp(-r dt)]
g_rupture = b     (r_off/r) [1-exp(-r dt)]
b_next-b  = g_form-g_rupture.
```

The accepted Phase-0 state trajectory debits only net positive bond-energy change from endpoint resource and sends
only net negative bond-energy change to heat. Stage A exposes, but does not add a sink for, simultaneous on/off
turnover:

```text
W_recycled       = epsilon_b min(g_form,g_rupture)
W_form_external  = epsilon_b g_form    - W_recycled
Q_rupture        = epsilon_b g_rupture - W_recycled

gross formation work = W_form_external + W_recycled
gross rupture release = Q_rupture + W_recycled.
```

`W_recycled` is the explicit maintenance-work entry. It is internal and changes no state. Gross rupture release
and external rupture heat are each partitioned by `k_tension*T : k_off` into weakening and baseline-dissolution
entries. This interpretation preserves the accepted `n` and `b` equations exactly; an added maintenance sink or a
gross external fuel debit was rejected during pre-test review as an unauthorized law change.

For every closed step:

```text
sum(m_next) = sum(m)
sum(n_next) + epsilon_b sum(b_next) + sum(Q_rupture)
    = sum(n) + epsilon_b sum(b).
```

Every natural/active/missing face flux, gross event, external fuel debit, recycled work, weakening/dissolution
partition, stored-energy total, heat total, and residual is returned in `StepLedger`.

## Generic face intervention hooks

`FaceIntervention` contains only immutable per-face matter and resource coefficients in `[0,1]`. Plans are fixed
arrays, not state, trackers, moving masks, reservoirs, or boundary conditions. Composition is elementwise
multiplication; binary plans commute and are idempotent. Their arrays are backed by immutable bytes, so NumPy's
write flag cannot be re-enabled after construction.

No plan and the explicit all-one plan travel through the same update and yield byte-identical state and ledger.
A zero coefficient changes only the selected pre-existing transported face value at the first operation. The bond
law is computed from the common pre-step state and is not directly gated. Missing source and destination
contributions are stored as the same magnitude with opposite signs; the controller onset state-energy jump is
exactly zero.

**A face cut manufactures a barrier.** Stage A qualifies only that the manufactured cut is localized, paired,
conservative, and completely accounted. It supplies no evidence of natural autonomy, environmental exclusion,
individuality, or a future admissible scientific instrument.

## Deterministic qualification

The focused suite contains 21 synthetic tests and passes completely. It covers:

- field/domain validation, uniform spatial invariance, and no preferred-size parameter;
- isolated two-cell, periodic, and heterogeneous multi-face exchange;
- scalar/vector agreement, frozen-limit positivity, and exhaustive 2×2 corners;
- formation fuel, gross maintenance recycling, rupture, weakening, dissolution, and heat identities;
- zero/full/intermediate conductance and nonzero full-bond resource leakage;
- exact translations plus rotation/reflection covariance at operation-derived tolerance;
- byte-identical open gates, immutable/composable plans, and symmetric cut accounting;
- explicit dissolution, leakage, percolation, split, and merge constructions;
- an inert static shell and active open pattern that receive no individuality interpretation.

### Evidence-firewall deviation

The repository-wide command `python -m pytest -q` was run once and an attempted repeat was stopped when the
red-team identified that the suite initializes pre-existing scientific/seeded unit fixtures. The completed run had
reported `240 passed, 1 failed`; the historical motile-polar failure was also reproduced at accepted parent
`44d91f0...`. Those commands were outside the mission's synthetic-only evidence allowlist. They are disclosed for
provenance, not treated as Stage-A evidence, and no scientific contrast or inference was computed from them. No
motile-polar or other pre-existing substrate source/test was changed. The admissible qualification evidence is
only `tests/test_lattice_bond.py` plus the independent hand-built lattice stress scan described above.

## Anti-manufacture audit

| Risk | Stage-A evidence | Claim boundary |
|---|---|---|
| Preferred object size | No lattice-size/target/perimeter parameter; identical local states on 4×4 and 8×8 give identical face terms | no size selection exists in the law |
| Tracker influence | Engine API and executable AST contain no detector, tracker, component, ID, or adaptive support | topology/association cannot influence physics |
| Threshold-created membrane class | No threshold exists in engine/spec; fixture-only graph thresholds never enter engine imports | topology fixtures demonstrate representability only |
| Static crystal false positive | Frozen shell is inert and the engine has no individuality detector or criterion | low leakage or persistence alone proves nothing |
| Conductance circularity | Conductance and gated flux are compliance diagnostics only | no directly manipulated quantity may become primary response |
| Manufactured autonomy | A cut is explicitly labelled an artificial barrier and its missing paired flux is logged | no autonomy or environmental-exclusion claim |
| Activity false positive | An active open pattern has nonzero flux with no closed high-bond construction | activity alone proves nothing |
| Memory by declaration | `b` is structural; no writer, experience variable, or history assay exists | Stage A makes no memory claim either way |

Candidate future endpoint families are recorded only as `maintenance`, `recovery`, `internal activity`, `turnover`,
and `downstream response`. None is selected, operationalized, or implemented. Any future primary behavior requires a
separate freeze and cannot be a flux or bond term directly manipulated.

## Independent review and exact next action

The independent reviewer froze anti-manufacture kill switches before inspecting code, separately stress-tested the
admissible domain, reviewed the implementation/fixtures/claims, and found no binding mechanical defect. Its final
journal is part of this package.

The exact next action is **human review of Stage A only**. Qualification does not open Stage B or permit regime
discovery automatically.
