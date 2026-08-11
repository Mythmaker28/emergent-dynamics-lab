# FCDDH01R — final report

`FRESH_CROSSED_DIFFERENTIAL_DISCOVERY_HOLDOUT_01R`
Branch `dev/fresh-crossed-differential-discovery-holdout-01r`, append-only child of
`93f13f45e6b6550a7ff709768b7b574161ed6a4f`.
Base of this closure: `ffbda326703f93aa5a34c03e5f259e976771f793` (C7).

## Headline

The discovery analysis **was** computed, on twelve fresh, crossed, independent ancestries. The
candidate pattern is numerically identifiable and highly stable under leaving one ancestry out —
but **D4, D5 and D8 fail**. No axis is licensed and the hold-out was never opened. The arithmetic
is mechanically verified. The campaign is **not protocol-conformant**: the frozen executor/DEX
contract was repaired after 48 billed starts.

```
DISCOVERY_ANALYSIS_COMPUTED__AXIS_NOT_LICENSED_D4_D5_D8__ZERO_HOLDOUT_STARTS__PROTOCOL_NONCONFORMANT_POSTSTART_EXECUTOR_REPAIR
```

## 1. Commit chain

| role | commit | UTC |
|---|---|---|
| FCDDH00 parent tip | `93f13f45e6b6550a7ff709768b7b574161ed6a4f` | 05:06:33 |
| C1 reauthorization + master freeze | `e77ef550a04cbf90ba2f90e5083719913bc005a4` | 13:09:10 |
| C2 namespace, roles, randomization | `1936efde316672f3950d249427aec5cb6c6d44b4` | 13:09:13 |
| C3 durable executor, DEX0–16, Q0A–Q0W | `7dd098ea779ddbc241414fb3d7cad8d0d42279b8` | 13:09:28 |
| C4 discovery panel sealed | `b52b1eae820c69be601eaee7d7fa0d4d827eb463` | 13:24:01 |
| C5 post-construction executor repair | `2b152a2ad4f6abf4dc2c932fabff61a368fe1eed` | 13:43:27 |
| C6 threshold lock | `fc1b41f87cadcc94407e5ca70d0fb43a7fcbc968` | 13:51:52 |
| C7 opaque active raw-only lock | `ffbda326703f93aa5a34c03e5f259e976771f793` | 14:00:20 |

Linear, merge-free, 0 merge commits. The reported order
`b52b1eae → 2b152a2a → fc1b41f8 → ffbda326` is **verified from the exact objects**.

`main` = `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77`, unchanged, never checked out, does not contain
`FCDDH01R/`. `CLOSURE_COPY_MAIN_STATUS = EXACT_MATCH`. `PRIOR_ENVIRONMENT_MAIN_STATUS = NOT_OBSERVED`,
`PRIOR_ENVIRONMENT_PROCESS_STATUS = NOT_OBSERVED`. `REMOTE_REPOSITORY_SCOPE = NONE`.

## 2. Start accounting

| phase | charged starts | raw advance sequences |
|---|---|---|
| discovery construction | 48 | 48 |
| discovery sham | 96 | 96 |
| discovery active | 96 | 96 |
| hold-out (all three) | 0 | 0 |
| other / diagnostic / smoke / preflight | 0 | 0 |
| **FCDDH01R total** | **240** | **240** |

Child maximum 672 → **432 unused starts**, closed and non-transferable.
Historical FCDDH00: **108** charged (48 construction + 59 completed sham rows + 1 interrupted billed
sham row). **Cumulative lineage: 348** of a 780 maximum. The three counts are kept separate and
never merged.

On the "59/96" wording: 59 sham rows **completed and published**; a 60th was **launched and billed**.
Both statements are true of different quantities, the committed FCDDH00 closure already recorded 60
charged against 59 completed, and **no append-only correction is required**.

## 3. The two repairs, kept apart

**Prestart — permitted.** DEX13 exposed a real exactly-once defect: concurrent wrappers raced on the
`START_GATE`'s *temporary* file, not merely on its exclusive publication. The temporary is now unique
per claimant; eight simultaneous wrappers for one `RUN_ID` yield exactly one gate winner and exactly
one charge. Repaired **before** the first billed start. This is the class of repair the protocol
allows, and it is why the campaign is mandatory.

**Post-start — not permitted.** Real two-output rows exposed a publication terminal-state defect.
The remedy landed at C5, **after 48 billed starts**. See §6.

## 4. Panel and completeness

