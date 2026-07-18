# LCI-CAUSAL-TURNOVER-PREREG-03 — Phase 0: Independent view

*New independent agent. Mission: audit, metrology, and pre-registration of a turnover-survival test for
local causal individuation. My brief is to **criticize** the inherited result and protocol first, and I am
explicitly allowed to conclude that the next experiment is premature or ill-posed. I am **not** to justify
ACTIVE-RECONSTRUCTION. Branch `design/lci-causal-turnover-prereg-03` off `9c8a62c`. No prospective family is
opened by this mission; it stops before the first confirmatory seed and asks Tommy for authorization.*

Source verified: branch tip `exp/lci-causal-nonmerging-confirm-02` = `9c8a62c`; lineage `6470513` (merge audit) →
`9b7580bc` (PRESEAL) → `830c2d0` (RESULTS) → `9c8a62c` (R* addendum) all present; `main f3921a4`, `V4 23b53ae`,
`release` intact. Reproduction gate (Phase 1) run before writing this: the sealed certificate regenerates from the
committed raw with **0 differences at 1e-12**, and seeds 53001–53003 re-run **byte-identical** — so the rest result
is real and reproducible, and I am entitled (by the mission's own gate) to reason about the turnover.

---

## 0. One-paragraph independent position (preliminary; pilots pending)

The rest result `830c2d0` is genuine but **narrow**: it establishes *interventional-local* causal individuation on
a readout that is **coupled to memory by construction** (`uptake ∝ 1+λ₊·tanh(m₊)`), not distal/emergent behaviour,
and the graded decode is indeterminate. The turnover question, as posed, sits on top of an architecture whose memory
is an **intensive, mass-borne, passively-copied** field: new material inherits it (`Mf += g·m`), homogeneous death
preserves its concentration, and it is continuously re-templated and forgotten. Because of this, a naive "does the
causal effect survive turnover" test is at **high risk of being near-tautological** (the coupling multiplier is
always present; it only needs a nonzero own-remnant), while the project's **own prior result already found that
graded own-history is NOT maintained through deep turnover** on this architecture. The scientifically load-bearing
questions are therefore not "is there a positive effect" but **(i) feasibility** — can three droplets truly reach
per-droplet `M_i ≤ 0.25` while staying distinct/alive/non-fusing, measured by *real cohorts* not an analytic scalar
— and **(ii) own-specific, global-separable survival** — does whatever survives remain distinguishable from the
neighbour and from the global `up_ref` channel. My preliminary lean is **REPAIR**: the test is worth pre-registering
but only if it is built to discriminate passive-copy decay from genuine persistence and to kill the global channel,
and only after DEV pilots show feasibility is real. I will revise this to GO / REPAIR / NO-GO after the pilots.

---

## 1. The twelve questions

### Q1 — Does `830c2d0` really establish causal individuation *at rest*?

**Partly, and only in a narrow sense.** What is established and reproducible (I re-verified byte-identically): on a
0-fusion protocol where 3 droplets stay distinct all assay (23/23 valid, max coverage ≤5.6 %), a do-erase of a
droplet's own memory reduces *its own* integrated feeding (own +0.223, world-CI [0.193, 0.258], 23/23 & 69/69 > 0),
neighbour and sham ≈ 0, ablation exactly 0.000, and a tracker-free fixed mask converges (+0.207, ratio 1.08×).
Storage/readout at rest replicate (DD 2590; own-dose R² 0.691 ≫ neighbour −0.014).

Three caveats keep this narrow, two of them already stated honestly by the confirm-02 agent: **(a)** the readout
`uptake_eff = uptake·(1+λ₊·tanh(m₊))` (`sc_mcm/engine.py:79`) is **coupled to m₊ by construction** — the effect is
an algebraic multiplier, so "causal" here means *interventional-local*, not distal or emergent; **(b)** the **graded
metrologic decode is INDETERMINATE** (corr(dose, own) ≈ 0.17) — the individuation is interventional, not
metrological; **(c)** it is a **rest** result — zero material turnover (the assay is 40 settle + 40 horizon ≈ 10 %
turnover). So: causal individuation is established *interventionally and locally on persistent non-fusing entities*,
and nothing stronger. It is not identity, agency, or distal behaviour.

