# ADVERSARIAL CHECK — RPP98

**Scope.** Read-only. Nothing in `/home/claude/edl` was modified; all scratch work in `/tmp/chk`. I recomputed every published figure with code I wrote from the preregistration's own definitions, never by importing or re-running RPP98's modules, over all 123 archives in `/home/claude/TBRT02_raw`. Where I needed the programme's frozen semantics (the state machine `state_of`, the trigger gates, the linkage rule) I read the frozen modules and re-implemented them rather than importing RPP98's reading of them.

---

## VERDICT

Every headline number in `RPP98_RESULT.json` reproduces exactly under independent code — 4760, 274, 4349, 148, 87, 123, 16, 13, 706, 1212, 0.2546, 0.7514, all seven `dist()` blocks to the last decimal, and the integrity block including `t_first_zero` quartiles. The archives are genuine: I verified all 123 against the sealed sha256 in `TBRT02/work/TBRT02_SEALED_LEDGER_*.jsonl` — 123 match, 0 mismatch, 0 missing, and all 123 `meta.t_m` agree with the ledger. `RESULT_CONTENT_HASH` and `CAPABILITY_CONTENT_HASH` verify, the four `CODE_SHA256` entries verify, and re-running `rpp98_capability.py` reproduces the committed capability file byte-for-byte except `GENERATED_UTC`. `s[:,7]` is exactly what RPP98 says it is. The detector is correct.

The science is not. **The question RPP98 declares has never been asked was answered four days earlier, in this repository, on 256 worlds at the same law, and the answer was published** (F1). **The event RPP98 counts is not the event the frozen trigger selects**: of its 148 "late persistent episodes", 5 contain a maturation-length run of the frozen state, and **2 would fire the frozen trigger** — in both, the two "components" are a one-cell speck and a one- or two-cell speck (F2). **The threefold pseudo-replication the checker found in RPP97 four commits earlier, and which the mission accepted in full, is repeated verbatim** (F3). **123 of the 274 persistent episodes are persistent by the trigger's own definition, not by observation**, and the published minimum of the headline time-fraction is exactly `250/11000` (F4). **`masse_parent` is absolute time** (Spearman 0.77; median 2 cells before `t_m`, 92 after), which is RPP97's second fatal error in a new coat (F5). **The per-archive counts are unnormalised against an arm-dependent denominator set by Y extinction**, which is RPP97's fatal flaw restated (F6), and the post-`t_m` window that §4 certifies as unable to be truncated is 99.8% dead in one SELECTIVE arm and more than half dead in 12 of 41 (F7).

---

## FINDINGS

### F1. The question was already asked and answered, in this repository, before RPP98 was written. §1 and the commit message are false.
**FATAL. This is the whole mission.**

`RPP98_PREREGISTRATION.md` §1:

> `n_components` est enregistré à chaque pas dans `s[:,7]` […] Le checker n'en a lu que la valeur finale. **La trajectoire complète du nombre de composantes n'a jamais été examinée** — ni par RPP97, ni par le checker, ni par TBRT02

and commit `15f0ab3`: *"the one chosen — the full n_components trajectory — has never been read by anyone."*

The enumeration "ni par RPP97, ni par le checker, ni par TBRT02" omits **TLMR01**, the mission that wrote the column, whose world file RPP98's own `DEFINITIONS` block cites by path.

`/home/claude/edl/TLMR01/code/tlmr01_offline.py` reads the full trajectory `for t in range(A.T)` and computes:

- **M1** (`tlmr01_offline.py:120-137`) — *"e(n) = P(the world holds two or more centres at t+1 | it holds exactly ONE centre at t)"*, plus, in `tlmr01_design.py:147`, *"the **FULL transition table** `n_components(t) -> n_components(t+1)` by n, so no later definition of a fork needs a re-run."*
- **M2** (`tlmr01_offline.py:139-170`) — maximal runs of the two-centre state, their lengths, whether they reach `NEED = 250`, and their terminators.
- **M4** (`tlmr01_offline.py:201-212`) — steps at exactly one centre and `fraction_of_horizon_single_centre`.

These are published in `/home/claude/edl/TLMR01/out/TLMR01_ANALYSIS.json`, generated **2026-08-25T14:07:05Z**, four days before RPP98, over 512 archives. For `LAW_C_MCTT01` — **the exact law TBRT02 runs** (`tbrt02_fork.py:31-32`), 256 worlds:

| TLMR01 published, LAW_C, 256 worlds | value | RPP98 headline, 123 archives | my recomputation of the TLMR01 quantity on those 123 archives |
|---|---|---|---|
| M1: 1 → ≥2 transitions | **8292** over 1 541 980 single-centre steps, rate **0.005378** | `n_episodes = 4760` | 4760 transitions over 868 636 single-centre steps, rate **0.00548** |
| M4: `median_horizon_fraction_single_centre` | **0.7497** | `FRACTION_DU_TEMPS_PAR_ARCHIVE median = 0.2431` | median fraction at exactly one component **0.7269** |
| M2: two-centre runs / of length ≥250 | **16368 / 44**, terminators `FORMED_A_THIRD_CENTRE 8434`, `MERGED_TO_ONE_CENTRE 7900`, `LOST_A_CENTRE_TO_A_SINGLE_Y 34` | — | 9360 / 129, same three terminators |

Every episode in RPP98 begins with a 1 → ≥2 transition, so **`n_episodes` *is* TLMR01's M1 numerator**, and the per-step rate reproduces TLMR01's published LAW_C rate to 2%. "How many, when, how long does the separation hold" is M1, M2 and M4.

It is worse than that. `TLMR01/out/TLMR01_PATH_COVERAGE.json` publishes, per world, **`n_descent_attempts`** — the number of 1→2 transitions the frozen trigger observed over the whole horizon (50 worlds, max 62) — and **`terminal_descent_step`**, the step of the **last** separation in the trajectory (max 5642). `FIMRCC01/work/pbd/*.json` publishes the same for 26 LAW_C worlds: `n_descent_attempts` median **44.5** (min 1, max 73, sum 1152) against RPP98's headline median **42 episodes per archive**; `descent_step_terminal` 5574 against `descent_step_at_t_m` 693 in world `P_i001`, with a field literally named `TERMINAL_AND_AT_TRIGGER_DESCENT_DIFFER: true`.

And `tlmr01_world.py:108-113` — in the file RPP98 cites — says it in prose:

> *"The frozen FMRCT01 trigger keeps OVERWRITING descent_level/descent_step at every later 1 -> 2 transition, so its terminal value is the LAST separation in the trajectory and not the one that named this parent."*

`FIMRCC01/out/FIMRCC01_PRECONDITION_B_RESULT.json:75` repeats it. That sentence is the answer to RPP98's question, in the repository, in the code RPP98 read to learn what `s[:,7]` is.

Lesser prior art, for completeness: `CLEA01/code/clea01_run.py:24` computes `AMBIENT_mean_components` over `[t_m, end]` on the sibling OMLDCT02 archives; `OBTC02/code/metrics_obtc.py:225-265` (`track_components`) counts fissions and fusions frame by frame; `TBRT02/code/tbrt02_connectivity_posthoc.py` was written to record `daughter_CERTAIN_set_ever_split_into_2_or_more` over the whole post-`t_m` trajectory (its output file `TBRT02_CONNECTIVITY_EXPOSURE.json` has `RECORDS: {}` — written, never run, so it is not itself a prior answer).

§0 is an elaborate instrument for avoiding contaminated questions. It swept the checker's return and swept nothing else, and it chose the one question the checker had not personally measured without checking whether the parent mission had. The preregistration's central novelty claim is false.

### F2. The "late persistent episodes" are not the event the frozen trigger selects. The threshold is borrowed; the object is not.
**FATAL to the headline claim. This is the difference between 148 and 2.**

§2 defines `PERSISTANT` as `duree ≥ 250` and justifies it: *"le même seuil que le déclencheur gelé de FDFLT01, repris pour comparabilité et non choisi ici."* The threshold is the trigger's. The **state it is applied to is not**.

The frozen trigger's object (`fmrt01_endpoint.py:22-27, 40-51`, `fdflt01_endpoint.py:38-45`) is a maximal run of state **S** = *integrity ok* AND *nY ≥ 2* AND **exactly two** centres — a third centre is state P and **breaks the run** — followed at `run_start + 249` by the local-X gate `f5_ratio ≥ 1 − 1/e`. RPP98's object is a maximal run of `n_components ≥ 2`, which merges S and P into one run (`rpp98_episodes.py:21, 43`).

I measured, on the archives:

- Of the **148** late persistent episodes, **146** reach `n_max ≥ 3` at some point. The median fraction of an episode's steps spent at exactly two components is **0.10**.
- **5 of 148** contain a run of ≥250 consecutive steps in state S. Longest S-run inside a late persistent episode: min 3, q1 12, **median 21**, q3 61, max 516.
- Applying the frozen gates (`ncen == 2`, `t ≤ 6500`, `f5_ratio(k_xd) ≥ 1 − 1/e`, exactly as `tlmr01_offline.py:167-176` does) to those 5 candidates: **2 fire**.

