# GitHub provenance and stewardship audit 01R

## Verdict

| Question | Verdict | Basis |
|---|---|---|
| Is the ETPC -> EEFCA -> ETNBFC -> ETCMNFC chain internally coherent? | `PASS` | Each named commit exists locally and each later scientific commit has the preceding commit as its direct parent. |
| Is that scientific chain public on the named GitHub repository? | `FAIL` | No exact scientific branch, tag, release, pull request, or commit-search hit was found; none of the commits is an ancestor of current remote `main`. |
| Is the IPRR00R audit branch public? | `FAIL` (current state, not an attempted publication) | The local audit ref exists; the corresponding remote ref is absent. |
| Can an audit-only push be made without starting repository code? | `FAIL` | The sole active workflow triggers on every `push` and runs repository Python, DEV generation/reproduction, figure generation, and a container-wide reproduction target. |
| Can a draft PR be opened safely after such a push? | `FAIL` | The same workflow also triggers on every `pull_request`. A PR cannot cure the already-unsafe push and would add another trigger. |
| Is a verified bundle/archive currently evidenced by `SHA256SUMS`? | `PENDING` | At 2026-08-10 14:52 +02:00, `SHA256SUMS` had not yet been created. This item must be appended after final packaging; no verified-package claim is presently authorized. |

**Publication recommendation: do not push this branch and do not open a pull request.** Keep the final audit local,
then create a full Git bundle and a content archive from the final audit commit, verify both from a separate temporary
location, and bind their byte counts and SHA-256 values in `SHA256SUMS`. Remote publication becomes eligible only
after a separately reviewed workflow change makes audit-only refs/pathsets non-executing, or GitHub Actions is
administratively disabled for the publication operation. Neither change is part of IPRR00R.

## Repository state observed through GitHub first

The GitHub connector was queried before local provenance checks.

- Repository: `Mythmaker28/emergent-dynamics-lab`, repository ID `1295942465`.
- Visibility/default branch: public, `main`.
- Connector permission view: pull, triage, push, maintain, and admin were all reported available. Permission does not
  make a scientifically unsafe mutation eligible.
- Structured branch searches for the exact-twin, canonical-MF0, endpoint-functional, and independent-red-team
  families returned no branches.
- Structured commit search for ETCMNFC, plus exact-SHA searches for ETPC, EEFCA, ETNBFC, ETCMNFC, and the freeze
  commit, returned no commits.
- Structured pull-request search for the scientific/audit families returned no pull requests.
- Public GitHub API metadata reported zero releases and zero tags.
- Remote `main` resolved to `f382dbf077699aa65c80328b6519035d1cda4a57`.

The result is a **local-only evidence chain**. It must not be described as published, remotely reproducible, or
GitHub-backed merely because the local objects are coherent.

## Local commit chain

| Stage | Commit | Direct parent | Commit time (UTC) | Remote named ref |
|---|---|---|---|---|
| ETPC | `3f8dae8bbe2937c43661ba8adfe8aed63bf6b6ee` | `ba92a16a10c92cc400af81f022ef4dc78b16377e` | 2026-08-09 23:37:57 | absent |
| EEFCA | `de1524b22ff917dff1da6553f778a4f8019ac273` | ETPC | 2026-08-10 00:23:12 | absent |
| ETNBFC | `d86d24864e0f88c6483d11bcde601d1f13221a82` | EEFCA | 2026-08-10 01:35:23 | absent |
| ETCMNFC | `c5171b72f3ed2cdaba1968bdbd9ebf3776eab8d7` | ETNBFC | 2026-08-10 02:49:37 | absent |
| IPRR00R freeze | `55f4223dd6e965d5db36934f9ef0d96bfc344434` | ETNBFC | 2026-08-10 12:46:08 | absent |
| Sentinel amendment 1 | `d3491f5dda7bced17920de68624262cd9e976b10` | IPRR00R freeze | 2026-08-10 12:51:31 | absent |

`git merge-base --is-ancestor` passed for ETPC -> EEFCA, EEFCA -> ETNBFC, ETNBFC -> ETCMNFC, and ETNBFC ->
IPRR00R. The scientific and audit lines are siblings after ETNBFC; the audit line does not silently contain the
ETCMNFC tree. None of ETPC, EEFCA, ETNBFC, ETCMNFC, or IPRR00R was an ancestor of remote `main`.

The post-freeze scientific commit subjects refer only generically to sealed/untouched held-out state and the absence
of a primary allocation. They disclose no held-out identifier, seed, allocation, geometry, hash, size, timestamp, or
content. They are therefore L0 metadata under the frozen access table. No L1-L4 access occurred in this GitHub audit.

## Workflow safety audit

GitHub metadata reports exactly one active workflow:

- name: `emergent-metrology-ci`
- path: `.github/workflows/nasi-ci.yml`
- workflow ID: `313303737`
- state: active

The workflow blob is byte-identical at remote `main`, ETNBFC, ETCMNFC, the IPRR00R freeze, and sentinel amendment 1:
Git blob `fe1a991d75d5a8d36496123a52b36e7d6f98c613`.

The allowed blob declares `on: [push, pull_request]` with no branch or path filter. Its jobs:

1. check out the whole repository on Python 3.10 and 3.12;
2. execute freeze verifiers and regression programs;
3. execute a low-SNR DEV-generation command;
4. execute deterministic reproduction targets;
5. regenerate figures from raw artefacts;
6. build a repository Docker image and execute the repository-wide reproduction target inside it.

