# HANDOFF — MINIMAL-REPRODUCTION-FAILURE-AUTOPSY-01

**Status: created, NOT executed. Zero-run successor.**
Issued by FMRT01 under §24, because FMRT01's terminal disposition is
`MINIMAL_REPRODUCTION_NOT_QUALIFIED__DAUGHTER_INDEPENDENCE_NOT_ESTABLISHED`.

This is the **only** successor FMRT01 authorises. No other handoff is created.

---

## 1. Where the failure came from — named exactly

§24 requires naming which of six sites the failure came from. The frozen, ordered failure
partition (`IS_A_PARTITION = True`, sums to 85 of 85) answers it without interpretation:

| Site | Verdict | Evidence |
|---|---|---|
| **R0** | **FAILURE SITE — dominant** | 63 of 85 blocks never produced a maturation event at all. 46 extinct, 13 reached the horizon unmatured, 4 premature third centre. |
| **R1** | **NOT a failure site** | `triggered_R1_failed = 0`. All 22 eligible daughters passed R1 exactly; the median daughter's X field was 89.0 % newly produced material, minimum 70.8 %. |
| **R2** | **FAILURE SITE — decisive** | 19 of 22 eligible daughters failed R2. K = 3 against a required critical count of 4; exact one-sided p = 0.09482304591843077 against `H0: q <= 0.05`. |
| **Third-centre interference** | **NOT a failure site** | 0 third centres in any post-intervention window, in any arm. The 4 premature third centres all occurred before the trigger and are already counted under R0. |
| **X integrity** | **NOT a failure site** | 0 integrity failures in any post-intervention window. |
| **Intervention timing** | **NOT a failure site** | `trigger_too_late = 0`. Latest observed maturation was step 10708 against `LATEST_ALLOWED_TRIGGER = 10750`. |

**Two sites, R0 and R2. Not four, not six.**

---

## 2. The specific question the autopsy must answer first

Inside R2, the failure is **not** diffuse. It localises to one criterion:

| R2 criterion | SELECTIVE arm | SHAM arm |
|---|---|---|
| A — daughter Y centre still exists | 20 / 22 | 22 / 22 |
| C — X integrity held | 22 / 22 | 22 / 22 |
| E — post-intervention X births inside the daughter disc | 20 / 22 | — |
| **D — daughter-local X mass exceeds the survivor bound** | **3 / 22** | **8 / 22** |

Production inside the daughter did **not** stop when the parent was removed — criterion E fired in 20
of 22. What failed was the **mass** comparison.

And criterion D as frozen compares the **daughter's local X mass** against
`Q_0.95[Binomial(N_X_world_at_intervention, (1-muX)^250)]` — a bound derived from the **whole world's**
X stock. It asks the daughter alone to exceed what every old molecule anywhere in the lattice could have
left behind. The median SELECTIVE daughter fell 20 molecules short of that bound; the median SHAM
daughter, with its parent fully intact and feeding the region, still fell 8.5 short.

**A criterion that the SHAM arm clears only 8 times in 22 is not measuring "the daughter kept its
field". It is measuring something considerably stronger.**

This is stated as a fact about the frozen design. It was **not repaired** in FMRT01
(`MAX_POST_OUTCOME_SCIENTIFIC_REPAIRS = 0`), and it must not be repaired retrospectively by any
successor either. It can only be replaced, prospectively, in a freshly frozen design.

### The first question for the autopsy

> Is criterion D the right operationalisation of "the daughter maintains its own field", or does its
> world-scoped bound make it a test of something else? Derive the answer analytically, from the frozen
> kinetics, with **zero** engine runs. In particular: derive what a **daughter-scoped** null would be —
> the false-positive rate of a bound built from the X present **in the daughter's own disc** at the
> intervention rather than in the whole lattice — and establish whether such a bound still admits an
> exact, non-arbitrary 0.05 false-positive guarantee. If it does not, say so; do not invent a threshold.

