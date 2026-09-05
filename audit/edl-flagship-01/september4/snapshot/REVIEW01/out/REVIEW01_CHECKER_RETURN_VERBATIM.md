# RAPPORT DE CHECKER ADVERSAIRE — EDL, livrables du 2026-09-04

## VERDICT GLOBAL

L'arithmétique statistique est juste (j'ai reproduit les 12 grandeurs gelées, la table de sensibilité complète et les coûts d'accrual au dernier chiffre par mon propre code), mais les trois documents portent **quatre défauts fatals** — deux scripts déclarés « dans le bundle » qui n'y sont pas, un chiffre de McNemar qui n'existe que par le vocabulaire des chaînes, une phrase de disponibilité de données démentie par le fichier qu'elle invoque, et une table de dimensionnement fausse d'un facteur 2 — plus une conclusion « aucune expérience justifiée » qui ignore trois routes que l'adjudication acceptée du programme nomme déjà.

---

## FINDINGS

### F1 — FATALE — Les deux scripts de vérification ne sont **pas** dans le bundle, ni dans le commit

**Constat.** Le commit `fe6b6311a38a90dfe1be43a0b0ed71ed87fdf051` contient **251 fichiers** ; `git ls-tree -r --name-only HEAD | grep -i recovery` rend `RECOVERY/MANIFEST.json`, `RECOVERY_HASHES.json`, `RECOVERY_REPORT_20260904.md`, `SHA256SUMS_FULL_TREE` — **et rien d'autre sous `RECOVERY/`**. `git status --porcelain` rend `?? RECOVERY/scripts/`. Le bundle ne porte qu'une seule ref (`fe6b6311… refs/heads/recovery/edl-state-20260904`), donc il ne porte pas ces scripts. Horodatages : commit `2026-09-04T22:28:01`, bundle 22:28, `edl_verify_recovery.py` **22:29:26**, `edl_omldct03_independent.py` **22:29:59**. Écrits *après* le commit et *après* le bundle. `SHA256SUMS_FULL_TREE` (249 lignes) ne les liste pas ; `MANIFEST.json` déclare `N_FILES = 250` et un `TOP_LEVEL.RECOVERY = 4` — le manifeste de l'auteur contredit déjà la table de livraison de l'auteur.

**Citations fautives.**
- Rapport §5 : « | Scripts de reconstruction | `RECOVERY/scripts/edl_verify_recovery.py`, `edl_omldct03_independent.py` | **dans le bundle**, exécutés, `ALL_CHECKS_PASS` | »
- Rapport §1.5 : « dépôt local **propre** … portant un manifeste, les 246 empreintes avant/après, l'empreinte de chaque fichier de l'arbre, le rapport de récupération et **deux scripts de vérification** »
- Rapport §3.3 : « | Reproductibilité | … | **9/10** — 2 scripts autonomes, bibliothèque standard, `ALL_CHECKS_PASS` et 12/12 statistiques | »
- MS §9 : « Verification and recomputation scripts (`edl_verify_recovery.py`, `edl_omldct03_independent.py`; standard library only) **ship with the recovery bundle** »

**Correction.** Committer les deux scripts, refaire le bundle, republier son sha256 — ou retirer les quatre phrases. Le dépôt n'est pas « propre » (`?? RECOVERY/scripts/`). Tant que ce n'est pas fait, la note de reproductibilité est **0/10, pas 9/10** : c'est exactement le legs OPERATIONAL de TBRT02 C5 (« durability is not a commit ») et la cause de mort de TBRT01, répétés.

---

### F2 — FATALE — Le McNemar « 9 contre 0, p = 0,0039 » n'existe que par la chaîne de caractères

**Constat.** J'ai recompté depuis `PER_PAIR` : SELECTIVE `NO_COMPONENT_AT_THE_NEXT_STEP` sur les indices {85, 124, 321, 507, 530, 573, 595, 636, 768} ; SHAM `OUT_OF_RANGE` sur {231, 573, 593, 768, 793, 866}. Or **le retour de checker que vous citez comme source** (`OMLDCT03_CHECKER_RETURN_VERBATIM.md`, A9) écrit : « **Five** (231, 573, 593, 768, 793) are a one-cell daughter whose Y died while the world lived on… the string "OUT_OF_RANGE" **actively hides that five of the six are the daughter dying** ». Sous cette cartographie — que le checker a ouverte cas par cas — l'événement « le Y de la fille est mort » vaut **9 en SELECTIVE et 5 en SHAM**, discordance **7 contre 3**, McNemar exact **p = 0,34375** (recalculé). Le 9-contre-0 mesure la chaîne, pas l'événement. Et l'événement bien défini existe déjà, publié : `FIMRCC02_POWER.json` donne 11 extinctions / 1 sauvetage, **p = 0,00634765625** (je reproduis exactement).

**Citations fautives.**
- MS §3.1 : « The identity is terminated by total local extinction in **9 of 41** treated arms and **0 of 41** controls (exact McNemar, 9 versus 0 discordant, *p* = 0.0039) »
- Rapport §2.2 : « 9/41 bras SELECTIVE terminent l'intervalle par extinction totale de Y dans la fenêtre de la fille, **0/41** en SHAM »
- Matrice C5 : « Extinction de l'identité 9/41 contre 0/41 | **VÉRIFIÉ** | recompté ; McNemar exact `p = 0,0039` »

**Correction.** Supprimer le p entièrement. Écrire : « le Y de la fille meurt dans 9 des 41 bras traités et 5 des 41 témoins (7 contre 3 discordants) ; le monde meurt dans 12 contre 2 (11 contre 1, p = 0,0063, `FIMRCC02_POWER.json`) ; les six `OUT_OF_RANGE` témoins comprennent cinq morts de la fille, cf. checker A9. » Répondant à votre question 6.2 : oui, **le donner est déjà une faute**, mais pas pour la raison que vous croyez. Ce n'est pas l'exposition inégale qui tue le chiffre, c'est que la partition des chaînes n'est pas la partition des événements. Un « p sans taux d'erreur revendiqué » n'est pas une quantité ; ici il est en plus calculé sur le mauvais événement, et l'auteur avait dans son propre dossier les deux versions correctes.

---

### F3 — FATALE — « The programme has recorded per-step connectivity exposure » : le fichier est vide

**Constat.** `TBRT02/out/TBRT02_CONNECTIVITY_EXPOSURE.json`, 1 186 octets, généré `2026-08-27T03:20:33` (soit **la veille** de la fin de campagne, 2026-08-28T04:28) : `"RECORDS": {}` et `"N_ADMISSIBLE_TRIPLES_COVERED": 0`. Rien n'a été enregistré. Ce fichier est l'une des **7 entrées de `TBRT02/out/SHA256SUMS`** que le rapport déclare « **VÉRIFIÉ 7/7** » : il a été haché et jamais ouvert.

**Citation fautive.** MS §8 : « The programme **has recorded** per-step connectivity exposure so that this assumption can be re-tested later without re-spending a campaign. »

