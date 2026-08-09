# Corrigendum interprétatif à `DEV_05` — enregistré, non rétroactif

`DEV_05` (`29923e89`) n'est pas modifié. Ses artefacts restent scellés, vérifiés, et sa physique
est réutilisée telle quelle. Ce fichier corrige la **lecture** et lève l'ambiguïté sur l'opérateur.

## 1. Statuts corrigés

```
DEV05_PRIMARY_RESULT =
  LEDGER_VALID_TRACKED_COMPONENT_CONTINUITY_UNDER_FORCED_COUPLED_EXCHANGE

TURNOVER_80            = NOT_REACHED
SOURCE_REPLACEMENT_80  = NOT_REACHED
DECISION_CORRECTED     = RATE_DEPENDENT_REPLACEMENT

BREAKAGE_THRESHOLD_L24 = BRACKETED_BETWEEN_Q400_AND_Q800
BREAKAGE_THRESHOLD_L32 = NOT_REACHED_THROUGH_Q800
DOSE_RANGE_INSUFFICIENT_L32     = true
PLATEAU_ESTABLISHED             = false
AMBIENT_ASSISTANCE_ESTABLISHED  = false
ORGANIZATION_PRESERVATION       = NOT_TESTED
```

`DEV_05` avait retenu `DOSE_RANGE_INSUFFICIENT` comme décision unique. C'était trop faible :
l'effet de cadence y était déjà apparié et répliqué aux deux tailles. `RATE_DEPENDENT_REPLACEMENT`
est la décision correcte, et `DOSE_RANGE_INSUFFICIENT` reste vrai **à L=32 seulement** — à L=24
la gamme n'est pas « insuffisante », elle est **bornée par la rupture** entre Q400 et Q800.

`PLATEAU_ESTABLISHED = false` : aucun plateau n'a été démontré, seulement une croissance
fortement sous-linéaire.

## 2. Statut de l'opérateur — code, instrumentation, sémantique physique

Les trois niveaux sont distincts et `DEV_05` les avait confondus sous une seule étiquette.

```
OPERATOR_CODE_STATUS          = REIMPLEMENTED_PRESEAL
PHYSICAL_SEMANTIC_REPLICATION = REDESIGNED_PRESEAL
PARENT_SIGNAL_WORDING = REPRODUCED_PROSPECTIVELY_UNDER_REDESIGNED_OPERATOR
```

- **Code** : `dr_core.py` est un fichier neuf, il n'importe pas `dsc_core.py` et ne partage aucun
  objet-fonction avec lui. `REIMPLEMENTED_PRESEAL`.
- **Instrumentation** : `REDESIGNED`. Le compteur statique par cellule `credited` a disparu, la
  cohorte incumbent est scindée en `CORE`/`INTERMEDIATE`/`BOUNDARY`, l'atomicité est assertée,
  deux ledgers sont écrits. **Rien de tout cela ne touche le champ de matière.**
- **Sémantique physique** : testée bit à bit sur des états gelés, 36 cas (3 rayons × 4 axes ×
  3 quotas), aucun pas moteur. Résultat :
  - géométrie d'interface **identique membre à membre** (masques puits et source) ;
  - réservoirs et retraits **par cohorte identiques à 0,0** ;
  - champ de matière **non bit-identique** : `max|Δm| = 1,3·10⁻¹⁵`.

  La cause est isolée exactement : `DEV_05` déclare une cellule source inéligible dès
  `m ≥ MMAX − 10⁻¹²`, `DSC_04` dès `m ≥ MMAX`. En rétablissant le prédicat de `DSC_04`, la
  divergence tombe à **0,0** sur les mêmes 36 cas. **La sémantique physique ne diffère donc que
  dans une bande de saturation de 10⁻¹², à l'échelle de l'arrondi flottant, et nulle part
  ailleurs.**

Le critère de la mission est l'équivalence fonctionnelle *exacte* ; 1,3·10⁻¹⁵ ne l'est pas, donc
je conserve l'étiquette conservatrice `REDESIGNED_PRESEAL` — tout en disant précisément que la
différence n'est pas sémantique. C'est la raison pour laquelle on ne peut pas écrire à la fois
« physique exactement identique » et `REDESIGNED_PRESEAL` sans cette explication.

## 3. Deux lectures de `DEV_05` que cette mission renverse

**(a) L'« échafaudage incumbent protégé » était un artefact de normalisation.** `DEV_05`
rapportait `CORE_256_SURVIVAL` et `BOUNDARY_256_SURVIVAL` normalisées par `I₀`, ce qui donnait
l'apparence d'un noyau 4 à 6 fois mieux préservé que la coque. Mais à `t256` le noyau porte
**63 % de I₀** et la coque **17 %**. Normalisée par la masse propre de chaque cohorte à `t256`,
la survie noyau/coque vaut **1,02 à 1,44×**, et le rapport est **le plus élevé chez le SHAM**.
Le forçage **aplatit** le gradient de profondeur au lieu d'épargner le noyau.
⇒ `EXCHANGEABLE_SHELL_WITH_PROTECTED_CORE = NOT_SUPPORTED`.

**(b) L'ambiant n'assiste pas le turnover.** `DEV_05` avait signalé l'ambiant comme « le plus gros
terme non contrôlé » et proposé de le partitionner. La décomposition appariée bloc par bloc montre
que `AMBIENT_DELTA` est **négatif dans tous les bras directs** (−0,004 à −0,028 de M₂₅₆) : la
piste traitée porte **moins** d'ambiant que son sham apparié. L'ambiant n'aide pas, il est
déplacé. Un delta négatif ne prouve pas pour autant un remplacement causal.
⇒ `AMBIENT_ASSISTANCE = NOT_ESTABLISHED`, et le terme `AMBIENT_ASSISTED` reste interdit.

## 4. Portes globales, inchangées

```
ROUTE_E_VERDICT = NONE          AUTONOMOUS_RENEWAL = NOT_TESTED
IDENTITY = NOT_ESTABLISHED      INDIVIDUATION = NOT_ESTABLISHED
LIFE = NOT_ESTABLISHED          GENERALIZATION_BEYOND_LAW_16 = false
```

Plafond de revendication inchangé : `TRACKED_COMPONENT_CONTINUITY_UNDER_FORCED_TURNOVER`.
