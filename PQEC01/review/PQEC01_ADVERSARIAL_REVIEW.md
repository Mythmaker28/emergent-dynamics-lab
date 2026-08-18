# PQEC01 — INDEPENDENT ADVERSARIAL REVIEW

**Reviewer role.** Single authorized independent adversarial reviewer. Read-only on the candidate.
Nothing outside `/home/claude/PQEC01/review/` was written. No `World`, `WorldOBTC` or `PQECWorld`
was constructed; `_one_step` was never called; no organiser was seeded.
`NEW_SCIENTIFIC_RUNS_BY_REVIEW = 0`.

**Method.** Source reading; exact recomputation from the 128 raw `.npz` archives with numpy;
exact arithmetic on the frozen criteria; filesystem and git forensics. Scratch scripts:
`/home/claude/PQEC01/review/work/{a5_a9_phaseA.py, a10_phaseB.py, a10_sep.py, a10_field.py,
a2_hops.py, a6_a8.py}`.

**Candidate disposition under attack.**
`PROSPECTIVE_Q_ENVIRONMENT_OPERATOR_NOT_IDENTIFIED__ADDITIONAL_INSTRUMENTATION_REQUIRED`,
11 of 13 gates passing.

---

## SUMMARY OF THE ATTACK

Two attacks failed outright and the claims they targeted stand on the merits: **A2 (observer
inertness)** and **A10 (real descendant-local exposure)**. Both were attacked hard and both
survived exact verification against the raw archives and against the engine source.

Ten attacks produced confirmed defects. None of them forces the terminal disposition string to
change: `LOAD_BEARING_DEFECTS = 0`. But three of the reasons the candidate *gives* for that
disposition are wrong, and the provenance chain that is supposed to make the disposition
trustworthy has confirmed holes:

1. `PQEC01_METHODS_HASH` does not cover `pqec01_run.py` — the executor that actually ran the 128
   worlds — which was written 65 seconds *after* the freeze commit (**F01**).
2. A complete analysis run, including `PQEC01_INTERNAL_VALIDATION.json`, finished at 00:01:33;
   the two declared "fixes" were made at 00:02:20 and 00:06:01 and the final run at 00:07:58.
   One of the fixes flips validation TEST 2 at B1 from **FAIL (z = −14.32)** to
   **PASS (z = +1.16)** (**F14**).
3. `PQEC01_FINAL_DISPOSITION.json` was hand-edited at 00:08:39 after the last analysis run and
   contains four blocks the committed code does not write, including the block that names the
   missing object (**F16**).
4. The empty candidate region proves nothing about the calibration: criteria C1, C2 and C3 are
   **mutually unsatisfiable for every `kY` and every exposure**, so the claimed
   "0.1513 → 0.1528 decades, the measurement confirmed the arithmetic" is grid quantization,
   not a measurement (**F21**).
5. The feedback verdict "not significant" is a Simpson's-paradox artefact: Phase-B worlds that
   produced a descendant carry **+61.0 %** and **+51.9 %** more X than Phase A (z = +5.65,
   +5.88), worlds that did not carry −16.2 % and −10.2 %, and the pooled means cancel to
   +11.9 % / +15.2 % (**F18**).

---

## FINDINGS

Severity key: `LOAD_BEARING` = if confirmed, the terminal disposition must change.
`SUBSTANTIVE` = a published claim, number or gate is wrong or unsupported.
`COSMETIC` = label, presentation or vacuous construct.

---

### F01 — the methods hash does not cover the code that ran

- **ID** F01
- **ATTACK** A1 (freeze chronology)
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** `PQEC01_MASTER_FREEZE.json → PQEC01_METHODS_HASH` binds the programme's methods
  as of the freeze; freeze §"METHODS_HASH a1c910c8…".
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_freeze.py:18-24` (`methods_hash()`
  walks `os.listdir(CODE)` for `*.py` at call time); `/home/claude/edl/PQEC01/out/PQEC01_METHODS_HASH.txt:1`.
- **EXACT_NUMBERS** SHA-256 over the four files that existed at 23:26:40 — `pqec01_design.py`,
  `pqec01_freeze.py`, `pqec01_observer.py`, `pqec01_qualify.py` — reproduces
  `a1c910c870e92a2a8d33c8fdbc0d29224b7d02a7d9ab1c490383db2bd20e8142` **exactly**. Adding
  `pqec01_run.py` gives a different digest. `pqec01_run.py` mtime = 2026-08-17 23:28:32.452,
  i.e. **65 s after** the freeze commit (23:27:27) and **112 s after** the hash was computed.
  Un-hashed: `pqec01_run.py` (183 lines), `pqec01_manifest.py` (57), `pqec01_analyse.py` (604 at
  C3), and every engine file under `/home/claude/ORR01/code` and `/home/claude/OBTC02/code`.
  Hash over all 7 present `.py` files today: `34e43fd51c9840b6e29f624bd0bbe719aa1f1d2b06758c9d514074b8cf6545fa`.
- **WHY_IT_MATTERS** The un-hashed executor contains the stop-rule implementation, the `SCALARS`
  definition, the `_centres`/`CORE_R` implementation, the archive schema and the `n_rec` truncation.
  The freeze therefore cryptographically binds the *design* and the *observer* but not the
  *experiment*. Gate `PROSPECTIVE_FREEZE_PRECEDES_ALL_RUNS` is asserted, not demonstrated for the
  executing code.
- **SETTLING_COMMAND_OR_CALCULATION**
  `python3 -c "import hashlib,os;C='/home/claude/edl/PQEC01/code';h=hashlib.sha256();[ (h.update(f.encode()),h.update(open(os.path.join(C,f),'rb').read())) for f in sorted(['pqec01_design.py','pqec01_freeze.py','pqec01_observer.py','pqec01_qualify.py'])];print(h.hexdigest())"`
- **MINIMUM_REQUIRED_CHANGE** Either (a) publish a second, post-run `EXECUTION_HASH` covering
  `pqec01_run.py` plus the engine files, with the statement that it could not be frozen in advance
  because the runner did not yet exist; or (b) state in the freeze that `METHODS_HASH` covers
  design + observer only, and name the un-covered files.

---

### F02 — the source-equivalence test cannot detect a reordering or an addition

- **ID** F02
- **ATTACK** A2 (observer inertness)
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** C1 commit: "Checked by normalized source-text equality"; qualification
  `SOURCE_EQUIVALENCE.VERBATIM_SUBSET = True`, `UNDECLARED_DIFFERENCES = 0`.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_qualify.py:49-82`, decisive lines
  `:63-74` (`for l in eng_loop: if l in obs_loop: continue`) and `:79`
  (`"VERBATIM_SUBSET": len(missing) == 0`).
- **EXACT_NUMBERS** The test is a one-directional **set-membership** test over 14 engine lines and
  33 observer lines. Re-running the shipped predicate on mutated observer text:
  - counter block (`self.hops_offered[...] += …`, `self.hops_blocked[...] += …`) moved to **after**
    the `continue` → `VERBATIM_SUBSET = **True**` (undetected);
  - extra engine-state write `self.n["Y"][0, 0] += 1` appended → `VERBATIM_SUBSET = **True**`
    (undetected);
  - `continue` deleted → `VERBATIM_SUBSET = False` (the only mutation it catches).
- **WHY_IT_MATTERS** The brief's specific concern — the position of the `hops_offered` /
  `hops_blocked` update relative to the `continue` — is exactly the mutation this test is blind to.
  The qualification's own headline evidence for the highest-risk code in the programme is not
  evidence for the property it names.
- **SETTLING_COMMAND_OR_CALCULATION** Independent order-sensitive alignment (this review) shows the
  shipped code IS correct: engine physics lines 1–14 appear in the observer in the same relative
  order, with the counter block at engine index 7–9 preceding `continue` at index 11 in both. See
  `SUPPORTING CALCULATION 1`.
- **MINIMUM_REQUIRED_CHANGE** Replace the set test with an ordered `difflib` alignment of the two
  normalized statement sequences after deleting only `pq_*`, `del` and the two declared
  bookkeeping lines, and assert equality of the resulting sequences in both directions.

---

### F03 — the static mutation audit asserts a location it never checks, and its RNG detector is incomplete

- **ID** F03
- **ATTACK** A2
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** `STATIC_MUTATION_AUDIT.ENGINE_STATE_WRITES_ARE_ONLY_IN_THE_DECLARED_VERBATIM_LOOP = True`;
  `RNG_CALL_COUNT = 1`.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_qualify.py:104-107` (RNG name list),
  `:112-115` (the "only in the declared verbatim loop" predicate).
- **EXACT_NUMBERS** The predicate tests only the *attribute name* (`n[…]`, `hops_offered`,
  `hops_blocked`) and never the line number, although the walker records `lineno` at `:97, :99, :103`.
  A write to `self.n[...]` anywhere in the module satisfies it. The RNG detector matches only
  `{"binomial","random","integers","choice","normal","uniform","poisson"}` — it omits
  `hypergeometric` (which the engine's own `_exchange` uses,
  `/home/claude/ORR01/code/lawspec_v2.py:59,122`), `standard_normal`, `permutation`, `shuffle`.
  It also misses `ast.AugAssign` with an `Attribute` target and every in-place numpy method
  (`.fill`, `.__iadd__` through an alias, `np.add.at`).
- **WHY_IT_MATTERS** Two of the three qualification instruments therefore prove less than their
  field names claim. Only the differential fixture test carries real weight.
- **SETTLING_COMMAND_OR_CALCULATION** Read `pqec01_qualify.py:112-115`; note `w["line"]` is present
  in each dict and unused.
- **MINIMUM_REQUIRED_CHANGE** Assert `w["line"]` falls inside the `_diffuse` Y branch
  (`pqec01_observer.py:95-113`) for every engine-state write, and add `hypergeometric`,
  `standard_normal`, `permutation`, `shuffle` and `AugAssign`-on-`Attribute` to the walker.

---

### F04 — fixture coverage of the re-implemented loop is four orders of magnitude below the science

- **ID** F04
- **ATTACK** A2
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** C1 commit: "Seven differential fixtures … agree BIT-FOR-BIT"; the claim that
  `L = 5`, 8 steps and 7 fixtures qualify the verbatim Y sub-shift loop.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_qualify.py:39-41` (`FIXTURE_SEEDS`,
  `FIXTURE_STEPS = 8`, `FIXTURE_L = 5`), `:207-210` (the grid);
  `/home/claude/edl/PQEC01/out/PQEC01_INSTRUMENTATION_TESTS.json → TOTAL_Y_HOPS_IN_FIXTURES`.
