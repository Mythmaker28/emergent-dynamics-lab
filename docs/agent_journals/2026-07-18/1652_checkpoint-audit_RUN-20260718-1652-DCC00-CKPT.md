# DEEP-CHECKPOINT-CAUSAL-CUT-00 Phase 0 checkpoint audit journal

- **Role:** independent already-open DEV checkpoint eligibility auditor
- **Run ID:** `RUN-20260718-1652-DCC00-CKPT`
- **Start time:** 2026-07-18 16:52 +02:00
- **End time:** 2026-07-18 17:53:33 +02:00
- **Starting branch:** `codex/deep-checkpoint-causal-cut-00-phase0`
- **Starting Git state:** `cce7a27955f5cfb1fc3d95388bba9378bc8d85eb`; the primary integrator's
  `1646_design-integration_RUN-20260718-1646-DCC00-P0.md` was already untracked and was not modified
- **Ending Git state:** same HEAD; concurrent agents' journals and the integrator's draft feasibility/schema are
  untracked; this agent changed only this journal and changed no scientific source, shared report, index, schema,
  raw result, or prior journal

## Assigned scope

Audit only already-open DEV evidence for exact deep checkpoints containing at least two continuously tracked,
separated, viable entities after deep turnover. Preserve material continuity `M` and the distinction between raw
phenotype descriptors and scalar continuity `P`; require raw tracker evidence; do not write history, initialize a
seed, inspect a prospective namespace, inspect or compute future pair-feeding `Y/C/I`, use any `58xxx` record, modify
03G/V5, relax a threshold, or rescue a failed world by selecting surviving tracks.

## Actions

1. Read the operating contract and durable state in the required order, followed by the current Phase-0.5 manifest,
   report, and latest partial integration journal.
2. Hash-audited the existing DEV turnover summary, Phase-0 pair feasibility, Phase-0.5 access qualification, and
   Phase-0.6B no-swap qualification.
3. Audited only the mechanical/checkpoint keys needed for eligibility: world ID, eligibility, deep step, passive
   deep `M`, centroid geometry, first-censor record, recorded alive flags, selected pair, and state digests.
4. Inspected the serializer and the two reconstruction call paths without executing either path.
5. Searched tracked and present workspace paths for a persisted DEV checkpoint payload. No eligible DEV payload was
   found. The only tracked file name matching a binary deep-array artifact is
   `release/data/holdout_deep_arrays.npz`; it is not a 500xx DEV checkpoint and was not opened.
6. Compared the state digests persisted by the two accepted DEV qualification artifacts.

## Important files read or changed

Read:

- `AGENTS.md`
- `docs/RESEARCH_CHARTER.md`
- `docs/PROJECT_STATE.md`
- `docs/DECISION_LOG.md`, especially D-089 through D-092
- `docs/EXPERIMENT_INDEX.md`
- `docs/RUN_INDEX.md`
- `docs/agent_journals/2026-07-18/1646_design-integration_RUN-20260718-1646-DCC00-P0.md`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_DEV_MANIFEST.json`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_REPORT.md`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_REPORT.md`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_DEV_FEASIBILITY.json`
- `docs/individuation/ACCESS_STRUCTURE_00_PHASE05_REPORT.md`
- `docs/individuation/ACCESS_STRUCTURE_00_PHASE05_DEV_QUALIFICATION.json`
- `docs/individuation/ACCESS_STRUCTURE_00_PHASE06B_NOSWAP_DESIGN.md`
- `docs/individuation/ACCESS_STRUCTURE_00_PHASE06B_NOSWAP_RESULTS.json`
- `docs/individuation/CLAUDE_JOURNAL_ACCESS_STRUCTURE_00_PHASE06B_2026-07-17.md`
- `experiments/individuation/turnover_dev_raw.json`
- `experiments/individuation/turnover_dev_runner.py`
- `experiments/individuation/bijective_tracker.py`
- `experiments/individuation/access_structure_operators.py`
- `experiments/individuation/access_structure_dev_qualification.py`
- `experiments/individuation/access_structure_noswap_dev_feasibility.py`

Changed: this journal only.

