"""DOMC probe 1 — the dual window, the turnover clock, and site fidelity.

Probe 0 established a structural fact about the FROZEN sc_mcm world that no previous experiment
in this line recorded: it is not a one-body world. Started from the frozen uniform seed it
fragments into 22-34 detected components and relaxes to ~16 near-degenerate droplets. Every
published readout in the sc_iom / sc_mcm line was taken with `largest(st)` in that world.

Probe 1 asks only what Phase S needs to know before anything can be pre-registered:
  Q1  is there a founding width for which EXACTLY TWO components persist, and for how long?
  Q2  how many steps does the frozen turnover criterion (cohort M <= M_LOW = 0.35) need,
      measured PER COMPONENT rather than for `largest`?
  Q3  do the two components stay at their frozen sites (so that a geometric, provenance-blind
      reader can address them)?

No history, no memory readout, no hypothesis. Physics untouched; only the initial support of rho.
"""
from __future__ import annotations
import sys, json, time
sys.path.insert(0, "/home/claude/sweep")
import numpy as np

from edlab.experiments.sc_mcm import harness as H, config as C
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine
from edlab.experiments.sc_iom.engine import IOMState
from edlab.experiments.sc_hmc.harness import PulseChaseTracer

L = C.SPEC.size
SITE_A = (32, 16)
SITE_B = (32, 48)          # exactly L/2 from A along x: the reciprocal exchange is a pure roll


def _pd2(ay, ax, cy, cx, n=L):
    dy = np.abs(ay - cy); dy = np.minimum(dy, n - dy)
    dx = np.abs(ax - cx); dx = np.minimum(dx, n - dx)
    return dy ** 2 + dx ** 2


def blob(centres, w):
    ys = np.arange(L)[:, None] * np.ones((1, L))
    xs = np.ones((L, 1)) * np.arange(L)[None, :]
    m = np.zeros((L, L))
    for cy, cx in centres:
        m = np.maximum(m, np.exp(-_pd2(ys, xs, cy, cx) / (2.0 * w * w)))
    return m


def seed_pair(seed, w):
    s = C.seed_state(C.SPEC, C.TRACER, seed, "random")
    m = blob([SITE_A, SITE_B], w)
    return IOMState(s.rho * m, s.U * m, s.V * m, s.c.copy(), s.N.copy(), s.C * m,
                    s.uptake.copy(), np.zeros((C.MC.n_comp, L, L)), 0)


def relabel(st):
    out = st.copy()
    out.C = np.stack([out.rho.copy(), np.zeros_like(out.rho)])
    return out


def sited(st):
    """Provenance-blind geometric reader: for each frozen site, the detected component whose
    circular centroid is closest to it. Returns (entity or None, distance) per site."""
    es = H.entities(st)
    out = {}
    for nm, (cy, cx) in (("A", SITE_A), ("B", SITE_B)):
        best, bd = None, 1e9
        for e in es:
            d = float(np.sqrt(_pd2(np.array(e.centroid[0]), np.array(e.centroid[1]), cy, cx)))
            if d < bd:
                best, bd = e, d
        out[nm] = (best, bd)
    same = (out["A"][0] is not None and out["B"][0] is not None
            and out["A"][0] is out["B"][0])
    return out, len(es), same


def Mfrac(e):
    cm = np.asarray(e.cohort_mass, float)
    return float(cm[0] / cm.sum()) if cm.sum() > 0 else 1.0


def run(seed, w, horizon, relabel_at, cad=50):
    eng = H.mc_engine()
    pc = MultiChannelMemoryEngine(C.SPEC, C.MC, PulseChaseTracer())
    st = seed_pair(seed, w)
    rec = {"seed": seed, "w": w, "n_series": [], "first_not_two": None,
           "site": {"A": [], "B": []}, "turnover": []}
    cur, e2 = eng, None
    for t in range(1, horizon + 1):
        if t == relabel_at + 1:
            st = relabel(st)
            cur = pc
        st = cur.step(st)
        if t % cad == 0:
            info, ncomp, collide = sited(st)
            rec["n_series"].append([t, ncomp, bool(collide)])
            if rec["first_not_two"] is None and ncomp != 2:
                rec["first_not_two"] = t
            for nm in ("A", "B"):
                e, d = info[nm]
                rec["site"][nm].append([t, (int(e.size) if e else 0),
                                        (round(float(e.mass), 3) if e else 0.0), round(d, 2)])
            if t > relabel_at:
                rec["turnover"].append([t - relabel_at,
                                        round(Mfrac(info["A"][0]), 4) if info["A"][0] else None,
                                        round(Mfrac(info["B"][0]), 4) if info["B"][0] else None])
    return rec


if __name__ == "__main__":
    t0 = time.time()
    HOR = int(sys.argv[1]) if len(sys.argv) > 1 else 1600
    RELAB = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    out = {"horizon": HOR, "relabel_at": RELAB, "M_LOW": C.M_LOW,
           "sites": {"A": SITE_A, "B": SITE_B}, "runs": []}
    for w in (3.0, 3.5, 4.0, 4.5, 5.0):
        for seed in (33000, 33001, 33002):
            r = run(seed, w, HOR, RELAB)
            out["runs"].append(r)
            tv = [x for x in r["turnover"] if x[1] is not None and x[1] <= C.M_LOW]
            print(f"w={w} s={seed} first_not_two={r['first_not_two']} "
                  f"n_end={r['n_series'][-1][1]} "
                  f"A_end={r['site']['A'][-1][1]}c/{r['site']['A'][-1][3]}d "
                  f"B_end={r['site']['B'][-1][1]}c/{r['site']['B'][-1][3]}d "
                  f"M<=0.35 at tau={tv[0][0] if tv else None}", flush=True)
    out["seconds"] = round(time.time() - t0, 1)
    json.dump(out, open("probe1_pair_window.json", "w"), indent=1)
    print("DONE", out["seconds"], "s")
