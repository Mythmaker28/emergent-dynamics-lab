# FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00 — rapport (révision après `HUMAN_REVIEW_REVISE`)

> ## Disposition candidate : `ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_MANDATE_ADDRESSED_PRB6_OPEN`
>
> **Cinq des six `PRE_RUN_BLOCKER` gelés sont fermés mécaniquement : PRB-1, PRB-2, PRB-3,
> PRB-4, PRB-5.**
> **`PRB-6` reste OUVERT** : aucun vérificateur cryptographique n'existe dans l'allowlist
> gelée. Le verrou est implémenté et refuse en son absence ; le vérificateur lui-même
> n'est pas livré. Ce blocker est **rapporté, pas maquillé**.
>
> Les onze corrections `HR-1 … HR-11` ordonnées par la revue `bc2a42c4` sont appliquées.
>
> **`scientific_run_authorized = false`.** Ce record ne prononce aucune acceptation
> humaine.

---

## 0. Les quatre catégories, tenues séparées

1. **Preuves mécaniques** — 933 tests, reproduits ici.
2. **Décisions de gouvernance** — les verrous, les seuils, les préconditions.
3. **Limitations** — `LK-L1 … LK-L3`, `RE-L1 … RE-L9`, plus les résidus par blocker.
4. **Résultats scientifiques** — **catégorie vide.**

---

## 1. Autorité, lignée, portée — **la portée du §8 restituée en entier (HR-11)**

| Élément | Valeur |
|---|---|
| Record définissant le mandat | `00afcdd1aacbdf32bb030d85ced735a2920421f6` |
| Candidat partiel révisé | `c6d4acf037d4e51d59e5b75dc91b977b9eb83dbd` |
| Revue contraignante | `bc2a42c468eec5a4e1732ebb08c7cc20c4dab7dd`, disposition `HUMAN_REVIEW_REVISE` |
| Lignée | `00afcdd1 → c6d4acf → bc2a42c → cette révision`, chaîne linéaire, aucun merge |
| Branche | `codex/future-route-e-pre-run-blocker-closure-00-revision` (nom Git, **pas** un identifiant scientifique) |

### 1.1 Ce que le §8 du record accepté dit, avec son titre

Le rapport précédent citait fidèlement les six items **en omettant le titre du bloc**,
donc leur portée. Le voici en entier, littéralement :

> **Obligations portées à la prérégistration** (`ROUTE_E_REPLICATION_DENSITY_PREREGISTRATION_00`),
> à n'exécuter qu'après fermeture **et** revue humaine des blockers :
> 1. Chiffrer les deux seuils non chiffrés (A16 / B16) …
> 2. Nommer le générateur externe, l'ordre des tirages et la stratégie de seed (L-HR2) …
> 3. Faire du prédicat d'acceptation du sampler la construction du `LatticeBondSpec` (L-HR1) …
> 4. Préenregistrer la rupture de track par la porte d'association (B17) …
> 5. Dire de quel `Δ` parle le plafond de claim (A18) …
> 6. Nommer `run_owned_future_pipeline` dans le test de refus de PRB-5 (B15) …

Et, du mandat de cette mission, le même §8 dit :

> `FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00` **pourra** fermer les six `PRE_RUN_BLOCKER`.

**Deux couches, deux missions.** A–F appartiennent à la prérégistration ; `PRB-1 … PRB-6`
sont le mandat de cette mission. **Aucun renommage A→1, B→2 n'est effectué**, et le
travail A–F ne consomme pas la mission.

### 1.2 Allowlist, écrite avant la première édition

| # | Chemin | Statut | Justification littérale |
|---|---|---|---|
| 1 | `edlab/substrates/lattice_bond/future_route_e_pre_run_locks.py` | **ajouté** | mécanisme des six `PRE_RUN_BLOCKER` — mandat |
| 2 | `tests/test_future_route_e_pre_run_locks_00.py` | **ajouté** | tests positifs, négatifs et de contournement des six blockers + HR-1…11 |
| 3 | `edlab/substrates/lattice_bond/future_route_e_pre_run_frame.py` | modifié | corrections HR-1…HR-11 sur le travail anticipatoire A–F |
| 4 | `tests/test_future_route_e_pre_run_blocker_closure_00.py` | modifié | mise en cohérence des tests A–F avec la portée restituée |
| 5 | `docs/individuation/FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_REPORT.md` | modifié | ce rapport |
| 6 | `docs/individuation/FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_DECISION.json` | modifié | décision |

