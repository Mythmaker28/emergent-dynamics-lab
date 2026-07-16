# Final PRESEAL audit 03D

## Verdict

**NOT READY — REPAIR REQUIRED.**

No valid `FINAL_SEAL_MANIFEST_03D.json` was created. The prospective family remains unopened and unauthorized.
This audit executed no seed in `54001-54120` and created no prospective result.

## Audited object

- Remote: `https://github.com/Mythmaker28/emergent-dynamics-lab.git`
- Branch: `codex/lci-causal-turnover-preseal-integration-03c`
- Exact audited commit: `a5e0a552b3f34a8cf9912292cd74bce3c6aee2d3`
- Exact parent: `cd74eda96cbcf6e1489f8a6572d1eda8f619b8a1`
- Required ancestry:
  `244bc3262580f1344db1b00582f626a48c75ab4e -> ca7929bedb4e9eb08695a82484619e344b8c4085
  -> cd74eda96cbcf6e1489f8a6572d1eda8f619b8a1 -> a5e0a552b3f34a8cf9912292cd74bce3c6aee2d3`
- Audit branch: `audit/lci-causal-turnover-final-preseal-03d`

Canonical Git-object verification passed:

| artifact | expected blob | observed blob |
|---|---|---|
| `PRESEAL_CANDIDATE.json` | `39a2d036c6810a9f10c00fa803896be5bf251bf5` | same |
| `PRESEAL_CANDIDATE_PROTOCOL.md` | `c4c40c9b001d83a25ae2934ca7e051ef825cdb7f` | same |
| `TURNOVER_EXECUTION_MANIFEST_03C.json` | `e109d7eabbc944b1d25d743c13c2f7561e7fccca` | same |

All 21 protected blobs listed by the execution manifest match the canonical objects at the audited commit.

## Gate disposition

| audit | disposition | summary |
|---|---|---|
| 1. Provenance and unused family | **FAIL** | Tip, parent, ancestry, candidate blobs, unopened-family search, committed state, and blob-size checks pass. Required protected `main` object `f3921a4` is absent from every fetched ref and cannot be fetched by object name, so the protected-main condition cannot be certified. |
| 2. Family and reserve | **PASS WITH LEDGER CAVEAT** | Exact 50 primary + 46 reserve family, cap 96, minimum 18, feasibility-only trigger, ascending reserve, and stop rule are implemented. Independent quadrature gives `P(N_valid >= 18 | N=96) = 0.924519`, matching the rounded `0.93`. Duplicate/tampered records are not rejected because the execution ledger is not immutable. |
| 3. Execution authorization | **FAIL — MATERIAL** | Approval binds the execution-manifest blob but not a final-seal hash. The same authorization can initialize another output path. No authorization-consumption record, immutable execution ledger, hash chain, completion marker, or raw-result checksum exists. |
| 4. Material turnover and geometry | **PASS** | Passive tracer, per-target `M_i`, first eligible `M_i <= 0.25` snapshot, cap 1500, all-target validity, bijective censorship, five evidence frames, and distinct event classes are implemented and pass existing DEV/synthetic tests. |
| 5. L/N/P/E/G access structure | **FAIL — MATERIAL** | Definitions, masking, deterministic geometric neighbours, label exclusion, centring, and sidecar persistence pass. E/G each flatten 8 x 64 x 64 = 32,768 predictors. At the minimum 18 worlds an outer fold has 51 training rows, a predictor/row ratio of 642.5, with no frozen reduction or dimensional adequacy certificate. |
| 6. Statistical inference | **FAIL — MATERIAL** | LOWO, training-only scaling, fixed lambda, fixed-fold uncertainty, and no bootstrap refit pass. The authoritative analysis has no within-world permutation ownership null, no causal-expression gate, no `L_over_G` gate, and declares the primary pass from the local-storage decoder gate alone. |
| 7. Mechanistic controls | **PASS WITH DOCUMENTATION WARNING** | Lambda-plus-only preserves `lambda_minus=0.15`; full ablation, sham, neighbour erasure, fixed-mask readout, and the no-active-reconstruction boundary are distinct. The authoritative protocol names `eta_w=0` and copy-disabled DEV diagnostics but does not itself state the required no-new-writing/passive-copy and counterfactual-not-same-physics interpretations. |
| 8. Decision tree and claims | **FAIL — MATERIAL** | Forbidden identity/life/reproduction/heredity/active-reconstruction claims are excluded. The authoritative candidate does not freeze the required A-F outcome tree, and its emitted `primary_gate_pass` does not require causal expression. |
| 9. Environment and reproduction | **FAIL — MATERIAL** | Manifest says Python 3.10.12 / NumPy 2.2.6 / SciPy 1.15.3; `pyproject.toml` requires Python >=3.11; Docker uses Python 3.11 and NumPy 2.1.3 without SciPy; the available venv is Python 3.12.10 / NumPy 2.5.1 / SciPy 1.18.0. No committed script regenerates the power headline, and prospective raw/certificate checksums are not specified. |

## Material blockers

### B1 — final-seal and one-execution authorization are not enforced

