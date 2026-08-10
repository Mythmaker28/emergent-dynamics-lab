# PROTOCOL_DEVIATIONS

## D1 — my first dependency audit false-failed on its own blacklist

The audit searched the driver's source for forbidden **substrings** and therefore matched the
blacklist literal it was itself carrying, reporting a failure that did not exist. Replaced by
resolved-symbol AST analysis over `wl2_prod.py`, `wl2_ref.py`, `wl2_sham.py` and `wl2_panel.py`,
which distinguishes a call from a mention. `wl2_panel.py` legitimately *names* the two future
carrier executables as strings inside `FUTURE_ACTIVE_CARRIER_ARM_LOCK.json`, to prevent arm
shopping; the corrected audit confirms it never imports or calls them, and that no active-operator
symbol is called anywhere in the programme.

## D2 — the per-time sham reader series was not persisted

`FRESH_SHAM_RAW_ARCHIVE` contains the 16 descendant checkpoints, the 16 immutable mask pairs, and
every threshold-determining scalar exactly as a rational (`B`, `RHO_MED`, `G2^2`,
`TAU_MATERIAL_L2^2`). It does **not** contain the per-scored-time `SHAM_0` series `X_A[h], X_B[h]`,
which I failed to serialise before the arrays went out of scope.

I did not re-run the shams to recover it. The sham tranche is exactly 32 starts, it was fully
spent, and `MAX_EXTRA_ZERO_OR_RELOAD_CONTROL_STARTS_AFTER_PANEL_LOCK = 0`. Re-running would have
been a `SHAM_START_BUDGET_PROTOCOL_BREACH`, and a budget that bends when it is inconvenient is not
a budget.

Scientific impact: none that I can identify. The sham is the identity operator applied to sealed
checkpoint bytes, the engine is bit-deterministic, and the twin oracle passed 16 of 16 over the
full horizon including the terminal state hash. The series is therefore an exactly reproducible
function of bytes that *are* archived. A future programme re-derives it by running `SHAM_0` again,
which it must do anyway to form `delta = X[INT] - X[SHAM_0]`.

## D3 — start-accounting convention, stated rather than assumed

One constructed descendant state counts as one start, which is exactly the convention WSFSCRP00
used for `make_founder` (found + relax + history + settle = 1). Here the precursor is computed once
per `(seed, geometry)` and shared by the two allocation branches, because the H3 pairing requires
identical precursor bytes. That is strictly **less** engine work than the inherited convention
assumes, so counting one per descendant over-counts rather than under-counts. The raw number of
engine advance sequences (28) is logged alongside the 18 charged starts so the two can be compared.

## No other deviations

No push, no pull request, no workflow trigger. Tommy's checkout untouched. No parent output
overwritten. No historical active row loaded. No active operator constructed or applied.
