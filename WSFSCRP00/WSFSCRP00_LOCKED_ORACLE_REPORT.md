# `WSFSCRP00` — rapport de l'oracle verrouillé

**L'évaluation verrouillée n'a jamais été ouverte.**

L'ordre de précédence déterministe fixe la disposition à l'étape 4 (échec de rang Q2), en amont
de l'étape 7 (évaluation verrouillée). En conséquence :

```
LOCKED_DEV_EVALUATION_FOUNDERS_GENERATED = 6   (64000, 64004, 64008 FAR ; 64007, 64003, 64011 NEAR)
LOCKED_DEV_EVALUATION_OUTCOMES_OPENED    = 0
LOCKED_FEATURE_ARRAYS_OPENED             = 0
LOCKED_SUPERFAMILY_EXECUTED              = 0
LOCKED_ADMISSION_UTILITY_RUN             = 0
MODEL_PREDICTION_FILES_WRITTEN           = 0
LOCKED_FEATURE_BLINDNESS                 = NOT_REACHED
```

Les six fondateurs verrouillés **existent** : ils ont été générés et scellés pendant la tranche de
qualification, avec leurs masques `t0` hachés, parce que l'allocation équilibrée des rôles exige
que tous les candidats soient produits avant toute assignation. Leurs **résultats** n'ont jamais
été calculés, et la superfamille environnementale verrouillée n'a jamais été exécutée, sur aucun
fondateur.

Aucun remplacement de fondateur n'a eu lieu, aucune politique de reprise n'a été invoquée,
aucun sous-ensemble n'a été rescoré.
