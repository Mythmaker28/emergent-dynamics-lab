# Reproducibility guide 05

## Scope

This guide rebuilds the paper’s statistics, figures, bibliography ledger, and PDFs from committed sources. It does **not** execute the simulation engine or any 54xxx seed. Run it from a clean checkout with the paper branch checked out.

## Frozen source commits

- V4.1 correction: `847d51ef78d0d55d30f05df275d97aa4af0c558f`
- CONFIRM-02 preseal/result/addendum: `9b7580bc3a09293a4b0b19b70cff8c39c5cb1378`, `830c2d006f5278295e965887f8ccedee34d47e67`, `9c8a62cd3f6794eb9ac435f638671e5561086cd0`
- Prospective turnover: `9cb996bb891f9a618e593f2f5c302f30210458de`
- Raw-only reproduction and paper parent: `a8d6446fade6dbeb984e269fab27ddd5ebf75286`
- Final seal SHA-256: `cdf7277a00e3017a1389e9334d983364b9aa0af88c646cdec2999e6ad88757fd`

## Requirements

- Git with access to the complete local object database.
- Python 3.11+ with NumPy, SciPy, Matplotlib, and the dependencies already used by the repository’s raw-only analysis.
- Tectonic 0.16.9 or another compatible LaTeX engine for PDF compilation.
- Poppler `pdfinfo` and `pdftoppm` for PDF QA.

## Numerical and figure rebuild

```powershell
$py = 'C:\path\to\python.exe'
& $py paper/persistence-without-ownership-05/scripts/recompute_and_figures_05.py
& $py paper/persistence-without-ownership-05/scripts/validate_package_05.py
```

Expected reconstruction summary:

```json
{"confirm02_valid":23,"engine_imported":false,"figures":8,"seed_executed":false,"turnover_outcome":"B","turnover_valid":21,"v41_deep_h1":0.69469387421633}
```

Expected package validator status is `PASS`, with a 7,000–9,000-word manuscript, eight figures, 30 verified references, 21 turnover-valid worlds, and Outcome B.

The reconstruction script uses `git show COMMIT:PATH` to bypass working-tree end-of-line conversion. It verifies source byte hashes before parsing. It writes only under `paper/persistence-without-ownership-05/`. A run that imports `edlab` engine modules or initializes a seed must be rejected.

## Reference verification

The committed bibliography is already verified. A live refresh is optional and changes no scientific result:

```powershell
& $py paper/persistence-without-ownership-05/scripts/verify_references_05.py
```

Expected: 30 verified, 0 failed. Because the lookup uses the Crossref REST API, metadata formatting can drift; DOI identity is the relevant check.

## PDF build

```powershell
& $py paper/persistence-without-ownership-05/scripts/build_pdfs_05.py `
  --tectonic 'C:\path\to\tectonic.exe'
```

The outputs are:

- `output/pdf/PERSISTENCE_WITHOUT_OWNERSHIP_05.pdf`
- `output/pdf/PERSISTENCE_WITHOUT_OWNERSHIP_05_SUPPLEMENT.pdf`

Tectonic logs are emitted beside the PDFs. Warnings must be reviewed; undefined references, missing citations, missing figures, or overfull boxes are blockers.

## Visual QA

Render every page, inspect every rendered page, and record the page count and defects in `PDF_VISUAL_QA_REPORT_05.md`:

```powershell
pdfinfo output/pdf/PERSISTENCE_WITHOUT_OWNERSHIP_05.pdf
pdftoppm -png -r 140 output/pdf/PERSISTENCE_WITHOUT_OWNERSHIP_05.pdf tmp/pdfs/main/page
pdfinfo output/pdf/PERSISTENCE_WITHOUT_OWNERSHIP_05_SUPPLEMENT.pdf
pdftoppm -png -r 140 output/pdf/PERSISTENCE_WITHOUT_OWNERSHIP_05_SUPPLEMENT.pdf tmp/pdfs/supp/page
```

Check title/author placeholders, table and equation clipping, figure legibility, caption wrapping, blank pages, bibliography continuity, page numbers, and stray control text. Delete temporary render files after inspection.

## Scientific acceptance checks

1. Seeds 54001–54050 appear as historical raw records only; no seed execution occurs.
2. Exactly 50 primary worlds, 21 valid worlds, minimum 18, and no reserve.
3. `G_OWN_PERM=true`, `G_CAUSAL=true`, `G_LOCAL_EXCLUSION=false`, `DISTRIBUTED_ENV=false`.
4. L-over-E and L-over-B have lower intervals ≤0.
5. Outcome is exactly B.
6. V4.1 deep h1 is 0.69469387421633 across exactly three original worlds and carries no certification claim.
7. 03M compares 9,357 terminal leaves and reports maximum numeric absolute difference 0.
8. The conclusion does not establish environmental absence, active reconstruction, identity, agency, life, reproduction, heredity, or evolution.
