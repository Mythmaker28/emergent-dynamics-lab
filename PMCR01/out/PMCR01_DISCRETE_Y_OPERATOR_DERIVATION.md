# PMCR01 — dérivation de l'opérateur discret exact de la lignée `Y`

> Rien n'est ajusté et rien n'est simulé. La loi est **écrite depuis le chemin de
> code**, puis **vérifiée contre les arguments que l'ordonnanceur passe réellement**
> à `binomial`, capturés au point d'usage. `rng.binomial(n, p)` *est* la loi
> binomiale : prouver les arguments prouve la loi, sans aucun échantillonnage.

## 1. L'invariant d'occupation, fait porteur de catégorie A

```
_diffuse  accepte min(movers, dest_free)          -> ne peut pas dépasser CAP
_react    convertit SY -> Y et SX -> X            -> occupation conservée
_decay    convertit Y -> WY et X -> WX            -> occupation conservée
_exchange retire exactement ce qu'il insère       -> occupation conservée
```

Donc, en **toute** cellule et à **tout** pas :
`nX + nY + nSX + nSY + nWX + nWY ≤ CAP = 16`. C'est un fait de LawSpec, connu avant
tout run, et c'est la seule chose que la catégorie A sait de l'environnement de `Y`.

## 2. Ordre intra-pas, transcrit et non supposé

```
   _diffuse           ['X', 'p_hop_X']
   _diffuse           ['Y', 'p_hop_Y']
   _diffuse           ['SX', 'p_hop_X']
   _diffuse           ['SY', 'p_hop_X']
   _react             []
   _decay             []
   _feed_and_outflow  []
```

`_decay` s'exécute **après** `_react` : un `Y` nouveau-né est exposé à la
décroissance **dès son pas de naissance**. Ce n'est pas une hypothèse, c'est
`kinetics.World._one_step`.

## 3. La loi de descendance exacte, pour un `Y`

Soit, à la cellule occupée par le `Y`, après les quatre passes de diffusion :

```
c = min(nSY, free)              le nombre de candidats dans _react
p = min(1, kY · nX · nY)        la probabilité de naissance dans _react
m = muY                         la probabilité de retrait dans _decay
```

La fonction génératrice de la descendance d'un `Y` en un pas est **exactement**

```
f(z) = (m + (1−m) z) · (1 − p (1−m) (1−z))^c
```

— le premier facteur pour le parent, le second pour les `c` tirages candidats
indépendants, chacun donnant une naissance avec probabilité `p`, chaque nouveau-né
survivant à son propre pas de décroissance avec probabilité `1−m`. D'où

```
R = E[descendance] = (1 − muY) · (1 + c p)
Var                = m(1−m) + c p m(1−m) + (1−m)² c p (1−p)
```

### Vérification contre l'ordonnanceur

| état cellulaire | kY | muY | `c` analytique / capturé | `p` analytique / capturé | `m` analytique / capturé | `R` |
|---|---|---|---|---|---|---|
| nX=3 nSY=4 free=6 | 0 | 0 | 4 / 4 | 0 / 0 | 0 / 0 | 1.000000 |
| nX=3 nSY=4 free=6 | 0.05 | 0 | 4 / 4 | 0.15 / 0.15 | 0 / 0 | 1.600000 |
| nX=3 nSY=4 free=6 | 0.05 | 0.25 | 4 / 4 | 0.15 / 0.15 | 0.25 / 0.25 | 1.200000 |
| nX=3 nSY=4 free=6 | 0.5 | 0.9 | 4 / 4 | 1 / 1 | 0.9 / 0.9 | 0.500000 |
| nX=7 nSY=4 free=4 | 0 | 0 | 4 / 4 | 0 / 0 | 0 / 0 | 1.000000 |
| nX=7 nSY=4 free=4 | 0.05 | 0 | 4 / 4 | 0.35 / 0.35 | 0 / 0 | 2.400000 |
| nX=7 nSY=4 free=4 | 0.05 | 0.25 | 4 / 4 | 0.35 / 0.35 | 0.25 / 0.25 | 1.800000 |
| nX=7 nSY=4 free=4 | 0.5 | 0.9 | 4 / 4 | 1 / 1 | 0.9 / 0.9 | 0.500000 |
| nX=1 nSY=7 free=7 | 0 | 0 | 7 / 7 | 0 / 0 | 0 / 0 | 1.000000 |
| nX=1 nSY=7 free=7 | 0.05 | 0 | 7 / 7 | 0.05 / 0.05 | 0 / 0 | 1.350000 |

**Tous les arguments concordent : True.**

## 4. Le plafond exact `Q_max`, par énumération exhaustive

L'intensité de naissance par pas est `c · p = kY · Q` dans la branche linéaire, avec
`Q = nX · min(nSY, free)`. En énumérant les **15504** états cellulaires admissibles à
`nY = 1` sous l'invariant d'occupation :

