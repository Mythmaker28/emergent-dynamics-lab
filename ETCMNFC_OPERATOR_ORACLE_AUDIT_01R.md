# Audit indépendant ETCMNFC — opérateur et oracles 01R

## Verdict scientifique court

L'opérateur est **mathématiquement correct sur son domaine étroit et bien formé** : avec des
identifiants uniques, une matrice d'éligibilité booléenne, deux listes de sites disjointes de même longueur et
des montants `float64` finis, l'appariement gelé est bien maximum puis lexicographiquement minimal, la
transposition est une involution d'octets et elle préserve le multi-ensemble ainsi que la somme non pondérée
exacte de `Mf[0]`.

En revanche, le paquet `60/60` ne constitue **pas** une vérification indépendante de ces faits sur les blocs
DEV, et la qualification globale des oracles échoue. Les trois oracles vides de la première passe sont de vrais
`FAKE_PASS` (ce que le dossier reconnaît). Parmi leurs remplaçants, `F2_MASK_CROSS_CHECK_VIA_KAPPA` n'est pas
un oracle d'égalité de masque : deux corruptions distinctes du masque sont acceptées par une construction
adversariale. Le registre `F5` accepte aussi des lignes supplémentaires, dupliquées ou d'axes/appels inconnus.
Enfin, `etcmnfc_verify.py` n'utilise jamais le résultat `60/60` qu'il charge, ne vérifie ni le protocole ni
`SHA256SUMS`, et accepte des valeurs `PASS` de mauvais type parce qu'elles sont simplement converties en
booléens.

Le commit audité ne contient par ailleurs aucune définition ni revendication de « trois opérateurs orientés » :
le mot `orientation` est absent du coeur, des résultats et du rapport, et l'unique opérateur d'intervention
explicite est `transpose`. Si ce triplet faisait partie du résultat annoncé à auditer, il y a discordance de
handoff et cette revendication est **FAIL / ABSENTE DU COMMIT CIBLE**.

Conséquence : la revendication maximale auditée ici est **un opérateur logiciel conditionnel**, pas une
qualification DEV indépendante, pas une sonde ON entièrement exacte, et aucune affirmation de transport.

## Périmètre et intégrité de l'accès

- Commit audité : `c5171b72f3ed2cdaba1968bdbd9ebf3776eab8d7`.
- Freeze indépendant antérieur à toute lecture ETCMNFC :
  `55f4223dd6e965d5db36934f9ef0d96bfc344434`.
- Tous les chemins ont été présentés avant lecture à
  `C:/Users/tommy/Documents/IPRR00R_BOOTSTRAP/Assert-IPRR00RSafe.ps1`.
- Aucun module du dépôt, moteur, monde, exécuteur scientifique, trajectoire, état primaire ou contenu tenu à
  l'écart n'a été importé, ouvert ou exécuté.
- La lecture des protocoles et rapports autorisés a exposé un nom d'allocation et un nom de géométrie tenus à
  l'écart. C'est **L1** : les valeurs exactes ne sont pas reproduites ici et l'audit dépendant correspondant est
  `NOT_AUDITABLE`. Aucun contenu ni résultat tenu à l'écart n'a été ouvert.
- Les artefacts d'état DEV bruts ne faisaient pas partie du périmètre de lecture. Toute affirmation qui dépend
  de leurs valeurs est donc `INDETERMINATE`, même si un JSON commis affirme `PASS`.

## Verdicts par revendication

