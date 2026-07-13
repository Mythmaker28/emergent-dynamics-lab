# EXP-GT-SOURCE-P — the single prospective run. **VERDICT: FAIL → RETIRED (D-067).**

Frozen observer (`SOURCE_TRANSDUCER_FREEZE_MANIFEST.json`, `sources.py` sha256 `a1606c96…`), fresh split generated
after the freeze, each world observed **once**. Development certificate was 20/20. **No composite score.**

## The split

Eight worlds, jointly holding out **topology** (no triple used in development or in any burned split),
**layout**, **phase** (development ran entirely at `clk_phase = 0`; all eight are non-zero), **program**,
**implementation**, **delay asymmetry**, **source-duplication pattern**, and **intervention/context schedule**.
Four implementations — `tri_tap`, `sync3`, `edge_xor`, `reg_delay` — were never used or inspected during
development. Zero-leakage assertions passed; all eight worlds passed `assert_qualified` before the observer ran.

## Results — 24 transducers (95% Wilson intervals)

| metric | all | unseen impls | seen impls |
|---|---|---|---|
| region found | 100.0 % [86.2, 100] | 100.0 % | 100.0 % |
| independent-source **count** correct | 95.8 % [79.8, 99.3] | 94.4 % | 100.0 % |
| source **identities** exact | 62.5 % [42.7, 78.8] | 61.1 % | 66.7 % |
| source-duplication (lag count) correct | 75.0 % [55.1, 88.0] | 66.7 % | 100.0 % |
| **transducer class correct** | **50.0 %** [31.4, 68.6] | 55.6 % | 33.3 % |
| **reachable-manifold classification** | **50.0 %** | 55.6 % | 33.3 % |
| **function on the reachable manifold** | **29.2 %** [14.9, 49.2] | 33.3 % | 16.7 % |
| two independent ground-truth paths agree | 50.0 % | 55.6 % | 33.3 % |

**FALSE ABSTENTION: 12/24.** Twelve modules were declared `FINITE_STATE` — *"this module remembers something I
cannot explain"* — and **not one of them is a state machine.** Every one is a static or finite-history function of
its sources. False certainty as scored: 5/24 against a preregistered bar of zero (see the caveat below).

By channel — that is, by **distance from the clock**:

```
FINITE_STATE verdicts:   channel 0: 0     channel 1: 4     channel 2: 8
```

## The cause

`harvest()` labels each sample with its source history as `g[t − d]`, where `d` is the source's lag. **When
`d > t`, `t − d` is negative and numpy reads from the end of the array.** The row is then labelled with a source
history from a completely different time — *a state the world never produced*.

Channel 0's clock lag (12–18) sits below the settle margin of 32, so no feature is ever read before time begins.
Channel 1's lag is ~35 and channel 2's ~47: 3 and 15 of the 64 sampled steps respectively are labelled with
fabricated histories. Those rows contradict the real ones, the consistency check correctly rejects every finite
lag window, and the observer concludes the module has hidden internal state.

> The observer whose entire thesis is *"never evaluate a function on states the world cannot realize"*
> **fabricated source histories itself**, by indexing before the beginning of time.
>
> Its consistency check worked perfectly. It detected the contradiction and reported hidden state. The thing that
> was hiding state was the array index.

`assert_manifold_generated` guarded the wrong side of the pair: it verified that every row had a **generated
output**, never that the row was **labelled with the history that produced it**.

## An error of mine in the scorer, reported because it inflates the failure

On channels with program bit 0, the observer reported the second source as the **write-enable rail** `(20,1)`
rather than the register — and it is **right**. Pulsing `we` to 1 makes the register load, so `we` genuinely is an
upstream cause; the observer's table `y = clk AND we` is a correct and complete description of the world, at
coverage 1.0. My `truth_sources` filtered that cell out as an "inert rail" — a justification I wrote *in order to
make the ground truth produce the source count I expected*. That is the D-053 error, committed by me, in the
scorer, after everything.

So some of the 5 false-certainty rows are my mis-scoring, not the observer's error. **This does not rescue the
design.** The 12 false abstentions are real, are not scoring artefacts, and alone fail the run.

## Verdict and classification (mission §11)

**RETIRED.** Preserved unchanged. Not patched, not re-tuned, no second cycle.

- **Primary: MANIFOLD IDENTIFICATION.** The manifold was populated with rows whose source-history labels were read
  from before the start of the observation window.
- **Contributing: SCOPE CALIBRATION of my own verification.** The development certificate inspected **channel 0 of
  three** — the single channel where the defect cannot appear. Twenty cases, one third of the available ground
  truth exercised.
- **Not source discovery.** Source counts were 95.8 % correct; duplication patterns were recovered; on every
  channel where no feature was read before time began, the class was 100 % correct.

**EXP-SC-01 remains BLOCKED.**

## What survives, and what it costs

The *ontology* did what it was built to do. Where the index defect could not bite, the observer took three and four
boundary taps and returned **two causes**; it recovered a duplicated source, an inverted-delayed tap, a
history-dependent edge detector, a module built out of internal state whose interface is nonetheless static, and
two registers with byte-identical baseline series that it refused to merge. It abstained exactly where the world
could not answer, and refused to abstain where it could.

None of that is certified. It was measured on a run that failed, and a design that fails is retired whatever else
it got right. The next observer inherits the ontology as a **hypothesis**, not as a result.

## Next strategy (mission §11)

An **active experiment-planning observer**: one that *chooses* its interventions to maximise causal
identifiability rather than executing a fixed tomography schedule — and that, before estimating any function,
proves every feature it uses was **observed inside the window it claims to have observed it in**.
