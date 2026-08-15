# OBFOR01 — sceau confirmatoire de provenance et de revendication

```
TARGET_MISSION       ORGANIZER-BOUND-FULL-OPERATOR-RESIDUAL-01
TARGET_REPORTED      FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_QUALIFIED
FINAL_DISPOSITION    CONDITIONAL_FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_QUALIFIED
SCIENTIFIC_RUNS_USED 0
```

Aucune affirmation en prose n'a été acceptée comme preuve. Tout est reconstruit depuis les
objets Git, les manifestes, les fichiers bruts et le code exécutable.

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
aucun critère, aucune graine, aucun comptage n'a changé — mais elle est consignée.

### Conformité à l'autorisation de runs

Le sceau attendait probablement un **FAIL**. La preuve ne le soutient pas, et je ne concède pas
un échec que les textes gelés contredisent.

- Le parent OBTR01 a gelé `NEXT_SCIENTIFIC_ELIGIBILITY = NO_FRESH_RUN_AT_THE_QUALIFIED_POINT_FOR_THIS_QUESTION`
  — « cette question » étant la fenêtre historique — **et**, dans le même artefact, a listé
  *« the absolute radial deficit found in §15 »* comme `ELIGIBLE_AT_THE_QUALIFIED_POINT`. C'est
  exactement la question confiée à OBFOR01.
- Le mandat qui gouvernait OBFOR01 comporte §16 (phase raw-only **avant** tout nouveau start),
  §17 (**critère d'ouverture** d'une validation fraîche), §18 (conditions S, M, E), §19
  (statistiques de validation) et §20 (**budget de runs** et graines fraîches). Un mandat qui
  budgète des runs ne les interdit pas.
- Un handoff **ultérieur**, `ORGANIZER-BOUND-FULL-OPERATOR-RECONSTRUCTION-01`, porte bien
  `NEW_ENGINE_STARTS = 0`. Il est arrivé **après** la livraison d'OBFOR01 et ne peut pas la lier
  rétroactivement. Il est nommé ici pour que rien ne soit dissimulé.

**Défaut réel trouvé au passage** : la chaîne d'éligibilité d'OBTR01 se lit trop facilement
comme une interdiction générale de runs, parce que le qualificatif de portée
`FOR_THIS_QUESTION` est enfoui dans le jeton. C'est un défaut de *rapport*, et c'est
vraisemblablement l'origine de la prémisse du sceau.

```
ORIGINAL_ZERO_RUN_MISSION_COMPLIANCE = PASS
FRESH_SUBSTUDY_PROSPECTIVITY         = PASS
```

## 3. Flux d'information des prédictions

Tracé en **analysant le prédicteur gelé**, pas en lisant sa docstring.

| entrée | catégorie | traitement |
|---|---|---|
| point du LawSpec, noyaux exacts, condition, taille, horizon, burn-in, cadence, 28 graines | **A** | connus avant le run |
| **trajectoire de l'organisateur** | **A** | **SIMULÉE EX ANTE**, partagée par construction dans chaque bras simulé. Aucun chemin réalisé du moteur n'est injecté : `simulate_arm` tire lui-même les incréments de l'organisateur depuis le même noyau exact |
| **loi de flux de naissance** | **B** | **MESURÉE** sur jusqu'à 40 bras historiques et injectée comme loi. Non-cible pour les bras frais, gelée avant eux — et **porteuse** : l'ablation gelée montre qu'une source de Poisson de même moyenne déplace la prédiction mobile de 1,27 point |
| `N_X` des bras historiques | B | sert **uniquement** à écarter les bras éteints du calcul du flux ; non porteur |
| refus de capacité | non utilisé | non simulés, bornés séparément à 0,018 % sur `r80` |
| tore fini, ordre des événements | A | appliqués par construction, transcrits depuis la source |
| `r80`, `M2`, profil observés de **quelque** bras | **C** | **non utilisés**. `simulate_arm` ne prend aucune statistique observée et n'en référence aucune ; les valeurs observées ne sont lues qu'ensuite, pour comparer |

