# `DUAL_OWNER_MEMORY_COLLISION_00` — rapport

**2026-08-09** · parent `b6bc514126ffd559407065eb89c07b4e950958ce`
(branche `dev/route-e-p09-dose-yoked-closure`, bundle `_bundles/route-e-p09-dose-yoked-closure.bundle`,
SHA-256 `d3d4c35e744ef300e5005e1678b4581bcacdae59486ea230ea330dc1ad3962c7` — vérifié)
· `ROUTE_E_STATUS = CLOSED` · `ISING_LIFE_LAB_STATUS = CONTINUES`
· 1 protocole scellé (`ecbaa85e5bbd1fdcd071a8274c2cd0a983d11dca9c15bc7952720adaa563582f`)
· **360 trajectoires** sur un maximum de 384 · 29 fixtures mécaniques, 10 vérifications
· aucun artefact parent modifié · `LawSpec` importée, jamais éditée

> **Verdict scellé : `ENVIRONMENT_EXPLAINS`.**
>
> Deux composants matériels coexistant dans un même monde communicant portent bel et bien des
> états mémoire **distincts**, **écrits localement**, **effaçables sélectivement**, **échangeables
> par une permutation exactement conservative**, et **survivant à 75 % de renouvellement
> matériel**. Mais ce n'est **pas** cet état qui détermine leur réponse causale future.
> Quand on échange les deux mémoires en laissant tout le reste bit-identique, les réponses
> **ne s'échangent pas** (fraction de transfert **−0,276**, IC [−0,355 ; −0,164], 10/12 blocs).
> Quand on échange l'**environnement local** — les deux mêmes poignées externes `c` et `N`,
> par la **même** permutation — les réponses s'échangent **entièrement** (fraction de transfert
> **+1,614**, IC [1,256 ; 1,732], **12/12 blocs**, p = 0,00049).
>
> L'adressabilité est établie. La **propriété causale** ne l'est pas : dans cette `LawSpec`, ce
> qui individue causalement les deux composants est le champ externe qui les entoure, pas la
> mémoire qu'ils portent.

---

## 0. Phase 0 — éligibilité des preuves

Aucune observation antérieure sélectionnée en développement ne devient ici une confirmation.

| source | statut réel, vérifié dans le dépôt | contribution autorisée |
|---|---|---|
| `M_MINUS_ORDER_READER_00` (`6ae4a0e`) | **DÉVELOPPEMENT seulement.** Disposition gelée : `ORDER_READER_CANDIDATE — GO to human scientific review only`, **`NO-GO for automatic prospective execution`**. Sa propre frontière scientifique dit qu'il n'établit « ni la propriété locale, ni la mémoire individuelle, ni l'identité, ni la confirmation prospective », et que le verdict parent `NO_MEMORY_FIRST_STAGE — STOP THIS PREREGISTRATION CANDIDATE` reste inchangé. | **aucune.** Aucun de ses espaces de graines n'est réutilisé. |
| `DOWNSTREAM_ORDER_READER_01` (`5ae9886`) | **`CODE-ONLY INSTRUMENT QUALIFIED — NO SCIENTIFIC OUTCOME OR SEED OPENED`**, `GO FOR HUMAN SEAL REVIEW; STOP FOR EXECUTION`, `equivalence_margin = null`. Jamais exécuté. | **aucune.** |
| `INTERVENTIONAL_INDIVIDUALITY_00` (`44d91f0`) | `AUDIT_INVALID` et jamais exécuté : sa spec Phase 0 enregistre `implementation_authorized = false`, `engine_execution_authorized = false`, `scientific_or_prospective_authorized = false`. | **aucune.** |
| `EXP-SC-MULTI-CHANNEL-ORGANIZATIONAL-MEMORY-00` (`5841b9b`) | La seule ligne avec une **validation prospective** de mémoire causale **et** de renouvellement : `G1–G9`, `G13–G15` PASS sur un split prospectif tenu à l'écart, turnover `M ≈ 0,12 ≤ M_LOW`, effacement / transplantation / plafond de clones ; **`G10–G12` (dimensionnalité, individuation) ÉCHOUENT**. | **la `LawSpec` et l'horizon.** C'est le socle de ce programme. |

