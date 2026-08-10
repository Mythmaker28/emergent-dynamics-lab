# CORRIGENDUM BORNÉ — `EXACT_ENDPOINT_FUNCTIONAL_CONGRUENCE_AUDIT_00` (EEFCA)

**Émis par** `EXACT_TWIN_NATIVE_BOUNDARY_FLUX_CONFIRMATION_00` (ETNBFC), avant tout démarrage
moteur visant une cible.
**Commit parent (résolu, non deviné)** `de1524b22ff917dff1da6553f778a4f8019ac273`
— `git rev-parse de1524b` sans ambiguïté, `--disambiguate` renvoie une seule référence.
**Grand-parent** `3f8dae8bbe2937c43661ba8adfe8aed63bf6b6ee`.
**Nature** : ajout en annexe. **Aucune sortie parente n'est réécrite.**

Six corrections étaient exigées. Elles sont traitées une par une.

---

## 1. La matrice algébrique proposée par l'audit : portée réelle

EEFCA §2.2 a démontré que, pour toutes masses `M_A, M_B > 0` et tout `p`, la matrice

```
P = [[p, M_B(1+p)/M_A], [M_A(1−p)/M_B, −p]]
```

est involutive et conservatrice. **Cette démonstration reste valide, mais uniquement dans
l'algèbre agrégée exacte sur le couple de scalaires `(z̄_A, z̄_B)`.** Elle n'a **pas** été
établie, et n'est pas ici revendiquée, comme :

| propriété | statut réel |
|---|---|
| involution **bit-exacte sur le champ complet** | **NON DÉMONTRÉE.** Le calcul portait sur deux scalaires. Une application affine sur des moyennes, réinjectée site par site en flottant, n'a aucune raison de restaurer l'état sérialisé bit pour bit. |
| **admissibilité de domaine** | **NON DÉMONTRÉE.** Aucune vérification que `\|Mf[0]_i\| ≤ ρ_i` reste satisfaite site par site après application, ni que la porte `alive` est respectée. |
| **préservation des parcelles** | **FAUSSE PAR CONSTRUCTION.** Un décalage additif de moyenne ne transporte aucune parcelle de matière : il réécrit un champ en place. |
| **échange physique** | **NON.** Rien n'est déplacé d'un site à un autre. C'est une réécriture de coordonnée, pas un échange. |

La formulation d'EEFCA « une involution conservatrice **existait** et n'a pas été utilisée » est
donc **trop forte**. Formulation corrigée :

> Une involution conservatrice existait **au niveau de l'algèbre agrégée où ETPC avait posé son
> opérateur**. Elle aurait suffi à réparer le défaut algébrique constaté, mais elle n'était pas
> pour autant l'opérateur physique correct, et EEFCA ne l'a jamais qualifiée comme tel.

---

## 2. Retrait de l'argument d'« incommensurabilité » des masses flottantes

EEFCA §B2.3 écrivait : *« Δz̄_A = +1,085064 et Δz̄_B = −1,005159 ; ces deux nombres sont
incommensurables en double précision, donc une variation flottante exactement nulle impose
n_A^bnd = n_B^bnd = 0. »*

**Cet argument est retiré.** Il est faux. Tout `float64` est un rationnel dyadique ; deux `float64`
non nuls sont toujours commensurables. Un argument d'incommensurabilité ne peut rien établir sur
des flottants. C'était un raisonnement de plausibilité déguisé en preuve.

**Méthode correcte, appliquée ici : inventaire exact de la représentation.** Les quatre points de
départ de développement (`61000–61003`, géométrie `FAR`) ont été **rejoués** et enregistrés
durablement, puis le masque de frontière du registre a été énuméré cellule par cellule.

| bloc | rejeu bit-identique au hash ETPC commis | cellules de frontière | cellules de composante | **intersection** |
|---|---|---|---|---|
| 61000 | **oui** | 128 | 42 | **0** |
| 61001 | **oui** | 128 | 42 | **0** |
| 61002 | **oui** | 128 | 42 | **0** |
| 61003 | **oui** | 128 | 42 | **0** |

**La conclusion d'EEFCA est confirmée — par la bonne méthode.** Le masque
`{alive & ¬roll(alive)}` avec `alive = ρ > 1e-4` est **exactement disjoint** de l'ensemble
intervenu, donc l'invariance de l'exposition `z` à la frontière est bien vide de contenu.

**Limite déclarée :** l'inventaire couvre **4 des 10 blocs** — le plafond de blocs de
développement fixé par l'autorisation. C'est un échantillon vérifié, pas l'ensemble complet.

*Effet secondaire utile :* les hachages logiques des quatre points de départ rejoués sont
**identiques bit pour bit** à ceux commis par ETPC, dans une autre session et un autre processus.
C'est une preuve indépendante de reproductibilité computationnelle bit-exacte.

