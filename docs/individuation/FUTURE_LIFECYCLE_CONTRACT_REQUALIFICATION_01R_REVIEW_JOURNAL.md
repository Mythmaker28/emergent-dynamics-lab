# FUTURE-LIFECYCLE-CONTRACT-REQUALIFICATION-01R — review journal

Two independent read-only reviewers were commissioned. Each received **the same exact positive
allowlist** and nothing else, was instructed to STOP immediately if it needed an undeclared path, and was
told to try to falsify the implementer's claims rather than confirm them. Neither wrote to the clean
room; both verified afterwards that they had not.

| reviewer | mandate | verdict |
|---|---|---|
| **A** | mandatory API, exact call sites, schedule authority, mutation kills, minimality | **PASS** |
| **B** | historical/current lineage, synthetic survivorship proof, qualification scope, firewall compliance | **PASS** |

Neither reviewer requested an undeclared path, so neither had cause to STOP on that ground.

Both verdicts are recorded as returned. Neither was a rubber stamp: between them they invented four
mutants that the suite did **not** kill, found one factual overstatement in the lineage section, one
inaccurate claim in the enumeration section, one missing artifact, and one undisclosed contaminant. All
were fixed before sealing. The fixes are listed below with the mutant that now closes each.

---

## Reviewer A — mandatory API, call sites, schedule authority, mutations, minimality

### What A could not break

- **Signature.** `(frames, spec, *, sampled_frames: 'Sequence[int]')` — no default, no `__wrapped__`, no
  `__defaults__`/`__kwdefaults__`, no module- or package-level `__getattr__`, exactly one
  `def track_components` in the tree, exactly two mentions in `lattice_bond/__init__.py`.
- **Adversarial call shapes, 18 of them.** Correctly rejected: omission (`TypeError`), explicit `None`,
  positional third argument, `bytes`/`bytearray`/`str`/`set`/`frozenset`, negatives, non-monotone,
  wrong length, `bool`, `np.bool_`, `Fraction`, float arrays. Correctly accepted: generators, `range`,
  `np.array([0, 5])`, `list`/`int` subclasses, iterable-only objects, `()` frames with `()` schedule.
  Validation runs **before** the `if not frames` early return.
- **Call-site inventory** reproduced exactly by A's own independent AST pass. Zero `track_components`
  calls in any `edlab/` source file. Every positive call passes `sampled_frames=` by keyword with exactly
  two positional arguments.
- **Schedule authority.** Every fixture routes through `_observed(schedule, *masks)`, which stamps the
  detector states **from** the declaration. No `range(len(...))` of an already-built sequence anywhere.
- **Unchanged files.** `lifecycle.py`, `future_lifecycle_runner.py` and `lattice_bond/__init__.py` match
  their recorded digests in both the historical and the successor packages.
- **Baseline.** 219 passed / 0 failed, reproduced in an independently rebuilt copy.

### What A broke, and what was done about it

