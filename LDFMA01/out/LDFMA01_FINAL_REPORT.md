# LDFMA01 — FINAL REPORT

**LOCKED-DAUGHTER-FAILURE-MECHANISM-ARBITRATION-01**
*Why the ambient turnover saturates while the locked daughter almost never turns over — and which
single route that licenses.*

```
FINAL_DISPOSITION = LOCKED_DAUGHTER_FAILURE_MECHANISM_IDENTIFIED__
                    ONE_MATCHED_CONTROL_TEST_ELIGIBLE
NEW_SCIENTIFIC_ENGINE_RUNS = 0   NEW_SEEDS = 0   NEW_TRAJECTORIES = 0
ROUTES_EVALUATED = 3   ROUTES_SELECTED = 1   CHECKERS = 1   CASCADES = 0
```

---

## 1. A fifth rollback, and a 572 KB recovery

The container reverted to the FDOT01 C2 snapshot again before this mission began, erasing TLMR01,
FIMRCC01 and every staged upload. Nothing was lost: two incremental bundles chained to a commit the
snapshot already held restored tip `3d67654` for **572 275 bytes**, after which 18 of 18 FIMRCC01
artefacts verified against their own `SHA256SUMS`.

## 2. The record, bound and recomputed

**37 artefacts** bound by exact bytes, zero missing. Every declared count was **recomputed from the
per-world records**, not read from the artefact asserting it: 256 LAW_C worlds, 26 triggered, 22
removals, 22/22 ambient, 2 018 complete intervals, median 93, locked daughter 1/22 and 1/256,
`P(K≥2 | N=50, p=1/256) = 0.0165`, zero fresh worlds. All ten reproduce.

TLMR01's `22/22` is **not called false**. It is a true statement about a broader population object.

## 3. A third reconstruction, from raw bytes

`ldfma01_raw.py` imports neither `tlmr01_offline` nor any `fimrcc01_*` module, reads neither
`c_cid` nor `k_id`, takes its constants from the PQEC01 and BPRTC01 freeze JSONs, and finds
components by **BFS flood-fill** rather than union-find or label propagation.

```
world-level verdict      26 / 26
trigger step t_m         26 / 26
daughter cell set        22 / 22
parent cell set          22 / 22
removal fidelity         22 / 22 on all five checks
component-count disagreements   0
locked-daughter COMPLETE and FUNCTIONAL   1 / 22   (required result reproduced)
```

`FIMRCC01_RECORD_NOT_INTERPRETABLE` is not available: the record reproduces.

## 4. The funnel

| code | stage | n |
|---|---|---|
| L2 | no accepted Y birth inside the locked identity | 5 |
| **L3** | **accepted birth occurs but no Y removal** | **16** |
| SUCCESS | complete turnover with local X on both sides | 1 |

`L5` is unreachable by construction; `L0, L1, L4, L6, L7, L9–L12` are unobserved. The **termination
type is `SPLIT_OR_TIE` in 22 of 22**, always with exactly two successor candidates within `CORE_R`.
Under the exposure model that split is **causally upstream** of L2/L3 — both orderings are published.

## 5. The mechanism, in two parts

**Part 1 — exposure.** At the trigger the whole world holds **2 to 5 Y particles**;
`parent_nY + daughter_nY = world_nY` in 22 of 22. The daughter persists a median 230 steps, giving
**11 385 particle-steps** across the 22 worlds and `λ = muY × particle-steps` of mean **0.383**. The
exposure model predicts **5.809** completed worlds among those that saw a birth. Five are observed.
The daughter's turnover is **exposure-limited**, and exposure is occupancy × identity lifetime.

**Part 2 — attribution.** The frozen endpoint attributes a ledger event to the component whose cell
set contains it *at step t*, while the archive writes cell rows *after* the step. A decay that
empties a cell is invisible to it. Re-attributing the identical rows one step earlier — a
**lower-bounding proxy**, not a repair — raises the count from **1 to 8** and the COMPLETE rate from
**1/22 to 5/22**, FUNCTIONAL to at most **4/22**. **Seventeen of the 21 failures survive the repair**,
for the physical reason in part 1.

