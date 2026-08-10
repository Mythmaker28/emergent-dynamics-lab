# SQDT00_PARENT_PROVENANCE_AND_APPEND_ONLY_LEDGER

Append-only. Nothing in any parent programme is rewritten, amended or corrected in place.

## 1. The chain, resolved from the committed branch — never from prose

Every id below was read with `git rev-parse` / `git log` from
`refs/heads/dev/fresh-weighted-l2-carrier-factorial-00` in Tommy's repository. None was inferred
from an abbreviation and none was invented.

    7cc1ffa  WSCPL00                       (context, not a parent of this programme's claims)
    e912a1004c5b9732d12a8fcc417002bfd1135622  WSCCRP00
    f81daf91dd70a05f34372fb85d2c3fba0dd5550b  WSFSCRP00 closure
    f9e1e39170a746bc5d8c43a80bc878cf24180714  FSCMA00
    f65851c39496f379edac8b665dce87ba7cf1ebfb  GIMB00
    0d92b612e051166b84d1a7d08d681ea78f5a512d  GIMB00 delivery record
    226b2c93bdc34e5bec2ebc28d0c6066dc3123b14  WL2SMF00
    2c9fc97c5e05de2b15ccceeba0c9bc36e327e3b0  WL2SMF00 delivery record   <- accepted parent
    53c3ea7e8f9d4400fad2c998ee0eacc5ab917d2b  FWL2CF00 commit 1, pre-execution
    30403fc1b15890f70f2504d454ffb8ea8ef2160c  FWL2CF00 commit 2, sham reconstruction
    817c27886e97a90e2d54a410a65d9574654b1dc3  FWL2CF00 commit 3, raw only
    09c56ae7e37ef22b08675a57e9ca609474d9c63e  FWL2CF00 commit 4, decoded analysis
    e9a06286354284fe06fa15742a128919e3b64fcf  FWL2CF00 commit 5, delivery repair
    96c7d295e72106cd949d810fa92807c2514e7449  FWL2CF00 commit 6, provenance record  <- SQDT00 parent

**12 of 12 arrows verified**: for each pair, `git rev-parse <child>^` equals the stated parent and
`git rev-list --parents -n1 <child>` shows exactly one parent. There is no merge anywhere in the
chain, so "direct parentage" is unambiguous at every step.

Tommy's `main` is `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77` and is untouched.

## 2. Content verification, twice, in two containers, with two git implementations

1. **From the object database, on the device.** `git archive 96c7d295 FWL2CF00` extracted into a
   temporary directory never written by hand. `SHA256SUMS` carries 198 entries; the tree holds 199
   files (the 198 plus the manifest itself); **198 verified, 0 failed**.
2. **In this cloud container, independently.** The container's own copy of `SHA256SUMS` has
   content sha256 `051d3bdd2c502819d60535b30b48839bd65d490d7c10aea36605b31c5d363d95`, identical to
   the committed blob's content; all **198 verified, 0 failed** against it.
3. **Cross-implementation tree id.** The `FWL2CF00` subtree id is
   `159577eeb703d5878b2efe37737b535fddc29046` when computed by git 2.34.1 on the device from the
   object database, and the same when recomputed by git 2.43.0 in this container from
   independently held bytes. A git tree id is a pure content hash with no history dependence, so
   this single agreement certifies **every** blob id in the subtree recursively — it is strictly
   stronger than the 51 explicit top-level bindings, which were also checked and all match.

Parent subtrees additionally bound: `WL2SMF00` `8b002dc2a86974af0beb442a1013895ef5b47e36`,
`GIMB00` `bc56bfb17107114048416e27287ee27901f94a57`, `FSCMA00`
`27a62919b9664ab8fdb114f17e51016cfc3ccb46`.

## 3. Bundle

`FWL2CF00.bundle` passes `git bundle verify`, contains
`96c7d295e72106cd949d810fa92807c2514e7449` on
`refs/heads/dev/fresh-weighted-l2-carrier-factorial-00`, and declares exactly one prerequisite,
`2c9fc97c5e05de2b15ccceeba0c9bc36e327e3b0`.

**Inherited discrepancy, recorded not repaired.** The bundle's sha256 on disk is
`012ccb1b85bf5bb276240a7328d50ab821c1f94729b32e51d0c091dcce502a6d`, whereas the text committed
inside FWL2CF00 commit 6 records `ef96b306a0b0541e7e8d9fd617b113a419c6b31203374c083d39d7754a6a3fe7`.
The recorded digest was computed for the bundle as it stood before commit 6 existed, over tip
`e9a06286`; the bundle was then rebuilt over the new tip during delivery. Provenance is sound —
the bundle verifies, carries the true tip and names the correct prerequisite — and the parent
record is **not** rewritten. Carried forward as
`PARENT_BUNDLE_DIGEST_RECORD_IS_STALE_BY_ONE_APPEND_ONLY_COMMIT`.

Lesson taken for this programme: a digest of a delivery artifact must be recorded **after** the
last commit it is meant to describe, or not at all. SQDT00 records its bundle digest only in its
final delivery commit.

## 4. What the parent's committed claims actually mean — exact restatement

The following is the precise content SQDT00 inherits. It is quoted in meaning, not softened.

* **FWL2CF00 disposition**
  `FRESH_ACTIVE_PANEL_COMPLETE__RELATIVE_AT_LEAST_TWO__SECOND_BELOW_ABSOLUTE_MATERIALITY`.
* **What passed.** All 32 locked carrier cells were material against prospectively sealed
  thresholds (margins `M2/TAU` 3.14 – 10.20). The gauge-invariant quotient needs more than one
  affine coordinate: `QDIM0` (total scatter material, `R0/E_TAU = 3.675`), `QDIM2`
  (`I2/I1 = 0.0995 > 0.01`) and `QDIM3` (`I2/R0 = 0.0885 >= 0.05`) all passed, and the one-family
  reconstruction failed (`R1/R0 = 0.1112`, worst cell 0.4011), i.e. one affine coordinate does not
  reproduce the panel.
* **What failed.** `QDIM1`: the second increment is **below the absolute materiality floor**,
  `sqrt(I2)/A_TAU = 0.570`. The second dimension is *relatively* present and *absolutely*
  under-powered.
* **Why that is not a contradiction.** `I2 <= R0` always, and the aggregation lemmas give
  `R0 <= E_TAU` and `sqrt(I2) <= A_TAU` under the all-immaterial null. The modal gate therefore
  strictly implies the total gate, and passing the total gate while failing the modal gate is the
  designed conservatism, not an inconsistency.
* **What was not evaluable.** `FRESH_STRATUM_TRANSFER = NOT_EVALUABLE_FROM_COMMITTED_PARENT_OBJECT`,
  because GIMB00 serialised only scalars (`R_STRATUM_0`, `E_STRATUM`, `P_STRATUM_PLUS/MINUS`,
  `sector`, support counts) and never the vectors `psi_plus` / `Psi_minus`. **A scalar cannot be
  projected onto.** Removing that defect for the FWL2CF00 geometry is the entire point of SQDT00's
  discovery object.
* **Cost.** 16 sham replays + 32 active + 0 other = 48 of 48 starts, zero retries.

## 5. Claims SQDT00 explicitly does not inherit

* No claim that the second dimension is real. It is relatively present and absolutely
  under-powered; that is all.
* No claim about geometry, allocation or history order. FSCMA00 showed those three collapse into
  seed parity in the inherited constructor, and neither WL2SMF00, FWL2CF00 nor SQDT00 tests them.
* No claim that the parent's rank-one label was physical: FSCMA00 showed it to be a
  channel-labelling artefact.
* No relation whatsoever between the FWL2CF00 quotient basis and any GIMB00 object.

## 6. Deviations opened at Section 0

* **D0** — the verbatim SQDT00 handoff text was lost to context compaction; the surviving
  structured constraints are honoured literally, but deliverable names, gate texts and report
  explanation wordings are reconstructed rather than quoted.
* **D1** — a full `git clone` and a depth-14 `git fetch` of the device repository both exceeded
  the 45 s bridge call limit (the repository sits on a network mount). The fresh-clone
  requirement is met instead by an object-database extraction into a never-hand-written temporary
  directory, plus an independent recomputation of the subtree id in a second container with a
  different git version, plus `git bundle verify` for object-graph integrity.