| Revendication | Verdict 01R | Fondement indépendant |
|---|---:|---|
| Le comptage publié contient 60 lignes et 60 booléens vrais | **PASS (arithmétique seulement)** | Relecture JSON : 60 lignes, 60 valeurs `true`, 12 familles de portes. Cela ne valide pas les propriétés nommées. |
| Les 60 portes ont été indépendamment reproduites sur DEV | **INDETERMINATE** | Les entrées DEV brutes ne sont ni lisibles dans ce mandat ni liées dans le paquet par un inventaire de blobs d'entrée ; les sorties sont des résumés. |
| Trois opérateurs orientés et leurs valeurs non nulles appartiennent au résultat ETCMNFC | **FAIL / ABSENT** | Zéro occurrence de `orientation` dans le coeur, les JSON et le rapport ; l'inventaire AST ne trouve qu'une intervention explicite, `transpose`. |
| Appariement maximum puis minimum lexicographique, conditionné par `(bool, ids uniques)` | **PASS conditionnel** | Réimplémentation séparée comparée à une énumération exhaustive de tous les appariements : 19 266 cas, 0 divergence. |
| Objectif d'appariement aveugle aux valeurs une fois la matrice booléenne fixée | **PASS par inspection du code**, mais **FAKE_PASS pour la porte** | `frozen_matching` et `_max_matching` ne reçoivent que matrice et identifiants. La porte Phase C2 appelle toutefois deux fois la fonction sur des copies identiques ; elle ne teste aucune variation de valeur. |
| Manifeste complet indépendant des valeurs | **FAIL / revendication retirée correctement** | L'éligibilité lit `rho` et `Mf[0]`. Le dossier publie désormais honnêtement cette correction de portée. |
| Transposition = involution d'octets, somme non pondérée exacte conservée | **PASS conditionnel** | Théorème de permutation et réplique indépendante, y compris zéro signé et subnormal, pour listes égales et disjointes. |
| Interface de transposition fail-closed sur manifeste mal formé | **FAIL** | Les listes `I/J` de longueurs inégales sont acceptées ; `zip(I,J)` ignore silencieusement les extrémités supplémentaires. Une liste `I` vide avec `J` non vide retourne aussi l'identité. |
| `w_i = 1` est établi par la seconde passe | **FAIL comme preuve ; fait physique INDETERMINATE** | Le test choisit lui-même des poids uniformes puis montre qu'un champ aléatoire non uniforme brise la conservation. Il montre que l'hypothèse est load-bearing, pas qu'elle est vraie dans le modèle. |
| Première passe F5/F6/F2 | **FAKE_PASS** | Même expression contre elle-même ; identité de permutation de `roll` ; même objet contre lui-même. Le dossier conserve et reconnaît correctement l'incident. |
| F5 remplaçant : registre interne = retour capturé | **PASS logique étroit ; DEV INDETERMINATE** | Le comparateur peut rejeter une perturbation d'un ulp. Mais il ne valide pas le schéma du registre et aucune donnée de face n'est persistée dans le JSON pour relecture indépendante. |
| F5 `STATE_BUFFER_REPRODUCED` pour les deux canaux | **FAIL en portée** | `c` est reconstruit contre l'état ; pour `N`, le code compare seulement la divergence du registre au retour capturé, pas le tampon d'état `N` appliqué. |
| F6 débit/crédit pour chaque face | **PASS seulement pour le stencil testé** | La perturbation d'une face horizontale donne deux cellules opposées. C'est cohérent avec `f-roll(f)`, mais la porte ne balaie ni toutes les faces ni toutes les lignes de registre. |
| F2 masque enregistré exactement croisé par `kappa` | **FAIL** | `kappa == 1` hors matière n'est pas une biconditionnelle. Une cellule matière avec `kappa == 1` peut être retirée, et une cellule externe avec `kappa == 1` peut être ajoutée, sans faire échouer le prédicat. |
| `full_state_sha` couvre l'état complet | **INDETERMINATE** | Le hash énumère un tuple fixe de champs. La revue affirme avoir comparé à `vars(st)`, mais ni son code indépendant ni l'état brut ne sont commis dans le périmètre auditable. |
| `etcmnfc_verify.py` est un vérificateur indépendant et fail-closed | **FAIL** | Même implémentation importée, entrée `G` chargée puis inutilisée, contrôles négatifs non rejoués, schémas non validés, protocole/hashes ignorés, tests d'absence fondés sur des noms de fichiers. |
| Empreintes des artefacts autorisés | **PASS pour les octets commis** | Les SHA-256 recalculés concordent avec `ETCMNFC/SHA256SUMS` pour les douze artefacts contrôlés. Le vérificateur ne fait cependant pas ce contrôle. |

## Résultats indépendants détaillés

### 1. Appariement et transposition

Une implémentation séparée de la politique gelée a été opposée à un oracle par énumération exhaustive. Pour
toutes les matrices booléennes de tailles `1x1`, `2x2`, `3x3` et `3x2`, avec plusieurs permutations
d'identifiants uniques, le cardinal et la liste lexicographiquement minimale concordent :

