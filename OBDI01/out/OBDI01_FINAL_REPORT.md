```
MISSION       ORGANIZER-BOUND-DOMAIN-INVARIANCE-01
DISPOSITION   DOMAIN_INVARIANCE_PARTIAL
```

Le gate D hérité d'OBTC02 a été démontré **désaligné** avec la question qu'il prétendait poser :
son seuil ne bouge que de 1.6 % quand le domaine double, il ne compare jamais deux tailles, et
sous une loi où la borne est vraie par construction il rejette 40.7 % des bras à `L = 72` — un
taux qui *croît* avec le nombre de trames. La Route B a donc été figée : le gate reste un
endpoint secondaire verrouillé, et un nouvel outcome principal mesure directement la dépendance
en `L`. Quinze bras neufs à `L ∈ {36, 72, 96}` ont tourné, tous techniquement valides, les deux
évaluateurs d'accord partout, sans le moindre arrêt anticipé. Trois composantes sur quatre
passent. La quatrième — l'écart entre le cœur du nuage et l'organisateur — échoue **par manque de
précision, non par détection d'une dépendance** : son estimation ponctuelle vaut `+0.0708` et
exclut toutes les alternatives non bornées, mais son intervalle d'équivalence déborde la marge
gelée de `0.042`. L'invariance de domaine n'est donc **pas établie**, et OBTC02 reste
`ORGANIZER_BOUND_CLOUD_PARTIAL`, inchangé.

---

## 1. Provenance

L'archive de livraison scindée a été relue **hors ligne**, espace de noms réseau supprimé et
`GIT_NO_LAZY_FETCH=1`, sans qu'aucun distant ne soit joignable ni configuré.

```
archive        OBTC02_OFFLINE_REPO.tar.gz
dépôt          nu et superficiel (fichier `shallow` présent)
branche portée codex/organizer-bound-turnover-cloud-02
tête           bb7fea748560ce8489d18ca64973f95e907ec382      → conforme
arbre          4a22920b8fcde77225d13f0d6ce7928e54619388      → conforme
frontière      d65c0c5961520fda7b3eaccee18962b9f6d5db16
profondeur     24 commits
```

La livraison est **mono-branche**. Les deux missions antérieures ne sont donc pas rembarquées :
elles sont référencées par empreinte au-delà de la frontière superficielle. Une vérification qui
exigerait leurs `refs` dans cette archive serait mal posée, et le contrôle a été corrigé en ce
sens plutôt que déclaré en échec.

`PROVENANCE_STATUS = SELF_CONTAINED_SPLIT_DELIVERY_PASS`.

## 2. Identité gel ↔ artefact

Pour chaque mission, chaque fichier du manifeste de code de son propre `_freeze.json` a été
comparé, empreinte par empreinte, au fichier réellement présent dans l'artefact.

```
OBTC02   10 fichiers au manifeste, 10 identiques         → PASS
OBTC01   exactement 2 fichiers diffèrent : gate_obtc.py, protocol_obtc.py
         → EXACTLY_EXPLAINED_BY_TWO_DOCUMENTED_PATCHES
```

Les deux fichiers divergents d'OBTC01 sont exactement les deux défauts qu'OBTC02 avait
documentés — la convention de frontière des tiers, et l'appel manquant `online.frame(fr)`. Aucune
différence non documentée. La relation est **expliquée**, pas excusée.

## 3. Matrice complète des dix-sept starts d'OBTC02

Reconstruite depuis les résultats gelés d'OBTC02 et sa propre spécification, jamais de mémoire.

| # | bras | cond | L | tech | sci | passées | échec |
|---|------|------|---|------|-----|---------|-------|
| 1 | P/seed9101 | P | 36 | ✓ | ✗ | 4 | extinction |
| 2–6 | P/seed9102–9106 | P | 36 | ✓ | ✓ | 10 | — |
| 7 | S/seed9201 | S | 36 | ✓ | ✗ | 8 | SOURCE_ATTACHMENT, CORE_CONTINUITY |
| 8 | S/seed9202 | S | 36 | ✓ | ✗ | 8 | SOURCE_ATTACHMENT, CORE_CONTINUITY |
| 9 | S/seed9203 | S | 36 | ✓ | ✗ | 9 | SOURCE_ATTACHMENT |
| 10 | D/seed9501 | D | 72 | ✓ | ✓ | 10 | — |
| 11 | D/seed9502 | D | 72 | ✓ | ✗ | 9 | RELATIVE_LOCALIZATION |
| 12 | D/seed9503 | D | 72 | ✓ | ✗ | 9 | RELATIVE_LOCALIZATION |
| 13–15 | R/seed9301–9303 | R | 36 | ✓ | ✗ | 4–5 | par construction |
| 16–17 | N/seed9401–9402 | N | 36 | ✓ | ✗ | 2 | par construction |

Dix-sept bras techniquement valides sur dix-sept ; les deux évaluateurs d'accord partout.

## 4. D est le seul axe à exigence gelée non satisfaite

```
P_STATUS  PASS      exigence gelée 5, obtenu 5
R_STATUS  PASS      exigence gelée 3, obtenu 3
N_STATUS  PASS      exigence gelée 2, obtenu 2
D_STATUS  FAIL      exigence gelée 2, obtenu 1
S_STATUS  FAIL_ON_THE_PER_ARM_GATE__NO_FROZEN_REQUIREMENT
E_STATUS  NOT_OPENED
```

`D_IS_THE_ONLY_AXIS_WITH_AN_UNMET_FROZEN_REQUIREMENT = True`. La mission est donc autorisée à
continuer ; sinon elle se serait arrêtée sur `INHERITED_NON_DOMAIN_AXIS_NOT_CLOSED` avec
`SCIENTIFIC_RUNS_USED = 0`.

