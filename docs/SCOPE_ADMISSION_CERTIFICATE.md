# SCOPE_ADMISSION_CERTIFICATE.md

**Status: QUALIFIED.** EXP-GT-ADMIT, run `results/EXP-GT-ADMIT-20260717-001`. **10/10, 0 failures.**
**Architecture head V4 is FROZEN and UNTOUCHED.** Admission is a *separate* controller.

**An A / S / F decision is INVALID unless admission returns `ADMITTED`.**

## Why it exists

D-060: V4 declares a component-separation limit of 4 cells and **never checks that the data respect it**. Handed an
E1 relief placed **one row** from a gun, it silently **merged** the two into one component and emitted a confident
`DIFFERENT`. *A confident verdict on a case the instrument cannot resolve is a fabricated certainty*, and the
observability contract forbids it.

## The hard part — why the obvious check cannot work

**You cannot detect an unresolved merge by looking.** Two components 2 cells apart merge into one blob, and no
amount of staring at that blob tells you it was two — *that is exactly what "below the resolution limit" means*. A
geometric check here is circular.

## So admission is CAUSAL, not geometric

> **A discovered component is ATOMIC iff no proper sub-part of it can be cleanly ablated to a *different* effect.**

- A genuine single component (a Gosper gun): every sub-fragment ablation either **mutilates** it (builds a new
  emitter) or reproduces the whole component's effect. No clean sub-part with a distinct causal role exists.
- A **merged blob** (gun + relief eater): the relief is a sub-fragment whose clean ablation *opens a channel the
  whole blob's ablation leaves dead*. The blob is **not atomic** → **OUT_OF_SCOPE**.

Effects are measured on the **raw output line**, never projected onto the discovered output nodes — because *the
merged blob hides the very output that would expose it*. My first version projected, and duly admitted the merged
case.

## Checks performed (observable and intervention-derived only; no hidden label is read)

| check | refusal |
|---|---|
| observation window spans ≥ 6 inferred clock periods | `OUT_OF_SCOPE` |
| the phase quotient's **group action is supported** — the strike schedule is the *full cycle*, not a sample | `OUT_OF_SCOPE` |
| baseline and intervention windows exactly matched | structural invariant |
| per-component **valid-strike coverage** ≥ 50% of the cycle | `INSUFFICIENT_COVERAGE` |
| no edge rests on a **single strike** (an anecdote, not a measurement) | `CONFOUNDED` |
| every live output validly sourced, every suppressed output validly inhibited | `INSUFFICIENT_COVERAGE` |
| **causal atomicity** of every discovered component | `OUT_OF_SCOPE` |

## Frozen must-pass / must-fail results

| case | verdict | expected |
|---|---|---|
| **separation BELOW the limit (relief 1 cell from a gun) — the case V4 answered confidently** | **OUT_OF_SCOPE** | ✅ |
| separation ABOVE the limit (4 empty cells clear) | ADMITTED | ✅ |
| plain 4-channel circuit | ADMITTED | ✅ |
| circuit with inert decoration | ADMITTED | ✅ |
| **plain circuit at strike phase 33** (a phase where the whole ablation is itself invalid) | ADMITTED | ✅ |
| **cross-inhibitor** (collision debris 1 cell apart at the annihilation site) | ADMITTED | ✅ |
| coverage-starved probe | INSUFFICIENT_COVERAGE | ✅ |
| biased / sampled phase schedule | OUT_OF_SCOPE | ✅ |
| valid-strike coverage 10 of 60 phases | INSUFFICIENT_COVERAGE | ✅ |
| an edge inferred from a single strike | CONFOUNDED | ✅ |

**Non-vacuity in both directions:** admission both **admits** and **refuses**, and all four refusal codes fire.
**Admission does not gag the head:** on admitted cases `A_TOPO` still returns SAME and DIFFERENT correctly.

## Three of my own bugs, caught by the certificate — and one of them nearly became a false scientific claim

1. **Effects projected onto discovered output nodes.** The merged blob hides the output that exposes it, so the
   projection showed nothing and the merged case was **ADMITTED**. Fixed: measure on the raw line.
2. **Atomicity judged at a single strike phase.** At the 6 phases where the whole-component ablation is *itself*
   invalid, `whole_effect` is `None` and every clean sub-fragment looks "distinct from nothing". Admission therefore
   refused **four ordinary phase-shift nulls** *and* **every cross-inhibitor circuit** — and I was one commit away
   from recording, as a scientific finding, that the crown case is out of scope. **It is not.** Atomicity is now
   judged only at phases where the whole ablation is valid, and a sub-part must be confirmed at a **majority** of
   them. **An admission controller that refuses valid cases is not conservative; it is broken.**
3. **A cache key that omitted the probe region**, so a coverage-starved probe silently returned the un-starved
   verdict. *A cache that can answer a question it was never asked is not a cache — it is a bug.*

## Audit of the D-060 prospective run

Applied post hoc to the frozen V4 answers on the third held-out split: **12/12 ADMITTED, 12/12 correct.**
**The prospective claim of D-060 stands, and is now known to be calibrated as well as right.**

## Certified limits

| | |
|---|---|
| component separation | **4 cells** |
| minimum valid-strike fraction | **0.5** of the cycle |
| minimum observed clock periods | **6** |
| minimum strikes per edge | **2** |
