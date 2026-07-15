# CONFIRMATION_PREREGISTRATION_ADDENDUM_01 — LOCAL-CAUSAL-INDIVIDUATION-00

**Purpose.** The prospective analysis of 51xxx exposed two under-specifications in the sealed gate. Running the sealed confirmation 52001–52012 under the *original* gate would inherit a post-hoc coordinate choice and two uncommitted analysis scripts — which would make any "confirmation" scientifically void. This addendum **repairs and freezes** the gate so a **valid** confirmation can be run later. It changes the analysis of the *unseen* confirmation family only; it does **not** rewrite the 51xxx result (that stays as re-scored in STATISTICAL_REAUDIT_01). **This must be committed BEFORE any 52xxx data is generated.** No parameter here may be adjusted after 52xxx is observed.

## Frozen carry-overs (unchanged from 3def3df)
Engine C1c (unchanged), targets K=3, size≥45, pairwise separation ≥24, local Gaussian drive σ=0.8·r_g, two phases 60 steps, amp∈[0.005,0.035], overlap tracker (TRACKER_SPEC), features = 11-D memory descriptor, decoder = grouped leave-one-world-out ridge λ=1, uncertainty = world-level percentile bootstrap n=3000 seed 20260715. Confirmation seeds = 52001–52012 (from FREEZE_SEAL; sha of the 4 sealed docs verified intact).

## Repair R1 — K2 must be BEHAVIOURAL, and both coordinates pre-declared
The original K2 ("behavioural own-history decode R²>0.50") was certified with a **memory** decode and a **post-hoc** coordinate switch (dose→order). For confirmation:
- **K2a (storage readout, memory features):** report own-dose and own-order LOGO R² with world-bootstrap CI and within-world null p — for **both** coordinates, no post-hoc selection. Pre-declared pass: max(dose,order) lower-CI > within-world null-95 **and** own−neighbour CI>0. (This is the effect actually demonstrated at rest; label it *storage/readout individuation*, not "causal".)
- **K2b (behavioural expression, NEW — the real causal test):** decode own history from **behavioural/readout observables** (per-droplet Δuptake statistics and Δ(mean c) relative to the same-seed no-drive counterfactual), same LOGO/λ/bootstrap. Pre-declared pass for *causal expression*: behavioural own R² lower-CI > within-world null-95 for at least one pre-declared coordinate, **and** a **readout-ablation** (λ_plus=λ_minus=0) collapses it to null. Only if K2b passes may the word "causal" be used.

## Repair R2 — commit the regenerator
`experiments/individuation/exp1_reaudit.py` (this branch) regenerates every headline number, **including** the permutation null (global + within-world) and the deep-turnover decode that had no committed script. Confirmation analysis MUST run through it (plus a behavioural-decode block for K2b); no ad-hoc inline scoring.

## Repair R3 — controls are first-class, not "pending"
Confirmation run must emit, per seed (including seeds with no admissible triple — record the reason): (1) global-common-history drive; (2) fake local pulse on empty space; (3) permuted-between-droplets re-simulated drive; (4) inert-memory-channel (λ=0); (5) readout ablation; (6) matched counterfactual (already in C_ij); (7) K5 tracker-independence — every headline recomputed under the naive largest-overlap tracker; (8) global/local/body-environment baselines incl. mass, edge-distance, local environmental state (not only size/position).

## Frozen confirmation gate (evaluated once, never adjusted)
| gate | pass condition (frozen) |
|---|---|
| C-K1 | DD_memory ≥ 10 **and** median off-diagonal |Δm| < 0.05 **and** absolute diagonal |Δm| > 3× baseline memory (guards against ratio-only dominance) |
| C-K2a | storage-readout own (best pre-declared coord) lower-CI > within-world null-95 **and** own−neigh CI>0 |
| C-K2b | behavioural own lower-CI > within-world null-95 **and** ablation collapses it (this alone licenses "causal") |
| C-K3 | own-dose deep lower-CI > 0.50 at M≤0.5 (certification); report INDETERMINATE if significant-but-sub-threshold |
| C-K4 | memory own R² − max(size,mass,position,edge) baseline R² CI excludes 0 |
| C-K5 | C-K1…C-K4 verdicts unchanged under the naive tracker |

**Decision rule (frozen):** confirmation *replicates the rest result* iff C-K1 ∧ C-K2a ∧ C-K4 ∧ C-K5 on 52xxx. *Causal expression at rest* is established iff additionally C-K2b. *Deep-turnover maintenance* is established iff C-K3; if dose is significant-but-sub-threshold in both families, report INDETERMINATE and quantify the pooled two-family CI. ACTIVE-RECONSTRUCTION-00 (Exp 2) is authorized **only** if rest is replicated **and** C-K2b passes **and** C-K3 is INDETERMINATE/NEGATIVE (i.e. genuine Case A) — not before.

## Reproducibility contract
No hyperparameter tuning after 52xxx opens. Analysis = frozen `exp1_reaudit.py` + committed behavioural block, seed 20260715. Every seed recorded (feasibility failure vs censure vs tracking loss vs negative scientific result distinguished). Commit this addendum + scripts, THEN run 52xxx once.
