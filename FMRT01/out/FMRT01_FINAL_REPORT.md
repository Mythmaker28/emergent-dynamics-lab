# FMRT01 — FRESH MINIMAL REPRODUCTION TEST 01
## FINAL REPORT

The first causal experiment in this programme. It asks one question and answers it:
**after a matured daughter centre is formed, and its parent centre alone is removed, does the daughter
independently maintain and renew its qualified X field?**

---

## 0. The answer in one paragraph

No — not at the level this experiment was built to detect. Of 85 seed blocks, 22 produced a functional
daughter that reached the frozen maturation event and was intervention-eligible. All 22 of them passed
R1 exactly: the daughter's X field was built from newly produced material, not inherited stock.
After selective removal of the parent centre, 3 of those 22 met the frozen R2 criterion for independent
maintenance. The frozen decision rule required 4. The exact one-sided p-value against `H0: q <= 0.05`
is `0.09482304591843077`, above 0.05. **H0 is not rejected.** The conditional autonomy rate is `0.13636363636363635`
with an exact one-sided 95% lower bound of `0.038223511006417944`, which does not clear the null.

Minimal reproduction is **not** causally established. The experiment is technically valid and the
result is a real negative, not a failure of execution.

---

## 1. What was fixed before any world existed

The freeze was committed **alone**, holding 21 files and zero world artefacts, at
`90750ad6e0fff8e0add76371b33fccf749f02806`. The raw was committed before any analysis, at
`61f8f39682f3e557827735207292e4a97d3a5aab`.

| Fixed in advance | Value |
|---|---|
| Design | A |
| Blocks x arms | 85 x 3 = 255 primary worlds (cap 256) |
| Null | `q <= 0.05`, one-sided 0.05 |
| Decision rule | `critical(M) = smallest k with P[Binomial(M,0.05) >= k] <= 0.05` |
| Methods hash | `ca6318d7ccd38cd6d4eb75b32a4d54d6de98265594204693c21a1680c5e7fd87` |
| Engine | byte-unchanged, `2172deae5bbabf37…` |
| New parameter points | 0 |
| Adaptive retuning | forbidden, not used |
| Adaptive sample size | forbidden, not used |

The design choice was made mechanically and against the previous mission's proposal:

- **A paired 3-arm common-seed blocks** — 150 worlds for power 0.80 at q = 0.40; contrast matched — the three arms are bit-identical immediately before the intervention, by construction
- **B 2:1:1 independent allocation (SPOIQ01 proposal)** — 256 worlds for power 0.80 at q = 0.40; contrast unmatched — arms differ by seed as well as by treatment

A reaches the 0.80 power target at q = 0.40 with 150 primary worlds where B needs 256, and it delivers a strictly stronger causal contrast because the arms share the exact pre-intervention state. B was not retained merely because SPOIQ01 proposed it.

---

## 2. Execution

| | |
|---|---|
| Blocks attempted | 85 |
| Blocks completed | 85 |
| Technical failures | 0 |
| Technical reserves spent | 0 of 6 |
| Pre-intervention fork identity held | True, in every block |
| Raw archives | 85 |

Every block's three arms were forked from one bit-identical pre-intervention state by deep copy,
and that identity was still verified by physical-state hash and RNG fingerprint rather than assumed.

---

## 3. The primary result

| Quantity | Value |
|---|---|
| Trigger-eligible worlds M | 22 |
| R1 exact | 22 of 22 |
| R2 successes K | 3 |
| Critical count required at M | 4 |
| Conditional autonomy rate q | `0.13636363636363635` |
| Exact one-sided 95% lower bound | `0.038223511006417944` |
| Exact two-sided 95% interval | `[0.029055851128746688, 0.34912209725740806]` |
| Exact one-sided p-value | `0.09482304591843077` |
| Reject H0 | **False** |
| Both decision formulations agree | True |

Population-level, with every seeded block in the denominator and pre-intervention failures counted as
failures rather than censored: 3 of 85, rate `0.03529411764705882`, exact 95% interval `[0.0073384869548482725, 0.09969637090688122]`.

The conditional rate is **not** substituted for the population rate anywhere.

---

## 4. The controls did their job

| Arm | Daughter exists | Criterion D | Post-intervention births | R2 pass | Median final N_X |
|---|---|---|---|---|---|
| SELECTIVE | 20/22 | 3 | 20 | **3** | 158.0 |
| SHAM | 22/22 | 8 | — | 8 | 244.5 |
| GLOBAL | 0/22 | 0 | — | 0 | 80.5 |

