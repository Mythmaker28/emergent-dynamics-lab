# FCDDH01R — protocol-conformity corrigendum (append-only)

Written at 2026-08-11T17:15:05Z during an offline record review of the existing FCDDH01R evidence.
Base commit: `ffbda326703f93aa5a34c03e5f259e976771f793` (C7, the opaque active raw-only lock).
No earlier commit is amended, rebased or edited. Nothing below changes a scientific value.

---

## 1. What this corrigendum corrects

The committed FCDDH01R prose — chiefly `FCDDH01R_ENGINEERING_DELTA.md` amendment 1 and
`FCDDH01R_EXECUTOR_CODE_SUPERSESSION.json` — describes the post-construction executor repair as
*"the one and only class of change the owner reauthorization permits"*. That statement is true
about the **class** of change and false about its **timing**, and the committed record does not
anywhere draw the timing conclusion. This corrigendum draws it.

## 2. The finding

```
PROTOCOL_CONFORMITY_STATUS = NONCONFORMANT
PRIMARY_DEVIATION          = POST_FIRST_BILLED_START_EXECUTOR_PUBLICATION_CONTRACT_CHANGE
VIOLATED_RULES             = SECTION_4_SOURCE_FREEZE_AND_STRICT_STOPS_5_AND_OR_11
POST_STOP_SHAM_AND_ACTIVE_STARTS = 192
RETROACTIVE_REPAIR_STATUS  = NOT_POSSIBLE
```

The committed `FCDDH01R_MASTER_FREEZE.md` §6 makes durable execution a **scientific gate**: *"No
engine may start until the chosen mechanism proves DEX0–DEX16 with dummy fixtures only."* Its §7
stop list then contains, verbatim:

* stop 5 — *"DEX or Q0A–Q0W failed, skipped, vacuous or **repaired after the first billed start**"*
* stop 11 — *"**post-first-start changes** to frozen source, config, queues, schedules or command
  templates"*

Both are triggered on their literal committed text:

| | evidence |
|---|---|
| first billed start | `START_GATE` 2026-08-11T13:10:32Z (DISCOVERY_construct) |
| 48 billed construction starts complete | 13:11:57Z |
| panel sealed and committed | `b52b1eae…` at 13:24:01Z |
| **frozen executor source changed** | `2b152a2a…` at **13:43:27Z** |
| 96 sham starts | 13:44:00Z – 13:46:59Z |
| 96 active starts | 13:52:06Z – 13:54:53Z |

`DURABLE_PHASE_SUPERVISOR.py` moved from `138334612d…` to `310aa162a2…` and
`EXACT_ONCE_PHASE_STATE_MACHINE.py` from `a9cd877a84…` to `cfcb8b3dfa…` — frozen source under the
§6 gate, changed after 48 billed starts (stop 11). `DEX12`'s and `DEX4`'s assertions were replaced
and `DEX17`–`DEX19` were added in the same commit — the DEX campaign repaired after the first
billed start (stop 5). Stop 5 does **not** need the "DEX0–DEX16 still PASS" hedge: its committed
wording is about *repair*, not about *failure*.

**192 sham and active starts were acquired after the point at which the programme should have
stopped.** They are billed, recorded, and not deniable.

## 3. What is NOT corrected

The change touched **no scientific dependency**. The exact `b52b1eae…..2b152a2a…` diff is 827 added
generation-2 DEX evidence files, one added supersession record, and six modified files: four
engineering/test modules, one preflight report, one engineering-delta document. Zero paths under
`_work/`, `_plans/` or `_ledger/`; zero locks, manifests, archives, panel files, schedules,
thresholds or analyzers. `run_id` does not depend on the executor code hash, so no charged row
changed identity.

The numerical result therefore stands as a **deterministic descriptive calculation**. It is not
rescued, not reinterpreted, and not promoted to a prospective confirmation.

## 4. Documentation corrections (metadata only)

1. **`FCDDH01R_DEPENDENCY_FIREWALL_REPORT.md` is stale for four engineering modules.** Committed at
   C3 and never re-issued, its *Module hashes* section still lists the generation-1 digests of
   `DURABLE_PHASE_SUPERVISOR.py`, `EXACT_ONCE_PHASE_STATE_MACHINE.py`, `fr_dex.py` and
   `fr_dummy.py`. All sixteen **scientific** module hashes in that file remain byte-correct at C7.
   The C3 file is not edited; the corrected values are recorded in
   `FCDDH01R_SCIENTIFIC_DEPENDENCY_AND_PAYLOAD_IDENTITY_AUDIT.json`.

2. **`MIN_FULL_VS_LOAO_ALIGNMENT_SQUARED` must not be reported as "≥ 0.999278".** The exact
   committed minimum is `0.9992776839495647`, which is **below** 0.999278 by 3.16e-7. The correct
   certified statement is `min alignment² = 0.9992776839495647 ≥ 0.999277`. Rounding the value to
   six decimals and then asserting `≥` overstates it. No gate depends on this: D6's threshold is
   0.80.

3. **`FCDDH01R_DISCOVERY_ACTIVE_RAW_LOCK.json` carries `artifact = "FCDDH00_DISCOVERY_ACTIVE_RAW_LOCK"`
   while `programme = "FCDDH01R"`.** Inherited field naming, consistent with the master freeze's
   incorporation of FCDDH00 objects *by committed identity*. No scientific consequence; recorded so
   the label is never read as provenance.

4. **`FCDDH01R_RANDOMIZATION_LICENSE` was never rebuilt at closure.** Master freeze §5 requires it
   to be rebuilt from new-panel evidence at closure. The original execution stopped before closure.
   Rebuilding it now would be an analysis change, which this review is not licensed to make. It is
   therefore recorded as `NOT_REBUILT_AT_CLOSURE__NO_CONSUMER` — no exact-T p-value was computed, no
   randomization inference was drawn, and the axis is not licensed, so the license has no consumer.

## 5. Two judgments, kept separate

**Prospective status.** This is not a clean compliant preregistered experiment. The historical
programme should have stopped after construction. DEX17–DEX19 are useful evidence for a *future*
executor design; they do not restore confirmatory status.

**Mechanical / numerical integrity.** Scientific dependencies, randomization, raw outputs, locks and
analyzers remained identical across the change, and the completeness, twin-identity, reference-
agreement and firewall checks all pass. The discovery panel supports a deterministic descriptive
calculation.

Mechanical completeness does not erase the freeze violation. The freeze violation does not
invalidate the arithmetic. Both are in the record.

## 6. Composite disposition

```
DISCOVERY_ANALYSIS_COMPUTED__AXIS_NOT_LICENSED_D4_D5_D8__ZERO_HOLDOUT_STARTS__PROTOCOL_NONCONFORMANT_POSTSTART_EXECUTOR_REPAIR
```

Original prospective gate fields are unchanged. This corrective record adds an evidence/compliance
qualifier and nothing else.