Neither part alone explains 1 of 22.

## 6. Why the ambient endpoint saturates

Every world contains **65 to 117** COMPLETE identity intervals after the removal. **Zero complete
intervals other than the daughter's own begin inside any daughter's window**; the ambient bloom
arrives **706 to 2 614 steps later**, in a population that did not exist at the removal. The
`22/22` measures succession, not competition. The repeated-opportunity expression is retained only
as an **illustration** — with n ≥ 694 it cannot fail — and the conclusion rests on the two
model-free facts above.

## 7. The single success

No significance test was run; one success is not a population sample. Of **39** comparable features
only 4 lie outside the failure range, against a null expectation of **3.5** — the uniqueness scan
carries no evidence of a separating feature. Three of the four are restatements of the outcome. The
one available-before-outcome "unique" feature, `f5_ratio_at_trigger = 1.0`, is a **cap artefact** of
a folded statistic whose unfolded twin ranks 13 of 22.

The success is **not** ordinary everywhere: it sits at rank ≤ 3 of 22 and outside the failure
interquartile span on the parent–daughter distance and on three ambient measures. It is ordinary on
lifetime, occupancy, local X and birth count.

**No available-before-outcome feature separates it.** There is no prospective eligibility criterion.

## 8. The routes

**Route B — `NO_MINIMAL_CHANGE_JUSTIFIED`.** Three candidates evaluated. B1 repairs a failure never
observed: 0 of 22 daughters went extinct. B2 targets a bloom that arrives after the daughter is
gone. B3 needs a swept value, which the launcher forbids. This classification does **not** depend on
the attribution probe.

**Route A — `MATCHED_CONTROL_TEST_ELIGIBLE`, endpoint E3.** E5 remains rejected: it substitutes
ambient turnover for daughter turnover. E1-corrected is rejected as the *selected* endpoint because
adopting an attribution repair found after the outcomes would be post-outcome endpoint selection —
it becomes a **precondition** of the handoff instead. E3 passes all seven conditions, with a stated
ceiling on condition 7.

**41 paired blocks** under an admissible fork at `t_m`, power **0.971** at the point estimate and
0.402 at the Wilson lower bound.

## 9. The checker changed the answer

One adversarial checker, zero runs. Its raw return was written, hashed
(`f93c85a7082973c426fbe99bd5a47c7bda20b1c2ceac81101595058ede0ce5ba`) and written to Windows
**before any finding was read for action**. **28 findings, none dismissed, four load-bearing upheld.**

**C-03 changed the disposition.** I had rejected E3 on the ground that persistence is not the
binding constraint. That was wrong, and it was mine: the exposure model reproduces the corrected
completion count to 5.809 against 5, so persistence × occupancy *is* binding. With the argument
withdrawn, Route A became eligible and the mission moved off a pause.

**C-21 corrected my budget arithmetic.** I charged the shared prefix per paired block, making the
fork look more expensive; it must be charged per seed. 41 pairs, not 22.

**C-16 and C-17** caught the worst of my prose: the autopsy markdown named features as falsified
that its own JSON says are not, and an inclusive interquartile test inverted three of seven
falsifications on tied discrete features.

The checker was wrong about exactly one thing (C-05's naming of `i153`), and that is recorded too.

## 10. Standing status

```
H3_STATUS                     = NOT_TESTED
REPRODUCTION_STATUS           = NOT_TESTED
HEREDITY_STATUS               = NOT_TESTED
AUTONOMOUS_COHESION_STATUS    = NOT_ESTABLISHED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
X_LAWSPEC_BASELINE            = UNCHANGED
FINITE_SIZE_RELEVANCE         = NOT_SUPPORTED
COMPANION_PAPER_V1_1_STATUS   = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED
```

One handoff is created and **not executed**:
`HANDOFF_ONE_MATCHED_LOCKED_DAUGHTER_CONTROL_TEST_01.md`.
