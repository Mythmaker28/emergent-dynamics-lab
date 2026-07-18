# Stage-A independent adversarial review journal

- Role: independent adversarial reviewer
- Run ID: `RUN-20260718-2022-CAA01-A-REDTEAM`
- Start: 2026-07-18 20:22:03 +02:00
- End: IN PROGRESS
- Starting branch: `codex/causal-addressability-architecture-01-stage-a`
- Starting HEAD: `9ec894fbeba7ec2974a917a182d152e9d8074431`
- Starting Git state: untracked main Stage-A journal only
- Assigned scope: independently derive the first E-accessible horizon and exhaustive existing-edge inventory before fixture-output inspection; then adversarially audit only the isolated Stage-A implementation, deterministic fixtures, qualification evidence, accounting, and claim boundaries.

## Evidence firewall

Forbidden and not opened: `results/`, raw or scientific worlds, DEV outcomes, checkpoints, seeds, 500xx/570xx/580xx paths, V5/03G, scientific analyzers, prospective namespaces.

The reviewer will use only the accepted Phase-0 report/spec/source allowlist, the durable project governance files required by `AGENTS.md`, the exact allowlisted frozen source files necessary to derive equations, and newly created Stage-A code/tests/reports after the static derivation is frozen below.

## Static derivation (must precede fixture-output inspection)

### Exact update order and first E-accessible horizon

The frozen `MultiChannelMemoryEngine.step` order is:

1. evaluate signed face fluxes from old `rho,c` and transport old `rho,U,V,C,Mf`;
2. evaluate target uptake from transported `rho,U,V,Mf`, old/current `N`, and `m_plus`;
3. apply local inheritance and homogeneous death;
4. update `U,V` toggle reaction and neighbour diffusion;
5. compute alive mask, world-global uptake reference, local writer, memory templating/diffusion, and clipping;
6. update `c` from old `c`, old `rho`, and newly written `m_minus`;
7. update `N` from post-uptake `N`, neighbour post-uptake `N`, and the local reservoir;
8. return the state with clock incremented once.

Let `t0` be capture after any common reset and before a common exogenous probe contribution `P(t)`. The committed
report and spec do **not** authorize lazy first-use capture: every `r_p` is captured at the common pre-probe state,
and they explicitly define `S_B0=sum a_x(t0)*uptake_x(t0)` and `n_B0=sum a_x(t0)`. An earlier reviewer inference
that derived within-step references could instead be captured from the first update is retracted. That would be a
different environmental port and is forbidden by this mission.

This exact reference convention creates a fatal update-order contradiction. Old-state boundary parents used by
face transport do equal their references on update 1, so target uptake itself is E-invariant on update 1. But later
within that same frozen update the engine reads newly derived external parents:

- post-transport external `u,v` enter target toggle diffusion;
- post-growth/death external `m` enters target memory templating/diffusion;
- current-step external uptake and alive status enter target `up_ref`;
- post-uptake external `N` enters target nutrient diffusion.

Those parents generally differ from their pre-probe references during update 1. Exact `e=0` therefore holds them
to stale `t0` values while `e=1` reads the current derived values. A purely symbolic counterexample needs no fixture:
for a boundary outside cell with nonzero first-update uptake `g_B`, open nutrient diffusion reads
`N_B'=r_N+P(t)-g_B`, while held E reads `N_B^E=r_N+P(t)`. The target returned `N` differs by the corresponding
nonzero `dt*D_N*g_B` boundary contribution. Similarly, unless coincidentally equal, stale `S_B0,n_B0` change
`up_ref`, `Psi`, and returned target `Mf` on update 1.

Thus there is no single admissible `H*` satisfying the committed obligations:

- for the first-update uptake-only diagnostic, E is inactive and the earliest E effect on uptake can be update 2;
- for the returned state and the exhaustive E-to-response graph, E is already active at update 1, so
  `H*_whole_state=1`.

The Stage-A mission explicitly requires structural E inactivity and first-update E invariance, not merely uptake
invariance. The exact committed port fails those static gates. Deferring E activation or capturing derived
first-update sufficient statistics would repair the contradiction only by inventing a new environmental port after
failure, which is expressly prohibited. This alone compels `STOP_ARCHITECTURE` before fixture tuning.

### Exhaustive existing E-parent inventory for the failed intended H*=2 design

For fixed target support `Omega`, the committed E port must substitute every outside-neighbour parent read into a
target destination, for both periodic axes and both sides of every boundary face, regardless of realised flux sign.
The inventory is:

1. **Face-flux parents:** outside `rho` and `c` in `dc`, saturating `chi`, upwind selection, crowding, and `D_rho`
   diffusion. Both variables affect the scalar face flux even when the outside cell is not the material donor.
2. **Transported donor parents:** outside `U/rho`, `V/rho`, every cohort component `C/rho`, and every memory
   component `Mf/rho` wherever the frozen sign selects the outside donor. Sign selection itself remains the frozen
   function of the gated `rho,c` parents.
3. **Toggle-neighbour parents:** outside post-transport `U/rho` and `V/rho` entering target `lap(u)` and `lap(v)`;
   target alive and reaction parents stay local.
