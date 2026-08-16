# ISING LIFE LAB — HANDOFF (BRUT UNIQUEMENT, ZÉRO RUN)
## MINORITY-Y-Q-BOUND-DERIVATION-01
## MYQBD01 — dériver un opérateur d'exposition environnementale depuis les `Q` déjà enregistrés

> Produit par `PMCR01-REVIEW-DRIVEN-Q-INSTRUMENTATION-REPAIR-01`.
> **Ne pas exécuter dans la session de réparation.**
> Remplace `MINIMAL-Y-CHANNEL-ARCHITECTURE-DESIGN-01`, marqué `SUPERSEDED_NOT_AUTHORIZED`.

```
OWNER                 = Tommy
REPOSITORY            = Mythmaker28/emergent-dynamics-lab
PARENT_PROGRAM        = PROSPECTIVE-MINORITY-CHANNEL-REACHABILITY-01
PARENT_DISPOSITION    = EXISTING_ARCHITECTURE_WINDOW_NOT_YET_PROSPECTIVELY_LOCATED
SHORT_NAME            = MYQBD01
NEW_SCIENTIFIC_ENGINE_RUNS      = 0
NEW_WORLD_CONSTRUCTIONS         = 0
NEW_SEEDS                       = 0
SCIENTIFIC_TRAJECTORY_REPLAY    = forbidden
ARCHITECTURE_IMPLEMENTATION     = forbidden
FRESH_Y_TEST_EXECUTION          = forbidden
PROSPECTIVE_Q_CALIBRATION_EXECUTION = forbidden
TOMMY_ACTION_REQUIRED = NONE
```

## 0. Verser ce texte dans le dépôt avant toute autre action

Premier commit de MYQBD01 : ce fichier, ou son SHA-256, versé dans le dépôt. La leçon héritée du
sceau OBFOR01 — un mandat gouvernant absent de l'arbre rend la conformité invérifiable — s'applique
sans exception.

## 1. Pourquoi cette mission remplace la conception d'architecture

PMCR01 a d'abord conclu `STOP__ARCHITECTURE_CHANGE_REQUIRED`. Sa revue adverse a confirmé un défaut
porteur : l'intensité d'exposition environnementale

```
Q = nX · min(nSY, free)   à la cellule propre de l'organisateur
```

n'est pas une quantité inaccessible. Elle est **instrumentée et enregistrée** par l'architecture
existante — `ORR01/code/observe.py`, lignes 55, 59, 69, champ d'indice 20 — et présente dans
**les 28 bras livrés**, sans aucune valeur manquante.

Ce que PMCR01 n'a donc PAS établi : que l'architecture doive changer.
Ce qui lui manque réellement : une **borne gelée à l'avance** sur `Q`, permettant de transporter la
région non vide en `(β, muY)` vers une région exécutable en `(kY, muY)`.

## 2. Question unique de la mission

> Les trajectoires `Q` déjà enregistrées des 28 bras OBFOR01, traitées **explicitement comme un
> jeu de données de développement**, fournissent-elles un opérateur d'environnement rigoureux
> **spécifique à la branche**, ou une borne conservatrice, suffisant pour cartographier la région
> non vide `(β, muY)` en une région candidate exécutable `(kY, muY)` destinée à un test
> indépendant ultérieur ?

## 3. Statut probatoire imposé — à écrire dans chaque artefact

```
LES_28_BRAS = POST_OUTCOME_DEVELOPMENT_DIAGNOSTIC
```

Aucune borne sur `Q` n'a été gelée avant l'exécution de ces bras. Ils sont **admissibles** comme
jeu de découverte et de conception de calibration. Ils ne sont **pas** une borne inférieure
prospectivement gelée et ne doivent jamais être présentés comme une preuve confirmatoire d'une
fenêtre `kY`. Toute formulation qui efface cette distinction est un défaut porteur.

Symétriquement : ne pas les déclarer scientifiquement inertes au motif qu'ils n'ont pas été
préenregistrés. Un jeu de découverte déclaré est une pièce légitime pour concevoir une confirmation
indépendante.

## 4. Ordre de travail imposé

1. **Reconstruction exacte de chaque trajectoire `Q`.** Les 28 bras, colonne 20, empreintes
   SHA-256 par tableau source. Aucune sélection de bras favorables, aucune exclusion.
2. **Analyses statique et mobile séparées.** Les deux branches sont des conditions gelées
   distinctes (`p_hop_Y = 0` contre `p_hop_Y = p_hop_X`), 14 bras chacune. La réparation PMCR01 a
   déjà mesuré une différence matérielle entre elles ; ne jamais les moyenner.
3. **La branche MOBILE est la branche porteuse** pour la séparation spatiale. La branche statique
   ne peut pas prouver la séparation, et la non-séparation statique ne peut pas prouver
   l'impossibilité de persistance mobile.