### Q2 — What is *directly coupled by construction*?

Enumerated from the frozen engine (`sc_mcm/engine.py`, `sc_iom/engine.py`), all pre-existing, none added here:

| coupling | code | consequence |
|---|---|---|
| own memory → own feeding | `g ∝ ρ·N·(1+λ₊·tanh(m₊))` (l.79) | erase m₊ ⇒ factor→1 ⇒ own uptake drops **mechanically** |
| new material inherits memory | `Mf += g·m` (l.83) | **passive copy / templating** of history onto fed mass |
| homogeneous death preserves concentration | `ρ,Mf *= (1−k·dt)` (l.87) | intensive `m = Mf/ρ` is invariant under pure death |
| memory rides the scaffold | advection `dM` by flux `fl` (l.68–69) | memory transported with material |
| write signal references a **global scalar** | `Ψ = tanh(k_exp(N−c)+k_up(uptake−up_ref))` (l.103–104) | every cell's writing is centred on world-mean uptake |
| memory → attractant | `c += … s·ρ·(1+λ₋·tanh(m₋))` (l.116) | second coupled channel (order → attractant) |

**Implication that governs the whole design:** at deep turnover, a positive *interventional* own-effect is expected
**almost by construction** as long as *any* own-specific m₊ remnant survives, because the multiplier is always there.
The non-trivial science is therefore whether an own-specific remnant **survives and stays separable**, not whether
the multiplier fires.

### Q3 — What does "survive the turnover" mean *exactly*?

It must be decomposed into three independent levels and never conflated:

1. **Physical/material** — the droplet remains a single distinct, alive, non-fusing component while its constituent
   mass is replaced: quantified per-droplet by `M_i(t)` = fraction of the *rest-snapshot* material still in droplet
   `i`. "Deep" ≡ `M_i ≤ 0.25` (≥75 % replaced) **for each of the three** entities, measured by real cohorts.
2. **Storage** — the droplet's *own* local history is still stored / decodable from its renewed material.
3. **Causal + distinction** — the droplet's causal capacity over its own feeding persists **and** stays own-specific
   (own > neighbour, own > sham) **and** is not explained by the global channel.

"Survive" is **not** "`M_i ≤ 0.25` was reached" alone (that is only the precondition), nor "a positive own effect
exists" alone (Q4). All three levels, in ladder order (règle finale), or the claim is unearned.

### Q4 — Is a positive causal effect after turnover *sufficient*?

**No.** Because the readout is coupled by construction (Q2), `own_deep > 0` is a low bar met by any surviving remnant.
It is necessary but insufficient without, jointly: **(a)** own-specificity preserved at depth (`own−neighbour > 0`
*and* `own−sham > 0`, not merely `own > 0`); **(b)** global-channel separability (the effect is not reproducible from
`up_ref` / common environment); **(c)** evidence the surviving signal is the *original own history*, not a passively
copied common template or a trivial geometric confound. A bare `own_deep > 0` would be, on this engine, close to
guaranteed and close to meaningless.

### Q5 — Should we *also* decode the own local history after turnover?

**Yes — and it is the more informative rung.** Storage decode (does graded own dose/order survive?) is strictly
harder than the interventional multiplier and is exactly where the architecture has already failed once: the prior
`EXP1_RESULTS_AND_DECISION` found deep own-dose decode **R²=0.37 [0.14, 0.72] (indeterminate)** and own-order
**collapses (−0.66)**. Per the règle finale, storage survival must be *measured and reported*, and its failure
*qualifies* any causal-survival claim. I will report it as its own gate (G3-deep) and not let a passing interventional
G4 paper over a failing G3.

### Q6 — How to distinguish persistent memory, passive copy, and reconstruction?

This is the deepest question, and on this engine the answer is uncomfortable: **the mechanism is, by construction,
passive copy.** New material inherits `m` (`Mf += g·m`) and death preserves concentration; there is **no
error-correcting or self-rebuilding term**. So:

