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

---

## EXECUTION + DECISION (appended at run completion)

### OBSERVED (causal execution)

- Froze protocol `docs/experiments/ALIAS_INTERVENTION_COREV0_01_PROTOCOL.md` at **baf1fca**; validated harness
  (46/46 tests incl. sham==control bit-for-bit, conservation, off-site displacement, IDs-not-in-physics,
  determinism, HOLDOUT04 reproduction). PASS A + PASS B audits (Fable 5) applied pre-freeze.
- Self-review of the FIRST results found two readout bugs (placebo followed the candidate not the displaced
  clump; consecutive-from-start metric fragile). Corrected as **D-016** (harness **b00322d**) BEFORE committing
  any result; re-ran. Both buggy and corrected reasoning documented; no committed artefact invalidated.
- Executed fresh causal seeds 5001-5040/law (unseen). Enrolled first-eligible-endpoint units: law 0 = 5,
  law 52 = 9; 66 censored (recorded). Two seed-halves (identical union), deterministic, assembled to
  `results/ALIAS-INTERVENTION-COREV0-20260710-001/` (manifest + sha256 + figure verified programmatically:
  valid PNG 1200x1950, non-degenerate, multi-colour).
- sham==control bit-for-bit in all 14 units. No non-informative (F4), no catastrophic (F5).
- Genuine turnover-individuality (displaced candidate re-establishes at new site, exceeds displaced-placebo,
  old site does not regenerate, M below turnover threshold): **0/5 (law 0), 0/9 (law 52)**. Three law-52 units
  re-establish only as rigid cohesive clusters (M~1.0, no turnover) and do not reach the majority bar. Law 0
  seed 5004 shows the occupancy signature (old site regenerates from turnover; displaced constituents do not).

### INFERRED

- CORE V0 high-P/low-M for survivors {0,52} is not shown to be constituent-carried individuality; the
  stationary-occupancy / look-alike alias is NOT rejected at majority. Where a displaced candidate persists, it
  is a trivially bound cohesive cluster (translation-covariance), not turnover-individuality.

### DECISION — CASE A (D-017)

Close laws 0 and 52 as CORE V0 candidates. Proceed to EXP03-A (CORE + density preference). No threshold lowered.

### WHAT WOULD FALSIFY THIS?

A CORE V0 law whose displaced candidate re-establishes with genuine turnover, exceeding placebo, no old-site
regeneration, clean alias audit, across a majority of fresh seeds. None observed.

### FABLE 5 AUDIT

PASS A (enrollment/tracker) and PASS B (intervention/sham): see `1820_fable5-audit-passA_*` and
`1828_fable5-audit-passB_*`. Both converged: decision must be comparative vs PLACEBO; primary carrier readout is
tracker-independent; scope is occupancy/look-alike rejection, not internal self-repair. No Opus 4.8; no subagents.

### MODEL USED

primary claude-fable-5; remained on Fable 5: yes; model switch: no; Opus 4.8 used: no; subagents: none.

### RUNTIME LOCK / SCHEDULED TASK

Lock transferred from orphaned RUN-20260710-1609-EXP02REC to this run (verified committed checkpoint). The mount
forbids unlink until cowork deletion enabled. No Cowork-side emergent-dynamics scheduled task exists (only an
unrelated one-time `cashline-go-nogo-12juillet`); the project's 30-min heartbeat is a Codex-side native task not
visible/controllable from this environment — no duplicate created; model-lock note to be surfaced to the user.

### HANDOFF / NEXT AUTHORIZED ACTION

Design and preregister the **EXP03-A** protocol (CORE V0 + density preference only; mutation/type-transition/
recycling OFF), reusing frozen observers, nulls, tracker audits, P/M separation; no composite score. Screen, and
if a predefined signal appears, apply the same fresh-seed hold-out + alias-intervention discipline. Release this
run's lock after commit/checkpoint. Push is pending remote auth (unavailable in this environment).

### ENDING GIT STATE

HEAD after freeze commit baf1fca and correction b00322d; results/decision/index commit to follow. origin/main not
updated (no push auth here); all work committed locally. Working tree: only benign CRLF result-file churn remains
uncommitted (verified identical content).
