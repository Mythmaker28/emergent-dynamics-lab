# FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00 — rapport (autorisation A1-R, après `f152c3c`)

> **Aucun token composite n'est émis.** Les faits sont exposés champ par champ au §2 et,
> pour l'incrément A1-R, aux §19–§25. Ce record ne prononce **aucune acceptation humaine**.
>
> **Lecture.** Les §1–§13 décrivent l'incrément `c08e27c` ; les §14–§18 l'incrément A1
> (`f152c3c`) ; les **§19–§25** l'incrément **A1-R**, et le **§25 remplace le §18** comme
> déclaration finale courante.
>
> `PRB-6 = CANDIDATE_CLOSED` — vérificateur BLS/G1 maintenu livré, fixtures committées
> hors réseau (deux dépôts de l'organisation drand, un tiers), round dérivé et vérifié
> cryptographiquement.
> `PRB-5 = OPEN`. Le garde reste **écrit et testé** mais **non installé**.
>
> **A1-R s'arrête au §4, avant toute mutation matérielle.** L'audit des liaisons est
> reproduit exactement (`9 assertions · 13 sites · 10 hors allowlist · 4 records`, §20.2)
> puis **dépassé** : un **quatorzième** site, `test_rs01_12`, exécute une vraie collecte de
> nœuds contre `RUNNER_STACK_REQUALIFICATION_01`, dont `tests/test_future_lifecycle_runner_integration.py`
> est un **sélecteur** — ajouter un seul nom de test à ce fichier, comme le §7 le demande,
> exige de réécrire un record que le §2 déclare `PRESERVE_BYTE_IDENTICAL` (§20.3).
> Surtout, la précondition architecturale du §4 **échoue** : le signal Route E est
> **contournable**, et il existe **trois** entrées réelles hors allowlist —
> `future_prospective_measurement_bridge.run_measurement_bridge`, qui se déclare
> « the single supported measurement entry point » et fait tourner le moteur **avant**
> d'appeler `run_owned_future_pipeline` **sans** signal, plus `stage_b.py` et
> `stage_b_reproduce.py`, qui ne référencent **jamais** le lifecycle (§21).
>
> `ANTI_REROLL` : moitié « choix du round » **CANDIDATE_PASS**, moitié « publication »
> **UNPROVEN**. La décision A2 du propriétaire est **gelée et enregistrée**, non
> implémentée (§23).
>
> **`guard_signal_authoritative = false`** · **`accepted_entry_integration_present = false`**
> · **`historical_qualification_files_modified = 0`**
> · **`human_review = PENDING`** · **`scientific_run_authorized = false`**
>
> Il est **interdit** de résumer ce package par « les pre-run blockers sont fermés ».

---

## 1. Autorité, lignée, base

| Élément | Valeur |
|---|---|
| Mandat | `00afcdd1aacbdf32bb030d85ced735a2920421f6`, §8 |
| Première revue contraignante | `bc2a42c468eec5a4e1732ebb08c7cc20c4dab7dd` — `HUMAN_REVIEW_REVISE` |
| Revue indépendante contraignante | `31ccccfb9e61809cf5d461a70425e00c3db7bc17` — `HUMAN_REVIEW_REVISE` |
| Base exclusive de cette révision | `054140024267183fa43ef86755cd1c82d5a41483`, **parent unique**, aucun merge |
| Autorisation propriétaire | extension d'allowlist du §3, intégration **et** PRB-6 |
| Mission | `FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00`, **non consommée** |
| Branche Git | `codex/future-route-e-pre-run-blocker-closure-00-authorized-integration` — nom Git, pas un identifiant scientifique |

État de départ, non réécrit : `PRB-1 = PARTIAL` · `PRB-2 = STRUCTURAL_ONLY /
OPEN_GLOBALLY` · `PRB-3 = LOCAL_PASS / PARTIAL_GLOBALLY` · `PRB-4 =
CLOSED_AT_DIGEST_LEVEL_ONLY` · `PRB-5 = OPEN` · `PRB-6 = OPEN` · `HR-10/D = LOCAL_PASS /
PARTIAL_GLOBALLY` · `ANTI_REROLL = UNPROVEN` · `human_review = PENDING` ·
`scientific_run_authorized = false`.

---

## 2. Disposition — champs factuels séparés

| Blocker | Mécanisme | Intégration dans une source acceptée | Tests discriminants | Statut |
|---|---|---|---|---|
| **PRB-1** | présent, **avec persistance réelle** | **non** | oui (writer no-op ⇒ 6 rouges ; relecture retirée ⇒ 3 rouges) | mécanisme + persistance livrés |
| **PRB-2** | présent ; **authenticité désormais établie** | **non** (blocker §7) | oui | couches 1–5 livrées, **enforcement bloqué** |
| **PRB-3** | présent, chemin interne unique | **non** | oui (ordre modifié ⇒ 7 rouges ; cutoff optionnel ⇒ 5 rouges) | livré pour le chemin Route E |
| **PRB-4** | présent | **non** | oui | **niveau digest seulement** |
| **PRB-5** | **garde écrit et testé, NON installé** | **non** | oui (garde qui accepte un signal non typé ⇒ 4 rouges) | **OPEN** |
| **PRB-6** | **vérificateur maintenu livré** | s.o. | oui (appel du helper retiré ⇒ 12 rouges ; contrôle de randomness retiré ⇒ 1 rouge) | **CANDIDATE_CLOSED** |

`blocker_status()` ne renvoie **aucun** champ `closed` et porte `human_review_required =
True` pour les six. Aucun schéma fictif n'a été créé.

---

## 3. Allowlist effectivement utilisée

| Chemin | Statut | Autorisé par |
|---|---|---|
| `edlab/substrates/lattice_bond/future_route_e_pre_run_frame.py` | modifié | §3 handoff |
| `edlab/substrates/lattice_bond/future_route_e_pre_run_locks.py` | modifié | §3 handoff |
| `edlab/substrates/lattice_bond/route_e_beacon_verifier.py` | **ajouté** | §3 handoff |
| `tools/drand_verify/main.go` | **ajouté** | §3 handoff |
| `tools/drand_verify/go.mod` | **ajouté** | §3 handoff |
| `tools/drand_verify/go.sum` | **ajouté** | §3 handoff |
| `tests/data/route_e_beacon_vectors.json` | **ajouté** | §3 handoff |
| `tests/test_route_e_beacon_verifier.py` | **ajouté** | §3 handoff |
| `tests/test_future_route_e_pre_run_integration_00.py` | **ajouté** | §3 handoff |
| `tests/test_future_route_e_pre_run_locks_00.py` | modifié | §3 handoff |
| `docs/individuation/…_00_REPORT.md` | modifié | §3 handoff |
| `docs/individuation/…_00_DECISION.json` | modifié | §3 handoff |

**Autorisés mais volontairement NON modifiés** (voir §7) :
`future_lifecycle_owned_pipeline.py`, `future_lifecycle_runner.py`, `lifecycle.py`.
Ils sont **byte-identiques** à la base, vérifié par comparaison.

**`pyproject.toml` n'a pas été touché** et n'a pas eu besoin de l'être : le vérificateur
est un helper Go externe, pas une dépendance Python.

---

## 4. PRB-6 — vérificateur maintenu, hors réseau — **CANDIDATE_CLOSED**

### 4.1 Ce qui est livré

`tools/drand_verify` est un helper **Go, sans réseau**, construit sur
`github.com/drand/kyber-bls12381 v0.3.4` et `github.com/drand/kyber v1.3.1` (donc
`github.com/kilic/bls12-381 v0.1.0`). **Aucune BLS artisanale n'a été écrite** : aucune
arithmétique de courbe ne figure dans ce dépôt.

Propriétés **vérifiées dans le code source des bibliothèques, pas dans leur documentation** :

| Exigence | Constat, avec l'emplacement |
|---|---|
| Scheme exact | `crypto/schemes.go` : `const SigsOnG1ID = "bls-unchained-g1-rfc9380"` |
| DST RFC 9380 | `NewPedersenBLSUnchainedG1` : `BLS_SIG_BLS12381G1_XMD:SHA-256_SSWU_RO_NUL_` (G1) |
| Groupes | même fonction : `KeyGroup = Pairing.G2()`, `SigGroup = Pairing.G1()` |
| Message | `DigestFunc` : `sha256.New()` + `binary.Write(h, binary.BigEndian, round)` |
| `randomness` | `RandomnessFromSignature` : `sha256.Sum256(sig)` |
| Clé G2 96 o, signature G1 48 o | imposé par le helper et par `FromCompressed` |
| Désérialisation compressée canonique | `kilic/bls12-381 g1.go/g2.go FromCompressed` → `fromBytes` → `fe.isValid()` : *« must be less than modulus »* (rejet de `x ≥ p`) |
| Contrôle de sous-groupe | `g1.go` : `if !g.InCorrectSubgroup(p) { return nil, errors.New("point is not on correct subgroup") }` ; idem `g2.go` |
| Point à l'infini | `FromCompressed` **l'accepte** et renvoie `Zero()` — **le helper le rejette donc explicitement**, pour G1 et pour G2 |
| Encodage non canonique résiduel | le helper **re-sérialise** le point et exige l'égalité octet à octet avec l'entrée |

Interface : **un** objet JSON borné sur stdin (8 192 octets max), champs stricts,
`DisallowUnknownFields`, un seul objet accepté, argv fixe `["verify"]`, **aucun shell**,
environnement minimal (`PATH=""`, `LC_ALL=C`), timeout, stdout borné, stderr borné et
traité comme diagnostic, codes de sortie documentés (0 verdict, 2 configuration,
3 interne).

L'adaptateur `route_e_beacon_verifier.py` **épingle** la chaîne : `chain_hash`,
`public_key` (96 o), `scheme`, `DST`, période et genesis sont des constantes de module.
**Elles ne proviennent jamais du receipt ni de la réponse beacon** ; une réponse qui
annonce une autre chaîne est refusée. Il distingue exactement cinq issues :

```text
verified · invalid · unavailable · configuration_error · internal_error
```

et la traduction est fixe : **`unavailable` est le SEUL WAIT**, sur le **même** round ;
tout le reste est **STOP**. Un verdict « verified » qui ne réécho pas le scheme et le DST
épinglés est refusé comme `internal_error` — un helper qui se contenterait de dire
« verified » n'est pas cru.

### 4.2 Ce qui n'est pas livré, et le reste ouvert

- Le **binaire n'est pas committé**. Un vérificateur absent ou non exécutable est un
  **STOP**, jamais un passage. C'est testé dans les deux branches.
- La base de données de sommes de contrôle Go (`sum.golang.org`) est **inaccessible**
  depuis cet environnement : le build a utilisé `GOSUMDB=off`. Les modules sont **épinglés
  par version et par hash dans `go.sum`**, mais ces hashes n'ont **pas** été confrontés au
  journal de transparence. **À vérifier par un tiers disposant du réseau** (`go mod verify`
  + sumdb). C'est un résidu de provenance, déclaré, non masqué.
- Les chemins canoniques `golang.org/x/*` ne se résolvent pas ici ; `go.mod` porte deux
  `replace` **explicites** vers `github.com/golang/{sys,crypto}`, qui sont les mêmes dépôts
  amont, épinglés aux mêmes versions.

---

## 5. Vecteurs hors réseau et cas négatifs

**Aucun endpoint drand n'a été contacté. Aucun round live n'a été récupéré.**

**Formulation corrigée (A3).** Il n'existe **aucun jeu de vecteurs officiel signé et
versionné par drand** pour `bls-unchained-g1-rfc9380`. Les trois vecteurs employés sont
des **fixtures committées** dans des dépôts publics, dont **deux appartiennent à
l'organisation drand** (`drand/tlock`, `drand/drand-client`) et **un à un tiers**
(`noislabs/drand-verify`) — ce dernier ne doit **jamais** être présenté comme un jeu
officiel drand. Chaque fixture a été récupérée en https depuis
`raw.githubusercontent.com`, et `tests/data/route_e_beacon_vectors.json`
enregistre pour chacun : dépôt, ref, chemin, licence, sha256 du fichier source récupéré,
taille, chain hash, clé publique, scheme, round, signature, randomness, provenance de la
randomness, transformation (aucune) et résultat attendu.

| Id | Source | Chaîne | Round | Randomness |
|---|---|---|---|---|
| **V1** | `github.com/drand/tlock`, `tlock_test.go`, Apache-2.0 / MIT, sha256 `f2e71105…ef71` | **quicknet** | 12 040 883 | **dérivée** `sha256(sig)` |
| **V2** | `github.com/noislabs/drand-verify` — **tiers, PAS l'organisation drand** —, `src/verify.rs`, Apache-2.0, sha256 `47c7a755…f9a6` | **quicknet** | 123 | **dérivée** `sha256(sig)` |
| **V3** | `github.com/drand/drand-client`, `test/beacon-verification.test.ts`, Apache-2.0 / MIT, sha256 `e9b91a7a…c67d` | `walkthrough` (**pas** quicknet ; même scheme) | 38 | **COMMITTÉE** |

**V3 est le seul vecteur dont la randomness est committée** : il prouve
`randomness = sha256(signature)` contre un fichier officiel, et c'est vérifié
(`b2fc2132…9ccca` reproduit exactement). Pour V1 et V2 la randomness est **dérivée**, ce
que le fichier de vecteurs dit explicitement.

**Contrôle inter-implémentations.** Les trois vecteurs ont été revérifiés avec `py_ecc`,
une implémentation Python pure **sans rapport** avec `kilic`/`kyber` : accord complet.
Les contre-épreuves passent aussi : round 124 → invalide, clé `walkthrough` sur un round
quicknet → invalide, et **DST fastnet (G2) appliqué à un round quicknet → invalide**.
`py_ecc` a servi d'oracle d'audit uniquement ; ce n'est **pas** une dépendance du dépôt.

Cas négatifs exécutés contre le vrai binaire : round ±1 · mauvaise clé · signature altérée
· randomness incohérente · point à l'infini · encodage non canonique (`x ≥ p`) · longueur
incorrecte · scheme fastnet · champ JSON supplémentaire · deux objets JSON · JSON
malformé — plus, côté adaptateur, helper absent, helper qui plante, timeout, sortie
malformée, sortie sans `status`, statut inconnu, succès forgé sans écho épinglé, sortie
surdimensionnée. Le catalogue complet est dans le fichier de vecteurs et le test
`test_crypto_04` vérifie qu'il est complet.

---

## 6. Anti-reroll — la moitié qui passe et la moitié qui ne passe pas

**Ce qui passe.** Le round est **dérivé** du timestamp public gelé par
`designated_round(T) = beacon_round_at_or_after(T + 86400)`. Il n'est **argument nulle
part** : ni `RouteERequest`, ni `verify_public_commitment` n'ont de champ `round`,
`scheme`, `dst` ou `chain_hash`. Un round voisin, même cryptographiquement valide, est
refusé. Il n'existe **aucune boucle**, aucun retry, aucun endpoint alternatif :
l'adaptateur fait **exactement un** `subprocess.run` et un timeout est terminal. Une
indisponibilité renvoie **WAIT sur le même round**.

**Ce qui ne passe pas.** Que la racine ait été **réellement publiée**, immuablement, à
l'instant déclaré, reste **affirmé** par le `venue` et la `reference` du commitment, pas
vérifié. La vérification drand prouve le **round**, pas la publication. Fermer cette
moitié demande une preuve d'inclusion propre au registre choisi, qui n'est pas livrée.

```text
ANTI_REROLL_round_selection = CANDIDATE_PASS
ANTI_REROLL_publication     = UNPROVEN
```

---

## 7. PRB-5 — blocker précis, non contourné

Le garde **existe** : `RouteERequest` (signal **typé**, jamais une chaîne libre),
`enforce_route_e_guard(request, entry_point=…)`, qui exécute le chemin gelé complet —
`ENTRY_GUARD → LOCAL_EVIDENCE → ROOT_DIGEST → RECEIPT_ROOT_BINDING → VERIFIER` — avec la
vérification cryptographique réelle, et **ne peut jamais retourner**. Il est testé de bout
en bout, y compris avec le vrai binaire et le vrai vecteur.

**Il n'est pas installé.** L'installer signifie ajouter, en **première** instruction des
cinq fonctions acceptées :

```python
if route_e is not None:
    from .future_route_e_pre_run_locks import enforce_route_e_guard

    enforce_route_e_guard(route_e, entry_point="<nom littéral>")
```

Cette modification a été **écrite, exécutée et mesurée** pendant cette mission : les cinq
fonctions refusent alors correctement, `RouteEGuardRefused` avant tout effet, et le
comportement sans signal est inchangé. **Mais elle change les octets de trois sources
acceptées**, et ces octets sont épinglés, test par test, par **deux fichiers hors
allowlist**. Neuf tests verts deviennent rouges :

```text
tests/test_future_lifecycle_runner_integration.py
  ::test_14_no_public_entry_point_accepts_a_lifecycle_closure            (pin de signature)
  ::test_23e_lifecycle_source_is_unchanged_across_the_succession         (pin de hash)
  ::test_23f_current_source_matches_the_successor_qualification          (pin de hash)
  ::test_23g_runner_integration_remains_pending_formal_requalification   (pin de hash)
  ::test_23i_every_historically_pinned_artifact_is_explicitly_accounted_for
  ::test_rs01_13_the_successor_qualification_binds_the_current_lineage_and_hashes
  ::test_rs01_15_the_historical_runner_package_is_pinned_and_immutable
tests/test_future_lifecycle_owned_pipeline.py
  ::test_op_21a_the_public_signature_accepts_no_injectable_artifact      (pin de signature)
  ::test_op_23e_the_accepted_stack_sources_are_unchanged_by_this_mission (pin de hash)
```

La condition du §9 du handoff — *« aucun nouveau test n'échoue »* — est **binding**. Les
modifications des trois sources acceptées ont donc été **intégralement annulées** : elles
sont **byte-identiques** à la base. `PRB-5` reste **OPEN**, le garde est déclaré non
installé dans le code lui-même (`GUARD_IS_NOT_INSTALLED`), et l'extension nécessaire est
demandée au §11. **Aucune fermeture n'est fabriquée.**

Ce qui est testé aujourd'hui sur les cinq **vraies** fonctions reste donc la propriété
**faible** LK-L1 : chacune refuse à son propre premier contrôle, avec son exception typée,
avant entropie, réseau, sous-processus non cryptographique, seed/famille/namespace, loi ou
CI, moteur, lecture historique et écriture persistante. Ce n'est **pas** un refus Route E.

Recherche de façades alternatives : aucun export, CLI, runner ou point d'entrée
supplémentaire donnant accès aux mêmes capacités n'a été trouvé. Aucune sixième entrée
réelle n'est à signaler.

---

## 8. PRB-1 … PRB-4 et HR-10

- **PRB-1** inchangé depuis `0541400` et toujours discriminant : couverture exacte du
  support (orphelin, non assigné, doublon de clé, doublon de triple), octets canoniques,
  écriture atomique bornée non écrasante, relecture obligatoire, digest recomputé **depuis
  les octets relus**, symlinks et chemins hors racine refusés. Intégration : **absente**.
- **PRB-2** : couches 1 à 4 déjà livrées ; la couche 5 — **authenticité** — l'est
  désormais. Il n'existe **plus aucun callback booléen** dans une signature publique :
  `verify_public_commitment` prend une réponse beacon et un chemin de vérificateur, jamais
  un verdict. `verifier=lambda _: True` n'est plus exprimable. Enforcement dans les
  entrées acceptées : **bloqué** (§7).
- **PRB-3** : un seul `_frozen_check_order`, utilisé par les deux entrées publiques **et**
  par le garde ; `must_precede_unix` obligatoire sans défaut ; la phase `VERIFIER` fait
  maintenant la vérification cryptographique réelle.
- **PRB-4** : inchangé, revendiqué **au niveau digest uniquement**.
- **HR-10 / D** : `assemble_draw_outcome` n'a **aucun** paramètre `classifier` ; le seam
  est privé. L'assembleur reste **anticipatoire** : aucune source acceptée ne l'appelle
  (`RE-L10`), donc D reste `PARTIAL`.

**HR-1 … HR-11** : tous conservés. HR-4 et HR-5 sont désormais prouvés contre le **vrai**
vérificateur au lieu d'un callback synthétique. HR-3 : correctif `PASS`, propriété globale
détaillée au §6.

---

## 9. Tests réellement exécutés

Python **3.11.15**, pytest **8.4.2**, numpy **2.4.4**. Aucun réseau, aucun contact drand,
aucune donnée historique, aucun pas moteur dans les tests de cette mission.

| # | Commande exacte | Périmètre | Collectés | Passed | Failed |
|---|---|---|---|---|---|
| 1 | `pytest tests -q` sur la base `0541400` | dépôt entier, base | **1 241** | 1 236 | **5** |
| 2 | `pytest tests/test_future_route_e_pre_run_locks_00.py -q` | PRB + HR | **152** | 152 | 0 |
| 3 | `pytest tests/test_future_route_e_pre_run_blocker_closure_00.py -q` | A–F, **fichier non modifié** | **104** | 104 | 0 |
| 4 | `pytest tests/test_future_route_e_pre_run_integration_00.py -q` | garde + cinq vraies entrées + blocker | **33** | 33 | 0 |
| 5 | `pytest tests/test_route_e_beacon_verifier.py -q` | vérificateur Go + adaptateur | **42** | 42 | 0 |
| 6 | `pytest -q <les sept fichiers nommés>` | régression sur la lignée acceptée | **673** | 673 | 0 |
| 7 | `pytest tests -q --ignore=<les quatre fichiers de mission>` | `tests/` moins la mission | **946** | 941 | **5** |
| 8 | `pytest tests -q` | **suite candidate entière** | **1 277** | 1 272 | **5** |
| 9 | groupes 2+3+4+5, deux fois de suite | déterminisme | 331 | 331 | 0 |

`152 + 104 + 33 + 42 + 946 = 1 277` : groupes **disjoints**, aucun double comptage.
**0 skip, 0 xfail, 0 xpass, 0 deselected, 0 erreur de collecte** partout.
Le groupe 6 est nommé **régression sur la lignée acceptée (sept fichiers)**, jamais « la
suite entière ». **933 n'est pas et n'a jamais été la suite totale.**

### 9.1 Builds

```text
go version go1.24.7 linux/amd64
CGO_ENABLED=0 GOOS=linux   GOARCH=amd64 go build -trimpath -ldflags="-buildid="
   sha256 2534fa4af5ed6d6d4294be26542b52fe7445412532db97e66a955cacba3cca6d   3 433 098 o
CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build -trimpath -ldflags="-buildid="
   sha256 ea15b5de9f88a6fd0557e1912c31493670f9322bc901d8841b6868cd3220045c   3 527 168 o  (PE32+)
```

Rebuild Linux : **byte-identique**. Les deux binaires ont été construits dans un
répertoire temporaire et **ne sont pas committés**. Modules épinglés :
`github.com/drand/kyber v1.3.1`, `github.com/drand/kyber-bls12381 v0.3.4`,
`github.com/kilic/bls12-381 v0.1.0`, plus `golang.org/x/{crypto,sys}` via les `replace`
déclarés — tous dans `go.sum`. Aucun cgo. Le binaire Windows n'a **pas** été exécuté ici.

### 9.2 Mutations discriminantes (copies jetables, jamais committées)

Chaque mutant est **sémantiquement valide** : il compile, s'importe et change le
comportement, jamais la syntaxe ni une signature.

| Mutation | Effet |
|---|---|
| writer d'évidence remplacé par un no-op | **6 rouges** |
| relecture des octets remplacée par un parse direct | **3 rouges** |
| ordre des phases modifié | **7 rouges** |
| cutoff rendu optionnel partout (garde + anchor + priorité) | **5 rouges** |
| appel du helper remplacé par un faux « verified » | **12 rouges** |
| contrôle `randomness = sha256(signature)` neutralisé | **1 rouge** |
| round pris dans la réponse de l'appelant au lieu d'être dérivé | **2 rouges** |
| appel du vrai classifieur retiré | **3 rouges** |
| garde acceptant un signal non typé | **4 rouges** |

Les cinq mutations « retrait du hook de garde dans chaque fonction acceptée » ne sont pas
applicables ici : **le hook n'est pas installé** (§7). Elles ont été exécutées lors de
l'essai d'intégration et tuaient chacune 1 à 2 tests ; elles seront rejouables dès que
l'extension d'allowlist du §11.1 sera accordée.

### 9.3 Les cinq échecs hérités

```text
tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[split|merge|tie|collapse]
    TypeError: track_components() missing 1 required keyword-only argument: 'sampled_frames'
tests/test_motile_polar.py::test_scramble_preserves_all_declared_invariants_and_destroys_organization
    AssertionError: support overlaps its own translate: displacement would not conserve mass
```

Ensemble, node IDs, signatures et causes **strictement identiques** à la base :
**`new_failures = 0`**. Aucun skip, xfail ni deselection ne les masque. Ils ne sont
**jamais** présentés comme verts ni résolus. Aucune réparation n'a été tentée : elle n'est
pas autorisée dans cette mission. La revue finale devra dire si cette dette est compatible
avec une fermeture pré-run ou si une réparation séparée doit précéder la prérégistration.

---

## 10. Ce qui demeure inconnu, et les contradictions relevées

- **Contradiction rapportée, non tranchée en silence** : le mandat et le reviewer
  précédent supposaient que le DST exact suffirait à identifier le schéma. Le code source
  de drand montre que **deux** schémas signent sur G1 — `bls-unchained-on-g1` (fastnet)
  avec le **DST G2**, et `bls-unchained-g1-rfc9380` (quicknet) avec le DST G1. Le helper
  refuse tout autre scheme, et le contrôle inter-implémentations montre qu'un round
  quicknet évalué avec le DST fastnet est **invalide** — la discrimination est donc
  effective, mais le piège devait être nommé.
- **Non résolu** : les hashes `go.sum` n'ont pas été confrontés à `sum.golang.org`
  (inaccessible ici). **À vérifier par un tiers.**
- **Non trouvé** : aucun jeu de vecteurs officiel, signé et versionné **par drand**
  spécifiquement pour `bls-unchained-g1-rfc9380`. Les vecteurs utilisés viennent de dépôts
  officiels (drand/tlock, drand/drand-client) et d'un tiers (noislabs), tous committés.
- **Scientifiquement, tout reste inconnu** : aucune valeur de `Δ(f)`, de `ψ`, aucune
  fraction observée, aucune répartition sur les cinq états terminaux, aucun monde Route E,
  aucune loi tirée, aucune condition initiale, aucun seed scientifique, aucun round de
  beacon **scientifique** consulté, aucun namespace, aucune famille. Route E reste **un
  protocole sélectionné, non confirmé**. Le seul résultat publié demeure le premier article
  (`https://doi.org/10.5281/zenodo.21403458`), sans ownership local, sans autonomie, sans
  individualité complète, sans reconstruction, sans reproduction et sans hérédité.

---

## 11. Autorité demandée

### 11.1 Installer le garde (fermeture de PRB-5 et enforcement de PRB-2)

Extension strictement limitée aux **deux fichiers de tests** qui épinglent les octets :

```text
tests/test_future_lifecycle_runner_integration.py
tests/test_future_lifecycle_owned_pipeline.py
```

Portée : mettre à jour les neuf assertions listées au §7 — sept pins de hash et deux pins
de signature — pour tenir compte du paramètre `route_e` et des nouveaux digests, **sans**
supprimer un seul contrôle. Les trois sources acceptées sont déjà autorisées ; le diff
attendu y est exactement le bloc de cinq lignes montré au §7, répété cinq fois.

### 11.2 Fermer la seconde moitié de l'anti-reroll

Preuve d'inclusion vérifiable propre au registre d'ancrage choisi, pour établir que la
racine a bien été publiée immuablement avant l'instant désigné. Aucun chemin n'est
proposé ici : le choix du registre est une décision de gouvernance.

### 11.3 Provenance des modules Go

Une exécution de `go mod verify` et une confrontation de `go.sum` au journal de
transparence, depuis un environnement disposant du réseau.

---

## 12. Firewall et remote

Aucune lecture de `results/`, aucun shard, monde, trajectoire ou checkpoint ouvert, aucun
seed, famille, namespace, loi ou CI créé, aucun appel moteur dans les tests de cette
mission, **aucun beacon live consulté**, aucun calcul de `Δ(f)` ou `ψ`, aucune
prérégistration, aucun run, aucune analyse scientifique. Fixtures synthétiques
déterministes, répertoires temporaires et vecteurs cryptographiques publics versionnés
uniquement.

Git : chemins exacts, `GIT_INDEX_FILE` neutralisé, index de preuve sous `/tmp`, ajout
**chemin par chemin**, aucun `git add -A`, aucun checkout, stash, amend, rebase, merge,
cherry-pick, `git gc`, aucun nettoyage. `main` immobile à
`f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77`, `.git/index` réel intact, working tree sale
préservé, toutes les branches antérieures préservées, les records `bc2a42c4` et
`31ccccfb` non modifiés, archives et résidus divulgués conservés.

**Remote.** Une tentative de push **normale**, unique, de la seule branche de cette
révision. Aucun `--force`, aucun retry, aucun changement de credentials, aucun push de
`main`.

---

## 13. Prochaine étape

La seule étape suivante possible est une **revue humaine indépendante** de la fermeture
des six PRB. La prérégistration
(`ROUTE_E_REPLICATION_DENSITY_PREREGISTRATION_00`) reste **interdite** jusqu'à cette
acceptation, et resterait de toute façon une prérégistration, **pas un run**.

> ### `human_review = PENDING`
> ### `scientific_run_authorized = false`
>
> `PRB-6 = CANDIDATE_CLOSED` · `PRB-5 = OPEN` · `PRB-2` enforcement bloqué ·
> `ANTI_REROLL` : choix du round `CANDIDATE_PASS`, publication `UNPROVEN`.
> Aucune acceptation humaine n'est prononcée ici.

---

## 14. A1 — audit obligatoire des neuf pins, et arrêt

L'autorisation A1 étend l'allowlist à `tests/test_future_lifecycle_runner_integration.py`
et `tests/test_future_lifecycle_owned_pipeline.py`, et impose : *« Si leur nombre ou leur
nature diffère, arrête-toi avant de les mettre à jour. »* **Leur nature diffère.** Voici
l'énumération, faite **avant** toute modification.

### 14.1 Les neuf tests et ce qui les protège réellement

| # | Fichier de test | Objet protégé | Ancienne valeur | Ce qui l'invalide |
|---|---|---|---|---|
| 1 | `…runner_integration.py::test_14_no_public_entry_point_accepts_a_lifecycle_closure` | jeu de paramètres **exact** de `publish_future_family_completion` et `open_analysis_access` | `{run_directory, tracking, sampled_frames}` + annotations littérales | tout paramètre ajouté, y compris un `route_e` keyword-only typé |
| 2 | `…owned_pipeline.py::test_op_21a_the_public_signature_accepts_no_injectable_artifact` | liste **ordonnée** des paramètres de `run_owned_future_pipeline` ; `list(open_owned_analysis_access) == ["run_directory"]` | liste littérale de 6 noms | idem |
| 3 | `…owned_pipeline.py::test_op_23e_the_accepted_stack_sources_are_unchanged_by_this_mission` | sha256 de `instrumentation.py`, `lifecycle.py`, `future_lifecycle_runner.py`, `__init__.py` | `lifecycle.py = 3120d820…d03053`, `runner = 7691da35…4b33d08` | toute édition d'octet |
| 4 | `…runner_integration.py::test_23e_lifecycle_source_is_unchanged_across_the_succession` | `UNCHANGED_LIFECYCLE_SHA256` **et** l'égalité entre `CONTRACT_00_QUALIFICATION.json` et `CONTRACT_REQUALIFICATION_01R_QUALIFICATION.json` | `3120d820…d03053` | édition de `lifecycle.py` |
| 5 | `…runner_integration.py::test_23f_current_source_matches_the_successor_qualification` | **toutes** les entrées `source_hashes_sha256` de `…01R_QUALIFICATION.json` | digests dans le **document historique** | édition de `lifecycle.py` ou `future_lifecycle_runner.py` |
| 6 | `…runner_integration.py::test_23g_runner_integration_remains_pending_formal_requalification` | `lineage.unchanged_runner_sha256` de `…01R_QUALIFICATION.json` | digest dans le **document historique** | édition de `future_lifecycle_runner.py` |
| 7 | `…runner_integration.py::test_23i_every_historically_pinned_artifact_is_explicitly_accounted_for` | `HISTORICALLY_PINNED_ARTIFACTS` (7 entrées) **et** `lineage.divergent_from_historical_pin` de `…01R_QUALIFICATION.json` | 7 digests + le bloc de divergence déclarée | édition de `lifecycle.py` (une divergence non déclarée fait échouer le test) |
| 8 | `…runner_integration.py::test_rs01_13_the_successor_qualification_binds_the_current_lineage_and_hashes` | `source_hashes_sha256` de `…RUNNER_STACK_REQUALIFICATION_01_QUALIFICATION.json` **et** `historical_versus_current.runner_source_changed_by_this_mission is False` **et** `…_historical == …_current` | digests + **assertion sémantique** | édition de `future_lifecycle_runner.py` |
| 9 | `…runner_integration.py::test_rs01_15_the_historical_runner_package_is_pinned_and_immutable` | `HISTORICAL_RUNNER_PACKAGE_DIGESTS` **et** `identity_proofs.future_lifecycle_runner_py_sha256` de `…RUNNER_HARDENING_00_QUALIFICATION.json`, avec le message « the runner this mission requalifies is byte-identical to the hardened one » | digest dans un record **scellé** d'une autre mission | édition de `future_lifecycle_runner.py` |

### 14.2 Pourquoi A1 ne suffit pas

Les neuf tests s'appuient sur **treize sites de liaison** répartis sur **deux fichiers de
tests** (dans l'allowlist A1) **et quatre documents de qualification historiques** (hors
allowlist A1) :

```text
docs/individuation/FUTURE_LIFECYCLE_CONTRACT_00_QUALIFICATION.json
    source_hashes_sha256[lifecycle.py]
docs/individuation/FUTURE_LIFECYCLE_CONTRACT_REQUALIFICATION_01R_QUALIFICATION.json
    source_hashes_sha256[lifecycle.py] · source_hashes_sha256[future_lifecycle_runner.py]
    lineage[unchanged_runner_sha256]
docs/individuation/FUTURE_LIFECYCLE_RUNNER_STACK_REQUALIFICATION_01_QUALIFICATION.json
    source_hashes_sha256[lifecycle.py] · source_hashes_sha256[future_lifecycle_runner.py]
    historical_versus_current[runner_source_changed_by_this_mission]  <- SÉMANTIQUE
    historical_versus_current[future_lifecycle_runner_py_sha256_historical|_current]
docs/individuation/FUTURE_LIFECYCLE_RUNNER_HARDENING_00_QUALIFICATION.json
    identity_proofs[future_lifecycle_runner_py_sha256]                <- RECORD SCELLÉ
    identity_proofs[future_lifecycle_runner_py_blob|_identical_at]
    identity_proofs[bound_lifecycle_package_unchanged_sha256]
```

Trois raisons, chacune suffisante, d'arrêter :

1. **Hors allowlist.** Ces quatre documents ne sont pas listés par A1, et le §3 interdit
   explicitement de modifier « les anciens records ».
2. **Ce ne sont pas des digests, ce sont des affirmations de mission.**
   `runner_source_changed_by_this_mission is False` et l'`identity_proofs` de
   `HARDENING_00` sont des **tripwires délibérés** : ils existent précisément pour qu'une
   modification ultérieure du runner ne puisse pas passer inaperçue. Les mettre à jour
   reviendrait à **masquer le tripwire en éditant la qualification** — exactement ce qu'une
   revue humaine antérieure de ce programme a interdit.
3. **Ce serait une requalification, pas un rebaselining.** Rendre la suite verte après
   édition des trois sources acceptées suppose de **requalifier** quatre missions déjà
   scellées et humainement acceptées. Cela demande son propre mandat, sa propre revue, et
   très probablement de nouveaux documents de qualification — ce qu'aucune autorisation en
   cours ne couvre.

**Conséquence.** Aucun pin n'a été modifié. Aucun crochet n'a été installé. Les trois
sources acceptées restent **byte-identiques** à `c08e27c`. `PRB-5` reste **OPEN**.

```text
guarded_entry_count = 0
accepted_entry_integration_present = false
behavioral_hook_mutations_killed = 0   (non applicable : aucun crochet n'est installé)
```

Les six mutations comportementales du §6 de l'autorisation **n'ont pas été exécutées** :
elles supposent des crochets installés. Elles restent prêtes et seront exécutables dès que
l'autorité demandée au §14.3 sera accordée.

### 14.3 Autorité désormais nécessaire (remplace A1)

A1 tel qu'écrit est **insuffisant**. Ce qu'il faut, précisément :

```text
1. les deux fichiers de tests déjà accordés par A1 (suffisants pour les pins 1, 2, 3,
   et pour les constantes UNCHANGED_LIFECYCLE_SHA256, HISTORICALLY_PINNED_ARTIFACTS,
   HISTORICAL_RUNNER_PACKAGE_DIGESTS) ;
2. PLUS une décision explicite sur les quatre documents de qualification historiques,
   au choix du propriétaire :
   (a) autoriser leur mise à jour, en documentant chaque transition ancienne -> nouvelle
       valeur et en conservant l'ancienne comme preuve de lignée ; ou
   (b) créer un document de requalification propre à cette mission qui supersède
       explicitement les bindings concernés, en laissant les records historiques intacts.
```

L'option (b) est la plus conservatrice : elle ne réécrit aucun record scellé. Elle exige
en revanche que les tests concernés lisent le nouveau document, donc une modification des
deux fichiers de tests **et** la création d'un document — ce qui dépasse aussi A1.

---

## 15. Réconciliation des identifiants de tests (§7 de l'autorisation)

L'autorisation compare `191` (base `0541400`) à `152 + 33 = 185` et en déduit **six tests
nets manquants**. Cette soustraction **omet un fichier** : la mission compte désormais
**quatre** fichiers, pas trois.

| Groupe | `0541400` | `c08e27c` |
|---|---|---|
| `test_future_route_e_pre_run_locks_00.py` | **191** | 152 |
| `test_future_route_e_pre_run_integration_00.py` | — | 33 |
| `test_route_e_beacon_verifier.py` | — | **42** |
| **total mission (hors A–F)** | **191** | **227** |

Le solde réel est donc **+36**, pas −6. Par fonction distincte : **115 → 155**.

Classification des **25** noms de fonctions qui disparaissent :

| Classe | Nombre | Détail |
|---|---|---|
| **déplacé** | 9 | `hr4_01…07`, `hr5_01…02` → `test_route_e_beacon_verifier.py`, où ils sont **renforcés** : ils s'exécutent contre le vrai vérificateur et de vrais vecteurs au lieu de callbacks synthétiques |
| **déplacé** | 3 | `prb5_real_01/02/03` → `weak_01`, `blocker_01`, `blocker_02` dans le fichier d'intégration |
| **renommé** | 11 | `prb2_08`, `prb3_03`, `prb5_08/09`, `prb5_facade_04/05/06/07`, `prb6_03/08/09` — renommés parce que la propriété a changé de forme (statut factuel, absence de callback) |
| **fusionné / paramétré** | 1 | `prb6_05` (vérificateur qui lève) → `test_helper_01` (helper qui plante) + `test_helper_04/05` |
| **supersédé par construction** | 1 | `hr4_02_a_verifier_that_does_not_return_true_is_STOP` : le callback booléen qu'il testait **n'existe plus**, donc la propriété est inviolable par construction. Le cas adverse équivalent est `test_helper_05_a_forged_success_without_the_pinned_echo_is_refused` (un helper qui dit « verified » sans réécho du scheme et du DST épinglés est refusé) et `test_helper_04` (statut inconnu ⇒ `internal_error`) |
| **nouveau** | 40 | garde, round dérivé, vecteurs, protocole du helper, blocker |

**Aucune assertion matérielle n'a été supprimée ni réduite en silence.** Aucune
restauration n'est donc nécessaire dans `tests/test_future_route_e_pre_run_locks_00.py`,
et ce fichier n'est pas modifié par ce commit.

---

## 16. A2 — dossier de décision propriétaire sur le registre public

**Aucun texte gelé ne fixe de registre.** Vérifié : le mandat `01S` et les deux revues
humaines ne nomment ni venue, ni format de preuve, ni racine de confiance. La seule
contrainte littérale est *« public immutable or append-only commitment, verifiable without
a secret »*, précisée par `ARCHITECTURE_01` : la **publication** peut exiger un credential,
la **vérification** non. Le mot « zenodo » n'apparaît que comme DOI du premier article,
jamais comme venue d'ancrage.

**Rien n'est implémenté ici.** Trois options, à trancher par le propriétaire.

| | **A. OpenTimestamps (Bitcoin)** | **B. RFC 3161 (TSA)** | **C. Sigstore / Rekor** |
|---|---|---|---|
| Preuve d'inclusion | fichier `.ots` (opérations + `BitcoinBlockHeaderAttestation`) | jeton DER `.tsr` (CMS `SignedData`, `TSTInfo`) | bundle Sigstore v0.3 (preuve d'inclusion + checkpoint signé) |
| Antériorité | inclusion dans un bloc Bitcoin ; `nTime` de l'en-tête ; adossée à la preuve de travail | `genTime` **signé** par la TSA, immédiat | **faible** : la doc Sigstore dit que l'`integratedTime` de Rekor v1 vient de son horloge interne et est *mutable sans détection* |
| Vérification hors ligne | oui **si** l'en-tête de bloc (80 o) est livré ; réserve : aucun vérificateur « headers-only » prêt à l'emploi identifié | **oui, nativement** ; il faut livrer le certificat TSA et sa chaîne | oui (`--offline`) mais il faut embarquer la racine TUF |
| Racine de confiance | Bitcoin (PoW), **pas de partie unique** | **une seule partie** (mitigeable par 2–3 TSA indépendantes) | l'opérateur du journal + TUF ; partie unique pour le temps |
| Windows + Linux, Python 3.11 | `opentimestamps` (LGPL-3.0, dernière release ≈ 2022, maintenance lente) + `python-bitcoinlib`, `pycryptodomex` | `rfc3161-client` 1.0.6 (2026-04), Apache-2.0, **wheels abi3 Windows + manylinux**, PyO3, aucune fonction réseau | `sigstore` (Apache-2.0, bien maintenu) mais arbre de dépendances large |
| Fichiers / dépendances à ajouter | `.ots`, en-tête de bloc, `anchor.json` + 2–3 dépendances lourdes (ou un parseur `.ots` maison) | `.tsq`, `.tsr`, `tsa_chain.pem` + **1** dépendance | bundle + `trusted_root.json` + nombreuses dépendances |
| WAIT / STOP | **WAIT réel** : l'attestation est *pending* quelques heures, puis `ots upgrade`. **STOP** si elle n'est pas complète, ou si `nTime ≥ T` | **aucun WAIT** (synchrone). **STOP** si `genTime ≥ T`, empreinte ≠ racine, chaîne invalide | STOP si l'inclusion ou le checkpoint ne valide pas |
| Publication | gratuite, **sans compte** | FreeTSA gratuit, sans compte | identité OIDC requise (acceptable : la vérification reste sans secret) |
| Satisfait littéralement « public immutable or append-only » | **oui** | **non** — un jeton TSA n'est pas un registre | oui pour l'append-only, **non** pour l'antériorité |

