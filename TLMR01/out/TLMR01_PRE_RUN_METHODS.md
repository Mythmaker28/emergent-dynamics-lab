# TLMR01 — PRE-RUN METHODS, COMPLETE AND CLOSED

`TARGETED-LINEAGE-MEASUREMENT-FOR-REPRODUCTION-01`. Published **before world 1**. Every rule,
threshold, unit and ordering below is fixed by the master freeze `b354944f0e5b7f82`.

## The one scientific question

At three exact, previously executed laws, what are the fork hazard **e(n) above the occupation
support ceiling n = 5**, the occupation-resolved maturation law **s(n)**, **P(trigger | matured)**,
the **single-centre time exposure** and the **integrated trigger-to-turnover rate** — measured
directly, never modelled?

**Primary estimand:** e(n) for n > 5. Its success criterion is SUPPORT, not a value: whether
e(n) becomes DIRECTLY_MEASURED (≥10 worlds and ≥30 single-centre steps) in at least one stratum
above n = 5. There is deliberately no threshold on its value, because a measurement programme
that set one would be taking a threshold from the outcomes it judges.

**Selection statistic:** M5, the integrated rate, unit = world. It orders the laws for the
selection rule and is kept in a separate role from the primary on purpose.

## The three laws — no new tuple is invented

| law | kY | muY | p_hop_Y | worlds | why it is here |
|---|---|---|---|---:|---|
| `LAW_A_B1` | 2.51189e-05 | 9.26119e-05 | 0.102633 | 128 | established daughter formation and functional-turnover anchor (FDOT01 7 of 160) |
| `LAW_B_POINT_D10` | 2.51189e-05 | 9.26119e-05 | 0.0102633 | 128 | slow-mobility post-removal anchor with a measured integrated event rate (3 of 256) |
| `LAW_C_MCTT01` | 0.00100475 | 0.000740895 | 0.102633 | 256 | high-occupation law that directly populates the n>5 regime missing from e(n); its Stage B was never executed |

Everything else is identical across the three: engine, LawSpec, feed and exchange law,
scheduler, initial condition, centre classifier, identity rule, trigger rule, intervention,
horizon, CAP, L = 36, p_hop_X, muX, kX, X_SEED. `X_LAWSPEC_BASELINE = UNCHANGED`,
`NEW_PARAMETER_POINTS = 0`.

## What was closed before world 1

| gate | result |
|---|---|
| `ALL_PRE_RUN_ARTEFACTS_PRESENT` | **True** |
| `METHODS_CLOSURES_AGREE` | **True** |
| `NO_INHERITED_MODULE_HAS_DRIFTED` | **True** |
| `INSTRUMENTATION_INERTNESS` | **PASS** |
| `ARCHIVE_DECISION_RECONSTRUCTION` | **PASS** |
| `PATH_COVERAGE` | **PASS** |
| `WRITER_AND_READ_BACK` | **True** |
| `OFFLINE_AGREEMENT_NON_VACUOUS` | **True** |
| `SEED_GATES` | **True** |
| `PRIMARY_BUDGET_EXACT` | **True** |

### Methods closure, computed two independent ways

- **33** module files execute; **39** files hashed including byte-identical alternative copies.
- **6** import names resolve to more than one file on the search path; all candidates are
  byte-identical (`ALL_AMBIGUITY_IS_BYTE_IDENTICAL = True`).
- **0** inherited modules have drifted from any ancestor's frozen hash.
- **3** executing modules appear in no inherited manifest — `topology`, `nulls_obtc` and
  `source_operator` — which is FOTSEA01's gap. They execute from `OBTC01/code`, **not** from the
  `OBTC02/code` paths FOTSEA01 named, because `metrics_obtc.py` inserts `/home/claude/OBTC01/code`
  at import time. Both copies are byte-identical; the hazard was that nothing was checking.

### Instrument qualification (§5)

- `INSTRUMENTATION_INERTNESS = PASS` — bit-identical fields, RNG state and scheduler counter at
  every step, with and without recording, on all three laws.
- `ARCHIVE_DECISION_RECONSTRUCTION = PASS` — the component structure rebuilds from written rows alone.
- `PATH_COVERAGE = PASS` — 18 deterministic geometry cases, and on every law: Y birth, Y removal,
  X birth, fork, split termination, merge termination, clean continuation, fresh identity, the
  descent rule, a **natural** trigger, the selective-removal path and its conservation audit.
- **100 % line coverage** of `run_world`, `tl_record`, `build` and `tlmr_init`, including the
  integrity-fault branch, which is proved to fire by a deliberately corrupted fixture.
- The offline reconstruction reproduces the online record exactly — state machine, centroids
  bit-for-bit, local-X disc mass, identity link, maturation candidates and t_m — on 5 worlds
  across 3 laws, and the gate is required to be **non-vacuous** (4 candidates, 3 removals).
