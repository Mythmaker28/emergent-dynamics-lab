# FUTURE-LIFECYCLE-OWNED-PIPELINE-RUNNER-00 — review journal

Two independent adversarial reviewers were commissioned after the implementation/test checkpoint. Each
received only the frozen Part I protocol, the exact permitted source and tests, the closed synthetic
clean room, and the historical qualification documents by exact path. Both mutated only copies under
`/tmp`, and both verified afterwards that the clean room was byte-unchanged. Neither ever requested an
undeclared path.

| reviewer | mandate | round 1 | round 2 | round 3 |
|---|---|---|---|---|
| **A** | ownership and the public boundary | **FAIL** (1 blocker, 5 material) | **FAIL** (1 blocker, 4 material) | **PASS** |
| **B** | tampering and provenance | **FAIL** (4 blockers, 6 material) | **FAIL** (3 blockers, 4 material) | **PASS** |

Both final verdicts bind the same commit, `d9995ce53c53e619aa2e25a29f0d36d94431bfc7`, and the same two
files. **One FAIL controls; there was no majority voting.** Eight blockers were raised in total and all
eight were real.

---

## The two findings that mattered

**Round 1 — Reviewer A: the frames are content-addressed, not acquisition-bound.** A frame whose detected
components are unchanged can replace the acquired one once the digests are re-pinned; the lifecycle
document is the only anchor outside the acquisition chain and it binds the tracking, not the pixels.
Reviewer A demonstrated it with a twenty-line attacker script leaving `LIFECYCLE.json` and
`COMPLETION.json` byte-identical to the genuine run, and observed that the module's phrase "per-field
tamper coverage is claimed" was therefore false. **No repair exists without a secret.** The claim was
rewritten from attestation to reproduction and the residue became OP-L3. In round 3 Reviewer A showed the
first wording of OP-L3 still *understated* it: the substitution space is not exotic specks but any frame
preserving per-frame component count and track topology — a four-cell blob may become the whole lattice.
OP-L3 was widened again and `test_op_13a3` now demonstrates the strong case under the default detector.

**Round 2 — both reviewers: the on-disk invocation witness was a loop index.** The first fix relocated a
variable without changing its coupling, and then asserted the stronger, false property in the limitation
register. Reviewer A: *"a net regression in truthfulness, in the register a reader is being asked to
sign."* Reviewer B applied the frozen A1/A2 patches to the shipped module and showed three, four and five
real calls all producing an identical accepted ledger. The repair is the `_InvocationCounter` wrapper
Reviewer A specified; Reviewer A verified it afterwards by editing the call site of a module copy rather
than by trusting the delivered test, and reported seven of seven drift cases caught from the persisted
evidence.

Reviewer B additionally proved that `analysis_evidence_sha256` was mathematically forced to equal
`sha256(COMPLETION.json)`, so the field could not witness the final gate; two mutants that never call the
gate reproduced it exactly. That claim was **withdrawn** rather than patched, and the property it was
supposed to carry is now pinned behaviourally by `test_op_01b`.

---

## Reviewer A — ownership and the public boundary

| id | finding | resolution |
|---|---|---|
| **B1** (r1) | detection-equivalent frame substitution accepted | not repairable; recorded as OP-L1/OP-L3, pinned by `test_op_13a3` |
| **B1** (r2) | OP-L4 false: counter tied to the loop, not the call | `_InvocationCounter` wrapper; `test_op_02c` with four separable flavours |
| M1 (r1) | identity block unchecked on read (28/28 mutations accepted) | exact key set, `authority`, `declared_by`, str→str; `test_op_14e` |
| M2 (r1) | `dilation_radius` of 10⁹ made the entry point non-terminating | bounded by `max(frame_shape)`; `test_op_15i` |
| M3 (r1) | limitation lived in a test docstring; no OP-L1 existed | full register OP-L1…OP-L7 in the module docstring |
| M4 (r1) | `test_op_13a2` stopped one step short of its own scenario | cell-count-preserving edit; re-pinned variant is `test_op_13a3` |
| M5 (r1) | the capability carries no owned evidence | disclosed as OP-L6, pinned by `test_op_23f` |
| M1 (r2) | OP-L3 understated by a very wide margin | rewritten to component-count-and-topology; measured table reconfirmed |
| M2 (r2) | specification coercion: `1.9` silently ran as `1` | plain-number strictness; `test_op_22k` |
| M3 (r2) | negative persisted shape leaked an untyped `ValueError` | `min(row_shape) >= 2` on read; `test_op_22l` |
| M4 (r2) | boolean `requested_sample_label` matched label `0` | `_plain_int`; `test_op_22m` |

Accepted without repair: five prose minors from round 3 (a superseded docstring sentence in
`test_op_13a3`, register ordering, a cosmetic "single supported entry point" collision, a ragged line
wrap, and re-exported accepted-dependency names). They are recorded here rather than fixed, because both
PASS verdicts bind this exact source/test state and re-opening it would invalidate them.

