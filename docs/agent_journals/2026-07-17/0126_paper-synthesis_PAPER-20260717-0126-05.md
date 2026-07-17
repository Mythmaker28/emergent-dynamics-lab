# Agent journal — paper synthesis

- **Role:** manuscript synthesis, numerical reconciliation, visual communication, adversarial review, PDF QA
- **Run ID:** `PAPER-20260717-0126-05`
- **Start:** 2026-07-17 01:26:23 +02:00 (branch creation)
- **End:** 2026-07-17 02:09:00 +02:00; finalized immediately before the coherent package commit
- **Starting Git state:** clean worktree at `a8d6446fade6dbeb984e269fab27ddd5ebf75286`
- **Starting branch:** isolated `paper/persistence-without-ownership-05`, created exactly from the starting commit
- **Ending Git state:** 38 package/journal files staged as one coherent commit; no unstaged or unrelated change; commit identity recorded in the final handoff
- **Scheduled-run lock:** not applicable; this was a direct user-requested manuscript task and launched no experiment

## Assigned scope

Create a 7,000–9,000-word external-review manuscript and complete supporting package from protected V4.1, CONFIRM-02, prospective turnover 03G, and raw-only reproduction 03M. Do not run a simulation, change scientific code or protocol, alter protected histories, push, submit, post, or contact anyone.

## Important sources read

- Repository operating contract and research-state documents required by `AGENTS.md`.
- V4.1 correction commit `847d51ef78d0d55d30f05df275d97aa4af0c558f` and its committed raw/ledger artifacts.
- CONFIRM-02 preseal `9b7580bc3a09293a4b0b19b70cff8c39c5cb1378`, prospective result `830c2d006f5278295e965887f8ccedee34d47e67`, and post-hoc addendum `9c8a62cd3f6794eb9ac435f638671e5561086cd0`.
- Sealed turnover result `9cb996bb891f9a618e593f2f5c302f30210458de`, final seal `cdf7277a00e3017a1389e9334d983364b9aa0af88c646cdec2999e6ad88757fd`, raw manifest, ledger, certificate, protocol, manifest, and decision tree.
- Independent reproduction `a8d6446fade6dbeb984e269fab27ddd5ebf75286`.

## Actions and reproducible commands

1. Created the isolated paper branch at exact parent `a8d6446…` and expanded sparse checkout only for source reading and paper outputs.
2. Wrote `scripts/recompute_and_figures_05.py` to read exact Git bytes, verify hashes, recompute only from committed raw data, call the independent 03M estimator, and generate eight figures.
3. Ran:

   ```powershell
   & 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' `
     paper/persistence-without-ownership-05/scripts/recompute_and_figures_05.py
   ```

   Result: CONFIRM valid 23; turnover valid 21; Outcome B; V4.1 deep h1 0.69469387421633; eight figures; `engine_imported=false`; `seed_executed=false`.
4. Verified 30 DOI references with `scripts/verify_references_05.py`; 30 verified, 0 failed.
5. Drafted the 7,060-word manuscript, standalone supplement, claim ledger, reconciliation, provenance map, figure index, raw registry, reproducibility guide, cover letter, French public summary, three hostile reviews, and response draft.
6. Compiled PDFs with official Tectonic 0.16.9 and removed all overfull boxes and undefined-reference/citation warnings.
7. Rendered 21 manuscript pages and 6 supplement pages at 140 dpi. Inspected all 27 pages via 14 lossless paired-page sheets. Recorded page-level results in `PDF_VISUAL_QA_REPORT_05.md` and removed temporary renders.
8. Ran `scripts/validate_package_05.py`: PASS; 7,060 words; eight figures; 17 exact source bindings; 30 references; exact Outcome B; no experiment or seed execution.

## OBSERVED

- 03G has 50 primary raw worlds for seeds 54001–54050, each once, 21 valid, minimum 18, no reserve.
- Exact gates: `G_OWN_PERM=true`, `G_CAUSAL=true`, `G_LOCAL_EXCLUSION=false`, `DISTRIBUTED_ENV=false`; Outcome B.
- L-over-E and L-over-B failed the frozen positive-lower-bound criterion.
- V4.1 deep h1 grouped R² is 0.69469387421633 across only three original worlds; historical certification was withdrawn; deep h2 is not established.
- 03M agrees over 9,357 terminal leaves, including 9,283 numeric leaves, with maximum absolute difference 0.
- Final PDFs are visually intact across all 27 pages.

## INFERRED

- The sealed C1c result dissociates causal persistence from preregistered local ownership.
- The strongest licensed statement is a passive local causal remnant whose exclusive ownership remains unresolved.
- V5 should coexist with V4.1, preserve it as the correction record, and become the primary external-review manuscript.

## HYPOTHESIS

A future architecture with protected bistability, active error correction, compartment-specific histories, or explicit reconstruction could pass the ownership conjunction even where C1c fails.

## WHAT WOULD FALSIFY THIS?

A separately sealed prospective architecture in which target-local scope L fails to beat the same matched alternatives, or in which causal expression collapses, would falsify that future architecture-specific hypothesis. The present package makes no prediction that every richer architecture will pass.

## Failures and dead ends

- The bundled document Python lacked Matplotlib; the repository’s established virtual environment was used for the final no-engine reconstruction.
- Initial Tectonic output contained overfull hash/code lines; `seqsplit`, a dedicated hash macro, and emergency stretch removed all overfull boxes before QA.
- Bundled Poppler override wrappers pointed to a missing relative location; direct bundled native Poppler executables were used.
- No scientific dead end required adaptation, new data, or a prospective rerun.

## Decisions

- Preserve the exact failed ownership gate as the paper’s main result.
- Treat `DISTRIBUTED_ENV=false` as “detectable environmental ownership not established,” never environmental absence.
- Keep the historical V4.1 point estimate only as qualified context.
- Package as primary V5 coexisting with, not replacing or deleting, V4.1.

## Files changed

- Added only `paper/persistence-without-ownership-05/**`, two compiled PDFs under `output/pdf/`, and this individual journal.
- No runner, engine, protocol, experiment, result, raw record, statistical gate, environment, family, tracking, A–F tree, or DEV scientific payload was modified.

## Unresolved risks

- Author, affiliation, ORCID, contribution, funding, conflict, corresponding-author, target-journal, and repository-release fields require human completion.
- Valid-world inference is conditional on frozen feasibility and tracking.
- Tested access scopes are finite and do not exhaust distributed representations.
- The causal readout is directly engineered; active reconstruction is absent.

## Handoff

Review the V5 package scientifically, fill human metadata only after review, select a journal, and preserve V4.1 as the correction record. Do not run another 54xxx family. The exact future Git action, if authorized, is `git push -u origin paper/persistence-without-ownership-05`.

## Exact next authorized action

Human external scientific review of the committed V5 package; no experiment, push, submission, posting, or contact is authorized by this run.
