# `WSCPL00` — gel du protocole, et où il s'est arrêté

## Ce qui a été gelé avant toute exécution porteuse de résultat

| élément | valeur gelée |
|---|---|
| rôles de données | `FORMULATION_TRAIN` = 61000–61002 ; `MODEL_SELECTION_VALIDATION` et `UNTOUCHED_PILOT_EVALUATION` non alloués |
| découpage | par **bloc fondateur indépendant** et par **famille d'intervention entière** — jamais par instant, cellule, bras ou échantillon voisin |
| candidat point de mesure macro | **branche de dominance** : `signe(masse_A − masse_B)` au moyen du lecteur de sites **gelé** (`domc_core.read_sites`), qui prédate ce programme |
| horizon | `H = 400` pas natifs, fixé avant toute mesure d'intervention |
| familles d'intervention | 5, toutes issues d'opérateurs déjà scellés (manifeste joint) |
| moteur | `PPAIEngine`, `g = +1/3`, **inchangé** : aucune équation, aucun `alive`, aucun gain, aucun limiteur, aucune topologie modifiés |
| budget | 24 démarrages de qualification, 160 de pilote, 12 blocs fondateurs |

## La porte de faisabilité, et pourquoi elle a fermé

Un point de mesure de branche doit satisfaire deux conditions avant qu'un modèle ne soit
construit : être **non dégénéré** (prendre les deux valeurs) et être **réactif à
l'intervention** (avoir une variance de label sous intervention). La seconde a été testée avec
les opérateurs **les plus forts** disponibles — si les plus forts ne bougent pas le label, les
plus faibles ne le bougeront pas.

**Résultat : `NO_VALID_MACRO_BRANCH_ENDPOINT`.** Détail dans le rapport final.

Aucune autre définition de branche n'a été essayée. Enchaîner les points de mesure jusqu'à ce que
l'un bouge serait exactement le magasinage que toute cette chaîne existe pour empêcher, et le
handoff exclut par ailleurs l'entrée dans un attracteur, l'effacement mémoire, la transition rare
et la réponse externe comme points de mesure alternatifs de ce pilote.

## Ce qui n'a donc jamais été gelé, faute d'avoir été atteint

Dimension latente, échelles de blocs mésoscopiques, `alpha`, longueur d'historique macro, espaces
de recherche d'hyperparamètres, budget d'optimisation, marges pré-gelées de Brier et de
calibration, bornes `eta`, contrôle par permutation. **Aucune de ces valeurs n'a été choisie**,
donc aucune n'a pu être choisie en regardant un résultat.
