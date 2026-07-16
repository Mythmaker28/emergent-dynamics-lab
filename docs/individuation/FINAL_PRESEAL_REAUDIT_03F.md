# Final PRESEAL re-audit 03F

## Verdict

**NOT READY — REPAIR REQUIRED.**

Repair commit `23b6e9b3c667705158af833c1cf8458a03c8fb66` does not close every material blocker from audit
`9038ff08f7487e10f3615c269ed2a3af7197e2cb`. No `FINAL_SEAL_MANIFEST_03E.json` was created.

The prospective family remains unopened. This re-audit executed no seed in `54001-54096`, instantiated no
prospective world with such a seed, and created no prospective output.

## Audited objects

- Remote: `https://github.com/Mythmaker28/emergent-dynamics-lab.git`
- Repair branch: `repair/lci-causal-turnover-preseal-03e`
- Exact repair tip: `23b6e9b3c667705158af833c1cf8458a03c8fb66`
- Exact repair parent: `a5e0a552b3f34a8cf9912292cd74bce3c6aee2d3`
- Previous audit: `9038ff08f7487e10f3615c269ed2a3af7197e2cb`
- Previous audit parent: `a5e0a552b3f34a8cf9912292cd74bce3c6aee2d3`
- Protected archive: `archive/main-f3921a4` =
  `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77`
- Audit branch: `audit/lci-causal-turnover-final-re-audit-03f`

The repair is one commit adding 17 files and 1,459 lines to the audited parent. All 21 blob IDs listed by
`TURNOVER_EXECUTION_MANIFEST_03E.json` match the canonical Git objects at the repair tip.

## Audit disposition A-J

| audit | result | evidence |
|---|---|---|
| A — provenance | **FAIL** | All required refs resolve exactly and no structured `54001-54096` result record or filename was found. However, the unchanged 03C candidate still declares itself `AUTHORITATIVE` and its executable 32,768-dimensional runner remains present, so supersession is not unambiguous and a competing authority remains active. |
| B — blocker closure | **FAIL** | Only B6 closes cleanly. B1-B5 retain material implementation or reproducibility defects described below. |
| C — access scopes | **FAIL** | The 03E extractor produces L=11, N=11, P=33, E=24, Gm=18, Gf=18; E and Gm masking pass. A synthetic target-memory swap leaves Gf identical while changing L, falsifying the claim that Gf nests L. The old authoritative 03C raw E/G decoder also remains reachable. |
| D — ownership and causal gates | **FAIL** | The library implements the declared permutation, local-exclusion, causal, and conjunctive primary functions. No canonical raw-data analysis driver calls them, joins the causal batteries, or emits the primary/A-F decision. |
| E — statistical integrity | **FAIL** | LOWO, training-only scaling, fixed ridge `lambda=1`, fixed-fold bootstrap, duplicate-world rejection, null failure, and local-synthetic pass are reproducible. A distributed synthetic produces positive E skill and failed local exclusion, but no implementation classifies it as outcome F. |
| F — authorization and ledger | **FAIL** | The same synthetic approval starts two independent run directories. Arbitrary seed `99999` is accepted, a seed can be appended after completion, and deletion of the completion entry leaves a valid prefix that `verify_chain` accepts. Runner/analysis blobs are not direct authorization fields, runtime hashes are not compared with the seal, and partial-seed resume is absent. |
| G — family, power, feasibility | **FAIL** | Family constants and independent power regeneration pass. The 03E runner has no reserve-activation function and never calls `run_seed`, `record_seed`, or `close_run`; therefore the frozen primary/reserve sequence is not executable without post-seal code or external orchestration. |
| H — tracking and events | **PASS** | Tracer observationality, per-target turnover, first eligible snapshot, cap, bijective censorship, no daughter continuation, five evidence frames, and fission/fragmentation/merge/loss/death distinctions pass the committed tests and source audit. |
| I — environment | **FAIL** | The exact Linux/Python 3.11.15 environment could not be recreated: Docker failed because a WSL update is required. The alleged lock is not installable with `pip -r`; `platform==Linux-x86_64` is an invalid requirement. A substitute Python 3.12 Windows environment with the exact three package versions passed tests, but does not satisfy the sealed platform requirement. |
| J — decision tree | **FAIL** | The JSON contains A-F wording, Boolean strings, precedence, forbidden claims, and future-only active-reconstruction flags. There is no executable evaluator or analysis path that computes `DISTRIBUTED_ENV` and selects one outcome; known distributed synthetic data therefore cannot reach F through committed code. |

