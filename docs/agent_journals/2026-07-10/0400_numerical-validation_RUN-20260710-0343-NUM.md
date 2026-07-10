# Audit numérique indépendant — CORE V0

## AGENT / ROLE

- Sous-agent `numerical_validation`.
- Rôle : audit numérique indépendant des forces, des conventions périodiques et asymétriques, du déterminisme et de l'invariance aux IDs diagnostiques.

## RUN ID

- `RUN-20260710-0343-NUM`

## START TIME

- `2026-07-10T04:00:00+02:00` environ.
- Première capture explicite de l'horloge pendant le run : `2026-07-10T04:02:08.765+02:00`.

## END TIME

- `2026-07-10T04:11:19.072+02:00` pour la dernière mesure avant rédaction du journal.

## STARTING GIT STATE

- Repository : `C:/Users/tommy/Documents/ising v3`.
- Branche : `main`, sans commit (`No commits yet on main`) au premier contrôle.
- HEAD : inexistant.
- Worktree : dirty, avec `.gitignore`, `.runtime/`, `docs/`, `edlab/`, `pyproject.toml` et `tests/` non suivis.
- Le repository a été initialisé et modifié concurremment par l'agent principal. Je n'ai pas créé ces fichiers.

## ASSIGNED SCOPE

- Inspecter les deux chemins de forces de CORE V0.
- Auditer les conventions périodiques et la direction receveur/source d'une matrice asymétrique.
- Tester le déterminisme et l'invariance des états physiques aux IDs diagnostiques.
- Exécuter la suite existante.
- Chercher activement des contre-exemples aux cutoffs, à `r` proche de zéro, aux coutures périodiques et sur des mondes aléatoires.
- Ne modifier aucun code. Seul ce journal pouvait être créé/modifié.

## VERDICT

**REQUEST CHANGES pour déclarer le chemin de forces génériquement validé.**

- Le domaine nominal de la baseline CORE V0 observé ici est numériquement cohérent : 10 000 fixtures du validateur courant passent, et une banque ad hoc de 1 000 mondes incluant `N = 32` et `N = 64`, coutures et seuils adjacents ne produit aucune violation de la tolérance gelée `1e-12 + 1e-10*abs(F_ref)`.
- Un contre-exemple hors de la banque nominale invalide néanmoins l'assertion générique d'accord des deux chemins : pour des séparations très petites, le calcul vectorisé `sqrt(dx**2 + dy**2)` sous-déborde avant `np.hypot` dans la référence. La première violation de la tolérance dans le balayage décimal apparaît à `r = 1e-158`. À `r <= 1e-162`, le chemin vectorisé voit une distance nulle et retourne une force nulle tandis que la référence retourne environ `1.7` en norme.
- Une configuration antipodale exacte à une demi-boîte n'a pas de direction minimale unique. Si `interaction_range > box_size/2`, la convention `round/rint` choisit une direction qui peut s'inverser après une translation globale suivie du wrap. Les lois de la baseline sont protégées de ce cas (`interaction_range <= 0.22`, `box_size = 1`), mais l'API ne contraint ni ne documente cette limite.
- Le replay est bit-à-bit déterministe à backend constant dans les cas exécutés, et les IDs diagnostiques n'affectent pas la physique. En revanche, deux trajectoires parties du même état avec les backends `reference` et `vectorized` divergent fortement après plusieurs centaines de pas dans 2 cas baseline-like sur 3. Cela ne réfute pas l'accord ponctuel des forces : c'est une limite de reproductibilité attendue dans un système sensible aux arrondis. Le backend doit rester gelé et enregistré.

## ACTIONS PERFORMED

1. Lecture des deux implémentations de forces et du validateur.
2. Lecture du conteneur d'état, des specs, de l'initialisation, du pas et de la simulation.
3. Lecture des tests moteur, IDs, entités, tracker et continuité pertinents.
4. Exécution de toute la suite de tests existante.
5. Extension non persistante du validateur courant à 10 000 fixtures.
6. Construction en mémoire d'oracles analytiques à deux particules : asymétrie, couture, seuils `nextafter`, coïncidence et quasi-coïncidence.
7. Banque en mémoire de 1 000 mondes aléatoires/adversariaux avec tailles `(2, 3, 8, 32, 64)`, 1 à 5 types, matrices asymétriques et injections de coutures/cutoffs.
8. Tests de permutation de labels ID et de permutation conjointe de l'ordre de stockage.
9. Replays de trajectoires à backend constant et comparaison de trajectoires entre backends.
10. Probe secondaire des specs avec scalaires `NaN/Inf`.
11. Aucun fichier temporaire ni résultat expérimental persistant n'a été créé par ces probes.

