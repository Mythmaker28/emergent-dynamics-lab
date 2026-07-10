# Réaudit numérique borné du commit `b8aaaf2`

## AGENT / ROLE

- Sous-agent `numerical_validation`.
- Rôle : réaudit numérique indépendant et borné des réparations du moteur CORE V0.

## RUN ID

- `RUN-20260710-NUM2`

## START TIME

- `2026-07-10T04:21:08.519+02:00`.

## END TIME

- `2026-07-10T04:23:29.811+02:00` pour la dernière capture Git/horloge avant rédaction.

## STARTING GIT STATE

- Repository : `C:/Users/tommy/Documents/ising v3`.
- Branche : `main`.
- HEAD : `b8aaaf2b414a7130bc00e01e82842c0b2d727183`.
- `origin/main` : `b8aaaf2b414a7130bc00e01e82842c0b2d727183`.
- Commit audité : `fix: repair numerical domain and lineage auditability`.
- Parent : `65af67e716ba157b4eef24ef1b69b589313d03f6`.
- Worktree : clean au premier contrôle (`## main...origin/main`).

## PRIOR JOURNAL REFERENCED

- `docs/agent_journals/2026-07-10/0400_numerical-validation_RUN-20260710-0343-NUM.md`.
- Ce réaudit vérifie explicitement les findings numériques consignés dans ce journal antérieur ; il ne le réécrit pas.

## ASSIGNED SCOPE

- Auditer exclusivement le commit exact `b8aaaf2` après réparations.
- Vérifier `hypot` de `r=1e-158` jusqu'au domaine subnormal.
- Vérifier le rejet de `interaction_range >= box_size/2`.
- Vérifier le rejet de `NaN` et `Inf`.
- Vérifier force et un pas à la tolérance gelée sur une banque incluant `N=64`.
- Vérifier déterminisme et neutralité physique des IDs diagnostiques.
- Exécuter la suite de tests.
- Ne modifier aucun code ; créer seulement ce nouveau journal.

## VERDICT

**FAIL strict pour la réparation numérique complète demandée.**

La réparation est substantielle et corrige le défaut pratique qui commençait à `r=1e-158`, mais elle n'est pas complète sur tout le domaine subnormal demandé :

- `np.hypot` conserve correctement chacun des 167 rayons sondés, y compris `5e-324` ;
- les deux chemins passent désormais à `r=1e-158`, `1e-161`, `1e-162`, `1e-200`, `1e-300`, `1e-308`, `1e-310` et `1e-314` ;
- huit rayons subnormaux sondés échouent encore à la tolérance ; le premier est `r=1e-315` ;
- au plus petit subnormal `5e-324`, `F_ref=-2.0` et `F_vec=-1.7`, soit une erreur `0.3`, puis une erreur après un pas de `0.00012` en position périodique et `0.006` en vitesse ;
- la cause résiduelle est le chemin scalaire, qui calcule encore `magnitude * dx / distance`, donc multiplie par le subnormal avant de diviser. Le produit est quantifié avant la normalisation.

Tous les autres gates demandés passent : suite complète, banque nominale avec `N=64` et un pas, rejet de la demi-boîte, rejet des scalaires non finis, replay exact et invariance ID.

## FINDINGS ANTÉRIEURS — STATUT APRÈS RÉPARATION

