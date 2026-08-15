# OBFOR01 — sceau confirmatoire de provenance et de revendication

```
TARGET_MISSION       ORGANIZER-BOUND-FULL-OPERATOR-RESIDUAL-01
TARGET_REPORTED      FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_QUALIFIED
FINAL_DISPOSITION    CONDITIONAL_FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_QUALIFIED
SCIENTIFIC_RUNS_USED 0
REVUE_ADVERSE        1 (obligatoire) — 6 défauts confirmés
TOUR_DE_RÉPARATION   1 (le seul autorisé) — appliqué, voir §7
```

Aucune affirmation en prose n'a été acceptée comme preuve. Tout est reconstruit depuis les
objets Git, les manifestes, les fichiers bruts et le code exécutable. **Y compris les
affirmations de ce sceau lui-même** : la revue adverse obligatoire a trouvé six défauts confirmés
dans une première rédaction, et §7 en rend compte sans les lisser.

---

## 1. Récupération hors ligne

Sept morceaux et l'archive complète vérifient leurs empreintes enregistrées. Sous `unshare -rn` :
`git fsck --full` propre, zéro objet manquant, aucun remote, aucun paquet promisor — **aucun
objet externe n'est requis**.

### La distinction de sommets tient, et elle compte

| sommet | valeur | ce que c'est réellement |
|---|---|---|
| `HISTORICAL_MTW01_PACKAGE_TIP` | `85ba2d8892b82e2d…` | l'unique tête du paquet **hors arbre** `MTW01_gen2_branch.bundle`. `git cat-file` ne le résout **pas** dans l'histoire livrée : **ce n'est pas un commit de cette histoire** |
| `OBTR01_PARENT_TIP` | `062d3735b726bb93…` | la frontière shallow, portée comme **commit réel** |
| `OBFOR01_FREEZE_TIP` | `050e666ed40dbcc1…` | le gel |
| `FIRST_FRESH_ARMS_COMMIT` | `0148acc7dcdc52d1…` | les 28 bras |
| `OBFOR01_FINAL_TIP` | `55e8812eee7ca48a…` | la tête livrée |

`DISTINCTION_HOLDS = true`. Confondre les deux aurait été une erreur de catégorie : l'un est la
tête d'un paquet historique récupéré hors dépôt, l'autre le parent de la mission.

**Commits** : 10 nouveaux commits OBFOR01 ; 11 atteignables dans l'histoire livrée — le onzième
étant la frontière. La revendication « 10 commits » est exacte.

Le push n'a **pas** été retenté. Le 403 est une limite d'autorisation de session, pas un défaut
scientifique.

## 2. Statut prospectif des 28 bras

**Les quatorze fichiers porteurs sont présents dans l'arbre du commit de gel et sont identiques
au bit près à HEAD** : `_freeze.json`, `m6`, `run`, `residual`, `mechanisms`, `observables`, les
deux yaml de protocole, `kinetics.py`, `lawspec_v2.py`, `engine_obtc.py`, `metrics_obtc.py`,
`protocol_obtc02.py`. Rien de porteur n'a bougé après le gel.

Le commit de gel contient déjà, sous forme lisible par machine : la définition complète du
modèle, les valeurs de prédiction et l'algorithme qui les produit, la marge de ±2,9 %, le nombre
et l'allocation des bras, les 28 graines énumérées, l'unité expérimentale indépendante, les trois
critères primaires, les règles d'inclusion et d'invalidité technique, la procédure d'équivalence
et la règle de non-retune.

### Comptage des bras

28 déclarés au gel, 28 présents, 28 analysables, **aucune extinction**, aucune graine dupliquée,
aucune réutilisation des 377 graines retirées, un blob brut dans l'arbre pour chaque bras, et
**chaque bras inclus** dans l'analyse finale. Les 28 ont été soumis en **un seul `pool.map`**
depuis le registre gelé : aucun bras n'a donc pu être inspecté avant que les choix d'un bras
ultérieur ne soient fixés.

Horodatages employés **comme preuve d'ordre seulement** : gel à l'époque 1786798437, bras à
1786799147, écart 710 s. La preuve liante est le contenu de l'arbre, pas l'horloge.

### Faiblesse divulguée, non lissée

`adjudicate_obfor01.py`, la figure, la livraison et la relecture **n'existaient pas** au gel. La
**règle** de décision, les trois critères, la marge, le registre de graines, le budget, la règle
d'inclusion et la règle d'ablation étaient tous dans `_freeze.json` au gel ; le **code qui les
évalue** a été écrit après les bras. C'est une faiblesse de forme, pas de fond — aucun seuil,
aucun critère, aucune graine, aucun comptage n'a changé — mais elle est consignée. Une
conséquence concrète en est tirée en §4E.

