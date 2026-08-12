# ORR01_APPEND_ONLY_CORRECTIONS

Append-only. No inherited artefact and no frozen byte of this mission is edited. Each entry is
dated, linked to the hash and commit it concerns, and carries its reason.

---

## C-1 — 2026-08-12 — the inherited bundle was not a self-contained checkout

**Concerns** `MCM01_branch.bundle` and `MCM01_selfcontained.pack`, MCM01 commit `506272a`.

MCM01 verified its bundle by **extracting and indexing its packfile** and hashing the blobs. That
proves the bundle's contents but not that a checkout can be reconstructed offline. The inherited
repository was a **blobless promisor clone**: `git rev-list --objects --missing=print HEAD` listed
**392 missing objects** of 2229 reachable. In the `f3921a4..HEAD` range **0** were missing, which
is why MCM01's packfile check succeeded and why the deficiency was invisible to it.

Repaired here, not retroactively: the partial-clone filter was removed and `git fetch --refetch`
materialised every object (**0 missing**, `fsck` clean). A further finding is recorded because it
will recur: **git 2.43 bundles do not carry the shallow boundary**, so a bundle produced from a
shallow clone verifies as prerequisite-free and then fails to clone with *"Failed to traverse
parents of commit f3921a4d… remote did not send all necessary objects"*. The artefact is
therefore a gzipped **bare shallow repository**, from which a real offline `git clone` and
`git checkout` were performed and the MCM01 tests were run.

```
PROVENANCE_STATUS = SELF_CONTAINED_OFFLINE_READBACK_PASS
old artefacts left untouched
```

---

## C-2 — 2026-08-12 — three MCM01 statements about the ratchet are corrected

**Concerns** `MCM01_FINAL_REPORT.md` section 7, commit `506272a`. Not modified.

| MCM01 statement | correction, from exact finite-state analysis |
|---|---|
| occupancy "rises monotonically" | **false in general.** `O(t+1)−O(t) = add − out` and `out > 0` whenever waste exists. Monotone only in the resource-only sub-dynamics, where `out ≡ 0`. |
| "`O` rises until `free = 0` everywhere" | **false in general.** The chain is absorbed into a **no-room** configuration, which is not the same as zero free capacity. On an exact two-cell ring started at the protocol's own initial condition, `P(no room anywhere) = 1` but `P(both cells full) = 0`, the resource settling at 2.5× its set-point with free capacity still present. On the L = 36 lattice the no-room configuration does sit at capacity — that is a large-system property, not a theorem. |
| "the full state is absorbing" | **holds only on a sub-space.** Exhaustive over the 84 states of a one-cell six-species system: of 56 full states, **10 are absorbing and 46 are not**. An explicit cycle is exhibited: a full state carrying waste loses a unit through the outflow, which re-opens capacity, which the feed immediately refills. |

What survives, and is now exact: the feed is additive and drives occupancy strictly above its own
set-point until no room remains; and at stationarity `phi·E[R] = muX·N_X + muY·N_Y`, so the room
the system can hold is pinned to the body's own death flux. A new exact scope statement is added:
**on a single cell the same additive feed stops exactly at `S0`** — the ratchet requires
additivity *and* transport, not either alone.

```
CURRENT_ADDITIVE_LAWSPEC = SCOPE_LIMITED   (explicit scope, narrower than MCM01 stated)
```

---

## C-3 — 2026-08-12 — "extinction is inevitable" is true but is not a property of this LawSpec

`n_X = 0` is invariant and reachable from **all 84** states of the enumerated system, so on a
finite lattice the body goes extinct with probability 1 and in a.s. finite time — under the
additive LawSpec **and under every repair of it**. Extinction therefore cannot discriminate
between LawSpecs. Every maintenance claim in this project is, and must remain, a claim about a
**quasi-stationary level and a persistence time over a stated window**.

---

## C-4 — 2026-08-12 — "supercritical" is downgraded

**Concerns** `MCM01_FINAL_REPORT.md` section 6 and `MCM01/out/_audit.json`.

At `kX = 1`, which is what MTW01 and MCM01 actually ran, `p_X = min(1, kX·nX·nY)` saturates at
`n_X ≥ 1`: with capacity not binding, the birth law is **identical** for `n_X = 1` and `n_X = 2`.
The low-density map is a step, not a linear operator; there is no linearisation about `n_X = 0`
and no branching multiplier.

```
SCALAR_CRITICALITY = NOT_VALID at kX = 1
SCALAR_CRITICALITY = APPROXIMATE at small kX, where the map is exactly linear but its
                     coefficients are random and endogenous, so the growth rate is the top
                     Lyapunov exponent of a product of random operators
MTW01 "the point was supercritical"  ->  BY_PREVIOUS_MEAN_FIELD_CRITERION_ONLY
```

`c_X·G(0)` is retained only as a descriptive statistic — the expected offspring number of a
single body molecule in a frozen environment — and only in the mean form corrected by MCM01
addendum C-1.

---

## C-5 — 2026-08-12 — a sequential-rule implementation diverged from the written rule

**Concerns** `code/run.py` under `METHODS_CORE_HASH = 1cfdb192…b949a84d`.

The written rule 9 is *"all formed clouds collapse over the first three seeds → STOP"*. The code
implemented *"no repaired arm passed over the first three seeds → STOP"*. Those are not the same
condition, and the difference fired: the three repaired clouds had **not** collapsed — they were
maintained at `N_X = 110` to `124` with occupancy drift `0.00000` — but none had passed the gate,
so the run stopped after three pairs.

**Direction and consequence.** The coded rule is **stricter** than the written one: it stops
earlier and consumes fewer starts. It cannot inflate a positive result. And it could not change
the disposition: with 0 of 3 repaired seeds `MAINTENANCE_ACHIEVED`, the frozen success criterion
of 5 of 6 was already unreachable. The written protocol was then completed in `code/run2.py` —
the remaining three pairs and all eight controls — and the full six-pair result is reported.

```
PROTOCOL_VIOLATION = SEQUENTIAL_RULE_IMPLEMENTATION_STRICTER_THAN_ITS_TEXT
direction = conservative      disposition unchanged = YES      written protocol completed = YES
frozen bytes edited = NONE
```

---

## C-6 — 2026-08-12 — the historical MINCORE spatial failure

No video, animation or frame sequence of the MINCORE run is present anywhere in the workspace or
the repository; only a single end-of-run descriptor was ever saved.

```
MINCORE_HISTORICAL_SPATIAL_FAILURE = UNRESOLVED
visual classification = NO_VISUAL_DATA
```

The question is not blocking and the mission continued. It is worth noting that the ORR01 gate,
applied post hoc to the eight historical MCM01 arms, classifies all eight as `OCCUPANCY_RATCHET`
— which is indirect support for the conjecture that MINCORE's "fills the domain" was the lattice
filling with resource, but it is not the visual evidence and it does not close the question.
