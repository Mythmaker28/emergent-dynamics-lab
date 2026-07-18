# CONSOLIDATION II — SIGN-SAFE IDENTIFIABILITY — FINAL REPORT

## What was done
Resolved the T6′ contradiction, replaced the falsified lower-bound claim with a proved set-identification theory
(T6-A..E), built an independent sign-safe instrument, qualified it on a fresh preregistered prospective split,
reproduced it with a second clean-room implementation, audited coverage and sensitivity, diagnosed the FHN
quantitative bias, and built a one-command reproduction that passes.

## Headline results
1. **The contradiction was a scope omission, not a bug.** The 40/40 bracket coverage held because every tested
   regime had ≥1 clean reference. With no clean anchor the bracket is one-sided, and its side is set by
   `sign(α·κ)` — attenuation → lower bound, amplification → upper bound. The historical "lower bound" assumed
   attenuation.
2. **Repaired theory (proved + property-tested).** T6-A (attenuation → `max|v|≤|q|`), T6-B (amplification →
   `min|v|≥|q|`), T6-C (clean anchor → bracket, sign pins the extreme), T6-D (sparsity: `m≥2s+1` for point-ID),
   T6-E (no anchor + no sign → non-identifiable, symbolic impossibility). Property tests ≥0.97 over 400 trials each.
3. **Sign-safe instrument qualified.** Fresh development 10/10 correct (0 hard failures); fresh prospective 10/10
   with **0 invalid sets**; the amplifying case that broke historical CRD-03 now returns a valid UPPER bound /
   sign-pinned point. Safety metric (confident exclusion of truth) = **0 across 1600+ trials, all sign regimes,
   all (m,s)**.
4. **Independent reproduction.** A second clean-room implementation (numpy only) agrees 20/20 on status class.
5. **Cross-substrate.** FHN structural identifiability transfers exactly; absolute recovery is biased (0.86) due to
   a diagnosed pre-window calibration issue → Outcome **S2: structural pass, quantitative substrate-specific**.
6. **One-command reproduction passes** (`make reproduce-paper`): freeze verification (16 files), stale-cache
   rejection, theorem tests, dev, prospective, independent-implementation agreement. Dockerfile pinned (not built
   in this sandbox).

## Honest limitations
- The Docker image was not built/executed here (no container runtime); the Dockerfile is provided, unverified E2E.
- FHN quantitative accuracy is substrate-specific.
- The historical CRD-03 frozen instrument still carries the sign bug — documented, not patched; the sign-safe
  instrument is a separate module.
- No external human review (required for peer-review-submission status).

## Standing constraints
No droplet pilot executed. No droplet physics / `β` / `D_int` / governing equations modified. Historical freezes
intact (v00 6/6, CRD-01 4/4, CRD-03 4/4). Historical artefacts not rewritten. New work under `consolidation/` and
`independent_replication/`.
