# EXP03-B Internal Critique — PASS A (mechanism challenge)

- Run RUN-20260710-1930-EXP03B; model claude-opus-4-8 (lock lifted); target orbital mechanism @a788500.
- Question: is the orbital/transverse interaction just a radial interaction-matrix/range change?

## Argument it is NOT
- CORE V0 forces are central (along the connecting line); central pair forces conserve angular momentum, so from
  an irrotational start they cannot generate net circulation. The orbital term is purely transverse
  (`rot90(unit)`), equal-and-opposite (linear momentum conserved) but torque-producing about the pair midpoint —
  it INJECTS angular momentum / vorticity. No radial interaction (any matrix/range) can produce this.
- Distinguishing observable/ablation: net internal circulation / total angular momentum. Verified by
  `test_circulation_injected_vs_radial_from_rest` (orbital: |L|>0 from rest; radial: |L|~0) and by the screen's
  `mean_abs_circulation` (OFF vs ON). Sanity: one law shifted |circulation| ~0.05 -> ~0.78 under ON.

## Verdict
Genuinely distinct causal family. No STOP. As in EXP03-A: a P/M distributional shift alone is Level 1 descriptive,
not proof of the family; distinctness rests on the circulation/angular-momentum signature.
