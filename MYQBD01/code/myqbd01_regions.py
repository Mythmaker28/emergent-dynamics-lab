"""MYQBD01 §14-§16 — discovery-region construction and the terminal disposition.

The one-Y first-birth operator IS identifiable from the exact per-step organiser Q. The FULL
mobile candidate region additionally needs the two-Y / separation operator, which §11-§12 show
is not identifiable from an organiser-only ledger. This module builds what is constructible,
shows exactly where construction stops, and rules out structural preclusion.

No engine. Exact arithmetic over the recorded arms.
"""
from __future__ import annotations

import glob
import json
import math
import os

import numpy as np

OUT = "/home/claude/MYQBD01/out"
RAW = "/home/claude/OBFOR01/raw"
BURN_IN, HORIZON = 2000, 11000
Q_MAX = 28
TAU_SEP_MOBILE = 125.0
ALPHA_SURVIVAL, N_STAR, GAMMA_SEP = 0.5, 10.0, 0.5


def arm_Q(prefix):
    out = {}
    for p in sorted(glob.glob(os.path.join(RAW, "%s*.npz" % prefix))):
        z = np.load(p, allow_pickle=True)
        f = [str(x) for x in z["fields"]]
        q = z["series"][BURN_IN:HORIZON, f.index("Q")].astype(float)
        out[os.path.basename(p)[:-4]] = q
    return out


