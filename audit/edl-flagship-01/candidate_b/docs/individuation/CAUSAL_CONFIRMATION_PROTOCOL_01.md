# CAUSAL_CONFIRMATION_PROTOCOL_01 — LCI-CAUSAL-CONFIRMATION-01 (frozen before any prospective data)

*Protocole gelé du test causal comportemental non confondu. Étend/répare CONFIRMATION_PREREGISTRATION_ADDENDUM_01. À committer AVANT le premier seed prospectif ; aucun paramètre modifiable après ouverture. Calibré uniquement sur DEV 50001–50010. Plateforme scellée : Python 3.11.15, numpy 2.2.6, scipy 1.15.3 (PDE chaotique → déterminisme byte-identique sur plateforme fixe, vérifié 420 flottants max|Δ|=0).*

## 1. Critique du protocole candidat, et ce que je change

Le protocole candidat (in-place : snapshot → branches contrefactuelles → standardiser N,c → washout → stimulus commun → réponse) est bon dans l'intention mais **confondu tel quel** et **incomplet** :

1. **Le readout doit être un CONTRASTE apparié, pas un décodage absolu.** Le signal comportemental « en place » (Δuptake vs no-drive) est empiriquement à **~95 % du nutriment résiduel** (corr 0.95 ; résidu ≈11× la mémoire). Je remplace le décodage absolu par le **contraste apparié intact − erase-target** : les deux branches partent du **même snapshot** (ρ, U, V, N, c identiques) et ne diffèrent QUE par le champ mémoire local de la cible. Le résidu, la taille, la masse, la position sont **communs-mode et s'annulent** dans la différence. C'est ce qui rend le test non confondu.
2. **Ne PAS resetter c.** c pilote l'advection chimiotactique (χ) et la cohésion ; un reset brutal déplace la gouttelette (perturbe la mesure). Je **standardise seulement N** (N:=N0 uniforme ; n'affecte ni ρ, ni m, ni c) et je laisse c partagé depuis le snapshot. Robustesse additionnelle par **washout naturel long** (200 pas, aucun reset) où N ET c relaxent seuls.
3. **Coordonnée figée par la physique.** Oubli rapide m1 (η_d1=0.35, e-fold ≈28 pas) vs lent m2 (η_d2=0.006, e-fold ≈1666). Tout washout oublie m1 ⇒ **DOSE (m₊, m2 lent) = PRIMAIRE ; ORDRE (m₋, m1 rapide) = SECONDAIRE**. Déclaré avant observation, cohérent avec le turnover profond (ordre négatif).
4. **La certification est une MATRICE d'interventions à effet ABSOLU, jamais un ratio seul** (contrainte de mission respectée) : effet propre absolu + IC groupé par monde, effondrement sous ablation, nullité voisin/sham, double dissociation reset↔effacement, survie au washout.

## 2. Design gelé

**Bloc STOCKAGE (verbatim exp1_prospective).** 1 monde/seed, warm 800 ; K=3 cibles (size≥45, pairwise≥24, géométrique, indépendant des outcomes) ; histoires locales gaussiennes σ=0.8·r_g, 2 phases×60 pas, amp∈[0.005,0.035] i.i.d. par cible (rng(seed)) ; features mémoire 11-D lues en place ; matrices d'influence Cm (|Δm₊|), Cu (|Δuptake|). Schéma de sortie superset de `exp1_prospective_raw.json` → consommé par `exp1_reaudit.py` pour K2a et C-K1.

**Bloc CAUSAL COMPORTEMENTAL (nouveau, non confondu).** Depuis le snapshot post-histoire commun S0 (après settle 120), branches contrefactuelles ; chacune = copie de S0 + une intervention `do` locale, puis standardisation, washout, **stimulus uniforme commun** (N += 0.50 pendant 15 pas — sonde gelée), puis **réponse comportementale intégrée sur horizon 120** (nutriment consommé par gouttelette suivie + croissance), gouttelette suivie par le **tracker overlap gelé** (θ=0.1) ET lue aussi sur **masque fixe** (readout sans tracker, C-K5).

