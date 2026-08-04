# FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00 — rapport (révision corrective après `31cccc`)

> **Aucun token de disposition composite n'est émis.** Les faits sont exposés séparément,
> champ par champ, au §2. Ce record ne prononce **aucune acceptation humaine**.
>
> `PRB-5 = OPEN` · `PRB-6 = OPEN` · `ANTI_REROLL = UNPROVEN`
>
> **`scientific_run_authorized = false`**
>
> Il est **interdit** de résumer ce package par « les pre-run blockers sont fermés », ou
> par « cinq blockers sur six sont fermés ».

---

## 0. Les quatre catégories, tenues séparées

1. **Preuves mécaniques** — tests exécutés et mutations discriminantes, §10.
2. **Décisions de gouvernance** — les verrous, l'ordre gelé, les préconditions, ce qui est
   déclaré hors protocole.
3. **Limitations et conflits d'allowlist** — `LK-L1 … LK-L5`, `RE-L1 … RE-L10`, plus les
   sous-obligations restantes par blocker, §12.
4. **Résultats scientifiques** — **catégorie vide.**

---

## 1. Autorité, lignée, base

| Élément | Valeur |
|---|---|
| Mandat | `00afcdd1aacbdf32bb030d85ced735a2920421f6`, §8 |
| Candidat partiel initial | `c6d4acf037d4e51d59e5b75dc91b977b9eb83dbd` |
| Première revue contraignante | `bc2a42c468eec5a4e1732ebb08c7cc20c4dab7dd` — `HUMAN_REVIEW_REVISE` |
| Candidat révisé | `a379efa6e230efd6b4051b36717169be9c0f5dbf` |
| **Revue indépendante contraignante** | `31ccccfb9e61809cf5d461a70425e00c3db7bc17` — `HUMAN_REVIEW_REVISE` |
| Base de cette révision | `31ccccfb…`, **parent unique**, aucun merge |
| Mission | `FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00`, **non consommée** |
| Branche Git | `codex/future-route-e-pre-run-blocker-closure-00-revision-2` — nom Git, **pas** un identifiant scientifique |

### 1.1 La portée du §8, maintenue intégralement

> **Obligations portées à la prérégistration** (`ROUTE_E_REPLICATION_DENSITY_PREREGISTRATION_00`),
> à n'exécuter qu'après fermeture **et** revue humaine des blockers : 1. … 6.

et, du mandat de cette mission :

> `FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00` **pourra** fermer les six `PRE_RUN_BLOCKER`.

**Deux couches, deux missions.** A–F appartiennent à la prérégistration et restent du
travail **anticipatoire** ; `PRB-1 … PRB-6` sont le mandat de cette mission. Aucun
renommage `A→1`, aucun identifiant `00R`, aucune mission nouvelle, aucune prérégistration.

### 1.2 État de départ, non réécrit

```text
PRB-1 = PARTIAL           PRB-4 = CANDIDATE_CLOSED_AT_DIGEST_LEVEL
PRB-2 = STRUCTURAL_ONLY   PRB-5 = OPEN
PRB-3 = PARTIAL           PRB-6 = OPEN
HR-10 = PARTIAL           ANTI_REROLL = UNPROVEN
```

---

## 2. Disposition — champs factuels séparés, sans token

| Fait | Valeur |
|---|---|
| Mécanisme présent | PRB-1 **oui** · PRB-2 **oui** · PRB-3 **oui** · PRB-4 **oui** · PRB-5 **non** · PRB-6 **gate seul** |
| Persistance présente | PRB-1 **oui** (écriture atomique + relecture + recomputation) |
| Intégration dans une source acceptée | **non**, pour les six, sans exception |
| Tests discriminants présents | PRB-1 **oui** · PRB-2 **oui** · PRB-3 **oui** · PRB-4 **oui** · PRB-5 **oui, pour la propriété faible seulement** · PRB-6 **oui** |
| Authenticité cryptographique établie | **non** — dépend de `PRB-6` |
| Sous-obligations restantes | §4 à §8, et `blocker_status()` |
| Revue humaine encore requise | **oui, pour les six** |
| Autorisation scientifique | **false** |

