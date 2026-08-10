# `EXACT_ENDPOINT_FUNCTIONAL_CONGRUENCE_AUDIT_00`

**Portée** `AUDIT_ONLY` · **démarrages moteur** `0` · **nouvelles trajectoires** `0`
**Branche** `audit/exact-endpoint-functional-congruence-00`
**Parent** `3f8dae8bbe2937c43661ba8adfe8aed63bf6b6ee` (`EXACT_TWIN_PUBLIC_PATH_COUNTERFACTUAL_00`)

---

## 0. Ce qu'il faut retenir

L'audit répond aux quatre questions posées. Deux réponses sont défavorables au travail parent, et
elles sont défavorables pour des raisons vérifiables, pas par prudence rhétorique.

```
OPERATOR_INVOLUTION                   = FAIL
REPRESENTATION_PERMITS_CONSERVATIVE_INVOLUTION = YES
ENDPOINT_PROTOCOL_CONFORMANCE         = PROSPECTIVELY_AMENDED_BUT_AUTHORIZATION_DEVIATION
EXACT_FUNCTIONAL_MAP                  = COMPLETE
EXACT_ENDPOINT_DIRECTION              = NOT_DERIVABLE
FUTURE_TEST_LATERALITY                = TWO_SIDED_ONLY
OPPOSITE_SIGN_MECHANISM               = AUDIT_DATA_INSUFFICIENT
NATIVE_DOWNSTREAM_ENDPOINT            = ELIGIBLE
HELD_OUT_INTEGRITY                    = PRESERVED
FUTURE_CONFIRMATORY_PROGRAM           = ELIGIBLE_IN_PRINCIPLE
```

Le corrigendum complet est dans `ETPC_CORRIGENDUM.md`. Le présent rapport donne la méthode, les
preuves et ce qui reste ouvert.

---

## 1. Phase A — provenance, inventaire, sentinelle

### 1.1 Provenance

| élément | valeur |
|---|---|
| commit parent | `3f8dae8bbe2937c43661ba8adfe8aed63bf6b6ee` |
| bundle parent sha256 | `846e3c2ba5c2adb01b5beed3c83f8b0a2007f7fe4a6b5c2d027ba1a100499a5b` |
| archive parent sha256 | `1f9271f48dbad16be82ae83e18ef84aa4580db920a87d2411ea8a7e9cf456685` |
| protocole parent sha256 | `df26647833dbe5a5f45195ee3c72058420872367345ec5425892634b91f03071` |
| handoff d'autorisation sha256 | `3461bfe067b22b394c85a253e5208c3596e05b2630c538b2095f423332684266` |

`AUTHORIZATION_HANDOFF_VERIFIABLE = false`. Le flux d'octets canonique du handoff n'est pas un
artefact du dépôt : son empreinte est **enregistrée telle que donnée**, jamais **affirmée comme
vérifiée**. Distinction volontaire.

Scellé de code parent intact : `etpc_core.py`, `etpc_gates.py`, `etpc_phaseA.py`, `etpc_run.py` —
**4/4 conformes** à `code_sha256` du protocole scellé.

### 1.2 Inventaire du matériau brut — et ce qui manque

Ce que le parent a commis : `etpc_PRIMARY.pkl` (10 blocs), `etpc_gates.json`,
`etpc_analysis_PRIMARY.json`, `etpc_phaseA.json`, `etpc_verify.json`, `etpc_protocol.json`.

```
RAW_SPATIAL_FIELDS_RETAINED = false
```

**Défaut du parent, découvert ici.** `etpc_run.py` écrivait chaque checkpoint `.npz` dans un
`tempfile.mkdtemp()` **jamais commis**. Les enregistrements commis ne contiennent que des
**moyennes** de `c` et `N` sur le support de halo, des empreintes publiques, les vecteurs de
réponse et des résumés de géométrie — **aucun tableau `c`, `N`, `ρ` ou `Mf`**.

