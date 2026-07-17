# HISTORY-TRANSPORT-00 — DEV-only randomized-history audit

Status: **STOP-HISTORY-CONTRAST — AUDIT GATE FAILED BEFORE INTERVENTION IMPLEMENTATION — DEV ONLY — NO
PROSPECTIVE DESIGN GO — NO FEEDING PROBE EXECUTED**

Canonical parent: `8a690f64e31647e949a8cb74fbf7457f706cd437`. Machine result:
`HISTORY_TRANSPORT_00_DEV_RESULTS.json` (SHA-256
`2dfc6b66f6a9be3ce2082f9ce1a37d229291faed459b292d594d6cf5a20b63e9`). The audit used only already-open DEV
seeds `50001-50010`. It did not open a family, compute a new future-feeding endpoint, implement a clamp arm, select a
margin, or reinterpret 03G or ACCESS-STRUCTURE Phase 0-0.7.

## 1. Independent scientific judgment

The proposed causal question is good, and it genuinely avoids the arbitrary zero-memory reference that stopped
CORE-SUFFICIENCY-00. It cannot be answered from the existing local-individuation worlds, however, because those
worlds contain **no prospectively assigned categorical histories `H_A` and `H_B`**. They contain three independently
drawn continuous amplitude pairs per eligible world. The implemented allocation is neither categorical nor blocked,
and the balanced Latin-square allocation promised in the historical preregistration is absent from the code.

Any current A/B analysis would therefore require a retrospective rule: threshold cumulative dose, threshold order,
rank targets, or select the most separated pair. Those rules can be made feeding-blind, but they do not become
prospective randomized assignments. The mission explicitly makes this an audit-gate failure, so the correct decision
is **STOP-HISTORY-CONTRAST**, not REVISE and not a weak pilot.

This is a failure to identify the requested estimand, not evidence that local-history transport is absent.

## 2. Exact recovered history assignment

The same implementation appears in `exp1_prospective.py`, `causal_confirm.py`, `turnover_dev_runner.py`, and
`turnover_engine_03g.py`:

1. warm the same C1c world for 800 steps;
2. select `K=3` targets by size `>=45` and pairwise periodic centroid distance `>=24`;
3. initialize `np.random.default_rng(world_seed)` — the same numeric seed namespace used for the world;
4. make six sequential independent draws from `[0.005, 0.035)`, grouped as `(a1,a2)` for target indices `0,1,2`;
5. add a target-centred Gaussian nutrient patch with `sigma=max(3,0.8*r_g)` for 60 steps at `a1`, then 60 steps at
   `a2`, simultaneously for all targets;
6. settle 120 steps;
7. define continuous `dose=a1+a2` (primary) and `order=a2-a1` (secondary).

There is no A/B label, treatment vector, random permutation, blocking variable, or Latin-square table. Assignment is
generated before future feeding and is therefore outcome-blind, but it is not a categorical randomized treatment and
uses no independent randomization namespace.

Exact eligible-world pairs `(a1,a2)` are below; the JSON preserves full float64 values.

| world | target 0 | target 1 | target 2 | deep disposition |
|---:|---:|---:|---:|---|
| 50001 | (0.033303, 0.030259) | (0.005081, 0.028979) | (0.031953, 0.009402) | invalid: target 1 split at +153 |
| 50002 | (0.029655, 0.015181) | (0.022643, 0.009276) | (0.025249, 0.029476) | valid, deep +847 |
| 50003 | (0.017385, 0.010356) | (0.014856, 0.033188) | (0.032726, 0.014714) | invalid: target 2 lost at +236 |
| 50004 | (0.032595, 0.032010) | (0.009922, 0.006043) | (0.016053, 0.034046) | valid, deep +793 |
| 50005 | (0.024588, 0.026585) | (0.008050, 0.010180) | (0.010818, 0.032408) | valid, deep +831 |
| 50006 | (0.013191, 0.033738) | (0.032793, 0.020809) | (0.034776, 0.024388) | invalid: target 0 split at +692 |
| 50007 | (0.034269, 0.021947) | (0.008704, 0.013747) | (0.027003, 0.008952) | valid, deep +890 |
| 50009 | (0.012088, 0.018165) | (0.032092, 0.018739) | (0.029441, 0.033921) | invalid: target 0 split at +436 |

