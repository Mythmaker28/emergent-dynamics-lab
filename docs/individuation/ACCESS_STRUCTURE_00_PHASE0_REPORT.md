# ACCESS-STRUCTURE-00 — Phase 0 scientific and technical audit

Status: **PHASE 0 COMPLETE — REVISE — HUMAN REVIEW REQUIRED — NO PROSPECTIVE SEED AUTHORIZED**
Branch: `codex/access-structure-00-phase0`, based exactly on V5 commit
`d4a146a241588c0debd3a0cc6133bc6f6bb8824c`.

This report treats the certified 03G Outcome B as fixed prior evidence. It does not reopen 03G, reinterpret its
decision tree, modify V5, or authorize active reconstruction.

## 1. Independent scientific judgment

03G established that erasing the tracked target's local memory field changes its future feeding after deep material
turnover, and that this effect collapses when the `m_plus -> uptake` channel is ablated. It did **not** perform a
sufficiency transplant, an environment reset, a body-standardized environmental assay, or a matched-versus-crossed
state exchange. Its decoder scopes were finite summaries rather than causal compartments. Therefore Outcome B does
not locate the turnover-surviving causal state.

The new question is legitimate and not answered by `G_LOCAL_EXCLUSION=false` or `DISTRIBUTED_ENV=false`. The most
informative next experiment is a four-cell local/environment factorial under a common probe, supplemented by a
matched-versus-crossed arm and body/global-channel controls. Decoding is secondary.

The strongest current alternative is not a demonstrated environmental store. It is that a residual local `m_plus`
field is read directly by the uptake equation while body and environment remain correlated with it. In the four
already-open feasible DEV worlds, the mean observed erase effect as a fraction of intact feeding is 0.0458–0.0613;
the algebraic direct-coupling prediction is 0.0512–0.0675. That agreement is DEV evidence only, but it makes the
residual-readout/body alternative load-bearing.

## 2. Exact 03G scope audit

The label for every gated decoder was target own cumulative dose (`a_phase1 + a_phase2`). Each valid original world
contributed exactly three target rows. Outer leave-one-original-world-out ridge regression used lambda 1, scaling
learned on training worlds only, and fixed-world fold losses. The 1,000-permutation ownership null shuffled labels
within original world using seed `20260715`.

The letters below are decoder scopes. `P` here is not the project's phenotype observable `P(tau)`, and the `Gm/Gf`
scope names are distinct from gate names prefixed `G_`.

| Scope | Exact 03G definition | Dimension | Role | Important limitation |
|---|---|---:|---|---|
| `L` | On the tracked target mask, five summaries each of `m1=Mf[0]/rho` and `m2=Mf[1]/rho` (mean, SD, p10, p50, p90), plus `SD(m1-m2)` | 11 | gated | Memory summaries only; not the whole droplet, body, geometry, extracellular fields, or full spatial memory pattern |
| `N` | The same 11 memory summaries for the geometrically nearest of the other two preselected targets, ordered by periodic centroid distance | 11 | gated exclusion | Not every neighbouring component and not the complete neighbourhood |
| `P` | Concatenation of `L`, nearest-target memory, and farther-target memory | 33 | diagnostic | Contains `L`; cannot be an exclusion comparator and does not represent all local physical context |
| `B` | Target mask cell count, `sum(rho)`, mean/SD `rho`, mean `U/rho`, mean `V/rho`, mean `N`, mean `c` | 8 | gated exclusion | Not a pure body scope: it includes target-local nutrient and attractant; it omits shape, position, full fields, `uptake`, and memory |
| `E` | Eight fields (`rho,U/rho,V/rho,c,N,uptake,m1,m2`) averaged in periodic radial annuli `[0,6)`, `[6,12)`, `[12,24)` around the target centroid; only target-mask `m1/m2` cells are set to zero | 24 | gated exclusion | Still includes target `rho,U/rho,V/rho,c,N,uptake`; target-memory zeros can encode mask geometry; no information outside radius 24 |
| `Gm` | Over cells with `rho>0.30`, mean and SD of the same eight fields after zeroing target-mask `m1/m2`, plus mean uptake over `rho>1e-4` and occupied fraction | 18 | gated exclusion | A target-memory-minus global first/second-moment summary, not the full world state |
| `Gf` | Exact concatenation `L || Gm`; `Gf[:,0:11]` is byte-for-byte `L` | 29 | diagnostic | Necessarily contains `L`; explicitly never an exclusion comparator |

