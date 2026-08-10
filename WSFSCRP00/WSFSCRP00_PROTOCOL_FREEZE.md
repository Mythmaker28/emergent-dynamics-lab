# `WSFSCRP00` — gel du protocole

Tout ce qui suit a été écrit et haché **avant** la génération du premier candidat
(`WSFSCRP00_FREEZE_PRE_GENERATION.json`), puis exécuté de haut en bas.

| élément | valeur gelée |
|---|---|
| file de candidats | 16 entrées, graines `64000–64015`, géométries alternées `FAR`/`NEAR` |
| espace de noms | disjoint de `61000–61009` (DEV exposé) et de `62000–62009` (**tenu à l'écart du projet, jamais lu**) |
| admissibilité | exactement deux composantes éligibles à `t0` ; rejet et passage à l'entrée suivante sinon |
| grappe d'ascendance | une par graine du générateur ; `seed_state` est tiré indépendamment par graine |
| allocation des rôles | règle de hachage équilibrée déterministe sur l'**identifiant opaque**, sans inspecter l'état |
| point de mesure | deux canaux à support figé (spécification jointe) |
| grille `H`, horizon | héritée : pas natifs 40…400, horizon 400 |
| superfamilles | 2 TRAIN, 1 LOCKED ; **aucune quatrième famille créée** |
| plafond de preuve | `RESPONSE_INFORMED_HELD_OUT_SINGLE_SUPERFAMILY_TRANSFER`, `STRICT_PROSPECTIVE_OUT_OF_FAMILY = false` |
| budget | 48 qualification, 144 post-porte, 192 total |

**Choix de conception informés par la réponse, déclarés comme tels :** le point de mesure, sa
forme à deux canaux, les familles de modèles, les marges numériques et les contrôles sont ceux
fixés dans le prompt d'autorisation. Aucun choix adaptatif supplémentaire n'a été obtenu en
rouvrant les trajectoires exposées ; en particulier `ETA_ORACLE`, `ETA_SCI_b` et les seuils
proviennent du rejeu exact et de l'échelle **pré-intervention**, jamais d'une amplitude de
réponse exposée.

Les données exposées `WSCPL00`/`WSCCRP00` (fondateurs `61000–61003` et leurs bras, y compris la
trajectoire `+0,5·N₀`) sont `EXPOSED_FORMULATION_DATA`, exclues de tout rôle de ce programme.
