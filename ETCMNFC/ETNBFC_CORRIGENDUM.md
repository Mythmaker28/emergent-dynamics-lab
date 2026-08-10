# CORRIGENDUM BORNÉ — `EXACT_TWIN_NATIVE_BOUNDARY_FLUX_CONFIRMATION_00` (ETNBFC)

**Émis par** `EXACT_TWIN_CANONICAL_MF0_NATIVE_FLUX_CONFIRMATION_00` (ETCMNFC), **avant** tout
démarrage moteur porteur de cible.
**Commit parent résolu** `d86d24864e0f88c6483d11bcde601d1f13221a82` (`git rev-parse` sans
ambiguïté ; ascendance directe depuis `de1524b22ff917dff1da6553f778a4f8019ac273`, un seul commit).
**Nature** : ajout en annexe. **Aucune sortie du parent n'est réécrite.**

Six points étaient exigés.

---

## 1. L'arrêt d'ETNBFC était correct sous son propre protocole gelé

Sans réserve. Sous la clé d'appariement gelée d'ETNBFC — `bytes(rho_i)`, correspondance exacte,
tolérance interdite — il n'existait aucune paire inter-composante sur les quatre points de
contrôle audités, et le prouver était la bonne conduite. De même, sa porte `F10` exigeait un
registre par face dans les bras OFF, et l'implémentation native à gain nul est un calcul fusionné
`lap(X)` sans objet par face réalisé. Les deux constats sont exacts et restent au dossier.

```
ETNBFC_STOP_UNDER_ITS_OWN_PROTOCOL = CORRECT
```

---

## 2. Zéro support à `ρ` exact n'est **pas** un théorème d'impossibilité

C'est ici que le rapport parent a dépassé ses données. Mesurer 0 paire à `ρ` byte-identique sur
quatre blocs de développement établit que **cette clé-là** n'a pas de support. Cela n'établit
**pas** :

```
NO_BYTE_LEVEL_CONSERVATIVE_INVOLUTION_EXISTS   <-- NON ÉTABLI, et maintenant RÉFUTÉ
```

**Réfuté par construction.** Si le porteur canonique est `x_i = Mf[0]_i` et le contenu physique
`Q = Σ_i w_i x_i`, alors échanger les octets bruts entre deux sites donne

```
ΔQ_paire = (w_i − w_j) · (x_j − x_i)
```

Des **poids de stockage identiques** suffisent donc à la conservation exacte. `ρ_i = ρ_j` n'était
nécessaire que pour la description plus forte — et abandonnée — d'un échange de valeurs
*intensives* `z` entre parcelles de masse égale.

**Vérifié sur les blocs réels, pas seulement en algèbre.** Avec `w ≡ 1` (établi par conséquence :
des poids délibérément non uniformes brisent la conservation sous la même permutation), la
transposition d'octets bruts sur les paires appariées donne, sur les quatre blocs de
développement, **21 paires par bloc, dont 21 à `ρ` différent** :

| bloc | paires | paires à `ρ` **inégal** | `ΔQ_A = −ΔQ_B` (rationnel exact) | domaine sans écrêtage |
|---|---|---|---|---|
| 61000 | 21 | **21** | ±14,4009… | oui |
| 61001 | 21 | **21** | ∓14,4481… | oui |
| 61002 | 21 | **21** | ±14,4989… | oui |
| 61003 | 21 | **21** | ∓14,3417… | oui |

Multi-ensemble brut de `Mf[0]` préservé ; contenu rationnel exact `Q` préservé ; involution
**bit-exacte sur l'état complet** ; seul `Mf[0]` modifié ; projection publique bit-identique à
`t0`. **60/60 portes hors ligne**, contrôles adversariaux compris.

Tommy avait raison, et la bifurcation que j'avais proposée — fondation en miroir **ou** réécriture
du noyau OFF — était un **faux dilemme**. Je le retire.

---

## 3. Une permutation brute de `Mf[0]` est involutive sans `ρ` égal ; sa conservation dépend des poids ; son domaine doit être vérifié

