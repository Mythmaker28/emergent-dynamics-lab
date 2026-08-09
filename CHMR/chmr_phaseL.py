"""CHMR Phase L — lineage / rank audit.

PART 1 is raw-only and reports what the parent artefacts can and cannot answer.
PART 2 establishes lineage continuity PROSPECTIVELY, which the mission requires before the new
programme may rely on any turnover statement. It is calibration: no endpoint, no probe, no
response, no arm comparison.
"""
from __future__ import annotations
import sys, os, json, pickle, statistics as S
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
import numpy as np
import domc_core as K
import chmr_lineage as LG
from edlab.experiments.sc_mcm import harness as H, config as C
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine
from edlab.experiments.sc_hmc.harness import PulseChaseTracer

D = "/home/claude/sweep/DOMC"
CAD = 25          # checkpoint cadence: droplets move far less than one cell per 25 steps


# =============================================================== PART 1 : raw-only audit
def raw_only_audit():
    out = {"question": "can the parent turnover claim be re-derived from raw artefacts?"}
    # 1a. the parent sc_mcm / sc_iom lines
    out["parent_line_raw_state"] = {
        "results/sc_mcm": "present but EMPTY (0 bytes)",
        "results/sc_iom": "present but EMPTY (0 bytes)",
        "git_tracked_artifacts": "docs and code only; no raw world, no checkpoint, no field dump",
        "consequence": "no connected-component recomputation, no temporal lineage graph and no "
                       "argmax-switch statistic can be derived for the parent line. Interpolation "
                       "or reconstruction is forbidden.",
        "PARENT_COMPONENT_MEMORY_THROUGH_TURNOVER": "NOT_IDENTIFIABLE"}
    # 1b. what DOMC itself stored
    B = pickle.load(open(os.path.join(D, "domc_FAR_PROSP_cc-00.pkl"), "rb"))
    rows = []
    for b in B:
        for k, v in b["arms"].items():
            for w in ("t0", "turn"):
                rows.append({"seed": b["seed"], "arm": k, "when": w,
                             "n_components": v[w]["n_components"],
                             "d_A": v[w]["d_A"], "d_B": v[w]["d_B"],
                             "alive_A": v[w]["alive_A"], "alive_B": v[w]["alive_B"]})
    out["domc_stored_evidence"] = {
        "time_points_stored": 2,
        "spatial_state_stored": False,
        "n_components_values": sorted({r["n_components"] for r in rows}),
        "max_site_distance_t0": max(max(r["d_A"], r["d_B"]) for r in rows if r["when"] == "t0"),
        "max_site_distance_turn": max(max(r["d_A"], r["d_B"]) for r in rows if r["when"] == "turn"),
        "note": "DOMC never used largest(st): it used a frozen-site nearest-centroid reader, so "
                "the rank-statistic defect of the parent line does not apply to it directly. But "
                "two time points are not a lineage: with no intermediate checkpoint, a split and "
                "re-merge, or a swap of which physical object occupies a site, is invisible.",
        "DOMC_A_B_LINEAGE_FROM_RAW": "NOT_IDENTIFIABLE"}
    return out


# ========================================== PART 2 : prospective lineage, calibration only
def track(st0, eng, steps, cad=CAD, relabel_at=None, pc=None):
    frames, edges = [], []
    cur, e = st0.copy(), eng
    frames.append(LG.snapshot(cur))
    for t in range(1, steps + 1):
        if relabel_at is not None and t == relabel_at + 1:
            cur = K.relabel(cur)
            e = pc
        cur = e.step(cur)
        if t % cad == 0:
            f = LG.snapshot(cur)
            edges.append(LG.link(frames[-1], f))
            frames.append(f)
    return frames, edges, cur