**Recommandation, à valider par le propriétaire :** **A en primaire, B en garde-fou
obligatoire**. A est la seule option satisfaisant littéralement l'obligation gelée avec une
antériorité qui ne repose pas sur une partie unique ; B est instantané, vérifiable hors
ligne nativement, et couvre exactement la fenêtre WAIT de A. C est écarté comme ancre
temporelle primaire **par sa propre documentation**.

Séquence opérateur si A+B est retenu : figer `R` → jeton RFC 3161 auprès de ≥ 2 TSA →
`ots stamp` → attendre la confirmation Bitcoin → `ots upgrade` jusqu'à attestation
complète → extraire la hauteur et l'en-tête → **vérifier `nTime < T` et `genTime < T`,
sinon STOP** → committer `R.ots`, l'en-tête, `R.tsq`, les `.tsr`, `tsa_chain.pem` et un
`anchor.json` liant racine, hauteur, `nTime`, `genTime`, `T` et le round drand.

**Non vérifié depuis les sources primaires** : taille typique d'un `.ots` ; licence et
disponibilité de wheels du paquet `opentimestamps` (PyPI bloqué par robots.txt) ;
existence d'un vérificateur OTS hors-ligne « headers-only » prêt à l'emploi ; limites de
débit de FreeTSA ; toute voie Certificate Transparency acceptant une charge arbitraire de
32 octets.

