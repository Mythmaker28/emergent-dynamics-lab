# FCDDH01R — verification report

What was verified, by what method, and what it establishes. Written before the final delivery commit
exists; the final tip, child-subtree identity, bundle digest and bundle size are therefore reported
**out of band** and appear nowhere in this file, to avoid self-reference.

## 0. Constraints honoured

```
SIMULATION_AND_RAW_ADVANCE_LIMIT   = 0     observed: 0
NEW_SEED_AND_SCIENTIFIC_ROW_LIMIT  = 0     observed: 0
HOLDOUT_START_LIMIT                = 0     observed: 0
ANALYSIS_CHANGE_SCOPE              = NONE  observed: none
REMOTE_REPOSITORY_SCOPE            = NONE  observed: no fetch, push, PR or any remote call
VERIFICATION_DECODES               = 1 authorised, 0 spent
TOMMY_TECHNICAL_ACTION_REQUIRED    = false
```

## 1. Commit resolution and chain integrity

Every reported prefix resolved **uniquely** from the local repository; no full hash was inferred
from a prefix.

| reported prefix | resolved |
|---|---|
| `93f13f45` | `93f13f45e6b6550a7ff709768b7b574161ed6a4f` |
| `b52b1eae` | `b52b1eae820c69be601eaee7d7fa0d4d827eb463` |
| `2b152a2a` | `2b152a2ad4f6abf4dc2c932fabff61a368fe1eed` |
| `fc1b41f8` | `fc1b41f87cadcc94407e5ca70d0fb43a7fcbc968` |
| `ffbda326` | `ffbda326703f93aa5a34c03e5f259e976771f793` |
| `f3921a4d` | `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77` |

* chain from the parent to C7: **linear, 0 merge commits**
* reported order `b52b1eae → 2b152a2a → fc1b41f8 → ffbda326`: **VERIFIED from the exact objects**
* C7 was the tip of every ref containing it before this closure; no competing descendant existed
* `main` = `f3921a4d…` = the committed audit value → `CLOSURE_COPY_MAIN_STATUS = EXACT_MATCH`;
  `main` does not contain `FCDDH01R/`
* `origin/main` is a stale remote-tracking ref only; it was read, never contacted

## 2. Base-state record taken before the first write

Branch, HEAD, tree and subtree identities, local refs, and the hash of every worktree item
overlapping the closure subtree were recorded before anything was written. See
`FCDDH01R_CLOSURE_BASE_AND_WORKTREE_AUDIT.json`.

`RECORD_STATE = SP` — C7 present with prepared but uncommitted closure files.

**No ambiguous overlap exists.** Every artifact created by this review carries a name absent from
both C7 and the worktree, so nothing was overwritten and no path required adjudication.

## 3. Worktree-against-C7 content check

All **6307** paths of the C7 `FCDDH01R/` subtree are present on disk and re-hash **byte-identical**
to their committed blobs. 0 mismatches, 0 missing.

Method note worth recording: a first attempt used `git diff-index` against an index freshly
populated by `git read-tree`, which reported *every* path as modified. That is a stat-cache artefact
of an index carrying no stat information — **not** content drift. The direct blob re-hash
(`git hash-object`, which applies the same clean filters git applies when committing) is the
controlling evidence and it is clean.

The closure commits are built from a **temporary index seeded by `git read-tree ffbda326…`**, so
every pre-existing blob is carried over from the commit object itself. No worktree copy of an
existing path can enter the new commits, by construction.

## 4. Campaign status

```
CURRENT_WORKSPACE_CAMPAIGN_STATUS = COMPLETE
PRIOR_ENVIRONMENT_MAIN_STATUS     = NOT_OBSERVED
PRIOR_ENVIRONMENT_PROCESS_STATUS  = NOT_OBSERVED
```

All three phases carry `status/PHASE_COMPLETE` and `status/PHASE_RESULT.json`. Every declared row is
charged, completed, sealed and published. No phase is mid-flight and no WAL is inconsistent.

Two stale `phase.lock` files name a process in the prior environment (`cwd
/home/claude/sweep/FCDDH01R`). That environment cannot be observed from here, so **no claim is made
about it**. The locks are preserved, inventoried, neither committed nor deleted; nothing was resumed
or interacted with.

## 5. Ledger integrity across this review

| | before | after |
|---|---|---|
| WAL records (3 phases) | 2736 | 2736 |
| charged starts | 240 | 240 |
| raw advance sequences | 240 | 240 |
| hold-out bytes read | 0 | 0 |

