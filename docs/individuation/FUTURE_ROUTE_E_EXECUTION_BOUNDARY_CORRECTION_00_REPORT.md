# FUTURE_ROUTE_E_EXECUTION_BOUNDARY_CORRECTION_00 — rapport

> **Ce record ne prononce aucune acceptation humaine et n'autorise aucune donnée scientifique.**
>
> La stratégie des cinq gardes facultatifs est **retirée**. Elle est remplacée par une
> **entrée Route E dédiée, placée au-dessus du pont existant**, et par une **admission
> indépendante** qui décide, après coup et sans moteur, ce qui peut contribuer au dataset.
>
> La propriété revendiquée est exactement celle-ci :
> *aucun artefact ne contribue au dataset Route E, à un `Y_i` ou à `k` sans satisfaire
> intégralement le manifeste pré-run, l'enrôlement, le beacon, l'inventaire de tentatives et
> la vérification indépendante.*
> Il n'est **pas** revendiqué qu'on empêche quiconque d'appeler `LatticeBondEngine`, de copier
> le code ou de lancer une simulation exploratoire :
> `UNIVERSAL_ENGINE_EXECUTION_PREVENTION = NOT_CLAIMED`, littéralement.
>
> **`human_review = PENDING`** · **`pilot_authorized = false`** ·
> **`preregistration_authorized = false`** · **`scientific_run_authorized = false`**

---

## 1. Base et lignée

| Élément | Valeur |
|---|---|
| Base exclusive | `da0ec3f1e6198fcb25690cee02490f0d2ce9d034` |
| Parent attendu, vérifié | `f152c3c43d316cfbc4d7704fc91c69e51ee5fefa` ✔ |
| Différence base ↔ parent | exactement **2 `M`** : le REPORT et la DECISION de `…PRE_RUN_BLOCKER_CLOSURE_00` ✔ |
| Merge | **non** — la base a exactement 1 parent |
| Branche source | `codex/future-route-e-pre-run-blocker-closure-00-a1r-architectural-stop` |
| Branche de cet incrément | `codex/future-route-e-execution-boundary-correction-00` |
| Reconstruction depuis les rapports | **aucune** ; tous les objets requis sont présents dans le dépôt |

---

## 2. Décisions propriétaires appliquées telles quelles

```text
A1_R2_ALLOWLIST_EXTENSION            = REJECTED
PRB5_AS_WRITTEN                      = SUPERSEDED
FIVE_FUNCTION_GUARD_STRATEGY         = RETIRED
SELECTED_TOPOLOGY                    = NEW_DEDICATED_ROUTE_E_ENTRY_ABOVE_EXISTING_BRIDGE
ROUTE_E_SECURITY_BOUNDARY            = CANONICAL_EXECUTION_PLUS_INDEPENDENT_ADMISSION
UNIVERSAL_ENGINE_EXECUTION_PREVENTION = NOT_CLAIMED
```

**Aucun paramètre `route_e=None` n'a été ajouté à une fonction générique.** C'est vérifié
par `test_arch_03`, qui inspecte les cinq signatures réelles, et par `test_arch_04`, qui
vérifie que le pont ne contient ni `route_e` ni référence au nouveau module.

---

## 3. Pré-run et post-run sont deux objets différents

### 3.1 Racine pré-run `P`

`P = SHA-256( "EDLAB/ROUTE-E/PRE-RUN/v1\0" ‖ canonical_json(manifeste) )`.

Le manifeste lie exactement quinze champs, ni plus ni moins :

```text
canonical_cutoff_C · crash_retry_and_attempt_policy · designated_round_rule
distributions_and_draw_algorithm · experiment_id · fixture_class · kind · mode
outcome_and_claim_ceiling · output_namespace · protocol_and_analysis_digests
run_identity · sample_size_and_world_policy · schema_version · source_commit_and_digests
```

