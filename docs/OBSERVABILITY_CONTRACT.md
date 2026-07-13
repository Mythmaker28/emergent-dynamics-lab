# OBSERVABILITY_CONTRACT.md

**Status: BINDING.** Preregistered in EXP-GT-02 (D-051), extended by EXP-GT-A-CERT (D-055).

## What the observer receives

Every head receives **only**:

1. raw cell-state frames of a settled configuration;
2. the right to intervene — anywhere, at a time of its choosing — and to observe the consequences;
3. the system's **declared I/O interface** (here: the output line, a row index).

It never receives component labels or locations, the program word, gate identities, hidden graph edges, expected
outputs, or any evaluator quantity. No head imports from the evaluator. **Absolute position is never an identity:**
graphs are expressed in **ordinals and delays**.

## Two labels per case, not one

Every benchmark case carries **the relation** (SAME / DIFFERENT) **and whether that relation is identifiable at
all** from the supplied observations. Every head may output **INDETERMINATE**.

**Correct abstention is a PASS. Resolving a relation the data cannot support is fabrication, and is scored as a
FAILURE.** A head that cannot abstain cannot be trusted when it does not.

`A` abstains when: a **live** output has no discovered source (coverage insufficient); an intervention could not be
**proved clean** (see below); or nothing causal was discovered at all.

## Every intervention must be proved, not assumed

This is not boilerplate. It is the correction of a real confound that silently produced a fictitious causal graph.

**A destructive micro-ablation does not remove a component — it can REPLACE it.** A 5×5 tile cleared inside a
Gosper gun does not delete the gun; it mutilates it into a *different working machine* that emits a glider stream
down a new diagonal, arriving at output columns that carry nothing in the intact circuit (measured: 55–58, 95–98,
135–138). A causal graph inferred from such interventions is the graph of a system that never existed. The first
tomography did exactly this and produced 20 spurious "components" for a 4-component circuit, including edges in
which *deleting matter made an output rise*.

Therefore every intervention used as evidence must satisfy, **executably**:

- **EFFICACY** — it actually removed live matter. A silent no-op is not evidence of anything.
- **SPECIFICITY** — it is applied at the **scale of a discovered component**, not at an arbitrary tile.
- **NON-SHATTERING** — the world returns to an exactly periodic state afterwards. *And it is given time to do so*:
  freeing a suppressed stream refills the pipeline to the boundary, which takes longer than the observation
  window. Judging this too early flagged two perfectly clean ablations as confounded — **an abstention caused by
  the observer's own impatience is not honest uncertainty.**
- **NON-OVERLAP** — no two components' ablation boxes overlap, or ablating one mutilates the other.

An intervention that fails verification is marked **CONFOUNDED and excluded from the evidence.** It is not quietly
used anyway.

## Every estimator must be invariant to what it claims to ignore

A causal **delay** is a property of the path, not of when we happened to strike it. Ablating at *t*=0 destroys
whatever is in the box *at that phase*, so a naive "first frame the output changes" estimator swings by up to half
the inter-glider spacing — **measured: 214 vs 229 across a half-period shift.** That inflated the null tolerance to
15 steps and cost `A` its finest resolution.

The delay is therefore the **earliest onset over a full cycle of strike phases**. The measured null deviation then
drops to **zero**, and `A` resolves the finest edit the substrate admits (4 steps).

## Tolerances are derived, never chosen

Every threshold comes from a **development null distribution** and is declared **before** any held-out case is
evaluated. **No threshold is ever derived from, or adjusted on, a held-out case.**

A tolerance is compared **pairwise** (`|d₁ − d₂| ≤ tol`), never by quantizing into buckets: 214 and 229 differ by
15, but with `tol = 15` they fall in buckets 13 and 14 and a bucket-based head calls them DIFFERENT. **A boundary
between two buckets is not a tolerance** — two values within tolerance can still straddle it.

## Every ground-truth label must itself be auditable

The ban on tuning a head to pass a case is **not sufficient**. D-053: `A` was graded DIFFERENT on two circuits with
the *same causal graph*, and the prescribed fix was to sharpen `A` until it agreed. **The expected label must be
checkable, or the instrument will be tuned to reproduce a labelling error.**

Concretely, every circuit admitted to the benchmark must pass, executably:

- **VIABILITY** — every channel the architecture declares live actually carries a stream. *(A dead 4-channel circuit
  shipped as a "held-out architecture" from EXP-GT-00 to D-052 because nobody ever asserted that a declared circuit
  computes anything.)*
- **PERIODICITY** — the settled state is exactly periodic. *(Necessary but NOT sufficient: an empty grid is
  perfectly periodic. Viability and periodicity must BOTH hold.)*
- **GRAPH AGREEMENT** — the causal graph derived from **geometry** and the causal graph derived from
  **intervention** agree edge-for-edge. Two independent paths, no shared code. Disagreement rejects the circuit;
  it does not patch it. *(This check caught three real bugs during construction, including a component whose
  ablation box overlapped its neighbour's.)*

## Declared limits of the current probe

- **Component separation:** matter separated by ≤ 4 empty cells **merges** and cannot be resolved.
- **Program invariance of `A`: NOT CERTIFIABLE on this substrate.** The memory bit is implemented by *adding an
  eater*, so the program **is** part of the causal graph. Any "pass" here is a test that cannot fire. This requires
  a substrate with **state-based memory** (a latch or storage loop) — a required property of the next benchmark.
