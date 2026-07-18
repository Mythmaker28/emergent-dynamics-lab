# PROSPECTIVE CERTIFICATE — EXP-GT-CONTINUOUS-FINGERPRINT-00

# RESULT: **FAIL**

**One run. Hash-gated. Nothing tuned. The instrument is RETIRED, not repaired.**

The prospective experiment verified the sha256 of all six frozen files before executing a single episode. The
radii, battery, representation, noise model, admission rules and verdict logic were fixed at the freeze, and the
gates G1–G10 were fixed in the protocol **before the instrument existed**.

---

## The gates

| gate | requirement | result |
|---|---|---|
| **G1** | continuity / false-difference pairs are **not** called DIFFERENT | **PASS** |
| **G2** | **every DIFFERENCE pair separates** | ### **FAIL** |
| **G3** | strict non-overlap of the continuity and difference regions | **PASS** |
| **G4** | every abstention case returns INDETERMINATE | **PASS** |
| **G5** | false sameness: `INDISTINGUISHABLE` under limited **and** `DIFFERENT` under rich | **PASS** |
| **G6** | unit invariance, exact (max relative deviation <= 1e-9) | **PASS** — deviation **0.0** |
| **G7** | continuity survives the unseen elevated noise regime (1.6x) | **PASS** |
| **G8** | hidden state detected prospectively | **PASS** |
| **G9** | non-vacuous (>= 4 DIFFERENT and >= 4 INDISTINGUISHABLE) | **PASS** |
| **G10** | the two truth paths agree on every scored case | **PASS** — **54/54, 0 disagreements** |

**Matrix: 52 / 54.** Both failures are the same case, in both arms.

| arm | max(continuity) | min(difference) | **gap** | r_continuity | r_separation |
|---|---|---|---|---|---|
| limited | 2.808 | 40.152 | **+37.344** | 7.786 | 23.357 |
| rich | 4.410 | 43.556 | **+39.146** | 8.207 | 24.622 |

The separation is enormous and strictly non-overlapping. **That is not what failed.**

---

## What failed: C-P-13, `P_leak | P_cascade`, in both arms

The instrument returned **INDETERMINATE** where the predeclared gate required **DIFFERENT**.

It was **not** the metric. The distance was **64.15** (limited) and **234.30** (rich) — far above the separation
radius of 23.36. The instrument *measured* the difference correctly and then **refused to report it**.

The refusal came from the **in-flight guard**: *"46% of the right system's responses are STILL MOVING when the
window ends."*

### Why the guard fired, established from the noise-free ground truth

| system | tail block \|r\| as % of peak | previous block \|r\| as % of peak | change |
|---|---|---|---|
| `P_leak` (first-order) | 0.032% | 0.688% | 0.66% |
| `P_cascade` (**second-order**) | 0.931% | **6.247%** | **5.3%** |

The guard declares a row in flight if its tail moves by more than **5% of its own peak**. `P_cascade`'s tail moves
by **5.3%**. **The guard fired correctly, by its own specification.** The response really was still decaying.

### Why that is nevertheless a failure of the instrument

The privileged path — which never imports the instrument — reports `P_cascade`'s settling time as **108 samples**,
comfortably inside the frozen **160**-sample window, and `in_flight = False`. **The window was long enough. The
instrument could have decided this case and did not.**

The two criteria disagree because they measure different things. The frozen guard's 5%-of-peak threshold was
calibrated on **development** systems that are **first-order**, whose transients collapse fast (`P_leak`: 0.66%).
A **second-order** system has a slower tail, and `T3 = 21` — a parameter **reserved to the prospective split and
never seen during development** — puts that tail exactly on the wrong side of the threshold.

**Classification: observer failure — settling criterion.** Secondarily a **scope failure**: the settling criterion
was fitted, implicitly, to the tail behaviour of the development family, and does not cover the declared
prospective family.

---

## What the instrument did NOT do

