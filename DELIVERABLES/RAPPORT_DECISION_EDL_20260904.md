# EDL-FLAGSHIP-01 — Rapport de décision scientifique

**Date** : 2026-09-04 · **Version 2**, après revue contradictoire indépendante
(28 findings, 28 acceptés, 0 rejeté) · **Opérateur** : autonome

**Statuts atteints**
`RECOVERY_VERIFIED` · `EXPERIMENT_FROZEN` puis exécuté (CCRA01) ·
`RESULT_INCONCLUSIVE` pour OMLDCT03 · `READY_FOR_TOMMY_REVIEW`

> **Note de version.** La v1 de ce rapport contenait cinq erreurs fatales, dont
> un test statistique calculé sur le mauvais événement, un dimensionnement faux
> d'un facteur deux, et une conclusion « aucune expérience n'est justifiée » qui
> ignorait trois des quatre routes que le registre du programme nomme déjà. Le
> retour du checker est consigné verbatim
> (`REVIEW01/out/REVIEW01_CHECKER_RETURN_VERBATIM.md`,
> `sha256 f1d5b1b0…4084a1`, commit `4a632d9`) et **a été commité avant d'être
> traité**. L'adjudication est en `REVIEW01/out/REVIEW01_ADJUDICATION.md`.

---

## 0. Le résultat en six phrases

1. La charge de durabilité est intacte et l'état scientifique est **récupéré et
   vérifié par recalcul** : `METHODS_HASH` 17/17, empreintes publiées 7/7,
   6 verbatims de checker dont 4 confrontés à une empreinte déclarée.
2. Les **123 archives brutes (~440 Mo) sont absentes**, ainsi que les sorties de
   huit missions : aucun recalcul depuis les brutes n'est possible ici.
3. **GitHub est refusé (403), pas de pont** : la PR #34,
   `paper/persistence-without-ownership-v1` et la branche
   `codex/one-matched-locked-daughter-control-test-02` @ `99b8044a` sont
   **inaccessibles, non perdues**. Aucun jugement n'est porté sur elles.
4. **La thèse par défaut est conservée**, et je ne prétends pas l'avoir renforcée :
   sa jambe positive (FDOT01, FDFLT01) n'est pas dans l'état récupéré.
5. **Une expérience était justifiée, et elle est faite** : CCRA01, une ré-analyse
   en risques concurrents des 41 paires existantes, **zéro monde neuf, zéro
   archive brute**, spécifiée par un agent **aveugle**, gelée et hachée avant
   exécution, avec test de capacité 5/5. Résultat : **`NEGATIF`** — le critère
   gelé a été exécuté à une résolution démontrée suffisante et n'a pas été
   franchi.
6. **Aucune campagne coûtant des mondes n'est justifiée** : 12 h de calcul
   achètent ≈ 45 paires, soit une puissance de 0,15 ; 0,80 demanderait ≈ 400
   paires et ≈ 105 h murales — et ce « 400 » est un point sans barre d'erreur
   (34 % des vérités compatibles avec ces données donnent une puissance < 0,50 au
   même effectif).

---

## 1. Phase 1 — Récupération durable

### 1.1 Chaîne de vérification

| Contrôle | Résultat |
|---|---|
| base64 **stricte** (`validate=True`) | OK, 1 147 356 octets |
| `sha256(base64)` | `928b8969…c0d3ed` |
| `sha256(tar.gz)` **avant** extraction | `d1eb8ba1…7ba1bd` |
| gzip CRC32 + ISIZE | OK (860 517 → 4 167 680 octets) |
| tar lisible | 274 membres (246 fichiers, 28 répertoires) |
| chemins absolus · `..` · liens · fichiers spéciaux · collisions | **0 · 0 · 0 · 0 · 0** |
| extraction | quarantaine dédiée, `extractall(filter="data")` |
| `sha256` par fichier **avant vs après** | **246/246 identiques** |

Arbre récupéré : **246 fichiers, 3 963 075 octets de charge** ; arbre complet
hors `.git` au premier commit : 4 053 773 octets.

### 1.2 Vérifié par recalcul

| Objet | Valeur | Verdict |
|---|---|---|
| `METHODS_HASH` (formule gelée appelée, non réimplémentée, 17 fichiers) | `21571fb4…d4d63c920a007e188bdc24e0d94d1f99` | **VÉRIFIÉ** — identique à la note d'armement et au champ du `TBRT02_MASTER_FREEZE`, concordance fichier par fichier 17/17 |
| `TBRT02/out/SHA256SUMS` | 7 entrées | **VÉRIFIÉ 7/7 — au niveau des OCTETS** |
| Verbatims de checker | 6 fichiers | `CLOSE01 = 1543a8c9…135e` ; 4 des 6 confrontés à l'empreinte déclarée dans leur adjudication, toutes concordantes ; RPP97 et TBRT02-C4bis n'en déclarent pas |
| Test gelé d'OMLDCT03 | 12 grandeurs | **REPRODUIT AU DERNIER CHIFFRE** par implémentation indépendante |
| **CCRA01** (nouveau) | composite ordonné, 41 paires | **VÉRIFIÉ** — recalculé par un second chemin : 17 / 24 / 0, `p = 983500178123/1099511627776`, `theta_hat = −0,17073170731707318`, concordance exacte |