```text
public_registry_inclusion_proven = false
anti_reroll_publication_inclusion_proven = false
ANTI_REROLL = UNPROVEN
```

---

## 17. A3 — provenance des modules Go

Aucun fichier Go n'a été modifié.

| Contrôle | Commande | Résultat |
|---|---|---|
| Vérification **locale** contre `go.sum` | `GOPROXY=off go mod verify` | **`all modules verified`** |
| Re-téléchargement dans un `GOMODCACHE` temporaire, **`GOSUMDB=sum.golang.org`, jamais `off`** | `env -i … GOMODCACHE=<tmp> GOPROXY=direct GOSUMDB=sum.golang.org go mod download github.com/drand/kyber-bls12381` | **exit 0** |
| Sonde discriminante : module **absent** de `go.sum`, qui force une consultation du journal | `… go mod download github.com/google/uuid@v1.6.0` | **échec** : `reading https://sum.golang.org/lookup/…: 403 Forbidden — Host not in allowlist: sum.golang.org` |

**Lecture rigoureuse.** Le succès de la deuxième ligne **ne prouve pas** que le journal de
transparence a été consulté : lorsqu'une entrée existe déjà dans `go.sum`, le go command
vérifie contre `go.sum` et **ne consulte pas** la base de sommes. La troisième ligne le
démontre : dès qu'une consultation est réellement nécessaire, elle échoue, parce que
`sum.golang.org` n'est pas dans l'allowlist réseau de cet environnement.

