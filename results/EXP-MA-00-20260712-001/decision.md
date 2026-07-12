# EXP-MA-00 — R8 FAILS. Multistable active-droplet substrate RETIRED. No GATE-0, no law map.

Protocol SHA `f59dd700baac59620c50f739b2fb2ad6ce4b0e13`, frozen before any screen. R7 and R8 only, exactly as
preregistered. No mechanism was added after observing a failure.

## The structural result: localization and multistability are mutually exclusive in this domain
Blind Halton screen of the frozen bounded domain (32 points, `lam ∈ [0.5, 6.0]`):

| | laws | demixing_index |
|---|---|---|
| **pass R7 (localized)** | 2, 4 | **0.043, 0.008** — essentially MIXED droplets |
| **genuinely demixed** (0.18–0.42, comparable to a synthetic Janus) | 5, 9, 16, 17, 18 | **all FAIL R7** — space-filling, PR 0.15–0.99 |

**0/32 laws are both localized and demixed.** Where the droplets hold together, `lam` fails to demix them; where
`lam` demixes, the droplets do not hold together. Median demixing over all 115 detected entities in the whole
domain: **0.012**. The synthetic reference (proven fireable) puts a Janus droplet at > 0.3.

## R8 on the laws that did pass R7 — entirely unseen seeds 7101–7108

| law | condition | R8-A separation ratio (need > 2.0) | R8-B accuracy (chance 0.12) | verdict |
|---|---|---|---|---|
| 2 | frozen law | **1.42 FAIL** | **0.19 FAIL** | R8 FAIL |
| 2 | **NEGATIVE CONTROL `lam = 0`** | 1.32 FAIL | 0.21 FAIL | R8 FAIL (as it must) |
| 4 | frozen law | **1.31 FAIL** | **0.15 FAIL** | R8 FAIL |
| 4 | **NEGATIVE CONTROL `lam = 0`** | insufficient entities (2) | — | — |

Entities under the same law are **not more different from each other than each is from itself over time**
(ratio 1.3–1.4, needed > 2.0), and a 1-NN rule fitted on early states **cannot re-identify them later**
(0.15–0.19 against chance 0.12).

**The `lam = 0` negative control fails identically.** At the laws that localize, the demixing term is doing
nothing: the frozen law is statistically indistinguishable from the control in which multistability is switched
off. That is the cleanest possible statement of the failure, and it is exactly what the built-in control was
preregistered to detect.

## Verdict
**R8 FAILS. The substrate is RETIRED. GATE-0 and the law map are NOT authorized** — as preregistered, they were
conditional on R7 **and** R8 passing. **No mechanism is added.**

## What this rules out, precisely (no overclaiming)
It does **not** show that multistable substrates cannot support individuality. It shows that **this** minimal
two-species demixing droplet, **within this frozen bounded domain**, cannot hold a droplet together and demix its
interior at the same time. The cohesive mechanism (shared attractant) and the demixing mechanism (mutual repulsion)
compete for the same flux: the parameter regimes that make the first strong enough to localize make the second too
weak to structure the interior, and vice versa. A substrate in which cohesion and internal structure are **carried
by different, non-competing degrees of freedom** is not excluded by this result — it is what the result points to.

## Methodological note
Every metric used here was first proven — on synthetic cases — to be able to **fire** and to **fail**
(`tests/test_r8_gates.py`: 10 cases including "entity present but wrong identity → zero identity recovery";
`tests/test_multistable_phenotype.py`: 5 cases separating mixed / Janus / core-shell / two-domain, with translation
and rotation invariance). The demixing metric is *proven* able to detect a Janus droplet. It found none.
