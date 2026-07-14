# CRD-03 INDEPENDENT REPLICATION REPORT

## Method
Clean-room reimplementation `independent_replication/recover.py` from the frozen protocol only — imports NO
operational code (`pident`, `racq`, `exp_gt_crd03`); own names, own RNG, own tests. Blinded stages: R1 synthetic
closed-form (own model), R2 historical dev reconstruction, R3 historical prospective. Second substrate
`substrate_fhn.py` (FitzHugh-Nagumo excitable network) — genuinely different dynamics.

## What reproduces (the historical result is NOT a code artifact)
- **Differential contamination is identifiable and correctable.** R1: single κ=+0.12 → located, q̂/q=1.001;
  differential κ∈[0.05,0.20] located. Reproduces the CRD-02-fix claim from independent code.
- **Common-mode contamination is unidentifiable → attenuated value / lower bound.** R1: κ∝couplings → single
  consistent attenuated channel. Reproduces T5.
- **Collinear references abstain** (spread < 0.15 → ILL_CONDITIONED). Reproduces.

## What does NOT survive (independent audit finding)
- **The lower-bound / point-estimate rule fails under sign inversion.** Independent implementation reproduces the
  SAME failure as the frozen instrument: all-amplifying contamination under an asserted attenuation contract →
  q̂/q = 1.106 (overstatement). Coverage of the historical point estimate: 40/40 attenuating, **0/40 amplifying**,
  3/40 mixed-sign. This is a METHOD limitation (reproduced independently), not a code bug.
- **Fix verified.** The sign-agnostic bracket `[min|v|,max|v|]` covers |q| **40/40 in every regime**; the
  corrected rule abstains on a point estimate unless a sign contract is independently established.

## Second substrate (FitzHugh-Nagumo)
Structural transfer: differential contamination LOCATED, common-mode → lower value, amplifying → abstain (fixed
rule). **But clean-case recovery is biased (q̂/q ≈ 0.86, not 1.00)** — the excitable substrate's nonlinear drift
processing leaves residual, so quantitative accuracy is substrate-specific. The identifiability LOGIC transfers;
the quantitative accuracy does not transfer without substrate-specific calibration.

## Replication gates
| gate | result |
|---|---|
| R1 κ=0.12 corrected/bounded | PASS (located, 1.001) |
| R2 differential identifiable | PASS |
| R3 common-mode unidentifiable | PASS (bound) |
| R4 collinear abstains | PASS |
| R5 unseen topologies recovered | PASS (structural) / quantitative caveat on FHN |
| R6 hidden state / persistence | PASS (FHN has hidden recovery var; located) |
| R7 nonlinear/hysteretic represented | PASS (odd/even; FHN nonlinear) |
| R8 unit transforms don't change claims | PASS (scale-invariant ratios) |
| R9 no implementation labels in estimator | PASS (clean-room) |
| R10 truth/estimator separate | PASS |
| **sign/amplification (Phase E)** | **FAIL as stated — lower-bound theorem T6 falsified; restricted to T6′** |

## Shared dependencies (unavoidable)
numpy only. No historical instrument code. The historical *ground-truth systems* (ctrans) were used for R2/R3
reconstruction, as permitted (raw system definitions, not instrument code).
