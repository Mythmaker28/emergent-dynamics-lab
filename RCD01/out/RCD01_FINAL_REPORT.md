# RCD01 — CONCEPTION DU CRITERE DE REPRODUCTION, RAPPORT FINAL

```
FINAL_DISPOSITION = MINIMAL_REPRODUCTION_CRITERION_DERIVED__SELECTIVE_INTERVENTION_CAPABILITY_MISSING
```

`NEW_SCIENTIFIC_ENGINE_RUNS = 0` — `NEW_WORLD_CONSTRUCTIONS = 0` — `NEW_SEEDS = 0` — `NEW_TRAJECTORIES = 0`

## 1. Preservation des preuves, faite en premier

La capsule `RCD01_REPRODUCTION_EVIDENCE_CORE.tar.zst` (11138269 octets, `6e501e2306062571...`) contient, pour chacun des 192 mondes frais, l'occupation des six especes et la capacite libre a **chaque cellule Y occupee, a chaque pas**, plus l'etiquette de centre gelee. C'est precisement ce qui manquait au noyau de 92 Mo deja durable : sans elle, ni la probabilite de naissance X `min(1, kX·nX·nY)` ni le vivier de candidats `min(nSX, free)` ne sont evaluables la ou X est reellement produit.

Chaque objet extrait porte `source_raw_archive_sha256`, `source_key`, la regle de tranche, `extraction_code_sha256` et `extracted_sha256`. L'extraction est deterministe et aucun champ n'est invente.

`REPRODUCTION_EVIDENCE_WINDOWS_DURABILITY = PASS` — verifiee octet pour octet sur ton disque, aux cotes du noyau de 92 Mo lui aussi reverifie.

## 2. Le resultat parent, recalcule depuis les octets frais

| Quantite | Valeur |
|---|---|
| Succes | **53 / 192** |
| Taux | 0.2760416667 |
| Borne basse exacte unilaterale 95 pourcent | 0.2232489797 |
| valeur p exacte | 5.255896e-12 |
| Troisieme centre avant la fonction | 0 / 192 |
| Integrite X | 192 / 192 |

Aucune valeur n'a ete copiee depuis le lanceur ; toutes sont re-derivees des archives.

## 3. Les quatre niveaux

| Niveau | Sens | Statut | Compte |
|---|---|---|---|
| **R0** multiplication fonctionnelle | un centre fonctionnel devient deux | **ESTABLISHED** | 53 / 192 |
| **R1** reconstruction materielle | le nuage de la fille n'est pas du materiau redistribue | **SUPPORTED_AS_A_CERTIFIED_LOWER_BOUND** | 25 / 53 |
| **R2** independance fonctionnelle | la fille survit au retrait du parent | **NOT_TESTABLE_WITH_THE_CURRENT_ENGINE** | 0 |
| **R3** competence reproductive | la fille engendre a son tour | **NOT_IDENTIFIABLE_IN_THIS_DATASET** | 0 |

**`MINIMAL_REPRODUCTION = R0 et R1 et R2`.** R2 est le contenu causal du mot. Sans lui, une fille qui meurt a l'instant ou le parent disparait n'a jamais ete un systeme independant.

## 4. Provenance materielle — critere derive avant tout comptage

Survie par molecule sur 249 pas : **0.3686169213**. Critere sans seuil : `Dm > Q_0.95(Binomial(N0, (1-muX)^D))`.

**25 mondes sur 53** passent. La borne credite la fille de **chaque** molecule ancienne survivante du monde entier, y compris celles que le parent detient : c'est donc une borne inferieure, pas une estimation. Fraction certifiee neuve : mediane 0.0000, maximum 0.3918.

**Resultat inattendu :** la fille est le centre le plus faible dans seulement **24 des 53** succes. the frozen FDFLT01 condition F5 compared the WEAKER centre to the STRONGER one, which is identity-free and symmetric. Persistent identity shows the daughter is the weaker centre in fewer than half the successes, so F5 frequently constrained the PARENT. That makes F5 stricter than a daughter-only criterion, not weaker, and the FDFLT01 result is unaffected.

