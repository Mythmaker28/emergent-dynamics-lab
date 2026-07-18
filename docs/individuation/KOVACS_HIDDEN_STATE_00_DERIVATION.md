# KOVACS-HIDDEN-STATE-00 — exact theoretical derivation (Phase 0)

**Mission question.** Can two frozen histories bring exact clones of one organism to the same
declared macro-observable `Z`, yet — released under identical dynamics, environment, boundary and
`up_ref`, with no probe — produce *different subsequent relaxation of `Z`*?

This document derives the Kovacs logic for **this** engine before any new response outcome is
inspected. It fixes what a positive or negative result would and would not establish, and states the
conditions that separate a genuine null from an invalid match. Symbols and parameters are taken from
the audited parent lineage (`M_MINUS_SIGN_DERIVATION.md`, commit `ea6e6a0` / `03a909a`); nothing here
depends on a Kovacs excursion, which is not computed in Phase 0.

## 1. The engine as a deterministic macro-map

The substrate is the 64×64 multi-channel intensive-memory engine (`edlab.experiments.sc_mcm`). A full
microstate is

```
x = (rho, U, V, c, N, C, uptake, Mf=(Mf1,Mf2), step)          on the 64×64 grid
```

with intensive memory `m_k = Mf_k / max(rho, eps)` and readouts `m_plus = tanh(m1+m2)` (uptake gain)
and `m_minus = tanh(m1-m2)` (attractant gain). After seeded initialisation the update `x_{t+1} =
F(x_t; e_t)` contains **no stochastic draw** and retains no RNG (manifest `cloning.rng_state`,
`common_random_numbers: vacuous`). `e_t` is the exogenous environment/boundary input. `F` is therefore
a deterministic map and every downstream quantity is a deterministic functional of `(x_0, e_{0:t})`.

The transport/growth/death structure (from the parent derivation) matters for the argument:

- mass `rho` and each `Mf_k` are transported by the **same** donor-face flux;
- growth inherits the local intensive value, uniform death multiplies `rho` and `Mf` together, so
  neither growth nor death changes the intensive `m_k`;
- the memory update is
  `m_{k,t+1} = alive · clip( m_k^T + dt·alive·[ eta_w·Psi − eta_dk·m_k^T + eta_t·(Tmean−m_k^T) + D_m·Lap ], −1, 1 )`
  with `Psi_t = tanh(k_exp[N−c] + k_up[uptake − up_ref])`, `up_ref` = mean uptake over alive cells;
- frozen rates `dt=0.1, eta_w=0.015, eta_d1=0.35 (fast), eta_d2=0.006 (slow), eta_t=0.010, D_m=0.010,
  k_exp=k_up=1, lam_plus=0.25, lam_minus=0.15`.

Two consequences are used below. (i) The state carries **two memory timescales** (`q1=1−dt·eta_d1=0.965`
fast; `q2=0.9994` slow): a slow field that integrates history over hundreds of steps and a fast field
that forgets in ~30 steps. (ii) `up_ref` is **endogenous** (a mean over the organism's own alive
cells), so if two branches differ internally they generically induce *different* environments unless
`up_ref` is clamped common.

## 2. `Z`-sufficiency as an autonomy (semiconjugacy) property

Let `Z = phi(x)` be a scalar macro-observable (Phase-0 primary: core mass, §4). Say `Z` is a
**sufficient macrostate for its own evolution** under `(F, e)` on a set of reachable states `R` iff
there exists a function `f` with

```
phi(F(x; e)) = f(phi(x), e)      for all x in R.                (Z-AUTONOMY)
```

Equivalently, `phi` semiconjugates the micro-map `F` to a scalar macro-map `f`: knowing `Z` (and the
common environment) is enough to predict the next `Z`. If (Z-AUTONOMY) holds, then two states with
equal `Z` under equal `e` produce equal `Z` at every future step — no hidden coordinate can influence
the trajectory of `Z`.

**Kovacs falsification.** Suppose we can construct two reachable states `x_A, x_B in R` with

```
phi(x_A) = phi(x_B) = m*      (matched macro-observable),
e_A(t) = e_B(t)               (identical environment/boundary/up_ref),
```

and observe, after `k` common steps,

```
phi(F^k(x_A; e)) ≠ phi(F^k(x_B; e)).                            (KOVACS DIVERGENCE)
```

Then no `f` satisfying (Z-AUTONOMY) exists on `R`: `Z` is **not** a sufficient macrostate, and the
difference `x_A − x_B` — invisible to `Z` at the match — is **functionally active** on the future of
`Z`. This is a *constructive* falsification: one matched pair that diverges suffices in principle; we
aggregate over independent source worlds only to estimate the effect and its sign robustly.

