# EXP-RD-03 PROTOCOL (preregistered; frozen before any result is inspected)

## 0. Why this experiment exists (correction of EXP-RD-02)

EXP-RD-02 reported 6/90 audited causal re-establishments and then withdrew all six on an
"observer sensitivity" test. **That test was invalid.** Two defects:

1. **The cadence perturbation was not observer-only.** Enrollment used `t* = WARMUP_SNAP * cadence`,
   so changing the cadence changed the *enrollment time*, and therefore enrolled a **different structure at a
   different time on a different branch trajectory**. That is a physics/enrollment perturbation, not an observation
   perturbation. Its eliminations carry no information.
2. **The tracker perturbation was a no-op.** `tracker_scale` built a `TrackerSpec` that the causal readout never
   consumed (the readout is detection + site proximity; the lineage tracker does not enter it). "Survives tracker
   perturbation" was therefore vacuous.

**Recorded verdict (superseding D-031):** no promotion; **6/90 provisional causal successes**; **observer robustness
UNRESOLVED**. Gray-Scott is **NOT** retired. The six units are **not** recorded as observer failures.

Frozen throughout: thresholds (ORGANIZED_P=0.8, TURNOVER_M=0.5, PLACEBO_MARGIN=0.25, DET.threshold=0.25,
DET.min_cells=12), no composite scores, no visual selection, no mechanism change, no post-hoc halo tuning,
passive tracers never influence dynamics, P never recalibrated.

## PART A — observer-ONLY sensitivity (fixed physics)

**Claim under test:** are the 6 provisional successes an artefact of *how we looked*, or of *what happened*?

**Design.** Per unit (law, seed), the physical trajectory is computed **once**:
- enrollment at the **frozen reference cadence** `REF_CADENCE = 50` → a **single fixed `t*`**, identical for every
  observer setting;
- one fixed pre-intervention state `s*`; the four branches CONTROL / SHAM / PERTURBED / PLACEBO built from `s*`;
- branch snapshots stored **once** at the finest cadence `FINE_CADENCE = 25`.

The observer is then varied **offline on that same stored trajectory**:
- observation cadence ∈ {25, 50, 100} (subsampling the stored snapshots; denominators `n_post` reported per setting:
  30 / 15 / 7);
- readout site radius scale ∈ {0.8, 1.0, 1.2} (SITE_RADIUS = 10.0 cells).

Nothing physical, no branch, and no `t*` changes across the 9 settings. Tracker parameters are **not** varied and
their absence is disclosed: the causal readout does not use the lineage tracker.

**Decision (frozen).** A unit is **observer-robust** iff it is classified AUDITED in **all 9** settings.
Not-robust units are recorded as observer-fragile with the failing settings named. This resolves the
UNRESOLVED status either way; it does not by itself promote anything.

## PART B — causal-boundary displacement sweep (nested supports)

**Hypothesis.** A Gray-Scott entity may not be the detected V mask. It may include its **U-depletion field** and its
**reaction-diffusion halo**. Displacing only the V mask may therefore amputate the entity and leave the causally
relevant part behind — which would make "destroyed" (75/90 in RD-02) a boundary error, not a substrate result.

**Supports (mechanistic; no tuning).** From each law's OWN parameters, the diffusion length is
`ell = sqrt(Du / F)` cells (dx = dt = 1). The V mask is dilated by a Euclidean disk of radius:

| support | radius (cells) |
|---|---|
| S0 detected mask only | 0 |
| S1 mask + small halo | 2 |
| S2 ≈ one diffusion length | ceil(ell) |
| S3 ≈ two diffusion lengths | ceil(2·ell) |

Supports are strictly nested (S0 ⊆ S1/S2 ⊆ S3). Radii per frozen law: ell ∈ [1.56, 3.78] → S2 ∈ {2,3,4},
S3 ∈ {4,5,8}. These follow from (Du, F) alone and are fixed before any result is seen.

**Displacement.** Inside the selected support, **U, V and ALL passive temporal cohorts (CU, CV) are translated
together** by DELTA = (20, 20), conservatively swapped with the destination site. Zero displacement is an exact
no-op (SHAM ≡ CONTROL, checked bit-for-bit).

**Branches.** CONTROL / SHAM / PERTURBED / PLACEBO from the identical pre-intervention state. PLACEBO displaces a
matched non-candidate support of the **same cell count** by the same DELTA.

**Laws & seeds (frozen).** All nine screening-permitted laws {1,5,7,10,11,13,14,16,19}; **unseen** causal seeds
13001–13004 (4 per law). Denominator: 9 × 4 = **36 units per support**, 144 unit-supports total. `n_post` is the
actual post-intervention snapshot count (15 at cadence 50, HORIZON = 750), stated explicitly.

**Readout (unchanged from RD-02).** AUDITED requires, jointly: SHAM ≡ CONTROL; re-establishment at the new site
(frac_new_organized > 0.5); exceeds PLACEBO by > 0.25; **no old-site regeneration** (frac_old_organized ≤ 0.5, the
look-alike/occupancy alias check); and **continued temporal-cohort turnover** after recovery (min M < 0.5 at lags
{1,3,6}) — a frozen lump is a failure, not a success. Wilson 95% intervals on every rate.

**Decision rule (frozen, written before results):**
- A **compact** support (S0 or S1) repeatedly re-establishes with continued turnover **and** survives Part-A
  observer-only sensitivity → **retain as candidate** for individuality.
- Re-establishment requires a **broad** support (S2/S3, i.e. the environmental niche must be carried along) →
  classify **niche/site-carried** and **REJECT**: that is a transported environment, not a transported individual.
- **No** support succeeds → **retire classical Gray-Scott** and propose a **motile open-system substrate**.

A monotone increase of success with support size is itself evidence for niche/site-carriage and against
individuality; it will be reported as such.
