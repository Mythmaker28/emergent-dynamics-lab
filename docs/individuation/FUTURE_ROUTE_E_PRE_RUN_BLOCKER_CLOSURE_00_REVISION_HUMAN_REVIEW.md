# HUMAN REVIEW — FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00 (révision `a379efa6`)

> ## Disposition : `HUMAN_REVIEW_REVISE`
>
> **Candidat audité :** `a379efa6e230efd6b4051b36717169be9c0f5dbf`
> **Parent unique :** `bc2a42c468eec5a4e1732ebb08c7cc20c4dab7dd`
> **Disposition candidate refusée en l'état :** `ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_MANDATE_ADDRESSED_PRB6_OPEN`
>
> Deux motifs indépendants, chacun suffisant :
>
> 1. **`PRB-6` est OUVERT** — le candidat le reconnaît. Aucun vérificateur BLS/G1 maintenu
>    n'est livré. Un gate fail-closed n'est pas un vérificateur.
> 2. **`PRB-5` n'est PAS fermé**, contrairement à ce que le candidat déclare. Les 25 refus
>    paramétrés portent sur `route_e_entry`, une fonction qui ne référence les cinq entrées
>    acceptées **que sous forme de chaînes de caractères**. Preuve par mutation ci-dessous :
>    les 33 tests `PRB-5` passent **inchangés** contre un stub qui ne fait rien.
>
> Et un défaut matériel de preuve : **les nombres de tests annoncés pour la non-régression
> et pour la « suite totale » ne sont pas ceux du dépôt au commit candidat.**
>
> **`scientific_run_authorized = false`**

---

## 0. Les quatre catégories, tenues séparées

1. **Preuves mécaniques** — reproduites ici indépendamment, en clean-room, avant lecture du
   rapport candidat pour ce qui relève du mandat.
2. **Décisions de gouvernance** — auditées ; deux refusées (disposition, fermeture de PRB-5).
3. **Limitations** — celles déclarées par le candidat, plus celles qu'il ne déclare pas.
4. **Résultats scientifiques** — **catégorie vide. Aucun n'existe, aucun n'a été produit,
   aucun n'a été utilisé.**

**Méthode.** Les textes gelés `00afcdd1…` (mandat, notamment le titre et le §8) et
`bc2a42c4…` (HR-1…HR-11) ont été lus **intégralement et en premier**, la matrice
exigences → mécanismes → tests → preuves a été construite ensuite, et le candidat n'a été
inspecté qu'après. Les tests du candidat ont été traités comme des **objets à auditer**,
non comme des preuves auto-authentifiantes : d'où l'expérience de mutation du §4.5.

---

## 1. Git, lignée et change set — **PASS**

`GIT_INDEX_FILE` explicitement neutralisé (`GIT_INDEX_FILE=[]`) avant chaque vérification ;
les deux index de preuve vivent sous `/tmp` et sont jetés. Aucun checkout, aucun stash,
aucun amend, rebase, merge, cherry-pick, `git add -A`, `git gc`, aucun nettoyage.

### 1.1 Chaîne exacte

| Commit | Parents (`rev-list --parents -n1`) | Lignes `^parent` |
|---|---|---|
| `00afcdd1aacbdf32bb030d85ced735a2920421f6` | `63c371d52036c7e91ec928118c2b8901776d79d0` | **1** |
| `c6d4acf037d4e51d59e5b75dc91b977b9eb83dbd` | `00afcdd1…` | **1** |
| `bc2a42c468eec5a4e1732ebb08c7cc20c4dab7dd` | `c6d4acf0…` | **1** |
| `a379efa6e230efd6b4051b36717169be9c0f5dbf` | `bc2a42c4…` | **1** |

`00afcdd1 → c6d4acf → bc2a42c → a379efa6` : chaîne strictement linéaire, **aucun merge**,
`a379efa6` a bien `bc2a42c4` pour **parent unique**. Arbre candidat
`31bba83a537d9015f0bff713c383c91510bcedf8`, arbre parent
`5a644ec5d5c05d633e8d0c55f7765d9549be9b79`.

### 1.2 Change set complet — exactement six chemins, `2 A / 4 M / 0 D`

| Chemin exact | Statut | Mode | Octets parent → candidat | sha256 du contenu candidat |
|---|---|---|---|---|
| `docs/individuation/FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_DECISION.json` | `M` | `100644` | 18 955 → 23 170 | `8eaba3a2e54defea53324d9c2a60d15f1fa66cb7e53284474470be2ab594af15` |
| `docs/individuation/FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_REPORT.md` | `M` | `100644` | 43 875 → 19 487 | `61b43576ead8ac044babc201a25b954359b03f4e526a1785ecb58577c5e08b97` |
| `edlab/substrates/lattice_bond/future_route_e_pre_run_frame.py` | `M` | `100644` | 48 289 → 77 829 | `3e08ddc7be429f1e5d4a1e0c689bd8477a20e9750d90f7f76904b52e41e4785d` |
| `edlab/substrates/lattice_bond/future_route_e_pre_run_locks.py` | **`A`** | `100644` | — → 26 884 | `2fa5538dc255e25a3a5afb51f174516fba9f267368e7efe791b958ef4a387492` |
| `tests/test_future_route_e_pre_run_blocker_closure_00.py` | `M` | `100644` | 34 823 → 35 422 | `df484559a36828d7874bdf09d386c6f65c1916a3d62f41b558d436b332112da5` |
| `tests/test_future_route_e_pre_run_locks_00.py` | **`A`** | `100644` | — → 45 706 | `7b6335141192350af92c43391865b75f44af3b2b255f48529207363f3f470b69` |

`numstat` : `370/280`, `173/595`, `684/36`, `666/0`, `14/5`, `1215/0`. **Aucune suppression,
aucun changement hors allowlist**, aucune source acceptée touchée (moteur, `specs`, `state`,
`instrumentation`, `lifecycle`, runner, pipeline possédé, pont de mesure, `__init__`,
`pyproject.toml`, tests préexistants, documents 01S, record `bc2a42c4`).

### 1.3 Preuve bidirectionnelle et constructive

- **Sens inverse.** Index temporaire initialisé sur l'arbre du candidat ; les quatre chemins
  modifiés remis à leurs blobs parents par `--cacheinfo`, les deux ajoutés retirés par
  `--force-remove`. `write-tree` produit `5a644ec5d5c05d633e8d0c55f7765d9549be9b79`, qui
  **est** `bc2a42c4^{tree}`. **MATCH EXACT.**
