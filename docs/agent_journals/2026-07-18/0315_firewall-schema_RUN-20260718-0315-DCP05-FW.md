# Agent journal — DIRECTED-CAUSAL-PAIR-00 Phase 0.5 firewall and raw-schema audit

- Role: independent outcome-firewall, execution-integrity, and raw-schema auditor
- Run ID: `RUN-20260718-0315-DCP05-FW`
- Start time: 2026-07-18 03:15 CEST
- End time: 2026-07-18 03:26 CEST
- Starting Git state: clean branch `codex/directed-causal-pair-00-phase05` at
  `4bcb551092291b7383c4168f653818d4bade14f6`
- Ending Git state: HEAD unchanged at `4bcb551092291b7383c4168f653818d4bade14f6`; shared worktree contains this
  journal plus concurrent untracked work from the other Phase-0.5 agents; this unique journal is the only file
  written by this agent
- Worktree: `C:\Users\tommy\Documents\ising-v3-directed-causal-pair-00-phase0`
- Runtime lock: not applicable; this was a direct human-requested, read-only design audit, not a scheduled run

## Assigned scope

Independently threat-model Phase 0.5's outcome firewall, seed and manifest guards, prohibition on reading any
`58xxx` artefact, atomic ordered-prefix resume, and smallest sufficient mechanical raw schema. Inspect accepted
repository patterns and tests, but do not initialize or execute any world, enumerate or inspect any `58xxx`
result, compute any pair `Y`, `C`, or `I`, or edit any file other than this journal.

## Operating-contract and provenance audit

Read in the required order:

1. `AGENTS.md`;
2. `docs/RESEARCH_CHARTER.md`;
3. `docs/PROJECT_STATE.md`;
4. `docs/DECISION_LOG.md` in full;
5. `docs/EXPERIMENT_INDEX.md`;
6. `docs/RUN_INDEX.md`;
7. the latest journal,
   `docs/agent_journals/2026-07-18/0243_scientific-design_RUN-20260718-0243-DIRECTED-CAUSAL-PAIR-00-P0.md`;
8. the current Phase-0 report, machine summary, and draft schema:
   `DIRECTED_CAUSAL_PAIR_00_PHASE0_REPORT.md`,
   `DIRECTED_CAUSAL_PAIR_00_PHASE0_DEV_FEASIBILITY.json`, and
   `DIRECTED_CAUSAL_PAIR_00_RAW_SCHEMA_DRAFT.json`.

Also inspected, without executing, the Phase-0 audit and tests, the 03G runner, ledger, raw persistence/schema, and
focused end-to-end tests. The 03G chain is useful precedent for fail-before-engine validation, hash binding,
immutable raw records, explicit resume, and last-published manifests. It is not safe to copy mechanically for this
mission without the corrections below.

No result directory or prospective-family artefact was inspected. No engine, tracker, writer, clamp, or probe was
initialized. No `58xxx` filename or result set was enumerated.

## Important files read

- `experiments/individuation/directed_causal_pair_phase0_audit.py`
- `experiments/individuation/test_directed_causal_pair_phase0.py`
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_RAW_SCHEMA_DRAFT.json`
- `experiments/individuation/turnover_runner_03g.py`
- `experiments/individuation/turnover_ledger_03g.py`
- `experiments/individuation/turnover_raw_schema_03g.py`
- `experiments/individuation/test_turnover_end_to_end_03g.py`

## Reproducible audit commands

Read-only commands used:

```powershell
git branch --show-current
git rev-parse HEAD
git status --short --branch
rg --files experiments/individuation edlab docs/individuation
rg -n "seed|manifest|resume|prefix|atomic|raw|ledger|analyzer" `
  experiments/individuation/turnover_runner_03g.py `
  experiments/individuation/turnover_ledger_03g.py `
  experiments/individuation/turnover_raw_schema_03g.py
```

No experimental or synthetic execution command was run.

## OBSERVED

### Accepted strengths worth reusing