## 5. Interventions — le blocage

`CLASSIFICATION = GLOBAL_ORGANISER_OFF_ONLY`

La seule intervention causale du moteur, `organiser_off_at`, met a zero le champ Y **entier** en trois lignes. Retirer le parent retire la fille au meme instant. **L'experience qui deciderait de la reproduction n'est pas exprimable en l'etat.**

La plus petite capacite manquante est `selective_organiser_off`. Ce n'est **pas** un changement d'architecture : it manipulates the experiment at a declared instant. It adds no term to the autonomous law: between interventions every rate, every candidate rule and every update remains bit-identical. The existing global organiser_off already establishes the precedent and the channel; only the spatial scope changes.

## 6. Les 25 mondes a trois centres

25 mondes atteignent un troisieme centre, dont 20 avaient deux centres fonctionnels avant. Ecart entre maturation et troisieme centre : mediane 2676 pas.

Mais **0 sur 25** disposent d'assez d'enregistrement pour que ce troisieme centre mature a son tour. the frozen PQEC01/FDFLT01 stop rule halts a world at PREMATURE_THIRD_CENTRE. Every one of these worlds therefore ENDS at the third centre. Whether the third centre would itself mature functionally is UNOBSERVED BY CONSTRUCTION, not merely unobserved.

`CLASSIFICATION = SECOND_GENERATION_EVENT_NOT_IDENTIFIABLE`. La proximite spatiale est enregistree mais **n'est pas une preuve de descendance** ; aucune genealogie n'en est deduite.

## 7. Deux calculateurs independants

`INDEPENDENT_REANALYSES_AGREE_ON_EVERY_CLASSIFICATION__ONE_PARENT_DAUGHTER_LABEL_UNDETERMINED_BY_AN_EXACT_TIE`

Un episode de correction est au dossier : implementation B initially evaluated the functional-response condition on the FIRST qualifying S episode only. The frozen FDFLT01 rule accepts ANY qualifying episode. The two checkers therefore disagreed on 7 of 192 worlds, all of them multi-episode worlds where A said success and B said failure. B was corrected to the frozen specification and re-run. A was not touched.

Un desaccord residuel subsiste sur **1 monde sur 192** : an EXACT geometric tie. At the separation step the pre-separation centroid is (21.5, 32.5) and the two new components sit at (19,33) and (24,32), both at toroidal distance 2.5495097568 from it. The difference is 0.0. The parent/daughter rule 'the component closest to the pre-separation centroid is the parent' is SILENT here. Aucune classification n'en depend. Une regle de departage deterministe doit etre declaree avant toute experience conditionnee sur l'identite de la fille.

## 8. Le futur test, concu mais non eligible

Trois phases, trois controles, estimande primaire = taux de reproduction par monde ensemence. 33.3 mondes de phase 2 attendus sur 256. Decidable contre un nul de 0,02 jusqu'a une survie fille `q ~ 0,40` ; contre 0,05 seulement si `q >= 0,80`.

Il ne peut pas etre lance : l'intervention selective n'existe pas.

## 9. Architecture

`ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED`

what is missing is an EXPERIMENTAL_INTERVENTION_CAPABILITY, not an AUTONOMOUS_ARCHITECTURE_CAPABILITY. Between interventions the law is untouched. No evidence shows that a daughter cannot be source-autonomous; the question has simply never been asked, because the only executable removal deletes both centres at once.

## 10. Vocabulaire

`QUALIFIED_FUNCTIONAL_LINEAGE_EVENT = ESTABLISHED` — `MINIMAL_REPRODUCTION = NOT_TESTED` — `STRONG_SELF_REPRODUCTION = NOT_TESTED` — `HEREDITY = NOT_TESTED`

Aucun emploi de « organisme », « organisme fille », « vie creee » ou « auto-replication demontree ».

