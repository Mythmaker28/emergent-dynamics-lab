# Emergent Dynamics Lab

This private research repository tests a narrow, falsifiable question:

> Can local particle-dynamics laws produce mesoscopic organization that remains phenotypically continuous while its material constituents turn over, and that may later recover after a controlled perturbation?

The pipeline described below is the periodic two-dimensional particle-dynamics substrate (`CORE V0`). It is not the current line of work: decision D-021 (2026-07-10, `docs/DECISION_LOG.md`) retired Particle Dynamics for the persistent-individuality question, and later lines of work used other substrates. The project does **not** claim life, consciousness, autopoiesis, memory, or identity from visually interesting patterns.

## Current state

This README does not track the project state. Read [ROADMAP.md](ROADMAP.md), a dated snapshot of the records whose section 6 lists the lines of work by decision, and the durable state files that [AGENTS.md](AGENTS.md) lists. Known test failures and their causes are in [docs/TEST_STATUS.md](docs/TEST_STATUS.md).

## CORE V0 pipeline

- deterministic positions, velocities, types, asymmetric interactions, short-range repulsion, finite-range response, damping, and periodic boundaries;
- scalar O(N²) and independent vectorized force paths;
- periodic proximity-component entity detection;
- geometry/size lineage association with explicit birth, disappearance, split, merge, and ambiguity events;
- ID-independent phenotype descriptor `Phi` and phenotype continuity `P(tau)`;
- diagnostic-ID Jaccard material retention `M(tau)`;
- first-class ID-permutation, static-material-flux, and tracker/cadence controls;
- reproducible CLI experiments with manifests, raw/indexed tables, summaries, and audit figures.

`P` and `M` remain separate. There is no `theseus_score` or composite `memory_score`. The initial `P > 0.8, M < 0.5` quadrant is an exploratory probe, not an identity definition.

## Reproduce locally

Python 3.11 or later (`pyproject.toml`). The commands install `scipy==1.15.3`, the version pinned in `requirements-lock.txt`, because `pyproject.toml` did not declare SciPy as of 2026-10-30 (`ROADMAP.md` step H1); without it, the tests that need SciPy fail with `ModuleNotFoundError: No module named 'scipy'` (`docs/TEST_STATUS.md`).

POSIX shell:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]' 'scipy==1.15.3'
.venv/bin/python -m pytest -q
.venv/bin/python -m edlab.cli validate-forces
.venv/bin/python -m edlab.cli nulls
```

PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[dev]' 'scipy==1.15.3'
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m edlab.cli validate-forces
.\.venv\Scripts\python.exe -m edlab.cli nulls
```

Before autonomous work, read [AGENTS.md](AGENTS.md) and the durable state files it lists.