### Conformité à l'autorisation de runs — *statut révisé*

La première rédaction de ce sceau concluait `PASS`. **Ce verdict est retiré**, non parce qu'une
violation aurait été trouvée, mais parce qu'il n'était pas démontrable depuis la livraison. Il
reposait sur trois piliers dont un seul est une preuve :

| pilier | lisible dans l'arbre livré ? | statut |
|---|---|---|
| OBTR01 liste *« the absolute radial deficit found in §15 »* comme `ELIGIBLE_AT_THE_QUALIFIED_POINT` | **oui** — `OBTR01/out/_freeze.json` → `NEXT_ELIGIBILITY` | **preuve** : la *question* confiée à OBFOR01 était ouverte |
| le mandat d'OBFOR01 (§16–§20 : phase raw-only, critère d'ouverture, conditions S/M/E, statistiques, **budget de runs**) | **non** | prose invérifiable sur un document absent du dépôt |
| le handoff ultérieur `…RECONSTRUCTION-01` portant `NEW_ENGINE_STARTS = 0`, arrivé après livraison | **non** | prose invérifiable sur un document absent du dépôt |

Un sceau dont l'instruction fondatrice est *« do not accept prose claims as evidence »* ne peut
pas certifier une conformité à partir de prose — fût-elle la sienne. Le pilier 1 établit que la
question était ouverte ; il n'établit pas quel budget de runs le mandat gouvernant avait fixé,
parce que ce mandat n'est pas dans l'arbre.

**Défaut réel trouvé au passage** : la chaîne d'éligibilité d'OBTR01 se lit trop facilement
comme une interdiction générale de runs, parce que le qualificatif de portée `FOR_THIS_QUESTION`
est enfoui dans le jeton. C'est un défaut de *rapport*.

**Correctif de procédure** : verser le texte du handoff gouvernant — ou son empreinte — dans le
dépôt à l'ouverture de chaque mission. Tant que ce n'est pas fait, la conformité de budget n'est
pas une propriété vérifiable de la livraison.

```
ORIGINAL_ZERO_RUN_MISSION_COMPLIANCE = NOT_DETERMINABLE_FROM_THE_DELIVERED_EVIDENCE
                                       (constat d'invérifiabilité, non de violation :
                                        aucune preuve de dépassement n'a été trouvée non plus)
FRESH_SUBSTUDY_PROSPECTIVITY         = PASS
```

## 3. Flux d'information des prédictions

Tracé en **analysant le prédicteur gelé**, pas en lisant sa docstring.

| entrée | catégorie | traitement |
|---|---|---|
| point du LawSpec, noyaux exacts, condition, taille, horizon, burn-in, cadence, 28 graines | **A** | connus avant le run |
| **trajectoire de l'organisateur** | **A** | **SIMULÉE EX ANTE**, partagée par construction dans chaque bras simulé. Aucun chemin réalisé du moteur n'est injecté : `simulate_arm` tire lui-même les incréments de l'organisateur depuis le même noyau exact |
| **loi de flux de naissance** | **B** | **MESURÉE** sur 40 bras historiques et injectée comme loi. Non-cible pour les bras frais, gelée avant eux. **Conditionnante par provenance** — voir ci-dessous |
| `N_X` des bras historiques | B | sert **uniquement** à écarter les bras éteints du calcul du flux ; non porteur |
| refus de capacité | non utilisé | non simulés, bornés séparément à 0,018 % sur `r80` |
| tore fini, ordre des événements | A | appliqués par construction, transcrits depuis la source |
| `r80`, `M2`, profil observés de **quelque** bras | **C** | **non utilisés**. `simulate_arm` ne prend aucune statistique observée et n'en référence aucune ; les valeurs observées ne sont lues qu'ensuite, pour comparer |

### Le flux de naissance n'est pas « porteur à 1,27 point » — ce chiffre est retiré

La première rédaction justifiait `CONDITIONAL` par un nombre : remplacer le flux mesuré par une
source de Poisson de même moyenne déplacerait la prédiction mobile de **1,27 point**. Ce nombre
provenait d'**un** run de 30 bras comparé à **un** autre run de 30 bras. Le tour de réparation l'a
répliqué **16 fois de chaque côté** :

| | prédiction mobile (moyenne de 16 répliques × 30 bras) | écart-type entre répliques |
|---|---|---|
| flux empirique mesuré | **−4,803 %** | 0,563 |
| source de Poisson, même moyenne | **−5,218 %** | 0,548 |
| **différence** | **+0,41 ± 0,20 point** (t = 2,11, 30 ddl) | — |

