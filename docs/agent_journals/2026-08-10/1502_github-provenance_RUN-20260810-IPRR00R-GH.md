# Agent journal: GitHub provenance and workflow safety

- Role: independent Git/GitHub provenance and stewardship auditor
- Run ID: `RUN-20260810-IPRR00R-GH`
- Parent mission: `RUN-20260810-1441-IPRR00R`
- Start time: 2026-08-10 14:47 +02:00
- Current checkpoint time: 2026-08-10 14:52:39 +02:00
- Starting Git state: local branch `audit/chatgpt-independent-red-team-roadmap-01r` at freeze commit
  `55f4223dd6e965d5db36934f9ef0d96bfc344434`; remote audit ref absent.
- Current Git state: same branch at sentinel amendment 1
  `d3491f5dda7bced17920de68624262cd9e976b10`; no file staged, committed, pushed, or PR-created by this agent.
- Assigned scope: Git/GitHub metadata, the explicitly allowlisted workflow blob, audit-package provenance; no
  scientific code/content execution and no held-out, near, checkpoint, trajectory, engine, or primary-allocation
  path access.

## Important files read or changed

Read:

- `INDEPENDENT_AUDIT_FREEZE_01R.md`
- external `IPRR00R_ALLOWLIST.json` and `Assert-IPRR00RSafe.ps1`
- `.github/workflows/nasi-ci.yml` only after sentinel amendment 1 allowed that exact path

Created (not staged or committed by this agent):

- `GITHUB_PROVENANCE_AND_STEWARDSHIP_01R.md`
- this journal

## Actions and reproducible checks

1. Used the GitHub connector first to query repository metadata, branches, commits, and pull requests.
2. Used the unauthenticated public GitHub API only for release, tag, workflow, and workflow-run metadata after
   connector coverage was exhausted. `gh` 2.97.0 is installed but no CLI host authentication is configured.
3. Verified exact local commit objects and direct parents with `git show -s`.
4. Verified ancestry using `git merge-base --is-ancestor`.
5. Queried exact remote refs with `git ls-remote`; no broad ref enumeration was used.
6. Fetched only the known remote-main commit object, without checkout or tree materialization, to compare workflow
   blob identity and ancestry.
7. Compared `.github/workflows/nasi-ci.yml` blob IDs at remote main, ETNBFC, ETCMNFC, freeze, and amendment 1.
8. Opened the workflow only after the corrected sentinel returned `IPRR00R_PATH_ALLOWED`.
9. Did not execute any repository code, action, workflow, container, scientific verifier, or reproduction target.

Representative metadata commands:

```powershell
git merge-base --is-ancestor <earlier> <later>
git ls-remote origin refs/heads/<exact-authorized-name>
git rev-parse '<commit>:.github/workflows/nasi-ci.yml'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File `
  C:\Users\tommy\Documents\IPRR00R_BOOTSTRAP\Assert-IPRR00RSafe.ps1 `
  -Kind Path -Value '.github/workflows/nasi-ci.yml'
git show 'HEAD:.github/workflows/nasi-ci.yml'
```

## OBSERVED

- ETPC, EEFCA, ETNBFC, and ETCMNFC form a direct local parent chain.
- IPRR00R branches from ETNBFC, not ETCMNFC.
- The named remote scientific and audit refs are absent; current remote main contains none of the five local commits.
- GitHub structured search finds none of the exact scientific/audit commits and no related PR.
- GitHub reports zero releases and zero tags.
- The sole workflow is active and unconditionally triggers for both pushes and pull requests.
- The workflow executes repository DEV/reproduction/figure/container commands.
- The same workflow blob is present in every relevant local/remote state.
- No `SHA256SUMS` existed at the checkpoint; package verification is pending.

## INFERRED

- A push of the audit branch can launch outcome-generating repository execution even if the diff contains only
  Markdown/audit files.
- Opening a draft PR would add another workflow trigger and cannot repair the unsafe push.
- The scientific chain is locally coherent but is not public evidence.
- Local bundle/archive publication is the only currently eligible stewardship path.

## HYPOTHESIS

A later audit-only remote publication could be safe if workflow routing is changed and independently confirmed so
that the exact audit ref/pathset produces no run. This is a future stewardship hypothesis, not authorization to
change the workflow now.

## WHAT WOULD FALSIFY THIS?

- For the push-safety verdict: an active remote workflow configuration, in force before ref creation/update, proving
  that the exact audit branch and audit-only paths cannot schedule any job, plus a zero-run post-push check.
- For the local-only verdict: a discoverable GitHub ref/tag/release/PR binding the exact commits, or proof that those
  commits are ancestors of remote main.
- For package integrity: successful independent bundle verification and archive re-extraction bound by final
  SHA-256 values.

## Failures and dead ends

- Initial direct invocation of the sentinel was blocked by Windows execution policy.
- Invoking it with `-ExecutionPolicy Bypass` exposed a real normalization bug: `.TrimStart('./')` removed the leading
  dot from `.github`, denying the explicitly allowlisted workflow. The workflow was not opened at that point.
- Parent audit recorded and committed a narrow normalization correction as amendment 1. Traversal and prohibited
  path probes still deny. Only after that correction passed was the workflow opened.
- `gh auth status` reports no authenticated host, so no CLI write or authenticated API operation was attempted.
- HTTP `HEAD` requests to commit endpoints returned 422 and were not treated as evidence; structured connector
  exact-SHA searches and ref/ancestry checks were used instead.

## Decisions

- `NO_PUSH`: current unconditional `push` workflow violates the frozen publication gate.
- `NO_DRAFT_PR`: current unconditional `pull_request` workflow adds a second scientific execution trigger.
- `LOCAL_PACKAGE_REQUIRED`: final Git bundle and archive must replace remote publication for this mission.

## Unresolved risks and handoff

- Parent must create the final commit, bundle, archive, and `SHA256SUMS` without pushing.
- This agent should be recalled after packaging to append independent bundle/archive verification. Until then the
  package line in the deliverable remains `PENDING`.
- No other agent should describe the local scientific chain or IPRR00R audit as public.
