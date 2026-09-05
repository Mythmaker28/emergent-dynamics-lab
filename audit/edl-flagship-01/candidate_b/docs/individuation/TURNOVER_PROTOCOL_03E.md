# Authoritative PRESEAL candidate protocol — LCI-CAUSAL-TURNOVER-PRESEAL-03E (REPAIRED)

## Status: NOT AUTHORIZED, NOT EXECUTED, NOT SEALED. Repair of the audited 03C candidate `a5e0a552`.

This is the single canonical specification. **`PRESEAL_CANDIDATE_PROTOCOL.md` (03C) and the 03A addenda are
SUPERSEDED** by this file for every material blocker below; their history is retained, not rewritten. No `54xxx`
seed has been run. This repair does **not** create a final seal; a fresh independent agent must re-audit and seal.

The six material blockers of `FINAL_PRESEAL_AUDIT_03D` are addressed here; each maps to committed, tested code.

## Central question (unchanged)

Does the target droplet retain its **own graded causal information** through deep material turnover under the
passive-copy C1c architecture, stored **locally** rather than recoverable equally from a geometric neighbour, a
target-memory-masked environment, or the target-memory-removed global world? No identity/life/reproduction/heredity/
evolution/active-reconstruction claim is made.

## Frozen engine, geometry, family (unchanged from 03C, re-affirmed)

Engine `MultiChannelMemoryEngine` C1c (`eta_w=0.015, eta_d1=0.35, eta_d2=0.006, k_exp=1.0, lam_plus=0.25,
lam_minus=0.15`). 3 targets ≥45 cells, pairwise ≥24. Two 60-step local Gaussian histories, amp `[0.005,0.035]`;
primary label = own cumulative dose `a1+a2`. Rest settle 120. Deep threshold per-target passive-cohort `M_i≤0.25`.
Turnover cap 1500. Probe uniform `0.25×5`, horizon 40, N-standardise 40. Bijective tracker; diagnostic cohorts/IDs
never enter physics/association/features. **Family: primary `54001-54050` (50) + reserve `54051-54096` (46), cap 96,
minimum 18 valid worlds**, outcome-blinded ascending reserve (unchanged; audit PASS).

## B3 — low-dimensional access scopes (was 32,768 predictors)  → `turnover_scope_features_03e.py`

E and G are no longer raw 8×64×64 field stacks. Frozen, physically-interpretable, ≤24-predictor features, chosen
without consulting any outcome; scaling still learned on training worlds only:

| scope | definition | dims |
|---|---|---|
| L | target memory (`m1/m2` mean/std/p10/p50/p90, std(m1−m2)) | 11 |
| N | geometric-nearest neighbour memory (same 11) | 11 |
| P | target + nearest + farther neighbour memory (diagnostic) | 33 |
| B | target body baseline | 8 |
| **E** | 8 fields × 3 fixed radial annuli around target, **target m1/m2 masked** | **24** |
| **Gm** | occupied-cell global mean+std of 8 fields (**target memory removed**) + up_ref + occ_frac | **18** |
| Gf | same global summary **including** the target (diagnostic; nests L) | 18 |

Detectability (frozen): these detect own-dose information carried by the coarse radial/global profile; they cannot
see fine sub-annulus or non-radial spatial detail — stated, not silently assumed absent. Raw fields are persisted
only as a future-work coarse 8×8 downsample and are **not** the decoder input.

## B2/STAT — repaired inference & gates  → `turnover_statistics_03e.py`

Unit = original world; outer **leave-one-original-world-out**; ridge λ=1; training-only scaling; **no** refit in the
bootstrap; **no** original world in train and test; own cumulative dose the sole primary coordinate (order/m− secondary,
no max-switch). A **content-hash duplicate-world guard** rejects a world duplicated under a new id (disguised leakage a
by-id check cannot see). Frozen gates:

- **G-OWN-PERM** — L own-dose held-out mean skill exceeds a **within-original-world dose permutation null**, frozen p<0.05.
- **G-LOCAL-EXCLUSION** — L strictly lower held-out loss than **N, E, Gm, B** (each paired Student-t lower 95% > 0).
  L is **not** required to beat Gf (it nests L). This removes the incoherent "L beats G-full" gate.
- **G-CAUSAL** — paired original-world causal-expression gate at deep turnover: own(intact−erase) lower CI>0, own>sham,
  own>neighbour, **λ₊-only ablation collapse** (own under λ₊=0 < 0.5×own, λ₋ preserved), fixed-mask directionally
  consistent, ≥18 worlds.
- **PRIMARY PASS = G-OWN-PERM ∧ G-LOCAL-EXCLUSION ∧ G-CAUSAL.** A positive feeding contrast alone is insufficient.
- G-INCREMENT (P-over-L, Gf-over-L): interpretive only; cannot rescue a failed exclusion gate.

## B1 — one-shot authorization & hash-chained ledger  → `turnover_execution_ledger.py`, `turnover_prospective_runner_03e.py`

Approval must bind the exact **FINAL_SEAL sha256** (not just the manifest blob), `one_execution_only`, the manifest
blob, the frozen phrase, and a non-empty id/approver/UTC. Execution atomically **O_EXCL-creates** the canonical run
ledger; a second fresh start is refused. The ledger is append-only and **hash-chained** (tamper/reorder/truncate
rejected by `verify_chain`); it consumes the authorization id, records code/env hashes and the planned family, stores a
**SHA-256 per raw output**, refuses to rerun a completed seed, and a completion entry closes it with the raw manifest.
Honest boundary: this enforces one execution in the canonical run directory; it cannot bind a malicious external copy.

## B4 — canonical A–F decision tree  → `TURNOVER_DECISION_TREE_03E.json`

One machine-readable tree (A supported / B passive local remnant / C silent trace / D persistence fails / E
feasibility failure / F distributed-environmental), each with a Boolean gate expression, authorized wording, forbidden
claims, and an `active_reconstruction_justified` flag (true only for B/D, and only for a FUTURE separately-authorized
architecture). Precedence E→F→A→C→B→D.

## B5 — environment & power  → `TURNOVER_ENVIRONMENT_03E.md`, `turnover_power_regen.py`

One authoritative turnover env (Python 3.11.15 / numpy 2.2.6 / scipy 1.15.3 / matplotlib 3.10.9), scoped separately
from the V4 paper Docker, bound to the seal by lock hash. Committed deterministic power regenerator reproduces
`P(N_valid≥18|96)=0.924519`. Clean-room verified.

## B6 — protected-main provenance  → `PROVENANCE_REPORT_03E.md`

Local `main`=`f3921a4` verified and archived to `archive/main-f3921a4` (main untouched); its relation to the remote
`main`=`6d0bed6…` is documented as an out-of-scope repo-sync matter — the turnover lineage descends from CONFIRM-02,
never from main.

## Stop conditions (unchanged)

No `54xxx` before explicit human approval bound to a final seal. No code/feature/seed/gate change after the seal.
No extension past 54096. <18 valid worlds at cap → feasibility failure (Outcome E), no endpoint verdict. This repair
creates no final seal and runs no seed.
