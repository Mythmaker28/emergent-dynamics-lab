# LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03E — environment repair & clean-room report (blocker B5 / ENV-01, REPRO-01)

## The contradiction (audited)

Four descriptions disagreed: manifest 03C said Python 3.10.12; `pyproject.toml` requires `>=3.11`; the `Dockerfile`
pins numpy 2.1.3 / matplotlib 3.9.2 / sympy 1.13.3 and **no scipy**; the audit venv was 3.12.10 / numpy 2.5.1 /
scipy 1.18.0. And no committed script regenerated the power headline.

## Resolution — scope the turnover environment separately

The repository `Dockerfile`/`pyproject` serve the **V4 paper** (Set-Valued Causal Metrology) reproduction — a
different pipeline that legitimately uses numpy 2.1.3 + sympy and no scipy. Conflating it with the turnover pipeline
was the root of the contradiction. The repair **scopes** the turnover environment to its own authoritative lock,
`TURNOVER_ENVIRONMENT_LOCK_03E.txt`, bound to the final seal by SHA-256:

| component | authoritative turnover value |
|---|---|
| Python | 3.11.15 (satisfies `pyproject >=3.11`) |
| NumPy | 2.2.6 |
| SciPy | 1.15.3 |
| Matplotlib | 3.10.9 |
| platform | Linux x86_64 (determinism guaranteed only here) |

This is the exact platform on which CONFIRM-02 reproduced byte-identically and on which every 03E test passes. The
turnover execution manifest 03E records this env and its lock hash; the runner refuses to start unless the lock is
present and its hash is recorded in the ledger start entry.

## Committed power regenerator (REPRO-01 closed)

`experiments/individuation/turnover_power_regen.py` regenerates the family-size headline deterministically (2-D
Gauss-Legendre quadrature, no RNG):

```
mean_valid_probability        = 0.386363636363...
P(N_valid >= 18 | N = 50)     = 0.570903754176   (matches audit 0.570904)
P(N_valid >= 18 | N = 96)     = 0.924519023324   (matches audit 0.924519023326 to 1e-9)
```

## Clean-room run (this repair)

Created from the lock (`python3.11 -m venv; pip install numpy==2.2.6 scipy==1.15.3 matplotlib==3.10.9`) and executed:

| check | result |
|---|---|
| imports + compile of all 03E modules | PASS |
| `test_turnover_preseal_03e.py` (18 assertions: B1/B2/B3/B5) | PASS |
| `turnover_power_regen.py` (matches 0.924519 / 0.570904) | PASS |
| `turnover_prospective_runner_03e.py --selfcheck` (no engine, no seed) | PASS |
| existing `test_bijective_tracker.py` | 10/10 PASS |
| existing `test_turnover_preseal_03c.py` | 9/9 PASS |

If this environment cannot be recreated from the lock, the candidate remains NOT READY.
