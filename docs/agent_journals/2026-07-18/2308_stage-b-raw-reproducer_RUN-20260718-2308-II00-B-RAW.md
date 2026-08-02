# Stage-B independent raw-only reproducer journal

- Role: independent Stage-B raw-only reproducer
- Run ID: `RUN-20260718-2308-II00-B-RAW`
- Start time: `2026-07-18 23:08:01 +02:00`
- End time: `2026-07-18 23:08:58 +02:00` (preregistration turn complete; reproduction not started)
- Starting Git branch: `codex/interventional-individuality-00-stage-b`
- Starting Git state: no short-status entries observed at journal creation
- Assigned scope: preregister an independent raw-only reproduction contract before any Stage-B DEV output exists; do not implement or inspect/init a world until the committed B1 manifest and raw schema are sealed and supplied.

## Immutable source firewall

Before raw reproduction begins, the reproducer may read only:

1. the exact committed B1 manifest named by the parent agent;
2. the exact committed raw schema named by that manifest; and
3. every raw world shard enrolled by that manifest, plus the manifest-declared hash inventory needed to verify them.

The reproducer must not read or import:

- `engine.py`;
- `instrumentation.py`;
- `stage_b.py` or any production/online runner;
- online classification code or generated online classifications;
- the Stage-B report or atlas;
- any candidate, picked-world, shortlist, representative-world, or visualization list;
- historical checkpoints, scientific result files, prior DEV worlds, seeds, or source worlds;
- any file outside the committed B1 manifest/schema/raw-shard allowlist except this journal and the reproducer implementation/output paths explicitly added to the allowlist before execution.

This firewall is semantic as well as path-based: copied extracts, cached values, summaries, screenshots, logs, comments, or messages conveying forbidden online outcomes are also forbidden. The parent may provide only the sealed commit identifiers and exact allowed paths/hashes, not scientific signs or candidate hints.

## Frozen independent algorithm obligations

The reproducer will be implemented independently from the raw schema and mathematical definitions frozen in the B1 manifest. It will not copy, import, dynamically call, or translate the production classifier implementation.

It must:

1. reject any manifest or schema whose committed bytes or declared hashes do not match the supplied seal;
2. enumerate the complete enrolled world set from the manifest, never from directory discovery or a selected list;
3. verify that every enrolled shard exists exactly once, has the declared byte hash, carries the declared world identity and neutral initial-condition class, and contains the complete declared frame/horizon coverage;
4. reject duplicate, missing, extra, truncated, non-finite, malformed, out-of-order, or schema-incompatible raw records;
5. derive per-track and per-world quantities only from raw numerical records using the frozen thresholds, chronology, boundary conventions, tolerances, and precedence encoded in the committed B1 manifest/schema;
6. reproduce all nine regime classes literally and exhaustively: the class identifiers, precedence, gates, and tie handling will be read from the sealed manifest and may not be renamed, merged, split, reordered, or inferred from online output;
7. assign exactly one of the nine classes to each enrolled world or fail closed;
8. reproduce complete region aggregation from the manifest-declared law-family coordinates and region bins, including counts for all nine classes, denominators, neutral-initial-condition strata, and any manifest-required marginal totals; no post hoc binning, smoothing, dropping, or empty-bin suppression is permitted;
9. preserve exact non-candidate and failed-world records and never select surviving subsets;
10. emit a machine-readable reproduction result containing input hashes, complete world-level classifications, complete region aggregates, invariant-check results, and deterministic serialization metadata.

No intervention, cut, conductance response, memory test, reproduction test, parameter adaptation, threshold relaxation, or scientific-world initialization is permitted in this task.

## Determinism and two-run byte identity

After implementation, the independent reproducer must be executed twice from the same sealed inputs in fresh output locations/processes. Canonical machine-readable outputs must be byte-identical. Ordering, numeric formatting, newline convention, and serialization must be explicitly fixed before the first run. The two output SHA-256 hashes and byte counts must be recorded here. A mismatch is binding and cannot be resolved by choosing one run.

## Preregistered kill switches

Stop reproduction and return a failed independent-qualification disposition to the parent if any of the following occurs:

- the committed B1 manifest or raw schema was not sealed before the first DEV world was initialized;
- any allowed input hash differs from its committed/declarative hash;
- the parent cannot provide an exact finite allowlist of manifest, schema, raw shards, reproducer paths, and output paths;
- any forbidden file or forbidden outcome-bearing information is opened, imported, received, or cached;
- the reproducer requires production engine, instrumentation, runner, classifier, report, atlas, or picked-world logic to compute a result;
- enrolled-world enumeration depends on filesystem discovery, online success, a shortlist, a visualization, or survival filtering;
- an enrolled raw shard is missing, extra, duplicated, truncated, malformed, non-finite, out of order, hash-mismatched, or inconsistent with declared identity/IC/horizon metadata;
- the raw schema is insufficient to reconstruct any mandatory gate, one of the exact nine regime classes, or the complete declared region aggregation without assumptions;
- a threshold, precedence rule, tolerance, coordinate, region boundary, empty-bin rule, or class identifier is ambiguous after sealing;
- the independent algorithm cannot assign exactly one frozen class to every enrolled world;
- any result requires post hoc threshold changes, fixture tuning, parameter-region changes, subset selection, or preferred-sign reasoning;
- raw-derived conservation, boundary-work, tracker, chronology, or accounting identities required by the manifest fail;
- the two fresh executions are not byte-identical;
- the independent world-level or region-level result disagrees with the sealed production result when comparison is finally authorized, with neither implementation privileged to resolve the discrepancy.

No disagreement or kill switch authorizes inspecting scientific outcomes to repair the method, replacing failed worlds, expanding the family, or continuing to a later scientific stage.

## Actions and evidence so far

- OBSERVED: this journal was preregistered before the reproducer received a B1 manifest, raw schema, or any DEV output.
- OBSERVED: only repository identity/status and wall-clock time were queried before this journal was written.
- INFERRED: no raw reproduction can begin until the parent supplies a committed seal and exact allowlist.
- HYPOTHESIS: the sealed raw schema will be sufficient for a genuinely independent reconstruction of every gate and all nine classes.
- WHAT WOULD FALSIFY THIS?: any mandatory derived quantity, class decision, or region aggregate requiring forbidden implementation knowledge or an unstated convention.
- Failures/dead ends: none yet.
- Decisions: fail closed on incomplete enrollment, insufficient raw observability, ambiguity, firewall breach, nondeterminism, or disagreement.
- Unresolved risks: the B1 manifest/schema and permitted reproducer paths do not yet exist in the information available to this role.

## Files read or changed

- Read: no scientific source, manifest, schema, result, raw shard, report, or atlas.
- Changed: this journal only.

## Reproducible commands executed

```powershell
$pwd.Path
git branch --show-current
git rev-parse --show-toplevel
git status --short
Get-Date -Format 'yyyy-MM-dd HH:mm:ss K'
Get-Date -Format 'HHmm'
```

## Handoff

Await the exact committed B1 manifest/schema seal and a finite source allowlist. Until then, do not implement the reproducer, inspect any raw output, or initialize any world.

- Ending Git branch: `codex/interventional-individuality-00-stage-b`
- Ending Git state for assigned scope: this journal is the sole new file created by this role; parent-owned concurrent changes were not inspected.

## Protocol clarification before implementation

At parent instruction after pre-output contract commit `1e11a1b`, exactly two additional pre-output design sources are admitted:

1. `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B1_RAW_SCHEMA.json`
2. `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B1_REPRODUCTION_SPEC.json`

Only the bytes of those two paths at commit `1e11a1b` may be read during independent implementation. This is a protocol clarification, not outcome access. The B1 manifest remains forbidden until the parent separately authorizes post-seal execution. Production `engine.py`, `instrumentation.py`, `stage_b.py`, tests, reports, results, classification, atlas, and picked-world information remain forbidden. Implementation before that later authorization is limited to this journal and `edlab/substrates/lattice_bond/stage_b_reproduce.py`; no DEV world may be initialized or read.

## Independent implementation turn

- Time: `2026-07-18 23:08:58 +02:00` to `2026-07-18 23:43:38 +02:00`
- Contract commit: `1e11a1b`
- Raw-schema SHA-256: `ffa9be82bd4c3285e75e1ac46b63a0a794598e2169afcb6a2890c3834749fe01`
- Reproduction-spec SHA-256: `a0c52688e7a2e1a07b8138b1c51507199145d212940b49af5a8655969c23de70`
- New independent source: `edlab/substrates/lattice_bond/stage_b_reproduce.py`
- Independent source SHA-256 before external static review: `504b0046defe75271d45b186fe6d725b5dea789ee6ee4e19dd5600067354f2fd`

### Implemented obligations