The engine state at the deep snapshot is richer than every scope: `rho`, extensive `U,V`, extracellular `c,N`,
diagnostic cohorts `C`, last-step `uptake`, and extensive two-channel memory `Mf`. `up_ref` is not a persistent state
variable: at each step it is recomputed as mean current uptake over alive cells and enters the memory-writing signal.
It is a global dynamical coupling and must be tested by a dynamical ablation, not treated as a stored scalar.

### Frozen gate logic

- `G_OWN_PERM`: positive held-out `L` skill under the within-world permutation test (`p<0.05`).
- `G_LOCAL_EXCLUSION`: conjunction of positive `L` information and strictly lower held-out loss for `L` than each
  of `N`, `E`, `Gm`, and `B`, using the lower bound of the original-world Student-t interval.
- `DISTRIBUTED_ENV`: true only if `E` or `Gm` has a positive skill lower bound and `L` does not strictly beat it.
- `G_CAUSAL`: target erase effect positive, above sham and neighbour erase, directionally consistent on fixed masks,
  collapsed by `lam_plus=0` with `lam_minus=0.15`, and at least 18 valid worlds.
- Primary 03G ownership gate: `G_OWN_PERM AND G_LOCAL_EXCLUSION AND G_CAUSAL`.

Certified 03G had 21 valid worlds. `L` skill was 0.39545 (t95 lower 0.17532), permutation `p=0.000999`;
`L>N` and `L>Gm` passed, while `L>E` (t95 lower -0.02206) and `L>B` (t95 lower -0.02261) failed. `E` and `Gm`
did not themselves have positive skill lower bounds, so `DISTRIBUTED_ENV=false`. These are exactly compatible with
uncertain access through coarse summaries; they are not evidence that environmental information is absent.

## 3. What the frozen E/G summaries could not detect

`E` and `Gm` discarded or confounded all of the following:

- angular, non-radial, phase, topology, interface, and fine-scale spatial information;
- within-annulus gradients, multimodality, higher moments, cross-field covariance, and multi-point relations;
- target-to-neighbour alignment and any relational code that exists only in a matched local/environment pair;
- the identity and detailed state of non-target droplets; `N` covered only the nearest of two selected targets;
- environment beyond radius 24 in `E`, and all spatial location in `Gm`;
- temporal trajectories, delays, and a dynamically generated global channel;
- complete target memory patterns, because `L` retained only 11 distribution summaries;
- a clean separation of body and environment: `E` retained several target-local fields and `B` retained `N,c`;
- causal sufficiency or necessity of a compartment, because none of these scopes was transplanted or reset.

Consequently, `DISTRIBUTED_ENV=false` means only “the own-dose label was not established as comparably decodable
from these two frozen low-dimensional summaries.” It must never be rewritten as “environmental storage absent.”

## 4. Competing hypotheses and prospective signatures

Let `Y(L,E)` be future integrated target feeding under the identical standardized probe with target body held fixed
within the counterfactual block. `L0` is a validated local-state null and `E0` a validated standardized environment.

| Hypothesis | `Y(L,E0)-Y(L0,E0)` local-only | `Y(L0,E)-Y(L0,E0)` environment-only | matched `Y(L,E)` | crossed `Y(L_A,E_B)` | Interpretation if controls pass |
|---|---:|---:|---:|---:|---|
| `H_L` uniquely local access | positive | equivalent to null | positive | follows `L_A`, not match | local causal sufficiency; “ownership” still requires superiority to E/body/cross controls |
| `H_E` environmental access | equivalent to null | positive | positive | follows `E_B` | environment remains sufficient when local state is standardized |
| `H_R` redundant access | positive | positive | positive | positive unless match-specific | L and E are independently sufficient |
| `H_S` synergistic/relational access | equivalent to null | equivalent to null | positive | reduced if matching matters | joint state succeeds while separate states do not; matched-cross contrast locates relational specificity |
| `H_0` residual readout/body/global confounding | fails sham/body/global controls, or follows body/direct algebraic readout rather than source pairing | variable | variable | variable | no storage-location claim; direct-readout and body explanations are reported separately |

