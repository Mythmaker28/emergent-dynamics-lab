```
MISSION       ORGANIZER-BOUND-TURNOVER-CLOUD-02
DISPOSITION   ORGANIZER_BOUND_CLOUD_PARTIAL
```

Les deux défauts d'OBTC01 sont mécaniquement fermés, le plan scientifique a été rejoué **sans le
moindre redesign** — `SCIENTIFIC_THRESHOLD_DIFF = EMPTY`, enveloppe prédictive bit-à-bit
identique — et dix-sept bras ont tourné sur des graines entièrement neuves, tous techniquement
valides, les deux évaluateurs d'accord partout. Le mécanisme de source est confirmé. Un élément
confirmatoire manque : la condition de taille de domaine exigeait 2 bras sur 3 et en donne 1.

---

## 1. Provenance

Artefact OBTC01 réassemblé dans un espace neuf ; sommes des trois morceaux recalculées ; `sha256`
de l'archive `9e6af669…16c2b` ; clone **espace de noms réseau supprimé** (DNS et TCP négatifs à
l'intérieur, positifs à l'extérieur, `GIT_NO_LAZY_FETCH=1`).

```
HEAD a0ed70cd05ada70f4cbe6555edf1e3d9f6a98922   arbre 0f8f82e34e7e18e7c2efaba4b779adecde7b304f
branche codex/organizer-bound-turnover-cloud-01   1391 fichiers
objets manquants 0   remotes promisor 0   porcelain vide   fsck propre
freeze, spec, registre des starts, brut de 8101 et sorties divergentes : tous présents
harnais rejoués : OBTC01 4/4 PASS, CSC01 ALL_PASS, ORR01 ALL_PASS
```

**Une divergence attendue est consignée** : le manifeste de gel d'OBTC01 enregistre l'état
*avant* correctif, alors que l'artefact contient le code *après*. Exactement **deux fichiers sur
dix** diffèrent — `gate_obtc.py` et `protocol_obtc.py` — et 8 fichiers de code sur 10 plus 5
documents sur 5 sont identiques à l'octet. En annulant précisément les deux éditions documentées,
les deux fichiers **retrouvent exactement leur hachage gelé**. La différence est donc exactement
les deux correctifs, et rien d'autre.

## 2. HEAD, arbre, branche et commits

Branche `codex/organizer-bound-turnover-cloud-02`, partie du HEAD OBTC01 exact ci-dessus.

## 3. Cause racine du défaut principal

```
fichier   OBTC01/code/protocol_obtc.py     fonction  run_arm     rappel  per_step
appels à `online.*` dans per_step, code GELÉ    : ['step']
appels à `online.*` dans per_step, code CORRIGÉ : ['step', 'frame']
trames attendues 220 au total, 180 éligibles après burn-in
compte observé : flux 0, table 220
```

Huit agrégats ont divergé : `core_exists_frac`, `frac_r80_org_ok`, `frac_with_org`,
`median_core_to_org`, `median_step_displacement`, `disp_over_N3`, `drift_thirds`, `third_means`.

## 4. Cause racine du défaut secondaire

Convention écrite : trois blocs consécutifs égaux des pas post-burn-in, indexés depuis zéro.
Convention codée : `(t − BURN_IN) · 3 // T_WINDOW` avec `t` partant de `BURN_IN + 1`, ce qui place
les frontières un pas trop tard. Sur `T = 9000`, **2 pas** sur 9000 changent de tiers ; la
différence relative observée sur le bras consommé est `2.5 × 10⁻⁵` et n'aurait pas pu changer la
classification. Le défaut reste réel : c'est une erreur de frontière, et une erreur de frontière
compte exactement quand un run est près du seuil.

L'audit a montré que la correction « moins un » n'est équivalente au découpage tableau que pour
les horizons **divisibles par trois**. La convention retenue reproduit donc littéralement le
découpage tableau, cas dégénéré compris : `q = T//3` ; si `q == 0` le bucket est 2 ; sinon
`min(2, i//q)`. Elle est vérifiée exacte pour `T` = 9000, 9001, 8999, 300, 5, 4, 3 et 1.

## 5. Direction du biais

```
DIRECTION = FALSE_NEGATIVE_ONLY_FOR_THE_GATE_AS_A_WHOLE
```

