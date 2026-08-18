# PQEC01 — ADDENDUM DE CORRECTION DE RELECTURE

> Émis par FLCR01. **Aucun historique n'est réécrit.** Chaque nombre ci-dessous est *calculé*
> depuis les archives brutes ou depuis des objets Git ; rien n'est affirmé sans source.

## A. Provenance

**Portée du hachage de méthodes.** PQEC01_METHODS_HASH covered the DESIGN and the OBSERVER code only. The runner was NOT included in the pre-run methods hash, and neither was the analyser. Any reading of that hash as binding the whole method is withdrawn.

- couvert : `pqec01_design.py`, `pqec01_observer.py`, `pqec01_qualify.py`, `pqec01_freeze.py`
- **non couvert** : `pqec01_run.py (the runner)`, `pqec01_analyse.py (the analyser)`, `pqec01_manifest.py`, `pqec01_repair.py`

**Hachage d'exécution rétrospectif** (runner, moteur exact, observateur, manifeste gelé) :

```
c3a35a64daada5395f5e8b0fb415a1aec23ae92e6e45b4ceed167da96d6bb37f
```

*Ce qu'il prouve* : que ces octets sont ce que la livraison contient aujourd'hui.
*Ce qu'il ne prouve pas* : it is computed AFTER the runs. It cannot establish that the runner was fixed before the first start. Only the Git history can, and it shows the runner first appearing in C3, i.e. in the same commit as the outputs it produced -- not before them.

**Chronologie.** a complete analysis run, INCLUDING PQEC01_INTERNAL_VALIDATION.json, existed before the two analysis corrections were made. The operator therefore saw validation output before editing analysis code.

Reproductibilité : the pre-fix analyser was recovered from commit 7d97205 and re-run on the identical 128 raw archives; the pre-fix outputs below are regenerated, not remembered.

| test | avant correctif | après correctif | changé |
|---|---|---|---|
| B1 TEST 1 first birth | z = 0.876, PASS | z = 0.876, **PASS** | non |
| B1 TEST 2 two plus Y step fraction | z = -14.315, **FAIL** | z = 1.157, **PASS** | **oui** |
| B1 TEST 3 founder survival | z = -1.433, PASS | z = -1.433, **PASS** | non |
| B2 TEST 1 first birth | z = -0.832, PASS | z = -0.832, **PASS** | non |
| B2 TEST 2 two plus Y step fraction | z = -144.367, **FAIL** | z = -2.823, FAIL | non |
| B2 TEST 3 founder survival | z = 0.040, PASS | z = 0.040, **PASS** | non |

**Le changement du test B1.** a test moved from FAIL to PASS after its failure was visible. That is the shape of a post-hoc rescue. The defence -- that the fix restores a rule the freeze states verbatim (the unit is the world; frame pseudoreplication is forbidden) -- is a defence, not a proof.

**Disposition inchangée** : `PROSPECTIVE_Q_ENVIRONMENT_OPERATOR_NOT_IDENTIFIED__ADDITIONAL_INSTRUMENTATION_REQUIRED` avant comme après (11 portes contre 10).

## B. Comptes — vérifiés depuis les archives brutes

```
TOTAL_PHASE_B_WORLDS                   88
TOTAL_Y_BIRTHS                         56
WORLDS_REACHING_TWO_CENTRES            34
DISCOVERY_TWO_Y_COLOCATED_STEPS        12474
DISCOVERY_TWO_Y_SEPARATED_STEPS        73674
ALL_WORLD_COLOCATED_ONE_CENTRE_STEPS   17331
ALL_WORLD_TWO_Y_SEPARATED_STEPS        92635
ALL_WORLD_two_or_more_centre_steps     92649  (n_centres >= 2, inclut l'état P)
```

**Chiffre retiré.** 16474 is unsupported and is withdrawn. It appears to have been formed by mixing a discovery-only separated-state count into an all-world co-location count. The correct all-world co-located figure is 17331 and the correct discovery-only co-located figure is 12474.

Définitions : the two differ by the steps spent in three-or-more centres. Reporting n_centres >= 2 as 'separated' silently folds state P into state S; the state-S figures above use n_centres == 2 exactly.

## C. Flux de données

- **La partition de Phase A n'a pas été respectée** : phase_a() globs every A_*.npz and the region's exposure lower confidence bound is computed over ALL 40 Phase-A worlds. The frozen discovery/validation split (31/9) was never applied to Phase A.
- **Des quantités de validation de Phase B sont entrées dans le calcul de la région** : the region's separation statistics -- worlds reaching two centres, the median separation delay tau used as a criterion input -- were pooled over all 88 Phase-B worlds, validation included.

Littéraux retirés :