12 independent upstream ancestries (73000–73011), 4 descendants each = 48, complete within-ancestry
factorial crossing {NEAR, FAR} × {H3 member 0, 1} from **one byte-identical precursor per quartet**,
12 distinct precursors (max multiplicity 1), mask identity 48/48, one global NEAR blob and one global
FAR blob, uniform 390 engine steps per construction row, 0 construction rejections. Panel
verification: **15/15 PASS**.

* 48 complete construction rows, 96 complete sham rows, 96 complete sealed/published/verified active rows
* 48/48 sham twins bit-identical over the **full horizon** (terminal hash, per-time hashes, touch set; 11 scored times)
* 48 positive, finite `TAU`, independently reproduced by the reference path; range `[7.055948e-04, 1.264019e-03]`
* **no billed incomplete row**; **no replay, replacement or idempotent runner recovery**
* threshold lock `fc1b41f8…` (13:51:52Z) predates every active row (first active gate 13:52:06Z)
* opaque raw lock `ffbda326…` (14:00:20Z) predates the first target-response decoding (14:01:00Z)
* **zero** hold-out byte, lock, axis object, row, score or numerical access
* no 71000-series scientific byte entered the panel in any role

## 5. Generation-1 / generation-2 publication audit

| | construction | sham | active |
|---|---|---|---|
| rows | 48 | 96 | 96 |
| WAL records | 624 | 1056 | 1056 |
| records per row | 13 | 11 | 11 |
| `VERIFIED` records | 144 | 96 | 96 |
| reported monotonicity alerts | 48 | 0 | 0 |
| contract generation | 1 | 2 | 2 |

Generation 1 emitted the row-terminal `VERIFIED` once per *declared output*; construction rows
declare two (`d_<did>.npz`, `m_<did>.npz`). Both outputs were sealed and published for every row,
no recovery happened between them, no row was skipped or duplicated, and repeated mask bytes were
distinguished from distinct precursor bytes by two separate PASS checks.

**Conclusion: a latent recovery weakness without observed raw corruption** — not proven data
corruption, and not a harmless conformant implementation. Under generation 1, a row killed between
output 1's `VERIFIED` and output 2's publication would have been skipped as complete on resume. The
window never opened here. Generation 2 seals all outputs, then publishes all outputs, then emits
exactly one row-terminal `VERIFIED`; `os.replace` is still never used on a final path.

## 6. Protocol conformity

```
PROTOCOL_CONFORMITY_STATUS       = NONCONFORMANT
PRIMARY_DEVIATION                = POST_FIRST_BILLED_START_EXECUTOR_PUBLICATION_CONTRACT_CHANGE
VIOLATED_RULES                   = SECTION_4_SOURCE_FREEZE_AND_STRICT_STOPS_5_AND_OR_11
POST_STOP_SHAM_AND_ACTIVE_STARTS = 192
RETROACTIVE_REPAIR_STATUS        = NOT_POSSIBLE
```

Master freeze §6 makes durable execution a scientific gate; §7 stop 5 forbids DEX or Q0A–Q0W being
*"repaired after the first billed start"* and stop 11 forbids *"post-first-start changes to frozen
source, config, queues, schedules or command templates"*. Both are triggered on their literal
committed text. Stop 5 does not need the "DEX0–DEX16 still PASS" hedge: its wording is about
*repair*, not failure.

The exact C4→C5 diff: 827 added generation-2 DEX evidence files, one added supersession record, four
modified engineering/test modules, one modified preflight report, one modified engineering-delta
document. **Zero scientific paths.** No simulation equation, scientific runner, carrier definition,
reader, mask, horizon, weight, randomization, row schedule, checkpoint, threshold or analyzer
changed. `run_id` does not depend on the executor code hash.

Two judgments, kept separate:

* **Prospective** — this is not a clean compliant preregistered experiment; the programme should
  have stopped after construction. DEX17–DEX19 inform a *future* executor design; they restore
  nothing.
* **Mechanical/numerical** — dependencies, randomization, raw outputs, locks and analyzers were
  identical across the change, so the panel supports a deterministic descriptive calculation.

## 7. Gate ladder D0–D11

