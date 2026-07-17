# LCI turnover raw reproduction 03M

- Result: **REPRODUCED**.
- Raw inputs: `results/LCI-TURNOVER-PROSPECTIVE-03G/raw_manifest_03g.json` (SHA-256 `ce8d2cb0b6158965acaeef3553f44c7f9bf0ef9b9567c858ff5cbb27f903a328`) and the 50 exact raw records listed in it.
- Generating script: `analysis/lci-turnover-raw-reproduction-03m/raw_reproduction_03m.py`.
- Certified-results commit: `9cb996bb891f9a618e593f2f5c302f30210458de`.
- Analysis branch parent: `9cb996bb891f9a618e593f2f5c302f30210458de`; authorization commit `c158bc0b848710edeafd425f31dfcbd5aefc0934` is its exact parent and an ancestor.

## Provenance and raw integrity

The canonical final-seal SHA-256 is `cdf7277a00e3017a1389e9334d983364b9aa0af88c646cdec2999e6ad88757fd`. All 22 final-seal canonical artifacts and all 37 execution-manifest runtime bindings match their declared Git blobs and SHA-256 values. The packaging bindings for the repaired execution manifest and reproduction guide match the committed objects.

The ledger verifies at terminal `CERTIFIED`: 108 ordered entries, tip `0d579d0fa40fd19afe7bfc26140133fc9c57de2b656a7606aa5a5bd8591791aa`. Seed starts and completions are exactly 54001–54050, once each, in ascending order. There are zero `SEED_RESUMED` events, zero reserve completions, and no second execution initialization. Git records each of the 50 raw paths as one addition after authorization, with no raw modification/overwrite.

All 50 exact committed raw blobs pass `LCI-TURNOVER-RAW-03G-v1`; every committed-byte SHA-256, ledger raw hash, and raw-manifest digest agrees. The Windows working-tree EOL conversion was deliberately bypassed and the checkout was not rewritten. There are 21 valid original worlds against the frozen minimum 18. Validity is exactly the conjunction of the frozen feasibility fields; reserve activation used only `seed, eligible, deep_reached, rest_assay_valid, deep_assay_valid, valid, reason` and used no outcome field.

## Canonical and independent reproduction

The frozen canonical analyzer was run on a temporary copy containing the exact immutable raw family and the exact ledger prefix ending at `FAMILY_CLOSED`. This was necessary because the committed ledger is already terminal `CERTIFIED`; the original run directory and certified outputs were never modified. The regenerated certificate and report are byte-for-byte identical to the committed artifacts.

The independent script reimplemented the preprocessing, training-fold scaling, λ=1 ridge, outer leave-one-original-world-out folds, fixed-world uncertainty, 1,000 within-world permutations, causal contrasts, and A–F tree without importing canonical analysis code. It agreed over 9357 compared leaves (9283 numeric), with maximum absolute numeric difference `0.0`.

| Quantity | Canonical | Independent |
|---|---:|---:|
| valid worlds | 21 | 21 |
| own-dose mean skill | 0.395445738 | 0.395445738 |
| permutation null p95 | 0.148331437 | 0.148331437 |
| empirical p | 0.000999000999 | 0.000999000999 |
| own causal mean | 0.164844991 | 0.164844991 |
| outcome | B | B |

Every canonical model prediction, original-world fold loss, t interval, fixed-fold bootstrap summary, permutation summary, paired scope contrast, causal interval, gate, and outcome in the machine JSON matched the independent calculation within the material tolerance `1e-12` (in fact, exact numeric agreement).

## A — G_OWN_PERM

Own-dose mean held-out skill is `0.395445738`; the null 95th percentile is `0.148331437` and empirical p is `0.000999000999` (threshold `<0.05`). The observed world-level skill t interval is `[0.175322714, 0.615568762]`. `G_OWN_PERM=true`.

## B — G_LOCAL_EXCLUSION

Positive paired values mean L has lower held-out loss than the comparator.

| Contrast | Mean | 95% t interval | Required lower > 0 |
|---|---:|---:|---:|
| L vs N | 0.530415889 | [0.236323626, 0.824508152] | true |
| L vs E | 0.207167727 | [-0.0220630992, 0.436398554] | false |
| L vs Gm | 0.489483547 | [0.0796802251, 0.899286869] | true |
| L vs B | 0.144609858 | [-0.0226050984, 0.311824815] | false |

The exact failed components are `L_over_E, L_over_B`. Therefore `G_LOCAL_EXCLUSION=false`: the target-local representation does not strictly exclude all frozen N, E, G-minus-target, and B comparison scopes.

