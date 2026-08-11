import hashlib, json, os, time
H=os.path.dirname(os.path.abspath(__file__)); W=H+"/_work"; P0="/home/claude/sweep/FCDDH00"
sha=lambda p: hashlib.sha256(open(p,'rb').read()).hexdigest()
def w(n,s): open(os.path.join(H,n),"w").write(s); return sha(os.path.join(H,n))
AUTH=open(os.path.join(H,"FCDDH01R_OWNER_REAUTHORIZATION_VERBATIM.txt"),"rb").read()
AUTHSHA=hashlib.sha256(AUTH).hexdigest()
ident=json.load(open(H+"/FCDDH01R_SCIENTIFIC_OBJECT_IDENTITY_MANIFEST.json"))
nl=json.load(open(H+"/FCDDH01R_NO_LOOK_RETRY_LICENSE.json"))
cb=json.load(open(H+"/FCDDH00_FINAL_CLOSURE_BINDING.json"))
q=json.load(open(H+"/FCDDH01R_NAMESPACE_AND_ROLE_QUEUES.json"))
dex=json.load(open(H+"/DURABLE_EXECUTOR_PREFLIGHT_REPORT.json"))

json.dump({"AUTHORIZATION":"THIS_PROMPT_WHEN_SENT_BY_TOMMY","OWNER":"Tommy",
 "AUTHORIZATION_CLASS":"ONE_FRESH_ENGINEERING_CORRECTED_REEXECUTION",
 "authorization_file":"FCDDH01R_OWNER_REAUTHORIZATION_VERBATIM.txt",
 "authorization_sha256":AUTHSHA,"authorization_bytes":len(AUTH),
 "NEXT_PROGRAM":"FRESH_CROSSED_DIFFERENTIAL_DISCOVERY_HOLDOUT_01R","SHORT_NAME":"FCDDH01R",
 "BRANCH":"dev/fresh-crossed-differential-discovery-holdout-01r",
 "DIRECT_GIT_PARENT_TIP":cb["FCDDH00_TIP"],"SCIENTIFIC_ESTIMAND_PARENT_TIP":"334b7c2ba6d97dadb403c7a1ea9700a1c61ad512",
 "PARALLEL_EXECUTORS_AUTHORIZED":0,"PUSH_AUTHORIZED":False,"DRAFT_PR_AUTHORIZED":False,
 "WORKFLOW_TRIGGER_AUTHORIZED":False,"TOMMY_ACTION_REQUIRED":False,"TOMMY_GIT_ACTION_REQUIRED":False,
 "FCDDH01R_CHILD_MAXIMUM_CHARGED_STARTS":672,"FCDDH00_HISTORICAL_CHARGED_STARTS":108,
 "FCDDH00_PLUS_FCDDH01R_LINEAGE_MAXIMUM":780,
 "OTHER_REAL_ENGINE_STARTS_AUTHORIZED":0,"DIAGNOSTIC_REAL_ENGINE_STARTS_AUTHORIZED":0,
 "TIMING_REAL_ENGINE_STARTS_AUTHORIZED":0,"SMOKE_TEST_REAL_ENGINE_STARTS_AUTHORIZED":0,
 "PREFLIGHT_ENGINE_STARTS_AUTHORIZED":0,
 "REPORTED_ORIGINAL_FCDDH00_AUTHORIZATION_SHA256":"f4312234273d85ef43307964b20b7105ac5e8b147dc7d064a484b7cadaddfe3f",
 "COMMITTED_ORIGINAL_FCDDH00_AUTHORIZATION_SHA256":"9dcdd47aaaf4482a349ee95a0f89f061516e8a199cb77911c0345e9eff011169",
 "AUTHORIZATION_DIGEST_RECONCILIATION":"REPORTED_DIGEST_NOT_REPRODUCIBLE__COMMITTED_DIGEST_IS_CONTROLLING__IDENTITY_ESTABLISHED_BY_CONTENT",
 "reconciliation_detail":("22 declared serializations of the committed verbatim text (LF, CRLF, CR, "
   "BOM variants, trailing-newline variants, per-line and whole-text whitespace normalisation, blank-line "
   "collapse, UTF-16LE/BE, latin-1 and ascii lossy) were hashed; NONE reproduces the reported digest. The "
   "committed FCDDH00 binding, written at FCDDH00 commit 1 long before this reauthorization existed, already "
   "records that the stored text is the handoff message AS RECEIVED BY THE EXECUTOR 'including the line-join "
   "artefacts present in the received text'; characters were LOST in delivery, so no serialization transform "
   "can recover the owner's source bytes and the two digests CANNOT agree. Authorization identity is instead "
   "established by content: the committed text is titled FCDDH00, names parent 334b7c2b, the same branch, "
   "workdir, 96/96/96 and 128/128/128 budgets, D0-D11, H0-H9 and 2517/65536, every one of which THIS "
   "reauthorization independently restates. The reported digest is therefore NOT adopted and NOT claimed "
   "verified; the committed digest is bound as controlling and the discrepancy is reported to the owner.")},
 open(H+"/FCDDH01R_OWNER_REAUTHORIZATION_BINDING.json","w"),indent=1)

