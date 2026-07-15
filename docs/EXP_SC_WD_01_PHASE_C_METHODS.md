# WD-01 Phase C — Methods, Controls & Audits (reproducibility)

## Mechanism
Frozen MCM writing parameterized via MCParams (C0/C1) or a split-signal subclass (C2). C0/C1 change ONLY
{eta_w, eta_d1, eta_d2, k_exp}; readouts (lam_plus 0.25 → uptake, lam_minus 0.15 → attractant) unchanged.
Copy-correctness: the C2 subclass in `single` mode is bit-identical to the frozen MCM engine (max|dev|=0.00e0
over 150 steps), so `split` mode changes only the Ψ→component mapping.

## Protocol
Two-phase nutrient history (T=60 each), coordinates h1=a_e+a_l (cumulative), h2=a_l−a_e (order). Warm body
(C0, WARMUP=2000), **erase memory (Mf=0)** before each history (isolates the history; identical start for all
candidates), settle S=20 (preregistered), read memory. Families F_mid[0.003,0.02] (viable), F_low[0.001,0.008].

## Decoding (leak-free)
Grouped **leave-history-out** ridge (λ=1), standardized on the training fold; rows sharing a history (across
seeds) kept in one fold. Storage decoded from entity-mean (2-D) and spatial (10-D: mean/std/p10/p50/p90 of
m1,m2 over entity cells). Prospective also evaluated by strict train-on-dev/test-on-prospective (frozen decoder).

## Controls
- Baselines: constant (R²=0), shuffled-history (null mean ≈ −0.4, 95th ≈ 0.11), C0 negative control (rank-1).
- Causal (mean-transplant into a common erased body B0): full vs lam_plus=0 vs lam_minus=0 vs both=0; erase.
  Memory-inert (both=0) collapses to ≈0 → confirms the common body removes the body confound.
- Causal (in-place, memory-isolated): dR = R_full − R_both0 on the SAME post-history state (spatial memory intact).

## Capacity–viability map (§13)
Across candidates/families: storage 2nd-dim coupling σ₂/σ₁ vs entity size (viability). All candidates stay
localized (size ≈31–37); C1 lifts σ₂/σ₁ from 0.02 (C0) to 0.10–0.23 while viable → **CV-A for storage**. The
causal-response shortfall occurs at fixed viability → an observability limit, not CV-B.

## Reproduction commands
```
export REPO=$PWD PYTHONPATH=$PWD:results/wd01_phasec PYTHONPYCACHEPREFIX=/tmp/pyc
python3 -B results/wd01_phasec/dev_runner.py        # resumable; grouped dev selection
python3 -B results/wd01_phasec/prosp_runner.py      # SEALED prospective (manifest-driven), once
python3 -B results/wd01_phasec/causal_runner.py     # mean-transplant causal + ablations
python3 -B results/wd01_phasec/causal_inplace.py    # in-place memory-isolated causal
```
Raw: phasec_{dev,prospective_,causal_transplant_,causal_inplace_}raw.pkl. Sealed manifest:
prospective_manifest.json (SHA-256 c6d0cd3c5b82aa122ac7e5649888fbc53ca6faa8db68e2c1b48863e87fb9e202).

## Reproduction / Genome / Quantum audits
- REPRODUCTION READINESS: NOT READY — causal 2-D and transplantable second coordinate not achieved.
- GENOME: NOT REQUIRED — a failed causal readout does not justify a compact heritable code; the memory is
  distributed and (for coordinate 1) transplantable. Revisit only if serial bottlenecks later fail.
- QUANTUM: NOT USED — this is a classical readout-observability problem with no benchmarkable quantum advantage.
