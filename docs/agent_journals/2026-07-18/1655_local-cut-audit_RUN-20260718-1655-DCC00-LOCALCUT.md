# DEEP-CHECKPOINT-CAUSAL-CUT-00 Phase 0 local-cut audit journal

- **Role:** independent candidate-operator and mechanical-locality auditor
- **Run ID:** `RUN-20260718-1655-DCC00-LOCALCUT`
- **Start time:** 2026-07-18 16:54:48 +02:00
- **End time:** 2026-07-18 17:48:02 +02:00
- **Starting branch:** `codex/deep-checkpoint-causal-cut-00-phase0`
- **Starting Git state:** `cce7a27955f5cfb1fc3d95388bba9378bc8d85eb`; tracked clean; other agents' untracked journals present and left untouched
- **Ending Git state:** `cce7a27955f5cfb1fc3d95388bba9378bc8d85eb`; tracked clean; this journal and
  two other agents' journals untracked

## Assigned scope

Independently audit existing candidate local-cut operators for a no-writer exact-deep-checkpoint `C00/C10/C01/C11`
design. Inspect support and arrays touched, confinement, global coupling, boundary/collar discontinuity, sham,
body/environment/clock preservation, tracker/fusion/viability, and already-open DEV mechanical evidence only. Do
not execute prospective data, compute or inspect feeding outcomes, or modify shared implementation/design/schema/index
files.

## Actions

- Read `AGENTS.md`, the charter, durable state, decision log, experiment/run indexes, current integration journal,
  and the last experiment manifest/report in the required order.
- Inspected the frozen engine equations, global diagnostic ablations, memory-erasure branches, access-structure
  exchange operators, and no-swap boundary-clamp implementation/tests/DEV mechanics.
- Confirmed the inherited `STOP_PAIR_MECHANICS` record is accepted and not reinterpreted.
- Ran the existing synthetic/no-outcome operator suites only. No new DEV world, prospective world, feeding probe,
  pair outcome, `Y`, causal contrast, or interaction was run or read.
- Audited the already-committed Phase-0.6B mechanical summary through an explicit allow-list of mechanical fields:
  state/deep hashes, isolation, tracker events, finiteness, coverage, temporal jump and viability only.

## Important files read or changed

- Read: `edlab/experiments/sc_mcm/engine.py`, `experiments/individuation/turnover_diag_engine.py`,
  `causal_confirm.py`, `turnover_engine_03g.py`, `access_structure_noswap_operators.py`,
  `access_structure_noswap_dev_feasibility.py`, its tests, and the Phase-0.6B design.
- Changed: this journal only.

## Reproducible commands and experiments

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -m pytest -q `
  experiments/individuation/test_access_structure_noswap_operators.py
# 9 passed in 5.44s

& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -m pytest -q `
  experiments/individuation/test_access_structure_operators.py `
  experiments/individuation/test_directed_causal_pair_phase05_mechanics.py
# 59 passed in 3.70s
```

The tests are implementation/mechanics tests. They do not qualify a per-entity readout cut and were not treated as
scientific evidence.

## Candidate-operator audit