**Non modifiés** : `engine.py`, `specs.py`, `state.py`, `instrumentation.py`,
`lifecycle.py`, `future_lifecycle_runner.py`, `future_lifecycle_owned_pipeline.py`,
`future_prospective_measurement_bridge.py`, tout `__init__.py`, `pyproject.toml`, tout
test existant, tout document 01S, et **le record humain `bc2a42c4`**. Aucun fichier ni
champ `00R` n'est créé.

---

## 2. Matrice du mandat actuel — `PRB-1 … PRB-6`

| PRB littéral | Sous-obligations littérales | État initial | Implémentation | Test | Preuve de fermeture |
|---|---|---|---|---|---|
| **PRB-1** *persist the track-component join* | écrire `(frame, canonical cell-set digest, track_id)` dans une évidence liée à la racine | ouvert | `JoinRecord`, `canonical_cell_set_digest`, `build_track_component_join`, `join_digest`, replié dans `route_e_root` | `test_prb1_01…09` | digest canonique lié à la forme, ordre-indépendant ; support manquant refusé ; join vide refusé ; changer le join change la racine |
| **PRB-2** *mandatory receipt* | l'entrée scientifique supportée refuse sans receipt vérifié | ouvert | `RouteEReceipt` exigé par `open_route_e_analysis` **et** par `route_e_entry` | `test_prb2_01…03`, `test_prb5_04` | absence → `ReceiptMissing` ; receipt liant une autre racine → `ReceiptInvalid` ; receipt incohérent avec son commitment → refus à la construction |
| **PRB-3** *frozen check order* | épingler par test : `local evidence → root digest → verifier` | ouvert | `CHECK_ORDER` + `_OrderTrace` dans `open_route_e_analysis` | `test_prb3_01…06` | échec à l'étape *n* lève **avant** l'étape *n+1* ; trace observée `["LOCAL_EVIDENCE"]`, puis `[…,"ROOT_DIGEST"]`, puis `[…,"VERIFIER"]` ; réordonner lève `CheckOrderViolation` |
| **PRB-4** *replay binding* | lier identité du run et enrôlement de famille dans la racine | ouvert | `FamilyEnrolment` (identité + seed root + digest du plan + comptes) → `enrolment_digest` → `route_e_root` | `test_prb4_01…04` | évidence bit-identique + identité différente ⇒ **racine différente** |
| **PRB-5** *single supported entry point* | fermer ou déclarer hors protocole les **cinq** entrées, avec test de refus | ouvert (1/5) | `route_e_entry` garde les cinq entrées littérales | `test_prb5_01…09`, paramétrés **par entrée** | 5 × 5 refus paramétrés, chacun sous `ForbiddenEffects` ; aucune dispatch vers une fonction acceptée (spies : 0 appel) |
| **PRB-6** *external anchoring* | commitment public immuable ou append-only, vérifiable sans secret | ouvert | `PublicCommitment` + `verify_public_commitment`, fail-closed, avec la précondition d'antériorité stricte | `test_prb6_01…07` | absence, mauvaise racine, absence de vérificateur, vérificateur non-`True`, vérificateur qui lève, antériorité non stricte : **tous refusés** — **mais le vérificateur n'est pas livré : BLOCKER OUVERT** |

### 2.1 `PRB-6` — pourquoi il reste ouvert, honnêtement

La fermeture exige un **vérificateur cryptographique maintenu** (BLS sur G1, RFC 9380,
compatible quicknet). Aucun n'est disponible : l'ajouter modifierait `pyproject.toml`,
hors allowlist gelée, et le firewall interdit tout accès réseau et tout téléchargement du
beacon. **Aucune BLS artisanale n'a été écrite**, conformément au mandat.

Ce qui **est** livré : le gate complet, fail-closed, qui refuse en l'absence de
vérificateur ; la précondition d'antériorité publique stricte ; et le parsing strict du
round. Ce qui **n'est pas** livré : le vérificateur. `blocker_status()["PRB-6"]["closed"]`
vaut `False` et le dit.

**Conséquence en cascade, déclarée :** l'anti-reroll de HR-3 dépend de `PRB-6`. Tant que
`PRB-6` est ouvert, **la garantie anti-reroll est déclarée NON PROUVÉE**, dans le code
(`ANTI_REROLL`) et ici.

---

## 3. Matrice du travail anticipatoire A–F

