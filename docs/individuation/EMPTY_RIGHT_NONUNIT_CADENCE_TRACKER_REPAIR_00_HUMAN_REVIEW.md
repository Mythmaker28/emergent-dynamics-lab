# EMPTY-RIGHT-NONUNIT-CADENCE-TRACKER-REPAIR-00 — human review

**Terminal disposition: `HUMAN_REVIEW_ACCEPTED`**
**Accepted mission disposition: `TRACKER_REPAIR_INSUFFICIENT`**

Issued by the project owner and human reviewer, 2026-08-02.

This decision accepts the correctness of the implemented repair while accepting that the survivorship
trapdoor **remains open in the supported default API**. It does **not** qualify the repaired tracker for
future scientific use.

---

## 1. Accepted candidate

| field | value |
|---|---|
| branch | `codex/empty-right-nonunit-cadence-tracker-repair-00` |
| candidate commit | `4cf846c9052d42a18faee9b201ca00fd6740204f` |
| authorized parent | `f7b6c9797dc6bdfc969ddf5c3421bef9991e339c` |
| decision branch | `codex/empty-right-nonunit-cadence-tracker-repair-00-human-review` |

Candidate lineage from the authorized parent, four commits, first-parent linear:

```
4cf846c tracker: record independent reviews and return TRACKER_REPAIR_INSUFFICIENT
89681c0 tracker: close the coverage gaps found by the independent reviewers
0509ad8 tracker: bind empty right frames to the declared sample schedule
04d2d31 tracker: freeze empty-right/non-unit-cadence semantic contract (part I)
```

## 2. Pre-write verification

All nine required checks were executed against the candidate before this record was written.

| # | check | result |
|---|---|---|
| 1 | full candidate hash resolved | `4cf846c9052d42a18faee9b201ca00fd6740204f`, object type `commit` |
| 2 | ancestry from `f7b6c97` | `git merge-base --is-ancestor` → **YES**; exactly 4 first-parent commits |
| 3 | exactly six files changed, within the authorized allowlist | **6**, listed in §2.1 |
| 4 | `lifecycle.py` and `future_lifecycle_runner.py` byte-identical | **IDENTICAL** — blobs `a3592eb7…` and `44135ee7…`; content SHA-256 `3120d820…d03053` and `7691da35…f4b33d08` |
| 5 | Part I remained frozen | candidate report is the checkpoint-1 report **plus a pure append**: the first **13 375 bytes** (SHA-256 `3242d52d…fa10a`) are byte-for-byte identical; 20 411 bytes appended as Part II |
| 6 | Reviewer A returned `FAIL` | journal line 54 `## VERDICT: FAIL`; qualification record `A / frame and tracker semantics → FAIL` |
| 7 | Reviewer B returned `PASS` | journal line 222 `## VERDICT: **PASS**`, line 224 recommending `TRACKER_REPAIR_QUALIFIED` scoped and conditioned |
| 8 | frozen criterion requires `TRACKER_REPAIR_INSUFFICIENT` | Part I §13, quoted verbatim in §5 below, is met literally |
| 9 | original dirty checkout unchanged | `main` still at `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77`; 21 dirty entries (19 `.cache_active/` deletions + untracked `docs/paper/full/` and `results/sc_hmc/`), all pre-existing; none of the candidate paths present |

### 2.1 The six changed files

```
docs/individuation/EMPTY_RIGHT_NONUNIT_CADENCE_TRACKER_REPAIR_00_QUALIFICATION.json
docs/individuation/EMPTY_RIGHT_NONUNIT_CADENCE_TRACKER_REPAIR_00_REPORT.md
docs/individuation/EMPTY_RIGHT_NONUNIT_CADENCE_TRACKER_REPAIR_00_REVIEW_JOURNAL.md
edlab/substrates/lattice_bond/instrumentation.py
tests/test_empty_right_nonunit_cadence_tracker_repair.py
tests/test_lattice_bond_instrumentation.py
```

