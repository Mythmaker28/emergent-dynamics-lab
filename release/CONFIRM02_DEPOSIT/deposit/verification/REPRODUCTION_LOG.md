# Reproduction log — CONFIRM02 deposit pass

## Decision

The frozen reproduction recipe has two stages.

**Stage 1 — simulation.** `nonmerging_confirm.py` over seeds 53001–53032. Each seed runs an 800-step
warm-up of a chaotic reaction-transport PDE on a 64×64 grid, then five branch families
(intact, erase×3, sham, ablate, erase_ablate×3) each with an N-standardisation reset, a 40-step
settle, a 5-step probe and a 40-step measured horizon. **NOT RE-RUN.** This is not "demonstrably
cheap": it is tens of thousands of PDE steps per seed across 32 seeds, far beyond the per-call
tooling budget available for this pass. Skipping it is recorded rather than papered over.

**Stage 2 — analysis / certificate.** `nonmerging_analyze.py` on the committed raw record. Pure
NumPy: leave-one-group-out ridge decoding, 3000-sample bootstrap CIs, 5000-sample within-group
permutation nulls, 5000-sample world bootstrap. **RE-RUN**, because it is demonstrably cheap.

## Command actually executed

```
python3 sources/experiments/nonmerging_analyze.py \
        sources/experiments/nonmerging_confirm_raw.json \
        verification/RECOMPUTED_CERTIFICATE_02.json
```

Wall clock: **33.7 s** (real 0m33.660s). NumPy 2.2.6 on the machine used for this pass — the same
NumPy version as the sealed platform.

## Result

Console output reproduced every gate verdict:

```
seeds=32 eligible=23 G0-valid=23 nonfusing_frac=1.00
[G0 feasibility] valid>=12:True frac>=0.85:True -> PASS
[G1 storage]     DD_mem=2590 off=7.03e-05 -> PASS
[G2 readout]     dose_R2=+0.691 null95=+0.153 neigh=-0.014 -> PASS
[G3 causal]      own CI=[0.19258340353198225, 0.2232705006888931, 0.25834348856712364] ... abl_ratio=0.000 own_fixed=0.20679489102504786 -> PASS
[G4 locality]    own-neigh CI=[0.19258547407545254, ...] neigh_mean=-7.316792126109839e-06 -> PASS
[G5 robustness]  own_fixed CI=[0.1799347054467802, ...] same_sign=23/23 tracked/fixed=1.0814659135610676 -> PASS
>>> G6 causal individuation: PASS
```

**All gated statistics reproduce exactly**, digit for digit, including every `per_seed` row.

**Not byte-identical.** Five non-gating floats differ by 1–3 units in the last place
(relative 1.4×10⁻¹⁶ to 1.6×10⁻¹⁴):

| key | committed | re-derived |
|---|---|---|
| `G2.dose_ci[0]` | 0.5812680051877672 | 0.5812680051877673 |
| `G2.dose_ci[1]` | 0.8241650210611119 | 0.8241650210611118 |
| `G2.order_R2` | 0.375538457118857 | 0.3755384571188567 |
| `G2.order_null95` | 0.10560937206682695 | 0.10560937206682686 |
| `G2.neighbour_dose_R2` | −0.014269612843656132 | −0.014269612843656354 |

This is the expected signature of a different BLAS/LAPACK backend behind the same NumPy version
(all five come from the ridge/least-squares path in G2). It touches **no gate** and **no headline
number**. It is carried as five `DIFFERS` rows (X01–X05) in the provenance ledger, and the
manuscript quotes these quantities only at a precision where both computations agree.

## Independent secondary checks (from the committed raw record, not from the certificate)

- 32 records; 23 with `eligible=true`; 23 with `g0_valid=true`.
- 69 droplet-targets = 23 × 3; **69/69** own effects > 0; per-target range +0.0298 to +0.9022.
- World-level own mean 0.2236416257 — matches `G3.own_mean` exactly.
- Fixed-mask world mean 0.2067948910; tracked/fixed 1.0814659136 — match exactly.
- Ablation mean exactly 0.0.
- Max coverage across valid worlds 1.1963 %–5.6396 %.
- corr(world dose, own) = +0.173795 — consistent with the "+0.17" quoted in `VERDICT_02`.

## Seal integrity

All 8 SHA-256 entries in the PRESEAL `sealed_file_sha256` manifest were re-hashed against the
content committed at the branch tip `9c8a62c`. **8/8 match.** No code or protocol file changed after
the seal.

## Not done, deliberately

- No new simulation, no new seed, no new exploratory analysis.
- No figure regenerated (`make_nm_figure.py` not run; the committed PNG is deposited as-is).
- Nothing committed, pushed, tagged or merged.
- Nothing submitted anywhere.
