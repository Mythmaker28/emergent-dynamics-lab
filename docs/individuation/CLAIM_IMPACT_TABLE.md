# CLAIM_IMPACT_TABLE — LCI-CAUSAL-MERGE-INCIDENT-01 (Phase 4)

*Impact du merge/double-tracking sur chaque claim de LCI-CAUSAL-CONFIRMATION-01. Fondé sur : audit du raw
committé (Phase 1, `merge_incident_audit.py/.json`), replay déterministe event-by-event (Phase 2,
`merge_replay.py`, `MERGE_INCIDENT_FIRST_MERGE.png`), tracker bijectif corrigé (Phase 3,
`bijective_tracker.py` + `apply_corrected_tracker.py`), audit washout (Phase 5, `washout_audit.py`), pilote DEV
non-fusionnant (Phase 6, `pilot_nonmerging_dev.py` + `measure_pilot_effect.py`). Plateforme scellée reproduite
byte-identique. **Aucun nouveau claim positif tiré des diagnostics post hoc ; aucun retrait silencieux de monde ;
aucun changement de seuil après observation.***

## Faits porteurs (recalculés, indépendants)

- Fusion physique confirmée par **3 méthodes concordantes** : (i) 19 paires (taille,masse,mean_c) finales
  byte-identiques dans la branche intacte, 11/13 mondes ; (ii) replay — une composante connexe périodique
  recouvre >50 % de ≥2 masques-cibles fixes, premier merge t=62–109 (phase horizon, **après** le stimulus de 15
  pas) ; (iii) tracker bijectif — 22/39 cibles censurées MERGED aux **mêmes pas** que le replay.
- Grille 64²=4096. Composantes finales fusionnées : jusqu'à **52 %** de la grille (mondes all-3 : 36–52 %).
  Croissance ×19 médiane (max ×43).
- **Composantes finales uniques réelles = 24** pour 39 cibles nominales. **Survivants individuels (tracker
  bijectif) = 17/39** ; 11/13 mondes ≤1 survivant ; mondes propres 52008/52018 = 3/3.
- Readout **masque-fixe** (sans tracker) non effondré (0 paire identique) ⇒ fusion pilotée par le stimulus,
  postérieure au début d'horizon.
- Effet propre **tracké +2.03** [1.63,2.48] vs **masque-fixe +0.53** [0.36,0.73] ⇒ **inflation ×4.8** par le
  tracker. Voisin **+0.0006** (propre) dans les mondes non fusionnés vs **+0.247** dans les fusionnés.
- DEV, probes non-fusionnants (géométrie seule) : effet propre masque-fixe **+0.42–0.44, 8/8 mondes>0** — ~même
  magnitude que le probe scellé fusionnant ⇒ l'effet masque-fixe n'est **pas** un artefact de fusion.

## Table d'impact (10 claims)

| # | Claim historique (CONFIRMATION_VERDICT_01) | Statut | Justification |
|---|---|---|---|
| 1 | **Stockage local au repos** (C-K1, DD_mem 5951) | **INCHANGÉ** | Mesuré au repos, avant tout stimulus/fusion ; indépendant du tracker comportemental. |
| 2 | **Lecture de l'histoire locale au repos** (C-K2a, own-dose R²=0.75 ≫ voisin) | **INCHANGÉ** | Décodage de features mémoire 11-D au repos ; pas de tracker de comportement, pas de fusion. |
| 3 | **Effet causal mémoire→uptake** (existence) | **QUALIFIÉ** | Survit **tracker-free** : masque-fixe +0.53 (13/13), effondrement ablation 0.000, double-diss 1.13, et DEV non-fusionnant +0.44 (8/8). MAIS magnitude **+2.03 gonflée ×4.8** par le tracker ⇒ remplacer par la valeur masque-fixe. |
| 4 | **Localité spatiale** de l'effet (voisin 10 %) | **QUALIFIÉ** | Propre (≈0) seulement dans les 2 mondes non fusionnés ; **contaminé (+0.247)** dans les fusionnés. Le « 10.4 % » poolé sous-estime la contamination (dilution par 2 mondes propres). |
| 5 | **Individuation causale d'une gouttelette persistante** | **SUSPENDU** | 11/13 mondes : les cibles fusionnent en une composante géante (36–52 % de la grille) ⇒ l'entité **ne persiste pas** comme individu pendant la mesure. |
| 6 | **« 39/39 gouttelettes >0 »** | **INVALIDÉ** (en tant que 39 entités distinctes) | Seulement **24** composantes finales uniques ; **17/39** survivent sous tracker bijectif. Le 39/39 est gonflé par double-comptage (readout couplé positif partout, y compris tracker-free). |
| 7 | **« Tracking 13/13 robuste, toutes gouttelettes survivent »** | **INVALIDÉ** | Le tracking n'est pas robuste : 11/13 mondes ont des tracks effondrés. « Survie » = 2–3 tracks verrouillent le **même** blob, pas une survie individuelle. Spec (un-à-un) ≠ implémentation (non-bijective). |
| 8 | **G3 (expression causale comportementale)** | **PARTIEL / À RE-ÉNONCER** | Sous-gates robustes tracker-free : (a) existence, (b) ablation 0.000, (e) double-diss. Compromis : (c) localité voisin (contaminée en fusion), la magnitude, et C-K5 « tracker-independence » (le fixe est ×0.2 du tracké — le **signe** est indépendant, pas la **magnitude**). G3 doit être ré-énoncé sur le readout masque-fixe et re-confirmé sans fusion. |
| 9 | **G6 (individuation causale)** = (G1&G2) ∧ G3 | **SUSPENDU** | Requiert des entités distinctes et persistantes ; la fusion (11/13) l'invalide comme mesuré. |
| 10 | **Justification d'ACTIVE-RECONSTRUCTION** (Cas A) | **BLOQUÉE** | Précondition = G6. G6 suspendu ⇒ bloquée jusqu'à une confirmation **non-fusionnante** (Phase 6 montre qu'elle est réalisable). |

## Lecture d'ensemble

Le diagnostic « fusion / double-tracking » est **confirmé** par mon audit indépendant. Mais l'incident n'efface
pas tout : il sépare deux lectures qui étaient conflées dans le VERDICT_01.

- **Ce qui tombe** : le comptage « 39 gouttelettes individuées », la « robustesse 13/13 » du tracking, la
  magnitude +2.03, l'**individuation d'une entité persistante** (G6), et donc la bascule ACTIVE-RECONSTRUCTION.
- **Ce qui tient (qualifié, non re-confirmé ici)** : une **empreinte causale mémoire→feeding locale**, plus
  petite (~+0.5 tracker-free), qui s'effondre sous ablation et résiste à la double-dissociation, et qui est
  présente même sous un probe **non-fusionnant** (DEV +0.44, 8/8). Le stockage et la lecture au repos sont
  intacts.

Ces éléments « qui tiennent » sont des **diagnostics** : ils **qualifient** les claims existants et ne
constituent **aucun nouveau claim positif**. La ré-établissement propre de l'effet mémoire→feeding exige une
**confirmation prospective non-fusionnante** (protocole corrigé Phase 6), à confier à un futur agent après revue.

*main/V4/release intacts. Rien poussé/tagué/publié. Aucune revendication d'identité, de vie ou d'agence.*