**Divulgué** : le terme d'échantillonnage de la marge de ±2,9 % est dimensionné sur la
**dispersion historique** de `r80`. C'est une dispersion, pas une moyenne ; elle ne peut pas
déplacer la comparaison ponctuelle ; elle était gelée avant les bras frais. Elle est nommée
plutôt que cachée.

```
STATIC_PREDICTION_MODE = CONDITIONAL
MOBILE_PREDICTION_MODE = CONDITIONAL
RATIO_PREDICTION_MODE  = CONDITIONAL
```

**Pourquoi pas inconditionnel** : rien de dérivé de la cible n'entre, et la trajectoire de source
est simulée et non injectée — la prédiction est donc réellement prédictive des nuages frais. Mais
un modèle auquel il faut **dire l'intensité de la source** n'est pas un opérateur inconditionnel
de premiers principes.

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

### B. Confirmation fraîche sur 28 bras

Résumés par bras **recalculés depuis les `.npz` bruts** et reproduisant l'enregistrement
exactement.

| critère | n | prédit | observé | erreur relative | IC 95 % | point dedans | **intervalle entier dedans** |
|---|---|---|---|---|---|---|---|
| profil absolu statique | 14 | 6,0076 | 5,9991 | −0,14 % | [−1,05 ; +0,77] | oui | **oui** |
| profil absolu mobile | 14 | 8,0574 | 8,0771 | +0,24 % | [−1,18 ; +1,67] | oui | **oui** |
| rapport mobile/statique | 14/14 | 1,3412 | 1,3464 | +0,39 % | [−1,30 ; +2,07] | oui | **oui** |

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

**Gelé avant les runs frais** : les prédictions d'ablation elles-mêmes, la règle d'ablation, la
décomposition séquentielle et factorielle — toutes dans l'arbre du commit de gel.
**Diagnostics post-outcome** : les distances observées (qui ne peuvent exister qu'après les
bras), l'arithmétique des facteurs, et la comparaison continu→discret. **Aucune ablation
post-outcome n'est le test confirmatoire primaire** : les trois critères primaires sont les
profils absolus et leur rapport, tous gelés.

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
est faible.

## 5. Adjudication

Les neuf exigences de la disposition la plus forte sont toutes remplies. La seule chose qui
empêche `UNCONDITIONAL` est le mode de prédiction : le sceau est explicite — *« If realized
source paths or birth fluxes are injected, choose the CONDITIONAL disposition even if prediction
accuracy is excellent. »* Le flux de naissance **est** injecté comme loi mesurée, et il est
porteur.

```
FINAL_DISPOSITION = CONDITIONAL_FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_QUALIFIED
```

La disposition rapportée par OBFOR01 est donc **réduite d'un qualificatif**. Tout ce qu'elle
affirmait des trois critères survit ; ce qu'elle ne disait pas, c'est qu'il faut **dire au modèle
l'intensité de la source**.

### Revendication maximale autorisée

> Dans le LawSpec qualifié et au point gelé, un opérateur discret
> source–transport–décroissance — alimenté par (i) les noyaux exacts, l'ordre intra-pas, le tore
> fini et l'horizon fini, tous connus avant le run, et (ii) une **loi de flux de naissance
> mesurée sur des bras historiques et gelée avant les bras frais** — prédit prospectivement,
> sans paramètre ajusté et à ±2,9 % près, trois observables de réponse de source sur graines
> fraîches : le rayon `r80` absolu résumé par la médiane intra-graine en source statique, le même
> en source mobile, et leur rapport. La prédiction est **conditionnelle** à cette loi de flux.
> Rien au-delà de ces trois observables n'est revendiqué : ni fermeture de la densité marginale,
> ni théorie d'état complet, ni résidu `M2` exactement nul, ni quoi que ce soit touchant à la
> reproduction, à l'hérédité ou à une cohésion autonome.

### Formulations à retirer