- **EXACT_NUMBERS** Fixtures: 7 × 8 steps × 4 sub-shifts = **224** Y sub-shift executions;
  `TOTAL_Y_HOPS_IN_FIXTURES = **7**` accepted-branch executions; `MAX_nY_IN_FIXTURES = 5`;
  `distinct_Y_cells_max` ≤ 4. Scientific runs (recomputed from all 128 archives):
  **1 112 091** Y `_diffuse` calls → **4 448 364** sub-shift executions; **125 582** offered Y hops;
  **125 538** accepted (`yhop` column 6, 125 537 ledger rows); **44** blocked Y hops across
  **34** worlds (max 4 in one world). Coverage ratio 224 / 4 448 364 = **1 : 19 859**;
  accepted branch 7 / 125 538 = **1 : 17 934**. The qualification record reports **no blocked-hop
  count at all**, so the `movers.sum() > 0 ∧ ¬accepted.any()` path — the only path on which the
  counter placement relative to `continue` is observable — is not shown to have been exercised.
  Domain: `L = 5` (25 cells) vs `L = 36` (1296); 8 steps vs up to 11 000.
- **WHY_IT_MATTERS** Bit-exactness is only as strong as the branches it visits. The one branch the
  brief singles out is the one neither instrument covers.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/PQEC01/review/work/a2_hops.py`
  (reads the `yhop` and `capacity` keys of all 128 archives; `offered − blocked = accepted`
  checks out: 125 582 − 44 = 125 538).
- **MINIMUM_REQUIRED_CHANGE** Add one non-scientific fixture with `cap_override` low enough to force
  blocked Y hops (assert `hops_blocked["Y"] > 0` in both arms) and report the blocked count per
  fixture in `PQEC01_INSTRUMENTATION_TESTS.json`.
  **Mitigation to record:** the counters are declared write-only
  (`/home/claude/OBTC02/code/engine_obtc.py:132`) and `pqec01_analyse.py:42-55` never reads the
  `capacity` key, so a counter error could not reach any PQEC01 result.

---

### F05 — the firewall's own permitted quantity reveals the outcome

- **ID** F05
- **ATTACK** A3 (outcome firewall)
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** Freeze §11: "During execution, inspect only: process return code, expected file
  existence, file size, schema, checksum, the technical-validity flags"; C3 commit: "The outcome
  firewall held for the whole execution."
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_run.py:134-139` (the ledger record,
  including `steps_recorded` at `:137` and `seconds` at `:139`), `:175-178` (the live print, which
  emits `bytes=`), `/home/claude/edl/PQEC01/out/PQEC01_RUN_LEDGER.jsonl`.
- **EXACT_NUMBERS** Over all 128 ledger rows: `corr(bytes, steps_recorded) = **0.9992**`;
  `corr(seconds, steps_recorded) = **0.9965**`. Phase-B only: 0.9992 and 0.9968. Range:
  `B_B1_i038_s945497148` → 270 steps / **244 746 bytes** / 0.77 s;
  a horizon world → 11 000 steps / **10 245 129 bytes** / ≈37 s. 42 of 128 worlds stopped early.
  `steps_recorded` itself is written to the live-appended ledger and is not on the permitted list.
- **WHY_IT_MATTERS** File size is on the permitted list, is printed for every world as it lands, and
  determines the stop step to within a step — hence EXTINCT vs HORIZON vs PREMATURE_THIRD_CENTRE.
  The firewall as specified cannot hold; the permitted metadata *is* the outcome.
- **SETTLING_COMMAND_OR_CALCULATION** `numpy.corrcoef` over the ledger's `bytes` and
  `steps_recorded` columns (script in `work/`, reproduced above).
- **MINIMUM_REQUIRED_CHANGE** Remove `bytes` and `seconds` from the permitted list, or pad every
  archive to a fixed size before the checksum is taken. Record, as this review does, that **no
  action was taken on the leak**: all 128 frozen seeds ran exactly once, `RESERVES_USED = 0`, no
  world was re-run or replaced, and `pqec01_analyse.py` was committed at C3 before it was run.

---

### F06 — the declared scope of the exposure-phase fix is false

- **ID** F06
- **ATTACK** A5 (step-phase identity)
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** `pqec01_analyse.py:96-100`: "`scalars` is retained only for the stop-rule
  variables, which are post-step by definition"; C4 commit: "the `ycells` ledger … is used instead".
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_analyse.py:119-121`
  (`mean_nSY`, `mean_free`, `mean_N_X` from `col(d, …)`), `:244-251` (Phase-B `mean_Q_founder`,
  `mean_nSY`, `mean_free`, `mean_N_X` from `col(d, …)`), `:331`, `:342` (those three feed
  `feedback()`).
- **EXACT_NUMBERS** `mean_nSY`, `mean_free`, `mean_N_X` are **not** stop-rule variables (the frozen
  stop rules are `N_Y`, `n_centres`, integrity, horizon) yet still come from the post-step
  `scalars` array. `mean_Q_founder` (Phase B, `:244`) is an exposure quantity taken post-step.
  Size of the phase error, recomputed over all 40 Phase-A worlds: event-aligned mean exposure
  **2.8730222222** vs post-step **2.4699694444** → **+16.32 %**; 39 of 40 worlds differ; max
  per-world difference **0.536111**.
- **WHY_IT_MATTERS** The named exposure quantities are clean — `E_w`, `S_w`, the transition kernel
  (all from `ycells` columns 7/8), the radial profile (from the field) and the region's LCB all pass.
  But the comment claims a stronger property than the code delivers, and the feedback analysis, the
  only place `mean_nSY` / `mean_free` / `mean_N_X` are used for a scientific claim, still runs on
  post-step data.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/PQEC01/review/work/a5_a9_phaseA.py`.
- **MINIMUM_REQUIRED_CHANGE** Either recompute `mean_nSY`/`mean_free`/`mean_N_X`/`mean_Q_founder`
  from the reconstructed field at the pre-reaction phase, or narrow the comment to
  "`scalars` is retained for the stop-rule variables and for the three distribution-level feedback
  summaries, which are compared post-step on both sides."

---

### F07 — `*_founder` scalars are not the founder's

- **ID** F07
- **ATTACK** A5 / A6
- **SEVERITY** COSMETIC
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** The scalar names `Q_founder`, `nSY_founder`, `free_founder`, `nX_founder`,
  `candY_founder`.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_run.py:84-88` (`fy, fx = cells[0]`),
  `:27-29` (`SCALARS`); consumed at `pqec01_analyse.py:244`.
- **EXACT_NUMBERS** `cells` comes from `np.nonzero(nY)` (row-major), so `cells[0]` is the
  lexicographically smallest occupied Y cell, not the founder. Phase A is unaffected (exactly one Y
  cell at every one of 11 000 steps in all 40 worlds). Phase B has ≥2 occupied Y cells at
  **109 409** steps across 34 worlds, where `cells[0]` is the descendant roughly half the time.
- **WHY_IT_MATTERS** `mean_Q_founder` is published for all 88 Phase-B worlds under a name that
  asserts lineage the engine cannot supply — the very limit the disposition's `OBJECT_2` names.
- **SETTLING_COMMAND_OR_CALCULATION** `numpy.nonzero` ordering; multi-cell step counts from
  `python3 /home/claude/PQEC01/review/work/a10_phaseB.py "B_*"`.
- **MINIMUM_REQUIRED_CHANGE** Rename to `Q_first_cell`, … , or drop `mean_Q_founder` from the
  Phase-B summaries.

---

### F08 — `descendant_exposure_rows` is not a count of descendant rows

- **ID** F08
- **ATTACK** A6 (lineage-label ambiguity) / A10
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** `PQEC01_FINAL_DISPOSITION.json → PHASE_B_TOTALS.descendant_exposure_rows`
  = {B1 125 574, B2 118 757}; gate `PHASE_B_REAL_DESCENDANT_EXPOSURE_RECORDED`.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_analyse.py:225`
  (`desc = [r for r in yc if r[0] >= first_birth >= 0]`), `:254`, `:563`, `:581-582`.
- **EXACT_NUMBERS** The predicate selects **every** `ycells` row at or after the first birth step,
  including the founder's own row at every such step. Published total **244 331**. Recomputed from
  the raw archives, the number of rows at a cell other than the row-major-first occupied Y cell is
  **112 223** (B1 **52 309**, B2 **59 914**) — the published figure overstates by **2.18×**.
- **WHY_IT_MATTERS** The gate is `sum(desc_rows) > 0`, which is satisfied by a single founder row
  after a single birth, so the gate does not test what its name says. The headline number in the
  disposition is 2.18× the real one.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/PQEC01/review/work/a10_sep.py`
  (`total non-first-cell rows at multi steps: 112223`).
- **MINIMUM_REQUIRED_CHANGE** Define
  `descendant_local_rows = Σ_t max(0, n_occupied_Y_cells(t) − 1)` and republish; make the gate
  require ≥1 such row in ≥1 world at each Phase-B point.

---

### F09 — `separation_delay_after_first_birth` assumes the separating pair came from the first birth

- **ID** F09
- **ATTACK** A6
- **SEVERITY** COSMETIC
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** `PQEC01_PHASE_B_WORLD_SUMMARIES.json → separation_delay_after_first_birth`;
  C4 commit: "measured median delay from first birth to two centres is 111 steps".
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_analyse.py:239-240`.
- **EXACT_NUMBERS** 18 of 34 birth-worlds had more than one birth event; **2 of 34** had more than
  one birth event *before* separation, so the delay is attributed to a lineage that may not be the
  separating one. **0 of 34** had a Y death between the first birth and separation. Dropping the
  2 ambiguous worlds moves the median from **111.0** to **107.0**.
