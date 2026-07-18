# INDEPENDENT_JUDGMENT_01 — LOCAL-CAUSAL-INDIVIDUATION-00

**Author:** new independent audit agent (not the author of 6806f1f). **Branch:** `exp/local-causal-individuation-00` @ 6806f1f. **Scope:** audit of Phase 0 (3def3df) + prospective Exp-1 (51001–51012). **Constraint:** `main` (f3921a4), V4 (23b53ae) and release untouched; nothing pushed/tagged. h2-on-C1c stays closed.

This document is my own scientific judgment. It agrees with the previous agent where the evidence holds, and contradicts it where the claims exceed the evidence. All numbers were **recomputed from the committed raw data** (`exp1_prospective_raw.json`, `exp1_maintenance_raw.json`) with an independently written analysis (`exp1_reaudit.py`), cross-checked against the committed `exp1_analyze.py` and against a second decoder implementation (SVD ridge vs normal-equation ridge — identical to 3 decimals).

---

## Executive position (one paragraph)

At rest, **local memory *storage* and *own-history readout* individuation is real and holds up to hostile re-analysis** — it survives a within-world permutation null (p≈2×10⁻⁴), is stable under leave-one-world-out jackknife, beats neighbour and all trivial baselines, and the influence matrix is diagonal in **absolute** terms (not merely as a near-zero-denominator ratio). **But three inherited claims are overstated:** (1) the word *"causal"* is not earned — the certified "own R²>0.5" is a **memory-feature readout**, not the **behavioural** decode that the preregistration defines as K2; (2) the K2 pass was obtained by a **post-hoc coordinate switch** (the committed code tests `dose` → prints `CHECK`; the report re-narrates via `order` → `PASS`); (3) the deep-turnover headline *"NOT maintained"* is wrong in both directions — dose maintenance is **significantly above the null** (p≈10⁻³) yet **not certified ≥0.50**, i.e. INDETERMINATE, and only the **order** coordinate genuinely collapses. Consequently I do **not** endorse the inherited recommendation to proceed directly to ACTIVE-RECONSTRUCTION-00. The correct next move is **REPLICATE/REPAIR** (sealed confirmation 52xxx + a genuine behavioural K2 decode + the pending controls), executed under a **repaired, unambiguous gate frozen before any 52xxx data is seen**.

---

## Answers to the ten mandated questions

**1. What is actually established?**
Established (rest): (a) **storage individuation** — a strictly-local nutrient drive writes a droplet-local memory footprint; the single-perturbation influence matrix C_ij is diagonal with median |diag|≈**0.180** vs median |off|≈**1.8×10⁻⁵** (DD≈9018), and the diagonal write is ≈**11×** the baseline memory magnitude, so this is a real absolute effect, robust to a denominator ε up to 10⁻⁶; (b) **own-history readout specificity** — a droplet's own local history is decodable from its own memory features (order R²=**0.654**, dose R²=**0.450**) far above neighbour (−0.31) and above the within-world permutation null (p=2×10⁻⁴ and 7×10⁻³), stable under jackknife, and non-trivial (beats size −0.17, position −0.17, size+position −0.22). This is genuine per-droplet individuation of *stored memory* at rest.

**2. Which of the previous agent's statements are too strong?**
Three. (i) *"Local **causal** individuation is ESTABLISHED at rest."* — "causal/behavioural expression" (K2) was never decoded behaviourally; the evidence is a memory readout plus a Δuptake dominance *ratio*. (ii) *"K2 … PASS."* — the committed analysis prints **CHECK** for K2 (own dose=0.45, not >0.5); the PASS uses `order` chosen after seeing that `dose` failed. (iii) *"NOT maintained through deep material turnover."* — dose maintenance R²=0.368 **beats the within-world null** (p≈10⁻³, jackknife 0.27–0.43); its 95% CI is [0.14, 0.72]. The honest status is **INDETERMINATE**, and there is positive evidence **against total loss**. The body of `EXP1_RESULTS_AND_DECISION.md` is more careful ("NOT ESTABLISHED", "marginal", "own≫neigh"); it is the **headline and commit message** that overreach.

**3. Is there pseudo-replication between the three droplets of one world?**
Partially, but it is controlled where it matters. The decoder uses **grouped leave-one-world-out** cross-validation and the bootstrap/permutation nulls resample **whole worlds**, so the CIs and p-values are already at the world level (9 units), not the 27-row level. The residual issue is that the **point R²** is computed over 27 pooled rows and n_worlds=9 is small, so all CIs are wide. I verified the conclusions do **not** hinge on any single world (jackknife order 0.556–0.689). Verdict: **no fatal pseudo-replication; low power.** The mission's inherited worry ("27 treated as independent") is only true for the point estimate, not for the inference.

**4. Were the 27 observations treated as independent when the experimental unit is the seed/world?**
For inference (CV, bootstrap, nulls): **no** — grouping is by world. For the reported point estimates and the DD median: effectively yes (pooled). I re-report everything at world level with per-seed jackknife (§ STATISTICAL_REAUDIT). The effective n is **9 worlds**, and every claim is stated against that.

**5. Were the 3/12 exclusions planned and independent of results?**
**Yes.** The excluded seeds are 51001, 51006, 51008. The selection rule (`pick()`: size ≥ 45 **and** pairwise periodic centroid distance ≥ 24) is frozen in the sealed PREREGISTRATION (3def3df) and uses **only geometry** — it never touches the history amplitudes, the memory features, or any decode. All 9 retained worlds have min pairwise distance ≥ 24.6. Exclusion is outcome-independent and defensible. (Minor gap: the per-seed geometric reason for each exclusion is not logged in the raw beyond `ok:false`.)