Conséquence directe : la Phase F (décomposition spatiale corps / frontière / coquille) est
**impossible**. Ce n'est pas un choix ; c'est une limite de données. Et il faut le dire dans
l'autre sens aussi : **aucun champ spatial jamais ouvert n'est ouvert par cet audit, parce qu'il
n'en existe aucun**.

`etpc_HELDOUT.pkl` n'existe pas. La géométrie tenue à l'écart n'a jamais été exécutée et n'est
pas lue ici.

### 1.3 Déclaration de statut rétrospectif

Cet audit est **entièrement rétrospectif** vis-à-vis des quatre valeurs de point de mesure, de
leurs intervalles de confiance et de leurs `p`, tous déjà connus et cités dans le rapport parent.
L'auteur d'ETPC et l'auteur de l'audit sont **le même agent**. Ces deux faits sont déclarés en
tête, pas enfouis : ils bornent ce que l'audit peut prétendre établir.

### 1.4 Sentinelle de démarrage moteur

`eefca_sentinel.py` remplace `builtins.__import__` **avant tout autre import** et lève
`RuntimeError('AUDIT_SCOPE_VIOLATION')` sur tout module d'exécution (`edlab`, `ppai_engine`,
`ppai_core`, `domc_core`, `chmr_core`, `etpc_core`, `etpc_run`, `etpc_gates`). Elle **ferme par
défaut** : un module inconnu de la liste mais enraciné dans `edlab` est également refusé.

Test de la sentinelle elle-même : `AUDIT_SCOPE_VIOLATION: forbidden runtime import 'edlab'` —
elle se déclenche bien.

Résultat final après exécution complète de `eefca_audit.py` :

```
{'NEW_ENGINE_STARTS': 0, 'forbidden_import_attempts': [], 'sentinel': 'fails closed'}
```

Aucun import interdit n'a même été **tenté** par l'audit. Dans `eefca_verify.py`, le contrôle V1
**provoque délibérément** la sentinelle pour prouver qu'elle se déclenche ; son rapport affiche
donc `forbidden_import_attempts: ['edlab']`. Cette entrée unique est la sonde, pas une infraction :
l'import a été refusé, aucun module d'exécution n'a été chargé, aucun état n'a avancé.

`NEW_ENGINE_STARTS = 0`. `AUDIT_SCOPE_VIOLATION` non déclenché.

---

## 2. Phase C — l'opérateur (question Q1)

### 2.1 Réduction symbolique

L'opérateur exécuté est, sur le couple `(z̄_A, z̄_B)`, l'application affine

```
P = [[1−a, a], [b, 1−b]] ,   a = m*/M_A , b = m*/M_B , m* = min(M_A, M_B)
```

de déterminant `1−a−b`, de trace `2−a−b`, de valeurs propres `{1, 1−a−b}`. Le vecteur propre à
gauche pour la valeur propre 1 est `(M_A, M_B)` : c'est **exactement** la conservation de `Σρz`.

Le second mode — le **contraste** `z̄_A − z̄_B` — est multiplié par `1−a−b` à chaque application.
Sur les dix blocs, `1−a−b ∈ [−0,9747 ; −0,9087]`, donc **`P² ≠ I` partout**, avec un facteur de
contraste résiduel de 0,826 à 0,950 après deux applications.

### 2.2 Le point décisif : l'involution conservatrice existait

ETPC avait scellé la justification « involution exacte **ou** conservation exacte de `Σρz`, pas
les deux, quand `M_A ≠ M_B` ». **Cette justification est fausse**, et c'est démontrable en
quelques lignes.

