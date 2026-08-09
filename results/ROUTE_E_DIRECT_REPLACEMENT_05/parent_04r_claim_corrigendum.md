# Corrigendum aux claims de `04R` — enregistré, non rétroactif

Ce fichier corrige la **lecture** du parent `7e418282` (`ROUTE_E_DSC04_RAW_ONLY_CAUSAL_CLOSURE_04R`).
Aucun octet de `04R` n'est modifié : ses artefacts restent scellés tels quels et vérifiés.

## 1. Le contrôle direct était sur-conclu

```
PARENT_DIRECT_RESULT = PROMISING_DESCRIPTIVE_SIGNAL_UNVERIFIED
```

`04R` a conclu simultanément `DIRECT_INTERFACE_EXCHANGE_TOLERATED_DEV = true` **et**
`DIRECT_CONTROL_ONLY_VALID`, alors que ses propres constats étaient :

```
EVENT_LEDGER_STATUS      = RAW_INSUFFICIENT
CAUSAL_SET_INVARIANTS    = FAIL
DIRECT_DYNAMIC_CAPTURE_ZERO = FAIL 0/18
```

C'est incohérent. Un bras dont un compteur obligatoire échoue dans 18 cas sur 18, et dont le
ledger événementiel n'existe pas, ne peut pas être déclaré « valide ». Les nombres du bras direct
(masse 0,983–1,018, fraction fraîche 0,21–0,28, résidu incumbent 0,589–0,682, 18/18 non fusionnés)
restent des **descriptions honnêtes de sorties**, mais leur statut est **descriptif non vérifié**,
pas confirmé. Cette mission les re-mesure de zéro, avec ledger, sur des graines fraîches.

## 2. Le « 95,9 % » n'est pas une fraction de masse

```
95.9_PERCENT = ACCEPTED_PLACEMENT_DECISIONS_AT_GRAPH_DISTANCE_1
```

C'est une part de **décisions de placement acceptées**, comptées dans un histogramme de tags.
La masse par tag n'a jamais été persistée. Il est donc interdit de le convertir en fraction de
masse ou d'événements. Le seul énoncé exact qui subsiste : là où le compte `ACCEPTED` vaut
exactement zéro (`D1_REDESIGNED`, L=24), la masse de halo distant est exactement nulle.

## 3. Fusion et capture

```
MERGER_OCCURRENCE = CONFIRMED          (l'événement de fusion est réellement détecté)
MERGER_CAPTURE    = NOT_IDENTIFIABLE   (la masse qui entre PAR la fusion n'est pas isolable)
DYNAMICS_MEDIATED_CAPTURE_FOUND = NOT_IDENTIFIABLE
EP_1_OF_9 = NOT_AUDITABLE
ARITHMETIC_1_OF_144 = REPRODUCED_DIAGNOSTIC_ONLY
```

`04R` disait `DYNAMICS_MEDIATED_CAPTURE_FOUND = false` ; c'était trop fort. Les compteurs étant
invalides, le bon statut est **non identifiable**, pas **faux**. De même, la reproduction
arithmétique du 1/144 est un diagnostic de calcul, pas un endpoint auditable.

## 4. Portes globales, inchangées

```
ROUTE_E_VERDICT   = NONE
AUTONOMOUS_RENEWAL = NOT_TESTED
IDENTITY          = NOT_ESTABLISHED
INDIVIDUATION     = NOT_ESTABLISHED
LIFE              = NOT_ESTABLISHED
GENERALIZATION_BEYOND_LAW_16 = false
```

## 5. Ce que `DEV_05` a le droit de revendiquer

```
CLAIM_SCOPE = FORCED_DIRECT_INTERFACE_MATERIAL_TURNOVER_ONLY
```

Un remplacement matériel **imposé par l'opérateur** à travers une interface gelée. Jamais une
capture naturelle, jamais un renouvellement autonome, jamais une individuation. Et la continuité
du tracker n'est **pas** une identité causale : au mieux
`TRACKED_COMPONENT_CONTINUITY_UNDER_FORCED_TURNOVER`.
