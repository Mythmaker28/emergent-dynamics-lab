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

import myqbd01_seal_audits as AUD

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
    # Under a FAVOURABLE admissible environment, is a persisting one-Y-seeded lineage possible
    # for some admissible (kY, muY)?
    # SEAL REPAIR (review F20): the pre-seal docstring said "Q sustained at Q_MAX". That framing
    # was WRONG -- the in-box witness uses exposure c*nX = 12, not Q_MAX = 28. The framing is
    # dropped and the witness is now stated against the arms' OWN measured magnitudes, with a
    # third witness added at the measured mean so the claim no longer rests on an inflated pool.
    def stable_survival(c, p, m, T=HORIZON):
        s = 1.0
        for _ in range(T):
            s = -math.expm1(math.log1p(-(1 - m) * s) + c * math.log1p(-p * (1 - m) * s))
        return s
    # C2 repair: use an IN-BOX ADMISSIBLE witness, at the discovery-scale kY (not 25x above it),
    # so "the operator does not forbid a window" is demonstrated at admissible (kY, muY).
    # kY at the first-birth scale (~3.5e-5), muY at the inherited MTW01 scale (~1.95e-6),
    # c at the mean organiser candidate pool. Also report the larger favourable witness for
    # contrast, clearly labelled as above-scale.
    # measured, not assumed: the mobile arms' own mean candidate pool and mean nX at the organiser
    cand_mean = float(np.mean([np.mean(q) for q in
                               [np.load(f, allow_pickle=True)["series"]
                                [BURN_IN:HORIZON,
                                 [str(x) for x in np.load(f, allow_pickle=True)["fields"]]
                                 .index("cand_Y_at_org")].astype(float)
                                for f in sorted(glob.glob(os.path.join(RAW, "M__*.npz")))]]))
    nX_mean = float(np.mean([np.mean(q) for q in
                             [np.load(f, allow_pickle=True)["series"]
                              [BURN_IN:HORIZON,
                               [str(x) for x in np.load(f, allow_pickle=True)["fields"]]
                               .index("u_nX_at_org")].astype(float)
                              for f in sorted(glob.glob(os.path.join(RAW, "M__*.npz")))]]))
    c_box = 3                     # SEAL REPAIR (F20): this is 3.12x the MEASURED mean pool
    kY_box, muY_box = 4e-5, 1.9511206603301160e-06
    p_box = min(1.0, kY_box * 4 * 1)
    R_box = (1 - muY_box) * (1 + c_box * p_box)
    surv_box = stable_survival(c_box, p_box, muY_box)
    # SEAL REPAIR (F20/F21): a third witness at the arms' OWN measured magnitudes, so
    # non-preclusion no longer rests on any inflated pool.
    p_meas = min(1.0, kY_box * nX_mean * 1)
    R_meas = (1 - muY_box) * (1 + cand_mean * p_meas)
    surv_meas = stable_survival(cand_mean, p_meas, muY_box)
    c_fav, kY_fav, muY_fav = 7, 1e-3, 1e-4
    p_fav = min(1.0, kY_fav * 4 * 1)
    R_fav = (1 - muY_fav) * (1 + c_fav * p_fav)
    surv_fav = stable_survival(c_fav, p_fav, muY_fav)
    structural = {
        "QUESTION": "does the exact operator prove NO admissible (kY,muY) can meet the frozen "
                    "mobile conditions under the MOST FAVOURABLE admissible environment?",
        "in_box_admissible_witness": {
            "c": c_box, "kY": kY_box, "muY": muY_box,
            "note": "kY at the first-birth discovery scale (~3.5e-5), muY at the inherited "
                    "MTW01 scale",
            "SEAL_CORRECTION_F20": ("the pre-seal comment claimed c = 3 was 'near the mean "
                                    "organiser candidate pool'. It is not: the measured mean "
                                    "cand_Y_at_org over the 14 mobile arms is %.6f, so c = 3 is "
                                    "%.2fx it, and the witness exposure c*nX = 12 is %.2fx the "
                                    "arms' own mean Q = %.6f. The claim is corrected here and a "
                                    "MEASURED-magnitude witness is added below."
                                    % (cand_mean, 3.0 / cand_mean, 12.0 / 3.169730, 3.169730)),
            "R_mean_offspring": R_box, "survival_to_T": surv_box,
            "supercritical": R_box > 1},
        "measured_environment_witness": {
            "c": cand_mean, "kY": kY_box, "muY": muY_box, "nX": nX_mean,
            "note": "the arms' OWN measured mean candidate pool and mean nX at the organiser; "
                    "no inflated magnitude anywhere",
            "R_mean_offspring": R_meas, "survival_to_T": surv_meas,
            "supercritical": R_meas > 1},
        "most_favourable_witness": {"c": c_fav, "kY": kY_fav, "muY": muY_fav,
                                    "ABOVE_DISCOVERY_SCALE": True,
                                    "R_mean_offspring": R_fav, "survival_to_T": surv_fav,
                                    "supercritical_and_survives": R_fav > 1 and surv_fav > 0.5},
        "STRUCTURAL_PRECLUSION_PROVED": False,
        "why_not": ("even at the arms' OWN MEASURED magnitudes (c = %.6f, nX = %.6f, kY = 4e-5, "
                    "muY = 1.95e-6) the one-Y-seeded lineage is supercritical (R = %.9f > 1), "
                    "and at the in-box point (c = 3) R = %.6f > 1, so the operator does NOT "
                    "forbid a window at admissible magnitudes. The obstruction is a MISSING LEDGER (descendant exposure) and "
                    "MISSING IDENTIFIABILITY (two-Y operator), which the freeze explicitly "
                    "rules inadmissible as structural proof."
                    % (cand_mean, nX_mean, R_meas, R_box)),
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
        # SEAL REPAIR (review F25): was a hardcoded literal; now DERIVED by an AST audit of
        # every data access in all eight modules.
        "NO_TARGET_DERIVED_Y_OUTCOME": AUD.target_derived_audit()["NO_TARGET_DERIVED_Y_OUTCOME"],
        "MOBILE_REGION_POSITIVE_WIDTH": "NOT_CONSTRUCTIBLE",
        "ALL_ARM_INTERSECTION_POSITIVE_WIDTH": "NOT_CONSTRUCTIBLE",
        "NO_SINGLE_ARM_CREATES_THE_REGION": "N/A_region_not_constructible",
        "NO_FAVORABLE_SUBSET_SELECTION": True,
        # SEAL REPAIR (review F27/F30): was a literal resting on a sentinel installed in 1 of 8
        # modules; now DERIVED by a static proof that no module imports an engine at all.
        "SCIENTIFIC_RUNS_USED_ZERO":
            AUD.zero_run_static_proof()["NO_MODULE_CAN_CONSTRUCT_A_WORLD"],
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
    print("structural preclusion proved:", structural["STRUCTURAL_PRECLUSION_PROVED"])
    print("   in-box witness   c=3        R=%.9f supercritical=%s"
          % (structural["in_box_admissible_witness"]["R_mean_offspring"],
             structural["in_box_admissible_witness"]["supercritical"]))
    print("   MEASURED witness c=%.6f R=%.9f supercritical=%s"
          % (cand_mean, R_meas, R_meas > 1))
    print("\npositive-disposition requirements:")
    for k, v in req.items():
        print("   %-40s %s" % (k, v))
    print("\nFINAL_DISPOSITION =", disposition)


if __name__ == "__main__":
    main()
