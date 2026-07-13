# EXP-GT-01 — factorizing did not make it pass; it made the failure legible (2026-07-12)

The observer still fails. But this time I can say *what is wrong with it*, in two sentences, and that is the whole
difference.

The scalar observer of EXP-GT-00 failed with one number: 1.518, "too far". No idea why. The factorized observer
fails with a table, and the table names the bugs. **The S head scores 0.000 for two circuits with different memory
words** — it is blind, because my blinded probe grid (stride 20) is too coarse to land on the channel tracks, so no
pulse ever distinguishes a gated channel from an open one. I never stated a *resolution* requirement for the probe
design and never verified one. And **the A and F heads are confounded**: I computed the E1 fingerprints on the
post-handoff final frame — a state with gliders mid-flight — and compared them against fingerprints from a fresh
grid. That compares transients, not architectures.

Neither of those is a weight to tune. They are design errors, and factorizing is what exposed them.

## What did work
**E1 is now a real Ship-of-Theseus gate.** The component is handed off to a functionally equivalent, microscopically
distinct implementation — relief installed *before* the incumbent is removed, so the gate is never unmanned — and all
three assertions hold: the trajectory genuinely changed (441/701 frames), the replacement genuinely happened, and the
**input-output behaviour is identical at every single timestep**. No silent interval. The held-out implementation
passes too, after assertion (iii) caught my first attempt putting the relief *below* the output line.

**And the L head says "I don't know."** Two exact copies at the same phase produce literally identical trajectories,
so lineage is not identifiable from trajectories alone — and the head reports **INDETERMINATE** instead of
manufacturing an answer. A scalar distance had no way to express that. It would have returned 0.0 and called them the
same individual, which is a guess dressed as a measurement.

## Standing
Droplets blocked, correctly. Nothing promoted. EXP-GT-00 preserved unchanged as the record of the first failed
observer. No head tuned to pass, no threshold moved, no composite score anywhere.

Ten substrates and observers in, the pattern of this project is clear and I have stopped resenting it: I keep
building instruments that cannot see, and the only reason I ever find out is that I keep building the thing that
checks them.
