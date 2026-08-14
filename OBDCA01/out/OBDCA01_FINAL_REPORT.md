```
MISSION              ORGANIZER-BOUND-DOMAIN-CONTRACT-AUDIT-01
DISPOSITION          CUMULATIVE_CLOUD_QUALIFIED_UNDER_FROZEN_PRIMARY__ATTACHMENT_ESTIMAND_LIMITED
SCIENTIFIC_RUNS_USED 0
```

Deux conclusions, indépendantes l'une de l'autre, et toutes deux défavorables à ma propre mission
précédente.

**La marge liante était `0,25`.** Le protocole gelé d'OBDI02 porte exactement **un** champ nommé
`equivalence_margin`, valant `0,25`, et le gate gelé n'utilise que ce champ pour fixer `PASS`. Le
chiffre `0,042` vit dans un **autre** champ, `stringent_reference_margin`, dont la chaîne de
statut gelée dit textuellement *« reported, never decisive »*. Le TOST à `0,25` passe avec
`p = 6,6 × 10⁻⁵`. La disposition finale d'OBDI02 a pourtant été choisie par
`analysis_obdi02.py`, un fichier **écrit après l'ouverture des résultats**, qui a ajouté une
condition — l'intervalle devait tenir dans `[−0,042 ; +0,042]` — que le gel avait explicitement
privée de force décisoire. **C'est une violation de protocole**, dans le sens conservateur : elle
a retenu une qualification que le gel accordait.

**Et pourtant l'estimand primaire ne mesure pas ce qu'il prétend.** `|C−Y|` dépend massivement de
la population : `corr(log N_X, log |C−Y|) = −0,846`, le coefficient de `log N_X` dans le modèle
conjoint a un `t = −18,0`, le sous-échantillonnage des champs **réels** montre que réduire la
population de ~115 à 5 molécules gonfle la distance mesurée d'un facteur `1,40` sans toucher à la
physique, et surtout : sous un mécanisme **strictement invariant en `L`**, dans lequel seules les
distributions de population observées sont injectées, un coefficient au moins aussi grand que
`+0,0822` apparaît avec probabilité **`0,357`**. L'effet est donc **typique d'un pur artefact de
mesure** et ne peut pas être attribué à la taille du domaine.

La qualification cumulative est accordée sous le primaire gelé, et elle est **explicitement
limitée** : la taille et le profil du nuage sont bornés ; l'invariance précise du **centre
estimé** n'est pas revendiquée.

---

## 1. Provenance

Artefact scindé d'OBDI02 recomposé dans un répertoire neuf, relu sous `unshare -rn` avec
`GIT_NO_LAZY_FETCH=1`.

```
6 morceaux, empreintes des six conformes ; archive recomposée conforme
git rev-parse HEAD           be09dde3c56212930b4848bb50df409b57e7d2d0   conforme
git rev-parse HEAD^{tree}    83b0592b1479e3715d44108a3cc6cf6d07c8e6fa   conforme
git rev-list --missing=print 0 objet manquant
git fsck --full              propre
git status --porcelain       vide
branche codex/organizer-bound-domain-invariance-02 ; 1667 fichiers ; 8 commits
frontière superficielle 5a37a7be… = tête d'OBDI01 ; aucun distant ; aucun pack promisor
138 trajectoires présentes ; registre des seeds, manifeste de gel, code d'analyse, sortie de
puissance, rapport final, artefacts OBDI01 pour la généalogie : tous présents
```

**Reproduction du `METHODS_CORE_HASH`.** Les seize fichiers du manifeste ont été retrouvés, avec
leur empreinte exacte, répartis sur `OBDI02/code`, `OBDI01/code` et `OBTC02/code`, et le hash a
été **recalculé depuis le manifeste** : `59b19169fa087caa39f8b1139a946d8a1cbad23519bea3e604c8bd5bad525f1b`,
identique à l'enregistré. Le `spec_sha256` se reproduit également.

`PROVENANCE_STATUS = SELF_CONTAINED_SPLIT_DELIVERY_PASS`.

## 2. HEAD, arbre, branche et commits

