# FUTURE-LIFECYCLE-OWNED-PIPELINE-RUNNER-00 — report

> **Part I is the frozen evaluation protocol.** It was committed alone, as checkpoint 1, before any
> implementation or test file existed. Everything after the Part I terminator is append-only material
> added later. Part I is a byte-exact prefix of this document.

**Mission:** `FUTURE_LIFECYCLE_OWNED_PIPELINE_RUNNER_00`
**Authorized parent:** `d493168d9013198723200308e1c3a91141ac2de4`
**Branch:** `codex/future-lifecycle-owned-pipeline-runner-00`
**Lineage:** `af765d2 → 9185afa → 4e1fd0c → c2fe25b → bc801c1a → 9a1bfaff → fb5619ba → 0fdb9092 → d493168`

---

# PART I — FROZEN EVALUATION PROTOCOL

## I.1 Why this mission exists

`FUTURE_LIFECYCLE_RUNNER_STACK_REQUALIFICATION_01` was accepted with one headline limitation, recorded as
L1/L2 and repeated in its human review: `future_lifecycle_runner.py` does **not** invoke
`track_components`. It receives an already-built `TrackingResult` and a declared schedule as two separate
arguments, so it verifies *declared* evidence and cannot know how many samples were actually acquired.
Outside occupied frames and live intervals the declared schedule is free in both directions.

This mission builds the missing owner: one supported synthetic entry point that performs acquisition
itself and creates every downstream artifact, so that invocation provenance exists **inside the API**.

## I.2 The exact claim being evaluated

> Within the supported synthetic public entry point, every acquired frame used for analysis comes from an
> invocation performed by the runner at a declared schedule position, is content-bound in an acquisition
> ledger, persisted and re-read before tracking, then passed through mandatory tracking, lifecycle
> validation and the qualified completion gate before analysis access is possible.

Nothing stronger will be asserted.

## I.3 Explicitly rejected claims

Any evidence that appears to support the following is out of scope and must be read as not claimed:

- proof of physical wall-clock time or of elapsed engine steps;
- proof that an external experimental source is honest;
- cryptographic authority of any digest;
- real-engine integration; scientific-runner readiness;
- scientific validity; individuality; rehabilitation of Stage B;
- protection against an actor who edits this module, the tracker, the lifecycle validator or the
  qualified runner, monkeypatches attributes, uses reflection, or controls both the written bytes and the
  verifying code;
- provenance authority for evidence that has been re-forged *in its entirety* and left internally
  consistent. Per-field tamper coverage is claimed; wholesale consistent re-forgery is not prevented and
  is the same content-addressed limitation the qualified runner already documents.

**Calling a synthetic source with the label `1_000_000` proves that the invocation was recorded under
that label. It does not prove that one million physical engine steps elapsed.** This sentence is
load-bearing and must be repeated verbatim in the final report and in the qualification JSON.

## I.4 API boundary

The single new supported surface is
`edlab/substrates/lattice_bond/future_lifecycle_owned_pipeline.py`, re-exported from
`edlab/substrates/lattice_bond/__init__.py`.

Two public entry points and their supporting types are permitted. The run entry point accepts:

- a destination directory;
- an **injectable synthetic acquisition source** (a callable);
- a requested schedule;
- the tracker/detector specifications the pipeline must use;
- a caller-declared acquisition-source identity document.

It must **not** accept, as caller-provided substitutes for executing a stage: prebuilt frame sequences;
tracking records; lifecycle records; lifecycle dispositions; qualification documents; completion
manifests; `AnalysisAccess`; acquisition ledgers; or persisted evidence directories.

The analysis entry point accepts a directory and **nothing else**: every specification, schedule and frame
is re-read from disk. This is deliberate — a caller cannot re-supply the inputs that would be compared
against the persisted evidence.

## I.5 Required owned execution order

1. validate the requested schedule *before* acquisition;
2. call the acquisition source exactly once for every scheduled sample, in strict order;
3. record every actual invocation;
4. immediately canonicalize and copy each returned frame so later caller mutation cannot affect it;
5. reject malformed frames and acquisition failures;
6. persist acquired frames and a canonical acquisition ledger;
7. bind each ledger entry to sequence position, requested sample label, returned frame digest, shape and
   dtype / canonical mask type;
8. bind a canonical identity document for the acquisition source, explicitly labelled caller-supplied
   identity and not external authority;
9. atomically persist the acquisition evidence;
10. discard the in-memory evidence;
11. re-read schedule, ledger and frames from disk;
12. independently recompute and verify every digest;
13. call `track_components` itself, with the re-read frames and mandatory keyword-only `sampled_frames`;
14. derive lifecycle inputs from actual tracker output;
15. execute the existing lifecycle validator;
16. use the existing qualified runner publication path;
17. re-read and reverify all downstream evidence;
18. publish `COMPLETE` only after the whole chain succeeds;
19. return or unlock `AnalysisAccess` only after final verification.

