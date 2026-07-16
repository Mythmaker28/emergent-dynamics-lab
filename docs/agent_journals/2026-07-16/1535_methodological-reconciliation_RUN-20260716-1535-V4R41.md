# Agent journal — RUN-20260716-1535-V4R41

- role: independent methodological reconciler and paper integrator
- run ID: `RUN-20260716-1535-V4R41`
- start time: 2026-07-16 15:00 CEST
- end time: finalized immediately before the paper-branch commit
- starting Git state: clean isolated clone at
  `23b53aee4169deeda30aad2a9dba8587024f8d3d`
- ending Git state: coherent V4.1 reconciliation staged for one local commit
- assigned scope: preserve canonical V4.0 unchanged; regenerate headline
  numbers from committed artifacts; audit bootstrap leakage; replace the
  inference with original-world grouped outer validation; produce the V4.1
  manuscript, supplement, ledgers, machine-readable results, reproducibility
  commands, cover letter, French summary, and visual PDF audit

## Important files read

- `AGENTS.md`
- `docs/RESEARCH_CHARTER.md`
- `docs/PROJECT_STATE.md`
- `docs/DECISION_LOG.md`
- `docs/EXPERIMENT_INDEX.md`
- `docs/RUN_INDEX.md`
- latest available journals, manifests, and experiment summaries
- canonical V4.0 release manifest, manuscript, supplement, claim ledger,
  statistical re-audit, reproduction code, and committed raw artifacts

## Actions

1. Located exact V4.0 commit `23b53aee...` and extracted all 37 release-manifest
   files from canonical Git blobs.
2. Verified all 37 SHA-256 values and created a byte-preserved V4.0 snapshot.
3. Reproduced the V4.0 analysis without running a simulation.
4. Audited the V4 bootstrap and found duplicate-history leakage in 3,000/3,000
   realized replicates.
5. Implemented leave-one-original-world-out ridge prediction with training-fold
   preprocessing and a crossed world-and-history exclusion sensitivity.
6. Recomputed longitudinal, tracker, transplant, in-place, and historical
   body-baseline values from committed artifacts.
7. Classified every headline numerical change as unchanged, corrected, or
   withdrawn and reconciled every authorized claim to the V4.1 ledger.
8. Wrote and compiled the V4.1 manuscript and supplement.
9. Rendered and inspected every page in both V4.1 PDFs and both preserved V4.0
   PDFs: 41 pages total.
10. Kept unsealed turnover and active-reconstruction results outside the V4.1
    abstract, results, and conclusion. Executed no prospective seed.

## Reproducible commands

```powershell
$analysisPython = "C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe"
$pdfPython = "C:\Users\tommy\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

& $analysisPython .\paper\organizational-memory-v4-1-reconciliation\v4.1\scripts\reconcile_v4_1.py
& $analysisPython -m pytest .\paper\organizational-memory-v4-1-reconciliation\v4.1\scripts\test_v4_1_reconciliation.py -q
& $pdfPython .\paper\organizational-memory-v4-1-reconciliation\v4.1\scripts\build_pdfs.py
& $pdfPython .\paper\organizational-memory-v4-1-reconciliation\v4.1\scripts\render_pdf_qa.py
& $pdfPython .\paper\organizational-memory-v4-1-reconciliation\v4.0\verify_v4_0.py
```

## OBSERVED

- Canonical V4.0 deep h1 is 0.8878 with reported bootstrap interval
  [0.8366, 0.9581].
- Every realized V4 bootstrap replicate contains a duplicate history that is
  relabelled as a new fold.
- Original-world grouped deep h1 is 0.6947 with fold scores 0.7454, 0.4141,
  and 0.9246.
- The descriptive t interval is [0.0513, 1.3381]; the fixed-fold world-block
  percentile range is [0.4859, 0.8858].
- Deep h2 is -1.1183.
- The artifact records 36/36 surviving, zero lost, zero switches, and mean deep
  M=0.1902.
- The summary artifact has no persisted masks, association edges, ambiguity
  alternatives, or merge/fusion events.
- Longitudinal and largest-component deep h1 values are 0.6947 and 0.6706.

## INFERRED

- The V4.0 interval is not leakage-free for out-of-world generalization.
- The positive deep h1 point survives, but the 0.50 lower-bound certification
  does not.
- Similar tracker points support access to globally imposed informational
  content under either selection rule, not a local-storage conclusion.
- Event-level fusion-free continuity cannot be independently reconstructed.

## HYPOTHESIS

With substantially more independently generated original worlds, the
cumulative-drive point may remain positive, but the current committed artifacts
cannot determine a reliable lower bound.

## WHAT WOULD FALSIFY THIS?

- A canonical code path showing that duplicated bootstrap draws could never
  cross training and testing would falsify the leakage diagnosis.
- A committed event-level evidence package with masks, edges, gate terms, and
  merge adjudications could falsify the claim that fusion handling is
  unreconstructable.
- A frozen local/neighbour/environment/world access comparison could establish
  a local-specific estimate and supersede the current global-only conclusion.

## Failures and dead ends

- No LaTeX engine was installed. The V4.1 PDFs were built deterministically from
  Markdown with ReportLab.
- One attempted Poppler text-extraction command was unavailable in the bundled
  binary set. Numerical and boundary checks were performed against source and
  JSON, while visual checks used complete page renders.
- Poppler reported font-discovery warnings for unavailable aliases, but all
  rendered pages displayed their text and figures correctly.

## Decision

Withdraw the V4.0 certification and local-storage interpretation. Retain the
positive grouped point estimate and direct artifact counts with explicit
small-W and event-evidence limitations.

## Unresolved risks

- W=3 for the primary result is insufficient for high-confidence uncertainty.
- Fusion handling remains unauditable from the committed summary.
- Local storage remains unresolved.
- The historical body baseline and secondary causal artifacts have their own
  small-W and tracker/recipient limitations.

## Handoff

The paper package is ready for external methodological inspection as a
reconciliation, but its final scientific verdict is `MAJOR REPAIR STILL
REQUIRED`. Do not submit, publish, push, or merge automatically.