- Standalone imports restricted to Python standard library plus NumPy; no project import exists.
- Externally supplied sealed-manifest SHA-256 is mandatory.
- Raw-contract hashes are embedded and must match manifest bindings.
- Result paths are containment-checked; symlink and traversal inputs fail closed.
- Runtime forbidden basenames and selected-world/report/atlas paths fail closed.
- Enrolled worlds are enumerated only from the sealed manifest and sorted by `world_id` for world output.
- Shard identity/status, physics file hash/bytes, ZIP membership, exact declared array inventory, shapes/dtypes, required arrays, replay/vector-reference indicators, matter balance, residuals, and cohort conservation are validated.
- Periodic matter-only detector, lift-based winding, geometry-only association, collapse-aware tracker, split/merge/unresolved/contact handling, passive cohort propagation, observations, metrics, frozen nine-class precedence, law/IC atlas, candidate-region rule, and final disposition precedence are independently implemented.
- Output uses canonical UTF-8 JSON with sorted keys, compact separators, no NaN, terminal LF, exclusive creation, file flush and fsync.
- Two-run execution remains deliberately unperformed until sealed manifest/raw inputs are separately authorized.

### Static and synthetic evidence

```text
AST imports: __future__, argparse, collections, dataclasses, hashlib, json,
math, numpy, os, pathlib, sys, typing, zipfile
compile: OK
CLI --help: OK
synthetic matter-only detector: OK
synthetic one-to-one periodic tracker: OK
empty-world classifier precedence: OK
canonical serialization repeat identity: OK
git diff --check on assigned files: OK
```

The synthetic checks used only hand-built in-memory arrays. No manifest, shard manifest, physics file, result, scientific state, or world was opened or initialized.

### Current observations and risks

- OBSERVED: the implementation was derived only from the two admitted pre-output contracts.
- OBSERVED: static parsing confirms the source imports no `edlab` or other project module.
- INFERRED: exact byte equality with production classification may still depend on an output object schema supplied by the sealed B1 manifest; the reproduction contract defines canonical encoding and content obligations but does not enumerate every production output key.
- WHAT WOULD FALSIFY THIS?: the sealed manifest lacks an exact classification-output schema or uses raw-array/shard-manifest structures not completely specified by the two admitted contracts. Either condition must fail closed rather than be repaired using production output.
- UNRESOLVED: independent pre-output static audit requested from the Stage-B adversarial reviewer; findings pending.

### Binding adversarial finding before qualification

The Stage-B adversarial reviewer reported that the current standalone source cannot consume the actual producer-side contract: the two admitted reproduction documents do not specify the producer's nested manifest and shard structures, law-specific `dt` selection, or the exact production classification object schema. The reviewer transmitted examples of producer field names, but those arose from production knowledge outside this role's two-file pre-output source allowlist. They are recorded only as evidence of a schema mismatch and are not used to patch the implementation.

Disposition for this implementation turn: **hold / not statically qualified**. The source is preliminary despite compiling and passing hand-built smoke checks. Resolution requires either:

1. a newly committed, outcome-free reproduction contract that completely and normatively specifies the manifest structure, shard identity/inventory structure, per-law time-step selection, and exact classification output schema, followed by explicit authorization to read that contract; or
2. a fail-closed instrumentation/protocol revision.

Patching from production source, tests, generated output, reviewer-reported field fragments, or trial-and-error fixture failures remains forbidden. No manifest or DEV output was opened.

## Normative v2 amendment authorization

Parent authorization admits exactly one new outcome-free design source: `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B1_REPRODUCTION_SPEC.json` at commit `22ee3f7`. Its exact committed bytes and SHA-256 may be reread and used to repair the held reproducer. The raw schema remains the previously authorized version at commit `1e11a1b` with SHA-256 `ffa9be82bd4c3285e75e1ac46b63a0a794598e2169afcb6a2890c3834749fe01` and will not be reread. Production source, tests, manifests, results, reports, online classifications, atlases, and selected-world information remain forbidden.

### v2 repair and static evidence

- v2 contract SHA-256: `1255630ada7c3e85342a814eaa4d98ba989e625f45ac6ebb0698dfd7a26330ca`
- Repair interval through: `2026-07-19 00:02:35 +02:00`
- Provisional source SHA-256: `1f1c787505a7020ad05f032bdd663e8d3e893b06be5af44c399a4d4607d3d906`

Repairs derived from the v2 contract and pre-output adversarial findings:

- exact nested manifest, source-hash, law/IC/execution, seven-threshold and deterministic enrollment layout;
- external full-manifest hash plus internal excluding-field seal and strict finite canonical JSON;
- per-world nested law `spec.dt` and physical bounds;
- exact nested shard identity, physics inventory and terminal-failure behavior;
- complete root/shard name inventory without opening forbidden online/root-classification files;
- exact physics keyset/layout/dtypes, neutral scale/missing/controller gates and raw-scale reference criterion;
- LIFO weighted periodic detector operations, geometry-only tracking, law-specific time step, exact passive-cohort domain/conservation/no-clipping behavior and stop at final track point;
- exact seven-gate candidate logic including zero percolated fraction;
- exact production classification top-level/world/atlas/candidate-region schema with no audit metadata;
- law-local candidate-region completeness and global disposition precedence.

Hand-built, non-world checks passed:

```text
weighted row-wrap detector centroid/radius/winding exact values: PASS
one-to-one, split, merge, collapse and geometric-tie tracking branches: PASS
cohort tolerance, identity rejection and no-clipping behavior: PASS
all nine classifier precedence branches: PASS
v2 nested canonical manifest, internal seal, external hash and class-order preservation: PASS
strict canonical/non-finite JSON rejection: PASS
array inventory equality/rejection: PASS
exact classification object, nested atlas and law-local candidate region: PASS
failed-shard family behavior without reading failure content: PASS
AST standalone import allowlist, compile and diff check: PASS
```

One attempted inline inventory check failed because PowerShell quoting corrupted the Python command; it did not execute the intended assertion or alter any file. The same check was immediately rerun via an in-memory here-string and passed.

### Remaining normative hold after v2

Static and exhaustive hand-built adversarial comparisons identified details not stated exactly enough in v2 to qualify an independent byte reproduction:

1. detector lift traversal must normatively bind LIFO, neighbour order and push-time lift assignment;
2. law physical-bound field names must be explicit;
3. reference raw-scale array membership and aggregation order must be explicit;
4. failed-shard exact/optional inventory rules must be explicit;
5. `per_ic.complete` must be normatively typed and defined;
6. candidate IDs must specify clearing under higher-precedence non-candidate regimes;
7. merge ancestry ordering must be explicit;
8. divergence grouping must explicitly bind `(axis0 difference) + (axis1 difference)`.

The held source has not been qualified and no manifest/result/world has been read. Await another outcome-free normative amendment rather than importing production behavior through inspection.

## Normative v3 authorization

Parent authorization admits exactly `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B1_REPRODUCTION_SPEC.json` at commit `7a95934`, SHA-256 `f47a8d7febf9b9e4abe10281e04005ba4d565f825527a8cfb61d277bafa409a1`. It may be reread and used to resolve the eight held exactness gaps. No other source authorization changes; production source/tests/manifests/results and all outcome-bearing files remain forbidden.

### v3 final static qualification

- Completion time: `2026-07-19 00:08:39 +02:00`
- Final source SHA-256: `0fc99f9c1dc9b4356db65652ad9581140dd63deaf8b1ed98b6d0a6640ff0e3a5`
- Disposition: `STATIC_REPRODUCER_QUALIFIED`

The v3 source closes every held normative issue:

- exact v3 contract hash and schema binding;
- exact unseen-set/LIFO/push-time detector traversal and NumPy weighting order;
- nested law spec with per-world `dt`, `m_max`, and `n_max`;
- reference raw scale over exactly state `m/n/b` and raw-schema ledger fields in layout order;
- independently sorted source track IDs;
- explicitly grouped axis divergences;
- world-precedence candidate-ID clearing;
- boolean per-IC completion;
- failure inventory with required `failure.json`, optional preserved physics/online entries, declared-vs-actual closure, bytes, and permitted physics hashing without reading forbidden failure/online content.

Local static/hand-built checks all passed: v3 canonical manifest/seals, weighted periodic detector, split/merge/collapse/tie tracking, cohort tolerance and no clipping, all nine classifier branches, exact output/atlas with boolean completion and candidate clearing, failed shards with and without preserved files, malformed/non-finite JSON, array inventory, standalone import allowlist, compilation, CLI and diff checks.

Independent adversarial parity evidence at the final source hash:

```text
69,630 weighted periodic detector supports: exact
8,192 three-frame tracker trajectories: exact track IDs, points, parents and unresolved state
2,304 actual-engine synthetic cohort advances: array-exact
32 multi-step full synthetic measurement trajectories across two dt values: exact observations, regime and candidate IDs
128 synthetic family classifications: exact dictionary, atlas and disposition
static compile and diff checks: pass
```

Reviewer verdict: `PASS_INDEPENDENT_SOURCE_FOR_DURABLE_TESTS`. This is static source qualification only. It does not authorize reading the future sealed manifest, opening DEV raw shards, running the reproducer on a scientific family, or comparing outcomes. Those remain gated by a separately committed manifest and parent authorization.

No production source/test, Stage-B manifest, result, online output, scientific state, or DEV world was opened in this role.

### Final pre-seal executable self-integrity gate

At explicit pre-seal instruction, `load_manifest` now requires the exact manifest source entry `source_sha256["edlab/substrates/lattice_bond/stage_b_reproduce.py"]` and compares it to SHA-256 of `Path(__file__).resolve()`. A hand-built canonical manifest carrying the current source hash was accepted; an otherwise identical manifest carrying a false source hash was rejected with the intended binding error. Compilation remained clean.

- Provisional source SHA-256 after self-integrity patch: `8a7a4b1133c715fca596fb0bd04d7ab24f3182b6edaaa5a2c6d28dc3428f255f`
- No Stage-B manifest or result was opened.

Red-team also identified that NumPy reduction and byte reproducibility require exact runtime-environment equality. The authorized v3 contract does not define `manifest.environment` or its key names. This second gate is held pending a committed outcome-free v4 contract and explicit parent authorization; it will not be reconstructed from producer/reviewer knowledge.

## Normative v4 authorization

Parent authorization admits exactly `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B1_REPRODUCTION_SPEC.json` at commit `f29a6a54`, SHA-256 `9031a954881aba12dddf081e57850af9c1df92eded5a177b731b245246c6c7c2`. It may be reread to bind the exact manifest environment object while retaining executable self-hash verification. No manifest, result, production source/test, or other file is newly authorized.

The supplied abbreviated commit token did not resolve locally. Read-only Git identity showed the intended current contract commit is `f29a6a5ef57e416d60439b1ba19d8b17099907e5`; red-team then explicitly confirmed that full identifier. The v4 contract was read only from that exact object.

### v4 pre-shard integrity qualification

- Completion time: `2026-07-19 00:16:46 +02:00`
- v4 contract SHA-256 bound in source: `9031a954881aba12dddf081e57850af9c1df92eded5a177b731b245246c6c7c2`
- Final source SHA-256: `c058e96697347f8af613159cdcb58de5ee3e254d201c237961f366cc1fd08b58`
- Static disposition remains: `STATIC_REPRODUCER_QUALIFIED`

`load_manifest` now rejects before any shard access unless:

1. the manifest binds the exact SHA-256 of the executing `stage_b_reproduce.py` bytes; and
2. `manifest.environment` has exactly the four keys `python_version`, `numpy_version`, `platform`, and `byteorder`, with exact values equal to `sys.version`, `np.__version__`, `platform.platform()`, and `sys.byteorder`.

Hand-built finite canonical manifests proved the positive path and separate source-hash/environment mismatch rejection paths. Static compilation, standard-library-plus-NumPy import audit, CLI parsing, and assigned-file diff checks remained clean. No Stage-B manifest, result, shard, world, or forbidden outcome-bearing file was opened.

## Post-run raw-only audit authorization

Post-run authorization admits exactly:

- manifest: `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B1_MANIFEST.json`, expected SHA-256 `194e082f9d3809f2531912d825480fad5b683dbe9d9fceec8050260fe493dd50`;
- external digest: `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B1_MANIFEST.sha256`;
- RUN1: `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B1_RAW_REPRODUCTION_RUN1.json`;
- RUN2: `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B1_RAW_REPRODUCTION_RUN2.json`;
- result root: `results/INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-DEV`;
- every manifest-enrolled `{world_id}/shard_manifest.json`, restricted to identity, status, declared file inventory, row counts, and physics integrity metadata;
- every enrolled permitted `physics.npz` required by the raw audit.

Still forbidden: result-root `enrollment.json`, `classification.json`, `root_manifest.json`, every `online.json` and `failure.json`, any docs classification/report/atlas, production sources/tests, and selected-world information. A fresh recomputation may be performed in memory only; no third output file may be written. Only this journal may be changed during the audit.

### Post-run raw-only audit result