- The writer and read-back are qualified on a fixture seed; the fixture found a real defect
  (`np.savez_compressed` appends `.npz`, so the atomic temporary name was never replaced).

### Defects found by this mission's own fixtures, before world 1

| id | what | fixed how |
|---|---|---|
| D-DESCENT-TERMINAL-OVERWRITE | the inherited trigger overwrites its descent fields at every later 1 → 2 separation, so its terminal value is not the one that named the removed parent (a fixture fired at 299 and finished carrying 1165) | `run_world` snapshots `AT_TRIGGER` at the firing step and reports terminal values separately; the inherited module is untouched |
| D-ARCHIVE-NO-LOCAL-X | `P(trigger | matured)` was not reconstructable from the archive at all: the frozen f5 ratio sums X over a disc covering cells with no Y | the schema records `k_xd` per component per step, proved equal to `ID.disc_mask` at all 1296 centres |
| D-ROUNDED-CENTROID | a centroid stored to three decimals could flip an identity link within rounding of CORE_R | exact centroid inputs `a0`, `so`, `m` stored; the offline reader recomputes the frozen expression bit-for-bit |
| D-CLOSURE-ROOT-FILTER | the first methods closure filtered by a hand-written list of three project roots and silently dropped three modules that execute from a fourth | the filter is gone; anything not stdlib and not site-packages counts |
| D-WRITER-TEMP-NAME | the atomic write replaced a temporary file that numpy had never created | temporary name ends in `.npz` |

## Seeds

`sha256(PARENT_TIP | 'TLMR01' | LAW_ID | ROLE | INDEX)[:8] mod 2^32`, with the parent tip
**resolved from the repository**: `9f4c70ceeb05b0b8a1f27c4cfc855e125f921ce9`.
The handoff prose carried `098cfa12f3460f3cc56a6419bfe6c4eb501ec4f8`, which is ILRR01's tip and not FOTSEA01's; the handoff itself
instructs that the value be re-resolved rather than trusted. The discrepancy is reported, not smoothed.

512 primary seeds (LAW_A_B1 128, LAW_B_POINT_D10 128, LAW_C_MCTT01 256), 6 technical reserves. Distinctness and disjointness — primary/reserve,
law/law, and against the fixture band — are proved by enumeration, not argued. Seed set hash
`f5f0243770bbf86a`.

## Power and selection, entirely pre-computed

Floor `F_INTEGRATED = 0.0032015171041760242`, the exact one-sided lower 95 % bound on **BPRTC01's published
3 of 256** post-removal functional complete turnovers at POINT_D10 — the only parent endpoint
that matches M5 in kind. The principle (match the endpoint kind) was stated before the value was
computed, which is why FDOT01's easier 7 of 160 is reported as a stronger reference and never
used as the gate.

| law | n | p\* for K ≥ 2 | K needed (E3) | K needed (E6) | binding K | confirmation n |
|---|---:|---:|---:|---:|---:|---:|
| `LAW_A_B1` | 128 | 0.0232115 | 3 | 4 | **4** | 735 |
| `LAW_B_POINT_D10` | 128 | 0.0232115 | 3 | 4 | **4** | 735 |
| `LAW_C_MCTT01` | 256 | 0.011651 | 4 | 6 | **6** | 770 |

Declared limitation, before world 1: at LAW_B_POINT_D10 the design is **underpowered** relative
to its own inherited expectation — BPRTC01 measured this exact chain at this exact law as 3 of
256, and p\*(128) is larger than that. It is stated here rather than repaired later by pooling
or by moving worlds. The pooled p\*(512) = 0.00583688 is shown only for contrast and is **not** the
design's assurance.

## Claim ceiling and vocabulary

```
H3_STATUS                                      = NOT_TESTED
REPRODUCTION_STATUS                            = NOT_TESTED
HEREDITY_STATUS                                = NOT_TESTED
AUTONOMOUS_COHESION_STATUS                     = NOT_ESTABLISHED
X_LAWSPEC_BASELINE                             = UNCHANGED
ARCHITECTURE_CHANGE_NECESSITY                  = NOT_ESTABLISHED
COMPANION_PAPER_V1_1_STATUS                    = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED
PTOPD01_LINEAGE_POINT_ROUTE_STATUS             = PAUSED
OLD_ROUTE_A_STATUS                             = REJECTED__NOT_AUTHORISED
FINITE_SIZE_RELEVANCE                          = NOT_SUPPORTED
```
Forbidden vocabulary: *organism*, *daughter organism*, *life created*, *self-replication
demonstrated*. Forbidden claims — reproduction, heredity, life, autonomous cohesion, H3
confirmation, Kamimura–Kaneko validation, a minority window — **including in denial**.

The ceiling is: *the named objects have been measured at the laws and occupancies stated.*
Nothing more, and no point is qualified by this mission.