- `NO_REFIT_AFTER_VIEWING_VALIDATION` : WITHDRAWN — it is contradicted by the reproduced chronology above
- `NO_OUTCOME_DRIVEN_REPLACEMENT` : RECOMPUTED from the run ledger and the manifest (see COMPUTED_GATES)
- `NO_FRAME_PSEUDOREPLICATION` : WITHDRAWN as a literal; the pre-fix analyser demonstrably violated it
- `FEEDBACK_CONTROLLED_OR_EXPLICITLY_MODELLED` : already flipped to False in the PQEC01 repair round

all 128 worlds are POST_OUTCOME_DEVELOPMENT_DATA from this point on. No untouched holdout is reconstructed; the historical DISCOVERY/VALIDATION labels are retained only as a descriptive stability diagnostic and are never again called held-out.

## D. Pare-feu

file size, runtime and steps_recorded are all monotone in how long a world ran, and a world's run length IS its stop outcome. These three quantities were visible in the live run log, so outcome-dependent stop time leaked through the firewall during execution.

Corrélation `bytes` vs `steps_recorded` = **0.9992**. Médiane des tailles : 3476996 octets (arrêt précoce, n=42) contre 9939636 (horizon complet, n=46).

**Mais la fuite est inerte** : the leak is real but inert: the schedule was fixed by the freeze, every frozen seed ran exactly once, no reserve was drawn and no world was replaced or re-run. Nothing in the execution could have adapted to what leaked.

## E. Rétroaction — revendication retirée

« feedback not significant » est **retiré**. the published pooled comparison is confounded four ways at once: it conditions on nothing while the effect exists only where a birth occurred; worlds stop at outcome-dependent times; the analysis windows are therefore unequal; and the number of active X sources is itself the mechanism under test.

| point | comparaison | n | delta | relatif | z | signif. |
|---|---|---|---|---|---|---|
| B1 | pooled | 29 | +40.53 | +36.5 % | +4.28 | **oui** |
| B1 | birth worlds | 14 | +74.08 | +66.7 % | +6.03 | **oui** |
| B1 | no birth worlds | 15 | +9.21 | +8.3 % | +1.70 | non |
| B1 | horizon matched | 9 | +53.12 | +47.9 % | +4.24 | **oui** |
| B1 | matched time window | 22 | +16.31 | +14.4 % | +2.10 | **oui** |
| B2 | pooled | 44 | +16.91 | +15.2 % | +1.84 | non |
| B2 | birth worlds | 18 | +57.66 | +51.9 % | +5.88 | **oui** |
| B2 | no birth worlds | 26 | -11.29 | -10.2 % | -1.17 | non |
| B2 | horizon matched | 37 | +9.97 | +9.0 % | +1.03 | non |
| B2 | matched time window | 44 | +1.24 | +1.1 % | +0.17 | non |

- fenêtre appariée B1 : `[2000, 4000]`, 22 mondes sur 44 couvrent la fenêtre. this comparison is itself survivorship-biased: only worlds that lived past step 4000 can contribute, and living that long is an outcome. It removes the unequal-window confound and introduces a selection one; it is reported as a bound on the confound, not as a clean estimate.
  - fenêtre minimale naïve rejetée : largeur 1 pas — the shortest world sets the window; at B1 this gives a width of one step, which cannot support any comparison
- fenêtre appariée B2 : `[2000, 4000]`, 44 mondes sur 44 couvrent la fenêtre. this comparison is itself survivorship-biased: only worlds that lived past step 4000 can contribute, and living that long is an outcome. It removes the unequal-window confound and introduces a selection one; it is reported as a bound on the confound, not as a clean estimate.
  - fenêtre minimale naïve rejetée : largeur 2236 pas — the shortest world sets the window; at B1 this gives a width of one step, which cannot support any comparison

**Avertissement causal.** NONE of these comparisons identifies a causal effect. Whether a birth occurred is not randomised -- it is itself an outcome of the same exposure that drives X production, so birth-worlds are selected for high exposure. Stopping is outcome-dependent. PQEC01 cannot estimate this feedback cleanly and no causal number is claimed.

**Indice développemental conservé.** Y birth, and the appearance of multiple Y centres, may substantially increase X production. The mechanism is architecturally plausible: kX = 1.0 makes p_X = 1 wherever nX*nY >= 1, so a second Y at a different cell adds a saturated X source rather than competing for the first. This is a clue for the next design, not a measured effect.

## F. Incertitude de l'opérateur

`P(rester à Q = 0)` : valeur groupée publiée **0.8208**, sans incertitude. Au niveau du monde : **0.8106 ± 0.0557** (e.t. 0.0088, 40 mondes).

- a row-normalised matrix is row-stochastic by construction. Using `row_stochastic == True` as evidence of identification was tautological and is withdrawn as a gate.
- dominance d'un seul monde sur la ligne zéro : **0.0427**
- états d'exposition visités par moins de 5 mondes : `aucun`
- one world; the pooled transition table is NOT a sample of independent draws

