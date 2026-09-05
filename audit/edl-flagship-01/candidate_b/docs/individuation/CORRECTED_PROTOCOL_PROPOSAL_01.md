# CORRECTED_PROTOCOL_PROPOSAL_01 — LCI-CAUSAL-MERGE-INCIDENT-01 (Phase 6)

*Proposition de protocole corrigé **non-fusionnant**, à confier à un futur agent après revue. Cette mission
**n'ouvre aucune nouvelle famille prospective** : elle propose seulement la préinscription corrigée, calibrée
sur DEV (seeds 50001–50010), sélectionnée par **critères géométriques uniquement**. `pilot_nonmerging_dev.py`,
`measure_pilot_effect.py`. Rien scellé, rien poussé.*

## Problème résolu

Le probe scellé (stimulus **uniforme** `st.N += 0.50` × **15** pas = +7.5 = 7.5× N0) percole la grille et
fusionne les cibles dans **6/8 mondes DEV** et **11/13 mondes de confirmation**, détruisant l'individuation qu'il
prétend mesurer. Le tracker non-bijectif double-compte les composantes fusionnées.

## Ce qui est CONSERVÉ (inchangé, ces éléments étaient corrects)

- **Snapshot commun** S0 post-histoire ; branches contrefactuelles partageant corps+environnement.
- **intact**, **erase-target**, **erase-neighbour**, **sham** (patch vide), **ablation** (λ→0), **inert**.
- **Standardisation environnementale** (reset N:=N0 avant stimulus commun).
- **Analyse groupée par monde** (unité = monde ; 3 gouttelettes non indépendantes ; bootstrap au niveau monde).
- Double-dissociation reset↔effacement.

## Ce qui est CORRIGÉ

### 1. Probe non-fusionnant (sélection GÉOMÉTRIQUE uniquement)

Sweep DEV (8 mondes éligibles), critères : **aucune fusion**, **aucune collision d'affectation**, **aucune
composante géante** (couverture max < 15 % de la grille), **survie** des 3 cibles, **tracking bijectif**. **9
probes** passent. Sélection (jamais fondée sur la taille de l'effet) :

| Option | Probe | Couverture max (pire monde DEV) | Fusion |
|---|---|---|---|
| **Primaire (recommandée)** | **uniforme, amp=0.25, dur=15** | 7.8 % | 0/8 |
| Alternative A (plus douce) | uniforme, amp=0.25, dur=5 | 3.7 % | 0/8 |
| Alternative B (amplitude pleine, locale) | **local** identique autour de chaque cible, amp=0.5, dur=15 | 5.2 % | 0/8 |
| ~~Scellé (à abandonner)~~ | ~~uniforme, amp=0.5, dur=15~~ | ~~49.9 %~~ | ~~6/8~~ |

Recommandation **uniforme amp=0.25 dur=15** : changement minimal (amplitude divisée par 2), **conserve le
stimulus uniforme commun** (chaque gouttelette reçoit exactement le même stimulus → l'annulation commun-mode du
contraste apparié reste rigoureuse), marge géométrique confortable. L'option locale (B) préserve l'amplitude
pleine sans percolation mais introduit une structure spatiale ; à réserver si un SNR supérieur est nécessaire,
en la déclarant explicitement « commune par cible ».

### 2. Tracker bijectif avec censure explicite (`bijective_tracker.py`)

Matching biparti de poids maximal sur la matrice de recouvrement track×composante ; **une composante ⇒ au plus un
track ; un track ⇒ au plus une composante** ; **censure** à la première fusion (MERGE), division (SPLIT), perte
(LOST) ou ambiguïté (AMBIGUOUS) ; **jamais de réassignation silencieuse** ; géométrie seule (aucun accès à
l'histoire, la mémoire ou l'outcome). Tests : translation périodique, wrapping, croisement sans fusion, fusion
synthétique, division synthétique, perte, ambiguïté — **10/10 PASS**. Une fusion **physique** censure les
trajectoires (MERGE) : le tracker ne « répare » pas la fusion, il la **déclare**.

### 3. Readout primaire tracker-free + lecture pré-fusion

- **Readout primaire = masque fixe** (régions figées à S0), tracker-free, robuste par construction au
  double-comptage.
- Readout tracké **secondaire**, sous **tracker bijectif** avec censure MERGE ; tout monde où une cible est
  censurée avant l'horizon de lecture est **exclu au niveau de la gouttelette** (géométrique, outcome-independent,
  déclaré d'avance) — jamais un retrait silencieux.
- **Gate géométrique préalable** (bloquant) : un monde n'entre dans l'analyse comportementale que si les 3 cibles
  restent **distinctes et vivantes** sur tout l'horizon de lecture (0 merge). Ce gate est **indépendant de
  l'outcome** et scellé avant run.
- Horizon de lecture court possible (lecture appariée immédiate) pour mesurer **avant** toute fusion.

### 4. Readouts comportementaux (honnêtes)

- **uptake intégré** sur horizon court — *directement couplé par construction* (`g ∝ N·ρ·(1+λ₊·m₊)`) ; ce n'est
  pas un readout « distal » indépendant, c'est un readout couplé rendu causal par le **contraste apparié** (le
  résidu et le couplage direct s'annulent en commun-mode). À déclarer explicitement comme tel.
- **croissance pré-fusion** (Δmasse/Δtaille) sur horizon court, secondaire.
- **attractant secondaire / chimiotaxie** comme axe convergent, secondaire.

## Viabilité (OBSERVATIONNEL, DEV, PAS une confirmation)

Sous les probes non-fusionnants, l'effet propre masque-fixe (intact−erase-target) sur DEV vaut **+0.42–0.44,
8/8 mondes>0** — ~même magnitude que le probe scellé fusionnant (+0.44). L'effet mémoire→feeding **n'est donc pas
un artefact de fusion** ; il est mesurable **sans** percolation. **Ceci est une observation sur données DEV déjà
vues ; ce n'est PAS un nouveau claim positif et n'ouvre aucune famille prospective.**

## Gates proposés (à sceller par le futur agent, AVANT tout run 53xxx/…)

1. **G0 géométrique (bloquant, nouveau)** : 0 fusion, 0 collision, couverture max < 15 %, 3 cibles vivantes sur
   l'horizon de lecture, tracking bijectif — sinon le monde/gouttelette est exclu (géométrique, outcome-independent).
2. G1/G2 stockage & lecture au repos (inchangés).
3. **G3 ré-énoncé** : effet propre **masque-fixe** worldboot 2.5 % > 0 ; ablation < 0.15 ; **voisin < 0.35 mesuré
   dans les mondes non-fusionnés** ; sham < 0.15 ; double-diss ; survie washout (avec washout ≈800 pas OU reset
   assumé).
4. **G6** = G1&G2 & G3 **sous G0** (individuation seulement si entités distinctes tout l'horizon).
5. Transplant secondaire **exécuté** ou annonce retirée (Phase 5).

## STOP

Cette proposition **ne lance rien**. La prochaine prospective (famille de seeds neuve + gates ci-dessus scellés)
doit être confiée à **un autre nouvel agent après revue**. ACTIVE-RECONSTRUCTION reste **bloquée** jusqu'à une
confirmation non-fusionnante réussie.

*main/V4/release intacts. Rien poussé/tagué/publié.*
