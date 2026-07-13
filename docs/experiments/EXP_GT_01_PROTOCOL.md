# EXP-GT-01 — factorized ground-truth identity metrology
**Preregistered and frozen BEFORE any result. EXP-GT-00's observer and results are preserved unchanged.**

## 1. The ontology (the actual fix)
A scalar identity distance conflates five independent facts. They are separated, and **never recombined into a
composite score**:

| head | question | ground truth held by the evaluator |
|---|---|---|
| **A** | same **causal architecture**? | channel count, topology, propagation latencies |
| **S** | same **program / memory state**? | the stored bit word |
| **F** | same **functional I/O behaviour**? | the passive output signature an external observer sees |
| **L** | same **historical lineage**? | whether one continuous causal run connects the two windows |
| **M** | same **microscopic material implementation**? | which cells actually implement each component |

## 2. Expected vectors (ground truth, declared in advance)
`1` = same, `0` = different, `-` = not identifiable from trajectories (and the observer must not pretend otherwise).

| challenge | A | S | F | L | M |
|---|---|---|---|---|---|
| **E1** function-preserving handoff (component swapped for a microscopically distinct equivalent) | 1 | 1 | **1** | 1 | **0** |
| **E2** damage-and-repair (component removed, function breaks, then restored) | 1 | 1 | **0 then 1** | 1 | 0 |
| (a) same architecture, different program | 1 | **0** | 0 | 0 | 0 |
| (c) **identical passive output, different mechanism** (1010 vs 0101) | 1 | **0** | **1** | 0 | 0 |
| (b) different architecture, same program | **0** | 1 | **1** | 0 | 0 |
| (d1) exact copy, same program, reset history | 1 | 1 | 1 | **0** | **0** |
| (d2) copy with **reset memory** | 1 | **0** | 0 | **0** | **0** |

Two entries earn their keep. **(c)** has F=1 and S=0: identical passive output, different memory — a scalar cannot
express this. **E1** has F=1 and M=0: same function, different matter — this is the Ship of Theseus, and it is
exactly what the EXP-GT-00 scalar got wrong.

**(d1) is the honest hard case for L:** two exact copies at the same phase produce *literally identical*
trajectories. **L is then NOT identifiable from trajectories alone**, and the L head must **report indeterminacy
rather than guess**. Claiming to resolve L there would be fabrication.

## 3. E1 — the real gate, with assertions (no vacuity)
The old challenge (e) deleted a still-life and re-placed an identical one at the same phase, restoring the grid
exactly (0/701 frames differed) and "passing" at d = 0.0000. **E1 must therefore assert, per unit:**
1. **the grid trajectory actually changed** (frames differ);
2. **the replacement actually occurred** (old component's cells gone; new component's cells present, at a different
   site);
3. **the complete input-output behaviour is identical at EVERY timestep — no silent interval.**
The handoff installs the functionally-equivalent replacement **before** removing the incumbent, so the gate is never
unmanned. A **held-out replacement implementation** (a different microscopic realisation, never used in development)
is reserved for the final evaluation.

## 4. The observer — temporal causal-response fingerprints
It receives **only raw cell-state trajectories** plus the right to act: **standardized input pulses** and **blinded
counterfactual micro-perturbations** at *unlabeled* candidate sites. It records the **time-lagged influence** of each
perturbation on the output.
**It is NEVER given component positions, component labels, program bits, or the hidden causal graph.**
Deliberately, this replaces raw flow/output statistics — which is what made EXP-GT-00 mistake a brief flow
disturbance for a change of individual.

## 5. Freezing and evaluation
Representation and **per-head** decision rules are frozen on **development circuits**, then evaluated on **held-out
architectures, programs, layouts, and at least one entirely held-out replacement implementation**.
**Each head must meet its own preregistered criterion. Heads are NOT collapsed into a composite.**
Every head must first pass **synthetic must-pass and must-fail** cases.

**Only if EXP-GT-01 passes may a frozen representation be ported prospectively to EXP-SC-01. If it fails, the
droplets stay blocked.**
