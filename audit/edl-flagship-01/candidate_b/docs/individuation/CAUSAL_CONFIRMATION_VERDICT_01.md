# CAUSAL_CONFIRMATION_VERDICT_01 — LCI-CAUSAL-CONFIRMATION-01

*Rapport final. Confirmation prospective scellée exécutée UNE FOIS sur la famille 52001–52024 (PRESEAL 8b2e12d). 13 mondes éligibles / 24 (éligibilité géométrique 54 %, indépendante des outcomes), 39 gouttelettes. Plateforme scellée py3.11.15 / numpy2.2.6 / scipy1.15.3, déterminisme byte-identique (420 flottants, max|Δ|=0). Bootstrap/null seed 20260715.*

## VERDICT EN UNE LIGNE
Le **stockage** et la **lecture** au repos de l'histoire locale propre sont **répliqués** ; et pour la première fois dans ce projet, l'**expression causale comportementale** de la mémoire locale est **ÉTABLIE par un test d'intervention non confondu** (l'effacement de la mémoire propre supprime l'avantage comportemental, l'effacement d'une voisine non, l'ablation du canal l'annule, l'effet survit au washout et à la suppression du résidu de nutriment) — **mais** le **décodage** de la valeur exacte de la dose depuis le comportement reste **indéterminé** (sous-puissant), et le maintien au **turnover profond** n'a pas été re-testé dans cette confirmation (hérité INDÉTERMINÉ pour la dose, NÉGATIF pour l'ordre).

## Résultats par section

**STOCKAGE LOCAL :** RÉPLIQUÉ. C-K1 : DD_mem médian **5951** (≥10), |diag Δm|=0.203, |off Δm|=3.5×10⁻⁵ (<0.05). (OBSERVED)

**LECTURE LOCALE :** RÉPLIQUÉE. C-K2a : décodage own-dose depuis les features mémoire 11-D **R²=0.754** IC-monde [0.693, 0.867], null-intra p=2×10⁻⁴ ; own-order R²=0.303 [0.004, 0.722], p=6×10⁻⁴ ; voisin −0.231. max(dose,order) IC-bas ≫ null-95 ET own−voisin CI>0. (OBSERVED)

**CAUSALITÉ COMPORTEMENTALE :** **ÉTABLIE (G3 PASS, toutes conditions).** Effet propre apparié (intact − erase-target) sur le nutriment intégré : moyenne **+2.03**, IC-monde bootstrap **[+1.63, +2.48]**, **13/13 mondes >0**, **39/39 gouttelettes >0**, SNR-monde **8.93**. Effondrement sous ablation λ→0 : **exactement 0.000**. Localité : effet voisin = **10.4 %** de l'effet propre. Sham (efface zone vide) : 14.8 % (marginal < 15 % ; l'effet propre dépasse le sham **6.8×**, effet corrigé-sham +1.73). Double dissociation reset↔effacement : effet sans standardisation N = +2.29 (ratio 1.13) ⇒ **mémoire, PAS résidu de nutriment**. Survie au washout naturel 200 pas : IC-monde [+1.57, +2.41], 13/13. Indépendance tracker (C-K5, readout masque fixe) : IC-monde [+0.36, +0.73], 13/13. (OBSERVED)

**DÉCODAGE COMPORTEMENTAL (secondaire) :** **INDÉTERMINÉ.** Décodage own-dose depuis le vecteur d'effet comportemental : R²≈0.00 IC [−0.25, +0.39] (sous le null intra à 13 mondes) ; corr(dose, effet propre spécifique) poolée = +0.26 (tendance positive faible). Puissance prévue ~0.10–0.45 à 13 mondes (calibrée DEV : n=9→0.10, n=18→0.75). S'effondre correctement sous ablation (R²=−0.07). ⇒ Le comportement est causalement **façonné** par l'histoire propre (établi), mais n'**encode** pas de façon lisible la **valeur** graduée de la dose à cette puissance. (INFERRED : sous-puissance ; pré-déclaré non-gating.)

