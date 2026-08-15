# ISING LIFE LAB — HANDOFF (INERTE, ZÉRO RUN)
## MINIMAL-Y-CHANNEL-ARCHITECTURE-DESIGN-01
## MYCAD01 — concevoir, sans l'implémenter, la plus petite capacité manquante

> Produit par `PROSPECTIVE-MINORITY-CHANNEL-REACHABILITY-01`, après revue adverse et réparation.
> **Ne rien implémenter et ne rien exécuter.** Ce handoff est un cahier des charges de conception.

```
OWNER                = Tommy
REPOSITORY           = Mythmaker28/emergent-dynamics-lab
PARENT_PROGRAM       = PROSPECTIVE-MINORITY-CHANNEL-REACHABILITY-01
PARENT_DISPOSITION   = STOP__ARCHITECTURE_CHANGE_REQUIRED
SHORT_NAME           = MYCAD01
NEW_ENGINE_STARTS    = 0
NEW_ARCHITECTURE_IMPLEMENTATION = 0
CODE_WRITTEN_INTO_THE_ENGINE = forbidden
RETUNE               = forbidden
TOMMY_ACTION_REQUIRED = NONE
```

## 0. Verser ce texte, et le rapport parent, dans le dépôt avant toute autre action

Le sceau OBFOR01 n'a pas pu certifier la conformité de budget parce que le mandat gouvernant
n'était nulle part dans l'arbre. **Premier commit de MYCAD01** : ce fichier et
`PMCR01_FINAL_REPORT.md` (ou leurs empreintes) versés dans le dépôt.

## 1. Ce que PMCR01 a établi, et pourquoi une architecture nouvelle est requise

- Les canaux `kY` (naissance) et `muY` (mort) sont des chemins **exécutables, atteignables**
  constructeur → ordonnanceur, prouvés par oracles de mutation déterministes. Ils ne sont pas
  absents.
- L'intensité de naissance minoritaire est `β = kY · E[Q]`, `Q = nX · min(nSY, free)` à la cellule
  de l'organisateur. `inf Q = 0` sur l'ensemble admissible, donc la **borne inférieure** de la
  fenêtre `(kY, muY)` n'est **pas certifiable** en catégorie A. C'est la raison **porteuse** de
  l'arrêt, et elle est indépendante de la branche (statique comme mobile).
- Raisons subsidiaires (branche mobile seulement) : une horloge de retrait unique `muY` pour deux
  rôles ; une couche d'observables mono-organisateur.

La capacité manquante n'est donc **pas** un canal de naissance ou de mort — ils existent. C'est un
mécanisme qui rende le **plancher** de l'intensité de naissance une **quantité de LawSpec** plutôt
qu'une propriété du nuage réalisé.

## 2. Objet de MYCAD01

Concevoir, **sur papier et en algèbre exacte uniquement**, la plus petite espèce/événement dont
l'ajout rendrait `ROBUST_NONEMPTY_REGION_EXISTS` certifiable en catégorie A, **sans** :

- démarrer le moteur ;
- écrire du code dans le moteur ;
- bouger la ligne de base `X` ;
- revendiquer reproduction, hérédité, cohésion autonome, ou tester H3.

## 3. Candidat de tête à évaluer (ne pas adopter d'office)

Une **espèce précurseur `Y` locale, finie, conservée**, liée à l'organisateur, de taille `P` et de
taux de reconstitution `rho`, consommée par la naissance de `Y`.

Pour ce candidat, produire :

```
WHY_EXISTING_ARCHITECTURE_CANNOT_EXPRESS_IT   (déjà établi : inf Q = 0)
MINIMAL_NEW_STATE_OR_EVENT                    (la 7e espèce, son événement de reconstitution)
CONSERVATION_OR_ACCOUNTING_REQUIREMENT        (ALL_OCC, free(), _exchange re-dérivés à 7 espèces)
EXPECTED_NEW_DEGREE_OF_FREEDOM                (une 2e échelle 1/rho, indépendante de 1/muY)
NEW_FAILURE_MODES                             (état absorbant pool-vide ; compétition CAP ; alias rho~phi)
SMALLEST_STATIC_QUALIFICATION_NEEDED          (liste en §5)
```

## 4. Contraintes de conception héritées, à respecter

1. **La borne inférieure doit être une quantité de LawSpec.** C'est tout le point : un pool plein
   garantit `β ≥ kY · P_min` par construction, indépendamment du nuage.
2. **La ligne de base `X` ne doit pas bouger.** Une nouvelle espèce occupant `CAP` entre en
   compétition avec SX/SY dans `_exchange` et dans `free()`. Prouver, en algèbre, que la réponse de
   source `X` qualifiée reste inchangée — sinon la capacité est disqualifiée.
3. **Pas d'aliasing caché.** Si le pool est reconstitué par le chémostat, `rho` s'aliase à
   `phi`/`S0` exactement comme l'offre SY l'est déjà, et le degré de liberté disparaît. La
   reconstitution doit être un canal **distinct**.
4. **Un zéro structurel n'est pas un petit nombre.** L'absence de pool n'est pas un pool faible.
5. **Toute observable primaire future doit être débiaisée** (leçon héritée : la médiane intra-graine
   d'un quantile de premier franchissement biaise de plusieurs pour cent).
6. **Éviter le biologisme.** Ni membrane, ni génome, ni couche de saturation, ni « mémoires »
   multiples, sauf si un blocage précis et exécutable l'impose.

## 5. Qualification statique minimale exigée (avant tout run futur)

```
re-dériver l'invariant d'occupation à 7 espèces ; prouver que _exchange conserve exactement
re-énumérer Q_max sous le nouvel ensemble admissible
oracles de mutation : kY, muY, ET rho
prouver la ligne de base X inchangée : mêmes arguments de hasard capturés sur la branche X,
    pour la même graine, pool présent-plein et pool présent-vide
étendre metrics_obtc pour résoudre PLUSIEURS organisateurs avant toute observable nommant
    « l'organisateur »
```

## 6. Dispositions terminales admissibles pour MYCAD01

Exactement une :

```
MINIMAL_CAPABILITY_STATICALLY_QUALIFIED_DESIGN_READY   (conception prête, toujours zéro run)
CANDIDATE_CAPABILITY_REJECTED_MOVES_X_BASELINE
CANDIDATE_CAPABILITY_REJECTED_ALIASES_AN_EXISTING_RATE
STOP__NO_MINIMAL_CAPABILITY_WITHOUT_MOVING_X
```

## 7. Statuts à reporter inconditionnellement

```
H3_STATUS                  = NOT_TESTED
REPRODUCTION_STATUS        = NOT_TESTED
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED
HISTORICAL_WINDOW_STATUS   = NOT_PORTABLE
X_LAWSPEC_BASELINE         = UNCHANGED
SCIENTIFIC_RUNS_USED       = 0
TOMMY_ACTION_REQUIRED      = NONE
```