- The 03G verifier checks mode/family, exact file hashes and Git blobs, environment, seal, and authorization before
  dynamically importing its engine.
- 03G raw publication uses exclusive creation, a same-directory temporary file, flush/fsync, and atomic replace.
- Existing tests verify that invalid authorization creates no run directory or ledger and performs no engine import.
- Existing tests cover explicit resume, a second-fresh-start refusal, ledger tamper/truncation, raw-hash tamper,
  mixed schema, duplicate worlds, and a feasibility-only reserve projection.
- Phase 0 fixed exactly four eligible worlds and fixed each pair and sentinel before treatment.

### Load-bearing gaps in patterns that must not be inherited

1. **The accepted 03G ordered-seed API trusts its caller.**
   `record_seed_started(run_dir, seed, expected_seed)` checks equality between two caller arguments, while the runner
   calls `_run_one(run_dir, seed, seed, ...)`. The runner itself normally derives the next seed correctly, but the
   ledger does not independently establish that completed records form the exact prefix. A set of completed IDs can
   hide a hole or reordering. Phase 0.5 needs an internal immutable-plan check, not this caller assertion.

2. **Ledger append and anchor update are not one atomic transaction.** A crash after fsynced JSONL append and before
   the atomically replaced anchor leaves a valid new ledger line plus a stale anchor; verification correctly fails
   closed, but no ordinary resume path can distinguish and adopt that durable tail. For four DEV worlds this should
   be simplified to immutable, atomically published unit records as the authority, with the summary/progress file
   derived from their exact contiguous prefix.

3. **The Phase-0 audit accepts any subset of the open DEV namespace.** It converts raw IDs to a set and checks
   subset inclusion. That is suitable for its static audit but too weak for Phase 0.5. The qualification manifest
   must require the exact ordered list `[50002, 50004, 50005, 50007]`, reject duplicates, reject booleans and strings
   masquerading as integers, and bind the already-fixed A/B/sentinel assignments.

4. **The draft schema is not an outcome firewall.** It requires `integrated_tracked_uptake` and
   `integrated_fixed_mask_uptake`, permits a free-form `raw_descriptor`, and leaves several target-keyed objects open
   to additional properties. A mechanical executor using this schema could compute or smuggle the forbidden result
   while still validating.

5. **Hashes of masks are insufficient for the required engine-free reproduction.** The draft stores only body,
   core, and halo mask hashes. A standard-library reproducer cannot recompute overlaps, coverage, collar intrusion,
   adjacency/contact, or periodic geometry from hashes. Canonical mask content or an equally sufficient primitive
   representation must be persisted.

6. **A generic corrected-probe return value is dangerous here.** Reusing a function that accumulates uptake and
   merely discarding its returned result would still compute the forbidden endpoint. The schedule-only path must
   advance the unchanged physics while exposing only state hashes and mechanical viability/geometry to its logger.

7. **A commit ID alone does not bind a dirty execution.** The DEV manifest and every raw record must bind hashes of
   the actual scheduler, logger, writer adapter, probe-schedule adapter, tracker, no-swap operator, schema,
   reproducer, and fixed inputs. Git commit plus exact SHA-256/Git-blob bindings are both needed.

## Threat model and required controls

### F1 — accidental or indirect scientific analysis

Threat: a top-level analyzer import, helper import, returned probe payload, logging callback, exception, or free-form
JSON field computes or exposes `Y`, a directed `C`, an interaction `I`, a contrast, or a feeding outcome.

Required controls:

- Use a two-stage entry point. Stage 1 is standard-library-only and validates the entire manifest and read/write
  boundary. Only then may it dynamically import the mechanical executor.
- The mechanical runner must have no top-level import of any analyzer/statistics/outcome module. In particular, do
  not copy 03G's top-level `turnover_analyzer_03g` pattern.
- Add a recursive exact-key firewall before publication and again on load. Reject case-insensitively exact keys and
  prefixes such as `Y`, `Y_*`, `C`, `C_*`, `I`, `I_*`, `outcome*`, `feeding*`, `contrast*`, `effect*`,
  `estimand*`, `directed_matrix*`, and `analyzer*`. Use a schema whitelist as the primary defense; the denylist is
  defense in depth.