| Finding du journal précédent | Statut à `b8aaaf2` | Preuve du réaudit |
|---|---|---|
| Sous-débordement vectorisé par `sqrt(dx²+dy²)` dès `r=1e-158` | **CORRIGÉ** pour la norme vectorisée | `hypot(r,0)==r` pour `167/167` rayons ; `r=1e-158`, `1e-162`, `1e-200` passent |
| Accord générique jusqu'au plus petit subnormal | **NON CORRIGÉ COMPLÈTEMENT** | `8/17` rayons subnormaux échouent ; premier `1e-315`, minimum `5e-324` |
| Quantification scalaire liée à `magnitude * dx / distance` au plus petit subnormal | **NON CORRIGÉ** | `F_ref=-2.0` contre `F_vec=-1.7` à `5e-324` |
| Direction minimum-image non unique à une demi-boîte | **CORRIGÉ PAR REJET DU DOMAINE** | exact, juste au-dessus et `0.6` rejetés par les deux forces et `step`; juste sous `0.5` accepté |
| Specs acceptant `NaN/Inf` | **CORRIGÉ** | `36/36` combinaisons field/value testées rejetées |
| Banque nominale trop petite, sans `N=64`, sans assertion un-pas | **CORRIGÉ EN PARTIE** | validateur 1 024 fixtures, dont 170 à `N=64`, mesure force et un pas |
| Neutralité physique des IDs | **TOUJOURS PASS** | 20 cas trajectoire, différence maximale `0`; null officiel PASS |
| Replay à backend constant | **TOUJOURS PASS** | `0/20` échec bit-à-bit dans le même environnement |
| Perte commune de covariance par translation pour paires quasi-coïncidentes encodées à des positions absolues différentes | **NON CORRIGÉE** | erreur `2.053837599991226e-09` à `r=1e-8`; `2.05343268436e-05` à `r=1e-12` |
| Divergence longue entre backends à trajectoire libre | **NON RÉAUDITÉE / LIMITE TOUJOURS DOCUMENTÉE** | hors du scope borné ; aucun claim d'interchangeabilité trajectorielle n'est fait ici |
| Tests persistants manquants pour oracle asymétrique exact, `nextafter` complet et permutation de stockage | **PARTIELLEMENT NON CORRIGÉ** | les nouveaux tests couvrent `1e-162`, demi-boîte, finitude, `N=64` et un pas ; pas le dernier subnormal ni tous les oracles antérieurs |

## ACTIONS PERFORMED

1. Vérification que HEAD et `origin/main` pointent exactement sur `b8aaaf2` et que le worktree est propre.
2. Inspection du diff `65af67e..b8aaaf2` pour `engine.py`, `specs.py`, `validation/forces.py` et `tests/test_engine.py`.
3. Exécution de toute la suite de tests.
4. Exécution du validateur officiel sur 256 puis 1 024 fixtures.
5. Balayage non persistant de 167 rayons de `1e-158` au plus petit subnormal, avec comparaison force et un pas.
6. Test explicite de la frontière `interaction_range` juste sous, exactement à et juste au-dessus de `box_size/2`, sur les deux backends et `step`.
7. Test de 36 valeurs non finies réparties sur les specs.
8. Replays et permutations d'IDs sur les deux backends.
9. Reprobe borné de la covariance par translation à `r=1e-8` et `r=1e-12`.
10. Aucun code ni test modifié.

## FILES READ

- `edlab/substrates/particle_dynamics/engine.py`
- `edlab/specs.py`
- `edlab/validation/forces.py`
- `edlab/validation/nulls.py`
- `edlab/experiments/baseline.py`
- `tests/test_engine.py`
- Le diff Git du commit `b8aaaf2`.
- `docs/agent_journals/2026-07-10/0400_numerical-validation_RUN-20260710-0343-NUM.md`.

## FILES CREATED OR MODIFIED

- Créé uniquement : `docs/agent_journals/2026-07-10/0421_numerical-reaudit_RUN-20260710-NUM2.md`.
- Aucun fichier de code, test, spec ou résultat modifié.

## COMMANDS / EXPERIMENTS EXECUTED

### Identification exacte du commit

```powershell
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git show -s --format='%H%n%P%n%ci%n%s' b8aaaf2
git diff b8aaaf2^ b8aaaf2 -- edlab/substrates/particle_dynamics/engine.py edlab/specs.py edlab/validation/forces.py tests/test_engine.py
```

### Suite complète

```powershell
& '.\.venv\Scripts\python.exe' -m pytest -q
```

Résultat : `28 passed in 1.14s`.

### Validateur officiel, banque incluant `N=64`

```powershell
& '.\.venv\Scripts\python.exe' -c "from edlab.validation.forces import validate_force_paths; print(validate_force_paths(fixtures=1024))"
```

Résultat :

- fixtures : `1024` ;
- tailles cycliques : `(2,3,8,16,32,64)`, soit 170 fixtures à `N=64` ;
- erreur absolue force maximale : `1.3322676295501878e-15` ;
- erreur force scaled maximale : `0.0002874395839500966` ;
- erreur absolue un-pas maximale : `1.1102230246251565e-16` ;
- erreur un-pas scaled maximale : `9.869460877505616e-06` ;
- tolérance : `1e-12 + 1e-10*abs(reference)` ;
- verdict officiel : `passed=True`.

Le run intermédiaire à 256 fixtures avait également passé : force max `1.3322676295501878e-15`, force scaled `0.0002530167113697451`, un-pas max `1.1102230246251565e-16`, un-pas scaled `6.303866418408212e-06`.

