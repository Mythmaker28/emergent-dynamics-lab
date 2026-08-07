# ANTI_STAGNATION_ROUTE_E_FEASIBILITY_SWEEP_00 — rapport

**2026-08-07** · balayage DEV exécuté · aucun run primaire, aucune reproduction, holdout fermé
· 0 fichier de production modifié · 0 nouveau document d'audit.

---

## 1. Substrat

Le checkout local (`f3921a4d`, 15 juillet) était bien une branche périmée. Le dernier tip
authentique est **`7e6faeb173a6a2692a541dc0006c75a3972b08d1`**, porté **uniquement** par
`route-e-empty-right-nonunit-disk-closure.bundle` (sha256 `b3be0a5f…6670`, vérifié) — il est
**absent de la base d'objets locale**. Lignée reconstituée et vérifiée :

```
199f29eb → fb83059 → c17712b → f069d33 → 7e6faeb
```

Elle recoupe exactement les GO/NO-GO 00 (`c17712b`) et 01 (`f069d33`) déjà enregistrés. Le
tip a été monté en lecture seule via un dépôt temporaire et des alternates ; **le worktree
de Tommy n'a pas été touché**.

## 2. Question et paramètre de contrôle

Le pilote (48/48 mécaniquement inéligibles) a une occupation de **0,55 par construction, pas
par accident** : l'IC de production tire `m ~ U(0,1)` en dur et le détecteur seuille à `0,45`,
donc `P(m ≥ 0,45) = 0,55` exactement. **Aucun champ de `LatticeBondSpec` ne contrôle
l'occupation.**

Le paramètre de contrôle utilisé est donc l'IC elle-même, via une carte de quantile monotone
à un seul paramètre. Propriété utile : **à `p = 0,55` la carte est l'identité**, donc ce bras
est *bit-identique* à l'IC de production — le balayage contient le régime du pilote comme cas
exact, vérifié `np.array_equal` sur L = 16/24/32.

## 3. Autopsie du pilote (rejouée sur ses artefacts authentiques)

| Grandeur | Valeur publiée |
|---|---|
| Cause d'inéligibilité | **`WRAPPING_COMPONENT_PRESENT`, 48/48** — jamais le résidu |
| Enroulement à t0 | 6/48 ; le reste apparaît à la frame 16 (33), 32 (7), 48 (2) |
| `labelled_fraction` (t0) | médiane **0,748**, étendue [0,671 ; 0,811] |
| Conservation cohorte/matière | dérive max **3,3 × 10⁻¹⁶** |
| Coût | **299,4 s** de temps mural pour les 48 mondes |

Deux conséquences importantes.

**(a)** Le monde est tué en 1,5 – 4,7 % de son horizon, par l'enroulement, *avant* que la
convention de résidu ait la moindre occasion de s'appliquer. Le résultat « 48/48 » n'a jamais
été un test de remplacement matériel.

**(b)** `_enrolled_cohort` enrôle **l'union de tous les composants détectés**. Comme la matière
et la cohorte sont exactement conservées, le mélange pousse tout rapport local vers le rapport
global : **le résidu est plancheré par `labelled_fraction`**. À 0,75, `f = 0,20` est
arithmétiquement hors d'atteinte quelle que soit la dynamique. La docstring du code nomme la
limite dégénérée (enrôler tout le champ donne un résidu ≡ 1) sans voir qu'enrôler 75 % en est
à 5 points.

## 4. Balayage exécuté

864 mondes DEV (720 + 144 en raffinement), tous passés par le **pont de mesure de production**
— détecteur, tracker et calcul du résidu non modifiés, aucune approximation substituée.
Occupation réalisée **0,008 → 0,670**. Quatre bras à cardinalité égale : `ROUTE_E`,
`SHUFFLED`, `COMPACT_ISLANDS` (contrôle positif), `SPANNING_BAND` (contrôle négatif).

### Vérification différentielle 1 — reproduction du pilote · **PASS**

Au bras `p = 0,55` (IC bit-identique) : `labelled_fraction` médiane **0,7520** contre **0,7483**
publiée ; taux d'enroulement **1,00** contre **1,00**. Le harnais reproduit le pilote.

### Vérification différentielle 2 — ma propre prédiction · **FALSIFIÉE, puis expliquée**

