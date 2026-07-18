# Claim ledger V4 — canonical reproducible numbers

Every longitudinal number is the output of the committed `python -m reproduction.primary`. Old (V1–V3)
values are historical and non-reproducible (`HEADLINE_NUMBER_ERRATUM.md`). Evidence classes: OBSERVED
(deterministic), ESTABLISHED (CI supports direction/threshold), NOT ESTABLISHED (gate not met with a CI that
excludes the threshold — underpowered/inconclusive, not a demonstrated absence), INFERRED (wide/overlapping
CI), SPECULATIVE (hypothesis). No claim is FALSIFIED.

| # | Claim | V3 value | V4 canonical value | class | authorized wording | provenance |
|---|-------|----------|--------------------|-------|--------------------|-----------|
| 1 | h1 decodable at initial (M≈1) | 0.92 [0.86,0.99] (sealed) / — | **0.78 [0.56,0.94]** | ESTABLISHED | "h1 is decodable at rest" | reproduction.primary; tca_holdout_raw.pkl |
| 2 | **h1 retained through deep turnover (primary result)** | 0.98 [0.97,1.00] | **0.89 [0.84,0.96]** | **ESTABLISHED (CERTIFIED)** | "h1 remained strongly decodable at deep turnover: R²=0.89, 95% CI [0.84,0.96]" | reproduction.primary; deep step 800, M≈0.19 |
| 3 | h1 tracker-independent | 0.96/0.98/0.99 (largest/2nd/long) | **0.91 (largest) / 0.89 (longitudinal)** | OBSERVED | "h1 decodes comparably from the largest and longitudinal trackers" | reproduction.primary tracker_independence |
| 4 | track survival through deep turnover | 36/36, 0 switches | **36/36, 0 switches** | OBSERVED | "100% track survival, zero reassignment switches" | raw (tca_holdout_raw.pkl) |
| 5 | h1 causal necessity (inert/erase carry no info) | −0.19 deterministic | −0.19 deterministic (unchanged) | OBSERVED | "erasure/readout ablation destroys the decode" | phasec_causal_*_raw.pkl |
| 6 | h1 causal sufficiency (transplant) | 0.61 [−0.69,0.87] | 0.61 [−0.69,0.87] (unchanged; separate experiment) | INFERRED (wide) | "transplant reinstates h1 in the point estimate; effect size uncertain" | phasec_causal_transplant_raw.pkl |
| 7 | h1 vs body size+mass (sealed) | 0.93 vs 0.64, CIs overlap | 0.93 vs 0.64 (sealed family; unchanged, labelled) | INFERRED (suggestive) | "suggestive; CIs overlap" | h2cert_sealed_raw.pkl (historical) |
| 8 | h2 decodable at initial | 0.90 [0.41,0.97] (sealed) | **0.80 [0.53,0.92]** | ESTABLISHED (storage) | "h2 is decodable at rest" | reproduction.primary; init |
| 9 | h2 causal expression | −0.04 / 0.30 (transplant/in-place) | unchanged | NOT ESTABLISHED | "h2 stored but causal expression not established; response ~1-D" | phasec |
| 10 | **h2 deep-turnover retention** | 0.34 [−0.89,0.87] (spans 0.50) | **−0.24 [−0.78,0.32] (below 0.50)** | **NOT ESTABLISHED** | "under the canonical analysis, h2 remained below the qualification threshold at deep turnover (R²=−0.24, 95% CI [−0.78,0.32]); this bounds the C1c architecture and this metric, not a substrate impossibility" | reproduction.primary; deep |
| 11 | mechanism of h2 non-persistence | indeterminate | indeterminate (unchanged) | SPECULATIVE | "the mechanism is indeterminate" | — |
| 12 | individuation | not supported | not supported (unchanged) | — | "does not individuate droplets" | — |

## Impact summary
The only load-bearing number that changed is **h1 deep-turnover: 0.98 → 0.89** (CI [0.97,1.00] → [0.84,0.96]).
It **remains CERTIFIED** (lower bound 0.84 ≫ 0.50). The h2 deep-turnover conclusion (**not established**) is
unchanged, now at −0.24 [−0.78,0.32]. **No conclusion is overturned; no claim is strengthened.** The change is
purely from adopting the committed reproducible pipeline over an uncommitted, non-recoverable one.
