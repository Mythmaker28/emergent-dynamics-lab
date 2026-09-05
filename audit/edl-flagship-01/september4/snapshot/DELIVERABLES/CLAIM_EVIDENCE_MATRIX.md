# Matrice revendication → preuve — EDL, 2026-09-04, **v2**

Après revue contradictoire indépendante : 28 findings, **28 acceptés, 0 rejeté**.
Retour verbatim `REVIEW01/out/REVIEW01_CHECKER_RETURN_VERBATIM.md`,
`sha256 f1d5b1b0…4084a1`, **commité avant traitement** (`4a632d9`).

Quatre niveaux, un seul compte :

- **VÉRIFIÉ** — recalculé ou re-haché dans cette session, **à partir des artefacts récupérés**.
- **DÉRIVÉ** — calculé par moi dans cette session, mais à partir d'hypothèses ou de méthodes qui ne sont dans aucun artefact (projections, simulations).
- **CITÉ** — lu dans un artefact récupéré dont l'intégrité est vérifiée, non recalculé (les brutes manquent).
- **DÉCLARÉ** — connu par le ledger ou une note, **sans artefact** dans cette récupération.

Aucun superlatif n'est employé sans avoir cherché son contre-exemple.

---

## A. Récupération et intégrité

| # | Revendication | Niveau | Preuve | Portée / limite |
|---|---|---|---|---|
| A1 | La charge décode et l'archive est valide | **VÉRIFIÉ** | base64 strict ; `sha256(b64)=928b8969…c0d3ed` ; `sha256(tar.gz)=d1eb8ba1…7ba1bd` ; CRC gzip ; 274 membres | ne dit rien du contenu |
| A2 | Aucun chemin hostile | **VÉRIFIÉ** | 0 absolu, 0 `..`, 0 lien, 0 fichier spécial, 0 collision (casse comprise) | — |
| A3 | Extraction fidèle octet à octet | **VÉRIFIÉ** | `sha256` par fichier avant/après : **246/246** | — |
| A4 | `METHODS_HASH` intact | **VÉRIFIÉ** | formule gelée **appelée**, non réimplémentée : `21571fb4…4d1f99`, 17 fichiers, 17/17 | atteste les octets des méthodes, **pas** l'histoire git |
| A5 | Empreintes publiées | **VÉRIFIÉ (octets)** | `TBRT02/out/SHA256SUMS` : **7/7** | **une empreinte n'atteste pas le contenu** — voir A8 |
| A6 | Verbatims de checker | **VÉRIFIÉ (partiel)** | 6 présents ; `CLOSE01 = 1543a8c9…135e` ; 4/6 confrontés à une empreinte déclarée, toutes concordantes | RPP97 et TBRT02-C4bis : empreinte **calculée, non confrontée** |
| A7 | Cette récupération porte la provenance git | **FAUX — refusé explicitement** | commit `fe6b631` sans parent ; aucun objet de `99b8044a…`, `5372fd8`, `77cc3c70…` | à greffer par le propriétaire |
| A8 | `TBRT02_CONNECTIVITY_EXPOSURE.json` permet de re-tester l'hypothèse de connexité | **FAUX — refusé explicitement** | `RECORDS = {}`, `N_ADMISSIBLE_TRIPLES_COVERED = 0`, généré 2026-08-27T03:20:33, **avant le premier triplet admissible** | empreinte juste, contenu vide. L'hypothèse **ne peut pas** être re-testée sans les brutes |
| A9 | « 123 archives vérifiées » | **CITÉ, au passé seulement** | vérifiées **au scellement** ; `GATE01/out/OMLDCT03_INTEGRITY.json` (2026-08-30T06:33) : `sha256_mismatch 0`, **`missing 123`**, `INTEGRITY_GATE_PASSES = false` | la porte échoue **parce que les archives sont absentes du conteneur**, non par divergence d'empreinte |

## B. OMLDCT03 — le test gelé

