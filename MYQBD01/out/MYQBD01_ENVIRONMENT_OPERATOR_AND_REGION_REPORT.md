# MYQBD01 — opérateur d'environnement et construction de région

## 1. Opérateur un-`Y`, redérivé indépendamment (§10)

`f(z) = (m + (1−m)z)·(1 − p(1−m)(1−z))^c`, `c = min(nSY,free)`, `p = min(1,kY·nX·nY)`, `m = muY`.
Les nouveau-nés décroissent dès leur pas de naissance (`_decay` suit `_react`). Vérifié contre une
**énumération exhaustive** indépendante (parent survit, nb naissances, nb nouveau-nés survivants) :
erreur max **2.2e-16**. Non repris de
PMCR01.

## 2. La réduction `β = kY·E[Q]` (§9)

```
CLASSIFICATION = SCALAR_Q_REDUCTION_VALID_ONLY_FOR_FIRST_BIRTH
```

Exacte pour l'intensité de la **première** naissance d'un seul `Y` (régime non saturé). Elle échoue
au-delà sur au moins quatre plans indépendants : dépletion de `SY` (condition 5), corrélation
temporelle IAT ~7–9 (condition 7), écart moyenne-arithmétique vs croissance multiplicative
(condition 8), et absence d'exposition de descendant (condition 9). Elle ne peut donc pas servir
seule à la région finale.

## 3. Le processus à deux `Y` n'est pas Galton–Watson (§11)

Deux `Y` co-localisés tirent **un seul** `Binomial(c, min(1,kY·nX·2))` du pool partagé `c`, et non
deux `Binomial(c, min(1,kY·nX·1))` indépendants. Contre-exemple exact :
- **régime non saturé** : les moyennes coïncident (`p2 = 2 p1`), mais le **support** diffère
  (naissances ≤ `c` contre ≤ `2c`) et la variance diffère ;
- **régime saturé** : les **moyennes** divergent (4,0 contre 4,8).

```
TWO_Y_STATE_OPERATOR_STATUS = NOT_IDENTIFIABLE_FROM_ORGANISER_ONLY_LEDGER
```

## 4. Ce qui est constructible, et où la construction s'arrête (§14)

Constructible : le diagnostic de **première naissance** par bras mobile, `B_i(kY) = kY·Σ_t Q(t)`,
identifiable exactement. Le `kY` donnant une naissance attendue sur la fenêtre est dans
`[3.24e-05,
3.87e-05]`.

**Non constructible** : la persistance au-delà de la première naissance (opérateur à deux `Y` non
identifiable), la séparation et le troisième centre (exposition de descendant non enregistrée), une
borne inférieure sur `β` (chaque bras mobile a `Q10 = 0` : aucun plancher d'exposition de queue
basse), et le contrôle de rétroaction au-delà de la première naissance.

## 5. Ce n'est PAS une préclusion structurelle (§15)

Sous l'environnement admissible **le plus favorable** (Q soutenu, sans épisodes nuls, sans
rétroaction), une lignée un-`Y` est surcritique et survit (témoin : `R > 1`, survie > 0,5). L'opérateur
exact **ne démontre donc pas** l'impossibilité. L'obstruction est un **registre manquant** et une
**non-identifiabilité**, que le gel exclut explicitement comme preuve structurelle.

---

## Réparations du sceau (A2, A5, A6, A7, A8)

### A2 — dépendance temporelle : distributions, pas une moyenne

Estimateur nommé : **séquence-initiale-positive à paires chevauchantes** (celui que le candidat
utilisait réellement ; la ligne morte `pair` a été retirée).

| branche | min | q25 | médiane | moyenne | q75 | max | IQR | bras du max |
|---|---|---|---|---|---|---|---|---|
| statique | 5,783 | — | 6,977 | 7,177 | — | 9,719 | 0,744 | `S__seed9300009` |
| mobile | 5,335 | — | 6,461 | **9,197** | — | **35,335** | 2,075 | `M__seed9300015` |

La médiane mobile est **sous** la moyenne statique. Trois estimateurs alternatifs (Geyer par
paires disjointes, première autocorrélation négative, blocs de 500) sont publiés par bras : ils
divergent matériellement sur la queue. **L'écart entre estimateurs est lui-même un constat** ;
PQEC01 doit en geler un et dimensionner ses blocs sur le **maximum**.

Les blocs temporels effectifs restent un diagnostic **intra-bras**. L'unité indépendante est le
bras — jamais la trame, jamais un bloc.

### A5 — portée exacte de `β = kY·E[Q]`

Clamp actif sur **0 des 126 000** pas mobiles examinés (il exigerait `nX ≥ 25 000`). L'exposant de
croissance trempé `E_t[log R_t]` vaut `1,248125×10⁻⁴` contre `kY·E[Q] − muY = 1,248381×10⁻⁴` :
**écart relatif −2,047×10⁻⁴**. Les conditions 7 et 8 (corrélation temporelle, moyenne vs
croissance multiplicative) étaient donc présentées de façon **trop pessimiste**.