Formulation plus étroite, qui est celle qu'il faut retenir : **quatre** des cinq conditions
dérivées des trames deviennent automatiquement fausses quand le flux est vide —
`RELATIVE_LOCALIZATION`, `CORE_CONTINUITY`, `SOURCE_ATTACHMENT`,
`MODEL_PREDICTION_COMPATIBILITY`. La cinquième, `NO_TRUE_WINDING`, devient automatiquement
**vraie**, parce que son critère est « au plus zéro trame enroulée » et que zéro trame le
satisfait trivialement. Le gate étant une conjonction, un flux vide ne peut produire qu'un échec
global — mais l'affirmation par condition n'est **pas** uniforme, et `NO_TRUE_WINDING` aurait été
rapportée satisfaite sur aucune preuve. La portée est celle de la configuration OBTC01 et de ses
seuils ; aucune propriété universelle n'est revendiquée.

## 6. Diff scientifique

```
LAWSPEC_DIFF                    NONE
SCIENTIFIC_GATE_FORMULA_DIFF    NONE
SCIENTIFIC_THRESHOLD_DIFF       EMPTY   (0 entrée, comparaison mécanique clé par clé)
INTERVENTION_DIFF               NONE
SEQUENTIAL_SCIENTIFIC_RULE_DIFF NONE
enveloppe prédictive N2          bit-à-bit identique à celle gelée par OBTC01
```

## 7. Diff d'instrumentation

```
INSTRUMENTATION_DIFF     online.frame restauré ; compteurs et sommes de contrôle de transport de
                         trames ajoutés ; NO_TRUE_WINDING gardé contre un flux vide, garde
                         inatteignable dès que RUN_TECHNICALLY_VALID est vrai ; les deux
                         conditions inter-bras implémentées depuis leurs seuils déjà gelés ;
                         l'agrégateur post hoc réécrit indépendamment du flux
TEMPORAL_INDEXING_DIFF   frontières de tiers corrigées, exactes pour tout horizon
TECHNICAL_VALIDITY_LAYER ADDED
SEED_FAMILY_DIFF         familles OBTC01 retirées, familles OBTC02 fraîches
```

## 8. Validation du transport des trames

Sur un run propre : attendu 180, flux 180, table 180, sommes d'index et de charge identiques.
Six fautes injectées, **toutes attrapées** : aucun appel, dernière trame omise, première trame
éligible omise, trame du milieu dupliquée, première trame dupliquée, tous les appels décalés d'une
trame. `FRAME_STREAM_TABLE_IDENTITY = PASS`.

## 9. Validation des tiers

`THIRD_BOUNDARY_TESTS = PASS` sur huit horizons, divisibles et non divisibles par trois, jusqu'à
la fenêtre minimale.

## 10. Accord online / post hoc

```
synthétique, 24 bras aléatoires                  PASS
historique, 8 séries ORR01 et CSC01 enregistrées PASS
brut de la seed 8101, après correctif            PASS
sur les 17 bras confirmatoires                   PASS, sans exception
```

Les deux agrégateurs ne partagent que la spécification des seuils et la fonction finale de
verdict ; toute l'agrégation est écrite deux fois, par des routes différentes.

## 11. Reclassification diagnostique de 8101

Après correctif, flux et table s'accordent sur les 180 trames enregistrées, et le run est
techniquement valide. **Cette reclassification reste `DIAGNOSTIC_ONLY`** : elle n'est ni une
confirmation, ni un pilote, ni une justification de seuil, d'enveloppe ou de budget.

## 12. Seeds retirées

`8101` — exécutée et ouverte — plus `8102-8106, 8201-8203, 8301-8303, 8401-8402, 8501-8503`,
retirées par précaution bien qu'elles n'aient jamais tourné.

## 13. Seeds fraîches

`P 9101-9106`, `S 9201-9203`, `R 9301-9303`, `N 9401-9402`, `D 9501-9503`. Règle de génération
gelée avant les runs. Disjonction prouvée par balayage de **tous** les `.py`, `.yaml` et `.json`
du dépôt reconstruit — **111 graines distinctes** trouvées dans MCM01, ORR01, CSC01, OBTC01,
`edlab`, `results` et `tests` — intersection **vide**.

## 14. Chronologie des prédictions

Les neuf quantités sont `DERIVED_BEFORE_8101`. Preuve : le manifeste de gel d'OBTC01 enregistre
**zéro démarrage dans chaque classe** et contient déjà les prédictions analytiques. Elles sont
re-dérivées ici depuis le code seul et concordent :

