# FCDDH01R — protocol deviations

Complete inventory. Every entry is stated against the committed `FCDDH01R_MASTER_FREEZE.md`.

```
PROTOCOL_CONFORMITY_STATUS       = NONCONFORMANT
PRIMARY_DEVIATION                = POST_FIRST_BILLED_START_EXECUTOR_PUBLICATION_CONTRACT_CHANGE
VIOLATED_RULES                   = SECTION_4_SOURCE_FREEZE_AND_STRICT_STOPS_5_AND_OR_11
POST_STOP_SHAM_AND_ACTIVE_STARTS = 192
RETROACTIVE_REPAIR_STATUS        = NOT_POSSIBLE
```

## D-1 — PRIMARY. Frozen executor / publication contract changed after the first billed start

| | |
|---|---|
| when | commit `2b152a2a…`, 2026-08-11T13:43:27Z |
| after | 48 billed construction starts (first `START_GATE` 13:10:32Z, last 13:11:57Z) |
| what | `DURABLE_PHASE_SUPERVISOR.py` `138334612d…` → `310aa162a2…`; `EXACT_ONCE_PHASE_STATE_MACHINE.py` `a9cd877a84…` → `cfcb8b3dfa…` |
| also | `DEX12` and `DEX4` assertions replaced; `DEX17`–`DEX19` added; `fr_dex.py`, `fr_dummy.py` changed |
| rules | master freeze §6 (durable execution is a scientific gate) and §7 stops 5 and 11 |
| consequence | 96 sham + 96 active = **192 starts acquired after the stop** |
| repairable | **NO.** A freeze violation cannot be undone after the fact. |
| scientific reach | **NONE.** Zero paths under `_work/`, `_plans/`, `_ledger/`; no lock, manifest, archive, panel file, schedule, threshold or analyzer touched. `run_id` does not depend on the executor code hash. |

Stop 5 is triggered on its literal committed wording — *"DEX or Q0A–Q0W … repaired after the first
billed start"* — and does not depend on whether DEX0–DEX16 remained PASS. Stop 11 is triggered
directly. Both are recorded.

## D-2 — Test assertions changed after observing a failure

Declared by the executor rather than quietly amended, which is the right handling; the timing is
still post-start.

* `DEX12` — its expectation encoded the old contract; replaced by a strictly stronger one.
* `DEX4` — a fixed three-second sleep replaced by a bounded 45 s poll after the refusal marker was
  found on disk, written after the old window closed. The invariant held; the assertion was
  load-dependent.

## D-3 — Latent generation-1 publication defect, no observed corruption

`PhaseLedger.publish_raw` emitted the row-terminal `VERIFIED` once per declared output. The 48
construction rows each declare two, producing 48 reporter monotonicity alerts.

* Both outputs were sealed and published for every row (96 `RAW_SEALED`, 96 `RAW_PUBLISHED`).
* Zero recoveries happened between them; zero supervisor restarts; zero `os.replace` on a final path.
* No row was skipped or duplicated — 48 distinct `run_id`s, 48 gates, gate set = run-id set.
* Repeated mask bytes were correctly distinguished from distinct precursor bytes: the panel
  verification checks within-quartet mask identity (48/48) and across-ancestry precursor
  distinctness (12, max multiplicity 1) as two separate checks, both PASS.

**Precise conclusion: a latent recovery weakness without observed raw corruption.** Neither proven
data corruption nor a harmless conformant implementation.

## D-4 — One owner-reported parent value does not verify

`REPORTED_ORIGINAL_FCDDH00_AUTHORIZATION_SHA256 = f4312234…` vs
`COMMITTED_ORIGINAL_FCDDH00_AUTHORIZATION_SHA256 = 9dcdd47a…`. 22 declared serializations of the
committed verbatim text reproduce neither. Characters were lost in delivery; the committed text is
the message *as received by the executor*. Identity is established by content, not by digest.
Touches no normative hash, formula, gate, code lock, seed role, budget or claim. **Did not require a
stop.** Detail: `FCDDH01R_REPORTED_PARENT_DISCREPANCY.json`.

