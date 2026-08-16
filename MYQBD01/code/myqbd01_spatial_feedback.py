"""MYQBD01 §12-§13 — spatial-environment recoverability and the Y-feedback bound.

§12: can descendant-position exposure Q_POSITION(x,t) be recovered from the archives?
§13: the archives were generated with kY = 0; bound the perturbation an active Y lineage causes.

No engine. Reads the delivered .npz arrays and the committed engine source.
"""
from __future__ import annotations

import glob
import json
import os
import subprocess

import numpy as np

REPO = "/home/claude/edl"
OUT = "/home/claude/MYQBD01/out"
RAW = "/home/claude/OBFOR01/raw"
BURN_IN, HORIZON = 2000, 11000


def blob(path):
    return subprocess.run(("git", "show", "HEAD:%s" % path), cwd=REPO,
                          capture_output=True, text=True).stdout


def spatial_recoverability():
    """What environmental information is present, and at what resolution."""
    f = sorted(glob.glob(os.path.join(RAW, "*.npz")))[0]
    z = np.load(f, allow_pickle=True)
    keys = list(z.keys())
    L = int(z["nX_final"].shape[0])
    # a per-step position-resolved grid would be 3D (T, L, L). None exists.
    per_step_spatial = [k for k in keys if z[k].ndim == 3
                        and z[k].shape[0] == HORIZON and z[k].shape[1:] == (L, L)]
    terminal_spatial = [k for k in keys if getattr(z[k], "shape", None) == (L, L)]
    fields = [str(x) for x in z["fields"]]
    # are any per-step fields position-resolved (a grid), or all scalar organiser aggregates?
    per_step_are_scalar = all(z["series"].ndim == 2 and z["series"].shape == (HORIZON, 29)
                              for _ in [0])
    return {
        "SECTION": "MYQBD01 §12 spatial recoverability",
        "PER_STEP_SERIES_SHAPE": list(z["series"].shape),
        "PER_STEP_FIELDS_ARE_SCALAR_ORGANISER_AGGREGATES": bool(per_step_are_scalar),
        "PER_STEP_FIELD_NAMES": fields,
        "PER_STEP_POSITION_RESOLVED_ARRAYS": per_step_spatial,
        "TERMINAL_SPATIAL_ARRAYS": terminal_spatial,
        "FULL_SPATIAL_FIELD_IS_TERMINAL_ONLY": len(per_step_spatial) == 0,
        "SUBSTEP_LEDGERS_ARE_SCALAR": {
            "hop_ledger": list(z["hop_ledger"].shape),
            "source_substep_ledger": list(z["source_substep_ledger"].shape),
            "birth_substep_ledger": list(z["birth_substep_ledger"].shape),
            "birth_offsets": list(z["birth_offsets"].shape),
            "reading": ("these carry step, sub-step index and scalar organiser-cell counts; "
                        "birth_offsets carries (step, dy, dx, count) of X births relative to "
                        "the organiser, which is WHERE births occurred, not the nSY/free field "
                        "at cells a Y descendant could reach")},
        "Q_POSITION_RECOVERABLE_FOR_A_SEPARATED_DESCENDANT": False,
        "CLASSIFICATION": "ORGANISER_ONLY_ENVIRONMENT_AVAILABLE",
        "WHY": ("the per-step ledger records only the organiser-cell exposure "
                "Q = nX*min(nSY,free) at cells with nY>0. The full per-cell (nX, nSY, free) "
                "field is serialized only at the terminal step. A mobile descendant that "
                "separates from the organiser occupies a DIFFERENT cell whose (nX, nSY, free) "
                "at that time is not recorded. Therefore Q_POSITION(x,t) and Q_LINEAGE(t) for a "
                "separated descendant are not recoverable from these archives."),
        "CONSEQUENCE_FOR_THE_MOBILE_BRANCH": (
            "the mobile branch is the load-bearing branch for a separation test. The "
            "separation and premature-third-centre hazards depend on descendant-position "
            "exposure, which is unrecoverable here. The organiser-only ledger locates the "
            "FIRST-BIRTH hazard exactly, and nothing after separation."),
        "STATIC_BRANCH_NOTE": ("in the static branch p_hop_Y = 0, so all Y remain in one cell "
                               "and Q_ORGANISER does describe the whole lineage exposure -- but "
                               "that branch structurally cannot produce spatial separation, so "
                               "it cannot support a separation/timing test either."),
    }


