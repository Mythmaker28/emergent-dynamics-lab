# Agent Journal — RUN-20260710-EXP02-STR

## VERDICT / RECOMMENDATION

**GO pour l'implémentation du writer, STOP pour l'exécution d'EXP02 tant que l'équivalence et la reprise ne passent pas.**

Conserver exactement la génération physique/détection/tracking actuelle, mais extraire les lignes par transaction naturelle `(law_index, seed)` et les ajouter, dans l'ordre historique, à quatre CSV plats sous `results/EXP02-COREV0-20260710-001/raw/`. Un checkpoint atomique doit enregistrer après chaque transaction les offsets octet, nombres de lignes, SHA-256 de préfixe et plages par run. Les agrégats doivent être reconstruits dans une seconde passe streaming à partir des raw validés. Le test d'acceptation doit prouver l'égalité **octet pour octet et ligne pour ligne** des quatre tables avec `run_baseline` sur une fixture minuscule non triviale, puis prouver qu'une interruption/reprise donne les mêmes octets sans doublon.

Cette option est préférable ici à 3 600 shards (quatre fichiers × 900 runs) : elle minimise le changement, conserve les tables CSV et leur ordre comme contrat, facilite l'audit existant et rend l'équivalence binaire directe. La contrepartie est un protocole de checkpoint/troncature plus strict, décrit ci-dessous.

## AGENT / ROLE

Sous-agent indépendant / audit borné de scalabilité et conception du chemin d'artefacts streaming EXP02.

## RUN ID

`RUN-20260710-EXP02-STR`

## START TIME

2026-07-10 04:44:34 +02:00

## END TIME

À finaliser après le dernier contrôle Git.

## STARTING GIT STATE

- Dépôt : `C:\Users\tommy\Documents\ising v3`
- Branche : `main`
- HEAD : `06fcd26c11b39476da5d80c24bf901be21658b36`
- `origin/main` : synchronisé (`0 0` dans `git rev-list --left-right --count origin/main...HEAD`)
- Worktree : propre avant la création du présent journal.
- `results/**/raw/` est effectivement ignoré par `.gitignore`.

## ASSIGNED SCOPE

Auditer `edlab/experiments/baseline.py` et `docs/experiments/EXP02_COREV0_PROTOCOL.md` au HEAD courant. Proposer une architecture minimale de CSV streaming/chunked sous `raw/`, checksums/manifests, agrégats et test d'équivalence bit/row avec le runner complet sur fixture minuscule. Rechercher les risques mémoire, artefacts partiels, reprise et Git. Ne modifier aucun code ; le seul fichier autorisé est ce journal.

## ACTIONS PERFORMED

- Lu dans l'ordre le contrat et la mémoire durable obligatoires : `AGENTS.md`, charter, état, décisions, index d'expériences, index de runs, dernier journal partiel, puis manifeste et résumé du dernier essai terminé.
- Inspecté intégralement le runner, le protocole EXP02, la politique d'artefacts, le test pipeline existant, la CLI, l'audit candidat, les mesures de continuité, le tracker et le moteur.
- Inspecté l'état Git, la synchronisation avec `origin/main`, la règle `.gitignore` et l'espace disque local.
- Mesuré les tailles et lignes des quatre tables de `BASELINE-COREV0-20260710-002`, puis extrapolé linéairement de 36 à 900 runs.
- Évalué deux options : shards immuables par run, ou quatre CSV plats avec append transactionnel et checkpoint d'offsets. Retenu la seconde pour la compatibilité et l'équivalence binaire, avec reprise fail-closed.
- Aucun code modifié, aucun test scientifique ni EXP02 lancé, aucun lock de run acquis : cet audit n'est pas un wake planifié et n'a touché ni la simulation ni un artefact expérimental.

## IMPORTANT FILES READ

