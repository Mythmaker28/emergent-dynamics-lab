# ACTIVE TRANSDUCER PROTOCOL (frozen; RETIRED at D-069)

## Model classes, compared

`STATIC` · `DELAYED_STATIC` (source-specific delays) · `FINITE_HISTORY(h)` · `FINITE_STATE`
plus the refusals: `INSUFFICIENT_HISTORY`, `EQUIVALENCE_CLASS_ONLY`, `OUT_OF_SCOPE`, `CONFOUNDED`, `INDETERMINATE`.

Selection is by **consistency**: if one provenance-valid source-history row ever produced two different outputs,
the class is too small and is rejected. That single check is what makes the answer falsifiable.

## Hidden state may be asserted only when

1. every row is **provenance-valid** (source samples re-read from their episode and compared);
2. the window covers **every tested lag** (`max_lag + MAX_HISTORY`);
3. **no** finite-history model up to `MAX_HISTORY` explains the data;
4. context differences have been modelled.

**A contradiction caused by missing history yields `INSUFFICIENT_HISTORY` — never `FINITE_STATE`.** The retired
D-067 observer called twelve combinational gates state machines because its own index had wrapped. This one claimed
hidden state on exactly the two true state machines, prospectively, and nowhere else.

## The defect that retired this protocol

The search **only widens**. On contradiction it escalates to a longer history window. It never performs the
opposite test — *is this measured lag functionally redundant on the covered manifold?* — and so on `xor3`, whose
output gate reads its inputs at two different depths, it returned a **correct three-feature model** (table verified
against privileged simulation, every row) whose second clock lag is redundant. The minimal model is
`DELAYED_STATIC`; it reported `FINITE_HISTORY`.

§7 asks for **the smallest predictive representation**. A search that only grows cannot find it.

The redundancy test is well defined and cheap: a feature `j` is redundant iff, for every covered row, flipping `j`
(where the flipped row is also covered) leaves the output unchanged. It must be run **only on a fully covered
manifold** — on a partial manifold the test passes vacuously, which is itself a trap.
