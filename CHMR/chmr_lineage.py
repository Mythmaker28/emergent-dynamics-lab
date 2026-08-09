"""CHMR — component lineage tracker.

Built because DOMC's parent line reports were read with `largest(st)` in a world that holds
22-34 components: `largest` is a RANK STATISTIC, not an identity. This module builds an explicit
temporal lineage graph from stored checkpoints, with splits and fusions represented and never
forced into a one-to-one match.

Frozen connectivity: the detector of the parent LawSpec, untouched
(SCDetectionSpec(threshold=0.30, min_cells=12), periodic labelling).
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/home/claude/sweep")
import numpy as np
from edlab.experiments.sc_mcm import harness as H, config as C

L = C.SPEC.size


def snapshot(st):
    """Everything the lineage needs from one checkpoint, and nothing else."""
    es = H.entities(st)
    out = []
    for e in es:
        cells = set(map(tuple, e.cells.tolist()))
        out.append({"cells": cells, "size": int(e.size), "mass": float(e.mass),
                    "cy": float(e.centroid[0]), "cx": float(e.centroid[1]),
                    "cohort": np.asarray(e.cohort_mass, float).tolist()})
    out.sort(key=lambda d: -d["size"])
    return out


def link(prev, cur):
    """Edges by SPATIAL OVERLAP of cell sets. Many-to-many is kept as such: a parent with two
    children is a split, a child with two parents is a fusion. Nothing is forced to match."""
    E = []
    for i, p in enumerate(prev):
        for j, c in enumerate(cur):
            ov = len(p["cells"] & c["cells"])
            if ov > 0:
                E.append({"parent": i, "child": j, "overlap_cells": ov,
                          "frac_of_parent": ov / max(len(p["cells"]), 1),
                          "frac_of_child": ov / max(len(c["cells"]), 1)})
    return E


def analyse_track(frames, edges):
    """frames: list of snapshots. edges[k]: edges from frame k to frame k+1."""
    rep = {"n_frames": len(frames), "n_components": [len(f) for f in frames],
           "argmax_switches": [], "splits": [], "fusions": [], "disappearances": [],
           "appearances": [], "rank_gap": [], "ties": []}
    for k, f in enumerate(frames):
        if len(f) >= 2:
            g = (f[0]["size"] - f[1]["size"]) / max(f[0]["size"], 1)
            rep["rank_gap"].append([k, f[0]["size"], f[1]["size"], round(g, 4)])
            if f[0]["size"] == f[1]["size"]:
                rep["ties"].append(k)
        elif len(f) == 1:
            rep["rank_gap"].append([k, f[0]["size"], 0, 1.0])
    for k, E in enumerate(edges):
        par = {}
        chi = {}
        for e in E:
            par.setdefault(e["parent"], []).append(e)
            chi.setdefault(e["child"], []).append(e)
        for i, v in par.items():
            if len(v) >= 2:
                rep["splits"].append({"frame": k, "parent": i,
                                      "children": [e["child"] for e in v],
                                      "parent_size": frames[k][i]["size"]})
        for j, v in chi.items():
            if len(v) >= 2:
                rep["fusions"].append({"frame": k, "child": j,
                                       "parents": [e["parent"] for e in v]})
        for i in range(len(frames[k])):
            if i not in par:
                rep["disappearances"].append({"frame": k, "component": i,
                                              "size": frames[k][i]["size"]})
        for j in range(len(frames[k + 1])):
            if j not in chi:
                rep["appearances"].append({"frame": k + 1, "component": j,
                                           "size": frames[k + 1][j]["size"]})
        # the argmax is index 0 by construction (frames are size-sorted)
        if not frames[k] or not frames[k + 1]:
            continue
        linked = any(e["parent"] == 0 and e["child"] == 0 for e in E)
        if not linked:
            best_child_of_argmax = max((e for e in E if e["parent"] == 0),
                                       key=lambda e: e["overlap_cells"], default=None)
            rep["argmax_switches"].append({
                "frame": k, "from_size": frames[k][0]["size"],
                "to_size": frames[k + 1][0]["size"],
                "argmax_at_k_became_child": (best_child_of_argmax["child"]
                                             if best_child_of_argmax else None),
                "kind": "argmax identity moved to a different physical object"})
    rep["n_argmax_switches"] = len(rep["argmax_switches"])
    rep["n_splits"] = len(rep["splits"])
    rep["n_fusions"] = len(rep["fusions"])
    return rep


def founder_lineage(frames, edges, start_frame, start_idx, min_frac=0.0):
    """FIXED_FOUNDER_LINEAGE_ITT: every descendant of the founding component is retained, splits
    included. Returns, per frame, the set of component indices belonging to the lineage."""
    cur = {start_idx}
    lin = {start_frame: set(cur)}
    for k in range(start_frame, len(frames) - 1):
        nxt = set()
        for e in edges[k]:
            if e["parent"] in cur and e["frac_of_child"] > min_frac:
                nxt.add(e["child"])
        cur = nxt
        lin[k + 1] = set(cur)
        if not cur:
            break
    return lin


def readouts(frames, edges, sites=None):
    """The five mandated readout conventions, expressed as the component index set per frame."""
    n = len(frames)
    out = {}
    out["FRAMEWISE_LARGEST"] = {k: ({0} if frames[k] else set()) for k in range(n)}
    # TERMINAL_LARGEST_BACKTRACKED: start from the terminal argmax and walk backwards
    back = {}
    cur = {0} if frames[-1] else set()
    back[n - 1] = set(cur)
    for k in range(n - 2, -1, -1):
        prev = set()
        for e in edges[k]:
            if e["child"] in cur:
                prev.add(e["parent"])
        cur = prev
        back[k] = set(cur)
    out["TERMINAL_LARGEST_BACKTRACKED"] = back
    out["ALL_COMPONENTS"] = {k: set(range(len(frames[k]))) for k in range(n)}
    out["WORLD_LEVEL"] = {k: set(range(len(frames[k]))) for k in range(n)}   # same set, but the
    # WORLD_LEVEL convention aggregates without any component identity at all (see summarise)
    return out


def summarise(frames, idxset, world_level=False):
    """Size, mass and cohort-M for a set of components per frame."""
    out = []
    for k, f in enumerate(frames):
        ii = idxset.get(k, set())
        if world_level:
            ii = set(range(len(f)))
        if not ii:
            out.append({"frame": k, "n": 0, "size": 0, "mass": 0.0, "M": None})
            continue
        size = sum(f[i]["size"] for i in ii)
        mass = sum(f[i]["mass"] for i in ii)
        coh = np.sum([f[i]["cohort"] for i in ii], axis=0)
        M = float(coh[0] / coh.sum()) if coh.sum() > 0 else None
        out.append({"frame": k, "n": len(ii), "size": size, "mass": mass, "M": M})
    return out
