# LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03E — reproduction commands

Authoritative turnover environment (scoped separately from the V4 paper Docker):

```bash
python3.11 -m venv venv && venv/bin/pip install numpy==2.2.6 scipy==1.15.3 matplotlib==3.10.9
export PYTHONPATH=$PWD PYTHONIOENCODING=utf-8
```

## Repair tests (synthetic/static; NO engine, NO 54xxx seed, NO authorization)

```bash
venv/bin/python experiments/individuation/test_turnover_preseal_03e.py     # B1/B2/B3/B5: ALL PASS (18 assertions)
venv/bin/python experiments/individuation/turnover_power_regen.py          # P>=18@96=0.924519, @50=0.570904
venv/bin/python experiments/individuation/turnover_prospective_runner_03e.py --selfcheck   # static wiring; no seed
```

## Existing audited tests (still pass)

```bash
venv/bin/python experiments/individuation/test_bijective_tracker.py        # 10/10
venv/bin/python experiments/individuation/test_turnover_preseal_03c.py     # 9/9
```

## Power headline regeneration (REPRO-01)

```bash
venv/bin/python experiments/individuation/turnover_power_regen.py
# -> mean 0.386363..., P(>=18|50)=0.570903754176, P(>=18|96)=0.924519023324  (matches audit)
```

## What is NOT run

No `54xxx` seed. No engine instantiated by the tests. `turnover_prospective_runner_03e.py` refuses execution unless
`FINAL_SEAL_MANIFEST_03E.json` exists (it does not — this repair creates no seal) and an approval binds its sha256.
A fresh independent agent re-audits, seals, and only then may a human authorize one execution.
