# MYQBD01 — dérivation d'une borne `Q` minoritaire, brut uniquement
## Rapport final, après relecture adversariale indépendante et l'unique round de réparation
## Zéro run scientifique

```
MISSION                    MINORITY-Y-Q-BOUND-DERIVATION-01
PARENT                     PROSPECTIVE-MINORITY-CHANNEL-REACHABILITY-01 (réparé)
PARENT_TIP                 8c2afa32e1e19ecf7ee5ff6e803dbb50cf2f0367
BRANCHE                    codex/minority-y-q-bound-derivation-01
GEL + ANALYSE (commit)     decfda575000775b1d49025af64636f6b2e97037
POINTE RELUE (pré-répar.)  f88147a3b5603aa2c301061c495fdd87200b3b55
POINTE FINALE              voir MANIFEST.txt de la livraison
FINAL_DISPOSITION          EXISTING_Q_DATA_INSUFFICIENT__PROSPECTIVE_Q_CALIBRATION_REQUIRED
ARCHITECTURE               NOT_ESTABLISHED
SCIENTIFIC_RUNS            0
REPAIR_COMMIT_COUNT        1
```

Les 28 bras OBFOR01 sont, sans exception, un **jeu de développement** :
`POST_OUTCOME_DEVELOPMENT_DIAGNOSTIC`. Aucune borne sur `Q` n'a été gelée avant leur exécution.
Ils servent à découvrir la structure de l'environnement et à concevoir un test futur ; ils ne
prouvent aucune fenêtre `kY`, aucune persistance, aucune séparation, ni reproduction ni hérédité.

Une relecture adversariale indépendante — la **deuxième** de MYQBD01, la §19 interne en ayant déjà
consommé une — a produit **32 constats** : **0 porteur**, 15 substantiels, 4 cosmétiques, **10
attaques sur 12 mises en échec**. Verdict : `CANDIDATE_DISPOSITION_SUPPORTED`. L'unique round de
réparation autorisé a été appliqué. **La disposition n'a pas bougé** ; ce sont les **certificats
d'appui** qui ont été refaits, et plusieurs étaient faux.

---

## Réponses aux dix questions