def frozen_world_audit(seeds, steps=2600):
    """The question DOMC raised and could not answer: in the FROZEN uniform-seed sc_mcm world,
    does `largest(st)` stay on one physical object? Calibration only."""
    out = []
    for s in seeds:
        eng = H.mc_engine()
        st = H.seed_mc(s)
        frames, edges, _ = track(st, eng, steps)
        rep = LG.analyse_track(frames, edges)
        gaps = [g[3] for g in rep["rank_gap"]]
        out.append({"seed": s, "steps": steps, "cadence": CAD,
                    "n_components_min_max": (min(rep["n_components"]), max(rep["n_components"])),
                    "n_argmax_switches": rep["n_argmax_switches"],
                    "argmax_switch_frames": [a["frame"] * CAD for a in rep["argmax_switches"]],
                    "n_splits": rep["n_splits"], "n_fusions": rep["n_fusions"],
                    "n_disappearances": len(rep["disappearances"]),
                    "median_rank1_rank2_gap": S.median(gaps) if gaps else None,
                    "min_rank1_rank2_gap": min(gaps) if gaps else None,
                    "n_frames_with_gap_below_0.05": sum(1 for g in gaps if g < 0.05),
                    "n_exact_ties": len(rep["ties"])})
        print("frozen-world", s, out[-1], flush=True)
    return out


def founded_pair_audit(seeds, geom="FAR", steps=1400, relabel_at=390):
    """The lineage the NEW programme will rely on: the founded pair, tracked continuously through
    the turnover window, with splits and fusions retained."""
    K.set_geometry(geom)
    out = []
    for s in seeds:
        eng = K.engine()
        pc = MultiChannelMemoryEngine(C.SPEC, C.MC, PulseChaseTracer())
        st = K.found(s)
        frames, edges, _ = track(st, eng, steps, relabel_at=relabel_at, pc=pc)
        rep = LG.analyse_track(frames, edges)
        # founder lineages: the two components present at the first frame that has two
        k0 = next((k for k, f in enumerate(frames) if len(f) >= 2), None)
        lin = {}
        if k0 is not None:
            for idx in (0, 1):
                lin[idx] = LG.founder_lineage(frames, edges, k0, idx)
        conts = {}
        for idx, l in lin.items():
            present = [k for k in range(k0, len(frames)) if l.get(k)]
            conts[idx] = {"first_frame": k0, "last_frame_present": max(present) if present else None,
                          "continuous_to_end": bool(present and max(present) == len(frames) - 1),
                          "max_components_in_lineage": max((len(l[k]) for k in l), default=0),
                          "M_series": [(k * CAD, LG.summarise(frames, l)[k]["M"])
                                       for k in range(k0, len(frames), 4)]}
        gaps = [g[3] for g in rep["rank_gap"]]
        out.append({"seed": s, "geometry": geom,
                    "n_components_min_max": (min(rep["n_components"]), max(rep["n_components"])),
                    "n_argmax_switches": rep["n_argmax_switches"],
                    "n_splits": rep["n_splits"], "n_fusions": rep["n_fusions"],
                    "median_rank1_rank2_gap": S.median(gaps) if gaps else None,
                    "lineage": conts})
        print("founded-pair", s, {k: v for k, v in out[-1].items() if k != "lineage"},
              {i: (v["continuous_to_end"], v["max_components_in_lineage"])
               for i, v in conts.items()}, flush=True)
    return out


if __name__ == "__main__":
    OUT = {"programme": "CORE_HALO_MISMATCH_RECOVERY_00", "phase": "L_LINEAGE_RANK_AUDIT",
           "connectivity": "FROZEN parent detector, SCDetectionSpec(0.30, 12), periodic labelling",
           "cadence": CAD}
    OUT["PART1_raw_only"] = raw_only_audit()
    OUT["PART2_frozen_world_largest_audit"] = frozen_world_audit((32000, 32001, 32002))
    OUT["PART2_founded_pair_lineage"] = founded_pair_audit((36000, 36001, 36002, 36003))
    json.dump(OUT, open("chmr_phaseL.json", "w"), indent=1, default=str)
    print("DONE")