Branches (par seed) :
| code | branche | rôle |
|---|---|---|
| A | intact, N standardisé | référence |
| B | sham : efface une zone VIDE (hors gouttelette) | contrôle de procédure |
| C_j | efface la mémoire de la gouttelette j (Mf[:,région_j]=0) | erase-target (i=j) & erase-neighbour (i≠j) |
| E | ablation du canal (λ₊=λ₋=0), mémoire intacte | spécificité du canal de lecture |
| E∘C_j | efface j SOUS ablation | effondrement propre (doit ≈0) |
| F | mémoire inerte (m gelée depuis l'écriture) | mémoire figée vs dynamique |
| A_res, C_j^res | intact / erase SANS standardisation N (résidu gardé) | double dissociation reset↔effacement |
| A_long, C_j^long | intact / erase, washout naturel 200 pas, sans reset | survie au washout (G3) |
| ND | baseline sans-drive standardisée | référence comportementale nulle |

Standardisation N : `st.N := N0` uniforme (N seulement ; ρ, U, V, c, Mf intacts). Washout court WASHOUT_B=40 (transitoire) ; washout long WASHOUT_LONG=200 (résiduel ΔN<~1 % N0 par la courbe DEV, aucun reset).

**Effets préinscrits** (par gouttelette i, effet = intact − intervention, sur uptake intégré ; masse/taille/mean_c en axes secondaires) :
`eff_own_i = A_i − C_i[i]` ; `eff_own_abl_i = E_i − (E∘C_i)[i]` ; `eff_sham_i = A_i − B_i` ; `eff_neigh_i = moy_{j≠i}(A_i − C_j[i])` ; `eff_res_i = A_res_i − C_i^res[i]` ; `eff_long_i = A_long_i − C_i^long[i]`.

## 3. Classification des coordonnées (figée, pré-observation)

DOSE = **PRIMAIRE** (portée par m2 lent, survit au washout). ORDRE = **SECONDAIRE** explicitement justifié (portée par m1 rapide, non-survivant). Aucune bascule post-hoc. La certification causale porte sur la dose ; l'ordre est rapporté (stockage K2a) et, comportementalement, attendu non-significatif après washout.

## 4. Gates figés (évalués une fois, jamais ajustés) — seuils calibrés sur DEV

| gate | condition (gelée) | DEV observé (marge) |
|---|---|---|
| **G1 / C-K1** stockage | DD_mem ≥ 10 **et** médiane\|off Δm\| < 0.05 **et** \|diag Δm\| > 3× base | DD 9018, off 1.8e-5, diag 11.4× |
| **G2 / C-K2a** lecture stockage | max(dose,order) storage-decode IC-bas > null-intra-95 **et** own−neigh CI>0 | dose R² 0.61 p=2e-4 |
| **G3 / C-K2b** expression causale comportementale (PRIMAIRE) | **TOUTES** : (a) eff_own par-monde, IC-bas bootstrap-monde 2.5 % **> 0** ; (b) \|eff_own_abl\|/\|eff_own\| < **0.15** ; (c) \|eff_neigh\|/\|eff_own\| < **0.35** ; (d) \|eff_sham\|/\|eff_own\| < **0.15** ; (e) double diss. : eff_res > 0, même signe, 0.5 < eff_res/eff_own < 2.0 ; (f) survie washout : eff_long > 0 | (a) 8/8>0, SNR 5.3 ; (b) 0.000 ; (c) 0.092 ; (d) 0.007 ; (e) 1.047 ; (f) >0 |
| **G3-decode** (SECONDAIRE, rapporté non-gating) | behavioural own-dose LOGO R² IC-bas > null-intra-95 | R²=0.25 (sous-puissant à n≈9, cf §5) |
| **G4 / C-K4** non-trivialité | eff_own non expliqué par size/mass/position/edge/env-local (déjà communs-mode dans le contraste apparié ; de plus baseline-decode dose ≈0) | contraste annule size/mass/pos |
| **G5 / C-K5** indépendance tracker | verdicts G1–G4 inchangés sous le readout **masque fixe** (sans tracker) | eff_own_fixed >0, même ordre |
| **G4-turnover / C-K3** dose profonde | own-dose deep IC-bas > 0.50 à M≤0.5 ; sinon INDÉTERMINÉ ; FALSIFIÉ seulement si règle de falsification préinscrite passe | (hérité : 0.368 [0.14,0.72] INDÉTERMINÉ) |
| **G6** individuation causale | passe **seulement si** G1∧G2 (stockage spécifique) **ET** G3 (expression causale comportementale) | — |

**Règle de décision (gelée).** Réplique le repos ssi C-K1∧C-K2a∧C-K4∧C-K5 sur la famille. Expression causale comportementale établie ssi de plus **G3**. Maintien dose ssi C-K3. ACTIVE-RECONSTRUCTION justifiée **seulement** en Cas A authentique (repos répliqué ∧ G3 passe ∧ C-K3 INDÉTERMINÉ/NÉGATIF) — et **interdite dans cette mission** de toute façon.

## 5. Puissance et famille scellée

Analyse de puissance au niveau monde (rééchantillonnage des 8 mondes DEV éligibles, éligibilité observée 80 %) :

| n mondes | P(G3 existence : eff_own par-monde IC-bas>0) | P(G3-decode : LOGO IC-bas > null-95) |
|---|---|---|
| 6 | 1.00 | 0.01 |
| 9 | 1.00 | 0.10 |
| 18 | 1.00 | 0.75 |

⇒ **G3 (primaire, intervention) est pleinement alimenté dès n≥6** ; les 52001–52012 (~9 mondes éligibles) suffisent pour la certification causale primaire. **G3-decode (secondaire)** exige ~18 mondes. Compute bon marché ⇒ je **scelle une extension préinscrite justifiée par la puissance** : famille de confirmation **52001–52024** (les 12 scellés d'origine + 12 pré-déclarés ici, AVANT tout run), donnant ~19 mondes éligibles → decode secondaire alimenté à ~0.75 **et** primaire robuste. Aucune extension après observation ; l'éligibilité géométrique est indépendante des outcomes.

## 6. Vérifications (Phase 3 DEV, auto-autorisée)

- **Déterminisme** : 50001 exécuté 2×, pipeline complet → **420 flottants, max\|Δ\|=0 (byte-identique)**.
- **Isolation causale** : standardisation ne touche que N (ρ, U, V, c, Mf inchangés) ; erase ne zère que la région cible (voisines intactes → eff_neigh 0.09) ; ablation → eff_own_abl **exactement 0.000** ; effet survit au washout 200 (eff_long>0) ; double dissociation (eff_res≈eff_own, ratio 1.047 ⇒ mémoire, pas résidu).
- **Éligibilité DEV** : 8/10 (50008, 50010 <K, géométrique).

## 7. Provenance / seeds / exclusions / environnement

- Branche `exp/lci-causal-confirmation-01` depuis 53fd2b6. main f3921a4 / V4 23b53ae / release intacts. Rien poussé.
- DEV 50001–50010 (calibration, OBSERVED). **CONFIRMATION scellée 52001–52024** (12 d'origine FREEZE_SEAL + 12 extension pré-déclarée ; jamais inspectés ; aucune donnée/cache/log préexistante — vérifié).
- Exclusion : seed retenu ssi ≥K=3 cibles géométriquement éligibles (size≥45, pairwise≥24) ; raison d'exclusion enregistrée par seed. Indépendant des outcomes.
- Pipeline unique : `experiments/individuation/causal_confirm.py` (runner) + `causal_analyze.py` (analyse/gates) + `power_analysis.py`. Bootstrap/null/permutation seed **20260715**. Environnement scellé dans le manifeste PRESEAL.

*Aucune nouvelle physique : seulement lectures de champs, reset de N, ablation existante (λ→0), sonde nutriment uniforme, mise à zéro locale de la mémoire. Aucune revendication d'identité, de vie ou d'agence.*
