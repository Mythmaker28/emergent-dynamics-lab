# Résumé français

La version V4.0 annonçait qu'une information liée à la dose cumulée restait
fortement décodable après un remplacement matériel profond, avec un R² de 0,89
et un intervalle [0,84 ; 0,96], présenté comme certifié au-dessus du seuil de
0,50.

La réconciliation V4.1 n'exécute aucune nouvelle simulation. Elle reprend
uniquement les artefacts déjà validés et utilise le monde initial, identifié par
la graine de simulation, comme unité externe de validation.

L'audit montre que le bootstrap V4.0 dupliquait des histoires puis attribuait
aux copies de nouveaux identifiants de plis. Dans les 3 000 réplications
effectivement utilisées, cela plaçait des copies exactes de lignes issues du
même monde initial à la fois dans l'entraînement et dans le test.

Avec une validation laissant un monde initial entier de côté, le R² profond
pour la dose cumulée devient 0,695. Les trois scores par monde sont 0,745,
0,414 et 0,925. Le point reste positif, mais les données disponibles ne
permettent plus de certifier une borne inférieure supérieure à 0,50. La
certification V4.0 est donc retirée.

Le contraste d'ordre temporel n'est pas établi au turnover profond. Les comptes
36/36 et zéro changement d'affectation sont bien reproduits dans l'artefact de
synthèse, mais les événements détaillés de fusion et les arêtes d'association
ne sont pas conservés; cette continuité ne peut donc pas être entièrement
réauditée.

La conclusion autorisée est étroite: des caractéristiques internes à une
composante contiennent encore une information sur une histoire imposée
globalement après un fort remplacement matériel. Les artefacts V4 ne permettent
pas de montrer que cette information est stockée localement dans une composante
plutôt que distribuée dans le monde simulé.

Verdict scientifique: la valeur ponctuelle positive subsiste, mais la
certification et l'interprétation locale ne sont pas reproductibles sous une
inférence strictement groupée par monde initial.