- **WHY_IT_MATTERS** Small in magnitude, but the field name asserts a parent–child relation the
  engine cannot supply.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/PQEC01/review/work/a6_a8.py`.
- **MINIMUM_REQUIRED_CHANGE** Rename to `steps_from_first_birth_to_two_centres` and report the
  2-world ambiguity.

---

### F10 — a decision gate is decided by a pooled step count

- **ID** F10
- **ATTACK** A7 (frame pseudoreplication)
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** Gate `NO_FRAME_PSEUDOREPLICATION`; freeze §9 "uncertainty: world-level; …
  never N_frames"; freeze `INDEPENDENT_UNIT = "ONE WORLD. Frames, cells, particles and event rows
  are never independent experimental units."`
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_analyse.py:318`
  (`"IDENTIFIED_STATES": [… if Ntr[i].sum() >= 30]`), consumed at `:578-579` by gate
  `TWO_Y_OPERATOR_IDENTIFIED`; `:584` (`"NO_FRAME_PSEUDOREPLICATION": True` — a hardcoded literal).
- **EXACT_NUMBERS** `Ntr` row sums at B1 discovery: **105 567 / 5 391 / 28 345 / 0 / 0**; at B2:
  **241 396 / 7 083 / 45 316 / 0 / 0**. These are step-to-step transitions, not worlds. They come
  from **9 of 29** discovery worlds at B1 and **12 of 28** at B2. One world
  (`B_B1_i039_s950085585`) supplies **8 703 of 28 351 = 30.7 %** of B1's separated steps; at B2 the
  top world supplies **7 419 of 45 328 = 16.4 %**. The threshold "≥ 30" is met at the world level by
  9 and 12 worlds, not by 5 391 and 7 083 independent observations. Consecutive steps in a
  co-location episode are near-perfectly autocorrelated.
- **WHY_IT_MATTERS** The gate the freeze installed specifically to forbid this is asserted as a
  literal `True` in the same function that violates it. Recomputed honestly the gate would be
  `False`, giving 10 of 13 (the terminal disposition string is unchanged).
- **SETTLING_COMMAND_OR_CALCULATION** Per-world contribution table in this review
  (`PQEC01_PHASE_B_WORLD_SUMMARIES.json → steps_two_centres` grouped by `split`).
- **MINIMUM_REQUIRED_CHANGE** Change the identification criterion to "≥ 10 worlds contribute ≥ 1
  visit to the state", and compute `NO_FRAME_PSEUDOREPLICATION` instead of asserting it.

---

### F11 — the published operators carry no uncertainty at all

- **ID** F11
- **ATTACK** A7
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** C4 commit: "a 25-state event-aligned exposure transition kernel with
  P(stay at Q=0) = 0.8208"; `PQEC01_ENVIRONMENT_OPERATOR.json → TRANSITION_MATRIX`.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_analyse.py:104-106`
  (`np.add.at(k, (q[:-1], q[1:]), 1.0)`; `kern_acc` summed across worlds), `:129`
  (`K = kern_acc / rowsums`), `:293-309` (`Ntr` summed across worlds), `:177`.
- **EXACT_NUMBERS** The Q kernel pools 40 worlds × 9 000 steps = **360 000** transitions into one
  matrix with no world-level standard error. `_iat` (an integrated-autocorrelation-time estimate) is
  computed per world at `:123` and stored as `iat_Q_founder` but is **never used** to inflate any
  uncertainty. `row_stochastic = True` at `:177` is true by construction (K is formed by dividing
  each row by its own sum) and is nevertheless one of four conditions of gate
  `PHASE_A_SPATIAL_OPERATOR_IDENTIFIED` (`:552-556`).
- **WHY_IT_MATTERS** Both objects the programme calls "the operator" are point estimates with no
  error bars, and one of the four conditions certifying the Phase-A operator is a tautology.
- **SETTLING_COMMAND_OR_CALCULATION** Read `:177` and `:552-556`; note `iat_Q_founder` appears in
  `PQEC01_PHASE_A_WORLD_SUMMARIES.json` and nowhere else.
- **MINIMUM_REQUIRED_CHANGE** Publish per-world kernels and a world-level standard error on each
  reported entry (at minimum on `P_stay_zero`), and drop `row_stochastic` from the gate.

---

### F12 — held-out validation worlds feed the candidate region

- **ID** F12
- **ATTACK** A8 (discovery/validation leakage)
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** Freeze §8 `VALIDATION_IS_NOT_TOUCHED_UNTIL_THE_OPERATOR_IS_FROZEN = true`;
  `pqec01_analyse.py:3-4` "the operator is identified on DISCOVERY worlds alone".
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_analyse.py:439-465` — the loop at
  `:440-450` iterates **all** `blk["PER_WORLD"]` with no `split` filter; `tau` at `:465`;
  `MEASURED_INPUTS` at `:452-463`; `tau` enters criterion C3 at `:474`.
- **EXACT_NUMBERS** `median_separation_delay_steps = 111.0` is the median over **34** worlds, of
  which **13 are VALIDATION**. Discovery-only median = **83.0** (n = 21). Region maximin margin:
  published (τ = 111) **−0.152828**; discovery-only (τ = 83) **−0.153881**; frozen τ = 125
  **−0.152301**. `total_Y_births = 56`, `worlds_reaching_two_centres = 34`,
  `mean_colocated_step_fraction = 0.1558` and `empirical_separation_rate_per_world = 0.3864` all
  pool the 31 Phase-B validation worlds.
- **WHY_IT_MATTERS** `CANDIDATE_REGION_POSITIVE_WIDTH` is a decision gate; its inputs are supposed
  to be discovery-only. The verdict does not change (empty either way), but the published
  τ = 111 — the number the C4 message calls "an independent 11 % check" — is a leaked statistic
  that moves to 83 on the discovery set alone.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/PQEC01/review/work/a6_a8.py`.
- **MINIMUM_REQUIRED_CHANGE** Filter `pb` to `split == "DISCOVERY"` inside `candidate_region()`, and
  republish τ, the region margin and the "independent check" claim on the discovery set.

---

### F13 — the frozen Phase-A holdout is declared and then never used