- **Sens direct.** Index initialisé sur l'arbre du parent ; les six changements appliqués.
  `write-tree` produit `31bba83a537d9015f0bff713c383c91510bcedf8`, qui **est**
  `a379efa6^{tree}`. **MATCH EXACT.**

Les deux sens ensemble prouvent que ces six chemins expliquent **entièrement** la
différence, et qu'il n'existe **aucun** septième changement.

### 1.4 État du dépôt préservé

| Élément | Valeur constatée |
|---|---|
| `.git/HEAD` | `ref: refs/heads/main` |
| `refs/heads/main` | `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77` — **immobile** |
| Véritable `.git/index` | **135 281 octets**, mtime `2026-08-03 23:45` — identique à la revue `bc2a42c4`, **non touché** |
| `…-closure-00` | `c6d4acf0…` — non déplacée |
| `…-closure-00-human-review` | `bc2a42c4…` — non déplacée |
| `…-closure-00-revision` | `a379efa6…` |
| `…-axis-convention-and-frame-closure-01s-human-review` | `00afcdd1…` — non déplacée |
| Checkout sale | préservé ; ce record y ajoute **un** fichier (voir §12) |

### 1.5 Discipline d'identifiants — **PASS**

Aucun identifiant `00R`, aucune mission scientifique nouvelle, aucun renommage `A→1`.
Le suffixe `-revision` est un nom de branche Git, pas un identifiant scientifique, et le
candidat le déclare explicitement (`identifier_discipline`). Vérifié dans les deux modules
et les deux tests : les libellés `A`–`F` et `PRB-1`…`PRB-6` restent disjoints.

---

## 2. La disposition candidate — **REFUSÉE comme token**

Le champ n'est même pas nommé `disposition` : il s'appelle `candidate_disposition`, et il
porte la valeur

```text
ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_MANDATE_ADDRESSED_PRB6_OPEN
```

**Aucun schéma ne l'autorise.** Le champ `schema` du record vaut la chaîne libre
`"route-e-pre-run-blocker-closure/v2"` ; **aucun fichier de schéma correspondant n'existe
dans l'arbre**. Le seul schéma présent qui contraigne un champ littéralement nommé
`disposition` est `future-lifecycle-contract/v1`, où `qualification.disposition` vaut
`{"const": "QUALIFIED"}` — objet entièrement différent, sans rapport. La valeur est donc
une **chaîne libre non validée**.

Le candidat déclare le token « dérivé » (`disposition_literal_source`). **Cela ne suffit
pas** : un outcome token inventé, non prescrit par `00afcdd1…`, ni par le
`…_01S_DECISION.json`, ni par `bc2a42c4…`, ne devient pas canonique parce qu'il s'annonce
comme dérivé. Et `MANDATE_ADDRESSED` est **factuellement trop fort** au vu du §4.5.

**Exigence.** Remplacer le token composite par des champs factuels séparés, sans créer de
vocabulaire canonique nouveau — par exemple :

```text
PRB-1, PRB-3 (partiel), PRB-4 = CANDIDATE_CLOSED
PRB-2                        = STRUCTURAL_ONLY
PRB-5, PRB-6                 = OPEN
human_review                 = PENDING
```

**À la décharge du candidat**, il ne prétend nulle part avoir obtenu une acceptation
humaine : `candidate_disposition_status = "PROPOSED BY THE IMPLEMENTATION AGENT; NOT A
HUMAN ACCEPTANCE"`, `human_acceptance_declared_here = false`,
`human_review_accepted_emitted_here = false`, `next_action_authorised = "INDEPENDENT HUMAN
REVIEW OF THIS REVISED CANDIDATE"`. La transparence est réelle ; c'est la **forme** du
token qui est refusée, plus le fait qu'il agrège en un mot un état que les faits séparent.

---

## 3. Ce que la contrainte décisive impose

Le candidat reconnaît lui-même :

```text
PRB-6 = OPEN
ANTI_REROLL = UNPROVEN
```

Cette revue le confirme et en tire les conséquences, sans exception :

- `PRB-6` **n'est pas fermé** ;
- `HUMAN_REVIEW_ACCEPTED` **n'est pas prononcé** ;
- `ROUTE_E_REPLICATION_DENSITY_PREREGISTRATION_00` **n'est pas autorisée** ;
- **aucun run n'est autorisé.**

Aucun token littéral contraire n'a été découvert dans les textes gelés : `00afcdd1…` §8
conditionne la prérégistration à « fermeture **et** revue humaine des blockers », et
`bc2a42c4…` §12 le répète.

---

## 4. `PRB-1 … PRB-6`, jugés indépendamment

### 4.1 `PRB-1` — *persist the track-component join* — **PARTIEL**

*Ce qui tient, reproduit ici indépendamment du candidat :*

| Épreuve | Résultat reproduit |
|---|---|
| Indépendance à l'ordre : `join_digest([r1,r2]) == join_digest([r2,r1])` | **vrai** |
| Doublons **visibles** : `join_digest([r1]) != join_digest([r1,r1])` | **vrai** — un doublon n'est pas silencieusement absorbé |
| Join vide | **refusé** (`ValueError`) |
| Digest lié à la forme : `(16,16)` vs `(32,32)` sur les mêmes indices | **digests différents** |
| Cellules : ordre et doublons internes | **invariants** (tri + déduplication) |
| Support manquant pour une assignation | **`ValueError`**, jamais une ligne muette |
| Sérialisation | JSON canonique, `sort_keys`, séparateurs ASCII, `allow_nan=False`, hex de longueur fixe validé — **non ambiguë** |
| Liaison à `route_e_root` | le digest du join est l'un des trois slots ; permuter deux slots change la racine |

*Ce qui ne tient pas :*

