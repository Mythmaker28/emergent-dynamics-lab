# NONMERGING_CONFIRM_INDEPENDENT_VIEW — LCI-CAUSAL-NONMERGING-CONFIRM-02

*Nouvel agent indépendant. Je critique le protocole proposé (CORRECTED_PROTOCOL_PROPOSAL_01) AVANT toute donnée
nouvelle, en refaisant moi-même la géométrie DEV. Je donne mon opinion et je diverge là où je peux le justifier.
Base `6470513` (tip audit/lci-causal-merge-incident-01). Branche à créer : `exp/lci-causal-nonmerging-confirm-02`.
`8b2e12d`/`c371346`/`b415503` intacts ; main `f3921a4`, V4, release intacts ; rien poussé/mergé/publié ;
ACTIVE-RECONSTRUCTION interdite. Déterminisme byte-identique re-vérifié.*

## 0. Ce que je re-mesure moi-même (géométrie DEV, sans jamais regarder l'effet causal)

Caractérisation géométrique (tracker bijectif, 8 mondes DEV, `geom_char.py`) — couverture de grille maximale
pire-monde et validité (3 composantes distinctes & 3 vivantes & aucun MERGE/SPLIT/LOST/AMBIGUOUS) par horizon :

| probe | injection cumulée | H40 | H60 | H80 | H120 |
|---|---|---|---|---|---|
| uniforme 0.25×15 | 3.75 | 3.5 % ✓ | 4.5 % ✓ | 5.4 % ✓ | **7.8 %** ✓ |
| **uniforme 0.25×5** | **1.25** | 3.3 % ✓ | 3.4 % ✓ | 3.4 % ✓ | **3.7 %** ✓ |
| uniforme 0.20×5 | 1.00 | 3.3 % ✓ | 3.3 % ✓ | 3.3 % ✓ | 3.4 % ✓ |
| local 0.5×15 | 7.50 | 3.5 % ✓ | 4.8 % ✓ | 4.9 % ✓ | 5.2 % ✓ |
| uniforme 0.25×1 | 0.25 | 3.2 % ✓ | 3.2 % ✓ | 3.2 % ✓ | 3.2 % ✓ |

Tous restent valides (cap 15 %). La différence est la **marge** et sa **stabilité en horizon**.

## Réponses aux 10 questions

### 1. Meilleur probe parmi les options DEV ?
**Uniforme 0.25×5.** C'est le meilleur compromis marge/mesurabilité : couverture ~3.3–3.7 % **quasi
insensible à l'horizon** (donc marge robuste ~11 points sous le cap), injection cumulée faible (1.25), et il
conserve un stimulus **uniforme identique** à chaque cible (essentiel pour l'annulation commun-mode du contraste
apparié). Je le préfère indépendamment ; la préférence externe (0.25×5) coïncide, mais ma justification est la
mienne : la **stabilité en horizon** de la marge (3.4 % à H120), que 0.25×15 n'a pas.

### 2. 0.25×15, 0.25×5, ou local commun ?
**0.25×5.** Contre 0.25×15 : sa couverture **croît avec l'horizon** (jusqu'à 7.8 % à H120) → marge plus étroite
et dépendante du moment de lecture (fragile). Contre local 0.5×15 : injection **6× plus grande** (7.5) et
structure spatiale non-uniforme qui complique l'argument commun-mode ; marge un peu moins bonne (5.2 %). 0.25×5
domine : plus faible injection, marge stable, uniforme.

### 3. Quel choix maximise la marge géométrique sans utiliser la taille de l'effet ?
Sur la **marge géométrique pure**, plus le probe est doux, meilleure est la marge : 0.25×1 (3.2 %) > 0.20×5
(3.4 %) > 0.25×5 (3.7 %). Mais la marge n'est pas le seul critère géométrique : le probe doit délivrer un
**stimulus commun défini et non-trivial** pour qu'il y ait un comportement à suivre (survie + tracking + une
réponse d'uptake existante sont des critères géométriques/dynamiques, pas l'effet causal). Je fixe donc la borne
**inférieure** du probe par « injection commune non-triviale (cumul ≥ ~1) », et parmi ces probes je choisis la
**meilleure marge** → **0.25×5** (cumul 1.25, marge 3.7 % stable). Je ne consulte jamais la taille de l'effet
causal pour ce choix.

### 4. Readout individuel primaire : tracker bijectif ou masque fixe ?
**Tracker bijectif — je concours avec la proposition, et je corrige ma propre position antérieure.** Dans l'audit
précédent j'avais mis le masque fixe en primaire ; c'était une erreur conceptuelle pour un claim
d'**individuation** : l'individuation concerne une **entité mobile persistante**, or le masque fixe mesure une
**région spatiale figée** — il peut rater une gouttelette qui se déplace (empreinte spatiale ≠ identité
longitudinale). Le readout **suivi bijectivement** est le seul qui suive l'entité. Le masque fixe devient un
**contrôle convergent tracker-free** (G5).
**Raffinement indépendant (divergence mineure)** : je refuse d'ériger « masque fixe, borne inférieure worldboot
>0 » en **condition dure de G3**. Une entité mobile peut quitter son patch initial → le masque fixe est alors un
**sous-estimateur conservateur**, pas une condition de validité. Je place donc en G3 la condition convergente
« masque fixe **de même signe, estimation ponctuelle >0** » et je reporte son IC worldboot en **G5** (robustesse),
sans en faire un pass/fail primaire. Le primaire reste le tracker bijectif.