**Diagnostic de S, consigné et non réparé.** Avec `p_hop_Y = 0` l'organisateur ne bouge pas : la
trajectoire déroulée a une variance nulle, donc la corrélation de position qui entre dans
`SOURCE_ATTACHMENT` vaut `0/0 = NaN` ; et le nul N3 à trames décorrélées a un déplacement médian
nul, donc le rapport qui entre dans `CORE_CONTINUITY` vaut de nouveau `0/0 = NaN`. Physiquement
les bras S sont les plus propres de toute la mission : `core_exists = 1.000`,
`|cœur − organisateur| = 0.00`, modèle 6/6. Le protocole gelé n'exigeait rien de S : cet échec ne
peut rendre aucun axe non satisfait, et **aucun seuil n'a été touché**.

## 5. Autopsie brute des trois bras D

Recalculée depuis les seules archives `.npz`, sans lire aucune sortie de gate.

```
bras          borne   localisées / éligibles   fraction   médiane r80_org   q95     max
D/seed9501    12.80        180 / 180            1.0000        8.49         11.05   12.04
D/seed9502    12.80        168 / 180            0.9333        8.06         13.06   15.30
D/seed9503    12.80        168 / 180            0.9333        8.06         13.17   17.89
```

Carte temporelle des trames en échec :

```
D/seed9502   pas 2500–2900 (série de 9), 4550–4600 (série de 2), 9850 (isolée)   séries [9, 2, 1]
D/seed9503   pas 2100–2350 (série de 6), 3000, 3100, 5750–5800, 6100, 6200       séries [6,1,1,2,1,1]
```

Le fait décisif est ailleurs. Les cinq bras P **passants** à `L = 36` dépassent eux aussi la
borne : fractions `0.9722, 0.9833, 0.9722, 0.9944, 1.0000`. La différence entre un succès et un
échec de cette condition est **combien de trames**, pas **s'il y en a**. Un verdict sur la
physique tiré de ce nombre exige donc de connaître d'abord les caractéristiques opérationnelles
du test.

## 6. Séparation de la localisation absolue et de l'invariance de domaine

La condition héritée est

```
RELATIVE_LOCALIZATION :  fraction des trames avec  r80_organiser ≤ min(12.8, 0.35 L)  ≥ 0.95
```

Deux questions distinctes s'y superposent :

* **localisation absolue** — le rayon reste-t-il sous un plafond fixe ? *Mesurée*, et satisfaite
  sur l'immense majorité des trames de tout bras sain, aux deux tailles.
* **invariance de domaine** — le rayon dépend-il de `L` ? **Non mesurée du tout.**

Les deux coïncideraient si le seuil suivait `L`. Il ne le suit pas : le terme absolu `12.8`
domine dès `L ≥ 37`.

```
borne(36) = min(12.8, 12.6) = 12.60      terme actif : fraction de domaine
borne(72) = min(12.8, 25.2) = 12.80      terme actif : absolu
rapport 1.0159  →  doubler L change le rayon admissible de 1.6 %
```

## 7. Caractéristiques opérationnelles du gate hérité — sans aucun nouveau run

Rééchantillonnage par blocs (longueur 10 trames) **par bras**, sur tous les bras sains P et D
d'OBTC02, passants ou non. La vérité est `H_bound` **par construction** : ces séries sont
produites par le LawSpec gelé, donc tout échec est une propriété du gate, pas de la physique.

```
autocorrélation de rang 1 de r80_org   moyenne 0.736   étendue 0.632 – 0.854

L = 36   borne 12.60   fraction médiane 0.9889   q05 0.9556   P(échec) = 0.030
L = 72   borne 12.80   fraction médiane 0.9611   q05 0.8722   P(échec) = 0.407

dépendance au nombre de trames
   L = 36    60 → 0.0623    180 → 0.0312    540 → 0.0043    1800 → 0.0001     (décroît)
   L = 72    60 → 0.2992    180 → 0.4110    540 → 0.5073    1800 → 0.6163     (croît)
```

À `L = 36` le test est **consistant** : plus de données, plus d'acceptation. À `L = 72` il est
**anti-consistant** : la probabilité d'exceedance par trame dépasse le budget de 5 %, donc plus
de données rendent le rejet plus certain. C'est la quantité de données, et non la physique, qui
décide du verdict.

Pour contraste, la grandeur que l'axe vise réellement — le rayon `r80` mesuré depuis le centre du
nuage, donc libre du décalage de repère — vaut `7.0711` à `L = 36` et `7.0355` à `L = 72`, soit
une différence relative de `0.50 %`.

## 8. `LEGACY_D_GATE_STATUS`

```
LEGACY_D_GATE_STATUS = MISALIGNED_WITH_DOMAIN_INVARIANCE
```

Six motifs, tous chiffrés au §6 et au §7 : seuil quasi indépendant de `L` ; aucune comparaison
inter-domaines ; redondance avec le test identique déjà appliqué à P ; taux de faux négatifs de
`0.407` à `L = 72` contre `0.030` à `L = 36` ; anti-consistance ; désaccord avec une mesure
directe qui donne `0.50 %`.

**Ce que ce statut ne fait pas.** Il n'établit pas que le nuage est borné quand `L` croît — c'est
exactement ce que cette mission devait tester sur données fraîches. Il ne supprime pas le gate.
Il ne rescore aucun bras d'OBTC02. La disposition d'OBTC02 reste `ORGANIZER_BOUND_CLOUD_PARTIAL`
et son axe D reste `FAIL`.

## 9. Route

```
ROUTE = B
```

Le gate D hérité reste un **endpoint secondaire verrouillé** : ni supprimé, ni réinterprété, ni
réaccordé. Le nouvel outcome principal mesure directement la dépendance en `L`.

Route A rejetée : garder le gate hérité comme outcome principal reviendrait à reposer une
question dont le §8 montre qu'elle n'est pas celle de l'axe. Route C rejetée : les §11–§14
montrent que l'opérateur produit des prédictions sans paramètre à chaque `L` candidat et que le
plan dispose d'une puissance très large.

## 10. Statut du design et des données

```
DESIGN_STATUS             OUTCOME_INFORMED_TARGETED_FOLLOWUP
CONFIRMATORY_DATA_STATUS  FRESH_AND_PREREGISTERED
```