```text
go_mod_verify_local = pass
sumdb_transparency_verified = false
```

À faire par un tiers disposant du réseau : `go mod verify` **et** un téléchargement à
cache vide avec `GOSUMDB=sum.golang.org`, sur les cinq modules épinglés.

---

## 18. Déclaration finale de cet incrément

```text
guarded_entry_count                      = 0
behavioral_hook_mutations_killed         = 0   (non applicable : aucun crochet installé)
accepted_entry_integration_present       = false
public_registry_inclusion_proven         = false
sumdb_transparency_verified              = false
ANTI_REROLL                              = UNPROVEN
human_review                             = PENDING
preregistration_authorized               = false
scientific_run_authorized                = false
```

Aucune acceptation des six PRB n'est demandée : A2 reste non résolu. La prochaine étape est
la **décision propriétaire sur le registre public** et sur l'autorité du §14.3, puis
seulement la revue humaine indépendante complète.

---

## 19. A1-R — préflight de lignée

| Contrôle | Résultat |
|---|---|
| Base | `f152c3c43d316cfbc4d7704fc91c69e51ee5fefa` — objet présent, type `commit` |
| Parent | `c08e27c0d7c133789333a73fa66fedc5ab0a2979` ✔ attendu |
| Grand-parent | `054140024267183fa43ef86755cd1c82d5a41483` ✔ attendu |
| Merge | **non** — `f152c3c` a exactement **1** parent |
| Différence `c08e27c → f152c3c` | exactement **2 `M`** : le REPORT et la DECISION, comme annoncé |
| Objets historiques requis | `00afcdd1`, `c6d4acf`, `bc2a42c`, `a379efa6`, `31ccccfb`, `0541400`, `c08e27c` — tous présents |
| Reconstruction depuis les rapports | **aucune** |

