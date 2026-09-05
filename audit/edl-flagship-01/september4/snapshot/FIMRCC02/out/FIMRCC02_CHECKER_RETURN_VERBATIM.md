# ADVERSARIAL CHECKER RETURN — FIMRCC02

**Scope.** Repository `/home/claude/edl` at `c2c1ef7`. Nothing committed, nothing under any mission directory modified; all scratch work in `/tmp/gatetest`. The TBRT02 archives are absent (`/home/claude/TBRT02_raw` empty), so **no finding below rests on any archive**. Everything I assert as VERIFIED was recomputed from committed files with my own code. What the missing archives block me from checking is listed at the end, and it is less than FIMRCC02 needs it to be: the repository already contains executed, committed, paired SELECTIVE-vs-SHAM measurements of the very endpoint in question, and those alone are enough to falsify the mission's two headline claims.

**Arithmetic first, because it is the only part that survives.** Every number in `FIMRCC02_POWER.json` reproduces. I re-ran `/home/claude/edl/FIMRCC02/code/fimrcc02_power.py` under an instrumented `open()` and diffed its output against the committed artefact: **zero differences** outside `GENERATED_UTC`. Extinction sets, 11/1/1/28, `n_disc = 12`, exact two-sided `p = 13/2048 = 0.00634765625`, `k* = 20` at `n = 28`, the nine-point power curve, and the ties table all reproduce to the last digit. Both content hashes verify under `omldct02_hashes.content_digest`. The code opens only `RPP98/work/shard0.json`, `shard1.json` and its own source; no `.npz`, no path under `TBRT02/`, and the only subprocess is `date -u`. **The file-level claim "no archive was opened to produce this file" holds.** That is the end of the good news.

---

## F1 — The premise under the p = 0.0063 headline is false by definition, and refuted by executed data already in the repository. FATAL.

`/home/claude/edl/FIMRCC02/out/FIMRCC02_POWER.json:49` — `CONSTAT_1.raisonnement`:

> « dans un monde ou Y est eteint, les trois criteres valent leur minimum par definition ... La direction de la paire est donc FORCEE »

Every clause of that is wrong against the frozen definitions.

**E3.** `/home/claude/edl/FIMRCC01/code/fimrcc01_e4.py:33` computes `"steps_after_tm": e["end"]-tm`. `e["end"]` is the last step at which the daughter's identity interval exists. Y extinction **bounds E3 above** by `t_first_zero − t_m`; it does not set it to a minimum. I computed that bound for each of the 11 seeds FIMRCC02 calls "forced", from the committed shards:

```
seed   t_m    t_1st_zero   upper bound on E3_SELECTIVE
507    1552   1568          16
124    1060   1081          21
595    1023   1048          25
573     693    761          68
 85     685    842         157
393    1247   1525         278
530     549    982         433
321    1641   2257         616
636     617   1250         633
768     479   1212         733
347    1108   2059         951
```

TLMR01's published E3 marginal (`/home/claude/edl/FIMRCC01/out/FIMRCC01_ENDPOINT_TABLE.json`) is min 31, median 230, mean 314, max 1472. **Six of the eleven bounds exceed the median; five exceed the mean.** The SHAM arm's interval does not run to the horizon either — all 22 TLMR01 daughters ended by `SPLIT_OR_TIE` at a median of 230 steps (I counted `END_REASON` across `/home/claude/edl/FIMRCC01/work/pa_out/*.json`: 22 of 22 `SPLIT_OR_TIE`, zero extinctions). So in an extinct-SELECTIVE pair the sign is not forced; it is not even biased in a direction FIMRCC02 has established.

**The repository already measured this and got the opposite sign.** `/home/claude/edl/OMLDCT02/out/OMLDCT02_FROZEN_ANALYSIS.json` contains 33 executed matched pairs on this exact endpoint. Two of them have `SELECTIVE_termination = "NO_COMPONENT_AT_THE_NEXT_STEP"` — the world lost all components, i.e. the extinction case:

| index | SELECTIVE_duration | SHAM_duration | sign |
|---|---|---|---|
| 450 | **257** | 88 | favours SELECTIVE |
| 482 | **214** | 128 | favours SELECTIVE |

Both of the only two executed instances of the case FIMRCC02 calls "forced in favour of SHAM" went in favour of SELECTIVE. n = 2 is not a refutation of a tendency; it is a complete refutation of a claim of logical necessity, which is what `par definition` and `FORCEE` assert.

**E4** is `y_births_after_tm + y_deaths_after_tm` (`fimrcc01_endpoint_table.py:44`). FIMRCC02 says "il n'y a plus ni naissance ni mort de Y a lui attribuer". Extinction of Y **is** a sequence of Y deaths; the arm heading to extinction can accumulate more Y deaths inside the interval, not fewer. The direction is arguably reversed.

**E5** is `len(turnover_in(ev, t_m))`. `/home/claude/edl/TLMR01/code/tlmr01_offline.py:249-254` retains every interval with `e["end"] > t_m`. An extinct arm still has 16 to 951 steps of live world after `t_m`; every interval that turned over in that span counts. Not forced to zero.

**Load-bearing:** total. `CONSTAT_1`, its `VERDICT` string, the commit message ("11 paires sur 12 forcees par la mort du monde"), `ROUTE_A`'s rejection, and the disposition `NON_INTERPRETABLES__CONFONDUS_PAR_LA_MORTALITE_DIFFERENTIELLE` all rest on this one sentence.

---

## F2 — "p = 0.0063 under the strict null" is a statement about a test nobody would run, contradicted by the same document, and it misstates the size of the problem by a factor of ~45.

VERIFIED by computation.

`fimrcc02_power.py:70-71` sets `n_disc = sel_only + sham_only = 12` and computes the sign test on those twelve pairs alone. **That arithmetic silently assumes the other 29 pairs are exact ties.** If they are not, they enter `n` and the p-value changes completely.

The same artefact denies the assumption four keys later. `FIMRCC02_POWER.json:113` — `E3_EST_DIFFERENT`: *"E3 a 22 valeurs distinctes sur 22 mondes ... les egalites exactes seront rares."* **`CONSTAT_1` needs 29 exact ties; `CONSTAT_4` says E3's exact ties are rare. Both cannot be true.** The measured answer is in the repository: OMLDCT02's E3-duration tie rate is **1 in 33 (3.0 %)**; TBRT02's own C4 §12 paired duration contrast has **7 zeros in 41 (17.1 %)**. Neither is anywhere near 29 in 41.

