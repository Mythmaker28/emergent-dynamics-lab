# MINCORE_SCOPE_CORRECTION_ADDENDUM

**Append-only.** This document corrects the scope of the MINCORE record. It adds nothing to the
evidence base: **no engine was started, no world was advanced, no trajectory was produced for
this addendum.** The only computation performed here is closed-form algebra on a reduced ODE
(section 4) and SHA-256 verification of bytes that already existed (section 1). Nothing written
below changes any file already committed on `gen2/minority-composite-seed-00`; the earlier
documents stand as written and are corrected only by this addendum.

---

## 1. Byte provenance — recovery and verification

One targeted recovery was attempted, from artefacts already present: the working tree at
`MINCORE/`, the local branch `gen2/minority-composite-seed-00` in the clone `edl`, and the
recovery bundle `MINCORE_gen2_branch.bundle`. Nothing was fetched, nothing was requested from
anyone.

All twelve declared SHA-256 values were recomputed and compared before any byte was reused:

| artefact | declared SHA-256 | recomputed | verdict |
|---|---|---|---|
| `code/mincore.py` | `f5ecd405…c385af1` | identical | OK |
| `code/pilot.py` | `1077a26f…8cfa5f8d` | identical | OK |
| `code/integrity.py` | `75c7fce3…611d2dd74c` | identical | OK |
| `out/GEN2_MINORITY_COMPOSITE_PREPLAN.md` | `e45c78b7…98bf2ae` | identical | OK |
| `out/GEN2_MINORITY_COMPOSITE_DECISION_RECORD.md` | `3a0de550…57d7bd` | identical | OK |
| `out/GEN2_MINORITY_COMPOSITE_FINAL_REPORT.md` | `d500812e…2514389` | identical | OK |
| `out/_freeze.json` | `6bcf3b31…d3506b1` | identical | OK |
| `out/_static_gate.json` | `3a43540a…94f98f` | identical | OK |
| `out/_integrity.json` | `11fc3d30…b3877ab3989` | identical | OK |
| `out/_pilot.json` | `14c51bd5…c442384047` | identical | OK |
| `out/pilot.log` | `09d013f1…53d07581` | identical | OK |
| `MINCORE_gen2_branch.bundle` | `693d7b5d…936c32bf78f` | identical | OK |

```
MINCORE_BYTES = INDEPENDENTLY_VERIFIED
RECOVERY_ATTEMPTS = 1
MISSING_ARTEFACTS = 0
```

A separate note, because it matters for reproducibility: an automatic formatting pass touched
`code/mincore.py`, `code/pilot.py` and `code/integrity.py` after the MINCORE freeze was written.
The hashes above are the **post-formatting** bytes, and they are the bytes that the freeze record
`out/_freeze.json` names. The freeze record and the executed bytes therefore agree; what cannot
be asserted from the surviving artefacts alone is that the formatting pass preceded the run
rather than followed it. Since the pass is whitespace-and-import-order only and the executed
result is a single donor trajectory whose descriptor is stored, this is recorded as a
provenance caveat, not as a defect:

```
CODE_BYTES_MATCH_FREEZE_RECORD = TRUE
FORMATTING_PASS_ORDER_RELATIVE_TO_RUN = UNRESOLVED
```

---

## 2. What the MINCORE stop did and did not establish

### 2.1 The stop itself was correct

The frozen protocol required the first source cluster to stand clear of the wall by
`WALL_MARGIN_ELLX * ell_X = 2.0 * 3.1623 = 6.3246` sites before any arm could be built from it.
The realised donor at 4000 steps had `min_dist_to_wall = 0`. The gate refused, the run stopped,
and no arm was built. That is the protocol behaving as designed, and it is not withdrawn.

### 2.2 The `integrity.py` arm was a protocol-order violation

`code/integrity.py` line 97 executes `P.run_arm(pay, "XY_COMPOSITE_INTACT", 1, match_gate=True)`
— a complete `RECV_STEPS = 4000` receiver arm on the scientific kinetics — in order to test that
a score cannot be read before the horizon. Its output was discarded and its existence was
declared in `out/_freeze.json`. Declaring it was right. Running it there was not.