- The DEV schema must use `additionalProperties: false` at every object, including target maps and operation logs.
  No free-form descriptor or metadata dictionary is allowed.
- Create a probe-schedule-only adapter whose return type contains no uptake/feeding field. A test double should make
  any access to an outcome accumulator raise; the full mechanical run must still pass.
- Treat full-state hashes as opaque commitments. Do not serialize uptake arrays or values in DEV mechanical raw.
- Capture subprocess stdout/stderr in firewall tests and require it to contain only the declared mechanical status.

### F2 — unauthorized seed or namespace access

Threat: a broad `500xx` range, generic CLI `--seed`, environment override, input glob, path traversal, symlink or
junction, or prospective template allows an unauthorized world or artefact to be opened before rejection.

Required controls:

- Manifest mode is exactly `DEV_MECHANICAL`; the executable rejects every other mode, including the seedless
  prospective-template mode.
- The only executable world list is exactly `[50002, 50004, 50005, 50007]` in that order. It is repeated in the
  immutable plan hash and checked at the engine-constructor boundary.
- Pair assignments, sentinel, initial checkpoint hash, and Phase-0 selection-record hash are fixed per world. No
  pair selection function runs after any branch behavior exists.
- No CLI seed, range, input-root, or glob option exists. Inputs are an exact hash-bound allowlist.
- Resolve every allowed read and write path, then require it to remain under the exact repository or canonical run
  directory. Reject symlink/junction escapes and all unrecognized files.
- Validate schema, exact IDs, paths, hashes, code bindings, and empty/fresh-or-explicit-resume state before engine
  import, run-directory creation, or any world initialization.
- A runtime read guard should allow only the manifest's exact fixed input files after imports. No `glob`, `rglob`,
  `iterdir`, or directory-wide result scan may be required.
- Add a synthetic forbidden-namespace decoy whose open/read methods raise and prove the qualification never touches
  it. Also make any attempted enumeration outside the canonical output directory raise.

### F3 — non-atomic or order-dependent resume

Threat: a crash, orphan file, duplicate, hole, future unit, reordered unit, stale progress file, mismatched binding,
or changed execution order silently alters which clones are run or which raw records are accepted.

Required controls:

- Freeze one canonical ordered plan of unit IDs. A unit ID includes original world, history arm, access regime, and
  recipient where applicable. Hash the full list.
- Each canonical record contains `sequence_index`, `unit_id`, `plan_sha256`, `manifest_sha256`, all code/input
  bindings, and `previous_record_sha256`. The executor derives the expected next tuple internally from the plan.
- Atomically publish each record with canonical JSON (`sort_keys`, compact separators, `allow_nan=False`, one final
  newline), fsync, replace, and immediate read-back/hash verification. Never overwrite an existing canonical
  record.
- On resume, accept only records equal to the first `k` plan entries, with a valid predecessor chain and exact
  bindings. Reject holes, duplicates, future records, unknown files, wrong filenames, mismatched hashes, and
  non-canonical bytes.
- Make immutable unit records authoritative. A progress file is derived and may be regenerated. This avoids a
  two-file ledger/anchor commit gap. Publish the COMPLETE manifest last and only after all required records verify.
- An atomically complete next record left by a crash may be adopted only if it is exactly entry `k` and fully
  validates. A partial temporary file is never evidence; quarantine or reject it within the canonical run directory.
- Each arm starts from deserialized immutable checkpoint bytes, including RNG state where applicable. Never clone
  from another arm's mutated object. Derive any per-unit stream from the frozen unit ID with a stable cryptographic
  hash, never Python's salted `hash()` or directory order.
- Prove order independence on synthetic mechanics by executing units in a deliberately permuted harness and
  comparing each unit's state/mechanical record after removing storage sequence metadata. Production still uses the
  one fixed order.

### F4 — raw summaries that cannot be independently checked