4. **Memory-neighbour parents:** outside post-inheritance/death `Mf/rho` entering target `_tmean(mk)` and `lap(mk)`
   for both memory components; writer decay and target alive remain local.
5. **Attractant-neighbour parents:** outside old/current `c` entering target `lap(c)`. Target `rho0`, decay, and
   `m_minus` production are local persistent/body paths and are not reclassified as E.
6. **Nutrient-neighbour parents:** outside post-uptake `N` entering target `lap(N)`, decomposed exactly as
   `r_N + P(t) + e*(N-r_N-P(t))`. The common exogenous `P(t)` is identical in all arms. The target reservoir is
   recomputed as `F*(N0-N_target)` and is never independently held.
7. **World-global writer parent:** the external contribution to `up_ref`, including both uptake numerator and alive
   denominator. It must obey `S_B^E=S_B0+e*(S_B-S_B0)`,
   `n_B^E=n_B0+e*(n_B-n_B0)`, and the frozen empty-set rule in
   `up_ref^E=(S_A+S_B^E)/(n_A+n_B^E)`; holding the numerator alone is incomplete.

There is no E gate on persistent target `rho,U,V,C,Mf,c,N`, target body dynamics, target geometry, `eta_w`, the
local reservoir, the common probe, outgoing target-to-environment destination updates, or the clock. `C` is in the
transport inventory even though it is diagnostic/passive because incomplete boundary transport would violate
state and conservation identity. The inventory is exhaustive for the allowlisted frozen equations only; adding an
engine path later invalidates it.

### Arm compilation and clone order frozen before fixtures

`Y^a(l,e)` uses `L0E0/L1E0/L0E1/L1E1`, with `1=open`. Capture one exact `t0` state and immutable mask/reference
bundle, then make four same-source deep copies before any arm runs. Canonical execution order may be fixed for
serialization, but every permutation must return byte-identical per-arm outputs. Compile E and L controls from
immutable inputs; their controllers commute. `q_L=0` deletes only the pointwise first-update
`lam_plus*m_plus` multiplicative contribution and automatically reopens for update 2. E remains active for updates
1 and 2. No tracker, diagnostic ID, response, or prior arm may modify support or control state.

The later `Y_i^k(k_A,k_B)` cut namespace, where `1=cut`, is absent from this implementation and evidence package.

### Accounting identities frozen before fixtures

For each extensive transported channel `X in {rho,U,V,C[k],Mf[k]}`, let `F_X,f` be the frozen signed oriented
boundary-face flux and `F_X,f^E` the target-destination flux evaluated with E-substituted parents. The exact declared
target boundary work is

`W_X^E = -dt * sum_boundary s(Omega,f) * (F_X,f^E - F_X,f)`.

Outside destination updates retain `F_X,f`; therefore `W_X^E` is also the explicit directed global imbalance
introduced by the incoming-only port. It may not be hidden as conservation. Aggregated target changes must equal
frozen transport plus this logged work, followed only by the separately enumerated local growth, nutrient sink,
inheritance, death, reaction, writer, clipping, production, decay, and reservoir terms.

For each neighbour stencil field `z`, the raw E boundary work is the coefficient-weighted sum of substituted
outside-parent differences over target boundary slots: `dt*D_int*alive*(z^E-z)` for `u,v`,
`dt*(eta_t/4 + D_m)*alive*(m^E-m)` before writer clipping/scaling, `dt*D_c*(c^E-c)`, and
`dt*D_N*(N^E-N)`. Any nonlinear/clipping remainder must be logged separately, never absorbed into boundary work.

Global identities require exact logged equality of `(S_B^E,n_B^E,up_ref^E)` to the formula above and exact
probe residual `N_ext^E-r_N-P(t)-e*(N_ext-r_N-P(t)) = 0`. Source/sink residuals are output delta minus the ordered
sum of frozen transport, declared E boundary work, growth/N consumption, inheritance, death, toggle reaction,
writer/forgetting/template/diffusion, clipping, `c` production/decay, and nutrient reservoir. Tolerances must be
derived from the operation count and IEEE-754 accumulation path before outputs are inspected; byte identity is
required where the paths are required to be exact.

## Implementation and evidence audit

NOT YET OPENED.

## OBSERVED

- The requested isolated branch is at the exact accepted parent commit.

## INFERRED

- None yet.

## HYPOTHESIS

- The committed environmental sample-and-hold port may fail the quasi-autonomy exclusion even if it is mechanically well-accounted; qualification requires structural evidence, not a favorable fixture response.

## WHAT WOULD FALSIFY THIS?

- A complete source-derived edge inventory, exact accountancy, and synthetic qualification demonstrating that the candidate deletes only pre-existing post-`t0` E-to-response innovations without manufacturing an autonomous boundary or adding any response path.

## Failures/dead ends

- None yet.

## Decisions

- No scientific or architectural disposition yet.

## Unresolved risks

- H* and the exhaustive E-parent bundle remain to be derived before any Stage-A fixture output is inspected.

## Handoff

IN PROGRESS.
