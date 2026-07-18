# REPOSITORY-HYGIENE-00 journal

Role: primary repository-maintenance and recovery agent
Run ID: RUN-20260718-0310-REPOSITORY-HYGIENE-00
Start: 2026-07-18 approximately 03:10 Europe/Paris
End: 2026-07-18 approximately 13:53 Europe/Paris
Starting Git: main at f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77, heavily dirty
Ending Git: maintenance/repository-hygiene-00 at the commit containing this finalized journal; exact tip recorded in handoff
Experiment: NONE — repository maintenance only

## Assigned scope

Recover the dirty primary checkout, repair malformed refs, stop ordinary
Windows worktree failures caused by historical cache names, audit worktree
registrations, preserve all scientific history, and leave a clean primary
checkout. The directed-causal-pair worktree and branches were protected.

## Important files read

- AGENTS.md
- docs/RESEARCH_CHARTER.md
- docs/PROJECT_STATE.md
- docs/DECISION_LOG.md
- docs/EXPERIMENT_INDEX.md
- docs/RUN_INDEX.md
- docs/agent_journals/2026-07-13/2130_expgt03_the_null_that_could_not_fire.md
- docs/consolidation/SIGNSAFE_FREEZE_MANIFEST.json
- docs/consolidation/FINAL_HARDENING_REPORT.md

## Important files changed

- .gitignore
- scripts/New-IsolatedWorktree.ps1
- tests/test_new_isolated_worktree_helper.py
- docs/maintenance/REPOSITORY_HYGIENE_00_REPORT.md
- docs/maintenance/REPOSITORY_HYGIENE_00_RECOVERY_MANIFEST.json
- docs/maintenance/REPOSITORY_HYGIENE_00_WINDOWS_PATHS.md
- docs/RUN_INDEX.md
- docs/PROJECT_STATE.md
- this journal
- removal from the maintenance tip of 34 generated results/_tomo_cache files

No experiment, V5, 03G, frozen raw, scientific code, scientific protocol, or
scientific conclusion was modified.

## Actions

1. Captured porcelain status, ignored/untracked inventories, binary patches,
   refs, worktrees, raw malformed-ref bytes, object residue, and fsck output in
   a timestamped directory outside the repository.
2. Preserved the exact index and meaningful working state as two verified
   commits on rescue/primary-dirty-20260718-031627.
3. Verified rescue blob equality, exclusions, tree equality, secret heuristic,
   and remote tip.
4. Archived the valid c8a8b354 history, then moved only malformed loose refs
   and duplicate temporary-object residue to external evidence.
5. Preserved five stale zero-byte lock files after read-only ownership checks.
6. Created maintenance/repository-hygiene-00 from f3921a4.
7. Removed all 34 current tomo cache artefacts from that tip, added the precise
   ignore rule, helper, and four synthetic tests.
8. Qualified the helper against the real f3921a4 tree.
9. Copied and verified all 523 new-to-HEAD files externally before removing
   their primary copies.
10. Restored 350 tracked non-cache paths from the original HEAD archive,
    reattached the exact index entries, and switched the primary checkout to
    the already-pushed maintenance branch.
11. Created and removed only run-owned clean validation worktrees.
12. Independently audited V5, 03G, their raw registries, the 03G reproduction,
    and the downstream frozen raw family through Git objects.
13. Re-ran show-ref, for-each-ref, all-ref object resolution, full fsck,
    scientific subtree diffs, focused tests, diff-check, and remote read-back.
14. On resumed closure, found one last zero-byte background maintenance lock
    with no Git process owner, preserved it externally, and issued verified
    final recovery inventory v2 covering 947 files.

## Reproducible commands

~~~powershell
git status --porcelain=v2 --branch --untracked-files=all
git worktree list --porcelain
git show-ref
git for-each-ref --format='%(refname)%09%(objectname)%09%(objecttype)'
git fsck --full --no-reflogs

& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -m pytest -q tests\test_new_isolated_worktree_helper.py
.\scripts\New-IsolatedWorktree.ps1 -Repository 'C:\Users\tommy\Documents\ising v3' -Path 'C:\Users\tommy\Documents\ising-v3-historical-helper-final-test-00' -Commitish f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77
~~~

The exact recovery and restoration commands are in the external RESTORE.md.

## OBSERVED

- Original primary status: 350 staged deletions, five staged modifications,
  19 unstaged deletions, five unstaged modifications, and 744 untracked files.