Les trois propriétés sont maintenant séparées proprement :

| propriété | ce dont elle dépend réellement |
|---|---|
| **involution octet** | rien d'autre que la disjonction des 2-cycles |
| **conservation exacte de `Q`** | **poids de stockage identiques** (`w_i = w_j`), et rien d'autre |
| **admissibilité de domaine** | `\|x_j\| ≤ ρ_i` **et** `\|x_i\| ≤ ρ_j`, plus la porte `alive`, vérifiées paire par paire |

Deux avertissements, tous deux soulevés par les relecteurs indépendants et adoptés :

- **`Q` n'est pas un invariant dynamique.** L'opérateur préserve `Q` **à `t0`**. Un pas natif fait
  passer `Q` de 0,184192 à 0,152807 (mort `keep = 1 − dt·k`, reconstruction `Mf = ρ·newm`).
  « Opérateur conservateur » ne doit jamais se lire « grandeur conservée ».
- Ce n'est **ni** une transplantation de `z`, **ni** un échange de parcelles matérielles.
  Les `ρ` étant inégaux, l'état intensif d'après échange est `z'_i = Mf[0]_j / ρ_i` : des valeurs
  qui n'existaient nulle part avant. `ρ` n'est pas touché ; aucune matière ne se déplace.
  Le nom exact est **redistribution du porteur canonique**.

---

## 4. L'absence de registre par face OFF n'empêche pas une exclusion structurelle

La porte `F10` d'ETNBFC exigeait l'identité des flux d'événements par face dans les bras OFF.
Cette exigence était **plus forte que la science ne le demande**. Une exclusion de voie
structurelle suffit, et elle est établie ici sans inventer une seule face :

1. **Statique.** À `gain == 0` le noyau exécute `return lap(X)` sans lire `kap`, et la branche
   teste le **paramètre** `self.par.gain`, jamais une valeur d'état : le flot de contrôle ne peut
   donc pas dépendre de `Mf[0]` non plus.
2. **Dynamique.** Sur les blocs de développement, `OFF_SWAP` et `OFF_SHAM` ont des projections
   publiques **bit-identiques** après la fenêtre gelée — `ρ, U, V, c, N, C, uptake` **et `Mf[1]`**,
   champ non cible inclus délibérément — alors que `Mf[0]` diffère réellement.

Le relecteur indépendant a durci ce résultat : il a remplacé l'échange par six perturbations, dont
`z ≡ +1` saturé, `Mf[0] ≡ 0` et **une injection de NaN**. Dans tous les cas, les sept tableaux
publics plus `Mf[1]` restent bit-identiques après un pas. Qu'un NaN n'atteigne aucun champ public
rend l'exclusion **structurelle et non numérique**.

```
GAIN_ZERO_PUBLIC_PATH_EXCLUSION = PASS_BIT_EXACT (fenêtre d'un cycle, blocs de développement)
```

Portée déclarée : établi **pour le seul cycle d'échange gelé testé**. Non généralisé à une
évolution ultérieure ni à un autre opérateur. Et il faut le dire nettement : à `g = 0`,
`κ(z,0) = 1` identiquement, donc cette porte est **proche d'une tautologie**. Sa valeur réelle est
étroite mais authentique — elle exclut une fuite d'implémentation (aliasing, mutation en place).
**Ce n'est pas un contrôle scientifique et cela ne porte aucun contenu inférentiel sur les bras ON.**

---

## 5. Fondation en miroir et réécriture du noyau OFF ne sont pas autorisées

```
MIRROR_FOUNDATION  = forbidden
OFF_KERNEL_REWRITE = forbidden
```

Aucune des deux n'a été tentée, et aucune n'était nécessaire : le point 2 montre que l'opérateur
existait sans elles, et le point 4 que l'exclusion OFF s'obtient sans toucher à `lap(X)`.

---

## 6. La question causale `c`/`N` reste `NOT_TESTED`

