# CCRA01 et revue du 4 septembre : adjudication indépendante

**Disposition : calcul CCRA01 confirmé ; analyse rétrospective, aveuglement déclaré mais non vérifiable ; manuscrit C v0.2 non publiable en l'état.** La récupération résout la lacune documentaire. Elle n'ajoute aucune expérience prospective et ne démontre ni une capacité, ni un mécanisme, ni l'absence d'un effet. Une correction de notre audit précédent est nécessaire : le recoût à deux bras donne bien **38 paires**, et non 36, lorsque le plafond d'OMLDCT02 devient contraignant.

Source auditée : `recovery/edl-state-20260904`, `b391a73978f515e50738e8fade20c389cf131d8b`. Les fichiers sources restent inchangés. Ce sous-audit n'a lancé aucun monde et n'a importé aucun moteur ; les simulations statistiques mentionnées ci-dessous sont des tirages de lignes déjà acquises ou des signes synthétiques.

## 1. Ce que l'histoire Git établit

| Commit | Heure UTC déclarée | Changement vérifié |
|---|---|---|
| `fe6b631` | 4 septembre 22:28:01 | Racine autonome de récupération : 251 fichiers ; pas de parent historique EDL |
| `6c77300` | 22:58:59 | Ajout des deux scripts de vérification/recalcul auparavant absents |
| `4a632d9` | 23:04:31 | Retour adverse de 28 findings, avant l'adjudication |
| `c363afd` | 23:19:29 | Code, protocole et capacité CCRA01 **avec** adjudication REVIEW01 |
| `0fdc550` | 23:20:15 | Résultat CCRA01, 46 secondes après le commit de gel |
| `23eb684` | 23:28:20 | Manuscrit v0.2, rapport et matrice révisés ; v0.1 préservée |
| `178b26e` | 23:28:42 | Correction documentaire de taille |
| `b391a739` | 23:29:20 | Mention de vérification finale |

Le protocole, le code et la capacité sont identiques octet à octet entre `c363afd` et le sommet livré. Les SHA-256 du protocole (`2cae5619…dad39`) et du code (`df1d4d6e…273b3`) concordent. Le commit de gel n'est donc pas littéralement « seul » : il contient aussi l'adjudication, écart déjà reconnu par la matrice de l'auteur. Aucun résultat CCRA01 n'y est présent.

Les horodatages et messages Git sont des métadonnées de l'auteur, pas un horodatage externe indépendant. L'ordre des objets prouve une séparation des versions commitées ; il ne prouve pas que personne n'a exécuté ou consulté une analyse avant le commit. Les résultats OMLDCT03 des mêmes 41 paires figurent déjà dans les ancêtres de CCRA01.

Le protocole fournit un inventaire de six fichiers autorisés et une déclaration d'absence d'exposition aux issues. **Aucun transcript du spécificateur, journal d'accès ou détail de son contexte hérité n'est livré.** Le niveau correct est `BLINDING_DECLARED__NOT_INDEPENDENTLY_VERIFIABLE`. Un auteur secondaire réellement aveugle peut réduire certains choix opportunistes ; il ne transforme pas les données déjà acquises, sélectionnées et examinées par le programme en échantillon prospectif.

Preuve reproductible : `HISTORY_AND_BINDINGS.json`.

## 2. Recalcul de CCRA01 depuis les endpoints indépendants

Les dix champs effectifs par paire ont été reconstruits depuis `results/OMLDCT03_PER_PAIR.json`, lui-même produit auparavant depuis les cellules des archives. Les 410 comparaisons avec les enregistrements de septembre concordent. Un nouveau score ordinal indépendant est appliqué ; le script gelé est ensuite exécuté comme contrôle différentiel, après inspection AST de ses imports limités à la bibliothèque standard.

| Quantité | Résultat indépendant |
|---|---:|
| Paires retenues | 41/41 |
| SELECTIVE pire / meilleur / égal | 17 / 24 / 0 |
| Paires décidées par le rang | 11 : 7 pertes, 4 gains |
| Paires décidées par la durée | 30 : 10 pertes, 20 gains |
| Seuil critique, alpha unilatéral 0,025 | 28 pertes |
| p exact | 983500178123/1099511627776 = 0,8944882011955997 |
| theta estimé | −0,17073170731707318 |
| Intervalle descriptif 95 %, transformé de Clopper–Pearson, aucune égalité | [−0,473664 ; +0,157808] |
| Analyse secondaire au départage par exposition | Même 17/24/0 et même p |

Le JSON complet du résultat gelé et celui de ses cinq contrôles de capacité sont identiques aux fichiers livrés. Les contrôles indépendants couvrent l'énumération exhaustive des signes pour m=0…14, l'inversion de tous les signes en échangeant les bras, l'invariance au renommage des deux chaînes de rang 0, les 41 égalités synthétiques, et le compte critique exact.