| gate | verdict | rule | observed |
|---|---|---|---|
| D0 | PASS | structural anchor | true by construction |
| D1 | PASS | cell materiality on every acquired row | 96/96 |
| D2 | **PASS** | direct carrier contrast `‖z₂−z₁‖² > 4·TAU²` | **48/48** |
| D3 | PASS | `‖X̄_D‖` certifiably > 0 (identifiability) | enclosure strictly positive |
| D4 | **FAIL** | absolute materiality vs `A_X̄` | certified strict failure |
| D5 | **FAIL** | `Σ_b J[b; v_D[−b]] ≥ 10/12` | **0 of 12** |
| D6 | PASS | `min_b alignment²(v_D, v_D[−b]) ≥ 0.80` | 0.9992776839495647 |
| D7 | PASS | `max_b` projected leverage < 0.50 | 0.1386169981190795 (73008) |
| D8 | **FAIL** | deletion sign **and** material margin | sign 12/12, margin 0/12 |
| D9 | PASS | allocation-exchange invariance + co-optimal orbits | 12/12, 0 co-optimal (cap 12) |
| D10 | PASS | production vs independent reference | 96/96 M₂², 96/96 gauge, 48/48 TAU |
| D11 | PASS | trainer dependency + firewall root | forbidden imports = [] |

`DISCOVERY_AXIS_SERIALIZATION_STATUS = NOT_LICENSED__FAILED_GATES=D4,D5,D8`
`HOLDOUT_STATUS = NOT_REACHED_BY_PREDECLARED_STOP`

## 8. The numbers

```
‖X̄_D‖              = 5.695567518165154e-04   (certified enclosure, width 2⁻²⁰⁰)
A_X̄[DISCOVERY]     = 2.924046708945949e-03   (certified enclosure)
ratio               = 0.194783739
floor / signal      = 5.133899
energy ratio        = 0.037940705
min alignment²      = 0.9992776839495647      (LOAO, 12 folds)
max leverage        = 0.1386169981190795      (ancestry 73008)
D5 count            = 0 of 12                 (predeclared criterion 10/12)
```

The amplitude is about **19.5 %** of the inherited operational floor; the floor is about **5.13×**
the signal; the energy is about **0.03794** of the floor energy. The effect is **not** described as
exactly zero.

**D4 is a certified strict failure, not UNRESOLVED.** `upper(‖X̄_D‖) = 5.695568e-04 <
lower(A_X̄) = 2.924047e-03`; the certified intervals are disjoint and one-ulp tight, so no rounding
ambiguity is possible.

**Correction.** `min alignment²` must not be reported as "≥ 0.999278". The exact value
`0.9992776839495647` is below that by 3.16e-07. The correct certified statement is **≥ 0.999277**.
No gate depends on it — D6's threshold is 0.80.

## 9. D5 and D8 anatomy

Both fail on **response materiality**, not on **sign**.

* All 48 full-axis pairing scores are strictly positive: **0 sign reversals**.
* All 48 material margins `p − A_PAIR` are negative: **48/48 fail**.
* D5: all 12 omitted-ancestry signed scores are positive on their own fold axis; every worst-pair
  margin is negative; `Σ_b J = 0`.
* D8 clause 1 (signed deletion mean > 0): **12/12 PASS**, minimum lower bound `5.538464e-04`.
* D8 clause 2 (mean retained worst-pair material margin > 0): **0/12**, margins in
  `[−2.654179e-03, −2.611160e-03]`.
* Co-optimal gauge orbits: **0** (cap 12). Allocation-exchange invariance: 12/12. Production and
  reference agree at `rel 1e-9 / abs 1e-30`.
* Interval status: no gate is UNRESOLVED; D4 and D8 clause 1 are certified, D5 and D8 clause 2 are
  strict integer/sign failures.

**D5 failing alone does not establish allocation fragility.** Here signs do not reverse; only
material margins fail. The orbit is behaviourally stable and sub-material.

**D4, D5 and D8 are not three independent negative results.** They reuse the same inherited
TAU-propagated bounds (`A_X̄`, `A_PAIR`, `A_X`) and are three views of one fact: the interaction
amplitude lies below its inherited operational floor.

The predeclared `10/12` D5 criterion is an internal stability guard — not a p-value, not a
population result.

## 10. Why LOAO stability is not replication

The twelve leave-one-ancestry-out folds share **eleven of twelve** ancestries with the full fit and
with each other. `alignment² ≈ 0.99928` says the estimator does not lurch when one ancestry is
removed. It is **internal estimator stability**, not independent replication and not a hold-out
result. Maximum leverage `0.1386` says no single ancestry dominates the projected estimate; it says
nothing about materiality.

## 11. Strongest supported wording

> Across 48 descendants nested within twelve independent ancestries, the direct carrier contrast
> mechanically satisfies its inherited materiality gate, while its NEAR-versus-FAR modulation yields
> a numerically identifiable and internally stable but sub-material discovery pattern. Because the
> executor contract changed after billed starts, this is a deterministic descriptive result, not a
> clean prospective confirmation. It does not clear the inherited materiality and worst-pair gates;
> no scientific axis is licensed and no independent hold-out validation occurred.

