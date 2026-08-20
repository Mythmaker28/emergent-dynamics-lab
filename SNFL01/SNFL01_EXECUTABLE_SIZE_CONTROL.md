# SNFL01 — EXECUTABLE SIZE CONTROL QUALIFICATION

**Result: `ELIGIBLE_SET_SIZE_CONTROL_NOT_EXECUTABLE`** — and, independently of that, the factor is
not separable from delivered material. No mutation oracle was run, because nothing imports.

## 1. The control exists, and it is exactly the right one

`P07/p07_core.py` (blob `9f457608…`, sha256 `4d06add2…`) defines it:

```
line 55  MASK_GATES = ("FROZEN", "COMOVING", "TRACKALL")
line 60  class Gate:
line 61      """A sink eligibility rule. `PARENT` reproduces DEV_05 exactly."""
line 64      def __init__(self, name, mask="FROZEN", track=True, thresh=True, spread="ORDERED"):
line 74  PARENT_GATE = Gate("PARENT")
```

`FROZEN` = the downstream half of `C256` frozen at `t256` (the DEV_05 parent rule) → `COMOVING` = the
downstream half of the **current** track `C_t` → `TRACKALL` = the **entire** current track. That is
precisely an eligible-set cardinality ladder, already written, already sealed, already used.

## 2. It cannot be executed

`p07_core.py` opens with

```python
from od_core import (THRESH, MMAX, comps, largest_bounded, cells_of, nbrs, fhash, advect,
                     LatticeBondState, LatticeBondEngine, graph_distance, AXES)
```

**`od_core.py` does not exist.** Not tracked, not untracked, not in any commit: zero occurrences
across all **12 615** objects of `git rev-list --all --objects`, and zero in
`git ls-files --others --exclude-standard`.

It is not a leaf dependency — it is the **root of the entire Route E operator stack**:

| module | imports `od_core` |
|---|---|
| `results/ROUTE_E_DYNAMIC_SOURCE_CAPTURE_04/dsc_core.py` | lines 23–25 |
| `P07/p07_core.py` | first import |
| `P08/p08_core.py` | line 53 |
| `P09/p09_run.py` | line 15 |

`P09/p09_run.py` also imports `morph02_ic`, which likewise has **0** occurrences.
(`bridge00_harness` does survive, at `results/ROUTE_E_CAUSAL_BRIDGE_00/bridge00_harness.py`.)

So the picture is precise, and it is not "the code is missing":

* the **engine** survives — `edlab/substrates/lattice_bond/engine.py`, blob `0980525690…`,
  27 439 bytes, byte-identical at `29923e8`, `99df745` and `b6bc514`;
* the **gate** survives as source text;
* the **analysis** layer survives *and runs* — `dr05_flux_decomposition.py` imports only
  `csv, json, math, statistics, pathlib`;
* the **glue** between engine and operator does not survive.

Every module capable of starting a scientific world fails on its first import line.

Section 3 is explicit: *"If no independent executable size control exists:
`ELIGIBLE_SET_SIZE_CONTROL_NOT_EXECUTABLE`. Do not implement one in this mission."* Writing
`od_core.py` would also move the executable path away from the one that produced every inherited
number, so nothing measured with it could be compared against the prior evidence at all.

## 3. Even with a runnable stack, the factor is not separable

The delivered quantity per event is

```
q_event = min(planned dose, sink capacity, source capacity)
```

where sink capacity is a sum over the eligible set. So `|E|` reaches the outcome **only through the
material it unlocks**: where the planned dose or the source binds, enlarging `|E|` changes nothing;
where `|E|` binds, enlarging it necessarily delivers more material. There is no operating point at
which cardinality moves and delivered mass does not.

This is measured, not argued. P07 07B, matched planned dose Q400, matched `t256` state, 18 blocks:

| gate | L | delivered / M256 | incumbent removed | efficiency | continuity |
|---|---|---|---|---|---|
| `PARENT` | 24 | 0.620 | 0.460 | **0.744** | 9/9 |
| `COMOVING` | 24 | 0.744 | 0.478 | 0.643 | 8/9 |
| `TRACKALL` | 24 | **3.865** | **0.298** | **0.075** | 8/9 |
| `PARENT` | 32 | 0.414 | 0.377 | **0.910** | 9/9 |
| `COMOVING` | 32 | 0.413 | 0.375 | 0.910 | 9/9 |
| `TRACKALL` | 32 | **3.835** | **0.261** | **0.067** | 8/9 |

Enlarging the eligible set to the whole component multiplies delivered mass by **6.2** and removes
**less** incumbent. Section 3's requirement — change `|E|` "without silently changing total dose …
material quantity" — cannot be met by this architecture. Independently of the missing module, this is
`ELIGIBLE_SET_SIZE_NOT_SEPARABLE_FROM_OTHER_PHYSICS`.

## 4. And the experiment has largely been run already

P07's 07B is a prospectively sealed, matched-dose, matched-state, 18-block execution of exactly the
enlargement this mission proposes. Its **sealed primary contrast failed**: `COMOVING` gains 20 % at
L=24 (8/9, p = 0.039) and is **strictly nil** at L=32 (0/9). P07's own words:

> Un masque co-mobile ne lève pas le plafond, parce que le puits n'était pas la borne active.

The ledger says why: at Q400 the **source** is the active bound in **87.0 %** (L=24) and **96.6 %**
(L=32) of executed events; the sink binds in 7.8 % and 0 %. P07's headline is *saturation conjuguée* —
releasing one side moves the constraint onto the other instead of lifting the ceiling.

What genuinely remains open is the enlarged mask **at Q800**, where 07A shows `CAP_PARENT = 0` and
`CAP_TRACKALL > 0` at **100 %** of the 4 036 rejections. That is a real gap — and it is unreachable,
because reaching it requires both the missing module and a factor that cannot be isolated.