**Une vérification d'empreinte atteste des octets, jamais du contenu.**
Illustration prise dans ces mêmes 7/7 :
`TBRT02/out/TBRT02_CONNECTIVITY_EXPOSURE.json` a une empreinte juste et un
contenu **vide** — `RECORDS = {}`, `N_ADMISSIBLE_TRIPLES_COVERED = 0`, généré le
2026-08-27T03:20:33, **avant l'existence du premier triplet admissible**.
Conséquence : l'hypothèse de connexité **ne peut pas** être re-testée sans relire
les archives brutes, contrairement à ce que sa propre section `MOTIVE` annonce.

Le test gelé d'OMLDCT03, recalculé :

| | `W+` | `n` | `p` exact bilatéral | médiane | HL | IC 95 % |
|---|---|---|---|---|---|---|
| durée | 521,0 | 41 | 0,24638633591985126 | +0,21357410029805912 | +0,33307812236654888 | (−0,238539 ; 0,836988) |
| exposition | 504,0 | 41 | 0,34791725337890966 | +0,56946808437843366 | +0,31613569679774711 | (−0,310966 ; 0,873899) |

Aucune égalité dans les |différences| ; 25/41 positives sur les deux critères.
**C'est une reconstruction sur les mêmes 41 paires, pas une réplication
indépendante.**

### 1.3 Divergences réconciliées

| Point | Consigné à l'armement | Constaté | Résolution |
|---|---|---|---|
| empreintes publiées | 6/6 | `SHA256SUMS` en liste **7** | 7/7 vérifiées ; le compte de 6 précède l'ajout de `TBRT02_SEQUENTIAL_ADDENDUM.json` (déclaré le 2026-08-27T03:19:42Z) |
| verbatims de checker | 5/5 | **6** présents | 6 vérifiés ; 2 sans empreinte déclarée dans leur adjudication (schéma différent) |

**Une « divergence » annoncée dans la v1 n'en était pas une** : RPP97 mesure une
taille de composante *en cellules* dans deux fenêtres antérieures au fork (`t_m`
médian 713 sur ces 41 triplets, donc `[t_m−2000, t_m−1000]` est tronquée au début
du monde pour 41/41), tandis que RPP98 mesure une masse parentale *en quanta Y*
sur des épisodes bien plus tardifs. Unités différentes, supports temporels
disjoints, objets différents. Retiré.

### 1.4 Ce qui est absent, et ce que cela interdit

- **Les 123 archives brutes (~440 Mo).** Aucun `.npz`. → interdit tout recalcul
  depuis les brutes et toute lecture de `c_cid`, donc **le legs primaire de
  TBRT02**.
- **Sorties absentes** : `FDOT01/out`, `FDFLT01/out`, `OMLDCT02/out`,
  `TLMR01/out`, `ORR01/out`, `OBTC02/out`, `FMRCT01/out`, `FMRT01/out`. En
  particulier `OMLDCT02_MASTER_FREEZE.json` est absent : le gel qu'OMLDCT03
  déclare exécuter n'est lisible ici **que par les citations qu'en font OMLDCT03
  et son checker**.
- **Toute la provenance git**, et le répertoire `paper/`.

**Dix** répertoires portent un `out/` : BPRTC01, CLOSE01, FIMRCC02, GATE01,
MCTT01, OMLDCT03, PQEC01, RPP97, RPP98, TBRT02. Trois n'ont pas été audités ici
et devraient l'être : `MCTT01/out/MCTT01_SELECTED_LAW.json` — **c'est le fichier
qui fixe `LAW_C_MCTT01`, la loi dont tous ces résultats dépendent** —,
`PQEC01/out/PQEC01_MASTER_FREEZE.json`, `BPRTC01/out/BPRTC01_MASTER_FREEZE.json`.

### 1.5 Sauvegarde durable

GitHub renvoie **403 au proxy de session**. Refus non contourné, aucun jeton
demandé. La sauvegarde prend donc la seule forme disponible : dépôt local propre,
branche **`recovery/edl-state-20260904`**, premier commit **sans parent**, portant
le manifeste, les 246 empreintes avant/après, l'empreinte de chaque fichier, le
rapport de récupération, **deux scripts de vérification**, le retour de checker
verbatim, son adjudication, et le gel + le résultat de CCRA01 — puis un **bundle
git** livré hors du conteneur.

