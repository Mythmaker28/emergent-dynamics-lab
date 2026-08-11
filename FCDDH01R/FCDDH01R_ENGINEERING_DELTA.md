# FCDDH01R engineering delta

The only permitted class of change, and the only class made.

## Scientific path: byte-identical, with exactly one path constant

13/13 scientific modules are
**byte-identical** to the committed FCDDH00 objects: the certified-interval core, the independent
reference, the SHAKE256 scheduler, the child-marker runner, the G1 construction worker, the
acquisition launcher, the decode layer, the discovery and hold-out drivers, the oracle, the hold-out
fixed-axis scorer, the exact 2^16 enumerator and the canonical 44-field schema. The carrier
executable `FWL2CF00/fw_worker.py` is unchanged (`a10a8af515649851…`,
`unchanged = True`) and the immutable parent basis is unchanged.

`DISCOVERY_AXIS_TRAINER_V1.py` differs by **exactly 1 line**:
its firewall root `ALLOWED_ROOT`. This is not merely permitted, it is **required**: keeping the
FCDDH00 root would ADMIT dead-panel paths and fail DEX9. Every formula, gate, fold rule, sign
convention and refusal in that file is unchanged.

## New engineering, outside the numerical path

* `DURABLE_PHASE_SUPERVISOR.py` — detached phase supervisor: own session, stdin disconnected,
  durable append-only logs, fsynced PID/start-time/boot identity and heartbeat, exclusive flock per
  phase, at most one billed row at a time, no interactive shell or PTY dependency, atomic opaque
  publication, pollable without decoding science, exits at every phase barrier.
* `EXACT_ONCE_PHASE_STATE_MACHINE.py` — immutable `RUN_ID`, the ten monotone states, the
  append-only WAL **directory** of individually published atomic records, the exclusive
  `START_GATE` filesystem claim that charges the row, non-overwriting publication by exclusive
  link (never `os.replace`), and the conservative recovery matrix.
* `fr_dummy.py`, `fr_dex.py`, `fr_plan.py`, `fr_launch.sh` — mock-only failure injection, the frozen
  plan builder and the frozen launch template.
* retry-specific paths, programme labels, seed namespace and report names.

Nothing else changed. No engine, no LawSpec, no reader, no carrier, no mask rule, no horizon, no
weight, no threshold rule, no gate, no sample size, no claim ceiling.

## The frozen launch template

```
/usr/bin/nohup /usr/bin/setsid -f /usr/bin/python3 -u \
    /home/claude/sweep/FCDDH01R/DURABLE_PHASE_SUPERVISOR.py <plan> \
    </dev/null >>phase.log 2>>phase.err &
```

It has authority **because DEX0 passed**, not because a manual says so: a real bounded tool call was
allowed to expire at the same 120-second boundary that killed FCDDH00, and the supervisor kept the
same PID and start identity, kept heartbeating, and completed all ten dummy rows afterwards. A
second trial killed the entire launcher process group explicitly with the same result.

## What the campaign caught before any billed start

DEX13 exposed a real exactly-once defect: concurrent wrappers raced on the gate's *temporary* file,
not merely on its exclusive publication. The temporary is now unique per claimant. Eight simultaneous
wrappers for one `RUN_ID` now yield exactly one gate winner and exactly one charge. This is precisely
why the campaign is mandatory.

---

## Amendment 1 — publication is a two-pass, row-terminal operation (post DISCOVERY_CONSTRUCTION)

Executor code generation 1 `d531210e…` → generation 2 `5c6ca886…`.
Full record: `FCDDH01R_EXECUTOR_CODE_SUPERSESSION.json`. Zero engine starts consumed.

**What was wrong.** `PhaseLedger.publish_raw` emitted the row-terminal state `VERIFIED` once per
*declared output*. Every real construction row declares two outputs (`d_<did>.npz`, `m_<did>.npz`).
The visible symptom was cosmetic — 48 false entries in `wal_monotone_violations`, adjudicated in
`FCDDH01R_WAL_MONOTONICITY_ADJUDICATION.json`. The defect underneath was not cosmetic:
`PhaseLedger.decide` reads `VERIFIED` as *this row is finished*, so a row killed after its first
output was published and before its second would have been **skipped as complete on resume**,
leaving a charged row with an unpublished declared output. That is a line-resumability failure —
exactly the class FCDDH01R was reauthorized to eliminate.

**Why it was not caught by DEX0–DEX16.** Every DEX row built by `mkrows` declared exactly one
output. With one output, per-output `VERIFIED` and row-terminal `VERIFIED` are indistinguishable.
The campaign was blind to arity, and the real phases are the only place arity is 2. The lesson is
recorded as a test-design finding, not merely a code finding: a durability harness must exercise
the *shape* of the real row, not only its failure modes.

**The remedy.** `publish_raw` is split into `seal_output` (emits `RAW_SEALED`) and `publish_sealed`
(emits `RAW_PUBLISHED`); neither emits a terminal record. `_publish_all` now runs two ordered
passes — seal every declared output, then publish every declared output — and emits exactly one
row-terminal `VERIFIED` afterwards. Outputs already final from an earlier generation are adopted
idempotently by digest, and `os.replace` is still never used on a final path.

**The proof.** Three new zero-engine cases, plus a tightened old one:

| case | injection | required behaviour |
|---|---|---|
| DEX17 | SIGKILL after output 1 is published, before the row is terminal | resume publishes output 2; one gate, one advance, one terminal record |
| DEX18 | two-output happy path, three rows | `verify_monotone` returns empty; exactly one `VERIFIED` per row, last |
| DEX19 | SIGKILL after seal-all, before publish-all | resume publishes both; one gate, one advance, one terminal record |
| DEX12 | tightened | publication alone no longer terminates a row; `SKIP_VERIFIED` requires the terminal record |

Campaign result after the change: **20/20 PASS**, zero engine starts, dummy still engine-free.
`Q0A–Q0W` rerun **23/23 PASS**. Scientific object identity re-verified with **zero drift**.

**Not done.** The completed `DISCOVERY_CONSTRUCTION` WAL was not edited, rewritten or compacted,
and no row was re-charged or replayed. Its 48 legacy reporter entries stand, explained.

**Test-integrity note.** Two assertions were changed *after* observing a failure. Both are declared
here rather than quietly amended. DEX12's expectation encoded the old contract and was replaced by
a strictly stronger one. DEX4's fixed three-second sleep was replaced by a bounded poll after the
refusal marker was found on disk, written after the old window closed — the invariant held; the
assertion was load-dependent.