**Correction.** Remplacer par : « The programme declared an intent to record per-step connectivity exposure (`TBRT02_CONNECTIVITY_EXPOSURE.json`), but the file was generated before any admissible triple existed and carries zero records; the assumption **cannot** be re-tested without re-reading the raw archives. » Et corriger le rapport §1.2, qui compte 7/7 comme une vérification de contenu alors que c'est une vérification d'octets.

---

### F4 — FATALE — Le dimensionnement du §4 est faux d'un facteur ≈ 2 ; « 45 s méd. » et « 337 s max » ne sont dans aucun artefact

**Constat.** J'ai relu les 885 lignes de `TBRT02/work/TBRT02_SEALED_LEDGER_{0,1}.jsonl`. `runtime_s` : **médiane 85,1 s**, moyenne 89,38 s, **max 627,6 s**, somme 79 102 s. `TBRT02_RUN_STATE.json.0/1` : `batch_seconds` 39 065,1 et 38 977,7 — soit **≈ 10,9 h de temps mural à 2 workers pour 885 graines**. Aucune occurrence de 45 ni de 337 dans l'arbre. Conséquences, toutes recalculées :

| | rapport | mesuré |
|---|---:|---:|
| n = 41 (885–1000 graines) | 6,2 h | **11,0 h** (valeur observée de la campagne elle-même) |
| n = 400 (9 757 graines) | 61,0 h | **121,1 h** |
| « au pire » n = 400 | 456,7 h | **125,5 h** (borne 99,9 % par TCL ; σ du total = 2,7 h) |
| 12 h à 2 workers | 1 920 graines → 79 paires → puissance 0,20 | **≈ 967 graines → 45 paires → puissance 0,16** |

Trois erreurs distinctes : (a) la médiane employée est fausse d'un facteur 1,9 ; (b) on projette une **somme** avec une **médiane**, ce qui n'est pas défini ; (c) la colonne « au pire » multiplie 9 757 par le maximum, ce qui n'est pas un pire cas mais un événement de probabilité ~0 — le vrai écart-type du total est de ±2 %, pas d'un facteur 7,5. Enfin la première ligne du tableau (6,2 h à n = 41) est démentie par la campagne que le rapport décrit lui-même deux pages plus haut.

**Citations fautives.**
- Rapport §4 : « | heures @ 2 workers, **45 s méd.** | **@ 337 s max** | » et la ligne « | **400** | **≈ 0,80** | **9 757** | **6 302** | **61,0** | **456,7** | »
- Rapport §4 : « **12 h à 2 workers ≈ 1 920 graines ≈ 79 paires ≈ puissance 0,20.** Il manque un facteur 5 en temps médian, et jusqu'à **38** au pire. »

**Correction.** Refaire la colonne temps sur `mean(runtime_s) = 89,38 s` et publier la source (`TBRT02_SEALED_LEDGER_*.jsonl`, 885 lignes). Écrire « il manque un facteur ≈ 10 en temps mural (121 h contre 12 h) », supprimer la colonne « au pire » ou la remplacer par une borne à 99,9 % (125,5 h). La conclusion d'abstention **se renforce**, mais aucun de ces chiffres n'est publiable tel quel. Réponse à votre question 6.4 : 571,649/885 = 0,645932 et 0,688720 à 3 bras **tiennent, je les reproduis exactement** ; c'est le « 45 s » qui est inventé et il n'est compatible ni avec le ledger ni avec `batch_seconds`.

---

### F5 — FATALE — « Aucune expérience n'est justifiée » est sur-déterminée : l'adjudication acceptée du programme nomme quatre routes, vous en examinez une

**Constat.** `CLOSE01/out/CLOSE01_CHECKER_ADJUDICATION.json`, finding **F17, verdict ACCEPTED, gravité PORTANTE**, champ `les_quatre_pistes_tues` :

```
0 : pre-enregistrer en CODE la condition au niveau du corps … sur les 41 triplets
1 : la comparaison au mecanisme de deplation du coeur (Reynolds, Ponce-Dawson, Pearson 1997),
    mesurable sur les series par pas deja archivees
2 : le cadre des RISQUES CONCURRENTS pour la mortalite differentielle :
    analyse cause-specifique ou composite ordonne
3 : E3/E4/E5 de FIMRCC01, toujours FUTURE_QUESTION_RECORDED__NOT_AUTHORISED
```

et F17 : « le legs tait les quatre choses concrètes que le registre nomme … **dont trois sur des données qui existent déjà** ». Le rapport ne discute que la route 0. La **route 2 ne coûte ni un monde ni une archive brute** : un estimand de risques concurrents / composite ordonné sur les 41 paires se spécifie à partir de `PER_PAIR` (durées, expositions, type de terminaison) et de `FIMRCC02_POWER.json` (les 13 indices d'extinction) — les deux sont dans cette récupération, je viens de les utiliser. C'est exactement ce que le manuscrit prescrit en §6.2 comme réparation générale, et exactement ce que le checker range en « Suspected, not verified » (« That the observed positive point estimate would survive a properly specified competing-risks analysis »). Aucune des quatre « raisons indépendantes » du §4 ne l'écarte : la raison 1 (pas d'exécuteur durable) ne s'applique pas à une ré-analyse de `PER_PAIR` que vous avez déjà faite deux fois ce soir ; la raison 2 (budget) ne s'applique pas ; la raison 3 est *l'argument pour* faire cette analyse, pas contre.

**Citations fautives.**
- Rapport §4 : « **Non.** `EXPERIMENT_NOT_JUSTIFIED`, pour quatre raisons indépendantes, dont chacune suffirait. »
- Rapport §4.4 : « L'expérience qui serait vraiment décisive ne coûte aucun monde — et elle est bloquée par les données… **Elle exige les 123 archives brutes (~440 Mo)** »
- Rapport §2.2 RPP97 : « La piste « mécanisme de déplétion du cœur (Reynolds, Ponce-Dawson, Pearson 1997) » est, en l'état, **fermée**. » — contredit par `TBRT02_C5_CLOSURE.json §6[1]`, qui l'inscrit au legs comme faisable sur les séries déjà archivées, et par CLOSE01 F17 route 1.

**Correction.** Réponse à votre question 6.5 : **oui, vous écartez trop vite.** Remplacer la conclusion par : « aucune expérience *coûtant des mondes* n'est justifiée ; une analyse de risques concurrents pré-spécifiée sur les 41 paires existantes est justifiée, ne coûte rien, ne demande pas les brutes, et est la route 2 de CLOSE01 F17 ». Et retirer « fermée » sur RPP97, ou l'appuyer sur un artefact.

---

### F6 — PORTANTE — « la seule chose corroborée par deux campagnes indépendantes » est fausse par votre propre matrice