| index / arm | S-run | candidate step | component sizes (cells) | f5 | gate |
|---|---|---|---|---|---|
| i0365 SELECTIVE | 3393–3652 (260) | 3642 | [1, 1] | 0.621 | **FAIL** |
| i0391 SELECTIVE | 1248–1763 (516) | 1497 | [1, 2] | 0.845 | PASS |
| i0411 SELECTIVE | 989–1241 (253) | 1238 | [1, 5] | 0.481 | **FAIL** |
| i0664 SHAM | 1101–1502 (402) | 1350 | [1, 1] | 0.944 | PASS |
| i0793 DISPLACED | 2471–2753 (283) | 2720 | [1, 6] | 0.413 | **FAIL** |

**The trigger-grade answer to RPP98's own question is 2 events in 123 archives (2 of 41 worlds), and in both the two "bodies" are single cells.** The published answer is 148 in 87 of 123. The commit headline *"la fenêtre du déclencheur n'est pas le seul lieu où la question se pose"* is a claim about the trigger's question, evidenced by a count of a different and far weaker event.

The size dimension makes this worse, and it was in hand. RPP98 already reads `k_ncells` — it is `masse_parent`. It never reads it for the *second* component. I did:

- Second-largest component **at the first step of the episode**, all 4760 episodes: median **1 cell**; **57.6% are exactly 1 cell**.
- Second-largest component during **late persistent** episodes: median over the episode min 1, q1 2, **median 3**, q3 4, max 11. **89.9% have a median second component ≤ 5 cells.** Median largest component during those same episodes: **15.5 cells**.
- Episodes that are **both** maturation-length in state S **and** have a median second component ≥ 5 cells: **0 of 148**.

The typical "persistent multi-component episode" is a small cloud shedding a one-to-three-cell speck that stays more than five cells away. §9 forbids the word "division"; it does not stop the count from being presented as though the objects were comparable to the one the trigger names.

### F3. Threefold pseudo-replication — the identical finding RPP97 accepted four commits earlier.
**LOAD-BEARING for every reported n and every claim of weight.**

`RPP97_CHECKER_ADJUDICATION.json`, `F7_THREEFOLD_PSEUDO_REPLICATION`, verdict **ACCEPTED**: *"Real independent n is 41 worlds, not 123 archives."* `CLEA01_MATCHED_PAIR_MODEL_COMPARISON.json:5` states the programme's convention as a field: `THE_INDEPENDENT_UNIT_IS_THE_BASE_SEED: true`.

`tbrt02_fork.one_seed` runs one common prefix to `t_m` (`tbrt02_fork.py:46-58`), deep-copies it into three arms, intervenes, then runs each from `t_m + 1` (`tbrt02_fork.py:119-124`). I verified: **`s[0 .. t_m]` — all eight columns — is bit-identical across the three arms in 41 of 41 seeds**, and the arms' `n_components` first differ at exactly `t_m + 1` in 41 of 41.

Consequences in the published file, all verified by me:

- `n_episodes = 4760` contains **288 exact triplicates of 96 distinct pre-`t_m` episodes**, plus **123 copies of 41 distinct `t_m`-straddling episodes** whose start and whose first ≥250 steps are shared.
- The three "early persistent" episodes (274 − 148 − 123) are **one event**: seed 118, `t_start = 523`, `duree = 299`, counted three times.
- `n_archives_avec_tardif_persistant: 87` is **41 of 41 distinct base seeds**. Every world has one in at least one arm. "87 of 123" is a threefold restatement of "41 of 41".
- `N_EPISODES_PAR_ARCHIVE`, `DUREE_TOUS_EPISODES`, `MASSE_PARENT_TOUS_EPISODES`, `FRACTION_DU_TEMPS_PAR_ARCHIVE`, `t_start_TOUS_EPISODES` and `BORNE_DE_TRIVIALITE` all pool `n = 123` or `n = 4760` as if independent.

Nothing in the preregistration, the result file, or the commit message mentions the shared prefix. The mission wrote `RPP97_STATUS` into its own §10 and did not carry F7 across.

### F4. 123 of the 274 persistent episodes are persistent by construction. So is the minimum of the headline time-fraction.
**LOAD-BEARING for `n_persistants`, `FRACTION_PERSISTANTS_PAR_ARCHIVE`, `FRACTION_DU_TEMPS_PAR_ARCHIVE` and `n_chevauchant_t_m`.**

`t_m` is the 250th consecutive step of a run at exactly two centres. Therefore the `n_components ≥ 2` run containing `t_m` has length ≥ 250 **by definition**, in every archive. Verified: all 123 `t_m`-straddling episodes are persistent, minimum `duree` exactly **250**.

