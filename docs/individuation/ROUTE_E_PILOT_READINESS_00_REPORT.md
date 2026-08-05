# ROUTE_E_PILOT_READINESS_AND_FEASIBILITY_00 — rapport

> **Ce record ne prononce aucune acceptation humaine, ne calcule aucun `k`, n'évalue jamais les
> seuils 42/9 et ne conclut ni POSITIF ni NÉGATIF sur Route E.**
>
> `a1_r5_confirmatory_disposition = STOP` (inchangé) · `pilot_executed = true` ·
> `pilot_disposition = PILOT_DESIGN_RISK_OBSERVED` · `confirmatory_run_authorized = false`

---

## 1. Base récupérée et vérifiée (Phase 0)

Les trois valeurs annoncées ont été retrouvées **dans un dépôt Git réel**, pas déduites d'un
correctif. La chaîne complète a été reconstruite dans un clone propre : `git clone` depuis
`origin`, `git fetch` du commit `199f29eb`, puis dépaquetage successif des trois bundles.

| Élément | Attendu | Observé | |
|---|---|---|---|
| commit A1-R5 | `eccd46bc2a64e9348f6a41cf6d488d28c3736e81` | identique | ✔ |
| parent | `2cb7a48f05016ffd764c4d11ba7c27eaaff97225` | identique | ✔ |
| arbre | `886572a1835321579b00bab2698fca50ac7c5356` | identique | ✔ |
| `route-e-a1r5.bundle` | 12 938 o · `1abd029a…3e3308` | identique | ✔ |
| `route-e-a1r5.patch` | 43 539 o · `3b53b9f3…abf1cc4` | identique | ✔ |
| `git patch-id --stable` | `32871460dbe539d665ae8c4e6881c2a695c49fe2` | identique | ✔ |

Lignée complète vérifiée : `199f29eb` → `e5049d06` (A1-R3) → `2cb7a48f` (A1-R4) → `eccd46bc`
(A1-R5). Les trois fichiers épinglés par le record A1-R5 (`route_e_aggregate.py` 4 700 o,
`route_e_strict.py` 9 420 o, `future_route_e_world_evidence.py` 20 602 o) correspondent
octet pour octet à leurs SHA-256 déclarés. Les trois fichiers épinglés par le record
`EXECUTION_BOUNDARY_CORRECTION` diffèrent au commit A1-R5 — c'est attendu, R3/R4/R5 les ont
modifiés — et ils correspondent **à leur propre commit de scellement** `199f29eb`, ce qui a
été vérifié séparément.

**Aucun record R3, R4 ou R5 n'a été amendé.** Cet incrément est un successeur append-only sur
la branche `pilot/route-e-pilot-readiness-00`, créée depuis exactement `eccd46bc`.

---

## 2. Décision propriétaire RNG appliquée

`rng_mapping_owner_decision = SELECT_OPTION_1_TOP_53_BITS`, implémentée et versionnée :

```text
u = (word >> 11) * 2**-53
output_mapping         = U53_TOP_BITS_V1
source_word            = uniforme sur les 2^64 mots de block[0:8], big-endian
output_support         = {j / 2^53 : 0 <= j < 2^53}
output_distribution    = uniforme exacte sur cette grille
output_range           = [0,1)
low_11_bits_affect_output = false
supersedes             = U64_DIVIDE_V0_SUPERSEDED
```

L'ancienne application reste appelable sous le nom explicite
`draw_uniform_superseded_v0` : aucun artefact ancien ne peut être réinterprété en silence,
et un manifeste qui nomme une autre version est refusé (`PILOT_MAPPING_VERSION`).

La contradiction `U[0,1]` (texte 01S gelé) contre `[0,1)` (docstring) est corrigée **vers
l'avant** : la loi idéale continue est `U[0,1]`, sa réalisation numérique est une grille
dyadique finie de pas `2**-53`, strictement dans `[0,1)`, et aucune égalité littérale avec la
mesure de Lebesgue n'est revendiquée.

