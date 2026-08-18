# FLCR01 — INDEPENDENT ADVERSARIAL REVIEW

Single authorized review. Read-only on the candidate. Zero new scientific runs: no World was
constructed or stepped. Everything below is exact arithmetic, re-derivation of the candidate's own
finite Markov chain, direct reads of `.npz` archives, source and Git objects. Scratch under
`/home/claude/FLCR01/review/work/`.

**Candidate** `/home/claude/edl` @ `codex/founder-versus-lineage-continuity-reconciliation-01`,
C1 `e302cca`, C2 `58c2c03`. Working tree clean; all 17 FLCR01 paths tracked.

**Disposition under attack** `LINEAGE_CRITERION_SUPPORTED__OPERATOR_NOT_IDENTIFIED_FROM_PQEC01`,
`ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED`, non-empty lineage region of **563** grid points,
`kY ∈ [1.58e-05, 5.62e-04]`, `muY ∈ [1.00e-08, 1.19e-03]`.

---

## 0. What reproduces, before anything is attacked

Independently recomputed from `/home/claude/PQEC01/raw` and from the candidate's own algorithms:

| quantity | candidate | this review |
|---|---|---|
| lineage region, as coded | 563 points, kY [1.584893e-05, 5.623413e-04], muY [1.0e-08, 1.188502e-03] | **identical to all digits** |
| founder region | 0 points | 0 points at τ = 83, 111 and 125 alike |
| `muY ≥ 1−0.5^(1/τ)` at τ = 83 / 111 / 125 | 8.316397e-03 / 6.225112e-03 / 5.529831e-03 | identical |
| `muY ≤ 1−0.5^(1/11000)` | 6.301139e-05 | identical |
| incompatibility factors | 131.98 / 98.79 / 87.76 | identical |
| Phase-A world-level mean exposure `E_w` | 2.873022222222222 | 2.8730222222 (n = 40, from `ycells` col 8, burn-in 2000, clip 40) |
| two-centre hold episodes | n = 380, median 16, mean 243.78, q90 614.8, max 4999 | identical |
| separation delay after first birth | n = 34, median 111 | identical |
| Phase-B counts | 88 worlds, 56 births, 34 reaching two centres | identical |
| L1/L2/L3 at B1 | 16/44, 16/44, 16/44 | identical |
| L1/L2/L3 at B2 | 18/44, 44/44, 18/44 | identical |

Arithmetic and data handling are sound. Every defect below is about **what the numbers are taken to
mean**, not about the numbers being miscomputed.

---

## 1. Findings

### F01 — the founder gate is not "what makes the region empty"

- **ID** F01 · **ATTACK** A1 · **SEVERITY** SUBSTANTIVE · **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** `FLCR01_CRITERION_MATRIX.json` FOUNDER_SURVIVAL row:
  `consequence_for_the_region = "forces muY <= 6.30e-05 and is what makes the region empty for
  every kY and every exposure"`.
- **EXACT_FILE_AND_LINES** `/home/claude/edl/FLCR01/code/flcr01_science.py:216-217`;
  `/home/claude/edl/FLCR01/out/FLCR01_CRITERION_MATRIX.json` FOUNDER_SURVIVAL block;
  `/home/claude/edl/FLCR01/out/FLCR01_LINEAGE_REGIONS.json:39`.
- **EXACT_NUMBERS** On the identical 81×81 grid with E = 2.873022222222222, W = 9000, T = 11000 and
  the technical clamp `kY·CAP·N_STAR ≤ 0.1`:
  `{C1, C2_FOUNDER, C3}` = **0** points at τ = 83, 111, 125;
  `{C1, C3}` (drop C2_FOUNDER only) = **191 / 225 / 239** points at τ = 83 / 111 / 125;
  `{C1, C2_FOUNDER}` (drop C3 only) = **1056** points at every τ;
  `{C1}` alone = 1944 points.
  Furthermore **501 of the 563** published lineage points (89.0 %) already satisfy C2_FOUNDER.
- **WHY_IT_MATTERS** Emptiness is a property of the conjunction. The single frozen criterion whose
  deletion opens the *largest* region is C3 (1056), not C2_FOUNDER (225) — 4.7× larger. Attributing
  emptiness to the founder gate alone is false, and it is the specific false attribution that makes
  the subsequent narrative ("replacing C2_FOUNDER dissolves the contradiction") look like the whole
  story when it is not (see F04).
- **SETTLING_COMMAND_OR_CALCULATION** `python3 /home/claude/FLCR01/review/work/` — count grid points
  satisfying each subset of {C1, C2_FOUNDER, C3, technical} over
  `grid_k = 10**linspace(-6,-2,81)`, `grid_m = 10**linspace(-8,-1,81)`.
- **MINIMUM_REQUIRED_CHANGE** Replace the sentence with: "C2_FOUNDER forces muY ≤ 6.30e-05; jointly
  with C1 and C3 the region is empty. C2_FOUNDER alone is not sufficient for emptiness — dropping C3
  instead leaves 1056 points."

### F02 — the founder rejection is scientific, not outcome-driven

- **ID** F02 · **ATTACK** A1 · **SEVERITY** — · **STATUS** ATTACK_REFUTED
- **CLAIM_ATTACKED** "Founder survival is rejected on scientific grounds that stand independently of
  any region … that argument would stand even if founder survival happened to admit a wide region."
- **EXACT_FILE_AND_LINES** `flcr01_science.py:205-218` (`why`, region-free),
  `flcr01_science.py:272-277` (`WHY_NOT_CHOSEN_FOR_CREATING_A_REGION`),
  `flcr01_science.py:278-281` (`IF_FOUNDER_IDENTITY_WERE_ESSENTIAL`),
  `FLCR01_CRITERION_AUDIT.md:58-70`, `flcr01_final.py:46-49`.
- **EXACT_NUMBERS** The stated ground — "the X cloud already turns over completely; requiring one
  tagged Y particle to persist imposes on Y precisely the property the project denies is required of
  X" — contains no region term and is stated in a field distinct from
  `consequence_for_the_region`. The decisive adversarial test: of the two single-criterion deletions
  that dissolve the contradiction, the candidate chose the one that yields the **smaller** region
  (delete C2_FOUNDER → **225** points; delete C3 → **1056** points). A region-maximising author would
  have deleted C3 and kept the founder gate.
- **WHY_IT_MATTERS** The hypothesis that founder survival was discarded to manufacture a region is
  refuted by the candidate's own arithmetic running against it.
- **SETTLING_COMMAND_OR_CALCULATION** Same subset counts as F01; compare 225 vs 1056.
- **MINIMUM_REQUIRED_CHANGE** None. Optionally record the 225-vs-1056 contrast as positive evidence
  that the choice was not region-maximising.

### F03 — lineage continuity is measurable from recorded quantities alone; no genealogy is invented

- **ID** F03 · **ATTACK** A2 · **SEVERITY** — · **STATUS** ATTACK_REFUTED
- **CLAIM_ATTACKED** `NO_INVENTED_GENEALOGY`; `SHARED_PARENT_POOL` declared unidentifiable rather
  than imputed; every retained criterion computable from `N_Y`, `n_centres`, integrity.
- **EXACT_FILE_AND_LINES** `flcr01_science.py:81-90` (`_classify` reads only `nY`, `ncen`,
  `integrity_ok`); `flcr01_science.py:105-108` (`N_Y`, `n_centres` pulled from `scalars`);
  `/home/claude/edl/PQEC01/code/pqec01_run.py:32-56` (`_centres`: union-find single linkage over
  occupied Y cells, toroidal distance, `if d <= CORE_R` at line 53, `CORE_R = 5.0` bound from the
  master freeze at line 24); `/home/claude/edl/OBTC01/code/engine_obtc.py:158-167`
  (`p = min(1, kY·nX·nY)` per cell, `cand = min(nSY, free0)`, `births = Binomial(cand, p)`);
  `flcr01_science.py:181-184` (`RECORDED_BUT_NOT_IDENTIFIABLE`).
- **EXACT_NUMBERS** `CORE_R = 5.0` confirmed. Because `p = min(1, kY·nX·nY) = 0` whenever `nY = 0`
  in a cell, and every world is seeded with exactly one Y, total extinction is absorbing and
  `N_Y > 0 ⟺ at least one Y descended from the initial state` — LINEAGE_NON_EXTINCTION is exact, not
  approximate. No line in the four FLCR01 scripts assigns a parent to any birth; `ybirth` rows are
  `(step, y, x, count)` only. Independent recomputation of the whole state operator from raw
  reproduces the candidate exactly: worlds visiting each state B1 `{E:28, O:44, C:16, S:16, P:7,
  F:0}`, B2 `{E:0, O:44, C:18, S:18, P:7, F:0}`; 380 hold episodes; 56 births; 34 worlds reaching
  two centres.
- **WHY_IT_MATTERS** The attack fails. The criterion set does not need, and does not fake, a
  genealogy.
- **SETTLING_COMMAND_OR_CALCULATION** Re-run `_classify` over `scalars[:, N_Y]` and
  `scalars[:, n_centres]` for the 88 `B_*.npz`; compare state counts with
  `FLCR01_STATE_OPERATOR.json`.
