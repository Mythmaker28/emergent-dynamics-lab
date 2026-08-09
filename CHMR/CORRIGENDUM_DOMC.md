# Corrigendum à `DUAL_OWNER_MEMORY_COLLISION_00` — enregistré, sans nouvelle exécution

`DOMC` (`1b4c80e03ef7637073edb581c7cbf6b346956860`) **n'est pas modifié**. Ses artefacts restent
scellés et vérifiés. Ce fichier corrige les **dispositions**, l'**estimand**, les **contrôles** et
le **statut probatoire**, à partir des seuls enregistrements bruts. Zéro appel moteur.

Sortie machine : `chmr_phaseA.json` · code `chmr_phaseA.py`.

---

## 0. Vérification du parent

| élément | valeur vérifiée |
|---|---|
| `PARENT_COMMIT` | `1b4c80e03ef7637073edb581c7cbf6b346956860` |
| ascendance | `b6bc514126ffd559407065eb89c07b4e950958ce` est ancêtre **direct**, distance exactement 1 commit |
| `PARENT_BUNDLE_SHA256` | **`29505e987fa8e5b541dfc3d172417befd3739078008191a97e9c372c2b8b661a`** (le préfixe/suffixe annoncé `29505e98…b661a` est confirmé sur l'artefact complet) |
| `git bundle verify` | *okay* ; contient `refs/heads/dev/dual-owner-memory-collision-00 → 1b4c80e` ; requiert `b6bc514` |
| sceau du protocole | intact ; les 5 fichiers de code scellés sont inchangés |
| séparation DEV / CONFIRM | **disjointe** : 34000–34011 contre 35000–35011 |
| registre d'allocation | 108 + 84 + 120 + 48 = **360 trajectoires** |

---

## 1. Dispositions corrigées

```
DOMC_DISPOSITION                    = COMPONENT_OWNERSHIP_NOT_ESTABLISHED
                                      + ENVIRONMENT_DOMINATED_RESPONSE
LOCAL_MARKER_SEPARABILITY           = ESTABLISHED
MEMORY_FIELD_MANIPULABILITY         = ESTABLISHED
FUNCTIONAL_SELECTIVE_ADDRESSABILITY = RESTRICTED_ONE_SIDED
EXCLUSIVE_ENVIRONMENTAL_MEDIATION   = NOT_ESTABLISHED
TURNOVER_PERSISTENCE                = MARKER_ONLY_PENDING_LINEAGE_AUDIT
CAUSAL_INDIVIDUATION                = NOT_ESTABLISHED
STRONG_PAPER_GATE                   = FAIL
```

`ENVIRONMENT_EXPLAINS`, la disposition scellée de `DOMC`, est **retirée** : elle sur-interprète.
L'échange d'environnement **amplifie** (`T = +1,61 > 1`), ce qui n'est pas un transport un-pour-un,
et la médiation exclusive par l'environnement n'a jamais été testée.

---

## 2. L'estimand : `NORMALIZED_TRANSFER_CONTRAST`, et il n'est pas borné

`T = ⟨c − a, b − a⟩ / ‖b − a‖²` est un **coefficient de projection** sur un axe non borné. Le
nom « fraction de transfert » suggérait une borne que l'estimand n'a pas. Renommé
`NORMALIZED_TRANSFER_CONTRAST`.

```
MEMORY_CROSS      = -0,276  [-0,355 ; -0,164]
→ ANTI-TRANSFERT significatif, PAS une absence d'effet

ENVIRONMENT_CROSS = +1,614  [+1,256 ; +1,732]
→ transfert AMPLIFIÉ, PAS un transport un-pour-un
```

### 2.1 Numérateurs et dénominateurs bruts, par bloc

Le dénominateur est `‖R_propre − R_autre‖²`, le carré de la longueur de l'axe d'histoire.

| jeu | échéance | dénominateur min / médian / max | rapport max/min | dénominateurs < 1 % de la médiane |
|---|---|---|---|---|
| FAR prospectif | `t0` | 2,71·10³ / 6,07·10³ / 1,63·10⁴ | **6,0×** | **0 / 24** |
| FAR prospectif | après renouvellement | **14,5** / 4,01·10³ / 4,16·10⁵ | **28 700×** | **5 / 24** |
| NEAR prospectif | `t0` | 708 / 1,75·10³ / 6,74·10³ | 9,5× | 0 / 24 |

**Correction majeure.** À `t0` les rapports ne sont pas pilotés par de petits dénominateurs :
l'étendue est de 6×, aucun dénominateur n'est petit. **Après renouvellement, cinq dénominateurs
sur vingt-quatre tombent sous 1 % de la médiane**, l'étendue atteint 28 700×, et la moyenne de `T`
explose à `+5,77 [−2,45 ; +13,98]` alors que la médiane vaut `+0,017`. **Tous les chiffres
post-renouvellement de `G5` dans le rapport `DOMC` — `+0,017` pour la mémoire, `+0,465` pour
l'environnement — sont retirés comme non interprétables.** Ils ne sont pas faux au sens du calcul :
ils sont des quotients par un axe d'histoire quasi nul.

### 2.2 Le contraste apparié direct

```
T_ENVIRONMENT − T_MEMORY   (même bloc, même axe, apparié)
  t0                      médiane +1,886  [+1,329 ; +1,980]   12/0 blocs   p = 0,00049
  après renouvellement    médiane +0,114  [−3,743 ; +0,485]    8/4 blocs   p = 0,39   (non interprétable, cf. 2.1)
```

C'est ce contraste, et non la comparaison de deux intervalles séparés, qui porte la conclusion.

---

## 3. Multiplicité

Holm-Bonferroni sur la famille confirmatoire telle qu'elle a réellement été exécutée (11 tests) :

| test | *p* brut | *p* Holm | survit |
|---|---|---|---|
| `G3` propriété `t0` FAR | 0,00049 | 0,0059 | oui |
| `G4` dissociation A `t0` | 0,00049 | 0,0059 | oui |
| `G5` `NTC` environnement `t0` | 0,00049 | 0,0059 | oui |
| `T_env − T_mem` `t0` | 0,00049 | 0,0059 | oui |
| `G3` propriété `t0` NEAR | 0,00049 | 0,0059 | oui |
| `G5` `NTC` mémoire `t0` **NEAR** | 0,00049 | 0,0059 | oui |
| `G5` `NTC` environnement après renouv. | 0,0064 | 0,038 | oui |
| **`G5` `NTC` mémoire `t0` FAR** | 0,0386 | **0,193** | **NON** |
| `G4` dissociation B `t0` | 0,146 | 0,584 | non |
| `G3` propriété après renouv. NEAR | 0,146 | 0,584 | non |
| `G3` propriété après renouv. FAR | 0,388 | 0,775 | non |
| `G5` `NTC` mémoire après renouv. | 0,388 | 0,775 | non |

**Conséquence.** L'anti-transfert mémoire **ne survit pas** à la correction de multiplicité **à la
géométrie FAR** (`p` Holm = 0,193). Il y survit **à la géométrie NEAR** (`p` Holm = 0,0059, 0/12
blocs positifs). L'énoncé exact est donc : *anti-transfert significatif à la géométrie
rapprochée, direction cohérente mais non significative après multiplicité à la géométrie
éloignée.*

---

## 4. Les contrôles chirurgicaux exacts

| contrôle | résultat |
|---|---|
| `AA_CROSS` — déplacement | médiane **0,698** [0,423 ; 0,922], p = 0,0005 : la chirurgie **n'est pas** un no-op |
| `AA_CROSS` — projection sur l'axe d'histoire | **+0,0023** [+0,00005 ; +0,0075], p = 0,146 : elle est **orthogonale** à l'axe mesuré |
| `AA_CROSS_ENV` — déplacement | 0,212 [0,022 ; 0,277], p = 0,0005 |
| `AA_CROSS_ENV` — projection | **−0,00002** [−0,0028 ; +0,0001], p = 1,00 |
| `NO_OP_PERMUTATION` — `ERASE_SHAM` bit-exact sur tout l'état | **PASS** |
| `NO_OP_PERMUTATION` — permutation appliquée deux fois = identité (mémoire) | **PASS** |
| `NO_OP_PERMUTATION` — idem pour la permutation d'environnement | **PASS** |
| `SURGERY_ONLY` — la permutation laisse `rho, U, V, c, N, C` bit-identiques | **PASS** |
| `SURGERY_ONLY` — la permutation d'environnement laisse `rho, U, V, C, Mf` bit-identiques | **PASS** |

Correction : `DOMC` rapportait un « plancher mécanique » de 0,155. Le déplacement chirurgical réel
est **0,698**, quatre fois plus grand. Ce qui sauve l'inférence n'est pas sa petitesse mais son
**orthogonalité** : projeté sur l'axe d'histoire, il vaut 0,0023, soit 0,8 % de l'effet mémoire
mesuré. C'est le bon argument, et ce n'est pas celui que `DOMC` avançait.

---

## 5. Effacement : valeurs absolues, incertitude, test d'équivalence

Le rapport `1,08 million ×` n'est **plus** le titre. C'est le quotient d'un grand effet ciblé par
un effet non ciblé quasi nul ; un tel quotient est instable et non informatif.

| grandeur | médiane | IC 95 % | étendue |
|---|---|---|---|
| effacer A → **cible** A | **4,717** | [3,533 ; 6,276] | [3,019 ; 9,363] |
| effacer A → **hors cible** B | **3,09·10⁻⁶** | [2,25·10⁻⁶ ; 9,57·10⁻⁶] | [1,61·10⁻⁶ ; 9,46·10⁻⁵] |
| effacer B → **cible** B | **18,767** | [15,39 ; 24,60] | [11,16 ; 30,71] |
| effacer B → **hors cible** A | **7,532** | [5,26 ; 15,15] | [3,90 ; 61,43] |

Test d'équivalence réel (TOST apparié, marge = 10 % de l'effet ciblé médian de la même
opération) :

