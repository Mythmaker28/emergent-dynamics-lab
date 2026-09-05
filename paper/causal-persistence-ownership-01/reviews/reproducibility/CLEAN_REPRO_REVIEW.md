# Independent clean-copy reproducibility review

**Final disposition: PASS for the stated same-data, clean-copy reconstruction scope. Zero open fatal or major findings.** The final run reproduced all 25 compared artifacts byte for byte, including both PDFs. This acceptance supersedes the initial correction request below while preserving its evidence.

Reviewer: clean-reproduction agent, internal computational review #3. Review scope: executable closure, relocated-file independence, exact numerical/document reconstruction, input-corruption rejection and rendered document legibility. This is not external peer review or regeneration of simulation worlds.

## Initial disposition: corrections required before final acceptance

The first isolated-copy rebuild succeeded at all four declared steps. It used no Git command, simulator import or new world. A one-byte raw-data change was rejected before any analytical result was written. Mathematical computations already present in the master and newly rebuilt package agreed, but the master PDFs/results lagged current editable sources. Final artifact equality must be checked after the integrator's rebuild.

| ID | Severity | Finding | Required disposition |
|---|---|---|---|
| CRR-01 | Major document correctness | ReportLab's bundled Vera font lacks the Greek symbols used in the mathematical definitions. Manuscript pages 2-3 and Supplement pages 1-5 render them as empty boxes. Static font mapping confirms missing Delta, Psi, beta, delta, epsilon, eta, lambda, rho, sigma, tau and chi. | Embed a complete font as a portable input or render explicit readable equivalents; rebuild and inspect all affected pages. |
| CRR-02 | Minor layout | Supplement S5.1's four-column feature table uses a generic 12% width for its long Construction column, producing broken words and excessive row height. | Assign widths matching this table's content and inspect the complete table. |
| CRR-03 | Minor layout | Figure 1's panel-a title touches panel-b's vertical axis label. | Shorten the title or increase panel spacing. |
| CRR-04 | Release synchronization | At first inspection, generated master artifacts predated current source additions: full ablation, nonzero sign counts, cohort tokens, reference [8], and revised text. Input files did not change during the clean run. | Rebuild master, freeze its source versions and repeat comparison. This is expected during editing; it cannot remain at final delivery. |
| CRR-05 | Minor provenance completeness | The initial `results/REPRODUCTION.json` included primary results, figures and PDFs, but not the reviewer-generated statistical/source-check JSONs used by the package. | Include those in a final release artifact manifest or clearly link the independent review's hash inventory. |

## Procedure and evidence

The version tested is defined by the complete `tested_inputs` hash inventory in `CLEAN_REPRO_CHECK_20260905T010951232688Z.json`; the source Git head was `cc1f186b8017e123fd7b1876b683838d08814e09`, and the new paper was not yet committed. The test created a new directory under `C:/Users/tommy/Documents/edl-paper-clean-reproduction-20260905/`, containing the complete data/source capsule, analysis scripts, the two editable sources and required reference inputs. No pre-existing results, figures, PDFs, resolved Markdown, reviewer-generated JSON, bytecode, or Git metadata were copied.

The declared rebuild ran from a path containing spaces. PATH and PYTHONPATH were empty, user-site packages were disabled, and the top-level process used Python's isolated mode. Only explicitly passed absolute interpreter paths launched child processes. The dependency libraries already installed locally were reused: Python 3.12.10, NumPy 2.5.1, SciPy 1.18.0, Matplotlib 3.11.0; rendering used Python 3.12.14, ReportLab 4.4.9 and pypdf 6.10.0. The pip wheel cache did not contain the required numerical packages. This establishes relocated-copy and clean-process reproducibility, not a clean dependency installation, cross-platform equivalence, independence from BLAS versions, or fresh experimental replication.

The initial successful rebuild checked 222 manifest entries and reconstructed the historical analysis, independent primary analysis, statistician's sensitivity calculations, source-model parameter extraction, four figures and both documents. The exact command and subprocess outputs are retained in the machine report. Existing historical replay, predictions, fold losses, figures and reviewer computations agreed; mismatched artifacts were the currently unsynchronized output versions listed in the report.

The negative case was a second fresh copy. At the first occurrence of `54001` in `seed_54001.json`, one byte was changed from `5` to `6`, preserving JSON syntax and file size. `scripts/analyze.py` failed on the SHA-256 check. Its result and figure directories contained no files. Master source files were never modified.

