# Author authorisation — CONFIRM-02 deposit

**Date of record: 2026-08-08.** This file exists so that every value in the deposit that came from
the author rather than from a repository artefact is traceable to a single declaration.

## What the corresponding author declared

| Item | Value | Where it was written |
|---|---|---|
| Copyright holder | **Tommy Lepesteur** | `release/LICENSE-CODE` line 1, `release/LICENSE-DATA-TEXT` line 1 |
| Author name | **Tommy Lepesteur** | `release/AUTHORS.md`, `release/CITATION.cff` (`family-names: Lepesteur`, `given-names: Tommy`) |
| Licence, data / figures / text | **CC-BY-4.0** | `DEPOSIT_METADATA.json` → `license: "cc-by-4.0"`, `release/LICENSE-DATA-TEXT` |
| Licence, source code | **Apache-2.0** (unchanged, already in the repository) | `release/LICENSE-CODE` |

Provenance of these four values is the author's declaration of record, **not** a derivation from
any pre-existing repository content. The artefacts were written to match the declaration; the
declaration was not read out of the artefacts. Ledger rows `N01`, `N02`, `N03` are marked
`VERIFIED` on that basis and say so in their note field.

## What the author did NOT declare, and what was therefore not written

| Item | Status | Ledger row |
|---|---|---|
| Affiliation | `NOT_DECLARED` — never present in the repository, not invented | `N04` |
| ORCID | `NOT_FOUND` — no ORCID exists anywhere in the repository, not invented | `N05` |
| DOI | `NOT_FOUND` — none minted or reserved, not invented | `N06` |
| Funder | `NOT_FOUND` — recorded as an unfilled placeholder in `release/README_RELEASE.md` | — |

## What this authorisation is not

**It is not authorisation to deposit.** Choosing a licence and naming a copyright holder settles
*what the record would say*; it does not settle *whether the record is created*. As of this file:

```
SUBMISSION_STATUS = NOT_SUBMITTED
ZENODO_RECORD_CREATED  = false
ZENODO_RECORD_RESERVED = false
ZENODO_RECORD_PUBLISHED = false
DEPOSIT_AUTHORISED_BY_AUTHOR = false
```

Nothing has been uploaded to Zenodo, no DOI has been reserved, and no automated step in this
repository will create one. That remains a separate, explicit decision.

## What still gates a release, on scientific grounds rather than administrative ones

The claim ceiling in `LIMITATIONS_AND_CLAIM_CEILING.md` is unchanged by anything in this file. In
particular the maximal authorised claim remains *"Local interventional causal individuation in
non-merging droplets"*, the simulation stage was **not** re-run in the verification pass, and the
`h2` temporal-order coordinate's deep-turnover retention is **not** established. Resolving a
licence marker does not raise a claim ceiling.