I computed the realistic null. Grant FIMRCC02 its own (false, per F1) premise that mortality forces 11 pairs to SHAM and 1 to SELECTIVE, and let the 28 both-alive pairs be untied and fair under the strict null of no effect. Then `n = 40`, `K = 11 + Bin(28, ½)`:

```
P(reject at α = 0.05)  = 0.2858
E[p-value]             = 0.2594
median p-value         = 0.1539
P(p ≤ 0.0063)          = 0.049
```

The published number **0.0063 occurs with probability 4.9 %**. It is not "what the frozen test would return"; it is one tail point of a distribution whose centre is p = 0.15.

As a function of `q = P(the extinct-arm pair favours SHAM)`:

```
q    0.00   0.10   0.30   0.50   0.70   0.90   0.9167  1.00
α'   0.425  0.276  0.093  0.0385 0.093  0.276  0.2985  0.425
```

Two things follow. **(a)** The confound is real: type-I error inflates from a nominal 0.0385 to 0.28–0.43. FIMRCC02 is right that the frozen contrast is not interpretable as it stands. **(b)** Its headline overstates that by presenting a near-certainty, and F1 shows the empirically supported value of `q` is near **0**, not near 1 — the inflation is just as large but points the other way, which makes the `VERDICT` string's directional reading ("retournerait significatif ... il ne distingue pas la fille ne persiste pas de retirer le parent tue le monde") unsupported.

The honest sentence was available and is one line: *the frozen paired sign test has a type-I error of roughly 0.29 rather than 0.05 if extinction biases the pair sign, and I have not established that it does or in which direction.*

---

## F3 — The terminal disposition is false. A pre-registered confirmatory test of daughter persistence exists, on a disjoint seed set, frozen before the mortality table existed, with a pre-declared minimum pair count of exactly 41.

VERIFIED. This is the finding that ends the mission.

`/home/claude/edl/FIMRCC02/out/FIMRCC02_CLOSURE.json:36`:
> `NO_PREREGISTERED_CONFIRMATORY_TEST_OF_DAUGHTER_PERSISTENCE_IS_AVAILABLE_ON_THESE_ARMS__ENDPOINT_TRUNCATED_BY_DEATH`

and `:32`, the stated condition that would legitimise ROUTE_C:
> *"un pre-enregistrement ecrit par quelqu'un qui n'a pas vu la table de mortalite, ou sur un jeu de graines disjoint **qui n'existe pas ici**."*

Both halves of that condition are satisfied, in this repository, and have been since 25–26 August. `/home/claude/edl/OMLDCT02/out/OMLDCT02_MASTER_FREEZE.json`, `GENERATED_UTC 2026-08-25T22:30:05`, `THIS_FREEZE_PRECEDES_EVERY_SCIENTIFIC_WORLD: true`:

```
PRIMARY_ENDPOINT   "paired post-intervention duration of the same locked daughter identity"
COPRIMARY_ENDPOINT "paired post-intervention locked-daughter particle-step exposure"
SIGN_CONVENTION    "SELECTIVE minus SHAM, on the paired log difference"
PAIRED_TEST        "two-sided exact Wilcoxon signed-rank with Pratt ranking ... No normal approximation anywhere."
ALPHA              0.05
ZERO_DIFFERENCE_TREATMENT  "PRATT_EXACT_SIGN_FLIP"
MINIMUM_VALID_PAIR_COUNT   41
NULL_RESULT_INTERPRETATION "INCONCLUSIVE__NO_CLAIM_OF_EQUIVALENCE__NO_CLAIM_OF_NO_EFFECT"
```

That is E3, with a frozen test, a frozen α, a frozen tie rule, a frozen combination rule and a frozen minimum pair count — written **four days before RPP98 computed `n_zero_steps`** and therefore by an author who had not seen the mortality table.

And the seed set is disjoint. `/home/claude/edl/TBRT02/out/TBRT02_MASTER_FREEZE.json`:
- `SELECTIVE: "the parent's Y is removed through the engine's decay channel, Y -> WY; **the OMLDCT02 treatment, kept for comparability**"`
- `TARGET_VALID_TRIPLES: 41` — the same integer as OMLDCT02's `MINIMUM_VALID_PAIR_COUNT`
- `TBRT01_AND_OMLDCT02_SEEDS_ARE_INSIDE_THE_FORBIDDEN_SET: true`, `SEEDS_DISJOINT_FROM_EVERYTHING_RUN_BEFORE: true`, `N_FORBIDDEN: 6842`

OMLDCT02 terminated at `INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS` with 33 pairs against a required 41. **TBRT02 delivered 41 triples of the same treatment at the same law on seeds explicitly excluded from OMLDCT02's set.** The pre-registered confirmatory test FIMRCC02 declares unavailable is sitting in the repository with its accrual target met, and it is the only object in this entire programme that is both frozen in advance and now executable.

FIMRCC02 does not mention OMLDCT02 anywhere in either code file or either artefact. Neither does its prior-art gate.

---

## F4 — "Truncation by death / E3 does not exist in an extinct world" is wrong against three independent frozen sources. FATAL, exactly as the task anticipated.

VERIFIED.

`/home/claude/edl/FIMRCC02/out/FIMRCC02_CLOSURE.json:16`:
> *"E3 ... n'est pas MANQUANT dans un monde ou Y est eteint : il N'EXISTE PAS. Un critere non defini sous le traitement ne se moyenne pas."*

1. **The frozen measurement code defines it.** `/home/claude/edl/FIMRCC01/code/fimrcc01_e4.py:33`: `"steps_after_tm": e["end"]-tm`. `/home/claude/edl/FIMRCC01/code/fimrcc01_precondition_a.py` — `id_trace` simply stops extending the interval when a step has no components (`if not cl: prev_c=None; prev_ids=[]; continue`), leaving `e["end"]` at the last live step; and `follow()` returns a **named end reason for precisely this case**: `END_REASON = "NO_COMPONENT_AT_THE_NEXT_STEP"`.
2. **The frozen pre-registration enumerates it.** `OMLDCT02_MASTER_FREEZE.json`, `MATCHED_DESIGN.identity_terminates_at`: `["split", "merge", "tie or ambiguity", **"empty component"**, "administrative horizon"]`. World death is one of five pre-declared ways the clock stops — a measured outcome, not an undefined one.
3. **It has been measured.** OMLDCT02 indices 450 and 482, above: E3 = 257 and 214 in exactly that termination mode.

