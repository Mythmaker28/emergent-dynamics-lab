# NONMERGING_CONFIRM_VERDICT_02 — LCI-CAUSAL-NONMERGING-CONFIRM-02

*Rapport final. Confirmation prospective corrigée **non-fusionnante**, scellée (PRESEAL `9b7580bc`), exécutée
UNE fois sur la famille 53001–53032. Plateforme scellée py3.11.15/numpy2.2.6/scipy1.15.3, déterminisme
byte-identique (Phase 4). Bootstrap/null seed 20260715. Nouvel agent indépendant : j'ai d'abord critiqué et
divergé du protocole proposé (Phase 0), puis gelé, puis exécuté.*

## VERDICT EN UNE LIGNE
**CAS A — sur un protocole non-fusionnant où les trois gouttelettes restent réellement distinctes tout l'essai
(23/23 mondes valides, 0 fusion), l'effacement de la mémoire propre d'une gouttelette réduit causalement et
spécifiquement SON PROPRE nourrissage (own +0.223 IC-monde [0.193, 0.258], 23/23 ; voisin et sham ≈ 0 ; ablation
0.000 ; masque-fixe convergent +0.207, ratio 1.08×), le stockage et la lecture au repos étant répliqués (DD 2590 ;
dose R² 0.69 ≫ voisin) — G0–G6 PASS : individuation causale ÉTABLIE au sens INTERVENTIONNEL/LOCAL, avec le readout
honnêtement déclaré couplé à m₊ ; décodage gradué INDÉTERMINÉ ; ACTIVE-RECONSTRUCTION envisageable mais NON lancée
(répliquer + re-tester le turnover non-fusionnant d'abord).**

## Champs
- **PROBE :** uniforme 0.25 × 5 pas (injection cumulée 1.25 × N0) ; standardisation de N (reset N:=N0, pas de
  washout) ; horizon 40 ; readout primaire = uptake intégré [1,40] sur la composante suivie **bijectivement**.
- **FAMILLE :** 53001–53032 (32 seeds scellés, cap 32, exécutée une fois ; 53xxx neuve).
- **MONDES INITIALEMENT ÉLIGIBLES :** 23/32 (72 % ; géométrique, outcome-independent).
- **MONDES G0 VALIDES :** 23/23 éligibles (100 % ; couverture max 1.2–5.6 % ≪ 15 %).
- **FUSIONS :** 0. Aucune composante ≥15 % ; 3 composantes distinctes à chaque pas dans toutes les branches.
- **TRACKING BIJECTIF :** 23/23 ; aucun MERGE/SPLIT/LOST/AMBIGUOUS ; aucune composante partagée (tests 10/10).
- **STOCKAGE :** PASS (G1 ; DD_mem 2590, |off| 7×10⁻⁵).
- **LECTURE :** PASS (G2 ; own-dose R² **0.691** IC>null95 0.153 ; voisin −0.014 ; dose primaire pré-déclaré).
- **EFFET OWN :** **+0.223** IC-monde worldboot **[0.193, 0.258]**, **23/23 mondes >0**, 69/69 gouttelettes >0.
- **SHAM :** ≈ 0 (byte-niveau) ; gate appariée borne inf. worldboot(own−sham) = +0.193 > 0 (PASS ; pas de ratio).
- **VOISIN :** ≈ 0 (moyenne −7×10⁻⁶) ; borne inf. worldboot(own−voisin) = +0.193 > 0 — **localité parfaite**.
- **ABLATION :** **0.000** — |own_abl|/|own| = 0 (**manipulation check** attendu par construction ; pas une preuve isolée).
- **MASQUE FIXE :** convergent **+0.207** IC-monde [0.180, 0.234], **même signe 23/23**, ratio tracked/fixe **1.08×**
  (PAS 4.8× comme sous fusion).
- **CAUSALITÉ :** **ÉTABLIE** — non-fusionnante, own-spécifique, voisin-null, sham-null, effondrement sous ablation,
  masque-fixe convergent. Sens **interventionnel** (do-effacement) sur un **readout couplé**.
- **INDIVIDUATION :** **G6 PASS** — individuation causale d'entités persistantes distinctes.
- **DÉCODAGE GRADUÉ :** **INDÉTERMINÉ** (secondaire, non-gating ; corr(dose monde, own) = +0.17). Individuation
  interventionnelle, pas métrologique.
- **TURNOVER :** non re-testé ici (hérité INDÉTERMINÉ dose / NÉGATIF ordre) ; re-test non-fusionnant recommandé.
- **ACTIVE-RECONSTRUCTION :** envisageable (Cas A) mais **NON lancée** ; répliquer (famille indépendante) + turnover
  profond non-fusionnant d'abord ; interdite cette mission.
- **CLAIMS ÉTABLIS :** stockage au repos ; lecture au repos ; **expression causale comportementale non-fusionnante,
  own-spécifique, sur 3 entités distinctes persistantes** (interventionnelle).
- **CLAIMS QUALIFIÉS :** le readout est **directement couplé à m₊** (pas un comportement distal/émergent) ; le
  **décodage gradué** de la dose depuis le comportement n'est pas établi.
- **CLAIMS INVALIDÉS :** aucun nouveau (l'ancien +2.03 / « 39/39 » restait corrigé par l'erratum de l'audit ;
  rien n'est ré-invalidé ici).
- **POINT DE VUE INDÉPENDANT :** J'ai **critiqué et divergé** du protocole proposé (probe choisi sur ma propre
  géométrie pour sa marge stable en horizon ; masque fixe **rétrogradé** de gate G3 dure à contrôle convergent G5
  car il rate une entité mobile ; sham-gate ratio remplacé par IC apparié ; transplant **retiré**). Le résultat
  **réfute le Cas E** (l'effet n'est **pas** un artefact de fusion : il persiste, propre et convergent
  tracked/fixe, **sans** aucune fusion) et confirme, honnêtement qualifié, une individuation causale
  interventionnelle. Je **n'over-vends pas** : c'est un readout couplé, pas une preuve de comportement distal ni de
  métrologie graduée.
- **PROVENANCE :** PRESEAL `9b7580bc` (off `6470513`) ; RÉSULTATS = ce commit (distinct). `8b2e12d`/`c371346`/
  `b415503`/`53fd2b6` non réécrits.
- **MAIN/V4/RELEASE :** INTACTS (main `f3921a4`).
- **RIEN POUSSÉ/MERGÉ/PUBLIÉ :** rien poussé, tagué, mergé, publié, soumis ; V4 non modifié ;
  ACTIVE-RECONSTRUCTION non lancée ; aucune revendication d'identité, de vie ou d'agence.

## Rapport Observed / Inferred / Falsified / Speculative

**OBSERVED (mesuré, reproductible byte-identique).** 23/32 éligibles ; 23/23 G0-valides non-fusionnants
(couverture ≤5.6 %) ; own +0.223 [0.193,0.258] 23/23 ; sham & voisin ≈0 ; ablation 0.000 ; masque-fixe +0.207
[0.180,0.234] 23/23, ratio 1.08× ; DD_mem 2590 ; dose R² 0.691 ≫ voisin −0.014.

**INFERRED (conclusion des observations).** La mémoire locale stockée **cause** une modification own-spécifique du
nourrissage de chaque gouttelette **distincte et persistante** (interventionnel) : l'effacement propre l'abaisse,
l'effacement du voisin/sham ne fait rien, l'ablation du canal l'annule — sur des entités qui **ne fusionnent
jamais**. G6 individuation causale PASS.

**FALSIFIED (rejeté par ces données).** (i) **Cas E** « l'ancien effet causal était un artefact de
fusion/percolation » : **rejeté** — l'effet subsiste, propre, sous un protocole 0-fusion. (ii) Null fort « des
gouttelettes coexistantes ne peuvent être individuées causalement sans fusionner » : **rejeté**.

**SPECULATIVE (non établi ici).** Décodage métrologique gradué de la dose depuis le comportement ; survie au
turnover profond non-fusionnant ; tout comportement **distal/émergent** au-delà du nourrissage couplé ;
généralisation hors plateforme. Ces points restent ouverts et guident la suite (réplication + turnover
non-fusionnant, à confier à un autre agent).

## Reproduction
```bash
python -m venv venv && venv/bin/pip install numpy==2.2.6 scipy==1.15.3 matplotlib==3.10.9
export PYTHONPATH=$PWD; mkdir -p work
venv/bin/python experiments/individuation/test_bijective_tracker.py                       # 10/10
venv/bin/python experiments/individuation/nonmerging_confirm.py work/nm_confirm_raw.json $(seq 53001 53032)
venv/bin/python experiments/individuation/nonmerging_analyze.py work/nm_confirm_raw.json docs/individuation/NONMERGING_CONFIRM_CERTIFICATE_02.json
venv/bin/python experiments/individuation/make_nm_figure.py
```

## Commande PowerShell de push (À EXÉCUTER MANUELLEMENT — aucun push automatique)
```powershell
cd "C:\Users\tommy\Documents\ising v3"
git push origin exp/lci-causal-nonmerging-confirm-02:exp/lci-causal-nonmerging-confirm-02
```
