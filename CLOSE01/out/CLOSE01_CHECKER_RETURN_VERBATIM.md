# ADVERSARIAL CHECKER RETURN — CLOSE01

**Scope.** Repository `/home/claude/edl` at `8c571a0` (the dossier was generated at `37030e4`, committed at `730be40`). The 123 sealed `.npz` archives are absent from this container, as expected; CLOSE01 opens none, and neither did I. Nothing under any mission directory was modified; all scratch in `/tmp`. Every figure marked VERIFIED below was recomputed by me from the committed files, most of it with code that imports nothing from this repository except `omldct02_hashes` for the two content digests.

**Headline.** The arithmetic transcription is clean — I could not break a single number that CLOSE01 copies out of a source file, and both content hashes reproduce. The defects are elsewhere and they are severe: the closure's own one-sentence summary is false against a mission the closure itself cites two paragraphs later; the "wall is arithmetic, not a power problem" claim is false as stated and drops the qualifier that the cited source put in its own status string; the single most informative number in the executed test's record (duration `p = 0.0433` in the stratum where the confound is absent) is suppressed while the reserve that points the other way is kept; and section 4 credits the author with guards that were pre-existing artefacts he breached. A successor reading CLOSE01 instead of the 435 files would come away with a materially wrong picture of what the programme established, of why it stopped, and of what could still be done with the data that already exist.

---

## PART A — WHAT REPRODUCED

Stated first, because it is a lot, and because the failures below are not failures of transcription.

- **Section 1, every figure.** `FIMRCC01/out/FIMRCC01_ENDPOINT_ADJUDICATION.json`: `E0.STATUS` = `["SATURATED","NON_DISCRIMINATING","NOT_ELIGIBLE_AS_PRIMARY"]`; `E0.evidence.worlds` = `"22/22 FUNCTIONAL among removal worlds"`; `k_among_removed_worlds` `"1/22"`; `world_level_rate` `"1/256"`; `world_level_point` `0.00390625`; `ratio_to_F_INTEGRATED` `1.2201`; `P_K_GE_2_AT_N50_WORLD_LEVEL` `0.0165`. All six match the dossier byte for byte. I re-derived them independently: `P(X≥2 | n=50, p=0.00390625) = 0.0165089`, `0.00390625 / 0.0032015171 = 1.2201247`. Both reproduce.
- **Section 2, every figure.** I reimplemented Pratt midranks and the exact conditional sign-flip enumeration in `Fraction` and got `W⁺ = 521.0`, duration `p = 0.24638633591985126`; `W⁺ = 504.0`, exposure `p = 0.34791725337890966` — identical to the published values. `exp()` of the frozen HL and interval endpoints gives 1.395 / [0.788, 2.309] and 1.372 / [0.733, 2.396], exactly as printed. `N_PAIRS_RETAINED = 41`, `AND_RULE_PASSES = false`, `n_zero = 0` all correct.
- **Section 3, TLMR01 sums.** `sum(M1_by_occupancy[*].k) = 8292`, `sum(...n) = 1541980`, `sum(M2...n) = 16368`, `sum(M2...k) = 44`, `M4.median_horizon_fraction_single_centre = 0.7496818181818181`. All four sums recomputed and correct (see F9 for what they *mean*).
- **Section 3, CLEA01.** `CLEA01_CAUSAL_KERNEL_ADJUDICATION.json`: `consecutive_row_pairs_compared = 668041`, `cells_with_no_Moore_1_predecessor = 0`, `VERDICT = "EXACT"`. Correct.
- **Section 4, finding counts.** RPP97 `FINDINGS_ACCEPTED = 15`, `FINDINGS_REJECTED = 0`; RPP98 `N_ACCEPTED = 16 / N_REJECTED = 0`; FIMRCC02 `16 / 0`. All three correct. The three withdrawal status strings are byte-identical to their sources.
- **Provenance.** The four checker-verbatim sha256 all match (`sha256sum` on each file). `git rev-list --count 06c5923..37030e4 = 156`, which is exactly what the script would have read at generation time. `123` archives and `41` admissible triples both recomputed from `TBRT02/work/TBRT02_SEALED_LEDGER_{0,1}.jsonl` (885 rows, 41 `ADMISSIBLE`, 123 distinct archive paths). "28 rollbacks" matches the commit log (`b62c79e`, "28e retour arriere"). `METHODS_HASH 21571fb4…` matches `TBRT02_C4_ANALYSIS.json`.
- **Both content hashes.** `CLOSURE_CONTENT_HASH = 3a7489c5…` and `AUTHORISATION_CONTENT_HASH = 3486ab36…` recompute under `omldct02_hashes.content_digest`.
- **The accrual reserve is honest and independently confirmed.** Recosting the 885-row ledger by cumulative `instance_cost` in index order, the 512-instance ceiling exhausts at index 738 with **36** admissible pairs — a third figure alongside the operator's 760/36 and the checker's 789/38, and the invariant holds under all three: the frozen stream exhausts before 41 pairs.
- **No status is silently changed.** All six statuses in section 5 match every source I checked. Section 4's three terminal strings match. The defect is omission, not mutation (F19).

---

## PART B — FINDINGS

### F1 — "le seul test confirmatoire pre-enregistre du programme" is false, and the dossier's own section 3 contains the counter-example. **LOAD-BEARING: it is the closure's one-sentence summary and it is the premise on which the human was asked to close.**

`LA_CLOTURE_EN_UNE_PHRASE` and the section-2 title both assert that OMLDCT03 is *the only* pre-registered confirmatory test of the programme, executed and null. `CLOSE01_HUMAN_AUTHORISATION.json:LA_QUESTION_POSEE_VERBATIM` puts the same sentence to the owner: *"le seul test confirmatoire pre-enregistre du programme a ete execute a son effectif requis et ne detecte pas d'effet."*