- **ID** F13
- **ATTACK** A8
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** Freeze §8 table "A: discovery 31, validation 9"; gate
  `PHASE_A_SPATIAL_OPERATOR_IDENTIFIED`.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_analyse.py:63-182` — `phase_a()`
  never reads `m["split"]`; `:429-430` — `candidate_region()` takes `E` and `S` over
  `pa["PER_WORLD"]`, i.e. all 40; `:552-556` — the gate.
- **EXACT_NUMBERS** The freeze allocated **31 discovery / 9 validation** Phase-A worlds
  (`ANALYSIS_SPLIT.REALISED.A`). All **40** enter `mean_E_w = 2.8730222222`,
  `relative_SE = 0.0426725876`, the radial profile, the Q kernel and the region's
  `one_sided_95_LCB_of_mean_exposure = 2.6713463862`. Zero Phase-A worlds are held out.
- **WHY_IT_MATTERS** The Phase-A spatial operator — the one operator the programme claims to have
  identified — has **no out-of-sample check whatever**, contrary to a rule the freeze states
  explicitly. Note this is the *opposite* error from F12: Phase B holds out and then leaks; Phase A
  declares a holdout and consumes it.
- **SETTLING_COMMAND_OR_CALCULATION** `grep -n 'split' pqec01_analyse.py | sed -n '1,20p'` — the
  only `split` filter in the file is at `:298` inside `operator()`.
- **MINIMUM_REQUIRED_CHANGE** Either fit the Phase-A operator on the 31 discovery worlds and report
  `mean_E_w` and the radial profile on the 9 validation worlds as a held-out check, or delete the
  Phase-A split from the freeze table and state that Phase A is a single-set calibration.

---

### F14 — the two declared fixes were made after the validation numbers were written to disk, and one flips a validation verdict

- **ID** F14
- **ATTACK** A9 (refitting after validation)
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** C4 commit: "Two defects in this analysis were found and fixed **before the
  disposition was written**"; "It was NOT refitted after seeing validation; that is the retune the
  freeze forbids."
- **EXACT_FILE_AND_LINES** `git diff 7d97205 d61e9a3 -- PQEC01/code/pqec01_analyse.py`; the two
  fixes at `/home/claude/edl/PQEC01/code/pqec01_analyse.py:95-107` (exposure phase) and `:386-395`
  (world-level SE in TEST 2).
- **EXACT_NUMBERS** Filesystem and bytecode forensics, reasoning explicitly from the chronology:
  | time (UTC) | evidence | event |
  |---|---|---|
  | 23:58:27.452 | last raw `.npz` mtime | 128th start finishes |
  | 23:59:35 | git commit `7d97205` | **C3**: `pqec01_analyse.py` v1 committed, **29 995 bytes** |
  | **00:01:33.211** | `out/` **directory** mtime | last file *created* in `out/` — i.e. the nine analysis outputs, ending with `PQEC01_FINAL_DISPOSITION.json`, were created here. **A complete analysis run, including `PQEC01_INTERNAL_VALIDATION.json`, finished at 00:01:33.** |
  | **00:02:20** | `__pycache__/pqec01_analyse.cpython-311.pyc` header `src_mtime` | `pqec01_analyse.py` **edited**, now **31 338 bytes** |
  | 00:05:25.737 | `.pyc` mtime | module imported (source still 31 338 B, mtime 00:02:20) |
  | **00:06:01.237** | source mtime | `pqec01_analyse.py` **edited again** → **34 322 bytes** |
  | 00:07:58.3 | eight output mtimes | final analysis run |
  | 00:08:39.113 | `PQEC01_FINAL_DISPOSITION.json` mtime = commit time | see **F16** |

  Directory mtime is updated by file *creation*, not by rewriting an existing file; every analysis
  output has an mtime later than 00:01:33, so all nine must have been created at or before
  00:01:33 by an earlier run of the C3 code.

  **Effect of the TEST 2 fix, recomputed exactly** from
  `PQEC01_PHASE_B_WORLD_SUMMARIES.json` (`steps_two_plus_Y`, `steps_recorded`, `split`):
  | | B1 | B2 |
  |---|---|---|
  | C3 pooled-step SE `sqrt(f_d(1−f_d)/Σ_V steps)` | f_d 0.242170, f_v 0.220343, se 1.525e-03, **z = −14.32, FAIL** | f_d 0.178376, f_v 0.040202, se 9.571e-04, **z = −144.37, FAIL** |
  | C4 world-level SE | f_d 0.135120, f_v 0.237753, se 0.0887025, **z = +1.157, PASS** | f_d 0.196632, f_v 0.045252, se 0.0536292, **z = −2.823, FAIL** |

  **The fix flips B1 TEST 2 from FAIL to PASS.** Gate `INTERNAL_VALIDATION_PASS` is `False` under
  both versions, so the disposition string is unchanged — but the C4 narrative "passes at B1
  (z = +1.16) and FAILS at B2", and with it the entire "generalizes at one parameter point and not
  the other" reasoning that names the missing object, exists only after the fix. Under the C3 code
  the sub-operator failed at **both** points, a strictly stronger negative.

  **Effect of the exposure fix**: Phase-A `mean_E_w` 2.4699694444 → 2.8730222222;
  `relative_SE` 0.0425545958 → 0.0426725876 (gate threshold 0.05 — passes under **both**, so
  `PHASE_A_SPATIAL_OPERATOR_IDENTIFIED` does not flip); region LCB 2.2970658775 → 2.6713463862,
  moving the maximin margin from **−0.159584** to **−0.152828**, i.e. **+0.006756 decades in the
  candidate's favour**; the region is empty under both.
- **WHY_IT_MATTERS** The freeze's prohibition is on *acting after the outcome is visible*, not on
  acting after the disposition is written. By the filesystem record the validation z-values existed
  on disk for 47 seconds before the first edit and for 4 min 28 s before the second. The commit
  message's formulation ("before the disposition was written") is true but does not answer the
  question the freeze asks.
- **DEFENCE THAT MUST BE RECORDED** Both fixes restore rules the freeze states **verbatim** and in
  advance: §9 `uncertainty` = "world-level; the estimator of any branch quantity is the mean over
  worlds and its standard error uses N_worlds, **never N_frames**", and §9
  `Q_POSITION = nX * min(nSY, free)` at the qualified pre-reaction phase (freeze §3 `RECORDS`,
  `PQEC01_INSTRUMENTATION_SPEC.md`). Neither fix had a free parameter, neither was chosen from a
  menu, and each moved the analysis *towards* the preregistered specification. The content was
  preregistered; only the timing was outcome-visible.
- **SETTLING_COMMAND_OR_CALCULATION**
  `stat -c '%n %y' /home/claude/edl/PQEC01/out /home/claude/edl/PQEC01/code/pqec01_analyse.py` and
  `python3 -c "import struct;print(struct.unpack('<IIII', open('/home/claude/edl/PQEC01/code/__pycache__/pqec01_analyse.cpython-311.pyc','rb').read(16)))"`
  (→ `src_mtime` 00:02:20, `src_size` 31338); TEST 2 recomputation from the published per-world
  summaries.
- **MINIMUM_REQUIRED_CHANGE** Amend the C4 record to state the true chronology: an analysis run
  completed at 00:01:33 and wrote validation outputs; both fixes were made after that; the TEST 2
  fix changes B1 from FAIL to PASS; the fixes' content was fixed in advance by freeze §9. Publish
  the pre-fix validation JSON alongside the post-fix one so a reader can see both.

---

### F15 — three no-refit / no-replacement claims are hardcoded literals in the file that was edited

- **ID** F15
- **ATTACK** A9
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** `PQEC01_INTERNAL_VALIDATION.json → NO_REFIT_AFTER_VIEWING_VALIDATION: true`;
  `PQEC01_FINAL_DISPOSITION.json → ACCOUNTING.NO_OUTCOME_DRIVEN_REPLACEMENT: true` and the four
  literal gates.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_analyse.py:417`
  (`"NO_REFIT_AFTER_VIEWING_VALIDATION": True`), `:542`, `:567`
  (`"PROSPECTIVE_FREEZE_PRECEDES_ALL_RUNS": True`), `:572`
  (`"NO_OUTCOME_DRIVEN_REPLACEMENT": True`), `:580`
  (`"FEEDBACK_CONTROLLED_OR_EXPLICITLY_MODELLED": True`), `:584`
  (`"NO_FRAME_PSEUDOREPLICATION": True`).
- **EXACT_NUMBERS** **4 of the 13** decision gates are Python literals that no data can falsify.
  `NO_REFIT_AFTER_VIEWING_VALIDATION` is asserted at line 417 of the same file whose lines 386–395
  were rewritten after validation outputs existed (F14).
- **WHY_IT_MATTERS** A gate that cannot fail is not a gate. `GATES_PASSED = 11` overstates the
  evidential content of the decision procedure by four.
- **SETTLING_COMMAND_OR_CALCULATION** `grep -n ': True,\?$' pqec01_analyse.py` restricted to the
  `gates` dict at `:566-584`.
- **MINIMUM_REQUIRED_CHANGE** Compute `NO_FRAME_PSEUDOREPLICATION` (see F10) and
  `FEEDBACK_CONTROLLED_OR_EXPLICITLY_MODELLED` (see F18); derive
  `PROSPECTIVE_FREEZE_PRECEDES_ALL_RUNS` from the git commit time vs the minimum raw mtime; derive
  `NO_OUTCOME_DRIVEN_REPLACEMENT` from `RESERVES_USED == 0 and len(ledger) == len(frozen)`.

---

### F16 — the committed disposition file is hand-edited and not reproducible from the committed code