```text
matching_unique_ids_cases 19266 failures 0
```

Cette réussite dépend de deux préconditions non gardées par l'API : unicité des identifiants et schéma des
paires. Avec des identifiants dupliqués, la réplique retourne deux couples sémantiquement identiques. Dans
`etcmnfc_core.py:217-231`, la garde ne teste que la disjonction des sites ; elle ne teste pas
`len(I) == len(J)` avant le `zip` :

```text
I_empty_J_extra  accepted applied 0 pair, declared I=0 J=1
I_extra          accepted applied 1 pair, declared I=2 J=1
J_extra          accepted applied 1 pair, declared I=1 J=2
duplicate        rejected ValueError
```

Sur les entrées valides, la conservation de la somme rationnelle non pondérée est une conséquence directe de
la permutation. `Fraction(float)` échoue correctement par exception sur `NaN` et les infinis, mais l'API ne
transforme pas cette exception en verdict de schéma explicite. Le résultat est donc exact pour les valeurs
finies, pas robuste comme parseur d'entrée hostile.

### 2. Les portes O1 ne testent pas ce que leur nom annonce

- `etcmnfc_gates.py:127,159` construit `transpose(..., identity=True)`, qui retourne
  inconditionnellement une copie avant toute opération, puis compare cette copie à l'entrée. La porte nommée
  `MATCHING_PROSPECTIVE` ne touche pas l'appariement : **FAKE_PASS**.
- `etcmnfc_phaseC2.py:197-201` appelle `frozen_matching` sur une matrice et ses copies identiques. Cela teste
  au mieux le déterminisme immédiat. L'aveuglement aux valeurs est vrai par inspection de
  `etcmnfc_core.py:162-195`, pas grâce à cette porte.
- La correction publiée — l'objectif est aveugle, le prédicat d'éligibilité ne l'est pas — est exacte et doit
  rester la formulation maximale.

### 3. Incident de première passe

Les sources confirment exactement l'incident publié :

- `etcmnfc_phaseC.py:99-112` reconstruit deux fois la même expression ;
- `etcmnfc_phaseC.py:119` soustrait la somme exacte d'un tableau de celle de sa permutation ;
- `etcmnfc_phaseC.py:131` compare le masque à nouveau dérivé du même objet retourné.

Le JSON de première passe contient 22 lignes, 21 `PASS` et l'échec de support F10. Les lignes F2/F5/F6
marquées vraies restent des `FAKE_PASS`, même si elles sont ensuite explicitement superseded. Leur conservation
historique et leur divulgation sont de bonnes pratiques de provenance ; elles ne les convertissent pas en
preuves.

### 4. Oracles de seconde passe

#### F5

`F5_LEDGER_EQUALS_NATIVE_RETURN` compare bien une divergence reconstruite à la valeur capturée au retour,
et son altération d'un ulp peut échouer. Mais la construction de dictionnaires à
`etcmnfc_phaseC2.py:76-91` ne valide ni l'ensemble exact des appels, ni l'ensemble exact des axes, ni
l'unicité des lignes. Une réplique de la logique accepte :

```text
extra_unrecognized_axis  rows=4 accepted=True
extra_call               rows=4 accepted=True
duplicate_identical_row  rows=4 accepted=True
wrong_duplicate_then_correct rows=4 accepted=True
```

Les lignes supplémentaires peuvent être ignorées ou écrasées. Le JSON ne conserve que `faces_recorded=4`,
pas les tableaux de face ; le fait numérique n'est donc pas recalculable ici.

`F5_STATE_BUFFER_REPRODUCED` est aussi trop large : à `etcmnfc_phaseC2.py:112-123`, le tampon `c` est
reconstruit, tandis que `N` n'est testé que par `n_from_ledger == ret[2]`. La porte ne reconstruit pas l'état
`N` après mise à jour.

#### F6

La nouvelle porte est un bon test unitaire local du stencil choisi : une unité ajoutée à une face crée deux
changements opposés aux deux extrémités. Elle devient probante pour le retour capturé seulement en conjonction
avec F5. Sa portée publiée devrait être « le stencil d'une face testée a la symétrie débit/crédit », pas
« chaque face observée a été auditée indépendamment ».

#### F2

Le prédicat réel (`etcmnfc_phaseC2.py:153-165`) impose seulement :

