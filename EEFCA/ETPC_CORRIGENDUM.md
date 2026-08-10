# CORRIGENDUM — `EXACT_TWIN_PUBLIC_PATH_COUNTERFACTUAL_00`

**Émis par** `EXACT_ENDPOINT_FUNCTIONAL_CONGRUENCE_AUDIT_00` (portée : `AUDIT_ONLY`).
**Commit parent** `3f8dae8bbe2937c43661ba8adfe8aed63bf6b6ee`.
**Nature** : ajout en annexe. **Aucune sortie, aucun gel, aucun scellé du parent n'est réécrit.**
**Démarrages moteur de cet audit** : `0`. **Nouvelles trajectoires** : `0`.

L'auteur d'ETPC et l'auteur de cet audit sont le même agent. Tout ce qui suit est
contradictoire contre son propre travail antérieur.

---

## B1 — Registre exact des démarrages moteur du parent

| poste | démarrages |
|---|---|
| R2 fondateur | 1 |
| R3 non-interrompu + reprise | 2 |
| R5 paire de jumeaux + deux forks | 4 |
| R8 paire OFF | 2 |
| R9 paire d'ordre + référence in-process + processus séparé | 4 |
| R10 deux fondateurs + deux rejeux | 4 |
| **sous-total qualification** | **17** (plafond autorisé 24) |
| 10 blocs × (1 fondateur + 4 bras) | 50 |
| relances, plantages, blocs abandonnés | **0** |
| **TOTAL** | **67** (plan 124, plafond absolu 160) |

Le total réconcilie exactement avec le chiffre rapporté. Aucun démarrage caché.

---

## B2 — L'opérateur : ce qui a été autorisé, ce qui a été scellé, ce qui a été exécuté

L'opérateur exécuté agit sur le couple de moyennes `(z̄_A, z̄_B)` par la matrice

```
P = [[1−a,   a  ],
     [ b,   1−b ]]        a = m*/M_A ,  b = m*/M_B ,  m* = min(M_A, M_B)
```

Mesuré sur les dix blocs primaires, à partir des seuls scalaires déjà commis :

| grandeur | intervalle observé sur 10 blocs |
|---|---|
| `a` | 0,908722 … 1,000000 |
| `b` | 0,926305 … 1,000000 |
| `det P = 1 − a − b` | −0,974704 … −0,908722 |
| valeurs propres | `{1, 1−a−b}` |
| facteur de contraste après **deux** applications `(1−a−b)²` | 0,8258 … 0,9500 |
| `P² = I` ? | **faux dans les dix blocs** |

Le contraste `z̄_A − z̄_B` est multiplié par `(1−a−b)` à chaque application. Deux applications
le multiplient donc par `(1−a−b)² ≠ 1`. **L'application n'est pas involutive.**
Un inverse analytique exact stocké n'est pas une preuve d'involution : ce sont deux propriétés
différentes, et seule la première a été vérifiée.

### B2.1 — La justification scellée est fausse

ETPC a scellé l'argument suivant : *involution exacte OU conservation exacte de `Σρz`, pas les
deux, quand `M_A ≠ M_B`*. **Cet argument est faux.**

**Théorème (vérifié bloc par bloc).** Pour toutes masses `M_A, M_B > 0` et tout réel `p`, la
matrice

```
P = [[      p        ,  M_B(1+p)/M_A ],
     [ M_A(1−p)/M_B  ,      −p       ]]
```

est **à la fois** une involution exacte (trace 0, det −1) **et** exactement conservatrice de
`Σρz = M_A z̄_A + M_B z̄_B`. Les deux conditions sont compatibles identiquement, et non pas
seulement à masses égales. Le cas `p = 0` donne l'échange de moyennes redimensionné par les
masses `[[0, M_B/M_A], [M_A/M_B, 0]]`.

Vérification numérique sur les dix blocs primaires : involution `P² = I` à 1e-16 près,
résidu de conservation ≤ 1,78e-15 dans tous les blocs, **10/10**.

**`REPRESENTATION_PERMITS_CONSERVATIVE_INVOLUTION = YES`.**
Une involution conservatrice existait algébriquement et n'a pas été utilisée.

### B2.2 — Ce que l'application exécutée conserve réellement

| grandeur du registre | conservée ? | mesure |
|---|---|---|
| `Σρz` | **oui, en flottant seulement** | dérive max 2,109e-15 ; **jamais** identique bit à bit |
| `Σz` | non | dérive max 2,714 (sur ≈ 285) |
| multi-ensemble brut de `z` | non | sha256 différent dans les 10 blocs |
| histogramme de `z` (32 cases) | non | différent dans les 10 blocs |
| covariance `ρ–z` | non | variation relative 0,47 % … 0,96 % |
| exposition de `z` à la frontière matière–bain | **oui, bit à bit, 10/10** | **mais de façon vide — voir B2.3** |

