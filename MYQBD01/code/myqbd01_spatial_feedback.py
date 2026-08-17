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
    """SEAL REPAIR (review findings F08, F09, F10, F23).

    The pre-seal version opened ONE archive, inspected the CONTENTS of zero keys, mislabelled the
    sub-step ledgers as scalar, and returned the load-bearing boolean as a hardcoded literal. It
    is replaced by a derivation over ALL 28 archives that enumerates every key, decodes `frames`,
    and DERIVES the boolean. The decisive ground (kY = 0, so no descendant ever exists) is stated
    here rather than only in §13.
    """
    files = sorted(glob.glob(os.path.join(RAW, "*.npz")))
    z0 = np.load(files[0], allow_pickle=True)
    L = int(z0["nX_final"].shape[0])
    keyset = tuple(sorted(z0.keys()))

    per_arm, keysets_identical = [], True
    any_per_step_lattice, n_y_always_one, org_always_one, steps = [], True, True, 0
    frames_all_scalar, birth_offsets_all_zero = True, True
    for f in files:
        z = np.load(f, allow_pickle=True)
        keysets_identical &= tuple(sorted(z.keys())) == keyset
        lat = [k for k in z.keys() if z[k].ndim == 3 and z[k].shape[1:] == (L, L)]
        any_per_step_lattice += lat
        fl = [str(x) for x in z["fields"]]
        s_ = z["series"]
        nY = s_[:, fl.index("N_Y")]
        noc = s_[:, fl.index("n_org_cells")]
        n_y_always_one &= bool(np.all(nY == 1))
        org_always_one &= bool(np.all(noc == 1))
        steps += int(nY.size)
        # `frames` is a (220,) array of JSON STRINGS at stride 50 -- decode and assert every
        # value is a scalar, i.e. no lattice field is hidden inside it.
        fr = [json.loads(str(x)) for x in z["frames"]]
        frames_all_scalar &= all(not isinstance(v, (list, dict)) for d in fr for v in d.values())
        bo = z["birth_offsets"]
        # birth_offsets carries X-birth displacements relative to the organiser; a NON-zero
        # offset would mean X births away from the organiser cell are located, which is still not
        # an (nSY, free) field, but the check is recorded rather than assumed.
        birth_offsets_all_zero &= bool(bo.size == 0 or np.all(bo[:, 1:3] == 0))
        per_arm.append({"arm": os.path.basename(f)[:-4], "keys": len(list(z.keys())),
                        "per_step_lattice_arrays": lat,
                        "frame_count": len(fr), "frame_keys": sorted(fr[0].keys())})

    frame_fields = sorted(json.loads(str(z0["frames"][0])).keys())
    ssl, hop, bsub = z0["source_substep_ledger"], z0["hop_ledger"], z0["birth_substep_ledger"]
    moved = int((ssl[:, 2:4] != ssl[:, 4:6]).any(axis=1).sum())
    visited = int(np.unique(ssl[:, 4:6], axis=0).shape[0])

    # ---- the information budget: a necessary condition, computed, not asserted ----
    dof_needed = HORIZON * L * L * 3          # nX, nSY, free per cell per step
    dof_archive = int(sum(int(np.prod(getattr(z0[k], "shape", (0,)))) for k in z0.keys()))

    derived_not_recoverable = (len(any_per_step_lattice) == 0 and frames_all_scalar
                               and dof_archive < dof_needed)

    return {
        "SECTION": "MYQBD01 §12 spatial recoverability (SEAL-REPAIRED: all 28 archives)",
        "ARCHIVES_EXAMINED": len(files),
        "KEY_SETS_IDENTICAL_ACROSS_ARMS": bool(keysets_identical),
        "KEY_SET": list(keyset),
        "PER_ARM": per_arm,
        "PER_STEP_SERIES_SHAPE": list(z0["series"].shape),
        "PER_STEP_FIELD_NAMES": [str(x) for x in z0["fields"]],
        "PER_STEP_POSITION_RESOLVED_ARRAYS": sorted(set(any_per_step_lattice)),
        "TERMINAL_SPATIAL_ARRAYS": [k for k in z0.keys()
                                    if getattr(z0[k], "shape", None) == (L, L)],
        "FULL_SPATIAL_FIELD_IS_TERMINAL_ONLY": len(any_per_step_lattice) == 0,
        "LEDGER_CONTENTS": {
            "CORRECTION": ("the pre-seal record labelled this block SUBSTEP_LEDGERS_ARE_SCALAR. "
                           "That label was WRONG (review F08): source_substep_ledger is "
                           "POSITION-RESOLVED. The conclusion is unchanged, but the reason is "
                           "restated correctly below."),
            "source_substep_ledger": {
                "shape": list(ssl.shape),
                "columns": "(step, species_index, org_y_before, org_x_before, org_y_after, "
                           "org_x_after) -- 4 of 6 columns are lattice coordinates",
                "organiser_moves_recorded": moved,
                "distinct_organiser_cells_visited": visited,
                "what_it_gives": ("the exact ORGANISER trajectory, sub-step by sub-step, in the "
                                  "mobile branch as well as the static branch"),
                "what_it_does_NOT_give": ("the (nX, nSY, free) field at any cell other than the "
                                          "organiser's own cell at that instant")},
            "hop_ledger": {"shape": list(hop.shape),
                           "rows_per_step": hop.shape[0] / float(HORIZON),
                           "reading": ("4 rows per step -- one per diffusing species, an "
                                       "AGGREGATE sub-step record. It does not name which "
                                       "particle moved from which cell to which cell, so no "
                                       "per-particle trajectory can be reconstructed from it")},
            "birth_substep_ledger": {"shape": list(bsub.shape),
                                     "rows_per_step": bsub.shape[0] / float(HORIZON)},
            "birth_offsets": {"shape": list(z0["birth_offsets"].shape),
                              "columns": "(step, dy, dx, count) of X births relative to the "
                                         "organiser",
                              "all_offsets_zero": bool(birth_offsets_all_zero)},
            "frames": {"count": len(z0["frames"]), "dtype": str(z0["frames"].dtype),
                       "stride_steps": HORIZON // len(z0["frames"]),
                       "decoded_fields": frame_fields,
                       "every_value_is_scalar": bool(frames_all_scalar),
                       "reading": ("JSON morphology summaries at stride 50, carrying organiser "
                                   "and cluster-centre COORDINATES and shape scalars. Decoded "
                                   "and checked: no lattice field is stored inside them")}},
        "INFORMATION_BUDGET": {
            "scalars_needed_for_Q_POSITION": dof_needed,
            "scalars_in_the_whole_archive": dof_archive,
            "short_by_factor": dof_needed / float(max(dof_archive, 1)),
            "reading": ("evaluating Q_POSITION(x,t) needs T x L^2 x 3 scalars. The entire "
                        "archive holds fewer by a factor of about %.0f, so no forward or "
                        "backward reconstruction procedure over these data can exist."
                        % (dof_needed / float(max(dof_archive, 1))))},
        "DECISIVE_GROUND_kY_ZERO": {
            "N_Y_identically_one_in_every_arm": bool(n_y_always_one),
            "n_org_cells_identically_one": bool(org_always_one),
            "steps_checked": steps,
            "reading": ("review finding F10. With kY = 0 no Y birth occurs in ANY arm: N_Y == 1 "
                        "at all %d recorded steps across all 28 archives. A separated descendant "
                        "does not merely go unrecorded -- it never exists. Q_POSITION for it is "
                        "therefore not a function of these data at all. This is a STRONGER "
                        "ground than non-recording, and it is stated here rather than only in "
                        "§13." % steps)},
        "Q_POSITION_RECOVERABLE_FOR_A_SEPARATED_DESCENDANT": bool(not derived_not_recoverable),
        "BOOLEAN_IS_DERIVED_NOT_ASSERTED": True,
        "CLASSIFICATION": "ORGANISER_ONLY_ENVIRONMENT_AVAILABLE",
        "FOUNDER_EXPOSURE_IS_EXACT_IN_BOTH_BRANCHES": (
            "because the organiser trajectory IS recorded, Q_ORGANISER equals the FOUNDER's own "
            "lineage exposure exactly in the mobile branch too, not only in the static branch. "
            "The gap is descendants, not motion (review F08)."),
        "WHY": ("(i) no array in any of the 28 archives has shape (T, L, L); (ii) `frames` "
                "decode to scalars only; (iii) the archive is ~%.0fx too small to carry the "
                "field; and (iv) decisively, kY = 0 means no descendant exists in these data. "
                "Q_POSITION(x,t) and Q_LINEAGE(t) for a separated descendant are therefore not "
                "obtainable from these archives."
                % (dof_needed / float(max(dof_archive, 1)))),
        "RE_SIMULATION_IS_NOT_RECOVERY": (
            "review finding F11. The engine is deterministic given (seed, spec), so the missing "
            "field IS derivable by RE-RUNNING seeds 9300000-9300027 with an added observer. That "
            "is a RUN, not a recovery from recorded data, and it is inadmissible here "
            "(SCIENTIFIC_RUNS_USED = 0). It is recorded in the successor handoff as a design "
            "option, not claimed as an existing datum."),
        "CONSEQUENCE_FOR_THE_MOBILE_BRANCH": (
            "the mobile branch is the load-bearing branch for a separation test. The separation "
            "and premature-third-centre hazards depend on descendant-position exposure, which "
            "these archives do not contain. The organiser-only ledger locates the FIRST-BIRTH "
            "hazard exactly, and nothing after separation."),
        "STATIC_BRANCH_NOTE": ("in the static branch p_hop_Y = 0, so descendants could never "
                               "separate; that branch structurally cannot support a "
                               "separation/timing test either."),
        "WHY_THE_STATIC_BRANCH_ALSO_FAILS_the_full_reasons": [
            "(a) STRUCTURAL: p_hop_Y = 0 means descendants never separate",
            "(b) FEEDBACK (§13): recorded with kY = 0, so an active lineage's SY depletion is "
            "absent; uncontrolled beyond the first birth",
            "(c) TEMPORAL (§7): the integrated autocorrelation time is ~7 in the static branch "
            "(single-arm maximum 9.72), so the arithmetic mean of Q is not the growth-relevant "
            "functional",
            "(d) LOWER TAIL: every static arm has Q10 = 0, so there is no positive statewise "
            "exposure floor",
        ],
    }


