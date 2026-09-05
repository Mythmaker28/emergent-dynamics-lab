# Authoritative seed manifest — LCI-CAUSAL-TURNOVER-PRESEAL-03C

## Status

`NOT OPENED — NOT AUTHORIZED — ZERO 54xxx SEEDS EXECUTED`

## Development-only evidence

Committed DEV family `50001-50010` remains exploratory. Claude's `n=4` feasible diagnostics are not prospective
claims and are not used to select features, thresholds, coordinates, or the seed family.

## Exact prospective family

| tier | inclusive range | count |
|---|---:|---:|
| primary | `54001-54050` | 50 |
| feasibility reserve | `54051-54096` | 46 |
| total hard cap | `54001-54096` | 96 |

Minimum valid original worlds: **18**.

Primary seeds are all executed after a valid human approval. Reserve activation is sequential and uses only the
frozen feasibility projection after all 50 primary seeds are complete. It stops when 18 valid worlds are reached or
at seed 54096. There is no family `54097-54120` in this experiment and no extension beyond the hard cap.

The runner accepts no user-specified seed list; it derives the next authorized seed from this manifest and the
feasibility-only ledger.

## Outcome-blinding proof obligation

The activation function reads only:

`seed, eligible, deep_reached, rest_assay_valid, deep_assay_valid, valid, reason`.

It persists `endpoint_fields_used: []`. Unit tests mutate labels and endpoint payloads without changing the reserve
decision.
