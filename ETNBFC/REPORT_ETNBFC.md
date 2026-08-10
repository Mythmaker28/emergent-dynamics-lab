# `EXACT_TWIN_NATIVE_BOUNDARY_FLUX_CONFIRMATION_00` (ETNBFC)

**Branche** `confirm/exact-twin-native-boundary-flux-00`
**Parent (résolu)** `de1524b22ff917dff1da6553f778a4f8019ac273` — EEFCA
**Grand-parent** `3f8dae8bbe2937c43661ba8adfe8aed63bf6b6ee` — ETPC
**Autorisation** Tommy, 2026-08-10, `oui_go`
**Démarrages moteur** `8` sur un plafond de qualification de `24`
**Contrastes cibles ouverts** `0` · **blocs primaires** `0` · **géométrie tenue à l'écart** `intacte`

---

## 0. Résultat

Le programme s'arrête en qualification, **avant tout point de mesure**, sur un arrêt terminal
prévu par le protocole lui-même. Il s'arrête pour **deux raisons structurelles indépendantes**,
toutes deux établies par mesure exacte et non par argument.

```
STATE_OPERATOR               = CONSERVATIVE_SWAP_UNAVAILABLE
COUNTERFACTUAL_IMPLEMENTATION = NOT_TESTED
NATIVE_FLUX_OBSERVER         = NOT_AVAILABLE  (aux bras à gain nul)
PRIMARY_NATIVE_BOUNDARY_FLUX = NOT_TESTED
GAIN_ZERO_EXCLUSION          = NOT_TESTED     (au niveau du registre exigé)
REPLICATION                  = NOT_REACHED
ETNBFC_DISPOSITION           = NOT_TESTED
```

`NOT_TESTED` n'est pas `NOT_ESTABLISHED`, et encore moins « pas d'effet ». Rien n'a été mesuré.

---

## 1. Phase A — provenance, contamination, gel

### 1.1 Provenance résolue, jamais devinée

| élément | valeur |
|---|---|
| parent EEFCA (abrégé fourni) | `de1524b` |
| **parent résolu** | `de1524b22ff917dff1da6553f778a4f8019ac273` |
| désambiguïsation | une seule référence (`git rev-parse --disambiguate`) |
| grand-parent ETPC | `3f8dae8bbe2937c43661ba8adfe8aed63bf6b6ee` |
| branche grand-parent | `dev/exact-twin-public-path-counterfactual-00` → même commit |
| bundle EEFCA vérifié | `c752d185b3e79594ebbff91e1553113a377b4c986cba4ae44d94788239406ae6` |
| bundle ETPC | `846e3c2ba5c2adb01b5beed3c83f8b0a2007f7fe4a6b5c2d027ba1a100499a5b` |
| archive ETPC | `1f9271f48dbad16be82ae83e18ef84aa4580db920a87d2411ea8a7e9cf456685` |

Le corrigendum EEFCA borné exigé est joint (`EEFCA_CORRIGENDUM.md`), traité point par point,
**avant** le premier démarrage moteur.

### 1.2 Registre de contamination

| blocs | géométrie | rôle | fichiers ouverts | point de mesure calculé |
|---|---|---|---|---|
| `61000–61009` | FAR | **`DEVELOPMENT_EXPOSED`** | tous, définitivement | disque ETPC, déjà connu |
| `61000–61003` | FAR | **`QUALIFICATION_ONLY`** (ce programme) | points de contrôle rejoués et commis | **aucun** |
| `62000–62009` | NEAR | **`HELD_OUT_UNSEEN`** | **aucun** | **aucun** |
| primaires nouveaux | — | **non alloués** | — | — |

**Pourquoi aucun identifiant primaire n'a été alloué.** Le protocole gèle les manifestes de blocs
« avant d'ouvrir un contraste cible ». Le programme s'est terminé **en qualification**, en amont
de ce gel. Allouer dix identifiants primaires pour les abandonner immédiatement les aurait brûlés
sans contrepartie. Ils restent disponibles, non alloués, non vus. La géométrie tenue à l'écart
`62000–62009` n'a été ni lue, ni listée pour son contenu, ni hachée.

