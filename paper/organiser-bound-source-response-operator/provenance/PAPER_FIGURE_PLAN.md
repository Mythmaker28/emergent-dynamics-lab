# FIGURE PLAN (LRCPS01 §11)

4 main figures of a maximum of 6.

a figure exists only to carry a claim from the matrix; every panel is regenerated from a hashed source file by code/make_figures.py; no panel carries LOST or NOT_TESTED evidence

| ID | § | Claims | Panels | Schematic content |
|---|---|---|---|---|
| Fig1 | 2 | A1 | 2 | panel a is a schematic; the particle positions drawn in it are not measured data and the caption says so |
| Fig2 | 4 | A1, A2, A3 | 2 | none |
| Fig3 | 5 | B0, B1, B2, B3, B4, B5, B6, B7 | 4 | none |
| Fig4 | 6 | C1, B3 | 3 | none |

## Why each figure exists

### Fig1 — `fig1_model_and_event_order`

the reader cannot judge any later number without the event order and the exact definition of the reported radius

- a schematic lattice with the source cell and the reported radius
- the seven-substep event order read from the kinetics module

### Fig2 — `fig2_prospective_confirmation`

it is the paper's central result and its falsifier: the reader must see the frozen line, the margin, and every individual arm

- 28 individual arms against the frozen prediction and its margin
- the three pre-declared endpoints with their intervals against the margin

### Fig3 — `fig3_summary_rule_artefact`

the second result needs four things side by side: that the field agrees, that the record disagrees only under one summary rule, how far a dynamics-free surrogate gets, and where it stops

- profile difference at 15 radii, both conditions, arm counts stated
- the historical residual by lattice size under the two summary rules
- four summary cells under observation, surrogate and full construction
- within-arm dispersion under the same three accounts

### Fig4 — `fig4_mechanism_ablation`

an ablation claim is only readable as a picture of distances

- distance from the observation for four constructions
- the same constructions built up in physical order
- the two main effects and the interaction

## Figures dropped

- **Fig5 (planned)** — the lineage calibration surface. its evidence is LOST_DOCUMENTARY and was in any case adjudicated invalid.
- **Fig6 (planned)** — the route-arbitration atlas. same loss; nothing survives to regenerate it from.

## Regenerated artefacts

| Figure | PDF sha256 | source data sha256 |
|---|---|---|
| `fig1_model_and_event_order` | `46605f6249b459f9…` | `f2c6a98c2fc5ddac…` |
| `fig2_prospective_confirmation` | `59cbc67efbb9c341…` | `da49158fec81f9fa…` |
| `fig3_summary_rule_artefact` | `606096d5f97c428f…` | `bd1ce3aefb9768a8…` |
| `fig4_mechanism_ablation` | `b2ad0c41c2740b4c…` | `457f012283b2f606…` |
