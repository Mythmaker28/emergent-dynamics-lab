# MRFA01 — CRITERION D, AUDITED FROM ITS DEFINITION

## The formula

```
criterion_D  <=>  daughter_mass_post  >  Q_0.95[ Binomial( N_X_world_at_intervention , (1-muX)^250 ) ]
```

Source: `FMRT01/code/fmrt01_endpoint.py survivor_upper(), applied in fmrt01_run.py to NX_world`.

## Every symbol, with its scope

| Symbol | Quantity | Spatial scope | Temporal scope | Independent unit |
|---|---|---|---|---|
| `daughter_mass_post` | count of X molecules | LOCAL: a disc of radius CORE_R = 5.0 around the daughter centre, 81 of 1296 cells (6.25 % of the lattice) | a single instant, t_m + 250 | the block |
| `N_X_world_at_intervention` | count of X molecules | GLOBAL: the entire 36x36 torus, all 1296 cells | a single instant, t_m | the block |
| `(1-muX)^T_HOLD` | per-molecule survival probability | none, a scalar | the whole 250-step hold | the molecule |
| `Q_0.95[Binomial(N,(1-muX)^250)]` | a count | GLOBAL, inherited from N | the whole hold | the block |

### Why each was chosen

- **`daughter_mass_post`** — it is the quantity the daughter is supposed to be maintaining
- **`N_X_world_at_intervention`** — chosen to make the bound CONSERVATIVE: the daughter disc cannot contain more old X than the whole world holds, so no amount of diffusion into the disc can breach it. The conservatism is real and deliberate. The cost is that the reference is a different spatial object from the quantity it is compared with.
- **`(1-muX)^T_HOLD`** — decay is per-molecule Bernoulli in the frozen engine, so survival over 250 steps is exactly this
- **`Q_0.95[Binomial(N,(1-muX)^250)]`** — it makes the false-positive rate of D at most 0.05 under the null 'no new daughter-local X'

## What D actually compares

- **left_hand_side**: a LOCAL count over 6.25 % of the lattice at one instant
- **right_hand_side**: a quantile of a GLOBAL count over 100 % of the lattice
- **reference_derived_from**: WHOLE_WORLD_X_MASS
- **reference_NOT_derived_from**: ['daughter-local single-centre physics', 'parent-local physics', 'the SHAM world', 'any measured control']

The disc is **81 of 1296 cells, 0.0625 of the lattice**. The reference is computed on all of it.

## What that costs, in molecules

| | |
|---|---|
| Median bound D demands | 94.0 |
| Median daughter mass at the moment of intervention | 71.0 |
| Blocks where the bound exceeds the daughter's **entire** mass | 20 of 22 |
| Median excess | +23.0 |
| Bound as a multiple of the daughter's own decayed stock | 3.549 |
| Measured old material in the fixed disc (GLOBAL arm), median | 19.0 |
| Analytic bound / measured old material | 4.86 |

> in 20 of 22 blocks a daughter that PERFECTLY maintained its field, losing nothing, would still be scored a failure. D cannot detect maintenance; it can only detect growth.

## The decisive property: D is not invariant to world size

| World X scaled by | Median bound | SELECTIVE passes | SHAM passes |
|---|---|---|---|
| x0.5 | 49.5 | 20/22 | 22/22 |
| x1 | 94.0 | 3/22 | 8/22 |
| x2 | 181.0 | 0/22 | 0/22 |
| x4 | 352.0 | 0/22 | 0/22 |

D's right-hand side scales with the number of X molecules anywhere in the world; its left-hand side does not. Adding X in a distant corner of the lattice, with no change whatsoever to the daughter, flips D against the daughter. A criterion whose verdict depends on matter that is nowhere near the object it is about is not measuring that object. This is decisive and it does not depend on FMRT01's outcome.

## Is D alpha-valid?

Yes. D's false-positive rate really is bounded by 0.05 under its stated null, and that is worth preserving. But alpha-validity is necessary, not sufficient: a test that can never fire is alpha-valid and useless. D is close to that regime here.

## Classification

```
WORLD_SCALE_CRITERION_MISAPPLIED_TO_LOCAL_DAUGHTER
```

derived from the definition and from the scientific object 'local daughter autonomy', not from the fact that D failed. The two load-bearing facts are (i) the LHS and RHS are different spatial objects differing by a factor of 16 in area, and (ii) D is not invariant to world size or to unrelated X elsewhere, which the scientific object must be.

## What D would have needed

a reference built at the daughter's own scale that still accounts for X diffusing IN from elsewhere. FMRT01 solved the diffusion problem by inflating the reference to the whole world. The three-arm fork already contained the exact empirical answer and it was not used for the endpoint.

---

## §4 — the SHAM arm as a mechanistic falsification test

| | |
|---|---|
| SHAM daughter survives | 22/22 |
| SHAM produces X in the fixed daughter disc | 22/22 |
| SHAM Y removed | 0 |
| SHAM passes criterion D | 8/22 |
| SHAM **fails** criterion D | 14/22 |
| Agrees with FMRT01's reported 8/22 | True |

**A_D_correctly_requires_a_stronger_property** → `REJECTED`

A would require D to be a coherent measure of local function that simply sets a high bar. It is not coherent at the local scale: its verdict changes with world size and with X that is nowhere near the daughter. A high bar on the wrong quantity is not a high bar.

**B_D_is_mis_scaled_relative_to_local_function** → `SUPPORTED`

the physical reason SHAM fails D is arithmetic, not biological. The daughter disc holds a median 32.2 % of the world's X, while D's reference is computed on 100 % of it. The median SHAM daughter ends the hold at 78.5 X against a bound of 94.0. The deficit is the scope gap, and it is present even with the parent fully intact and feeding the region.

**C_the_daughter_is_not_actually_functional_even_under_SHAM** → `MECHANICALLY_REFUTED`

under SHAM the daughter Y centre survives in 22 of 22 and new X is produced inside its own fixed disc in 22 of 22, median 114 molecules. In the frozen engine X is born only where nX>0 AND nY>0, so production inside the disc requires a Y inside the disc. The daughter is a functioning source.

### The physical reason

X birth is Y-gated: engine_obtc.py _react_core draws births ~ Binomial(min(n[res],free), min(1, k*nX*nY)), so a cell with nY = 0 can never produce X. The GLOBAL arm, which removes every Y, produced EXACTLY ZERO X inside the fixed daughter disc across all 22 blocks. Production is therefore a direct, unambiguous signature of a local Y source, and it is present in both SHAM and SELECTIVE. What D measures instead is whether the local mass beats a global stock figure, which is a different question.
