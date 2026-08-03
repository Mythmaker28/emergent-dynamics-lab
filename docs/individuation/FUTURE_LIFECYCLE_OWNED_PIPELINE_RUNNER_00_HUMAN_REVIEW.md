# FUTURE-LIFECYCLE-OWNED-PIPELINE-RUNNER-00 — human review record

**Disposition: `HUMAN_REVIEW_ACCEPTED`**

This record discharges the human-review gate opened by `FUTURE_LIFECYCLE_OWNED_PIPELINE_RUNNER_00`. It is
a governance decision on a sealed candidate. It changes no source, no test and no historical artifact, it
does not edit the candidate documents, and it starts no engineering work.

---

## 1. Candidate and ancestry

| item | value |
|---|---|
| branch under review | `codex/future-lifecycle-owned-pipeline-runner-00` |
| candidate commit | `10034eaa0bd8f2c32278959db96ae0095f737298` |
| authorized parent | `d493168d9013198723200308e1c3a91141ac2de4` |
| frozen protocol (checkpoint 1) | `f2295bd5454db3c50357acc5e23604561d95168c` |
| implementation (checkpoint 2) | `c0e4fb2d17360fa916ccb173166302b2fc811bd7` |
| final reviewed source/test (checkpoint 3) | `d9995ce53c53e619aa2e25a29f0d36d94431bfc7` |
| candidate tree | `3595680c539e3029a7944d714f426294dead8176` |

Ancestry verified by exact-object parent traversal, one commit at a time. The chain is linear, complete,
and exactly as declared:

```
d493168  docs: accept future lifecycle runner stack requalification 01 review   (authorized parent)
   |
f2295bd5 docs: freeze owned pipeline runner 00 part I evaluation protocol       (checkpoint 1)
   |
c0e4fb2d feat: owned synthetic pipeline runner and its successor tests          (checkpoint 2)
   |
d9995ce5 test: apply both independent reviewers findings across three rounds    (checkpoint 3, reviewed)
   |
10034eaa docs: seal owned pipeline runner 00 report, qualification and journal  (candidate)
```

No side parent, no unexpected intermediate. **Every ancestry claim recorded in the candidate is true.**

---

## 2. Tree relation — proved constructively

Both path-set relations were proved by reconstruction under a temporary index outside the repository. No
directory listing, glob, `git status`, `git ls-tree -r`, tree-wide name listing, `find`, `rg --files`,
broad grep or archive-on-tree operation was used at any point of this review.

**Proof 1 — candidate versus authorized parent.** Reading the tree of `d493168` and overwriting exactly
the five declared paths with their candidate blobs reproduces the candidate tree bit-for-bit
(`3595680c…` both sides). Therefore **no path outside the declared five differs**. All five are absent at
`d493168`, so all five are additions and **nothing pre-existing was modified**:

- `edlab/substrates/lattice_bond/future_lifecycle_owned_pipeline.py`
- `tests/test_future_lifecycle_owned_pipeline.py`
- `docs/individuation/FUTURE_LIFECYCLE_OWNED_PIPELINE_RUNNER_00_REPORT.md`
- `docs/individuation/FUTURE_LIFECYCLE_OWNED_PIPELINE_RUNNER_00_QUALIFICATION.json`
- `docs/individuation/FUTURE_LIFECYCLE_OWNED_PIPELINE_RUNNER_00_REVIEW_JOURNAL.md`

**Proof 2 — the seal changed only the three documents.** The same construction from `d9995ce5`,
overwriting only the three document paths, reproduces the identical candidate tree. At `d9995ce5` the
report already existed (Part I alone, created at checkpoint 1) while the qualification and journal did
not; the seal appended Part II and added the other two. **The seal touched no source and no test**, so the
technical evidence attaches to exactly the bytes both reviewers examined.

**Part I integrity.** The frozen protocol at `f2295bd5` is 15,949 bytes with SHA-256
`5b0cdb742c7789ad3127e349304bb6fc070b50c9827b82966d08a5bc499aeef7`. The first 15,949 bytes of the sealed
27,787-byte report have the identical SHA-256. **Part I is a byte-exact prefix**; the protocol was not
rewritten to fit the outcome.

