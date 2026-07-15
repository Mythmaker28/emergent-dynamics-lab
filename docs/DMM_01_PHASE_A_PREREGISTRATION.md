# DMM-01 — Phase A Causal-Decomposition Preregistration (frozen C1c; diagnostic ablations only)

## Design
From identical post-history states (dev seeds 37001-37003, SMC-01-style 2-phase histories, band [0.003,0.02]),
clone branches and evolve forward (no drive) under diagnostic variants; decode h2/h1 from memory DIST at
matched elapsed-time checkpoints; also record old-material fraction M (PulseChase, passive).

## Branches
- A0 normal C1c (eta_t0.010, D_m0.010).
- A4 templating off (eta_t=0).
- A3 diffusion off (D_m=0).
- A34 both off (eta_t=0, D_m=0).
- A6 static: freeze body (no growth/death/turnover), evolve ONLY memory maintenance — isolates intrinsic homogenization.
All diagnostic; independently ablatable; no history labels enter dynamics.

## Orthogonalization (time vs turnover)
Fit transparent model h2_decodability ~ time + M across branches (branches decouple time from M because
smoothing-off branches keep h2 while M still falls). Report partial effects of time and M, interaction, CIs.

## Old/new-material audit
At checkpoints, split entity cells by cohort (PulseChase): old (cohort0>0.5) vs new (cohort1>0.5). Decode h2
from old-cell DIST, new-cell DIST, all-cell DIST. Tests dilution vs homogenization vs acquisition.

## Decoder-stability audit
Compare frozen-initial decoder vs checkpoint-specific decoder vs train-early/test-late. Distinguish
information loss from representational drift.

## Phase A verdict menu (mission §11). Gate: do not modify maintenance until decided.
## Grouping: leave-history-out; no row-LOO. Viability tracked (localized size).
