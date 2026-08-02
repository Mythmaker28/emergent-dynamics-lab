# FUTURE-LIFECYCLE-RUNNER-INTEGRATION-00 — report

## Part I — FROZEN PRE-IMPLEMENTATION CONTRACT

This part is frozen before any implementation code exists. It is committed alone, and the qualification
in Part II must cite and compare against this commit. Nothing in Part I may be silently revised; a
required deviation is a reason to return `RUNNER_INTEGRATION_INSUFFICIENT`, not to edit this section.

### 1. Authority and scope

- Human-review branch: `codex/future-lifecycle-contract-00-human-review`
- Human-review commit: `b2331d75153763c8efbfbcd401084a331584f259`
- Decision record: `docs/individuation/FUTURE_LIFECYCLE_CONTRACT_00_HUMAN_REVIEW.md`
- Disposition: `HUMAN_REVIEW_ACCEPTED`
- Accepted lifecycle parent: `4282fc6ead915639711f5096c7825d3880a640d4`
- This branch: `codex/future-lifecycle-runner-integration-00`, rooted at the human-review commit so
  that the integration physically contains its own authorization.

**Scope.** Engineering only. Build a *future-family* runner integration skeleton in which the qualified
lifecycle contract is an unavoidable part of the only supported completion path. No scientific
experiment, no engine execution, no historical Stage-B integration, no scientific outcome.

**Explicit non-scope.** This mission establishes nothing about individuality, ownership, persistence,
life, death, feasibility or any physical phenomenon. It does not interpret, revise, repair or supersede
`STOP-LOCAL-CUT`, `STOP-OWNERSHIP-IDENTIFIABILITY`, `FINAL_STOP_ARCHITECTURE_CONFIRMED`,
`DEV_FEASIBILITY_FAIL`, `AUDIT_INVALID`, `FUTURE_LIFECYCLE_CONTRACT_QUALIFIED`, or the Kovacs
`SCALAR_ONLY_FEASIBLE → STOP_PROSPECTIVE`.

### 2. Supported public API (frozen)

Module: `edlab.substrates.lattice_bond.future_lifecycle_runner`.
`__all__` is frozen to exactly the following names. Anything not listed here is private and unsupported.

**Two entry points, and only two:**

```
publish_future_family_completion(run_directory, tracking, sampled_frames) -> CompletionRecord
open_analysis_access(run_directory, tracking, sampled_frames)             -> AnalysisAccess
```

**Supporting names:** `SCHEMA_VERSION`, `INTEGRATION_VERSION`, `LIFECYCLE_DOCUMENT_NAME`,
`COMPLETION_MANIFEST_NAME`, `RunnerState`, `CompletionRecord`, `AnalysisAccess`,
`RunnerIntegrationError`, `LifecycleEvidenceError`, `CompletionPublicationError`,
`CompletionEvidenceError`.

**Frozen prohibitions on the API surface.** There is no `emit_complete`, no `mark_complete`, no
`force_*`, no `skip_*`, no `unsafe_*`, no override flag, no `lifecycle_ok` parameter, no public
serializer for the completion manifest, and no public constructor path for `AnalysisAccess`.
**No public function accepts a `LifecycleRunClosure`, a `LifecycleTerminalRecord`, a lifecycle
document, a disposition string or any status enum as a parameter.** The only admitted evidence of
lifecycle qualification is a document the integration itself wrote and then re-read from disk.

`CompletionRecord` is an inert value object describing what was published. It is **not** a capability:
holding one grants no analysis access. `AnalysisAccess` is the capability, and it can only be obtained
from `open_analysis_access`, which re-derives it from disk every time.

### 3. State machine (frozen)

```
UNSTARTED -> LIFECYCLE_PERSISTED -> LIFECYCLE_VERIFIED -> COMPLETE_PUBLISHED
```

Transitions are monotonic and internal. There is no public setter, and no state may be reached if an
earlier transition failed. `COMPLETE_PUBLISHED` is unreachable before lifecycle persistence **and**
read-back verification have both succeeded.

Ordered obligations of `publish_future_family_completion`:

1. accept a structurally valid synthetic `TrackingResult` and a declared ordered sample schedule;
2. refuse if either output target already exists (no overwrite, ever);
3. invoke `qualify_and_write_lifecycle_contract` — qualification and canonical persistence in one
   qualified primitive → `LIFECYCLE_PERSISTED`;