`H_0` is an explanatory layer, not guaranteed to be mutually exclusive with local access. A local transplant can be
causally sufficient yet still amount only to a short-lived directly coupled remnant. That would support local access,
not individual memory or active reconstruction.

## 5. Smallest intervention design

The minimal identifying core is a paired 2x2 factorial for each target in each original world, with one additional
cross arm:

1. `L0E0`: standardized local state/body in standardized environment (double-null reference).
2. `L1E0`: original target-local state in standardized environment (local sufficiency; environment reset while
   local state is preserved).
3. `L0E1`: standardized target-local state/body in its original environment (environmental sufficiency; local state
   erased while environment is preserved).
4. `L1E1`: matched local state plus matched original environment.
5. `LAEB`: target-local state from A with environment from B, for every predeclared eligible ordered A!=B pairing.

All five use one common additive probe schedule and the same future-feeding horizon. “Common probe” means identical
external forcing; it must not erase the environmental state being tested. Totals of environmental nutrient and
attractant energy are matched across branches by an outcome-independent operator, while their organization may
differ. Target `rho`, mask geometry, mass, and body variables are identical within each primary counterfactual
block. Ordered target/cross results are averaged to one vector per original world before inference.

Required parallel controls are:

- exact excision/reimplantation sham and null-memory sham with the same interpolation, copies, mass correction, and
  number of engine calls as active manipulations;
- body-only arms that preserve `rho`/geometry but neutralize local memory, and memory-on-neutral-body arms;
- the five principal arms repeated with global `up_ref` ablated while preserving all local equations;
- `lam_plus=0, lam_minus=0.15` readout ablation and a direct algebraic `m_plus` prediction;
- bijective tracked readout as primary plus fixed initial mask as tracker-independent convergence control;
- a no-history/body/geometry baseline and complete pre-probe state-balance audit.

The precise state partition for implementation must be exhaustive and non-overlapping:

- local memory `L`: intensive `Mf/rho` on the frozen target support;
- body `B`: support/mask, `rho`, `U/rho`, and `V/rho` on that support;
- environment `E`: extracellular `N,c` everywhere plus all physical state outside target support;
- global coupling `G`: the dynamical `up_ref` computation, tested as an engine ablation;
- `C` and target IDs remain diagnostic only and must never enter physics or association.

The target support, body-neutralization rule, environment-reset construction, donor-to-recipient map, boundary blend,
and energy-matching correction must be frozen from manipulation validity alone. None may be selected by future
feeding or own-dose decoding.

## 6. Primary endpoint and claim logic

Primary outcome is integrated feeding on the bijectively tracked target during the frozen horizon under the common
probe. Define world-level contrasts after averaging technical target/cross replications inside each world:

- `tau_L = Y(L1,E0)-Y(L0,E0)`;
- `tau_E = Y(L0,E1)-Y(L0,E0)`;
- `tau_LE = Y(L1,E1)-Y(L0,E0)`;
- `tau_S = Y(L1,E1)-Y(L1,E0)-Y(L0,E1)+Y(L0,E0)`;
- `tau_match = Y(L1,E1)-mean(Y(LA,EB), A!=B)`.

The prospective preregistration must freeze a positive practical margin and an equivalence margin from DEV
manipulation noise, not from confirmation outcomes. A non-significant contrast is “not established,” never “absent.”
Separate failure is required by an equivalence upper bound before `H_S` can be supported. Simultaneous one-sided
world-level intervals or a predeclared multiplicity correction are required.

Claim rules:

- **LOCAL OWNERSHIP supported** only if `tau_L` exceeds the practical margin after environment standardization and
  prospectively exceeds E, body, sham, and crossed controls.
- **ENVIRONMENTAL ACCESS supported** only if `tau_E` exceeds the margin with the local state/body standardized.
- **REDUNDANT supported** only if both `tau_L` and `tau_E` independently exceed the margin.
- **SYNERGISTIC supported** only if `tau_LE` and the interaction pass while the upper equivalence bounds for both
  separate contrasts are below the frozen sufficiency margin. A positive `tau_match` supports relational matching.