`blocker_status()` ne renvoie **plus aucun champ `closed`** : il renvoie ces faits, un par
un, avec `human_review_required = True` partout. Le champ `candidate_disposition` et le
token `ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_MANDATE_ADDRESSED_PRB6_OPEN` sont **supprimés**
du `DECISION.json`. Aucun schéma fictif n'a été créé pour donner à ces champs une
apparence canonique : ce sont des faits, pas un vocabulaire.

---

## 3. Allowlist littérale, chemin par chemin

Écrite avant la première édition, depuis les textes gelés.

| # | Chemin | Statut | Justification |
|---|---|---|---|
| 1 | `edlab/substrates/lattice_bond/future_route_e_pre_run_locks.py` | modifié | mécanisme des six `PRE_RUN_BLOCKER` (fichier créé par cette mission) |
| 2 | `edlab/substrates/lattice_bond/future_route_e_pre_run_frame.py` | modifié | HR-10 : suppression du paramètre `classifier` de l'API publique |
| 3 | `tests/test_future_route_e_pre_run_locks_00.py` | modifié | tests PRB/HR corrigés + refus sur les cinq **vraies** fonctions |
| 4 | `docs/individuation/FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_REPORT.md` | modifié | ce rapport |
| 5 | `docs/individuation/FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_DECISION.json` | modifié | cette décision |

**Non modifiés** : `engine.py`, `specs.py`, `state.py`, `instrumentation.py`,
`lifecycle.py`, `future_lifecycle_runner.py`, `future_lifecycle_owned_pipeline.py`,
`future_prospective_measurement_bridge.py`, tout `__init__.py`, `pyproject.toml`, tout
test préexistant, `tests/test_future_route_e_pre_run_blocker_closure_00.py` (A–F,
**inchangé** depuis `a379efa6`), tout document 01S, et **les deux records humains
`bc2a42c4` et `31ccccfb`**.

### 3.1 Matrice obligation → chemin d'exécution → fichier → statut atteignable

| Obligation littérale | Chemin d'exécution réel | Fichier nécessaire | Autorisé ? | Mécanisme | Test discriminant | Statut atteignable |
|---|---|---|---|---|---|---|
| PRB-1 *write the join into root-bound evidence* | écriture → relecture → recomputation | `future_route_e_pre_run_locks.py` | **oui** | `write_join_evidence` / `read_join_evidence` | writer → no-op ⇒ **13 rouges** | mécanisme **et** persistance livrés ; **intégration non** |
| PRB-2 couches 1–2 (présence, liaison à la racine recomputée) | chemin Route E | `future_route_e_pre_run_locks.py` | **oui** | `_frozen_check_order` | recomputation retirée ⇒ rouge | livré |
| PRB-2 *the supported entry point refuses without a receipt* | à l'intérieur des cinq fonctions acceptées | `future_lifecycle_*.py`, `lifecycle.py` | **NON** | — | — | **impossible** sous l'allowlist |
| PRB-2 couche 3 (authenticité) | vérificateur BLS maintenu | `pyproject.toml` + lockfiles | **NON** | — | — | **impossible** : c'est PRB-6 |
| PRB-3 *frozen check order* | chaque API publique Route E | `future_route_e_pre_run_locks.py` | **oui** | un seul `_frozen_check_order` | phase retirée ⇒ **7 rouges** ; cutoff optionnel ⇒ **3 rouges** | livré pour le chemin Route E |
| PRB-4 *replay binding* | algèbre de digest | `future_route_e_pre_run_locks.py` | **oui** | `FamilyEnrolment` → `route_e_root` | mutation de champ ⇒ racine différente | **niveau digest seulement** |
| PRB-5 *refusal test on the five entry points* | à l'intérieur des cinq fonctions | `future_lifecycle_*.py`, `lifecycle.py` | **NON** | — | refus réel neutralisé ⇒ **1 à 2 rouges par fonction** | **OPEN** |
| PRB-6 *external anchoring* | vérificateur BLS/G1 maintenu | `pyproject.toml`, `go.mod`, `go.sum`, adaptateur, vecteurs | **NON** | gate fail-closed seul | absence de vérificateur ⇒ STOP | **OPEN** |
| HR-10 *classifieur non substituable* | API publique d'assemblage | `future_route_e_pre_run_frame.py` | **oui** | `classifier` retiré, seam privé | appel retiré ⇒ **3 rouges** | livré ; **intégration non** |