w("FCDDH00_FAILURE_AND_REUSE_BOUNDARY.md", f"""# FCDDH00 failure and reuse boundary

`FCDDH00_FINAL_DISPOSITION = {cb['FCDDH00_FINAL_DISPOSITION']}` — permanently closed. FCDDH01R
neither rescues nor reclassifies it. A positive or negative FCDDH01R result can never overwrite the
fact that FCDDH00 produced **no** target active response, axis, materiality, hold-out or inferential
outcome; its G1 and twin-sham evidence remains methodological only.

## Reconstruction of the 108 charged starts (ledger primary, not prose)

| component | count |
|---|---|
| discovery construction | {cb['reconstruction']['construction_charged']} |
| sham rows from {cb['reconstruction']['sham_complete_twin_pairs']} complete bit-identical twin pairs | {cb['reconstruction']['sham_rows_from_complete_pairs']} |
| complete sham singleton (`SHAM_0_71007_FAR_a1`) | {cb['reconstruction']['sham_complete_singletons']} |
| interrupted billed sham row (`{cb['reconstruction']['sham_interrupted_billed_row']}`) | 1 |
| setup / other charges | {cb['reconstruction']['setup_or_other_charges']} |
| active starts | {cb['reconstruction']['active_charged']} |
| hold-out starts | {cb['reconstruction']['holdout_charged']} |
| **total charged** | **{cb['reconstruction']['TOTAL_CHARGED']}** |
| **total raw advance sequences** | **{cb['reconstruction']['TOTAL_RAW_ADVANCE_SEQUENCES']}** |

`{cb['reconstruction']['arithmetic']}`

**The "at 59/96" wording.** {cb['reported_59_of_96_wording']['ledger_primary']}
Append-only correction required: **{cb['reported_59_of_96_wording']['append_only_correction_required']}** —
{cb['reported_59_of_96_wording']['note']}. The committed WAL is primary; the prose was not smoothed.

## Zero-look proof

`FCDDH01R_NO_LOOK_RETRY_LICENSE = {nl['FCDDH01R_NO_LOOK_RETRY_LICENSE']}`.
`FCDDH00_TARGET_RESPONSE_LOOKS = 0`, `FCDDH00_CONFIRMATORY_TESTS = 0`, `FCDDH00_ALPHA_SPENT = 0`.
All {nl['evidence']['searched_committed_FCDDH00_subtree_paths']} paths of the committed FCDDH00
subtree were enumerated. Absent, as required: any active raw archive, active raw manifest or lock,
threshold lock, axis object, gate ladder or score table, randomization result, and any hold-out
outcome artefact. The only hold-out-named committed files are the frozen SCORER CODE and the design
role-queue file — code and design, never an outcome. Therefore the preregistered 12+16 sample sizes
and the single exact 2^16 confirmatory family stand with **no** multiplicity or alpha adjustment.

## Reuse boundary

Reused exactly (verified byte-for-byte): the G1 route and its static constructor proof, the frozen
scientific source, symbolic coefficient certificates, schemas, dependency firewall, synthetic oracle
fixtures, the exact enumerator, the failure diagnosis and start-ledger semantics, the parent
provenance binders and the immutable FCRA00 objects.

Prohibited and not used anywhere: any 71000-series precursor, checkpoint, mask, completed or partial
sham trajectory, randomization bit, execution order or ledger token — as data, as a row, as a
threshold, as a gauge, as calibration, as training or validation, or as support for any conclusion.
Even apparently complete 710xx rows are excluded because the interruption fell at a position in a
randomized execution schedule and runtime can in principle depend on state or assigned condition:
resuming that panel could condition inclusion on runtime. **Freshness here is bias control, not
tidiness.** The 29/29 bit-identical twin result is bound as historical integrity prose only.
""")