- `TOTAUX.n_chevauchant_t_m = 123` is not an observation; it is 1 per archive, forced.
- `n_persistants = 274` = **123 forced** + 3 (one event × 3 arms) + 148 late.
- `FRACTION_DU_TEMPS_PAR_ARCHIVE.min = 0.022727272727272728` is **exactly 250/11000** — the floor is the trigger's definition.
- `FRACTION_PERSISTANTS_PAR_ARCHIVE.max = 1.0` comes from seven archives that have **exactly one episode** — the forced one — because Y died: indices 866/DISPLACED, 793/SHAM, 768, 595, 530, 347, 124 with 7779–10018 dead steps each. `mean = 0.1327` against `median = 0.0588` is driven by those denominators of 1.

None of this is disclosed. §5's "borne de trivialité" is presented as the guard against a degenerate reading; it does not mention that nearly half the persistent episodes are the trigger's own selection criterion read back.

### F5. `masse_parent` is absolute time. This is RPP97's second fatal error, reproduced.
**LOAD-BEARING for `MASSE_PARENT_TOUS_EPISODES` and `MASSE_PARENT_EPISODES_TARDIFS`, which are two of the six preregistered quantities.**

`RPP97_CHECKER_ADJUDICATION.json`, `WHAT_A_SUCCESSOR_MUST_DO_DIFFERENTLY[4]`: *"test for a confound with absolute time by a leave-one-out predictor before claiming a trend."* Not done. §3's stated defence — *"sans échelle ou en comptages bruts, jamais des différences de densités contre un total mobile (leçon de RPP97)"* — guards against the *density* form of the error and walks into the *time* form.

Measured over all 4760 episodes: **Pearson corr(`t_start`, `masse_parent`) = 0.826, Spearman 0.771.**

| `t_start` bin | n | median `masse_parent` (cells) |
|---|---|---|
| [0, 500) | 242 | 2 |
| [500, 1000) | 252 | 3 |
| [1000, 2000) | 425 | 6 |
| [2000, 3000) | 924 | 73 |
| [3000, 4000) | 1679 | 97 |
| [4000, 6000) | 1163 | 112 |
| [6000, 11000) | 75 | 173 |