All eight reconstructed manuscript pages and nine Supplement pages were rendered to PNG and inspected individually. The initial visual findings are CRR-01 through CRR-03. Poppler emitted fallback-font configuration warnings, but the observed Greek-box defect was independently traced to the embedded Vera font's actual character map. A first console print of missing Unicode glyphs failed under CP1252; repeating with escaped JSON succeeded and did not modify any scientific artifact.

## Final recheck

The final immutable machine record is `CLEAN_REPRO_CHECK_20260905T014051917162Z.json`. It identifies 241 copied input/build/asset files, including all 222 scientific manifest entries, and verifies that none changed during the test. A new owned Matplotlib configuration directory was used. The four-stage rebuild completed successfully in approximately 12.5 seconds. All 25 compared output files are byte-identical to the stabilized master: historical replay, primary summaries, numeric substitutions, all CSVs, all five PNG/vector figure pairs, both resolved Markdown files, both PDFs, and the two reviewer-generated JSON computations consumed by the build. The complete file list and hashes, including those reviewer JSONs, are in the machine record's `artifact_comparisons`; this also supplies the missing provenance inventory requested in CRR-05.

This delivery recheck supersedes the preceding successful round `CLEAN_REPRO_CHECK_20260905T012609223728Z.json` solely because newly authored CSV serialization was made explicitly LF before release. The earlier record is preserved. All scientific values and both PDF hashes are unchanged; the existing 17-page visual evidence and font checks therefore remain exactly applicable, without a new visual interpretation.

The negative copy again rejected the size-preserving one-byte raw mutation before analytical output. Both direct `analyze.py` and the top-level `reproduce.py` returned failure; no result or figure file was produced. The final clean copies contain no Git checkout, and PATH remains empty. No simulator was imported and no new world was run.

The intermediate second round (`CLEAN_REPRO_CHECK_20260905T012040298250Z.json`) identified one additional minor reproducibility defect, **CRR-06**: the PDF creation/modification timestamps varied, because `SimpleDocTemplate` overrode the partial canvas factory's invariant default. PDF text and sizes were already identical. Adding `invariant=1` directly to the document template resolved that defect; the final PDFs now agree byte for byte. Fixed deterministic PDF metadata are build conventions, not evidence of a publication date.

| Finding | Final disposition and evidence |
|---|---|
| CRR-01 | RESOLVED. Four DejaVu Serif faces and their license are included and independently hash-checked. `PDF_GLYPH_CHECK.json` finds zero used body-codepoint gaps in all four faces; all actually used DejaVu TrueType fonts are embedded. Greek mathematical definitions are visually readable. |
| CRR-02 | RESOLVED. S5.1 uses content-specific widths; the complete feature table is readable on Supplement page 6. |
| CRR-03 | RESOLVED. Figure 1's shortened titles and adjusted spacing remove the collision. |
| CRR-04 | RESOLVED. All 25 comparisons are byte-identical after the final synchronized rebuild; no tested source changed during execution. |
| CRR-05 | RESOLVED through the explicitly linked complete comparison/hash inventory above; statistical sensitivity and static source-check JSONs are individually included. |
| CRR-06 | RESOLVED. Both final PDF byte hashes match the master after deterministic template metadata are enabled. |

All eight corrected manuscript pages and nine corrected Supplement pages were individually inspected. Both final PDFs were then rendered again using the same Poppler command. `FINAL_VISUAL_CHECK.json` verifies that every one of the 17 final PNGs is byte-identical to its individually inspected corrected counterpart; no changed page escapes the visual review. There are no empty pages or unresolved numeric-template tokens. Generic Poppler fallback-font configuration warnings persist, but all scientific prose and mathematical glyphs are present in the embedded fonts and no corresponding visual defect remains.

| Final document | Pages | SHA-256 |
|---|---:|---|
| MANUSCRIPT.pdf | 8 | `0ed41ee9aad7cf9f7a4e40dc6aa2e6632133bb2001f9048684f6f22ceffde8d9` |
| SUPPLEMENT.pdf | 9 | `7a9ad1f38e89b5054114b1d729a8726c7e21e8bb00325859e28c215685db7a07` |

README and data-provenance wording correctly distinguish the ordinary portable rebuild from the Git-dependent one-time export recipe. They also distinguish recorded reduced measurements from full spatial trajectories and the conditioned 21-world inference population from all 50 generated worlds. The review makes no statement about a new dependency installation, other platforms, independent physical trajectories, new seeds or biological validation. Those limitations remain explicit rather than being treated as hidden failures.