The earlier report should not be read as saying that the code followed the plan exactly, or that
no arm was consumed. **A full arm was consumed, and it was consumed inside an integrity harness
that the plan placed outside the experimental sequence.** The order of operations in the plan
was: freeze → integrity tests → blocks. A full-horizon arm executed during the integrity step is
an experimental start executed out of order, whatever is done with its output afterwards.

```
INTEGRITY_HARNESS_ARM = PROTOCOL_ORDER_VIOLATION
PLAN_EXECUTED_AS_WRITTEN = FALSE
ARMS_CONSUMED_OUTSIDE_THE_BLOCK_SEQUENCE = 1
```

The mechanical correction adopted for all future work is stated in section 6.

### 2.3 Ledger audit — the machine ledger under-counts by one

Two independent records of the same quantity disagree:

| source | mechanism | value |
|---|---|---|
| `out/_freeze.json` → `declared_out_of_plan_outcome_informative_starts.count` | hand-declared | 3 |
| `code/pilot.py` line 32 → `PRE_FREEZE_STARTS` | hard-coded constant | 2 |
| `out/_pilot.json` → `ledger.total_outcome_informative` | computed as `LEDGER["count"] + PRE_FREEZE_STARTS` | 3 |
| true total (3 declared out-of-plan + 1 in-plan donor) | audit | **4** |

`PRE_FREEZE_STARTS` was set to 2 — the two short capacity probes — and never raised to 3 when
the `integrity.py` arm was added to the declared list. The machine-written ledger in
`out/_pilot.json` therefore reports **3** where the audited total is **4**. The final report's
figure of four starts is the correct one; the JSON is the one that is wrong. The four are:

1. a 300-step probe on a 12×12 world (revealed `2*S0 == CAP` left no free capacity);
2. a 200-step probe on a 40×40 world (informed `CAP = 16`);
3. the full 4000-step `XY_COMPOSITE_INTACT` arm inside `integrity.py` (section 2.2);
4. the in-plan donor `donor_11`, 4000 steps, which hit the wall gate.

```
MINCORE_OUTCOME_INFORMATIVE_STARTS_AUDITED = 4
MACHINE_LEDGER_IN__pilot_json = UNDERCOUNTS_BY_1
LEDGER_DEFECT_CAUSE = PRE_FREEZE_STARTS_CONSTANT_NOT_UPDATED_WHEN_THE_THIRD_ITEM_WAS_DECLARED
```

The bounded invariant checks in `integrity.py` (lines 15, 32, 38, 44, 53, 59: 60 to 300 steps
each, asserting exact algebraic invariants, never reading a score) are **not** counted as
outcome-informative starts, in this addendum as in the original ledger. Section 6 turns that
informal distinction into an enforced one.

### 2.4 What the saved outputs do and do not contain

The single descriptor stored at the stop is:

```
N_X = 1186    N_Y = 1081    support_cells = 439    min_dist_to_wall = 0
n_contact_components = 56   largest_component_cells = 355   n_Y_centres = 2
Rg_X_about_Y = 7.8809   XY_contact_density = 0.3713   conversion_flux_per_XY = 1.7292
Y_centroid = (19.9658, 20.0370)
```

Present and usable: aggregate counts, the number of contact components, the size of the largest
one, the number of Y-only components, the radius of gyration of X about the Y centroid, and the
distance from the occupied support to the wall.

**Absent, and therefore left unresolved:** the per-component `N_X` and `N_Y`; the mass and
species composition of whichever component reaches the wall; radial profiles of X and Y about
any centre; and the chronology of Y births. The saved output is one descriptor at one time; it
contains no time series and no per-component decomposition. No missing trajectory is
reconstructed here, and no reclassification that would require those fields is attempted.

```
PER_COMPONENT_MINORITY_AT_THE_STOP        = UNRESOLVED
WALL_TOUCHING_COMPONENT_COMPOSITION       = UNRESOLVED
RADIAL_PROFILES                           = UNRESOLVED
Y_BIRTH_CHRONOLOGY                        = UNRESOLVED
```

One descriptive statement is licensed by what is stored, and it is descriptive only:
`N_Y / N_X = 0.9114` at the stop, so the organiser was not a numerical minority of the material
at that time. This is a description of one saved state. It is **not** used anywhere in this
mission to select a parameter, a threshold or a horizon; see the provenance table in the
preplan.