L'effet annoncé était de **−1,27 point** : la réplication donne un effet trois fois plus petit et
**de signe opposé**. Les deux runs gelés se situent à **−1,58** et **+1,45** écarts-types de leurs
propres moyennes de réplique, dans des directions opposées : les 1,27 point étaient deux
excursions Monte-Carlo ordinaires lues comme un mécanisme. Le côté statique de la même ablation
donnait déjà 0,068 point, dix-neuf fois moins — l'alerte était disponible et n'a pas été levée.

**Réponse en dose, avec contrôle de délivrance.** Doubler l'intensité de la source déplace la
prédiction mobile de **+0,01 ± 0,23 point** (t = 0,04), alors que le nuage double bien
(115,2 → 235,6 particules en fenêtre). Le résidu `r80` résumé par la médiane est donc
**invariant d'intensité** dans le régime testé : le biais de population finie est déjà saturé à
N ≈ 117, et le résidu est porté par la trajectoire partagée, pas par la force de la source.

### Pourquoi la qualification reste malgré tout conditionnelle

La justification numérique tombe ; la justification **dérivationnelle** demeure, et elle suffit :

> M6 ne peut pas démarrer sans qu'on lui remette une loi de flux de naissance **mesurée sur la
> sortie du moteur**. Il ne dérive pas la source depuis le chémostat : on la lui donne. Une
> prédiction dont les entrées comprennent une mesure du système prédit est conditionnelle à cette
> mesure, quelle que soit sa sensibilité numérique.

Le classificateur du sceau a été corrigé en conséquence. Il testait `load_bearing`, un drapeau
**saisi à la main** ; une fois ce drapeau ramené à sa valeur mesurée, cette version aurait émis
`UNCONDITIONAL`. Elle est nommée ici, et rejetée : « l'entrée pèse peu » n'est pas « l'opérateur
n'a pas besoin de l'entrée ». On ne relève pas une revendication sur la foi d'un résultat nul.
L'insensibilité mesurée est rapportée comme un résultat de **robustesse**, pas comme une licence.

```
STATIC_PREDICTION_MODE = CONDITIONAL   (fondement : provenance de l'entrée, non sensibilité)
MOBILE_PREDICTION_MODE = CONDITIONAL
RATIO_PREDICTION_MODE  = CONDITIONAL
```

**Divulgué** : le terme d'échantillonnage de la marge de ±2,9 % est dimensionné sur la
**dispersion historique** de `r80`. C'est une dispersion, pas une moyenne ; elle ne peut pas
déplacer la comparaison ponctuelle ; elle était gelée avant les bras frais.

## 4. Recomputation de chaque nombre porteur

### A. Analyse historique / développementale

```
116 bras confirmés exactement : 41 / 37 / 38 à L = 36 / 72 / 96, une graine par unité
profil radial : max |z| 0,6357 (annoncé 0,64) ; écart de probabilité max 0,00378 (annoncé 0,0038)

r80, règle MÉDIANE   mobile -5,10 % (z -16,57)   statique -1,83 % (z -1,51)
r80, règle MOYENNE   mobile -0,70 % (z  -1,85)   statique -1,39 % (z -0,76)
M2                   mobile +1,61 % (z  +0,39)   statique +4,02 % (z +0,33)

dispersion intra-bras 1,780 mobile contre 0,783 en tirages indépendants -> facteur 2,27
asymétrie +1,072 mobile contre +0,313 statique
```

Tous ces nombres se reproduisent. **Mais leur reproduction n'est pas une vérification
indépendante** : `seal_flow_and_numbers.historical()` ré-implémente au caractère près les
conditions d'inclusion de la mission. Ré-exécuter un filtre ne peut que confirmer qu'il a été
exécuté ; c'est structurellement incapable de détecter que le filtre lui-même sélectionne sur un
résultat. Le sceau a donc **fait varier la règle** au lieu de la répéter.

#### La règle d'inclusion conditionne sur un résultat

`residual_obfor01.py` ne garde un bras que si `nY_final ≥ 1` **et** `nX_final ≥ 40` **et** au
moins 50 trames en fenêtre. Or `nX_final` est la **population terminale** : un *résultat* du bras,
pas une variable de conception.

| règle | n | résidu mobile médian | erreur-type | z |
|---|---|---|---|---|
| **règle de la mission** (`nX_final ≥ 40`, ≥ 50 trames) | 116 | **−5,101 %** | 0,308 | −16,6 |
| seuil de population retiré, ≥ 50 trames conservé | 126 | **−4,348 %** | 0,478 | −9,1 |
| aucun seuil dépendant du résultat | 129 | **−2,144 %** | 1,539 | **−1,39** |

Les dix bras écartés portent des résidus systématiquement **plus élevés** (+33,4 ; +19,9 ; +5,0 ;
+4,7 ; +4,7 …) et huit d'entre eux ont `nX_final = 0` : la règle pousse la valeur de tête vers le
bas. Au niveau le plus permissif le résidu historique **n'est plus distinguable de zéro**
(z = −1,39) — mais ce niveau admet des bras quasi éteints et son erreur-type est cinq fois plus
grande. L'énoncé défendable est donc :