```
branche   codex/organizer-bound-domain-contract-audit-01
parent    be09dde3c56212930b4848bb50df409b57e7d2d0   (tête d'OBDI02, inchangée)
commits   six, séparés selon le §18 du mandat
```

Aucun commit hérité n'a été réécrit.

## 3. Hiérarchie des artifacts

Vérifiée dans le dépôt, pas présumée. Chaque fichier a été daté par le commit qui l'a introduit,
puis classé par rapport au commit de gel (`2bffe759`) et au commit des runs (`80e7f88d`).

| rang | niveau | fichier | phase | dans `METHODS_CORE_HASH` |
|---|---|---|---|---|
| 1 | spécification machine gelée avant les runs | `OBDI02/code/obdi02_protocol.yaml` | AT_FREEZE | **oui** |
| 2 | contenu couvert par le hash | 16 fichiers | PRE_FREEZE / AT_FREEZE | **oui** |
| 3 | manifeste de gel | `OBDI02/out/_freeze.json` | AT_FREEZE | non |
| 4 | plan pré-freeze horodaté | `_plan_inputs.json`, `_power.json`, `_seeds.json`, `_summary_choice.json` | PRE_FREEZE | non |
| 5 | code d'analyse gelé | `gate_obdi02.py`, `run_obdi02.py`, `worker_obdi02.py` | PRE_FREEZE | **oui** |
| 6 | rapport final | `OBDI02_FINAL_REPORT.md` | POST_RUN | non |
| 7 | fichiers reconstruits après les runs | `analysis_obdi02.py`, `_evidence.json`, `_posthoc.json`, `figures_obdi02.py` | **POST_RUN** | **non** |
| 8 | résumé conversationnel | — | — | — |

```
FROZEN_PROTOCOL_SOURCE_OF_TRUTH   OBDI02/code/obdi02_protocol.yaml
FROZEN_ANALYSIS_SOURCE_OF_TRUTH   OBDI02/code/gate_obdi02.py, run_obdi02.py, worker_obdi02.py
POSTRUN_RECONSTRUCTED_FILES       analysis_obdi02.py, figures_obdi02.py, readback_obdi02.py,
                                  OBDI02_FINAL_REPORT.md, SHA256SUMS, _arms.json, _delivery.json,
                                  _evidence.json, _posthoc.json, _r80_org_frames.json,
                                  _readback.json, _results.json, _run.log,
                                  obdi02_precision_closure.png
```

**Règle appliquée** : un fichier de rang 7 ne peut ajouter rétroactivement ni marge, ni outcome
primaire, ni condition de qualification, ni disposition, ni règle d'arrêt. Il peut seulement
rapporter, expliquer ou diagnostiquer ce que les rangs 1 à 5 ont déjà fixé.

## 4. Source de vérité du protocole

`OBDI02/code/obdi02_protocol.yaml`, introduit **au commit de gel**, couvert par le
`METHODS_CORE_HASH`. Les règles liantes qu'il contient sont exactement deux :

```
primary_endpoint.decision_rule
  PASS si et seulement si l'intervalle bilatéral à 90 % entier tient dans la marge.
  Une estimation ponctuelle proche de zéro ne suffit pas. Exclure H_linear ne suffit pas.
  Exclure H_sublinear ne suffit pas.

population_support_gate.qualification
  « the global qualification requires BOTH the population support gate AND the conditional
    equivalence test »
```

Il ne contient **aucune** table faisant correspondre un résultat à l'un des neuf noms de
disposition. Cette absence est le point d'entrée du défaut du §15.

## 5. Chronologie de `0.25`

```
occurrences totales : 110 (plus 5 sous la forme 0.2500)
couvertes par METHODS_CORE_HASH : obdi02_protocol.yaml UNIQUEMENT
champ                 primary_endpoint.equivalence_margin
valeur                0.25
phase du fichier      AT_FREEZE
rôle                  EQUIVALENCE_MARGIN — le seul champ portant ce nom dans tout le gel
usage par le gate     gate_obdi02.py : delta = float(p["equivalence_margin"]) ;
                      "PASS": achieved <= delta
```