- **Passive copy** (what this engine does): the deep `m` is a decayed + templated + diffused *copy* of the rest `m`,
  fully predicted by the forgetting/templating/inheritance kernel. Signature: monotone decay of own-specificity toward
  the forgetting floor; the deep signal is reproduced by propagating the rest `m` through turnover with **no new
  droplet-specific writing**.
- **Persistent (material-independent) memory**: information held in a store *not* carried by the turning-over mass
  (e.g. internal bistable `(u,v)`, attractant `c` geometry, or position) that would survive even if mass-borne `m`
  were zeroed. This is *also the confound to kill* (Q12 E4): if "survival" is really a stable size/position
  difference, it is not memory.
- **Reconstruction**: the deep own-specific signal is *stronger or better-corrected* than the passive-decay
  prediction — something actively rebuilds it. **Not expected on C1c** and, if seen, would itself be the surprising
  result that motivates (not confirms) an active architecture.

**Discriminator to pre-register:** a **passive-decay null** — propagate the rest snapshot through the identical
turnover with memory writing frozen / no re-write, and require the observed deep own signal to *match* the passive
prediction. A match ⇒ "passive copy," which is honestly *not* "persistent memory" and *not* reconstruction.

### Q7 — Where does the information reside during turnover?

In the **mass-intensive concentration `m = Mf/ρ`**, continuously copied from old to new mass by the inheritance term,
scaled (but concentration-preserved) by death, decayed by forgetting `η_d`, and homogenized by templating `η_t` and
diffusion `D_m`. It does **not** reside in any material-independent store. So "the information survives turnover" is
mechanistically "the intensive field's copy-and-decay leaves a remnant" — which is precisely why the passive-decay
null (Q6) and the global-channel audit (Q8) are load-bearing rather than optional.

### Q8 — Can the global `up_ref` channel resynchronize the droplets?

**Real risk, and undertested.** `up_ref` = global mean uptake over alive cells enters *every* cell's write signal
(`sc_mcm:103`). Prior work characterized it **only at rest** (a 120-step drive), where far |Δm| ≈ 8e-6 — negligible.
But turnover is **600+ steps of continuous rewriting with no reinforcing drive**; over that horizon even a weak
common-mode term can accumulate and either (a) pull all droplets' `m` toward a common value (own-specificity lost —
would read as "homogenized"), or (b) if `up_ref` happens to co-vary with a droplet's own state, spuriously *sustain*
a shared signal that mimics retained individuation. The rest conclusion **does not transfer** to the turnover regime
and must be re-measured *in* it. This is the `GLOBAL_CHANNEL_AUDIT`.

### Q9 — How to measure matter, phenotype, and causality *separately*?

No composite score (mission mandate, and a composite would hide independent failure modes):

- **`M_i` (matter)** — a **per-target passive cohort** seeded at the rest snapshot (cohorts *never* enter any rate —
  strictly observational; verified in the engine), read within the bijectively-tracked region. Replaces the inherited
  **analytic** `(1−k·dt)^T` scalar, which is identical for all droplets and measures nothing per-entity.
- **`P_i` (phenotype)** — size, mass, radius of gyration, shape/localisation (janus, radial_u, interface), basal
  uptake, attractant `c`, viability — each reported **separately** from `detect()` + fields.
- **`F_i` (causal fingerprint)** — the confirm-02 battery reported as **separate components**: intact − erase-target,
  intact − erase-neighbour, intact − sham, ablation, tracked-bijective, fixed-mask, and the uptake/growth/attractant
  sub-effects. **Not** reduced to a single scalar.
- **`G` (global coupling)** — `up_ref`, world-mean, inter-droplet correlation, own→neighbour contamination, and the
  predictability of own from the global world state.

### Q10 — What result would justify ACTIVE-RECONSTRUCTION?

