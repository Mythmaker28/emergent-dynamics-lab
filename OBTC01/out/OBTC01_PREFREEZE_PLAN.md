# OBTC01 — plan pré-freeze

Ce document fixe la question, l'opérateur, les nuls, les conditions et la règle de décision
**avant** le premier démarrage informatif. Les seuils numériques ne sont pas recopiés ici : ils
vivent dans `organizer_bound_cloud_protocol.yaml`, qui est la source unique.

## 1. Question

Le LawSpec équilibré, **sans aucun mécanisme de cohésion ajouté**, produit-il un nuage `X`
spatialement borné relativement à l'organisateur, maintenu par un flux local de naissance et de
mort, traversé par un renouvellement matériel, causalement dépendant de l'organisateur,
quantitativement prédit par un opérateur source–transport–décroissance, robuste aux graines et à
la taille du domaine, sans saturation globale et sans confinement par une paroi ?

## 2. L'opérateur, lu sur le moteur, sans paramètre libre

| lecture | conséquence |
|---|---|
| `p_X = min(1, k_X·n_X·n_Y)` est nul partout où `n_Y = 0` | `X` naît **en une seule cellule** : celle de l'organisateur |
| `_diffuse` fait quatre passes par pas, chacune `Binomial(n, q)`, `q = p_hop/4` | déplacement par pas et par axe `B1 − B2`, variance `a = 2q(1−q) = 0.05`, donc `D = 0.025` — et **non** `p_hop/4` |
| `_decay` tire `Binomial(n_X, µ_X)` par cellule, sans dépendance de position ni de voisinage | l'âge d'une molécule est géométrique de paramètre `µ_X` |
| l'acceptation d'un saut est `min(movers, dest_free)` | le transport n'est **pas** libre : c'est le seul écart à la convolution, et il est mesuré, pas supposé |

Convolution testée :  `ρ_t(x) = Σ_{s≤t} B_s K_{t−s}(x − Y_s)`,  `K_u = (1−µ)^u P_u`.

Prédictions analytiques, calculées avant les runs et gelées :

```
ℓ_X isolée               2.5000        ℓ relative           3.5355
r80 source statique      6.0828        r80 repère source    8.5440
|cœur − organisateur|    3.1239 (module moyen)   3.1930 avec la correction d'échantillon à N_X=120
retard optimal           249 pas       décroissance source-off : e-folding 249.5 pas, demi-vie 172.9
```

## 3. Les quatre nuls, et lequel peut confirmer

| nul | conditionné sur | ce qu'il peut établir |
|---|---|---|
| **N0** `CONDITIONAL_NULL` | `N_X` et le domaine | l'existence d'une localisation quelconque |
| **N1** `CONDITIONAL_NULL` | la trajectoire réelle de l'organisateur **et** l'historique réel des naissances | un excès de compacité **au-delà** d'une source mobile — jamais la suffisance du mécanisme, puisqu'on lui remet la sortie du mécanisme |
| **N2** `GENERATIVE_NULL` | **rien de réalisé** ; seule la taille d'échantillon est appariée | la **suffisance** de l'opérateur : c'est le seul nul qui prédit |
| **N3** `CONDITIONAL_NULL` | la distribution marginale des positions du cœur | la persistance organisationnelle du cœur |

Toute statistique de forme de N2 est invariante à l'intensité de naissance ; seule la taille
d'échantillon est appariée, et seulement parce que le bruit d'échantillonnage en dépend.

## 4. Le confondant identifié avant les runs

Sous N2 — où il n'y a **aucune** cohésion par construction — la fraction de masse de la
composante principale passe de 0.23 à 0.80 quand `N_X` passe de 30 à 320. Une statistique de forme
comparée à un **seuil fixe** récompenserait donc une population plus grande comme si c'était de la
cohésion. Toute comparaison de cette mission est faite contre le nul **évalué à la valeur de
`N_X` du bras lui-même**. (`_metric_dependence.json`.)

## 5. Conditions

`P` organisateur mobile, 6 graines — condition principale.
`S` organisateur immobilisé par `p_hop_Y = 0`, 3 graines — profil statique et temps de relaxation.
`R` source retirée après le burn-in par `Y → WY`, occupation conservée exactement, 3 graines.
`N` aucune source, 2 graines.
`D` domaine `L = 72`, 3 graines.
`E` trajectoire exogène gelée — **ouverte seulement si** la mesure montre que le mouvement de
l'organisateur est matériellement couplé à `X`. Le critère est la fraction de sauts de `Y`
refusés par la capacité, mesurée directement par les compteurs du moteur.

## 6. Ce qui est interdit dans cette mission

Aucun mécanisme de cohésion. `C3_NEIGHBOUR_PROTECTED_DECAY` n'est pas réintroduit et sa valeur
`lambda = 0.129449` n'est ni réutilisée ni prise comme point de départ. Aucune adhésion `X-X`,
aucune protection contre la mort, aucune attraction vers l'organisateur, aucune réduction de
diffusion, aucune interaction de voisinage. Aucun paramètre de performance n'existe, donc aucune
calibration de performance n'a lieu.

## 7. Ce qui n'est pas testé

Ni H3, ni reconstruction, ni reproduction, ni héritabilité, ni individualité, ni séparation en
deux descendants, ni mémoire, ni propriété de « vivant ». `H3_STATUS = NOT_TESTED`,
`REPRODUCTION_STATUS = NOT_TESTED`, `AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED`,
inconditionnellement.