## FILES READ

- `edlab/substrates/particle_dynamics/engine.py`
- `edlab/validation/forces.py`
- `edlab/state.py`
- `edlab/specs.py`
- `edlab/entities/detection.py`
- `edlab/entities/tracking.py`
- `edlab/observables/phenotype.py`
- `edlab/observables/continuity.py`
- `edlab/validation/nulls.py`
- `edlab/experiments/baseline.py`
- `tests/test_engine.py`
- `tests/test_entities.py`
- `tests/test_tracker.py`
- `tests/test_continuity.py`
- `tests/test_experiment_pipeline.py`
- `tests/test_runtime_lock.py`
- Les deux prompts attachés concernant la mission et le journal obligatoire.
- `docs/agent_journals/2026-07-10/0343_main-agent_run-001.md`
- `docs/agent_journals/2026-07-10/0347_protocol-audit_RUN-20260710-0343-PROT.md`

## FILES CREATED OR MODIFIED

- Créé uniquement : `docs/agent_journals/2026-07-10/0400_numerical-validation_RUN-20260710-0343-NUM.md`.
- Aucun fichier de code, test, spec, résultat ou configuration n'a été modifié.

## COMMANDS / EXPERIMENTS EXECUTED

### Suite existante

```powershell
& '.\.venv\Scripts\python.exe' -m pytest -q
```

Résultat : `16 passed in 0.86s`.

### Validateur courant étendu

```powershell
& '.\.venv\Scripts\python.exe' -c "from edlab.validation.forces import validate_force_paths; print(validate_force_paths(fixtures=10000))"
```

Résultat :

- fixtures : `10000` ;
- erreur absolue maximale : `8.881784197001252e-16` ;
- erreur scaled maximale : `0.00016819213505243037` ;
- verdict du validateur : `passed=True`.

### Banque aléatoire/adversariale non persistante

- RNG : `np.random.default_rng(0xED1AB)`.
- 1 000 fixtures.
- `N in {2, 3, 8, 32, 64}`.
- 1 à 5 types.
- `box_size` logarithmiquement varié d'environ `0.1` à `5`.
- `interaction_range` limité à `0.08..0.45 * box_size` pour cette banque.
- Injection cyclique de paire à la couture, juste sous/au-dessus/au cutoff court et au cutoff d'interaction.
- Comparaison force, un pas, relabeling ID, et équivariance à la permutation des lignes.

Résultats :

- violations de la tolérance force : `0/1000` ;
- erreur absolue force maximale : `3.552713678800501e-15` ;
- erreur scaled maximale : `0.0011098308074627846` ;
- erreur physique maximale après un pas : `4.440892098500626e-16` ;
- échecs exacts après relabeling ID : `0/1000` ;
- erreur maximale d'équivariance à l'ordre, vectorisé : `5.329070518200751e-15` ;
- erreur maximale d'équivariance à l'ordre, référence : `4.440892098500626e-15` ;
- violations de tolérance liées à l'ordre : `0/1000`.

### Oracle asymétrique

Configuration : deux particules de types `(0,1)`, distance `0.1`, `short_range=0.02`, `interaction_range=0.2`, matrice `[[0,1],[-0.5,0]]`.

Oracle analytique :

```text
F0x = 0.8888888888888888
F1x = 0.4444444444444444
```

Résultats sur paire intérieure et paire équivalente à la couture :

- erreur référence/oracle maximale : `2.220446049250313e-16` ;
- erreur vectorisé/oracle maximale : `3.3306690738754696e-16` ;
- désaccord maximal entre chemins : `1.1102230246251565e-16`.

Le signe positif des deux forces est attendu : le coefficient du receveur de type 1 est négatif et son vecteur vers la source pointe vers `-x`. Aucune conservation de quantité de mouvement n'est attendue pour une matrice asymétrique.

### Cutoffs avec `nextafter`

Configuration : coefficient `0.75`, répulsion `1.7`, `short_range=0.02`, `interaction_range=0.2`.

