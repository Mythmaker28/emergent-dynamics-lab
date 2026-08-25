# FIMRCC01 — PRECONDITION B RESULT

**Independent offline reconstruction of the endpoint, from raw physical inputs only.**

```
MISSION            = FIMRCC01
SECTION            = 3, completed under the owner's closure instruction
PRECONDITION_B     = PASS
FRESH_WORLDS_RUN   = 0
```

## 1. What was required

Two offline classifiers of the same archives. The second must reach every load-bearing quantity
without consulting anything the online code decided. The owner's closure instruction extended the
requirement beyond the original M2 / M3 / M5 / event-step agreement to the **naming itself**: which
of the two components at the trigger is the daughter, whether the selective removal was faithful,
what the X function did on either side of the turnover, what the competing terminal events were,
and what the world-level locked-daughter verdict is.

**Not used as an input anywhere:** the online component id, the online identity id, the online
selected-daughter id, the online trigger verdict, the online maturation verdict, the online
turnover verdict, the online M5 verdict, the online terminal label.

**Used as inputs:** the cell rows (`t`, `y`, `x`, per-cell Y occupancy), the world Y total, the
Y-birth / Y-death / X-birth ledgers, the toroidal geometry, the frozen centre rule, the frozen
FMRCT01 descent rule, and the intervention ledger's step and cell list — the last only to locate
the removal in time and to audit its fidelity, never to decide which component is the daughter.

## 2. Pass 1 — all 256 LAW_C archives

| quantity | result |
|---|---|
| worlds compared | **256** |
| steps compared | **2 816 000** |
| episodes compared | **16 368** |
| component count agrees at every step | 256 / 256 |
| episodes agree | 256 / 256 |
| M2 agrees | 256 / 256 |
| M3 agrees | 256 / 256 |
| M5 agrees | 256 / 256 |
| event step agrees | 256 / 256 |
| fast component algorithm vs explicit union-find | 20 609 sampled steps, **0** disagreements |

## 3. Pass 2 — the naming itself, on the 26 triggered worlds

The parent/daughter naming is defined only where a trigger occurred. For the other 230 worlds the
independent reconstruction returned `NOT_TRIGGERED` in pass 1, with M3 and the event step agreeing
in all 256.

| check | result |
|---|---|
| world-level verdict | **26 / 26** |
| event step `t_m` | **26 / 26** |
| daughter cell set | **22 / 22** |
| parent cell set | **22 / 22** |
| all checks together | **26 / 26** |

Independent verdicts: `TRIGGERED_AND_SELECTIVE_REMOVAL_APPLIED` 22, and
`TRIGGERED_IDENTITY_NOT_CARRIED__NO_REMOVAL` 4.

### Selective-removal fidelity, audited rather than trusted

| check | result |
|---|---|
| Y conserved (`before − removed = after`) | 22 / 22 |
| WY gained equals Y removed | 22 / 22 |
| parent cells emptied | 22 / 22 |
| daughter occupancy untouched | 22 / 22 |
| generator hash unchanged across the call | 22 / 22 |

### The locked-daughter endpoint, on the independently named daughter

| | |
|---|---|
| COMPLETE | **1 / 22** |
| FUNCTIONAL | **1 / 22** |
| reproduces Precondition A | yes |
| ambient endpoint FUNCTIONAL | 22 / 22 |
| ambient complete intervals, total | 2 018 |
| daughter life after `t_m` | min 31, median 230, max 1 472 steps |

## 4. Two things the reconstruction surfaced

**The literal MRCI01 clause 4 is degenerate at this law.** In **26 of 26** triggered worlds the
literal reading returns `DESCENT_AMBIGUOUS_BOTH_INSIDE_CORE_R`. FMRCT01 documented this as its
reason for the frozen rule and measured it on FDOT01's archives; it is now measured at LAW_C and
it is total.

**The frozen trigger's terminal descent fields are the wrong ones.** They keep being overwritten
at every later 1→2 transition, so their terminal value names the last separation in the
trajectory, not the one that named this parent. Terminal and at-trigger values differ in **25 of
26** worlds. TLMR01 recorded the defect; this reconstruction snapshots the naming *as of* the
trigger step, as the online code does when it fires.

**A defect of my own, recorded rather than smoothed.** The first version of this module read the
terminal values instead of the at-trigger ones and disagreed with the archive on world
`P_i001_s1474284807`. The cause was that bug in the reconstruction, not a data disagreement. It is
recorded here.

## 5. Verdict

```
CONFIRMED_LOAD_BEARING_DISAGREEMENTS = 0
DISAGREEING_WORLDS                   = none
PRECONDITION_B                       = PASS
```

The independent reconstruction **agrees** on the load-bearing locked-daughter endpoint. The
disposition is therefore not `FIMRCC01_TECHNICALLY_INVALID`, and the human-selected disposition A
is not being forced through a technical defect: there is no technical defect.

```
H3_STATUS                    = NOT_TESTED
REPRODUCTION_STATUS          = NOT_TESTED
HEREDITY_STATUS              = NOT_TESTED
AUTONOMOUS_COHESION_STATUS   = NOT_ESTABLISHED
X_LAWSPEC_BASELINE           = UNCHANGED
```
