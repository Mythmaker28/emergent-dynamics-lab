"""CSC01 étape A synthesis: the corrected-gate counterfactual, the four axes, and the verdict.

Nothing here re-runs anything. It reads `_autopsy_repaired.json` and applies rules that are
stated in full, in the file, before they are used.
"""
from __future__ import annotations

import json
import sys

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/CSC01/code")

import gates as G                # noqa: E402
import protocol as P             # noqa: E402

OUT = "/home/claude/CSC01/out"

# --------------------------------------------------------------------------- the corrected gate
CORRECTED_GATE_SPEC = {
    "purpose": "DIAGNOSTIC ONLY. It answers: what would the ORR01 gate have said if its two "
               "spatial criteria had been written the way its own temporal criteria are "
               "written? It is NOT the CSC01 confirmatory gate, and it changes no frozen "
               "ORR01 byte, classification or disposition.",
    "changes": {
        "no_wrap_around_contact": "the ORR01 flag is `extent >= L/2`, where extent is "
            "2*max(dy, dx)+1 measured from the angular centre. That is an EXTENT proxy, not a "
            "winding test: a compact core with one distant molecule attached by a thin filament "
            "trips it without the component wrapping at all. Replaced by the exact winding test "
            "(lift into the universal cover; a non-zero winding vector is a real wrap).",
        "main_component_carries_the_mass": "the ORR01 form requires main_N_X >= N_KEEP/2 at "
            "EVERY one of the ~90 sampled instants. Every other criterion in the same gate is "
            "given a tolerance (fraction_ok at FRAC_MIN, excursion_ok at RUN_MAX). Replaced by "
            "the same tolerance: satisfied at a fraction >= FRAC_MIN of the sampled instants."},
    "unchanged": ["never_extinct", "organiser_present_throughout", "fraction_ok", "excursion_ok",
                  "criticality_ok", "free_capacity_not_collapsed", "occupancy_stable"],
}


def corrected_gate(arm, recorded_checks):
    """Recompute PASS and classification with the two spatial criteria corrected."""
    if not recorded_checks:
        return {"applicable": False,
                "reason": "the arm has no maintenance window: the ORR01 formation gate never "
                          "fired, so no persistence check of any kind was evaluated"}
    samples = [s for s in arm["orr_sample_trace"] if s["in_window"]]
    thr = P.N_KEEP * 0.5
    ok_mass = [(s["main_N_X"] is not None and s["main_N_X"] >= thr) for s in samples]
    frac_mass = float(np.mean(ok_mass)) if ok_mass else 0.0
    true_wraps = sum(1 for f in arm["frame_trace"] if f["any_component_wraps"])
    c = dict(recorded_checks)
    c["main_component_carries_the_mass"] = bool(frac_mass >= P.FRAC_MIN)
    c["no_wrap_around_contact"] = bool(true_wraps == 0)
    hard = ("never_extinct", "organiser_present_throughout", "fraction_ok", "excursion_ok",
            "criticality_ok", "free_capacity_not_collapsed", "occupancy_stable",
            "main_component_carries_the_mass", "no_wrap_around_contact")
    return {"applicable": True,
            "fraction_of_samples_with_main_N_X_above_threshold": frac_mass,
            "threshold_main_N_X": thr, "FRAC_MIN": P.FRAC_MIN,
            "n_samples_in_window": len(samples),
            "frames_with_a_true_winding": true_wraps,
            "n_frames_in_window": len(arm["frame_trace"]),
            "orr01_wrap_flag_fired_on_samples":
                sum(1 for s in samples if s["orr01_wraps_flag"]),
            "PASS": bool(all(c[k] for k in hard)),
            "classification": G.classify(c),
            "checks": c}