- Juste sous le cutoff court : `F0x = -3.774758283725532e-16` dans les deux chemins.
- Exactement au cutoff court : `F0x = 0` dans les deux chemins ; la branche utilisée est la branche intermédiaire, dont l'enveloppe vaut zéro.
- Juste au-dessus : `F0x = 0` dans les deux chemins à cette précision.
- Juste sous le cutoff d'interaction : `F0x = 1.6653345369377348e-16` dans les deux chemins.
- Exactement au cutoff d'interaction : `F0x = 0`, car le support est strictement `distance < interaction_range`.
- Juste au-dessus : `F0x = 0`.
- Désaccord maximal entre chemins dans cette table : `0`.

### Balayage `r` proche de zéro

Balayage : `r = 10^-k`, `k=1..323`, plus le plus petit subnormal positif float64.

- Nombre de rayons non nuls sondés : `324`.
- Première violation de `1e-12 + 1e-10*abs(F_ref)` : `r=1e-158`.
- À `r=1e-158` : désaccord force `1.388924264489333e-08`, tolérance `1.71e-10`.
- À `r=1e-161` : `F_ref=-1.7`, `F_vec=-1.7101791018167187`, désaccord `0.010179101816718772`.
- À `r=1e-162` : `F_ref≈-1.7`, `F_vec=0`, désaccord `≈1.7`.
- À `r=1e-200` : `F_ref=-1.7`, `F_vec=0`, désaccord `1.7`.
- Au plus petit subnormal positif `5e-324`, le chemin référence quantifie lui aussi la force (`-2.0`) à cause de l'ordre `magnitude * dx / distance`, tandis que le chemin vectorisé retourne `0`; désaccord maximal observé `2.0`.

Effet après un pas `dt=0.02` :

| r | max position périodique | max vitesse |
|---:|---:|---:|
| `1e-158` | `5.555697069926924e-12` | `2.7778485067742054e-10` |
| `1e-161` | `4.071640726688308e-06` | `0.00020358203633437377` |
| `1e-162` | `0.0006800000000000139` | `0.034` |
| `1e-200` | `0.0006800000000000139` | `0.034` |

Cause directement lue et reproduite : la référence utilise `np.hypot(dx,dy)` ; le vectorisé utilise `sqrt(sum(displacement*displacement))`, donc le carré sous-déborde avant la racine.

### Couture, translation et demi-boîte

- La paire asymétrique à la couture et sa paire intérieure ont donné les mêmes forces à `3.33e-16` près de l'oracle.
- Pour des paires presque coïncidentes encodées à la couture et à l'intérieur, les deux chemins partagent une perte de covariance par translation due à l'annulation dans la soustraction des positions :
  - séparation `1e-8` avec composante transverse `r/3` : différence de force entre représentations `2.053837599991226e-09` ;
  - séparation `1e-12` : différence `2.0534326843624218e-05` ;
  - les deux chemins restent d'accord entre eux dans ces cas, donc leur comparaison mutuelle ne détecte pas ce défaut commun de représentation float64.
- Cas antipodal exact, `box_size=1`, distance `0.5`, `interaction_range=0.75` : les deux chemins donnent `±0.7692307692307692`. Après translation globale et wrap, les directions s'inversent ; différence maximale `1.5384615384615383` dans chaque backend.
- Cette ambiguïté antipodale n'est pas active dans la baseline actuelle, dont la portée maximale lue est inférieure à `box_size/2`.

### Déterminisme et IDs

- 20 cas de trajectoire : 10 seeds, deux backends, 16 particules, 50 pas, cadence 7.
- Échecs de replay exact dans le même process/backend : `0/20`.
- Échecs d'identité physique après remplacement des IDs par une permutation bijective disjointe : `0/20`.
- Null officiel `ID_PERMUTATION` : `passed=True`, différence maximale des tableaux physiques après 20 pas : `0`.
- Null officiel `STATIC_MOTIF_WITH_MATERIAL_FLUX` : `passed=True`, `P=1.0`, `M=0.0` ; ce résultat n'a pas été interprété comme phénomène scientifique.

### Divergence longue entre backends

Trois configurations baseline-like, `N=64`, `steps=600`, mêmes états initiaux :

| Law/seed | max position finale périodique | max vitesse finale |
|---|---:|---:|
| `0 / 101` | `0.1397165896811341` | `1.2414910144476696` |
| `1 / 202` | `0.4189811229676727` | `0.8593449179740977` |
| `2 / 303` | `3.4015843041249744e-05` | `0.00011410736173800978` |