Le commit initial dit explicitement qu'il **n'hérite d'aucune histoire git**,
qu'il n'est descendant ni de `99b8044a…`, ni de `5372fd8`, ni de `77cc3c70…`, et
qu'aucun commit d'origine n'est reconstruit ou reparenté. `main` n'est pas
touché ; aucune branche existante n'est écrasée.

> **Ce que la revue a trouvé ici, et que je répète pour qu'il ne se reperde pas** :
> le premier bundle, déjà livré, ne contenait pas les deux scripts — ils ont été
> écrits *après* lui. C'est le legs `OPERATIONAL` de TBRT02 C5 (« durability is
> not a commit ») répété six heures après l'avoir cité. Le bundle final et son
> empreinte figurent au §5.

---

## 2. Phase 2 — Audit scientifique

### 2.1 Les trois lignes hors de portée

PR #34, `paper/persistence-without-ownership-v1`, branche `codex/…` @ `99b8044a`
— **non lues, GitHub 403, non déclarées perdues**. Aucun jugement n'est porté sur
elles. Toute note comparative que j'écrirais serait de la fabrication.

### 2.2 TBRT02 — vérifié sur artefacts

- **Question** : après retrait de l'influence parentale, et en présence d'une
  source Y concurrente appariée qu'elle pourrait absorber à tort, une organisation
  issue de la fille conserve-t-elle une ascendance propre ?
- **Positif réel** : 885 graines, 53 déclenchées, **41 triplets valides** (cible
  41), 609,52 instances-bras sur 926 (plafond non contraignant), **`technical_failures = 0`**,
  `METHODS_HASH` inchangé de bout en bout. Les 123 archives ont été vérifiées au
  sha256 **au moment où elles ont été scellées** ; la dernière exécution commitée
  de la porte d'intégrité du programme (`GATE01/out/OMLDCT03_INTEGRITY.json`,
  2026-08-30T06:33) rend `sha256_mismatch = 0`, **`missing = 123`**,
  `INTEGRITY_GATE_PASSES = false` — elle échoue **parce que les archives sont
  absentes du conteneur**, non parce qu'une empreinte diverge.
- **Négatif réel** : la mission **n'adjuge rien**. La condition de réfutation a
  été gelée *en mots* et jamais opérationnalisée en code. Sous la lecture stricte
  elle **ne peut pas se déclencher** (démontré, cherché sur > 4000 mondes adverses
  dont 7560 lignes de contact direct) ; sous la lecture au niveau du corps fournie
  *après coup*, elle se déclenche 17 fois sur 41. Aucune des deux n'était fixée
  avant les données.
- **Puissance / effectif** : 41 triplets. Borne séquentielle pré-enregistrée
  0,070461 à n = 41 — **inadmissible et non rapportée comme résultat**.
- **Prospectif / post hoc** : design, graines, plafond, addendum séquentiel
  (déclaré à 9 graines, 0 triplet) : prospectifs. La condition de réfutation
  effective : **post hoc**.
- **Contrôles** : SHAM / SELECTIVE appariés sur la même graine, préfixe identique
  bit à bit jusqu'à `t_m` sur les trois bras des 41 triplets. Disjonction des
  graines avec OMLDCT02 : **intersection 0**, régénérée depuis la dérivation
  commitée par le checker.
- **Confusions** : le déplacement est plus invasif que le retrait (téléportation
  hors de tout canal du moteur), bornée et certifiée sur objets réels.
- **Portée** : `MODEL_C_STATUS = NOT_REFUTED AND NOT CORROBORATED`.
  `NOTHING_IN_THIS_MISSION_ESTABLISHES_ANY_CLAIM_ABOUT_LINEAGE_IN_THE_WORLD`.
- **Manque pour publier** : la condition au niveau du corps, gelée **en code**,
  avec test de capacité, lue sur les 41 triplets — zéro monde neuf, mais **exige
  les archives brutes**. Six erreurs d'opérateur sont listées par la mission
  elle-même : elle n'est pas « techniquement irréprochable », elle a zéro échec
  technique, ce qui n'est pas la même chose.

### 2.3 OMLDCT03 — vérifié et recalculé

- **Positif réel** : 41/41 paires admissibles, accord des deux classificateurs
  gelés sur les 82 bras. Le checker de la mission, après réimplémentation *from
  scratch*, retrouve durée, exposition et type de terminaison sur 41/41 paires et
  82/82 bras, **zéro écart**. Mon propre recalcul retrouve les 12 statistiques au
  dernier chiffre.
- **Négatif réel** : **effet non détecté**, règle ET non franchie.
  `TERMINAL = MATCHED_LOCKED_DAUGHTER_CONTROL_EFFECT_NOT_DETECTED__INCONCLUSIVE_UNDER_FROZEN_POWER`,
  `NULL_RESULT_INTERPRETATION = INCONCLUSIVE__NO_CLAIM_OF_EQUIVALENCE__NO_CLAIM_OF_NO_EFFECT`.