| A–F | Élément conservé | Correction HR nécessaire | Contribution éventuelle à PRB-1…6 | Ce que cela ne ferme / ne prouve pas |
|---|---|---|---|---|
| **A** seuils | frontières `25/67` et `ψ₀ = 1/4`, `ψ₁ = 1/8`, régions `d ≥ 25` / `d ≤ 2` / `3…24`, CP exactes | **HR-1** (censure disjointe), **HR-2** (observé vs inconnu) | aucune | ne ferme aucun `PRE_RUN_BLOCKER` ; ne chiffre rien d'observé |
| **B** générateur | SHA-256 compteur FIPS 180-4, domaines, ordre canonique, rejets consommés | **HR-3** (ancrage public), **HR-4** (BLS), **HR-5** (WAIT/STOP), **HR-6** (grille), **HR-7** (preuve) | **dépend** de `PRB-6` ; ne le ferme pas | ne prouve pas l'anti-reroll tant que `PRB-6` est ouvert |
| **C** validateur | `in_proposal_box ∧ LatticeBondSpec(**fields)`, 40 000 + 48 points | portée bornée au validateur inspecté | aucune | un accord fini n'est pas une équivalence universelle |
| **D** rupture d'association | cause `ASSOCIATION_GATE_TRACK_BREAK` et sa condition discriminante | **HR-10** (intégration + ambiguïté fail-closed) | aucune | n'est pas branchée dans le pont ni le pipeline acceptés, qui sont immuables |
| **E** `Δ` et plafond | onze axes, binding monotone `f` | **HR-8** (axes manquants), **HR-9** (plafond réel) | aucune | un blacklist lexical ne garantit aucune sémantique |
| **F** entrée publique | refus réel de `run_owned_future_pipeline` | absorbée par `PRB-5`, étendue aux cinq entrées | **sous-obligation B15 de `PRB-5`** | à elle seule ne fermait pas `PRB-5` |

---

## 4. Résolution individuelle de `HR-1 … HR-11`

| ID | Correction appliquée | Preuve |
|---|---|---|
| **HR-1** | La censure est redéfinie comme la disposition **`OBSERVED_FAILURE_HORIZON_WITHOUT_REPLACEMENT`** — état terminal `RIGHT_CENSORED_AT_HORIZON` avec `cohort_residual > f` — **disjointe** des quatre autres échecs observés, de l'inéligibilité mécanique et de l'inconnu technique. `DISPOSITION_TABLE` l'énonce ligne par ligne. | `test_hr1_01…03` : une seule disposition alimente le seuil |
| **HR-2** | `DrawDisposition` distingue **observé** / **inéligible** / **inconnu**. `draw_score(TECHNICALLY_UNKNOWN)` vaut **`None`**, jamais `0`. `robust_verdict` : `POSITIF` ssi `S ≥ 42`, `NÉGATIF` ssi `S + C ≤ 9`, sinon `TECHNICAL_FAIL` s'il reste des inconnus, sinon `INDÉTERMINÉ`. À `C = 0` il **coïncide exactement** avec la règle gelée. | `test_hr2_01…06`, dont les 68 valeurs de `S` à `C = 0` |
| **HR-3** | Le round est désormais désigné par le **timestamp PUBLIC du commitment externe**, jamais par un commit local. `ANTI_REROLL` est réécrit : la propriété est **conditionnelle**, la condition est `PRB-6`, et elle est déclarée **UNPROVEN** tant que `PRB-6` est ouvert. `verify_public_commitment(..., must_precede_unix=T)` refuse tout commitment publié à ou après `T`. | `test_hr3_01…03`, `test_prb6_06` |
| **HR-4** | `consume_beacon_round` **exige** un vérificateur BLS : `None` ⇒ `STOP` (« an HTTP response is not evidence »), non-`True` ⇒ `STOP`, exception ⇒ `STOP`, `randomness ≠ sha256(signature)` ⇒ `STOP`. Aucun vérificateur n'est empaqueté (LK-L2). | `test_hr4_01…07` |
| **HR-5** | Round indisponible ⇒ **`BeaconUnavailable` (WAIT)**, avec « never the next round, never an alternative endpoint, never another source ». Chaîne, round, encodage ou signature invalides ⇒ **`BeaconInvalid` (STOP)**. | `test_hr5_01…02` (8 réponses malformées) |
| **HR-6** | Le tirage entier passe par **`draw_index_below`**, rejet exact sur `limit = (2⁶⁴ // n)·n` : **biais modulo supprimé**. `UNIFORMITY_STATEMENT` distingue les **quatre** claims — continue idéale, grille réalisée, uniforme exacte sur la grille, borne d'approximation — et énonce « NO LITERAL EQUALITY WITH LEBESGUE MEASURE IS CLAIMED », avec les pas réels `6,0e-19` (affinité) et `3,3e-21` (taux). | `test_hr6_01…06` |
| **HR-7** | `REJECTION_PROOF` donne la preuve analytique complète : `P(retour = a) = Σ q^(m-1)/|B| = 1/|A|`, indépendante de `a`, terminaison presque sûre, espérance `|B|/|A|`. Les tests statistiques sont explicitement des **diagnostics**. | `test_hr7_01` |
| **HR-8** | `DELTA_DEFINITION` gagne `numerator`, `denominator` (**exactement 67**, jamais réduit), `invalid_cases` (⇒ `TECHNICALLY_UNKNOWN`, jamais `0`), `relation_to_censoring`, `relation_to_mechanical_ineligibility`, `no_retroactive_effect`. | `test_hr8_01…03` |
| **HR-9** | Le blacklist est **rétrogradé** en `lexical_ceiling_screen`, documenté comme « LIMITED SOFTWARE AID … not, and cannot be, a semantic guarantee ». Le plafond **exécutoire** est `RouteEClaim` : vocabulaire fermé (`Estimand`, `ClaimScope`, `ClaimVerdict`), rendu **uniquement** par gabarits autorisés, texte libre refusé. Les **six contournements** recensés échouent désormais, plus six paraphrases adversariales. | `test_hr9_01…06` (12 phrases) |
| **HR-10** | `assemble_draw_outcome` **est** le chemin de production Route E d'un tirage et **appelle toujours** `classify_track_terminations` (prouvé par substitution). Motif ambigu ⇒ **`AmbiguousTermination`**, jamais une supposition. | `test_hr10_01…08` |
| **HR-11** | Le titre et la portée du §8 sont restitués — dans ce rapport §1.1, dans le docstring du module A–F, et dans celui du fichier de tests A–F. | `test_prb_f_08` |