Origine : lue dans `OBDI01/code/obdi01_protocol.yaml`,
`principal_outcome.components.A_shape_invariance.margin`, elle-même justifiée dans le gel
d'OBDI01 comme « la moitié de l'exposant de l'alternative non bornée la plus lente ».

## 6. Chronologie de `0.2918`

```
occurrences : 14 ; couvertes par le hash : obdi02_protocol.yaml
rôle        : BORNE ATTEINTE par OBDI01, |β| + c·se avec c = 2,7996
définition  : 0.0708 + 2.799625 × 0.0789 = 0.2918
ce n'est pas une marge ; c'est une sortie de test
```

## 7. Chronologie de `0.0418` et `0.042`

```
0.0418 : 13 occurrences ; rôle MARGIN_EXCESS ; définition 0.2918 − 0.2500
0.042  : 133 occurrences ; couvertes par le hash : obdi02_protocol.yaml et run_obdi02.py
         champ  primary_endpoint.stringent_reference_margin
         statut gelé, verbatim : « reported, never decisive »
         usage par le gate : bloc STRINGENT_REFERENCE, marqué
                             "PRE-DECLARED UNDERPOWERED — reported, never decisive"
         usage par run_obdi02.py : une ligne d'impression, étiquetée « pre-declared underpowered »
```

Le premier fichier à en faire une **condition** est `analysis_obdi02.py`, phase **POST_RUN**, rang
7, hors `METHODS_CORE_HASH` : il crée la clé `primary_interval_inside_[-0.042,+0.042]` et la place
dans la conjonction qui décide de la qualification.

## 8. Rôle exact de chaque valeur

```
0.25    EQUIVALENCE_MARGIN, liante, gelée, utilisée par le gate gelé
0.2918  borne atteinte par OBDI01, sortie de test
0.0418  excès de cette borne sur la marge
0.042   cible secondaire de précision, gelée comme NON décisive, promue en gate par un
        fichier post-run
```

**Verdict sur les cinq affirmations :**

```
A  0.25_WAS_THE_BINDING_PRIMARY_MARGIN                          VRAI
B  0.042_WAS_THE_BINDING_PRIMARY_MARGIN                          FAUX
C  0.25_PRIMARY__0.042_SECONDARY_PRECISION_TARGET                VRAI — retenu, plus complet
D  THE_FROZEN_PROTOCOL_CONTAINS_CONFLICTING_BINDING_MARGINS      FAUX
E  THE_BINDING_MARGIN_IS_NOT_RECOVERABLE                         FAUX
```

Il n'y a pas de conflit **dans** le gel : un champ est la marge, un autre est une référence
explicitement non décisoire. Le conflit est apparu **après** le gel, entre le rang 1 et le rang 7.

## 9. Outcome primaire

```
PRIMARY_ESTIMAND
β_CY = d log d_CY / d log L ,  d_CY(L) = médiane_{trames de la fenêtre} |C−Y|  ÷  pred(L)
```

`pred(L)` est la prédiction exacte de taille finie de l'opérateur source–transport–décès.

## 10. Unité indépendante

```
INDEPENDENT_UNIT      SEED
WITHIN_SEED_SUMMARY   médiane de |C−Y| sur les 180 trames de la fenêtre d'analyse
C                     centre de Fréchet toroïdal du champ X, minimiseur exact séparable, sur un
                      site du réseau
Y                     l'unique cellule avec n_Y > 0
métrique              hypot(wdist1(dy, L), wdist1(dx, L))
```

Traitement gelé des extinctions : la graine est consommée, jamais remplacée, jamais supprimée.
Traitement gelé des bras à faible population : **aucun**. La définition gelée d'un bras
analysable est seulement « résumé fini et strictement positif ».

## 11. Méthode d'équivalence

TOST sous forme d'intervalle, `α = 0,05` unilatéral par test, intervalle bilatéral à **90 %**,
`c = 1,64485`. **Recalcul par deux routes indépendantes :**