**Conflit d'allowlist, énoncé sans détour :** les quatre lignes marquées **NON** sont les
seules qui fermeraient réellement PRB-2 (authenticité), PRB-5 et PRB-6. Aucun fichier
interdit n'a été touché. Les extensions exactes nécessaires sont demandées au §11.

---

## 4. PRB-1 — évidence persistée, complète et liée

Ce qui est **livré** :

- **Couverture exacte du support.** `build_track_component_join` refuse quatre défauts
  distincts, chacun **avant toute écriture** : assignation orpheline (`orphan
  assignment`), composant détecté non assigné (`incomplete join`), clé `(frame, index)`
  dupliquée, deux triples identiques. La politique sur les doublons est **le refus**,
  déclarée comme telle, jamais l'absorption silencieuse par le digest.
- **Sérialisation canonique.** `canonical_join_bytes` produit exactement les octets écrits
  **et** digérés : `join_digest(records) == sha256(canonical_join_bytes(records))`. Les
  lignes sont triées, donc permuter l'entrée donne des octets identiques.
- **Écriture atomique et bornée.** `write_join_evidence` refuse une racine absente, une
  racine qui est un lien symbolique, un chemin sortant de la racine (`realpath`), et toute
  réécriture. L'écriture passe par un fichier temporaire dans la même racine, `fsync`,
  puis `os.link` — **non écrasant**. Sans lien atomique disponible, le writer refuse au
  lieu de dégrader silencieusement.
- **Relecture obligatoire.** `read_join_evidence` refuse un lien symbolique, un fichier
  absent, du JSON non canonique, et tout ce qui ne fait pas un aller-retour octet pour
  octet. Le digest renvoyé est `sha256` **des octets lus sur le disque**.
- **Liaison à la racine.** `_frozen_check_order` recompute `route_e_root` depuis le digest
  **relu**, jamais depuis un objet resté en mémoire ni depuis une chaîne d'appelant.

Ce qui **reste ouvert** : aucune source acceptée n'appelle ce writer. L'évidence n'existe
que si un appelant Route E l'écrit — `LK-L5`.

---

## 5. PRB-2 — présence, liaison et authenticité, séparées

| Couche | Statut | Preuve |
|---|---|---|
| 1. Présence et forme minimale du receipt | **livrée** | `ENTRY_GUARD` refuse `None` et tout objet d'un autre type, **avant tout effet** ; sa racine n'est ni lue ni crue à ce stade |
| 2. Recomputation interne de la racine | **livrée** | plus **aucune** signature publique n'accepte de racine fournie par l'appelant (`test_prb2_04`) |
| 3. Liaison receipt ↔ racine recomputée | **livrée** | receipt auto-cohérent sur une racine mensongère **rejeté** (`test_prb2_05`) ; évidence mutée après émission ⇒ invalide (`test_prb2_06`) ; enrôlement différent ⇒ liaison cassée (`test_prb2_07`) |
| 4. Antériorité publique obligatoire | **livrée** | `must_precede_unix` n'a **plus de défaut `None`** ; absence ⇒ refus sur les deux chemins publics |
| 5. Authenticité cryptographique de la provenance | **OUVERTE** | dépend de `PRB-6` ; aucun vérificateur maintenu n'existe dans l'allowlist |

Ordre effectivement imposé, identique sur les deux entrées publiques :