- `AGENTS.md`
- `docs/RESEARCH_CHARTER.md`
- `docs/PROJECT_STATE.md`
- `docs/DECISION_LOG.md`
- `docs/EXPERIMENT_INDEX.md`
- `docs/RUN_INDEX.md`
- `docs/agent_journals/2026-07-10/0343_main-agent_run-001.md`
- `results/HOLDOUT-COREV0-20260710-003/manifest.json`
- `results/HOLDOUT-COREV0-20260710-003/summary.json`
- `docs/experiments/EXP02_COREV0_PROTOCOL.md`
- `docs/ARTIFACT_POLICY.md`
- `edlab/experiments/baseline.py`
- `edlab/experiments/audit_candidates.py`
- `edlab/observables/continuity.py`
- `edlab/entities/tracking.py`
- `edlab/substrates/particle_dynamics/engine.py`
- `edlab/cli.py`
- `tests/test_experiment_pipeline.py`
- `.gitignore`
- `pyproject.toml`

## FILES CREATED OR MODIFIED

- `docs/agent_journals/2026-07-10/0444_streaming-design_RUN-20260710-EXP02-STR.md` uniquement.

## COMMANDS / EXPERIMENTS EXECUTED

- Lectures `Get-Content -Raw` des fichiers ci-dessus.
- `git status --short --branch`, `git rev-parse HEAD`, `git log`, contrôle avance/retard avec `origin/main`, et `git check-ignore` sur un chemin `results/.../raw/example.csv`.
- `rg -n` sur les listes globales, écritures CSV, audit candidat et exigences EXP02.
- Comptage PowerShell des lignes et octets des quatre CSV de baseline 002.
- `Get-PSDrive C` : 153,5 Gio libres observés au moment de l'audit.
- Aucun test ou run expérimental lancé ; les artefacts existants seuls ont été lus.

## OBSERVED

### Mémoire et volume

Le runner conserve globalement quatre listes de dictionnaires pour toute l'expérience (`baseline.py:209-212`), les alimente jusqu'à la fin (`253`, `284`, `286`, `300`), puis seulement écrit les CSV (`309-312`). Il reconstruit ensuite deux tableaux NumPy depuis toutes les mesures et transmet encore la liste entière au plotter (`426-427`).

Baseline 002 contient, pour 36 runs :

| Table | Lignes observées | Octets observés | Projection 900 runs |
|---|---:|---:|---:|
| `measurements.csv` | 36 722 | 3 661 665 | 918 050 lignes / 91 541 625 octets |
| `lineage_events.csv` | 19 269 | 1 469 101 | 481 725 / 36 727 525 |
| `entity_observations.csv` | 16 937 | 13 620 325 | 423 425 / 340 508 125 |
| `association_edges.csv` | 89 190 | 9 798 926 | 2 229 750 / 244 973 150 |

Projection linéaire totale : **713 750 425 octets, soit 680,7 Mio**. Ce n'est pas une mesure d'EXP02 et la densité d'entités dépendra des lois. En mémoire, plusieurs millions de dictionnaires, chaînes JSON et objets Python auront un coût plusieurs fois supérieur au CSV ; plusieurs Gio sont plausibles. Les objets `snapshots`, `entities_by_step` et chaque `LineageTracker` sont en revanche bornés à un run/cadence ; il n'est pas nécessaire de changer cette partie ni la trajectoire physique.

### Artefacts partiels et reprise

- `output_dir.mkdir(..., exist_ok=False)` est exécuté au début (`baseline.py:169`). Un crash laisse un répertoire qui bloque toute relance mais ne fournit aucune reprise sûre.
- `laws.json` est publié avant la boucle, tandis que les quatre CSV ne sont publiés qu'après toutes les simulations. Un arrêt tardif perd donc tout le progrès encore uniquement en RAM.
- `_write_csv` écrit directement le nom final sans fichier temporaire. Un arrêt pendant les quatre écritures peut laisser un mélange de fichiers complets et tronqués.
- `manifest.json` est écrit en dernier, ce qui aide à reconnaître une exécution incomplète, mais le runner n'a ni statut explicite `COMPLETE`, ni checkpoint, ni vérification/reprise.
- `audit_candidates.py:17,54-56` recharge entièrement mesures, événements et observations dans des listes. Même avec un writer streaming, appeler cet audit tel quel recréerait un risque mémoire et il ne sait pas lire `raw/`.

### Git et disponibilité