### 2.1 Correction factuelle du dossier A1-R5

Le dossier RNG d'A1-R5 écrit : *« Cost: every drawn value changes »*. **C'est faux, et c'est
mesuré ici plutôt que réaffirmé.** Sur 4 000 tirages réels, environ deux tiers des valeurs
changent, et l'écart maximal observé est d'**un unité au dernier rang** (≤ 2⁻⁵²). Le gain réel
n'est pas l'amplitude mais la **forme** : l'ancienne application arrondissait sur une grille
irrégulière (plus fine près de 0), donc ses sorties n'avaient pas toutes le même nombre
d'antécédents ; `U53_TOP_BITS_V1` est exactement uniforme sur une grille régulière. Le test
`test_rng_03` porte cette mesure.

### 2.2 Assertions historiques modifiées, listées

Quatre assertions épinglaient l'ancienne application. Elles sont corrigées, jamais supprimées,
et chaque site porte un commentaire nommant la valeur remplacée :

| Fichier | Test | Ancienne valeur | Nouvelle |
|---|---|---|---|
| `test_future_route_e_a1r4_verifiable_closure.py` | `test_m04` | `word / float(2**64)` | `(word >> 11) * 2**-53` |
| `test_future_route_e_a1r4_verifiable_closure.py` | `test_m05` | `IC_RESOLUTION_BITS == 64` | `== 53` |
| `test_future_route_e_pre_run_blocker_closure_00.py` | `test_prb_b_02` | `/ 2.0**64` | `(word >> 11) * 2**-53` |
| `test_future_route_e_pre_run_locks_00.py` | `test_hr6_05` | `cap/2**64 ≈ 6,0e-19`, `(hi-lo)/2**64 ≈ 3,3e-21` | `cap/2**53 = 1,2312767348986591e-15`, `(hi-lo)/2**53 = 6,830473686658678e-18` |

Les deux tests A1-R5 qui **démontraient** le défaut (`test_r5_the_top_of_the_range…`,
`test_r5_the_output_grid_is_not_2_pow_minus_64_near_one`) restent verts et inchangés : ce sont
des énoncés arithmétiques vrais sur l'ancienne application, et ils gardent leur valeur
historique.

---

## 3. Les six portes

Toutes les portes sont exercées par comportement dans
`tests/test_route_e_pilot_readiness_00.py` (**48 tests**). Aucun `assert <drapeau>`, aucune
recherche de chaîne tenant lieu de comportement, aucun agrégateur local, aucun appel direct au
scoreur interne là où le parcours public est exigé, aucun `skip`, aucun `xfail`.

### G1 — parcours publics synthétiques réels · **PASS**

Un constructeur public, `build_synthetic_transport_world`, produit un monde
**cohérent en transport** par un **échange pur** : `forward == reverse` partout, donc le flux
net de matière est identiquement nul — le composant reste détecté tout l'horizon par
construction — tandis que les flux **bruts** sont non nuls, si bien que la cohorte se mélange
réellement avec la matière non étiquetée.

* `Y = 1` vrai : résidu **exactement 1** à l'enrôlement (vérifié sur les octets), chute par
  transport, `gross_in_unlabelled > 0`, dérive de conservation nulle, `Y = 1` à `f = 0,20`.
* `Y = 0` vrai : `exchange = 0`, résidu **exactement 1,0** à l'horizon, disposition
  `OBSERVED_FAILURE_HORIZON_WITHOUT_REPLACEMENT` — un échec **observé**, pas un incident.
* Le **même** monde sépare les trois conventions : `{0,01 : 0 · 0,05 : 0 · 0,2 : 1}`.
* Fixture pré-dépletée ⇒ refus `ENROLMENT_NOT_FULLY_LABELLED`.
* Trame rescellée ⇒ refus `FRAME_LEDGER_DISAGREEMENT`.
* L'entrée destinée aux données moteur refuse la fixture synthétique (`FIXTURE_CLASS_REFUSED`).

