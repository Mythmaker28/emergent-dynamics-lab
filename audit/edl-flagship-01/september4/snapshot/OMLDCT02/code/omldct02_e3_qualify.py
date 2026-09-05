"""OMLDCT02 section 7 — PRE_RUN_E3_QUALIFICATION.

Two layers.

FIXTURE LAYER.  Classifier A's primitives (LDFMA01/code/ldfma01_raw.py: components_bfs, centroid,
link, link_reason) against classifier B's (omldct02_e3_b: _components_uf, _centroid, _link_map) on
hand-built adversarial configurations and on a large deterministic random stress.  The hand-built
cases carry the answer written out by hand, so a case where BOTH implementations are wrong in the
same way is still caught.

WORLD LAYER.  Classifier A's already-frozen per-world outputs — post_removal_identity_lifetime and
daughter_particle_steps_after_t_m, computed by LDFMA01 before OMLDCT02 existed and committed — are
compared against classifier B's end-to-end E3_DURATION and E3_EXPOSURE recomputed from the same raw
archives.  A's numbers cannot be tuned to match: they are already in the repository.

The qualification PASSES only if every layer agrees exactly.  Nothing here is relaxed to obtain a
pass; a disagreement is reported as a disagreement.
"""
from __future__ import annotations
import os, sys, json, math, hashlib, datetime, glob

REPO = os.environ.get("OMLDCT02_REPO", "/home/claude/edl")
os.environ.setdefault("LDFMA01_REPO", REPO)
os.environ.setdefault("OMLDCT02_REPO", REPO)
sys.path.insert(0, os.path.join(REPO, "LDFMA01", "code"))
sys.path.insert(0, os.path.join(REPO, "OMLDCT02", "code"))
import numpy as np
import ldfma01_raw as A          # classifier A's primitives, frozen
import omldct02_e3_a as AA       # classifier A, rebound through its OMLDCT02 adapter
import omldct02_e3_b as B        # classifier B, rebound

def _b_components(ys, xs): return B._components_uf(list(ys), list(xs))
def _b_centroid(ys, xs, idx): return B._centroid(np.asarray(ys, np.int64), np.asarray(xs, np.int64), idx)

# ------------------------------------------------------------------ hand-built fixtures
# each entry: (name, ys, xs, expected components written out by hand, why)
HAND_COMPONENTS = [
 ("empty", [], [], [], "no cells at all"),
 ("single", [5], [5], [[0]], "one cell is one component"),
 ("boundary_exactly_CORE_R", [0, 3], [0, 4], [[0, 1]],
  "3-4-5 triangle: squared distance is exactly 25 = CORE_R^2, and the frozen test is <=, so they join"),
 ("just_outside", [0, 0], [0, 6], [[0], [1]], "squared distance 36 > 25"),
 ("wrap_y", [0, 34], [0, 0], [[0, 1]], "toroidal dy = min(34, 2) = 2"),
 ("wrap_x", [0, 0], [0, 33], [[0, 1]], "toroidal dx = min(33, 3) = 3"),
 ("wrap_both", [1, 34], [1, 34], [[0, 1]], "dy = 3, dx = 3, squared 18 <= 25"),
 ("wrap_boundary", [0, 33], [0, 32], [[0, 1]], "dy = 3, dx = 4, squared exactly 25"),
 ("chain_transitive", [0, 0, 0], [0, 5, 10], [[0, 1, 2]],
  "single linkage: 0-1 and 1-2 are within range, 0-2 is not, and the component is still one"),
 ("two_groups", [0, 1, 20, 21], [0, 1, 20, 21], [[0, 1], [2, 3]], "two separated pairs"),
 ("ordering", [20, 0, 21, 1], [20, 0, 21, 1], [[0, 2], [1, 3]],
  "groups are ordered by smallest member, not by position"),
]

# each entry: (name, prev centroids, cur centroids, expected mapping, expected reasons, why)
HAND_LINKS = [
 ("continued", [(0.0, 0.0)], [(0.0, 2.0)], {0: 0}, {0: "CONTINUED"}, "unique both ways"),
 ("out_of_range", [(0.0, 0.0)], [(0.0, 10.0)], {}, {0: "OUT_OF_RANGE"}, "no candidate"),
 ("split", [(0.0, 0.0)], [(0.0, 2.0), (0.0, 34.0)], {}, {0: "SPLIT_OR_TIE"},
  "two candidates forward, terminates without preference"),
 ("exact_tie", [(0.0, 0.0)], [(0.0, 3.0), (0.0, 33.0)], {}, {0: "SPLIT_OR_TIE"},
  "equidistant candidates: a tie terminates, it is never resolved"),
 ("merge", [(0.0, 0.0), (0.0, 4.0)], [(0.0, 2.0)], {}, {0: "MERGE", 1: "MERGE"},
  "one candidate forward each, but two back"),
 ("clean_pair_and_ambiguity", [(0.0, 0.0), (20.0, 20.0)], [(0.0, 1.0), (20.0, 21.0), (20.0, 23.0)],
  {0: 0}, {0: "CONTINUED", 1: "SPLIT_OR_TIE"},
  "one identity survives while another in the same step does not"),
 ("empty_cur", [(0.0, 0.0)], [], {}, {0: "NO_PARTNER"}, "nothing to link to"),
 ("boundary_link", [(0.0, 0.0)], [(3.0, 4.0)], {0: 0}, {0: "CONTINUED"},
  "centroid distance exactly CORE_R links, because the frozen test is <="),
]