```
SCALAR_Q_REDUCTION_STATUS = EXACT_FOR_FIRST_BIRTH_IN_ONE_Y_UNCLAMPED_REGIME__
                            INSUFFICIENT_FOR_COMPLETE_TWO_Y_SPATIAL_WINDOW
```

L'insuffisance repose sur : exposition de descendant manquante ; structure à pool partagé ;
rétroaction ; absence de tout registre d'environnement à deux `Y`. **Pas** sur une erreur
d'approximation de première naissance exagérée.

### A6 — deux `Y` : loi exacte sur le domaine admissible

À `kY = 4×10⁻⁵`, `c = 3`, `nX = 4` — pool partagé `Binomial(3, 3,2×10⁻⁴)` contre somme naïve de
deux `Binomial(3, 1,6×10⁻⁴)` :

```
support            0..3        contre 0..6
écart de moyenne   2,26e-16    (égales à la précision machine : 2·p1 = p2 exactement, non clampé)
écart de variance  -1,600e-04  (relatif)
distance VT        1,535e-07
masse sur des issues IMPOSSIBLES sous la loi exacte : 9,828e-15
```

Le contre-exemple pré-sceau à `kY = 0,05` / `0,20` — **1250× et 5000×** l'échelle admissible — est
conservé comme illustration structurelle uniquement, plus comme preuve quantitative.

```
CONCLUSION = MEAN_ONLY_EQUIVALENCE_TO_HIGH_ACCURACY_IN_UNCLAMPED_ADMISSIBLE_REGIME__
             BUT_EXACT_SUPPORT_AND_DEPENDENCE_ARE_NOT_GALTON_WATSON
```

La correction de pool partagé n'est petite **que** tant que les deux `Y` sont co-localisés sur le
pool de l'organisateur. Dès la séparation, l'exposition du descendant n'est plus une petite
correction à une quantité enregistrée : c'est une quantité **non enregistrée**. A6 étant
numériquement bénin ne sauve donc pas la région — c'est A4 qui porte, et A4 échoue.

### A7 — certificats de rétroaction, régénérés

```
taux d'OFFRE _exchange   phi = 0,20
taux EFFECTIF mesuré     0,355735 +- 0,013473  (14 bras statiques)   ratio 1,78x
```

`phi` paramètre `Binomial(max(S0 − nSY, 0), phi)` vers `S0 = 3` ; la relaxation observée est le
**net** de cette offre, de l'apport diffusif des voisines et du prélèvement hypergéométrique
qu'`_exchange` applique sur `{SX, SY, WX, WY}`. Substituer `phi` à la reconstitution — ce que
faisait le certificat pré-sceau — **sous-estime** la vitesse d'effacement.

Trois conditionnements, publiés séparément :

```
UNCONDITIONAL_MEAN_DEPLETION            101,52 %   (E[nSY] = 0,985048) — dénominateur inadéquat
CONDITIONAL_ON_BIRTH_POSSIBLE_DEPLETION  55,13 %   (E[nSY | cand_Y >= 1] = 1,814057) — RÉFÉRENCE
CONDITIONAL_ON_BIRTH_REALIZED_DEPLETION  48,57 %   (pondéré par 1-(1-p)^cand ; dérivé, kY = 0)
```

```
FIRST_BIRTH            : contrôlé (-1 SY sur 1,814, effacé en ~2,8 pas)
SECOND_BIRTH_AND_BEYOND: NON contrôlé
TWO_Y_COLOCATED        : non contrôlé (pool partagé, déplétion doublée)
TWO_Y_SEPARATED        : non bornable (exposition non enregistrée)
STATUS = FROZEN_ENVIRONMENT_FEEDBACK_NOT_FULLY_CONTROLLED
```

Cela **soutient la calibration** ; cela ne **prouve pas** une préclusion structurelle.

### A8 — témoins de non-préclusion, étiquetés par typicité

```
REPRÉSENTATIF (exposition mesurée E[Q] = 3,169730) : R = 1,000124838   marge 63,98x muY
FAVORABLE, ATYPIQUE (c = 3, nX = 4, exposition 12) : R = 1,000478048
                                                     eta* = 0,004063547247 (racine d'extinction)
                                                     survie à T = 11000 : 0,995957500914
```

Les deux sont `POST_OUTCOME_DEVELOPMENT_DIAGNOSTIC`. Le cadrage pré-sceau « l'environnement
admissible le plus favorable, `Q` maintenu à `Q_MAX` » était faux sur ses propres termes :
`Q_MAX = 28`, le témoin utilise 12 ; son pool vaut **3,12×** et son exposition **3,79×** les
moyennes mesurées. Le témoin **représentatif** porte désormais la conclusion — il n'utilise
aucune magnitude gonflée. Usage logique unique : `STRUCTURAL_PRECLUSION_NOT_PROVED`. Ce n'est
**pas** une qualification prospective de fenêtre.

`eta*` (racine asymptotique de `f(eta) = eta`) et la survie après exactement `T` pas sont deux
quantités distinctes ; les deux sont publiées pour qu'aucune ne soit prise pour l'autre.
