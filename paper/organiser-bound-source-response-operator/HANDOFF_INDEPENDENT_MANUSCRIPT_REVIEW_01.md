# HANDOFF — INDEPENDENT MANUSCRIPT REVIEW 01

**From** LRCPS01 (paper synthesis, zero engine runs, zero reviews).
**To** a successor whose entire job is to attack this manuscript.
**Predecessor tip** `f01439c` on `codex/lineage-route-closure-and-paper-synthesis-01`,
built on the FLCR01 tip `06c592313df96601de8d2a89676d5a5cf79fc414`.

`TOMMY_ACTION_REQUIRED = NONE` · `TOMMY_GIT_ACTION_REQUIRED = NONE`

---

## 1. What you are receiving

A compiled companion manuscript (10 pages) and supplement (7 pages) on the frozen
source-response operator, with four regenerated figures, a 213-row numerical
reconciliation binding every number to a hashed source file, a 20-claim scope matrix, a
claim linter reading zero, an overlap audit reading `NO_REUSED_PASSAGE`, and a readiness
score of **86 / 100**.

`DISPOSITION = MANUSCRIPT_V1_COMPLETE__INDEPENDENT_REVIEW_ELIGIBLE`

Review-eligible means only that you can attack it without first repairing it.

## 2. The three things I could not do, and you should

These are the fourteen readiness points I did not earn. They are not writing problems.

1. **No one outside this session has attacked the text.** That is your job. Budget
   permitting, do it adversarially rather than editorially.
2. **The 28 confirmation arms were run once, by one implementation.** They are re-runnable
   from the committed seeds and the hashed methods core. Re-running them is the single
   highest-value experiment available to you and consumes 28 engine runs.
3. **The confirmation stands at one parameter point.** One lattice size, one source
   strength, two mobility settings. The historical record spans three lattice sizes,
   which is why the estimator diagnosis is not a single-size artefact; the confirmation
   itself is not replicated across the parameter space.

## 3. Attacks I consider most likely to land

Ranked by my own estimate of how much of the paper they would remove. I have not
suppressed any of these; several are already stated in the text against our own interest,
which is exactly why an attacker should start there.

1. **The margin is wide enough to be unfalsifiable in practice.** `±2.9 %` against
   observed deviations of `−0.14 %`, `+0.24 %` and `+0.39 %`. Compute what fraction of
   plausible alternative constructions would also have passed. If most would, the test
   discriminates less than the paper implies. The counter-argument in the text is that
   the margin is applied to the distance from the *point prediction*, not from zero, and
   the construction predicted `−1.24 %` and `−5.69 %` — but that argument needs checking,
   not accepting.
2. **The mobile mean cell.** The construction predicts `−1.87 %` against `−0.58 %`
   observed. The paper reports this. Ask whether a construction that misses one of four
   cells by more than a percentage point should be described as reproducing the record.
3. **The static radial profile.** Three arms, `|z| = 8.90` at `r = 4`. I declare it not
   evaluated and give the reason. Test that reasoning: recompute the standard error at
   that radius and confirm that the collapse is a small-sample artefact rather than a
   real disagreement I explained away.
4. **`SECTION_SCOPE_AMENDMENTS`.** I widened 34 value scopes after writing the
   manuscript, each with a stated reason. Every one of those is an opportunity for me to
   have rationalised a placement. Read the amendment table against the manuscript.
5. **The i.i.d. surrogate's population law.** It draws from the *predicted* stationary
   law. If that law is itself slightly wrong, the surrogate's bias estimate inherits the
   error, and the decomposition of the static deficit into "mostly estimator" shifts.
6. **The claim linter is mine.** I wrote both the rules and the text they check. Test the
   linter with deliberately bad input: insert a forbidden formulation and confirm it
   fires; insert a bare numeral and confirm it fires; remove a status line and confirm it
   fires.
7. **The ablation ladder is analytic, not experimental.** The four constructions are
   simulations of the ideal process, not four sets of arms. The distances in figure 4a
   are therefore distances between a construction and one observation, not between two
   measurements.

## 4. What you must not do

- Do not repair a defect you find in a way that removes the record of it. If a claim is
  wrong, withdraw it and say so in the same document.
- Do not upgrade any wording ceiling in `decisions/PAPER_SCOPE_AND_CLAIM_MATRIX.json`.
  Ceilings may be lowered on evidence; raising one requires new evidence, which this
  handoff does not authorise.
- Do not submit to a journal. `JOURNAL_SUBMISSION = FORBIDDEN_BY_THIS_MISSION__NOT_ATTEMPTED`,
  and no successor inherits an authorisation the predecessor did not have.
