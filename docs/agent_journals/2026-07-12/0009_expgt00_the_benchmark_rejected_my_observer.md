# EXP-GT-00 — the benchmark rejected my observer (2026-07-12)

This is the best day's work in the project, and it produced no positive result.

I built a Game-of-Life computational hierarchy with real ground truth: verified gliders, a verified eater, a working
inhibit gate, a memory bit, and a tiny FSM whose output is *exactly* 194 × (open channels) — I can check the
observer's answers against the truth because I hold the truth. And by construction the benchmark hands me the
hardest case for free: programs 1010, 0101 and 1100 emit **identical** output (388). Same function, different
mechanism, no way to tell them apart from behaviour alone.

My observer nailed that one (d = 1.42). It nailed exact copies (d = 0.000). It nailed different architectures.

**And it failed the Ship of Theseus.** Under progressive component replacement — the thing this entire research
programme is *about* — the representation moved **further** (1.518) than it moves between genuinely different
programs (1.21–1.42). It keys on flow and output statistics, and while a component is briefly absent the flow
changes, so it concludes the individual has changed. It would have looked at a droplet replacing its constituents and
reported a *new individual* every time. On the droplet substrate there is no ground truth, so **I would never have
known.**

That is precisely why the user made me build this before touching EXP-SC-01, and I would not have built it myself.

## And the sixth silent no-op
Challenge (e), as I first wrote it, deleted a still-life eater and re-placed an identical one at the same phase. That
restores the grid exactly: **0 of 701 frames differed.** It "passed" at d = 0.0000. A perfect score on a test that
could not fire. I only caught it because two rows of the results table read exactly 0.0000 and I have been burned
five times already this session.

The lesson has stopped being a lesson and become a habit: **when a metric returns a perfect score, assume it is
broken until you have shown it can fail.**

## Standing
EXP-SC-01 is blocked, and correctly so. Nothing is promoted. D-046 unchanged, D_int untouched, no threshold moved,
no substrate tuned. The next job is a representation that survives component replacement — designed and frozen on
this benchmark, evaluated on held-out circuits, and only then allowed anywhere near a droplet.