Une clé inconnue est refusée. **Une clé post-run, à n'importe quelle profondeur, est
refusée** : `seed`, `draw_plan`, `law_fields`, `initial_conditions`, `measurement_root`,
`join_digest`, `round`, `randomness`, `y`, `k`, `outcome`, `result`, `verdict`, … Le
refus est déclenché aussi bien par un **nom de clé** que par une **valeur de chaîne**
égale à l'un de ces termes.

Le round est dérivé de `C` **seul** :
`designated_round(C) = beacon_round_at_or_after(C + 86400)`, et
`designated_round_rule` doit être **littéralement** la règle épinglée. Le timestamp de la
preuve n'entre nulle part dans ce calcul.

Le seed est dérivé par **séparation de domaine** depuis `P` et la randomness vérifiée :

```text
seed_root = SHA-256( "EDLAB/ROUTE-E/SEED-FROM-PRE-RUN-ROOT/v1\0"
                     ‖ chain_hash ‖ round(8 o, big-endian) ‖ randomness(32 o) ‖ P )
```

Ce n'est **pas** un doublon de `frame.derive_seed_root`, qui lie un commit de
prérégistration : lier `P` est précisément la correction que cette mission apporte, car
c'est le manifeste — pas un commit — dont l'antériorité est prouvée. Aucun seed, round,
plan, loi ou condition initiale ne peut être injecté par l'appelant : `test_injection_01`
vérifie que la signature publique n'accepte aucun de ces noms.

### 3.2 Racine post-run `E`

`E = SHA-256( "EDLAB/ROUTE-E/POST-RUN/v1\0" ‖ canonical_json(enveloppe) )`.

L'enveloppe lie `P`, la preuve, la réponse beacon et le round vérifiés, le digest du seed
root, le plan de tirage et l'enrôlement complets, le snapshot des sources, l'ordre des
mondes, **toutes** les tentatives (succès, crashes, invalidités), les racines de mesure
de chaque monde, les joins et l'inventaire exact des fichiers.

**Les deux types sont non interchangeables** : préfixes de domaine différents **et**
`kind` différents (`route-e-pre-run-manifest/v1` contre `route-e-post-run-envelope/v1`).
Présenter une enveloppe comme un manifeste est refusé (`test_bundle_04`), et la même
valeur ne peut pas produire les deux racines (`test_arch_01`).

**Aucun cycle de hachage** : `worlds → attempts → file inventory → envelope → receipt`.
L'inventaire exclut explicitement les trois fichiers écrits après lui, et chaque objet ne
lie que ce qui le précède.

---

## 4. Entrée canonique

`edlab/substrates/lattice_bond/future_route_e_execution.py`

```python
run_route_e(pre_run_bundle_path, beacon_response_path, output_directory)
```

Trois paramètres, pas un de plus. Aucun callback de vérification, aucun booléen
d'autorisation, aucune loi, condition initiale, seed, round, root, tracking, outcome ou
résultat. Ordre gelé, les sept premières phases étant **purement calculatoires** :

```text
 1 READ_AND_CANONICALISE_BUNDLE      lecture, forme canonique exigée octet pour octet
 2 RECOMPUTE_PRE_RUN_ROOT            P recalculé depuis les octets relus
 3 VERIFY_ANTERIORITY                la preuve doit lier CE P et CE C
 4 DERIVE_ROUND_FROM_CUTOFF          round = f(C) uniquement
 5 VERIFY_BEACON                     vérificateur épinglé, cryptographie réelle
 6 DERIVE_SEED_PLAN_ENROLMENT        entièrement en mémoire
 7 CHECK_NAMESPACE_FIRST_WRITE_WINS  observation seule
──────────────────────────────────── PREMIER EFFET AUTORISÉ ──────────────────────────
 8 CREATE_OUTPUT_ROOT                mkdir atomique + persistance de l'enrôlement
 9 EXECUTE_WORLDS                    appel INTERNE de run_measurement_bridge
10 RECORD_ATTEMPTS                   inventaire append-only, aucun remplacement
11 SEAL_ENVELOPE                     inventaire, enveloppe, reçu
```