4. read the exact persisted bytes back from disk;
5. call `verify_lifecycle_document` against the **original** tracking inputs and schedule, and
   additionally assert that the persisted bytes equal the canonical bytes of the reverified object
   → `LIFECYCLE_VERIFIED`;
6. compute the lifecycle-document digest over the **bytes read back from disk**, never over the
   in-memory object returned by step 3;
7. atomically publish a canonical completion manifest, non-overwriting → `COMPLETE_PUBLISHED`;
8. return an inert `CompletionRecord`.

`open_analysis_access` must independently repeat the disk verification on every call: read the
completion manifest, reject non-canonical bytes, read the lifecycle document named by the manifest,
check its digest against the manifest, re-run `verify_lifecycle_document` against the supplied tracking
inputs and schedule, cross-check every manifest binding against the reverified object, and only then
issue the capability.

### 4. Threat model and non-bypassability definition (frozen)

**Claimed.** Within the committed supported public API of this module, and given immutable on-disk
evidence, there is no code path that publishes `COMPLETE` or returns an `AnalysisAccess` without the
qualified lifecycle contract having been executed from the supplied tracking inputs, canonically
persisted, read back, and independently reverified.

**Defended against:** callers using the public API in any order; callers fabricating
`LifecycleRunClosure` / `LifecycleTerminalRecord` objects; callers hand-writing a lifecycle document
containing a nominal `"disposition": "QUALIFIED"`; callers hand-writing or editing a completion
manifest; tampered, truncated, non-canonical or digest-mismatched on-disk evidence; a lifecycle
document present without a completion manifest; swapped tracking inputs or a changed sample schedule at
analysis time; publication races and pre-existing targets.

**Explicitly NOT claimed.** This is Python. The claim does **not** extend to an actor who edits this
module or `lifecycle.py`, monkeypatches module attributes, uses reflection or private names, replaces
the import, or controls both the written bytes and the verifying code. No absolute protection is
asserted. The claim is scoped to the committed supported API plus immutable on-disk evidence, and to
nothing else.

### 5. Permitted input types (frozen)

`tracking` must be a `TrackingResult` from `edlab.substrates.lattice_bond.instrumentation`, built by
synthetic fixtures only. `sampled_frames` must be an ordered, strictly increasing sequence of
nonnegative integers. `run_directory` must be an existing directory. No historical, engine-produced,
world-derived or seed-derived input is admitted anywhere in this mission.

### 6. Completion manifest schema (frozen)

Canonical JSON: UTF-8, sorted keys, compact separators, `ensure_ascii`, `allow_nan=False`.
Exactly these keys, no others:

| Key | Meaning |
|---|---|
| `schema_version` | `"future-lifecycle-runner-integration/v1"` |
| `integration_version` | implementation identifier of this module |
| `lifecycle_schema_version` | copied from the qualified lifecycle primitive |
| `lifecycle_validator_version` | copied from the qualified lifecycle primitive |
| `lifecycle_document_relative_path` | relative identity of the persisted lifecycle document |
| `lifecycle_document_sha256` | digest of the bytes **read back from disk** |
| `lifecycle_input_sha256` | lifecycle input binding from the reverified contract |
| `lifecycle_records_sha256` | terminal-record binding from the reverified contract |
| `sampled_frames` | declared schedule binding |
| `terminal_record_count` | count from the reverified contract |
| `disposition` | `"COMPLETE"` |
| `canonicalization` | explicit declaration of the byte canonicalization rules |

No scientific measurement, outcome, world name, seed, law or candidate may appear. The manifest stores
only a **relative** lifecycle identity, so identical inputs yield byte-identical manifests regardless of
directory.

The published JSON Schema of the lifecycle contract is **not** used as proof of validity anywhere.
Verification uses the qualified implementation only.

### 7. Failure semantics (frozen)

On any error: raise a typed `RunnerIntegrationError` subclass; do not publish `COMPLETE`; do not return
analysis access; never convert missing lifecycle evidence into success; never overwrite an existing
artifact; leave no temporary file that could be mistaken for completion. Temporary files are created
with `mkstemp` in the destination directory, are identity-checked, and are removed only if still owned
by this invocation.

A lifecycle document may legitimately survive a crash between step 5 and step 7. It must **not**
independently imply `COMPLETE`; analysis stays locked until a valid completion manifest exists.

