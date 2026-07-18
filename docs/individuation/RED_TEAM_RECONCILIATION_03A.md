# LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03A — Red-team reconciliation

*Resolves the six parallel-audit points. Two of them (2, 3) were **real defects that changed a reported DEV
conclusion**; all are now fixed in code and re-verified. No 54xxx seed executed.*

## Point 1 — prospective runner seed allowlist ✅ RESOLVED
The DEV runner (`turnover_dev_runner.py`) is intentionally locked to 50001–50010 (a safety feature — it can never run
prospective seeds). The prospective run needs a **separate sealed runner**: `turnover_prospective_runner.py`, which
accepts **only 54001–54096** (+ endpoint-blinded reserve 54097–54120) and is blocked by a hard **authorization
guard** (`TP03A_PROSPECTIVE_AUTHORIZED` must equal a sealed token that does not yet exist). Verified: a `54001` run
prints `⛔ NOT AUTHORIZED`; a DEV seed via the prospective path is `REFUSED` (not in family). No output file is
created. `--selfcheck 50002` validates the schema on one DEV seed without touching any 54xxx.

## Point 2 — geometric neighbour (not (i+1)%K) ✅ RESOLVED — **corrects a DEV conclusion**
The parent decode used `neigh = dose[(i+1)%K]`, an **arbitrary index label**. Replaced by the **geometrically
nearest droplet** (minimum periodic centroid distance). Impact on the DEV data (11-D target features):

```
own-dose R²=0.135    neigh (i+1)%K R²=+0.580  [ARTIFACT]    neigh (geometric-nearest) R²=−1.04
```

The parent's alarming "neighbour decodes own-dose better than own (0.58 > 0.135)" — which I had read as evidence of
**homogenized/distributed** encoding in `TURNOVER_SELF_AUDIT_03A.md` — was an **(i+1)%K labelling artefact**. With the
correct geometric neighbour, **own exceeds both the geometric neighbour and the global scope**, and the honest DEV
state is simply **unresolved/underpowered** (own does not beat its own permutation null at n=4), **not** distributed.
The frozen analysis (`turnover_ownership_analyze.py`) uses geometric neighbours throughout;
`TURNOVER_OWNERSHIP_DEV_CERTIFICATE.json` carries the corrected numbers.

## Point 3 — leak-free world bootstrap ✅ RESOLVED — **real leakage demonstrated**
The parent's `boot_ci` resamples worlds **and relabels groups**, so a world duplicated in a resample gets two group
ids and — under LOGO — its identical rows sit in **both train and test**. Measured: a duplicated world occurs in
**91 %** of resamples; the naive CI median is inflated (0.207, tail to +0.85) versus the **leak-free** CI
[−0.33, 0.135, 0.38]. The frozen analysis computes LOGO predictions **once on unique worlds**, then bootstraps worlds
over the fixed per-world held-out (y, prediction) pairs — a duplicated world can never enter both train and test.

## Point 4 — λ₊-only ablation ✅ RESOLVED
The existing ablation zeros **both** λ₊ and λ₋. Added `MEM_ABLATE_PLUS` (λ₊=0, **λ₋=0.15 kept**) as the **primary**
manipulation check; the both-zero ablation is recorded separately and never conflated. DEV (rest, seed 50002):

```
own intact            = [0.514, 0.100, 0.118]
own FULL ablation      = [0.000, 0.000, 0.000]   (both channels)
own λ₊-ONLY ablation   = [0.055, 0.015, 0.017]   (~10% residual via the λ₋ attractant channel)
```

So the own-effect is ~90 % the direct uptake coupling (λ₊) and ~10 % the attractant channel (λ₋) — reported
separately, not hidden. The prospective runner persists `ablate_plus` and `ablate_full`.

## Point 5 — family cap ✅ RESOLVED
Already raised from 50 to **96** (`TURNOVER_POWER_REPAIR_03A.md`: Beta-Binomial P(N_valid≥18)=0.93). The reserve
`54097–54120` is **endpoint-blinded**: it may be activated **only** on a pre-outcome *geometric-eligibility*
shortfall (a quantity computable before any assay), declared before execution, hard cap 120 — no outcome is ever
inspected to decide activation.

## Point 6 — persist L/P/E/G state ✅ RESOLVED
The prospective runner **persists, per feasible world at the deep snapshot**: 11-D target memory features (L),
the L/P/E/G scope features (`scope_feats`), centroids (for the geometric neighbour), M_i, and dose. So the frozen
analysis can test environment/global ownership **without re-running**. Self-check confirms `persists_scopes=True`.
(Had this been infeasible, the honest fallback — stated here — would have been that E/G ownership cannot be tested;
it **is** feasible, so it is tested.)

## Net effect on the verdict
The corrections **weaken** my earlier distributed/homogenized lean (it rested on the (i+1)%K artefact) and leave the
ownership question cleanly **unresolved/underpowered at DEV** — which is exactly what the powered prospective test
(N=96, geometric neighbour, leak-free bootstrap, λ₊-only ablation, persisted L/P/E/G) is designed to settle. The
recommendation stands: **GO FOR SEAL** of the repaired design — but **do not seal or run**; a fresh agent audits,
verifies hashes/unused seeds, and executes once after Tommy's authorization.