- **MINIMUM_REQUIRED_CHANGE** None.

### F04 — the 563-point region is produced by dropping C3, not by replacing C2_FOUNDER

- **ID** F04 · **ATTACK** A3 · **SEVERITY** **LOAD_BEARING** · **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** "removes the muY upper bound entirely; the C1-versus-C3 contradiction
  dissolves" (`FLCR01_CRITERION_MATRIX.json`, LINEAGE_NON_EXTINCTION) and
  `FLCR01_LINEAGE_OPERATOR_REPORT.md:72-75` ("en remplaçant la survie du fondateur par la
  non-extinction de la lignée, la borne supérieure sur muY s'évanouit, et avec elle
  l'incompatibilité d'un facteur 98,8").
- **EXACT_FILE_AND_LINES** `flcr01_science.py:339-347` (the entire lineage region loop);
  `flcr01_science.py:232-234`; `flcr01_science.py:369-380` (GATE_FAMILY declares L1…L7);
  `FLCR01_LINEAGE_REGIONS.json:3-11, 41-54`.
- **EXACT_NUMBERS** Of the 563 published points:
  **501 (89.0 %) satisfy C2_FOUNDER** — the criterion said to have been removed;
  **90 (16.0 %) satisfy C3** at τ = 83, 111 and 125 alike — 84.0 % violate it;
  **195 (34.6 %) satisfy C1** — 65.4 % violate it.
  The region loop applies exactly four conditions: `kY·CAP·N_STAR ≤ 0.1`,
  `P_first_birth_by_T ≥ 0.5`, `P_lineage_alive_at_T ≥ 0.5`, `P_at_or_above_N_STAR ≤ 0.5`.
  L3, L4, L5, L6 and L7 — including the declared replacement for C3,
  `L5_THIRD_CENTRE_CONTROL` — are **never evaluated anywhere in the region**.
- **WHY_IT_MATTERS** The disposition's headline number is presented as the consequence of one
  criterion substitution that the candidate defends at length. It is not. Nine tenths of the region
  is compatible with the criterion that was removed, and five sixths of it violates a *different*
  frozen criterion that was removed silently and whose declared replacement is never applied. The
  region is therefore not the region of the gate family the same file publishes; the region of the
  declared gate family is unknown, and the largest closed-form subset compatible with the frozen
  separation bound is 90 points, not 563.
- **SETTLING_COMMAND_OR_CALCULATION** For each of the 563 points evaluate
  `(1-muY)**11000 >= 0.5`, `kY*2.873022222222222*9000*(1-muY)**tau <= 0.5` and
  `kY*2.873022222222222*9000 >= 1`; count 501, 90, 195.
- **MINIMUM_REQUIRED_CHANGE** Either evaluate L5 (or the frozen C3 bound) inside the region and
  publish the resulting count, or state explicitly in `LINEAGE_CONTINUITY_REGION` and in the
  disposition that the region enforces L1, L2 and an undeclared population cap only, that 84 % of it
  violates the frozen separation bound, and that 89 % of it would also have satisfied the founder
  gate.

### F05 — an undeclared gate removes 65 % of the region

- **ID** F05 · **ATTACK** A3 · **SEVERITY** SUBSTANTIVE · **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** `GATE_FAMILY` (L1…L7) and `THRESHOLD_PROVENANCE` present the complete gate set
  and the provenance of every threshold.
- **EXACT_FILE_AND_LINES** `flcr01_science.py:345` (`pr["P_at_or_above_N_STAR"] <= 1 - THRESH`);
  `flcr01_science.py:369-393`; `FLCR01_LINEAGE_REGIONS.json:3-35`.
- **EXACT_NUMBERS** Points passing `technical ∧ L1 ∧ L2` = **1624**. The population cap removes
  **1061** of them, leaving 563 — it does **65.3 %** of the filtering. It appears in no
  `GATE_FAMILY` entry and in no `THRESHOLD_PROVENANCE` entry. Grid points surviving the technical
  clamp: 4536 of 6561. Individual failure counts: L1 only 1064, cap only 1061, L2 only 968,
  L1 and L2 880.
- **WHY_IT_MATTERS** The single most restrictive condition in the derivation is invisible in the
  published gate family, so the point count cannot be reproduced from the published specification.
  (Its direction is conservative — it shrinks the region — which is why this is SUBSTANTIVE and not
  LOAD_BEARING.)
- **SETTLING_COMMAND_OR_CALCULATION** Recount the region with and without line 345's third
  conjunct: 1624 vs 563.
- **MINIMUM_REQUIRED_CHANGE** Add the cap to `GATE_FAMILY` (e.g. `L0_POPULATION_CAP: P(nY ≥ N_STAR
  at T_horizon) ≤ 0.5`) with its provenance, and note that it removes 1061 of 1624 points.

### F06 — L1 is evaluated over 11000 steps while it is declared over 9000

- **ID** F06 · **ATTACK** A3 · **SEVERITY** **LOAD_BEARING** · **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** `L1_FIRST_BIRTH = "P(first Y birth before T_birth=9000) >= 0.50"` and
  `THRESHOLD_PROVENANCE.T_birth = {value: 9000, source: INHERITED (the analysis window)}`.
- **EXACT_FILE_AND_LINES** `flcr01_science.py:306` (`def _profile(..., T=T_HORIZON)`);
  `flcr01_science.py:314` (`p_no_birth = exp(T*cc*log1p(-p1))`); `flcr01_science.py:343`
  (`_profile(kY, muY, C_POOL, NX)` — called without `T`, so T = 11000);
  `flcr01_science.py:327` (`T_BIRTH, T_SEP = T_WINDOW, T_WINDOW`);
  `FLCR01_LINEAGE_REGIONS.json:4, 17-24`.
- **EXACT_NUMBERS** Evaluating L1 at the declared `T_birth = 9000` (survival still at 11000) gives
  **473** points, not 563 — **90 published points (16.0 %) fail the gate as written**. The published
  kY lower edge moves from **1.584893e-05 to 1.995262e-05** (×1.259). Applying both this and the
  candidate's own measured exposure (F14) gives **510** points,
  kY ∈ [2.818e-05, 5.623e-04], muY ∈ [1.000e-08, 7.943e-04]; only **309 of 563 (54.9 %)** of the
  published points survive both corrections.
- **WHY_IT_MATTERS** The disposition's point count and kY lower bound are quoted from a computation
  that used a 22 % longer window than the gate it claims to evaluate, in the permissive direction.
- **SETTLING_COMMAND_OR_CALCULATION** Replace line 343 with `_profile(kY, muY, C_POOL, NX,
  T=T_BIRTH)` for the first-birth term only; recount → 473.
- **MINIMUM_REQUIRED_CHANGE** Pass `T=T_BIRTH` to the first-birth term, or restate L1 as
  "before T_horizon = 11000" and remove the `T_birth` provenance entry.

### F07 — the §3 contradiction is real and independent of everything measurable

- **ID** F07 · **ATTACK** A3 · **SEVERITY** — · **STATUS** ATTACK_REFUTED
- **CLAIM_ATTACKED** `FOUNDER_GATE_REGION = EMPTY_FOR_ALL_kY_AND_ALL_EXPOSURE`, and the reading of
  C3 as forbidding a *second* separated centre.
- **EXACT_FILE_AND_LINES** `flcr01_science.py:25-77`; `FLCR01_FOUNDER_CONTRADICTION.json:8-36`;
  `/home/claude/edl/PQEC01/code/pqec01_design.py:42-53` (the frozen margins).
- **EXACT_NUMBERS** Re-derived independently: `1 − 0.5^(1/83) = 8.316397e-03`,
  `1 − 0.5^(1/111) = 6.225112e-03`, `1 − 0.5^(1/125) = 5.529831e-03`,
  `1 − 0.5^(1/11000) = 6.301139e-05`; ratios 131.98, 98.79, 87.76 — all identical to the candidate.
  Division of C3 by C1 is licit because C1 supplies `kY·E·W ≥ MINEV = 1`, so
  `(1−muY)^τ ≤ GAMMA/(kY·E·W) ≤ GAMMA/MINEV = 0.5`. `{C1, C2_FOUNDER, C3}` is empty on the grid at
  τ = 83, 111 **and** 125, so the emptiness does not depend on the τ substitution of F28.
  PQEC01 named this margin `no_premature_third_centre` (`pqec01_design.py:53`), but algebraically
  `n_sep = B·(1−muY)^τ ≤ 0.5` bounds the expected number of *surviving newborn* Y — i.e. it forbids
  the **second** centre. FLCR01's reading is the correct one and corrects the parent's label.
- **WHY_IT_MATTERS** The foundation of the whole mission holds. The founder gate could not have
  produced a positive region regardless of the data, and the candidate's identification of the
  deeper error (C3 opposes the object under test) is algebraically correct.
- **SETTLING_COMMAND_OR_CALCULATION** Evaluate `1 - 0.5**(1/tau)` and `1 - 0.5**(1/11000)`; count
  `{C1,C2F,C3}` over the grid at each τ → 0, 0, 0.
- **MINIMUM_REQUIRED_CHANGE** None.

### F08 — all 128 worlds are correctly labelled developmental

- **ID** F08 · **ATTACK** A4 · **SEVERITY** COSMETIC · **STATUS** DEFECT_CONFIRMED ·
  **ATTACK_VERDICT** ATTACK_REFUTED
- **CLAIM_ATTACKED** "all 128 worlds are POST_OUTCOME_DEVELOPMENT_DATA from this point on … the
  historical DISCOVERY/VALIDATION labels are retained only as a descriptive stability diagnostic and
  are never again called held-out."
- **EXACT_FILE_AND_LINES** `flcr01_science.py:3-4, 134` (`"split_historical": m["split"]`);
  `flcr01_correct.py:217-226`; `flcr01_bind.py:31-40`; `FLCR01_LINEAGE_OPERATOR_REPORT.md:3-4`;
  `FLCR01_FINAL_DISPOSITION.json:27` ("it authorizes a clean test, it confirms nothing");
  cosmetic defect at `flcr01_correct.py:164-165` (`DISCOVERY_TWO_Y_COLOCATED_STEPS`,
  `DISCOVERY_TWO_Y_SEPARATED_STEPS`).
- **EXACT_NUMBERS** A full grep of `FLCR01/out/*` and `FLCR01/code/*` for
  `held.out|prospectiv|confirmator|holdout|VALIDATION|DISCOVERY|confirm` returns **0** places where
  FLCR01 output is called prospective, held-out or confirmatory, and **0** places where a
  reanalysis is presented as confirmation. All 88 per-world records carry the key
  `split_historical`, never `split`. Phase A (40) enters only `E_FEEDBACK` and
  `F_OPERATOR_UNCERTAINTY`; Phase B (88) enters the state operator; 40 + 88 = 128 covered.
  `PQEC01_OBSERVER_PHYSICS_STATUS = INERTNESS_CONFIRMED` is legitimate: observer inertness was
  qualified at PQEC01 C1 (`0c8ed48`), before the first scientific start.
  Cosmetic: two keys in `B_COUNTS` use the bare word `DISCOVERY` without the `_historical`
  qualifier used everywhere else (values 12474 and 73674).
- **WHY_IT_MATTERS** The attack fails. This is the cleanest of the eight areas.
- **SETTLING_COMMAND_OR_CALCULATION** `grep -rn -i "held.out\|prospectiv\|confirmator\|holdout"
  /home/claude/edl/FLCR01/out /home/claude/edl/FLCR01/code`.
- **MINIMUM_REQUIRED_CHANGE** Rename the two `B_COUNTS` keys to
  `HISTORICAL_DISCOVERY_SUBSET_*` for consistency.

### F09 — pooled B1 and pooled B2 are computed on different denominators

- **ID** F09 · **ATTACK** A5 · **SEVERITY** SUBSTANTIVE · **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** The five published comparisons are comparable across parameter points, and the
  addendum's withdrawal of the old pooled figure ("worlds stop at outcome-dependent times; the
  analysis windows are therefore unequal") has been remedied.
- **EXACT_FILE_AND_LINES** `flcr01_correct.py:307-310` (`wA_full`; `w["nX"][BURN_IN:w["n"]]` with a
  per-world upper limit; the filter `if w["n"] > BURN_IN`);
  `PQEC01_REVIEW_CORRECTION_ADDENDUM.md:84, 89`; `flcr01_correct.py:350-357`.
- **EXACT_NUMBERS** B1 pooled: `n_B = 29` of 44 — **15 worlds with `steps_recorded ≤ 2000` are
  silently dropped** (verified from raw: 15 B1 worlds stop at or before step 2000), and the 29
  retained have windows of unequal length between 1 and 9000 steps. B2 pooled: `n_B = 44` of 44,
  every window exactly 9000 steps. The published contrast is B1 +40.53 (+36.5 %, z = +4.28,
  significant) versus B2 +16.91 (+15.2 %, z = +1.84, not significant). The A baseline is the same
  40 worlds × 9000 steps in both rows.
- **WHY_IT_MATTERS** The B1 pooled row is exactly the statistic whose four confounds the addendum
  itself lists as grounds for withdrawing the earlier claim, republished with a significance verdict
  and no warning. The B1-versus-B2 contrast that feeds test D is a comparison of a survivor-selected
  unequal-window statistic against a complete equal-window one.
- **SETTLING_COMMAND_OR_CALCULATION** Count B1 worlds with `steps_recorded ≤ 2000` → 15;
  44 − 15 = 29 = the published `n_B`.
- **MINIMUM_REQUIRED_CHANGE** Attach to the `pooled` row the same explicit survivorship block that
  `matched_time_window` carries, stating 15 of 44 excluded at B1 and 0 of 44 at B2, and stating that
  the retained windows are of unequal length at B1 only.

### F10 — "+1 % to +67 % depending only on which stratification is chosen" is false

- **ID** F10 · **ATTACK** A5 · **SEVERITY** SUBSTANTIVE · **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** Architecture test D evidence and `WHY_NOT_DISPOSITION_1`: "the same comparison
  ranges from about +1 % to +67 % depending only on which stratification is chosen".
- **EXACT_FILE_AND_LINES** `flcr01_science.py:444-447`; `flcr01_final.py:36-41`;
  `FLCR01_LINEAGE_REGIONS.json:102`; `FLCR01_FINAL_DISPOSITION.json` `WHY_NOT_DISPOSITION_1`.
- **EXACT_NUMBERS** +1.1 % is **B2 / matched_time_window**; +66.7 % is **B1 / birth_worlds**. They
  differ in parameter point *and* in comparison. Within B1 alone the range is **+8.3 % … +66.7 %**;
  within B2 alone **−10.2 % … +51.9 %**. Neither is "the same comparison" and neither varies "only"
  by stratification.
- **WHY_IT_MATTERS** The width of the range is the sole quantitative support for declaring test D
  not to hold and for failing disposition-1 requirement 5. Overstating it by conflating two axes
  makes a real but smaller instability look larger and hides that the *point* is a second source of
  variation.
- **SETTLING_COMMAND_OR_CALCULATION** Read `relative_delta` for all 10 published cells in
  `E_FEEDBACK.FOUR_COMPARISONS`.
- **MINIMUM_REQUIRED_CHANGE** Rewrite as: "within a single parameter point the estimate ranges from
  +8.3 % to +66.7 % (B1) and from −10.2 % to +51.9 % (B2), and across points the same comparison
  varies by up to 13.3 percentage points."

### F11 — test D cites only the non-significant half of the matched-window comparison

- **ID** F11 · **ATTACK** A5 · **SEVERITY** SUBSTANTIVE · **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** "the matched-window comparison is not significant at B2" as evidence that
  feedback does not necessarily amplify X.
- **EXACT_FILE_AND_LINES** `flcr01_science.py:445-447`; `flcr01_correct.py:324-337`;
  `PQEC01_REVIEW_CORRECTION_ADDENDUM.md:88, 93, 95, 97`.
- **EXACT_NUMBERS** B1 matched window `[2000, 4000)`: delta **+16.31 (+14.4 %), se 7.7634,
  z = +2.102, `significant_at_2se = true`**, retaining **22 of 44** worlds — every one of them
  selected for having lived past step 4000. B2 matched window: **+1.24 (+1.1 %), z = +0.174,
  not significant**, retaining **44 of 44**. The addendum's own WARNING states the direction of the
  bias, and at B1 the excluded 22 are precisely the extinct-early worlds, so the retained mean is
  biased upward.
- **WHY_IT_MATTERS** The one comparison the addendum designs to remove the unequal-window confound
  is significant at the point where survivorship is severe and null at the point where there is
  none. Quoting only B2 presents the least informative half of the evidence as the whole of it.
- **SETTLING_COMMAND_OR_CALCULATION** Read `E_FEEDBACK.FOUR_COMPARISONS.B1.matched_time_window`.
- **MINIMUM_REQUIRED_CHANGE** State both: significant at B1 (z = +2.10, 22/44 retained) and not at
  B2 (z = +0.17, 44/44 retained), and that the B1 result is upward-biased by construction.

### F12 — a self-refuting sentence in the correction addendum

- **ID** F12 · **ATTACK** A5 · **SEVERITY** SUBSTANTIVE · **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** `F_OPERATOR_UNCERTAINTY.IDENTIFICATION_CONSEQUENCE`.
- **EXACT_FILE_AND_LINES** `flcr01_correct.py:414-418`;
  `/home/claude/edl/FLCR01/out/PQEC01_REVIEW_CORRECTION_ADDENDUM.json`, `F_OPERATOR_UNCERTAINTY`.
- **EXACT_NUMBERS** Published verbatim: *"with **0** of 25 exposure states visited by fewer than 5
  independent worlds, the upper tail of the kernel is not estimated at world level at all."*
  `STATES_VISITED_BY_FEWER_THAN_5_WORLDS = []`. The minimum world count over the 25 visited exposure
  states is 20 (state 13); the next lowest is 30 (state 22); 22 of 25 states are visited by 37–40
  worlds.
- **WHY_IT_MATTERS** A conclusion is asserted while its own stated premise is empty. This is a
  format-string template that fires regardless of the data — the exact failure mode this whole
  mission was convened to correct in the parent. It is published in a *correction* addendum.
- **SETTLING_COMMAND_OR_CALCULATION** Read the two adjacent keys.
- **MINIMUM_REQUIRED_CHANGE** Make the sentence conditional on a non-empty list, or replace it with
  the true finding: every visited exposure state has ≥ 20 contributing worlds, so world-level
  support is adequate; the identification deficit lies elsewhere.

### F13 — no feedback magnitude is asserted as identified

- **ID** F13 · **ATTACK** A5 · **SEVERITY** COSMETIC · **STATUS** DEFECT_CONFIRMED ·
  **ATTACK_VERDICT** ATTACK_REFUTED on the main clause
- **CLAIM_ATTACKED** That the addendum still asserts a feedback magnitude as if identified.
- **EXACT_FILE_AND_LINES** `flcr01_correct.py:359-370` (CAUSAL_WARNING, PRESERVED_DEVELOPMENTAL_CLUE
  — "a clue for the next design, not a measured effect"); `flcr01_final.py:24`
  (`feedback_sufficiently_represented_or_bounded: False`); `FLCR01_FINAL_DISPOSITION.json`
  `FEEDBACK_STATUS = UNRESOLVED_NOT_CONTROLLED`; cosmetic at `flcr01_correct.py:358`.
- **EXACT_NUMBERS** The key `FOUR_COMPARISONS` contains **six** comparison blocks (`pooled`,
  `birth_worlds`, `no_birth_worlds`, `horizon_matched`, `matched_time_window`, `nSY_birth_worlds`)
  plus three metadata blocks. The Simpson structure is displayed, not hidden: at B2 the pooled
  +15.2 % decomposes into +51.9 % (birth worlds, n = 18) and −10.2 % (no-birth worlds, n = 26); at
  B1, +36.5 % into +66.7 % (n = 14) and +8.3 % (n = 15). Both decompositions are published and the
  strata sum to the pooled n exactly (14+15 = 29; 18+26 = 44).
- **WHY_IT_MATTERS** The attack fails on its main clause. The candidate withdrew the old claim and
  substituted no new one.
- **SETTLING_COMMAND_OR_CALCULATION** Enumerate the keys of `E_FEEDBACK.FOUR_COMPARISONS.B1`.
- **MINIMUM_REQUIRED_CHANGE** Rename `FOUR_COMPARISONS` to `COMPARISONS`.

### F14 — the exact chain's environment is not measured from PQEC01; it is imported from MYQBD01

- **ID** F14 · **ATTACK** A6 · **SEVERITY** **LOAD_BEARING** · **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** `LINEAGE_CONTINUITY_REGION.METHOD`: "exact finite Markov chain … **at the
  measured mean candidate pool and mean organiser nX**"; and `FLCR01_FINAL_DISPOSITION.json:27`:
  "DEVELOPMENTAL — derived from post-outcome data under a mean-field environment".
- **EXACT_FILE_AND_LINES** `flcr01_science.py:323-324`
  (`E = 2.873022222222222  # measured Phase-A world-level mean exposure` /
  `C_POOL, NX = 0.961651, 4.312563`); `flcr01_science.py:292, 296` (`cc = max(int(round(c)), 1)`,
  `p = min(1.0, kY*nx*n)`); `flcr01_science.py:343`;
  `/home/claude/edl/PQEC01/code/pqec01_design.py:23-27`
  (`# developmental magnitudes measured by the parent (design input only, never a sample unit)`,
  `DEV_MEAN_CAND_Y = 0.9616507936507939`, `DEV_MEAN_NX_ORG = 4.312563492063493`);
  `/home/claude/edl/MYQBD01/out/MYQBD01_DISCOVERY_REGION.json:133`;
  `/home/claude/edl/MYQBD01/review/MYQBD01_ADVERSARIAL_REVIEW.md:417`.
- **EXACT_NUMBERS** `0.961651` and `4.312563` are truncations of MYQBD01's `DEV_MEAN_CAND_Y` and
  `DEV_MEAN_NX_ORG`, measured over MYQBD01's **14 mobile arms** — a different programme, not
  PQEC01. PQEC01's own Phase-A values, recomputed by this review from the 40 `A_*.npz` `ycells`
  ledgers (burn-in 2000, `Q_local = nX·min(nSY,free)`):
  mean candidate pool **1.1169611111**, mean local `nX` **3.9125277778**,
  mean exposure `E = mean(nX·cand)` **2.8730222222** — the last reproducing line 323 to all 16
  digits, which confirms my recomputation pipeline against the candidate's.
  Because `cc = max(round(0.961651), 1) = 1`, the chain's expected births per step at n = 1 is
  `1 · kY · 4.312563 = kY · 4.312563`, against the engine's `kY · E[nX·cand] = kY · 2.8730222`.
  **Inflation factor 4.312563 / 2.8730222 = 1.5011.** (Even the product of PQEC01's own means,
  3.9125278 × 1.1169611 = 4.370141, is the wrong first moment — the mean of a product is not the
  product of means when nX and cand are positively dependent, as they are.)
- **WHY_IT_MATTERS** The one quantity the disposition calls "measured" and "post-outcome" is neither:
  it is a design constant inherited from a grandparent experiment, and it is 50 % too large for the
  law it is standing in for. Every number in the disposition's region triple depends on it.
- **SETTLING_COMMAND_OR_CALCULATION** `grep -rn "0.961651\|4.312563" /home/claude/edl` → the only
  definitions are `PQEC01/code/pqec01_design.py:26-27` and MYQBD01 outputs. Recompute
  `mean(nX·min(nSY,free))` over `A_*.npz` `ycells[:,8]` for steps ≥ 2000 → 2.8730222222.
- **MINIMUM_REQUIRED_CHANGE** Replace `C_POOL, NX` with the exposure the chain actually needs —
  `E = 2.8730222222` entering as `cc = 1, nx = E` — recompute the region (600 points,
  kY ∈ [2.239e-05, 5.623e-04], muY ∈ [1.000e-08, 7.943e-04]), and change METHOD to name the source
  of any constant not measured in PQEC01.

### F15 — no world-level uncertainty enters the region at all

- **ID** F15 · **ATTACK** A6 · **SEVERITY** **LOAD_BEARING** · **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** The region triple `563 / kY ∈ [1.58e-05, 5.62e-04] / muY ∈ [1.00e-08,
  1.19e-03]` as a statement about the admissible plane.
- **EXACT_FILE_AND_LINES** `flcr01_science.py:323` (E defined), `:334` (E used — **founder loop
  only**), `:339-347` (lineage loop — E never appears), `:343` (`_profile(kY, muY, C_POOL, NX)`);
  `flcr01_science.py:406-408` (STATUS: "the chain uses mean exposure, not the position-resolved
  field"); `/home/claude/edl/PQEC01/out/PQEC01_ENVIRONMENT_OPERATOR.json`
  `PHASE_A_SPATIAL.WORLD_LEVEL`.
- **EXACT_NUMBERS** The lineage region is a function of two scalars and contains **zero** dispersion
  terms. Even the mean exposure E is not used by it. The measured Phase-A world-level exposure
  distribution (n = 40, recomputed by this review, identical to the parent's): mean **2.8730222**,
  sd **0.7753860**, se **0.1225993**, min **0.0**, q05 **1.157967**, q10 **2.553278**,
  median 3.101889, max **3.3774444**. Region recomputed on the identical grid at each exposure:

  | exposure Q | provenance | points | kY range | muY range |
  |---|---|---|---|---|
  | 4.312563 | as built (MYQBD01) | **563** | [1.585e-05, 5.623e-04] | [1.0e-08, 1.189e-03] |
  | 2.873022 | PQEC01 measured mean | **600** | [2.239e-05, 5.623e-04] | [1.0e-08, 7.943e-04] |
  | 2.553278 | q10 of E_w | 600 | [2.512e-05, 5.623e-04] | [1.0e-08, 6.494e-04] |
  | 2.097636 | mean − 1 sd | 591 | [3.162e-05, 5.623e-04] | [1.0e-08, 5.309e-04] |
  | 1.322250 | mean − 2 sd | 589 | [5.012e-05, 5.623e-04] | [1.0e-08, 3.548e-04] |
  | 1.157967 | q05 of E_w | 590 | [5.623e-05, 5.623e-04] | [1.0e-08, 2.901e-04] |
  | 4.444e-04 | 2nd lowest world | **0 — EMPTY** | — | — |
  | 0.0 | lowest world | **0 — EMPTY** | — | — |

  Only **399 of the 563** published points (70.9 %) remain admissible at PQEC01's own measured mean;
  201 points that are admissible there are absent from the published region.
  Intersection over all 40 Phase-A world exposures: **0 points**. Region admissible in ≥ 90 % of
  worlds: **483** points, kY ∈ [**2.512e-05, 1.413e-04**], muY ∈ [**1.000e-08, 1.939e-04**] — the
  published muY ceiling is **6.13×** and the published kY ceiling **3.98×** the 90 %-robust bounds.
- **WHY_IT_MATTERS** Non-emptiness itself is robust (38 of 40 world exposures give a non-empty
  region), so the disposition's *label* survives. The published *box* does not: it is the box at a
  single, imported, 50 %-inflated exposure, and it is roughly 4–6× wider on both axes than anything
  supported at world level. A successor that picks the published lower kY edge 1.58e-05 for
  CLEAN-LINEAGE-OPERATOR-CALIBRATION-02 will be outside the region at PQEC01's own measured mean
  exposure, which begins at 2.24e-05.
- **SETTLING_COMMAND_OR_CALCULATION** Re-run the region loop with `c = 1.0, nx = Q` for each Q in
  the table; intersect the 40 per-world point sets.
- **MINIMUM_REQUIRED_CHANGE** Propagate the measured world-level exposure distribution: publish the
  region at the mean **and** its ≥ 90 %-of-worlds robust core, and replace the single box in
  `FLCR01_FINAL_DISPOSITION.LINEAGE_REGION` with both.

### F16 — the chain is falsified, in the permissive direction, at both points where it is testable

- **ID** F16 · **ATTACK** A6 · **SEVERITY** **LOAD_BEARING** · **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** `LINEAGE_CONTINUITY_REGION.STATUS = "EXACT_UNDER_A_MEAN_FIELD_ENVIRONMENT"` and
  `nonempty_developmental_region_derived = true`.
- **EXACT_FILE_AND_LINES** `flcr01_science.py:306-319` (`_profile`), `:313-314` (`p1 = min(1, kY·nx·1)`,
  `p_no_birth = exp(T·cc·log1p(−p1))`), `:343-347`; measured values at
  `FLCR01_LINEAGE_REGIONS.json:57-78`.
- **EXACT_NUMBERS** Parameter points read from raw metadata:
  B1 `kY = 2.5118864315095822e-05, muY = 9.261187281287937e-05`;
  B2 `kY = 2.1544346900318823e-05, muY = 1e-08`. Both satisfy the region's four conditions, so both
  lie **inside** the published 563-point region.

  | | chain as built | measured (44 worlds) | exact two-sided binomial p |
  |---|---|---|---|
  | B1 P(first birth by T) | **0.6963** | 16/44 = 0.3636 | **7.81e-06** |
  | B2 P(first birth by T) | **0.6402** | 18/44 = 0.4091 | **2.40e-03** |
  | B1 P(lineage alive at T) | 0.5167 | 16/44 = 0.3636 | **4.94e-02** |
  | B2 P(lineage alive at T) | 0.9999 | 44/44 = 1.0000 | 1.000 |

  At both points the chain says **L1 passes** (≥ 0.50) while the worlds say **L1 fails** (threshold
  22/44; observed 16/44 and 18/44; combined 34/88 = 0.3864, exact two-sided p = **0.0422**).
  Two independent causes, both quantified: (i) the 1.5011× exposure inflation of F14; (ii)
  `P_first_birth_by_T` conditions on `nY ≡ 1` for all T steps and therefore ignores founder
  mortality entirely. Correcting both with the elementary competing-risks form
  `a = (1−kY·E)(1−muY)`, `P = kY·E·(1−a^T)/(1−a)` at `E = 2.8730222222`:
  **B1 → 0.3665** against measured 0.3636 (p = **1.000**); **B2 → 0.4938** against 0.4091
  (p = **0.293**). The corrected chain agrees with the data at both points; the shipped one does not.
  Regions at the exposures calibrated to the observed first-birth rates:
  B1 → Q = **1.6358**, 593 points, kY ∈ [3.981e-05, 5.623e-04], muY ∈ [1.000e-08, 4.340e-04];
  B2 → Q = **2.2199**, 554 points, kY ∈ [3.162e-05, 5.012e-04], muY ∈ [1.000e-08, 5.309e-04].
- **WHY_IT_MATTERS** "EXACT" is true of the linear algebra and false of the model. The region is
  derived from a chain that, at the only two places in the entire 128-world corpus where it can be
  confronted with data, over-predicts the gate it uses to build the region by 0.33 and 0.23 in
  probability, is rejected at p = 7.8e-06 and p = 2.4e-03, and gets the pass/fail verdict wrong in
  the direction that enlarges the region. The published kY lower edge is 2.0–2.5× too low and the
  published muY ceiling 2.2–2.7× too high once the chain is calibrated to its own data.
- **SETTLING_COMMAND_OR_CALCULATION** Evaluate `_profile` at the exact B1 and B2 parameters; compare
  to `P_first_birth` and `P_lineage_alive_at_end` in
  `TWO_CENTRE_FUNCTIONAL_REGION.MEASURED_AT_TWO_POINTS_ONLY`; exact binomial test on 44 worlds.
- **MINIMUM_REQUIRED_CHANGE** Replace `P_first_birth_by_T` with a form that accounts for founder and
  lineage mortality, set the exposure to PQEC01's measured `E`, and add a
  `CHAIN_VS_MEASUREMENT_AT_B1_B2` block to `FLCR01_LINEAGE_REGIONS.json` reporting predicted versus
  observed with the exact binomial p-values. Until then the region's STATUS must read
  `NOT_VALIDATED_AT_EITHER_MEASURED_POINT`.

### F17 — the chain's topological assumption is undisclosed

- **ID** F17 · **ATTACK** A6 · **SEVERITY** SUBSTANTIVE · **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** STATUS "the chain uses mean exposure, not the position-resolved field" as a
  complete statement of the chain's idealisation.
- **EXACT_FILE_AND_LINES** `flcr01_science.py:291-303` (one binomial of size `cc = 1` per step for
  every population size n; `nmax = int(N_STAR) + 2 = 12` with reflection at
  `min(max(n+b-d,0), nmax)`); `flcr01_science.py:406-408`;
  `/home/claude/edl/PQEC01/out/PQEC01_ENVIRONMENT_OPERATOR.json`
  `DISCOVERY_ONLY.B1.WHY_NOT_GALTON_WATSON`.
- **EXACT_NUMBERS** `_chain` places **all n Y in one cell with one candidate slot**, for every n. It
  is therefore the co-located law only. The parent's own environment operator records
  `IS_GALTON_WATSON = False` because "co-located Y draw ONE binomial from a shared candidate pool,
  and **separated Y occupy different cells with different (nX, nSY, free)**". Over the 88 Phase-B
  worlds, **92 635** recorded steps were spent in exactly two spatial centres and 17 331 in the
  co-located one-centre state — i.e. 84.2 % of the multi-Y step budget is in the configuration the
  chain cannot represent. The truncation at nmax = 12 additionally reflects mass back from above
  N_STAR, biasing `P_at_or_above_N_STAR` low.
- **WHY_IT_MATTERS** The disclosed idealisation is environmental; the undisclosed one is
  topological, is the larger of the two, and is the reason the chain cannot be checked against the
  primary criterion at all.
- **SETTLING_COMMAND_OR_CALCULATION** Read `cc = max(int(round(c)), 1)` = 1 for c = 0.961651;
  compare `ALL_WORLD_TWO_Y_SEPARATED_STEPS = 92635` to
  `ALL_WORLD_COLOCATED_ONE_CENTRE_STEPS = 17331`.
- **MINIMUM_REQUIRED_CHANGE** Extend STATUS to
  `EXACT_UNDER_A_ONE_CELL_CO_LOCATED_MEAN_FIELD_APPROXIMATION`, cite the parent's
  `IS_GALTON_WATSON = False`, and state that 92 635 of the recorded multi-Y steps are outside the
  chain's support.

### F18 — architecture test A is declared not to hold on evidence silent about its predicate

- **ID** F18 · **ATTACK** A7 · **SEVERITY** SUBSTANTIVE · **STATUS** DEFECT_CONFIRMED (overclaim)
- **CLAIM_ATTACKED** `A_lineage_incompatible_with_third_centre_control_for_all_kY_muY: HOLDS =
  false, evidence = "the exact chain admits 563 grid points satisfying L1, L2 and the N_STAR bound
  simultaneously"`.
- **EXACT_FILE_AND_LINES** `flcr01_science.py:427-431`; `FLCR01_LINEAGE_REGIONS.json:88-91`;
  `flcr01_science.py:416-417` ("nothing in the exact chain predicts them, because the chain counts Y
  and does not place them").
- **EXACT_NUMBERS** The proposition is about **third-centre control**. The cited evidence contains
  no third-centre term: the three conditions are L1, L2 and the population cap. The same file states
  the chain cannot place Y. Of the 563 points, only **90 (16.0 %)** satisfy the frozen separation
  bound `kY·E·W·(1−muY)^τ ≤ 0.5`, the only closed-form centre-count constraint in existence; only
  **88** satisfy that bound together with C2_FOUNDER.
- **WHY_IT_MATTERS** A universally quantified incompatibility is refuted with a witness set that
  never tests the property in question. If A were re-scored honestly it would be NOT_ESTABLISHED,
  which changes `ARCHITECTURE_CHANGE_JUSTIFIED = False` into a statement resting on tests B, D and E
  only — and D and E carry defects F10/F11 and F16.
- **SETTLING_COMMAND_OR_CALCULATION** Check whether the substring `L5` or `P_third` appears anywhere
  in `flcr01_science.py:339-347` → it does not.
- **MINIMUM_REQUIRED_CHANGE** Re-score A as `NOT_ESTABLISHED` with the evidence "the region enforces
  no centre-count condition; 90 of 563 points satisfy the frozen separation bound", or evaluate a
  third-centre condition inside the region.

### F19 — "none of the five tests A-E holds" misreports test C

- **ID** F19 · **ATTACK** A7 · **SEVERITY** SUBSTANTIVE · **STATUS** DEFECT_CONFIRMED (overclaim)
- **CLAIM_ATTACKED** `WHY_NOT_DISPOSITION_3`: "architecture change is not justified: **none of the
  five tests A-E holds**".
- **EXACT_FILE_AND_LINES** `flcr01_final.py:42-45`; `flcr01_science.py:437-441` (test C
  `"HOLDS": "NOT_ESTABLISHED"`); `flcr01_science.py:452`
  (`any_hold = any(v["HOLDS"] is True for v in tests.values())`);
  `FLCR01_LINEAGE_REGIONS.json:96-99`.
- **EXACT_NUMBERS** Test C's `HOLDS` is the string `"NOT_ESTABLISHED"`, not `False`. The aggregate
  is computed with `is True`, which correctly excludes it, but the narrative converts "not
  established" into "does not hold". Of the five tests, **three** are `False`, **one** is
  `NOT_ESTABLISHED`, and one (A) is `False` on void evidence (F18).
- **WHY_IT_MATTERS** "Not established" and "does not hold" are exactly the distinction this mission
  exists to enforce; collapsing them in the disposition record is the same error one level up.
- **SETTLING_COMMAND_OR_CALCULATION** Read `ARCHITECTURE.TESTS.C_...HOLDS`.
- **MINIMUM_REQUIRED_CHANGE** "three of the five tests do not hold, one is not established, and one
  is not evaluable on the evidence presented".

### F20 — the report names the failure of a gate not used in the region and is silent on the failure of the two that are

- **ID** F20 · **ATTACK** A7 · **SEVERITY** SUBSTANTIVE · **STATUS** DEFECT_CONFIRMED (underclaim)
- **CLAIM_ATTACKED** `FLCR01_LINEAGE_OPERATOR_REPORT.md:88`: "Aux deux points, **L3 échoue** (0,364
  et 0,409 contre un seuil de 0,50) et **L5 passe** (0,841)."
- **EXACT_FILE_AND_LINES** `FLCR01_LINEAGE_OPERATOR_REPORT.md:83-89` (the table itself);
  `FLCR01_LINEAGE_REGIONS.json:57-78`; `flcr01_science.py:344-345`.
- **EXACT_NUMBERS** The same table shows **L1 = 0.364 and 0.409** — below 0.50 at both points — and
  **L2 = 0.364 at B1** — below 0.50. L1 and L2 are the **only two gates that define the 563-point
  region**. L3 is not used in the region at all. Combined over both points, L1 = **34/88 = 0.3864**,
  exact two-sided binomial p = **0.0422** against the 0.50 threshold; per point 16/44 (p = 0.0961)
  and 18/44 (p = 0.2912). L3 is numerically identical to L1 at both points (a world reaches two
  centres exactly when it has a birth), so the sentence reports one of two identical columns as
  failing and the other as unremarked.
- **WHY_IT_MATTERS** The published narrative flags the failure of a gate that carries no weight in
  the disposition and passes over, in the same table, the failure of the two gates on which the
  disposition's only positive claim rests. Taken with F16 this is the sharpest available evidence
  against the region as published, and it is present in the candidate's own output.
- **SETTLING_COMMAND_OR_CALCULATION** Read the L1 and L2 columns of the table on lines 85-86 and
  compare with the 0.50 threshold in `GATE_FAMILY`.
- **MINIMUM_REQUIRED_CHANGE** Add: "L1 fails at both points (0.364, 0.409; combined 34/88,
  p = 0.042) and L2 fails at B1 (0.364). These are the two gates that define the lineage continuity
  region, and the exact chain predicts both to pass at both points."

### F21 — H_hold = 16 makes L4 incapable of failing, and its provenance is stated wrongly twice

- **ID** F21 · **ATTACK** A7 · **SEVERITY** SUBSTANTIVE · **STATUS** DEFECT_CONFIRMED (underclaim)
- **CLAIM_ATTACKED** `THRESHOLD_PROVENANCE.H_hold`: "the median observed duration of a two-centre
  episode **over all 128 worlds** … `NOT_OPTIMIZED_AGAINST_OUTCOMES`: a location statistic of an
  observed distribution, chosen before any gate was evaluated".
- **EXACT_FILE_AND_LINES** `flcr01_science.py:117-132` (episode extraction), `:160-166`
  (`TWO_CENTRE_HOLD_DURATIONS`), `:326` (`H_HOLD = float(hold["median"])`), `:360`
  (`P_hold_ge_H = sum(... w["max_hold_S"] >= H_HOLD ...) / n`), `:387-393`;
  `flcr01_science.py:157` and `FLCR01_LINEAGE_OPERATOR_REPORT.md:4` (`UNIT: one world`,
  "L'unité est **le monde**").
- **EXACT_NUMBERS** The 380 episodes come from **34** of the **88 Phase-B** worlds. The 40 Phase-A
  worlds have `kY = 0` and contribute **zero** episodes, so "over all 128 worlds" is false.
  The episode-pool median is **16**; the world-level statistic under the programme's own declared
  unit — the median of the 34 per-world maximum hold durations — is **1422**, larger by **88.9×**.
  Consequences at the two measured points:

  | H_hold | provenance | B1 P_hold_ge_H | B2 P_hold_ge_H | conditional on reaching S |
  |---|---|---|---|---|
  | 16 | episode median (as used) | 16/44 = 0.3636 | 18/44 = 0.4091 | **1.0000 / 1.0000** |
  | 125 | frozen TAU_SEP | 15/44 = 0.3409 | 15/44 = 0.3409 | 0.9375 / 0.8333 |
  | 1422 | world-level median | 8/44 = **0.1818** | 9/44 = **0.2045** | 0.5000 / 0.5000 |

  At H = 16, `P_hold_ge_H` equals `P_reach_two_centres` **exactly** at both points: L4 cannot fail
  for any world that reaches S. Single-world dominance of the episode pool is 30/380 = 0.079, and
  the episodes are right-censored — 7 worlds per point are stopped by the engine at
  `PREMATURE_THIRD_CENTRE` and 28 B1 worlds at `EXTINCT`.
- **WHY_IT_MATTERS** The episode-level median is the only unit choice under which L4 passes; under
  the unit the programme declares everywhere else, L4 fails at both measured points. Calling it
  `NOT_OPTIMIZED_AGAINST_OUTCOMES` is therefore true only of the *statistic* and false of the *unit*
  choice, which is what determines the verdict.
- **SETTLING_COMMAND_OR_CALCULATION** Recompute the median of the 34 per-world `max_hold_S` values
  → 1422; recount `max_hold_S ≥ 1422` → 8/44 and 9/44.
- **MINIMUM_REQUIRED_CHANGE** Correct "128 worlds" to "34 of the 88 Phase-B worlds"; publish both
  the episode-level (16) and world-level (1422) thresholds with L4 evaluated at each; state that at
  H = 16 the gate is implied by L3 and cannot bind.

### F22 — three gate texts do not describe the quantities computed

- **ID** F22 · **ATTACK** A7 · **SEVERITY** SUBSTANTIVE · **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** `GATE_FAMILY` L3, L4, L5 as operational definitions.
- **EXACT_FILE_AND_LINES** `flcr01_science.py:373-378` (texts) versus `:358-361` (computations);
  `FLCR01_LINEAGE_REGIONS.json:6-8`.
- **EXACT_NUMBERS**
  L3 declares "before `T_sep = 9000`"; computed as `w["reached_S"]`, i.e. at any step up to 11000.
  **3 of the 34** S-worlds first reach S at step ≥ 9000 (first-S steps: min 390, median 4842, max
  10432), so the declared gate gives **31/88 = 0.3523**, not 34/88 = 0.3864.
  L4 declares "once formed", i.e. conditional on reaching S; computed with denominator `n = 44`, all
  worlds. Conditionally it is **1.0000** at both points.
  L5 declares "no third centre **before the hold completes**"; computed as `1 − P(reached_P at any
  step)` = 0.8409 at both points.
- **WHY_IT_MATTERS** The published table is read as evaluating the published gates. It does not.
  Two of the three mismatches are permissive (L3's longer window, L4's unconditional denominator
  masking a value of 1.0).
- **SETTLING_COMMAND_OR_CALCULATION** Count worlds with `first_S >= 9000` → 3; recompute
  `P_hold_ge_H` with denominator = number of S-worlds → 16/16 and 18/18.
- **MINIMUM_REQUIRED_CHANGE** Either enforce the declared windows and denominators, or restate the
  three gate texts to match the computed quantities.

### F23 — NOT_ESTABLISHED is not too weak on the strength of the two-point L3 evidence

- **ID** F23 · **ATTACK** A7 · **SEVERITY** — · **STATUS** ATTACK_REFUTED (underclaim arm)
- **CLAIM_ATTACKED** That `ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED` understates the
  evidence, given that the two-centre gate L3 fails at both measured points.
- **EXACT_FILE_AND_LINES** `FLCR01_LINEAGE_REGIONS.json:61, 72, 81-83`;
  `flcr01_science.py:412-419`; `flcr01_science.py:437-441`.
- **EXACT_NUMBERS** L3 = 16/44 at B1 (exact two-sided binomial p vs 0.50 = **0.0961**) and 18/44 at
  B2 (p = **0.2912**); neither shortfall is significant on its own. Pooling the two points gives
  34/88 = 0.3864, p = 0.0422 — but the two points are one draw each from a two-dimensional plane
  spanning four decades in kY and seven in muY, and the candidate's own
  `binom_se_reach_two` = 0.0725 and 0.0741 make the shortfall ≈ 1.9 se and ≈ 1.2 se. Two points
  cannot identify a surface; the candidate's `EMPTY_OR_NONEMPTY =
  NOT_DETERMINABLE_ACROSS_THE_PLANE` is the correct verdict and the disposition already fails
  disposition-1 on the primary criterion for exactly this reason (`WHY_NOT_DISPOSITION_1`).
- **WHY_IT_MATTERS** The underclaim arm of A7 fails on its strongest single point. The overclaim
  arm (F18, F19) and the disclosure arm (F20, F21, F22) do not.
- **SETTLING_COMMAND_OR_CALCULATION** Exact binomial tests of 16/44 and 18/44 against 0.50.
- **MINIMUM_REQUIRED_CHANGE** None.

### F24 — the reproducibility ledger does not tell the truth about which script writes which file

- **ID** F24 · **ATTACK** A8 · **SEVERITY** SUBSTANTIVE · **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** `EVERY_FLCR01_JSON_IS_PRODUCED_BY_COMMITTED_CODE` and `FLCR01_SOURCE_HASHES`.
- **EXACT_FILE_AND_LINES** `flcr01_bind.py:45-50` (the `prod` map), `:64-67` (the hash maps);
  `/home/claude/edl/FLCR01/out/PQEC01_REPRODUCIBILITY_LEDGER.json:3-10, 28-32`;
  `flcr01_final.py:88-90`.
- **EXACT_NUMBERS** `FLCR01/out` contains **9** JSON files; the map lists **6**. Missing:
  `FLCR01_FINAL_DISPOSITION.json` and `FLCR01_FEEDBACK_REANALYSIS.json` (both written by
  `flcr01_final.py:88-90`) and `PQEC01_REPRODUCIBILITY_LEDGER.json` itself.
  `FLCR01_SOURCE_HASHES` lists **3** of the **4** committed sources. Missing:
  `flcr01_final.py`, sha256 `213e26d15c16c5ce53467d4fe4cc3c45efa55b25cd1c9012c8180b674bb3dbee` —
  the script that computes `FINAL_DISPOSITION`. Cause is ordering: the ledger was written at 12:35
  and `flcr01_final.py` was last modified at 12:36. The three listed hashes do verify against the
  working tree (`ae9854b8…`, `d6fc0fe3…`, `559d532f…`).
- **WHY_IT_MATTERS** The one artefact whose job is to certify reproducibility omits the script that
  produces the terminal disposition and the two files that carry it.
- **SETTLING_COMMAND_OR_CALCULATION** `sha256sum /home/claude/edl/FLCR01/code/*.py` and compare with
  `FLCR01_SOURCE_HASHES`; `ls FLCR01/out/*.json | wc -l` → 9 versus 6 listed.
- **MINIMUM_REQUIRED_CHANGE** Run the ledger last, or have it enumerate `FLCR01/out` and
  `FLCR01/code` by glob rather than by hand-written literal.

### F25 — every narrative deliverable is hand-written, while the ledger asserts no hand-edited blocks

- **ID** F25 · **ATTACK** A8 · **SEVERITY** SUBSTANTIVE · **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** `NO_HAND_EDITED_BLOCKS_IN_FLCR01: true`, and `flcr01_final.py`'s docstring
  "§11 — terminal disposition, **plus the three narrative reports**".
- **EXACT_FILE_AND_LINES** `flcr01_final.py:1` (docstring) versus `flcr01_final.py:88-90` (writes
  two JSONs and nothing else); no `.md` write in any of the four scripts.
- **EXACT_NUMBERS** Grep for `.md` writes across `FLCR01/code/*.py` returns **0** matches. **Four**
  committed markdown deliverables have no generating code and no hash entry:
  `FLCR01_CRITERION_AUDIT.md` (4822 B), `FLCR01_LINEAGE_OPERATOR_REPORT.md` (6019 B),
  `PQEC01_REVIEW_CORRECTION_ADDENDUM.md` (8999 B),
  `HANDOFF_CLEAN_LINEAGE_OPERATOR_CALIBRATION_02.md` (5513 B). These are the documents a reader
  actually reads, and they contain the sentences attacked in F04, F20 and F21.
- **WHY_IT_MATTERS** `NO_HAND_EDITED_BLOCKS_IN_FLCR01: true` is scoped to JSON without saying so,
  while the docstring claims code produces the narrative. FLCR01's own critique of PQEC01 was that
  four narrative blocks had been hand-added to a disposition file
  (`PQEC01_HAND_EDIT_ACKNOWLEDGED`); FLCR01 hand-writes four entire narrative documents.
- **SETTLING_COMMAND_OR_CALCULATION** `grep -rn "\.md" /home/claude/edl/FLCR01/code/*.py` → the only
  hits are in prose, none in a write path.
- **MINIMUM_REQUIRED_CHANGE** Either generate the four markdown files from the JSONs, or restate the
  key as `NO_HAND_EDITED_BLOCKS_IN_ANY_FLCR01_JSON` and add
  `FLCR01_MARKDOWN_IS_HAND_WRITTEN: true` with sha256 of each.

### F26 — the correction addendum cannot be regenerated from the repository

- **ID** F26 · **ATTACK** A8 · **SEVERITY** SUBSTANTIVE · **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** `PQEC01_REVIEW_CORRECTION_ADDENDUM.json: "FLCR01/code/flcr01_correct.py"` under
  `EVERY_FLCR01_JSON_IS_PRODUCED_BY_COMMITTED_CODE`.
- **EXACT_FILE_AND_LINES** `flcr01_correct.py:16` (`PRE = "/home/claude/FLCR01/work/prefix/out"`),
  `:62` (reads `{PRE}/PQEC01_INTERNAL_VALIDATION.json`), `:110` (hashes
  `/home/claude/FLCR01/work/prefix/pqec01_analyse_PREFIX.py`), `:41-44` (six engine files under
  `/home/claude/ORR01/` and `/home/claude/OBTC02/`).
- **EXACT_NUMBERS** `git ls-files | grep -c "FLCR01/work"` → **0**. `/home/claude/FLCR01/work` is
  outside the repository root `/home/claude/edl` (`git check-ignore` reports
  "outside repository"). The recovered pre-fix analyser (30 059 B, sha256
  `cb486ce271b9c1ae01c2148ff87233f2906622c13d1f634486bf8828530e3caa`) and its regenerated outputs
  exist only in that untracked directory. Six further inputs are read from two sibling programmes.
  Of the six lines of the `prod` map, this is the only entry whose script cannot run from a fresh
  clone.
- **WHY_IT_MATTERS** The addendum is the artefact that corrects the parent's record. Its
  regeneration depends on files that are neither committed nor hashed into the ledger, so a fresh
  clone reproduces `flcr01_bind`, `flcr01_science` and `flcr01_final` but not `flcr01_correct`.
- **SETTLING_COMMAND_OR_CALCULATION** `git ls-files FLCR01 | wc -l` → 17, none under `work/`; try
  running `flcr01_correct.py` from a clone → `FileNotFoundError` at line 62.
- **MINIMUM_REQUIRED_CHANGE** Commit `pqec01_analyse_PREFIX.py` and the regenerated pre-fix outputs
  under `FLCR01/work/prefix/` (or reconstruct them in-script from the C3 Git blob), and record the
  external engine paths and hashes in the ledger.

### F27 — two of the six disposition requirements are hardcoded constants

- **ID** F27 · **ATTACK** A8 · **SEVERITY** SUBSTANTIVE · **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** `DISPOSITION_1_REQUIREMENTS` as a computed evaluation.
- **EXACT_FILE_AND_LINES** `flcr01_final.py:19-25`, specifically `:20`
  (`"lineage_is_the_correct_criterion": True`) and `:25`
  (`"one_clean_disjoint_test_can_confirm_it": True`); the selector at `:26-31`, whose second branch
  is `elif d1["lineage_is_the_correct_criterion"] and not L["EMPTY"]`.
- **EXACT_NUMBERS** Four of the six requirements are derived from files
  (`cm["FOUNDER_SURVIVAL_VERDICT"]`, `not L["EMPTY"]`, `len(MISSING_FROM_DATA) == 0`, literal
  `False` for feedback); **two are literal `True`**. The terminal label
  `LINEAGE_CRITERION_SUPPORTED__OPERATOR_NOT_IDENTIFIED_FROM_PQEC01` is selected by a branch whose
  first conjunct is one of the two hardcoded constants.
- **WHY_IT_MATTERS** A hardcoded `True` is load-bearing for the disposition label. It cannot be
  falsified by any run of the code, so the disposition selector cannot reach
  `FOUNDATIONAL_CRITERION_NOT_RESOLVED` for any reason other than an empty region.
- **SETTLING_COMMAND_OR_CALCULATION** Set line 20 to `False` and re-run `flcr01_final.py`; the
  disposition changes to `FOUNDATIONAL_CRITERION_NOT_RESOLVED__NO_NEW_RUN_AUTHORIZED` with no other
  input altered.
- **MINIMUM_REQUIRED_CHANGE** Derive both from the criterion matrix
  (`cm["PRIMARY_CRITERION_SELECTED"]`, `cm["SUPPORTING_CRITERION"]`) or mark them explicitly as
  editorial judgements rather than requirements evaluated by the code.

### F28 — dead parameters and an undeclared τ substitution

- **ID** F28 · **ATTACK** A8 · **SEVERITY** COSMETIC · **STATUS** DEFECT_CONFIRMED
- **CLAIM_ATTACKED** Housekeeping of the science module.
- **EXACT_FILE_AND_LINES** `flcr01_science.py:424` (`def architecture_test(fc, reg, op)` — `fc` and
  `op` are never referenced in the body); `flcr01_science.py:17` (`TAU_FROZEN = 125.0`) versus
  `:44` and `:337` (both hardcode `(1 - muY) ** 111.0`).
- **EXACT_NUMBERS** τ = 111.0 is the **measured** median separation delay
  (`SEPARATION_DELAY_AFTER_FIRST_BIRTH.median = 111.0`, n = 34), substituted for the analytically
  frozen `TAU_SEP = 125.0` inside the founder-region test and inside the exposure-independence
  sweep. The substitution is stricter, not laxer — `(1−muY)^111 ≥ (1−muY)^125` — and the founder
  region is empty at 83, 111 and 125 alike (0 points each), so nothing turns on it.
- **WHY_IT_MATTERS** Harmless here, but a post-outcome measured value silently replacing a frozen
  constant inside a criterion test is the exact pattern the mission is auditing.
- **SETTLING_COMMAND_OR_CALCULATION** Recount `{C1, C2_FOUNDER, C3}` at τ = 125 → 0.
- **MINIMUM_REQUIRED_CHANGE** Use `TAU_FROZEN` and report the τ = 111 variant separately, labelled
  as a measured-value sensitivity check; drop the unused parameters.

---

## 2. Attack-by-attack summary

| attack | verdict | load-bearing | substantive | cosmetic |
|---|---|---|---|---|
| A1 founder rejection scientific or outcome-driven | **ATTACK_REFUTED** — it is scientific | 0 | 1 (F01) | 0 |
| A2 measurable without invented genealogy | **ATTACK_REFUTED** | 0 | 0 | 0 |
| A3 contradiction removed or hidden | **DEFECT_CONFIRMED** | 2 (F04, F06) | 1 (F05) | 0 |
| A4 all 128 worlds developmental | **ATTACK_REFUTED** | 0 | 0 | 1 (F08) |
| A5 Simpson / stopping bias | **DEFECT_CONFIRMED** | 0 | 4 (F09–F12) | 1 (F13) |
| A6 world-level uncertainty in the region | **DEFECT_CONFIRMED** | 3 (F14–F16) | 1 (F17) | 0 |
| A7 architecture over/under-claimed | **DEFECT_CONFIRMED** (overclaim yes, underclaim partly) | 0 | 5 (F18–F22) | 0 |
| A8 reproducibility | **DEFECT_CONFIRMED** | 0 | 4 (F24–F27) | 1 (F28) |

## 3. What survives and what does not

**Survives.** The founder gate is genuinely unsatisfiable a priori, by an algebra I re-derived
independently and that is genuinely independent of kY and of exposure. The rejection of founder
survival is made on scientific grounds stated without reference to any region, and the adversarial
test of that claim runs against the outcome-driven hypothesis: the criterion the candidate deleted
opens a region 4.7× smaller than the alternative it did not delete. Lineage continuity and
two-centre continuity are exactly measurable from recorded quantities; no genealogy is invented
anywhere; `n_centres` is single-linkage at CORE_R = 5.0 as claimed; extinction is absorbing, so
`N_Y > 0` is exactly "descended from the initial state". All 128 worlds are correctly and
consistently labelled post-outcome developmental data, and nothing in FLCR01 is called prospective,
held-out or confirmatory. Every count I recomputed from raw matched to the digit. The refusal to
call the two-centre region determinable from two parameter points is correct.

**Does not survive.** The region triple in the disposition. It is computed in an environment
imported from a different programme (MYQBD01's `DEV_MEAN_CAND_Y`, `DEV_MEAN_NX_ORG`) while being
described as measured, at an effective exposure 1.5011× PQEC01's own measured mean; it carries no
world-level dispersion at all, although the parent measured that dispersion and although the region
is empty at 2 of the 40 measured world exposures and 4–6× wider than its own 90 %-of-worlds robust
core; it evaluates L1 over 11000 steps while declaring 9000; it applies an undeclared population cap
that does 65 % of the filtering; it never evaluates L3–L7, including the gate declared as the
replacement for C3, so 84 % of it violates the frozen separation bound while 89 % of it satisfies
the founder gate it is supposed to have superseded; and the chain that produces it is rejected by
the data at both points where data exist (p = 7.8e-06 and 2.4e-03), in the direction that enlarges
the region — while a two-line correction of the exposure and of the neglected founder mortality
brings it into agreement (p = 1.000 and 0.293).

None of this makes the region empty. Non-emptiness is robust across 38 of the 40 measured world
exposures and across every correction I applied (473 to 600 points). What is not supportable is the
specific triple `563 / [1.58e-05, 5.62e-04] / [1.00e-08, 1.19e-03]`, its "measured" provenance, and
its status as a derivation. The categorical label survives; the quantitative disposition does not.

On the second half of the disposition, `ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED` is the
right verdict, reached partly for wrong reasons: test A is scored on evidence that never touches its
predicate, test D on a mis-stated range and a selectively cited significance, test E on the chain of
F16, and the narrative converts test C's `NOT_ESTABLISHED` into "does not hold". Conversely the
underclaim argument fails on its strongest point — L3's shortfall is 0.096 and 0.291 by exact
binomial test, and two points cannot identify a surface — but succeeds on disclosure: L1 fails at
both points and L2 at one, in the candidate's own published table, unremarked, and these are the two
gates the region is built from; and L4's threshold is the one unit choice under which it cannot
fail (episode median 16 versus world-level median 1422, 88.9×).

The correction addendum is the strongest single artefact in the delivery — it withdraws claims
against its own interest, publishes the firewall leak, the FAIL→PASS test change and the
survivorship warning. It is weakened by three things: the B1 pooled row reproduces exactly the
confound the addendum withdrew the old claim for, on 29 of 44 worlds against B2's 44 of 44; the
"+1 % to +67 %" range conflates parameter point with stratification; and
`IDENTIFICATION_CONSEQUENCE` asserts a conclusion whose stated premise is the empty set.

**Verdict rationale.** The criterion question is resolved, so
`CANDIDATE_TOO_STRONG__CRITERION_NOT_RESOLVED` is wrong. The region is if anything too permissive,
so `CANDIDATE_TOO_CONSERVATIVE__LINEAGE_REGION_IS_DERIVED` is wrong. Five load-bearing defects mean
`CANDIDATE_DISPOSITION_SUPPORTED` is wrong. The disposition's label stands, its numbers do not, and
the reasons are provenance (an imported constant sold as measured, an unregenerable addendum, an
untruthful ledger, unhashed hand-written narrative) and evidence (no dispersion, a chain falsified
where testable, an undeclared gate, a mislabelled window).

---

```
REVIEWER_VERDICT              = EVIDENCE_OR_PROVENANCE_INCOMPLETE
LOAD_BEARING_DEFECTS          = 5
SUBSTANTIVE_DEFECTS           = 16
COSMETIC_DEFECTS              = 3
ATTACKS_REFUTED               = 3 of 8
FOUNDER_REJECTION_IS_SCIENTIFIC = YES
LINEAGE_MEASURABLE_WITHOUT_GENEALOGY = YES
CONTRADICTION_TRULY_REMOVED   = UNDETERMINED
NEW_SCIENTIFIC_RUNS_BY_REVIEW = 0
```
