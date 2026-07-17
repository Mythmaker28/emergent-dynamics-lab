# ACCESS-STRUCTURE-00 — Phase 0.6A boundary-safe operator qualification

**Status: COMPLETE — STOP-TRANSPLANT — NO TECHNICAL GO — NO SCIENTIFIC FEEDING TEST — HUMAN REVIEW REQUIRED**

This is an operator-engineering result on the already-open DEV namespace only. It does not locate the
turnover-surviving causal state and does not alter certified 03G Outcome B, V4.1, V5, or certified raw results.

## 1. Independent scientific judgment

The Phase 0.5 hard-cut failure reproduced exactly. Its maximum `22.872170460755093x` seam is a real local
donor/recipient mismatch, not a missing scheduler phase, coordinate error, tracker artefact, or uncarried previous
buffer. It occurs for `rho` in seed 50002 arm `C_B_E_A`; the same interface changes the two physical face-flux RMS
values by `79.05x` and `86.74x` their recipient-natural values. Donor and recipient body IoU there is only `0.465`,
and four donor outer-interface cells are occupied where the recipient has none.

The two predeclared repair families solve individual-arm totals but not causal interpretability. The best candidate,
`RIP_HARD_R8`, keeps every arm viable, retains the donor memory payload, makes the original outer seam exactly
natural, and greatly reduces outward propagation. It does so by moving the discontinuity inward. At that internal
interface, independently balancing `rho`, `U`, and `V` clips density while leaving extensive internal fields
positive, so `u=U/rho` and `v=V/rho` become singular in near-empty cells. Its worst all-interface ratio is
`1.7598e11`; even excluding those derived concentrations, `rho`, `c`, `N`, and `m_plus` reach `208.78x`, `9.56x`,
`9.96x`, and `7.63x` recipient-natural variation. This is not a near miss against `1.25x`.

Wider quintic transitions reduce several raw-field ratios but still fail the unchanged envelope, lose tracking
viability, and at radius 7 lose the frozen donor-body coverage guard. No configuration simultaneously preserves
payload, body/update consistency, physical balance, seam bounds, and viability. The outcome is therefore
**STOP-TRANSPLANT**, not another radius/taper scan. This stops this surgical transplant route as operationalized;
it is not a claim that local, environmental, redundant, or synergistic access is absent.

## 2. Scope, data, and frozen execution

- Branch: `codex/access-structure-boundary-repair-06`, required parent
  `fa261734300631f16ca5e0bacceba11d5f7ddc1e`.
- Checkpoint implementation/specification commit: `59b4dda1a5b74a14f9a268391d73ea0788181368`, pushed before qualification.
- Seeds requested: exactly `50001-50010`; operators ran only on existing deep-feasible worlds
  `50002,50004,50005,50007`.
- Existing no-operator dispositions were preserved for the other six worlds.
- Complete fixed grid: two families, four configurations, 24 arms/configuration (4 worlds x 6 technical arms).
- Measurement times: `0+,1,5,10,20,40`.
- Active crossed-arm feeding measurements: **zero**. Storage hypotheses evaluated: **zero**.

Execution command:

```powershell
C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe `
  -m experiments.individuation.access_structure_boundary_safe_qualification `
  --output docs\individuation\ACCESS_STRUCTURE_00_PHASE06A_RESULTS.json `
  --seeds 50001 50002 50003 50004 50005 50006 50007 50008 50009 50010