Une remarque du dossier `INTERVENTIONAL_INDIVIDUALITY_00` est **portée en avant comme rival
vivant**, pas comme obstacle : sa disposition acceptée `STOP_ARCHITECTURE` ferme le substrat
scaffold à un **nouveau port environnemental**, au motif que c'est un substrat à **copie
passive**. Ce programme n'ajoute aucun port — il n'utilise que les deux poignées externes `N` et
`c` déjà présentes — donc il n'est pas bloqué ; mais le motif devient l'hypothèse `H_MATERIAL`,
et le résultat ci-dessous lui donne largement raison.

---

## 1. Un fait structurel que la ligne parente n'avait pas enregistré

Le monde `sc_mcm` **n'est pas un monde à un corps**. Parti de la graine uniforme gelée, il se
fragmente en **22 à 34 composants détectés** et se relaxe vers ~16 gouttelettes quasi
dégénérées. À l'instant de lecture publié (`WARMUP` + histoire + `SETTLE` ≈ t = 2240) il y en a
**22 à 24**, dont les trois plus grosses font 22, 22 et 22 cellules.

Toutes les lectures publiées de la ligne `sc_iom` / `sc_mcm` sont prises avec `largest(st)` —
c'est-à-dire **la plus grosse d'une vingtaine d'objets physiquement distincts et quasi égaux**.
Ce n'est pas une erreur d'analyse de leur part : c'est un fait sur le substrat qui n'avait pas
été mesuré, et il rend la question « deux composants coexistants » non pas exotique mais
**générique**. Ce qui manquait n'était pas la coexistence, c'était l'**adressage**.

La fondation utilisée ici y répond : deux calottes gaussiennes de largeur `W_FOUND = 3,0` aux
deux sites gelés donnent **exactement deux composants** de t = 100 à t ≥ 1550, épinglés à leur
site à 0,2 cellule près, sur toutes les graines. Aucune physique n'est touchée : seul le
**support initial** de `rho` est restreint, et `U`, `V`, `C` sont multipliés par le même masque
pour que `Σ_c C == rho` reste exact (fixture 1).

---

## 2. Ce que le monde a de « communicant », mesuré et non affirmé

Trois canaux relient les deux composants, et un seul est fort :

| canal | portée | couplage mesuré à d = 32 |
|---|---|---|
| attractant `c` | longueur d'écrantage `√(D_c/δ) = 3,1` cellules | `exp(−32/3,1) ≈ 3·10⁻⁵` |
| nutriment `N` | longueur d'écrantage `√(D_N/F) = 4,5` cellules | `exp(−32/4,5) ≈ 8·10⁻⁴` |
| **`up_ref`** dans le signal d'écriture `Ψ` | **globale, instantanée, non atténuée** | exact |

La **collision** annoncée par le nom du programme a donc été mesurée directement : on pilote un
seul côté et on regarde ce qui atterrit dans la mémoire de l'autre.

| code piloté | `Δm₊` côté piloté | `Δm₊` côté non piloté | fuite |
|---|---|---|---|
| `N0` | +0,2269 | +0,0002 | **0,00077** |
| `NN` | +0,2269 | +0,0001 | **0,00042** |
| `cc` | −2,63 | ≈ 0 | — |

**Les mémoires ne se percutent pas.** À cette séparation, l'écriture est locale à 3 ou 4 ordres
de grandeur près. C'est une réponse quantitative à la question posée, et elle est positive.

*(Note incidente, et elle porte : `N0` et `NN` produisent le **même** `Δm₊` à 10⁻⁴ près. Doubler
la dose de nutriment ne change pas ce qui est stocké. La saturation de `Ψ` que le certificat
`sc_mcm` invoquait pour expliquer un stockage ~1-D est ici **mesurée directement** sur le canal
`N`. Le canal `c`, lui, est loin de saturer : `cc` déplace `m₊` de −2,63.)*

---

## 3. Phase C — la paire d'histoires, et pourquoi la paire d'ordre a été écartée

