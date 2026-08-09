# `EXACT_TWIN_PUBLIC_PATH_COUNTERFACTUAL_00` — rapport

**2026-08-09** · parent `ba92a16a10c92cc400af81f022ef4dc78b16377e`
(bundle SHA-256 `1a1cea19272a4c8659d756cfb50338c2cbadc50cb893f3ef3c2553d185655479`)
· `NEW_LAWSPEC = false` · `PPAI_REOPENED = false`
· protocole scellé `df26647833dbe5a5f45195ee3c72058420872367345ec5425892634b91f03071`
· **67 démarrages moteur** sur 124 planifiés (160 absolus) · 26/26 portes R0–R10 · 11/11 vérifications

> **Verdict : `PRIMARY_NOT_CONFIRMED`. La géométrie tenue à l'écart n'a pas été ouverte.**
>
> L'infrastructure de jumeaux exacts est **valide de bout en bout** : le modèle est
> intégralement déterministe, les jumeaux sont bit-identiques pas à pas, l'opérateur conserve
> **exactement** Σρz, et l'exclusion à gain nul est **bit-exacte dans les dix blocs** — `tau_off`
> vaut exactement `0,0`. Aucun chemin caché n'existe.
>
> Le résultat scientifique est un **échec préenregistré propre** : l'échange de `z` produit bien
> un effet public réel, mais **de signe opposé** à la dérivation scellée
> (`+2,88·10⁻⁵` au lieu de négatif, p unilatéral = 1,000), et la réponse retardée **ne change
> pas** (`tau_on = +0,0091` [−0,0023 ; +0,0205], p bilatéral = **0,098**).
>
> `PUBLIC_PATH_REGIME = CONSTITUTIVE_PUBLIC_RESPONSE` (avec inversion de signe déclarée).
> `EXACT_TWIN_DISPOSITION = NOT_ESTABLISHED`.

---

## Phase A — corrigendum `PPAI` (zéro exécution cible)

### A/B/C, avec micro-fixture où tous les termes retirés sont actifs

| référence | LawSpec | exécutable | SHA-256 |
|---|---|---|---|
| **A** original `sc_mcm` | `MCParams(lam_plus=0,25 ; lam_minus=0,15)` + héritage | `edlab/experiments/sc_mcm/engine.py` | `d51a5db1848e…` |
| **B** base `PPAI` expurgée | chemins privés et héritage retirés | `PPAI/ppai_engine.py` | `9c7d0c133007…` |
| **C** `PPAI` à `g = 0` | idem B, un paramètre | `PPAI/ppai_engine.py` | `9c7d0c133007…` |
| racine | `ScaffoldEngine` gelé (`beta=0,10`) | `edlab/substrates/scaffold/engine.py` | `dee42f1879c9…` |

Micro-fixture : `m₊`, `m₋`, `z` non nuls, gradients `c`/`N` non nuls, liens matière–bain actifs,
croissance et mort actives, matière fraîche entrante, 25 pas.

- **B == C bit pour bit : VRAI** — mais B et C sont le **même exécutable** à un paramètre près.
  Cette identité est quasi tautologique et déclarée comme telle.
