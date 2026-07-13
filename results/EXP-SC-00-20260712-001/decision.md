# EXP-SC-00 — ORTHOGONALITY QUALIFICATION FAILS (O2). Substrate RETIRED. No R8, no GATE-0, no law map.

Protocol SHA `aed457c2` + Amendment 1 SHA `fc4f4d97`, both frozen before the runs they govern.
Scaffold = **exactly** the EXP-CH-00 law-2 parameters (an R7 survivor, D-038) — not hand-chosen.
Every metric passed synthetic must-pass **and** must-fail cases first (`tests/test_scaffold.py`, 8 cases).

## What passed
- **O1 PASS** — the scaffold coheres with the internal network **disabled** (`a = 0`): PR 0.133, entity Rg 2.36,
  16 entities. **Cohesion does not depend on the internal network.** The orthogonal architecture works.
- **O3 PASS** — violently structured `u`/`v` on a sub-threshold scaffold produce **zero** entities. The internal
  fields cannot manufacture a droplet.
- **O4 PASS** — flipping a droplet's internal state changes its **future specific uptake** by 13–28 %, and the
  `beta = 0` negative control changes it by **exactly 0.0 %**. **Identity is causally efficacious, not decorative.**

## What failed
- **O2 FAIL at every `beta` in the declared grid, on both unseen seeds.** Distinct internal states do **not** leave
  localization intact: the entity radius of gyration varies across internal states by **1.83–4.12 cells** against a
  frozen tolerance of 1.5.

| beta | O1 | O2 (dPR / dRg) | O3 | O4 (uptake change) | verdict |
|---|---|---|---|---|---|
| 0.05 | PASS | FAIL (0.012 / 1.83) | PASS | **FAIL (8.2 %)** | fail |
| 0.10 | PASS | FAIL (0.023 / 3.64) | PASS | PASS (13.8 %) | fail |
| 0.15 | PASS | FAIL (0.035 / 2.81) | PASS | PASS (20.3 %) | fail |
| 0.20 | PASS | FAIL (0.047 / 4.12) | PASS | PASS (28.4 %) | fail |

**No `beta` passes.** At the smallest coupling (0.05), O2 still fails *and* O4 fails too — so there is no coupling
strength at which the internal state is **both** causally efficacious **and** leaves localization invariant.

## The precise, scoped finding
**Identity acting through UPTAKE is not orthogonal to cohesion, because uptake feeds GROWTH and growth feeds the
scaffold's own mass balance.** The internal state changes how fast a droplet eats; how fast it eats changes how big
it is; how big it is *is* its localization. The channel that makes identity matter is the same channel that builds
the body.

This is the **third** instance of one architectural pattern, and the pattern is now the finding:
- EXP-MA-00: cohesion and internal *structuring* shared the **transport flux**.
- EXP-SC-00: cohesion and internal *causal efficacy* share the **mass balance**.
Separating the degrees of freedom was **not enough** — the *couplings* must be separated too.

**Scope:** this does not show that scaffold+internal-network architectures cannot work. It shows that **a behavioural
coupling routed through growth** cannot be orthogonal to cohesion. It points precisely at couplings that do **not**
feed the scaffold's mass balance — motility *direction* (where the droplet goes, not how much it eats), oscillation
*phase*, or *response to an external probe*. That is a different substrate, preregistered from the outset, and it is
**not** added here.

## An honest near-miss, recorded because it is the whole point
At the hand-set `beta = 0.6`, O2 failed. A post-hoc scan then "found" `beta = 0.15` passing **both** O2 and O4 on the
seed the failure was observed on (dRg 1.04). Adopting it would have been tuning-after-failure. Instead `beta` was
re-declared as **selected by the qualification, prospectively**, on a frozen grid and unseen seeds (Amendment 1).
**On unseen seed 8101, `beta = 0.15` fails O2 (dRg 1.95).** The window did not replicate. Had I taken the post-hoc
value, I would have proceeded to R8 on a substrate that does not qualify.
