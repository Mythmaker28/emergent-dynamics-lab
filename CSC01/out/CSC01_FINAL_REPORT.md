```
MISSION       CHEMOSTAT-SPATIAL-COHESION-01
DISPOSITION   INHERITED_SPATIAL_FAILURE_REATTRIBUTED__COHESION_NOT_QUALIFIED
```

L'échec spatial hérité d'ORR01 n'était pas une délocalisation. La population `X` du chémostat
équilibré **est** localisée, durable et traversée par le renouvellement — et sa localisation
s'explique entièrement, sans paramètre libre, par une source ponctuelle qui diffuse et une durée
de vie finie. Ce qu'ORR01 a mesuré comme un échec spatial était en réalité **deux défauts de son
propre gate**, démontrés ici de façon constructive. Le mécanisme de cohésion minimal sélectionné
augmente la cohésion de façon mesurable et appariée, mais ne franchit pas le critère gelé.

---

## 1. Verrou de livraison

L'artefact auto-suffisant hérité, `ORR01_offline_repo.tar.gz`, pesait 38 826 938 octets et
dépassait la limite de livraison de 30 Mo. `zstd` est absent de cet environnement et `xz -9e` ne
gagne que 0.35 % (38 952 960 → 38 817 244 octets) parce que la charge est déjà constituée de
packfiles git compressés. L'artefact a donc été **scindé**, sur une copie, l'original restant
octet pour octet inchangé.

```
parts                3, tailles 19 000 000 / 19 000 000 / 826 938 octets, toutes < 29 Mo
sha256 des parts     0e2ade14…7943   0b8ff48e…1851   4640a1eb…ec26
sha256 de l'ensemble f06e8b7888b3742400ae5a05159caac3261520c0c5280e9b0d9d5e5f73267f95
scripts              reassemble_and_verify.sh / .ps1, offline_readback.sh, SHA256SUMS
```

La vérification a été **exécutée**, pas seulement écrite. Réassemblage dans un répertoire neuf,
sommes des parts OK, sha256 de l'ensemble OK, extraction OK, puis clone **réseau coupé**
(`unshare -rn`, contrôle DNS et TCP négatifs à l'intérieur du namespace, positifs à l'extérieur,
`GIT_NO_LAZY_FETCH=1`) :

```
HEAD          d89c2217697c33cfb66a6878b885442f13b19c57   OK
arbre         b1cb4ae8f5d0c829eee752d11dd407310fd6c477   OK
fichiers      1292        objets manquants 0        fsck propre
tests ORR01 rejoués depuis l'état reconstruit : PROTOCOL_ADVERSARIAL_AUDIT = PASS, ALL_PASS = True
PROVENANCE_STATUS = SELF_CONTAINED_SPLIT_DELIVERY_PASS
```

Déviation de nommage, consignée en append-only (D-1) : les parts portent le nom de l'artefact
**ORR01**, parce que c'est lui qui était indélivrable. L'artefact CSC01 est scindé selon le même
schéma en fin de mission.

## 2. Les deux résultats hérités, séparés

`CSC01_INHERITANCE_NOTE.md`, append-only, ne modifie aucun octet gelé.

| grandeur | contrôle additif (v1) | chémostat équilibré (v2) |
|---|---|---|
| occupation finale | **20 736 = 100.0 % de la capacité**, 6 bras sur 6 | **7 781 = 37.5 %**, 6 bras sur 6 |
| dérive d'occupation | 1.622 – 1.627 | **0.00000**, `std(O) == 0` |
| capacité libre à l'organisateur (sur 16) | 0.14 – 0.20 | **8.96 – 9.17** |
| `N_X` moyen sur la fenêtre | 0.0 – 16.5 | **63.3 – 123.6** |

Le contrôle `SHAM_REINSERT` conserve l'occupation exactement mais ne renouvelle rien : `N_X`
moyen 0.1 et 16.1. Le maintien n'est donc pas attribuable à la conservation de l'occupation, mais
au **renouvellement matériel**.

```
INHERITED_OCCUPANCY_RATCHET_REPAIR = QUALIFIED
```

Un bras qui annule la dérive, conserve la capacité libre, empêche le remplissage et permet le
renouvellement de `X` n'est pas « une réparation échouée ». La disposition globale d'ORR01 reste
exacte au sens de son propre critère gelé et **n'est pas révisée** ; ce qui est corrigé est
l'attribution de la cause.

