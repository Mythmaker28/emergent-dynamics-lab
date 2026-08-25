# HANDOFF — FRESH INTEGRATED MINIMAL REPRODUCTION CAUSAL CONFIRMATION 01

```
SHORT_NAME          = FIMRCC01
PARENT              = TLMR01 — TARGETED-LINEAGE-MEASUREMENT-FOR-REPRODUCTION-01
PARENT_DISPOSITION  = TARGETED_LINEAGE_OBJECTS_MEASURED__
                      ONE_DIRECTLY_MEASURED_LAW_CONFIRMATION_ELIGIBLE
SELECTED_LAW        = LAW_C_MCTT01   (the exact MCTT01 selected law, directly measured here)
KIND                = CAUSAL CONFIRMATION on fresh disjoint seeds. Not a search, not a calibration.
STATUS              = CREATED, NOT EXECUTED. Authorising it is Tommy's decision.
```

## 0. Two preconditions, before world 1, in this order

**P1 — close the verification gap the independent check found (F-01).** The per-world
reconstruction that produced every number in TLMR01 ran on the owner's machine, because the
bridge could not carry 800 MB of archives into the container after a total rollback. The
cross-check of that path used two archives that turn out to be an extinct world and a single-Y
world: the identity link and the toroidal distance are never called in either, and no episode, no
maturation candidate and no removal exists in either. **The device path is verified for the
archive reader, M1 with zero forks and M4, and is UNVERIFIED for M2, M3, M5, the identity link
and the toroidal distance** — that is, for the entire selection statistic.

Re-measure **at least three `LAW_C_MCTT01` archives with `C_selective_removal_applied = true`**
in a container, with the byte-identical frozen `tlmr01_offline.py`, and diff field for field
including `post_removal_intervals`. Publish tags, seeds and sha256. If they agree, P1 closes and
nothing else changes. **No world of this confirmation runs until it closes.**

**P2 — re-verify the law binding against the owner's copies.** Only `LAW_A_B1` is bit-verifiable
in the container that produced this handoff: `BPRTC01_MASTER_FREEZE.json`,
`MCTT01_SELECTED_LAW.json` and `MCTT01_PHYSICS_DIFF_FROM_B1.json` are absent, so `tlmr01_laws`,
`tlmr01_run` and `tlmr01_seeds` do not import there and
`PARENT_TIP_RESOLVED_FROM_THE_REPOSITORY` is an unverifiable assertion in that container. The
frozen `TLMR01_MEASUREMENT_LAWS.json` carries the sha256 of all four source artefacts. Check all
three against the owner's copies before spending a world.

## 1. What TLMR01 established, and at what ceiling

- **The primary estimand is delivered.** `e(n)` above PTOPD01's occupation support ceiling
  `sI = 5` is DIRECTLY_MEASURED at `LAW_C_MCTT01` in **281 of the 311 strata above the ceiling**,
  the highest at **n = 296**, on 7,317 forks over 1,380,875 single-centre steps across 176 worlds.
  PTOPD01 could not obtain it at all because no archive recorded the exposure denominator.
- **The pooled value 0.0052988 describes no occupancy.** The hazard runs from 0.046 at n ∈ 6–10
  to 0.173 at n ∈ 41–80 and 0.0003 at n ≥ 161, and 86 % of the exposure sits in the top band.
  Use the stratum table, never the pooled number.
- **`s(n) = 0` above separation occupancy 4, at every law.** All 44 + 68 + 46 maturations begin
  at occupancy 2, 3 or 4; **15,252 episodes beginning at n ≥ 5 produced zero maturations**,
  15,243 of them at LAW_C. This replicates PTOPD01's *zero of 3,602 above occupancy 3 at B1
  mobility* and extends it to a law 40× in kY. It is the sharpest constraint you inherit.
- **`P(trigger | matured)`**: 33/68, 19/46, 32/44. At LAW_A and LAW_B the deadline is the
  dominant failure (25 and 26); at LAW_C it never fires and every failure is the local-X ratio.
  The three columns are marginals and can double-count.
- **M5, the integrated rate**: 0/128, 0/128, **22/256** — lower 95 % 0.0589, above the
  endpoint-matched floor `F_INTEGRATED = 0.0032015171041760242`.

Claim ceiling, unchanged: *the named objects have been measured at the laws and occupancies
stated.* No point is qualified.

## 2. The finding that must travel with the selection

The frozen DOTC01 turnover endpoint is **confounded with occupancy**. `D|C` is 22/22 at LAW_C and
0/23 and 0/15 at LAW_A and LAW_B — but at LAW_C the 22 removals leave **2,018** complete
post-removal identity intervals, median 93 per world, 1,813 FUNCTIONAL, so an endpoint asking for
*at least one* is saturated; while LAW_A and LAW_B hold occupancy 1 for 97.7 % and 91.0 % of
their single-centre steps and produce **no** complete post-removal interval at all.

All 44 matured and all 32 triggering LAW_C episodes begin at separation occupancy 2, 3 or 4 —
occupancy-identical to the other two laws. The triggering configurations do not differ. What
differs is the ambient occupancy of the post-removal window.

