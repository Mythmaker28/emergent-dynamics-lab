# Audit indépendant ETCMNFC — endpoint et inférence 01R

## Verdict scientifique

`ETCMNFC` ne fournit aucun résultat causal sur un flux attribuable à A ou B. Le maximum défendable
est plus étroit : les artefacts DEV dérivés décrivent, au point de départ, une unique région
`rho > 1e-4`, des composantes A/B profondes qui ne touchent aucun des liens matière–bain recensés,
et un arrêt avant toute réduction d'un contraste cible. Même cet arrêt n'est pas complètement
reproductible au niveau du **masque au moment de l'échange** dans le périmètre autorisé : la porte
`F10` et le vérificateur utilisent le masque du fichier d'entrée, alors que le masque effectivement
enregistré par la sonde un pas plus tard a une cardinalité différente dans les deux blocs dynamiques
publiés.

La formule exacte est donc :

```text
EMPTY_PRESTEP_SUPPORT_IN_COMMITTED_DERIVED_JSON = PASS_INTERNAL_CONSISTENCY
EMPTY_SUPPORT_AT_REALIZED_EXCHANGE_TIME          = INDETERMINATE
PER_COMPONENT_NATIVE_BOUNDARY_FLUX               = NOT_IDENTIFIABLE / NOT_TESTED
CAUSAL_EFFECT                                     = NOT_TESTED
REPLICATION                                       = NOT_AUDITABLE (L1) AND NOT_REACHED
```

`60/60` n'est ni 60 histoires, ni 60 réplications, ni un endpoint. Il s'agit de 60 assertions
hors ligne : 44 lignes étiquetées par bloc sur seulement quatre blocs DEV, plus 16 assertions
globales/adversariales. Les quatre blocs partagent exactement les mêmes ensembles géométriques A
et B. Les portes dynamiques réécrites portent principalement sur deux blocs.

L'inventaire autorisé ne contient en outre qu'un opérateur scientifique : `transpose()` applique
une transposition de `Mf[0]` selon un matching gelé. Aucun ensemble de « trois opérateurs orientés »
avec trois valeurs séparées n'apparaît dans le protocole, le coeur, les portes ou les JSON. Le
marqueur `TEST_LATERALITY = TWO_SIDED_ONLY` règle la latéralité d'un test ; les trois oracles
superseded sont des tests défectueux, pas trois opérateurs. Toute revendication « trois opérateurs
orientés » est `FAIL/UNSUPPORTED` pour ce commit.

## Périmètre et intégrité aveugle

- Commits audités : ETPC `3f8dae8bbe2937c43661ba8adfe8aed63bf6b6ee`, EEFCA
  `de1524b22ff917dff1da6553f778a4f8019ac273`, ETNBFC
  `d86d24864e0f88c6483d11bcde601d1f13221a82`, ETCMNFC
  `c5171b72f3ed2cdaba1968bdbd9ebf3776eab8d7`.
- Chaque chemin a été validé par la sentinelle externe avant lecture.
- Aucun module Python du dépôt n'a été importé ou exécuté. Les recomputations utilisent seulement
  la bibliothèque standard, `git show` et les JSON autorisés.
- Aucun moteur, monde, trajectoire, étape, reprise, allocation primaire ou contenu tenu à l'écart
  n'a été ouvert ou exécuté.
- Une exposition de **nom** classée L1 ayant révélé une allocation tenue à l'écart, tout audit
  dépendant de cette allocation est `NOT_AUDITABLE`. La valeur exposée n'est pas reproduite ici.
- Les artefacts bruts nécessaires à une reconstruction depuis les champs de grille se trouvent
  hors du périmètre de lecture. Ce rapport distingue donc strictement cohérence interne des JSON
  dérivés et reproduction à partir de données brutes.

## Evidence lue et empreintes

