# Reproducibility Manifest

## Environment
Python 3 + numpy 2.2, scipy 1.15, matplotlib (pip --break-system-packages). Frozen scaffold engine blob 7c91b91.
Run with `PYTHONPYCACHEPREFIX=/tmp/pyc python3 -B`, `PYTHONPATH=$REPO:$REPO/results/wd01_phasec` (candidate engines).

## Branch / commit registry (all isolated; main untouched f3921a4; not pushed)
HMC 25c419a | HSI 709f963 | IOM-00 0ea1250 | MCM-00 5841b9b | WD-01 PhaseB 9a39f8c |
WD-01 PhaseC seal be08738 / result a07b95b | SMC-01 seal d0f47b6 / result 3dc8c35 |
DMM-01 seal 5bd46e7 / result 49e96ad | H2-CERT-01 seal 5e1196f / result 1f8f789 | Consolidation: this commit.

## Sealed prospective registry (SHA-256, generated before selection, executed once)
- WD-01 Phase C: c6d0cd3c5b82aa122ac7e5649888fbc53ca6faa8db68e2c1b48863e87fb9e202 (dev 34001-3 / prosp 35001-3)
- SMC-01:        2d6986fe2499cb52fdc309f5b1867cff56cb04b4bd7884633c4c2a148d5792ef (dev 36001-3 / prosp 36501-3)
- DMM-01:        923d8890ea25ab5a136078486f282ad8e07f4cdbaa125da40ef930f5bb8a00b6 (dev 37001-3 / prosp 37501-3)
- H2-CERT-01:    4265b98cacb705a7bea56a2e0a5bbe36e10fec3d977e7da6e655037189193fee (prosp 38501-4)
Seed-family disjointness: 32xxx(MCM dev) 33xxx(MCM prosp) 34-35xxx(PhaseC) 36xxx(SMC) 37xxx(DMM) 38xxx(H2CERT) — all disjoint.

## Raw-data index
results/sc_mcm/certificate.json; results/wd01/wd01_diag_raw.pkl;
results/wd01_phasec/phasec_{dev,prospective_,causal_transplant_,causal_inplace_}raw.pkl;
results/smc01/smc01_{fields,turnover,prospective_storage}_raw.pkl;
results/dmm01/dmm01_{phaseA,pooled_turnover,prospective_turnover}_raw.pkl;
results/h2cert/h2cert_{pilot,sealed}_raw.pkl.

## Reproduction commands (per experiment; runners committed beside data)
WD-01: results/wd01/run_diag.py -> analyze.py -> figure.py
PhaseC: results/wd01_phasec/{dev_runner,prosp_runner,causal_runner,causal_inplace}.py
SMC-01: results/smc01/{fields_runner,turnover_runner,prosp_storage}.py
DMM-01: results/dmm01/{phaseA,pooled,prosp}.py
H2-CERT: results/h2cert/{pilot,cert}.py
Determinism: seeds fixed in each manifest; PulseChase passive; ablation params unit-tested (H2-CERT-01).

## Figures (paper set; each traces to committed raw + script)
results/wd01/wd01_diagnostic.png; results/wd01_phasec/phasec_figure.png; results/smc01/smc01_figure.png;
results/dmm01/dmm01_figure.png; results/h2cert/h2cert_figure.png; docs/paper/paper_claim_ladder.png.
