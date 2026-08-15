```
MISSION      ORGANIZER-BOUND-FULL-OPERATOR-RESIDUAL-01
DISPOSITION  FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_QUALIFIED
```

---

## 1. Provenance

L'artefact fractionné d'OBTR01 a été reconstruit dans un environnement neuf, sous `unshare -rn`
avec `GIT_NO_LAZY_FETCH=1` : aucun réseau n'existe dans l'espace de noms, donc rien ne peut
venir d'un dépôt distant. Les six morceaux et l'archive entière vérifient leurs empreintes ;
`git fsck --full` est propre ; `git rev-list --objects --missing=print` ne signale aucun objet
manquant ; `git status --porcelain` est vide ; aucun remote, aucun paquet promisor.

Les 20 entrées du manifeste MTW01 se décomposent en **19 fichiers portés dans la livraison**,
tous re-vérifiés depuis l'arbre, plus le paquet `MTW01_gen2_branch.bundle` vérifié hors arbre :
le décompte hérité « 20 sur 20 » est corrigé et non abaissé (note B-2). L'empreinte de
`_window.json` commence bien par `3a1b7ae5` et finit par `216342`.

Les conditions source statique et source mobile sont toutes deux présentes (P 6, S 3, D 3, R 3,
N 2), avec les données moléculaires, les trajectoires d'organisateur, les naissances, les morts
et les refus de transport. Les huit quantités annoncées par OBTR01 ont été **recalculées depuis
la copie de travail extraite et sont identiques au bit près**.

```
PROVENANCE_STATUS = SELF_CONTAINED_SPLIT_DELIVERY_PASS
```

## 2. HEAD, arbre, branche et commits

```
HEAD    062d3735b726bb9c7325aef063c803823e46218d
tree    30f418dd278359fb0a2d609310de12b29816c31d
branche codex/organizer-bound-timescale-rederivation-01  (héritée)
        codex/organizer-bound-full-operator-residual-01  (cette mission)
base    ad8f6bfb939ddb9a5b3b5c66155a3fdf118b2b29 (OBDCA01), frontière shallow vérifiée
commits 14 depuis la base, 1736 fichiers dans la copie de travail
```

## 3. Note de non-portabilité

Une note append-only sépare **`EMPTY_WINDOW`** de **`WINDOW_MECHANISM_ABSENT`**. Une fenêtre
vide serait un énoncé quantitatif, réfutable en déplaçant un paramètre. Ce qui est vrai ici est
autre : l'intervalle abstrait `(0 ; 1,787×10⁻⁴)` **est** non vide, mais `k_Y = 0` exactement
rend la bande atteignable égale au singleton `{0}`, la borne basse `a_Y < R_Y` est **stricte**,
et l'intersection est vide. Substituer zéro dans une formule qui contraint un taux de naissance
d'organisateur ne fabrique pas un taux nul : cela constate qu'il n'y a pas de naissance du tout,
et les bornes hautes sont alors satisfaites **vacuement**. Les anciennes égalités temporelles
sont des identités algébriques au point qualifié, donc aucune expérience de séparation des temps
n'y est éligible — non par manque de puissance, mais parce qu'il n'y a qu'une échelle.

```
HISTORICAL_WINDOW_STATUS = NOT_PORTABLE
```

## 4. L'observable statique exacte

```
OBSERVABLE   r80_organiser = metrics_obtc.radii(nX, organiser_y, organiser_x)[0.8]
CONDITION    STATIC (p_hop_Y = 0)
FORMULE      r_q = d[ searchsorted( cumsum(w trié par d)/N , q, side='left') ]
             la plus petite distance de réseau atteignable à laquelle la masse cumulée
             EMPIRIQUE d'environ 80 particules atteint 0,8
RÉSUMÉ INTRA-GRAINE   MÉDIANE sur les trames en fenêtre (step > 2000)
RÉSUMÉ INTER-GRAINES  moyenne arithmétique sur les bras analysables
UNIT_OF_ANALYSIS      SEED
NORMALIZATION         aucune ; prédiction et observation sont des longueurs absolues
```

**C'est un rayon, pas un moment quadratique.** Un déficit de 1,8 % sur ce rayon correspond à
3,6 % sur une variance, et les deux ne doivent jamais être cités comme un seul chiffre.

## 5. L'observable mobile exacte

Identique, à la condition près : `CONDITION = MOBILE`, organisateur libre au point qualifié,
population par trame d'environ 120 particules.