| A's finding | status | fix | now killed by |
|---|---|---|---|
| **OBS-1** monotonicity was pinned only on the first adjacent pair — every `test_12` case used a 2-entry schedule. A's `x_firstpair` mutant passed 219/219. | **fixed** | `test_12c` added: four 3-entry non-monotone schedules | mutant 13 |
| **OBS-2** the observed-frame cross-check was never pinned for a *unit-cadence* declared schedule; A's `x14` mutant let a `CONTINUATION` at frame 7 through under a declared `(0, 1)` — the exact survivorship shape this mission exists to close | **fixed** | `test_12d` added | mutant 14 |
| **OBS-3** the cross-check was pinned only against frames whose components all carried the same stamp; `observed[:1]` survived | **fixed** | `test_every_component_of_a_frame_must_carry_the_declared_frame_number` added, using handcrafted components with mismatched stamps | mutant 15 |
| **OBS-4** "12/12 killed" was inflated by the `test_23f` source-hash tripwire, which fires on any byte change | **fixed** | mutation table now reports **semantic** killers with both tripwires (`test_23f`, `test_23i`) excluded | — |
| **OBS-5** `test_m8`'s AST inventory is evadable by aliasing (`_tc = track_components`) | **accepted, documented** | not exploitable: an aliased *schedule-free* call still dies at runtime with `TypeError`, which A verified. The inventory's `set(inventory) == {four test files}` guard also catches a schedule-supplying wrapper injected into any source file. | — |
| **OBS-6** `test_unit_cadence_results_are_unchanged_from_the_qualified_parent` asserted only membership and determinism, not equality against a pinned parent output — the name over-claimed | **fixed** | renamed to `test_unit_cadence_results_are_on_schedule_and_deterministic`, docstring states what is and is not claimed and where the value pins live | — |
| **OBS-7** the schedule entry for an *empty* detector position is unverifiable in principle and taken on the caller's declaration | **accepted, inherent** | already documented in the validator docstring; bracketed by strict monotonicity. It is the single place where "schedule authority" is declaration-only, and it is now called out in the report. | — |
| **NIT-8** a `dict` was accepted as a schedule while `set`/`frozenset` were rejected — inconsistent with the stated "ordered sequence only" rule | **fixed** | `Mapping` added to the rejected-container tuple; `test_12e` added | mutant 16 |
| **NIT-9** `pyproject.toml` pins `pytest>=8.2,<9`; the run used pytest 9.1.1 | **disclosed, not fixed** | `pyproject.toml` is not on this mission's modification allowlist. Recorded in `environment_deviations` rather than silently reconciled. | — |

---

## Reviewer B — lineage, survivorship proof, scope, firewall

### What B could not break

- **All seven lineage properties are falsifiable.** B built eight lineage mutants and confirmed each is
  caught: tamper a `00` document → `23a`; rewrite the historical tracker hash → `23a`+`23b`; bind current
  source to the historical hash → `23c`+`23f`; change the recorded reason → `23d`; touch `lifecycle.py` →
  `23e`+`23f`; touch another bound test → `23f`; flip `requalified_by_this_mission` → `23g`; drop a node
  id and re-seal the digest → `23h`. 8/8 killed.
- **`test_23h` cannot be fooled by configuration.** `pyproject.toml` carries only `addopts = "-ra"`, and
  collecting the whole `tests/` directory yields exactly the same node set as the four selectors, so the
  binding really is the entire test surface.
- **Historical immutability.** All six `00` package digests recomputed and matched; clean-room mtimes
  independently show no historical document was rewritten.
- **`test_e1` is not vacuous.** 4096 configurations, real detector, mandatory API, only
  `LifecycleContractError` caught (any other exception fails the test), all five required outcomes
  asserted, plus `with_disappearance > 0` to foreclose a disappearance-free alphabet.
- **The 1295 invariant is correct.** B re-derived it: avoiding words force the empty letters into a
  prefix, `Σ_{k=0..4} 7^k = 2801`, `4096 − 2801 = 1295`. B also confirmed empirically that restoring the
  legacy fallback makes `test_e1` fail with `assert 1295 == 0` on the off-schedule counter — the
  historical number reproduced exactly through the current alphabet.
- **No overclaiming.** No document claims runner integration is requalified, that historical runners were
  inspected, or that every repository caller supplies the schedule. B's own AST pass reproduced the
  call-site counts exactly.

### What B broke, and what was done about it

