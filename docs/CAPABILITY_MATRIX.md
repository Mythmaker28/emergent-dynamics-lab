# CAPABILITY MATRIX — every observer generation

**Legend.** `QUALIFIED` = demonstrated on a frozen prospective split, once, against privileged ground truth ·
`DIAGNOSTIC ONLY` = measured, but on burned worlds, or with an evaluator defect that invalidates the metric, or
recovered correctly under a criterion that was not the one being tested · `FAILED` = tested prospectively and did
not meet its preregistered bar · `UNTESTED` = never exercised (in several cases **not constructible** in that
substrate, which is noted).

Nothing below is a scalar and nothing is composited. A generation may fail on one capability and hold on another;
that is the whole point of factorization, and it is why the retirements did not destroy the results.

| capability | G0 monolith (EXP-GT-00) | G1 factorized V2 | G2 head V3 | G3 head V4 (GoL) | G4 module discovery | G5 source-transducer | G6 active causal |
|---|---|---|---|---|---|---|---|
| **object boundary** | FAILED (persistent-site heuristic) | DIAGNOSTIC ONLY (declared components) | DIAGNOSTIC ONLY | DIAGNOSTIC ONLY ¹ | **QUALIFIED** (exact, mean IoU 1.000 on unseen impls) | QUALIFIED | **QUALIFIED** (region found 24/24) |
| **causal source discovery** | UNTESTED | UNTESTED | UNTESTED | UNTESTED (sources are declared) | **FAILED** (delayed copies counted as independent parents) | DIAGNOSTIC ONLY ² | **QUALIFIED** (count 100 %, identities 100 % vs privileged audit) |
| **temporal provenance** | UNTESTED | UNTESTED | UNTESTED | UNTESTED ³ | UNTESTED | **FAILED** (negative index fabricated source histories) | **QUALIFIED** (20/20; 0 fabricated, 0 excluded, lag 17→56 no degradation) |
| **reachable manifold** | UNTESTED | UNTESTED | UNTESTED | UNTESTED | **FAILED** (tables measured off-manifold) | DIAGNOSTIC ONLY ⁴ | **QUALIFIED** (coverage correct; partial → `EQUIVALENCE_CLASS_ONLY` on unseen) |
| **function (I/O on the reachable manifold)** | DIAGNOSTIC ONLY (output-series distance) | **QUALIFIED** (head F) | QUALIFIED (F) | **QUALIFIED** (F) | **FAILED** (50 % on unseen impls) | **FAILED** (29.2 %) ⁴ | **QUALIFIED** (100 % vs privileged simulation) |
| **hidden state** | UNTESTED | UNTESTED | UNTESTED | UNTESTED (not constructible in GoL library) | UNTESTED | **FAILED** (12/24 false `FINITE_STATE`) | **QUALIFIED** (6/6, on the true state machines and nowhere else) |
| **model minimality** | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | **FAILED** (21/24; cannot eliminate a redundant history variable) |
| **architecture** | **FAILED** (composite scalar) | **FAILED — IMPLEMENTATION** (held-out) | **FAILED → RETIRED** | **QUALIFIED** (A_TOPO/A_TAU/G, third fresh split, D-060) ¹ | DIAGNOSTIC ONLY (micro/macro quotient) | DIAGNOSTIC ONLY | DIAGNOSTIC ONLY ⁵ |
| **lineage** | UNTESTED | **QUALIFIED** (head L) | QUALIFIED (L) | **QUALIFIED** (L; E1/E2 Ship-of-Theseus) | UNTESTED | UNTESTED | UNTESTED |
| **abstention** | **FAILED** (never abstained) | QUALIFIED (fires) | QUALIFIED | **QUALIFIED** (fires) ¹ | **FAILED** (6/24 false certainty, 0 abstentions) | **FAILED** (12/24 false abstention) | **QUALIFIED** (response-level: 9/24 abstentions, all correct) ⁶ |
| **PROSPECTIVE STATUS** | **FAILED** | **FAILED** | **FAILED → RETIRED** | **QUALIFIED** (GoL; hierarchy UNTESTED) | **FAILED → RETIRED** (D-065) | **FAILED → RETIRED** (D-067) | **FAILED → RETIRED** (D-069) |