The autopsy must also state honestly whether replacing D would have changed FMRT01's outcome. It must
compute that counterfactual on FMRT01's already-committed raw archives and report it, **and it must
label the number as a post-hoc re-reading of a completed negative experiment, never as a result.**

---

## 3. The second question — R0

63 of 85 worlds never reached the maturation event. 46 of those went extinct outright.

> What is the exact extinction hazard at B1 over the 11 000-step horizon, and is the observed 46/85
> consistent with it? Derive it from the frozen kinetics. Establish whether the low trigger rate
> (22/85 = 0.2588) is a property of the law, of the horizon, or of the maturation definition.

Note that 0.2588 sits between the FDFLT01 conservative planning input (0.2141) and its point estimate
(0.2760), so the sample-size planning was sound. R0 is a **cost**, not an error.

---

## 4. Constraints on this successor — binding

- `NEW_SCIENTIFIC_ENGINE_RUNS = 0`. This is a **zero-run** autopsy. It reasons from FMRT01's committed
  raw archives and from the frozen kinetics. It runs no world.
- **Do not switch parameter point.** B1 stays. §24 is explicit: *"Do not switch parameter point
  automatically."* A negative R2 result is not evidence that B1 is the wrong point.
- **Do not change substrate.** No `lattice_bond`, no Route E, no alternative engine.
- **Do not reimplement the engine from any report.** `engine_obtc.py` stays byte-identical at
  `2172deae5bbabf37238cf7712cb17663c151494befcf85505c537a7cac0ded30`.
- **Do not rewrite inherited history** at or below `06c592313df96601de8d2a89676d5a5cf79fc414`.
- **Do not repair FMRT01's frozen artefacts.** `FMRT01_FINAL_DISPOSITION.json` in particular is left
  exactly as its frozen module wrote it, including the gate-addressing defect documented in
  `FMRT01_DISPOSITION_ADJUDICATION.json`.

### One defect this successor must fix in its own tooling, prospectively

`fmrt01_review.py` and `fmrt01_final.py` both read durability verdicts out of artefacts that are frozen
**before** those verdicts exist — the master freeze and the raw manifest. Two of ten decision gates and
two of nineteen review attacks fired falsely for this reason alone. Any successor must place each
durability verdict in its own file and read it from there, and must fix that **in its own freeze, before
running anything** — never afterwards.

---

## 5. What this successor may NOT conclude

Whatever it finds:

```
H3_STATUS = NOT_TESTED
REPRODUCTION_STATUS = NOT_TESTED
HEREDITY_STATUS = NOT_TESTED
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED
STRONG_SELF_REPRODUCTION_STATUS = NOT_TESTED
R3_STATUS = NOT_TESTED
X_LAWSPEC_BASELINE = UNCHANGED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
```

R3 — whether a daughter can itself participate in producing a further functional daughter — is **not**
opened by this handoff. §23 reserves that for a positive FMRT01, and FMRT01 was negative. Do not jump
to it, and do not jump to heredity.

---

## 6. Inputs already committed and already durable

| Artefact | Where |
|---|---|
| Freeze commit, 21 files, no world artefact | `90750ad6e0fff8e0add76371b33fccf749f02806` |
| Raw commit, before any analysis | `61f8f39682f3e557827735207292e4a97d3a5aab` |
| 85 raw archives + sealed records | `FMRT01/raw/` |
| Per-world results | `FMRT01_WORLD_RESULTS.json` / `.csv` |
| Pre-run durability, verified by read-back | `FMRT01_PRE_RUN_DURABILITY.json` — `PASS` |
| Raw durability, verified by read-back | `FMRT01_RAW_DURABILITY.json` — `PASS` |
| On Tommy's disk | `ISING_LIFE_AUTHORITATIVE_RECOVERY\FMRT01\prerun\` and `...\FMRT01\raw\` |

The autopsy starts from these. It does not regenerate them.