- La fermeture littérale dit **« write** (frame, canonical cell-set digest, track_id) **into
  root-bound evidence »**. Le module `future_route_e_pre_run_locks.py` ne contient **aucune
  primitive de persistance** : ni `open`, ni `Path`, ni `write_bytes`, ni `write_text`
  (vérifié statiquement ; `os` et `math` y sont d'ailleurs importés sans être utilisés). Le
  join est **calculé et lié par digest, en mémoire** ; il n'est **jamais écrit**. La moitié
  « write into evidence » de l'obligation n'est pas livrée.
- **Complétude du support non contrôlée.** Un composant présent dans
  `components_by_frame` mais sans assignation est **silencieusement omis** du join
  (reproduit : 2 assignations, 2 lignes, un composant supplémentaire ignoré sans trace).
  Rien n'atteste que le join couvre l'ensemble des composants détectés d'une frame
  échantillonnée.
- Aucune source acceptée n'appelle `build_track_component_join`.

**Verdict : l'algèbre de digest est fermée ; l'obligation d'écriture ne l'est pas.**

### 4.2 `PRB-2` — *mandatory receipt* — **STRUCTUREL SEULEMENT**

Les trois couches exigées, séparées :

1. **Obligation structurelle — PASS.** `open_route_e_analysis` et `route_e_entry` exigent
   tous deux un receipt ; l'absence lève `ReceiptMissing` avant tout le reste ; un objet
   d'un autre type lève `ReceiptInvalid` ; `RouteEReceipt.__post_init__` refuse à la
   construction un receipt dont le commitment ne lie pas la même racine.
2. **Liaison à la racine — PASS.** Un receipt liant une autre racine lève `ReceiptInvalid`
   (reproduit).
3. **Authenticité cryptographique de la provenance — OUVERTE.** Reproduit ici en trois
   lignes : `route_e_root(...)` → `PublicCommitment(venue="anything", reference="anything",
   published_at_unix=1)` → `RouteEReceipt(...)` → `open_route_e_analysis(..., verifier=lambda
   c: True)` **atteint l'étape `VERIFIER` et la franchit**. La seule chose qui arrête
   l'appel est `scientific_run_authorized is False` — **pas** l'authenticité. Le vérificateur
   étant fourni par l'appelant, la vérité est fournie par l'appelant.

**Le passage n'est pas jugé par vacuité** : PRB-2 est évalué sur ses trois couches, et deux
passent réellement. Mais deux réserves matérielles subsistent, indépendantes de `PRB-6` :

- La fermeture gelée dit « **the supported scientific entry point** refuses without a
  verified receipt ». Les trois modules acceptés
  (`future_lifecycle_owned_pipeline`, `future_lifecycle_runner`, `lifecycle`) contiennent
  **zéro** occurrence de `receipt`, `RouteE` ou `route_e` (compté : `0`, `0`, `0`). Aucun
  point d'entrée supporté n'exige de receipt. Le receipt est exigé par **deux fonctions
  neuves qu'aucun chemin de production n'appelle**.
- `recomputed_root_sha256` est une **chaîne fournie par l'appelant**. Aucune fonction ne
  recompute la racine depuis une évidence relue. Le gate compare un receipt à une assertion,
  pas à une évidence.

### 4.3 `PRB-3` — *frozen check order* — **PARTIEL**

*Ce qui tient.* L'ordre `LOCAL_EVIDENCE → ROOT_DIGEST → VERIFIER` est réellement imposé par
le **flot de contrôle** de `open_route_e_analysis` : un échec à l'étape *n* lève avant
l'entrée de l'étape *n+1*, et les traces reproduites sont exactement `["LOCAL_EVIDENCE"]`,
`["LOCAL_EVIDENCE","ROOT_DIGEST"]`, puis `[…,"VERIFIER"]`. Le vérificateur n'est appelé
qu'en troisième position.

*Ce qui ne tient pas :*

- `_OrderTrace` **ne peut pas se déclencher depuis le chemin réel** : le corps de la
  fonction est du code en ligne droite, donc `order.enter` reçoit toujours la bonne étape.
  Le seul test qui le fait lever (`test_prb3_05`) **appelle la classe privée directement** :
  il teste le traceur, pas le gate. Le « pin par test » est donc, sur ce point, décoratif.
- **Contournement par l'autre chemin public.** `route_e_entry` — également public, également
  consommateur de receipt et de vérificateur — ne contient **ni** `_OrderTrace` **ni**
  l'étape `LOCAL_EVIDENCE` (vérifié sur la source), et applique un ordre différent
  (autorisation → receipt → vérificateur). L'ordre gelé n'est donc pas imposé à tous les
  chemins publics du module.
- `must_precede_unix` vaut **`None` par défaut** dans `open_route_e_analysis`, et
  `route_e_entry` **ne le transmet pas du tout** : le contrôle d'antériorité — la
  précondition anti-reroll de HR-3 — est **désactivé par défaut** et **absent** du second
  chemin.

### 4.4 `PRB-4` — *replay binding* — **CANDIDATE_CLOSED (au niveau digest)**

Reproduit indépendamment :

| Épreuve | Résultat |
|---|---|
| Évidence bit-identique, `run_identity` différente | **racine différente** |
| Mutation de `seed_root_sha256` | digest différent |
| Mutation de `draw_plan_digest` | digest différent |
| Mutation de `n_draws` | digest différent |
| Mutation de `worlds` | digest différent |
| Permutation des trois slots de `route_e_root` | **racine différente** |
| `FamilyEnrolment` fail-closed (types, longueurs, positivité, `bool` rejeté) | conforme |

Réserve : comme pour `PRB-1`, la racine est **calculée**, jamais **persistée ni ancrée** —
la liaison est vraie en algèbre, inerte en pratique tant que `PRB-6` est ouvert.

### 4.5 `PRB-5` — *single supported entry point* — **OUVERT** *(le candidat le déclare fermé)*

C'est le point décisif de cette revue.

**Fait 1 — le gate ne garde rien.** `future_route_e_pre_run_locks.py` n'importe **aucun**
des trois modules acceptés (ses seuls imports sont `hashlib`, `json`, `math`, `os`,
`dataclasses`, `enum`, `typing`, plus `TrackingResult` et, localement, le module de cadre).
Les cinq entrées n'y figurent que comme **chaînes de caractères** dans
`SUPPORTED_ENTRY_POINTS`. Il n'existe donc **aucun chemin de code** de `route_e_entry` vers
une fonction acceptée — et symétriquement **aucune obligation** d'appeler `route_e_entry`
avant elles.

**Fait 2 — les tests ne peuvent pas échouer.** `test_prb5_08` remplace les cinq callables
par des spies et affirme `reached == []`. Comme le gate ne les référence pas, l'assertion
est **vraie par construction**, quel que soit le comportement du gate.

**Preuve par mutation, exécutée ici.** `route_e_entry` a été remplacée, dans une copie
clean-room, par un **stub qui ne fait rien** d'autre que lever les exceptions attendues, sans
aucun rapport avec les cinq entrées :

```text
python3 -m pytest tests/test_future_route_e_pre_run_locks_00.py -q -k "prb5"
  →  33 passed, 123 deselected
```

**Les 33 tests `PRB-5`, dont les 25 refus paramétrés et les 5 tests de non-dispatch, passent
inchangés contre le stub.** Ils ne distinguent pas le mécanisme livré d'un stub : leur
contenu probant sur les cinq entrées acceptées est **nul**.

**Fait 3 — l'état réel n'a pas bougé.** Le seul test de refus portant sur une **vraie**
fonction acceptée reste celui hérité de `PRB-F` sur `run_owned_future_pipeline`, dans le
fichier A–F (dont le diff parent → candidat ne touche que le docstring et
`test_prb_f_08`). C'est exactement le « **1 sur 5** » que `bc2a42c4` §2.2 et §8 avait jugé
insuffisant : *« PRB-5 exige un test de refus pour cinq points d'entrée. Un seul en a un.
PRB-5 reste ouvert. »* **Rien dans cette révision ne change ce fait.**

**Note de justice.** La contrainte est réelle : les cinq fonctions n'ont pas de paramètre
d'autorisation et l'allowlist gelée interdit de les modifier. La voie « **declare out of
protocol** » que le texte gelé autorise est légitime — mais elle vient avec « **with a
refusal test: `open_owned_analysis_access`, `future_lifecycle_runner.open_analysis_access`,
`publish_future_family_completion`, `qualify_and_write_lifecycle_contract` (and, per B15,
`run_owned_future_pipeline`)** », c'est-à-dire un test de refus **sur ces fonctions-là**.
Quatre d'entre elles n'en ont toujours aucun.

**Ce qu'il faut, et c'est borné :** quatre tests de refus supplémentaires appelant les quatre
vraies fonctions publiques, chacune sous `ForbiddenEffects`, prouvant le refus avant
entropie, réseau, sous-processus, seed/famille/namespace, loi ou CI, moteur, lecture ou
écriture scientifique — exactement ce qui existe déjà pour `run_owned_future_pipeline`.
Et requalifier `route_e_entry` en **convention de protocole**, non en gate.

### 4.6 `PRB-6` — *external anchoring* — **OUVERT** *(correctement déclaré)*

Propriétés effectivement présentes, toutes reproduites :

| Propriété exigée | Constat |
|---|---|
| Gate fail-closed | **oui** — `verify_public_commitment` ne retourne que `None` ou lève |
| Vérificateur obligatoire | **oui** — aucun défaut, aucune inférence |
| Absence de vérificateur ⇒ STOP | **oui** — `CommitmentInvalid` ; côté beacon, `BeaconInvalid("STOP: no BLS verifier supplied…")` |
| Indisponibilité authentique ⇒ WAIT | **oui** — `BeaconUnavailable`, `disposition = "WAIT"`, « retry the SAME round; never the next round, never an alternative endpoint, never another source » |
| Chaîne / round / encodage / signature / randomness invalides ⇒ STOP | **oui** — chaîne épinglée, round strictement égal au round désigné, hex strict, `len(randomness)==32`, `len(signature)==48`, `sha256(signature)==randomness` |
| Verdict non `True`, vérificateur qui lève | **refus** dans les deux cas |
| Antériorité stricte du commitment public | **oui**, quand `must_precede_unix` est fourni (cf. §4.3) |
| Aucun contact avec drand | **oui** — aucun `requests`/`urllib`/`httpx`/`http.client`/`socket.` dans les deux modules ; `socket.socket` armé pour lever pendant les tests |
| Aucune BLS artisanale | **oui** — aucune arithmétique de courbe n'a été écrite |

Vérifications indépendantes du contexte cryptographique épinglé : `chain_hash` =
`52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971` (quicknet),
`scheme = bls-unchained-g1-rfc9380`, `period = 3 s`, `genesis = 1692803367`, clé publique
**192 caractères hex = 96 octets** (G2, conforme), signature attendue **48 octets** (G1,
conforme). Arithmétique du round recomputée indépendamment sur sept instants :
`r = 1 + ceil((T − genesis)/période)`, et `t(r) ≥ T > t(r−1)` vérifié à chaque fois ;
`designated_round(T) = beacon_round_at_or_after(T + 86400)` confirmé.

**Conclusion obligatoire, prononcée :**

```text
PRB-6 = OPEN
```

Aucun mock, callback ou stub ne constitue une preuve positive. **Défaut supplémentaire à
corriger lors de la fermeture** (cf. §9) : le **DST RFC 9380 exact n'est pas épinglé**, et
`consume_beacon_round` délègue au vérificateur anonyme **la construction du message et le
DST** — précisément l'endroit où `bls-unchained-on-g1` (fastnet, DST G2) et
`bls-unchained-g1-rfc9380` (quicknet, DST G1) diffèrent.

---

## 5. `HR-1 … HR-11`, jugés séparément

| ID | Verdict | Constat |
|---|---|---|
| **HR-1** | **PASS** | Les cinq états gelés sont nommés (`FROZEN_TERMINAL_STATES`) ; la censure devient la disposition unique `OBSERVED_FAILURE_HORIZON_WITHOUT_REPLACEMENT`, **disjointe** des quatre autres échecs observés, de `MECHANICALLY_INELIGIBLE` et de `TECHNICALLY_UNKNOWN`. Le défaut décisif du §3.2 de `bc2a42c4` est **réparé** : le seuil `C > 25` attribue désormais une cause au lieu de recouvrir tout nul. |
| **HR-2** | **PASS** | `draw_score(TECHNICALLY_UNKNOWN)` vaut `None`, jamais `0`. **Vérifié exhaustivement** ici sur les 2 346 couples `(S, U)` admissibles : **0 décision non fondée** — toute décision rendue vaut pour **toute** complétion des inconnus. À `U = 0` la règle coïncide exactement avec la règle gelée. *Réserve mineure, non porteuse :* dans **496** cas toutes les complétions donnent `INDÉTERMINÉ` et la fonction renvoie tout de même `TECHNICAL_FAIL` ; c'est un choix conservateur défendable, mais le docstring (« a decision is returned only when it holds for every completion ») ne le décrit pas exactement. |
| **HR-3** | **PASS sur la correction, propriété globale `UNPROVEN`** | Le round est désormais indexé sur le **timestamp public** du commitment externe, jamais sur un commit local ; `ANTI_REROLL` est réécrit en trois temps et déclare la garantie **UNPROVEN** tant que `PRB-6` est ouvert. C'est exactement ce qui était demandé. **Mais la propriété anti-reroll reste non établie**, et l'est doublement : par `PRB-6` ouvert, et parce que le contrôle d'antériorité est optionnel (§4.3). |
| **HR-4** | **PASS** | `consume_beacon_round` exige un vérificateur ; `None`, non-`True`, exception et `randomness ≠ sha256(signature)` sont quatre STOP distincts, tous reproduits. « An HTTP response is not evidence » est dans le message. Aucun vérificateur empaqueté (LK-L2, déclaré). |
| **HR-5** | **PASS** | Séparation stricte WAIT / STOP : `BeaconUnavailable.disposition = "WAIT"` pour l'indisponibilité seule ; `BeaconInvalid.disposition = "STOP"` pour tout le reste. La règle interdit explicitement round suivant, endpoint alternatif et autre source. |
| **HR-6** | **PASS** | Le biais modulo est **supprimé, pas borné** : `limit = (2⁶⁴ // 3)·3`, `limit % 3 == 0`, rejet de `2⁶⁴ − limit = 1 = 2⁶⁴ mod 3`, chaque résidu recevant exactement `6 148 914 691 236 517 205` blocs — recomputé ici. `floor(3·u)` a disparu du plan de tirage. Les quatre claims d'uniformité sont distingués et « NO LITERAL EQUALITY WITH LEBESGUE MEASURE IS CLAIMED » est écrit. Pas de grille recomputés : **6,012 09e-19** (affinité, contre 6,01e-19 annoncé) et **3,335 19e-21** (taux, contre 3,34e-21) — **conformes**. |
| **HR-7** | **PASS** | `REJECTION_PROOF` donne la preuve analytique complète et correcte (`Σ q^{m−1}/\|B\| = 1/\|A\|`, indépendance de `a`, terminaison presque sûre, espérance `\|B\|/\|A\|`), et les tests statistiques sont explicitement requalifiés en **diagnostics**. |
| **HR-8** | **PASS** | `DELTA_DEFINITION` gagne `numerator`, `denominator`, `invalid_cases`, `relation_to_censoring`, `relation_to_mechanical_ineligibility`, `no_retroactive_effect`. **Dénominateur toujours exactement 67, vérifié aux deux points d'application** : `robust_verdict` refuse tout `n ≠ 67` (testé sur 66, 68, 0, 1) et `RouteEClaim` lève `ClaimRefused` sur `n = 66`. |
| **HR-9** | **PASS** | `RouteEClaim` est **réellement fermé** : `Estimand` (6), `ClaimScope` (1), `ClaimVerdict` (6), champs entiers et flottants bornés, rendu **uniquement** par gabarit ; `render_claim` sur du texte libre lève `ClaimRefused`. Aucune racine interdite (`own`, `alive`, `life`, `autonom`, `individual`, `reconstruct`, `reproduc`, `hered`, `self-`) n'apparaît dans un rendu autorisé. Le blacklist est correctement **rétrogradé** en `lexical_ceiling_screen`, documenté comme aide limitée, et `RE-L9` le déclare. *Résidu déclaré et confirmé :* une paraphrase (« the blob keeps its identity through renewal ») passe encore le screen — c'est bien la limite annoncée, pas un défaut caché. |
| **HR-10** | **PARTIEL** | La branche fail-closed existe et fonctionne : deux états terminaux observés incompatibles ⇒ `AmbiguousTermination` (reproduit). **Mais « appelle toujours le classifieur réel » est inexact** : `assemble_draw_outcome` expose un paramètre `classifier=None` **substituable par l'appelant**, et un classifieur fourni qui renvoie `()` court-circuite entièrement `classify_track_terminations` (reproduit : disposition `SUCCESS`, `association_gate_breaks = 0`). Le seam de test est aussi un contournement. Par ailleurs `assemble_draw_outcome` n'est appelée par **aucune** source acceptée : appeler cette fonction « THE Route E production path » anticipe une production qui n'existe pas — ce que le rapport §3 admet ailleurs (« n'est pas branchée dans le pont ni le pipeline acceptés »), mais que le §4 contredit. |
| **HR-11** | **PASS** | Le titre du bloc — « **Obligations portées à la prérégistration** (`ROUTE_E_REPLICATION_DENSITY_PREREGISTRATION_00`), à n'exécuter qu'après fermeture **et** revue humaine des blockers » — est restitué **littéralement** dans le rapport §1.1, dans le docstring du module A–F, dans le docstring du fichier de tests A–F et dans `mandate_two_layers.section_8_title_literal`. La phrase de mandat de la mission est citée à côté. La portée est rétablie, et les deux couches ne sont plus confondues. |

