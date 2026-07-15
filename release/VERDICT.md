# PRE-RELEASE-CLEANROOM-01 — Final verdict

## VERDICT: NOT READY (one material blocker) — release engineering COMPLETE and clean-room VERIFIED, but the manuscript's headline numbers are not yet regenerable from committed artifacts.

This is a deliberately strict call, consistent with scientific rigor: a package sent for scientific review
should regenerate its own headline numbers from its committed code+data. It currently does not. Everything
else required to publish is done and verified.

## What is DONE and VERIFIED (green)
- **Frozen environment:** Python 3.10.12; numpy 2.2.6, scipy 1.15.3, matplotlib 3.10.9; `requirements-lock.txt`
  + full 145-pkg snapshot; reference hardware and per-step runtime documented (`release/ENVIRONMENT.md`).
- **Portable data:** CSV/NPZ/JSON exports of every primary/secondary number with `DATA_SCHEMA.md`; pickles
  retained for provenance (`release/data/`, `PORTABLE_DATA_AUDIT.md`).
- **One-command reproduction:** `python -m reproduction.primary` — deterministic, reads only committed data,
  fails loudly on missing dependency/data, regenerates the primary table, figure, JSON, and manifest.
- **Clean-room reproduction: PASS.** Fresh venv from the lockfile in a stripped environment produced
  **byte-identical** `primary_table.csv` and `primary_results.json` (SHA-256 match); `--check` within
  tolerance (`release/CLEANROOM_REPRODUCTION_REPORT.md`). Independent-environment, not third-party.
- **Conclusions reproduce robustly:** h1 deep-turnover **CERTIFIED** (bootstrap lower bound 0.84 ≫ 0.50);
  h2 deep-turnover **NOT ESTABLISHED** (CI ≤ 0.50); 36/36 track survival, 0 switches.
- **Licenses & citation:** Apache-2.0 (code), CC-BY-4.0 (data/text) verbatim; `CITATION.cff`, `AUTHORS.md`,
  release README, `DEPENDENCY_LICENSE_AUDIT.md` (all deps BSD/PSF, Apache-compatible).
- **Release branch prepared** locally (`release/organizational-memory-v1`, from V3 commit 897f81d); **not
  pushed, not tagged**. Manifest + public tree with hashes (`RELEASE_MANIFEST.json`, `PUBLIC_RELEASE_TREE.txt`).
- V3 commits preserved unmodified; `main` untouched; nothing pushed.

## BLOCKER (must resolve before scientific review)
**B1 — Primary-result numbers are not regenerable from committed artifacts.** The inline scoring script that
produced the manuscript's h1 deep **0.98** [0.97,1.00] and h2 deep **0.34** [−0.89,0.87] was never committed.
The committed-data reproduction yields the **same conclusions** with different point estimates: h1 deep
**0.89** [0.84,0.96] (still CERTIFIED) and h2 deep **−0.24** [−0.79,0.32] (still NOT ESTABLISHED). No standard
decoder tried reproduces the exact inline values. **Fix (no new simulation):** either recover + commit the
original scoring script, or adopt the committed `reproduction/` package as canonical and update the inline
values in a **future V4** (do not rewrite V3 history).

## Secondary blockers (pre-existing, operator metadata)
- B2 — Author / affiliation / funding are placeholders (`CITATION.cff`, `AUTHORS.md`, manuscript title page).
- B3 — No external/human replication; only independent-environment reproduction (by design).
- B4 — AI-assistance disclosure to be adapted to the target venue's policy.

## If B1 is resolved
If the operator recovers the scoring script (or accepts the reproduction's numbers in V4) and fills the
metadata, this package flips to **READY FOR V3 SCIENTIFIC REVIEW**: the reproduction infrastructure,
environment freeze, portable data, licensing, and clean-room verification are already in place and green.

## Constraints honored
No new physics; no new scientific simulation (only deterministic re-analysis of committed data); no change to
save h2; no push, tag, DOI, upload, or submission.