```
Q_max = 28,  atteint en {'nX': 7, 'nY': 1, 'nSX': 0, 'nSY': 4, 'nWX': 0, 'nWY': 0, 'free': 4}
Q = 0 est admissible : True  (60.1 % des états admissibles)
infimum de Q sur l'ensemble admissible = 0
```

`Q_max = 28` est retrouvé indépendamment ici ; il coïncide avec le plafond nommé
dans le handoff hérité, ce qui est une concordance et non une reprise.

**Conséquence décisive.** La catégorie A connaît l'**ensemble** admissible. Une
valeur strictement positive de `E[Q]` est une propriété de la **mesure** sur cet
ensemble — c'est-à-dire du nuage réalisé. La borne **supérieure** `β ≤ 28 kY` est
certifiable sans aucun run ; la borne **inférieure** ne l'est pas.

## 5. Pourquoi un rapport de branchement scalaire n'est pas légitime ici

`c` et `p` sont fonctions de l'état de la cellule **du `Y` lui-même**, et `nX` à
cette cellule est produit **par ce `Y`** : `_react` ne crée du `X` que là où
`nX·nY ≥ 1`. L'environnement de la lignée est **endogène**. Le plus petit état exact
est donc `(n_Y par cellule occupée, et (nX, nSY, free) à chacune de ces cellules)`,
et non un scalaire.

```
OPÉRATEUR CONDITIONNEL   : CONDITIONAL_EXACT
FERMETURE MARGINALE      : NOT_CLOSED
```

C'est le même diagnostic que le parent a posé pour `X`, pour la même raison
structurelle. Il n'est pas hérité : il est redérivé ici sur la branche `Y`.

## 6. Saturation du canal `X` — le point qui décide de la notion de « minorité »

`p_X = min(1, kX · nX · nY)` avec `kX = 1.0`. Donc **`p_X = 1` exactement** dès que
`nX·nY ≥ 1`. Vérifié contre l'ordonnanceur :

| nX | nY (même cellule) | `p_X` analytique | `p_X` capturé | concorde |
|---|---|---|---|---|
| 0 | 1 | 0.000 | 0.0 | True |
| 1 | 1 | 1.000 | 1.0 | True |
| 3 | 1 | 1.000 | 1.0 | True |
| 3 | 2 | 1.000 | 1.0 | True |
| 7 | 3 | 1.000 | 1.0 | True |

**Un seul organisateur sature déjà la source `X` à pleine puissance.** Un
deuxième `Y` dans la *même* cellule n'ajoute rien ; il n'ajoute quelque chose qu'en
**se séparant**, et ce qu'il ajoute alors est une **deuxième cellule-source**.
« Minorité en nombre » et « minorité en rôle causal » se dissocient donc
complètement : le nombre de `Y` n'est pas une variable de minorité dans cette
architecture.

## 7. La couche d'observables est mono-organisateur par construction

```
out["organiser_y"], out["organiser_x"] = int(oy[0]), int(ox[0])
```

metrics_obtc.frame takes oy[0], ox[0] from np.nonzero(nY). With two organisers it silently reports one of them, chosen by row-major order, and r80_organiser is measured about that arbitrary centre. Every inherited observable, every frozen gate and the qualified source-response operator are SINGLE-ORGANISER BY CONSTRUCTION.

## 8. Constantes exactes du noyau

```
q = p_hop/4        = 0.025658350974743116
a = 2q(1−q)        = 0.050000     (manifeste : a_X = 0.05)
D = q(1−q)         = 0.025000     (manifeste : D_X = 0.025)
D_rel = 2D         = 0.050000     (manifeste : D_relative = 0.05)
concordance avec le manifeste gelé : True
```

Le déplacement par axe est la **différence de deux Bernoulli(q)**, pas `p_hop/4` :
c'est la loi exacte établie par OBTR01, réemployée ici sans réapprentissage.

Temps de séparation de deux `Y`, `⟨r²⟩ = 4 D_rel t` :

| distance (cellules) | pas |
|---|---|
| 1.000 | 5.0 |
| 2.500 | 31.2 |
| 5.000 | 125.0 |
| 6.083 | 185.0 |
| 8.544 | 365.0 |

## 9. Ce que l'opérateur permet de conclure, et ce qu'il ne permet pas

| affirmation | statut |
|---|---|
| la loi d'un pas est exacte conditionnellement à `(nX, nSY, free)` | **établie**, vérifiée argument par argument |
| `β ≤ 28 kY` pour tout état admissible | **établie** par énumération |
| `β ≥ ε > 0` pour un `ε` numérique | **non établissable** en catégorie A |
| un rayon spectral scalaire suffit | **non** : l'environnement est endogène |
| la densité marginale de la lignée se ferme | **non** |

