# FCDDH00 — Git and parent-provenance INTENT (Commit 1, pre-numerical)

This file states *what will be proved* in Commit 2 and *how*, and records the Git-metadata
resolutions already performed. It contains no decoded score, vector, checkpoint field,
trajectory, threshold value or response array.

## 1. Resolved identifiers (metadata only)

```
DIRECT_PARENT_PROGRAM  = FSQBT00_CORRECTIVE_RESIDUAL_AUTOPSY_00  (FCRA00)
DIRECT_PARENT_BRANCH   = dev/fsqbt00-corrective-residual-autopsy-00
DIRECT_PARENT_TIP      = 334b7c2ba6d97dadb403c7a1ea9700a1c61ad512
DIRECT_PARENT_TREE     = b36f821850a970c6cbb6a29ca539b3a99bbd5d8c
FCRA00_SUBTREE         = b43e04983e6a3cbf31b6ccc84b5267fbe17b1ad2      (334b7c2b:FCRA00)
DIRECT_PARENT_BUNDLE   = FCRA00_tip_334b7c2b.bundle
DIRECT_PARENT_BUNDLE_SHA256 = 95ef451164d31bea9b16b94e6d86aadad40c696a308e007e9955b1e506ae2e3b
FSQBT00_TIP            = b3f45ac7781e0dd48f34886b7c63840af520d502   tree 6c362f8acb4a80da8769986129a6ea0af58f099d
FSQBT00_SUBTREE        = ab11f2c0187b645f4793cb2b08dfa599fe506d4f      (b3f45ac7:FSQBT00)
SQDT00_TIP             = 16717582e7f0dfd371f21c56465e11113d8b6675   tree 6b3e8650eb62d31380c705944756e4211d20bdae
SQDT00_SUBTREE         = 2a68162bcbd2881267afbb7adbf19a03b7c028ba      (16717582:SQDT00)
FWL2CF00_SOURCE        = 96c7d295e72106cd949d810fa92807c2514e7449   tree 626dfe3278748b62495f4a90eaa61183770f2d82
FWL2CF00_SUBTREE       = 159577eeb703d5878b2efe37737b535fddc29046      (96c7d295:FWL2CF00)
TOMMY_MAIN             = f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77   tree 8672babd1bc11d5912cf4820b06fa5947ebcd04b
```

All five reported prefixes resolve uniquely and agree with the owner-reported values.
`git merge-base --is-ancestor` establishes the chain `96c7d295 ≺ 16717582 ≺ b3f45ac7 ≺ 334b7c2b`.
`main` is on a separate line and is **not** an ancestor of the dev chain; it must remain at
`f3921a4d…` for the whole programme.

The direct-parent commit chain immediately below the tip is
`334b7c2b → 47ab394f → db189490 → 7b72e6a9 → b9a4514e → 88d14e79 → e517121f …`, consistent with
the eight FCRA00 commits reported by the parent.

## 2. Branch creation and commit mechanics (intent)

`dev/fresh-crossed-differential-discovery-holdout-00` is created **from
`334b7c2ba6d97dadb403c7a1ea9700a1c61ad512`** and advanced by lock-free plumbing only:

```
export GIT_INDEX_FILE=<scratch index outside the repo>
git read-tree <parent-commit>
git add -f FCDDH00/<paths>
T=$(git write-tree)
C=$(git commit-tree $T -p <parent-commit> -F <message file>)
printf '%s\n' "$C" > .git/refs/heads/dev/fresh-crossed-differential-discovery-holdout-00
```

Reason: the working copy is exposed through a create-only mount on which `unlink` returns
`EPERM`, so a stale `.git/index.lock` (dated 2026-08-09) cannot be removed and ordinary
`git add`/`git commit` are unavailable. The plumbing path writes only *new* objects and one *new*
ref file; it never touches `main`, never rewrites history and never removes anything. This is a
packaging/plumbing accommodation with no effect on content: each commit's tree is verified after
the fact with `git cat-file`/`git ls-tree` and by an independent object extraction.