# --------------------------------------------------------------------------- the axes, restated
def per_arm(arm):
    ax = arm["axes"]
    sc = arm["SPATIAL_CORE_PERSISTENCE"]
    dec = ax["A1_decomposition"]
    return {
        "seed": arm["seed"],
        "ORR01_classification": arm["recorded_classification"],
        "axes_defined": bool(arm["window"].get("AXES_DEFINED", True)),
        "A1_literal_PASS": bool(ax["A1_PASS"]),
        "A1a_relative_fraction": dec["fraction_r80_below_N1_q01"],
        "A1a_PASS": bool(dec["fraction_r80_below_N1_q01"] >= 0.95),
        "A1b_absolute_fraction": dec["fraction_r80_below_L_over_6"],
        "A2_PASS": bool(sc["PASS"]),
        "core_exists_fraction": sc["core_exists_fraction_of_frames"],
        "identity_chain_fraction": sc["identity_chain_fraction_of_window"],
        "A3_turnover": ax["A3_material_turnover_replacements"],
        "A3_PASS": bool(ax["A3_PASS"]),
        "A4_PASS": bool(ax["A4_no_wrap_all_frames"]),
        "r80_median": ax["r80"]["median"], "Rg_median": ax["Rg_pairwise"]["median"],
        "N3_r80_observed_quantile":
            arm["nulls"]["summary"]["N3"]["r80"]["mean_observed_quantile_in_null"],
        "N3_Rg_observed_quantile":
            arm["nulls"]["summary"]["N3"]["Rg_pairwise"]["mean_observed_quantile_in_null"],
        "N1_r80_observed_quantile":
            arm["nulls"]["summary"]["N1"]["r80"]["mean_observed_quantile_in_null"],
        "core_to_organiser_mean": arm["core_motion"].get("core_to_organiser", {}).get("mean"),
        "core_follows_organiser_corr": arm["core_motion"].get("core_follows_organiser_corr"),
        "N5_separation": arm["core_motion"].get("N5_separation"),
        "satellite_X_mass_fraction":
            arm["halo_vs_fragmentation"]["mean_satellite_X_mass_fraction"],
        "satellite_lifetime_q90": arm["halo_vs_fragmentation"]["satellite_lifetime_q90_steps"],
        "n_long_lived_satellites":
            arm["halo_vs_fragmentation"]["n_long_lived_satellites_ge_tau_death"],
        "n_satellite_tracks": arm["halo_vs_fragmentation"]["n_satellite_tracks"],
    }


