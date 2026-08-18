# FLCR01 — OPÉRATEUR D'ÉTATS DÉVELOPPEMENTAL ET RÉGIONS

> Les 128 mondes PQEC01 sont `POST_OUTCOME_DEVELOPMENT_DATA`. Rien ici n'est prospectif,
> réservé ni confirmatoire. L'unité est **le monde**.

## 1. Occupation d'états, par point de paramètres

| point | mondes | E | O | C | S | P | F |
|---|---|---|---|---|---|---|---|
| B1 | 44 | 28 | 44 | 16 | 16 | 7 | 0 |
| B2 | 44 | 0 | 44 | 18 | 18 | 7 | 0 |

(nombre de **mondes indépendants** visitant chaque état, pas de pas.)

- B1 : jamais visités `['F']` ; moins de 5 mondes `aucun` ; dominance d'un monde par ligne {'E': 0.0, 'O': 0.066, 'C': 0.157, 'S': 0.201, 'P': 0.0, 'F': 0.0}
- B2 : jamais visités `['E', 'F']` ; moins de 5 mondes `aucun` ; dominance d'un monde par ligne {'E': 0.0, 'O': 0.028, 'C': 0.141, 'S': 0.15, 'P': 0.0, 'F': 0.0}

À **B2** (`muY = 10⁻⁸`) l'état `E` n'est **jamais** visité : aucune extinction en 44 mondes.
À **B1** (`muY = 9,26×10⁻⁵`) il l'est par 28 mondes sur 44. C'est la signature directe du rôle
de `muY` — et c'est ce que la porte fondateur essayait de contraindre dans les deux sens.

## 2. Durée de maintien à deux centres — la mesure nouvelle

```
épisodes à deux centres : 380
minimum   1 pas
médiane   16 pas
moyenne   244 pas
q90       615 pas
maximum   4999 pas
```

La distribution est **extrêmement asymétrique** : la médiane vaut 16 pas, la moyenne 244 et le
maximum 4999. La plupart des séparations se referment presque aussitôt ; une minorité tient des
milliers de pas. Rapporter une durée moyenne de maintien serait trompeur.

Délai entre première naissance et deux centres : médiane **111 pas** (n = 34), contre `TAU_SEP = 125`
gelé analytiquement — un écart de 11 %.

## 3. Statut des covariables — rien ne manque dans les données

**`RECORDED_BUT_NOT_USED`** (déjà dans les archives, jamais exploité) :

- birth-cell exposure class (in ycells, column Q_local, every step)
- local nX, nSY, free and candidate pool for EVERY occupied Y cell (ycells)
- source-relative displacement (src ledger + ycells positions)
- co-location duration (derivable from n_centres and N_Y)
- separation distance (max_pair_dist scalar, every step)
- number of active spatial centres (n_centres scalar, every step)

**`MISSING_FROM_DATA`** : `aucun`

**`RECORDED_BUT_NOT_IDENTIFIABLE`** :

- which individual Y produced a birth in a multiply occupied cell (SHARED_PARENT_POOL — an aggregate-engine limit, not a recording gap)
- per-particle lineage age

every covariate the PQEC01 successor handoff called 'missing instrumentation' is in fact RECORDED_BUT_NOT_USED. No additional field is required to condition the operator; what is missing is world coverage across the (kY, muY) plane, which is a design problem, not an instrumentation one.

## 4. Les trois régions

### Région de survie du fondateur

**VIDE** (0 points de grille). C1 and C3 force muY >= 6.2e-03 while C2_FOUNDER forces muY <= 6.3e-05; kY and the exposure cancel

### Région de continuité de lignée

**NON VIDE** — 563 points de grille, `kY ∈ [1.58e-05, 5.62e-04]`, `muY ∈ [1.00e-08, 1.19e-03]`.

Méthode : exact finite Markov chain on total Y count using the engine's own per-step binomial birth and death laws, at the measured mean candidate pool and mean organiser nX. Statut : **EXACT_UNDER_A_MEAN_FIELD_ENVIRONMENT — the chain uses mean exposure, not the position-resolved field**

**La contradiction disparaît.** En remplaçant la survie du fondateur par la non-extinction de
la lignée, la borne supérieure sur `muY` s'évanouit, et avec elle l'incompatibilité d'un facteur
98,8. Ce n'est pas un ajustement de seuil : c'est le retrait d'une exigence d'identité de
particule que l'objet scientifique n'a jamais imposée.

### Région fonctionnelle à deux centres — le critère **primaire**

**NOT_DETERMINABLE_ACROSS_THE_PLANE.** L3, L4 and L5 depend on SPATIAL rates -- centre formation, hold and third-centre appearance -- which were measured at exactly two (kY, muY) points. Two points cannot identify a surface over a two-dimensional plane, and nothing in the exact chain predicts them, because the chain counts Y and does not place them.

Mesuré aux deux seuls points disponibles :

| point | L1 première naissance | L2 lignée vivante | L3 deux centres | L4 maintien ≥ 16 | L5 pas de 3ᵉ |
|---|---|---|---|---|---|
| B1 | 0.364 | 0.364 | 0.364 ± 0.073 | 0.364 | 0.841 |
| B2 | 0.409 | 1.000 | 0.409 ± 0.074 | 0.409 | 0.841 |

Aux deux points, **L3 échoue** (0,364 et 0,409 contre un seuil de 0,50) et **L5 passe** (0,841).
Mais deux points ne déterminent pas une surface sur un plan : world coverage across the plane at the SAME instrumentation -- a design problem, not a missing field

## 5. Test de changement d'architecture

| test | tient ? |
|---|---|
| A lineage incompatible with third centre control for all kY muY | **False** |
| B requires different removal rates for founder and newborn | **False** |
| C requires age state contact or position dependent Y death | **NOT_ESTABLISHED** |
| D feedback necessarily causes uncontrolled X amplification | **False** |
| E exact operator proves every admissible lineage region empty | **False** |

```
ARCHITECTURE_CHANGE_JUSTIFIED = False
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
```

Explicitement **non** inféré de : the founder gate being self-contradictory ; PQEC01 provenance being incomplete ; a misspecified validation model ; the old positive gate being impossible ; more data being desirable.

Si un changement devenait un jour nécessaire, le plus petit degré de liberté manquant serait
**state-dependent Y removal (muY conditioned on the number of centres)** — it is the minimal change that could enforce third-centre control without killing the founder, and it adds no species and no new physical state variable -- only a dependence of an existing rate on an already-computed quantity


no candidate above introduces a new chemical species, and none is authorised by this mission