## Reproducible read-only commands and checks

```powershell
git status --short --branch
git rev-parse HEAD
git log -8 --oneline --decorate
Get-FileHash -Algorithm SHA256 <each existing DEV evidence file>
rg -n "ACCESS-STRUCTURE-00-IOMState-v1|metadata_json" .
git ls-tree -r -l HEAD | Select-String -Pattern "(?i)(access.*(npz|pkl|pickle|npy)|noswap.*(npz|pkl|pickle|npy)|checkpoint|deep.*(npz|pkl|pickle|npy))"
```

A standard-library, read-only JSON projection selected only the mechanical keys listed under Actions and compared
`worlds[*].state_hash` across the two existing qualification records. No engine or writer was imported or run.

Exact evidence hashes in this checkout:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `experiments/individuation/turnover_dev_raw.json` | 886164 | `dd326f0a31b829c8961b660b4a31533c789c19f407d2ccdc22b44fd9d48c8f54` |
| `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_DEV_FEASIBILITY.json` | 12618 | `cca455da45ce522e65113456ae2e7b497e89c634cc88e62db1411726ddb838bf` |
| `docs/individuation/ACCESS_STRUCTURE_00_PHASE05_DEV_QUALIFICATION.json` | 802296 | `15ed040fe61465ce4a389997bbc2e636a62a7dbd1d040116c26acdd88b8d5b87` |
| `docs/individuation/ACCESS_STRUCTURE_00_PHASE06B_NOSWAP_RESULTS.json` | 527579 | `100ecb994718153d3e898b610a9b80b2c5ea74005d41493cd9cc0988fa6edee6` |

## OBSERVED

### World-by-world checkpoint inventory

The pre-existing three-target world-level gate is retained. A tracker failure in one target invalidates the whole
original world; the other two tracks are not salvaged as a new pair.

| World | Existing deep record | Existing tracker disposition | Existing selected A/B and deep distance | Passive deep `M` vector | Exact serialized checkpoint admissible now? |
|---:|---|---|---|---|---|
| 50001 | none | target 1 `SPLIT@153` | none | none | no |
| 50002 | step 847 | empty `first_censor`; all 84 recorded turnover frames report all three alive | A=0, B=2; 34.37257070658307 | `[0.19399027122102552, 0.24979364401673357, 0.14509491462257568]` | no |
| 50003 | none | target 2 `LOST@236` | none | none | no |
| 50004 | step 793 | empty `first_censor`; all 79 recorded turnover frames report all three alive | A=0, B=1; 29.24205822351404 | `[0.2494180137355821, 0.24976935420627078, 0.21932890413506204]` | no |
| 50005 | step 831 | empty `first_censor`; all 83 recorded turnover frames report all three alive | A=1, B=0; 32.971137653282 | `[0.16378143695398298, 0.23030102225923835, 0.24993830710442896]` | no |
| 50006 | none | target 0 `SPLIT@692` | none | none | no |
| 50007 | step 890 | empty `first_censor`; all 89 recorded turnover frames report all three alive | A=1, B=0; 32.22276393881174 | `[0.22705715851499184, 0.21010424776025538, 0.2496506369279655]` | no |
| 50008 | none | fewer than the frozen `K=3` eligible targets; turnover not started | none | none | no |
| 50009 | none | target 0 `SPLIT@436` | none | none | no |
| 50010 | none | fewer than the frozen `K=3` eligible targets; turnover not started | none | none | no |

Thus 50002/50004/50005/50007 are **observation-level deep candidates**, not executable checkpoint artifacts. The
existing record supplies endpoint pair separation, not continuous pair distance or exact halo overlap over the
turnover interval. The turnover JSON supplies `first_censor` and sampled `alive` flags, but not every association
edge, individual gate term, chosen assignment, or tracker assignment history. Those omissions prevent the stronger
continuous geometry/tracker-independence gate required by this mission.

### No persisted exact checkpoint payload