**What A could not break.** ≈3,400 probes across three rounds. Field sweep of 657 re-pinned mutations:
591 refused, and for the first time **every single acceptance is accounted for** — 36 harness no-ops, 6
value-identical no-ops, 23 disclosed OP-L2 perturbations, 1 disclosed OP-L7. Zero undisclosed, down from
28 in round 1. Byte-level fuzz: 352 trials, 0 accepted. Injection: 12 frame shapes and 9 schedule shapes
including `ndarray` subclasses lying about `shape` *and* `ndim`, a `Sequence` whose `__len__` lies and
whose `__iter__` changes on the second pass, and a shifty `os.PathLike` — all closed. Exception, rival
and concurrency paths including an 8-way thread race: exactly one winner, seven `OwnedPublicationError`,
no leftovers.

---

## Reviewer B — tampering and provenance

| id | finding | resolution |
|---|---|---|
| **B1** (r1, r2) | no on-disk witness of the acquisition count | `_InvocationCounter`; `test_op_02c`; OP-L4 rewritten |
| **B2** (r1) | `_atomic_create`'s no-TOCTOU claim untested; an `exists()`-guarded write could write through a dangling symlink | `test_op_19a2`; mutant R3 |
| **B2** (r2) | `analysis_evidence_sha256` forced equal to the manifest digest | claim withdrawn; joint digest + `test_op_01b`; mutants R11 |
| **B3** (r1) | the final gate had zero coverage | `test_op_01b` |
| **B3** (r2) | the driver asserted mutation semanticity and had no timeout | flag deleted, 180 s timeout added |
| **B4** (r1) | identity block unbound on read | see Reviewer A M1 |
| M2 (r1) | `OSError` escaped the typed hierarchy | `_atomic_create` types every `OSError` |
| M4 (r1) | `requested_sample_label` binding untested | `test_op_12c2`; mutant R1 |
| M5 (r1) | `test_op_21c` passed whether or not the guard fired | invocation list asserted empty; mutant R5 |
| M1 (r1) | schedule non-monotonicity untested in isolation | `test_op_22g2`; mutant R2 |
| M3 (r2) | the lying-`ndarray` hardening was uncovered | `test_op_22n`; mutant R12 |

Accepted without repair, with reasons written down: the `OSError` typing remains unpinned (Reviewer B
argues correctly that `monkeypatch.setattr(owned.os, "link", ...)` would close it in three lines, and
that is recorded as owed work); the two symlink guards are individually redundant and only pinned in
combination, which Reviewer B calls acceptable provided nothing claims otherwise — nothing does; the
`dilation_radius` bound is unpinned at both endpoints; `dtype` is the one frame question still asked of
the caller object rather than of the owned copy, which Reviewer B measured to produce **no false
evidence** because the copy coerces truthiness; and ledger entry R10 does not compile.

**What B could not break.** Round 3: 49/49 naive ledger edits and 14/14 binding edits refused; 41/49
re-pinned tampers refused, with all 8 survivors being exactly OP-L2 and OP-L7; 15/15 row attacks and 9/9
schedule and count attacks refused; four in-process drift attacks (skip, duplicate, wrapper bypass,
trailing extra) all refused **by the persisted evidence**; three attempts to produce a record while a
refusing gate is in place all died on `test_op_01b`; twelve hostile pre-existing publication targets all
failed closed with typed errors.

---

## Disposition of every finding

Eight blockers raised, eight resolved — five by repair, three by withdrawing or weakening a claim that
could not be supported. Nineteen material findings: fifteen repaired, four recorded as disclosed
limitations with the reviewer's own wording. Residual minors are listed above and are prose or owed
coverage, not behaviour.

Two claims were **deleted rather than defended**: "per-field tamper coverage is claimed", and
"`analysis_evidence_sha256` … can only be computed from an `AnalysisAccess` the qualified runner actually
issued". Both were false, both were caught by a reviewer, and neither survives anywhere in the delivered
material.

## Post-review state

- **486 passed, 0 failed, 0 skipped** under Python 3.11.15 and pytest 8.4.2.
- Node digest `2fb7d16b0014e785e7c678b1aa6587471fcd9fab0748963fa69537f5cf98d5d8`, recomputed by both reviewers.
- Owned module coverage **431 statements / 188 branches / 0 missed / 0 partial / 100%**; runner-stack
  coverage unchanged at 194/56.
- Mandatory ledger A1–A14 plus R1–R13: 26 real kills, none via a hash tripwire, plus one non-compiling
  entry (R10) whose intended mutant Reviewer B verified dies.
- **No accepted source modified.** Two files added.

Both reviewers returned **PASS** against `d9995ce53c53e619aa2e25a29f0d36d94431bfc7`, each stating
explicitly that they would sign OP-L1 to OP-L7 and the boxed guarantee as written. The disposition is
`OWNED_PIPELINE_RUNNER_00_QUALIFIED`, and the only authorized next action is **human review**.
