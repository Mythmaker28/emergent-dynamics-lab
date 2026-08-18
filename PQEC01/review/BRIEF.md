# PQEC01 — INDEPENDENT ADVERSARIAL REVIEW (the single authorized review)

You are an **independent adversarial reviewer**. Your job is to **refute**, not to praise.
Uncertainty is not evidence. Never write the bare word `REFUTED`; use only
`DEFECT_CONFIRMED`, `DEFECT_PLAUSIBLE`, `ATTACK_REFUTED` (= the attack failed, the claim stands).

## HARD CONSTRAINTS
- **Read-only** on the candidate. Write ONLY under `/home/claude/PQEC01/review/`.
- **Do NOT run the engine.** Do not construct `kinetics.World` / `WorldOBTC` / `PQECWorld`, do not
  call `_one_step`, do not seed an organiser. Reading `.npz`, reading source, and exact arithmetic
  are fine. `NEW_SCIENTIFIC_RUNS_BY_REVIEW` must be 0.
- Do not run `git push`/`commit`/`checkout`/`reset`.

## THE CANDIDATE
```
repo            /home/claude/edl
branch          codex/prospective-q-environment-calibration-01
C1 instrumentation+qualification   0c8ed487641a06904f2690b23ee991857088ca00
C2 FREEZE, ALONE                   0bba579f46895248364f3c74cd3c0e798c26eb4a
C3 all 128 starts + raw manifest   7d97205818ae723683280053512a27f1872db375
C4 analysis + candidate disposition d61e9a34367b42bd7534647ad9802a9892639f31
code            /home/claude/edl/PQEC01/code/
outputs         /home/claude/edl/PQEC01/out/
raw archives    /home/claude/PQEC01/raw/*.npz   (128 files, ~1 GB)
engine          /home/claude/ORR01/code/{kinetics,observe,lawspec_v2}.py,
                /home/claude/OBTC02/code/engine_obtc.py
```

## CANDIDATE DISPOSITION UNDER ATTACK
`PROSPECTIVE_Q_ENVIRONMENT_OPERATOR_NOT_IDENTIFIED__ADDITIONAL_INSTRUMENTATION_REQUIRED`
with 11 of 13 decision gates passing; failures are `INTERNAL_VALIDATION_PASS` (validation TEST 2
at B2, world-level z = −2.82) and `CANDIDATE_REGION_POSITIVE_WIDTH` (empty region).

## THE 12 ATTACKS — run every one
**A1 — freeze chronology.** Is `PQEC01_MASTER_FREEZE.{md,json}` genuinely in a commit of its own,
containing no raw outcome and no statistic, and does that commit strictly precede every scientific
archive? Check `git show --stat` on C2, and compare the freeze commit time against the raw file
mtimes. Check the freeze's `PQEC01_METHODS_HASH` actually covers the code that ran.

**A2 — observer inertness.** The observer RE-IMPLEMENTS the engine's four frozen sub-shifts
verbatim for species Y (`PQECWorld._diffuse`). This is the highest-risk code in the programme.
Attack it: compare it line by line with `engine_obtc.WorldOBTC._diffuse`; check the RNG call
order, the `hops_offered`/`hops_blocked` update position relative to the `continue`, the
`self.free()` call inside the loop, and whether `self.track and sname == "X"` can ever fire. Then
attack the qualification itself: are `L = 5`, 8 steps and 7 fixtures enough? Does any fixture
exercise a case the scientific runs hit but the fixtures do not?

**A3 — outcome firewall.** Did any scientific outcome reach a decision before all 128 starts
finished? Read `pqec01_run.py` and `PQEC01_RUN_LEDGER.jsonl`. Note that the ledger stores
`seconds`, which correlates with early stopping. Was anything acted on?

**A4 — accounting of starts.** Are all 128 frozen seeds present exactly once, with the frozen
splits, and no extra? Any reserve used? Any world dropped, replaced or re-run? Cross-check
`PQEC01_MASTER_FREEZE.json → SEED_RULE.SEEDS` against `PQEC01_RAW_MANIFEST.json` and the ledger.

**A5 — step-phase identity.** The claim is that `pq_field[t]` and the `ycells` rows are the
post-diffusion pre-reaction state of step `t`. Verify against `PQECWorld._react` and
`WorldOBTC._react`. Separately: the `scalars` array is computed AFTER `_one_step()` returns.
The analysis says it fixed this by using `ycells` instead — check that EVERY exposure quantity
in the analysis really comes from `ycells` or the field, and that no post-step scalar leaked into
`E_w`, the transition kernel, the radial profile, the region, or any validation test.

