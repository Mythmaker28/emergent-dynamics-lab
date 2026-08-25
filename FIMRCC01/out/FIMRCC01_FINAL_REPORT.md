# FIMRCC01 — FINAL REPORT

**FRESH-INTEGRATED-MINIMAL-REPRODUCTION-CAUSAL-CONFIRMATION-01**
*A confirmation that stopped at its own gate, and the measurement that stopped it.*

```
FINAL_DISPOSITION = CONFIRMATION_PRECONDITIONS_NOT_MET__LINEAGE_ROUTE_PAUSED
FRESH_WORLD_COUNT = 0
FRESH_SEEDS       = 0
CHECKERS_USED     = 0
```

---

## 1. What this mission was for

TLMR01 measured 512 worlds at three exact laws and selected one, `LAW_C_MCTT01`, as eligible for a
prospective confirmation on fresh disjoint seeds. Its own handoff attached two preconditions and
one warning. The warning was that the frozen turnover endpoint might be **confounded with
occupancy**: at LAW_C, 22 removals leave 2 018 complete post-removal identity intervals, median 93
per world, while LAW_A and LAW_B produce none at all. The handoff said so plainly and required the
successor to publish the ambient rate **before world 1** and to declare a discriminating endpoint
if the inherited one turned out to be saturated.

That is exactly what happened. This report is the result.

---

## 2. Section 0 — both preconditions closed

### P1 — the device path

Every number in TLMR01 came from a reconstruction that ran on the owner's machine, because the
bridge could not carry 800 MB of archives into the container after a total rollback. The
independent checker found that the cross-check of that path used two archives that were an extinct
world and a single-Y world: the identity link and the toroidal distance were never called in
either, and no episode, no maturation candidate and no removal existed in either. It recorded this
as F-01 and attached it to the successor.

It is closed. Three `LAW_C_MCTT01` archives **with a removal applied** were re-measured in the
container with the byte-identical frozen `tlmr01_offline.py` and diffed field for field including
`post_removal_intervals`.

```
N_CROSS_CHECKED             = 3
ALL_HAVE_A_REMOVAL_APPLIED  = true
identity link calls         = min 11 716
toroidal distance calls     = min 127 008
episodes reconstructed      = 266
post-removal intervals      = 280
CROSS_CHECK_PASS            = True
NON_VACUOUS                 = True
```

A defect of my own is recorded in that artefact rather than smoothed away: the first run reported
M1, M2 and M4 differing at every world. The cause was JSON round-tripping integer dict keys to
strings in my comparison, not a data disagreement. Both sides are now normalised identically.

### P2 — the law binding

`BPRTC01_MASTER_FREEZE.json`, `MCTT01_SELECTED_LAW.json` and `MCTT01_PHYSICS_DIFF_FROM_B1.json`
were absent from the container that issued the handoff, so `tlmr01_laws`, `tlmr01_seeds` and
`tlmr01_run` did not import there and the selected law was not bit-verifiable. All three were
retrieved from the owner's evidence capsules.

**All four source artefacts hash to their declared values.** All three laws verify at the IEEE-754
bit level. Every one of the 14 shared frozen constants has a byte-verified source. All 518 frozen
seeds re-derive from the parent-tip string, and the seed-set hash agrees.

One residual is reported and not argued away: the parent commit **object**
`9f4c70ceeb05b0b8a1f27c4cfc855e125f921ce9` is unrecoverable — the rollback erased it, and it is in
none of the three owner-side bare repositories nor in any bundle. Its content is not verifiable.
What corroborates the tip *string* independently is that `TLMR01_C1_C2.bundle`, written before the
rollback, names that exact commit as its prerequisite.

```
PARENT_GIT_OBJECT_STATUS  = PARENT_GIT_OBJECT_NOT_RECOVERED
PARENT_SOURCE_BYTE_STATUS = SOURCE_BYTES_AND_CHAIN_PREREQUISITE_VERIFIED
```

---

## 3. Precondition A — the locked daughter

The daughter was not invented here. It is named by frozen inherited code at the 1→2 separation, by
the FMRCT01 descent rule, carried forward by the strict identity link, and recorded in every
archive. FIMRCC01 reads those fields; it does not choose them.

The decision rule was written and hashed **before** the measurement ran
(`654d8fc5…5209`), so the verdict could not be reverse-engineered from the numbers.

```
A1 unique localisation   22 / 22      PASS
A2 no silent tie          0 tie-breaks PASS
A3 endpoint askable      22 / 22      PASS
PRECONDITION_A = PASS
```

The daughter interval survives a median of **230** steps after the removal, up to 1 472.

### The disclosure that changed the mission

| endpoint | on the 22 removal worlds |
|---|---|
| frozen, unrestricted | **22 / 22 FUNCTIONAL** — 2 018 complete intervals, median 93 per world |
| locked on the daughter | **1 / 22 COMPLETE and FUNCTIONAL** |

The `M5 = 22/256` that made this law confirmation-eligible is carried by the **ambient
population**, not by the daughter. This was published before world 1, as the handoff required.

---

## 4. Precondition B — two classifiers

Classifier 1 is the frozen `tlmr01_offline`, byte-unchanged, which reads the online component id.
Classifier 2 reads coordinates and per-cell Y occupancy only, closes the single-linkage relation by
label propagation instead of union-find, and reconstructs the components, the centroids, the
identity links, the episodes, the maturation gates, the identity intervals and their event content.

```
worlds compared        256
steps compared   2 816 000
episodes compared   16 368
M2 / M3 / M5 / event step agreement   256 / 256   (100 %)
```

At the owner's closure instruction the requirement was extended to the **naming itself**. On the 26
triggered worlds, with no online verdict or id used as an input:

