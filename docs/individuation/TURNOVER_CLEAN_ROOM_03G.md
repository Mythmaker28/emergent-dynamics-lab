# Turnover 03G clean-room and DEV verification

Date: 2026-07-16. Branch: `repair/lci-causal-turnover-end-to-end-03g`. Exact parent:
`23b6e9b3c667705158af833c1cf8458a03c8fb66`.

This report verifies implementation and integration only. It is not a prospective scientific result, a final seal,
or human authorization.

## Authoritative environment

- Platform: Windows AMD64, Windows build `10.0.26200`.
- Interpreter: CPython `3.12.10`.
- Clean environment: `C:\Users\tommy\Documents\ising-lci-turnover-03g-clean`.
- Lock: `docs/individuation/TURNOVER_ENVIRONMENT_LOCK_03G.txt`.
- Lock SHA-256: `bdffda614e9fb1062d301a6c25b13737362f54c621a90c6d8d1f52c2271f4f4f`.
- Imports: NumPy `2.2.6`, SciPy `1.15.3`, Matplotlib `3.10.9`.
- `pip check`: no broken requirements.
- `pip freeze --exclude pip`: exact set equality with the committed lock.

Recreation commands:

```powershell
$root = "C:\Users\tommy\Documents\ising-lci-turnover-repair-03g"
$clean = "C:\Users\tommy\Documents\ising-lci-turnover-03g-clean"
python -m venv $clean
& "$clean\Scripts\python.exe" -m pip install --upgrade pip
& "$clean\Scripts\python.exe" -m pip install -r "$root\docs\individuation\TURNOVER_ENVIRONMENT_LOCK_03G.txt"
& "$clean\Scripts\python.exe" -m pip check
```

No exact Linux-reproduction claim is made.

## Protected-artifact integrity

The production and DEV execution manifests each protect 37 transitive artifacts, including the scoped
`.gitattributes` rules that freeze audited working-tree bytes. Canonical Git blob IDs were
computed with `git hash-object --path`, so repository filters are represented exactly rather than by CRLF-converted
working-copy assumptions. Runtime byte SHA-256 and canonical Git blob checks produced zero mismatches for both
manifests.

A staged-index checkout simulation using `git cat-file --filters --path` reproduced every protected runtime
SHA-256 and Git blob pair, 37/37. This specifically verifies that a fresh checkout applies the sealed LF/CRLF rules
rather than depending on the current working copy.

The DEV seal-to-manifest-to-authorization binding also passed:

- DEV manifest SHA-256: `a4e41737b3eb2fe516b6d83452ae4a60f6f069cc585ecd008f6f5f15befaaf30`.
- DEV manifest Git blob: `0de7dfd368b97529a542faaa6ee369cf60142412`.
- DEV seal SHA-256: `764d3d5881c548b64a57c1206465846b1199af233c5cbd4da43552f628383947`.
- Protected-map digest: `49d1173fd3acf8e4d406d1fdca3fd556675b5e43ceea096d6d34fdf31c8a75d8`.
- Family digest: `f1276ef845d680915ba6e17104d2d6f92f20e7bcf3fc3dcf0021925b91e5fd9e`.

`docs/individuation/FINAL_SEAL_MANIFEST_03G.json` is absent.

## Test evidence

All commands used the clean interpreter.

| Check | Result |
|---|---|
| `python -m unittest experiments.individuation.test_turnover_end_to_end_03g -v` | 7/7 PASS in 69.185 s |
| `test_turnover_preseal_03e.py` | 18/18 PASS |
| `test_turnover_preseal_03c.py` with repository `PYTHONPATH` | 9/9 PASS |
| `test_bijective_tracker.py` | 10/10 PASS |
| `test_turnover_tracer.py` with repository `PYTHONPATH` and `PYTHONUTF8=1` | ALL PASS, including seed-50001 fission censorship |
| `turnover_runner_03g.py --selfcheck` | PASS; engine not imported and no seed run |
| protected Python compilation | 27/27 PASS |
| power regenerator | `P(N_valid>=18|50)=0.5709037541746931`; `P(N_valid>=18|96)=0.9245190233241044` |