**Constat.** Votre matrice D4 écrit : « La dégénérescence de CLEA01 se reproduit 41/41 sous SELECTIVE | **CITÉ** | `C5 §3a`, `C4 §11` ». Et `TBRT02_C5_CLOSURE.json §3a` dit : « SELECTIVE reproduces CLEA01's degeneracy without exception: in 41 of 41 worlds… **CLEA01 closed on exactly this; it was not an artefact of that mission.** » C'est un second fait corroboré par deux campagnes, présent dans l'état récupéré, listé par vous. De plus, c'est le genre d'erreur **exact** pour lequel CLOSE01 a été retirée : `LE_CONSTAT_SUR_MOI` = « **Affirmer une unicité sans avoir cherché.** » (F1, gravité FATALE, ACCEPTED).

**Citations fautives.**
- Rapport §2.3 : « **C'est la seule chose de cet état qui soit corroborée par deux campagnes indépendantes.** »
- Matrice C3 : « **seule revendication de cette relève corroborée par deux campagnes** »

**Correction.** Remplacer « la seule » par « l'une des deux, avec la dégénérescence CLEA01 (D4) », ou supprimer le quantificateur. Aucun superlatif ne doit sortir d'un état récupéré à 18 missions sur 40.

---

### F7 — PORTANTE — Le profil des 33 paires d'OMLDCT02 **contredit** la thèse centrale au lieu de la corroborer

**Constat.** J'ai vérifié la mécanique de la fusion dans un fichier **présent dans la récupération**, `OMLDCT02/code/omldct02_e3_b.py:107-131` et `:216-219` : MERGE ne se déclenche que si `rc[cur]==1` et `cc[j]>1`, c'est-à-dire s'il existe **au moins deux prédécesseurs** dans le rayon. Avec une seule composante au pas précédent, `cc[j] ≤ 1` : la fusion est bien arithmétiquement impossible. Mais votre propre chiffre d'occupation dit **99,6 %**, donc sur **41 des 9 713 pas** du bras traité il y avait ≥ 2 composantes et le canal était disponible. Et surtout, la campagne que vous invoquez comme corroboration montre **2 MERGE sous SELECTIVE sur 33 paires** : le canal n'y est pas supprimé, il y est raréfié (2 contre 5). Votre « corroboration indépendante » réfute donc précisément la phrase la plus forte du manuscrit.

**Citations fautives.**
- MS §2 : « Channel (b) is therefore not made *rarer* by the treatment — it is made **unavailable**. »
- MS §3.3 / abstract : « Two campaigns … show **the same structural signature**. »

**Correction.** Écrire : « the channel is arithmetically unavailable on the 99.6 % of at-risk steps where the daughter is the world's only component, and rare elsewhere; in the 33-pair campaign it fired twice under treatment (2 vs 5), so the effect is a strong suppression, not a deletion ». Et corriger le titre, qui promet « deletes ». Réponse à votre question 6.3 : la **disjonction des graines tient** — je l'ai vérifiée moi-même en régénérant les 1 030 graines d'OMLDCT02 depuis `omldct02_seed_manifest.derive` (intersection **0** avec les 885 graines consommées par TBRT02, cf. « CE QUI TIENT ») — mais « indépendantes » s'arrête là : même loi (bits IEEE identiques), même moteur, mêmes classifieurs gelés, même analyste. Et la corroboration, sur le canal qui compte, est **discordante**.

---

### F8 — PORTANTE — La puissance projetée : la méthode est licite, la conclusion « n ≈ 400 » n'a aucune précision, et la puissance gelée du programme est tue

**Constat.** J'ai réimplémenté le rééchantillonnage (20 000 tirages appariés, α = 0,05 bilatéral, règle ET avec concordance des médianes) : **durée 0,213, exposition 0,156, ET 0,147** à n = 41 ; 0,308 à 100 ; 0,545 à 200 ; 0,722 à 300 ; **0,831 à 400** ; 0,809 à 370. Vos 0,22 / 0,17 / 0,16 et 0,158 / 0,317 / 0,551 / 0,727 / ≈0,80 se reproduisent. Le problème n'est donc pas l'arithmétique, c'est ce qui manque :

1. **Aucune incertitude.** J'ai fait un double bootstrap (150 « vérités » rééchantillonnées, 200 tirages internes) : la puissance à n = 400 va de **0,000 à 1,000**, q05 = 0,042, médiane 0,913 ; **33 % des vérités compatibles avec vos données donnent une puissance < 0,50 à n = 400**, 20 % donnent < 0,20. L'IC de Hodges-Lehmann sur la durée est (−0,239 ; +0,837) et contient zéro : au niveau 95 %, **l'effectif requis pour 0,80 n'est pas borné supérieurement**. « n ≈ 400 pour 0,80 » est un point sans barre.
2. **C'est de la puissance observée.** À effet estimé sur l'échantillon, la puissance est une fonction monotone du p (Hoenig & Heisey) : dire « le test a été exécuté à une puissance de 0,16 » est une reformulation de « p = 0,246 », pas une information nouvelle.
3. **La puissance gelée n'est jamais confrontée.** Deux findings acceptés le réclament : checker OMLDCT03 F10 (« `LDFMA01/out/HANDOFF…md` publishes it at n = 41 (0.402 at the Wilson lower bound, 0.971 at the point estimate, 1.000 at the upper) ») et CLOSE01 F7 (ACCEPTED, PORTANTE, même chiffre). Vos trois documents ne le mentionnent nulle part. Le terminal se termine par `INCONCLUSIVE_UNDER_FROZEN_POWER` et vous ne dites pas ce qu'était cette puissance gelée.

**Citations fautives.**
- Matrice B4 : « Le test a été exécuté à une puissance où il ne pouvait presque pas conclure | **VÉRIFIÉ** | rééchantillonnage des 41 différences : 0,22 / 0,17 / **0,16** »
- MS §5 : « reaches 0.80 near **n ≈ 400** »

**Correction.** Reclasser B4 en **DÉRIVÉ** (votre propre définition de VÉRIFIÉ est « recalculé ou re-haché dans cette session, **à partir des artefacts récupérés** » ; aucun artefact ne contient 0,16). Écrire : « puissance au *seul* effet observé : 0,15 [0,00 ; 1,00] à n = 400 par double bootstrap ; l'effectif pour 0,80 n'est pas identifié, l'IC de l'effet contenant zéro. La puissance gelée à la conception valait 0,402 / 0,971 / 1,000 (LDFMA01) : ce n'est pas le test qui était sous-puissant par conception, c'est l'hypothèse de puissance de la conception qui était fausse. »

---

### F9 — PORTANTE — La contamination (checker F7 / CLOSE01 F5) est absente des trois documents, et elle est vérifiable ici