**6. Was the 24-cell separation frozen before the prospective seeds?**
**Yes.** It is fixed in PREREGISTRATION.md and P0_TECHNICAL_AUDIT.md (both sealed at 3def3df, sha256 verified intact), derived from the DEV 50001–50003 contamination-vs-distance curve (<1% contamination by ≈24 cells). It predates any 51xxx seed.

**7. Is the diagonal dominance large because diagonal effects are large, or because the off-diagonal denominator is ≈0?**
**Both, but the diagonal is genuinely large.** Median diagonal |Δm|≈0.180 is ≈11× the baseline memory magnitude (≈0.016) — a substantial local write. The off-diagonal ≈1.8×10⁻⁵ is a diffusion halo. So DD≈9018 is *not* an artifact of a vanishing denominator: it survives inflating the denominator by ε up to 10⁻⁶ (DD still ≈8667) and only collapses at ε=10⁻³ (i.e. when you add noise larger than the off-diagonal itself). **K1 storage individuation is real in absolute terms.**

**8. Is the causal *behaviour* a substantial absolute effect, or a tiny numerical difference?**
This is the weak point. The behavioural footprint (Δuptake) has median diagonal ≈**2.7×10⁻⁴** vs off ≈1.9×10⁻⁷ (DD≈1629). The **ratio** is diagonal, but the **absolute** diagonal behavioural change is ~700× smaller than the memory-write effect, and I could not verify its substantiality against the uptake dynamic range from the committed raw (baseline uptake is not stored). More importantly, K2 as preregistered requires a **behavioural decode R²>0.50**, which was **never computed**. So the "causal expression" claim rests on a small-magnitude dominance ratio, not on a demonstrated behavioural effect. **Status: NOT ESTABLISHED as causal/behavioural.**

**9. Does the 0.23 permutation null indicate a small-sample, group-structure, or decoder problem?**
Resolved — and it **redeems** the null rather than condemning it. The reported "null 95th pct ≈ 0.23" is a **within-world** permutation (shuffle the 3 history labels *inside* each world), which is the *correct, stricter* null for individuation. I reproduce it (my within-world null-95 = 0.237 dose / 0.266 order). My **global** permutation null-95 is only ≈0.05. The 0.23 ceiling is simply the small-sample luck of a K=3-per-world / 9-world design — **not** leakage or a decoder pathology. The observed signals clear it (dose p=7×10⁻³, order p=2×10⁻⁴). My initial suspicion that 0.23 signalled leakage was **falsified** by computing both nulls — a differential-verification success.

**10. Is Experiment 2 (ACTIVE-RECONSTRUCTION) genuinely justified now?**
**Not yet.** Three reasons. (a) Its premise — "individuation is not maintained through turnover, so we need active reconstruction" — is **partly false**: dose maintenance is significantly non-zero (only sub-threshold); only *order* is lost. (b) The rest **causal** claim it builds on is not established (K2 behavioural decode never done). Building a new architecture to fix *turnover* before the *rest causal* effect is demonstrated on the existing architecture is premature. (c) The sealed **confirmation family 52xxx** and several mandatory controls (inert channel, global-common history, fake pulse, permuted-between-droplets, tracker-independence K5) are **pending**. Per the mission's own gate logic we are **not cleanly in Case A**. Decision: **REPLICATE/REPAIR first**, then re-evaluate DESIGN.

---

## Where I agree / disagree with the previous agent

Agree: the rest storage result is real; the diffusion halo is local and bounded; H0 (global synchronization prevents individuation) is rejected at rest; deep-turnover **order** does not survive; the refusal to claim identity/life/agency; the discipline of sealing a prereg and disjoint seed families; the reproducibility of the rest decode from committed code (a genuine improvement over the V3 headline-number incident).

Disagree: the "causal" framing of the rest result; the K2 PASS (post-hoc coordinate switch, wrong feature class); the "NOT maintained" turnover headline (should be INDETERMINATE-positive for dose); the direct GO to ACTIVE-RECONSTRUCTION; and the fact that **two load-bearing numbers (permutation null; deep-turnover decode) had no committed script** — the exact failure mode the project already suffered in V3. My `exp1_reaudit.py` closes that gap.

## Principal alternative explanations I considered
- *World-level confound (scaffold realization drives the decode, not per-droplet history).* Tested and rejected by the within-world permutation null (signal survives).
- *Near-zero-denominator inflating DD.* Tested and rejected by the absolute-magnitude and ε-sensitivity audit.
- *Trivial geometry (size/position) masquerading as memory.* Tested and rejected (baselines all R²<0).
- *Decoder overfitting under LOGO.* Tested by SVD-vs-normal-equation cross-check (identical) and jackknife stability.
- *Order "collapse" is an active anti-signal.* Rejected: deep-order p=0.92 vs null → it is **absence of signal** (negative R² = noise), not anti-correlation.

## Changes I judge necessary before any confirmation
1. **Repair the K2 gate**: define K2 as a **behavioural** decode (own history from Δuptake / readout observables) with a fixed coordinate rule (test **both** dose and order, pre-declare the pass condition), and commit the script **before** touching 52xxx.
2. **Commit** `exp1_reaudit.py` (permutation null + deep decode) so every headline number is reproducible-as-committed.
3. Run the pending **controls** (inert channel, global-common history, fake pulse, permuted-between-droplets) and **K5 tracker-independence** as first-class, not "pending".
4. Only then run **52xxx once**, apply the frozen scripts, and never adjust a gate afterward.
