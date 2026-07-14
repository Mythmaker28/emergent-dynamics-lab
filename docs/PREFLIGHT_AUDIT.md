# PREFLIGHT AUDIT — SC-PILOT-CAUSAL-FINGERPRINT

**Repository clean at `b87f4cb` when the audit began.** No historical artifact overwritten or amended. All prior
failures and development diagnostics preserved. **The fingerprint was not tuned, patched or modified.**

---

## P1 — the 14-step replacement transient. **OUTCOME P1-B.**

**What I claimed:** *"behaviour uninterrupted"* and *"bounded 14-step transient"*, simultaneously. That was
ambiguous, and one half of it was wrong.

**What actually happened**, measured on the declared behavioural output (`out_cells`) of the E1 swap
(`and_or` → `xnor_and`, both computing AND):

| | |
|---|---|
| accessible output deviating steps, before the swap | **none** |
| accessible output deviating steps, after the swap | **exactly one — t = 53, channel 2** |
| span from the swap (t = 40) to the last deviating step | **14** |
| internal cells still differing at t = 159 | 1 (the two implementations *are* different insides — expected) |

**The figure 14 is a SPAN, not a count.** `transient_steps` was computed as
`last_deviating_step − t_swap + 1`, and exactly one step inside that span actually deviated.

**Correction, adopted:**

> **The pre-replacement accessible behaviour was recovered after a bounded 14-step transient. Continuity was NOT
> exact at every intermediate step: the accessible output deviated on one step.**

**"Uninterrupted behaviour" is withdrawn.** This changes no fingerprint verdict — the E1 *fingerprint* distance of
0.0000 is a comparison of the two systems' fingerprints and is untouched — but the trajectory claim was overstated
and is corrected.

---

## P2 — is the prospective ground truth independent of the fingerprint? **PASS — 18/18.**

**Path 1 — construction-declared.** The labels (`CONTINUITY` / `DIFFERENCE` / `COLLISION`) were declared in
`exp_gt_fp_p.py` from the *circuits built* — `and_or`, `xnor_and`, `direct_buf` all compute AND by construction —
and were committed at **`b87f4cb`, before the prospective run**.

**Path 2 — privileged full-state evaluation.** `exp_preflight.py` **never imports `fingerprint.py`**. It drives the
engine directly, applies the admissible interventions by privileged full-state clamping, and decides by **exact
equality of raw traces**. It uses **no distance function, no block structure, no radii, no compression and no
verdict rule** of the instrument under test.

**Result: the privileged path reproduces all 18 declared expectations, on both arms** — including the four
`DIFFERENCE` pairs, and including the droplet-arm `COLLISION` (`AND(clk,1) ≡ OR(clk,0)`), which it independently
confirms is genuinely indistinguishable under the droplet repertoire.

**Declared shared assumption.** The two paths share the **declared nuisance model** — clock phase and internal
latency — and they must, because both measure the same world and those are the same two nuisances. They share
nothing else.

**Three defects the audit found *in itself*, and fixed in the audit — not in the instrument:**

1. a single common cyclic shift cannot absorb a phase difference *and* a latency difference simultaneously;
2. `T_SIG = 128` truncated the aligned block of the longer-latency system — **a window shorter than the response,
   which is the D-067 defect, reappearing in my own audit**;
3. non-responding rows aligned to the window start leak phase and latency — **the same defect the instrument had
   already found and fixed in its own development.**

Each produced a *false difference in the audit*. None was in the instrument.

---

## P3 — the bounded partition-dependence addendum. **NOT EXECUTED.**

Verified: `FINGERPRINT_FREEZE_MANIFEST.json` contains **no** occurrence of *partition*, *lobe*, *alias*,
*bifurcation*, *observer_relative*, *object count*, *replication* or *duplication*. **It was never a gate of the
frozen protocol**, and no stress test covering the seven required cases exists anywhere in the repository.

**Classified honestly: an unexecuted bounded diagnostic that is NOT part of the fingerprint qualification.**
No retrospective PASS is fabricated. The historical hold-out is untouched.

It would have to be executed **inside** any droplet pilot, because the pilot's within-versus-between logic is
partition-dependent by construction: it presupposes an object count, and a droplet that forms two lobes, merges,
splits or aliases its tracker would silently change the denominator.

---

## P4 — raised BY the audit, not requested. **THE FROZEN INSTRUMENT IS NOT DEFINED ON THE DROPLET'S OBSERVABLE.**

**The instrument's response representation** (`fingerprint.py`, sha256 `798fff03…`, frozen at `b87f4cb`):

```python
a_obs = np.array([...], dtype=np.uint8)        # DISCRETE SYMBOLS
a_dev = (a_obs != a_bas).astype(np.uint8)      # EXACT inequality
ds.append((x != y).sum() / n)                  # HAMMING distance
```

**Hamming distance presupposes discrete symbols.**

**The droplet's accessible observable** is `uptake` = `dt·g0·ρ·N·qq·(1 + β·σ)` — a **continuous float field of
order 1e-3**, never 0 or 1.

| applying the frozen instrument as-is | result |
|---|---|
| cast to `uint8` | every sample truncates to **0** → every droplet's fingerprint is identical → **universal false sameness** |
| compared as floats | exact inequality fires on **every** sample → every droplet is DIFFERENT from every other **and from its own later self** → **universal false difference** |

**Neither is a measurement.**

**What is missing from the freeze:** any quantization or thresholding rule for a continuous observable; any
tolerance `ε` or continuous metric; any mapping from the frozen **binary** probe amplitudes `{0,1}` to `N` / `c`
field units.

**Each of these is a free parameter that materially controls the within-versus-between separation the pilot exists
to test.** Supplying them now is **defining the instrument**, not adapting it — and a patched instrument cannot
inherit the prospective qualification of the unpatched one.

**This is the failure mode the preflight was mandated to catch, and it caught it.** I should have seen it at D-072:
I flagged that *temporal provenance* does not transfer to a continuous substrate, and did not notice that the
**response representation** does not either. That omission is mine, and it is now on the record.

---

## DECISION

**`PREFLIGHT_FAIL`** — execution would require modifying the instrument.

Per Phase 2: **STOP.** The fingerprint is not patched, and no patched version is called prospectively qualified.