Truncation by death is the situation where an outcome is *measured at a time after the unit has died* — quality of life at six months for someone who died at three. E3 is a **duration from `t_m` to the interval's end**. There is no post-death measurement; death is the event that defines the value. The frame is not merely arguable, it is inverted.

The correct frame is **competing risks**: the daughter's identity can end by split, merge, tie, world extinction, or the horizon, and the treatment shifts the mix. That is a real and serious problem for interpreting a raw duration contrast. Its standard answers are (i) cause-specific analysis, (ii) a composite ordering with world-death at the worst rank. FIMRCC02 names (ii) as `ROUTE_C`, calls it *"la reponse methodologique standard a la troncature par la mort"*, and refuses it on the ground that no clean pre-registration exists — which F3 shows is false, and which anyway would not be needed, because OMLDCT02's frozen Pratt sign-flip rule already specifies how a zero-difference pair is handled.

---

## F5 — Novelty: the endpoint, the paired design, the power calculation, the test, and the mortality observation are all already in this repository. FIMRCC02 claims four firsts and has none.

VERIFIED. This is the RPP98 failure mode reproduced.

**The power analysis is not first.** `/home/claude/edl/LDFMA01/out/LDFMA01_MATCHED_CONTROL_POWER.json`, section titled *"6 — matched-control power"*, 2026-08-25T18:45, contains `E3_CONTINUOUS_ALTERNATIVE`: `paired_log_SD_from_the_22_SELECTIVE_worlds: 0.997`, `n_pairs: 22`, `detectable_shift_at_80pc_power_approx: "about a two-fold change in persistence"`, and the note *"reported so the rejection of E3 cannot be mistaken for a power argument. **E3 has the power**; it does not have the alignment."* `/home/claude/edl/LDFMA01/out/HANDOFF_ONE_MATCHED_LOCKED_DAUGHTER_CONTROL_TEST_01.md` publishes a power table **at n = 41 paired blocks** (0.402 / 0.971 / 1.000 across the Wilson interval) for the forked SELECTIVE/SHAM design. FIMRCC02's closure: *"La puissance prospective de ces trois criteres est donc IDENTIFIEE pour la premiere fois."*

**The contrast has been executed.** OMLDCT02, 33 pairs, exact two-sided p = 0.4009 on duration and 0.2311 on exposure, Hodges–Lehmann 0.196 with interval [−0.259, 0.677]. I computed the sign split myself from the per-pair table: 18 SELECTIVE-longer, 14 SHAM-longer, 1 tie; sign-test p = 0.597. Paired log-difference SD = 1.453 on 33 pairs.

**The endpoint has been audited by a third mission.** `/home/claude/edl/EVCS01/out/EVCS01_FINAL_DISPOSITION.json`, `E3_ENDPOINT_COMPOSITION_MEASURED__DECISION_REFERRED_TO_THE_OWNER`, 66 arms, 28 checker findings adjudicated.

**A paired SELECTIVE-minus-SHAM contrast on TBRT02's own 41 seeds is already published.** `/home/claude/edl/TBRT02/out/TBRT02_C4_ANALYSIS.json`, `12_EXPLORATORY_PAIRED_CONTRASTS`: `SELECTIVE_minus_SHAM_CERTAIN_duration: n_positive 24, n_zero 7, n_negative 10` (I computed the sign test on that: two-sided p = 0.0243, tie rate 17.1 %). It is a different duration — the Model C lineage set, not the identity interval — but it is a paired duration contrast on exactly the seeds at issue, and it points the opposite way from FIMRCC02's premise.

**Differential mortality is not "brought to light here."** Three prior sources, all committed:
- RPP97's checker, quoted verbatim inside RPP98's: *"the parent removal kills the world in 12 of 41 SELECTIVE arms […] a further reason a post-`t_m` window would have produced a real arm contrast."*
- `/home/claude/edl/RPP98/out/RPP98_CHECKER_RETURN_VERBATIM.md` findings **F6 and F7**, with the full table (`SHAM 2, SELECTIVE 12, DISPLACED 5 of 41`; alive-fraction means 0.954 / 0.718 / 0.891), the named worlds (507, 595, 124), *and the exposure-normalised correction showing the contrast disappears* (4.17 / 3.78 / 3.48).
- `/home/claude/edl/GATE01/out/EDL_PRIOR_ART_MAP.json:91` — *"Y s'eteint dans 12 des 41 bras SELECTIVE, 5 DISPLACED, 2 SHAM"* — and `:94`, `LE_RISQUE_HONNETE`: *"Un contraste apparie de comptes apres t_m mesurera en partie la mort du monde et non la persistance de la fille."*

That last one is the core methodological finding of FIMRCC02, written three lines above the file's end, by the same operator, **four minutes before the gate was run**, in the file FIMRCC02's closure cites by name in the very sentence where it claims nobody has studied it.

---

## F6 — The prior-art gate is theatre as operated and structurally blind by construction.

VERIFIED by running the gate myself.

**The terms were chosen so that only the parent could be flagged.** `/home/claude/edl/GATE01/out/FIMRCC02_PRIOR_ART.json` — `TERMS = ['F_INTEGRATED','K_REQUIREMENT','prospective power','paired','FUTURE_QUESTION_RECORDED','sign test','power_at_n50']`. Five of the seven are FIMRCC01's private vocabulary. Result: 18 files, **12 of them FIMRCC01**, and zero from LDFMA01, OMLDCT01, OMLDCT02 or EVCS01. I confirmed why: no LDFMA01 file contains two of those terms — `LDFMA01_MATCHED_CONTROL_POWER.json` matches only `paired`, one short of the threshold. The single most relevant artefact in the repository misses the gate by one word.

