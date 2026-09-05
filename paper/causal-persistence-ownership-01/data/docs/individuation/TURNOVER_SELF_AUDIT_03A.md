# LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03A — Adversarial self-audit

*I am the same agent that produced design commit `244bc32`. This is not a fresh independent audit; it is an explicit
attempt to **falsify my own prior interpretation**, with every change from the parent proposal documented. Branch
`design/lci-causal-turnover-preseal-repair-03a` off `244bc32`. No 54xxx seed run; no active reconstruction; nothing
pushed.*

## 0. Reproduction (TASK 1)

Every parent headline number regenerates from the committed script `turnover_dev_analyze.py` on the committed raw:
feasibility 4/8, deep own +0.131, own-dose 0.135, neigh-dose 0.580, retention 0.68, up_ref ~2.5e-4. Events
classified separately (`TURNOVER_EVENTS_03A.json`): **FISSION 3, LOSS/DEATH 1, FEASIBLE 4, INELIGIBLE 2**. Fission
events (50001@153, 50006@692, 50009@436) are preserved as a **censored secondary dataset** — no reproduction claim
is made from a daughter.

## 1. Five things my parent interpretation got wrong or over-claimed

### 1.1 "Interventional causal individuation survives" — FALSIFIED as evidence of individuation
New test (TASK 3D, `turnover_dev_diagnostics.py`): at deep turnover the observed own-effect fraction is **0.87× the
algebraic direct-coupling prediction** `⟨λ₊·m₊/(1+λ₊·m₊)⟩` (obs mean 0.052 vs pred 0.061; per-world obs ≤ pred).
So the entire interventional effect is **the algebraic multiplier acting on a surviving m₊ remnant — with no
dynamical amplification** (it is if anything slightly *below* the passive prediction, consistent with partial
re-writing during the horizon). My parent framing ("interventional individuation survives, a low bar") was correct
that it is a low bar but **understated how low**: it is a near-identity, fully predicted from `m₊` and `λ₊`. It is
**not** evidence of any droplet-level causal capacity beyond the coupling term.

### 1.2 "Spatial-locality individuation survives" — WITHDRAWN
`own − neighbour > 0` at depth demonstrates **local perturbability** (zeroing the target's co-located memory field
locally reduces the target's coupled feeding), **not ownership** of graded history. Erasing a spatial region reduces
whatever feeding that region supports, regardless of whether the *information* is the droplet's own, a neighbour's,
or environmental. The phrase "spatial-locality individuation survives" conflated perturbability with ownership. I
withdraw it. The correct statement: *a spatially co-located, passively-copied memory remnant remains locally
perturbable.*

### 1.3 "up_ref negligible" — strengthened causally, but "global channel excluded" was too strong
Parent measured only the write-signal magnitude (global/local 6e-4). The repair adds the **causal** `up_ref := 0`
ablation (TASK 3C): deep memory ratio **1.00** and deep own-effect **identical** to intact. So `up_ref`
specifically is causally irrelevant. **However**, `up_ref` is not the only possible global/distributed channel
(field diffusion, shared environment). The parent implicitly treated "up_ref small" as "global excluded"; the
distributed-access test (§2) shows the broader question is **unresolved**, not settled.

### 1.4 "Graded storage fails" — downgraded to "ownership unresolved at DEV"
Parent asserted graded storage *fails* (own-dose 0.135 < neigh-dose 0.580). At n=4 worlds this is not a licensed
conclusion: in the L/P/E/G scope decode (§2) **no scope decodes own-dose above its within-world null** (all R²<0).
The honest statement is that own-graded ownership is **unresolvable at DEV**, not established as failing. This is a
correction *against* my own prior (I had leaned too hard on a negative from n=4).

### 1.5 Power: 50 seeds / ≥18 valid was internally inconsistent
Beta-Binomial propagation of the DEV small-sample uncertainty gives **P(N_valid≥18) = 0.57 at N=50** — a coin flip,
not the implied ≥90 %. Corrected to **N=96** (P=0.93). (Parent `TURNOVER_POWER.md`.)

## 2. The competing hypothesis I did not consider: distributed access structure

The causal information may not belong to one droplet; it may be redundantly/synergistically encoded across the
droplet (L), neighbours (P), environment (E), and global state (G). DEV exploratory scope decode of own-dose
(world-grouped LOGO + within-world permutation null, n=4 worlds / 12 samples, 3-D scopes):

```
L own-dose R²=-0.21 (null95 0.21)   P=-0.40 (0.11)   E=-0.36 (-0.08)   G=-0.36 (-0.36)   → none beat null
committed 11-D: own-dose 0.135, neigh-dose 0.580
```

At n=4 this **cannot separate local from distributed** — but it decisively shows my parent "local" reading is
**not supported** by DEV. The 11-D neighbour-dose (0.580) exceeding own-dose (0.135) is a live hint of shared/global
structure. A prospective ACCESS-STRUCTURE test (own vs L/P/E/G) is preregistered (`TURNOVER_ANALYSIS_SPEC_03A.md`).

## 3. What I now hold (with evidence tier)

- **OBSERVED (DEV, byte-identical):** feasibility 50 % (fission-dominated); deep own = 0.87× algebraic prediction;
  up_ref=0 ⇒ memory & own-effect unchanged; copy-disabled ⇒ m₊ collapses to 0.26×; eta_w=0 ⇒ 0.44× remnant.
- **SUPPORTED (mechanistic):** the surviving effect is a **passively-copied, algebraically-coupled remnant**; passive
  inheritance is **necessary** to sustain it; there is **no reconstruction** and **no global-channel** contribution.
- **NOT ESTABLISHED:** droplet **ownership** of graded history at depth (own > neighbour AND > global). Unresolved at
  DEV; needs the powered prospective test.
- **FALSIFIED (of my own parent claims):** "interventional individuation survives" as evidence of individuation
  (it is pure direct coupling); "spatial-locality individuation survives" (perturbability ≠ ownership).
- **SPECULATIVE:** any active reconstruction; any distal/emergent behaviour.

## 4. Net effect on the design

The repair moves the **primary** gate from the interventional effect (now demoted to a mechanistic check with the
algebraic prediction as its null) to **graded own-history ownership** (own-dose > neighbour AND > global), adds the
five mechanistic nulls (A/B/C/D/E), adds the distributed-access L/P/E/G test, and re-powers the family to N=96. The
DEV evidence predicts the prospective outcome will most likely be **Outcome B or D** (a passive local/homogenized
remnant, no ownership) — which is precisely the result that would *motivate* (not confirm) ACTIVE-RECONSTRUCTION,
and which is worth establishing at power rather than asserting from n=4.