| Niveau | Artefact | SHA-256 du blob |
|---|---|---|
| ETCMNFC | `etcmnfc_gates_offline.json` | `d0b165750b42a45065bb03412ae3a63f4dd0f4ea5c18c324bf022e13a9db3da7` |
| ETCMNFC | `etcmnfc_phaseC.json` | `565966f57fae2a361016f80b77a67654f7f9f6628be987846f809cffdb5ebfbe` |
| ETCMNFC | `etcmnfc_phaseC2.json` | `bfcf4acd311d4170377bdad82e2d0dfb3bf5469cdd7c91ca9787026b0320bbb8` |
| ETCMNFC | `etcmnfc_verify.json` | `a8fe2c4a52902e0290019f4e5d65c5d2077b4a24b8b018ee3e4286bce29a687b` |
| ETCMNFC | `probe_alive_topology.json` | `1fae351a592f970d3393b60a0bbe010b07920060cd6db6c2c92a769b5fa5eca2` |
| ETCMNFC | `probe_attribution.json` | `be4241a2593af6399c8a83655a10e9a074318796ddc752ffb90a20607e756421` |
| ETCMNFC | `probe_depth.json` | `0cc6219420228e2a9acc576c06a1e28c13ee1865e6f1eef17c33a7ec7ce9c6d6` |
| ETCMNFC | `etcmnfc_core.py` | `b9c878acd70ab6d9734eb70e9fadc71b2db70cc919f9132656ce0ddc20ec1d02` |
| ETCMNFC | `etcmnfc_phaseC.py` | `c5cabcbc57574d651a349a5504ce89a9307cadd76357a935e7dee61401364906` |
| ETCMNFC | `etcmnfc_phaseC2.py` | `039a0967d79153636baa61f322924d56510df8025e0824164f828a64f023d662` |
| ETPC | `etpc_protocol.json`, `etpc_gates.json`, `etpc_verify.json` | `df266478...`, `c9eac362...`, `da79097f...` |
| EEFCA | `eefca_audit.json`, `eefca_protocol.json`, `eefca_verify.json` | `376ddd95...`, `77f3051a...`, `5b64cb3c...` |
| ETNBFC | `etnbfc_b0.json`, `etnbfc_c0.json`, `etnbfc_protocol.json` | `5bd762be...`, `f1a1e935...`, `d2d69558...` |

Les empreintes ETCMNFC ci-dessus concordent avec `ETCMNFC/SHA256SUMS`. Les trois fichiers
`probe_*` sont donc liés au commit, mais aucun générateur dédié de ces trois fichiers n'est commis
sous `ETCMNFC/`; leur provenance arithmétique exacte reste insuffisante pour expliquer les
contradictions de dérivés ci-dessous.

## Reconstruction indépendante des dénominateurs

### Ce que signifie réellement `60/60`

La recomputation de `etcmnfc_gates_offline.json` donne :

| Objet | Total | PASS | Unités réelles |
|---|---:|---:|---|
| assertions hors ligne | 60 | 60 | 44 lignes bloc-spécifiques + 16 lignes globales/adversariales |
| blocs DEV distincts | 4 | — | mêmes ensembles de sites A/B |
| assertions Phase C première passe | 22 | 21 | une porte F10 échoue |
| assertions Phase C2 réécrites | 14 | 14 | dix lignes sur deux blocs + quatre globales |
| vérifications finales | 19 | 19 | méta-vérifications, pas histoires indépendantes |

Les 44 lignes bloc-spécifiques de la qualification hors ligne sont onze propriétés répétées sur
quatre états. Elles ne sont pas 44 histoires indépendantes. Les 16 autres lignes sont des
propriétés globales ou des exemples adversariaux. Interpréter `60/60` comme un taux de réplication
est un **échec de dénominateur**.

### Support et attribution au point de départ

Les fichiers `etcmnfc_phaseC.json`, `probe_attribution.json` et
`probe_alive_topology.json` concordent exactement sur les comptes suivants :

| bloc DEV | liens matière–bain au point de départ | liens dont l'extrémité matière est dans A/B | cellules A/B adjacentes au bain | régions `alive` | A/B dans la même région |
|---|---:|---:|---:|---:|---|
| 1 | 172 | 0 | 0 | 1 | oui |
| 2 | 172 | 0 | 0 | 1 | oui |
| 3 | 172 | 0 | 0 | 1 | oui |
| 4 | 172 | 0 | 0 | 1 | oui |
| **agrégé descriptif** | **688** | **0** | **0** | — | — |

Cet agrégat est une somme descriptive, pas quatre géométries. La canonicalisation des listes
`sites_A`/`sites_B` produit le même SHA-256
`a3d537acb69e55414a4c9c95e8d523c9716f7a5ddf95eac9c97a1c22b88275f9` pour les quatre blocs :
**une seule géométrie** est répétée avec quatre états.

Le critère codé en F10 exige que *tous* les liens matière–bain soient attribuables à A ou B. Cette
condition est plus forte qu'une simple porte de support non vide. Cela ne sauve cependant pas le
programme : le compte publié est zéro, donc le sous-ensemble requis est vide dans le masque
pré-step publié.

## Contradictions et limites load-bearing

### 1. F10 n'utilise pas le masque effectivement présent lors de l'échange

