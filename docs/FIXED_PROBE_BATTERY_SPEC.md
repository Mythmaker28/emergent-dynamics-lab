# FIXED PROBE BATTERY — SPECIFICATION (frozen)

> **A measurement coordinate system must not adapt to the entity being compared.**

The active planner (G6) is **prospectively qualified** and is **switched off** inside fingerprint acquisition. It
chooses a different intervention sequence per world — which is exactly what made it efficient, and exactly what
would make two entities' fingerprints incomparable.

Every system receives the same probe **types, amplitudes, durations, relative timings, contexts, observation
windows, order and normalization**. No probe is ever selected in response to a system's observed ambiguity.

## Addresses are fixed by the LAYOUT, not by which components exist

My first battery listed the machine's *actual* registers — so a system with a second register received a **longer
battery** than one without. A coordinate system whose number of axes depends on the thing being measured is not a
coordinate system. The three internal slots (register, second-register, write-enable) exist in every layout;
clamping a slot that happens to hold nothing is a legal intervention that produces no response, and *no response*
is a comparable coordinate.

## The battery

| probe | kind | target | droplet arm | rich arm |
|---|---|---|---|---|
| `drive_high` | clamp HIGH, 6 steps | the exogenous drive | ✅ | ✅ |
| `drive_low` | clamp LOW, 6 steps | the exogenous drive | ✅ | ✅ |
| `drive_pulse_up` / `_down` | one-step pulse | the exogenous drive | ✅ | ✅ |
| `supply_pulse_up` / `_down` | one-step pulse | the entity's own external supply line | ✅ | ✅ |
| `internal0/1/2_high` / `_low` | sustained clamp | register, second-register, write-enable slots | ❌ **no droplet analogue** | ✅ |

Every probe is applied at **all 8 clock-phase offsets**. The 8 rows are then **sorted lexicographically**: a global
phase shift cyclically permutes them, so sorting is an exact **group quotient** over the phase — the same move that
rescued the V4 timing head. It is not an average: averaging over phase integrates out the signal with the nuisance,
which is what killed V3.

Constants: `T_OBS = 200` · `T_PROBE = 80` · `W_RESP = 96` · `W_ALIGN = 40` · `D_HOLD = 6` · `TAIL = 16` ·
`COVERAGE_FLOOR = 0.5`.

## Normalization — three rules, each earned by a failure in development

**1. The response is ABSOLUTE, not merely a deviation.** A deviation-only fingerprint is **blind to output
inversion**: `AND(clk,1) = clk` and `XOR(clk,1) = NOT clk` deviate from their own baselines on *exactly the same
steps*, in opposite directions. Measured: **d(AND, XOR) = 0.0000** — a false sameness on two genuinely different
functions.

**2. Aligned blocks are READ FROM THE EPISODE, never zero-padded.** Padding a short response to a fixed length
makes the *padding*, not the behaviour, carry the difference: two systems with different latencies get different
amounts of zero and are called different for it. Measured: **d = 0.0946** between a channel and its own
lengthened twin.

**3. Two landmarks, for two situations.** A row that **responded** is aligned to its own **response onset** — the
shape is what the probe revealed, and reading it from the onset makes it invariant to internal latency. A row that
**did not respond** has no onset, and aligning it to the window start lets the latency leak in; it is aligned
instead to the entity's **own first rising edge** — a behavioural landmark. Using the rising edge for *both* was
worse (**d = 0.154**): `ref` wraps inside the window while `onset` does not, so their difference is invariant only
modulo a period. *The landmark must match the question.*

**Latency is reported, and never enters any distance.**

## Distance and verdicts

**Distance** = the mean, over probe **blocks**, of each block's normalized Hamming distance. Not a Hamming distance
over the concatenation: a long probe would otherwise dominate a short one purely by being long, and the weights
would be an accident of sampling. Per-block normalization also makes control **L1** honest — a smuggled class label
becomes *one more block*, weighted like any other, instead of a few bytes lost in a vector of sixteen hundred.

**Verdicts:** `INDISTINGUISHABLE_UNDER_REPERTOIRE` · `DIFFERENT` · `INDETERMINATE`. **There is no SAME.**

**Frozen radii** (derived on development, never moved): rich `r_c = 0.0075`, `r_s = 0.0226` · droplet
`r_c = 0.015`, `r_s = 0.0451`. Continuity distances on development were **exactly 0.0000** in both arms.