### Balayage quasi-zéro et subnormal

Configuration identique au journal antérieur pour rendre la comparaison directe :

- matrice `[[0.75]]` ;
- `repulsion_strength=1.7` ;
- `short_range=0.02` ;
- `interaction_range=0.2` ;
- `damping=0` ;
- monde unité, deux particules, séparation uniquement sur x ;
- `dt=0.02` pour le test un-pas.

Rayons : `10^-k`, `k=158..323`, plus `np.nextafter(0,1)=5e-324`.

Résumé :

- rayons sondés : `167` ;
- rayons normaux : `150`, échecs `0` ;
- rayons subnormaux : `17`, échecs `8` ;
- `hypot_identity_failures=0` ;
- plus grand rayon en échec : `1e-315` ;
- plus petit : `5e-324` ;
- erreur force maximale : `0.30000000000000004` ;
- erreur position périodique maximale après un pas : `0.00012000000000000899` ;
- erreur vitesse maximale après un pas : `0.005999999999999998`.

Points représentatifs :

| r | Fref x | Fvec x | erreur force | verdict tolérance |
|---:|---:|---:|---:|---|
| `1e-158` | `-1.7` | `-1.7` | `0` | PASS |
| `1e-162` | `-1.6999999999999997` | `-1.7` | `2.220446049250313e-16` | PASS |
| `1e-200` | `-1.7` | `-1.7` | `0` | PASS |
| `1e-300` | `-1.7` | `-1.7` | `0` | PASS |
| `1e-308` | `-1.7` | `-1.7` | `0` | PASS |
| `1e-310` | `-1.7000000000000148` | `-1.7` | `1.4876988529977098e-14` | PASS |
| `1e-314` | `-1.6999999999505935` | `-1.7` | `4.940647890805394e-11` | PASS |
| `1e-315` | `-1.6999999995059343` | `-1.7` | `4.940656772589591e-10` | FAIL |
| `1e-320` | `-1.700098814229249` | `-1.7` | `9.88142292490668e-05` | FAIL |
| `1e-323` | `-1.5` | `-1.7` | `0.19999999999999996` | FAIL |
| `5e-324` | `-2.0` | `-1.7` | `0.30000000000000004` | FAIL |

À `5e-324`, l'erreur après un pas est `0.00012000000000000899` en position périodique et `0.005999999999999998` en vitesse.

### Frontière demi-boîte

Pour `box_size=1` :

- `interaction_range=np.nextafter(0.5,0)` : accepté par `forces_reference`, `forces_vectorized` et `step` ;
- `interaction_range=0.5` : rejeté par les trois chemins avec `ValueError` mentionnant `box_size/2` ;
- `interaction_range=np.nextafter(0.5,+inf)` : rejeté par les trois ;
- `interaction_range=0.6` : rejeté par les trois.

Verdict : PASS pour la convention stricte demandée.

### Scalaires non finis

Valeurs testées pour chaque champ : `NaN`, `+Inf`, `-Inf`.

Champs testés :

- `LawSpec.repulsion_strength` ;
- `LawSpec.short_range` ;
- `LawSpec.interaction_range` ;
- `LawSpec.damping` ;
- `WorldSpec.box_size` ;
- `WorldSpec.initial_speed` ;
- `RunSpec.dt` ;
- `DetectionSpec.connection_radius` ;
- les deux échelles de `PhenotypeSpec` ;
- les deux paramètres de `TrackerSpec`.

Résultat : `0/36` valeurs acceptées, toutes rejetées par `ValueError`. Verdict : PASS.

### Déterminisme et IDs

- 20 trajectoires : 10 seeds, deux backends, `N=16`, 3 types, 50 pas, cadence 7.
- Échecs de replay exact : `0/20`.
- Échecs de neutralité ID : `0/20`.
- Différence physique maximale après permutation bijective des IDs : `0.0`.
- Null officiel `ID_PERMUTATION` : `passed=True`, détail `maximum physical-array difference after 20 steps: 0`.

Verdict : PASS.

### Covariance par translation quasi-coïncidente

Même fixture que le journal antérieur : paire à la couture et copie intérieure géométriquement équivalente, composante transverse `r/3`.

- `r=1e-8` : écart de force entre représentations `2.053837599991226e-09` pour les deux chemins.
- `r=1e-12` : référence `2.0534326843624218e-05`, vectorisé `2.053432684367973e-05`.
- Les chemins restent d'accord entre eux sur chaque représentation.

