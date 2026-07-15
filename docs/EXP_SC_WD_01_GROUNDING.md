# EXP-SC-WRITING-DIMENSIONALITY-01 — Repository Grounding (G1)

Date: 2026-07-15. Repo: `Mythmaker28/emergent-dynamics-lab` (local mount). Agent: autonomous scientific handoff.

## Verified state (OBSERVED)
- **Live HEAD is `main`**, currently deep in a *causal-metrology* line (Set-Valued Causal Metrology, EXP-GT-NASI-00, EXP-GT-PC-00) whose commits repeatedly record "Droplet pilot + EXP-SC-01 BLOCKED". The handoff's implied "MCM just passed, on the MCM branch" is **not** the state of `main`. The droplet arc lives on isolated `exp/` branches.
- **Cited MCM commits exist and are the tip of `exp/sc-multi-channel-organizational-memory-00`:**
  - `0ea1250` IOM-00 FINAL — "PASS – HISTORY-CLASS MEMORY ONLY" (high-dim *storage* later downgraded).
  - `65582d0` MCM storage-audit + preregistration (IOM erratum; readout R1: m+→uptake, m−→attractant).
  - `5841b9b` MCM FINAL — "PASS – ORDER-SENSITIVE MEMORY ONLY".
- **`7c91b91` is a git BLOB, not a commit** — it is the content hash of the frozen scaffold *engine file*, used as an integrity anchor in commit messages ("bit-identical to frozen engine 7c91b91"). No missing scaffold commit; the earlier apparent discrepancy is resolved.
- **Code + raw results present.** `edlab/experiments/sc_mcm/{engine,experiment,continuous,harness,certify,config}.py` (549 LoC) and `results/sc_mcm/{central_dev,central_prospective,cont_dev,cont_prospective}.pkl`, `certificate.json`, figures. `sc_mcm` is tracked on the MCM branch (not on `main`); raw `.pkl` are gitignored but present in the tree.
- **Certificate reproduces the handoff numbers**: channel_contrast 70.3 (dev)/73.1 (prosp); order on uptake axis ~1e-4; ablate_all 0.0; turnover_M 0.12; size 103.5/93; continuous decode p1=-0.087, p2=0.570, n_dims_decodable=1, response_effdim=1.08, individuation_auc=0.748; gates G10-G12 FALSE; verdict "PASS — ORDER-SENSITIVE MEMORY ONLY".

## Premises checked
- **Backward compatibility (independently, this session):** MCM(lam_minus=0) is **bit-identical** to IOM-00 over 200 steps (max|dev|=0.00e0, all fields). lam_minus perturbs **only** attractant `c` (d_Mf=0, d_rho=0 at one step) → the write is genuinely frozen and the 2nd channel is orthogonal. (G3 PASS.)
- **No leakage:** the physics receives only nutrient/attractant drives; no identity tag, cohort id, seed id, or probe label enters the dynamics. Probe/condition labels exist only in the analysis harness. (G6 PASS.)
- **Sealed/blocked assets untouched:** HMC prospective (9501–9516) SEALED; SC-PILOT-CAUSAL-FINGERPRINT and EXP-SC-01 BLOCKED. Not opened, not launched.
- **Environment traps** (per prior note) confirmed: create-only FUSE mount (no unlink), stale `.git` locks, 45 s one-shot shells (no background jobs), a 30-min heartbeat committing to `main`. → work on an isolated branch, commit via lock-free plumbing, checkpoint every unit.

## Working branch
New isolated branch **`exp/sc-writing-dimensionality-01`** created from the verified MCM final **`5841b9b`**. `main` is not touched.