- Pour `law 0 / seed 101`, la divergence combinée position/vitesse dépasse `1e-12` au pas 162, `1e-6` au pas 437, `1e-3` au pas 485 et `0.1` au pas 534.
- Pour `law 1 / seed 202`, les mêmes seuils sont franchis aux pas 165, 336, 392 et 438.
- Ces trajectoires ne doivent pas être utilisées comme exigence d'égalité backend-à-backend. Le test indépendant pertinent reste la force sur le même état et l'erreur à un pas ; la reproductibilité scientifique doit fixer le backend.

### Specs non finies

Les constructeurs suivants ont été acceptés sans exception :

- `LawSpec(..., repulsion_strength=NaN)` ;
- `LawSpec(..., damping=NaN)` ;
- `WorldSpec(box_size=NaN)` ;
- `WorldSpec(box_size=Inf)` ;
- `WorldSpec(initial_speed=NaN)` ;
- `RunSpec(seed=1, dt=NaN)`.

Ce probe n'affirme pas que l'exécution les accepte silencieusement jusqu'au bout : les contrôles de finitude de `ParticleState` font échouer plusieurs chemins ultérieurement. Il observe uniquement que les specs ne rejettent pas ces scalaires à leur frontière d'entrée.

## OBSERVED

- Les deux chemins sont structurellement séparés : boucle scalaire et tensorisation all-pairs.
- L'ordre de matrice est bien `interaction[receiver, source]` dans les deux chemins.
- Les seuils sont cohérents entre chemins sur les fixtures exactes exécutées.
- Les tests existants passent tous au snapshot du code audité.
- L'accord nominal est largement à l'intérieur de la tolérance gelée.
- Le contre-exemple quasi-coïncident provoque une violation majeure, pas une simple différence au dernier bit.
- La convention périodique à demi-boîte est non unique et dépend de la représentation après wrap lorsqu'elle est physiquement active.
- Les IDs ne sont pas lus dans les fonctions de forces et n'ont modifié aucun tableau physique dans les probes.
- Le même backend rejoue exactement dans le même environnement ; les backends ne restent pas trajectoriellement interchangeables sur 600 pas.
- Les specs acceptent plusieurs scalaires `NaN/Inf`.

## INFERRED

- Les résultats de la baseline utilisant le backend vectorisé ne sont pas invalidés par le seul contre-exemple subnormal : les distances `1e-158` ne correspondent pas à une échelle physiquement résolue du monde nominal float64. En revanche, le composant ne doit pas être déclaré génériquement validé tant que sa politique de singularité/quasi-coïncidence n'est pas fixée et testée.
- La divergence longue entre backends est compatible avec une amplification dynamique de différences ponctuelles de quelques ulps. Elle impose de comparer les chemins sur le même état, pas de demander des trajectoires identiques indéfiniment.
- La limitation `interaction_range < box_size/2` des lois actuelles protège le vertical slice de l'ambiguïté antipodale par coordonnée, mais cette protection est accidentelle tant qu'elle n'est ni validée ni documentée au couplage `LawSpec/WorldSpec`.
- Le validateur courant est trop doux pour les claims de robustesse : ses 32 fixtures ont `N <= 16` et n'injectent pas de quasi-coïncidence, demi-boîte, couture exacte ou `nextafter` de façon explicite.

## HYPOTHESIS

- Les divergences longues observées sont principalement dues à la sensibilité/chaoticité et aux changements discrets de voisinage près du cutoff, plutôt qu'à une inversion systématique de convention entre backends. Cette interprétation est compatible avec l'accord à un pas, mais aucun exposant de Lyapunov ni ablation des cutoffs n'a été mesuré ici.
- La baseline nominale ne rencontre probablement jamais les rayons subnormaux, mais aucun artefact de trajectoire brute permettant de vérifier le minimum de toutes les séparations n'a été inspecté dans ce run.

## WHAT WOULD FALSIFY THIS?

