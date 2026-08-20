# SNFL01 — PARENT BINDING

**Scientific parent:** `dev/route-e-p09-dose-yoked-closure` @ `b6bc514126ffd559407065eb89c07b4e950958ce`
— a descendant of both `8e619e6` (DEV_06, which declared `SIZE_NORMALIZED_FLUX_LIMIT`) and `99df745`
(P07, which defines the eligible-set size control), carrying `P07`, `P08`, `P09` and `results/`
together. Ancestry verified with `git merge-base --is-ancestor` in both cases.

The FTCTR01/EBR01/EBR02 tip `8239fa7a` was **not** used as the parent: it is documentary.

## The three programmes that actually hold the evidence

| what | programme | commit |
|---|---|---|
| the mechanism `SIZE_NORMALIZED_FLUX_LIMIT` | `ROUTE_E_DIRECT_EXCHANGE_FLUX_DECOMPOSITION_06` | `8e619e61…` |
| the ×8 dose numbers and the 0.20 target | `ROUTE_E_DIRECT_INTERFACE_REPLACEMENT_FRONTIER_05` | `29923e89…` |
| the eligible-set **size control** | `ROUTE_E_EXCHANGE_THROUGHPUT_CAUSAL_PROGRAM_07` | `99df7453…` |

## Entry gate (§2) — all six pass

| requirement | result | binding |
|---|---|---|
| `LATTICE_BOND_ENGINE_PRESENT` | **true** | `edlab/substrates/lattice_bond/engine.py`, blob `0980525690…`, sha256 `e027a9c5…`, 27 439 B, identical at `29923e8`, `99df745`, `b6bc514` |
| `PRIOR_X8_CONDITION_PRESENT` | **true** | arm `DIRECT_Q800_UNIFORM` in `direct_replacement_summary.json` (sha256 `4e2026f4…`) and `dr05_paired_flux_rows.csv` (sha256 `4a2396f1…`) |
| `NORMALIZED_FLUX_ESTIMATOR_PRESENT` | **true** | `dr05_flux_decomposition.py:107` `I_over_I0_treated = It / I0`; stdlib-only imports |
| `ELIGIBLE_SET_DEFINITION_PRESENT` | **true** | `P07/REPORT_P07.md §1`: `i ∈ MASK ∧ i ∈ TRACK ∧ m[i] ≥ THRESH`, third conjunct proved dead code |
| `TARGET_0_20_PROVENANCE_PRESENT` | **true** | `direct_replacement_protocol.json` `/endpoints/FORCED_COMPONENT_TURNOVER_80 = ["I/I0 <= 0.20","I/T <= 0.20"]` |
| `PRIOR_INDEPENDENT_UNIT_IDENTIFIED` | **true** | same protocol: `"n = 9 independent blocks per size, one LawSpec"` |

**The mission was not stopped at §2.** `STOP__SIZE_NORMALIZED_FLUX_PARENT_EVIDENCE_INCOMPLETE` does
not apply: the evidence is complete, byte-verified, and independently recomputed.

## Where it stops instead

At §3. `P07/p07_core.py` — the file that defines the size control — begins
`from od_core import (THRESH, MMAX, comps, …, LatticeBondEngine, …)`, and **`od_core.py` exists
nowhere in this repository**: 0 occurrences across all 12 615 objects and 0 among untracked files.
It is the root module of the whole Route E operator stack (`dsc_core.py`, `p07_core.py`,
`p08_core.py`, `p09_run.py` all import it). Details and the separability finding:
`SNFL01_EXECUTABLE_SIZE_CONTROL.md`.

## Two corrections to the mission's premise, both from the parent's own bytes

1. **There is no established plateau.** DEV_06's commit message states verbatim:
   *"at L=24 the range is not insufficient, it is BOUNDED BY BREAKAGE between Q400 and Q800.
   `PLATEAU_ESTABLISHED = false`."*
2. **`0.385` and `0.419` are two lattice sizes, not two contexts** — and the first is
   survivor-conditioned: at L=24/Q800, **7 of 9 blocks are `TREATED_TRACK_LOST`**, so the median
   `0.385416` rests on **two** worlds (`[0.3682, 0.4027]`). At L=32/Q800 all nine survive
   (`0.418707`). Recomputed by this mission directly from `dr05_paired_flux_rows.csv`.

```
DISPOSITION = ELIGIBLE_SET_SIZE_CONTROL_NOT_EXECUTABLE
```