Le design a été choisi après avoir vu l'échec d'OBTC02 : le dire autrement serait faux. Les
données, elles, sont entièrement neuves et produites après le gel. Un design informé par le
résultat, évalué sur données fraîches, soutient une affirmation **sur l'axe de domaine
seulement** : il ne relève pas OBTC02 et n'autorise pas à dire que la qualification est complète.

## 11. Les quatre hypothèses

| | énoncé | exposant `β` de `r` en `L` | exposant de densité |
|---|---|---|---|
| `H_bound` | taille intrinsèque fixée par l'opérateur ; correction de taille finie calculable | `0` | `−2` |
| `H_linear` | fraction fixe du domaine | `1` | `0` |
| `H_sublinear` | croissance non bornée mais plus lente ; cas de référence diffusif | `1/2` | `−1` |
| `H_fill` | le nuage occupe le tore ; l'enroulement devient typique | `1` | `0` |

Seule `H_bound` est *prédite* par l'opérateur source-transport-décès gelé ; les trois autres sont
les alternatives que l'axe doit exclure.

## 12. Le noyau discret exact et les couches de statut

```
UNBLOCKED_DISCRETE_KERNEL           EXACT
SAMPLED_CLOUD_STATISTICS            EXACT_LAW__MONTE_CARLO_EVALUATION
FULL_CAPACITY_CONSTRAINED_OPERATOR  APPROXIMATE_WITH_EMPIRICAL_ERROR
```