**Contrôle d'identité indépendant.** La variation observée de `Σz` est reproduite exactement par
`n_A·Δz̄_A + n_B·Δz̄_B` à partir des seuls comptages de cellules et des décalages de moyenne
(résidu max 8,17e-14 sur ≈ 285, soit 3e-16 en relatif). L'opérateur a donc bien appliqué un
décalage additif uniforme à chaque composante et n'a touché rien d'autre.

### B2.3 — Nouvelle constatation : la conservation à la frontière est vide

L'exposition `Σ_{frontière} z` est **identique bit à bit avant et après l'intervention dans les
dix blocs**. Ce n'est pas une propriété rassurante de l'opérateur : c'est un angle mort du
registre.

*Preuve de disjonction.* La variation serait `n_A^bnd·Δz̄_A + n_B^bnd·Δz̄_B` avec des comptages
entiers. Au bloc 0, `Δz̄_A = +1,085064` et `Δz̄_B = −1,005159` ; ces deux nombres sont
incommensurables en double précision, donc une variation flottante **exactement nulle** impose
`n_A^bnd = n_B^bnd = 0`. Corroboration : `n_boundary_cells = 128` dans les dix blocs, alors que
toute la matière détectée fait 40 à 42 cellules selon le bloc (porte R6 sur le bloc de qualification : `Mf[0] sites changed = 42` ; blocs primaires : 40, 41 ou 42). Le masque
`ρ > 1e-4` est un halo diffus dont le bord se situe loin des corps détectés.

**Pourquoi cela compte.** Des sept grandeurs du registre, c'est celle dont le *nom* est le plus
proche du point de mesure **autorisé** (frontière matière–bain). Sa stabilité était disponible
pour être lue comme une confirmation. Elle n'en est pas une : à l'instant de l'intervention, le
masque et l'intervention ne se rencontrent pas.

### B2.4 — Nom honnête de l'opérateur

`PHYSICALLY_CONSERVATIVE_RECIPROCAL` est retiré comme nom non qualifié. Les mots
« permutation » et « échange exact » sont retirés. Le nom exact est :

```
BIJECTIVE_NONINVOLUTIVE_MASS_CONSERVING_AFFINE_MEAN_TRANSFER
```

---

## B3 — Audit des oracles : ce que les portes nommées ont réellement testé

| fixture | ce qu'elle a testé | ce qu'elle n'a **pas** testé |
|---|---|---|
| `test_swap_then_inverse` | `P⁻¹(P(x)) = x` à 1e-12 (résidu 2,776e-17) | `P(P(x)) = x` |
| `test_swap_declared_invariants` | `\|ΔΣρz\| < 1e-9` | les six autres grandeurs du registre |
| `test_swap_bijection_and_involution` | **rien** | **l'involution qu'elle nomme** |

Constat établi par analyse AST du code parent, pas par lecture : l'appel
`chk('R7_PERMUTATION', 'test_swap_bijection_and_involution', <condition>, …)` a reçu comme
condition la **constante littérale `True`**. Le résidu mesuré `P(P(x)) = 1,958e+00` a seulement
été **imprimé** dans la chaîne de détail, jamais comparé à quoi que ce soit.

**Circonstance atténuante, versée au dossier :** la chaîne de détail disait bien
« *involutive only when the two masses are equal … DECLARED, not asserted* ». La non-involution
n'a donc pas été dissimulée dans le texte. Ce qui est fautif, c'est le verdict **PASS** attaché
à une porte dont le nom affirme l'involution.

**C'est la constatation la plus grave de cet audit :** une porte nommée qui ne testait pas la
propriété qu'elle nommait.

---

## B4 — Table R0–R10 corrigée

26 lignes exécutées, 26 **PASS** au parent. Une seule ligne change de statut.

