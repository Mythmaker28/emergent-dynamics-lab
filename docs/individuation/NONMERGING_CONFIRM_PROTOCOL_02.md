# NONMERGING_CONFIRM_PROTOCOL_02 — LCI-CAUSAL-NONMERGING-CONFIRM-02 (frozen)

*Protocole gelé de la confirmation prospective corrigée non-fusionnante. Base `6470513`
(audit/lci-causal-merge-incident-01). Branche `exp/lci-causal-nonmerging-confirm-02`. Gelé AVANT toute donnée
53xxx. `8b2e12d`/`c371346`/`b415503` intacts ; main `f3921a4`, V4, release intacts. Déterminisme byte-identique
(Phase 4). Après PRESEAL : aucun changement de code/gate/seed ; la prospective est exécutée UNE fois.*

## 1. Objectif

Confirmer prospectivement l'expression causale comportementale locale de la mémoire **avec trois gouttelettes
restant réellement distinctes pendant tout l'essai** (correction de l'incident de fusion de
LCI-CAUSAL-CONFIRMATION-01). Unité statistique = **le monde**.

## 2. Probe (sélectionné par géométrie DEV uniquement — jamais par la taille de l'effet)

**Uniforme, amplitude 0.25 ajoutée à N par pas, pendant 5 pas.** Injection cumulée = **1.25 × N0**.
Sélection (`geom_char.py`, 8 mondes DEV, tracker bijectif) : couverture de grille maximale pire-monde **~3.4 %**
(≪ cap 15 %), **insensible à l'horizon** (3.3 % à H40 → 3.7 % à H120), 3 composantes distinctes, 3 cibles
vivantes, aucun MERGE/SPLIT/LOST/AMBIGUOUS. Comparé à 0.25×15 (couverture croissante jusqu'à 7.8 %, marge
horizon-dépendante) et local 0.5×15 (injection 6× plus grande) : 0.25×5 a la meilleure marge stable. La marge
géométrique décide ; l'effet causal n'est jamais consulté pour ce choix.

## 3. Standardisation de N (PAS un washout)

