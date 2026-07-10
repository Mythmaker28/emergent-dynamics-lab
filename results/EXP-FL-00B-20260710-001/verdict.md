# EXP-FL-00B — Passive-tracer resolution sensitivity: verdict

Protocol @357bc2f. RUN-20260710-2115-EXPFL00B. Model: claude-opus-4-8 (lock lifted by user).

## OBSERVED
- Passive invariance: the mass field A is IDENTICAL for 8 vs 32 cohorts (max diff 0.0) -> cohort count never
  affects dynamics.
- Reference (known turnover) M_min by granularity: G8=0.067, G16=0.0024, G32=0.0024, G64=0.0024 -> turnover
  resolved at ALL granularities (all <= 0.15).
- Representative static Flow-Lenia regimes (blind map-#1 laws {0,6,12,18}) mean field M: G8=0.9916, G16=0.9915,
  G32=0.9911 -> static regimes stay high-M at every granularity; finer tracers do NOT reveal hidden turnover.

## DECISION (pre-declared criterion; yield-independent)
Selected cohort resolution **G* = 8** (coarsest granularity resolving the reference turnover, convergent). The
map #1 negative is confirmed NOT to be a tracer-resolution artifact: static-regime M is invariant to granularity.
EXP_FL_01 map #2 uses G*=8 and must instead widen the PARAMETER DOMAIN (flux-favouring), not the tracer.
