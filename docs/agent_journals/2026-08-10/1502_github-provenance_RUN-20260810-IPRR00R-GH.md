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

## Recall checkpoint: independent P1 package verification

- Recall interval: 2026-08-10 15:15-15:22:41 +02:00
- Package target: substantive audit commit `e0561989db5de1b278b3b27d1e035afe6f3c6e75`
- Ending branch state before this append: `audit/chatgpt-independent-red-team-roadmap-01r` at amendment-2 commit
  `e49cb988825e00cc6c19af621cb974c475e89f95`
- Fresh verification root: `C:/Users/tommy/Documents/IPRR00R_VERIFY_GH_E056_20260810_1505`
- Repository mutations by this agent: none; only this journal and the assigned GitHub deliverable were appended,
  without staging, commit, push, or PR.

### Reproducible package checks

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath <exact-package>
git -C <fresh-bare-repo> bundle verify <exact-bundle>
git bundle list-heads <exact-bundle> refs/heads/audit/chatgpt-independent-red-team-roadmap-01r
git -C <fresh-bare-repo> fetch --no-tags <exact-bundle> `
  refs/heads/audit/chatgpt-independent-red-team-roadmap-01r:refs/heads/verified-iprr00r
git -C <fresh-bare-repo> fsck --full --strict --no-dangling
git -C <fresh-bare-repo> rev-parse '<commit>:<allowed-archive-path>'
git hash-object --no-filters -- <freshly-extracted-file>
```

### OBSERVED

- ZIP: 71,788 bytes; SHA-256
  `908fb9a88798edfeb7998376023ad9d35487f565d7a4b7e6b7a4d54e68f6c976`.
- Bundle: 618,754,826 bytes; SHA-256
  `a95449da74ed7890e5a32d40b0e1b9640370503ac8d50fae7a6d9bd8aabe5392`.
- Bundle verification reported complete history and exactly the expected audit ref at `e0561989...`.
- Fresh bare fetch produced the expected commit; full strict fsck returned exit 0 with no output.
- Archive enumeration found 15 files and one directory entry; there were no duplicate, traversal, absolute, or
  symlink entries.
- After amendment-2 path closure, all 15 archive paths passed the sentinel and all 15 extracted files matched their
  `e0561989...` Git blobs byte for byte.
- `SHA256SUMS` had 14 unique entries covering exactly the 14 other files; 14/14 hashes matched.
- GitHub CLI version 2.97.0 is installed; `gh auth status` returned exit 1 and no authenticated host.

### INFERRED

- P1 is a valid, complete local carrier for the substantive audit commit `e0561989...`.
- P1 cannot certify later amendment 2 or this attestation because they postdate its payload commit.
- Credential availability would not make a push eligible while the unconditional scientific workflow remains active.

### WHAT WOULD FALSIFY THIS?

- Any size/hash mismatch on the preserved P1 package bytes.
- Failure to advertise/fetch `e0561989...`, a bundle prerequisite, or a strict fsck diagnostic.
- Any archive path not allowlisted, any traversal/duplicate/symlink, any file differing from its commit blob, or any
  missing/incorrect `SHA256SUMS` entry.

### Failures and dead ends preserved

- The first ZIP file-count check treated a directory entry ending in a Windows separator as a file and reported 16;
  using `ZipArchiveEntry.Name` correctly distinguished 15 files plus one directory. No content had been extracted.
- The corrected enumeration then found amendment 1 absent from the allowlist. The verifier stopped before opening or
  extracting it and reported the blocker.
- Amendment 2 added only the two literal audit-amendment paths and requalified the sentinel. Verification resumed
  after commit `e49cb98...`.
- A later script assumed `.NET` exposed `System.IO.Path.GetRelativePath`; this host does not. The final check used an
  absolute-root prefix proof plus relative substring and completed successfully.

### Decision and handoff

- `P1_BUNDLE = PASS`
- `P1_ARCHIVE = PASS`
- `P1_SHA256SUMS = PASS`
- `FINAL_P2_REPACKAGE = REQUIRED`
- `NO_PUSH = UNCHANGED`
- `NO_DRAFT_PR = UNCHANGED`

Parent should commit this attestation, create final P2 packages containing amendment 2 and the attestation, and run
the same package-verification protocol on P2 before calling the final wrappers verified.
