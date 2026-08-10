# PROTOCOL_DEVIATIONS

## Inherited, unchanged

* **D1 (WL2SMF00)** — a substring-based dependency audit false-positived on its own blacklist and
  was replaced by a resolved-symbol AST audit. That corrected audit is what this programme binds.
* **D2 (WL2SMF00)** — the per-time `SHAM_0` reader series was not persisted. This programme exists
  in part to reconstruct it, and did so, 16 of 16.
* **D3 (WL2SMF00)** — the descendant start-accounting convention was declared, with 28 raw advance
  sequences against 18 charged starts.

## New in FWL2CF00

### N1 — the device bridge could not carry the full-field raw archives

Repeated `device_commit_files` calls timed out on multi-megabyte payloads (5.4 MB, then 1.8 MB
chunks), while small files succeeded. The committed raw archive therefore stores, per continuation,
the exact raw `rho` bytes on the reader's **union support** at `t0` and all ten scored times, the
two immutable masks, the support index, and the per-time plus terminal **full-state hashes** of the
complete engine state.

This is not a silent reduction. Sufficiency is proved: the reader series rebuilt from the compact
archive **alone** equals, string-for-string in exact rational form, the series rebuilt from the full
64x64 fields by the independent readback process — for all 16 sham and all 32 active continuations.
The fixed reader consumes `rho` only on that support, so nothing the decision path uses is missing.
The full fields remain in the session workspace and are not committed.

Impact on the science: none identified. Every gate is computed from quantities the committed archive
reproduces exactly.

### N2 — no full-field byte comparison of the reconstructed sham series was possible

Stated rather than glossed: the original per-time series never existed, so there is nothing to
compare byte-for-byte against, and no such comparison is claimed. Identity rests on sealed input
checkpoint bytes (hash-checked before and after every continuation), the parent's full-horizon twin
determinism evidence, exact agreement with every locked aggregate scalar, and independent
production/reference reader agreement.

### N3 — `R1` and `R2` optimiser certification is float-exhaustive plus exact spot certification

`R0` is certified **exactly** for the optimiser, because it reduces to an exact binary quadratic
form. `R1` and `R2` were enumerated exhaustively in float64 over all 32768 linked swap assignments
with a Weyl / backward-stability error bound of `3.66e-16`; the observed gap between the winner and
the runner-up exceeds that bound by factors of `6e8` to `1.8e10`, and the argmin coincides with the
exactly certified `R0` argmin for all three `k`. Declared because it is a hybrid, not a pure exact
enumeration.

## No other deviations

Zero retries, zero replacements, zero omitted rows, zero top-ups. No historical active row was
loaded or refitted. No threshold, panel member, arm, coefficient, bound, route or code was changed
after any lock. No push, no PR, no workflow trigger. Tommy's checkout untouched.
