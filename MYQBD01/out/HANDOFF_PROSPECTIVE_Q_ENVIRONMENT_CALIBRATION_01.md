# ISING LIFE LAB — HANDOFF
## PROSPECTIVE-Q-ENVIRONMENT-CALIBRATION-01 (PQEC01)
## Calibrer prospectivement l'environnement `Q` résolu en position, pour un test `Y` ultérieur

> Produit par `MINORITY-Y-Q-BOUND-DERIVATION-01`, après une relecture adversariale indépendante
> (verdict `CANDIDATE_DISPOSITION_SUPPORTED`, 0 défaut porteur) et l'unique round de réparation
> autorisé. **Ne pas exécuter dans la session MYQBD01.** Seule éligibilité active suivante.

```
OWNER                 = Tommy
REPOSITORY            = Mythmaker28/emergent-dynamics-lab
PARENT_PROGRAM        = MINORITY-Y-Q-BOUND-DERIVATION-01
PARENT_DISPOSITION    = EXISTING_Q_DATA_INSUFFICIENT__PROSPECTIVE_Q_CALIBRATION_REQUIRED
SHORT_NAME            = PQEC01
ARCHITECTURE_CHANGE   = forbidden
X_LAWSPEC_BASELINE    = UNCHANGED
TOMMY_ACTION_REQUIRED = NONE
```

## 0. Verser ce texte dans le dépôt avant toute autre action.

---

## 1. Le déficit d'information exact que PQEC01 doit combler

MYQBD01 a établi, **dérivé sur les 28 archives** (et non sur une seule, comme le faisait la
version pré-sceau) :

| drapeau | valeur | conséquence |
|---|---|---|
| `SOURCE_TRAJECTORY_POSITION_RESOLVED` | **vrai** | `source_substep_ledger` donne la trajectoire exacte de l'organisateur (4 colonnes de coordonnées sur 6) |
| `FULL_LATTICE_ENVIRONMENT_PER_STEP` | **faux** | aucun tableau `(T,L,L)` ; les `frames` décodent en scalaires ; l'archive est ~49× trop petite |
| `HISTORICAL_DESCENDANT_TRAJECTORY_EXISTS` | **faux** | `kY = 0` dans les 28 bras ⇒ `N_Y ≡ 1` aux 308 000 pas ⇒ aucun descendant n'a jamais existé |
| `DESCENDANT_Q_POSITION_RECONSTRUCTIBLE` | **faux** | conséquence calculée des trois lignes ci-dessus |

**Savoir où est la source ne donne pas l'environnement ailleurs.** `Q_POSITION(x,t)` exige
`(nX, nSY, free)` à une cellule *différente*, à chaque pas. C'est un **registre manquant**, pas une
impossibilité physique : l'architecture sait parfaitement l'enregistrer, personne ne le lui a
demandé.

> **La re-simulation prospective n'est pas une récupération rétrospective.** Le moteur est
> déterministe étant donné `(graine, spec)` : rejouer les graines parentes `9300000`–`9300027`
> avec un observateur ajouté reproduirait le champ manquant. C'est un **run**. La raison pour
> laquelle PQEC01 a besoin de mondes neufs est la **prospectivité** et l'**information de
> descendant manquante** — jamais une indisponibilité de l'architecture.

---

## 2. Question scientifique

Une calibration **gelée à l'avance et ensemencée indépendamment** peut-elle caractériser
l'environnement spatial aligné sur l'événement que rencontrent **une puis deux** lignées `Y`
mobiles, assez bien pour dériver une région candidate exécutable `(kY, muY)` destinée à un test de
confirmation **ultérieur et disjoint** ?

---

## 3. Deux phases obligatoirement séparées

Un argument rigoureux peut supprimer l'une des deux ; sans cet argument, les deux sont requises.

### Phase A — calibration de l'environnement spatial, `Y` inactif

**But.** Caractériser l'environnement X/source qualifié **sans rétroaction `Y`**, et enregistrer le
champ pré-réaction complet **à chaque pas d'ordonnanceur**.

`kY = 0`, `muY = 0`. C'est exactement le contrefactuel que l'opérateur un-`Y` requiert.

À enregistrer au minimum, **dans `pre_react`**, sur l'état post-diffusion pré-réaction :

```
nX(x,t)                   champ complet sur le tore
nSY(x,t)                  champ complet
free(x,t)                 champ complet
c(x,t) = min(nSY, free)   compte de candidats, par cellule
Q_POSITION(x,t) = nX·c    exposition résolue en position
position de la source / de l'organisateur, par pas ET par sous-pas
rejets de capacité (births refusés faute de `free`)
événements d'échange (_exchange : offres, prélèvements hypergéométriques)
```

