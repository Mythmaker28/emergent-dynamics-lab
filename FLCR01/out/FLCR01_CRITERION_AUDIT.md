# FLCR01 — AUDIT DE CRITÈRE
## Survie du fondateur, ou continuité de la lignée ?

## 1. La contradiction, d'abord — elle précède toute donnée

Les critères gelés de PQEC01 s'éliminent algébriquement :

```
C1        : kY · E · W ≥ 1
C2_FONDER : (1 − muY)^11000 ≥ 0,5
C3        : kY · E · W · (1 − muY)^τ ≤ 0,5

C1 ∧ C3  ⟹  (1 − muY)^τ ≤ 0,5   ⟹   muY ≥ 1 − 0,5^(1/τ)
C2_FONDER                        ⟹   muY ≤ 1 − 0,5^(1/11000) = 6,301×10⁻⁵
```

**`kY` et l'exposition `E` se simplifient.** Il ne reste qu'une contrainte sur `muY` seul :

| `τ_sep` | `muY` ≥ (C1 ∧ C3) | `muY` ≤ (C2) | compatible | facteur |
|---|---|---|---|---|
| 83 | 8,316×10⁻³ | 6,301×10⁻⁵ | **non** | **132,0** |
| 111 (mesuré) | 6,225×10⁻³ | 6,301×10⁻⁵ | **non** | **98,8** |
| 125 (gelé) | 5,530×10⁻³ | 6,301×10⁻⁵ | **non** | **87,8** |

Indépendance vérifiée : en balayant l'exposition sur quatre décades (`E` de 0,01 à 100), la marge
maximin reste à **−0,1508 décade**. Elle ne bouge pas parce qu'elle ne dépend pas de `E`.

```
FOUNDER_GATE_REGION = EMPTY_FOR_ALL_kY_AND_ALL_EXPOSURE
```

**PQEC01 ne pouvait pas produire de région candidate positive sous ses critères gelés, quelles que
soient les données.** La marge observée n'est pas la confirmation d'une mesure : c'est la valeur
d'une identité qui n'a jamais dépendu de la mesure.

**Où est le conflit.** `C2_FONDER` exige que la particule `Y` **initiale** survive 11 000 pas,
tandis que `C3` exige qu'un `Y` **nouveau-né** soit mort en `τ` pas pour qu'aucun second centre ne
se forme. Les deux passent par le **même scalaire `muY`**, qui s'applique identiquement à tout `Y`.
La porte demande à un seul paramètre d'être simultanément minuscule et grand.

**L'erreur plus profonde.** `C3` interdit un second centre séparé alors que l'objectif scientifique
est précisément que **deux** centres organisateurs apparaissent et persistent. Le jeu de critères
ne se contredit pas seulement numériquement — **il s'oppose à la chose qu'il a été écrit pour
détecter**.

## 2. Quatre critères, comparés sur le sens scientifique

L'objet scientifique est : **la persistance d'une lignée organisatrice à travers le renouvellement
matériel** — pas la préservation d'un identifiant de particule arbitraire.

| critère | nécessaire | suffisant | invariant au renouvellement | exige une généalogie | le moteur agrégé peut l'identifier |
|---|---|---|---|---|---|
| **Survie du fondateur** | **non** | non | **non** | **oui** | seulement tant que `nY = 1` |
| **Non-extinction de la lignée** | oui | non | oui | non | oui (`N_Y > 0`) |
| **Continuité de l'organisateur** | oui | non | oui | non | oui (grappe + réponse `X` locale) |
| **Continuité fonctionnelle à deux centres** | oui | **oui** | oui | non | oui |

**Pourquoi la survie du fondateur est rejetée.** Le nuage `X` se renouvelle déjà intégralement ;
tout le programme porte sur une structure qui persiste pendant que sa matière est remplacée. Exiger
qu'une particule étiquetée persiste impose à `Y` exactement la propriété que le projet nie exiger
de `X`. C'est un critère d'**identité de particule** portant une étiquette organisationnelle.

**Cet argument ne dépend d'aucune région.** Il tiendrait même si la survie du fondateur admettait
une large région. Le critère n'est pas choisi parce qu'il crée une région : il est choisi depuis
l'objet testé.

**Si l'identité du fondateur était réellement essentielle**, ce serait pour une revendication
portant sur un *individu* plutôt que sur une lignée — « cet organisateur-ci a survécu à une
perturbation ». Aucune revendication de ce type n'est dans le périmètre, et le programme interdit
de toute façon les revendications de reproduction et d'hérédité.

## 3. Aucune généalogie inventée

Le moteur tire `births = Binomial(min(nSY, free₀), min(1, kY·nX·nY))` **par cellule**. Dans une
cellule multiplement occupée, aucun observateur ne peut dire quel `Y` a produit la naissance.

**Aucun des trois critères retenus n'en a besoin.** Tous sont des fonctions du compte total, de
l'occupation cellulaire, de la structure de grappe et des champs locaux — tous enregistrés à chaque
pas. Les états opérationnels sont :

```
E  EXTINCT                            O  ONE_ORGANISING_CENTRE
C  TWO_OR_MORE_Y_COLOCATED_ONE_CENTRE S  TWO_SPATIAL_CENTRES
P  THREE_OR_MORE_SPATIAL_CENTRES      F  ORGANISER_INTEGRITY_FAILURE
```

Là où une généalogie serait nécessaire, elle est déclarée **non identifiable**, jamais imputée.

```
CRITÈRE PRIMAIRE RETENU   = TWO_CENTRE_FUNCTIONAL_CONTINUITY
CRITÈRE DE SOUTIEN        = LINEAGE_NON_EXTINCTION
SURVIE DU FONDATEUR       = REJECTED_AS_A_GATE
```
