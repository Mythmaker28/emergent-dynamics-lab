# Emergent Dynamics Lab

This private research repository tests a narrow, falsifiable question:

> Can local particle-dynamics laws produce mesoscopic organization that remains phenotypically continuous while its material constituents turn over, and that may later recover after a controlled perturbation?

The current substrate is periodic two-dimensional particle dynamics (`CORE V0`). The project does **not** claim life, consciousness, autopoiesis, memory, or identity from visually interesting patterns.

## Current pipeline

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

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[dev]'
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m edlab.cli validate-forces
.\.venv\Scripts\python.exe -m edlab.cli nulls
```

Before autonomous work, read [AGENTS.md](AGENTS.md) and the durable state files it lists.