Trois propriétés de cet estimateur décident de tout ce qui suit : c'est un **quantile d'échantillon
fini**, c'est un **premier franchissement** donc un minimum sur `d`, et il vit sur le **support
discret** des distances toriques atteignables, dont l'espacement au voisinage de ces rayons est
de quelques pour cent.

## 6. Les prédictions, non arrondies

```
statique  r80 = 6.082763  (bloc gelé : 6.08276253029822)
mobile    r80 = 8.544004  (bloc gelé : 8.54400374531753)
statique  M2  = 24.628174
mobile    M2  = 46.684748
```

`PRE_RUN_OR_POST_RUN_PREDICTION = PRE_RUN` : les deux rayons figurent dans le yaml qu'OBTC02 a
gelé et haché dans `METHODS_CORE` avant qu'aucun bras ne tourne. Ils sont **recalculés ici depuis
la résolvante par une route indépendante** et reproduisent le bloc gelé au dernier chiffre.

## 7. Les observations, non arrondies

```
                                    règle MÉDIANE   règle MOYENNE       M2
statique (3 bras OBTC02)               5.971238        5.997900     25.618215
mobile   (116 bras OBDI02, 3 tailles)  8.108…          8.484…       47.437…
```

## 8. Résidu statique

```
OBSERVABLE          r80_organiser, résumé par la MÉDIANE
PREDICTED_VALUE     6.082763
OBSERVED_VALUE      5.971238
RESIDUAL            -1,833 %          (rapporté : « environ -1,8 % »)
UNIT_OF_ANALYSIS    SEED
CONFIDENCE_INTERVAL erreur type sur 3 bras, z = -1,51
```

Sous la règle **MOYENNE** appliquée aux mêmes trames : **-1,39 %**. Sur `M2`, moyenne par
particule et donc sans biais à tout `N` : **+4,02 %**.

## 9. Résidu mobile

```
PREDICTED_VALUE     8.544004
OBSERVED_VALUE      8.101 (L=36)  /  8.108 (trois tailles)
RESIDUAL            -5,17 % (L=36, z = -7,98)  /  -5,10 % (116 bras, z = -16,57)
par taille          -5,17 %, -4,77 %, -5,34 %  à L = 36, 72, 96
```

Sous la règle **MOYENNE** : **-0,70 %** (z = -1,85). Sur `M2` : **+1,61 %**.

Le chiffre rapporté « environ -6,1 % » provenait des 5 bras P d'OBTC02 (-6,05 %). Sur 116 bras
il vaut -5,10 %, et les deux sont compatibles.

## 10. Résidu de rapport

```
rapport prédit    1.404626
rapport observé, règle MÉDIANE gelée   1.3569   ->  -3,40 %
rapport observé, règle MOYENNE         1.4163   ->  +0,83 %
```

Le couple rapporté `1,3443 / 1,4046` vaut `0,95709`, soit **-4,29 %** ; sur valeurs non arrondies
et avec la source mobile mieux échantillonnée, l'écart est **-3,40 %**.

## 11. Statut du rapport `1,4046`

```
MOBILE_BROADENING_HYPOTHESIS  SUPPORTED
NO_MOBILE_BROADENING_RATIO_1  REJECTED
EXACT_RATIO_PREDICTION        EQUIVALENCE_NOT_ESTABLISHED (sur les données historiques)
```

L'intervalle historique à trois bras statiques est large de 17 % relativement au point estimé.
**Contenir la prédiction dans un intervalle large n'est pas une équivalence**, et qualifier le
rapport d'« exact » sur trois bras statiques surestimerait ce qu'ils peuvent montrer. La
direction, elle, n'est pas ambiguë : 1 est exclu. Le §14 rouvre la question sur des bras frais,
où elle passe.

## 12. Modèle M0 — approximation continue historique

Profil exponentiel isotrope de même longueur de localisation, domaine infini, premier passage
continu, pas de capacité finie.

```
statique  r80 continu 7.4858 contre 6.0828 sur réseau   ->  CONTINUUM_TO_DISCRETE = -18,74 %
mobile    r80 continu 10.5865 contre 8.5440             ->  CONTINUUM_TO_DISCRETE = -19,29 %
```

**M0 se trompe d'un cinquième.** Il ne sert que de référence historique ; ce n'est pas le modèle
utilisé ici, et cette correction n'a jamais fait partie du résidu sous étude.

## 13. Modèle M1 — noyau discret sans blocage sur réseau infini