J'avais prédit `résidu ≥ labelled_fraction`. Violée dans **60/529** cas, jusqu'à 0,60 d'écart.
Diagnostic : **60/60 de ces mondes ont `ncEnd = 0`** — le composant se dissout, perdant sa
cohorte marquée juste avant de disparaître. Ce n'est pas du remplacement matériel, c'est un
`DISSOLVED_DETECTED_TRACK`, que le prédicat gelé classe en échec observé. **Mon critère
d'atteignabilité était trop permissif et la « bande candidate » à p ∈ {0,20 ; 0,35} était un
artefact de dissolution.** C'est la passe de raffinement unique qui l'a corrigé.

### Raffinement (passe unique, horizon **gelé 1024**)

| Bras | n | dissous | persistants | PASS f = 0,20 / 0,05 / 0,01 |
|---|---|---|---|---|
| `ROUTE_E` | 72 | **72/72** | **0** | 0 / 0 / 0 |
| `COMPACT_ISLANDS` (contrôle +) | 72 | **71/72** | 1 | 0 / 0 / 0 |

Le seul monde persistant (îlots, p = 0,35, L = 32) finit à un résidu de **0,730** pour un
plancher de 0,600 : il échoue la porte de très loin.

## 5. Le résultat : une pince, pas un seuil

- **Occupation ≳ 0,45** : enroulement dynamique → `MECHANICALLY_INELIGIBLE`. Taux 0,67 → 1,00.
- **Occupation ≲ 0,35** : dissolution totale avant l'horizon gelé → aucun composant persistant,
  donc aucun positif possible.
- **Entre les deux** : à h = 256 une fenêtre *transitoire* apparaît (jusqu'à 48 % de mondes
  survivants et bornés à L = 32, p ≈ 0,35) — **elle se referme entièrement à l'horizon gelé
  1024**. C'était un artefact d'horizon, pas une bande.

Borne de Wilson conservatrice à 95 % sur le taux de passage à `f = 0,20`, sur les 144 mondes
au format gelé : **0,0000**.

La densité seule n'explique donc rien : baisser l'occupation ne produit pas des mondes
éligibles, elle **remplace un mode d'échec par l'autre**. Mon hypothèse initiale — « occupation
proche de `p_c` ⇒ pas d'entités bornées » — est **réfutée dans le domaine balayé**. `p_c ≈ 0,593`
n'est de toute façon qu'un repère i.i.d. sans validité pour ce champ dynamique corrélé, et
n'est pas utilisé comme explication ici.

La morphologie, elle, **change le mode d'échec** : à cardinalité égale, `COMPACT_ISLANDS`
n'enroule jamais (0,00 à tous les niveaux) là où `ROUTE_E` enroule dès 0,35 — mais elle ne
produit toujours aucun passage. La porte de mesure est **cohérente** : elle ne rejette aucun
cas positif évident, parce qu'aucune entité bornée persistante n'a jamais été produite.

## 6. Limitation déclarée dominante

**Le balayage fait varier l'occupation à loi fixe** (`dt = 1,0`, reste aux défauts gelés) ;
**le pilote fait varier la loi à occupation fixe**. Aucun des deux ne fait varier les deux.
La conclusion ferme donc l'occupation comme sauvetage à un paramètre **pour cette loi**, et
rien de plus. Elle ne réfute pas la convention universellement.

C'est le point qui compte pour la suite : `NONMERGING_CONFIRM_02` **a** produit des gouttelettes
bornées persistantes non fusionnantes (23/23 mondes valides, 0 fusion, couverture ≤ 5,6 %). Ce
régime existe — dans une *autre* famille de lois. L'axe suivant est donc la loi, pas la densité.

Autres limitations, non susceptibles de changer le signe : horizon 256 pour le balayage large
(le raffinement décisif est à 1024) ; `SHUFFLED` dégénéré à t0 puisque l'IC de production est
déjà i.i.d. ; mondes d'un même niveau non indépendants ; atteignabilité mesurée comme borne
supérieure sans identité de piste.

## 7. Décision

```
DECISION = NO_ONE_PARAMETER_RESCUE_OBSERVED_IN_SCANNED_RANGE
```

L'occupation ne sauve pas Route E dans `[0,008 ; 0,670]` pour cette loi. La convention n'est
**pas** déclarée universellement réfutée. La prochaine hypothèse porte sur la famille de lois,
pas sur la densité.
