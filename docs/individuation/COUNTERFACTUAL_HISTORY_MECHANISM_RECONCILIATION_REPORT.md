# COUNTERFACTUAL-HISTORY-MECHANISM-RECONCILIATION-00

## Independent scientific judgment

**Decision: `UNRESOLVED`.**

The dose-dependent feeding effect is strongly consistent with ordinary physical carryover: high-dose histories produce larger bodies, larger occupied area, larger core/world `rho`, altered `c/v`, and higher baseline uptake before the common probe. Dividing feeding by pre-probe mass or body-cell area removes and reverses the positive total-feeding contrast. However, the frozen body/geometry models do not predict the feeding contrast reproducibly outside the held-out original world in both coupled and isolated arms. `PHYSICAL-CARRYOVER-ONLY` is therefore not established.

Targeted `mplus/mminus` variables add no reproducible LOWO information and generally worsen prediction. The positive `m_minus` EARLY-minus-LATE sign is explained by correcting the frozen two-timescale theory: slow `m2` retains the early episode more strongly, so `m1-m2` has a positive—not negative—contrast. The state is small and persists through both probe conditions, but the feeding order contrast remains null. It is a theory/sign correction with a non-functional targeted state under this probe, not an order-memory or landscape discovery.

No condition justifies a causal-landscape pilot, and no new seed is authorized.

## Provenance and scope

- accepted parent and final result commit: `ea6e6a0ab2ccc3e94eba364ddb459088c96d6033`;
- frozen raw SHA-256: `d4e6f2d9cedcc8b459973e10641b1b28d91b3b52315cbba36120640ef9386da6`;
- manifest SHA-256: `298dcc02d391eb8952d3d293fdaf1bcd9ceef2c032d8e521771ee50cce569457`;
- 24 already-open DEV worlds, 17 complete original-world blocks;
- no new world, history, namespace, or prospective execution;
- branch potential outcomes never count as replicates;
- all scaling and fitting occur inside each original-world held-out fold.

The same-manifest replays are diagnostic re-observations required because the parent JSON did not retain target memory and baseline uptake at the standardized and final probe checkpoints. All 17 replays matched the parent exactly on 32 frozen hashes/feeding values per world. They are not an independent confirmation.

## 1. Sign derivation verdict

The exact engine writes `m1` and `m2` with the same endogenous `Psi`, but `eta_d1=0.35` and `eta_d2=0.006`. In the homogeneous recurrence `m_{k,t+1}=(1-dt eta_dk)m_{k,t}+dt eta_w x_t`, two 60-step episodes followed by 120 settle steps give

`m_k(EARLY)-m_k(LATE) = -dt eta_w Delta q_k^120 (1-q_k^60)^2/(1-q_k)`.

For `Delta=0.01`, the fast difference is `-4.64e-06`, the slow difference is `-2.91e-05`, and the corrected `m_minus=tanh(m1-m2)` order is `+2.44648e-05`. The frozen negative orientation was a convention/theory error in the intended reduced model. The exact nonlinear trajectory is still required for magnitude and is not governed by an amplitude-only sign theorem. Full algebra is in `M_MINUS_SIGN_DERIVATION.md`.

## 2. Order-state characterization

All values below are original-world paired factorial contrasts. Intervals are 95% Student-t intervals.

| checkpoint | coupled `m_minus` order | isolated `m_minus` order | signs |
|---|---:|---:|---:|
| deep pre-probe | `+0.003668 [0.003064, 0.004272]` | identical | 17/17 positive |
| standardized pre-stimulus, settle step 40 | `+0.003820 [0.003157, 0.004483]` | `+0.003734 [0.003074, 0.004393]` | 17/17 positive in each |
| probe horizon step 40 | `+0.003434 [0.002625, 0.004243]` | `+0.002833 [0.002089, 0.003577]` | 16/17 positive in each |

The isolated-minus-coupled order difference is `-8.64e-05 [-2.70e-04, +9.69e-05]` before stimulation and `-6.01e-04 [-1.19e-03, -1.37e-05]` at the final checkpoint. Thus isolation modestly attenuates the final positive state, but does not create or reverse it.

Low and high dose strata agree:

| checkpoint | low EARLY−LATE | high EARLY−LATE |
|---|---:|---:|
| deep pre-probe | `+0.003875 [0.003028, 0.004722]` | `+0.003461 [0.002884, 0.004038]` |
| coupled final step 40 | `+0.003621 [0.002267, 0.004975]` | `+0.003247 [0.002652, 0.003842]` |
| isolated final step 40 | `+0.002721 [0.001409, 0.004032]` | `+0.002946 [0.002485, 0.003407]` |

The contrast is consistent but small: roughly `0.003--0.004` on a bounded tanh readout whose branch means are around `-0.27` to `-0.32`. It is dominated by `m2` (`m2` order `-0.003883`, 17/17 negative), while `m1` order is near zero. Crucially, the parent feeding order contrasts cross zero: coupled `-0.003812 [-0.013689, +0.006064]`; isolated `-0.004693 [-0.014432, +0.005047]`. The corrected state has no targeted feeding-order function established here.

## 3. Physical decomposition of dose feeding

Pre-probe dose contrasts show a broad physical shift:

| quantity | mean dose contrast [95% interval] | sign pattern |
|---|---:|---:|
| body mass | `+3.626 [2.469, 4.783]` | 17/17 positive |
| body area (`body_size`) | `+4.059 [2.276, 5.842]` | 15 positive, 1 negative, 1 zero |
| body radius of gyration | `+0.128 [0.071, 0.185]` | 15/17 positive |
| core `rho` mass | `+4.556 [3.551, 5.561]` | 17/17 positive |
| world `rho` mass | `+5.637 [4.701, 6.574]` | 17/17 positive |
| core nutrient `N` | `+0.000375 [-0.000654, 0.001404]` | heterogeneous |
| world nutrient `N` | `+0.000811 [0.000598, 0.001024]` | 17/17 positive |
| core attractant `c` | `+0.04219 [0.03403, 0.05036]` | 17/17 positive |
| core `u` | `+0.00439 [-0.02787, 0.03665]` | heterogeneous |
| core `v` | `+0.02726 [0.00643, 0.04808]` | 14/17 positive |
| core `sigma` | `-0.01237 [-0.03452, 0.00978]` | heterogeneous |
| nearest-neighbour distance | `-0.700 [-2.254, 0.853]` | heterogeneous |
| world baseline uptake (`up_ref`) | `+1.737e-06 [1.255e-06, 2.218e-06]` | 17/17 positive |
| focal instantaneous uptake, deep pre-probe | `+0.002041 [0.000323, 0.003760]` | 12 positive, 5 negative |
| focal uptake after standardization settle | coupled `+0.002220 [0.000456, 0.003985]`; isolated `+0.002175 [0.000393, 0.003958]` | intervals positive |

The frozen total-feeding effects are coupled tracked `+0.18776 [0.05195, 0.32357]`, isolated tracked `+0.17904 [0.03878, 0.31930]`, coupled fixed-mask `+0.17875 [0.02942, 0.32809]`, and isolated fixed-mask `+0.17463 [0.02390, 0.32536]`. The similar tracked and fixed-mask effects argue against tracker association as their source.

The two formulas frozen before inspecting their values are explicitly exploratory:

- tracked integrated uptake / pre-probe mass: coupled dose `-0.01017 [-0.01520, -0.00513]`, isolated `-0.01065 [-0.01633, -0.00497]`;
- fixed integrated uptake / pre-probe body-cell area: coupled `-0.004554 [-0.008835, -0.000272]`, isolated `-0.004650 [-0.008995, -0.000304]`.

The positive total effect disappears and reverses after simple size normalization. This is strong descriptive evidence for physical scaling/carryover, but ratio normalization is secondary and cannot alone prove the causal decomposition.

## 4. Out-of-world prediction

The fixed ridge family (`alpha=1`, training-fold scaling only) predicts each original world's tracked-feeding dose contrast from the other 16 worlds.

| arm / model | LOWO Q2 | RMSE | mean squared-error improvement vs training mean [95% interval] |
|---|---:|---:|---:|
| coupled mass/area | `+0.121` | `0.240` | `+0.0164 [-0.0353, 0.0681]` |
| coupled body/geometry | `+0.142` | `0.237` | `+0.0178 [-0.0331, 0.0687]` |
| coupled body/geometry + targeted memory | `-0.317` | `0.294` | `-0.0123 [-0.0813, 0.0566]` |
| isolated mass/area | `-0.014` | `0.266` | `+0.0081 [-0.0449, 0.0610]` |
| isolated body/geometry | `-0.119` | `0.280` | `+0.0007 [-0.0663, 0.0677]` |
| isolated body/geometry + targeted memory | `-0.591` | `0.334` | `-0.0323 [-0.1161, 0.0514]` |

Adding targeted memory changes squared error by coupled `-0.03014 [-0.06192, +0.00163]` and isolated `-0.03303 [-0.06862, +0.00257]`; negative means worse. It fails the frozen incremental-value criterion.

The body/geometry panel also fails its strict explanation criterion because its improvement interval crosses zero in both arms and isolated Q2 is negative. With only 17 complete worlds, this is insufficient to distinguish imperfect physical modeling from a genuine residual. No clone- or target-level pseudoreplication was used.

## 5. Decision and claim boundary

- `CAUSAL-LANDSCAPE-JUSTIFIED`: **no**. The corrected small order state has no feeding-order function, its reduction to body/geometry was not identified, no validated nonphysical residual exists, and no named landscape perturbation direction remains.
- `PHYSICAL-CARRYOVER-ONLY`: **not established**. Descriptive evidence is strong, but the fixed physical model does not generalize in both arms.
- Final: **`UNRESOLVED`**.

Permitted interpretation: causal dose-dependent feeding occurred in this DEV counterfactual design; its targeted memory mediation was not established; ordinary physical carryover is the leading candidate; and the frozen negative order prediction failed because its reduced-theory orientation was wrong.

This does not establish absence of all memory, local ownership, order memory, causal-landscape memory, identity, or heredity.

## Exact next human decision

Keep the causal-landscape pilot at **NO-GO**. Human review must either accept `UNRESOLVED` and close this line, or explicitly authorize preparation—not execution—of a new `BODY-EQUALIZATION-00` preregistration. Its required directional prediction would be that equalizing pre-probe body mass/area and the named core physical panel collapses the dose contrast in frozen step-40 integrated tracked uptake. Until that design and its manipulation equivalence are reviewed, no new seeds or landscape search are authorized.