**Pourquoi la fixture `Y = 1` n'est pas un monde moteur, et ne doit pas l'être.** Savoir si le
moteur canonique peut produire un composant qui persiste tout en étant matériellement remplacé
est *la question scientifique du pilote*. Fabriquer la fixture en cherchant un `Y = 1` dans
l'espace des lois, puis la présenter comme une porte, répondrait à cette question par un
exemple choisi — exactement l'erreur que ce programme ne cesse d'enregistrer. La fixture est
donc construite par transport, déclarée `SYNTHETIC_NON_SCIENTIFIC`, refusée par l'entrée
moteur et refusée par la preuve de provenance.

### G2 — transport transitionnel vérifié · **PASS**

Le pont de mesure qualifié ne persiste **que les trames échantillonnées** : entre deux d'entre
elles, seize pas moteur dont les flux bruts n'existent qu'en mémoire. **La recomputation
exigée par G2 est donc impossible depuis la sortie du pont** — c'est un fait sur la conception
de la persistance, pas un défaut du pont, à qui l'on n'a jamais demandé de registre de
transport. Les deux issues honnêtes étaient `BLOCKED_PILOT_GATE_MISSING_TRANSPORT_LEDGER` ou
persister la preuve manquante. Ce pilote persiste la preuve manquante.