The honest logic is **inverted** relative to any pressure to "confirm" it. ACTIVE-RECONSTRUCTION is motivated by a
turnover **failure** of the passive architecture: it proposes to *remove the passive copy and add active
self-maintenance*. So it is justified only by a clean demonstration that **G0 feasibility holds** (3 distinct/alive/
non-fusing at `M_i ≤ 0.25`) **AND own-history storage degrades/fails at deep turnover** — i.e. the passive copy does
*not* maintain graded own-specific information (which is what the prior EXP1 negative already suggests). A turnover
**success** on the passive engine would **remove** the motivation (Q11). Either way this mission launches nothing; it
only pre-registers the discriminating test. I will not tune the design to reach a pre-decided ACTIVE-RECONSTRUCTION.

### Q11 — What result would instead show C1c already suffices?

If, on the corrected non-fusing protocol with real per-droplet `M_i ≤ 0.25`, the deep own causal effect **survives**,
stays **own-specific** (own−neighbour > 0, own−sham > 0), is **separable from the global channel**, and (ideally)
graded own storage survives — then passive-copy C1c **does** maintain causal individuation through deep turnover and
ACTIVE-RECONSTRUCTION is unnecessary. This is a live possibility precisely because the interventional bar is easier
than the graded-decode bar on which EXP1 failed; it could pass where EXP1 did not.

### Q12 — Which alternative explanations must be killed *prospectively*?

| # | alternative | prospective kill |
|---|---|---|
| E1 | fusion/percolation artefact | G0 non-fusing censorship at write, turnover, and both assays; coverage cap |
| E2 | tracker cross-attribution (the ×4.8 merge-incident inflation) | bijective tracker + fixed-mask convergent control at depth |
| E3 | global `up_ref` / common-environment resynchronization | global-channel audit + up_ref-neutralized diagnostic + global-mean-history decoder |
| E4 | trivial size/mass/position confound (not memory) | ablation collapse (λ→0) + baseline decoders that must FAIL where memory succeeds |
| E5 | passive-copy-only (no real persistence) | passive-decay null (memory-frozen propagation) must match the observed deep signal |
| E6 | insufficient / mis-measured turnover | per-droplet cohort `M_i ≤ 0.25` gate per entity (not the analytic scalar) |
| E7 | survivor-selection bias (39/39 → 17 lesson) | world-level censorship (any invalid entity ⇒ whole world invalid), pre-declared feasibility floor, all seeds reported |

---

## 2. What I inherit vs. what I must not reuse

**Reuse (verified sound):** the frozen `MultiChannelMemoryEngine` / C1c (no physics change permitted); the storage
block of `causal_confirm.py` (G1/G2); the **bijective tracker** (`bijective_tracker.py`, censors MERGE/SPLIT/LOST/
AMBIGUOUS); the frozen probe **uniform 0.25×5**; world-level G0 censorship; the paired-contrast logic that makes the
coupled readout interventional.

**Do NOT reuse blindly (audit findings, detailed in `TURNOVER_ENGINE_AUDIT.md`):**

- `exp1_maintenance.py` — the inherited turnover runner **estimates `M` analytically** as `(1−k·dt)^TURN ≈ 0.21`
  (one global scalar for all 3 droplets; measures no real per-droplet material), uses the **old non-bijective overlap
  tracker** (cadence 5, θ=0.1, no censorship — the exact bug that inflated the merge incident ×4.8), runs **no causal
  assay at depth**, and has **no global-channel control**. Its M threshold was `M_LOW=0.35`, not 0.25.
- `sc_iom/config.py` legacy constants: `PROBE=("N",add,0.50,15)` is the **fusing** probe that caused the merge
  incident — must stay replaced by 0.25×5. `G_TURNOVER_KEEP=0.5` is an **arbitrary** retention threshold — the
  mission explicitly forbids re-inventing 0.50; any retention gate must be justified from the question and power.
- The **particle-substrate** observables `observables/continuity.py` (Jaccard `material_retention` over particle IDs),
  `entities/tracking.py`, `observables/phenotype.py` are a **different lineage** (discrete particles, not the scaffold
  field). Using them here would be a category error. The scaffold material tracer must be built from the cohort field
  `C`.

---

