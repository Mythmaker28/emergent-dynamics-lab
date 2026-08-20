# HANDOFF — LATTICE-BOND BOTTLENECK ARBITRATION 01

**Zero engine runs. Zero seeds. Zero worlds. No reimplementation of `od_core.py`.**

This is the successor SNFL01 authorises. It is not a recovery mission and it does not need one: the
work it proposes runs entirely on artefacts that survive by bytes, using an analysis layer that
imports only `csv, json, math, statistics, pathlib`.

## Why this and not a sweep

SNFL01 stopped because the Route E **execution** stack cannot start a world — `od_core.py` is absent
from all 12 615 objects of the repository. But the **analysis** stack runs, and the raw per-event
ledgers survive:

```
P07/p07a_event_ledger.csv.gz      P07/p07b_event_ledger.csv.gz
P07/p07a_rows.csv.gz              P07/p07b_rows.csv.gz
P07/p07a_trace.csv.gz             P07/p07b_trace.csv.gz
P07/p07a_impulse_capacity.csv.gz  P07/p07c_cadence_events.csv
results/ROUTE_E_FLUX_DECOMPOSITION_06/dr05_paired_flux_rows.csv
results/ROUTE_E_FLUX_DECOMPOSITION_06/dr05_event_cohort_fates.csv
results/ROUTE_E_FLUX_DECOMPOSITION_06/dr05_scaffold_timecourse.csv
```

DEV_06 and P08 §1 both produced substantive results from exactly this material with **0 engine
calls**. The mode is proven in this programme.

## The four questions, in order of what the surviving bytes can actually settle

**Q1 — the cardinality distribution that has never been published.**
Only the scalar `median_eligible_sink_sites_per_event = 1` survives. From `p07a_event_ledger.csv.gz`
and `p07b_event_ledger.csv.gz`, recompute per arm, per size, per dose: minimum, median, mean,
maximum, and the fractions with `|E| = 0` and `|E| = 1`. This is the object §5 of SNFL01 required and
could not obtain. It is a deliverable in its own right.

**Q2 — which bound is active, as a function of dose.**
P07 reports the split at Q400 (source 87.0 % / 96.6 %, sink 7.8 % / 0 %). The ledgers carry every
event at every dose. Produce the full active-bound decomposition of `q = min(planned, sink, source)`
across Q100 → Q800 and both sizes. This answers whether the sink's eligible set ever becomes the
dominant bound before the component breaks — the question SNFL01 wanted to test experimentally.

**Q3 — is the L=24 ×8 condition a saturation or a mortality?**
7 of its 9 blocks carry `TREATED_TRACK_LOST`. DEV_06 already found the failures occur between
`t = 7696` and `t = 10880` at compositions (`I/I0` 0.36–0.42) *indistinguishable from the two
survivors*, and called breakage a **connectivity** event rather than a compositional threshold. Use
`dr05_scaffold_timecourse.csv` and `dr05_failure_risk_sets.csv` to test that directly. If confirmed,
the correct statement about the ×8 condition is not "the flux plateaus at 0.385" but "the object
dies, and the survivors are not a plateau".

**Q4 — arbitrate the remaining mechanisms against P08's law.**
P08 established `Φ(s) = min(q/s, ρ)` with `ρ` measured independently and falling by a factor 3–5.
Rank the candidate limiters — self-inflicted deregistration of the mask, source saturation at `MMAX`,
the cadence/relaxation mediator (sink bite ÷24–47 at the second event of a burst), connectivity
breakage — by how much of the observed shortfall each accounts for **in the ledgers**, not in prose.

## Frozen rules inherited from SNFL01 (do not renegotiate)

* Independent unit = **one seed block**. The 144 logical trajectories are **never** `n = 144`.
* `I0` = the block's own `t256` incumbent mass; never pooled, never recomputed per condition.
  Audited: identical across all 7 arms in **0 of 18** divergent blocks.
* `FORCED_COMPONENT_TURNOVER_80` requires **both** `I/I0 ≤ 0.20` **and** `I/T ≤ 0.20`.
* `0.385` (L=24, **n = 2**) and `0.419` (L=32, n = 9) are two **sizes**, not two contexts, and the
  first is survivor-conditioned. Report them separately, always with their n.
* `PLATEAU_ESTABLISHED = false` stands until something overturns it with data.
* No estimand may be invented; no interpolation; no predicted flux for an untested cardinality.

## What would end this line honestly

If Q1–Q4 show that the shortfall is dominated by source saturation and connectivity breakage rather
than by eligible-set cardinality, then eligible-set size is **not** the bottleneck, the SNFL01
question is answered in the negative from surviving evidence, and Route E's throughput line can be
closed with a real mechanism rather than an unresolved plateau. That is a legitimate ending, and it
costs zero engine starts.

If instead the ledgers show a dose region where the sink's eligible set is the dominant active bound
*before* breakage, then — and only then — is there a case for restoring an executable path, and that
case should be made with the numbers in hand rather than in advance.