**DOSE APRÈS TURNOVER :** **INDÉTERMINÉ (hérité, non re-testé).** Le pipeline scellé de cette mission ne comprenait pas le bloc turnover profond ; toute addition post-PRESEAL est interdite. Valeur héritée de l'audit : R²=0.368 IC [0.14, 0.72], significatif vs null (p=1.2×10⁻³) mais <0.50 non certifié. (Report inchangé.)

**ORDRE APRÈS TURNOVER :** **NÉGATIF (hérité).** R²=−0.659, p=0.92. Cohérent avec la physique : m₋ porté par la composante rapide m1 (e-fold ≈28 pas), non-survivante. (Report inchangé.)

**CONTAMINATION :** Basse. Comportementale : effet voisin 10.4 % de l'effet propre. Stockage : |off Δm| = 3.5×10⁻⁵ (DD 5951). Toutes les cibles à séparation ≥24.1 (min observé). (OBSERVED)

**TRACKING :** Robuste. 13/13 mondes, toutes gouttelettes suivies survivent l'horizon dans toutes les branches. C-K5 : le certificat tient aussi sous readout masque-fixe (sans tracker). (OBSERVED)

**CONTRÔLES :** ablation (0.000), voisin (10 %), double-dissociation (1.13), survie-washout (13/13), tracker-indépendance : **PASS**. Sham : **PASS marginal** (14.8 %). No-drive baseline, mémoire inerte (F), influence appariée : enregistrés. (Tous scellés pré-confirmation ; aucun POST HOC.)

## CLASSIFICATION

**CLAIMS ÉTABLIS (OBSERVED)**
- Individuation de **stockage** local au repos (C-K1) — répliquée sur famille indépendante 52xxx.
- **Lecture** spécifique de l'histoire propre depuis la mémoire (C-K2a, dose R²=0.75 ≫ voisin) — répliquée.
- **Expression causale comportementale locale de la mémoire** (G3) : l'état mémoire stocké **cause** l'augmentation du nourrissage ultérieur de la gouttelette, **spécifiquement à elle** (voisin 10×), **via le canal de lecture** (ablation→0), **non attribuable au résidu environnemental** (double dissociation), **robuste au washout et au tracker**. — **NOUVEAU** : premier test causal comportemental non confondu qui passe.

**CLAIMS QUALIFIÉS (SUPPORTED WITH QUALIFICATION)**
- Le comportement est causalement **façonné** par l'histoire propre, mais le **décodage de la valeur de dose** depuis le comportement n'est **pas** établi (sous-puissant ; tendance +0.26). L'individuation causale est démontrée au sens **interventionnel** (do-effacement), pas au sens **métrologique** (readout gradué).

**CLAIMS NON ÉTABLIS / INDÉTERMINÉS**
- Décodage comportemental gradué de la dose (puissance insuffisante à 13 mondes).
- Maintien de la dose au **turnover profond** (hérité INDÉTERMINÉ ; non re-testé ici).

**CLAIMS FALSIFIÉS**
- Null fort « des gouttelettes coexistantes ne peuvent être individuées localement » : **rejeté** (stockage + causalité).
- **Null de confusion résiduelle** « le signal comportemental est du nutriment résiduel, pas de la mémoire » : **rejeté** par la double dissociation (effet identique avec/sans résidu ; ratio 1.13) et l'effondrement sous ablation. Aucune revendication porteuse falsifiée.

**MEILLEURE EXPLICATION ALTERNATIVE :** Écartée par le design. L'alternative principale — le signal comportemental serait du **résidu de nutriment dose-corrélé** (mon jugement Phase 0 : corr résidu-Δuptake=0.95, résidu 11× la mémoire) — est **directement réfutée** ici : le contraste apparié annule le résidu (commun-mode), l'effet **survit sans standardisation N** (double dissociation, ratio 1.13) et **s'annule sous ablation du canal mémoire** (0.000). Alternative résiduelle restante : le décodage gradué faible pourrait être réel mais sous le seuil de détection (sous-puissance), non un vrai zéro.

