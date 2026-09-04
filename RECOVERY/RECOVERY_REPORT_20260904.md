# EDL — Rapport de récupération, 2026-09-04

`STATUS = RECOVERY_VERIFIED`

## 0. Ce que ce dépôt est, et ce qu'il n'est pas

Ce dépôt est une **récupération au niveau des fichiers**. Il porte les octets ;
il ne porte **pas** la provenance git du programme.

- Il n'hérite d'**aucune** histoire git. Son premier commit n'a pas de parent.
- Il n'est **pas** la branche `codex/one-matched-locked-daughter-control-test-02`,
  ni un descendant de `99b8044a037ccfb690131bdccbfa579985d73da8`, ni de
  `5372fd8`, ni de `77cc3c70a7690b102ca744cd0c20fd094351c79b`
  (`PARENT_TIP_AT_FREEZE` du gel TBRT02).
- Aucun commit d'origine n'est reconstruit, reparenté ou imité. Les empreintes de
  commit citées dans les artefacts (`bdd62e1`, `be9854f`, `dfab44a`, `bf47b4d`,
  `803457e`, `8a28411`, `9bebfda`, `ec4f83b`, `b895ff7`, `672ccc1`, `384333f`,
  `15f0ab3`) désignent des objets qui **ne sont pas dans ce dépôt**.

Il est destiné à être **greffé** sur le dépôt d'origine par son propriétaire,
jamais à s'y substituer.

## 1. Provenance

| | |
|---|---|
| Canal | document de Projet claude.ai `claude/durability/EDL_STATE.b64.txt` |
| Écrit le | 2026-08-31T03:38:18Z |
| Récupéré le | 2026-09-04T22:17Z |
| Contexte | conteneur de calcul effacé entre le 2026-08-31T03:45Z et le 2026-08-31T11:45Z ; `/home/claude/edl`, `/home/claude/durability` et `/mnt/user-data/uploads` absents |
| Pont vers l'ordinateur | **absent** (aucun outil `mcp__remote-devices__*`) |
| GitHub | **refusé, 403 au proxy** (`git ls-remote https://github.com/`). Refus non contourné, aucun jeton demandé |

## 2. Chaîne de vérification de la charge

| Contrôle | Résultat |
|---|---|
| base64, validation **stricte** (`validate=True`) | OK — 1 147 356 octets, alphabet propre |
| `sha256(base64)` | `928b8969e7e6cdc43884c1767db5e708eb462efa5de773be1d67a0c763c0d3ed` |
| `sha256(tar.gz)` **avant** extraction | `d1eb8ba11b4ab4986fd66f6a30afd6ef69d65d540f1c0aae190849a1897ba1bd` |
| gzip CRC32 + ISIZE | OK — 860 517 octets compressés, 4 167 680 décompressés |
| tar lisible | OK — 274 membres (246 fichiers, 28 répertoires) |
| chemins absolus | aucun |
| composants `..` | aucun |
| liens symboliques / physiques sortants | aucun (0 lien de tout type) |
| fichiers spéciaux / périphériques | aucun |
| collisions de noms (exactes et insensibles à la casse) | aucune |
| extraction | quarantaine dédiée, `tarfile.extractall(filter="data")` |
| `sha256` par fichier **avant** vs **après** extraction | 246/246 identiques, 0 manquant, 0 divergent |

`RECOVERY/RECOVERY_HASHES.json` porte les 246 empreintes avant et après.
`RECOVERY/SHA256SUMS_FULL_TREE` porte l'empreinte de chaque fichier de l'arbre.

## 3. Ce qui est VÉRIFIÉ par recalcul

1. **`METHODS_HASH`** recalculé par la formule gelée
   (`tbrt02_freeze.H.canonical_digest({p: file_sha256(p) for p in METHODS})`,
   17 fichiers) :
   `21571fb4cb1df9ac2e9089924e9d6ee5d4d63c920a007e188bdc24e0d94d1f99`.
   Identique au champ `METHODS_HASH` de `TBRT02_MASTER_FREEZE.json` et à la
   valeur consignée à l'armement. Concordance **fichier par fichier, 17/17**.