**There is no no-removal control anywhere in TLMR01's 512 worlds**, so this is an inference, not
a measured contrast. **The confirmation must fix that**: see §3.

## 3. What the confirmation must be

```
SELECTED_LAW_ONLY                      = LAW_C_MCTT01, exactly as measured. No other law.
FRESH_DISJOINT_SEEDS                   = mandatory; disjoint from TLMR01's 512 primary,
                                         6 reserve and the 71xxx fixture band, proved by
                                         enumeration
NO_DESIGN_MISSION_MAY_INTERVENE        = true
NEW_PARAMETER_POINT                    = forbidden
NEW_LAW                                = forbidden
INTERPOLATION                          = forbidden
RESPONSE_SURFACE                       = forbidden
ADAPTIVE_SAMPLE_SIZE                   = forbidden
ADAPTIVE_STOPPING                      = forbidden
POST_OUTCOME_THRESHOLD_CHANGE          = forbidden
MAX_POST_OUTCOME_SCIENTIFIC_REPAIRS    = 0
```

**A matched no-removal control arm is REQUIRED.** The SHAM arm already exists in the inherited
`fmrct01_world.intervene(w, ())` and is proved a bit-exact no-op. Run it on the same seeds, at
the same trigger step, so that the post-removal turnover rate can be compared against the rate in
a window that had no removal. Without that arm the confirmation would inherit exactly the
confound this handoff exists to name.

**The endpoint must be shown to discriminate before it is used.** Publish, before world 1, the
ambient rate of COMPLETE_TURNOVER-satisfying intervals per world at this law's occupancy. If the
endpoint is saturated, the confirmation must declare a discriminating endpoint — for example one
conditioned on occupancy, or one comparing removal against SHAM within the same world — and
freeze it before any world runs. This is a design requirement, not a licence to search endpoints
after seeing outcomes.

**Power.** At the measured lower bound 0.0589 against `F_INTEGRATED`, the exact one-sided 95 %
test reaches 80 % power at **n = 50** worlds. A two-arm design doubles that. Price the SHAM arm
and the engineering in the declared ceiling — the clause ILRR01's Route A failed.

## 4. Gates that carry no information — do not inherit them as evidence

| gate | why it cannot fail |
|---|---|
| `ARCHIVE_DECISION_RECONSTRUCTION` | regroups cells by the component id the online code wrote, so it reproduces the online grouping for any decomposition |
| `ONLY_Y_LAW_FIELDS_DIFFER` | tests a dictionary for having the three keys it was built with |
| `failure_modes.not_exactly_two_centres` | the frozen state S already requires exactly two centres |
| terminators `INTEGRITY_FAULT`, `UNCLASSIFIED` | unreachable by construction |

The replacement for the first, which the independent check supplied and which the successor must
run: at every step, `len(comps) == s.n_components`, component ids contiguous `0..k-1`, and the
sum of component `nY` equal to the world `nY`.

## 5. Clauses inherited at birth — re-emit these verbatim into your own handoff

```
MEASUREMENT_NOT_POINT_SEARCH                             = true
ONE_ZERO_RUN_DETOUR_ONLY                                 = spent — no further finite-size mission
SECOND_FINITE_SIZE_EXTENSION                             = forbidden
NEW_SIZE_LADDER                                          = forbidden
POST_OUTCOME_SIZE_RETUNING                               = forbidden
NEW_PARAMETER_SWEEP                                      = forbidden
GENERIC_CALIBRATION_SUCCESSOR                            = forbidden
INTERPOLATION                                            = forbidden
RESPONSE_SURFACE                                         = forbidden
EVERY_SUCCESSOR_MUST_RE_EMIT_THESE_CLAUSES               = true
REOPENING_FINITE_SIZE_REQUIRES_EXPLICIT_HUMAN_AUTHORISATION = true
MAX_INDEPENDENT_CHECKERS                                 = 1
MAX_REVIEW_CASCADES                                      = 0
CHECKER_RETURN_WRITTEN_BEFORE_ANY_FINDING_IS_ACTED_ON    = mandatory
SECOND_TARGETED_MEASUREMENT_CAMPAIGN                     = forbidden
```

## 6. Vocabulary that remains binding

```
H3_STATUS                                      = NOT_TESTED
REPRODUCTION_STATUS                            = NOT_TESTED
HEREDITY_STATUS                                = NOT_TESTED
AUTONOMOUS_COHESION_STATUS                     = NOT_ESTABLISHED
X_LAWSPEC_BASELINE                             = UNCHANGED
ARCHITECTURE_CHANGE_NECESSITY                  = NOT_ESTABLISHED
FINITE_SIZE_RELEVANCE                          = NOT_SUPPORTED
PTOPD01_LINEAGE_POINT_ROUTE_STATUS             = MEASURED, NOT QUALIFIED
COMPANION_PAPER_V1_1_STATUS                    = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED
```

Forbidden vocabulary unchanged: *organism*, *daughter organism*, *life created*,
*self-replication demonstrated*. The frozen status strings are the only permitted formulation,
in the affirmative and in the negative alike.

---

*Issued by TLMR01 after 512 primary worlds, zero technical failures, zero reserves used, one
independent checker and one adjudication. TLMR01 does not execute it.*
