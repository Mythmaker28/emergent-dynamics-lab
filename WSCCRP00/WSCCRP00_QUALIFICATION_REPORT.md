# `WSCCRP00` — rapport de qualification

**TRAIN_SELECTION uniquement. `LOCKED_DEV_EVALUATION` n'existe pas et n'a jamais été ouvert.**
20 démarrages moteur sur un plafond de qualification de 24.

## Q1 — exactitude et domaine

| contrôle | résultat |
|---|---|
| `r[b,u,0] = 0` quand l'opérateur ne change aucune variable lue par `a` | **exactement 0,0** dans les 16 unités |
| masses finies, dénominateurs strictement positifs | oui, à tous les temps scorés |
| identités sham / rechargement / redémarrage | héritées et revérifiées, bit-exactes |
| **décomposition champ / appartenance** | **ÉCHEC — voir ci-dessous** |

Le contrôle `r = 0` à `h = 0` n'est pas décoratif : les opérateurs de porteur ne touchent que
`Mf[0]`, que `a` ne lit pas. Il vaut donc exactement zéro, et le vérifier écarte une classe
entière de fuites.

## Q2 — signal matériel : **PASS**

```
A_bu = Σ_h w_h |r[b,u,h]|        ETA_b = max(ETA_ORACLE, 0,01·G_b)
```

| fondateur | `G_b` | `ETA_b` | S1 transposition | S2 réfl. intensive | S2 réfl. extensive | S2 ablation totale |
|---|---|---|---|---|---|---|
| 61000 | 0,1491 | 0,00149 | **0,01418** | **0,01220** | **0,01321** | **0,00920** |
| 61001 | 0,1894 | 0,00189 | **0,00669** | **0,01270** | **0,01006** | **0,00530** |
| 61002 | 0,1641 | 0,00164 | **0,01228** | **0,01191** | **0,01207** | **0,00757** |
| 61003 | 0,1307 | 0,00131 | **0,00949** | **0,00752** | **0,00698** | **0,00376** |

Les deux superfamilles TRAIN dépassent `ETA_b` dans les **4** fondateurs (il en fallait 2 et 3).
Le signal n'est **pas** porté par le bras environnemental : celui-ci est verrouillé et n'a pas
été exécuté.

## Q3 — rang de la réponse : **PASS**

Matrice `16 unités × 10 temps`, pondérée par `√w_h` :

```
valeurs singulières : 0,040058  0,025863  0,014812  0,012311  0,004898
sigma_2 / sigma_1 = 0,6456      (porte > 0,10)
après retrait du gabarit global : 0,5869
énergie du mode 1 : 59,4 %
|cos| au gabarit dominant : min 0,014 · médiane 0,807
```

La réponse n'est **pas** de rang un : ce n'est pas un gabarit unique multiplié par une amplitude.
`RANK_ONE_RESPONSE` n'est pas déclenché.

## Le contrôle d'éligibilité de la Section 4 : **ÉCHEC**

```
fraction d'énergie attribuable à l'appartenance :  médiane 0,988 · max 1,228
seuil d'inéligibilité :                            0,50
```

Réponse à masques figés : `A_fix/A_dyn` médiane 0,73, au-dessus de `ETA_b` dans 16/16 unités,
mais **décorrélée en forme** de la réponse du lecteur gelé (`corr` médiane −0,039, plage
−0,77 … +0,56).

Ce contrôle est en **amont** de Q4 et Q5 : il porte sur l'éligibilité du point de mesure, pas sur
la trivialité du prédicteur. Q4 et Q5 n'ont donc **pas** été exécutés, et aucune représentation
n'a été construite.

## Disposition

```
WSCCRP00_DISPOSITION = NO_EXACT_CONTINUOUS_CAUSAL_ORACLE
DETAIL               = MEMBERSHIP_JUMP_DOMINATED_ENDPOINT
```

*Note de nommage, déclarée plutôt que dissimulée :* l'**oracle de redémarrage** est exact et
fonctionne (rejeu bit-exact, jumeaux sham, `r=0` à `h=0`). Ce qui échoue est la condition de
continuité/éligibilité de la Section 4. J'utilise l'étiquette de la liste fournie à laquelle la
Section 6 rattache l'échec du point de mesure, assortie du qualificatif `DETAIL`, sur le modèle
que le handoff emploie lui-même pour Q4. Choisir une étiquette de la liste qui décrirait mal
l'échec aurait été pire que de la qualifier.