This is not a passive documentation lint. It executes repository scientific code and creates/recreates development
outputs. Therefore an audit-only push satisfies the frozen contradiction criterion: it can launch an
outcome-generating scientific workflow. Public API history corroborates that both trigger types are live: the
repository reports 165 workflow runs, and the first 100 returned runs comprise 81 `push` events and 19
`pull_request` events, all completed successfully.

Additional stewardship defects, independent of the scientific stop:

- GitHub-owned actions are referenced by mutable major-version tags, not immutable commit SHAs.
- Python packages are constrained by version ranges, not a locked dependency file/hash set.
- The container build executes repository-controlled Docker instructions, expanding the execution surface.
- No explicit job-level `permissions`, path filters, branch filters, or audit-only exclusion exists in the workflow.

## Safe publication gate

The exact gate for any later remote publication is all of the following:

1. a reviewed remote workflow state that cannot execute repository/scientific code for the exact audit ref and
   audit-only pathset;
2. confirmation from GitHub metadata that the safe workflow state is active before the audit ref is created or
   updated;
3. a push that contains audit documentation/tools only and no scientific code, result, manifest, DEV artefact, or
   workflow change;
4. post-push inspection showing zero workflow runs caused by that ref update;
5. only then, at most one draft PR, followed by the same zero-run check.

The current repository fails gates 1 and 2. IPRR00R must stop remote mutation here.

## Package verification still required

After the final audit commit, append a package-verification record to this file. It must include:

- final commit and branch ref;
- exact bundle and archive filenames and byte sizes;
- independently recomputed SHA-256 for each;
- `git bundle verify` output and confirmation that the final audit ref is advertised by the bundle;
- archive extraction into a fresh temporary directory and exact agreement of the extracted `SHA256SUMS`/audit
  deliverables with the final commit;
- proof that the verification directory is outside every scientific checkout.

Until that append exists, bundle/archive integrity is `PENDING`, not `PASS`.

## Independent package verification — P1 substantive audit at `e0561989`

Verification time: 2026-08-10 15:16-15:22 +02:00. Verification root:
`C:/Users/tommy/Documents/IPRR00R_VERIFY_GH_E056_20260810_1505`, outside every scientific checkout.

| P1 object | Independently observed bytes | Independently recomputed SHA-256 | Verdict |
|---|---:|---|---|
| `IPRR00R_AUDIT_ONLY_e0561989db5de1b278b3b27d1e035afe6f3c6e75.zip` | 71,788 | `908fb9a88798edfeb7998376023ad9d35487f565d7a4b7e6b7a4d54e68f6c976` | `PASS` |
| `IPRR00R_FULL_e0561989db5de1b278b3b27d1e035afe6f3c6e75.bundle` | 618,754,826 | `a95449da74ed7890e5a32d40b0e1b9640370503ac8d50fae7a6d9bd8aabe5392` | `PASS` |

### Bundle verification: `PASS`

- `git bundle verify` returned exit 0 and reported a complete history using Git's SHA-1 object format.
- The bundle advertised exactly one ref, `refs/heads/audit/chatgpt-independent-red-team-roadmap-01r`, at exactly
  `e0561989db5de1b278b3b27d1e035afe6f3c6e75`.
- A fresh bare repository successfully fetched that ref. The fetched ref resolved to the same object and
  `git cat-file -t` classified it as a commit.
- `git fsck --full --strict --no-dangling` returned exit 0 with no diagnostic output.

The SHA-1 statement above describes Git's internal object format; the independent SHA-256 in the table binds the
618,754,826-byte bundle wrapper.

### Archive and manifest verification: `PASS`

- The ZIP contains exactly 15 true file entries and one directory entry.
- Every filename passed the corrected external sentinel before content access. No absolute path, `..` traversal,
  case-insensitive duplicate, exact duplicate, or symbolic-link entry was present.
- All 15 files were freshly extracted under the verification root.
- For every extracted file, `git hash-object --no-filters` and byte size matched the exact blob at
  `e0561989db5de1b278b3b27d1e035afe6f3c6e75`: 15/15 exact byte matches.
- The extracted `SHA256SUMS` contains exactly 14 unique, well-formed entries. Its path set is exactly the other 14
  ZIP files, and every independently recomputed SHA-256 matched: 14/14.

The first attempt stopped closed before opening or extracting `INDEPENDENT_AUDIT_FREEZE_01R_AMENDMENT_1.md`, whose
ordinary L0 audit filename was absent from the original allowlist. Amendment 2, committed at
`e49cb988825e00cc6c19af621cb974c475e89f95`, added exactly the amendment 1 and amendment 2 audit-document paths and
requalified positive and negative sentinel probes. Full extraction resumed only after that closure. No scientific,
held-out, checkpoint, trajectory, engine, runner, or primary-allocation content was opened or executed.

### Scope of this `PASS`

This is a conclusive verification of **P1**, whose payload/ref is the substantive audit commit `e0561989...`. It is
not a claim that P1 contains the later amendment 2 or this post-package attestation. A final P2 repackage from the
post-attestation commit remains required; P2 must receive the same independent size, SHA-256, bundle-ref/fetch/fsck,
archive-byte, and manifest checks before it inherits `PASS`.

Local GitHub CLI 2.97.0 remains unauthenticated (`gh auth status` exit 1). That is not the reason publication is
withheld: the unconditional scientific `push` and `pull_request` workflow independently compels `NO_PUSH` and
`NO_DRAFT_PR`, even if credentials later become available.