---

## 3. The six status fields

```
FROZEN_MINCORE_CONFIGURATION         = SOURCE_LOCALIZATION_AND_MINORITY_GATE_FAIL
STATIC_LOCALIZATION_GATE             = INCOMPLETE__DEFECT_DISCOVERED_POST_START
CAUSAL_ARMS_COMPLETED                = 0
BILINEAR_MINORITY_CORE_FAMILY        = NOT_CLOSED
Y_SATURATION_MATHEMATICALLY_REQUIRED = NOT_ESTABLISHED
OBSERVED_MECHANISM                   = CONSISTENT_WITH_Y_REPLICATION_TOO_FAST__NOT_PROVEN
```

Reading of each:

- **`FROZEN_MINCORE_CONFIGURATION`** — the specific frozen point failed on two counts at once:
  the source cluster did not stay localised (it reached the wall), and the organiser did not stay
  a minority. Neither is a statement about the model family.
- **`STATIC_LOCALIZATION_GATE`** — the static gate in `out/_static_gate.json` tested a growth
  inequality and a predicted cluster radius of 12.32 sites against a margin of 7.68. It did not
  test the *timescale* condition that decides whether a growing cluster ever separates. That
  defect was found only after the run, so the gate is incomplete, not merely unlucky.
- **`CAUSAL_ARMS_COMPLETED = 0`** — the donor gate refused before any arm was built. The arm that
  ran inside `integrity.py` is counted as a consumed start (section 2.2), not as a causal arm:
  it had no control, no comparison and no retained output.
- **`BILINEAR_MINORITY_CORE_FAMILY = NOT_CLOSED`** — see section 4.
- **`Y_SATURATION_MATHEMATICALLY_REQUIRED = NOT_ESTABLISHED`** — nothing in the sources requires
  a saturating term on Y for a bounded maintained state to exist. The counterexample in
  section 4 has no Y-saturation term and is bounded and stable.
- **`OBSERVED_MECHANISM`** — a single descriptor at a single time is consistent with the
  organiser replicating too fast relative to cluster separation, and is also consistent with
  other mechanisms that the stored fields cannot separate. It is not proven.

---

## 4. Withdrawal of the bilinear impossibility statement

### 4.1 What was claimed, and why it is wrong

The earlier work asserted, as a general property, that a bilinear birth term in `X*Y` together
with a linear death term on `Y` makes maintenance of `Y` and boundedness of `Y` mutually
exclusive. **That statement is withdrawn.**

It is true only in the artificial reduction in which the per-`Y` birth rate is a constant:
`dy/dt = y*(lambda - muY)` with `lambda` independent of `x` and `y`. There, `y` grows or decays
exponentially and no positive equilibrium exists. But that reduction is not the model. In
`code/mincore.py` the number of births in a cell is
`Binomial(cand, min(1, k*nX*nY))` with `cand = min(n_resource, free)` and
`free = CAP - occupancy`, so the effective per-`Y` rate carries a capacity factor that falls to
zero as the cell fills. With that factor present, a positive equilibrium can exist and can be
stable.

### 4.2 Explicit counterexample, with MINCORE's own constants

Well-mixed reduction of the same reaction, with the capacity factor kept:

```
dx/dt = kX * x * y * c(x,y) - muX * x
dy/dt = kY * x * y * c(x,y) - muY * y            c(x,y) = s * (1 - (x+y)/K)
```

Using MINCORE's frozen `kX = 0.02, kY = 0.0008, muX = 0.005, muY = 0.0005` and `s = 3, K = 10`:

Any interior equilibrium lies on the ray `y/x = kY*muX/(kX*muY) = 0.4`, and `x` solves
`0.42 x^2 - 3 x + 0.625 = 0`, whose discriminant is `7.95 > 0`. Both roots are positive:

| equilibrium | x | y | c | x+y | eigenvalues of the Jacobian | verdict |
|---|---|---|---|---|---|---|
| upper | 6.92806 | 2.77123 | 0.09021 | 9.6993 | −1.19147e−1, −6.55799e−4 | **stable node** |
| lower | 0.21479 | 0.08592 | 2.90979 | 0.3007 | −1.61508e−3, +1.49992e−3 | saddle |