It is worth being exact about the shape of this failure, because it is not the shape the programme feared.

* **It never manufactured a false SAME.** Zero false `INDISTINGUISHABLE` verdicts anywhere.
* **It never manufactured a false DIFFERENT.** Zero false `DIFFERENT` verdicts anywhere.
* **It never confused a change of units with a change of the world.** G6 exact: relative deviation **0.0**.
* **It never called a collision an identity.** The false-sameness pair returned `EQUIVALENCE_CLASS_ONLY` under the
  limited repertoire and `DIFFERENT` under rich — the collision is real, repertoire-relative, and reported as such.

The failure is **conservative**: the instrument abstained where it should have spoken. That is far preferable to
the alternative, and it is still a failure. **INDETERMINATE is not DIFFERENT, and the gate said DIFFERENT.**

---

## Coverage, responsiveness, abstention

Every abstention case abstained, **for the declared reason**:

| case | system | mechanism |
|---|---|---|
| C-P-21 | `P_silent_dead` | responsiveness 0 — *silence is not a fingerprint* |
| C-P-22 | `P_silent_dead` vs `P_silent_sat` | **two silent systems are not the same system** — refused, not matched |
| C-P-23 | `P_noisy` | response below its own noise floor — *unreadable, not indistinguishable* |
| C-P-24 | `P_slow` | in flight (true settling 651 >> window 160) — a genuine window shortfall |
| C-P-25 | `P_drifty` | baseline wanders 5x its own white-noise scale — nonstationary |
| C-P-26 | `P_leak_loud` | **measurement-contract violation** — same system, 4x noisier channel |
| C-P-27 | `P_lowcov` | drive line unreachable; coverage 0.25 < floor 0.5 — **and it still answers the supply probes it admits.** It could have produced a confident number from a quarter of the battery. It refused. |

Coverage is 1.00 and responsiveness > 0 for every non-silent, non-restricted system.

## False sameness (C-P-20)

`P_leak` vs `P_hidden` — an internal mode **unreachable from the external fields** that nonetheless feeds the
readout. Under limited access it sits at **exactly zero for all time**: the two systems are **bit-for-bit
identical** (privileged residual **0.0**). Instrument distance **2.514** -> `INDISTINGUISHABLE_UNDER_REPERTOIRE`,
reported as **`EQUIVALENCE_CLASS_ONLY`**. Clamp its address — rich access only — and the distance is **88.85** ->
`DIFFERENT`.

**Both statements are true.** Equivalence is relative to a repertoire. Neither is a metaphysical claim about
identity, and the instrument never emits the word SAME.

## False difference

Every representation-artefact pair stayed inside the continuity radius: independent re-measurement (2.42),
**affine unit change `u -> 250u - 0.02` (2.57)**, solver refinement (2.53), carrier time-origin shift (2.59), an
extra unobservable internal degree of freedom (2.74), and continuity at an **unseen 1.6x noise level** (2.81).

## Hidden-state detection (C-P-16)

`P_mem_p` vs `P_mem_m` — the same equations, the bistable well on the other side. Distance **204.18** ->
**DIFFERENT**. It is visible because the memory shifts the operating point of the saturating readout and therefore
changes the system's **incremental causal gain**. A hidden state that merely added a constant to the output would
be absorbed by the readout offset `b` and would be, **correctly, unidentifiable**.

## Decision

Per the freeze manifest's own failure rule, written before the run:

> If either arm fails prospectively: the instrument version is **RETIRED**, artifacts preserved, and **no repaired
> version inherits this split**. A future version requires a new split and a new authorization.

The in-flight guard's threshold is a **one-line change**. It is **not made here**, and a repaired instrument would
**not** be prospectively qualified — it would be an instrument tuned on its hold-out. The hold-out is now **burned**.

**EXP-GT-CONTINUOUS-FINGERPRINT-00: FAIL — RETIRED.**
