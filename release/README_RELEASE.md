# IsingV3 — organizational memory in a simulated droplet (release candidate)

**Status: RELEASE CANDIDATE — prepared, not published.** No push, tag, DOI, or upload has been performed.

## What this is
A prospective, kill-switched falsification ladder testing whether an engineered internal memory field is a
causal, transplantable, turnover-surviving organizational memory in a simulated reaction-transport droplet.

**Headline results (see the manuscript and `reproduction/`):**
- **h1** (global cumulative-dose coordinate): decodable, causally necessary, and **retained through deep
  material turnover** — the load-bearing result (CERTIFIED: held-out R² lower bound ≫ 0.50).
- **h2** (temporal-order coordinate): stored, but deep-turnover retention is **not established** (CI spans the
  0.50 threshold); the mechanism of non-persistence is indeterminate. Nothing is claimed as falsified.

## Reproduce the primary result (one command)
```
python -m pip install -r requirements-lock.txt
python -m reproduction.primary            # writes reproduction/outputs/ + prints the certification
python -m reproduction.primary --check    # additionally asserts values within tolerance of EXPECTED.json
```
Runs in ~20–30 s on 2 vCPU. Reads only committed data (`results/observer/tca_holdout_raw.pkl`); exits
non-zero with a clear message if a dependency or data file is missing. See `release/ENVIRONMENT.md`.

## Where to start (a reader arriving at the repo)
1. `docs/paper/full/ORGANIZATIONAL_MEMORY_FULL_MANUSCRIPT_V3.pdf` — the manuscript.
2. `docs/paper/full/SUPPLEMENT_V3.pdf` — full model spec and provenance.
3. `reproduction/` — one-command deterministic reproduction of the primary certification.
4. `release/data/` — portable CSV/NPZ/JSON exports (`DATA_SCHEMA.md`), no unpickling required.
5. `release/CLEANROOM_REPRODUCTION_REPORT.md` — independent-environment reproduction result and the
   reproducibility caveat (reproduced point estimates vs. the manuscript's inline values).

## Licensing
- Code: Apache-2.0 (`LICENSE-CODE`).
- Data, figures, tables, manuscript text: CC-BY-4.0 (`LICENSE-DATA-TEXT`).
- Cite via `CITATION.cff`.

## Honest caveats
- Author/affiliation/funding are placeholders pending the corresponding author.
- The exact published point estimates (h1 deep 0.98, h2 deep 0.34) were produced by an inline analysis that
  was not committed; the committed-data reproduction yields the same **conclusions** with slightly different
  point estimates (h1 deep ≈ 0.89, CERTIFIED; h2 deep ≈ −0.24, not established). See the cleanroom report.
- Single simulated model; no external/human replication yet.
