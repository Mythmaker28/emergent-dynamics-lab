# DROPLET ACCESS EQUIVALENCE — what the limited arm is allowed to do, and why

**The limited arm was frozen BEFORE the prospective worlds were generated.**

## What the unchanged β = 0.10 scaffold substrate actually exposes

From `edlab/substrates/scaffold/engine.py`, the state is `rho` (matter), `U`/`V` (internal bistable species),
`c` (attractant), `N` (nutrient), `C` (cohorts, for turnover), `uptake` (the behavioural observable).

| field | can an experimenter perturb it non-destructively? |
|---|---|
| `N` — nutrient | **YES.** Externally supplied and diffusive. A bolus, global or spatially coarse, is an ordinary intervention. |
| `c` — attractant | **YES.** An external diffusive field. |
| `rho` — the droplet's own matter | **NO.** Touching it is displacement or destruction, not a probe. |
| `U`, `V` — the internal state | **NO.** Writing to them is *reprogramming the identity you are trying to measure*. This is the R8-C cargo intervention: it is destructive by construction. |

**There is no droplet analogue of clamping a register.** There is no droplet analogue of a one-step, single-site
write. There is no oracle that selects a context.

## The mapping, stated so it can be disputed

| Boolean substrate | droplet | admissible in the limited arm? |
|---|---|---|
| the clock — the single exogenous drive | the external `N` / `c` field | **YES** — `drive_high`, `drive_low`, `drive_pulse_up/down` |
| the drive line at the entity's own column | a **locally applied bolus** at the droplet's location | **YES** — `supply_pulse_up/down` |
| a register / the write-enable | `U`, `V` — the internal state | **NO.** Absent from the limited battery entirely. |
| observation of any internal cell | imaging `u`, `v` | **NOT USED.** The fingerprint reads only the **declared behavioural output** (the analogue of `uptake`). |

The `supply` probe is the **most generous** reading of "a locally addressed external perturbation". If one rejects
even that, the limited repertoire shrinks to the four global drive probes — and control **L2** measures exactly what
happens when probes are removed: two genuinely different systems **collapse into one fingerprint**. Probe-repertoire
adequacy is load-bearing, and it is demonstrated, not asserted.

## What the limited arm costs — measured, not assumed

Under the droplet repertoire, systems that differ **only in an internally-gated cause** are **indistinguishable**:

- `AND(clk, reg=1)` and `OR(clk, reg=0)` are both `clk`. No admissible droplet probe steps the register.
- a machine with a **third** cause (`and3`) is indistinguishable from one with two.
- the redundant-lag system and its clean twin are indistinguishable (they differ only in a glitch on a register step).
- a **gated** state machine and an **ungated** one are indistinguishable at the context where the gate is open.

**Development: 4/4 such pairs are DIFFERENT under rich access and INDISTINGUISHABLE under the droplet repertoire.**
False sameness rises as access falls. That is a property of the droplet, not of the fingerprint, and it is the
single most important limitation on anything the pilot could ever claim.