### 8. Cadence limitation (frozen, retained)

The existing rejection of **empty right detector frame + non-unit cadence** is retained unchanged.
`instrumentation.py` is **not** repaired and the committed JSON Schema is **not** modified. Tests must
prove that this input can neither publish completion nor unlock analysis. The positive path must use a
real generic tracker output at a declared non-unit cadence already known to qualify.

### 9. Test matrix (frozen — 24 required behaviours, synthetic fixtures only)

1. qualifying real generic-tracker output at declared non-unit cadence
2. lifecycle validation failure blocks completion
3. zero terminal states blocks completion
4. multiple terminal states block completion
5. one invalid track causes global rejection
6. missing lifecycle file blocks analysis
7. tampered lifecycle bytes block analysis
8. non-canonical lifecycle bytes block analysis
9. swapped tracking input blocks analysis
10. changed sampling schedule blocks analysis
11. mismatched lifecycle digest blocks analysis
12. tampered completion manifest blocks analysis
13. non-canonical completion manifest blocks analysis
14. hand-constructed `LifecycleRunClosure` cannot satisfy the gate
15. hand-constructed terminal rows cannot satisfy the gate
16. direct nominal `"disposition": "QUALIFIED"` cannot satisfy the gate
17. a persistence exception leaves no completion manifest
18. a verification exception leaves no completion manifest
19. an existing output target is never overwritten
20. a lifecycle document without a completion manifest does not unlock analysis
21. empty-right-frame plus non-unit cadence remains rejected
22. no supported public API exposes an unchecked completion emitter
23. the existing bound lifecycle suite remains unchanged and passes
24. deterministic reruns produce byte-identical canonical completion evidence

Tests must not be weakened to achieve qualification.

### 10. Terminal dispositions (frozen)

`RUNNER_INTEGRATION_QUALIFIED` · `RUNNER_INTEGRATION_INSUFFICIENT` · `STOP_INTEGRATION`.
`STOP_INTEGRATION` is automatic on firewall breach, scientific execution, historical retrofit or
scientific-outcome generation. After any terminal disposition the only authorized next action is human
review.

### 11. File allowlist (frozen)

Exactly five new files, no existing file modified:

1. `edlab/substrates/lattice_bond/future_lifecycle_runner.py`
2. `tests/test_future_lifecycle_runner_integration.py`
3. `docs/individuation/FUTURE_LIFECYCLE_RUNNER_INTEGRATION_00_REPORT.md`
4. `docs/individuation/FUTURE_LIFECYCLE_RUNNER_INTEGRATION_00_QUALIFICATION.json`
5. `docs/individuation/FUTURE_LIFECYCLE_RUNNER_INTEGRATION_00_REVIEW_JOURNAL.md`

The existing lifecycle implementation, schema, instrumentation, package exports, tests and qualification
package are **not** modified. Requiring a sixth or modified file is a stop condition, not a scope
expansion. In particular the integration is **not** re-exported from
`edlab/substrates/lattice_bond/__init__.py`, because that file is hash-bound by the accepted package.

### 12. Prohibited-material firewall (frozen)

Not opened, enumerated, grepped, hashed or otherwise inspected: physics shards; shard filenames or
manifests; world names or per-world metadata; trajectories; candidate records; reconstructed
checkpoints; failed-autopsy inputs; any `results/` directory; prospective or `54xxx` seed namespaces;
global project indexes; `stage_b.py`; `stage_b_reproduce.py`; Kovacs materials.

Not done: engine or scientific-runner execution; historical Stage-B retrofit; selection of successful
historical worlds; repair of `instrumentation.py`; modification of the committed JSON Schema; opening a
new scientific family; creating a scientific preregistration; emitting any scientific outcome.

Permitted reads are limited to the human-review decision record, the seven bound lifecycle deliverables,
`lifecycle.py`, the relevant exports in `lattice_bond/__init__.py`, `tests/test_future_lifecycle_contract.py`,
only the tracker type definitions and cadence/frame interfaces required from `instrumentation.py`,
`tests/test_lattice_bond_instrumentation.py` limited to synthetic interface usage, and ordinary
packaging/test configuration. A complete read ledger is maintained in Part II.

---

*Part II (implementation, verification, independent reviews and terminal disposition) is appended after
this contract is committed. This file's state at the pre-implementation commit is the frozen reference.*