- Pour la cause du sous-débordement : remplacer dans une branche test le calcul de norme vectorisé par une norme mise à l'échelle ou `hypot`, normaliser avant de multiplier dans la référence, puis montrer que les mêmes cas `1e-158..5e-324` restent en désaccord majeur réfuterait l'explication actuelle.
- Pour la divergence sensible : exécuter les deux backends en arithmétique plus précise ou avec une loi lisse sans cutoff et constater le même calendrier de divergence forte affaiblirait l'hypothèse d'amplification d'arrondis/cutoffs.
- Pour la sûreté de la baseline : observer dans ses trajectoires des séparations proches de la zone `<=1e-158` invaliderait l'inférence que ce contre-exemple est hors domaine nominal.
- Pour l'invariance ID : trouver un état physique identique où un simple relabeling bijectif des IDs change force, position, vitesse, détection physique ou topologie du tracker réfuterait le verdict actuel.

## FAILURES / DEAD ENDS

- Une première tentative de lecture de fichiers avec `$args[0]` dans une commande PowerShell n'a pas transmis l'argument ; les fichiers ont été relus avec des chemins littéraux directs.
- Deux gros probes combinés ont terminé sans stdout récupérable via l'orchestrateur après un yield long. Ils ont été redécoupés et réexécutés en petits probes ; seuls les résultats effectivement visibles ci-dessus sont consignés.
- Aucun paquet de haute précision ni backend tiers n'a été ajouté, afin de respecter la contrainte de non-modification et de rester sur l'environnement réellement utilisé.

## DECISIONS MADE

- Classer le domaine nominal comme **PASS conditionnel**, mais le claim générique de validation des forces comme **REQUEST CHANGES**, au lieu de masquer le cas subnormal comme non pertinent.
- Ne pas classer la divergence à 600 pas comme bug de convention : l'accord même-état et un-pas passe, tandis que le replay backend-constant est exact.
- Traiter le cas demi-boîte comme une limite de contrat à interdire ou documenter, pas comme une inversion entre les deux implémentations : elles appliquent la même convention.
- Ne modifier aucun code ni test conformément au scope.

## UNRESOLVED RISKS

- Politique explicite absente pour les particules exactement coïncidentes ou presque coïncidentes : actuellement `r=0` est silencieusement sans interaction, alors que `r>0` arbitrairement petit tend vers une répulsion finie.
- Norme vectorisée non robuste au sous-débordement et calcul scalaire `magnitude * dx / distance` quantifié aux plus petits subnormaux.
- Covariance par translation limitée par la soustraction de positions proches à des coordonnées absolues différentes ; les deux chemins partagent ce risque.
- Ambiguïté de minimum-image à une demi-boîte lorsque la portée l'autorise.
- Absence de validation `isfinite` pour plusieurs scalaires de specs.
- Tests persistants incomplets : pas d'oracle de magnitude asymétrique pour les deux backends, pas de banque `N=32/64`, pas de `nextafter`, pas de quasi-coïncidence, pas de permutation de l'ordre de stockage, pas d'assertion un-pas dans le validateur officiel.
- Aucun test cross-platform/BLAS/NumPy n'a été effectué ; « exact » signifie ici même process, Python et NumPy de l'environnement courant.

## HANDOFF

Priorité recommandée avant d'étiqueter les forces « validated » :

1. Fixer explicitement la politique `r≈0` : norme robuste, ordre de normalisation robuste, ou softening/minimum separation préenregistré ; ne pas simplement relâcher la tolérance.
2. Ajouter un oracle persistant à `r=1e-158`, `1e-161`, `1e-162` et un cas coïncident, avec résultat attendu documenté.
3. Ajouter l'oracle asymétrique de magnitude sur les deux backends, les six `nextafter` de cutoff, une couture, `N=32/64`, un pas d'intégration et la permutation de stockage.
4. Interdire/valider `interaction_range >= box_size/2` au couplage monde/loi, ou documenter exactement l'ambiguïté antipodale admise.
5. Rejeter les scalaires non finis dans les specs.
6. Garder `vectorized` gelé pour les résultats de screening et consigner le backend dans chaque manifeste ; ne pas mélanger des trajectoires produites par les deux backends.

## ENDING GIT STATE

- Branche : `main`.
- HEAD observé avant rédaction : `c7fd8e7481fd3807ed36976db5bbef2fe3ea7dad` (`experiment: record CORE V0 baseline and freeze holdout`), créé concurremment par l'agent principal.
- Commits créés par ce sous-agent : aucun.
- Push effectué par ce sous-agent : non.
- Modifications de ce sous-agent : uniquement ce journal.
- Au contrôle avant rédaction, trois artefacts `results/BASELINE-COREV0-20260710-001/*candidate_audit*` étaient non suivis ; ils sont apparus concurremment et ne proviennent pas de cet audit.
