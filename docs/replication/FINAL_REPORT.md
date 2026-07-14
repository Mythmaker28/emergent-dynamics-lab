# INDEPENDENT REPLICATION & CONSOLIDATION — FINAL REPORT

## What was done
An independent, adversarial reconstruction of CRD-03 from the frozen protocol only (no operational code imported),
a genuinely different second substrate (FitzHugh-Nagumo), an empirical coverage audit, a formal theorem treatment,
and a critical review whose goal was to reject the work.

## Headline findings

1. **The core identifiability result reproduces.** Differential contamination is independently identifiable and
   correctable (κ=0.12 → q̂/q=1.001); common-mode is unidentifiable (→ bound); collinear references abstain. The
   historical PASS is not a code artifact.

2. **A load-bearing operational claim is falsified.** The "rigorous lower bound from the largest-amplitude
   channel" silently assumes contamination *attenuates* (`sign(lam_i e_i) ≥ 0`). Under amplification (negative
   contamination, or a negative drift coupling with κ>0) the frozen instrument returns a confident **10.5%
   overstatement labelled CORRECTED**, and the point estimate covers the truth **0/40** times. Every historical
   case used κ≥0 and positive couplings, so this was never tested. The droplet POD study itself measured a
   negative-coupling reference (`c_global`, a=−0.50), so real substrates hit this.

3. **The fix is clean and verified.** Report the bracket `[min|v_i|, max|v_i|]` (covers |q| **40/40** in every
   regime, sign-agnostic) and abstain on a point estimate unless a sign contract is independently established
   (T6′). The corrected operational rule supersedes the frozen `LOWER_BOUND_ONLY`/`CORRECTED` logic.

4. **Quantitative accuracy is ctrans-specific.** On FHN the contamination *logic* transfers, but clean-case
   recovery is biased (q̂/q≈0.86). "General continuous metrology" is not supported; the identifiability structure
   is general, the quantitative accuracy is not.

5. **The droplet negative-transfer result stands and is reinforced** — the same sign issue would compound the
   already-common-mode contamination of the nutrient-field references.

## Consolidation gaps
No one-command containerized rebuild; no full figure pipeline; T6 correction not yet folded into a frozen
instrument. These keep the work below peer-review-ready.

## Standing constraints
No droplet pilot executed. No droplet physics / `β` / `D_int` / `rho` / `U` / `V` modified. Frozen historical files
unchanged (v00 6/6, CRD-01 4/4, CRD-03 4/4). New code lives only in `independent_replication/` and read-only docs.
The historical CRD-03 freeze was NOT rewritten — its flaw is documented, not silently repaired.