| # | Revendication | Niveau | Preuve | Portée / limite |
|---|---|---|---|---|
| B1 | 41/41 paires admissibles | **CITÉ** | `OMLDCT03_ADMISSIBILITY.json` ; accord A/B sur 82 bras ; checker : réimplémentation *from scratch*, 0 écart | recalcul impossible sans les brutes |
| B2 | Les 12 statistiques sont exactes | **VÉRIFIÉ** | implémentation indépendante ; concordance au dernier chiffre | **reconstruction, pas réplication** |
| B3 | Effet non détecté | **VÉRIFIÉ** | durée 0,2464 ; exposition 0,3479 ; règle ET non franchie | `INCONCLUSIVE`, ni équivalence ni absence d'effet |
| B4 | Puissance à l'effet observé ≈ 0,14 (règle ET, n = 41) | **DÉRIVÉ** | rééchantillonnage des 41 différences | puissance *a posteriori*, monotone du `p` : **elle n'ajoute rien** au `p`. Sans barre d'erreur elle est trompeuse (voir B7) |
| B5 | Puissance gelée à la conception : 0,402 / 0,971 / 1,000 | **DÉCLARÉ** | `LDFMA01/out/HANDOFF…md` — **absent** ; deux findings acceptés concordants (checker F10, CLOSE01 F7) | ce n'est pas le test qui était sous-puissant par conception, c'est l'hypothèse de puissance qui était fausse |
| B6 | L'accrual gelé n'a pas été honoré | **CITÉ + VÉRIFIÉ (coûts)** | plafond 512 épuisé à l'indice 789 avec **38** paires ; coût 2 bras recoûté **571,649**, soit 0,645932 inst./graine — recalculé par moi | restreint « le test gelé a été exécuté » à « la **procédure** gelée a été exécutée » |
| B7 | « n ≈ 400 pour une puissance de 0,80 » | **DÉRIVÉ, et non identifié** | double bootstrap 100 × 200 : q05 0,02, médiane 0,885, q95 1,00 ; **34 % des vérités compatibles donnent < 0,50** ; l'IC de HL contient zéro | l'effectif requis n'est **pas borné supérieurement** au niveau 95 % |
| B8 | La décision n'était pas aveugle | **VÉRIFIÉ** | `TBRT02_C4_ANALYSIS.json §12`, publié 2 jours avant sur les **mêmes 41 graines** : 24 / 7 / 10, test des signes exact `p = 0,024307`, recalculé | n'enfle pas l'erreur de 1ʳᵉ espèce ; coûte la revendication d'aveuglement |
| B9 | La règle ET achète peu de sévérité | **CITÉ** | `ρ = 0,9751` entre les deux critères, accord de signe 41/41 (checker F8) | « un critère rapporté deux fois » |

## C. La non-échangeabilité de l'endpoint

