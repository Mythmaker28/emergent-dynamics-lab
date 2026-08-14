# CSC01_APPEND_ONLY_CORRECTIONS

Append-only. Aucun artefact hérité et aucun octet gelé de cette mission n'est édité. Chaque entrée
est datée, rattachée au fichier et au commit qu'elle concerne, et porte sa raison et la
**direction** de son effet.

---

## D-1 — 2026-08-14 — l'artefact auto-suffisant est livré scindé, sous son nom d'origine

**Concerne** `/home/claude/ORR01_offline_repo.tar.gz` (38 826 938 octets, sha256
`f06e8b78…67f95`), laissé **inchangé**.

L'artefact dépassait la limite de livraison de 30 Mo. `zstd` est absent de cet environnement et
`xz -9e` ne gagne que 0.35 % (38 952 960 → 38 817 244 octets) parce que la charge utile est déjà
constituée de packfiles git compressés. L'artefact a donc été **scindé** plutôt que recompressé,
sur une copie, la copie étant ensuite supprimée.

`§3` parlait des parts « de l'artefact CSC01 ». Les parts livrées portent le nom de l'artefact
**ORR01**, parce que c'est lui qui était indélivrable et que c'est lui que `§3` exige de rendre
délivrable. L'artefact CSC01 sera scindé selon le même schéma en fin de mission.

```
PROVENANCE_STATUS = SELF_CONTAINED_SPLIT_DELIVERY_PASS
parts 3, max 19 000 000 octets, toutes sous la limite de 29 Mo
vérification exécutée : sommes des parts OK, sha256 de l'ensemble reassemblé OK, extraction OK,
clone hors réseau (unshare -rn, contrôle DNS et TCP négatifs à l'intérieur, positifs à
l'extérieur) OK, HEAD OK, arbre OK, 1292 fichiers, 0 objet manquant, fsck propre,
tests ORR01 rejoués depuis l'état reconstruit : ALL_PASS = True
```

---

## D-2 — 2026-08-14 — le membre absolu de l'axe A1 du pré-plan est insatisfiable par construction

**Concerne** `CSC01_AUTOPSY_PREPLAN.md` §5, axe A1, tel que déclaré avant toute mesure.

A1 était une **conjonction** de deux conditions : `r80 ≤ q01(r80 | N1)` (compacité **relative**,
face au nul d'absence totale d'organisation) et `r80 ≤ L/6 = 6` (compacité **absolue**), exigées
à ≥ 95 % des trames.

Le second membre est insatisfiable par construction à ce point de conception, et la démonstration
est **sans paramètre libre** : le nul N3 est le profil stationnaire exact d'une source ponctuelle
avec mort au taux `µ_X`, c'est-à-dire la population la plus compacte que ce modèle puisse produire
**sans aucune interaction entre molécules**. Sa médiane de `r80` vaut **6.00**, soit exactement
`L/6`. Un seuil que le cas idéal ne franchit qu'une fois sur deux ne peut pas être exigé à 95 %
des trames. (Test T12 : le profil N3 reproduit son propre moment analytique
`⟨r²⟩ = 2a(1−µ)/µ = 24.90` à 24.63 sur le tore, et `ℓ_X = 2.5` exactement.)

