# MYQBD01 — INDEPENDENT ADVERSARIAL REVIEW (final seal, second review overall)

Reviewer role: single authorized independent adversarial reviewer. Mandate:
`/home/claude/MYQBD01/review/REVIEWER_BRIEF.md`.
Status vocabulary used throughout: `DEFECT_CONFIRMED`, `DEFECT_PLAUSIBLE`, `ATTACK_REFUTED`
(= the attack failed, the attacked claim stands). The bare word for "attack succeeded" is never
used; every judgement is one of the three above.

```
CANDIDATE_TIP_REVIEWED   f88147a3b5603aa2c301061c495fdd87200b3b55  (verified: git rev-parse)
BRANCH                   codex/minority-y-q-bound-derivation-01     (clean working tree)
PARENT                   8c2afa32e1e19ecf7ee5ff6e803dbb50cf2f0367
OUTPUTS VERIFIED         30 / 30 lines of MYQBD01_SHA256SUMS verify OK
RAW ARCHIVES READ        28 .npz in /home/claude/OBFOR01/raw  (14 S__, 14 M__)
SCIENTIFIC_RUNS_USED_BY_REVIEW = 0   (no World constructed, no _one_step called, no engine import)
```

Everything below was obtained by reading source, reading `.npz` arrays, and exact arithmetic /
enumeration / PGF algebra. Scratch scripts are in `/home/claude/MYQBD01/review/work/`.

---

## 0. THE THREE PROVENANCE FACTS, CARRIED

**P-1 — the seal launcher's `CANDIDATE_REPORTED_TIP = decfda5` is stale.** Confirmed:
`git log --oneline` on the branch gives `f88147a` (tip) with `decfda5` its immediate parent.
`decfda5` is a true ancestor, one commit behind. This review reviews `f88147a`. The stale
identifier is recorded as finding **F32**. It is cosmetic here only because the reviewed content
strictly contains the reported content; had the extra commit removed anything it would not be.

**P-2 — `MYQBD01_MASTER_FREEZE.{md,json}` was committed in the same commit `decfda5` as
`MYQBD01_ARM_LEVEL_Q_SUMMARIES.{csv,json}` and `MYQBD01_TEMPORAL_DEPENDENCE.json`.** Confirmed by
`git show --stat decfda5`. There is no independent Git checkpoint proving the freeze predates
detailed statistical access. Recorded as finding **F31**. My judgement on whether any surviving
claim depends on that ordering: **no**, and here is the precise reason. The freeze binds
thresholds and a region rule whose only function is to gate a *positive* disposition. The
delivered disposition is negative (`EXISTING_Q_DATA_INSUFFICIENT…`), and the two requirements
that block it — `MOBILE_SPATIAL_ENVIRONMENT_RESOLVED` and `TWO_Y_STATE_OPERATOR_VERIFIED` — are
both decided by *structural* facts about the archive's key set (§12, §11), not by any threshold
in the freeze and not by any statistic in the summaries. Peeking at Q statistics could only have
tempted a positive claim; it cannot manufacture a negative one. The ordering would become
load-bearing the moment any positive region were asserted, and none is.

**P-3 — MYQBD01 §19 already consumed one adversarial review inside the candidate**
(`MYQBD01_REVIEW_AND_REPAIR.json`: 15 attacks, 0 load-bearing, 0 material, 3 cosmetic repaired,
12 refuted, reviewer concurring). Mine is the second review overall. Every finding below carries
`RELATION_TO_PRIOR_INTERNAL_REVIEW` ∈ {repeats, deepens, contradicts, new}. Tally over the 32
findings: **repeats 2, deepens 5, contradicts 5, new 20**. The five contradictions are F02, F08,
F09, F15 and F20 — in each the prior review recorded the item as cleanly settled at source; I
confirm the *conclusions* but find the *evidence* that produced them wrong (F02 cites a file that
did not execute; F08 repeats a misdescription of `source_substep_ledger`), absent (F09: the
load-bearing boolean is a hardcoded literal), demonstrated only far outside the admissible
parameter box (F15: 1250–5000×), or built on an inflated witness the prior review itself created
and never checked against the arms (F20: 3.79×).

---

## 1. WHAT THE ARCHIVES ACTUALLY ARE (the basis for A4, stated once)

The 28 delivered arms were written by `/home/claude/OBFOR01/code/run_obfor01.py:129-142`
(`np.savez_compressed`), **not** by `protocol_obtc02.py:167-179` — only `run_obfor01.py` emits
`hop_ledger`, `source_substep_ledger` and `birth_substep_ledger`. The executing world is
`run_obfor01.Instrumented` → `engine_obtc.WorldOBTC` → `lawspec_v2.WorldV2` → `kinetics.World`.
All 28 archives carry the identical 15-key set (verified). Loaded spec (from
`/home/claude/OBTC02/code/obtc02_protocol.yaml` `point:` block, via
`run_obfor01.build` → `protocol_obtc02.spec_for`):
`L=36, CAP=16, S0=3, phi=0.2, omega=0.05, muX=0.004, muY=0.0, kX=1.0, kY=0.0,
p_hop_X=0.10263340389897246, p_hop_Y = 0 (S) or p_hop_X (M), X_SEED=4,
HORIZON=11000, BURN_IN=2000, SAMPLE_EVERY=50`.

### 1.1 EVERY KEY, EXACT SHAPE, DTYPE, PER-COLUMN MEANING, CADENCE, INVERTIBILITY

| key | shape | dtype | per-column meaning | cadence | invertible to a lattice field? |
|---|---|---|---|---|---|
| `series` | (11000, 29) | float64 | 29 named columns, see `fields` | **every step, stride 1**, label = post-increment `w.step` ∈ 1…11000 | **No.** Every one of the 29 columns is either a lattice-wide sum (`N_X…N_WY`, `O_total`, `free_total`, `accepted_births_X`, `deaths_X`), a cumulative counter (`flux_in`, `flux_out`, `displaced_total` — all three carry the identical cumulative value, ending 3 379 405 in `M__seed9300014`), a lattice-wide mean (`free_at_source_mean`), or a value read **at the organiser cell only** (`u_nX_at_org`, `nSX_at_org`, `nSY_at_org`, `nW_at_org`, `free_at_org`, `p_X_at_org`, `c_X_total`, `c_X_per_org`, `expected_births_X`, `cand_Y_at_org`, `Q`, `source_on`, `n_org_cells`). Written in `Recorder.pre_react` / `close_step`, `observe.py:51-104`. |
| `fields` | (29,) | `<U19` | the 29 column names, index 20 = `Q` | once | n/a |
| `nX_final` | (36, 36) | int64 | X occupancy | **terminal step only** | yes, at t = 11000 only |
| `nY_final` | (36, 36) | int64 | Y occupancy | terminal only | yes, at t = 11000 only |
| `nSX_final` | (36, 36) | int64 | SX occupancy | terminal only | yes, at t = 11000 only |
| `nSY_final` | (36, 36) | int64 | SY occupancy | terminal only | yes, at t = 11000 only |
| `nWX_final` | (36, 36) | int64 | WX occupancy | terminal only | yes, at t = 11000 only |
| `nWY_final` | (36, 36) | int64 | WY occupancy | terminal only | yes, at t = 11000 only |
| `molecule_births` | (n, 4), n = 118 in `M__seed9300014` | int64 | `(id, birth_step, birth_y, birth_x)` of **labelled X molecules still alive at the end** (`run_obfor01.py:133-136` zips `tr.id, tr.birth_step, tr.birth_y, tr.birth_x`, and `Tracker.death` deletes dead entries from those arrays, `engine_obtc.py:106-116`) | per surviving molecule | **No.** Birth coordinate only; no trajectory, and no positions of the 5 258 molecules that died. |
| `molecule_deaths` | (5258, 5) | int64 | `(id, birth_step, birth_y, birth_x, death_step)` — `d[:5]` of the 6-tuple, so the `cause` field is dropped (`run_obfor01.py:137-138`, `engine_obtc.py:111-112`) | per death | **No.** Gives *when* a molecule died, never *where*. |
| `frames` | (220,) | **`<U572` — JSON strings, not indices** | each decodes to a dict of **24 scalar** morphology fields: `step, N_X, N_Y, n_components, main_cid, main_N_X, main_mass_fraction, n_eff_components, centre_y, centre_x, r50, r80, r90, Rg, core_fraction, geodesic_diameter, organiser_y, organiser_x, organiser_to_core, wraps_y, wraps_x, any_winding, legacy_extent_proxy, r80_organiser` | **stride 50**: steps 50, 100, …, 11000 (220 of 11000) | **No.** Verified: the value types over all 220 frames are exactly `{int, float, bool}` — no list, no array, no lattice. `metrics_obtc.frame(nX, nY, core_radius)` consumes only X and Y, so SX/SY/WX/WY have **zero** spatial constraint from frames. Carries *coordinates* (`organiser_y/x`, `centre_y/x`) but no *field values*. |
| `birth_offsets` | (n, 4), n = 3 862 here; 97 973 rows pooled over 28 arms | int64 | `(step, dy, dx, count)` of **X** births relative to the organiser (`engine_obtc.py:183-189`); step label = pre-increment | per step with a birth | **Degenerate.** Verified over all 28 arms: **every one of the 97 973 rows has (dy, dx) = (0, 0)**. Necessarily so: `p_X = min(1, kX·nX·nY)` is non-zero only where `nY > 0`, and `n_org_cells ≡ 1`. Carries no spatial information whatever. |
| `hop_ledger` | (44000, 4) | int64 | `(step, species_index ∈ {0:X,1:Y,2:SX,3:SY}, movers_offered, movers_blocked)` — **lattice-wide sums over all 1 296 cells AND all 4 directions**, one row per `_diffuse` call (`run_obfor01.py:75-77`) | 4 rows per step × 11000 | **No.** Two integers stand in for 4 × 1 296 = 5 184 per-cell Binomial outcomes. |
| `source_substep_ledger` | (44000, 6) | int64 | `(step, species_index, org_y_before, org_x_before, org_y_after, org_x_after)` — the **position of the single Y**, before and after each `_diffuse` call (`run_obfor01.py:65-67, 78`) | 4 rows per step × 11000 | **Yes, for the Y field only.** This is genuinely position-resolved and fully determines the organiser trajectory at sub-step resolution. It says nothing about occupancy of any species at any cell. |
| `birth_substep_ledger` | (11000, 6) | int64 | `(step, total_X_born_this_step, org_y, org_x, free_at_org_before, nSX_at_org_before)` (`run_obfor01.py:86-87`); step label = pre-increment | 1 row per step | **No.** One organiser cell, one lattice-wide birth total. |

Step-label convention (undocumented in the candidate, finding F03): `series[:,0]` runs 1…11000
(written in `close_step` after `w.step += 1`), while `hop_ledger`, `source_substep_ledger`,
`birth_substep_ledger` and `birth_offsets` all label the *same physical sub-step* with the
pre-increment value 0…10999. Cross-checked: `frames` organiser coordinates at step *t* equal the
post-diffusion organiser position recorded at ledger step *t−1* in **220/220** frames.

### 1.2 THE RECONSTRUCTION ATTEMPT, DONE EXPLICITLY