| # | Revendication | Niveau | Preuve | Portée / limite |
|---|---|---|---|---|
| C1 | MERGE exige ≥ 2 prédécesseurs | **VÉRIFIÉ** | `OMLDCT02/code/omldct02_e3_b.py:107-131, 216-220`, **relu dans cette session** | le canal est inatteignable quand la composante suivie est seule **au pas précédent** |
| C2 | Mélange : SELECTIVE 32/9/0/0, SHAM 28/0/7/6 | **VÉRIFIÉ** | recompté depuis `PER_PAIR` par script indépendant | n = 41 |
| C3 | Le même profil apparaît dans les 33 paires d'OMLDCT02 | **CITÉ** | checker F3 : 29 split / 2 merge / 2 extinction contre 22 / 5 / 6 | **2 MERGE sous SELECTIVE** : le canal y est raréfié, pas supprimé |
| C4 | Le canal est **supprimé** | **FAUX — corrigé** | 99,6 % des pas à risque n'ont qu'une composante, mais 41 pas sur 9 713 en ont ≥ 2, et C3 en compte 2 déclenchements | écrire « supprimé sur les 99,6 % de pas à risque, raréfié ailleurs » |
| C5 | Occupation mono-composante 99,6 % / 6,4 % | **CITÉ** | checker F3 : 9 672/9 713 et 534/8 353 | mesuré sur les brutes, absentes ici |
| C6 | « Extinction de l'identité 9 contre 0, `p = 0,0039` » | **RETIRÉ — la statistique portait sur la chaîne, pas sur l'événement** | checker A9 : **cinq des six** `OUT_OF_RANGE` du bras SHAM sont une fille dont le Y meurt pendant que le monde continue | remplacé par C7 |
| C7 | Mortalité de trajectoire : 11 / 1 / 1 / 28, `p = 0,00634765625` | **VÉRIFIÉ** | `FIMRCC02/out/FIMRCC02_POWER.json`, relu et recalculé | le cadrage « 12 contre 2 » a été **formellement retiré** par le programme et n'est pas ré-émis |
| C8 | `p = 0,246` est un mélange (+0,6325 sur 28 ; −0,3231 sur 13) — **et 0,0433 sur les 32 sans extinction traitée** | **CITÉ (table) ; VÉRIFIÉ (recalcul du checker adverse)** | table de sensibilité, 5 lignes | toute restriction conditionne sur une variable post-traitement → **inadmissible comme estimand**. Donné en entier pour éviter la divulgation asymétrique |
| C9 | Aucune spécification ne renverse la règle ET | **CITÉ** | poolé 74 paires → 0,141 / 0,117 | le verdict est robuste ; **son sens** ne l'est pas |
| C10 | C'est une découverte de cette relève | **FAUX — refusé explicitement** | mortalité différentielle : 3 sources (`GATE01` 02:07:38, `FIMRCC02_POWER` 02:11:47, checker F2). Suppression du canal MERGE : **1 seule**, checker F3 | contribution = assemblage, vérification, corroboration, généralisation, **et CCRA01** |
| C11 | « La seule chose corroborée par deux campagnes » | **FAUX — corrigé** | il y en a **deux** : celle-ci et la dégénérescence CLEA01 (D4) | aucun superlatif sans avoir cherché |

## D. TBRT02 — la campagne

| # | Revendication | Niveau | Preuve | Portée / limite |
|---|---|---|---|---|
| D1 | 885 graines, 53 déclenchées, 41 triplets, `technical_failures = 0` | **CITÉ + VÉRIFIÉ** | `C5 §1` ; recompté par le checker sur les 885 lignes du ledger | « zéro échec technique » ≠ « techniquement irréprochable » : la mission liste **six** erreurs d'opérateur |
| D2 | La mission n'adjuge rien | **CITÉ** | `C5 §2` : « ANSWER: NOTHING » | `MODEL_C_STATUS = NOT_REFUTED AND NOT CORROBORATED` |
| D3 | La borne séquentielle 0,070461 est inadmissible | **CITÉ** | `C4 §8` | **ne pas rapporter comme résultat** |
| D4 | La dégénérescence CLEA01 se reproduit 41/41 sous SELECTIVE | **CITÉ** | `C5 §3a`, `C4 §11` : « CLEA01 closed on exactly this; it was not an artefact of that mission » | **second fait corroboré par deux campagnes** |
| D5 | Le déplacement a fait pire que ne rien faire (17/41 vs 26/41) | **CITÉ** | `C5 §3b` | **post hoc**, non pré-enregistré |
| D6 | Censure à droite différente par bras (8 / 29 / 16) | **CITÉ** | `C5 §3c` | porte sur la durée du set CERTAIN, **pas** sur l'endpoint d'OMLDCT03 |
| D7 | Coûts mesurés : `runtime_s` méd. 85,10 s, moy. 89,38 s, max 627,6 s ; 10,85 h murales à 2 workers pour 885 graines | **VÉRIFIÉ** | 885 lignes de `TBRT02_SEALED_LEDGER_*.jsonl` ; `batch_seconds` 39 065,1 / 38 977,7 | **remplace les « 45 s / 337 s » de la v1, qui ne figurent dans aucun artefact** |
| D8 | Rendement admissible | **VÉRIFIÉ (4,633 %) / DÉCLARÉ (4,10 %)** | 41/885 observé ici ; 33/805 est OMLDCT02, dont `out/` est absent. Postérieur de Jeffreys Beta(41,5 ; 844,5) : q05 3,578 %, méd. 4,650 %, q95 5,906 % | tenir le taux au point estimé est l'erreur qu'EVCS01 a trouvée dans son propre instrument et corrigée |
| D9 | Disjonction des graines OMLDCT02 / TBRT02 | **VÉRIFIÉ (par le checker)** | 1 030 graines régénérées depuis `omldct02_seed_manifest.derive` ; **intersection 0** | corroboré par `TBRT02_MASTER_FREEZE.TBRT01_AND_OMLDCT02_SEEDS_ARE_INSIDE_THE_FORBIDDEN_SET = true` |