## Six-blocker closure matrix

| blocker | previous failure | 03E repair | code/document evidence and test | result | residual limitation |
|---|---|---|---|---|---|
| B1 authorization/final seal/ledger | Approval could be replayed; no final-seal binding or immutable ledger | Added final-seal field validation, O_EXCL ledger creation, hash chain, raw hashes, completion event | `turnover_execution_ledger.py`; committed positive tests pass. Independent red team accepted the same approval in two directories, arbitrary seed `99999`, and a post-completion append; truncating completion still verified | **FAIL** | No canonical directory enforcement, no global authorization consumption, no family/order validation, no close enforcement, no partial resume, no truncation anchor |
| B2 ownership/permutation/causal gates | No ownership permutation or causal primary gate | Added within-world permutation, L-vs-N/E/Gm/B, causal battery, and `primary = perm AND exclusion AND causal` | `turnover_statistics_03e.py`; null/local/duplicate/causal synthetic checks pass | **FAIL** | Library is not connected to a canonical analysis driver or decision output; distributed synthetic cannot be assigned to F |
| B3 E/G dimensionality | 32,768 predictors against 51 minimum training rows | Added fixed E=24, Gm=18, Gf=18 summaries | Dimensions and target masking pass; synthetic swap proves Gf is invariant while L changes | **FAIL** | Gf does not nest L as claimed; old 03C raw decoder and old authoritative candidate remain reachable |
| B4 canonical A-F tree | No frozen outcome tree | Added `TURNOVER_DECISION_TREE_03E.json` | Six outcomes, precedence, wording, and forbidden claims are present | **FAIL** | Expressions are unevaluated strings; no committed classifier connects statistics and feasibility to a unique outcome |
| B5 environment and power | Conflicting environment descriptions; no power regenerator | Added scoped environment text/lock and deterministic quadrature script | Power reproduces `0.924519023324`; canonical lock SHA-256 is correct | **FAIL** | Exact Linux environment not recreated; lock is not a valid requirements lock; runtime interpreter/packages/platform are not enforced by the runner |
| B6 main/provenance | Protected `f3921a4` object unavailable remotely | Added remote archival ref | `archive/main-f3921a4` resolves exactly to full protected hash; prior audit and repair ancestry resolve exactly | **PASS** | Archive is intentionally not an ancestor of turnover; current remote `main` remains a different lineage |

## Material findings

### F1 — the repaired runner is not an execution runner

`turnover_prospective_runner_03e.py:178-203` validates authorization, creates or resumes a ledger, and exits.
Its AST contains zero calls to `run_seed`, `ledger.record_seed`, or `ledger.close_run`. The primary/reserve plan,
valid-world stopping rule, raw output persistence, and completion closure cannot be executed by this canonical
entry point.

### F2 — authorization remains replayable across output directories

`turnover_execution_ledger.start_or_resume` applies O_EXCL only to the path supplied by `--run-dir`.
`turnover_prospective_runner_03e.py:182` accepts an arbitrary directory. The same authorization and seal
successfully initialized two fresh synthetic directories. The claimed “canonical run directory” is neither a
constant nor an enforced resolved path.

### F3 — the ledger does not enforce its declared lifecycle

