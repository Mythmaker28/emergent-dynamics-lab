# GIT_PROVENANCE_AND_FRESH_CLONE_VERIFICATION

## Chain

    e912a1004c5b9732d12a8fcc417002bfd1135622   WSCCRP00
      -> f81daf91dd70a05f34372fb85d2c3fba0dd5550b   WSFSCRP00 closure
        -> f9e1e39170a746bc5d8c43a80bc878cf24180714   FSCMA00
          -> f65851c39496f379edac8b665dce87ba7cf1ebfb   GIMB00
            -> 0d92b612e051166b84d1a7d08d681ea78f5a512d   GIMB00 delivery record
              -> 226b2c93bdc34e5bec2ebc28d0c6066dc3123b14   WL2SMF00   <- this programme

Branch `dev/weighted-l2-sham-materiality-foundation-00`, parent the exact full `0d92b61`. Every
arrow was verified as a **direct parent** with `git rev-parse <c>^`, and the six commits are the
first-parent list from the tip. Short hashes were resolved before use; none was trusted.

## Content verification, from the committed tree

    git archive dev/weighted-l2-sham-materiality-foundation-00 WL2SMF00 | tar x -C <fresh dir>
    -> 65 of 65 SHA256SUMS entries verified, 0 failures

The manifest covers 33 top-level artifacts and the 32 sealed checkpoint/mask files. Parent trees
re-verified in the same session: WSFSCRP00 49/49, FSCMA00 35/35, GIMB00 25/25.

## Independent recomputation of the tree id

| computed by | git version | `WL2SMF00` subtree id |
|---|---|---|
| device repository | 2.34.1 | `d62851570fb4e45bfd5bee2efa84c8c46c1ce0ec` |
| cloud container, fresh empty repo | 2.43.0 | `d62851570fb4e45bfd5bee2efa84c8c46c1ce0ec` |

A tree id is a pure content hash with no history dependence, so an exact match across two
independent implementations on separately transferred bytes is a stronger check than a same-machine
re-read. Every parent source file this programme consumed was additionally bound by recomputing its
**git blob object id** from local bytes: 6 of 6 match.

## Zero-active-outcome re-check from the committed tree

`ZERO_ACTIVE_OUTCOME_ACCESS_LEDGER.json` and `WL2SMF00_NUMERICAL_THRESHOLD_LOCK.json` are both in
the committed tree and both record: 0 fresh active outcomes generated, 0 opened, 0 old active
outcomes loaded by the threshold pipeline, 0 old shams used as calibration units, and post-t0
advances of exactly `SHAM_0` x 16 and `SHAM_1` x 16 with nothing else. The resolved-symbol AST
audit is reproducible from the committed sources.

## Bundle

    git bundle create WL2SMF00.bundle ^0d92b612... refs/heads/dev/weighted-l2-sham-materiality-foundation-00
    git bundle verify -> "is okay"; prerequisite exactly 0d92b612e051166b84d1a7d08d681ea78f5a512d

`WL2SMF00.bundle` is placed in the repository folder alongside `FSCMA00.bundle` and `GIMB00.bundle`.

## What was deliberately not done

* No push, no pull request, no workflow trigger. `PUSH_AUTHORIZED = false`.
* Tommy's checkout was not moved, checked out, merged or modified; it remains on `main` at
  `f3921a4d`. Every operation used a separate `GIT_INDEX_FILE`, so the user's index was untouched.
* No parent output was overwritten. The WSFSCRP00, FSCMA00 and GIMB00 trees are unchanged.

## Known cosmetic artefact

The mounted filesystem does not permit `unlink`, so `git hash-object` leaves inert `tmp_obj_*`
files under `.git/objects/*/`. Git ignores files that do not match an object name. Recorded rather
than hidden.

    DELIVERY_STATUS = COMPLETE