```text
ENTRY_GUARD (receipt présent, cutoff présent — rien n'est cru)
  → LOCAL_EVIDENCE        (relecture de l'artefact persisté)
  → ROOT_DIGEST           (racine RECOMPUTÉE depuis les octets relus)
  → RECEIPT_ROOT_BINDING
  → VERIFIER              (commitment vérifié, antériorité stricte)
```

**Ce que PRB-2 ne ferme pas, et pourquoi.** Le texte gelé dit « **the supported scientific
entry point** refuses without a verified receipt ». Les trois modules acceptés ne
contiennent **aucune** occurrence de `RouteEReceipt`, `route_e_entry` ou
`future_route_e_pre_run_locks` — vérifié par test (`test_prb5_real_03`). Le receipt est
donc exigé par des fonctions Route E qu'aucun chemin de production n'appelle. Ce n'est
**pas** une fermeture par vacuité invoquant `scientific_run_authorized = false` : c'est un
conflit d'allowlist, nommé au §3.1 et au §11.

---

## 6. PRB-3 — un ordre unique sur tous les chemins publics

- **Un seul chemin interne**, `_frozen_check_order`, utilisé par `open_route_e_analysis`
  **et** par `route_e_entry` (`test_prb3_05`).
- `LOCAL_EVIDENCE → ROOT_DIGEST → VERIFIER` reste l'ordre gelé ; `CHECK_PHASES` en donne
  la réalisation (`ENTRY_GUARD` en préflight qui ne croit rien, `RECEIPT_ROOT_BINDING`
  comme sous-étape de `VERIFIER`), **sans réordonner ni supprimer** les trois phases
  gelées (`test_prb3_01`).
- Échec d'évidence ⇒ racine et vérificateur **jamais** atteints, prouvé par espion
  (`test_prb3_02`). Échec de liaison ⇒ vérificateur jamais atteint (`test_prb2_03`).
  Succès synthétique ⇒ journal exact des cinq étapes, vérificateur appelé **exactement une
  fois** (`test_prb3_03`).
- `must_precede_unix` **obligatoire**, sans défaut, sur les deux entrées, et propagé par
  `route_e_entry` (`test_prb3_06`, `test_prb3_07`).
- L'appel direct à `_OrderTrace` subsiste (`test_prb3_04`) mais **n'est plus le test
  principal** : les tests principaux instrumentent les vraies frontières.

`route_e_entry` est **requalifié en façade de protocole**. Le module le déclare
(`FACADE_IS_NOT_A_GATE`, `LK-L4`) : elle n'est pas dans le call graph des cinq fonctions,
n'en importe aucune, ne peut intercepter aucun appel direct, et **aucun test de la façade
n'est une preuve à leur sujet**.

---

## 7. PRB-5 — les cinq vraies fonctions, testées ; le blocker reste OUVERT

Les cinq entrées littérales du mandat sont testées **en appelant la vraie fonction
publique**, dans un contexte Route E non autorisé, sous `ForbiddenEffects` armant
entropie, réseau, sous-processus, `open`, **lecture** (`Path.read_bytes` / `read_text`),
écriture, `mkdir` et `LatticeBondEngine.step` :

| Vraie fonction publique | Exception typée observée | Effet atteint |
|---|---|---|
| `future_lifecycle_owned_pipeline.run_owned_future_pipeline` | `OwnedPublicationError` | **aucun** |
| `future_lifecycle_owned_pipeline.open_owned_analysis_access` | `OwnedEvidenceError` | **aucun** |
| `future_lifecycle_runner.open_analysis_access` | `CompletionEvidenceError` | **aucun** |
| `future_lifecycle_runner.publish_future_family_completion` | `CompletionPublicationError` | **aucun** |
| `lifecycle.qualify_and_write_lifecycle_contract` | `LifecyclePublicationError` | **aucun** |

`ForbiddenEffects.hits == []` et le répertoire temporaire est **vide** après chaque refus.

**Pouvoir discriminant, mesuré** (copies jetables, jamais committées) : neutraliser le
refus **à l'intérieur** de chacune des cinq fonctions rend son test **rouge** — 2, 1, 1, 2
et 2 échecs respectivement. Les deux qui n'en tuent qu'un possèdent un **second** refus
fail-closed en aval (« no owned pipeline binding … », « no completion manifest … »), que
le test de message capture.