```
a = 0.050000   D = 0.025000   ell_X = 2.500000   ell_rel = 3.535534
r80 statique 6.082763   r80 relatif 8.544004   cœur-organisateur 3.123878
retard optimal 249.000000   décroissance source-off 249.499666
FIT_TO_8101 : aucune          UNRESOLVED : aucune
```

## 15. Statut de l'opérateur idéal

```
UNBLOCKED_DISCRETE_KERNEL = EXACT
```

Portée : le noyau `K_u = (1−µ)^u P_u` de la marche libre à quatre tentatives, avec
`a = 2q(1−q)` exact et le profil stationnaire inversé par transformée de Fourier exacte sur le
tore. C'est une propriété du **noyau**, pas du run.

## 16. Statut de l'opérateur complet

```
FULL_CAPACITY_CONSTRAINED_OPERATOR = APPROXIMATE_WITH_EMPIRICAL_ERROR
```

Pas `WITH_BOUNDS` : aucune borne déterministe, aucun intervalle certifié et aucune borne
probabiliste préenregistrée n'a été produite avant les runs, et une majoration analytique
exigerait de borner la distribution d'occupation locale, qui n'est pas disponible. Les taux de
refus sont donc rapportés comme des **mesures** :

```
sur les 17 bras frais   X moyenne 3.38e-4, maximum 5.58e-4
                        Y moyenne 3.85e-4, maximum 1.79e-3
diagnostic 8101         X 3.4e-4, Y 8.9e-4
```

Aucune enveloppe n'a été resserrée : elle est identique à l'octet près.

## 17. Satisfiabilité du gate

Certificat constructif rejoué : un bras synthétique satisfait les **dix** conditions par bras
simultanément, et briser chacune à son tour brise exactement celle-là. Les **deux** conditions
inter-bras sont certifiées séparément : sur un jeu sain elles passent toutes deux ; en doublant
`r80` au grand domaine seule `DOMAIN_SIZE_INVARIANCE` tombe ; en supprimant la décroissance seule
`CAUSAL_SOURCE_DEPENDENCE` tombe. **Convention de regroupement** : OBTC01 déclarait douze
conditions, dix évaluables sur un bras et deux qui ne le sont pas — un bras seul ne peut exhiber
ni l'invariance à la taille du domaine ni la réponse au retrait de la source.

```
GATE_SATISFIABILITY PASS   FRAME_STREAM_TABLE_IDENTITY PASS   THIRD_BOUNDARY_TESTS PASS
ONLINE_POSTHOC_AGREEMENT PASS   PROTOCOL_ADVERSARIAL_AUDIT PASS
```

## 18. Hash du gel

```
OBTC01_METHODS_CORE_HASH  f81b1c7ab92d1634b816c2b2f68ccf4fe3aadee4d9495822bbc71a11b7734eb5
OBTC02_METHODS_CORE_HASH  747c1f5e68da95c7b63b81b09fcc531cc0dc7b0e13a3ceadb54d10103fc350f7
démarrages avant ce gel   calibration 0, confirmation 0, contrôle 0, sonde de coût 0
```

## 19. Budget

Plafonds hérités, inchangés : calibration 4, confirmation 24, contrôle 8, sonde 2.

## 20. Starts consommés

```
SYNTHETIC_TESTS                  0 démarrage (mode statique et TEST borné)
RAW_ONLY_REPLAYS                 0 démarrage (relecture de données enregistrées)
COST_PROBES                      0
SCIENTIFIC_CONFIRMATORY_STARTS   17  (confirmation 12 : P 6, S 3, D 3 ; contrôle 5 : R 3, N 2)
TECHNICALLY_INVALID_STARTS       0
SCIENTIFICALLY_FAILED_STARTS     11
SCIENTIFICALLY_PASSED_STARTS     6
```

## 21. Condition P — organisateur mobile

**5 bras sur 6 passent les dix conditions par bras. Le critère gelé est 5 sur 6 : atteint.**
`9101` s'éteint. Les cinq autres : `N_X` moyen 118.7 à 128.6, `r80` 6.71 à 7.07,
distance cœur–organisateur 2.24 à 3.16, renouvellement 35.3 à 36.1, **6 statistiques sur 6 dans
l'enveloppe préenregistrée**, zéro enroulement réel, occupation exactement constante.

Rayon de giration observé 5.613 à 5.892 contre **5.853** analytiques. Durée de vie moléculaire
moyenne 240.0 à 247.9 pas contre **250** analytiques. Distance cœur–organisateur 2.24 à 3.16
contre **3.124**. Aucun paramètre ajusté.