```
route 1  le gate gelé lui-même, ré-exécuté          β = +0.08219488   se = 0.04390627
route 2  seconde implémentation, écrite ici, lisant les .npz bruts, reconstruisant |C−Y| depuis
         les positions du centre et de l'organisateur, refaisant la médiane, le logarithme, la
         pente pondérée et l'intervalle
                                                    β = +0.08219488   se = 0.04390627
écart |Δβ| = 0.00e+00   |Δse| = 0.00e+00
résumés par bras identiques sur 129 bras, indéfinis des deux côtés sur 9, total 138
la route 2 a reproduit CHAQUE distance enregistrée à partir des positions : True
```

## 12. Taxonomie gelée

Les neuf noms sont bien gelés dans le protocole. **Aucune règle gelée ne fait correspondre un
résultat à un nom.** Ce qui est gelé à la place, ce sont les deux règles liantes du §4.

## 13. TOST à `0.25`

```
intervalle 90 %      [ +0.00998 ; +0.15441 ]     entièrement inclus dans [−0.25 ; +0.25]
test unilatéral bas  statistique  7.56   p = 1.93e−14
test unilatéral haut statistique  3.82   p = 6.62e−05
p du TOST            6.62e−05  <  α = 0.05
VERDICT              PASS
```

Pour mémoire seulement, l'intervalle à 99,49 % qu'employait OBDI01, appliqué à ces données :
`[−0.0407 ; +0.2051]`, borne atteinte `0.2051` — il passerait aussi à `0,25`.

## 14. TOST à `0.042`

```
intervalle 90 %      [ +0.00998 ; +0.15441 ]     déborde [−0.042 ; +0.042]
test unilatéral bas  p = 2.34e−03
test unilatéral haut p = 0.820
p du TOST            0.820
VERDICT              FAIL
```

**Taille d'effet sur `L = 36 → 96` (facteur 2,67).** L'exposant se lit
`(96/36)^β` :

```
estimation ponctuelle   ×1.0840
borne basse de l'IC     ×1.0098
borne haute de l'IC     ×1.1635
ce que la marge 0.25 autorise    ×1.2779
ce que la cible 0.042 autorise   ×1.0421
```

## 15. Application littérale de la disposition

**Sous la marge `0,25`** — l'intervalle est entièrement contenu, le gate de maintien de
population passe aux trois tailles (43, 42, 44 analysables pour un seuil de 39), donc la règle
gelée de qualification globale — « BOTH the population support gate AND the conditional
equivalence test » — est **satisfaite**.

Pourquoi l'équivalence n'a-t-elle pas été déclarée dans OBDI02 ? **Elle l'a été.**
`OBDI02/out/_results.json` enregistre `PRIMARY.PASS = true`. C'est la disposition finale qui a
divergé, choisie par `analysis_obdi02.py` (POST_RUN, rang 7, hors hash), lequel a ajouté la
condition `primary_interval_inside_[-0.042,+0.042]`.

**Sous la marge `0,042`**, hypothétiquement : l'estimation ponctuelle sort de la marge et
l'intervalle à 90 % exclut zéro. La taxonomie n'autoriserait alors pas vraiment
`..._NOT_ESTABLISHED`, qui exige une estimation compatible avec zéro et l'absence de preuve
positive de croissance ; la lecture honnête serait plus proche de `DOMAIN_SIZE_INVARIANCE_FAIL`.
Cette branche est sans objet : `0,042` n'est pas la marge liante.

**Règle de sous-puissance.** Le protocole gelé ne déclare pas `0,042` liante ; il le déclare
non décisoire **et** sous-puissant à l'avance (puissance `0,314`, `n` requis 200 par taille
contre un plafond de 49). La règle d'arrêt pour sous-puissance porte sur le **primaire liant** :
à `0,25` le `n` requis était **10** et **46** ont été lancés. Le plan était donc **sur-puissant**
pour le test qui gouvernait.

```
PROTOCOL_VIOLATION : OUI, mais pas celle-là.
```

La violation est l'ajout post-run d'une condition de qualification par un fichier de rang 7.
Elle va dans le sens **conservateur** : elle retient une qualification que le gel accordait. Elle
n'a fabriqué aucun résultat, déplacé aucun seuil dans le sens permissif, écarté aucun bras,
remplacé aucune graine. C'est néanmoins une violation, et elle est consignée comme telle.