## E. CCRA01 — gelée par un spécificateur aveugle, exécutée

| # | Revendication | Niveau | Preuve | Portée / limite |
|---|---|---|---|---|
| E1 | Le spécificateur n'a vu aucune valeur d'issue | **VÉRIFIÉ (procédure)** | six fichiers autorisés seulement ; préregistration portant son propre inventaire de contamination | garantie procédurale, pas cryptographique |
| E2 | Le gel précède l'exécution | **VÉRIFIÉ** | commit `c363afd` ; `CCRA01_PREREGISTRATION.md` `2cae5619…dad39`, `ccra01_frozen.py` `df1d4d6e…273b3` ; `--run` exécuté après | **écart déclaré** : le gel aurait dû être commité seul, `c363afd` porte aussi l'adjudication |
| E3 | Test de capacité 5/5 PASS | **VÉRIFIÉ** | `CCRA01_CAPABILITY.json` ; C4 recoupe la queue exacte contre l'énumération des 2^m séquences, m = 0..14, 0 divergence | legs primaire de TBRT02 honoré |
| E4 | L'artefact évité est mesuré | **VÉRIFIÉ** | C5 : renommage `OUT_OF_RANGE → NO_COMPONENT…` dans le seul bras traité ; statistique naïve déplacée de **8 paires**, statistique gelée identique bit à bit | mesuré, pas supposé |
| E5 | 17 pire / 24 meilleur / 0 égalité ; `p` unilatéral = 0,8944882011955997 ; `theta_hat = −0,17073170731707318` | **VÉRIFIÉ** | recalculé par un second chemin, concordance exacte sur les quatre grandeurs | — |
| E6 | `TERMINAL = NEGATIF`, seuil non franchi à résolution suffisante | **VÉRIFIÉ** | `k` critique 28, `DESIGN_COULD_HAVE_REJECTED = true` | `NEGATIVE_BUT_VALID` : un critère gelé exécuté et non franchi |
| E7 | Le confondant de mortalité domine le composite | **FAUX — non soutenu** | 11 paires décidées par le rang, 30 par le départage sur la durée | la direction pré-déclarée n'est pas soutenue |
| E8 | SELECTIVE est meilleur | **NON REVENDIQUÉ** | test **unilatéral** ; `theta_hat` négatif n'autorise aucune conclusion inverse | aucune équivalence, aucune absence d'effet |

## F. Lignes retirées