- **UNRESOLVED** for insufficient uncertainty, failed controls, or patterns not uniquely classified.

No outcome authorizes identity, individual memory, ownership in a metaphysical sense, life, or active reconstruction.

## 7. Secondary analyses

Secondary only:

- conditional own-dose decoding from predeclared `L`, `E`, `L+E`, matched and crossed representations;
- a predeclared continuous partial-information decomposition reporting unique-L, unique-E, redundancy, and synergy;
- body, geometry, neighbour, and global-channel baselines;
- direct algebraic readout prediction and state-decay trajectories.

Every transform, scaling step, model fit, hyperparameter, and PID assumption must be learned or applied inside
held-out original-world folds. No feature or decoder may be selected using new confirmation outcomes. PID results
must be labelled model-dependent and cannot override the causal primary endpoint.

## 8. DEV-only technical feasibility

Already-open DEV family: `50001-50010`. Deep feasible worlds are 50002, 50004, 50005, and 50007 at steps
847, 793, 831, and 890. All four have three alive/distinct targets and valid deep assays; intact maximum component
coverage is 0.008–0.015.

The committed JSON stores summaries and intervention outcomes, not complete snapshots. Deterministic reconstruction
was therefore tested from the already-open seeds. Reconstructed `m_plus` and material-retention vectors agree with
the committed diagnostic records to maximum absolute errors of `1.67e-16` and `1.11e-16`, respectively, across all
four worlds. No new seed or prospective family was opened.

| Capability | Current status | Phase-0 judgment |
|---|---|---|
| deterministic full deep-state reconstruction | available and numerically reproduced on 4/4 DEV worlds | feasible |
| local `Mf` erase with exact body geometry/mass preserved | existing | feasible |
| N standardization, uniform common probe, tracked and fixed-mask readouts | existing | feasible, but N reset alone is not environment standardization |
| global `up_ref` ablation | existing DEV diagnostic engine | feasible; prior 2-world assay is exploratory only |
| full environment reset preserving local state | absent | required repair |
| standardized local body in original environment | absent | required repair |
| matched/crossed A+B graft | absent | required repair |
| mass/geometry/energy-matched active and sham grafts | absent | required repair |
| branch-level numerical-disturbance envelope and equivalence margin | absent | required repair |

The intervention is technically implementable because the complete state is copyable and all causal arrays are
explicit. It is not yet technically qualified. A graft can violate `sum(C)=rho`, introduce boundary shocks, change
mass or geometry, allow a donor-map artefact to predict the label, or destroy the very environmental organization
under test. Those are validation failures, not details to defer until after prospective data.

## 9. Seed-namespace audit

- `50001-50010`: already-open DEV; only these were executed during Phase 0 reconstruction.
- `51xxx`, `52xxx`, `53xxx`: historical families; read-only context, not candidates.
- `54001-54050`: consumed certified 03G primary family.
- `54051-54096`: unexecuted but reserved by the 03G manifest and therefore unavailable.
- Historical documents also mention superseded `54097-54120`; that namespace must not be silently recycled.

An all-ref text scan for apparent `55xxx` values is contaminated by five-digit byte counts in historical raw indexes,
and the repository contains a broken ref `refs/heads/probe/tmp01`. No new family is selected in Phase 0. Before a
future seal, the seed audit must classify semantic seed declarations across valid refs and dispose of or explicitly
exclude the broken ref without deleting evidence.

## 10. Recommendation

**REVISE.** The causal factorial is the right next question and the four DEV deep states are reconstructible, so
`STOP` is not warranted. `GO` is not justified because the environment reset, standardized-body operator,
matched/cross graft, equivalent sham, disturbance bounds, practical/equivalence margins, and semantic seed-family
audit are not yet frozen and validated.

Exact next authorized action: human review of this Phase-0 design, followed—only if approved—by a DEV-only
manipulation-qualification repair on seeds `50001-50010`. Do not preregister or open prospective seeds until that
repair passes and a separate exact preregistration receives explicit human approval.
