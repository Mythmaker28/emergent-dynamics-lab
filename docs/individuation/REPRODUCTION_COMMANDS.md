# REPRODUCTION_COMMANDS — LOCAL-CAUSAL-INDIVIDUATION-00 re-audit

All numbers in INDEPENDENT_JUDGMENT_01 / STATISTICAL_REAUDIT_01 / VERDICT_01 regenerate from committed raw data (no engine re-run needed). Deterministic; bootstrap/permutation seed 20260715.

## Rest headline (committed author script — exact reproduction)
```
cd experiments/individuation
cp exp1_prospective_raw.json /tmp/exp1_prosp.json     # exp1_analyze.py reads this path
python3 exp1_analyze.py
# -> DD median 9018 ; own-dose 0.450 ; own-order 0.654 [0.517,0.856] ; neighbour -0.306 ; size -0.172 ; K2 -> CHECK
```

## Full independent re-audit (this branch — regenerates null + deep decode too)
```
cd experiments/individuation
cp exp1_prospective_raw.json /tmp/exp1_prosp.json
cp exp1_maintenance_raw.json /tmp/exp1_maint.json
python3 exp1_reaudit.py
# -> rest & deep dose/order R2, world-bootstrap CI, GLOBAL + WITHIN-WORLD permutation nulls with p,
#    leave-one-world jackknife, K4 baselines (size/position/size+pos), C_ij absolute audit + eps-sensitivity.
```

## Figure + machine-readable summary
```
cd experiments/individuation
python3 make_fig.py       # writes figure_individuation_audit.png + reaudit_summary.json
```

## Integrity checks
```
# working tree == sealed blobs @6806f1f
R=.; git -C "$R" ls-tree -r 6806f1f -- experiments/individuation | \
  while read m t sha p; do [ "$(git -C "$R" hash-object "$p")" = "$sha" ] && echo "OK $p" || echo "DIFF $p"; done
# FREEZE_SEAL doc hashes
python3 - <<'PY'
import hashlib,json
b="experiments/individuation"; s=json.load(open(f"{b}/FREEZE_SEAL.json"))
for f in ["PREREGISTRATION.md","TRACKER_SPEC.md","SEED_MANIFEST.md","P0_TECHNICAL_AUDIT.md"]:
    print(f, hashlib.sha256(open(f"{b}/{f}",'rb').read()).hexdigest()==s[f])
PY
```

## Environment
numpy + matplotlib only for the re-audit (no `edlab` engine needed). `pip install numpy matplotlib`. Python 3.11+. A future 52xxx confirmation additionally needs the committed `edlab` package (195 files) + `requirements-lock.txt`.

## What is NOT reproduced here (and why)
- Confirmation family 52001–52012: **not run** (Phase B gated; see CONFIRMATION_PREREGISTRATION_ADDENDUM_01 — gate must be repaired & frozen first).
- Engine-level regeneration of the raw JSONs from seeds: not attempted in-sandbox; the system is a chaotic reaction-diffusion PDE, so cross-platform bitwise reproduction is not expected — the appropriate provenance guarantee is committed-script determinism on a fixed platform, which the confirmation run will establish.
