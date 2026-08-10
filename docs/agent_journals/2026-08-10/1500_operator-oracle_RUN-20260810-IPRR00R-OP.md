# IPRR00R operator/oracle subaudit journal

- Role: independent ETCMNFC operator and oracle red-team subagent.
- Run ID: `RUN-20260810-IPRR00R-OP`.
- Start time: 2026-08-10 14:47:25 +02:00.
- Starting Git branch: `audit/chatgpt-independent-red-team-roadmap-01r`.
- Starting Git commit: `55f4223dd6e965d5db36934f9ef0d96bfc344434`.
- Assigned scope: audit only the allowlisted ETCMNFC operator, gate and oracle blobs at
  `c5171b72f3ed2cdaba1968bdbd9ebf3776eab8d7`; create this journal and
  `ETCMNFC_OPERATOR_ORACLE_AUDIT_01R.md`; do not stage or commit.
- External path sentinel SHA-256:
  `044F9B86435C1DF8310717060C287BB0581A62901509F4E2BF5BE527620F2E12`.
- External allowlist SHA-256:
  `FF704DCE4F3AB81D2916D9418BC6B19AA50759B8395CB9F0B93EE97AED06A5A7`.

## Access boundary at start

No ETCMNFC blob has yet been opened by this subagent. Every content path will be presented to the external
sentinel before `git show`. Repository Python modules, scientific engines, worlds, runners, trajectories,
checkpoints, primary-ID allocations, and path names containing prohibited tokens remain unopened and unexecuted.
The parent reported that a commit-message name exposed a held-out allocation; it is classified L1, will not be
repeated here, and makes that held-out audit `NOT_AUDITABLE` without stopping this DEV/code audit.

## Running evidence log

### Important files read

All reads were Git blobs from `c5171b72f3ed2cdaba1968bdbd9ebf3776eab8d7`, after a successful path
sentinel invocation:

- `ETCMNFC/etcmnfc_protocol.json`;
- `ETCMNFC/etcmnfc_core.py`;
- `ETCMNFC/etcmnfc_gates.py` and `etcmnfc_gates_offline.json`;
- `ETCMNFC/etcmnfc_phaseC.py` and `etcmnfc_phaseC.json`;
- `ETCMNFC/etcmnfc_phaseC2.py` and `etcmnfc_phaseC2.json`;
- `ETCMNFC/etcmnfc_verify.py` and `etcmnfc_verify.json`;
- `ETCMNFC/REVIEW_1_NUMERICAL_ORACLE.md`;
- `ETCMNFC/REPORT_ETCMNFC.md`;
- `ETCMNFC/SHA256SUMS`.

No repository module was imported or executed. No raw scientific state, forbidden path, engine, world, runner,
trajectory, primary allocation, or held-out content was opened.

### Access classification

The allowlisted protocol/report prose exposed a name-based held-out allocation and geometry name. This is L1.
The exact values are intentionally omitted, and the dependent held-out audit is `NOT_AUDITABLE`. No content,
result, internal held-out manifest, size, timestamp, or content hash was opened; safe DEV/code work continued.

### Reproducible actions and outputs

1. Recalculated SHA-256 values from Git blob bytes and compared twelve operator/oracle/report artefacts with
   `ETCMNFC/SHA256SUMS`: twelve matches, zero mismatches.
2. Parsed `etcmnfc_gates_offline.json`: 60 rows, 60 true booleans; the twelve gate-family counts and four
   manifests were enumerated. Parsed Phase C: 22 rows, 21 true, one F10 failure. Parsed Phase C2: 14/14 stored
   true. Parsed verifier output: 19/19 stored true.
3. Reimplemented the frozen boolean matching and opposed it to an independent brute-force enumerator over
   19,266 unique-ID cases: zero divergence.
4. Tested malformed pair-list schemas: duplicate sites raise, but unequal `I/J` lengths and one empty side are
   silently accepted/truncated by the audited loop.
5. Tested exact rational arithmetic: a finite permutation preserved the exact unweighted sum; `NaN` raised
   `ValueError`; infinities raised `OverflowError`.
6. Built independent F2 adversaries. The intended mask passed; flipping a non-unit-kappa material cell failed;
   removing a unit-kappa material cell passed; adding a unit-kappa outside cell also passed.
7. Built independent F5 ledger-schema adversaries. An extra axis, an extra call, a duplicate row and a wrong
   duplicate followed by the correct row all passed the Phase C2 reconstruction logic.
8. Parsed `etcmnfc_verify.py` with AST. `G` has zero load uses; `SHA256SUMS`, the protocol and `hashlib` are not
   used. A three-row malformed Phase C2 object with truthy non-boolean values passed the V5 predicate; a
   negative start count passed the cap; an empty log passed the DEV-only universal quantifier.
9. Recomputed each stored manifest's base hash and internal site-ID mapping. All base hashes, IDs, disjointness
   and counts agreed. Hashing the complete record failed by construction, and changing a derived delta did not
   affect its embedded manifest hash.
10. Audited the source-named gates. The per-block O1 identity hook is an unconditional no-op. Phase C2 O1 runs
    matching twice on identical copies. First-pass F2/F5/F6 are the recorded vacuous gates. Phase C2 F5 rebuilds
    the applied `c` buffer but does not rebuild the applied `N` buffer.
