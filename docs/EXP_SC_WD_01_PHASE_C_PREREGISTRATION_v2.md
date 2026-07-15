# WD-01 Phase C — Preregistration (committed BEFORE selection)

Supersedes the schematic preregistration in `EXP_SC_WD_01_PHASE_C_PREREGISTRATION.md` with an executable spec.
No prospective run or inspection occurs until the selected mechanism is frozen and committed.

## Hypotheses
H1 dynamic-range; H2 write-signal insufficiency (see position). C1 tests H1; C2 tests H2.

## History family (two independent temporal coordinates, one physical channel = nutrient N)
Two-phase drive: phase A amplitude a_e for T=60 steps, then phase B amplitude a_l for T=60 steps, then
settle S=20, then read. a_e,a_l ~ U[lo,hi] independent. Coordinates: **h1=a_e+a_l (cumulative/slow)**,
**h2=a_l−a_e (recent−early/order)**. h1⊥h2 by construction (independent equal-variance draws → corr≈0).
- Family F_mid: [lo,hi]=[0.003,0.020] (viable, partially saturating).
- Family F_low: [lo,hi]=[0.001,0.008] (more graded; for the capacity–viability map).
Protocol: warm body with C0 engine (WARMUP=2000), **erase memory (Mf=0)** before each history (isolates the
history; all candidates start identical). Interrogation window S=20 fixed (preregistered; retains fast comp).

## Realized-input measurement (a requested 2-D history is not 2-D if the write collapses it)
Record Ψ(t) saturation occupancy, per-component write increments, integrated drive, fraction of steps with
|m|>0.999, and realized (m1,m2,m+,m−). Report design corr(h1,h2) and condition number.

## Development
Seeds {34001,34002,34003} (NEW). N_hist=12/family. RNG: F_mid seed 34100, F_low seed 34101.

## Prospective (SEALED — manifest hashed in results/wd01_phasec/prospective_manifest.json)
Seeds {35001,35002,35003} (NEW, disjoint). N_hist=12/family. RNG: F_mid 35100, F_low 35101. Novel coordinate
values + novel seeds. Generated and SHA-256-hashed now; executed once after freeze. HMC 9501–9516 untouched.

## Candidates (parametrize the FROZEN functional form via MCParams unless noted)
- **C0** frozen: eta_w0.05, eta_d1 0.03, eta_d2 0.003, k_exp 2.0, k_up 1.0 (baseline / negative control).
- **C1a** eta_w0.020, eta_d1 0.25, eta_d2 0.004, k_exp 1.0  (de-saturate + fast-forgetting fast comp).
- **C1b** eta_w0.030, eta_d1 0.15, eta_d2 0.003, k_exp 0.5  (strong Ψ de-saturation via low k_exp).
- **C1c** eta_w0.015, eta_d1 0.35, eta_d2 0.006, k_exp 1.0  (gentle, strong timescale separation).
- **C2a** distinct signals (subclass, minimal): component-0(fast) ← Ψ_a=tanh(k_a·(uptake−up_ref)); component-1(slow)
  ← Ψ_b=tanh(k_b·(N−c)); eta_w0.03, eta_d1 0.15, eta_d2 0.003, k_a=8.0, k_b=1.0. Two already-present local
  signals; no labels; each channel bounded and independently ablatable. Authorized only if C1 stays rank-1
  under the fair matched test (minimality).

## Decoding (leak-free)
Grouped **leave-history-out** ridge (lam=1), standardized on the training fold only; rows sharing a history
(across seeds) stay in the same fold. Decode h1,h2 from entity-mean (2-D) and spatial (10-D). Report the better.

## Baselines / controls
constant (R²=0), shuffled-history, same-law/different-seed, exact-clone ceiling; erase, transplant,
channel-specific ablation (lam_plus→0, lam_minus→0, both→0), material turnover.

## Selection rule (DEV, F_mid)
Score = min(R²(h1),R²(h2)) using the better readout, subject to viability (median localized size, not
whole-grid). Minimality tiebreak: prefer C0<C1<C2 if within 0.05. Proceed to prospective only if the winner
reaches score ≥0.40 on DEV F_mid; else FAIL at development and leave the prospective family SEALED/unused.

## Prospective pass gate (all required)
Both h1,h2 grouped R²≥0.50 on the sealed family; incremental R² of each coord after the other ≥0.15;
σ₂/σ₁ ≥0.30; viability preserved; both coordinates causally expressed (erase+ablation); no leakage.

## Stopping rule
One candidate frozen; prospective run once; no post-hoc repair on that family; row-LOO never used except to
document the earlier error.