**Pourquoi le blocker reste OUVERT, sans échappatoire.** Ces refus sont le **premier
contrôle propre à chaque fonction**, pas un refus Route E : `run_directory must already
exist`. Le texte gelé exige « close or declare out of protocol, **with a refusal test** »
sur ces cinq noms ; la déclaration hors protocole existe (`OUT_OF_PROTOCOL_ENTRY_POINTS`)
et les cinq tests existent désormais, mais **aucun mécanisme Route E ne vit à l'intérieur
de ces fonctions**, et en installer un signifie éditer une source acceptée, ce que
l'allowlist gelée interdit. **`PRB-5 = OPEN`.** Aucune fermeture n'est fabriquée avec des
tests seuls.

Recherche des façades alternatives : aucun export, CLI, runner ou point d'entrée
alternatif n'a été trouvé qui ouvrirait la même capacité sans passer par ces cinq
fonctions.

---

## 8. PRB-6 — inchangé, OUVERT, et rien n'a été installé

Aucune modification de `pyproject.toml`, aucun `go.mod`, aucun `go.sum`, aucun lockfile,
aucune installation, **aucun contact drand**, aucun round choisi, aucune BLS artisanale.

Les gates fail-closed sont préservés : absence de vérificateur ⇒ **STOP** ; verdict
non-`True`, vérificateur qui lève, `randomness ≠ sha256(signature)`, mauvaise chaîne,
mauvais round, longueurs non conformes (G1 48 o, G2 96 o) ⇒ **STOP** ; indisponibilité
authentique ⇒ **WAIT** sur le **même** round, jamais le suivant, jamais un autre endpoint,
jamais une autre source.

```text
PRB-6 = OPEN
ANTI_REROLL = UNPROVEN
```

La demande d'autorisation d'ingénierie étroite, avec les chemins exacts, est au §11.2.

---

## 9. HR-1 … HR-11

| ID | Correctif local | Propriété globale |
|---|---|---|
| HR-1 | **PASS**, inchangé | censure disjointe, disposition unique |
| HR-2 | **PASS**, inchangé + preuve exhaustive sur les 2 346 couples `(S, U)` | aucune décision non fondée |
| HR-3 | **PASS**, inchangé | **`ANTI_REROLL = UNPROVEN`**, conditionné par `PRB-6` |
| HR-4 | **PASS** ; cas négatifs élargis à neuf réponses malformées | aucun vérificateur livré |
| HR-5 | **PASS**, inchangé | WAIT / STOP strictement séparés |
| HR-6 | **PASS**, inchangé | biais modulo **supprimé**, pas borné |
| HR-7 | **PASS**, inchangé | preuve analytique du rejet |
| HR-8 | **PASS**, inchangé | dénominateur exactement 67 aux deux points d'application |
| HR-9 | **PASS** ; l'alias `check_claim_within_ceiling` est conservé mais documenté comme l'aide **rétrogradée** | plafond exécutoire = `RouteEClaim` |
| **HR-10** | **CORRIGÉ** : le paramètre `classifier` est **retiré** de l'API publique ; le seam vit dans `_assemble_draw_outcome`, privé et non ré-exporté ; le passer publiquement lève `TypeError` | **intégration toujours absente** : aucune source acceptée n'appelle l'assembleur — déclaré dans le docstring et dans `RE-L10`, non caché |
| HR-11 | **PASS**, inchangé | titre et portée du §8 restitués |

---

## 10. Tests réellement exécutés — périmètres nommés, aucun total préannoncé

Clean-room ; Python **3.11.15**, pytest **8.4.2**, numpy **2.4.4**. Aucun réseau, aucun
contact drand, aucune donnée historique, aucun moteur scientifique.