```

Machine-result SHA-256:
`8A3260EE48E0451C988E03F527D5FB507A1B684A345147A43569E38F5AE3A7BB`.

## 3. Phase 0.5 failure re-audit

The exact Phase 0.5 runner was executed inside the new qualification. All exact controls were again zero, all six
old active arms were again 4/4 viable, and the old failure summary reproduced byte-for-value at the reported
summary level:

| Quantity | Re-audit |
|---|---:|
| maximum outer seam ratio | `22.872170460755093` (`rho`, seed 50002, `C_B_E_A`) |
| values passing `1.25x` | `4/168` |
| individual-arm balance | fail |
| maximum old arm deltas | `c=84.5781`, `U=58.1427`, `rho=40.7211` |
| reciprocal-pair conservation | `9.095e-13` maximum; still not an arm-level control |
| exact coordinate/no-op/round-trip/reinsert/matched shams | `0.0` |
| active crossed feeding | not evaluated |

For the maximum-seam arm, recipient-natural versus post-cut mean jumps were:

| View | Natural | Post-cut | Ratio |
|---|---:|---:|---:|
| `rho` | `0.0027953` | `0.0639353` | `22.8722` |
| `N` | `0.0037553` | `0.0199666` | `5.3170` |
| `c` | `0.0217903` | `0.1107042` | `5.0804` |
| `m_plus` | `0.0452959` | `0.2860179` | `6.3144` |
| `u` | `0.1121028` | `0.6542698` | `5.8363` |
| prior-step `uptake` | `1.517e-5` | `1.748e-4` | `11.5221` |

The new bands show that the exact hard cut changes only payload core/interface collar at `0+`, then propagates:

| Step | payload core max RMS | interface collar | inner halo | outer halo | far environment |
|---:|---:|---:|---:|---:|---:|
| `0+` | `1.3469` | `1.2076` | `0` | `0` | `0` |
| 1 | `1.3469` | `1.1379` | `0.5514` | `2.90e-4` | `1.43e-8` |
| 5 | `1.3472` | `1.0648` | `0.6548` | `0.2662` | `6.28e-5` |
| 10 | `1.3477` | `0.9985` | `0.7236` | `0.2978` | `0.00117` |
| 20 | `1.3484` | `0.9832` | `0.7829` | `0.3992` | `0.02798` |
| 40 | `1.3386` | `0.9535` | `0.8344` | `0.4800` | `0.04425` |

Values are maximum per-field RMS, not a cross-field scalar score. The driver changes by band and time; the initial
maximum is `u/v` inside the transplanted state, while the `22.872x` outer seam is specifically `rho`.

## 4. Operator families and payload guard

The grid was committed and pushed before execution.

1. `RIP_HARD_R9` and `RIP_HARD_R8`: preserve the recipient outer interface, substitute only radius-9 or radius-8
   interior, and apply recipient-shaped local total correction.
2. `CPP_QUINTIC_R8` and `CPP_QUINTIC_R7`: retain a full donor core and use a quintic transition to recipient state
   through outer radius 10, with the same local constrained correction.

Physical `rho,U,V,c,N` totals are matched separately in each arm. Passive base cohorts preserve both their
per-cell sum-to-`rho` invariant and recipient channel totals. `Mf/rho` remains the protected payload and is not
total-matched. Stored prior-step `uptake` remains recipient state because the next update does not read it.

Payload passes only if the frozen 11-feature `L` contrast projection and every defined memory projection are at
least 0.50 and at least 90% of the donor body lies in the full-weight core. No feeding enters this guard.

## 5. Complete grid results

| Configuration | Per-arm physical totals | Valid/trackable arms | worst outer seam | worst all-interface seam | min `L` projection | min memory projection | min body coverage | Payload | GO |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| `RIP_HARD_R9` | pass | 21/24 | `1.0x` | `2.1790e11x` | `0.8020` | `1.0000` | `1.0000` | pass | no |
| `RIP_HARD_R8` | pass | **24/24** | `1.0x` | `1.7598e11x` | `0.6790` | `1.0000` | `0.9492` | pass | no |
| `CPP_QUINTIC_R8` | pass | 22/24 | `1.5100e9x` | `4.7254e10x` | `0.5713` | `1.0000` | `0.9492` | pass | no |
| `CPP_QUINTIC_R7` | pass | 22/24 | `1.6345e9x` | `3.8448e10x` | `0.5713` | `1.0000` | `0.8983` | **fail** | no |

Tracking losses were pre-endpoint technical failures: three arms for `RIP_HARD_R9`, two for `CPP_QUINTIC_R8`, and
two for `CPP_QUINTIC_R7`. `RIP_HARD_R8` is the only configuration with 24/24 valid arms.

The seam conclusion is insensitive to reasonable thresholds. Counts at or below `1.25/1.5/2/3/5x`, out of 216
field-arm-world values, were:

- `RIP_HARD_R9`: `28/29/40/60/133`;
- `RIP_HARD_R8`: `31/32/40/54/130`;
- `CPP_QUINTIC_R8`: `49/81/155/192/194`;
- `CPP_QUINTIC_R7`: `66/128/177/191/198`.

Even the widest transition leaves 18 values above `5x`, loses two arms, and misses body coverage in two arms. No
conclusion depends on the single `1.25x` cutoff.

## 6. Individual-arm balance and body/energy audit

Across all candidates, maximum absolute global deltas were:

- `rho,U,V`: `5.684e-14` each;
- `c`: `2.274e-13`;
- `N`: `4.547e-13`;
- diagnostic `C`: `1.900e-11` maximum and inside the relative float64 criterion;
- stored prior-step `uptake`: `0`;
- base-cohort `sum(C)-rho`: `2.554e-15` maximum.

Thus the new operators genuinely solve the old per-arm scalar-total defect. They do not solve body/on-manifold
balance. Non-negative active-set correction fired in 39-41 physical field/arm combinations per configuration.
Because the five physical arrays were projected independently, clipped `rho` can coexist with positive `U/V`,
manufacturing extreme intensive concentrations. On the fixed expected-donor support, immediate mass can change by
up to 130.6% even for `RIP_HARD_R8`; donor/recipient body IoU reaches 0.238 in the standardization arms. A scalar
global ledger is therefore not a body-state ledger.

The engine has no energy variable or conserved Hamiltonian. The predeclared diagnostic proxies show that bulk
`c/N` L2 magnitude changes by at most 1.80-2.67% inside a region, while the `c/N` gradient proxy rises by as much as
160% (`CPP_R7`), 208% (`CPP_R8`), 231% (`RIP_R8`), and 348% (`RIP_R9`). Matching field totals does not match the
field organization that drives flux.

## 7. Best candidate and propagation tradeoff

`RIP_HARD_R8` is the best of the failed operators because it alone combines 24/24 viability, exact active-operation
shams, per-arm scalar balance, outer seam ratio 1.0, and payload pass. Its maximum band RMS values are:

| Step | payload core | preserved interface collar | inner halo | outer halo | far environment |
|---:|---:|---:|---:|---:|---:|
| `0+` | `2.5471e11` | `0` | `0` | `0` | `0` |
| 1 | `154.21` | `0.4693` | `1.54e-8` | `1.76e-8` | `1.52e-8` |
| 5 | `18.56` | `0.6230` | `0.0293` | `5.11e-5` | `6.84e-8` |
| 10 | `9.67` | `0.6884` | `0.0741` | `0.00178` | `2.25e-6` |
| 20 | `4.31` | `0.7689` | `0.1801` | `0.1369` | `1.06e-4` |
| 40 | `2.03` | `0.8523` | `0.4453` | `0.1786` | `0.00112` |

Relative to the hard cut, its step-40 far disturbance falls from `0.04425` to `0.00112`, but the surgery-time core
disturbance rises from `1.3469` to `2.55e11`. The apparent outward improvement is achieved by retaining an
off-manifold singularity behind the preserved collar. This is exactly the failure mode the mission forbids: the
shock is relocated, not controlled.

## 8. Phase, shams, and negative controls

- Scheduler step/parity was identical in every donor-recipient operation; mismatches are refused.
- Persistent current state includes `rho,U,V,c,N,C,Mf,uptake,step`.
- There is no persistent prior-state, flux, gradient, velocity, update cache, or RNG state to transplant.
- Fluxes/gradients and `up_ref` are recomputed by the next update; tracker state is external to physics.
- Every same-source new active-operation sham is exact (`0.0` maximum state error).
- Inherited no-op, serialization, round trip, reinsert, coordinate-transform, and matched-state controls again
  equal zero. The prior Phase 0.5 sham feeding-neutrality check again equals zero.

The failures therefore cannot be attributed to an omitted dynamical buffer or coordinate transform. They arise
from the simultaneous requirements of donor contrast, recipient boundary/body state, and arm-level balance.

## 9. Decision and claim logic

**STOP-TRANSPLANT.** Do not seal a preregistration, open a prospective seed, relax the seam envelope, scan more
radii/tapers, or run crossed feeding with these operators. A joint manifold-preserving body/environment
counterfactual would be a new intervention concept and a new authorization, not a bounded parameter correction to
this failed grid.

This result does **not** mean that local storage, environmental storage, redundant access, or relational synergy is
absent. Those hypotheses remain **UNRESOLVED** because the required counterfactuals were not technically qualified.
It also does not change the certified statement that a causal feeding effect survives turnover.

## 10. Validation

All required regressions passed:

- `python -m pytest experiments\individuation\test_turnover_end_to_end_03g.py -q` -> `7 passed`;
- `python experiments\individuation\test_bijective_tracker.py` -> `10/10 checks PASS`;
- `python -X utf8 experiments\individuation\test_turnover_tracer.py` -> `6/6 checks PASS`;
- `python -m pytest experiments\individuation\test_access_structure_operators.py experiments\individuation\test_access_structure_boundary_safe.py -q` -> `23 passed` (8 inherited Phase 0.5 plus 15 new focused tests);
- Python machine-result assertions -> PASS: exact seed namespace, 10 worlds/4 feasible, four frozen configurations,
  96 arms, zero operator-construction failures, exact active-operation shams, per-arm physical-balance pass, no
  technical GO, no new family, and no scientific crossed feeding;
- `git diff --check` -> pass (line-ending conversion notices only).

No failed configuration or tracking loss was omitted from the JSON or report.
