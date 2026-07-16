# V4.1 reproducibility commands

All commands are analysis-only. They read committed artifacts and do not launch
the simulation engine.

From the repository root:

```powershell
$analysisPython = "C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe"
$pdfPython = "C:\Users\tommy\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

& $analysisPython .\paper\organizational-memory-v4-1-reconciliation\v4.1\scripts\reconcile_v4_1.py
& $analysisPython -m pytest .\paper\organizational-memory-v4-1-reconciliation\v4.1\scripts\test_v4_1_reconciliation.py -q
& $pdfPython .\paper\organizational-memory-v4-1-reconciliation\v4.1\scripts\build_pdfs.py
& $pdfPython .\paper\organizational-memory-v4-1-reconciliation\v4.1\scripts\render_pdf_qa.py
& $pdfPython .\paper\organizational-memory-v4-1-reconciliation\v4.0\verify_v4_0.py
```

Canonical V4.0 reproduction, retained for audit but not treated as valid V4.1
inference:

```powershell
$env:REPRO_OUT = Join-Path $env:TEMP "organizational-memory-v4-repro"
Push-Location .\paper\organizational-memory-v4-1-reconciliation\v4.0\canonical
& $analysisPython -m reproduction.primary --check
& $analysisPython -m reproduction.test_canonical
Pop-Location
Remove-Item Env:\REPRO_OUT
```

The V4.0 commands reproduce the V4.0 numbers. The V4.1 command answers a
different methodological question: performance across held-out original worlds.

## Inputs

- `results/observer/tca_holdout_raw.pkl`
- `results/wd01_phasec/phasec_causal_transplant_raw.pkl`
- `results/wd01_phasec/phasec_causal_inplace_raw.pkl`
- `results/h2cert/h2cert_sealed_raw.pkl`

No frame recomputation, trajectory replay, seed execution, or physics call is
performed.

## Primary V4.1 estimator

- model: ridge regression, lambda = 1;
- scaling: mean and standard deviation from the outer training worlds only;
- constant columns: removed using the outer training worlds only;
- outer group: simulation seed, interpreted as the original world;
- score: pooled out-of-world R-squared;
- sensitivity: each test row additionally excludes its history from training;
- uncertainty: original-world fold values, a descriptive small-sample t
  interval, and exact block resampling of fixed out-of-world predictions.

Because only two to four original worlds exist in the relevant artifacts, none
of the intervals is used as high-confidence certification.