Avant le probe : **reset N := N0** (standardisation de N), puis **40 pas de settle**. Le résidu de nutriment est
retiré **par construction** (pas par décroissance naturelle) et le contraste apparié annule tout reliquat. On
n'appelle **jamais** ceci un « washout » et il n'y a **aucune gate de survie au washout**. (Le washout naturel de
200 pas de l'ancien protocole laissait ~19 % de résidu ; on ne le réutilise pas.)

## 4. Readout

- **Readout individuel PRIMAIRE** : uptake **intégré sur l'horizon [1, 40]** de la composante suivie par le
  **tracker bijectif** un-à-un (`bijective_tracker.py`). Moment exact du readout : somme cumulée de `st.uptake`
  sur le masque de la composante attribuée à la cible, à chaque pas t = 1..40.
- **Readout CONVERGENT (G5)** : uptake intégré sur le **masque fixe** initial (géométrie figée au début de
  l'horizon), tracker-free. C'est un contrôle convergent, **pas** une preuve d'identité longitudinale (il mesure
  une région fixe, pas l'entité mobile).
- **Honnêteté** : ce readout est **directement couplé à m₊ par construction** (`uptake ∝ N·ρ·(1+λ₊·m₊)`). Le
  contraste apparié intact−erase est ce qui le rend causal (le couplage direct et tout résidu s'annulent en
  commun-mode). L'individuation démontrée est **interventionnelle et locale** (do-effacement), pas une preuve de
  comportement distal ni de décodage gradué.

## 5. Branches (par monde)

`intact | erase_j (j=1..3) | sham (efface un patch vide lointain) | ablate (λ→0) | erase_ablate_j`.
Contrastes : own = intact−erase-target ; neighbour = intact−erase-neighbour ; sham = intact−sham ;
ablation (manipulation check) = ablate−erase_ablate-target.

## 6. Censure au niveau MONDE (G0)

Tracker bijectif : matching biparti maximal ; une composante ↔ au plus un track ; censure explicite
MERGE/SPLIT/LOST/AMBIGUOUS ; jamais de réassignation silencieuse ; périodicité correcte (tests 10/10,
`test_bijective_tracker.py`). **Si une des 3 cibles est censurée, ou si <3 composantes distinctes à un pas, ou si
la couverture max ≥ 15 %, dans une des branches de contraste {intact, erase×3, sham}, le monde est G0-INVALIDE
pour l'analyse individuelle primaire.** On ne conserve **jamais** seulement les gouttelettes restantes ; raison +
pas enregistrés ; le monde compte contre la faisabilité ; aucune exclusion silencieuse ; **tous les seeds
apparaissent** au rapport.

## 7. Gates gelés

**G0 — Validité géométrique + faisabilité globale.**
Par monde : 3 cibles éligibles (taille≥45, paires≥24), 3 composantes uniques à chaque pas, aucun
MERGE/SPLIT/LOST/AMBIGUOUS, couverture max < 15 %, 3 cibles vivantes jusqu'à la fin, tracker bijectif.
Faisabilité globale : **mondes G0-valides ≥ 12** ET **fraction non-fusionnante des éligibles ≥ 0.85**. Si la
faisabilité échoue → **FEASIBILITY FAIL** (ni positif ni négatif scientifique).

**G1 — Stockage local.** Matrice d'influence mémoire Cm : DD_mem médian ≥ 10, |off| < 0.05 (diagonale absolue).
Niveau monde.

**G2 — Lecture locale.** Décodage own-dose (primaire) / own-order (secondaire) depuis features mémoire 11-D :
borne inf. worldboot du meilleur > null intra-monde 95 %, ET own ≫ neighbour. Dose pré-déclaré primaire, ordre
secondaire ; aucune bascule post-hoc ; bootstrap par monde (seed 20260715).

**G3 — Causalité comportementale non-fusionnante** (mondes G0-valides seulement). Readout primaire = tracked
bijectif. Conditions cumulatives :
- borne inf. worldboot(own) > 0 ;
- 3 entités distinctes pendant TOUTE la mesure (garanti par G0) ;
- **borne inf. worldboot(own − sham) > 0** (gate appariée ; remplace le ratio fragile <0.15) ;
- **borne inf. worldboot(own − neighbour) > 0** ;
- ablation : |own_abl| / |own| < 0.15 (**manipulation check** attendu par construction, pas preuve isolée) ;
- masque fixe de **même signe, estimation ponctuelle > 0** (convergent ; son IC est reporté en G5) ;
- effet non expliqué par taille/masse/position/résidu N (le contraste apparié les annule commun-mode ; vérifié).

**G4 — Localité.** borne inf. worldboot(own − neighbour) > 0 ; matrice complète ; aucune composante partagée
(garanti par le tracker bijectif) ; pas de double comptage.

**G5 — Robustesse au readout.** tracked (primaire) et masque fixe (convergent) de **même signe** à tous les
mondes ; borne inf. worldboot(own_fixed) > 0 ; écart tracked/fixe **quantifié** (attendu ~1× à ~1.5×, PAS ~4.8×
comme sous fusion).

**G6 — Individuation causale.** PASS **seulement si** G0 (faisabilité) ∧ G1 ∧ G2 ∧ G3 ∧ G4, et **aucune fusion**
dans les mondes analysés. Le **décodage gradué** de la dose depuis le comportement reste **secondaire,
non-gating**.

## 8. Décision (Phase 7)

- **Cas A** : G0, G1, G2, G3(+G4) passent → individuation causale au repos **ÉTABLIE** (interventionnelle,
  readout couplé, honnête) ; réplication/turnover non-fusionnant ensuite ; ACTIVE-RECONSTRUCTION *envisageable*
  mais **non lancée**.
- **Cas B** : stockage passe, causalité échoue → état stocké mais readout causal individuel non établi.
- **Cas C** : faisabilité G0 échoue → probe encore invalide ; aucune conclusion causale (FEASIBILITY FAIL).
- **Cas D** : effet seulement au masque fixe → empreinte spatiale, pas individuation longitudinale.
- **Cas E** : effet disparaît sous protocole non-fusionnant → ancien effet attribuable à la fusion.

*Aucun claim positif tiré du pilote DEV. main/V4/release intacts. Rien poussé/mergé/publié.
ACTIVE-RECONSTRUCTION interdite.*
