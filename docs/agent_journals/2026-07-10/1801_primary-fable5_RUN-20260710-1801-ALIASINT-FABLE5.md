# Agent Journal — RUN-20260710-1801-ALIASINT-FABLE5

## AGENT / ROLE

Primary operational agent (Claude **Fable 5**). Resume the causal-intervention handoff for CORE V0
diagnostic survivors `{0, 52}`: freeze the sham-controlled, alias-rejecting matched-branch protocol,
self-audit it under Fable 5, validate the implementation, execute, and take the CORE V0 decision.

## MODEL

- primary model: **claude-fable-5**
- remained on Fable 5: **yes** (model lock honored; no Opus 4.8; no auto-router escalation used)
- subagents: none launched (audit performed directly under Fable 5)

## RUN ID

`RUN-20260710-1801-ALIASINT-FABLE5`

## START TIME

2026-07-10 18:01 +02:00

## END TIME

In progress.

## STARTING GIT STATE

- Repository: `C:\Users\tommy\Documents\ising v3` (mounted).
- Branch: `main`; HEAD `313ce951de3d0eefefa8432a3bb7764a674180fa`; `origin/main` identical.
- Prompt reported last SHA `4f0368e`; the real repo had advanced to `313ce95` (Codex continued). Repo is source of truth.
- Working tree: 71 result files show as "modified" but `git diff --ignore-all-space` is EMPTY; working copies are CRLF, committed blobs are LF (verified: 75 CR vs 0 CR; no `.gitattributes`, no `core.autocrlf`). These are a **benign CRLF/LF artifact of the Windows mount, not a data change**. NOT committed. This corroborates the reported "raw data intact".
- One untracked file: the previous session's in-progress delegated auditor journal `1721_holdout04-audit_...md` (left unfinalized when Codex exhausted quota). Not rewritten (AGENTS.md).

## RUNTIME LOCK / NON-OVERLAP

- Found `.runtime/scheduled_task.lock` owned by `RUN-20260710-1609-EXP02REC` (the quota-exhausted Codex primary), start 2026-07-10T14:09Z, starting_head `622ba9c`.
- Verified owner reached a genuine committed checkpoint: `622ba9c` is an ancestor of HEAD; HEAD==origin/main; zero non-CRLF working-tree changes; the Cowork scheduler shows no concurrent emergent-dynamics run.
- The mounted FS initially forbade `unlink`; enabled cowork file deletion, then released the orphaned lock by its matching run-id (policy-compliant: genuine finish, not age) and acquired the mutex for my run/experiment. Lock now held by `RUN-20260710-1801-ALIASINT-FABLE5` / `ALIAS-INTERVENTION-COREV0-20260710-001`.

## ASSIGNED SCOPE

LAW 0 / LAW 52 -> frozen causal protocol -> same-state matched branches (CONTROL / SHAM / PERTURBED)
-> alias audit -> CORE V0 decision. No EXP03 before this test. No threshold changes. No composite score.

## IMPORTANT FILES READ

- `AGENTS.md`, `docs/RESEARCH_CHARTER.md`, `docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md` (D-001..D-015),
  `docs/EXPERIMENT_INDEX.md`, `docs/RUN_INDEX.md`.
- Journals `1609_primary...` and `1721_holdout04-audit...` (both left "In progress").
- Code: `edlab/state.py`, `specs.py`, `substrates/particle_dynamics/engine.py`, `observables/phenotype.py`,
  `observables/continuity.py`, `entities/detection.py`, `entities/tracking.py`, `experiments/baseline.py`,
  `experiments/audit_candidates.py`, `cli.py`, `runtime_lock.py`.

## OBSERVED (recovery)

- EXP02 verified state (from durable docs + manifests): 900/900 runs, 648,740 measurements; tau float-key
  fragmentation was a derived-aggregation bug (D-013), raw/P/M/hashes intact; nine 2/3 screening laws
  `{0,12,35,52,73,94,209,225,298}`; direct diagnostics 47 rows / 22 endpoints, 0/47 reject occupancy/look-alike alias.
- HOLDOUT04: 45/45; frozen >=2/5 fresh-seed gate retains `{0,52}` (law 0 seeds {3002,3004}; law 52 seeds {3001,3003});
  seven laws rejected; both survivors alias-unresolved (D-014, D-015).
- No frozen causal protocol file exists. `ALIAS-INTERVENTION-COREV0-20260710-001` is DESIGN_ONLY. The intended
  direction (PROJECT_STATE NEXT ACTION + D-015) is a preregistered intervention that **displaces a detected
  organization off its former spatial site**, with an exact sham, to reject stationary occupancy / look-alike flux.
- Independent reproduction (my code, sandbox Python 3.10 + numpy 2.2.6): the exact frozen cross-cadence eligibility
  rule enrolls **precisely** law 0 seeds {3002,3004} and law 52 seeds {3001,3003} and censors all other holdout
  seeds — a clean differential cross-check that reproduces the HOLDOUT04 disposition from an independent path, and
  advances the hypothesis the 1721 auditor left unfinished. Existing suite: **38/38 pass** in my environment.

## INFERRED (recovery)

- The survivors are diagnostic only; P/M alone are alias-compatible. A same-state matched-branch displacement test
  is the minimal causal design that can separate "identity = spatial site (occupancy)" from "identity = constituents".

## HYPOTHESIS

- A (individuality): the organization is carried by its constituents; displacing them off-site carries the phenotype
  to the new site and the old site does not immediately continue "the same" entity.
- B (occupancy/look-alike): the phenotype is bound to a site; displacing constituents leaves the old site to
  regenerate the phenotype from turnover particles while the moved constituents disperse.
- Prior expectation (skeptical, per charter): B is more likely; 0/47 direct rows rejected the alias.

## WHAT WOULD FALSIFY THIS?

- See frozen falsifiers F1..F5 in `docs/experiments/ALIAS_INTERVENTION_COREV0_01_PROTOCOL.md` (to be frozen this run).

## ACTIONS / COMMANDS (running log)

- Verified CRLF artifact; transferred runtime lock; reproduced HOLDOUT04 eligibility independently; ran 38/38 suite.

## FAILURES / DEAD ENDS

- Mount forbids `unlink` until cowork deletion is enabled (resolved).

## DECISIONS

- Pending: freeze ALIAS-INTERVENTION protocol (this run).

## UNRESOLVED RISKS / HANDOFF / ENDING GIT STATE

In progress.