Noyau exact de `X`, noyau exact de l'organisateur, ordre intra-pas exact, mortalité géométrique,
naissance au sous-pas exact. C'est l'opérateur qu'OBTR01 a qualifié `CONDITIONAL_EXACT`.

## 14. Modèle M2 — le même sur tore fini

Taille exacte, images périodiques, profil stationnaire fini, horizon et burn-in exacts, cadence
d'observation exacte. La correction infini→tore est **inférieure à un pas de quantification de
`r80`**, donc `r80` ne peut pas la résoudre ; ce sont les chiffres de `M2` qu'il faut lire pour
cette correction, et elle est négligeable.

## 15. Modèle M3 — trajectoire de source conditionnelle

La trajectoire de l'organisateur est **partagée par tout le nuage** : toutes les particules d'un
même âge subissent le même déplacement de source. C'est le seul ingrédient qui sur-disperse la
statistique par trame.

## 16. Modèle M4 — flux de naissance génératif endogène

Ressources, capacité libre, occupation de la cellule source, règle exacte de naissance,
fluctuation temporelle de `B_t`. Le flux mesuré est **sur-dispersé** relativement à Poisson :
variance/moyenne = **1,285**, autocorrélation 0,067 au décalage 1.

## 17. Modèle M5 — opérateur conditionnel à capacité finie

Non simulé, mais **borné** : §24 mesure 3,6×10⁻⁴ refus par saut offert et une borne certifiée de
0,9 % de molécules jamais refusées sur toute une vie. Il est caractérisé, pas modélisé.

## 18. Modèle M6 — prédiction complète de l'observable

M2 à M5 plus l'estimateur réellement utilisé, la population finie, l'échantillonnage, le
traitement des extinctions et l'agrégation par graine. **Sans aucun paramètre ajusté.**

```
                                   résidu médiane   résidu moyenne   sd intra-bras   asymétrie
M6 mobile, complet                     -5,69 %         -1,87 %          1,681          0,99
M6 statique, complet                   -1,24 %         -1,49 %          0,667          0,15
OBSERVÉ mobile (moteur, L=36)          -5,17 %         -0,58 %          1,780          1,07
OBSERVÉ statique (moteur)              -1,83 %         -1,39 %          0,737            —
```

## 19. Ordre intra-pas

Lu dans `kinetics.py` : `_diffuse X` → `_diffuse Y` → `_diffuse SX` → `_diffuse SY` → `_react` →
`_decay` → `_feed_and_outflow`.

## 20. Traitement des nouveau-nés

`_react` s'exécute **après** `_diffuse X` et `_diffuse Y`, donc une molécule née au pas `t`
apparaît sur la cellule **post-déplacement** de l'organisateur et ne peut pas diffuser pendant ce
pas ; son premier incrément relatif a lieu un pas complet plus tard. `_decay` s'exécutant après
`_react`, elle peut mourir à l'âge 0. Les **141 009 enregistrements de naissance** vérifiés sont
tous exactement sur la cellule de l'organisateur.

Toute molécule d'âge `a` a pris exactement `a` incréments relatifs tirés du même `K_rel`, donc
`K_rel(a) = K_rel^{*a}` : **aucun noyau dépendant de l'âge n'est nécessaire**. Se tromper d'ordre
déplacerait `r80` de 0,20 %.

```
INTRA_STEP_ORDER_CORRECTION = NEGLIGIBLE
```

## 21. Temps fini

Burn-in 2000 pas = **8,0 temps de relaxation de la masse**, déficit résiduel 3,3×10⁻⁴. Le mode de
forme le plus lent du tore vaut 658 pas, soit 3,04 e-foldings, mais c'est une propriété du
domaine et non du nuage. La question est tranchée empiriquement : **le simulateur M6 part d'un
réseau vide et porte le même burn-in**, donc ses chiffres sont déjà des prédictions à temps fini.

```
FINITE_TIME_CORRECTION = NEGLIGIBLE
```

## 22. Tore fini

En dessous d'un pas de quantification de `r80`. Résolue sur `M2`, elle reste négligeable.

```
FINITE_TORUS_CORRECTION = NEGLIGIBLE
```

## 23. Flux de naissance

```
moyenne 0.4834   variance/moyenne 1.285 (Poisson : 1,0)   autocorrélation 0.067, 0.045, 0.021
E[âge] mesuré 247.62 sur 6141 molécules contre 249.00 géométrique   ->  rapport 0.9945
N_X* = B/µ prédit 120.8 contre 120.6 observé                        ->  rapport 1.0023
```