Le chemin valide **retourne un `RouteERunRecord`**. Il ne se termine pas par un
`raise "unreachable"` et ne dépend d'aucun booléen global qu'il faudrait basculer plus tard.

**Le vérificateur est épinglé par ses octets.** Son emplacement peut venir de
l'environnement, mais un binaire dont le SHA-256 n'est pas
`2534fa4a…3cca6d` (linux-amd64) ou `ea15b5de…20045c` (windows-amd64) **n'est pas un
vérificateur** : l'emplacement n'est donc pas un point d'injection (`test_injection_05`).
Un vérificateur absent ou non épinglé est un **STOP**, jamais un pass.

---

## 5. Admission indépendante

`edlab/substrates/lattice_bond/future_route_e_admission.py`

```python
verify_route_e_run(output_directory, final_receipt_path=None)
```

Elle relit **tous** les octets depuis le disque, recalcule `P`, le seed, le plan,
l'enrôlement, l'inventaire et `E`, **ne fait aucun pas moteur** (`test_arch_05` vérifie
que le module ne contient ni `LatticeBondEngine`, ni `from .engine import`, ni `.step(`),
et re-dérive les outcomes depuis l'évidence persistée.

**Elle ne croit aucun `Y_i`, aucun `k` et aucun verdict écrit par le runner.** Le runner
n'en écrit aucun, et l'admission **refuse** toute racine où un tel champ apparaît
(`RUNNER_WROTE_AN_ANSWER`, `test_reader_02`).

Re-dérivation honnête des outcomes, depuis `LIFECYCLE.json` seul :

| Évidence persistée | Disposition | `Y` |
|---|---|---|
| crash consigné dans l'inventaire | `TECHNICALLY_UNKNOWN` | **`None`** — jamais un 0 silencieux |
| un état terminal d'échec observé | `OBSERVED_FAILURE_*` | `0` |
| aucun enregistrement terminal | `MECHANICALLY_INELIGIBLE` | `0` |
| uniquement `RIGHT_CENSORED_AT_HORIZON` | `TECHNICALLY_UNKNOWN` | **`None`** |

La dernière ligne est le point délicat, et il est traité littéralement : la table gelée
scinde `RIGHT_CENSORED_AT_HORIZON` entre `SUCCESS` et
`OBSERVED_FAILURE_HORIZON_WITHOUT_REPLACEMENT` **selon une preuve de remplacement vérifiée**
que cette mission ne produit pas. L'ambiguïté est donc **nommée**, jamais résolue en
silence : `Y` reste inconnu, ni 1 ni 0.

Refus systématiques : inventaire incomplet, tentative supprimée, ordre modifié, fichier
ajouté ou retiré, digest divergent, enveloppe ou reçu discordants.

**Sorties refusées** — parce qu'aucune ne porte `ROUTE_E_PROVENANCE.json` avec le tag
canonique :

| Origine | Verdict | Preuve additionnelle |
|---|---|---|
| pont générique | `NOT_A_CANONICAL_ROUTE_E_ROOT` | le source du pont ne contient ni le nom ni le tag |
| `stage_b.py` | `NOT_A_CANONICAL_ROUTE_E_ROOT` | idem, et aucune référence `future_route_e` |
| `stage_b_reproduce.py` | `NOT_A_CANONICAL_ROUTE_E_ROOT` | idem, **et ses octets restent lisibles et intacts** |
| les cinq fonctions historiques | `NOT_A_CANONICAL_ROUTE_E_ROOT` | leurs sources ne contiennent ni le nom ni le tag |
| tag forgé | `NOT_A_CANONICAL_ROUTE_E_ROOT` | le tag doit être exactement le tag canonique |

Les seuils **42 / 9** ne sont **jamais** appliqués hors d'un run confirmatoire scientifique,
et les unités d'un pilote ou d'une fixture synthétique ne sont **jamais** ajoutées au `k`
confirmatoire (`test_scope_05`).

---

## 6. Anciens chemins : classés, non modifiés