- **SHAM** removed 0 molecules, as it must, and the trigger-and-audit machinery did not itself destroy
  daughter function: the daughter survived in 22 of 22.
- **GLOBAL** drove every Y to zero (`final_NY_all_zero = True`), no daughter survived anywhere, and the X
  field decayed to a median of 80.5 — the old-material interpretation is supported, not assumed.
- The three arms order themselves exactly as a causal reading predicts on final X:
  GLOBAL 80.5 < SELECTIVE 158.0 < SHAM 244.5.
- **No third centre interfered** in any post-intervention window, in any arm: SELECTIVE 0, SHAM 0.

---

## 5. Where the failures actually are

The partition is ordered, mutually exclusive and exhaustive; its self-check reports
`IS_A_PARTITION = True` and sums to 85 of 85.

| Class | Count |
|---|---|
| `no_trigger` | 63 |
| `trigger_too_late` | 0 |
| `triggered_R1_failed` | 0 |
| `R1_ok_R2_failed_third_centre` | 0 |
| `R1_ok_R2_failed_integrity` | 0 |
| `R1_ok_R2_failed_other` | 19 |
| `MINIMAL_REPRODUCTION_SUCCESS` | 3 |

Read plainly, there are **two** failure sites and they are not the ones a hopeful reading would pick:

1. **R0 — most worlds never make a functional daughter at all.** 63 of 85 blocks never triggered.
   Of those, 46 went extinct, 13 reached the horizon without maturing, and 4 produced a premature
   third centre. Extinction, not third-centre interference, is the dominant pre-intervention loss.
2. **R2 — the daughter does not hold up on its own.** 19 of the 22 eligible daughters failed R2 for
   reasons that were neither third-centre interference (0) nor loss of X integrity (0).

And there are three sites where **nothing** went wrong:

- **R1 did not fail once.** `triggered_R1_failed = 0`.
- **Intervention timing cost nothing.** `trigger_too_late = 0`.
- **X integrity never broke** in a post-intervention window.

---

## 6. The most interesting thing in the data

R1 passed **22 of 22**. The daughters are not made of the parent's material.
The fraction of each daughter's X field that was produced after separation ranges from `0.7079` to `0.9714`,
median `0.8781`. This is measured molecule by molecule from the engine's inert tracker, with a
threshold-free criterion, and it is the counterfactual F5 asks, restricted to material that existed
before the daughter did.

Separately, criterion E — post-intervention X births **inside** the surviving daughter disc — fired in
20 of 22 SELECTIVE worlds. Production inside the daughter did not stop when the parent was removed.

What failed was criterion **D**: the daughter's local X mass had to exceed the exact 95%% binomial upper
bound on how much of the **whole world's** pre-intervention X could still be alive after 250 steps.
The median SELECTIVE daughter fell `-20.0` molecules short of that bound; the median SHAM daughter, with its
parent fully intact, fell `-8.5` short. the frozen bound is Q_0.95 of the survival of the WHOLE WORLD's X stock over 250 steps, while the mass compared is the daughter's local X alone. The bound is therefore severe by construction: it asks the daughter alone to exceed what every old molecule anywhere could leave behind. That severity is exactly what makes the 0.05 false-positive rate valid, and it is also why the median daughter falls short of it even in the SHAM arm, where the parent is untouched.

That is a property of the frozen criterion, stated here as a fact and **not repaired**
(`MAX_POST_OUTCOME_SCIENTIFIC_REPAIRS = 0`). It is the single most important thing for the successor
mission to examine, because a criterion that the SHAM arm clears only 8 times in 22 is measuring
something much stronger than "the daughter kept its field".

---

## 7. Post-hoc description, quarantined

`STATUS = POST_HOC__NOT_PART_OF_THE_FROZEN_TEST__NO_DECISION_ATTACHED`

these quantities were computed after the outcome was known. None of them was prespecified, none carries a decision, and none is used to support or weaken the terminal disposition. They are published because they are the most informative content of the data and hiding them would be worse than quarantining them.

Paired on the same 22 blocks, criterion D:

| | SHAM passes | SHAM fails |
|---|---|---|
| **SELECTIVE passes** | 1 | 2 |
| **SELECTIVE fails** | 7 | 12 |

Discordant pairs 9, exact two-sided sign test `p = 0.1796875`. Direction: removing the parent centre lowers criterion-D passage on the same blocks. **No decision is attached to
this number.** post hoc; the frozen primary test is the one-sample exact binomial against q <= 0.05