w("FCDDH01R_ENGINEERING_DELTA.md", f"""# FCDDH01R engineering delta

The only permitted class of change, and the only class made.

## Scientific path: byte-identical, with exactly one path constant

{ident['byte_identical_modules']}/{ident['byte_identical_expected']} scientific modules are
**byte-identical** to the committed FCDDH00 objects: the certified-interval core, the independent
reference, the SHAKE256 scheduler, the child-marker runner, the G1 construction worker, the
acquisition launcher, the decode layer, the discovery and hold-out drivers, the oracle, the hold-out
fixed-axis scorer, the exact 2^16 enumerator and the canonical 44-field schema. The carrier
executable `FWL2CF00/fw_worker.py` is unchanged (`{ident['carrier_executable']['sha256'][:16]}…`,
`unchanged = {ident['carrier_executable']['unchanged']}`) and the immutable parent basis is unchanged.

`DISCOVERY_AXIS_TRAINER_V1.py` differs by **exactly {ident['modules']['DISCOVERY_AXIS_TRAINER_V1.py']['n_differing_lines']} line**:
its firewall root `ALLOWED_ROOT`. This is not merely permitted, it is **required**: keeping the
FCDDH00 root would ADMIT dead-panel paths and fail DEX9. Every formula, gate, fold rule, sign
convention and refusal in that file is unchanged.

## New engineering, outside the numerical path

* `DURABLE_PHASE_SUPERVISOR.py` — detached phase supervisor: own session, stdin disconnected,
  durable append-only logs, fsynced PID/start-time/boot identity and heartbeat, exclusive flock per
  phase, at most one billed row at a time, no interactive shell or PTY dependency, atomic opaque
  publication, pollable without decoding science, exits at every phase barrier.
* `EXACT_ONCE_PHASE_STATE_MACHINE.py` — immutable `RUN_ID`, the ten monotone states, the
  append-only WAL **directory** of individually published atomic records, the exclusive
  `START_GATE` filesystem claim that charges the row, non-overwriting publication by exclusive
  link (never `os.replace`), and the conservative recovery matrix.
* `fr_dummy.py`, `fr_dex.py`, `fr_plan.py`, `fr_launch.sh` — mock-only failure injection, the frozen
  plan builder and the frozen launch template.
* retry-specific paths, programme labels, seed namespace and report names.

Nothing else changed. No engine, no LawSpec, no reader, no carrier, no mask rule, no horizon, no
weight, no threshold rule, no gate, no sample size, no claim ceiling.

## The frozen launch template

```
/usr/bin/nohup /usr/bin/setsid -f /usr/bin/python3 -u \\
    /home/claude/sweep/FCDDH01R/DURABLE_PHASE_SUPERVISOR.py <plan> \\
    </dev/null >>phase.log 2>>phase.err &
```

It has authority **because DEX0 passed**, not because a manual says so: a real bounded tool call was
allowed to expire at the same 120-second boundary that killed FCDDH00, and the supervisor kept the
same PID and start identity, kept heartbeating, and completed all ten dummy rows afterwards. A
second trial killed the entire launcher process group explicitly with the same result.

## What the campaign caught before any billed start

DEX13 exposed a real exactly-once defect: concurrent wrappers raced on the gate's *temporary* file,
not merely on its exclusive publication. The temporary is now unique per claimant. Eight simultaneous
wrappers for one `RUN_ID` now yield exactly one gate winner and exactly one charge. This is precisely
why the campaign is mandatory.
""")

