"""FSQBT00 Sections 14-17 -- decision matrix, independent-unit report, deviations, disposition,
start ledger. Zero starts."""
from __future__ import annotations
import json, hashlib
OUT = "/home/claude/sweep/FSQBT00"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
CELL = json.load(open(f"{OUT}/CELL_MATERIALITY_REPORT.json"))
P2 = json.load(open(f"{OUT}/FROZEN_P2_TRANSFER_REPORT.json"))
E2 = json.load(open(f"{OUT}/FROZEN_E2_OR_PROJECTIVE_P2_REPORT.json"))
FQ = json.load(open(f"{OUT}/FRESH_QUOTIENT_REPORT.json"))
LIC = json.load(open(f"{OUT}/CORRECTED_TRANSFER_LICENSES.json"))
THR = json.load(open(f"{OUT}/FRESH_WEIGHTED_L2_THRESHOLDS.json"))

n_over = sum(1 for b, v in P2["P2_OUTSIDE_RESIDUAL_per_block"].items() if v > P2["TUBE_P2_LOBO"])
over_blocks = {b: v / P2["TUBE_P2_LOBO"] for b, v in P2["P2_OUTSIDE_RESIDUAL_per_block"].items()
               if v > P2["TUBE_P2_LOBO"]}

# projective-P2 second-origin branch is gated by P2 transfer (P20 requires P2 pass)
PROJ = "NOT_EVALUABLE__GATED_BY_P2_NONTRANSFER" if P2["FROZEN_P2_TRANSFER_STATUS"] != "TRANSFERRED" else "SEE_REPORT"

matrix = {
    "CELL_MATERIALITY_STATUS": CELL["CELL_MATERIALITY_STATUS"],
    "CORRECT_LOBO_P2_LICENSE": LIC["P2_TRANSFER_LICENSE_CORRECTED"],
    "CORRECT_LOBO_E2_LICENSE": LIC["E2_AXIS_TRANSFER_LICENSE_CORRECTED"],
    "FROZEN_P2_TRANSFER_STATUS": P2["FROZEN_P2_TRANSFER_STATUS"],
    "FROZEN_E2_TRANSFER_STATUS": E2["FROZEN_E2_TRANSFER_STATUS"],
    "E2_CARRIER_ORIENTATION_STATUS": E2["E2_CARRIER_ORIENTATION_STATUS"],
    "PROJECTIVE_P2_SECOND_ORIGIN_STATUS": PROJ,
    "FRESH_QUOTIENT_STATUS": FQ["FRESH_QUOTIENT_STATUS"],
    "GEOMETRY_STATUS": "NOT_TESTED_IN_THIS_DESIGN",
    "ALLOCATION_STATUS": "NOT_TESTED_IN_THIS_DESIGN",
    "DOSE_STATUS": "NOT_TESTED_IN_THIS_DESIGN",
}
DISPOSITION = ("FRESH_PANEL_COMPLETE__FROZEN_P2_NOT_TRANSFERRED_PERBLOCK_TUBE_BREACH__"
               "FROZEN_E2_NOT_TRANSFERRED__CARRIER_DIRECTION_REPLICATED_12_OF_12__"
               "FRESH_QUOTIENT_RELATIVE_AT_LEAST_TWO_SECOND_BELOW_ABSOLUTE")