`main` is never checked out, moved, merged or edited. No amend, rebase, reset, force update,
history replacement, push, PR or workflow trigger is performed. The repository additionally runs
an autonomous heartbeat that may commit to `main` concurrently; FCDDH00 stays on its own branch
and re-verifies `main`'s tip at every phase boundary, reporting any change as a fatal stop.

## 3. Execution topology (intent)

Physics and analysis run in an isolated cloud execution container at `/home/claude/sweep`, whose
`edlab`, `DOMC`, `PPAI`, `ETPC`, `ETCMNFC`, `WSFSCRP00`, `WL2SMF00`, `FWL2CF00`, `SQDT00`,
`FSQBT00`, `FCRA00` trees were extracted **from the parent tree object
`b36f821850a970c6cbb6a29ca539b3a99bbd5d8c` by `git archive`**, not from a working directory. The
byte identity of every executable and parent object used by FCDDH00 against that tree object is
re-verified path-by-path in Commit 2 (`PARENT_PROVENANCE_BINDING.json`) and again at closure.
Artefacts are transported back into the repository working copy and committed by the plumbing
path above; no Git action is delegated to Tommy.

## 4. What Commit 2 must prove (binding list)

1. Byte identity, against `334b7c2b`'s tree, of every parent object FCDDH00 consumes:
   `SQDT00/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz` / `.json` and its loader; the parent `mu`, `P1`,
   `P2`, `e1`, `e2` and their numerical certificates; the immutable parent-P2 residual gauge rule;
   the G1 complete-factorial constructor and the ancestry graph; the H3 complementary-allocation
   orbit semantics; the two historical carrier executables and their 1× parameters; the
   weighted-L2 production and reference readers; the descendant-specific twin-sham materiality
   rule; the exact coefficient/bound propagation certificate; the engine runner and start-ledger
   contract.
2. The FCRA00 fact-and-claim binder: each owner-reported Section-0 fact checked against committed
   bytes, with any discrepancy recorded and **no parent artefact amended**.
3. G1 static eligibility (see `G1_WITHIN_ANCESTRY_ELIGIBILITY_AUDIT.md`): identical upstream
   precursor bytes for the four cells; one descendant per cell; geometry independent of
   allocation construction order; reader-compatible masks and support; no geometry/allocation
   label in any admission, reader, gauge or threshold formula; no seed-parity fallback; no G2
   substitute; and byte-for-byte reproduction of every historical parity-selected branch by the
   explicit form, proved by **static source equivalence with no physics instantiated**.
4. The static runner audit: `C_SETUP_D`, `C_SETUP_H`, `C_BLOCK_MAX`, `N_D_ATTEMPT`,
   `N_H_ATTEMPT`, derived from the exact committed code without advancing physics.
5. A complete namespace inventory (used, reserved, generated, opened, exposed) and the resulting
   clean interval `N ≥ 71000`, `N ≡ 0 (mod 1000)`.
6. The single 256-bit OS randomization seed, fsynced before any derivation and committed before
   construction, with SHAKE256 known-answer fixtures and the complete schedule.
7. The symbolic estimand ledger, exact interaction coefficient map, exact TAU propagation
   certificate and the P2 gauge / co-optimality specification.
8. Source hashes and a resolved-symbol dependency graph for every FCDDH00 executable, with zero
   dynamic imports, zero `eval`, zero unresolved `getattr`, zero filename/seed label inference and
   zero string-to-call dispatch.

**Zero engine starts and zero new outcome arrays in Commit 2.** Any provenance conflict is a
fatal zero-start stop with disposition
`PARENT_PROVENANCE_OR_G1_ELIGIBILITY_UNRESOLVED__ZERO_STARTS`.

## 5. State at Commit 1

```
FCDDH00 charged starts           = 0
FCDDH00 raw advance sequences    = 0
new states generated             = 0
candidates constructed           = 0
parent artefacts modified        = 0
main tip                         = f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77 (unchanged)
declared pre-freeze deviations   = 1 (see PRE_NUMERICAL_ACCESS_LEDGER.jsonl)
```
