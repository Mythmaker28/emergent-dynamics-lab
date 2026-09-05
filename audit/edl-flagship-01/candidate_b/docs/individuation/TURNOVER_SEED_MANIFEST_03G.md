# Authoritative seed manifest - turnover PRESEAL 03G

Status: **NOT AUTHORIZED - NOT SEALED - ZERO 54xxx SEEDS EXECUTED**.

## Prospective family

| tier | inclusive range | count |
|---|---:|---:|
| primary | `54001-54050` | 50 |
| feasibility reserve | `54051-54096` | 46 |
| hard cap | `54001-54096` | 96 |

Minimum valid original worlds: **18**.

The runner executes every primary seed in ascending order. After `PRIMARY_CLOSED`, reserve activation reads only
the persisted projection:

`seed, eligible, deep_reached, rest_assay_valid, deep_assay_valid, valid, reason`.

It reads no label, feature, effect, decoder, gate, or outcome field. If fewer than 18 primary worlds are valid, the
runner executes reserve seeds in ascending order and stops immediately when 18 valid worlds are reached or after
seed `54096`. There is no extension.

## DEV allowlist

The structurally identical DEV smoke manifest may use only previously opened seeds `50001-50010`. Its outputs are
watermarked `DEV/EXPLORATORY`, use a distinct canonical directory, and cannot authorize the prospective family.
