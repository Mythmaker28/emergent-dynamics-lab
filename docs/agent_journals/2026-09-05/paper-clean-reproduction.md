# EDL-ASTRA-FLAGSHIP-PAPER-01: independent clean-copy reproduction

Role: internal clean-reproducibility reviewer #3. Run ID: PAPER-CLEAN-REPRODUCTION-20260905. Start: 2026-09-05 01:04 UTC (approximately). Starting Git head: cc1f186b8017e123fd7b1876b683838d08814e09; worktree had untracked paper and other agents' reports. Those files were treated as shared work with explicit ownership. Scope: write only this journal and `paper/causal-persistence-ownership-01/reviews/reproducibility/`; independent copies under a newly created owned staging root. No commit, push, simulator, new world, other journal or index mutation.

Read: AGENTS.md; research charter; project state; decision/run/experiment indices; primary current journal; article input manifest, raw-only reconstruction code, numerical and PDF builders, reviewer scripts, dependency requirements, editable/resolved paper and Supplement. Applied PDF skill for independent reconstruction/visual QA; marker succeeded immediately before initial rebuild.

Actions: wrote reusable clean-copy script; inspected local pip cache (required wheels unavailable); copied only inputs into two fresh trees; ran all four reconstruction stages with PATH and PYTHONPATH empty and user site disabled; compared 23 generated artifacts against master; corrupted one raw byte in second copy; rendered and individually inspected all 17 PDF pages. Commands and complete source hashes are in the machine check record and review.

OBSERVED: positive rebuild succeeds; raw corruption fails before analytical outputs; no source change during the run; no new worlds. Main pre-existing outputs are stale relative to current sources; this is reported for final synchronization. Greek letters render as boxes because Vera has no corresponding glyphs. Table S5.1's Construction column is too narrow. Figure 1 has a minor label collision.

INFERRED: executable analysis closure is sufficient for this same-data reconstruction on the existing Windows libraries. This does not establish a fresh dependency installation, engine trajectory regeneration or independent scientific replication.

HYPOTHESIS: with font, table, figure and synchronization corrections, the package will reproduce without a major open delivery issue. WHAT WOULD FALSIFY THIS: failure in final clean-copy rebuild, an unexplained numerical mismatch, unbound external data access, corruption accepted, or unresolved unreadable mathematical notation.

Failures/dead ends: no numerical failure. Initial Unicode console output hit CP1252 and was rerun as escaped JSON. Pip cache lacks necessary wheels; no network install was attempted. Poppler reports generic configured fallback-font warnings. All issues are preserved rather than erased.

Decision: initial clean-copy execution passes; final review remains open pending source freeze and corrected visual QA. Handoff: reported CRR-01 through CRR-05 to primary. End/final Git state and accepted disposition will be appended after final recheck.

## Final review closure, 2026-09-05 01:29 UTC

The primary corrected missing Greek glyphs by including four DejaVu Serif faces and their license/hash manifest, changed S5.1 table widths and Figure 1 spacing, then synchronized all outputs. Round 2 reran the relocated-copy analysis successfully but exposed variable PDF creation/modification timestamps. This new minor finding CRR-06 was isolated to metadata; text and sizes matched. The primary placed `invariant=1` directly on SimpleDocTemplate and normalized only newly authored JSON serializers to UTF-8 LF.

Final round `20260905T012609223728Z` passed with 240 build inputs inventoried, 222 scientific manifest entries verified, all 25 compared artifacts byte-identical, and no input changed during execution. Both direct analysis and top-level rebuild reject one raw byte of corruption before any analytical file. Scientific execution remained zero worlds and zero simulator imports. NumPy/SciPy/Matplotlib and ReportLab dependencies were reused locally in clean processes, with a fresh Matplotlib config cache; no claim of fresh dependency installation is made.

`pdf_glyph_check.py` independently verifies all four font binaries and the license against their manifest, checks every used printable character across all four body faces, and checks embedding/extraction. PASS. The corrected eight manuscript and nine Supplement pages were inspected individually. Final PDFs were re-rendered and all 17 PNGs matched their inspected counterparts byte for byte, captured in `FINAL_VISUAL_CHECK.json`.

Final acceptance: PASS_SAME_DATA_CLEAN_COPY, zero open fatal/major findings; CRR-01 through CRR-06 resolved within the documented scope. Important owned outputs: CLEAN_REPRO_REVIEW.md, three immutable CLEAN_REPRO_CHECK JSONs, PDF_GLYPH_CHECK.json, FINAL_VISUAL_CHECK.json, FINAL_REVIEW.json, and three reusable audit scripts. No commit/push or other agent file edit was performed. Ending Git head observed during final verification: 85b912f4a2de4bcf819a3d4881313cc1328e67e0, reflecting concurrent authorized primary work; owned review paths remained untracked for integrator staging. Next exact authorized action: primary incorporates this review and its evidence hashes into the release ledger and completes PR35 handoff.

## Final delivery serialization recheck, 2026-09-05 01:42 UTC

The primary requested one bounded repeat after author-written CSV output was made explicitly LF and the scientific-check JSON serialization was normalized. No scientific value or document content changed. Read the new serializer line and confirmed the starting/ending observed Git head remains 85b912f4a2de4bcf819a3d4881313cc1328e67e0. Ran the same owned clean-copy/negative-corruption script in a new staging tree.

New immutable record: `CLEAN_REPRO_CHECK_20260905T014051917162Z.json`. PASS: 241 build inputs inventoried, 222 scientific manifest entries verified, 25/25 artifacts byte-identical, no source changed during execution, both integrity-failure paths reject the raw one-byte mutation before any analytical output. Rebuild duration approximately 12.5 seconds. Both PDF hashes are identical to the previously inspected final artifacts; the established 17-page visual and font evidence is reused on that exact-byte basis. No additional scientific analysis, test gate or simulation was introduced.

Updated only the assigned final review JSON, review Markdown and this journal, adding the new immutable machine record. Previous reports remain preserved. Final status remains PASS_SAME_DATA_CLEAN_COPY with zero open fatal/major findings. Handoff: primary uses the new report name in the release ledger and manifest, then completes the authorized delivery.