11. Searched the allowlisted core, result JSONs and report for the reported three-operator/orientation layer:
    zero occurrences of `orientation` and no triplet of operators. AST inventory found one explicit intervention,
    `transpose`; therefore a reported three-oriented-operator result is absent from the target commit.

Representative command forms:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File `
  C:\Users\tommy\Documents\IPRR00R_BOOTSTRAP\Assert-IPRR00RSafe.ps1 `
  -Kind Path -Value ETCMNFC/<allowlisted-path>
git -C C:\Users\tommy\Documents\ising-v3-iprr00r-audit `
  show c5171b72f3ed2cdaba1968bdbd9ebf3776eab8d7:ETCMNFC/<allowlisted-path>
```

The independent tests ran as `python -` from standard input, without a repository import or scientific-state
write.

## OBSERVED

- The valid-input byte swap and unweighted sum theorem are correct.
- The matching replica agreed with brute force in 19,266 exhaustive small cases under unique IDs.
- The published result files and selected sources are internally hash-consistent with the committed
  `SHA256SUMS`.
- The first-pass vacuous oracles are retained and explicitly superseded.
- The replacement F2 predicate accepts at least two wrong masks.
- The replacement F5 parser accepts extra and duplicate ledger rows.
- The verifier loads the 60-row result but never uses it, and does not validate hashes or schemas.
- The raw DEV values required to independently reproduce the stored per-block results were outside this audit's
  permitted content scope.
- No three-oriented-operator layer exists in the audited core/results/report, despite that claim appearing in the
  audit mandate's reported-result description.

## INFERRED

- ETCMNFC contains a defensible software operator only under strict, currently implicit input preconditions.
- `60/60`, `14/14` and `19/19` are committed row counts, not independent certifications.
- `ON_NATIVE_FLUX_OBSERVER = VALID_PASSIVE_EXACT` is too strong as a bundled verdict because the exact-mask
  suboracle fails and the ledger schema is permissive.
- The honest correction `matching objective value-blind; eligibility state-dependent` should be retained.

## HYPOTHESIS

A strict schema plus an actually independent verifier will preserve the valid permutation/matching result while
turning several current PASS rows into explicit schema or oracle failures. This is a tooling repair hypothesis,
not a hypothesis about transport.

## WHAT WOULD FALSIFY THIS?

- A counterexample with unique identifiers in which the audited matching differs from a complete brute-force
  lexicographic maximum would falsify the conditional matching verdict.
- A proof that the model's kappa map is biconditional with the alive mask at every valid state, together with a
  new oracle checking both directions and all cells, would falsify the current F2 failure in scope. The current
  source checks only one direction plus one selected corruption.
- Persisted, allowlisted raw DEV arrays and ledgers, independently parsed and recomputed by code not importing
  ETCMNFC, could upgrade the per-block verdicts from `INDETERMINATE`.
- A strict verifier rejecting non-boolean PASS values, missing/extra rows, malformed counts, hash mismatches and
  every ledger corruption would falsify the verifier failure after a new committed revision; it does not change
  the verdict on the audited commit.

## Failures and dead ends

- One `git show | Select-Object` preview returned exit code 1 after the consumer closed the pipe; the blob was
  subsequently parsed in full via `subprocess.check_output`, with SHA-256 and JSON census recorded.
- One no-op shell invocation contained only variable assignment due to a mistyped temporary commit string; it
  opened no path and changed no state.
- A final exact-path tracking check used `--error-unmatch` under `ErrorActionPreference=Stop` and stopped after
  confirming the deliverable was untracked. It was repeated safely with `git ls-files --stage -- <exact path>`.

## Decisions

- Do not score DEV numerical claims without raw inputs.
- Credit the operator theorem separately from its physical `w_i=1` interpretation.
- Classify the first-pass named properties as `FAKE_PASS`, not merely weak tests.
- Classify replacement F2 and fail-closed verification as `FAIL`; classify F5/F6 narrowly rather than discarding
  their substantive local checks.
- Preserve the L1 exposure without reproducing its values and continue only the safe code/DEV audit.

## Unresolved risks

- `full_state_sha` relies on a fixed field tuple; completeness cannot be checked without the state schema.
- The asserted actual storage weights remain outside the evidence proved by the consequence test.
- The committed independent review has no separately committed review code or raw-output transcript, so its
  independence and numerical rederivations are not independently attestable here.
- The matching exhaustiveness test covered all small matrices but is not a machine-checked proof for arbitrary
  size; the source argument and the empirical oracle agree.

## End state and handoff

- End time: 2026-08-10 14:59:35 +02:00.
- Ending Git branch: `audit/chatgpt-independent-red-team-roadmap-01r`.
- Ending Git commit observed: `d3491f5dda7bced17920de68624262cd9e976b10` (the parent advanced the audit
  branch while this subaudit was running; this agent did not create that commit).
- This agent staged and committed nothing.
- Created, untracked at handoff:
  - `ETCMNFC_OPERATOR_ORACLE_AUDIT_01R.md`, 277 lines, SHA-256
    `8F661F56D889E4C8EA20784FD07C9C606AF7EFC5580CF0CE887CC55E0067A5EF`;
  - this journal.
- Exact next action: parent should review the deliverable, then include both audit-only files in the coherent
  IPRR00R commit and propagate the F2/verifier failures into the claim ledger and final report.