| # | Commande exacte | Périmètre | Collectés | Passed | Failed |
|---|---|---|---|---|---|
| 1 | `pytest tests -q` **sur la base `31cccc`** | dépôt entier, base | **1 206** | 1 201 | **5** |
| 2 | `pytest tests/test_future_route_e_pre_run_locks_00.py -q` | PRB + HR corrigés | **191** | 191 | 0 |
| 3 | `pytest tests/test_future_route_e_pre_run_blocker_closure_00.py -q` | A–F (fichier inchangé) | **104** | 104 | 0 |
| 4 | `pytest -q <les sept fichiers nommés>` | **régression sur la lignée acceptée** : `test_future_lifecycle_contract`, `test_future_lifecycle_runner_integration`, `test_empty_right_nonunit_cadence_tracker_repair`, `test_future_lifecycle_owned_pipeline`, `test_future_prospective_measurement_bridge`, `test_axis_transpose_equivariance_01s`, `test_lattice_bond_instrumentation` | **673** | 673 | 0 |
| 5 | `pytest tests -q --ignore=<locks> --ignore=<A–F>` | `tests/` **moins** les fichiers de mission | **946** | 941 | **5** |
| 6 | `pytest tests -q` | **suite candidate entière** | **1 241** | 1 236 | **5** |
| 7 | `pytest <locks> <A–F> -q`, deux fois de suite | déterminisme | 295 | 295 | 0 |

`191 + 104 + 946 = 1 241` : groupes **disjoints**, aucun double comptage.
**0 skip, 0 xfail, 0 xpass, 0 deselected, 0 erreur de collecte** partout.

**933 n'est pas la suite totale** et n'est plus employé. Le nombre 673 désigne désormais
explicitement la **régression sur la lignée acceptée (sept fichiers nommés)**, jamais « la
suite entière moins deux fichiers ».

### 10.1 Mutations discriminantes (copies jetables, jamais committées)

| Mutation | Effet sur les tests |
|---|---|
| PRB-1 : `write_join_evidence` remplacé par un no-op | **13 rouges** |
| PRB-3 : phase `LOCAL_EVIDENCE` retirée du chemin unique | **7 rouges** |
| PRB-3 : `must_precede_unix` redevenu optionnel | **3 rouges** |
| HR-10 : appel au classifieur retiré du chemin public | **3 rouges** |
| PRB-5 : refus retiré dans `run_owned_future_pipeline` | **2 rouges** |
| PRB-5 : refus retiré dans `open_owned_analysis_access` | **1 rouge** |
| PRB-5 : refus retiré dans `future_lifecycle_runner.open_analysis_access` | **1 rouge** |
| PRB-5 : refus retiré dans `publish_future_family_completion` | **2 rouges** |
| PRB-5 : refus retiré dans `qualify_and_write_lifecycle_contract` | **2 rouges** |
| Contrôle : `route_e_entry` remplacé par un stub qui ne fait rien | **2 rouges** parmi les tests d'ordre (`prb3`) — la façade est donc réellement épinglée au chemin unique ; les tests de façade passent encore, ce qui est **attendu et déclaré**, et les tests des cinq vraies fonctions sont **inchangés**, ce qui est exactement la séparation voulue |

### 10.2 Les cinq échecs hérités

```text
tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[split]
tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[merge]
tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[tie]
tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[collapse]
    TypeError: track_components() missing 1 required keyword-only argument: 'sampled_frames'
tests/test_motile_polar.py::test_scramble_preserves_all_declared_invariants_and_destroys_organization
    AssertionError: support overlaps its own translate: displacement would not conserve mass
```

Ensemble **strictement identique** entre la base `31cccc` et ce candidat :
**`new_failures = 0`**. Ce sont des rouges **préexistants**, mais cela **n'en fait pas des
tests verts**. Les fichiers en cause (`tests/test_lattice_bond_stage_b.py`,
`tests/test_motile_polar.py`, `edlab/substrates/lattice_bond/instrumentation.py`,
`edlab/experiments/exp_mo_00_gate0.py`) sont **hors allowlist** de cette mission : la
dette ne peut pas être réparée ici. **Décision explicite du propriétaire demandée** au
§11.3. Cette révision **n'invente aucune dérogation**.