The gate's own docstring (`/home/claude/edl/GATE01/code/edl_prior_art_gate.py:23-33`) prescribes the fix and FIMRCC02 ignored it: *"Les termes doivent etre les NOMS DES GRANDEURS, pas les mots du concept. Une porte franchie avec des termes vagues est une porte contournee."* I ran it with the names of the quantities this mission actually reasons about — `matched-control power`, `paired log difference`, `post-removal identity lifetime`, `MINIMUM_VALID_PAIR_COUNT`, `PRATT`, `Wilcoxon`, `identity lifetime`, `matched control`:

```
28 flagged. Top of the ranking:
 [4] LDFMA01/out/HANDOFF_ONE_MATCHED_LOCKED_DAUGHTER_CONTROL_TEST_01.md
 [4] LDFMA01/out/LDFMA01_ROUTE_ARBITRATION_FINAL.json
 [4] OMLDCT01/out/OMLDCT01_CAUSAL_ESTIMAND.json
 [4] OMLDCT01/out/OMLDCT01_MASTER_FREEZE.json
 [4] OMLDCT02/out/OMLDCT02_MASTER_FREEZE.json
 [2] OMLDCT02/out/OMLDCT02_FROZEN_ANALYSIS.json
```

Every one of these would have received `ANSWERS_THE_QUESTION`, and a single one of those forbids the freeze under the gate's own rule.

**The rule is trivially passable.** Two obscure terms that co-occur nowhere give 0 flagged files and `PASSE`. I verified: `['POWER_CONTENT_HASH','p_bilateral_du_test_des_signes']` → 0 flagged, exit 0. `['prospective power','power_at_n50','K_REQUIREMENT']` → 4 flagged, all FIMRCC01. The `>= 2 terms` rule has no notion of term rarity, no weighting, and no floor on how many files must be examined. A gate that passes on an empty flagged set is not a gate.

**Structural blind spots, in the code.** `edl_prior_art_gate.py:53` skips anything under `GATE01/` — so `EDL_PRIOR_ART_MAP.json`, the programme's own inventory of what is already established, **can never be flagged by the gate that exists to find what is already established**. `edl_prior_art_gate.py:42` accepts only `/out/` or `/work/` with `.json|.md|.jsonl`, plus `/code/*.py`. I enumerated the consequences: **all 18 files under `review/` directories are invisible**, including `LDFMA01/review/LDFMA01_CHECKER_RAW.txt` and `OMLDCT02/review/OMLDCT02_CHECKER_RAW.txt`. In a programme where the load-bearing prior findings live in adversarial checker returns — as F5 demonstrates — excluding `review/` is the single worst filter available.

**The verdicts are boilerplate.** 18 files, **3 distinct `REASON` strings**: one used 9 times, one 8 times, one once. `TLMR01/out/TLMR01_POWER_RULE.json` is marked `IRRELEVANT — "partage un vocabulaire de puissance mais ne porte pas sur E3/E4/E5 apparies"` — while TLMR01's 22 worlds are the **source of the E3 and E4 marginals that `CONSTAT_4` is built on**. That verdict is not honest; at minimum it is incoherent with the artefact it gates.

**The gate has no independent temporal standing.** `git show --stat 952bcc5`: `GATE01/out/FIMRCC02_PRIOR_ART.json` was committed **in the same commit as `fimrcc02_power.py` and `FIMRCC02_POWER.json`**. Whatever the gate is for, it is not for showing that the search preceded the result — RPP98, for all its faults, committed its capability test alone (`e3a3804`) and its pre-registration alone (`15f0ab3`). FIMRCC02 dropped that discipline for the one artefact whose whole value is being *opposable*.

---

## F7 — The E4 tie-rate bound is arithmetically false, cannot be derived from the source it cites, rests on an argument that is asserted rather than proved, and transports a marginal the repository has already shown to be an instrument artefact.

VERIFIED, four separate defects.

**(a) The number is wrong.** `FIMRCC02_POWER.json:110`: *"le taux d'egalites de E4 est donc **superieur a 25 pour cent**."* The per-world E4 values are published in `FIMRCC01_ENDPOINT_TABLE.json:PER_WORLD`. I counted them: `{0:5, 1:7, 2:6, 3:2, 4:1, 5:1}`, n = 22. Sum of squared frequencies = **116/484 = 0.23967**. That is **23.97 %, below 25 %.** The stated conclusion is false by its own arithmetic.

**(b) "at least equal to" is wrong.** For two i.i.d. draws the collision probability is **exactly** Σf², not "at least" it.

**(c) It is not derivable from the marginal FIMRCC02 says it used.** The cited source is the *published marginal* (22 worlds, 6 distinct values, mode 1 at 31.82 %) — not the per-world table. I enumerated every frequency vector consistent with that marginal: Σf² ranges **0.1942 to 0.2603**. The only defensible statement from the marginal alone is **≥ 19.4 %**, which is materially weaker than the ">25 %" claimed. Either FIMRCC02 read the per-world table (and got 23.97 % wrong) or it read the marginal (and had no basis for 25 %). Both readings fail.

**(d) "Pairing can only increase ties" is asserted, and false in general.** `FIMRCC02_POWER.json:109`: *"les deux bras ... partagent un prefixe bit a bit identique jusqu'a t_m, ce qui ne peut qu'AUGMENTER le taux d'egalites."* Dependence does not imply exact equality: two perfectly correlated variables with a constant offset have correlation 1 and tie rate 0. No proof is offered and none exists. Worse, the argument is applied **inconsistently** — the same shared prefix is invoked to raise E4's tie rate and silently ignored for E3, which is exempted two keys later.

**(e) The transport is illegitimate on two axes.** TLMR01's 22 worlds are all *removal* worlds (SELECTIVE-like) with **zero extinctions** — I verified 22 of 22 `END_REASON = SPLIT_OR_TIE` in `/home/claude/edl/FIMRCC01/work/pa_out/`, and `/home/claude/edl/LDFMA01/out/LDFMA01_MINIMAL_ARCHITECTURE_CANDIDATES.json` states it: *"0 of 22 daughters went extinct."* The marginal is transported to a design where 12 of 41 SELECTIVE arms are extinct, and applied to both arms including SHAM, which has no analogue in the source.

