# FIMRCC01 — PRECONDITION CLOSURE REPORT

**The mission ends at the precondition gate. No world was run.**

```
MISSION           = FRESH-INTEGRATED-MINIMAL-REPRODUCTION-CAUSAL-CONFIRMATION-01
SHORT_NAME        = FIMRCC01
PARENT            = TLMR01, tip 1de537386d584f2ff6abfb72ca46dec3e02e3c36
HUMAN_DECISION    = A__PRECONDITIONS_NOT_MET
FRESH_WORLD_COUNT = 0
FRESH_SEEDS       = 0
```

## 1. The checkpoint, bound

**The law binding is bit-exact.** The three source artefacts the TLMR01 handoff flagged as absent
were retrieved from the owner's machine. All four `SOURCE_BYTES` hash to their declared values:

| artefact | sha256 |
|---|---|
| `PQEC01/out/PQEC01_MASTER_FREEZE.json` | `1d41505e…b83c` |
| `BPRTC01/out/BPRTC01_MASTER_FREEZE.json` | `9ba9e8ef…21f1` |
| `MCTT01/out/MCTT01_SELECTED_LAW.json` | `aa3b023d…2faf` |
| `MCTT01/out/MCTT01_PHYSICS_DIFF_FROM_B1.json` | `d0cb0f64…a9d0` |

All three laws verify at the **IEEE-754 bit level** against the patterns MCTT01 published —
`kY = 0x3f50763f01e8e5b2`, `muY = 0x3f484713dc1c8ab5`, `p_hop_Y = 0x3fba462ec93926a0`. Every one of
the 14 shared frozen constants has a byte-verified source. `tlmr01_laws`, `tlmr01_seeds` and
`tlmr01_run` now import in the container, which they did not in the container that issued the
handoff. All **518** frozen seeds re-derive from the parent-tip string and the seed-set hash agrees.

**The parent commit object is honestly reported as not recovered.**

```
PARENT_GIT_OBJECT_STATUS   = PARENT_GIT_OBJECT_NOT_RECOVERED
PARENT_SOURCE_BYTE_STATUS  = SOURCE_BYTES_AND_CHAIN_PREREQUISITE_VERIFIED
```

The commit `9f4c70ceeb05b0b8a1f27c4cfc855e125f921ce9` is unrecoverable in the container, in all
three owner-side bare repositories and in every bundle checked. Its tree and message cannot be
verified. What is verified is the four source artefacts byte for byte, and that
`TLMR01_C1_C2.bundle` — written before the rollback — names that exact commit as its prerequisite.
**Content recovery is not object recovery and is not reported as such.**

**P1, the device path** — the near-vacuous first cross-check the independent checker called F-01 is
replaced. Three LAW_C worlds **with a removal applied**, identical field for field including
`post_removal_intervals`. `CROSS_CHECK_PASS = True`, `NON_VACUOUS = True`.

## 2. Precondition A — PASS

The daughter was **not** redefined. It is already named by frozen inherited code at the 1→2
separation and recorded in every archive.

| gate | requirement | result |
|---|---|---|
| A1 unique localisation | the recorded daughter localises to exactly one offline component and one identity interval in every removal world | **22 / 22** |
| A2 no silent tie | no world required a tie-break of any kind | **0 tie-breaks** |
| A3 endpoint askable | the daughter interval survives at least one step after `t_m` | **22 / 22** |

The decision rule was written and hashed — sha256
`654d8fc59161e50f83868fad32b3e6c217960786421c591eb9f35095590b5209` — **before** the measurement ran.

## 3. Precondition B — PASS

256 worlds, 2 816 000 steps, 16 368 episodes, **zero** disagreements on M2, M3, M5 and the event
step; then the naming itself reconstructed independently on the 26 triggered worlds, agreeing
26 / 26 on the verdict and 22 / 22 on both the daughter and the parent cell sets, with all five
selective-removal fidelity checks at 22 / 22.

## 4. Why the confirmation cannot proceed

The endpoint that is above the floor is **saturated**; the endpoint that **discriminates** is at
the floor.

| | unrestricted (E0) | locked daughter (E1) |
|---|---|---|
| removal worlds satisfying it | **22 / 22** | **1 / 22** |
| complete intervals, total | 2 018 | 1 |
| median per world | 93 | 0 |
| world-level rate | 22 / 256 | **1 / 256** |
| ratio to `F_INTEGRATED` | 26.8× | **1.22×** |
| `P(K ≥ 2 \| N = 50)` | — | **0.0165** |

The `M5 = 22/256` that made LAW_C confirmation-eligible was carried by the **ambient population**,
not by the daughter. Restricted to the one identity the frozen code names as the daughter, the
retrospective world-level rate is 1/256, and at the frozen N = 50 the pre-declared K ≥ 2 criterion
has ≈ 1.65 % assurance. No larger N repairs it.

The three surviving candidates are paired count contrasts. Their prospective power is not
identified, because no matched no-removal arm exists anywhere in TLMR01's 512 worlds — which is
precisely the gap the SHAM arm was designed to fill. Selecting one after developmental outcome
access would change the scientific question, so none was selected.

## 5. What was not done

- no `SELECTIVE`, `SHAM` or `GLOBAL_OFF` arm was executed;
- no fresh base block, no reserve, no scientific-scale fixture world;
- no endpoint switch to E3, E4 or E5;
- no sample-size, parameter, law or threshold change;
- no post-hoc power rule, no new control design;
- no second checker, no review cascade, no new design mission;
- no handoff of any kind.

## 6. Disposition

```
FINAL_DISPOSITION          = CONFIRMATION_PRECONDITIONS_NOT_MET__LINEAGE_ROUTE_PAUSED
NEXT_SCIENTIFIC_ELIGIBILITY = NONE__LINEAGE_ROUTE_PAUSED
```

Reopening requires an explicit new human authorisation and a newly derived matched-control design.
Nothing in this mission authorises one.