> La magnitude −5,10 % est une propriété conjointe de l'observable **et** de la règle
> d'inclusion. Le déplacement imputable à la règle est de 0,75 point au niveau comparable et
> jusqu'à 2,96 points au niveau le plus permissif.

**Trois bornes du défaut, énoncées pour ne pas l'exagérer.**

1. Les **28 bras frais ne sont pas filtrés** : 28 déclarés = 28 présents = 28 inclus, aucun
   éteint. La confirmation fraîche ne subit pas cette sélection.
2. La **loi de flux** n'est pas filtrée par cette règle (`empirical_birth_flux` n'écarte que les
   bras éteints), donc les prédictions gelées n'en dépendent pas.
3. La dispersion inter-bras utilisée pour dimensionner la marge (4,15 %) provient du jeu
   **filtré** ; sans filtre elle vaut 5,4 % voire 17,5 %. Une marge dimensionnée sans filtre
   aurait donc été **plus large**, donc plus permissive : sur ce point la mission s'est pénalisée
   elle-même.

Le défaut porte sur le nombre **motivant** d'OBFOR01, pas sur ses critères confirmatoires.

### B. Confirmation fraîche sur 28 bras

Résumés par bras **recalculés depuis les `.npz` bruts** et reproduisant l'enregistrement
exactement.

| critère | n | prédit (± σ Monte-Carlo) | observé | erreur relative | règle gelée ±2,9 % |
|---|---|---|---|---|---|
| profil absolu statique | 14 | 6,0076 ± 0,315 % | 5,9991 | −0,14 % | **dedans** |
| profil absolu mobile | 14 | 8,0574 ± 0,563 % | 8,0771 | +0,24 % | **dedans** |
| rapport mobile/statique | 14/14 | 1,3412 ± 0,645 % | 1,3464 | +0,39 % | **dedans** |

La colonne σ est nouvelle et obligatoire : c'est l'écart-type Monte-Carlo de la **prédiction
elle-même**, mesuré sur 16 répliques indépendantes du plan gelé à 30 bras. L'artefact gelé ne
publiait que l'erreur-type intra-réplique (0,275 / 0,602). **Une prédiction ponctuelle assortie
d'un σ non déclaré de ±0,56 % n'est pas un point.** Conséquence directe : la prédiction mobile
gelée (−5,69 %) est elle-même à −1,58 σ de la moyenne répliquée (−4,80 %) ; jugée contre cette
moyenne, l'observation fraîche s'écarterait de **−0,69 %** au lieu de +0,24 % — toujours très à
l'intérieur de la marge, mais la précision apparente de l'accord initial devait une part à la
chance.

#### Le test passe — et il ne discrimine pas grand-chose

Un **témoin sans physique**, disponible avant l'ouverture d'OBFOR01 puisqu'il ne demande que les
bras déjà livrés par OBDI02 et OBTC02 — « les bras frais ressembleront aux bras historiques »,
c'est-à-dire la moyenne des médianes historiques (statique : 5,9712 sur 3 bras ; mobile L = 36 :
8,1021 sur 41 bras ; rapport 1,3569) — a été soumis aux **trois mêmes critères gelés** :

| modèle | statique | mobile | rapport | verdict à ±2,9 % |
|---|---|---|---|---|
| M6 complet (la mission) | −0,14 % | +0,24 % | +0,39 % | passe |
| **témoin sans physique (copie historique)** | **+0,47 %** | **−0,31 %** | **−0,77 %** | **passe aussi** |
| idéal non corrigé | −1,38 % | **−5,46 %** | — | **rejeté sur le mobile** |
| M6 sans trajectoire partagée | — | **−3,55 %** | — | **rejeté sur le mobile** |

Deux conclusions, l'une négative et l'autre positive, et il faut les deux :

- Les bras frais **ne séparent pas** l'opérateur d'une simple ressemblance historique. Écrire que
  l'opérateur « prédit prospectivement » suggère un pouvoir discriminant que ce plan n'a pas.
- Les bras frais **séparent bien** la trajectoire organisatrice partagée de son absence, et
  l'opérateur corrigé de l'opérateur idéal nu. C'est un résultat de mécanisme, et il tient.

Noter aussi que le **critère statique ne discrimine rien** : même l'idéal non corrigé y passe
(−1,38 %). Seuls le critère mobile et le rapport portent de l'information sur le mécanisme.

L'énoncé correct est donc : *trois prédictions énoncées à l'avance n'ont pas été falsifiées, et à
l'intérieur du même test le mécanisme de trajectoire partagée est requis.*