## 22. Condition S — organisateur immobilisé

Rôle déclaré dans le manifeste gelé : profil statique et temps de relaxation, **pas** le passage
du gate par bras — la règle de qualification ne mentionne que P, D, R et N. Les trois bras
échouent `SOURCE_ATTACHMENT` pour une raison structurelle et attendue : la source ne bouge pas, la
corrélation des trajectoires déroulées est indéfinie, et `min(NaN, NaN) ≥ 0.5` est faux.

Physiquement le résultat est net : cœur présent à **1.000** des trames, distance cœur–organisateur
**0.00**, six statistiques sur six dans l'enveloppe, dérive 0.011 à 0.054, `N_X` 79 à 86.

## 23. Condition R — source retirée

```
e-folding observé   233, 297, 245 pas      prédiction analytique 249.5, fenêtre gelée [124.7, 499.0]
résidu après 5 e-foldings   0.000, 0.000, 0.000     seuil 0.05
N_X final   0, 0, 0
CAUSAL_SOURCE_DEPENDENCE, volet R : 3 sur 3 requis, 3 obtenus
```

C'est la confirmation la plus nette de la mission : le nuage disparaît, au rythme que l'opérateur
prédisait avant qu'aucun bras ne tourne.

## 24. Condition N — absence de source

`N_X = 0` du premier au dernier pas, sur les deux bras. 2 sur 2 requis, 2 obtenus.

## 25. Condition D — taille de domaine

**1 bras sur 3 passe ; le critère gelé est 2 sur 3 : non atteint.** Les deux échecs portent sur
`RELATIVE_LOCALIZATION`, à une fraction de trames de **0.933** contre **0.95** exigés — six
pour cent des trames dépassent la borne de 12.8, elle-même fixée à 1.5 fois la prédiction
analytique.

La condition **inter-bras**, elle, passe largement : `r80` médian **7.071** à `L = 36` contre
**7.036** à `L = 72`, soit une différence relative de **0.005** là où un rayon proportionnel à `L`
en donnerait 1.000. Le rayon est donc indépendant du domaine ; ce qui manque est le passage
**par bras** de la fraction de trames sous la borne, et le critère gelé porte sur les bras.

## 26. Condition E

Non ouverte. Le déclencheur analytique écrit avant la seed 8101 n'est pas satisfait : le
couplage de la source à `X` se mesure au niveau `3.85 × 10⁻⁴`, et surtout le confondant que E
existe pour éviter — conditionner un nul sur une trajectoire issue du résultat — ne se présente
pas, puisque le nul **génératif** ne conditionne sur aucune trajectoire réalisée. Ni l'existence
de 8101 ni la concordance observée n'ont modifié cette décision.

## 27. Renouvellement

Mesuré au niveau **moléculaire**, par registre d'identités : 35.3 à 36.2 remplacements complets,
**0.0000** unité initiale encore présente à la fin, **1.0000** des unités finales nées pendant la
fenêtre, sur tous les bras vivants. Durée de vie moyenne 240 à 248 pas contre 250 analytiques.

## 28. Localisation relative

`r80` dans le repère de l'organisateur sous la borne gelée à **1.000** des trames pour les cinq
bras P passants, et à 0.933 pour deux bras `D`.

## 29. Effet du domaine

Rayon médian 7.071 (`L = 36`) contre 7.036 (`L = 72`) : **0.5 %** d'écart pour un domaine deux
fois plus grand et quatre fois plus vaste. `DOMAIN_SIZE_INVARIANCE = PASS`.

## 30. Causalité de la source

`CAUSAL_SOURCE_DEPENDENCE = PASS`. Retirer la source fait disparaître le nuage avec le temps
prédit ; sans source, rien ne se maintient.

## 31. Compatibilité prédictive

Toutes les statistiques de tous les bras passants tombent dans l'enveloppe générative
préenregistrée, **6 sur 6**, seuil gelé 5 sur 6. L'enveloppe n'a pas été resserrée : elle est
identique à l'octet à celle d'OBTC01.

## 32. Portée scientifique

Dans le LawSpec équilibré testé, une source organisatrice mobile maintient causalement un nuage
dissipatif localisé et matériellement renouvelé, dont les principales échelles sont compatibles
avec un opérateur source–transport–décroissance préenregistré. Ce nuage n'est **pas** self-bound,
ne possède **pas** de cohésion autonome, n'est **pas** une cellule, ne possède **pas** d'identité,
ne se reproduit **pas**, ne mémorise **pas**, ne confirme **pas** H3 et ne valide **pas**
globalement Kamimura–Kaneko.

