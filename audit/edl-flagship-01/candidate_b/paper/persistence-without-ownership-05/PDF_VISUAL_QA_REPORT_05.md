# PDF visual-QA report 05

## Verdict

**PASS — all 27 PDF pages were rendered and visually inspected.** No clipped text, clipped figures, overlapping objects, missing glyphs, missing images, blank pages, malformed tables, broken equations, or unresolved reference markers were observed.

## Build

- Compiler: Tectonic 0.16.9, official Windows x86_64 release.
- Release ZIP SHA-256: `131a24604785a9600989a3d91225f597df52ac06f00aeffe86fd529f99ee5cdd`.
- Main PDF: 21 letter-size pages, 1,260,988 bytes, SHA-256 `27be51ed84fa99b58b6f7af7558c11daa62e67bcddf53c26c953e9ea604e706a`.
- Supplement PDF: 6 letter-size pages, 68,154 bytes, SHA-256 `3bb7dbd102ff7edd568bfc6f0920997d7dae49958fa749b95e3475c8cc15c8fe`.
- Renderer: Poppler `pdftoppm`, 140 dpi, lossless PNG.
- Inspection format: every page individually rendered; adjacent pages paired into 14 lossless contact sheets for systematic inspection.

## Main manuscript page audit

| Pages | Content inspected | Result |
|---|---|---|
| 1–2 | Title, explicit author placeholders, alternative titles, structured abstract, Introduction opening | PASS |
| 3–4 | Introduction close, Figure 1 and full caption, operational definitions | PASS |
| 5–6 | Related work, model equations, protected source hashes, V4.1 correction | PASS |
| 7–8 | Figure 2, CONFIRM-02 text, Figure 3, seal and one-shot protocol | PASS |
| 9–10 | Material tracer equation, Figure 4, access scopes, grouped gates, Results opening | PASS |
| 11–12 | Figure 5 causal intervals, Figure 6 ownership intervals, exact gate vector and Outcome B | PASS |
| 13–14 | Figure 7 decision tree, positive/negative interpretations, correction history | PASS |
| 15–16 | Authorization defect, seal, raw-only reproduction, Discussion, Limitations opening | PASS |
| 17–18 | Figure 8, remaining limitations, Conclusion, availability and disclosure sections | PASS |
| 19–20 | Human conflict/funding placeholder and references 1–23 | PASS |
| 21 | References 24–30 and terminal page number | PASS; lower-page whitespace is the normal bibliography ending, not a blank page |

## Supplement page audit

| Pages | Content inspected | Result |
|---|---|---|
| 1–2 | Title, contents, evidential boundary, exact source-lineage table, seal, V4.1 and CONFIRM-02 opening | PASS |
| 3–4 | V4.1 and CONFIRM tables, 03G population/scopes/statistics, primary numerical table, 03M | PASS |
| 5–6 | Correction chronology, claim-classification table, guarded reproduction commands, risks, artifact inventory | PASS |

## Typesetting-log audit

- No `Overfull` box remains in either final log.
- No undefined citation or reference warning remains.
- No missing figure, emergency stop, or fatal error appears.
- A small number of underfull-box warnings remain in prose/table cells and one bibliography entry; visual inspection confirmed they cause only benign word spacing and no layout defect.
- Tectonic emitted a standalone-Windows fontconfig notice but used and embedded its downloaded TeX fonts successfully; no missing-glyph or substitution defect is visible.

## Scientific presentation checks

- All eight figures are present and legible.
- Every figure caption states sample unit, number of worlds, historical/prospective or DEV status, uncertainty treatment, generating script, and source artifact.
- L-over-E and L-over-B visibly cross zero and are labelled as failed exclusions.
- The decision figure visibly maps the exact frozen gate vector to Outcome B.
- V4.1 is visibly marked corrected/qualified and is never presented as certified above 0.50.
- Author, affiliation, ORCID, contribution, funding, and conflict placeholders remain explicitly unfilled for human action.

Temporary PNG renders and contact sheets were deleted after this audit; the two final PDFs remain under `output/pdf/`.