- **côté A** : marge ± 0,472 ; moyenne 1,36·10⁻⁵, IC 90 % [−1,1·10⁻⁷ ; 2,7·10⁻⁵] → **ÉQUIVALENT**.
  L'effacement du composant fortement écrit est sans effet mesurable sur l'autre.
- **côté B** : marge ± 1,877 ; moyenne 16,72, IC 90 % [5,74 ; 27,69] → **NON ÉQUIVALENT**.
  L'effacement du composant faiblement écrit déplace l'autre de 40 % de son propre effet.

D'où `FUNCTIONAL_SELECTIVE_ADDRESSABILITY = RESTRICTED_ONE_SIDED`.

---

## 6. `H_GLOBAL` : ce qui était « réfuté par construction » ne l'était pas

`DOMC` écrivait que `H_GLOBAL` est réfutée par construction parce que les deux affectations ont une
série de forçage identique pas à pas. **Seul le forçage *tenté* était équilibré par construction.**
Les quantités globales *réalisées* n'ont jamais été enregistrées par `DOMC`.

Ce que les enregistrements bruts permettent d'établir, sans moteur :

| grandeur observée (à `t0`, 12 blocs) | médiane |
|---|---|
| résidu d'antisymétrie intra-monde `‖Δ_AB + Δ_BA‖ / échelle` | **0,292** |
| différence de somme au niveau du monde `‖Σ_AB − Σ_BA‖ / échelle` | **0,132**, sign test **p = 0,0005** |

