# EXP-GT-02 — instrument repair: observability contract, coverage-certified probes, phase matching
**Preregistered and frozen BEFORE any result. Observer v2 (EXP-GT-01) and its failures are preserved unchanged.**
This is an **instrument-repair** experiment. It is **not** weight tuning: v2's S head never intersected the channel
tracks, and no distance function on a blind probe can be tuned into sight.

## 1. OBSERVABILITY CONTRACT (new, and binding on every head)
Every benchmark case carries **two** labels, not one:
- the **relation** (SAME / DIFFERENT), and
- whether that relation is **IDENTIFIABLE from the supplied observations**.

**Every head must be able to output SAME, DIFFERENT, or INDETERMINATE.**
**Correct abstention is a PASS.** A head that resolves a relation the data cannot support is **fabricating**, and is
scored as a **failure**, not as a lucky guess. In particular: **two exact copies with distinct hidden histories
produce literally identical trajectories; any head that reports a lineage DIFFERENCE there has fabricated it.**

## 2. S repair — coverage-certified blind causal probing
**The stride-20 grid was invalid**: the channel tracks at the probe row sit at columns `gun_col + 29`
(34, 74, 114, 154 for the development layout), and a stride-20 scan starting at 20 **never touches them**. The S head
was blind by construction, and scored 0.000 on circuits with different memory words.

**Replacement: an exhaustive stride-1 blind scan, with a coverage certificate, using two intervention types** — the
observer is given **no component labels, positions, program bits or causal graph**:
- **INJECTION probe** (upstream of the gates): a standardized glider pulse at every column. It is **absorbed** iff its
  diagonal meets a gate ⇒ the columns with **zero** output change mark the **GATED** channels.
- **DELETION probe** (downstream of the gates, upstream of the output): a blind 5x5 tile is cleared for 8 consecutive
  steps (≥ 2 glider periods, so no clock phase can hide) at every column. The output **drops** iff a live stream
  passes through ⇒ these columns mark the **OPEN** channels.
Union = the channel set (**A**); the open/gated labelling, ordered by transverse coordinate, = the memory word (**S**),
which is therefore **layout-invariant**.

**COVERAGE CERTIFICATION — required BEFORE any unknown program is read.** The probe must reconstruct **known** words:
`1010`, `0101`, `1111`, `0000`, and the **same word across a held-out layout**.
**MUST-FAIL controls:** identical words (same program, different layout; and a program compared with itself) must be
reported **SAME**. A probe that cannot read a known word is not permitted to read an unknown one.

## 3. A and F repair — phase matching, not distance tuning
**Never compare a transient post-handoff frame with a fresh initialization.** v2 did exactly that, which is why its A
and F heads were confounded.
- Every configuration is **re-settled** to a common, fully-established state before any fingerprint is taken.
- **F** is derived from a **frozen standardized input-output intervention suite over complete logical episodes** —
  whole clock periods, never partial ones.
- **A** is derived from **time-lagged causal influence structure**, made invariant to translation, layout, cyclic
  clock phase, and to microscopically different but functionally equivalent component implementations: responses are
  accumulated over a **complete inferred clock period** and expressed in the **intrinsic transverse frame**.

## 4. E1 and E2 evaluated SEPARATELY
- **E1** (function-preserving handoff — the hard Ship-of-Theseus case): must preserve **A, S, F, L** and change **M**.
  Evaluated with **both** the development and an **entirely held-out** replacement implementation.
- **E2** (damage-and-repair): **F may legitimately break** and later recover, while **L** is preserved.
  **E2 is NOT the Ship-of-Theseus equivalence case and is never used as one.**

## 5. Freezing and held-out evaluation
Representations, **probe schedules**, phase-invariance rules and **per-head criteria** are frozen on development
circuits. Evaluation is then on **held-out architectures, programs, spatial layouts, clock phases and replacement
implementations**.

**Every head is reported separately. There is no scalar composite — ever.**

**EXP-SC-01 remains BLOCKED until A, S and F pass their held-out criteria AND L demonstrates calibrated
SAME / DIFFERENT / INDETERMINATE behaviour** (including correct abstention on exact copies).
