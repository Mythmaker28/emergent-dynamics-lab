# SUBMISSION READINESS (LRCPS01 §17)

## `READINESS_SCORE = 86 / 100`

| Component | Weight | Earned | Evidence |
|---|---:|---:|---|
| manuscript and supplement compile to PDF | 10 | **10** | MANUSCRIPT.pdf 10 pages, SUPPLEMENT.pdf 7 pages |
| no placeholder text anywhere | 5 | **5** | lint check E3 |
| figures present as PDF, PNG and source data | 5 | **5** | 4 figures, each with three artefacts |
| every reported number traced to a hashed source file | 12 | **12** | 213 reconciliation rows, all carrying SOURCE_HASH and JSON_PATH |
| no number reaches the page except through a generated macro | 8 | **8** | lint check E5 on the manuscript body |
| every load-bearing claim bound to existing rows | 5 | **5** | 20 claims, 15 load-bearing, self-test PASS |
| claim linter at zero load-bearing errors | 10 | **10** | LOAD_BEARING_CLAIM_LINT_ERRORS = 0 |
| no reused passage | 5 | **5** | longest common run 8 words against 7 targets |
| bibliography closed in both directions | 5 | **5** | 11 entries, all cited, no dangling citation |
| primary result is prospective, not retrospective | 8 | **8** | the two absolute predictions and their ratio carry PRE_RUN status and the methods hash was FROZEN before the confirmation arms ran |
| declared falsifier existed and could have fired | 6 | **6** | either absolute endpoint outside the margin, a ratio interval containing unity, or a single extinction or invalid arm would have been visible in the endpoint table |
| independent unit is the arm throughout | 6 | **6** | no frame, step, particle or birth event is counted as a replicate in any confirmatory statement |
| independent adversarial review of this manuscript | 6 | **0** | ADVERSARIAL_REVIEWS = 0 for this mission by budget |
| independent replication of the confirmation arms | 5 | **0** | the 28 arms were run once, by one implementation, in one session |
| coverage beyond a single parameter point | 4 | **1** | one lattice size for the confirmation, three sizes in the historical record, two mobility settings, one source strength |

## What the score means

The mechanical properties of this package are as good as this session can make them: every number is bound to a hashed file, the linter is at zero, nothing is reused, and the falsifier was real and public before the data existed. The missing points are not cosmetic and are not recoverable by more writing: no independent party has attacked the text, no independent party has re-run the arms, and the confirmation stands at a single parameter point. A journal reviewer would raise exactly those three.

## Points not earned

**independent adversarial review of this manuscript** — 6 points lost.

Scored zero against our own interest. No one outside this session has attacked this text.

**independent replication of the confirmation arms** — 5 points lost.

Scored zero. Re-running them is possible from the committed code and seeds, and has not been done.

**coverage beyond a single parameter point** — 3 points lost.

One quarter credit: the historical record spans three lattice sizes, which is why the estimator diagnosis is not a single-size artefact, but the confirmation itself is not replicated across the parameter space.

