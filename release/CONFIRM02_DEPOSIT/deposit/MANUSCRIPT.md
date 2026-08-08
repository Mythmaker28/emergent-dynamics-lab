# Local interventional causal individuation in non-merging droplets

**A frozen prospective computational study (LCI-CAUSAL-NONMERGING-CONFIRM-02)**

Status: **DEPOSIT DRAFT — NOT SUBMITTED.** No preprint server, no journal, no DOI, no
repository record has been created for this work. Author, affiliation and licence fields are
**unresolved blockers** (Section 11).

---

## Abstract

We report a frozen, prospectively pre-registered *in silico* experiment in a reaction-transport
droplet model (a **computational model**; no physical, chemical or biological system was studied).
Three droplets are held **genuinely distinct throughout the trial** — no fusion, no percolation, no
shared connected component — and we ask whether erasing the internal memory field of one droplet
causally and specifically changes **that droplet's own** nutrient uptake. Across a sealed seed
family (53001–53032, run once), 23 of 32 seeds were geometrically eligible and 23/23 eligible worlds
passed the frozen geometric validity gate with **zero fusion events** (worst-world grid coverage
1.20 %–5.64 %, cap 15 %). The paired own-erasure contrast is **+0.2236** integrated-uptake units
(world-bootstrap 95 % CI [0.1926, 0.2583]); **23/23 worlds** and **69/69 droplet-targets** are
positive; the sham contrast (erasing a distant empty patch) is ≈ 0 (−6.8×10⁻⁹) and the neighbour
contrast is ≈ 0 (−7.3×10⁻⁶); the effect collapses to exactly 0.000 when the memory→uptake channel is
ablated (a manipulation check, not independent evidence); and a tracker-free fixed-mask control
converges at **+0.2068** (ratio tracked/fixed **1.08×**).

**Disclosed here, in the abstract, not only in the limitations:** the behavioural readout is **not a
distal or emergent behaviour**. Uptake is **directly coupled to the memory field m₊ by construction**,
through the sealed engine term `g ∝ N·ρ·(1 + λ₊·m₊)` (exactly: `g = dt·g0·ρ·N·qq·(1+β·σ)·(1+λ₊·m₊)`
with λ₊ = 0.25). What the paired intact−erase contrast establishes is therefore an **interventional,
local** causal relation on a **coupled** readout — not that the droplet does anything at a distance,
and not that dose can be read off behaviour (graded decoding is **INDETERMINATE**, world-level
corr(dose, own) = +0.174).

**Statistical unit and nesting, stated explicitly:** the 69 droplet-targets are **nested within 23
eligible worlds** (3 targets per world). They are **NOT 69 independent replications**. All gated
inference is at the **world** level (n = 23, world bootstrap); the 69/69 figure is descriptive
consistency, not 69 degrees of freedom.

**Maximal claim made by this work, verbatim:**

> **Local interventional causal individuation in non-merging droplets.**

We do **not** claim distal behaviour, graded metrology, global identity, a bounded entity
established, or Turing behaviour. Generalisation beyond this fixed software platform is not
established.

---

## 1. Background and what this study corrects

A prior confirmation in the same lineage (LCI-CAUSAL-CONFIRMATION-01) reported a much larger own
effect (+2.03, "39/39 droplets"). A subsequent audit
(`docs/individuation/CLAIM_IMPACT_TABLE.md`, `MERGE_INCIDENT_INDEPENDENT_VIEW.md`, commit `6470513`)
found that in 11/13 of those worlds the targets **fused into a percolating giant component**
(36–52 % of the grid) and the tracker was **non-bijective**, so several tracks locked onto the *same*
blob. That inflated the tracked readout by a factor **4.80×** relative to a tracker-free fixed mask
and contaminated locality. The "39/39 distinct droplets" claim was **INVALIDATED as 39 distinct
entities**.

The present study is the corrected, non-fusing re-run. Its purpose is to test whether the causal
effect is an artefact of fusion (Case E) or survives when the three droplets are provably distinct at
every step.

## 2. Model and the coupling that must be disclosed

The substrate is a chaotic reaction-transport PDE on a **64 × 64** grid (4096 cells) with an
engineered internal memory field. The sealed engine
(`edlab/experiments/sc_mcm/engine.py`, blob `2a2aaf47`, commit `65582d0`) computes per-cell uptake as

```
g = dt · g0 · ρ · N · qq · (1 + β·σ) · (1 + λ₊ · m₊)
```