| formulation | pourquoi | remplacement |
|---|---|---|
| « `M2` concorde » | l'intervalle mobile est [−6,56 ; +9,78] % : il n'exclut presque rien | « aucun déficit `M2` détecté, à faible puissance » |
| « l'opérateur prédit les valeurs **absolues** du profil » | vrai seulement pour `r80` résumé par la médiane et son rapport, et seulement conditionnellement au flux mesuré | « l'opérateur prédit les trois observables de réponse de source testées, conditionnellement à une loi de flux gelée » |

## 6. Prochaine éligibilité

La qualification conditionnelle passant, le handoff
`PROSPECTIVE_MINORITY_CHANNEL_REACHABILITY_01_HANDOFF.md` est produit **et non exécuté**.

---

```
GOOD_NEWS =
Le cœur de la revendication tient sous audit adverse. Les sept morceaux et l'archive vérifient,
fsck est propre, aucun objet externe n'est requis, et la distinction entre la tête du paquet
historique 85ba2d8 — qui n'est pas un commit de l'histoire livrée — et le parent 062d3735 est
confirmée. Les quatorze fichiers porteurs sont dans l'arbre du commit de gel et identiques au
bit près à HEAD. Les 28 bras sont tous là, aucun éteint, aucun dupliqué, aucun exclu, tous
soumis en un seul lot. Et les trois critères primaires passent avec l'INTERVALLE ENTIER, pas
seulement le point, à l'intérieur de ±2,9 % : −0,14 %, +0,24 %, +0,39 %. Tous les nombres de
tête se recalculent : 116 bras, max |z| 0,6357, écart 0,00378, distances d'ablation 0,0197 /
0,2975 / 0,0889 / 0,4669.
LESS_GOOD_NEWS =
Trois choses. D'abord le mode de prédiction : la trajectoire de source est bien simulée ex ante,
mais le flux de naissance est une loi MESURÉE et injectée, et il est porteur — l'opérateur doit
qu'on lui dise l'intensité de la source, donc la qualification est CONDITIONNELLE et non
inconditionnelle. Ensuite, le code d'adjudication, la figure, la livraison et la relecture
n'existaient pas au gel : la règle était gelée, l'évaluateur non. Enfin, « M2 concorde » était
trop fort : l'intervalle mobile [−6,56 ; +9,78] % n'exclut presque rien, et l'absence de déficit
détecté ne fait pas un résidu exactement nul.
ORIGINAL_ZERO_RUN_MISSION_COMPLIANCE =
PASS. Le sceau attendait un FAIL ; les textes gelés ne le soutiennent pas. OBTR01 a listé le
déficit radial absolu comme ELIGIBLE_AT_THE_QUALIFIED_POINT, et le mandat d'OBFOR01 comportait un
critère d'ouverture, des conditions de validation et un budget de runs. Le handoff qui impose
NEW_ENGINE_STARTS = 0 est arrivé après la livraison et ne lie pas rétroactivement. Défaut réel
trouvé : la chaîne d'éligibilité d'OBTR01 se lit trop facilement comme une interdiction générale.
FRESH_SUBSTUDY_PROSPECTIVITY =
PASS
PREDICTION_MODE =
CONDITIONAL
FINAL_DISPOSITION =
CONDITIONAL_FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_QUALIFIED
MAXIMAL_AUTHORIZED_CLAIM =
Un opérateur discret source–transport–décroissance, alimenté par les noyaux exacts, l'ordre
intra-pas, le tore fini et l'horizon fini connus avant le run, PLUS une loi de flux de naissance
mesurée sur des bras historiques et gelée avant les bras frais, prédit prospectivement et sans
paramètre ajusté, à ±2,9 % près et intervalle entier compris, trois observables de réponse de
source sur graines fraîches : r80 absolu résumé par la médiane en source statique, le même en
source mobile, et leur rapport. Conditionnel à cette loi de flux. Aucune fermeture de densité
marginale, aucune théorie d'état complet, aucun résidu M2 exactement nul, aucune revendication de
reproduction, d'hérédité ou de cohésion autonome.
NEXT_SCIENTIFIC_ELIGIBILITY =
PROSPECTIVE_MINORITY_CHANNEL_REACHABILITY_01
SCIENTIFIC_RUNS_USED = 0
TOMMY_ACTION_REQUIRED = NONE
```