`etcmnfc_phaseC.py` enregistre le masque de la sonde après l'étape dans `ON_LEDGER`, puis recalcule
F10 séparément en rechargeant l'état de départ et en posant `alive = st.rho > ALIVE_EPS`. Le
vérificateur final répète le même calcul pré-step ; ce n'est pas une reconstruction indépendante.

Les JSON démontrent que les deux masques n'ont pas même cardinalité :

| bloc dynamique | cardinalité utilisée par F10 (pré-step) | cardinalité enregistrée au temps d'échange | écart |
|---|---:|---:|---:|
| 1 | 1662 | 1663 | +1 |
| 2 | 1663 | 1664 | +1 |

Le contenu du masque au temps d'échange n'est pas persisté dans les JSON autorisés, seulement sa
cardinalité. Il est donc impossible de vérifier si le nouveau site est ou non adjacent à A/B. Une
distance pré-step élevée rend l'absence plausible, mais la plausibilité n'est pas une preuve.

Conséquence :

```text
F10_EMPTY_SUPPORT_AT_PRESTEP = PASS_INTERNAL
F10_EMPTY_SUPPORT_AT_ACTUAL_EXCHANGE = INDETERMINATE
```

### 2. Le ratio de profondeur publié ne se recalcule pas

Pour chaque bloc, la clé `rho_ratio_component_min_over_boundary_median` de `probe_depth.json` ne
vaut pas `rho_min_in_A_or_B / rho_at_material_endpoints.median`, pourtant les noms de champs
affirment exactement ce quotient :

| bloc DEV | ratio recomputé | ratio publié | erreur relative du publié |
|---|---:|---:|---:|
| 1 | 2365.946 | 2026.583 | -14.34 % |
| 2 | 2307.335 | 1975.249 | -14.39 % |
| 3 | 2466.562 | 2094.951 | -15.07 % |
| 4 | 2409.839 | 2130.036 | -11.61 % |

Le récit « environ 2000 » reste un ordre de grandeur, mais le dérivé exact et sa provenance sont
`FAIL`. Aucun générateur commis ne permet d'identifier un autre numérateur ou dénominateur.

### 3. La convention de distance est incohérente

`probe_depth.json` nomme une distance « lattice » mais publie une médiane non entière
`13.892443989...`, caractéristique d'une distance euclidienne. La revue numérique distingue
elle-même 14 pas en distance de graphe 4-connexe de 13.0 en distance euclidienne. Le rapport
principal résume « 13 cellules de réseau » sans fixer cette convention. Le fait qualitatif
« profondément séparé de la frontière au point de départ » est soutenu ; la quantité « 13
cellules de réseau » est `INDETERMINATE/MISLABELLED`.

### 4. Les données de flux brutes ne sont pas persistées dans les JSON autorisés

La première passe contenait trois oracles incapables d'échouer ; le programme le reconnaît et les
remplace. Les sorties de remplacement enregistrent des booléens, des comptes et des textes, pas
les tableaux de faces, masques et buffers nécessaires à une recomputation indépendante. Le
vérificateur réexécute le même environnement interdit à cet audit. Ainsi :

- la présence du code d'une sonde ON et de contrôles négatifs est observable ;
- le journal `14/14` est observable ;
- l'égalité bit-exacte des flux/buffers ne peut pas être recalculée depuis les seuls blobs JSON
  autorisés ;
- aucune valeur de contraste de flux attribuable n'existe, puisque le programme affirme ne pas
  l'avoir réduite.

Le verdict indépendant du flux est donc `INDETERMINATE` pour la reproduction numérique de la
sonde et `NOT_TESTED` pour l'effet causal.

## Continuité ETPC → EEFCA → ETNBFC → ETCMNFC

### ETPC

- L'infrastructure de jumeaux exacts est consignée comme bit-exacte.
- L'opérateur exécuté n'est pas involutif lorsque les masses diffèrent ; sa porte nommée
  « involution » recevait littéralement `True` et n'évaluait pas la propriété.
- L'endpoint exécuté était une moyenne spatiale de `c`, sans `N`, pas un flux réalisé de `c` et
  `N` sur les liens matière–bain autorisés.
- Sa direction unilatérale ne se propageait pas du dérivé local de `kappa` jusqu'à la moyenne
  spatiale.

Verdict de continuité : `ETPC_EXACT_TWIN_INFRASTRUCTURE = SUPPORTED_BY_RECORD` mais
`ETPC_CONFIRMATORY_ENDPOINT = FAIL`.

### EEFCA