## 3. Le rejeu, et pourquoi il ne viole pas la contrainte « raw-only »

ORR01 n'a sauvegardé que 3 de ses 102 relevés de composantes par bras. L'histoire spatiale est
absente du brut ; l'état qui l'a produite est entièrement déterminé par la graine sauvegardée et
le moteur gelé. Le rejeu la re-dérive, et n'est admis qu'après **preuve mécanique**, bras par
bras :

```
série 10 250 x 29 rejouée == série enregistrée, bit pour bit (np.array_equal, float64)   6/6
six champs finaux entiers identiques                                                     6/6
gate post-hoc gelé, recalculé sur les 102 relevés régénérés, identique CHAMP PAR CHAMP    6/6
les 3 relevés effectivement sauvegardés reproduits à l'octet                              6/6
```

Le troisième test est le plus fort : il montre que le rejeu reproduit aussi les observables
**spatiales** qu'ORR01 avait jetées. Les rejeux sont comptés dans une classe déclarée **non
scientifique** ; `SCIENTIFIC_RUNS_USED` reste 0 pour la question A.

## 4. Géométrie torique, corrigée

Toute observable est définie pour être correcte sur un tore en **toutes** circonstances, y
compris masse enroulée ou multimodale : centre de Fréchet (site minimisant la somme pondérée des
distances toriques au carré, exact et séparable), rayon de giration sous sa forme **par paires**
sans centre, quantiles radiaux pondérés, diamètre géodésique, et test d'enroulement **exact** par
relèvement dans le revêtement universel. Là où ORR01 employait une définition valable seulement
hors enroulement, celle-ci est recalculée en parallèle pour que l'écart soit une mesure.

Douze tests d'intégrité, mode STATIC, 0 démarrage. Le labelliseur torique est vérifié
différentiellement contre celui d'ORR01 sur 60 masques aléatoires ; le profil de source
ponctuelle contre son propre moment analytique ; l'invariance par translation rigide sur toutes
les observables.

## 5. Les nuls, et lequel décide

| nul | ce qu'il contient | quantile observé de `r80`, moyenne sur 6 bras |
|---|---|---|
| N1 hasard spatial complet | rien | **0.000** |
| N4 permutation d'étiquettes | la distribution des comptes par cellule | **0.000** |
| N3 source ponctuelle statique, exacte | source ponctuelle + durée de vie | 0.73 – 1.00 |
| N3b source ponctuelle **errante** | la trajectoire réelle de l'organisateur, l'historique réel des naissances, diffusion libre, aucune interaction | **0.33 – 0.82** |

Battre N1 ne prouve que la localisation. N3b est le nul décisif : il reproduit la source réelle
et l'histoire de naissance réelle du bras, sans la moindre interaction entre molécules. La
population observée s'y place **en plein milieu**, jamais du côté compact, dans aucun bras et
pour aucune observable.

Le profil N3 est validé contre son propre résultat analytique : `⟨r²⟩ = 2a(1−µ)/µ = 24.90` sur le
réseau infini, 24.63 sur le tore `L = 36`, et `ℓ_X = √(D_X/µ_X) = 2.5` exactement avec
`D_X = q(1−q) = 0.025`.

## 6. Le cœur est asservi à l'organisateur

```
distance moyenne centre du cœur – organisateur      2.61 – 3.27 cellules   (ell_X = 2.5)
corrélation des trajectoires déroulées, axe y       0.895 – 0.943
corrélation des trajectoires déroulées, axe x       0.567 – 0.974
déplacement net de l'organisateur sur la fenêtre    7.3 – 24.7 cellules
déplacement net du cœur sur la fenêtre              8.1 – 21.9 cellules
```

Le cœur est un objet **spatialement continu** : son déplacement moyen sur 10 pas vaut 0.23–0.29
cellule contre 8.1–11.9 pour le nul N5 à trames décorrélées, soit un facteur de séparation de 32
à 49. Mais ce qu'il suit continûment, c'est l'organisateur.

## 7. Halo contre fragmentation

| grandeur, fenêtre de maintien | valeur sur les 6 bras |
|---|---|
| composantes satellites par trame | 28.5 – 32.9 |
| durée de vie médiane d'un satellite | **0 pas** (une seule trame) |
| durée de vie, quantile 0.90 | 20 pas |
| durée de vie maximale | 260 – 410 pas |
| fraction de la masse `X` hors composante principale | 0.39 – 0.50 |
| satellites vivant au moins `1/µ_X = 250` pas | quelques unités par bras |

