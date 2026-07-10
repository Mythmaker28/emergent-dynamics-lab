# Réaudit numérique final du commit `eebd7fa`

## AGENT / ROLE

- Sous-agent `numerical_validation`, audit numérique final borné.

## RUN ID

- `RUN-20260710-NUM3`

## START TIME

- `2026-07-10T04:29:12.528+02:00`.

## END TIME

- `2026-07-10T04:30:03.640+02:00` avant rédaction.

## STARTING GIT STATE

- Repository : `C:/Users/tommy/Documents/ising v3`.
- Branche : `main`.
- HEAD et `origin/main` : `eebd7fa8292aa3bc089f0c2a991e451888f7ebe3`.
- Commit : `fix: eliminate residual subnormal force error`.
- Parent : `b8aaaf2b414a7130bc00e01e82842c0b2d727183`.
- Worktree : clean.

## PRIOR JOURNALS REFERENCED

- `docs/agent_journals/2026-07-10/0400_numerical-validation_RUN-20260710-0343-NUM.md`.
- `docs/agent_journals/2026-07-10/0421_numerical-reaudit_RUN-20260710-NUM2.md`.

## ASSIGNED SCOPE

- Vérifier uniquement le résiduel numérique sur le commit exact `eebd7fa`.
- Exécuter les 29 tests.
- Balayer les 167 rayons de `1e-158` à `5e-324`.
- Exécuter la banque officielle 1 024 fixtures, force et un pas.
- Confirmer rapidement les rejets demi-boîte et non-finis.
- Ne modifier aucun code ; créer seulement ce journal.

## VERDICT

**PASS exact sur tout le scope demandé.**

- `29 passed`.
- Balayage : `167/167` cas force et un-pas exactement égaux entre backends ; erreur maximale `0.0`.
- Banque officielle 1 024 : force et un-pas, erreurs absolues et scaled maximales `0.0`, `passed=True`.
- Demi-boîte : tous les cas interdits sondés rejetés ; portée juste sous la limite acceptée.
- Non-finis : smoke checks inchangés, tous rejetés.

Le finding résiduel de NUM2 est corrigé : la référence normalise maintenant `dx/distance` et `dy/distance` avant d'appliquer la magnitude.

## ACTIONS PERFORMED

1. Vérification de HEAD, `origin/main`, parent et worktree.
2. Inspection du diff ciblé de `engine.py` et `tests/test_engine.py`.
3. Exécution de la suite complète.
4. Exécution du validateur officiel à 1 024 fixtures.
5. Exécution du balayage exact des 167 rayons avec force et un pas.
6. Smoke checks demi-boîte et non-finis.
7. Aucune exploration additionnelle.

## FILES READ

- `edlab/substrates/particle_dynamics/engine.py`
- `tests/test_engine.py`
- Les deux journaux numériques antérieurs cités ci-dessus.

## FILES CREATED OR MODIFIED

- Créé uniquement : `docs/agent_journals/2026-07-10/0429_numerical-final-reaudit_RUN-20260710-NUM3.md`.
- Aucun code, test, résultat ou spec modifié.

## COMMANDS / EXPERIMENTS EXECUTED

### Suite

```powershell
& '.\.venv\Scripts\python.exe' -m pytest -q
```

Résultat : `29 passed in 1.15s`.

### Banque officielle

```powershell
& '.\.venv\Scripts\python.exe' -c "from edlab.validation.forces import validate_force_paths; print(validate_force_paths(fixtures=1024))"
```

Résultat :

```text
fixtures=1024
max_absolute_error=0.0
max_scaled_error=0.0
max_one_step_absolute_error=0.0
max_one_step_scaled_error=0.0
absolute_tolerance=1e-12
relative_tolerance=1e-10
passed=True
```

La banque inclut les tailles cycliques `(2,3,8,16,32,64)`.

### Balayage quasi-zéro/subnormal

- Rayons : `10^-k` pour `k=158..323`, plus `np.nextafter(0,1)=5e-324`.
- Configuration : même loi que NUM2 (`repulsion_strength=1.7`, `short_range=0.02`, `interaction_range=0.2`, `dt=0.02`).
- Cas : `167`.
- Violations de tolérance : `0`.
- Cas exactement égaux pour force, position un-pas et vitesse un-pas : `167/167`.
- Erreur force maximale : `0.0`.
- Erreur force scaled maximale : `0.0`.
- Erreur position un-pas maximale : `0.0`.
- Erreur vitesse un-pas maximale : `0.0`.
- Échecs `hypot(r,0)==r` : `0`.

Points auparavant critiques, tous exacts :

| r | Fref x | Fvec x | erreur force | erreur un-pas |
|---:|---:|---:|---:|---:|
| `1e-158` | `-1.7` | `-1.7` | `0` | `0` |
| `1e-162` | `-1.7` | `-1.7` | `0` | `0` |
| `1e-315` | `-1.7` | `-1.7` | `0` | `0` |
| `1e-320` | `-1.7` | `-1.7` | `0` | `0` |
| `1e-323` | `-1.7` | `-1.7` | `0` | `0` |
| `5e-324` | `-1.7` | `-1.7` | `0` | `0` |

### Smoke checks de contrat

- `interaction_range in {0.5, nextafter(0.5,+inf), 0.6}` : `6/6` appels de forces rejetés.
- `interaction_range=nextafter(0.5,0)` : `2/2` backends acceptent.
- `LawSpec(damping=NaN)`, `WorldSpec(box_size=Inf)`, `RunSpec(dt=-Inf)` : `3/3` rejetés.

## OBSERVED

- Le commit exact demandé est audité et correspond à `origin/main`.
- Le changement d'ordre de calcul supprime toutes les divergences du balayage NUM2.
- Le nouveau test persistant vérifie explicitement le plus petit subnormal positif.
- Aucun écart force ou un-pas n'est observé dans les deux banques exécutées.

## INFERRED

- Le résiduel identifié dans NUM2 est corrigé pour les fixtures et la tolérance préenregistrées.
- Ce PASS est un résultat de validation numérique du moteur, pas une preuve du phénomène scientifique recherché.

## HYPOTHESIS

- Aucune nouvelle hypothèse scientifique n'a été introduite.

## WHAT WOULD FALSIFY THIS?

- Une réexécution du même commit et environnement produisant une différence non nulle ou un test rouge invaliderait ce PASS.
- Un nouvel état fini dans le domaine autorisé dépassant la tolérance devrait être consigné comme nouveau finding, sans réécrire ce journal.

## FAILURES / DEAD ENDS

- Aucun.

## DECISIONS MADE

- Classer le gate numérique demandé **PASS**, sans prolonger l'audit au-delà du scope.
- Ne modifier ni code ni tolérance.

## UNRESOLVED RISKS

- Le PASS est limité au float64, au process et à l'environnement logiciel courant.
- Les limites scientifiques et la divergence possible de trajectoires longues entre backends restent hors de ce réaudit final borné.

## HANDOFF

- Le gate numérique résiduel est fermé sur `eebd7fa`.
- Aucun correctif supplémentaire n'est requis par ce scope avant la prochaine étape décidée par l'agent principal.

## ENDING GIT STATE

- Branche : `main`.
- HEAD et `origin/main` : `eebd7fa8292aa3bc089f0c2a991e451888f7ebe3` avant création du journal.
- Commit créé : aucun.
- Push : non.
- Seule modification de ce sous-agent : ce journal.
