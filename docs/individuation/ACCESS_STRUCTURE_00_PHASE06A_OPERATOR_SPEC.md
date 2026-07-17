# ACCESS-STRUCTURE-00 Phase 0.6A operator specification

**Frozen before DEV execution. Status: engineering qualification only; no prospective seed and no scientific
crossed-feeding contrast are authorized.**

## Question and claim boundary

Can a local spatial transplant preserve a meaningful donor-state contrast while controlling the interface,
matching each recipient arm's own physical totals, preserving complete update phase, remaining trackable, and
keeping all compensation inside the declared `C` support?

This specification cannot locate storage. A small seam obtained by deleting the donor contrast is a failure. A
correction that exports imbalance into `H` or `E`, or uses future feeding to select a configuration, is a failure.

## Fixed data and support

- Complete already-open DEV namespace: seeds `50001-50010`, with operators only on the existing deep-feasible
  worlds. No other seed is accepted by the runner.
- Outer `C` radius: 10 periodic lattice cells around the rounded target centroid, inherited from Phase 0.5.
- `H`: the one-cell ring outside `C`; `E`: the complement. Every candidate leaves all cells outside `C` exact.
- Measurements: surgery time `0+`, then steps `1,5,10,20,40` in payload core, interface collar, inner halo, outer
  halo, and far environment.
- Statistical/scientific outcomes: none. No active-arm future feeding is computed.

## Two operator families and complete grid

There are exactly two serious families and four configurations. All four will be reported.

| Configuration | Family | Full donor radius | Recipient-preserved/taper region | Scientific purpose |
|---|---|---:|---|---|
| `RIP_HARD_R9` | recipient-interface-preserving interior substitution | 9 | hard recipient state for `d>9` through outer radius 10 | tests whether moving the hard cut inward by one recipient layer controls the external seam without sacrificing the body |
| `RIP_HARD_R8` | recipient-interface-preserving interior substitution | 8 | hard recipient state for `d>8` through radius 10 | exposes the payload-versus-collar tradeoff with a second, predeclared collar only |
| `CPP_QUINTIC_R8` | constrained phase-consistent projection | 8 | quintic donor weight from 1 at radius 8 to 0 at radius 10 | matches value and first-derivative weight endpoints while retaining a radius-8 exact-memory core |
| `CPP_QUINTIC_R7` | constrained phase-consistent projection | 7 | quintic donor weight from 1 at radius 7 to 0 at radius 10 | the single wider transition tests whether seam control requires unacceptable payload loss |

No radius, taper, balance basis, or constraint may be added or selected after this DEV execution.

## State mapping and individual-arm balance

The donor is moved by an integer toroidal translation; there is no interpolation, rotation, rescaling of
coordinates, RNG use, relaxation step, or surgery-time engine update.

For `rho,U,V,c,N`, the provisional field is

`x0 = x_recipient + w * (x_donor_translated - x_recipient)`.

Each field is then projected to the recipient arm's own total. The correction is supported only where `w>0`; its
spatial basis is fixed by the recipient field and `w`, not by the donor label or any future outcome. A bounded
active-set solve preserves non-negativity. `H` and `E` receive no correction. Balance is judged independently in
each arm at `abs(error) <= 1e-12 + 1e-10*abs(reference)`; reciprocal-pair conservation has no role.

`Mf/rho` is the protected history payload. It is donor-weighted and reconstructed on the balanced `rho`; its total
is deliberately not forced to the recipient total because doing so would erase the causal contrast being tested.
This exception is explicit: memory is written/forgotten each step and is not a conserved physical total.

The 12 base passive cohorts are balanced by deterministic row/column scaling so their per-cell sum equals `rho`
and their recipient global channel totals remain matched. The three appended diagnostic tracers are independently
total-balanced. Diagnostic cohorts do not feed physics. Stored `uptake` remains the recipient's previous-step
readout because the next update does not read it.

The balance ledger reports global and `C/H/E` totals for every persistent array, mass, nutrient, diagnostic
material, body state, and the stored uptake readout. The engine has no energy variable or Hamiltonian; bulk `c/N`
L2 magnitude and `c/N` gradient magnitude are therefore reported as explicitly non-conserved environmental-energy
proxies rather than mislabeled as exact invariants.

## Dynamical phase

The donor and recipient must have the same scheduler step or the operation is refused. The state snapshot contains
all persistent arrays. The engine has no persistent prior-state, flux, gradient, velocity, cache, or RNG state;
these quantities are recomputed. Tracker state is external to physics and is re-seeded from outcome-independent
post-surgery geometry. A phase-preserving improvement is only an engineering result.

## Failure re-audit and technical controls

The exact Phase 0.5 runner is re-executed and must reproduce maximum seam ratio `22.872170460755093`, individual-arm
imbalance, zero exact-control error, and its existing world dispositions. The hard-cut crossed pair is separately
audited at all six time points with the new bands, interface-face, flux, geometry, phase, and ledger diagnostics.

Retained controls: no-op, exact serialization/round trip, same-source reinsert, coordinate-transform sham, and
matched-state sham from Phase 0.5. Each new configuration adds a same-source active-operation sham through the
same mapping/projection code. It must be exact. A mismatched scheduler phase must be refused.

## Payload guard

Payload is measured without feeding from `rho,u,v,c,N,m1,m2,m_plus` on the full-weight, occupied core. For each
field, contrast projection is

`dot(candidate-recipient, donor-recipient) / ||donor-recipient||^2`,

where 1 is exact donor contrast and 0 is recipient state. The frozen 03G 11-feature `L` vector is measured on the
expected translated donor body. A meaningful-payload pass requires:

- `L` contrast projection at least `0.50`;
- each defined memory-field (`m1,m2,m_plus`) projection at least `0.50`;
- at least `0.90` of the expected donor body under full donor weight.

Sensitivity at payload projections `0.25,0.50,0.75` will be reported. These are technical retention fractions,
not scientific effect thresholds.

## Technical decision gates

`TECHNICAL GO` requires one complete configuration to pass simultaneously on every qualified arm/world:

1. all required per-arm physical totals pass the frozen float64 criterion;
2. the original outer boundary and every changed interface face have mean-jump ratios at most `1.25` for every
   causal view, with sensitivity at `1.5,2,3,5` reported and no relaxed threshold substituted;
3. propagation in `H/E` is bounded and does not exceed the corresponding hard-cut disturbance envelope;
4. scheduler and complete persistent phase are preserved; same-source active-operation shams are exact;
5. all branches remain finite, bijectively trackable, and below the coverage cap for 40 steps;
6. the payload guard passes; and
7. no future feeding or outcome-dependent tuning occurs.

If no configuration satisfies disturbance control and payload retention together after these two predeclared
families, the transplant strategy receives `STOP-TRANSPLANT`. `REVISE` is reserved for one specific bounded
correction justified by the complete grid rather than an invitation to scan more variants.
