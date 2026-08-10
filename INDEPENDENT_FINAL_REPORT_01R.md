# Rapport final indépendant IPRR00R

## Verdict scientifique

`ETCMNFC_PRIMARY_C_N = NOT_TESTED` et le programme actuel reste **non éligible à une exécution
primaire**. L'arrêt avant primaire était prudent, mais sa portée correcte est
`NOT_IDENTIFIABLE`, jamais « pas d'effet ». L'opérateur de transposition survit comme résultat
logiciel conditionnel ; le paquet `60/60` ne survit pas comme certification indépendante, et le
joint endpoint c/N est structurellement mal spécifié pour la configuration à un seul corps
matériel connecté.

La preuve autorisée établit seulement que les résumés dérivés du masque **pré-step** décrivent une
frontière matière–bain non vide et zéro face incidente aux masques A/B. Elle n'établit pas que ce
support est vide au moment exact de l'échange : les deux résumés dynamiques conservent un masque
d'échange ayant une cellule `alive` de plus que le masque rechargé par F10, sans conserver le
masque complet permettant de refaire l'attribution. Le stop demeure donc correct pour une raison
plus fondamentale : A et B sont des masques internes à un même corps ; la propriété native ne
possède aucune attribution de sa frontière extérieure entre A et B.

```text
NATIVE_COMPONENT_BATH_SUPPORT             = EMPTY_PRE_STEP; NOT_AUDITABLE_AT_EXCHANGE
PER_COMPONENT_OUTER_BOUNDARY_ATTRIBUTION  = NOT_IDENTIFIABLE
GLOBAL_BODY_BATH_FLUX                     = IDENTIFIABLE_AS_GLOBAL_LEDGER; NOT_A_PRIMARY_RESULT
ONE_STEP_GLOBAL_REACHABILITY              = UNRESOLVED_IN_IPRR00R
ETCMNFC_PRIMARY_C_N                       = NOT_TESTED
STOP_REASON                               = JOINT_ENDPOINT_STRUCTURALLY_MISSPECIFIED
```

Aucun moteur, monde, pas d'intégrateur, trajectoire, allocation primaire ou contenu tenu à
l'écart n'a été ouvert ou exécuté. Une exposition L1 de nom a rendu l'audit dépendant de ce
held-out `NOT_AUDITABLE`; elle n'invalide ni l'audit statique, ni les recomputations DEV autorisées,
ni l'audit GitHub. Aucun identifiant exposé n'est reproduit dans ce rapport.

## Ce que l'audit indépendant a changé

1. **Opérateur.** Une transposition out-of-place de 2-cycles disjoints et bien formés est une
   involution d'octets et préserve le multi-ensemble ainsi que la somme dyadique non pondérée de
   `Mf[0]`. L'appariement a concordé avec un oracle exhaustif indépendant dans 19 266 cas à IDs
   uniques. Ce n'est ni une transplantation de `z`, ni un mouvement de matière. L'API accepte
   toutefois silencieusement des listes I/J de longueurs inégales, et l'éligibilité dépend de
   `rho` et de `Mf[0]` même si l'objectif d'appariement n'en dépend pas.
2. **Dénominateur.** `60/60` signifie 60 assertions stockées vraies : 44 lignes bloc-spécifiques
   sur quatre états DEV, plus 16 assertions globales/adversariales. Les quatre blocs ont la même
   géométrie A/B et le même manifeste de paires : l'effectif géométrique est un, pas quatre ni 60.
3. **Oracles.** Les premières portes F2/F5/F6 sont de vrais `FAKE_PASS`. Le F2 de remplacement
   accepte deux classes de masques faux ; F5 accepte des lignes supplémentaires, dupliquées ou
   inconnues ; la porte O1 de phase C2 relance des copies identiques ; l'« identity hook » est un
   no-op. Le vérificateur charge le ledger 60/60 sans l'utiliser, ne lit ni protocole ni
   `SHA256SUMS`, et accepte plusieurs schémas mal formés.
4. **Nombre d'opérateurs.** Le commit cible contient un seul opérateur scientifique,
   `transpose()` sur `Mf[0]`. La revendication de trois opérateurs orientés est absente et donc
   `CONTRADICTED` dans ce dossier.
5. **Endpoint.** Les comptes pré-step sont cohérents en interne : une région, 172 liens
   matière–bain par bloc et zéro incidence A/B, soit 0/688 descriptif sur quatre répétitions de la
   même géométrie. F10 et le vérificateur utilisent toutefois le masque pré-step, pas le masque
   enregistré au temps d'échange. Le support réalisé est `INDETERMINATE` dans ce périmètre.
6. **Profondeur.** Les quatre ratios nommés
   `component_min / boundary_median` ne se recalculent pas : écarts relatifs de 11,6 à 15,1 %.
   La distance est aussi libellée de façon incohérente : 13 en euclidien contre 14 en graphe.