```text
future_prospective_measurement_bridge.py = GENERIC_INTERNAL_COMPONENT
stage_b.py                               = LEGACY_EXECUTOR / OUT_OF_ROUTE_E
stage_b_reproduce.py                     = PRESERVED_INDEPENDENT_REPRODUCER
les cinq fonctions historiques           = GENERIC_OR_DOWNSTREAM / OUT_OF_ROUTE_E
```

Aucun de ces fichiers n'est modifié, et aucun ne reçoit de signal Route E.
`stage_b_reproduce.py` n'exécute aucun moteur et reste pleinement utilisable pour la
reproductibilité historique : lui refuser une **revendication Route E** ne touche pas ses
octets, ce que `test_inadmissible_03` vérifie explicitement.

---

## 7. Fichiers de cet incrément

| Chemin | État | Octets | SHA-256 |
|---|---|---|---|
| `edlab/substrates/lattice_bond/future_route_e_execution.py` | **ajouté** | 38 329 | `d766d59a9a8b4d273732c2cebefc1edc23e24a966fb94909eeb9f2642ea2b687` |
| `edlab/substrates/lattice_bond/future_route_e_admission.py` | **ajouté** | 23 150 | `8ece89e2140fc2b2b406917acce2707627117dce712da004ca45107fa71a6bcc` |
| `tests/test_future_route_e_execution_boundary_00.py` | **ajouté** | 44 419 | `063b47177a1f63fa11cad5cea794d8b0616444cdeb3e9c7ec0f2b24c232af7ab` |
| `…_CURRENT_SOURCE_QUALIFICATION.json` | **ajouté** | 8 559 | `89e824bd27703e8264d52f99b243679035b440a8b46eba6c6a91790a153c234d` |
| `…_REPORT.md` | ajouté | — | — |
| `…_DECISION.json` | ajouté | — | — |
| `docs/PROJECT_STATE.md` | modifié | réconciliation d'autorité seulement | — |
| `docs/DECISION_LOG.md` | modifié | réconciliation d'autorité seulement | — |

Le digest final du fichier de tests, ci-dessus, est la valeur **vérifiée hors bande** que le
record current-source ne peut pas contenir sans créer un cycle — exactement la convention
que le record `01R` accepté applique à son propre sélecteur.

Aucun autre fichier n'est touché. **Aucun faux run n'est créé** dans `EXPERIMENT_INDEX` ni
`RUN_INDEX`.

---

## 8. Qualifications et contrainte des 251 nœuds

Les quatre qualifications historiques restent **byte-identiques** :

```text
FUTURE_LIFECYCLE_CONTRACT_00_QUALIFICATION.json                  8f423bb0…5514ece
FUTURE_LIFECYCLE_CONTRACT_REQUALIFICATION_01R_QUALIFICATION.json 0752b86c…7061f403
FUTURE_LIFECYCLE_RUNNER_STACK_REQUALIFICATION_01_QUALIFICATION.json 509f27b2…fd6643a
FUTURE_LIFECYCLE_RUNNER_HARDENING_00_QUALIFICATION.json          f29da369…207f58df
historical_qualification_files_modified = 0
```

La collecte historique est **strictement inchangée** :

```text
node_count       = 251
node_list_sha256 = a425c3736f0b5d819ef708c2433b785cf706381798ffc48a7ce4b5941161276a
```

**Aucun test n'est ajouté, supprimé ou renommé dans les quatre sélecteurs.** Tous les
nouveaux tests vivent dans `tests/test_future_route_e_execution_boundary_00.py`, qui n'en
est pas un. `test_collection_14` recollecte les quatre sélecteurs depuis l'extérieur et
compare le compte et le SHA-256 ; `test_rs01_12`, à l'intérieur du sélecteur, fait la même
chose et reste vert.

**Ordre de qualification respecté, sans scellement intermédiaire :**

```text
code final → tests comportementaux finaux → record current-source append-only
           → pin littéral de ce record dans le nouveau fichier de test → REPORT et DECISION
```

