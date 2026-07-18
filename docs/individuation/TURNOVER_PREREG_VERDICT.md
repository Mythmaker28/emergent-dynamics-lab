# LCI-CAUSAL-TURNOVER-PREREG-03 — Verdict (Phase 10)

*Independent agent. Audit + metrology + candidate pre-registration of a turnover-survival test for local causal
individuation. No prospective family opened; no confirmatory seed run; human authorization requested. I did not shade
anything toward ACTIVE-RECONSTRUCTION.*

## VERDICT EN UNE LIGNE
**REPAIR — le test est faisable et reproductible, mais tel que posé il n'établirait que la barre BASSE (effet causal
interventionnel, couplé par construction, qui survit ~par construction : DEV deep_own +0.131, 4/4 mondes) tandis que
la barre SIGNIFIANTE (stockage gradué own-spécifique) s'homogénéise localement et échoue probablement (DEV own-dose
0.135 < voisin 0.580) ; la faisabilité est réelle mais coûteuse (~50 % des mondes éligibles perdent une gouttelette
par FISSION/mort), donc la famille prospective ne doit être ouverte qu'après les réparations ci-dessous, et
ACTIVE-RECONSTRUCTION reste BLOQUÉE.**

## QUESTION
Une gouttelette ayant reçu une histoire locale propre conserve-t-elle (1) cette information, (2) sa capacité causale
propre sur son nourrissage, (3) sa distinction vis-à-vis des voisines, après renouvellement profond de sa matière
(`M_i ≤ 0.25`), tout en restant une composante physique distincte ?

## POINT DE VUE INDÉPENDANT
Le résultat au repos est réel mais ÉTROIT : le readout `uptake ∝ (1+λ₊·tanh(m₊))` est couplé à la mémoire PAR
CONSTRUCTION, la mémoire est intensive, portée par la masse, COPIÉE PASSIVEMENT sur la matière neuve (`Mf += g·m`) et
préservée par la mort homogène. Un test naïf « l'effet causal survit-il au turnover » est donc à HAUT RISQUE d'être
quasi-tautologique. Les vraies questions sont la FAISABILITÉ et la SÉPARABILITÉ (own vs voisin vs global). Les
pilotes DEV confirment exactement cette dissociation.

