# SNFL01 — FINAL REPORT

**SIZE-NORMALIZED-FLUX-LIMIT-01** · Owner: Tommy Lepesteur · 2026-08-20
**FINAL_DISPOSITION = `ELIGIBLE_SET_SIZE_CONTROL_NOT_EXECUTABLE`**
Primary starts **0 / 128** · reserve **0 / 4** · commits **1 / 5** · reviews **0 / 1**

---

## 1. Summary

The entry gate passed. All six §2 requirements are byte-verifiable, and every inherited number was
**recomputed from raw rows** rather than copied from a report. The mission then stopped at §3, for a
reason that is not a technicality: **`od_core.py`, the root module of the entire Route E operator
stack, does not exist in this repository** — 0 occurrences across all 12 615 objects and 0 among
untracked files. `dsc_core.py`, `p07_core.py`, `p08_core.py` and `p09_run.py` all fail on their first
import line. The engine survives; the gate survives as source; the analysis layer survives and runs;
the glue between engine and operator is gone.

Three further findings, each from the parent's own bytes, change what the mission was asking:

* **there is no established plateau** — DEV_06's commit records `PLATEAU_ESTABLISHED = false`;
* **`0.385` and `0.419` are two lattice sizes, not two contexts**, and the first rests on **two
  surviving worlds of nine**;
* **the experiment has largely been run** — P07 07B is a sealed, matched-dose, 18-block eligible-set
  enlargement whose primary contrast **failed**.

Zero worlds were constructed. Nothing was reimplemented.

## 2. The parent, bound by hash

Scientific parent `dev/route-e-p09-dose-yoked-closure` @ `b6bc514126ffd559407065eb89c07b4e950958ce`,
a descendant of DEV_06 (`8e619e6`) and P07 (`99df745`), both verified with
`git merge-base --is-ancestor`. The FTCTR01/EBR02 tip `8239fa7a` is documentary and was not used.

| bound object | blob | sha256 |
|---|---|---|
| `edlab/substrates/lattice_bond/engine.py` | `0980525690…` | `e027a9c5…` |
| `P07/p07_core.py` | `9f457608…` | `4d06add2…` |
| `direct_replacement_protocol.json` | `40a158de…` | `85d37725…` |
| `direct_replacement_summary.json` | `e6892353…` | `4e2026f4…` |
| `dr05_paired_flux_rows.csv` | `1aec668f…` | `4a2396f1…` |
| `dr05_flux_decomposition.py` | `1c9e1e29…` | `d7fbe914…` |

**Entry gate §2: 6/6 pass.** `STOP__SIZE_NORMALIZED_FLUX_PARENT_EVIDENCE_INCOMPLETE` does not apply.

## 3. What the inherited numbers actually are

Recomputed by this mission directly from `dr05_paired_flux_rows.csv`:

| | L = 24 | L = 32 |
|---|---|---|
| `I/I0` at Q100 (×1) | 0.593736 · n = 9 | 0.660552 · n = 9 |
| `I/I0` at Q800 (×8) | **0.385416 · n = 2** | **0.418707 · n = 9** |
| blocks lost at Q800 | **7 of 9** `TREATED_TRACK_LOST` | 0 of 9 |

The L=24 median is `median([0.3682, 0.4027])`. The `SOURCE_ONLY_Q800` arm at L=24 lost **9 of 9**.
Of 126 paired rows, 110 are `OK` and 16 are `TREATED_TRACK_LOST`.

The target is a **joint** endpoint: `FORCED_COMPONENT_TURNOVER_80 = ["I/I0 <= 0.20", "I/T <= 0.20"]` —
both must cross.

**Denominator audit (0 runs).** For each of the 18 `(size, block)` pairs, `I0` was compared across all
seven arms: **0 of 18 divergent**. `I0_CONSISTENCY = PASS`.

## 4. Why the control cannot be exercised

`P07/p07_core.py` defines exactly the right control — `MASK_GATES = ("FROZEN","COMOVING","TRACKALL")`
at line 55, `class Gate` at line 60, `PARENT_GATE = Gate("PARENT")` at line 74, whose docstring reads
*"A sink eligibility rule. `PARENT` reproduces DEV_05 exactly."* `FROZEN → COMOVING → TRACKALL` is an
eligible-set cardinality ladder, already written and already sealed.

