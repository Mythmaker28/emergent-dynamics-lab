# M_MINUS-ORDER-READER-00 — frozen DEV-only protocol

Status: **FROZEN BEFORE THE FIRST 570XX READER OUTPUT**

## 1. Scope and preserved result

This is a one-shot mechanistic reader test on the already-open DEV source worlds `57001–57024`. It preserves exact
parent `ea6e6a0ab2ccc3e94eba364ddb459088c96d6033` and the completed verdict
`NO_MEMORY_FIRST_STAGE — STOP THIS PREREGISTRATION CANDIDATE`. It does not reopen the feeding endpoint, alter its
signs, extend the family, inspect or reserve a prospective namespace, modify 03G/V5, or authorize ownership,
identity, active reconstruction, reproduction, or heredity.

Only worlds that already supplied a complete four-history block in the parent result can supply a reader block.
The original source world remains the statistical unit. History branches and perturbation arms never increase
`n`; failed potential outcomes are not encoded as zero.

## 2. Code-only causal audit

The frozen engine computes, after transport, uptake, decay, internal dynamics and memory writing,

```text
z(x)       = newm1(x) - newm2(x)
m_minus(x) = tanh(z(x))
q_c(x)     = s rho0(x) [1 + lam_minus m_minus(x)]
c'         = c + dt [D_c lap(c) + q_c - delta c].
```

`lam_minus` occurs in exactly this attractant-production term. It does not directly multiply uptake, nutrient,
internal `U/V`, memory writing, or tracker association. The causal descendants are:

1. the same-step local attractant-production increment `dt q_c`;
2. the updated attractant field `c` after diffusion and decay;
3. next-step chemotactic face flux through `dc`, with the saturated response
   `chi=chi0/[1+(mean_face_c/c_sat)^2]`;
4. transported `rho/U/V/C/Mf`, hence centroid displacement and morphology;
5. subsequent uptake and memory writing indirectly through changed material, nutrient and `Psi(N-c, uptake-up_ref)`.

The unique directly downstream, sign-identifiable observable is therefore local attractant production. Directional
movement would add gradient, saturation, geometry and tracking terms whose sign is not identifiable from
`m_minus` alone, so it is not selected.

## 3. Frozen reader and perturbation

### Primary observable

At the first update after the common standardized isolation settle, define

```text
Y_h(a) = dt sum_{x in core} s rho0_h(x)
         [1 + lam_minus (1+a) tanh(newm1_h(x)-newm2_h(x))].
```

`Y` is the actual production component of the engine's `c` update, integrated on the fixed radius-10 local core.
Diffusion and decay are excluded because they are not multiplied by `lam_minus`. No tracker is used in this
readout.

### Perturbation direction and amplitude

The direction `v` is a fractional gain change of the existing local `m_minus -> attractant production` reader on
the fixed core for one update. The three arms are

```text
a = -epsilon, 0, +epsilon
epsilon = 2/3.
```

With frozen `lam_minus=0.15`, the effective local coefficients are exactly `0.05`, `0.15`, and `0.25`. These are
the pre-existing `lam_minus` values in the engine's committed readout grid; epsilon is not estimated or tuned on
any 570xx history contrast. Outside the fixed core, the engine remains at `lam_minus=0.15`. No secondary amplitude
is authorized because the source term is exactly affine in this gain.

The perturbation lasts one engine update and the horizon is that same update. `a=0` must be byte-identical to the
unmodified qualified clamp engine. The intervention does not edit `rho/U/V/c/N/C/uptake/Mf` before the arms split;
it changes only the declared reader contribution to the resulting `c` field.

### Susceptibility

```text
chi_h = [Y_h(+epsilon) - Y_h(-epsilon)] / (2 epsilon)
      = dt s lam_minus sum_core rho0_h m_minus_h.
```

The raw `chi_h` is primary. The single frozen robustness normalization is

```text
chi_h_mass = chi_h / sum_core rho0_h,
```

using pre-perturbation core mass. It is secondary and cannot replace an unfavorable raw result.

## 4. Histories and isolation

The four parent histories remain unchanged:

- `H_L_EARLY`, `H_L_LATE`;
- `H_H_EARLY`, `H_H_LATE`.

For each complete parent world, reconstruct the exact deep-turnover state and require its stored parent state hash.
Use the qualified radius-10 core and two-cell collar. Reset only `N := N0`, then settle for 40 steps with:

- the qualified two-cell no-swap boundary clamp;
- a translated, same-seed, no-history, no-drive reference trajectory;
- `up_ref=0`;
- untouched focal memory and physical core;
- no common feeding stimulus.

