# CAUSAL_CONFIRMATION_REPRODUCTION_01 — commandes exactes (LCI-CAUSAL-CONFIRMATION-01)

Reproduction complète du test causal comportemental non confondu. Branche `exp/lci-causal-confirmation-01`.
Moteur = PDE réaction-diffusion **chaotique** ⇒ garantie de provenance = **déterminisme byte-identique sur plateforme fixe** (vérifié : 420 flottants, max|Δ|=0), PAS reproduction bit-à-bit inter-plateforme. Seed bootstrap/null figé **20260715**.

## 0. Environnement scellé
```
python -m venv v
v/bin/pip install numpy==2.2.6 scipy==1.15.3 matplotlib==3.10.9   # cf CAUSAL_CONFIRMATION_ENV_01.txt
export PYTHONPATH=<repo-root>
```
Python 3.11.15 utilisé pour la confirmation scellée. Le moteur `edlab` (paquet committé) est requis pour tout run.

## 1. Reproduire l'audit hérité (contexte, numpy seul)
```
cd experiments/individuation
cp exp1_prospective_raw.json /tmp/exp1_prosp.json
cp exp1_maintenance_raw.json /tmp/exp1_maint.json
v/bin/python exp1_reaudit.py       # own-order 0.654, own-dose 0.450, DD 9018, deep-dose 0.368 ...
```

## 2. Sonde Phase 0 (confond résiduel, courbe de washout, effet standardisé) — DEV seuls
```
v/bin/python experiments/individuation/probe_confound_dev.py 50001 50002 50003 50004 50005
# -> residual ΔN ~53% N0, corr(residual,Δuptake)=0.95, washout curve, transplant effect
```

## 3. Calibration DEV du test causal + puissance (DEV 50001–50010 uniquement)
```
# régénère le raw de calibration (déterministe ; = causal_dev_calibration_raw.json, aux branches intact/erase près*)
v/bin/python experiments/individuation/causal_confirm.py /tmp/dev_causal.json $(seq 50001 50010)
v/bin/python experiments/individuation/causal_analyze.py /tmp/dev_causal.json
v/bin/python experiments/individuation/power_analysis.py /tmp/dev_causal.json
# -> existence G3 power=1.00 (n>=6) ; decode power n9=0.10, n18=0.75  (cf PROTOCOL_01 §5, PRESEAL §power)
```
*`causal_dev_calibration_raw.json` (committé pour archivage) a été produit lors de la calibration Phase 3 par un build
antérieur du runner (avant l'ajout des branches erase_ablate / intact_long / integ_fixed). Les branches **intact** et
**erase** — les seules utilisées par la puissance — sont **byte-identiques** au runner scellé (déterminisme vérifié).
Re-générer avec le runner scellé produit un sur-ensemble de clés sans changer les valeurs intact/erase.

## 4. Confirmation scellée (famille 52001–52024, UNE FOIS) — le résultat porteur
```
# raw committé = experiments/individuation/causal_confirmation_raw.json (13/24 mondes éligibles)
v/bin/python experiments/individuation/causal_confirm.py /tmp/conf.json $(seq 52001 52024)
v/bin/python experiments/individuation/causal_analyze.py /tmp/conf.json          # gates K2a / G3 / matrice
v/bin/python experiments/individuation/causal_certificate.py /tmp/conf.json      # certificat + per-seed
v/bin/python experiments/individuation/make_causal_figure.py                     # figure (lit /tmp/causal_confirmation_52xxx.json)
```
Résultats attendus (déterministes sur plateforme scellée) : STOCKAGE own-dose R²=0.754 ; **G3 ÉTABLIE**
(effet propre +2.03 IC-monde [1.63,2.48], 13/13 mondes, ablation 0.000, voisin 10 %, double-diss 1.13, washout survit,
tracker-indépendant) ; décodage gradué INDÉTERMINÉ. Cf `CAUSAL_CONFIRMATION_GATE_CERTIFICATE_01.json` et `..._VERDICT_01.md`.

## 5. Vérification de déterminisme (Phase 3)
```
v/bin/python experiments/individuation/causal_confirm.py /tmp/a.json 50001
v/bin/python experiments/individuation/causal_confirm.py /tmp/b.json 50001
# comparer récursivement tous les flottants -> max|Δ| doit être 0 (byte-identique)
```

## Provenance
- Seeds : DEV 50001–50010 ; CONFIRMATION scellée **52001–52024** (12 FREEZE_SEAL + 12 extension pré-déclarée, justifiée par la puissance, scellée au PRESEAL). Éligibilité géométrique observée 13/24 (indépendante des outcomes).
- Commits : Phase 0 `c3dc94e` · PRESEAL `8b2e12d` · RESULTS `c371346` · (SAUVEGARDE = ce commit). Parent audit `53fd2b6`.
- **main `f3921a4` / V4 `23b53ae` / release : INTACTS. Rien poussé, tagué ni publié.** ACTIVE-RECONSTRUCTION non lancée.
