# Causal Persistence Through Material Turnover Without Evidence of Local Ownership — Version 1.0

**A Prospective Test of Engineered Memory in Simulated Droplets**

Author: Tommy Lepesteur — Independent Researcher, Rennes, France — ORCID [0009-0009-0577-9563](https://orcid.org/0009-0009-0577-9563)
Repository: <https://github.com/Mythmaker28/emergent-dynamics-lab>

This directory is the first public, external-review version (**Version 1.0**) of the manuscript and its supporting artifacts. It is an *editorial* release: the manuscript text, figures, tables, gates, statistics, and scientific conclusions are identical to the internal working package described under "Provenance" below. Only publication metadata — title finalization, authorship, affiliation, ORCID, funding, competing-interest, ethics, licensing, and version labelling — has been completed here.

## Primary conclusion

> An engineered experience-dependent state remains causally active through deep material turnover but fails a preregistered criterion for exclusive target-local ownership. The frozen decision tree selects **Outcome B** (a causal feeding effect without ownership). Within the tested C1c architecture, causal persistence is insufficient to establish individual memory.

The result establishes causal persistence and, separately, does **not** establish local ownership; it does **not** claim that ownership is absent, that individual memory does not exist, or that identity was falsified. See `CLAIM_LEDGER_V1.md` for the exact permitted and prohibited wording.

## Package contents

| File | Purpose |
|---|---|
| `PERSISTENCE_WITHOUT_EVIDENCE_OF_LOCAL_OWNERSHIP_V1.tex` / `.pdf` | Main manuscript source and compiled PDF (21 pages). |
| `PERSISTENCE_WITHOUT_EVIDENCE_OF_LOCAL_OWNERSHIP_V1_SUPPLEMENT.tex` / `.pdf` | Supplementary information source and compiled PDF (6 pages). |
| `figures/` | The eight source-bound figures (byte-identical to the committed originals). |
| `references.bib` | Bibliography (30 DOI-verified references). |
| `README.md` | This file: provenance, licensing, correspondence, release status. |
| `METADATA_V1.json` | Machine-readable metadata, scientific invariants, and a SHA-256 file manifest. |
| `CITATION.cff` | Citation metadata (CFF 1.2.0). No DOI is asserted. |
| `CLAIM_LEDGER_V1.md` | Exact claim classes, evidence, and terminology boundaries. |
| `RELEASE_CHECKLIST_V1.md` | Completed editorial items and remaining release blockers. |
| `PDF_VISUAL_QA_REPORT_V1.md` | Page-by-page visual QA of the compiled PDFs, with hashes. |

## Provenance and version mapping (internal "V5" → public "Version 1.0")

The scientific synthesis was developed internally as the fifth-generation manuscript candidate ("V5") in the directory `paper/persistence-without-ownership-05`. **This public release renames that candidate as Version 1.0** — the first version intended for external scientific review. There is no public "V5"; the "V5"/"-05" labels are internal development identifiers only, and appear here solely in this provenance note and in committed file paths, never as the manuscript's public version.

The public version 1.0 branch is `paper/persistence-without-ownership-v1`, created from the manuscript commit and adding only this `paper/persistence-without-ownership-v1/` directory. The internal package `paper/persistence-without-ownership-05` is preserved unchanged and is inherited in this branch's tree.

Canonical commits (in the repository above):

- **Manuscript / analysis package:** `d4a146a241588c0debd3a0cc6133bc6f6bb8824c`
- **Independent raw-only reproduction (paper parent):** `a8d6446fade6dbeb984e269fab27ddd5ebf75286`
- **Sealed prospective turnover result (03G):** `9cb996bb891f9a618e593f2f5c302f30210458de`
- **Final seal SHA-256:** `cdf7277a00e3017a1389e9334d983364b9aa0af88c646cdec2999e6ad88757fd`

The experiment/data lineage (V4.1 correction, CONFIRM-02, 03G turnover, 03M reproduction) is documented in the Supplement and in the committed source-binding registry. The complete reproducibility toolchain — regeneration scripts, `SOURCE_BINDINGS_05.json`, `NUMERICAL_RECONCILIATION_05.*`, `REFERENCE_VERIFICATION_05.json`, `RAW_DATA_REGISTRY_05.json`, and the recomputed data — lives at the canonical path `paper/persistence-without-ownership-05/` in commit `d4a146a` and is inherited unchanged in this branch. Numerical regeneration therefore uses those canonical committed generators; Version 1.0 duplicates none of them, so no script or registry is silently forked or renamed.

## Correspondence

No public correspondence email is asserted in Version 1.0. No email address intended for public correspondence exists in the committed public metadata, so none is invented or exposed here. Correspondence should be directed to **Tommy Lepesteur, ORCID [0009-0009-0577-9563](https://orcid.org/0009-0009-0577-9563)**. A journal submission system may later require the corresponding author to provide an email address privately; that is a submission-time action, not a change to this preprint.

## Licensing

- The **manuscript text, supplementary text, and figures** in this package are released under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
- **Repository source code** retains its existing license, the **Apache License 2.0**. No code is relicensed by this package.

## Data and code availability status

All code, protocols, raw records, ledgers, certificates, and reproduction artifacts are version-controlled in the repository above. **At the time of writing these commits reside in the author's local repository and have not yet been pushed to the public remote**, so they are not yet externally reachable. The code and data will be made available upon public release of the repository. No public archive DOI is asserted for this version; no unrelated prior deposit or DOI is reused.

## Release blockers (must be resolved before external distribution)

1. **Public push not performed.** Commits `d4a146a`, `a8d6446`, and `9cb996bb` are not reachable from any remote branch. Push the branch (see `RELEASE_CHECKLIST_V1.md`) and confirm public reachability before citing these commits as available.
2. **Corresponding email.** If a chosen venue requires a corresponding-author email, provide it to the submission system privately; do not assume the ORCID-only statement satisfies every venue.
3. **AI-assistance wording.** The disclosure follows a general form; adapt it to the specific target journal's AI policy at submission.
4. **External peer review.** This is a preprint; it has not undergone external review.

## Scope: what this package does not do

This package performs no simulation, no new experiment, no re-analysis, no reserve seed, no second execution, no Git history rewrite, no merge to `main`, no push, no journal submission, and no DOI reservation or external archive deposit. It modifies no file of the internal `paper/persistence-without-ownership-05` package.

## Internal artifacts intentionally excluded

The internal working package additionally contained preparation materials that are **not** part of this public scientific release: a cover-letter draft, an adversarial ("hostile") reviewer dossier and response draft, a French lay summary, and internal package-validation output. These are editorial preparation aids, not part of the scientific record, and are omitted here. They remain in the inherited internal package for the author's reference.
