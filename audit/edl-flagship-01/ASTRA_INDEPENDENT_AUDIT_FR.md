# EDL-ASTRA-FLAGSHIP-AUDIT-01

**FLAGSHIP_NOT_YET_JUSTIFIED — 5 septembre 2026.** Les données permettent un papier spécialisé défendable autour du candidat B. Elles ne justifient pas encore un papier phare réunissant persistance, non-échangeabilité et lignée. La jambe positive FDFLT01 est désormais vérifiée. Le paquet Claude du 4 septembre reste absent, donc CCRA01 et la résolution de ses cinq findings fatals restent non vérifiés.

Audit réalisé par Astra dans un checkout isolé, sans nouveau monde. Les résultats ci-dessous proviennent des fichiers et des nouveaux scripts de ce dossier. Les conversations antérieures ont servi à retrouver les sources, jamais à certifier les résultats. Une revue de l'agent ne constitue pas une validation externe.

## Réponses aux huit questions

1. **Archives retrouvées.** Les 123 NPZ TBRT02 sont contenus dans les 41 `TRIPLE_*.tar` de `C:\Users\tommy\Documents\ising v3\TBRT02`. Les 192 NPZ FDFLT01 proviennent de `C:\Users\tommy\Documents\ising v3\ISING_LIFE_AUTHORITATIVE_RECOVERY\FDFLT01\rawcore\FDFLT01_RAW_CORE.tar.zst`. Ce sont deux ensembles différents. Copies durables dans `recovery/TBRT02_raw` et `recovery/FDFLT01_core`, sur `recovery/astra-edl-tbrt02-20260905`, commit `2422492d13fa5e333d4d3111e9ca95de2d7cc9b7`. Les sorties de nombreuses missions sont présentes dans l'historique `5372fd86`; l'identité exacte des « huit sorties absentes » de Claude reste inconnue sans son inventaire.
2. **53/192 : OUI, depuis les données brutes nécessaires à l'endpoint.** Reconstruction des comptes Y et des centres sur **1 291 322 lignes** à partir des cellules, naissances et décès, puis reconstruction de X aux instants utiles. **5 184 champs** du tableau historique concordent, zéro désaccord, zéro exclusion, zéro réserve. Les cinq autres plans de champs complets ne sont pas récupérés : ne pas annoncer une identité d'octets avec les 192 NPZ complets d'origine.
3. **Cinq fatals corrigés : NON DÉMONTRÉ.** Le verbatim des 28 findings et ses corrections du 4 septembre ne sont pas accessibles. Les revues historiques FDFLT01, OMLDCT03 et CLOSE01 ne sont pas ce document. Accepter un finding ne prouve pas sa résolution.
4. **CCRA01 : arithmétique conditionnelle correcte, validité prospective inconnue.** Si les 17/41 sont des victoires adverses indépendantes sans égalités, le test binomial exact unilatéral supérieur donne **0,8944882012**. Le code, le composite, les égalités, le classement des paires, le gel, l'aveuglement et les cinq tests de capacité manquent. Une spécification avant analyse sur des données déjà vues dans le programme ne devient pas automatiquement une confirmation prospective. La conclusion « la mortalité ne domine pas » n'est pas autorisée par une non-significativité seule.
5. **Meilleure thèse : candidat B resserré.** « Dans ce modèle à mémoire construite, un état dépendant de l'histoire reste causalement actif après un profond renouvellement matériel. Cela ne suffit pas à établir sa propriété informationnelle locale : le critère prospectif d'exclusion des représentations concurrentes n'est pas satisfait. » La non-échangeabilité, l'individualité, la reproduction et l'hérédité ne sont pas établies par cette expérience.
6. **Note éditoriale : 15/20 pour B comme papier spécialisé, après corrections ciblées.** Ce jugement n'est ni une probabilité d'acceptation ni une mesure scientifique. Le potentiel de papier marquant reste modéré, environ 11/20. A : 12/20 comme note technique; C : 9/20 dans l'état vérifiable actuel. Voir les neuf critères séparés dans `FLAGSHIP_DECISION_MATRIX.md`.
7. **Freins à une soumission sérieuse.** Des formulations de B assimilent encore l'échec d'un critère à une falsification de la propriété ou de la mémoire; la portée doit rester celle d'une preuve insuffisante. Il faut rendre centrale la copie passive et le couplage construit au readout, borner l'inférence aux 21 mondes admissibles et aux décodeurs/scopes gelés, raccourcir la chronique historique, mettre à jour la disponibilité des sources désormais distantes, et faire relire les hypothèses statistiques et la nouveauté par un lecteur externe. Pour une synthèse C, il faut en plus récupérer et auditer CCRA01 et les 28 findings. Une validation externe est souhaitable pour une conclusion forte; son absence ne rend pas automatiquement une étude simulée impubliable.
8. **Action unique de Tommy : fournir `Edl recovery 20260904.bundle`**, identifié par SHA-256 `8c43b31d9311fa2cb51bab9fd055c1286eafe0b091d96bcd3ec0e106d934d46f`, branche `recovery/edl-state-20260904`, HEAD annoncé `b391a739`. Aucun Git ni calcul à exécuter par Tommy. Ce fichier est l'entrée la plus susceptible de lever les inconnues restantes; son contenu sera vérifié avant de promettre qu'il contient toutes les pièces.