All histories receive the same history-independent boundary construction. After the settle, split byte-identical
copies into the three reader arms and run the one-update perturbation. The collar frame at the perturbation update
is identical across arms. Coupled continuation is not a primary outcome; the direct local source makes transport
unnecessary for this test.

## 5. Factorial estimands

Within every original world compute the frozen contrasts on both raw and mass-normalized susceptibility:

```text
delta_chi_O  = 0.5[(chi_LE-chi_LL) + (chi_HE-chi_HL)]
delta_chi_D  = 0.5[(chi_HE+chi_HL) - (chi_LE+chi_LL)]
delta_chi_DO = (chi_HE-chi_HL) - (chi_LE-chi_LL).
```

Also report the low-dose and high-dose EARLY-minus-LATE contrasts separately. No world-specific sign flip,
feature selection, matching, trimming or body-based exclusion is allowed.

The algebraic prediction is **positive** `delta_chi_O`: the accepted structured state has positive
EARLY-minus-LATE `m_minus`, and `chi` is a positive mass-weighted linear functional of `m_minus` for
`dt,s,lam_minus>0`. Raw density weighting could falsify that prediction; the sign is not changed after inspection.

## 6. Primary mechanism ablation

Repeat the complete standardized isolation settle and reader probe with `lam_minus=0`, leaving `lam_plus` and every
other engine parameter unchanged. The gain perturbation is multiplicative, so all three arms remain at an effective
coefficient of zero. This is the primary mediation test.

Material reduction is frozen as at least 90% attenuation of `|delta_chi_O|` relative to intact, with the ablated
interval including zero. Because the selected observable is the exact `lam_minus` source term, any ablated
susceptibility above the frozen float64 tolerance `1e-12 + 1e-10*abs(reference)` is a manipulation failure, not a
biological residual.

## 7. Manipulation and validity gates

All must pass before scientific classification:

1. parent manifest and raw content bindings pass, including exact complete-world membership;
2. every reconstructed deep state matches its stored parent hash;
3. parent exact-clone identity and fixed history labels are preserved;
4. `-epsilon/0/+epsilon` map exactly to effective local coefficients `0.05/0.15/0.25`;
5. all arm input states and collar frames are byte-identical before the perturbation update;
6. `a=0` is byte-identical to the probe-disabled qualified engine;
7. the plus/minus source and final-`c` changes reverse symmetrically within float64 tolerance;
8. with `lam_minus=0`, all perturbation arms are byte-identical and susceptibility is numerically zero;
9. deterministic rerun reproduces every arm hash and scalar exactly;
10. the standardized settle retains a viable focal track without ambiguity, while the primary source readout
    itself remains tracker-independent;
11. no history-, arm- or droplet-level pseudoreplication enters inference.

Any failed gate yields `MANIPULATION_INVALID`.

## 8. Frozen summaries and gates

For every original-world contrast report `n`, mean, median, standard deviation, 95% Student-t interval, and sign
counts. No branch is an independent observation. Multiple secondary contrasts are descriptive and do not replace
the primary order contrast.

The structured parent order state is reproduced only if at least 75% of complete worlds are positive and the 95%
interval for the deep core `m_minus` order contrast excludes zero positively.

`ORDER_READER_CANDIDATE` requires all of:

- the structured positive order state is reproduced;
- raw isolated `delta_chi_O` has at least 75% positive original-world signs and a 95% interval above zero;
- both low- and high-dose EARLY-minus-LATE raw susceptibility contrasts have at least 75% positive signs;
- mass-normalized `delta_chi_O` has at least 75% positive signs and a 95% interval above zero;
- intact `delta_chi_O` is reduced at least 90% by `lam_minus=0`, whose interval includes zero;
- all manipulation gates pass.

Classification precedence after valid manipulation:

1. `ORDER_READER_CANDIDATE` if all its gates pass;
2. `ORDER_STATE_WITHOUT_READER_EFFECT` if the state reproduces but primary order susceptibility is not established;
3. `PHYSICAL_SUSCEPTIBILITY` if an established order susceptibility persists under `lam_minus=0` or reverses under
   mass normalization in a way consistent with body weighting;
4. `UNRESOLVED` if heterogeneity or uncertainty prevents the above distinctions.

`NO_VALID_READER` applies only at the code-only stage. `SIGN_THEORY_CORRECTED` is recorded as a theory result but
does not override the empirical reader classification or reinterpret the parent STOP verdict.

## 9. Claim and stopping boundary

The maximum permitted positive statement is:

> DEV evidence that temporal order changes a local `m_minus`-linked attractant-production response operator under
> standardized inputs.

Even that result is not ownership, individual memory, identity, heredity, prospective confirmation, or a feeding
effect. Stop after DEV and return for human review. Do not open prospective seeds, seal a protocol, run an ownership
pair, or start a generic causal-landscape battery automatically.