**Constat.** `TBRT02/out/TBRT02_C4_ANALYSIS.json`, section `12_EXPLORATORY_PAIRED_CONTRASTS`, présente dans la récupération : `SELECTIVE_minus_SHAM_CERTAIN_duration : n 41, median 7700, n_positive 24, n_zero 7, n_negative 10`. Test des signes exact sur 24 contre 10 : **p = 0,024307** (je l'ai calculé). Publié le 2026-08-28, sur **ces mêmes 41 graines**, deux jours avant OMLDCT03. Le checker en fait son F7 (« It does not inflate the type-I error … What it costs is **the claim of blindness** ») ; CLOSE01 le reprend en F5, ACCEPTED. Vos trois documents n'en disent pas un mot, et le rapport §2.2 écrit au contraire :

**Citation fautive.** Rapport §2.2 : « **Prospectif / post hoc** : la **procédure statistique** est prospective et a été exécutée sans modification. »

**Correction.** Ajouter une ligne à la grille OMLDCT03 : « Contamination : la direction d'un contraste apparié corrélé sur ces mêmes 41 graines était publiée deux jours avant (`TBRT02_C4_ANALYSIS.json §12`, 24/10, p = 0,0243, recalculé). La procédure était prospective ; la décision de l'exécuter ne l'était pas. » C'est la troisième mission de suite qui omet ce constat.

---

### F10 — PORTANTE — « 12/41 contre 2/41 » est un cadrage causal formellement retiré

**Constat.** `CLOSE01_CHECKER_ADJUDICATION.json`, F15, ACCEPTED : « j'ai repris le cadrage causal « le retrait éteint dans **12 contre 2** » que ma propre adjudication avait **retiré** : le contraste causé est **11 extinctions et 1 sauvetage** ». `FIMRCC02_POWER.json` donne les quatre cases : 11 / 1 / 1 / 28. Le rapport ré-émet le cadrage retiré.

**Citation fautive.** Rapport §2.2 : « sur toute la trajectoire post-`t_m`, **12/41 contre 2/41** »

**Correction.** Écrire « 11 paires où le traitement éteint et le témoin non, 1 l'inverse, 1 les deux, 28 aucune (p = 0,0063) ».

---

### F11 — PORTANTE — « 123 archives toutes vérifiées » au présent : phrase retirée, et démentie par la dernière exécution de la porte

**Constat.** `GATE01/out/OMLDCT03_INTEGRITY.json` (présent dans l'arbre, 2026-08-30T06:33) : `OCTETS = {sha256_match: 0, sha256_mismatch: 0, missing: 123}`, `CONTENU.n_arms_read = 0`, `ALL_ARCHIVE_HASHES_MATCH = false`, `ALL_CONTENT_CHECKS_PASS = false`, **`INTEGRITY_GATE_PASSES = false`**. Et `CLOSE01_CHECKER_ADJUDICATION.CE_QUI_EST_RETIRE[6]` : « « 123 archives vérifiées » **au présent** ». Le rapport le remet au présent, sans qualification temporelle.

**Citation fautive.** Rapport §2.2 : « 609,52 instances-bras sur un plafond de 926 (plafond non contraignant), **0 échec technique, 123 archives toutes vérifiées** »

**Correction.** « 123 archives vérifiées **au moment où elles ont été scellées** (`TBRT02_SEALED_LEDGER`, sha256 par archive) ; la dernière exécution commitée de la porte d'intégrité du programme rend `missing = 123` et `INTEGRITY_GATE_PASSES = false`. » Au passage : le rapport §2.3 décrit GATE01 comme « un instrument » et ne dit jamais que ses deux portes **refusent** OMLDCT03 (`OMLDCT03_INTEGRITY.json`, et `OMLDCT03_PRIOR_ART.json` : `N_FLAGGED = 41`, passée « APRÈS coup, en réponse au constat F9 »).

---

### F12 — PORTANTE — Divulgation asymétrique dans le rapport, et incohérence avec le manuscrit

**Constat.** Le rapport donne le mélange qui soutient le mur et tait le chiffre qui pointe dans l'autre sens ; le manuscrit, lui, le donne (§4, ligne « drop the 9 treated window-extinctions | 32 | **0.0433** »). J'ai recalculé les deux : n = 32, durée p = **0,0433**, médiane +0,6325 ; exposition p = 0,0770, médiane +0,7295. C'est le constat F6 de CLOSE01, ACCEPTED, PORTANTE, mot pour mot : « il discute déjà le confondant dans le sens qui soutient le mur, et il **tait le chiffre qui pointe dans l'autre** ».

**Citation fautive.** Rapport §2.2 : « Le `p = 0,246` publié est un **mélange** : médiane +0,6325 sur les 28 paires que le traitement ne tue pas, **−0,3231** sur les 13 qui contiennent une extinction. » *(fin de la puce — le p = 0,0433 n'apparaît nulle part dans le rapport)*

**Correction.** Ajouter, dans la même phrase : « et sur les 32 paires sans extinction traitée, le critère primaire seul rend p = 0,0433, rapport médian 1,88 — franchissant l'alpha gelé, mais conditionnant sur une variable post-traitement et donc inadmissible comme estimand ». Aligner les deux documents.

---

### F13 — PORTANTE — Ce qui « manque » à OMLDCT03 est réduit à un dixième du retour de checker

**Constat.** Le checker rend onze findings, dont F1 (accrual, LOAD-BEARING), F4 (« the load-bearing sentence of that file is **false as written** »), F5 (porte d'intégrité sautée, = RPP98 F15 répété), F6 (le 4ᵉ terminal gelé est inatteignable), F7, F8 (ρ = 0,9751, « **It is one endpoint reported twice** »), F9 (clauses héritées absentes, gel lié par un horodatage, pas de digest de code, une chaîne terminale gelée mutée), F10.

**Citation fautive.** Rapport §2.2 : « **Manque pour publier** : rien de statistique. Il manque que l'artefact **nomme** les deux confusions, ce qu'il ne fait pas. »

**Correction.** Énumérer au moins F1, F4, F7, F8, F9. « Rien de statistique » est faux : F8 établit que la règle ET n'achète presque aucune sévérité (ρ = 0,975, concordance de signe 41/41), ce qui est un constat statistique, et il n'est repris dans aucun des trois documents alors que l'abstract présente deux p comme deux critères.

---

### F14 — MATÉRIELLE — Vocabulaire interdit, quatre occurrences

**Constat.** La règle est écrite dans l'arbre, dernière ligne d'`OMLDCT03/out/EDL_BILAN_20260830.html` : « le vocabulaire du vivant reste exclu du dossier, **y compris pour le nier** ». Occurrences :

| fichier : ligne | citation |
|---|---|
| MS:42 | « We make **no claim** about persistence, ownership, individuation, minimal **reproduction**, or **heredity**. » |
| MS:206 | « that any criterion of minimal **reproduction** is met » |
| MS:208 | « peaking at 1–6 Y over **its life** in 40 of 41 treated arms » |
| Rapport:237 | « la restriction aux 28 paires où les deux bras ont **Y vivant** » |

Les jetons `REPRODUCTION_STATUS = NOT_TESTED` / `HEREDITY_STATUS = NOT_TESTED` (MS:220, Rapport:405-406, Matrice:88-89) sont **permis** et n'entrent pas dans ce constat.

**Correction.** MS:42 → « We make no claim about persistence, ownership, or individuation, and no programme status is moved; the frozen status tokens are re-emitted in §7. » MS:206 → supprimer la clause. MS:208 → « over its identity interval ». Rapport:237 → « où Y n'est éteint dans aucun des deux bras ». Risque adjacent à surveiller : « always-survivor stratum », « the worlds it does kill », « the daughter dying » (MS §4, §3.1) — tolérables comme vocabulaire de risques concurrents, mais à border explicitement.

---

### F15 — MATÉRIELLE — Jeton verbatim fabriqué

**Constat.** La chaîne réelle, dans `FIMRCC02/out/FIMRCC02_POWER.json`, champ `CE_QUE_CETTE_ANALYSE_DECIDE.E3_E4_E5_TELS_QUE_GELES_SUR_SELECTIVE_CONTRE_SHAM`, est `NON_INTERPRETABLES__CONFONDUS_PAR_LA_MORTALITE_DIFFERENTIELLE`. Le manuscrit imprime une traduction anglaise **en police de code**, comme un jeton d'artefact. Ce jeton n'existe nulle part.

**Citation fautive.** MS §8 : « a pre-freeze power analysis that declared the frozen endpoints `NON_INTERPRETABLE__CONFOUNDED_BY_DIFFERENTIAL_MORTALITY` »

**Correction.** Citer la chaîne française telle quelle, avec sa traduction en clair hors backticks. Le rapport §2.2 la cite correctement — les deux documents divergent.

---

### F16 — MATÉRIELLE — La revendication d'antériorité ne dit pas ce que ses trois sources disent

**Constat.** J'ai lu les deux sources. `GATE01/out/EDL_PRIOR_ART_MAP.json` (`LE_RISQUE_HONNETE`) et `FIMRCC02/out/FIMRCC02_POWER.json` portent **exclusivement** sur la **mortalité différentielle** (« Y s'éteint dans 12 des 41 bras SELECTIVE… un contraste apparié de comptes après t_m mesurera en partie la mort du monde »). Ni l'un ni l'autre ne mentionne MERGE, la suppression d'un canal de terminaison, ni la non-échangeabilité de l'endpoint. Ce fait-là n'apparaît **qu'une fois**, dans le checker d'OMLDCT03, F3.

**Citation fautive.** Rapport §3.2 : « ce fait n'est *pas* une découverte de cette relève. Il est écrit **trois fois** dans le programme — `GATE01/out/EDL_PRIOR_ART_MAP.json` (02:07), `FIMRCC02/out/FIMRCC02_POWER.json` (02:11), et le checker d'OMLDCT03 (F2, F3). »

**Correction.** « La **mortalité différentielle** est écrite trois fois (GATE01 02:07, FIMRCC02 02:11, checker F2). La **suppression du canal MERGE** est écrite une fois, dans le checker F3, et nulle part ailleurs. » Les deux horodatages, eux, sont exacts (`2026-08-30T02:07:38` et `T02:11:47`) — vérifiés.

---

### F17 — MATÉRIELLE — L'abstract juxtapose deux vecteurs d'ordre incompatible

**Constat.** L'abstract donne la clé d'ordre `SPLIT_OR_TIE / EXTINCTION / MERGE / OUT_OF_RANGE` = 32/9/0/0 et 28/0/7/6, puis, deux phrases plus loin, « (**29 / 2 / 2** against **22 / 5 / 6**) » — où l'ordre est split/**merge**/extinction (§3.3 l'explicite). Un lecteur qui applique la clé annoncée lit « 2 extinctions » là où il y a 2 fusions.

**Citation fautive.** MS abstract : « The same asymmetry appears in an earlier, independent 33-pair campaign under the same law (**29 / 2 / 2** against **22 / 5 / 6**). »

**Correction.** Épeler les canaux dans l'abstract, ou réordonner en 29/2/2 → split 29 / extinction 2 / merge 2.

---

### F18 — MATÉRIELLE — « years apart in programme time »

**Constat.** Gel OMLDCT02 : `2026-08-25T22:30:05` (cité dans `LE_GEL_APPLIQUE.source`). Fin de campagne TBRT02 : `2026-08-28T04:28:02` (`TBRT02_RUN_STATE.json.0`). OMLDCT03 : `2026-08-30T04:33:08`. **Cinq jours**, deux missions.

**Citation fautive.** MS §3.3 : « Two campaigns, **accrued years apart in programme time** and under different ceilings, show the same structural signature. »

**Correction.** « accrued five days and two missions apart, under different ceilings (512 and 926) ».

---

### F19 — MATÉRIELLE — « total local extinction » : c'est le monde qui meurt, pas la fille

**Constat.** `omldct02_e3_b.py:207-209` : `NO_COMPONENT_AT_THE_NEXT_STEP` est émis quand `W.rows(t+1) is None`, c'est-à-dire quand il n'y a **aucune cellule Y occupée dans le monde entier**. Le checker A9 le dit : « differing from `NO_COMPONENT_AT_THE_NEXT_STEP` only in that **the world also died** in the latter ». Le mot « local » inverse le sens : c'est la mort du monde, ce que FIMRCC02 nomme précisément comme le confondant.

**Citation fautive.** MS §3.1 : « The identity is terminated by **total local extinction** »

**Correction.** « by the extinction of Y in the whole world ». Et corriger le tableau §2 ligne (d), dont la glose « no components at all » est juste, pour que §3.1 ne la contredise pas.

---

### F20 — MATÉRIELLE — « rendement admissible observé » : 4,10 % n'est pas observé ici, 4,633 % l'est

**Constat.** J'ai recompté : TBRT02 = **41 admissibles / 885 graines = 4,633 %**. Le 4,10 % est 33/805, le rendement d'OMLDCT02, que votre propre matrice classe **F4 = DÉCLARÉ, « `OMLDCT02/out` absent »**. Le dimensionnement est donc bâti sur un chiffre non vérifiable présenté comme observé (il gonfle le nombre de graines de 13 % : 9 757 au lieu de 8 635). Second défaut : la méthode. `TBRT02_MASTER_FREEZE.HOW_THE_CEILING_WAS_SIZED` enregistre que le plafond 926 a été dimensionné « with the admissible rate drawn from its own **Jeffreys posterior** rather than held at the point estimate » — et que tenir le taux au point estimé était « the error EVCS01 found in its own instrument and fixed ». Votre §4 retient le taux au point estimé, sans incertitude : régression vers une erreur que le programme a consignée et corrigée.

**Citations fautives.**
- MS §5 : « At the **admissible-pair yield actually observed in this programme** (≈ 4.1 %) »
- Rapport §4 : « Dimensionnement au **rendement admissible observé**, comme demandé »

**Correction.** Donner les deux : « rendement observé sur le flux costé, 41/885 = 4,63 % ; rendement déclaré d'OMLDCT02, 33/805 = 4,10 % (non vérifiable ici) », et propager l'incertitude par un postérieur de Jeffreys comme EVCS01.

---

### F21 — MATÉRIELLE — C1 est classée « non relue » alors qu'elle est vérifiable dans l'arbre

**Constat.** J'ai vérifié la règle de fusion dans `OMLDCT02/code/omldct02_e3_b.py:107-131` (`_link_map` : `mp[i]=j` seulement si `rc[i]==1` **et** `cc[j]==1`) et `:216-219` (`if cur not in mp: rc==0 → OUT_OF_RANGE ; rc>1 → SPLIT_OR_TIE ; sinon → MERGE`). Le classifieur B est l'un des deux classifieurs gelés dont l'artefact déclare l'accord sur les 82 bras. La règle est donc lisible ici.

**Citation fautive.** Matrice C1 : « la ligne source n'est pas dans cette récupération — **citation du checker, non relue** »

**Correction.** Reclasser C1 en **VÉRIFIÉ** avec la source `omldct02_e3_b.py:107-131,216-219`, et ajouter la portée : la fusion est impossible quand la composante suivie est seule *au pas précédent*, ce qui vaut sur 99,6 % des pas et non partout (cf. F7).

---

### F22 — MATÉRIELLE — Trois missions à sortie présente ne sont jamais auditées, et le compte de §2.3 est faux

**Constat.** Répertoires portant un `out/` dans l'arbre : BPRTC01, CLOSE01, FIMRCC02, GATE01, **MCTT01**, OMLDCT03, **PQEC01**, RPP97, RPP98, TBRT02 = **dix**, pas sept. `BPRTC01/out/BPRTC01_MASTER_FREEZE.json`, `MCTT01/out/{MCTT01_SELECTED_LAW.json, MCTT01_PHYSICS_DIFF_FROM_B1.json}` et `PQEC01/out/PQEC01_MASTER_FREEZE.json` ne sont cités dans aucun des trois documents — et `MCTT01_SELECTED_LAW.json` est portant : c'est le fichier qui fixe `LAW_C_MCTT01`, la loi dont **tous** vos résultats dépendent. Votre propre `MANIFEST.json` les compte (`TOP_LEVEL: BPRTC01 1, MCTT01 2, PQEC01 9`).

**Citation fautive.** Rapport §2.3 : « **Cinq missions sur sept portant une sortie** sont retirées ou n'adjugent rien ; la sixième (OMLDCT03) est un non-détecté sous-puissancé ; la septième (GATE01) est un instrument. »

**Correction.** Corriger à dix, et ajouter une ligne pour chacune des trois (au minimum : MCTT01 = la loi sélectionnée, gel, `ALL_CHECKS_PASS = true`, non auditée ici).

---

### F23 — MATÉRIELLE — La « divergence non réconciliée » RPP97/RPP98 n'est pas une divergence

**Constat.** RPP97 mesure une taille de composante **en cellules** (`largest_component_ever_seen_in_the_windows = 4`, `median_size_when_undefined = 1`) dans deux fenêtres qui, `t_m` valant en médiane 713 (min 370, max 1673 — recalculé sur `PER_PAIR`), sont **toutes tronquées au début du monde** : `[t_m−2000, t_m−1000]` est négative pour **41 des 41** triplets. RPP98 mesure une masse parentale **en quanta Y** (`MASSE_PARENT_TOUS_EPISODES.median = 88`) sur 4 760 épisodes de `t_start` médian **3 329**. Unités différentes, supports temporels disjoints, objets différents. Il n'y a rien à réconcilier.

**Citation fautive.** Rapport §1.3 : « | taille des composantes | RPP97 §1 : plus grande composante observée = **4 cellules** | RPP98 : masse parentale médiane = **88 quanta** par épisode | **Non réconcilié.** Les deux mesures portent sur les mêmes 123 archives »

**Correction.** Supprimer la ligne, ou la remplacer par : « aucune divergence : cellules contre quanta, et les fenêtres de RPP97 sont clipées à t < t_m (t_m médian 713) tandis que les épisodes de RPP98 démarrent à t médian 3 329. »

---

### F24 — MATÉRIELLE — Les blocs de statuts diffèrent entre les trois documents, tous trois se disant « inconditionnels »

**Constat.** `CLOSE01_CHECKER_ADJUDICATION.STATUTS_INCHANGES` en porte **16**, `OMLDCT03_FROZEN_TEST_RESULT.STATUTS_INCHANGES` **13**. Rapport §5 et matrice §H : **10**. MS §7 : **6**. Absents des trois : `OMLDCT03_STATUS = FROZEN_STATISTICAL_PROCEDURE_EXECUTED_AT_ITS_REQUIRED_N_ON_A_MATCHED_SAMPLE_OBTAINED_OUTSIDE_ITS_ACCRUAL_RULE__EFFECT_NOT_DETECTED__INCONCLUSIVE`, `RPP97_STATUS`, `RPP98_STATUS`, `FIMRCC02_STATUS`, `FIMRCC01_E3_E4_E5_STATUS`, `OBFOR01_HISTORICAL_WINDOW_STATUS`. C'est la sixième répétition d'un constat accepté (checker F9, CLOSE01 F19 « cinquième répétition »).

**Citations fautives.** Rapport §5 « **Statuts ré-émis inconditionnellement** » ; MS abstract « Programme statuses are **unchanged and re-emitted in §7** ».

**Correction.** Ré-émettre les 16, à l'identique, dans les trois documents — en particulier `OMLDCT03_STATUS`, qui est la borne exacte de la revendication centrale et que vous paraphrasez au §2.2 sans le citer.

---

### F25 — MATÉRIELLE — Le rapport cite mal le sous-titre de son propre manuscrit

**Constat.** MS ligne 3 : « Removing an object removes a competing termination channel, and **a pre-registered paired endpoint** stops being exchangeable ». Rapport ligne 308 : « a pre-registered paired **survival** endpoint ». Le mot ajouté est précisément le mot chargé.

**Correction.** Citer exactement, ou changer le sous-titre du manuscrit — pas les deux versions dans le même dossier.

---

### F26 — MINEURE — Trois affirmations non sourçables dans des documents dont la discipline est le sourçage

**Constats et citations.**
- Rapport §4.1 : « Le conteneur revient à un instantané ancien **toutes les 76 à 90 minutes** » — aucune occurrence de cette cadence dans l'arbre (les artefacts parlent de « eleven container rollbacks », « 28e retour arrière », « vingt-cinq fois »). Soit sourcer, soit marquer « observation opérationnelle de cette session, non consignée ».
- MS §5 : « about seven times **the largest ceiling this programme has ever authorised** » — 6 302/926 = 6,81, arithmétiquement juste, mais le superlatif porte sur 40 missions dont 8 `out/` sont absents : invérifiable ici. Écrire « the largest ceiling recorded in this recovery (926) ».
- MS §8 : « at least one recent published criterion in this area admits spatially disjoint replicators » — **sans référence**, alors que la référence est dans l'arbre : `TBRT02/out/TBRT02_PRIOR_ART_SWEEP.md §1`, Hintze & Bohm (2026), *npj Complexity*, doi:10.1038/s44260-026-00074-2, arXiv:2508.08047, marquée « VÉRIFIÉE, LUE ». Le préambule de ce balayage interdit lui-même les références non vérifiées. La citer.

---

### F27 — MINEURE — « technically flawless », et deux mésattributions de source

**Constats et citations.**
- MS §6.3 : « a completed, **technically flawless** 41-triple campaign » — `TBRT02_C5_CLOSURE.4_MY_OWN_ERRORS_IN_THIS_MISSION` liste **six** erreurs de l'opérateur dans cette campagne. Le champ du ledger est `technical_failures: 0`. Écrire « a campaign with zero technical failures ».
- Matrice C4/C6 attribuent l'occupation 99,6 % / 6,4 % et le mélange au checker ; la source primaire des 12/2 et du strate n = 28 est `FIMRCC02/out/FIMRCC02_POWER.json` (`paires_les_deux_vivants: 28`, listes d'indices), **présent dans la récupération**. La citer.
- Matrice F4 classe « OMLDCT02 : 33/805 » en **DÉCLARÉ** ; le 805 est dans `TBRT02_MASTER_FREEZE.HOW_THE_CEILING_WAS_SIZED` (« OMLDCT02's PROSPECTIVE 805-seed ledger »). Le 805 est CITÉ, seul le 33 est déclaré.
- MS §9 : « the figures in §3.2, §3.3 and §4 … were **not** recomputed » — j'ai recalculé **4 des 5 lignes** du §4 depuis `PER_PAIR` seul, et la 5ᵉ depuis `PER_PAIR` + `FIMRCC02_POWER.json`. La phrase est fausse en votre défaveur ; vous aviez de quoi vérifier et ne l'avez pas fait.

---

### F28 — MINEURE — Deux incohérences numériques internes

- **Taille de l'arbre.** Rapport §1.4 : « Arbre récupéré : **4,05 Mo** ». `RECOVERY/RECOVERY_REPORT_20260904.md` §5, livré dans le bundle : « Arbre récupéré : **5,0 Mo** ». Mesuré : 246 fichiers de charge = 3 963 075 o ; arbre hors `.git` = 4 062 099 o ; `MANIFEST.TOTAL_BYTES = 4 053 773`. Le rapport suit le manifeste, le rapport de récupération se trompe de 25 %. Corriger `RECOVERY_REPORT`.
- **Puissance à 79 paires.** Rapport §4 : « ≈ 79 paires ≈ **puissance 0,20** ». Sa propre table (0,158 à 41, 0,317 à 100) interpole à 0,26 ; mon bootstrap donne **0,254** à n = 79. Le 0,20 n'est cohérent ni avec la table du même paragraphe ni avec le calcul.

---

## CE QUI TIENT — mes propres recalculs, avec mes valeurs

Tout ce qui suit a été recalculé par mon code, sans importer aucun module du dépôt.

**Le test gelé, 12/12 grandeurs, au dernier chiffre** (rang signé exact par DP sur les rangs entiers, médiane, Hodges-Lehmann par moyennes de Walsh, intervalle par inversion, trim 280) :

| | W⁺ | n | p exact bilatéral | médiane | HL | IC 95 % |
|---|---|---|---|---|---|---|
| durée | 521.0 | 41 | 0.24638633591985126 | +0.21357410029805912 | +0.3330781223665489 | (−0.23853947588423452 ; 0.8369882167858358) |
| exposition | 504.0 | 41 | 0.34791725337890966 | +0.5694680843784337 | +0.3161356967977471 | (−0.31096591919555827 ; 0.8738989882841586) |

Aucune égalité dans les |différences| (la loi exacte est licite), 25 positives / 16 négatives sur les deux critères, `n_zero = 0`. Les valeurs `+0,33307812236654888` et `+0,31613569679774711` du rapport §1.2 sont **le même double** que celles de l'artefact — j'ai vérifié l'égalité flottante, ce n'est pas un écart.

**Mélange des terminaisons** : SELECTIVE `SPLIT_OR_TIE` 32 / `NO_COMPONENT_AT_THE_NEXT_STEP` 9 / `MERGE` 0 / `OUT_OF_RANGE` 0 ; SHAM 28 / 0 / 7 / 6. Croisement : **22 paires finissent de la même façon dans les deux bras, 19 non.**

**Table de sensibilité, les cinq lignes** (les quatre premières depuis `PER_PAIR`, la cinquième en croisant les 13 indices d'extinction de `FIMRCC02_POWER.json`) :

| spécification | n | durée p | durée méd. | expo. p | expo. méd. |
|---|---|---|---|---|---|
| test gelé tel qu'exécuté | 41 | 0.2464 | +0.2136 | 0.3479 | +0.5695 |
| retirer les 9 extinctions traitées | 32 | **0.0433** | +0.6325 | 0.0770 | +0.7295 |
| strate « survivants dans les deux bras » | 28 | 0.0774 | +0.6325 | 0.0946 | +0.7295 |
| retirer les 7 MERGE témoins | 34 | 0.2932 | +0.2071 | 0.3605 | +0.5118 |
| même terminaison dans les deux bras | 22 | 0.1207 | +0.4454 | 0.1465 | +0.6208 |

Et le mélange : 13 paires avec extinction → médiane **−0.3231**, 6/13 positives ; les 28 autres → **+0.6325**, 19/28 positives. Tout se reproduit.

**Coûts d'accrual** — je reproduis exactement les trois chiffres du checker F1 et les vôtres, depuis les 885 lignes du ledger : total 3 bras enregistré **609.51703** ; recoût 2 bras **571.6494** ; par graine **0.645932** (2 bras) et **0.688720** (3 bras) ; un budget de 512 instances s'épuise **à l'indice 789 avec 38 paires** (dépensé 511.535).

**Campagne TBRT02** : 885 graines, **53 déclenchées**, **41 admissibles**, **0 `technical_failure`**, plafond 926 non contraignant, `prefix_limit_used = 6501` sur les 885. Rendement admissible **41/885 = 4,633 %**.

**`METHODS_HASH`** : les 17 fichiers de `TBRT02_MASTER_FREEZE.METHODS_FILES` existent tous, leurs 17 sha256 concordent, et le digest canonique recalculé par la formule gelée rend `21571fb4cb1df9ac2e9089924e9d6ee5d4d63c920a007e188bdc24e0d94d1f99` = le champ du gel. **17/17.**

**`TBRT02/out/SHA256SUMS`** : 7 entrées, **7/7 OK**, 0 manquante.

**Verbatims de checker** : 6 présents ; 4 adjudications déclarent un `CHECKER_RETURN_SHA256` (CLOSE01, FIMRCC02, OMLDCT03, RPP98) et les 4 concordent ; RPP97 et TBRT02-C4bis n'en déclarent pas. `CLOSE01 = 1543a8c9fd28de77…`. **A5 et A6 de votre matrice sont justes.**

**Disjonction des graines, vérifiée par moi et non citée** : j'ai régénéré les 1 030 graines d'OMLDCT02 depuis la dérivation commitée (`omldct02_seed_manifest.derive`, tip `d8b5007…`, nonce 0) et intersecté avec les 885 graines effectivement consommées par TBRT02 → **intersection 0**. Corroboré structurellement par `TBRT02_MASTER_FREEZE.TBRT01_AND_OMLDCT02_SEEDS_ARE_INSIDE_THE_FORBIDDEN_SET = true`.

**Bundle** : `sha256 = bba3171540fa494d1987b30dfd095f4305e15c3bb63e5d19bda83c542d6f4360`, **1 005 914 octets** — exacts. Commit `fe6b6311a38a90dfe1be43a0b0ed71ed87fdf051`, **sans parent**, branche `recovery/edl-state-20260904`, unique ref du bundle — exact. `RECOVERY_HASHES.json` : 246 avant, 246 après, **identiques**.

**Extractions et chiffres cités dans TBRT02/RPP97/RPP98** — tous retrouvés littéralement : borne séquentielle `PREREGISTERED_READINGS["41"] = 0.070461`, addendum déclaré à `DECLARED_AT_SEEDS_DONE = 9`, `DECLARED_AT_VALID_TRIPLES = 0`, `2026-08-27T03:19:42` ; C5 §2 « ANSWER: NOTHING », « >4000 adversarial worlds including 7560 rows », « 17 of 41 » ; C5 §3b « 17 of 41 treated worlds against 26 of 41 » ; C5 §3c « 8, 29 and 16 of 41 » ; C5 §3d « 41 triples, 123 archives, 440 MB » ; RPP97 `fraction_undefined = 0.99559`, `largest_component_ever_seen_in_the_windows = 4`, fenêtres antérieures au fork, colonnes identiques à la décimale sur les trois bras ; RPP98 `n_archives 123`, `all_contiguous`, `all_11000_steps`, `n_episodes 4760`, `n_persistants 274`, `MASSE_PARENT.median 88` ; CLOSE01 `N_FINDINGS 22 / N_ACCEPTED 22 / N_REJECTED 0`.

**Physique gelée du manuscrit §1** — vérifiée contre le gel et le code : `L = 36`, `CAP = 16`, `T_HORIZON = 11000`, `CORE_R = 5.0`, `LATEST_ALLOWED_TRIGGER = 6500` ; SELECTIVE = « the parent's Y is removed through the engine's decay channel, Y → WY » ; le déplacement conserve la masse exactement et ne consomme aucun aléa. L'ordonnanceur « `diffuse ×4 → react → decay → feed` » est **correct** contre `ORR01/code/kinetics.py:154-158` (quatre appels `_diffuse` : X, Y, SX, SY) et son docstring `:7`, malgré la formulation plus grossière de `MCTT01_SELECTED_LAW.SCHEDULER`.

**Bootstrap de puissance** — mécanique reproduite (mes valeurs, α = 0,05 bilatéral, règle ET avec concordance) : n=41 → 0.213 / 0.156 / **0.147** ; 100 → 0.308 ; 200 → 0.545 ; 300 → 0.722 ; 370 → 0.809 ; 400 → **0.831**. Vos 0,22 / 0,17 / 0,16 et votre colonne de puissance tiennent aux erreurs de Monte-Carlo près. Réponse à votre question 6.1 : **la méthode est légitime en soi** — rééchantillonner les différences appariées observées est un plug-in bootstrap standard — mais elle estime la puissance **à l'effet empirique**, ce que vos documents ne disent nulle part ; et le chiffre livré est un point sans dispersion alors que la dispersion l'annule (F8).

---

## CE QUE JE N'AI PAS PU VÉRIFIER, ET POURQUOI

1. **Les 33 paires d'OMLDCT02 (29/2/2 contre 22/5/6), le poolé 74 paires (0,141 / 0,117), le ρ = 0,943 sur les 33.** `OMLDCT02/out` est absent — y compris `OMLDCT02_MASTER_FREEZE.json`, `OMLDCT02_FROZEN_ANALYSIS.json`, `OMLDCT02_RAW_MANIFEST.json`, `OMLDCT02_FORBIDDEN_SEEDS.json`. Ces quatre chiffres reposent **entièrement** sur une phrase du checker. Votre matrice les classe correctement CITÉ ; c'est la moitié non vérifiée de la revendication centrale.
2. **L'occupation 99,6 % / 6,4 % (9 672/9 713 et 534/8 353), les 12/2 extinctions de trajectoire, les 9 extinctions absorbantes, les 5 `OUT_OF_RANGE` = mort de la fille.** Mesurés par le checker sur les 123 archives `.npz` ; aucune archive dans la récupération (0 `.npz`, arbre 4,06 Mo contre ~440 Mo). Je n'ai vérifié que l'arithmétique interne (9 672/9 713 = 99,58 % ; 534/8 353 = 6,39 %) et la cohérence des indices d'extinction avec `PER_PAIR`.
3. **`ldfma01_raw.py:143`.** Le répertoire `LDFMA01` n'existe pas dans l'arbre. J'ai vérifié la règle équivalente sur le **classifieur B** (`omldct02_e3_b.py`), ce qui suffit à établir la propriété arithmétique mais pas à confirmer la citation de ligne.
4. **La puissance gelée 0,402 / 0,971 / 1,000.** Source `LDFMA01/out/HANDOFF_…md`, absente. Connue par deux findings acceptés concordants (checker OMLDCT03 F10, CLOSE01 F7).
5. **Tout le contenu du ledger cité en §F de la matrice** — FDOT01 7/160 e-value ≈ 5,2 ; FDFLT01 53/192, p = 5,26 × 10⁻¹², E = 1,22 × 10¹⁰ ; FMRCT01 K = 0/372 ; OBTC02 r80 7,071 vs 7,036. Les `out/` correspondants sont absents ; le seul document de synthèse récupéré (`EDL_BILAN_20260830.html`) ne les porte pas. **Y compris la jambe positive de la thèse phare (FDFLT01)** : je ne peux ni la confirmer ni l'infirmer, et votre §3.1 a raison de ne pas la revendiquer.
6. **PR #34, `paper/persistence-without-ownership-v1`, la branche `codex/one-matched-locked-daughter-control-test-02` @ `99b8044a`.** Non consultés : refus GitHub assumé, conformément à votre consigne. Je ne porte aucun jugement dessus, et je confirme que vos trois documents n'en portent aucun non plus.
7. **L'exécution effective de vos deux scripts.** Je ne les ai pas lancés pour ne rien écrire sous `/home/claude/edl_durable`. J'ai vérifié qu'ils n'importent que la bibliothèque standard (`collections, json, math, os, statistics, sys` / `hashlib, json, os, subprocess, sys`) et j'ai reproduit indépendamment leur résultat statistique. Je ne peux donc pas confirmer le jeton `ALL_CHECKS_PASS`, seulement que les 12 grandeurs qu'il est censé couvrir se reproduisent.
8. **La cadence de rollback du conteneur (76–90 min) et l'effacement « entre deux tours de cette session même ».** Observations d'exécution, non consignées dans un artefact ; je n'ai aucun moyen de les recouper.

*Aucun fichier n'a été écrit, modifié ou supprimé sous `/home/claude/edl_durable` ni `/home/claude/edl_recovery` ; `git status` y montre le même unique `?? RECOVERY/scripts/` qu'à mon arrivée (c'est le finding F1, pas mon fait). Aucun worker de campagne lancé, `tbrt02_repair.py` jamais exécuté, aucun accès GitHub tenté. Mon code de travail est dans le scratchpad de session.*
