# REPOSITORY-HYGIENE-00 maintenance report

Status: COMPLETE — PRIMARY CHECKOUT CLEAN AND RECOVERABLE

Date: 2026-07-18
Repository: C:\Users\tommy\Documents\ising v3
Maintenance branch: maintenance/repository-hygiene-00
Starting branch and HEAD: main at f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77
Implementation commits:

- 02e6224eddd3d33f363aa3b66ca535d6f63fd0bb
- b7506433f14f2643dfbdc16149084afd414ad8a4

This was repository maintenance only. No world or scientific engine was
initialized. No scientific definition, result, conclusion, V5 file, 03G file,
or frozen raw result was edited.

## Outcome

The primary checkout is clean on maintenance/repository-hygiene-00. Normal
Windows checkout of the maintenance tip succeeds. Historical commit f3921a4
can be materialized with the new sparse helper while retaining its exact full
index tree and excluding exactly the 19 Windows-invalid cache paths.

All pre-existing worktree registrations were preserved. No registration was
prunable. The protected directed-causal-pair worktree was not modified. It was
actively changing under another agent throughout this run, so it cannot
truthfully be described as clean; this maintenance run certifies only that it
was untouched here.

No reset --hard, git clean, force push, history rewrite, destructive rebase,
object pruning, worktree prune, or git gc was used.

## Exact starting inventory

The durable original inventories are under:

C:\Users\tommy\Documents\ising-v3-recovery\REPOSITORY-HYGIENE-00-20260718-031627

Primary starting state:

| Item | Observed |
|---|---:|
| branch | main |
| HEAD | f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77 |
| origin/main | e17f431c7c1aab8ad9bfeb3420a8c5022e311553 |
| staged deletions | 350 |
| staged modifications | 5 |
| unstaged deletions | 19 |
| unstaged modifications | 5 |
| untracked files | 744 |
| untracked bytes | 268,975,022 |
| ignored files | 13,566 |
| ignored bytes | 994,156,768 |
| registered worktrees | 13 |
| missing registered directories | 0 |

The five MM paths were .gitignore, docs/CAPABILITY_MATRIX.md,
docs/DECISION_LOG.md, edlab/substrates/ctrans/evaluator.py, and
edlab/substrates/ctrans/manifests.py.

Of the 744 untracked files, 221 were byte/filter-identical copies of paths
present at HEAD and 523 were new to HEAD. The main untracked groups were:

| Group | Files | Bytes |
|---|---:|---:|
| subset_b415503.tar | 1 | 175,093,760 |
| results | 151 | 41,615,344 |
| _to_delete | 21 | 19,666,648 |
| docs | 342 | 16,475,326 |
| outputs | 2 | 7,530,558 |
| subset_lci_b415503.tar | 1 | 2,713,600 |
| lci_subset_53fd2b6.tar | 1 | 2,334,720 |
| experiments | 67 | 1,873,682 |

Ignored content was dominated by results (5,588 files, 705,718,804 bytes) and
.venv (7,696 files, 282,041,177 bytes). It was left machine-local and ignored.

Exact inventory commands:

~~~powershell
git status --porcelain=v2 --branch --untracked-files=all
git status --ignored --porcelain=v2 --branch
git diff --cached --binary
git diff --binary
git worktree list --porcelain
git show-ref
git for-each-ref --format='%(refname)%09%(objectname)%09%(objecttype)'
git ls-tree -r -l HEAD -- results/_tomo_cache
git fsck --full --no-reflogs
~~~

## Recovery evidence

The external directory contains 945 inventoried files totalling 358,776,620
bytes, excluding the inventory file itself. Every entry was rehashed with zero
mismatches.

Final inventory:

- file: final_recovery_sha256.json
- SHA-256: 9e5abb49febc39b53e44f25e2e0e15d98b7d26a2f4cc6d2d392197b1790d872e

Tracked-state evidence:

- tracked_staged_full_index_binary.patch
- tracked_unstaged_full_index_binary.patch
- tracked_combined_from_HEAD_full_index_binary.patch
- tracked_noncache_head_restore.zip
- tracked_noncache_head_restore_manifest.json

Untracked-state evidence:

- external_recovery_manifest.json hashes all 744 original untracked files;
- untracked_snapshot_manifest.json verifies all 523 new-to-HEAD files;
- untracked_snapshot contains those 523 files, 255,855,456 bytes, with zero
  hash mismatches.

One file, experiments/individuation/turnover_prospective_runner.py, triggered
the assignment-secret heuristic. It was deliberately excluded from Git and is
available only in the external snapshot pending manual review.

## Rescue branch

Branch: rescue/primary-dirty-20260718-031627

- 401212c4f377280fdaee0d80022381aacdf39273 preserves the exact captured index
  tree cd969152f00358e36d0d702a906e4a1d4e3fef2e.
- 0c2b7b5952ee7eee533e9d5124c1d42e2287e9f5 adds the verified meaningful
  working state, tree c57ed22b9199863ee373f0b77eea893ceb1b505e.
- 476 selected new paths and the five tracked working-state paths match their
  captured bytes.
- 47 excluded new paths and all 19 invalid cache names are absent.
- largest rescue blob: 15,182,123 bytes.
- remote tip was independently read back as
  0c2b7b5952ee7eee533e9d5124c1d42e2287e9f5.

The first HTTP upload timed out after the server accepted the ref. A subsequent
read-back proved the remote ref already existed at the exact local tip; no
force push was used.

## Ref repair

Two malformed loose refs were present:

1. refs/heads/probe/tmp01 contained 125 bytes: an unlink warning followed by
   c8a8b354f10e0988adff4264bf0b1fdffcdf19c9. Raw SHA-256:
   bc7cc41b686267e08cadd706ac6c2cf93267de9ec12387114f9658fb4d2f2fe8.
2. refs/heads/.probe contained test plus a newline. Raw SHA-256:
   f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2.

The embedded c8a8b354 commit is valid and has parent e17f431c. It was preserved
as:

refs/archive/probe-tmp01-recovered-20260718

The malformed raw files were moved to external recovery. A 162-byte temporary
object named tmp_obj_T8KiR3 was proven byte-identical to the proper loose object
and was also moved to recovery; no Git object was deleted.

Initial fsck exit 10 was explained by the two malformed refs. Dangling commits,
trees, and blobs were recorded but not deleted. After repair, show-ref,
for-each-ref, log --all, and fsck enumerate normally. The archive ref makes the
c8a8b354 history reachable.

Four zero-byte stale locks were preserved externally after verifying that no
writer owned them: the original HEAD.lock, index.lock, objects/maintenance.lock,
and a second index.lock encountered during the controlled primary restoration.
They must not be restored.

## Windows-invalid cache paths

Commit f3921a4 contains 19 paths with the forbidden Windows character vertical
bar under results/_tomo_cache. It also contains 15 validly named generated
cache files there. The maintenance tip removes all 34 cache artefacts from the
current index and adds the precise ignore rule:

results/_tomo_cache/

No historical commit was rewritten. The complete path list and helper contract
are in REPOSITORY_HYGIENE_00_WINDOWS_PATHS.md.

The helper:

scripts/New-IsolatedWorktree.ps1

- refuses an occupied or already registered target;
- resolves the requested commit before mutation;
- fails closed on any undocumented Windows-invalid path outside
  results/_tomo_cache;
- creates the worktree with --no-checkout;
- excludes only the invalid historical cache paths through non-cone sparse
  checkout;
- verifies HEAD, exact index tree, exact skip-worktree set, and clean status;
- performs a non-force transactional rollback when a post-registration
  verification fails.

## Primary cleanup method

Cleanup was recoverable and path-explicit:

1. Hash and patch evidence was captured before state changes.
2. The exact index and meaningful working state were committed to the rescue
   branch and verified.
3. All 523 new-to-HEAD files were copied to external recovery, rehashed, and
   only then removed from the primary path.
4. The 350 non-cache tracked paths were materialized from a git archive of the
   original HEAD and reattached to the index in explicit batches. The five MM
   index entries were then reattached explicitly.
5. The 19 missing invalid cache paths were removed from the index explicitly.
6. The clean maintenance worktree was removed, then the primary checkout
   switched to the maintenance branch. The target branch supplied the approved
   deletion of all 34 current cache artefacts.