`access_structure_operators.serialize_state` defines a complete NPZ payload with arrays
`rho,U,V,c,N,C,uptake,Mf` plus scheduler `step` under schema `ACCESS-STRUCTURE-00-IOMState-v1`. The DEV result files
persist only `state_hash` values and zero-error round-trip diagnostics produced in memory. The serialization schema
and `metadata_json` occur only in the serializer source; no accessible 500xx DEV NPZ/bytes payload, payload path,
payload size, or payload SHA-256 is indexed. A content digest is not a serialized checkpoint from which execution
can begin.

The two historical scripts reconstruct the deep state by calling `to_S0(seed)` and `run_to(..., deep_step)`, which
replays the history-bearing path. That is not permitted here: the mission requires beginning from an already
serialized checkpoint and forbids writing new history. No reconstruction or new serialization was run.

### Exact unexplained digest conflict

The conflicting keys and paths are:

- `docs/individuation/ACCESS_STRUCTURE_00_PHASE05_DEV_QUALIFICATION.json`:
  `worlds[seed==50002].state_hash = 8046a8d9567176fd318f93bd55027fc4f20ba8c14d0328a7687647a656967788` and
  `worlds[seed==50004].state_hash = 5a981dba0c3a297d255a29e3b79f3ca667d149064ada31e3b9e0fc8a47691272`.
- `docs/individuation/ACCESS_STRUCTURE_00_PHASE06B_NOSWAP_RESULTS.json`:
  `worlds[seed==50002].state_hash = bfe23b0c2bae892a60938eb65f629afca3155889fee7f77f90b30ab74a21ba4f` and
  `worlds[seed==50004].state_hash = 4f6422672e2948c828a12670fda6b3946b5ddf077ea226c88bf7863bcdffaf9f`.

Both artifacts identify the same deep steps 847 and 793. Their source functions nominally use the same
`to_S0 -> run_to` reconstruction. Phase-0.6B additionally permits an optional external pickle through environment
variable `ASNS_CACHE`, but the result contains no cache-used flag, path, payload hash, or provenance binding and no
cache artifact is present. Cache use is therefore a possible explanation, not an established one. The mismatch is
**unexplained and not an expected consequence of two declared reconstruction paths**. By contrast, 50005 agrees at
`c63ce1017a9b0f0a1b3e1aa4666d6e0acc1328916aea189ce140ac220b0ce2ce`, and 50007 agrees at
`a8a044c655151365f1ce06021c99a193876cab7e5933f53cbaf7a03f52011693`.

### Exact `P/M` limitation

The eligible deep summaries explicitly persist passive material `M`. They do **not** persist the charter's scalar
phenotype continuity `P(tau) = exp(-RMS(Phi_t-Phi_t+tau))` at the exact deep checkpoint. In
`turnover.traj[*].per[*]`, the field named `P` is a raw descriptor mapping (`size`, `mass`, `rg`, `uptake`,
`mean_sig`, `janus`, `radial_u`, `interface`, `mean_c`), not scalar continuity `P(tau)`. Moreover, the deep instant
can fall between the ten-step trajectory records, and the deep object stores `M`, centroids, and a different feature
vector rather than scalar `P`. Therefore the required explicit joint `(P,M)` record is absent: `M` exists; scalar
`P` does not. No retrospective `P` was computed in this audit.

## Protocol deviation: accidental display of outcome-bearing fields

One read-only command used `Get-Content -TotalCount` on minified one-line JSON:

```powershell
Get-Content experiments/individuation/turnover_dev_raw.json -TotalCount 80
Get-Content experiments/individuation/turnover_dev_diagnostics_raw.json -TotalCount 40
```

Because each JSON file is minified onto a single long line, the command displayed portions of pre-existing
outcome-bearing single-target records, including branch-behaviour fields in `rest_beh` and diagnostic outcome fields
in `turnover_dev_diagnostics_raw.json`. This was outside the intended mechanical-key projection and is recorded as a
protocol deviation. No exposed numerical outcome was copied into this journal, analyzed, contrasted, selected on,
or used in any eligibility or scientific judgment.

