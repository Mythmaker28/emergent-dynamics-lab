# EXP-SC-WRITING-DIMENSIONALITY-01 — Phase C Preregistration (authored, NOT executed)

Phase B justifies a minimal writing change. Executing it properly needs a fresh dev/prospective split, a
sealed prospective family, and a one-shot evaluation — a separate session. This preregistration fixes the
design NOW so the next run cannot tune on the outcome. **No physics was modified this session.**

## Diagnosis to fix
Storage is rank-1 because m1,m2 are two EMAs of ONE saturating+clipped scalar Ψ. The minimal cures target
the *number of independent write signals* and the *dynamic range*, NOT more readout channels.

## Candidate family (choose the SMALLEST that clears the gate; prefer C1/C2 over C3)
- **C0 (baseline):** frozen Ψ, frozen m. Reference.
- **C1 (range/gain):** reduce write gain and/or soften the m-clip so the viable regime stays graded
  (e.g. lower k_exp, lower eta_w, or replace the hard clip with a soft bound). One scalar; tests whether
  de-saturation alone lifts rank. Preregistered grid: k_exp∈{0.5,1.0,2.0}, eta_w∈{0.02,0.05}, soft-bound∈{off,on}.
- **C2 (component-specific write signal):** let the two components integrate **different already-present
  physical signals** — e.g. m1 driven by uptake-surprise (uptake−up_ref), m2 by the nutrient−attractant
  balance (N−c) — instead of both by the same Ψ. This is the *smallest change that creates a second
  independent write axis* without new state or labels. Grid: mixing angle θ∈{0,30,45,60,90}°.
- **C3 (local bounded recurrence):** only if C1+C2 fail. Local, bounded, independently ablatable, uses
  existing fields, no IDs/labels, preserves turnover/viability.

## Fixed before any run
- Histories: independent (p1,p2) over a **matched** range chosen from C0's graded band (from D2: ~[0.001,0.01]);
  plus a spatial-contrast arm only if already supported. Declared RNG seeds.
- Dev families: new disjoint seeds (34000-range). **Prospective: new sealed seeds (35000-range), generated
  and hashed BEFORE selection, opened once.** HMC 9501–9516 stay sealed; SC-PILOT/EXP-SC-01 stay blocked.
- Readout axes unchanged (m+→uptake, m−→attractant). Decoder: grouped leave-history-out ridge (primary),
  nearest-centroid + shuffled-label + constant + same-law/different-seed + exact-clone as controls.
- Primary metrics: held-out R² for BOTH coordinates; incremental R² of coord-2 | coord-1; sensitivity σ₂/σ₁;
  viability (localized size in band); turnover M; erase/transplant/channel-ablation contrasts.
- **Pass gate (preregistered):** two coordinates each R²≥0.5 on the SEALED prospective family, each beating
  constant + shuffled + same-law baselines; incremental coord-2 R²≥0.2; σ₂/σ₁≥0.3; viability preserved; no leakage.
- **Stop rule:** if the sealed test fails, report FAIL. Do not repair on the same split; do not add C3 after
  seeing C1/C2 results unless preregistered as the escalation.

## Prediction (SPECULATIVE)
C1 alone likely insufficient (one scalar remains one scalar). **C2 is the smallest plausible fix**: two
distinct physical drives give two genuinely independent write axes, and a de-saturated range lets them stay
analog. If C2 still collapses to rank-1, the substrate cannot store 2 independent magnitudes by local writing
and the program should stop escalating (memory ≠ individuation).
