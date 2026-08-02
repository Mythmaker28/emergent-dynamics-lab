# FUTURE-LIFECYCLE-CONTRACT-REQUALIFICATION-01R — report

**Mission:** `MANDATORY_SAMPLED_FRAMES_LIFECYCLE_REQUALIFICATION_01R`
**Terminal disposition:** `LIFECYCLE_REQUALIFICATION_01R_QUALIFIED`
**Authorized parent:** `af765d23fda2d85d77a439278ab03e92c495014a`
**Branch:** `codex/mandatory-sampled-frames-lifecycle-requalification-01r`

This mission makes the declared sampled-frame schedule **mandatory** throughout the supported generic
tracker and the permitted synthetic stack, and issues a **successor** lifecycle-contract qualification
against the repaired tracker. It does **not** requalify runner integration, wires no runner, allocates no
seed and opens no scientific material.

---

## 1. Lineage

| role | commit |
|---|---|
| accepted repaired-tracker ancestor | `4cf846c9052d42a18faee9b201ca00fd6740204f` |
| accepted repair human-review ancestor | `7539c32831d84771e2425c21b6966c2667155dfb` |
| authorized parent (accepted stop review) | `af765d23fda2d85d77a439278ab03e92c495014a` |

Ancestry verified by `git merge-base --is-ancestor` in both directions of the chain
`4cf846c → 7539c32 → af765d2`. The parent carries `HUMAN_REVIEW_ACCEPTED_STOP`, attempted disposition
`STOP_LIFECYCLE_REQUALIFICATION`, and authorization for this fresh successor. The stop-review record
classifies the prior breach as `METADATA_ONLY_FIREWALL_BREACH` and rejects post-hoc exclusion filtering
as insufficient; this mission therefore used **positive exact-path allowlists only**.

---

## 2. Firewall

**Status: no breach.**

Every artifact was reached by predeclared exact path: `git cat-file -e <commit>:<path>` for existence,
`git show <commit>:<path>` for content, and a hash of that byte stream only. No directory was listed.
No `git ls-tree -r`, no `find`, no `rg --files`, no recursive `ls`, no broad `git grep`, no `git archive`
on a tree, no wildcard capable of discovering an unknown file, no hash of a directory listing, and no
listing-then-filter. The 33 allowlisted paths were materialized one at a time into a clean room and each
was verified against its exact Git blob hash (33/33 exact, 0 mismatches).

Not opened, enumerated, grepped, hashed or inspected: physics or scientific shards, shard-related
filenames or manifests, world-level material, trajectories, candidates, checkpoints, autopsy inputs,
result directories, scientific namespaces, global indexes, historical scientific runners, Kovacs material.
No engine, scientific runner, physical tracker execution, feasibility simulation, parameter sweep,
autopsy or scientific analysis was run. All fixtures are handcrafted synthetic masks.

The dirty state of `main` was **not** inspected and its dirty paths were **not** enumerated. Only the ref
identity was recorded, before and after.

### Disclosed near-miss (independent reviewer B)

Reviewer B disclosed, unprompted, that it ran `stat -c '%y %n' docs/individuation/*.md
docs/individuation/*.json` — a wildcard over a documentation directory, which is the class of act the
stop review forbids. Recorded in full rather than waved through:

- it ran inside the **isolated clean room**, not the repository;
- that directory contained exactly the allowlisted documents and nothing else, so the enumerated
  namespace was **closed**;
- **0** undeclared paths, **0** scientific names, **0** shard-related entries, **0** manifests were
  discovered or could have been;
- no repository directory was listed by anyone at any point.

Classification: **not a scientific-firewall breach** — the harm the stop review names (learning and
hashing forbidden shard filenames) was structurally impossible in that namespace. The judgement of
whether the procedural deviation is nonetheless material is left to human review, not asserted away
here. Reviewer B also used the result honestly: it is how the missing review journal (finding 4) and
the historical-document mtime corroboration were found.

---

## 3. The API change

`edlab/substrates/lattice_bond/instrumentation.py` only.

```
- def track_components(frames, spec, sampled_frames: Sequence[int] | None = None) -> TrackingResult
+ def track_components(frames, spec, *, sampled_frames: Sequence[int]) -> TrackingResult
```

