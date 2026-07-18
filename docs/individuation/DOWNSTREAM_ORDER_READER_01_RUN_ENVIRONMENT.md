# DOWNSTREAM-ORDER-READER-01 — prospective execution environment and command

- Human authorization: exact manifest-bound authorization received 2026-07-18.
- Sealed parent: `0949ff7167082a894c12480e0b2c75b4cae1c7c6`.
- Manifest SHA-256: `0d40765937ca203269bd7fa935f3db4c999576dabf2d6ca0f96223f777ba03e4`.
- Execution branch: `codex/downstream-order-reader-prospective-seal-00`, the branch name required by the immutable
  manifest. The latest human instruction authorized execution exactly as sealed after the separate run-branch
  preflight had previously failed closed with zero initialized worlds.
- Worktree: `C:\Users\tommy\Documents\ising-v3-downstream-order-reader-seal-00`.
- OS: `Windows-11-10.0.26200-SP0`.
- Python: `3.12.10`.
- NumPy: `2.5.1`.
- SciPy: `1.18.0`.
- pytest: `8.4.2`.
- Dependency lock: unchanged sealed `requirements-lock.txt`.
- External authorization path:
  `C:\Users\tommy\Documents\DOWNSTREAM_ORDER_READER_01_EXECUTION_AUTHORIZATION.json`.
- External authorization SHA-256: `c31e5bd7065f841b0b84648450b30353910c46af11b81e2ef870c36b5b6016b2`.
- Process start: 2026-07-18 01:00:58 CEST.
- Raw COMPLETE written: 2026-07-18 01:56:12 CEST.
- Initial invocations: 1; resumes: 0; modified-code retries: 0.
- Preflight: exact manifest/parent/branch/clean tree/output absence/48 seeds/15 bound hashes; sealed engine-free
  verifier PASS 25/25 before any world initialization.

Exact execution command:

```powershell
$env:PYTHONUTF8='1'
$py='C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe'
$manifest='docs/individuation/DOWNSTREAM_ORDER_READER_01_PROSPECTIVE_MANIFEST.json'
$authorization='C:\Users\tommy\Documents\DOWNSTREAM_ORDER_READER_01_EXECUTION_AUTHORIZATION.json'
$output='results/DOWNSTREAM-ORDER-READER-01-PROSPECTIVE-001'
& $py -m experiments.individuation.downstream_order_reader_prospective `
  --manifest $manifest `
  --authorization $authorization `
  --execute `
  --output-dir $output
```

Independent reproduction command, run twice with the second output outside the repository:

```powershell
& $py -m experiments.individuation.downstream_order_reader_reproduce `
  --manifest $manifest `
  --raw-dir results/DOWNSTREAM-ORDER-READER-01-PROSPECTIVE-001 `
  --output results/DOWNSTREAM-ORDER-READER-01-PROSPECTIVE-001-independent-reproduction.json
```

Both reproduction files had SHA-256
`35616172409424d28d765acecb2c29ac1f2527fb7acd48196a9113e85081b679` and were byte-identical.

Post-run non-scientific regression validation:

```text
24 passed in 1.98s
```

The test set comprised the sealed instrumentation, prospective contract and seal tests. It uses synthetic/temp
fixtures and did not initialize another scientific source world.
