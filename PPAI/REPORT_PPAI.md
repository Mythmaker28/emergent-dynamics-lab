# `PUBLIC_PATH_ADAPTIVE_INTERFACE_00` — rapport

**2026-08-09** · parent `586108f43d8706183f4e8cde8735f866133d3ea7`
(branche `dev/core-halo-mismatch-recovery-00`, bundle SHA-256 **vérifié**
`9a41376f9defc7e6721b4efd596ad2b782507ea17492c04868ab3e8d3bb4a534`)
· `PROGRAM_STATUS = SEPARATE_MODEL_CONSTRUCTION, NOT_CONFIRMATION_OF_SC_MCM`
· `NEW_LAWSPEC_AUTHORIZED = true`, sous contraintes
· **18 nouvelles trajectoires** sur un maximum de 240 · 22/22 fixtures
· arrêt terminal avant tout bras confirmatoire

> **Verdict : `NO_WASH_WINDOW`.**
>
> La `LawSpec` construite est valide : elle se réduit **bit à bit** à la `LawSpec` racine gelée à
> gain nul, elle est positive et stable aux deux gains non nuls, elle ne contient **aucun** chemin
> privé, et son unique couplage nouveau réalise exactement le graphe causal autorisé.
>
> Mais le protocole ne peut pas démarrer : **l'état public des deux composants ne peut pas être
> apparié pendant que `z` reste séparé.** L'écart de halo tombe de 148 % à 48 % du niveau moyen en
> 560 pas sans jamais approcher les 10 % exigés, tandis que masse et taille **divergent** de 8 % et
> 5 % vers 46 % et 47 %. La séparation de `z` passe sous le plancher de 50 % vers t ≈ 480.
>
> **Ce n'est pas causé par le nouveau couplage.** Le même échec se produit à `ZERO_FEEDBACK`, où
> le moteur est bit-identique au `ScaffoldEngine` racine gelé. L'état public non appariable est
> **hérité** de la construction de fondation et d'histoires de `DOMC`/`CHMR`.
>
> La règle d'arrêt `NO_WASH_WINDOW` se déclenche. Aucun bras confirmatoire n'est exécuté : toutes
> les portes en aval sont conditionnées à un état public apparié. `MODEL_BUILDING_PAPER_GATE = FAIL`.

---

## Phase A — corrections apportées à `CHMR` (zéro appel moteur)

Sortie machine `ppai_phaseA.json`. Sceau `CHMR` intact, parent vérifié.

### A.1 Mouvements signés vers le prototype opposé — **la disposition mandatée est contredite par les artefacts bruts**

La mission demandait `OPPOSITE_STATE_OVERWRITE = NOT_ESTABLISHED` « sauf si les artefacts bruts
exacts démontrent le contraire ». Ils le démontrent, et je le rapporte tel quel.

| | FAR confirmatoire | NEAR tenu à l'écart |
|---|---|---|
| A (cœur H sous halo L) → prototype L | **+0,639** [+0,636 ; +0,648] | **+0,596** [+0,592 ; +0,601] |
| B (cœur L sous halo H) → prototype H | **+0,307** [+0,303 ; +0,315] | **+0,258** [+0,252 ; +0,264] |
| séparation H/L | 2,131 → **0,111** | 2,075 → **0,305** |

Les **deux** mouvements sont positifs, les deux intervalles excluent zéro, aux deux géométries.
Ce n'est donc pas seulement un effondrement de séparation : chaque cœur se déplace bien vers le
prototype opposé, de façon **asymétrique** (0,64 contre 0,31).

**Mais le critère directionnel n'était pas gelé avant les résultats de `CHMR`.** Un critère
post hoc peut *retirer* une revendication, jamais l'établir. La disposition retenue est donc :

```
OPPOSITE_STATE_OVERWRITE = NOT_ESTABLISHED
  (non réfuté non plus : NON ADJUDIQUÉ, faute de critère directionnel gelé.
   Les mouvements signés bruts sont publiés ci-dessus et vont dans le sens de l'écrasement.)
```