## RÉSULTAT REST HÉRITÉ
confirm-02 (`830c2d0`) reproduit BYTE-IDENTIQUE (certificat régénéré 0 diff à 1e-12 ; seeds 53001–3 re-run
identiques). Individuation causale INTERVENTIONNELLE/LOCALE au repos : own +0.223 [0.193,0.258], voisin/sham ≈0,
ablation 0.000, masque-fixe 1.08×, DD 2590, dose R² 0.691. Décodage gradué INDÉTERMINÉ. Antérieur EXP1 : maintien
au turnover profond NON établi (own-dose 0.37 [0.14,0.72], ordre s'effondre).

## TURNOVER IMPLÉMENTÉ
Runner DEV résumable (`turnover_dev_runner.py`), refuse tout seed hors 50001–50010. Écriture locale (bloc storage
confirm-02 verbatim) → snapshot REST → essai causal 0.25×5 sur BRANCHES → turnover NEUTRE (sans drive/probe, C1c
inchangé, écriture ACTIVE justifiée/gelée Phase 4C) sur le monde non perturbé → snapshot PROFOND au 1er instant
pré-déclaré (3 vivantes/distinctes/non-fusionnantes, `M_i≤0.25`) → essai causal identique en profondeur. REST du
runner concorde exactement avec `nm.run_seed` (auto-cohérence).

## TRACEURS
Cohortes passives par cible ajoutées à `C`, semées au snapshot (`MATERIAL_TRACER_SPEC.md`). STRICTEMENT
OBSERVATIONNELLES : champs byte-identiques avec/sans traceurs sur 850 pas (max|Δ|=0.0) ; jamais nourries (index de
feed 11 < base 12) ; déterministes (0.0) ; `M_i` monotone, sans artefact de périodicité.

## M_i
Mesuré PAR gouttelette (plus l'estimation analytique globale héritée). DEV feasibles : `M_i` 0.96→~0.20, chaque
gouttelette ≤0.25 au profond. Contamination croisée (matière du voisin) mesurée et gatée.

## P_i
Séparés (sans score composite) : taille, masse, rg, forme/localisation (janus, radial_u, interface), uptake basal,
attractant c, viabilité — via `detect()`.

## F_i
Composantes séparées : own (intact−erase-target), own−voisin, own−sham, ablation, tracked bijectif, masque-fixe.
DEV PROFOND : own +0.131, sham −0.000, voisin −0.000, ablation +0.000, fixe +0.136 — **4/4 mondes own>0**.

## CANAL GLOBAL
`up_ref` NE resynchronise PAS : au profond, terme global `|k_up(uptake−up_ref)|`=3.2e-4 ≈ **1700× plus petit** que le
terme local `|k_exp(N−c)|`=0.56 (ratio 6e-4). La mémoire s'homogénéise quand même (écart inter-gouttelettes m₊
0.07→0.007) mais par forgetting/templating LOCAL, pas par le global. Dissociation : la LOCALITÉ SPATIALE survit
(own≫voisin interventionnel), le CONTENU GRADUÉ non.

## FUSIONS/PERTES
**0 fusion.** Attrition = FISSION ×3 (réelle : 61→38+22 ; 105→68+36) + PERTE ×1. Faisabilité 4/8 éligibles (50 %).

## STOCKAGE DEEP DEV
own-dose R²=0.135 < voisin-dose 0.580 (n=4 mondes/12 échantillons, sous-puissant ET vraisemblablement quasi-nul par
homogénéisation). **G3 = PRIMAIRE-À-RISQUE** ; c'est le rung qui échoue.

## CAUSALITÉ DEEP DEV
own worldCI [0.114,0.148]>0 ; own−sham [0.114,0.148]>0 ; own−voisin [0.114,0.148]>0 ; ablation ≈0 ; tracked/fixe
même signe. SURVIT — mais barre BASSE (multiplicateur couplé sur un résidu spatialement localisé). Rétention
deep/rest ~0.68 (deep < rest, CI [−0.086,−0.046]).

## PUISSANCE
Interventionnel sur-puissant (P(borne inf>0)=1.000 dès n=6). G0 faisabilité : ~44–49 seeds pour ≥12 mondes valides à
90 %. G3 stockage gradué : ≥18 mondes valides ET un effet réel — à risque. Déterminisme byte-identique.

## FAMILLE PROPOSÉE
`54001–54050` (50 seeds, cap 50, gelé). **ABSENTE de tout le registre** (18 branches vérifiées). **NON OUVERTE.**

## RISQUES
`TURNOVER_RISK_REGISTER.md` — load-bearing : R1 tautologie du readout couplé, R2 homogénéisation graduée, R3
attrition par fission, R12 copie-passive ≠ persistance. Tous adressés par le design (G3 co-primaire, null de décroissance
passive, censure au niveau monde, diagnostic up_ref neutralisé).

## PRESEAL CANDIDAT
`PRESEAL_CANDIDATE_PROTOCOL.md` + `PRESEAL_CANDIDATE.json` (étiquetés NOT AUTHORIZED FOR PROSPECTIVE RUN ; hashes de
contenu enregistrés). Certificat DEV non-prospectif `TURNOVER_DEV_CERTIFICATE.json`.

## DÉCISION : **REPAIR**
Réparations requises AVANT toute autorisation prospective :
1. **G3 (stockage gradué own vs voisin vs global) devient CO-PRIMAIRE**, dimensionné pour ≥18 mondes valides ; G4
   seul (interventionnel couplé) NE peut PAS valider G6.
2. **Null de décroissance passive (`eta_w=0`) gating** : l'effet profond observé doit correspondre à la prédiction
   copie-passive (sinon reconstruction — inattendue sur C1c).
3. **Diagnostic up_ref neutralisé** (`up_ref:=0`) + décodeur global-moyenne, exécutés prospectivement.
4. **Cadre pré-engagé honnête** : le résultat attendu est « localité spatiale survit / contenu gradué non », PAS un
   titre « individuation survit au turnover ». Pas de 0.50 inventé pour G5.
5. **Famille 50 seeds** (attrition ~50 %), cap gelé, tous les mondes rapportés, aucune extension post-outcome.
Avec ces réparations : GO possible sur autorisation. Sans elles (run centré-G4) : le résultat serait trompeur.

## AUTORISATION PROSPECTIVE : **NON DONNÉE**
## ACTIVE-RECONSTRUCTION : **BLOQUÉE** (et non justifiée par ce travail : elle le serait par un ÉCHEC du stockage
gradué, pas par la survie interventionnelle — logique non inversée)

## PROVENANCE
Branche `design/lci-causal-turnover-prereg-03` off `9c8a62c`. Lignée `6470513`→`9b7580bc`→`830c2d0`→`9c8a62c`
intacte. Ce commit = design (pas un PRESEAL final).

## MAIN/V4/RELEASE
INTACTS : `main f3921a4`, `V4 23b53ae`, release. C1c, probe 0.25×5, tracker bijectif, PRESEAL/RESULTS historiques,
C1c — non modifiés.

## RIEN POUSSÉ/MERGÉ/PUBLIÉ
Rien poussé, mergé, tagué, publié, soumis. Aucun seed 54xxx exécuté. Aucune revendication d'identité, de vie ou
d'agence. Commande de push fournie pour exécution MANUELLE par Tommy uniquement.