`transport_ledger/` contient, par monde, quatre fichiers float64 contigus : `matter.f64`
(1 025 trames), `tracer.f64` (1 025), `forward.f64` et `reverse.f64` (1 024 chacune, flux
**mis à l'échelle**, exactement les tableaux consommés par le transport). `matter_scale` n'est
pas persisté séparément, et ce n'est pas un raccourci : l'admission vérifie
`post = pre − dt·div(forward − reverse)` contre la matière persistée, identité qu'une échelle
forgée ne peut pas satisfaire.

Pour chacune des 1 024 transitions de chacun des 48 mondes, l'admission recalcule et vérifie :
flux non négatifs, matière non négative, cohérence matière/flux, `0 ≤ traceur ≤ matière`,
finitude, conservation globale, et **égalité avec le traceur persisté**. Résultat mesuré :
`transport_max_tracer_deviation = 0` et `global_tracer_conservation_max_drift = 0` sur les
48 mondes.

La recomputation est un **second énoncé indépendant** de la même arithmétique, pas un appel à
l'assistant du producteur ; `test_g2_07` exige que les deux coïncident bit à bit.

### G3 — jointure, piste, horizon · **PASS**

* **Naissance tardive** : un composant né après l'enrôlement, dont le résidu est
  **exactement 0,0**, est détecté, et il ne score pas — la règle A1-R4 le refuse. Le composant
  enrôlé, lui, garde 1,0. Sans la règle, ce monde aurait scoré `Y = 1` aux trois conventions.
* Trame manquante, horizon tronqué, masque incohérent ⇒ `TECHNICAL_INVALID`, jamais `Y = 0`.
* Couverture composant–piste exacte vérifiée sur un monde moteur réel.
* Le masque est désormais **re-dérivé** de la matière persistée (voir §5).

### G4 — parcours moteur véritable · **PASS**

`verify_engine_provenance` **prend des pas moteur, et le dit dans son nom**. Elle réexécute le
moteur canonique depuis la loi et la condition initiale persistées et exige l'identité **octet
pour octet** des flux, de la matière, du masque échantillonné et de la cohorte transportée, à
chaque transition. Un monde manuscrit échoue ; une perturbation de `1e-15` échoue ;
**48/48 mondes du pilote réussissent**.

Et le contrôle différentiel décisif : les trames échantillonnées produites par l'acquisition
pilote sont **byte-identiques** à celles de `run_measurement_bridge` pour la même loi, la même
condition initiale et le même calendrier, aux trois tailles de réseau. Le pilote mesure donc
le même objet que mesurerait le confirmatoire.

### G5 — séparation des incidents · **PASS**

Crash, preuve absente, registre absent, flux incohérent, cohorte qui fuit, jointure rompue,
trame manquante, horizon tronqué : tous donnent `Y = None` aux trois conventions, disposition
`TECHNICALLY_UNKNOWN`, unité explicitement invalidée, jamais `Y = 0`. Un producteur qui écrit
une réponse est refusé (`RUNNER_WROTE_AN_ANSWER`). Le parcours de crash de l'outil est couvert
de bout en bout par `test_g5_04`, qui exécute réellement `tools/run_route_e_pilot_00.py`.

**Incidents observés sur le pilote : 0 sur 48.**

### G6 — isolement irréversible · **PASS**

```text
namespace prefix                    = PILOT-      (imposé au manifeste, à l'acquisition et à l'admission)
contributes_to_k                    = false       (champ mécanique sur chaque verdict, aucun chemin ne le met à vrai)
confirmatory_aggregator_callable    = false       (l'agrégateur de PRODUCTION refuse 24 unités : PRIMARY_UNIT_COUNT_WRONG)
thresholds 42/9 evaluated           = false       (aucune de ces constantes n'existe sur le chemin pilote)
confirmatory seed reserve consumed  = false       (domaines de graine disjoints)
A2 / public beacon required         = false       (aucune signature du chemin pilote n'accepte beacon, round ou randomness)
```

---

## 4. Revue indépendante — FAIL, puis une passe corrective

Un relecteur indépendant, en lecture seule et borné aux six portes, a rendu **FAIL sur G1**,
avec G2, G3 et G5 également en échec, et **quatre contre-exemples exécutables**. Ils sont
listés ici sans adoucissement, parce qu'ils étaient tous réels.

| # | Défaut | Gravité |
|---|---|---|
| CE-1 | En ne réécrivant que les trames **`mask`** — jamais re-dérivées — il a fabriqué un `Y = 1` aux trois conventions dans un monde dont les flux étaient **identiquement nuls**. Toutes les vérifications G2 passaient à une déviation de 0,0 pendant que le résidu était lu sur un composant imaginaire. | **faux `Y`** |
| CE-2 | La tolérance d'égalité était **une** borne absolue tirée du maximum de matière sur tout le registre. Une seule cellule lointaine à `1e11` l'élargissait jusqu'à laisser passer une cohorte effacée : déviation rapportée 0,9, monde `ADMITTED`, `Y = 1`. | **faux `Y`** |
| CE-3 | Une trame `mask` blanchie transformait un défaut de preuve en **résultat scientifique négatif** (`DISSOLVED_DETECTED_TRACK`, `Y = 0`) au lieu d'un incident. | **incident converti en résultat** |
| CE-4 | `--horizon` / `--cadence` étaient des options libres non liées au manifeste : même loi, même graine, `Y = 0` à l'horizon 64 et `Y = 1` à 4 096. La revendication « rien qu'un opérateur puisse varier sans changer le hash du manifeste » était donc fausse. | **contamination du no-reroll** |

Il a également relevé trois faiblesses de tests : `test_rng_02` tautologique (n'appelait aucune
fonction de production), `test_g6_06` reposant sur une recherche de chaîne, et `test_g3_04`
exerçant la couverture de jointure sur un chemin que l'admission pilote n'emprunte pas.

### La passe corrective, unique

**Cause racine unique**, telle que le relecteur l'a nommée : le `mask` était le seul canal
persisté jamais re-dérivé de la preuve qu'il est censé résumer, alors qu'il décide seul quels
composants existent et sur quelles cellules le résidu est lu.

1. **Le masque est re-dérivé** de `matter >= matter_threshold` depuis le registre et exigé
   identique (`MASK_NOT_DERIVED_FROM_MATTER`). Ferme CE-1 **et** CE-3.
2. **Le critère d'égalité devient élément par élément et relatif** — le critère float64 déjà
   gelé par `AGENTS.md`, `abs(erreur) ≤ 1e-12 + 1e-10·abs(référence)` — donc aucune cellule
   lointaine ne peut élargir la borne appliquée à une autre. Ferme CE-2.
3. **Le calendrier est lié au manifeste committé** : les options `--horizon` / `--cadence` sont
   supprimées de l'outil, et une admission scientifique refuse un registre déclarant un autre
   calendrier (`SCHEDULE_NOT_THE_COMMITTED_ONE`). Ferme CE-4.
4. La provenance moteur couvre désormais aussi le masque.
5. `contributes_to_k` devient un champ mécanique porté par chaque verdict.
6. Les trois faiblesses de tests sont corrigées : `test_rng_02` interroge la vraie fonction,
   `test_g6_06` inspecte les vraies signatures, et l'outil est couvert de bout en bout.

Les quatre contre-exemples sont désormais des **tests de régression armés**
(`test_ce1…test_ce4b`). Portes touchées re-vérifiées : **48 tests, tous verts.**

---

## 5. Le pilote

### 5.1 Pré-sortie, gelée avant le premier monde

```text
manifeste committé  → P_pilot = c48339216548ba758820857e23c3e6e40f90319b2b09de358058ffc32f887f87
graine              = SHA-256(domaine ‖ ROUTE_E_PILOT_FEASIBILITY_00 ‖ P_pilot)
seed_root_sha256    = bd61848219fe84129849ce9948d7750ca8bd79764d5f834d25fea666cb7f73cb
inventaire          = 48 mondes écrits AVANT le premier pas moteur
calendrier          = 65 trames, cadence 16, horizon 1024  (dérivé du manifeste seul)
aucun beacon, aucun remplacement, aucun retry, aucun top-up, aucune seconde graine
```

**Le no-reroll est démontré, pas seulement déclaré.** Le pilote a été exécuté deux fois — une
fois avant la passe corrective, une fois après — et les deux exécutions ont produit des
registres de transport **byte-identiques pour les 48 mondes** (`ledger_sha256` identiques,
même `P_pilot`, mêmes admissions, mêmes `Y`). Une seconde exécution n'est pas un second tirage :
c'est le même tirage.

### 5.2 Ce que le pilote a mesuré

```text
mondes attendus / exécutés          48 / 48
incidents techniques                0
provenance moteur vérifiée          48 / 48   (octet pour octet, 1024 transitions chacune)
transitions recalculées par monde   1024      déviation traceur 0 · dérive de conservation 0
horloge murale                      299,4 s
```

**Résultat primaire, à la spécification gelée (seuil 0,45 · min_cells 3) :**

```text
mondes mécaniquement inéligibles                     48 / 48
mondes avec au moins une piste éligible               0 / 48
cause, dans les 48 cas                                WRAPPING_COMPONENT_PRESENT
```

Le garde-fou d'attrition du plan 01S déclenche `INDETERMINATE — MECHANICAL_INELIGIBILITY`
au-delà de 0,50. **La fraction observée est 1,00.** Sur les 24 mondes CI1 pris comme
échantillon descriptif, l'intervalle de Clopper-Pearson à 95 % est **[0,858 ; 1,000]**. Le
pilote n'attache aucune règle de décision à ce chiffre et 24 tirages ne le déterminent pas à la
précision du confirmatoire ; il est descriptif, et il est éloquent.

**Le composant percolant est produit par la dynamique, pas par la loi de condition initiale.**

```text
mondes enroulant le tore dès la trame d'enrôlement      6 / 48
mondes enroulant le tore quelque part dans l'horizon   48 / 48
première trame d'enroulement : min 0 · médiane 16 · max 48
```

Sur 42 des 48 mondes, le réseau n'est pas percolant au départ et le devient sous l'action du
moteur, en médiane dès la **première** trame échantillonnée. Changer la loi de condition
initiale ne réglerait donc pas le problème.

**Concordance CI1/CI2 : 24 paires sur 24** ont la même éligibilité et le même statut
d'enroulement. La dépendance à la condition initiale n'est pas ce qui décide ici.

**Fraction de matière étiquetée à l'enrôlement : moyenne 0,745** (min 0,671 · max 0,811).
Matière totale et cohorte totale sont toutes deux exactement conservées, donc ce rapport est
**figé pour toute la durée du run** ; sous mélange complet, tout résidu local tend vers lui. Les
trois conventions gelées — 0,01 · 0,05 · 0,20 — sont toutes très en dessous.

### 5.3 Le test d'inventaire, et ce qu'il tranche

Pour chaque piste éligible on rapporte `q`, `q_min_inventory = max(0, 1 − U/C)` et leur écart.

**`q_min_inventory = 0,0` partout.** Le seuil n'est donc **pas** rendu inaccessible par la
conservation : la réserve non étiquetée `U` est toujours largement supérieure à la masse `C` du
composant. La cause n'est pas une impossibilité d'inventaire ; c'est le **mélange homogène
tendant vers la fraction globale**, exactement la deuxième des trois branches que le protocole
demandait de distinguer.

### 5.4 Traceur d'union contre traceur focal — le résultat le plus important

Le traceur primaire marque **l'union** de tous les composants enrôlés. Il mesure donc le
remplacement par de la matière initialement extérieure à toute cette union, et non la
disparition de la matière propre au composant focal. Le diagnostic focal a été calculé sur les
**mêmes flux persistés** (le transport est linéaire en la cohorte : aucun pas moteur, aucun
second tirage).

À seuil 0,60, la seule configuration de la matrice où des mondes sont éligibles, pour les
9 mêmes pistes :

| | résidus observés |
|---|---|
| `q` **union** | 0,744 · 0,787 · 0,813 · 0,817 · 0,821 · 0,863 · 0,865 · 0,899 · 0,904 |
| `q` **focal** | 0,000 · 0,000 · 0,000002 · 0,000084 · 0,0018 · 0,155 · 0,221 · 0,691 · 0,733 |

Le traceur d'union donne, pour chacune de ces pistes, une valeur qui **colle à la fraction
étiquetée globale** du monde (0,69 – 0,81) : il mesure le mélange de l'union, pas le
remplacement du composant. Le traceur focal, sur exactement les mêmes pistes et les mêmes
octets, montre **quatre composants dont plus de 99,8 % de la matière a été remplacée**, dont
deux à un résidu exactement nul.

**Le traceur d'union surestime massivement le résidu et produirait des faux négatifs
systématiques.** C'est mesuré, sur des preuves relues, et non conjecturé.

### 5.5 Matrice de sensibilité — rapportée entière, aucune cellule sélectionnée

Diagnostic seulement, calculé sur les mêmes preuves, sans aucun re-tirage. La ligne gelée est
`seuil 0,45 · min_cells 3`, et sa recomputation reproduit exactement l'admission primaire —
c'est vérifié par assertion pour chacun des 48 mondes.

| seuil | min_cells | enroulement à t₀ | enroulement quelque part | mondes éligibles | `Y=1` à 0,01 / 0,05 / 0,20 |
|---|---|---|---|---|---|
| 0,30 | 2 / 3 / 5 | 48 | 48 | 0 | 0 / 0 / 0 |
| **0,45** | 2 / 3 / **5** | 6 | 48 | **0** | **0 / 0 / 0** |
| 0,60 | 2 | 0 | 0 | 9 | 0 / 0 / 0 |
| 0,60 | 3 | 0 | 0 | 9 | 0 / 0 / 0 |
| 0,60 | 5 | 0 | 0 | 8 | 0 / 0 / 0 |

Aucune cellule de cette matrice ne produit un seul `Y = 1` avec le traceur d'union. Le seuil de
détection ne sauve pas la conception : il déplace le problème de l'inéligibilité vers le
résidu.

---

## 6. Disposition

```text
pilot_disposition = PILOT_DESIGN_RISK_OBSERVED
```

Deux risques de conception distincts, tous deux mesurés :

1. **Le critère d'éligibilité gelé est incompatible avec la dynamique du moteur.** L'exigence
   « aucun composant enroulant nulle part à aucune trame » est violée par 48 mondes sur 48,
   parce que le moteur conduit le champ de matière vers une configuration percolante en
   médiane dès la première trame échantillonnée. À la conception gelée, le confirmatoire
   `67 × 2` renverrait `INDETERMINATE — MECHANICAL_INELIGIBILITY` avec une quasi-certitude,
   pour environ cinq minutes de calcul.
2. **La convention d'enrôlement en union masque la quantité mesurée.** Là où des composants
   sont éligibles, le résidu d'union se colle à la fraction étiquetée globale (≈ 0,74) tandis
   que le résidu focal des **mêmes** pistes descend à 0. La conception gelée produirait donc un
   NÉGATIF qui refléterait la convention de mesure, non la physique.

Ce que le pilote **ne** démontre **pas** : que Route E est fausse. Un résidu bas réellement
vérifié démontre que l'instrument peut répondre — et le diagnostic focal en montre quatre.
L'absence de résidu bas *sous la convention d'union* signale un risque de conception ; elle ne
démontre aucune impossibilité.

---

## 7. Suite complète et régressions

| | collectés | passés | échoués | ignorés |
|---|---|---|---|---|
| référence à `eccd46bc`, cet environnement | 1 469 | 1 435 | 12 | 22 |
| après cet incrément | 1 510 | 1 476 | 12 | 22 |

`new_failures = 0` : l'ensemble des identifiants en échec est **identique** à la référence.
Les douze se répartissent en deux familles, caractérisées et non déguisées :

* **5 hérités historiques** — `test_lattice_bond_stage_b.py::…[split|merge|tie|collapse]` et
  `test_motile_polar.py::test_scramble_preserves_all_declared_invariants…`, exactement ceux que
  le record `EXECUTION_BOUNDARY_CORRECTION` déclare ;
* **7 dus à `STOP_PINNED_VERIFIER_UNAVAILABLE`** — le vérificateur drand épinglé est absent de
  cet environnement, donc `verify_round` renvoie `configuration_error` là où les tests
  attendent `invalid`. Ils échouent **fermés**, ce qui est le comportement voulu ; ils sont
  reportés par décision propriétaire.

---

## 8. Déclaration finale factuelle

```text
a1_r5_confirmatory_disposition        = STOP
rng_mapping_version                   = U53_TOP_BITS_V1
rng_mapping_owner_decision_applied    = true
public_synthetic_y0_verified          = true
public_synthetic_y1_verified          = true
synthetic_rejected_by_engine_pilot_entry = true
real_engine_public_path_verified      = true
transition_transport_recomputed       = true
global_tracer_conservation_verified   = true
join_exact_coverage_verified          = true
track_continuity_verified             = true
technical_incident_fail_closed        = true
pilot_isolation_verified              = true
independent_gate_review               = FAIL, one corrective pass applied, gates re-verified
pilot_owner_authorized                = true
pilot_executed                        = true
pilot_worlds_expected                 = 48
pilot_worlds_completed                = 48
pilot_disposition                     = PILOT_DESIGN_RISK_OBSERVED
confirmatory_k_computed               = false
a2_authorized                         = false
confirmatory_run_authorized           = false
human_review                          = PENDING
```

Restent indispensables avant le confirmatoire, et explicitement non traités ici :
`STOP_PINNED_VERIFIER_UNAVAILABLE`, `STOP_SOURCE_AUTHORITY_UNFROZEN`,
`STOP_NAMESPACE_AUTHORITY_UNFROZEN`, `A2_PUBLIC_INCLUSION_PROOF_PENDING`, l'imposition
canonique de la forme `67 × 2`, le durcissement contre un système de fichiers hostile, et la
préenregistration confirmatoire complète.