## Contrôle des douze affirmations de Claude

| # | Affirmation | Résultat indépendant |
|---|---|---|
| 1 | base64/gzip/tar stricts | **UNVERIFIED** pour le paquet absent `EDL_STATE.b64.txt`; extraction sûre vérifiée séparément pour les 45 archives locales retrouvées. |
| 2 | 246 fichiers sans chemin hostile | **UNVERIFIED** pour ce paquet. Notre extraction distincte compte 375 fichiers; ne pas substituer ce nombre à 246. |
| 3 | 246/246 octets identiques | **UNVERIFIED**. Notre preuve couvre notamment 123/123 NPZ contre le registre scellé et le core FDFLT01 contre son archive historiquement hachée. |
| 4 | METHODS_HASH 21571fb4…4d1f99 | **VERIFIED**, formule exacte appliquée aux 17 blobs de méthodes. |
| 5 | 7/7 hashes et connectivité vide | **VERIFIED** dans la récupération historique : sept hashes; JSON de 1 186 octets, `RECORDS={}`, couverture zéro. Vide scientifiquement, pas un fichier de zéro octet. |
| 6 | 12 statistiques OMLDCT03 | **VERIFIED FROM RAW**, 492 comparaisons d'endpoints/terminaisons contre A et B historiques; 12/12 statistiques. Limites d'acquisition et d'intervalle ci-dessous. |
| 7 | gel/agent aveugle CCRA01 | **UNVERIFIED** : aucun contenu de contexte, protocole ou graphe de commits correspondant. |
| 8 | 17/24, p=.894, négatif | **CONDITIONAL ARITHMETIC ONLY**. Les effectifs ne sont pas reconstruits; la phrase d'absence de dominance n'est pas démontrée. |
| 9 | 123 bruts et huit sorties absents | Leur absence dans son conteneur est invérifiable ici. **Les 123 bruts sont retrouvés sur le disque**; des sorties de 18 missions sont inventoriées. « Huit missions » non identifiées précisément. |
| 10 | FDFLT01 invérifiable | **RÉSOLU LOCALement** : endpoint 53/192 reproduit depuis le core. Les 123 TBRT02 ne sont pas les archives nécessaires à FDFLT01. |
| 11 | 12 h→45 paires/.15; 105 h→.80 | **UNVERIFIED** : endpoint, modèle d'effet, rendement, temps et code du calcul absents. 45/12=3,75 paires/h et une extrapolation linéaire donnerait environ 394 paires à 105 h; ce calcul d'unités n'est pas une puissance. |
| 12 | 28 findings acceptés, cinq fatals | **UNVERIFIED**, contenu exact et résolution inconnus. Les cinq inconnues ne sont pas considérées comme corrigées. |

