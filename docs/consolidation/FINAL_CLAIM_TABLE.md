# FROZEN CLAIM TABLE (post-hold-out)

| id | claim | assumptions | evidence | prospective | hold-out | falsifier | status |
|---|---|---|---|---|---|---|---|
| C1 | RMS-over-window differencing dilutes transients as √(W′/W)→0; an integral does not | finite-energy transient | T1 + numeric | — | — | a transient not diluted | SOLID |
| C2 | A sham sharing only the drift *distribution* cannot remove its realized trajectory | independent realizations | T2 | — | — | per-instance removal | SOLID |
| C3 | One reference leaves `q(1−αĸ)` — scale unidentifiable | no absolute scale | T3 | — | — | recovery without scale | SOLID |
| C4 | Differential contamination is identifiable given distinct couplings | spread ≥ 0.15; ≥1 clean | T4 | 10/10 | — | a hidden differential case | SOLID |
| C5 | Common-mode contamination (κ_i ∝ a_i) is **non-identifiable** | — | T5, T6-E (constructive) | 10/10 | — | any passive recovery | SOLID |
| C6 | Attenuation ⇒ `max\|v\| ≤ \|q\|` (lower bound) | 0 ≤ α_iκ_i < 1 ∀i | T6-A, **0/2000 violations** | ✓ | ✓ | a violating case | SOLID |
| C7 | Amplification ⇒ `min\|v\| ≥ \|q\|` (**upper** bound) | α_iκ_i ≤ 0 ∀i | T6-B, **0/2000 violations** | ✓ | ✓ | a violating case | SOLID (corrects historical error) |
| C8 | Clean anchor ⇒ `\|q\| ∈ [min\|v\|, max\|v\|]` | ∃i: κ_i=0 | T6-C | ✓ | ✓ | anchor case the bracket misses | SOLID |
| C9 | Sparse contamination: m ≥ 2s+1 ⇒ point-ID | differential, distinct couplings | T6-D | ✓ | ✓ | a counterexample at m≥2s+1 | SOLID |
| C10 | No anchor + no sign ⇒ non-identifiable | — | T6-E (q′=2q construction) | ✓ | ✓ | any recovery | SOLID (impossibility) |
| C11 | Point identification of \|q\| | **conditional on an EXTERNALLY established sign/anchor contract** | benchmark used ORACLE contracts | ✓ | — | — | **CONDITIONAL — contracts not shown obtainable from passive data** |
| C12 | The instrument never emits a set excluding the truth | — | — | 10/10 | **541/1333 INVALID at SNR=5** | low-SNR null-gate misfire | **REFUTED — WITHDRAWN** |
| C13 | Structural identifiability transfers across substrates | rest pre-window | ctrans + FHN | — | — | a substrate mis-classifying | STRUCTURAL only |
| C14 | Quantitative accuracy transfers | — | FHN 0.86 | — | — | — | **ctrans-SPECIFIC** |
| C15 | Passive droplet references are common-mode contaminated | shared field N | POD | — | — | a clean far-field reference | SOLID (negative) |
| C16 | Droplet identity / continuity / life | — | — | — | — | — | **NEVER CLAIMED** |

**C12 is withdrawn.** The safety property holds only in the high-SNR regime tested; at SNR=5 the null-response gate
produces confident `{0}` sets that exclude the truth. No claim of universal safety may enter an abstract.