C'est la lecture rigoureuse : je ne peux pas transformer une observation en confirmation après
coup, et je ne peux pas non plus prétendre que les données disent le contraire de ce qu'elles disent.

### A.2 `CORE_CROSS` et `HALO_PULSE_RESTORE` : aucune marge d'équivalence gelée n'existe

| contraste (réponse signée A−B, moins l'appariée) | médiane | IC 95 % | p randomisation |
|---|---|---|---|
| `CORE_CROSS` à `T_RECOVERY`, FAR | +0,0120 | [−0,529 ; +0,303] | 0,621 |
| `CORE_CROSS` à `T_RECOVERY`, NEAR | +0,2643 | [+0,085 ; +1,291] | 0,351 |
| `HALO_PULSE_RESTORE` à la fin, FAR | +0,4183 | [−15,93 ; +1,395] | 0,354 |
| `HALO_PULSE_RESTORE` à la fin, NEAR | −12,807 | [−27,98 ; +3,005] | 0,062 |

Aucune marge d'équivalence n'avait été scellée pour ces contrastes. `p > 0,05` n'est pas une
équivalence.

```
FUNCTIONAL_INERTNESS = NOT_ESTABLISHED   (pour les deux bras, aux deux géométries)
```

### A.3 Ce que le TOST de `DOMC` testait réellement

L'estimand était **le déplacement hors cible seul**, `‖R_B(ERASE_A) − R_B(NONE)‖`, testé contre
`[−0,472 ; +0,472]` par TOST apparié au niveau des blocs. La marge est 10 % du déplacement *ciblé*
médian de la même opération, utilisée **uniquement comme échelle**.

Il ne teste **pas** 4,72 contre 3,1·10⁻⁶ ; ces deux nombres ne sont pas commensurables sous une
marge unique. Lecture correcte : *effacer le composant fortement écrit déplace son voisin d'une
quantité statistiquement équivalente à zéro à l'échelle déclarée* ; effacer le faiblement écrit
non (moyenne 16,7, IC 90 % [5,74 ; 27,69] contre ±1,877). `RESTRICTED_ONE_SIDED` inchangé.

### A.4 Maintenance : différences absolues, et générique ≠ spécifique à l'histoire

| | FAR confirmatoire | NEAR tenu à l'écart |
|---|---|---|
| écart de halo apparié à `T_RECOVERY` | 0,1349 | 0,1143 |
| écart de halo orphelin | 0,0782 | 0,0570 |
| **différence absolue** | **+0,0566** [+0,0540 ; +0,0579] | **+0,0573** [+0,0526 ; +0,0606] |
| en fraction de l'écart initial | **5,3 %** | **6,6 %** |

Les rapports `1,72×` et `2,01×` sont **retirés**.

```
GENERIC_HALO_RETENTION              = ESTABLISHED  (+0,057 d'écart absolu)
HISTORY_SPECIFIC_HALO_MAINTENANCE   = NOT_ESTABLISHED
```

`ORPHAN_HALO` retire la **matière**, pas l'**histoire** : le contraste apparié/orphelin confond
« un corps est présent et sécrète » avec « ce corps porte l'histoire qui a écrit ce halo ».
`CHMR` n'a aucun bras avec matière présente, halo non croisé et cœur sans histoire spécifique.
Le second ne se déduit pas du premier.

### A.5 Ablation de l'écrivain : un seul terme, effets hors cible petits mais non testés

`lam_minus` n'apparaît **qu'une fois** dans le corps exécutable de `step` : le facteur de
production d'attractant. Effets hors cible observés (`HALO_CROSS_WRITER_OFF` contre `HALO_CROSS`) :
`|Δ masse relative| ≤ 0,0027`, `|Δ taille| = 0`, viabilité intacte dans tous les blocs.

```
NON_TARGET_EQUIVALENCE = NOT_ESTABLISHED comme test formel
  (aucune marge n'avait été gelée ; les différences sont rapportées avec leurs intervalles)
```

### A.6 Nature probatoire des comptages de changements de lignée

```
18 / 27 / 19  =  PROSPECTIVE_STRUCTURAL_REPLAY
```

`results/sc_mcm` et `results/sc_iom` ne contiennent aucun état brut. Ces comptages proviennent de
**nouvelles exécutions** du monde gelé sous la connectivité gelée. Ils démontrent que
`largest(st)` est dangereux dans ce monde ; ils **ne peuvent pas** quantifier les changements dans
les trajectoires historiques effectivement rapportées. Preuve brute historique : **aucune**.

### A.7 Portée de l'invalidation

```
COMPONENT_LINEAGE_AND_TURNOVER_CLAIMS_USING_FRAMEWISE_LARGEST = NOT_AUDITABLE
INSTANTANEOUS_OR_WORLD_LEVEL_RESULTS                          = NOT_AUTOMATICALLY_INVALIDATED
```

La formulation « toute la ligne `sc_iom`/`sc_mcm` est invalidée » est retirée comme trop large.

### A.8 Formulation mécaniste

« filtre passe-bas du champ local » est retiré au profit de
`CONSISTENT_WITH_A_LEAKY_OR_LOW_PASS_TRACE` : aucune analyse de fonction de réponse ni
fréquentielle n'existe ; `CHMR` a échantillonné 12 fois une seule relaxation.

### A.9 Dispositions `CHMR` retenues

```
CHMR_DISPOSITION            = STATIC_ENVIRONMENTAL_CONTROL + PERSISTENT_INTERNAL_MARKER_EROSION
CORE_REBUILDS_HALO          = REFUTED
MUTUAL_CORE_HALO_ATTRACTOR  = REFUTED
HALO_TO_INTERNAL_MARKER     = PERSISTENT_CONTRAST_EROSION
OPPOSITE_STATE_OVERWRITE    = NOT_ESTABLISHED (non adjudiqué, cf. A.1)
FUNCTIONAL_HALO_REPROGRAMMING = NOT_ESTABLISHED
CURRENT_LOCAL_FIELD_CONTROL = SUPPORTED_NOT_EXCLUSIVE
PARENT_COMPONENT_TURNOVER   = NOT_IDENTIFIABLE
CHMR_LINEAGE_TURNOVER       = PASS_CHMR_ONLY
STRONG_PAPER_GATE           = FAIL
```

### A.10 Table complète `G0`–`G10` de `CHMR`, corrigée

| porte | statut | après correction |
|---|---|---|
| `G0_PROTOCOL` | PASS | protocole scellé `b1e4b065…` avant toute sortie confirmatoire |
| `G1_LINEAGE` | PASS | 0 scission, 0 fusion, 0 disparition sur 256 trajectoires |
| `G2_SURGERY` | PASS | multisets exacts, champs hors cible bit-identiques, `c` réalisé conservé à 4,5·10⁻¹³ |
| `G3_TIMESCALE` | PASS | résidu orphelin 0,0739 ≤ 0,10 à `T_RECOVERY = 350` |
| `G4_MISMATCH` | PASS | les quatre états distincts ; inversion exacte du halo |
| `G5_CORE_TO_HALO` | **ÉCHEC** | contraste primaire −0,111 ; `dir_A` mauvais signe |
| `G6_NECESSITY` | **NON APPLICABLE** | pas de nécessité pour une reconstruction inexistante ; l'ablation retire +0,024 de maintenance |
| `G7_HALO_TO_CORE` | **PASS sur le marqueur**, ÉCHEC sur la réponse | Δ = +0,452 / +0,399, p = 0,00049 ; réponse rand p = 0,354 / 0,062 → `FUNCTIONAL_INERTNESS = NOT_ESTABLISHED` |
| `G8_CAUSAL_RESPONSE` | PASS pour le halo courant, ÉCHEC pour le cœur | `CORE_CROSS` p = 1,00 (FAR) |
| `G9_TURNOVER` | PASS (`CHMR` seulement) | `M` = 0,187 / 0,200, lignées continues |
| `G10_HELD_OUT` | PASS | tout se réplique à NEAR |

---

## Phase B — audit causal structurel

### B.1 Le graphe de dépendance **ancien** (`sc_mcm`), au niveau des équations

```
N, c, uptake ──► Ψ = tanh(k_exp(N−c) + k_up(uptake−up_ref))     [engine l.154]
Ψ ──► m1, m2 ──► m₊ = m1+m2 ,  m₋ = m1−m2
m₊ ══► uptake        PRIVÉ  : g = … × (1 + lam_plus·tanh(m₊))    [l.79]   ← 1 saut vers le lecteur
m₋ ══► production c  PRIVÉ+ASYMÉTRIQUE : c += dt(… + s·ρ(1+lam_minus·m₋) …)  [l.116]
uptake ──► ρ ──► c ──► chimiotaxie ──► ρ
ρ, U, V, c ──► réponse au défi = [taille, rg, uptake spécifique, masse, c]
```

Chemins dirigés mémoire → réponse : `m₊ → uptake → uptake spécifique` (**direct, privé, 1 saut**),
`m₊ → uptake → ρ → taille/masse` (direct, privé, 2 sauts), `m₋ → production c → c → chimiotaxie`
(public mais **asymétrique en espèce**).

```
CLASSIFICATION = pas de DIRECT_PUBLIC_PATH ;
                 un DIRECT PRIVATE PATH (lam_plus) + une sécrétion asymétrique (lam_minus).
                 Aucun des deux ne correspond au graphe autorisé.
```

### B.2 Le graphe **nouveau** (`PPAI`)

```
N, c, uptake ──► Ψ ──► m1 = z ──► κ(z) = 1 + g·tanh(z)
κ ──► perméabilité de face, MÊME facteur pour c ET pour N
     ──► flux public réalisé c/N ──► ρ, géométrie ──► réponse au défi
```

Retirés : `lam_plus`, `lam_minus`, et l'héritage `Mf += g·m`.
Arêtes interdites vérifiées absentes : `z → réponse`, `z → force`, `z → survie`,
`z → lecteur de défi`, `z → identité de composant`.

```
CLASSIFICATION = DIRECT_PUBLIC_PATH par construction, et aucun chemin privé.
```

### B.3 Coefficients estimés sur les séries temporelles scellées de `CHMR`

| coefficient | valeur | identifiable |
|---|---|---|
| `K_ENV_TO_CORE` | **−0,01634** [−0,01761 ; −0,01466] par pas et par unité d'écart de halo | oui, n = 96 |
| `K_CORE_TO_ENV` | **−0,02658** [−0,02714 ; −0,02514] d'écart de halo excédentaire par unité d'écart de cœur | oui, n = 12 |
| `K_ENV_TO_RESPONSE` | pente **+66,7**, r = 0,596 | oui, n = 60 |
| `K_CORE_TO_RESPONSE_GIVEN_ENV` | **+0,726** contre `β_halo` = 74,8 → **rapport 0,0097** | oui, n = 60 |

Le cœur pèse donc **environ 1 %** de ce que pèse le halo sur la réponse, une fois le halo
partialisé. C'est la quantification exacte de la conclusion de `CHMR`.

**Aucune fonction de transfert n'est fabriquée** : 12 points sur une seule relaxation ne peuvent
pas identifier une réponse fréquentielle. Les quatre coefficients sont des pentes locales.

### B.4 Pourquoi désaturer l'écrivain ne réparerait pas le chemin manquant

L'écrivain sature : `N0` et `NN` stockent le **même** `m₊` à 10⁻⁴ près (mesuré en Phase C de
`DOMC`). Désaturer élargirait la **plage dynamique** de la valeur stockée. Cela ne créerait
**aucune arête de sortie**. Dans le graphe parent, les seules arêtes quittant la mémoire sont
`lam_plus` (privée, directement dans le lecteur) et `lam_minus` (sécrétion asymétrique). Un plus
grand nombre sur un fil qui ne mène nulle part de public reste une absence de propriété causale.
C'est pourquoi ce programme **ajoute une arête de sortie** et **retire les privées**, au lieu de
retoucher `eta_w` ou `k_exp`.