- **Puissance** : à l'**effet observé** (rééchantillonnage des 41 différences —
  c'est une puissance *a posteriori*, monotone du p, pas une information neuve) :
  **0,14** pour la règle ET à n = 41. La **puissance gelée à la conception** valait
  0,402 / 0,971 / 1,000 (borne basse de Wilson / estimation ponctuelle / borne
  haute), d'après `LDFMA01/out/HANDOFF…md` — **DÉCLARÉ**, le fichier est absent,
  mais deux findings acceptés concordants le citent. Ce n'est donc pas le test qui
  était sous-puissant par conception : **c'est l'hypothèse de puissance de la
  conception qui était fausse.**
- **Prospectif / post hoc** : la **procédure statistique** est prospective et a
  été exécutée sans modification. L'**accrual** ne l'est pas : la règle d'arrêt
  gelée d'OMLDCT02 (plafond 512 instances-bras) appliquée au flux de TBRT02
  s'épuise à l'indice 789 avec **38** paires et rendrait
  `INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS`. **Et la décision de l'exécuter ne l'est
  pas non plus** : la direction d'un contraste apparié corrélé sur ces mêmes 41
  graines était publiée deux jours plus tôt (`TBRT02_C4_ANALYSIS.json §12`,
  24 positifs / 7 nuls / 10 négatifs, test des signes exact **p = 0,024307**,
  recalculé). Cela n'enfle pas l'erreur de première espèce ; cela coûte la
  revendication d'aveuglement.
- **Confusions — les deux qui portent** :
  1. **Mortalité différentielle.** Sur toute la trajectoire post-`t_m` :
     **11 paires** où le traitement éteint et le témoin non, **1** l'inverse,
     **1** les deux, **28** aucune — test des signes exact **p = 0,00634765625**
     (`FIMRCC02_POWER.json`, vérifié). *Le cadrage « 12 contre 2 » a été
     formellement retiré par le programme et n'est pas ré-émis ici.* Le `p = 0,246`
     publié est un **mélange** : médiane +0,6325 sur les 28 paires sans extinction,
     **−0,3231** sur les 13 qui en contiennent — **et, sur les 32 paires sans
     extinction dans le bras traité, le critère primaire seul rend `p = 0,0433`,
     médiane +0,6325.** Ce chiffre franchit l'alpha gelé ; il conditionne sur une
     variable post-traitement et est **inadmissible comme estimand**. Je le donne
     parce que le taire serait la divulgation asymétrique exacte pour laquelle
     CLOSE01 a été retirée.
  2. **Non-échangeabilité structurelle.** Le canal MERGE exige au moins deux
     prédécesseurs (`omldct02_e3_b.py:107-131, 216-220`, **relu ici**). Quand la
     fille est le seul objet du monde, il est **arithmétiquement inatteignable**.
     Mélange observé — SELECTIVE 32/9/0/0, SHAM 28/0/7/6 — et occupation
     mono-composante **99,6 % contre 6,4 %** (CITÉ du checker : les brutes sont
     absentes). **Le canal n'est pas supprimé, il est supprimé sur les 99,6 % de
     pas à risque et raréfié ailleurs** : dans les 33 paires d'OMLDCT02 il se
     déclenche **2 fois** sous SELECTIVE contre 5 sous SHAM.
  - **Un troisième point, statistique, que la v1 avait manqué** : les deux
    critères de la règle ET sont corrélés à **ρ = 0,9751** avec 41/41 accords de
    signe. C'est **un critère rapporté deux fois** ; la conjonction n'achète
    presque aucune sévérité. Il manque donc bien quelque chose de statistique à
    OMLDCT03, contrairement à ce que la v1 affirmait — de même que ses findings
    F1 (accrual), F4 (la phrase portante du fichier d'admissibilité est fausse
    telle qu'écrite), F5 (porte d'intégrité sautée), F9 (clauses héritées absentes).
- **Portée** : exécution valide de la *procédure* statistique gelée d'OMLDCT02 sur
  un échantillon apparié de 41 paires — **pas** de l'*expérience* gelée
  d'OMLDCT02.

### 2.4 CCRA01 — nouvelle, gelée, exécutée, `NEGATIF`

*Détail complet au §4.* Composite ordonné insensible au renommage de chaîne :
17 paires où SELECTIVE est strictement pire, 24 où il est strictement meilleur,
0 égalité ; `p` unilatéral exact = 0,8944882011955997 contre la direction
pré-déclarée `theta > 0` ; seuil non franchi à une résolution démontrée
suffisante (`k` critique 28, `DESIGN_COULD_HAVE_REJECTED = true`).

### 2.5 Lignes retirées

