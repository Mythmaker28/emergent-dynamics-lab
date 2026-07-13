# ARCHITECTURE_RESOLUTION_CERTIFICATE.md

**Instrument:** `edlab/identity/blind_a.py` — blind interventional causal tomography.
**Experiment:** EXP-GT-A-CERT (`edlab/experiments/exp_gt_acert.py`), run `results/EXP-GT-ACERT-20260713-001`.
**Verdict: QUALIFIED — on development data.** *(Held-out evaluation is EXP-GT-03 and has not yet been run.
This certificate states what the instrument can resolve. It does not yet claim it generalizes.)*

## What `A` measures

`A` is the **causal architecture**: which components exist, which outputs each can influence, with what sign and
what delay. It is computed as a **graph** and compared as a **graph** — isomorphism-aware, layout-free,
translation-free. Output nodes enter only as **ordinals**; components only through their **edge sets**.

**`A` is never a distance in columns.** D-052 compared *channel-gap distances* against a tolerance of 6.0 and
graded two isomorphic graphs "different" because their guns sat 5 columns further apart. That is geometry. Geometry
lives in **`G`**, which is reported separately and never composited (D-053).

## The measured null — the noise floor

The tolerance is **derived from data, not chosen**. Eight development nulls, each of which changes the *picture*
and none of which changes the *graph*:

| null | A | G | delays |
|---|---|---|---|
| clock phase +15 / +30 / +45 | SAME | SAME | 214 × 4 |
| translation +10 / +20 columns | SAME | SAME | 214 × 4 |
| channel spacing 40 → 45 | SAME | **DIFFERENT** | 214 × 4 |
| inert decoration (3 still lifes off-track) | SAME | SAME | 214 × 4 |
| decoy eaters (gate density and appearance, off-track) | SAME | SAME | 214 × 4 |

**Maximum delay deviation across all eight nulls: 0 steps.** → **DERIVED DELAY TOLERANCE = 0.**
**false-DIFFERENT rate: 0/8.**

That zero is *earned*, not assumed: with a naive "first frame the output changes" delay estimator the deviation was
**15 steps** (214 vs 229 under a half-period phase shift). The estimator now takes the **earliest onset over a full
cycle of strike phases** — a causal delay is a property of the path, not of when we happened to strike it.

## Certified resolution

| capability | certified value |
|---|---|
| **smallest detectable delay edit** | **4 steps** — the finest the substrate admits (a gun moved by (1,1) keeps its diagonal and output column, and arrives exactly 4 steps earlier) |
| **smallest detectable edge edit** | **one edge** (a cross-stream inhibitor: adds `gunSW → out`, plus one *emergent* shielding edge) |
| **smallest detectable node edit** | **one node** (a fifth channel) |
| **redundancy change** | **detected** (one path vs two paths into a single output node) |
| **component separation limit** | **4 cells** — matter closer than this merges and cannot be resolved |

**false-SAME rate: 0/8** across delay edits (k = 1, 2, 4, 8), edge addition, node addition, redundancy change, and
the same-function/different-mechanism case.

## The case that matters most

**Same function, different mechanism.** A channel closed by a **memory gate** (an eater) and the same channel
closed by a **cross-stream inhibitor** produce a **frame-for-frame identical output series** (mean 1.9967, |FFT|
distance 0.000000). `F` cannot separate them, and no observer of behaviour alone ever could.

**`A` = DIFFERENT.** The blind head recovers both graphs correctly — including an **emergent shielding edge**
(`gun3 → out2`) that the hand-written wiring diagram did not contain: the inhibitor stream is *consumed* by channel
3, shielding channel 2 behind it, so ablating channel 3's gun frees the stream and kills channel 2.

## Abstention fires

Starved of coverage (components discoverable only in columns 0–100), two live outputs have no discoverable source.
`A` returns **INDETERMINATE** — not SAME. An output that is demonstrably live and whose cause was never found is
**missing evidence, not evidence of sameness.**

**All three verdicts — SAME, DIFFERENT, INDETERMINATE — have fired correctly on known cases.** A criterion that
cannot both fire and fail is not a criterion.

## NOT certified — stated, not hidden

1. **Program invariance of `A`. NOT CONSTRUCTIBLE on this substrate.** A memory bit of 0 is implemented by *adding
   an eater*, so setting a bit adds a node and two edges: **the program IS the architecture.** "Same architecture,
   different program" cannot be built here, and any head that "passes" program-invariance in this family passes a
   test that **cannot fire**. EXP-GT-02B's A head passed it by comparing channel *positions*, which no program can
   move — **that pass is hereby marked VACUOUS.** Certifying this requires a substrate whose memory is a **state of
   fixed wiring** (a latch or storage loop). **Required property of the next benchmark.**

2. **Component separation ≤ 4 cells.** Below this, proximity cannot separate two components from one component's
   own internal fragments.

3. **Redundancy with identical `F`.** Not realizable in this component library without a glider reflector; the
   redundant path doubles the stream rate. Disclosed, not faked.

4. **Held-out generalization. NOT YET TESTED.** This certificate is granted on development data. EXP-GT-03 must
   freeze every head and evaluate on entirely unseen architectures, programs, layouts and implementations.
   **EXP-SC-01 remains BLOCKED.**