**Forward from t = 0.** The initial state is known exactly (`SX = SY = 3` everywhere, `X = 4`,
`Y = 1` at (18,18), `WX = WY = 0`). Advancing one step requires the per-cell `movers` arrays of
four `_diffuse` calls. The ledger gives one `offered` total per (step, species). Counting how
often that total happens to be zero (the only case in which the motion *is* determined):

```
species   rows    offered == 0            mean offered   total blocked
X        11000      21  ( 0.19 %)              12.25            64
Y        11000    9948  (90.44 %)               0.10             1
SX       11000       0  ( 0.00 %)             392.64          1569
SY       11000       0  ( 0.00 %)             392.79          1460
```

SX and SY diffusion is undetermined at **every one of the 11 000 steps**. Reconstruction fails at
step 0. The Y field is the sole exception and is fully determined — but by
`source_substep_ledger`, not by `hop_ledger`.

**Backward from the terminal grids.** Inverting one step requires undoing `_exchange`
(`lawspec_v2.py:90-129`: per-cell `Binomial(max(S0−n,0), phi)` offers plus per-cell multivariate
hypergeometric removal from {SX,SY,WX,WY}) — recorded only as a *cumulative* scalar; `_decay`
(per-cell `Binomial(nX, muX)`) — recorded only as the per-step total `deaths_X`, which is
non-zero on 4 197 of 11 000 steps; `_react` — this one *is* per-cell invertible via
`birth_offsets`; and four `_diffuse` calls — undetermined as above. Reconstruction fails at the
first backward step.

**Counting.** The full 6-species occupancy history is 6 × 1 296 × 11 000 = **85 536 000** integers.
One archive stores **874 986** numeric entries plus ≈ 5 280 frame scalars: a ratio of **97.2 : 1**,
and most stored entries are redundant sums. For the SY field specifically, the archive constrains
each step by exactly two scalars (`N_SY`, `nSY_at_org`), leaving **1 294 free degrees of freedom
per step** at each of the 10 999 non-terminal steps.

**The decisive fact, which the candidate never states in §12.** `kY = 0.0` in the loaded spec.
Verified empirically over all 28 arms and all 11 000 steps each: **`N_Y ≡ 1` and
`n_org_cells ≡ 1` at every one of the 308 000 recorded steps; zero Y births ever occurred.**
`Q_POSITION(x,t)` "for a separated mobile descendant" is therefore not a censored observable —
the event it measures has probability exactly zero under the archives' own law. This is stronger
than "unrecorded": no reconstruction, however complete, and no re-reading of the data can produce
it.

### 1.3 WHAT *IS* EXTRACTABLE, AND WHY IT DOES NOT CHANGE THE DISPOSITION

`Q_POSITION(x, t)` is exactly computable at the **one** step where the full fields exist. I
computed it for all 28 terminal snapshots as `nX·min(nSY, CAP − Σ_species)`. Pooled radial profile
about the organiser:

```
dist   0      1      2      3      4      5      6      7      8      9     10     11     12
meanQ  2.500  3.402  2.604  1.690  1.138  0.716  0.463  0.345  0.231  0.146  0.090  0.067  0.047
P(Q>0) 0.250  0.683  0.592  0.444  0.314  0.213  0.150  0.104  0.077  0.048  0.027  0.019  0.015
```

Mean number of cells with `Q > 0` is 60.4 of 1 296. This is a genuine quantitative result the
candidate left on the table, and it points *away* from the region being derivable: a descendant
that separates sees an exposure falling by a factor ≈ 7 within 6 cells. It is 28 snapshots at one
instant and cannot furnish a per-step lineage operator.

---

## 2. FINDINGS

Every finding carries all mandated fields. `LOAD_BEARING` means: if confirmed, the final
disposition must change.

---

### F01
- **ID** F01
- **ATTACK** A1
- **SEVERITY** LOAD_BEARING
- **STATUS** ATTACK_REFUTED
- **CLAIM_ATTACKED** `Q_LEDGER_EVENT_EXACT`: the `Q` written in `Recorder.pre_react` is the exact exposure entering the Y-birth Binomial at the same step; no sub-step between the write and the Y `cand` computation can change `min(nSY, free)`.
- **EXACT_FILE_AND_LINES** `/home/claude/ORR01/code/observe.py:51-70` (`pre_react`, `free` at 54, `cy` at 59, `Q` at 69); `/home/claude/OBTC02/code/engine_obtc.py:176-193` (`_react`: `pre_react` at 178, `_react_core()` at 179) and `:158-174` (`_react_core`: `pair` at 161, `free0` at 162, loop at 164, `p` at 165, `cand` at 166); `/home/claude/ORR01/code/kinetics.py:154-162` (`_one_step` order); `/home/claude/OBFOR01/code/run_obfor01.py:80-87` (`Instrumented._react`, read-only).
- **EXACT_NUMBERS** Over all 28 arms × 11 000 steps = 308 000 rows: `max |Q − u_nX_at_org · cand_Y_at_org| = 0.000e+00`; `max |cand_Y_at_org − min(nSY_at_org, free_at_org)| = 0.000e+00`; `max |free_at_org − (CAP − occupancy_at_org)| = 0.000e+00` with CAP = 16. `n_org_cells ≡ 1`, so `Q = nX·cand_Y` cell-exactly.
- **WHY_IT_MATTERS** An off-by-one-phase `Q` would invalidate every downstream number in the mission.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/MYQBD01/review/work/a1_a5_a7.py`. Source argument: `free0` and `pair = nX·nY` are both materialised **once**, above the two-iteration loop (`engine_obtc.py:161-162`); the X iteration rebinds only `self.n["SX"]` and `self.n["X"]`, never `self.n["SY"]`, so the Y iteration's `cand = min(self.n["SY"], free0)` is untouched. Independently, an X birth converts SX → X and so conserves per-cell occupancy exactly, meaning even a recomputed `free` would be unchanged. Nothing at all executes between line 178 and line 179.
- **MINIMUM_REQUIRED_CHANGE** None.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** deepens — the prior review argued the point from source only; this adds a 308 000-row exact numerical identity test that the candidate never performed.

### F02
- **ID** F02
- **ATTACK** A1
- **SEVERITY** COSMETIC
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** The phase map's `ENGINE_Y_BIRTH` provenance and the reported scheduler order.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/MYQBD01/code/myqbd01_phase.py:31, 44-46` reads `kin = blob("ORR01/code/kinetics.py")` and takes `free0`/`p`/`cand` line numbers from it, yielding `/home/claude/edl/MYQBD01/out/MYQBD01_Q_PHASE_MAP.json` `ENGINE_Y_BIRTH` = lines 117 / 119 / 120. `/home/claude/edl/MYQBD01/out/MYQBD01_Q_SEMANTICS_AND_PHASE_REPORT.md:5-7` reports the order ending `… → _decay → _feed_and_outflow`.
- **EXACT_NUMBERS** kinetics.py:117/119/120 vs the executed `engine_obtc.py:162/165/166`. `kinetics.World._react` was **never called** for these archives: `WorldOBTC._react` (engine_obtc.py:176) calls `self._react_core()`, not `super()._react()`. Likewise the 7th scheduled operator was `lawspec_v2.WorldV2._exchange` (lawspec_v2.py:90-129) under `LAWSPEC_V2_EXCHANGE`, not `kinetics.World._feed_and_outflow`.
- **WHY_IT_MATTERS** A report whose sole purpose is phase provenance cites a file that did not execute. The semantics happen to be identical (`_react_core` is a verbatim copy of the kinetics loop minus the `hazard_armed` block, which draws no random number), so the conclusion is unaffected — but the citation is not evidence for the archives.
- **SETTLING_COMMAND_OR_CALCULATION** `diff <(sed -n 113,133p /home/claude/ORR01/code/kinetics.py) <(sed -n 158,174p /home/claude/OBTC02/code/engine_obtc.py)`; and grep the MRO: `WorldOBTC(V2.WorldV2)`, `WorldV2(K.World)`.
- **MINIMUM_REQUIRED_CHANGE** In `MYQBD01_Q_PHASE_MAP.json`, cite `OBTC02/code/engine_obtc.py:162,165,166` as `ENGINE_Y_BIRTH` (retaining the kinetics.py lines as `INHERITED_EQUIVALENT`), and state in the .md that the 7th operator executed is `_exchange`.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** contradicts in emphasis — the prior review cited `engine_obtc.py:161-166` (correct) while the delivered artefact still cites kinetics.py; the mismatch was not recorded as a defect.

### F03
- **ID** F03
- **ATTACK** A1
- **SEVERITY** COSMETIC
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** That the phase map fully documents the ledger's step phase.
- **EXACT_FILE_AND_LINES** `/home/claude/ORR01/code/observe.py:89-91` (`close_step` sets `r["step"] = int(w.step)` after `kinetics.py:162` `self.step += 1`) vs `/home/claude/OBFOR01/code/run_obfor01.py:75, 78, 86` and `/home/claude/OBTC02/code/engine_obtc.py:189`, all of which record `int(self.step)` *inside* the sub-step.
- **EXACT_NUMBERS** `series[:,0]` = 1, 2, …, 11000. `birth_substep_ledger[:,0]` = 0, 1, …, 10999. `hop_ledger` and `source_substep_ledger` likewise 0…10999. The same physical reaction is labelled *t* in the ledgers and *t+1* in `series`. Cross-check: `frames` organiser coordinates at step *t* match `source_substep_ledger` post-diffusion position at step *t−1* in 220/220 frames.
- **WHY_IT_MATTERS** A latent join trap. It is currently harmless: no MYQBD01 module joins `series` to any ledger by step (verified — the ledgers are opened only for `.shape`). Any successor that does join them will silently shift by one step.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/MYQBD01/review/work/a4_detail.py`.
- **MINIMUM_REQUIRED_CHANGE** One line in `MYQBD01_Q_PHASE_MAP.json` recording the two step-label conventions and the offset.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** new.

### F04
- **ID** F04
- **ATTACK** A2
- **SEVERITY** SUBSTANTIVE
- **STATUS** ATTACK_REFUTED
- **CLAIM_ATTACKED** IAT ≈ 7 (static) / 9 (mobile); the independent unit is the arm (14 per branch), never the 9 000 frames; the 14 arms in a branch are independent.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/MYQBD01/code/myqbd01_arms.py:35-57` (`acf_iat`), `:162-173` (`branch`); `/home/claude/edl/MYQBD01/out/MYQBD01_TEMPORAL_DEPENDENCE.json`. Seeding: `kinetics.py:76`, `lawspec_v2.py:82-83`, `engine_obtc.py:43`.
- **EXACT_NUMBERS** My independent reimplementation reproduces the candidate's mean IAT to all printed digits: static 7.1772, mobile **9.19672185075826** (identical to `MYQBD01_FINAL_DISPOSITION.json` `mean_integrated_autocorr_time_mobile`). Two further estimators agree at branch level: block-means with block 500 gives 7.560 (S) / 9.352 (M); a low-frequency spectral estimate gives 9.433 (S) / 9.164 (M). Independence: 28 distinct seeds 9300000…9300027, no repeats; within an arm the three streams are the SeedSequence root, child `(1,)` (`rng_feed`) and child `(2,)` (tracker) — disjoint spawn keys, no shared parent state. Empirically, over the 378 distinct arm pairs the maximum cross-arm correlation of the in-window Q series is |r| = **0.05278**, mean r = **0.00084**, against a heuristic standard error of √(IAT/9000) ≈ 0.03.
- **WHY_IT_MATTERS** If the arms shared a seed or a parent state, the 14-arm uncertainty would be fictitious.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/MYQBD01/review/work/a2_iat.py` and `.../a3b.py`.
- **MINIMUM_REQUIRED_CHANGE** None.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** new — the prior review did not list temporal dependence among its load-bearing attacks.

### F05
- **ID** F05
- **ATTACK** A2
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** The branch-level summary "IAT ~7-9" as an adequate description of the temporal dependence, and the estimator used to produce it.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/MYQBD01/code/myqbd01_arms.py:48-55` (the stopping rule; the variable `pair` computed at line 51 is dead and never read); `:45` caps the ACF at lag 2000; `/home/claude/edl/MYQBD01/out/MYQBD01_TEMPORAL_DEPENDENCE.json` `MOBILE.mean_iat`.
- **EXACT_NUMBERS** The IAT is heavy-tailed, not "~7-9": arm `M__seed9300015` has IAT = **35.335**, i.e. **3.84×** the mobile mean of 9.1967, corroborated by block-500 = 31.417 and spectral = 47.322. Next largest 12.065 (`M__seed9300027`), 10.805 (`M__seed9300016`). The candidate's rule advances the index by 1 over *overlapping* pairs `(acf[k], acf[k+1])` rather than summing the textbook Geyer pair sums `Γ_m = ρ_{2m} + ρ_{2m+1}`; on 26 of 28 arms the two agree to ≤ 0.006, but on `S__seed9300006` it gives 6.968 vs 10.063 and on `S__seed9300013` 7.107 vs 8.198 — a 44 % and 15 % understatement.
- **WHY_IT_MATTERS** The brief's concern is that a badly underestimated IAT could make even the 14-arm claim optimistic. It does not, and the direction is favourable: even the worst arm retains 9000/35.335 = **254.7** effective within-arm blocks, while the candidate conservatively uses n = 14 for branch uncertainty. But the delivered headline understates the dispersion by nearly 4× and the estimator is non-standard without being labelled so.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/MYQBD01/review/work/a2_iat.py`.
- **MINIMUM_REQUIRED_CHANGE** Report `max_iat` alongside `mean_iat` per branch in `MYQBD01_TEMPORAL_DEPENDENCE.json` (35.335 mobile, 9.719 static), name the estimator "overlapping-pair initial-positive-sequence", and delete the dead `pair` line.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** new.