`/home/claude/edl/FDFLT01/out/FDFLT01_MASTER_FREEZE.json` (2026-08-20T23:59:35) carries `FREEZE_IS_COMMITTED_ALONE_BEFORE_ANY_SCIENTIFIC_START: true`, `COMPLETE_PRE_RUN_METHODS_HASH: "PASS"`, `DECISION_RULE = {PRIMARY_N: 192, PRIMARY_NULL_RATE: 0.1, PRIMARY_ALPHA: 0.05, PRIMARY_CRITICAL_SUCCESS_COUNT: 27, REJECT_H0_IF: "SUCCESS_COUNT >= 27"}`, an `OUTCOME_FIREWALL`, a `CLAIM_CEILING`, three frozen `TERMINAL_DISPOSITIONS` and `MAX_POST_OUTCOME_SCIENTIFIC_REPAIRS: 0`. `/home/claude/edl/FDFLT01/out/FDFLT01_FINAL_DISPOSITION.json` records it executed at its planned N: `PRIMARY_SUCCESS_COUNT: 53`, `PRIMARY_EXACT_P_VALUE: 5.255896417897822e-12`, `PRIMARY_EXACT_TEST_REJECTS_H0: true`, `TECHNICALLY_VALID: true`.

That is a pre-registered confirmatory test, executed at its required N, which **rejected its null** — and CLOSE01 lists it, in its own section 3, as `"point_de_lignee_qualifie": "FDFLT01, taux de succes superieur a 0,10"`. The document contradicts itself between section 3 and its own headline.

Two further executed pre-registered adjudications are equally excluded by the word "seul": TBRT02's frozen refutation condition with its pre-registered sequential bound (`TBRT02_C4_ANALYSIS.json:8_…`, `preregistered_value_at_n_41 = 0.070461`), executed and found uninformative; and OMLDCT02's own execution of *this same frozen procedure* on 33 pairs on 2026-08-26 (`OMLDCT02_FROZEN_ANALYSIS.json`, both medians positive), which OMLDCT03's checker flags in F7 as an un-accounted second execution at α = 0.05.

The defensible sentence is "the only executed pre-registered *matched-control paired* test of the locked daughter". The sentence written is a claim of uniqueness across the programme, made without the anteriority search that exists in this repository precisely to prevent it — which is the failure mode that withdrew RPP98 and FIMRCC02. This is the fourth instance.

---

### F2 — "aucun effectif ne repare un rapport de 1,22" and "ce n'est pas un probleme de puissance" are false as stated, and the dossier drops the qualifier its own source put in the status string. **LOAD-BEARING: the disposition is named `PROGRAMME_CLOSED_ON_A_QUANTIFIED_INSTRUMENT_LIMIT` on this claim, and legacy item 1 instructs the successor on it.**

`FIMRCC01_ENDPOINT_ADJUDICATION.json:E1_E2.STATUS` is `["CLAIM_ALIGNED", "NOT_DECISION_CAPABLE_AT_THE_FROZEN_N"]`. The source scopes the incapacity **to the frozen N, in the status string itself**. CLOSE01 reproduces six fields from that object and omits the `STATUS` — the one field that contradicts the conclusion it then draws.

VERIFIED by computation. The frozen test is `exact one-sided binomial, alpha = 0.05, against F_INTEGRATED` (`FIMRCC01_ENDPOINT_PREREGISTRATION.json:CRITERION_3_POWER`), with `k*` a derived quantity (`k_star_at_n50: 2` in the table, not a constant). Recomputing `k*(N)` and power at `p = 0.00390625` against `F = 0.0032015171`:

| N | k\* | power |
|---|---|---|
| 50 | 2 | 0.0165 (reproduces FIMRCC01 exactly) |
| 10 000 | 43 | 0.2845 |
| 42 000 | 155 | 0.7711 |
| 50 000 | 182 | **0.8390** |
| 100 000 | 351 | 0.9804 |

A ratio of 1.22 with a rate of 0.0039 is **exactly** a sample-size problem: ~5×10⁴ world-runs reach 84 % power. The claim "no larger N repairs it" is true only under the other reading — that `K ≥ 2` is frozen as a constant independent of N — and under *that* reading the test's size also tends to 1, so the criterion is broken, not "unrepairable by N". Either way, `"ce n'est pas un probleme de puissance, c'est un probleme de separation entre le signal et le plancher"` is wrong, and it is stated twice: once in section 1 and once, more strongly, in the legacy.

The true and far more useful sentence, which the record supports and the closure does not write, is: *repairing this endpoint on the world-run denominator needs roughly 5×10⁴ world-runs, about fifty times the programme's own declared affordability ceiling* (TLMR01's eligibility clause `E6_confirmation_affordable_at_or_below_1024_worlds`). That is a resource limit, quantified. What CLOSE01 asserts instead is an arithmetic impossibility, and it hands that assertion to the successor as the first thing they must believe.

---

### F3 — The dossier reports `0.0165` and suppresses the `0.6697` sitting on the adjacent line of the same JSON object, and never states the 8.6 % trigger yield that generates the whole wall. **LOAD-BEARING.**

`FIMRCC01_ENDPOINT_ADJUDICATION.json:E1_E2` publishes **two** assurance figures for the same endpoint at the same n = 50:

```
P_K_GE_2_AT_N50_WORLD_LEVEL              0.0165
P_K_GE_2_AT_N50_REMOVED_WORLD_DENOMINATOR 0.6697
```

I verified both: `P(X≥2 | 50, 0.00390625) = 0.016509`, `P(X≥2 | 50, 0.0454545) = 0.669730`. CLOSE01 copies the first and omits the second — a figure forty times larger, on the same endpoint, from the same object, published by the same file.

The reason the two differ is stated plainly in the record and never appears in the closure: `LDFMA01/out/HANDOFF_ONE_MATCHED_LOCKED_DAUGHTER_CONTROL_TEST_01.md` — *"TRIGGER YIELD = 22 of 256 LAW_C worlds, 8.6 %"* — and `LDFMA01_MATCHED_CONTROL_ENDPOINTS.json:49`, *"only 22 paired blocks are expected from 512 primary arm instances, because just 8.6 % of LAW_C worlds ever reach a removal."* The "wall" is, arithmetically, the statement that 91.4 % of the engine work produces no informative unit.

I do not claim the 0.6697 route is usable as it stands — the pre-registration says a candidate on a different denominator "must state its own floor or be struck under criterion 1", and no such floor exists. That is precisely why it needed to be *stated and disposed of*, not silently dropped. A closure that rests its whole disposition on one assurance number owed the successor the second one and a sentence on why it does not help.