Threat: the reproducer merely trusts booleans such as `halo_overlap=false`, `sham_exact=true`, or
`mechanically_complete=true`, or it imports the engine to recover missing primitives.

Required controls:

- Persist primitives sufficient to recompute every mechanical gate with standard-library code.
- Summaries are derived and checked against primitives; they are never the sole evidence.
- Run the reproducer in a temporary directory containing only the reproducer, schema, raw manifest, and records,
  with the repository/engine absent from `PYTHONPATH`.
- The reproduction output contains no timestamp, absolute path, hostname, random ordering, or environment-specific
  field. Two generations must be byte-identical and hash-identical.

## Smallest sufficient mechanical raw schema

The strongest firewall is two mode-specific payloads, not one permissive object:

1. `DIRECTED-CAUSAL-PAIR-00-MECHANICAL-DEV-v1`: executable in Phase 0.5 and structurally incapable of carrying a
   response.
2. A separately sealed future scientific extension that may carry primitive recipient-specific probe observations
   but never derived `Y`, `C`, or `I`. The Phase-0.5 executor must reject this mode and must not import its analyzer.

### Per-unit binding and identity

Required fields:

- schema, mission, `DEV_MECHANICAL` mode, sequence index, unit ID;
- phase-0 commit, code commit, manifest hash, plan hash, schema hash, previous-record hash;
- exact protected-file and input hashes;
- original world ID; immutable initial checkpoint and clone hashes; RNG-state hash if applicable;
- fixed A/B/sentinel target indices and pair-selection hash;
- exact history arm, access regime, recipient, and fixed execution-order digest.

### Writer, sham, clamp, and probe-schedule operations

Store compact explicit operation blocks, not an unsupported pass Boolean:

- frozen writer/schedule ID and hash;
- treatment bits for A and B;
- phase start/end steps, amplitude tuple, patch/mask hash, target label, `HISTORY` versus `SHAM`, and array-operation
  count/digest for both targets;
- common writer-loop and operation-order digests proving schedule length and numerical disturbance match;
- recipient/core/collar/reference-replay mask encodings and hashes;
- `up_ref=0` flag, own-replay source hash, intended-write mask, actual-write mask, and unintended-write count;
- corrected probe schedule constants and operation digest only: standardization action, settle length, pulse amplitude
  and duration, and mechanical horizon. No uptake accumulator or response values.

### Per-required-step mechanical evidence

For every frozen required step, persist:

- step and phase; opaque full-state and RNG hashes;
- A/B/sentinel labels, fixed target indices, tracker IDs, component IDs/status, periodic centroids, and component sizes;
- all association alternatives and individual overlap/distance/size gate terms, selected edge, and assignment cost;
- canonical packed bitsets or canonical run-length encodings for each target's body/component, radius-10 core,
  radius-12 halo, and active clamp collar. A 64x64 packed mask is only 512 bytes before encoding and is sufficient for
  a standard-library `int.bit_count()` reproducer;
- pair distance, core-overlap cells, halo-overlap cells, halo gap, and body/core coverage derived from those
  primitives;
- component-switch, fusion/contact, target/partner/sentinel eligibility, collar/partner and collar/wrong-core
  intersections, partner intrusion, nonfinite-state flag, and unintended-write count.

The distance-minus-24 continuous gap and discrete halo overlap are separate fields. At exact distance 24 the
distance gate can pass while inclusive discrete halos can still intersect; the overlap gate must independently
fail closed.

### Terminal record and complete block

- `mechanically_complete` is a Boolean, never a response value.
- `first_failure` is null or an enum plus exact step and evidence. Required reasons include distance below 24,
  halo/core overlap, contact/fusion, tracker switch, target/partner/sentinel invalidity, collar intersection,
  clone/sham/schedule mismatch, nonfinite state, forbidden field, hash/binding mismatch, and unexpected record.
- A world-level block enumerates every required unit ID and is `COMPLETE_VALID` only when the exact planned set is
  present and all mechanical gates pass. A failed or absent arm is recorded as incomplete/invalid with its reason;
  it is never encoded as zero.