**Dépendance du rapport** : les bras statiques et mobiles sont des ensembles de graines
**disjoints**, tirés d'un registre gelé unique et exécutés en un seul lot. Les deux moyennes sont
donc indépendantes et la variance delta est la somme des deux variances relatives. Les traiter
comme appariés serait faux : il n'y a aucun appariement.

### C. Ablations et décomposition

```
distances : complet 0,0197 | sans trajectoire partagée 0,2975 | Poisson 0,0889 | idéal non corrigé 0,4669
facteurs recalculés : 15,1 | 4,51 | 23,7   (annoncés 15 | 4,5 | 24)
séquentielle : -0,66 -> -4,42 -> -5,69, observé moteur L36 -5,17
factorielle : trajectoire -3,74 | flux -1,30 | interaction +0,06
erreur du modèle continu : -18,74 % statique, -19,29 % mobile
ordre intra-pas 0,201 % | refus de capacité 0,018 % | tore fini sous un pas de quantification
```

**Ce qui survit à la réplication, et ce qui n'y survit pas :**

| terme | valeur gelée | survit ? | pourquoi |
|---|---|---|---|
| effet principal **trajectoire partagée** | −3,74 pt | **oui** | ≈ 6 σ de réplique (0,563 pt) et confirmé indépendamment sur les bras frais : sans lui l'écart au mobile est −3,55 %, hors marge |
| effet principal **flux de naissance** | −1,30 pt | **non** | la réplication donne +0,41 ± 0,20 pt, de signe opposé |
| interaction | +0,06 pt | **non** | sous le bruit |

**Le « facteur 4,5 » n'est pas un rejet.** La variante à source de Poisson est 4,5 fois plus
éloignée de l'observation que le modèle complet, mais son propre résidu vaut −4,42 % contre une
observation de −5,17 % : elle **passe** le critère primaire à ±2,9 % pour son propre compte.
Rapporter un modèle qui passe sous forme de rapport de distances le fait paraître rejeté. Il ne
l'est pas — et la différence sous-jacente ne se réplique même pas.

**Gelé avant les runs frais** : les prédictions d'ablation elles-mêmes, la règle d'ablation, la
décomposition séquentielle et factorielle — toutes dans l'arbre du commit de gel.
**Diagnostics post-outcome** : les distances observées, l'arithmétique des facteurs, la
comparaison continu→discret. **Aucune ablation post-outcome n'est le test confirmatoire
primaire** : les trois critères primaires sont les profils absolus et leur rapport, tous gelés.

### D. Portée de la revendication

| niveau | statut |
|---|---|
| mise à jour d'état conditionnelle exacte | `CONDITIONAL_EXACT` |
| prédiction au niveau des observables | **qualifiée pour les trois observables testées** |
| fermeture de la densité marginale | `NOT_CLOSED` |
| théorie physique d'état complet | non revendiquée |

**Correction apportée à une formulation trop large.** Les résidus `M2` portent des intervalles
très larges : mobile **+1,61 % [−6,56 ; +9,78]**, statique **+4,02 % [−20,15 ; +28,19]**. Zéro
est dans les deux, donc **aucun déficit n'est détecté** — mais un résidu exactement nul **n'est
pas établi**. « `M2` concorde » ne doit pas devenir « `M2` est exactement nul » : la puissance
est faible. La branche statique repose par ailleurs sur **trois** bras historiques.

### E. Le critère de décision : ce qui était gelé, et ce qui ne l'était pas

Le texte gelé est une **règle ponctuelle**, sans intervalle, sans niveau de confiance et sans
quantile :

> `"RULE": "the observed value must lie within ±2,9 % of the M6 point prediction, relatively"`

Le critère « **intervalle entier** à l'intérieur », le facteur 1,96, la variance delta du rapport
et le `TOST_style_p` apparaissent tous pour la première fois dans `adjudicate_obfor01.py`,
committé en `cb1aaa2`, c'est-à-dire **après** les bras (`0148acc`). Ils sont **post-gel**.

- *À décharge* : ce critère est **plus strict** que la règle gelée. L'appliquer ne pouvait que
  rendre le passage plus difficile.
- *À charge* : δ = 2,9 avait été dimensionné comme ≈ 2 erreurs-types d'échantillonnage de cette
  expérience même ; un critère qui ajoute ensuite 1,96 erreur-type consomme presque toute la
  marge. Il n'est passé confortablement que parce que les bras frais se sont révélés moins
  dispersés que supposé (2,71 % contre les 4,15 % historiques ayant servi au dimensionnement).

**Le critère de référence est donc la règle ponctuelle gelée.** L'intervalle entier est rapporté
à côté, comme supplément post-gel plus strict :