1. `kappa == 1` sur le complément du masque déclaré ;
2. au moins une valeur non unitaire dans le masque ;
3. le même tableau `kappa` pour les deux appels ;
4. une corruption particulière, choisie sur la première cellule vraie, doit échouer.

Ce n'est pas une caractérisation unique du masque. Construction indépendante :

```text
true_mask                    accepted=True  equals_true=True
flip_nonunit_alive_to_false  accepted=False equals_true=False
drop_unit_kappa_alive_cell   accepted=True  equals_true=False
add_outside_unit_kappa_cell  accepted=True  equals_true=False
```

Le contrôle négatif choisi peut échouer tandis que d'autres masques faux passent. Le verdict de la porte
nommée est donc **FAIL**, et non un simple manque de puissance statistique.

#### Poids `w`

À `etcmnfc_phaseC2.py:178-190`, `w_uniform_ok` est la conservation de la somme non pondérée par une
permutation ; les « vrais poids uniformes » sont choisis par le test. Le champ aléatoire non uniforme montre
que la conclusion changerait sous d'autres poids. Il ne dérive pas les poids physiques du modèle. La
sémantique `w_i=1` exige une preuve de schéma/source séparée et autorisée.

### 5. Le vérificateur n'est pas indépendant

Analyse AST de `etcmnfc_verify.py` :

```text
name_loads G 0
name_loads P1 2
name_loads P2 10
reads_SHA256SUMS False
reads_protocol False
hashlib_uses 0
```

`G = json.load(open("etcmnfc_gates_offline.json"))` à la ligne 27 n'est jamais relu. Le résultat `60/60`
peut donc être altéré sans affecter le vérificateur. À `:104-110`, V5 demande seulement que les valeurs
stockées soient truthy et que trois noms soient présents ; il ne rejoue aucun contrôle négatif. À
`:137-145`, le budget et l'absence d'artefact reposent sur des compteurs, logs et noms de fichiers déclarés.

Une mutation en mémoire conservant seulement trois lignes, avec `PASS` respectivement égal à la chaîne
`"false"`, à `NaN` et à l'entier `1`, satisfait V5. Un compteur négatif satisfait le plafond et un log vide
satisfait le test « seulement DEV » :

```text
tampered_rows_only_three_schema_wrong_V5 True
budget_check_negative_count True
empty_log_DEV_check True
```

Python considère en effet la chaîne `"false"`, `1` et `NaN` comme vrais. Aucun schéma n'impose un booléen JSON
strict, aucun nombre fini, une cardinalité exacte ou des champs interdits. Le contrôle V7c est également
filename-keyed : renommer un artefact suffit à le cacher, tandis qu'un nom innocent contenant le motif testé
peut faire échouer la porte.

Le vérificateur réimporte en outre `etcmnfc_core`, donc son V1 n'est pas une réimplémentation indépendante.
Il redérive certaines propriétés avec le même code, mais ne compare pas les manifests recalculés à `G`.
`etcmnfc_verify.json` (`19/19`) est donc un relevé d'exécution, pas un certificat fail-closed.

### 6. Hashes et cohérence interne

Les SHA-256 recalculés sur les blobs Git autorisés correspondent tous aux lignes de `SHA256SUMS` :

| Artefact | SHA-256 |
|---|---|
| `etcmnfc_core.py` | `b9c878acd70ab6d9734eb70e9fadc71b2db70cc919f9132656ce0ddc20ec1d02` |
| `etcmnfc_gates.py` | `ff6e59f610cc2e87e3716dc43d859824d2fe1d5933cceb98e65bed2a1d9d291e` |
| `etcmnfc_gates_offline.json` | `d0b165750b42a45065bb03412ae3a63f4dd0f4ea5c18c324bf022e13a9db3da7` |
| `etcmnfc_phaseC.py` | `c5cabcbc57574d651a349a5504ce89a9307cadd76357a935e7dee61401364906` |
| `etcmnfc_phaseC.json` | `565966f57fae2a361016f80b77a67654f7f9f6628be987846f809cffdb5ebfbe` |
| `etcmnfc_phaseC2.py` | `039a0967d79153636baa61f322924d56510df8025e0824164f828a64f023d662` |
| `etcmnfc_phaseC2.json` | `bfcf4acd311d4170377bdad82e2d0dfb3bf5469cdd7c91ca9787026b0320bbb8` |
| `etcmnfc_verify.py` | `1c8d3ad24a6b5c934e48e0bc9cdc7e665d35fad0a7440dccc227dcb6363d1f25` |
| `etcmnfc_verify.json` | `a8fe2c4a52902e0290019f4e5d65c5d2077b4a24b8b018ee3e4286bce29a687b` |
| `etcmnfc_protocol.json` | `075e5c8994f6a9785c14ed72b444431238e4e84ff53d5cb91d5fe921e9522109` |
| `REVIEW_1_NUMERICAL_ORACLE.md` | `7b39a73507f4c2da4a2372e7ba540c8cd4eacd284035685b9a62693c7493d346` |
| `REPORT_ETCMNFC.md` | `aa1dbb56d3c1b15764255cf97d6bdd2136d560d3598aeddcd38b8812108e0af9` |