**Le terminal historique `NEGATIF` est arithmétiquement reproduit.** Il signifie ici « direction adverse non soutenue par cette procédure ordinale », sous ses hypothèses d'échantillonnage. Il ne signifie ni absence d'effet, ni équivalence, ni élimination du problème de mesure. Le plancher de six discordances garantit seulement qu'un rejet serait possible ; ce n'est pas une démonstration de puissance suffisante. À m=41, le seuil entier donne une taille nulle exacte de 0,0137666, inférieure à 0,025 ; les 27 rejets sur 2 000 permutations du contrôle sont compatibles avec cette discrétisation.

Une décomposition **post hoc, non substituée au test primaire**, conserve seulement le rang : 7 pertes/4 gains/30 égalités, p unilatéral 0,274414. Elle montre pourquoi le titre « arm-symmetric composite » exige une restriction : le sens négatif du composite complet repose principalement sur la durée, dont le protocole reconnaît explicitement qu'elle reste sensible au canal MERGE.

Preuves : `CCRA_INDEPENDENT.json`, `FROZEN_DIFFERENTIAL_REPLAY.json`, `ANALYTIC_TESTS.json`.

## 3. Nouvelle lecture des archives

Les 82 NPZ SHAM/SELECTIVE ont été rehachés contre le ledger scellé puis relus, avec chargement NumPy sans pickle. Un nouveau calcul des composantes à partir des cellules donne :

- SELECTIVE : 9 672 pas à une composante sur 9 713 pas inclusifs ; les **41 autres pas sont exactement les 41 pas déclencheurs t_m**, un par paire. Tous les pas strictement postérieurs à t_m, jusqu'à la fin de l'intervalle suivi, n'ont qu'une composante dans ces 41 archives.
- SHAM : 534 pas à une composante sur 8 353 ; les autres occupent deux à cinq composantes.
- L'absence de Y dans le monde entier après t_m concerne 12 indices SELECTIVE et 2 SHAM, avec table appariée **11 / 1 / 1 / 28** et p descriptif exact bilatéral 0,00634765625.

La qualification 99,6 % est donc reproduite, avec son dénominateur inclusif. Les deux composantes à t_m correspondent au cadre enregistré au déclenchement ; elles ne constituent pas une observation de retour ultérieur du canal MERGE dans SELECTIVE pendant l'intervalle. Cela ne permet pas d'extrapoler une suppression absolue à d'autres campagnes ou paramètres ; le profil cité de 33 paires reste un autre jeu de données.

Preuve : `RAW_OCCUPANCY_AND_MORTALITY.json`, qui détaille les pas relatifs à t_m.

## 4. Les 28 findings : acceptés n'est pas synonyme de corrigés

La matrice `FINDINGS_28_MATRIX.csv` donne une disposition, un commit et une preuve pour chacun. Bilan : **14 résolus**, **9 résolus avec une limite ou une portée explicite**, **1 route traitée sans démonstration exhaustive**, **4 partiels**.

Les quatre premiers défauts fatals reçoivent une correction observable : scripts ajoutés et livrés ; test 9-contre-0 retiré ; fichier vide reconnu ; facteur temporel corrigé. Le cinquième est traité par l'exécution de CCRA01 et la reconnaissance de deux autres routes sur données existantes. Cela clôt l'omission initiale, mais ne justifie pas une affirmation universelle qu'aucune expérience possible n'aurait d'intérêt.

Les résidus précis sont :

- **F8, puissance** : code/RNG/résultats bootstrap originaux absents ; la puissance empirique d'une conjonction de deux tests n'est pas une simple fonction du seul p de durée ; les « vérités compatibles » ne sont pas des probabilités établies par ce bootstrap. La non-détection ne prouve pas à elle seule qu'une hypothèse de puissance antérieure était fausse.
- **F9, contamination** : l'exposition antérieure est divulguée, mais la phrase « cela n'enfle pas l'erreur de première espèce » est inconditionnelle. L'arithmétique d'un test fixé ne certifie pas le contrôle d'erreur de la procédure qui décide de l'appliquer après inspection d'issues corrélées.
- **F24, statuts** : le manuscrit v0.2 promet une réémission verbatim mais abrège trois chaînes `RPP97_STATUS`, `RPP98_STATUS`, `FIMRCC02_STATUS` en `WITHDRAWN under their recorded strings`. Le rapport et la matrice donnent les valeurs complètes.
- **F28, taille** : les 3 963 075 octets de charge sont correctement distingués, mais le rapport de récupération nomme encore 4 053 773 octets comme taille de l'arbre complet du premier commit. `git ls-tree -rl fe6b631` donne **251 fichiers et 4 050 424 octets de blobs** ; le manifeste et l'arbre final ont d'autres périmètres.