### F06
- **ID** F06
- **ATTACK** A3
- **SEVERITY** LOAD_BEARING
- **STATUS** ATTACK_REFUTED
- **CLAIM_ATTACKED** static mean-of-arm-means E[Q] = 2.369048 (sd 0.130602), mobile 3.169730 (sd 0.162990); the separation is not an artefact of one or two arms, of the burn-in choice, or of the filename prefix.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/MYQBD01/code/myqbd01_arms.py:98-100, 138, 162-173`; `/home/claude/edl/MYQBD01/out/MYQBD01_ARM_LEVEL_Q_SUMMARIES.json`. Branch assignment source: `myqbd01_arms.py:84, 102` reads `condition` from `/home/claude/OBFOR01/out/_validation.json`.
- **EXACT_NUMBERS** Every arm ID and its own in-window (steps 2000–10999) mean Q, recomputed from raw:

| arm | Q_mean | Q_sd | Q10 | frac(Q=0) | organiser moves / distinct cells |
|---|---|---|---|---|---|
| M__seed9300014 | 3.171222 | 4.684621 | 0.0 | 0.5464 | 1038 / 373 |
| M__seed9300015 | 2.872556 | 4.556334 | 0.0 | 0.5902 | 1105 / 409 |
| M__seed9300016 | 3.106667 | 4.624344 | 0.0 | 0.5429 | 1052 / 392 |
| M__seed9300017 | 3.384556 | 4.826148 | 0.0 | 0.5262 | 1064 / 438 |
| M__seed9300018 | 3.086000 | 4.597978 | 0.0 | 0.5568 | 1047 / 325 |
| M__seed9300019 | 3.147889 | 4.564635 | 0.0 | 0.5334 | 1047 / 373 |
| M__seed9300020 | 3.200556 | 4.709508 | 0.0 | 0.5386 | 1043 / 391 |
| M__seed9300021 | 3.228444 | 4.644757 | 0.0 | 0.5340 | 1036 / 356 |
| M__seed9300022 | 3.429889 | 4.897139 | 0.0 | 0.5262 | 1107 / 381 |
| M__seed9300023 | 2.920111 | 4.353294 | 0.0 | 0.5420 | 1133 / 400 |
| M__seed9300024 | 3.240111 | 4.738525 | 0.0 | 0.5372 | 1015 / 455 |
| M__seed9300025 | 3.047667 | 4.599586 | 0.0 | 0.5517 | 1068 / 324 |
| M__seed9300026 | 3.158556 | 4.731914 | 0.0 | 0.5402 | 1070 / 381 |
| M__seed9300027 | 3.382000 | 4.933120 | 0.0 | 0.5332 | 1088 / 399 |
| S__seed9300000 | 2.493000 | 4.243106 | 0.0 | 0.6483 | 0 / 1 |
| S__seed9300001 | 2.339889 | 3.997044 | 0.0 | 0.6551 | 0 / 1 |
| S__seed9300002 | 2.355111 | 3.952815 | 0.0 | 0.6438 | 0 / 1 |
| S__seed9300003 | 2.338222 | 4.017138 | 0.0 | 0.6451 | 0 / 1 |
| S__seed9300004 | 2.375778 | 3.980577 | 0.0 | 0.6422 | 0 / 1 |
| S__seed9300005 | 2.183556 | 3.681973 | 0.0 | 0.6539 | 0 / 1 |
| S__seed9300006 | 2.386667 | 4.035739 | 0.0 | 0.6451 | 0 / 1 |
| S__seed9300007 | 2.319778 | 4.037711 | 0.0 | 0.6531 | 0 / 1 |
| S__seed9300008 | 2.342889 | 3.993631 | 0.0 | 0.6470 | 0 / 1 |
| S__seed9300009 | 2.482667 | 4.177383 | 0.0 | 0.6438 | 0 / 1 |
| S__seed9300010 | 2.377556 | 4.067317 | 0.0 | 0.6531 | 0 / 1 |
| S__seed9300011 | 2.495333 | 4.068829 | 0.0 | 0.6264 | 0 / 1 |
| S__seed9300012 | 2.598556 | 4.271857 | 0.0 | 0.6321 | 0 / 1 |
| S__seed9300013 | 2.077667 | 3.705648 | 0.0 | 0.6683 | 0 / 1 |

  Branch aggregates, reproduced **exactly**: static mean-of-arm-means **2.369048**, sd **0.130602**, se 0.034905, range [2.077667, 2.598556]; mobile **3.169730**, sd **0.162990**, se 0.043561, range [2.872556, 3.429889]. Totals also reproduce: 28 arms, 14/14, **308 000** series rows, **0** missing Q, observed **Q_max = 28**.
  Not driven by one or two arms: the branches are *completely* separated (max static arm mean 2.598556 < min mobile arm mean 2.872556, gap 0.274000), and the minimum leave-one-out difference over all 28 single-arm deletions is 0.778269 vs the full 0.800683. Welch t = 14.3439. Because the two groups are completely separated, any non-identity relabelling strictly reduces the difference, so the exact two-sided permutation p-value is **2 / C(28,14) = 2 / 40 116 600 = 4.99e-8**.
  Burn-in sensitivity (difference mobile − static): 0.806000 (burn 0), 0.803054 (500), 0.793436 (1000), **0.800683 (2000, the chosen value)**, 0.767652 (3000), 0.757776 (4000), 0.736893 (5000), 0.728271 (6000). Stable.
  Branch assignment verified **against the dynamics, not the filename**: `p_hop_Y` is not stored in the archives, so I used `source_substep_ledger` — every `S__` arm has **0 organiser moves and exactly 1 distinct organiser cell across all 44 000 sub-step rows** (`p_hop_Y = 0`), and every `M__` arm has 1015–1133 moves over 324–455 distinct cells. Assignment is correct for all 28.
- **WHY_IT_MATTERS** These are the mission's only headline statistics.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/MYQBD01/review/work/a3_arms.py` and `.../a3b.py`.
- **MINIMUM_REQUIRED_CHANGE** None.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** deepens — the prior review reproduced headline numbers; the dynamical verification of branch assignment, the LOO analysis and the exact permutation p-value are new.

