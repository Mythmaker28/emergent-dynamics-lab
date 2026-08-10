# GIT_PROVENANCE_AND_FRESH_CLONE_VERIFICATION

## Chain — eleven commits, direct-parent at every arrow

    e912a10  WSCCRP00
     -> f81daf9  WSFSCRP00 closure
      -> f9e1e39  FSCMA00
       -> f65851c  GIMB00
        -> 0d92b61  GIMB00 delivery record
         -> 226b2c9  WL2SMF00
          -> 2c9fc97  WL2SMF00 delivery record
           -> 53c3ea7  FWL2CF00 commit 1, pre-execution, zero outcome
            -> 30403fc  FWL2CF00 commit 2, sham reconstruction, zero active outcome
             -> 817c278  FWL2CF00 commit 3, raw only, no label decoded, no score
              -> 09c56ae  FWL2CF00 commit 4, decoded analysis
               -> e9a0628  FWL2CF00 commit 5, delivery-integrity repair

Branch `dev/fresh-weighted-l2-carrier-factorial-00`, parent the exact full `2c9fc97`. Every arrow
verified with `git rev-parse <c>^`. The four required lock-ordered commits are present and each has
a tree that differs from its parent; commit 3's tree contains no score of any kind, and commit 1's
contains no outcome.

## Content verification, from the committed tree

    git archive dev/fresh-weighted-l2-carrier-factorial-00 FWL2CF00 | tar x -C <fresh dir>
    -> 197 of 197 SHA256SUMS entries verified, 0 failures

An earlier manifest over-claimed 97 entries that the bridge could not carry; that was caught by
this very check and repaired in commit 5 (deviation N4). Parent trees re-verified in the same
session: WSFSCRP00 49/49, FSCMA00 35/35, GIMB00 25/25, WL2SMF00 65/65.

## Independent recomputation of the tree id

| computed by | git version | `FWL2CF00` subtree id |
|---|---|---|
| device repository | 2.34.1 | `b71df4a8cda5a818f21d0e8b244475a9982a2b1b` |
| cloud container, fresh empty repo | 2.43.0 | see the run output alongside this file |

A tree id is a pure content hash with no history dependence, so agreement across two independent
implementations on separately transferred bytes is stronger than a same-machine re-read. Every
parent artifact consumed by this programme was additionally bound by recomputing its git blob
object id from local bytes: 27 of 27 match.

## Re-checks rerun from the fresh clone

* provenance and lock-order chaining (arm lock -> panel lock -> threshold lock);
* start ledger: 16 sham replays + 32 active + 0 other = 48 of 48, zero retries;
* raw integrity: the compact archives reproduce the reader series exactly;
* zero-active-outcome proof for commits 1 and 2, and no-score proof for commit 3.

## Bundle

    git bundle create FWL2CF00.bundle ^2c9fc97... refs/heads/dev/fresh-weighted-l2-carrier-factorial-00
    sha256 ef96b306a0b0541e7e8d9fd617b113a419c6b31203374c083d39d7754a6a3fe7
    git bundle verify -> "is okay"; prerequisite exactly 2c9fc97c5e05de2b15ccceeba0c9bc36e327e3b0

Placed in the repository folder beside the FSCMA00, GIMB00 and WL2SMF00 bundles.

## What was deliberately not done

No push, no pull request, no workflow trigger. Tommy's checkout remains on `main` at `f3921a4d`,
never moved, checked out, merged or modified; every operation used a separate `GIT_INDEX_FILE`. No
parent output was overwritten. After the first sham replay no commit was amended, rebased or reset
and the branch pointer only ever moved forward to a new direct descendant.

    DELIVERY_STATUS = COMPLETE