## 33. Prochaine éligibilité

La qualification complète n'est pas atteinte : il manque un bras à la condition de domaine. La
re-dérivation des temps n'est donc pas encore éligible.

---

```
GOOD_NEWS
Les deux defauts sont fermes mecaniquement et le plan a ete rejoue sans redesign : le diff de
seuils scientifiques est vide, l'enveloppe predictive est identique a l'octet, et dix-sept bras
frais ont tourne, tous techniquement valides, les deux evaluateurs d'accord partout. La condition
principale passe 5 sur 6, exactement le critere gele. Le retrait de la source fait disparaitre le
nuage avec un e-folding de 233, 297 et 245 pas contre 249.5 predits avant tout run, residu nul.
Sans source, rien ne se maintient. Le rayon est le meme a L = 36 et L = 72 a 0.5 % pres. Et
l'operateur, derive avant que la moindre graine ne tourne, predit sans un parametre ajuste : rayon
de giration observe 5.613 a 5.892 contre 5.853, duree de vie moleculaire 240 a 248 pas contre 250,
distance coeur-organisateur 2.24 a 3.16 contre 3.124, six statistiques sur six dans l'enveloppe.

FRAME_STREAM_TABLE_IDENTITY
PASS

THIRD_BOUNDARY_TESTS
PASS

ONLINE_POSTHOC_AGREEMENT
PASS

SCIENTIFIC_THRESHOLD_DIFF_FROM_OBTC01
NONE

OCCUPANCY_RATCHET_REPAIR
QUALIFIED

SOURCE_BOUND_LOCALIZATION
PARTIAL

SOURCE_RESPONSE_OPERATOR_UNBLOCKED
EXACT

SOURCE_RESPONSE_OPERATOR_FULL
APPROXIMATE_WITH_EMPIRICAL_ERROR

AUTONOMOUS_COHESION_STATUS
NOT_ESTABLISHED

C3_STATUS
NOT_QUALIFIED

TURNOVER_STATUS
QUALIFIED

DOMAIN_SIZE_INVARIANCE
PASS

CAUSAL_SOURCE_DEPENDENCE
PASS

WHAT_IT_CHANGES
Le nuage lie a l'organisateur cesse d'etre une conjecture. Sur des graines fraiches, sous un gate
gele et certifie satisfaisable avant execution, il est stationnaire, borne relativement a sa
source, renouvele integralement environ trente-six fois, et il disparait quand on retire la source
au rythme exact que la theorie annoncait. Ce qui manque n'est pas le mecanisme mais un bras : la
condition de domaine exigeait deux bras sur trois passant TOUTES les conditions par bras et n'en
donne qu'un, deux bras echouant la fraction de trames localisees a 0.933 contre 0.95. La grandeur
que cette condition visait - le rayon ne doit pas croitre avec le domaine - est quant a elle
confirmee a 0.5 %. La mission etablit aussi, contre son propre resultat precedent, que la
statistique brute de cohesion depend fortement de N_X sous un nul sans cohesion : 0.233 a 0.800
quand N_X passe de 30 a 320, et la verification a L = 72 montre que le moteur en est la convention
de composante par adjacence, pas la densite ni le domaine.

NEXT_SCIENTIFIC_ELIGIBILITY
NONE

H3_STATUS
NOT_TESTED

REPRODUCTION_STATUS
NOT_TESTED

SCIENTIFIC_RUNS_USED
17 : confirmation 12 de 24 (P 6, S 3, D 3), controle 5 de 8 (R 3, N 2), calibration 0 de 4, sonde
de cout 0 de 2, invalides 0. Passants 6, echecs scientifiques 11, techniquement invalides 0. Les
tests synthetiques et les relectures de donnees enregistrees ne sont pas des demarrages.

TECHNICALLY_INVALID_RUNS
0

PROTOCOL_VIOLATIONS
NONE. Les deux defauts d'OBTC01 sont fermes avant le gel, aucun seuil scientifique n'a bouge,
aucun run n'a ete relance, aucune graine remplacee, aucun echec rejoue, et la regle sequentielle
n'a jamais eu a se declencher.

PROVENANCE_STATUS
SELF_CONTAINED_SPLIT_DELIVERY_PASS

TOMMY_ACTION_REQUIRED
NONE
```
