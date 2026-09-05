# Statistical reviewer — EDL-ASTRA-FLAGSHIP-PAPER-01

Role: independent statistical reviewer assigned by primary agent. Start: 2026-09-05; starting HEAD cc1f186b8017e123fd7b1876b683838d08814e09, clean initial state. Scope: existing 03G records, inference, denominator selection, LOWO dependence, permutation, scope comparisons and causal readout. No simulations, experiment launches, commit or push. This is an interactive review, not a scheduled run; scheduled-run lock does not apply.

Read: AGENTS.md, research charter, state, decision/experiment/run indices, last completed audit journal, pinned B manuscript, 03G frozen protocol/manifest/decision tree, historical independent implementation as a comparison target only, frozen source via exact Git 06fd9524 blobs, raw manifest and 50 JSON worlds.

OBSERVED: code constructs overlapping LOWO training folds; frozen intervals summarize fixed losses. All-branch assay geometry selects valid worlds. Fixed masks are initialized after branch-specific relaxation, not common between branches. Own-dose draws restart the same seed used by initial world construction. These facts constrain inference irrespective of numerical reproducibility.

INFERRED: failure of the exclusion conjunction cannot establish absent local ownership; loss intervals do not have demonstrated generalization coverage; permutation exchangeability after feasibility selection is an assumption. The engineered uptake connection requires an explicitly limited causal claim.

HYPOTHESIS: direct causal contrasts are stable across independent valid worlds, whereas ownership decisions depend on small-sample prediction uncertainty. WHAT WOULD FALSIFY THIS: raw-derived sign inconsistencies, substantial influence of one world, arithmetic mismatches, or a calibrated test showing scope equivalence.

Actions in progress: independent matrix-form LOWO/permutation calculation, delete-one-world full refitting, three explicitly post hoc ridge values, sign tests and paired collapse-margin summary. Outputs only under paper/causal-persistence-ownership-01/reviews/statistics/. Frozen source files unchanged.

Unresolved: manuscript review pending new draft from parent. Ending state, checks and final disposition will be appended below.

## Initial review completed — 2026-09-05 02:49 Europe/Paris

Changed only this journal and three files in the assigned statistics directory: STATISTICAL_REVIEW.md, recompute_sensitivity.py, STATISTICAL_SENSITIVITY.json. The script resolves source paths relative to its location, checks all 50 raw hashes and imports no project modules. The explicit reproduction command above ran successfully. Its matrix predictions agree with separate normal-equation calculations to 1.249e-16 across five scopes and 21 outer folds; held-world coefficients are identically zero; prediction rows preserve the intercept; all 1,000 permutations preserve world label multisets and training variances. A validation rerun after adding these meaningful assertions passed.

OBSERVED: 17 worlds ineligible, 11 SPLIT and 1 LOST before deep, 21 reached deep and all 21 valid. No realized extra assay-only exclusion. New independent LOWO/permutation agrees with historical arithmetic. Own effect, sham/neighbor contrasts and fixed-mask effect are positive in all 21. Paired half-own-minus-residual is 0.06428125 [0.05742986, 0.07113264], positive 21/21. Delete-world full refitting reveals E/B sign-of-bound and Gm sensitivity; no frozen gates changed.

Decision: initial methods review complete, major limitations repairable in a narrowed manuscript. The absence-of-ownership thesis itself is unsupported. No new experiments warranted by this review. Parent notified of every material finding and output. Parent owns aggregate indices, integration and Git publication, so the subagent does not modify shared indices or commit/push. Git state contains expected concurrent work by other agents; none is changed here. Exact next action: review parent's new MANUSCRIPT.tex and SUPPLEMENT.tex when supplied.

## Standalone packaging follow-up

Parent clarified that new manuscript sources will be MANUSCRIPT.md and SUPPLEMENT.md, with ReportLab-rendered PDFs. Updated the existing-data script to prefer article-local data/results and verify the full local INPUT_MANIFEST (222 files in this version), requiring all 50 raw records plus their manifest. Corrupt/incomplete article-local inputs fail closed. Repository fallback is used only when the article-local raw directory is absent. All output paths/status are relative and the standalone path needs no Git or repository. Reproduction passed with mode STANDALONE_PAPER_INPUTS, full 222-file hash/size verification and unchanged statistical validation (maximum direct-solve prediction difference 1.249e-16). Review reproduction instructions now use a portable Python command. No engine import. Awaiting parent's notification that Markdown text is ready for final review.

## Final article review — initial disposition

Read both new Markdown sources in full, analyze.py and all generated numerical tables. Added verify_final_tables.py and FINAL_NUMERICAL_CHECK.json under the assigned review directory only. Independent verification covers all 50 cohort rows, 21 world rows, 63 predictions and seven scopes (P/Gf included). Max prediction difference 6.94e-17, loss difference 7.55e-15, world-contrast difference 0 and summary difference 9.99e-16. One-sided sign probabilities match their explicit alternatives; the earlier review's two-sided numbers are distinct as expected. Tests passed without a simulator import. Removed only an incidental own Python bytecode file; no other agent's work touched.

FINAL_MANUSCRIPT_REVIEW.md finds all eight earlier statistical requirements adequately addressed in the new text. Three new minor factual wording repairs were sent to the parent: abstract denominator M (current marked/current total), unsaved coefficients claimed as retained, and missing positive-L-skill-band constituent in local-exclusion definition. No change to numerical outcome. Awaiting exact corrected text for verified PASS addendum. No new experiment, commit or push.

## Final verified disposition — 2026-09-05 03:22 Europe/Paris

Parent supplied corrected/resolved sources and new scale/full-ablation diagnostics. Read the resolved article, revised Supplement sections, 25-row claim matrix, updated analyze.py and SUMMARY. All three FM corrections verified. Extended the independent final-table checker to directly verify intact uptake scale, mean target-then-world fractional reduction and all 63 target full-ablation residuals. Confirmed 3.0080940789 units, 5.5666946% mean fractional reduction and exactly zero in all 63 full-ablation contrasts. Reproduction PASS, no new numerical differences beyond prior floating-point tolerance. Resolved-text SHA-256 values and current script/results/claim-matrix hashes recorded in FINAL_NUMERICAL_CHECK.json and the final review addendum.

Final decision: PASS for the bounded scientific/statistical text and artifact claims, with disclosed limits. No unresolved statistical finding remains in scope. The judgment is an internal AI review for author/outside expert evaluation, not external peer review, novelty certification, absent-ownership evidence or trajectory regeneration. Source-model code and all original inputs unchanged. Only assigned statistics-review files and this journal modified; no commit/push or shared index edits. Parent owns final package integration and PDF QA. Exact next action: parent may include this completed statistical review in the final package without another approval request.

Ending Git observation: HEAD 85b912f4a2de4bcf819a3d4881313cc1328e67e0 (parent's concurrent integration); this journal and assigned statistics directory are untracked pending parent's coherent commit. No subagent Git mutation occurred.
