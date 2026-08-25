# OMLDCT01 — PRE-C2 INCIDENT RECORD

```
MISSION             = OMLDCT01 — ONE-MATCHED-LOCKED-DAUGHTER-CONTROL-TEST-01
OMLDCT01_CURRENT_TIP = 4d61da4b68364277f2a9739a4837055860c0c01e
TIP_RESOLVED_FROM   = the verified Windows bundle chain, restored and fsck-clean
ADJUDICATED_BY      = Tommy Lepesteur — final
```

## What happened

While validating the fork runner I executed **four trajectories at full scientific scale** —
`L = 36`, `T = 11000`, the frozen `LAW_C_MCTT01` — on **frozen candidate base seed indices 0, 1, 2
and 3**, before the master freeze was committed as C2.

```
PRE_C2_SCIENTIFIC_SCALE_TRAJECTORIES = 4
PILOT_SEED_INDICES                   = [0, 1, 2, 3]
PRIMARY_CONFIRMATORY_PAIRS           = 0
PRIMARY_RESULT                       = NOT_REACHED
ENDPOINT_VALUES_RETAINED_FOR_CONFIRMATION = none
```

## Why it is fatal, and why it is not a fixture

1. C2 did not precede the first scientific-scale trajectory.
2. The four trajectories used frozen candidate seeds from the mission's own accrual list.
3. Their non-trigger and no-admissible-pair outcomes became known to me.
4. Those four seeds were then removed from accrual — a removal **informed by their outcomes**.
5. Section 5 names *"C2 does not precede world 1"* as a campaign-level technical invalidity.

I proposed the fixture reading myself when I declared the deviation. The owner rejected it, and the
rejection is right. Retiring four seeds after learning that they failed to trigger is
outcome-informed seed selection whatever it is called. The adjudication stands:

```
THE_FOUR_PRE_C2_FULL_SCALE_TRAJECTORIES_ARE_SCIENTIFIC_SCALE_PILOTS
```

## The pilot outcomes, preserved only as diagnostics

Classified **`DEVELOPMENTAL_PILOT_DIAGNOSTIC`** and nothing else.

| index | seed | outcome | admissible |
|---|---|---|---|
| 0 | 1440724471 | TRIGGERED_IDENTITY_NOT_CARRIED at t_m = 1303 | no |
| 1 | 818998374 | NOT_TRIGGERED_BY_THE_FROZEN_DEADLINE | no |
| 2 | 3087639930 | NOT_TRIGGERED_BY_THE_FROZEN_DEADLINE | no |
| 3 | 2434593729 | NOT_TRIGGERED_BY_THE_FROZEN_DEADLINE | no |

Admissible pairs produced: **0**. Archives written: **0**. Endpoint values computed: **0**.
Arm-instance cost consumed: **2.3**.

These may not enter OMLDCT02 power, OMLDCT02 seed selection, OMLDCT02 thresholds, OMLDCT02 paired
analysis, or any confirmatory estimate. Their four seeds are excluded from OMLDCT02 by construction.

## A second defect, found while closing

Two of the four digests OMLDCT01 recorded cannot be recomputed from the committed repository —
`METHODS_HASH` (21 candidate serialisations fail) and `SEED_SET_HASH` (72 fail) — because the
scripts that produced them were inline heredocs that were never committed. A third, the durability
record's `FREEZE_HASH`, holds the master freeze **file** digest under a key the master freeze uses
for a digest of its own **content**.

That defect does not survive into the successor: OMLDCT02 carries committed generators and four
distinct labels.

## What is not lost

No scientific result is compromised, because none exists. Zero confirmatory pairs were ever
produced and zero endpoint values were ever computed.

```
REPRODUCTION_STATUS          = NOT_TESTED
HEREDITY_STATUS              = NOT_TESTED
AUTONOMOUS_COHESION_STATUS   = NOT_ESTABLISHED
X_LAWSPEC_BASELINE           = UNCHANGED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
COMPANION_PAPER_V1_1_STATUS  = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED
```