**Un correctif local peut être `PASS` tout en laissant une propriété globale `UNPROVEN` :
c'est exactement le cas de HR-3.** La correction est bonne ; la propriété anti-reroll reste
non établie, et le restera jusqu'à la fermeture de `PRB-6`.

---

## 6. `A – F`, séparément

| | Verdict | Constat |
|---|---|---|
| **A** — seuils de censure et seconde CI | **PASS** | Frontières reproduites : `C = 24, 25 → NOT_SUFFICIENT`, `C = 26 → SUFFICIENT` ; `d ≤ 2 → NÉGLIGEABLE`, `d = 3, 24 → INDÉTERMINÉ`, `d ≥ 25 → MATÉRIEL`. Clopper-Pearson recomputé par une implémentation étrangère (queues binomiales exactes + bissection) : accord **à 0,0e+00** sur `(42,67)`, `(41,67)`, `(9,67)`, `(10,67)`, `(2,67)`, `(3,67)`, `(24,67)`, `(25,67)` — dont `CP inf(42,67) = 0,500104744020` et `CP sup(9,67) = 0,239741752063`, identiques aux valeurs acceptées en 01S. Le défaut décisif du §3.2 est réparé par HR-1, celui du §3.3 par HR-2. |
| **B** — générateur et beacon | **PASS comme anticipation ; anti-reroll `UNPROVEN`** | HR-3/4/5/6/7 appliqués (§5). Constantes gelées intactes. Ce qui manque n'est pas dans A–F : c'est `PRB-6`. |
| **C** — prédicat unique du moteur | **PASS (borné)** | Inchangé depuis `c6d4acf0` ; les 104 tests A–F passent intégralement ici. La borne énoncée en 01S et rappelée par `bc2a42c4` §5 tient : un accord fini n'est pas une équivalence universelle, et la portée est bornée au validateur inspecté. |
| **D** — rupture d'association | **PARTIEL** | La cause et sa condition discriminante restent correctes ; HR-10 ajoute la branche ambiguë. Mais l'« intégration » est dans une fonction anticipatoire que rien n'appelle, et le classifieur reste substituable (§5, HR-10). |
| **E** — `Δ` et plafond de claim | **PASS** | HR-8 et HR-9 appliqués et vérifiés (§5). |
| **F** — refus public | **PASS au sens étroit, inchangé** | Le test de refus réel sur `run_owned_future_pipeline` survit intact. Il ne ferme pas `PRB-5` (§4.5). |