### 1.3 Registre exact des démarrages moteur

| script | démarrages | ce qu'ils étaient |
|---|---|---|
| `etnbfc_b0.py` | 4 | fondateurs de développement 61000–61003, faisabilité d'appariement |
| `etnbfc_c0.py` | 4 | mêmes fondateurs, rejoués et **enregistrés durablement** |
| **total** | **8** | plafond qualification 24 ; plafond absolu 160 |

Relances, plantages, blocs abandonnés : **0**. Bras cibles avancés : **0**.

---

## 2. Phase B0 — sémantique canonique de `z` (établie, pas supposée)

### 2.1 `Mf[0]` est une **quantité**, pas une densité — et voici la preuve exécutable

Deux preuves indépendantes tirées du code, pas de l'apparence des unités :

1. **Construction.** `Mf = rho * newm` en fin d'écriture, avec `newm` intensif borné. `Mf[0]` est
   donc littéralement un produit densité × concentration, c'est-à-dire un contenu par cellule.
2. **Le transport est en forme divergence.** `mdon` = valeur donneuse de l'intensif `Mf/rho`,
   `gm = fl * mdon`, `dM += −(gm − roll(gm,1,axis))`. Une mise à jour télescopique conserve la
   **somme brute** du tableau. Elle ne conserverait **pas** une somme pondérée si les poids
   variaient. C'est cela qui fixe `w_i`, et non le fait que `w_i = 1` paraisse naturel.

### 2.2 Les poids d'intégration

Le stencil `lap(X) = roll+roll+roll+roll − 4X` ne porte **aucun** `dx` et aucune aire de cellule.
Le réseau 64×64 périodique a une mesure unitaire identique partout.

```
w_i = 1.0 exactement, pour toute cellule
Q   = somme exacte non pondérée de Mf[0]
```

Il n'existe **aucun** bit stocké ni source décrivant un volume de cellule variable, parce qu'une
telle grandeur n'existe pas dans le modèle. L'application d'un incrément d'état vers le contenu
physique est **l'identité** : pas de capacité, pas de poids de stockage intermédiaire.

### 2.3 Contraintes de domaine jointes — `|z| ≤ 1` n'est pas l'énoncé complet

| contrainte | énoncé exact | imposée par |
|---|---|---|
| **C1** | `\|Mf[0]_i\| ≤ ρ_i` | `np.clip(mk, −1, 1)` sur l'intensif, puis `Mf = rho*newm` |
| **C2** | `Mf[0]_i = 0` **exactement** si `ρ_i ≤ 1e-4` | `newm[kk] = clip(...) * alive` |
| **C3** | `Mf[1]` obéit aux mêmes bornes, **sans couplage à `Mf[0]`** | l'écriture met à jour chaque composante indépendamment ; `Psi` ne lit jamais `m` |
| **C4** | aucune variable d'occupation distincte de `ρ` | — |

La porte `alive` (C2) est une seconde condition jointe, exacte, **distincte** de C1 et de
`ρ > 0`. Un audit qui s'arrête à « `|z| ≤ 1` » la manque.

**Conséquence pour l'appariement.** Deux sites sont compatibles pour un échange de `Mf[0]` si et
seulement si leur `ρ` est **bit-identique** : même borne C1, même drapeau C2, admissibilité
garantie sans écrêtage. `ρ` est le seul champ non cible du domaine joint, et `w_i` est une
constante de compilation sans bits discriminants. Donc :

```
pair_key_i = bytes(rho_i)
```

*Déclaration d'ordonnancement, honnête :* cette dérivation a été écrite et exécutée **avant** la
mesure de la section 3, dans le même fichier, de haut en bas. Il n'y a pas eu de cérémonie de
scellement indépendante. Elle est de toute façon entièrement déterminée par le libellé du handoff
et par une lecture statique de l'exécutable ; aucun choix de clé n'aurait pu orienter le résultat.

---