- **A ≠ B dans chacun des canaux prédits** : `uptake` 9,5·10⁻⁵ (canal `lam_plus`), `c` 8,3·10⁻³
  (canal `lam_minus`), `Mf` 9,2·10⁻³ (canal héritage), `rho` 5,2·10⁻³ (aval de l'uptake).

```
PPAI_GAIN_ZERO_REPRODUCES_CONSTRUCTED_EXPURGATED_BASELINE = ESTABLISHED
ORIGINAL_PARENT_NESTED_NULL                               = NOT_ESTABLISHED
```

Le texte de `PPAI` disait « la `LawSpec` **racine** gelée », ce qui était exact ; le corrigendum
rend la distinction explicite et interdit toute lecture comme un emboîtement du **parent**.

### Les cinq autres corrections

1. **Graphe ancien reclassé** : `DIRECT_PRIVATE_READER_PATH + WEAK_ENVIRONMENT_MEDIATED_PUBLIC_PATH`.
   `m₋ → production c` fournissait déjà un chemin public **faible**. Dire qu'il n'y avait aucun
   chemin public était faux.
2. **« le cœur pèse 0,97 % du halo » est retiré.** `β_core|halo = +0,726` et `β_halo = +74,75`
   sont dans des **unités différentes** (par unité d'écart de cœur en `m₊`, par unité d'écart de
   halo en `c` moyen), jamais standardisées : leur rapport n'est pas une fraction interprétable.
   Les deux coefficients sont republiés séparément, sans rapport.
3. **Contraste de perméabilité — trois objets distincts, désormais nommés :**

   | objet | valeur |
   |---|---|
   | site, asymptotique `|z|→∞` | **2,000** (la contrainte scellée « ≤ 2× » mord exactement) |
   | site, au clip physique `|z| ≤ 1` | **1,6805** ← **c'est là que le 1,6805 a été mesuré** |
   | face matière–bain (bain `κ=1`, moyenne arithmétique), asymptotique | **1,400** |
   | face matière–bain, au clip | 1,291 |

   Le `1,6805` est une propriété de `κ(z)` seule, balayée sur une grille de `z` dans les fixtures
   G1.3/G1.4 ; ce n'est **ni** un rapport de face **ni** la valeur asymptotique. Aucune conclusion
   ne change : toutes les valeurs sont à ou sous la borne scellée.
4. **Arithmétique `CHMR` réconciliée, exactement.** `mvA` et `mvB` sont des **fractions
   adimensionnelles** de la séparation, pas des déplacements bruts ; les soustraire d'une
   séparation brute mélange les unités. L'identité cohérente est
   `sep_cross = sep_matched × (1 − mvA − mvB)`, et son **résidu par bloc vaut 0,000e+00** sur les
   douze blocs. Médianes : `sep_matched = 2,1311`, `mvA = 0,6386`, `mvB = 0,3073` →
   prédit `0,1152`, observé `0,1114` (les médianes de rapports ne sont pas le rapport des
   médianes ; les coordonnées absolues par bloc sont publiées).
   `OPPOSITE_STATE_OVERWRITE = NOT_ESTABLISHED` — aucun critère directionnel n'était gelé.
5. **« permutation conservative » remplacée par un registre d'invariants explicite** :
   multiset brut de `z`, `Σz`, `Σρz`, histogramme, covariance `ρ–z`, exposition de `z` à la
   frontière matière–bain, moyennes par composant, fraction transférée. `PPAI` conservait
   exactement le **multiset du champ intensif** ; `Σρz` n'était **pas** conservé, et le résidu
   d'histogramme effectif (1,2 %) était déclaré.

**Énoncés parents préservés** : `PPAI_G3 = FAIL_FOR_THE_PREREGISTERED_DESIGN`,
`NO_VALID_WASH_WINDOW_IDENTIFIED_IN_BOUNDED_DEV = SUPPORTED`, `PPAI_G4_TO_G10 = NOT_REACHED`,
`PPAI_CAUSAL_ARCHITECTURE = NOT_YET_TESTED`, `MORPHOLOGY_AS_UNIQUE_BLOCKER = NOT_ESTABLISHED`.

---

## Phase B — infrastructure de contrefactuels exacts : R0–R10, **26/26**

| porte | test | résultat |
|---|---|---|
| `R0` provenance | bundle, commit, artefacts | PASS |
| `R1` identité A/B/C | SHA-256 de chaque exécutable ; A≠B dans les canaux prédits ; B==C | PASS |
| `R2` schéma d'état | chaque tableau haché avec nom, forme, dtype, boutisme, octets | PASS |
| `R2` | intégrateur, file d'événements, forçage résiduel, accumulateurs, caches : **prouvés ABSENTS** | PASS |
| `R3` | `test_checkpoint_roundtrip` ; `test_uninterrupted_vs_resume` | PASS, hachages identiques |
| `R4` bruit exogène | **audit de non-aléatoire complet** : zéro attribut aléatoire dans tout le moteur | PASS |
| `R5` | `test_fork_memory_isolation`, `test_sham_noop`, `test_no_intervention_twins` | PASS, hachages identiques sur 120 pas |
| `R6` | `test_swap_touchset` : seuls `Mf[0]` et 42 sites changent ; `Mf[1]` intact | PASS |
| `R7` | `test_swap_then_inverse` résidu **2,78·10⁻¹⁷** ; `Σρz` conservé à **4,66·10⁻¹⁵** | PASS |
| `R8` | `test_gain_zero_public_exclusion` : **tous** champs publics bit-identiques sur 300 pas, avec `z` différant de 0,304 | PASS |
| `R9` | ordre de branche inversé, et processus séparé : hachages identiques | PASS |
| `R10` | `test_clean_bundle_replay` : bloc régénéré de zéro = rejoué depuis checkpoint | PASS |

**Le modèle est intégralement déterministe.** Le seul objet stochastique de tout le chemin est
`seed_state(…, "random")`, fonction déterministe de la graine évaluée **une fois à t = 0, avant
toute branche**. `R4` est donc acquitté par un audit de non-aléatoire, comme le protocole
l'exige, et non par un bruit artificiel. L'indépendance de branche est exacte par construction :
aucune variable aléatoire n'est jamais tirée après le point de branchement.

---

## Phase C — `z` et l'opérateur `P`

`z = m1 = Mf[0]/ρ` est une **concentration intensive portée par la matière** ; son contenu
extensif est `ρz = Mf[0]`. La mesure globale physiquement pertinente est donc `Σρz`.
`κ(z)` est recalculé à chaque pas depuis `Mf` et `ρ` : **aucun cache, aucune autre vue dérivée**.
`Mf[1]` est une coordonnée indépendante, jamais touchée.

```
m* = min(M_A, M_B)          la mesure matérielle commune exactement échangeable
a  = m*/M_A ,  b = m*/M_B   (l'un des deux vaut exactement 1)
z_A ← z_A + a (z̄_B − z̄_A)
z_B ← z_B + b (z̄_A − z̄_B)
```

Variation extensive `= m*(z̄_B − z̄_A) + m*(z̄_A − z̄_B) = 0`, **exactement**. Le composant le plus
léger échange toute sa moyenne ; le plus lourd n'échange que la part appariée en masse, donc la
matière excédentaire reste inchangée. Fractions transférées publiées : `a = 1,000000`,
`b = 0,926359` (bloc de qualification). Changements réciproques : `Δz̄_A = +1,085`,
`Δz̄_B = −1,005`.

**Bijectif** avec inverse exact stocké (résidu 2,78·10⁻¹⁷). **Involutif seulement si
`M_A = M_B`** — déclaré, non affirmé : `P(P(x))` a un résidu de 1,96 quand `a ≠ 1`.
Appliqué **par tampon**, jamais en place. Identité hors cible.

```
STATE_OPERATOR = PHYSICALLY_CONSERVATIVE_RECIPROCAL
```

---

## Phases D/E — résultats, géométrie primaire, 10 blocs (61000–61009)

Quatre rechargements indépendants d'**un même checkpoint complet** par bloc.

| critère | moyenne | IC 95 % | p randomisation | latéralité scellée |
|---|---|---|---|---|
| **flux public précoce** (Σ 1..40) | **+2,877·10⁻⁵** | [2,62·10⁻⁵ ; 3,13·10⁻⁵] | **1,000** | unilatéral **négatif** |
| **médiateur public retardé** (t = 200) | **+6,654·10⁻⁴** | [6,54·10⁻⁴ ; 6,77·10⁻⁴] | **1,000** | unilatéral **négatif** |
| **`tau_on`** réponse retardée | **+0,00912** | [−0,00230 ; +0,02054] | **0,0977** | bilatéral |
| **`tau_off`** | **exactement 0,0** | [0 ; 0] | — | bilatéral |
| `tau_public_path` | +0,00912 | [−0,00230 ; +0,02054] | 0,0977 | bilatéral |

**Contrôles structurels, tous exacts :**
- `T4` exclusion à gain nul : champs publics **bit-identiques** dans **10 blocs sur 10** ;
  `tau_off` vaut **exactement 0,0**. Aucun chemin caché.
- `T5` : état public **bit-identique** à `t0` entre `SWAP` et `SHAM` dans tous les blocs, et le
  hachage public **diffère** en fin de course dans tous les blocs sous gain actif.
- `Σρz` : dérive maximale **2,11·10⁻¹⁵**.
- ITT : **10/10** blocs analysables, aucun exclu.

### L'échec, précisément

Le signe prédit a été **dérivé et scellé avant exécution** depuis `κ = 1 + g·tanh(z)` avec `g > 0` :
un `z` plus élevé augmente la perméabilité locale, le composant est une **source** nette de `c`,
donc drainer plus vite devait **abaisser** le `c` local. **Observé : positif**, avec un intervalle
serré excluant zéro. Le test unilatéral préenregistré donne donc `p = 1,000`.

L'effet public **existe** — il est réel, reproductible et non nul — mais il va dans la direction
**opposée** à la dérivation scellée. Et la réponse retardée ne bouge pas (`p = 0,098`).

**Hypothèse mécaniste, explicitement post hoc et NON TESTÉE** : la dérivation portait sur le `c`
au **pic** (les cellules du corps), tandis que le lecteur gelé mesure la **moyenne sur un disque
de rayon 8**, bien plus large que le corps (~21 cellules, rayon ~2,6). Une diffusion plus rapide
aplatit le profil : le pic baisse mais **l'anneau monte**, et la moyenne sur le disque est
dominée par l'anneau. Autrement dit, la dérivée scellée portait sur la **mauvaise fonctionnelle
de `c`**. Cette hypothèse n'est pas testée ici : la tester exigerait un **nouveau lecteur**, ce
que les règles d'arrêt interdisent après un échec.

---

## Table des portes

| porte | statut |
|---|---|
| `T0_PUBLIC_RATCHET` | **PASS** — aucun chemin privé, étiquette, traqueur, provenance ou résultat futur dans la dynamique, l'intervention, le lecteur ou la clé de bruit |
| `T1_PARENT_AND_CORRIGENDUM` | **PASS** — provenance exacte, six corrections résolues |
| `T2_EXACT_COUNTERFACTUALS` | **PASS** — R0–R10, 26/26 |
| `T3_VALID_Z_INTERVENTION` | **PASS** — `Σρz` exact, opérateur réciproque précommis, état public bit-inchangé à `t0` |
| `T4_GAIN_ZERO_EXCLUSION` | **PASS, bit-exact** — `tau_off = 0,0` exactement, 10/10 blocs |
| `T5_TWIN_BASELINE` | **PASS** — jumeaux bit-identiques, `ON_SWAP` diffère à `t0` seulement par `z` |
| `T6_PUBLIC_FLUX` | **ÉCHEC tel que préenregistré** — effet réel mais de signe inverse, `p = 1,000` |
| `T7_DELAYED_PUBLIC_MEDIATOR` | **ÉCHEC tel que préenregistré** — idem, `p = 1,000` |
| `T8_DELAYED_RESPONSE` | **ÉCHEC** — `tau_on` p bilatéral `= 0,098` |
| `T9_PUBLIC_PATH_ABOLITION` | contrôle **PASS** (abolition bit-exacte), mais sans effet à abolir |
| `T10_HELD_OUT` | **NON ATTEINTE** — la géométrie tenue à l'écart n'est **pas** ouverte |

---

## Adjudication

```
COUNTERFACTUAL_IMPLEMENTATION = VALID
STATE_OPERATOR                = PHYSICALLY_CONSERVATIVE_RECIPROCAL
PUBLIC_PATH_REGIME            = CONSTITUTIVE_PUBLIC_RESPONSE
                                (effet public réel, précoce ET retardé, mais de signe
                                 opposé à la dérivation scellée ; aucune réponse retardée)
REPLICATION                   = NOT_REACHED
EXACT_TWIN_DISPOSITION        = NOT_ESTABLISHED
Stops déclenchés              : PRIMARY_NOT_CONFIRMED, NO_DELAYED_RESPONSE
```

### Revendication maximale autorisée

> Dans un modèle d'interface adaptative explicitement construit et **intégralement
> déterministe**, des jumeaux de checkpoint complets ont été exposés au même futur exogène — qui
> est vide, le modèle ne tirant aucune variable aléatoire après le point de branchement. Une
> intervention réciproque préenregistrée sur `z`, conservant **exactement** `Σρz` et laissant
> l'état public **bit-inchangé** à `t0`, a produit une différence publique **réelle et
> reproductible** en flux précoce et en médiateur retardé, **de signe opposé à la dérivation
> scellée**. Elle **n'a pas** modifié la réponse retardée. L'effet disparaît de façon **bit-exacte**
> lorsque la contribution adaptative est ramenée à son gain natif nul alors que `z` reste intact.

N'est **pas** autorisé : appariement d'état public, régénération endogène de médiateur,
adressabilité sélective ou double dissociation, propriété ou individualité, fermeture causale
minimale, persistance au renouvellement, autonomie, métabolisme, organismalité, reproduction,
hérédité, vie, conscience ou AGI. Et la géométrie tenue à l'écart reste **scellée et inutilisée**.

**Score de papier : `FAIL` avant, `FAIL` après.** Ce qui est acquis est une **infrastructure de
contrefactuels exacts vérifiée** — checkpoints bit-exacts, jumeaux bit-identiques, opérateur
exactement conservatif, exclusion de chemin caché bit-exacte — et un **négatif mécaniste propre**.

---

## Positionnement dans la littérature

- **Contrefactuels exacts en matière simulée.** L'exclusion à gain nul **bit-exacte** (`tau_off`
  exactement `0,0`) est une garantie plus forte qu'une non-significativité statistique : elle
  prouve structurellement qu'aucun chemin résiduel n'existe. Peu de travaux sur la matière
  adaptative publient cette garantie.
