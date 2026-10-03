# Roadmap

Snapshot of **2026-10-03**. It describes `main` at `f382dbf` (merge of PR [#30], 2026-08-05) and
the five open pull requests. Sources: `README.md`, `AGENTS.md`, `docs/RESEARCH_CHARTER.md`,
`docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md`, `docs/EXPERIMENT_INDEX.md`, `docs/RUN_INDEX.md`,
the decision files in `docs/individuation/`, the latest journal, the open PRs and the Git history.

**This roadmap authorizes nothing.** It is a reading aid. Where it disagrees with
`docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md`, a decision file or the latest journal, those
prevail. No scientific step starts without an explicit owner decision recorded in the repository.

## 1. Question and rules

- Question (`docs/RESEARCH_CHARTER.md`): *"Can automatically sampled local laws produce mesoscopic
  entities whose organization persists under progressive constituent turnover and may later
  recover after a controlled perturbation?"* Working phrase: **persistent dynamical individuality
  under constituent turnover**, "a target for operationalization, not a conclusion".
- `P(tau)` and `M(tau)` are kept as a joint distribution; no composite identity or memory score is
  authorized. A negative result stays negative; thresholds are not loosened to manufacture
  candidates.
- Working rules are in `AGENTS.md`: reading order, scheduled-run lock
  (`python -m edlab.runtime_lock`), one journal per agent, the 12-step end-of-run checklist, and
  *"Do not invent a direction merely to keep the automation busy."*

## 2. Where `main` stands (2026-08-05)

The active line is **Route E** on the lattice-bond substrate (`edlab/substrates/lattice_bond/`).

| Step | Record | Outcome |
|---|---|---|
| Second substrate | D-097–D-100; PRs #12–#14 (2026-07-18/19) | Stage A mechanics qualify (D-098); Stage B fixed family DEV-infeasible (D-099); autopsy `AUDIT_INVALID` (D-100) |
| Route selection | `FUTURE_PROSPECTIVE_READINESS_ARCHITECTURE_01_DECISION.json` (#18/#19); `FUTURE_PROSPECTIVE_MEASUREMENT_FEASIBILITY_AND_ROUTE_SELECTION_01R_DECISION.json` (#20) | `ARCHITECTURE_REVISE`, then `MEASUREMENT_FEASIBILITY_REVISE`; no route selected |
| Route E selected | `FUTURE_PROSPECTIVE_AXIS_CONVENTION_AND_FRAME_CLOSURE_01S_DECISION.json` (#22/#23, 2026-08-04) | `AXIS_FRAME_CLOSURE_01S_ROUTE_E_SELECTED`, primary route E |
| Pre-run blockers | `FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_DECISION.json` (#24–#28) | `human_review = PENDING`, `scientific_run_authorized = false`; the record says it "must never be summarised as 'the pre-run blockers are closed'" |
| Execution boundary | DECISION_LOG entry `FUTURE_ROUTE_E_EXECUTION_BOUNDARY_CORRECTION_00` (#29) | one dedicated entry `run_route_e(...)` and admission `verify_route_e_run(...)`; next action "one independent human review" |
| Pilot | `ROUTE_E_PILOT_READINESS_00_DECISION.json`; journal `docs/agent_journals/2026-08-05/0030_route-e-pilot_ROUTE-E-PILOT-READINESS-00.md` (#30, 2026-08-05) | `PILOT_DESIGN_RISK_OBSERVED` |

The pilot, from its journal and decision file:

- base: A1-R5 commit `eccd46bc` (`docs/PROJECT_STATE.md`: three external STOPs open, 23 of the 41
  test obligations not implemented); owner-authorised minimal closure (gates G1–G6), then ONE
  exploratory pilot of 24 laws × 2 initial conditions = 48 worlds;
- 48/48 worlds completed, 0 technical incidents, engine re-executions byte-identical;
- 48/48 mechanically ineligible (`WRAPPING_COMPONENT_PRESENT`): only 6/48 wrap at enrolment; the
  median first wrapping frame is 16, the first sampled frame after t = 0;
- labelled fraction at enrolment: mean 0.745 (range 0.671–0.811), conserved for the whole run;
- diagnostic at the non-frozen detection threshold 0.60 (9 eligible tracks): union residuals
  0.744–0.904; focal residuals of the same tracks 0.0, 0.0, 2e-6, 8.4e-5, 0.0018, 0.155, 0.221,
  0.691, 0.733;
- `confirmatory_run_authorized = false`, `preregistration_authorized = false`,
  `human_review = PENDING`; no `k` computed, the 42/9 thresholds not evaluated;
- deferred, not closed: `STOP_PINNED_VERIFIER_UNAVAILABLE`, `STOP_SOURCE_AUTHORITY_UNFROZEN`,
  `STOP_NAMESPACE_AUTHORITY_UNFROZEN`, the A2 public inclusion proof, canonical confirmatory 67×2
  enforcement, hostile-filesystem hardening, full confirmatory preregistration.

Handoff of the latest journal, verbatim: *"ONE owner decision, on the two observed design risks,
before any preregistration mission. Nothing else is authorised."*

## 3. Now: decisions for the owner

Only 3.1 is named by the latest journal as the next authorized action. 3.2 and 3.3 are open PRs
waiting for the owner; this file does not rank them.

### 3.1 Pilot design risks

- (a) The frozen eligibility rule against the wrapping component the engine produces in 48/48
  worlds.
- (b) The union enrolment convention against a component-focal cohort. The journal: "making it
  primary is a design decision for the owner, not for this mission".

### 3.2 Stacked Route E PRs: #31 ⊂ #32 ⊂ #33

All three target `main`, and each one contains the previous one.

| PR | Branch | Opened | Commits / files | Adds over the previous PR |
|---|---|---|---|---|
| [#31] | `codex/route-e-empty-right-nonunit-disk-closure-00` | 2026-08-07 | 4 / 30 (+4 605 −1 180) | BLS verifier install and Route E guard (optional extra `route-e`, `requirements-route-e-lock.txt`); PRB 1–4 and HR-10 operational closure; tracker baseline relevance closure; empty-right non-unit disk closure |
| [#32] | `dev/route-e-source-sink-00` | 2026-08-07 | 8 / 61 (+10 473 −1 180) | four DEV experiments run on 2026-08-07: anti-stagnation feasibility sweep, non-merging causal bridge, LAW16 occupancy frontier, single-disc source–sink |
| [#33] | `audit/chatgpt-independent-red-team-roadmap-01r` | 2026-08-26 | 29 / 452 (+154 992 −1 180) | 16 Route E DEV and audit commits (2026-08-07 → 08-10; the last one is "STOPPED IN QUALIFICATION … SCIENTIFIC_RESULT = NOT_TESTED") and an independent red-team audit in French (5 commits) |

Merging #33 as it stands brings in all 29 commits. The decision is the merge order, a partial merge
or a supersession.

All three branch from `199f29e`, the head of #29. They do not contain A1-R3, A1-R4, A1-R5 or the
pilot, which #30 brought to `main` on top of that same commit. A local trial merge of each into
`main` (`git merge-tree`, 2026-10-03) conflicts in
`edlab/substrates/lattice_bond/future_route_e_admission.py` and `future_route_e_execution.py`, and
for #33 also in `docs/RUN_INDEX.md`.

The audit in #33 concludes `ETCMNFC_PRIMARY_C_N = NOT_TESTED` with
`STOP_REASON = JOINT_ENDPOINT_STRUCTURALLY_MISSPECIFIED`. Its `NEXT_SCIENTIFIC_ROUTES_01R.md`
recommends, in order:

1. an append-only correction and archival consolidation of ETCMNFC;
2. an independent protocol review of `WARPED-SCALE-GEOMETRY-00`, without inferring eligibility from
   its name;
3. if the owner still values the local component-contour question, a preregistration of Route 1
   under a new identifier (it changes the question);
4. if the owner insists on the literal component–bath question, Route 3 only, at its full
   new-founding cost;
5. Route 2 never presented as A/B attribution; Routes 6 and 7 not recommended; Route 4 secondary;
   Route 5 as enabling metrology, not a causal result;
6. `QUANTUM-BASIN-00` reviewed on its own preregistered merits, after the multiscale decision.

These are recommendations in an unmerged PR, not decisions. `ETCMNFC`, `WARPED-SCALE-GEOMETRY-00`
and `QUANTUM-BASIN-00` appear only in that audit's files and journals. None of their protocols or
code is on `main` or on an open PR branch.

### 3.3 Manuscript PRs outside `main`

- [#34] (draft), `astra/ising-life-manuscript-v2-final-seal-01` →
  `archive/ising-life-flcr01-recovered-06c5923`: Ising Life source-response manuscript V2. Its
  description says "internally audited and ready for critical reading" and claims no peer review,
  submission, DOI or merge.
- [#35], `astra/edl-flagship-audit-01` → `recovery/astra-edl-tbrt02-20260905`: bounded
  causal-memory paper and a September recovery audit, disposition
  `FLAGSHIP_CLAIM_NOT_SUPPORTED_BUT_B_DELIVERED`. Its description: "The remaining author action is
  to read the manuscript and decide whether to pursue a specialist-journal submission."

Neither targets `main`. This file does not describe their base branches.

## 4. Now: hygiene steps (no scientific content)

Test suite on `main`, 2026-10-03 (Linux, Python 3.11.15, `pip install -e '.[dev]'`, numpy 2.4.6,
pytest 8.4.2): **1 468 passed, 27 failed, 22 skipped**. By error type:

- 16 × `ModuleNotFoundError: No module named 'scipy'` (`test_chemotaxis` 2, `test_motile_polar` 2,
  `test_multistable_phenotype` 5, `test_scaffold` 7);
- 7 × `configuration_error`, "no verifier supplied; PRB-6 requires a maintained verifier"
  (`test_route_e_beacon_verifier` 5, `test_future_route_e_pre_run_integration_00` 2), which the
  pilot attributes to `STOP_PINNED_VERIFIER_UNAVAILABLE`;
- 4 × `TypeError: track_components() missing 1 required keyword-only argument: 'sampled_frames'`
  (`test_lattice_bond_stage_b`).

With `scipy==1.15.3` added, the version pinned in `requirements-lock.txt`: **1 483 passed,
12 failed, 22 skipped**. Fifteen of the 16 `scipy` failures pass. The sixteenth,
`test_motile_polar.py::test_scramble_preserves_all_declared_invariants_and_destroys_organization`,
then fails with `AssertionError: support overlaps its own translate: displacement would not
conserve mass`.

These 12 match the pilot's by group. The pilot recorded 1 476 passed, 12 failed and 22 skipped in
its own environment: the 7 verifier failures and 5 inherited ones. The execution boundary
correction record declares the 5 by node ID: the 4 `test_lattice_bond_stage_b` tests and the
scramble test. Here they fail with the causes recorded in §9.3 of the pre-run blocker closure
report. The pilot records do not list the 7 verifier node IDs. This run collected 7 more tests than
the pilot (1 517 against 1 510) and counted 7 more passes; the difference was not investigated.

Each step below fits in one PR. Steps marked *owner wording* change governance text and need the
owner's words.

| Step | Done when |
|---|---|
| H1. Declare `scipy` in `pyproject.toml`, or mark the tests that need it. It is imported by `edlab/substrates/chemotaxis/diagnostics.py`, `edlab/substrates/motile_polar/observables.py` and `edlab/experiments/sc_hsi/core.py`, and pinned to 1.15.3 in `requirements-lock.txt`. With that version installed, 15 of the 16 `scipy` failures pass. | A fresh `pip install -e '.[dev]'` gives no `ModuleNotFoundError`. |
| H2. Adapt the 4 `test_lattice_bond_stage_b` tests to the mandatory `sampled_frames` argument. Keep their node IDs: `test_historical_13b` in `tests/test_future_route_e_execution_boundary_00.py` pins them "so a rename or a deletion cannot pass as a repair". Check PR #31 first: it edits this file. | The 4 tests pass under the same node IDs, or the owner records why one stays. |
| H3. The other 8 failures have recorded causes but no repair. The pilot attributes the 7 verifier failures to `STOP_PINNED_VERIFIER_UNAVAILABLE`, which its decision lists in `deferred_confirmatory_stops`. The scramble failure is raised by the guard in `swap_support` (`edlab/experiments/exp_mo_00_gate0.py:62`); §9.3 of the pre-run blocker closure report records it, and no repair was authorized there. PR #31 installs a verifier and edits both verifier test files; whether it fixes the 7 was not checked. | Each failure is repaired, or the owner records why it stays. |
| H4. CI: `.github/workflows/nasi-ci.yml` runs on every push and pull request. It runs the NASI and point_cert reproduction (Python 3.10 and 3.12, plus a container job) but never `pytest tests/`. The audit in #33 flags the unfiltered trigger. | CI runs `pytest tests/` once H1–H3 are done; the owner has decided the trigger scope. |
| H5. README: it still presents `CORE V0` particle dynamics, retired by D-021, as the current substrate, and its commands are PowerShell only. | The README points to the current state and has POSIX commands. |
| H6. *Owner wording*: the charter's "Current substrate and causal ladder" and the "Authorized sequence" in `AGENTS.md` still describe the CORE V0 → EXP03-C ladder, exhausted by D-020/D-021. | The text matches the current line or is marked historical. |
| H7. After 3.1, record the pilot in `docs/PROJECT_STATE.md` and `docs/DECISION_LOG.md`. PROJECT_STATE was last changed on 2026-08-04: its `pilot_authorized = false` predates the pilot, and its NEXT ACTION and CURRENT QUESTION sections date from earlier phases. DECISION_LOG has no pilot entry. Update `docs/individuation/A1R5_RNG_MAPPING_OWNER_DECISION.md` too: it still reads `PENDING`, while the pilot record shows `owner_decision = SELECT_OPTION_1_TOP_53_BITS` applied. | The state files agree with the latest decision record. |
| H8. `docs/RUN_INDEX.md`: move the six rows that sit after a blank line, in 5- and 3-column formats, into the 9-column table. | The file holds one well-formed table. |

## 5. Later

- The question has not changed. The sequence in `AGENTS.md` ended with the Particle Dynamics
  decision (D-020/D-021), and every later line of work began with an explicit decision. Nothing
  beyond the latest handoff is pre-authorized.
- Written candidates, none authorized:
  - the ordering in #33's `NEXT_SCIENTIFIC_ROUTES_01R.md` (section 3.2);
  - `ROUTE_E_REPLICATION_DENSITY_PREREGISTRATION_00`, the preregistration mission named in the
    pre-run blocker closure record, which does not authorize it;
  - earlier mission roadmaps in `docs/individuation/`:
    `DOWNSTREAM_ORDER_READER_01_NULL_MECHANISM_ROADMAP.md`,
    `FUTURE_PROSPECTIVE_MEASUREMENT_FEASIBILITY_AND_ROUTE_SELECTION_01R_ROADMAP.md`,
    `FUTURE_PROSPECTIVE_READINESS_ARCHITECTURE_00_ROADMAP.md`,
    `FUTURE_PROSPECTIVE_READINESS_ARCHITECTURE_01_ROADMAP.md`.

## 6. History

The Git history of `main` starts on 2026-07-14 (root commits `b473ded`, the CRD-03 freeze, and
`d0f47b6`, 2026-07-15). DECISION_LOG entries start on 2026-07-10, so the first decisions predate
the history.

### Decisions (`docs/DECISION_LOG.md`)

| Decisions | Line of work | Outcome |
|---|---|---|
| D-001–D-016 | setup, `CORE V0` particle dynamics, EXP02 regime map, hold-outs | D-015 freezes the HOLDOUT04 survivors {0,52} for an alias-rejecting intervention |
| D-017–D-021 | alias intervention, EXP03-A/B/C | survivors closed (CASE A, D-017); EXP03-A/B/C negative (D-018–D-020); Particle Dynamics retired for the current question (D-021) |
| D-022–D-027 | Flow-Lenia | blind maps negative (D-023, D-025); first causal survivors (D-026) withdrawn (D-027) |
| D-028–D-036 | open reaction-diffusion, Gray-Scott | closed Flow-Lenia retired (D-028); candidate withdrawn (D-035); Gray-Scott retired, causal methodology R1–R6 (D-036) |
| D-037–D-046 | motile polar, chemotactic, multistable droplet and scaffold substrates | each retired (D-037, D-040, D-042, D-044, D-046) |
| D-047–D-077 | EXP-GT metrology: observers against a ground-truth benchmark | observers retired (D-058, D-065, D-067, D-069); both fingerprint arms pass (D-072); pilot preflight fails (D-073); branch closed (D-077) |
| D-078–D-085 | causal-response decomposition (CRD) | sign-safe instrument passes (D-084); large hold-out fails, publication blocked (D-085) |
| D-086–D-088 | LCI turnover preseals 03C and 03G | prospective 03G execution certifies Outcome B without ownership (D-088) |
| D-089–D-096 | access structure, directed causal pair, deep checkpoint, ownership identifiability, causal addressability | each stops; D-095 retains an unadmitted candidate |
| D-097–D-100 | INTERVENTIONAL-INDIVIDUALITY-00 on lattice-bond | see section 2 |
| un-numbered | `FUTURE_ROUTE_E_EXECUTION_BOUNDARY_CORRECTION_00` | execution boundary corrected once (#29) |

D-001–D-100 are dated 2026-07-10 → 2026-07-19. D-057, D-059, D-061 and D-062 do not exist, and
D-096 is written before D-095. From 2026-08-02 on, decisions are kept as decision files in
`docs/individuation/` (readiness architecture 00 and 01, route selection 01R, 01S, pre-run blocker
closure 00, execution boundary correction 00, the A1-R5 RNG mapping dossier, the pilot). The log
has only one later entry, the un-numbered boundary correction.

### Merged pull requests (`git log --first-parent --merges main`)

| PRs | Merged | Subject, from the branch names |
|---|---|---|
| #1–#5 | 2026-07-16 | LCI causal confirmation, merge-incident audit, non-merging confirmation, turnover final seal 03L, authorization contract 03J |
| #6 | 2026-07-17 | LCI turnover prospective 03G-001 |
| #7 | 2026-07-17 | paper: persistence without ownership (05) |
| #8–#10 | 2026-07-18 | downstream order reader: prospective seal (#8 and #9, same branch), null-mechanism audit (#10) |
| #12–#14 | 2026-07-18/19 | interventional individuality 00: Stage A (#12), Stage B (#13 and #14, same branch) |
| #15–#16 | 2026-08-02 | empty-right non-unit cadence tracker repair; mandatory `sampled_frames` lifecycle requalification (stop review) |
| #17–#21 | 2026-08-03 | owned pipeline runner (human review); readiness architecture 01 and its human review; measurement feasibility and route selection 01R (human review); paper: persistence without ownership v1 |
| #22–#29 | 2026-08-04 | axis convention and frame closure 01S and its human review; Route E pre-run blocker closure 00, its human review, revisions 1 and 2, authorized integration; execution boundary correction 00 |
| #30 | 2026-08-05 | Route E pilot readiness 00 (merge `f382dbf`, the current `main`) |

PR #11 is not among the merges.

---

To refresh this file, re-read the same sources and keep it descriptive: state what the records say
and cite them.

[#30]: https://github.com/Mythmaker28/emergent-dynamics-lab/pull/30
[#31]: https://github.com/Mythmaker28/emergent-dynamics-lab/pull/31
[#32]: https://github.com/Mythmaker28/emergent-dynamics-lab/pull/32
[#33]: https://github.com/Mythmaker28/emergent-dynamics-lab/pull/33
[#34]: https://github.com/Mythmaker28/emergent-dynamics-lab/pull/34
[#35]: https://github.com/Mythmaker28/emergent-dynamics-lab/pull/35
