# EBR02 — CRITICAL EXECUTABLE MAP

**Static verification: NOT PERFORMED — no engine source was recovered.** Nothing was imported,
nothing executed, nothing written from prose.

| item | file | commit | blob SHA | exact lines | semantic result |
|---|---|---|---|---|---|
| integer per-cell Y occupancy | — | — | — | — | `NOT_RECOVERED` |
| four ordered Y sub-shifts | — | — | — | — | `NOT_RECOVERED` |
| Binomial mover count | — | — | — | — | `NOT_RECOVERED` |
| sequential state update between sub-shifts | — | — | — | — | `NOT_RECOVERED` |
| toroidal wrapping | — | — | — | — | `NOT_RECOVERED` |
| destination free-capacity calculation | — | — | — | — | `NOT_RECOVERED` |
| destination-capacity refusal | — | — | — | — | `NOT_RECOVERED` |
| `p_hop_Y` path | — | — | — | — | `NOT_RECOVERED` |
| `muX` path | — | — | — | — | `NOT_RECOVERED` |
| `kY` and `muY` paths | — | — | — | — | `NOT_RECOVERED` |
| `nSY` candidate-pool semantics | — | — | — | — | `NOT_RECOVERED` |
| X birth acceptance | — | — | — | — | `NOT_RECOVERED` |
| X decay | — | — | — | — | `NOT_RECOVERED` |
| exact scheduler order | — | — | — | — | `NOT_RECOVERED` |
| centre classifier | — | — | — | — | `NOT_RECOVERED` |

**0 of 15.** `CRITICAL_EXECUTABLE_SEMANTICS = FAIL`.

## What was searched this time, and it was not nothing

The IPRR00R full bundle is a **complete, hash-verified, never-before-scanned** history: 304 commits,
5 282 objects, 3 210 blobs, `fsck` clean, whose tip `cff7f263` and predecessor `e0561989` are both
**absent** from the authoritative repository. It was scanned two ways:

* by **path**, over all 5 282 `rev-list --all --objects` entries — 0 hits for `ORR01`, `OBTC02`,
  `OBFOR01`, `OBTR01`, `PQEC01`, `FLCR01`, or any engine filename;
* by **content digest**, hashing all 3 210 blob contents against the 24 expected digests — 0 matches.
  This is naming-independent: a renamed, moved or restructured `kinetics.py` would still have been found.

A token sweep over every blob returned `p_hop_Y` 0, `TAU_SEP` 0, `rng.binomial` 0,
`np.random.binomial` 0, `TWO_CENTRES` 0, `ONE_CENTRE` 0. The 38 `nSY` byte-hits were opened and
rejected: they are inside `.npz` ZIP members and `P08/p08b_trace.csv.gz`, the same class of
compressed-binary coincidence seen in every previous sweep.

The bundle is an `emergent-dynamics-lab` audit history — its tip tree carries `CHMR`, `DOMC`,
`EEFCA`, `ETCMNFC`, `ETNBFC`, `ETPC`, `P07`, `P08`, `P09`, `PPAI` and the `INDEPENDENT_AUDIT_FREEZE_01R`
documents. It is a real recovery of real history. It is not the history that holds the engine.