---

### F4 — `CE_QUE_LE_MUR_EXPLIQUE` generalises one endpoint's failure into an exoneration of the entire terminal record, against the operator's own inventory. **MATERIAL, and self-serving.**

CLOSE01: *"la longue serie de dispositions terminales en « non identifiable », « insuffisant », « sous-puissant » ou « techniquement invalide » n'est pas un defaut de soin. C'est le meme obstacle rencontre par des routes differentes."*

`GATE01/out/EDL_PRIOR_ART_MAP.json:CE_QUI_EST_RETIRE_INVALIDE_OU_EN_PAUSE` — the operator's own list — includes `OBTC01: "AUDIT_INVALID"`, `MCM01: "MINCORE_CLOUD_MAINTENANCE_FAIL"`, `ORR01: "CRITICALITY_STATUS = NOT_VALID"`, `PQEC01: "PROSPECTIVE_Q_ENVIRONMENT_OPERATOR_NOT_IDENTIFIED__ADDITIONAL_INSTRUMENTATION_REQUIRED"`, `OMLDCT01: "OMLDCT01_TECHNICALLY_INVALID"`, and the three withdrawals. None of these is the 1.22× floor ratio. Two are instrument or infrastructure failures; one is an unidentified operator; three are the author's own judgment errors, catalogued at length in the dossier's own section 4. INV01, from which this sentence descends, at least hedged with *"la grande majorite"*; CLOSE01 removes the hedge and adds *"n'est pas un defaut de soin"* — a blanket absolution of a record that section 4 then documents as containing 47 accepted findings across three withdrawn missions.

FIMRCC01's own `THIS_IS_NOT` list (`"evidence that the phenomenon is impossible"`, `"evidence that the architecture cannot support it"`, `"a negative fresh confirmation"`, `"a reason to reinterpret TLMR01 retrospectively"`) and its `FINAL_DISPOSITION = CONFIRMATION_PRECONDITIONS_NOT_MET__LINEAGE_ROUTE_PAUSED` are both absent from section 1.

---

### F5 — OMLDCT03's accepted finding F7 — the contamination, and the `p = 0.0243` contrast published on these exact 41 seeds two days earlier — is absent from the closure entirely. **LOAD-BEARING for the words "pre-enregistre" and "confirmatoire".**

`OMLDCT03/out/OMLDCT03_CHECKER_ADJUDICATION.json:FINDINGS.F7_LA_CONTAMINATION_N_EST_PAS_ENUMEREE`, verdict `ACCEPTED`: *"TBRT02_C4_ANALYSIS.json section 12, commite deux jours avant, publie sur CES MEMES 41 GRAINES un contraste apparie SELECTIVE moins SHAM de duree : 24 positifs, 7 nuls, 10 negatifs, test des signes p = 0,0243 — et il pointe dans le meme sens que mon resultat. […] Ce que cela coute, c'est la revendication d'aveuglement : la decision D'EXECUTER a ete prise avec le signe d'un contraste correle sur les memes graines deja en main."*

VERIFIED: `TBRT02/out/TBRT02_C4_ANALYSIS.json:12_EXPLORATORY_PAIRED_CONTRASTS` gives `n_positive 24, n_zero 7, n_negative 10`; the exact two-sided sign test on 24/34 is **0.024306510109454393**.

CLOSE01 carries three reserves on the executed test and this is not one of them. `le_gel.origine` instead reads *"2026-08-25T22:30:05, avant tout monde"* — true of the freeze, and the exact claim the checker singled out as true of the freeze and false of the analyst. A successor reading section 2 is told the test was frozen before the worlds and executed; they are not told that a correlated paired contrast in the same direction on the same 41 seeds was in the repository, published, when the decision to execute was taken. Nor that the same frozen procedure had already been run once at α = 0.05 on 33 pairs, with no alpha-accounting anywhere in the record.

---

### F6 — The executed test's positive point estimate is **not** handled honestly in both directions: the reserve that lowers the estimate is stated, the diagnostic that raises it past α is suppressed. **LOAD-BEARING.**

CLOSE01's first reserve says only that the published figure *"melange un ecart positif chez les mondes que le traitement ne tue pas et un ecart negatif chez ceux qu'il tue."* No magnitude. The magnitudes are in the record and I recomputed all of them from `OMLDCT03_FROZEN_TEST_RESULT.json:PER_PAIR` with my own exact Wilcoxon:

| specification | n | duration p | median ratio |
|---|---|---|---|
| the frozen test, as executed | 41 | 0.24639 | 1.238 |
| **drop the 9 SELECTIVE window-extinctions** | 32 | **0.04333** | **1.882** |
| drop the 7 SHAM MERGE pairs | 34 | 0.29320 | — |
| same termination in both arms | 22 | 0.12068 | — |

Every one reproduces the OMLDCT03 checker's table exactly. The primary endpoint, alone, in the stratum where the named confound is absent, crosses the frozen α with a point estimate of 1.88×.

I accept the principled objection and state it in the same breath: all of these condition on a post-treatment variable, which `FIMRCC01_ENDPOINT_PREREGISTRATION.json` forbids by name and OMLDCT03's authorisation excludes explicitly; the AND rule fails in every specification (exposure never rejects); OMLDCT03 was right to refuse them as results. But CLOSE01 is not OMLDCT03 — it is the terminal record, and it *does* discuss the confound, in a direction that supports "the instrument cannot decide". Reporting the sign of the mixture and withholding the magnitude, when the magnitude crosses the alpha the freeze set, is asymmetric disclosure in the author's own direction. The closure asks the successor to accept a wall; the strongest number in the record pointing away from that wall is the one it does not print.

---

### F7 — `INCONCLUSIVE_UNDER_FROZEN_POWER` is reproduced and the frozen power is still never stated, after a checker pointed at the file. **LOAD-BEARING for a legacy document.**

`OMLDCT03_CHECKER_RETURN_VERBATIM.md`, F10 (accepted): *"the terminal string ends `INCONCLUSIVE_UNDER_FROZEN_POWER` and nothing in OMLDCT03 says what the frozen power was — `LDFMA01/out/HANDOFF_…md` publishes it at n = 41."* VERIFIED at that path:

```
p(SELECTIVE)          power at 41 pairs
0.101 (Wilson lower)  0.402
0.227 (point)         0.971
0.434 (Wilson upper)  1.000
```

CLOSE01 prints the terminal string verbatim and adds nothing. A successor is told a test "did not detect an effect" and is given a distribution-free interval, but not the design's power against the effect it was sized for. This is an accepted finding of the surviving mission, repeated by its closure.

---

### F8 — Section 3's `preconditions_du_test_apparie` attributes an audit of one data set to a different test on a different data set, and attaches the wrong denominator. **LOAD-BEARING: it tells a successor the paired test's preconditions were independently audited. They were not.**

CLOSE01: *"FIMRCC01, A et B toutes deux PASS, fidelite auditee, 26 mondes sur 26."*

`FIMRCC01/out/FIMRCC01_PRECONDITION_B_RESULT.json` ran on `PASS_1_ALL_256_LAW_C_ARCHIVES` — TLMR01's 256 archives, on 2026-08-25. TBRT02's 123 archives did not exist until 2026-08-28. FIMRCC01's preconditions A and B are preconditions of the *fresh binary confirmation on E1/E2*, on an entirely different corpus. Calling them "les preconditions du test apparie" is a scope transfer that the source does not license — and note that INV01, which CLOSE01 is otherwise copying here, wrote only `"preconditions A et B toutes deux PASS"` without the words "du test apparie". The mis-scope was introduced by CLOSE01.

The `26/26` is also mis-attached. In the source, `AGREEMENT.world_level_verdict` is `"26/26"`; the *fidelity* block is `SELECTIVE_REMOVAL_FIDELITY = {Y_conserved: "22/22", WY_gained_equals_Y_removed: "22/22", parent_emptied: "22/22", daughter_untouched: "22/22", rng_unchanged: "22/22"}`. The audited-fidelity denominator is 22, not 26.

And the actual precondition record of the paired test points the other way: `OMLDCT03_CHECKER_ADJUDICATION.json:F5_AUCUNE_PORTE_D_INTEGRITE_N_A_ETE_PASSEE`, verdict `ACCEPTED` — *"c'est le constat F15 de RPP98 mot pour mot"*.

---

### F9 — The TLMR01 entry pools across strata that TLMR01 deliberately resolved, mislabels 16 368 two-centre episode segments as "runs multi-centres", and offers four bare integers under a heading that promises rates. **LOAD-BEARING for section 3.**

From `TLMR01/code/tlmr01_design.py:151` and `tlmr01_offline.py:181`, an M2 record is an **episode**: *"a maximal run of the frozen FDFLT01 state S (exactly two centres, Y occupancy at least two, integrity intact, no third centre)"*, and a new episode begins whenever the world re-enters that state. VERIFIED consequence: the 16 368 M2 rows terminate as `FORMED_A_THIRD_CENTRE 8434`, `MERGED_TO_ONE_CENTRE 7900`, `LOST_A_CENTRE_TO_A_SINGLE_Y 34`. So the count is inflated by the 8 434 third-centre formations, and 16 368 **exceeds** the 8 292 transitions out of the single-centre state that CLOSE01 prints on the line above. Presented side by side with no definitions, the two numbers are arithmetically incoherent: a reader cannot have more multi-centre runs than entries into multi-centre. They are not runs; they are exactly-two-centre segments.

Three further drops:
- **Pooling.** M1's rate ranges from `k=0 / n=104 554` at occupancy 1 to `0.0359` at occupancy 6. The whole point of TLMR01 was occupancy resolution (`"PTOPD01 could not obtain it above the occupation support n = 5 and named it missing"`, `"primary_regime: n > 5"`). CLOSE01's pooled 8292/1541980 destroys exactly the resolution that was TLMR01's contribution.
- **Clustering.** TLMR01 publishes a `world_clustered_95_CI` on every stratum and warns in its design that *"M1, M2, M3 and M4 have units that repeat within a world"*. CLOSE01 gives naive pooled counts with no interval and no clustering note, under the heading `CE_QUI_EST_ETABLI`.
- **Character.** INV01, the direct ancestor of this section, wrote that two of the programme's few positive results are *"structurels (le noyau causal de CLEA01) ou **descriptifs** (les mesures M1-M5 de TLMR01) plutot que confirmatoires."* CLOSE01 drops "descriptifs".

Minor, same entry: `sur_pas_a_un_centre: 1541980` is the M1 denominator; `M4.single_centre_steps_total` is `1542156`. The label is off by the 176 terminal steps with no observable successor.

---

### F10 — The FDFLT01 entry omits the law, the claim ceiling, the estimate and the timing sensitivity. **MATERIAL.**

CLOSE01: *"point_de_lignee_qualifie: FDFLT01, taux de succes superieur a 0,10, 2026-08-21."*

`FDFLT01_MASTER_FREEZE.json:POINT.LABEL = "B1"`, `kY = 2.5118864315095822e-05`, `muY = 9.261187281287937e-05`. `TLMR01_MEASUREMENT_LAWS.json` confirms these are exactly `LAW_A_B1`. **Every other entry in section 3 is at LAW_C_MCTT01**, and the law is never named for this one. At LAW_A_B1, TLMR01 measured its own integrated event at `K = 0, n = 128, ELIGIBLE: false`.

Also dropped: `CLAIM_CEILING = "…exceeds 0.10. Nothing further."`; the actual estimate `0.2760` with `[0.2141, 0.3450]` and `p = 5.26e-12`; and `TIMING_SENSITIVITY.T_90.would_reject_at_p0_0.10 = false` — the result does not survive the latest timing threshold the mission itself tested. Stating only "superieur a 0,10" simultaneously underclaims the effect and overclaims its scope.

---

### F11 — `le_materiel` omits that the third arm is not the arm the pre-registration named — which INV01 required be written "au titre, pas en note". **MATERIAL.**

