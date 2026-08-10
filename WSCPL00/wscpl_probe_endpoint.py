"""WSCPL00 Phase B1 feasibility probe: does a valid, non-degenerate macro BRANCH endpoint exist?

FORMULATION_TRAIN role only. Development blocks only. No primary, no held-out.
This probe exists to decide, before any freeze, whether a mechanistic branch endpoint is even
alive in this substrate. If the candidate endpoint is constant, the programme stops as
NO_VALID_MACRO_BRANCH_ENDPOINT rather than inventing a livelier one.
"""
from __future__ import annotations
import sys, os, json
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/PPAI")
sys.path.insert(0, "/home/claude/sweep/ETPC")
sys.path.insert(0, "/home/claude/sweep/ETCMNFC")
import numpy as np
import domc_core as K, etpc_core as E, etcmnfc_core as Z

CK = "/home/claude/sweep/ETNBFC/checkpoints"
FORM = (61000, 61001, 61002)          # FORMULATION_TRAIN only
H = 400
STRIDE = 10
STARTS = {"n": 0, "log": []}
K.set_geometry("FAR")


def macro(st):
    """Candidate macro observables, all from FROZEN readers that predate this programme."""
    pick, dist, n = K.read_sites(st)
    out = {"n_components": int(n)}
    for nm in ("A", "B"):
        e = pick[nm]
        if e is None:
            out[nm] = None
            continue
        ys, xs = e.cells[:, 0], e.cells[:, 1]
        r = st.rho[ys, xs]
        u = st.U[ys, xs] / np.maximum(r, 1e-12)
        v = st.V[ys, xs] / np.maximum(r, 1e-12)
        out[nm] = {"size": int(len(ys)), "mass": float(r.sum()),
                   "sigma": float(((u - v) / (u + v + 1e-12)).mean())}
    return out


rows = []
for sd in FORM:
    st = E.load(f"{CK}/dev_FAR_{sd}.npz")
    eng = Z.engine(Z.GAIN_ON)
    STARTS["n"] += 1
    STARTS["log"].append(f"FORM_PROBE_{sd}")
    tr = []
    cur = st.copy()
    for t in range(0, H + 1):
        if t % STRIDE == 0:
            m = macro(cur)
            if m["A"] and m["B"]:
                tr.append({"t": t,
                           "dom_size": int(np.sign(m["A"]["size"] - m["B"]["size"])),
                           "dom_mass": int(np.sign(m["A"]["mass"] - m["B"]["mass"])),
                           "sigA": int(np.sign(m["A"]["sigma"])),
                           "sigB": int(np.sign(m["B"]["sigma"])),
                           "nA": m["A"]["size"], "nB": m["B"]["size"],
                           "mA": m["A"]["mass"], "mB": m["B"]["mass"],
                           "sA": m["A"]["sigma"], "sB": m["B"]["sigma"],
                           "ncomp": m["n_components"]})
            else:
                tr.append({"t": t, "lineage_lost": True, "ncomp": m["n_components"]})
        if t == H:
            break
        cur = eng.step(cur)

    def flips(key):
        v = [r[key] for r in tr if key in r]
        return sum(1 for a, b in zip(v, v[1:]) if a != b and a != 0 and b != 0)

    rows.append({"seed": sd, "n_samples": len(tr),
                 "lineage_lost_any": any(r.get("lineage_lost") for r in tr),
                 "flips_dominance_size": flips("dom_size"),
                 "flips_dominance_mass": flips("dom_mass"),
                 "flips_sigmaA": flips("sigA"), "flips_sigmaB": flips("sigB"),
                 "dom_size_values": sorted({r["dom_size"] for r in tr if "dom_size" in r}),
                 "dom_mass_values": sorted({r["dom_mass"] for r in tr if "dom_mass" in r}),
                 "sigmaA_values": sorted({r["sigA"] for r in tr if "sigA" in r}),
                 "ncomp_values": sorted({r["ncomp"] for r in tr}),
                 "size_range_A": [min(r["nA"] for r in tr if "nA" in r),
                                  max(r["nA"] for r in tr if "nA" in r)],
                 "size_range_B": [min(r["nB"] for r in tr if "nB" in r),
                                  max(r["nB"] for r in tr if "nB" in r)],
                 "mass_diff_final": tr[-1].get("mA", 0) - tr[-1].get("mB", 0),
                 "trace": tr})
    r = rows[-1]
    print(f"seed {sd}: flips(size)={r['flips_dominance_size']} flips(mass)={r['flips_dominance_mass']} "
          f"flips(sigA)={r['flips_sigmaA']} ncomp={r['ncomp_values']} "
          f"sizeA={r['size_range_A']} sizeB={r['size_range_B']}", flush=True)

json.dump({"role": "FORMULATION_TRAIN", "horizon": H, "stride": STRIDE,
           "engine_starts": STARTS, "blocks": rows},
          open("/home/claude/sweep/WSCPL00/wscpl_probe_endpoint.json", "w"), indent=1)
print("\nSTARTS:", STARTS["n"])