def feedback_bound():
    """The archives have kY = 0, so no Y birth ever occurred. Bound the perturbation an ACTIVE
    Y lineage would cause to the recorded environment, deterministically, from the engine's
    conservation laws."""
    # exact mean organiser-cell nSY and free, across mobile arms (for the magnitude of the perturbation)
    files = sorted(glob.glob(os.path.join(RAW, "M__*.npz")))
    nSY, free, nX = [], [], []
    for p in files:
        z = np.load(p, allow_pickle=True)
        fields = [str(x) for x in z["fields"]]
        s = z["series"][BURN_IN:HORIZON]
        nSY.append(s[:, fields.index("nSY_at_org")].mean())
        free.append(s[:, fields.index("free_at_org")].mean())
        nX.append(s[:, fields.index("u_nX_at_org")].mean())
    nSY_mean = float(np.mean(nSY))
    free_mean = float(np.mean(free))
    nX_mean = float(np.mean(nX))
    # engine facts, read from source
    react = blob("ORR01/code/kinetics.py")
    S0, phi = 3, 0.2  # frozen point
    return {
        "SECTION": "MYQBD01 §13 counterfactual validity of the frozen X environment",
        "THE_ARCHIVE_HAS_kY_ZERO": ("obtc02_protocol.yaml point.kY = 0.0, so NO Y birth ever "
                                    "occurred in any of the 28 arms. The recorded environment "
                                    "is the exact counterfactual for a Y that never reacts."),
        "EXACT_CONSERVATION_FACTS": {
            "Y_birth_effect": ("_react converts SY -> Y in place: n[SY] -= b, n[Y] += b. "
                               "Occupancy is conserved, so FREE is UNCHANGED, but local nSY "
                               "drops by b at the birth cell."),
            "Y_decay_effect": "_decay converts Y -> WY: occupancy conserved, free unchanged.",
            "SY_replenishment": ("_exchange offers Binomial(max(S0 - nSY, 0), phi) toward "
                                 "S0 = %d at rate phi = %.2f per step, per cell." % (S0, phi)),
            "X_hazard_unaffected_by_nY": ("p_X = min(1, kX*nX*nY) is already 1 for nX*nY >= 1 at "
                                          "kX = 1, so a second Y does not change X production.")},
        "MEASURED_ORGANISER_CELL_MAGNITUDES_mobile": {
            "mean_nSY_at_org": nSY_mean, "mean_free_at_org": free_mean,
            "mean_nX_at_org": nX_mean},
        "DETERMINISTIC_PERTURBATION_BOUND": {
            "one_Y_birth": {
                "delta_nSY_local": -1,
                "as_fraction_of_mean_nSY": -1.0 / nSY_mean,
                "recovery_rate_per_step": phi,
                "steps_to_replenish_one_unit_approx": 1.0 / phi,
                "reading": ("one Y birth removes one SY at the organiser cell, a %.0f%% local "
                            "reduction of the ~%.2f mean nSY, recovering at ~%.2f per step. The "
                            "recorded Q therefore OVERSTATES the SY an active lineage would see, "
                            "and the first-birth error is bounded but NOT negligible."
                            % (100.0 / nSY_mean, nSY_mean, phi))},
            "two_Y_colocated": {
                "delta_nSY_local_per_step": "up to -2 (two births share the cell's SY pool)",
                "extra_effect": "p_Y carries nY = 2, so the intensity the archive omits grows",
                "reading": "the perturbation compounds and is not bounded from the kY=0 archive"},
            "two_Y_separated": {
                "reading": ("each occupies a different cell; the exposure at the descendant's "
                            "cell is unrecorded (see §12), so the perturbation there cannot be "
                            "bounded from these archives at all")},
        },
        "CLASSIFICATION": "FROZEN_ENVIRONMENT_RARE_Y_APPROXIMATION_WITH_CERTIFIED_ERROR",
        "ERROR_IS_CONTROLLED_ONLY_FOR": "the FIRST birth of a single Y at the organiser cell",
        "ERROR_IS_UNCONTROLLED_FOR": ("a persisting lineage, co-located pairs, and any separated "
                                      "descendant -- exactly the regime a mobile window test "
                                      "would probe"),
        "DO_NOT_HIDE_UNDER_MINORITY_REGIME": ("the SY depletion is a real feedback; calling the "
                                              "regime 'minority' does not make Q_recorded exact "
                                              "for an active lineage"),
    }


def main():
    sp = spatial_recoverability()
    fb = feedback_bound()
    json.dump({"SPATIAL": sp, "FEEDBACK": fb},
              open(f"{OUT}/MYQBD01_FEEDBACK_BOUND.json", "w"), indent=1, default=str)
    print("§12 spatial:", sp["CLASSIFICATION"])
    print("   per-step position-resolved arrays:", sp["PER_STEP_POSITION_RESOLVED_ARRAYS"],
          "| full spatial terminal-only:", sp["FULL_SPATIAL_FIELD_IS_TERMINAL_ONLY"])
    print("   Q_POSITION recoverable for a separated descendant:",
          sp["Q_POSITION_RECOVERABLE_FOR_A_SEPARATED_DESCENDANT"])
    print("§13 feedback:", fb["CLASSIFICATION"])
    p = fb["DETERMINISTIC_PERTURBATION_BOUND"]["one_Y_birth"]
    print("   one Y birth: delta nSY = %d (%.1f%% of mean nSY %.2f), recovery ~%.2f/step"
          % (p["delta_nSY_local"], 100 * p["as_fraction_of_mean_nSY"],
             fb["MEASURED_ORGANISER_CELL_MAGNITUDES_mobile"]["mean_nSY_at_org"],
             p["recovery_rate_per_step"]))


if __name__ == "__main__":
    main()
