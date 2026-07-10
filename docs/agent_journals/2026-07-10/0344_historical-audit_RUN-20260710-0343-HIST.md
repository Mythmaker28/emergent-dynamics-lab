# Journal de l'agent historical-audit

## AGENT / ROLE

- Agent : sous-agent `historical_audit`
- Rôle : audit indépendant, strictement read-only, de la source historique `Mythmaker28/ising-life-lab`

## RUN ID

`RUN-20260710-0343-HIST`

## START TIME

2026-07-10 vers 03:44 CEST. L'heure exacte n'a pas été capturée avant la première commande; ne pas lui attribuer une précision à la seconde.

## END TIME

2026-07-10 03:56 CEST.

## STARTING GIT STATE

### Nouveau workspace

- Repository : `C:\Users\tommy\Documents\ising v3`
- Remote observé plus tard pendant le run : `origin = https://github.com/Mythmaker28/emergent-dynamics-lab.git`
- Branche : `main`
- HEAD : branche non née, aucun commit résolu par `git rev-parse HEAD`
- État initial exact : le porcelain Git n'a pas été capturé avant la première lecture. Le premier listing montrait `.git/` et `docs/`. D'autres agents ont créé des fichiers en parallèle pendant ce run.

### Clones historiques inspectés

- `C:\Users\tommy\Documents\ising-life-lab`
  - remote : `https://github.com/Mythmaker28/ising-life-lab.git`
  - branche checkout : `toolkit-core-r1`
  - HEAD : `05f41d52c49f17f11397c32e8946f1df5c899725`
  - l'objet `9992e6c` n'y est pas présent.
- `C:\Users\tommy\Documents\ising-v2-final`
  - remote : `https://github.com/Mythmaker28/ising-life-lab.git`
  - branche checkout : `main`
  - HEAD : `67590d7c031b4ef7d04e514283f13630906d67f2`
  - dirty/clean au début : non capturé avant les commandes de lecture. Le status final est massivement dirty avec modifications et fichiers non suivis préexistants; aucune commande de ce run n'a écrit dans ce clone.

## ASSIGNED SCOPE

1. Chercher réellement `revival/universe-regime-discovery` et le commit `9992e6c` dans les clones locaux, refs, remotes, reflogs et historique raisonnable.
2. Ne modifier absolument rien dans l'ancien dépôt.
3. Si le contenu est accessible, inspecter le diff et inventorier fichiers, paramètres, tests et baseline disponibles.
4. N'exécuter des tests qu'en évitant toute écriture dans le dépôt historique.
5. Distinguer strictement ce qui est observé de ce qui était seulement rapporté par l'agent historique.
6. Créer uniquement ce journal dans le nouveau dépôt.

## ACTIONS PERFORMED

- Recherche des clones portant le remote `Mythmaker28/ising-life-lab` sous `C:\Users\tommy\Documents`.
- Inspection sans checkout de `show-ref`, branches locales/distantes, logs `--all`, reflogs, objets Git et refs textuelles.
- Interrogation read-only du remote avec `git ls-remote --heads origin`.
- Inspection des deux commits historiques :
  - `a1da19e841d962a6de9c9be9068c55c2ff68c088`
  - `9992e6c5149537add3802d1805e8f2c82548442b`
- Inspection du diff cumulé depuis `67590d7` jusqu'à `9992e6c`.
- Lecture directe des fichiers depuis l'objet Git avec `git show 9992e6c:<path>`; aucun checkout.
- Recalcul indépendant, depuis le CSV versionné, des statistiques P/M avec Python standard library seulement.
- Extraction de l'arbre `9992e6c` dans un répertoire temporaire Windows, installation temporaire de dépendances et exécution des tests hors du clone historique avec bytecode et cache pytest désactivés.
- Nettoyage vérifié du répertoire temporaire.
- Lecture du protocole utilisateur et des règles obligatoires de journalisation dans les trois pièces jointes.

## FILES READ

### Métadonnées Git

- `.git/config`, refs et reflogs des deux clones historiques.
- Objets commits `67590d7`, `a1da19e`, `9992e6c`.

### Diff historique final : 24 fichiers, 9 271 insertions