| Existing candidate | Direct support / arrays | What is mechanically established | Disposition for `C00/C10/C01/C11` |
|---|---|---|---|
| `lam_plus=0` | World-global scalar parameter. It changes the `m_plus -> uptake` multiplier at every lattice cell; downstream it changes `uptake,N,rho,U,V,Mf,C` and later `c`. | Existing global branch remains viable and retains an uptake endpoint. | **Reject as local cut.** `MCParams.lam_plus` is one scalar (`edlab/experiments/sc_mcm/engine.py:25-31`), consumed globally in `g` (`:79`). The only declared plus-only control constructs a whole-world engine (`experiments/individuation/turnover_engine_03g.py:35,132`). It cannot cut A while leaving B intact. |
| `up_ref=0` | World-global memory-write reference. | Existing global diagnostic is viable. | **Reject.** It modifies writing everywhere, not local access, and it is itself needed to make the collar isolation proof exact (`turnover_diag_engine.py:76`; no-swap feasibility `:224-231`). |
| `copy_disabled` / `eta_w=0` | World-global passive inheritance or write term. | Historical mechanistic diagnostics only. | **Reject.** These alter history propagation/writing rather than access to an already-formed state and cannot implement A-only/B-only cuts. |
| Local `Mf` erase or standardization | One fixed target/component or disk; direct change only to `Mf` at surgery (`causal_confirm.py:99-108`; no-swap operators `:186-207`). | Spatial support can be exact and initial `rho,U,V,c,N,C,uptake,step` can remain unchanged. | **Reject as channel cut.** It destroys or replaces the candidate stored state itself. It tests state necessity, not whether an unchanged state is directionally accessed. The existing sham erases an empty patch (`causal_confirm.py:182-187`), so it is not disturbance-matched to deleting nonzero target memory. |
| Fixed two-cell boundary replay / `NoSwapClampEngine` | Fixed collar `10 < d <= 12`; overwrites all eight persistent arrays `rho,U,V,c,N,C,uptake,Mf` after every step (`access_structure_operators.py:34`; no-swap operators `:83,104-115,175-178`). | Disabled path is byte-identical; 12/12 already-open targets were finite/trackable for 40 steps; own replay is an exact no-op; under **global `up_ref=0`**, a far-environment perturbation leaves the core bit-identical. | **Reject.** It is a multi-field boundary controller, not a readout-channel cut; it changes the common boundary/body/environment, writes `Mf` on the collar, and is non-conservative. Its exact isolation does not hold as proved under the ordinary global coupling. The ring is fixed, not comoving, and the qualification has no per-step collar/body/partner overlap or pair-separation evidence. |
| Reciprocal core exchange / transplant | Complete `C` block, all eight arrays. | Exact translation and reciprocal pair conservation. | **Reject by accepted D-090.** It creates hard seams up to 22.872x, perturbs halo/far environment and fails individual-arm balance. It also changes body/environment rather than cutting a channel. |

No implemented hard no-flux cut or per-entity masked `lam_plus` operator exists in the searched code. Designing an
array-valued or comoving `lam_plus` mask now would be inventing a new operator after the question was posed; it
cannot inherit any qualification above and is expressly outside this audit.

## Exact provenance and mechanical contradictions

- Engine locality is not purely spatial: `up_ref = mean(uptake[alive])` is world-global
  (`edlab/experiments/sc_mcm/engine.py:103`). A far-environment change alters uptake and therefore the core memory
  update in the same step, bypassing any spatial collar. The existing exact-isolation tests acknowledge this by
  setting `up_ref_zero=True` (`test_access_structure_noswap_operators.py:69-73,93-96`), while the ordinary reference
  clamp uses the default `False` (`access_structure_noswap_dev_feasibility.py:165-184`).
- The Phase-0.6B result records four reconstructed deep states at steps `847,793,831,890` with state hashes
  `bfe23b0...`, `4f64226...`, `c63ce10...`, `a8a044c...`
  (`ACCESS_STRUCTURE_00_PHASE06B_NOSWAP_RESULTS.json:111-127,3938-3954,7765-7781,11592-11608`). It reports
  12 targets and all-arm 40-step viability (`:83-101`). That supports checkpoint feasibility, not a pair-local cut.
- The active reference collar has maximum temporal jump `1.8145423147669801` and maximum eventual core disturbance
  `1.8655212794863028`; the own-replay sham is exactly `0.0` on both (`...NOSWAP_RESULTS.json:96-101`). The gate only
  checks `max(sham) <= max(intervention)` (`access_structure_noswap_dev_feasibility.py:358-359`), so a perfect no-op
  passes; it does not demonstrate a disturbance-matched sham.
- Claimed reference-source independence is assigned as the literal constant `indep_of_recipient = True`, not
  measured (`access_structure_noswap_dev_feasibility.py:321-327`). This is a provenance assertion, not an injection
  or manipulation-artifact test.
- Phase-0.6B reconstructs each deep state with `tdd.run_to` and persists only a hash
  (`access_structure_noswap_dev_feasibility.py:68-83`). The exact serializer exists, but no Phase-0.6B serialized
  deep payload is indexed. An execution design requiring exact serialized checkpoints must first create a bound,
  raw-only checkpoint artefact from already-open DEV reconstruction; the present hashes alone are not executable
  checkpoint payloads.