---

## 3. Byte identity

Recomputed from the candidate's own Git blobs and compared against `d493168`:

| path | sha256 | verdict |
|---|---|---|
| `edlab/substrates/lattice_bond/future_lifecycle_owned_pipeline.py` | `cc617f06f517aba7c890b9efbf069b7994696af243fc5a584220411747cae919` | new |
| `tests/test_future_lifecycle_owned_pipeline.py` | `063b58bfebd5602fc2b15a420cd2e9ffdbeeda62b1cb5b709847d14076ea67ff` | new |
| `edlab/substrates/lattice_bond/instrumentation.py` | `65d4185bd9ef212b013d8d30000499f291f043f289e3e7bccbd536f466e810ef` | **unchanged** |
| `edlab/substrates/lattice_bond/lifecycle.py` | `3120d820e30f2b7f71a709ba0fe335a732a0dc849473265f506d2c0307d03053` | **unchanged** |
| `edlab/substrates/lattice_bond/future_lifecycle_runner.py` | `7691da3583ecd0fa6a84b87ebedceb815815307340c62eddaabb3190f4b33d08` | **unchanged** |
| `edlab/substrates/lattice_bond/__init__.py` | `9d3bea5ac70b514b592f71c2c46738dfdaec62e0072e8055a512b2e22ac6d5b0` | **unchanged** |
| `edlab/substrates/lattice_bond/engine.py` | `e027a9c56b773ed077cdfe725951d215b631c54b7080da73e5321ccedb6d9ff6` | **unchanged** |
| `tests/test_lattice_bond_instrumentation.py` | `f91fd9e7c2bc20f28ad523fa224fd371f70bdc4e62bc2c81b374a412a0ee2abf` | **unchanged** |
| `tests/test_future_lifecycle_contract.py` | `b12b34651236c526ea772ce5c15ff5b2ca4054f638340069d0178be37c297126` | **unchanged** |
| `tests/test_future_lifecycle_runner_integration.py` | `a982415a6796bd7185ef3afac241d263d50bd98b03cb549136854fffe2dfaa1b` | **unchanged** |
| `tests/test_empty_right_nonunit_cadence_tracker_repair.py` | `50918cf0a77f0505e54e42f177de4084281dd2f05257b4e29942b2666615675e` | **unchanged** |
| `pyproject.toml` | `e187c1a5809a4b2631bd4e9b947a00ae6790b872a970ba625d283e855a5d498c` | **unchanged** |

Every source and test hash recorded in the qualification JSON was recomputed here from the object store
and **every one is true**. All accepted pre-existing production sources are byte-identical to `d493168`.

---

## 4. Reused evidence

The 486-test run, the coverage measurement, the mutation ledger, the 49 naive and 49 re-pinned tamper
cases and every reviewer probe were executed against `d9995ce5`. Proof 2 shows `10034eaa` adds documents
only, and section 3 shows every source and test hash matches the reviewed bytes exactly. **The evidence is
therefore reused, not re-run.** Nothing was executed during this review: no engine, tracker, pipeline,
test, mutation, sweep or scientific analysis.

Recomputed here directly from the qualification JSON, not copied from prose:

| quantity | declared | recomputed | verdict |
|---|---|---|---|
| ordered node count | 486 | `len(node_ids) = 486` | PASS |
| per-file counts | 49 / 52 / 87 / 63 / 235 | identical by prefix count, sum 486, zero duplicates | PASS |
| ordered node digest | `2fb7d16b0014e785e7c678b1aa6587471fcd9fab0748963fa69537f5cf98d5d8` | SHA-256 of the node IDs joined by `\n`, no trailing newline, reproduces it exactly | PASS |
| passed / failed / skipped | 486 / 0 / 0 | 486 / 0 / 0 | PASS |
| Python / pytest | 3.11.15 / 8.4.2 | as declared, satisfying `pytest>=8.2,<9` | PASS |
| owned module coverage | 431 statements, 188 branches, 0 missed, 0 partial, 100% | as declared, denominators measured | PASS |
| existing runner coverage | 194 statements, 56 branches, no regression | as declared | PASS |
| compiled semantic mutants killed | 26 | 27 ledger entries, 26 real kills, `R10` listed as non-compiling | PASS |

