# STATISTICAL_REAUDIT_01 — LOCAL-CAUSAL-INDIVIDUATION-00

Independent recomputation from committed raw data. Deterministic; bootstrap/permutation seed **20260715** (V4 convention). Regenerate with `python3 experiments/individuation/exp1_reaudit.py` (reads the two committed raw JSONs). Decoder cross-checked two ways (normal-equation ridge vs SVD ridge — identical). Experimental unit = **world/seed (n=9)**; all inference is grouped at that level.

## 0. Provenance & integrity
| item | result |
|---|---|
| branch tip | `6806f1f` (matches mission) |
| Phase-0 seal | `3def3df` ancestor ✓ |
| V4 ancestor | `23b53ae` ancestor ✓ |
| main / release | `f3921a4` / untouched ✓ |
| working tree vs sealed blobs (16 files) | all **OK** (git hash-object == ls-tree) |
| FREEZE_SEAL doc hashes (PREREG, TRACKER, SEED, P0) | all **4 match** sha256 ✓ |
| FREEZE_SEAL `combined_seal_sha256` | **not reproducible** from obvious concat recipes (undocumented construction; non-load-bearing — component hashes verify integrity) |
| committed rest analysis (`exp1_analyze.py`) | reproduces 0.450 / 0.654 / DD 9018 **exactly** ✓ |
| committed permutation-null script | **absent** (recomputed here) |
| committed deep-turnover decode script | **absent** (`exp1_maintenance.py` produces `feat_deep`; nothing consumes it — recomputed here) |

## 1. Rest decode (prospective 51xxx, 9 worlds, 27 droplet–history pairs)
| target | R² | world-boot 95% CI | jackknife (leave-1-world) min–max | within-world null 95% | empirical p |
|---|---|---|---|---|---|
| own **order** | **+0.654** | [+0.517, +0.856] | +0.556 … +0.689 | +0.266 | **0.0002** |
| own **dose** | **+0.450** | [+0.380, +0.752] | +0.390 … +0.495 | +0.237 | **0.0070** |
| neighbour dose | −0.306 | — | — | — | (specificity; ≤0 expected) |
| size only | −0.172 | — | — | — | K4 baseline |
| position (cy,cx) | −0.166 | — | — | — | K4 baseline |
| size+position | −0.219 | — | — | — | K4 baseline |

Global permutation null 95th pct ≈ **0.05** (both coordinates); within-world null 95th pct ≈ **0.24–0.27**. The reported "null 0.23" = the within-world null (correct, stricter). Observed signals clear it. Decoder SVD cross-check: own-order 0.654, own-dose 0.450 (identical to normal-equation).

**Reading:** own ≫ neighbour ≈ trivial baselines; stable across worlds; beats the individuation-specific null. Storage/readout individuation at rest is **robust**.

## 2. Deep turnover (maintenance 51xxx, M=0.211, 3/3 tracks alive in all 9 worlds)
| target | R² | world-boot 95% CI | jackknife min–max | within-world null p | status |
|---|---|---|---|---|---|
| own **dose** | **+0.368** | [+0.140, +0.722] | +0.271 … +0.430 | **0.0012** | significant vs null, **not certified ≥0.50** → INDETERMINATE |
| own **order** | −0.659 | [−0.867, +0.528] | −0.869 … −0.474 | 0.92 | indistinguishable from zero → **order maintenance NEGATIVE** |
| neighbour dose | −0.005 | — | — | — | clean |

**Reading:** two different fates. Dose individuation is **partially retained** through 79% material turnover (significantly non-zero, jackknife-stable, but the lower CI 0.14 fails the 0.50 bar). Order individuation is **lost** (noise-level). The inherited single headline "not maintained" conflates these and, for dose, is contradicted by its own significance vs the null.

## 3. Influence matrix C_ij — ABSOLUTE audit
Single-perturbation differential design (perturb i, measure |Δ| in j, vs same-seed no-drive baseline).