Cherchons `P = [[p, q], [r, s]]` sur `(z̄_A, z̄_B)`.
Involution ⟺ `trace = 0` et `det = −1` ⟺ `s = −p` et `qr = 1 − p²`.
Conservation de `Σρz = M_A z̄_A + M_B z̄_B` ⟺ `(M_A, M_B)` vecteur propre à gauche de valeur
propre 1 ⟺ `q = M_B(1+p)/M_A` et `r = M_A(1−p)/M_B`.
Alors `qr = (1+p)(1−p) = 1 − p²` — **satisfait identiquement**, pour toutes masses.

Les deux exigences ne sont donc pas en concurrence : elles sont **compatibles pour toute paire de
masses**. Le cas `p = 0` donne l'échange de moyennes redimensionné `[[0, M_B/M_A], [M_A/M_B, 0]]`.

Vérification numérique bloc par bloc, à partir des seules masses commises : `P² = I` à 1e-16,
résidu de conservation ≤ 1,78e-15, **10 blocs sur 10**.

```
REPRESENTATION_PERMITS_CONSERVATIVE_INVOLUTION = YES
```

### 2.3 Quand la déviation a-t-elle eu lieu ?

La non-involution a été **écrite dans `etpc_protocol.json`, scellé avant la campagne primaire**.
L'amendement est donc **prospectif vis-à-vis des résultats** — il n'a pas été fabriqué après coup
pour arranger un chiffre. Mais il est **hors autorisation** : le handoff demandait une involution
« chaque fois que la représentation le permet », et la représentation le permettait.

C'est une distinction qui compte, et elle joue dans les deux sens : elle **innocente** ETPC de
tout ajustement post-hoc, et elle le **condamne** sur la conformité.

```
ETPC_OPERATOR_PROTOCOL_CONFORMANCE = PROSPECTIVELY_AMENDED_BUT_AUTHORIZATION_DEVIATION
STOP : PROSPECTIVE_PROTOCOL_DEVIATION_NONINVOLUTIVE
```

### 2.4 Inventaire des invariants, et un angle mort

Voir `ETPC_CORRIGENDUM.md` §B2.2–B2.3. Résumé : l'application ne conserve que `Σρz`, et
seulement en flottant (dérive max 2,109e-15, **jamais** bit à bit). Elle change le multi-ensemble
brut de `z`, `Σz`, l'histogramme et la covariance `ρ–z`.

L'exposition de `z` à la frontière matière–bain est, elle, **identique bit à bit dans les dix
blocs** — mais c'est **vide de sens** : on démontre (§B2.3) que le masque de frontière du registre
(`ρ > 1e-4`, 128 cellules dans les dix blocs) est **disjoint** des 40 à 42 cellules touchées. La grandeur dont le nom est
le plus proche du point de mesure autorisé était donc **aveugle à l'intervention**. C'est une
constatation nouvelle de cet audit, obtenue sans moteur, à partir des seuls scalaires commis.

### 2.5 Audit des oracles

Analyse AST du code parent, pas relecture à l'œil :

- `test_swap_then_inverse` a testé `P⁻¹(P(x)) = x` (résidu 2,776e-17). Ce n'est **pas**
  l'involution.
- `test_swap_bijection_and_involution` a reçu comme condition la **constante littérale `True`**.
  Elle n'a rien testé. Le résidu mesuré `P(P(x)) = 1,958` n'a été qu'**imprimé**.
- `test_swap_declared_invariants` n'a assuré qu'**une** des sept grandeurs du registre.

La chaîne de détail de la porte disait bien « *DECLARED, not asserted* » : la non-involution
n'était pas dissimulée. Ce qui est fautif, c'est le **PASS** attaché à une porte dont le nom
affirme l'involution. **C'est la constatation la plus grave de l'audit.**

```
R7_PERMUTATION_OVERALL = FAIL_NONINVOLUTIVE
T3_CAUSAL_COHERENCE    = VALID_AS_IMPLEMENTED
T3_HANDOFF_CONFORMANCE = FAIL_NONINVOLUTIVE
T3_OVERALL             = FAIL
```

Nom honnête de l'opérateur : `BIJECTIVE_NONINVOLUTIVE_MASS_CONSERVING_AFFINE_MEAN_TRANSFER`.