Worlds 50008 and 50010 had fewer than three geometrically eligible targets and received no histories. These are
outcome-independent exclusions inherited unchanged from the already-open DEV raw data.

## 3. Audit-gate findings

| required question | finding | gate |
|---|---|---|
| exact conditions | three continuous `(a1,a2)` pairs, not A/B | recovered, but wrong estimand |
| randomized/outcome-independent | continuous draws are future-outcome-blind; no categorical randomization and no separate namespace | **fail for requested factor H** |
| both conditions within worlds | no assigned conditions exist | **fail** |
| targets per condition/world | undefined | **fail** |
| spatial balance | no blocking/Latin square; target index is size-ordered | **fail** |
| non-memory effects | all 24 assigned targets change non-memory state before the probe | **fail as a memory-specific history contrast** |
| protocol-predicted direction | higher continuous dose is the primary `m_plus` coordinate; no binary A>B contrast was defined | **fail** |
| label recovery without feeding | exact continuous values recover from seed/code; A/B cannot be recovered because none were assigned | **fail** |

The preregistration/code discrepancy is material: `experiments/individuation/PREREGISTRATION.md` says histories are
assigned by a balanced Latin-square design, while every executable generator directly assigns sequential RNG draws
to size-ordered target indices. Realized target-index means are unequal (`0: 0.04816`, `1: 0.03439`, `2: 0.04942`),
and midpoint-high counts are `6/8`, `3/8`, and `7/8`, respectively. Approximate chance balance cannot substitute for
the missing design.

## 4. Why the obvious A/B repairs are invalid

All following rules are outcome-blind, and all are still rejected:

| candidate rule | observed availability | reason rejected |
|---|---|---|
| dose above/below the protocol-range midpoint `0.04` | both labels in 7/8 eligible worlds; world 50006 is 3/0 | retrospective dichotomization; not assigned |
| order `a2-a1 >= 0` versus `<0` | both labels in 7/8 eligible worlds; deep-valid world 50005 is 3/0 | retrospective dichotomization; order was continuous/secondary |
| max-dose versus min-dose | always produces one pair | post-assignment selection and discards the middle target |
| maximum `(dose,order)` separation | always produces one pair | Phase-0.5 engineering helper, not historical assignment; discards a target |

No feeding outcome was consulted to reach these rejections.

## 5. Pre-probe body, geometry, nutrient, and physical-state audit

For each of the 24 assigned targets, the audit reconstructed the post-history snapshot and the same-seed,
same-time no-drive counterfactual. It stopped before nutrient standardization or any future-feeding probe.

Every target changed in at least one of `rho,U,V,c,N` beyond the float64 numerical criterion. Across targets:

| pre-probe history minus no-drive diagnostic | range | mean |
|---|---:|---:|
| detected size difference | -30 to +61 cells | +17.5 |
| mass difference | -18.208 to +46.938 | +15.345 |
| radius-of-gyration difference | -3.630 to +4.309 | +0.288 |
| centroid separation | 0.020 to 6.898 cells | 1.094 |
| body-mask IoU | 0.000 to 0.975 | 0.716 |
| local `rho` RMS difference | 0.076 to 0.290 | 0.185 |
| local `U` RMS difference | 0.071 to 0.405 | 0.238 |
| local `V` RMS difference | 0.053 to 0.347 | 0.168 |
| local `c` RMS difference | 0.048 to 0.208 | 0.123 |
| local `N` RMS difference | 0.208 to 1.003 | 0.583 |
| complete two-channel `Mf` RMS difference | 0.045 to 0.148 | 0.107 |

This does not invalidate the historical continuous-memory result. It does mean the nutrient histories are not
memory-only assignments: a future A/B effect could be expressed through body, geometry, nutrient exposure, internal
physical state, memory, or their combination. A new design would need to address `H_0` prospectively; target-level
residualization cannot repair the missing randomization and would not make targets independent.

## 6. First-stage result

The requested `H_A-H_B` first stage for complete `Mf`, `m_plus/m_minus`, spatial organization, body/geometry,
nutrient/physical state, and the frozen 11-D fingerprint is **not estimable**, because no assigned H groups exist.

For transparency only, applying the rejected `dose>=0.04` split to the passive deep `m_plus` diagnostics gives
world-level A-B values:

| world | rejected midpoint-split deep `m_plus` A-B |
|---:|---:|
| 50002 | +0.03457 |
| 50004 | -0.03127 |
| 50005 | -0.01502 |
| 50007 | -0.09490 |

The sign changes. The rejected order-sign split is available in only three deep worlds and gives
`+0.11532, -0.06819, +0.08465`. These values are not estimands and cannot be used to choose a history rule. The
historical frozen 11-D decoder may recover continuous own dose across worlds; decoding a continuous coordinate is not
a categorical randomized first stage.

## 7. Complete world-level causal estimands

The intervention gate stopped before implementation, so unavailable values are reported as **N/A, not zero**.

| original world | assigned `n(H_A),n(H_B)` | `delta_coupled` | `delta_isolated` | transport difference | retention ratio |
|---:|---:|---:|---:|---:|---:|
| 50002 | N/A | N/A | N/A | N/A | N/A |
| 50004 | N/A | N/A | N/A | N/A | N/A |
| 50005 | N/A | N/A | N/A | N/A | N/A |
| 50007 | N/A | N/A | N/A | N/A | N/A |

The other six worlds are the outcome-independent feasibility dispositions in Section 2. No target-level outcome was
treated as a replicate, no model was fit, and no retention ratio was regularized or invented.

## 8. Boundary, global-channel, mediation, and manipulation status

No HISTORY-TRANSPORT arm was run. Prior ACCESS mechanics establish one candidate history-independent reference: the
qualified two-cell replay of a same-seed no-history trajectory. The exact own-trajectory replay is a useful
manipulation sham but may carry the target history, so it is not a common isolation reference. No second independent,
on-manifold, history-independent boundary construction is currently qualified; reference robustness therefore also
remains unavailable.

All technically defensible `up_ref` options were audited without selecting by outcome:

| global rule | identification | current status |
|---|---|---|
| predefined no-history trajectory | history-independent, time-varying, on-manifold | strongest future primary candidate; not run here |
| predefined no-history constant | history-independent | requires a frozen source/time rule and continuity qualification |
| `up_ref=0` | removes global information | engine-valid prior secondary ablation, not ordinary coupling |
| ordinary dynamic `up_ref` | may contain history | cannot identify local sufficiency if left history-bearing |

The frozen normal engine would remain primary in a valid future design and `lam_plus=0` secondary. Neither was run
here because there is no randomized history contrast to mediate. Manipulation diagnostics at steps 0/1/5/10/20/40,
boundary-reference effects, and global dependence are therefore N/A rather than passed.

## 9. Competing hypotheses, including H_RELATIVE

`H_RELATIVE` remains scientifically plausible but unestablished. Existing observations—large erase effects,
substantial ambient memory in no-history twins, and reversal between erase and twin references—are consistent with a
relative-history account. They are also compatible with several other mechanisms. The distinctive prediction needed
here, survival of an assigned history contrast under common inputs, was not testable. Full-field or spatial
correlations cannot be selected from these outcomes to manufacture a first stage.

See `HISTORY_TRANSPORT_00_HYPOTHESIS_TABLE.md` for the complete competing-hypothesis logic.

## 10. Decision, permitted claim, and human action

Decision: **STOP-HISTORY-CONTRAST**, which entails **STOP-HISTORY-TRANSPORT for this mission**. The failure is not one
bounded operator correction; it is the absence of the treatment factor that defines the primary estimand. Therefore
the mission's REVISE route does not apply.

Permitted claim:

> The legacy local-individuation DEV worlds used outcome-blind continuous nutrient histories, not prospectively
> assigned categorical histories A and B. Consequently randomized local-history transport under causal isolation was
> not tested, and no conclusion about its presence or absence is licensed.

No prospective claim, family, practical margin, equivalence margin, minimum-valid-world threshold, decoder, or power
calculation can be frozen from this audit. A future attempt requires a **new human-authorized protocol**, created
before data, that actually assigns H_A/H_B within worlds, implements the allocation it preregisters, demonstrates a
protocol-predicted post-turnover first stage without outcome-selected features, addresses the observed body/geometry/
nutrient changes, qualifies at least two valid common boundary references, and freezes global-channel handling and
all kill-switches. It is not authorized by this report.