Nothing in (KOVACS DIVERGENCE) requires, uses, or implies identity, ownership, reconstruction, or that
`x_A` and `x_B` are the "same" microstate. It is a statement about the information content of one
scalar under the engine's own dynamics.

Two boundary conditions make the falsification clean and are therefore protocol requirements:

- **Common environment.** `e_A = e_B` must be enforced, or a divergence could be attributed to a
  history-dependent environment rather than to the internal hidden state. Because `up_ref` is
  endogenous, the primary release clamps `up_ref` to a common value and uses one common,
  history-independent no-drive boundary source (the qualified continuation already built in the parent
  lineage). A coupled/endogenous-`up_ref` arm is secondary and is *not* the primary estimand.
- **No manipulation at release.** The match must not be produced by editing the state (surgery), and
  the act of declaring the match/starting the readout must not perturb `x`. Release is simply
  "continue `F`." A one-step discontinuity diagnostic checks `|Z(t_R+1) − Z(t_R)|` against the
  free-running increment to exclude a bookkeeping artifact.

## 3. Matched macrostate ≠ matched microstate (why hidden DOF are expected to be present)

`Z` is one scalar; `x` has O(10^4) active degrees of freedom. Matching `phi` fixes a codimension-1
surface in state space, not a point, so generic `x_A, x_B` on `{phi = m*}` differ. This is only a
*possibility* argument until it is shown that the histories actually place the two clones on **different**
points of that surface. The already-open DEV data answer this quantitatively.

Auditing the frozen COUNTERFACTUAL-HISTORY-CORE-00 DEV results (17 complete worlds, 57001–57024;
`KOVACS_HIDDEN_STATE_00_CANDIDATE_Z_AUDIT.json`), within-world-centred across the four histories, the
fraction of each observable's history variation that **survives a match on the primary `Z` (core-region
mass, §4)** is:

| co-observable | corr with core mass | fraction surviving at fixed core mass |
|---|---:|---:|
| body area (`body_size`) | 0.886 | 0.46 |
| shape (`body_rg`) | 0.802 | 0.60 |
| tracked body mass (`body_mass`) | 0.945 | 0.33 |
| uptake memory (`mplus_mean`) | −0.093 | 0.996 |
| order memory (`mminus_mean`) | −0.284 | 0.96 |

So even with the *weak* existing histories (all four are monotone-growth, dose-dominated), matching the
core mass leaves ~46 % of the area variation, ~60 % of the shape variation, ~33 % of the tracked
body-mass variation, and essentially all of the internal memory variation unmatched. Hidden DOF w.r.t. a
single-amount match are **present** (the body-mass-referenced version of this table, 25–57 %, is in the
audit JSON as a secondary reference). A Kovacs pair designed to diverge (an overshoot-then-decline
history against a monotone-approach history, protocol §3) is expected to place the clones far more
distinctly on `{phi=m*}` than these monotone-growth histories do.

## 4. The primary macro-observable `Z`

