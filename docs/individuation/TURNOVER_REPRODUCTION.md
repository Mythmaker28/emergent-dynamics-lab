# LCI-CAUSAL-TURNOVER-PREREG-03 — Reproduction commands

Pinned venv (byte-identical determinism verified on this platform):

```bash
python -m venv venv && venv/bin/pip install numpy==2.2.6 scipy==1.15.3 matplotlib==3.10.9
export PYTHONPATH=$PWD; mkdir -p work
```

## Phase 1 — reproduce the confirm-02 rest gate (must be byte-identical)

```bash
# regenerate the sealed certificate from committed raw -> 0 differences at 1e-12
venv/bin/python experiments/individuation/nonmerging_analyze.py \
    experiments/individuation/nonmerging_confirm_raw.json work/nm_cert_repro.json
# engine determinism spot-check (byte-identical to committed raw for these seeds)
venv/bin/python experiments/individuation/nonmerging_confirm.py work/nm_spot.json 53001 53002 53003
```

## Tracker / tracer / periodicity tests (all PASS)

```bash
venv/bin/python experiments/individuation/test_bijective_tracker.py      # 10/10
venv/bin/python experiments/individuation/test_turnover_tracer.py        # 6/6 (no-feedback, feed-guard,
                                                                         # determinism, M monotonicity, bijective)
```

## DEV turnover pilots (seeds 50001–50010; NO confirmatory seed)

```bash
venv/bin/python experiments/individuation/turnover_dev_runner.py work/turnover_dev_raw.json $(seq 50001 50010)
venv/bin/python experiments/individuation/turnover_dev_analyze.py work/turnover_dev_raw.json \
    docs/individuation/TURNOVER_DEV_CERTIFICATE.json
```

The runner **refuses any seed outside 50001–50010** (`REFUSED: ... runs NO confirmatory seed`). Committed raw:
`experiments/individuation/turnover_dev_raw.json`. Expected: 8 eligible, 4 feasible (deep@~790–890,
M_i≤0.25), deep_own ≈ +0.13 (4/4 worlds), deep own-dose R² < neighbour-dose (homogenization).

## NOT run by this mission

No `54xxx` (proposed confirmatory family) seed is executed. Opening it requires Tommy's authorization
(`TURNOVER_PREREG_VERDICT.md`).
