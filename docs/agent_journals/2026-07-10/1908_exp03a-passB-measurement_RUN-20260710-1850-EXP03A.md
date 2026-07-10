# EXP03-A Internal Critique — PASS B (measurement challenge)

- Run: RUN-20260710-1850-EXP03A. Model: claude-opus-4-8 (lock lifted). Independent of PASS A.
- Question: how could density preference inflate P or long-track counts WITHOUT turnover-individuality?

## Alternative explanations to preserve (must be reported, not explained away)

- **Densification:** high `comfortable_density` packs particles into dense components the detector connects into
  large, persistent blobs -> longer tracks and higher P, but with HIGH material retention (no turnover). Signature:
  ON increases long tracks/P while `mean_turnover` DROPS (M rises).
- **Rigid clusters:** strong `density_strength` -> tight cohesive clusters translating as units -> long tracks,
  high P, M~1.0 (the same trivial-cohesion failure seen in CORE V0 law 52 under alias-intervention).
- **Bridge artefacts:** density attraction forms inter-cluster bridges -> connected-component merges -> spurious
  large entities and inflated split/merge/ambiguous events. Signature: ON raises merge/split/ambiguous counts.
- **Reduced mobility / longer slot residence:** homeostatic settling slows particles -> longer residence in
  spatial slots -> longer tracks and higher P by reduced change, i.e. LESS dynamics, not individuality.
- **Tracker-friendly motion:** slower, more regular motion -> more reliable association -> longer tracks -> P/long
  inflation without turnover.

## Guards already in the design

- P and M kept separate; no composite. The screen logs `mean_turnover`, track lengths, censoring, and
  split/merge/ambiguous counts so these confounds are visible OFF vs ON.
- Any ON screening permission is only a PERMISSION: it must pass the frozen fresh-seed hold-out, the direct alias
  audit, and (if authorized) the same-state matched-branch causal intervention — exactly as CORE V0. Screening or
  a distributional shift never equals turnover-individuality.
- The five levels are reported separately (distributional shift / screening signal / fresh-seed recurrence /
  alias rejection / causal re-establishment).

## Verdict

Confounds enumerated and instrumented. A positive screen must be read against densification / rigidity / bridge /
mobility explanations before any candidate claim. **No STOP;** proceed to the frozen screen.