- `.gitignore` ignore déjà exactement `results/**/raw/`; c'est conforme au protocole.
- Les raw ne seront donc ni visibles dans `git status`, ni présents après clone/pull. Un checksum prouve l'intégrité d'un fichier présent, pas sa disponibilité. Le manifeste doit dire explicitement `raw_storage: local_ignored` et l'index commité doit suffire à vérifier ou régénérer, jamais prétendre que les raw ont été poussés.
- Au départ, `HEAD` est propre et synchronisé avec `origin/main`. Une reprise sous un SHA ou une config différente doit être refusée, pas fusionnée silencieusement.
- Les 153,5 Gio libres observés rendent ~0,7 Gio plausible localement, mais un préflight doit quand même exiger une marge (raw + temporaires + dérivés), car l'extrapolation n'est pas une borne.

## PROPOSED MINIMAL ARCHITECTURE

### 1. Une génération commune, deux sinks

Extraire du runner une unité pure `RunArtifactBatch` par `(run_ordinal, law_index, seed)` contenant les quatre collections dans le même ordre que maintenant. Ne changer ni `initialize_world`, ni `simulate`, ni la détection, ni les trackers, ni `measure_tracks`. Le runner complet garde un sink en mémoire pour référence ; EXP02 utilise un sink streaming. Cette séparation teste le stockage sans introduire un second calcul scientifique.

Déclarer quatre schémas de colonnes explicites dans l'ordre actuel, au lieu de les inférer de la première ligne. Conserver exactement `csv.DictWriter`, la représentation des floats/booléens, les JSON actuels et le terminateur `\r\n`. Retarder l'en-tête jusqu'au premier batch non vide afin de préserver le comportement historique d'une table entièrement vide (fichier de zéro octet).

L'ordre contractuel reste : lois croissantes, graines dans l'ordre configuré, cadences dans l'ordre configuré, puis l'ordre actuel interne de chaque table. Aucun tri postérieur, aucune parallélisation des runs dans ce premier vertical slice.

### 2. Quatre CSV append-only sous `raw/`, transaction par run

Arborescence locale ignorée :

```text
results/EXP02-COREV0-20260710-001/raw/
  run_plan.json
  checkpoint.json
  measurements.csv
  lineage_events.csv
  entity_observations.csv
  association_edges.csv
```

Pour chaque run :

1. Construire seulement ses quatre batches en mémoire.
2. Sérialiser chaque batch en bytes UTF-8 avec schéma et newline gelés.
3. Ajouter les quatre buffers ; `flush` puis `fsync` chaque fichier.
4. Écrire `checkpoint.json.tmp`, `fsync`, puis `os.replace` vers `checkpoint.json` **en dernier**.

Le checkpoint versionné contient au minimum : experiment ID, SHA Git, indicateur worktree propre, hash canonique de la config, hash de `laws.json`, run ordinal suivant, couple loi/graine terminé, offsets octet et nombres de lignes par table, SHA-256 de chaque préfixe, présence d'en-tête et plages octet/ligne de chaque run. Ces plages forment aussi l'index de chunks pour l'analyse sans créer des milliers de fichiers.

### 3. Reprise fail-closed

Au redémarrage, sous le lock obligatoire :

- refuser si experiment ID, SHA Git, config, LawSpecs, schéma ou ordre de run diffèrent ;
- recalculer le SHA de chaque préfixe jusqu'à l'offset commité ;
- si un fichier est plus court que son offset ou si le hash diffère : **STOP_CORRUPT**, ne pas réparer narrativement ;
- s'il est plus long : tronquer exactement à l'offset du dernier checkpoint, car ces octets ont été écrits avant le commit atomique du checkpoint ;
- reprendre au run ordinal suivant ; ne jamais append sur la seule foi de la taille ou du nom de fichier ;
- si le manifeste final `COMPLETE` existe et valide tous les hashes, refuser une nouvelle écriture.

Cette séquence couvre un crash avant, pendant ou après l'append : seul le checkpoint publié après `fsync` fait foi. Le SHA de préfixe doit être recalculé une fois lors d'une reprise ; 0,7 Gio reste acceptable et évite de sérialiser un état interne de `hashlib` non portable.

### 4. Finalisation, manifests et chaîne de checksums

Après 900/900 runs et validation de tous les préfixes :