**RPP97** — `WITHDRAWN_AS_A_DESCRIPTION__ARITHMETIC_SOUND__SCIENCE_MIS_SPECIFIED`.
Pré-enregistrement détruit avec le conteneur **après** lecture des premiers
chiffres → `POST_HOC__CANNOT_ADJUDICATE`. Fenêtres antérieures au fork, donc
contraste entre bras vide par construction. `S1` indéfini sur 99,56 % des
pas-composantes. **Aucun chiffre utilisable.** Je ne dis **pas** que la piste
Reynolds / Ponce-Dawson / Pearson 1997 est fermée : `TBRT02_C5_CLOSURE §6[1]` et
CLOSE01 F17 route 2 l'inscrivent au legs comme faisable sur les séries par pas
déjà archivées. C'est RPP97 qui est retirée, pas la question.

**RPP98** — `WITHDRAWN__…_THE_COUNTED_EVENT_IS_NOT_THE_CLAIMED_EVENT`. Descriptif
d'intégrité intact et utile ; ne fonde aucune revendication.

**FIMRCC02** — `WITHDRAWN__A_PREREGISTERED_TEST_ALREADY_EXISTS…`. **Son analyse de
puissance tient** et elle est décisive : E3/E4/E5 tels que gelés sont
`NON_INTERPRETABLES__CONFONDUS_PAR_LA_MORTALITE_DIFFERENTIELLE` (chaîne française
d'origine, `FIMRCC02_POWER.json`). Écrite avant tout gel, aucune archive ouverte.

**CLOSE01** — `WITHDRAWN_AS_WRITTEN`, 22 findings, 22 acceptés. Tiennent : ses §0
et §7, les chiffres copiés, les deux hachages de contenu, la réserve sur
l'accrual. **Et son F17, que la v1 avait ignoré : quatre routes concrètes, dont
trois sur des données existantes.**

### 2.6 Déclarés seulement

`code/` récupéré, `out/` absent : FDOT01 (7/160, e-value ≈ 5,2), FDFLT01 (53/192,
`p = 5,26 × 10⁻¹²`, `E = 1,22 × 10¹⁰`), FMRCT01 (`K = 0/372`), OMLDCT02 (33/805),
OBTC02 (r80 7,071 vs 7,036). **Non vérifiables ici.** Le « 805 » est toutefois
cité dans `TBRT02_MASTER_FREEZE.HOW_THE_CEILING_WAS_SIZED`.

### 2.7 Ce que l'audit établit

Aucune ligne de l'état récupéré ne porte une revendication positive à la fois
vérifiée ici et non retirée. Deux faits sont corroborés par **deux campagnes
indépendantes** — et il y en a exactement deux, pas un :

- la **dégénérescence de CLEA01** : sous SELECTIVE, l'ensemble de lignage
  permissif est identique au certain dans 41/41 mondes ; CLEA01 avait clos sur
  exactement cela ;
- la **non-échangeabilité de l'endpoint** : SELECTIVE 32/9/0/0 contre SHAM
  28/0/7/6 sur 41 paires, et 29 split / 2 merge / 2 extinction contre
  22 / 5 / 6 sur les 33 paires indépendantes d'OMLDCT02.

---

## 3. Phase 3 — Choix de la thèse

**Thèse conservée, inchangée** : *un état historique reste causalement actif
pendant un renouvellement profond de la matière, mais persistance et causalité ne
suffisent pas à établir une propriété locale ou une individualité.*

Je n'ai pas changé de thèse et **je ne prétends pas l'avoir renforcée** : sa jambe
positive n'est pas dans l'état récupéré et son manuscrit est derrière un 403.

Ce que cette relève lui apporte : **sa borne, et un test gelé qui la tient**. La
jambe négative était portée par des retraits et des dégénérescences d'instrument.
Elle gagne (i) un argument structurel vérifié et corroboré sur deux campagnes, et
(ii) **CCRA01**, un critère pré-enregistré par un agent aveugle, testé en
capacité, exécuté, et non franchi — un `NEGATIVE_BUT_VALID` au sens du programme,
qui se cite et se publie.

**PR #34 reste papier compagnon / repère négatif, non fusionnée, non soumise.**

Le manuscrit livré n'est pas le papier phare : c'est la **section de bornage** que
le papier phare exige, écrite comme un texte autonome parce qu'elle est
intégralement soutenue par des artefacts vérifiables.

**Antériorité, précisément.** La **mortalité différentielle** est écrite trois
fois dans le programme (`GATE01/EDL_PRIOR_ART_MAP.json` 2026-08-30T02:07:38 ;
`FIMRCC02_POWER.json` T02:11:47 ; checker OMLDCT03 F2). La **suppression du canal
MERGE** est écrite **une seule fois**, dans le checker d'OMLDCT03 F3, et nulle
part ailleurs. Aucune des deux n'est une découverte de cette relève ; la
contribution est l'assemblage, la vérification, la corroboration sur une seconde
campagne, la généralisation — et CCRA01, qui est neuf.

### Notation

| Axe | Thèse phare | Manuscrit de bornage + CCRA01 | PR #34 |
|---|---|---|---|
| Solidité scientifique | non évaluable ici | **8/10** | non évaluable |
| Nouveauté conceptuelle | 6/10 (déclaré) | **5/10** — le fait est connu du programme, jamais publié ; CCRA01 est neuf | non évaluable |
| Puissance empirique | non évaluable ici | **4/10** — n = 41 + n = 33 ; CCRA01 a une résolution démontrée mais un seul jeu | non évaluable |
| Reproductibilité | non évaluable ici | **8/10** — 3 scripts autonomes, bibliothèque standard, gel haché avant exécution ; −1 parce que le premier bundle livré ne les contenait pas | non évaluable |
| Potentiel de publication | non évaluable ici | **6/10** — Registered Report / note méthodologique | non évaluable |
| Risque de surinterprétation | **élevé** | **faible** | non évaluable |

---

## 4. Phase 4 — L'expérience : justifiée, gelée, exécutée

`CLOSE01_CHECKER_ADJUDICATION.FINDINGS.F15_F16_F17…`, verdict `ACCEPTED`, gravité
`PORTANTE`, champ `les_quatre_pistes_tues`, nomme quatre routes **dont trois sur
des données qui existent déjà**. La v1 n'en examinait qu'une. La route 3 —
*risques concurrents pour la mortalité différentielle : analyse cause-spécifique
ou composite ordonné* — ne coûte **ni un monde ni une archive brute**.

### 4.1 Comment le biais a été évité

J'avais vu la table de sensibilité, le mélange des terminaisons et la direction du
contraste. **Un pré-enregistrement écrit par moi aurait été du théâtre.** CCRA01 a
donc été spécifié par un **agent aveugle**, à qui ont été donnés le design, les
deux classificateurs gelés, le schéma des champs et le seul fait structurel sur
MERGE — et **aucune valeur d'issue**. Sa préregistration déclare sa propre
contamination et il confirme n'avoir ouvert aucun fichier de résultat.

### 4.2 Le gel

`CCRA01/out/CCRA01_PREREGISTRATION.md` `sha256 2cae5619…dad39` ·
`CCRA01/code/ccra01_frozen.py` `sha256 df1d4d6e…273b3` · **commit `c363afd`,
avant toute lecture des données réelles.**

Mapping chaîne → cause, justifié sur le code et non sur une interprétation :

| chaînes | cause | rang |
|---|---|---|
| `OUT_OF_RANGE`, `NO_COMPONENT_AT_THE_NEXT_STEP` | `NO_LINKABLE_SUCCESSOR` | 0 (pire) |
| `SPLIT_OR_TIE`, `MERGE` | `AMBIGUOUS_CONTINUATION` | 1 |
| `REACHED_THE_WINDOW_HORIZON` | `NO_TERMINATION_OBSERVED` | 2 (meilleure) |

Les deux fusions sont des théorèmes sur `_link_map`, pas des espérances. La
première : les deux chaînes recouvrent le même prédicat `rc[cur] == 0`, scindé par
une propriété *globale* du monde — donc le même événement change d'étiquette selon
le bras. La seconde : `MERGE` seul est inatteignable quand la fille est seule,
mais l'union `SPLIT_OR_TIE ∪ MERGE` est atteignable des deux côtés. **Les trois
rangs sont atteignables dans les deux bras.**

Estimand : `theta = P(SELECTIVE strictement pire) − P(SELECTIVE strictement
meilleur)` sur le composite lexicographique (rang, durée) — un **effet total**,
identifié par le seul appariement exact. Test des signes apparié exact,
unilatéral, `alpha = 1/40` en arithmétique entière, aucun flottant au seuil.
Rétention : **les 41 paires, sans exception** ; les exclusions tentantes sont
nommées et interdites d'avance.

**Test de capacité 5/5 PASS** — le legs primaire de TBRT02 honoré : C1 la
statistique *peut* franchir ; C2 elle ne franchit pas sous permutation
d'étiquettes de bras (2000 réplicats, taux 0,0135 ≤ alpha) ; C3 et C5 recherches
adverses ; C4 queue exacte recoupée par énumération des 2^m séquences, m = 0..14,
0 divergence. **C5 mesure l'artefact évité** : sous un pur renommage
`OUT_OF_RANGE → NO_COMPONENT_AT_THE_NEXT_STEP` dans le seul bras traité, une
statistique naïve fondée sur les chaînes se déplace de **8 paires** ; la
statistique gelée ne bouge pas d'un bit.

### 4.3 Le résultat — `TERMINAL = NEGATIF`

| | |
|---|---|
| paires retenues | **41 / 41**, 0 exclusion |
| SELECTIVE strictement pire | **17** |
| SELECTIVE strictement meilleur | **24** |
| égalités | 0 |
| décidées par le rang seul / par le départage sur la durée | 11 / 30 |
| `k` critique à `alpha = 1/40` | 28 · `DESIGN_COULD_HAVE_REJECTED = true` |
| `p` unilatéral exact | `983500178123/1099511627776` = **0,8944882011955997** |
| `theta_hat` | **−0,17073170731707318** |
| terminal | `NEGATIF` · `THRESHOLD_NOT_CROSSED_AT_ADEQUATE_RESOLUTION` |

Recalculé par un second chemin, concordance exacte sur les quatre grandeurs.

**Ce que cela dit** : la direction pré-déclarée — SELECTIVE plus souvent la pire
des deux issues, ce que produirait le confondant de mortalité — **n'est pas
soutenue**. Le confondant ne domine pas le composite : les 9 issues de rang 0 du
bras traité sont compensées par le départage sur la durée.

**Ce que cela ne dit pas** : le test est unilatéral ; malgré `theta_hat` négatif,
**rien n'est revendiqué dans l'autre direction**. Aucune équivalence, aucune
absence d'effet. Rien sur une capacité de la fille verrouillée, rien sur un
mécanisme, rien sur les hasards cause-spécifiques par canal (non identifiables
ici), rien sur le bras DISPLACED, rien hors de ce jeu de paramètres gelé.

### 4.4 Aucune campagne coûtant des mondes n'est justifiée

Coûts **mesurés sur les 885 lignes du ledger scellé**, non importés de
l'extérieur : `runtime_s` médiane **85,10 s**, moyenne **89,38 s**, écart-type
97,06 s, max 627,6 s ; `batch_seconds` 39 065,1 et 38 977,7 → **10,85 h de temps
mural à 2 workers pour 885 graines**, soit 0,01226 h/graine.

Rendement admissible : **observé 41/885 = 4,633 %**. Le 4,10 % de la consigne est
33/805, le rendement **déclaré** d'OMLDCT02, dont les sorties sont absentes.
Comme EVCS01 l'a imposé après avoir trouvé l'erreur dans son propre instrument, le
taux est tiré d'un **postérieur de Jeffreys** Beta(41,5 ; 844,5) et non tenu au
point estimé : médiane 4,650 %, q05 **3,578 %**, q95 5,906 %.

| n paires | puissance (règle ET, effet observé) | graines (q50) | graines (q05 défavorable) | inst.-bras 2 br | h murales @ 2 workers |
|---:|---:|---:|---:|---:|---:|
| 41 | 0,139 | 882 | 1 146 | 570 | 10,8 |
| 45 | 0,152 | 968 | 1 258 | 625 | 11,9 |
| 100 | 0,322 | 2 151 | 2 795 | 1 389 | 26,4 |
| 200 | 0,563 | 4 302 | 5 590 | 2 779 | 52,7 |
| 400 | 0,828 | 8 603 | 11 180 | 5 557 | **105,5** |

**12 h murales à 2 workers ≈ 978 graines ≈ 45 paires (q50), 35 au q05 → puissance
≈ 0,15.** Il manque un facteur ≈ 9 en temps mural, et le plafond historique le
plus élevé enregistré dans cette récupération est 926 instances-bras contre les
5 557 requises.

**Et ce « 400 » n'a pas de barre.** Double bootstrap (100 vérités rééchantillonnées
× 200 tirages) : à n = 400 la puissance va de 0,02 (q05) à 1,00 (q95), médiane
0,885, et **34 % des vérités compatibles avec ces 41 paires donnent une puissance
< 0,50**. L'IC de Hodges-Lehmann contient zéro : au niveau 95 %, **l'effectif
requis pour 0,80 n'est pas borné supérieurement**. Cette puissance est en outre
une puissance *a posteriori*, fonction monotone du `p` observé.

