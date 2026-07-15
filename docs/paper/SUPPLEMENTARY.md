# Supplementary Materials

## S1. Experiment map (branches, commits, verdicts)
See docs/paper/EXPERIMENT_MAP.md. Chain: HMC 25c419a; HSI 709f963; IOM-00 0ea1250; MCM-00 5841b9b;
WD-01 Phase B 9a39f8c; Phase C a07b95b; SMC-01 3dc8c35; DMM-01 49e96ad; H2-CERT-01 1f8f789;
paper 112aace; observer 6891ef8; tracker audit 568af39; post-incident 7afd6e4.

## S2. Sealed prospective registry (SHA-256; generated before selection; executed once)
Phase C c6d0cd3c...; SMC-01 2d6986fe...; DMM-01 923d8890...; H2-CERT-01 4265b98c...
Seed families disjoint: 32xxx/33xxx (MCM), 34/35xxx (Phase C), 36xxx (SMC), 37xxx (DMM), 38xxx (H2-CERT).

## S3. Frozen longitudinal tracker
Full specification in docs/audit/TCA_01_TRACKER_SPEC.md. Never uses h1/h2/M/labels. Holdout on untouched seeds
38502-38504 (38501 excluded as the incident/development seed).

## S4. Supplementary tables
- Claim ledger: docs/paper/CLAIM_LEDGER.{json,md} + CLAIM_LEDGER_TCA_ADDENDUM.md (classified claims).
- Errata ledger: docs/paper/ERRATA_LEDGER.md (E1-E8 wording corrections).
- Gate certificates (machine-readable): results/*/*_gate_certificate.json.
- Causal/transplant code-path audit: docs/audit/TCA_01_CAUSAL_TRANSPLANT_AUDIT.md.
- H1 load-bearing audit: docs/paper/H1_LOAD_BEARING_AUDIT.md + TCA_01_HOLDOUT_CERTIFICATION.md.

## S5. Negative results (retained, not buried)
- Individuation FAIL (HSI); high-dim storage downgraded (WD-01 Phase B, row-LOO leakage 0.57->0.19);
  causal 2nd-dimension FAIL (Phase C); h2 deep-turnover FAIL (H2-CERT, longitudinally confirmed 0.34<0.5).

## S6. Reproducibility appendix (commands)
Environment: python3, numpy, scipy, matplotlib. `PYTHONPATH=$REPO:$REPO/results/wd01_phasec`.
Per-experiment runners are committed beside their data (results/<exp>/*.py). Viewer: scripts/observe_droplet.py.
Longitudinal holdout: reruns deterministically from the sealed H2-CERT manifest seeds 38502-38504.
