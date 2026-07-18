# REPRODUCTION & CI — EXP-GT-NASI-00 (deliverables 21, 22)

## What was verified in THIS environment
* `make reproduce-nasi` runs the deterministic NASI battery. Run TWICE -> identical canonical SHA256
  `36b25c3ed1e13caa9d0321ac1f0fb7eee9ceeae8aa197bfd2ddf3418ec2ddd4a` (bit-identical; content-addressed seeds).
* `noise_aware/verify_freeze.py`: all 4 frozen files match the freeze manifest -> PASS.
* `noise_aware/cache_poison_test.py`: canonical SHA invariant to a poisoned bytecode cache when a fresh
  `PYTHONPYCACHEPREFIX` is used -> PASS. (This environment actively exhibited stale-bytecode and truncated
  mount-sync hazards during development; every run uses a fresh cache prefix and `-B`.)
* Python 3.10, numpy-only. `make` 4.3 available.

## What could NOT be completed here (honest status)
* **Docker is not installed in this sandbox** (`docker: command not found`). The pinned container
  (`Dockerfile`, python:3.11-slim, numpy 2.1.3) is therefore NOT BUILT and NOT RUN here. A Dockerfile that
  has not been built does not satisfy the container gate. CLEAN REPRODUCTION is **INCOMPLETE** pending a
  build+run on a host with Docker and a clean CI runner.
* **GitHub Actions** (`.github/workflows/nasi-ci.yml`) is CONFIGURED (freeze verify, regressions, low-SNR
  dev, determinism, cache-poison, figures, on py3.10 + py3.12, plus a container build+run job) but has NOT
  been executed in CI from this sandbox (no push performed; no runner).
* Clean-clone reproduction: the sandbox git index/refs are partially locked (see FINAL_REPORT); a genuine
  fresh `git clone` + `make reproduce-paper-all` on Tommy's machine or CI is the remaining step.

## To finish the gate (on a host with Docker)
```
git clone <repo> && cd <repo>
docker build -t nasi-repro .
docker run --rm nasi-repro make reproduce-paper-all      # expect CANON_SHA256 36b25c3e...
```
