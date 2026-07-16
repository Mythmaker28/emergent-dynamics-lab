# LCI-CAUSAL-TURNOVER-PREREG-03 — Risk register

| # | risk | severity | status / evidence | mitigation (pre-registered) |
|---|---|---|---|---|
| R1 | **Coupled-readout tautology** — G4 (deep own effect) passes near-automatically because `uptake ∝ 1+λ₊·tanh(m₊)` | HIGH | REAL — DEV deep_own +0.131, 4/4 worlds, trivially powered | G3 storage co-PRIMARY; passive-decay null; G4 alone cannot pass G6 |
| R2 | **Graded homogenization** — own-history decode fails at depth (memory homogenizes) | HIGH | REAL — DEV deep own-dose 0.135 < neigh 0.580; m₊ spread 0.07→0.007 | size ≥18 valid; report honestly; G3 is PRIMARY-at-risk, expected to fail |
| R3 | **Feasibility attrition** — droplets fission/die during turnover (~50 %) | HIGH | REAL — 4/8 feasible; fission ×3 (genuine, 61→38+22) + loss ×1 | ≥12 valid floor; 50-seed family; all seeds reported; world-level censorship |
| R4 | **Survivor-selection bias** (the 39/39→17 lesson) | HIGH | controlled | any invalid entity → whole world invalid; never keep survivors; count against floor |
| R5 | **Tracker cross-attribution** (the ×4.8 merge inflation) | MED | controlled — bijective 10/10 tests; fixed-mask ratio ~0.96 at deep | bijective tracker + fixed-mask convergent readout; censor MERGE/SPLIT/LOST/AMBIGUOUS |
| R6 | **Global `up_ref` resynchronization** during turnover | MED→LOW | tested in-regime: global/local ratio 6e-4 (negligible) | up_ref-neutralized diagnostic + global-mean-history decoder (pre-registered) |
| R7 | **Material mis-measurement** (analytic M, not per-droplet) | MED | fixed — per-target passive cohorts; no-feedback max|Δ|=0.0 (850 steps) | measured M_i per entity; cross-attribution reported; M_i≤0.25 per droplet |
| R8 | **Deep-snapshot definition sensitivity** (depth target / first-vs-best instant) | MED | pre-declared | first qualifying instant only; M≤0.25 fixed; no best-instant selection; TURN_CAP=1500 |
| R9 | **Determinism / platform drift** | LOW | verified byte-identical (two-run max|Δ|=0.0; Phase-1 gate 0-diff) | pinned venv numpy2.2.6/scipy1.15.3; determinism gate before analysis |
| R10 | **Fission is scientifically interesting but OUT OF SCOPE** (division/reproduction = parking lot) | — | noted | report fission rate as a feasibility fact only; no division/heredity work |
| R11 | **Compute cost** — 50-seed family ≈ 35–50 min single-core | LOW | flagged | resumable checkpoint per seed; batchable |
| R12 | **Passive-copy ≠ persistence** — surviving signal is passively copied, not stored material-independently | HIGH (interpretive) | REAL by construction (`Mf+=g·m`) | passive-decay null must match observed; claim "passive copy," never "persistent memory" |

**Load-bearing risks are R1/R2/R12 (interpretive):** even a "successful" run establishes only that a passively-copied,
spatially-localized remnant lets the coupled multiplier still fire — not that graded own history or a
material-independent memory survives. The pre-registration is built so these cannot be over-claimed.
