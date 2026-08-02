# FUTURE-LIFECYCLE-CONTRACT-00 independent scope red-team journal

- Role: independent adversarial reviewer; anti-retrofit and lifecycle-closure gate
- Run ID: `FUTURE-LIFECYCLE-CONTRACT-00-REDTEAM-0251`
- Start time: 2026-07-19 02:51 Europe/Paris
- End time: 2026-07-19 03:07:59 +02:00
- Starting Git branch: `codex/future-lifecycle-contract-00`
- Starting Git HEAD: `389dac1127e3035cdf195c1905965832a299ad6d`
- Ending Git state: HEAD `869c5b2f0f27c759417be80580c85a368b17c897`; shared worktree contains the
  reviewed future-only implementation, tests, schema, specification and agent-journal changes pending the lead's
  final commit. This reviewer changed only this journal.
- Assigned scope: inspect only the generic tracker/detector and schema sources explicitly provided later, the two committed Stage-B/autopsy reports, synthetic fixtures, and the new lifecycle-contract implementation. Do not inspect or enumerate current-family raw data, manifests, trajectories, candidates, per-world metadata, result paths, or the forbidden Stage-B implementation/reproducer.

## Important files read

- `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B_REPORT.md`
- `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B_AUTOPSY_REPORT.md`
- `edlab/substrates/lattice_bond/instrumentation.py` (only the exact generic detector/tracker definitions and event
  construction selected by the source allowlist)
- `tests/test_lattice_bond_instrumentation.py` (only exact generic tracker lifecycle tests)
- `docs/individuation/FUTURE_LIFECYCLE_CONTRACT_00_SOURCE_ALLOWLIST.json`
- `docs/individuation/FUTURE_LIFECYCLE_CONTRACT_00_SPEC.md`
- `edlab/substrates/lattice_bond/lifecycle.py`
- `tests/test_future_lifecycle_contract.py`
- `docs/individuation/FUTURE_LIFECYCLE_CONTRACT_00_SCHEMA.json`
- Code-review skill instructions (outside the repository)

No current-family shard, filename inventory, per-world metadata, raw input, trajectory, candidate record, manifest, result, Stage-B implementation, or Stage-B reproducer was opened or listed.

## Actions and reproducible commands

- Verified branch, HEAD, clean status and recent commit subjects with read-only Git commands.
- Verified the two exact allowed report paths with `Test-Path` and read only those reports.
- Formulated pre-implementation adversarial kill switches and sent them to the lead agent.
- Ran two exact focused synthetic test passes using
  `C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe -m pytest -q tests/test_future_lifecycle_contract.py`:
  first `43 passed`, then `44 passed` after the second concurrency regression was added.
- Ran a hand-built in-memory horizon/silent-end probe: the valid non-unit horizon fixture produced
  `RIGHT_CENSORED_AT_HORIZON`; the pre-horizon event omission produced
  `SILENT_PRE_HORIZON_TERMINATION`.
- Reproduced an initial late-target race showing that `os.replace` overwrote a concurrently created target. The lead
  replaced it with destination-absent `os.link` and added a preservation regression.
- Reproduced a second exclusive-open race showing that unconditional exception cleanup deleted another publisher's
  newly created partial. The lead added explicit `owns_partial` tracking and a regression proving the competing
  partial bytes survive.

## Preliminary kill switches

1. Reject any lifecycle contract that infers termination from observation absence.
2. Reject unless every observed track has exactly one machine-verifiable terminal row.
3. Reject a pre-horizon terminal row without a contemporaneous explicit tracker event.
4. Reject an end-of-horizon survivor unless it is explicitly marked as right-censored.
5. Reject conflicting or duplicate terminal events, unknown terminal kinds, dangling successors, temporal mismatches, and invalid early censoring.
6. Require complete parent and successor accounting for every split or merge; successors remain independently subject to terminal closure.
7. Require an explicit run-level zero-track closure when no tracks exist.
8. Require canonical, schema-versioned lifecycle rows bound by counts and digests to the complete future track/event input.
9. Reject a helper-only validator: future publication/`COMPLETE` status must be transactionally gated on validation success.
10. Reject any dependency on current-family artifacts or any terminal decision using physics, candidate, outcome, or scientific-classification fields.

## Allowed generic-source audit

Exact allowed source reviewed:

- `edlab/substrates/lattice_bond/instrumentation.py`, event vocabulary, tracker records, event records, `TrackingResult`, and `track_components` only;
- `tests/test_lattice_bond_instrumentation.py`, generic detector/tracker lifecycle tests only;
- frozen future-only source allowlist and contract specification.

The generic tracker has a future-only cadence limitation that must not be hidden: when the right detector frame is
empty, `track_components` assigns the transition frame as `transition_index + 1` rather than obtaining it from an
explicit sample schedule. Consequently, a non-unit-cadence disappearance can carry a temporally incorrect
`DISSOLUTION` event. This observation is a generic source property only and is not attributed to the closed family.
The lifecycle validator must reject such a mismatch against its explicit schedule. Hand-built non-unit-cadence
events alone cannot qualify generic tracker integration for that case.

Further implementation acceptance conditions:

- The dissolution-backed state must be named/documented as a detected-track ending, not physical death or material
  destruction.
- Every internal continuation must have exact point/event/assignment coverage; canonicalization must not silently
  deduplicate malformed rows.
- Event target IDs must be checked against target component assignments rather than assumed to align positionally.
- A source-only helper can qualify contract mechanics, but cannot honestly be described as an installed publication
  gate until a future-family writer makes it non-bypassable. The report must preserve this integration obligation.