### F07
- **ID** F07
- **ATTACK** A4
- **SEVERITY** LOAD_BEARING
- **STATUS** ATTACK_REFUTED
- **CLAIM_ATTACKED** `Q_POSITION(x,t)` for a separated mobile descendant is not recoverable from the archives (`SPATIAL_ENVIRONMENT_STATUS = ORGANISER_ONLY_ENVIRONMENT_AVAILABLE`). The whole calibration disposition rests on this.
- **EXACT_FILE_AND_LINES** Archive writer `/home/claude/OBFOR01/code/run_obfor01.py:129-142`; ledger construction `:65-87, 124-128`; `Tracker` `/home/claude/OBTC02/code/engine_obtc.py:38-122`; `birth_offsets` `:183-189`; recorder `/home/claude/ORR01/code/observe.py:38-104`; frame builder `/home/claude/OBTC02/code/metrics_obtc.py:167` (`def frame(nX, nY, core_radius)` — consumes X and Y only); spec `/home/claude/OBTC02/code/obtc02_protocol.yaml` `point:` `kY: 0.0`, `muY: 0.0`.
- **EXACT_NUMBERS** Full 15-key enumeration in §1.1 above, verified identical across all 28 arms. Decisive numbers: (i) **zero** arrays of shape (T, 36, 36) exist; the only (36,36) arrays are the 6 terminal grids, i.e. the full field exists at **1 of 11 000** steps. (ii) `frames` is (220,) `<U572` JSON strings decoding to **24 scalars** each, value types exactly `{int, float, bool}` — no lattice, stride 50. (iii) `birth_offsets`: **97 973 rows over 28 arms, all with (dy,dx) = (0,0)** — zero spatial content. (iv) `hop_ledger` gives 2 integers where the engine drew 4 × 1296 = **5 184** per-cell values; SX and SY have `offered > 0` at **100.00 %** of the 11 000 steps, so their motion is never determined. (v) Counting: **85 536 000** unknowns vs **880 266** stored numbers, ratio **97.2**; the SY field has **1 294** free degrees of freedom per step. (vi) **`kY = 0.0` ⇒ `N_Y ≡ 1` and `n_org_cells ≡ 1` at all 308 000 recorded steps across 28 arms — zero Y births ever.**
- **WHY_IT_MATTERS** This is the single item the brief names most load-bearing. If `Q_POSITION` were recoverable the candidate would be too conservative and the disposition would have to change to `CANDIDATE_TOO_CONSERVATIVE…`.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/MYQBD01/review/work/a4_enum.py`, `.../a4_detail.py`, `.../a4_recon.py`, `.../a4_frames.py`, `.../a4_qpos.py`. The obstruction is threefold and each part is independently sufficient: (1) **structural** — no key holds any per-cell occupancy of any species at any t < 11000 outside the organiser cell; (2) **information-theoretic** — the operators that move mass (`_diffuse`, `_decay`, `_exchange`) appear only as lattice-wide sums, so neither forward nor backward reconstruction closes, and it fails already at step 0 on SX/SY; (3) **measure-theoretic and decisive** — with `kY = 0` no descendant ever existed, so the quantity is not a function of the data at all. Regarding item (a) of the scope note: `frames` does carry organiser and cluster-centre *coordinates* at stride 50, but `Q_POSITION(x,t) = nX(x)·min(nSY(x), free(x))` needs *field values at a cell*, not the coordinate of an object; and the organiser coordinate is already available at stride 1 from `source_substep_ledger`, so `frames` adds nothing to this question. Regarding item (b): `molecule_births`/`molecule_deaths` carry birth coordinates of labelled X molecules (not trajectories, not death positions, and never Y).
- **MINIMUM_REQUIRED_CHANGE** None to the conclusion. See F08–F10 for required changes to the evidence.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** deepens — the prior review asserted "unrecoverable, confirmed" in one clause; this is the first full key-by-key enumeration with an explicit failed reconstruction and an explicit obstruction.

### F08
- **ID** F08
- **ATTACK** A4
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** "`SUBSTEP_LEDGERS_ARE_SCALAR` … these carry step, sub-step index and scalar organiser-cell counts" — and, in the commit message for `f88147a`, "the sub-step ledgers are organiser-cell scalars".
- **EXACT_FILE_AND_LINES** `/home/claude/edl/MYQBD01/code/myqbd01_spatial_feedback.py:50-58` (the `SUBSTEP_LEDGERS_ARE_SCALAR` block); the ledger it misdescribes is built at `/home/claude/OBFOR01/code/run_obfor01.py:65-67, 78` and reshaped at `:126-127`.
- **EXACT_NUMBERS** `source_substep_ledger` is (44000, 6) with columns `(step, species_index, org_y_before, org_x_before, org_y_after, org_x_after)`: **4 of its 6 columns are lattice coordinates**, at 4 sub-steps × 11 000 steps. It fully determines the organiser trajectory at sub-step resolution — verified: it yields 1015–1133 moves over 324–455 distinct cells for each mobile arm and exactly 0 moves / 1 cell for each static arm, and it agrees with the `frames` organiser coordinates in 220/220 frames.
- **WHY_IT_MATTERS** The one key the brief singles out for attack is the one the candidate describes wrongly. The load-bearing conclusion survives (knowing *where* the Y is does not give `nX`, `nSY`, `free` *there*), but a reader relying on §12 would conclude no Y position is recorded at all, and `Q_LINEAGE` for the founder — which *is* fully available, since the recorded Q is Q along a genuinely mobile Y trajectory — would be wrongly written off.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/MYQBD01/review/work/a4_detail.py` (prints the ledger rows) and `.../a3_arms.py` (org_moves / org_cells columns).
- **MINIMUM_REQUIRED_CHANGE** Rename the key to `SUBSTEP_LEDGER_CONTENTS` and state the actual column semantics of all four ledgers; record that `Q_ORGANISER == Q_LINEAGE` holds for the founder in the mobile branch too (not only the static branch, as `MYQBD01_Q_PHASE_MAP.json` `EQUALITIES_IN_THE_ONE_Y_BASELINE` currently implies).
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** contradicts — the prior review repeated the same "substep ledgers are organiser-cell scalars" formulation and did not open the array.

### F09
- **ID** F09
- **ATTACK** A4
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** That §12's evidence establishes `Q_POSITION_RECOVERABLE_FOR_A_SEPARATED_DESCENDANT = False` and `ORGANISER_ONLY_ENVIRONMENT_AVAILABLE`.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/MYQBD01/code/myqbd01_spatial_feedback.py:28-87`. Specifically: line **30** `f = sorted(glob.glob(os.path.join(RAW, "*.npz")))[0]` — **one** archive of 28; lines **35-37** compute `per_step_spatial` and `terminal_spatial` from shapes only; line **40** `per_step_are_scalar = all(z["series"].ndim == 2 and z["series"].shape == (HORIZON, 29) for _ in [0])` — a one-element generator, i.e. a no-op comprehension that evaluates a *shape* condition and is reported under the name "fields are scalar"; lines **50-58** report only `.shape` for the four ledgers; line **59** `"Q_POSITION_RECOVERABLE_FOR_A_SEPARATED_DESCENDANT": False` is a **hardcoded literal**, not a computed result.
- **EXACT_NUMBERS** Archives examined by §12: **1 of 28** (`M__seed9300014`, first in sorted order). Keys whose *contents* §12 inspects: **0** of 15. Computed booleans in the returned dict: `FULL_SPATIAL_FIELD_IS_TERMINAL_ONLY` (from `len(per_step_spatial) == 0`) and `PER_STEP_FIELDS_ARE_SCALAR_ORGANISER_AGGREGATES` (from a shape check). The load-bearing flag is a literal.
- **WHY_IT_MATTERS** The correct conclusion is reached from an incomplete key enumeration. The mission's terminal disposition turns on this single boolean, and as delivered it is asserted rather than derived. I have independently derived it (F07), so the conclusion stands — but the candidate's own evidence does not carry it, and a differently-shaped archive would have produced the same hardcoded `False`.
- **SETTLING_COMMAND_OR_CALCULATION** Read `myqbd01_spatial_feedback.py:28-87`; compare with the enumeration in §1.1 of this review, which covers all 15 keys × 28 archives.
- **MINIMUM_REQUIRED_CHANGE** Replace the literal with a derivation over **all 28 archives** that (i) asserts the key set is identical, (ii) asserts no array has shape (T, L, L), (iii) decodes `frames` and asserts every value is a scalar, (iv) asserts `birth_offsets[:,1:3] == 0` everywhere, and (v) reports the per-column semantics of the three ledgers from the writer `run_obfor01.py:65-87`.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** contradicts — the prior review recorded this as a load-bearing attack "refuted at source"; the source it refers to does not perform the check.

### F10
- **ID** F10
- **ATTACK** A4
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** The stated *reason* `Q_POSITION` is unavailable ("a mobile descendant that separates occupies a DIFFERENT cell whose (nX, nSY, free) at that time is not recorded").
- **EXACT_FILE_AND_LINES** `/home/claude/edl/MYQBD01/code/myqbd01_spatial_feedback.py:61-71` (`WHY`, `CONSEQUENCE_FOR_THE_MOBILE_BRANCH`) — the reason given is *non-recording*. The decisive fact is stated only in the other function, `:125-127` (`THE_ARCHIVE_HAS_kY_ZERO`), and never enters §12.
- **EXACT_NUMBERS** `kY = 0.0` and `muY = 0.0` (`obtc02_protocol.yaml` `point:`), propagated by `protocol_obtc02.spec_for` and `run_obfor01.build`. Verified in the data: `N_Y ≡ 1` and `n_org_cells ≡ 1` at **308 000 / 308 000** recorded steps across all 28 arms; total Y births = **0**.
- **WHY_IT_MATTERS** "Not recorded" invites the rebuttal "then re-derive it". "The event has probability zero under the archives' own law" does not. The candidate's §12 argument is strictly weaker than the argument available to it, and this weakness is exactly what an attacker aims at.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/MYQBD01/review/work/a4_recon.py` (prints the N_Y / n_org_cells check over all 28 arms).
- **MINIMUM_REQUIRED_CHANGE** Add to §12's `WHY`: with `kY = 0` no Y birth occurs in any arm (verified `N_Y ≡ 1` over 308 000 steps), so a separated descendant does not merely go unrecorded — it never exists; `Q_POSITION` for it is not a function of these data at all.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** new.

### F11
- **ID** F11
- **ATTACK** A4
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_PLAUSIBLE
- **CLAIM_ATTACKED** Implicitly, that PQEC01 must consist of ≥ 30 *fresh* worlds because the spatial fields of the existing arms are unavailable.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/MYQBD01/out/HANDOFF_PROSPECTIVE_Q_ENVIRONMENT_CALIBRATION_01.md` §3 (`nombre de mondes indépendants : à fixer (>= 30 recommandé)`); §2 ("par des mondes neufs et indépendants"). Determinism: `kinetics.py:76` `self.rng = np.random.default_rng(seed)`; `lawspec_v2.py:82-83`; `engine_obtc.py:43`; inertness of observers already demonstrated at `run_obfor01.py:169-185`.
- **EXACT_NUMBERS** The 28 seeds are in the filenames (9300000–9300027) and in `/home/claude/OBFOR01/out/_validation.json`; the spec is frozen. The trajectories are therefore a deterministic function of (seed, spec), and re-running the same 28 seeds with an added *observer-only* position-resolved recorder would reproduce the identical 308 000 steps and yield `nX(x,t)`, `nSY(x,t)`, `free(x,t)` exactly. Cost: 28 world constructions vs ≥ 30.
- **WHY_IT_MATTERS** This is the strongest available counter to "unrecoverable", and it must be answered explicitly rather than ignored. My judgement: re-simulation is a **RUN, not a recovery**. It is forbidden to this review (`SCIENTIFIC_RUNS_USED_BY_REVIEW = 0`), it is not "recoverable from the archives" in any sense the brief's question uses, and — decisively — it inherits `kY = 0`, so it would still produce **no descendant**. It therefore does not overturn F07. But it does bear on the *successor*: the existing arms' spatial fields are re-derivable, and the reason PQEC01 needs fresh worlds is **prospectivity** (the 28 arms are `POST_OUTCOME_DEVELOPMENT_DIAGNOSTIC` and their outcomes are already opened), not unavailability. Graded `DEFECT_PLAUSIBLE` because the handoff's *conclusion* (fresh worlds) is right while its *stated ground* is incomplete.
- **SETTLING_COMMAND_OR_CALCULATION** Read `run_obfor01.py:169-185` (the instrumentation-inertness test, which already proves an added observer does not move the RNG stream) together with `_validation.json` `SEEDS`.
- **MINIMUM_REQUIRED_CHANGE** One paragraph in `HANDOFF_PROSPECTIVE_Q_ENVIRONMENT_CALIBRATION_01.md` §3: state that the 28 parent arms' position-resolved fields are deterministically re-derivable by re-instrumenting seeds 9300000–9300027, that this is nevertheless not admissible as the calibration because those arms are post-outcome and carry `kY = 0`, and that fresh, prospectively frozen, `kY`-active worlds are required for that reason.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** new.

### F12
- **ID** F12
- **ATTACK** A5
- **SEVERITY** SUBSTANTIVE
- **STATUS** ATTACK_REFUTED
- **CLAIM_ATTACKED** (side a) That `β = kY·E[Q]` might fail even for the first birth, because of the clamp `p = min(1, kY·nX·nY)` and because `E[Q]` averages a correlated series.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/MYQBD01/code/myqbd01_operators.py:99-132` (conditions 3, 7, 8); engine `engine_obtc.py:165-167`.
- **EXACT_NUMBERS** Clamp: the maximum `u_nX_at_org` over all 28 arms × 11 000 steps is **15**, and `nY ≡ 1`, so at the discovery-scale `kY = 4e-5` the clamp argument is at most `6.0e-4`. The clamp is active on **0 of 126 000** in-window mobile steps (fraction `0.000e+00`). Correlation: the expected first-birth count is `E[Σ_t c_t p_t] = kY·Σ_t E[Q_t]` by linearity of expectation, which holds for any dependence structure whatever; autocorrelation affects the *variance* of the estimate, not the *mean*, and the candidate handles that separately by using 14 arms.
- **WHY_IT_MATTERS** If the scalar reduction failed even for the first birth, the one thing the mission declares constructible would collapse.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/MYQBD01/review/work/a6_a8.py`.
- **MINIMUM_REQUIRED_CHANGE** None.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** new.

### F13
- **ID** F13
- **ATTACK** A5
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** (side b) `SCALAR_Q_REDUCTION_VALID_ONLY_FOR_FIRST_BIRTH` "fails on at least four independent counts", two of which are (7) temporal correlation and (8) the arithmetic-mean-vs-multiplicative-growth gap. The candidate is **too pessimistic** on those two.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/MYQBD01/code/myqbd01_operators.py:116-124` (conditions 7 and 8) and `:138-143` (`WHY`); mirrored in `/home/claude/edl/MYQBD01/out/MYQBD01_TWO_Y_OPERATOR.json`.
- **EXACT_NUMBERS** For a lineage in the recorded (exogenous) environment the quenched growth exponent is `mean_t log R_t` with `R_t = (1−muY)(1 + c_t·p_t)`, `c_t = cand_Y_at_org(t)`, `p_t = min(1, kY·nX_t)`. Computed exactly over the 14 mobile arms at `kY = 4e-5`, `muY = 1.9511206603301160e-06`:
  `mean_t log R_t = 1.248125298e-04`; the scalar reduction `kY·E[Q] − muY = 1.248380857e-04`. **Relative discrepancy 2.0471e-04.** Because `kY·Q_t ≤ kY·Q_max = 4e-5 × 28 = 1.12e-3`, `log(1+x) = x + O(x²/2)` bounds the gap by ≤ 5.6e-4 relative *a priori*.
  Consequently the long `Q = 0` episodes (frac(Q=0) ≈ 0.53–0.59) are fully absorbed by the arithmetic mean at admissible `kY`, and correlation does not enter the exponent at all.
