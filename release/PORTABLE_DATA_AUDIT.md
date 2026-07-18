# Portable data audit

Every primary/secondary number traces to a committed raw pickle; the portable exports below make them readable
without unpickling. Raw pickles are retained in-repo for provenance. SHA-256 of each raw input is in
`release/data/data_manifest.json` and `RELEASE_MANIFEST.json`.

| portable file | format | source pickle | content |
|---|---|---|---|
| holdout_longitudinal.csv | CSV (144 rows) | results/observer/tca_holdout_raw.pkl | per-record × per-checkpoint memory stats, M, true h1/h2 |
| holdout_deep_arrays.npz | NPZ | same | deep-checkpoint 36×11 feature matrix + labels (decoder input) |
| causal_transplant.csv | CSV | results/wd01_phasec/phasec_causal_transplant_raw.pkl | response-vector norms under full / inert / erased |
| causal_inplace.csv | CSV | results/wd01_phasec/phasec_causal_inplace_raw.pkl | in-place full vs inert response norms |
| primary_table.csv | CSV | (regenerated) | per-checkpoint decode R² + bootstrap CI |
| primary_results.json | JSON | (regenerated) | gates, checkpoints, seeds, hashes |
| data_manifest.json | JSON | — | raw-input SHA-256 + export inventory |

## Decoder-search note (why the reproduction number differs from the manuscript inline value)
The exact inline scoring that produced the manuscript's h1 deep 0.98 / h2 deep 0.34 is not committed. During
this audit the following decoders were tried against the committed holdout features and none reproduced those
exact values (all reproduced the *conclusions*): grouped leave-one-history-out ridge (λ ∈ {3,1,0.3,0.1,0.03,0.01}),
leave-one-seed-out ridge, kNN (k ∈ {3,5}), per-history-aggregated R², `largest`-tracker features, and
feature sets F10 / F10+mminus_std / F10+size. Reproduced deep values cluster at h1 ≈ 0.89 (CERTIFIED) and
h2 ≈ −0.24…+0.04 (NOT ESTABLISHED). The committed `reproduction/` package fixes one fully-specified decoder as
canonical. See `CLEANROOM_REPRODUCTION_REPORT.md` (release blocker #1).

## Integrity
- No analysed run was excluded from the exports.
- Deterministic: fixed bootstrap seed (20260715); clean-room CSV/JSON are byte-identical (SHA-256 match).
