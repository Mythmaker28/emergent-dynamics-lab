# FMRT01 — THE ONE ADVERSARIAL REVIEW
## §21 — exactly one independent reviewer, run after candidate analysis, creating no world
`REVIEWER_CREATED_WORLDS = False`. `MAX_ADVERSARIAL_REVIEWS = 1`, reviews run = 1.
The reviewer was **not patched after seeing its own verdicts**, as in FDFLT01 and SPOIQ01.

| # | Attack | Reviewer verdict |
|---|---|---|
| 1 | paired common-seed design | `ATTACK_REFUTED` |
| 2 | pre-intervention bit identity | `ATTACK_REFUTED` |
| 3 | sample-size derivation | `ATTACK_REFUTED` |
| 4 | R1 exact provenance | `ATTACK_REFUTED` |
| 5 | selective mask specificity | `ATTACK_REFUTED` |
| 6 | sham implementation | `ATTACK_REFUTED` |
| 7 | global-off implementation | `ATTACK_REFUTED` |
| 8 | trigger timing | `ATTACK_REFUTED` |
| 9 | late-trigger rule | `ATTACK_REFUTED` |
| 10 | R2 old-material bound | `ATTACK_REFUTED` |
| 11 | post-off daughter X births | `ATTACK_REFUTED` |
| 12 | third-centre handling | `ATTACK_REFUTED` |
| 13 | conditional denominator M | `ATTACK_REFUTED` |
| 14 | population denominator | `ATTACK_REFUTED` |
| 15 | exact binomial test | `ATTACK_REFUTED` |
| 16 | raw-before-analysis chronology | `DEFECT_CONFIRMED` |
| 17 | pre-run and raw durability | `DEFECT_PLAUSIBLE` |
| 18 | absence of post-outcome code changes | `ATTACK_REFUTED` |
| 19 | claim ceiling | `ATTACK_REFUTED` |

Raw counts from the reviewer: 17 refuted, 1 confirmed, 1 plausible, out of 19 attacks.

---

## Adjudication of the two attacks the reviewer did not refute

Both fired on **brittle key lookups**, not on substance — the same failure class as FDFLT01 attack 4
(wrong file path) and SPOIQ01 attack 13 (literal substring match).

### 16 raw-before-analysis chronology

- Reviewer verdict: `DEFECT_CONFIRMED`
- Adjudicated: **`REFUTED_ON_SUBSTANCE__REVIEWER_PREDICATE_IS_BRITTLE`**
- Why the predicate fired: the reviewer reads RAW_COMMIT out of FMRT01_RAW_MANIFEST.json. That field cannot exist: the raw manifest is written BEFORE the raw commit, so it structurally cannot carry its own commit SHA. The reviewer demanded a field whose existence would itself be an anachronism.
- Substantive check (`checked directly against git, not against a JSON key`):

```json
{
 "raw_commit": "61f8f39682f3e557827735207292e4a97d3a5aab",
 "object_type": "commit",
 "n_files_in_raw_commit": 91,
 "analysis_files_in_raw_commit": [],
 "analysis_files_anywhere_in_the_tree_at_the_raw_commit": [],
 "analysis_outputs_present_in_that_tree": []
}
```

### 17 pre-run and raw durability

- Reviewer verdict: `DEFECT_PLAUSIBLE`
- Adjudicated: **`REFUTED_ON_SUBSTANCE__REVIEWER_LOOKED_IN_THE_WRONG_FILE`**
- Why the predicate fired: the reviewer reads WINDOWS_PRE_RUN_DURABILITY out of the COMMITTED master freeze, where it is deliberately PENDING and deliberately never rewritten, and RAW_DURABILITY_BEFORE_ANALYSIS out of the raw manifest, which likewise predates the verdict. Both verdicts live in files created after the frozen ones, precisely so that no committed freeze is ever edited.
- Substantive check (`checked against the durability records and their read-back evidence`):

```json
{
 "pre_run_verdict_file": "FMRT01_PRE_RUN_DURABILITY.json",
 "WINDOWS_PRE_RUN_DURABILITY": "PASS",
 "pre_run_read_back_all_identical": true,
 "pre_run_restored_tree_identical": true,
 "pre_run_methods_hashes_reproduced": "33/33",
 "raw_verdict_file": "FMRT01_RAW_DURABILITY.json",
 "RAW_DURABILITY_BEFORE_ANALYSIS": "PASS",
 "raw_read_back_all_identical": true,
 "raw_restored_tree_identical": true,
 "npz_archives_restored_from_device": 85
}
```

---

## What survives

`LOAD_BEARING_DEFECT_CONFIRMED_AFTER_ADJUDICATION = False`.

The residual defect is **in the reviewer, not in the experiment**: fmrt01_review.py is a hashed frozen module. It is NOT edited after seeing its own verdicts, exactly as in FDFLT01 and SPOIQ01. The brittle predicates are recorded here as a known limitation of the reviewer for any successor mission.