- **Le piège du lecteur.** L'échec est instructif : la dérivée locale scellée était correcte sur
  le **pic** du champ, et le lecteur gelé mesurait une **moyenne de disque**. Toute préinscription
  de signe doit porter sur la **fonctionnelle effectivement lue**, pas sur la variable locale.
- **Interfaces dépendantes de l'état.** Un couplage `κ(z)` borné à 1,68× au clip modifie le champ
  public de façon mesurable (`2,9·10⁻⁵` en flux précoce, `6,7·10⁻⁴` en médiateur) mais bien en
  dessous de ce qu'il faudrait pour déplacer une réponse.

## Discipline

**67 démarrages moteur** sur 124 planifiés : 17 en qualification (plafond 24) et 50 en primaire.
Les 50 de la géométrie tenue à l'écart **ne sont pas consommés** — un échec primaire termine le
programme. Graines 61000–61009, jamais utilisées. Unité indépendante = le bloc fondateur.
Inférence par retournement de signe exact, valeurs brutes par bloc publiées. Portes
déterministes en égalité **bit à bit**, jamais en `p > 0,05`. Aucun conditionnement sur la
livraison, la lignée, la survie ou l'effet visible. Après cet échec, rien n'est ajouté : ni gain
plus fort, ni sauvetage à gain négatif, ni nouvel état, ni nouveau lecteur, ni nouvelle histoire,
ni nouvel opérateur, ni nouveau sous-ensemble, ni horizon supplémentaire.