---

## 5. Preuves mécaniques

| Fait | Mesure |
|---|---|
| Ordre de checks `PRB-3` | trace observée exactement `LOCAL_EVIDENCE → ROOT_DIGEST → VERIFIER` ; échec à l'étape *n* ⇒ étape *n+1* jamais atteinte |
| Refus par entrée `PRB-5` | **5 entrées × 5 scénarios = 25 refus**, chacun exécuté sous `ForbiddenEffects` (entropie, réseau, sous-processus, `open`, `write_bytes`, `write_text`, `mkdir`, `engine.step` tous armés pour lever) |
| Non-dispatch `PRB-5` | les cinq fonctions acceptées remplacées par des spies : **0 appel** |
| Replay `PRB-4` | racine différente sous une identité différente, à évidence identique |
| Join `PRB-1` | digest canonique invariant par ordre et doublons, sensible à la forme du lattice ; support manquant refusé |
| Ancrage `PRB-6` | 6 familles de refus, dont l'antériorité stricte |
| Biais modulo | `limit % 3 == 0` et `2⁶⁴ − limit == 2⁶⁴ mod 3` : **le biais est supprimé, pas borné** |
| Pas de grille | `6,01e-19` (affinité), `3,34e-21` (taux) — mesurés, pas déclarés |
| Réseau | recherche statique : ni `requests`, ni `urllib`, ni `httpx`, ni `http.client`, ni `socket.` dans les deux modules ; et `socket.socket` armé pour échouer pendant `consume_beacon_round` |
| A–F conservés | 40 000 propositions accept-path ↔ moteur **0 divergence**, 48 points `nextafter` **0 divergence**, accord algébrique **40 000/40 000** |

---

## 6. Tests réellement exécutés

| Groupe | Collectés | Résultat |
|---|---|---|
| 1. `tests/test_future_route_e_pre_run_locks_00.py` (PRB-1…6 + HR) | **156** | 156 passed |
| 2. `tests/test_future_route_e_pre_run_blocker_closure_00.py` (A–F) | **104** | 104 passed |
| 3. Non-régression (suite entière moins les deux) | **673** | 673 passed |
| 4. Suite totale | **933** | **933 passed** |

`156 + 104 + 673 = 933` : groupes **disjoints**, aucun double comptage. **0 failed,
0 skipped, 0 xfail, 0 xpass, 0 deselected, 0 erreur de collection.** Python **3.11.15**,
pytest **8.4.2**, numpy **2.4.4**. Deux exécutions successives des 260 tests de cette
mission donnent le même résultat : **déterministes**.

