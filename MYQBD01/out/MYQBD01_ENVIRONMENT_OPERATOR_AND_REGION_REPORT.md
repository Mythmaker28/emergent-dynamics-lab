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