**Il n'y a par ailleurs aucun exécuteur durable** : le conteneur a été effacé
entre deux tours de cette session, GitHub est refusé, il n'y a pas de pont.

**Les deux routes encore ouvertes, à zéro monde neuf**, sont la condition au
niveau du corps gelée en code (route 1 — exige les brutes) et la comparaison au
mécanisme de déplétion du cœur sur les séries par pas déjà archivées (route 2 —
exige les brutes également).

---

## 5. Phase 5 — Livraison

| Livrable | Fichier | État |
|---|---|---|
| Rapport de décision (FR) | `RAPPORT_DECISION_EDL_20260904.md` | ce document, v2 |
| Manuscrit (EN) | `MS_EDL_NONEXCHANGEABILITY_v0.2.md` | brouillon, **non soumis** |
| Matrice revendication → preuve | `CLAIM_EVIDENCE_MATRIX.md` | v2 |
| Retour de checker verbatim | `REVIEW01/out/REVIEW01_CHECKER_RETURN_VERBATIM.md` | `sha256 f1d5b1b0…4084a1`, **commité avant traitement** |
| Adjudication | `REVIEW01/out/REVIEW01_ADJUDICATION.md` | 28 acceptés, 0 rejeté |
| Gel CCRA01 | `CCRA01/out/CCRA01_PREREGISTRATION.md` · `CCRA01/code/ccra01_frozen.py` | `2cae5619…` · `df1d4d6e…`, commit `c363afd` |
| Capacité + résultat CCRA01 | `CCRA01/out/CCRA01_CAPABILITY.json` · `CCRA01_RESULT.json` | 5/5 PASS · `NEGATIF` |
| Scripts de reconstruction | `RECOVERY/scripts/*.py` | exécutés, `ALL_CHECKS_PASS` |
| Bundle de récupération | `EDL_RECOVERY_20260904.bundle` | empreinte au §5.1 |
| Draft PR | **non créée** — GitHub 403 | bloquée |