7. **Inférence.** L'allocation s'annule bien dans le statisticien D sous les deux potentiels
   déterministes. Le test de Fisher est un test exact de sharp null, mais ici essentiellement un
   comptage de signes à n=10, plancher bilatéral 2/1024 et sans information graduée sur la
   magnitude. L'intervalle inversé est un intervalle de compatibilité sous effet additif constant,
   pas un intervalle exact pour un effet moyen hétérogène. Aucun contraste cible n'existe.

## Scores du dossier et du papier

Les scores mesurent la **force documentaire du claim audité**, pas sa probabilité d'être vrai ni
la qualité globale du projet. Chaque score répartit 100 points entre traçabilité des octets (20),
congruence code–claim (25), reproduction indépendante (25), preuve brute pertinente (20) et
clarté de portée (10). Un claim non observé ou contaminé reste `NON-SCORÉ` plutôt que de recevoir
un zéro artificiel.

| Partie réellement auditée | Score | Limite déterminante |
|---|---:|---|
| Dossier — théorème logiciel de transposition et déterminisme du matching | **82/100** | preuve hors moteur forte, mais domaine d'entrée insuffisamment gardé et données DEV brutes non relues |
| Dossier — qualification `60/60`, oracles et vérificateur | **34/100** | octets traçables, mais faux/incomplets oracles et vérificateur non indépendant |
| Dossier — topologie et support pré-step | **66/100** | cohérence croisée forte des JSON ; une géométrie et aucune reconstruction depuis le masque brut |
| Dossier — support au temps exact de l'échange | **NON-SCORÉ** | `NOT_AUDITABLE / INDETERMINATE` : masque complet non retenu et cardinalité différente |
| Dossier — effet causal c/N | **NON-SCORÉ** | `NOT_TESTED` : aucun contraste cible |
| Papier — exposé méthodologique maximal « permutation conditionnelle » | **74/100** | publiable après réduction de portée et correction des gardes/oracles |
| Papier — récit d'arrêt par endpoint/topologie | **55/100** | conclusion prudente, mais preuve temporelle, ratios et vocabulaire quantitatif à corriger |
| Papier — résultat causal, absence d'effet ou généralisation | **NON-SCORÉ** | aucun résultat primaire et réplication held-out non auditable |

Le matériau soutient donc au mieux une **note méthodologique/corrective**, pas un papier de résultat
causal ETCMNFC. Les qualifications DEV, un scellement temporel prospectif et une géométrie
identifiable restent à reconstruire sous un nouvel identifiant avant toute autre prétention.

## Roadmap sans lancement

La route la moins coûteuse et informative est le flux natif traversant les contours A/B gelés,
mais elle répond honnêtement à une question **composante–matériau environnant**, pas
composante–bain. Un flux extérieur global à horizon justifié est une nouvelle hypothèse systémique
sans attribution A/B. Seule une nouvelle fondation à deux corps déconnectés, chacun avec sa vraie
frontière vers le bain, conserve littéralement la question originale ; elle a le meilleur score
de fidélité scientifique mais le coût le plus élevé.

`WARPED-SCALE-GEOMETRY-00` et `QUANTUM-BASIN-00` restent `NON-SCORÉ` et non autorisés à l'exécution
par cet audit. La prochaine valeur informationnelle vient d'abord d'une revue indépendante du
pilote multiscalaire ; poursuivre la voie de transport à un corps achète moins d'information,
sauf choix explicite de la nouvelle fondation à deux corps.

## État GitHub et conservation

La lignée locale ETPC → EEFCA → ETNBFC → ETCMNFC est une chaîne directe cohérente, mais aucune de
ses refs, commits, PR, release ou tag n'est présente sur le dépôt public observé. Le plan, le code
et les résultats ETCMNFC ont été ajoutés dans le même commit ; le hash du protocole scelle ses
octets, pas son antériorité temporelle.

Le seul workflow actif se déclenche sans filtre sur `push` et `pull_request` et exécute du code
scientifique du dépôt. En conséquence, **aucun push et aucune draft PR n'est admissible** sous la
règle zéro moteur/trajectoire. La remise sûre est un bundle Git et une archive audit-only vérifiés
localement. Une publication distante ne redevient éligible qu'après une correction du workflow
revue séparément et une confirmation préalable qu'aucun run ne peut être déclenché par la ref et
le pathset d'audit.

## Décision et action exacte suivante

Conserver le stop, publier une correction append-only locale et ne pas recycler le programme
ETCMNFC sous le même identifiant. L'action scientifique suivante autorisée par cet audit est la
**revue de protocole, sans exécution, de `WARPED-SCALE-GEOMETRY-00`**. Si la priorité du propriétaire
reste strictement la question composante–bain, la seule alternative fidèle est de rédiger — sans
lancer — un nouveau protocole Route 3 à deux corps et une nouvelle séparation DEV/held-out.