def main():
    mob = arm_Q("M__")

    # ---- what IS constructible: the one-Y first-birth diagnostic, per mobile arm ----
    # In the unclamped regime the expected number of first Y births over the window at coupling
    # kY, using the arm's OWN exact exposure, is B_i(kY) = kY * sum_t Q(t). This is identifiable.
    first_birth = []
    for a, q in mob.items():
        sq = float(q.sum())
        q10 = float(np.quantile(q, 0.10))
        # the kY at which the arm expects >= 1 first birth over the window
        kY_one = 1.0 / sq if sq > 0 else math.inf
        first_birth.append({"arm": a, "sum_Q": sq, "Q10": q10,
                            "kY_for_one_expected_first_birth": kY_one,
                            "has_positive_lower_tail_exposure": q10 > 0})
    kY_min = min(r["kY_for_one_expected_first_birth"] for r in first_birth)
    kY_max = max(r["kY_for_one_expected_first_birth"] for r in first_birth)
    any_positive_tail = any(r["has_positive_lower_tail_exposure"] for r in first_birth)

    # ---- what is NOT constructible, and why ----
    not_constructible = {
        "PERSISTENCE_beyond_first_birth": (
            "the lineage survival to T requires iterating the offspring operator past the first "
            "birth, i.e. the TWO_Y state. §11 proves that operator is not a branching process "
            "and is NOT_IDENTIFIABLE from an organiser-only ledger (co-located Y share one "
            "candidate pool; separated Y have different, unrecorded environments)."),
        "SEPARATION_and_THIRD_CENTRE": (
            "these hazards depend on descendant-position exposure Q_POSITION(x,t). §12 shows the "
            "archives record only the scalar organiser-cell exposure per step plus a single "
            "terminal spatial snapshot, so Q_POSITION for a separated descendant is "
            "unrecoverable."),
        "LOWER_BOUND_ON_beta": (
            "every mobile arm has Q10 = 0 (Q = 0 more than half the time), so even the "
            "first-birth exposure has no positive lower-tail floor: there is no positive "
            "statewise lower bound on the birth intensity derivable from these arms."),
        "FEEDBACK": (
            "§13: the archive has kY = 0, so an active lineage's SY depletion is absent; the "
            "environment is a rare-Y approximation controlled only for the first birth."),
    }

    # ---- rule OUT structural preclusion, explicitly ----
    # Under the MOST FAVOURABLE admissible environment (Q sustained at Q_MAX, no zero episodes,
    # no feedback), is a persisting one-Y-seeded lineage possible for some admissible (kY,muY)?
    def stable_survival(c, p, m, T=HORIZON):
        s = 1.0
        for _ in range(T):
            s = -math.expm1(math.log1p(-(1 - m) * s) + c * math.log1p(-p * (1 - m) * s))
        return s
    # most favourable: c = Q_MAX-relevant candidate pool, choose a point that is clearly super-
    # critical yet bounded, to witness that the operator does NOT forbid a window
    c_fav = 7                     # max candidate pool with nX>=1 (from the admissible enumeration)
    kY_fav, muY_fav = 1e-3, 1e-4
    p_fav = min(1.0, kY_fav * 4 * 1)     # unclamped
    R_fav = (1 - muY_fav) * (1 + c_fav * p_fav)
    surv_fav = stable_survival(c_fav, p_fav, muY_fav)
    structural = {
        "QUESTION": "does the exact operator prove NO admissible (kY,muY) can meet the frozen "
                    "mobile conditions under the MOST FAVOURABLE admissible environment?",
        "most_favourable_witness": {"c": c_fav, "kY": kY_fav, "muY": muY_fav,
                                    "R_mean_offspring": R_fav, "survival_to_T": surv_fav,
                                    "supercritical_and_survives": R_fav > 1 and surv_fav > 0.5},
        "STRUCTURAL_PRECLUSION_PROVED": False,
        "why_not": ("under a favourable-enough admissible environment a one-Y-seeded lineage is "
                    "supercritical and survives, so the operator does NOT forbid a window. The "
                    "obstruction is a MISSING LEDGER (descendant exposure) and MISSING "
                    "IDENTIFIABILITY (two-Y operator), which the freeze explicitly rules "
                    "inadmissible as structural proof."),
    }

    # ---- the requirement checklist for the positive disposition ----
    req = {
        "ALL_28_ARMS_ACCOUNTED_FOR": True,
        "ALL_14_MOBILE_ARMS_INCLUDED": len(mob) == 14,
        "NO_FRAME_PSEUDOREPLICATION": True,
        "Q_EVENT_PHASE_RESOLVED": True,                 # Q_LEDGER_EVENT_EXACT
        "MOBILE_SPATIAL_ENVIRONMENT_RESOLVED": False,    # §12
        "ONE_Y_OPERATOR_VERIFIED": True,                # §10
        "TWO_Y_STATE_OPERATOR_VERIFIED": False,          # §11
        "FROZEN_ENVIRONMENT_ERROR_CONTROLLED": False,    # §13, only first birth
        "NO_TARGET_DERIVED_Y_OUTCOME": True,             # Q is environmental, not a Y outcome
        "MOBILE_REGION_POSITIVE_WIDTH": "NOT_CONSTRUCTIBLE",
        "ALL_ARM_INTERSECTION_POSITIVE_WIDTH": "NOT_CONSTRUCTIBLE",
        "NO_SINGLE_ARM_CREATES_THE_REGION": "N/A_region_not_constructible",
        "NO_FAVORABLE_SUBSET_SELECTION": True,
        "SCIENTIFIC_RUNS_USED_ZERO": True,
    }
    positive_ok = all(v is True for v in req.values())

    disposition = "EXISTING_Q_DATA_INSUFFICIENT__PROSPECTIVE_Q_CALIBRATION_REQUIRED"

    out = {
        "SECTION": "MYQBD01 §14-§16 discovery region and disposition",
        "WHAT_IS_CONSTRUCTIBLE": {
            "one_Y_first_birth_diagnostic_per_mobile_arm": first_birth,
            "kY_for_one_expected_first_birth_range": [kY_min, kY_max],
            "any_arm_has_positive_lower_tail_exposure": any_positive_tail,
            "reading": ("the first-birth intensity kY * sum_t Q(t) is identifiable per arm, but "
                        "it only says a first birth can occur; it says nothing about "
                        "persistence, separation or a third centre.")},
        "WHAT_IS_NOT_CONSTRUCTIBLE": not_constructible,
        "STRUCTURAL_PRECLUSION_CHECK": structural,
        "POSITIVE_DISPOSITION_REQUIREMENTS": req,
        "POSITIVE_DISPOSITION_ATTAINABLE": positive_ok,
        "EXACT_MISSING_ITEMS": [
            "per-step position-resolved environmental arrays (nX, nSY, free) for the mobile "
            "descendant positions (§12)",
            "an identifiable two-Y / separated-lineage operator, which needs the above (§11)",
            "a controlled frozen-environment feedback error beyond the first birth (§13)",
            "a positive lower-tail exposure (every mobile arm has Q10 = 0)",
        ],
        "FINAL_DISPOSITION": disposition,
        "WHY_NOT_POSITIVE": ("MOBILE_SPATIAL_ENVIRONMENT_RESOLVED and TWO_Y_STATE_OPERATOR_"
                             "VERIFIED are both false; the mobile candidate region is not "
                             "constructible from an organiser-only ledger."),
        "WHY_NOT_STRUCTURAL_PRECLUSION": structural["why_not"],
        "TARGET_SELECTION": "NOT_PERFORMED (only after a positive disposition)",
        "NEXT_SCIENTIFIC_ELIGIBILITY": "PROSPECTIVE_Q_ENVIRONMENT_CALIBRATION_01",
    }
    json.dump({"MOBILE_ARM_REGIONS": out["WHAT_IS_CONSTRUCTIBLE"]},
              open(f"{OUT}/MYQBD01_MOBILE_ARM_REGIONS.json", "w"), indent=1, default=str)
    json.dump(out, open(f"{OUT}/MYQBD01_DISCOVERY_REGION.json", "w"), indent=1, default=str)

    print("constructible: one-Y first-birth kY range [%.2e, %.2e]; any positive lower tail: %s"
          % (kY_min, kY_max, any_positive_tail))
    print("structural preclusion proved:", structural["STRUCTURAL_PRECLUSION_PROVED"],
          "(favourable witness survives:", structural["most_favourable_witness"]
          ["supercritical_and_survives"], ")")
    print("\npositive-disposition requirements:")
    for k, v in req.items():
        print("   %-40s %s" % (k, v))
    print("\nFINAL_DISPOSITION =", disposition)


if __name__ == "__main__":
    main()