- Do not attempt a push. See §6.

## 5. Where everything is

```
paper/organiser-bound-source-response-operator/
  manuscript/MANUSCRIPT.tex .pdf   numbers.tex (generated)  preamble.tex
  supplement/SUPPLEMENT.tex .pdf   S1_methods S3_margin S4_arms S6_radial S7_models
  figures/          fig1..fig4, each as .pdf and .png
  figure_data/      one JSON per figure, the exact numbers plotted
  bibliography/references.bib      11 entries, all cited
  decisions/        PAPER_STRATEGY_DECISION, PAPER_SCOPE_AND_CLAIM_MATRIX,
                    PAPER_NARRATIVE_DECISION, PAPER_TITLE_AND_ABSTRACT_OPTIONS
  provenance/       PAPER_SOURCE_BINDING, PAPER_NUMERICAL_RECONCILIATION (.json/.csv),
                    PAPER_MACRO_INDEX, PAPER_RESULT_INVENTORY, PAPER_PROVENANCE_LEDGER,
                    PAPER_MISSING_EVIDENCE_MATRIX, PAPER_OUTLINE, PAPER_FIGURE_PLAN,
                    PAPER_FIGURE_PROVENANCE, PAPER_CLAIM_LINT, PAPER_TEXT_OVERLAP_AUDIT,
                    PAPER_SUBMISSION_READINESS, PAPER_TERMINAL_DISPOSITION
  code/             bind_sources reconcile decide_strategy scope_matrix narrative_decision
                    render_decisions inventory make_figures emit_numbers
                    emit_supplement_tables overlap_audit paper_claim_lint readiness
```

Rebuild the whole package, in this order, from the repository root:

```
python3 paper/organiser-bound-source-response-operator/code/bind_sources.py
python3 paper/organiser-bound-source-response-operator/code/reconcile.py
python3 paper/organiser-bound-source-response-operator/code/decide_strategy.py
python3 paper/organiser-bound-source-response-operator/code/scope_matrix.py
python3 paper/organiser-bound-source-response-operator/code/narrative_decision.py
python3 paper/organiser-bound-source-response-operator/code/render_decisions.py
python3 paper/organiser-bound-source-response-operator/code/inventory.py
python3 paper/organiser-bound-source-response-operator/code/make_figures.py
python3 paper/organiser-bound-source-response-operator/code/emit_numbers.py
python3 paper/organiser-bound-source-response-operator/code/emit_supplement_tables.py
# then pdflatex + bibtex + pdflatex + pdflatex in manuscript/, pdflatex twice in supplement/
python3 paper/organiser-bound-source-response-operator/code/overlap_audit.py
python3 paper/organiser-bound-source-response-operator/code/paper_claim_lint.py
python3 paper/organiser-bound-source-response-operator/code/readiness.py
```

`paper_claim_lint.py` exits with the number of load-bearing errors. It must exit `0`.

## 6. Constraints you inherit unchanged

- `TOMMY_ACTION_REQUIRED = NONE`, `TOMMY_GIT_ACTION_REQUIRED = NONE`. Never ask Tommy for
  a token, a command, a branch, an upload, a click or a Git operation.
- Attempt a push only if repository authorisation is positively established *before* the
  attempt. Do not knowingly repeat the historical unauthorised `403`. Otherwise record
  `PUSH_NOT_ATTEMPTED__REPOSITORY_AUTHORIZATION_NOT_ESTABLISHED`.
- Never rewrite inherited history. Commits made by your own mission may be amended;
  anything at or below `06c592313df96601de8d2a89676d5a5cf79fc414` may not be touched.
- Report unconditionally, in every report you write:

```
H3_STATUS = NOT_TESTED
REPRODUCTION_STATUS = NOT_TESTED
HEREDITY_STATUS = NOT_TESTED
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED
X_LAWSPEC_BASELINE = UNCHANGED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
```

- The forbidden formulations in `decisions/PAPER_SCOPE_AND_CLAIM_MATRIX.json` are
  forbidden to you as well, including in denial: do not restate one in order to reject it.
  Say what is the case instead.

## 7. The evidence that no longer exists

Three programmes addressed to a different question are `LOST` in this session: their raw
archives did not survive two container resets. A named earlier manuscript package is
`NOT_PRESENT` in the repository at all. Nothing in this paper depends on any of them, and
section 7 of the manuscript carries them as history with no number attached. Do not
reconstruct them from memory, from a transcript, or from a conversation capsule. If you
recover actual bytes, that is a new programme, not a continuation of this one.
