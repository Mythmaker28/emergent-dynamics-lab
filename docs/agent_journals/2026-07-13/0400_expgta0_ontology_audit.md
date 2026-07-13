# EXP-GT-A0 — I was told to sharpen the ruler. The ruler was right. (2026-07-13)

**Role:** autonomous research agent. **Run:** EXP-GT-A0-20260713-001.
**Start Git:** `d260730` (D-052). **Scope:** Phase 0 of the general ground-truth emergence metrology mission —
correct the ontology of `A` **before** repairing its resolution.

## The instruction I did not follow

D-052 and `PROJECT_STATE.md` both say the next action is an **A RESOLUTION CERTIFICATE**: derive a finer tolerance
from the development null so that `A` can resolve the 5-column channel-gap difference it currently misses.

I did not do that, and the mission brief was right to forbid it. **The premise is false.**

## OBSERVED

Three architectures are declared in `exp_gt_00.py`:
`ARCH_TRAIN = (5,45,85,125)` (spacing 40), `ARCH_HELD_OUT = (5,50,95,140)` (spacing 45) and `(10,46,82,118)` (36).
EXP-GT-02B's "different ARCHITECTURE" case was sp40 vs sp45 (confirmed from `tomo.npz`: `arch2_1010` channels at
cols 67/80/157/171 = the sp45 layout).

I extracted **two** ground-truth graphs per circuit and compared them:

1. the **declared structural graph** from `build()`;
2. a **verified active-influence graph**, measured by privileged ablation of every gun and every gate, recording
   which channel outputs actually move and after how long.

| program | pair | declared edges identical | structurally isomorphic | verified-active isomorphic | delays equal |
|---|---|---|---|---|---|
| 1010 | sp40 vs sp45 | **yes** | yes | **yes** | **yes** (174,174,234,234) |
| 0101 | sp40 vs sp45 | **yes** | yes | **yes** | **yes** |
| 1111 | sp40 vs sp45 | **yes** | yes | **yes** | **yes** (234×4) |

Viability, all-open program, per-channel mean output:

| layout | spacing | per-channel output | verdict |
|---|---|---|---|
| (5,45,85,125) | 40 | 0.671 × 4 | VIABLE |
| (5,50,95,140) | 45 | 0.671 × 4 | VIABLE |
| **(10,46,82,118)** | **36** | **0.0 × 4** | **DEAD** |

Each gun works **alone** at each of those columns (0.671 each). Swept spacing 34→49: 34–37 BROKEN, ≥38 VIABLE.

`fast.step` proved bit-exact against `engine.step` on 480 adversarial comparisons including forced border cells.

## INFERRED

`build()` writes its edges over **channel ordinals** — `(gun_i → out_i)`, `(gun_i → gate_i → out_i)`. **The gun
columns never enter the causal graph.** So two layouts with the same program do not merely *happen* to be
isomorphic; they are **the same edge set**. `arch_id = "A" + "-".join(gun_cols)` is a **layout id wearing an
architecture's name**, and that string is the only thing that ever made these cases "different architectures".

The Gosper gun spans 36 columns. At spacing 36 the bounding boxes **touch**: gun *i*'s right block (rows 7–8,
cols gc+34..35) is diagonally adjacent to gun *i+1*'s left block (rows 9–10, cols gc+36..37). They destroy each
other. The failure is in the **layout**, not the component.

## HYPOTHESIS → tested → CONFIRMED

*If* the two "architectures" differ only in geometric embedding, *then* `A = SAME` is correct and the benchmark
label is wrong. Confirmed on all three programs, on both the declared and the measured graph, including delays.

## WHAT WOULD FALSIFY THIS?

Any of: a difference in the declared edge sets; a non-isomorphic verified active graph at equal program; unequal
causal delays; a cross-channel edge present in one layout and absent in the other. **None occurred** for sp40 vs
sp45. (The sp36 layout *does* show cross-channel edges and unequal delays — but that is because it is a wreck,
not an architecture: `gate2` ablation perturbs *all four* outputs and baseline outputs are debris.)

## DECISIONS

1. **`A = SAME` for sp40 vs sp45 is CORRECT.** Expected label corrected to **A = SAME, G = DIFFERENT**.
   The recorded "A failure" is reclassified **FAILED — ONTOLOGY** (benchmark-label error), **not** an
   observer-resolution failure. **The tolerance is untouched.**
2. **D-052's prescribed repair is WITHDRAWN.** Deriving a finer tolerance to make `A` report DIFFERENT on a
   5-column gap change would have tuned `A` into a **layout detector**. The instrument was right and the
   reference was wrong; sharpening the ruler would have broken it.
3. **`G` (geometric embedding) is introduced** as an auxiliary, never-composited diagnostic head, so that a real
   geometric difference has somewhere to live without being mistaken for an architectural one.
4. **`ARCH_HELD_OUT[1]` is VOID and quarantined.** A viability assertion is now mandatory for every circuit.
5. **EXP-GT-00's case (b) "PASS" is CORRECTED to a FAIL.** `d_diff_arch_same_program = 0.684` was *credit for a
   large distance between two systems with the same causal architecture*. Under the corrected label the criterion
   inverts. Observer v1's persistent-site transverse profile is layout-sensitive by construction — it was a **G**
   detector, never an **A** detector. The EXP-GT-00 artefacts are **preserved unchanged**; only the label moves.

## FAILURES / DEAD ENDS

The `Write` tool truncated a source file at 11,095 bytes mid-line on this mount; the module imported and *ran*
in its truncated state. Caught by `wc -c` + `ast.parse`. All code is now written through the shell and byte-count
verified. **A file that imports is not a file that is complete.**

## UNRESOLVED RISK — and it is the real blocker

**The benchmark has never contained one genuinely different causal architecture.** Every circuit in the family is
four independent parallel channels `gun_i → (gate_i) → out_i`. There is no topological variation anywhere: no edge
addition, no edge removal, no delay change, no redundancy, no feedback, no cross-channel coupling.

So `A` has **never been tested against a real architectural difference** — and a finer tolerance would have had
*nothing to resolve*. `A` cannot be certified until such architectures **exist**.

## HANDOFF — exact next authorized action

Build a **verified circuit library with genuine topological contrasts** (edge add/remove, delay change, redundant
two-path, feed-forward vs feedback, inert decoration, cross-channel coupling), where **each circuit's declared
graph is empirically verified against the dynamics by privileged knockout** and each layout passes the viability
assertion. Only then can EXP-GT-A-CERT derive a resolution — in **causal-graph space**, never in column-distance
space.