## DÉCISION : **ACTIVE-RECONSTRUCTION JUSTIFIED (Cas A) — mais REPLICATE recommandé d'abord ; non lancé (interdit cette mission)**

La règle de décision gelée (PROTOCOL_01 §4) : ACTIVE-RECONSTRUCTION justifiée **seulement** si repos répliqué **∧** G3 passe **∧** C-K3 INDÉTERMINÉ/NÉGATIF. **Les trois tiennent** (Cas A authentique). Donc la **précondition** d'ACTIVE-RECONSTRUCTION-DESIGN-00 est **désormais satisfaite** — contrairement à l'audit précédent (qui échouait G3). **Cependant**, par prudence scientifique et vu (i) le décodage gradué indéterminé, (ii) l'éligibilité observée (54 %) sous l'attendu, (iii) le sham marginal (14.8 %), (iv) le turnover profond non re-testé, je **recommande d'abord une RÉPLICATION indépendante** (nouvelle famille de seeds + bloc turnover profond scellé dans le pipeline causal) **avant** d'engager du compute sur une nouvelle architecture. ACTIVE-RECONSTRUCTION **n'est pas lancée** (interdite dans cette mission).

## POINT DE VUE INDÉPENDANT
J'ai commencé en critiquant la conclusion héritée et en refusant le K2b de l'ADDENDUM (Δuptake en place vs no-drive) comme **confondu à ~95 % par le résidu de nutriment** — quantifié empiriquement (Phase 0). J'ai remplacé le décodage absolu par un **contraste d'intervention apparié** qui annule le résidu par construction et le réfute par double dissociation. Le résultat renverse ma propre hypothèse préférée d'échec (Cas B « mémoire causalement muette ») : **la mémoire N'EST PAS muette** — elle change causalement le comportement, faiblement mais reproductiblement (13/13 mondes) et **spécifiquement** (voisin 10×). Ce que j'ai qualifié à la baisse, c'est le **décodage gradué** : l'individuation causale est **interventionnelle** ici, pas métrologique. L'audit précédent avait raison sur le repos, sur-vendait « causal » ; cette confirmation **établit** le causal au sens propre (do-intervention) tout en gardant le décodage gradué comme question ouverte. Escalader vers ACTIVE-RECONSTRUCTION est maintenant **permis par la règle**, mais je conseille de répliquer et de re-tester le turnover profond d'abord — le vrai levier ouvert n'est pas la persistance mais la **métrologie du readout** (pourquoi le comportement porte l'existence mais pas la valeur graduée).

## PROVENANCE / REPRODUCTIBILITÉ
- Branche `exp/lci-causal-confirmation-01` : Phase 0 `c3dc94e`, PRESEAL `8b2e12d`, RÉSULTATS (ce commit). Parent audit `53fd2b6`.
- **ÉTAT DE MAIN / V4 / RELEASE : INTACTS** (main f3921a4, V4 23b53ae, release inchangés).
- **RIEN POUSSÉ / TAGUÉ / PUBLIÉ / SOUMIS.** V4 non modifié. ACTIVE-RECONSTRUCTION non lancée. Aucune revendication d'identité, de vie ou d'agence.
- Commandes exactes de reproduction :
  ```
  # env scellé
  python -m venv v && v/bin/pip install numpy==2.2.6 scipy==1.15.3 matplotlib==3.10.9
  export PYTHONPATH=<repo>
  # confirmation (déterministe, plateforme fixe) — écrit le raw
  v/bin/python experiments/individuation/causal_confirm.py /tmp/conf.json $(seq 52001 52024)
  # gates + certificat
  v/bin/python experiments/individuation/causal_analyze.py /tmp/conf.json
  # puissance (calibrée DEV) : causal_confirm.py sur 50001-50010 puis power_analysis.py
  ```
- Raw : `experiments/individuation/causal_confirmation_raw.json`. Certificat : `docs/individuation/CAUSAL_CONFIRMATION_GATE_CERTIFICATE_01.json`. Figure : `docs/individuation/CAUSAL_CONFIRMATION_FIGURE_01.png`.