Trigger times: min 646, median 3323.0, max 10708 against `LATEST_ALLOWED_TRIGGER = 10750`. one block matured at step 10708, only 42 steps inside the frozen boundary. FDFLT01's largest observed maturation was 9464, so the planning input understated the tail. No world was lost, but the margin was thin and is reported rather than left implicit.

Parent/daughter identity: level 1 (minimum toroidal distance to the pre-separation centroid) resolved 21 of 22. One block needed level 4, the lexicographic canonical tie-break — the exact tie class first seen in RCD01 as F_B1_i182_s961444860 occurs in fresh worlds too.

Observed trigger rate 22/85 = `0.258824`, between the conservative planning input `0.214117` and the FDFLT01
point estimate `0.276042`. The sample-size was not optimistic.

---

## 8. Integrity of the run

### Durability, both times verified by reading back from the disk

| Stage | Verdict | Evidence |
|---|---|---|
| Pre-run, before world #1 | `PASS` | read-back hashes identical; restored tree SHA identical; 33/33 frozen method hashes reproduced from the device copy; worlds run at that point: 0 |
| Raw, before any analysis | `PASS` | read-back hashes identical; restored tree SHA identical; 85 archives restored from the device copy |

A write receipt was never accepted as proof. In both cases the files were staged **back** from the
Windows disk into the container and re-hashed, and the repository was rebuilt from the device copy in a
scratch clone.

### The one thing that was disclosed rather than concealed during the run

> the raw filename convention appends _NOTRIG to blocks in which the frozen trigger never fired. Building this manifest therefore reveals TRIGGER OCCURRENCE, which the frozen firewall listed as withheld. This is a real imperfection of the runner, which was frozen before any world existed and is not edited now. Its causal consequence is nil: all 85 blocks had already completed when the manifest was built, no reserve was spent, the sample size was fixed and non-adaptive, and no R1 or R2 outcome was exposed. It is reported rather than concealed.

### The adversarial review

One review, 19 attacks, reviewer not patched after seeing its verdicts. 17 refuted outright.
The two it did not refute were adjudicated on substance and both fell:

- **16 raw-before-analysis chronology** → `REFUTED_ON_SUBSTANCE__REVIEWER_PREDICATE_IS_BRITTLE`. the reviewer reads RAW_COMMIT out of FMRT01_RAW_MANIFEST.json. That field cannot exist: the raw manifest is written BEFORE the raw commit, so it structurally cannot carry its own commit SHA. The reviewer demanded a field whose existence would itself be an anachronism.
- **17 pre-run and raw durability** → `REFUTED_ON_SUBSTANCE__REVIEWER_LOOKED_IN_THE_WRONG_FILE`. the reviewer reads WINDOWS_PRE_RUN_DURABILITY out of the COMMITTED master freeze, where it is deliberately PENDING and deliberately never rewritten, and RAW_DURABILITY_BEFORE_ANALYSIS out of the raw manifest, which likewise predates the verdict. Both verdicts live in files created after the frozen ones, precisely so that no committed freeze is ever edited.

`LOAD_BEARING_DEFECT_CONFIRMED_AFTER_ADJUDICATION = False`.

---

## 9. A defect in my own frozen decision module, reported in full

fmrt01_final.py, frozen and hashed before any world existed, reads two of its ten decision gates out of files that structurally cannot contain the values it wants. It reads PRE_RUN_DURABILITY out of the COMMITTED master freeze, where the field is PENDING and is deliberately never rewritten, and RAW_DURABILITY_BEFORE_ANALYSIS out of the raw manifest, which is written before that verdict exists. Both gates therefore read false while both operations in fact PASSED with read-back proof.

the frozen module expects the committed master freeze to be edited to PASS after the freeze commit. FDFLT01 established, from a documented incident, that a freeze which is silently rewritten is worthless even when its content matches. The two frozen rules are in direct conflict and the conflict was unavoidable: a bundle cannot be built before the commit it carries. I resolved it in favour of NEVER rewriting a committed freeze, and I record the cost here rather than hiding it.

The frozen module was **not edited** (`sha256 = 1f84af3913f783ca23a066c105e96382dadf69633e2e7d370025390a1ad4c2f0`, unchanged). Its literal output is preserved in
`FMRT01_FINAL_DISPOSITION.json` exactly as written:

```
TECHNICALLY_VALID   = False
FINAL_DISPOSITION   = MINIMAL_REPRODUCTION_TEST_TECHNICALLY_INVALID
```

