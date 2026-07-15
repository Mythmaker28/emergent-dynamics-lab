# PDF QA Report (full manuscript V1/V2 + supplement)

## Programmatic checks (both manuscripts)
- Compilation: pdflatex + bibtex + 2x pdflatex, halt-on-error, exit clean.
- Undefined citations/references (final pass): 0.
- Bibliography: 36 entries, all cited resolve to numbers.
- Severe overfull hboxes (>30pt): 0 (one 37.7pt intervention-table row fixed via wrapping p-column + shortened cells).
- Missing figures: 0 (all 8 \includegraphics resolved).
- Pages: V1 22, V2 22, Supplement 3 (main 15-25 target met).
- Counted words (abstract..conclusion, emphasis preserved): V1 6295, V2 6386 (6000-8000 target met).
- Tables: 10; Figures: 8; Numbered equations: 6 (Psi, memory update, two readouts, coordinates, R2, tracker score).

## Visual inspection (rendered pages, representative across document)
- p1 title/abstract: clean; numbered citations resolve; italics correct.
- p3 model/introduction: numbered equations and citations render; no glyph loss.
- p6 (short paper) / figure pages: figures embed at readable resolution with full captions.
- p15 (V2): Figure 3 (tracked 3-panel) + Table 8 (gate outcomes) + Limitations render cleanly; captions complete.
- References page: numbered list, DOIs/venues present, no duplicated numbering.
- Headings: no orphaned headings observed; section/paragraph structure intact.
Every page was rendered; the above are the representative checks recorded. No blocking issues found.

## Author metadata (only user-required input)
Placeholders remain, as instructed: [AUTHOR NAME REQUIRED], [AFFILIATION REQUIRED], [ORCID IF AVAILABLE],
[FUNDING STATEMENT REQUIRED]. The AI-assistance disclosure is a draft for the target venue's policy.