Any failure must leave no valid `COMPLETE` and no usable analysis access.

## I.6 Required invariants

**Acquisition ownership.** No public frames parameter exists; no public tracking, lifecycle, manifest or
access-object parameter exists; the source is called exactly once per schedule element; calls occur in
schedule order; no call is skipped or duplicated; exceptions fail closed; partial acquisition cannot
publish `COMPLETE`; post-return mutation of source-owned arrays cannot change persisted evidence.

**Acquisition-ledger integrity.** Tampering with any of the following must block completion and analysis:
schedule; order; sample count; sequence position; frame bytes; frame digest; shape; dtype; source identity
document; ledger digest; a missing or additional frame; a missing or additional ledger row.

**Tracker composition.** `track_components` is called by the runner itself; mandatory `sampled_frames` is
supplied from the re-read ledger; no default or compatibility path exists; tracker output cannot be
injected by the caller; tracker source identity and specification are bound; empty-right disappearance at
non-unit cadence remains valid terminal information.

**Lifecycle and completion.** Lifecycle records are derived from actual tracker output; no caller-authored
`QUALIFIED` disposition is trusted; exactly-one-terminal accounting remains mandatory; canonical evidence
is persisted, discarded, re-read and independently verified; no `COMPLETE` or analysis access exists after
any mismatch; atomic publication remains mandatory; a rival publication in the TOCTOU window fails closed.

**Zero detection.** A run in which acquisition occurs but nothing is detected may follow the lifecycle
contract's actual semantics, but the acquisition count and the exact schedule must remain proven by the
ledger, no arbitrary prebuilt evidence may substitute for acquisition, and the report must distinguish
"no detected entity" from "no acquisition occurred".

**External clock.** The owned runner establishes invocation provenance inside its API; it does not
establish physical elapsed time outside that API; acquisition-source identity remains a reproducibility
binding, not an authority certificate.

## I.7 Frozen synthetic test matrix

At minimum, and using handcrafted boolean masks only:

1. successful unit-cadence run;
2. successful non-unit cadence `(0, 5, 11, 12)`;
3. disappearance plus surviving track;
4. zero-detection acquisition;
5. schedule omission;
6. explicit `None` schedule;
7. malformed / non-monotonic schedule;
8. acquisition-source exception at every position;
9. malformed frame at every position;
10. mutable-buffer attack after return;
11. schedule padding / truncation tampering after persistence;
12. ledger row reorder;
13. frame substitution;
14. source-identity tampering;
15. tracker-spec tampering;
16. forged lifecycle disposition;
17. forged `COMPLETE`;
18. stale evidence reuse;
19. rival atomic publication;
20. analysis access attempted before completion;
21. re-opened analysis after every individual manifest-field tamper.

## I.8 Frozen mandatory mutation ledger

The following load-bearing mutants are frozen before implementation. Each must be killed by a **named
semantic regression**; a hash-only tripwire does not count as a semantic kill. The ledger may not be
silently reduced or renamed.

| id | mutation |
|---|---|
| A1 | skip an acquisition call |
| A2 | duplicate an acquisition call |
| A3 | use caller / in-memory frames instead of the disk-reloaded frames |
| A4 | trust the recorded frame digest instead of recomputing it |
| A5 | trust the acquisition ledger instead of reverifying it |
| A6 | replace the re-read schedule with the caller's requested schedule |
| A7 | bypass `track_components` |
| A8 | accept injected tracker output |
| A9 | construct a `QUALIFIED` lifecycle disposition directly |
| A10 | skip lifecycle execution |
| A11 | skip the final re-verification |
| A12 | replace atomic publication with a plain write |
| A13 | omit the source / spec / source-code bindings |
| A14 | return analysis access early, before final verification |

## I.9 Modification allowlist

Only these paths may change:

- `edlab/substrates/lattice_bond/future_lifecycle_owned_pipeline.py`
- `edlab/substrates/lattice_bond/__init__.py`
- `tests/test_future_lifecycle_owned_pipeline.py`
- `docs/individuation/FUTURE_LIFECYCLE_OWNED_PIPELINE_RUNNER_00_REPORT.md`
- `docs/individuation/FUTURE_LIFECYCLE_OWNED_PIPELINE_RUNNER_00_QUALIFICATION.json`
- `docs/individuation/FUTURE_LIFECYCLE_OWNED_PIPELINE_RUNNER_00_REVIEW_JOURNAL.md`

Not modifiable: `instrumentation.py`; `lifecycle.py`; `future_lifecycle_runner.py`; `engine.py`; the four
pre-existing bound test files; `pyproject.toml`; any historical report, qualification, review journal,
human-review record or schema.

**If the implementation cannot be completed within this allowlist the disposition is
`OWNED_PIPELINE_RUNNER_00_REVISE`, naming the exact missing authority.** It will not be smuggled in.

## I.10 Test selectors and environment