C'est un **halo de renouvellement**, pas une fragmentation : une nuée de molécules isolées créées
et détruites en permanence autour d'un cœur. La composante principale n'est pas « la population »,
et le critère d'ORR01 qui l'exigeait ne mesurait pas ce qu'il croyait mesurer.

## 8. Le premier défaut du gate hérité : un substitut d'étendue pour un test de bord

ORR01 déclare `wraps = (extent ≥ L/2)` avec `extent = 2·max(dy, dx) + 1`. C'est une mesure
d'**étendue**, pas d'enroulement.

**Démonstration constructive** (test T10, état construit à la main, mode STATIC) : un cœur 5 × 5
de 100 molécules plus un filament de 8 cellules d'épaisseur 1 donne `extent = 20.24 ≥ 18` donc
`wraps = True`, alors que le rayon de giration de la composante vaut **2.63**, que `r80 = 2.83`,
et que le vecteur d'enroulement exact est **nul dans les deux directions**.

**Sur les données réelles** : l'indicateur s'est déclenché sur 2 relevés sur 90 (graine 5003,
`extent` 19.13 et 18.45, `Rg` 3.93 et 4.02) et 1 sur 90 (graine 5006, `extent` 18.65,
`Rg` 3.96). Le test exact appliqué aux 5 400 trames des six bras trouve **zéro** enroulement réel.
Les deux classements `BOUNDARY_ARTEFACT` sont des faux positifs.

## 9. Le second défaut : le seul critère sans tolérance

Le gate ORR01 comporte neuf conditions dures. Sept portent une tolérance explicite
(`FRAC_MIN = 0.95`, `RUN_MAX = 250`, `OCC_TOL`, `FREE_MIN`). `main_component_carries_the_mass`
exige `main_N_X ≥ 25` à **chacun** des ~90 relevés, sur une quantité stochastique.

**Démonstration constructive** (test T11) : un cœur de 48 molécules, **entièrement** contenu dans
`B(c, 2ℓ_X)` — fraction 1.000, `r80 = 2.24` — échoue parce qu'une seule colonne vide le sépare en
deux composantes de 24. 24 < 25.

**Sur les données réelles**, graine 5001 : 2 relevés en défaut sur 90, à `main_N_X = 18` et
`main_N_X = 24`. Le second manque le seuil **d'une molécule**, et le bras est classé
`ORGANISATION_LOST`.

## 10. Le contrefactuel, purement diagnostique

Si les deux critères spatiaux avaient été écrits comme les critères temporels du même gate :

| graine | classement ORR01 | classement corrigé | fraction des relevés au seuil | enroulements réels |
|---|---|---|---|---|
| 5001 | `ORGANISATION_LOST` | **`MAINTENANCE_ACHIEVED`** | 0.978 | 0 |
| 5003 | `BOUNDARY_ARTEFACT` | `ORGANISATION_LOST` | 0.911 | 0 |
| 5005 | `MATERIAL_COLLAPSE` | `MATERIAL_COLLAPSE` | 0.589 | 0 |
| 5006 | `BOUNDARY_ARTEFACT` | **`MAINTENANCE_ACHIEVED`** | 1.000 | 0 |

**Ceci n'est pas une confirmation et ne peut pas en être une** : c'est une reclassification post
hoc d'un gate gelé sur des données déjà vues. Elle ne modifie aucune disposition — 2 sur 6
n'atteint pas davantage le critère gelé de 5 sur 6. Elle établit seulement que la **cause**
invoquée par ORR01 n'est pas ce que ses propres données montrent.

Un troisième point, qui n'est pas un défaut mais un seuil : les graines 5002 et 5004, classées
`TRANSIENT_FORMATION`, avaient à `t = 1250` un `N_X` de 118 et 129 et satisfont le critère de
formation à `t = 1784` et `t = 1387`. Elles ont formé **tard**, pas « transitoirement », et aucun
de leurs neuf critères de persistance n'a jamais été évalué.

## 11. Verdict de la question A

Quatre axes déclarés avant toute mesure, appliqués aux six bras réparés :