**R10 accounting.** The ledger does not claim 27/27. It records 27 entries, 26 real kills, and names
`R10` in `non_compiling_entries` with the reason: its `prelude2` anchor matched at the wrong indentation
so the mutant does not compile. The mutant it intends was applied at the correct indentation by Reviewer
B as its own `D5` and dies against all four `test_op_02c` flavours. The classification carried in the
qualification — 21 behavioural, 4 content-integrity, 1 API-signature, 1 non-compiling — was **measured by
Reviewer B from each killing test's own failure output**, not asserted by the driver, and no kill comes
from a hash tripwire. **This is honest accounting and is accepted as such.**

---

## 5. Reviewer history

| reviewer | mandate | round 1 | round 2 | round 3 |
|---|---|---|---|---|
| **A** | ownership and the public boundary | FAIL (1 blocker, 5 material) | FAIL (1 blocker, 4 material) | **PASS** |
| **B** | tampering and provenance | FAIL (4 blockers, 6 material) | FAIL (3 blockers, 4 material) | **PASS** |

Both PASS verdicts bind exactly `d9995ce53c53e619aa2e25a29f0d36d94431bfc7`, which is the commit this
review verified. One FAIL controls; there was no majority voting; no blocker is open.

**The failure history is intact, not laundered.** Eight blockers, all recorded as real. Two of them were
resolved by *deleting a false claim rather than defending it*, and both deletions remain visible in the
journal:

1. **"Per-field tamper coverage is claimed"** — falsified by Reviewer A, who showed a detection-equivalent
   frame substitution accepted with `LIFECYCLE.json` and `COMPLETION.json` byte-identical to a genuine
   run. Not repairable; became OP-L3.
2. **"`analysis_evidence_sha256` … can only be computed from an `AnalysisAccess` the qualified runner
   actually issued"** — falsified by Reviewer B, who proved
   `canonical(verified_completion_evidence())` *is* the completion manifest's own bytes, so the field was
   a restatement of `completion_manifest_sha256` and two mutants that never call the gate reproduced it.
   Claim withdrawn; the gate's load-bearing property is now pinned behaviourally by `test_op_01b`.

A third correction is recorded with equal candour: the first attempt at an on-disk invocation witness
advanced a counter once per loop iteration — definitionally the loop index — and a *stronger and false*
sentence had been written into the limitation register on top of it. Both reviewers falsified it with the
frozen `A1`/`A2` patches. It was repaired with an `_InvocationCounter` wrapper and `test_op_02c`, and
OP-L4 was rewritten to state only what is true.

The surviving re-pinned mutations are recorded quantitatively and remain visible: **49/49 naive ledger
edits and 14/14 binding edits refused; 41/49 re-pinned tampers refused, with all 8 survivors accounted
for by exactly OP-L2 and OP-L7**; 15/15 row attacks and 9/9 schedule and count attacks refused.

---

## 6. The accepted claim

Acceptance is granted for exactly this claim and nothing broader:

> Within the supported module-level synthetic API, the runner itself invokes the acquisition source once
> for each declared schedule element, persists and re-reads the resulting frames and acquisition ledger,
> executes mandatory tracking and lifecycle validation from that re-read evidence, and blocks COMPLETE
> and AnalysisAccess unless the complete local evidence set is internally consistent.

The terminal disposition `OWNED_PIPELINE_RUNNER_00_QUALIFIED` is **valid under that claim**. The
candidate's own `accepted_claims` and `claim_boundary` do not exceed it.

### Verified alongside the claim