**(f) E4's narrowness is a known, quantified instrument defect.** `/home/claude/edl/LDFMA01/out/LDFMA01_FAILURE_PARTITION.json` and the handoff's precondition P1: *"the archive writes cell rows AFTER the step. A Y decay that empties a cell removes that cell from the step-t rows, so the frozen attribution ... cannot see it."* Across the same 22 worlds the decay rate predicts **8.44** constituent removals and the frozen rule counts **1**; re-attributing at t−1 raises it to 8. E4 is half Y-deaths. Its range of 0–5 with a mode at 1 is substantially the defect, not the physics, and LDFMA01 made repairing it a **precondition before world 1**. FIMRCC02 builds `E4_STATUT_PROSPECTIF = SOUS_PUISSANT_SAUF_EFFET_TRES_LARGE` on that artefact without mentioning it.

**(g) It is the move FIMRCC01's frozen pre-registration forbids.** `FIMRCC01_ENDPOINT_PREREGISTRATION.json`, `CRITERION_3_POWER.for_paired_count_candidates`: from these marginals only non-degeneracy may be reported, *"which is a necessary and not a sufficient condition"*, and `NO_POWER_NUMBER_WILL_BE_INVENTED_FOR_THESE: true`. An underpower verdict derived from the marginal is that number under another name.

**Measured paired tie rates were available without opening anything:** OMLDCT02 E3-duration **1/33 = 3.0 %**; TBRT02 C4 §12 **7/41 = 17.1 %**.

---

## F8 — The post-treatment retraction is right in genre, wrong in three specifics, and dismisses an estimand that this design point-identifies.

The genre is correct. The naive contrast `E[Y | S_obs = 1, A = 1] − E[Y | S_obs = 1, A = 0]` on a treatment-affected survival indicator is not a causal contrast. Nothing below excuses the original sentence in `FIMRCC02_POWER.json:117`. But the retraction gets three things wrong and overcorrects into a different false statement.

**"Cela brise l'appariement" is false.** Restricting to a subset of pairs does not break pairing. Each retained pair is still bit-identical to `t_m` and still exchangeable within itself. Restriction changes the **population**, not the matching. The sentence describes a failure mode this design does not have.

**"Le contraste restreint n'estime aucune quantite causale" is false in this design.** This is a deterministic within-seed crossover: both arms are run on the same seed with the same random stream to `t_m`, and OMLDCT02 verified the intervention **consumes no random number**. Therefore **both potential survival indicators `S(1)` and `S(0)` are observed for every seed.** In the standard truncation-by-death / SACE literature the entire difficulty is that principal-stratum membership `(S(1), S(0))` is latent and the effect is only partially identified under monotonicity plus sensitivity assumptions. **Here the stratum is observed.** The always-survivor average causal effect on `{ω : S(1,ω) = S(0,ω) = 1}` is a genuine, point-identified causal quantity — it is the mean of individual causal differences `E3(1,ω) − E3(0,ω)` over an explicitly enumerated set of seeds — with no monotonicity, no exclusion restriction and no sensitivity analysis required. FIMRCC02 walks into the one setting where principal stratification is trivially identified and rejects it in a single sentence using the vocabulary of the setting where it is not.

**"Aucun n plus grand ne le repare" is half wrong.** True for the ATE (bias, not variance). False for the always-survivor effect, which is consistently estimable and does improve with n.

**What is actually true, and unsaid:** the always-survivor stratum is defined by the treatment's own effect, so (i) it is a narrower estimand than the one FIMRCC01 froze, (ii) it cannot be identified prospectively for a fresh seed, and (iii) any claim from it must be labelled as an effect among worlds the removal did not kill — never generalised to all worlds. That is a claim-ceiling problem, not an identification problem, and it is exactly the kind of thing the programme's `CLAIM_CEILING` machinery exists to handle.

**Net:** both of the mission's positions on ROUTE_B are wrong, in opposite directions. The original ("the only askable version") ignored the change of estimand; the retraction ("estimates nothing causal, breaks the matching, unfixable by n") is a stronger and equally false claim. The self-correction is presented as the mission's methodological centrepiece and it is not correct.

---

## F9 — "The power is identified for the first time / FIMRCC01's field can be replaced by a number." Three separate falsehoods, one of them a contradiction between adjacent keys of the same object.

VERIFIED.

**(a) FIMRCC01's stated obstacle is untouched.** `FIMRCC01_ENDPOINT_TABLE.json`, `POWER_NOT_ESTIMABLE_IN_ADVANCE`: *"no matched control arm exists anywhere in TLMR01's 512 worlds, **so the distribution of the within-block difference between arms is unknown**."* The obstacle is the *difference distribution*, not the arm. FIMRCC02 never measures it — it opens no archive — and it does not use the published one (OMLDCT02's 33 paired log differences, SD 1.453, HL 0.196, HL interval [−0.259, 0.677]). The named obstacle stands exactly where FIMRCC01 left it.

**(b) No power number is produced for any of the three.** For E3: a curve indexed by an unknown `p_true`. For E4: a false tie-rate bound (F7). For E5: nothing. `FIMRCC02_CLOSURE.json:39` says `E5_STATUS: "NOT_ASSESSED..."` and `:40`, in the same dictionary, says *"La puissance prospective de **ces trois criteres** est donc IDENTIFIEE pour la premiere fois."* Two adjacent keys, flat contradiction.

**(c) `CONSTAT_2` contains no mission-specific information beyond the integer 28.** `k* = 20`, the nine-point power curve, the ties table — every number follows from `Bin(n, ½)` and nothing else. Substitute any 28 pairs of any quantity in any field and the table is identical. It is not a fact about E3, E4, E5, TBRT02, LAW_C, or the daughter. Calling it the thing "the mission delivers anyway" is calling a binomial table a result.

**(d) "Le verrou nomme est tombe" is selective quotation.** `FIMRCC01_ENDPOINT_ADJUDICATION.json`, `E3_E4_E5.why_not`, gives **five** reasons. Only the second concerns the missing arm. Reasons 1 (*"they are contrasts, not the frozen binary reproduction event"*), 4 (*"selecting one now would change the scientific question after developmental outcome access"*) and 5 (*"no fresh run may be authorised from them inside this mission"*) are untouched by TBRT02's existence. Reason 4 in particular is precisely the contamination objection FIMRCC02 raises against ROUTE_C — and it applies to the whole reopening, not to one route.