---

## Phase C — la `LawSpec` construite

**Coordonnée choisie et gelée avant tout résultat : `z = m1`.** C'est la coordonnée que la ligne
parente a certifiée robuste (`TCA-01` certifie `h1` ; `SMC-01` : `h2` s'homogénéise, `h1`
persiste ; `H2-CERT-01` : `h2` transitoire sous renouvellement profond), et c'est la seule non
saturée ici — `m2` sature à 1,0.

**Loi d'interface :**

```
κ(z) = 1 + g·tanh(z)                      bornée, impaire, centrée : κ(0) = 1 exactement
facteur de face = ½(κ(z_i) + κ(z_j))      symétrique → invariante par translation et rotation,
                                          symétrique dans l'étiquette de propriétaire
appliquée au transport diffusif de c ET de N, avec le MÊME facteur
```

`g ∈ {−1/3, 0, +1/3}`, **fixé et non optimisé** : la positivité impose `|g| < 1`, et la contrainte
gelée « contraste de perméabilité ≤ 2× le natif » donne `(1+g)/(1−g) ≤ 2`, soit `g ≤ 1/3`.
Contraste mesuré : **1,6805×**.

**La matière fraîche démarre à `z = 0`** : le terme d'héritage `Mf += g·m` du parent est **retiré**.
Toute persistance au renouvellement devrait être physiquement réécrite.