Le flux **ne remodèle pas** la distribution des âges. Mais sa sur-dispersion est **matérielle** :
la remplacer par une source de Poisson de même moyenne déplace le résidu mobile de -5,69 % à
-4,42 %.

```
ENDOGENOUS_SOURCE_CORRECTION = QUALIFIED
```

## 24. Refus de capacité

```
sauts offerts par vie de molécule       25.56
refus attendus par vie                   0.0091
fraction certifiée jamais refusée        99.09 %
shadow replay : moves retirés            0.0355 %  ->  M2 0.0355 %,  r80 0.0178 %
sur champs réels (30 bras)               fraction refusée 7,37×10⁻⁴, au rayon carré moyen 18,6
```

Même en concentrant **tous** les refus sur les mouvements sortants, retirer 0,036 % des
mouvements déplace `M2` d'autant : **deux ordres de grandeur sous le résidu étudié**.

```
CAPACITY_REJECTION_CORRECTION = NEGLIGIBLE
```

## 25. Estimateur

C'est ici que tout se joue. Quatre estimateurs sur **les mêmes trames**, laissés libres de se
contredire :

| | statique | mobile (116 bras) |
|---|---|---|
| `r80`, résumé **MÉDIANE** (règle gelée) | **-1,83 %** | **-5,10 %**, z = -16,6 |
| `r80`, résumé **MOYENNE**, mêmes trames | -1,39 % | **-0,70 %**, z = -1,9 |
| `M2`, moyenne par particule | +4,02 % | +1,61 %, z = +0,4 |
| **profil radial complet** | — | **max \|z\| = 0,64** sur 15 rayons |

Le nuage suit l'opérateur idéal **à chaque rayon**, l'écart maximal en probabilité étant 0,0038
sur 116 bras. Seul le quantile résumé par la médiane décroche, et il décroche aux trois tailles
de domaine.

Le mécanisme : le premier franchissement est un **minimum sur `d`**, donc biaisé vers le bas ; et
la série par trame est **asymétrique à droite** (asymétrie +1,07 en mobile contre +0,31 en
statique) et **sur-dispersée** (sd intra-bras 1,78 contre 0,77 sous tirages indépendants). La
médiane d'une statistique asymétrique à droite se place sous sa moyenne, et le nuage mobile
fluctue bien davantage parce que la source erre.

```
ESTIMATOR_CORRECTION = QUALIFIED
```

## 26. Décomposition du résidu

Rapportée **des deux façons**, parce que l'attribution n'est pas indépendante de l'ordre.

**Séquentielle**, physiquement ordonnée, sur le résidu mobile en médiane (points de pourcentage) :

```
noyau discret + tore + temps fini, trames indépendantes   -0,66
+ trajectoire de source partagée                          -4,42   (gain -3,77)
+ flux de naissance mesuré                                -5,69   (gain -1,27)
```

**Factorielle 2×2** sur {trajectoire partagée, flux endogène} :

```
effet principal, trajectoire partagée   -3,74
effet principal, flux de naissance      -1,30
interaction                             +0,06   (immatérielle : les deux sont séparables)
```

**Aucun mécanisme ne se voit créditer la totalité du résidu.**

## 27. Fermeture conditionnelle