```
A1 compacité relative (r80 sous le q01 de N1, à >= 95 % des trames)     5 bras sur 6
A2 persistance du cœur (cœur présent >= 95 % ET chaîne d'identité >= 95 %)  2 bras sur 6
A3 renouvellement matériel (>= 10 remplacements)                        6 bras sur 6  (35.8 – 37.1)
A4 aucun enroulement réel, jamais                                       6 bras sur 6
cœur présent à >= 90 % des trames                                       5 bras sur 6
```

Deux corrections du pré-plan, consignées en append-only avec leur direction :

* **D-2** — le membre **absolu** de A1 (`r80 ≤ L/6 = 6`) est insatisfiable par construction : le
  nul N3, sans paramètre libre, a pour médiane de `r80` exactement **6.00**. Un seuil que le cas
  idéal ne franchit qu'une fois sur deux ne peut être exigé à 95 % des trames. La règle littérale
  aurait rendu `ORR01_DELOCALIZATION_CONFIRMED`, étiquette que les mêmes données réfutent au
  quantile 0.000 contre deux nuls indépendants. **La correction va contre le sens de la règle
  littérale et est signalée comme telle.**
* **D-3** — le barreau de verdicts n'était pas monotone : le verdict le plus faible exigeait la
  même prémisse que les plus forts, si bien qu'aucune donnée ne pouvait l'atteindre. Corrigé en
  entier avant application. A2 n'est **pas** assoupli : il est atteint à 1.000 par deux bras.

Barreau corrigé, première ligne applicable, règle 4 :

```
LOCALISÉ ∧ CŒUR_PRÉSENT dans 5 bras (>= 4)                                          OUI
critère spatial du gate ORR01 jamais vrai dans ces bras (faux dans 3, jamais évalué dans 2)  OUI
démonstration constructive du défaut réussie (T10 et T11)                            OUI
```

```
VERDICT_QUESTION_A = ORR01_LOCALIZATION_GATE_INVALID
```

Réponse physique, à côté de l'étiquette : la population `X` est **localisée**, avec un cœur
présent à 91–98 % des trames dans cinq bras sur six, un halo de renouvellement portant 39–50 %
de la masse, aucun enroulement, et un renouvellement complet ~36 fois sur la fenêtre.

## 12. Portée de C-5

Les ensembles de graines et de bras sont des constantes d'un module **gelé avant le premier
démarrage de confirmation** — re-vérifié ici : 12 fichiers de code sur 12 et 6 documents sur 6
hachent toujours exactement comme `_freeze.json`. `run2.py` appelle le même `protocol.run_arm` et
ne réimplémente rien. La règle codée s'arrête strictement plus tôt que la règle écrite, et le
critère gelé de 5 sur 6 était déjà inatteignable ; aucun résultat positif ne pouvait être
fabriqué. La règle écrite n'avait **pas** été déclenchée, donc poursuivre était de la conformité,
pas un choix dépendant du résultat.

```
C5_SCOPE = C5_ADJUDICATIVELY_INVARIANT
```

Les graines ORR01 5001–5006 et 7001–7002 ne servent dans CSC01 qu'à l'autopsie brute de la
question A, et sont **interdites** en calibration, confirmation et contrôle.

## 13. Mécanisme spatial intrinsèque : recherche opérateur par opérateur

| opérateur | ce qu'il fait dépendre de la densité locale de `X` |
|---|---|
| `_diffuse` | la capacité libre de la **destination**, qui **bloque** l'entrée dans les cellules denses : une exclusion, donc une répulsion. Elle ne peut qu'étaler. |
| `_react` | rien : `p_X = min(1, k_X·n_X·n_Y)` est nul partout où `n_Y = 0`. Avec un organisateur, `X` naît en **une seule cellule**. |
| `_decay` | rien : `Binomial(n_X, µ_X)` par cellule, indépendant de la position et du voisinage. |
| `_exchange` | rien : `X` n'est pas dans le pool échangeable, l'opérateur ne transporte pas `X`. |

Aucun opérateur ne rend le transport, la naissance ou la mort d'une molécule `X` **attractivement**
dépendant de la densité locale de `X`. La seule structure localisante est : naissance en un point,
durée de vie finie. Et les mesures du §5 concordent avec cette prédiction sans paramètre libre.

```
INTRINSIC_LOCALIZATION_MECHANISM = ABSENT_IN_DECLARED_OPERATOR
```

## 14. Route

