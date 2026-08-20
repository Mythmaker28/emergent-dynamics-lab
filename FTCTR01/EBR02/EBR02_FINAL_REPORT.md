# EBR02 — FINAL REPORT (single bounded recovery attempt)

**FTCTR01-RECOVER-FROM-LRCPS01-FULL-BUNDLE-02** · Owner: Tommy Lepesteur · 2026-08-20
**RECOVERY_DISPOSITION = `RECOVERY_BLOCKED__BUNDLE_PART_SET_INCOMPLETE`**
**ROUTE = `RECOVERY_ROUTE_CLOSED__EXACT_EXECUTABLE_NOT_PRESERVED`**
Engine runs 0 · Worlds 0 · Seeds 0 · Reimplementation: not attempted

---

## 1. The LRCPS01 parts did not arrive

Both candidate recovery directories were inventoried after you reported the files were placed:

* `C:\Users\tommy\Downloads\ising-life-byte-recovery\` — **1 file**, the README EBR01 wrote there.
* `C:\Users\tommy\Documents\ising-v3-recovery\` — **0 top-level files**, 63 sub-directories.

`LRCPS01_FULL.bundle.PART*` : **0 parts.** `LRCPS01_BUNDLE_PARTS_SHA256*` : **absent.**
`OBOPR01_*` : **absent.**

```
PART_SET_STATUS         = INCOMPLETE_PART_SET
CHECKSUM_MANIFEST_STATUS = CHECKSUM_MANIFEST_MISSING
```

The part count cannot even be stated, because the manifest that would declare it is itself among the
missing files. No device-wide search was launched.

**One thing did move, and it matters operationally:** `C:\Users\tommy\Documents\ising v3` was
relocated *into* `ising-v3-recovery\`. Its old mount is now empty. The live repository is intact at
`ising-v3-recovery\ising v3` with every FTCTR01 and EBR01 commit present, tip `0c5ad54d`. Nothing was
lost; the path simply changed, and this report was committed to the new location.

## 2. What the recovery directory *did* contain — and it was worth checking

Two 618 MB bundles named `IPRR00R_..._FULL_....bundle`, with a real checksum manifest. Section 2 says
a bundle called "full" is not trusted on its filename — so it was neither trusted nor dismissed.

| check | result |
|---|---|
| `sha256` vs `IPRR00R_FINAL_PACKAGE_SHA256SUMS.txt` | `11a3170f…` **EXACT_MATCH** |
| `git bundle verify` | **exit 0** — *"The bundle records a complete history."* |
| thin or full | **FULL** — zero prerequisites |
| advertised refs | 1 — `refs/heads/audit/chatgpt-independent-red-team-roadmap-01r` @ `cff7f263` |
| restored | **304 commits**, 5 282 objects, 3 210 blobs, 0 tags, 0 remotes |
| `git fsck --full` | **exit 0**, no dangling or missing objects |
| second bundle `e0561989` | proved an **ancestor** of `cff7f263` ⇒ entirely contained in the verified one |

This is a genuine recovery of genuine history: **`cff7f263` and `e0561989` are both absent from the
authoritative repository**, so these 304 commits had never been scanned by FTCTR01 or EBR01.

Getting it there required a workaround worth recording: a backgrounded copy of the 618 MB file was
killed twice — `setsid` does **not** save a job from the end of a tool call in this environment. A
resumable 1 MiB `dd` with `skip`/`seek`, truncated to a MiB boundary between calls, completed it.

## 3. And it does not contain the engine

Scanned two independent ways:

* **by path** — all 5 282 `rev-list --all --objects` entries: **0** hits for `ORR01`, `OBTC02`,
  `OBFOR01`, `OBTR01`, `PQEC01`, `FLCR01`, or any engine filename;
* **by content digest** — sha256 of all 3 210 blob contents against the 24 expected digests:
  **0 matches**. Naming-independent: a renamed or relocated `kinetics.py` would still have surfaced.

Token sweep over every blob: `p_hop_Y` 0, `TAU_SEP` 0, `rng.binomial` 0, `np.random.binomial` 0,
`TWO_CENTRES` 0, `ONE_CENTRE` 0. The 38 `nSY` byte-hits were opened and rejected — `.npz` ZIP members
and `P08/p08b_trace.csv.gz`.

The tip tree is `CHMR`, `DOMC`, `EEFCA`, `ETCMNFC`, `ETNBFC`, `ETPC`, `P07`, `P08`, `P09`, `PPAI`,
`INDEPENDENT_AUDIT_FREEZE_01R…` — the `emergent-dynamics-lab` project, again.

## 4. The classifier route, taken properly, terminates immediately

Section 6 is right that the classifier need not appear in the paper's methods hash, and offers
recovery through its scientific lineage instead. That route was taken: `PQEC01`, `FLCR01`,
`pqec01_run.py`, `pqec01_analyse.py`, `pqec01_design.py`, `flcr01_science.py`, `CORE_R`, `n_centres`,
`centre_count`, `TWO_CENTRES`, `ONE_CENTRE` — **0 hits** in the only newly available history.
Condition 1 (exact source bytes exist) fails, so conditions 2, 3 and 5 are untestable and condition 4
fails with it. Condition 6 was honoured: **no replacement classifier was written.**

`PAPER_SOURCE_BINDING.json` places `PQEC01` at `/home/claude/PQEC01` with 128 raw archives and an
**empty** `sha256` map, and `FLCR01` at `/home/claude/edl/FLCR01`. Neither has a counterpart in any
git history reachable on this device.

## 5. The raw package was not used as an excuse

Per section 4, absence of `OBOPR01_RAW_CONFIRMATION_PACKAGE.tar.zst` was **not** treated as a blocker.
`DEVELOPMENTAL_RAW_COMPARISON_STATUS = UNAVAILABLE`, and FTCTR01 would simply have omitted the
post-outcome comparison. The decision was made on the engine and classifier alone, exactly as
instructed — and they are absent.

## 6. Disposition, and the route closes

```
RECOVERY_DISPOSITION      = RECOVERY_BLOCKED__BUNDLE_PART_SET_INCOMPLETE
ROUTE                     = RECOVERY_ROUTE_CLOSED__EXACT_EXECUTABLE_NOT_PRESERVED
FTCTR01_CONTINUATION      = NOT_AUTHORIZED
FTCTR01_FINAL_DISPOSITION = STOP__CRITICAL_EXECUTABLE_BYTES_MISSING
FURTHER_RECOVERY_AUTHORIZED = NO
```

Per section 10 this is the end of the recovery route. No further disk search, repository scan,
bundle family, report-based reconstruction or recovery mission is authorised, by me or by a successor.

The two-centre Y/X architecture ran inside cloud containers that were reset twice. Its paper kept its
*hashes*; nobody kept its *bytes*. `TAU_SEP = 125`, the `101 births / 250 steps` threshold, the `C3`
surrogate and every developmental timing observation attached to them are hereby
**`NON_EXECUTABLE__WITHDRAWN`**: they are conversational quantities with no executable referent, and
they must not be cited as results again.

## 7. Recommended new scientific direction — outside the lost architecture

The programme is not out of science; it is out of *that* science. Three routes survive **by bytes**,
in descending order of readiness:

**A. Finish the mechanism you already measured (strongest).** DEV_06 established
`SIZE_NORMALIZED_FLUX_LIMIT` on the `lattice_bond` substrate: dose saturates because events are
**rejected** — 0 % at Q100, 40.6 % at Q800/L=24, 94.8 % sink-only, with a median eligible set of
**one cell**. That is a measured mechanism with a controllable handle (eligible-set size), a working
per-event ledger, and a substrate that runs today. The obvious next question is whether enlarging the
eligible set — rather than raising the dose — moves `I/I₀` below the 0.20 gate that ×8 dose could not
reach. It is a one-parameter, pre-registerable, falsifiable experiment on surviving code.

**B. Use the second substrate nobody has used.** `github.com/Mythmaker28/ising-life-lab` (package
`isinglab`, 121 commits) is a complete, independent Ising / cellular-automata / Hopfield toolkit on
this machine that this research programme has never touched. It is a genuine *replication substrate*:
any claim that survives on both `edlab` and `isinglab` is far stronger than one that lives on a single
engine — and cross-substrate transfer is precisely the weakness the consolidation commit already
flagged ("FHN structural not quantitative").

**C. Fix the process failure that cost you the architecture.** Three programmes (CLOC02, RSLOC03,
RIRA01) and the entire source-response engine were lost to container resets, while their *hashes*
survived in a paper. Externalising **code**, not only numbers, on every mission — one small bundle per
programme, pushed or hashed into the owner's repository the same day — is a half-hour habit that would
have made this whole recovery unnecessary. It is the highest-leverage change available and it costs no
science budget.

Whichever you pick, the entry condition is the one FTCTR01 taught at its own expense: **check that the
executable objects exist before writing the freeze.**