Recomputing the same ten gates from their true sources changes exactly two — `PRE_RUN_DURABILITY, RAW_DURABILITY_BEFORE_ANALYSIS` — and nothing else:

| Gate | Frozen module | True source |
|---|---|---|
| `ALL_BLOCKS_ACCOUNTED` | True | True |
| `NO_TECHNICAL_FAILURE` | True | True |
| `FORK_IDENTITY_OK` | True | True |
| `UNARMED_INERTNESS` | True | True |
| `FIXTURES_PASS` | True | True |
| `FAILURE_PARTITION_VALID` | True | True |
| `PRE_RUN_DURABILITY` | False | True |
| `RAW_DURABILITY_BEFORE_ANALYSIS` | False | True |
| `NO_LOAD_BEARING_REVIEW_DEFECT` | True | True |
| `DECISION_RULES_AGREE` | True | True |

REJECT_H0 is false under BOTH readings, so no correction of the gate addressing can reach MINIMAL_REPRODUCTION_CAUSALLY_QUALIFIED. The adjudication moves the result from one negative disposition to a different negative disposition. It converts nothing.

Reported disposition: **`MINIMAL_REPRODUCTION_NOT_QUALIFIED__DAUGHTER_INDEPENDENCE_NOT_ESTABLISHED`**, because the adjudicated one, because declaring this experiment technically invalid would be a false statement: there were 0 technical failures, fork identity held in every block, and both durability operations passed with staged read-back verification from the Windows disk.

For successors: fmrt01_review.py and fmrt01_final.py both assume durability verdicts live inside artefacts that are frozen before those verdicts exist. Any successor mission must place the durability verdict in its own file and must read it from there.

---

## 10. History and provenance

- Inherited history at and below `06c592313df96601de8d2a89676d5a5cf79fc414` was **not** rewritten: `INHERITED_HISTORY_UNTOUCHED = True`.
- Parent tip `a453e215f39150afe8a2e9c59a74150b9abecd63` is an ancestor of HEAD: True.
- Commits added by this mission: 2.
- this mission began after the FIFTH container rollback. The repository was restored from RCD01_INCREMENT.bundle on Tommy's Windows disk. The SPOIQ01 capability module was never made durable and was destroyed; it is RECONSTRUCTED here and RE-QUALIFIED from scratch, and SPOIQ01's recorded hashes are NOT claimed.

- The SPOIQ01 durability debt is `UNPAYABLE__ARTEFACTS_DESTROYED`. SPOIQ01's outputs never reached external storage before the fifth container rollback and were destroyed with the container. A search of the current container and of the Windows recovery tree finds no SPOIQ01 artefact of any kind. The debt cannot be paid by transferring something that no longer exists, and no SPOIQ01 hash is reasserted from memory. The capability SPOIQ01 qualified has been REBUILT and RE-QUALIFIED inside FMRT01 from scratch, which is the only honest remedy; that re-qualification is what this freeze rests on.

---

## 11. What this does and does not establish

**Established:** in 85 fresh worlds at the frozen B1 law, a second spatial centre reaching the frozen
maturation event is built from newly produced X, not from the parent's material — 22 of 22, exactly and
threshold-free. And removing the parent centre alone is a real perturbation with a measurable effect on
the daughter's field, distinguishable from both no intervention and total organiser removal.

**Not established:** that the daughter maintains its field independently at the strength the frozen R2
criterion demands. The null `q <= 0.05` stands.

Unconditionally, and regardless of anything above:

```
H3_STATUS = NOT_TESTED
REPRODUCTION_STATUS = NOT_TESTED
HEREDITY_STATUS = NOT_TESTED
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED
X_LAWSPEC_BASELINE = UNCHANGED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
STRONG_SELF_REPRODUCTION_STATUS = NOT_TESTED
R3_STATUS = NOT_TESTED
```

minimal reproduction under R0+R1+R2 at the frozen B1 law. Not strong self-reproduction, not second-generation competence, not heredity, not evolution, not life.

---

## 12. Terminal disposition

```
MINIMAL_REPRODUCTION_NOT_QUALIFIED__DAUGHTER_INDEPENDENCE_NOT_ESTABLISHED
```

Successor, zero-run, created but not executed: `HANDOFF_MINIMAL_REPRODUCTION_FAILURE_AUTOPSY_01.md`.
No parameter point is switched. No architecture change is proposed. No substrate change is proposed.