Route A indisponible : il n'existe pas de cœur cohésif défendable, seulement un cœur asservi à
la source. Route C requise en préalable : tous les classements spatiaux hérités sont contaminés
par D-4, D-5 et D-6, et le gate CSC01 est neuf — un mécanisme ne peut pas être comparé à une
référence qui n'existe pas encore sous le gate qui le jugera.

```
ROUTE = C_THEN_B
```

Une seule comparaison appariée sur des graines neuves. Le bras `C0`, chémostat inchangé, est
**simultanément** la mesure Route C sous le gate corrigé et le contrôle apparié de Route B. Les
bras `C0` ne sont jamais rapportés comme une confirmation de cohésion.

## 15. Le gate, source unique de vérité

`localization_gate.yaml` porte les seuils, les quatre axes, les douze classes et l'ordre de
classement. **Aucun nombre n'apparaît dans le code.** Deux implémentations le lisent : une en
flux, une en tableau.

**Axe 1 — compact ET cohésif.** `r80` sous le q01 de N1 à ≥ 0.95 des trames, **et** `r80` sous le
q05 de **N3b** à ≥ 0.80 des instants testés. Le second membre est le test de cohésion proprement
dit. Il alimente le nul avec le **taux de mort réalisé du bras lui-même**, pour qu'un mécanisme
qui se contente d'allonger la vie — et donc étale le nuage — ne puisse pas être pris pour de la
cohésion.

**Axe 2 — durable.** Jamais éteint, organisateur présent, `N_X ≥ 50` à ≥ 0.95 des pas, excursion
≤ 250 pas, et un cœur présent à ≥ 0.90 des trames, le cœur étant la boule de rayon **5.0 cellules
fixes** — `2·ℓ_X` de la référence, en valeur absolue, pour que les deux bras soient mesurés
identiquement.

**Axe 3 — vivant, non figé.** ≥ 10 remplacements complets, et capacité libre moyenne ≥ 1.0 dans
la boule du cœur : un amas tenu ensemble faute de place est un bloc coincé, pas une population.

**Axe 4 — pas un artefact.** Aucun enroulement **réel**, dérive d'occupation ≤ 0.05, capacité
libre à l'organisateur ≥ 0.5, et **aucune lecture de score** — audit AST statique de l'opérateur.

Classes nouvelles qui comptent : `LOCALISED_BUT_NOT_COHESIVE`, ce qu'est un halo asservi à sa
source, et `FROZEN_AGGREGATE`, ce qu'est un amas sans renouvellement ou sans place.

## 16. Sélection du mécanisme, déterministe

Cinq candidats, minimisation lexicographique sur des propriétés **structurelles** seulement, sans
aucune mesure ni résultat :

| | S1 params | S2 opérateurs | S3 ne touche pas au transport | S4 ne crée pas de matière hors source | S5 préserve les contrôles | S6 analyse exacte à une cellule |
|---|---|---|---|---|---|---|
| **C3 décroissance protégée par les voisins** | 1 | 1 | ✓ | ✓ | ✓ | ✓ |
| C2 autocatalyse locale | 1 | 1 | ✓ | ✗ | ✗ | ✓ |
| C1 transport adhésif | 1 | 1 | ✗ | ✓ | ✓ | ✓ |
| C4 confinement par matrice | 1 | 1 | ✗ | ✓ | ✓ | ✓ |

```
gagnant = C3_NEIGHBOUR_PROTECTED_DECAY, unique
loi     = µ_X(cellule) = µ_X · (1 − λ) ** m(cellule),  m = nombre de X dans les 4 cellules voisines
lecture physique = stabilisation mutuelle : une molécule entourée des siennes est dégradée plus
                   lentement. Rien n'est créé ; une mort est seulement rendue moins probable.
```

L'opérateur lit une cellule et ses quatre voisines, et rien d'autre : la contrainte de localité
MINCORE est préservée exactement. Aucune réduction globale, aucun score.

## 17. Calibration passive de λ

Assay passif sur ses propres graines 6301–6304, qui ne lit **qu'une** statistique structurelle de
l'état de référence — la médiane, par molécule, du nombre de voisins `X` à l'intérieur du cœur —
et rien d'autre. Aucun verdict de gate, aucun `PASS`, aucune statistique de compacité n'entre.
La cible et le facteur 1/2 étaient déclarés avant l'exécution.