`GATE01/out/EDL_PRIOR_ART_MAP.json`, `CE_QUI_DOIT_ETRE_FAIT_AVANT_TOUT_GEL` item 3: *"L'ARME EST DISPLACED, PAS GLOBAL_OFF. FIMRCC01 exigeait SELECTIVE, SHAM et GLOBAL_OFF. TBRT02 fournit SELECTIVE, SHAM et DISPLACED. […] le troisieme bras n'est pas celui que le pre-enregistrement nommait, et cela doit etre ecrit au titre, pas en note."* `FIMRCC01_FINAL_DISPOSITION.json` carries `GLOBAL_OFF_ARM_EXECUTED: false`; `TBRT02_MASTER_FREEZE.json:ARMS = ["SHAM","SELECTIVE","DISPLACED"]`, with DISPLACED described in its own freeze as *"a teleport: no engine channel moves mass across the lattice in one step"* and `DISPLACEMENT_IS_MORE_INVASIVE_THAN_REMOVAL`.

CLOSE01 names no arm at all, and omits that TBRT02's own primary adjudication is `2_WHAT_THE_MISSION_ADJUDICATES: {"ANSWER": "NOTHING."}` because its frozen refutation condition could not fire.

---

### F12 — Section 3's "six entries" are not INV01's six: one established result is deleted and replaced without a note, and the deleted one is the only one carrying a reserve. **MATERIAL.**

`EDL_PRIOR_ART_MAP.json:CE_QUI_EST_ETABLI` has six entries: CLEA01 kernel, TLMR01 M1–M5, FDFLT01, FIMRCC01 preconditions, **OBFOR01_OPERATEUR** (`"FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_QUALIFIED"`, `reserve: "HISTORICAL_WINDOW_STATUS = NOT_PORTABLE"`, `force: "qualifie sous reserve"`), TBRT02 material.

CLOSE01's section 3 has six entries: the same five, with OBFOR01 deleted and `le_test_execute: OMLDCT03` substituted. The count matches; the content does not. The entry removed is the one the inventory flagged as qualified *under a NOT_PORTABLE reserve*, and `HISTORICAL_WINDOW_STATUS` appears nowhere in CLOSE01. A successor comparing the two documents sees "six entries" in both and has no way to know one was swapped out.

---

### F13 — "Le calcul etait juste a chaque fois" is false, and "les trois retraits ont la meme cause" flattens a distinction the sources draw. **MATERIAL, and self-serving.**

`RPP97_CHECKER_ADJUDICATION.json`:
- `F6_THE_CENTROID_IS_FLOORED_NOT_AVERAGED`: *"ACCEPTED. My bit-identity claim is FALSE. […] rpp97_stats.centroid_frozen uses `soy // m`; the frozen centroid is a true mean, `soy / m`. […] differs in 6.1 per cent of window component-steps, 64.6 per cent over the horizon."* That is a computation that was wrong.
- `F11`: *"c_cand stores round(1e6 * min(1, kY*nX*nY)) — a capped, scaled, rounded PROBABILITY, not the propensity […] and not the birth propensity at all, which carries the min(nSY, free) factor I dropped."*
- `F10`: *"I wrote 'nX_total RISES' and cited 272 at t_m-250 then 252 at t_m-1 — a FALL."*
- `F9`: *"Nothing in the repository produces RPP97_RESULT.json; its tables came from uncommitted ad-hoc code."* The arithmetic is not even reproducible from the repository.

`FIMRCC02_CHECKER_ADJUDICATION.json`: `F7_MA_BORNE_SUR_LES_EGALITES_DE_E4_EST_FAUSSE_QUATRE_FOIS`; `F2` — the published `p = 0.0063` was a tail point presented as the rule, with the correct figure `P_rejet_a_alpha_0.05 = 0.2858`; `F16_n_zero_steps__JUSTE_PAR_CHANCE`.