EEFCA sépare correctement infrastructure, opérateur, endpoint et dérivation fonctionnelle. Son
audit établit documentellement que la conformance de l'opérateur et celle de l'endpoint ETPC
échouent, et que la direction exacte est non dérivable. Il ne fournit pas les champs spatiaux
bruts nécessaires à la décomposition manquante. Le nom « endpoint-functional congruence » ne doit
donc pas être lu comme un résultat positif.

### ETNBFC

ETNBFC établit correctement, sous sa règle gelée, l'absence de paires à `rho` byte-identique et
l'absence de registre de faces natif dans le bras gain-zéro. Mais il transforme à tort une
condition suffisante d'admissibilité (égalité de `rho`) en condition nécessaire. Son propre
fichier `etnbfc_weak_alternative.json` montre déjà un appariement complet admissible sous le
contrôle d'inégalités. ETCMNFC corrige ensuite ce point par construction.

Verdict : `ETNBFC_STOP_UNDER_OWN_PROTOCOL = PASS`, mais
`ETNBFC_NO_CONSERVATIVE_INVOLUTION_EXISTS = FAIL`.

### ETCMNFC

ETCMNFC fournit une transposition brute involutive de `Mf[0]` préservant son multi-ensemble et sa
somme exacte à `t0`. Le prédicat d'éligibilité dépend néanmoins de l'état (`rho`, `Mf[0]`) ; seul
l'objectif de matching est aveugle aux valeurs. Cela rend l'estimand conditionnel à une politique
d'appariement différente par état.

Le programme corrige honnêtement ses trois oracles vacants, puis s'arrête avant contraste cible.
L'arrêt scientifique est prudent. L'argument exact d'endpoint est toutefois plus faible que le
rapport : le support pré-step est vide dans les dérivés publiés, mais le support au temps
d'échange n'est pas recomputable et son masque a déjà changé de cardinalité.

## Séparation des axes de revendication

| Axe | Observable réellement disponible | Verdict 01R | Maximum défendable |
|---|---|---|---|
| existence d'un endpoint | aucune valeur de contraste cible réduite | `NOT_TESTED` | le programme s'est arrêté avant le calcul |
| cardinalité du support | 172 liens/bloc, 0 attribuable dans le masque pré-step dérivé | `PASS_INTERNAL` au pré-step ; `INDETERMINATE` au temps d'échange | support pré-step vide dans une géométrie |
| topologie | un label `alive`, A/B même label, quatre fois la même géométrie | `PASS_INTERNAL`, `INDETERMINATE_RAW` | une région sous un seuil et une convention donnés |
| flux natif | source de sonde + résumés booléens, pas de ledger brut autorisé | `INDETERMINATE` | existence documentée d'une sonde ON ; pas sa reproduction indépendante |
| attribution | aucun lien pré-step étiqueté A/B ; masque réel non conservé | `NOT_IDENTIFIABLE` | aucune attribution causale |
| minimalité | tie-break lexicographique d'un matching **maximal** ; aucune intervention plus petite testée | `FAIL` si « minimal » est revendiqué | minimalité lexicographique seulement |
| causalité | zéro contraste cible ; règle statistique non utilisée | `NOT_TESTED` | aucune affirmation d'effet ou d'absence d'effet |
| généralité | quatre états DEV, une géométrie ; dynamique surtout sur deux états | `FAIL` pour généralité ; `NOT_AUDITABLE` pour réplication tenue à l'écart | diagnostic DEV d'une configuration |

## Vocabulaire red-team

- **`native`** : signifie ici que la sonde copie le calcul ON du noyau ; cela ne rend pas le point
  de mesure par composante identifiable.
- **`flux`** : défendable pour un transfert de face ON enregistré ; non défendable pour un effet
  attribué à A/B qui n'a pas été calculé.
- **`topological`** : au maximum une connectivité 4-voisins périodique d'un masque seuillé, pas un
  invariant topologique robuste aux seuils ou aux conventions.
- **`canonical`** : nom du porteur `Mf[0]` et de sa somme à `t0`, pas preuve d'unicité physique.
- **`minimal`** : le matching est de cardinalité maximale puis minimal lexicographiquement. Aucun
  minimum d'intervention, de flux ou de mécanisme n'est établi.
- **`necessary` / `forced` / `causal`** : aucun témoin n'existe dans les données autorisées.
- **`MF0`** : index du premier champ mémoire. Il ne signifie ni « minimal flux zéro » ni mécanisme
  minimal.

## Explications alternatives compatibles avec tous les observables