- **WHY_IT_MATTERS** Two of the four cited grounds for the classification do not bind at the magnitudes this mission is about. The classification itself survives on grounds (5) SY depletion and (9) descendant exposure, both of which are real — so this is not load-bearing. But a reader is told the scalar reduction fails four ways when at `kY = 4e-5` two of those ways are ~1e-4 effects.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/MYQBD01/review/work/a6_a8.py` (section "A5(b)").
- **MINIMUM_REQUIRED_CHANGE** Annotate conditions 7 and 8 in `MYQBD01_TWO_Y_OPERATOR.json` with the measured magnitude at the discovery scale (relative gap 2.05e-4) and state that the classification rests on conditions 5 and 9.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** new.

### F14
- **ID** F14
- **ATTACK** A6
- **SEVERITY** LOAD_BEARING
- **STATUS** ATTACK_REFUTED
- **CLAIM_ATTACKED** Two co-located Y draw **one** `Binomial(c, min(1, kY·nX·2))` from a shared candidate pool, so the process is not Galton–Watson; and the demonstration numbers (support 4 vs 8, variance 0.84 vs 1.02; clamped means 4.0 vs 4.8).
- **EXACT_FILE_AND_LINES** Engine: `/home/claude/OBTC02/code/engine_obtc.py:160-167` — `pair = nX*nY` is formed once, `cand = np.minimum(self.n["SY"], free0)` is **one** pool per cell, and one `rng.binomial(cand, p)` is drawn per cell irrespective of `nY`; the `nY` dependence lives entirely inside `p`. Candidate derivation: `/home/claude/edl/MYQBD01/code/myqbd01_operators.py:148-215`.
- **EXACT_NUMBERS** Recomputed independently: unclamped `c=4, kY=0.05, nX=3` → `p1 = 0.15`, `p2 = 0.30`; true mean 1.200000 = naive mean 1.200000; **true variance 0.840000 vs naive 1.020000**; **support max 4 vs 8**. Clamped `c=4, kY=0.20, nX=3` → `p1 = 0.60`, `p2 = 1.00`; **true mean 4.000000 vs naive 4.800000**; true variance 0.000000 vs naive 1.920000. All four published numbers reproduce exactly.
- **WHY_IT_MATTERS** If the two-Y process *were* a sum of independent one-Y operators, the two-Y operator would be identifiable from the one-Y ledger and `TWO_Y_STATE_OPERATOR_VERIFIED` could flip.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/MYQBD01/review/work/a6_a8.py` (section A6); source read of `_react_core`.
- **MINIMUM_REQUIRED_CHANGE** None.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** repeats and deepens — the prior review made the same structural point; the exact recomputation of all four numbers is added.

### F15
- **ID** F15
- **ATTACK** A6
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** That the exhibited counterexample demonstrates material non-independence in the regime this mission concerns.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/MYQBD01/code/myqbd01_operators.py:178-179` — `unclamped = one_point(4, 0.05, 3)`, `clamped = one_point(4, 0.20, 3)`; the admissible scale is `kY_box = 4e-5` at `myqbd01_regions.py:91`.
- **EXACT_NUMBERS** The demonstration `kY` values are **0.05 and 0.20**, i.e. **1 250×** and **5 000×** the admissible `4e-5`. Recomputed at admissible magnitudes: for `c = 3, kY = 4e-5, nX = 4` (`p1 = 1.600e-04`, `p2 = 3.200e-04`) the means are exactly equal, the variances are 9.596928e-04 (shared pool) vs 9.598464e-04 (naive) — a **relative gap of −1.600e-04** — and the probability that the naive independent sum exceeds the shared-pool cap `c` is **9.83e-15**. At `nX = 15`: relative variance gap −6.004e-04, excess probability 1.94e-12. At `c = 7`: −1.600e-04 and 1.29e-27.
- **WHY_IT_MATTERS** `IS_GALTON_WATSON = False` is exactly true as a structural statement (F14) — but at the magnitudes the mission is about, a Galton–Watson approximation would carry a certified relative error of ~1e-4. §11 uses non-Galton-Watson-ness as one of its grounds for `NOT_IDENTIFIABLE`; that ground is quantitatively weak. The binding ground — separated Y occupy different, unrecorded cells — is untouched, so the status does not change.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/MYQBD01/review/work/a6_a8.py` (section "ADMISSIBLE SCALE").
- **MINIMUM_REQUIRED_CHANGE** Add an `ADMISSIBLE_SCALE_MAGNITUDE` block to `MYQBD01_TWO_Y_OPERATOR.json` reporting the −1.6e-4 relative variance gap and the 9.8e-15 support-excess probability at `kY = 4e-5`, and state that `NOT_IDENTIFIABLE` rests on the spatial ground, not on the branching-process ground.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** contradicts — the prior review wrote "the mean coincidence in the unclamped regime is not fatal" and closed the item; it never evaluated the coupling at the admissible `kY`, where it is ~1e-4.

### F16
- **ID** F16
- **ATTACK** A7
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** The recovery model: "`_exchange` offers `Binomial(max(S0 − nSY, 0), phi)` toward S0 = 3 at rate phi = 0.20 per step, per cell", giving `recovery_rate_per_step = 0.20` and `steps_to_replenish_one_unit ≈ 5`.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/MYQBD01/code/myqbd01_spatial_feedback.py:130-134, 141-151`; the operator itself at `/home/claude/ORR01/code/lawspec_v2.py:90-129`, in particular `:105` `taken = _hyper_split(rng, pool, k)` and `:106-108`, which **remove** units drawn without replacement from the pool `{SX, SY, WX, WY}` — SY included.
- **EXACT_NUMBERS** Measured directly on the 14 **static** arms, where the organiser cell is fixed at (18,18) so `nSY_at_org` is a clean fixed-cell series: regressing `Δ nSY(t)` on `(S0 − nSY(t))` over steps 2000–10999 gives slope **0.355735 ± 0.013473** (sd over 14 arms), against the claimed `phi = 0.20`. **Ratio measured/claimed = 1.779.** The model is missing the hypergeometric removal term entirely; the true SY dynamics are `+ins_sy − taken_SY`, and the candidate models only `+ins_sy`.
- **WHY_IT_MATTERS** §13 is labelled `…WITH_CERTIFIED_ERROR`. The certificate's relaxation rate is wrong by 78 %. It does not flip a requirement — `FROZEN_ENVIRONMENT_ERROR_CONTROLLED` is already `False` — but a certificate whose numbers are wrong is not a certificate, and a successor could carry the 0.20 figure forward.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/MYQBD01/review/work/a1_a5_a7.py` (final section).
- **MINIMUM_REQUIRED_CHANGE** Replace `recovery_rate_per_step: phi` with the measured effective mean-reversion rate 0.3557 (14 static arms, sd 0.0135), and state that under `LAWSPEC_V2_EXCHANGE` the SY balance is `+Binomial(max(S0−nSY,0), phi) − hypergeometric removal from {SX,SY,WX,WY}`, not the additive feed of `kinetics._feed_and_outflow`.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** new — the prior review's C1 repair addressed only *where phi was read from*, never whether the model in which phi appears is the operator that ran.

### F17
- **ID** F17
- **ATTACK** A7
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** "one Y birth removes one SY at the organiser cell, a 100 % local reduction of the ~0.99 mean nSY" — i.e. `as_fraction_of_mean_nSY = −1 / nSY_mean`.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/MYQBD01/code/myqbd01_spatial_feedback.py:143-151`; the conditioning that the engine actually imposes is at `engine_obtc.py:166-167` (`cand = min(nSY, free0)`; a birth is possible only where `cand ≥ 1`).
- **EXACT_NUMBERS** Unconditional mobile in-window mean `nSY_at_org` = **0.985048**, giving the candidate's 1/0.985048 = **101.5 %**. But a Y birth can occur only when `cand_Y ≥ 1`, and conditional on that, mobile `E[nSY_at_org | cand_Y ≥ 1]` = **1.814057** (and `E[cand_Y | cand_Y ≥ 1]` = 1.777084). The correct local depletion is **1/1.814057 = 55.1 %**, not 101.5 % — the claim overstates the perturbation by a factor **1.84**. (Static arms: mean `nSY_at_org` = 0.470254, mean `cand_Y` = 0.466000, mean `u_nX_at_org` = 5.208119; mobile mean `u_nX_at_org` = 4.312563, mean `cand_Y` = 0.961651.)
- **WHY_IT_MATTERS** The brief asks whether a ~100 % local depletion is consistent with calling the first-birth error "controlled". The premise is wrong: conditioned on the event that can actually trigger the depletion, it is ~55 %. This makes the first-birth error *more* defensible than the candidate claims — the defect is an overstatement against the candidate's own interest, but it is still a wrong number in a document whose classification name contains "CERTIFIED_ERROR".
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/MYQBD01/review/work/a1_a5_a7.py` (section A7).
- **MINIMUM_REQUIRED_CHANGE** Report the depletion against `E[nSY | cand_Y ≥ 1] = 1.814057` (55.1 %) and keep the unconditional figure only as a marginal statistic, clearly labelled.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** new.