## 3. My plan (before implementing anything prospective)

Ladder-ordered; each rung is only interpreted if the previous one holds (règle finale). **DEV seeds 50001–50010
only**; 51xxx/52xxx/53xxx are read-only for diagnosis; no new confirmatory seed is run.

1. **Audit** (this doc + `TURNOVER_ENGINE_AUDIT.md`, `MATERIAL_TRACER_SPEC.md`, `GLOBAL_CHANNEL_AUDIT.md`).
2. **Material tracer** — per-target passive cohorts appended to `C` (never enter physics), seeded at the rest
   snapshot; `M_i(t)` = tracer-cohort mass in the bijective region / total mass in region. Validate: (a) determinism,
   (b) `Σ` conservation, (c) zero-feedback (fields byte-identical with vs without tracer cohorts).
3. **DEV runner** `turnover_dev_runner.py` (resumable, checkpoint per seed): write local histories (confirm-02
   storage) → **rest snapshot** → rest causal assay on *branches* (0.25×5) → **turnover** on the unperturbed world
   with `M_i`, `P_i`, `G` recorded and explicit censorship → **deep snapshot** at the first pre-declared step where all
   three satisfy `M_i ≤ 0.25` & alive & distinct & non-fusing & under coverage cap → deep causal assay on branches
   (same probe/horizon/gates).
4. **DEV pilots** on 50001–50010: determinism (byte-identical two-run); time-to-`M_i≤0.25`; fusion/loss/split rates;
   feasibility of ≥12 valid worlds in a future family; deep storage decode; deep causal battery; passive-decay null;
   global-channel separability (own vs neighbour vs global-mean-history; up_ref-neutralized diagnostic). Tracker /
   periodicity / no-feedback tests.
5. **Power** — dimension separately: feasibility, deep storage, deep causal own, own−sham, own−neighbour, ratio
   (secondary). World-level bootstrap. Propose a **fresh** seed family and verify its absence from the whole registry.
   **Do not open it.**
6. **PRESEAL candidate** — full frozen protocol/gates/nulls/power/seeds/env/hashes/commands, labelled
   `PRESEAL_CANDIDATE — NOT AUTHORIZED FOR PROSPECTIVE RUN`. Commit to the design branch (not named a final PRESEAL).
7. **STOP** — present GO / REPAIR / NO-GO, risks, and request Tommy's authorization. Launch nothing.

## 4. Gate philosophy I will freeze

- **G0 feasibility is the first real rung** and can by itself yield NO-GO: if 3 droplets cannot reach `M_i≤0.25` while
  staying distinct/alive/non-fusing in ≥ a pre-declared number of worlds, the question is not yet answerable and no
  amount of downstream statistics matters.
- **G3 (deep storage) and G4 (deep causal) are separate**; a coupled-readout G4 pass does not substitute for a G3
  storage pass. Report both; qualify claims by the weaker.
- **G5 retention** has two tiers: *causal survival* (deep own lower-CI > 0) and *strong retention* (deep/rest ratio
  lower bound above a **justified** threshold). I will **not** default the threshold to 0.50; if no mechanistic
  justification exists it stays secondary and descriptive.
- **G6 individuation-through-turnover** passes only if G0 ∧ G1 ∧ G2 ∧ G3 ∧ G4 **and** own stays distinct from
  neighbour/sham **and** the global channel cannot explain the effect.

## 5. Preliminary verdict (to be finalized after pilots)

**REPAIR-leaning.** The test is worth pre-registering, but only rebuilt around: real per-droplet `M_i`, the bijective
tracker, a passive-decay null, and an in-regime global-channel audit — and only if DEV pilots show G0 feasibility is
genuinely reachable at `M_i≤0.25` for three non-fusing entities. If pilots show feasibility is not reachable without
fusion/loss, the honest call is **NO-GO / premature**. If feasibility is clean and the design discriminates
passive-copy from persistence, it becomes **GO** for a fresh, human-authorized family. I will not pre-commit to a
result, and I will not shade the design toward ACTIVE-RECONSTRUCTION.