## 6. Numerical verification — method and separation

The gate ladder was re-derived by **exact rational arithmetic** over the committed certified
enclosures. The verifier imports only `json`, `os`, `sys` and `fractions`, reads only JSON evidence,
opens no `.npz`, and has no import path to `fh_core`, `fh_ref`, `fh_runner`, `fh_cworker`,
`fh_aworker`, `fh_decode`, `fh_disc`, `fh_hold`, `fh_oracle`, `fh_rand`, the trainer, the hold-out
scorer, the exact enumerator, `numpy` or `edlab`. It therefore **provably cannot** import, construct
or advance the simulation runner.

**Result: the independently re-derived ladder agrees with the committed ladder on all ten
numerically re-derivable gates** (D1 ✓, D2 ✓, D3 ✓, D4 ✗, D5 ✗, D6 ✓, D7 ✓, D8 ✗, D9 ✓, D10 ✓). D0
is a structural anchor and D11 is an AST source audit; both are accepted from their committed
reports.

Anchors, all verified against the reported values:

```
norm(X_BAR_D)   5.695567518165154e-04   reported 5.695568e-04   OK
A_X_BAR         2.924046708945949e-03   reported 2.924047e-03   OK
ratio           0.194783739             reported 0.194784       OK
max leverage    0.1386169981190795      reported 0.1386         OK
D5 count        0 of 12                                          OK
failed gates    {D4, D5, D8}                                     OK
```

One reported anchor is **corrected**: `MIN_FULL_VS_LOAO_ALIGNMENT_SQUARED` was stated as
`≥ 0.999278`; the exact minimum `0.9992776839495647` is below that by 3.16e-07, so the certified
statement is `≥ 0.999277`. D6's threshold is 0.80, so no gate is affected.

`D4` is a **certified strict failure**: the enclosures are disjoint and one-ulp tight, so
`UNRESOLVED` is excluded on the exact objects, not merely on rounded point values.

## 7. Target-access chronology

```
ORIGINAL_FIRST_TARGET_ACCESS_PROOF = RECOVERED
FIRST_TARGET_ACCESS_PROVENANCE     = COMPLETE
```

The original event is committed verbatim from `FCDDH01R/PRE_NUMERICAL_ACCESS_LEDGER.jsonl`:
2026-08-11T14:01:00Z, 240 charged starts before access, 0 prior looks, 0 confirmatory tests, 0 alpha
spent, binding the panel lock, the threshold lock and the raw lock by commit and digest. Nothing was
invented or backdated.

Chronology is **consistent, not contradictory**: threshold lock 13:51:52Z precedes the first active
gate 13:52:06Z; raw lock 14:00:20Z precedes the first decoding 14:01:00Z. This review's own
read-only access is logged with its real time in
`FCDDH01R_VERIFICATION_ACCESS_LEDGER.jsonl` and is never presented as the original.

## 8. Post-commit verification performed after the final delivery commit

1. every scoped blob re-read through independent Git-object reads and re-hashed
2. every `SHA256SUMS` line re-checked against the committed blobs
3. repository object integrity (`git fsck --strict`)
4. exact final tip and child-subtree identity computed
5. child subtree recomputed with **both locally available Git implementations** (2.34.1 on the
   repository host and 2.43.0 in the review environment) and compared
6. every task-branch change confirmed to lie inside `FCDDH01R/`
7. local Git bundle created from the final tip
8. bundle read back from a fresh temporary repository with its documented prerequisite chain
9. bundle SHA-256 and byte size recorded

Their results, and the identities they produce, are reported **out of band** — they cannot appear in
a file that is itself inside the thing being hashed.

## 9. Blockers checked and not triggered

* no irreconcilable base, parent, chain, branch, `main` or reachable-object mismatch
* no active or uncertain local campaign phase; no inconsistent WAL
* no missing or inconsistent opaque raw lock
* no contradictory target-access chronology
* no total above 240 FCDDH01R starts; no hold-out byte
* no raw / archive / gate / reference mismatch
* the post-start executor mutation is recorded and is **not** described as conformant
* no official axis or hold-out lock despite the failed gates
* no silently missing mandatory artifact
* no checksum, subtree, Git-object or bundle failure
* no request to alter the scientific result or reopen the experiment

## 10. Verdict

The record is **verified as an honest, complete and internally consistent account of a
non-conformant campaign that nevertheless produced a mechanically sound deterministic descriptive
calculation.** The scientific values were treated as evidence to check, never as values to rescue.
