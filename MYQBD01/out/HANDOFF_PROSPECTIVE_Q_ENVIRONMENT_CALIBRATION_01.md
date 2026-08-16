# ISING LIFE LAB — HANDOFF
## PROSPECTIVE-Q-ENVIRONMENT-CALIBRATION-01
## PQEC01 — geler et enregistrer l'environnement `Q` résolu en position, pour un test `Y` ultérieur

> Produit par `MINORITY-Y-Q-BOUND-DERIVATION-01`. **Ne pas exécuter dans la session MYQBD01.**
> Ce handoff est le seul admissible après la disposition
> `EXISTING_Q_DATA_INSUFFICIENT__PROSPECTIVE_Q_CALIBRATION_REQUIRED`.

```
OWNER                 = Tommy
REPOSITORY            = Mythmaker28/emergent-dynamics-lab
PARENT_PROGRAM        = MINORITY-Y-Q-BOUND-DERIVATION-01
PARENT_DISPOSITION    = EXISTING_Q_DATA_INSUFFICIENT__PROSPECTIVE_Q_CALIBRATION_REQUIRED
SHORT_NAME            = PQEC01
DYNAMIC_Y_BIRTH_DEATH = INACTIVE (kY = 0, muY = 0) unless separately justified (see §4)
ARCHITECTURE_CHANGE   = forbidden
X_LAWSPEC_BASELINE    = UNCHANGED
TOMMY_ACTION_REQUIRED = NONE
```

## 0. Verser ce texte dans le dépôt avant toute autre action.

## 1. Pourquoi cette calibration, et pas une architecture

MYQBD01 a établi que le champ `Q` déjà enregistré est **exact à l'événement** pour la première
naissance d'un seul `Y` (`Q_LEDGER_EVENT_EXACT`), mais qu'il est **scalaire, à la cellule
organisatrice seule**, avec les tableaux spatiaux complets seulement au pas terminal. Il ne peut
donc pas localiser l'exposition d'un descendant séparé, ni identifier l'opérateur à deux `Y`, ni
borner la rétroaction au-delà de la première naissance. Ce n'est ni une impossibilité structurelle
(l'opérateur ne l'a pas démontrée), ni un défaut d'architecture : c'est un **registre manquant**.
PQEC01 comble ce registre **sans changer la physique**.

## 2. Objectif

Produire, par des mondes neufs et indépendants, un **registre `Q` aligné sur l'événement et résolu
en position**, suffisant pour dériver l'environnement d'exposition d'un descendant mobile et une
**borne inférieure de confiance au niveau du monde** sur l'exposition, à `LawSpec X` inchangé.

## 3. Ce qui doit être gelé avant tout run

```
branche exacte                     : MOBILE (condition M, p_hop_Y = p_hop_X) — la branche porteuse
nombre de mondes indépendants      : à fixer (>= 30 recommandé) ; disjoints des mondes du test Y ultérieur
graines ou règle de génération     : gelées, disjointes de tout registre scientifique existant
horizon et burn-in                 : 11000 / 2000 (identiques au parent)
registre Q aligné sur l'événement  : Q enregistré dans pre_react, par pas (déjà exact)
CHAMPS SPATIAUX COMPLETS PAR PAS   : nX(x), nSY(x), free(x) sur tout le tore, ou au minimum sur un
                                     voisinage suivant la trajectoire du descendant — c'est le
                                     champ manquant que PQEC01 doit ajouter à l'instrumentation
                                     (observateur seulement ; aucune loi modifiée)
exposition organisateur ET position: Q_ORGANISER et Q_POSITION(x) le long des trajectoires admissibles
incertitude au niveau du monde     : unité = un monde ; jamais la trame (IAT ~7-9)
traitement de la corrélation temp. : temps d'autocorrélation intégré par monde, blocs effectifs
règle de borne inférieure          : quantile bas au niveau du monde, gelé (les bras parents ont Q10 = 0)
aucun retune adaptatif
mondes de calibration DISJOINTS des mondes du test Y ultérieur
```

## 4. Naissance/mort de `Y` : inactives par défaut

`kY = 0`, `muY = 0`. La calibration enregistre l'environnement **contrefactuel** (celui qu'un `Y`
inerte verrait), qui est exactement ce que l'opérateur un-`Y` requiert. **N'activer** une
naissance/mort dynamique de `Y` que si la logique exacte de calibration l'exige — par exemple pour
mesurer la dépletion de `SY` induite par une lignée active (§13 du parent) — et alors le justifier
séparément, en isolant l'effet et sans en faire le test primaire.

## 5. Ce que la calibration doit livrer

1. Le champ `Q_POSITION(x,t)` résolu en position, par monde, aligné sur l'événement.
2. L'opérateur d'environnement de descendant mobile (transport relatif, contact, ré-encontre).
3. Une **borne inférieure de confiance au niveau du monde** sur l'exposition, propagée avec le
   traitement de corrélation temporelle.
4. Une **borne de rétroaction** certifiée pour au moins la première et la deuxième naissance.
5. Un opérateur à deux `Y` identifiable (états `ONE_Y`, `TWO_Y_COLOCATED`, `TWO_Y_SEPARATED`,
   `THREE_OR_MORE_STOP`, `EXTINCT`), avec position relative à la source.

## 6. Dispositions terminales admissibles

```
Q_CALIBRATION_SUFFICIENT__MOBILE_ENVIRONMENT_OPERATOR_DERIVED   (peut alors préenregistrer, sans
                                                                 l'exécuter, un test frais de fenêtre Y)
Q_CALIBRATION_INSUFFICIENT__EXACT_MISSING_FIELD_NAMED
STOP__ENVIRONMENT_OPERATOR_STRUCTURALLY_PRECLUDES_WINDOW        (seulement si l'opérateur exact le prouve)
```

## 7. Points d'attention hérités

- **Unité indépendante = le monde.** Jamais la trame (IAT ~7–9).
- **Aucune règle d'inclusion conditionnée sur un résultat** (leçon OBFOR01).
- **Le critère se gèle en entier avant les runs.**
- **Toute revendication est opposée à un témoin sans physique.**
- **Ne pas présenter un contrôle vide comme un contrôle** (leçon PMCR01).
- **`Q10 = 0` chez tous les bras parents** : une borne inférieure d'exposition ne peut pas venir
  d'une moyenne ; elle doit venir d'un quantile bas au niveau du monde, gelé à l'avance.

## 8. Statuts à reporter inconditionnellement

```
H3_STATUS                  = NOT_TESTED
REPRODUCTION_STATUS        = NOT_TESTED
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED
HISTORICAL_WINDOW_STATUS   = NOT_PORTABLE
X_LAWSPEC_BASELINE         = UNCHANGED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
SCIENTIFIC_RUNS_USED       = 0   (dans PQEC01 la conception ; les runs de calibration sont un temps ultérieur)
TOMMY_ACTION_REQUIRED      = NONE
```