```
m* = 5   (médianes par bras : 5.00, 4.50, 5.00, 5.00 ; médiane groupée 5.000)
λ  = 1 − 2^(−1/m*) = 0.129449
µ_eff(m*) = 0.002000 = µ_X / 2 exactement       ℓ_X : 2.5000 isolée → 3.5355 à m*
STATUS = CALIBRATED
```

## 18. Audit adverse, dix-huit cas

Deux comptent plus que les autres. **A08** soumet au gate un halo compact, durable, renouvelé et
**asservi à sa source**, et exige `LOCALISED_BUT_NOT_COHESIVE` : le gate ne doit pas appeler
cohésion ce que la question A vient de disqualifier. **A09** lui soumet un nuage réellement
compact et exige `COHESION_ACHIEVED` : le gate ne doit pas être infranchissable. **A11** exige
l'accord champ par champ des deux implémentations sur 24 traces aléatoires. **A12** exige que
déplacer un seuil dans le yaml déplace le verdict, sur les quatre axes.

L'audit a trouvé un vrai défaut **avant** le gel : le gate en flux comptait les trames spatiales
avec son compteur de fenêtre, qui continue d'en admettre après la fermeture de la fenêtre. Corrigé
sur la borne de l'implémentation en tableau. Un second point a réordonné le classement pour que
`DELOCALISED` soit atteignable.

```
PROTOCOL_ADVERSARIAL_AUDIT = PASS   (18 / 18, plus l'audit AST de l'opérateur)
GATE_SINGLE_SOURCE_OF_TRUTH = PASS
ONLINE_POSTHOC_SYNTHETIC_AGREEMENT = PASS
```

## 19. Gel

```
METHODS_CORE_HASH  5570a5f6dbad488e67d4917f75efcf9ce1183c8861651655b72ad9c960a1f20f
gate spec sha256   4bf1a2e5f5e397dcff917b2d77ec9942bc9922413443c895d4d5bf7236d66a5e
gelé avant         le premier démarrage de confirmation
démarrages avant   calibration 4, confirmation 0, contrôle 0
17 fichiers de code et 10 documents gelés ; re-vérifiés en fin de mission : 17 / 17 identiques
```

## 20. Plan confirmatoire

Six paires sur graines neuves 6101–6106, plus quatre contrôles. **Les deux implémentations du
gate s'accordent sur les seize bras.**

| graine | C0 chémostat inchangé | C3 mécanisme |
|---|---|---|
| 6101 | `LOCALISED_BUT_NOT_COHESIVE` | `TRANSIENT_FORMATION` |
| 6102 | `LOCALISED_BUT_NOT_COHESIVE` | `TRANSIENT_FORMATION` |
| 6103 | `TRANSIENT_FORMATION` | `TRANSIENT_FORMATION` |
| 6104 | `LOCALISED_BUT_NOT_COHESIVE` | `MATERIAL_COLLAPSE` |
| 6105 | `LOCALISED_BUT_NOT_COHESIVE` | `TRANSIENT_FORMATION` |
| 6106 | `LOCALISED_BUT_NOT_COHESIVE` | `MATERIAL_COLLAPSE` |

```
C3 COHESION_ACHIEVED        0 sur 6        critère gelé : 5 sur 6      succès = NON
C0 non COHESION_ACHIEVED    6 sur 6
```

Contrôles : `NO_ORGANISER` → `NO_FORMATION` sur les deux graines, `N_X` maximal 0, comme prédit —
le mécanisme ne peut rien créer. `LAMBDA_ZERO` → `LOCALISED_BUT_NOT_COHESIVE` et
`TRANSIENT_FORMATION`, c'est-à-dire le comportement de la référence : λ est bien la seule cause
de toute différence.

## 21. Ce que le mécanisme fait réellement

Ce n'est pas un résultat nul.

```
taux de mort réalisé          C0 0.004008   →   C3 0.002497      (moitié, comme conçu)
N_X moyen sur la fenêtre      C0 115 – 128  →   C3 172 – 180
statistique de cohésion       C0 0.074      →   C3 0.519
différence appariée           +0.444 en moyenne, positive dans 6 graines sur 6
                              test des signes bilatéral exact p = 0.031   (DESCRIPTIF)
fraction de trames avec cœur  C0 0.941      →   C3 0.676   (seuil 0.90)
```

Le mécanisme **produit** de la cohésion mesurable : le nuage devient plus compact que son propre
nul sans interaction, dans les six graines. Mais il la paie deux fois.