## 3. Phase B1/B2 — **premier arrêt** : le support d'échange exact est vide

### 3.1 Inventaire exact de la représentation

Sur chacun des quatre points de départ de développement, grille de 4096 cellules :

| bloc | valeurs `ρ` **distinctes** sur toute la grille | valeurs répétées | cellules vivantes | `ρ` distincts parmi les vivantes | **paires A–B exactes** |
|---|---|---|---|---|---|
| 61000 | **4096 / 4096** | **0** | 1662 | 1662 | **0** |
| 61001 | **4096 / 4096** | **0** | 1663 | 1663 | **0** |
| 61002 | **4096 / 4096** | **0** | 1660 | 1660 | **0** |
| 61003 | **4096 / 4096** | **0** | 1664 | 1664 | **0** |

**Chaque cellule de la grille porte un motif binaire `float64` unique.** Pas une seule valeur
n'est répétée, nulle part — ni dans le bain, ni dans la matière, ni entre les deux composantes.

### 3.2 De combien s'en faut-il ?

Ce n'est pas un échec de peu :

| bloc | distance ULP minimale entre un site A et son plus proche site B | écart relatif minimal |
|---|---|---|
| 61000 | 4,6 × 10¹³ | 7,2 × 10⁻³ |
| 61001 | 1,2 × 10¹³ | 1,9 × 10⁻³ |
| 61002 | 1,6 × 10¹⁴ | 2,3 × 10⁻² |
| 61003 | 9,8 × 10¹³ | 1,3 × 10⁻² |

Les densités des deux composantes diffèrent dès la **troisième décimale**. Aucun raffinement de
comptabilité, aucun ordre de tri, aucune tolérance autorisée ne peut créer une paire.

### 3.3 Verdict

`O2_EXACT_MATCH_SUPPORT` ne trouve rien ; `O10_RECIPROCAL_NONTRIVIALITY` et `O11_FIXED_COVERAGE`
n'ont rien à couvrir. Le protocole l'a prévu explicitement :

```
STATE_OPERATOR    = CONSERVATIVE_SWAP_UNAVAILABLE
CAUSAL_FLUX_EFFECT = NOT_TESTED
SCIENTIFIC_RESULT  = NOT_TESTED
```

Aucun autre ordre, aucun appariement approché, aucune seconde tentative n'a été essayé —
le protocole l'interdit, et ce serait de toute façon vain à 10¹³ ULP.

### 3.4 Diagnostic : pourquoi c'était structurellement improbable

`ρ` est un champ continu d'EDP en flottant double. Deux régions évoluées indépendamment ne
partagent aucun bit. La condition d'appariement exact n'est donc pas une contrainte *forte* : dans
cette classe de modèle, elle est **presque sûrement insatisfaisable**, indépendamment des
histoires imposées, de la géométrie et de la graine.

**Ce qui aurait pu marcher, et reste non testé.** Si les deux composantes étaient fondées comme
images miroir *exactes* l'une de l'autre, et si le pas d'intégration était exactement
équivariant par cette réflexion en arithmétique flottante, alors `ρ` serait bit-identique par
paires miroir et le support d'échange serait complet. Cela demande une **nouvelle fondation** —
donc une nouvelle autorisation. Ce n'est **pas** testé ici, et l'équivariance flottante de
`_face_flux` (qui contient un `np.where(dc > 0, …)`) n'est **pas** démontrée.

### 3.5 Une variante plus faible existe — nommée, mesurée, **non utilisée**

Une transposition brute d'octets de `Mf[0]` entre deux sites **quelconques** de A et B conserve
exactement le multi-ensemble de `Mf[0]` (donc `Q`) et est exactement involutive : ces deux
propriétés ne demandent **pas** l'égalité des `ρ`. Ce qu'exige l'égalité des `ρ`, c'est
l'admissibilité de domaine garantie et le sens physique de « même quantité de matière, mémoire
différente ».

Mesuré, pour information : sous le seul test d'admissibilité `|Mf[0]_i| ≤ ρ_j` et
`|Mf[0]_j| ≤ ρ_i`, **58 à 61 %** de tous les couples `(i,j)` sont admissibles et un appariement
complet **21/21** existe dans les quatre blocs.