## FDFLT01 : positif réel, portée étroite

La règle historique est un test de probabilité d'un événement opérationnel de deux centres au point B1, contre p≤0,10. Les graines 192+6 reproduisent la formule gelée; les 192 graines utilisées sont uniques. Le freeze `23522612` précède le dépôt des bruts `3f275604`, qui précède l'analyse `a96505ff`. L'endpoint, le second scorer, les graines et le master freeze ont des blobs inchangés entre le freeze et l'historique récupéré. Les 28 fichiers du capsule de méthodes correspondent à leurs empreintes. Cette preuve établit la cohérence de l'enregistrement; elle ne démontre pas l'absence universelle de tout essai non enregistré.

Le calcul indépendant donne 66 mondes avec naissance, 58 passant le maintien temporel, puis 53 passant la réponse locale. Proportion 0,2760417; p exact unilatéral **5,2558964×10⁻¹²**; borne de confiance exacte inférieure unilatérale 95 % **0,223249**; intervalle bilatéral **[0,214117; 0,345024]**. Le seuil gelé était 27 succès. Sensibilités gelées : 55 à 173 pas, 53 à 250, 39 à 402, 21 à 575. La sensibilité longue n'est pas un changement du terminal primaire.

Les scalaires sont enregistrés après le pas; `ycells` et X sont enregistrés avant réaction, après diffusion. La reconstruction ajoute les naissances et soustrait les décès pour comparer les bons états. L'endpoint historique conserve son assemblage de maintien après le pas et réponse X avant réaction. Cette convention doit être explicitée, pas changée après résultat. La réponse utilise des disques pouvant se chevaucher et le rapport faible/fort; elle n'identifie pas une propriété exclusive ni une fille persistante. Le contrôle statistique p₀=0,10 n'est pas un contrôle mécanistique concurrent. B1 est choisi dans une phase de développement antérieure : les nouvelles graines confirment ce point, pas une universalité sur les lois.

Deux défauts documentaires restent visibles : le champ secondaire `FIRST_FAILING_COMPONENT_COUNTS` contient des marges chevauchantes et non une partition; la valeur SHA du capsule dans `FDFLT01_DURABILITY.json` est erronée. Le capsule réel correspond au sidecar et aux 28 empreintes internes. Rien de cela n'est silencieusement réécrit dans le gel. Le comptage de l'identité du « nouveau centre » n'est pas une preuve de généalogie.

## OMLDCT03 : reproductible et inconclusif

Un nouveau classificateur reconstruit les composantes et poursuit l'identité verrouillée depuis les cellules brutes, sans importer A ou B. Il respecte les distances toriques, l'arrêt sur liens ambigus, et l'exposition incluant t_m alors que la durée l'exclut. Aucun désaccord sur 41 paires × 2 bras × 2 classificateurs historiques × 3 quantités.

| Quantité | Durée | Exposition |
|---|---:|---:|
| W+ | 521 | 504 |
| p exact bilatéral | 0,246386336 | 0,347917253 |
| médiane différence des logs | 0,213574100 | 0,569468084 |
| Hodges–Lehmann | 0,333078122 | 0,316135697 |
| intervalle historique | [-0,238539476; 0,836988217] | [-0,310965919; 0,873898988] |

La règle ET échoue. Retirer le parent supprime aussi un concurrent du suivi : SELECTIVE donne 9 terminaisons sans composante et 32 splits/ties; SHAM donne 28 splits/ties, 6 sorties de portée et 7 merges. Ces événements ne se réduisent pas à une mesure biologique de survie. Le diagnostic « 99,6 % des pas » de Claude n'est pas reproduit ici, faute du code et de la convention de risque CCRA01; les 7 contre 0 merges, eux, le sont.