def run_fixtures():
    rows = []; ok = True
    for name, ys, xs, exp, why in HAND_COMPONENTS:
        a = A.components_bfs(ys, xs); b = _b_components(ys, xs)
        good = (a == exp) and (b == exp)
        ok &= good
        rows.append({"layer": "components", "case": name, "expected_by_hand": exp,
                     "A": a, "B": b, "A_matches_hand": a == exp, "B_matches_hand": b == exp,
                     "A_equals_B": a == b, "PASS": good, "why": why})
    for name, ys, xs, exp, why in HAND_COMPONENTS:
        if not ys: continue
        for g in exp:
            ca = A.centroid(ys, xs, g); cb = _b_centroid(ys, xs, g)
            good = ca == cb
            ok &= good
            rows.append({"layer": "centroid", "case": f"{name}:{g}", "A": list(ca), "B": list(cb),
                         "A_equals_B_bitwise": good, "PASS": good})
    for name, prev, cur, expmap, expreason, why in HAND_LINKS:
        amap = A.link(prev, cur); areason = A.link_reason(prev, cur)
        bmap, rc, cc, near = B._link_map(prev, cur)
        good = (amap == expmap) and (bmap == expmap) and (areason == expreason)
        ok &= good
        rows.append({"layer": "link", "case": name, "expected_map_by_hand": {str(k): v for k, v in expmap.items()},
                     "A_map": {str(k): v for k, v in amap.items()},
                     "B_map": {str(k): v for k, v in bmap.items()},
                     "A_reasons": {str(k): v for k, v in areason.items()},
                     "expected_reasons_by_hand": {str(k): v for k, v in expreason.items()},
                     "A_equals_B": amap == bmap, "PASS": good, "why": why,
                     "near_boundary": near})
    return rows, ok

# ------------------------------------------------------------------ deterministic random stress
def run_stress(n_conf=3000, n_link=1500, seed=20260825):
    rng = np.random.default_rng(seed)
    comp_bad = []; cen_bad = []; link_bad = []; near = []
    for _ in range(n_conf):
        n = int(rng.integers(1, 13))
        ys = rng.integers(0, B.L, n).tolist(); xs = rng.integers(0, B.L, n).tolist()
        a = A.components_bfs(ys, xs); b = _b_components(ys, xs)
        if a != b: comp_bad.append({"ys": ys, "xs": xs, "A": a, "B": b})
        for g in a:
            ca = A.centroid(ys, xs, g); cb = _b_centroid(ys, xs, g)
            if ca != cb: cen_bad.append({"ys": ys, "xs": xs, "g": g, "A": list(ca), "B": list(cb)})
    for _ in range(n_link):
        npv = int(rng.integers(1, 5)); ncu = int(rng.integers(0, 5))
        # centroids on a half-integer lattice: the values a real component centroid can take
        prev = [(float(rng.integers(0, 2 * B.L)) / 2, float(rng.integers(0, 2 * B.L)) / 2) for _ in range(npv)]
        cur = [(float(rng.integers(0, 2 * B.L)) / 2, float(rng.integers(0, 2 * B.L)) / 2) for _ in range(ncu)]
        amap = A.link(prev, cur); bmap, rc, cc, nb = B._link_map(prev, cur)
        if amap != bmap: link_bad.append({"prev": prev, "cur": cur, "A": amap, "B": bmap})
        near.extend(nb)
    return {"n_component_configurations": n_conf, "n_link_configurations": n_link, "seed": seed,
            "component_disagreements": comp_bad[:20], "n_component_disagreements": len(comp_bad),
            "centroid_disagreements": cen_bad[:20], "n_centroid_disagreements": len(cen_bad),
            "link_disagreements": link_bad[:20], "n_link_disagreements": len(link_bad),
            "n_near_boundary_link_comparisons": len(near),
            "PASS": not comp_bad and not cen_bad and not link_bad}

if __name__ == "__main__":
    fx, fx_ok = run_fixtures()
    st = run_stress()
    out = {"MISSION": "OMLDCT02", "SECTION": "7 — PRE_RUN_E3_QUALIFICATION, fixture layer",
           "GENERATED_UTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "CLASSIFIER_A": "LDFMA01/code/ldfma01_raw.py, reached through OMLDCT02/code/omldct02_e3_a.py",
           "CLASSIFIER_B": "OMLDCT02/code/omldct02_e3_b.py",
           "REBOUND_IN_OMLDCT02_C1_NOT_INHERITED_BY_REFERENCE": True,
           "FIXTURES": fx, "FIXTURE_LAYER_PASS": bool(fx_ok),
           "RANDOM_STRESS": st, "STRESS_LAYER_PASS": bool(st["PASS"]),
           "DECLARED_WINDOW_ASYMMETRY": B.DECLARED_WINDOW_ASYMMETRY}
    p = os.path.join(REPO, "OMLDCT02", "out", "OMLDCT02_E3_QUALIFICATION_FIXTURES.json")
    with open(p, "w") as fh: json.dump(out, fh, indent=1)
    print("FIXTURE_LAYER_PASS =", fx_ok, " STRESS_LAYER_PASS =", st["PASS"])
    print("component disagreements:", st["n_component_disagreements"],
          " centroid:", st["n_centroid_disagreements"], " link:", st["n_link_disagreements"])
    print("near-boundary link comparisons seen:", st["n_near_boundary_link_comparisons"])
    print("wrote", p)