| critère | statique | mobile | rapport | marge |
|---|---|---|---|---|
| **point (règle gelée, référence)** | −0,14 % | +0,24 % | +0,39 % | 2,9 |
| intervalle entier, normale 1,96 (post-gel) | 1,049 | 1,666 | 2,071 | 2,9 |
| intervalle entier, Student (13 / 13 / 26 ddl) | 1,142 | 1,811 | 2,153 | 2,9 |
| idem, σ de la prédiction propagé | 1,351 | 2,228 | **2,595** | 2,9 |

Deux corrections statistiques :

- Le `TOST_style_p` employait une queue **normale** sur une erreur-type à **13 degrés de
  liberté**. Corrigé sur une loi de Student : statique **2,38 × 10⁻⁵** au lieu de 1,28 × 10⁻⁹
  (facteur ≈ 18 600), mobile **1,44 × 10⁻³** au lieu de 1,26 × 10⁻⁴ (facteur ≈ 11). La conclusion
  d'équivalence tient ; la p-valeur publiée était fausse.
- Propager le σ Monte-Carlo de la prédiction porte le rapport à **2,595 %** contre une marge de
  2,900 % : à l'intérieur, mais avec 0,3 point de réserve seulement. Cette propagation
  **double-compte** en partie, puisque δ budgétait déjà 0,635 point d'erreur de modèle — raison
  supplémentaire de retenir la règle ponctuelle gelée comme critère de référence plutôt que de
  choisir après coup celui qui arrange.

Enfin, appliquer la recette de marge au **rapport** aurait donné ≈ 3,15 % et non 2,9 % : le
rapport a été jugé contre une marge un peu **plus serrée** que sa propre recette, ce qui est le
sens conservateur.

## 5. Adjudication

Les neuf exigences de la disposition la plus forte sont remplies, la cinquième étant évaluée
contre le **critère gelé** (règle ponctuelle) et non contre le critère post-gel.

Ce qui empêche `UNCONDITIONAL` n'est plus un nombre mais une dérivation : le flux de naissance est
une **loi mesurée** injectée dans le prédicteur, que M6 ne dérive pas. Le sceau est explicite —
*« If realized source paths or birth fluxes are injected, choose the CONDITIONAL disposition even
if prediction accuracy is excellent. »*

```
FINAL_DISPOSITION = CONDITIONAL_FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_QUALIFIED
```

La disposition rapportée par OBFOR01 est **réduite d'un qualificatif**, et sa portée est resserrée
par §4B : ce que les bras frais établissent est une non-falsification assortie d'une exigence de
mécanisme, pas une capacité prédictive discriminante.

### Revendication maximale autorisée

> Dans le LawSpec qualifié et au point gelé, un opérateur discret
> source–transport–décroissance — alimenté par (i) les noyaux exacts, l'ordre intra-pas, le tore
> fini et l'horizon fini, tous connus avant le run, et (ii) une **loi de flux de naissance
> mesurée sur des bras historiques et gelée avant les bras frais** — a énoncé **à l'avance** trois
> prédictions ponctuelles que les graines fraîches **n'ont pas falsifiées**, chacune dans la marge
> gelée de ±2,9 % : le rayon `r80` absolu résumé par la médiane intra-graine en source statique,
> le même en source mobile, et leur rapport. À l'intérieur du même test, la **trajectoire
> organisatrice partagée est requise** : la retirer manque l'observation mobile de −3,55 %, et
> l'opérateur idéal non corrigé la manque de −5,46 %, tous deux hors marge. La prédiction est
> **conditionnelle** à la loi de flux, sur un fondement dérivationnel : M6 ne dérive pas la
> source, on la lui remet. Rien au-delà de ces trois observables n'est revendiqué : ni fermeture
> de la densité marginale, ni théorie d'état complet, ni résidu `M2` exactement nul, ni quoi que
> ce soit touchant à la reproduction, à l'hérédité ou à une cohésion autonome.

**Limites qui voyagent avec la revendication et ne doivent jamais en être détachées**

1. Un témoin **sans physique** passe les trois mêmes critères : le plan ne discrimine pas
   l'opérateur d'une ressemblance historique. Il discrimine le mécanisme de trajectoire partagée.
2. Les prédictions **ne sont pas des points** : σ = 0,315 % (statique) et 0,563 % (mobile).
3. « Sans paramètre ajusté » est **retiré** : la loi de flux est une distribution empirique
   d'environ 360 000 échantillons estimée **en échantillon** sur les mêmes bras historiques
   L = 36 qui servent de référence développementale. C'est une estimation non paramétrique, pas
   l'absence d'estimation. La formulation défendable est « sans paramètre ajusté **aux bras
   frais** ».
4. Le résidu **historique** −5,10 % dépend d'une règle d'inclusion conditionnée sur un résultat
   (bande −5,10 / −4,35 / −2,14 %).
