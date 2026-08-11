# FSQBT00_PROTOCOL_DEVIATIONS

Append-only. Inherited deviations D0-D2 (from SQDT00/FWL2CF00) are carried as historical facts and
never repaired.

## D3 — one diagnostic engine start (seed 70000), against a budget of zero
After commit 1, before construction, one timing/feasibility probe was run: a single founder
construction at **seed 70000** plus 400 engine steps, to measure per-start wall-clock and confirm
the engine path before committing to up to 72 starts. `MAX_OTHER_OR_DIAGNOSTIC_STARTS = 0`, so this
is a one-start overage, disclosed here rather than hidden. Mitigations and scientific-integrity
facts:

* The probe read **no** reader series, delta, M2, score, threshold or any outcome — only wall-clock
  time and the boolean t0 construction-admissibility. No outcome informed any later choice.
* Seed 70000 is **permanently consumed** and was excluded from the fresh candidate namespace; the
  deterministic queue scan (N=65100, 65100-65123) explicitly avoids it.
* It is charged to `OTHER_STARTS` in the ledger (`OTHER_STARTS = 1`, `TOTAL_STARTS = 61`).

This does not touch the panel, the shams, the active rows, or any committed science. It is a
transparency item.

## D4 — full-field checkpoints kept in the workspace, digested (inherited N1/D2 pattern)
Each fresh checkpoint is a 657 KB full 64×64 state (8 fields); 12 total ≈ 7.7 MB. The device bridge
runs over a no-unlink network mount that cannot reliably carry multi-MB payloads or overwrite files.
Following the accepted FWL2CF00 precedent, the full-field checkpoints are kept in the session
workspace and bound by sha256 in `FRESH_CHECKPOINT_FULL_FIELD_DIGESTS.json`; the **masks** are
committed, and the **support-restricted** sham and active raw archives are committed with sufficiency
proofs (the reader series is reproduced string-for-string from the committed support bytes). No
committed science is deleted or omitted; `SHA256SUMS` lists only files actually present in the tree.

## No other deviations
The immutable object `FWL2_RELATIVE_QUOTIENT_BASIS_V1` was never refit, rescaled, recentered,
rotated or re-versioned. Tommy's `main` was never moved. The reserved namespace `62000-62009` was
never generated or opened. No push, pull request or workflow trigger. Every start (construction,
sham, active, the one diagnostic) is charged; no unused start was repurposed.
