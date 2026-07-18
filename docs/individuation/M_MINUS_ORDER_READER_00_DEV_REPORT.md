# M_MINUS-ORDER-READER-00 — DEV-only mechanistic reader report

## Disposition

**DEV classification: `ORDER_READER_CANDIDATE`.**

The same-dose EARLY-versus-LATE history contrast changes the frozen local attractant-production susceptibility in
the algebraically predicted direction after a common standardized isolation settle. The result is positive in all
17 complete original worlds, at both dose levels, in the raw primary observable and after the frozen core-mass
normalization. Setting `lam_minus=0` collapses the susceptibility contrast exactly, and every manipulation gate
passes.

This is a bounded DEV result on already-open source worlds, not prospective confirmation. The accepted parent
classification remains **`NO_MEMORY_FIRST_STAGE — STOP THIS PREREGISTRATION CANDIDATE`**. The present result does
not establish a feeding-order effect, ownership, individual memory, identity, heredity, or active reconstruction.

## 1. Phase-A causal and sign audit

The exact engine path is

```text
m_minus(x) = tanh(newm1(x)-newm2(x))
q_c(x)     = s rho0(x) [1 + lam_minus m_minus(x)]
c'         = c + dt [D_c lap(c) + q_c - delta c].
```

`lam_minus` occurs only in the attractant-production source. The updated attractant field later affects gradients,
the saturated chemotactic response, face flux, transport, centroid displacement and morphology. Those later signs
depend on state and geometry; local source production is the only direct downstream observable whose sign is
identifiable from `m_minus` alone.

The earlier negative reduced-theory prediction was an algebraic orientation error under the unchanged
EARLY-minus-LATE contrast. With the frozen scalar recurrence, `q1=0.965`, `q2=0.9994`, `w=0.0015`, `T=60`,
`S=120`, and `Delta=0.01`:

```text
Delta m1          = -4.6377041581e-06
Delta m2          = -2.9102795171e-05
Delta(m1-m2)      = +2.4465091013e-05
Delta tanh(m1-m2) = +2.4464801452e-05.
```

Theory disposition: **`SIGN_THEORY_CORRECTED`**. This correction does not turn the completed parent
preregistration into a pass.

## 2. Frozen reader and intervention

Exactly one reader was selected before any new 570xx reader output:

```text
Y_h(a) = dt sum_core s rho0_h(x)
         [1 + lam_minus(1+a)tanh(newm1_h(x)-newm2_h(x))].
```

It is the one-update integrated attractant-production source on the fixed radius-10 focal core. The symmetric
perturbation is a one-update fractional gain change of the pre-existing local `lam_minus*m_minus` source:

```text
a = -2/3, 0, +2/3
effective local lam_minus = 0.05, 0.15, 0.25.
```

These values came from the committed pre-existing coefficient grid, not from the 570xx outcomes. The primary
susceptibility is

```text
chi_h = [Y_h(+epsilon)-Y_h(-epsilon)]/(2 epsilon)
      = dt s lam_minus sum_core rho0_h m_minus_h.
```

Each deep state was standardized with `N:=N0`, a 40-step qualified two-cell no-swap clamp, `up_ref=0`, and a
same-seed no-history/no-drive common boundary. The perturbation duration and horizon were both one update. The
primary source readout is tracker-independent. The sole frozen robustness endpoint is susceptibility per
pre-perturbation fixed-core `rho` mass.

## 3. Original-world results

The unit is the original source world. Seventeen parent-complete worlds contributed one factorial block each;
counterfactual histories and perturbation arms did not increase `n`. The seven parent-incomplete worlds were not
rerun and were not encoded as zero.

### Structured state and primary order susceptibility

| Estimand | Mean | Median | SD | 95% Student-t CI | Signs |
|---|---:|---:|---:|---:|---:|
| deep core `m_minus`, order | 0.003667894 | 0.003523799 | 0.001175422 | [0.003063548, 0.004272241] | 17 positive / 0 negative |
| raw `delta_chi_O` | 0.0003129292 | 0.0002656092 | 0.0001274333 | [0.0002474090, 0.0003784494] | 17 / 0 |
| mass-normalized `delta_chi_O` | 8.989063e-06 | 9.220196e-06 | 2.148001e-06 | [7.884663e-06, 1.009346e-05] | 17 / 0 |

The raw primary and normalized robustness intervals exclude zero in the frozen positive direction, with no
opposite-sign world.