- **No public `frames` parameter exists.** The run entry point's full parameter list is
  `(run_directory, *, acquisition_source, sampled_frames, detector_spec, tracker_spec,
  acquisition_source_identity)`; the analysis entry point takes `(run_directory)` and nothing else. None
  of `frames`, `frame_sequence`, `masks`, `tracking`, `tracking_result`, `lifecycle`, `lifecycle_records`,
  `disposition`, `qualification`, `manifest`, `completion`, `access`, `analysis_access`, `ledger`,
  `acquisition_ledger` or `evidence_directory` appears.
- **No tracking record, lifecycle record, disposition, manifest, ledger or access object can be supplied
  publicly.** Verified in the signatures and pinned by `test_op_21a` and `test_op_21h`.
- **The acquisition source is invoked once per schedule element**, through `_InvocationCounter`, which
  advances its counter inside `__call__`; the loop only reads `counter.ordinal_of_last_call`. Skips,
  duplicates, wrapper bypasses and trailing calls are refused **from the persisted evidence**.
- **Returned buffers are copied before caller mutation** — `np.array(frame, dtype=np.bool_, copy=True,
  order="C")` immediately on return, and every geometry question is asked of the copy.
- **Persisted evidence is discarded and re-read**: `del entries, ledger, payload, shape, acquired,
  ordinal` followed by `evidence = _reverify_acquisition(directory)`.
- **The runner calls `track_components` itself**, and **mandatory `sampled_frames` comes from the re-read
  ledger** (`sampled_frames=evidence.sampled_frames`).
- **Lifecycle records derive from tracker output**, through the accepted
  `publish_future_family_completion`.
- **Partial or failed acquisition cannot publish COMPLETE**; the owned binding is written only after the
  qualified gate succeeds, and the final analysis gate is on the success path with its exception
  propagating.
- **Disappearance at `(0, 5, 11, 12)` remains terminal information** — `DISSOLVED_DETECTED_TRACK` @5
  alongside `RIGHT_CENSORED_AT_HORIZON` @12, with exactly-one-terminal accounting.
- **Zero detection remains distinguishable from zero acquisition**: four empty masks publish and unlock
  with zero components while the ledger still proves four acquisitions at the exact schedule; an empty
  schedule is refused before any acquisition.
- **Physical elapsed time is not authenticated**, and **acquisition-source identity is a reproducibility
  binding, not authority** (`authority: "NONE"`, `declared_by: "caller"`).
- **No scientific claim follows.**

---

## 7. Package-export limitation — recorded, and accepted as deferred

The new entry point was **not** re-exported through `edlab/substrates/lattice_bond/__init__.py`, because
that file is byte-pinned at `9d3bea5a…` by the accepted RS01 qualification and verified by the
unmodifiable bound test `test_rs01_13`. Editing the re-export would have turned a green tripwire red.

**Decision.** The candidate claims only a supported *module-level* API. Part II §II.7 states the
non-modification prominently and names the supported surface as
`edlab.substrates.lattice_bond.future_lifecycle_owned_pipeline`; the qualification JSON records
`init_reexport_deferred: true` and `init_reexport: "DEFERRED_MISSING_AUTHORITY"`; and the accepted claim
is scoped to `run_owned_future_pipeline`. Nowhere does the candidate assert that a user can import the API
from the `lattice_bond` package namespace. This is therefore a **non-load-bearing deferred package-export
obligation** and is accepted as such.

