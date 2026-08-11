# FCDDH00 — FRESH_CROSSED_DIFFERENTIAL_DISCOVERY_HOLDOUT_00 — FINAL REPORT

```
TOP_LEVEL_DISPOSITION =
    DISCOVERY_SHAM_OR_ACTIVE_PANEL_INCOMPLETE__NO_AXIS__ZERO_HOLDOUT_STARTS
```

**No scientific question of this programme was answered, and none was falsely answered.** The
apparatus was built, frozen, audited and proved; the twelve-block crossed discovery panel was
built and sealed exactly as specified; the twin-sham phase was then terminated by an
executor-side process-control failure that cost one charged engine start, after which the panel
could no longer be completed within the frozen budget. The programme closed itself at the
predeclared stop rather than repairing the gap.

---

## 1. What was achieved

**The G1 within-ancestry crossed design is real and is now committed.** This is the substantive
gain of the run and it survives the closure.

FSQBT00's twelve blocks carried one descendant each with geometry and allocation tied to
`S mod 4`, so the two factors were confounded with the ancestry. FCDDH00 unties them: **twelve
independent upstream ancestries, each carrying the complete `{NEAR, FAR} × {H3 member 0, H3
member 1}` quartet, all four descendants grown from one byte-identical precursor.** That was
proved statically before any engine start and verified numerically inside every worker:

* `seed_state(SPEC, TRACER, S, "random")` is a pure seeded draw — no engine step, no advance, no
  geometry symbol — so the precursor is a function of `S` alone and costs **zero** engine advances;
* geometry enters only afterwards, as an explicit argument, through `set_geometry → _blob`, before
  any history is applied; allocation enters only at `apply_dual_history`;
* every one of the 48 descendants re-checked, at run time and with zero advances, that
  `found(S) == PRECURSOR(S) × blob(g)` field by field. **48/48 passed.**
* the historical parity route, the historical explicit route and the FCDDH00 route execute the
  *identical* operation sequence and differ only in the guard selecting `(hA, hB)`, which is the
  same Boolean under `a := 0 if S % 2 == 0 else 1`. No new LawSpec, no new engine, no new
  executable.

`FCDDH00_G1_STATIC_ELIGIBILITY = PASS`.

**Panel.** 12 blocks (seeds 71000–71011), 12 distinct precursor hashes, 48 descendants, one per
cell, **zero rejected candidates**, 390 engine steps each, production/reference mask agreement
48/48, `B > 0` and finite `ρ` 48/48. Sealed and committed with the complete checkpoint and mask
**bytes** — the FSQBT00 missing-checkpoint-bytes defect is not repeated.

**Provenance.** `FCDDH00_PROVENANCE_STATUS = PASS`. All **1392 of 1392** execution-tree paths are
byte-identical to the parent tree object `b36f8218`; the chain `96c7d295 ≺ 16717582 ≺ b3f45ac7 ≺
334b7c2b` is verified; the FCRA00 bundle digest matches `95ef4511…`; `main` is untouched at
`f3921a4d`. Every owner-reported FCRA00 fact was re-checked against committed bytes and agrees
(24/24 cell materiality, 12/12 direct carrier contrast, 10/12 e2 sign concordance, frozen P2
`NOT_TRANSFERRED` with exactly 3 blocks over the tube).

**Oracle.** `FCDDH00_PREANALYSIS_ORACLE_STATUS = PASS` — 23 groups Q0A–Q0W, every one with a
positive analytic identity and at least one required-to-fail mutation of a real dependency; all
fired. Two of the oracle's own first-draft expectations were **wrong and were corrected against
the committed bytes before any engine start**: the parent basis is *nested* (`P1 = e1e1ᵀ` inside
`P2 = P1 + e2e2ᵀ`, so `P1P2 = P1 ≠ 0`), and the analytic K-tail of the enumerable fixture is
16/65536, not 1/65536.

---

## 2. What stopped it

The twin-sham driver was launched as a background job **inside a tool call**. That tool call has a
120-second wall limit; when it expired the harness killed the entire process group, terminating
row `SHAM_1_71007_FAR_a1` in flight. 59 of the 96 required rows had completed and been published.

The write-ahead ledger did its job exactly as designed:

| evidence for the lost row | |
|---|---|
| `INTENDED` written and fsynced | yes |
| `ACK` marker | **present** |
| `ADVANCE` marker (fsynced) | **present** |
| output bytes | absent |

Under the frozen contract an existing `ADVANCE` marker means the start is **charged and may never
be replayed**. That marker is written just before the `execv` into the committed parent worker,
which the master freeze already declares "deliberately CONSERVATIVE: it can only over-charge a
deterministic pre-flight failure, never under-charge an engine advance". That conservatism was
**honoured, not reinterpreted after the fact** — reinterpreting it because it now hurts would be
precisely the post-hoc favourable reading the protocol exists to prevent.