Le pin est **littéral** (`89e824bd…c234d`), jamais recalculé depuis le fichier, jamais
wildcardé, jamais un préfixe, et il n'existe aucune découverte du « dernier record trouvé ».
Le record porte `human_review = PENDING` et `self_accepting = false` : il ne s'auto-accepte
pas.

---

## 9. Tests discriminants

`tests/test_future_route_e_execution_boundary_00.py` — **72 tests**, tous verts avec le
vérificateur épinglé présent.

| § | Exigence | Tests |
|---|---|---|
| 1 | bundle absent, faux type ou altéré ⇒ refus avant tout effet | `bundle_01…08` |
| 2 | preuve valide mais manifeste différent ⇒ refus | `bundle_05`, `bundle_06` |
| 3 | `P` contenant une donnée post-run ⇒ refus | `pre_run_01` (9 cas), `pre_run_02` |
| 4 | round ou seed injecté ⇒ impossible | `injection_01…05` |
| 5 | zéro `mkdir`, moteur ou écriture avant vérification | `no_effect_01` (5 cas), `no_effect_02`, `no_effect_03` |
| 6 | bundle synthétique valide ⇒ premier effet réellement atteint | `valid_01…03` |
| 7 | appel direct au pont ⇒ admission refusée | `inadmissible_01` |
| 8 | sortie Stage-B ⇒ admission refusée | `inadmissible_02` |
| 9 | reproducteur historique ⇒ refusé sans bloquer sa lecture | `inadmissible_03` |
| 10 | `P`, beacon, plan, monde, join, crash ou inventaire modifiés ⇒ `E` invalide | `tamper_01` (10 cas), `tamper_02`, `tamper_03` |
| 11 | lecteur indépendant, recomputation sans moteur | `reader_01…03` |
| 12 | pilote et confirmation disjoints | `scope_01…06` |
| 13 | les cinq échecs hérités restent identiques | `historical_13`, `historical_13b` |
| 14 | collecte sélectionnée toujours 251, même SHA-256 | `collection_14`, `collection_14b` |

`no_effect_01` et `no_effect_02` sont les plus durs : ils **arment `os.mkdir` et le pont
pour exploser**, puis exigent que le refus arrive quand même — et, pour `no_effect_02`,
que la phase du refus soit **exactement** `CREATE_OUTPUT_ROOT`, ce qui prouve que rien
n'a été écrit avant.

**Vérificateur absent** : 47 passent, 22 sont ignorés avec la raison explicite
« aucun vérificateur dont les octets correspondent au build reproductible épinglé ».
La convention est celle, déjà acceptée, de `tests/test_route_e_beacon_verifier.py` : le
binaire n'est délibérément pas committé, et **les deux branches affirment quelque chose de
réel** — sans vérificateur, le run est refusé à `VERIFY_BEACON` et rien n'est écrit.

---

## 10. Campagne mutationnelle unique

Cinq mutations sémantiquement valides, **pins documentaires exclus** de la campagne
(`historical_13`, `collection_14`). Aucun mutant n'est compté comme tué par un hash, une
signature, un import, une erreur de syntaxe, un `TypeError` ou une collecte cassée.