- `docs/revival/REPO_AUDIT_2026.md`
- `docs/revival/SYNTHESE_FR_TOMMY.md`
- `docs/revival/UNIVERSE_REGIME_RESEARCH_CHARTER.md`
- `results/revival/audit_memory_evidence.txt`
- `results/revival/exp01/pm_rows.csv`
- `results/revival/exp01/pm_scatter.png`
- `results/revival/exp01/provenance.json`
- `results/revival/exp01/run_summaries.json`
- `results/revival/exp01/summary.md`
- `results/revival/exp01/verdict.json`
- `universe/.gitignore`
- `universe/README.md`
- `universe/__init__.py`
- `universe/detect.py`
- `universe/engine.py`
- `universe/experiments/exp01_measurability.py`
- `universe/observe.py`
- `universe/phenotype.py`
- `universe/spec.py`
- `universe/tests/test_detect_track.py`
- `universe/tests/test_engine.py`
- `universe/tests/test_verification.py`
- `universe/theseus.py`
- `universe/track.py`

## FILES CREATED OR MODIFIED

- Créé uniquement : `docs/agent_journals/2026-07-10/0344_historical-audit_RUN-20260710-0343-HIST.md`
- Aucun fichier modifié dans `ising-life-lab` ou `ising-v2-final`.
- Des fichiers temporaires ont été créés sous `%TEMP%`, puis supprimés après vérification. Ils n'étaient dans aucun dépôt.

## COMMANDS / EXPERIMENTS EXECUTED

Commandes importantes, sous forme reproductible :

```powershell
$env:GIT_OPTIONAL_LOCKS='0'
git -C C:\Users\tommy\Documents\ising-v2-final show-ref
git -C C:\Users\tommy\Documents\ising-v2-final branch --all --no-color
git -C C:\Users\tommy\Documents\ising-v2-final reflog show --all --date=iso
git -C C:\Users\tommy\Documents\ising-v2-final cat-file -t 9992e6c
git -C C:\Users\tommy\Documents\ising-v2-final ls-remote --heads origin
git -C C:\Users\tommy\Documents\ising-v2-final diff --find-renames --name-status 67590d7 9992e6c
git -C C:\Users\tommy\Documents\ising-v2-final show 9992e6c:<path>
git -C C:\Users\tommy\Documents\ising-v2-final grep -n '^def test_' 9992e6c -- universe/tests
```

Recalcul du CSV : lecture par pipe de `git show 9992e6c:results/revival/exp01/pm_rows.csv`, puis calcul Python standard-library des moyennes, corrélations, rangs moyens, quadrants, bins et agrégats par lag. Aucun fichier produit.

Test indépendant :

1. `git archive --format=zip -o <temp> 9992e6c`
2. extraction dans `%TEMP%`
3. dépendances temporaires : NumPy 2.5.1, SciPy 1.18.0, pytest 9.1.1 sous Python 3.12.10
4. `PYTHONDONTWRITEBYTECODE=1`
5. `python -B -m pytest -p no:cacheprovider universe/tests -q`

Résultat : `19 passed in 26.40s`, exit code 0.

## OBSERVED

### Statut de la source historique

- La branche correcte existe localement dans `ising-v2-final` :
  - `refs/heads/revival/universe-regime-discovery -> 9992e6c5149537add3802d1805e8f2c82548442b`
- Une branche avec faute de frappe existe aussi et pointe vers le même objet :
  - `refs/heads/revival/universe-regive-discovery -> 9992e6c5149537add3802d1805e8f2c82548442b`
- Le reflog de la branche correcte montre :
  - création depuis `main`/`67590d7` à 02:33:22 CEST;
  - commit vertical slice `a1da19e` à 02:55:49;
  - commit de synthèse/nettoyage `9992e6c` à 02:57:38.
- `9992e6c` est un objet commit valide dans `ising-v2-final` et absent du clone `ising-life-lab` contrôlé.
- Les seuls clones correspondant à ce remote trouvés sous `Documents` sont `ising-life-lab` et `ising-v2-final`.
- Le remote annonçait au moment du contrôle uniquement :
  - `main -> f95b3dc94e1a5faa3da1d3f13e4ea4dc3cc75c4b`
  - `memory-ai-lab -> be6d69f1d89660c96aadf5eb2b653b0dd8f1aa85`
  - `toolkit-core-r1 -> 05f41d52c49f17f11397c32e8946f1df5c899725`
- Aucune ref distante `revival/*` n'est annoncée par `git ls-remote`.
- Le clone `ising-v2-final` a une ref locale `origin/main` ancienne à `67590d7`, différente du `main` distant annoncé à `f95b3dc`.
- Conclusion limitée : le commit est récupérable localement mais n'est pas annoncé par une branche du remote. L'absence absolue de tout objet orphelin côté GitHub n'a pas été démontrée.

### Contenu réel du diff