start_ledger = {
    "PANEL_CONSTRUCTION_STARTS": 12, "SHAM_STARTS": 24, "ACTIVE_STARTS": 24,
    "OTHER_STARTS": 1, "TOTAL_STARTS": 61,
    "RAW_ENGINE_ADVANCE_SEQUENCE_COUNT": 12 + 24 + 24,
    "caps": {"panel": 24, "sham": 24, "active": 24, "other": 0, "total": 72},
    "OTHER_STARTS_detail": "one timing/feasibility probe (seed 70000, founder+settle+400 steps) after "
                           "commit 1; read no reader series, delta, score or outcome; seed 70000 "
                           "permanently consumed and excluded from the panel (deviation D3). This "
                           "exceeds MAX_OTHER_OR_DIAGNOSTIC_STARTS=0 by one and is disclosed, not hidden.",
    "no_unused_start_repurposed": True,
}
disp = {
    "programme": "FRESH_SERIALIZED_QUOTIENT_BASIS_TRANSFER_00",
    "DISPOSITION": DISPOSITION,
    "parent": "16717582e7f0dfd371f21c56465e11113d8b6675",
    "decision_matrix": matrix,
    "headline_reading": {
        "cells": f"all 24 fresh carrier rows material (margins {CELL['margin_min']:.2f}-{CELL['margin_max']:.2f})",
        "frozen_P2": f"aggregate transfers (projected energy {P2['P2_PROJECTED_ENERGY']:.3e} > E_TAU "
                     f"{P2['E_TAU_FRESH']:.3e}; aggregate residual {P2['P2_OUTSIDE_RESIDUAL']:.3e} < tube "
                     f"{P2['TUBE_P2_LOBO']:.3e}) BUT {n_over}/12 blocks breach the per-block tube "
                     f"(over: {', '.join(f'{b} x{r:.2f}' for b,r in over_blocks.items())}); by the "
                     f"no-mean-concealment rule (T4) P2 does NOT transfer",
        "frozen_e2": f"incremental energy {E2['E2_INCREMENTAL_ENERGY']:.3e} < E_TAU floor "
                     f"{E2['E_TAU_FRESH']:.3e} and gated by the P2 per-block failure -> NOT_TRANSFERRED",
        "carrier_direction": f"the direct native carrier contrast is material in "
                             f"{E2['CO2_direct_material_blocks']}/12 blocks and concordant with the parent "
                             f"e2 orientation in {E2['CO1_concordant']}/12 -- a separately valid replication "
                             f"of the carrier EFFECT that does not depend on the frozen axis transferring",
        "fresh_quotient": f"fresh data, with its OWN affine fit, independently reproduces the parent's "
                          f"qualitative structure: relative at least two (I2/R0={FQ['ratios']['I2_over_R0']:.3f}, "
                          f"R1/R0={FQ['ratios']['R1_over_R0']:.3f}), second below absolute materiality",
        "geometry_note": f"the {n_over} breaching blocks are all NEAR geometry; recorded as a "
                         f"hypothesis-generating observation ONLY, not a tested effect (geometry NOT_TESTED)",
    },
    "what_this_is_not": "NOT a transfer of the parent P2/e2 object (it failed per-block). The fresh "
                        "relative-two structure is NEW structure, not object transfer, and does not "
                        "rescue the failed transfer.",
    "independent_units": 12, "start_ledger": start_ledger,
    "geometry_tested": "NOT_TESTED_IN_THIS_DESIGN", "allocation_tested": "NOT_TESTED_IN_THIS_DESIGN",
    "dose_tested": "NOT_TESTED_IN_THIS_DESIGN (historical 1x only; SQDT00 proved 2x inadmissible)",
    "TOMMY_ACTION_REQUIRED": False, "TOMMY_GIT_ACTION_REQUIRED": False,
    "PUSH_AUTHORIZED": False, "DRAFT_PR_AUTHORIZED": False, "WORKFLOW_TRIGGER_AUTHORIZED": False,
    "deviations": ["D0_inherited", "D1_inherited", "D2_inherited",
                   "D3_one_diagnostic_start_seed70000_no_outcome_read_seed_consumed",
                   "D4_full_field_checkpoints_kept_in_workspace_digested_bridge_limit"],
    "immutable_object_untouched": "FWL2_RELATIVE_QUOTIENT_BASIS_V1 was never refit, rescaled, "
                                  "recentered, rotated or re-versioned",
}
json.dump(disp, open(f"{OUT}/FSQBT00_FINAL_DISPOSITION.json", "w"), indent=1, default=str)
json.dump(start_ledger, open(f"{OUT}/FSQBT00_START_LEDGER.json", "w"), indent=1)
print("DISPOSITION:", DISPOSITION)
print("blocks over tube:", over_blocks)
print("start ledger:", {k: v for k, v in start_ledger.items() if isinstance(v, int)})
