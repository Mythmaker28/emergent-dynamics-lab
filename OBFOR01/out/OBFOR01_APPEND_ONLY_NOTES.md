# OBFOR01 — notes append-only

Fichier **append-only**. Aucune entrée n'est modifiée après écriture, et aucun artefact gelé
d'OBTR01, d'OBDCA01, d'OBDI02, d'OBTC02 ou de MTW01 n'est touché : les entrées ci-dessous
*lisent* et *ajoutent*.

---

## B-1 — 2026-08-15 — `EMPTY_WINDOW` n'est pas `WINDOW_MECHANISM_ABSENT`

**Concerne** l'interprétation de la disposition héritée `ORIGINAL_WINDOW_NOT_PORTABLE`. Rien
dans OBTR01 §13–§14 n'est modifié ; cette note en fixe la lecture pour éviter une confusion qui
serait facile à commettre et coûteuse à corriger plus tard.

### Les deux énoncés qu'il faut séparer

**`EMPTY_WINDOW`** dirait : le mécanisme existe, ses deux bornes sont bien définies, et
l'intervalle admissible est vide — la borne haute est passée sous la borne basse. C'est un
énoncé *quantitatif*, réfutable en déplaçant un paramètre, et c'est ce que MTW01 testait à son
propre point gelé, où il obtenait `emptiness_lhs = 189,82 > 1`.

**`WINDOW_MECHANISM_ABSENT`** dit tout autre chose : le canal auquel `R_Y` se rapportait
n'existe pas dans le LawSpec qualifié. Ce n'est pas une borne qui a bougé ; c'est le référent
qui a disparu.

### Ce qui est vrai au point qualifié, en quatre points

1. **L'intervalle historique abstrait peut être numériquement non vide.** En substituant les
   valeurs du point qualifié dans les anciennes formules, OBTR01 obtient l'intervalle ouvert
   `(0 ; 1,787×10⁻⁴)`. Il est non vide. Ce fait, isolé, n'est pas un résultat.
2. **La bande atteignable est `{0}`.** `k_Y = 0` exactement, donc `R_Y = k_Y·Q = 0` pour toute
   valeur de `Q`, y compris `Q_max = 28`. L'ensemble des taux que le système peut réaliser est
   le singleton `{0}`.
3. **La borne basse est stricte.** L'inégalité historique est `a_Y < R_Y`, et non `a_Y ≤ R_Y`.
   Avec `µ_Y = 0` elle se lit `0 < 0`, qui est fausse. L'intersection entre l'intervalle et la
   bande atteignable est donc **vide**.
4. **Substituer zéro ne restaure pas le mécanisme.** Écrire `R_Y = 0` dans une formule qui
   contraint un taux de naissance d'organisateur ne fabrique pas un taux de naissance
   d'organisateur nul : cela constate qu'il n'y a pas de naissance d'organisateur du tout. Les
   deux bornes hautes deviennent alors *vacuement* satisfaites, et une satisfaction vacuité
   n'est pas une condition franchie.

### Conséquence sur les égalités temporelles

Au point qualifié, les anciennes égalités entre échelles de temps ne sont plus des coïncidences
physiques à vérifier : ce sont des **identités algébriques**. `ℓ_rel` est *défini* comme
`√(D_rel/µ_X)`, donc `ℓ_rel²/D_rel = 1/µ_X` identiquement ; `core_R = 2ℓ_X` exactement, donc les
deux premiers passages continus valent tous deux `1/(2µ_X)` ; et sept des huit échelles sont des
multiples rationnels fixes de `1/µ_X`. Une expérience qui les observerait « en accord » n'aurait
rien mesuré, puisque le désaccord est arithmétiquement impossible.

### Statuts fixés par cette note

```
ORIGINAL_WINDOW_STATUS          = ORIGINAL_WINDOW_NOT_PORTABLE
WHY                             = WINDOW_MECHANISM_ABSENT, NOT EMPTY_WINDOW
ABSTRACT_INTERVAL               = (0 ; 1.787e-4), non vide, sans référent
REACHABLE_BAND                  = {0}
LOWER_BOUND                     = STRICT, donc l'intersection est vide
TEMPORAL_EQUALITIES             = ALGEBRAIC_IDENTITIES_AT_THE_QUALIFIED_POINT
TIMESCALE_SEPARATION_EXPERIMENT = NOT_ELIGIBLE_AT_THE_CURRENT_POINT
```

**Aucune expérience confirmatoire de séparation des temps n'est éligible au point actuel.** Ce
n'est pas un manque de puissance : c'est qu'il n'existe qu'une seule échelle à séparer.

---

## B-2 — 2026-08-15 — correction d'un décompte hérité : « 20 fichiers sur 20 »

**Concerne** la phrase d'OBTR01 §4 selon laquelle le manifeste MTW01 vérifie « 20 fichiers sur
20 ». Reproduite plutôt que recopiée, cette formule recouvre en réalité :

- **19 fichiers** effectivement portés dans la livraison, sous `OBTR01/verify/mtw01/`, tous
  re-vérifiés ici depuis l'arbre livré ;
- **1 entrée supplémentaire**, `MTW01_gen2_branch.bundle` (sha256 `22f6bbfa…`), vérifiée au
  moment de la récupération mais **délibérément non copiée** dans le dépôt : elle contient les
  mêmes 19 fichiers sous forme d'objets git, et la porter doublerait l'artefact sans rien
  ajouter à la vérifiabilité.

Le décompte est donc **corrigé et non abaissé** : `19/19` en arbre plus `1/1` hors arbre. La
livraison reste auto-suffisante sans le paquet. Aucune conclusion d'OBTR01 ne dépend de ce
point ; il est consigné parce que le mandat exige que rien ne soit recopié sans reproduction.

```
MTW01_MANIFEST_ENTRIES     = 20
MTW01_IN_TREE_VERIFIED     = 19 / 19
MTW01_OUT_OF_TREE_VERIFIED = 1 / 1  (le paquet)
DELIVERY_SELF_CONTAINED    = TRUE sans le paquet
```

---