Il existe donc une **différence au niveau du monde, statistiquement détectable**, valant environ
**13 %** du contraste intra-monde ; et les deux affectations ne sont pas des images miroir exactes
(résidu 29 %). `H_GLOBAL` n'est pas réfutée : elle est **bornée**. L'effet mesuré reste
majoritairement intra-monde, mais la composante mondiale est réelle et doit être déclarée.

Le registre des quantités globales *réalisées* devient une exigence de `CHMR-00`, où il est
enregistré à chaque intervention.

---

## 7. Reclassification probatoire

`G3` (propriété locale) **échoue après renouvellement matériel** dès la première exécution complète
de développement. Tout ce qui a été **sélectionné ou exécuté après** cet échec est reclassé :

```
EXPLORATORY_POST_GATE_FAILURE
  · le balayage Phase C des 8 paires d'histoires
  · domc_FAR_DEV_cc-00
  · domc_FAR_PROSP_cc-00
  · domc_NEAR_PROSP_cc-00
```

Ces exécutions restent des **confirmations valides de leur propre protocole rescellé**, qui est un
ensemble d'hypothèses différent et plus étroit. Mais **aucun résultat `DOMC` ne peut être invoqué
comme preuve confirmatoire pour `G4`–`G9` de la chaîne originelle.** `CHMR-00` doit établir sa
propre chaîne confirmatoire, ce qu'il fait avec des blocs fondateurs jamais utilisés.

---

## 8. Score de force du papier

| | avant | après |
|---|---|---|
| propriété causale par composant | revendiquée réfutée par un critère primaire scellé | **NOT_ESTABLISHED** ; le critère primaire ne survit pas à la multiplicité à FAR |
| médiation environnementale | `ENVIRONMENT_EXPLAINS` | **NOT_ESTABLISHED** (amplification, pas transport) |
| persistance au renouvellement | établie (`M = 0,240`, 100 % sous le seuil) | **MARKER_ONLY_PENDING_LINEAGE_AUDIT** (cf. Phase L) |
| chaîne confirmatoire `G4`–`G9` | prospective | **EXPLORATORY_POST_GATE_FAILURE** |
| `STRONG_PAPER_GATE` | — | **FAIL** |
