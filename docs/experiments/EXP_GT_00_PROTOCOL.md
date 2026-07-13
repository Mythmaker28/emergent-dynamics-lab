# EXP-GT-00 — ground-truth metrology for dynamic identity (Game of Life)
**Preregistered. The observer is developed and frozen HERE, then evaluated on held-out circuits, and only then may
it be used on the droplet substrate (EXP-SC-01).**

## Why a metrology branch exists
EXP-SC-00B's snapshot R8-B failed. That could mean "no dynamic identity exists" or "my representation cannot see
it", and the droplet substrate cannot tell me which — there is no ground truth in it. So identity representations
are validated first on a system where **we possess the truth**.

## The system
Conway's Life (B3/S23), exact, dead borders. **Every component verified empirically — nothing canonical is trusted
unchecked** (`tests/test_life.py`):
- **glider / channel** — period-4 displacement exactly (+1, +1); moves at c/4 (one cell per FOUR steps)
- **eater (fishhook)** — absorbs a glider stream and is restored intact
- **inhibit gate / MEMORY BIT** — eater present ⇒ channel gated (output 0); absent ⇒ gliders flow (output 194)
- **tiny FSM** — k parallel gun→channel→gate units; **output = 194 × (open channels)**, exactly as the hidden causal
  model predicts

## The split
- **DISCOVERY OBSERVER**: receives **only raw cell-state trajectories**.
- **EVALUATOR**: retains component locations, the causal graph, memory contents, inputs, outputs and program
  identity. **Never shown to the observer.**

## The five challenge classes
(a) same architecture, different memory/program; (b) different architecture, same function; (c) **identical visible
output produced by different mechanisms** (programs 1010 / 0101 / 1100 all emit exactly 388 — free by construction);
(d) exact copies with reset history; (e) **progressive micro-component replacement under continuous function**.

**Validity is COUNTERFACTUAL, not visual**: a standardized probe glider is injected into each channel and the change
in output is recorded. A representation that merely *looks* similar cannot fake this.

## Decision
The observer is **fit for use** only if: (d) ≈ 0, (e) small, (a)/(b)/(c) large, and
**min(different-identity distance) / max(same-identity distance) > 1.0**.
**If it fails, it is NOT used on the droplet substrate.** EXP-SC-01 does not run until an observer passes here and
is then frozen and evaluated on held-out architectures, programs and layouts.