**Cette variante n'a pas été utilisée.** L'autorisation impose l'appariement exact et interdit
toute correspondance par tolérance. Elle est consignée comme diagnostic pour une éventuelle
autorisation future, pas comme un contournement.

---

## 4. Phase C0 — **second arrêt, indépendant** : le registre de flux natif n'existe pas à gain nul

Même si l'opérateur avait été disponible, le programme aurait buté sur un obstacle distinct.

### 4.1 Inventaire des chemins d'échange natifs

| espèce | terme | classe | débit/crédit apparié ? |
|---|---|---|---|
| `c` | `D_c · _face_transport(c, κ)` | transport | **oui si `g ≠ 0`**, non si `g = 0` |
| `c` | `+ s·ρ` | source unilatérale | non |
| `c` | `− δ·c` | puits unilatéral | non |
| `N` | `D_N · _face_transport(N, κ)` | transport | **oui si `g ≠ 0`**, non si `g = 0` |
| `N` | `+ F·(N₀ − N)` | relaxation vers réservoir | non |
| `N` | `N − g` (absorption de croissance) | puits de réaction, écrêté | non |

Le prédicat matière–bain est **natif** : `alive = ρ > 1e-4`, exactement celui que le noyau
utilise pour construire `z`. Les liens de frontière `{(i,j) : alive_i XOR alive_j}` sont donc
bien définis sans reconstruction.

### 4.2 Bras ON — le registre existe et est exact

Avec `g ≠ 0`, `_face_transport` matérialise `fl = κ_face · (X_j − X_i)` face par face et
l'applique en débit/crédit télescopique. Vérifié : le registre de faces reconstruit sa propre
divergence **bit pour bit** (`True`).

```
F1_UNIQUE_REALIZED_TRANSFER_EXISTS (bras ON) = PASS
```

### 4.3 Bras OFF — le registre **n'existe pas**

Avec `g == 0`, le noyau exécute `return lap(X)` : une somme fusionnée à cinq termes. **Aucune
quantité par face n'est calculée.** Et la forme par faces avec `κ ≡ 1` n'est **pas** bit-identique
au stencil fusionné :

```
cellules différant : 3307 / 4096
écart maximal      : 1,110e-15   (pur ordre de sommation)
```

Un registre pour le bras OFF devrait donc être **reconstruit** — ce que la Phase C0 interdit
explicitement (« ne jamais recalculer un gradient, un laplacien, un flux proposé ou une
différence finie à partir des champs stockés ») — ou bien il faudrait **changer l'exécutable**,
ce qu'interdisent `NEW_LAWSPEC = false` et `NEW_PHYSICS = false`.

```
F1_UNIQUE_REALIZED_TRANSFER_EXISTS (bras OFF) = FAIL
F10_GAIN_ZERO_LEDGER_IDENTITY                 = NOT_SATISFIABLE_AS_WRITTEN
REALIZED_BOUNDARY_FLUX_STATUS                 = DEFINED_IN_ON_ARMS_ONLY
```

### 4.4 Distinction à ne pas écraser

Le **contenu scientifique** de la porte à gain nul — « changer `z` ne change rien au transport
public quand la contribution adaptative est coupée » — reste établissable bit-exactement au niveau
de **l'état public**, et ETPC l'a d'ailleurs déjà établi dans dix blocs de développement
(`tau_off` exactement `0,0`, empreintes publiques OFF identiques). Ce qui n'est **pas**
établissable, c'est la version **au niveau du registre d'événements** exigée ici. Les deux ne
doivent pas être confondues.

---

## 5. Ce que ce programme a produit malgré l'arrêt

1. **Points de contrôle durables et commis** (`ETNBFC/checkpoints/`), hachés — le défaut du
   `tempfile.mkdtemp()` d'ETPC n'est pas répété.
2. **Reproductibilité bit-exacte inter-session prouvée** : les quatre points de départ rejoués
   ici produisent des hachages logiques **identiques** à ceux commis par ETPC.
