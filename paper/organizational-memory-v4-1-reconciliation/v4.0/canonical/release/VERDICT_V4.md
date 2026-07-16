# CANONICAL-REANALYSIS-V4-01 — Final verdict

## VERDICT: READY FOR INDEPENDENT HUMAN REVIEW.
Not "ready for public release": author/affiliation/funding metadata must still be filled and Tommy must
explicitly authorize any push, tag, DOI, or deposit.

## Basis
The manuscript's headline longitudinal numbers now come **exclusively** from the committed, deterministic
`reproduction/` package, and the whole V4 package is internally consistent, reproducible, and honestly
documented.

- **Canonical numbers adopted** (frozen): h1 deep-turnover **0.89 [0.84, 0.96] — CERTIFIED**; h2 deep-turnover
  **−0.24 [−0.78, 0.32] — NOT ESTABLISHED**; survival **36/36**; switches **0**. (Exact: h1 0.8878
  [0.8366, 0.9581]; h2 −0.2394 [−0.7850, 0.3182]; the brief's "−0.79" is −0.7850 rounded — the pipeline value
  −0.78 governs.)
- **No decoder was reconstructed or tuned** to recover 0.98; the old 0.98 / 0.34 are documented as historical,
  non-reproducible in `HEADLINE_NUMBER_ERRATUM.md`.
- **Figures and the synthesis table are generated only by the pipeline** (`reproduction/figures.py`, imported
  by `reproduction.primary`); no number is hand-inscribed in any image or synthesis cell.
- **Clean-room from a fresh lockfile venv: 7/7 outputs byte-identical** (CSV, JSON, all four figures
  hash-identical, synthesis table). `--check` and `test_canonical` PASS in the stripped environment.
- **V4 manuscript compiles: 24 pages, 0 undefined references, 0 overfull>10pt.** No residual canonical use of
  the old headline numbers; the only `0.98` substring in the PDF is a pipeline-generated moderate-checkpoint CI
  bound (`0.93 [0.89, 0.98]`), not the historical headline.
- **Automatic canonical test** (`python -m reproduction.test_canonical`) asserts the four frozen numbers within
  tolerance and passes.
- **No conclusion is overturned.** Only the h1 deep point/CI shrank (0.98→0.89); it is still certified. The h2
  "not established" conclusion is unchanged. Interpretation guardrails honored: h1 not called near-perfect /
  individual memory / identity; h2 not called globally impossible / no-memory / definitively falsified.

## Deliverables (this mission)
`ORGANIZATIONAL_MEMORY_FULL_MANUSCRIPT_V4.{tex,pdf}`, `SUPPLEMENT_V4.pdf`, `HEADLINE_NUMBER_ERRATUM.md`,
`CLAIM_LEDGER_V4.md`, `STATISTICAL_REAUDIT_V4.md`, `CLEANROOM_V4_REPORT.md`, `COVER_LETTER_V4.md`,
`RELEASE_MANIFEST_V4.json`, plus the extended `reproduction/` package (figures + canonical test) and updated
release README / CITATION.

## Remaining before public release (operator, not done here)
1. Fill author / affiliation / ORCID / funding (title page, `CITATION.cff`, `AUTHORS.md`).
2. Adapt the AI-assistance disclosure to the target venue's policy.
3. (Recommended) an external human replication of the primary result.
4. Explicit authorization from Tommy to push / tag / mint a DOI / deposit — none performed.

## Constraints honored
No new model; no new scientific simulation (only deterministic re-analysis of committed data); no decoder
tuned to save any number; no push, tag, DOI, upload, preprint, or submission. V3 commits preserved unmodified;
`main` untouched.
