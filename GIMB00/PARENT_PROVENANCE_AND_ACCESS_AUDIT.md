# PARENT_PROVENANCE_AND_ACCESS_AUDIT

## Ancestry, proved not narrated

    e912a1004c5b9732d12a8fcc417002bfd1135622   (WSCCRP00, reported ancestor)
      -> f81daf91dd70a05f34372fb85d2c3fba0dd5550b   (WSFSCRP00 closure)
        -> f9e1e39170a746bc5d8c43a80bc878cf24180714   (FSCMA00)

Each link verified on the device repository as a **direct parent**, not merely an ancestor, and the
three commits form the first-parent chain. Short hashes were resolved locally; none was trusted.

## Byte binding of every raw source

Each raw file's **git blob object id was recomputed from local bytes** as
`sha1("blob <len>\0" + bytes)` and compared with the object id in the committed tree. This binds
the analysed bytes to the commit independently of any filename.

| path | committed blob | recomputed | match |
|---|---|---|---|
| `FSCMA00/FSCMA00_LOCKED_RAW_CELL_SCORES.json` | `647f431120a29951` | `647f431120a29951` | True |
| `FSCMA00/fscma_probe_raw.json` | `cffe72bb244fee0a` | `cffe72bb244fee0a` | True |
| `FSCMA00/fscma_locked_carrier.json` | `0c58470738a1fe2e` | `0c58470738a1fe2e` | True |
| `FSCMA00/FSCMA00_S5_S8.json` | `2941652b899c4291` | `2941652b899c4291` | True |
| `WSFSCRP00/wsfscrp_q01.json` | `8c29d49e13d614f8` | `8c29d49e13d614f8` | True |
| `WSFSCRP00/wsfscrp_core.py` | `132b65759c57cd73` | `132b65759c57cd73` | True |

Manifests re-verified from bytes: WSFSCRP00 **49/49**,
FSCMA00 **35/35**, zero failures.

## Raw-source adequacy

The handoff named three raw sources. CARRIER_LOCKED time-resolved rows are NOT in FSCMA00_LOCKED_RAW_CELL_SCORES.json -- that file carries the environmental rows and the derived scores. The LOCKED carrier curves live in FSCMA00/fscma_locked_carrier.json, which is in the same committed tree and is bound above by blob oid. Located by committed provenance, not by filename convenience, exactly as instructed.

| panel | rows | curve length | exact rational strings | founders |
|---|---|---|---|---|
| CARRIER_BASIS | 12 | [10] | True | [64001, 64002, 64005, 64006, 64009, 64010] |
| CARRIER_LOCKED | 12 | [10] | True | [64000, 64003, 64004, 64007, 64008, 64011] |
| ENV_PROBE_AND_DOSE | 12 | [10] | True | [64001, 64002, 64005, 64006, 64009, 64010] |
| ENV_LOCKED | 6 | [10] | True | [64000, 64003, 64004, 64007, 64008, 64011] |

Only shapes and hashes were inspected at this stage. Numeric response arrays were loaded strictly
after the master freeze was written and hashed.

## Access ledger for Phase 1

Every WSFSCRP00 and FSCMA00 row is exposed. Phase 1 is post hoc corrective reanalysis of exposed
development rows. The words held-out, confirmed, blind and replicated are not available to it.
Namespaces 62000-62009 were not opened, generated or read at any point.

**VERDICT: PROVENANCE_BOUND**