**¹** V4's architecture head is prospectively qualified on Game of Life *only*, with declared limits: **no scope
self-check** (components closer than 4 cells are silently merged), program-invariance **not constructible**,
feedback **not constructible**, and **hierarchical blind discovery never attempted**.

**²** G5's prospective source-**count** was 95.8 %, but the source-**identity** metric is invalidated by an
evaluator defect of mine (the write-enable rail was excluded from ground truth). It is therefore not a result. The
same question was answered cleanly by G6 against a corrected privileged audit.

**³** Temporal provenance was not a concept before D-067. G3's windows happen to have been adequate; **that is not
a demonstration**, and it may not be claimed as one.

**⁴** G5's function failure is *caused by* its provenance failure, not by an independent defect of manifold
reasoning. Its manifold logic — coverage, partial tables, off-manifold abstention — was correct on development and
is not separately falsified; it is DIAGNOSTIC ONLY because it was never tested on uncorrupted features.

**⁵** G6 recovered micro regions correctly, but the **full hierarchy** (machine graph, A/S/F/L/M, counterfactual
validation of macro objects) was gated behind prospective qualification and therefore **never ran**.

**⁶** G6's three errors were **description-level** (a model-class label), not **response-level**. It never claimed
a wrong function, a wrong source, a wrong coverage, or a state machine that was not one. The description-level
failure is recorded in the `model minimality` row, where it belongs.

---

## SCOPE CLARIFICATIONS (D-071) — two capabilities that must not be assumed to travel

**1. Temporal provenance is qualified ONLY for the certified Boolean-world pipeline and its executable provenance
contract.** The 20/20 certificate and the "0 fabricated / 0 excluded rows" result are statements about
`provenance.py`, `Episode`, `_idx` and the assertion that re-reads every source sample from its own episode. They
are **not** a statement about any other substrate's data path. A continuous reaction-diffusion field has no
episodes, no discrete lags and no cell samples to re-read; its provenance contract does not exist yet and would
have to be built and certified separately.

**2. Exact direct-edge recovery is established ONLY in the synchronous Boolean substrate, under the declared
one-step pulse access.** "Flip a cell at step t and whatever differs at t+1 is a direct child" is a theorem about
a **synchronous, discrete, unit-delay** update rule with **arbitrary single-cell write access**. It has no droplet
analogue: droplet dynamics are continuous and diffusive (there is no "one step later"), and no experimenter can
flip one lattice site of a physical droplet's interior.

**3. (D-073) The RESPONSE REPRESENTATION is qualified ONLY for a BINARY observable.** The frozen fingerprint
decides by **Hamming distance over `uint8` symbols**. The droplet's accessible observable is a **continuous float**.
The instrument is **undefined** there: cast to `uint8` every droplet is identical; compared as floats every droplet
differs from its own later self. Supplying the missing quantization / tolerance / amplitude-mapping rules is
**instrument definition**, not adaptation. This is why `SC-PILOT-CAUSAL-FINGERPRINT` returned `PREFLIGHT_FAIL`.

**Neither capability is assumed to transfer to droplets.** Any droplet claim must re-earn both from scratch, under
that substrate's own access constraints. This is recorded here precisely because the temptation to quote a Boolean
result in a continuous substrate is exactly the category of error that retired three observers.

---

## The scope of the D-069 verdict, stated exactly

**G6 predicted every measured function correctly.** Its tables agree with privileged simulation on **every row of
every world**, including the four implementations it had never seen. It did not misunderstand the prospective
worlds.

**G6 failed the preregistered minimal-representation criterion**, on 3 of 24 transducers, because its search can
**widen** a history window but cannot **eliminate a redundant history variable**. On `xor3` it therefore reported
`FINITE_HISTORY` where `DELAYED_STATIC` is the minimal truth — a correct model with one argument too many.

It is **not fully qualified**, and it is **not a failure of comprehension**. It is a failure of *description
minimality*, and that distinction is the entire content of the strategic question that follows.