Residuals at both points are below `3e-18`. The upper equilibrium is bounded (`x+y = 9.70 < K`),
maintained (`x > 0`, `y > 0`), has strictly linear death on `Y` and no saturating term on `Y`.
It is therefore a counterexample to the withdrawn statement, built from the project's own rate
constants. Computation: `code/withdrawal_counterexample.py`; output
`out/_withdrawal_counterexample.json`.

### 4.3 What survives

What survives is narrow and it is a statement about the *reduction*, not about the family:

> If the per-`Y` birth rate is treated as a constant independent of the state, the reduced
> equation for `y` has no positive equilibrium. The MINCORE engine does not have that property,
> because `cand` and `free` depend on the state.

```
BILINEAR_PLUS_LINEAR_DEATH_IMPOSSIBILITY = WITHDRAWN
SCOPE_THAT_SURVIVES = THE_CONSTANT_RATE_REDUCTION_ONLY
BILINEAR_MINORITY_CORE_FAMILY = NOT_CLOSED
```

Two consequences for the record. First, the MINCORE stop cannot be read as evidence that the
model family is exhausted; it is evidence about one frozen point in it. Second, no future work
may cite the withdrawn statement as a reason not to test a bilinear minority core.

---

## 5. What was actually missing from the MINCORE static gate

This is stated here because it defines the mission that follows, and because it is a
deduction from the frozen source, not from any output.

`out/_static_gate.json` checked that an X cloud around a Y seed **grows**
(`c*kX*n_Y*A_Y > muX*(A_Y + pi*ell_X^2)`, satisfied with margin factors 1.10 to 5.34) and that
the predicted cluster radius left a wall margin. Growth and geometry were tested. **The rate at
which new organisers appear, relative to the time two organisers need to move apart, was not
tested at all.** That comparison is the Kamimura–Kaneko condition, it is the only condition that
distinguishes a dividing cluster from an exploding one, and its absence is the defect referred
to by `STATIC_LOCALIZATION_GATE = INCOMPLETE__DEFECT_DISCOVERED_POST_START`.

Supplying that missing comparison, deriving it in dimension 2, and adjudicating it before any
further reconstruction work, is the whole content of `MINCORE-TIMESCALE-WINDOW-01`.

---

## 6. Mechanical correction carried into all subsequent work

The `integrity.py` violation was possible because "a bounded invariant check" and "an
experimental arm" were distinguished only by the intention of whoever wrote the file. That
distinction is now enforced by the code rather than asserted in prose. From this mission
onward:

1. Every module that may advance a world exposes exactly one entry point that increments the
   start ledger, and the ledger raises before the advance, not after.
2. The integrity harness imports a guarded facade whose `advance` refuses more than
   `MAX_TEST_STEPS` steps in total across the whole harness, and whose descriptor/score
   functions are not importable at all. A full-horizon arm inside the harness is therefore a
   `RuntimeError`, not a judgement call.
3. Integrity tests run **before** the freeze, so that fixing a test failure never invalidates a
   freeze; the freeze hash is taken over the tested bytes.
4. The audited start total is recomputed at the end from the ledger itself, and cross-checked
   against a hand-declared list; a mismatch is reported as a failure, not silently overwritten
   by a constant.

```
GUARDED_TEST_FACADE = REQUIRED_FROM_MTW01_ONWARD
TEST_BUDGET_ENFORCEMENT = MECHANICAL
FREEZE_ORDER = TESTS_THEN_FREEZE_THEN_BLOCKS
```

---

## 7. Prohibitions restated

Nothing in this addendum claims reproduction, heredity, evolution, organism, life, autopoiesis,
fresh matter, biological mass, material lineage, that the same individual persists, or that
material ownership is proven. The MINCORE cluster is a cluster of counters on a lattice. The
word "division" below and in the preplan means one geometric event — a contact structure with
one organiser becomes two contact structures with one organiser each — and nothing beyond it.

```
ENGINE_STARTS_CONSUMED_BY_THIS_ADDENDUM = 0
REPOSITORY_HISTORY_REWRITTEN = NO
PREEXISTING_RESULTS_ALTERED = NO
TOMMY_ACTION_REQUIRED = NONE
```