---

## 11. Autorité demandée

### 11.1 Intégration réelle de PRB-2 et PRB-5

Extension d'allowlist strictement limitée à un refus Route E **à l'intérieur** des cinq
fonctions acceptées :

```text
edlab/substrates/lattice_bond/future_lifecycle_owned_pipeline.py
edlab/substrates/lattice_bond/future_lifecycle_runner.py
edlab/substrates/lattice_bond/lifecycle.py
```

Portée demandée : ajouter, en **première** vérification de chacune des cinq fonctions
publiques, un refus Route E fail-closed (receipt vérifié requis, sinon exception dédiée),
sans changer aucun comportement existant lorsque le refus ne se déclenche pas. Aucune
autre modification.

### 11.2 Fermeture de PRB-6

Chemins exacts à ajouter, aucun autre :

```text
tools/drand_verify/main.go                                helper Go hors réseau, vérificateur drand v2
tools/drand_verify/go.mod                                 dépendances épinglées
tools/drand_verify/go.sum                                 hachages
edlab/substrates/lattice_bond/route_e_beacon_verifier.py  adaptateur Python, sans shell
tests/data/route_e_beacon_vectors.json                    table de vecteurs hors réseau
tests/test_route_e_beacon_verifier.py                     tests, dont tous les cas négatifs
pyproject.toml                                            uniquement si drand-verify est retenu comme oracle secondaire
```

Épinglage obligatoire du futur chemin Quicknet :

```text
scheme      = bls-unchained-g1-rfc9380
public key  = G2, 96 bytes
signature   = G1, 48 bytes
message     = SHA256(uint64_be(round))
DST         = BLS_SIG_BLS12381G1_XMD:SHA-256_SSWU_RO_NUL_
randomness  = SHA256(signature)
```

Cas négatifs obligatoires : signature altérée ; round ±1 ; mauvaise chaîne ou clé ;
**DST fastnet appliqué à un round Quicknet** ; randomness incohérente ; point à l'infini ;
point hors sous-groupe ; encodage non canonique ; helper absent, mal configuré ou crashé ;
indisponibilité authentique ⇒ **WAIT** sur le même round ; invalidité ou vérification
impossible ⇒ **STOP**.

Points **non résolus** depuis les sources primaires, à trancher avant implémentation : le
chemin de désérialisation exact de la version épinglée de `kyber-bls12381`
(`FromCompressed`, avec contrôles de sous-groupe, point à l'infini et encodage canonique,
plutôt que `FromBytes`) ; la provenance et les checksums du binaire ; l'existence d'un jeu
de vecteurs officiel versionné par drand pour ce schéma ; le modèle d'entrée/sortie JSON
borné et fail-closed de l'adaptateur. **Aucune recherche n'a impliqué d'installation ni de
requête de beacon.**

### 11.3 Dette héritée des cinq rouges

Deux options, au choix du propriétaire — cette révision n'en choisit aucune :

1. autorisation étroite d'ajouter `tests/test_lattice_bond_stage_b.py`,
   `tests/test_motile_polar.py` et les sources concernées à l'allowlist pour les réparer ;
2. décision formelle de les traiter comme **baseline héritée** déclarée, avec le mandat
   historique « zéro fail » explicitement borné au périmètre de la lignée acceptée.

---

## 12. Limitations

**Verrous** — `LK-L1` sources acceptées immuables, donc tout verrou est **en amont**
d'elles ; `LK-L2` aucun vérificateur BLS empaqueté, donc l'authenticité de PRB-2 reste
ouverte ; `LK-L3` la racine Route E **lie** la racine de mesure, elle ne la remplace pas ;
`LK-L4` `route_e_entry` est une **façade**, pas un gate, et n'est pas dans le call graph
des cinq fonctions ; `LK-L5` **rien** dans ce module n'est appelé par une source acceptée.

