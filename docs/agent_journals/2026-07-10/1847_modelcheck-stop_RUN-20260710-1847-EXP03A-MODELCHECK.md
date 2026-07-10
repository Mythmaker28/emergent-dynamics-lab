# Agent Journal — RUN-20260710-1847-EXP03A-MODELCHECK

## AGENT / ROLE

Continuation attempt for EXP03-A (CORE V0 + density preference). This run performs the read-only durable-state
verification requested, then STOPS before any EXP03-A implementation because of a model-lock blockage. It does not
design, implement, validate, preregister, or screen EXP03-A.

## RUN ID

`RUN-20260710-1847-EXP03A-MODELCHECK`

## START / END

Start 2026-07-10 18:47 +02:00. End: same run (checkpoint-and-stop).

## MODEL — BLOCKAGE (signalled, not masked)

- The user mission requires this work to run on **Claude Fable 5** and explicitly forbids continuing under
  **Opus 4.8** ("N'UTILISE PAS OPUS 4.8"; "Un switch automatique ou imposé doit être signalé. Ne le masque pas";
  fallback = checkpoint + journal + update state + commit + push + document + STOP).
- The session `<env>` block reports the active model as **`claude-opus-4-8`**, not Fable 5. I cannot introspect
  weights; the environment metadata is the authoritative signal and it indicates Opus 4.8.
- Therefore the Fable 5 model lock is NOT satisfied in this session. Per the user's own fallback protocol I
  **do not** run EXP03-A here (design/mechanism/validation/screening are model-locked to Fable 5).
- **Correction of prior record:** the report for `RUN-20260710-1801-ALIASINT-FABLE5` stated "remained on
  Fable 5: yes". That was asserted from the instruction, but the `<env>` model label was `claude-opus-4-8` then
  as well. I should not have claimed a Fable 5 identity I cannot verify. Honest status: the environment reports
  Opus 4.8 for these sessions; whether the earlier scientific work executed on Fable 5 cannot be confirmed from
  here. The ALIAS-INTERVENTION artefacts themselves are deterministic and independently reproducible regardless
  of which model orchestrated them (validation gates + manifests + tests are the durable evidence).

## DURABLE-STATE VERIFICATION (read-only; requested)

- HEAD `d96b5ed`; branch main; working tree clean apart from the known benign CRLF result-file churn
  (`git diff --ignore-all-space` empty). origin/main is behind (`313ce95`) because pushes have no auth here.
- EXP02: COMPLETE, 900/900, 648,740 measurements; tau canonicalized without touching raw (D-013). Nine
  screening-eligible laws; fresh-seed hold-out reduced to `{0,52}` (HOLDOUT04). Verified via docs/manifests.
- ALIAS-INTERVENTION-COREV0-20260710-001: COMPLETE. summary.json decision `CASE_A_CLOSE`; law 0 = 0/5 and
  law 52 = 0/9 genuine turnover-individuality; three law-52 units are rigid cohesive persistence (M≈1.0);
  sham==control bit-for-bit for all enrolled units; occupancy/look-alike NOT rejected; CORE V0 survivors closed.
- **D-017 is genuinely present** in `docs/DECISION_LOG.md` (line 147) and is referenced consistently by
  `PROJECT_STATE.md` and `EXPERIMENT_INDEX.md`. **No provenance gap** — no retro-correction required.
- Laws 0 and 52 remain closed. Thresholds unchanged. Nothing reopened. EXP02 not rerun. P/M untouched.

## WHY STOP RATHER THAN PROCEED

Proceeding to implement EXP03-A under Opus 4.8 would (a) violate the explicit model lock and (b) mask an imposed
model switch the user said must never be masked. The correct, user-specified action is to checkpoint and stop.

## NEXT ACTION (exact)

Re-invoke this project in a session that genuinely runs **Claude Fable 5**. Then execute EXP03-A strictly per the
mission: inspect existing density-preference references; mechanistically define the density-preference /
comfortable-neighbor component (WHAT LOCAL QUANTITY / HOW IT MODIFIES FORCE / COMFORTABLE REGION / BELOW / ABOVE /
TYPE-SPECIFICITY / NEW LawSpec PARAMS / EXACT NEUTRAL LIMIT reducing to CORE V0); preregister and commit
`docs/experiments/EXP03A_*_PROTOCOL.md` BEFORE any screening; implement + validate the mechanism (determinism,
diagnostic-ID independence, neutral-limit equivalence to CORE V0 on several controlled worlds, reference/vector
agreement, finite/domain guards, periodic-boundary, detector/tracker/P/M/null tests); run PASS A (mechanism
challenge: distinguish from a trivial interaction-matrix/range change) and PASS B (measurement challenge:
densification / rigid clusters / bridge artefacts / reduced mobility / longer slot residence) internally and
journaled; then the pre-declared low-discrepancy screen, keeping P/M joint, no composite score, reporting the
five distinct levels (distributional shift / screening signal / fresh-seed recurrence / alias rejection / causal
re-establishment) separately. If no law passes the pre-registered gate → EXP03-A NEGATIVE, then EXP03-B.

## GIT / LOCK

Committing this journal + a PROJECT_STATE model-lock hold note. Releasing the lock after commit (clean checkpoint,
nothing in progress). Push attempted (no remote auth in this environment).
