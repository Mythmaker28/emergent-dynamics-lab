# MERGE_INCIDENT_INDEPENDENT_VIEW — LCI-CAUSAL-MERGE-INCIDENT-01

*Nouvel agent indépendant. Mission : auditer la fusion physique / double-tracking suspectée dans
LCI-CAUSAL-CONFIRMATION-01. Je ne suppose ni que le résultat causal est valide, ni qu'il est invalidé. Ce
document est ma **position figée**, produite AVANT toute nouvelle simulation (Phase 2+), mais **fondée sur une
ré-analyse du raw committé** (`causal_confirmation_raw.json` @ `b415503`) — c.-à-d. sur des faits recalculés,
pas sur le diagnostic hérité, ni sur la branche `audit/tracker-continuity-incident-01` (que je n'ai pas lue
pour préserver l'indépendance). Il formule des **prédictions falsifiables** que la Phase 2 (replay) testera.*

Provenance : base `b415503` (tip de `exp/lci-causal-confirmation-01` ; BACKUP au-dessus des RÉSULTATS
`c371346`, PRESEAL `8b2e12d`, audit `53fd2b6`). Branche d'audit isolée : `audit/lci-causal-merge-incident-01`.
main `f3921a4`, V4, release : **intacts, rien ouvert, rien poussé**. ACTIVE-RECONSTRUCTION **interdite** cette
mission. Plateforme : py3.11.15 / numpy2.2.6 / scipy1.15.3 / mpl3.10.9 ; **déterminisme byte-identique vérifié**
(snapshot stockage seed 52001 : n_detected=38, sizes=[73,58,56], centroïde à 1e-6 → reproduit le raw scellé).

---

## 0. Ce que j'ai vérifié moi-même sur le raw committé (Phase 1, POST HOC)

Grille **64×64 = 4096 cellules**, seuil de détection ρ>0.30·ρ_max, min 12 cellules (frozen). 13 mondes
éligibles / 24 (éligibilité géométrique 54 %), 3 cibles/monde → 39 gouttelettes nominales.

| Fait recalculé (raw, tracker de `causal_confirm.py`) | Valeur |
|---|---|
| Paires de tracks à **(taille, masse, mean_c) finales EXACTEMENT égales** (branche intacte) | **19** |
| Mondes concernés | **11 / 13** |
| Mondes où les **3** tracks finissent sur **une seule** composante | **52005, 52010, 52012, 52017** |
| Mondes SANS duplication détectée | **52008, 52018** (2) |
| Croissance taille finale/initiale | médiane **19.4×**, max **42.8×** |
| Couverture de grille de la composante fusionnée (max) | **52 %** (2122/4096) ; les 4 mondes « all-3 » : 36–52 % |
| Composantes finales **uniques réelles** (diagnostic D) | **24** — vs 39 gouttelettes nominales |
| Effet propre suivi (tracké) `intact−erase-target`, IC-monde | **[+1.63, +2.03, +2.48]**, 13/13, 39/39 |
| Effet propre **masque fixe** (sans tracker), IC-monde | **[+0.36, +0.53, +0.73]**, 13/13 |
| **Facteur d'inflation tracké / masque-fixe** | **4.80×** |
| Paires identiques dans le readout **masque fixe** (integ_fixed) | **0** |
| Effet voisin `A−erase-neighbour` : mondes fusionnés vs non fusionnés | **+0.247** vs **+0.0006** |
| Effondrement sous ablation \|abl\|/\|own\| | 0.000 |

Reproduction fidèle du GATE_CERTIFICATE scellé (mêmes chiffres à l'identique) : mon pipeline est faithful, donc
la critique porte sur la mesure, pas sur une divergence d'implémentation.

**Découverte annexe (spec ≠ implémentation).** `TRACKER_SPEC.md` (l.9-11) prescrit une affectation
**un-à-un** (« a component may be claimed by at most one track ; highest overlap wins ») et une **cadence de 5
pas**. `causal_confirm.py::measure_branch` implémente en réalité un `best = max(ents, key=overlap)` **indépendant
par track**, **sans exclusion croisée**, à **cadence 1**. La spec gelée et l'implémentation gelée **se
contredisent** : c'est le mécanisme qui autorise plusieurs tracks à choisir la même composante.

---

## Réponses aux 10 questions

### 1. Les égalités taille/masse/mean_c prouvent-elles que plusieurs tracks lisent la même composante ?

**OUI, quasi-certainement.** `size`, `mass`, `mean_c` sont calculés (l.132-133 du runner) sur
`tracks[i] = mask(best)`, le masque d'**une** composante connexe détectée. Deux composantes physiquement
distinctes ne peuvent pas partager une masse et un mean_c **byte-identiques à 16 chiffres** (masse = somme de ρ
sur des centaines de cellules ; c'est un flottant « continu »). L'égalité exacte impose que
`tracks[a]` et `tracks[b]` pointent vers **le même objet composante** au dernier pas. Les 19 paires prouvent
donc que, au readout final, il y a **≤ 24 composantes réelles pour 39 tracks**. Ceci ne dit pas encore *pourquoi*
(fusion physique, collision d'affectation, wrap) — c'est la Q2.

### 2. Fusion physique, collision d'affectation, wrapping périodique, composante géante/percolante, ou autre ?

**Ma conclusion provisoire : une composante géante percolante (fusion physique) DÉCLENCHE une collision
d'affectation dans un tracker non-bijectif.** Les deux à la fois, avec la fusion physique comme cause racine.
Faisceau de preuves (raw seul) :

- **Percolation** : les composantes finales couvrent 36–52 % d'une grille de 4096 cellules, à partir de
  gouttelettes de 45–96 cellules (1–2 %). Croissance ×20 médiane. Une composante à 52 % de la grille sur une
  topologie périodique **est** percolante.
- **Fusion, pas simple collision entre distinctes** : dans 52005/52010/52012/52017 les **3** tracks pointent la
  **même** composante avec taille/masse/mean_c identiques. Une collision d'affectation « pure » (deux composantes
  distinctes que le tracker confond) n'égaliserait pas la masse. L'égalité impose **une seule** composante.
- **Collision d'affectation en surcouche** : le tracker n'étant pas bijectif (Q0), rien ne l'empêche
  d'assigner cette composante unique à 2–3 tracks au lieu d'en **censurer** les surnuméraires.
- **PAS un wrap périodique** : un wrap ferait d'**une** entité traversant la frontière **une seule** entité
  comptée une fois ; ici deux centroïdes initialement **≥24 cellules apart** (SEP=24.1 min) convergent — ce sont
  bien deux entités initialement séparées qui finissent confondues, pas une entité mal étiquetée.

**Prédiction falsifiable pour la Phase 2** : au dernier pas des mondes « all-3 », les masques fixes des 3 cibles
seront **inclus dans une unique composante connexe périodique**, et cette composante apparaîtra pendant/juste
après le stimulus (voir Q3). Si le replay montrait au contraire des composantes distinctes que le tracker
confond, ou une entité unique dès le snapshot (wrap), je réviserais cette réponse.

### 3. À quel moment cela apparaît-il ?

**Pendant/juste après le stimulus, PAS pendant le washout.** Preuve directe dans le raw : les paires identiques
sur le readout **masque fixe** (integ_fixed) = **0**. Les masques fixes sont figés au **début de l'horizon**
(l.117, après le washout de 40 pas, avant le stimulus). Zéro collision à cet instant ⇒ les 3 régions sont encore
**distinctes** en fin de washout. La fusion survient donc **après** le début de l'horizon — c.-à-d. quand le
stimulus uniforme injecte le nutriment et déclenche la croissance. Corrélat : la branche `intact_long`
(washout naturel 200 pas, moins de croissance résiduelle en amont) présente **8** paires vs **19** pour
`intact` ; la branche `ablate` (canal mémoire coupé, moins d'amplification) **14**. La fusion **corrèle avec la
croissance amplifiée** ⇒ dynamique, pilotée par le stimulus. **Prédiction Phase 2** : premier événement MERGE
détecté dans la fenêtre `t ∈ [début stimulus, début stimulus + ~30]`.

### 4. Le stimulus est-il excessif ?

**OUI, pour l'objectif poursuivi.** `st.N += 0.50` à chaque pas pendant 15 pas = **+7.5 de nutriment uniforme**
ajouté à un champ d'ambiant N0 = 1.0, soit **7.5× l'ambiant** déversé partout en 15 pas. Comme
`uptake ∝ N·ρ·(1+β·σ)·(1+λ₊·m₊)`, cette injection provoque une croissance explosive (×20 médiane) puis
percolation. Le stimulus est **auto-défaisant** : il détruit l'individuation (séparation spatiale des
gouttelettes) qu'il est censé sonder. Ce n'est pas « un peu trop fort » : à 11/13 mondes fusionnés, c'est le
régime **par défaut** du protocole. Note : les amplitudes STIM_AMP/STIM_DUR sont dites « frozen PROBE » calibrées
sur DEV — mais rien dans le PRESEAL n'atteste d'un **critère géométrique de non-fusion** lors de cette
calibration (à vérifier sur `causal_dev_calibration_raw.json`, Phase 6).

### 5. Le contraste intact−erase-target reste-t-il interprétable après fusion ?

**Partiellement — comme empreinte causale SPATIALE, pas comme comportement d'une entité persistante.** Le
contraste apparié annule toujours le commun-mode (corps/environnement identiques entre branches, seule la mémoire
locale diffère), donc la **différence** reste un effet causal réel : « effacer la mémoire au site i réduit
l'uptake intégré sur la région contenant i ». MAIS deux dégâts :

1. **Magnitude tracker-gonflée ~5×** : la région suivie est un blob fusionné géant ; `integ_upt` intègre
   l'uptake de tout le blob. Le chiffre porteur **+2.03 doit être remplacé par la valeur masque-fixe +0.53**.
2. **Localité contaminée** : effacer un **voisin** qui partage le blob affecte la même région de lecture. D'où
   voisin **+0.247** dans les mondes fusionnés contre **+0.0006** dans les non fusionnés. Le « 10 % » poolé
   sous-estime la contamination (moyenne diluée par 2 mondes propres).

Donc : interprétable comme **effet causal local mémoire→feeding** (plus faible), **pas** comme « le nourrissage
d'une gouttelette distincte et persistante ».

### 6. Le masque fixe est-il une preuve d'individuation, ou seulement une empreinte causale spatiale ?

**Seulement une empreinte causale spatiale.** Un masque fixe est une **région d'intérêt figée** à la géométrie
pré-stimulus ; il ne **suit pas une entité**. Un effet `intact−erase` positif sur ce masque prouve que
**zéroïser la mémoire dans ce patch réduit causalement l'uptake intégré là** — localité d'un effet causal.
L'**individuation** exige davantage : qu'une **entité distincte et persistante** porte ET exprime sa propre
mémoire **dans le temps**. Dès que l'entité fusionne dans un blob géant (11/13 mondes), elle **cesse de
persister comme individu**. Le résultat masque-fixe que l'agent précédent invoquait comme « tracker-independence
PASS » établit donc la **localité spatiale d'un effet causal**, **pas** l'individuation causale d'une gouttelette.
C'est la distinction centrale de tout l'incident.

### 7. Quels claims historiques restent valides ?

Classement provisoire (détaillé en Phase 4 après replay) :

- **Stockage local au repos (C-K1)** : **inchangé** — mesuré au repos, avant tout stimulus/fusion.
- **Lecture de l'histoire au repos (C-K2a, dose R²=0.75 ≫ voisin)** : **inchangé** — décodage de features mémoire
  au repos, sans tracker de comportement.
- **Effet causal mémoire→uptake (existence G3a, ablation G3b, double-diss G3e)** : **QUALIFIÉ** — survit comme
  effet **spatial/mondial** (masque-fixe +0.53, 13/13 ; effondrement ablation 0.000 ; ratio double-diss 1.13),
  mais la magnitude +2.03 est un artefact de mesure.
- **Localité (voisin 10 %, G3c)** : **QUALIFIÉ** — propre (≈0) seulement dans les 2 mondes non fusionnés ;
  contaminé (+0.247) dans les fusionnés.
- **Individuation causale d'une gouttelette persistante (G6)** : **SUSPENDU** — l'entité ne persiste pas.
- **« 39/39 gouttelettes »** : **INVALIDÉ** en tant que « 39 entités distinctes » — 24 composantes uniques
  réelles ; le 39/39>0 est gonflé par double-comptage.
- **« Tracking 13/13 robuste »** : **INVALIDÉ** — le tracking n'est pas robuste ; 11/13 mondes ont des tracks
  effondrés (« survie » = les deux tracks verrouillent le même blob, pas une survie individuelle).
- **G6 / bascule ACTIVE-RECONSTRUCTION** : **BLOQUÉ** (Q8).

### 8. ACTIVE-RECONSTRUCTION est-elle encore justifiée ?

**NON — bloquée.** La règle gelée (PROTOCOL_01 §4 ; PRESEAL `G6`) exige G6 = individuation causale = (G1&G2
stockage) **ET** G3 (causal comportemental). G6 est **suspendu** car la confirmation n'a **pas** mesuré des
entités individuées (fusion 11/13). Même le VERDICT_01 recommandait « REPLICATE d'abord » ; l'incident fournit
la raison concrète : le test causal comportemental a été exécuté sur des mondes qui **perdent l'individuation
pendant la mesure**. Bloquée jusqu'à une confirmation **non-fusionnante**.

### 9. Meilleure explication alternative ?

**Le signal « d'individuation comportementale » au readout tracké est en grande partie un ARTEFACT DE MESURE** :
(i) le tracker suit une croissance explosive pilotée par le stimulus (×20) et (ii) collisionne de façon
non-bijective sur une composante percolante partagée — d'où le gonflement ~4.8× et la localité contaminée. Le
**signal authentique résiduel** est une **empreinte causale mémoire→feeding locale et plus petite**
(masque-fixe +0.53, effondrement sous ablation, double-dissociation) — pas de l'individuation d'entité.
*Alternative secondaire à tester* : même l'effet masque-fixe pourrait être en partie confondu par un couplage
temporel croissance↔mémoire local ; le pilote DEV (Phase 6) doit le vérifier avant tout claim positif.

*Position contradictoire assumée* : je **contredis** la lecture forte (« 39/39 gouttelettes individuées,
effet +2.03 ») et je **confirme** une lecture faible (effet causal local mémoire→feeding). Je pourrais
**exonérer** davantage le résultat si la Phase 2 montrait que la quasi-totalité de l'effet intégré s'accumule
**avant** le premier merge (readout majoritairement pré-fusion) ; je durcirais au contraire si l'effet masque-fixe
lui-même s'effondrait sous un tracker bijectif ou disparaissait avant fusion.

### 10. Test minimal qui corrige le problème sans nouvelle physique ?

Trois leviers, **physique inchangée** (uniquement lectures de champ, reset N, ablation existante, sonde uniforme,
zéroïsation mémoire locale) :

1. **Réduire le stimulus jusqu'à absence de fusion**, sélectionné par **critère géométrique** (aucune fusion,
   aucune composante géante, tracking bijectif, survie, localisation) — jamais par la taille de l'effet.
   Candidats : STIM_AMP plus faible, STIM_DUR plus court, impulsion unique, HORIZON plus court.
2. **Tracker bijectif avec censure explicite** : matching biparti de poids maximal ; à la **première** fusion
   d'une cible, **censurer** les trajectoires concernées comme MERGE (ne pas réassigner silencieusement).
3. **Lecture appariée immédiate** : mesurer l'effet `intact−erase` **avant** toute fusion (readout à horizon
   court), pour que le contraste porte sur des entités encore distinctes.

Ces trois éléments constituent le protocole corrigé (Phase 6), **DEV seulement**, **sans ouvrir de nouvelle
famille prospective**.

---

## Position figée avant replay (résumé)

1. **Égalités = même composante** : oui (preuve arithmétique).
2. **Nature** : composante géante percolante (fusion physique) + collision d'affectation non-bijective ; **pas**
   un wrap. À confirmer event-by-event.
3. **Moment** : pendant/après le stimulus (masque-fixe non effondré ⇒ post-début-horizon).
4. **Stimulus** : excessif (auto-défaisant, 11/13 fusionnés).
5. **Stockage/lecture au repos** : inchangés.
6. **Effet mémoire→feeding** : survit comme **empreinte causale spatiale** (~0.53), pas comme individuation.
7. **39/39 & tracking 13/13** : invalidés en l'état ; **24** composantes réelles.
8. **G6 & ACTIVE-RECONSTRUCTION** : suspendus/bloqués.
9. **Aucun nouveau claim positif** issu des diagnostics post hoc (B/C/D). Aucun retrait silencieux de monde.
   Aucun changement de seuil après observation.

*Rien poussé/tagué/publié. main/V4/release intacts. Aucune revendication d'identité, de vie ou d'agence. Ceci
est une position pré-replay, explicitement falsifiable par la Phase 2.*