---

## 3. Phase D — le point de mesure (question Q2)

Trois objets distincts portaient le même nom.

| niveau | objet réel |
|---|---|
| **autorisé** | flux **réalisé** de `c` **et** de `N` à la frontière matière–bain, intégré tôt |
| **scellé** | `Σ_{t=1..40}` de la **moyenne de `c` sur un disque de rayon 8**, orientée par `q` |
| **exécuté** | identique au scellé (`series_c` → `float(cur.c[sup].mean())`) |

Ce qui sépare le premier des deux autres :

1. Une moyenne de champ sur un disque **n'est pas un flux**. Aucune face, aucun gradient, aucun
   terme de transport n'entre dans le calcul.
2. **`N` n'est jamais lu** (vérifié par AST : aucun indiçage sur `'N'` dans
   `etpc_analyse.py`). L'autorisation demandait `c` **et** `N`. *Note d'intégrité :* la moyenne
   de `N` sur le disque **existe** dans les enregistrements commis ; elle n'est **délibérément
   pas** calculée ici, car la calculer en connaissant déjà le résultat sur `c` serait une
   sélection de point de mesure post-hoc, interdite par `NEW_ENDPOINT_SELECTION = false`.
3. Le disque de rayon 8 couvre ≈ 197 cellules pour un corps de ≈ 21 : **≈ 89 % du support est du
   bain**, pas de la frontière.

Le protocole scellé et le code exécuté concordent entre eux : la déviation est **prospective**,
mais **hors autorisation**.

```
ENDPOINT_PROTOCOL_CONFORMANCE = PROSPECTIVELY_AMENDED_BUT_AUTHORIZATION_DEVIATION
T6 = NOT_TESTED_AS_AUTHORIZED
STOP : MATERIAL_ENDPOINT_SUBSTITUTION
```

**Contrôle de reconstruction.** Les deux scalaires publiés ont été recalculés depuis les seuls
tableaux commis, sans moteur :

| scalaire | reconstruit | commis | résidu max par bloc |
|---|---|---|---|
| `early` | 2,876648e-05 | 2,876648e-05 | **0,000e+00** |
| `mediator` | 6,653644e-04 | 6,653644e-04 | **0,000e+00** |

**L'arithmétique du parent est exacte.** Le problème n'est pas le calcul : c'est l'objet calculé.
Un intervalle de confiance propre autour du mauvais objet reste un intervalle propre autour du
mauvais objet.

---

## 4. Phase E — congruence fonctionnelle exacte (question Q3)

Chaîne complète, flèche par flèche, du `z` intervenu au scalaire publié :

| flèche | classe |
|---|---|
| `P(z) → z` | `STRUCTURAL_IDENTITY` — affine, exactement connue |
| `z → κ = 1 + g·tanh z` | `MONOTONE_FOR_ALL_ADMISSIBLE_STATES` |
| `κ → coefficient de face 0,5(κ_i+κ_j)` | `MONOTONE_FOR_ALL_ADMISSIBLE_STATES` |
| coefficient de face `→` mise à jour réalisée de `c` | **`STATE_CONDITIONAL_SIGN`** |
| champ `→` moyenne sur disque de rayon 8 | **`NO_SIGN_THEOREM`** |
| moyenne `→` médiateur retardé à `t = 200` | `EMPIRICAL_ONLY` |
| médiateur `→` lecteur de réponse à 20 composantes | **`NO_SIGN_THEOREM`** |
| réponse `→ tau` | `STRUCTURAL_IDENTITY` |

### L'échelle de dérivées