- 221 untracked files were HEAD-identical; 523 were new to HEAD.
- The external snapshot preserves all 523 new paths with zero hash mismatch.
- The rescue branch preserves 476 meaningful new paths and all five tracked
  working-state files; 47 generated/unsafe paths remain external only.
- refs/heads/probe/tmp01 embedded a valid commit after an error string. The
  commit is now reachable through refs/archive/probe-tmp01-recovered-20260718.
- Exactly 19 historical paths were Windows-invalid, all under one generated
  cache directory.
- No pre-existing worktree registration was stale or prunable.
- The protected worktree grew while the maintenance ran; another agent was
  demonstrably active.
- A normal maintenance-tip Windows worktree and a sparse historical worktree
  both validated exactly.
- Final pre-report ref audit: 75 refs, zero unresolved targets, show-ref and
  for-each-ref exit 0.
- Final pre-report fsck: exit 0, zero errors; 11 dangling commits, 10 dangling
  trees, and 32 dangling blobs preserved.

## INFERRED

- The primary dirt was not one coherent change and could not safely be erased
  wholesale. It required two preservation channels: a reviewable rescue branch
  and a complete external snapshot.
- The broken ref was a write-residue problem, not lost history: the embedded
  object was valid and recoverable.
- Ignoring the cache directory alone would prevent recurrence but could not
  repair historical Windows checkout. Sparse materialization plus exact-tree
  verification is required.
- The protected worktree's dirt is independent scientific activity, not a
  maintenance defect. Cleaning it would violate the coordination boundary.

## HYPOTHESIS

Future ordinary worktrees from the maintenance tip will materialize normally
on Windows, and historical commits with only documented tomo-cache invalid
paths will materialize through the helper without changing their index tree.

## WHAT WOULD FALSIFY THIS?

- A normal worktree at the maintenance tip failing on a Windows-invalid path.
- git write-tree in a helper-created historical worktree differing from the
  requested commit tree.
- Any skip-worktree entry not belonging to the detected invalid path set.
- Any V5/03G/frozen raw object ID or inventory hash differing from the recorded
  canonical baseline.
- A remote maintenance or rescue ref differing from its local tip.
- An external snapshot entry failing its SHA-256 check.

## Failures and dead ends

- Three controlled temporary-index rescue attempts failed: an old index lock,
  a Windows-invalid Test-Path call, and a malformed PowerShell path separator.
  Their indexes/path lists were preserved externally. Independent commit
  verification then passed.
- Initial helper tests failed because Git protected the synthetic NTFS-invalid
  fixture, a one-line PowerShell function result auto-unrolled to characters,
  native stderr became a terminating PowerShell 5.1 error, and Test-Path
  rejected the invalid name. Each was corrected and the final four tests pass.
- The first rescue push returned HTTP 408 after the server accepted the exact
  ref. A read-back found the correct remote tip; a later non-forced retry was
  rejected only because the same ref already existed.
- The tracked-restore script encountered a second zero-byte index lock after
  materializing the restore archive. No writer owned it; it was preserved.
  Explicit batch staging then completed. One initial batch partially succeeded
  before .synctest's ignore rule caused an exit; exact forced staging of only
  the recorded HEAD paths completed the restoration.

## Decisions

1. Preserve rather than delete all ambiguous primary content.
2. Keep the 47 unsafe/generated paths external; do not push the secret-flagged
   runner.
3. Preserve the valid probe history through an archive ref; never restore the
   malformed loose-ref bytes.
4. Remove generated tomo cache files only from the new maintenance tip; never
   rewrite historical commits.
5. Do not prune any worktree or object.
6. Do not update DECISION_LOG or EXPERIMENT_INDEX because no scientific
   decision or experiment state changed.

## Unresolved risks

- Historical commits still contain Windows-invalid cache names by design and
  require the helper on Windows.
- The protected scientific worktree remains actively dirty under its owner.
- The external recovery directory contains a secret-flagged file and must not
  be bulk-added to Git.
- The final report commit cannot contain its own hash; exact local/remote final
  tips are recorded in the final handoff.

## Handoff

Use the primary checkout normally from maintenance/repository-hygiene-00. For a
historical commit, use scripts/New-IsolatedWorktree.ps1 with a new empty target.
For recovery, prefer rescue/primary-dirty-20260718-031627 and the external
RESTORE.md. Do not merge or create a pull request as part of this mission.

Exact next authorized action: human review of the maintenance report and,
separately, continuation by the owner of the protected directed-causal-pair
worktree.