Checkpoint 1 (`04d2d31`) changed **only** the report — `git diff --name-only f7b6c97 04d2d31 -- edlab tests` returned nothing — so Part I was frozen and committed before any source was touched.

---

## 3. Correct repair accepted

The source repair itself is recorded as **correct**. Specifically:

- the accepted parent's empty-right fallback **conflated schedule position with actual sampled frame**
  (`right[0].frame if right else transition_index + 1`);
- the defect was **reproduced before modification**;
- at schedule `(0, 5, 11, 12)`, exhaustive enumeration of **4096** synthetic configurations produced
  **1295 global rejections**;
- **every** rejected configuration belonged to the disappearance group;
- **no** survival configuration was rejected;
- rejection was therefore **outcome-dependent**;
- after the repair, the same enumeration produced **zero** such rejection;
- the declared sample schedule now determines the actual right frame;
- **no new terminal-event taxonomy was needed**;
- lifecycle and completion source remained unchanged;
- all **seven** lifecycle-stack proof steps passed;
- all **four** horizon cases passed;
- approximately **29 000** repaired synthetic runs produced **zero** accidental `TERMINAL_AT_HORIZON`;
- the `TERMINAL_AT_HORIZON` guard was **separately shown to remain live** on a handcrafted
  `TrackingResult` that no tracker would emit;
- all **15** test-matrix cases passed;
- all **14** required mutants were killed;
- **808** legacy unit-cadence fixtures produced **zero** parent/repaired mismatch.

**These are mechanical synthetic qualification results only. They are not scientific findings about the
Stage-B worlds.**

---

## 4. Reason for insufficiency accepted

The decisive limitation is recorded as follows:

- the repaired path **requires an explicit `sampled_frames`**;
- `sampled_frames` still **defaults to `None`**;
- the default path **reproduces the original defect**;
- **no current production caller supplies the schedule**;
- all located `track_components(...)` call sites are **tests**;
- only the new repair suite opts into the corrected path;
- therefore the repository contains a **proven exit** from the trapdoor, but **the exit is not
  mandatory**;
- **no supported future family may rely on an optional safety mechanism.**

---

## 5. Adjudication of the split review

Part I §13, frozen at `04d2d31` before any source was touched:

> `TRACKER_REPAIR_QUALIFIED` · `TRACKER_REPAIR_INSUFFICIENT` · `STOP_TRACKER_REPAIR`.
>
> `TRACKER_REPAIR_INSUFFICIENT` if the tracker alone cannot close the survivorship mechanism without
> changing lifecycle or integration source. `STOP_TRACKER_REPAIR` on scientific-data access, engine
> execution, historical retrofit or scope violation. After any terminal disposition the only authorized
> next action is human review.

**Reviewer A's `FAIL` controls**, because the frozen Part I qualification rule required the survivorship
trapdoor **itself to be closed**, not merely an opt-in repair to exist.

**Reviewer B's `PASS` remains valid evidence** that the repair *semantics* are correct. It does **not**
override the mandatory-path requirement. Reviewer B's own OBS-1 — that the repair is opt-in and that no
in-tree caller opts in — is the evidence on which the frozen criterion fires, and Reviewer B correctly
recorded that the opt-in design was **forced by the allowlist, not chosen for convenience**.

The disagreement was not resolved by majority. It was resolved by the frozen rule.

---

## 6. Hash-tripwire interpretation

`test_23_bound_lifecycle_package_remains_byte_identical` **correctly fails** after the authorized change
to `instrumentation.py`.

This is **not an incidental regression** and **must not be hidden by editing the old qualification in
place**.

It proves that:

- the old lifecycle qualification remains **historically valid at its original commit**;
- its instrumentation hash is **no longer the current successor-branch hash**;
- a **successor** lifecycle qualification must be issued;
- the existing runner integration and hardening packages **cannot yet be claimed as formally current**
  on top of the repaired source.