- The later directed-pair mechanics added the missing collar/body/partner and continuous pair diagnostics, but the
  accepted stop occurred before any access regime: no history arm completed and no clone entered access
  (`DIRECTED_CAUSAL_PAIR_00_PHASE05_REPORT.md:8-13,40-49`). That stop supplies no qualification by inheritance.

## OBSERVED

- The frozen `m_plus -> uptake` coefficient `lam_plus` is one world-global scalar in `MCParams`; every existing
  `lam_plus=0` branch ablates the channel everywhere, not at one entity.
- Local `Mf` erasure is spatially targeted but destroys the stored state; it is not a cut of the readout/access
  channel while preserving the candidate state.
- The no-swap operator overwrites all eight state arrays on a fixed two-cell collar after every engine step. Its
  bit-exact isolation test also sets the world-global `up_ref` to zero.
- There is no existing operator that zeros only the `m_plus -> uptake` term on A, B, both or neither while leaving
  the other entity and all common fields under the same frozen equations.
- No outcome-bearing raw result was opened. The only JSON extraction used an explicit mechanical-field allow-list;
  no feeding array, `Y`, `C`, `I`, effect, dose contrast or own-history contrast was selected.

## INFERRED

An exact-clone four-arm pair factorial is not mechanically interpretable unless one operator can cut the same
predeclared channel at A and/or B without using tracker/diagnostic identity in physics, without changing the partner
or global channel, and with a non-vacuous matched sham plus continuous confinement evidence.

The currently viable deep worlds do not cure the operator problem. A viable pair plus a non-local or multi-field
manipulation cannot identify diagonal, crossed, common-mode, relational or artefactual responses.

## HYPOTHESIS

No existing operator meets that bar. A new local readout mask may be conceivable, but it is not yet an operator and
cannot inherit the global-ablation or collar-clamp qualifications.

## WHAT WOULD FALSIFY THIS?

An existing tested operator that (1) zeros only the declared readout term on a physical, outcome-independent,
continuously confined A/B support; (2) leaves all other equations, the partner, environment, boundary and clock
unchanged at intervention; (3) has a disturbance-matched sham; and (4) preserves viable bijective pair tracking
without any diagnostic identity entering physics.

## Failures and dead ends

- A PowerShell metadata command initially had an empty pipeline parse error; it changed no file and was rerun with
  an explicit intermediate array.
- A Windows wildcard passed directly to `rg` was invalid; the query was rerun with `rg -g`.

## Decisions

- Treat global `lam_plus=0`, local `Mf` erasure, passive-copy disablement, `up_ref=0`, and collar replay as distinct
  interventions; none may be relabelled as a local readout cut without passing its own mechanical contract.
- **Independent verdict: `STOP-LOCAL-CUT`.** This is an operator-availability/mechanical-interpretability stop, not
  a negative causal result. No minimal factorial may be executed and no outcome schema may expose response values
  until a separately authorized operator already exists and passes mechanical qualification.

## Unresolved risks

- A future operator would need an outcome-independent physical support that remains confined to the same entity
  without diagnostic IDs or tracker association entering physics. No such support rule is currently certified.
- It would also need pairwise no-fusion/tracker independence, per-step cut support, A/B and sentinel intersection,
  global `up_ref` leakage, sham disturbance, boundary jump, mass/field balance and clock equality in raw numerical
  diagnostics. These gates must pass before any `Y_A/Y_B` field becomes readable.
- A global `up_ref=0` in every arm could remove one bypass but would change the scientific system and still would
  not turn the collar into a single-channel cut.

## Handoff

Return **`STOP-LOCAL-CUT`** for DEEP-CHECKPOINT-CAUSAL-CUT-00 Phase 0. Preserve the four already-open deep-state
hashes as feasibility leads only. Do not implement a masked/comoving readout coefficient, do not run a four-arm
factorial, and do not expose or compute `Y_A`, `Y_B`, the causal matrix or any outcome contrast under the present
operator inventory. A new operator would require a separate authorization and a fresh DEV-only mechanical phase;
it is not a revision of the accepted writer-path stop.
