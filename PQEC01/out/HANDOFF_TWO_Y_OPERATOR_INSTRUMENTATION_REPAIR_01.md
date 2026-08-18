# ISING LIFE LAB — HANDOFF
## TWO-Y-OPERATOR-INSTRUMENTATION-REPAIR-01 (TYOIR01)
## Réparation d'instrumentation **étroitement délimitée** — pas une troisième calibration

> Produit par `PROSPECTIVE-Q-ENVIRONMENT-CALIBRATION-01` après une relecture adversariale unique
> et l'unique round de réparation autorisé. Disposition parente :
> `PROSPECTIVE_Q_ENVIRONMENT_OPERATOR_NOT_IDENTIFIED__ADDITIONAL_INSTRUMENTATION_REQUIRED`.
> **Ne pas exécuter dans la session PQEC01. Ce n'est pas une calibration générique.**

```
PARENT_PROGRAM        = PROSPECTIVE-Q-ENVIRONMENT-CALIBRATION-01
ARCHITECTURE_CHANGE   = forbidden
NEW_SPECIES           = forbidden
ENGINE_PHYSICS_CHANGE = forbidden
X_LAWSPEC_BASELINE    = UNCHANGED
TOMMY_ACTION_REQUIRED = NONE
```

## 0. Ce qui manque, exactement — trois objets nommés, rien d'autre

PQEC01 a **enregistré** l'exposition locale de descendants réels (56 naissances, 34 mondes
atteignant deux centres, 92 649 pas d'état séparé mesuré). Ce qui bloque l'identification n'est
donc **pas** la donnée spatiale — c'est trois objets précis.

### Objet 1 — le sous-opérateur à deux `Y` n'est pas **conditionné**

Le test de validation prédéclaré n° 2 passe en B1 (`z = +1,16`) et **échoue en B2**
(`z = −2,82`) : les mondes de découverte passent 19,66 % des pas avec `nY ≥ 2`, les mondes de
validation 4,53 %. Un sous-opérateur qui généralise à un point de paramètres et pas à l'autre
n'est pas identifié.

**Variables de conditionnement manquantes, à enregistrer et à porter dans les états :**

```
classe d'exposition de la cellule de naissance à l'instant de la première naissance
temps écoulé depuis la première naissance
déplacement relatif du descendant par rapport à la source au moment où la co-localisation cesse
```

TYOIR01 doit **redéfinir l'espace d'états** en produit `{ONE_Y, TWO_Y_COLOCATED,
TWO_Y_SEPARATED, EXTINCT, PREMATURE_THIRD_CENTRE} × {classe d'exposition} × {âge de lignée
discrétisé}`, et geler ce découpage **avant** tout run.

### Objet 2 — un canal d'identité indexé par descendant est **impossible sans toucher la physique**

Le moteur tire `births = Binomial(min(nSY, free0), min(1, kY·nX·nY))` **par cellule**. Dans une
cellule multiplement occupée, aucun observateur ne peut dire quel `Y` a produit la naissance —
c'est `SHARED_PARENT_POOL`, et PQEC01 ne l'a jamais inventé. L'âge de lignée exigé par l'objet 1
n'est donc **pas** observable en général.

**Ce que TYOIR01 doit faire :** définir l'âge de lignée sur ce qui **est** identifiable — l'âge
d'une **cellule occupée** depuis sa dernière transition d'occupation, et l'âge du **centre**
depuis sa formation — puis **démontrer** que le sous-opérateur conditionné sur ces substituts
observables généralise, ou déclarer qu'il ne le peut pas. **Ne pas** inventer de parent.

### Objet 3 — la rétroaction de `Y` sur `X` est **grande et non modélisée**

Conditionnellement à ce qu'une naissance ait eu lieu, `N_X` est supérieur de **+61,0 %**
(`z = +5,65`) en B1 et **+51,9 %** (`z = +5,88`) en B2 par rapport à la Phase A, avec une
dépletion concordante de `nSY` (`z = −5,92` et `−6,00`). L'analyse groupée de PQEC01 masquait cet
effet par un paradoxe de Simpson (+11,9 % / +15,2 %, `z ≈ 1,3–1,8`, « non significatif »).

**Mécanisme, architectural et non stochastique :** `kX = 1,0`, donc `p_X = min(1, kX·nX·nY)` vaut
déjà 1 dès que `nX·nY ≥ 1`. Un second `Y` sur une cellule **différente** ajoute donc une seconde
source `X` saturée au lieu d'entrer en compétition avec la première : la production de `X`
double approximativement.

