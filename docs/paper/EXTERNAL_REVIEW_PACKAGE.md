# EXTERNAL REVIEW PACKAGE (deliverable 15)
`EXTERNAL HUMAN REVIEW: PENDING` — an internal agent cannot substitute for an independent human reviewer.

## Contents
* Manuscript: `MANUSCRIPT.md`. Theorem appendix: `THEOREM_APPENDIX.md`, `STABLE_BIAS_IMPOSSIBILITY.md`.
* Claim table: `FINAL_CLAIM_TABLE.md`. Taxonomy: `FAILURE_TAXONOMY.md`. Anchors: `EXTERNAL_ANCHORS.md`.
* Statistical audit: `SET_STATISTICAL_AUDIT.md`. Figures + provenance: `docs/point_cert/figures/`.
* Raw artifacts: `results/EXP-GT-NASI-PROSPECTIVE/`, `results/EXP-GT-PC-PROSPECTIVE/` (all cases + forensics).
* Instruments (frozen): `noise_aware/nasi.py` (3027044479), `point_cert/pointcert.py` (8c1bf736).
* Reproduction: `Makefile`, `Dockerfile`, `.github/workflows/nasi-ci.yml`, `REPRODUCTION_LOG.md`.

## One-command reproduction (host with Docker)
```
docker build -t emergent-metrology-repro . && docker run --rm emergent-metrology-repro make reproduce-all
# expect PC_CANON_SHA256 17080664... and NASI 36b25c3e...
```

## Reviewer checklist
1. Re-derive T6-A..E and Propositions 1–2; check the set propagation matches the inequalities.
2. Confirm 0 false {0} on both hold-outs; confirm point coverage 101/127 and 0 catastrophic.
3. Confirm blind arm used_truth = 0; confirm generator commit precedes results commit, instrument hashes
   unchanged between them.
4. Check the marginal-vs-conditional coverage distinction (set 0.959 marginal; contam_highSNR 0.80).
5. Reproduce the stable-bias demo (var→0, bias persists).
6. Rebuild the container; check canonical hashes.

## Ten strongest objections
See `HOSTILE_REVIEW_FINAL.md` (oracle contracts; stable-bias assumptions; prospective reuse; set/point
conflation; conditional vs marginal; FHN inflation; droplet overinterpretation; duplicated evidence; figure
denominators; Docker; selective zero-catastrophic reporting) — each RESOLVED / claim-narrowed / marked
blocking-for-point-only.

## Response template
For each reviewer objection: (a) restate; (b) evidence file + hash; (c) resolution: correction /
claim-narrowing / explicit limitation / conceded-blocking; (d) manuscript section updated.

## Known limitations
Marginal empirical set coverage only (not uniform; degrades on stable-contamination direction); point ID
withdrawn; substrate-specific quantitative recovery; Docker/CI not executed in sandbox; no external human
review; droplet is a negative example, not a proof about all substrates.