### F18
- **ID** F18
- **ATTACK** A7
- **SEVERITY** COSMETIC
- **STATUS** ATTACK_REFUTED
- **CLAIM_ATTACKED** That S0 and phi come from the actually-loaded spec rather than a class default (the prior review's C1 repair).
- **EXACT_FILE_AND_LINES** `/home/claude/edl/MYQBD01/code/myqbd01_spatial_feedback.py:107-122` (parses the `point:` block of `OBTC02/code/obtc02_protocol.yaml` from the committed blob); the class default it avoids is `/home/claude/ORR01/code/kinetics.py:37` `phi = 0.05`.
- **EXACT_NUMBERS** `obtc02_protocol.yaml` `point:` gives `S0: 3`, `phi: 0.2` — and the loaded spec is built from exactly that block by `protocol_obtc02.spec_for` (`d = {k: PT[k] for k in (…, "phi", …)}`), invoked by `run_obfor01.build:91`. So `phi = 0.2`, not the `kinetics.Spec` default `0.05`. The C1 repair is correct.
- **WHY_IT_MATTERS** A rate read from a class default rather than the executed spec would falsify the whole feedback section.
- **SETTLING_COMMAND_OR_CALCULATION** `grep -n "phi" /home/claude/OBTC02/code/obtc02_protocol.yaml`; `sed -n 31,37p /home/claude/OBTC02/code/protocol_obtc02.py`.
- **MINIMUM_REQUIRED_CHANGE** None (but see F16: the right value is now used in the wrong model).
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** repeats — this is the prior review's C1; I confirm the repair landed.

### F19
- **ID** F19
- **ATTACK** A8
- **SEVERITY** LOAD_BEARING
- **STATUS** ATTACK_REFUTED
- **CLAIM_ATTACKED** (side a) The in-box witness `c = 3, kY = 4e-5, muY = 1.9511e-6` gives `R = 1.000478 > 1`, and the survival iteration converges to a non-degenerate fixed point.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/MYQBD01/code/myqbd01_regions.py:80-98` (`stable_survival`, the witness); `:99-119` (`structural`). PGF `f(z) = (m + (1−m)z)·(1 − p(1−m)(1−z))^c` from `myqbd01_operators.py:44-45`, verified there against an exhaustive enumeration.
- **EXACT_NUMBERS** `p_box = min(1, 4e-5 × 4 × 1) = 1.60000000e-04`; `R_box = (1 − 1.9511206603301160e-06)(1 + 3 × 1.6e-4) = **1.000478048**`, `R − 1 = 4.780479e-04` — the reported 1.000478 is exact. The iteration `s ← 1 − (1 − (1−m)s)(1 − p(1−m)s)^c` from `s = 1` gives 0.9984518240 (T=1000), 0.9963072594 (5000), **0.9959575009 (T = 11000, the reported value)**, 0.9959364528 (50 000), 0.9959364528 (200 000), 0.9959364528 (10^6). An independent bisection on the extinction equation `η = f(η)` gives the minimal fixed point `η* = 0.004063547247`, i.e. asymptotic survival **0.995936452753**. The T = 11000 iterate differs from the exact limit by **2.1e-5**. The fixed point is converged and is **not** numerically degenerate. Independent check of the PGF itself: `myqbd01_operators.py` verifies the closed form against brute-force enumeration over (parent survives, #births, #newborn survivors) with max abs error **2.2e-16** at 5 test points.
- **WHY_IT_MATTERS** If `R > 1` failed or the fixed point were degenerate, `STRUCTURAL_PRECLUSION_PROVED = false` would lose its witness and the disposition could become `STRUCTURAL_PRECLUSION_PROVED`.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/MYQBD01/review/work/a6_a8.py` (section A8).
- **MINIMUM_REQUIRED_CHANGE** None.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** deepens — the prior review's C2 repair introduced the witness; this is the first check that its fixed point converges and matches an independent root-find.

### F20
- **ID** F20
- **ATTACK** A8
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** That `c_box = 3` is "near the mean organiser-cell candidate pool", and the framing that the check evaluates "the MOST FAVOURABLE admissible environment (Q sustained at Q_MAX)".
- **EXACT_FILE_AND_LINES** `/home/claude/edl/MYQBD01/code/myqbd01_regions.py:78-79` (docstring: "Q sustained at Q_MAX"), `:90` (`c_box = 3  # near the mean organiser-cell candidate pool in the arms`), `:92` (`p_box = min(1.0, kY_box * 4 * 1)` — `nX` **hardcoded to 4** with no comment), `:22` (`Q_MAX = 28`), `:104-105` (the `note` repeating the claim).
- **EXACT_NUMBERS** The mobile arms' actual mean `cand_Y_at_org` is **0.961651**, so `c_box = 3` is **3.12×** it, not "near" it. The hardcoded `nX = 4` is 0.93× the actual mean `u_nX_at_org` = 4.312563 (that one is fair, but it is the seed value `X_SEED = 4`, unexplained). The witness's exposure is `c·nX = 12`, which is **3.79×** the arms' own measured mean `Q = 3.169730` — and simultaneously only 12 of `Q_MAX = 28`, so it is neither "near the mean" nor "the most favourable". Further, `(R − 1)/σ² = 0.9921` with offspring variance σ² = 4.818734e-04, so this is *not* the near-critical regime the phrase "so marginal it is indistinguishable from criticality" would suggest; the survival of 0.9959 is carried chiefly by `muY = 1.95e-6` (near-immortality of the founder), not by supercriticality.
- **WHY_IT_MATTERS** The witness is the sole evidence for `STRUCTURAL_PRECLUSION_PROVED = false`. Its exposure is inflated 3.79× over the measured environment and its description is inconsistent with both the code and the data. Not load-bearing only because the conclusion survives without the inflation — see F21.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/MYQBD01/review/work/a6_a8.py` (section A8).
- **MINIMUM_REQUIRED_CHANGE** In `MYQBD01_DISCOVERY_REGION.json`, replace the `c_box` note with the measured mean `cand_Y_at_org = 0.961651`, justify or remove the hardcoded `nX = 4`, drop the "Q sustained at Q_MAX" framing (the witness uses 12, not 28), and add the measured-environment witness of F21.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** contradicts in part — the prior review's C2 repair *created* this witness and certified it "in-box"; it never checked `c_box` against the arms.

### F21
- **ID** F21
- **ATTACK** A8
- **SEVERITY** SUBSTANTIVE
- **STATUS** ATTACK_REFUTED
- **CLAIM_ATTACKED** (side b, arguing the opposite as the brief requires) That with `R − 1 ≈ 4.8e-4` the witness is so marginal as to be vacuous, and that `Q10 = 0` (Q = 0 more than half the time) makes the sustained-`c = 3` premise inadmissible — so that non-preclusion is not established.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/MYQBD01/code/myqbd01_regions.py:99-119`; the `Q10 = 0` facts at `myqbd01_regions.py:49-54` and reproduced here from raw.
- **EXACT_NUMBERS** The attack fails, and non-preclusion is in fact **more robust than the candidate shows**. Drop the witness entirely and use the arms' own measured environment: `R = (1 − muY)(1 + kY·E[Q]) = (1 − 1.9511206603301160e-06)(1 + 4e-5 × 3.169730) = **1.000124838 > 1**`. The margin is structural: `kY·E[Q] = 1.267892e-04` exceeds `muY = 1.9511206603301160e-06` by a factor **64.98**. And the `Q10 = 0` objection is answered quantitatively by F13: the quenched exponent `mean_t log R_t = 1.248125e-04` versus the arithmetic-mean reduction `kY·E[Q] − muY = 1.248381e-04`, a relative discrepancy of **2.05e-04** — so the long zero-exposure episodes (frac(Q = 0) = 0.5262–0.5902 mobile, 0.6264–0.6683 static) are fully absorbed by the mean at admissible `kY` and do not invalidate the premise. To *prove* structural preclusion one would need `sup` over the admissible box of `E[log R_t]` ≤ 0, i.e. `kY·E[Q] ≤ muY/(1−muY)`, which at `E[Q] = 3.169730` would require `kY ≤ 6.16e-07` — two orders of magnitude below the frozen discovery scale. That is precisely what would settle it, and it is false in the box.
- **WHY_IT_MATTERS** This is the one place where a confirmed defect could have flipped the verdict to `STRUCTURAL_PRECLUSION_PROVED`. It does not: the conclusion holds on the arms' own numbers without any inflated witness.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/MYQBD01/review/work/a6_a8.py`.
- **MINIMUM_REQUIRED_CHANGE** None to the conclusion; adding the measured-environment witness (F20) would make it self-evident.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** deepens — the prior review asserted "an admissible supercritical witness exists"; this replaces the assertion with the measured-environment computation and the exact preclusion threshold `kY ≤ 6.16e-07`.

### F22
- **ID** F22
- **ATTACK** A9
- **SEVERITY** SUBSTANTIVE
- **STATUS** ATTACK_REFUTED
- **CLAIM_ATTACKED** All 28 delivered arms are used, none dropped, and no inclusion rule is conditioned on an outcome.
- **EXACT_FILE_AND_LINES** Every `glob` in the candidate: `myqbd01_arms.py:85` `"*.npz"`; `myqbd01_operators.py:87` `"M__*.npz"`; `myqbd01_regions.py:29` `"%s*.npz"` called with `"M__"`; `myqbd01_spatial_feedback.py:30` `"*.npz"` then `[0]`, and `:95` `"M__*.npz"`. Branch labels come from `myqbd01_arms.py:84, 102` via `_validation.json`.
- **EXACT_NUMBERS** `_validation.json` declares **28** arm tags; the raw directory holds **28** `.npz`; the two sets are equal (0 files without a declaration, 0 declarations without a file), so the `dec.get("condition")` path cannot silently yield `branch = None` and drop an arm. Conditions: S = 14, M = 14. Seeds 9300000–9300027, all distinct. `extinct` = `[]`. Delivered counts reproduce exactly: `TOTAL_ARMS == 28`, `STATIC == 14`, `MOBILE == 14`, `TOTAL_FRAMES == 308000`, `Q_MISSING == 0`, `Q_MAX == 28` — all `true`. No glob or filter references any outcome quantity.
- **WHY_IT_MATTERS** A silent exclusion, or an outcome-conditioned inclusion rule, would make the branch means selection artefacts.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/MYQBD01/review/work/a3_arms.py`; the tag/file set comparison in the A9 block of this review's transcript.
- **MINIMUM_REQUIRED_CHANGE** None.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** new.

### F23
- **ID** F23
- **ATTACK** A9
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** That the §12 spatial classification is drawn from the delivered arm set.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/MYQBD01/code/myqbd01_spatial_feedback.py:30`: `f = sorted(glob.glob(os.path.join(RAW, "*.npz")))[0]`.
- **EXACT_NUMBERS** **1 of 28** archives is opened (`M__seed9300014.npz`, first in sorted order — and it is a *mobile* arm, so no static archive is examined at all by §12). The classification `ORGANISER_ONLY_ENVIRONMENT_AVAILABLE` and the boolean that blocks the positive disposition are produced from that single file. I verified independently that all 28 share the identical 15-key set and identical shapes for the 12 fixed-shape keys, so the generalisation happens to be sound.
- **WHY_IT_MATTERS** An arm-selection defect in the one section that decides the disposition. It is not outcome-conditioned (it is lexicographic), so it is not a bias — but it is a coverage failure in the load-bearing section, and its soundness was established by me, not by the candidate.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/MYQBD01/review/work/a4_recon.py` (first block asserts the key set across all 28).
- **MINIMUM_REQUIRED_CHANGE** Loop `spatial_recoverability()` over all 28 archives and assert key-set and shape identity, reporting per-arm.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** new.

### F24
- **ID** F24
- **ATTACK** A10
- **SEVERITY** LOAD_BEARING
- **STATUS** ATTACK_REFUTED
- **CLAIM_ATTACKED** `NO_TARGET_DERIVED_Y_OUTCOME` — no MYQBD01 computation consumes a quantity derived from the target it is meant to predict (e.g. an `r80`-like statistic), including via laundering through intermediate files.
- **EXACT_FILE_AND_LINES** Enumerated over all 8 modules in `/home/claude/edl/MYQBD01/code/`. Archive keys opened: `series`, `fields`, `nX_final` (shape only, `myqbd01_arms.py:107`; `myqbd01_spatial_feedback.py:33`), and `hop_ledger`/`source_substep_ledger`/`birth_substep_ledger`/`birth_offsets` (shape only, `myqbd01_spatial_feedback.py:51-54`). Series columns read, exhaustively: `Q` (×3), `u_nX_at_org` (×3), `n_org_cells` (×2), `nSY_at_org` (×2), `free_at_org` (×2), `cand_Y_at_org` (×1). Intermediate files read: `_validation.json` (`myqbd01_arms.py:83`), from which only `condition`, `seed`, `L` and `tag` are taken (`:84, 102, 106-107`).
- **EXACT_NUMBERS** The `frames` key — which is the sole container of the OBTC02/OBFOR01 target statistics `r80`, `r80_organiser`, `Rg`, `r50`, `r90`, `centre_y/x`, `organiser_to_core`, `main_mass_fraction`, `core_fraction` — is opened by **0** of the 8 modules. The string `r80` occurs **0** times in the candidate source. `_validation.json` does contain `r80_median`, `r80_mean`, `r80_sd`, `r80_skew` per arm, and **none of those keys is read**. All 6 series columns consumed are environmental (organiser-cell resource/capacity/body-count), and none is a Y outcome: with `kY = muY = 0` there is no Y outcome in these archives at all (`N_Y ≡ 1`).
- **WHY_IT_MATTERS** If an `r80`-like statistic entered, the Q analysis would be conditioned on the very outcome the successor test must predict.
- **SETTLING_COMMAND_OR_CALCULATION** `grep -ohn 'fields.index("[a-zA-Z_]*")\|f.index("[a-zA-Z_]*")\|F.index("[a-zA-Z_]*")\|z\["[a-zA-Z_]*"\]' /home/claude/edl/MYQBD01/code/*.py | sort -u`; `grep -c r80 /home/claude/edl/MYQBD01/code/*.py`.
- **MINIMUM_REQUIRED_CHANGE** None to the conclusion.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** new — independently re-derived, as the brief requires.

### F25
- **ID** F25
- **ATTACK** A10
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** That `NO_TARGET_DERIVED_Y_OUTCOME` is established by an AST-based check with zero data accesses.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/MYQBD01/code/myqbd01_regions.py:131`: `"NO_TARGET_DERIVED_Y_OUTCOME": True,  # Q is environmental, not a Y outcome` — a hardcoded literal with a comment. The only `ast` usage in the mission is `/home/claude/edl/MYQBD01/code/myqbd01_phase.py:8, 49-60`, and it extracts the **scheduler call order** from `kinetics.World._one_step`; it performs no data-access audit of any kind.
- **EXACT_NUMBERS** AST-based data-access checks in the candidate: **0**. Modules importing `ast`: 1 of 8, for an unrelated purpose. Occurrences of `NO_TARGET_DERIVED_Y_OUTCOME` as a computed value: 0; as a literal: 1 (propagated verbatim into `MYQBD01_DISCOVERY_REGION.json`, `MYQBD01_FINAL_DISPOSITION.json`, `MYQBD01_MASTER_FREEZE.json`).
- **WHY_IT_MATTERS** A requirement in the frozen positive-disposition checklist is asserted, not verified. It happens to be true (F24), but nothing in the delivery demonstrates it, and the mechanism attributed to it does not exist.
- **SETTLING_COMMAND_OR_CALCULATION** `grep -n "ast\." /home/claude/edl/MYQBD01/code/*.py`; `grep -n "NO_TARGET_DERIVED" /home/claude/edl/MYQBD01/code/*.py`.
- **MINIMUM_REQUIRED_CHANGE** Add a real audit: walk each module's AST, collect every `*.index("…")` string constant and every `z["…"]` subscript, and assert the resulting set is disjoint from the target-statistic set `{r80, r80_organiser, Rg, r50, r90, centre_y, centre_x, organiser_to_core, main_mass_fraction, core_fraction, n_eff_components, geodesic_diameter}` and from the key `frames`.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** new.

### F26
- **ID** F26
- **ATTACK** A11
- **SEVERITY** SUBSTANTIVE
- **STATUS** ATTACK_REFUTED
- **CLAIM_ATTACKED** All 28 arms are labelled `POST_OUTCOME_DEVELOPMENT_DIAGNOSTIC`, and nowhere is a developmental quantity used as if confirmatory, nor is a forbidden claim (reproduction, heredity, autonomous cohesion, H3, a minority window, Kamimura–Kaneko) implied.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/MYQBD01/out/MYQBD01_FINAL_DISPOSITION.json:5` (`ARMS_STATUS`), `:70-77` (`STATUSES_REPORTED_UNCONDITIONALLY`); `MYQBD01_MASTER_FREEZE.json` `CLAIM_CEILING` and `:85`; `MYQBD01_MASTER_FREEZE.md:117`; `MYQBD01_FINAL_REPORT.md:15`; `MYQBD01_MOBILE_ARM_REGIONS.json` (the one quantitative per-arm output).
- **EXACT_NUMBERS** Scan over all 10 delivered `.md`/`.json` outputs: "Kamimura" **0** occurrences, "Kaneko" **0**, "autonomous cohesion" **0** outside the status line `AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED`, "minority window" **0**. Every occurrence of "reproduction"/"reproducti"/"heredity"/"H3" is a negation or an unconditional status: `H3_STATUS = NOT_TESTED`, `REPRODUCTION_STATUS = NOT_TESTED`, `CLAIM_CEILING = "… never reproduction or heredity"`, `MYQBD01_FINAL_REPORT.md:15` "Aucune borne sur `Q` n'a été gelée avant leur exécution", `MYQBD01_MASTER_FREEZE.md:117` "No later wording may erase the `POST_OUTCOME_DEVELOPMENT_DIAGNOSTIC` status of the 28". The only quantitative per-arm output, `kY_for_one_expected_first_birth`, is explicitly hedged at `myqbd01_regions.py:148-150`: "it only says a first birth can occur; it says nothing about persistence, separation or a third centre." The terminal disposition is negative, so no developmental quantity carries a confirmatory load anywhere.
- **WHY_IT_MATTERS** A developmental diagnostic presented as confirmatory would be the single most damaging failure available to this mission.
- **SETTLING_COMMAND_OR_CALCULATION** `grep -ih "reproduction\|heredity\|H3\|Kamimura\|autonomous cohesion\|minority window" /home/claude/edl/MYQBD01/out/*.json /home/claude/edl/MYQBD01/out/*.md | sort -u`.
- **MINIMUM_REQUIRED_CHANGE** None.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** new.

### F27
- **ID** F27
- **ATTACK** A12
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** Commit `decfda5`: "Sentinel aggregated over **all analysis processes**, all counters zero."
- **EXACT_FILE_AND_LINES** `SENT.install(...)` appears exactly once, at `/home/claude/edl/MYQBD01/code/myqbd01_arms.py:79-80`. The other seven modules — `myqbd01_phase.py`, `myqbd01_operators.py`, `myqbd01_regions.py`, `myqbd01_spatial_feedback.py`, `myqbd01_final.py`, `myqbd01_bind.py`, `myqbd01_deliver.py` — contain no reference to `pmcr01_sentinel`.
- **EXACT_NUMBERS** Modules with the sentinel installed: **1 of 8**. The delivered `_arms_sentinel.json` is therefore a witness over **one** process, not eight, and there is no aggregation step anywhere.
- **WHY_IT_MATTERS** `SCIENTIFIC_RUNS_USED = 0` is the mission's hardest constraint and the sentinel is its only in-process witness. A claim that it covered all processes when it covered one is a misstatement about the audit itself.
- **SETTLING_COMMAND_OR_CALCULATION** `grep -n "SENT\.\|pmcr01_sentinel" /home/claude/edl/MYQBD01/code/*.py`.
- **MINIMUM_REQUIRED_CHANGE** Either install the sentinel at the top of all eight modules and aggregate the counters into one record, or correct the commit message and `MYQBD01_MASTER_FREEZE` to say "installed in the one module that opens the archives; the remaining seven are shown by static import analysis never to import an engine module" (see F30).
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** new.

### F28
- **ID** F28
- **ATTACK** A12
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** That the sentinel patches `seed_one_organiser` in all the modules that expose it — its own comment says `V2.seed_one_organiser = seeded  # the third seeding entry point, previously unpatched`.
- **EXACT_FILE_AND_LINES** `/home/claude/PMCR01/code/pmcr01_sentinel.py:169-173` patches `K.World.__init__`, `K.World._one_step`, `K.seed_one_organiser`, `EN.seed_one_organiser`, `V2.seed_one_organiser`. The unpatched entry point is `/home/claude/ORR01/code/observe.py:151` `def seed_one_organiser(w, x_seed)`.
- **EXACT_NUMBERS** Module-level `seed_one_organiser` definitions in the engine tree: **4** — `kinetics.py:172`, `observe.py:151`, `lawspec_v2.py:188`, `engine_obtc.py:239`. Patched: **3**. `observe.seed_one_organiser` is missed, and it is a full re-implementation (it does not delegate), so calling it would seed the qualified initial state with `ORGANISER_SEEDINGS` still reading 0.
- **WHY_IT_MATTERS** The brief asks for an attack on the sentinel's coverage rather than its report. The coverage is incomplete by exactly one entry point, and the module comment asserts the enumeration is complete. Materiality is bounded: no MYQBD01 module imports `observe` (F30), so nothing exploited the gap — the counters are genuinely 0.
- **SETTLING_COMMAND_OR_CALCULATION** `grep -n "^def seed_one_organiser" /home/claude/ORR01/code/*.py /home/claude/OBTC02/code/engine_obtc.py`; compare with `pmcr01_sentinel.py:171-173`.
- **MINIMUM_REQUIRED_CHANGE** Add `import observe as OBS; OBS.seed_one_organiser = seeded` to `pmcr01_sentinel.install`, and change the comment to name four entry points.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** new.

### F29
- **ID** F29
- **ATTACK** A12
- **SEVERITY** COSMETIC
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** "the filesystem witness covers the real output roots" / `SCOPE_NOTE: the roots are DISCOVERED by glob over /home/claude/*/raw and /home/claude/*/out, not selected by the audited party`.
- **EXACT_FILE_AND_LINES** `/home/claude/PMCR01/code/pmcr01_sentinel.py:176-186` (`all_mission_output_roots`), `:188-…` (`raw_dir_witness`); the delivered report `/home/claude/edl/MYQBD01/out/_arms_sentinel.json`.
- **EXACT_NUMBERS** The glob is depth-2 only, so it watches **30** roots and misses the repository tree entirely: `/home/claude/edl/*/out` matches **13** existing directories, none watched, and **387** `.npz` files live under `/home/claude/edl`. The witness did fire correctly on the one root that changed — `/home/claude/MYQBD01/out`: files 5 → 9, **npz 0 → 0**, `NO_PHYSICS_ARRAY_WRITTEN = true` — and the two realistic scientific write targets, `/home/claude/OBFOR01/raw` and `/home/claude/OBTC02/raw`, **are** watched (verified). So the gap is real but does not touch the actual write paths of `run_obfor01.run_arm` or `protocol_obtc02.run_arm`.
- **WHY_IT_MATTERS** A witness whose scope is advertised as exhaustive should be exhaustive; "discovered by glob" is true but the glob depth is a hidden selection.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 -c "import glob;print(len(glob.glob('/home/claude/edl/*/out')))"` and the root list in `_arms_sentinel.json`.
- **MINIMUM_REQUIRED_CHANGE** Extend the glob to `/home/claude/**/raw` and `/home/claude/**/out` (or explicitly add the repo tree) and record the depth in `SCOPE_NOTE`.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** new.

### F30
- **ID** F30
- **ATTACK** A12
- **SEVERITY** SUBSTANTIVE
- **STATUS** ATTACK_REFUTED
- **CLAIM_ATTACKED** That, notwithstanding F27–F29, some MYQBD01 script could have started a scientific world, so `SCIENTIFIC_RUNS_USED = 0` is not established.
- **EXACT_FILE_AND_LINES** Complete import lists of all 8 modules in `/home/claude/edl/MYQBD01/code/`.
- **EXACT_NUMBERS** Not one of the 8 modules imports `kinetics`, `observe`, `lawspec_v2`, `engine_obtc`, `protocol_obtc02` or any other engine module. The full import set across the mission is `{__future__, ast, csv, glob, hashlib, json, math, os, shutil, subprocess, sys, tarfile, numpy, pmcr01_sentinel}` — and `pmcr01_sentinel` imports the engine only to *patch* it. A World cannot be constructed from any of these. This is a static proof that is independent of, and stronger than, the runtime counters. The delivered counters agree: `ENGINE_CONSTRUCT_CALLS = ENGINE_ADVANCE_CALLS = SCIENTIFIC_WORLD_STARTS = SCIENTIFIC_SEEDS_OPENED = 0`, `ORGANISER_SEEDINGS = 0`, `SEEDS_SEEN = []`, `VIOLATIONS = []`, `NEW_PHYSICS_ARRAYS_WRITTEN = 0`, `SCIENTIFIC_SEEDS_IN_THE_REGISTERS = 406`.
- **WHY_IT_MATTERS** This is what actually carries `SCIENTIFIC_RUNS_USED = 0`, and it survives every coverage defect in F27–F29.
- **SETTLING_COMMAND_OR_CALCULATION** `for f in /home/claude/edl/MYQBD01/code/*.py; do echo "$f: $(grep -E '^import |^from ' $f | tr '\n' ' ')"; done`.
- **MINIMUM_REQUIRED_CHANGE** None to the conclusion; record the static argument alongside the counters (see F27).
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** new.

### F31
- **ID** F31
- **ATTACK** A12
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** "Master freeze committed **before** detailed trajectory access" (commit `decfda5` message).
- **EXACT_FILE_AND_LINES** `git show --stat decfda5` in `/home/claude/edl`: `MYQBD01/out/MYQBD01_MASTER_FREEZE.md`, `MYQBD01_MASTER_FREEZE.json`, `MYQBD01_ARM_LEVEL_Q_SUMMARIES.csv`, `MYQBD01_ARM_LEVEL_Q_SUMMARIES.json` and `MYQBD01_TEMPORAL_DEPENDENCE.json` all land in **the same commit**.
- **EXACT_NUMBERS** Independent Git checkpoints separating the freeze from the statistics: **0**. Commits on the branch touching MYQBD01: **2** (`decfda5`, `f88147a`), and the freeze is in the first together with every arm-level statistic. The claim of ordering is unverifiable from the repository.
- **WHY_IT_MATTERS** Provenance fact P-2 of the brief. A freeze that cannot be shown to predate the statistics it gates is not a freeze.
- **SETTLING_COMMAND_OR_CALCULATION** `cd /home/claude/edl && git show --stat decfda5`.
- **MINIMUM_REQUIRED_CHANGE** For any successor: commit the freeze alone, in its own commit, before the module that reads trajectory values is run — and record that commit hash inside the freeze. For MYQBD01 itself the defect cannot be repaired retroactively; it must be stated in `MYQBD01_MASTER_FREEZE.md` that no independent checkpoint exists. See §0 P-2 for why no surviving claim depends on the ordering.
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** new — the prior internal review did not examine Git ordering.

### F32
- **ID** F32
- **ATTACK** A11
- **SEVERITY** COSMETIC
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** The seal launcher's `CANDIDATE_REPORTED_TIP = decfda5` identifies the candidate.
- **EXACT_FILE_AND_LINES** Recorded in `/home/claude/MYQBD01/seal/out/SEAL01_CANDIDATE_BINDING.json`; contradicted by `git rev-parse codex/minority-y-q-bound-derivation-01` = `f88147a3b5603aa2c301061c495fdd87200b3b55`.
- **EXACT_NUMBERS** `decfda5` is the tip's parent: exactly **1** commit behind. The extra commit `f88147a` adds `MYQBD01_REVIEW_AND_REPAIR.json`, the three cosmetic repairs C1–C3 and the successor handoff; it removes nothing (verified by `git show --stat`). Working tree clean; 30/30 checksums of the reviewed tree verify.
- **WHY_IT_MATTERS** Provenance fact P-1. A seal bound to the wrong hash binds the wrong artefact; here the reviewed content strictly contains the reported content, so nothing is lost, but the binding record is wrong as written.
- **SETTLING_COMMAND_OR_CALCULATION** `cd /home/claude/edl && git rev-parse codex/minority-y-q-bound-derivation-01 && git log --oneline -2`.
- **MINIMUM_REQUIRED_CHANGE** Update `CANDIDATE_REPORTED_TIP` to `f88147a3b5603aa2c301061c495fdd87200b3b55` in the binding record, or record `decfda5` explicitly as "reported tip, superseded; actual reviewed tip f88147a".
- **RELATION_TO_PRIOR_INTERNAL_REVIEW** new — the prior internal review reviewed `decfda5` and could not have seen this.

---

## 3. ATTACK-BY-ATTACK OUTCOME

| attack | principal claim | outcome |
|---|---|---|
| A1 Q event phase | `Q_LEDGER_EVENT_EXACT` | **stands** (F01); 2 cosmetic citation/labelling defects (F02, F03) |
| A2 temporal dependence | IAT ≈ 7/9, unit = arm, arms independent | **stands** (F04); dispersion understated ~3.8× (F05) |
| A3 branch separation | 2.369048 / 3.169730, robust | **stands** (F06), reproduced exactly, complete separation, exact permutation p = 4.99e-8 |
| A4 descendant exposure | `Q_POSITION` unrecoverable | **stands** (F07); evidence insufficient and one key misdescribed (F08–F10); re-simulation channel is a run, not a recovery (F11) |
| A5 β = kY·E[Q] | valid only for the first birth | **stands** (F12); 2 of its 4 grounds are ~1e-4 effects at admissible kY (F13) |
| A6 two-Y independence | shared pool, not Galton–Watson | **stands** (F14); demonstrated only 1250–5000× above scale (F15) |
| A7 Y feedback | frozen-environment error "certified" | classification stands, but **both certificate numbers are wrong** (F16: 1.78×; F17: 1.84×); S0/phi provenance correct (F18) |
| A8 calibration vs preclusion | `STRUCTURAL_PRECLUSION_PROVED = false` | **stands, and more robustly than shown** (F19, F21); witness inflated 3.79× and mis-described (F20) |
| A9 arm selection | all 28 used, no outcome conditioning | **stands** (F22); §12 reads 1 of 28 (F23) |
| A10 target-derived input | none | **stands**, independently re-derived (F24); the claimed AST check does not exist (F25) |
| A11 claim boundary | no forbidden claim, all arms developmental | **stands** (F26); stale reported tip (F32) |
| A12 zero-run enforcement | `SCIENTIFIC_RUNS_USED = 0` | conclusion stands on a static argument (F30), but the sentinel's **coverage claim fails on three counts** (F27, F28, F29) and the freeze has no independent checkpoint (F31) |

Attacks whose principal claim survived intact: A1, A2, A3, A4, A5, A6, A8, A9, A10, A11 = **10**.
Attacks that landed: **A7** (the §13 certificate is quantitatively wrong in both of its numbers) and
**A12** (the sentinel's advertised coverage is false in three distinct ways).

## 4. DISPOSITION

No load-bearing defect was confirmed. The four pillars of
`EXISTING_Q_DATA_INSUFFICIENT__PROSPECTIVE_Q_CALIBRATION_REQUIRED` each survived a dedicated
attack and were re-derived independently here: the Q ledger is event-exact (F01, 0.000e+00
residual over 308 000 rows); the branch statistics are exact (F06); descendant-position exposure
is genuinely unavailable, and for a stronger reason than the candidate gives (F07, F10); and
structural preclusion is genuinely not proved, more robustly than the candidate shows (F21).
`ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED` follows, and `SCIENTIFIC_RUNS_USED = 0` holds
on a static import argument that is independent of the sentinel's defects (F30).

The candidate is not too conservative: the only additional spatial information extractable from
the archives is a single terminal `Q_POSITION` snapshot per arm, and it points away from a
derivable region (§1.3). It is not too strong: the disposition merely requires a prospective
calibration, which is what the missing ledger warrants.

Fifteen substantive defects remain, concentrated in the *supporting certificates* rather than in
the disposition: §12's evidence is drawn from one archive with a hardcoded conclusion (F09, F23),
§13's two published numbers are wrong by 78 % and 84 % (F16, F17), §11's counterexample is
demonstrated 1250–5000× outside the admissible box (F15), §8's non-preclusion witness is inflated
3.79× (F20), the `NO_TARGET_DERIVED_Y_OUTCOME` requirement is asserted rather than checked (F25),
and the zero-run sentinel's coverage claim is false in three ways (F27–F29) with no independent
Git checkpoint for the freeze (F31). None of these changes the terminal disposition; all of them
should be repaired before the record is carried into PQEC01.

```
REVIEWER_VERDICT              = CANDIDATE_DISPOSITION_SUPPORTED
LOAD_BEARING_DEFECTS          = 0
SUBSTANTIVE_DEFECTS           = 15
COSMETIC_DEFECTS              = 4
ATTACKS_REFUTED               = 10
DESCENDANT_EXPOSURE_RECOVERABLE = NO
SCIENTIFIC_RUNS_USED_BY_REVIEW  = 0
```