---

## 7. Tests réellement exécutés — **la déclaration ne se reproduit pas**

Clean-room vérifié blob par blob contre le candidat (les six sha256 du §1.2 sont reproduits
localement à l'octet près). Environnement **identique à l'annonce** : Python **3.11.15**,
pytest **8.4.2**, numpy **2.4.4**. Aucun réseau, aucun contact drand, aucun moteur
scientifique, aucune lecture de donnée historique.

Commandes exactes et résultats :

```text
1. python3 -B -m pytest tests/test_future_route_e_pre_run_locks_00.py -q
   →  156 passed                                   [annoncé 156]   OK

2. python3 -B -m pytest tests/test_future_route_e_pre_run_blocker_closure_00.py -q
   →  104 passed                                   [annoncé 104]   OK

3. python3 -B -m pytest tests -q \
     --ignore=tests/test_future_route_e_pre_run_locks_00.py \
     --ignore=tests/test_future_route_e_pre_run_blocker_closure_00.py
   →  946 collected, 941 passed, 5 FAILED          [annoncé 673 passed, 0 failed]   ÉCART

4. python3 -B -m pytest tests -q
   →  1206 collected, 1201 passed, 5 FAILED        [annoncé 933 passed, 0 failed]   ÉCART

5. python3 -B -m pytest tests/test_future_route_e_pre_run_locks_00.py \
                        tests/test_future_route_e_pre_run_blocker_closure_00.py -q
   →  260 passed, identique à l'exécution précédente — déterminisme confirmé
```

`156 + 104 + 946 = 1206` : les groupes sont **réellement disjoints**, aucun double comptage.
Aucun `skip`, `xfail`, `xpass` ni `deselected` ; **0 erreur de collecte**.

### 7.1 D'où viennent 673 et 933 — cause identifiée, pas supposée

`673` n'est pas « la suite entière moins les deux fichiers ». C'est **exactement** la somme
des sept fichiers de tests de la lignée acceptée :

```text
test_future_lifecycle_contract.py                       52
test_future_lifecycle_runner_integration.py             87
test_empty_right_nonunit_cadence_tracker_repair.py      63
test_future_lifecycle_owned_pipeline.py                235
test_future_prospective_measurement_bridge.py          160
test_axis_transpose_equivariance_01s.py                 27
test_lattice_bond_instrumentation.py                    49
                                                    ------
                                                       673
```

Exécuté ici : ces sept fichiers donnent **673 passed** ; augmentés des deux fichiers de la
mission, **933 passed**. Les chiffres du candidat sont donc **réels, mais pour un
sous-ensemble**, et leurs **étiquettes sont fausses** : le répertoire `tests/` du dépôt au
commit candidat contient **38 fichiers** et **1 206 tests**, pas 933.

### 7.2 Les cinq échecs sont **préexistants** et **non imputables au candidat**

```text
tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[split]
tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[merge]
tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[tie]
tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[collapse]
    E   TypeError: track_components() missing 1 required keyword-only argument: 'sampled_frames'

tests/test_motile_polar.py::test_scramble_preserves_all_declared_invariants_and_destroys_organization
    E   AssertionError: support overlaps its own translate: displacement would not conserve mass
```

Les quatre premiers sont la signature `track_components(..., *, sampled_frames)` introduite
par la réparation du tracker ; le cinquième est une assertion de fixture. **Aucun des
fichiers en cause n'est touché par le change set** (§1.2) : ils sont bit-identiques chez
`bc2a42c4`, donc ces cinq rouges existaient déjà et **la révision ne les a pas créés**. Ils
étaient simplement **hors du sous-ensemble mesuré** depuis au moins 01S.

### 7.3 Ce que cela oblige

Ce n'est **pas** une fabrication : les 933 tests existent et passent. C'est un **défaut de
portée et d'étiquetage de la preuve mécanique**, qui se propage depuis 01S. À corriger :

- renommer le groupe 3 en ce qu'il est — *régression sur la lignée acceptée (sept fichiers)* —
  et le groupe 4 en *sous-ensemble de la lignée acceptée + mission*, ou bien mesurer
  réellement `tests/` ;
- déclarer les cinq rouges préexistants comme **dette héritée connue**, avec leur cause, au
  lieu d'écrire `failed: 0` sur un périmètre non nommé ;
- corriger `DECISION.json.tests` en conséquence (`total`, `non_regression_tests`, `failed`,
  et la phrase « `156 + 104 + 673 = 933` ; groupes disjoints »).

---

## 8. Limitations de **cette** revue

- Le clean-room reconstitue l'arbre du candidat **sans** `results/` (710 Mo de données
  historiques, délibérément non transportées : le firewall interdit d'ouvrir des données
  scientifiques) et sans les documents de `docs/individuation` autres que ceux atteints par
  chemin exact. Aucun test collecté ne dépend de `results/` — la collecte est complète
  (1 206) et les seules erreurs observées sont les cinq échecs analysés au §7.2 — mais
  l'absence de ce répertoire est une différence assumée avec l'arbre committé.