"Every figure I rechecked reproduced" (RPP97's own phrasing) means the published numbers can be recomputed from the author's code. CLOSE01 upgrades that to "le calcul etait juste", which is a different and false claim.

On "the same cause": FIMRCC02's own adjudication quotes the checker drawing the opposite distinction — *"RPP97 et RPP98 ont publie des affirmations fausses sur des donnees qu'elles avaient lues ; FIMRCC02 a publie des affirmations fausses sur des donnees qu'elle n'avait PAS lues."* CLOSE01 merges three distinct failure modes (mis-specified mechanism / prior art + wrong counted event / false premise + reopening without authorisation) into one flattering diagnosis — "I chose the question myself and was wrong" — which happens to be the diagnosis that leaves the author's arithmetic and method intact.

---

### F14 — "la garde produite": FIMRCC02 is credited with two guards that were pre-existing artefacts it *breached*, and the other two guards' documented failures are omitted. **LOAD-BEARING for section 4, which exists to record what was learned.**

**FIMRCC02.** CLOSE01: *"la garde produite: l'exigence d'une autorisation humaine explicite pour rouvrir une route, et le test lui-meme."* Both are false.
- The requirement is in `FIMRCC01/out/FIMRCC01_FINAL_DISPOSITION.json:REOPENING_REQUIRES = "an explicit new human authorisation and a newly derived matched-control design"`, dated 2026-08-25. FIMRCC02 did not produce it — `FIMRCC02_CHECKER_ADJUDICATION.json:F10_GOUVERNANCE__J_AI_ROUVERT_SANS_AUTORISATION` (ACCEPTED, `gravite: PORTANTE`) records that FIMRCC02 **violated** it.
- "le test lui-meme" is `OMLDCT02_MASTER_FREEZE.json`, dated 2026-08-25T22:30:05, five days before FIMRCC02. FIMRCC02 did not produce it either; its fatal finding F3 is that it declared the test non-existent while it sat in the repository.

**RPP97.** CLOSE01 credits it with *"tester toute statistique contre le temps absolu et contre l'exposition avant publication."* `RPP98_CHECKER_ADJUDICATION.json:LE_CONSTAT_SUR_MOI…`: *"J'ai ecrit les sections 0, 3 et 4 de RPP98 specifiquement pour ne pas repeter les quatre echecs de RPP97, et trois des quatre sont revenus : le temps absolu (F5), la statistique non normalisee (F6), la fenetre vide par construction (F7)."* The guard is presented as produced; the record says it failed one mission later.

**RPP98.** CLOSE01 credits GATE01 as *"une porte d'anteriorite mecanique et opposable."* `FIMRCC02_CHECKER_ADJUDICATION.json:F6_MA_PORTE_D_ANTERIORITE_EST_DU_THEATRE_TELLE_QUE_JE_L_AI_UTILISEE` (ACCEPTED, PORTANTE) — the gate skipped `GATE01/` and `review/`, its "at least two terms" rule had no notion of rarity, and *"ce que la porte aurait donne avec les bons termes: 28 fichiers […] dont un seul suffisait a interdire le gel."* It was then repaired by the checker's finding (`MIN_FLAGGED = 10`, `MIN_DISTINCT_REASONS = 5`, `review/` included — all annotated "Constat F6, adopte" in `GATE01/code/edl_prior_art_gate.py`), and then skipped entirely by the next mission (`OMLDCT03_CHECKER_ADJUDICATION.json:F9`, *"GATE01 n'a pas ete passee"*). None of this appears in section 4.

---

### F15 — Legacy item 4 restates the mortality framing the operator's own adjudication retracted, and contradicts the dossier's own section 2 without saying so. **MATERIAL.**

CLOSE01 legacy: *"le retrait eteint l'espece dans 12 des 41 mondes traites contre 2 temoins."*

`FIMRCC02_CHECKER_ADJUDICATION.json:CE_QUI_EST_RETIRE` includes *"la suggestion finale sur la mortalite differentielle : elle est post-hoc et **le chiffre est 11 contre 1**"*, and the finding body: *"le contraste **cause** est 11 extinctions et 1 sauvetage sur 41 graines, pas 12 contre 2 : la graine 793 est morte dans les deux bras et 780 seulement en SHAM."* The marginal counts 12 and 2 are correct (RPP97 checker item 7: `SELECTIVE 12, DISPLACED 5, SHAM 2`); the causal verb "le retrait eteint … dans 12 … contre 2" is the framing that was withdrawn.

Separately, section 2 tells the successor "9 sur 41 contre 0" and section 6 tells them "12 sur 41 contre 2", for what reads as the same phenomenon, with no word on the different windows (in-window daughter extinction vs whole post-`t_m` trajectory). And `DISPLACED 5` is dropped.

The same item asserts the mortality *"n'a jamais fait l'objet d'une etude propre."* `FIMRCC02_CHECKER_RETURN_VERBATIM.md` measured the alive fractions by arm (0.954 / 0.718 / 0.891, min 0.002), identified `n_zero_steps` as the correct graded exposure denominator, and named the correct frame — **competing risks**, with its two standard answers, cause-specific analysis or an ordered composite. None of that is in CLOSE01.

---

### F16 — Legacy item 5 gives the successor the less dangerous of GATE01's two documented failure modes. **MATERIAL.**

CLOSE01: *"des termes vagues signalent deux cents fichiers et la porte est contournee."* That is supported — `GATE01/code/edl_prior_art_gate.py` docstring: vague terms → *"203 fichiers signales. Un operateur devant 203 lignes ne lit rien."*

The failure that actually happened is the other one, and is hard-coded into the gate as the fix: *"la regle « au moins deux termes » n'a aucune notion de rarete : deux termes obscurs donnent zero fichier signale et **la porte PASSE**"* — plus the gate being blind to `GATE01/` and `review/`, where the checker returns live. A gate that produces a false PASS is the mode a successor needs warned about. (Incidental source inconsistency, not CLOSE01's: the docstring says the right terms gave "26 fichiers"; the committed `GATE01/out/RPP98_PRIOR_ART.json` says `N_FLAGGED: 25`.)

---

### F17 — The legacy omits everything the record says a successor could actually DO, including two routes on the existing raw. **LOAD-BEARING: this is the section whose entire purpose is the handoff.**

`TBRT02/out/TBRT02_C5_CLOSURE.json:6_WHAT_A_SUCCESSOR_COULD_DO_WITH_THIS_RAW_WITHOUT_A_NEW_WORLD`:
1. *"pre-register the body-level condition in code, with a capability test, and read it on these 41 triples as a genuine test — the archives already carry c_cid"*
2. *"the core-depletion spot-division mechanism comparison (Reynolds, Ponce-Dawson, Pearson 1997), measurable on the per-step component and free-capacity series already archived"*

And `5_THE_BEQUEST.PRIMARY`: *"a successor's refutation condition must be OPERATIONALISED IN CODE before the first world, not merely stated in words — and it must ship with a CAPABILITY TEST […] A condition that has never been shown capable of firing is not a test."* That is arguably the most transferable lesson in the programme — an entire frozen primary adjudication returned `ANSWER: NOTHING` because of it — and it is not among CLOSE01's six legacy points.

Add the competing-risks frame from F15 and FIMRCC01's `E3/E4/E5 = FUTURE_QUESTION_RECORDED__NOT_AUTHORISED` (still the live status per `OMLDCT03_CHECKER_ADJUDICATION.json:STATUTS`, and dropped from CLOSE01's section 5). The successor is told the wall is arithmetic and offered exactly two moves — find a different observable, or *establish* an architecture change. The record names at least four concrete things they could do first, three of them on data that already exist. The human owner was likewise offered three routes, none of which was any of these.

---

### F18 — Provenance is stated in the present tense for a verification the repository's own gate currently records as impossible, and the closure never tells the successor where the data and the history actually live. **LOAD-BEARING for a terminal record.**

CLOSE01 `PROVENANCE`: *"archives_scellees: 123, verifiees au sha256 contre le registre scelle"*; sections 0 and 7: *"les 41 triplets et les 123 archives restent scellees et verifiables."*

`GATE01/out/OMLDCT03_INTEGRITY.json` — the most recent committed run of the programme's own integrity gate — reads:

```
OCTETS: {sha256_match: 0, sha256_mismatch: 0, missing: 123}
ALL_ARCHIVE_HASHES_MATCH: false
ALL_CONTENT_CHECKS_PASS:  false
INTEGRITY_GATE_PASSES:    false
```

The verification did happen historically (OMLDCT03's checker: 123/123, 0 mismatches; RPP98's adjudication likewise). But the terminal record asserts it in the present, and the one machine-checkable artefact in the repository says it cannot currently be performed. This figure is a hard-coded string in `close01_dossier.py`, not read from the gate.

Worse, the closure is silent on the fact recorded one commit earlier, in `TBRT02/out/TBRT02_RECOVERY_20260830_D.json`: *"le point faible n'est pas la redondance des donnees […] mais le fait que l'historique git ne vit que sur le disque de l'operateur : le document du Projet porte les fichiers et pas la provenance. **Ce n'est pas corrige ici et c'est note comme tel.**"* The 123 archives exist as 41 tars on one person's Windows disk; the entire git history — every hash, every checker verbatim, all provenance — exists on that same disk. A closure whose stated purpose is a legacy does not mention its own single point of failure.

---

### F19 — Governance: the inherited-clause block that two frozen texts require of every successor is not re-emitted, and the closure quotes OMLDCT03's superseded terminal rather than its post-adjudication status. **MATERIAL, and a fifth repetition of an accepted finding.**

- `FIMRCC01_FINAL_DISPOSITION.json:INHERITED_CLAUSES_RE_EMITTED_VERBATIM` carries `EVERY_SUCCESSOR_MUST_RE_EMIT_THESE_CLAUSES: "true"`; `LDFMA01/out/HANDOFF_…md §4` says the same. CLOSE01 re-emits none of them. This is `OMLDCT03_CHECKER_ADJUDICATION.json:F9` bullet 1, accepted, which was itself the second half of FIMRCC02's accepted F10.
- Section 2 prints `TERMINAL: "MATCHED_LOCKED_DAUGHTER_CONTROL_EFFECT_NOT_DETECTED__INCONCLUSIVE_UNDER_FROZEN_POWER"`, read from the pre-adjudication result file. The adjudication's own `OMLDCT03_STATUS` is `"FROZEN_STATISTICAL_PROCEDURE_EXECUTED_AT_ITS_REQUIRED_N_ON_A_MATCHED_SAMPLE_OBTAINED_OUTSIDE_ITS_ACCRUAL_RULE__EFFECT_NOT_DETECTED__INCONCLUSIVE"`, and `CE_QUI_EST_RETIRE_DE_MES_PROPRES_FORMULATIONS` explicitly withdraws *"le test GELE d'OMLDCT02 est EXECUTE"* as too broad. CLOSE01 puts the accrual reserve in a separate key and then reproduces the superseded string as the terminal — and titles the section `LE_SEUL_TEST_CONFIRMATOIRE_EXECUTE`.
- Section 5's `REMARQUE` says the statuses *"sont rapportes sans condition a chaque mission precisement pour qu'ils ne se deplacent jamais par inadvertance"* — while dropping, relative to OMLDCT03's own list: `FIMRCC01_E3_E4_E5_STATUS`, `COMPANION_PAPER_V1_1_STATUS`, `OMLDCT02_STATUS`, `CLEA01_STATUS`, `TBRT02_STATUS`, plus `HISTORICAL_WINDOW_STATUS = NOT_PORTABLE`, `FINITE_SIZE_RELEVANCE = NOT_SUPPORTED` and `PTOPD01_LINEAGE_POINT_ROUTE_STATUS` carried elsewhere. Nothing is *changed*; the unconditional block is simply truncated in the one document that claims to be its permanent home.
- Also in section 5: `X_LAWSPEC_BASELINE = UNCHANGED` and `ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED` are filed under `CE_QUI_N_A_JAMAIS_ETE_TESTE`. Neither is a "never tested" status.

**On standing:** I find nothing forbidding a programme-level closure, and the authorisation is properly recorded alone and first, hashed, with an explicit `AUCUNE_MESURE_NOUVELLE` clause — that part is done well. But the authorisation covers what was described to the owner, and F1 shows the description was wrong on its central point.

---

### F20 — The script's provenance claim about itself is false. **MATERIAL, in a document whose subject is provenance.**

`CLOSE01/code/close01_dossier.py` docstring, repeated verbatim in commit `730be40`: *"Aucun chiffre n'est ecrit de memoire : tout est relu des fichiers commites au moment ou ce script tourne."*

Read from files: 12 values (six FIMRCC01 fields, five OMLDCT03 fields, the four TLMR01 sums, the two hashes, the commit count). Hard-coded string literals: `668 041`, `26 mondes sur 26`, `41 triplets`, `123 archives`, `taux de succes superieur a 0,10`, `9 paires sur 41`, `12 des 41 … contre 2`, `15 acceptes`, `16 acceptes` ×2, `1,22` ×2, `0,79 a 2,31`, `deux cents fichiers`, `28`, `alpha 0.05`, `effectif requis 41`, `METHODS_HASH`, and every one of the three withdrawal status strings. The great majority of the load-bearing figures — including all four discussed in F9, F10, F15 and F18 — are written from memory.

---

### F21 — The closure is not discoverable by a successor following the repository's own operating contract. **MATERIAL.**

`/home/claude/edl/AGENTS.md` opens with a mandatory reading order: `AGENTS.md → docs/RESEARCH_CHARTER.md → docs/PROJECT_STATE.md → docs/DECISION_LOG.md → docs/EXPERIMENT_INDEX.md → docs/RUN_INDEX.md → docs/agent_journals/`. VERIFIED: `grep -c` for any of `TLMR01|FIMRCC|OMLDCT|RPP97|RPP98|CLOSE01` returns **0** in all four of those files; the newest journal directory is `2026-07-13`, six weeks before this programme's missions. CLOSE01 writes no journal, no `DECISION_LOG` entry (AGENTS.md: *"update `docs/DECISION_LOG.md` only for a genuine decision"* — closing a programme is one), and does not record anywhere that the contract is stale. A successor who follows the stated entry point will never reach CLOSE01.

---

### F22 — Smaller drops, each checkable, each in the author's favour or in the direction of a tidier record.

- **Causal kernel.** The `668 041` row pairs establish only the lower bound (no cell without an admissible Moore-1 source). The *coincidence* of derived and measured sets — the part CLOSE01 states — rests on `single_source_rows_used_for_the_upper_bound: 25577`. One number is offered for both. Also dropped: "self inclus"; `ONE_CONSERVATIVE_ASYMMETRY` at the `t_m` transition of the SELECTIVE arm; and CLEA01's own mission disposition, `CAUSAL_LINEAGE_NOT_IDENTIFIABLE_FROM_EXISTING_ARCHIVES__LINEAGE_ROUTE_PAUSED`.
- **The AND rule.** Section 2 presents *"les DEUX criteres doivent rejeter"* as a stringency device. `OMLDCT03…F8` (ACCEPTED): Pearson ρ = 0.9751, sign agreement 41/41 — I reproduced both — *"c'est un critere rapporte deux fois"*. Two endpoints are printed as two independent blocks with no note.
- **The frozen claim ceiling.** `OMLDCT02_MASTER_FREEZE.json:CLAIM_CEILING` and `IT_DOES_NOT_ESTABLISH` (seven named items) are quoted nowhere in CLOSE01 — the same accepted finding as `OMLDCT03…F3`.
- **The scale of the object.** `LDFMA01/out/HANDOFF_…md §3`: *"The locked daughter is a 1-to-6 particle object holding the world's entire Y population at the trigger: `parent_nY + daughter_nY = world_nY` in 22 of 22."* The checker adds *"peaking at 1–6 Y over its life in 40 of 41 SELECTIVE arms."* Nothing in CLOSE01 tells a successor the scale of what forty missions were tracking. This is not vocabulary hygiene; it is a material fact.
- **The accrual shortfall's size.** The reserve says the stream "s'epuise avant 41 paires" without the numbers, which the source gives as 36 (operator), 38 (checker) and, by my own recount, 36. The shortfall is 3–5 pairs, not unknown.
- **Interval coverage.** `0.95034` (accepted as `F11`, still unstated). The interval is distribution-free and is not labelled as such.
- **Wording.** Reserve 1 says *"l'espece suivie s'eteint"*. The species that goes extinct is Y, the ambient species; the tracked object is the locked daughter identity. The sentence inverts what is being followed.

---

## VERIFIED vs SUSPECTED vs NOT CHECKED

**Verified, by my own computation, from the committed files:** all six FIMRCC01 wall figures, re-derived from the binomial (0.016509, 0.669730, 0.936213, 1.2201247, 26.8427); the power-vs-N table in F2; both OMLDCT03 p-values, W⁺ statistics, HL estimates and interval endpoints, from an independent exact Pratt sign-flip enumeration in `Fraction`; the four sensitivity specifications in F6 (32→0.04333/1.882, 34→0.29320, 22→0.12068), ρ = 0.9751 and 41/41 sign agreement; the TBRT02 C4 §12 sign test (0.024306510109454393); the four TLMR01 sums and the M2 terminator decomposition (8434/7900/34) that shows 16 368 counts segments, not runs; 885 ledger rows, 41 admissible, 123 distinct archives, 609.517 total instance cost, ceiling exhausting at index 738 with 36 pairs; all four checker-verbatim sha256; the commit count 156 at `37030e4`; both CLOSE01 content hashes; FDFLT01's freeze/disposition and the identity of its point B1 with `LAW_A_B1`; zero references to any mission in the four `docs/` entry-point files; `INTEGRITY_GATE_PASSES: false` with 123 missing in the committed gate output.

**Suspected, not verified:** that the positive point estimate would survive a properly specified competing-risks analysis — F6 shows the raw contrast is a mixture and that the survivor stratum crosses α, but I did not estimate a cause-specific or composite effect and would not be entitled to invent one here. That the discrepancy between TLMR01's 22 removal worlds (`0 of 22 daughters went extinct`, per `LDFMA01_MINIMAL_ARCHITECTURE_CANDIDATES.json` and the FIMRCC02 checker's `22/22 SPLIT_OR_TIE`) and TBRT02's 41 SELECTIVE arms (9 in-window extinctions, 12 overall) reflects a real difference in the material rather than differing horizons — it is a large gap on the same treatment at the same law, it bears on section 3's `le_materiel`, and CLOSE01 does not mention it. That the human owner would have answered differently had F1, F3, F6, F7 and F17 been put to him — the exposure is documented and dated; the counterfactual is not observable.