Le coût équivalent à deux bras `prefix/H + 2×(H−prefix)/H` pour les graines déclenchées franchit 512 à l'indice **760 avec 36 paires**. Il confirme le recompte de l'auteur, et non le 789/38 du checker historique. Le coût enregistré de TBRT02 concerne trois bras et franchit 512 à l'indice 738 : ce n'est pas la même quantité. Les 41 paires ne respectent pas l'acquisition gelée d'OMLDCT02. Employer **procédure statistique gelée sur données acquises hors de sa règle d'acquisition**, pas « expérience confirmatoire valide ».

**Défaut indépendant supplémentaire : indice de l'intervalle.** La fonction gelée prend l'indice dont la CDF dépasse α/2, puis l'utilise comme indice de Walsh à base zéro. Sous le modèle idéal continu symétrique sans égalités, la couverture obtenue est **0,9487658**, et non au moins 0,95. L'indice conservateur voisin donne 0,9503413; intervalles descriptifs corrigés : durée **[-0,243158602; 0,837765822]**, exposition **[-0,318323912; 0,874949023]**. Les fichiers gelés et le terminal ne sont pas changés. La vérification de cette combinatoire ne valide pas, à elle seule, la symétrie des différences dans les données.

## Candidat B : conclusion soutenue et limites

Les 50 JSON bruts sont vérifiés contre le manifeste. Le seal SHA-256 `cdf7277a…8757fd` est confirmé; le commit d'autorisation `c158bc0b` est le parent direct du résultat `9cb996bb`. Les sources sont épinglées à `06fd9524` dans `candidate_b`, avec 191 fichiers vérifiés. Le programme historique 03M est rejoué en tant que tel, avec un simple adaptateur d'entrée vers les octets vérifiés. En complément, une nouvelle implémentation calcule les contrastes causaux et les prédictions ridge par moindres carrés augmentés, avec séparation stricte des mondes d'entraînement/test. Écart maximal sur les quantités comparées : **1,17×10⁻¹⁵**.

Sur 21 mondes valides : skill locale moyenne **0,395446**, intervalle t **[0,175323; 0,615569]**; effet causal propre **0,164845 [0,144322; 0,185368]**. L'avantage L sur E est **0,207168 [-0,022063; 0,436399]**, sur B **0,144610 [-0,022605; 0,311825]**. Le vecteur de gates et Outcome B reproduisent. La permutation p=0,000999 est obtenue par 03M historique, pas par une nouvelle troisième implémentation. Les 21 mondes sont l'unité d'inférence, pas les 63 cibles, les feuilles numériques ou les 1 000 permutations.

La sélection de 21/50 mondes et les scopes finis bornent la population cible. Les scores de validation croisée partagent des ensembles d'entraînement; leur intervalle t sur folds doit rester présenté comme la procédure gelée, sans promesse supplémentaire de couverture universelle. La conjonction d'exclusions n'autorise pas à transformer ses faux négatifs possibles en absence de propriété. Le résultat positif causal est utile, mais le couplage mémoire→feeding et la transmission passive sont construits dans le modèle. La nouveauté doit porter sur le test et ses limites, pas sur la découverte que des champs construits peuvent persister.

## Décision

**WRITE B, HOLD la synthèse C, conserver A comme compagnon; aucun nouveau calcul de mondes.** Le paquet manquant est la prochaine action à forte valeur informative. Aucune expérience additionnelle n'est suffisamment motivée pour demander un budget ou rédiger un faux freeze prospectif. Aucun nouveau manuscrit anglais n'est produit : la condition de papier phare effectivement vérifié n'est pas satisfaite. Le plan de renforcement est concret et borné dans `PAPER_STRENGTHENING_PLAN.md`.

Les assertions récentes sur CCRA01, sa puissance et ses reviewers restent ouvertes. Les travaux établis ne sont pas annulés par ces inconnues; ils ne doivent pas être fusionnés en une preuve unique portant sur des architectures et des populations différentes.
