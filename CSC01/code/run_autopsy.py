"""CSC01 étape A driver. One bit-exact replay per arm, then every measurement of the pre-plan."""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/CSC01/code")

import observe as OBS            # noqa: E402
import protocol as P             # noqa: E402

import autopsy as AU             # noqa: E402
import guard_csc as GC           # noqa: E402
import replay as RP              # noqa: E402

OUT = "/home/claude/CSC01/out"
ORR_OUT = "/home/claude/ORR01/out"


def recorded_records():
    recs = {}
    for fn in ("_results.json", "_results2.json"):
        d = json.load(open(os.path.join(ORR_OUT, fn)))
        for pair in d["pairs"]:
            for _, v in pair.items():
                recs[v["tag"]] = v
        for c in d["controls"]:
            recs[c["tag"]] = c
    return recs


def analyse(tag, rec):
    t0 = time.time()
    tr = AU.trace_arm(tag)
    series_eq, fields_eq, ph = AU.replay_fidelity(tag, tr)
    diffs = AU.gate_field_by_field(rec["gate_posthoc"], ph)
    fidelity = {"series_bit_identical": series_eq,
                "final_fields_bit_identical": fields_eq,
                "n_component_samples_regenerated": len(tr["orr_samples"]),
                "n_component_samples_saved_by_ORR01": len(rec["component_samples"]),
                "gate_field_by_field_differences": diffs,
                "GATE_RECOMPUTED_IDENTICAL": len(diffs) == 0,
                "REPLAY_IS_DETERMINISTIC_DECOMPRESSION":
                    bool(series_eq and all(fields_eq.values()) and not diffs)}
    # the three saved samples must also match, element by element
    saved_ok = True
    by_step = {int(s["step"]): s for s in tr["orr_samples"]}
    for s in rec["component_samples"]:
        r = by_step.get(int(s["step"]))
        saved_ok &= (r is not None and json.dumps(r, sort_keys=True) ==
                     json.dumps(s, sort_keys=True))
    fidelity["saved_component_samples_reproduced"] = bool(saved_ok)

    out = {"tag": tag, "seed": tr["seed"], "arm": tr["arm"],
           "recorded_classification": rec["classification"],
           "recorded_PASS": rec["PASS"], "fidelity": fidelity,
           "wall_seconds": round(time.time() - t0, 2)}
    if not fidelity["REPLAY_IS_DETERMINISTIC_DECOMPRESSION"]:
        out["ARM_DISCARDED"] = True
        return out
    out["ARM_DISCARDED"] = False

    formed = ph["formed_at"]
    frames, labels = tr["frames"], tr["labels"]
    steps = np.array([f["step"] for f in frames])
    if formed is None:
        # ORR01's formation gate never fired: N_X >= 30 with u >= 3 for 50 consecutive steps
        # was never reached before T_FORM_MAX. There is then no maintenance window, so the four
        # axes are UNDEFINED for this arm and it counts as "not satisfied" in the decision rule.
        # A nominal window [T_FORM_MAX, T_FORM_MAX + T_MAINT) is measured as well, labelled
        # DIAGNOSTIC_ONLY, and is never used in the verdict counts.
        lo, hi = int(P.T_FORM_MAX), int(P.T_FORM_MAX + P.T_MAINT)
        out["window"] = {"formed_at": None, "AXES_DEFINED": False,
                         "diagnostic_nominal_window": [lo, hi],
                         "reason": "ORR01 formation gate never fired within T_FORM_MAX"}
        diagnostic = True
    else:
        lo, hi = int(formed), int(formed + P.T_MAINT)
        out["window"] = {"formed_at": lo, "to": hi, "AXES_DEFINED": True,
                         "track_every": AU.TRACK_EVERY}
        diagnostic = False
    lo_idx = int(np.searchsorted(steps, lo, "left"))
    hi_idx = int(np.searchsorted(steps, hi, "left"))
    out["window"]["frames"] = hi_idx - lo_idx
    out["DIAGNOSTIC_ONLY"] = diagnostic

    nl = AU.run_nulls(tr, frames, lo_idx, hi_idx, tr["seed"])
    ax = AU.axes(frames, tr["series"], lo, hi, lo_idx, hi_idx, nl["pooled"])
    ax.pop("_centres", None)
    trk = AU.track(labels, frames, lo_idx, hi_idx)
    hf = AU.halo_vs_fragment(labels, frames, lo_idx, hi_idx, trk, tr["xfields"])
    cm = AU.core_motion(frames, lo_idx, hi_idx, tr["seed"])

    wf = hi_idx - lo_idx
    core_frac = np.array([frames[i]["core_fraction_within_2ellX"] for i in range(lo_idx, hi_idx)],
                         dtype=float)
    id_frac = trk["longest_unbroken_main_run_frames"] / max(wf, 1)
    core_exists_frac = float(np.mean(core_frac >= 0.5))
    out["SPATIAL_CORE_PERSISTENCE"] = {
        "core_exists_fraction_of_frames": core_exists_frac,
        "main_identity_breaks_in_window": trk["main_identity_breaks_in_window"],
        "longest_unbroken_main_run_frames": trk["longest_unbroken_main_run_frames"],
        "longest_unbroken_main_run_steps": trk["longest_unbroken_main_run_frames"] * AU.TRACK_EVERY,
        "identity_chain_fraction_of_window": id_frac,
        "modal_main_track_coverage": trk["modal_main_track_coverage"],
        "PASS": bool(core_exists_frac >= 0.95 and id_frac >= 0.95),
        "PASS_definition": "declared in the pre-plan: core exists in >= 0.95 of window frames "
                           "AND the unbroken main-component identity chain covers >= 0.95 of "
                           "the window"}
    out["axes"] = ax
    out["tracking"] = {k: v for k, v in trk.items()
                       if k not in ("tracks", "main_track_per_frame", "cid_to_tid")}
    out["halo_vs_fragmentation"] = hf
    out["core_motion"] = cm
    out["nulls"] = nl
    out["ORR01_gate_spatial_checks"] = {
        "main_component_carries_the_mass": ph["checks"].get("main_component_carries_the_mass"),
        "no_wrap_around_contact": ph["checks"].get("no_wrap_around_contact"),
        "checks_present": bool(ph["checks"])}
    # where exactly did the ORR01 spatial criterion fail?
    thr = P.N_KEEP * 0.5
    bad = [{"step": int(s["step"]),
            "main_N_X": (s["main"] or {}).get("N_X"),
            "n_components": s["n_components"], "n_escapees": s["n_escapees"],
            "N_X_total": s["N_X_total"]}
           for s in tr["orr_samples"]
           if lo <= s["step"] < hi and not (s["main"] is not None and s["main"]["N_X"] >= thr)]
    # traces kept so that the corrected-gate counterfactual can be computed without re-tracing
    stepset = {int(f["step"]): f for f in frames}
    out["orr_sample_trace"] = [
        {"step": int(s["step"]),
         "main_N_X": (s["main"] or {}).get("N_X"),
         "orr01_wraps_flag": bool((s["main"] or {}).get("wraps", True)),
         "orr01_extent": (s["main"] or {}).get("extent"),
         "orr01_Rg": (s["main"] or {}).get("radius_of_gyration"),
         "true_any_component_wraps": bool(stepset[int(s["step"])]["any_component_wraps"])
         if int(s["step"]) in stepset else None,
         "in_window": bool(lo <= s["step"] < hi)}
        for s in tr["orr_samples"]]
    keep = ("step", "r50", "r80", "r90", "Rg_pairwise", "core_fraction_within_2ellX",
            "main_mass_fraction", "n_eff_components", "n_components", "main_N_X",
            "any_component_wraps", "centre_y", "centre_x", "organiser_y", "organiser_x",
            "organiser_to_centre", "main_geodesic_diameter", "N_X")
    out["frame_trace"] = [{k: f[k] for k in keep} for f in frames[lo_idx:hi_idx]]
    out["ORR01_gate_spatial_failures"] = {"threshold_main_N_X": thr, "n_failing_samples": len(bad),
                                          "n_samples_in_window": sum(1 for s in tr["orr_samples"]
                                                                     if lo <= s["step"] < hi),
                                          "failing": bad[:20]}
    return out