- `record_seed` accepts a seed outside the frozen family.
- `record_seed` does not reject writes after a completion entry.
- Removing the terminal completion entry produces a valid hash-chain prefix accepted by `verify_chain`.
- No partial-seed/checkpoint event or atomic partial-resume protocol exists.
- Concurrent resumes are not serialized around append.

The chain detects modification and reordering of retained entries, but it is not a complete immutable
one-execution state machine.

### F4 — the seal does not enforce code or environment identity

The runner hashes the final-seal file but does not parse it or compare its protected objects with runtime files.
It records current working-copy code and environment hashes after authorization without checking them against
the seal or execution manifest. Load-bearing `turnover_statistics.py` and `turnover_event_evidence.py` are not
protected by the 03E execution manifest. The authorization validator accepts no runner or analysis blob fields.

The manifest approval phrase and committed template phrase also disagree:

- manifest: `I AUTHORIZE ONE PROSPECTIVE EXECUTION OF LCI-CAUSAL-TURNOVER-PRESEAL-03E`
- template: the same text plus `FINAL_SEAL_SHA256=<FINAL_SEAL_SHA256>`

### F5 — there is no canonical 03E analysis or decision implementation

`turnover_statistics_03e.py` is a library. There is no 03E equivalent of the raw-data builder and report writer,
and no code evaluates the A-F tree. The runner persists low-dimensional scope JSON, but no canonical module:

1. loads valid ledger-backed raw records;
2. constructs L/N/P/E/Gm/Gf/B matrices;
3. constructs the deep causal batteries;
4. evaluates ownership and causal gates;
5. computes `DISTRIBUTED_ENV`;
6. chooses exactly one A-F outcome.

### F6 — G-full does not nest L

Gf is only an occupied-cell global mean/std summary. Swapping the same memory-value multiset between the target
and another region leaves Gf unchanged while changing the target-local L vector. Gf therefore contains target
memory contribution but does not mathematically nest the 11-dimensional target-local representation.

### F7 — authority is ambiguous

03E adds a new protocol and candidate but does not change the old files. `PRESEAL_CANDIDATE.json` still says
`AUTHORITATIVE PRESEAL CANDIDATE`; `PRESEAL_CANDIDATE_PROTOCOL.md` still says it is canonical; and the old 03C
runner remains executable. The new prose saying those files are superseded does not make the repository authority
machine-unambiguous.

### F8 — exact environment reproduction failed

The canonical lock bytes have the claimed SHA-256
`a0bdccc0c2d91d7df9b1781df9198fa6d9131bd45a1e46e4c18b72a8f86aea0e`.
However, the file is a descriptive contract rather than an installable hash-locked environment. Docker could not
start its Linux engine because the host requires a WSL update, and `pip install -r` rejects the lock syntax.
Per the mission’s mandatory rule, inability to recreate the exact environment is independently sufficient for a
NOT READY verdict.

## Positive findings retained

- Exact repair tip, parent, previous audit, previous audit parent, and protected archive match.
- All 03E manifest-listed blob IDs match canonical Git objects.
- No structured prospective seed record or filename for `54001-54096` was found in fetched branch history.
- 03E scope dimensions are low and fixed; target-memory masking for E/Gm works.
- LOWO uses original-world folds, training-only scaling, fixed lambda, and fixed-fold uncertainty.
- Null, local, duplicate-world, and causal synthetic checks pass.
- Power regenerates independently:
  `P(N_valid >= 18 | N=50)=0.570903754175`,
  `P(N_valid >= 18 | N=96)=0.924519023324`.
- Tracker 10/10, tracer checks, event distinctions, and lambda-plus-only preservation pass.
- The A-F wording avoids identity, life, reproduction, heredity, evolution, and demonstrated active reconstruction.

## Seal disposition

`FINAL_SEAL_MANIFEST_03E.json` is intentionally absent. The required authorization template remains invalid and
contains no seal hash. A separate repair and another fresh independent re-audit are required before human
authorization can be safe.