with `λ₊ = 0.25`, `λ₋ = 0.15`, `m₊ = tanh(m[0] + m[1])`. The frozen protocol states the same
proportionality in shorthand: **`uptake ∝ N·ρ·(1 + λ₊·m₊)`**
(`NONMERGING_CONFIRM_PRESEAL_02.json`, key `behavioural.coupling_note`, commit `9b7580bc`).

**Consequence, acknowledged up front.** A memory field that is multiplicatively wired into the uptake
rate will change uptake when erased. The experiment is therefore *not* a test of whether memory has
*any* effect on the readout; that is true by construction. What the design tests, and what the paired
contrast isolates, is whether the effect is **own-specific, local, entity-resolved, and robust to
tracker choice on droplets that never merge** — i.e. whether the three droplets behave as three
causally individuated loci rather than one smeared medium. The manipulation check (λ → 0) collapsing
to exactly 0.000 is the *expected* behaviour of a correctly wired channel; it is reported as a
sanity check on the intervention machinery, **not** as independent evidence for the claim.

## 3. Frozen prospective design (PRESEAL `9b7580bc`, off `6470513`)

Everything in this section was frozen **before any 53xxx datum existed**.

| Item | Frozen value | PRESEAL key |
|---|---|---|
| Probe | uniform, amplitude 0.25 added to N per step, 5 steps | `probe.amp_per_step`, `probe.n_steps` |
| Cumulative injection | 1.25 × N0 | `probe.cumulative_injection_x_N0` |
| Probe selection criterion | **DEV geometry only**; effect size never consulted | `probe.selection` |
| N standardisation | reset N := N0, then 40 settle steps (explicitly **not** a washout) | `standardisation` |
| Behavioural horizon | 40 steps; readout = uptake integrated over t = 1..40 | `frozen_constants.HORIZON` |
| Primary readout | integrated uptake on the **bijectively tracked** component | `behavioural.primary_readout` |
| Convergent control | integrated uptake on the **fixed initial mask** (tracker-free, G5) | `behavioural.convergent_readout` |
| Targets per world | K = 3 | `frozen_constants.K` |
| Fusion cap | max grid coverage < 15 % | `frozen_constants.COVER_CAP` |
| Feasibility floor | ≥ 12 valid worlds AND ≥ 0.85 non-fusing fraction of eligible | `feasibility_thresholds` |
| Gate thresholds | DD_MIN 10.0, OFF_MAX 0.05, ABL_RATIO_MAX 0.15 | `gate_thresholds` |
| Coupling constants | λ₊ = 0.25, λ₋ = 0.15 | `frozen_constants.LAM_PLUS/LAM_MINUS` |
| Seed family | 53001–53032, cap 32, no extension after outcomes | `seeds` |
| Bootstrap / null seed | 20260715 | `determinism_seed` |
| Platform | Python 3.11.15, NumPy 2.2.6, SciPy 1.15.3, Matplotlib 3.10.9 | `environment` |

**World-level censorship (pre-declared).** If any of the 3 targets is censored
(MERGE / SPLIT / LOST / AMBIGUOUS), or fewer than 3 distinct components exist at any step, or
coverage reaches the 15 % cap, in **any** contrast branch {intact, erase×3, sham}, the **whole world**
is G0-INVALID. Survivors are never kept alone. Every seed appears in the raw record.

**Power.** Frozen pre-data DEV sizing gives own = +0.218 ± 0.063 at H = 40, need_n = 0.7 worlds
(`power.own_H40`). The 12-world floor is ≈ 17× the power requirement; the family was sized for
credibility across distinct worlds, not for statistical power.

**Seal integrity.** The PRESEAL carries a SHA-256 manifest of 8 sealed files
(`sealed_file_sha256`). All 8 were re-hashed in this deposit pass and **all 8 match exactly** — no
post-seal code drift (see `PROVENANCE_LEDGER.md`, rows SEAL-01..SEAL-08).

## 4. Results (RESULTS `830c2d0`, family run once)

### 4.1 Feasibility and geometry (G0)

- 32 seeds run; **23 eligible** (71.9 %), 9 ineligible (`fewer_than_K_eligible`) — eligibility is
  purely geometric and outcome-independent.
- **23/23** eligible worlds G0-VALID; non-fusing fraction **1.0**.
- **Zero** fusion events. Worst-world maximum grid coverage across the 23 worlds:
  **1.20 % – 5.64 %**, far below the 15 % cap.
- Bijective tracker: no MERGE / SPLIT / LOST / AMBIGUOUS; no shared components; unit tests 10/10.

### 4.2 Storage and rest-state readout (G1, G2)