- La preuve de non-dispatch de `PRB-5` est **négative et bornée** : elle établit que les
  tests livrés n'ont aucun pouvoir discriminant, **pas** que `route_e_entry` serait nuisible.
- Aucun round drand n'a été consulté, aucun vérificateur BLS n'a été exécuté : les
  propriétés de `consume_beacon_round` sont vérifiées **contre des vérificateurs synthétiques
  fournis par le test**, ce qui est précisément la limite que `PRB-6` nomme.
- `main` a été relevée deux fois pendant la revue et n'a pas bougé ; le dépôt porte un
  heartbeat autonome, donc cette immobilité est un constat horodaté, pas une garantie.
- Les six sha256 du §1.2 sont recomputés depuis les objets Git **et** depuis l'arbre extrait ;
  ils concordent. Aucun autre chiffre du candidat n'est repris sans reproduction.

---

## 9. Recherche consultative `PRB-6` — sans rien modifier ni installer

Comparaison des quatre routes, sur sources primaires. Aucune allowlist n'a été étendue,
aucune dépendance installée, aucun identifiant de mission inventé.

**Socle normatif** (drand `crypto/schemes.go`) : `bls-unchained-g1-rfc9380` ⇒ signature sur
**G1**, clé sur **G2**, message `sha256(round en uint64 big-endian)`, DST
**`BLS_SIG_BLS12381G1_XMD:SHA-256_SSWU_RO_NUL_`**, `randomness = sha256(signature)`. **Piège
confirmé :** le schéma antérieur `bls-unchained-on-g1` (fastnet) signe aussi sur G1 mais avec
le **DST G2** — toute implémentation doit distinguer les deux. C'est exactement le point que
le candidat ne pin pas (§4.6).

