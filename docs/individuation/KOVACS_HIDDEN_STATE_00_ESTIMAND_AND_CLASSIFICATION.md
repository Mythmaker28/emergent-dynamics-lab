# KOVACS-HIDDEN-STATE-00 — causal estimand and classification table (Phase-0 design)

**Statistical unit.** The original source world `w`. Histories, crossings, clones, branches, reference/
sham arms and time points never increase `n`. All summaries are over the set of **complete** worlds.

## 1. Per-branch Kovacs hump (excursion from the matched macrostate)

For branch `b ∈ {OVER, APPR}` in world `w`, released at its match step `t_R^b` with `Z_b(t_R^b) ≈ m*`,
the probe-free relaxation `Z_b(t_R^b + s)` for `s = 0 … T_hor` is compared to the **direct-relaxation
reference** `Z_ref` — the common history-independent no-drive continuation, which by construction passes
through `m*` at `t_ref` — evaluated from the same macrostate: `Z_ref(t_ref + s)`.

The signed Kovacs hump of branch `b` is the trapezoidal area of the departure from the directly-relaxed
reference over the fixed horizon (step units):

```
K_b(w) = Σ_{s=0..T_hor} [ Z_b(t_R^b + s) − Z_ref(t_ref + s) ] · Δs           (signed area; Δs = 1 step)
```

If `Z` were a sufficient macrostate (§2 of the derivation), a branch released at `m*` would follow the
directly-relaxed reference and `K_b(w) = 0`. A nonzero `K_b` is the hump: relaxation from the *same*
macrostate that depends on hidden history.

## 2. Primary estimand — between-history hump difference

```
D_w = K_OVER(w) − K_APPR(w)  =  Σ_s [ Z_OVER(t_R^OVER + s) − Z_APPR(t_R^APPR + s) ] · Δs
```

`D_w` is the between-history difference of the two Kovacs humps in world `w`. It is the primary estimand
because:

- it **cancels the common reference** and any shared environmental forcing (the `Z_ref` term drops out),
  so it is not an artifact of `m*` failing to be an equilibrium;
- it is **exactly zero under `Z`-sufficiency** (both branches would track the reference), so a
  systematic nonzero `D_w` is a direct falsification of `Z`-autonomy;
- on the **frozen common core mask** the two `Z` are sums over the *same* cells, so `D_w` differences
  like-for-like with no tracker/support mismatch.

**Aggregation (frozen).** Over the complete worlds compute mean, median, standard deviation, the 95 %
Student-t interval, and the sign count of `{D_w}`. `n` = number of complete worlds. No scaling or
fitting is applied to the primary estimand.

**Signed vs absolute.** The primary rule is **two-sided / unoriented** (the project's unoriented gate),
because a frozen sign is not derived from any observed excursion. A secondary, theory-motivated
directional expectation (that the overshoot branch — arriving from a larger body — carries greater
residual core mass, giving `D_w > 0`) is recorded but does **not** set the primary gate and is reported
descriptively.

## 3. Frozen decision gate

Let the **validity block** for a world be: both branches matched (`|Z_b(t_R^b) − m*| ≤ tol`); focal
bijectively tracked through `t_R + T_hor`; coverage < cap; common boundary hash identical across
branches; `up_ref` clamped equal; own-replay sham bit-exact; identical-history clone `D ≡ 0`; and
one-step discontinuity within the free-running increment. A world failing any of these is **not**
complete and is censored (never imputed).

- **Primary gate (unoriented):** across complete worlds, `{D_w}` has **≥ 75 % common sign** AND its
  **95 % t-interval excludes zero**.
- **Minimum worlds:** a pre-declared minimum number of complete worlds `N_min` (proposed ≥ 12 of the 24
  DEV worlds for a DEV read; the confirmatory `N_min` and power to be locked by the power analysis at
  seal). Fewer than `N_min` complete → `DEV-FEASIBILITY-FAIL` (design-level; no substantive inference).
- **Robustness concordance:** the frozen-mask primary `Z` (core mass) and the tracked body-mass
  robustness reading must agree in sign of the aggregate; disagreement routes to `UNRESOLVED`.
- **Age control concordance:** the crossing-rule variant and the equal-age variant must agree in sign;
  disagreement routes to `UNRESOLVED` (age cannot be excluded as the driver).

## 4. Classification table

| outcome | Boolean condition | meaning (bounded) |
|---|---|---|
| **HIDDEN_STATE_SUPPORTED** | validity block passes for ≥ `N_min` worlds; own-replay & identical-history & discontinuity shams clean; primary unoriented gate on `D_w` passes; robustness and age-control concordance hold | `Z` is **not** a sufficient macrostate; a functionally-active hidden history-dependent DOF acts on the future of `Z`. **No** claim of identical state, ownership, identity, reconstruction or heredity. |
| **Z_SUFFICIENT_NOT_ESTABLISHED** | validity block passes for ≥ `N_min` worlds; shams clean; primary gate on `D_w` **not** met (interval includes zero or sign inconsistent) | Bounded null: no divergence established at this power. **Never** converted into "`Z` is sufficient", "no hidden state", or "no memory". |
| **MATCH_INVALID** | fewer than `N_min` worlds are matchable (both branches within `tol`) — equivalently, the match fails for more than (`N_total` − `N_min`) of the `N_total` eligible worlds — OR timing/common-release/`up_ref`/viability/one-step-discontinuity/manipulation gate fails where estimable | The match or common release is not established; neither divergence nor null is interpretable. |
| **UNRESOLVED** | validity passes but controls conflict (robustness sign disagreement, age-variant disagreement, or own-replay/identical-history anomalies) or power is insufficient | No classification; specify the conflicting controls. |

## 5. Guardrails on interpretation

- A positive result is **not** evidence of ownership/identity/reconstruction/heredity; it is
  insufficiency of one scalar plus a functionally-active hidden coordinate (derivation §7).
- A result is **not** valid merely because the two branches later differ: the release intervention,
  timing, boundary and `up_ref` must be common and pre-declared, and the shams must be clean. A
  divergence with a failed validity block is `MATCH_INVALID`, not `HIDDEN_STATE_SUPPORTED`.
- `Z_SUFFICIENT_NOT_ESTABLISHED` is a statement about this design's power, never a sufficiency proof.
- Every threshold here (`tol`, `A_min`, `t_ref`, `T_hor`, `N_min`, 75 %/95 %) is frozen before data and
  is **not** selected from any excursion.
