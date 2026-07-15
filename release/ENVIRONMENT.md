# Frozen environment (reference reproduction)

## Interpreter and libraries (exact)
- Python: **3.10.12**
- numpy: **2.2.6**
- scipy: **1.15.3**  (used elsewhere in the repo; not required by `reproduction.primary`)
- matplotlib: **3.10.9**
- Lockfile: `requirements-lock.txt` (three pins). Full environment snapshot: `release/pip_freeze_full.txt` (145 pkgs).

## Reference system
- OS: Ubuntu 22.04 (Linux 6.8.x x86_64), containerized.
- CPU: 2 vCPU. RAM: ~3.8 GiB. No GPU required.
- Filesystem: any POSIX; outputs written under `reproduction/outputs/`.

## Root command
```
python -m reproduction.primary          # reproduce primary certification + figure + table + manifest
python -m reproduction.primary --check  # additionally assert values within tolerance of EXPECTED.json
python -m reproduction.export_portable  # (re)generate release/data portable exports
```
The command reads ONLY `results/observer/tca_holdout_raw.pkl`; it exits non-zero with a clear message if a
dependency or that data file is missing.

## Expected runtime (reference system, cold)
| step | work | wall time |
|---|---|---|
| import + load raw | numpy/matplotlib import, unpickle 36 records | < 3 s |
| decode + bootstrap | 4 checkpoints × 2 coords × 3000 history-grouped bootstraps | ~15–25 s |
| figure + CSV/JSON/NPZ | matplotlib render + writes | ~2 s |
| **total** | `python -m reproduction.primary` | **~20–30 s** |
| export_portable | CSV/NPZ from 4 pickles (no bootstrap) | < 3 s |

Determinism: fixed bootstrap seed (20260715) ⇒ byte-identical CSV/JSON across runs on the same
numpy build (verified: identical SHA-256).
