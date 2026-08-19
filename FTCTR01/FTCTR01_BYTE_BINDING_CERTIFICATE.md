# FTCTR01 — BYTE-BINDING CERTIFICATE

**Program:** FUNCTIONAL-TWO-CENTRE-TIMESCALE-REDERIVATION-01 (FTCTR01)
**Owner:** Tommy Lepesteur
**Date (UTC):** 2026-08-19
**Outcome:** `STOP__CRITICAL_EXECUTABLE_BYTES_MISSING`
**Scientific engine runs used:** 0 · **World constructions:** 0 · **Seeds:** 0

---

## 0. Why this document exists instead of a derivation

The mission is explicit:

> The mission begins only if the following survive by bytes: exact engine scheduler, Y diffusion
> semantics, centre-classification rule, qualified X source-response operator, `muX` and `p_hop_Y`
> values, `CORE_R` definition, capacity and boundary rules.
> If a critical source is absent: `STOP__CRITICAL_EXECUTABLE_BYTES_MISSING`. Do not reconstruct it
> from memory.

Not one of those objects resolves to bytes in the only repository reachable from this session.
Therefore **no freeze was written, no derivation was attempted, and no number was produced.**
`FTCTR01_MASTER_FREEZE.md` / `.json` and `FTCTR01_METHODS_HASH` **do not exist**: freezing a
derivation plan for an architecture that has no executable referent would be fabrication, not
pre-registration.

This certificate is therefore the only scientific product of the mission: a **falsifiable,
re-runnable absence certificate**.

---

## 1. Search universe

| Quantity | Value |
|---|---|
| Repository (device) | `C:\Users\tommy\Documents\ising v3` |
| Remote | `https://github.com/Mythmaker28/emergent-dynamics-lab.git` |
| `HEAD` (`main`) | `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77` |
| `git` on device | 2.34.1 |
| Refs (`refs/heads` + `refs/remotes`) | 193 (123 unique tips) |
| Reachable commits | 397 |
| Objects in the object database | 12 817 |
| Blobs | 10 005 (1 143 944 703 B) |
| Unique paths ever committed | 10 397 |
| Untracked working-tree files | 8 492 |
| Nested repositories / submodules | 0 / 0 |
| Most recent commit on **any** ref | **2026-08-11** |

The newest work anywhere in the repository predates this mission by eight days and belongs to the
`AXMAT00` / `FCDDH01R` / `FCDDH00` chain (A/X materiality, crossed differential discovery),
recorded in project memory. Nothing after it exists.

---

## 2. Primary search (implementation 1)

Executed on the device through `git` plumbing, with a positive control at every stage.

1. **Ref names.** `git branch -a`, `git for-each-ref --sort=-committerdate` over all 193 refs.
   → No ref matches `obfor|organi[sz]er-bound|prospective-q|q-environment|founder-versus|fvlcr|pqec|cloc|rsloc|ftctr|two.?centre|timescale`.
2. **Commit messages.** `git log --all --format='%ci|%h|%s'` over 397 commits.
   → No commit announces any of the four declared parents.
3. **Every path ever committed.** `git log --all --name-only --format=''` → 10 397 unique paths.
   → Zero name matches.
4. **Content of every reachable text blob.** `git rev-list --all --objects`, filtered to
   `.py .md .json .txt .yaml .yml .cfg .toml .ipynb .csv` → 7 930 unique blobs, streamed through
   `git cat-file --batch` and grepped for
   `p_hop_Y | TAU_SEP | nSY | \bkY\b | muY | mu_Y | two-centre | third centre | OBFOR | PQEC | FVLCR | CLOC02 | RSLOC`.
   → **0 hits.**
5. **Content of every blob ≤ 512 KiB, reachable or not.** From
   `git cat-file --batch-all-objects --batch-check` → 9 654 blobs, 120 225 165 B, split into four
   chunks and streamed.
   → **1 raw-byte match** for `nSY`, inspected in context and **rejected**: it lies inside a
   zlib/gzip-compressed binary blob (`cat -v` shows surrounding high-bit noise). No textual
   occurrence exists.
6. **Untracked working tree.** `git ls-files --others --exclude-standard` → 8 492 files;
   1 322 source/text files and 5 550 JSON files grepped.
   → **0 hits.**
7. **Archives.** `tar tzf` on the payload archives at repository root
   (`FCDDH00_srcA.tgz`, `WL2SMF00_payload.tgz`, `FSCMA00_payload.tgz`, `GIMB00_payload.tgz`, `FW5.tgz`)
   → 0 member names matching `centre|hop|lineage|founder|tau`.
8. **Structural enumeration.** `edlab/substrates/` contains exactly twelve substrate packages:
   `boolnet, chemotaxis, ctrans, flow_lenia, lattice_bond, life, motile_polar, multistable,
   particle_dynamics, reaction_diffusion, scaffold` (+ `__init__`). Each engine docstring was read.
   None is a discrete particle-count lattice.
9. **Repository isolation.** `find -maxdepth 3 -name .git` → no nested repository; no `.gitmodules`.

**Positive control.** The identical pipeline, run on the identical corpus, returns 41 blob-lines
for `CORE_RADIUS` and 42 ref-qualified files across all tips. The method finds what is there.

---

## 3. Independent search (implementation 2)

A second operator re-derived the same question **without reading implementation 1's scripts,
intermediate files, or results**, and chose its own primitives (independent enumeration of the
6 pack `.idx` files and all 256 loose-object directories; direct zlib inflation of bundle
packfiles; end-to-end streaming of tar payloads).