| required property | how it is met |
|---|---|
| `sampled_frames` has no default | signature carries no default; `inspect.Parameter.empty` asserted |
| type is non-optional | annotation is `Sequence[int]`; `None`/`Optional` absent from the annotation string |
| explicit `None` is rejected | `_validated_sample_schedule` raises `ValueError("sampled_frames is mandatory and must not be None")` |
| omission fails at the public API boundary | keyword-only with no default ⇒ `TypeError` raised by Python itself |
| every permitted caller passes it explicitly | AST inventory over the exact allowed paths, asserted in-suite |
| schedule strictly increasing | pre-existing validation retained |
| schedule length matches the observations | pre-existing validation retained |
| observed frames agree with the declared schedule | pre-existing cross-check retained |
| empty-right transitions use the actual declared right frame | `right_frame = schedule[transition_index + 1]`, unconditional |
| no transition-index fallback remains | helper `_transition_right_frame` **deleted**; `right[0].frame if right else …` absent from source |
| no implicit unit-cadence reconstruction remains | no `range(len(frames))` anywhere in the module |
| no compatibility alias restores the old signature | `__init__.py` mentions `track_components` exactly twice — one import, one `__all__` entry |

**Keyword-only was chosen deliberately.** The mission prefers it where the API permits a minimal change,
and it does: every permitted caller lives in a modifiable test file. Keyword-only additionally makes it
impossible for a third positional argument to slide into the schedule slot. Any caller outside the
declared paths that still passes a schedule positionally now fails **loudly** with `TypeError` rather
than silently — which is the correct direction for a fail-closed contract.

