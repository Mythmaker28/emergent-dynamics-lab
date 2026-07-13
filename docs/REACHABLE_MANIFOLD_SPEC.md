# REACHABLE MANIFOLD SPECIFICATION

> "Discover the smallest set of independent causal processes and histories that explains what the box can do,
> **only on the states the world can actually realize**."

## The admissible repertoire (declared, frozen before the prospective run)

**For structure** — ancestry, lags, independence: one-step **pulses**, at every phase of the inferred period.

**For function** — the manifold itself: **sustained source regimes only**. Free running, plus constant clamps on
every subset of the module's sources. Transient pulses do **not** populate the manifold: a one-step glitch is not
an operating regime, and letting a single transient sample define a row of a law is how an artefact becomes a
physics.

**Never**: clamping a boundary **tap**. A tap is a consequence; clamping it fabricates a world. A source is a
cause; clamping it interrogates *this* one.

This restriction is declared, not discovered: a pulse *would* reach rows that clamps cannot. Every coverage figure
is therefore coverage **relative to this repertoire** — which is precisely what an INDETERMINATE verdict reports.

## What must be asserted

Every reported reachable state was **actually generated** (`assert_manifold_generated`); every source clamp
**took** (the source's series must actually hold the value asked for, or the run is rejected); no impossible
boundary assignment entered function estimation; intervention windows are equal; histories span the declared lags.

## Coverage governs the claim

Full Cartesian product covered → a static table may be reported. Otherwise: a **partial** table, a finite-history
transducer, a context-conditioned transducer, or **INDETERMINATE**. Off-manifold behaviour is never invented.

`lag8_and` vs `lag8_or` — two taps of one source separated by exactly one clock period — are identical under every
sustained regime (coverage 4/8) and differ only where the world cannot go. Verdict: **INDETERMINATE**, not SAME.

`lag15_or` vs `lag15_xor` — byte-identical free-running outputs — are fully covered *because clamping the source
reaches the separating row*. Verdict: **DIFFERENT**. Refusing to look would have been false abstention.

## THE DEFECT THAT KILLED THIS DESIGN (D-067)

`harvest()` builds each row's feature vector as `g[t − d]`, where `d` is a source lag. **When `d > t`, `t − d` is
negative, and numpy reads from the END of the array.** The row is then labelled with a source history from a
completely different time — a state the world never produced, invented by the observer whose entire purpose was to
never do that.

The consistency check did its job: the fabricated rows contradicted the real ones, so the model class was rejected
and the observer escalated to `FINITE_STATE` — *"this module remembers something I cannot explain."* The thing that
remembered something was the array index.

`assert_manifold_generated` guarded the wrong side of the pair. It verified that every row had a **generated
output**. It never verified that the row was **labelled with the source history that actually produced it**.
