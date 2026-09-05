# Complete article package

**Testing causal memory expression and local predictive advantage after material turnover**

Start with `MANUSCRIPT.pdf` and `SUPPLEMENT.pdf`. Editable sources are the two corresponding `.md` files; `_RESOLVED.md` copies contain the exact data-derived substitutions used for typesetting. Scientific figures ship as PNG and vector PDF. The findings support a bounded computational assay case study; they do not establish absent local ownership, active memory restoration, life or heredity.

## Rebuild

Use Python 3.12 with the versions in `requirements.txt`:

```console
python scripts/reproduce.py
python reviews/statistics/verify_final_tables.py
python reviews/editorial/editorial_scale_check.py
python scripts/write_claim_matrix.py
```

If numerical and renderer libraries live in separate environments:

```console
python scripts/reproduce.py --pdf-python PATH_TO_RENDERER_PYTHON
```

The rebuild performs no network lookup, needs no Git checkout or external data directory, imports no simulator, and launches no new worlds. It verifies scientific input hashes, replays the frozen raw-only algorithm, independently recomputes contrasts/predictions, runs statistical and static-model review checks, then generates tables, figures, resolved text and PDFs. Fonts and their license are included and hash-checked.

`scripts/prepare_inputs.py` is only the historical export recipe; it intentionally requires the documented recovered Git objects and is not part of ordinary reconstruction. Regenerating physical trajectories is a distinct task and was not performed for this release.

## Review evidence

- `CLAIM_EVIDENCE_MATRIX.csv`: claim, evidence, calculation and scope.
- `DATA_PROVENANCE.md`: frozen source lineage, exact bytes and epistemic limits.
- `REPRODUCIBILITY_AUDIT.md`: clean-copy reproduction and visual QA.
- `INDEPENDENT_REVIEW_LEDGER.md`: adversarial findings and checked dispositions.
- `reviews/`: four separate internal review roles plus their independent scripts/results.
- `ASTRA_FINAL_HANDOFF_FR.md`: scientific judgment, journal fit and final action for Tommy.
- `CHANGED_FILES.txt`: repository paths included in the PR change set.

The complete September-bundle adjudication and earlier raw recovery remain separately under repository `audit/edl-flagship-01/`. Those different experiments are not additional worlds in the paper's sample. PR35 is the single review vehicle: https://github.com/Mythmaker28/emergent-dynamics-lab/pull/35. No merge, submission or publication is performed by this delivery.

## Portable review archive

`../EDL_PAPER_REVIEW_PACKAGE.zip` contains this complete article folder. Its SHA-256 is supplied beside the archive. `RELEASE_MANIFEST.json` inventories all delivered article files, including independent-review scripts and machine evidence; the manifest excludes its own hash to avoid self-reference. This standalone archive contains the B article. The separate September adjudication remains in the repository.