---

## F10 — Governance: the mission reopens a question its parent locked, without the authorisation the parent requires, and drops the clauses the parent mandates.

VERIFIED against frozen text.

`/home/claude/edl/FIMRCC01/out/FIMRCC01_FINAL_DISPOSITION.json`:
```
NEXT_SCIENTIFIC_ELIGIBILITY : "NONE__LINEAGE_ROUTE_PAUSED"
NO_HANDOFF_IS_EMITTED       : true
REOPENING_REQUIRES          : "an explicit new human authorisation and a newly derived
                               matched-control design. Nothing in this mission authorises one."
E3_STATUS / E4_STATUS / E5_STATUS : "FUTURE_QUESTION_RECORDED__NOT_AUTHORISED"
```
FIMRCC02 rewrites all three statuses (`POWER_NOW_IDENTIFIED__...`) with **no human authorisation recorded anywhere in either artefact**. The only referral to the operator in the mission is about the mortality question, not about reopening E3/E4/E5.

`FIMRCC01_FINAL_DISPOSITION.INHERITED_CLAUSES_RE_EMITTED_VERBATIM` and `LDFMA01/out/HANDOFF...md §4` both carry `EVERY_SUCCESSOR_MUST_RE_EMIT_THESE_CLAUSES = true`. **Neither FIMRCC02 artefact contains the clause block.** `STATUTS_INCHANGES` is a different list and does not include `MEASUREMENT_NOT_POINT_SEARCH`, `POST_OUTCOME_ENDPOINT_SELECTION`, `MAX_POST_OUTCOME_SCIENTIFIC_REPAIRS`, `MAX_INDEPENDENT_CHECKERS`, or the rest.

**And the retraction was already frozen, in writing, in the file FIMRCC02 cites as its parent.** `/home/claude/edl/FIMRCC01/out/FIMRCC01_ENDPOINT_PREREGISTRATION.json`, `WHAT_IS_DELIBERATELY_NOT_PERMITTED`, item 2:
> *"**conditioning the endpoint on any quantity measured after the trigger.**"*

ROUTE_B was prohibited by name on 25 August. FIMRCC02 proposed it on 30 August as *"LA_SEULE_VERSION_POSABLE"*, then retracted it eleven minutes later as an original insight — *"CETTE PHRASE ETAIT FAUSSE, ET JE LA RETIRE ICI AVANT QU'UN CHECKER LA TROUVE"* — without noting that the prohibition was already frozen in the pre-registration it reads at the top of its own docstring. The mission's showpiece self-correction is a rediscovery of its parent's rule.

---

## F11 — The mission failed the contamination checklist its own immediately-preceding artefact wrote for it.

VERIFIED. `/home/claude/edl/GATE01/out/EDL_PRIOR_ART_MAP.json:86-93`, `CE_QUI_DOIT_ETRE_FAIT_AVANT_TOUT_GEL`, written 02:07:38, four minutes before the gate ran:

- **Item 2:** *"CONTAMINATION. J'ai deja beaucoup vu des archives TBRT02 : C3, C4, C4bis, C5, RPP97, RPP98 et deux retours de checker. Une section 0 doit enumerer tout cela, y compris les constats de METHODE et pas seulement les grandeurs — c'est le constat F12 de RPP98."* — **FIMRCC02 has no section 0.** It has two inline "DEJA VUE" labels on two quantities and nothing on method exposure. RPP98's F12 is exactly the finding that a "what has been seen" section which filters *outcomes* and discards inherited *method* findings is *"a fairness device pointed in one direction."* Repeated verbatim, four minutes after being written down as the thing not to repeat.
- **Item 6:** *"GATE01 passe avec les NOMS DES GRANDEURS avant le gel."* — not done (F6).
- **Item 3:** the DISPLACED-not-GLOBAL_OFF substitution *"doit etre ecrit au titre, pas en note"* — it is in a sub-key named `UNE_TROISIEME_VOIE_A_EXAMINER`.
- **Item 4** (unit = 41 seeds, never 123 archives) is honoured — `fimrcc02_power.py:62` keys on `r["index"]`. Credit where due.

This is load-bearing because the mission's single strongest move — refusing ROUTE_C on contamination grounds — is made by an author who declined to enumerate his own contamination.

---

## F12 — The closing suggestion is the same overclaim that got RPP97 and RPP98 withdrawn, and it uses the same number as a defect and a discovery within one mission.

`/home/claude/edl/FIMRCC02/out/FIMRCC02_CLOSURE.json:44`:
> *"La mortalite differentielle **mise au jour ici** — 12 mondes sur 41 ... — est elle-meme un effet cause, large, apparie et non confondu, **dont personne n'a encore fait un objet d'etude**."*

- **"Mise au jour ici" is false**, three times over (F5). The sentence cites `EDL_PRIOR_ART_MAP.json` **by filename one clause earlier**, and that file carries the same 12/5/2 numbers at line 91 and names the confound at line 94.
- **"Personne n'a encore fait un objet d'etude" is false.** RPP98's checker made it findings F6 and F7, marked both LOAD-BEARING, tabulated alive-fractions per arm, named three worlds, and *computed the exposure-normalised correction* showing the striking contrast disappears. That is more study than FIMRCC02 gives it.
- **The same number is a bug in one file and a feature in the other.** `CONSTAT_1` presents the 12-vs-2 sign test as an artefact that fakes significance. The closure presents the same test on the same data as a real caused effect worth a mission. If the mortality sign test is valid, `CONSTAT_1`'s objection collapses to *"the frozen endpoint is partly driven by a real causal effect"* — a mediation/composite question, not a defect. If it is not valid, the closing suggestion is unsupported. FIMRCC02 needs both and states both.
- **It is the ROUTE_C violation, with the label removed.** Two keys earlier the closure refuses ROUTE_C because *"je le concevrais APRES avoir vu la table de mortalite — 12 contre 2 — qui est precisement ce qui le rend attrayant."* Then it proposes the 12-vs-2 contrast itself as the next question, on the ground that it saw the 12-vs-2 table. *"Je ne le gele pas : je le note"* is not a distinction the RPP97/RPP98 withdrawals recognise — nominating a hypothesis because you saw its data is post-hoc whether or not you freeze it in the same file.
- **"Non confondu" and "large" are claims, not measurements.** Within-pair the comparison is unconfounded; that much is by construction. But no test is run, no error rate is stated, no correction is applied, and seed 793 is dead in both arms and 780 dead only in SHAM — the caused contrast is 11 extinctions and 1 rescue on 41 seeds, not 12 against 2. Presenting three arms adjacent with no test is what RPP98's F10 was written about.