La première exécution complète en développement a utilisé la paire d'**ordre** gelée de `sc_mcm`
(`Nc` contre `cN`, c'est-à-dire `H1` contre `H2`). Elle a donné un « effet de propriété »
spectaculaire — rapport histoire/site **68×**, 12/12 blocs — et cet effet était **faux**.

| ce que la paire d'ordre séparait | valeur médiane |
|---|---|
| états mémoire `|Δm₊|` | **0,153** |
| états mémoire `|Δm₋|` | 0,149 |
| **taille des corps** `|Δtaille|` | **9 cellules sur 46** |
| attractant local `|Δc|` | 0,248 |

Le composant qui « possédait `H1` » était simplement **plus gros de 20 %**. L'échange
réciproque, qui permute des états presque identiques, ne pouvait rien tester : il déplaçait la
réponse de 0,5 sur 110, soit 0,5 %.

C'est exactement le rôle de la Phase C. Huit paires candidates gelées, sélection sur les 12 blocs
de développement seulement, sur un critère calculé **entièrement dans le dictionnaire scalaire
gelé de l'état au repos, avant toute sonde, toute réponse, toute intervention et tout critère
de jugement** :

    Q = (|Δm₊| + |Δm₋|) / (1 + |Δtaille| / taille moyenne)

| paire | `Q` | `|Δm₊|` | `|Δm₋|` | `|Δtaille|` / taille | `|Δc|` | `|ΔN|` |
|---|---|---|---|---|---|---|
| `Nc\|cN` | 0,253 | 0,153 | 0,149 | 9 / 46 | 0,248 | 0,187 |
| `NN\|cc` | 1,514 | 2,858 | 0,124 | 40 / 42 | 0,796 | 2,149 |
| `NN\|00` | 0,222 | 0,225 | 0,225 | 45,5 / 44 | 0,218 | 2,119 |
| **`cc\|00`** | **2,672** | **2,631** | 0,102 | **0,5 / 21** | 1,027 | 0,027 |
| `Nc\|00` | 0,151 | 0,138 | 0,138 | 30 / 36 | 0,765 | 0,916 |
| `N0\|0N` | **0,000** | 0,000 | 0,000 | 7,5 / 36 | 0,070 | 0,185 |
| `NN\|Nc` | 0,139 | 0,086 | 0,086 | 14 / 58 | 0,537 | 1,204 |
| `cN\|cc` | 1,662 | 2,616 | 0,116 | 20 / 31 | 0,502 | 1,128 |

`cc|00` gagne, et gagne pour la bonne raison : **séparation mémoire 2,63 avec un désaccord de
corps de 0,5 cellule sur 21**. Les deux corps sont appariés. Le confond résiduel déclaré est
l'attractant local, `|Δc| = 1,03` — et c'est précisément pour lui que le bras `CROSS_ENV`
existe.

---

## 4. Le plan

Un monde, deux sites gelés, un plan 2×2 complet **apparié à l'intérieur de chaque bloc
fondateur** :

|  | site A | site B |
|---|---|---|
| `DUAL_AB` | possède `cc` | possède `00` |
| `DUAL_BA` | possède `00` | possède `cc` |

Les deux bras ont, pas à pas, une **série de forçage global identique** (fixture 7) : seule
l'affectation spatiale change. `H_GLOBAL` est donc réfutée par construction si les deux bras
diffèrent.

Deux opérations géométriques, et rien d'autre :

- **effacement sélectif** : `Mf ← 0` sur un demi-plan ;
- **permutation réciproque** : `x → (L − x) mod L`. C'est une **involution**, une **permutation
  exacte des sites du réseau** (fixtures 3, 3b : multiset identique, `math.fsum` identique au bit
  près), elle échange les deux sites des **deux** géométries gelées, et elle laisse `rho`, `U`,
  `V`, `c`, `N`, `C` **bit-identiques** (fixture 4) — donc les corps ne bougent pas
  (vérification 7 : `max |Δtaille| = 0`).
- la **même** permutation appliquée à `c` et `N` au lieu de `Mf` : c'est `CROSS_ENV`,
  l'adjudicateur pré-enregistré de `H_ENVIRONMENT`.

Le lecteur en ligne est **aveugle à la provenance** : audit AST des sept fonctions en ligne,
aucune n'accède à `C` ni à `mem()` (fixture 9). La provenance ne sert qu'à l'auditeur, pour le
critère de renouvellement gelé.

Critère primaire scellé, la **FRACTION DE TRANSFERT** : la réponse post-échange projetée sur
l'axe qui joint la réponse du site quand il possède sa propre histoire et celle qu'il montre
quand il possède l'autre. 0 = l'échange n'a rien déplacé ; 1 = il a tout déplacé. Signée, jamais
tronquée. Unité indépendante : le **bloc fondateur**, jamais le composant, la cellule ou le pas
de temps.

---

## 5. Résultats — split prospectif tenu à l'écart, blocs 35000–35011

### 5.1 L'état, lui, se comporte exactement comme un état possédé

Médianes sur les 12 blocs prospectifs, à l'échéance :

| bras | `m₊` A | `m₊` B | taille A | taille B | `c` A | `c` B |
|---|---|---|---|---|---|---|
| `AB` (A possède `cc`) | **−0,857** | **+1,772** | 21 | 21 | 1,634 | 0,610 |
| `BA` (A possède `00`) | **+1,773** | **−0,858** | 21 | 21 | 0,609 | 1,633 |
| `AA` (les deux `cc`) | −0,857 | −0,859 | 21 | 21 | 1,636 | 1,635 |
| `AB` + **échange mémoire** | **+2,066** | **−0,733** | 21 | 21 | 1,634 | 0,610 |
| `AB` + **échange environnement** | −0,857 | +1,772 | 21 | 21 | **0,606** | **1,637** |

Tout ce que la mission demandait au niveau de l'état est là :

- **distincts** : écart `Δm₊ = 2,63`, corps appariés à 21 cellules contre 21 ;
- **adressables séparément** : fuite d'écriture 0,0004–0,0008 ;
- **effaçables sélectivement** : effacer A déplace A de 1,055 et B de **6,9 × 10⁻⁷** —
  **sélectivité 1,08 million**, 12/12 blocs, p = 0,00049 ;
- **échangeables par permutation conservative** : après l'échange, l'écart résiduel entre l'état
  de A et l'ancien état de B vaut **11,2 %**, et 4,7 % pour B. L'échange est fidèle à ~89–95 % ;
  `Σ Mf` inchangé à 1,1 × 10⁻¹⁴ près (ordre de sommation flottante seulement) ;
- **survivants au renouvellement** : à l'horizon parent gelé `T_TURN = 700`, `M` médian =
  **0,240**, maximum 0,290, **100 %** des lectures sous `M_LOW = 0,35` — soit **75 % de la
  matière remplacée**, et les deux composants toujours présents dans **120 lectures sur 120**.

### 5.2 Et pourtant la réponse causale ne suit pas la mémoire

| échange | fraction de transfert | IC 95 % | signe | p |
|---|---|---|---|---|
| **mémoire** (réflexion), à l'échéance | **−0,276** | [−0,355 ; −0,164] | 2 / 10 | 0,039 |
| **mémoire** (translation), à l'échéance | −0,277 | [−0,354 ; −0,162] | 2 / 10 | 0,039 |
| mémoire, après renouvellement | +0,017 | [−0,012 ; +1,568] | 8 / 4 | 0,39 |
| **environnement**, à l'échéance | **+1,614** | **[1,256 ; 1,732]** | **12 / 0** | **0,00049** |
| **environnement**, après renouvellement | **+0,465** | [0,096 ; 0,547] | 11 / 1 | 0,0063 |

L'échange de mémoire **a** un effet causal réel : son déplacement médian, 5,65, dépasse le
plancher mécanique du sham (`DUAL_AA` + même permutation) de **36×**, 12/12 blocs, p = 0,00049.
Il n'est pas nul. Mais il ne va **pas** vers la réponse de l'autre propriétaire — il s'en
éloigne. La variante par **translation pure** donne le même chiffre à 0,001 près : le
retournement du motif n'y est pour rien.

L'échange d'**environnement**, lui, transporte la réponse **au-delà** de l'autre propriétaire
(1,61 > 1). Il faut le dire précisément : cela établit la **suffisance** de l'environnement, pas
une décomposition exacte, parce que `CROSS_ENV` permute aussi `N` et perturbe donc plus que ne le
faisait la différence d'histoire elle-même. L'énoncé exact est : *l'échange d'environnement
transporte les réponses, et davantage ; l'échange de mémoire ne les transporte pas du tout.*

### 5.3 La propriété apparente ne survit pas au renouvellement

| échéance | `d_histoire` | `d_site` | rapport | IC 95 % | signe | p |
|---|---|---|---|---|---|---|
| à l'échéance | 16,62 | 2,79 | **5,55** | [3,56 ; 7,72] | 12 / 0 | **0,00049** |
| après renouvellement | 57,66 | 52,62 | **1,009** | [0,9996 ; 2,588] | 8 / 4 | 0,39 |

Après 700 pas, `d_site` a été multiplié par 19 : les deux composants ont divergé pour des
raisons qui n'ont rien à voir avec leur histoire, et le rapport tombe à 1. Ce n'est pas
« la mémoire s'efface » — `m₊` tient largement — c'est que la dérive du monde noie la
distinction dans la lecture *in situ*.

### 5.4 La double dissociation n'est établie qu'à moitié

| intervention | déplacement du site visé | déplacement de l'autre | sélectivité | signe | p |
|---|---|---|---|---|---|
| effacer **A** (mémoire forte) | 1,055 | **6,9 × 10⁻⁷** | **1 077 293×** | 12 / 0 | **0,00049** |
| effacer **B** (mémoire faible) | 4,196 | 1,684 | 2,88× | 9 / 3 | 0,146 |

Effacer le composant **fortement écrit** est d'une localité extraordinaire. Effacer le composant
**faiblement écrit** ne l'est pas : l'effet fuit vers l'autre site et le test apparié
n'atteint pas le seuil. `G4` **échoue** en tant que double dissociation, et c'est déclaré
comme tel, pas arrondi.

### 5.5 Deux géométries, deux splits : le motif se réplique

| | `G1` | `G2` (`M` médian) | `G3` échéance | `G3` renouv. | `G5` échéance |
|---|---|---|---|---|---|
| FAR développement (`cc\|00`) | 12/12 | 0,309 | ×10,7 p = 0,0005 | ×4,98 p = 0,0005 | **−0,279** p = 0,0063 |
| **FAR prospectif** | **12/12** | **0,240** | **×5,55 p = 0,0005** | ×1,009 p = 0,39 | **−0,276 p = 0,039** |
| **NEAR prospectif** (d = 16) | **12/12** | **0,259** | **×3,53 p = 0,0005** | ×1,27 p = 0,146 | **−0,481 p = 0,00049** |

Le signe du critère primaire est **négatif dans les trois exécutions**, et à la géométrie
rapprochée il est deux fois plus négatif (0/12 blocs positifs). Rien ne dépend d'un tirage.

---

## 6. Les portes

| porte | statut | ce qui la décide |
|---|---|---|
| `G0` éligibilité des preuves | **PASS** | documenté §0 ; aucune observation DEV antérieure promue |
| `G1` faisabilité duale | **PASS** | 12/12 blocs, 120/120 lectures avec les deux sites occupés, exactement 2 composants |
| `G2` renouvellement matériel | **PASS** | `M` médian 0,240, max 0,290, 100 % sous `M_LOW = 0,35` |
| `G3` propriété (histoire > position) | **PASS à l'échéance**, **ÉCHEC après renouvellement** | ×5,55 p = 0,0005 ; puis ×1,009 p = 0,39 |
| `G4` effacement sélectif | **ÉCHEC comme double dissociation** | A : 10⁶× p = 0,0005 ; B : 2,88× p = 0,146 |
| `G5` échange réciproque | **ÉCHEC** | transfert −0,276, IC entièrement du mauvais côté de 0 |
| `G6` irréductibilité scalaire | **NON INFORMATIVE** | `R²` en validation croisée négatif pour **les deux** dictionnaires (−0,338 confondants, −0,363 mémoire) : il n'y a rien à décoder, l'écart de réponse est quasi constant d'un bloc à l'autre. Non-décodabilité ≠ irréductibilité. |
| `G7` nullité du forçage global | **PASS** | fixture 7, série identique pas à pas |
| `G8` cécité à la provenance | **PASS** | fixture 9, audit AST de 7 fonctions |
| `G9` réplication prospective | **PASS** | développement et prospectif concordent sur **chaque** porte, aux deux géométries |

**Disposition scellée retenue : `ENVIRONMENT_EXPLAINS`** — « `CROSS_ENV` transporte les réponses
et `CROSS` ne les transporte pas ». C'est littéralement ce qui s'est produit.
`ADDRESSABLE_BUT_NOT_TRANSFERABLE` s'applique en second : les états sont distincts, locaux et
sélectivement effaçables, mais la réponse future ne voyage pas avec eux.

---

## 7. Ce que cela retire à la ligne parente

Le certificat `EXP-SC-MULTI-CHANNEL-ORGANIZATIONAL-MEMORY-00` établit une mémoire causale,
effaçable et transplantable. Ce programme ne le contredit pas — il en **délimite la portée**.

La lecture du certificat passe par une **transplantation dans un corps commun effacé** :
`read_signature(eng, B0, donor_mem)` écrit la mémoire du donneur dans `B0` et lit la signature
au repos. Cette construction **isole** la contribution de la mémoire en supprimant toute
différence de corps et d'environnement. C'est légitime, et c'est ce qui donne le contraste 70×.

Ce programme pose la question complémentaire, celle que la mission demandait : **entre deux corps
qui coexistent réellement**, la mémoire est-elle ce qui décide de la réponse ? Réponse mesurée :
non. Elle y contribue — 36× le plancher mécanique — mais l'environnement local la domine et
transporte à lui seul l'identité de la réponse.

Formulation autorisée, et pas davantage :

> Dans cette `LawSpec` et à ces deux séparations, deux composants coexistants portent des états
> mémoire écrits localement, sélectivement effaçables, et échangeables par une permutation
> exactement conservative qui survit à 75 % de renouvellement matériel. La réponse causale
> future de chaque composant **ne suit pas** cet état : elle suit le champ externe local. Aucune
> revendication d'individualité, d'identité, d'hérédité, de reproduction, d'organisation ou
> d'autonomie n'est autorisée par un quelconque résultat de ce programme.

---

## 8. Discipline respectée

- **360 trajectoires** sur 384. Les sondes 0, 1 et 2 et le balayage Phase C font évoluer des
  mondes mais ne produisent ni sonde, ni réponse, ni critère de jugement : ils sont comptés
  comme invocations moteur, suivant la convention de `P07`–`P09`.
- 12 blocs de développement (34000–34011), 12 blocs prospectifs (35000–35011), **disjoints**,
  jamais utilisés auparavant (vérification 5).
- L'unité indépendante est le **bloc fondateur**. Aucun composant, aucune cellule, aucun pas de
  temps n'a été mis en commun comme réplicat.
- Aucune analyse n'est conditionnée à la survie : **120 lectures sur 120** entrent dans chaque
  analyse (vérification 10).
- Avec 12 blocs appariés, le test exact ne peut **jamais** descendre sous `2/2¹² = 0,00049`.
  C'est le plancher, il est déclaré, et aucune valeur inférieure n'est publiée.
- Aucune `LawSpec`, aucun champ, aucun canal mémoire, aucun contrôleur, aucun seuil de détecteur
  ou de traqueur n'a été ajouté. Le détecteur gelé (`0,30`, 12 cellules) est intact.
- Une seule chose a été ajoutée après scellement : l'appel du bras `CROSS_ENV` — dont le bras et
  la règle d'interprétation **sont** dans le protocole scellé — par un fichier séparé
  (`domc_analyse_env.py`) qui **importe l'estimateur scellé sans le modifier**, plutôt que
  d'éditer un fichier scellé et d'en casser silencieusement l'empreinte.

## 9. Ce qui n'est pas fait, et ne le sera pas dans ce programme

Pas de reconstruction en matière fraîche : la mission la conditionnait à l'établissement de la
propriété causale locale, qui n'est pas établie. Pas de troisième géométrie, pas de distance
supplémentaire, pas de neuvième histoire, pas de nouveau lecteur, pas de révision de seuil, pas
de nouvelle `LawSpec`, pas de sauvetage par contrôleur, pas d'extension opportuniste d'horizon.
