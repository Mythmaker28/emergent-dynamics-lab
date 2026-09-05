# Release checklist — Version 1.0

Status legend: `[x]` done in this editorial pass · `[ ]` pending human/release action.

## Editorial completion (done in Version 1.0)

- [x] Canonical title set: "Causal Persistence Through Material Turnover Without Evidence of Local Ownership".
- [x] Subtitle set: "A Prospective Test of Engineered Memory in Simulated Droplets".
- [x] Internal "alternative titles" block (the multi-candidate title list) removed from the manuscript.
- [x] Author: Tommy Lepesteur. Affiliation: Independent Researcher, Rennes, France. ORCID: https://orcid.org/0009-0009-0577-9563.
- [x] Institutional-affiliation guard: the internal laboratory name, the repository/project name, and the author's code-host handle are **not** used as an affiliation; the sole affiliation is "Independent Researcher, Rennes, France".
- [x] Version label set to "Version 1.0" on manuscript and supplement; internal development version labels removed from the public manuscript and supplement.
- [x] Funding: "This research received no external funding." (No grant agency, research program, employer, archive/deposit service, code host, or AI vendor is credited as a funder.)
- [x] Competing interests: "The author declares no competing interests."
- [x] Author contributions (CRediT, single author) completed; no AI listed as author.
- [x] AI-assistance disclosure completed (OpenAI ChatGPT/Codex and Anthropic Claude, under author direction; author responsible).
- [x] Ethics approval statement added (computer simulations only; no human/animal/clinical/PII data).
- [x] Consent for publication: "Not applicable."
- [x] Acknowledgments added (open-source software maintainers; no invented collaborators).
- [x] Licensing stated: manuscript + supplementary text + figures under CC BY 4.0; code retains Apache-2.0 (no silent relicense).
- [x] Data and code availability rewritten to reference the repository and commits `d4a146a` / `a8d6446` / `9cb996bb`, with honest "not yet public / will be made available upon public release" phrasing; no DOI asserted; no reuse of unrelated deposits.
- [x] Correspondence handled without inventing an email (ORCID-only; private email deferred to submission).
- [x] `CITATION.cff` (CFF 1.2.0) present; version 1.0.0; author/ORCID/affiliation set; no DOI created or reserved.
- [x] Placeholder sweep clean: no bracketed author/affiliation/ORCID/funding/email/date/venue fields, no bare fill-me markers, and no internal development version label remain in the public manuscript or supplement.
- [x] Journal-neutral: no target-journal name appears anywhere.
- [x] Manuscript and supplement compiled; every page visually inspected (see `PDF_VISUAL_QA_REPORT_V1.md`).
- [x] Scientific invariants verified unchanged (50 primary / 21 valid / 0 reserve worlds; Outcome B; `G_OWN_PERM=true`, `G_CAUSAL=true`, `G_LOCAL_EXCLUSION=false`, `DISTRIBUTED_ENV=false`; 9,357 leaves, max numeric difference 0).
- [x] Figures and `references.bib` confirmed byte-identical to the committed originals.

## Pending release actions (human / networked machine)

- [ ] **Push the public branch and confirm reachability.** The manuscript commit `d4a146a` and its lineage are not yet on the public remote. From the repository root on a networked machine:

  ```powershell
  cd "C:\Users\tommy\Documents\ising v3"
  git push origin paper/persistence-without-ownership-v1:paper/persistence-without-ownership-v1
  ```

  Then confirm the commits are reachable, e.g.:

  ```powershell
  git ls-remote origin paper/persistence-without-ownership-v1
  git branch -r --contains d4a146a241588c0debd3a0cc6133bc6f6bb8824c
  ```

  Do **not** force-push and do **not** touch `main`; this command creates a new remote branch only. (A separate, pre-existing local↔remote `main` divergence is out of scope for this package and must not be resolved by force-push.)
- [ ] **Corresponding email.** If the chosen venue requires it, supply a corresponding-author email to the submission system privately.
- [ ] **AI-policy wording.** Adapt the AI-assistance disclosure to the specific venue's policy if it differs from the general form used here.
- [ ] **Venue selection.** Choose a target journal/preprint server and conform length, section order, and data-availability format to its template (kept journal-neutral here).
- [ ] **External peer review.** Solicit external scientific review; this is a preprint.

## Explicitly out of scope (not performed, by design)

- No new simulation, experiment, re-analysis, reserve seed, or second execution.
- No Git history rewrite; no merge to `main`; no push, tag, code-host release, external archive deposit, or journal submission.
- No modification of the internal `paper/persistence-without-ownership-05` package or its Git history.
- No DOI created or reserved.
