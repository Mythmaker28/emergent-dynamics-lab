# FINAL HARDENING — REPORT

## What this mission established
1. **The theorems are sound.** 0 validity violations across 4000 ε-separated trials (T6-A/B/C/E). The earlier
   non-unit numbers were *informativeness*, not pass rates; every one of the 14 residual cases was a **safe
   refusal**, not a counterexample. **THEOREM PACKAGE: PASS.**
2. **The sign/anchor contracts were oracle-derived.** All 8 point identifications in the benchmark depended on
   contracts read from ground truth. Removing them → 0 points, safety preserved. Point-identification claims are now
   explicitly **conditional on externally established contracts**, which the benchmark does not show to be obtainable
   from passive data.
3. **The large hold-out FAILED.** N=2000 stratified (preregistered at a76f8a7, instrument hash-gated): **541/1333
   emitted sets exclude the truth (40.6%)**, all from a **null-response gate misfiring at SNR=5** — the instrument
   confidently claims *no response* ({0}) when a real response exists. The 10-case prospective contained no low-SNR
   stratum and passed; the stratified hold-out failed immediately. Stop rule invoked: failure preserved, instrument
   **not** patched, hold-out burned.
4. **Cross-substrate: Track A.** FHN transfers structurally; quantitative accuracy remains ctrans-specific (0.86).
5. **Clean reproduction incomplete.** No container runtime available; the Dockerfile was never built. Per the
   mission's own rule, an unbuilt Dockerfile does not satisfy the gate.

## Honest position
The **identifiability theory is solid and publishable in substance**. The **instrument is not safe as implemented**:
its detection gate produces confident false-negative sets outside the high-SNR regime it was developed in. That is a
repairable engineering defect, but the repair requires new development data and a **fresh** hold-out, neither of
which this mission may consume.

## Required next steps (not performed — would need new preregistration)
- Replace the heuristic null-response gate with a noise-aware detector with a declared false-negative rate.
- Re-derive detection thresholds on new development data.
- Preregister and run a **new** large hold-out (this one is burned).
- Build and run the container; add CI.
- Obtain external human review.

## Standing constraints
No droplet pilot executed. No droplet physics / β / D_int / governing equations modified. Historical freezes intact
(v00 6/6, CRD-01 4/4, CRD-03 4/4, sign-safe 2/2) verified from the HEAD tree. Historical artefacts not rewritten.
No claim of identity, individuality, life, or material-turnover continuity.
