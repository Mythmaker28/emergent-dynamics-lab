# `WSFSCRP00` — jeu de lecture au redémarrage et rapport de jumeaux

`INDEPENDENT_REVIEW = NOT_PERFORMED` · `ORACLE_CHECK = SINGLE_EXECUTOR_INTERNAL`.
Un seul exécuteur Claude. L'implémentation de référence ci-dessous est un **oracle de référence
interne**, pas un relecteur indépendant, pas un second modèle, pas un sous-agent.

## Énumération du jeu de lecture

Aucune fonction n'a été crue sur son nom. Les champs sérialisés sont énumérés par **inspection
dynamique de `vars(state)`**, pas par une liste de noms de confiance. L'état canonique contient
exactement : `rho, U, V, c, N, C, uptake, Mf, step`. Le moteur ne porte ni mémoire d'intégrateur,
ni file d'événements, ni état d'ordonnanceur, ni cache non reconstructible ; `kappa` est recalculé
depuis `Mf` et `rho` à chaque pas. Le réseau est périodique 64×64, fixé par `ScaffoldSpec`.
Aucun tirage aléatoire n'existe après `t0` : le seul objet stochastique est évalué une fois à
`t = 0`, avant toute branche.

Incertitude résiduelle, documentaire : la graine RNG globale de NumPy n'est pas sérialisée dans le
point de contrôle. Elle ne peut affecter aucun état scoré, puisque le pas moteur ne tire rien —
et le test de déterminisme plein horizon ci-dessous le confirme empiriquement.

## Tests exécutés

| test | résultat |
|---|---|
| **jumeau sham 1 = jumeau sham 2, plein horizon** (400 pas, deux rechargements indépendants des mêmes octets) | **6/6 fondateurs TRAIN identiques** — courbes des deux canaux et empreinte d'état final |
| rechargement = octets sources | 6/6 |
| masques byte-identiques avant et après les exécutions complètes | 6/6 |
| accord lecteur de production / lecteur de référence sur la paire **non ordonnée** | **12/12** fondateurs admissibles |
| `rho` finie, `B_b > 0`, masques disjoints et non vides | 12/12 |
| zéro structurel `r(h=0) = (0,0)` quand l'opérateur ne touche pas `rho` | **12/12** |
| ensemble touché déclaré = ensemble touché mesuré | 12/12, `['Mf']` seul |
| domaine post-état (`\|Mf0\| ≤ rho` et la porte `alive`) | 12/12 |

```
SHAM_TWIN_NONDETERMINISM              = NOT_OBSERVED
FIXED_SUPPORT_READER_MUTABLE_OR_INCORRECT = NOT_OBSERVED
INTERVENTION_DOMAIN_OR_TOUCHSET_VIOLATION = NOT_OBSERVED
PARENT_PROVENANCE_UNRECOVERABLE       = NOT_OBSERVED
RESTART_FIDELITY                      = FULL (les deux jumeaux utilisent le même chemin de
                                        rechargement canonique, et le déterminisme plein horizon
                                        est vérifié)
```

Le zéro structurel `r(h=0)` est utile mais potentiellement vide : il est rapporté **en plus** du
test de déterminisme plein horizon, jamais à sa place.