---

## F13 — The DISPLACED alternative is recommended on outcome grounds and is a different, more invasive treatment. It survives the closure's retraction unexamined.

`FIMRCC02_POWER.json:118`: *"le bras DISPLACED perd Y dans 5 graines contre 12 pour SELECTIVE ; le contraste DISPLACED contre SHAM est **moins confondu**."*

I verified the arithmetic: DISPLACED vs SHAM has 5 discordant mortality pairs (4 / 1), exact two-sided sign p = 0.375, and 35 both-alive pairs. So the confound is indeed smaller. But:

- **The arm is selected because of its outcome.** The stated criterion is "it kills fewer worlds", which is a post-treatment quantity observed in the same table the closure refuses to design around.
- **It is not a milder version of the same intervention.** `TBRT02_MASTER_FREEZE.json`: `DISPLACEMENT_IS_MORE_INVASIVE_THAN_REMOVAL — "removal uses the engine's own decay channel. Displacement is a teleport: no engine channel moves mass across the lattice in one step."` A DISPLACED-vs-SHAM contrast answers a different causal question, and its lower mortality is a property of a different treatment, not a cleaner estimate of the same one.
- **The closure retracts ROUTE_B and leaves this standing.** Every objection the closure raises against restricting to survivors applies identically to preferring an arm because fewer of its worlds die.

---

## F14 — E5's stated reason is wrong on the inherited facts and ignores a far sharper published one.

`FIMRCC02_CLOSURE.json:39`: `E5_STATUS: "NOT_ASSESSED__AMBIENT_POPULATION_SATURATED_AT_E0__NOT_FROZEN"`.

E0 is a **binary** and is saturated (22/22). E5 is a **count** and is explicitly `CRITERION_2_SATURATED: false` in `FIMRCC01_ENDPOINT_TABLE.json` — 20 distinct values across 22 worlds, min 65, median 93, max 117, sd 13.7. The two are different objects and FIMRCC02 conflates them.

The real reason is published and much stronger. `/home/claude/edl/LDFMA01/out/LDFMA01_MATCHED_CONTROL_ENDPOINTS.md`: E5 fails conditions 1 and 2 **by construction** — *"2 017 of 2 018 ambient complete intervals begin after the locked identity has already ended"*, the bloom arrives 706–2614 steps after the removal, and the handoff's §3 says flatly *"Do not use an ambient endpoint."* FIMRCC02 reaches a weaker version of the right conclusion by a wrong route, and marks it `NOT_ASSESSED` while claiming in the adjacent key to have identified its power.

---

## F15 — Smaller defects, all VERIFIED, none individually fatal.

- **"80 % power requires an effect of 0.80."** `fimrcc02_power.py:139-140` returns the first *grid point* reaching 0.80. I solved it: the true threshold at n = 28 is **p = 0.7630**. Published as a result in the artefact and in the commit message.
- **The ties table compares tests of different actual sizes.** I computed the realised two-sided size: n = 28 / k = 20 → **0.0357**; n = 21 / k = 16 → **0.0266**; n = 14 / k = 12 → **0.0129**. Part of the "power cost of ties" is the discrete test becoming three times more conservative. Not stated.
- **`CONSTAT_3` reports conditional power.** It fixes `n_d` rather than averaging over its distribution. Conservative and defensible, but it is the power of a test conditioned on the tie count, not the power of the procedure, and it is not labelled as such.
- **The parent is bound by a timestamp, not a hash.** `FIMRCC02_CLOSURE.json:7`: `"FIMRCC01_ENDPOINT_PREREGISTRATION": "2026-08-25T16:31:48.018905+00:00"`. FIMRCC01 binds its own pre-registration by `PREREGISTRATION_SHA256`. A timestamp string is not a binding; the file it names could change without detection.
- **The closure carries no `CODE_SHA256`** for `fimrcc02_closure.py`, though the power file self-hashes. There is no `SHA256SUMS` in `/home/claude/edl/FIMRCC02/out/`, unlike FIMRCC01, LDFMA01, OMLDCT01 and OMLDCT02.
- **"Il y a vingt minutes" is wrong.** The JSON key is `JE_RETIRE_UNE_PHRASE_QUE_J_AI_ECRITE_IL_Y_A_VINGT_MINUTES`. `GENERATED_UTC` 02:11:47 → 02:23:41 = **11 min 54 s**. Trivial in isolation; not trivial in a mission whose entire defence is *"La difference entre les deux n'est pas le resultat : c'est le moment."*

---

## F16 — `n_zero_steps`: the reading happens to be right, FIMRCC02 verifies none of it, and it cites the wrong provenance while inverting the lesson attached to the number.

VERIFIED, with a partial acquittal on the contamination question.

`/home/claude/edl/RPP98/code/rpp98_measure.py:43`: `"n_zero_steps": int(sum(1 for v in nc if v == 0))` where `nc = srow[:,7]` — the **online component count** (`FDOT01/code/fdot01_centres.components`, toroidal single-linkage at CORE_R = 5). Zero components means no Y-occupied cells, i.e. Y extinct.

**What FIMRCC02's code actually asserts** (`fimrcc02_power.py:64`) is `n_zero_steps > 0` ⇒ "Y éteint" — *any* zero-component step *anywhere in the 11 000-step trajectory*, with no check that it is after `t_m`, no check that it is terminal, and no use of `t_first_zero`, which the same record carries.

**I checked it from the shards and the reading holds — by luck, not by construction.** In all 19 arms with `n_zero_steps > 0`: `t_first_zero + n_zero_steps = 11000` **exactly**, and `t_first_zero > t_m` in every case. Extinction is absorbing here for a physical reason FIMRCC02 does not state and RPP98's checker did: Y birth is `p = min(1, kY·nX·nY)`, zero wherever `nY = 0` (`/home/claude/edl/TBRT02/code/tbrt02_c4bis_close.py:158`).

