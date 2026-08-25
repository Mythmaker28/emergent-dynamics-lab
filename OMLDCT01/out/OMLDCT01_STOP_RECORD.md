# OMLDCT01 — STOP BEFORE WORLD 1

```
STOP_CODE   = STOP__PRIMARY_AND_COPRIMARY_DECISION_RULE_INCOMPLETE
WORLDS_RUN  = 0
SEEDS_USED  = 0
ARM_INSTANCES_CONSUMED = 0
```

## What was completed before the gate

**§1 — restoration and parent binding.** A **sixth** container rollback had reset the workspace to
`82f6c84` before this launcher arrived. The three-link Windows chain restored tip
`2101b301a2444a4a825a6cd338a8db7334c53c9f` for **952 079 bytes**; `git fsck --full` exit code 0;
**29 of 29** LDFMA01 artefacts verified against their own `SHA256SUMS`; the checker raw return
hashes to `f93c85a7…`, matching the adjudication. `LDFMA01_WINDOWS_DURABILITY = PASS`. Twenty
artefacts bound by exact bytes, none missing.

**§1 — independent recomputation.** All six declared evidence items reproduce from the 26 committed
per-world records rather than from the artefacts asserting them:

| item | declared | recomputed |
|---|---|---|
| selective-removal worlds | 22 | 22 |
| locked-daughter complete-functional success | 1/22 | 1/22 |
| failures | 21 | 21 |
| dominant failure L3 | 16/21 | 16/21 |
| `SPLIT_OR_TIE` termination | 22/22 | 22/22 |
| ambient = succession | — | 2 017 of 2 018 begin after the daughter identity is gone |

L2 = 5 and L3 = 16 sum to 21, so the partition is exhaustive.

**§2 — law binding.** `LAW_C_MCTT01` verified at the IEEE-754 bit level against the handoff's own
published patterns: `kY 0x3f50763f01e8e5b2`, `muY 0x3f484713dc1c8ab5`,
`p_hop_Y 0x3fba462ec93926a0`. Every shared frozen constant has a byte-verified source.
`NEW_PARAMETER_POINTS = 0`, `X_LAWSPEC_BASELINE = UNCHANGED`.

## Why the mission stops here

Section 2 of the launcher requires the committed handoff to state whether the exposure endpoint is

```
co-primary under an AND rule
hierarchical secondary
or descriptive support
```

and says, in terms: **"Do not invent this relation."**

The committed handoff says only:

> **DECISION RULE.** Wilcoxon signed-rank on the paired log difference, two-sided, α = 0.05, **on
> both the primary and the co-primary**. Declared before world 1 and not revisable.

"On both" says the test is *run* on both endpoints. It does not say what the mission concludes when
they **disagree** — and they can disagree: exposure is the sum of occupancy over the interval while
lifetime counts steps, and occupancy ranged from 1 to 6 across the 22 retrospective daughters.

- Under an **AND rule**, a split verdict is negative.
- Under a **hierarchical** rule, it is positive with the secondary reported.
- Under **descriptive support**, the co-primary never gates at all.

Those are three different experiments with three different terminal verdicts. Choosing between them
now — after I wrote that handoff myself, and with the retrospective data in hand — would be exactly
the silent fixing of a decision rule the launcher's constraints exist to prevent.

## Four other items the handoff does not freeze

Section 5 requires seven things from the handoff. It supplies three and omits four:

| required | present |
|---|---|
| paired statistic | ✓ Wilcoxon signed-rank |
| direction | ✓ two-sided |
| alpha | ✓ 0.05 |
| **primary / co-primary combination** | ✗ |
| **treatment of zero differences** | ✗ |
| **minimum valid pair count** | ✗ |
| **technically-invalid rule** | ✗ |
| **null-result interpretation / equivalence margin** | ✗ |

The launcher's own §15 vocabulary does **not** collapse "not detected" into "no effect" — it
supplies `MATCHED_LOCKED_DAUGHTER_CONTROL_EFFECT_NOT_DETECTED__INCONCLUSIVE_UNDER_FROZEN_POWER` —
so `STOP__TERMINAL_LOGIC_OVERSTATES_A_NULL_RESULT` is **not** triggered. But §5 also requires
`NULL_RESULT_INTERPRETATION = frozen before outcomes`, and the handoff freezes nothing of the kind.

## A correction of my own, recorded

The first run of the completeness check reported "treatment of zero differences: present". The
check used the bare substring `ties`, which matches inside **identities**. That false positive is
corrected above rather than left standing.

## What unblocks it

Five lines from Tommy, added to the handoff and frozen before world 1. Nothing else in the design
changes, and no result has been seen.

```
PRIMARY_AND_COPRIMARY_COMBINATION = <AND | HIERARCHICAL | DESCRIPTIVE_SUPPORT>
ZERO_DIFFERENCE_TREATMENT         = <Pratt | Wilcoxon-drop | exact-sign>
MINIMUM_VALID_PAIR_COUNT          = <n>
TECHNICALLY_INVALID_RULE          = <what makes a pair or the run invalid>
NULL_RESULT_INTERPRETATION        = <equivalence margin, or "inconclusive, no equivalence claim">
```

```
REPRODUCTION_STATUS = NOT_TESTED   HEREDITY_STATUS = NOT_TESTED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED   X_LAWSPEC_BASELINE = UNCHANGED
COMPANION_PAPER_V1_1_STATUS = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED
```
