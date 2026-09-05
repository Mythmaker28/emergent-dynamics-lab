# Reproducibility audit — PASS

Final scope: same-data analysis, document reconstruction and source documentation. **No new simulated world, engine import or physical-trajectory regeneration.** Four internal reviews are closed for the delivered claim set; limitations of the scientific design remain explicit.

## Clean-copy result

The independent checker created a fresh relocated copy under `C:/Users/tommy/Documents/edl-paper-clean-reproduction-20260905/`. It copied the declared inputs and scripts, not pre-existing numerical results, plots, PDFs, resolved Markdown, bytecode or Git metadata. Paths contained spaces. PATH and PYTHONPATH were cleared, user-site packages disabled, and the top-level checker used Python isolated mode. Matplotlib's cache was fresh. No external repository or raw-data fallback was required.

Final machine evidence: `reviews/reproducibility/CLEAN_REPRO_CHECK_20260905T014051917162Z.json` and `reviews/reproducibility/FINAL_REVIEW.json`. It inventories 241 build inputs, verifies all 222 scientific manifest entries, and reproduces **25 of 25 compared artifacts byte for byte**, including the historical replay, new primary calculations, statistical/model checks, tables, five figures, resolved text and both PDFs. Input hashes before and after the run match; no source changed during that test.

This is a clean file copy and clean processes using existing local dependencies. It is not a fresh dependency installation, a container build, a Linux/macOS validation or a claim of BLAS-independent numerical identity. The local wheel cache did not contain the required numerical stack. That limit is recorded rather than disguised as a completed environment installation.

## Environments

| Component | Verified environment |
|---|---|
| Numerical reconstruction | CPython3.12.10; NumPy2.5.1; SciPy1.18.0; Matplotlib3.11.0 |
| PDF rendering | CPython3.12.14; ReportLab4.4.9; pypdf6.10.0 |
| Platform tested | Windows AMD64; exact platform record in `results/REPRODUCTION.json` |
| Fonts | Included DejaVu Serif normal/bold/italic/bold-italic with supplied license; separate hash manifest |

The ordinary single-environment command is `python scripts/reproduce.py`. The verified local configuration used the documented `--pdf-python` option because numerical and PDF libraries are in separate interpreters. Absolute interpreter locations are recorded in the independent machine check as execution evidence; the article's ordinary rebuild does not hard-code those paths.

## Negative and independent checks

- A separate copied raw file was altered by one byte while preserving valid JSON and length. Both direct analysis and the complete reproduce entry point rejected its SHA-256 before writing any result or figure. The master input remained untouched.
- The primary new augmented least-squares/causal reconstruction agrees with historical03M to maximum absolute difference1.1657341758564144e-15 over the checked summaries. Historical03M is transparently reused for the replay, not relabelled a new implementation.
- The statistician's separate implementation verifies63 predictions for seven scopes in21 worlds, including zero held-world fitting influence and correct intercept weights. Maximum prediction difference6.94e-17; maximum loss difference7.55e-15; per-world causal contrasts agree exactly.
- Independent editorial raw extraction verifies the intact uptake, the definition-dependent relative reduction and all63 full-ablation contrasts equal to zero.
- Static model inspection independently verifies29 frozen parameters, the actual mutual-inhibition update, source inheritance, material denominator and all selected-world ablation branch validity.
- The source/construct final check verifies the25 claim rows, evidence paths and eight references shared by both resolved documents.

Review scripts and JSON are included in `RELEASE_MANIFEST.json`, in addition to their direct timestamped check inventories. They are not omitted from the final artifact inventory merely because the shorter `results/REPRODUCTION.json` lists the core pipeline products.

## PDF and visual verification

| Output | Pages | Final SHA-256 |
|---|---:|---|
| MANUSCRIPT.pdf | 8 | `0ed41ee9aad7cf9f7a4e40dc6aa2e6632133bb2001f9048684f6f22ceffde8d9` |
| SUPPLEMENT.pdf | 9 | `7a9ad1f38e89b5054114b1d729a8726c7e21e8bb00325859e28c215685db7a07` |

Every page of both corrected documents was rendered to PNG and inspected individually by the clean reviewer. The integrator separately inspected mathematical definitions, the causal figure and the feature/parameter tables. The final17 page images match the corrected, inspected images exactly. No missing glyph, clipped content or unresolved table/figure overlap remains in that inspection.

The first rendering exposed Greek characters missing from ReportLab's Vera font, a narrow feature-table column and neighbouring figure labels. DejaVu fonts are now bundled and hash-checked; the builder asserts complete used-character coverage, and the independent PDF/font checker confirms it. Table-specific widths and shorter figure headings correct the layout defects. Poppler's global fallback-font configuration emits warnings for unused system fonts; the actual used mathematical fonts are embedded and verified.

A clean comparison also exposed wall-clock PDF metadata despite an initial canvas-level invariant request. Setting `invariant=1` on `SimpleDocTemplate` fixes that override. The final PDF bytes, not only extracted text, match between independently executed builds.

## Separate recovery audit

The corrected older audit suite completed seven checks, including source hashes, FDFLT raw endpoints, OMLDCT endpoints/statistics, Walsh-index diagnostics, candidate-B reconstruction and analytic fixtures. Its cost erratum now agrees with the separate September auditor:38 pairs at index789, rather than the integrator's former36/760. The independent September scripts also pass their frozen differential replay and five analytic CCRA tests. These different datasets are not additional primary observations in the paper.

## What PASS does not mean

The procedure does not validate independent randomized history assignment, calibrated cross-validation coverage, all-world effects, absence of ownership, unique maintenance mechanisms or biological realism. It does not independently verify another author's outcome blindness or reconstruct an absent original power-analysis script. Neither internal review nor exact artifact reproduction is journal acceptance. Those boundaries remain in the paper and the claim matrix.