- **ID** F16
- **ATTACK** A9
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** That `PQEC01_FINAL_DISPOSITION.json` is the output of the committed analysis;
  the disposition's own text "this disposition may only be used when a SPECIFIC missing field …
  is named. … The specific objects are named below."
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_analyse.py:616-622` — `main()`
  writes exactly `SECTION, ACCOUNTING, DECISION_GATES, GATES_PASSED, GATES_TOTAL, PHASE_B_TOTALS,
  CANDIDATE_DISPOSITION`; `/home/claude/edl/PQEC01/out/PQEC01_FINAL_DISPOSITION.json`.
- **EXACT_NUMBERS** The committed file carries **four additional top-level keys** that no line of
  the committed code produces: `MISSING_OBJECT_NAMED`, `EMPTY_REGION_IS_PREREGISTERED`,
  `PHASE_A_DESIGN_DISPERSION_MISS`, `POST_HOC_DESCRIPTIVE_X_ESTABLISHMENT`. mtime **00:08:39.113**
  vs **00:07:58.3** for the other eight analysis outputs — a 41-second gap, exactly the C4 commit
  timestamp. Re-running `python3 pqec01_analyse.py` deletes all four blocks, including the
  `MISSING_OBJECT_NAMED` block that the disposition's own text says the launcher requires.
- **WHY_IT_MATTERS** The single artefact that carries the terminal disposition is not reproducible
  from the sealed code. The numbers inside the hand-added block (19.66 %, 4.53 %, z = −2.82,
  z = +1.16) do check out against `PQEC01_INTERNAL_VALIDATION.json`, so this is a provenance defect,
  not a numerical one — but it is the disposition file.
- **SETTLING_COMMAND_OR_CALCULATION**
  `python3 -c "import json;print(sorted(json.load(open('/home/claude/edl/PQEC01/out/PQEC01_FINAL_DISPOSITION.json'))))"`
  vs `pqec01_analyse.py:616-622`; `stat -c '%y' PQEC01_FINAL_DISPOSITION.json`.
- **MINIMUM_REQUIRED_CHANGE** Move the four blocks into `main()` so the file regenerates byte-for-
  byte, or emit them into a separate, clearly hand-written `PQEC01_DISPOSITION_NARRATIVE.md`.

---

### F17 — every validation test and every gate threshold post-dates the data

- **ID** F17
- **ATTACK** A9
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** The label "PREDECLARED TEST 1 / 2 / 3" and "predeclared validation TEST 2".
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_analyse.py:378` ("PREDECLARED
  TEST 1"), `:384` ("PREDECLARED TEST 2"), `:398` ("PREDECLARED TEST 3"), thresholds at `:404`
  (`abs(z1) <= 2.0`), `:318` (`>= 30`), `:552-556` (`>= 29`, `< 0.05`);
  `/home/claude/edl/PQEC01/out/PQEC01_MASTER_FREEZE.json` top-level keys.
- **EXACT_NUMBERS** The freeze's 23 top-level keys contain `DECISION_GATES_ALL_REQUIRED_FOR_THE_
  POSITIVE_DISPOSITION` (13 gate **names**) and `FROZEN_ANALYSIS_FORMULAS` (13 formulas), but **no
  validation test, no test statistic, no |z| threshold and no gate threshold**. The first appearance
  of all of them is `pqec01_analyse.py`, first committed at **7d97205 (23:59:35)** — **68 seconds
  after** the last raw archive was written (23:58:27) and after all 128 outcome arrays existed on
  disk.
- **WHY_IT_MATTERS** "Predeclared" is the load-bearing word of the whole validation section. What is
  actually preregistered is a list of gate names and a list of formulas; the operational content —
  which statistic, which threshold, which unit — was authored in a window in which the data existed.
  In mitigation, 604 lines cannot have been written in 68 seconds, so the file was almost certainly
  drafted while the firewall was up; but nothing binds it.
- **SETTLING_COMMAND_OR_CALCULATION**
  `git log --diff-filter=A --format='%H %cd' -- PQEC01/code/pqec01_analyse.py` → `7d97205 …23:59:35`;
  `ls --time-style=full-iso -la /home/claude/PQEC01/raw | sort -k6 | tail -1` → `23:58:27.452`.
- **MINIMUM_REQUIRED_CHANGE** In any successor, commit the analysis script — with its statistics and
  thresholds — in the freeze commit itself, and include it in `METHODS_HASH` (see F01).

---

### F18 — the "no significant feedback" verdict is a Simpson's-paradox artefact

- **ID** F18
- **ATTACK** A11 (feedback comparison)
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** `PQEC01_FINAL_DISPOSITION.json → MISSING_OBJECT_NAMED.WHAT_IS_NOT_CLAIMED`:
  "measured feedback on nSY was -0.18% to -0.24% and not significant at the world level"; gate
  `FEEDBACK_CONTROLLED_OR_EXPLICITLY_MODELLED`; `PQEC01_FEEDBACK_ANALYSIS.json` `mean_N_X`
  `z = 1.321` (B1) and `z = 1.839` (B2), both `significant_at_2se: false`.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_analyse.py:329-368` (`feedback()`),
  `:580` (the literal gate).
- **EXACT_NUMBERS** Recomputed from the published per-world summaries, splitting Phase B by whether
  the world produced a Y birth (Phase A reference: mean N_X **111.0165**, sd 29.0723, n 40):

  | set | n | mean N_X | Δ vs A | z |
  |---|---|---|---|---|
  | B1, birth | 16 | **178.7557** | **+61.02 %** | **+5.653** |
  | B1, no birth | 28 | 93.0604 | −16.17 % | −2.002 |
  | B1, pooled (published) | 44 | 124.2224 | +11.90 % | +1.321 |
  | B2, birth | 18 | **168.6721** | **+51.93 %** | **+5.880** |
  | B2, no birth | 26 | 99.7230 | −10.17 % | −1.173 |
  | B2, pooled (published) | 44 | 127.9295 | +15.23 % | +1.839 |

  Medians: A **121.021**, B1 **119.852**, B2 **121.883** — a pooled *median* shift of −1.0 % and
  +0.7 % against a pooled *mean* shift of +11.9 % and +15.2 %. Same split on `mean_nSY`:
  A 2.955570; B1 birth **2.926750** (−0.98 %) vs no-birth 2.963564; B2 birth **2.931493** (−0.82 %)
  vs no-birth 2.960286 — four to five times the published pooled −0.18 % / −0.24 %.
  **Mechanism, not statistics:** the frozen point has `kX = 1.0`, so
  `p = min(1, kX·nX·nY) = 1` in every cell holding both X and Y
  (`/home/claude/OBTC02/code/engine_obtc.py:165-167`), and X production per step equals
  `Σ min(nSX, free)` over X-bearing Y cells. Two separated Y therefore roughly **double** the X
  source. Phase A has exactly one Y forever (`kY = 0`, `muY = 0`), max `mean_N_X` **125.47**;
  Phase B reaches **267.66**.
- **WHY_IT_MATTERS** The pooled two-sample z-test on a bimodal mixture of a −16 % subgroup and a
  +61 % subgroup has almost no power against the actual alternative, and its null result is reported
  as evidence that feedback is absent. Computed honestly the gate
  `FEEDBACK_CONTROLLED_OR_EXPLICITLY_MODELLED` should be `False` (10 of 13 gates; the disposition
  string is unchanged).
- **CONFOUNDS THAT MUST BE STATED, BOTH WAYS** (i) Conditioning on "had a birth" is conditioning on
  an outcome, and births are driven by `Q = nX · cand_Y`, so part of the +61 % is reverse causation
  (high X causes births). (ii) The step ranges are not matched: 35 of 44 B1 worlds stop before the
  horizon and **15 stop before `BURN_IN = 2000`**, in which case `pqec01_analyse.py:244-251` silently
  averages the whole record including the burn-in transient. Matching on step range
  (`steps_recorded == 11000`) gives B2 **+8.98 %, z = +1.03** (n = 37) and B1 **+47.85 %, z = +4.24**
  (n = 9). The defensible conclusion is therefore not "+61 % feedback" but **"the design cannot
  answer the feedback question"** — which is a stronger reason for the negative disposition than the
  one given.
- **SETTLING_COMMAND_OR_CALCULATION** Group `PQEC01_PHASE_B_WORLD_SUMMARIES.json` by
  `n_Y_births > 0` and by `steps_recorded == 11000` and recompute the two-sample z against
  `PQEC01_PHASE_A_WORLD_SUMMARIES.json`.
- **MINIMUM_REQUIRED_CHANGE** Publish the birth-stratified and horizon-matched comparisons beside
  the pooled one, replace "not significant" with "the comparison is confounded by outcome-dependent
  stopping and by the number of X sources and cannot be interpreted", and compute the feedback gate.

---

### F19 — the `mean_free` feedback channel is exactly constant by construction

- **ID** F19
- **ATTACK** A11
- **SEVERITY** COSMETIC
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** Freeze §9 `feedback_delta` names `free` as one of three feedback channels;
  `pqec01_analyse.py:347-350` calls it "variance … numerically degenerate", "`free` is pinned near
  CAP − occupancy in every world".
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_analyse.py:342-366`;
  `/home/claude/ORR01/code/lawspec_v2.py:90-129` (`_exchange`: every inserted unit displaces one
  already present, so occupancy is conserved cell by cell and step by step).
- **EXACT_NUMBERS** Phase-A `mean_free`: mean **9.996141975308642**, sd **exactly 0.0**, n = 40.
  This is the deterministic initial-condition constant
  `(CAP·L² − 6·L² − 1 − X_SEED)/L² = (20736 − 7776 − 5)/1296 = 12955/1296 = 9.996141975308642`
  with CAP 16, L 36, S0 3, X_SEED 4. Published Phase-B mean **9.996141975308644**, delta
  **1.7763568394e-15** (2 ULP), `se_of_delta` **2.08e-16**, **z = 8.530** (B1) and **6.793** (B2) —
  pure floating-point summation-order round-off.
- **WHY_IT_MATTERS** `free` is not "pinned near" a value; under LAWSPEC_V2_EXCHANGE it is an exact
  invariant, so it can never carry feedback information. The channel is uninformative by
  construction, which is a freeze defect (§9 names it) rather than an analysis defect; the analysis
  correctly disqualifies it, but publishes a z of 8.53 next to the disqualification.
- **SETTLING_COMMAND_OR_CALCULATION** `12955/1296` in exact arithmetic; `sd = 0.0` in
  `PQEC01_FEEDBACK_ANALYSIS.json → PHASE_A_REFERENCE.mean_free`.
- **MINIMUM_REQUIRED_CHANGE** Replace the z field with `null` when `VARIANCE_DEGENERATE`, and state
  the exact invariant (`Σ free = CAP·L² − initial occupancy`) rather than "pinned near".

---

### F20 — Phase A and Phase B are averaged over different, outcome-selected step ranges

- **ID** F20
- **ATTACK** A11
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** `COMPARISON_IS_DISTRIBUTION_LEVEL_NOT_PAIRED` — that the only caveat needed is
  the absence of pairing.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_analyse.py:244-251` — the
  `if n > BURN_IN … else …mean()` fallback; `:119-121` for the Phase-A side.
- **EXACT_NUMBERS** Phase A: `steps_recorded` = **11 000 for all 40 worlds**, mean over
  [2000, 11000). Phase B1: min **270**, median **3 998**, max 11 000; **35 of 44** below the horizon
  and **15 of 44 below `BURN_IN = 2000`**, for which the code averages [0, n) — including the
  burn-in transient — instead of [2000, n). Phase B2: min 4 236, median 11 000, **7 of 44** below
  the horizon, none below BURN_IN. Stop mix: B1 {EXTINCT 28, PREMATURE_THIRD_CENTRE 7, HORIZON 9};
  B2 {HORIZON 37, PREMATURE_THIRD_CENTRE 7}.
- **WHY_IT_MATTERS** The stopping is caused by the outcome (extinction, third centre), so the step
  window over which each world's summary is formed is outcome-dependent. Phase A and Phase B
  summaries are not commensurable, and the difference between B1 (+11.9 %) and B2 (+15.2 %) tracks
  the difference in stopping, not only the difference in `(kY, muY)`.
- **SETTLING_COMMAND_OR_CALCULATION** Distribution of `steps_recorded` per point in
  `PQEC01_PHASE_B_WORLD_SUMMARIES.json`; horizon-matched z values in F18.
- **MINIMUM_REQUIRED_CHANGE** Restrict the feedback comparison to a common window (e.g. worlds with
  `steps_recorded == T_HORIZON`, or the first 2000–4236 steps of every world), and never fall back
  to averaging across `BURN_IN`.

---

### F21 — the empty region is independent of the measurement; the "the measurement confirmed the arithmetic" claim is vacuous

- **ID** F21
- **ATTACK** A12(a) (terminal-disposition inflation)
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** C4 commit and `PQEC01_FINAL_DISPOSITION.json → EMPTY_REGION_IS_PREREGISTERED`:
  "The calibration replaced the mean-exposure proxy with measured, world-level quantities and the
  shortfall moved by 0.0015 decades. The boundary arithmetic was not the weak link; the measurement
  confirmed it." Also freeze §2: the boundary arithmetic "uses the parent's MEAN exposure as a
  proxy; the calibration replaces that proxy with measured … quantities, **which can move every
  boundary**."
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_analyse.py:466-482` (the criteria
  and the grid), `:507-526` (`MAXIMIN_ON_MEASURED_INPUTS`);
  `/home/claude/edl/PQEC01/out/PQEC01_CANDIDATE_REGION.json`.
- **EXACT_NUMBERS** The exposure enters only through `births = kY · LCB(E) · T_WINDOW` in C1 and
  through the same product in C3. Since `kY` is a free grid parameter bounded only by
  C4 (`kY·CAP·N_STAR ≤ 0.1 → kY ≤ 6.25e-4`) and by the grid range `[1e-6, 1e-2]`, only the
  **product** `kY·E` matters, so `E` is not identified by the criteria at all. Analytically:

  ```
  C1: kY·E·W ≥ MIN_EVENTS = 1
  C3: kY·E·W·(1−muY)^τ ≤ GAMMA_SEP = 0.5
  C1 ∧ C3 ⟹ (1−muY)^τ ≤ 0.5 ⟹ muY ≥ 1 − 0.5^(1/τ)
  C2: (1−muY)^11000 ≥ 0.5 ⟹ muY ≤ 1 − 0.5^(1/11000) = 6.301139e-05
  τ = 111 → muY ≥ 6.225112e-03   (contradiction, factor 98.8)
  τ = 125 → muY ≥ 5.529831e-03   (factor 87.8)
  τ =  83 → muY ≥ 8.316397e-03   (factor 132.0)
  ```

  So the region is empty **for every `kY` and every exposure**, for any τ in the observed range.
  Numerically, on the shipped 161 × 161 grid the maximin margin barely moves with the exposure LCB:
  0.5 → **−0.150068**; 1.0 → −0.151098; 2.2971 (pre-fix) → −0.159578; 2.6713 (published) →
  **−0.152820**; 3.1697 (the design proxy) → −0.152116; 5.0 → −0.150068; 20.0 → −0.152128 — a
  spread of 0.0095 decades over a **460-fold** range of exposure, i.e. pure grid quantization. On a
  1201 × 1201 grid over `kY ∈ [1e-9, 1e-1]` the margin converges to **−0.1514** for every LCB from
  0.5 to 200, with the optimum always at `kY·E·W ≈ 0.706`.
- **WHY_IT_MATTERS** The agreement "preregistered −0.1513 vs measured −0.1528" is presented as the
  calibration confirming the boundary arithmetic. It is an identity: the shortfall could not have
  moved. The freeze's own justification for running the calibration despite the preregistered empty
  region ("which can move every boundary") is arithmetically false. Consequently
  `CANDIDATE_REGION_POSITIVE_WIDTH` was **unsatisfiable by any outcome** from the moment C2 was
  committed, and with it the positive terminal disposition
  `PROSPECTIVE_Q_ENVIRONMENT_OPERATOR_IDENTIFIED`.
- **SETTLING_COMMAND_OR_CALCULATION** The three-line implication above; and the LCB sweep in
  `/home/claude/PQEC01/review/work/` (reproduced numbers above).
- **MINIMUM_REQUIRED_CHANGE** Replace the claim with: "the region is empty as a matter of frozen
  arithmetic — C1 ∧ C3 require `muY ≥ 1 − 0.5^(1/τ)` while C2 requires
  `muY ≤ 1 − 0.5^(1/T_HORIZON)`, incompatible by a factor of 98.8 for every `kY` and every
  exposure. The measurement neither confirmed nor could have refuted it." Mark
  `CANDIDATE_REGION_POSITIVE_WIDTH` as a structurally unsatisfiable gate and hand the contradiction
  (separation timescale τ ≈ 111 vs required founder lifetime 11 000) to the successor as the object
  to be redesigned.

---

### F22 — a headline count in the sealed commit message matches no computed quantity

- **ID** F22
- **ATTACK** A12(a)
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** C4 commit: "Here: 56 real Y births across 88 active-Y worlds, 34 worlds
  reaching two spatial centres, **16474 steps of measured co-location** and 73674 steps of measured
  SEPARATED two-Y state".
- **EXACT_FILE_AND_LINES** Commit `d61e9a34367b42bd7534647ad9802a9892639f31` message;
  `/home/claude/edl/PQEC01/out/PQEC01_ENVIRONMENT_OPERATOR.json → DISCOVERY_ONLY.*.STATE_OCCUPANCY_STEPS`;
  `PQEC01_FINAL_DISPOSITION.json → PHASE_B_TOTALS.colocated_steps`.
- **EXACT_NUMBERS** Every candidate quantity, recomputed:
  discovery-only `TWO_Y_COLOCATED` occupancy = 5 391 + 7 083 = **12 474**;
  all-worlds `steps_colocated_one_centre` = 7 814 + 9 517 = **17 331**;
  discovery-only `steps_colocated_one_centre` = 5 391 + 7 083 = 12 474;
  all-worlds `steps_with_multiple_occupied_Y_cells` = 50 857 + 58 552 = 109 409.
  **None equals 16 474.** The companion figure **73 674** *is* exactly the discovery-only
  `TWO_Y_SEPARATED` occupancy (28 349 + 45 325). So the natural partner of 73 674 is 12 474, and
  16 474 appears to be a transcription of it, inflating the number by **32.1 %**.
  The same sentence mixes **all-world** counts (56 births, 88 worlds, 34 worlds) with
  **discovery-only** step counts without saying so.
- **WHY_IT_MATTERS** This is the sealed record of what the calibration achieved. One of its four
  headline numbers is unsupported and the sentence silently changes denominator mid-way.
- **SETTLING_COMMAND_OR_CALCULATION**
  `python3 -c "import json;d=json.load(open('/home/claude/edl/PQEC01/out/PQEC01_ENVIRONMENT_OPERATOR.json'))['DISCOVERY_ONLY'];print(sum(v['STATE_OCCUPANCY_STEPS']['TWO_Y_COLOCATED'] for v in d.values()), sum(v['STATE_OCCUPANCY_STEPS']['TWO_Y_SEPARATED'] for v in d.values()))"`
  → `12474 73674`.
- **MINIMUM_REQUIRED_CHANGE** Correct to "12 474 discovery steps of measured co-location and 73 674
  discovery steps of measured separated two-Y state (17 331 and 92 649 over all 88 worlds)".

---

### F23 — "an independent 11 % check on TAU_SEP" is over-read

- **ID** F23
- **ATTACK** A12(a)
- **SEVERITY** SUBSTANTIVE
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** C4 commit: "The measured median delay from first birth to two centres is 111
  steps against the analytically frozen TAU_SEP = 125 — an independent 11% check on a constant that
  had only ever been derived."
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_analyse.py:439-465`;
  `/home/claude/edl/PQEC01/code/pqec01_design.py:20` (`TAU_SEP = CORE_R**2/(4*D_REL) = 125.0`);
  `PQEC01_CANDIDATE_REGION.json → SEPARATION_TIME_USED`.
- **EXACT_NUMBERS** The 111 is (a) a **median** compared against a mean-first-passage scale;
  (b) computed over **all 34** birth-worlds including the **13 validation** worlds — the
  discovery-only median is **83.0** (n = 21), a **−33.6 %** deviation from 125, not −11.2 %;
  (c) censored: 14 of 88 Phase-B worlds stopped at `PREMATURE_THIRD_CENTRE` and 28 B1 worlds went
  extinct, and `pqec01_analyse.py:444-446` further drops any world with delay ≤ 0; (d) attributed to
  the first birth even where a later birth produced the separating pair (F09, 2 of 34 worlds; median
  moves 111 → 107 when they are dropped). A statistic that reads 83, 107 or 111 depending on which
  subset is used is not an 11 % agreement with a derived constant.
- **WHY_IT_MATTERS** This is offered as the one place the calibration independently validated a
  frozen analytic constant.
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/PQEC01/review/work/a6_a8.py`
  (`median delay DISCOVERY-only = 83.0 (n=21) ; published (all splits) = 111.0`).
- **MINIMUM_REQUIRED_CHANGE** Report the discovery-only median (83), the all-worlds median (111), the
  number censored, and a world-level interval; withdraw "independent 11 % check" or restate it as
  "the measured separation delay is of the same order as the derived τ = 125, with a
  split-dependent median between 83 and 111".

---

### F24 — "Phase A spatial operator identified" rests on three near-vacuous conditions and one real one

- **ID** F24
- **ATTACK** A12(a)
- **SEVERITY** COSMETIC
- **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** Gate `PHASE_A_SPATIAL_OPERATOR_IDENTIFIED = True`; C4 commit "Phase A spatial
  operator identified over 40 worlds".
- **EXACT_FILE_AND_LINES** `/home/claude/edl/PQEC01/code/pqec01_analyse.py:552-556`.
- **EXACT_NUMBERS** The four conjuncts: `N_WORLDS >= 29` (40 by frozen design, cannot fail);
  `row_stochastic` (`np.allclose(K.sum(1)[K.sum(1)>0], 1.0)` where `K = kern_acc/rowsums` — true by
  construction); `relative_SE < 0.05` (**0.0426725876** — the only informative test, and it holds
  under the pre-fix exposure too at 0.0425545958); `isfinite(radial[1])` (3.0359). Separately, the
  freeze's own distribution-free floor came back empty:
  `distribution_free_lower_bound_10th_pct = **0.0**` and `worlds_with_positive_S_w = **0 of 40**` —
  every Phase-A world spends at least 10 % of its steps at `Q = 0`, and `min_E_w = 0.0`.
  `no_single_world_dominance` compares a one-world leave-out shift (2.8730/39 = 0.0736) against
  0.5·sd = 0.3877 and cannot fail here.
- **WHY_IT_MATTERS** "Identified" is doing a lot of work for a gate that reduces to one precision
  check, while the freeze's own quantile bound — the reason `N_A = 40` clears the "distribution-free
  10th-percentile floor of 29" — returned a vacuous 0.
- **SETTLING_COMMAND_OR_CALCULATION** Read `:552-556` and `:141-142`;
  `PQEC01_ENVIRONMENT_OPERATOR.json → PHASE_A_SPATIAL.WORLD_LEVEL`.
- **MINIMUM_REQUIRED_CHANGE** Drop `row_stochastic` and `N_WORLDS >= 29` from the gate, add the
  radial-profile monotonic-decay and kernel-stability checks that "identified" implies, and record
  that the distribution-free bound returned 0.

---

## THE FIVE ATTACKS THAT FAILED, IN DETAIL

### A2 — OBSERVER INERTNESS: ATTACK_REFUTED (the claim stands)

The re-implemented Y sub-shift loop (`/home/claude/edl/PQEC01/code/pqec01_observer.py:90-117`) was
aligned statement-by-statement, **in order**, against
`/home/claude/OBTC02/code/engine_obtc.py:142-156`:

| # | engine (`WorldOBTC._diffuse`) | observer (Y branch) |
|---|---|---|
| 1 | `rng = self.rng` | `rng = self.rng` (obs :94) |
| 2 | `for shift, ax in NEI:` | `for sub, (shift, ax) in enumerate(EN.NEI):` — the single declared difference; `EN.NEI` is the same tuple object, same order, same bound names, no rng consumed |
| 3 | `n = self.n[sname]` | identical (:96) |
| 4 | `movers = rng.binomial(np.maximum(n, 0), p_hop / 4.0)` | identical (:98) |
| 5 | `dest_free = np.roll(self.free(), -shift, axis=ax)` | identical (:99) |
| 6 | `accepted = np.minimum(movers, np.maximum(dest_free, 0))` | identical (:100) |
| 7-9 | `if sname in self.hops_offered:` + two `+=` | identical, **before** the `continue` (:101-103) |
| 10-11 | `if not accepted.any(): continue` | identical (:104-105) |
| 12 | `self.n[sname] = n - accepted + np.roll(accepted, shift, axis=ax)` | identical (:106) |
| 13-14 | `if self.track and sname == "X": self.tracker.move(...)` | identical (:107-108) |

- **RNG call order.** Exactly **one** `rng.binomial` per sub-shift in both, in the same position, on
  the same array shape, from the same generator (`self.rng`, bound once before the loop). The only
  other rng calls in the whole module: none (`RNG_CALL_COUNT = 1`, independently confirmed by
  reading the file). The observer's extra statements — `off0`, `blk0`, `before_all = …copy()`,
  `before = n.copy()`, `np.nonzero(accepted)`, the `pq_*` appends, `del` — consume no randomness and
  mutate no engine array.
- **Counter position relative to `continue`.** Correct: engine indices 7–9 precede index 11 in both.
  (The *test* that is supposed to establish this cannot — F02 — but the code is right.)
- **`self.free()` inside the loop.** Pure: `/home/claude/ORR01/code/kinetics.py:86-90`,
  `free() = sp.CAP - sum(self.n[k])`. Called once per sub-shift at the same point in both.
- **Can `self.track and sname == "X"` ever fire?** No. The branch is reached only after the guard
  `if sname != "Y": … return` at `pqec01_observer.py:78-89`, so `sname == "Y"` identically. The
  engine evaluates the same condition to `False` for Y, so the behaviour is identical; the line is
  dead in both. For `X`, `SX`, `SY` the observer delegates to `super()._diffuse` (:82), which is the
  engine's own code.
- **No other physics is overridden.** `_react` (:119-134), `_decay` (:136-145) and
  `_feed_and_outflow` (:147-154) each take read-only snapshots, call `super()`, and diff. The
  `observe.Recorder` passed to both arms is documented and verified write-only
  (`/home/claude/ORR01/code/observe.py:35-95`; no `rng`, no assignment into `w.n`).
- **The differential test** (`pqec01_qualify.py:124-158`) compares, at **every** step, the six
  species byte-for-byte, all **three** bit-generator states (`rng`, `rng_feed`, `tracker.rng`),
  `hops_offered`, `hops_blocked`, `births_total`, the step counter and the engine's own
  `state_hash()`. `ALL_BIT_EXACT = True` over 7 fixtures, with 18 Y births, 13 Y deaths and
  `max nY = 5`.
- **The observer file has not changed since it was qualified**: `pqec01_observer.py` mtime
  23:18:58.767 < qualification output 23:20:36.786 < first scientific archive 23:29:09.080, and the
  working tree is clean against `d61e9a3`.

**Verdict: OBSERVER_INERTNESS_HOLDS = YES.** The defects found (F02, F03, F04) are in the
*instruments that certify* inertness, not in inertness itself. They mean the claim rests on the
differential test alone, and that test's coverage of the duplicated loop is 1 : 17 934 of the
science by accepted-hop count.

### A10 — DESCENDANT-POSITION EXPOSURE: ATTACK_REFUTED (the claim stands)

Verified directly from the raw `.npz`, never from the summaries:

1. **More than one distinct Y cell at the same step.** Across all 88 Phase-B archives, **109 409**
   steps carry ≥2 `ycells` rows, in **34** worlds (B1 50 857 steps in 16 worlds; B2 58 552 in 18).
   Worked example, `B_B1_i000_s942104457`, step 2690, the two raw rows
   `(step, y, x, nY, nX, nSY, free, cand_Y, Q)`:
   `[2690, 12, 2, 1, 3, 0, 12, 0, 0]` and `[2690, 14, 7, 1, 8, 0, 5, 0, 0]` —
   two distinct cells, distinct `nX` (3 vs 8), distinct `free` (12 vs 5), distinct payloads.
2. **The rows carry that cell's own values.** For five worlds spanning the coverage range
   (`B_B1_i039_s950085585` 20 679 rows / 9 679 multi-cell steps; `B_B2_i011_s966153195`;
   `B_B1_i022_s960856267`; `B_B2_i008_s941377808`; `B_B2_i022_s966253201`) the field was
   reconstructed from `field0` + cumsum(`field_delta`) and **all six** of `nY`, `nX`, `nSY`,
   `free = max(CAP − Σ6, 0)`, `cand_Y = min(nSY, free)` and `Q = nX·cand_Y` matched the `ycells`
   payload **exactly** (`np.array_equal`, every row). In every one of the five, the number of
   `ycells` rows equalled the number of occupied Y cells in the field over all steps
   (20 679 = 20 679, etc.) — the ledger is lossless, no cell dropped, no cell duplicated.
   Engine invariants hold in the raw: `free.min() = 0`, `occ.max() = 16 = CAP`.
3. **The exposure is real, not all zero.** Of the **112 223** rows at a cell other than the
   row-major-first occupied Y cell, **44.7 %** carry `Q > 0` (per-world range 34.4 %–63.0 %), with
   per-world maximum `Q` between **24 and 28**.
4. **Separation events are real under the frozen definition.** The first step with ≥2 single-linkage
   clusters at toroidal Euclidean distance > `CORE_R = 5.0` was recomputed **independently from the
   `ycells` positions** with an independent union-find, for all 34 birth-worlds. It agrees with the
   published `separation_first_step` in **34 of 34** worlds (difference exactly 0 in every case),
   and the independently recomputed `max_pair_dist` matches the recorded scalar in **34 of 34**.
   The median delay 111.0 reproduces by both routes.

**Verdict: DESCENDANT_EXPOSURE_REALLY_RECORDED = YES.** The parent's central gap ("28 archives, no Y
descendant at any of 308 000 steps") is genuinely closed. What is *not* supported is the published
row count (F08) and the exact separation-delay attribution (F09, F12, F23).

### A4 — ACCOUNTING: ATTACK_REFUTED

All **128** frozen seeds regenerate byte-for-byte from
`seed = 940000000 + int(SHA256(parent_tip|program|phase|point|index)[:12],16) mod 50000000` with the
frozen deterministic collision rule (`A`, `B1`, `B2` all `regenerated == frozen: True`). Each appears
**exactly once** in `PQEC01_RUN_LEDGER.jsonl` (multiplicity histogram `{1: 128}`), 128 distinct tags,
`MISSING = []`, `UNEXPECTED = []`. The 15 reserve seeds are disjoint from the scientific band and
**none was used**. `TECHNICALLY_INVALID = []`, `engine_invariants_ok = true` for all 128. Five
randomly selected archives were re-hashed from disk: SHA-256 matches both the manifest and the
ledger, and the byte counts match, in 5 of 5.

### A8 (split rule) — ATTACK_REFUTED

`split_of(seed) = DISCOVERY if int(SHA256("SPLIT|"+parent_tip+"|"+seed)[:8],16) % 3 < 2 else
VALIDATION` is a function of the frozen seed only; it contains no outcome. Recomputed
independently, it reproduces the freeze's label for **128 of 128** seeds and the ledger's label for
**128 of 128**. Discovery and validation are disjoint in all three sets (A 31/9, B1 29/15, B2 28/16).
The Phase-A LCB feeding the region uses **no** Phase-B world. (The leaks found are elsewhere:
F12, F13.)

### A5 (step-phase identity) — ATTACK_REFUTED

`PQECWorld._react` (`pqec01_observer.py:119-129`) records `pq_field[st]` and the `ycells` rows at
`st = int(self.step)` **before** calling `super()._react()`. The step counter is incremented at the
end of `K.World._one_step` (`/home/claude/ORR01/code/kinetics.py:154-162`), after
`_feed_and_outflow`, so `st = t` while the four `_diffuse` calls for step `t` have completed and
`_react_core` has not started. In `_react_core`
(`/home/claude/OBTC02/code/engine_obtc.py:158-174`), `pair = nX * nY` and
`free0 = np.maximum(self.free(), 0)` are both evaluated **once, before** the X reaction, and
`self.n[prod] = self.n[prod] + births` **rebinds** the dict entry rather than mutating the array
`nX` points at — so the Y birth law is exactly
`Binomial(min(nSY, free0), min(1, kY·nX·nY))` on the recorded state. `ycells` columns 4, 5, 6, 7, 8
are precisely `nX`, `nSY`, `free`, `cand_Y`, `Q = nX·cand_Y` at that state, confirmed exactly
against the reconstructed field (A10 item 2). `STEP_LABEL_MAPPING.VERIFIED = true` with
pre-increment labels 0…7 and `w.step = 8`.
**Where post-step scalars remain**, they do not touch the quantities the brief names:
`E_w` and `S_w` (`:111-112`, from `ycells` col 8), the transition kernel (`:101-105`, `ycells`
col 8), the radial profile (`:76, :90`, from the field), the region LCB (`:429`, from `E_w`),
TEST 1 (`:253`, `_p_no_birth` reads `ycells` only) are all event-aligned. TEST 2 uses post-step
`N_Y`, but symmetrically on both discovery and validation, and `N_Y` is a frozen stop-rule variable
that the freeze itself calls post-step. The residual leakage is documented as F06/F07.

---

## A12 — THE DISPOSITION, ARGUED BOTH WAYS

### (a) Is the candidate claiming TOO MUCH?

| claim | verdict |
|---|---|
| "Phase A spatial operator identified" | **Over-read (F24).** The gate reduces to one precision test at 0.0427 against a 0.05 threshold; two of the four conjuncts cannot fail; the freeze's own distribution-free 10th-percentile bound returned **0.0** with **0 of 40** worlds positive. The radial profile and the kernel are real objects but carry **no uncertainty at all** (F11) and are pooled over 360 000 step transitions. |
| "the parent's central gap is closed" | **Supported.** 56 births, 112 223 verified descendant-cell exposure rows carrying that cell's own `(nX, nSY, free, cand_Y, Q)` at the event-aligned phase, checked against the field. This is the strongest thing the programme did. |
| "111 vs the analytically frozen 125 — an independent 11 % check" | **Over-read (F23).** Discovery-only median 83 (−33.6 %). Split-dependent, censored, median-vs-mean-scale. |
| "16474 steps of measured co-location" | **Unsupported (F22).** No computed quantity equals it; the discovery-only figure is 12 474. |
| "the measurement confirmed the [boundary] arithmetic" | **Vacuous (F21).** C1 ∧ C2 ∧ C3 are unsatisfiable for every `kY` and every exposure; the shortfall cannot move with the measurement. |
| "measured feedback … not significant at the world level" | **Wrong (F18).** Birth-worlds carry +61.0 % / +51.9 % more X (z = +5.65 / +5.88); the pooled null is a mixture artefact. |
| "the two-Y sub-operator generalizes at one parameter point and not the other" | **Exists only after the post-outcome fix (F14).** Under the C3 statistic it failed at both. |
| labelling everything `CANDIDATE_REGION_REQUIRING_DISJOINT_CONFIRMATION`, `NOT_A_CONFIRMED_WINDOW`, `POST_HOC_DESCRIPTIVE`, `DESIGN_DISPERSION_MISS` | **Correct and creditable.** The dispersion miss (sd 0.163 → 0.775, 4.76×; relative SE 0.81 % → 4.27 %) is disclosed rather than smoothed, and `N_A` was correctly not resized. |

### (b) Is the candidate too WEAK — should it have been `..._OPERATOR_IDENTIFIED`?

**No. ATTACK_REFUTED, on two independent grounds.**

1. **`CANDIDATE_REGION_POSITIVE_WIDTH` cannot be satisfied by any outcome** (F21). The positive
   disposition requires all 13 gates; this one is structurally unsatisfiable, so the positive
   disposition was unreachable from the moment the freeze was committed. The candidate is not being
   conservative — the gate set is degenerate. (This is a criticism of the freeze, not a licence to
   upgrade the disposition.)
2. **The failed validation test survives multiplicity.** Six tests were executed (3 at each of 2
   points). B2 TEST 2 has |z| = 2.8227 → two-sided p = **0.00476**; Bonferroni over 6 →
   **0.0286 < 0.05**. The other five have Bonferroni-adjusted p of 0.912, 1.000, 1.000, 1.000, 1.000.
   So "one test out of six, just noise" does not survive.
   *Counter-note in the candidate's favour, stated for completeness:* the TEST 2 statistic is a
   normal-approximation two-sample z on a per-world fraction that is exactly zero in **16 of 28**
   discovery and **10 of 16** validation worlds at B2. A normal approximation on that distribution
   is not trustworthy at p ≈ 0.005 in either direction. That argues the test **cannot decide**,
   which supports `NOT_IDENTIFIED`, not `IDENTIFIED`.

### (c) Is `EXISTING_ARCHITECTURE_FEEDBACK_PRECLUDES_CONTROLLED_WINDOW` correctly NOT used?

**Yes. ATTACK_REFUTED.** The strongest case for that label would run: the region is empty because
τ ≈ 111 (separation) is four orders of magnitude shorter than the 11 000 steps of founder survival
C2 demands, and that is an architecture property; and F18 shows real, large feedback (X source
doubling). But the label specifically asserts that **feedback** precludes a **controlled window**,
and neither element is established: (i) the emptiness is a timescale contradiction among C1/C2/C3
in which no feedback term appears (F21); (ii) the measured feedback, while large in birth-worlds,
is confounded by outcome-dependent stopping and by conditioning on the birth (F18/F20) and no
result shows preclusion **across the admissible region**, which is what the label requires. The
freeze's own text ("it is NOT structural preclusion") and the disposition's `WHAT_IS_NOT_CLAIMED`
block are correct on this point. Withholding the label is right.

### (d) Should the disposition have been `CALIBRATION_TECHNICALLY_INVALID`?

**No.** The freeze defines technical invalidity narrowly — corrupt serialization, process
interruption, observer schema failure, checksum failure, engine invariant violation. None occurred:
128/128 archives present with matching checksums, complete key schema, `free ≥ 0` and `occ ≤ CAP`
verified in the raw for the worlds inspected, and observer inertness holds. The provenance defects
(F01, F14, F16, F17) are serious but are not on that list.

---

## SUPPORTING CALCULATION 1 — order-sensitive alignment of the two `_diffuse` loops

Normalized (comments stripped, whitespace collapsed) statement sequences, observer-only lines
(`pq_*`, `del`, `ys, xs = …`, `for y, x in zip…`, `before = n.copy()`) removed:

```
--- engine (engine_obtc.py:142-156)      +++ observer (pqec01_observer.py:90-117)
+off0 = self.hops_offered.get(sname, 0)          <- observer bookkeeping, pure read
+blk0 = self.hops_blocked.get(sname, 0)          <- observer bookkeeping, pure read
+before_all = self.n["Y"].copy()                 <- pure copy, never read back
 rng = self.rng
-for shift, ax in NEI:
+for sub, (shift, ax) in enumerate(EN.NEI):      <- the ONE declared difference
 n = self.n[sname]
 movers = rng.binomial(np.maximum(n, 0), p_hop / 4.0)
 dest_free = np.roll(self.free(), -shift, axis=ax)
 accepted = np.minimum(movers, np.maximum(dest_free, 0))
 if sname in self.hops_offered:
 self.hops_offered[sname] += int(movers.sum())
 self.hops_blocked[sname] += int((movers - accepted).sum())
 if not accepted.any():
 continue
 self.n[sname] = n - accepted + np.roll(accepted, shift, axis=ax)
 if self.track and sname == "X":
 self.tracker.move(accepted, shift, ax)
```

All 14 engine statements appear in the observer **in the same relative order**; the three added
statements are pure reads/copies executed before the loop.

## SUPPORTING CALCULATION 2 — the region is empty for every exposure

```
C1: kY·E·W ≥ 1                        C2: (1−muY)^11000 ≥ 0.5      C3: kY·E·W·(1−muY)^τ ≤ 0.5
C1 ∧ C3  ⟹  (1−muY)^τ ≤ 0.5  ⟹  muY ≥ 1 − 0.5^(1/τ)
C2       ⟹  muY ≤ 1 − 0.5^(1/11000) = 6.301139e-05

τ = 111 (published)   : muY ≥ 6.225112e-03   vs   muY ≤ 6.301139e-05   ratio  98.8   EMPTY
τ = 125 (frozen)      : muY ≥ 5.529831e-03                             ratio  87.8   EMPTY
τ =  83 (discovery)   : muY ≥ 8.316397e-03                             ratio 132.0   EMPTY
```

Maximin margin on the shipped 161×161 grid, as a function of the exposure LCB:

| LCB(E) | 0.5 | 1.0 | 2.2971 (pre-fix) | 2.6713 (published) | 3.1697 (design proxy) | 5.0 | 20.0 |
|---|---|---|---|---|---|---|---|
| margin (decades) | −0.150068 | −0.151098 | −0.159578 | **−0.152820** | −0.152116 | −0.150068 | −0.152128 |

Spread 0.0095 decades over a 460× range of exposure — grid quantization. On a 1201×1201 grid over
`kY ∈ [1e-9, 1e-1]` the margin converges to −0.1514 for every LCB from 0.5 to 200.

---

## WHAT WOULD HAVE CHANGED THE DISPOSITION, AND DID NOT

| candidate load-bearing failure | result |
|---|---|
| observer not inert → everything invalid | **Refuted.** Verbatim in order; no extra rng; no engine mutation outside the declared loop; bit-exact on 7 fixtures over all three generator states. |
| descendant exposure not really recorded → `PHASE_B_REAL_DESCENDANT_EXPOSURE_RECORDED` false, headline claim void | **Refuted.** 112 223 verified descendant-cell rows; separation recomputed independently, 34/34 exact agreement. |
| a start missing, replaced or re-run → `CALIBRATION_TECHNICALLY_INVALID` | **Refuted.** 128 seeds, once each, 0 reserves, 5/5 checksums verified. |
| post-step scalar in `E_w` / kernel / radial / region / a validation test | **Refuted** for all five; residual leakage confined to the three feedback summaries (F06). |
| the two fixes flip a gate in the candidate's favour | **Confirmed for a test verdict (B1 TEST 2, FAIL → PASS), not for a gate.** `INTERNAL_VALIDATION_PASS` and `CANDIDATE_REGION_POSITIVE_WIDTH` are false under both the pre-fix and the post-fix code. |
| feedback so large the architecture precludes a window | **Not established.** Feedback is real and large in birth-worlds (F18) but confounded, and no preclusion across the region was shown. |
| gates recomputed honestly (F10, F18) | 11 → 10 of 13. Disposition string unchanged. |

---

```
REVIEWER_VERDICT              = EVIDENCE_OR_PROVENANCE_INCOMPLETE
LOAD_BEARING_DEFECTS          = 0
SUBSTANTIVE_DEFECTS           = 20
COSMETIC_DEFECTS              = 4
ATTACKS_REFUTED               = 2 of 12
OBSERVER_INERTNESS_HOLDS      = YES
DESCENDANT_EXPOSURE_REALLY_RECORDED = YES
NEW_SCIENTIFIC_RUNS_BY_REVIEW = 0
```

**Reading of the verdict.** No attack forced the terminal disposition string to change, and
`PROSPECTIVE_Q_ENVIRONMENT_OPERATOR_NOT_IDENTIFIED__ADDITIONAL_INSTRUMENTATION_REQUIRED` is the
right string. The verdict is `EVIDENCE_OR_PROVENANCE_INCOMPLETE` rather than
`CANDIDATE_DISPOSITION_SUPPORTED` because the record does not establish three things it asserts:
`PQEC01_METHODS_HASH` does not cover the executor that ran the science (F01); the validation
numbers were on disk before both declared fixes, one of which flips a validation verdict, while
`NO_REFIT_AFTER_VIEWING_VALIDATION` is a hardcoded literal (F14, F15); and the file carrying the
terminal disposition was hand-edited after the last analysis run and does not regenerate from the
sealed code (F16). Separately, two of the reasons given for the disposition are wrong on the
arithmetic (F21, F18) and one headline number is unsupported (F22). None of that makes the
calibration invalid, and none of it makes the operator identified.
