# Authorization binding regression 03I

Date: 2026-07-16. Interpreter:
`C:\Users\tommy\Documents\ising-lci-turnover-03g-clean\Scripts\python.exe`.

Environment verification passed:

- CPython `3.12.10`, Windows AMD64;
- NumPy `2.2.6`, SciPy `1.15.3`, Matplotlib `3.10.9`;
- `pip check`: no broken requirements;
- `pip freeze --exclude pip`: exact 12-entry set equality with `TURNOVER_ENVIRONMENT_LOCK_03G.txt`;
- production and DEV protected maps identical, 37/37 runtime SHA-256 and Git blob pairs valid.

## Focused authorization contract

The following cases run inside the existing 03G integration test, preserving the required 7/7 suite count:

| Case | Expected | Result |
|---|---|---|
| calculated canonical seal hash in `final_seal_sha256` and expanded phrase | accept validator | PASS |
| literal `{final_seal_sha256}` phrase | reject | PASS |
| literal `<FINAL_SEAL_SHA256>` phrase | reject | PASS |
| wrong hash in phrase | reject | PASS |
| correct phrase, wrong separate hash field | reject | PASS |
| correct field, wrong phrase | reject | PASS |
| template missing placeholder | reject | PASS |
| template duplicates placeholder | reject | PASS |
| uppercase hash | reject | PASS |
| 63-character hash | reject | PASS |
| 65-character hash | reject | PASS |
| modified whitespace or case | reject | PASS |
| failure before engine initialization | reject; zero imports | PASS |
| no permission, ledger, or prospective run directory on failure | create nothing | PASS |

The 63/65 variants and whitespace/case variants are grouped under the mission's numbered cases 10 and 11.

## Regression matrix

| Check | Result |
|---|---|
| 03G production integration, including all A–F fixtures | 7/7 PASS in 47.043 s |
| 03E frozen regression | 18/18 PASS |
| 03C frozen regression | 9/9 PASS |
| bijective tracker | 10/10 PASS |
| tracer and event checks | ALL PASS |
| DEV end-to-end provenance replay | CERTIFIED, Outcome E, seed 50001 only, engine imports 0 |
| committed DEV explicit resume | `already_certified`, 10 entries, terminal tip `53dceb8c8ec6118911ffdf0b0357d6894dd4341212f8b27e0ebb92cbaf3e9b29` |
| static production self-check | PASS; no engine imported and no seed run |
| protected Python compilation | PASS |
| power regenerator | unchanged: `P(N_valid>=18|50)=0.5709037541746931`; `P(N_valid>=18|96)=0.9245190233241044` |
| clean environment | PASS |

## Negative execution evidence

- `results/LCI-TURNOVER-PROSPECTIVE-03G` does not exist.
- DEV evidence contains zero `54xxx` seed or world records.
- No final seal or valid prospective authorization exists in this repair.
- The focused failure test mocks both engine import and ledger initialization and observes zero calls.
- The DEV provenance replay supplies an injected seed-50001 record executor and mocks engine import; zero calls were
  observed.

**Recommendation: READY FOR NARROW RE-AUDIT.**