### Dose-level order consistency

| Same-dose EARLY-minus-LATE contrast | Mean | 95% Student-t CI | Signs |
|---|---:|---:|---:|
| low-dose raw | 0.0002920462 | [0.0002286044, 0.0003554880] | 17 / 0 |
| high-dose raw | 0.0003338122 | [0.0002468245, 0.0004207999] | 17 / 0 |
| low-dose per core mass | 9.372209e-06 | [8.105630e-06, 1.063879e-05] | 17 / 0 |
| high-dose per core mass | 8.605917e-06 | [7.482288e-06, 9.729547e-06] | 17 / 0 |

### Dose and interaction susceptibility

| Estimand | Mean | 95% Student-t CI | Positive / negative |
|---|---:|---:|---:|
| raw `delta_chi_D` | -0.003355300 | [-0.004233290, -0.002477311] | 0 / 17 |
| raw `delta_chi_DO` | 4.176601e-05 | [-3.577037e-05, 0.0001193024] | 9 / 8 |
| mass-normalized `delta_chi_D` | -5.284242e-06 | [-2.912187e-05, 1.855339e-05] | 6 / 11 |
| mass-normalized `delta_chi_DO` | -7.662913e-07 | [-1.690806e-06, 1.582238e-07] | 4 / 13 |

The reader has a negative raw dose contrast, but that contrast is not robust to the predeclared mass
normalization. The dose-by-order interaction is not established on either scale. Neither quantity was a gate for
replacing the primary order estimand.

## 4. `lam_minus` mechanism test and validity

With `lam_minus=0`, every `-epsilon/0/+epsilon` arm is identical, `delta_chi_O=0` in all 17 worlds, its interval is
exactly `[0,0]`, and the mean attenuation fraction is `1.0` (100%; frozen minimum 90%). All reconstructed deep
states match their parent hashes. All deterministic reruns, probe-disabled identities, symmetric sign reversals,
non-`c` identities, zero-coefficient identities, tracker-independence and original-world aggregation gates pass.

The exact collapse is expected from the selected constitutive source:
`chi_h = dt*s*lam_minus*sum(rho0*m_minus)`. It is strong evidence that this measured susceptibility is the intended
`lam_minus` reader rather than a separate body or geometry response. It is also partly a structural identity of the
chosen one-step source assay; it does not independently show that the endogenous system propagates the order state
into movement or feeding.

## 5. Independent raw-only reproduction

The raw-only reproducer used the consolidated JSON without importing the runner or initializing the engine. It
recomputed every per-world factorial contrast, summary, gate and classification:

- `reproduction_pass=true`;
- `stored_classification_match=true`;
- `all_stored_contrasts_match=true`;
- `original_world_statistical_unit=true`;
- `runner_imported=false`, `engine_initialized=false`, no prohibited runtime module.

Bindings:

- parent result commit: `ea6e6a0ab2ccc3e94eba364ddb459088c96d6033`;
- before-output freeze commit: `8349c55`;
- protocol SHA-256: `d0096f028b9d9e35d6cabb54b73c0e47ca8ee512efb8b0702c8ab8de86cf2ead`;
- consolidated DEV result SHA-256: `ebe6043d91aed3fefada489602e84f5affd43f0dd67873bb2fbff11bc4aff7f7`;
- raw-only reproduction SHA-256: `61c51a7baf5fcf082e8ce764f3db1275a90e10c89e5a8a77821efcd2b490da5b`.

Validation: 35 focused and regression tests passed in 63.74 seconds, covering the reader, the parent exact-clone
experiment and the qualified no-swap clamp. A second raw-only reproduction was byte-identical to the committed
reproduction artefact.

## 6. Claim boundary and human decision

The exact maximum permitted claim is:

> DEV evidence that temporal order changes a local `m_minus`-linked attractant-production response operator under
> standardized inputs.

No stronger claim is supported. In particular, the assay does not establish that the state belongs to an
individual, that it is sufficient for feeding, that it survives a prospective test, or that it is actively
reconstructed.

**Next decision: human review.** Decide whether this direct constitutive source assay is a prospectively defensible
reader worth transferring unchanged into a separately preregistered test. If the scientific requirement is an
executed downstream behavior rather than direct source production, reject this candidate and design that endpoint
pre-data. Do not open prospective seeds, seal a protocol, run `LOCAL_OWNERSHIP_PAIR_00`, or launch a generic reader
battery automatically.