| # | Mission | Statut | Ce qui tient |
|---|---|---|---|
| F1 | CLOSE01 | `WITHDRAWN_AS_WRITTEN` (22/22 acceptés) | §0 et §7 ; les chiffres copiés ; deux hachages ; la réserve sur l'accrual ; **et son F17 : quatre routes concrètes, dont trois sur des données existantes** |
| F2 | FIMRCC02 | `WITHDRAWN` — un test pré-enregistré existait déjà | **son analyse de puissance** : `NON_INTERPRETABLES__CONFONDUS_PAR_LA_MORTALITE_DIFFERENTIELLE` (chaîne française d'origine), écrite avant tout gel, aucune archive ouverte ; et sa table 11/1/1/28 |
| F3 | RPP97 | `WITHDRAWN…SCIENCE_MIS_SPECIFIED` | **rien d'utilisable.** Pré-enregistrement détruit après lecture des premiers chiffres ; fenêtres antérieures au fork ; `S1` indéfini sur 99,56 % des pas. **La question Reynolds/Ponce-Dawson/Pearson n'est pas fermée pour autant** : `C5 §6[1]` et CLOSE01 F17 route 2 l'inscrivent au legs |
| F4 | RPP98 | `WITHDRAWN` — événement compté ≠ événement revendiqué | le descriptif d'intégrité des séries |

## G. Déclarés seulement

| # | Revendication | Niveau | Pourquoi |
|---|---|---|---|
| G1 | FDOT01 : 7/160, e-value ≈ 5,2 | **DÉCLARÉ** | `FDOT01/out` absent |
| G2 | FDFLT01 : 53/192, `p = 5,26 × 10⁻¹²`, `E = 1,22 × 10¹⁰` | **DÉCLARÉ** | `FDFLT01/out` absent — **jambe positive de la thèse phare** |
| G3 | FMRCT01 : `K = 0/372` | **DÉCLARÉ** | `FMRCT01/out` absent |
| G4 | OMLDCT02 : 33 paires | **DÉCLARÉ** ; le **805** est **CITÉ** | `OMLDCT02/out` absent ; « 805-seed ledger » figure dans `TBRT02_MASTER_FREEZE.HOW_THE_CEILING_WAS_SIZED` |
| G5 | OBTC02 : r80 7,071 vs 7,036 | **DÉCLARÉ** | `OBTC02/out` absent |

## H. Non audités dans cette session, alors qu'ils sont présents

**Dix** répertoires portent un `out/`, pas sept. Trois n'ont pas été audités :
`MCTT01/out/MCTT01_SELECTED_LAW.json` — **il fixe `LAW_C_MCTT01`, la loi dont tous
ces résultats dépendent** —, `PQEC01/out/PQEC01_MASTER_FREEZE.json`,
`BPRTC01/out/BPRTC01_MASTER_FREEZE.json`.

## I. Hors de portée — aucun jugement porté

PR #34 · `paper/persistence-without-ownership-v1` · branche
`codex/one-matched-locked-daughter-control-test-02` @ `99b8044a`.
GitHub 403, pas de pont. **Non déclarées perdues.**

## J. Statuts — les seize, ré-émis à l'identique

`H3_STATUS = NOT_TESTED` · `REPRODUCTION_STATUS = NOT_TESTED` ·
`HEREDITY_STATUS = NOT_TESTED` · `AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED` ·
`X_LAWSPEC_BASELINE = UNCHANGED` · `ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED` ·
`COMPANION_PAPER_V1_1_STATUS = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED` ·
`OMLDCT02_STATUS = INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED` ·
`CLEA01_STATUS = CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED` ·
`TBRT02_STATUS = CLOSED__RAW_COMPLETE__PRIMARY_ADJUDICATION_INCONCLUSIVE_BY_CONSTRUCTION` ·
`FIMRCC01_E3_E4_E5_STATUS = FUTURE_QUESTION_RECORDED__NOT_AUTHORISED` ·
`OBFOR01_HISTORICAL_WINDOW_STATUS = NOT_PORTABLE` ·
`RPP97_STATUS = WITHDRAWN_AS_A_DESCRIPTION__ARITHMETIC_SOUND__SCIENCE_MIS_SPECIFIED` ·
`RPP98_STATUS = WITHDRAWN__THE_QUESTION_WAS_ALREADY_ANSWERED_BY_TLMR01__AND_THE_COUNTED_EVENT_IS_NOT_THE_CLAIMED_EVENT` ·
`FIMRCC02_STATUS = WITHDRAWN__A_PREREGISTERED_TEST_ALREADY_EXISTS__AND_THE_CENTRAL_PREMISE_IS_FALSE_BY_DEFINITION` ·
`OMLDCT03_STATUS = FROZEN_STATISTICAL_PROCEDURE_EXECUTED_AT_ITS_REQUIRED_N_ON_A_MATCHED_SAMPLE_OBTAINED_OUTSIDE_ITS_ACCRUAL_RULE__EFFECT_NOT_DETECTED__INCONCLUSIVE`

Nouveau :
`CCRA01_STATUS = FROZEN_BY_A_BLIND_SPECIFIER__CAPABILITY_TESTED__EXECUTED__NEGATIF__THRESHOLD_NOT_CROSSED_AT_ADEQUATE_RESOLUTION`