Primary `Z` = **core-region mass** = `sum(rho over the frozen radius-10 core mask centred at the
pre-history checkpoint focal centroid)`. Rationale (full comparison in
`KOVACS_HIDDEN_STATE_00_CANDIDATE_Z.md`): interpretable (mass in the organism's core region);
**tracker-independent endpoint** (a frozen coordinate mask, no per-step re-segmentation); **identical
support for both clones** because they share the checkpoint centroid, which makes the between-branch
difference cancel common drift exactly; strongly history-controllable (frozen dose contrast +4.56,
17/17); monotone / threshold-crossable. It **contains** the focal body mass — the geometry gate
`body ⊆ core` gives `core mass ≥ body mass`, and in DEV the core-region mass is **1.10–2.03× the tracked
body mass (median 1.38×)**, so it is explicitly *not* identical to body mass; it also includes any
peri-focal `rho` inside the fixed disk. Tracked whole-body mass is retained as a tracker-dependent
robustness co-observable that additionally indicates whether a divergence is intra-focal or driven by
peri-focal material, never the primary endpoint. The internal readouts `m_plus, m_minus` are excluded on
principle: they *are* candidate hidden coordinates, so matching on them would conflate the matched and
the tested quantity.

## 5. Present vs functionally-active: the non-trivial content

That hidden DOF are *present* at a matched amount (from §3) is close to trivial — one scalar cannot
capture a 10^4-dimensional state. The mission's establishable claim is stronger and non-trivial:
the hidden DOF are **functionally active**, i.e. they causally drive a *different future trajectory of
the macro-observable itself* under identical dynamics. Most micro-differences are dynamically
irrelevant: the fast memory channel forgets in ~30 steps, diffusion `D_m` and templating `eta_t`
homogenise local structure, and deep material turnover (below) replaces ≥75 % of the substance. Whether
a matched-`Z` difference **persists and expresses** on `Z` after all of that is a genuine empirical
question with a real null. Kovacs isolates exactly this: it does not ask "do the states differ" (they
do) but "does a difference the chosen macrostate cannot see change what that macrostate does next."

## 6. Persistence through deep turnover

Between history and match, each branch undergoes the frozen 1000-step deep-turnover interval already
validated in the parent lineage (`deep_valid` requires old focal-material fraction `M ≤ 0.25`, i.e.
≥75 % material replacement, focal bijectively tracked, coverage < 15 %). This is deliberately retained:
a Kovacs divergence that survives turnover concerns history-dependent state that is **carried or
regenerated across material replacement**, not a transient of the freshly-written memory field. It does
**not** license any ownership or continuity-of-substance claim — turnover validity is a persistence
condition on the observable, not a statement about which cells "belong" to the organism.

## 7. What a result establishes — and its strict boundary

If the frozen match, sham and common-release gates pass and the aggregated between-history excursion is
non-zero in the frozen direction (`HIDDEN_STATE_SUPPORTED`), the established claims are exactly two:

1. **Insufficiency of `Z`**: the selected macrostate `Z` is not an autonomous descriptor of its own
   evolution under the engine's dynamics.
2. **Functionally relevant hidden history-dependent DOF**: some history-dependent degree of freedom
   invisible to `Z` at the match is causally active on the future of `Z`.

It does **not** establish, and the protocol forbids inferring: identical complete physical states;
local ownership; individual identity; active reconstruction; heredity; or agency. A conserved-sign
divergence driven by a match at differing `dZ/dt` is a *legitimate* Kovacs signature (in the classical
effect the two protocols also match volume at differing rates); the required direct-relaxation
reference, identical-history clone control and one-step discontinuity diagnostic exist to show the
divergence is dynamical, not a matching artifact.

If the gates pass but no divergence is established (`Z_SUFFICIENT_NOT_ESTABLISHED`), the result is a
bounded null: it is **never** converted into proof that `Z` is sufficient, that no hidden state exists,
or that the organism lacks memory. It states only that this design, at this power, did not exhibit a
functionally-active hidden coordinate on `Z`.

If the match, timing, common-release, viability or manipulation gates fail (`MATCH_INVALID`), or valid
gates leave conflicting controls (`UNRESOLVED`), no substantive claim is made in either direction.

## 8. Genuine null vs invalid match — the separation condition

The two failure modes must be distinguishable from the raw record alone (schema in
`KOVACS_HIDDEN_STATE_00_NULL_DIAGNOSTIC_SCHEMA.json`). The separating facts are:

- **matched?** `|Z_A(t_R) − Z_B(t_R)| ≤ tol` with `tol` frozen mechanically (a fixed fraction of the
  between-world checkpoint-mass scale, §protocol), and `m*` set by a frozen outcome-independent rule;
- **common release?** identical dynamics, one common boundary hash, `up_ref` clamped equal, probe-free,
  same release step / recorded branch age;
- **shams identical?** exact own-replay reproduces bit-for-bit; identical-history clone gives
  `D ≡ 0`; one-step discontinuity within the free-running bound;
- **viable?** focal bijectively tracked through the horizon, coverage < cap, no imputation of failed
  branches.

A **genuine null** is: all four blocks pass AND the between-history excursion is indistinguishable from
zero. An **invalid match** is: any block fails. Because every gate is recorded per world, a null cannot
be silently manufactured by a broken match, and a spurious "divergence" from a tracker or clamp failure
is caught as `MATCH_INVALID` rather than read as `HIDDEN_STATE_SUPPORTED`.

## 9. Summary of the logic

1. `F` is a deterministic macro-map; `Z`-sufficiency ⇔ `Z` evolves autonomously (semiconjugacy).
2. Construct two clones matched on `Z=m*` under a common environment via **history/timing, not
   surgery**; continue `F` with no probe.
3. Divergence of `Z` falsifies `Z`-autonomy and demonstrates a functionally-active hidden coordinate;
   a clean null (gates pass, no divergence) leaves `Z`-sufficiency *not established*, never *proved*.
4. Deep turnover makes the test about persistent/regenerated history, with no ownership claim.
5. Statistical unit is the original source world; histories, crossings, clones, branches and time
   points never increase `n`.
