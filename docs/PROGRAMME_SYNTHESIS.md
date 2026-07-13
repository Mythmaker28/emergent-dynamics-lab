# PROGRAMME SYNTHESIS — what is identifiable, what is not, and what keeps killing the observers

Required by §13 of EXP-GT-ACTIVE-CAUSAL-00. **Automatic construction of further observers stops here.**

Three observers have been built and retired under a one-development-cycle / one-prospective-run rule:

| | observer | development | prospective | classification |
|---|---|---|---|---|
| D-065 | conductor-bounded **module discovery** | 18/18 | **FAIL** — function 50 % on unseen impls, false certainty 6/24 | mistook a **representational boundary** for a causal interface |
| D-067 | **source-transducer** (sources, not taps; reachable manifold) | 20/20 | **FAIL** — 12/24 false abstentions | **temporal provenance**: negative index fabricated source histories |
| D-069 | **active experiment planner** (version space, provenance contract) | 15/15 + 20/20 | **FAIL** — transducer class 21/24 | **model minimality**: the version space widens and never narrows |

> ### The exact scope of the D-069 verdict
>
> **FAILED — IMPLEMENTATION / MODEL MINIMALITY**, with an independent evaluator ground-truth defect of mine.
> The observer is retired under its **full-hierarchy criterion**. The causal source-transducer **ontology is not
> falsified**, and neither is the observer's comprehension of the worlds:
>
> - **It predicted every measured function correctly** — every table agrees with privileged simulation, on every
>   row of every world, including four implementations it had never seen.
> - **It failed the preregistered minimal-representation criterion** on 3/24, because its search can *widen* a
>   history window but cannot *eliminate a redundant history variable*.
>
> It is **not fully qualified**. It did **not** fail to understand the prospective worlds. Both statements are
> required, and neither may be dropped.

---

## I. What is now ESTABLISHED as identifiable in this substrate

Each of these was measured prospectively, on implementations never seen during development, and survives the
retirement of the observer that demonstrated it.

**Causal structure.** The direct-edge graph is exactly recoverable by one-step pulses: flip a cell at step `t` and
nothing else differs at `t`, so whatever differs at `t+1` is a direct child and nothing else. Non-vacuous by
construction. *(All three observers; never once the failure point.)*

**Independent causal sources — 100 %, prospectively.** Boundary taps are **not** inputs. Traced to roots, three and
four taps collapse to two causes; a wire and its own buffer merge; two registers with **byte-identical baseline
series** stay distinct. Correlation is not dependence and synchronisation is not identity — only a dissociating
intervention decides.

**Causes that are invisible in the baseline.** The write-enable rail is constant 0 forever and is a genuine cause:
clamping it makes every register load. The privileged source set is therefore **program-dependent** (`{clk, reg}`
where the register holds 1; `{clk, we}` where it holds 0). A variable is causal if an admissible intervention on it
changes the downstream distribution — not if it looks active.

**The function on the reachable manifold — 100 %, prospectively.** Measured only on joint source histories the
world can actually generate, with every feature's provenance re-read and verified.

**The reachable manifold itself.** Two taps of one source separated by exactly one clock period cannot be
dissociated under any sustained regime: half that manifold is unproducible, and the observer correctly returns
`EQUIVALENCE_CLASS_ONLY` rather than a table. Conversely, two modules with **byte-identical free-running outputs**
*are* separable by clamping the source, and abstaining there would be false abstention.

**Hidden state, honestly.** A module that *contains* a register is not thereby a state machine (`reg_delay` has a
latch and a static interface). `FINITE_STATE` was claimed on exactly the two true state machines and nowhere else.

**Temporal provenance is a solved problem — and only because it is enforced.** Window sized to the widest
hypothesis *tested*; sampling from `max(margin, max_lag)`; a negative index **refused**, not wrapped. Result: at
lag 56 the observer performs exactly as at lag 17.

---

## II. What is NOT identifiable — facts about the world, not failures of a method

**Off-manifold behaviour.** Where the dynamics cannot produce a joint source history, no observer can learn the
function there. `lag8_and` and `lag8_or` are genuinely indistinguishable under sustained regimes. The correct
output is `EQUIVALENCE_CLASS_ONLY`, and it always will be.

**Minimal source sets are not unique.** `{clk, reg}` and `{clk, we}` can both d-separate the same output. This is
an equivalence class, not an ambiguity to be resolved.

**A redundant lag is invisible to a widening search.** If a structural lag exists but is functionally redundant on
the reachable manifold, then *both* the two-lag and the one-lag model are correct. Only a **minimality test** —
which no observer here performed — distinguishes them, and it is exactly a *narrowing* operation.

---

## III. The pattern across all three failures — this is the real finding

Every observer discovered the world correctly and then **misdescribed it**, and every time the misdescription came
from a structure I imposed and never questioned:

1. **D-065** — I defined a module's inputs as *the wires crossing a boundary I drew*. The world's causes do not
   respect my boundary.
2. **D-067** — I defined the usable window as *a constant chosen in advance*. The world's lags do not respect my
   constant.
3. **D-069** — I defined model selection as *a search that only grows*. The world's minimal explanation does not
   respect my direction of search.

In each case the observer's own consistency check **worked perfectly** and detected the contradiction — and then
attributed it to the world rather than to me. D-067 concluded twelve combinational gates were state machines. The
thing hiding state was an array index.

**And in two of the three, my evaluator was independently wrong**, in the same direction each time: I removed a
real cause (`we`), or hand-declared a function from the circuit I *intended* to build (`xor3`), because doing so
made the ground truth produce the number I expected. A scorer that is adjusted until it agrees with the answer I
anticipated is not a scorer. It is a mirror.

**Two standing rules, independent of any observer:**

- **A certificate must exercise every instance the world offers, not the most convenient one.** D-067's 20/20
  inspected channel 0 of three — the only channel where its defect could not fire.
- **An assertion must guard the side that can be wrong.** "Every row was generated" was true, and useless.

---

## IV. What a fourth observer would have to do — and why I am not building it

The minimality defect is a **one-line class of fix** (test each feature for redundancy on the covered manifold
before naming the class). That is precisely why the failure rule forbids it: three observers have now died of
defects that each looked like a one-line fix *after* the prospective run, and each time the patch would have
concealed a structural habit rather than removed it.

The honest next step is not a fourth observer of the same shape. It is to ask whether **model selection itself**
should be adversarial: two searches, one growing and one shrinking, required to meet — a differential check on the
*description*, not merely on the *measurement*. That is a design question, and per §13 it is where I stop and hand
back.

**EXP-SC-01 remains BLOCKED.** It has been blocked through three observers, and blocking it was right every time:
each one would have produced a confident, wrong description of an unknown world.
