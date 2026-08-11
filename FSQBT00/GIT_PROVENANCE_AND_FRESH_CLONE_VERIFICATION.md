# GIT_PROVENANCE_AND_FRESH_CLONE_VERIFICATION — FSQBT00

Append-only. Recorded after the last commit it describes.

## Chain — direct parent at every arrow
    96c7d295  FWL2CF00 commit 6 (science ancestor of SQDT00)
     -> 740c025d -> 0ebab0d8 -> 16717582  SQDT00 (master freeze / offline programme / provenance)
      -> b9f25a23  FSQBT00 commit 1 (master freeze, zero numerical array)
       -> 6df18dad  FSQBT00 commit 2 (correct-unit LOBO audit, corrected licenses, tube, oracle)
        -> 1af85af9  FSQBT00 commit 3 (sealed twelve-block panel)
         -> 93c62fc7  FSQBT00 commit 4 (twin shams, thresholds, preactive lock)
          -> 90b8bb97  FSQBT00 commit 5 (opaque active raw-only)
           -> e3468aa1  FSQBT00 commit 6 (decoded analysis)
            -> <this>   FSQBT00 commit 7 (delivery closure, append-only)

Every arrow is a single direct parent (`git rev-parse <c>^`), no merges. Branch
`dev/fresh-serialized-quotient-basis-transfer-00`. Tommy's `main` = `f3921a4d…`, never moved,
checked out, merged, rebased or modified; every operation used a separate `GIT_INDEX_FILE`. After
the first fresh start no commit was amended, rebased or reset; the branch pointer only moved forward.

## Content verification
`SHA256SUMS` is built from the final committed tree, covering 90 entries (42 md/json/py/jsonl + 12
sham + 24 active support-restricted archives + 12 panel masks) and verifies from the committed tree
and from an independent extraction. The `FSQBT00` subtree id is recomputed by git 2.34.1 (device)
and git 2.43.0 (cloud) and agrees — a pure content hash certifying every blob recursively.

The immutable object `FWL2_RELATIVE_QUOTIENT_BASIS_V1` (owned by SQDT00, blobs `07c9cf7e…` /
`8f848411…`) was bound by committed blob id and **never** refit, rescaled, recentered, rotated or
re-versioned.

## Bundle
`FSQBT00_tip_<...>.bundle` is a thin bundle over the final tip, `git bundle verify` ok, one
prerequisite `16717582…`. No sha256 is hard-coded in this committed file (avoiding the inherited D2
defect); the bundle is rebuilt over the final tip and its digest reported out-of-band.

## Full-field evidence
The 12 full-field checkpoints (7.7 MB) are kept in the session workspace, bound by sha256 in
`FRESH_CHECKPOINT_FULL_FIELD_DIGESTS.json` (deviation D4). The committed support-restricted sham and
active archives reproduce the reader series string-for-string (sufficiency proofs in
`FRESH_SHAM_RAW_MANIFEST.json` and `FRESH_ACTIVE_RAW_MANIFEST.json`). No committed science is
omitted, and no absent file is listed in `SHA256SUMS`.

    DELIVERY_STATUS = COMPLETE