w("DURABLE_EXECUTOR_SPEC.md", f"""# FCDDH01R durable executor specification

## Contract (four parts, nothing more is claimed)

```
EXACTLY_ONCE_LAUNCH_AUTHORIZATION
AT_MOST_ONCE_ENGINE_ADVANCE
EXACTLY_ONCE_OPAQUE_RAW_PUBLICATION
NO_REPLAY_AFTER_UNCERTAIN_OR_INCOMPLETE_BILLED_LAUNCH
```

Without an engine that can atomically commit its internal advance together with the ledger, an
arbitrary SIGKILL cannot guarantee that every launched row *completes*. "Exactly-once" here is
shorthand for the four properties above and never a completion promise.

## States

`PLANNED → DISPATCH_INTENT → WRAPPER_ACK → START_GATE → ENGINE_OPENED → ADVANCE_STARTED →
ENGINE_EXIT_OK → RAW_SEALED → RAW_PUBLISHED → VERIFIED`, each checksummed and fsynced. Billing
begins irreversibly at `START_GATE`. Every pure hash, input, order, code and space check precedes
the gate. No engine import, constructor or advance may occur until the gate is exclusively published
**and** its parent directory is fsynced.

## Recovery matrix

| evidence | action |
|---|---|
| `VERIFIED` | skip forever |
| no gate, no live matching worker | redispatch the same `RUN_ID` |
| no gate, delayed wrapper possible | redispatch permitted: only one wrapper can win the atomic gate |
| gate + exact live worker identity | adopt and wait, never relaunch |
| gate + complete prefix through `ENGINE_EXIT_OK` and `RAW_SEALED` | finish publication/verification, no engine |
| `RAW_SEALED` alone or a broken prefix | billed incomplete, fatal |
| gate + dead worker, no sealed raw | charged once, never replayed |
| engine evidence without a gate | runner invariant failure, stop |
| PID / start-time / boot identity uncertain | freeze all starts |

Construction rejects the **whole candidate** and continues the frozen queue only while the required
complete-block count remains arithmetically attainable. After a panel is sealed, any sham or active
loss closes that panel.

## Polling contract (frozen)

```
HEARTBEAT_PERIOD_SECONDS = 5            POLL_CALL_TARGET_SECONDS <= 30
MAXIMUM_SILENT_INTERVAL_BEFORE_STATUS_CHECK_SECONDS <= 60
ONE_SUPERVISOR_PER_PHASE = true         MAX_SAFE_SUPERVISOR_RESTARTS_PER_PHASE = 4
AUTO_REPLAY = false                     AUTO_REPLACEMENT = false
ENGINE_ROW_WALLCLOCK_TIMEOUT = NONE
```

The heartbeat is liveness metadata and can never prove a row completed. Status calls read process
metadata, ledgers, opaque filenames, hashes and an expected-count boolean only. No subprocess
watchdog, no wall-clock kill, no duration-based admission, ordering or stopping: runtime may depend
on state or on the assigned condition.

## Campaign result

`{dex['FCDDH01R_DEX_CAMPAIGN_STATUS']}` — {dex['tests']} tests, dummy worker engine-free
(`{dex['dummy_is_engine_free']}`), `REAL_ENGINE_CONSTRUCTOR_COUNT = {dex['REAL_ENGINE_CONSTRUCTOR_COUNT']}`,
`REAL_ENGINE_ADVANCE_COUNT = {dex['REAL_ENGINE_ADVANCE_COUNT']}`,
charged starts in the 672 child ledger during the campaign = {dex['charged_starts_in_the_672_child_ledger']}.
""")

w("FCDDH01R_START_BUDGET_AND_LINEAGE_LEDGER.md", f"""# FCDDH01R start budget and lineage ledger

```
FCDDH00_HISTORICAL_CHARGED_STARTS      = 108   (permanently charged to the closed parent)
FCDDH00_UNUSED_PERMISSIONS             = expired with that authorization; neither transferred nor data
FCDDH01R_CHILD_MAXIMUM_CHARGED_STARTS  = 672
FCDDH00_PLUS_FCDDH01R_LINEAGE_MAXIMUM  = 780
```

Per-phase maxima, planning rules, setup accounting, raw-advance accounting and the "charge the
larger count" convention are inherited exactly: discovery 96/96/96, hold-out 128/128/128.

```
OTHER_REAL_ENGINE_STARTS_AUTHORIZED       = 0
DIAGNOSTIC_REAL_ENGINE_STARTS_AUTHORIZED  = 0
TIMING_REAL_ENGINE_STARTS_AUTHORIZED      = 0
SMOKE_TEST_REAL_ENGINE_STARTS_AUTHORIZED  = 0
PREFLIGHT_ENGINE_STARTS_AUTHORIZED        = 0
```

Every durability validation was dummy-only. Static runner audit (unchanged from the parent):
`C_PRECURSOR_ADVANCE = 0`, `C_BLOCK_MAX = 4`, `C_SETUP_D = C_SETUP_H = 0`,
`N_D_ATTEMPT = {q['N_D_ATTEMPT']} >= 12`, `N_H_ATTEMPT = {q['N_H_ATTEMPT']} >= 16`.

Namespace `N = {q['N']}`; discovery candidates {q['DISCOVERY_CANDIDATE_QUEUE'][0]}–{q['DISCOVERY_CANDIDATE_QUEUE'][-1]},
hold-out candidates {q['HOLDOUT_CANDIDATE_QUEUE'][0]}–{q['HOLDOUT_CANDIDATE_QUEUE'][-1]}.
{q['selection']}
""")
print("docs written")