**Premièrement**, des molécules qui vivent plus longtemps diffusent plus loin. Le nuage grossit,
et à rayon de cœur fixe — celui de la référence, 5.0 cellules — la fraction de trames possédant un
cœur tombe sous le seuil de durabilité. La cohésion gagnée en compacité relative est perdue en
étalement absolu.

**Deuxièmement**, la protection est auto-renforçante **dans les deux sens**. Un nuage qui
s'amincit se protège moins, ce qui l'amincit davantage. Deux bras sur six se sont éteints ainsi,
avec des excursions de 3 237 et 6 723 pas sous le seuil. Le mécanisme introduit une bistabilité
que la référence n'a pas.

Le test des signes est **descriptif** et n'est pas le critère de décision : le critère gelé est
5 bras sur 6 `COHESION_ACHIEVED`, et il n'est pas atteint.

## 22. Bornes de temps héritées

`C3` ne modifie **pas** le transport. `D_X`, `D_Y` et le temps de première séparation
`τ_sep = Δ²/(8 D_Y)` sont inchangés, ainsi que la loi de naissance de `Y` et donc le hasard
cumulé. **La fenêtre minoritaire MTW01 n'est pas invalidée par ce mécanisme**, et la disposition
`COHESION_CORRECTED_TIMESCALE_REDERIVATION_ONLY` ne s'applique pas — la raison est structurelle et
non un jugement : le mécanisme touche `_decay`, pas `_diffuse`.

Ce qui change et doit être consigné : `ℓ_X = √(D_X/µ_X)` devient **dépendante de l'état**, valant
2.500 pour une molécule isolée et 3.536 au voisinage médian. Tout énoncé utilisant un `ℓ_X`
unique doit être re-dérivé sous ce mécanisme. Aucun énoncé de ce type n'est produit ici.

## 23. Ce qui n'a pas été testé, et ne doit pas être lu entre les lignes

Rien dans cette mission ne teste la reproduction, l'hérédité, l'évolution, l'individualité, la
propriété matérielle ou H3. Aucune molécule n'est suivie individuellement ; le « renouvellement »
est un flux compté, pas une lignée. Aucune structure appelée ici cœur, halo ou composante n'est
une membrane, une cellule, ni un individu. La population est nommée `X_POPULATION`, `X_CLOUD`,
`MAIN_COMPONENT` ou `SPATIAL_CORE`, jamais `BODY`. Aucun résultat de cette mission n'est fusionné
avec MINCORE ni MTW01 : le LawSpec diffère.

```
H3_STATUS = NOT_TESTED          REPRODUCTION_STATUS = NOT_TESTED
```

## 24. Éligibilité scientifique suivante

Le prochain pas éligible n'est pas un mécanisme de plus. Les mesures désignent une seule question
bien posée : **peut-on obtenir de la cohésion sans allonger la durée de vie ?** `C3` échoue parce
que sa cohésion et son étalement viennent du même changement. Un mécanisme qui agit sur le
transport à durée de vie constante — le candidat `C1`, écarté ici uniquement parce qu'il touche
au transport — sépare les deux effets. Il exigerait alors, par la règle §20, une re-dérivation
explicite des bornes de première séparation avant tout énoncé de fenêtre.

Deuxième piste, moins coûteuse : le seuil de durabilité de l'axe 2 est mesuré à un rayon de cœur
**absolu**, choisi pour que les deux bras soient comparables. C'était le bon choix pour cette
comparaison, et c'est aussi ce qui a fait échouer `C3` sur l'axe 2. Une mission ultérieure peut
légitimement demander si un cœur qui grandit avec la population reste un cœur — mais cette
question doit être **gelée d'avance**, pas décidée après avoir vu ces résultats.

## 25. Fichiers et reproduction

```
branche          codex/chemostat-spatial-cohesion-01, depuis d89c221, 11 commits séparés
code             CSC01/code/    17 fichiers gelés, hachés dans _freeze.json
données brutes   CSC01/raw/     16 bras, série complète 29 champs x 11 000 pas + champs finaux
sorties          CSC01/out/     _provenance, _calibration, _audit, _freeze, _results, _analysis,
                                _stage_a, _decisions, _autopsy_repaired, _null_n3b,
                                _ledger_consolidated, csc01_cohesion.png
documents        CSC01_AUTOPSY_PREPLAN.md, CSC01_APPEND_ONLY_CORRECTIONS.md,
                 CSC01_INHERITANCE_NOTE.md, CSC01_FINAL_REPORT.md
livraison        CSC01/delivery/  scripts, sommes, et les parts de l'artefact auto-suffisant
```