Specifically, this audit did **not** compute or inspect any new future response, did not compute or inspect the
directed-pair Phase-0.5 `Y/C/I` (none exists), did not rank or select a pair/world from an outcome, did not open any
prospective raw record or any `58xxx` record, did not run an engine/writer/probe, and did not modify 03G/V5. All
reported eligibility facts come solely from the mechanical/checkpoint keys enumerated above. After recognizing the
deviation, no outcome-bearing raw was reopened. Any outcome-sensitive inference by this auditor is disclaimed.

## INFERRED

The existing evidence supports exactly four candidate **coordinates in deterministic DEV reconstruction space**,
but zero admissible exact checkpoints under the user's contract. Reconstructing and serializing them now would
create new history-bearing executions rather than begin from already-serialized bytes, and is therefore outside
scope. The two digest conflicts additionally prevent pretending that a unique exact state is already fixed for
50002 and 50004.

Endpoint separation plus an empty censor summary is weaker than the requested continuous geometry, fusion/tracker
independence, and complete association evidence. Missing scalar `P` means the required joint `P/M` audit cannot be
claimed even for the four observational candidates.

## HYPOTHESIS

If independently preserved, hash-bound serialized payloads corresponding to the four deep candidates exist outside
the searched workspace, at least 50005 and 50007 may be recoverable without replay because their accepted state
digests agree across two records. This is a recovery hypothesis only, not evidence that the payloads exist or that
their continuous mechanical gates pass.

## WHAT WOULD FALSIFY THIS?

- Finding no byte payload matching the agreeing digest for 50005 or 50007 would falsify recoverability.
- Finding an exact payload does not by itself admit a checkpoint: a bound tracker/geometry record with continuous
  separation, halo, fusion, assignment alternatives, individual gates, and explicit joint scalar `P/M` must also
  validate.
- For 50002/50004, a provenance-bound explanation plus exact payload identifying one authoritative digest would be
  required before either can be considered uniquely fixed.

## Failures and dead ends

- PowerShell's case-insensitive `ConvertFrom-Json` rejected the qualification JSON because it contains both `C` and
  `c` keys. A standard-library JSON key projection was used instead.
- A broad minified-JSON display exposed outcome-bearing fields; this is documented above and those fields were not
  used.
- In-memory zero-error serialization tests do not supply a persisted serialized checkpoint.
- The optional `ASNS_CACHE` path is not provenance-bound and no cache artifact is available for audit.

## Decisions

- Do not salvage two remaining tracks from any world whose frozen three-target tracker gate failed.
- Do not use endpoint separation as a substitute for continuous pair geometry.
- Do not treat a content digest or deterministic reconstruction recipe as a serialized checkpoint.
- Do not compute missing scalar `P` retrospectively.
- Checkpoint-side disposition: **NOT ADMISSIBLE / REVISE BEFORE ANY DEV FACTORIAL**. This does not decide whether a
  local-cut operator exists; it says the present repository provides zero exact checkpoints that the proposed
  factorial may legally start from.

## Unresolved risks

- The source of the 50002/50004 digest divergence is unknown.
- An unindexed external cache could exist, but absence from the searched workspace and lack of a bound hash means it
  is not auditable evidence.
- The existing turnover trajectory cadence cannot prove continuous pair separation or zero halo overlap.
- Tracker summaries omit accepted/rejected association edges and individual gate terms.
- Scalar continuity `P` is absent at the exact deep instant.
- This auditor's accidental exposure to pre-existing outcome fields forbids any outcome-sensitive interpretation;
  the checkpoint disposition is mechanical only.

## Handoff

Return to the primary integrator:

1. report four observational candidates but **zero exact serialized checkpoint admissions**;
2. report the exact two-world digest conflict as unexplained, with `ASNS_CACHE` only a possible unbound cause;
3. fail closed on continuous geometry, complete tracker evidence, and explicit joint scalar `P/M`;
4. do not execute or reconstruct a DEV factorial under this mission;
5. keep the separate candidate-operator audit independent of the accidentally displayed outcomes.

Exact next authorized action within Phase 0: incorporate this fail-closed checkpoint inventory into the design
judgment. Any future attempt to locate external checkpoint bytes must be read-only and must verify their payload
hashes before opening an engine; recreating them with the history writer is not authorized by this mission.
