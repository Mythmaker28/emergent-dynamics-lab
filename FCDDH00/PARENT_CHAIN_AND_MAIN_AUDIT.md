# FCDDH00 — PARENT CHAIN AND MAIN AUDIT

`FCDDH00_PROVENANCE_STATUS = PASS`

## 1. Chain

```
FWL2CF00   96c7d295e72106cd949d810fa92807c2514e7449   tree 626dfe3278748b62495f4a90eaa61183770f2d82
   |                                       subtree 96c7d295:FWL2CF00 = 159577eeb703d5878b2efe37737b535fddc29046
SQDT00     16717582e7f0dfd371f21c56465e11113d8b6675   tree 6b3e8650eb62d31380c705944756e4211d20bdae
   |                                       subtree = 2a68162bcbd2881267afbb7adbf19a03b7c028ba
FSQBT00    b3f45ac7781e0dd48f34886b7c63840af520d502   tree 6c362f8acb4a80da8769986129a6ea0af58f099d
   |                                       subtree = ab11f2c0187b645f4793cb2b08dfa599fe506d4f
FCRA00     334b7c2ba6d97dadb403c7a1ea9700a1c61ad512   tree b36f821850a970c6cbb6a29ca539b3a99bbd5d8c
   |                                       subtree = b43e04983e6a3cbf31b6ccc84b5267fbe17b1ad2
FCDDH00 c1 2c1495c3a0b06863548984d989d6e9e34c97d685
```

`git merge-base --is-ancestor` confirms `96c7d295 < 16717582 < b3f45ac7 < 334b7c2b`. The
FCRA00 bundle `FCRA00_tip_334b7c2b.bundle` hashes to `95ef451164d31bea9b16b94e6d86aadad40c696a308e007e9955b1e506ae2e3b`, matching the
owner-reported prefix `95ef4511`. Every owner-reported abbreviated identifier resolves uniquely
and agrees.

## 2. Tommy's main

`main = f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77`, tree `8672babd1bc11d5912cf4820b06fa5947ebcd04b`. It is **not** an
ancestor of the dev chain and is never checked out as a work branch, never moved, never merged
and never edited. It is re-read at every phase boundary; any change is a fatal stop. FCDDH00
advances its own ref only, by lock-free plumbing (`GIT_INDEX_FILE` scratch index, `write-tree`,
`commit-tree`, direct ref write), because the working copy sits on a create-only mount with a
stale `.git/index.lock` that cannot be unlinked.

## 3. Byte identity of the execution tree

The execution tree at `/home/claude/sweep` was extracted **from the parent tree object**
(`git archive` for the bulk, `git cat-file blob` for the 19 paths that `.gitattributes` marks
`text eol=crlf`, so that raw blob bytes are used everywhere).

```
paths checked        : 1392
byte identical       : 1392
mismatches           : 0
absent in the cloud  : 0
git blob ids         : sha1(b'blob <len>\0' + content) in-process; no subprocess
```

## 4. The specifically bound parent objects

| bound object | path | byte identical |
|---|---|---|
| `FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz` | `SQDT00/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz` | True |
| `FWL2_RELATIVE_QUOTIENT_BASIS_V1.json` | `SQDT00/FWL2_RELATIVE_QUOTIENT_BASIS_V1.json` | True |
| `parent_basis_loader_and_certificate` | `SQDT00/sq_offline.py` | True |
| `immutable_parent_P2_residual_gauge_rule` | `FSQBT00/fq_analysis.py` | True |
| `G1_complete_factorial_constructor` | `DOMC/domc_core.py` | True |
| `G1_founder_generator_and_engine_wiring` | `WSFSCRP00/wsfscrp_core.py` | True |
| `H3_complementary_allocation_orbit_semantics` | `PPAI/ppai_core.py` | True |
| `carrier_1_executable` | `ETCMNFC/etcmnfc_core.py` | True |
| `carrier_2_executable` | `PPAI/ppai_core.py` | True |
| `weighted_L2_production_reader` | `WL2SMF00/wl2_prod.py` | True |
| `weighted_L2_reference_reader` | `WL2SMF00/wl2_ref.py` | True |
| `weighted_L2_estimand_and_gauge_spec` | `WL2SMF00/WEIGHTED_L2_ESTIMAND_AND_GAUGE_SPEC.md` | True |
| `materiality_semantics_and_units` | `WL2SMF00/MATERIALITY_SEMANTICS_AND_UNITS.md` | True |
| `modal_and_contrast_propagation_certificate` | `WL2SMF00/MODAL_AND_CONTRAST_PROPAGATION_CERTIFICATE.json` | True |
| `descendant_specific_twin_sham_materiality_rule` | `FSQBT00/fq_sham.py` | True |
| `engine_runner_and_start_ledger_contract` | `FWL2CF00/fw_worker.py` | True |
| `tube_P2_lobo_certificate` | `FSQBT00/TUBE_P2_LOBO_CERTIFICATE.json` | True |
| `corrected_transfer_licenses` | `FSQBT00/CORRECTED_TRANSFER_LICENSES.json` | True |
| `historical_G1_constructor_driver` | `FSQBT00/fq_construct.py` | True |
| `parent_ancestry_block_row_map` | `FSQBT00/TRUE_ANCESTRY_BLOCK_ROW_MAP.json` | True |
| `FCRA00_primary_recomputation` | `FCRA00/PRIMARY_INDEPENDENT_RECOMPUTATION.json` | True |
| `FCRA00_carrier_anatomy` | `FCRA00/CARRIER_COMMON_DIFFERENTIAL_ANATOMY.json` | True |
| `FCRA00_direction_arbitration` | `FCRA00/DISCOVERY_DIRECTION_LOBO_ARBITRATION.json` | True |
| `FCRA00_direction_rule_freeze` | `FCRA00/DISCOVERY_DIRECTION_RULE_FREEZE.json` | True |
| `FCRA00_final_disposition` | `FCRA00/FCRA00_FINAL_DISPOSITION.json` | True |

## 5. Owner-reported FCRA00 facts, verified against committed bytes

| fact | owner reported | from bytes | agrees |
|---|---|---|---|
| FSQBT00_CELL_MATERIALITY | 24_OF_24 | PASS_24_OF_24 (n_pass=24) | True |
| FSQBT00_DIRECT_CARRIER_CONTRAST_MAGNITUDE | 12_OF_12 | 12 | True |
| FSQBT00_PARENT_E2_SIGN_CONCORDANCE | 10_OF_12 | 10 | True |
| FROZEN_P2_TRANSFER_AS_FROZEN | NOT_TRANSFERRED | NOT_TRANSFERRED | True |
| blocks exceeding the frozen P2 tube | 3 | 3 | True |

`TUBE_P2_LOBO = 1.2166510017869535e-07`. No parent
artefact was edited, amended, reinterpreted or overwritten; FCDDH00 is an append-only child.

## 6. Namespace

`N = 71000`; discovery candidates `71000..71023`,
hold-out candidates `71024..71055`.
N = 71000 is the smallest admissible value; no increment was required