Not supported: that the axis replicated; that a population direction was proven; that this is a
clean preregistered negative; that no physical interaction exists; that a second material dimension
was found. No population, causal-transfer, individuality, life, memory or agency claim follows.

## 12. Axis and hold-out

No official axis object was created. Any diagnostic vector appearing in a gate report (`v_D`,
`v_fold`) is an **unlicensed discovery calculation** and is not exposed through the canonical axis
loader or path. Zero hold-out starts is the **correct** outcome of the predeclared stop: the axis
was never licensed, so there was nothing to validate, and opening the hold-out would have burned
irreplaceable ancestries against an unlicensed direction.

## 13. Protocol fields carried forward

```
FCDDH01R_NO_LOOK_RETRY_LICENSE = PASS      (0 target-response looks, 0 confirmatory tests, 0 alpha
                                            spent in FCDDH00; 341 committed parent paths enumerated)
FCDDH01R_RANDOMIZATION_LICENSE = NOT_REBUILT_AT_CLOSURE__NO_CONSUMER
SEED_NAMESPACE                 = N = 73000; discovery 73000–73023 (12 used), hold-out 73024–73055 (0 used)
                                 72000 rejected: the FCDDH00 closure itself exposed "N ≥ 72000"
PARENT_IDENTITY                = 1392 / 1392 execution-tree paths byte-identical, 0 mismatches
OWNER_REPORTED_PARENT_VALUES   = all verify EXCEPT the FCDDH00 authorization SHA-256
```

## 14. Existing DEX interruption-safety evidence

Verified from the committed tree; **no new test was run**. Generation-2 campaign: **20/20 PASS**,
`REAL_ENGINE_CONSTRUCTOR_COUNT = 0`, `REAL_ENGINE_ADVANCE_COUNT = 0`, 0 charged starts, dummy worker
engine-free (imports only `__future__`, `hashlib`, `json`, `os`, `sys`, `time`). DEX17 (kill inside
the publication window), DEX18 (multi-output WAL monotone), DEX19 (kill after seal-all, before
publish-all) all PASS. `Q0A–Q0W` **23/23 PASS**, non-vacuous, 0 engine starts, all 11 negative
controls fire.

DEX0 is the load-bearing one: the launch template kept its PID, start identity and heartbeat across
a deliberate expiry at the same 120-second bounded-call boundary that killed FCDDH00, and completed
all ten dummy rows afterwards; a second trial killed the whole launcher process group with the same
result.

This evidence shows the generation-2 repair **works**. It cannot retroactively satisfy the prestart
engineering gate and cannot restore conformity.

## 15. Missing or ineligible artifacts

* `FCDDH01R_RANDOMIZATION_LICENSE` — `NOT_REBUILT_AT_CLOSURE__NO_CONSUMER` (D-6)
* official axis object — `NOT_GENERATED_BY_PREDECLARED_STOP`
* every hold-out deliverable — `NOT_GENERATED_BY_PREDECLARED_STOP`
* fold-axis four-pair breakdown — `PERSISTED_AS_SUMMARY_ONLY` (D-10)
* `HANDOFF_FCDDH01R_FINAL_RECORD_REVIEW.md` — absent from the workspace; declared digest not
  verifiable and not claimed verified (D-11)

Full inventory: `FCDDH01R_PROTOCOL_DEVIATIONS.md` (D-1 … D-11) and `FCDDH01R_MANIFEST.json`.

## 16. Future eligibility (descriptive only — starts nothing)

The fixed-support, allocation-averaged `NEAR−FAR × carrier` interaction fails its inherited
materiality gate. That does **not** negate the separately passing direct-carrier contrast (D2,
48/48). Adding blocks does not automatically repair an averaged minimum-effect criterion. No
immediate rerun, dose change, third carrier, alternate axis or threshold change follows from this
record.

Two things *could* become eligible under a **distinct future task**: a zero-simulation anatomy of the
existing `A_X` rule, and/or a separately pre-analysis-locked exploratory full-field audit. An `A_X`
audit would first have to classify `A_X` as a minimum-effect criterion, an uncertainty envelope, a
mixed operational bound, or unresolved — exact twin shams do **not** reduce a minimum-effect
criterion to zero, and sharper joint error propagation would be methodological only. A future
full-field audit would need one frozen primary physical estimand, fixed times and weights, an
active-blind threshold, and multiplicity control if several endpoints were unavoidable. **No future
audit can reclassify FCDDH01R**, and any positive claim would require fresh prospective validation.
An ancestry-level calibrated P2 population estimand remains an orthogonal scientific question and is
not part of this record.
