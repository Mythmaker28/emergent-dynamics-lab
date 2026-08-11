# FCDDH00 — ENGINE START BUDGET AND WRITE-AHEAD SPECIFICATION

Derived **statically from the exact committed runner**. No physics instantiated, **no timing
probe, no smoke test** — the authorization permits zero diagnostic starts and this programme
performs none.

## 1. Exact operation ledger

| term | value | reason |
|---|---|---|
| `C_PRECURSOR_ADVANCE` | **0** | PRECURSOR(S) = seed_state(SPEC,TRACER,S,'random') draws from numpy.random.default_rng(S) and performs zero engine steps; domc_core.found(S) only multiplies it by the explicit geometry mask. A pure read/draw costs zero. |
| `C_NEAR_A0_DESCENDANT_ADVANCE` | 1 | one fresh process, one raw advance sequence of 390 engine steps (150 founding + 120 history + 120 settle) |
| `C_NEAR_A1_DESCENDANT_ADVANCE` | 1 | idem |
| `C_FAR_A0_DESCENDANT_ADVANCE` | 1 | idem |
| `C_FAR_A1_DESCENDANT_ADVANCE` | 1 | idem |
| separately state-advancing qualification operations | **0** | `wsfscrp_core.t0_masks, wsfscrp_core.reference_masks, wsfscrp_core.B_of, np.isfinite, wsfscrp_core.save, hashlib.sha256` are pure reads/hashes and cost zero |
| **`C_BLOCK_ACTUAL`** | `0 + 1 + 1 + 1 + 1 + 0` = **4** | |
| `C_SETUP_D`, `C_SETUP_H` | 0, 0 | no setup operation of either phase instantiates and advances physics |

```
N_D_ATTEMPT = floor((96  - 0) / 4) = 24   (>= 12 required: True)
N_H_ATTEMPT = floor((128 - 0) / 4) = 32   (>= 16 required: True)
ENGINE_START_LEDGER_STATUS = BUDGET_FEASIBLE
```

Per descendant the sham phase costs 2 starts and the active phase
2 starts. `PHASE_CONSTRUCTION_CHARGE = C_SETUP_ACTUAL + sum over
attempted candidates of C_BLOCK_ACTUAL`. **The budget uses `max(charged process starts, raw
advance sequences)`**, which here are equal by construction: one fresh process per raw advance
sequence.

## 2. The write-ahead contract

1. an `INTENDED` record is written **and fsynced** before any launch;
2. the child writes an **ACK** marker (its own process identity) as its first action, before any
   engine import or instantiation, and fsyncs it;
3. the child writes an **ADVANCE** marker, and fsyncs it, immediately before its **first** engine
   step;
4. a start is **CHARGED** iff the ADVANCE marker exists, or the launch outcome is uncertain;
5. a start is **not** charged, and may be retried, **only** when the idempotency record proves
   that no engine was instantiated and no state advanced (ACK without ADVANCE, or neither) and no
   output file was produced;
6. every charged start is permanent: never replayed, never replaced, never resumed;
7. a launch is refused outright once the phase would exceed its hard maximum.

For the acquisition phases the launcher `fh_aworker.py` writes both markers and then `os.execv`s
into the **unchanged committed parent worker** `FWL2CF00/fw_worker.py`, replacing its own process
image, after checking that worker's SHA-256 and git blob id. There is therefore exactly one
process per start, running the committed carrier executable path byte-for-byte. Writing ADVANCE
before the exec is deliberately conservative: it can only over-charge a deterministic pre-flight
failure, never under-charge an engine advance.

## 3. Worked examples (persisted)

### pre_launch_transport_failure

{
 "sequence": [
  "INTENDED written and fsynced",
  "process control failed before exec",
  "ack marker ABSENT",
  "advance marker ABSENT",
  "no output file"
 ],
 "charged_process_starts": 0,
 "raw_advance_sequences": 0,
 "retry_permitted": true,
 "why": "the idempotency record proves no engine was instantiated and no state advanced"
}
### uncertain_launch

{
 "sequence": [
  "INTENDED written and fsynced",
  "subprocess raised or timed out",
  "ack marker present or unreadable",
  "advance marker unreadable"
 ],
 "charged_process_starts": 1,
 "raw_advance_sequences": 1,
 "retry_permitted": false,
 "why": "an uncertain launch is charged and never replayed"
}
### complete_block

{
 "sequence": [
  "4 descendant workers, each INTENDED -> ack -> advance -> published output"
 ],
 "charged_process_starts": 4,
 "raw_advance_sequences": 4,
 "retry_permitted": false,
 "why": "C_PRECURSOR_ADVANCE = 0 (the precursor is a pure seeded draw with zero engine steps); each of the four descendants is one fresh process and one raw advance sequence of 150 + 120 + 120 = 390 engine steps; admissibility is a pure read"
}
### candidate_failing_on_the_fourth_descendant

{
 "sequence": [
  "precursor (0 advances)",
  "descendant 1 ok",
  "descendant 2 ok",
  "descendant 3 ok",
  "descendant 4 rejected on admissibility"
 ],
 "charged_process_starts": 4,
 "raw_advance_sequences": 4,
 "retry_permitted": false,
 "why": "the precursor plus the advances actually performed are charged; the block is rejected whole and never resumed"
}

## 4. Hard maxima and authority

```
discovery : construction <= 96   sham <= 96    active <= 96    (total <= 288)
hold-out  : construction <= 128  sham <= 128   active <= 128   (total <= 384)
programme : <= 672
OTHER_OR_DIAGNOSTIC_STARTS_AUTHORIZED = 0     POST_PANEL_SHAM_RETRIES_AUTHORIZED = 0
ACTIVE_RETRIES_AUTHORIZED = 0                 REPLACEMENT_AFTER_FIRST_SHAM = false
REPLACEMENT_AFTER_FIRST_ACTIVE_BYTE = false
```

Unused authorized starts are recorded separately at closure: **authority is not an obligation to
spend.**