| B's finding | status | fix | now killed by |
|---|---|---|---|
| **OBS-1** the lineage section read as if exactly one pinned artifact had moved. **Two** of the seven did: `instrumentation.py` and `tests/test_future_lifecycle_contract.py` | **fixed** | `lineage.divergent_from_historical_pin` now enumerates both with historical digest, current digest and reason; `test_23i` added, failing if any pinned artifact moves without being declared | mutant 17 |
| **OBS-2** three of the six digests in `test_23a` had never been pinned before and are self-attested by this mission | **fixed (disclosed)** | stated explicitly in the report rather than glossed; B corroborated from mtimes that no historical document was rewritten | — |
| **OBS-3** the report claimed the historical alphabet was "recorded in no allowlisted document"; the `00` review journal describes it in prose, and 01R had used "their union" where the prose says "a third blob" | **fixed** | alphabet changed to the prose-faithful reconstruction (third blob, not union); the report now cites the journal line and states precisely what *is* unrecorded — the third blob's pixel geometry | — |
| **OBS-4** `..._01R_REVIEW_JOURNAL.md` was declared in `changed_paths.added` but did not exist | **fixed** | this file | — |
| **OBS-5** `__pycache__/` directories from the implementer's runs were present and undisclosed | **fixed (disclosed)** | disclosed here. Structurally uncommittable: the branch is built by Git plumbing from explicitly hashed blobs at exactly the declared paths — there is no `git add`, so no untracked file can enter the commit. | — |
| **OBS-6** `test_23f` excludes itself, so a change to its own bodies is invisible in-suite | **accepted, disclosed** | inherent — a file cannot contain the digest of its own final bytes. Disclosed in the test, in the report, and closed out of band: B independently recomputed the digest and confirmed it matches the successor record. | — |
| **NIT-7** `FUTURE_LIFECYCLE_RUNNER_HARDENING_00` also binds the now-stale `instrumentation.py` digest, but was described only as "untouched" | **fixed** | `packages_carrying_a_now_stale_instrumentation_pin` lists all three; hardening marked `PENDING_FORMAL_REQUALIFICATION` alongside runner integration | — |
| **NIT-8** two assertions inside `test_23d` are self-referential in isolation | **accepted, documented** | non-vacuous as a composite: `23b`/`23c`/`23f` bind those constants to both qualification files and to disk. Recorded so the composite, not the individual assertion, is what is relied on. | — |
| **NIT-9** same pytest pin deviation A found | **disclosed** | see A's NIT-9 | — |

### B's self-disclosure

B disclosed, unprompted, that it ran `stat -c '%y %n' docs/individuation/*.md
docs/individuation/*.json` — a wildcard over a documentation directory, which is the class of act the
stop review forbids. It ran inside the **isolated clean room**, whose `docs/individuation/` contained
exactly the allowlisted documents and nothing else, so the enumerated namespace was closed: **0**
undeclared paths, **0** scientific names, **0** shard-related entries, **0** manifests were or could have
been discovered, and no repository directory was listed by anyone at any point.

Classified as **not a scientific-firewall breach** — the harm the stop review names is structurally
impossible in a namespace that contains no forbidden entry. Whether the procedural deviation is
nonetheless material is a judgement left to human review; it is recorded here in full and in
`..._01R_QUALIFICATION.json` under `disclosed_near_misses` rather than being argued away. B used the
result honestly, and it is how findings 2 and 4 were established.

---

## Post-review state

After all fixes, re-run in the clean room:

- **227 passed, 0 failed, 0 skipped** across the four bound selectors.
- **17/17 mutants killed**, including the four the reviewers invented and the lineage mutant B
  constructed. Each has at least one semantic killer independent of the two hash tripwires, except the
  lineage mutants, for which the `test_23*` assertions are themselves the semantic evidence.
- No reviewer finding was left unaddressed: eight fixed, five accepted with explicit documentation of why
  they are inherent or not exploitable, two disclosed as environment or procedural deviations.

Both reviewers returned **PASS**. The mission disposition is
`LIFECYCLE_REQUALIFICATION_01R_QUALIFIED`, and the only authorized next action is **human review**.

---

## HUMAN-REVIEW DEFERRAL ADDENDUM — NON_LOAD_BEARING_TRACEABILITY_GAP