| | Schéma G1/G2 | DST RFC 9380 | Contrôles sous-groupe / infini / canonicité | `randomness` | Maintenance, licence | Py 3.11 + Windows | Épinglage | Surface |
|---|---|---|---|---|---|---|---|---|
| **1. Helper Go hors réseau** (drand/drand v2 + `kyber-bls12381`) | natif, `Scheme.VerifyBeacon` | exact, lu dans `schemes.go` | `kilic/bls12-381` : `FromCompressed` fait courbe + sous-groupe + bit d'infini + canonicité (⚠ `FromBytes` non compressé **ne** teste **pas** le sous-groupe) | à la charge de l'appelant | v2.1.7 (juil. 2026), Apache-2.0 / MIT, **équipe drand** | sous-processus, pas de cgo ⇒ binaire statique, `GOOS=windows` trivial | `go.mod` / `go.sum` + checksum DB, `-trimpath` | frontière de **processus** |
| **2. `drand-client`** (npm) | oui, 5 schémas | correct | `@noble/curves` (JS pur) | **vérifie lui-même** `sha256(sig)==randomness` | v1.4.2 (mai 2025), Apache-2.0 / MIT | runtime **Node** à faire entrer dans l'allowlist | `package-lock.json`, `integrity sha512` | `verifyBeacon` **non exporté** ; `validatedBeacon()` a un chemin réseau |
| **3. Binding Python de `supranational/blst`** | cœur le plus solide (RFC 9380, min-pubkey **et** min-signature, DST arbitraire) ; **audit NCC Group 2021** | exact | **à la charge de l'appelant** (le README l'avertit) | non | v0.3.17 (juil. 2026), Apache-2.0 | binding classé « proof-of-concept » ; `run.me` **sans branche Windows/MSVC** ; **absent de PyPI** | vendoring d'un commit git, pas de hash PyPI | **FFI in-process** (C/asm + glue SWIG) ; assembler soi-même l'équation de couplage frôle l'interdit « BLS maison » |
| **4. `drand-verify`** (PyPI, wrapper PyO3 de `noislabs/drand-verify`) | `verify_quicknet()`, clé LOE en dur | identique à drand (`src/verify.rs`) | pile `zkcrypto/bls12_381` | **retourne la randomness** | 0.2.1 (sept. 2023), Apache-2.0, mainteneur individuel, **aucun audit**, amont ~21 étoiles | roues CPython 3.7–3.12, **Windows 32/64**, macOS, manylinux/musllinux | `pip install --require-hashes` opérationnel | FFI Rust |

**Recommandation classée.**

1. **Helper Go hors réseau — source de vérité.** C'est le code de vérification de drand
   lui-même, sans cgo, binaire statique Windows et Linux, épinglé par `go.sum`. Coût : une
   toolchain Go au build, une frontière de sous-processus, et `randomness = sha256(sig)` à
   ajouter côté appelant.
2. **`drand-verify` — oracle différentiel secondaire.** Pile cryptographique totalement
   indépendante (zkcrypto ≠ kilic), installation triviale avec hachages. **Jamais seul** :
   maintenance et provenance insuffisantes.
3. **`drand-client`** — troisième chemin utile (noble, même organisation que drand), mais
   runtime Node et API non exportée : à réserver à la génération de vecteurs en CI, hors
   runtime.
4. **Binding Python de blst** — dernier malgré le meilleur cœur : binding PoC, pas de
   Windows, pas de PyPI, contrôles laissés à l'appelant.

**Contrôle inter-implémentations, hors réseau.** Table de vecteurs figée en dépôt,
`(round, signature_hex, randomness_hex)` + clé quicknet ; exiger l'accord **bit à bit** sur
`(verdict, randomness)` entre deux implémentations au moins. Cas négatifs **obligatoires** :
round décalé de ±1 ; bit de poids fort de la signature altéré ; point hors sous-groupe ;
point à l'infini ; encodage non canonique (`x ≥ p`) ; **DST fastnet (G2) appliqué à un round
quicknet**. Un désaccord sur un seul de ces cas est un détecteur de bug.

**Autorité nécessaire.** Étendre l'allowlist gelée à *(i)* une dépendance de vérification
maintenue, *(ii)* son fichier de verrouillage avec hachages, *(iii)* un adaptateur, *(iv)*
ses tests et sa table de vecteurs, exige une **autorisation d'ingénierie étroite du
propriétaire**, sous l'identifiant `FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00` **inchangé**.
Cette revue **n'étend pas** l'allowlist et **n'invente aucun identifiant**.

**Non vérifiable depuis les sources primaires** : que `kyber-bls12381` appelle bien
`FromCompressed` (et non `FromBytes`) à la désérialisation ; les contrôles exacts de
`@noble/curves` et de `bls12_381::from_compressed` ; l'existence d'un jeu de vecteurs
officiel, signé et versionné par drand pour `bls-unchained-g1-rfc9380`.

---

## 10. Ce qui reste scientifiquement inconnu

**Tout.** Aucune valeur de `Δ(f)`, aucune de `ψ`, aucune fraction de censure observée,
aucune fraction d'inéligibilité mécanique observée, aucune répartition observée sur les cinq
états terminaux, aucun monde Route E, aucune loi tirée, aucune condition initiale tirée,
aucun seed scientifique, aucun round de beacon consulté, aucun namespace, aucune famille.

Route E demeure **un protocole sélectionné, non confirmé**. Le seul résultat publié du
programme reste le premier article (`https://doi.org/10.5281/zenodo.21403458`), qui établit
la persistance causale à travers le renouvellement matériel **sans** ownership local,
**sans** autonomie, **sans** individualité complète, **sans** reconstruction, **sans**
reproduction et **sans** hérédité.

