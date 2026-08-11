# FCDDH00 — PROTOCOL DEVIATIONS

Three items. All are disclosed here, in the machine-readable ledgers, and in the report. None is
concealed, none amends a parent artefact, and none was reinterpreted after seeing an outcome.

---

## D1 — Pre-freeze read of one inherited threshold constant (declared, nil impact)

**What.** During reconnaissance, *before* `FCDDH00_MASTER_FREEZE.md` was written, the executor read
`FSQBT00/CORRECTED_TRANSFER_LICENSES.json`. That file contains the immutable inherited constant
`TUBE_P2_LOBO = 1.2166510017869535e-07` and the parent basis diagnostics
`BASIS_S4_minAlignP2_sq = 0.996213331697554`, `BASIS_S5_minAligne2_sq = 0.9961579179639252`,
`BASIS_S6_maxBlockI2frac = 0.3528522342006583`.

**Why it is a deviation.** Section 3 of the authorization says Commit 1 "may not decode … a
threshold value". `TUBE_P2_LOBO` is a threshold value.

**Impact analysis — nil on every FCDDH00 estimand, gate and threshold.**

1. Every FCDDH00 gate, threshold, sample size and decision label is specified *verbatim by the
   owner authorization* and contains no free parameter that could be tuned to this constant.
2. `TUBE_P2_LOBO` enters FCDDH00 only in the Section 6.5 immutable-P2 hold-out summaries, whose
   form is predeclared by the owner; the hold-out was never opened, so it was never used at all.
3. The `BASIS_S*` values are diagnostics of an immutable parent object and enter no FCDDH00
   computation.
4. No FCDDH00 outcome existed at the time of the read: no state had been generated, no candidate
   constructed and no engine started.
5. The read is enumerated in `PRE_NUMERICAL_ACCESS_LEDGER.jsonl` (entry kind
   `PROTOCOL_DEVIATION__PRE_FREEZE_THRESHOLD_READ`), which was itself part of Commit 1.

Every other pre-freeze read is enumerated in the same ledger and is permitted: Git metadata,
opaque-file hashes, committed **source code** (necessary to bind "every formula, route, queue
rule, code path" into the freeze), design/namespace metadata, and array **shapes only** from the
parent basis.

---

## D2 — Executor process-control failure that terminated one charged sham start

**What.** The discovery twin-sham acquisition driver was launched as a background job *inside a
tool call*. That tool call has a 120-second wall limit; when it expired the harness killed the
whole process group, terminating row `SHAM_1_71007_FAR_a1` in flight. 59 of the 96 required rows
had completed and been published; the 60th was launched and lost.

**Adjudication under the frozen contract — charged, never replayed.**

| evidence | value |
|---|---|
| `INTENDED` record written and fsynced | yes (`seq 118`, token `a9191dfadd2352159571a4113e85c2f5`) |
| `ACK` marker present | **yes** |
| `ADVANCE` marker present, fsynced | **yes** |
| output file present | no |
| `COMPLETED` record | absent |

The frozen rule (master freeze §3.2, `fh_runner`) is: *a start is CHARGED iff the ADVANCE marker
exists, or the launch outcome is uncertain; a charged start is never replayed.* Both conditions
hold. The ADVANCE marker for the acquisition path is written immediately **before** the `execv`
into the committed parent worker, which the freeze already declares "deliberately CONSERVATIVE:
it can only over-charge a deterministic pre-flight failure, never under-charge an engine
advance". That conservatism is **honoured here rather than reinterpreted after the fact**, which
would be exactly the post-hoc favourable reinterpretation the protocol forbids. The row was in
any case ~1 s into a ~2 s worker, so the conservative charge is very probably also the factually
correct one.

**Consequence — the panel is closed, by two independent and sufficient arguments.**

1. **No-replay.** `SHAM_1_71007_FAR_a1` is charged and may never be replayed, so descendant
   `71007_FAR_a1` has a **missing twin**. Authorization §7.2: *"A mismatch, crash or missing twin
   stops the programme with zero discovery active starts; do not replace or rerun a descendant."*
2. **Arithmetic, independent of any judgement.** 60 sham starts are charged of the 96 authorized,
   leaving **36**. 37 rows are still missing. **37 > 36**: the complete twin-sham panel is
   *unreachable within the frozen budget* whatever view one takes of replay.

Therefore: `DISCOVERY_SHAM_STATUS = INCOMPLETE__PROCESS_CONTROL_FAILURE`,
`DISCOVERY_ACTIVE_STARTS = 0`, every hold-out field `NOT_REACHED_BY_PREDECLARED_STOP`, and the
top-level disposition is
`DISCOVERY_SHAM_OR_ACTIVE_PANEL_INCOMPLETE__NO_AXIS__ZERO_HOLDOUT_STARTS`.

**What was NOT done.** No row was rerun, replaced or imputed. No threshold was computed. No
`FCDDH00_DISCOVERY_THRESHOLD_LOCK.json` exists. No active start was made. No hold-out state was
generated. No reader series was decoded and no response quantity of any kind exists in this tree.
The twin-sham oracle was restricted to **hash-level** identity on the pairs that were actually
acquired.

**What the lost row does and does not tell us about the instrument.** All 29 descendants for which
both twins were acquired are **bit-identical over the full horizon** — identical per-time state
hashes, identical terminal hashes, identical full-field output digests, empty touch set, input
checkpoint unchanged. The instrument behaved exactly as required; the loss is purely executor
infrastructure.

**Mitigation for any future authorized programme.** Long acquisitions must be launched in their
own session (`setsid`), so that a tool-call wall limit cannot reach the worker process group, and
the driver must be resumable at the row level *before* the first start is charged, not after.

---

## D3 — Report-rendering amendment to `fh_close.py` (permitted, no numerical effect)

`fh_close.decision_matrix` originally read `DISCOVERY_SHAM_STATUS` only from
`FCDDH00_DISCOVERY_THRESHOLD_LOCK.json`. That lock must **not** exist for an incomplete panel, so
the field would have rendered as `NOT_REACHED_BY_PREDECLARED_STOP` instead of the correct
`INCOMPLETE__PROCESS_CONTROL_FAILURE`. Two lines were added so the field falls back to
`DISCOVERY_SHAM_RAW_MANIFEST.json`. This is a report-rendering defect fix explicitly permitted by
§13; it changes no number, no gate, no threshold and no verdict — only which already-determined
string is printed. The amended file is committed and hashed.

---

## Items that are NOT deviations

* **48 of 96 construction starts used.** Twelve blocks were accepted with zero rejections;
  authority is not an obligation to spend.
* **The nested parent basis.** `P1 = e1 e1ᵀ` lies *inside* `P2 = P1 + e2 e2ᵀ`, so `P1 P2 = P1 ≠ 0`.
  The oracle's first draft asserted mutual orthogonality; that expectation was wrong and was
  corrected against the committed bytes **before** any engine start, and the true structure is now
  the asserted truth with its own required-to-fail mutation.
* **Line endings.** The 19 files that `.gitattributes` marks `text eol=crlf` were taken as raw blob
  bytes (`git cat-file blob`) rather than eol-converted working-tree bytes, so that all 1392
  execution-tree paths are byte-identical to the committed objects. Line-ending form has no effect
  on Python semantics or on any numerical result.
* **Lock-free plumbing commits.** The working copy sits on a create-only mount with a stale
  `.git/index.lock` that cannot be unlinked, so commits are made with a scratch index,
  `write-tree`, `commit-tree` and a direct ref write. No history is rewritten, nothing is deleted,
  and `main` is never touched.
