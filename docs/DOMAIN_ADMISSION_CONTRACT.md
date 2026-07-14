# DOMAIN-ADMISSION CONTRACT

A formal gate that every future instrument must pass **before** it is applied to a substrate. It exists because
`SC-PILOT-CAUSAL-FINGERPRINT` reached the launch pad with an instrument that was **not defined** on the droplet's
observable, and nothing in the protocol was obliged to notice.

```
admissible  ==  intervention-compatible
            AND observable-compatible
            AND noise-model-defined
            AND units-defined
            AND metric-defined
            AND coverage-sufficient
            AND common-noise-channel-declared
```

The last conjunct is not decorative. It follows from the measurement-contract theorem: absolute gain is not
identifiable when both the output scale and the noise scale are free. See `CONTINUOUS_NOISE_TOLERANCE_CONTRACT.md`.

## Application 1 — the Boolean fingerprint on the droplet substrate

| clause | status |
|---|---|
| intervention-compatible | ~ external field perturbation exists |
| **observable-compatible** | **FAIL** — the instrument decides by Hamming distance over `uint8`; the droplet exposes a continuous float of order 1e-3 |
| **noise-model-defined** | **FAIL** |
| **units-defined** | **FAIL** |
| **metric-defined** | **FAIL** — no tolerance, no quantization rule, no continuous distance |
| coverage-sufficient | not reached |
| **common-noise-channel-declared** | **FAIL** — field noise never characterized |

**VERDICT: REJECTED.** This is D-073, and it is now a gate rather than an act of vigilance.

## Application 2 — the CONTINUOUS fingerprint on the droplet substrate

**VERDICT: REJECTED.**

The continuous instrument is admissible on `ctrans`. **It is not thereby admissible on droplets, and it did not
even qualify on `ctrans`.** Successful admission in a continuous *benchmark* is not automatic admission to a
continuous *physical substrate*. The droplet mapping still requires an **independent physical calibration** of:

* `N` amplitude · `c` amplitude · **uptake units** · **field noise** · spatial aggregation · temporal sampling ·
  **baseline drift** · physical relaxation time.

Every one of these is a **free parameter that materially controls the within-versus-between separation** the pilot
exists to test. Supplying them is **defining an instrument**, not adapting one — which is the exact lesson of the
preflight, and it does not stop being true just because the instrument is now continuous.

Two further clauses would fail today even if the physics were calibrated:

* **coverage-sufficient** — unestablished for a droplet's actual intervention access;
* **partition** — a droplet that forms two lobes, merges, splits, or aliases its tracker **silently changes the
  denominator** of any within-versus-between statistic. `ctrans` has **one declared object and no ambiguous
  boundary**, so partition dependence was **never exercised here** and **remains unresolved**. No partition
  robustness may be read into any result in this experiment.

## Standing rule

> **Admission is checked BEFORE the experiment, not defended AFTER it.**
> A confident verdict on a case the instrument cannot resolve is a **fabricated certainty**.
> A refusal on a case the instrument *could* have resolved is a **fabricated abstention** — exactly as dishonest,
> and harder to notice, because it looks like caution. `EXP-GT-CONTINUOUS-FINGERPRINT-00` failed on the second.
