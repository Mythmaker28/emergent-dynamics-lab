# `CORE_HALO_MISMATCH_RECOVERY_00` — rapport

**2026-08-09** · parent `1b4c80e03ef7637073edb581c7cbf6b346956860`
(branche `dev/dual-owner-memory-collision-00`, bundle `_bundles/dual-owner-memory-collision-00.bundle`,
SHA-256 **vérifié** `29505e987fa8e5b541dfc3d172417befd3739078008191a97e9c372c2b8b661a`)
· `NEW_LAWSPEC_AUTHORIZED = false` — `LawSpec` importée, jamais éditée
· 1 protocole scellé `b1e4b06587c07f00689e3c3b37428f45e430ea46e29496e5b74da86933c97f20`
· **256 nouvelles trajectoires** sur un maximum de 320 · 29/29 vérifications
· aucun artefact parent modifié

> **Verdict scellé : `HALO_OVERWRITES_CORE`**, avec deux qualifications obligatoires.
>
> Un halo imposé pendant 350 pas **détruit 91 % de l'écart de cœur**, et celui-ci **ne revient
> pas** après restauration exacte du halo (Δ = **+0,452** [+0,445 ; +0,463], p = 0,00049,
> répliqué à **+0,399** [+0,385 ; +0,422] sur la géométrie tenue à l'écart). La direction causale
> stable de ce substrat va **du halo vers le cœur**.
>
> **Qualification 1.** Le changement persistant porte sur le **marqueur de cœur seulement**. La
> réponse future après restauration n'est **pas** distinguable de l'appariée (p = 0,354 et 0,062
> en inférence de randomisation). La revendication maximale associée à `HALO_OVERWRITES_CORE` —
> « reprogramme la réponse ultérieure » — **n'est donc pas autorisée**.
>
> **Qualification 2.** Le cœur n'est pas inerte : une paire intacte **conserve 1,7 à 2,0 fois plus**
> d'écart de halo qu'un halo orphelin (0,127 contre 0,074, p = 0,00049), et couper l'écrivain
> existant `lam_minus` retire **+0,024** de cette maintenance (p = 0,00049, répliqué). C'est de
> l'**entretien**, pas de la **reconstruction** : après échange, le cœur intact ramène le halo
> **moins** loin vers son propre label que le cœur effacé (contraste primaire **−0,111**
> [−0,115 ; −0,108], p = 0,00049).
>
> `CORE_REBUILDS_HALO` est **réfuté**. `STRONG_PAPER_GATE = FAIL`.

---

## 1. Phase A — stabilisation de `DOMC`, sans moteur

Détail complet : `CORRIGENDUM_DOMC.md` et `chmr_phaseA.json`. Résumé des corrections :

- **Estimand renommé** `NORMALIZED_TRANSFER_CONTRAST` : `T = ⟨c−a, b−a⟩/‖b−a‖²` est un
  coefficient de projection **non borné**, pas une fraction.
  `MEMORY_CROSS = −0,276 [−0,355 ; −0,164]` = **anti-transfert significatif**, pas une absence
  d'effet. `ENVIRONMENT_CROSS = +1,614 [+1,256 ; +1,732]` = **transfert amplifié**, pas un
  transport un-pour-un.
- **Dénominateurs bruts publiés.** À `t0`, étendue 6×, aucun petit dénominateur. **Après
  renouvellement, 5 dénominateurs sur 24 tombent sous 1 % de la médiane** (étendue 28 700×) :
  tous les chiffres post-renouvellement de `G5` sont **retirés comme non interprétables**.
- **Contraste apparié direct** `T_ENV − T_MEM` = **+1,886 [+1,329 ; +1,980]**, 12/0, p = 0,00049.
- **Multiplicité (Holm, 11 tests)** : l'anti-transfert mémoire **ne survit pas** à FAR
  (p = 0,193) mais **survit** à NEAR (p = 0,0059, 0/12).
- **Contrôles chirurgicaux** : `AA_CROSS` déplace de **0,698** (ce n'est pas un no-op ; `DOMC`
  annonçait 0,155) mais sa **projection sur l'axe d'histoire est +0,0023** — c'est
  l'**orthogonalité**, pas la petitesse, qui sauve l'inférence. `NO_OP_PERMUTATION` et
  `SURGERY_ONLY` passent tous les tests bit-exacts.
- **Effacement en valeurs absolues** avec TOST : côté A **équivalent** (marge ±0,472, moyenne
  1,4·10⁻⁵) ; côté B **non équivalent** (moyenne 16,7, IC 90 % [5,7 ; 27,7] contre marge ±1,88).
  Le rapport `1,08 million ×` n'est plus le titre.
- **`H_GLOBAL` n'est pas réfutée par construction** : seul le forçage *tenté* l'était. Mesuré :
  différence de somme au niveau du monde = **0,132** du contraste intra-monde, **p = 0,0005** ;
  résidu d'antisymétrie **0,292**. `H_GLOBAL` est **bornée**, pas réfutée. Le registre des
  quantités **réalisées** est désormais enregistré à chaque intervention (vérification 12 :
  conservation à 4,5·10⁻¹³).
- **Reclassification** : `G3` ayant échoué après renouvellement, le balayage Phase C et les trois
  exécutions `cc|00` deviennent `EXPLORATORY_POST_GATE_FAILURE` pour `G4`–`G9` de la chaîne
  originelle.

Dispositions corrigées : `COMPONENT_OWNERSHIP_NOT_ESTABLISHED + ENVIRONMENT_DOMINATED_RESPONSE`,
`LOCAL_MARKER_SEPARABILITY = ESTABLISHED`, `MEMORY_FIELD_MANIPULABILITY = ESTABLISHED`,
`FUNCTIONAL_SELECTIVE_ADDRESSABILITY = RESTRICTED_ONE_SIDED`,
`EXCLUSIVE_ENVIRONMENTAL_MEDIATION = NOT_ESTABLISHED`,
`TURNOVER_PERSISTENCE = MARKER_ONLY_PENDING_LINEAGE_AUDIT`,
`CAUSAL_INDIVIDUATION = NOT_ESTABLISHED`, `STRONG_PAPER_GATE = FAIL`.

---

## 2. Phase L — audit de lignée et de rang

### 2.1 Ce que les artefacts bruts ne peuvent pas répondre

`results/sc_mcm` et `results/sc_iom` sont **vides** (0 octet) ; le dépôt ne contient que des
documents et du code pour cette ligne. Aucun état spatial, aucun point de contrôle. Interdiction
d'interpoler ou de reconstruire.

```
PARENT_COMPONENT_MEMORY_THROUGH_TURNOVER = NOT_IDENTIFIABLE
DOMC_A_B_LINEAGE_FROM_RAW                = NOT_IDENTIFIABLE
```

`DOMC` n'a stocké que **deux instants**. Deux instants ne sont pas une lignée : une scission
suivie d'une refusion, ou un échange de l'objet physique occupant un site, y sont invisibles.
`DOMC` n'utilisait pas `largest(st)` — son lecteur était le plus proche voisin d'un site gelé —
donc le défaut de statistique de rang de la ligne parente ne le touche pas directement ; mais sa
persistance au renouvellement reste **`MARKER_ONLY`** jusqu'à un suivi de lignée.

### 2.2 Ce que le programme établit prospectivement

Le monde gelé `sc_mcm`, suivi avec la connectivité gelée, cadence 25 pas, 2600 pas :

| graine | composants (min–max) | **changements de lignée de `largest(st)`** | scissions | fusions | disparitions | écart rang1/rang2 médian | égalités exactes |
|---|---|---|---|---|---|---|---|
| 32000 | 0–44 | **18** | 61 | 51 | 21 | 0,097 | 9 |
| 32001 | 0–44 | **27** | 53 | 61 | 14 | 0,056 | 17 |
| 32002 | 0–48 | **19** | 54 | 48 | 15 | 0,121 | 7 |

**`largest(st)` change d'objet physique 18 à 27 fois** en 2600 pas, avec 7 à 17 égalités exactes
de taille. C'est une statistique de rang, pas une identité. Toute lecture publiée de la ligne
`sc_iom`/`sc_mcm` prise avec `largest(st)` porte cette ambiguïté.

La lignée sur laquelle repose le présent programme est, elle, propre : sur **256 trajectoires**,
**zéro scission, zéro fusion, zéro disparition**, exactement deux composants, et **toutes les
lignées fondatrices continues de bout en bout** (vérifications 7 et 13). Les 7 « changements
d'argmax » enregistrés dans le split confirmatoire sont des échanges de rang entre les deux
composants de taille quasi égale, sans aucune rupture de lignée.

---

## 3. Le plan

Deux couches, mesurées séparément, jamais combinées en un score unique :

- **CŒUR** : le champ mémoire `Mf`. Vecteur marqueur gelé = `(m1, m2)` pondéré par la masse sur
  le composant sélectionné par le lecteur de site gelé.
- **HALO** : les deux poignées externes `c` et `N`. Vecteur gelé = `(⟨c⟩, ⟨N⟩)` sur le **support
  de halo** gelé, un disque de rayon 8 autour du site gelé.

Huit bras, maximum autorisé : `MATCHED_SHAM`, `HALO_CROSS`, `CORE_CROSS`, `DOUBLE_CROSS`,
`HALO_CROSS + CORE_ERASE`, `HALO_CROSS + WRITER_OFF`, `ORPHAN_HALO`, `HALO_PULSE_RESTORE`.

`WRITER_OFF` met `lam_minus` à **exactement 0** pendant la récupération. C'est l'ablation
zéro-contre-sham d'un terme **déjà présent** dans la `LawSpec` gelée —
`c += dt(D_c ∇²c + s·ρ(1 + lam_minus·m₋) − δc)` — et c'est **le seul endroit** où le cœur écrit
le halo. Rien n'est créé, rien n'est réglé.

```
WRITER_CAUSATION = IDENTIFIABLE
```

**Critère primaire scellé, `CORE_DEPENDENT_HALO_RECONSTRUCTION` :**
`CDHR_X(t) = [h_A − h_B]_X / [h_A − h_B]_apparié`. Vaut exactement **−1** juste après l'échange,
**+1** si le halo a été entièrement reconstruit vers le label que porte son cœur intact, **0** si
le label a disparu. Signé, continu, apparié dans le bloc, et il porte **les deux directions
miroir à la fois**. Les deux directions sont **aussi** testées séparément contre le bras à cœur
effacé.

---

## 4. Phase D — séparation des échelles de temps

Sur les 8 blocs de développement, **avant tout résultat de mésappariement** :

| t | résidu orphelin max | faisabilité lignée | |
|---|---|---|---|
| 250 | 0,1569 | oui | — |
| 300 | 0,1078 | oui | — |
| **350** | **0,0739** | **oui** | **PASSE** |
| 400 | 0,0507 | oui | passe |

```
T_RECOVERY = 350        TIMESCALE_SEPARATION = PASS
```

Choisi comme le **plus précoce** instant scellé passant les deux critères. Ni l'horizon ni le
critère de résidu n'ont été touchés après lecture des résultats.

---

## 5. Résultats — split confirmatoire (12 blocs, 37000–37011) et géométrie tenue à l'écart (12 blocs, 38000–38011)

### 5.1 Les quatre états de mésappariement sont obtenus (`G4` PASS)

| bras | écart de halo à t = 0 |
|---|---|
| `MATCHED_SHAM` | **+1,0598** |
| `HALO_CROSS` | **−1,0598** (inversion exacte, résidu médian 0,0) |
| `CORE_CROSS` | +1,0598 (halo intact, comme voulu) |
| `DOUBLE_CROSS` | −1,0598 |

L'écart de cœur est inversé par `CORE_CROSS` (12/12, p = 0,00049). Les quatre états
cœur × halo sont distincts et comparables immédiatement après intervention.

### 5.2 `G5` — le cœur intact ne reconstruit pas son halo. **ÉCHEC.**

`CDHR` à `T_RECOVERY = 350` (−1 = état croisé, +1 = reconstruit) :

| bras | FAR confirmatoire | NEAR tenu à l'écart |
|---|---|---|
| `MATCHED_SHAM` | +1,000 (référence) | +1,000 |
| **`HALO_CROSS`** | **−0,430** [−0,460 ; −0,414] | **−0,207** [−0,263 ; −0,167] |
| `HALO_CROSS + CORE_ERASE` | **−0,320** [−0,346 ; −0,305] | **−0,098** [−0,151 ; −0,068] |
| `HALO_CROSS + WRITER_OFF` | −0,454 [−0,486 ; −0,438] | −0,234 [−0,292 ; −0,192] |
| `ORPHAN_HALO` | +0,580 | +0,499 |
| `DOUBLE_CROSS` | −0,245 | −0,034 |
| `CORE_CROSS` | +1,216 | +1,212 |

**Contrastes primaires appariés :**

| contraste | FAR conf. | NEAR tenu à l'écart |
|---|---|---|
| intact − cœur effacé | **−0,111** [−0,115 ; −0,108] · p = 0,00049 · rand p = 0,00049 | **−0,106** [−0,115 ; −0,103] · p = 0,00049 |
| intact − écrivain coupé | **+0,024** [+0,024 ; +0,025] · p = 0,00049 | **+0,027** [+0,025 ; +0,029] · p = 0,00049 |

**Directions miroir** (il en faut deux, pas une) :

| direction | prédiction scellée | FAR conf. | NEAR |
|---|---|---|---|
| `dir_A` = h_A(croisé) − h_A(cœur effacé) | **> 0** | **−0,0057** ✗ | **−0,0049** ✗ |
| `dir_B` = h_B(croisé) − h_B(cœur effacé) | **< 0** | −0,0092 ✓ | −0,0073 ✓ |

Une seule direction a le bon signe, et le contraste primaire est **négatif** : le cœur intact
ramène le halo croisé **moins** loin vers son propre label qu'un cœur effacé. **`G5` échoue**,
aux deux géométries, avec le même signe et la même amplitude.

### 5.3 Mais le cœur **entretient** son halo (résultat positif, secondaire)

| grandeur | FAR conf. | NEAR |
|---|---|---|
| rétention appariée (paire intacte) | **0,1272** [0,1248 ; 0,1284] | **0,1307** [0,1255 ; 0,1343] |
| rétention orphelin (aucun cœur) | 0,0738 | 0,0652 |
| **excès de maintenance** | **+0,0534** · p = 0,00049 | **+0,0655** · p = 0,00049 |
| rapport | **1,72×** | **2,01×** |

La matière vivante conserve donc **près du double** d'écart de halo spécifique à l'histoire par
rapport à un halo orphelin — et couper l'écrivain existant en retire **+0,024**. C'est un effet
cœur → halo **réel, répliqué et significatif**, mais c'est de la **maintenance d'un état déjà en
place**, pas la **reconstruction d'un état déplacé**.

### 5.4 `G7` — le halo réécrit le cœur. **PASS (sur le cœur).**

Écart de cœur à `t = 700`, halo restauré à l'identique (résidu de restauration −0,055) :

| | FAR conf. | NEAR tenu à l'écart |
|---|---|---|
| apparié, jamais croisé | **−0,4987** [−0,511 ; −0,474] | **−0,4756** [−0,501 ; −0,436] |
| pulsé puis restauré | **−0,0423** [−0,052 ; −0,028] | **−0,0709** [−0,083 ; −0,050] |
| **différence** | **+0,4522** [+0,445 ; +0,463] · p = 0,00049 · rand p = 0,00049 | **+0,3987** [+0,385 ; +0,422] · p = 0,00049 |

**91 %** (FAR) et **85 %** (NEAR) de l'écart de cœur sont détruits par 350 pas de halo mésapparié,
et ils **ne reviennent pas** une fois le halo remis en place.

**Mais la réponse, elle, ne garde pas trace du passage :**

| réponse au défi à `t = 700`, moins l'appariée | médiane | p (signes) | p (randomisation) |
|---|---|---|---|
| `HALO_PULSE_RESTORE`, FAR conf. | +0,42 | 0,77 | **0,354** |
| `HALO_PULSE_RESTORE`, NEAR | −12,81 | 0,39 | **0,062** |

La réécriture est donc **réelle sur le marqueur** et **causalement inerte sur la réponse mesurée**.

### 5.5 `G8` — la réponse future suit le halo **courant**, pas le cœur

| bras, écart signé A−B moins l'apparié | FAR conf. | NEAR |
|---|---|---|
| `HALO_CROSS` | **−17,58** [−21,99 ; −1,30] p = 0,039 | **−9,01** [−18,31 ; −2,58] p = 0,0063 |
| `HALO_CROSS + CORE_ERASE` | −9,31 p = 0,039 | −8,91 p = 0,0063 |
| **`CORE_CROSS`** | **+0,012** [−0,53 ; +0,30] **p = 1,00** | +0,264 p = 0,039 |

Échanger les **cœurs** ne change **rien** à la réponse (p = 1,00 à FAR). Échanger le **halo** la
change fortement, et l'effacement du cœur ne supprime pas ce changement. C'est une réplication
propre, sur un plan mieux contrôlé, de ce que `DOMC` avait vu.

### 5.6 `G9` — renouvellement résolu par lignée. **PASS.**

| | `M` médian | `M` max | sous `M_LOW = 0,35` | lignées continues | lignées scindées |
|---|---|---|---|---|---|
| FAR développement | 0,183 | 0,231 | **100 %** | **toutes** | **0** |
| FAR confirmatoire | 0,187 | 0,227 | **100 %** | **toutes** | **0** |
| NEAR tenu à l'écart | 0,200 | 0,237 | **100 %** | **toutes** | **0** |

C'est exactement ce que `DOMC` ne pouvait pas établir : un renouvellement de **80 %** de la
matière **à l'intérieur d'une lignée continûment suivie**, sans scission ni fusion.

---

## 6. Tableau des portes

| porte | statut | ce qui la décide |
|---|---|---|
| `G0_PROTOCOL` | **PASS** | protocole scellé `b1e4b065…` avant toute sortie confirmatoire ; 9 fichiers de code hachés |
| `G1_LINEAGE` | **PASS** | 0 scission, 0 fusion, 0 disparition sur 256 trajectoires ; toutes les lignées continues |
| `G2_SURGERY` | **PASS** | multisets exactement préservés, champs hors cible bit-identiques, masse inchangée, `c` global réalisé conservé à 4,5·10⁻¹³ |
| `G3_TIMESCALE` | **PASS** | résidu orphelin 0,0739 ≤ 0,10 à `T_RECOVERY = 350`, faisabilité intacte |
| `G4_MISMATCH` | **PASS** | les quatre états cœur × halo distincts ; inversion exacte du halo, inversion du cœur 12/12 |
| **`G5_CORE_TO_HALO`** | **ÉCHEC** | contraste primaire **−0,111**, et `dir_A` a le mauvais signe. Une seule direction miroir. |
| `G6_NECESSITY` | **NON APPLICABLE** | la nécessité ne peut pas être testée pour une reconstruction inexistante. Mesure positive conservée : couper l'écrivain retire +0,024 de maintenance, p = 0,00049, répliqué |
| **`G7_HALO_TO_CORE`** | **PASS sur le cœur**, ÉCHEC sur la réponse | +0,452 et +0,399, p = 0,00049 ; réponse après restauration non distinguable (rand p = 0,354 / 0,062) |
| `G8_CAUSAL_RESPONSE` | **PASS pour le halo courant**, **ÉCHEC pour le cœur** | `CORE_CROSS` : p = 1,00 |
| `G9_TURNOVER` | **PASS** | `M` = 0,187 / 0,200, 100 % sous le seuil, lignées continues |
| `G10_HELD_OUT` | **PASS** | chaque résultat, signe et amplitude, se réplique à la géométrie tenue à l'écart, sans changer un lecteur, un seuil, un horizon ni une intervention |

---

## 7. Adjudication

```
DISPOSITION = HALO_OVERWRITES_CORE
              (critère du cœur atteint ; critère de la réponse NON atteint)

CORE_REBUILDS_HALO             = REFUTED   (G5 échoue, aux deux géométries)
PASSIVE_ENVIRONMENTAL_TRACE    = REFUTED   (le halo apparié retient 1,7-2,0x l'orphelin)
STATIC_ENVIRONMENTAL_CONTROL   = PARTIAL   (la réponse suit bien le halo courant, mais une
                                            réécriture persistante du cœur a lieu)
MUTUAL_CORE_HALO_ATTRACTOR     = REFUTED   (un seul effet dirigé passe)
TRANSIENT_MIXED                = REFUTED   (une disposition directionnelle stable passe :
                                            halo -> coeur, p = 0,00049, deux geometries)
WRITER_CAUSATION               = IDENTIFIABLE et mesuree : +0,024 de maintenance
STRONG_PAPER_GATE              = FAIL
```

### Revendication maximale autorisée

> Dans cette `LawSpec`, la couche externe locale gouverne la couche interne. Un état
> environnemental local transitoire, imposé par une permutation exactement conservative pendant
> 350 pas puis retiré, **détruit durablement 85 à 91 % du marqueur interne** d'une matière qui se
> renouvelle à 80 % à l'intérieur d'une lignée continûment suivie. La matière intacte
> **entretient** son hale spécifique à l'histoire — près du double d'un halo orphelin, et couper
> son écrivain existant en retire une part mesurable — mais elle ne le **reconstruit pas** après
> déplacement. La réponse future suit le champ externe **courant** ; échanger les états internes
> ne la modifie pas.

Ne sont **pas** autorisés : que la réponse ultérieure ait été reprogrammée (non établi,
rand p = 0,354 / 0,062) ; et toute revendication d'individualité, d'autonomie, d'organismalité,
de reproduction, d'hérédité ou de vie.

---

## 8. Positionnement dans la littérature

- **Mémoire matérielle.** Les mémoires matérielles rapportées dans les milieux amorphes, les
  suspensions cisaillées ou les mousses sont des états internes qui **survivent au retrait du
  forçage**. Ici le marqueur interne ne survit pas à un forçage *concurrent* : il est écrasé.
  L'objet mesuré est plus proche d'un **filtre passe-bas du champ local** que d'une mémoire.
- **Forçage localisé et vectoriel.** Le pilotage par demi-plan et la permutation par réflexion
  fournissent exactement l'ingrédient que ces travaux réclament : une adresse spatiale sans
  étiquette d'identité. Ils montrent que l'adressabilité géométrique n'implique pas la propriété
  causale.
- **Réponses non abéliennes.** L'ordre des entrées est ici stocké dans `m₋` mais, comme la Phase C
  de `DOMC` l'a montré, le canal d'ordre sépare les états de 0,15 quand le canal de dose les
  sépare de 2,6 : le substrat n'a pas la profondeur de stockage requise pour une réponse
  d'ordre robuste.
- **Bits matériels adressables indépendamment.** La séparabilité locale est établie ici
  (fuite d'écriture 4·10⁻⁴, effacement ciblé équivalent hors cible du côté fortement écrit) ;
  ce qui manque n'est pas l'adressage mais la **rétroaction du bit vers la fonction**.

---

## 9. Registre des revendications

| # | revendication | statut | appui |
|---|---|---|---|
| 1 | `largest(st)` change d'objet physique dans le monde gelé | **ÉTABLI** | 18–27 changements en 2600 pas, 3 graines |
| 2 | la lignée du programme est continue, sans scission ni fusion | **ÉTABLI** | 0/0/0 sur 256 trajectoires |
| 3 | le renouvellement matériel gelé est atteint dans une lignée continue | **ÉTABLI** | `M` = 0,187/0,200, 100 % |
| 4 | les quatre états cœur × halo sont obtenus | **ÉTABLI** | inversion exacte du halo |
| 5 | le cœur intact reconstruit son halo après échange | **RÉFUTÉ** | −0,111, `dir_A` mauvais signe |
| 6 | le cœur entretient son halo mieux qu'un halo orphelin | **ÉTABLI** | 1,72× et 2,01×, p = 0,00049 |
| 7 | l'écrivain existant `lam_minus` contribue à cette maintenance | **ÉTABLI** | +0,024, p = 0,00049 |
| 8 | un halo imposé réécrit durablement le marqueur de cœur | **ÉTABLI** | +0,452 / +0,399, p = 0,00049 |
| 9 | cette réécriture reprogramme la réponse ultérieure | **NON ÉTABLI** | rand p = 0,354 / 0,062 |
| 10 | la réponse future suit le halo courant | **ÉTABLI** | −17,6 / −9,0 |
| 11 | échanger les cœurs change la réponse | **RÉFUTÉ** | +0,012, p = 1,00 |
| 12 | la mémoire parente survit au renouvellement dans une lignée | **NON IDENTIFIABLE** | aucun état brut parent n'existe |

---

## 10. Discipline

- **256 nouvelles trajectoires** sur 320. 8 blocs DEV (36000–36007), 12 confirmatoires
  (37000–37011), 12 tenus à l'écart (38000–38011), **tous disjoints** et jamais utilisés
  auparavant (vérifications 4 et 5).
- L'unité indépendante est le **bloc fondateur**. Les composants et les instants sont des
  observations appariées répétées, jamais des réplicats.
- **Inférence de randomisation au niveau du bloc** en plus des tests exacts appariés ; TOST pour
  les effets hors cible ; plancher exact déclaré (`2/2¹² = 0,00049`).
- **Aucun conditionnement** sur le suivi, la survie ou la chirurgie : les 8 bras existent dans
  chacun des 32 blocs (vérification 6).
- Aucune nouvelle `LawSpec`, aucun canal de sortie privé, aucune troisième géométrie, aucune
  nouvelle paire d'histoires, aucun nouveau lecteur, aucune révision de seuil, aucun horizon
  opportuniste.
- Une seule chose ajoutée après scellement : le contraste de réponse du bras `HALO_PULSE_RESTORE`,
  dont le bras et la porte `G7` **sont** dans le protocole scellé, calculé par un fichier séparé
  qui **importe les estimateurs scellés sans les modifier** plutôt que d'éditer un fichier scellé.

---

## 11. Ce que cela ferme

`CORE_REBUILDS_HALO` est réfuté et `PASSIVE_ENVIRONMENTAL_TRACE` aussi ; la disposition retenue
est `HALO_OVERWRITES_CORE`, sans transfert de réponse. Le substrat `sc_mcm` a donc une couche
interne **manipulable, adressable, effaçable et permutable**, mais **subordonnée** : elle est
écrite par le champ local, elle ne le reconstruit pas, et elle ne commande pas la réponse.

Conformément aux règles d'arrêt : pas de nouvelle `LawSpec`, pas de canal de réponse privé, pas
de troisième géométrie, pas de nouvelle paire d'histoires, pas de nouveau lecteur, pas de
révision de seuil ou de marge, pas de temps de récupération opportuniste, pas de sauvetage par
contrôleur, pas de définition de halo supplémentaire, aucune expérience de reconstruction, de
reproduction ou d'hérédité.