**1. Le `Q` enregistré correspond-il à la phase d'événement de l'ordonnanceur ?**
Oui, **exactement** — `Q_LEDGER_STATUS = EVENT_EXACT`. Écrit dans `pre_react` sur l'état
post-diffusion pré-réaction, il est le paramètre `n` exact du binôme de naissance `Y`.
*Correction du sceau :* la carte de phase citait `kinetics.py:117/119/120`. Ces lignes sont
**héritées, non exécutées** : la classe qui a tourné est
`run_obfor01.Instrumented(engine_obtc.WorldOBTC)`, dont `_react` appelle `_react_core`. Le site
exécuté est **`engine_obtc.py:162`** (`free0`, calculé **une seule fois** avant la boucle),
**`164`** (boucle d'espèces), **`165`** (clamp de `p`), **`166`** (`cand = min(nSY, free0)`),
**`167`** (tirage binomial). L'identité de phase est inchangée. Convention de pas également
explicitée et **vérifiée sur les 28 bras** : `series` étiquette 1…11000 (post-incrément), les
registres de sous-pas 0…10999 (pré-incrément), donc `series_step = ledger_step + 1`.

**2. Quelle information indépendante : 28 bras ou 308 000 trames ?**
**28 bras** (14 par branche). *Correction du sceau :* rapporter « IAT ~7–9 » seul était trompeur.
Estimateur nommé (séquence-initiale-positive à **paires chevauchantes**, celui qu'utilisait
réellement le candidat) :

```
statique  min 5,783  médiane 6,977  moyenne 7,177  max  9,719 (S__seed9300009)  IQR 0,744
mobile    min 5,335  médiane 6,461  moyenne 9,197  max 35,335 (M__seed9300015)  IQR 2,075
```

La médiane mobile est **sous** la moyenne statique : la moyenne mobile de 9,197 est tirée par un
seul bras à **3,84×** la moyenne. Quatre estimateurs divergent matériellement sur la queue — cet
écart *est* un constat, et PQEC01 devra en geler un. Un IAT plus grand signifie **moins**
d'information indépendante : cela **renforce** la disposition d'insuffisance.

**3. `β = kY·E[Q]` suffit-il ?**
`SCALAR_Q_REDUCTION_STATUS = EXACT_FOR_FIRST_BIRTH_IN_ONE_Y_UNCLAMPED_REGIME__INSUFFICIENT_FOR_
COMPLETE_TWO_Y_SPATIAL_WINDOW`. Le clamp `p = min(1, kY·nX·nY)` n'est actif **à aucun** des
126 000 pas examinés (il exigerait `nX ≥ 25 000` ; le maximum observé est de trois ordres en
dessous). *Correction du sceau :* deux des quatre motifs d'insuffisance avancés — corrélation
temporelle et écart moyenne/croissance multiplicative — pèsent **−2,047×10⁻⁴ en relatif** à
l'échelle admissible. C'était **trop pessimiste**. L'insuffisance repose désormais sur
l'exposition de descendant manquante, la structure à pool partagé et la rétroaction — pas sur une
erreur d'approximation exagérée.

**4. Le `Q` organisateur décrit-il l'exposition du descendant ?**
**Non**, et la preuve a été entièrement refaite : la version pré-sceau ouvrait **une archive sur
28**, n'inspectait le contenu d'**aucune** clé, et renvoyait un booléen **codé en dur**. Elle est
maintenant **dérivée sur les 28 archives** (inventaire de 420 lignes clé×bras) :

```
SOURCE_TRAJECTORY_POSITION_RESOLVED     = true    <- correction : le registre N'EST PAS scalaire
FULL_LATTICE_ENVIRONMENT_PER_STEP       = false
HISTORICAL_DESCENDANT_TRAJECTORY_EXISTS = false
DESCENDANT_Q_POSITION_RECONSTRUCTIBLE   = false   <- calculé, jamais assigné
```

`source_substep_ledger` est `(44000, 6)` = *(pas, espèce, y_avant, x_avant, y_après, x_après)* :
**4 colonnes sur 6 sont des coordonnées**. Le dire correctement **renforce** le dossier — la
trajectoire de l'organisateur étant tracée, `Q_ORGANISER` **est** l'exposition exacte du fondateur
dans la branche mobile aussi. Mais **savoir où est la source ne donne pas l'environnement
ailleurs** : `Q_POSITION(x,t)` exige `(nX, nSY, free)` à une *autre* cellule, à chaque pas. Aucun
tableau `(T,L,L)` n'existe, les 220 `frames` décodent en scalaires (résumés morphologiques JSON),
et l'archive est **~49× trop petite**. Raison **décisive** : `kY = 0` dans les 28 bras ⇒ `N_Y ≡ 1`
aux **308 000** pas ⇒ **aucun descendant n'a jamais existé**. Son environnement n'est pas
non enregistré : il n'y a pas de descendant dont ce serait l'environnement.

**5. L'opérateur exact à deux `Y` est-il identifiable ?**
`TWO_Y_OPERATOR_STATUS = EXECUTABLE_LOCAL_LAW_DERIVED__FULL_SPATIOTEMPORAL_OPERATOR_NOT_
IDENTIFIABLE_FROM_EXISTING_ARCHIVES`. Le moteur tire **un seul** binôme sur un pool partagé : deux
`Y` co-localisés portent `nY = 2` dans `p`, ils ne tirent pas chacun le leur. *Correction du
sceau :* le contre-exemple pré-sceau utilisait `kY = 0,05` et `0,20`, soit **1250× et 5000×** le
`kY` admissible. À l'échelle admissible (`kY = 4×10⁻⁵`, `c = 3`, `nX = 4`) : moyennes égales à
2×10⁻¹⁶ près, écart relatif de variance **−1,600×10⁻⁴**, distance en variation totale
**1,5×10⁻⁷**, masse que la loi indépendante place sur des issues **impossibles** :
**9,83×10⁻¹⁵**. Conclusion honnête :
`MEAN_ONLY_EQUIVALENCE_TO_HIGH_ACCURACY_IN_UNCLAMPED_ADMISSIBLE_REGIME__BUT_EXACT_SUPPORT_AND_
DEPENDENCE_ARE_NOT_GALTON_WATSON`. La non-indépendance est **structurellement décisive** (aucune
théorie de branchement ne s'applique) sans être **numériquement grande**. C'est pourquoi le
registre manquant, et non la correction de pool, reste porteur : dès qu'un descendant se sépare,
son exposition n'est plus une petite correction à une quantité enregistrée — c'est une quantité
**non enregistrée**.

**6. La rétroaction de `Y` est-elle contrôlée ?**
Seulement pour la première naissance — `FROZEN_ENVIRONMENT_FEEDBACK_NOT_FULLY_CONTROLLED`.
**Les deux chiffres du certificat pré-sceau étaient faux.** Trois conditionnements sont désormais
publiés séparément :

```
déplétion inconditionnelle          101,52 %   (mauvais dénominateur : moyenne sur des pas
                                                où aucune naissance n'est possible)
conditionnelle à cand_Y >= 1         55,13 %   <- LE CHIFFRE DE RÉFÉRENCE
pondérée par naissance réalisée      48,57 %   (dérivée : kY = 0, donc jamais observée)
```

Et le taux de récupération : `φ = 0,20` est le taux d'**offre** de `_exchange`, pas la
reconstitution. Le taux effectif **mesuré** sur les 14 bras statiques vaut **0,355735 ± 0,013473**,
soit **1,78×** le nominal — parce que la cellule reçoit aussi du `SY` par diffusion et en perd par
le prélèvement hypergéométrique. Les deux corrections vont dans le sens **conservateur** : la
perturbation réelle est plus petite et s'efface plus vite qu'annoncé. Au-delà de la première
naissance, rien n'est bornable depuis une archive à `kY = 0`.

**7. La région mobile est-elle non vide sur les 14 bras ?**
`MOBILE_DISCOVERY_REGION_STATUS = NOT_DERIVABLE_FROM_EXISTING_ARCHIVES`. Diagnostic
constructible : la première naissance est identifiable (`kY ∈ [3,2×10⁻⁵ ; 3,9×10⁻⁵]` pour une
naissance attendue), mais **chaque bras mobile a `Q10 = 0`** — aucun plancher d'exposition de
queue basse. Une borne inférieure ne peut donc pas venir d'une moyenne.

**8. Une calibration prospective de `Q` est-elle nécessaire ?** **Oui.**

**9. Un changement d'architecture est-il structurellement justifié ?**
**Non** — `STRUCTURAL_PRECLUSION_PROVED = false`. Deux témoins, tous deux étiquetés
`POST_OUTCOME_DEVELOPMENT_DIAGNOSTIC` :

```
représentatif (exposition mesurée des bras, E[Q] = 3,169730) : R = 1,000124838, marge 63,98× muY
favorable, ATYPIQUE (c = 3, nX = 4, exposition 12)          : R = 1,000478048, eta* = 0,004063547247
```

*Correction du sceau :* le témoin favorable était présenté comme « l'environnement admissible le
plus favorable, `Q` maintenu à `Q_MAX` » — faux sur ses propres termes, puisque `Q_MAX = 28` et
qu'il utilise 12 ; son pool est **3,12×** et son exposition **3,79×** les moyennes mesurées. Le
témoin qui porte désormais la conclusion est le **représentatif**, qui n'utilise **aucune**
magnitude gonflée. Un registre manquant n'est pas une preuve d'impossibilité.

**10. Prochaine éligibilité unique :** `PROSPECTIVE_Q_ENVIRONMENT_CALIBRATION_01`, avec ses deux
phases séparées (A : environnement spatial, `Y` inactif ; B : lignée `Y` à faible effectif), sa
taille d'échantillon **justifiée** (29 mondes pour une borne inférieure sans hypothèse de
distribution au 10ᵉ centile à 95 %) et son gel committé **seul**.

---

## Conformité zéro-run — établie en trois parties séparées

```
ORIGINAL_RUNTIME_SENTINEL_COVERAGE = INCOMPLETE
RETROSPECTIVE_STATIC_ZERO_RUN_PROOF = PASS
FINAL_REPAIR_RUNTIME_GUARDS = PASS
```

La sentinelle d'origine était installée dans **1 module sur 8** — non « sur tous les processus »,
comme l'annonçait le message de commit `decfda5` ; elle manquait `observe.seed_one_organiser`,
quatrième point d'entrée de graine ; et son témoin de fichiers globbait à profondeur 2, sans
jamais surveiller l'arbre du dépôt. **Cela n'est pas revendiqué rétroactivement comme corrigé.**

La conformité est établie par la **preuve statique d'imports** — aucun module d'analyse MYQBD01
n'importe `kinetics`, `lawspec_v2`, `engine_obtc`, `observe`, un protocole ou un lanceur, donc
aucun ne pouvait construire un monde, quel que soit un compteur — **combinée** au témoin de
fichiers **récursif, sans limite de profondeur**. Le garde du round de réparation patche
**4 constructeurs de `World`**, **9 pas d'ordonnanceur** et **les 4 points d'entrée de graine**,
audite `subprocess`, et son déclenchement est **prouvé par contrôle positif**. Une seule
exception est déclarée : le garde lui-même importe le moteur, uniquement pour le patcher.

```
ENGINE_CONSTRUCT_CALLS = 0   ENGINE_ADVANCE_CALLS = 0   SCIENTIFIC_WORLD_STARTS = 0
SCIENTIFIC_SEEDS_OPENED = 0  NEW_PHYSICS_ARRAYS_WRITTEN = 0
```

Un run ne se définit ni par la taille du réseau ni par le numéro de graine.

## Provenance — le défaut de gel, déclaré

```
FREEZE_FILE_EXISTS                    = true
INDEPENDENT_PRE_OUTCOME_FREEZE_COMMIT = false
```

Le gel maître et les statistiques détaillées sont dans le **même commit** `decfda5` : **zéro**
point de contrôle Git indépendant n'établit l'antériorité du gel. L'historique **n'est pas
réécrit** et aucun point de contrôle antérieur n'est inventé. Ce défaut ne renverse pas ce
résultat parce qu'il est **développemental et négatif** : une préinscription manquante ne peut
que gonfler une revendication positive, et il n'y en a aucune ici. Il **interdit** en revanche
toute formulation du type « préinscription mécaniquement appliquée » ou « committé
indépendamment avant analyse ». Le hash de méthodes reste un enregistrement de provenance — pas
une preuve de point de contrôle.

## Trois rôles de commit, à ne pas confondre

```
MASTER_FREEZE_AND_ANALYSIS_COMMIT = decfda575000775b1d49025af64636f6b2e97037
PRE_REPAIR_REVIEWED_TIP           = f88147a3b5603aa2c301061c495fdd87200b3b55
POST_REPAIR_FINAL_TIP             = voir MANIFEST.txt
```

```
H3_STATUS = NOT_TESTED   REPRODUCTION_STATUS = NOT_TESTED
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED   HISTORICAL_WINDOW_STATUS = NOT_PORTABLE
X_LAWSPEC_BASELINE = UNCHANGED   ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
SCIENTIFIC_RUNS_USED = 0   TOMMY_ACTION_REQUIRED = NONE
```