**Interface : `STATE_DEPENDENT_ADAPTIVE_INTERFACE`**, pas « memristive ». L'audit formel montre que
`z` change bien la conductance, mais que `z` est mis à jour par `Ψ(N−c, uptake−up_ref)`, une
dépendance aux **champs** et à l'absorption, non au **flux** de l'interface elle-même. La
condition memristive n'est donc pas vérifiée.

---

## Phase D — DEV borné : 6 blocs, 18 trajectoires

| porte | résultat |
|---|---|
| `G1.1` gain 0 reproduit la `LawSpec` racine gelée **bit à bit** sur 400 pas | **PASS**, `max|diff| = 0,000e+00` |
| `G1.2` la branche générale de flux égale `lap` à l'arrondi près | PASS, 2,22·10⁻¹⁶ |
| `G1.3–1.6` positivité, bornes, contraste ≤ 2×, `κ(0)=1`, imparité | PASS |
| `G1.7` stabilité 900 pas aux deux gains non nuls | PASS, tous champs finis et positifs |
| `G1.8` la matière fraîche démarre à `z = 0` | PASS (audit AST du corps exécutable) |
| `G1.9` aucun chemin privé `lam_plus`/`lam_minus` | PASS |
| `G0.1–0.4` anti-oracle, lecteurs aveugles à `z`, forçage global identique | PASS |
| `G4.0a` la permutation est une bijection exacte du champ intensif | PASS |
| `G4.0b` résidu de l'histogramme de `z` effectif | PASS, 50 cellules sur 4096 (1,2 %), tolérance mécanique gelée 5 % |
| `G4.1–4.4` `ρ,U,V,c,N,C` bit-identiques, involution 1,1·10⁻¹⁶, effacement propre, `|Δz| = 1,09` | PASS |
| **lignée** | 2 composants, **0 scission, 0 fusion, 0 disparition** dans les 18 trajectoires |