No user change was discarded before its rescue commit and external evidence
were verified.

## Worktree audit

All 13 pre-existing worktree directories existed. No registration had a
prunable or locked marker, so no pre-existing registration was removed.

The maintenance edit worktree and three transient validation worktrees were
created by this run and removed only after each was proven clean. The final
registration count remains 13. The 12 worktrees other than the protected
directed-causal-pair worktree were clean at audit time.

The protected path remained:

C:\Users\tommy\Documents\ising-v3-directed-causal-pair-00-phase0

Its branch and HEAD remained codex/directed-causal-pair-00-phase05 at
4bcb551092291b7383c4168f653818d4bade14f6 during the audit. Its untracked
working set grew substantially while this run proceeded, demonstrating
independent live activity. This run did not switch, stash, reset, remove,
stage, or write that worktree or either protected branch.

## Scientific integrity

The maintenance branch starts from f3921a4, a lineage that does not itself
contain the later V5/03G package. Integrity was therefore checked on the
canonical Git objects and descendant scientific branches, not by claiming
those files exist on the maintenance tip.

Verified unchanged:

- V5 source subtree a56a9f3ea1d5988fc08a67bc75d95f4f3197c2fe;
- V5 package inventory SHA-256
  401849316b07cdab949867578f2ea676cdf83b015c716be37638211a2d8a31bf;
- 03G result tree 14050a8eca2b67b897b9b3fdc3b4b69151adbbf9;
- 03G 50-world raw tree 968c1305ad5d095b2b8603a09070e9d377e81fe4;
- 03G raw inventory SHA-256
  267e6792102eb561f7edbba4fb9eeb73daca51658eb256af17ee24ab7e66e3dd;
- 03G raw manifest SHA-256
  ce8d2cb0b6158965acaeef3553f44c7f9bf0ef9b9567c858ff5cbb27f903a328;
- independent 03G reproduction tree
  0c61edde4cb8db14660aece653ac8a423271d630;
- downstream prospective worlds tree
  de178399ac6b5cb123d87c6a458112b3421c6b06;
- downstream raw collection SHA-256
  8d4baaac198cf5e5526359ad723d4cebd0c0614ffa2441fead41144ef573adf1.

All 50 03G raw entries match their manifest. No integrity discrepancy was
found.

## Validation

Completed checks:

- focused helper tests: 4 passed;
- real historical f3921a4 helper test: exact HEAD and exact tree
  8672babd1bc11d5912cf4820b06fa5947ebcd04b, 19 exact skips, clean;
- normal maintenance-tip worktree: exact HEAD and exact tree
  bbac5961fb88c38aec06e97a585767b572778dff, zero tracked tomo cache paths,
  clean;
- all transient test worktrees removed cleanly;
- final external recovery inventory: 945 files, zero mismatches;
- git diff --check: pass;
- show-ref exit 0; for-each-ref exit 0; 75 refs and zero unresolved targets;
- fsck exit 0 with zero errors; 11 dangling commits, 10 dangling trees, and 32
  dangling blobs were preserved;
- canonical V5, 03G, and downstream frozen-result diffs: all exit 0;
- final remote checks are recorded in the journal and final handoff.

## Restoration

The authoritative instructions are external:

C:\Users\tommy\Documents\ising-v3-recovery\REPOSITORY-HYGIENE-00-20260718-031627\RESTORE.md

Preferred meaningful-state restoration:

~~~powershell
git -C 'C:\Users\tommy\Documents\ising v3' worktree add 'C:\Users\tommy\Documents\ising-v3-recovered-working' 0c2b7b5952ee7eee533e9d5124c1d42e2287e9f5
~~~

The external-only snapshot must be copied to a new empty directory and verified
against untracked_snapshot_manifest.json. The malformed ref bytes are forensic
evidence and must not be copied back into .git/refs.

## Git status

maintenance/repository-hygiene-00 was pushed without force and no pull request
was created. The implementation tip b7506433f14f2643dfbdc16149084afd414ad8a4
was read back from origin before the report commit. The report/journal commit
necessarily follows the text it contains; its exact local/remote tip is
reported in the final handoff.