```
DISPOSITION CONFORME QU'OBDI02 AURAIT DÛ ADOPTER
ORGANIZER_BOUND_TURNOVER_CLOUD_QUALIFIED_BY_DOMAIN_PRECISION_CLOSURE
```

## 16. Conformité de l'analyse de puissance

```
n requis à la marge liante 0.25        10 par taille       →  46 lancés
n requis à la référence 0.042          200 par taille      →  hors plafond d'un facteur 4
plafond déclaré avant les runs         49 par taille
puissance déclarée à 0.042 avant les runs   0.314
```

Conforme. La sous-puissance de la référence stringente était déclarée **avant** les runs, et elle
ne portait pas sur le test liant.

## 17. Matrice des 138 bras

```
138 bras   138 techniquement valides   138 accords online/post hoc   0 invalidité technique
9 extinctions        3 à L=36, 4 à L=72, 2 à L=96
6 bras non éteints à très faible population   1 à L=36, 1 à L=72, 4 à L=96
```

La matrice complète — graine, `L`, validité, extinction, `N_X` médian et minimal, fraction de la
fenêtre sous les seuils de population, `|C−Y|`, `R_g`, `r80`, profil, winding, classifications
online et post hoc, inclusion et motif d'exclusion — est dans `_adjudication.json`, champ
`ARM_MATRIX`. Le seul motif d'exclusion présent est « extinct : le résumé par graine est
indéfini ». **Aucune exclusion post-hoc n'a été appliquée.**

**Poids dans la régression.** L'estimateur gelé pondère une **taille**, pas un bras :
`w_L = n_L / sd_L(log résumé)²`. Un bras extrême agit donc deux fois — il déplace la moyenne de
sa taille et il gonfle l'écart-type de cette taille, ce qui en abaisse le poids. L'influence
nette est mesurée, pas argumentée : le bras le plus influent est `L72/seed8101006`, dont le
retrait déplacerait `β` de `−0,0338`.

## 18. Extinctions

```
L=36  3/46      L=72  4/46      L=96  2/46      total 9/138 = 6,5 %
```

Aucune tendance avec `L`. Chaque extinction a consommé sa graine, aucune n'a été remplacée,
aucune n'a été supprimée comme donnée manquante.

## 19. Bras à faible population

Règle post-hoc, diagnostique, **jamais appliquée** : `N_X` moyen sous la moitié de la médiane des
bras survivants de la même taille.

```
L=36  1/46      L=72  1/46      L=96  4/46
```

Ces bras sont **analysables** au sens gelé — leur résumé est fini et positif — tout en portant
une population cinq à vingt fois trop faible. La définition gelée ne sépare pas « le nuage
existe » de « le nuage est mesurable ». C'est la porte par laquelle la population entre dans une
statistique spatiale.

## 20. Influence de `N_X`

```
corr(log N_X, log |C−Y|)                                        −0.846
coefficient de log N_X dans  log|C−Y| = α + β_L log L + b log N_X   t = −18.03
β_L seul                                                        +0.1073
β_L avec log N_X contrôlé                                       +0.0557
β_L restreint aux bras N_X ≥ 60                                 +0.0414
β_L calculé sur les médianes par taille                         −0.0198
médianes inter-bras de |C−Y|      3.000 / 3.081 / 3.000 — plates
```

Contrôler la population divise le coefficient par deux ; le restreindre à une bande de population
définie indépendamment le divise par 2,6 ; l'agréger par une médiane robuste en change le signe.

## 21. Erreur finie du centre

**Dérivation.** Pour `N` molécules issues d'une loi de covariance `Σ`, la moyenne empirique
vérifie `E‖Ĉ − C*‖² = tr(Σ)/N`. Sur le tore le centre de Fréchet coïncide avec la moyenne
empirique tant que le nuage ne s'enroule pas, et le rayon de giration sans centre vérifie
`R_g² = tr(Σ)`, d'où une erreur par axe `σ = R_g / √(2N)`.

```
STATUT : EXACT pour la moyenne empirique de positions i.i.d. ;
         APPROXIMATIF pour le centre de Fréchet sur un tore, et seulement hors enroulement.
```