**Choix de `T_WASH` — critère gelé avant tout résultat de lavage :** appariement public à 10 %,
séparation de `z` maintenue à ≥ 50 %, sur 13 instants scellés.

```
T_WASH = AUCUN        WASH_WINDOW = NO_WASH_WINDOW
```

### Le premier statistique était mal posé, et je le déclare

Le critère gelé normalisait chaque différence publique A−B par **sa propre valeur au début du
lavage**. Masse et taille démarrent quasi égales (21 cellules contre 21) : ce dénominateur est
quasi nul et le critère exige qu'une différence déjà ≈ 0 le reste éternellement. C'est exactement
le piège du petit dénominateur que ce programme a corrigé dans `DOMC`.

J'ai donc recalculé avec un statistique **bien posé** — `|A−B|` divisé par le niveau moyen —
**avant qu'aucun résultat cible n'existe** : seul le diagnostic de lavage avait été calculé.

| t | `c` | `N` | `flux_c` | masse | taille | `rg` | séparation `z` |
|---|---|---|---|---|---|---|---|
| 0 | 1,478 | 0,024 | 0,331 | 0,081 | 0,049 | 0,056 | 1,000 |
| 200 | 0,933 | 0,025 | 0,500 | 0,463 | 0,556 | 0,229 | 0,987 |
| 400 | 0,593 | 0,018 | 0,421 | 0,467 | 0,471 | 0,199 | 0,553 |
| 560 | **0,477** | 0,015 | 0,382 | **0,462** | **0,471** | 0,195 | **0,306** |

