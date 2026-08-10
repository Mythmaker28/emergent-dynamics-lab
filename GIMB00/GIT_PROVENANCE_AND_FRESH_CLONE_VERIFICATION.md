# GIT_PROVENANCE_AND_FRESH_CLONE_VERIFICATION

## Chain

    e912a1004c5b9732d12a8fcc417002bfd1135622   WSCCRP00
      -> f81daf91dd70a05f34372fb85d2c3fba0dd5550b   WSFSCRP00 closure
        -> f9e1e39170a746bc5d8c43a80bc878cf24180714   FSCMA00
          -> f65851c39496f379edac8b665dce87ba7cf1ebfb   GIMB00      <- this programme

Branch `dev/gauge-invariant-mode-basis-00`. Each link is a **direct parent**, verified with
`git rev-parse <c>^`, and the four commits are the first-parent list from the tip. GIMB00's parent
is the exact full FSCMA00 commit, as required.

## Content verification, from the committed tree rather than the working tree

    git archive dev/gauge-invariant-mode-basis-00 GIMB00 | tar x -C <fresh dir>
    -> 24 of 24 SHA256SUMS entries verified, 0 failures

The parent trees were re-verified the same way in the same session: WSFSCRP00 49/49, FSCMA00 35/35.

## Independent recomputation of the tree id

The GIMB00 subtree object id was recomputed from separately transferred bytes by a **different git
installation on different hardware**:

| computed by | git version | subtree id |
|---|---|---|
| device repository | 2.34.1 | `a3b755e29b0ea3b6ae82d3bd9fa6cb26e1ec597b` |
| cloud container, fresh empty repo | 2.43.0 | `a3b755e29b0ea3b6ae82d3bd9fa6cb26e1ec597b` |

A tree id is a pure content hash with no history dependence, so an exact match across two
independent implementations is a stronger content check than a same-machine re-read.

Every raw parent file analysed by Phase 1 was additionally bound by recomputing its **git blob
object id** from local bytes as `sha1("blob <len>\0" + bytes)` and comparing with the object id in
the committed FSCMA00 tree. Six of six match.

## Bundle

    git bundle create GIMB00.bundle ^f9e1e39... refs/heads/dev/gauge-invariant-mode-basis-00
    sha256 c9a0b3c453ae989abc797744678bd48d05c31321b3bd4bb322a8e5fcf90673e1
    git bundle verify -> "is okay"
      contains  f65851c39496f379edac8b665dce87ba7cf1ebfb
      requires  f9e1e39170a746bc5d8c43a80bc878cf24180714

The bundle is thin by design: its stated prerequisite is exactly the FSCMA00 commit, which is
itself the ancestry assertion in machine-checkable form. `GIMB00.bundle` is placed in the
repository folder alongside `FSCMA00.bundle`.

## What was deliberately not done

* No push, no pull request, no workflow trigger. `PUSH_AUTHORIZED = false`.
* Tommy's checkout was not moved, checked out, merged or modified. It remains on `main` at
  `f3921a4d`, exactly where FSCMA00 left it. All work used a separate `GIT_INDEX_FILE`, so the
  user's index was never touched either.
* No parent output was overwritten. WSFSCRP00 and FSCMA00 trees are unchanged in this commit.

## Known cosmetic artefact

The mounted filesystem does not permit `unlink`, so `git hash-object` leaves `tmp_obj_*` files in
`.git/objects/*/`. Git ignores files that do not match an object name, so this is inert; it is
recorded rather than hidden. The objects themselves wrote and linked correctly, which is why every
tree, commit and archive above resolves.

    DELIVERY_STATUS = COMPLETE