| barreau | dérivabilité |
|---|---|
| 1. `dκ/dz = g·sech²(z) > 0` | **DÉRIVABLE, et elle a bien été dérivée** |
| 2. `d(flux)/dκ = D·∇c` sur la face | `STATE_CONDITIONAL` — dépend de l'orientation du gradient local |
| 3. moyenne sur disque de `div(D κ ∇c)` | **NON DÉRIVABLE** — le laplacien change de signe **à l'intérieur** du support |
| 4. + 40 pas d'intégration temporelle | **NON DÉRIVABLE** |
| 5. lecteur de réponse retardée | **NON DÉRIVABLE** — agrégat non monotone |

**Verdict.** La direction unilatérale scellée a été dérivée au **barreau 1** et appliquée au
**barreau 4**. Aucun signe ne se propage légitimement au-delà du barreau 2. La phrase du rapport
parent qui créditait la dérivée locale de `κ` en attribuant l'écart au lecteur est **retirée** et
remplacée par cette échelle explicite.

```
EXACT_ENDPOINT_DIRECTION = NOT_DERIVABLE
FUTURE_TEST_LATERALITY   = TWO_SIDED_ONLY
EXACT_FUNCTIONAL_MAP     = COMPLETE
```

Conséquence pratique : **toute reprise sur ce point de mesure doit être bilatérale**, non parce
que le test unilatéral a échoué — ce serait exactement le retournement post-hoc interdit — mais
parce que **le modèle ne fournit aucun théorème de signe** à ce niveau d'agrégation. La
justification est structurelle et antérieure au résultat.

---

## 5. Phase F — décomposition rétrospective : **non tentée**

`OPPOSITE_SIGN_MECHANISM = AUDIT_DATA_INSUFFICIENT`

Aucun champ spatial n'a été conservé (§1.2). Une décomposition corps / frontière / coquille /
support restant, à poids exhaustifs sommant exactement au total commis, est impossible.

L'explication « le disque agrège une région où le laplacien change de signe, alors que la
dérivation scellée portait sur le pic » reste une **hypothèse non testée**. Elle est nommée ici
comme hypothèse, et elle **ne doit pas** être citée comme une explication établie.

```
STOP : ENDPOINT_AUDIT_DATA_INSUFFICIENT   (Phase F uniquement ; la Phase D a réussi)
```

---

## 6. Phase G — éligibilité future (question Q4)

### Candidat retenu

| critère | `REALIZED_MATERIAL_BATH_BOUNDARY_FLUX` de `c` et `N` |
|---|---|
| sens scientifique | la grandeur **effectivement autorisée** : l'échange réalisé intégré à travers les faces matière–bain |
| provenance du code | la forme de flux de face existe dans `ppai_engine._face_transport`, scellée dans PPAI **avant** tout résultat ETPC |
| position dans la chaîne | **première** flèche publique, immédiatement en aval de `κ` |
| déjà inspecté ? | **NON — jamais calculé** |
| sélection post-hoc ? | **NON** — c'est le point de mesure autorisé, nommé avant tout résultat |
| direction dérivable ? | `STATE_CONDITIONAL`, calculable depuis un checkpoint **avant** toute évolution future |
| mesurable sur la géométrie tenue à l'écart ? | oui, sans toucher au LawSpec, au gain, à l'opérateur ni au lecteur |

Ce candidat passe le test qui compte : **il n'a pas été choisi parce qu'il arrangerait le
résultat existant** — il n'a jamais été calculé, et c'est celui que l'autorisation nommait dès le
départ.

### Explicitement inéligibles

- tout pic, anneau, rayon, décalage ou normalisation choisi **parce qu'il inverse le signe observé**
- un gain plus fort, ou négatif
- un nouvel état de mémoire, une nouvelle histoire, un nouvel opérateur, un nouveau LawSpec
- l'allongement de l'horizon **parce que** `p = 0,098` paraissait prometteur
- la réutilisation du test unilatéral échoué comme succès confirmatoire bilatéral
- toute lecture de la géométrie tenue à l'écart avant un nouveau protocole gelé

### Verdict