Cette cohérence lie les octets au commit, mais n'établit pas leur vérité. Le champ `hash` de chaque manifeste
DEV ne couvre que le sous-ensemble créé avant l'ajout des métriques. Les quatre hashes de base se recalculent,
mais aucun ne change si `delta_Q_A` est altéré ; le hash du record complet ne concorde donc pas par conception.
Le vérificateur ne consulte ni ce hash ni `SHA256SUMS`.

## Commandes et sorties reproductibles

Toutes les lectures ont suivi la forme :

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File C:\Users\tommy\Documents\IPRR00R_BOOTSTRAP\Assert-IPRR00RSafe.ps1 `
  -Kind Path -Value ETCMNFC/<chemin-autorisé>
git -C C:\Users\tommy\Documents\ising-v3-iprr00r-audit `
  show c5171b72f3ed2cdaba1968bdbd9ebf3776eab8d7:ETCMNFC/<chemin-autorisé>
```

Les analyses indépendantes ont été exécutées par `python -` depuis l'entrée standard, sans `PYTHONPATH`, sans
import du dépôt et sans écriture d'artefact scientifique. Elles ont couvert : recensement JSON ; SHA-256 ; AST
des dépendances du vérificateur ; oracle exhaustif d'appariement ; fixtures de schéma de paires ; fixtures de
masque ; fixtures de registre ; vérification du hash partiel des manifests. Les sorties numériques décisives
sont reproduites dans les sections précédentes.

## Réparations minimales avant tout nouveau label `VALID`

1. Ajouter un schéma fail-closed : `float64` fini, formes exactes, identifiants et coordonnées uniques, listes
   `I/J` de même longueur, aucun champ ou registre supplémentaire, appels et axes exactement attendus.
2. Remplacer F2 par l'égalité bit à bit avec un masque recomputé indépendamment depuis l'entrée `rho` et le seuil
   gelé ; tester séparément faux positif et faux négatif, y compris une cellule où `kappa == 1`.
3. Persister les tableaux de faces DEV autorisés par hash, puis reconstruire **les deux** tampons d'état (`c` et
   `N`) avec une implémentation indépendante.
4. Faire lire au vérificateur le protocole, `SHA256SUMS`, tous les blobs d'entrée et chaque ligne de résultat ;
   imposer des booléens JSON stricts, des nombres finis, les cardinalités exactes et la concordance valeur par
   valeur. Le vérificateur ne doit pas importer `etcmnfc_core` pour refaire ETCMNFC.
5. Établir `w_i=1` depuis un contrat de schéma/source explicitement audité. Le contre-exemple à poids non
   uniformes doit rester comme test de sensibilité, pas comme preuve du poids réel.
6. Ne pas convertir ces réparations d'outillage en autorisation scientifique : elles ne rendent ni le point de
   mesure causal identifiable, ni un contenu tenu à l'écart auditable, ni une affirmation de transport éligible.

## Conclusion

Le bon résultat à conserver est précis : **la construction de permutation est saine sur des entrées
préconditionnées** et la correction « objectif aveugle, éligibilité dépendante de l'état » est honnête. Le moins
bon résultat est load-bearing : **l'oracle global reste permissif et auto-référentiel**, y compris après la
seconde passe. `60/60`, `14/14` et `19/19` sont des comptages de lignes commises ; aucun ne mérite le statut de
certification indépendante dans l'état actuel.