- Memory influence matrix: **DD_mem = 2590.0** (threshold ≥ 10), mean |off-diagonal| = **7.03×10⁻⁵**
  (threshold < 0.05), diagonal 0.1869. **PASS.**
- Dose decoding from the 11-D memory feature vector: **R² = 0.691**, bootstrap CI [0.581, 0.824],
  within-null 95th percentile 0.153, empirical p = 2.0×10⁻⁴. Neighbour dose R² = **−0.014**.
  Order (secondary, pre-declared): R² = 0.376, null95 0.106. **PASS.**

### 4.3 Behavioural causal effect (G3, G4, G5)

Unit of inference = **world** (n = 23). CIs are world-bootstrap percentiles (5000 resamples,
seed 20260715).

| Contrast | Mean | World-bootstrap 95 % CI | Worlds > 0 |
|---|---|---|---|
| **own** (intact − erase-own) | **+0.2236** | [0.1926, 0.2583] | **23/23** |
| own − sham | (≡ own) | lower bound **+0.1926** | — |
| own − neighbour | (≡ own) | lower bound **+0.1926** | — |
| sham (intact − sham) | −6.8×10⁻⁹ | — | — |
| neighbour (intact − erase-neighbour) | −7.3×10⁻⁶ | — | — |
| ablation (λ→0 manipulation check) | **0.000** | ratio 0.000 | — |
| **fixed mask** (tracker-free, G5) | **+0.2068** | [0.1799, 0.2344] | 23/23 same sign |

Tracked/fixed ratio = **1.08×** — compared with the **4.80×** inflation measured in the fused,
non-bijective regime of the earlier incident. The effect is therefore **not** a fusion artefact.

Descriptively, all **69** droplet-targets are positive (per-target range +0.030 to +0.902). Again:
these 69 targets are **nested in 23 worlds**, 3 per world; they are **not 69 independent
replications**, and no p-value or CI in this manuscript treats them as such.

**G6 (composite: G0 ∧ G1 ∧ G2 ∧ G3 ∧ G4, no fusion) = PASS.**

### 4.4 What did *not* pass, or was not tested

- **Graded decoding of dose from behaviour: INDETERMINATE** (secondary, non-gating). World-level
  corr(world dose, own effect) = **+0.174**. There is no metrology here.
- **Deep material turnover was not re-tested** in this mission (inherited status: dose
  INDETERMINATE, order NEGATIVE).
- **Transplant was removed** from the design at PRESEAL time and was never run.
- **Active reconstruction** was forbidden for this mission and was not launched.

## 5. Post hoc sensitivity: R* = 0.2575 (ADDENDUM `9c8a62c`)

**This section is post hoc additional sensitivity work. It is NOT part of the frozen prospective
design, it did not exist at PRESEAL time, and no result in Section 4 depends on it.** It uses DEV
worlds only (50001–50009, 8 worlds), never prospective 53xxx seeds, and consults **geometry only** —
the causal effect size was never examined.

| Probe | Cumulative injection | No fusion | Worst coverage @H40 | G0-valid @H40 |
|---|---|---|---|---|
| 0.25×5 (**sealed**) | 1.2500 | 8/8 | **3.3203 %** | 8/8 |
| 0.2575×5 (R*) | 1.2875 | 8/8 | **3.3447 %** | 8/8 |

Difference in worst-world coverage: **+0.0244 percentage points** — inside the noise. Both pass.
Against a six-criterion anti-numerology test, R* = 0.2575 fails four criteria decisively (no
pre-declared correspondence; no mechanism forcing the value; does not beat neighbouring values; does
not recur as an emergent observable) and the first two criteria (dimensionless, scale-invariant) do
not discriminate it from 0.24, 0.25 or 0.26. **Conclusion: R* has no independent theoretical
derivation; the sealed 0.25×5 probe is kept.** The positive reading is narrow and only that: a +3 %
perturbation of the probe amplitude leaves the geometry unchanged, so the Section 4 conclusion does
not hinge on fine-tuning the amplitude.

## 6. What is explicitly NOT claimed

1. **Not distal behaviour.** The readout is the coupled uptake term. Nothing here shows an effect on
   anything the droplet does away from the coupling.
2. **Not graded metrology.** Dose is not decodable from behaviour (INDETERMINATE).
3. **Not global identity, not a bounded entity established, not life, not agency, not Turing
   behaviour.** The claim is local and interventional.
4. **Not independent replication.** One seed family, run once, on one fixed software platform, by one
   pipeline. 69 targets nested in 23 worlds.
5. **Not cross-platform.** Determinism is byte-identical on the sealed platform only; the PDE is
   chaotic.