Ce n'est **pas** revendiqué exact : les vérifications numériques le soutiennent, `R_g²/tr(Σ)`
valant `0,944` et `0,968` sur les champs testés. Termes non modélisés et consignés :
autocorrélation temporelle, multimodalité, halo, arrondi du centre au réseau, enroulement.

Avec `μ = 3,124` (l'offset vrai prédit par l'opérateur) et `R_g` typique, la loi de Rice donne :

```
N      3      5      10     20     40     60     80     100    121    160
E|C−Y| 4.161  3.738  3.417  3.265  3.194  3.170  3.159  3.152  3.147  3.141
```

Passer de `N = 121` à `N = 5` gonfle la distance mesurée de **18,8 %**, à attachement physique
rigoureusement inchangé.

## 22. Assay synthétique

Construit depuis la loi source–transport gelée, **sans aucun effet de domaine** : même centre
physique relatif à toutes les tailles, même loi, même algorithme de centre, même résumé, et des
effectifs **imposés** sur une grille couvrant les valeurs observées, 600 tirages par cellule.

```
N = 5     E|C−Y| = 3.685 / 3.875 / 3.967   à L = 36 / 72 / 96
N = 110   E|C−Y| = 3.002 / 3.277 / 3.169
```

Contrôle de l'assay : à `N` fixé, l'écart relatif maximal entre les trois tailles va de 2,8 % à
8,7 % — c'est le plancher de bruit de l'assay lui-même, et il est rapporté plutôt que masqué.

## 23. Downsampling raw-only

Sur 24 bras **réels** à population saine, on conserve la géométrie et la source produites par le
moteur et on ne réduit que le nombre de molécules, 200 réplicats par cellule.

```
N conservées      3      5      8      12     20     30     50     80
|C−Y| / pleine   1.602  1.400  1.277  1.204  1.138  1.098  1.075  1.051
déplacement moyen du centre (cellules)
                 1.98   1.50   1.20   0.97   0.76   0.62   0.44   0.29
```

## 24. Nul conditionné sur les populations

Mécanisme latent **strictement invariant en `L`** ; seules les distributions de population
effectivement observées par taille sont injectées ; 4000 réplicats.

```
β du nul   moyenne +0.0431   écart-type 0.1057   q95 +0.2144   q99 +0.2905
β observé  +0.0822
P(β_nul ≥ β_observé) = 0.357        CLASSIFICATION : TYPIQUE
```

La moyenne du nul n'est pas nulle mais `+0,043` : les queues de basse population sont un peu plus
lourdes aux grandes tailles, ce qui suffit à créer un coefficient positif apparent sans la moindre
physique de domaine.

## 25. Validité de l'estimand

```
ATTACHMENT_ESTIMAND_VALIDITY = ATTACHMENT_ESTIMAND_POPULATION_CONFOUNDED
```

Les trois conditions exigées sont établies : (1) la métrique dépend fortement de `N_X` par
construction **et** par erreur d'estimation ; (2) cette dépendance produit à elle seule un
coefficient au moins aussi grand que l'observé avec probabilité `0,357` ; (3) l'effet ne doit
donc pas être lu comme un éloignement physique du nuage.

**Réserve honnête.** Le confondant n'est pas propre à `|C−Y|` : les garde-fous sont eux aussi
sensibles à la population — `corr(log N_X, ·)` vaut `−0,600` pour `log R_g`, `−0,587` pour
`log r80` et `−0,881` pour la distance TV du profil, contre `−0,846` pour la métrique primaire.
Ce qui les distingue est que **leurs coefficients observés sont déjà indiscernables de zéro**, si
bien qu'aucun artefact n'a besoin d'être invoqué pour les expliquer, alors que le coefficient
primaire est entièrement expliqué par un artefact.

Cela n'annule pas le résultat gelé. Cela en limite l'interprétation physique.

## 26. Métriques alternatives — conception seulement

Comparaison **raw-only** sur les champs réels, mêmes 24 bras, même sous-échantillonnage :

```
N conservées                     3       5       8      12      20      30      50      80
|C−Y|            (centre)      1.602   1.400   1.277  1.204   1.138   1.098   1.075   1.051
r80,Y            (quantile)    0.874   0.925   0.950  0.961   0.972   0.987   0.992   0.999
moyenne de d_T(X_i,Y)²         0.984   1.002   0.997  0.999   0.986   1.001   0.998   1.001
```