- `a1da19e` ajoute le vertical slice, les tests, les résultats EXP01 et neuf fichiers `__pycache__` suivis par erreur.
- `9992e6c` ajoute la synthèse française et `universe/.gitignore`, puis supprime les neuf fichiers bytecode suivis.
- Diff final `67590d7..9992e6c` : 24 fichiers, 9 271 insertions, dont 7 080 lignes de CSV et un PNG de 168 438 octets.
- Aucun fichier de verrouillage ou déclaration d'environnement Python n'existe au tip : pas de `requirements*.txt`, `pyproject.toml`, `uv.lock`, `poetry.lock`, `environment.yml`, `Pipfile`, `setup.py` ou `setup.cfg` pour `universe/`.

### Paramètres historiques effectivement disponibles

Protocole EXP01 lu dans le script et les artefacts :

- substrat : Particle Life de référence NumPy O(N²), boundary périodique;
- `N=200`, boîte `90 x 90`, `dt=0.05`, `steps=1500`, temps simulé `75`;
- snapshot tous les `30` ticks, soit 51 snapshots;
- détection : graphe de rayon périodique, `link_radius=4.0`, `min_size=6`;
- tracker : `min_overlap=0.3` par défaut; `max_move=9.0` par défaut pour cette boîte; cette configuration vient des defaults de `Tracker`, pas du manifeste;
- track long : au moins 8 snapshots;
- lags : `30, 60, 120, 240` ticks;
- quatre lois, deux seeds par loi (`1, 2`), donc huit runs;
- graine du tirage de la loi random : `20260710`.

Lois exactes présentes dans `provenance.json` :

- `clump`, hash `00fa3c0cfd68f66e`: matrice diagonale `1.0`, hors-diagonale `-0.5`; `r_int=12`, `r_col=3`, collision `2`, friction `0.6`, max speed `5`.
- `chase`, hash `8885de90451dccdf`: matrice `[0.8,-0.6,0.5; 0.5,0.8,-0.6; -0.6,0.5,0.8]`; `r_int=14`, `r_col=3`, collision `2`, friction `0.7`, max speed `5`.
- `repel`, hash `283750ea19200bdc`: neuf coefficients `-0.3`; `r_int=10`, `r_col=3`, collision `2.5`, friction `0.8`, max speed `5`.
- `random1`, hash `2f365d6d0a896a0a`: matrice complète et valeurs flottantes exactes conservées dans `provenance.json`; `r_int=14.12703232156348`, `r_col=5.166618683622602`, collision `2.5262078390335727`, friction `0.6075569303716974`, max speed `2.0393105388272796`.

Observables :

- `M(tau)` = Jaccard des ensembles d'IDs persistants.
- `Phi` = 8 scalaires (`size`, `radius_gyration`, `anisotropy`, `area_shape`, `packing`, `speed_cm`, `vel_dispersion`, `ang_momentum_abs`) + histogramme des 3 types.
- Les dimensions de `Phi` sont z-standardisées séparément dans chaque run à partir du pool de phénotypes du run.
- `d_ref` est la médiane des distances par paires parmi au plus 200 vecteurs échantillonnés uniformément dans ce pool; le code ne filtre pas strictement les paires inter-tracks.
- `P(tau) = exp(-d/d_ref)`.

### Tests réellement présents et exécutés

- 19 fonctions de test réelles : 6 moteur, 11 détecteur/tracker/phénotype/nulls, 2 vérification différentielle.
- Exécution indépendante hors dépôt : `19 passed in 26.40s`.
- Le test de second chemin recalcule les forces via `cKDTree` et une boucle explicite et exige `allclose(..., atol=1e-9)` pour trois seeds; il a passé.
- Les toggles collision/interactions sont testés et ont passé.
- L'inertie des IDs est testée au niveau des forces et a passé.
- Les fixtures immobile, translation de track, rotation de l'anisotropie, turnover synthétique, crossing, split, merge, disparition et bruit diffus ont passé.
- Les deux tests appelés null models ont passé : ensembles d'IDs disjoints/Jaccard et motif statique identique avec IDs entièrement remplacés.

### Baseline archivée : ce qui a été vérifié indépendamment

- Le CSV versionné contient 7 079 lignes de mesures P/M plus un header.
- Les `run_summaries.json` contiennent 8 runs et totalisent 71 long tracks et 7 079 lignes.
- Recalcul sur le CSV versionné, dont P et M sont arrondis à quatre décimales :
  - Pearson `r = 0.6757240591`;
  - Spearman avec rangs moyens `rho = 0.6881734693`;
  - `P > 0.8` et `M < 0.5` : `0 / 7079`;
  - `P > 0.8` et `M < 0.8` : `1 / 7079`;
  - `P` moyen `0.7601584`;
  - `M` moyen `0.9312187`;
  - `M` arrondi min/max dans CSV : `0.0714 / 1.0`.