Ce finding commun de soustraction float64 n'est pas corrigé par `hypot`.

## OBSERVED

- Le commit audité est exactement celui demandé et correspond à `origin/main`.
- La suite complète et la banque nominale renforcée passent.
- Le changement vers `np.hypot` élimine le sous-débordement de la norme vectorisée sur tous les rayons testés.
- Le test persistant ajouté à `1e-162` passe et couvre correctement le défaut pratique initial.
- Le chemin scalaire conserve un ordre d'opérations non robuste aux derniers subnormaux.
- Les validations de domaine et de finitude demandées fonctionnent aux frontières sondées.
- Les IDs restent diagnostiques dans les trajectoires testées.

## INFERRED

- Le défaut résiduel n'est plus dans `hypot` : il est localisé dans l'accumulation scalaire `magnitude * dx / distance`, qui arrondit `magnitude*dx` avant la division.
- Le domaine nominal de la baseline n'est pas remis en cause par des séparations de l'ordre de `1e-315`; le FAIL porte sur l'exigence explicite d'accord jusqu'au domaine subnormal et sur la portée générique du validateur.
- Une écriture normalisant d'abord la direction, par exemple `magnitude * (dx / distance)`, devrait supprimer ce cas x-only, mais cela n'a pas été implémenté ni revendiqué comme testé dans ce run.

## HYPOTHESIS

- Le changement d'ordre dans la référence devrait aligner les deux chemins jusqu'au plus petit subnormal pour les fixtures axiales. Un balayage bidimensionnel et les mêmes tests un-pas seraient encore nécessaires avant de déclarer la réparation complète.

## WHAT WOULD FALSIFY THIS?

- Modifier uniquement l'ordre de normalisation scalaire, puis observer les mêmes huit échecs avec `hypot_identity_failures=0`, réfuterait la cause localisée actuelle.
- Un réaudit complet doit obtenir zéro violation de la tolérance force et un-pas sur la même liste de 167 rayons, y compris `5e-324`, sans relâcher la tolérance.

## FAILURES / DEAD ENDS

- Aucun probe n'a échoué à s'exécuter ou à produire son stdout.
- Aucune grosse banque supplémentaire n'a été lancée après le validateur officiel 1 024 fixtures, conformément au caractère borné du réaudit.

## DECISIONS MADE

- Rendre un verdict global strict **FAIL**, même si le défaut résiduel est hors domaine pratique, parce que la mission demandait explicitement le parcours jusqu'au subnormal.
- Distinguer « norme `hypot` corrigée » de « chemin de force complet corrigé ».
- Ne pas réinterpréter la divergence longue backend-à-backend comme régression et ne pas la réexécuter dans ce réaudit borné.
- Ne modifier aucun code.

## UNRESOLVED RISKS

- Référence scalaire quantifiée pour les derniers subnormaux.
- Le test persistant ne couvre que `1e-162`, pas `1e-315`, `1e-320`, `1e-323` ou `5e-324`.
- Covariance par translation quasi-coïncidente toujours limitée par la représentation float64.
- La permutation de l'ordre de stockage et la table analytique asymétrique complète restent des probes ad hoc antérieurs, pas des tests persistants visibles dans le diff ciblé.
- Le replay exact n'est revendiqué que dans le même process, backend et environnement logiciel.

## HANDOFF

Correctif minimal à faire auditer ensuite :

1. Dans la référence scalaire, normaliser avant de multiplier la magnitude (`magnitude * (dx / distance)` et idem y), ou utiliser une direction mise à l'échelle équivalente.
2. Ajouter un test paramétré au minimum sur `1e-162`, `1e-315`, `1e-320`, `1e-323` et `np.nextafter(0,1)`.
3. Vérifier force **et un pas** avec la tolérance gelée inchangée.
4. Relancer la suite complète et le validateur nominal ; aucun besoin de modifier les seuils scientifiques ou de relancer un screening avant ce gate.

## ENDING GIT STATE

- Branche : `main`.
- HEAD : `b8aaaf2b414a7130bc00e01e82842c0b2d727183` au dernier contrôle avant journal.
- `origin/main` : même SHA.
- Commits créés par ce sous-agent : aucun.
- Push effectué : non.
- Seule modification de ce sous-agent : ce nouveau journal non suivi au moment de sa création.
