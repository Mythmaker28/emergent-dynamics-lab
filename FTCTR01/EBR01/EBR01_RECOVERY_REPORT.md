# EBR01 — RECOVERY REPORT

**FTCTR01-EXECUTABLE-BYTE-RECOVERY-01** · Owner: Tommy Lepesteur · 2026-08-19
**RECOVERY_DISPOSITION = `RECOVERY_BLOCKED__EXTERNAL_ARTIFACTS_NOT_PRESENT_ON_DEVICE`**
Engine runs 0 · Worlds 0 · Seeds 0 · Reimplementation: not attempted, expressly forbidden

---

## 1. What the search found

The FTCTR01 audit's warning was justified, and acting on it paid off twice.

**Two new repositories were reached that no earlier mission had seen**, after `Documents` itself
proved non-grantable and its `ising-*` children had to be probed individually by name:

* `C:\Users\tommy\Documents\ising-life-lab` — a genuinely distinct project,
  `github.com/Mythmaker28/ising-life-lab`, package `isinglab`, 121 commits, newest ref 2025-11-14;
* `C:\Users\tommy\Downloads` — where **`LRCPS01_PAPER_PACKAGE.tar.zst` was found**, downloaded today
  at 21:24, together with `LRCPS01_MANUSCRIPT.pdf` and `LRCPS01_SUPPLEMENT.pdf`.

**Priority 1 — full Git bundle: `NOT_PRESENT`.** No `LRCPS01_FULL.bundle`, no `.PART*`, no
`OBOPR01_FULL.bundle`, under any accessible root.

**Priority 2 — raw confirmation package: `NOT_PRESENT`.** Neither
`OBOPR01_RAW_CONFIRMATION_PACKAGE.tar.zst` nor `OBFOR01_28_FRESH_CONFIRMATION_ARMS_V1.tar.zst`
exists. The 28 fresh arms are not on this machine.

**Priority 3 — paper capsule: `PRESENT`, and it is a manifest, not a recovery.** It decompresses
cleanly (1 925 120 B, 79 members). Its `code/` directory holds thirteen *paper-building* scripts —
`bind_sources.py`, `emit_numbers.py`, `make_figures.py`, `paper_claim_lint.py` and so on. It contains
**no engine source of any kind**: 0 of the 24 expected content hashes appear among its 70 files.

**Priority 4 — split deliveries: three thin bundles, wrong line, unusable.** The three
`persistence-without-ownership-v2*.bundle` files belong to the EDL paper line (two are byte-identical
duplicates). All three fail `git bundle verify` on the same missing prerequisite
`f382dbf077699aa65c80328b6519035d1cda4a57` — the *same* absent base commit FTCTR01's checker had
already reported for the orphan bundle inside `ising v3`. Their packs were nevertheless split at the
`PACK` magic and all 142 non-delta blobs inflated and hashed directly: **0 expected-hash matches**,
and every apparent token hit (`kY`, `nSY`, `kinetics`) resolves to compressed PDF bytes or to the
bibliography string *"Journal of Pharmacokinetics and Biopharmaceutics"*.

## 2. What the paper capsule did give — and why it settles the question

`provenance/PAPER_SOURCE_BINDING.json` is the expected-hash manifest the mission hoped for. It also
answers, unprompted, *where the engine lived*:

```
ORR01   -> /home/claude/ORR01          OBTR01  -> /home/claude/OBTR01
OBTC02  -> /home/claude/OBTC02         PQEC01  -> /home/claude/PQEC01
OBFOR01 -> /home/claude/OBFOR01        FLCR01  -> /home/claude/edl/FLCR01
```

Every path is inside an **ephemeral cloud container**. Its `REPO_HEAD`
`06c592313df96601de8d2a89676d5a5cf79fc414` and its branch
`codex/lineage-route-closure-and-paper-synthesis-01` **do not exist** in `ising v3` — `git cat-file`
returns *bad object*, and no ref among 193 matches. Its own `STATUS` is
`PAPER_ONLY_NONSCIENTIFIC_BINDING`.

The same file declares CLOC02 *"lost in the first container reset"* and RSLOC03 and RIRA01 *"lost in
the SECOND container reset"*, adding that externalised capsules *"are not mounted back into this
container."* `ORR01/code/kinetics.py` and its companions are in exactly that category. They were
never listed as lost only because the paper needed their hashes, not their bytes.

## 3. The hash sweep

A **naming-independent content-digest sweep** — a recovered file would be found even if renamed,
moved, or stripped of its directory structure:

| corpus | files hashed | expected-hash matches |
|---|---|---|
| extracted paper package | 70 | 0 |
| `ising-life-lab` (`.py .yaml .yml .json .md`, venvs excluded) | 357 | 0 |
| `Downloads` (regular files < 60 MB) | 93 | 0 |
| `ising v3` (`.py .yaml .yml` worktree) | 549 | 0 |
| non-delta blobs inside the three thin bundles | 142 | 0 |
| **total** | **1 211** | **0** |

Adjudication: `FILE_NOT_RECOVERED` × 24. `EXACT_MATCH` 0 · `HASH_MISMATCH` 0 ·
`MULTIPLE_CONFLICTING_VERSIONS` 0. No mismatch was repaired, because none arose.

## 4. The ceiling that existed before the search began

This is the finding worth carrying forward. Even a **perfect** artefact recovery could not have
authorised FTCTR01 to continue.

`PAPER_SOURCE_BINDING.json` is the only surviving expected-hash manifest, and it binds:

* `ORR01`: 3 code files + 3 outputs — full hashes;
* `OBTC02`: 3 code files — full hashes;
* `OBFOR01`: **outputs only**, 9 `out/*.json` files — *no code*;
* `OBTR01`: **outputs only** — *no code*;
* `PQEC01`: 128 raw archives with `files_present: {}` and `sha256: {}` — **nothing bound at all**;
* the centre-classification rule: **absent from the manifest entirely**.

So eleven of the engine files the launcher listed as "present and bound", and the whole centre
classifier, would have been `FULL_HASH_NOT_AVAILABLE` under §6 — and §6 forbids accepting a prefix or
a plausible-looking file as final verification. §8 would then have returned
`PARTIAL_RECOVERY__CENTRE_CLASSIFIER_MISSING`, and FTCTR01 still could not continue.

**The recovery route's ceiling was below its own pass mark.** Recording that is more useful than the
search result itself, because it tells the next operator that finding `LRCPS01_FULL.bundle` alone
would not be enough: the classifier needs the *PQEC01/FLCR01 code*, which no surviving manifest hashes.

## 5. What was refused

Three documentary substitutes were physically in hand and each would have let a careless operator
declare success: the manuscript and supplement PDFs, `supplement/S1_methods.tex`, and — most
temptingly — `figure_data/fig1_model_and_event_order.json`, which is the scheduler event order in
machine-readable form.

None was used. Rebuilding `kinetics.py` from Figure 1 would produce a model that *agrees with the
paper* and is nonetheless a **new architecture**, voiding `TAU_SEP = 125`, the `101/250` threshold,
the `C3` surrogate and every developmental observation attached to the old one. Behavioural agreement
is not byte recovery.

## 6. Disposition

```
RECOVERY_DISPOSITION      = RECOVERY_BLOCKED__EXTERNAL_ARTIFACTS_NOT_PRESENT_ON_DEVICE
FTCTR01_CONTINUATION      = NOT_AUTHORIZED
FTCTR01_FINAL_DISPOSITION = STOP__CRITICAL_EXECUTABLE_BYTES_MISSING   (unchanged)
```

No recovered branch was created, no freeze was written, no derivation was resumed, and
`ising-life-lab-recovered` was **not** created — there was nothing to restore, and an empty tree
would misrepresent the outcome. `ising-life-lab` was opened read-only; no history was merged; the
current Windows repository was not overwritten.

## 7. The one action that would unblock this

`C:\Users\tommy\Downloads\ising-life-byte-recovery\` has been created and is empty. Files placed
there, in this priority order, resume the recovery automatically:

1. `LRCPS01_FULL.bundle` (or every `LRCPS01_FULL.bundle.PART*`)
2. `LRCPS01_BUNDLE_PARTS_SHA256*`
3. `OBOPR01_FULL.bundle*`
4. `OBOPR01_RAW_CONFIRMATION_PACKAGE.tar.zst`
5. `OBOPR01_EXTERNAL_MANIFEST.json`
6. `OBOPR01_SHA256SUMS`

Items 1 and 4 are the ones that carry bytes. Items 2, 5 and 6 are what would let the eleven unhashed
engine files and the centre classifier be accepted at all — without them, §4 of the recovery still
lands on `PARTIAL_RECOVERY__CENTRE_CLASSIFIER_MISSING`.

If these artefacts were only ever delivered into a chat transcript and never saved to disk, then the
qualified source-response engine no longer exists anywhere, and the correct scientific conclusion is
the one FTCTR01 already reached: the two-centre clock is not derivable, and its inherited quantities
are `NON_EXECUTABLE__WITHDRAWN`.