The published pair `MASSE_PARENT_TOUS_EPISODES median 88` vs `MASSE_PARENT_EPISODES_TARDIFS median 92` is a comparison a reader is invited to make (they sit adjacent in §3's own order). It carries no information: episodes with `t_start ≤ t_m` have median `masse_parent` **2 cells** (they happen at median t = 401); late ones **92** (median t = 3442). Restricted to a fixed time band `t_start ∈ [1000, 2000)`, late = 7, early = 2 — the residual is a fraction of the raw gap. The longest episode in the corpus (2957 steps, i0094 SHAM, `t_start = 167`) has `masse_parent = 3`.

Separately: median `masse_parent` for **late persistent** episodes is **13 cells**, not 92. The persistent separations happen in small or dying worlds, not in the 200-cell late clouds.

Separately again: §0 declares *"la **taille** des composantes sur tout l'horizon"* already seen and rules that *"toute statistique qui en dépendrait serait post-hoc."* `masse_parent` **is** a component-size statistic (`k_ncells`). Two of §3's six preregistered quantities are forbidden by §0 of the same document.

### F6. The per-archive counts are unnormalised against an arm-dependent denominator set by Y extinction. This is RPP97's fatal flaw, restated.
**LOAD-BEARING for `N_EPISODES_TARDIFS_PAR_ARCHIVE`, `FRACTION_DU_TEMPS_PAR_ARCHIVE` and the whole `PAR_BRAS_APRES_t_m` block.**

RPP97 died of an unnormalised statistic that rose with a growing total. RPP98's episode counts are unnormalised statistics that rise with **how long Y stayed alive**, which varies by arm for a reason that has nothing to do with separations.

Verified:

- **corr(total alive steps, `fraction_du_temps`) = 0.901** (Pearson). corr(alive post-`t_m` steps, `n_tardifs`) = 0.761 Pearson, 0.377 on ranks.
- All **16** archives with `n_tardifs = 0` are archives where Y went extinct. Median `n_episodes`: **2** in the 19 extinct archives, **45** in the other 104. Median `fraction_du_temps`: **0.031** vs **0.254**.
- Extinction by arm: SHAM 2, SELECTIVE **12**, DISPLACED 5 of 41.

The published per-arm table therefore reads:

| arm | published `N_EPISODES_TARDIFS_PAR_ARCHIVE` q1 / median | my late episodes per 1000 **alive** post-`t_m` steps (median) |
|---|---|---|
| SHAM | 29 / 42 | 4.17 |
| SELECTIVE | **1** / 40 | 3.78 |
| DISPLACED | 25 / 36 | 3.48 |

The SELECTIVE first quartile of **1** is not a fact about separations. It is 12 dead worlds. Normalised by exposure the three arms are 4.17 / 3.78 / 3.48 and the striking contrast disappears. The correct denominator (`n_zero_steps` per archive) is computed and stored by `rpp98_measure.py:41` and never used.

### F7. §4's feasibility check is a calendar check. The post-`t_m` window is empty by extinction, differentially by arm.
**LOAD-BEARING. §4 exists specifically to prevent this and does not.**

§4: *"`t_m` va de 370 à 1673, donc l'intervalle après `t_m` compte au minimum 9 327 pas […] **Il n'y a rien à tronquer.** Cette section est ce que RPP97 n'avait pas et qui lui a coûté sa fenêtre de contrôle."*

The arithmetic is right (I verified `t_m ∈ [370, 1673]`, 39 distinct values, all archives 11000 contiguous steps). The inference is wrong. Fraction of the nominal post-`t_m` window in which Y is still alive:

| arm | mean | median | min | archives below 50% |
|---|---|---|---|---|
| SHAM | 0.954 | 1.000 | 0.030 | 2 / 41 |
| SELECTIVE | **0.718** | 1.000 | **0.002** | **12 / 41** |
| DISPLACED | 0.891 | 1.000 | 0.013 | 5 / 41 |

Index 507 SELECTIVE: `t_m = 1552`, extinct at 1568 — **15 live steps** out of a nominal 9447. Index 595 SELECTIVE: 24. Index 124 SELECTIVE: 20.

§3's last bullet says the per-arm block exists *"pour que le contraste ne soit pas vide par construction."* The contrast built to avoid emptiness is differentially empty, in the arm whose intervention causes the emptiness. RPP97's checker flagged exactly this in its "what I did not check" item 7 — *"the parent removal kills the world in 12 of 41 SELECTIVE arms […] a further reason a post-`t_m` window would have produced a real arm contrast"* — and RPP98's §0, which claims to enumerate what has been seen, lists the 19 extinctions as a *number* while ignoring the warning attached to it.

### F8. The triviality bound is one-dimensional and tests the dimension that could not fail.
**LOAD-BEARING for §5 and §6.**

§5 defines the trivial case as *"innombrables et d'une durée de un ou deux pas"* and answers it with a duration distribution. `SECTION_6_NUL_2_indistinguable_du_scintillement` is computed as `n_episodes_duree_ge_250 == 0` — false the moment a single episode lasts 250 steps, which is guaranteed by construction in all 123 archives (F4). **The section-6 null #2 is unreachable by construction and the file records it as a measured `false`.**

The triviality that is actually present is one of **size**, not duration (F2): a one-cell speck five cells away for 400 steps produces a "persistent episode". The archive carries `k_ncells` per component per step; RPP98 opens that array (`rpp98_measure.py:31`) and uses it only for the parent. A second-component-size test costs the same read and would have produced a very different §6.

### F9. The SELECTIVE intervention truncates the `t_m` episode at exactly `t_m` in 41 of 41, and that truncation is pooled into the headline duration distribution.
**LOAD-BEARING for `DUREE_TOUS_EPISODES`.**

Verified timing semantics (schema `removal_semantics`; `tbrt02_fork.py:51, 85-87, 119-124`; and empirically): the row at step `t` is written **after** the update and **before** the intervention. `s[t_m, 7] == 2` in 123/123. At `t_m + 1`: **SELECTIVE 1 component in 41/41**, SHAM 2 in 41/41, DISPLACED 2 in 41/41.

Consequently the `t_m`-straddling episode ends at `t_end − t_m` = **0 in 41/41 SELECTIVE** archives (median 418 SHAM, 934 DISPLACED). Its `duree` is exactly 250 — the forced minimum — in every SELECTIVE archive. Those 41 mechanically-truncated durations sit inside `DUREE_TOUS_EPISODES` (n = 4760, q1 = 2, median 7, q3 = 20, max 2957) with no marker. RPP98 never states anywhere that the recorded value at `t_m` is pre-intervention, or that `tardif` (`t_start > t_m`, `rpp98_episodes.py:73`) happens to coincide with "post-intervention" — the boundary is right, and it is right by accident, justified only as *"strict : commencer EN t_m n'est pas tardif."*

### F10. `PAR_BRAS_APRES_t_m` is a three-arm contrast with no preregistered test, and what it shows is F6.
**LOAD-BEARING for anything a reader takes from it.**

§3's last bullet says *"par bras […] pour que le **contraste** ne soit pas vide par construction"* — the word is "contrast". `rpp98_aggregate.py:88-101` then prints five distributions for each of SHAM / SELECTIVE / DISPLACED side by side, including `n_archives_avec_au_moins_un_tardif_persistant` = 31 / 29 / 27. No test, no interval, no correction, no statement that the three arms of a seed are not independent, no denominator. The differences that stand out (`N_EPISODES_TARDIFS` q1 = 29 / 1 / 25; `MASSE_PARENT` q1 = 71.75 / 55 / 75) are extinction (F6) and the time confound (F5). Presenting three arms adjacent with no test is a contrast whether or not the word "test" appears.

### F11. Headline statistics that §3 never enumerated are reported unlabelled in `TOTAUX`, while innocuous ones are labelled "context only".
**MATERIAL. It is selective application of the mission's own honesty device.**

§3 enumerates six quantities. `TOTAUX` reports ten, of which `n_chevauchant_t_m`, `n_archives_sans_episode`, `n_archives_sans_tardif`, `n_archives_avec_tardif_persistant` and `n_max_global` are in none of them. **`n_archives_avec_tardif_persistant: 87` is the number the commit message leads with** and it is not a preregistered quantity. Meanwhile `t_start` and `n_max` — both defined in §2 — are quarantined under `NON_PREENREGISTRE__CONTEXTE_SEUL` with an explicit apology. `n_max_global = 13` appears in **both** blocks: unlabelled in `TOTAUX` and confessed as non-preregistered 40 lines later. The label is applied where it costs nothing and omitted where it would touch the headline.

### F12. §0 claims to list everything already seen and lists only numbers, not the checker's method findings — including the one it then repeats.
**MATERIAL. It is the mechanism by which F3 and F7 got through.**

§0 reproduces six *measured quantities* from `RPP97_CHECKER_RETURN_VERBATIM.md` and concludes the previously announced question is contaminated. It reproduces none of the checker's **method** findings, although the mission's own adjudication accepted all fifteen. Absent: F7 (threefold pseudo-replication) → repeated as F3 here. Absent: the checker's `CHECKED AND FOUND SOUND` item 7 (the three arms are bit-identical up to `t_m + 1`) → the fact that makes F3 unavoidable. Absent: the extinction warning → F7 here. A section titled *"CE QUI A DÉJÀ ÉTÉ VU, ET QUI EST DONC INTERDIT DE SERVIR ICI"* that filters for contaminated *outcomes* and discards inherited *errors* is a fairness device pointed in one direction.

### F13. `masse_parent` is a cell count called a mass, and "parent" is the noun §9 forbids.
**MATERIAL for the reading; the number itself is defined correctly in §2.**

`rpp98_measure.py:47-50` builds `mass[t] = max k_ncells`. `k_ncells` is the number of **cells**; the archive carries `k_nY`, the Y **mass**, in the adjacent column, unused. `RPP98_RESULT.json`'s `DEFINITIONS` block defines `n_components` and `n_components_zero` and says nothing about `masse_parent`, so a reader of the result file alone sees `MASSE_PARENT_TOUS_EPISODES median 88` with no way to know it is not a mass.

And §9 rules: *"On ne dira pas « division », ni « corps qui se divise », ni rien qui suppose qu'un objet s'est scindé plutôt que que deux amas ont dérivé au-delà du rayon de liaison."* An attribute named **`masse_parent`**, defined as the object at `t_start − 1`, asserts exactly the parent/offspring relation §9 forbids. It is carried into `RPP98_RESULT.json` five times as a top-level key. The vocabulary rule guards the prose and not the schema.

Note also that at `t_start − 1` there is at most one component by the definition of a maximal run, so "la plus grande composante" is vacuous and `max` is decoration. In these 123 archives the `None` branch (`rpp98_episodes.py:74`) never fires — I confirmed all 4760 `masse_parent` values are non-`None` — because Y extinction is absorbing (a Y birth needs `kY·nX·nY` at an occupied cell), so `n_components = 0` can never be followed by `n_components ≥ 2`. The docstring's careful discussion of that case describes an impossibility.

### F14. The capability test covers the detector and nothing else — the one component that could not have produced RPP97's failure.
**MATERIAL. It is a gate that cannot catch the class of error it was built after.**

I ran my own adversarial inputs against `rpp98_episodes`. The detector is **correct**: gaps in `t` cut, single-step crenels are episodes, zero cuts like one, boundaries are handled, `>=` is `>=`, duplicate/decreasing `t` and negative `nc` raise. Uncovered cases are inert here (`int()` truncation would silently turn `nc = 1.9` into 1 and lose an episode; `mass_by_step` returning a genuine `0` is indistinguishable downstream from a present-but-zero value; `t_m` outside the series makes every episode `tardif`) — none occurs with `int32` archive input.

But `MEASUREMENT_MAY_PROCEED` certifies only that. It does not test that `s[:,7]` is what §2 says (I tested that; it is — F-verified below). It does not test the `k_ncells → masse_parent` join against a real table. It does not test the `t_m` semantics against an archive. RPP97's three load-bearing errors were all in the scientific mapping — wrong species, wrong confound, wrong scope — and none of them lived in a detector. A capability gate scoped to the detector is a gate positioned where the last mission did not fail.

### F15. The measure never checks the archives against the seals.
**MATERIAL for provenance; not load-bearing, because I checked and they pass.**

`rpp98_measure.py:66-71` reads the sealed ledger for `ADMISSIBLE` and takes `os.path.basename(d["path"])` — it reads `d["sha256"]` never. The `INTEGRITY` block it does write checks contiguity and step count but not `meta["integrity_ok"]` either (all 123 are `true`; I checked). I verified all 123 sha256 against the ledger: **123 match, 0 mismatch, 0 missing**, and `meta.t_m == ledger.t_m` in 123/123. The RPP97 checker listed this as the first thing it had not checked; RPP98 had the ledger open and did not close it.

### F16. Minor.
- `DEFINITIONS.n_components` says *"adjacence <= CORE_R = 5.0"* without saying **Euclidean**. It is Euclidean (`fdot01_centres.py:51`, `dy*dy+dx*dx <= CORE_R*CORE_R`). A reader who assumed Chebyshev-5 would get a different series: on 2448 sampled steps, Chebyshev-5 agrees with the recorded value on only ~88%.
- `dist()` reports `mean` alongside quartiles for heavily skewed integer counts (`DUREE`: median 7, mean 63.99). Labelled, so not a defect, but the means are reported and the medians are not the ones the commit message quotes.
- `rpp98_measure.py:66-67` reads the ledger shards without deduplicating by index (`tbrt02_run._load` does). It happens to be safe — 885 lines, 41 admissible, 41 unique — and `rpp98_aggregate.py:37` asserts uniqueness downstream.

---

## RPP97'S FOUR FAILURES — ANALOGUES HERE

| RPP97 failure | Analogue in RPP98 |
|---|---|
| **Wrong molecule** (X is the autocatalyst, not the substrate) | **No analogue at the column level** — `s[:,7]` is exactly what RPP98 says, verified. **Direct analogue at the claim level (F2):** the counted object is a maximal run of `n_components ≥ 2`; the object the claim is about is the frozen state S with the local-X gate. 148 of the former; 2 of the latter. Weak secondary analogue in F13: `k_ncells` (cells) used and named as a mass while `k_nY` sits unused in the same archive. |
| **A temporal trend that was really absolute time** | **Direct analogue, F5.** `masse_parent` vs `t_start`: Spearman 0.77; median 2 cells before `t_m`, 92 after, 2 → 173 across time bins. The `MASSE_PARENT_TOUS_EPISODES` / `MASSE_PARENT_EPISODES_TARDIFS` pair is a time comparison. No leave-one-out confound test was run, although RPP97's adjudication lists that as successor requirement #5. |
| **A control window empty by construction** | **Direct analogue, F7**, in a new form. §4 checks the calendar and declares *"il n'y a rien à tronquer."* The window is not empty by calendar; it is empty by **extinction**, and differentially by arm — SELECTIVE mean alive fraction 0.718, 12 of 41 below half, minimum 0.002. And **F8/F4**: `SECTION_6_NUL_2` is unreachable by construction, and 123 of 274 persistent episodes are forced by the trigger's own definition — the mirror image, a window **full** by construction. |
| **A claim asserted at a scope the windows could not reach** | **Direct analogue, F2 and F3.** *"la fenêtre du déclencheur n'est pas le seul lieu où la question se pose"* is asserted at the scope of the trigger's question and established for a strictly weaker event, at a trigger-grade count of 2. And "87 archives sur 123" is asserted at archive scope over 41 base seeds with bit-identical prefixes — the same inflation the mission accepted as F7 four commits earlier. |

**Additionally, RPP97's accepted successor list** (`RPP97_CHECKER_ADJUDICATION.json / WHAT_A_SUCCESSOR_MUST_DO_DIFFERENTLY`): item 2 "never an unnormalised statistic against a moving total" — **violated** (F6); item 3 "check the window is reachable before freezing it" — **half done** (F7); item 5 "test for a confound with absolute time" — **not done** (F5); item 7 "guard the nouns" — **violated in the schema** (F13). Items 4 ("place a window after `t_m`") and 6 ("commit the aggregation code") are honoured, and item 6 demonstrably so: `rpp98_aggregate.py` regenerates the result file and its content hash verifies.

---

## VERIFIED BY COMPUTATION (as opposed to suspected)

1. **`s[:,7]` is exactly what RPP98 says.** I recomputed toroidal single-linkage components from the `c_y`/`c_x` cell rows with my own union-find at Euclidean distance ≤ 5.0 on **6288 steps across 36 archives** (including `t_m − 1, t_m, t_m + 1, t_m + 2`, the first two and last two steps of each): **0 mismatches**. `len(unique(c_cid))` and `s[:,6]` (`n_y_cells`) also match on every step checked. Chebyshev-5 disagrees on ~12%, so the rule is unambiguously Euclidean. `components([])` returns `[]`, so 0 means Y extinct, as claimed.
2. **Timing.** `s[t]` is written after the step's update and before any intervention. `s[t_m, 7] == 2` in 123/123; at `t_m + 1`, SELECTIVE has 1 component in 41/41 and SHAM/DISPLACED 2 in 41/41. No one-step offset.
3. **Prefix identity.** `s[0..t_m]` bit-identical across the three arms in **41 of 41** seeds; `n_components` first diverges at exactly `t_m + 1` in 41/41.
4. **Archive provenance.** 123/123 sha256 match the sealed ledger; 123/123 `meta.t_m` match; 123/123 `integrity_ok` true; 123/123 contiguous with 11000 steps; `t_m ∈ [370, 1673]`, 39 distinct values.
5. **Every published number reproduces** under independent code: `n_episodes 4760`, `n_persistants 274`, `n_tardifs 4349`, `n_tardifs_persistants 148`, `n_chevauchant_t_m 123`, `n_archives_sans_episode 0`, `n_archives_sans_tardif 16`, `n_archives_avec_tardif_persistant 87`, `n_max_global 13`; all seven `dist()` blocks (`N_EPISODES`, `FRACTION_PERSISTANTS`, `DUREE`, `MASSE_PARENT`, `N_EPISODES_TARDIFS`, `MASSE_PARENT_TARDIFS`, `FRACTION_DU_TEMPS`) to full float precision; `BORNE_DE_TRIVIALITE` 706 / 1212 / 0.2546218487394958 / 274 / 0.7513781136832981; the integrity block including `t_first_zero` min 761 / median 1525 / max 3221.
6. **Hashes.** `RESULT_CONTENT_HASH`, `CAPABILITY_CONTENT_HASH` and all four `CODE_SHA256` verify. Re-running `rpp98_capability.py` reproduces the committed capability file exactly except `GENERATED_UTC`, and the same content hash.
7. **The detector is correct** on the preregistered definition, including every case my own adversarial battery could construct.
8. **The prior art is real and dated.** `TLMR01_ANALYSIS.json` `GENERATED_UTC 2026-08-25T14:07:05Z`; RPP98 preregistration committed `15f0ab3`, result `f0403d4` at 2026-08-29T22:39:39Z.

## SUSPECTED, NOT PROVEN

- That the author read `tlmr01_design.py` and `TLMR01_ANALYSIS.json`. I have proved the files exist, are committed, predate RPP98, and answer the question at the same law; I have proved the author read `tlmr01_world.py` (it is cited by path in `DEFINITIONS`) and therefore was two files from `tlmr01_design.py:147` and inside the file containing the "LAST separation in the trajectory" comment. Whether the omission of TLMR01 from §1's list is negligence or selection, I cannot determine. **Either way §1 and commit `15f0ab3` are false as written, and that does not depend on intent.**
- That the per-arm block was intended as a test. `rpp98_aggregate.py` computes no comparison. My claim in F10 is that adjacency plus the word "contraste" functions as one, not that a test was coded.
- That the 2 trigger-grade late separations (F2) are "real" events in any stronger sense. Both involve one- and two-cell components. I did not attempt the `link` identity rule on them.

## WHAT I DID NOT CHECK

1. Whether the engine faithfully records the simulation. I verified `s[:,6]`, `s[:,7]` and `c_cid` against each other and against the frozen `components` rule, and nothing else; I re-ran no world.
2. The `ADMISSIBLE` selection in the sealed ledger, or `TBRT02_FORBIDDEN_SEEDS`.
3. TLMR01's 512 archives themselves. I read `TLMR01_ANALYSIS.json`, `TLMR01_PATH_COVERAGE.json` and `FIMRCC01/work/pbd/*.json` as published and recomputed the equivalent quantities only on TBRT02's 123 archives.
4. Statistical significance of anything. I report counts, medians, quartiles and two correlation coefficients. The units are correlated three ways (F3) and I made no correction beyond reducing to base seeds where I said so.
5. Whether re-running `rpp98_measure.py` reproduces `work/shard{0,1}.json` byte-for-byte. I reproduced their *contents* independently instead; the 123 records are unique by `(index, arm)` and 62 + 61 = 123 with no duplicates or omissions.
6. `RPP97/out/RPP97_STATEMENT.md` and the RPP97 result beyond what §0 quotes and what the checker's return and adjudication record.