Aucune donnée Stage B, `M_MINUS`, trajectoire, shard, candidat ou résultat historique n'a
été ouverte pendant cette revue. Aucune calibration à partir de données. Aucun seed ni round
scientifique. Aucune prérégistration commencée. Aucune autorisation d'exécution. Route G n'a
pas été rouverte.

---

## 11. Prochaine mission conditionnelle

Les sources **n'autorisent aucun identifiant nouveau**, et ce record n'en invente aucun.

- **`ROUTE_E_REPLICATION_DENSITY_PREREGISTRATION_00` n'est PAS autorisée.**
- La seule mission autorisée reste **`FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00`**, dont le
  mandat n'est **pas** consommé. La révision suivante doit, sous ce même identifiant :
  1. **fermer `PRB-5`** par quatre tests de refus supplémentaires portant sur les **vraies**
     fonctions `open_owned_analysis_access`,
     `future_lifecycle_runner.open_analysis_access`, `publish_future_family_completion` et
     `qualify_and_write_lifecycle_contract`, sur le modèle exact de celui qui existe déjà pour
     `run_owned_future_pipeline` ; et requalifier `route_e_entry` en convention, non en gate ;
  2. **corriger la disposition** en champs factuels séparés (§2) ;
  3. **corriger la preuve de tests** : périmètre nommé, cinq rouges préexistants déclarés,
     `DECISION.json.tests` mis en cohérence (§7.3) ;
  4. **compléter `PRB-1`** (écriture effective dans une évidence liée à la racine, ou
     déclaration explicite que seule l'algèbre de digest est livrée) et **`PRB-3`**
     (`route_e_entry` soumise au même ordre gelé ; antériorité non optionnelle) ;
  5. **corriger HR-10** : soit retirer le paramètre `classifier` du chemin de production,
     soit cesser d'écrire « appelle toujours le classifieur réel » ;
  6. ne rien rouvrir de 01S, ne consulter aucune donnée, ne choisir aucun seed ni round.
- **Puis**, et seulement pour `PRB-6` : demander au propriétaire une **autorisation
  d'ingénierie étroite** permettant la dépendance de vérification maintenue, son fichier de
  verrouillage, l'adaptateur et les tests (§9), fermer `PRB-6` sous le **même** identifiant,
  et refaire une revue indépendante.

Ce qui est **acquis et n'a pas à être refait** : la vérification Git complète et les deux
preuves d'arbre ; l'arithmétique Clopper-Pearson et les frontières de censure et de
discordance ; la suppression exacte du biais modulo et les bornes de résolution ; la preuve
analytique du rejet ; la fermeture du vocabulaire de `RouteEClaim` ; le dénominateur figé à
67 ; la solidité exhaustive de `robust_verdict` ; les 156 + 104 tests de la mission et leur
déterminisme ; la restitution du §8.

---

## 12. Firewall, résidus et remote

**Firewall tenu.** Chemins Git exacts et `diff-tree` borné au couple parent–candidat.
`GIT_INDEX_FILE` neutralisé explicitement ; les deux index de preuve sous `/tmp`, jetés.
Aucun `git add -A`, aucun checkout, stash, amend, rebase, merge, cherry-pick, `git gc`,
aucun nettoyage de fichier utilisateur. `docs/individuation` n'a **pas** été énuméré : seuls
des chemins exacts ont été ouverts. `results/` n'a **pas** été parcouru. Stage B, `M_MINUS`,
Kovacs, shards, mondes, trajectoires, checkpoints et données du premier article :
**non ouverts**.

**Ce qui a été exécuté :** les tests du dépôt en clean-room, une copie mutée jetable pour la
preuve du §4.5, et des calculs fermés (binomiaux exacts, arithmétique du round, comptage de
seaux sur `2⁶⁴`) ne consommant aucune donnée du dépôt.

**Résidu non supprimable, redivulgué.** Le montage de travail est en création seule (`rm`
renvoie `EPERM`) : subsistent, sans effet sur l'arbre committé ni sur aucun objet référencé,
la sonde `.opr00_probe_delete_me`, des `.git/objects/*/tmp_obj_*`, et **deux archives de
transport créées par cette revue** — `REVIEW_a379efa6_tree.tar.gz` et
`REVIEW_bc2a42c_parent.tar.gz` — produites par `git archive` pour constituer le clean-room.
Elles ne sont dans aucun arbre committé. Le checkout sale gagne donc trois entrées
supplémentaires, plus ce record.

**Candidat non modifié.** Aucun des six fichiers candidats n'a été touché ; aucun ancien
record n'a été modifié ; `bc2a42c4` est intact. **Un seul fichier est ajouté par ce
record** — celui-ci — sur une branche dont l'unique parent est `a379efa6`. Preuve inverse :
retirer ce record de l'arbre de la branche de revue redonne **exactement**
`31bba83a537d9015f0bff713c383c91510bcedf8`, l'arbre de `a379efa6`.

**Remote.** Une tentative de push **normale**, unique, de la seule branche de revue. Aucun
`--force`, aucun push de `main`, aucun changement de credentials, aucun retry automatique.
En cas d'échec, la référence locale est préservée intacte et la commande sûre est rapportée
pour exécution manuelle.

---

## 13. Disposition

> ## `HUMAN_REVIEW_REVISE`
>
> **`PRB-6` reste OUVERT** — aucun vérificateur BLS/G1 maintenu n'est livré ; un gate
> fail-closed, une interface de vérification ou un test qui ne discrimine rien ne le
> remplacent pas.
> **`PRB-5` n'est pas fermé** — les 25 refus paramétrés ne portent pas sur les cinq entrées
> acceptées, et passent à l'identique contre un stub.
> `PRB-1` est partiel (l'écriture dans l'évidence n'est pas livrée), `PRB-2` est structurel
> seulement, `PRB-3` est partiel (second chemin public hors ordre gelé), `PRB-4` tient au
> niveau digest.
> `HR-1`…`HR-9` et `HR-11` **passent** ; `HR-10` est partiel ; `HR-3` est appliquée mais la
> propriété anti-reroll reste **UNPROVEN**, conditionnée par `PRB-6`.
> La preuve de tests doit être corrigée : le périmètre annoncé n'est pas celui du dépôt, et
> cinq rouges préexistants ne sont pas déclarés.
>
> Il est **interdit** de résumer ce package par « les pre-run blockers sont fermés ».
>
> `ROUTE_E_REPLICATION_DENSITY_PREREGISTRATION_00` n'est pas autorisée.
> Prochaine mission, et seule autorisée : **`FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00`**,
> non consommée.
>
> ### `scientific_run_authorized = false`