Its coverage strictly **exceeds** implementation 1:

* **all 10 005 blobs** fully decompressed and scanned, including the 258 unreachable/dangling objects
  and all 160 blobs above 1 MiB;
* 199 refs (including `refs/archive/*` and `refs/codex/turn-diffs/checkpoints/*`), 397 commits,
  the full `git reflog --all`, 9 528 historical paths;
* 1 203 tracked + 8 492 untracked working-tree files, plus 5 792 git-ignored non-`.venv` files;
* **all 46 `.bundle` files** byte-walked, including one *orphan history*
  (tip `4dc575ea1e4939700ddaa52f70e7baf8f8deb459`, `refs/tags/DCL01T_R_AUTHENTIC`) whose base commit
  is absent from `.git` and is therefore invisible to `git grep`;
* **all 81 tar/tgz payloads** (~1.6 GB compressed), including
  `ROUTE_E_RAW_EVIDENCE_ESCROW_00.tar.gz` (1 553 920 000 B decompressed);
* 9 registered worktrees, no stash entries.

**Verdict: ABSENT on every item.** Its positive controls (151 `FCDDH01R|Clopper-Pearson` hits;
1 125 files matching `sha256|seed`; 585 matches inside the 586 MB bundle; 16 391 matching lines in
the 1.4 GB escrow stream; 20+ real `tau_*` symbols recovered) demonstrate the method's sensitivity,
and each bundle walk terminated exactly at `filesize − 20`, i.e. at the pack trailer — proving full
traversal.

**Two independent implementations agree.** Per the mission's disagreement rule (§13), agreement is
the condition for a load-bearing conclusion; there is nothing to average.

---

## 4. The decisive structural fact

Beyond token absence, one property of the codebase makes the described architecture **impossible to
have ever run here**:

> **`np.random.binomial` / `rng.binomial` occur zero times in the repository, worktree and full
> history.**

All 69 textual occurrences of "binomial" are statistical inference (Clopper–Pearson tails via
`math.comb`, Beta-Binomial power analysis, exact McNemar). The mission's Y diffusion is defined by a
**Binomial movement of 0, 1 or 2 co-located Y particles**. A process that was never drawn cannot have
been executed. Likewise, "occupied" in this repository *always* means a continuum threshold
(`occupied = state.m >= spec.matter_threshold`, `edlab/substrates/lattice_bond/instrumentation.py:103`),
never an integer particle count, so **destination-capacity blocking of a hopping particle has no
implementation to be exact about.**

---

## 5. What *does* survive, and why it cannot be substituted

| Mission object | Nearest surviving thing | Why it is not a substitute |
|---|---|---|
| `CORE_R` | `CORE_RADIUS = 10` — `experiments/individuation/directed_causal_pair_phase0_audit.py:25`, `..._phase05_mechanics.py:52`, `..._phase05_reproduce.py:137` (`10.0`) | Core/halo geometry of the **lattice_bond** individuation experiments. It radiates around a detected continuum component, not around a Y particle. |
| centre classifier | `detect_components()` — `edlab/substrates/lattice_bond/instrumentation.py:95`, single-linkage over `m ≥ matter_threshold` | Classifies **matter cells**, not Y positions. It cannot return `ONE_CENTRE` / `TWO_CENTRES` for two point particles because the field it consumes does not exist in the described model. |
| capacity rule | bounded matter cap `MMAX`, periodic square lattice; "capacity" in P07/P08 = throughput | An amplitude bound on a continuum field, and a flux quota — neither is an occupancy cap on a destination cell. |
| X source-response | P07/P08/P09 source-placement & sink operators with `GATE_MASK`/`GATE_TRACK`/`GATE_THRESH` | Acts on the same single matter field `m`; there is no second species, no birth acceptance, no decay constant `muX`. |

Transferring any of these would be exactly the reconstruction-from-memory the mission forbids.

---

## 6. Exact objects that must be produced before FTCTR01 can begin

1. The executable implementing sequential **Y diffusion**: four ordered sub-shifts, binomial mover
   count over co-located particles, sequential state update between sub-shifts, toroidal geometry,
   destination-capacity refusal.
2. The scalar **`p_hop_Y`** actually used by that executable (the *mobile* value, not a nominal one).
3. The scalar **`muX`** (X decay) and the **X birth acceptance rule** together with its local-state
   accessors `nX`, `nSY`.
4. The pair **`(kY, muY)`** and their admissible domain.
5. The **centre-classification predicate** mapping Y positions to `ONE_CENTRE` / `TWO_CENTRES`
   (single-linkage / adjacency / toroidal rule as actually coded, not Euclidean distance assumed).
6. The **qualified discrete X source-response operator** and its qualification record.
7. The **`CORE_R`** of that architecture, and its **capacity and boundary rules**.
8. The **provenance of `TAU_SEP = 125`** — the commit and file in which the number was computed or
   declared.
9. The four parent seals: **OBFOR01**, its **confirmatory seal**, **PQEC01**, **FVLCR01**.
10. Event-aligned **Y offered/blocked ledgers** (or, failing that, the aggregate Y blocking rate with
    its estimand), required for §4 of the mission.
11. The **raw developmental timing arrays** (separation times, hold times, third-centre ordering),
    required for §10.

This is a named, closed list. It is not a request for "more data".

---

## 7. Reproduction

Every step above is a `git` plumbing command against the repository as it stands. Re-running §2
against `HEAD = f3921a4d…` with the same token set must return the same zero. Any future claim that
these bytes exist is falsified by, or falsifies, this certificate.