**Cadre A–F** — `RE-L1` … `RE-L9` inchangés ; `RE-L10` nouveau : `assemble_draw_outcome`
appelle toujours le vrai classifieur et n'a plus de paramètre `classifier`, mais reste
**anticipatoire** — aucune source acceptée ne l'appelle, donc
`ASSOCIATION_GATE_TRACK_BREAK` demeure une **convention**, pas une intégration, et la
cause ne doit pas être attribuée au tracker de production.

**Preuve** — les mutations sont conduites dans des copies jetables sous `/tmp`, jamais
committées. Les tests d'écriture utilisent `tmp_path` uniquement. `ForbiddenEffects`
couvre la liste énumérée et **rien de plus** : ce n'est pas une preuve d'innocuité
globale. Le clean-room reconstitue l'arbre sans `results/` (données historiques,
délibérément non transportées) ; aucun test collecté n'en dépend.

**Résidu de montage, redivulgué** — le montage est en création seule (`rm` renvoie
`EPERM`) : subsistent `.opr00_probe_delete_me`, des `.git/objects/*/tmp_obj_*`, et les
deux archives de transport `REVIEW_a379efa6_tree.tar.gz` et `REVIEW_bc2a42c_parent.tar.gz`
créées par la revue `31cccc`. Rien n'a été nettoyé ; aucune de ces entrées n'appartient à
un arbre committé.

---

## 13. Ce qui reste scientifiquement inconnu

**Tout.** Aucune valeur de `Δ(f)`, aucune de `ψ`, aucune fraction de censure, aucune
fraction d'inéligibilité, aucune répartition sur les cinq états terminaux, aucun monde
Route E, aucune loi tirée, aucune condition initiale tirée, aucun seed scientifique, aucun
round de beacon consulté, aucun namespace, aucune famille.

Route E reste **un protocole sélectionné, non confirmé**. Le seul résultat publié du
programme demeure le premier article (`https://doi.org/10.5281/zenodo.21403458`), qui
n'établit **ni ownership local, ni autonomie, ni individualité complète, ni
reconstruction, ni reproduction, ni hérédité**.

Aucune donnée Stage B, `M_MINUS`, Kovacs, trajectoire, shard, candidat ou résultat
historique n'a été ouverte. Aucun calibrage à partir de données. Route G n'a pas été
rouverte. Aucune prérégistration n'est commencée.

---

## 14. Prochaine étape conditionnelle

- **Obligations internes encore ouvertes** ⇒ la suite est une nouvelle correction sous le
  **même** identifiant `FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00`, **après** les
  autorisations du §11 ; sans elles, PRB-2 (authenticité), PRB-5 et PRB-6 ne peuvent pas
  être fermés, quel que soit le travail fourni.
- **Puis** : fermeture de PRB-6 sous le même identifiant, puis **revue humaine
  indépendante**.
- **Seulement après acceptation indépendante des six PRB** :
  `ROUTE_E_REPLICATION_DENSITY_PREREGISTRATION_00` — qui restera une **prérégistration**,
  **pas un run**.

---

## 15. Firewall et remote

Chemins Git exacts, `diff-tree` borné au couple parent–candidat, `GIT_INDEX_FILE`
neutralisé, index de preuve sous `/tmp`. Aucun `git add -A`, aucun checkout, stash, amend,
rebase, merge, cherry-pick, `git gc`, aucun nettoyage de fichier utilisateur, aucune
modification du véritable index. `main` immobile à
`f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77`, `.git/index` réel intact, working tree sale
préservé. Les branches `…-00`, `…-00-human-review`, `…-00-revision` et
`…-00-revision-human-review` sont préservées et non déplacées ; les records `bc2a42c4` et
`31ccccfb` ne sont pas modifiés.

**Remote.** Une tentative de push **normale**, unique, de la seule branche de révision.
Aucun `--force`, aucun push de `main`, aucun changement de credentials, aucun retry.

> ### `scientific_run_authorized = false`
>
> `PRB-5 = OPEN` · `PRB-6 = OPEN` · `ANTI_REROLL = UNPROVEN`
> Aucune acceptation humaine n'est prononcée ici.
