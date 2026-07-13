# EXP-GT-ACTIVE-P — the single prospective run. **VERDICT: FAIL → RETIRED (D-069).**

Frozen observer (`ACTIVE_OBSERVER_FREEZE_MANIFEST.json`, `active.py` sha256 `23c670fb…`), fresh split generated
after the freeze, each world observed **once**. Development was 15/15 across all three channels; the temporal
provenance certificate was 20/20.

## The split

Eight worlds jointly holding out topology, layout, program, phase, implementation, **channel distance** (every
world scored on all three channels), source duplication, delay asymmetry, context schedule and the combination of
transducer classes. Four implementations — `or3`, `xor3`, `fsm_gate`, `lag8_dm` — never used or inspected during
development. Zero-leakage assertions passed; all eight worlds passed `assert_qualified` before the observer ran.

## Results — 24 transducers (95 % Wilson intervals)

| metric | all | unseen impls |
|---|---|---|
| region found | 100.0 % [86.2, 100] | 100.0 % |
| independent-source **count** correct | **100.0 %** [86.2, 100] | 100.0 % |
| source **identities** exact (vs privileged audit) | **100.0 %** [86.2, 100] | 100.0 % |
| **function on the reachable manifold** (vs privileged simulation) | **100.0 %** (15/15 tables) | 100.0 % |
| **transducer CLASS correct** | **87.5 %** [69.0, 95.7] | 83.3 % |
| fabricated provenance rows | **0** | 0 |
| rows excluded for missing history | **0** | 0 |

**By channel — that is, by distance from the clock:**

```
channel 0   max lag 25   class correct 7/8   rows excluded 0
channel 1   max lag 41   class correct 7/8   rows excluded 0
channel 2   max lag 56   class correct 7/8   rows excluded 0
```

**The D-067 defect is definitively gone.** No degradation with source distance. At lag 56 the observer performs
exactly as at lag 17. The previous observer, at lag 47, declared the module a state machine.

**Hidden state was claimed on exactly the two true state machines** (`fsm_gate` unseen, `toggle`) and **nowhere
else** — 6/6, with no table emitted. The partial manifold (`lag8_dm`, unseen) was reported as
`EQUIVALENCE_CLASS_ONLY` at coverage 0.5 on all three channels.

Cost: **75 / 90 episodes (83 %)** against an exhaustive schedule; development was 49 %.

## Why it fails

**Transducer class: 21/24.** All three failures are `xor3`, on all three channels.

`xor3`'s output gate reads its two inputs at **different depths**, so the structural function carries **two** clock
lags. The observer measured both — correctly — and built a three-feature model. Its table **agrees with the
privileged simulation on every row**: the function is right, the sources are right, the coverage is right.

But the second lag is **functionally redundant**: on the reachable manifold the output is exactly
`XOR(clk(t−3), reg)`. The minimal model is `DELAYED_STATIC` with one lag. The observer reported
`FINITE_HISTORY(0)` with two.

> The version space **only ever widens.** When a lag window is contradicted, the observer escalates to a longer
> history. It never asks the opposite question — **is this lag necessary?** — and so it returns a correct model
> with too many arguments, and derives the wrong class from it.

§7 requires *"the smallest predictive representation"*. This observer does not search for it. It searches only
upward. That is a failure of a primary bar (`correct transducer class`), and the rule is absolute.

## An error of mine, recorded because it is the third of its kind

`TRUE["xor3"]` was a lambda I **hand-declared from the circuit I intended to build**, not from the circuit I built.
§2 required a second, intervention-derived path for every claimed function, and I built it only for the sources.
Under my own contract that world should have been **rejected before the observer ran**.

Scored against the correct privileged path, the observer's function accuracy is **100 %**. My defective scorer had
flagged the right rows for the wrong reason: I said the function was wrong; in fact the **class** was.

This does not rescue the design — the class bar fails on the correct ground truth too — but it must be on the
record. Three observers have now been retired, and in **two** of the three my own scorer was independently wrong.

## Verdict and classification (mission §13)

**RETIRED.** Preserved unchanged. Not patched. No second cycle.

- **TRANSDUCER INFERENCE — model minimality.** The version space widens and never narrows.
- **Not** source discovery (100 %), **not** manifold identification (0 fabricated rows, correct coverage, correct
  abstention), **not** temporal provenance (0 excluded rows, no degradation with distance), **not** scope
  calibration (balanced across every channel and lag band).
- Contributing, and mine: the ground-truth **function** path was never built, in violation of §2.

**EXP-SC-01 remains BLOCKED. Automatic construction of further observers STOPS here**, per §13. The programme-level
synthesis of what is and is not identifiable is in `PROGRAMME_SYNTHESIS.md`.
