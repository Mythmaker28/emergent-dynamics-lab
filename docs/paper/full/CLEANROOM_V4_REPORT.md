# Clean-room V4 report

Independent-environment reproduction of the **canonical V4** numbers and figures from committed data only.
Not a third-party / human replication.

## Procedure
1. Isolated tree (native filesystem) with only: the `reproduction/` package source, `requirements-lock.txt`,
   `reproduction/EXPECTED.json`, and `results/observer/tca_holdout_raw.pkl`.
2. Fresh `python -m venv`; installed **only** from `requirements-lock.txt` (numpy==2.2.6, matplotlib==3.10.9;
   Python 3.10.12).
3. Ran `python -m reproduction.primary --check` and `python -m reproduction.test_canonical` in a stripped
   environment (`env -i`, no inherited `PYTHONPATH`, no reused `__pycache__`).

## Result: PASS — 7/7 outputs byte-identical (SHA-256)
| output | match |
|---|---|
| primary_table.csv | ✓ |
| primary_results.json | ✓ |
| fig_longitudinal_v4.png | ✓ (hash-identical) |
| fig_h1_certification_v4.png | ✓ (hash-identical) |
| fig_h2_deepturnover_v4.png | ✓ (hash-identical) |
| fig_gate_summary_v4.png | ✓ (hash-identical) |
| synthesis_table.tex | ✓ |

Figures are **hash-identical** across environments because PNG metadata (software/time chunks) is suppressed
and the bootstrap seed is fixed (20260715). `--check` passed (values within tolerance point=0.06, ci=0.08);
`test_canonical` passed (the four frozen numbers within tolerance).

## Canonical numbers reproduced
h1 deep-turnover **0.89** [0.84, 0.96] (CERTIFIED); h2 deep-turnover **−0.24** [−0.78, 0.32] (NOT ESTABLISHED);
track survival 36/36; switches 0. Exact: h1 = 0.8878 [0.8366, 0.9581]; h2 = −0.2394 [−0.7850, 0.3182].

## V4 manuscript compilation & residual-number check
- `ORGANIZATIONAL_MEMORY_FULL_MANUSCRIPT_V4.tex` compiles with pdflatex+bibtex: **24 pages, 0 undefined
  references**, 0 overfull > 10pt.
- **No residual canonical use of the old headline numbers.** Whole-PDF scan: `0.97,1.00` = 0, `−0.89,0.87` = 0,
  `h2 = 0.34` = 0. The single occurrence of the substring `0.98` in the PDF is the **moderate-checkpoint h1 CI
  upper bound** `0.93 [0.89, 0.98]` in the pipeline-generated synthesis table (Table `tab:synthesis`) — itself
  a canonical pipeline output, not the historical `0.98` headline. The old values appear only in
  `HEADLINE_NUMBER_ERRATUM.md`, clearly labelled historical/non-reproducible.

## Determinism note
Deterministic given the same numpy build; the clean-room used the lockfile numpy 2.2.6. CSV/JSON/figures are
byte-identical to the canonical `reproduction/outputs/`.