- Store world-level minima and counts only as checked derivatives of the per-step primitives.

### Future scientific extension

To support later diagonal, crossed, pair-total, global, asymmetry, and interaction calculations without a generic
feature battery, the separately sealed prospective extension needs only:

- the same fixed world/pair/arm/regime/recipient bindings;
- primitive per-step recipient-labelled probe observations for A, B, and sentinel under the common schedule;
- the already-required body/mass/geometry mediator series and global/collar diagnostics;
- complete-block and censor status.

It must not store directed entries or contrasts. A later analyzer derives them by original world. DEV mechanical
raw must reject the entire extension, including its primitive response section.

## Required focused test matrix

### Manifest, namespace, and import firewall

1. Exact valid manifest reaches a fake mechanical executor; every malformed manifest below records zero engine
   imports, zero world initializations, zero run-directory creation, and zero output bytes.
2. Reject an out-of-range ID, an in-range but noneligible ID, missing eligible ID, duplicate, reorder, string ID,
   Boolean ID, extra reserve/seed-plan field, and any mode other than `DEV_MECHANICAL`.
3. Reject changed A/B/sentinel assignment, initial checkpoint, input hash, code hash, schema hash, plan hash, or
   canonical output path.
4. Reject path traversal and a symlink/junction escape for both reads and writes.
5. Static AST/import-closure test: no analyzer, statistics, outcome, reader, or decoder module is reachable from the
   mechanical entry point. Runtime test: none appears in `sys.modules` before or after execution.
6. Synthetic forbidden-namespace decoy and enumeration traps prove no read/open/stat/glob/list operation touches
   any non-allowlisted artefact.
7. Fake probe result whose outcome properties raise on access proves schedule viability does not inspect them.
8. Inject forbidden keys at every nesting depth and case; reject before publication. Confirm ordinary allowed keys
   containing the letters c, i, or y do not create false positives.
9. Seedless prospective manifest template is documentation-only and cannot execute.

### Atomic prefix and determinism

10. Resume accepts every valid prefix length from zero to complete and yields the same final bytes and hashes.
11. Reject a hole, duplicate, swapped records, future record, unknown file, wrong predecessor, wrong plan/binding,
    non-canonical JSON, and record-path mismatch.
12. Fault-inject before temp write, after fsync/before replace, after replace/before progress, and during final-manifest
    publication. Every restart either converges byte-identically or fails closed without overwrite.
13. Second fresh start is refused; explicit resume of COMPLETE is idempotent.
14. Existing exact next record is adopted; any mismatch is rejected and preserved for audit.
15. All prewriter clone hashes are identical within a world, and no mutable array or RNG object is shared across
    branches.
16. Permuted synthetic execution produces identical per-unit mechanics, proving storage order cannot change state.
17. Writer and sham operation counts, patch hashes, schedule lengths, and operation-order digests match exactly.

### Geometry, tracker, clamp, schema, and reproduction

18. Logged versus unlogged trajectories are bit-identical at every step, including RNG state.
19. Geometry calculations are independent of tracker IDs; relabeling diagnostic IDs changes labels only.
20. Periodic-distance and mask fixtures cover wraparound, exact 24, below 24, halo tangency/overlap, core overlap,
    crossing without label swap, component switch, contact, fusion, partner intrusion, and wrong-core collar contact.
21. NaN or infinity anywhere fails before JSON publication (`allow_nan=False` plus explicit full-state finite check).
22. Pair-context own-replay sham is full-state bit-exact for every history arm with the partner present.
23. Missing/duplicate arm or regime prevents complete-block status. A failed arm has a reason and no synthetic zero.
24. Schema rejects every extra property and malformed/variable-length mask encoding; exact arm and target cardinality
    is enforced.
25. Standard-library raw reproducer runs with engine/world imports trapped, recomputes all summaries from persisted
    primitives, rejects tampering, and emits byte-identical output twice.

## INFERRED