- Moyennes par lag recalculées depuis le CSV :
  - tau 30 : `M=0.97575`, `P=0.87846`, 1 965 lignes;
  - tau 60 : `M=0.95465`, `P=0.79989`, 1 894 lignes;
  - tau 120 : `M=0.91701`, `P=0.70365`, 1 752 lignes;
  - tau 240 : `M=0.85835`, `P=0.61798`, 1 468 lignes.
- Le `verdict.json` conserve les valeurs non arrondies au moment historique et annonce `M_min=1/14`, `M_max=1`, spread `0.928571...`, `MEASURABLE=true`.
- Important : l'expérience de simulation EXP01 n'a pas été réexécutée durant ce run. Le CSV et les JSON ont été lus et leurs agrégats recalculés. Cela valide la cohérence interne des artefacts, pas une reproduction indépendante des trajectoires.
- Le fichier `audit_memory_evidence.txt` sur l'ancienne claim CA a été lu, mais ses probes n'ont pas été réexécutées. Ses conclusions restent un rapport historique accessible, non reproduit par cet agent.

## INFERRED

- Le vertical slice historique est assez complet pour servir de référence de conception et de comportement, car le code, les paramètres, les tests et les artefacts sont tous accessibles dans le même objet Git local.
- Les chiffres centraux `7079`, `r≈0.68` et `0/7079` ne sont plus seulement une assertion orale : ils sont cohérents avec le CSV réellement versionné et ont été recalculés. Ils ne doivent toutefois pas être appelés une reproduction complète tant que la simulation n'est pas rerun depuis un environnement déclaré.
- Le test différentiel des forces fournit une validation indépendante réelle du calcul vectorisé dans l'environnement temporaire utilisé ici.
- La conclusion limitée « aucun point du quadrant initial dans ce petit échantillon archivé » est supportée. Une conclusion générale sur Particle Life ne l'est pas : seulement 4 lois et 2 seeds ont été exécutées.

## HYPOTHESIS

- Hypothèse historique non testée ici : une cadence de 30 ticks et le tracker conservateur pourraient casser les tracks à turnover rapide et créer des faux négatifs.
- Hypothèse historique non testée ici : des mécanismes de flux, frontière ou homéostasie pourraient peupler le quadrant high-P/low-M.
- Aucune de ces hypothèses n'est élevée au rang de résultat par cet audit.

## WHAT WOULD FALSIFY THIS?

- Une réexécution exacte du commit avec dépendances pinnées, mêmes lois/seeds et même pipeline qui ne reproduit pas les mêmes sorties démontrerait que les artefacts versionnés ne constituent pas une baseline reproductible.
- Une analyse des valeurs P/M non arrondies montrant un point `P>0.8, M<0.5` falsifierait le constat de quadrant vide. Les artefacts actuels ne contiennent pas ces valeurs non arrondies ligne par ligne.
- Un contrôle de cadence/tracker faisant apparaître, sur les mêmes trajectoires ou des trajectoires comparables, des tracks high-P/low-M robustes falsifierait l'interprétation « phénomène absent » en montrant un faux négatif de mesure.
- Un contrôle causal perturbation/récupération est nécessaire pour falsifier l'alternative « motif statique traversé par un flux » lorsqu'un candidat high-P/low-M apparaîtra.

## FAILURES / DEAD ENDS

- Le Python système 3.12 ne disposait initialement ni de NumPy ni de SciPy; le premier recalcul utilisant NumPy a échoué. Le recalcul a été refait avec la standard library.
- Les deux venvs historiques sous `ising-life-lab` sont cassés : ils référencent un Python 3.13 supprimé. Ils contiennent des packages mais leur exécutable ne démarre pas.
- Une première extraction `git archive | tar` a échoué, car PowerShell a corrompu le flux binaire (`bad header checksum`). Aucun dépôt n'a été écrit. L'extraction a été refaite correctement via une archive ZIP temporaire.
- Le premier essai de tests après cette extraction corrompue n'a exécuté aucun test (`universe/tests` absent, exit 4). Ce résultat n'a pas été retenu comme validation.
- `gh` n'est pas installé. Une tentative de consultation GitHub via l'outil web n'a pas fourni de preuve exploitable. La conclusion remote repose donc sur `git ls-remote`, pas sur l'API GitHub des objets.
- Le chargeur de dépendances workspace est resté bloqué et a été interrompu; les dépendances ont été installées dans un dossier temporaire isolé.

## DECISIONS MADE