| # | porte | fixture | parent | **corrigé** |
|---|---|---|---|---|
| 1–2 | `R0_PARENT_PROVENANCE` | provenance parent, table de référence | PASS | PASS |
| 3–5 | `R1_REFERENCE_IDENTITY` | identité de code A/B/C/racine ; A ≠ B ; B = C | PASS | PASS |
| 6–8 | `R2_STATE_SCHEMA` | hachage complet ; aucune lecture hors schéma ; état d'intégrateur absent | PASS | PASS |
| 9–10 | `R3_CHECKPOINT_EXACTNESS` | aller-retour ; non-interrompu vs reprise | PASS | PASS |
| 11–13 | `R4_EXOGENOUS_NOISE` | aucun tirage aléatoire ; vecteurs témoins ; invariance au nom de branche | PASS | PASS |
| 14–16 | `R5_TWIN_EXACTNESS` | isolation de fork ; sham no-op ; jumeaux sans intervention | PASS | PASS |
| 17 | `R6_INTERVENTION_TOUCHSET` | seul `Mf[0]` change, 42 sites, `Mf[1]` intact | PASS | PASS |
| 18 | `R7_PERMUTATION` | `test_swap_then_inverse` | PASS | PASS **renommé** `ANALYTIC_INVERSE` (résidu 2,776e-17), **non** inverse bit à bit |
| 19 | `R7_PERMUTATION` | `test_swap_declared_invariants` | PASS | PASS **restreint** : `Σρz` seul, en flottant |
| 20 | `R7_PERMUTATION` | `test_swap_bijection_and_involution` | PASS | **ÉCHEC — `FAIL_NONINVOLUTIVE`** ; condition = littéral `True` ; `P(P(x))` = 1,958 |
| 21 | `R7_PERMUTATION` | variations réciproques non nulles | PASS | PASS |
| 22–23 | `R8_GAIN_ZERO_EXCLUSION` | exclusion publique à gain nul ; test non vide | PASS | PASS |
| 24–25 | `R9_ORDER_INDEPENDENCE` | invariance série/parallèle ; processus séparé | PASS | PASS |
| 26 | `R10_CLEAN_REPLAY` | rejeu propre depuis le bundle | PASS | PASS |

```
R7_PERMUTATION_OVERALL = FAIL_NONINVOLUTIVE      (était : PASS)
R0-R10 corrigé          = 25 PASS / 1 FAIL       (était : 26/26)
```

---

## B5 — Table T0–T10 corrigée

| porte | parent | **corrigé** |
|---|---|---|
| `T0_PUBLIC_RATCHET` | PASS | **PASS** — inchangé |
| `T1_PARENT_AND_CORRIGENDUM` | PASS | **PASS** — inchangé |
| `T2_EXACT_COUNTERFACTUALS` | PASS (R0–R10, 26/26) | **PASS, mais 25/26** — l'infrastructure de jumeaux exacts tient ; seule la porte de l'opérateur tombe |
| `T3_VALID_Z_INTERVENTION` | PASS | **ÉCHEC** — `T3_CAUSAL_COHERENCE = VALID_AS_IMPLEMENTED`, `T3_HANDOFF_CONFORMANCE = FAIL_NONINVOLUTIVE` → **`T3_OVERALL = FAIL`** |
| `T4_GAIN_ZERO_EXCLUSION` | PASS bit-exact | **PASS bit-exact** — `tau_off = 0,0` exactement, 10/10 |
| `T5_TWIN_BASELINE` | PASS | **PASS** — inchangé |
| `T6_PUBLIC_FLUX` | ÉCHEC tel que préenregistré | **`NOT_TESTED_AS_AUTHORIZED`** — substitution matérielle du point de mesure (voir B6) |
| `T7_DELAYED_PUBLIC_MEDIATOR` | ÉCHEC tel que préenregistré | **ÉCHEC tel que scellé**, `p = 1,000` ; c'est un **niveau** médiateur, pas un flux |
| `T8_DELAYED_RESPONSE` | ÉCHEC, `p` bilatéral 0,098 | **`NOT_ESTABLISHED`** — ni effet, ni nul |
| `T9_PUBLIC_PATH_ABOLITION` | contrôle PASS | **`PASS_BIT_EXACT` pour l'abolition**, `NOT_ESTABLISHED` pour la voie ON → `T9_OVERALL = NOT_ESTABLISHED` |
| `T10_HELD_OUT` | NON ATTEINTE | **`NOT_REACHED`** — la géométrie tenue à l'écart n'est **pas** ouverte par cet audit |

---

## B6 — Le point de mesure : autorisé ≠ scellé = exécuté

| niveau | objet |
|---|---|
| **autorisé** (handoff ETPC) | changements intégrés précoces du **flux réalisé de `c` ET de `N`** à la frontière |
| **scellé** (`etpc_protocol.json`) | `Σ_{t=1..40}` de la **moyenne de `c` sur un disque de rayon 8**, orientée par `q` |
| **exécuté** (`etpc_analyse.py`, `series_c`) | identique au scellé : `float(cur.c[sup].mean())`, `sup` = disque de rayon 8 |

Différences matérielles :

1. **Classe d'objet.** Une moyenne de champ sur un disque n'est pas un flux. Aucune face, aucun
   gradient, aucun terme de transport n'apparaît dans le calcul. Le mot « flux » dans le nom du
   point de mesure était inexact.
2. **Variable.** `N` n'est **jamais** lu par ce point de mesure (vérifié par AST sur
   `etpc_analyse.py` : aucun indiçage sur `'N'`). L'autorisation demandait `c` **et** `N`.
   *Note d'intégrité :* la moyenne de `N` sur le disque **est** présente dans les enregistrements
   commis. Elle n'est **délibérément pas** calculée ici : la calculer maintenant, en connaissant
   déjà le résultat sur `c`, serait une sélection de point de mesure post-hoc, interdite par
   `NEW_ENDPOINT_SELECTION = false`.