1. **Bookkeeping de seuil** : A/B sont des taches denses définies près de `rho > 0.3`, tandis que
   le bain est défini par `rho <= 1e-4`; le support vide est alors une conséquence presque forcée
   de deux seuils séparés de trois ordres de grandeur, pas une propriété causale.
2. **Convention de coordonnées/distance** : 13 euclidien et 14 en graphe décrivent le même dessin,
   mais changent la formulation quantitative.
3. **Conditionnement par l'état** : la politique de matching lit `rho` et `Mf[0]`; les doses et les
   paires changent par bloc même quand la géométrie est identique.
4. **Localité de stencil** : une fenêtre d'un pas peut rendre nul un endpoint de frontière éloigné
   par construction, indépendamment du mécanisme recherché.
5. **Réduction globale à horizon plus long** : l'alternative longue décrite par la revue passe par
   un scalaire global et détruit l'attribuabilité A/B ; elle ne sauve pas l'estimand.
6. **Oracle circulaire / preuve dérivée** : les comptes F10 et V6 sont deux exécutions de la même
   formule sur le même état pré-step, pas deux sources indépendantes.

## Ce qui falsifierait chaque conclusion

| Conclusion | Témoin falsifiant exact |
|---|---|
| support vide au temps d'échange | un masque `alive` au moment exact des appels de transport, les masques A/B gelés et une liste de liens indépendante montrant au moins un lien attribuable |
| région unique | le masque brut et un étiquetage périodique préfixé donnant plus d'une composante ou des labels A/B distincts |
| absence d'attribution | un lien accepté dont l'extrémité matière appartient exactement à A ou B sous la règle gelée |
| profondeur annoncée | un générateur commis, une métrique fixée et une recomputation exacte qui reproduisent les trois fichiers `probe_*` |
| effet causal non testé | un contraste SWAP–SHAM préenregistré, sur support non vide, persisté bloc par bloc avec son sens, ses unités et son contrôle négatif |
| minimalité | l'énumération préenregistrée d'interventions de support strictement plus petit et un critère indépendant montrant qu'elles échouent toutes |
| généralité absente | plusieurs géométries réellement distinctes, fraîches, choisies sans résultat et reproduisant l'observable avec les mêmes règles |

## Claim ledger endpoint/inférence

| Claim | Verdict | Raison courte |
|---|---|---|
| `60/60` assertions hors ligne sont bien marquées PASS | `PASS` | recomptées 60/60 |
| `60/60` représente 60 histoires éligibles | `FAIL` | quatre blocs DEV, 44 répétitions bloc-spécifiques, 16 tests globaux |
| trois opérateurs orientés ont été évalués | `FAIL` | un seul `transpose()` scientifique est défini ; latéralité et oracles ne sont pas des opérateurs |
| le masque pré-step contient un support attribuable | `FAIL` | 0/688 dans les JSON dérivés |
| le support réel au temps d'échange est exactement vide | `INDETERMINATE` | masque réel différent en cardinalité et non persisté |
| A et B appartiennent à une seule région `alive` | `PASS_INTERNAL_ONLY` | trois JSON concordants, mais pas de reconstruction brute autorisée |
| quatre blocs fournissent quatre réplications topologiques | `FAIL` | un seul hash de géométrie |
| le ratio de profondeur publié est reproductible | `FAIL` | discordance de 11,6 à 15,1 % |
| la distance « 13 cellules réseau » est définie sans ambiguïté | `FAIL` | 13 euclidien contre 14 en graphe ; libellé incohérent |
| une valeur de flux par composante a été observée | `FAIL` | aucun contraste cible réduit |
| aucun effet causal existe | `OUT_OF_SCOPE / UNSUPPORTED` | endpoint non identifiable, pas de test |
| l'opérateur est causalement minimal | `FAIL` | maximalité de support et tie-break lexicographique seulement |
| le résultat se généralise | `FAIL` | DEV, une géométrie ; réplication tenue à l'écart non auditable |

## Conclusion

L'arrêt `NOT_IDENTIFIABLE` reste la décision scientifique correcte et prudente : rien n'autorise
à convertir un endpoint vide/non persistant en « pas d'effet ». Mais l'argument documentaire doit
être resserré. Les données autorisées établissent un **support pré-step vide dans une seule
géométrie DEV**, pas une preuve brute complète du support au temps exact de l'échange. Les termes
topologie, profondeur, flux, attribution, minimalité, causalité et généralité ne sont pas
interchangeables ; aucun ne doit être fourni par le PASS d'un autre.