## C — G_CAUSAL

| Contrast | Mean | 95% t interval |
|---|---:|---:|
| own intact−erase | 0.164844991 | [0.144321643, 0.185368338] |
| own−sham | 0.164844996 | [0.144321648, 0.185368344] |
| own−neighbour | 0.16484503 | [0.144321671, 0.185368389] |
| fixed mask | 0.142157483 | [0.12460949, 0.159705476] |
| λ+ only | 0.0181412477 | [0.0132184414, 0.0230640539] |

The λ+-only upper interval divided by the own-effect mean is `0.139913587`, below the frozen collapse ratio `0.5`; λ− remains `0.15`. Own positivity, own>sham, own>neighbour, λ+-only collapse, fixed-mask directional consistency, and the 18-world minimum all pass. `G_CAUSAL=true`.

## D — DISTRIBUTED_ENV and unique Outcome B

The exact frozen environmental source flags are `{"E": false, "Gm": false}` under the rule “E or Gm has positive held-out skill and L does not strictly beat that scope”. Therefore `DISTRIBUTED_ENV=false`. This does not prove that the environment stores nothing; it means environmental ownership is not established in the frozen E/G-minus-target access classes.

The gate vector is `FEASIBILITY=true`, `G_OWN_PERM=true`, `G_LOCAL_EXCLUSION=false`, `G_CAUSAL=true`, `DISTRIBUTED_ENV=false`. Exactly one A–F expression matches: **Outcome B — causal feeding effect without ownership**.

> A causal feeding effect remains after deep material turnover, but the target’s graded history is not shown to be locally owned relative to the frozen comparison scopes.

`G_OWN_PERM=true` beats the within-world null but does not by itself prove ownership. `G_LOCAL_EXCLUSION=false` blocks individuation. `DISTRIBUTED_ENV=false` does not transfer ownership to the environment. Forbidden interpretations remain: individual memory survives, identity survives, active reconstruction, heredity, reproduction, or definite environmental memory. Active reconstruction was not observed.

## Reproducibility record

- Clean executable: `C:\Users\tommy\Documents\ising-lci-turnover-03m-clean\Scripts\python.exe`.
- Runtime: CPython 3.12.10 on Windows AMD64.
- Packages: `{"contourpy": "1.3.3", "cycler": "0.12.1", "fonttools": "4.63.0", "kiwisolver": "1.5.0", "matplotlib": "3.10.9", "numpy": "2.2.6", "packaging": "26.2", "pillow": "12.3.0", "pyparsing": "3.3.2", "python-dateutil": "2.9.0.post0", "scipy": "1.15.3", "six": "1.17.0"}`.
- Wall runtime: 31.786 seconds.
- Command: `& "C:\Users\tommy\Documents\ising-lci-turnover-03m-clean\Scripts\python.exe" "C:\Users\tommy\Documents\ising-v3-reproduction-03m-final\analysis\lci-turnover-raw-reproduction-03m\raw_reproduction_03m.py" --repo "C:\Users\tommy\Documents\ising-v3-reproduction-03m-final"`.
- Simulation/runner modules imported: none. Engine import attempts: none. No seed command was called.

## Derived output hashes

- `analysis/lci-turnover-raw-reproduction-03m/CLAIM_IMPACT_03M.md` — SHA-256 `8ec0bbbe193d9570255b3c7eacbec6cbe857c6c38d10b964c40f75110af0f383`
- `analysis/lci-turnover-raw-reproduction-03m/OUTCOME_B_REPRODUCTION_03M.png` — SHA-256 `938ad2d4311b997020e58c9c70d5381fde7dc1d24eee3e269594eb099138d6a1`
- `analysis/lci-turnover-raw-reproduction-03m/PRIMARY_RESULTS_AND_GATES_03M.csv` — SHA-256 `e979decac2a73b43a9b28d275b9cf5e9b9012038971230b87e1c15ec59ab52e3`
- `analysis/lci-turnover-raw-reproduction-03m/REPRODUCTION_RESULT_03M.json` — SHA-256 `d8e4d500b22e7720a21af2533716e6e87abf59c1ab13e7831ebdb26c472ea3af`
- `analysis/lci-turnover-raw-reproduction-03m/SEED_FEASIBILITY_03M.csv` — SHA-256 `71fd1804a7c61ddb21e71d70523a085da4eb27a2a1034a8b0f8a914ae05a6c0e`

The report's own hash is recorded in the reproduction journal after generation, avoiding a self-referential hash cycle.