def main():
    tags = sys.argv[1:] or ["conf/REPAIRED/seed%d" % s for s in P.SEEDS_CONF]
    recs = recorded_records()
    res = []
    for t in tags:
        print("=== %s" % t, flush=True)
        r = analyse(t, recs[t])
        print("    replay exact=%s  gate identical=%s  wall=%.1fs"
              % (r["fidelity"]["REPLAY_IS_DETERMINISTIC_DECOMPRESSION"],
                 r["fidelity"]["GATE_RECOMPUTED_IDENTICAL"], r["wall_seconds"]), flush=True)
        res.append(r)
    name = sys.argv[0].split("/")[-1]
    payload = {"generated_by": name, "TRACK_EVERY": AU.TRACK_EVERY,
               "NULL_DRAWS": AU.NULL_DRAWS, "ell_X": AU.ELL_X,
               "arms": res, "ledger": GC.audit()}
    fn = os.path.join(OUT, os.environ.get("CSC01_AUTOPSY_OUT",
                      "_autopsy_%s.json" % ("repaired" if not sys.argv[1:] else "extra")))
    json.dump(payload, open(fn, "w"), indent=1, default=str)
    print("\nwrote %s" % fn)
    print("SCIENTIFIC_RUNS_USED = %d" % GC.scientific_runs_used())


if __name__ == "__main__":
    main()
