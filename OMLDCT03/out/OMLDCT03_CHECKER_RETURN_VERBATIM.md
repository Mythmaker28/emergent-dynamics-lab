# ADVERSARIAL CHECKER RETURN — OMLDCT03

**Scope.** Repository `/home/claude/edl` at `de74719`; the 123 sealed archives at `/home/claude/TBRT02_raw`. Nothing committed, nothing under any mission directory modified, all scratch in `/tmp/claude-0/.../scratchpad`. Every "VERIFIED" below was recomputed by me, most of it with code that imports nothing from this repository.

**Headline.** The arithmetic is clean — cleaner than any mission I have checked in this programme. All 41 per-pair durations, exposures and termination types reproduce exactly under my own from-scratch reimplementation of the components / centroid / link / identity chain; all published statistics reproduce to the last digit; the archives, the fork, the prefix, the seeds, the law bits and the method hashes all check out. **The executed analysis is a faithful execution of the frozen analysis.** What is *not* a faithful execution of the frozen *design* is the accrual, and that is where the load-bearing findings are. Below that sit one material scientific confound the mission was told in writing to test and did not, and a cluster of governance omissions that repeat findings already accepted against RPP98 and FIMRCC02.

---

## PART A — WHAT I VERIFIED SOUND

Stated first and plainly, because it is most of the mission.

**A1. The endpoints reproduce, independently.** I wrote `indep.py` from the stated definitions alone — toroidal single-linkage at `CORE_R = 5.0` on `L = 36` by explicit union-find over an interpreted adjacency loop; the anchor-on-first-member wrapped centroid; the strict one-forward/one-back link rule with `math.hypot ≤ CORE_R`; a single identity chased forward from `t_m`. It imports neither `ldfma01_raw`, `omldct02_e3_a`, `omldct02_e3_b` nor `omldct02_analysis`. On **all 41 pairs / 82 arms**: `E3_DURATION`, `E3_EXPOSURE` and `identity_termination_type` match `OMLDCT03_FROZEN_TEST_RESULT.json:PER_PAIR` exactly. **Zero discrepancies.** I also re-ran the two frozen classifiers themselves on 6 pairs (12 arms) with `PYTHONDONTWRITEBYTECODE=1`: the committed `OMLDCT03/work/omldct03_pairs.json` records are bit-identical dictionaries — the work file was not hand-edited.

**A2. The statistics reproduce, independently.** I reimplemented Pratt midranks, the exact conditional sign-flip DP (in `Fraction`, so no float question arises), the median, Hodges-Lehmann and the distribution-free interval:

| | published | mine |
|---|---|---|
| duration W+ | 521.0 | 521.0 |
| duration p | 0.24638633591985126 | 270904641269/1099511627776 = 0.24638633591985126 |
| duration median / HL | +0.21357410029805912 / +0.3330781223665489 | identical |
| duration interval | (−0.23853947588423452, 0.8369882167858358) | identical |
| exposure W+ | 504.0 | 504.0 |
| exposure p | 0.34791725337890966 | 191269532797/549755813888 = 0.34791725337890966 |
| exposure median / HL | +0.5694680843784337 / +0.3161356967977471 | identical |
| exposure interval | (−0.31096591919555827, 0.8738989882841586) | identical |

`n_nonzero = 41`, `n_zero = 0` both endpoints; no ties in `|d|`, so Pratt coincides with plain Wilcoxon here. The published `log_duration_difference` / `log_exposure_difference` reproduce from the published integer durations/exposures at max absolute error **0.0**.