4. **L'unité indépendante est le monde (le bras), jamais la trame.** 9000 trames par bras ne sont
   pas 9000 observations.
5. **Autocorrélation temporelle.** Quantifier la dépendance série de `Q` et en tenir compte dans
   toute incertitude au niveau du monde.
6. **Épisodes `Q = 0`.** Fréquence, durée, distribution des longueurs. La réparation a mesuré
   `P(Q=0)` à 0,6470 en statique et 0,5428 en mobile : les épisodes nuls dominent et leur
   structure décide de la validité de toute moyenne.
7. **Moyenne par monde et exposition de queue basse.** Ce qui compte pour une borne inférieure
   n'est pas `E[Q]` mais un quantile bas au niveau du monde.
8. **Relation entre `Q` et ses composantes** : trajectoire de la source, capacité libre, `nX`,
   `nSY`. Les champs `u_nX_at_org`, `nSX_at_org`, `nSY_at_org`, `free_at_org`, `cand_Y_at_org`
   sont tous enregistrés et doivent être exploités.
9. **Traitement exact du clamp** `p = min(1, kY · nX · nY)`. Le régime linéaire n'est valable que
   sous `kY · nX · nY ≤ 1` ; au-delà, la saturation change l'opérateur.
10. **`β = kY · E[Q]` suffit-il ?** Vérifier explicitement si la moyenne suffit ou si l'opérateur
    complet conditionné au temps (PGF par état) est requis. `Q` est corrélé en temps et fortement
    nul ; la substitution par la moyenne est une hypothèse, pas une identité.
11. **Incertitude au niveau du monde**, propagée jusqu'à la borne proposée.
12. **Aucune entrée dérivée d'un résultat `Y`.** `Q` est un covariable environnemental ; `r80`,
    `nY_final` et toute observable de sortie `Y` restent interdits.
13. **Aucune sélection de bras favorables.**
14. **Aucune construction ni rejeu du moteur scientifique.** Sentinelle obligatoire, agrégée sur
    tous les processus, avec témoin système de fichiers sur **toutes** les racines de sortie.
15. **Statut de découverte des 28 bras déclaré explicitement** dans chaque artefact.

## 5. Dispositions terminales admissibles

Exactement une :

```
EXISTING_Q_DATA_SUPPORTS_DISCOVERY_DERIVED_EXECUTABLE_Y_REGION
EXISTING_Q_DATA_INSUFFICIENT__PROSPECTIVE_Q_CALIBRATION_REQUIRED
EXISTING_ENVIRONMENT_OPERATOR_STRUCTURALLY_PRECLUDES_WINDOW
```

**Si la première passe** : créer — sans l'exécuter — un test frais de fenêtre `Y`
prospectivement gelé.

**Si la deuxième passe** : créer — sans l'exécuter — un handoff de calibration prospective de `Q`
comportant :

- des mondes neufs et indépendants ;
- la branche exacte (statique ou mobile) ;
- des graines gelées ou une règle de génération de graines gelée ;
- horizon et burn-in gelés ;
- un registre `Q` exact ;
- une borne de confiance inférieure **au niveau du monde** ;
- le traitement explicite de la dépendance temporelle ;
- aucun retune adaptatif ;
- des mondes de calibration **disjoints** des mondes du test `Y` ultérieur.

**Seule la troisième** peut réactiver la conception d'architecture, et uniquement si l'**opérateur**
— et non une simple incertitude large — démontre une impossibilité structurelle.

## 6. Points d'attention hérités

- **Un zéro structurel n'est pas un petit nombre.** `inf Q = 0` porte sur l'ensemble des états ;
  `E[Q] = 0` porterait sur la mesure. Ne pas les confondre, dans un sens ni dans l'autre.
- **Une ablation n'est un mécanisme que si elle est répliquée** (leçon OBFOR01).
- **Toute prédiction se publie avec son σ.**
- **Aucune règle d'inclusion ne doit conditionner sur un résultat** (leçon OBFOR01 : `nX_final ≥ 40`
  déplaçait la valeur de tête de plusieurs points).
- **Le critère de décision se gèle en entier, forme comprise**, avant les bras.
- **Toute revendication doit être opposée à un témoin sans physique** construit avant les runs.
- **Ne pas présenter un contrôle vide comme un contrôle** : un scan qui ne peut rien trouver n'est
  pas une preuve (leçon PMCR01 : le scan `Assert`/`Raise` sur des fichiers en contenant zéro).

## 7. Statuts à reporter inconditionnellement

```
H3_STATUS                  = NOT_TESTED
REPRODUCTION_STATUS        = NOT_TESTED
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED
HISTORICAL_WINDOW_STATUS   = NOT_PORTABLE
X_LAWSPEC_BASELINE         = UNCHANGED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
SCIENTIFIC_RUNS_USED       = 0
TOMMY_ACTION_REQUIRED      = NONE
```
