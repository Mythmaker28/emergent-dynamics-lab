# MYQBD01 — corrections applied in the single seal repair round

> The MASTER FREEZE is not edited. a freeze that is edited after the fact is not a freeze. Every correction below is recorded ALONGSIDE the freeze and names exactly what it supersedes.

## Superseded values

### C-F16 (review F16)
- **where** `MYQBD01_FEEDBACK_BOUND.json -> FEEDBACK` -> `DETERMINISTIC_PERTURBATION_BOUND.one_Y_birth.recovery_rate_per_step`
- **was** 0.2
- **now** 0.35573502919515165
- **why** phi = 0.20 is the _exchange OFFER rate, not the effective replenishment rate: the cell also loses SY to a hypergeometric removal and gains SY by diffusion. Measured by regressing d(nSY) on (S0 - nSY) over the 14 static arms, steps 2000-10999.
- **direction** CONSERVATIVE: recovery is FASTER than claimed, so the first-birth error is SMALLER than the pre-seal record stated

### C-F17 (review F17)
- **where** `MYQBD01_FEEDBACK_BOUND.json -> FEEDBACK` -> `DETERMINISTIC_PERTURBATION_BOUND.one_Y_birth.as_fraction_of_mean_nSY`
- **was** -1/0.985048 = -101.52% (unconditional mean nSY)
- **now** -1/1.814057 = -55.13% (conditional on cand_Y >= 1)
- **why** a Y birth is possible only when cand_Y = min(nSY, free) >= 1. The unconditional mean is the wrong denominator; conditional on a birth being possible the organiser cell holds 1.814057 SY on average (E[cand_Y | cand_Y>=1] = 1.777084).
- **direction** CONSERVATIVE: the depletion is smaller than claimed

### C-F08 (review F08)
- **where** `MYQBD01_FEEDBACK_BOUND.json -> SPATIAL` -> `SUBSTEP_LEDGERS_ARE_SCALAR (key renamed to LEDGER_CONTENTS)`
- **was** 'these carry step, sub-step index and scalar organiser-cell counts'
- **now** source_substep_ledger is (44000,6) = (step, species_index, org_y_before, org_x_before, org_y_after, org_x_after): 4 of 6 columns are lattice coordinates. It records 1038 organiser moves over 373 distinct cells in the arm inspected.
- **why** the label was factually wrong
- **direction** STRENGTHENS: because the organiser trajectory IS recorded, Q_ORGANISER is the FOUNDER's exact lineage exposure in the mobile branch too, not only the static branch. The gap is descendants, not motion.

### C-F09/F23 (review F09, F23)
- **where** `myqbd01_spatial_feedback.py -> §12` -> `Q_POSITION_RECOVERABLE_FOR_A_SEPARATED_DESCENDANT`
- **was** hardcoded literal False, from 1 of 28 archives with 0 key contents inspected
- **now** DERIVED over all 28 archives: key sets identical, no array of shape (T,L,L) in any arm, all 220 `frames` decoded and every value asserted scalar, and an information budget showing the archive is ~49x too small to carry the field
- **why** a load-bearing boolean returned as a literal is not evidence, even when it is right
- **direction** NEUTRAL on the value, decisive on the evidence

### C-F10 (review F10)
- **where** `myqbd01_spatial_feedback.py -> §12 WHY` -> `the stated reason Q_POSITION is unavailable`
- **was** 'a mobile descendant that separates occupies a DIFFERENT cell whose (nX,nSY,free) is not recorded' (non-recording)
- **now** with kY = 0 no Y birth occurs in ANY arm: N_Y == 1 at all 308000 recorded steps across all 28 archives. A separated descendant does not merely go unrecorded -- it never exists.
- **why** the decisive fact sat in §13 and never entered §12
- **direction** STRENGTHENS the disposition

### C-F20/F21 (review F20, F21)
- **where** `MYQBD01_DISCOVERY_REGION.json` -> `STRUCTURAL_PRECLUSION_CHECK framing and witness`
- **was** 'the MOST FAVOURABLE admissible environment (Q sustained at Q_MAX)'; c_box = 3 described as 'near the mean organiser-cell candidate pool'
- **now** framing dropped (the witness uses exposure 12, not Q_MAX = 28); measured mean cand_Y_at_org = 0.961651 recorded, so c = 3 is 3.12x it; and a THIRD witness added at the arms' OWN measured magnitudes: R = 1.000163936 > 1
- **why** non-preclusion must not rest on an inflated pool
- **direction** STRENGTHENS: non-preclusion now holds at the measured environment

