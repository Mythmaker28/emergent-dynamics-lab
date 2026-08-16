# MYQBD01 — sémantique de `Q` et phase d'ordonnanceur (Gate 0)

## 1. Phase exacte

Ordre de l'ordonnanceur (`kinetics.World._one_step`) :
`_diffuse X → _diffuse Y → _diffuse SX → _diffuse SY → _react → _decay → _feed_and_outflow`.

Le champ `Q` (index 20 de `series`) est écrit dans `Recorder.pre_react` (`observe.py:51`), sur
l'état **post-diffusion, pré-réaction**, à la ligne 69 :

```
m  = nY > 0
cy = np.minimum(nSY[m], free[m])
"Q": float((nX[m] * cy).sum())
```

`_react_core` lit `free0 = max(self.free(),0)` en tête de `_react`, et `cand_Y = min(nSY, free0)`,
`p_Y = min(1, kY·nX·nY)`. Comme `pre_react` s'exécute **avant** `_react_core` sur l'état identique,
`cand_Y` enregistré = le paramètre `n` exact du binôme de naissance `Y`, et `nX` = le multiplicateur
exact de `p_Y`. La ligne est finalisée à **chaque pas** (`series` a 11 000 lignes).

```
CLASSIFICATION = Q_LEDGER_EVENT_EXACT   (cellule organisatrice, régime un-Y, par pas, non sous-échantillonné)
```

**Réserve multi-Y.** `Q_enregistré = Σ nX·min(nSY,free)`. L'intensité de naissance par cellule est
`min(nSY,free)·min(1,kY·nX·nY)`. En régime non saturé à un `Y` par cellule, l'intensité vaut
`kY·Q_cellule` : donc `kY·Q_enregistré` est l'intensité exacte de **première naissance**. Avec
`nY ≥ 2` co-localisés, l'intensité porte un facteur `nY` que `Q_enregistré` omet ; sous saturation
la relation linéaire disparaît. `Q_enregistré` est l'exposition **un-Y** exacte et rien de plus.

## 2. Les six quantités `Q`, jamais confondues

| quantité | définition | égale à `Q_RECORDED` en régime un-Y ? |
|---|---|---|
| `Q_ORGANISER` | `nX·min(nSY,free)` aux cellules `nY>0` | oui |
| `Q_REACTION` | exposition entrant dans le binôme de naissance | **oui, exactement** |
| `Q_POSITION(x)` | exposition à une cellule `x` quelconque | non |
| `Q_LINEAGE` | `Q_POSITION` le long d'une lignée | non après séparation |
| `Q_AGGREGATE` | somme sur toutes les cellules contenant `Y` | oui tant qu'une seule cellule `Y` |
| `Q_RECORDED` | champ `Q` sérialisé | — |

**Divergence après la première naissance.** Dès qu'un descendant mobile quitte la cellule
organisatrice, `Q_POSITION` à sa nouvelle cellule est une quantité **différente et non
enregistrée**. Deux `Y` co-localisés couplent `Q_REACTION` (facteur `nY`). C'est le point porteur :
le champ enregistré est le même objet que le `Q` un-organisateur de PMCR01, mais **pas**
l'environnement de lignée à deux `Y`.
