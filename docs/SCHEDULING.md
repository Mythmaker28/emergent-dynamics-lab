# Native Scheduled Task

- Mechanism: Codex native heartbeat automation.
- Automation ID: `emergent-dynamics-lab-autonomous-research`.
- Name: `Emergent Dynamics Lab Autonomous Research`.
- Status verified: `ACTIVE`.
- Requested cadence: every 30 minutes.
- Effective recurrence verified: every 30 minutes.
- Destination: the current local Codex task at `C:\Users\tommy\Documents\ising v3`.
- Overlap protection: repository atomic JSON lock in `.runtime/scheduled_task.lock`; conservative owner-only release, no age-only stale deletion.

The heartbeat prompt reads durable state, executes the next authorized stage, journals every working invocation, tests, indexes outputs, commits/pushes, and stops at the protocol's terminal conditions. The cadence is a wake-up interval, not an instruction to terminate valid long experiments after 30 minutes.