- produire à la racine commit-able `schemas.json` et `raw_index.json` ;
- pour chaque raw : chemin relatif, schéma/version, lignes, octets, SHA-256 final ;
- pour chaque run : ordinal, loi, graine, plages de lignes/octets par table ;
- indexer le hash de `raw_index.json` dans le manifeste principal ;
- publier `manifest.json` en dernier, par temp + `os.replace`, avec `status: COMPLETE`, `expected_runs: 900`, `completed_runs: 900`, SHA de code, propreté Git, config/LawSpecs, commande exacte, dépendances, raw local ignoré, hashes des outputs dérivés et avertissement de pseudoréplication ;
- ne jamais considérer la seule présence d'un fichier comme preuve de complétude.

Le manifeste principal ne se hash pas lui-même. La chaîne est : `manifest.json -> SHA(raw_index.json) -> SHA/tailles/lignes des raw`, et `manifest.json -> SHA des dérivés`.

### 5. Agrégats en seconde passe streaming

Ne pas checkpoint-er un gros état analytique mutable. Après raw `COMPLETE`, relire les fichiers via les plages par run et produire des dérivés déterministes, chacun référencé au SHA de `raw_index.json` :

```text
schemas.json
raw_index.json
laws.json
aggregates/pm_joint_density.csv
aggregates/pm_by_tau_cadence_flags.csv
aggregates/law_screening.csv
aggregates/lifetime_turnover_events.csv
candidates/eligible_endpoints.csv
summary.json
summary.md
figures/...
REPRODUCE.md
manifest.json
```

Les bins/définitions de densité et du Pareto doivent être gelés avant EXP02 et inscrits au manifeste. Les agrégats conservent P et M séparés ; aucun `P*(1-M)`, `theseus_score`, `memory_score` ou équivalent. La règle candidate applique d'abord, pour **chaque cadence contributrice**, au moins huit observations et aucune ambiguïté/split/merge sur toute la track, puis groupe le même endpoint entre cadences, puis exige au moins deux graines sur trois par loi. Cela évite de reproduire le bug de join qui a invalidé hold-out 002.

Pour la corrélation et les figures, deux tableaux NumPy float64 de P et M projetés à ~918 050 lignes coûtent environ 14 Mio et restent raisonnables si l'on veut reproduire exactement `np.corrcoef`; toutes les lignes dictionnaires et JSON ne doivent jamais être rechargées. Sinon une accumulation stable en ordre de ligne est acceptable, mais l'équivalence numérique doit alors avoir une tolérance déclarée.

## REQUIRED EQUIVALENCE AND RECOVERY TESTS

### Test principal : `test_streaming_matches_full_runner_on_tiny_fixture`

Exécuter `run_baseline` et le nouveau runner streaming avec exactement la même config, le même experiment ID et le même faux SHA dans deux répertoires temporaires. La fixture doit être assez petite pour le test mais doit explicitement vérifier qu'elle n'est pas vacue ; si une table est légitimement vide, ajouter en plus un test synthétique de sink couvrant floats, booléens, JSON, virgules/guillemets et table vide.

Pour chacune des quatre tables :

1. `full/<table>.csv.read_bytes() == stream/raw/<table>.csv.read_bytes()` ;
2. SHA-256 identiques ;
3. mêmes en-têtes, même nombre de lignes et égalité champ par champ en ordre ;
4. compte du `raw_index.json` égal au compte réellement relu ;
5. `laws.json`, `summary.json` et `summary.md` égaux sémantiquement/bit à bit selon leur contenu déterministe ; exclure seulement du bit-comparatif les champs volontairement variables du manifeste comme le timestamp, mais vérifier tous leurs hashes et invariants.

Le test doit échouer sur une simple permutation de lignes : l'égalité de multiensemble n'est pas suffisante.

### Tests de reprise obligatoires

- Injecter un arrêt après append mais avant remplacement du checkpoint ; la reprise tronque les octets non validés, termine, et produit exactement les mêmes quatre fichiers que le run uninterrupted.
- Reprendre après un checkpoint valide ; aucun run n'est dupliqué.
- Corrompre un octet avant l'offset validé ; reprise refusée avec `STOP_CORRUPT`.
- Changer SHA/config/LawSpecs/schéma ; reprise refusée.
- Vérifier qu'aucun `manifest.json` `COMPLETE` n'est publié avant validation des 900 runs, des raw, des dérivés et des hashes.