Selectors, and only these five:

- `tests/test_lattice_bond_instrumentation.py`
- `tests/test_future_lifecycle_contract.py`
- `tests/test_future_lifecycle_runner_integration.py`
- `tests/test_empty_right_nonunit_cadence_tracker_repair.py`
- `tests/test_future_lifecycle_owned_pipeline.py`

Environment: Python 3.11.x; pytest satisfying the repository constraint `pytest>=8.2,<9`. Qualification
under pytest 9.x is forbidden. All tests run inside a disposable clean room outside the repository,
populated one exact allowlisted Git blob at a time, whose namespace contains no undeclared file, and whose
every file is byte-verified against its `d493168` blob. No glob is used to populate it.

Requirements: every collected test passes; **0 failed; 0 skipped**; the complete ordered node-ID sequence
and its SHA-256 are bound in the qualification JSON; per-file collected counts are reported; **100%
statement and branch coverage of the new owned-pipeline module**, with measured denominators; the current
runner-stack coverage must not regress; the full mandatory mutation ledger is killed.

## I.11 Checkpoints

At most four principal checkpoints: (1) this frozen protocol, alone; (2) implementation and tests;
(3) reviewer fixes; (4) final sealed documents. Part I may receive **only** append-only material after the
terminator below. Nothing above it may be rewritten, reordered or deleted. Superseded claims are preserved
under an explicit banner with their corrections appended beneath, never silently rewritten.

## I.12 Independent review

Two independent adversarial reviewers are launched after the implementation/test checkpoint. Each receives
only this frozen protocol, the exact permitted source and tests, the closed synthetic clean room, and the
historical qualification documents by exact path.

- **Reviewer A — ownership and public-boundary adversary.** Find any way to inject frames, tracker
  records, lifecycle records, manifests or access objects; test skipped and duplicated acquisition; test
  in-memory versus disk evidence; test exception and partial-publication paths; test whether the accepted
  claim exceeds the real composition.
- **Reviewer B — tampering and provenance adversary.** Mutate every acquisition-ledger field; attack
  schedule, order and count bindings; attack source, spec and source-code bindings; attack zero-detection
  behaviour; test atomic-publication races; verify that mutation kills are semantic; challenge the
  physical-time limitation and any provenance overclaim.

Each returns PASS or FAIL with blockers, material findings, minors and observations. Every valid
in-allowlist finding is applied, a new checkpoint is created, and targeted re-review is requested, until
both PASS **against the same source/test commit** or an out-of-scope blocker forces revision. A reviewer
must stop immediately if it needs an undeclared path.

## I.13 Scientific firewall

Only predeclared exact Git object paths. Forbidden throughout the mission and both reviews: directory
listings; globs or wildcards; `git status`; `git ls-tree -r`; tree-wide `--name-only` / `--name-status`;
`find`; `rg --files`; broad `git grep`; archive-on-tree operations; traversal followed by filtering;
project-memory search; opening any undeclared path. If a declared path is absent, stop — do not search for
a replacement.

Not to be opened, enumerated, named, hashed, inspected or executed: scientific shards or manifests; world
records or per-world metadata; trajectories; candidate records; reconstructed checkpoints; autopsy inputs;
result directories; scientific or historical runners; prospective namespaces; Stage-B material; Kovacs
material; global project indexes.

No engine and no scientific runner may execute. `engine.py` is a hard import dependency of the package and
is bound by hash; no `LatticeBondEngine` is instantiated and no step is taken. The generic tracker and the
new owned pipeline execute only on handcrafted synthetic boolean masks inside the closed clean room.

## I.14 Terminal dispositions

`OWNED_PIPELINE_RUNNER_00_QUALIFIED` requires **all** of: no firewall breach; every required invariant of
I.6 proved or its limitation explicitly recorded; the full I.7 matrix present; all collected tests passing
with 0 failed and 0 skipped under the pinned environment; 100% statement and branch coverage of the new
module with measured denominators; no regression in the runner-stack coverage; every mandatory mutant of
I.8 killed by a named semantic regression; historical artifacts unchanged; lineage bound; and **both**
independent reviewers returning PASS against the same final source/test checkpoint.

`OWNED_PIPELINE_RUNNER_00_REVISE` if a required repair falls outside the allowlist, a load-bearing
invariant cannot be established, or a reviewer blocker stands.

`STOP_OWNED_PIPELINE_RUNNER` immediately upon any scientific-firewall breach.

**One FAIL controls. There is no majority voting.**

## I.15 Prohibition on scope expansion

This mission may not wire a real scientific runner, open or execute Stage B, begin Route E or Route G, or
create a family, seed, namespace, experiment or scientific result. The only authorized next action after
success is **human review of `FUTURE_LIFECYCLE_OWNED_PIPELINE_RUNNER_00`**, which this mission may not
begin.

<!-- END OF FROZEN PART I — nothing above this line may change -->