---

```
DISPOSITION
INHERITED_SPATIAL_FAILURE_REATTRIBUTED__COHESION_NOT_QUALIFIED
composée de deux verdicts atomiques, tous deux nommés dans le mandat :
  question A : ORR01_LOCALIZATION_GATE_INVALID
  question B : mécanisme minimal sélectionné, calibré passivement, gelé et exécuté ;
               0 bras sur 6 COHESION_ACHIEVED contre un critère gelé de 5 sur 6.

VERDICT_QUESTION_A
ORR01_LOCALIZATION_GATE_INVALID

INHERITED_OCCUPANCY_RATCHET_REPAIR
QUALIFIED

INHERITED_SPATIAL_LOCALIZATION
La population X est localisée, durable et traversée par le renouvellement. Sa localisation est
entièrement expliquée, sans paramètre libre, par une source ponctuelle errante et une durée de
vie finie. Il n'y a pas de cohésion à expliquer dans les données héritées, et il n'y avait pas
non plus de délocalisation à corriger.

INTRINSIC_LOCALIZATION_MECHANISM
ABSENT_IN_DECLARED_OPERATOR

C5_SCOPE
C5_ADJUDICATIVELY_INVARIANT

ROUTE
C_THEN_B

MECHANISM_SELECTED
C3_NEIGHBOUR_PROTECTED_DECAY, unique sous la règle lexicographique, lambda = 0.129449 calibré
passivement sur m* = 5.

COHESION_RESULT
0 de 6 COHESION_ACHIEVED. La statistique de cohésion passe de 0.074 a 0.519, plus haute dans 6
graines sur 6, mais la duree de vie allongee etale le nuage et la fraction de trames avec un
coeur tombe de 0.941 a 0.676, sous le seuil de durabilite. Deux bras sur six se sont eteints par
la bistabilite que le mecanisme introduit.

TIMESCALE_IMPACT
Aucun. C3 ne touche pas au transport, donc D_X, D_Y et tau_sep sont inchanges et la fenetre
MTW01 n'est pas invalidee. COHESION_CORRECTED_TIMESCALE_REDERIVATION_ONLY ne s'applique pas.
ell_X devient dependante de l'etat, 2.500 isolee et 3.536 au voisinage median ; aucun enonce
utilisant un ell_X unique n'est produit sous ce mecanisme.

GATE_SINGLE_SOURCE_OF_TRUTH
PASS

ONLINE_POSTHOC_SYNTHETIC_AGREEMENT
PASS

PROTOCOL_ADVERSARIAL_AUDIT
PASS

H3_STATUS
NOT_TESTED

REPRODUCTION_STATUS
NOT_TESTED

SCIENTIFIC_RUNS_USED
20 : calibration 4 de 8, confirmation 12 de 16, controle 4 de 12, cost probe 0 de 2, invalides 0.
Les rejeux bit-exacts d'arcs ORR01 deja consommes sont comptes a part, 6, dans une classe
declaree non scientifique. Le harnais synthetique n'est pas un demarrage : 7 800 pas bornes et
aveugles au score sur un plafond de 20 000, 30 tests, 0 demarrage consomme. Consolide sur quatre
processus dans _ledger_consolidated.json.

PROTOCOL_VIOLATIONS
Aucune. Quatre corrections append-only sont consignees, dont deux portent sur le pre-plan de
cette mission (D-2 seuil insatisfiable par construction, D-3 barreau non monotone) et deux sur
le gate herite d'ORR01 (D-4 substitut d'etendue, D-5 critere sans tolerance), chacune avec sa
demonstration et la direction de son effet. Un defaut du gate CSC01 a ete trouve par l'audit
adverse AVANT le gel et corrige avant le premier demarrage de confirmation.

PROVENANCE_STATUS
SELF_CONTAINED_SPLIT_DELIVERY_PASS

NEXT_SCIENTIFIC_ELIGIBILITY
Un mecanisme de cohesion qui agit sur le transport a duree de vie constante, pour separer la
compacite de l'etalement que C3 confond. Il exige, par la regle du mandat, une re-derivation
explicite des bornes de premiere separation avant tout enonce de fenetre.

TOMMY_ACTION_REQUIRED
NONE
```