**This addendum was required by deferred human review. It was not present in the original final
journal.** Human review of candidate `9185afaa2de69cbfe20b7ee983261d03e2225ce7` returned
`HUMAN_REVIEW_DEFERRED`. Every technical verification passed — the bound suite reproduced 227 passed /
0 failed / 0 skipped under a pytest release satisfying the declared `>=8.2,<9` constraint, the collected
node list matched the bound list element for element with the recorded digest, and the 4096-case
enumeration returned zero on every required counter. The deferral was caused solely by three statements
about the historical-partition gap being **absent from this journal**, though both were correctly
recorded in `..._01R_REPORT.md` and `..._01R_QUALIFICATION.json`. Nothing previously written here was
wrong; it was incomplete. Nothing above this line has been rewritten or altered — this section is
appended.

### The five required facts

1. **The historical rejection total `1295` reproduced exactly.** It is an alphabet-independent
   combinatorial invariant: over an 8-letter alphabet containing exactly one empty mask, a depth-4 word
   avoids every `non-empty → empty` adjacency exactly when its empty letters form a prefix, so the
   avoiding words number `Σ_{k=0..4} 7^k = 2801` and the rejecting words number `4096 − 2801 = 1295`.
   Reviewer B re-derived the arithmetic independently and confirmed empirically that restoring the legacy
   fallback makes `test_e1` fail with `assert 1295 == 0` on the off-schedule counter.

2. **The historical internal partition `3910 / 186` did not reproduce.** This was stated in the report
   and the qualification JSON but was missing here.

3. **The fixture geometry needed to reconstruct that partition is absent from the allowlisted record.**
   `EMPTY_RIGHT_NONUNIT_CADENCE_TRACKER_REPAIR_00_REVIEW_JOURNAL.md:250` describes the historical
   alphabet only in prose — "empty, two disjoint blobs, a third blob, a joinable bar, a split bar, and a
   symmetric-tie pair that forces `TRACKING_UNRESOLVED`". The *pixel geometry* of those masks, on which
   the partition depends, is recorded in no allowlisted document.

4. **No fitting, historical recovery or search for a matching geometry was attempted.** Candidate
   alphabets were tried while reconstructing the prose description, and the search was stopped once it
   was clear the partition is geometry-dependent. Continuing to vary geometries until `186` appeared
   would have been curve-fitting, not verification. No attempt was made to recover the historical script,
   and none could have been made without leaving the exact-path allowlist.

5. **No qualification criterion, API claim, survivorship result, mutation result or terminal disposition
   depends on that partition.** Every required outcome of the enumeration is zero-valued and
   alphabet-independent (zero schedule-free invocations, zero off-schedule event frames, zero
   disappearance-correlated rejections, zero survival rejections, zero terminal-accounting failures), and
   `with_disappearance > 0` is asserted so the enumeration cannot pass vacuously on a disappearance-free
   alphabet. The disposition `LIFECYCLE_REQUALIFICATION_01R_QUALIFIED` is unchanged by this addendum.

### Observed partitions — recorded as fixture measurements, not as results

| run | with-disappearance / without |
|---|---|
| historical `00` record | 3910 / 186 |
| candidate 01R, declared alphabet | **3534 / 562** |
| independent Reviewer B, its own alphabet | **3516 / 580** |

Neither the candidate figure nor Reviewer B's is a scientific result, and neither is offered as one.
They are counts over handcrafted synthetic mask sequences, and they exist here only to make the gap
legible.

- The **disagreement between the three figures confirms that the internal partition is
  fixture-dependent** — three reconstructions of the same prose description give three different
  partitions.
- The **load-bearing `1295` rejection invariant is separate from that partition**: it is fixed by the
  position of the single empty mask in a depth-4 word and is therefore independent of every other mask's
  geometry. That is why it reproduces exactly while the partition does not.
- **The gap is documentary and non-load-bearing.** Classified `NON_LOAD_BEARING_TRACEABILITY_GAP`.

### Scope of this addendum

Documentation only. No test, simulation, enumeration or engine was run to produce it. No scientific
artifact was opened. No source, test, report, qualification JSON, historical package document or
human-review file was modified. No disposition was changed. The only authorized next action is **repeat
human review of the corrected candidate**.