- Completion time: `2026-07-19 00:39:08 +02:00`
- Audit result: **PASS**
- Final disposition independently reproduced: `DEV_FEASIBILITY_FAIL`
- Blockers: none

Integrity and determinism:

| Item | Result |
|---|---:|
| Manifest SHA-256 | `194e082f9d3809f2531912d825480fad5b683dbe9d9fceec8050260fe493dd50` |
| External digest text | exact same 64-hex digest |
| Executing reproducer SHA-256 | `c058e96697347f8af613159cdcb58de5ee3e254d201c237961f366cc1fd08b58` |
| RUN1 SHA-256 | `7b7cf200fd6cc7ccfbd77b19de0ca1231df22c1d2d9ab5d7548828df7c3ed14e` |
| RUN2 SHA-256 | `7b7cf200fd6cc7ccfbd77b19de0ca1231df22c1d2d9ab5d7548828df7c3ed14e` |
| Fresh in-memory canonical bytes SHA-256 | `7b7cf200fd6cc7ccfbd77b19de0ca1231df22c1d2d9ab5d7548828df7c3ed14e` |
| Canonical output size | `15436` bytes |
| Enrolled shard manifests | `64` |
| Terminal COMPLETE shards | `64` |
| Unique declared/verified physics hashes | `64` |
| Shard-binding aggregate SHA-256 | `298f86ee06182ad180e3110bc09bbe34d5c95e31bc9b0aa7a7e0a3e7a9e71927` |

The shard-binding aggregate is SHA-256 of canonical JSON over the manifest-enrollment-order records `{world_id,status,shard_sha256,physics_sha256}`. Every shard manifest was strict finite canonical JSON. Every allowed `physics.npz` passed declared byte/hash/inventory, exact key/shape/dtype, environment/source seal, replay, vector-reference, state bounds, neutral scale/missing/controller, matter/energy residual, passive-cohort, detector/tracker, observation and classifier gates. No failed shard existed.

Complete independently reproduced regime counts across 64 worlds:

```json
{"BOUNDED_ACTIVE_TURNOVER_CANDIDATE":11,"DISSOLVED":10,"EMPTY_OR_GAS":2,"PERSISTENT_NO_TURNOVER":30,"STATIC_CRYSTAL_OR_SHELL":11}
```

All other frozen regimes had count zero: `TRACKING_UNRESOLVED`, `ACTIVE_UNBOUNDED`, `PERCOLATED`, and `TURNOVER_WITHOUT_PERSISTENCE`.

Exact law/IC atlas, omitting zero-count regimes:

| Law | Soup, n=4 | Compact, n=4 | Region qualified |
|---|---|---|---|
| `L000` | candidate 1; persistent-no-turnover 1; static 2 | dissolved 1; persistent-no-turnover 3 | false |
| `L001` | candidate 1; persistent-no-turnover 3 | persistent-no-turnover 4 | false |
| `L002` | persistent-no-turnover 3; static 1 | empty-or-gas 2; persistent-no-turnover 2 | false |
| `L003` | persistent-no-turnover 4 | persistent-no-turnover 4 | false |
| `L004` | candidate 1; dissolved 1; static 2 | dissolved 2; persistent-no-turnover 1; static 1 | false |
| `L005` | candidate 2; persistent-no-turnover 2 | candidate 1; dissolved 1; persistent-no-turnover 1; static 1 | false |
| `L006` | candidate 2; dissolved 1; static 1 | candidate 1; dissolved 2; persistent-no-turnover 1 | false |
| `L007` | candidate 2; static 2 | dissolved 2; persistent-no-turnover 1; static 1 | false |

`candidate_regions` independently reproduces as the empty list. All 16 law/IC strata are complete, but no law reaches the frozen candidate replication minimum separately in both IC classes. With no numerical/instrumentation-invalid shard and no qualified region, frozen disposition precedence yields `DEV_FEASIBILITY_FAIL`.

RUN1 and RUN2 were each strict finite canonical JSON, byte-identical to one another, and byte-identical to the fresh in-memory raw reconstruction. No third output was written.

Firewall attestation: the audit did not open result-root `enrollment.json`, `classification.json`, `root_manifest.json`, any `online.json` or `failure.json`, any docs classification/report/atlas, production source/test, or selected-world list. Only the exact allowed manifest/digest, RUN1/RUN2, 64 enrolled shard manifests, permitted physics arrays, executing independent source, and this journal were accessed.