```
NATIVE_DOWNSTREAM_ENDPOINT  = ELIGIBLE
HELD_OUT_INTEGRITY          = PRESERVED
FUTURE_CONFIRMATORY_PROGRAM = ELIGIBLE_IN_PRINCIPLE
```

**Conditions non négociables** (branche B, la seule ouverte) :

1. test **bilatéral** du flux réalisé à la frontière matière–bain, `c` **et** `N` ;
2. opérateur **réparé** en l'involution conservatrice démontrée en §2.2 ;
3. les dix blocs primaires d'ETPC sont **reclassés données de développement, définitivement** ;
4. nouvelle géométrie fondatrice, protocole gelé et scellé **avant** toute exécution ;
5. la géométrie tenue à l'écart reste fermée jusqu'à ce gel.

**Rien n'est lancé.** Cette éligibilité est une conclusion d'audit, pas un démarrage.

---

## 7. Conclusions maximales autorisées

Ce que cet audit **peut** affirmer :

- l'infrastructure de contrefactuels exacts d'ETPC est **valide** et **survit** ;
- l'intervention appliquée est bien définie, bijective et conservatrice de `Σρz`, et le contraste
  ON/OFF reste une comparaison causale déterministe **légitime telle qu'implémentée** ;
- l'exécution **confirmatoire** d'ETPC est **invalide comme test des hypothèses autorisées**, pour
  deux raisons indépendantes : opérateur non involutif alors que l'involution était disponible, et
  substitution matérielle du point de mesure ;
- l'arithmétique publiée est exacte (reconstruction à résidu nul) ;
- la direction du point de mesure exécuté **n'est pas dérivable** du modèle ;
- une reprise confirmatoire est **éligible en principe**, sous conditions strictes.

Ce que cet audit **ne peut pas** affirmer, et n'affirme pas :

- il ne dit **rien** sur l'existence ou l'absence d'un effet causal de `z` sur la voie publique ;
- il ne fournit **aucun** mécanisme expliquant le signe observé (Phase F sans données) ;
- il ne convertit **pas** `p = 0,098` en effet ni en nul ;
- il n'ouvre **aucune** question d'appartenance, d'individualité, de clôture, d'autonomie, de
  métabolisme, d'hérédité, de vie ou d'esprit. Aucune de ces catégories n'est en jeu ici.

---

## 8. Attestation de non-accès à la géométrie tenue à l'écart

`etpc_HELDOUT.pkl` **n'existe pas**. La géométrie `NEAR` tenue à l'écart n'a jamais été exécutée,
sous aucun point de mesure. Aucun fichier la concernant n'a été ouvert, listé pour son contenu, ni
hachée en vue d'une inférence. `HELD_OUT_INTEGRITY = PRESERVED`.

---

## 9. Artefacts

| fichier | rôle |
|---|---|
| `eefca_sentinel.py` | garde d'import fermant par défaut, installée avant tout |
| `eefca_audit.py` | l'audit complet, phases A–G, zéro moteur |
| `eefca_audit.json` | toutes les sorties numériques, bloc par bloc |
| `eefca_protocol.json` + `.sha256` | plan d'audit scellé, portée, interdits, empreintes de code |
| `eefca_verify.py` / `eefca_verify.json` | vérificateur indépendant — **34/34 PASS** |
| `ETPC_CORRIGENDUM.md` | corrigendum B1–B7, tables R et T corrigées |
| `REPORT_EEFCA.md` | le présent rapport |
| `SHA256SUMS` | empreintes de tous les artefacts |

Le vérificateur redérive chaque affirmation portante depuis les seuls artefacts parents commis —
non-involution bloc par bloc, existence de l'involution conservatrice, inventaire des invariants,
disjonction du masque de frontière, reconstruction exacte des deux scalaires, condition littérale
de la porte R7 par AST, absence de lecture de `N`, absence des formulations interdites — puis les
compare à `eefca_audit.json`. **34 contrôles, 34 PASS.**