```
world-level verdict   26 / 26
event step t_m        26 / 26
daughter cell set     22 / 22
parent cell set       22 / 22
removal fidelity      22 / 22 on all five checks
locked-daughter endpoint reproduced   1 / 22
PRECONDITION_B = PASS
```

**One declared dependency, stated rather than claimed away.** The local X disc mass `xd` cannot be
recomputed: the narrow archive stores the X field only on Y-occupied cells, and the frozen gate
sums X over an 81-cell disc most of which is not. It is read from the component rows and attached
by matching *(centroid, ncells, nY)* — a physical match, never an id match. That match is a
bijection at every step of every world. It affects only `GATE_local_x_ratio`; the component
structure, M2, the identity intervals and the event step do not depend on it.

### Two things the reconstruction surfaced

The **literal MRCI01 clause 4** returns `DESCENT_AMBIGUOUS_BOTH_INSIDE_CORE_R` in **26 of 26**
triggered worlds. FMRCT01 documented this as its reason for the frozen rule and measured it on
FDOT01's archives; at LAW_C it is total.

The frozen trigger's **terminal** descent fields differ from the **at-trigger** ones in **25 of
26** worlds, because they keep being overwritten at every later 1→2 transition. TLMR01 named the
defect; this reconstruction snapshots the naming as of the trigger step. My own first version read
the terminal values and disagreed with the archive on one world — a bug in my reconstruction, not a
data disagreement, and it is recorded.

---

## 5. The endpoint adjudication

Six candidates, closed before any number existed, with a selection rule that deliberately prefers
the candidate **closest to the inherited definition** rather than the one with the most power.

| id | endpoint | on TLMR01 | verdict |
|---|---|---|---|
| E0 | unrestricted population | 22/22 | **SATURATED — not eligible as primary** |
| E1 | locked daughter, FUNCTIONAL | 1/22 | **claim-aligned, not decision-capable at N = 50** |
| E2 | locked daughter, COMPLETE only | 1/22 | as E1 |
| E3 | daughter persistence | median 230 | future question, not authorised |
| E4 | daughter constituent events | median 1 | future question, not authorised |
| E5 | ambient population, paired | median 93 | future question, not authorised |

The load-bearing arithmetic:

```
locked-daughter world-level rate      = 1 / 256 = 0.003906
F_INTEGRATED (endpoint-matched floor) = 0.0032015171041760242
ratio                                 = 1.219
K_REQUIREMENT at N = 50               = 2
P(K >= 2 | N = 50, p = 1/256)         = 0.0165
```

No larger N repairs it. The alternative sits essentially on the null: at N = 2 000 the assurance is
still under 10 %.

The paired count contrasts survive discrimination but their prospective power is **not
identified**, because no matched no-removal arm exists anywhere in TLMR01's 512 worlds. Choosing
one after developmental outcome access would change the scientific question. None was chosen.

---

## 6. What this is, and what it is not

No primary endpoint is simultaneously scientifically aligned, independently reconstructable,
non-saturated, and decision-capable under the frozen fresh design.

**This is** `PRECONDITIONS_NOT_MET`.

**This is not** evidence that the phenomenon is impossible. **Not** evidence that the architecture
cannot support it. **Not** a negative fresh confirmation — nothing was run. **Not** a reason to
reinterpret TLMR01 retrospectively: TLMR01's developmental result stands, and answers a broader,
population-level question than the minimal-reproduction claim it was hoped to license.

---

## 7. Standing status

```
H3_STATUS                          = NOT_TESTED
REPRODUCTION_STATUS                = NOT_TESTED
HEREDITY_STATUS                    = NOT_TESTED
AUTONOMOUS_COHESION_STATUS         = NOT_ESTABLISHED
ARCHITECTURE_CHANGE_NECESSITY      = NOT_ESTABLISHED
X_LAWSPEC_BASELINE                 = UNCHANGED
FINITE_SIZE_RELEVANCE              = NOT_SUPPORTED
PTOPD01_LINEAGE_POINT_ROUTE_STATUS = MEASURED, NOT QUALIFIED
COMPANION_PAPER_V1_1_STATUS        = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED
```

Clauses inherited at birth and re-emitted verbatim: `MEASUREMENT_NOT_POINT_SEARCH = true`;
`ONE_ZERO_RUN_DETOUR_ONLY = spent`; `SECOND_FINITE_SIZE_EXTENSION`, `NEW_SIZE_LADDER`,
`POST_OUTCOME_SIZE_RETUNING`, `NEW_PARAMETER_SWEEP`, `GENERIC_CALIBRATION_SUCCESSOR`,
`INTERPOLATION`, `RESPONSE_SURFACE`, `SECOND_TARGETED_MEASUREMENT_CAMPAIGN` = `forbidden`;
`EVERY_SUCCESSOR_MUST_RE_EMIT_THESE_CLAUSES = true`;
`REOPENING_FINITE_SIZE_REQUIRES_EXPLICIT_HUMAN_AUTHORISATION = true`;
`MAX_INDEPENDENT_CHECKERS = 1`; `MAX_REVIEW_CASCADES = 0`;
`CHECKER_RETURN_WRITTEN_BEFORE_ANY_FINDING_IS_ACTED_ON = mandatory`.

Forbidden vocabulary unchanged: *organism*, *daughter organism*, *life created*,
*self-replication demonstrated*.

---

## 8. The route

```
NEXT_SCIENTIFIC_ELIGIBILITY = NONE__LINEAGE_ROUTE_PAUSED
NO_HANDOFF_IS_EMITTED
```

Reopening requires an explicit new human authorisation and a newly derived matched-control design.
Nothing in this mission authorises one.

*Closed at the precondition gate, on the owner's decision, with zero fresh worlds run.*