5. Le critère **statique** ne discrimine rien et repose sur trois bras historiques.

### Formulations à retirer

| formulation | pourquoi | remplacement |
|---|---|---|
| « `M2` concorde » | l'intervalle mobile est [−6,56 ; +9,78] % : il n'exclut presque rien | « aucun déficit `M2` détecté, à faible puissance » |
| « l'opérateur prédit les valeurs **absolues** du profil » | vrai seulement pour `r80` résumé par la médiane et son rapport, conditionnellement au flux mesuré | « l'opérateur prédit les trois observables de réponse de source testées, conditionnellement à une loi de flux gelée » |
| « **sans paramètre ajusté** » | la loi de flux est estimée en échantillon sur ~360 000 tirages | « sans paramètre ajusté **aux bras frais** » |
| « prédit **prospectivement** » | un témoin sans physique passe les trois critères | « a énoncé à l'avance trois prédictions non falsifiées, à l'intérieur desquelles la trajectoire partagée est requise » |
| « la **forme** du flux de naissance est porteuse (1,27 point) » | réplication : +0,41 ± 0,20 pt, de signe opposé ; doubler l'intensité : +0,01 ± 0,23 pt | « la loi de flux est une **entrée mesurée**, d'où la conditionnalité ; son influence numérique est faible » |
| « la variante de Poisson est rejetée par un facteur 4,5 » | son résidu propre est −4,42 % et elle passe le critère à ±2,9 % | « plus éloignée de l'observation, mais non rejetée » |

## 6. Prochaine éligibilité

La qualification conditionnelle passant, le handoff
`PROSPECTIVE_MINORITY_CHANNEL_REACHABILITY_01_HANDOFF.md` est produit **et non exécuté**.

## 7. Revue adverse obligatoire et tour de réparation

La revue adverse exigée par le sceau a été menée contre **cette** rédaction, sur instruction de
réfuter. Elle a rendu six défauts confirmés, un partiellement confirmé et deux attaques réfutées.
Le tour de réparation unique autorisé a été appliqué intégralement. Toutes les valeurs de
réparation sont recalculées par `seal_repair.py` et déposées dans
`OBFOR01_SEAL_REPAIR_EVIDENCE.json` ; aucune ne provient de la prose de la revue.

| # | défaut confirmé | correction appliquée |
|---|---|---|
| 1 | l'effet de 1,27 pt du flux de naissance est du bruit Monte-Carlo ; `load_bearing` était un drapeau saisi à la main | chiffre retiré, `load_bearing = False`, `CONDITIONAL` re-fondé sur la provenance, classificateur corrigé et son verdict naïf (`UNCONDITIONAL`) nommé et rejeté (§3) |
| 2 | la confirmation fraîche manque de pouvoir discriminant | témoin sans physique construit et scoré ; revendication reformulée en « non falsifiée + mécanisme requis » (§4B, §5) |
| 3 | `ORIGINAL_ZERO_RUN_MISSION_COMPLIANCE = PASS` était une chaîne codée en dur, sur deux piliers absents de la livraison | abaissé à `NOT_DETERMINABLE_FROM_THE_DELIVERED_EVIDENCE`, piliers tabulés, correctif de procédure proposé (§2) |
| 4 | `nX_final ≥ 40` est une sélection sur résultat, et la « recomputation indépendante » ré-exécutait le même filtre | règle **variée** au lieu d'être répétée, bande de sensibilité publiée, bloc requalifié en reproduction de pipeline, trois bornes du défaut énoncées (§4A) |
| 5 | le critère « intervalle entier » est post-gel | étiqueté post-gel, règle ponctuelle gelée rétablie comme référence, `TOST` corrigé sur une loi de Student, σ de prédiction propagé et double-comptage signalé (§4E) |
| 6 | statistiques : p-valeurs fausses ; propagation du σ de prédiction | corrigées ; le rapport atteint 2,595 % contre 2,900 % avec propagation, réserve de 0,3 point signalée (§4E) |

Deux attaques ont été **réfutées** et sont consignées comme telles : `PREDICTION_MODE` n'est pas
`TARGET_CONTAMINATED` (aucune statistique de bras frais n'entre dans la prédiction ; le blob
`_freeze.json` `84f336af…` est identique au bit près à HEAD et antérieur à `0148acc`), et
substituer 1,96 par une valeur de Student ne renverse aucun critère (1,142 / 1,811 / 2,243,
tous < 2,9).

Une conséquence de méthode, pour la suite : **une ablation n'est un mécanisme que si elle est
répliquée.** Une différence unique entre deux runs de 30 bras dont l'écart-type de réplique vaut
0,56 point ne peut pas soutenir un effet de 1,27 point.

---

