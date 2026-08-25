# LDFMA01 — PARENT BINDING

```
MISSION           = LOCKED-DAUGHTER-FAILURE-MECHANISM-ARBITRATION-01
SHORT_NAME        = LDFMA01
PARENT            = FIMRCC01, tip 3d67654fc5cfa7e5502c4d7e93b13c090d735263  (resolved, matches)
PARENT_DISPOSITION = CONFIRMATION_PRECONDITIONS_NOT_MET__LINEAGE_ROUTE_PAUSED
NEW_SCIENTIFIC_ENGINE_RUNS = 0
```

## 0. A fifth rollback happened first

Between the close of FIMRCC01 and this launcher the container reverted to the FDOT01 C2 snapshot
(`82f6c84`) for the fifth time, erasing TLMR01, FIMRCC01, `MCTT01/out`, `BPRTC01/out` and every
staged upload. **Nothing was lost permanently.** Restoration cost **572 275 bytes** across the
bridge — two incremental bundles whose prerequisites chain to a commit the snapshot already
contained — after which 18 of 18 FIMRCC01 artefacts verified against their own `SHA256SUMS` and the
working tree was clean at `3d67654`. Details in `LDFMA01_ROLLBACK_INCIDENT_05.json`.

## 1. Bound by exact bytes

**37 artefacts**, zero missing, across nine groups: the TLMR01 final raw package, its final
analysis and selection, its checker and adjudication, and the FIMRCC01 checkpoint, Precondition A,
Precondition B, endpoint adjudication, final report and final disposition. Every sha256 is recorded
in `LDFMA01_PARENT_BINDING.json`.

## 2. Every declared count recomputed, not read

Each figure below was recomputed from the committed **per-world** records — 256 Precondition-A
records, 256 Precondition-B records, 26 descent-audit records — rather than read from the headline
artefact that asserts it.

| quantity | declared | recomputed | |
|---|---|---|---|
| LAW_C primary worlds | 256 | 256 | ✓ |
| triggered worlds | 26 | 26 | ✓ |
| selective-removal worlds | 22 | 22 | ✓ |
| unrestricted ambient-population endpoint | 22/22 | 22/22 | ✓ |
| complete identity intervals | 2 018 | 2 018 | ✓ |
| median complete intervals per removed world | 93 | 93 | ✓ |
| locked-daughter complete-functional events | 1/22 | 1/22 | ✓ |
| locked-daughter world-level events | 1/256 | 1/256 | ✓ |
| `P(K ≥ 2 \| N=50, p=1/256)` | 0.0165 | 0.0165 | ✓ |
| fresh worlds used by FIMRCC01 | 0 | 0 | ✓ |

A second, harder cross-check recomputes the locked-daughter and ambient figures from the *descent
audit* record set — a different implementation on a different pass — and they agree exactly.

## 3. What is preserved, and what is not being claimed

```
TLMR01 ambient-population result =
  VALID DEVELOPMENTAL RESULT FOR A BROADER POPULATION OBJECT
```

The `22/22` is **true**. It says that in every world that received a removal, at least one identity
*somewhere in the world* completed a constituent turnover afterwards. It is **not called false
here and is not being reinterpreted**.

What it does **not** do is measure the locked daughter. The identity the frozen code names as the
daughter satisfies the same endpoint in **1** of those 22 worlds. Those are two different objects
and LDFMA01 exists to explain the gap between them.

```
FIMRCC01 final disposition =
  CONFIRMATION_PRECONDITIONS_NOT_MET__LINEAGE_ROUTE_PAUSED
```

## 4. Standing status, unchanged

```
H3_STATUS                     = NOT_TESTED
REPRODUCTION_STATUS           = NOT_TESTED
HEREDITY_STATUS               = NOT_TESTED
AUTONOMOUS_COHESION_STATUS    = NOT_ESTABLISHED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
X_LAWSPEC_BASELINE            = UNCHANGED
COMPANION_PAPER_V1_1_STATUS   = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED
```