---

## 3. ETPC est publié comme matériellement dévié de l'autorisation de Tommy

Sans atténuation :

```
ETPC_AUTHORIZED_OPERATOR_CONFORMANCE = FAIL
    l'opérateur exécuté n'était pas involutif : P² ≠ I dans les dix blocs,
    facteur de contraste résiduel 0,826 à 0,950 après deux applications.

ETPC_AUTHORIZED_ENDPOINT_CONFORMANCE = FAIL
    le point de mesure exécuté était une moyenne de c sur un disque de rayon 8
    (≈ 197 cellules pour un corps de ≈ 21), et non le flux réalisé natif de c ET N
    aux liens matière–bain. N n'était jamais lu.

ETPC_CONFIRMATORY_VALIDITY = INVALID_FOR_AUTHORIZED_HYPOTHESES
ETPC_NATIVE_REALIZED_C_N_BOUNDARY_FLUX = NOT_TESTED
ETPC blocks 61000–61009 = DEVELOPMENT_ONLY, définitivement.
```

---

## 4. L'oracle d'involution à littéral `True` est un PASS faussement induit

`chk('R7_PERMUTATION', 'test_swap_bijection_and_involution', True, …)` — la condition affirmée
était la constante de compilation `True`, établie par analyse AST. La porte a été enregistrée
**PASS** alors qu'elle ne testait rien, et la propriété qu'elle nomme est **fausse** : le résidu
`P(P(x))` mesuré valait `1,958e+00`.

```
INDUCED_FALSE_PASS = CONFIRMED
```

La mention « DECLARED, not asserted » dans la chaîne de détail est versée au dossier comme
circonstance, **pas** comme excuse : le verdict lisible par machine était PASS.

---

## 5. L'explication du signe inversé du disque est **intestable** pour les anciennes données

`etpc_run.py` écrivait chaque point de contrôle `.npz` dans un `tempfile.mkdtemp()` jamais commis.
Aucun champ `c`, `N`, `ρ` ou `Mf` d'ETPC n'a survécu. L'hypothèse « le disque agrège une région où
le laplacien change de signe » **ne peut pas être testée sur ces données**, ni confirmée ni
réfutée. Elle reste une hypothèse nommée et ne doit jamais être citée comme explication établie.

```
OPPOSITE_SIGN_MECHANISM = UNTESTABLE_ON_THE_OLD_DATA
```

*Réparation appliquée ici :* les points de contrôle de développement de ce programme sont
enregistrés dans `ETNBFC/checkpoints/`, hachés et commis. Aucun `tempfile` non livré.

---

## 6. L'infrastructure utile est séparée de l'interprétation confirmatoire invalide

Ce qui **survit** intact, et doit être réutilisé :

```
ETPC_CHECKPOINT_TWIN_INFRASTRUCTURE  = VALID_IN_AUDITED_FIXTURES
ETPC_POST_BRANCH_RANDOMNESS          = ABSENT_IN_AUDITED_ENGINE
ETPC_GAIN_ZERO_PUBLIC_EXCLUSION      = BIT_EXACT_IN_10_DEVELOPMENT_BLOCKS
BITWISE_COMPUTATIONAL_REPRODUCIBILITY = ESTABLISHED
    (renforcé ici : rejeu inter-session bit-identique sur 4 blocs)
```

Ce qui est **invalide**, et ne doit jamais être cité :

```
ETPC_CONFIRMATORY_VALIDITY = INVALID_FOR_AUTHORIZED_HYPOTHESES
ETPC_DELAYED_RESPONSE_EFFECT = NOT_ESTABLISHED
ETPC_DELAYED_RESPONSE_NULL   = NOT_ESTABLISHED
```

Les deux ne se contaminent pas : le premier est une infrastructure de calcul vérifiée,
le second une inférence scientifique retirée.

---

## Héritage gelé, préservé sans inflation

```
PPAI_GAIN_ZERO_REPRODUCES_CONSTRUCTED_EXPURGATED_BASELINE = ESTABLISHED
ORIGINAL_PARENT_NESTED_NULL                               = NOT_ESTABLISHED
OLD_GRAPH = DIRECT_PRIVATE_READER_PATH + WEAK_ENVIRONMENT_MEDIATED_PUBLIC_PATH
CORE_TO_HALO_0.97_PERCENT_CLAIM                           = WITHDRAWN
CHMR_ARITHMETIC                                           = RECONCILED_EXACTLY
ETPC_OPERATOR = BIJECTIVE_NONINVOLUTIVE_MASS_CONSERVING_AFFINE_MEAN_TRANSFER
ETPC_HELD_OUT = NOT_REACHED_AND_UNOPENED
```
