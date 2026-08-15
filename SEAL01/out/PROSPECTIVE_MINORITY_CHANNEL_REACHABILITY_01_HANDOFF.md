# ISING LIFE LAB — HANDOFF
## PROSPECTIVE-MINORITY-CHANNEL-REACHABILITY-01
## PMCR01 — atteignabilité exécutable d'un canal minoritaire, zéro run

> Produit par `OBFOR01-CONFIRMATORY-PROVENANCE-AND-CLAIM-SEAL-01`, après revue adverse et
> tour de réparation.
> **Ne pas exécuter dans la session du sceau.**

```
OWNER                = Tommy
REPOSITORY           = Mythmaker28/emergent-dynamics-lab
PARENT_PROGRAM       = ORGANIZER-BOUND-FULL-OPERATOR-RESIDUAL-01
PARENT_TIP           = 55e8812eee7ca48a8eb16cb439e3812a69bfc971
PARENT_DISPOSITION   = CONDITIONAL_FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_QUALIFIED
                       (scellé, voir OBFOR01_CONFIRMATORY_CLAIM_SEAL_REPORT.md)
SHORT_NAME           = PMCR01
INITIAL_ENGINE_STARTS = 0
NEW_SEEDS_INITIALLY  = 0
RETUNE               = forbidden
TOMMY_ACTION_REQUIRED = NONE
```

## 0. Verser ce texte dans le dépôt avant toute autre action

Le sceau n'a pas pu certifier la conformité de budget d'OBFOR01 parce que le mandat qui la
gouvernait n'était nulle part dans l'arbre. **Premier commit de PMCR01** : ce fichier, ou son
SHA-256, versé dans le dépôt. Sans cela, la même invérifiabilité se reproduira.

## 1. Sur quoi exactement cette mission est éligible

Ce que le sceau a établi, dans ces termes et pas d'autres :

- L'opérateur source–transport–décroissance a **énoncé à l'avance** trois prédictions ponctuelles
  que 28 graines fraîches **n'ont pas falsifiées**, dans une marge gelée de ±2,9 %.
- À l'intérieur de ce même test, la **trajectoire organisatrice partagée est requise** : la
  retirer manque l'observation mobile de −3,55 %, l'idéal non corrigé la manque de −5,46 %.
- La prédiction est **conditionnelle** à une loi de flux de naissance mesurée, sur fondement
  dérivationnel : le modèle ne dérive pas la source, on la lui remet.

Ce que le sceau a **explicitement refusé** d'établir, et qu'il ne faut donc pas hériter :

- que l'opérateur « prédit prospectivement » au sens d'un pouvoir discriminant — un **témoin sans
  physique** (« les bras frais ressembleront aux bras historiques ») passe les trois mêmes
  critères ;
- que la prédiction est sans paramètre ajusté ;
- que le critère statique discrimine quoi que ce soit ;
- que la conformité de budget de la mission parente soit vérifiable.

C'est la partie **mécanistique** — la trajectoire partagée est requise — qui autorise à
*concevoir* un second temps indépendant. Pas la partie prédictive.

Ce qui reste interdit et le demeure : réutiliser la fenêtre `Y` historique, revendiquer une
reproduction, une hérédité ou une cohésion autonome, retuner un paramètre, ou tester H3.

## 2. Objectif

Déterminer, **sans exécuter le moteur**, s'il existe une région **exécutable** et non vide de
persistance minoritaire pour `Y`, et si les paramètres `k_Y` et `µ_Y` sont des **chemins actifs
constructeur → ordonnanceur** plutôt que des champs inertes.

## 3. Ordre de travail imposé

1. **Atteignabilité paramétrique exécutable.** Avant toute algèbre, tracer dans le code, depuis
   le constructeur du `Spec` jusqu'à l'appel effectif dans `_one_step`, ce que `k_Y` et `µ_Y`
   pilotent réellement. Produire le graphe d'appel et le statut :
   `K_Y_PATH = ACTIVE_CONSTRUCTOR_TO_SCHEDULER` / `INERT_FIELD` / `PARTIALLY_WIRED`,
   et de même pour `MU_Y_PATH`. Un paramètre inerte rend toute fenêtre abstraite sans objet.