L'état public **ne converge pas, il se sépare** : masse et taille passent de 8 % et 5 % à 46 % et
47 % et y restent. Le halo n'approche jamais 10 %. `z` passe sous le plancher vers t ≈ 480.

```
NO_WASH_WINDOW confirmé sous DEUX normalisations indépendantes.
```

### Ce n'est pas le nouveau couplage

| classe de gain | pire différence publique relative à t = 560 | séparation `z` | un instant passe-t-il 10 %/50 % ? |
|---|---|---|---|
| `NEGATIVE_FEEDBACK` | 0,561 (`c`) | 0,337 | **non** |
| `ZERO_FEEDBACK` (= racine gelée) | 0,520 (`c`) | 0,320 | **non** |
| `POSITIVE_FEEDBACK` | 0,477 (`c`) | 0,306 | **non** |

Le même échec se produit à gain nul, où le moteur est **bit-identique** au `ScaffoldEngine` racine.
L'état public non appariable est **hérité** de la fondation et des histoires de `DOMC`/`CHMR`,
pas créé par l'interface adaptative.

---

## Adjudication

```
INTERFACE                = STATE_DEPENDENT          (pas MEMRISTIVE : z est mis à jour par les
                                                     champs, pas par le flux d'interface)
CAUSAL_REGIME            = NOT_IDENTIFIABLE         (aucun bras confirmatoire n'a pu s'exécuter)
SELECTIVE_ADDRESSABILITY = NOT_ESTABLISHED
TURNOVER_PERSISTENCE     = NOT_IDENTIFIABLE
MINIMAL_CAUSAL_CLOSURE   = NOT_ESTABLISHED
MODEL_BUILDING_PAPER_GATE= FAIL
```

Porte `PPAI` : `G0` **PASS**, `G1` **PASS**, `G2` **PASS** (DEV), `G3_PUBLIC_STATE_MATCH`
**ÉCHEC → NO_WASH_WINDOW**, `G4`–`G10` **NON ATTEINTES**.

### Revendication maximale autorisée

> Une extension locale minimale a été construite dans laquelle une coordonnée interne déjà
> existante module la perméabilité publique de l'interface matière–bain aux deux champs `c` et `N`,
> avec un gain nul se réduisant **bit à bit** à la `LawSpec` racine gelée, une perméabilité
> strictement positive de contraste ≤ 1,68× le natif, aucun chemin privé de la mémoire vers la
> réponse, et une matière fraîche démarrant à `z = 0`. Le protocole confirmatoire **n'a pas pu
> démarrer** : dans cette géométrie de fondation, l'état public des deux composants ne peut pas
> être apparié pendant que leurs états internes restent séparés, et cette impossibilité est
> **héritée du substrat de fondation**, non créée par l'interface.