The panel then closes by **two independent and individually sufficient arguments**:

1. **No-replay.** Descendant `71007_FAR_a1` has a missing twin, and §7.2 says a missing twin stops
   the programme with zero discovery active starts.
2. **Arithmetic, needing no judgement at all.** 60 sham starts charged of 96 authorized leaves
   **36**; **37** rows are still missing; **37 > 36**. The complete twin-sham panel is unreachable
   within the frozen budget however one reads the replay rule.

---

## 3. What was deliberately NOT done

No row was rerun, replaced or imputed. No TAU was computed and **no threshold lock exists**. No
active start was made. **No hold-out state was generated.** No reader series was decoded and **no
response quantity of any kind exists in this tree** — no `z`, no `d`, no `x`, no axis, no score,
no p-value. The twin-sham oracle was restricted to hash-level identity on the pairs actually
acquired, precisely so that nothing resembling a partial analysis of an incomplete panel exists.

## 4. What the acquired evidence does establish about the instrument

All **29** descendants for which both twins were acquired are **bit-identical over the full
horizon**: identical per-time state hashes, identical terminal hashes, identical full-field output
digests, empty touch set at `t0`, input checkpoint unchanged, identical masks and normalizers.
The measuring apparatus behaved exactly as required. The loss is executor infrastructure, not
physics and not instrument.

## 5. Start ledger

| phase | charged | authorized | unused |
|---|---|---|---|
| discovery construction | 48 | 96 | 48 |
| discovery sham | 60 | 96 | 36 |
| discovery active | 0 | 96 | 96 |
| hold-out construction | 0 | 128 | 128 |
| hold-out sham | 0 | 128 | 128 |
| hold-out active | 0 | 128 | 128 |
| other / diagnostic | **0** | 0 | — |
| **total charged** | **108** | 672 | 564 |

`TOTAL_RAW_ADVANCE_SEQUENCES = 108`. There were no timing probes, no smoke tests and no
diagnostic continuations: `OTHER_STARTS = 0`.

## 6. Orthogonal field tuple

See `FCDDH00_DECISION_MATRIX.json` for all 44 canonical fields. The load-bearing ones:

```
FCDDH00_PROVENANCE_STATUS            = PASS
FCDDH00_G1_STATIC_ELIGIBILITY        = PASS
FCDDH00_PREANALYSIS_ORACLE_STATUS    = PASS
FCDDH00_RANDOMIZATION_LICENSE        = True   (never exercised; no outcome was ever scored)
DISCOVERY_CONSTRUCTION_STATUS        = COMPLETE
DISCOVERY_PANEL_STATUS               = SEALED_12_BLOCKS_48_DESCENDANTS
DISCOVERY_SHAM_STATUS                = INCOMPLETE__PROCESS_CONTROL_FAILURE
DISCOVERY_RAW_ACTIVE_STATUS          = NOT_REACHED_BY_PREDECLARED_STOP
every remaining discovery and hold-out field = NOT_REACHED_BY_PREDECLARED_STOP
FSQBT00_LEGACY_STRICT_MAX4_ALL_BLOCK_CONTAINMENT_STATUS = FAILED_AS_PREDECLARED
P2_POPULATION_TRANSFER_INTERPRETATION                   = INCONCLUSIVE_FROM_THIS_GATE_ALONE
```

The two inherited P2 fields are carried through **unchanged**: this programme neither reran nor
reclassified the historical gate, and it produced no evidence bearing on it.

## 7. Claim ceiling actually used

None of the positive clauses is used. FCDDH00 makes **no** claim about a carrier-differential
response to geometry, about materiality, about allocation-orbit robustness, about P2 transfer, or
about anything else. Its only affirmative claims are structural and are fully evidenced: the G1
within-ancestry crossed construction is freezable and was executed on twelve fresh ancestries; the
parent chain is byte-exact; the pre-analysis apparatus is non-vacuous; the twin-sham instrument is
bit-exact on every pair acquired.

## 8. Next eligible experiment

A rerun of exactly this authorization, with **no scientific change whatsoever**, on a fresh
namespace (`N = 71000` and the whole interval 71000–71055 are now consumed and may never be
reused). The single required engineering change is executor-side and is already specified in
`PROTOCOL_DEVIATIONS.md` D2: long acquisitions must run in their own session so that no tool-call
wall limit can reach the worker process group, and the driver must be row-resumable *before* the
first start is charged. That change touches no estimand, no gate, no threshold and no budget, so
it is a packaging fix — but the programme itself may not be restarted under the present
authorization, because its discovery namespace and 108 of its starts are spent.
