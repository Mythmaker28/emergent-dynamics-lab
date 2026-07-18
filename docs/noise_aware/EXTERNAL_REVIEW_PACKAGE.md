# EXTERNAL REVIEW PACKAGE — EXP-GT-NASI-00
`EXTERNAL HUMAN REVIEW: PENDING` (an internal agent cannot substitute for an independent human reviewer).

## Contents
* Theory: `docs/consolidation/SET_IDENTIFICATION_MANUSCRIPT.md` (T6-A..E).
* Failure audit: `HISTORICAL_FAILURE_AUDIT.md`.
* Instrument + spec: `noise_aware/nasi.py`, `NOISE_AWARE_SPEC.md`, `NASI_FREEZE_MANIFEST.json`.
* Preregistration: `PROSPECTIVE_PROTOCOL.md` (committed at 33ef80e BEFORE the run).
* Raw results: `results/EXP-GT-NASI-DEV/`, `results/EXP-GT-NASI-PROSPECTIVE/` (all 5000 cases + forensics).
* Audits: `PROSPECTIVE_AUDIT.md`, `REPLICATION_AND_FHN.md`, `HOSTILE_REVIEW.md`, `CLAIM_SCOPE.md`.
* Repro: `Makefile`, `Dockerfile`, `.github/workflows/nasi-ci.yml`, `REPRODUCTION.md`.
* Figures + provenance: `docs/noise_aware/figures/`.

## One-command reproduction (host with Docker)
```
docker build -t nasi-repro . && docker run --rm nasi-repro make reproduce-paper-all
# expect: CANON_SHA256 36b25c3ed1e13caa9d0321ac1f0fb7eee9ceeae8aa197bfd2ddf3418ec2ddd4a
```
Without Docker: `make reproduce-nasi` (numpy only).

## Reviewer checklist
1. Re-derive T6-A..E; check the interval propagation in `nasi.identify` matches the inequalities.
2. Confirm 0/5000 false `{0}` from the raw rows; confirm the 57 invalid points and 2 catastrophic.
3. Confirm `blind_used_truth = 0` (no oracle leakage) in dev and prospective.
4. Confirm the prospective generator commit (33ef80e) PRECEDES the results commit (2aef791) and the
   instrument hash is unchanged between them (no post-hoc tuning).
5. Rebuild the container and check the canonical SHA.
6. Judge whether the point-suppressed set-only variant deserves a fresh preregistered hold-out.

## Ten strongest objections
See `HOSTILE_REVIEW.md` (abstention-driven safety; 95% ≠ certainty; oracle/generator leakage; post-freeze
tuning; MC dependence; degeneracy; FHN inflation; figure selection; suppressed failures; duplicated
evidence; sandbox git integrity). Each is marked RESOLVED / NARROWING / BLOCKING there.

## Known limitations
POINT identification is unsafe under dropout/sparse contamination (withdrawn); coverage is claimed only
within the declared noise family; reproduction container/CI not executed in-sandbox; FHN is structural
only; droplets remain a negative passive-observability example.
