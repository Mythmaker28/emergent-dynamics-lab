# PDF visual-QA report

Inspection date: 2026-07-16
Inspector: Codex methodological reconciliation agent
Renderer: Poppler `pdftoppm`, 130 dpi
Build engine for V4.1: ReportLab through `scripts/build_pdfs.py`

## Scope and result

All 41 pages in the four delivered or preserved PDFs were rendered and visually
inspected. No page is blank, clipped, rotated incorrectly, missing a figure, or
missing a table. No replacement-glyph boxes were observed. V4.1 uses A4 pages;
the preserved V4.0 PDFs retain their original US-letter geometry.

Poppler emitted non-blocking font-discovery warnings for several unavailable
system aliases while producing the renders. The embedded text, equations, and
figure labels remain visible in every inspected page.

## File integrity

| PDF | Pages | SHA-256 | Result |
|---|---:|---|---|
| `ORGANIZATIONAL_MEMORY_V4_1_RECONCILIATION.pdf` | 6 | `f9c4f47c0d0b2beb488c515db3fd3ed74fd1857b3e21733376128756feffb9cf` | PASS |
| `SUPPLEMENT_V4_1.pdf` | 6 | `8df7c62aa99eda421fa9e17bf57e9fcdf3fdebd5362bb8eff2b9c96006fe03fe` | PASS |
| preserved `ORGANIZATIONAL_MEMORY_FULL_MANUSCRIPT_V4.pdf` | 24 | `1a3f3dc125df005b60c54973ba00b7226d9f0c4a8d973efe7ab6e461bdd6ab77` | PASS, unchanged |
| preserved `SUPPLEMENT_V4.pdf` | 5 | `3fc5af27f45b37f9a5531912e19aac542f897105dc379a40acd95dde6b4362ff` | PASS, unchanged |

## V4.1 manuscript: page-by-page inspection

| Page | Visible content | QA result |
|---:|---|---|
| 1 | title, status line, abstract, keywords, purpose and scope | PASS; hierarchy clear, no overflow |
| 2 | canonical evidence, preservation, leakage mechanism, frozen estimator | PASS; bullets and code hash legible |
| 3 | uncertainty method, primary results, Figure 1 and full caption | PASS; both panels and uncertainty bars visible |
| 4 | tracker/fusion correction, Figure 2, transplant results | PASS; axis labels and sample-size caption legible |
| 5 | secondary results, Figure 3, global-versus-local section, reconciliation table | PASS; four bars and all table rows visible |
| 6 | discussion, limitations, conclusion, verdict, data availability | PASS; no orphan page or clipped footer |

## V4.1 supplement: page-by-page inspection

| Page | Visible content | QA result |
|---:|---|---|
| 1 | title, canonical-source table, primary sample-size definitions | PASS |
| 2 | remaining sample sizes, bootstrap audit, duplicate-count table | PASS |
| 3 | frozen algorithm, crossed sensitivity, h1 and partial h2 fold tables | PASS |
| 4 | remaining fold tables, uncertainty, tracker/event-evidence tables | PASS |
| 5 | tracker limitations, secondary results, global-versus-local comparison | PASS |
| 6 | figure-caption audit, claim dispositions, reproduction boundary | PASS |

## Preserved V4.0 manuscript: page-by-page inspection

| Page | Visible content | QA result |
|---:|---|---|
| 1 | title and abstract | PASS; original placeholders retained |
| 2 | introduction | PASS |
| 3 | introduction and related work | PASS |
| 4 | related work | PASS |
| 5 | model opening and equations | PASS |
| 6 | model and experimental-method opening | PASS |
| 7 | parameter tables and methods | PASS |
| 8 | decoding, longitudinal tracker, and power method | PASS |
| 9 | intervention tables, experimental sequence, results opening | PASS |
| 10 | primary results and causal-memory discussion | PASS |
| 11 | order-coordinate and turnover results | PASS |
| 12 | tracker-continuity incident and discussion opening | PASS |
| 13 | primary-results tables and discussion | PASS |
| 14 | causal ladder figure and interpretation | PASS |
| 15 | causal figure, longitudinal synthesis table, text | PASS |
| 16 | longitudinal turnover figures and limitations opening | PASS |
| 17 | quantitative figure, conclusion, declarations | PASS |
| 18 | order-coordinate figure, disclosures, availability | PASS |
| 19 | storage figure and reproducibility statement | PASS |
| 20 | deep order-coordinate figure and references opening | PASS |
| 21 | gate-summary figure, gate table, references | PASS |
| 22 | claim-boundary tables and references | PASS |
| 23 | references | PASS |
| 24 | references completion | PASS |

## Preserved V4.0 supplement: page-by-page inspection

| Page | Visible content | QA result |
|---:|---|---|
| 1 | supplement title, scope, model equations | PASS |
| 2 | growth, death, memory writing/readout, parameters | PASS |
| 3 | history coordinates, detector, decoder, protocol history | PASS |
| 4 | registry, family hashes, candidate and certificate sections | PASS |
| 5 | tracker tests, turnover results, commands, data registry | PASS |

## Caption and sample-size audit

The three V4.1 figure captions explicitly state the relevant row, world,
history, donor-world, and recipient counts. Figure 1 labels its intervals as
descriptive; Figure 2 states that tracker agreement does not reconstruct fusion
handling or locate storage; Figure 3 states that its bars come from different
artifact families and therefore are not combined inferentially.

Final visual-QA verdict: **PASS**.
