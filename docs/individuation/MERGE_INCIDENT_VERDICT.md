# MERGE_INCIDENT_VERDICT — LCI-CAUSAL-MERGE-INCIDENT-01

*Audit indépendant de la fusion physique et du double-tracking observés dans LCI-CAUSAL-CONFIRMATION-01. Nouvel
agent ; diagnostic confirmé OU contredit par audit propre. Base `b415503`, branche isolée
`audit/lci-causal-merge-incident-01`. Plateforme scellée reproduite byte-identique. Aucune ACTIVE-RECONSTRUCTION,
aucune nouvelle famille prospective, aucun push automatique.*

## VERDICT EN UNE LIGNE

**Fusion physique (percolation jusqu'à 52 % de la grille 64²) dans 11/13 mondes, déclenchant une collision d'un
tracker non-bijectif (spec un-à-un ≠ implémentation) — confirmée par 3 méthodes indépendantes concordantes ; le
stockage et la lecture au repos restent intacts et une empreinte causale mémoire→feeding locale (~+0.5,
tracker-free, présente aussi sous probe non-fusionnant) subsiste, MAIS « 39/39 gouttelettes », « tracking 13/13 »,
la magnitude +2.03 et l'individuation causale d'une entité persistante (G6) sont invalidés/suspendus, et
ACTIVE-RECONSTRUCTION reste bloquée jusqu'à une confirmation non-fusionnante (démontrée réalisable).**

## Champs

- **FUSION PHYSIQUE :** OUI — percolation stimulus-induite (×19 croissance médiane), composante géante jusqu'à
  52 % de la grille ; ≥2 cibles dans une seule composante connexe périodique. Premier merge t=62–109 (phase
  horizon, après le stimulus de 15 pas). **Pas** un wrap périodique (cibles distinctes ≥24 apart qui convergent).
- **COLLISION DE TRACKER :** OUI — `measure_branch` affecte `max(overlap)` indépendamment par track (cadence 1),
  contredisant `TRACKER_SPEC.md` (un-à-un, cadence 5) ; 2–3 tracks lisent la même composante fusionnée, sans
  censure. Collision **consécutive** à la fusion physique (même pas).
- **MONDES AFFECTÉS :** 11/13 — 52001, 52004, 52005, 52006, 52010, 52011, 52012, 52013, 52017, 52021, 52022.
  Tous-3-fusionnés : 52005, 52010, 52012, 52017. Propres : 52008, 52018. (19 paires identiques ; 24 composantes
  uniques ; 17/39 survivants sous tracker bijectif.)
- **STOCKAGE AU REPOS :** INCHANGÉ (C-K1, DD_mem 5951 ; mesuré au repos, sans tracker/fusion).
- **EFFET CAUSAL MÉMOIRE→COMPORTEMENT :** QUALIFIÉ — survit tracker-free (masque-fixe +0.53 [0.36,0.73] 13/13 ;
  ablation 0.000 ; double-diss 1.13 ; DEV non-fusionnant +0.44 8/8), mais la magnitude tracker +2.03 est
  **gonflée ×4.8**. Non re-confirmé ici (diagnostic post hoc).
- **LOCALITÉ :** QUALIFIÉE — propre (voisin ≈+0.0006) dans les mondes non fusionnés ; **contaminée (+0.247)** dans
  les fusionnés ; le 10.4 % poolé dilue la contamination.
- **INDIVIDUATION CAUSALE :** SUSPENDUE — les entités ne persistent pas comme individus (fusion 11/13).
- **G3 :** PARTIEL / À RE-ÉNONCER sur le readout masque-fixe et re-confirmer sans fusion (existence + ablation +
  double-diss robustes tracker-free ; localité et magnitude compromises).
- **G6 :** SUSPENDU.
- **WASHOUT :** résidu réel à `WASHOUT_LONG=200` = **19.4 % de N0** (pas <2 %/~800 pas préinscrit, ni « <1 % »
  du commentaire du runner) ; « suppression du résidu » = fait par le **reset N**, pas par les 200 pas. Transplant
  secondaire annoncé **non exécuté**.
- **SHAM :** marginal (0.148 < 0.15), inchangé mais sujet au même caveat de fusion (branche sham fusionne aussi).
- **CLAIMS INCHANGÉS :** stockage au repos (C-K1) ; lecture de l'histoire au repos (C-K2a).
- **CLAIMS QUALIFIÉS :** effet causal mémoire→feeding (empreinte spatiale ~+0.5) ; localité ; G3.
- **CLAIMS INVALIDÉS :** « 39/39 gouttelettes » (24 composantes réelles ; 17/39 survivants) ; « tracking 13/13
  robuste » ; magnitude +2.03 ; individuation causale d'une entité persistante (G6 suspendu).
- **ACTIVE-RECONSTRUCTION :** BLOQUÉE jusqu'à confirmation non-fusionnante (Phase 6 : 9 probes DEV valides).
- **PROTOCOLE CORRIGÉ :** proposé (probe non-fusionnant sélectionné par géométrie — uniforme amp=0.25 dur=15 ;
  tracker bijectif + censure MERGE ; readout masque-fixe primaire ; gate géométrique bloquant). Conserve snapshot/
  intact/erase-target/erase-neighbour/sham/ablation/standardisation/analyse par monde. **Non scellé, non lancé.**
- **POINT DE VUE INDÉPENDANT :** Je **confirme** le diagnostic de fusion/double-tracking (par mon propre audit du
  raw + replay + tracker bijectif), et je **contredis** la lecture forte du VERDICT_01 (« 39/39 individuées,
  +2.03, tracking robuste »). Je **contredis aussi une invalidation totale** : l'effet mémoire→feeding n'est pas
  un pur artefact (tracker-free +0.5, présent sans fusion). Ma prédiction Phase 0 sur le **moment** de la fusion
  (« pendant/juste après le stimulus ») a été **partiellement falsifiée** par le replay (fusion en phase horizon,
  t=62–109) : je l'ai corrigée. Le mécanisme (croissance stimulus-induite) tient.
- **PROVENANCE :** branche `audit/lci-causal-merge-incident-01` off `b415503`. Historique `b415503`/`c371346`/
  `8b2e12d`/`53fd2b6` **non réécrit**.
- **MAIN/V4/RELEASE :** INTACTS (main `f3921a4`).
- **RIEN MERGÉ/PUBLIÉ :** rien poussé, tagué, publié, soumis ; V4 non modifié ; ACTIVE-RECONSTRUCTION non lancée ;
  aucune revendication d'identité, de vie ou d'agence. (Fusion des gouttelettes ≠ git merge.)

## Commandes de reproduction

```bash
# environnement scellé (plateforme fixe ; déterminisme byte-identique vérifié)
python -m venv venv && venv/bin/pip install numpy==2.2.6 scipy==1.15.3 matplotlib==3.10.9
export PYTHONPATH="$PWD" ; mkdir -p work

# Phase 1 — audit du raw
venv/bin/python experiments/individuation/merge_incident_audit.py \
    experiments/individuation/causal_confirmation_raw.json work/merge_incident_audit.json

# Phase 2 — replay event-by-event (confirmation + DEV) + figure du premier merge
venv/bin/python experiments/individuation/merge_replay.py work/merge_replay_log.json \
    52001 52005 52010 52012 52008 52018 52004 52006 52011 52013 52017 52021 52022
venv/bin/python experiments/individuation/merge_replay.py work/merge_replay_dev.json $(seq 50001 50010)
venv/bin/python experiments/individuation/make_merge_figure.py 52012

# Phase 3 — tracker bijectif : tests + application aux seeds scellés
venv/bin/python experiments/individuation/test_bijective_tracker.py
venv/bin/python experiments/individuation/apply_corrected_tracker.py

# Phase 5 — audit du washout (résidu N à 200 pas)
venv/bin/python experiments/individuation/washout_audit.py 52001 52005 52008 52012 52010 52018

# Phase 6 — pilote DEV non-fusionnant (sélection géométrique) + viabilité (observationnel)
venv/bin/python experiments/individuation/pilot_nonmerging_dev.py
venv/bin/python experiments/individuation/measure_pilot_effect.py
```

## Commande PowerShell de push de la branche d'audit (À EXÉCUTER MANUELLEMENT — aucun push automatique)

```powershell
# depuis le dépôt local ; pousse UNIQUEMENT la branche d'audit, ne touche ni main, ni V4, ni release
cd "C:\Users\tommy\Documents\ising v3"
git push origin audit/lci-causal-merge-incident-01:audit/lci-causal-merge-incident-01
```

*Livrables : `MERGE_INCIDENT_INDEPENDENT_VIEW.md`, `merge_incident_audit.py/.json`, `merge_replay.py` +
logs, `MERGE_INCIDENT_FIRST_MERGE.png`, `bijective_tracker.py` + `test_bijective_tracker.py` (10/10),
`apply_corrected_tracker.py`, `CLAIM_IMPACT_TABLE.md`, `MERGE_INCIDENT_ERRATUM.md`, `WASHOUT_PROTOCOL_AUDIT.md`,
`washout_audit.py`, `pilot_nonmerging_dev.py` + `measure_pilot_effect.py`, `CORRECTED_PROTOCOL_PROPOSAL_01.md`,
ce verdict.*