## INFERRED

- Le changement de writer suffit à borner la mémoire de génération à un seul run, mais **ne suffit pas** tant que `audit_candidates.py` et le plotter peuvent recharger les tables entières. Un finalizer EXP02 streaming/chunk-aware fait partie du même gate avant exécution.
- Le volume disque observé ne justifie pas Parquet, une base de données ou une compression dans ce premier slice. CSV plat + index de plages offre le chemin le plus facile à falsifier et à comparer au runner validé.
- La reprise doit rester séquentielle. Paralléliser les runs maintenant compliquerait l'ordre binaire, le checkpoint et la causalité sans nécessité démontrée.

## HYPOTHESIS

Un append transactionnel par `(law_index, seed)` avec schémas gelés et finalizer en seconde passe préservera exactement les quatre flux bruts du runner complet tout en rendant la mémoire indépendante du nombre total de runs.

## WHAT WOULD FALSIFY THIS?

- Une différence d'octet ou de ligne entre full et streaming sur la fixture.
- Une mémoire maximale qui croît avec le nombre de runs après flush/checkpoint.
- Une reprise qui duplique/perd une ligne ou accepte un préfixe corrompu.
- Un dérivé qui ne peut pas être régénéré depuis les raw + index + manifest, ou qui réintroduit un join cadence non propre.
- Une modification de trajectoire, détection, association, P ou M nécessaire pour faire passer le writer.

## FAILURES / DEAD ENDS

- Une première commande PowerShell de comptage a échoué sur un pipe placé directement après `foreach`; elle n'a rien écrit. La commande a été corrigée en collectant d'abord `$stats`.
- Les shards immuables par run ont été considérés pour simplifier l'atomicité. Ils faciliteraient la reprise mais imposeraient ~3 600 CSV, un lecteur concaténé et une notion de hash logique. Le CSV plat transactionnel donne ici une équivalence plus forte et moins de changements, à condition de tester strictement offsets/troncature/fsync.
- Aucun benchmark mémoire dynamique n'a été lancé : l'estimation est explicitement dérivée des artefacts baseline 002, conformément au scope sans nouveau run.

## DECISIONS MADE

Aucune décision scientifique ni modification de `docs/DECISION_LOG.md`. Recommandation architecturale seulement : quatre tables brutes plates transactionnelles sous `raw/`, transaction par loi/graine, checkpoint d'offsets atomique, finalizer streaming séparé, manifest `COMPLETE` en dernier.

## UNRESOLVED RISKS

- Les définitions exactes de bins de densité, résumé Pareto et tables par loi/tau/cadence ne sont pas encore gelées dans le protocole ; elles doivent l'être avant exécution, sans modifier P/M ni les seuils.
- La durabilité exacte de `fsync` + remplacement atomique doit être testée sous Windows, l'environnement réel.
- Les raw ignorés restent un point unique local tant qu'aucun stockage externe n'est autorisé ; les checksums ne sont pas une sauvegarde.
- L'extrapolation linéaire de 680,7 Mio peut sous-estimer des lois qui créent beaucoup plus d'entités/edges. Ajouter un préflight espace libre et des métriques progressives octets/run, lignes/run et durée/run.
- Le test pipeline actuel vérifie seulement l'existence des fichiers ; il ne couvre ni contenu, ni égalité, ni reprise.

## HANDOFF / EXACT NEXT AUTHORIZED ACTION

Implémenter le générateur de `RunArtifactBatch`, le sink CSV transactionnel et le finalizer streaming ; ajouter d'abord les tests d'équivalence binaire/ligne et de crash-reprise ci-dessus ; exécuter les tests pertinents sur un worktree propre. **Ne pas lancer EXP02** avant passage complet, manifeste de fixture vérifié et commit SHA propre/poussé. Ensuite seulement acquérir le lock programmé et lancer/reprendre les 900 runs.

## ENDING GIT STATE

À finaliser après le dernier contrôle Git.