### C-F25 (review F25)
- **where** `myqbd01_regions.py -> requirements` -> `NO_TARGET_DERIVED_Y_OUTCOME`
- **was** hardcoded literal True with a comment; 0 AST data-access checks existed
- **now** DERIVED by myqbd01_seal_audits.target_derived_audit(): AST walk of all 8 modules, 129 data-access keys collected from Subscript and .index() positions only, 0 outcome-descriptor accesses, 1 container read (`frames`) disclosed with its justification
- **why** the requirement asserted a check that did not exist
- **direction** NEUTRAL on the value, decisive on the evidence

### C-F27/F30 (review F27, F30)
- **where** `myqbd01_regions.py -> requirements` -> `SCIENTIFIC_RUNS_USED_ZERO / the zero-run ground`
- **was** a literal, resting on a sentinel claimed to be 'aggregated over ALL ANALYSIS PROCESSES' but installed in 1 of 8 modules
- **now** DERIVED by a static import proof: no MYQBD01 module imports any engine module, so none could construct or step a World, whatever a runtime counter says
- **why** the coverage claim was false; the conclusion needed a ground that does not depend on it
- **direction** STRENGTHENS: the ground is now stronger than the one claimed

### C-F05 (review F05)
- **where** `MYQBD01_TEMPORAL_DEPENDENCE.json (reported summary)` -> `'IAT ~7-9'`
- **was** IAT ~7-9, reported as branch means only
- **now** estimator-dependent AND heavy-tailed. Operator's initial-positive-sequence estimator: mobile mean 8.4277, max 24.5556 (M__seed9300015); static mean 7.1756, max 9.7186 (S__seed9300009). Reviewer's overlapping-pair variant: mobile mean 9.1967, max 35.335. Same outlier arm, different magnitude.
- **why** a bare branch mean hides a single arm at 3-4x it. Neither estimate is canonised; the divergence is itself the finding, and the successor must freeze one estimator.
- **direction** CONSERVATIVE: a larger IAT means LESS independent information per arm, which supports the insufficiency disposition rather than undermining it

### C-F13/F15 (review F13, F15)
- **where** `MYQBD01_TWO_Y_OPERATOR.json` -> `the counterexample scale and conditions 7-8`
- **was** non-independence demonstrated at kY = 0.05 and 0.20, i.e. 1250x and 5000x admissible; conditions 7 and 8 stated without magnitude
- **now** magnitudes at the admissible kY = 4e-5 recorded: relative variance gap -1.6e-4, support-excess probability 9.8e-15, quenched-vs-scalar relative gap 2.05e-4. NOT_IDENTIFIABLE rests on the SPATIAL ground, not on the branching-process gap.
- **why** a demonstration at 1250x the mission's own scale is a rhetorical scale
- **direction** WEAKENS two supporting arguments; the classification is unaffected

### C-F02/F03 (review F02, F03)
- **where** `MYQBD01_Q_PHASE_MAP.json` -> `ENGINE_Y_BIRTH provenance and the step-label convention`
- **was** cites kinetics.py:117/119/120; no step-label convention recorded
- **now** the executed engine is WorldOBTC (engine_obtc.py:162/165/166); kinetics.py lines are INHERITED_EQUIVALENT, not executed. series[:,0] is post-increment 1..11000 while all four ledgers label the same physical sub-step pre-increment 0..10999.
- **why** citing an inherited site as the executed one, and an undocumented off-by-one convention
- **direction** NEUTRAL: the event-phase identity itself is unaffected (F01 refuted the attack)

## Confirmed but NOT repairable here

### N-F31 (review F31)
- **what** MYQBD01_MASTER_FREEZE.{md,json} was committed in the SAME commit (decfda5) as MYQBD01_ARM_LEVEL_Q_SUMMARIES.{csv,json} and MYQBD01_TEMPORAL_DEPENDENCE.json. Independent Git checkpoints separating the freeze from the statistics: 0.
- **why not repairable** separating them retroactively would require rewriting inherited history, which this program forbids. Editing the freeze after the fact would be worse than the defect.
- **why not load-bearing** the freeze's own text declares the mission response-informed and developmental and explicitly disclaims blinding, and all 28 arms are classified POST_OUTCOME_DEVELOPMENT_DIAGNOSTIC. No claim in the record depends on the freeze predating the access.
- **successor must** PQEC01 must commit its freeze ALONE, in its own commit, before any module that reads trajectory values is run, and record that commit hash inside the freeze.

### N-F28 (review F28)
- **what** observe.seed_one_organiser is a fourth seeding entry point and is not patched by the sentinel (kinetics, lawspec_v2 and engine_obtc are).
- **why not repairable** the sentinel lives in the inherited PMCR01 tree, which this mission may not rewrite.
- **why not load-bearing** no MYQBD01 module imports observe -- or any engine module -- as the static import proof shows, so the unpatched entry point was unreachable from this mission's code.
- **successor must** patch all four entry points and name four in the comment.