Copie de travail propre : arbre de `f152c3c` restreint à `edlab/`, `tests/`, `tools/`,
`docs/individuation/` (chemins exacts, jamais d'énumération de répertoire scientifique).
**269 fichiers byte-identiques**, 0 fichier local en trop. Les **5** seuls écarts d'octets
(`sc_iom/engine.py`, `sc_mcm/config.py`, `sc_mcm/engine.py`, `scaffold/engine.py`,
`scaffold/observables.py`) sont la conversion **CRLF déclarée dans `.gitattributes`**
(`text eol=crlf`) appliquée par `git archive` à l'export — pas une divergence de contenu.

---

## 20. Audit obligatoire des liaisons (§3) — reproduit, puis **dépassé**

### 20.1 Les neuf assertions sont reproduites exactement

Copie **jetable** contenant le patch exact envisagé : paramètre keyword-only typé
`route_e: RouteERequest | None = None` sur les cinq fonctions, et comme **première
instruction exécutable après la docstring** `if route_e is not None:
enforce_route_e_guard(route_e, entry_point=…)`.

```text
pytest -q <les 7 fichiers de la lignée acceptée>   →  9 failed, 664 passed
```

Les neuf identifiants sont **exactement** ceux du §14. Aucun autre test ne casse.

### 20.2 Les treize sites, vérifiés contre les objets Git, pas contre les JSON

`historical_commit` = commit où le record a été scellé ; `historical_source_blob` = objet
Git réellement qualifié ; la valeur historique a été **recalculée depuis ce blob**.

| # | `record_path` | champ | valeur historique | `historical_commit` | `historical_source_blob` | consommateur | classification | traitement proposé |
|---|---|---|---|---|---|---|---|---|
| 1 | `…RUNNER_INTEGRATION.py` (allowlist) | `test_14.allowed_annotations` | `{run_directory, tracking, sampled_frames}` | — | — | `test_14` | `current_head_tripwire` | étendre à `route_e`, sans retirer un contrôle |
| 2 | `…OWNED_PIPELINE.py` (allowlist) | `test_op_21a` liste ordonnée | 6 noms | — | — | `test_op_21a` | `current_head_tripwire` | idem |
| 3 | `…OWNED_PIPELINE.py` (allowlist) | `test_op_23e` carte sha256 | `lifecycle=3120d820…`, `runner=7691da35…` | — | — | `test_op_23e` | `current_head_tripwire` | nouvelles valeurs + transition documentée |
| 4 | `FUTURE_LIFECYCLE_CONTRACT_00_QUALIFICATION.json` | `/source_hashes_sha256/…/lifecycle.py` | `3120d820…d03053` | `4282fc6ead9156…` | `a3592eb7d97b0ff9…` ✔ recalculé | `test_23b`, `test_23e` | **`historical_fact`** | **inchangé** |
| 5 | `…CONTRACT_REQUALIFICATION_01R…json` | `/source_hashes_sha256/…/lifecycle.py` | `3120d820…d03053` | `9185afaa2de69c…` | `a3592eb7d97b0ff9…` ✔ | `test_23e`, `test_23f` | **`historical_fact`** | **inchangé** |
| 6 | `…01R…json` | `/source_hashes_sha256/…/future_lifecycle_runner.py` | `7691da35…4b33d08` | `9185afaa2de69c…` | `44135ee74d8a19bd…` ✔ | `test_23f` | **`historical_fact`** | **inchangé** |
| 7 | `…01R…json` | `/lineage/unchanged_runner_sha256` | `7691da35…4b33d08` | `9185afaa2de69c…` | `44135ee74d8a19bd…` ✔ | `test_23g` | **`historical_fact`** | **inchangé** |
| 8 | `…01R…json` | `/lineage/historically_pinned_artifacts` + `/lineage/divergent_from_historical_pin` | 7 entrées | `9185afaa2de69c…` | — | `test_23i` | **`historical_fact`** | **inchangé** |
| 9 | `…RUNNER_STACK_REQUALIFICATION_01…json` | `/source_hashes_sha256/…/lifecycle.py` | `3120d820…d03053` | `9a1bfaff42009f…` (scellé `d493168`) | `a3592eb7d97b0ff9…` ✔ | `test_rs01_13` | **`historical_fact`** | **inchangé** |
| 10 | `…STACK_01…json` | `/source_hashes_sha256/…/future_lifecycle_runner.py` | `7691da35…4b33d08` | `9a1bfaff42009f…` | `44135ee74d8a19bd…` ✔ | `test_rs01_13` | **`historical_fact`** | **inchangé** |
| 11 | `…STACK_01…json` | `/historical_versus_current/runner_source_changed_by_this_mission` | `false` | `9a1bfaff42009f…` | — | `test_rs01_13` | **assertion sémantique de mission** | **inchangé** |
| 12 | `…STACK_01…json` | `/historical_versus_current/…_sha256_historical` ≡ `…_current` | `7691da35…` = `7691da35…` | `9a1bfaff42009f…` | `44135ee74d8a19bd…` ✔ | `test_rs01_13` | **assertion sémantique de mission** | **inchangé** |
| 13 | `…RUNNER_HARDENING_00_QUALIFICATION.json` | `/identity_proofs/{…_sha256, …_blob, …_identical_at}` et `/identity_proofs/bound_lifecycle_package_unchanged_sha256` | `7691da35…`, blob `44135ee7…`, `[23df99d, a2d44c6, 7facb41, c1faa07]` | `9d13e9b72596f3…` | `44135ee74d8a19bd…` ✔ **aux quatre commits cités** | `test_rs01_15` | **record scellé** | **inchangé** |

`9 assertions · 13 sites · 10 hors allowlist · 4 records` — **reproduit**.
Les quatre records sont **byte-identiques entre leur commit de scellement et le HEAD** :
`8f423bb0…`, `0752b86c…`, `509f27b2…`, `f29da369…`.

### 20.3 Un **quatorzième** site, que ni A1 ni A1-R n'anticipent

`test_rs01_12_the_successor_node_binding_is_complete_and_unaltered` **exécute une vraie
collecte** (`pytest --collect-only` en sous-processus) sur **quatre sélecteurs** et la
compare à `FUTURE_LIFECYCLE_RUNNER_STACK_REQUALIFICATION_01_QUALIFICATION.json` :

```text
test_binding.selectors    = [ …tracker_repair.py, …lifecycle_contract.py,
                              tests/test_future_lifecycle_runner_integration.py,
                              …lattice_bond_instrumentation.py ]
test_binding.node_count       = 251
test_binding.node_list_sha256 = a425c3736f0b5d819ef708c2433b785cf706381798ffc48a7ce4b5941161276a
```

`tests/test_future_lifecycle_runner_integration.py` **est un sélecteur**. Preuve
expérimentale, dans une copie jetable — **une seule** fonction de test ajoutée à ce
fichier :

```text
FAILED …::test_rs01_12_the_successor_node_binding_is_complete_and_unaltered
  AssertionError: collected node list differs
  At index 178 diff: '…::test_a1r_probe_new_layer_test_added_by_the_authorized_edit'
```

Le seul correctif possible est de réécrire `node_ids`, `node_count` et
`node_list_sha256` **dans STACK_01**, que le §2 déclare `PRESERVE_BYTE_IDENTICAL`.

**Contradiction interne à A1-R.** Le §7.1 (couche d'intégrité historique) et le §7.2
(épinglage du nouveau record) demandent d'ajouter des tests ; le §2 interdit de toucher
STACK_01. Les deux ne peuvent pas être vrais ensemble tant que le fichier
`tests/test_future_lifecycle_runner_integration.py` reçoit **un seul nom de test nouveau,
renommé ou supprimé**.

Une voie étroite subsiste et devrait être **autorisée explicitement** : réécrire
uniquement les **corps** des neuf tests de ce fichier, en **préservant exactement** les
noms, et placer toute nouvelle assertion dans
`tests/test_future_lifecycle_owned_pipeline.py`, dans
`tests/test_future_route_e_pre_run_integration_00.py` ou dans le nouveau fichier — aucun
de ces trois n'est un sélecteur. Cette contrainte n'est écrite nulle part dans A1-R.

Conformément au §3 — *« Si les nombres, la nature, les consommateurs ou les objets
diffèrent […], arrête-toi avant toute modification »* — **premier arrêt**.

---

## 21. §4 — précondition architecturale : le signal Route E est **contournable**

C'est l'arrêt décisif, et il est indépendant du §20.

### 21.1 Ce qui passe

| # | Condition | Verdict | Preuve |
|---|---|---|---|
| 1 | type et garde réutilisables sans duplication | **PASS** | `RouteERequest` et `enforce_route_e_guard` importés depuis `future_route_e_pre_run_locks` dans les trois sources ; aucun cycle d'import ; aucune duplication |
| 2 | les cinq fonctions réelles sont exactement celles listées | **PASS** | `inspect.signature` sur les cinq, et `SUPPORTED_ENTRY_POINTS` les nomme exactement |
| 5 | le format A2 futur n'imposera pas une nouvelle signature publique | **PASS** | le paramètre est typé par le **conteneur** `RouteERequest` ; ajouter à `PublicCommitment`/`RouteEReceipt` les champs OTS + RFC 3161 ne change **aucune** des cinq signatures |

### 21.2 Ce qui échoue

**Condition 3 — une sixième entrée réelle existe, hors allowlist.**

`edlab/substrates/lattice_bond/future_prospective_measurement_bridge.py` :

```text
1106  def run_measurement_bridge(run_directory, *, law_spec, initial_state,
1107                             sampled_frames, measurement_spec, intervention,
1108                             backend, acquisition_source_identity) -> MeasurementRecord:
1116      """The single supported measurement entry point.  It performs every stage itself.
1139      captures, step_count = _execute(...)        # -> 759 LatticeBondEngine(law_spec)
                                                     #    767 engine.step(...)
1148      _persist_captures(directory, captures, ...)  # frames écrites sur disque
1160      owned_record = run_owned_future_pipeline(directory,
1161          acquisition_source=_mask_source, sampled_frames=…, detector_spec=…,
1162          tracker_spec=…, acquisition_source_identity=…)   # AUCUN route_e
```

Ce module **se déclare lui-même** « the single supported measurement entry point ». Il
n'est **pas** dans l'allowlist A1-R. Deux conséquences, chacune suffisante :

1. Il **ne peut pas transmettre** un signal qu'il n'accepte pas : une demande Route E
   passant par lui atteint `run_owned_future_pipeline` avec `route_e=None`. **Le garde
   ne se déclenche jamais.**
2. Même s'il le transmettait, le refus arriverait **après** `LatticeBondEngine.step`
   (ligne 1139) et **après** l'écriture des frames (ligne 1148). Un garde qui refuse
   après l'exécution du moteur n'est pas un garde.

**Deux autres entrées réelles ignorent totalement les cinq fonctions :**

| Module | Références `lifecycle` | Moteur | Entrées | CLI |
|---|---|---|---|---|
| `stage_b.py` | **0** | `721 LatticeBondEngine(spec)`, `733–735 engine.step(...)` | `run_world` (718), `run_family` (1019), `main` (1065) | `--manifest`, `__main__` |
| `stage_b_reproduce.py` | **0** | — | `reproduce_complete_world` (1633), `reproduce_family` (1844), `main` (1952) | `__main__` |

`stage_b.run_family` énumère les mondes, fait tourner le moteur et écrit une racine de
résultats sous `namespace` — **une famille scientifique complète, sans une seule référence
au lifecycle**. C'est le constat déjà établi par l'audit de reprise de
`FUTURE_LIFECYCLE_CONTRACT_00` (« gate UNUSED / bypassable ») ; il n'a pas changé.

**Condition 4 — le signal n'est pas autoritatif.**

Un paramètre keyword-only **facultatif** est une **auto-déclaration** de l'appelant. Rien
dans `run_directory`, `tracking` ou `sampled_frames` ne permet à une fonction acceptée de
distinguer une intention Route E d'une autre. Le rendre **obligatoire** ne change rien :
l'appelant passerait `route_e=None`. Le rendre **inconditionnel** casserait le
comportement non-Route-E, que le §8 exige inchangé.

```text
guard_refuses_when_route_e_is_signaled      = true
route_e_request_cannot_omit_or_bypass_signal = false
guard_signal_authoritative                   = false
```

Conformément au §4 — *« Si une véritable demande Route E peut atteindre une capacité en
omettant le signal, ou si une sixième entrée existe hors allowlist, arrête-toi avant de
modifier sources et pins »* — **arrêt décisif**.

### 21.3 Ce qui n'a donc pas été fait

Aucune source acceptée modifiée · aucun pin modifié · aucun crochet installé · aucune
mutation comportementale exécutée · **aucun record `…_CURRENT_SOURCE_REQUALIFICATION_01.json`
créé** : il attesterait une transition qui n'a pas eu lieu et porterait
`source_changed_by_this_mission = true` sur des sources inchangées. Le créer serait une
affirmation dépassant les preuves.

Les quatre qualifications historiques restent **byte-identiques**. Les cinq sources
acceptées restent **byte-identiques** à `f152c3c`.

---

## 22. §11 — A3, sumdb, sans muter les fichiers Go

Aucun fichier Go modifié. `go1.24.7 linux/amd64`.

| # | Contrôle | Commande | Résultat |
|---|---|---|---|
| 1 | vérification locale | `GOPROXY=off go mod verify` | **`all modules verified`** |
| 2 | cache **vide**, `GOSUMDB=sum.golang.org` (**jamais `off`**) | `env -i … GOMODCACHE=<vide> GOPROXY=direct GOSUMDB=sum.golang.org go mod download <3 modules>` | exit 0 — **ne prouve rien** : `go.sum` couvre déjà les entrées, le journal n'est pas consulté |
| 3 | **sonde décisive** : `go.sum` **entièrement retiré**, la consultation du journal devient obligatoire | idem, sans `go.sum` | **échec** : `verifying go.mod: reading https://sum.golang.org/lookup/github.com/drand/kyber-bls12381@v0.3.4: 403 Forbidden — Host not in allowlist: sum.golang.org` |
| 4 | reconstruction de **contenu** (cache vide ; sumdb contourné — **explicitement pas une preuve de transparence**) | `GOPRIVATE='*' go build` | `go.sum` reconstruit = **10 lignes**, toutes **présentes verbatim** dans les 21 committées ; **0 ligne divergente**. Les 11 lignes en plus sont des entrées `/go.mod` du graphe de modules (tests amont), pas du build |
| 5 | rebuild reproductible depuis un cache **vide**, avec le `go.sum` committé | `CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -trimpath -ldflags=-buildid=` | sha256 **`2534fa4af5ed6d6d4294be26542b52fe7445412532db97e66a955cacba3cca6d`**, 3 433 098 o — **identique au digest enregistré** |

```text
go_mod_verify_local           = pass
go_sum_content_reconstruction = consistent (0 divergent line)
build_reproducible            = true (byte-identical)
sumdb_transparency_verified   = false
```

L'indisponibilité de `sum.golang.org` n'a justifié **aucune** modification de dépendance
et n'est pas maquillée. Elle reste à lever avant la revue finale, dans un environnement
discriminant.

---

## 23. §10 — décision A2 gelée, non implémentée ici

La décision propriétaire est enregistrée telle quelle, et **rien n'est implémenté** :

```text
public_registry = Bitcoin mainnet via complete OpenTimestamps proof
signed_time     = Sigstore RFC 3161 timestamp over canonical completed OTS proof
acceptance_rule = OTS AND RFC3161          (jamais OTS OR RFC3161)
```

Aucune racine publiée, aucun registre contacté, aucun `.ots`, aucun `.tsr`, aucun jeton.
Les obligations que le futur mandat A2 devra geler sont reprises intégralement dans la
DECISION (`a2_frozen_decision`) : preuve OTS **complète**, jamais `Pending` ; jeton portant
sur l'**encodage canonique de la preuve OTS complète** ; liaison indirecte au même
manifeste et à `route_e_root` ; round dérivé **uniquement** du cutoff canonique `C` ;
ni `nTime`, ni `genTime`, ni le choix du jeton ne sélectionnent le round ;
`genTime + accuracy < C` avec marge pré-gelée ; absence d'`accuracy` sans borne officielle
gelée ⇒ **STOP** ; aucun retry, restamp, registre alternatif ou nouveau round ; plusieurs
manifests/cutoffs prépubliés sans règle déterministe ou first-write-wins ⇒ anti-reroll
**non prouvé**.

```text
public_registry_inclusion_proven = false
ANTI_REROLL                      = UNPROVEN
```

---

## 24. §12 — matrice de tests, quatorze groupes

| # | Groupe | Collectés | Passés | Échoués |
|---|---|---|---|---|
| 1 | baseline complète de `f152c3c` | 1277 | 1272 | **5 hérités** |
| 2 | audit des liaisons — **copie jetable** portant le patch, hors arbre livré | 673 | 664 | **9 attendus** |
| 3 | intégrité des quatre records historiques (`23a`, `23h`, `rs01_12`, `rs01_15`) | 4 | 4 | 0 |
| 4 | nouveau record et son pin | — | — | **sans objet : aucun record créé** |
| 5 | cinq vraies entrées | 33 | 33 | 0 |
| 6 | PRB / HR | 152 | 152 | 0 |
| 7 | A–F inchangé | 104 | 104 | 0 |
| 8 | vérificateur / adaptateur inchangés | 42 | 42 | 0 |
| 9 | sept fichiers de lignée acceptée | 673 | 673 | 0 |
| 10 | `tests/` hors mission | 946 | 941 | **5 hérités** |
| 11 | suite candidate complète | 1277 | 1272 | **5 hérités** |
| 12 | seconde exécution déterministe (4 fichiers mission, ×2) | 331 | 331 | 0 — **identique** |
| 13 | six mutations comportementales | — | — | **non exécutées : aucun crochet installé** |
| 14 | `go mod verify` + tentative sumdb | voir §22 | | |

`152 + 104 + 33 + 42 + 946 = 1277` — groupes disjoints, aucun double comptage.
`skipped = 0` · `xfail = 0` · `xpass = 0` · `deselected = 0` · `collection_errors = 0`.

**Les cinq échecs hérités**, identifiants, signatures et causes **inchangés** :

```text
tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[split]
tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[merge]
tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[tie]
tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[collapse]
tests/test_motile_polar.py::test_scramble_preserves_all_declared_invariants_and_destroys_organization
```

`new_failures = 0`. Aucun skip, xfail, deselection, défaut de collecte ni changement de
cause. **Ils ne sont jamais présentés comme verts.**

Le groupe 13 n'est pas escamoté : les six mutations supposent des crochets installés.
Les exécuter sur un arbre sans crochet produirait des mutants tués **uniquement par les
pins**, ce que le §9 exclut explicitement.

---

## 25. Déclaration finale de cet incrément

```text
guarded_entry_count                          = 0
behavioral_hook_mutations_killed             = 0   (non applicable : aucun crochet installé)
guard_signal_authoritative                   = false
accepted_entry_integration_present           = false
historical_qualification_files_modified      = 0
current_source_requalification_human_review  = PENDING   (aucun record créé)
public_registry_inclusion_proven             = false
sumdb_transparency_verified                  = false
ANTI_REROLL                                  = UNPROVEN
human_review                                 = PENDING
preregistration_authorized                   = false
scientific_run_authorized                    = false
```

Aucune fermeture humaine n'est prononcée. Aucune acceptation des six PRB n'est demandée.
La prochaine étape est une **décision propriétaire sur l'architecture** : rendre le signal
Route E incontournable exige d'agir sur `future_prospective_measurement_bridge.py`,
`stage_b.py` et `stage_b_reproduce.py` — trois fichiers hors de toute allowlist en cours —
ou de reconnaître explicitement que le garde des cinq fonctions ne fermera jamais PRB-5.
