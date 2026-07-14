# EXP-GT-FINGERPRINT-00 — the single prospective run. **BOTH ARMS PASS.**

Frozen and hashed before this split existed (`FINGERPRINT_FREEZE_MANIFEST.json`; `fingerprint.py` sha256
`798fff03…`). Run once. No repair. Development was **18/18**.

## Results — 9 declared cases per arm

| | RICH arm | DROPLET arm |
|---|---|---|
| cases correct | **9/9** | **9/9** |
| **FALSE DIFFERENCE** (equivalent → DIFFERENT) | **0** | **0** |
| **FALSE SAMENESS** (different → INDISTINGUISHABLE) | **0** | **0** |
| INDETERMINATE | 0 | 0 |
| E1 pre/post-replacement distance | **0.0000** | **0.0000** |

### Continuity — behaviourally equivalent systems, never called different

| pair | rich | droplet |
|---|---|---|
| `and_or` vs `xnor_and` (two **unseen** AND implementations) | 0.0000 | 0.0000 |
| `and_or` vs `direct_buf` (buffered AND) | 0.0000 | 0.0000 |
| `and_or` vs itself at **different layout, phase and detour** | 0.0000 | 0.0000 |

Seven of ten systems use implementations **never fingerprinted**: `and_or`, `xnor_and`, `direct_buf`, `or3`,
`edge_xor`, `tri_tap`, `dup_lag`. Topologies and phases were used in no development world.

### Difference — different reachable function or genuine hidden state

| pair | rich | droplet |
|---|---|---|
| AND vs `edge_xor` (different truth table) | 0.1973 | 0.2094 |
| AND vs a **state machine** | 0.2274 | 0.3647 |
| a **LATCH** vs a **state machine** — *same parts, different behaviour* | 0.2274 | 0.3647 |
| AND vs a three-lag AND (`tri_tap`) | 0.0833 | 0.1049 |
| AND vs a two-lag AND (`dup_lag`) | 0.1391 | 0.1548 |

`reg_delay` **contains a register** and is not a state machine at its interface; `fsm_gate` is. The droplet
repertoire separates them at 0.3647 — from external field probes alone, by the **memory signature**: a *transient*
perturbation leaving a *permanent* mark.

### E1 — replacement during one continuous trajectory

`and_or` → `xnor_and`, two microscopically different AND implementations, **swapped mid-trajectory**:

```
identical before the swap;  accessible output deviated on ONE step (t=53);  recovered thereafter
pre-replacement vs post-replacement fingerprint distance = 0.0000   (continuity radius 0.015)
```

The material of the computation is replaced; the accessible behaviour deviates on **one step** and is then recovered; and the fingerprint does not move. *(See the correction below: 'uninterrupted' is withdrawn.)*

## Rich-versus-limited collision analysis — the cost of poor access, measured

| pair | RICH | DROPLET |
|---|---|---|
| `AND(clk, reg=1)` vs `OR(clk, reg=0)` — both are `clk` | **DIFFERENT** (0.1368) | **INDISTINGUISHABLE** (0.0000) |

Development, 4/4 such pairs: **DIFFERENT under rich access, INDISTINGUISHABLE under the droplet repertoire** —
including the D-069 redundant-lag system and the gated state machine. **False sameness rises as access falls.**
That is a property of the droplet, not of the fingerprint, and it bounds everything the pilot could claim.

## Declared limitations — stated before the run, not discovered after it

**1. The two STATE systems reuse development implementations.** The substrate contains no state machine that
development did not use, and I would not add one to the world generator after the instrument was frozen. Their
topology, layout, phase and pairing are new; their **implementation is not**. The hidden-state result tests the
battery's generalization — **not its generalization to an unseen state machine** — and may not be quoted as the
latter.

**2. This qualifies the fingerprint LOGIC under a droplet-*like* repertoire in a *Boolean* substrate.** Per the
D-071 scope clarifications, **temporal provenance is qualified only for the certified Boolean pipeline**, and
**exact direct-edge recovery only under one-step pulse access**. Neither transfers automatically. A droplet pilot
must build and certify its **own** provenance contract for a continuous, diffusive field with no episodes, no
discrete lags and no cell samples to re-read.

**3. The benchmark-label correction, made on development, before the freeze.** I first declared `(xor3, xor_gate)`
and `(toggle, fsm_gate)` to be continuity pairs in both arms. Under rich access the fingerprint separated them —
**and it was right to**: `xor3`'s reconvergent paths glitch on a register step, and `fsm_gate` freezes where
`toggle` does not. These are *measured responses*, not labels. The benchmark was wrong; the measurement was not.
The matrix was corrected with a stated principle — *equivalence is relative to a repertoire* — before anything was
frozen.

## Decision (mission §8)

**Both arms passed independently.** Per the preregistered rule, `SC-PILOT-CAUSAL-FINGERPRINT` is **AUTHORIZED as
an exploratory experiment** — and is **not executed here**. It is not EXP-SC-01, and it is not proof of identity.

**EXP-SC-01 itself remains BLOCKED.**


---

## CORRECTION (D-073, preflight P1) — the E1 trajectory claim was overstated

The wording above says the accessible behaviour was **"uninterrupted"**. **That is withdrawn.**

Measured on the declared behavioural output: after the mid-trajectory replacement, the accessible output **deviated
on exactly one step** (t = 53, channel 2). The figure **14** is the **SPAN** from the swap to the last deviating
step — not a count of deviating steps.

**Corrected claim:**

> The pre-replacement accessible behaviour was **recovered after a bounded 14-step transient**. Continuity was
> **NOT exact at every intermediate step**.

This changes **no fingerprint verdict**. The E1 *fingerprint* distance of 0.0000 compares the two systems'
fingerprints and is untouched, as are the development (18/18) and prospective (9/9, both arms) results. Only the
trajectory wording was wrong, and only it is corrected. See `docs/PREFLIGHT_AUDIT.md` §P1.