`r80_Y` évite l'estimation d'un centre mais reste biaisé : un quantile de `N` distances dérive de
`12,6 %`, et sa corrélation avec `log N_X` vaut `−0,870`, légèrement **pire** que la métrique
primaire. Son coefficient mesuré ici vaut `+0,0200 ± 0,0173`.

```
SELECTED_FOR_A_FUTURE_MISSION = moyenne par particule de d_T(X_i, Y)²
```

C'est le seul candidat dont l'absence de biais de population est **structurelle** et non
empirique : l'espérance d'une moyenne ne dépend pas du nombre de tirages, et le
sous-échantillonnage le confirme sur des champs réels jusqu'à trois molécules, à `1,6 %` près.
L'opérateur en fournit le second moment exactement, donc une prédiction sans paramètre existe.
Son coût est que la statistique de fenêtre n'est pas enregistrée dans les archives existantes :
elle est calculable sur le champ final de chaque bras, pas sur toute la fenêtre. Sa variance est
plus grande que celle d'un quantile, ce qui devra être payé en taille d'échantillon et non
dissimulé. **Aucun seuil confirmatoire n'est choisi ici.**

## 27. Statut cumulatif du nuage

```
maintien de population   43/46, 42/46, 44/46 analysables ; seuil requis 39/46      PASS
R_g selon L              β = −0.00304   IC 90 % [−0.01691 ; +0.01083]   ×0.997     PASS
r80 selon L              β = +0.00373   IC 90 % [−0.00823 ; +0.01569]   ×1.004     PASS
densité                  γ = −2.0612    IC 90 % [−2.2014 ; −1.9210]                PASS
winding                  0 / 8280 trames à chaque taille, 0 / 24 840 au total      ABSENT
profil radial            42/46, 41/46, 41/46 bras ; seuil requis 37/46             PASS
gate D historique        29/46, 25/46, 34/46 bras passent — 36,2 % d'échec         SECONDAIRE
                                                                                   DÉSALIGNÉ
|C−Y|                    TOST à 0.25 PASS ; estimand POPULATION_CONFOUNDED
```

```
CUMULATIVE_CLOUD_STATUS = QUALIFIED
```

**Portée autorisée.** Dans le LawSpec équilibré sans cohésion ajoutée, une source organisatrice
mobile maintient causalement un nuage dissipatif matériellement renouvelé dont la **taille propre
et le profil** restent bornés sur les tailles de domaine testées. La conclusion s'arrête là : elle
ne revendique **pas** une invariance précise du centre estimé, parce que la métrique qui la
porterait est confondue avec la population.

Interdits, inchangés : self-bound, cohésion autonome, cellule, identité, reproduction, mémoire,
confirmation d'H3, validation globale de Kamimura–Kaneko.

## 28. Prochaine éligibilité

```
NEXT_SCIENTIFIC_ELIGIBILITY = ORGANIZER_BOUND_TIMESCALE_REDERIVATION_ONLY
```

La marge primaire liante `0,25` passe, aucun conflit interne au gel n'existe, et aucun défaut
invalidant n'est trouvé. Le défaut de précision de `|C−Y|` reste une limitation et un chantier
méthodologique **parallèle** : il porte sur une métrique de position, et les temps de formation,
de relaxation et de décroissance n'en dépendent pas. Le chantier parallèle a un objet précis,
défini au §26, et il ne demande aucun run tant que l'estimand n'est pas préenregistré.

---