- An atomic writer must refuse a conflicting existing lifecycle file and must never publish partial or invalid bytes.

## OBSERVED

- The committed autopsy report records a fail-closed lifecycle-integrity failure while expressly declining to identify a historical world, law, trajectory mechanism, or scientific cause.
- The Stage-B disposition remains an accepted feasibility failure and is not changed by this mission.
- The frozen future-only specification uses an explicit sampled-frame schedule and a closed terminal algebra, which
  is structurally adequate provided the implementation validates the full point/event/assignment linkage.
- The final implementation validates exact assignment coverage, onset and continuation chronology, closed event
  polarity/arity, reciprocal lineage, one terminal event or explicit horizon witness, unresolved provenance, no
  afterlife, terminal-count bijection, canonical bytes, source/terminal digests and independent byte verification.
- The lifecycle input digest binds the explicit schedule plus the complete track/event/assignment inputs used by the
  contract. Association edges are deliberately outside this lifecycle input and are not mislabeled as being bound.
- The publication primitive now fails without overwriting a late target and without deleting a partial owned by a
  competing publisher.

## INFERRED

- A future contract must treat termination as explicit data, not as a post-hoc interpretation of missing observations.
- A standalone schema or validator is insufficient unless the future publication state machine cannot bypass it.
- Within the persisted generic tracker model, a future package admitted through qualification and independent byte
  verification cannot contain a silent per-track ending: each track has one event-backed terminal state or an
  explicit right-censor row, otherwise qualification fails.

## HYPOTHESIS

A generic post-tracker closure ledger plus a binding fail-closed publication gate can make lifecycle completeness machine-verifiable without changing detector/tracker association or using scientific outcomes.

## WHAT WOULD FALSIFY THIS?

- A generic tracker transition that cannot be represented without inference from current-family data.
- A publication path that can still emit or mark a future family complete after missing, duplicate, contradictory, or temporally invalid terminal rows.
- A synthetic valid split/merge/censoring lifecycle that cannot be expressed without importing physical or scientific-classification fields.

## Failures and dead ends

- One read-only PowerShell existence check had a parser error before reading any file; it was corrected with an array-wrapped pipeline. No scope expansion occurred.
- The worktree has no local `.venv`; one attempted invocation failed before Python ran. All actual synthetic checks
  then used the repository virtual environment at the exact path recorded above.
- Both publication races found during red-team review were fixable source defects and were repaired with focused
  regressions before this verdict.

## Decisions

- Do not discover source paths through broad repository listing. Wait for exact generic source paths selected by the lead.
- Do not claim that any generic silent-termination path caused the accepted historical failure.
- **Final independent verdict: PASS for source-only and synthetic qualification.** This is not a scientific result,
  not a retrospective repair, and not evidence about the cause of the accepted family failure.

## Unresolved risks

- Non-unit cadence with an empty right detector frame remains a future integration limitation of the current generic
  tracker source. The contract correctly rejects the resulting mismatched event; it does not silently manufacture a
  terminal state.
- No future-family writer exists in this mission. Therefore the atomic contract primitive is qualified, but an
  installed non-bypassable family-level `COMPLETE`/analysis gate is not claimed. A future entirely new family must
  bind its writer and independent verifier to this contract before execution or publication.
- Hard-link publication assumes a filesystem that supports same-directory hard links. A future preflight must treat
  lack of that capability as a publication failure, not add an overwriting fallback.

## Handoff

`PASS` for the stated source-only and hand-built synthetic qualification. The lead may include this journal in the
final coherent commit. The exact next authorized lifecycle action is human review; any later entirely new family
must predeclare schedule handling, resolve or constrain the generic empty-frame/non-unit-cadence limitation, and
make lifecycle qualification plus independent byte verification a binding pre-publication state transition.

## Superseding delta review — 2026-07-19 03:15:44 +02:00

The PASS above was superseded when a later independent synthetic reviewer found a partial-path substitution race
that this review had missed. The earlier verdict must not be quoted as the final review disposition without this
correction.

The repaired exact publication path was re-reviewed. It now:

- creates a unique same-directory partial with `tempfile.mkstemp`;
- retains the exclusively created descriptor open through destination-absent `os.link` publication;
- records the owned `(st_dev, st_ino)` identity from the descriptor;
- compares the published target identity, current partial-path identity and canonical target bytes against the owned
  descriptor/payload before returning success;
- removes a path only when its current identity matches the owned partial, preserving substituted or foreign bytes;
- rejects a swapped-link publication while preserving both the foreign target and foreign source bytes;
- canonicalizes unknown-event and collision diagnostics so input/internal permutations produce identical violation
  records.

The exact focused command was rerun after this repair:

`C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe -m pytest -q tests/test_future_lifecycle_contract.py`

Observed result: **50 passed in 0.21 s**. `git diff --check` over the exact allowed implementation, tests, schema,
specification and this journal also passed.

### Superseding independent verdict

**PASS** for source-only and synthetic qualification at HEAD
`ec494b4c428b394a8f3e8165898711261ab0840c`.

This superseding PASS retains every prior claim boundary: it is not a historical diagnosis or retrofit; the closed
family remains non-diagnostic; the generic empty-right-frame/non-unit-cadence mismatch is rejected rather than
repaired; and no future-family `COMPLETE`/analysis gate is claimed installed until a new family binds both this
publication primitive and independent canonical-byte verification.