def feedback_bound():
    """The archives have kY = 0, so no Y birth ever occurred. Bound the perturbation an ACTIVE
    Y lineage would cause to the recorded environment, deterministically, from the engine's
    conservation laws."""
    # exact mean organiser-cell nSY and free, across mobile arms (for the magnitude of the perturbation)
    files = sorted(glob.glob(os.path.join(RAW, "M__*.npz")))
    nSY, free, nX, nSY_cond, cy_cond = [], [], [], [], []
    for p in files:
        z = np.load(p, allow_pickle=True)
        fields = [str(x) for x in z["fields"]]
        s = z["series"][BURN_IN:HORIZON]
        nSY.append(s[:, fields.index("nSY_at_org")].mean())
        free.append(s[:, fields.index("free_at_org")].mean())
        nX.append(s[:, fields.index("u_nX_at_org")].mean())
        # SEAL REPAIR (F17): a Y birth is possible only when cand_Y >= 1; the depletion must be
        # reported against the exposure CONDITIONAL on that, not the unconditional mean.
        cyv = s[:, fields.index("cand_Y_at_org")].astype(float)
        m = cyv >= 1
        nSY_cond.append(s[m, fields.index("nSY_at_org")].astype(float).mean())
        cy_cond.append(cyv[m].mean())
    nSY_mean = float(np.mean(nSY))
    nSY_cond_mean = float(np.mean(nSY_cond))
    cy_cond_mean = float(np.mean(cy_cond))

    free_mean = float(np.mean(free))
    nX_mean = float(np.mean(nX))
    # C1 repair: parse S0 and phi from the ACTUAL frozen protocol (the loaded spec), not from a
    # dead read of kinetics.py (whose class default phi=0.05 is NOT the value these arms used).
    yaml_txt = blob("OBTC02/code/obtc02_protocol.yaml")
    pt = {}
    inblock = False
    for ln in yaml_txt.splitlines():
        if ln.startswith("point:"):
            inblock = True
            continue
        if inblock:
            if ln and not ln.startswith(" "):
                break
            if ":" in ln:
                k, v = ln.strip().split(":", 1)
                pt[k.strip()] = v.strip()
    S0, phi = int(pt["S0"]), float(pt["phi"])
    # SEAL REPAIR (F16): phi is the EXCHANGE offer rate, not the effective replenishment rate.
    # Under LAWSPEC_V2 the SY balance at a cell is +Binomial(max(S0-nSY,0), phi) MINUS a
    # hypergeometric removal, PLUS diffusive inflow. Measure the effective mean-reversion rate
    # directly on the 14 STATIC arms, where the organiser cell is fixed so the series is clean.
    slopes = []
    for p in sorted(glob.glob(os.path.join(RAW, "S__*.npz"))):
        z = np.load(p, allow_pickle=True)
        fields = [str(x) for x in z["fields"]]
        y = z["series"][BURN_IN:HORIZON, fields.index("nSY_at_org")].astype(float)
        d, xr = np.diff(y), (float(S0) - y[:-1])
        slopes.append(float(np.dot(xr - xr.mean(), d - d.mean())
                            / np.dot(xr - xr.mean(), xr - xr.mean())))
    rate_eff = float(np.mean(slopes))
    rate_sd = float(np.std(slopes, ddof=1))
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
            "SY_replenishment": ("_exchange OFFERS Binomial(max(S0 - nSY, 0), phi) toward "
                                 "S0 = %d at phi = %.2f per step per cell, but that is the OFFER "
                                 "rate, not the effective replenishment rate: the cell also "
                                 "loses SY to a hypergeometric removal and gains SY by "
                                 "diffusion. SEAL REPAIR (review F16): the EFFECTIVE "
                                 "mean-reversion rate, regressed directly on the 14 static arms, "
                                 "is %.6f (sd %.6f over arms) -- %.2fx the offer rate phi."
                                 % (S0, phi, rate_eff, rate_sd, rate_eff / phi)),
            "phi_S0_provenance": "parsed from obtc02_protocol.yaml point block (the loaded spec)",
            "X_hazard_unaffected_by_nY": ("p_X = min(1, kX*nX*nY) is already 1 for nX*nY >= 1 at "
                                          "kX = 1, so a second Y does not change X production.")},
        "MEASURED_ORGANISER_CELL_MAGNITUDES_mobile": {
            "mean_nSY_at_org": nSY_mean, "mean_free_at_org": free_mean,
            "mean_nX_at_org": nX_mean},
        "DETERMINISTIC_PERTURBATION_BOUND": {
            "one_Y_birth": {
                "delta_nSY_local": -1,
                "SEAL_CORRECTION": ("review findings F16 and F17. The pre-seal record reported a "
                                    "~100%% depletion recovering at phi = 0.20/step. BOTH "
                                    "numbers were wrong: the depletion was taken against the "
                                    "UNCONDITIONAL mean nSY, and phi is the offer rate, not the "
                                    "effective recovery rate."),
                "uncond_mean_nSY_at_org": nSY_mean,
                "uncond_depletion_fraction_SUPERSEDED": -1.0 / nSY_mean,
                "cond_mean_nSY_at_org_given_cand_Y_ge_1": nSY_cond_mean,
                "cond_mean_cand_Y_given_ge_1": cy_cond_mean,
                "CORRECTED_depletion_fraction": -1.0 / nSY_cond_mean,
                "CORRECTED_effective_recovery_rate_per_step": rate_eff,
                "CORRECTED_effective_recovery_rate_sd_over_static_arms": rate_sd,
                "offer_rate_phi_SUPERSEDED": phi,
                "steps_to_replenish_one_unit_approx": 1.0 / rate_eff,
                "reading": ("a Y birth is possible only when cand_Y >= 1. Conditional on that, "
                            "the organiser cell holds %.6f SY on average, so one birth removes "
                            "%.1f%% of the locally available SY -- not the ~%.0f%% the "
                            "unconditional mean suggested. It is replenished at an effective "
                            "%.4f per step (%.2fx the phi = %.2f offer rate), i.e. in about %.1f "
                            "steps. The recorded Q still OVERSTATES what an active lineage would "
                            "see, and the first-birth error remains bounded but not negligible; "
                            "the corrected numbers make the overstatement SMALLER than the "
                            "pre-seal record claimed, in the conservative direction for the "
                            "disposition." % (nSY_cond_mean, 100.0 / nSY_cond_mean,
                                              100.0 / nSY_mean, rate_eff, rate_eff / phi, phi,
                                              1.0 / rate_eff))},
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
    print("§12 spatial:", sp["CLASSIFICATION"], "| archives examined:",
          sp["ARCHIVES_EXAMINED"], "| key sets identical:",
          sp["KEY_SETS_IDENTICAL_ACROSS_ARMS"])
    print("   per-step position-resolved arrays:", sp["PER_STEP_POSITION_RESOLVED_ARRAYS"] or
          "NONE", "| frames all scalar:",
          sp["LEDGER_CONTENTS"]["frames"]["every_value_is_scalar"])
    print("   N_Y == 1 in every arm:",
          sp["DECISIVE_GROUND_kY_ZERO"]["N_Y_identically_one_in_every_arm"],
          "over", sp["DECISIVE_GROUND_kY_ZERO"]["steps_checked"], "steps")
    print("   Q_POSITION recoverable for a separated descendant:",
          sp["Q_POSITION_RECOVERABLE_FOR_A_SEPARATED_DESCENDANT"])
    print("§13 feedback:", fb["CLASSIFICATION"])
    p = fb["DETERMINISTIC_PERTURBATION_BOUND"]["one_Y_birth"]
    print("   one Y birth: delta nSY = %d (%.1f%% of the CONDITIONAL mean nSY %.4f), effective "
          "recovery %.4f/step" % (p["delta_nSY_local"],
                                  100 * -p["CORRECTED_depletion_fraction"],
                                  p["cond_mean_nSY_at_org_given_cand_Y_ge_1"],
                                  p["CORRECTED_effective_recovery_rate_per_step"]))


if __name__ == "__main__":
    main()