**Superseded wording, recorded so it is not quoted alone.** Part I §I.4 — frozen before implementation and
append-only by protocol — says the new surface is *"re-exported from `edlab/substrates/lattice_bond/
__init__.py`"*. That sentence describes intent, not outcome, and is **superseded by Part II §II.7**. It
must not be cited as a capability.

**Direct import from `future_lifecycle_owned_pipeline` is not equivalent to package re-export** and is not
accepted as such here. The exact missing authority is: permission to update
`tests/test_future_lifecycle_runner_integration.py` and/or the `__init__.py` entry of
`FUTURE_LIFECYCLE_RUNNER_STACK_REQUALIFICATION_01_QUALIFICATION.json`. Until that authority is granted,
package export or an exact frozen module import is a **prerequisite for any later scientific family**.

---

## 8. Correction — "there is no repair without a secret"

The review journal says, of Reviewer A's round-1 blocker, *"No repair exists without a secret."* Read
literally that is **too broad**, and it is superseded here.

**Correct formulation.** A purely self-contained mutable evidence directory cannot detect a complete,
internally consistent rewrite of itself. Preventing such re-pinning requires an **independent trust
anchor**. That anchor may be a secret-backed signature, but it may equally be a **public immutable or
append-only commitment** — a published Git object, a transparency log, a timestamped registry, WORM
storage, or an externally published root digest. No secret is required.

**Load-bearing test.** The phrase occurs once, in the journal's narrative, and nowhere else: it does not
appear in the report, in the qualification JSON, or in the module. The disposition, the accepted claims
and the limitation register make no appeal to it, and OP-L3 is stated as a measured empirical boundary
rather than an impossibility argument. **The statement is non-load-bearing shorthand and the qualification
remains valid under the corrected formulation**, so the review is accepted and the wording is superseded
here rather than deferred for a documentary correction. The candidate documents were not edited.

This correction has practical force: the repository is itself a Git object store, so an externally
anchored evidence root is achievable for future work **without any secret at all**.

---

## 9. OP-L3 — accepted as an explicit threat-model boundary

OP-L3 is accepted **only** with the following boundary, and no further:

- local frame and ledger hashes detect ordinary or partial tampering;
- **49/49** naive mutations are rejected;
- **41/49** fully re-pinned mutations are rejected;
- the surviving fully re-pinned transformations preserve the structural information the tracker/lifecycle
  stack actually consumes — per-frame component count and resulting track topology;
- morphology such as area, mass, centroid, pixel set and radius of gyration is **not bound into lifecycle
  semantics**, so for a terminating component a four-cell blob may be replaced by the whole lattice, and
  for a persisting one the space is bounded only by the tracker's own association thresholds;
- an adversary able to rewrite and consistently re-pin the entire mutable evidence directory is **outside
  the locally detectable threat model**;
- future scientific use **must externally anchor the final evidence root** before relying on morphology or
  any other unbound measurement.

**OP-L3 does not prove the pipeline scientifically trustworthy, and nothing in this record should be read
as claiming that.**

The remaining register entries are accepted as written, each pinned by a named test: OP-L1 (the artefacts
attest reproduction, not acquisition), OP-L2 (an inert specification perturbation is accepted), OP-L4 (the
recorded invocation count is a within-process witness only; on disk the fields carry no independent
information), OP-L5 (the publication primitive is leaner than the accepted runner's and fails closed
downstream), OP-L6 (the returned capability is the accepted runner's and carries no acquisition evidence),
OP-L7 (the declared identity payload is free text; its shape is bound, its content is not). Both reviewers
state they would sign all seven as written, each having measured the boundary rather than read it.

The owed work the candidate records rather than repairs is carried forward unchanged: the `OSError`
typing in `_atomic_create` is unpinned; the two symlink guards are pinned only in combination; the
`dilation_radius` bound is unpinned at both endpoints; `dtype` is the one frame question still asked of
the caller object rather than the owned copy (measured to produce no false evidence); `R10` needs
re-anchoring; `test_op_13a3`'s docstring still carries superseded OP-L3 wording; and the register is
ordered L1 L2 L3 L4 L7 L5 L6.

---

## 10. External clock

**Calling a synthetic source with the label `1_000_000` proves that the invocation was recorded under that
label. It does not prove that one million physical engine steps elapsed.** The owned runner establishes
invocation provenance inside its API; it does not establish physical elapsed time outside that API. The
sentence appears in the module header, in both public docstrings, and in a `provenance_disclosure` field
carried by both on-disk documents, so a consumer who never reads the source still meets it.

---

## 11. Scientific meaning

None. This is synthetic engineering infrastructure. No scientific entity or outcome was observed, no
historical result changes, Stage B remains closed, no prospective route is selected, Route G remains
deferred, no seed or namespace was allocated, and no engine or scientific runner executed at any point of
the mission or of this review.

---

## 12. Firewall, refs, residue and remote

**Firewall — no breach.** This review used exact named Git object paths only. Zero directory listings;
zero globs or wildcards; zero `git status`; zero `git ls-tree -r`; zero tree-wide name listings; zero
`find`; zero `rg --files`; zero broad greps; zero archive-on-tree operations; zero project-memory
searches; zero undeclared paths opened. The two path-set proofs were performed constructively with a
scratch index under `/tmp` precisely to avoid a tree-wide listing. Text inspection was confined to the
five declared mission paths plus the exactly named accepted sources listed in section 3. No scientific
data, runner, shard, manifest, world, trajectory, checkpoint, autopsy input, result directory, Stage-B,
prospective namespace or Kovacs material was opened, enumerated, named, hashed or executed. The
candidate's own `firewall` ledger records the same posture for the mission and both reviews, and nothing
observed here contradicts it.

**Refs preserved.** `refs/heads/main` was observed at `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77` before
this record was written and is left exactly there; `HEAD` remains on `main` and was not moved.
`refs/heads/codex/future-lifecycle-owned-pipeline-runner-00` remains at `10034eaa…`;
`refs/heads/codex/future-lifecycle-runner-stack-requalification-01-human-review` remains at `d493168…`.
No checkout, reset, merge, rebase, tag or ref deletion was performed. The human-review branch was verified
**not to exist** before creation. The commit was created with lock-free plumbing against a temporary index
under `/tmp`, because the working mount is create-only and cannot clear stale Git locks.

**Residue.** This review adds exactly one new file and writes nothing into the working tree. The residue
disclosed by the engineering mission is carried forward and is **the owner's to remove**, since the mount
refuses `unlink`: `.opr00_probe_delete_me` (6 bytes) at the repository root, an emptied `_opr00_staging/`,
and `_to_delete/opr00/` holding three transfer files.

**Remote.** The candidate's `remote_status` is `PENDING`. One ordinary authenticated push was attempted
after this commit; the result is reported in the session response. If it returned HTTP 403 the branch is
**NOT SYNCHRONIZED** and remains intact locally for a manual push. This is non-blocking for the
disposition.

---

## 13. Decision

**`HUMAN_REVIEW_ACCEPTED`.**

`OWNED_PIPELINE_RUNNER_00_QUALIFIED` is accepted, strictly within the claim in section 6 and strictly
subject to sections 7 to 10. Every recorded hash and ancestry claim checked here is true; no undeclared
path changed; the qualification depends on no materially false claim; the scientific firewall is intact.

### Sole authorized next mission

`FUTURE_PROSPECTIVE_READINESS_ARCHITECTURE_01`

Successor to the accepted `ARCHITECTURE_REVISE` decision. Its purpose is to return to **scientific
planning** now that the cadence, lifecycle, runner-stack and owned-pipeline blockers are closed. It must
compare at least:

- **revised Route E** — a replication-density estimand with a genuine prospective decision rule;
- **Route G** — a symmetry-broken internal convention without an imposed sign, with independence across
  co-housed entities, persistence through turnover, local addressability, environmental equalization and
  ownership tests;
- **Route F** — stop/consolidate, as the honest fallback.

It may select a route **only** if that route passes the frozen gates. It must treat the following as
**prerequisites for any later scientific family**:

1. package export, or an exact module import frozen in the future runner;
2. an externally anchored final evidence root (see section 8 — a public immutable or append-only
   commitment suffices; no secret is required);
3. no reuse or tuning from the closed Stage-B family;
4. no historical `M_MINUS` result used as Route-G confirmation.

That mission was **not** begun during this review.

### Not authorized

An experiment, a seed, an engine run, a scientific family, Stage-B wiring, scientific runner execution,
Route E or Route G *execution*, a prospective namespace, or scientific-data access.

No scientific conclusion follows from this record.