## D-5 — Declared self-corrections inside the panel verification

One check was mis-specified by the executor (`CARRIER_COUNTS_TWO_AND_TWO`, which confused the two
carrier *conditions* with the carrier mask *sizes*) and was corrected to
`CARRIER_MASKS_NON_DEGENERATE_AND_B_EXACT_POSITIVE` **before any target-response access**. No datum,
artifact or engine start changed. Declared in the artifact itself.

## D-6 — `FCDDH01R_RANDOMIZATION_LICENSE` never rebuilt at closure

Master freeze §5 requires it to be rebuilt from new-panel evidence at closure. The original
execution stopped before closure, and this review may not perform an analysis change. Recorded as
`NOT_REBUILT_AT_CLOSURE__NO_CONSUMER`: no exact-T p-value was computed, no randomization inference
was drawn, and the axis is not licensed, so nothing depends on it.

## D-7 — Documentation staleness (metadata only)

`FCDDH01R_DEPENDENCY_FIREWALL_REPORT.md`, committed at C3 and never re-issued, still lists the
generation-1 digests of the four engineering modules changed at C5. All sixteen **scientific**
module hashes in it remain byte-correct at C7. Corrected values are recorded in
`FCDDH01R_SCIENTIFIC_DEPENDENCY_AND_PAYLOAD_IDENTITY_AUDIT.json`; the C3 file is not edited.

## D-8 — `MIN_FULL_VS_LOAO_ALIGNMENT_SQUARED` reported as "≥ 0.999278"

The exact committed minimum is `0.9992776839495647`, below 0.999278 by 3.16e-07. The correct
certified statement is `≥ 0.999277`. No gate depends on it (D6's threshold is 0.80). Corrected here
and in `FCDDH01R_INDEPENDENT_SEMANTIC_VERIFICATION.json`.

## D-9 — Two stale phase locks preserved, not committed

`_ledger/DISCOVERY_active/phase.lock` and `_ledger/DISCOVERY_sham/phase.lock` are exclusive-flock
markers left by supervisor processes of the prior, unobservable execution environment
(`cwd = /home/claude/sweep/FCDDH01R`). They are process artifacts, outside the closure allowlist.
Left on disk untouched: preserved, inventoried, neither committed nor deleted. The corresponding
`DISCOVERY_construct/phase.lock` *is* committed at C7; that asymmetry is inherited and not repaired
here. Campaign status is judged from `status/PHASE_COMPLETE` on all three phases, not from the locks.

## D-10 — Fold-axis pair breakdown persisted as summary only

`fh_disc.py` computed the four per-pair scores on every fold-trained axis but persisted only the
fold summary (`J` and the worst margin). The four pairing scores and their `A_PAIR` floors are
persisted for the **full-discovery** axis only. Recovering the fold-axis breakdown would require
re-running the trainer over the raw archive — an analysis change, out of scope. Recorded in
`FCDDH01R_D5_D8_ANATOMY.json` as
`PERSISTED_AS_SUMMARY_ONLY__FOLD_AXIS_PAIR_BREAKDOWN_NOT_RECOVERABLE_WITHOUT_A_DECODE`.

## D-11 — Handoff document absent from the workspace

`HANDOFF_FCDDH01R_FINAL_RECORD_REVIEW.md` (declared SHA-256 `6d140449…`) is present neither in the
session uploads, nor in the working tree, nor in any tree object reachable from any ref. Its
declared digest could not be checked and is **not** claimed verified. The review's requirements were
taken from the task text, which reproduces them in full.

---

## Deviations explicitly NOT found

* no billed incomplete row
* no simulation-row replay, replacement, or idempotent runner recovery
* no hold-out byte, lock, axis object, row, score or numerical access
* no 71000-series scientific byte in the panel in any role
* no total above 240 FCDDH01R charged starts
* no raw / archive / gate / reference mismatch
* no official axis serialized despite the failed gates
* no threshold lowered, replaced, recalibrated or retrospectively reinterpreted
* no change to `main`, to any parent, or to any raw byte
* no remote repository operation of any kind
