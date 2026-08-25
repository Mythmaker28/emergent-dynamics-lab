# FIMRCC01 — ENDPOINT ADJUDICATION

Every candidate was fixed in `FIMRCC01_ENDPOINT_PREREGISTRATION.json`, sha256
`820be62b59e50d4e3e7d25a441856687291f149f28db1c0efa5e7f63fde73223`, published **before** any
number below existed. The set was closed at six. No seventh was introduced.

Frozen design: `N_BASE_BLOCKS = 50`, `K_REQUIREMENT = 2`, exact one-sided binomial at α = 0.05
against `F_INTEGRATED = 0.0032015171041760242`.

## The table

| id | endpoint | kind | on TLMR01 | modal fraction | discriminating? | power at n=50 | survives |
|---|---|---|---|---|---|---|---|
| E0 | unrestricted population | binary | 22/22 | 1.00 | **saturated** | 1.0000 / 0.9362 | no |
| E1 | locked daughter, FUNCTIONAL | binary | 1/22 | 0.95 | **saturated (the other way)** | 0.6697 / **0.0165** | no |
| E2 | locked daughter, COMPLETE only | binary | 1/22 | 0.95 | **saturated (the other way)** | 0.6697 / **0.0165** | no |
| E3 | locked daughter, persistence | count | median 230 | 0.05 | yes | not identified | — |
| E4 | locked daughter, constituent events | count | median 1 | 0.32 | yes | not identified | — |
| E5 | ambient population, paired | count | median 93 | 0.09 | yes | not identified | — |

Power is given for both denominators — per removal world and per world run — because the
pre-registration did not name one. Requiring a pass under **both** is the only resolution that
cannot be accused of choosing the convenient denominator after seeing the numbers. It does not
change the outcome.

## E0 — unrestricted population endpoint

```
STATUS = SATURATED
         NON_DISCRIMINATING
         NOT_ELIGIBLE_AS_PRIMARY
```

22 of 22 removal worlds FUNCTIONAL, 2 018 complete identity intervals, median 93 per world. The
endpoint is answered by the ambient population, not by one locked daughter.

**TLMR01's developmental result is preserved and is not called false.** It answers a broader,
population-level question than the intended minimal-reproduction claim: whether *any* identity
anywhere in the world completed a constituent turnover after the removal. At this law's occupancy
the answer is yes in every world that got a removal, and that is a true statement about the
population.

## E1 / E2 — locked-daughter binary endpoints

```
STATUS = CLAIM_ALIGNED
         NOT_DECISION_CAPABLE_AT_THE_FROZEN_N
```

| | |
|---|---|
| among removed worlds | 1 / 22, exact 95 % interval [0.00233, 0.19812] |
| at world level | 1 / 256, exact 95 % interval [0.00020, 0.01840] |
| ratio to `F_INTEGRATED` | **1.219** |
| `P(K ≥ 2 \| N = 50, p = 1/256)` | **0.0165** |

**This is the load-bearing reason the confirmation cannot proceed.** At N = 50 the pre-declared
K ≥ 2 criterion has approximately 1.65 % assurance under the measured world-level rate. No larger
N repairs it: 1/256 = 0.0039 sits only 1.22× above the endpoint-matched floor, so the alternative
is essentially on the null.

## E3 / E4 / E5 — paired count contrasts

```
STATUS = SECONDARY_MECHANISTIC_QUESTIONS
         NOT_SELECTED
         NOT_CONFIRMATORY_ENDPOINTS_IN_FIMRCC01
```

- they are contrasts, not the frozen binary reproduction event;
- the inherited data contain **no matched no-removal arm** at LAW_C, anywhere in 512 worlds;
- their prospective power is therefore **not identified**;
- selecting one now would change the scientific question **after** developmental outcome access;
- no fresh run may be authorised from them inside this mission.

```
E3_STATUS = FUTURE_QUESTION_RECORDED__NOT_AUTHORISED
E4_STATUS = FUTURE_QUESTION_RECORDED__NOT_AUTHORISED
E5_STATUS = FUTURE_QUESTION_RECORDED__NOT_AUTHORISED
```

No handoff is emitted for any of them.

## Conclusion

No primary endpoint is simultaneously **scientifically aligned**, **independently
reconstructable**, **non-saturated**, and **decision-capable under the frozen fresh design**.

This is `PRECONDITIONS_NOT_MET`.

It is **not** evidence that the phenomenon is impossible; **not** evidence that the architecture
cannot support it; **not** a negative fresh confirmation; and **not** a reason to reinterpret
TLMR01 retrospectively.