**A6 — lineage-label ambiguity.** Births in a multiply occupied cell have no identifiable parent.
Does any analysis or claim implicitly assume one? Check `PQEC01_ENVIRONMENT_OPERATOR.json` and the
Phase-B per-world fields (e.g. `descendant_exposure_rows`, `separation_delay_after_first_birth`).

**A7 — frame pseudoreplication.** The unit is the world. Hunt for any place a step, cell or event
row is used as an independent unit — in the world summaries, the feedback z-tests, the validation
tests, the transition-matrix uncertainty, or the region. One test was already repaired for this;
check whether others survive, including the pooled transition counts.

**A8 — discovery/validation leakage.** The split is a hash of the frozen seed. Verify it is
outcome-independent, that discovery and validation sets are disjoint, and that the Phase-A
quantities feeding the region (mean exposure LCB) do not mix a Phase-B validation world.

**A9 — refitting after validation.** Was anything changed after validation outcomes were visible?
Two analysis fixes are declared in C4's message. Were they made before or after the validation
numbers were seen, and do they change any validation verdict in the candidate's favour? Check the
git history and reason about it explicitly.

**A10 — descendant-position exposure.** The headline claim is that real descendant-local exposure
was recorded. Verify from the raw archives: open several Phase-B worlds, confirm `ycells` contains
rows for MORE THAN ONE distinct Y cell at the same step, and that those rows carry that cell's own
`nX`, `nSY`, `free`, `cand_Y`, `Q`. Confirm the separation events are real by the frozen
single-linkage / CORE_R = 5.0 definition, recomputing from the field or the ledgers.

**A11 — feedback comparison.** Phase A and Phase B are compared as distributions, not paired. Is
that done correctly? Attack the `mean_free` comparison whose variance is degenerate, the N_X
comparison (+12% to +15%, z ≈ 1.3–1.8, called not significant), and whether the comparison is
confounded by Phase-B worlds stopping early (different step ranges).

**A12 — terminal-disposition inflation OR deflation.** Argue BOTH sides. (a) Is the candidate
claiming too much — is "Phase A spatial operator identified" justified, is the 111 vs 125 step
agreement being over-read, is "the parent's central gap is closed" too strong? (b) Is the
candidate too weak — with 11 of 13 gates passing, a single failed validation test at one of two
points, and a preregistered empty region, should the disposition have been
`PROSPECTIVE_Q_ENVIRONMENT_OPERATOR_IDENTIFIED`? Also check that
`EXISTING_ARCHITECTURE_FEEDBACK_PRECLUDES_CONTROLLED_WINDOW` is correctly NOT used.

## OUTPUT — exactly two files
`/home/claude/PQEC01/review/PQEC01_ADVERSARIAL_REVIEW.md` and `…/PQEC01_ADVERSARIAL_REVIEW.json`

Each finding must carry: `ID, ATTACK, SEVERITY (LOAD_BEARING|SUBSTANTIVE|COSMETIC),
STATUS, CLAIM_ATTACKED, EXACT_FILE_AND_LINES, EXACT_NUMBERS, WHY_IT_MATTERS,
SETTLING_COMMAND_OR_CALCULATION, MINIMUM_REQUIRED_CHANGE`.
`LOAD_BEARING` = if confirmed, the terminal disposition must change.

End the `.md` with exactly this block:
```
REVIEWER_VERDICT              = <CANDIDATE_DISPOSITION_SUPPORTED |
                                 CANDIDATE_TOO_CONSERVATIVE__OPERATOR_IS_IDENTIFIED |
                                 CANDIDATE_TOO_STRONG__CALIBRATION_TECHNICALLY_INVALID |
                                 EVIDENCE_OR_PROVENANCE_INCOMPLETE>
LOAD_BEARING_DEFECTS          = <int>
SUBSTANTIVE_DEFECTS           = <int>
COSMETIC_DEFECTS              = <int>
ATTACKS_REFUTED               = <int of 12>
OBSERVER_INERTNESS_HOLDS      = <YES|NO|UNDETERMINED>
DESCENDANT_EXPOSURE_REALLY_RECORDED = <YES|NO|UNDETERMINED>
NEW_SCIENTIFIC_RUNS_BY_REVIEW = 0
```
A finding without exact file, lines and numbers is not a finding.
