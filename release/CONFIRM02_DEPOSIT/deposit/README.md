# CONFIRM02 deposit — Local interventional causal individuation in non-merging droplets

**Status: DEPOSIT PACKAGE, NOT A SUBMISSION.** Nothing here has been sent to Zenodo, to a preprint
server, or to a journal. No DOI exists. Two hard blockers remain (see "Blockers" below).

Study: `LCI-CAUSAL-NONMERGING-CONFIRM-02`
Branch: `exp/lci-causal-nonmerging-confirm-02` — `9b7580bc` (PRESEAL) → `830c2d0` (RESULTS) →
`9c8a62c` (ADDENDUM), off `6470513`. Nothing pushed, tagged or merged.

---

## The claim, and its ceiling

Maximal authorised claim, verbatim:

> **Local interventional causal individuation in non-merging droplets.**

Three things must be read alongside it, and are stated in the manuscript **abstract**, not buried:

1. **The readout is coupled by construction.** Uptake is wired to the memory field m₊ through
   `N·ρ·(1 + λ₊·m₊)` (λ₊ = 0.25). Erasing m₊ *must* move uptake. What the design tests is that the
   effect is own-specific, local, entity-resolved, and survives on droplets that never merge.
2. **The 69 droplet-targets are nested within 23 eligible worlds** (3 per world). They are **not**
   69 independent replications. All inference is at the world level, n = 23.
3. **This is a computational model.** No physical, chemical or biological system was studied.

Not claimed: distal behaviour, graded metrology, global identity, bounded entity established,
Turing behaviour.

## The four publication documents

| file | what it is |
|---|---|
| `MANUSCRIPT.md` | the paper: abstract, coupling disclosure, frozen design, results, post hoc addendum, what is not claimed, reproduction, blockers |
| `DEPOSIT_METADATA.json` | deposit metadata. `license` is deliberately `null`; the CC-BY-4.0 / Apache-2.0 choice sits under `license_proposal` pending approval. No invented ORCID, DOI, affiliation, funder or related identifier |
| `PROVENANCE_LEDGER.md` (+ `.csv`) | 108 rows. Every numeric claim traced to an exact path, commit, SHA-256 and JSON key / table cell, with verification mode and status |
| `LIMITATIONS_AND_CLAIM_CEILING.md` | binding ceiling on the other three: forbidden claims, the coupling, the nesting, the post hoc scope of R*, what VERIFIED means |

## Layout

```
MANUSCRIPT.md                      publication document 1
DEPOSIT_METADATA.json              publication document 2
PROVENANCE_LEDGER.md / .csv        publication document 3
LIMITATIONS_AND_CLAIM_CEILING.md   publication document 4
README.md                          this file
SHA256SUMS                         complete SHA-256 manifest of every file in this deposit
sources/docs/                      frozen protocol, preseal, certificate, verdict, power,
                                   determinism, independent view, R* addendum, figure,
                                   + the two prior-incident documents cited as contrast
sources/experiments/               runner, analysis script, committed raw record, bijective
                                   tracker + its unit tests, geometry selector, power explorer,
                                   figure script, R* sensitivity script
sources/engine/                    the sealed engine and config that define the m+ -> uptake coupling
sources/release/                   LICENCE files, CITATION.cff, AUTHORS.md (all with their
                                   unresolved placeholders left visible and untouched)
verification/                      re-derived certificate, structural diff, reproduction log,
                                   ledger build + render scripts, ledger counts
```

## Provenance summary

- **VERIFIED 94 | NOT_FOUND 9 | DIFFERS 5** (108 ledger rows).
- **VERIFIED means traced to an exact repository artefact. It does NOT mean independently
  reproduced.**
- **Seal integrity 8/8**: every SHA-256 in the PRESEAL's sealed-file manifest matches the committed
  content. No post-seal code drift.
- **Analysis stage re-run** (33.7 s) from the committed raw record with the committed script: every
  gated statistic reproduces exactly. Five non-gating floats differ by 1–3 ULP — recorded as the
  five DIFFERS rows, not hidden. **Simulation stage not re-run**: 32 seeds of a chaotic RD-PDE with
  an 800-step warm-up is not cheap.
- The nine NOT_FOUND rows are identity, licence and identifier fields. **Nothing was invented to
  fill them.**

## Verifying this deposit

```bash
sha256sum -c SHA256SUMS          # SHA256SUMS omits itself; verify the archive hash separately
python3 verification/build_ledger.py    # rebuilds PROVENANCE_LEDGER.csv, re-hashing every source
python3 verification/render_ledger.py   # re-renders PROVENANCE_LEDGER.md from the CSV
```

## Blockers

**Resolved by the author on 2026-08-08** (see `AUTHOR_AUTHORISATION_02.md`):

1. ~~Literal `[COPYRIGHT HOLDER]` marker in the licence files.~~ **Resolved** — both
   `sources/release/LICENSE-CODE` and `sources/release/LICENSE-DATA-TEXT` now read
   `Copyright 2026 Tommy Lepesteur` on line 1. The marker occurs nowhere in the deposit.
2. ~~Author name placeholder.~~ **Resolved** — `Tommy Lepesteur` in `sources/release/AUTHORS.md`
   and `sources/release/CITATION.cff`.
3. ~~CC-BY-4.0 is a proposal.~~ **Resolved** — approved by the author; `license` in
   `DEPOSIT_METADATA.json` is now `cc-by-4.0` (code stays Apache-2.0).

**Still open, nothing invented:**

4. **Affiliation and ORCID are undeclared.** The author declared a name only. Ledger rows N04, N05
   remain `NOT_FOUND`.
5. **No DOI, funder or related identifier exists.** Ledger row N06 remains `NOT_FOUND`.
6. **Nothing has been submitted.** Approving the licence is *not* authorisation to deposit. No
   Zenodo record has been created, reserved or published.

*No simulation was run, no analysis was invented, and nothing was submitted, in the making of this
deposit.*
