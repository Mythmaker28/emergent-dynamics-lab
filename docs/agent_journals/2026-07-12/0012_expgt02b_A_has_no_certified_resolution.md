# EXP-GT-02B — F and L work. A can't see 5 columns. (2026-07-12)

F passes all five cases, including the two that matter: a **pure phase shift** leaves it unmoved, and **two different
architectures implementing the same function** score **SAME**. L passes all three regimes, and — the part I care about
most — it says **INDETERMINATE** for exact copies instead of inventing a lineage difference.

A is fixed structurally and still fails.

The structural bug was real: a channel's detected *column* depends on **how it is gated** — an absorbed injection
shows up at ~gun+30, a deleted stream at ~gun+63 — so my architecture head **moved whenever the program moved**. It
was measuring memory and calling it architecture. The invariant is the **diagonal** `row − col`, which is what a
glider actually travels along and is the same however you gate the channel. Rebuilt on diagonals, A now correctly
ignores phase, ignores the program, and survives both E1 handoffs.

**And then it says two different architectures are the same.** Because the held-out layout's channel gaps differ by
**5 columns**, and my preregistered tolerance is **6.0**. The difference is smaller than the resolution I declared.

I could fix that in one character. I am not going to, because the case I would be fixing it on **is the held-out
case**, and a tolerance tuned on the test you're being graded by is not a measurement — it is a story about one.

## The lesson is the S lesson, one level up
S was not allowed to read an unknown word until it had proved it could read a known one. **A is not entitled to say
"same architecture" until it has certified the smallest architectural difference it can resolve.** Its tolerance must
be *derived* from the development null — the phase-shift comparison, which is the actual noise floor — and declared
before anything held-out is touched.

**An instrument must certify what it can resolve before its "SAME" means anything.** Every "SAME" A has emitted so
far — including the four it got right — is currently uninsured.

Droplets stay blocked. Nothing promoted. F and L are real; A is one certificate away, and the certificate is the
whole point.