**Ce que TYOIR01 doit faire :** intégrer un canal de production `X` **conditionné sur la
configuration `Y`** (nombre de centres, séparation) dans l'opérateur, ou en borner l'effet.
Toujours **stratifier** par présence de naissance ; ne jamais regrouper.

## 1. Précondition bloquante — les critères de fenêtre sont incompatibles par construction

Avant toute nouvelle instrumentation, ce point doit être tranché par le propriétaire du gel.
Les critères gelés hérités s'éliminent algébriquement :

```
C1 : kY·E·T_WINDOW >= MIN_EVENTS
C3 : kY·E·T_WINDOW·(1-muY)^tau <= GAMMA_SEP
C1 & C3  =>  muY >= 1 - (GAMMA_SEP/MIN_EVENTS)^(1/tau) = 6,225e-3   (tau = 111 mesuré)
C2       =>  muY <= 1 - (1-ALPHA_SURVIVAL)^(1/T_HORIZON) = 6,301e-5
```

`kY` et l'exposition **disparaissent**. Les deux bornes sont incompatibles d'un facteur **98,8**
(87,8 à `tau = 125` gelé). Autrement dit : **le fondateur doit survivre 11 000 pas** (donc `muY`
minuscule) **tandis qu'un nouveau-né doit mourir en ~111 pas** pour qu'aucun second centre ne se
forme (donc `muY` grand) — **le même paramètre**, pour deux usages opposés.

Aucune calibration, aucune instrumentation et aucune quantité de données ne peut rendre cette
région non vide sous ces critères. TYOIR01 doit donc, **avant tout run** :

- soit **découpler** les deux rôles de `muY` — conditionner la formation d'un second centre sur
  une condition spatiale ou de capacité plutôt que sur la mort du descendant ;
- soit **déclarer explicitement** que la fenêtre gelée est inatteignable par construction, et
  arrêter là.

**Ce n'est pas** `EXISTING_ARCHITECTURE_FEEDBACK_PRECLUDES_CONTROLLED_WINDOW` : ce n'est pas un
résultat de rétroaction, c'est une incompatibilité entre deux **critères d'acceptation**.

## 2. Exigences de méthode héritées, renforcées par ce qui a échoué

- **Geler le code d'analyse AVEC le design, dans le même commit, et le hacher.** PQEC01 a haché
  la conception mais pas l'exécuteur ni l'analyseur, écrits après le gel. Deux correctifs
  d'analyse ont dû être appliqués **après** que des sorties de validation existaient — l'un a fait
  passer un test de ÉCHEC à SUCCÈS. La disposition n'a pas bougé et les deux jeux de chiffres sont
  publiés, mais un gel qui couvre l'analyse rend ce débat inutile.
- **Vérifier qu'un contrôle se déclenche.** Le contrôle d'équivalence de source de PQEC01 était
  insensible à l'ordre : il acceptait un bloc de compteurs déplacé après un `continue`. Il est
  désormais séquentiel avec trois contrôles négatifs. **Tout contrôle livré doit venir avec la
  preuve qu'il échoue quand il le doit.**
- **Ne jamais grouper là où une strate change le signe** (leçon de l'objet 3).
- **L'unité est le monde.** Jamais la trame, la cellule ou la ligne d'événement.
- **Dimensionner sur la dispersion mesurée, pas héritée.** PQEC01 a visé 0,81 % d'erreur-type
  relative depuis la dispersion à 14 bras du parent et en a obtenu 4,27 % : la dispersion réelle
  au niveau du monde est **4,76×** plus grande, parce que **2 mondes frais sur 40** ont vu leur
  nuage `X` s'effondrer — un mode d'échec absent des bras développementaux.

## 3. Dispositions terminales admissibles

```
TWO_Y_OPERATOR_IDENTIFIED_WITH_OBSERVABLE_CONDITIONING
TWO_Y_OPERATOR_NOT_IDENTIFIABLE_WITHOUT_PHYSICS_CHANGE
FROZEN_WINDOW_CRITERIA_UNREACHABLE_BY_CONSTRUCTION
INSTRUMENTATION_REPAIR_TECHNICALLY_INVALID
```

## 4. Statuts à reporter inconditionnellement

```
H3_STATUS                     = NOT_TESTED
REPRODUCTION_STATUS           = NOT_TESTED
HEREDITY_STATUS               = NOT_TESTED
AUTONOMOUS_COHESION_STATUS    = NOT_ESTABLISHED
X_LAWSPEC_BASELINE            = UNCHANGED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
TOMMY_ACTION_REQUIRED         = NONE
```
