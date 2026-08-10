# GIT_PROVENANCE_AND_FRESH_CLONE_VERIFICATION — SQDT00

Append-only. Recorded after the last commit it describes (the lesson of inherited deviation D2).

## Chain — direct parent at every arrow

    …
    2c9fc97  WL2SMF00 delivery record
     -> 53c3ea7 … e9a06286  FWL2CF00 commits 1..5
      -> 96c7d295  FWL2CF00 commit 6 (provenance record)          <- SQDT00 parent
       -> 740c025d  SQDT00 commit 1 (pre-numeric master freeze)
        -> 0ebab0d8  SQDT00 commit 2 (complete offline programme)
         -> <this>   SQDT00 commit 3 (provenance + bundle, append-only)

`git rev-parse 740c025d^ = 96c7d295` and `git rev-parse 0ebab0d8^ = 740c025d`, each a single
direct parent, verified on the device. Branch
`dev/serialized-quotient-dose-transfer-00`. Tommy's `main` stays at
`f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77`, never moved, checked out, merged or modified; every
operation used a separate `GIT_INDEX_FILE`.

## Content verification, from the committed tree, twice

* On the device: `git archive 0ebab0d8 SQDT00 | tar x` into a fresh directory → `SHA256SUMS`
  verifies **24 of 24**, 0 failures (the 25th file is `SHA256SUMS` itself).
* Independent recomputation of the `SQDT00` subtree id:

  | computed by | git version | `SQDT00` subtree id |
  |---|---|---|
  | device repository | 2.34.1 | `b6bc8cdea4ec461b61c27ea09808238cf63448c1` |
  | cloud container, fresh empty repo, separately transferred bytes | 2.43.0 | `b6bc8cdea4ec461b61c27ea09808238cf63448c1` |

  A git tree id is a pure content hash with no history dependence, so agreement across two
  implementations on separately transferred bytes certifies every blob recursively.

## Parent binding
Every parent artifact consumed by this programme was bound by recomputing its git blob id from
local bytes (51 top-level `FWL2CF00` entries, all match) and, more strongly, by the cross-version
agreement on the `FWL2CF00` subtree id `159577ee…`. The offline rederivation additionally rebuilt
the reader series from the committed raw `rho` bytes and reproduced the committed series
string-for-string (48/48).

## Bundle
`SQDT00.bundle` (beside the FSCMA00, GIMB00, WL2SMF00 and FWL2CF00 bundles) is a thin bundle:

    git bundle create SQDT00.bundle ^96c7d295… refs/heads/dev/serialized-quotient-dose-transfer-00
    git bundle verify -> ok ; contains the branch tip ; requires exactly one prerequisite 96c7d295…

To avoid the parent's inherited defect D2 (a committed digest describing a bundle that was rebuilt
one commit later), **no bundle sha256 is hard-coded in this committed file**. The bundle is rebuilt
over the FINAL delivered tip after this commit exists, and its sha256 is reported out-of-band in
the delivery message accompanying the branch — computed after the last commit it describes. The
bundle is self-verifying regardless: `git bundle verify` confirms it carries the true tip and the
single correct prerequisite.

## What was deliberately not done
No push, no pull request, no workflow trigger. `PUSH_AUTHORIZED = DRAFT_PR_AUTHORIZED =
WORKFLOW_TRIGGER_AUTHORIZED = false`. No parent output overwritten. Zero engine starts across the
whole programme. The reserved namespace `62000–62009` was never generated or opened.

    DELIVERY_STATUS = COMPLETE