It opens with `from od_core import (THRESH, MMAX, comps, …, LatticeBondEngine, …)`, and `od_core.py`
is absent everywhere. It is the root of the stack, not a leaf: `dsc_core.py` (lines 23–25),
`p07_core.py`, `p08_core.py` (line 53) and `p09_run.py` (line 15) all import it. `morph02_ic`, also
imported by `p09_run.py`, is likewise absent.

§3 is explicit — *"Do not implement one in this mission."* Writing `od_core.py` would also move the
executable path away from the one that produced every inherited number, so nothing measured with it
could be compared to the prior evidence.

## 5. And the factor is not separable anyway

`q_event = min(planned dose, sink capacity, source capacity)`, where sink capacity is a sum over the
eligible set. `|E|` therefore reaches the outcome **only through the material it unlocks**: where the
planned dose or the source binds, enlarging `|E|` changes nothing; where `|E|` binds, enlarging it
necessarily delivers more. There is no operating point at which cardinality moves and delivered mass
does not.

Measured, at matched planned dose Q400 and matched `t256` state, 18 blocks (P07 07B):

| gate | L | delivered / M256 | incumbent removed | efficiency |
|---|---|---|---|---|
| `PARENT` | 24 | 0.620 | 0.460 | 0.744 |
| `TRACKALL` | 24 | **3.865** | **0.298** | **0.075** |
| `PARENT` | 32 | 0.414 | 0.377 | 0.910 |
| `TRACKALL` | 32 | **3.835** | **0.261** | **0.067** |

Enlarging the eligible set to the whole component multiplies delivered mass by **6.2** and removes
**less** incumbent. §1's requirement to hold dose fixed and §3's mutation oracle cannot both be met.

## 6. The experiment was largely performed in 2026-08

P07 07B released the gates one at a time at matched dose. Its **sealed** primary contrast **failed**:
`COMOVING` gains 20 % at L=24 (8/9, p = 0.039) and is **strictly nil** at L=32 (0/9). P07's own
sentence: *"Un masque co-mobile ne lève pas le plafond, parce que le puits n'était pas la borne
active."*

The ledger says why. At Q400 the **source** is the active bound in **87.0 %** (L=24) and **96.6 %**
(L=32) of executed events; the sink in 7.8 % and 0 %. P07's headline is *saturation conjuguée* —
release one side and the constraint moves to the other rather than the ceiling lifting.

What genuinely remains open is the enlarged mask **at Q800**, where 07A records `CAP_PARENT = 0` while
`CAP_TRACKALL > 0` at **100 %** of 4 036 rejections. That gap is real — and unreachable, needing both
the missing module and a factor that cannot be isolated.

## 7. Disposition

```
FINAL_DISPOSITION = ELIGIBLE_SET_SIZE_CONTROL_NOT_EXECUTABLE
```

No freeze was written. A freeze binds an executable path, and there is none to bind; producing a
methods manifest, a seed manifest and a pre-run durability capsule for runs that cannot occur would be
paperwork mistaken for provenance. No adversarial review was run: §16 places it *after* a candidate
result, and there is no result to attack.

## 8. Next action

`HANDOFF_LATTICE_BOND_BOTTLENECK_ARBITRATION_01.md` — **zero engine runs**, on artefacts that survive.
P07's per-event ledgers (`p07a_event_ledger.csv.gz`, `p07b_event_ledger.csv.gz`) and DEV_06's
timecourse and risk-set CSVs are intact, and the analysis layer imports only the standard library.
DEV_06 and P08 §1 both produced substantive results from exactly this material with 0 engine calls.

It asks four things the surviving bytes can settle: the eligible-set **cardinality distribution** that
has never been published (SNFL01 §5 needed it and could not get it); the **active-bound decomposition**
across the full dose range; whether the L=24 ×8 condition is a saturation or a **mortality** (7/9 lost,
failures at compositions indistinguishable from the survivors, already flagged by DEV_06 as a
connectivity event); and an **arbitration** of the remaining limiters against P08's law
`Φ(s) = min(q/s, ρ)`.

If that shows the shortfall is dominated by source saturation and connectivity breakage rather than by
eligible-set cardinality, the SNFL01 question is answered in the negative from surviving evidence and
Route E's throughput line closes on a mechanism rather than an unresolved plateau — at zero cost.