6. **Not a physical result.** This is a computational model throughout.

## 7. Reproduction and determinism

Frozen reproduction commands (`NONMERGING_CONFIRM_PRESEAL_02.json`, key `reproduction`):

```bash
python -m venv venv && venv/bin/pip install numpy==2.2.6 scipy==1.15.3 matplotlib==3.10.9
export PYTHONPATH=$PWD; mkdir -p work
venv/bin/python experiments/individuation/test_bijective_tracker.py
venv/bin/python experiments/individuation/nonmerging_confirm.py work/nm_confirm_raw.json $(seq 53001 53032)
venv/bin/python experiments/individuation/nonmerging_analyze.py work/nm_confirm_raw.json <certificate.json>
```

**Determinism.** Two independent full-pipeline DEV runs produced byte-identical raw JSON
(sha256 `a45a860e0a8418e72f7fe904001e971556ac420e34914a6f243a18523dac6edb`), identical tracker
statuses and identical G0 validity. This holds on the sealed platform and is **not** claimed
cross-platform.

**What was actually re-run for this deposit.** The **analysis stage only** was re-executed here,
from the committed raw record, using the committed analysis script — see `verification/` and
Section 8. The **simulation stage was not re-run** (32 seeds × 5 branch families of a chaotic
RD-PDE with an 800-step warm-up; far beyond the tooling budget of this pass).

## 8. Provenance, integrity, and one honest discrepancy

Every numeric claim above is traced in `PROVENANCE_LEDGER.md` to an exact file, an exact commit, a
SHA-256, and an exact JSON key or table cell. **VERIFIED in that ledger means "traced to an exact
repository artefact", not "independently reproduced."**

Re-running the committed analysis script on the committed raw record reproduced **all gated
statistics exactly** (own mean and CI, own−sham, own−neighbour, ablation, fixed-mask CI, same-sign
count, tracked/fixed ratio, DD_mem, off-diagonal, dose R², dose null95, dose p, and every per-seed
row). It did **not** reproduce the certificate byte-for-byte: **five non-gating floating-point
values differ in the last 1–3 units in the last place** (dose CI endpoints, neighbour dose R²,
order R², order null95) — a relative discrepancy of order 10⁻¹⁵, consistent with a different
BLAS/LAPACK backend on the machine used for this deposit pass. The differences are recorded verbatim
in `verification/certificate_diff.txt` and carried as status **DIFFERS** in the ledger. All values
quoted in this manuscript are quoted at a precision at which both computations agree.

## 9. AI-assistance disclosure

The simulation code, the analysis pipeline, the frozen protocol documents, the figures and the
drafting of this manuscript were produced with autonomous AI coding/analysis agents working under
human direction. The human corresponding author is responsible for all scientific content and for
the decision to release. AI assistance does not constitute authorship.

## 10. Data and code availability

All artefacts quoted here are included in this deposit under `sources/`, each with its SHA-256 in
`SHA256SUMS` and its originating commit in `PROVENANCE_LEDGER.md`. Nothing has been pushed, tagged,
merged or published; the work lives on the local branch
`exp/lci-causal-nonmerging-confirm-02` (`9b7580bc` → `830c2d0` → `9c8a62c`, off `6470513`).

## 11. Blockers — status at 2026-08-08

Settled by the corresponding author on 2026-08-08 (`AUTHOR_AUTHORISATION_02.md`):

1. **Copyright holder — RESOLVED.** `release/LICENSE-CODE` and `release/LICENSE-DATA-TEXT` now
   begin `Copyright 2026 Tommy Lepesteur`. At commit `4dfb73e` both carried the literal marker
   `[COPYRIGHT HOLDER — to be confirmed by the author before release]`; that marker is gone. The
   value comes from the author's declaration, not from any pre-existing repository artefact.
2. **Author name — RESOLVED.** `Tommy Lepesteur` in `release/AUTHORS.md` and, as
   `family-names: Lepesteur` / `given-names: Tommy`, in `release/CITATION.cff`.
3. **Licence — RESOLVED.** CC-BY-4.0 for data, figures and text; Apache-2.0 for code. Approved by
   the author; `DEPOSIT_METADATA.json` now carries a machine-actionable `license` field.

Still unresolved, and nothing invented:

4. **Affiliation and ORCID are undeclared.** The author gave a name only.
5. **No DOI, no funder, no related identifier** exists or has been minted.
6. **Nothing has been submitted.** Approving a licence is not authorisation to deposit. No Zenodo
   record has been created, reserved or published, and the author has not authorised one.

*Nothing in this deposit has been submitted anywhere.*
