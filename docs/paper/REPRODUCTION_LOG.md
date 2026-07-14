# CLEAN REPRODUCTION LOG (deliverables 9,10) — consolidation
## Verified in this environment
* `make reproduce-pc` deterministic: identical `PC_CANON_SHA256 17080664...` on two runs (content-addressed seeds).
* `make reproduce-nasi` deterministic: `36b25c3e...` (prior mission).
* Freeze verification PASS: `noise_aware/verify_freeze.py` and `point_cert/verify_pc_freeze.py` (NASI 3027044479 + point layer 8c1bf736 + generators intact).
* Cache-poisoning invariance PASS (`noise_aware/cache_poison_test.py`).
* All figures regenerate from raw artifacts (`make_figures.py`, `make_pc_figure.py`) with provenance manifests.
* Consolidated target `make reproduce-all` runs paper + NASI + PC pipelines.

## NOT completed here (honest)
* **Docker is not installed in this sandbox** (`docker: command not found`). The pinned container
  (`Dockerfile`) is NOT built and NOT run here. `docker build -t emergent-metrology-repro . && docker run
  --rm emergent-metrology-repro make reproduce-all` must be run on a host with Docker.
* GitHub Actions (`.github/workflows/nasi-ci.yml`, extended for PC) is configured but not executed from the
  sandbox (no push, no runner). Clean-clone reproduction pending a host.
* Therefore: `CLEAN REPRODUCTION: INCOMPLETE`. A Docker digest and CI run are the only remaining gate.