- The outcome firewall is strongest when scientific response data never enter the Phase-0.5 process, rather than
  when an analyzer is merely not called after response accumulation.
- The exact four-world list is an authorization boundary, not just a convenience. A broad `500xx` check permits
  mechanically different worlds and weakens outcome-independent selection.
- Hash-only geometry cannot meet the stated independent-reproduction requirement. Persisting compact masks is the
  minimum material increase that makes overlap/coverage/contact claims independently auditable.
- An immutable-record prefix is simpler and more crash-recoverable than a mutable ledger plus separately updated
  anchor for this bounded qualification.
- The eventual scientific schema can remain small and non-composite by storing recipient-labelled primitive probe
  series and deriving the directed matrix only later at world level.

## HYPOTHESIS

If the manifest is exact, the executor cannot import or access response analysis, every arm starts from one
immutable checkpoint, and all gates are reproducible from persisted primitives, then Phase 0.5 mechanical status is
independent of pair feeding behavior and safe to use solely as a precondition for a later human seal review.

## WHAT WOULD FALSIFY THIS?

- Any malformed or unauthorized manifest reaching engine import or run-directory creation.
- Any file access outside the exact allowlist, including a prospective/forbidden namespace artefact.
- Any DEV record containing a response, outcome, contrast, directed-entry, interaction, or analyzer field.
- Any probe-schedule qualification that reads or accumulates uptake even if it later discards the value.
- Any accepted resume state that is not the exact first `k` units of the frozen plan.
- Any arm whose output changes when independent unit execution order is permuted.
- Any claimed geometry/sham/clamp summary that the engine-free reproducer cannot recompute from raw primitives.
- Any summary or reproduction whose second generation is not byte-identical.

## Failures and dead ends

- One read-only `rg` command initially failed due to PowerShell quoting around a regular expression. It produced no
  repository change and was rerun with a single-quoted pattern.
- No package-provided JSON Schema validator was invoked because the assignment was a static audit and prohibited all
  edits except this journal. The schema recommendations are therefore a design result, not a validation claim.
- Copying the 03G ledger was rejected as the direct solution because its caller-supplied expected-seed check and
  append/anchor crash gap do not by themselves provide the exact atomic-prefix contract requested here.

## Decisions

1. Require a strict mechanical-only DEV schema and a separate future scientific extension.
2. Freeze the exact four eligible world IDs and pair assignments in an immutable ordered plan.
3. Make atomically published immutable unit records, not a completed-ID set, the authority for resume.
4. Require persisted mask primitives so raw-only reproduction recomputes rather than trusts geometry gates.
5. Treat even transient computation of uptake-derived pair outcomes during DEV as a firewall failure.

## Unresolved risks

- The final mechanical schedule's exact unit granularity (whole world versus arm/regime unit) must be chosen once and
  frozen before the DEV run. Per-arm/regime units improve restart cost, but whole-world complete-block rules still
  govern validity.
- The precise component-contact adjacency convention and inclusive halo-mask definition must be inherited from the
  accepted tracker/operator and written explicitly into both logger and reproducer; distance alone is not a proxy.
- Windows cannot generally guarantee portable directory-metadata fsync. Immediate read-back plus full prefix
  revalidation on resume is the durability boundary and must be stated rather than overclaimed.
- A full-state hash may commit to outcome-bearing internal arrays without revealing them; the package should state
  that this is an opaque mechanical provenance commitment, not an outcome measurement.

## Handoff

Before any Phase-0.5 DEV execution, implement and make focused tests pass for: exact four-world manifest validation
before engine import; allowlisted reads/no enumeration; strict nested outcome-key rejection; schedule-only probe
execution; immutable hash-chained prefix resume; canonical packed-mask mechanical raw; and an engine-free
byte-stable reproducer. Do not classify mechanics as qualified if any one of those contracts is absent.

Exact next action for the integrating agent: freeze the ordered mechanical unit plan and final mechanical-only raw
schema first, then write the preflight/firewall and resume tests against those frozen objects before running any of
the four DEV worlds.
