# FACTOR_HEADS_SPEC.md

Six heads. **Reported separately. Never composited.** A scalar identity score is what failed in D-048; it is banned
project-wide, and `edlab/identity/gates.py` enforces the ban.

Each head returns **SAME / DIFFERENT / INDETERMINATE**. **Correct abstention is a PASS. Fabricated certainty is a
FAILURE.**

| head | question | measured by | invariant to | sensitive to |
|---|---|---|---|---|
| **A** | causal architecture | blind interventional tomography: discover components from the raw trajectory (stationary matter, occupancy ≥ 0.25 over one period), ablate each **whole component**, prove the ablation clean, classify by effect (PERSISTENT_DOWN = source, PERSISTENT_UP = inhibitor, TRANSIENT = wire, NONE = inert), compare as a **graph** | translation, layout, spacing, clock phase, decoration, decoys | nodes, edges, signs, **delays** (tolerance 0, derived from the dev null) |
| **S** | program / memory word | the **certified** stride-1 injection/deletion probe (D-051), **preserved exactly** | layout, phase, material | the memory word |
| **F** | functional I/O relation | **per-output-node** \|FFT\| magnitude over 2 exact grid periods | mechanism, layout, cyclic phase (by construction, not alignment) | the I/O transfer relation |
| **L** | lineage | continuity of the observed causal run | — | observed branch/merge; **INDETERMINATE on observationally identical data** |
| **M** | material continuity | Jaccard of the *stationary* (constituting) matter | flowing matter | which cells carry the machine |
| **G** | geometric embedding | output-node **spacings** (translation-invariant) | translation | layout. **G is NOT identity. Auxiliary. Never composited.** |

## Design decisions that are not free parameters

**`F` is read per output node, not on the total line.** A delay edit shifts one channel in time, changing the
*superposition* on the total line while leaving every channel's own behaviour identical. Read on the total line, `F`
would move on a pure delay edit — and `F` would then be reporting an **architectural** change, which is `A`'s job.

**`A` is read off the graph, never off a distance in columns.** D-052 compared channel-gap distances against a
tolerance of 6.0 and graded two *isomorphic* graphs "different" because their guns sat 5 columns further apart.
Geometry lives in `G`.

**`A` delays are compared pairwise against a tolerance, never bucketed.** 214 and 229 differ by exactly 15; with a
tolerance of 15 and floor-quantization they land in buckets 13 and 14 and read DIFFERENT. **A bucket boundary is not
a tolerance.**

**`M` is *supposed* to be able to differ while A, S, F and L stay SAME.** That combination **is** the Ship of
Theseus. A scalar observer had no way to say it, and said "different individual" instead (D-048).

## Known defects (EXP-GT-03, held-out — NOT repaired)

1. **`A` is not phase-invariant on unseen phases.** The delay estimator strikes at phases (0, 15, 30, 45); the
   development phase-null used **the same four phases**, so it could not fire. On held-out phases every delay moves
   214 → 222.
2. **`A` over-abstains.** It returns INDETERMINATE when *any* intervention is confounded, though the contract says a
   confounded intervention is merely *excluded from the evidence*, and coverage may still be complete.