The 03G integration suite invokes production modules and covers the A–F fixtures, seal/code/analyzer/family/
environment/authorization tamper, ledger lifecycle and tamper cases, interrupted resume, second-run refusal, raw
tamper and mixed schemas, duplicate worlds, reserve blinding, feature dimensions, and exact G-full nesting.

Two setup dead ends were preserved:

1. The first direct 03C/tracer invocations lacked the documented repository `PYTHONPATH`; they failed during
   `edlab` import and passed after the environment was set.
2. The first tracer rerun used the Windows cp1252 console and failed while printing `Δ`; `PYTHONUTF8=1` repaired
   output encoding without changing test logic.
3. The pre-commit staged audit found that `core.autocrlf=true` would change newly committed LF artifacts on a fresh
   checkout. Scoped, protected `.gitattributes` rules now freeze exact LF bytes for 03G and DEV outputs while
   retaining the inherited audited CRLF bytes.
4. The first post-rebinding DEV invocation exposed an ambient-`PYTHONPATH` dependency before engine import. The
   ledger stopped safely at `PRIMARY_RUNNING`; the runner was repaired to insert its repository root, then a new
   clean fresh run succeeded without `PYTHONPATH`.

A whole-repository `python -m compileall -q edlab` still reports the pre-existing unrelated syntax error
`edlab/experiments/sc_hmc/driver.py:51: unterminated f-string literal`. That file is unchanged from the exact parent,
outside the 03G protected graph, and was not repaired under this mission. All 27 protected Python files compile.

## Real DEV end-to-end evidence

The structurally complete DEV path executed only previously opened seed `50001`:

`DEV authorization -> DEV seal -> runtime protected-file checks -> real C1c engine -> ledger -> canonical raw ->
raw manifest -> closed family -> analyzer -> Outcome E certificate -> CERTIFIED`.

- Canonical DEV directory: `results/LCI-TURNOVER-DEV-E2E-03G`.
- Ledger state: `CERTIFIED`, 10 entries.
- Ledger terminal tip: `e79cfc4f33cbd788fe1109d43b83d20ef4d6f4d4d295f8a3aad24203cd4fadf0`.
- Raw seed file SHA-256: `a43817bb72f62c8a2b0f9f1fa919579840e249546e260d2ebbeea10fa9663df6`.
- Raw manifest SHA-256: `acc06908e40ffe0c02c5e0f2a38d7d398fce4e41f73c9aa87e50392e4594f50a`.
- Analysis certificate SHA-256: `cffe379a6c41e71bc849db98ea5a7c8649b709ea12f87fa2cc793cb49ee87b5f`.
- Human report SHA-256: `ebcfab410b6c72de3b1a7a013c2c6806eb03223f8e1fe0e2349c3b4dc7a8a68a`.
- Raw schema: `LCI-TURNOVER-RAW-03G-v1`.
- Persisted event classification: `FISSION`.
- Explicit `g0`: rest valid, deep invalid.
- DEV outcome: E, feasibility failure (`n_valid=0` under the one-seed DEV cap).

The DEV Outcome E is exploratory operational evidence only. It is not a prospective finding and cannot support a
positive or negative scientific claim.

The second fresh invocation failed with
`canonical execution already exists; use explicit resume`. Explicit `--resume` returned `already_certified` with
the same 10 entries and terminal tip, without rerunning or overwriting seed `50001`.

## Seed and provenance boundary

Committed DEV raw and ledger evidence contains only seed `50001`. No seed `54001-54096` or any other `54xxx` seed
was executed or instantiated by this repair. No prospective raw was created.

Observed refs, without mutation:

- exact repair parent: `23b6e9b3c667705158af833c1cf8458a03c8fb66`;
- fresh audit input: `e18024b098f20dda0125a9010703a968e49cb171`;
- local `main` and `origin/main`: `6d0bed67339c1b422877b8bfaae6861669597a93`;
- protected archive: `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77`.

Current main and the protected archive remain distinct lineages. Neither was changed.
