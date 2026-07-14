# CTRANS — the continuous ground-truth substrate

The smallest world that can host the actual metrological problem. It is not an artificial-life world and does not
try to be one. It exists to qualify — or kill — a continuous-response causal fingerprint.

## Why it had to be built

`EXP-GT-FINGERPRINT-00` decides by **Hamming distance over `uint8` symbols**. The droplet's accessible observable
is a **continuous float of order 1e-3**. Cast it to `uint8` and everything collapses to `0`. Compare it by exact
float inequality and every system differs from **its own later self**. Neither is a measurement — that is D-073,
`PREFLIGHT_FAIL`. A continuous instrument must be built, and it can only be qualified against a continuous ground
truth with a **privileged** answer key.

Both failures are reproduced *in this substrate*, so the problem being solved is demonstrably the real one:

| naive mapping | measured here |
|---|---|
| cast to `uint8` | every sample -> `0`. Universal false **sameness**. |
| exact float inequality | **304 / 304** samples differ from a re-measurement of the *same system*. Universal false **difference**. |

## Structure

A 1-D chain of **6 sites**. Addresses are fixed for every system, so the battery is identical for every system.

| address | role | who may touch it |
|---|---|---|
| 0 | `DRIVE` — exogenous carrier field (period 12, base 0.50, amp 0.30) | any repertoire |
| 1 | `SUPPLY` — local supply line (constant 0.40) | any repertoire |
| 2–5 | internal sites | **rich access only** |

Internal site kinds: `LINEAR` (leaky integrator) · `SAT` (saturating transducer) · `BIST` (double-well bistable
memory) · `DEAD` (present, inert). Edges carry **integer transport delays** at sample resolution.

```
readout:      y_true(t) = g_out * tanh(k_out * C.x) / k_out          (k_out = 0 -> linear)
observable:   u(t)      = a * ( y_true(t) + Y_BASE + eta(t) + delta(t) ) + b
```

`Y_BASE = 1e-3` — the droplet's magnitude, on purpose. `eta ~ N(0, sigma^2)` i.i.d.; `delta` is a slow
Ornstein–Uhlenbeck baseline drift (`tau = 500`), **independent per episode**, so it does *not* cancel between a
probe episode and its baseline — because in a real experiment it does not.

## The one asymmetry that makes the problem solvable

`(a, b)` is the **readout** transform. It scales the signal **and the noise** by the same `a`. A change of the
system's **internal gain** scales the signal and **leaves the noise alone**.

> Any statistic normalized by the **measured noise scale** is therefore *exactly* invariant to a change of units
> and *exactly* sensitive to a change of gain.

Normalize by the response's own amplitude instead and gain differences vanish along with the units. That is
must-fail control **L7**, and it fails as predicted.

## Integration, and why "solver refinement is a nuisance" is a measurement and not a hope

RK4, `substeps = 4` (`h = 0.25`); the declared refinement is `substeps = 8` (`h = 0.125`). Delays are read at
**sample** resolution and held across substeps, so refining the solver changes the ODE accuracy and nothing else.

**Measured** relative disagreement between `h=0.25` and `h=0.125`:

| system | relative |
|---|---|
| `D_leak` | 5.915e-09 |
| `D_sat` | 6.392e-09 |
| `D_fb` | 8.836e-09 |
| `D_cascade` | 7.649e-08 |
| `D_mem_p` (bistable) | 2.146e-07 |

Solver tolerance `TOL_REL = 1e-5` sits above the worst of these and ~4 orders **below** any genuine difference.

## What the substrate provides as privileged ground truth

source variables · intervention addresses · accessible outputs · hidden states · causal delays · system class ·
**behaviourally equivalent implementation pairs** · genuinely different function pairs · genuinely different
hidden-state pairs · silent systems · unreadable systems · in-flight systems · nonstationary systems ·
**access-restricted systems** · known noise and drift · known interventions · independent raw-trace evaluation.

### Three constructions that are EXACT, not approximate — verified numerically

| construction | limited arm | rich arm |
|---|---|---|
| `hidden_mode` — an internal site **unreachable from the external fields** that nonetheless feeds the readout | max\|dy\| = **0.000e+00** (bit-for-bit identical) | **1.525e-03** (separable) |
| `dead_site` — a genuinely extra internal degree of freedom, coupled to nothing | **0.000e+00** | **0.000e+00** |
| `relocate` — the same transfer function on a different internal address | **0.000e+00** | **2.090e-03** |
| `supply_cause` under **drive-only** probing | **6.5e-19** (float roundoff — an exact collapse) | — |

The first row is the **false-sameness** case, and it is not a defect: it is a fact about the repertoire. The last
row is control **L4**'s collapse, exact by construction.

### The bistable memory: a TRANSIENT probe leaving a PERMANENT mark

The memory is **not** wired to add a constant to the output. A purely static output offset is exactly what the
readout offset `b` absorbs, and would be **correctly unidentifiable**. It is wired through the **saturating
readout**, where its state moves the operating point and therefore changes the system's **incremental causal
gain** (~7x between the two wells). Hidden state is visible exactly insofar as it changes the *response*.

Measured, noise-free, reading the tail long after a 24-sample step has ended:

| system | probe | peak | tail | verdict |
|---|---|---|---|---|
| `D_mem_p` | step **+1.8** | 5.80e-05 | 1.9e-11 | recovered |
| `D_mem_p` | step **−1.8** | 1.63e-03 | 1.23e-03 | **PERMANENT MARK** |
| `D_mem_m` | step **+1.8** | 1.36e-03 | 1.23e-03 | **PERMANENT MARK** |
| `D_mem_m` | step **−1.8** | 4.73e-04 | 1.3e-10 | recovered |

Asymmetric, state-dependent, and permanent. The carrier alone never flips it.

## Abstention systems — each independently confirmed by the privileged path

| system | world-level fact (privileged, noise-free) |
|---|---|
| `D_silent_dead` | `g_out = 0` -> **silent**, snr 0.00 |
| `D_silent_sat` | driven so deep into saturation its incremental gain is nil -> **silent** |
| `D_noisy` | **snr_true = 1.97** — below its own noise floor. *Unreadable, not indistinguishable.* |
| `D_slow` | **t_settle = 507** against a 160-sample window -> **in flight** |
| `D_drifty` | baseline drift excursion 0.91x the response -> **nonstationary** |
| `D_lowcov` | the DRIVE line is unreachable: 6 of 8 probes cannot happen -> coverage 0.25. It **does** answer the supply probes it admits — that is the point. |
| `D_leak_loud` | the same system on a 4x noisier channel -> **measurement-contract violation** |

`t_settle` is measured on a **1600-sample** horizon. The first version estimated the asymptote from the tail of a
200-sample window, so for a slow system it took 99% of a value still climbing and reported 182 for a system whose
true settling time is **507**. It would have certified "not in flight" for a response that was entirely in flight —
**D-067's error, inside the evaluator whose job is to catch it.** Fixed, and recorded.
