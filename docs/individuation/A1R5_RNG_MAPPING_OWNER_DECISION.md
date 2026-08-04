# Owner decision dossier — the 64-bit initial-condition mapping

**Status: PENDING. The frozen generator is NOT modified by this mission.**

## The defect, demonstrated

`draw_uniform` is `int.from_bytes(draw_block(...)[0:8], "big") / float(2**64)` and its
docstring says "a uniform in [0, 1) with exactly 64 bits of resolution". Both halves of
that sentence are false in binary64:

* `(2**64 - 1) / float(2**64) == 1.0`. The interval is **[0, 1]**, not `[0, 1)`.
  Exactly **1024** of the `2**64` words round up to `1.0` (every `w >= 18446744073709550592`),
  i.e. probability `2**-54 = 5.551e-17` per draw.
* The output grid is **not** `2**-64`. Near 1 the binary64 step is `2**-53`, so **2048**
  distinct 64-bit words collapse onto one output; 2048 consecutive words near the top
  produce **2** distinct values. Far from 1 the mapping is injective. The resolution claim
  is therefore scale-dependent and false where it matters most.

Note also that the frozen 01S text writes the law as `m[y,x] ~ U[0,1]` with a CLOSED
bracket, while the generator's docstring writes `[0,1)`. The two frozen statements already
disagree with each other, independently of the implementation.

## Quantified impact on a confirmatory family

Worst case 32x32 lattice, 134 worlds, two fields: **274 432** draws.
`P(at least one exact 1.0) = 1.52e-11`. Expected count `1.52e-11`.

`m = 1.0` and `n = 1.0` are *admissible*: `validate` allows `m <= m_max = 1.0`, and
`matter_forward` carries a factor `(1 - m_plus/m_max)` which is exactly 0 there. So the
defect does not crash and does not corrupt a run at this family size. It falsifies a
*declared* property, and a declared property that is false is a reviewer's finding whether
or not it ever fires.

## Options

**1 — exact mapping on the top 53 bits.** `(word >> 11) / float(2**53)`. Every output is
exactly representable in binary64, the grid is uniform with step `2**-53`, and the range is
strictly `[0, 1)` (verified for `word = 2**64 - 1`). Cost: every drawn value changes, so
every future draw plan changes. It does **not** invalidate anything already run, because
nothing has been run. **Recommended.**

**2 — keep the mapping, correct the claim.** Change the docstring to "uniform on the
rounded `2**-64` grid over `[0, 1]`" and record that `1.0` occurs with probability `2**-54`.
Zero code risk, zero change to any draw. Cost: the substrate keeps a law whose upper
endpoint is attainable, and every future reader must be told why.

**3 — exact intermediate representation then conversion.** Compute in `Fraction` or
`Decimal` and convert. Correct but slow, and the conversion re-introduces the same rounding
at the last step unless the numerator is bounded below `2**53` — which is option 1.

## Recommendation

**Option 1**, taken NOW rather than after a run, because it is free before any draw exists
and expensive after. Option 2 is defensible only if the owner prefers never to touch a
frozen generator; in that case the docstring and the 01S text must both be corrected in the
same commit, since they currently contradict each other.

This mission implements none of the three.
