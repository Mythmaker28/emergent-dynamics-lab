# SQDT00_INDEPENDENT_UNIT_AND_RANDOMIZATION_REPORT

## Independent unit
The independent unit is the **upstream ancestry block** (a seed's `found → advance → history →
settle` precursor), exactly as inherited from WSFSCRP00 and WL2SMF00. The design called for
`n = 8` such blocks. Repeated arms (two carriers), repeated doses (1× and 2×) and twin shams
within a block are **repeated conditions, never replications**.

## What was actually constructed
**Nothing.** The static 2× dose-axis audit fired stop rule S5 before any fresh panel, so the
8-block panel was designed and frozen but never built. There are therefore **0 constructed units**
and no randomization was drawn. `n_constructed = 0`.

## Frozen design that was not executed
* Seed namespace `66000–66015`, disjoint from `61000-61009`, the reserved-and-unread
  `62000-62009`, `63xxx`, `64000-64011`, `65000-65007`.
* Four cell-specific subqueues of four for `(NEAR, a0), (NEAR, a1), (FAR, a0), (FAR, a1)`,
  round-robin, two acceptances per cell.
* Parity de-confounding: each subqueue holds two even and two odd seeds; accept the first
  qualifier, then the next qualifier of the **opposite** parity, to break the FSCMA00
  parity ≡ geometry ≡ history-order collapse.

## Factors explicitly not tested
* **Geometry (FAR/NEAR):** `NOT_TESTED_IN_THIS_DESIGN`. The panel would have spanned it to widen
  the null and the ancestry variance, never to estimate a geometry effect, which the inherited
  reader-confound audit shows could be mechanical.
* **Allocation (a0/a1):** `NOT_TESTED_IN_THIS_DESIGN`, for the same reason.
* **Dose (1×/2×):** `STATICALLY_INADMISSIBLE` — the locked carriers carry no dose magnitude.

Because no units were constructed, no independence assumption is exercised and none is claimed.
