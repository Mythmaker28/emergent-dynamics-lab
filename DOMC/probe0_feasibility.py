"""DOMC probe 0 — G1_DUAL_FEASIBILITY.

Question, and only this question: can TWO material components be founded in ONE communicating
world and both survive the full experimental horizon, in the frozen sc_mcm LawSpec, with no
change whatsoever to the physics?

Nothing here is an experiment. It reports geometry, survival and coupling diagnostics so that
Phase S can be pre-registered on a geometry that is known to be viable. No history is applied,
no memory is read, no hypothesis is tested.
"""
from __future__ import annotations
import sys, json, time
sys.path.insert(0, "/home/claude/sweep")
import numpy as np

from edlab.experiments.sc_mcm import harness as H, config as C
from edlab.experiments.sc_iom.engine import IOMState

L = C.SPEC.size          # 64
N_H = 2                  # two components


# ---------------------------------------------------------------------------------------------
# founding: the ONLY change is the initial condition (a mask on rho and everything that rides it)
# ---------------------------------------------------------------------------------------------
def _pdist2(ay, ax, cy, cx, n):
    dy = np.abs(ay - cy); dy = np.minimum(dy, n - dy)
    dx = np.abs(ax - cx); dx = np.minimum(dx, n - dx)
    return dy ** 2 + dx ** 2


def blob_mask(centres, w, n=L):
    ys = np.arange(n)[:, None] * np.ones((1, n))
    xs = np.ones((n, 1)) * np.arange(n)[None, :]
    m = np.zeros((n, n))
    for (cy, cx) in centres:
        m = np.maximum(m, np.exp(-_pdist2(ys, xs, cy, cx, n) / (2.0 * w * w)))
    return m


def seed_pair(seed, centres, w):
    """seed_state gives the frozen random internal fields and cohort bands; we only restrict the
    initial scaffold support. sum_c C == rho is preserved because C is scaled by the same mask."""
    s = C.seed_state(C.SPEC, C.TRACER, seed, "random")
    m = blob_mask(centres, w)
    Mf = np.zeros((C.MC.n_comp, L, L))
    return IOMState(s.rho * m, s.U * m, s.V * m, s.c.copy(), s.N.copy(), s.C * m,
                    s.uptake.copy(), Mf, 0)


# ---------------------------------------------------------------------------------------------
def comps(st):
    return H.entities(st)


def geom(st):
    es = comps(st)
    es = sorted(es, key=lambda e: -e.size)
    out = []
    for e in es:
        out.append({"size": int(e.size), "mass": float(e.mass), "rg": float(e.rg),
                    "cy": float(e.centroid[0]), "cx": float(e.centroid[1]),
                    "upt": float(e.specific_uptake)})
    return out


def sep(g):
    if len(g) < 2:
        return None
    dy = abs(g[0]["cy"] - g[1]["cy"]); dy = min(dy, L - dy)
    dx = abs(g[0]["cx"] - g[1]["cx"]); dx = min(dx, L - dx)
    return float(np.hypot(dy, dx))


def run_one(seed, centres, w, horizon, cadence=200):
    eng = H.mc_engine()
    st = seed_pair(seed, centres, w)
    tr = []
    for t in range(1, horizon + 1):
        st = eng.step(st)
        if t % cadence == 0:
            g = geom(st)
            tr.append({"t": t, "n": len(g), "sep": sep(g),
                       "sizes": [c["size"] for c in g[:3]],
                       "masses": [round(c["mass"], 3) for c in g[:3]]})
    return st, tr


def single_reference(seed, horizon, cadence=200):
    """The frozen one-droplet world, for size/mass calibration and as the 'no neighbour' control."""
    eng = H.mc_engine()
    st = H.seed_mc(seed)
    tr = []
    for t in range(1, horizon + 1):
        st = eng.step(st)
        if t % cadence == 0:
            g = geom(st)
            tr.append({"t": t, "n": len(g), "sizes": [c["size"] for c in g[:3]],
                       "masses": [round(c["mass"], 3) for c in g[:3]]})
    return st, tr


if __name__ == "__main__":
    t0 = time.time()
    HOR = int(sys.argv[1]) if len(sys.argv) > 1 else 3400
    out = {"horizon": HOR, "L": L}

    # --- A. the frozen single-droplet world, 3 seeds: what does ONE component look like? -------
    A = {}
    for s in (32000, 32001, 32002):
        st, tr = single_reference(s, HOR)
        A[str(s)] = {"traj": tr, "final": geom(st)}
        print("single", s, tr[-1], flush=True)
    out["A_single"] = A

    # --- B. pair geometry ladder: does a founded pair persist, and at what separation? ---------
    #  centres are placed on one row so that a half-plane split in x is exactly symmetric.
    LADDER = {"d32": [(32, 16), (32, 48)],
              "d24": [(32, 20), (32, 44)],
              "d16": [(32, 24), (32, 40)]}
    B = {}
    for name, ctr in LADDER.items():
        for wid in (5.0, 7.0):
            key = f"{name}_w{wid:g}"
            st, tr = run_one(32000, ctr, wid, HOR)
            B[key] = {"traj": tr, "final": geom(st)}
            print(key, tr[-1], flush=True)
    out["B_ladder"] = B
    out["seconds"] = round(time.time() - t0, 1)
    json.dump(out, open("probe0_feasibility.json", "w"), indent=1)
    print("DONE", out["seconds"], "s")