Of the seven artifacts the tripwire pins, **six remain byte-identical**; exactly one differs, and it is
the file the repair had to change. The pin is a provenance assertion, not a runtime enforcement
mechanism, and nothing under `edlab/` reads it.

---

## 7. Claims not accepted

This human review does **not** claim that:

- the survivorship trapdoor is closed;
- the repaired path is mandatory;
- any real caller supplies the schedule;
- the lifecycle contract is currently requalified;
- the runner integration is currently requalified;
- the historical Stage-B runner is repaired;
- any scientific family is safe to run;
- the Stage-B result changed;
- Route E or Route G is authorized;
- any seed or preregistration may open.

---

## 8. Frozen scientific state

Unchanged by this decision:

- `STOP-LOCAL-CUT`
- `STOP-OWNERSHIP-IDENTIFIABILITY`
- `FINAL_STOP_ARCHITECTURE_CONFIRMED`
- `DEV_FEASIBILITY_FAIL`
- `AUDIT_INVALID`
- historical `FUTURE_LIFECYCLE_CONTRACT_QUALIFIED`
- historical `RUNNER_INTEGRATION_QUALIFIED`
- historical `HARDENING_QUALIFIED`
- `ARCHITECTURE_REVISE`
- Kovacs: `SCALAR_ONLY_FEASIBLE → STOP_PROSPECTIVE`

**"Historical" means valid for the exact source hashes and commits originally qualified. It does not mean
invalid or deleted.**

---

## 9. Next mission authorized

Exactly one successor mission is authorized:

### `MANDATORY_SAMPLED_FRAMES_LIFECYCLE_REQUALIFICATION_01`

It **may**:

1. remove the optional/default schedule path from the supported generic tracker API;
2. require every `track_components(...)` caller in the permitted synthetic stack to supply the
   authoritative sampled schedule;
3. update affected synthetic test call sites;
4. update the contract-test fixture that exercises the tracker;
5. replace the old hash-pin expectation with an explicit historical-versus-current binding test;
6. preserve the original qualification files unchanged;
7. create a successor lifecycle requalification package;
8. rerun and bind the complete permitted synthetic suites;
9. demonstrate that **no supported call sequence can invoke the generic tracker without an explicit
   schedule**;
10. demonstrate that disappearance at non-unit cadence remains **counted terminal information**;
11. define the remaining runner-integration requalification obligation.

It **must not**:

- modify `lifecycle.py`;
- modify `future_lifecycle_runner.py`;
- overwrite `FUTURE_LIFECYCLE_CONTRACT_00_QUALIFICATION.json`;
- rewrite any frozen report;
- run an engine;
- inspect historical scientific data;
- wire a real runner;
- requalify the runner integration in the same mission;
- open a family, preregistration or seed namespace;
- execute Routes E or G.

**Scope-expansion rule.** If making the schedule mandatory requires a production API change **larger than
removal of the optional path and direct call-site updates**, the mission must **freeze that expansion
before implementation** or return insufficient.

### 9.1 Successor qualification rule

The next mission must create new artifacts under a **successor identifier**, such as:

```
FUTURE_LIFECYCLE_CONTRACT_REQUALIFICATION_01
```

It **must not silently edit the historical `00` qualification.**

The successor package must bind:

- repaired `instrumentation.py`;
- unchanged `lifecycle.py`;
- updated synthetic tests;
- exact selectors and node IDs;
- source hashes;
- schedule-mandatory API;
- empty-right disappearance proof;
- old-versus-new qualification lineage;
- downstream requalification DAG.

Successful completion will qualify **only**:

- the mandatory schedule API;
- the repaired tracker;
- the lifecycle contract against the repaired tracker.

**Runner-integration requalification remains a later, separately human-authorized mission.**

---

## 10. Record scope

This decision record adds exactly one file and changes no existing file. It starts no requalification,
runs no engine, opens no scientific material, wires no runner, and allocates no seed.