**Mesures.** Membre relatif satisfait à 1.000 des trames dans 5 bras sur 6 (0.708 dans le bras
5005, qui s'éteint). Membre absolu satisfait à 0.043–0.126 des trames dans les 6 bras.

**Direction de l'effet.** La règle littérale déclenche la règle 2 du barreau et rendrait
`ORR01_DELOCALIZATION_CONFIRMED` — une étiquette que les mêmes données réfutent avec une force
écrasante : la quantile observée de `r80` dans le nul N1 vaut **0.000** dans les six bras, et
0.000 également dans le nul N4. La correction va donc **contre** le sens de la règle littérale ;
elle est signalée comme telle et le verdict littéral est rapporté à côté du verdict corrigé.

```
A1 corrigé = son seul membre relatif (r80 ≤ q01(r80 | N1) à ≥ 95 % des trames)
verdict sous la règle littérale  = ORR01_DELOCALIZATION_CONFIRMED   (réfuté par ses propres nuls)
```

---

## D-3 — 2026-08-14 — le barreau de verdicts du pré-plan n'est pas monotone

**Concerne** `CSC01_AUTOPSY_PREPLAN.md` §5, règles 3 à 5.

La règle 5 délivre `ORR01_PARTIAL_LOCALIZED_CORE` — l'affirmation **la plus faible** du barreau —
mais exige la **même** prémisse `A1 ∧ A2` que les règles 3 et 4. Or A2 est l'axe fort
(persistance du cœur *et* chaîne d'identité ininterrompue ≥ 0.95). Aucun schéma de données ne peut
donc atteindre le verdict faible tant que l'axe fort échoue : tout tombe en `UNRESOLVED`. Un
barreau de verdicts doit être monotone en force de l'affirmation.

**Correction, énoncée en entier avant application.** Par bras :

* `LOCALISÉ` := A1 (membre relatif, D-2) ∧ A4 (aucun enroulement réel, jamais)
* `CŒUR_PRÉSENT` := un cœur existe (≥ 50 % de la masse `X` dans `B(c, 2ℓ_X)`) à ≥ 0.90 des trames
* `CŒUR_CONTINU` := A2 tel que déclaré (cœur présent ≥ 0.95 **et** chaîne ininterrompue ≥ 0.95)

Barreau corrigé, première ligne applicable :

1. rejeu non exact pour ≥ 2 bras → `ORR01_RAW_LOCALIZATION_UNRESOLVED`
2. `LOCALISÉ` dans ≤ 2 bras → `ORR01_DELOCALIZATION_CONFIRMED`
3. `LOCALISÉ ∧ CŒUR_CONTINU` dans ≥ 5 bras **et** critère spatial du gate ORR01 vrai dans ceux-là
   → `ORR01_RAW_LOCALIZATION_CONFIRMED`
4. `LOCALISÉ ∧ CŒUR_PRÉSENT` dans ≥ 4 bras, critère spatial du gate ORR01 jamais vrai dans
   ceux-là, **et** démonstration constructive du défaut du gate réussie
   → `ORR01_LOCALIZATION_GATE_INVALID`
5. `LOCALISÉ ∧ CŒUR_PRÉSENT` dans ≥ 4 bras → `ORR01_PARTIAL_LOCALIZED_CORE`
6. sinon → `ORR01_RAW_LOCALIZATION_UNRESOLVED`

A2 n'est **pas** assoupli : il est atteint à 1.000 par les bras 5004 et 5006, donc il est
satisfaisable et il reste tel quel. Seule la structure du barreau est corrigée.

```
axes conservés tels que déclarés = A2, A3, A4
axe corrigé = A1 (D-2)      structure corrigée = le barreau (D-3)
```

---

## D-4 — 2026-08-14 — l'indicateur `wraps` d'ORR01 est un substitut d'étendue, pas un test d'enroulement

**Concerne** `ORR01/code/observe.py`, `component_report`, sous
`METHODS_CORE_HASH = 1cfdb192…b949a84d`. Non modifié.

ORR01 déclare `wraps = (extent >= L*0.5)` avec `extent = 2·max(dy, dx) + 1` mesuré depuis la
moyenne angulaire. C'est une mesure de l'**étendue** de la composante, pas de son **enroulement**.
Une composante compacte à laquelle un unique filament d'une cellule de large est attaché déclenche
l'indicateur sans faire le tour du tore.

**Démonstration constructive** (test T10, état construit à la main, mode STATIC, aucun démarrage
consommé) : un cœur 5 × 5 de 100 molécules plus un filament de 8 cellules d'épaisseur 1 donne
`extent = 20.24 ≥ 18` donc `wraps = True`, alors que le rayon de giration de la composante vaut
**2.63**, que `r80 = 2.83`, et que le test exact d'enroulement — relèvement dans le revêtement
universel — renvoie un vecteur d'enroulement **nul dans les deux directions**.

**Effet mesuré sur les données réelles.** Sur les quatre bras réparés disposant d'une fenêtre,
l'indicateur `wraps` d'ORR01 s'est déclenché sur **2 relevés sur 90** (graine 5003, pas 2700 et
2800 ; `extent` 19.13 et 18.45, `Rg` 3.93 et 4.02) et sur **1 relevé sur 90** (graine 5006, pas
5100 ; `extent` 18.65, `Rg` 3.96). Le test exact d'enroulement, appliqué aux 900 trames de la
fenêtre de chacun des six bras, renvoie **zéro** enroulement réel, dans les deux directions,
partout. Les deux classements `BOUNDARY_ARTEFACT` d'ORR01 sont donc des **faux positifs**.

```
défaut = TEST_DE_BORD_REMPLACÉ_PAR_UN_SUBSTITUT_D_ÉTENDUE
faux positifs mesurés = 2 bras sur 4 évaluables       enroulements réels mesurés = 0 partout
octets gelés édités = AUCUN
```

---

## D-5 — 2026-08-14 — le critère `main_component_carries_the_mass` est le seul du gate sans tolérance

**Concerne** `ORR01/code/gates.py`, même hash gelé. Non modifié.

Le gate ORR01 comporte neuf conditions dures. Sept d'entre elles portent une tolérance explicite
(`fraction_ok` à `FRAC_MIN = 0.95`, `excursion_ok` à `RUN_MAX = 250`, `occupancy_stable` à
`OCC_TOL`, `free_capacity_not_collapsed` à `FREE_MIN`, …). Le critère
`main_component_carries_the_mass` exige `main_N_X ≥ N_KEEP/2 = 25` à **chacun** des ~90 relevés,
sans aucune tolérance, sur une quantité qui fluctue de façon stochastique.

**Démonstration constructive** (test T11) : un cœur de 48 molécules, **entièrement** contenu dans
`B(c, 2ℓ_X)` (fraction 1.000, `r80 = 2.24`), échoue au critère parce qu'une seule colonne vide le
sépare en deux composantes de 24. 24 < 25.

**Effet mesuré sur les données réelles.** Graine 5001 : **2 relevés en défaut sur 90**, à
`main_N_X = 18` et `main_N_X = 24` — le second manque le seuil d'**une molécule** — et le bras est
classé `ORGANISATION_LOST`. Graine 5006 : **0 relevé en défaut sur 90**, le bras est classé
`BOUNDARY_ARTEFACT` par le seul défaut D-4.

**Contrefactuel, purement diagnostique.** Si les deux critères spatiaux avaient été écrits comme
les critères temporels du même gate — enroulement testé exactement, masse principale exigée à une
fraction `FRAC_MIN` des relevés — alors, sur les quatre bras disposant d'une fenêtre :

| graine | classement ORR01 | classement corrigé | fraction des relevés au-dessus du seuil | enroulements réels |
|---|---|---|---|---|
| 5001 | `ORGANISATION_LOST` | **`MAINTENANCE_ACHIEVED`** | 0.978 | 0 |
| 5003 | `BOUNDARY_ARTEFACT` | `ORGANISATION_LOST` | 0.911 | 0 |
| 5005 | `MATERIAL_COLLAPSE` | `MATERIAL_COLLAPSE` | 0.589 | 0 |
| 5006 | `BOUNDARY_ARTEFACT` | **`MAINTENANCE_ACHIEVED`** | 1.000 | 0 |

**Ce contrefactuel n'est pas une confirmation et ne peut pas en être une.** C'est une
reclassification post hoc d'un gate gelé, appliquée à des données déjà vues. Elle ne modifie
aucune disposition : le critère de succès gelé d'ORR01 était 5 bras sur 6, et 2 sur 6 ne
l'atteint pas davantage. Ce qu'elle établit est que la **cause** invoquée par ORR01 — la
délocalisation du nuage — n'est pas ce que ses propres données montrent.

```
défaut = CRITÈRE_TOUT_OU_RIEN_DANS_UN_GATE_À_TOLÉRANCES
direction = le défaut ne peut que produire des ÉCHECS, jamais des succès : il est conservateur
            pour ORR01 et ne peut avoir gonflé aucun résultat positif
disposition ORR01 révisée = NON     octets gelés édités = AUCUN
statut du contrefactuel = DIAGNOSTIC_ONLY, jamais confirmatoire
```

---

## D-6 — 2026-08-14 — deux bras réparés ont formé tardivement, pas « transitoirement »

**Concerne** `ORR01/code/protocol.py`, `T_FORM_MAX = 1250`. Non modifié. **Ce n'est pas un
défaut** : c'est un seuil, déclaré d'avance et appliqué correctement. Il est consigné parce qu'il
change la lecture de deux classements.

Le gate de formation exige `N_X ≥ 30` **et** `u ≥ 3.0` pendant **50 pas consécutifs**, avant
`t = 1250`. Les graines 5002 et 5004, classées `TRANSIENT_FORMATION`, avaient à `t = 1250` un
`N_X` de **118** et **129**, et un maximum de 160 et 159 sur la trajectoire. Elles satisfont le
critère de formation à `t = 1784` et `t = 1387`, soit **534** et **137** pas après l'échéance.

`TRANSIENT_FORMATION` s'y lit donc « a formé tard », et non « n'a pas formé ». Aucune fenêtre de
maintien n'ayant été ouverte pour ces deux bras, **aucun** de leurs neuf critères de persistance
n'a jamais été évalué par ORR01.

```
effet = 2 bras sur 6 n'ont jamais été évalués sur la persistance
direction = conservateur pour ORR01
```
