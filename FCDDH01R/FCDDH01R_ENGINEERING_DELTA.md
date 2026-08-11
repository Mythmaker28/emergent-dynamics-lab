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
