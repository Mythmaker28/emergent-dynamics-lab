# FCDDH01R durable executor specification

## Contract (four parts, nothing more is claimed)

```
EXACTLY_ONCE_LAUNCH_AUTHORIZATION
AT_MOST_ONCE_ENGINE_ADVANCE
EXACTLY_ONCE_OPAQUE_RAW_PUBLICATION
NO_REPLAY_AFTER_UNCERTAIN_OR_INCOMPLETE_BILLED_LAUNCH
```

Without an engine that can atomically commit its internal advance together with the ledger, an
arbitrary SIGKILL cannot guarantee that every launched row *completes*. "Exactly-once" here is
shorthand for the four properties above and never a completion promise.

## States

`PLANNED → DISPATCH_INTENT → WRAPPER_ACK → START_GATE → ENGINE_OPENED → ADVANCE_STARTED →
ENGINE_EXIT_OK → RAW_SEALED → RAW_PUBLISHED → VERIFIED`, each checksummed and fsynced. Billing
begins irreversibly at `START_GATE`. Every pure hash, input, order, code and space check precedes
the gate. No engine import, constructor or advance may occur until the gate is exclusively published
**and** its parent directory is fsynced.

## Recovery matrix

| evidence | action |
|---|---|
| `VERIFIED` | skip forever |
| no gate, no live matching worker | redispatch the same `RUN_ID` |
| no gate, delayed wrapper possible | redispatch permitted: only one wrapper can win the atomic gate |
| gate + exact live worker identity | adopt and wait, never relaunch |
| gate + complete prefix through `ENGINE_EXIT_OK` and `RAW_SEALED` | finish publication/verification, no engine |
| `RAW_SEALED` alone or a broken prefix | billed incomplete, fatal |
| gate + dead worker, no sealed raw | charged once, never replayed |
| engine evidence without a gate | runner invariant failure, stop |
| PID / start-time / boot identity uncertain | freeze all starts |

Construction rejects the **whole candidate** and continues the frozen queue only while the required
complete-block count remains arithmetically attainable. After a panel is sealed, any sham or active
loss closes that panel.

## Polling contract (frozen)

```
HEARTBEAT_PERIOD_SECONDS = 5            POLL_CALL_TARGET_SECONDS <= 30
MAXIMUM_SILENT_INTERVAL_BEFORE_STATUS_CHECK_SECONDS <= 60
ONE_SUPERVISOR_PER_PHASE = true         MAX_SAFE_SUPERVISOR_RESTARTS_PER_PHASE = 4
AUTO_REPLAY = false                     AUTO_REPLACEMENT = false
ENGINE_ROW_WALLCLOCK_TIMEOUT = NONE
```

The heartbeat is liveness metadata and can never prove a row completed. Status calls read process
metadata, ledgers, opaque filenames, hashes and an expected-count boolean only. No subprocess
watchdog, no wall-clock kill, no duration-based admission, ordering or stopping: runtime may depend
on state or on the assigned condition.

## Campaign result

`FAIL` — 17 tests, dummy worker engine-free
(`True`), `REAL_ENGINE_CONSTRUCTOR_COUNT = 0`,
`REAL_ENGINE_ADVANCE_COUNT = 0`,
charged starts in the 672 child ledger during the campaign = 0.