- Ne jamais checkout la branche historique et ne jamais exécuter pytest dans le clone dirty.
- Tester uniquement une archive temporaire de l'objet exact `9992e6c`.
- Ne pas réexécuter EXP01 dans ce sous-run : la mission bornée était l'audit historique; déclarer explicitement la baseline non reproduite plutôt que d'étendre silencieusement le scope.
- Ne pas modifier `docs/RUN_INDEX.md`, malgré la règle générale, car l'assignation spécifique interdit toute autre modification du nouveau dépôt. Le main agent doit indexer ce journal.

## UNRESOLVED RISKS

1. **Environnement non pinné.** Les 19 tests passent avec les versions temporaires actuelles, mais le commit ne déclare aucune version Python/NumPy/SciPy/pytest.
2. **Provenance insuffisante.** `provenance.json` contient `code_version="0.1.0-revival"`, pas le SHA Git. Il omet aussi cadence, paramètres du détecteur/tracker, lags et version des dépendances.
3. **Run ID incomplet.** `RunSpec.run_id()` n'incorpore ni `code_version`, ni configuration d'observation/détection/tracking; deux pipelines de mesure différents peuvent partager le même run ID.
4. **Comparabilité de P.** Le scaler et `d_ref` sont recalibrés séparément dans chaque run; agréger P entre lois/runs suppose une comparabilité qui n'est pas démontrée.
5. **Calibration décrite trop fortement.** Le code utilise toutes les paires du pool sous-échantillonné, pas uniquement des distances inter-tracks comme certaines docstrings le suggèrent.
6. **Nulls limités.** Les null models sont des fixtures unitaires, pas une baseline probabiliste intégrée au screening.
7. **Couverture ID plus faible que le protocole cible.** Le test IDs vérifie l'égalité des forces après relabeling, mais pas explicitement une évolution multi-step complète de deux états physiquement identiques avec IDs permutés.
8. **Couverture des invariances partielle.** La rotation testée porte sur l'anisotropie; la translation testée porte sur le maintien du track, pas sur l'égalité de tout le vecteur Phi.
9. **Lineage merge partielle.** Les merges sont loggés dans `events`, mais l'attribut `Track.parents` n'est pas rempli pour le child qui continue le parent dominant; le DAG annoncé n'est donc pas entièrement matérialisé dans l'objet track.
10. **Tracker conservateur.** Le fallback centroid n'est envisagé que si au moins un ID est partagé; un turnover de 100 % crée volontairement une nouvelle naissance. Cela empêche un faux stitch mais peut produire un faux négatif pour le phénomène cible.
11. **Résultats ligne par ligne arrondis.** Le CSV ne conserve P/M qu'à quatre décimales, alors que le verdict historique a été calculé avant arrondi.
12. **Pas de causalité expérimentale.** Aucun protocole perturbation/récupération n'est implémenté dans ce commit; P/M seuls ne démontrent pas l'auto-maintien.
13. **Remote.** La branche n'est pas annoncée sur le remote. Tant qu'elle n'est pas transférée vers le nouveau dépôt ou poussée explicitement, sa seule copie démontrée est locale.

## HANDOFF

- Source canonique récupérable : `C:\Users\tommy\Documents\ising-v2-final`, objet `9992e6c5149537add3802d1805e8f2c82548442b`.
- Ne pas travailler dans son checkout dirty. Lire avec `git show`/`git archive`.
- Utiliser le commit comme **référence historique auditée au niveau code/tests/artefacts**, pas comme dépendance du nouveau repo.
- Libellé recommandé :
  - `historical artifacts independently audited` pour code + CSV + recalculs;
  - `historical tests independently rerun: 19/19 passed`;
  - `historical experiment not independently rerun` pour EXP01.
- Le main agent doit ajouter ce run à `docs/RUN_INDEX.md`, car ce sous-agent était explicitement limité à un seul fichier.
- Si une reprise de code est décidée, corriger avant toute nouvelle baseline : environnement pinné, manifest complet hashé, SHA Git dans provenance, run ID couvrant tout le pipeline, tests d'invariance complets, sensibilité tracker/cadence.

## ENDING GIT STATE

### Ancien dépôt

- `ising-v2-final` reste checkout sur `main` à `67590d7c031b4ef7d04e514283f13630906d67f2`.
- Les refs historiques restent inchangées à `9992e6c`.
- Aucun commit, checkout, fetch, reset, clean, stash ou écriture de fichier n'a été effectué.
- Aucun push effectué.

### Nouveau dépôt

- Branche observée avant création du journal : `main`, HEAD non née.
- Fichier créé par cet agent : ce journal uniquement.
- Aucun commit créé par ce sous-agent.
- Aucun push effectué par ce sous-agent.