**Not checked:** the 123 `.npz` archives themselves (absent from this container, as expected — CLOSE01 opens none and neither did I); the internal correctness of TLMR01's, CLEA01's or FDFLT01's own measurement code beyond reading the definitions needed for F9, F10 and F22; the DISPLACED arm; the OBFOR01 / MYQBD01 / PMCR01 / OBTR01 lineage beyond the `NOT_PORTABLE` grep and INV01's summary of it; whether any of the 435 published files contains a further pre-registered confirmatory test beyond the three named in F1 — I did not run the anteriority gate, and neither did CLOSE01.

---

## VERDICT

Everything CLOSE01 copies out of a file, it copies correctly, and both its hashes bind. What it does with those numbers is the problem. Its one-sentence summary is contradicted by an entry in its own section 3 (F1); the arithmetic-impossibility claim on which the disposition is named is false by direct computation and drops the qualifier its source wrote into the status string (F2); the assurance figure that sits on the adjacent line of the cited object is omitted (F3); the accepted finding that the analyst was not blind is absent (F5); the reserve that lowers the estimate is printed and the diagnostic that carries it past α is not (F6); section 3 rests two of its six entries on a scope transfer and a stratification collapse (F8, F9); section 4 credits the author with two guards that were other missions' artefacts, breached (F14); and the legacy hands a successor a wall while withholding the four concrete things the record says they could do about it (F17).

Sections 0 and 7 are careful and correct — the closure genuinely does not claim absence, equivalence or a status change, and it says so twice. Section 2's numbers, taken as numbers, are exact. The accrual reserve is stated honestly and reproduces under my own recount. If the three sentences named in F1, F2 and F14 were corrected, the omissions in F3, F5, F6, F7, F17 and F18 supplied, and section 3's TLMR01 and FIMRCC01 entries rewritten to the scope their sources support, this would be a sound terminal record. As committed, it is not one, and the specific way it fails — asserting uniqueness without searching, asserting an impossibility the source scoped to one design, and crediting itself with guards it breached — is the same way the three withdrawn missions failed.