### N-F29 (review F29)
- **what** the filesystem witness globs at depth 2 and does not watch the repository tree; 13 directories matching /home/claude/edl/*/out are unwatched.
- **why not repairable** same inherited-tree constraint.
- **why not load-bearing** superseded as a ground by the static import proof, which does not depend on filesystem watching at all.
- **successor must** glob recursively and record the depth in the scope note.

## Net effect

of the 11 corrections, 4 STRENGTHEN the disposition's grounds (C-F08, C-F10, C-F20/F21, C-F27/F30), 3 move a number in the CONSERVATIVE direction (C-F16, C-F17, C-F05), 2 replace a literal by a derivation without changing its value (C-F09/F23, C-F25), and 2 weaken supporting arguments the classification never rested on (C-F13/F15, C-F02/F03). None moves the disposition.


## Corrections supplémentaires du même round unique

### C-A1a (constats F02)
- **où** `MYQBD01_Q_PHASE_MAP.json` → `ENGINE_Y_BIRTH provenance`
- **avant** kinetics.py:117/119/120 cited as the executed reaction path
- **après** engine_obtc.py:162 (free0, once, before the loop), 164 (species loop), 165 (p clamp), 166 (cand = min(nSY, free0)), 167 (binomial). kinetics.py lines retained as INHERITED_EQUIVALENT only. Executed class: run_obfor01.Instrumented(WorldOBTC); kinetics.World._react never ran.
- **pourquoi** an inherited site was cited as the executed one
- **direction** NEUTRAL: Q_LEDGER_STATUS = EVENT_EXACT is unaffected

### C-A1b (constats F03)
- **où** `MYQBD01_Q_PHASE_MAP.json` → `step-label convention`
- **avant** undocumented
- **après** series 1..11000 (post-increment) vs sub-step ledgers 0..10999 (pre-increment); series_step = ledger_step + 1, VERIFIED over all 28 arms
- **pourquoi** an implicit off-by-one between two label conventions
- **direction** NEUTRAL

### C-A2 (constats F05)
- **où** `MYQBD01_TEMPORAL_DEPENDENCE.json + arm summaries` → `IAT reporting`
- **avant** 'IAT ~7-9', branch means only
- **après** estimator NAMED (overlapping-pair initial-positive-sequence) and full distributions published: static min 5.783 / median 6.977 / mean 7.177 / max 9.719 / IQR 0.744; mobile min 5.335 / median 6.461 / mean 9.19672185075826 / max 35.335 (M__seed9300015, 3.84x the mean) / IQR 2.075. Three alternative estimators per arm, zero-episode summaries and early/late drift added.
- **pourquoi** a branch mean hid a heavy tail and an estimator dependence
- **direction** CONSERVATIVE: a larger IAT means less independent information per arm

### C-A4 (constats F08, F09, F10, F23)
- **où** `MYQBD01_DESCENDANT_RECOVERABILITY_AUDIT.json + RAW_KEY_INVENTORY.{csv,json}` → `descendant recoverability`
- **avant** one archive, zero key contents inspected, hardcoded boolean, ledgers called 'scalar'
- **après** all 28 archives, 420 key-by-arm inventory rows with shape/dtype/cadence/column semantics/coordinate presence/invertibility; four flags COMPUTED: SOURCE_TRAJECTORY_POSITION_RESOLVED=true, FULL_LATTICE_ENVIRONMENT_PER_STEP=false, HISTORICAL_DESCENDANT_TRAJECTORY_EXISTS=false, DESCENDANT_Q_POSITION_RECONSTRUCTIBLE=false
- **pourquoi** a disposition-blocking classification derived from 1 of 28 archives is not evidence
- **direction** STRENGTHENS: the kY=0 / N_Y==1 ground now sits in the section that uses it

### C-A5 (constats F13)
- **où** `MYQBD01_TWO_Y_OPERATOR.json` → `conditions 7 and 8`
- **avant** asserted as grounds for insufficiency, no magnitude
- **après** quenched exponent 1.248125e-04 vs scalar 1.248381e-04, relative gap -2.047e-04; clamp active on 0 of 126000 steps. SCALAR_Q_REDUCTION_STATUS restated exactly.
- **pourquoi** over-pessimistic: a 2e-4 effect was presented as invalidating
- **direction** WEAKENS two supporting arguments; the classification never rested on them

### C-A6 (constats F15)
- **où** `MYQBD01_TWO_Y_OPERATOR.json` → `two-Y counterexample scale`
- **avant** demonstrated at kY = 0.05 and 0.20 (1250x and 5000x admissible)
- **après** exact law over the ADMISSIBLE domain: mean gap 2.26e-16, variance relative gap -1.600256e-04, total-variation distance 1.535e-07, impossible-outcome mass 9.8279e-15. Conclusion: MEAN_ONLY_EQUIVALENCE_TO_HIGH_ACCURACY_IN_UNCLAMPED_ADMISSIBLE_REGIME__BUT_EXACT_SUPPORT_AND_DEPENDENCE_ARE_NOT_GALTON_WATSON
- **pourquoi** a demonstration at 1250x the mission's own scale is not quantitative evidence
- **direction** HONEST BOTH WAYS: the effect is smaller than implied, and the reason the region still fails is relocated onto A4 where it belongs

### C-A7 (constats F16, F17)
- **où** `MYQBD01_FEEDBACK_BOUND.json` → `feedback certificate`
- **avant** recovery 0.20/step (the offer rate); depletion ~100% (unconditional mean)
- **après** measured effective mean reversion 0.355735 +- 0.013473 (1.78x the offer rate), with the mechanism explained; and THREE conditionings published separately: unconditional 101.52%, conditional on cand_Y>=1 55.13% (the reference), birth-realised-weighted 48.57% (derived, since kY = 0)
- **pourquoi** both published numbers were wrong
- **direction** CONSERVATIVE: the perturbation is smaller and erased faster than certified

### C-A8 (constats F20, F21)
- **où** `MYQBD01_FEEDBACK_BOUND.json` → `non-preclusion witness`
- **avant** 'the MOST FAVOURABLE admissible environment (Q sustained at Q_MAX)', c = 3 called 'near the mean pool'
- **après** framing dropped (the witness uses exposure 12, not Q_MAX = 28); the witness is labelled EXPLICITLY FAVOURABLE / ATYPICAL with its 3.12x pool and 3.79x exposure ratios; and a REPRESENTATIVE witness at the arms' own measured E[Q] = 3.169730 now carries the conclusion: R = 1.000124838, margin 63.98x muY. eta* = 0.004063547247 and the T-step survival 0.995957500914 are published as the distinct quantities they are.
- **pourquoi** non-preclusion must not rest on an inflated magnitude
- **direction** STRENGTHENS: non-preclusion now holds at measured magnitudes

### C-A10 (constats F25)
- **où** `MYQBD01_DATA_ACCESS_AUDIT.json` → `NO_TARGET_DERIVED_Y_OUTCOME`
- **avant** a literal asserting an AST audit that did not exist
- **après** a real AST audit over 11 modules: executable accesses (Subscript string keys and index()/get() string arguments) separated from PROSE mentions (87 counted and explicitly not treated as reads). TARGET_DERIVED_Y_OUTCOME_READS = 0; one container read (`frames`) disclosed with its justification.
- **pourquoi** the claimed audit did not exist
- **direction** NEUTRAL on the value, decisive on the evidence

### C-A12 (constats F27, F28, F29, F30)
- **où** `MYQBD01_ZERO_RUN_COMPLIANCE.json + MYQBD01_REPAIR_ZERO_RUN_WITNESS.json` → `zero-run evidence`
- **avant** 'Sentinel aggregated over ALL ANALYSIS PROCESSES' — installed in 1 of 8 modules
- **après** reported in three separable parts: ORIGINAL_RUNTIME_SENTINEL_COVERAGE = INCOMPLETE (not retroactively claimed as fixed), RETROSPECTIVE_STATIC_ZERO_RUN_PROOF = PASS, FINAL_REPAIR_RUNTIME_GUARDS = PASS. The repair guard patches 4 World constructors, 9 scheduler steps and ALL FOUR seeding entry points, audits subprocess, walks the filesystem recursively with no depth limit, and PROVES it fires by positive control.
- **pourquoi** a false coverage claim, and a conclusion that needed a ground not depending on it
- **direction** STRENGTHENS

## Effet net

21 corrections in the single authorized round. 6 STRENGTHEN the disposition's grounds (C-F08, C-F10, C-F20/F21, C-F27/F30, C-A4, C-A8, C-A12), 4 move a number in the CONSERVATIVE direction (C-F16, C-F17, C-F05, C-A2, C-A7), 4 replace a literal or an absent audit by a real derivation without changing its value (C-F09/F23, C-F25, C-A4, C-A10), and the rest weaken supporting arguments the classification never rested on (C-A5, C-A6, C-F13/F15, C-F02/F03, C-A1a, C-A1b). NONE moves the disposition.