**On the withdrawal-taint question — using the number is legitimate, but not for the reason FIMRCC02 gives.** RPP98 was withdrawn for its *question* and its *claim*, not its integrity block, and that block was independently reproduced by an adverse checker: `RPP98_CHECKER_RETURN_VERBATIM.md` item 1 — own union-find, Euclidean ≤ 5.0, **6288 steps across 36 archives, 0 mismatches**, *"`components([])` returns `[]`, so 0 means Y extinct, as claimed"* — and item 5, *"Every published number reproduces under independent code ... the integrity block including `t_first_zero` min 761 / median 1525 / max 3221."* **That** is the provenance that launders the number. FIMRCC02 cites instead *"RPP98/work/shard*.json ... deja calcule et deja publie"* — the withdrawn mission's own work file, unverified, as though the fact of publication were the warrant.

**And it inverts the lesson attached to the number.** RPP98 F6: *"The per-archive counts are unnormalised against an arm-dependent denominator set by Y extinction ... The correct denominator (`n_zero_steps` per archive) is computed and stored by `rpp98_measure.py:41` **and never used**."* The checker's point is that `n_zero_steps` is the **exposure denominator**. FIMRCC02 uses it as a **binary death flag**, discarding exactly the graded exposure the checker identified as the right treatment — and thereby throws away the alive-fraction information (0.954 / 0.718 / 0.891, min 0.002) that would have shown the confound is a matter of degree in every arm, not a matter of 12 dead worlds.

---

## VERIFIED vs SUSPECTED

**Verified by my own computation, from committed files only:**
- Every number in `FIMRCC02_POWER.json` reproduces exactly; both content hashes verify; the code opens no archive.
- Extinction sets 12/2/5; 11/1/1/28; exact p = 13/2048; k\* = 20 at n = 28; the full power curve; the ties table.
- Type-I error under the realistic null: 0.2858 (E[p] = 0.259, median 0.154, P(p = 0.0063) = 0.049); the full α'(q) curve.
- E4 Σf² = 0.23967; marginal-only range 0.1942–0.2603.
- True 80 %-power threshold 0.7630; realised test sizes 0.0357 / 0.0266 / 0.0129.
- The E3 upper-bound table for the 11 seeds; 6 of 11 above TLMR01's median E3.
- OMLDCT02's 33 pairs: 18/14/1 sign split, sign-test p = 0.597, log-difference SD 1.453; both `NO_COMPONENT_AT_THE_NEXT_STEP` pairs favouring SELECTIVE.
- TBRT02 C4 §12 sign test: 24/7/10, p = 0.0243, tie rate 17.1 %.
- 22/22 `SPLIT_OR_TIE`, zero extinctions, in FIMRCC01's 22 source worlds.
- The gate reproduces its committed output exactly with FIMRCC02's terms (18 files); returns 28 with the names of the quantities, LDFMA01/OMLDCT01/OMLDCT02 at the top; returns 0 for two-term sets and still exits 0; `GATE01/` and all 18 `review/` files are structurally invisible; 3 distinct REASON strings across 18 judged files.
- `t_first_zero + n_zero_steps = 11000` and `t_first_zero > t_m` in all 19 extinct arms.
- Git: gate output committed in the same commit as the result it gates; the two artefacts are 11 min 54 s apart.

**Suspected, not verified:**
- That the sign of the E3 pair in extinct-SELECTIVE worlds is systematically *toward* SELECTIVE. Two observed pairs is a refutation of necessity, not an estimate of tendency.
- That E4's paired tie rate on TBRT02 would be materially below 25 %. Plausible from the E3 evidence; unmeasured.
- That the operator opened no archive outside the two committed scripts. The code paths are clean and the artefacts reproduce, but there is no session log; the closure's mission-wide claim (`AUCUNE_ARCHIVE_TBRT02_N_A_ETE_OUVERTE_PAR_CETTE_MISSION`) is broader than the file-level claim I can check, and the operator's own contamination note in `EDL_PRIOR_ART_MAP.json:88` says a great deal of TBRT02 has already been seen.

**Blocked by the absent archives:**
- Any actual E3, E4 or E5 value on TBRT02's 123 archives. Nothing here states what the frozen contrast would return. F1's refutation is by definition plus OMLDCT02's executed pairs, not by measurement on TBRT02.
- The paired tie rate, the paired difference distribution, and therefore the *true* power of any of the three endpoints on these 41 pairs.
- Whether TBRT02's 41 triples yield 41 pairs admissible under OMLDCT02's criteria (unique-exact daughter localisation, classifier agreement). F3 establishes that the frozen test exists, targets 41, and that TBRT02's SELECTIVE arm is declared to be OMLDCT02's treatment on disjoint seeds; it does **not** establish that 41 OMLDCT02-admissible pairs are recoverable. That is the one thing an archive-opening successor must check first, and it is the only honest reason FIMRCC02 could have given for not adopting the frozen test — and it gave a different, false one.

---

## What this leaves standing

Two things, and only two. The arithmetic reproduces bit-for-bit from committed code and committed inputs. And the *direction* of the concern in `CONSTAT_1` — that a raw paired count contrast on post-`t_m` quantities is contaminated by differential extinction — is correct, though it was established by RPP97's checker, established again with a table and an exposure-normalised correction by RPP98's checker, and written into `EDL_PRIOR_ART_MAP.json` by this operator four minutes before the mission began.

Everything the mission claims as its own is wrong: the p-value's premise (F1), the p-value's meaning (F2), the availability of a pre-registered test (F3), the truncation-by-death diagnosis (F4), the novelty (F5), the gate that certified the novelty (F6), the E4 bound (F7), the post-treatment retraction (F8), the identification of the power (F9), and the closing suggestion (F12). The mission stopped before opening an archive and called that the difference between itself and RPP97 and RPP98. The difference is smaller than that: RPP97 and RPP98 published false claims about data they had read; FIMRCC02 published false claims about data it had not read, on a question four earlier missions had already answered, behind a gate it configured so it could not see them.