**Branche porteuse : MOBILE** (condition M, `p_hop_Y = p_hop_X`). La branche statique
(`p_hop_Y = 0`) ne peut structurellement produire aucune séparation et ne peut donc pas porter le
test.

**Observateur seulement.** Aucune loi modifiée. L'inertie d'instrumentation doit être **prouvée**
(le flux RNG ne bouge pas quand on ajoute l'enregistreur), pas supposée.

### Phase B — calibration de lignée `Y` à faible effectif

**But.** Observer les **positions réelles des descendants**, mesurer la rétroaction et l'effet de
pool partagé, et déterminer si l'environnement gelé de la Phase A reste une approximation
contrôlée.

À prédéclarer, avant le premier monde :

- **un seul `Y` initial** ;
- des valeurs `kY`, `muY` de calibration choisies **sans aucun résultat de calibration** ;
- arrêt strict à l'extinction ou à la frontière gelée du troisième centre ;
- identités et positions complètes de toute la lignée `Y` ; naissances ; morts ; sauts ;
  co-localisation ; séparation ;
- l'**exposition locale pré-réaction de chaque `Y`**, pas seulement celle du fondateur ;
- la déplétion locale du pool, par cellule et par pas ;
- la perturbation environnementale **relative à la Phase A**, monde par monde.

> La Phase B est une **calibration développementale**, pas le test final de fenêtre. Les mondes de
> calibration doivent être **disjoints** des mondes de confirmation ultérieurs.

---

## 4. Unités indépendantes et taille d'échantillon — justifiée, pas décrétée

**L'unité est le monde.** Jamais la trame. Les blocs temporels effectifs sont un diagnostic
*intra*-monde et ne comptent jamais comme des mondes supplémentaires.

**Geler un estimateur d'IAT nommé avant le premier run.** Chez le parent, quatre estimateurs
divergent matériellement sur la queue ; l'écart entre estimateurs *est* un constat. Valeurs
parentes, estimateur séquence-initiale-positive à paires chevauchantes :

```
statique  min 5,783  médiane 6,977  moyenne 7,177  max  9,719 (S__seed9300009)  IQR 0,744
mobile    min 5,335  médiane 6,461  moyenne 9,197  max 35,335 (M__seed9300015)  IQR 2,075
```

La médiane mobile (6,46) est **sous** la moyenne statique : la moyenne mobile de 9,20 est tirée par
un seul bras à 35,3, soit **3,84×** la moyenne. Rapporter « IAT ~7–9 » seul masquait exactement
cela. **Dimensionner les blocs sur le maximum, pas sur la moyenne.**

**Justification de la taille d'échantillon.** Le livrable contraignant est une **borne inférieure
de confiance au niveau du monde** sur l'exposition — pas une moyenne (les 28 bras parents ont tous
`Q10 = 0`, donc aucun plancher ne peut venir d'une moyenne). Pour une borne inférieure
unilatérale **sans hypothèse de distribution** au quantile `q`, obtenue par le **minimum** de `n`
mondes, la couverture 95 % exige `(1−q)ⁿ ≤ 0,05`, soit `n ≥ ln(0,05)/ln(1−q)` :

| quantile visé | mondes minimum par condition |
|---|---|
| 20ᵉ centile | 14 |
| **10ᵉ centile** | **29** |
| 5ᵉ centile | 59 |

C'est ce qui justifie « ≥ 30 » — et non l'inverse. **Choisir le quantile d'abord, puis `n`.** Si la
règle de borne utilise la `k`-ième statistique d'ordre plutôt que le minimum, recalculer `n` en
conséquence et inscrire le calcul dans le gel.

Pour la Phase B, la même arithmétique s'applique à un événement : observer au moins une séparation
avec 95 % de probabilité quand le taux par monde vaut `p` exige `n ≥ ln(0,05)/ln(1−p)` — 29 mondes
si `p = 0,10`. **Ne pas dimensionner la Phase B sur l'intuition.**

À geler également : horizon, burn-in, cadence de trame, schéma complet du registre d'événements,
graines ou règle déterministe de génération, traitement de la corrélation temporelle,
incertitude au niveau du monde. **Aucun ajout ni remplacement adaptatif de mondes.**

---

## 5. Aucun retune piloté par les résultats

Gelé **avant le premier monde de calibration** : points de paramètres ; branche ; règles d'arrêt ;
règles d'invalidité ; schéma de champs ; estimands primaires ; construction de la borne
inférieure ; règle d'identification de l'opérateur ; matrice de décision.

Ne pas modifier `kY`, `muY`, l'horizon ou l'allocation de graines après avoir inspecté un
résultat.

**Committer le gel SEUL, dans son propre commit**, avant l'exécution de tout module lisant des
valeurs de trajectoire, et inscrire ce hash de commit **dans** le gel. Le parent ne l'a pas fait —
son gel et ses statistiques détaillées sont dans le même commit `decfda5`, donc
`INDEPENDENT_PRE_OUTCOME_FREEZE_COMMIT = false`. Cela n'a pas renversé un résultat **négatif et
développemental**, mais cela renverserait un résultat positif.

---

## 6. Couverture zéro-run et instrumentation

La sentinelle du parent était installée dans **1 module sur 8** et manquait un **quatrième** point
d'entrée de graine. PQEC01 doit :

- installer la sentinelle dans **tous** les modules et **agréger** les compteurs ;
- patcher les **quatre** points d'entrée : `kinetics`, `observe`, `lawspec_v2`, `engine_obtc` —
  et **tous** les constructeurs de `World`, y compris `observe.RecWorld` ;
- utiliser un inventaire de fichiers **récursif, sans limite de profondeur**, couvrant les racines
  de mission, du dépôt et de livraison ;
- auditer les commandes `subprocess` ;
- prouver que le garde **se déclenche** (contrôle positif), et non le supposer ;
- porter la conclusion par une **preuve statique d'imports** indépendante de tout compteur.

Un run ne se définit **ni** par la taille du réseau **ni** par le numéro de graine.

---

## 7. Ce que la calibration doit livrer

1. `Q_POSITION(x,t)`, résolu en position, par monde, aligné sur l'événement.
2. L'opérateur d'environnement de descendant mobile : transport relatif, contact, ré-rencontre.
3. Une **borne inférieure de confiance au niveau du monde** sur l'exposition, propagée avec le
   traitement de corrélation temporelle gelé.
4. Une **borne de rétroaction certifiée** pour au moins la première **et la deuxième** naissance —
   le parent ne contrôle que la première. Référence parente à battre : déplétion locale de
   **55,1 %** conditionnellement à `cand_Y ≥ 1`, effacée à un taux effectif mesuré de
   **0,3557/pas** (et non au taux d'offre `φ = 0,20`).
5. Un opérateur à deux `Y` **identifiable**, avec états `ONE_Y`, `TWO_Y_COLOCATED`,
   `TWO_Y_SEPARATED`, `THREE_OR_MORE_STOP`, `EXTINCT`, et position relative à la source.
   Rappel du parent : le tirage est **un seul binôme sur un pool partagé** — le processus n'est
   **pas** Galton–Watson, même si l'écart numérique au régime admissible est faible
   (écart relatif de variance ≈ −1,6×10⁻⁴, masse sur des issues impossibles ≈ 9,8×10⁻¹⁵).

---

## 8. Dispositions terminales admissibles

```
PROSPECTIVE_Q_ENVIRONMENT_OPERATOR_IDENTIFIED
PROSPECTIVE_Q_ENVIRONMENT_OPERATOR_NOT_IDENTIFIED__ADDITIONAL_INSTRUMENTATION_REQUIRED
EXISTING_ARCHITECTURE_FEEDBACK_PRECLUDES_CONTROLLED_WINDOW
CALIBRATION_TECHNICALLY_INVALID
```

- Seule la **première** peut autoriser la création d'un handoff ultérieur et disjoint
  `HANDOFF_FRESH_MINORITY_Y_WINDOW_TEST_01.md`.
- Seule la **troisième** peut réactiver une conception d'architecture. **Ne pas** réactiver
  l'architecture simplement parce que l'incertitude de calibration reste large.

---

## 9. Points d'attention hérités

- Aucune règle d'inclusion conditionnée sur un résultat (leçon OBFOR01).
- Toute revendication est opposée à un témoin sans physique.
- Ne pas présenter un contrôle vide comme un contrôle (leçon PMCR01).
- Une classification porteuse ne se dérive **jamais** d'une seule archive, et jamais d'un booléen
  codé en dur (leçon du sceau MYQBD01).
- Un audit revendiqué doit **exister** : le parent affirmait un contrôle AST d'accès aux données
  qui n'existait pas.

## 10. Statuts à reporter inconditionnellement

```
H3_STATUS                     = NOT_TESTED
REPRODUCTION_STATUS           = NOT_TESTED
AUTONOMOUS_COHESION_STATUS    = NOT_ESTABLISHED
HISTORICAL_WINDOW_STATUS      = NOT_PORTABLE
X_LAWSPEC_BASELINE            = UNCHANGED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
TOMMY_ACTION_REQUIRED         = NONE
```