**A3. The interval is valid.** `omldct02_analysis.py:76-99` trims 280 Walsh averages from each end; for n = 41 that is nominal coverage **0.95034** (trim 279 → 0.95188, trim 281 → 0.94877). It is the tightest trim still at or above 95 %. By explicit test inversion the exact acceptance region is (w[279], w[581]) = (−0.24316, 0.83777) and the published interval (w[280], w[580]) sits inside it — conservative at the stated level, marginally tighter than the conventional inversion interval. Not a defect. (Latent, not triggered: `hl_interval` builds its null from *untied* ranks 1..n while the p-value uses Pratt midranks. With `n_zero = 0` and no ties they coincide exactly. On OMLDCT02's own 33-pair run, which had one zero, they did not, and nobody noticed.)

**A4. Provenance of the data.** All **123** archives match the sha256 sealed in `TBRT02/work/TBRT02_SEALED_LEDGER_*.jsonl` (0 mismatches, 0 missing, byte sizes match); `integrity_ok` true on all; `steps_executed = 11000` on all. All fork/intervention fidelity fields pass on all 41 triples (`PHYSICAL_STATE_IDENTICAL`, `RNG_STATE_IDENTICAL`, SELECTIVE `parent_emptied` / `daughter_untouched` / `occupancy_conserved` / `rng_unchanged`, SHAM `removed_nothing` / `phys_unchanged`, `ALL_THREE_ARMS_DIVERGED`).

**A5. The common prefix is bit-identical.** I hashed every archive array restricted to `t ≤ t_m` — all nine cell columns, all nine component columns, the step array and the three ledgers — for all three arms of all 41 triples. **41/41 identical across arms.** The frozen `MATCHED_DESIGN` requirement ("one common prefix to the frozen functional-maturity time t_m … fork two bit-identical continuations") holds by measurement, not by assertion.

**A6. The daughter cell set is the right one.** This was flagged as the most likely place for a silent error; it is clean. TBRT02's `meta["intervention"]` carries exactly `('arm','competitor_cell','competitor_mass','daughter_cells','parent_cells','rng_hash_after','rng_hash_before','step')` on **all 123 archives** — there is no `daughter_cells_before` and no `daughter_cells_after` in these files at all (those names live in `TLMR01/code/tlmr01_world.py:114`, a different single-trajectory code path that TBRT02 never uses). `meta["intervention"]["daughter_cells"]` equals `FORK["locked_daughter_cells"]` in 41/41 triples × 3 arms, and `meta["t_m"] == meta["intervention"]["step"] == ledger t_m` in all of them. So `omldct03_admissibility.py:49` and `omldct02_c3_raw.py:126` are reading the same object under two names. There was no wrong field available to pick. And the fail-safe is real: `omldct02_e3_b.py:178` defaults to `iv.get("daughter_cells_after")`, which is absent here — had OMLDCT03 relied on the default, `dset` would be empty and all 82 arms would have returned `OK: False`. It cannot fail silently.

**A7. TBRT02's SELECTIVE is OMLDCT02's treatment.** By code: `tbrt02_fork.py:84-89` applies `FMW.intervene(arm, ())` for SHAM and `FMW.intervene(arm, pcells)` for SELECTIVE — the same two calls as `omldct02_fork.py:121-125`, on `pcells`/`dcells` from the same `TR.Trigger` with the same `PREFIX_LIMIT = min(horizon, LATEST_ALLOWED_TRIGGER+1)`, the same `L_GRID = 36`, the same `T_HORIZON = 11000`, and OMLDCT02's own `_write` and `SCHEMA` imported verbatim. The intervention is applied *after* the `t_m` row is recorded and the post-fork loop runs `range(t_m+1, horizon)` in both. By hashes: the law parameters in TBRT02's archives, in `tbrt02_fork.LAW`, in `tlmr01_laws.LAWS["LAW_C_MCTT01"]` and in the freeze's `Y_LAW_BITS` are the *same IEEE-754 bit patterns* (`0x3f50763f01e8e5b2`, `0x3f484713dc1c8ab5`, `0x3fba462ec93926a0`). All **8** method files common to OMLDCT02's and TBRT02's freezes have identical sha256, and all **39** files in OMLDCT02's `METHODS_HASH` manifest are byte-unchanged on disk today. The engine files reachable only through `tlmr01_world`'s hard-coded absolute paths (`/home/claude/ORR01/code`, `/home/claude/OBTC02/code`) are byte-identical to their in-repo copies, so that path oddity is inert. The third arm cannot contaminate: `forks` are three independent `copy.deepcopy(w)` taken before any arm runs, each carrying its own generators; the only shared object in the arm loop is the read-only `sp.CAP`.

**A8. Seed disjointness holds, verified from the lists.** OMLDCT02: 1024 base + 6 reserve. TBRT02: 3072 base + 8 reserve. Intersection of base sets: **0**. Intersection of (base ∪ reserve) sets: **0**. Of the **885** seeds TBRT02 actually consumed, **0** appear in OMLDCT02's manifest. No duplicate index in TBRT02's 885 rows; every seed matches the frozen manifest at its index; both shards are index-monotone (shard 0 = even, shard 1 = odd) and no seed was skipped, replaced or reordered on the basis of its outcome — only 41 admissible triples exist in the 885 attempted, and all 41 were retained, so there is no selection on outcome anywhere.

**A9. `OUT_OF_RANGE` is legitimate.** It is in classifier A's own vocabulary (`LDFMA01/code/ldfma01_raw.py:141`, `link_reason`: zero candidates within `CORE_R`) and B's (`omldct02_e3_b.py:217`). I opened all six SHAM cases and reconstructed the termination step. **Five** (231, 573, 593, 768, 793) are a one-cell daughter whose Y died while the world lived on — the nearest surviving component is 6.4 to 13.6 away. That is the frozen list's **"empty component"**, differing from `NO_COMPONENT_AT_THE_NEXT_STEP` only in that the *world* also died in the latter. **One** (866) is a 17-cell component fragmenting into four, none of whose centroids lies within 5.0 of the parent centroid — the frozen list's **"split"**. So all six are pre-declared modes and the string is a naming difference, not a sixth mode. It is *not* a defect. What is missing is that no artefact anywhere writes this mapping down, so `PER_PAIR` cannot be read as a competing-risks table without it, and the string "OUT_OF_RANGE" actively hides that five of the six are the daughter dying (see F2).

**A10. No administrative truncation.** Zero `REACHED_THE_WINDOW_HORIZON` in 82 arms; the longest duration is 831 against `T = 11000`. TBRT02's C5 declared its *lineage* durations right-censored at differing per-arm rates (8/29/16); **this endpoint is not censored at all**, in either arm. That C5 disclosure does not transfer to OMLDCT03's numbers and I found no horizon artefact.

**A11. Content hashes.** `ADMISSIBILITY_CONTENT_HASH`, `RESULT_CONTENT_HASH` and `AUTHORISATION_CONTENT_HASH` all reproduce under `omldct02_hashes.content_digest`. Classifiers A and B agree not only on the three fields the frozen rule requires but on *every* reported field — `interval_end`, `n_rows_in_interval`, `min_nY`, `max_nY`, `nY_histogram` — in all 82 arms. Four SHAM arms carry exact-boundary link comparisons (`d2 == R2 == 25.0`); A's `hypot ≤ 5.0` and B's `d2 ≤ 25` and my `hypot ≤ 5.0` all include them identically. `ARCHIVE_ROWS_WERE_ORDERED` true everywhere; `contiguous` true everywhere.

**A12. The declared exposure-window sensitivity is immaterial.** `omldct02_e3_b` computes `E3_EXPOSURE_SYMMETRIC_VARIANT` precisely so the `t_m`-inclusive window "is measured, not assumed away". OMLDCT03 never reports it. I ran it: p = **0.3348**, median +0.5705, HL +0.3426, against the frozen 0.3479 / +0.5695 / +0.3161. Nothing turns on it. (Recorded as an omission in F11, not as a defect.)

---

## PART B — FINDINGS

### F1 — The frozen *analysis* was executed; the frozen *accrual rule* was not, and under it these same data still read INSUFFICIENT. **LOAD-BEARING: it restricts what "the frozen test was executed" can mean.**

`OMLDCT02/out/OMLDCT02_MASTER_FREEZE.json` freezes six things OMLDCT03 quotes and four it never mentions:

```
ACCRUAL_RULE  "process the frozen base seeds in index order until 41 technically valid
               admissible pairs are retained, or the hard 512-arm-instance ceiling is exhausted."
MAX_PRIMARY_ARM_INSTANCES  512
SEED_SET_HASH  998f6fab…   N_BASE_SEEDS 1024
TARGET_VALID_PAIRED_BLOCKS 41
```

OMLDCT02 stopped at 33 pairs with `CAMPAIGN_STOPPED = "HARD_ARM_INSTANCE_CEILING"` and 510.569 of 512 spent. The terminal `INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS` **is the accrual rule firing**, not an accident.

I recosted TBRT02's 885-seed stream under OMLDCT02's own two-arm formula `(t_m+1)/H + 2(H−t_m−1)/H`:

- total cost of the whole TBRT02 stream, two-arm: **571.649** instances
- **a 512-instance budget exhausts at index 789 with 38 admissible pairs**

So: **run OMLDCT02's frozen accrual rule on TBRT02's own seeds and it terminates at 38 pairs with `INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS`.** The 41st pair exists only because TBRT02 was authorised a different ceiling (926, sized by EVCS01 for a three-arm campaign) for a different question. OMLDCT03 imports the accrual and leaves the rule that governs it behind.

Three further texts bear directly on this and OMLDCT03 confronts none of them:

- `OMLDCT02_FINAL_DISPOSITION.json`: `IS_ANY_FURTHER_EXPERIMENT_AUTHORISED: "No. SECOND_CLEAN_RESTART is forbidden, SECOND_TARGETED_MEASUREMENT_CAMPAIGN is forbidden, and nothing here authorises a successor."`
- `OMLDCT02_MASTER_FREEZE.json`: `SECOND_CLEAN_RESTART: "forbidden"`, `MAX_POST_OUTCOME_SCIENTIFIC_REPAIRS: 0`.
- `FIMRCC01/out/FIMRCC01_FINAL_DISPOSITION.json:INHERITED_CLAUSES_RE_EMITTED_VERBATIM`: `SECOND_TARGETED_MEASUREMENT_CAMPAIGN = forbidden`.

The counter-argument is real and I put it on the record: the 512 ceiling is a *cost* bound on OMLDCT02's own spending, OMLDCT03 spends zero new instances, and the operator is the authority who may lift a resource bound. But the human authorisation (`OMLDCT03_HUMAN_AUTHORISATION.json`) says the opposite of what happened — "**modifier un seul champ du gel OMLDCT02 — ni l'endpoint, ni le test, ni alpha, ni la regle de Pratt, ni le seuil de 41**" — while three other fields of the same freeze (`ACCRUAL_RULE`, `MAX_PRIMARY_ARM_INSTANCES`, `SEED_SET_HASH`) were set aside silently. The authorisation covers what was done only if you already agree that those three fields are not part of the freeze, and nothing in the record argues that.

**What this restricts:** the result is a valid execution of OMLDCT02's frozen *statistical procedure* on a matched sample of 41 pairs from the same law and the same treatment. It is not an execution of OMLDCT02's frozen *experiment*, whose stopping rule these data do not satisfy. The terminal string is real; the sentence "le test GELE d'OMLDCT02 est EXECUTE" is broader than what happened.

---

### F2 — Differential mortality: the confound the operator wrote down two hours earlier, and did not test. **LOAD-BEARING for the p-values; not for the terminal string.**

`GATE01/out/EDL_PRIOR_ART_MAP.json`, written at 02:07:38 on the day OMLDCT03 ran, item 5 of `CE_QUI_DOIT_ETRE_FAIT_AVANT_TOUT_GEL`, and `LE_RISQUE_HONNETE`:

> "CONFONDANTS : temps absolu et exposition (pas vivants apres t_m ; Y s'eteint dans 12 des 41 bras SELECTIVE, 5 DISPLACED, 2 SHAM) **testes avant publication, pas apres**."
> "Un contraste apparie de comptes apres t_m mesurera **en partie la mort du monde et non la persistance de la fille**. C'est le premier confondant a neutraliser."

VERIFIED, from the archives:

- **9 of 41 SELECTIVE** arms end the daughter's identity by total Y extinction inside her own window (`NO_COMPONENT_AT_THE_NEXT_STEP`); **0 of 41 SHAM**. I confirmed all nine are absorbing: `nY` hits 0 at `end+1` and never returns.
- Over the whole post-`t_m` trajectory: **12 of 41 SELECTIVE** worlds go extinct against **2 of 41 SHAM** (indices 780, 793), exactly reproducing the 12/2 in the prior-art map and RPP98's F6/F7.

Cause-specific sensitivity (mine, **post-hoc diagnostics, not the frozen test**):

| | n | duration p | duration median | exposure p | exposure median |
|---|---|---|---|---|---|
| the frozen test, as executed | 41 | 0.2464 | +0.2136 | 0.3479 | +0.5695 |
| drop the 9 SELECTIVE window-extinctions | 32 | **0.0433** | +0.6325 | 0.0770 | +0.7295 |
| always-survivor stratum (neither arm extinct) | 28 | 0.0774 | +0.6325 | 0.0946 | +0.7295 |
| drop the 7 SHAM MERGE pairs | 34 | 0.2932 | +0.2071 | 0.3605 | +0.5118 |
| pairs terminating the same way in both arms | 22 | 0.1207 | +0.4454 | 0.1465 | +0.6208 |

The 13 pairs containing an extinction have median log duration difference **−0.3231** with 6/13 positive; the other 28 have +0.6325 with 19/28 positive. **The published p = 0.246 is a mixture of a moderately positive contrast among worlds the treatment does not kill and a negative contrast among the worlds it does.**

Two things must be said in the same breath. First, this is *not* an alternative result: every restriction above conditions on a post-treatment variable, which `FIMRCC01_ENDPOINT_PREREGISTRATION.json` forbids by name and the OMLDCT03 authorisation explicitly excludes ("aucun sous-ensemble de survivants"). FIMRCC02's checker was right that the always-survivor stratum is unusually well behaved here — both potential survival indicators are observed for every seed, since both arms are run on the same stream — but it is still a narrower estimand than the one frozen. Second, and importantly: **no specification I can construct flips the AND rule.** Duration alone rejects at 32 pairs; exposure never does; the pooled 33+41 = 74 pairs give 0.141/0.117. `TERMINAL = ..._NOT_DETECTED__INCONCLUSIVE_UNDER_FROZEN_POWER` is robust.

What is wrong is that OMLDCT03 publishes the p-values with no statement at all about the 9-versus-0 asymmetry that its own `PER_PAIR` table displays, after being told in writing, by the same operator, hours earlier, to test exactly this before publishing. The confound is disclosed only as a column of strings a reader must decode.

---

### F3 — The two arms are not the same tracking problem. **LOAD-BEARING for interpretation; within the frozen CLAIM_CEILING.**

VERIFIED by direct measurement over the daughter's own window in each arm:

| | steps in window | of which the world holds **exactly one** component |
|---|---|---|
| SELECTIVE | 9713 | **9672 (99.6 %)** |
| SHAM | 8353 | **534 (6.4 %)** |

In the SELECTIVE arm the locked daughter is, essentially always, the only object in the world. The frozen link rule terminates an identity by (a) two-or-more successors in range, (b) two-or-more predecessors mapping to one successor — a MERGE — (c) no successor in range, (d) no components at all, (e) horizon. Channel (b) is *arithmetically impossible* with one predecessor (`ldfma01_raw.py:143` requires `len(bwd[c[0]])>1`). The observed mix follows exactly:

```
SELECTIVE : SPLIT_OR_TIE 32,  NO_COMPONENT_AT_THE_NEXT_STEP 9,  MERGE 0,  OUT_OF_RANGE 0
SHAM      : SPLIT_OR_TIE 28,  MERGE 7,  OUT_OF_RANGE 6,          NO_COMPONENT 0
```

and the same profile appears in OMLDCT02's own 33 pairs (SELECTIVE: 29 split / 2 merge / 2 extinction; SHAM: 22 split / 5 merge / 6 out-of-range), which is a useful independent corroboration that TBRT02's arms behave like OMLDCT02's.

The intervention removes the parent. The parent is the object that supplies the competing component. So a substantial part of "the daughter's identity lasts longer under SELECTIVE" is "there is no longer anything for the tracker to confuse her with." The freeze's `CLAIM_CEILING` is written to cover exactly this ("selective removal of the parent **changed** … the post-removal identity duration"), so a positive result would have been within bounds. But `CE_QUE_CE_TEST_NE_DIT_PAS` in the result file does not name it, `CLAIM_CEILING` and `IT_DOES_NOT_ESTABLISH` are never quoted anywhere in OMLDCT03, and the commit-message gloss (F10) points the reader the other way. For scale: the tracked object is 1–3 cells and 1–3 Y at `t_m`, peaking at 1–6 Y over its life in 40 of 41 SELECTIVE arms.

---

### F4 — The committed admissibility rule is not the frozen retention rule, and the artefact says it is. **MATERIAL for the record; numerically null — I checked.**

`OMLDCT03_ADMISSIBILITY.json` carries the key `LA_REGLE_APPLIQUEE_EST_CELLE_D_OMLDCT02_ET_N_EST_PAS_LA_MIENNE`, containing:

> `"une_paire_est_admissible_si": "les deux classificateurs geles rendent OK sur les DEUX bras et s'accordent EXACTEMENT sur E3_DURATION et E3_EXPOSURE"`

The frozen rule is `omldct02_c3_raw.py:131-134`, which has a **third** clause, `a["identity_termination_type"] == b["identity_termination_type"]`. And `omldct03_admissibility.py:63-65` adds **two clauses the frozen rule does not have**: `t_m_identical_across_arms` and `daughter_cells_identical_across_arms` (in `measure()` these are single inputs applied to both arms, so the question cannot arise). So the committed rule differs from the frozen one in both directions, and the sentence quoted above — the load-bearing sentence of that file — is false as written. The commit message `384333f` repeats it ("sous les criteres GELES d'OMLDCT02 … s'accordent EXACTEMENT sur E3_DURATION et E3_EXPOSURE").

`omldct03_frozen_test.py:12-14` declares the omission and repairs it at line 40, which is the right thing to have done and is stated honestly. The repair costs nothing: I confirmed from the committed work file that **A and B agree on `identity_termination_type` in all 82 arms**, so retention under the full rule is 41 and the gate was opened on a count the frozen rule does support. The claim is right; the file that carries it is not.

---

### F5 — The frozen pipeline's C3 integrity gate was skipped entirely. This is RPP98's accepted finding F15, verbatim, on the same 123 archives. **MATERIAL for provenance; not load-bearing, because I ran the check and it passes.**

`omldct03_admissibility.py:45`:

```python
path = os.path.join(RAW, os.path.basename(d["path"]))
```

`d["sha256"]` is present in the ledger row and is never read. Neither is `d["integrity_ok"]`, nor `meta["integrity_ok"]`, nor `NARROW_DTYPES_LOSSLESS`, nor `ARCHIVE_ROWS_WERE_ORDERED` (classifier B computes it and the driver discards it), nor the fork/intervention fidelity block, nor index/seed uniqueness. In OMLDCT02 all of this is `omldct02_c3_raw.raw_manifest()`, a **separate stage that runs before `measure()`** and whose output (`OMLDCT02_RAW_MANIFEST.json`) carries `ALL_ARCHIVE_HASHES_MATCH`, `ALL_FIDELITY_CHECKS_PASS`, `NO_DUPLICATE_SCIENTIFIC_SEED`, `ONE_SELECTIVE_AND_ONE_SHAM_PER_PAIR`. OMLDCT03 has no equivalent artefact.

Compare `RPP98/out/RPP98_CHECKER_RETURN_VERBATIM.md`, **F15**: *"`rpp98_measure.py:66-71` reads the sealed ledger for `ADMISSIBLE` and takes `os.path.basename(d["path"])` — it reads `d["sha256"]` never."* Sixteen of sixteen findings accepted; the mission withdrawn. Two missions later the same line is written again against the same archives.

I closed it: 123/123 sha256 match, 0 missing, byte sizes match, `integrity_ok` true everywhere, all fidelity fields pass, 41 unique indices and seeds, prefix bit-identical. Nothing is wrong with the data. What is wrong is that OMLDCT03 does not know that.

---

### F6 — OMLDCT03's code cannot reach the fourth frozen terminal. **LATENT, not triggered.**

Three line-level departures from the code the docstring says is "recopiee de `omldct02_c3_raw.analyse()`":

| | `omldct02_c3_raw.analyse()` | `omldct03_frozen_test.main()` |
|---|---|---|
| guard | `res = decide(...) if not undefined else None` (:162) | `res = decide(...) if (not undefined and n >= MINIMUM_VALID_PAIR_COUNT) else None` (:60) |
| fallback terminal | `"OMLDCT02_TECHNICALLY_INVALID"` (:172) | `"INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS"` (:83) |
| disagreement escalation | emits `CLASSIFIER_DISAGREEMENT_INDICES` and `ANY_CLASSIFIER_DISAGREEMENT_ON_A_RETAINED_PAIR` (:167-168) | emits only `DROPPED_INDICES` (:79) |

`omldct02_c3_raw.py:19-21` states the frozen rule: *"Section 11 makes a classifier disagreement on a retained pair a campaign-level technical invalidity, so disagreement is recorded and the pair is not silently dropped."* `omldct02_selftest.py:65-71` records the frozen precedence: *"technical invalidity dominates a positive p … enforced in the runner **and the disposition generator**, before the analysis result is consulted; the analysis object is never allowed to be the last word."*

OMLDCT03 has no runner and no disposition generator — C3, C4 and C5 are collapsed into one script whose analysis object *is* the last word, the technical-invalidity flag is not emitted, and an undefined log difference would be relabelled from a technical invalidity into an accrual shortfall. **Under this code no input can produce `OMLDCT02_TECHNICALLY_INVALID`.** With 0 disagreements, 0 undefined differences and n = 41 none of this fires, so nothing published is affected. But "decide() est appele INCHANGE" is true of `decide()` and not of the pipeline around it.

---

### F7 — Contamination is not enumerated, and the direction of the contrast on these exact 41 seeds was already published. **MATERIAL. It does not corrupt the alpha; it does corrupt the word "confirmatory".**

`OMLDCT03_HUMAN_AUTHORISATION.json` writes: *"la question, l'endpoint, le test, le seuil et la regle des egalites ont ete geles le 25 aout par une mission qui **ne pouvait pas voir ces donnees**."* True of the freeze. Not true of the analyst.

VERIFIED. `TBRT02/out/TBRT02_C4_ANALYSIS.json`, section `12_EXPLORATORY_PAIRED_CONTRASTS`, committed 2026-08-28 — two days before OMLDCT03 — publishes on **these same 41 seeds**, paired by index:

```
SELECTIVE_minus_SHAM_CERTAIN_duration : n 41, median +7700, n_positive 24, n_zero 7, n_negative 10
```

Exact two-sided sign test on 24/10: **p = 0.0243** (I computed it). It is a different duration (the Model C lineage set, not the identity interval), but it is a paired SELECTIVE-minus-SHAM duration contrast on precisely the seeds OMLDCT03 then took to the frozen test, and it points the same way OMLDCT03's result points (25 positive / 16 negative). The same file also publishes `SELECTIVE CERTAIN_duration median 10093` against `SHAM 1791`. And `OMLDCT02_FROZEN_ANALYSIS.json` had already shown both medians positive on 33 pairs of the same endpoint since 2026-08-26.

Two documents demanded that this be written down, and both are cited by OMLDCT03's own lineage:

- `GATE01/out/EDL_PRIOR_ART_MAP.json`, item 2: *"CONTAMINATION. J'ai deja beaucoup vu des archives TBRT02 : C3, C4, C4bis, C5, RPP97, RPP98 et deux retours de checker. **Une section 0 doit enumerer tout cela**, y compris les constats de METHODE et pas seulement les grandeurs — c'est le constat F12 de RPP98."*
- `RPP98_CHECKER_RETURN_VERBATIM.md` F12 (accepted) and `FIMRCC02_CHECKER_RETURN_VERBATIM.md` F11 (accepted).

OMLDCT03's section 0 enumerates the three withdrawals. It does not enumerate a single one of the prior looks at these archives. Third mission running.

**Precisely what this does and does not cost.** It does not inflate the type-I error of the executed test: every design choice — endpoint, statistic, tie rule, alpha, sign convention, retention, threshold — was frozen on 2026-08-25 before the worlds existed, and the only discretion OMLDCT03 exercised was fully determined (all 41 admissible triples, no subsetting). What it costs is the claim of blindness: the decision *to run at all* was taken with the sign of a correlated paired contrast on the same seeds already in hand. And the record contains no alpha-accounting for the fact that this frozen test has now been executed twice at α = 0.05 (33 pairs on 2026-08-26, 41 pairs on 2026-08-30). The first is formally stripped of inferential weight by `OMLDCT02_UNDER_ACCRUAL_INTERPRETATION_RULE.json`, so I do not claim the size is demonstrably above 0.05 — I claim nobody wrote the sentence that establishes it is not.

---

### F8 — The coprimary is not a second endpoint. **MATERIAL for how the AND rule is described.**

VERIFIED: on the 41 paired log differences, Pearson ρ(duration, exposure) = **0.9751**, Spearman **0.9662**, and the two agree in sign in **41 of 41 pairs individually**. (On OMLDCT02's 33: ρ = 0.943.) Mechanically, exposure is the sum of `nY` over an interval whose length *is* the duration, on an object holding 1–6 particles.

Two consequences. The freeze's `PRIMARY_AND_COPRIMARY_COMBINATION = AND_WITH_CONCORDANT_DIRECTION` is presented as a stringency device; at ρ = 0.975 it is barely more stringent than a single test — the intersection-union rule is not buying the protection the design claims for it. And in the other direction, the commit message's *"Les deux medianes sont POSITIVES et **concordantes**"* offers concordance as corroboration. Concordance here is close to arithmetically guaranteed: every individual pair already agrees in sign. It is one endpoint reported twice.

---

### F9 — Governance: the inherited clause block is not re-emitted, the gate was not run, and the freeze is bound by a timestamp. **MATERIAL. Two of these repeat findings already accepted against FIMRCC02.**

I grepped all of `OMLDCT03/`:

- **Inherited clauses: absent.** `FIMRCC01_FINAL_DISPOSITION.json:INHERITED_CLAUSES_RE_EMITTED_VERBATIM` and `LDFMA01/out/HANDOFF_…md §4` both carry `EVERY_SUCCESSOR_MUST_RE_EMIT_THESE_CLAUSES = true`. Not one of `MEASUREMENT_NOT_POINT_SEARCH`, `SECOND_TARGETED_MEASUREMENT_CAMPAIGN`, `MAX_INDEPENDENT_CHECKERS`, `MAX_REVIEW_CASCADES`, `CHECKER_RETURN_WRITTEN_BEFORE_ANY_FINDING_IS_ACTED_ON`, `POST_OUTCOME_SIZE_RETUNING`, … appears anywhere in OMLDCT03. **OMLDCT02 did re-emit them**, in `OMLDCT02_PARENT_BINDING.json`. This is the second half of FIMRCC02's F10, accepted three commits earlier, repeated.
- **GATE01 was not run.** `GATE01/out/` contains `RPP98_PRIOR_ART.json` and `FIMRCC02_PRIOR_ART.json` and nothing for OMLDCT03. The prior-art gate is the procedural instrument built as the answer to RPP98's withdrawal and repaired after FIMRCC02's; the fourth mission in the sequence skipped it. It is arguable that the gate is moot when the mission's whole premise *is* the prior art — but a gate run with "the names of the quantities" is precisely what would have surfaced `TBRT02_C4_ANALYSIS.json §12` and `OMLDCT02_FROZEN_ANALYSIS.json`, which is F7.
- **The freeze is bound by a timestamp, not a hash.** `LE_GEL_APPLIQUE.source = "OMLDCT02/out/OMLDCT02_MASTER_FREEZE.json, 2026-08-25T22:30:05"`. No `FREEZE_CONTENT_HASH`, no `FREEZE_FILE_SHA256`, no `METHODS_HASH`. Neither script reads the freeze file at all — the frozen strings in the result document are **transcribed by hand**, and nothing would catch a mis-transcription. I checked all six: `PRIMARY_ENDPOINT`, `COPRIMARY_ENDPOINT`, `SIGN_CONVENTION`, `ALPHA`, `MINIMUM_VALID_PAIR_COUNT` are exact; `PAIRED_TEST` is truncated, dropping *"; the conditional sign-flip distribution is enumerated by dynamic programming. No normal approximation anywhere."* This is FIMRCC02's F15 bullet ("the parent is bound by a timestamp, not a hash"), accepted, repeated.
- **No code digest and no SHA256SUMS.** `OMLDCT03/out/` holds three JSON files and nothing else; no string matching `sha256` occurs anywhere in the mission. OMLDCT02, TBRT02, LDFMA01 and FIMRCC01 all carry one.
- **Twenty frozen fields are never mentioned**, including `CLAIM_CEILING`, `IT_DOES_NOT_ESTABLISH`, `TERMINAL_VOCABULARY`, `NO_FIFTH_DISPOSITION`, `FORBIDDEN_WORDS_FOR_A_NON_POSITIVE_RESULT`, `MATCHED_DESIGN`, `SUPPORT_REQUIRES`, `ZERO_DIFFERENCE_TREATMENT`. The emitted terminal *is* one of the four frozen strings and no forbidden word is used of the result — the substance is respected; the frozen record of it is not carried forward.
- **A frozen terminal string is mutated in passing.** `OMLDCT03_HUMAN_AUTHORISATION.json:STATUTS_INCHANGES` sets `OMLDCT02_STATUS = "INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__ACCRUAL_REOPENED_UNDER_HUMAN_AUTHORISATION"`, under a freeze that says `NO_FIFTH_DISPOSITION: true`. Cosmetic in isolation; in a file whose subject is the sanctity of the freeze, it is the wrong place to improvise.

**Does the authorisation cover what was done?** For the analysis, yes, explicitly and in advance — count admissible pairs under the frozen criteria first, run only if the count reaches 41, change nothing, no substitute endpoint, no post-treatment restriction. All four honoured. For the accrual, no: the authorisation asserts that no field of the freeze is modified while `ACCRUAL_RULE`, `MAX_PRIMARY_ARM_INSTANCES` and `SEED_SET_HASH` were set aside without being named (F1). The statuses in both output files are internally consistent and correct against their sources, with the one exception above.

---

### F10 — One sentence in the commit message states a non-rejecting point estimate as a fact. **MATERIAL; the JSON is clean, the commit is immutable.**

Commit `9196992`:

> "Les deux medianes sont POSITIVES et concordantes — **l'identite dure plus longtemps dans le bras ou son parent est retire** — mais aucune ne rejette et la regle ET echoue."

The clause between the dashes is a generic present-tense statement about the world, attached to p = 0.246 / 0.348. The surrounding sentence retracts it and the JSON never makes it; `NULL_RESULT_INTERPRETATION` is correct, no forbidden word appears, and the terminal is right. But this is the same genre of sentence OMLDCT02 had to retract in `OMLDCT02_UNDER_ACCRUAL_INTERPRETATION_RULE.json` ("the one place in the record where I let 33 pairs speak as if they were 41"), pointed the other way. Given F3, it is also the reading the structure of the endpoint least supports.

The opposite error — a real signal buried under a null label — I looked for and did not find. The AND rule fails in every specification I could construct, including the two restrictions that favour it most and the illegitimate 74-pair pool. What the data actually support, stated in the units the freeze uses: **Hodges-Lehmann 1.40× on duration, distribution-free 95 % interval 0.79× to 2.31×; 1.37× on exposure, interval 0.73× to 2.40×.** A 2.3-fold increase in the locked daughter's post-intervention identity duration is not excluded by this test, and neither is a 21 % decrease. That sentence is missing from the artefact, and it is the one a reader needs. Related: the terminal string ends `INCONCLUSIVE_UNDER_FROZEN_POWER` and nothing in OMLDCT03 says what the frozen power was — `LDFMA01/out/HANDOFF_…md` publishes it at n = 41 (0.402 at the Wilson lower bound, 0.971 at the point estimate, 1.000 at the upper).

---

### F11 — Minor, all verified, none load-bearing.

- `omldct03_admissibility.py:35-37` reads both ledger shards with no de-duplication and no uniqueness assertion. Safe here (885 rows, 41 admissible, 41 unique — I checked), but the frozen `one_base_seed_contributes_at_most_one_valid_paired_observation` is asserted nowhere in the code. Same as RPP98's F16 third bullet.
- `omldct03_frozen_test.py:68` copies `adm["ADMISSIBILITY_CONTENT_HASH"]` forward without recomputing it. It is a transcription, not a binding. (I recomputed it; it holds.)
- If TBRT02 had yielded more than 41 admissible triples, `seeds()` would have used all of them rather than the first 41 in index order as the frozen accrual rule directs. Not triggered — there are exactly 41.
- `work/omldct03_pairs.json` — the durations — was committed in `de74719`, a commit whose message is about `ACTIVE_MISSIONS` durability. The commit-order discipline the mission rests on is real (the count in `384333f` contains no duration, and the durations land after the result), but the file was written by the same process that wrote the count, so the separation is a commit-graph discipline and not an information barrier. Slipping it into an unrelated commit undercuts the one thing that discipline is for.
- `E3_EXPOSURE_SYMMETRIC_VARIANT` is computed by the frozen classifier expressly so the `t_m`-inclusive window "is measured, not assumed away", and is never reported. I measured it: p = 0.3348 against 0.3479. Immaterial.
- Nominal coverage of the reported interval (0.95034) is not stated, and the interval's null is built from untied ranks while the p-value uses Pratt midranks. Identical here; a latent trap for any successor whose data contain zeros — as OMLDCT02's 33-pair run did.

---

## VERIFIED BY COMPUTATION vs SUSPECTED

**Verified, by my own code, from the archives and committed files:**
41/41 pairs and 82/82 arms reproduce on duration, exposure and termination type under an independent components/centroid/link/identity implementation. All published statistics reproduce exactly, p as exact rationals. Interval coverage 0.95034; test-inversion region (w[279], w[581]). 123/123 archive sha256, sizes, `integrity_ok`, `steps_executed`. Fork and intervention fidelity on all 41 triples. Bit-identical prefix through `t_m` across all three arms of all 41 triples, every array. Seed disjointness: 0 overlap on 1030 vs 3080, and 0 among the 885 consumed. All 39 `METHODS_HASH` files byte-unchanged; 8/8 shared method files identical across the two freezes; law bits identical; out-of-repo engine copies identical. `daughter_cells` = `locked_daughter_cells` in 41/41 × 3 arms; `daughter_cells_before`/`_after`/`removed_Y` absent from all 123 metas. A/B agreement on every field in 82/82 arms. Termination mix 32/9/0/0 and 28/0/7/6; all 9 SELECTIVE extinctions absorbing; all 6 SHAM `OUT_OF_RANGE` opened individually. 99.6 % vs 6.4 % single-component occupancy. Extinction 12/41 vs 2/41 after `t_m`; always-survivor stratum n = 28. Endpoint collinearity ρ = 0.9751, sign agreement 41/41. Sensitivity table above. TBRT02 recosted two-arm: 571.649 total, 512 exhausts at index 789 with 38 pairs. TBRT02 C4 §12 sign test p = 0.0243. All three OMLDCT03 content hashes. Frozen classifiers re-run on 12 arms, records bit-identical. No horizon truncation. Symmetric exposure variant p = 0.3348. Repository clean throughout.

**Suspected, not verified:**
That the observed positive point estimate would survive a properly specified competing-risks analysis. I have shown the raw contrast is a mixture; I have not estimated a cause-specific or composite effect, and I am not authorised to invent one here.
That the decision to bring TBRT02 to the frozen test was influenced by the direction already published in TBRT02 C4 §12 and OMLDCT02's 33 pairs. The exposure is documented and dated; the counterfactual is not observable.
That a two-arm rerun of TBRT02's seeds would produce byte-identical SELECTIVE and SHAM archives. The code path is clean by inspection (independent deepcopies, read-only `sp`, no global RNG, verified identical prefixes), but I did not re-execute the engine — that would be a scientific-scale construction and the guard forbids it.

**Not checked:** the DISPLACED arm beyond its non-interference; anything in TBRT02's C4/C4bis/C5 lineage adjudication beyond reading it for prior-art purposes; whether the 37 even-indexed and 0 odd-indexed seeds TBRT02 left unattempted past index 827 would have yielded further admissible triples.

---

## VERDICT

**Is the executed test a valid execution of the frozen design?**

The frozen *analysis* — endpoints, classifiers, retention, sign convention, log handling, Pratt ranking, exact enumeration, alpha, the intersection-union rule, the terminal vocabulary — was executed unchanged, on data that satisfies every matching, fidelity, disjointness and integrity requirement the design states, and every number published is correct. I attacked this for hours with independent code and found no arithmetic error, no silent deviation in retention, no wrong daughter set, no classifier substitution, no contaminated seed, no horizon artefact, no illegitimate termination string. **Say it plainly: the numbers are right and the analysis is the frozen one.**

The frozen *design* was not executed, in one specific and load-bearing respect: its accrual rule. `MINIMUM_VALID_PAIR_COUNT = 41` was reached, but by a sampling frame the freeze does not name, under a budget the freeze does not permit, after the freeze's own stopping rule had already fired and produced OMLDCT02's terminal. Applied to these very seeds, that rule fires again at 38 pairs. OMLDCT03 is therefore best described as *OMLDCT02's frozen statistical procedure, executed at its required n on a new matched sample obtained outside its accrual rule* — which is a real and defensible thing to have done, and is not what the artefacts and the commit message say was done.

Set against that, two substantive scientific caveats the mission does not carry: the endpoint's termination hazard is structurally different between the arms because the intervention removes the object that supplies the competing component (F3), and the raw contrast mixes a positive effect among surviving worlds with a negative one among the 9 the treatment kills (F2) — the confound the operator himself listed, in writing, two hours earlier, as the first thing to neutralise before publishing. Neither changes the terminal string, which is robust to every specification I could construct. Both change what the terminal string means.