| Mutation | Tués | Tueurs comportementaux (extraits) |
|---|---|---|
| vérification déplacée **après** le premier effet (`mkdir` en tête de fonction) | **47** | `bundle_01…08`, `pre_run_01`, `no_effect_01`, `injection_03` — tous perdent le refus attendu |
| liaison de `P` retirée (la preuve n'a plus à lier la racine) | **2** | `bundle_05_an_altered_manifest_invalidates_its_own_proof`, `no_effect_01[altered_manifest]` |
| seed injectable (repris du manifeste s'il est présent) | **7** | `tamper_00`, `reader_01`, `scope_06`, `tamper_02`, `tamper_03` — le seed recalculé ne correspond plus |
| sortie générique admise (l'exigence de provenance disparaît) | **3** | `inadmissible_01`, `inadmissible_02`, `inadmissible_03` |
| crash omis de l'inventaire | **2** | `tamper_02_a_crash_removed_from_the_inventory_is_detected`, `tamper_03` |

Chaque mutant est tué par la **perte de l'exception Route E attendue** ou par
**l'admission d'une chose qui devait être refusée**. Aucun n'est tué par un pin.

---

## 11. Matrice de tests

| Groupe | Collectés | Passés | Échoués |
|---|---|---|---|
| nouveau fichier, vérificateur **présent** | 72 | 72 | 0 |
| nouveau fichier, vérificateur **absent** | 69 | 47 | 0 (22 ignorés, raison explicite) |
| PRB / HR (`…pre_run_locks_00`) | 152 | 152 | 0 |
| A–F (`…blocker_closure_00`, inchangé) | 104 | 104 | 0 |
| garde et cinq entrées (`…pre_run_integration_00`) | 33 | 33 | 0 |
| vérificateur et adaptateur (inchangés) | 42 | 42 | 0 |
| sept fichiers de la lignée acceptée | 673 | 673 | 0 |
| quatre sélecteurs, collecte seule | 251 | — | — |
| **suite complète** | **1349** | **1344** | **5 hérités** |

Les cinq échecs hérités conservent **exactement** leurs identifiants, signatures et causes :

```text
tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[split]
tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[merge]
tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[tie]
tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[collapse]
tests/test_motile_polar.py::test_scramble_preserves_all_declared_invariants_and_destroys_organization
```

`new_failures = 0`. Aucun défaut de collecte, aucun changement de cause, aucun `xfail`,
aucune deselection. **Ils ne sont jamais présentés comme verts.**

---

## 12. Firewall scientifique

```text
scientific_run_performed      = false      scientific_seed_created   = false
scientific_family_executed    = false      scientific_namespace      = none
drand_contacted               = false      live_round_consulted      = false
results_directory_walked      = false      preregistration_started   = false
```

La **seule** exécution moteur de cette mission est une fixture temporaire, déclarée
`SYNTHETIC_NON_SCIENTIFIC`, d'**un** monde sur un réseau 16×16 avec un calendrier de trois
trames, dans le `tmp_path` de pytest. Son namespace doit commencer par
`SYNTHETIC-NONSCI-`, et l'admission la déclare non contributive **par construction** :
`contributes_to_k = false`, quels que soient ses chiffres. Le round consommé est le
**123**, celui de la fixture quicknet **committée** V2 ; aucun endpoint drand n'est contacté.

---

## 13. A2 — gelée, non implémentée

```text
public_registry  = Bitcoin mainnet via complete OpenTimestamps proof
signed_time      = Sigstore RFC 3161 timestamp over canonical completed OTS proof
acceptance_rule  = OTS AND RFC3161            (jamais OTS OR RFC3161)
```

Aucune racine publiée, aucun registre contacté. Le type de preuve `OTS_PLUS_RFC3161` est
**reconnu et refusé** : son vérificateur n'existe pas encore, donc un run qui le revendique
est arrêté plutôt que cru (`test_bundle_07`). Le seul type utilisable aujourd'hui est
`SELF_ATTESTED_NON_PUBLIC`, qui lie `P` et `C` structurellement, ne peut **jamais**
revendiquer une inclusion publique (`test_bundle_08`), et dont l'admission conclut que la
racine ne peut pas contribuer au dataset.

```text
public_pre_run_inclusion_proven = false
```

---

## 14. Déclaration finale factuelle

```text
architecture_cycle_removed               = true
pre_run_root_distinct_from_post_run_root = true
single_route_e_execution_api_present     = true
pre_effect_authorization_verified        = true
generic_bridge_outputs_admissible        = false
legacy_stage_b_outputs_admissible        = false
stage_b_reproduce_preserved              = true
selected_node_set_unchanged              = true
historical_qualification_files_modified  = 0
public_pre_run_inclusion_proven          = false
human_review                             = PENDING
pilot_authorized                         = false
preregistration_authorized               = false
scientific_run_authorized                = false
```

Aucune fermeture humaine n'est prononcée. La seule étape suivante est **une revue humaine
indépendante** de cet incrément.
