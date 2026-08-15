# ISING LIFE LAB — HANDOFF
## PROSPECTIVE-MINORITY-CHANNEL-REACHABILITY-01
## PMCR01 — atteignabilité exécutable d'un canal minoritaire, zéro run

> Produit par `OBFOR01-CONFIRMATORY-PROVENANCE-AND-CLAIM-SEAL-01`.
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

## 1. Pourquoi cette mission est éligible, et à quoi elle ne l'est pas

Le sceau a établi que l'opérateur source–transport–décroissance prédit **prospectivement** trois
observables de réponse de source sur graines fraîches, à ±2,9 %, **conditionnellement** à une loi
de flux de naissance mesurée et gelée. C'est cette capacité prédictive — et rien d'autre — qui
autorise à *concevoir* un second temps indépendant.

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

- **La règle de résumé est un mécanisme, pas un détail.** Une médiane intra-graine d'un quantile
  de premier franchissement biaise de plusieurs pour cent, et le biais dépend de la condition.
  Toute observable primaire de PMCR01 doit être une moyenne par particule ou une fonction
  exactement débiaisée.
- **La densité marginale ne se ferme pas.** Le flux de naissance vaut `min(n_SX, free)` local à
  86,7 % des pas. Prédire des observables ne veut pas dire disposer d'une équation d'évolution.
- **La prédiction héritée est conditionnelle** à une loi de flux mesurée. Si PMCR01 veut une
  prédiction inconditionnelle, il devra dériver le flux depuis le chémostat, pas le mesurer.
- **Un zéro structurel n'est pas un petit nombre.** `k_Y = 0` retire un canal ; il ne le rend pas
  faible.

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