| matrix | median \|diagonal\| | median \|off-diagonal\| | diag − off | DD (median) | DD range |
|---|---|---|---|---|---|
| memory-write \|Δm\| | **1.80×10⁻¹** | 1.84×10⁻⁵ | 1.80×10⁻¹ | **9018** | 2028 – 32395 |
| behavioural \|Δuptake\| | **2.66×10⁻⁴** | 1.92×10⁻⁷ | 2.66×10⁻⁴ | 1629 | 416 – 73134 |

Signs: all reported as |Δ| (magnitudes). ε-sensitivity of memory-write DD (median): ε=10⁻¹²→9018, 10⁻⁹→9018, 10⁻⁶→8667, 10⁻³→170. Absolute scale: baseline median |m1 p50| ≈ 1.58×10⁻², diagonal write ≈ 1.80×10⁻¹ → **≈11× baseline**. Sham/no-drive baseline is built into the differential (Δ vs no-drive counterfactual).

**Reading:** K1 storage dominance is a **real absolute** diagonal write, not a denominator artifact. The **behavioural** diagonal is diagonal-dominant in ratio but small in absolute magnitude (2.7×10⁻⁴) and never converted into a decode — hence cannot carry a "causal expression" claim on its own.

## 4. Control & exclusion ledger
| control (PREREG §Mandatory) | state | note |
|---|---|---|
| (1) global common history | **PENDING** | not in committed raw |
| (2) fake local pulses (drive empty space) | **PENDING** | not in committed raw |
| (3) permuted signals between droplets | **PARTIAL** | done in-analysis as neighbour-decode (−0.31) + within-world permutation null; not as a re-simulated drive |
| (4) inert memory channel (λ=0) | **PENDING** | not in committed raw |
| (5) readout ablation | **PENDING** | not in committed raw |
| (6) matched counterfactual, same seed | **DONE** | the C_ij differential baseline |
| (7) periodic detection + longitudinal tracking | **DONE** | frozen overlap tracker; 3/3 alive to M=0.21 |
| (8) global/local/body-environment baselines | **PARTIAL** | size, position tested (fail); mass/edge/env not separated |
| (9) tracker-independence (K5) | **PENDING** | headline not recomputed under the naive tracker |

| exclusion | seeds | rule | outcome-independent? |
|---|---|---|---|
| no well-separated triple | 51001, 51006, 51008 | frozen: size≥45 ∧ pairwise≥24 (geometry only) | **Yes** |

## 5. Gate re-scoring (against the frozen kill-switches)
| gate | frozen criterion | previous verdict | **my re-scored verdict** |
|---|---|---|---|
| K1 storage | DD≥10 ∧ off<0.05 | PASS | **PASS** (DD 9018; off 1.8e-5; absolute diagonal real) |
| K2 causal expression | **behavioural** own R²>0.50 ∧ (own−neigh) CI>0 | PASS (via order 0.65) | **NOT ESTABLISHED as specified** — no behavioural decode exists; memory-readout order=0.65 is a K1-adjacent storage readout, and the coordinate was chosen post-hoc. As *storage-readout specificity*: SUPPORTED-WITH-QUALIFICATION |
| K3 maintenance | own-dose lower CI>0.50 at M≤0.5 | NOT ESTABLISHED | **INDETERMINATE** (dose 0.368, CI [0.14,0.72]; significant vs null but sub-threshold). Order maintenance: NEGATIVE |
| K4 non-triviality | memory > size baseline | PASS | **PASS** (0.45 vs size −0.17, position −0.17, size+pos −0.22) |
| K5 tracker-independence | holds under both trackers | pending | **PENDING** (blocks any "confirmed") |

**Overall (frozen rule: K1∧K2∧K3∧K4∧K5):** not all gates pass ⇒ overall individuation is **NOT fully established**; the correct decomposition is *storage/readout established at rest; behavioural-causal not shown; maintenance indeterminate (dose)/negative (order); K5 pending.*
