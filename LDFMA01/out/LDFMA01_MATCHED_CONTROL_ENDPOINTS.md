# LDFMA01 — ROUTE A: MATCHED-CONTROL ENDPOINTS

E3 and E5 are re-derived here against the seven conditions. Being listed in FIMRCC01 gives them no
standing. A third candidate — the locked-daughter turnover endpoint with the attribution defect
repaired — is evaluated alongside them because it is the only one aligned with the mechanism
section 3 identified.

| | E1-corrected | E3 persistence | E5 ambient |
|---|---|---|---|
| 1 relevant to daughter independence | PASS | PARTIAL | **FAIL** |
| 2 does not substitute ambient for daughter | PASS | PASS | **FAIL** |
| 3 non-arbitrary decision rule | PASS | PASS | PASS |
| 4 reconstructable offline | PASS | PASS | PASS |
| 5 decision-capable within 512 arm instances | **FAIL** | PASS | PASS |
| 6 no outcome-chosen threshold | PARTIAL | PASS | PASS |
| 7 positive result advances reproduction | PASS | **FAIL** | **FAIL** |

## The binding arithmetic

Only **22 of 256** LAW_C worlds reach a selective removal — an 8.6 % trigger yield. A two-arm
design inside 512 primary arm instances therefore yields about **22 paired blocks**.

Exact McNemar, one-sided, α = 0.05, at 22 pairs:

| p(SELECTIVE) | p(SHAM) | power |
|---|---|---|
| 0.227 | 0.000 | **0.582** |
| 0.227 | 0.050 | 0.308 |
| 0.227 | 0.100 | 0.153 |
| 0.400 | 0.000 | 0.973 |

It can decide near-total suppression and nothing finer. Five discordant pairs all in one direction
would reach p = 0.031; four would not.

## E3 was not rejected for lack of power

E3 has the power — 22 paired blocks and a paired log-SD of 1.00 detect roughly a two-fold shift in
persistence. It was rejected because the funnel measured that **persistence is not the binding
constraint**: the daughters persist a median 230 steps, up to 1 472, and still fail. Answering a
question about a variable that does not fail would not advance the reproduction question.

E5 fails condition 2 by construction, and section 5 shows why: **2 017 of 2 018** ambient complete
intervals begin *after* the locked identity has already ended.

```
ROUTE_A_CLASSIFICATION = MATCHED_CONTROL_TEST_NOT_DECISION_CAPABLE
```
