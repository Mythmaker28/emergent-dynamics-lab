# Reproducibility release checklist

Status: **PREPARED, NOT RELEASED.** No push, tag, DOI, or public upload has been performed. Release requires
explicit authorization from the operator (Tommy). Main branch is untouched (HEAD f3921a4); nothing is pushed
(origin/main e17f431). This checklist is what a public archive (e.g. a Zenodo record from a tagged commit)
would contain.

## A. Code (frozen, in-repo)
- [x] Scaffold engine `edlab/substrates/scaffold/engine.py` (blob 7c91b91) + `observables.py` (detector).
- [x] Memory law `edlab/experiments/sc_iom/engine.py` (IOM-00, blob dc04f5d) and readouts
      `edlab/experiments/sc_mcm/engine.py` (MCM-00).
- [x] Candidate writing grid + selection `results/wd01_phasec/candidates.py`, freeze `FREEZE_C1c.json`.
- [x] Per-experiment resumable runners (WD-01, Phase C, SMC-01, DMM-01, H2-CERT) committed beside their data.
- [x] Longitudinal tracker spec `docs/audit/TCA_01_TRACKER_SPEC.md`; viewer `scripts/observe_droplet.py`.
- [x] Re-audit script + outputs backing every V3 CI (`STATISTICAL_REAUDIT.md`).

## B. Data (raw, in-repo)
- [x] `results/{sc_mcm,wd01,wd01_phasec,smc01,dmm01,h2cert,observer}/*.pkl,*.json`.
- [x] Machine-readable gate certificates (5) recording gates met **and not met**.
- [x] Sealed prospective manifests with SHA-256 hashes (Supplement S4).

## C. Manifests / provenance
- [x] Provenance table (main text `tab:provenance`): protocol / commit / freeze-date / execution-date / hash.
- [x] Branch+commit registry (Supplement S3); disjoint seed families 32xxx-38xxx (S4).
- [x] SHA-256 of each sealed family, generated before selection, executed once.

## D. Commands
- [x] Environment: python3 + numpy + scipy + matplotlib; `PYTHONPATH=$REPO:$REPO/results/wd01_phasec`.
- [x] One documented command per figure and per reported statistic (Supplement S9); tracker hold-out reruns
      deterministically from the H2-CERT manifest seeds 38502-38504.

## E. License and citation
- [ ] **TODO (needs operator decision):** choose a license (code: MIT/BSD/Apache-2.0; data/text:
      CC-BY-4.0 is typical) and add `LICENSE` + `CITATION.cff`.
- [ ] Reserve a DOI (Zenodo) from the tagged release commit -- **only on authorization**.
- [x] AI-authorship disclosure carried in the manuscript; to be repeated in the archive README.

## F. Pre-release verification gate (do before any public release)
- [x] V3 manuscript compiles clean (23 pp, 0 undefined refs).
- [x] Supplement V3 compiles clean (5 pp).
- [x] Every reported number traces to a committed file (data-availability statement, Supplement S9).
- [x] Every recent-literature DOI web-verified against its claim.
- [ ] Independent third-party rerun of at least the primary result (deep h1) from a clean checkout -- **not
      yet performed**; recommended before DOI.
- [ ] Operator authorization to push/tag/publish -- **not given**.

## G. Explicitly out of scope until authorized
- No `git push`, no tag, no Zenodo deposit, no preprint submission, no journal submission. These are gated on
  Tommy's explicit go-ahead.
