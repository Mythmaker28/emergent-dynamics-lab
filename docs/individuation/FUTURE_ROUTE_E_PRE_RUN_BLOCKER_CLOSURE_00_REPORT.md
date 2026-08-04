# FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00 — rapport (intégration autorisée, après `0541400`)

> **Aucun token composite n'est émis.** Les faits sont exposés champ par champ au §2.
> Ce record ne prononce **aucune acceptation humaine**.
>
> `PRB-6 = CANDIDATE_CLOSED` — vérificateur BLS/G1 maintenu livré, vecteurs officiels
> hors réseau, round dérivé et vérifié cryptographiquement.
> `PRB-5 = OPEN` — le garde est **écrit et testé** mais **non installé** : le crochet
> d'une ligne change les octets de trois sources acceptées, épinglés par deux fichiers de
> tests **hors allowlist**. Blocker rapporté, non contourné.
> `ANTI_REROLL` : moitié « choix du round » **CANDIDATE_PASS**, moitié « publication »
> **UNPROVEN**.
>
> **`human_review = PENDING`** · **`scientific_run_authorized = false`**
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

**Aucun endpoint drand n'a été contacté. Aucun round live n'a été récupéré.** Chaque
vecteur a été copié d'une **fixture committée** dans un dépôt officiel, récupérée en
https depuis `raw.githubusercontent.com`, et `tests/data/route_e_beacon_vectors.json`
enregistre pour chacun : dépôt, ref, chemin, licence, sha256 du fichier source récupéré,
taille, chain hash, clé publique, scheme, round, signature, randomness, provenance de la
randomness, transformation (aucune) et résultat attendu.

| Id | Source | Chaîne | Round | Randomness |
|---|---|---|---|---|
| **V1** | `github.com/drand/tlock`, `tlock_test.go`, Apache-2.0 / MIT, sha256 `f2e71105…ef71` | **quicknet** | 12 040 883 | **dérivée** `sha256(sig)` |
| **V2** | `github.com/noislabs/drand-verify`, `src/verify.rs`, Apache-2.0, sha256 `47c7a755…f9a6` | **quicknet** | 123 | **dérivée** `sha256(sig)` |
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