Rien d'autre n'est autorisé. Aucune revendication de fermeture causale, d'adressabilité, de
persistance au renouvellement, d'individualité, d'autonomie, de métabolisme, d'organismalité, de
reproduction, d'hérédité ou de vie.

**Score de papier : `FAIL` avant, `FAIL` après.** Le plafond de 88–91/100 exigeait `G3`–`G10` ;
`G3` échoue. Ce qui est acquis est une **`LawSpec` valide et un instrument vérifié**, pas un résultat.

---

## Positionnement dans la littérature

- **Interfaces memristives et matière adaptative.** La construction réalise la boucle
  flux → état → conductance → flux au niveau des équations, mais la mise à jour de l'état passe
  par les **champs** locaux, pas par le flux d'interface : c'est une interface **dépendante de
  l'état**, pas un memristor. La distinction est rarement faite dans la littérature sur la
  matière adaptative, et elle est vérifiable ici au niveau du code.
- **Appariement d'état public (« wash ») en matière active.** L'échec est instructif : deux corps
  pilotés différemment dans un même bain **ne reviennent pas** à un état public commun, parce que
  le pilotage change durablement leur **taille**. Tout protocole d'échange d'état en matière
  renouvelante doit apparier la morphologie, pas seulement le champ.
- **Bits matériels adressables.** L'adressabilité géométrique et la permutation conservative sont
  ici mécaniquement exactes (bijection du champ intensif, involution à 10⁻¹⁶). Ce qui bloque n'est
  pas l'adressage mais l'**appariement du contexte public**.

---

## Registre des revendications

| # | revendication | statut |
|---|---|---|
| 1 | la `LawSpec` construite se réduit bit à bit à la racine gelée à gain nul | **ÉTABLI** (0,000e+00 sur 400 pas) |
| 2 | la perméabilité est positive, bornée, de contraste ≤ 2× | **ÉTABLI** (1,6805×) |
| 3 | aucun chemin privé mémoire → réponse ne subsiste | **ÉTABLI** (audit AST du corps exécutable) |
| 4 | la permutation conserve exactement le champ intensif `z` | **ÉTABLI** ; résidu effectif 1,2 % déclaré |
| 5 | la lignée prospective est continue en DEV | **ÉTABLI** (0/0/0 sur 18 trajectoires) |
| 6 | l'état public peut être apparié pendant que `z` reste séparé | **RÉFUTÉ** (`NO_WASH_WINDOW`, 2 normalisations, 3 classes de gain) |
| 7 | l'échec d'appariement est causé par le nouveau couplage | **RÉFUTÉ** (identique à gain nul) |
| 8 | le cœur pèse ~1 % du halo sur la réponse, halo partialisé | **ÉTABLI** (rapport 0,0097) |
| 9 | désaturer l'écrivain réparerait le chemin causal | **RÉFUTÉ** structurellement (pas d'arête de sortie) |
| 10 | fermeture causale minimale | **NON ÉTABLI** |

---

## Discipline

- **18 nouvelles trajectoires sur 240.** Le maximum n'a pas été consommé : le protocole s'arrête
  à la porte `G3`, comme les règles d'arrêt l'exigent.
- 6 blocs de développement (40000–40005), jamais utilisés auparavant. Aucun bloc confirmatoire
  n'a été ouvert : les graines 41000+ restent vierges.
- Aucun conditionnement sur la survie, la chirurgie, la livraison ou la rétention de lignée.
- Conformément aux règles d'arrêt, après cet échec je n'ajoute **pas** : un gain plus fort, un
  second état interne, une sécrétion signée, une propulsion directe, un contrôleur ou un
  point de consigne, un autre lecteur, une autre durée de lavage, une autre paire d'histoires,
  ni une extension opportuniste d'horizon.