3. **Support.** Le disque de rayon 8 couvre ≈ 197 cellules pour un corps de ≈ 21 cellules :
   environ 89 % du support est du bain, pas de la frontière matière–bain.

Le protocole scellé et le code exécuté **concordent entre eux**. La déviation est donc
**prospective** vis-à-vis des résultats — elle a été écrite avant la campagne primaire — mais
elle est **hors autorisation**.

```
ENDPOINT_PROTOCOL_CONFORMANCE = PROSPECTIVELY_AMENDED_BUT_AUTHORIZATION_DEVIATION
T6 = NOT_TESTED_AS_AUTHORIZED
```

Renommer « flux » une moyenne sur un disque ne répare pas la substitution.

**Contrôle de reconstruction (Phase D).** Les deux scalaires commis ont été reconstruits à partir
des seuls tableaux commis :

| scalaire | reconstruit | commis | résidu max par bloc |
|---|---|---|---|
| `early` | 2,876648e-05 | 2,876648e-05 | **0,000e+00** |
| `mediator` | 6,653644e-04 | 6,653644e-04 | **0,000e+00** |

L'arithmétique du parent est donc **exacte**. Ce qui est en cause n'est pas le calcul, c'est
l'objet calculé.

---

## B7 — Ledger de revendications corrigé

### Formulations retirées

- « réel et reproductible » sans nommer la couche de reproductibilité concernée
- la phrase du parent qui créditait la dérivée locale de `κ` en attribuant l'écart au lecteur
- « échec préenregistré propre »
- `PHYSICALLY_CONSERVATIVE_RECIPROCAL` comme nom d'opérateur non qualifié
- « permutation » et « échange exact » pour l'opérateur exécuté

### Couches de reproductibilité, nommées séparément

| couche | statut |
|---|---|
| reproductibilité computationnelle bit à bit | **ÉTABLIE** (R3, R9, R10) |
| cohérence sur les 10 blocs primaires | **ÉTABLIE** (même signe partout, IC serré) |
| inférence sur la distribution des blocs fondateurs | **NON ÉTABLIE** pour les hypothèses unilatérales gelées |
| réplication sur géométrie tenue à l'écart | **NON ATTEINTE** |

### Dispositions corrigées

```
DESCRIPTIVE_PRIMARY_PUBLIC_PATTERN  = DELAYED_PUBLIC_MEDIATOR_ONLY__OPPOSITE_FROZEN_DIRECTION
PREREGISTERED_PUBLIC_PATH_DISPOSITION = NOT_ESTABLISHED
DELAYED_RESPONSE_EFFECT             = NOT_ESTABLISHED
DELAYED_RESPONSE_NULL               = NOT_ESTABLISHED
```

`tau_on` = 0,009122, IC95 [−0,002295 ; +0,020538], `p` bilatéral de randomisation = 0,097656,
`p` minimal atteignable avec 10 blocs = 0,001953. Un `p` de 0,098 n'est ni un effet ni un nul.
**Aucune marge d'équivalence rétrospective n'est ajoutée.**

### Partage de validité

| objet | verdict |
|---|---|
| `EXACT_TWIN_INFRASTRUCTURE_VALIDITY` | **VALIDE** — R3, R5, R8, R9, R10 sont bit-exacts et ne dépendent ni de l'opérateur ni du point de mesure |
| `APPLIED_INTERVENTION_CAUSAL_INTERPRETABILITY` | **VALIDE TELLE QU'IMPLÉMENTÉE** — l'application est bien définie, bijective, conservatrice de `Σρz` ; le contraste ON/OFF reste une comparaison causale déterministe légitime |
| `ETPC_PROTOCOL_CONFORMANCE` | **DÉVIATION MATÉRIELLE** |
| `ETPC_CONFIRMATORY_VALIDITY` | **INVALIDE COMME TEST DES HYPOTHÈSES AUTORISÉES** |

ETPC ne doit plus être décrit comme un échec préenregistré entièrement conforme. Son
infrastructure et ses contrastes déterministes observés survivent ; son exécution confirmatoire,
non.

---

## Arrêts terminaux déclenchés par cet audit

```
PROSPECTIVE_PROTOCOL_DEVIATION_NONINVOLUTIVE
MATERIAL_ENDPOINT_SUBSTITUTION
ENDPOINT_AUDIT_DATA_INSUFFICIENT      (Phase F seulement)
```

**Non déclenché :** `AUDIT_SCOPE_VIOLATION`. Démarrages moteur = 0, vérifié par sentinelle
fermant par défaut.
