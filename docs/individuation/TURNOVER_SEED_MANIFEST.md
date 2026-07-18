# LCI-CAUSAL-TURNOVER-PREREG-03 — Proposed seed manifest (NOT opened)

## DEV seeds used (this mission)

`50001–50010` — pre-existing DEV family (also used by the P0 contamination probes). Read-only for prospective
purposes. Results in `experiments/individuation/turnover_dev_raw.json`.

| seed | status | detail |
|---|---|---|
| 50001 | INVALID | droplet 1 **SPLIT** @153 (61→38+22 cells; genuine fission) |
| 50002 | FEASIBLE | deep@847, M=[0.194,0.250,0.145], deep_own=[0.182,0.109,0.149] |
| 50003 | INVALID | droplet 2 **LOST** @236 |
| 50004 | FEASIBLE | deep@793, M=[0.249,0.250,0.219], deep_own=[0.178,0.091,0.080] |
| 50005 | FEASIBLE | deep@831, M=[0.164,0.230,0.250], deep_own=[0.243,0.112,0.094] |
| 50006 | INVALID | droplet 0 **SPLIT** @692 |
| 50007 | FEASIBLE | deep@890, M=[0.227,0.210,0.250], deep_own=[0.127,0.081,0.129] |
| 50008 | INELIGIBLE | <3 well-separated targets |
| 50009 | INVALID | droplet 0 **SPLIT** @436 (105→68+36 cells) |
| 50010 | INELIGIBLE | <3 well-separated targets |

Eligible 8/10; feasible 4/8 (50 %); failures = fission ×3 + loss ×1; **fusion 0**.

Diagnostic re-reads permitted (never for parameter selection): `51xxx` (exp1 prospective), `52xxx`
(confirmation-01), `53xxx` (confirm-02). Not re-run.

## PROPOSED confirmatory family — `54001–54050` (NOT OPENED)

- **50 seeds, cap 50, frozen** (no post-outcome extension). Sized so P(≥12 valid worlds) ≥ 0.90 even under the
  conservative net rate 0.324/seed (`TURNOVER_POWER.md`). Expected ~29 eligible, ~14–20 valid.
- **Registry check — ABSENT.** `git grep '\b54[0-9]{3}\b'` across all 18 branches returns only byte-counts,
  decimal fractions, and physical-score values — **no seed-family definition**. Used families are
  30/31/32/33/50/51/52/53xxx. `54xxx` is fresh.
- **NOT opened by this mission.** No `54xxx` seed is run. Opening requires Tommy's explicit authorization after
  the REPAIR items in `TURNOVER_PREREG_VERDICT.md`.