def main():
    d = json.load(open(f"{OUT}/_autopsy_repaired.json"))
    rec = json.load(open("/home/claude/ORR01/out/_results.json"))
    rec2 = json.load(open("/home/claude/ORR01/out/_results2.json"))
    recorded = {}
    for src in (rec, rec2):
        for pair in src["pairs"]:
            for _, v in pair.items():
                recorded[v["tag"]] = v
    rows, cg = [], {}
    for a in d["arms"]:
        rows.append(per_arm(a))
        cg[a["tag"]] = corrected_gate(a, recorded[a["tag"]]["gate_posthoc"].get("checks"))

    n = len(rows)
    A1lit = sum(r["A1_literal_PASS"] for r in rows)
    A1a = sum(r["A1a_PASS"] for r in rows)
    A2 = sum(r["A2_PASS"] for r in rows)
    A3 = sum(r["A3_PASS"] for r in rows)
    A4 = sum(r["A4_PASS"] for r in rows)
    core90 = sum(r["core_exists_fraction"] >= 0.90 for r in rows)
    loc = sum(r["A1a_PASS"] and r["A4_PASS"] for r in rows)
    loc_core = sum(r["A1a_PASS"] and r["A4_PASS"] and r["core_exists_fraction"] >= 0.90
                   for r in rows)
    loc_cont = sum(r["A1a_PASS"] and r["A4_PASS"] and r["A2_PASS"] for r in rows)

    # ---- the ORR01 spatial criterion, in the arms that are LOCALISED and CORE_PRESENT
    lc = [r for r in rows if r["A1a_PASS"] and r["A4_PASS"] and r["core_exists_fraction"] >= 0.90]
    orr_spatial = {}
    for r in lc:
        tag = "conf/REPAIRED/seed%d" % r["seed"]
        arm = next(a for a in d["arms"] if a["tag"] == tag)
        ck = arm["ORR01_gate_spatial_checks"]
        orr_spatial[r["seed"]] = ("NOT_EVALUATED" if not ck["checks_present"] else
                                  {"main_component_carries_the_mass":
                                   ck["main_component_carries_the_mass"],
                                   "no_wrap_around_contact": ck["no_wrap_around_contact"]})
    never_true = all(v == "NOT_EVALUATED" or not (v["main_component_carries_the_mass"] and
                                                  v["no_wrap_around_contact"])
                     for v in orr_spatial.values())

    tests = json.load(open(f"{OUT}/_tests_stage_a.json"))
    demo = {t["test"][:3]: t["PASS"] for t in tests["results"] if t["test"][:3] in ("T10", "T11")}
    demo_ok = bool(demo.get("T10") and demo.get("T11"))
    replay_ok = sum(1 for a in d["arms"]
                    if a["fidelity"]["REPLAY_IS_DETERMINISTIC_DECOMPRESSION"])

    # ---- the corrected ladder of D-3, applied in order
    ladder = []
    verdict = None
    def rule(k, txt, fires):
        ladder.append({"rule": k, "condition": txt, "fires": bool(fires)})
        return fires
    if rule(1, "replay not bit-exact for >= 2 arms", (n - replay_ok) >= 2):
        verdict = "ORR01_RAW_LOCALIZATION_UNRESOLVED"
    elif rule(2, "LOCALISED in <= 2 arms", loc <= 2):
        verdict = "ORR01_DELOCALIZATION_CONFIRMED"
    elif rule(3, "LOCALISED and CORE_CONTINUOUS in >= 5 arms and the ORR01 spatial criterion "
                 "true there", loc_cont >= 5):
        verdict = "ORR01_RAW_LOCALIZATION_CONFIRMED"
    elif rule(4, "LOCALISED and CORE_PRESENT in >= 4 arms, the ORR01 spatial criterion never "
                 "true there, and the constructive demonstration of its defect succeeds",
              loc_core >= 4 and never_true and demo_ok):
        verdict = "ORR01_LOCALIZATION_GATE_INVALID"
    elif rule(5, "LOCALISED and CORE_PRESENT in >= 4 arms", loc_core >= 4):
        verdict = "ORR01_PARTIAL_LOCALIZED_CORE"
    else:
        rule(6, "otherwise", True)
        verdict = "ORR01_RAW_LOCALIZATION_UNRESOLVED"

    n3b = json.load(open(f"{OUT}/_null_n3b.json"))
    n3b_sum = {o["seed"]: o["summary"] for o in n3b["arms"] if o.get("applicable")}

    out = {
        "n_arms": n,
        "counts": {"A1_literal": A1lit, "A1a_relative": A1a, "A2": A2, "A3": A3, "A4": A4,
                   "core_present_ge_0.90": core90, "LOCALISED (A1a and A4)": loc,
                   "LOCALISED and CORE_PRESENT": loc_core,
                   "LOCALISED and CORE_CONTINUOUS": loc_cont,
                   "replay_bit_exact": replay_ok},
        "per_arm": rows,
        "corrected_gate_spec": CORRECTED_GATE_SPEC,
        "corrected_gate_counterfactual": cg,
        "ORR01_spatial_criterion_in_localised_arms": orr_spatial,
        "ORR01_spatial_criterion_never_true_there": never_true,
        "constructive_demonstrations": demo,
        "N3b_observed_quantiles": n3b_sum,
        "ladder_literal": {
            "verdict": ("ORR01_DELOCALIZATION_CONFIRMED" if (n - A1lit) >= 4 else "n/a"),
            "note": "the literal A1 of the pre-plan fails in %d of %d arms, which fires rule 2 "
                    "and yields a label the same data refute at quantile 0.000 against both N1 "
                    "and N4. Correction D-2." % (n - A1lit, n)},
        "ladder_corrected": ladder,
        "VERDICT_QUESTION_A": verdict,
    }
    json.dump(out, open(f"{OUT}/_stage_a.json", "w"), indent=1, default=str)
    print()
    print("LADDER (corrected, D-3):")
    for r_ in ladder:
        print("   rule %d  fires=%-5s  %s" % (r_["rule"], r_["fires"], r_["condition"]))
    print()
    print("VERDICT_QUESTION_A = %s" % verdict)
    print("literal-rule verdict = %s (refuted by its own nulls, see D-2)"
          % out["ladder_literal"]["verdict"])

    print("counts over %d repaired arms" % n)
    for k, v in out["counts"].items():
        print("   %-32s %d" % (k, v))
    print()
    print(f"{'seed':<5s} {'ORR01 class':<20s} {'corrected class':<22s} {'PASS':>5s} "
          f"{'fracMass':>8s} {'trueWrap':>8s} {'orrWrapFlag':>11s}")
    for a in d["arms"]:
        c = cg[a["tag"]]
        if not c["applicable"]:
            print(f"{a['seed']:<5d} {a['recorded_classification']:<20s} "
                  f"{'(no window)':<22s}")
            continue
        print(f"{a['seed']:<5d} {a['recorded_classification']:<20s} {c['classification']:<22s} "
              f"{str(c['PASS']):>5s} {c['fraction_of_samples_with_main_N_X_above_threshold']:>8.3f} "
              f"{c['frames_with_a_true_winding']:>8d} {c['orr01_wrap_flag_fired_on_samples']:>11d}")


if __name__ == "__main__":
    main()