- Location:
  `experiments/individuation/turnover_prospective_runner.py:106-119`,
  `experiments/individuation/turnover_prospective_runner.py:342-408`.
- Observed:
  `validate_human_approval` checks a Boolean `one_execution_only` field but writes no consumption state. `main`
  keys resumption only to the chosen output file. No final-seal field is read anywhere.
- Consequence:
  one approval can start multiple fresh output files; a resume cannot be globally distinguished from a prohibited
  second execution; tampered or duplicate records are not protected by an immutable ledger.
- Minimum repair:
  bind approval to the exact final-seal object and use a single append-only, hash-chained execution ledger that
  atomically consumes an authorization ID, records resume state, rejects duplicate/tampered records, and seals raw
  outputs and sidecars.

### B2 — the frozen primary gate does not answer the stated causal-ownership question

- Location:
  `experiments/individuation/turnover_statistics.py:184-250`,
  `experiments/individuation/turnover_ownership_analyze.py:84-108`,
  `docs/individuation/PRESEAL_CANDIDATE_PROTOCOL.md:150-170`.
- Observed:
  the local gate requires L versus intercept, N, E, and B. There is no within-world dose permutation null, no
  causal-expression gate, and no L-versus-global gate. `primary_gate_pass` is the local-storage gate alone.
- Consequence:
  the candidate can report a primary PASS without establishing prospective causal behavioural expression, and the
  ownership null required by this audit is not implemented.
- Minimum repair:
  predeclare and implement a world-preserving ownership null, a paired original-world causal-expression gate, and
  the complete frozen access/decision logic before any family execution.

### B3 — E/G dimensionality is not justified for the minimum sample

- Location:
  `experiments/individuation/turnover_scope_features.py:115-165`,
  `docs/individuation/PRESEAL_CANDIDATE_PROTOCOL.md:111-130`.
- Observed:
  each E/G row contains 32,768 float predictors. The minimum outer training set contains 51 target rows. The
  protocol explicitly forbids dimension reduction and provides no dimensional adequacy certificate for fixed
  lambda `1.0`.
- Consequence:
  L-versus-E/G loss comparisons mix radically different effective model capacities and cannot support a defensible
  local-versus-distributed storage conclusion at the minimum valid-world gate.
- Minimum repair:
  freeze a scientifically justified training-only representation or a prospectively validated scope-comparison
  method whose operating characteristics are established at 18 valid worlds.

### B4 — the authoritative A-F outcome tree is absent

- Location:
  `docs/individuation/PRESEAL_CANDIDATE_PROTOCOL.md`,
  `docs/individuation/PRESEAL_CANDIDATE.json`.
- Observed:
  no authoritative A-F decision tree is present. Mechanistic readouts are described as secondary diagnostics.
- Consequence:
  the mapping from decoder, causal-expression, distributed-access, and feasibility outcomes to allowed wording is
  not sealed before data.
- Minimum repair:
  freeze the complete A-F decision table, required gates, authorized wording, and forbidden overclaims in the
  authoritative protocol and machine-readable candidate.

### B5 — the declared execution environment is internally contradictory

- Location:
  `docs/individuation/TURNOVER_EXECUTION_MANIFEST_03C.json:43-47`,
  `requirements-lock.txt:1-6`,
  `pyproject.toml:5-13`,
  `Dockerfile:1-8`,
  `docs/individuation/TURNOVER_REPRODUCTION.md:3-55`.
- Observed:
  four environment descriptions disagree. The documented Windows commands point to another checkout and an
  interpreter that is not the declared Python 3.10.12 environment.
- Consequence:
  static checks passed only in an unpinned Python 3.12 environment; exact candidate reproducibility is not
  demonstrated.
- Minimum repair:
  provide one internally consistent lock/container, verify it end to end, and bind its files to the final seal.

### B6 — required protected-main provenance cannot be established

- Location: remote Git object database and advertised refs.
- Observed:
  `f3921a4` is not a valid fetched object and `git fetch origin f3921a4` reports no such remote ref. Current remote
  `main` is `6d0bed67339c1b422877b8bfaae6861669597a93`.
- Consequence:
  the mission's protected-main invariant cannot be verified.
- Minimum repair:
  identify the intended full protected-main hash and prove its relation to the advertised remote history before
  resealing.

## Positive findings retained

- The prospective branch hash, parent, and required 03A/03C ancestry are exact.
- No committed raw result, checkpoint, log, figure, output filename, JSON seed record, or historical diff was found
  for any seed `54001-54120`.
- No Git blob exceeds 100 MB; the largest observed blob is about 15.2 MB.
- The family and reserve arithmetic are exact.
- Independent posterior-predictive calculation reproduces:
  `P>=18 @ 50 = 0.570904` and `P>=18 @ 96 = 0.924519`.
- All manifest-listed candidate blobs match.
- Existing grouped-inference, scope-masking, reserve-blinding, event-evidence, tracker, and tracer tests pass.
- DEV diagnostics remain exploratory and were not promoted.
- V4.1 was not modified and no turnover result was inserted into paper results.

## Seal disposition

`FINAL_SEAL_MANIFEST_03D.json` is intentionally absent. The invalid authorization template contains no seal hash and
cannot authorize execution.