**Vérification statique et instrumentée** que rien de scientifique n'a été matérialisé :
aucun attribut `SEED`, `SCIENTIFIC_SEED`, `SEED_ROOT`, `BEACON_ROUND`, `FAMILY`,
`NAMESPACE`, `LAW_SPEC`, `WORLD` dans l'un ou l'autre module ; aucun appel à
`designated_round` avant sa définition ; aucun `engine.step` dans les 260 tests de cette
mission ; répertoire temporaire **vide** après refus.

---

## 7. Limitations

**Verrous (`future_route_e_pre_run_locks.py`)** — `LK-L1` : les sources acceptées étant
immuables, chaque verrou est en amont d'elles ; un appelant qui contourne le chemin Route
E est refusé par le premier contrôle de la fonction acceptée, propriété plus faible,
testée et bornée à part. `LK-L2` : aucun vérificateur BLS ou de commitment n'est
empaqueté — `PRB-6` reste ouvert. `LK-L3` : la racine Route E **lie** la racine de mesure
du pont, elle ne la remplace pas.

**Cadre A–F (`future_route_e_pre_run_frame.py`)** — `RE-L1` discriminateur
sous-dimensionné à `n = 67` (demi-largeur `0,124721` contre `0,0625`) ; `RE-L2` les cinq
entrées acceptées n'ont pas de paramètre d'autorisation ; `RE-L3` écart d'un ulp
concevable, jamais utilisé comme gate ; `RE-L4` étiquette de cause, pas un sixième état
terminal ; `RE-L5` règle d'attribution, pas une coupure de décision ; `RE-L6` aucun accès
réseau, aucun round sélectionné, aucun vérificateur empaqueté ; `RE-L7` A–F sont des
obligations de prérégistration et ne ferment pas `PRB-1…6` ; `RE-L8` les lois uniformes
sont exactes **sur une grille finie**, pas sur un continuum ; `RE-L9` le screen lexical
est une aide limitée, jamais une garantie sémantique.

**Résidus par blocker** : `PRB-5` — les fonctions acceptées restent atteignables hors du
chemin Route E ; `PRB-6` — **ouvert**, vérificateur non livré.

**Résidu de montage, redivulgué** : le montage est en création seule (`rm` renvoie
`EPERM`) ; subsistent `.opr00_probe_delete_me` et des `.git/objects/*/tmp_obj_*`, sans
effet sur aucun arbre ni objet référencé.

---

## 8. Ce qui reste scientifiquement inconnu

**Tout.** Aucune valeur de `Δ(f)`, aucune de `ψ`, aucune fraction de censure, aucune
fraction d'inéligibilité, aucune répartition sur les cinq états terminaux, aucun monde
Route E, aucune loi tirée, aucune condition initiale tirée, aucun seed scientifique,
aucun round de beacon consulté, aucun namespace, aucune famille.

Route E reste **un protocole sélectionné, non confirmé**. Le seul résultat publié du
programme demeure le premier article (`https://doi.org/10.5281/zenodo.21403458`), qui
n'établit **ni ownership local, ni autonomie, ni individualité complète, ni
reconstruction, ni reproduction, ni hérédité**.

Aucune donnée Stage B, `M_MINUS`, trajectoire, shard, candidat ou résultat historique n'a
été ouverte. Aucun calibrage à partir de données. Route G n'a pas été rouverte. Route F
n'est pas un backup automatique.

---

## 9. Arrêt et prochaine étape

> ### `scientific_run_authorized = false`

Aucune prérégistration n'est commencée. `ROUTE_E_REPLICATION_DENSITY_PREREGISTRATION_00`
n'est pas autorisée : le record accepté la conditionne à « fermeture **et** revue humaine
des blockers », et `PRB-6` n'est pas fermé.

**Seule étape suivante autorisée : une nouvelle revue humaine indépendante du candidat
révisé.** Ce rapport ne prononce aucune acceptation.

---

## 10. Firewall et remote

Chemins Git exacts et `diff-tree` borné au couple parent–candidat. `GIT_INDEX_FILE`
explicitement neutralisé avant chaque vérification ; les index temporaires vivent sous
`/tmp` et ne touchent jamais l'index du dépôt. Aucun `git add`, aucun `git add -A`, aucun
checkout, aucun stash, aucun `git gc`, aucun nettoyage de fichier utilisateur. `main`
immobile à `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77`, `.git/index` réel intact, working
tree sale préservé à 23 entrées. Les branches `…-00` et `…-00-human-review` sont
préservées et non déplacées ; le record `bc2a42c4` n'est pas modifié.

**Remote.** Une tentative de push **normale**, unique, de la seule branche de révision.
Aucun `--force`, aucun push de `main`, aucun changement de credentials, aucun retry.
