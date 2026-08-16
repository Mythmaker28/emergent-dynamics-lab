# MYQBD01 — dérivation d'une borne `Q` minoritaire, brut uniquement
## Rapport final — zéro run scientifique

```
MISSION            MINORITY-Y-Q-BOUND-DERIVATION-01
PARENT             PROSPECTIVE-MINORITY-CHANNEL-REACHABILITY-01 (réparé)
PARENT_TIP         8c2afa32e1e19ecf7ee5ff6e803dbb50cf2f0367
BRANCHE            codex/minority-y-q-bound-derivation-01
FINAL_DISPOSITION  EXISTING_Q_DATA_INSUFFICIENT__PROSPECTIVE_Q_CALIBRATION_REQUIRED
ARCHITECTURE       NOT_ESTABLISHED
SCIENTIFIC_RUNS    0
```

Les 28 bras OBFOR01 sont, sans exception, un **jeu de développement** :
`POST_OUTCOME_DEVELOPMENT_DIAGNOSTIC`. Aucune borne sur `Q` n'a été gelée avant leur exécution.
Ils servent à découvrir la structure de l'environnement et à concevoir un test futur ; ils ne
prouvent aucune fenêtre `kY`, aucune persistance, aucune séparation, ni reproduction ni hérédité.

## Réponses aux dix questions

1. **Le `Q` enregistré correspond-il à la phase d'événement de l'ordonnanceur ?** Oui,
   **exactement**. Écrit dans `pre_react` sur l'état post-diffusion pré-réaction, il est le
   paramètre `n` exact du binôme de naissance `Y`, à chaque pas. `Q_LEDGER_EVENT_EXACT`.
2. **Quelle information indépendante : 28 bras ou 308 000 trames ?** **28 bras** (14 par branche).
   Le temps d'autocorrélation intégré vaut ~7–9, donc les 9 000 trames par bras ne sont pas
   9 000 répliques. Toute incertitude de branche vient des 14 moyennes de bras.
3. **`β = kY·E[Q]` suffit-il ?** Non : `SCALAR_Q_REDUCTION_VALID_ONLY_FOR_FIRST_BIRTH`. Exact pour
   la première naissance d'un seul `Y` en régime non saturé ; faux au-delà (dépletion de `SY`,
   corrélation temporelle, écart moyenne vs croissance multiplicative, exposition de descendant).
4. **Le `Q` organisateur décrit-il l'exposition du descendant ?** **Non**. Le registre par pas est
   scalaire, à la cellule organisatrice seule ; les tableaux spatiaux complets n'existent qu'au
   **pas terminal**. `Q_POSITION(x,t)` d'un descendant séparé est **non récupérable**.
   `ORGANISER_ONLY_ENVIRONMENT_AVAILABLE`.
5. **L'opérateur exact à deux `Y` est-il identifiable ?** **Non** :
   `NOT_IDENTIFIABLE_FROM_ORGANISER_ONLY_LEDGER`. Deux `Y` co-localisés partagent un seul pool de
   candidats — le processus n'est pas Galton–Watson — et deux `Y` séparés ont des environnements
   différents non enregistrés.
6. **La rétroaction de `Y` est-elle contrôlée ?** Seulement pour la première naissance. L'archive
   a `kY = 0`, donc la dépletion de `SY` par une lignée active est absente ;
   `FROZEN_ENVIRONMENT_RARE_Y_APPROXIMATION_WITH_CERTIFIED_ERROR`. Une naissance retire un `SY`
   local (≈ 100 % de la moyenne ~0,99), récupéré à ~0,20/pas ; au-delà de la première naissance
   l'erreur n'est pas bornée depuis l'archive.
7. **La région mobile est-elle non vide sur les 14 bras ?** La région n'est **pas constructible**
   depuis un registre organisateur-seul. Diagnostic constructible : la première naissance est
   identifiable (`kY ∈ [3,2×10⁻⁵, 3,9×10⁻⁵]` pour une naissance attendue), mais chaque bras mobile
   a `Q10 = 0` — aucun plancher d'exposition de queue basse.
8. **Une calibration prospective de `Q` est-elle nécessaire ?** **Oui**.
9. **Un changement d'architecture est-il structurellement justifié ?** **Non**. Sous
   l'environnement admissible le plus favorable, une lignée un-`Y` est surcritique et survit :
   l'opérateur exact ne démontre aucune impossibilité. Un registre manquant n'est pas une preuve
   structurelle.
10. **Prochaine éligibilité unique :** `PROSPECTIVE_Q_ENVIRONMENT_CALIBRATION_01`.

## Ce qui manque exactement

1. Des tableaux environnementaux **résolus en position et par pas** (`nX, nSY, free`) pour les
   positions de descendant de la branche mobile.
2. Un opérateur de lignée à deux `Y` **identifiable**, qui exige le point 1.
3. Une erreur de rétroaction **contrôlée au-delà** de la première naissance.
4. Une **exposition de queue basse positive** (les 14 bras mobiles ont `Q10 = 0`).

## Conformité zéro-run

Sentinelle agrégée sur tous les processus : `ENGINE_CONSTRUCT_CALLS = ENGINE_ADVANCE_CALLS =
SCIENTIFIC_WORLD_STARTS = SCIENTIFIC_SEEDS_OPENED = NEW_PHYSICS_ARRAYS_WRITTEN = 0`, témoin système
de fichiers sur toutes les racines de sortie. Tous les calculs sont des recomputations
déterministes exactes (énumération, PGF, chaîne de Markov finie) sur des tableaux déjà committés.

```
H3_STATUS = NOT_TESTED   REPRODUCTION_STATUS = NOT_TESTED
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED   HISTORICAL_WINDOW_STATUS = NOT_PORTABLE
X_LAWSPEC_BASELINE = UNCHANGED   ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
SCIENTIFIC_RUNS_USED = 0   TOMMY_ACTION_REQUIRED = NONE
```