3. **Le corrigendum EEFCA borné**, dont le retrait de mon propre argument d'« incommensurabilité »
   et son remplacement par un inventaire exact — qui **confirme** la conclusion par la bonne
   méthode (intersection frontière ∩ composantes = **0**, 4 blocs sur 4).
4. **Deux faits structurels exacts** sur cette classe de modèle, réutilisables :
   le champ `ρ` n'a **aucune** valeur répétée ; le chemin à gain nul est un stencil fusionné sans
   décomposition par faces.

### Force du dossier, avant / après

| | avant | après |
|---|---|---|
| mécanisme de transport constitutif établi | non | **non** (inchangé — rien n'a été mesuré) |
| conformité d'ETPC | déjà retirée par EEFCA | inchangée |
| revendication d'involution conservatrice d'EEFCA | trop forte | **bornée à l'algèbre agrégée** |
| argument d'incommensurabilité d'EEFCA | invalide | **retiré, conclusion re-prouvée exactement** |
| preuves brutes durables | absentes (ETPC) | **présentes et hachées** |
| faisabilité de l'opérateur autorisé | inconnue | **résolue : indisponible, avec la mesure** |

Le solde net est **légèrement positif** et entièrement méthodologique. Aucun gain scientifique sur
la question causale : elle n'a pas été abordée.

---

## 6. Ce que ce rapport ne prétend pas

Aucune conclusion sur l'existence ou l'absence d'un effet causal de `z` sur le transport public.
Aucun médiateur retardé, aucune réponse retardée, aucun appariement d'états publics entre
histoires différentes. Aucune question d'appartenance, d'individualité, de clôture, de persistance
sous renouvellement, d'autonomie, de métabolisme, d'organismalité, de reproduction, d'hérédité, de
vie, de conscience ou d'AGI n'est ouverte ici.

Le point de mesure autorisé — le flux réalisé natif de `c` et `N` — reste **`NOT_TESTED`**, jamais
calculé, jamais regardé. La géométrie tenue à l'écart reste **scellée et intacte**.

---

## 7. Arrêts terminaux déclenchés

```
CONSERVATIVE_SWAP_UNAVAILABLE            (Phase B2, mesuré sur 4 blocs de développement)
REALIZED_BOUNDARY_FLUX_NOT_DEFINED       (Phase C0, bras à gain natif nul)
```

Non déclenchés : `TARGET_OPENED_BEFORE_FREEZE`, `HELD_OUT_PEEK_BEFORE_PRIMARY_PASS`,
`PRIMARY_BLOCK_REPLACEMENT`, `QUALIFICATION_BUDGET_EXHAUSTED`, `BLOCK_ROLE_COLLISION`.

Conformément au protocole, **aucune** réparation n'est tentée sous cet identifiant : ni gain
modifié, ni opérateur matriciel, ni correspondance approchée des masses, ni nouveau point de
mesure, ni fenêtre allongée, ni remplacement de graine.

---

## 8. Artefacts

| fichier | rôle |
|---|---|
| `etnbfc_protocol.json` + `.sha256` | portée, interdits, empreintes de code |
| `etnbfc_b0.py` / `etnbfc_b0.json` | sémantique canonique + faisabilité d'appariement exact |
| `etnbfc_c0.py` / `etnbfc_c0.json` | inventaire exact de la représentation + chemins d'échange natifs |
| `etnbfc_boundary_mask_inventory.json` | inventaire exact du masque de frontière (corrigendum §2) |
| `etnbfc_weak_alternative.json` | variante par inégalité, mesurée et non utilisée |
| `checkpoints/dev_FAR_6100{0..3}.npz` + `.hash.json` | preuves brutes durables |
| `EEFCA_CORRIGENDUM.md` | corrigendum borné, six points |
| `REPORT_ETNBFC.md` | le présent rapport |
| `etnbfc_verify.py` / `.json` | vérificateur indépendant |
| `SHA256SUMS` | empreintes de tous les artefacts |
