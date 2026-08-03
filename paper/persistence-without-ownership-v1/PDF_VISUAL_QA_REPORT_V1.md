# PDF visual QA report — Version 1.0

Both PDFs were compiled with `pdflatex` + `bibtex` (TeX Live), rendered to images at 120 dpi with `pdftoppm`, and every page was inspected visually. Builds are byte-deterministic (`SOURCE_DATE_EPOCH` fixed): recompilation reproduces the identical SHA-256.

## Artifacts and hashes

| Artifact | Pages | Words | SHA-256 |
|---|---|---|---|
| `PERSISTENCE_WITHOUT_EVIDENCE_OF_LOCAL_OWNERSHIP_V1.pdf` | 21 | 8,125 | `2c030bb0aa5ad7346ad25574d8c1ab14319956029c7d7fdc75ab47e854af9b0b` |
| `PERSISTENCE_WITHOUT_EVIDENCE_OF_LOCAL_OWNERSHIP_V1_SUPPLEMENT.pdf` | 6 | 2,582 | `e48af98e90e87ffca3411c817cae604d8708b26cf9a7ea51c5ed67e7e77b5f62` |

Manuscript counts: 8 figures, 0 in-text tables, 30 references. Supplement counts: 5 tables/longtables. Page sizes: US Letter (612×792 pt).

## Compile-time checks

- Exit status 0 for both documents; latexmk converged.
- No undefined references and no undefined citations in the final log.
- Zero overfull `\hbox` above 20 pt in the manuscript.
- Embedded PDF metadata set correctly:
  - Main — Title: "Causal Persistence Through Material Turnover Without Evidence of Local Ownership"; Author: "Tommy Lepesteur"; Subject and Keywords present.
  - Supplement — Title: "Supplementary Information: Causal Persistence Through Material Turnover Without Evidence of Local Ownership"; Author: "Tommy Lepesteur".

## Visual inspection — manuscript (21 pages)

| Page(s) | Content | Result |
|---|---|---|
| 1 | Title, subtitle, author, affiliation, "Version 1.0 / July 2026", ORCID+correspondence footnote, structured abstract | PASS — canonical title and subtitle render; author/affiliation/ORCID correct; no author/affiliation placeholder; no "alternative titles" block; all gate values present in abstract |
| 2–3 | Introduction; Figure 1 (falsification ladder) on p3 | PASS — figure legible, no clipping, caption complete, Outcome B labelled |
| 4–6 | Operational definitions, related work, model/memory (equations) | PASS — equations render; no clipped math |
| 7 | Figure 2 (scaffold and memory channels) | PASS — schematic legible, no clipping |
| 8–9 | Figures 3–4 (non-fusing intervention; material turnover/feasibility) | PASS — panels legible, captions complete |
| 10–13 | Results; Figures 5–7 (causal contrasts; ownership-scope exclusions; decision tree) | PASS — Fig 6 shows L-over-E and L-over-B "fails exclusion"; Fig 7 decision tree resolves to Outcome B |
| 14–17 | Interpretations, corrections, discussion; Figure 8 (claim boundary) on p17 | PASS — four-quadrant claim boundary legible |
| 18 | End of limitations (Version 1.0 preprint note); Conclusion; Data and code availability; AI-assistance disclosure; Author contributions | PASS — exact mandated wording verified for availability, AI disclosure, and CRediT |
| 19 | Funding; Competing interests; Ethics approval; Consent for publication; Acknowledgments; License; References begin | PASS — every statement matches the required exact text |
| 19–21 | References [1]–[30] | PASS — bibliography complete, DOIs present, ends cleanly at [30]; no duplicate/orphan entries |

## Visual inspection — supplement (6 pages)

| Page(s) | Content | Result |
|---|---|---|
| 1 | Title, author, "Version 1.0", ORCID footnote, table of contents | PASS — title/author/version correct; TOC (12 sections) renders |
| 2 | Source-lineage table; final-seal SHA-256; V4.1 correction detail | PASS — commit table not clipped |
| 3–4 | V4.1 tables, CONFIRM-02 tables, 03G population, primary numerical-results table | PASS — all numeric tables render without clipping; L−E and L−B lower bounds negative as required |
| 5 | Correction chronology; claim-classification table | PASS |
| 6 | Reproduction commands and guards; residual risks; artifact inventory | PASS — inventory describes the Version 1.0 package (no stale "unfilled metadata" or "hostile reviews" text) |

## Placeholder / forbidden-token sweep (rendered text and source)

The public manuscript and supplement contain no unresolved metadata placeholders of any kind: no bracketed author, affiliation, ORCID, funding, email, date, or venue fields; no bare fill-me markers; no internal laboratory or repository/project name used as an affiliation; no internal development version label; and no leftover multi-candidate title block. No visible email-placeholder token appears in either PDF. The English word for a fill-in marker occurs only inside the scientific correction-history narrative (describing the historical authorization-template defect), which is retained scientific content, not a metadata field. Reproduction paths in the supplement that carry the internal package's numeric suffix are accurate committed provenance paths, not public version labels.

## Scientific-invariant verification (unchanged from canonical package)

Confirmed present and unaltered in both PDFs: 50 primary worlds; 21 valid worlds; 0 reserve worlds executed; Outcome B; `G_OWN_PERM=true`; `G_CAUSAL=true`; `G_LOCAL_EXCLUSION=false`; `DISTRIBUTED_ENV=false`; causal feeding survives deep turnover; local ownership unresolved; no individual-memory/identity/life/agency/reproduction/heredity/active-reconstruction claim; independent raw-only reproduction across 9,357 leaves (9,283 numeric) with maximum absolute difference 0. Figures and `references.bib` are byte-identical to the committed originals.

## Verdict

Both PDFs pass visual and structural QA with no defects, no placeholders, and no altered scientific content.