**Minimality.** Four edits to the tracker (the fourth added on Reviewer A's NIT-8): the validator's `None` branch inverted from *return* to
*raise*, the signature, and the deletion of a two-line helper whose only remaining branch was the
fallback, plus `Mapping` added to the rejected-container tuple so that "ordered sequence only" is true
of dictionaries as well as sets. The `lifecycle.py` validator and the `future_lifecycle_runner.py`
integration are **byte unchanged**.

---

## 4. Permitted call-site inventory

Scope: the exact allowed source and test paths, and only those.

| path | migrated call sites | negative call sites |
|---|---|---|
| `tests/test_lattice_bond_instrumentation.py` | 21 | 8 |
| `tests/test_empty_right_nonunit_cadence_tracker_repair.py` | 6 | 13 |
| `tests/test_future_lifecycle_contract.py` | 4 | 1 |
| `tests/test_future_lifecycle_runner_integration.py` | 2 | 0 |

"Negative call sites" are calls lexically inside `pytest.raises(...)` that exist to prove a malformed or
absent schedule is refused. `edlab/substrates/lattice_bond/__init__.py` re-exports the symbol and calls
it nowhere; `engine.py`, `lifecycle.py` and `future_lifecycle_runner.py` contain no call at all — the
runner consumes a `TrackingResult`, which is why it is source-compatible without modification.

**The claim is:** *no schedule-free call remains in the permitted generic tracker and synthetic
qualification stack.*
**The claim is not:** *every repository runner supplies the schedule.* Callers inside firewalled
historical runners were neither inspected nor migrated, and nothing here should be read as knowledge of
them.

### Schedule authority

Every migrated caller declares its schedule **first** and stamps its detector states **from** that
declaration. No caller recovers a schedule from an already-built frame sequence, and none derives one
from transition indices. Cadences covered: unit `(0,1)`/`(0,1,2)`/`(0..11)`; unit from a non-zero origin
`(7,8)`; regular non-unit `(0,5)`; irregular `(0,5,11,12,40)`, `(0,5,11,17,23)`, `(3,9,20)`; very large
`(10¹², …)`; empty-right disappearance; multiple tracks; split; merge; unresolved handoff; temporary
contact; the lifecycle fixture; and both runner-integration fixtures.

One pre-existing fixture had to be rebuilt rather than annotated:
`test_tracker_spec_changes_do_not_change_detector_or_physics` handed the *same* frame-0 detector output
in twice, which declares two samples at one instant. The mandatory schedule makes that unconstructible —
correctly — so the fixture now uses a genuine two-frame stationary sequence. No property under test was
weakened.

---

## 5. Historical / current lineage and the tripwire migration

`test_23_bound_lifecycle_package_remains_byte_identical` pinned the **current tree** to the digests
recorded by `FUTURE_LIFECYCLE_CONTRACT_00`. It already failed on the authorized parent, because the 00
repair had changed the tracker. Overwriting its expected digest would have destroyed the evidence the
tripwire carries. It was therefore **split**, not patched:

| test | proves |
|---|---|
| `test_23a` | the six historical 00 package documents are byte-identical |
| `test_23b` | the historical qualification still records the **historical** tracker hash `f40c0817…` |
| `test_23c` | the successor qualification records the **repaired mandatory** tracker hash `65d4185b…` |
| `test_23d` | the two differ, and the recorded reason is `MANDATORY_SAMPLED_FRAMES_SCHEDULE` |
| `test_23e` | `lifecycle.py` is `3120d820…` in both packages and on disk — unchanged |
| `test_23f` | current source matches the **successor** qualification, not the historical one |
| `test_23g` | runner integration is `PENDING_FORMAL_REQUALIFICATION`, `requalified_by_this_mission: false` |
| `test_23h` | the bound node list is complete: a test cannot be quietly dropped from the qualification |
| `test_23i` | **every** historically pinned artifact is either byte-identical or explicitly declared divergent with both digests |

`test_23f` verifies every bound test file except itself, and says so: a file cannot contain the digest of
its own final bytes. Its digest is recorded in the successor qualification and verified out of band at
seal time — independent reviewer B recomputed it and confirmed it matches the recorded value.

**Two of the seven pinned artifacts moved, not one (Reviewer B, OBS-1).** The deleted tripwire pinned
seven artifacts. `instrumentation.py` diverged (the subject of this mission) and so did
`tests/test_future_lifecycle_contract.py`, whose two call sites had to be migrated. An earlier draft of
this report described the divergence in the singular. Both are now enumerated in
`lineage.divergent_from_historical_pin`, each with its historical digest, its current digest and its
reason, and `test_23i` fails if any pinned artifact moves without being declared — verified by mutant 17.

**Three of the six digests in `test_23a` are new pins (Reviewer B, OBS-2).** `SCHEMA.json`,
`SOURCE_ALLOWLIST.json` and `SPEC.md` are cross-recorded in unmodified packages; `_REPORT.md`,
`_QUALIFICATION.json` and `_HUMAN_REVIEW.md` had never been pinned before, so those three constants are
self-attested by this mission. Stated rather than glossed. Reviewer B corroborated independently, from
clean-room mtimes, that no historical document was rewritten.

### Hashes

| artifact | sha256 |
|---|---|
| historical tracker (00 qualification) | `f40c0817acaad99c881e47ca16a7059164735a37ab15f134f11d1d69c6fd6c88` |
| repaired optional tracker (parent `af765d2`) | `2d896897244bfbc6cd5c01740bff98521633d500178bb2aed176d32ea669dbf4` |
| **repaired mandatory tracker (this mission)** | `65d4185bd9ef212b013d8d30000499f291f043f289e3e7bccbd536f466e810ef` |
| `lifecycle.py` — unchanged | `3120d820e30f2b7f71a709ba0fe335a732a0dc849473265f506d2c0307d03053` |
| `future_lifecycle_runner.py` — unchanged | `7691da3583ecd0fa6a84b87ebedceb815815307340c62eddaabb3190f4b33d08` |
| `lattice_bond/__init__.py` — unchanged | `9d3bea5ac70b514b592f71c2c46738dfdaec62e0072e8055a512b2e22ac6d5b0` |

**Validity boundary.** `FUTURE-LIFECYCLE-CONTRACT-00` remains valid as a **historical record** of the tree
at `ec494b4c`: its documents are byte-identical, its digests still describe that tree, and its claims about
the lifecycle-contract primitive are untouched. It does **not** describe the current tracker source, and
no longer claims to.

---

## 6. What changed in the tests, and why

Five tests asserted properties that the mandatory API makes inexpressible. Each was **restated**, not
deleted:

| superseded test | replacement | reason |
|---|---|---|
| `test_sampled_frames_argument_is_optional_and_defaults_to_the_legacy_path` | `…_is_mandatory_and_has_no_schedule_free_default` | the optional argument is gone |
| `test_identity_schedule_is_inert_at_unit_cadence` | `test_unit_cadence_results_are_unchanged_from_the_qualified_parent` | there is no second call path to compare against |
| `test_15b_the_legacy_call_path_is_untouched_when_no_schedule_is_supplied` | `test_15b_the_schedule_free_call_path_no_longer_exists` | the legacy path is deleted |
| `test_generic_tracker_empty_right_frame_cadence_mismatch_is_rejected` | `…_now_qualifies_at_nonunit_cadence` + `test_invalid_event_frame_guard_is_live_but_unreachable_from_the_tracker` | the limitation is lifted; the guard must not become dead code |
| `test_21_empty_right_frame_at_nonunit_cadence_remains_rejected` | `test_21_…_now_publishes` + `test_21b_a_fabricated_off_schedule_frame_is_still_refused` | same, at the runner boundary |

Wherever the *old defective output* was needed as evidence, it is now **handcrafted** — never produced by
the tracker. That is the point: the tracker can no longer produce it, and the guards that caught it are
shown to be live rather than dead.

---

## 7. Exhaustive synthetic proof

Depth-4 enumeration over a declared 8-mask alphabet at schedule `(0, 5, 11, 12)`, run entirely through
the mandatory public API (`test_e1_exhaustive_depth4_enumeration_through_the_mandatory_api`).

| quantity | value |
|---|---|
| configurations | **4096** |
| schedule-free invocations | **0** (structurally impossible) |
| off-schedule event frames | **0** |
| disappearance-correlated global rejections | **0** |
| survival rejections | **0** |
| exhaustive-terminal-accounting failures | **0** |

Alphabet, declared before the run and all defined in the test module: the empty frame, two disjoint
blobs, a third blob, a joinable bar, a split bar, and the separated / collapsed pair that forces
`TRACKING_UNRESOLVED`. This follows the prose description of the historical alphabet recorded at
`EMPTY_RIGHT_NONUNIT_CADENCE_TRACKER_REPAIR_00_REVIEW_JOURNAL.md:250`.

**Reproducibility, recorded honestly.** The historical `00` record reports this enumeration partitioned
as 3910 with-disappearance / 186 without, and 1295 legacy rejections.

The **1295 reproduces exactly**, and is in fact an alphabet-independent combinatorial invariant: over an
8-letter alphabet containing exactly one empty mask, a depth-4 word avoids every `non-empty → empty`
adjacency exactly when its empty letters form a prefix, so the avoiding words number
`Σ_{k=0..4} 7^k = 2801` and the rejecting words number `4096 − 2801 = 1295`. Reproduced under six
different candidate alphabets, all giving 1295, and confirmed independently by reviewer B, who also
re-derived the arithmetic and observed that restoring the legacy fallback makes `test_e1` fail with
`assert 1295 == 0` on the off-schedule counter.

The **3910 / 186 partition was not reproduced.** This mission obtains **3534 / 562** on its declared
alphabet. The historical journal describes the alphabet only in prose; the *pixel geometry* of the third
blob is recorded in no allowlisted document, and the partition is geometry-dependent. Eleven candidate
alphabets were tried across two reconstruction rounds (six third-blob geometries under the prose-faithful
shape, five structural variants), giving without-disappearance counts from 240 to 1015 — none near 186.
Continuing to vary geometries until 186 appeared would be curve-fitting, not verification, so the search
was stopped and the gap is stated. It has **no bearing on any required outcome**: every required outcome
above is zero-valued and alphabet-independent, and `with_disappearance > 0` is asserted so the
enumeration cannot pass vacuously on a disappearance-free alphabet. Reviewer B reproduced the
non-reproduction independently and judged the handling honest.

---

## 8. Mutation matrix

Seventeen mutants, each applied to a disposable exact-file copy of the clean room. **17/17 killed.**
Mutants 13-16 are the three that *survived* Reviewer A's independent round plus its NIT-8; mutant 17 is
Reviewer B's OBS-1 falsification. Each was closed by adding coverage, then re-killed.

Two of the tests are hash tripwires (`test_23f`, `test_23i`) that fire on any byte change to a bound
file, so they "kill" every source-side mutant trivially. The table below lists **semantic** killers with
those two excluded, so that "17/17" is not read as semantic coverage it has not earned. Mutants 8-10, 12
and 17 are lineage mutants; for those the `test_23*` assertions *are* the semantic killers.

| # | mutant | killed by (semantic killers) |
|---|---|---|
| # | mutant | semantic killers (tripwires excluded) | count |
|---|---|---|---|
| 1 | restore `sampled_frames=None` default | `test_m1`, `test_m3`, `test_15b`, `test_02` | 9 |
| 2 | accept explicit `None` | `test_m2`, `test_m6`, `test_m7`, `test_15b` | 7 |
| 3 | restore transition-index fallback | `test_m5`, `test_02`–`test_11`, `test_e1`, `test_s1`–`s3` | 29 |
| 4 | infer unit cadence when missing | `test_m1`, `test_m2`, `test_m6`, `test_02` | 12 |
| 5 | omit the schedule at one permitted caller | `test_m8`, `test_deformation_does_not_switch_identity` | 2 |
| 6 | pass index-derived fake frames at a caller | 26 cadence and survivorship tests | 26 |
| 7 | skip schedule/frame consistency | `test_12b`, `test_12d`, `test_every_component_of_a_frame_…`, `test_a_declared_schedule_…` | 4 |
| 8 | bind current source to the historical hash | `test_23c`, `test_23d` | 2 |
| 9 | mutate a historical qualification document | `test_23a` | 1 |
| 10 | claim runner integration is requalified | `test_23g` | 1 |
| 11 | restore disappearance rejection (drop terminal info) | `test_e1`, `test_s1`, `test_s2`, `test_21`, +27 | 31 |
| 12 | omit a selected test from the qualification | `test_23h` | 1 |
| 13 | monotonicity checked only on the first adjacent pair *(Rev A)* | `test_12c` ×2 | 2 |
| 14 | cross-check skipped for contiguous unit cadence *(Rev A)* | `test_12d` | 1 |
| 15 | cross-check only the first component of a frame *(Rev A)* | `test_every_component_of_a_frame_must_carry_the_declared_frame_number` | 1 |
| 16 | accept a mapping as a schedule *(Rev A NIT-8)* | `test_12e` | 1 |
| 17 | silently diverge a pinned artifact without declaring it *(Rev B)* | `test_23i` | 1 |

No surviving schedule-free path and no surviving outcome-dependent (disappearance-correlated) rejection
path was found, by the implementer or by either reviewer.

---

## 9. Test binding

| field | value |
|---|---|
| selectors | the four exact test files |
| collected node IDs | 227 |
| canonical node-list digest | `ba6fbbebc2945465847a96a85ba97a6de666d35aa979b73ba58cd82827503d8a` |
| passed / failed / skipped | **227 / 0 / 0** |
| Python | 3.11.15 |
| pytest | 9.1.1 |
| platform | Linux-6.18.5-x86_64-with-glibc2.39 |

The digest is `sha256` over the sorted node IDs joined by newline. Full node list, per-file digests and
changed-path coverage are recorded in `FUTURE_LIFECYCLE_CONTRACT_REQUALIFICATION_01R_QUALIFICATION.json`.
No arbitrary historical subset was used: the four bound selectors are the entire declared test surface.

---

## 10. Qualification boundary

**Qualified.**

- The supported generic tracker has no schedule-free path: omission is a `TypeError`, explicit `None` is a
  `ValueError`, and no cadence is reconstructed from transition indices.
- Every `track_components` call site inside the declared exact source and test paths passes an
  authoritative declared schedule, by keyword.
- A synthetic disappearance established by an empty right detector frame is retained as exactly one
  counted terminal record at the declared frame, at unit, non-unit and irregular cadence.
- Across the exhaustive depth-4 enumeration, no run is rejected, no event frame is off-schedule, and
  terminal accounting is exhaustive.
- The historical `FUTURE-LIFECYCLE-CONTRACT-00` package is byte-identical and remains historically valid.

**Not qualified.**

- **Runner integration.** `FUTURE_LIFECYCLE_RUNNER_INTEGRATION_00` is **not** requalified by this mission
  and remains **pending formal requalification**. That the runner does not call `track_components` and is
  therefore source-compatible is a structural observation, not a requalification.
- Any caller of `track_components` outside the declared exact paths.
- Any scientific claim, physical result, historical result or prospective family.
- Tracker correctness beyond schedule authority; physical identity, life, individuality or death.

This is **synthetic mechanical evidence only**.

---

## 11. Pending downstream step and next action

Pending downstream step: **formal requalification of the future-lifecycle runner integration** against
the mandatory-schedule tracker.

The only authorized next action is **human review**.