```
GOOD_NEWS =
Le cœur factuel de la livraison tient sous audit adverse. Les sept morceaux et l'archive
vérifient, fsck est propre, aucun objet externe n'est requis, et la distinction entre la tête du
paquet historique 85ba2d8 — qui n'est pas un commit de l'histoire livrée — et le parent 062d3735
est confirmée. Les quatorze fichiers porteurs sont dans l'arbre du commit de gel et identiques au
bit près à HEAD. Les 28 bras frais sont tous là, aucun éteint, aucun dupliqué, aucun exclu, tous
soumis en un seul lot, et ils ne subissent aucun filtre. Les trois critères primaires passent la
règle gelée : -0,14 %, +0,24 %, +0,39 % pour une marge de 2,9 %. Et un résultat de mécanisme
survit à tout : retirer la trajectoire organisatrice partagée manque l'observation mobile de
-3,55 %, l'idéal non corrigé la manque de -5,46 %, tous deux hors marge, alors que le modèle
complet tombe à +0,24 %.
LESS_GOOD_NEWS =
Six défauts confirmés dans ma propre première rédaction, tous corrigés ici. Le plus lourd : un
témoin SANS PHYSIQUE, disponible avant l'ouverture d'OBFOR01, passe lui aussi les trois critères
(+0,47 %, -0,31 %, -0,77 %) — les bras frais ne séparent donc pas l'opérateur d'une simple
ressemblance historique, et « prédit prospectivement » est retiré. Ensuite : l'effet de 1,27 point
du flux de naissance ne se réplique pas (+0,41 +- 0,20 pt, signe opposé) et servait à justifier
CONDITIONAL ; le -5,10 % historique dépend d'une règle d'inclusion conditionnée sur un résultat
(-5,10 / -4,35 / -2,14 %) ; le critère « intervalle entier » est post-gel ; la p-valeur TOST était
fausse d'un facteur 18 600 ; les prédictions portaient un sigma Monte-Carlo non déclaré de
0,56 %. Enfin « sans paramètre ajusté » est faux et retiré.
ORIGINAL_ZERO_RUN_MISSION_COMPLIANCE =
NOT_DETERMINABLE_FROM_THE_DELIVERED_EVIDENCE. Le verdict PASS de ma première rédaction était une
chaîne codée en dur. Un seul de ses trois piliers est lisible dans l'arbre : OBTR01 liste bien le
déficit radial absolu comme ELIGIBLE_AT_THE_QUALIFIED_POINT, ce qui montre que la QUESTION était
ouverte. Les deux autres — le budget de runs du mandat d'OBFOR01 et la date d'arrivée du handoff
portant NEW_ENGINE_STARTS = 0 — sont de la prose sur des documents absents du dépôt. C'est un
constat d'invérifiabilité, non de violation : aucune preuve de dépassement n'a été trouvée non
plus. Correctif : verser le texte du handoff gouvernant, ou son empreinte, dans le dépôt à
l'ouverture de chaque mission.
FRESH_SUBSTUDY_PROSPECTIVITY =
PASS
PREDICTION_MODE =
CONDITIONAL
FINAL_DISPOSITION =
CONDITIONAL_FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_QUALIFIED
MAXIMAL_AUTHORIZED_CLAIM =
Un opérateur discret source-transport-décroissance, alimenté par les noyaux exacts, l'ordre
intra-pas, le tore fini et l'horizon fini connus avant le run, PLUS une loi de flux de naissance
mesurée sur des bras historiques et gelée avant les bras frais, a énoncé à l'avance trois
prédictions ponctuelles que 28 graines fraîches n'ont pas falsifiées, chacune dans la marge gelée
de +-2,9 % : r80 absolu résumé par la médiane en source statique, le même en source mobile, et
leur rapport. À l'intérieur du même test, la trajectoire organisatrice partagée est REQUISE.
Conditionnel à la loi de flux, sur fondement dérivationnel. Limites indissociables : un témoin
sans physique passe les mêmes critères ; les prédictions portent un sigma de 0,315 % et 0,563 % ;
aucun paramètre n'est ajusté AUX BRAS FRAIS, mais la loi de flux est estimée en échantillon ; le
résidu historique dépend d'une règle d'inclusion conditionnée sur un résultat ; le critère
statique ne discrimine rien et repose sur trois bras. Aucune fermeture de densité marginale,
aucune théorie d'état complet, aucun résidu M2 exactement nul, aucune revendication de
reproduction, d'hérédité ou de cohésion autonome.
NEXT_SCIENTIFIC_ELIGIBILITY =
PROSPECTIVE_MINORITY_CHANNEL_REACHABILITY_01
SCIENTIFIC_RUNS_USED = 0
TOMMY_ACTION_REQUIRED = NONE
```