```
GOOD_NEWS
Le contrat de preuve est reparable et il a ete repare. La marge liante est retrouvee sans
ambiguite : le protocole gele porte un seul champ equivalence_margin, valant 0.25, et le gate
gele n'utilise que lui. Le TOST correspondant passe avec p = 6.6e-05, recalcule par deux
implementations independantes qui s'accordent au dernier bit. Le gate de maintien de population
passe aux trois tailles. La regle gelee de qualification globale est donc satisfaite, et le nuage
lie a l'organisateur est QUALIFIE cumulativement pour sa taille propre et son profil : R_g donne
beta = -0.0030 [IC 90 pct -0.0169, +0.0108], r80 donne +0.0037 [-0.0082, +0.0157], la densite
gamma = -2.0612, zero enroulement sur 24 840 trames, le profil radial passe partout. La
re-derivation des temps devient eligible.

LESS_GOOD_NEWS
Deux defauts, tous deux miens. Premier : la disposition finale d'OBDI02 a ete choisie par un
fichier ecrit APRES l'ouverture des resultats, qui a promu en condition de qualification un
chiffre que le gel avait explicitement declare non decisoire. C'est une violation de protocole,
conservatrice mais reelle : elle a retenu une qualification que le gel accordait. Second : la
metrique qui a occupe trois missions ne mesure pas ce qu'on lui pretait. |C-Y| est confondu avec
la population — correlation -0.846, t = -18.0 pour log N_X, inflation x1.40 par
sous-echantillonnage des champs reels de 115 a 5 molecules — et sous un mecanisme strictement
invariant en L, injecter les seules distributions de population observees produit un coefficient
au moins aussi grand que l'observe avec probabilite 0.357. L'effet beta = +0.0822 est donc
TYPIQUE d'un pur artefact de mesure. La reserve vaut partiellement pour les garde-fous, eux aussi
population-sensibles, a ceci pres que leurs coefficients sont deja indiscernables de zero.

FROZEN_PRIMARY_MARGIN
0.25

TOST_AT_0P25
PASS

TOST_AT_0P042
FAIL

STRICT_0P042_TARGET_ROLE
SECONDARY

ATTACHMENT_ESTIMAND_VALIDITY
POPULATION_CONFOUNDED

INTRINSIC_CLOUD_SIZE_INVARIANCE
PASS

NON_EXTENSIVE_POPULATION
PASS

TRUE_WINDING
ABSENT_IN_TESTED_RANGE

RADIAL_PROFILE_COMPATIBILITY
PASS

CUMULATIVE_CLOUD_STATUS
QUALIFIED

WHAT_IT_CHANGES
L'adjudication change trois choses. Elle retablit la qualification cumulative que le protocole
gele d'OBDI02 accordait et qu'un fichier post-run avait retenue : la taille propre du nuage, sa
densite, son profil et l'absence d'enroulement sont qualifies sur 138 bras frais. Elle disqualifie
en meme temps l'interpretation physique de la seule metrique qui resistait : l'ecart coeur-
organisateur ne mesure pas un eloignement du nuage mais, pour l'essentiel, l'incertitude du centre
quand la population s'effondre, et le petit coefficient positif observe est reproductible sans la
moindre physique de domaine. Elle etablit enfin une regle de contrat utilisable : un fichier ecrit
apres l'ouverture des resultats ne peut pas ajouter une condition de qualification, et la
hierarchie des huit rangs rend cette regle verifiable plutot que rhetorique.

NEXT_SCIENTIFIC_ELIGIBILITY
ORGANIZER_BOUND_TIMESCALE_REDERIVATION_ONLY

H3_STATUS
NOT_TESTED

REPRODUCTION_STATUS
NOT_TESTED

SCIENTIFIC_RUNS_USED
0

PROTOCOL_VIOLATIONS
UNE. La disposition finale d'OBDI02 a ete selectionnee par OBDI02/code/analysis_obdi02.py, fichier
de phase POST_RUN, rang 7 de la hierarchie, hors METHODS_CORE_HASH, qui a ajoute la condition
primary_interval_inside_[-0.042,+0.042] alors que le protocole gele qualifie ce chiffre de
« reported, never decisive ». La violation va dans le sens conservateur. La disposition conforme
etait ORGANIZER_BOUND_TURNOVER_CLOUD_QUALIFIED_BY_DOMAIN_PRECISION_CLOSURE. Aucune autre
violation : aucun seuil deplace dans le sens permissif, aucun bras ecarte, aucune graine
remplacee, aucun run relance, et la regle de sous-puissance ne s'appliquait pas au test liant.

PROVENANCE_STATUS
SELF_CONTAINED_SPLIT_DELIVERY_PASS

TOMMY_ACTION_REQUIRED
NONE
```