Les fichiers originaux du premier rapport et de sa matrice ne sont pas préservés comme versions autonomes avant correction ; leurs phrases initiales sont accessibles via le verbatim du checker. Le manuscrit v0.1 est préservé et directement comparable. Nous ne faisons donc pas passer des citations adverses pour une preuve byte-à-byte d'une version absente.

## 5. Défauts nouveaux à corriger avant réemploi dans un article

Ces points ne changent aucun chiffre de CCRA01. Ils limitent son interprétation :

1. **Identifiabilité des hazards.** Le protocole affirme que supprimer un risque concurrent gonfle nécessairement les hazards cause-spécifiques restants et les rend non identifiables sans indépendance. C'est trop fort. Les risques instantanés observés parmi les trajectoires encore à risque et les incidences cumulées sont des quantités descriptives identifiables ; une distribution latente ou un effet direct dans un monde où un événement concurrent serait empêché pose une autre question. La condition d'indépendance ne doit pas être transférée de cette question contrefactuelle à toute estimation descriptive. Cette distinction est explicite dans [Pintilie, *Choice and Interpretation of Statistical Tests Used When Competing Risks Are Present*](https://pmc.ncbi.nlm.nih.gov/articles/PMC2654314/) et [Andersen et al., *Competing risks in epidemiology: possibilities and pitfalls*](https://pmc.ncbi.nlm.nih.gov/articles/PMC3396320/). Les passages pertinents étaient accessibles dans l'index de recherche ; l'ouverture intégrale de PMC a renvoyé un écran de vérification.
2. **Support commun n'est pas invariance de mesure.** Que chaque bras puisse atteindre les rangs 0/1/2 ne garantit ni une même distribution sous une hypothèse nulle mécanistique, ni une même signification biologique. CCRA01 est un composite commun par définition ; il conserve un effet total de l'intervention sur un instrument relationnel. Écrire « outcome labels share a common support » plutôt que « the measurement problem is repaired ».
3. **Appariement n'est pas randomisation.** Le code fork clone état physique et RNG puis applique les trois interventions nommées. Aucun tirage aléatoire d'affectation des étiquettes n'est montré. Une comparaison contrefactuelle dans ce modèle et sous ce couplage RNG est calculable, mais « identified by exact pairing alone » omet le modèle, le couplage et l'hypothèse de signes équiprobables/indépendants utilisée pour généraliser aux graines. Ne pas importer le langage d'un essai randomisé sans qualifier cette différence.
4. **Un effet sur un canal terminal peut être une partie de l'effet total.** La phrase « termination channels must be invariant under the intervention » est une règle trop générale. Elle est pertinente si l'on veut isoler une continuation intrinsèque de l'objet ; elle n'est pas une condition nécessaire de validité de tout effet total sur une durée définie identiquement. Les risques concurrents rendent surtout indispensable une cible d'inférence explicite.
5. **Post hoc n'est pas automatiquement conditionné sur le traitement.** Une analyse rétrospective peut conserver les 41 paires sans filtrage post-traitement — CCRA01 en est précisément un exemple. Elle demeure exploratoire quant à sa sélection, sans nécessairement avoir le biais de conditionnement propre aux restrictions aux survivants.
6. **Pas de domination réfutée.** L'abstract affirme que le confondant de mortalité « does not dominate ». Ce n'est pas établi par un p unilatéral élevé et un rang ordinal arbitré 30 fois par la durée. Remplacer par la simple description du critère non franchi et de la décomposition 11/30.

Deux détails de robustesse du code peuvent être consignés sans rejuger ce run : le schéma annoncé à onze champs en contient effectivement dix ; le validateur ne lie pas lui-même l'entrée à un SHA scellé et traite imparfaitement certains types malformés. Aucun de ces problèmes n'affecte les dix champs valides des 41 enregistrements effectivement contrôlés ici.

## 6. Puissance et temps : ce qui se reproduit

Les 885 durées de calcul donnent moyenne 89,380904 s, médiane 85,1 s, somme 79 102,1 s, maximum 627,6 s. Le maximum des deux `batch_seconds` donne 10,851417 h ; la somme des temps individuels divisée par deux donne 10,986403 h. Le premier est un proxy fondé sur les métriques de batch, pas une trace complète d'ordonnancement.

La loi de Jeffreys Beta(41,5 ; 844,5) donne q05/q50/q95 = 3,5779 % / 4,6499 % / 5,9063 %. À ce débit historique, 12 h correspondent à 978,67 graines, soit **45,51 paires attendues au taux médian** ; 400 paires correspondent à **105,48 h**. Les quantiles du taux ne sont pas à eux seuls des intervalles prédictifs de la campagne : l'aléa d'acquisition future et la relation entre durée et admissibilité restent à propager.

Le paquet ne contient pas l'algorithme, le RNG ou les sorties de la projection de puissance originale. Nous fournissons donc une **nouvelle analyse diagnostique explicitement spécifiée**, pas une fausse reproduction bit-à-bit : bootstrap apparié, 10 000 tirages par effectif, rangs moyens avec correction des égalités, approximation gaussienne sans correction de continuité, conjonction et accord de signe. Elle donne 0,1542 à 41 ; 0,1694 à 45 ; 0,3224 à 100 ; 0,5438 à 200 ; 0,8387 à 400. Les intervalles Monte-Carlo sont enregistrés. Ces valeurs soutiennent l'ordre de grandeur, pas le dernier chiffre publié.

Notre double bootstrap 100×200 donne q05/q50/q95 = 0,01975 / 0,6675 / 1 et 45 % des réplications sous 0,50, contre les 34 % publiés. C'est une fréquence sous un rééchantillonnage instable, pas une mesure de la probabilité que des « vérités compatibles » soient sous-puissantes. **Ces projections portent sur OMLDCT03, pas sur le composite CCRA01.** Elles n'autorisent aucun nouveau monde.

## 7. Erratum à notre précédent audit : 38, pas 36

Le script précédent `scripts/recompute_omldct.py` ajoutait deux continuations complètes dès que `TRIGGERED` était vrai. Or **12 des 53 graines déclenchées échouent avant fork**, par exemple l'indice 96 (`TRIGGERED_IDENTITY_NOT_CARRIED`, 703 pas de préfixe, pas d'archives). Seules les 41 entrées avec `ARCHIVES` ont effectivement produit les bras.