2. **Distinguer l'intervalle abstrait de l'intervalle exécutable.** L'intervalle historique
   `(0 ; 1,787×10⁻⁴)` est abstrait. Un intervalle **exécutable** est l'ensemble des valeurs que
   le moteur peut réellement réaliser compte tenu de la discrétisation binomiale, de la capacité
   `CAP`, du plafond `Q_max = 28` et de l'horizon. Les deux ne coïncident pas et ne doivent
   jamais être confondus.
3. **Opérateur discret de génération suivante pour `Y`.** Dériver exactement, dans
   l'environnement de réponse de source **désormais qualifié**, l'opérateur de génération
   suivante de `Y` : naissance `min(n_SY, free)·p_Y`, mort `Binomial(n_Y, µ_Y)`, transport par le
   noyau exact déjà validé. Donner son rayon spectral et le seuil de persistance.
4. **Chercher une région non vide sans retuner.** Balayer analytiquement `(k_Y, µ_Y)` à LawSpec
   `X` **inchangé**, celui-ci servant de ligne de base de contrôle. Aucun autre paramètre ne
   bouge.
5. **Préenregistrer, sans l'exécuter**, une expérience fraîche ultérieure **uniquement** si une
   région exécutable non vide est prouvée.

## 4. Points d'attention hérités, à ne pas réapprendre à ses dépens

**Sur la physique**

- **La règle de résumé est un mécanisme, pas un détail.** Une médiane intra-graine d'un quantile
  de premier franchissement biaise de plusieurs pour cent, et le biais dépend de la condition.
  Toute observable primaire de PMCR01 doit être une moyenne par particule ou une fonction
  exactement débiaisée.
- **La densité marginale ne se ferme pas.** Le flux de naissance vaut `min(n_SX, free)` local à
  86,7 % des pas. Prédire des observables ne veut pas dire disposer d'une équation d'évolution.
- **La prédiction héritée est conditionnelle** à une loi de flux mesurée. Si PMCR01 veut une
  prédiction inconditionnelle, il devra **dériver** le flux depuis le chémostat, pas le mesurer.
  Note utile : le résidu mobile s'est révélé **invariant** à un doublement de l'intensité de la
  source (+0,01 ± 0,23 pt, nuage vérifié doublé). La dépendance à la source est dérivationnelle,
  pas numérique.
- **Un zéro structurel n'est pas un petit nombre.** `k_Y = 0` retire un canal ; il ne le rend pas
  faible.

**Sur la méthode — cinq règles issues des six défauts corrigés dans le sceau**

1. **Une ablation n'est un mécanisme que si elle est répliquée.** Une différence unique entre
   deux runs de 30 bras dont l'écart-type de réplique vaut 0,56 point ne soutient pas un effet de
   1,27 point. Répliquer avant d'interpréter, toujours.
2. **Toute prédiction se publie avec son σ Monte-Carlo.** Une prédiction ponctuelle assortie d'un
   σ non déclaré n'est pas un point.
3. **Aucune règle d'inclusion ne doit conditionner sur un résultat.** `nX_final ≥ 40` sélectionne
   sur la population terminale et déplace la valeur de tête de plusieurs points. Les critères
   d'inclusion de PMCR01 doivent être fixés sur des variables de conception, gelés, et leur
   sensibilité publiée.
4. **Le critère de décision se gèle en entier, forme comprise** : point ou intervalle, niveau de
   confiance, loi de référence et degrés de liberté. Écrire le code qui l'évalue **avant** les
   bras, pas après. Une erreur-type à 13 ddl se lit sur une loi de Student.
5. **Toute revendication doit être opposée à un témoin sans physique** construit avant les runs.
   Si le témoin passe, le plan ne discrimine pas et la revendication doit le dire.

## 5. Dispositions terminales admissibles

Exactement une :

```
REACHABLE_NONEMPTY_Y_WINDOW_DERIVED
NO_MINIMAL_REACHABLE_Y_CHANNEL
STOP__ARCHITECTURE_CHANGE_REQUIRED
```

## 6. Statuts à reporter inconditionnellement

```
H3_STATUS                  = NOT_TESTED
REPRODUCTION_STATUS        = NOT_TESTED
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED
HISTORICAL_WINDOW_STATUS   = NOT_PORTABLE
X_LAWSPEC_BASELINE         = UNCHANGED
SCIENTIFIC_RUNS_USED       = 0
TOMMY_ACTION_REQUIRED      = NONE
```