```
ETNBFC_TARGET_C = NOT_TESTED       (et non NOT_ESTABLISHED, et surtout pas NO_EFFECT)
ETNBFC_TARGET_N = NOT_TESTED
```

Rien n'a été mesuré à propos d'un effet causal de la redistribution du porteur sur le transport
public — ni par ETNBFC, ni par ETCMNFC.

---

## Héritage gelé, préservé sans inflation

```
PPAI_GAIN_ZERO_REPRODUCES_CONSTRUCTED_EXPURGATED_BASELINE = ESTABLISHED
ORIGINAL_PARENT_NESTED_NULL                               = NOT_ESTABLISHED
CHMR_ARITHMETIC                                           = RECONCILED_EXACTLY
ETPC_CHECKPOINT_TWIN_INFRASTRUCTURE                       = VALID_IN_AUDITED_FIXTURES
ETPC_GAIN_ZERO_PUBLIC_EXCLUSION                           = BIT_EXACT_IN_10_DEVELOPMENT_BLOCKS
ETPC_AUTHORIZED_OPERATOR_CONFORMANCE                      = FAIL
ETPC_AUTHORIZED_ENDPOINT_CONFORMANCE                      = FAIL
ETPC_CONFIRMATORY_VALIDITY                                = INVALID
ETPC_10_BLOCKS                                            = DEVELOPMENT_ONLY
ETPC_DEVELOPMENT_DISK_C_EFFECT        = OBSERVED_CAUSALLY_BUT_NONCONFIRMATORY
ETPC_DEVELOPMENT_DELAYED_PUBLIC_MEDIATOR = OBSERVED_BUT_NONCONFIRMATORY
ETPC_NATIVE_REALIZED_C_N_BOUNDARY_FLUX                    = NOT_TESTED
ETPC_DELAYED_RESPONSE_EFFECT                              = NOT_ESTABLISHED
ETPC_HELD_OUT                                             = UNOPENED
EEFCA_CORRIGENDUM                                         = COMPLETE_AS_REPORTED
EEFCA_FLOAT_INCOMMENSURABILITY_ARGUMENT                   = WITHDRAWN
EEFCA_AGGREGATE_REFLECTION_SCOPE                          = BOUNDED_CORRECTLY
ETNBFC_EQUAL_RHO_SUPPORT_ON_4_DEV_BLOCKS                  = EXACTLY_ZERO_AS_REPORTED
ETNBFC_ON_FACE_LEDGER_RECONSTRUCTION                      = PASS_BIT_EXACT_AS_REPORTED
ETNBFC_OFF_NATIVE_FACE_LEDGER                             = NOT_AVAILABLE_AS_REPORTED
ETNBFC_TARGET_C                                           = NOT_TESTED
ETNBFC_TARGET_N                                           = NOT_TESTED
ETNBFC_PRIMARY_IDS                                        = NOT_ALLOCATED
ETNBFC_HELD_OUT                                           = UNOPENED
ETNBFC_DISPOSITION                                        = NOT_TESTED
ETNBFC_PROPOSED_FORK                                      = FALSE_DILEMMA_WITHDRAWN   <-- nouveau
```

Chaque revendication héritée a été revérifiée contre les preuves brutes commises avant d'être
reprise. Aucun écart de provenance n'a été trouvé : le commit parent, son ascendance et son bundle
se résolvent exactement ; le registre des huit démarrages du parent réconcilie ; aucun identifiant
primaire ni objet tenu à l'écart n'avait été ouvert.

**Constat supplémentaire, positif.** `PARENT_HELD_OUT_IDENTITY_COMMITMENT` était marqué
`TO_BE_VERIFIED`. Il est désormais **VÉRIFIÉ** : les identifiants `62000–62009` et la classe de
géométrie `NEAR` sont écrits dans `ETPC/etpc_run.py`, dont le sha256 figure dans le `code_sha256`
scellé de `ETPC/etpc_protocol.json`, commis en `3f8dae8b…`. Il s'agit donc bien d'un engagement
d'identité **auditable et antérieur aux résultats**, et non d'une désignation rétrospective.
