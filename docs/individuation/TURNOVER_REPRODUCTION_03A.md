# LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03A — Reproduction commands

Pinned venv (byte-identical determinism verified):

```bash
python -m venv venv && venv/bin/pip install numpy==2.2.6 scipy==1.15.3 matplotlib==3.10.9
export PYTHONPATH=$PWD; mkdir -p work
```

## Parent reproduction gate (still byte-identical)

```bash
venv/bin/python experiments/individuation/turnover_dev_analyze.py \
    experiments/individuation/turnover_dev_raw.json work/repro_cert.json      # 4/8 feasible, own +0.131, own-dose 0.135
```

## Repair diagnostics (DEV; NO 54xxx)

```bash
# DiagEngine sanity (off == frozen engine) is asserted inside the diagnostics run
venv/bin/python experiments/individuation/turnover_dev_diagnostics.py work/diag.json 50002 50004 50005 50007
venv/bin/python experiments/individuation/turnover_access_analyze.py docs/individuation/TURNOVER_DIAGNOSTICS_CERTIFICATE.json
# event classification + fission secondary dataset
# (inline script in the mission log; output committed as TURNOVER_EVENTS_03A.json)
```

Expected: obs_own_frac ≈ 0.87× algebraic prediction; up_ref=0 memory ratio 1.00 & deep-own identical; copy-disabled
m₊ ratio 0.26×; eta_w=0 ratio 0.44×; L/P/E/G own-dose all below null at n=4 (unresolved).

## Tests

```bash
venv/bin/python experiments/individuation/test_bijective_tracker.py     # 10/10
venv/bin/python experiments/individuation/test_turnover_tracer.py       # 6/6
```

## NOT run

No `54xxx` seed is executed. No active-reconstruction architecture is implemented. Opening the confirmatory family
requires Tommy's authorization (`TURNOVER_VERDICT_03A.md`).
