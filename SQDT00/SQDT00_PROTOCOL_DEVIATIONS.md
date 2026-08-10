# SQDT00_PROTOCOL_DEVIATIONS

Append-only. Each deviation states what was asked, what was done instead, and why the substitute
is at least as strong on the property that mattered.

## D0 — verbatim handoff text lost to context compaction
The session that received the SQDT00 handoff ran out of context; only the structured constraint
block, the six ordered questions (Q1_OFFLINE … Q6_TRANSFER), the section skeleton and the named
stop tokens survived into the working summary. The exact wording of the 38 deliverable names, the
Q0–Q19 gate texts and the 16 report explanations is therefore **reconstructed from the surviving
binding constraints, not quoted**. Every constraint that did survive is treated as binding and is
honoured literally: the estimand, the gauge, the thresholds, the dose semantics, the forbidden
aliases, the seed-namespace disjointness, the start budget and every `= false` flag. Impact:
naming only; no scientific object is affected.

## D1 — full `git clone` substituted by an object-database extraction plus a cross-version tree id
The mission asks for verification from a fresh temporary clone. Tommy's repository lives on a
network mount; a `git clone` and even a depth-14 `git fetch` of the relevant branch both exceeded
the 45-second bridge call limit. Substituted, and stronger on content integrity:

1. `git archive 96c7d295 FWL2CF00` extracted from the **object database** into a directory never
   written by hand — 198/198 `SHA256SUMS` entries verified, 0 failures.
2. The same manifest re-verified **inside this independent cloud container** against separately
   transferred bytes — 198/198, 0 failures.
3. The `FWL2CF00` subtree id `159577eeb703d5878b2efe37737b535fddc29046` recomputed by **git 2.34.1
   on the device** and by **git 2.43.0 in the container**; they agree. A git tree id is a pure
   content hash with no history dependence, so this single agreement certifies every blob id in
   the subtree recursively.
4. `git bundle verify FWL2CF00.bundle` supplies the object-graph-traversal check a clone would
   have given.

## D2 — inherited stale parent bundle-digest record, carried forward not repaired
`FWL2CF00.bundle` on disk has sha256
`012ccb1b85bf5bb276240a7328d50ab821c1f94729b32e51d0c091dcce502a6d`, while the digest recorded
inside FWL2CF00 commit 6 is `ef96b306…`. The recorded digest describes the bundle as it stood
before commit 6 existed (over tip `e9a06286`); the bundle was then rebuilt over the new tip during
delivery. The bundle verifies, carries the true branch tip `96c7d295` and names the correct single
prerequisite `2c9fc97c`, so provenance is sound. Parent outputs are **append-only** and are not
rewritten; the discrepancy is recorded here as
`PARENT_BUNDLE_DIGEST_RECORD_IS_STALE_BY_ONE_APPEND_ONLY_COMMIT`. Lesson applied to this
programme: SQDT00 records its own bundle digest only in its final delivery commit, after the last
commit the digest is meant to describe.

## No other deviations
No engine start was spent. No parent output was overwritten. `main` was never moved. The reserved
namespace `62000–62009` was never generated or opened. No push, pull request or workflow trigger.