### 5. Monde où une seule cible fusionne ou se perd ?
**Monde INVALIDE pour l'analyse individuelle primaire.** Jamais conserver seulement les gouttelettes restantes
(biais de survie / sélection post-hoc). Enregistrer raison + pas ; le monde **compte contre la faisabilité
géométrique** ; aucune exclusion silencieuse ; tous les seeds apparaissent au rapport. Je concours pleinement.

### 6. Proportion minimale de mondes valides ?
Gate de faisabilité en **deux volets** : (a) **fraction de non-fusion parmi les mondes éligibles ≥ 0.85** — si le
probe fait fusionner >15 % des mondes éligibles, il reste trop agressif → FEASIBILITY FAIL ; (b) **nombre absolu
de mondes G0-valides ≥ N_min** fixé par la puissance (Phase 3). Les deux doivent passer. (Justification de 0.85 :
DEV donne 8/8 = 100 % non-fusion à 0.25×5 ; exiger ≥85 % laisse une marge d'échantillonnage tout en refusant un
probe qui fusionnerait sensiblement.)

### 7. Nombre de seeds ?
Découle du calcul de puissance (Phase 3), pas d'un chiffre imposé. Estimation a priori : éligibilité historique
54–75 %, validité G0 attendue ~élevée (≥85 % des éligibles), unité = monde. Pour ~14–16 mondes valides avec
puissance ≥0.8 sur `own−sham` et `own−neighbour`, à un taux valide/seed ~0.5–0.6, il faut ~28–36 seeds. Je
**scellerai ~40 seeds (53001–53040)** si le calcul le confirme, cap inclus — famille et cap figés avant tout run,
aucune extension post-outcome.

### 8. Le sham historique <0.15 est-il une bonne gate ?
**NON.** C'est un **ratio de deux quantités bruitées** (il était marginal à 0.148), instable et peu
interprétable. Je le remplace par une gate **appariée** : **borne inférieure worldboot de (own − sham) > 0**.
C'est le bon test (le sham partage corps/environnement ; la différence appariée isole l'effet mémoire, et son IC
au niveau monde est directement interprétable). Je concours avec la proposition ; justification figée **avant**
les données.

### 9. Washout naturel nécessaire si N est standardisé ?
**NON.** Si N est explicitement remis à N0 (**standardisation de N**), le résidu est retiré **par construction**
et le contraste apparié annule tout reliquat. Un washout naturel de ~800 pas serait non seulement inutile mais
**risqué** : 800 pas d'évolution libre dans un champ proche de la percolation pourraient **fusionner ou déplacer**
les gouttelettes avant même la mesure (l'inverse du but). Je fige donc **Option A : standardisation de N**
(appelée ainsi, pas « washout »), contraste apparié conservé. Pas de gate « survie au washout » en primaire.
Un contrôle naturel **partiel** pourra être reporté honnêtement comme tel, sans prétendre supprimer le résidu.

### 10. Quel résultat justifierait réellement ACTIVE-RECONSTRUCTION ?
**Uniquement le Cas A authentique** : (i) faisabilité G0 globale passe (assez de mondes **non-fusionnants**
valides) ; (ii) stockage & lecture au repos répliqués ; (iii) causalité comportementale **non-fusionnante**
passe — `own−erase-target` worldboot >0, **3 entités distinctes pendant TOUTE la mesure**, own > neighbour, own
> sham (IC apparié >0), ablation compatible avec 0, masque fixe convergent de même signe, effet non expliqué par
taille/masse/position/résidu, stable entre mondes. C.-à-d. **individuation causale d'entités persistantes**, pas
une empreinte spatiale (Cas D) ni un stockage muet (Cas B). Et même alors : **répliquer + re-tester le turnover
profond non-fusionnant d'abord** ; non lancée ici. Un effet qui **disparaît** sous protocole non-fusionnant
(Cas E) attribuerait l'ancien résultat à la fusion.

## Décisions figées (avant données)

- **Probe : uniforme 0.25×5** (amplitude ajoutée/pas = 0.25 ; nombre de pas = 5 ; injection cumulée = 1.25× N0 ;
  horizon comportemental à finaliser par la puissance, candidat H=40 ; readout = uptake intégré sur [1,H] de la
  composante suivie bijectivement).
- **Standardisation de N** (reset N:=N0), pas de washout ; contraste apparié.
- **Readout primaire = tracker bijectif** ; masque fixe = contrôle convergent (G5).
- **Sham gate = worldboot(own − sham) borne inf. >0** (pas de ratio).
- **Ablation = manipulation check** (≈0 attendu par construction ; pas une preuve causale isolée).
- **Transplant : RETIRÉ de cette mission** (je n'annonce pas un contrôle non exécuté ; travail futur possible).
- **Censure au niveau monde** ; faisabilité séparée ; famille 53xxx neuve, scellée avec cap avant tout run.

*Aucun claim positif tiré du pilote DEV. main/V4/release intacts. Rien poussé/mergé/publié. Aucune revendication
d'identité, de vie ou d'agence.*