Le recoût fidèle vaut : préfixe/horizon pour chaque graine, puis deux continuations seulement si les bras ont été exécutés. Il donne **571,649364** instances, ou **571,649394** si l'on part du coût enregistré arrondi et retranche le bras DISPLACED. Le dernier indice terminé avant le franchissement est **788**, coût **511,535273**, **38 paires** ; l'indice **789** porte le coût à **512,126273**, toujours 38 paires.

**À retirer de l'autorité active de notre audit : 593,509909 ; indice 760 ; 36 paires.** L'erreur est la nôtre. Elle n'invalide pas la conclusion que 41 paires dépassent l'accrual gelé, mais elle invalide notre reproche numérique au checker. Les fichiers historiques doivent rester visibles avec cet erratum.

Correctif minimal recommandé au parent : dans la ligne de `cost2` du script, remplacer `if r.get('TRIGGERED')` par `if 'ARCHIVES' in r`, puis régénérer `OMLDCT03_INDEPENDENT.json` et les passages actifs du rapport/journal/handoff. Ajouter une assertion documentant les 12 déclenchements sans bras, afin que la distinction ne disparaisse pas. Ne pas réécrire un ancien journal pour cacher l'erreur.

Preuve et exemple complet : `PRIOR_ASTRA_COST_ERRATUM.json`.

## 8. Contribution scientifique conseillée

CCRA01 convient comme **réanalyse de sensibilité rétrospective et exemple des limites d'un suivi relationnel**. Il ne constitue pas une jambe positive de persistance, de propriété locale ou de reproduction ; le manuscrit de septembre le dit lui-même. Son résultat négatif n'améliore pas à lui seul la thèse phare B et ne doit pas être agrégé aux données d'une autre architecture.

Texte anglais réutilisable après intégration de la provenance :

> In a separate retrospective reanalysis of 41 matched trajectories, a documented ordered outcome combined the termination category with duration. An independently recomputed one-sided sign test returned 17 lower and 24 higher treated outcomes (p = 0.8945). Eleven comparisons were decided by termination rank and thirty by duration. The analysis therefore did not support its stated adverse direction. Its author reported outcome blinding and committed the specification before the result file; the available record does not independently verify that blinding. This reanalysis neither isolates a mechanism nor establishes equivalence or absence of an effect.

Le meilleur réemploi est un encadré ou supplément de méthode si le nouvel article en a besoin. À conserver séparément si ce cas détourne de la démonstration principale sur la persistance et l'absence de validation du critère de propriété locale.

## Reproduction

Depuis la racine du checkout, avec le Python scientifique existant :

```powershell
& 'C:\Users\tommy\Documents\ising-v3-recovery\ising v3\.venv\Scripts\python.exe' audit/edl-flagship-01/september4_adjudication/audit_september4.py
& 'C:\Users\tommy\Documents\ising-v3-recovery\ising v3\.venv\Scripts\python.exe' audit/edl-flagship-01/september4_adjudication/adjudicate_findings.py
```

Les sorties sont limitées à ce dossier. Validation réalisée avec Python 3.12, NumPy 2.5.1 et SciPy 1.18.0 ; temps d'exécution d'environ dix secondes sur ce checkout. Aucun moteur, nouveau monde, commit, push, modification des sources ou changement de statut expérimental n'a été effectué par ce sous-agent.