### 5.1 Interdits respectés

PR #34 ni fusionnée ni publiée · TBRT01 non relancé comme prospectif · aucune
expérience ouverte sans décision préalable · aucune revendication d'individuation
restaurée · **aucun holdout fabriqué après coup — CCRA01 retient les 41 paires et
interdit d'avance les exclusions tentantes** · simulation reproductible jamais
présentée comme validation externe · aucune série de commandes demandée · aucun
travail refait là où une récupération suffisait · aucune valeur, seuil ou graine
gelée touchée · aucun fichier de méthode reconstruit · garde non relâché ·
histoire héritée non réécrite · aucun worker de campagne relancé ·
`tbrt02_repair.py` jamais exécuté · retour de checker commité **avant** d'être
traité.

**Un écart que je déclare** : le gel CCRA01 aurait dû être commité **seul**, à la
manière du C2 de TBRT02. Le commit `c363afd` porte aussi
`REVIEW01_ADJUDICATION.md`. Aucun champ du gel n'en dépend et les empreintes des
deux fichiers gelés sont publiées, mais la convention n'a pas été tenue.

### 5.2 Statuts — les seize, ré-émis à l'identique

`H3_STATUS = NOT_TESTED` · `REPRODUCTION_STATUS = NOT_TESTED` ·
`HEREDITY_STATUS = NOT_TESTED` · `AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED` ·
`X_LAWSPEC_BASELINE = UNCHANGED` · `ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED` ·
`COMPANION_PAPER_V1_1_STATUS = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED` ·
`OMLDCT02_STATUS = INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED` ·
`CLEA01_STATUS = CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED` ·
`TBRT02_STATUS = CLOSED__RAW_COMPLETE__PRIMARY_ADJUDICATION_INCONCLUSIVE_BY_CONSTRUCTION` ·
`FIMRCC01_E3_E4_E5_STATUS = FUTURE_QUESTION_RECORDED__NOT_AUTHORISED` ·
`OBFOR01_HISTORICAL_WINDOW_STATUS = NOT_PORTABLE` ·
`RPP97_STATUS = WITHDRAWN_AS_A_DESCRIPTION__ARITHMETIC_SOUND__SCIENCE_MIS_SPECIFIED` ·
`RPP98_STATUS = WITHDRAWN__THE_QUESTION_WAS_ALREADY_ANSWERED_BY_TLMR01__AND_THE_COUNTED_EVENT_IS_NOT_THE_CLAIMED_EVENT` ·
`FIMRCC02_STATUS = WITHDRAWN__A_PREREGISTERED_TEST_ALREADY_EXISTS__AND_THE_CENTRAL_PREMISE_IS_FALSE_BY_DEFINITION` ·
`OMLDCT03_STATUS = FROZEN_STATISTICAL_PROCEDURE_EXECUTED_AT_ITS_REQUIRED_N_ON_A_MATCHED_SAMPLE_OBTAINED_OUTSIDE_ITS_ACCRUAL_RULE__EFFECT_NOT_DETECTED__INCONCLUSIVE`

Nouveau : `CCRA01_STATUS = FROZEN_BY_A_BLIND_SPECIFIER__CAPABILITY_TESTED__EXECUTED__NEGATIF__THRESHOLD_NOT_CROSSED_AT_ADEQUATE_RESOLUTION`.

---

## 6. L'unique action humaine nécessaire

**Rouvrir l'application de bureau Claude sur la machine Windows et relancer cette
tâche depuis cette application, avec le dossier `Documents/ising v3` connecté.**

Ce geste unique débloque les quatre choses qui manquent : les 123 archives brutes
(donc les routes 1 et 2, sans un monde neuf), les sorties absentes de huit
missions, un chemin d'écriture durable hors du conteneur, et la possibilité que ce
soit vous qui poussiez la branche `recovery/edl-state-20260904` — le proxy de
cette session refuse GitHub et je ne contourne pas ce refus.

En attendant, le bundle vous a été livré : il ne dépend d'aucun conteneur.