`E[n_X(t+1) | S_t] = T(S_t) n_X(t) + b(S_t)` est **exacte telle qu'écrite**, et chaque terme est
lu sur le moteur : le transport déplace `min(movers, dest_free)` par cellule, donc `T` dépend de
l'occupation et n'est le noyau gelé que **conditionnellement à l'absence de refus** ; `b =
min(n_SX, free)` à la cellule de l'organisateur et, à `k_X = 1`, ne dépend pas de `n_X` sinon par
`free` ; la décroissance est un facteur exactement linéaire `(1-µ_X)`. Conditionnellement à
l'état, l'application est linéaire.

```
FULL_ONE_STEP_CONDITIONAL_OPERATOR = CONDITIONAL_EXACT
```

## 28. Fermeture marginale

Elle **ne se ferme pas**. `T` et `n_X` sont deux fonctions de l'occupation et sont corrélées,
donc `E[T n] ≠ E[T] E[n]` ; et `b` est couplé à l'état local. Mesuré sur 57 bras :

```
corr(naissances, nSX_at_org)  +0.565
corr(naissances, free_at_org) -0.258
corr(free_at_org, N_X)        -0.120
naissances = min(nSX, free) sur 86,7 % des pas ; free nul sur 0,10 % des pas
```

Fermer la marginale exigerait la loi jointe de `(n_X, n_SX, free, position de l'organisateur)`,
qui n'est pas suivie. Ce qui **se ferme**, c'est la prédiction des **observables** — et c'est
tout ce que la disposition revendique.

```
MARGINAL_DENSITY_CLOSURE   = NOT_CLOSED
STATIONARY_PROFILE_CLOSURE = APPROXIMATE_WITH_CERTIFIED_BOUNDS
```

## 29. Analyses raw-only

Toute la phase précédant le gel est raw-only et n'a consommé **aucun** start. Les trois écarts
rapportés sont reproduits :

```
STATIC_RESIDUAL_REPRODUCED  PASS   (-1,83 % contre « environ -1,8 % »)
MOBILE_RESIDUAL_REPRODUCED  PASS   (-5,17 % à L=36, -5,10 % sur trois tailles)
RATIO_RESIDUAL_REPRODUCED   PASS   (-3,40 % contre -4,29 % arrondi)
DOMINANT_MECHANISM_CANDIDATE  ESTIMATOR__WITHIN_SEED_MEDIAN_OF_A_RIGHT_SKEWED_FIRST_CROSSING_QUANTILE
FRESH_VALIDATION_NEEDED     YES
```

L'explication ayant été construite sur les bras livrés, la tester sur eux ne peut pas être
confirmatoire. D'où la validation fraîche.

## 30. Validation fraîche

Gel complet **avant** tout bras : modèles M0–M6, observables, prédictions, résidus, hypothèses,
conditions, graines, horizons, budget, marges, analyses et dispositions. `METHODS_CORE_HASH`
figé. 377 graines retirées balayées sur 928 fichiers ; 28 graines fraîches à partir de 9300000,
disjointes. Budget dimensionné sur le résidu **statique**, le plus petit des deux.

L'instrumentation renforcée enregistre le registre des sauts, le registre des sous-pas de source
et le registre des sous-pas de naissance. Elle ne tire aucun nombre aléatoire, et ce n'est pas
affirmé mais **testé** : à graine fixée, même empreinte d'état, même `N_X`, même `r80`.

28 bras, 14 par condition, **aucune extinction**, 422 s sur deux cœurs.

```
                              prédit     observé   écart      IC95           verdict
profil absolu statique        6.0076      5.9991   -0,14 %  [-1,05 ; +0,77]   PASS
profil absolu mobile          8.0574      8.0771   +0,24 %  [-1,18 ; +1,67]   PASS
rapport mobile/statique       1.3412      1.3464   +0,39 %  [-1,30 ; +2,07]   PASS
équivalence du modèle complet                                                 PASS
```

Marge d'équivalence gelée **±2,9 %**, assemblée de termes nommés — erreur de Monte-Carlo de M6
0,28 % et 0,60 %, capacité certifiée 0,018 %, ordre intra-pas 0,20 %, deux erreurs types
d'échantillonnage à 14 bras 0,56 % et 1,11 % — et **non choisie pour contenir** -1,8 % et
-6,1 % : M6 **prédit** ces valeurs, et la marge s'applique à la distance entre l'observation et
la prédiction, pas à la distance à zéro.

**Contrôle d'ablation**, sur la médiane mobile observée 8,0771 :

```
modèle complet                    prédit 8.0574   distance 0.0197
sans la trajectoire partagée      prédit 8.3746   distance 0.2975   (facteur 15)
avec une source de Poisson        prédit 8.1660   distance 0.0889   (facteur 4,5)
valeur idéale non corrigée        prédit 8.5440   distance 0.4669   (facteur 24)
```

Contrôles secondaires, aucun décisif et tous concordants : résumé par la moyenne prédit -1,49 %
statique et -1,87 % mobile contre -1,24 % et -1,65 % observés ; dispersion intra-bras prédite
0,667 et 1,681 contre 0,699 et 1,645.

## 31. Starts utilisés

```
SCIENTIFIC_RUNS_USED       28   (14 condition S, 14 condition M)
TECHNICALLY_INVALID_RUNS    0
extinctions                 0
condition E                 NON OUVERTE
tracker cohérent avec les comptes   sur les 28 bras
registres par bras          44 000 lignes de sauts, 44 000 sous-pas de source,
                            11 000 sous-pas de naissance
blocked_fraction X          moyenne 4,04×10⁻⁴
```

## 32. Portée scientifique

Ce que la mission établit : l'opérateur conditionnel est exact ; sa densité marginale ne se ferme
pas ; le profil absolu est prédit sans paramètre ajusté ; les corrections de réseau, de temps
fini et de capacité sont quantifiées ; l'élargissement lié à une source mobile est confirmé ; les
résidus sont expliqués ; et l'opérateur est **suffisamment prédictif pour concevoir ultérieurement
un second temps indépendant**.

Ce qu'elle n'établit pas et n'affirme pas : que le système possède deux échelles indépendantes,
une fenêtre minoritaire, une identité, une mémoire, une cohésion autonome ; qu'il se reproduit ;
qu'il est self-bound ou vivant ; ni que Kamimura–Kaneko ou H3 soient confirmés.

## 33. Prochaine éligibilité

L'opérateur complet étant qualifié, la mission suivante peut **analyser**, sans exécuter
immédiatement un nouveau LawSpec, quel mécanisme minimal introduirait un second temps
indépendant : mortalité d'organisateur, renouvellement, catalyse `X+Y→2Y`, commutation de source
ou autre mécanisme physiquement défendable. **Aucun de ces mécanismes n'a été choisi ni testé
ici.**

---

```
GOOD_NEWS
Le déficit n'était pas dans le nuage. Le profil radial du nuage source-bound suit
l'opérateur idéal à chaque rayon, sur 116 bras, avec un écart maximal de 0,0038 en
probabilité. Les -1,8 % et les -6,1 % étaient portés par la règle de résumé : une
MÉDIANE intra-graine appliquée à un quantile de premier franchissement asymétrique
à droite. Un simulateur du processus idéal, sans aucun paramètre ajusté, reproduit
les deux résidus, leur dispersion et leur asymétrie ; et sur 28 bras frais, contre
des prédictions gelées avant tout run, les trois critères passent à -0,14 %,
+0,24 % et +0,39 %.

STATIC_RESIDUAL
EXPLAINED
MOBILE_RESIDUAL
EXPLAINED
MOBILE_STATIC_RATIO
QUALIFIED
FULL_ONE_STEP_CONDITIONAL_OPERATOR
CONDITIONAL_EXACT
MARGINAL_DENSITY_CLOSURE
NOT_CLOSED
FINITE_TORUS_CORRECTION
NEGLIGIBLE
FINITE_TIME_CORRECTION
NEGLIGIBLE
INTRA_STEP_ORDER_CORRECTION
NEGLIGIBLE
ENDOGENOUS_SOURCE_CORRECTION
QUALIFIED
CAPACITY_REJECTION_CORRECTION
NEGLIGIBLE
ESTIMATOR_CORRECTION
QUALIFIED
FULL_OPERATOR_ERROR
CERTIFIED
WHAT_IT_CHANGES
Le projet dispose désormais d'un opérateur qui prédit les valeurs ABSOLUES du
profil, et non seulement leurs rapports : statique 5,9991 contre 6,0076 prédits,
mobile 8,0771 contre 8,0574, sur des graines fraîches et des prédictions gelées.
Deux corollaires de méthode valent autant que le résultat. D'abord, la médiane
intra-graine d'un quantile de premier franchissement est un estimateur biaisé de
plusieurs pour cent, et ce biais dépend de la condition : il faut donc soit
l'inclure dans la prédiction, soit lui préférer une moyenne par particule. Ensuite,
la densité marginale ne se ferme pas — le flux de naissance est couplé au
`min(nSX, free)` local à 86,7 % des pas — de sorte que ce qui se ferme est la
prédiction des observables, pas une équation d'évolution de la densité. Le rapport
mobile/statique, seulement soutenu qualitativement sur les données historiques
(intervalle large de 17 % sur trois bras statiques), est ici qualifié à +0,39 %.
NEXT_SCIENTIFIC_ELIGIBILITY
INDEPENDENT_ORGANIZER_TIMESCALE_DESIGN_ANALYSIS_ONLY
H3_STATUS
NOT_TESTED
REPRODUCTION_STATUS
NOT_TESTED
AUTONOMOUS_COHESION_STATUS
NOT_ESTABLISHED
SCIENTIFIC_RUNS_USED
28 au total : 14 en condition S (source statique) et 14 en condition M (source
mobile). Aucune extinction, aucun bras rejoué, aucune graine remplacée, condition E
non ouverte, 0 run avant le gel.
TECHNICALLY_INVALID_RUNS
0
PROTOCOL_VIOLATIONS
NONE
PROVENANCE_STATUS
SELF_CONTAINED_SPLIT_DELIVERY_PASS
TOMMY_ACTION_REQUIRED
NONE
```