Le profil stationnaire sur le tore `L × L` est obtenu par inversion DFT de
`n̂(k) = 1 / (1 − (1−µ) φ(k))`, `φ(k) = [1 − a(1−cos k_y)][1 − a(1−cos k_x)]` : **exact**, sans
limite continue ni constante ajustée. Les statistiques qui sont des fonctionnelles d'un
échantillon **fini** tiré de cette loi exacte — rayon de giration autour du centre de Fréchet du
nuage, `r80` en repère nuage, enroulement du support — sont évaluées par tirage : la loi est
exacte, seule la fonctionnelle est estimée, et l'erreur de Monte-Carlo est rapportée. Enfin le
moteur refuse aussi les sauts vers une case pleine ; ce taux de refus est **mesuré**
(`≤ 4.7 × 10⁻⁴` par saut offert dans OBTC02, `≤ 4.7 × 10⁻⁴` également dans les quinze bras
d'OBDI01) et cité comme terme d'erreur empirique. **Il n'est pas converti en borne rigoureuse et
n'est pas extrapolé.**

## 13. Prédictions de taille finie

```
L     déficit m2      r80_org   R_g prédit     r80 nuage   |C−Y|    enroul.   masse > L/2   L/ℓ_rel   L/r80
36    6.256e-02        8.441    5.830±0.575     7.014      3.080     0.000     1.16e-02      10.18    4.21
72    7.747e-04        8.419    6.030±0.730     6.978      3.172     0.000     1.12e-04      20.36    8.43
96    3.483e-05        8.427    6.053±0.715     6.990      3.151     0.000     4.54e-06      27.15   11.24
108   7.196e-06        8.393    6.035±0.703     6.992      3.117     0.000     8.84e-07      30.55   12.64
144   6.021e-08        8.433    6.045±0.732     6.995      3.153     0.000     6.66e-09      40.73   16.85
```

Le « déficit m2 » est la **correction d'images périodiques** : le tore tronque la queue du profil
exact, donc sous `H_bound` le rayon mesuré doit **croître légèrement** avec `L` puis saturer, et
non rester exactement constant. Cette correction est une prédiction, pas une nuisance : elle vaut
`6.26 %` à `L = 36`, `0.077 %` à `L = 72`, et devient négligeable au-delà.

Une mise en garde est consignée : `r80` du profil exact est un quantile sur des distances de
réseau et se trouve donc **quantifié** — il peut être identique à deux `L` alors que le profil
diffère. C'est le **second moment** qui est la sonde sensible, et c'est lui qui porte la
correction.

La population n'est pas prédite par l'opérateur : `N_X = B/µ` avec `B` le nombre moyen de
naissances acceptées à l'organisateur, fixé par la ressource et la capacité **locales**. Le
chémostat maintenant la densité d'occupation constante, `B` est *attendu* indépendant de `L` —
mais c'est une **prédiction de cette mission**, pas une entrée.

## 14. Choix déterministe de la troisième taille de domaine

Règle gelée : la **plus petite** candidate de `{96, 108, 144}` qui atteint simultanément (a) une
puissance `≥ 80 %` contre `H_linear`, (b) un déficit d'images périodiques `≤ 10⁻³`, (c) un coût
total inférieur à une heure de moteur.

```
L = 96    puissance 1.0000    déficit 3.48e-05  négligeable   coût ≈ 398 s   ÉLIGIBLE
L = 108   puissance 1.0000    déficit 7.20e-06  négligeable   coût ≈ 453 s   ÉLIGIBLE
L = 144   puissance 1.0000    déficit 6.02e-08  négligeable   coût ≈ 622 s   ÉLIGIBLE
```

Les trois sont éligibles ; la règle sélectionne `96`. Le coût n'est pas contraignant ici et cela
est dit franchement plutôt que présenté comme une contrainte. `DOMAIN_SIZES = {36, 72, 96}`.

## 15. Décomposition de variance et analyse de puissance pré-gel

Bras utilisés : **tous les bras pertinents d'OBTC02, passants ou non** — P/seed9102–9106 et
D/seed9501–9503, ces derniers incluant **les deux qui ont échoué au gate hérité**, précisément
pour que la variance ne soit pas sous-estimée par conditionnement sur le succès. Exclus, avec
motifs : P/seed9101 (éteint), S (loi différente), R (fenêtre non stationnaire), N (pas de nuage).

Le résumé de bras est la **médiane** sur les 180 trames ; son erreur type est obtenue par
bootstrap par blocs, et non par `sd/√n_eff`, qui est l'erreur de la moyenne et ne serait pas
comparable.

```
statistique          L=36 sd_bras  intra   inter        L=72 sd_bras  intra   inter
R_g                     0.1002    0.1360  0.0000           0.1386    0.1485  0.0000
r80                     0.1591    0.1526  0.0449           0.2000    0.1755  0.0960
r80_organiser           0.4523    0.2600  0.3702           0.2442    0.2625  0.0000
|cœur − organisateur|   0.3605    0.3310  0.1427           0.3496    0.2699  0.2222
```

Une variance inter-graines nulle signifie **non résoluble à ce nombre de bras** — la dispersion
d'un bras à l'autre est déjà expliquée par l'erreur d'échantillonnage intra-bras — et non que les
graines seraient identiques. Pour la puissance, c'est le `sd` de bras **le plus grand** des deux
tailles qui est retenu : le calcul est conservateur.

```
n par taille exigé par la puissance contre H_linear      1
plancher d'estimabilité   1/√(2(n−1)) ≤ 0.40             5
n ADOPTÉ                                                 5      → 15 bras confirmatoires
DOMAIN_TEST_UNDERPOWERED = False
```

Le plancher est déclaré ouvertement comme une exigence **distincte** de la règle de puissance :
celle-ci seule autoriserait `n = 1`, ce qui rendrait la variance inter-graines inestimable.

## 16. Graines

Balayage de **818 fichiers** du dépôt reconstruit, cinq motifs, plus lecture structurelle des
`_results.json` de chaque mission : **159 entiers de type graine retirés**.

```
FRESH_OBDI01_SEEDS   L=36  771010 771011 771012 771013 771014
                     L=72  771110 771111 771112 771113 771114
                     L=96  771210 771211 771212 771213 771214
DISJOINT = True      recouvrement avec les retirées : ∅
```

Règle de sélection : le premier bloc de trois centaines consécutives où **aucun** entier du dépôt
balayé n'apparaît, puis `graine(L_j, k) = base + 100 j + 10 + k`. Déterministe. Les graines
d'**analyse** (Monte-Carlo, bootstrap) sont listées à part : elles pilotent des générateurs dans
du code d'analyse, ne démarrent jamais le moteur, et ne sont pas comptées comme runs.

## 17. L'outcome principal — région d'acceptation simultanée

`DOMAIN_INVARIANCE_REGION`. Le §8 ayant établi que le gate hérité confondait un test **absolu**
avec un test d'**invariance**, bâtir le nouvel outcome sur l'accord absolu avec une prédiction
répéterait exactement cette erreur. L'outcome principal teste donc la **dépendance en `L`** après
avoir divisé la prédiction de taille finie de l'opérateur : un rapport, dans lequel tout biais
multiplicatif indépendant de `L` s'annule.

Rejeter « l'exposant vaut 1 » n'est **pas** établir la bornitude. L'outcome est donc un test
d'**équivalence** : il ne peut être passé que par un intervalle qui exclut toute alternative non
bornée, jamais par une simple absence de rejet.

```
A  invariance de forme        y = log(observé) − log(prédit à ce L)
                              β = pente MCP de y sur log L
                              accepte ssi |β| + c·se(β) ≤ 0.25        sur R_g, r80, |C−Y|
B  exposant de densité        γ = pente MCP de log(N_X/L²) sur log L
                              accepte ssi |γ + 2| + c·se(γ) ≤ 0.25
C  aucun enroulement vrai     fraction de trames enroulées ≤ 0.01 à chaque L
D  compatibilité de profil    distance en variation totale entre le profil radial empirique
                              autour de l'organisateur et le profil exact, ≤ q99 de l'enveloppe
                              gelée, pour au moins 4 bras sur 5 à chaque L
```

La marge `0.25` est **la moitié de l'exposant de l'alternative non bornée la plus lente** de la
famille (`H_sublinear`, `α = 0.5`). Accepter exclut donc *toute* la famille, pas seulement
`H_linear`.

## 18. Multiplicité

```
K = 10 tests    α familial 5 %    correction Šidák
α par test = 0.005116197          valeur critique c = 2.7996
```

Deux lectures, toutes deux consignées. **Déclarer l'invariance** est une affirmation
intersection-union : elle exige que *toutes* les composantes passent, donc son niveau est celui
d'une seule composante et la multiplicité ne l'enfle pas. **Échouer la région alors que
`H_bound` est vraie** est en revanche un événement d'union : c'est cela que la correction Šidák
contrôle à 5 %.

L'enveloppe de la composante D est construite sur `n_eff = 27` trames indépendantes plutôt que
sur 180, à partir de l'autocorrélation `0.736` mesurée au §7 — choix pré-enregistré et
délibérément **conservateur**, puisqu'il élargit l'enveloppe.

```
enveloppe TV q99    L=36 0.0559    L=72 0.0543    L=96 0.0545
```

## 19. L'endpoint secondaire verrouillé

```
LEGACY_D_GATE   fraction de trames avec r80_organiser ≤ min(12.8, 0.35 L) ≥ 0.95, par bras
statut          VERROUILLÉ — rapporté exactement comme OBTC02 le définit, jamais réaccordé
rôle            secondaire ; son résultat ne peut modifier l'outcome principal dans aucun sens
```

Attendu sous `H_bound`, d'après le §7 : un taux de faux négatifs d'environ `0.41` par bras à
`L = 72` et au-delà, croissant avec le nombre de trames. Un échec sur certains bras de grand
domaine est donc le **comportement attendu de ce gate sous une bornitude vraie** et ne doit pas
être lu comme une preuve contre la bornitude.

## 20. Identité avec OBTC02

```
LAWSPEC_DIFF_FROM_OBTC02                 NONE
CHEMOSTAT_DIFF_FROM_OBTC02               NONE
COHESION_DIFF_FROM_OBTC02                NONE
SCIENTIFIC_PARAMETER_DIFF_FROM_OBTC02    NONE
DOMAIN_TEST_DESIGN                       NEW_PREREGISTERED_TARGETED_FOLLOWUP
```

L'identité est une **propriété du graphe d'appel**, pas une assurance : les bras sont produits en
appelant le `run_arm` d'OBTC02 **non modifié**, avec l'objet `Spec` d'OBTC02. Trois choses
seulement diffèrent, toutes déclarées : la taille de domaine, la graine, et le répertoire
d'écriture de l'archive brute. L'enveloppe N2 de compatibilité prédictive est **l'objet d'OBTC02
lui-même** à `L = 36` et `L = 72`, copié sans recalcul ; à `L = 96` elle est produite par le
`n2_envelope` d'OBTC02 avec sa propre grille, son propre nombre de tirages et sa propre graine.

**La seule mesure ajoutée** est un **observateur passif** posé sur `metrics_obtc.frame`, parce
que l'enregistrement de trame gelé porte des rayons et non le profil. L'observateur appelle la
fonction d'origine et rend son résultat inchangé, ne lit que le champ et la position de
l'organisateur, et ne tire aucun nombre aléatoire.

## 21. Gel

```
OBDI01_METHODS_CORE_HASH   6de8d12b03f7b0cc623c4501d38ef4e9a909fa46a9e7b220379ac471bf467833
spec_sha256                6d6cfed6d2b8cdefd7f4a818be07d61113b6f51371ad96e6a6c8de1e8dab0bf1
fichiers couverts          14        manquants au gel : aucun
EARLY_SCIENTIFIC_STOPPING  FORBIDDEN
SCIENTIFIC_RUNS_USED_AT_FREEZE   0
```

Le hash couvre le protocole gelé, les deux gates, les deux protocoles d'exécution, le moteur, les
métriques, les nuls, la topologie, l'opérateur, le garde-fou, et l'enveloppe N2 sérialisée. Aucun
fichier du noyau n'a changé entre le gel et l'exécution : vérifié empreinte par empreinte.

## 22. Tests d'instrument — 25 sur 25

Exécutés en **mode TEST**, qui n'ouvre aucun start et ne laisse aucune entrée au registre
(`ledger_untouched = True`).

```
T1  l'observateur laisse le hash d'état, la somme de contrôle des trames et la population
    strictement identiques, et voit exactement une ligne par trame
T2  le profil radial empirique reproduit un recalcul en force brute, écart maximal 0
T3  le profil prédit est un vecteur de probabilité ; TV(p,p) = 0 ; TV est bien la demi-distance L1
T4  la pente MCP retrouve exactement 0, 1/2, 1 et −2
T5  la région accepte H_bound et rejette H_linear, H_sublinear et H_fill ;
    et chacune des quatre composantes peut être brisée SEULE
T6  la valeur critique reproduit le niveau par test, et Šidák reproduit le niveau familial
T7  l'endpoint secondaire reproduit les verdicts ET les fractions exactes d'OBTC02
    (D/9501 1.0000 PASS, D/9502 0.9333 FAIL, D/9503 0.9333 FAIL)
```

T5 est le test qui compte : un gate qui ne peut pas échouer ne prouve rien.

## 23. Sonde de pipeline non scientifique

Un bras unique, graine `771999` hors du jeu confirmatoire, passé par exactement le code de
production, dans la classe `cost_probe` que le garde-fou exclut par construction du décompte
scientifique. Résultat : techniquement valide, évaluateurs d'accord, 180 trames de fenêtre,
`TV = 0.0258`, tous les résumés finis, `SCIENTIFIC_RUNS_USED = 0`. Ses nombres ne sont comparés à
aucun seuil et n'entrent nulle part. Les bras confirmatoires ne devaient pas être la première
sollicitation de bout en bout du chemin de production.

## 24. Budget et starts

```
classe          consommé / plafond
confirmation      15 / 24
contrôle           0 / 8
calibration        0 / 4
sonde de coût      0 / 2       (la sonde du §23 y est reclassée après coup, explicitement)
invalides          0
SCIENTIFIC_RUNS_USED = 15
```

## 25. Les quinze bras

```
bras              L    tech   N_X     R_g    r80    |C−Y|   densité    enroul.  TV      legacyD
L36/seed771010   36    ✓    119.5   5.718  6.708   2.828   0.09222      0     0.0148   ✗
L36/seed771011   36    ✓    125.0   5.870  7.071   3.000   0.09642      0     0.0184   ✓
L36/seed771012   36    ✓    119.0   5.553  6.708   2.236   0.09186      0     0.0359   ✓
L36/seed771013   36    ✓    126.5   5.698  6.708   3.000   0.09765      0     0.0176   ✓
L36/seed771014   36    ✓    117.3   5.776  7.071   2.828   0.09054      0     0.0159   ✓
L72/seed771110   72    ✓    120.7   6.143  7.071   3.162   0.02328      0     0.0106   ✓
L72/seed771111   72    ✓    123.2   6.317  7.211   3.162   0.02376      0     0.0171   ✓
L72/seed771112   72    ✓    120.1   6.272  7.211   3.162   0.02317      0     0.0300   ✗
L72/seed771113   72    ✓      0.0     nan    nan     nan   0.00000      0      nan     ✗   ÉTEINT
L72/seed771114   72    ✓    117.6   5.800  6.708   2.828   0.02268      0     0.0162   ✓
L96/seed771210   96    ✓    115.3   6.147  7.071   3.000   0.01251      0     0.0085   ✓
L96/seed771211   96    ✓    110.6   5.942  7.071   3.162   0.01200      0     0.0141   ✗
L96/seed771212   96    ✓    114.7   5.989  7.071   3.081   0.01244      0     0.0136   ✓
L96/seed771213   96    ✓    118.2   6.000  7.071   3.081   0.01283      0     0.0161   ✓
L96/seed771214   96    ✓    120.5   5.736  7.000   2.828   0.01308      0     0.0190   ✓
```

Quinze bras sur quinze techniquement valides ; les deux évaluateurs d'accord sur quinze ;
occupation exactement constante sur quinze ; refus de transport `≤ 4.7 × 10⁻⁴`. **Aucun arrêt
anticipé** : le plan a été exécuté en entier.

Sous le gate **par bras d'OBTC02** — celui que la mission n'utilise pas pour décider — **onze
bras sur quinze passent les dix conditions**, dont quatre sur cinq à `L = 96`. Les trois autres
échouent la seule `RELATIVE_LOCALIZATION`, et le quinzième est éteint.

## 26. Composante A — invariance de forme

```
statistique            β        se       |β| + c·se    marge   verdict   exclut H_sub   exclut H_lin
R_g                 +0.0077   0.0156      0.0514       0.25      ✓            ✓              ✓
r80                 +0.0351   0.0182      0.0862       0.25      ✓            ✓              ✓
|cœur − organis.|   +0.0708   0.0789      0.2918       0.25      ✗            ✓              ✓
```

Écarts relatifs à la prédiction sans paramètre :

```
R_g      L=36 −1.83 %   L=72 +1.70 %   L=96 −1.49 %
r80      L=36 −2.29 %   L=72 +1.04 %   L=96 +0.96 %
|C−Y|    L=36 −9.78 %   L=72 −2.93 %   L=96 −3.82 %
```

`R_g` et `r80` sont invariants sur une plage de domaine de facteur `2.67`, avec des intervalles
d'équivalence de `±0.044` et `±0.051` sur l'exposant log-log. La troisième statistique échoue
**par précision** : son estimation ponctuelle est compatible avec `H_bound` et les deux
alternatives non bornées sont exclues, mais l'intervalle déborde la marge de `0.042`.

## 27. Composante B — exposant de densité

```
γ = −2.0485 ± 0.0211     |γ + 2| + c·se = 0.1077 ≤ 0.25     ✓
exclut H_fill (γ = 0)          ✓
exclut H_sublinear (γ = −1)    ✓

L=36   densité observée 0.093737   prédite 0.093716   N_X moyen 121.48
L=72   densité observée 0.018579   prédite 0.023429   N_X moyen  96.31   (contient le bras éteint)
L=96   densité observée 0.012572   prédite 0.013179   N_X moyen 115.87
```

C'est un test réel et non une reformulation du profil : la population n'est **pas** prédite par
l'opérateur, puisque le taux de naissance est une grandeur locale mesurée. Le résultat confirme
la prédiction du §13 : `N_X` est indépendant de `L`, donc la densité tombe en `L⁻²`.

## 28. Composantes C et D

```
C   enroulement vrai        L=36  0 / 900     L=72  0 / 900     L=96  0 / 900      ✓
    tolérance gelée 0.01 ; le noyau exact avait produit 0 enroulement sur 3000 tirages à chaque L
D   compatibilité de profil L=36  5/4 bras    L=72  4/4 bras    L=96  5/4 bras     ✓
    seuils TV 0.0559, 0.0543, 0.0545 ; TV observées de 0.0085 à 0.0359
```

À `L = 72`, le bras éteint compte comme hors enveloppe (sa TV est indéfinie) : la composante
passe donc **exactement** à la limite, `4` sur les `4` requis. Ce n'est pas confortable et c'est
dit tel quel.

## 29. Verdict de l'outcome principal

```
DOMAIN_INVARIANCE_REGION_PASS = False
composante en échec : A_shape_invariance, sur la seule statistique |cœur − organisateur|
aucune alternative non bornée n'est soutenue par aucune statistique
```

## 30. L'endpoint secondaire sur graines fraîches

```
L = 36    4 / 5 bras passent      taux d'échec 0.20
L = 72    3 / 5 bras passent      taux d'échec 0.40
L = 96    4 / 5 bras passent      taux d'échec 0.20
global    11 / 15                 taux d'échec 0.267
```

Le contrôle croisé contre la condition `RELATIVE_LOCALIZATION` évaluée à l'intérieur du `run_arm`
d'OBTC02 donne un accord parfait sur les quinze bras.

Sous une loi où `H_bound` est vraie, le gate verrouillé rejette donc **4 bras sains sur 15, y
compris à `L = 36`**. Le bootstrap du §7 avait prédit `0.41` à `L = 72` — observé `0.40`, accord
étroit — mais sous-estimait `L = 36` (`0.030` prédit, `0.20` observé). Avec cinq bras par taille,
ces taux sont très imprécis et cela doit être dit. La conclusion qualitative du §8 en sort
néanmoins **renforcée** plutôt qu'affaiblie : ce gate est un test **absolu bruité à toutes les
tailles**, et non un problème propre aux grands domaines.

## 31. Défauts de cette mission, consignés et non excusés

**(a) L'extinction n'était pas pré-spécifiée.** Un bras s'est éteint à `L = 72`. Le plan gelé ne
disait pas comment traiter un bras éteint, alors que P/seed9101 s'était éteint dans OBTC02 et que
le cas était donc prévisible. C'est un défaut de conception de cette mission.

*Conséquences, quantifiées et non appliquées.* La pondération inverse-variance gelée a
automatiquement dévalué la taille contaminée, parce que le bras éteint gonflait la dispersion de
ce groupe : `γ` hors bras éteint vaut `−2.0385 ± 0.0203` contre `−2.0485 ± 0.0211` gelé. Le
verdict gelé a donc été protégé **par l'arithmétique, pas par le design**. Pour la composante A,
`n` est tombé de 5 à 4 à `L = 72`, ce qui a gonflé l'erreur type — de la statistique qui a
précisément échoué.

**(b) L'analyse de puissance du §15 a dimensionné contre `H_linear` en utilisant `R_g`.**
`|cœur − organisateur|` a une dispersion relative pré-enregistrée de `11.7 %` contre `2.4 %` pour
`R_g`, et une affirmation d'**équivalence** exige de la **précision**, ce qui est une exigence
distincte de la puissance contre une alternative lointaine. Avoir confondu les deux est le défaut
qui a produit l'échec de la composante A.

*Ce qu'il aurait fallu.* `se ≤ 0.0640` au lieu de `0.0789`, soit une réduction de variance de
`1.52`, soit environ **8 bras par taille** au lieu de 5.

**(c) Un commit a groupé les artefacts §4–§5 dans le commit §6.** Signalé ici ; l'historique n'a
pas été réécrit.

**(d) Le manifeste de gel ne couvre pas le module de LawSpec.** `lawspec_v2.py` et
`observe.py` ne sont dans le manifeste d'aucune mission ; la lacune est héritée d'OBTC02 et n'a
pas pu être réparée sans toucher au gel. Elle est contournée au §32bis par une comparaison
d'octets avec la livraison d'OBTC02, et signalée ici.

**(e) L'espace des dispositions du §33 est une reconstruction.** La liste verbatim des neuf
dispositions du mandat n'a pas survécu à la compaction de contexte de cette session. Elle est
reconstruite exhaustivement à partir des états terminaux de la mission et **déclarée comme
reconstruction**, non citée comme l'original.

## 32. Matrice cumulative des preuves

Règle : **aucune graine ne contribue à deux axes.**

| axe | preuve | graines | résultat | contribution OBDI01 |
|---|---|---|---|---|
| P nuage lié à l'organisateur | OBTC02 | 9101–9106 | PASS | AUCUNE |
| S organisateur immobilisé | OBTC02 | 9201–9203 | échec par bras, sans exigence gelée | AUCUNE |
| R retrait de la source | OBTC02 | 9301–9303 | PASS | AUCUNE |
| N absence d'organisateur | OBTC02 | 9401–9402 | PASS | AUCUNE |
| D domaine | OBTC02 | 9501–9503 | FAIL, instrument désaligné | — |
| D domaine | **OBDI01** | **771010–771214** | **PARTIEL** (A ✗, B ✓, C ✓, D ✓) | — |
| E | — | — | NOT_OPENED | AUCUNE |

Recouvrement de graines entre missions : **zéro**. Instruments : disjoints. Runs scientifiques :
OBTC02 17, OBDI01 15, partagés 0.

## 32bis. Livraison scindée et relecture hors ligne

Poussée tentée **une fois** vers `origin`. Réponse consignée telle quelle :

```
remote: access denied by the git proxy: Mythmaker28/emergent-dynamics-lab is not in this
session's authorized repository set, so the proxy will not inject a credential for it.
fatal: unable to access 'https://github.com/Mythmaker28/emergent-dynamics-lab.git/':
       The requested URL returned error: 403
```

Livraison autonome à la place : dépôt **nu et superficiel** mono-branche, archivé puis scindé en
morceaux de 19 Mo. Relecture sous `unshare -rn`, `GIT_NO_LAZY_FETCH=1`.

```
3 morceaux, empreintes des trois conformes, archive réassemblée conforme
tête et arbre conformes, copie de travail conforme, 1488 fichiers
frontière superficielle = bb7fea74… , c'est-à-dire la tête d'OBTC02
10 commits portés, fsck propre, porcelain vide, aucun pack promisor, aucun distant
16 archives brutes livrées, les neuf artefacts obligatoires présents
READBACK_STATUS = SELF_CONTAINED_SPLIT_DELIVERY_PASS
```

Deux points méritent d'être dits explicitement.

**(i) Les modules hérités sont vérifiés à leur emplacement canonique.** Neuf des quatorze
fichiers du noyau gelé ne sont pas des fichiers d'OBDI01 : ce sont ceux d'OBTC02, et la relecture
les résout dans `OBTC02/code/` où leurs empreintes correspondent **exactement** à celles du gel
d'OBDI01. L'identité du code entre les deux missions est donc vérifiable *à l'intérieur* de la
livraison, et non seulement affirmée.

**(ii) Une lacune de couverture, héritée et non réparable.** `lawspec_v2.py` et `observe.py`
définissent la loi et l'enregistreur, et ne figurent dans le manifeste de gel d'**aucune**
mission — ni OBTC02 ni celle-ci. On ne peut pas les y ajouter après coup sans changer le gel.
Ils sont donc vérifiés autrement : leurs octets livrés ici sont **identiques** à ceux livrés par
OBTC02. Cela transforme `LAWSPEC_DIFF_FROM_OBTC02 = NONE` d'une affirmation en un contrôle.


## 33. Disposition

Espace **reconstruit** (voir §31 d) : trois arrêts pré-run, cinq verdicts d'hypothèse, un
indécis — exhaustif et mutuellement exclusif.

```
INHERITED_NON_DOMAIN_AXIS_NOT_CLOSED       non : D était bien le seul axe non satisfait
DOMAIN_TEST_UNDERPOWERED                   non : n = 5 atteignait la règle de puissance gelée
AUDIT_INVALID                              non : 15/15 valides, 15/15 évaluateurs d'accord
DOMAIN_INVARIANCE_ESTABLISHED              non : la région n'a pas passé en entier
DOMAIN_INVARIANCE_PARTIAL                  ← RETENUE
DOMAIN_INVARIANCE_REFUTED__H_LINEAR        non : β exclut 1 sur les trois statistiques
DOMAIN_INVARIANCE_REFUTED__H_SUBLINEAR     non : β exclut 1/2 ; γ exclut −1
DOMAIN_INVARIANCE_REFUTED__H_FILL          non : γ exclut 0 ; zéro enroulement sur 2700 trames
DOMAIN_INVARIANCE_NOT_DECIDED              non : 3 composantes sur 4 passent, les 4 hypothèses
                                                sont discriminées, le résultat est informatif
```

## 34. Portée autorisée

**Peut être dit.** Sur graines fraîches pré-enregistrées et sur une plage de domaine de facteur
`2.67`, le rayon de giration et le rayon à 80 % du nuage ne montrent aucune dépendance en `L`
au-delà de la correction de taille finie calculée par l'opérateur, avec des intervalles
d'équivalence de `±0.044` et `±0.051` sur l'exposant. La population est indépendante de la taille
du domaine, donc la densité tombe en `L^−2.049 ± 0.021`, ce qui exclut à la fois une densité
constante et une population croissant avec la taille linéaire. Aucun enroulement topologique n'a
eu lieu sur 2700 trames. Le profil radial autour de l'organisateur est compatible avec le noyau
exact à chaque taille. L'écart entre le cœur et l'organisateur n'a **pas** été montré indépendant
du domaine à la marge gelée. Le gate D hérité rejette des bras sains à toutes les tailles.

**Ne peut pas être dit.** Que l'invariance de domaine est établie — la région gelée n'a pas
passé. Que la disposition d'OBTC02 est relevée — elle reste `ORGANIZER_BOUND_CLOUD_PARTIAL`,
inchangée. Que l'axe D d'OBTC02 est fermé. Et aucun des termes proscrits : auto-lié, cohésion
autonome, cellule, membrane, identité, reproduction, mémoire, confirmation d'H3, validation
globale de Kamimura–Kaneko, vie, organisme, autopoïèse, matière fraîche, lignée matérielle.

## 35. Prochaine éligibilité

**Éligible.** Une réplication de la **même région gelée**, sans redesign, avec un nombre de bras
dimensionné pour la **précision d'équivalence** de `|cœur − organisateur|` — environ 8 bras par
taille — et avec une règle pré-spécifiée pour les bras éteints. Ou bien étendre la plage vers le
haut (`L = 144` a été montré éligible au §14) pour raccourcir l'intervalle par un bras de levier
plus long plutôt que par plus de bras.

**Non éligible.** Rescorer OBTC02. Relâcher la marge d'équivalence après avoir vu le résultat.
Retirer de la région la statistique qui échoue. Ouvrir l'axe E, qu'aucune mission n'a défini.
Toute affirmation sur H3, la reproduction ou la cohésion autonome.

---

```
MISSION
ORGANIZER-BOUND-DOMAIN-INVARIANCE-01

DISPOSITION
DOMAIN_INVARIANCE_PARTIAL

LEGACY_D_GATE_STATUS
MISALIGNED_WITH_DOMAIN_INVARIANCE

ROUTE
B

DESIGN_STATUS
OUTCOME_INFORMED_TARGETED_FOLLOWUP

CONFIRMATORY_DATA_STATUS
FRESH_AND_PREREGISTERED

DOMAIN_SIZES
36, 72, 96

DOMAIN_INVARIANCE_REGION_PASS
False

A_SHAPE_INVARIANCE
FAIL sur |coeur - organisateur| seulement : beta = +0.0708, |beta| + c.se = 0.2918 contre une
marge de 0.25. R_g +0.0077 et r80 +0.0351 passent.

B_DENSITY_EXPONENT
PASS : gamma = -2.0485 +- 0.0211, exclut -1 et 0.

C_NO_TRUE_WINDING
PASS : 0 enroulement sur 2700 trames.

D_PROFILE_COMPATIBILITY
PASS : 5/4, 4/4, 5/4 bras dans l'enveloppe gelee.

LEGACY_D_GATE_ON_FRESH_SEEDS
L=36 4/5, L=72 3/5, L=96 4/5. Le gate verrouille rejette 4 bras sains sur 15, y compris a la plus
petite taille de domaine.

DOMAIN_SIZE_INVARIANCE_STATUS
NOT_ESTABLISHED

AUTONOMOUS_COHESION_STATUS
NOT_ESTABLISHED

H3_STATUS
NOT_TESTED

REPRODUCTION_STATUS
NOT_TESTED

OBTC02_DISPOSITION_AFTER_OBDI01
ORGANIZER_BOUND_CLOUD_PARTIAL (inchangee)

UNBLOCKED_DISCRETE_KERNEL
EXACT

SAMPLED_CLOUD_STATISTICS
EXACT_LAW__MONTE_CARLO_EVALUATION

FULL_CAPACITY_CONSTRAINED_OPERATOR
APPROXIMATE_WITH_EMPIRICAL_ERROR

WHAT_IT_CHANGES
L'echec du domaine d'OBTC02 n'etait pas une decouverte sur la physique : c'etait une propriete de
l'instrument. Le gate herite fixe un rayon admissible qui ne bouge que de 1.6 % quand le domaine
double, ne compare jamais deux tailles, et rejette 40.7 % des bras sains a L = 72 avec un taux
qui croit quand on lui donne plus de donnees. Un test direct, preenregistre et evalue sur quinze
graines neuves montre au contraire que la taille du nuage ne depend pas du domaine sur un facteur
2.67 : exposant +0.008 sur le rayon de giration et +0.035 sur r80, densite en L^-2.049, aucun
enroulement sur 2700 trames, profil radial compatible avec le noyau exact partout. Ce qui manque
n'est pas un mecanisme mais de la precision sur une seule grandeur, l'ecart coeur-organisateur,
dont l'intervalle d'equivalence deborde la marge de 0.042 faute d'avoir dimensionne la mission
sur elle plutot que sur le rayon de giration.

NEXT_SCIENTIFIC_ELIGIBILITY
Replication de la meme region gelee, sans redesign, avec environ 8 bras par taille et une regle
preenregistree pour les bras eteints ; ou extension a L = 144.

SCIENTIFIC_RUNS_USED
15 : confirmation 15 de 24, controle 0 de 8, calibration 0 de 4, sonde de cout 0 de 2,
invalides 0. Les tests d'instrument tournent en mode TEST et ne laissent aucune entree au
registre ; la sonde de pipeline est reclassee non scientifique et declaree.

TECHNICALLY_INVALID_RUNS
0

PROTOCOL_VIOLATIONS
NONE. Aucun seuil scientifique n'a bouge, aucun run n'a ete relance, aucune graine remplacee,
aucun echec rejoue, aucun arret anticipe. Quatre defauts de conception de cette mission sont
consignes au paragraphe 31 : l'extinction non prespecifiee, la puissance dimensionnee sur la
mauvaise statistique, un commit groupe, et un espace de dispositions reconstruit.

PROVENANCE_STATUS
SELF_CONTAINED_SPLIT_DELIVERY_PASS

TOMMY_ACTION_REQUIRED
NONE
```