2. **Empreintes de contenu publiées** : `TBRT02/out/SHA256SUMS` compte **7**
   entrées, `sha256sum -c` rend **7/7 OK**.
3. **Retours de checker verbatim** : 6 fichiers présents.
   `CLOSE01_CHECKER_RETURN_VERBATIM.md` =
   `1543a8c9fd28de771b27430669b2b8400c25e58ec47ad5c38ce5c4d87b42135e`,
   identique à la valeur consignée à l'armement et au champ
   `CHECKER_RETURN_SHA256` de son adjudication. Les adjudications de FIMRCC02,
   OMLDCT03 et RPP98 déclarent chacune l'empreinte de leur verbatim et les trois
   concordent. RPP97 et TBRT02-C4bis emploient un autre schéma et ne déclarent
   pas d'empreinte de verbatim : pour ces deux-là l'empreinte est **calculée, non
   confrontée**.
4. **Test gelé d'OMLDCT03, recalculé de bout en bout** à partir de `PER_PAIR`
   par une implémentation indépendante (rang signé exact par programmation
   dynamique sur la loi nulle, médiane, Hodges-Lehmann par moyennes de Walsh,
   intervalle par inversion du test) :
   durée `W+ = 521.0`, `p = 0.24638633591985126`, médiane `+0.21357410029805912`,
   HL `+0.33307812236654888`, IC `(-0.238539, 0.836988)` ;
   exposition `W+ = 504.0`, `p = 0.34791725337890966`, médiane `+0.56946808437843366`,
   HL `+0.31613569679774711`, IC `(-0.310966, 0.873899)`.
   **Concordance au dernier chiffre sur les douze grandeurs.**
   C'est une **reconstruction sur les mêmes données**, pas une réplication
   indépendante.

## 4. Divergences réconciliées

| Point | Valeur consignée à l'armement | Valeur constatée | Résolution |
|---|---|---|---|
| empreintes de contenu publiées | « 6/6 » | `SHA256SUMS` en liste **7** | 7/7 vérifiées. Le compte de 6 est antérieur à l'ajout de `TBRT02_SEQUENTIAL_ADDENDUM.json` (déclaré le 2026-08-27T03:19:42Z) |
| retours de checker verbatim | « 5/5 » | **6** fichiers | 6 présents ; 4 confrontés à une empreinte déclarée, 2 (RPP97, TBRT02-C4bis) sans empreinte déclarée dans leur adjudication |

## 5. Ce qui est ABSENT de cette récupération

- **Toutes les archives brutes** (123 fichiers, ~440 Mo). Aucun `.npz`, `.tar.zst`
  ni `.bundle`. Arbre récupéré : 5,0 Mo.
- Les sorties de **FDOT01, FDFLT01, OMLDCT02, TLMR01, ORR01, OBTC02, FMRCT01,
  FMRT01** : `code/` seulement, pas de `out/`. En particulier
  `OMLDCT02_MASTER_FREEZE.json` est absent — le gel qu'OMLDCT03 déclare exécuter
  n'est lisible ici que par les citations qu'en font OMLDCT03 et son checker.
- Toute la **provenance git**.
- Le répertoire **`paper/`** (donc `paper/persistence-without-ownership-v1`).
- La **PR #34** et la branche `codex/one-matched-locked-daughter-control-test-02`
  au commit `99b8044a…` : sur GitHub, **inaccessibles** depuis cette session (403).
  Elles ne sont pas déclarées perdues ; elles sont hors de portée.

## 6. Statuts ré-émis inconditionnellement

`H3_STATUS = NOT_TESTED` · `REPRODUCTION_STATUS = NOT_TESTED` ·
`HEREDITY_STATUS = NOT_TESTED` · `AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED` ·
`X_LAWSPEC_BASELINE = UNCHANGED` · `ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED` ·
`COMPANION_PAPER_V1_1_STATUS = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED` ·
`OMLDCT02_STATUS = INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED` ·
`CLEA01_STATUS = CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED` ·
`TBRT02_STATUS = CLOSED__RAW_COMPLETE__PRIMARY_ADJUDICATION_INCONCLUSIVE_BY_CONSTRUCTION`
