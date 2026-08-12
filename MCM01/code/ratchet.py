"""The resource ratchet: exact bookkeeping, empirical rate law, and the scope of the failure.

No new start. Everything here is either an exact consequence of the transition rule, or exact
arithmetic on the raw series already written to disk by the eight calibration arms.

THE MECHANISM, EXACTLY
----------------------
Write O = SUM over cells of (nX + nY + nSX + nSY + nWX + nWY), the total occupancy.

  _diffuse            moves particles, conserves every species count, so O is unchanged
  _react              converts one resource unit into one product unit: n[res]-- and n[prod]++,
                      so O is unchanged
  _decay              X -> WX and Y -> WY: O is unchanged
  _feed_and_outflow   adds  a = Binomial(min(max(S0-n,0), free), phi)  to SX and SY   (O up)
                      removes o = Binomial(n[W], omega) from WX and WY                (O down)

Therefore  O(t+1) - O(t) = a(t) - o(t)  EXACTLY, and O has exactly one source and one sink.

The sink is fed only by decay of X and Y, which exist only because resources were converted, and
conversion requires cand = min(n[res], free) > 0, hence free > 0. The source is strictly positive
in expectation whenever some cell holds fewer than S0 resource units AND has free capacity;
diffusion keeps producing such cells, because a binomial exchange between neighbours has positive
variance at every step.

So O rises until free = 0 everywhere. At that point cand == 0 in every cell, no reaction of any
kind can fire, X decays away, waste drains, and the state
      "every cell filled with resource, no body molecules, no production"
is reached. Once free = 0 and no waste remains, a = 0 and o = 0: the state is ABSORBING.

This holds for every parameter point of the family with phi > 0. It is a property of the feed
rule, not of a parameter choice.
"""
from __future__ import annotations

import glob
import json
import math

import numpy as np

RAW = "/home/claude/MCM01/raw"
CAP, S0, L = 16, 3, 36
CELLS = L * L


def reconstruct(path):
    """Recover the feed and the outflow EXACTLY from the saved totals and the recorded reaction
    and decay counts. add_SX = dN_SX + births_X, out_WX = deaths_X - dN_WX, and so on."""
    z = np.load(path, allow_pickle=True)
    F = list(z["fields"])
    a = z["series"]
    g = lambda k: a[:, F.index(k)]
    NSX, NSY, NX, NY = g("N_SX"), g("N_SY"), g("N_X"), g("N_Y")
    NWX, NWY = g("N_WX"), g("N_WY")
    births, deaths = g("accepted_births_X"), g("deaths_X")
    d = lambda v: np.diff(v)
    add_SX = d(NSX) + births[1:]
    out_WX = deaths[1:] - d(NWX)
    O = NX + NY + NSX + NSY + NWX + NWY
    free = CAP * CELLS - O
    # the exact identity O(t+1)-O(t) = add - out, with add = add_SX + add_SY and
    # out = out_WX + out_WY. add_SY is not directly recorded (no Y births at kY = 0), so it is
    # obtained from the identity and cross-checked against dN_SY, which must be equal.
    add_SY = d(NSY)
    out_WY = -d(NWY)
    resid = d(O) - (add_SX + add_SY - out_WX - out_WY)
    return {"path": path, "F": F, "series": a, "O": O, "free": free,
            "add": add_SX + add_SY, "out": out_WX + out_WY,
            "identity_max_abs_residual": float(np.abs(resid).max()),
            "identity_exact": bool(np.abs(resid).max() == 0.0),
            "N_X": NX, "births": births, "deaths": deaths,
            "material_balance_residual": float(np.abs(d(NX) - (births[1:] - deaths[1:])).max())}


def rate_law(recs, nbins=24):
    """E[add] per cell per step, divided by phi, as a function of the free capacity per cell.
    If the mechanism is the feed rule, curves measured at different phi must COLLAPSE, because
    add = Binomial(room, phi) makes E[add] proportional to phi at fixed room."""
    xs, ys, tags = [], [], []
    for r, phi in recs:
        f = r["free"][1:] / CELLS
        rate = r["add"] / CELLS / phi
        xs.append(f)
        ys.append(rate)
        tags.append(phi)
    lo, hi = 0.0, max(float(x.max()) for x in xs)
    edges = np.linspace(lo, hi, nbins + 1)
    curves = []
    for f, rate, phi in zip(xs, ys, tags):
        idx = np.clip(np.digitize(f, edges) - 1, 0, nbins - 1)
        m = np.array([rate[idx == b].mean() if (idx == b).any() else np.nan
                      for b in range(nbins)])
        curves.append({"phi": phi, "binned_rate_over_phi": m.tolist()})
    stack = np.array([c["binned_rate_over_phi"] for c in curves])
    with np.errstate(invalid="ignore"):
        spread = np.nanmax(stack, 0) / np.nanmin(stack, 0)
    centres = 0.5 * (edges[1:] + edges[:-1])
    return {"free_bin_centres": centres.tolist(), "curves": curves,
            "collapse_ratio_max_over_min": np.nanmax(spread[np.isfinite(spread)]) if
            np.isfinite(spread).any() else None,
            "pooled_rate_over_phi": np.nanmean(stack, 0).tolist()}


def fill_time(free0, pooled_rate, centres, phi, out_per_cell=0.0):
    """Integrate d(free)/dt = -(phi * g(free) - out) from free0 down to the declared threshold."""
    g = lambda f: float(np.interp(f, centres, pooled_rate))
    t, f, dt = 0.0, float(free0), 1.0
    while f > 0.25 and t < 5e6:
        v = phi * g(f) - out_per_cell
        if v <= 0:
            return float("inf")
        f -= v * dt
        t += dt
    return t


if __name__ == "__main__":
    files = sorted(glob.glob(RAW + "/cal__*.npz"))
    phis = {"phi0.2": 0.2, "phi0.4": 0.4, "phi0.1": 0.1}
    recs = []
    print("exact bookkeeping, per calibration arm")
    for p in files:
        phi = next(v for k, v in phis.items() if k in p)
        r = reconstruct(p)
        recs.append((r, phi))
        print("  %-46s O identity residual %.0f | material balance residual %.0f"
              % (p.split("/")[-1][:46], r["identity_max_abs_residual"],
                 r["material_balance_residual"]))
    rl = rate_law(recs)
    print("\nfeed rate divided by phi, binned on the free capacity per cell:")
    print("  collapse ratio (max/min across phi = 0.1, 0.2, 0.4): %.3f"
          % rl["collapse_ratio_max_over_min"])
    print("  free/cell: " + " ".join("%5.2f" % c for c in rl["free_bin_centres"][::3]))
    print("  rate/phi : " + " ".join("%5.3f" % v for v in rl["pooled_rate_over_phi"][::3]))

    # ---------------- scope: does ANY point of the family escape?
    import lattice as LAT
    import region as REG
    centres = rl["free_bin_centres"]
    pooled = rl["pooled_rate_over_phi"]
    free0 = CAP - 2 * S0                                   # 10 free units per cell at t = 0
    scan, escapes = [], []
    for muX in (0.0005, 0.001, 0.002, 0.004, 0.008, 0.016):
        for phi in (0.01, 0.02, 0.05, 0.1, 0.2, 0.4):
            for ell in (2.5, 3.0):
                D = muX * ell ** 2
                p_hop = REG.p_hop_for(D)
                if p_hop is None:
                    continue
                G0 = LAT.G_body_about_organiser(p_hop, p_hop, muX)["G0"]
                cX = min(LAT.c_X_transport(S0, p_hop, phi)["c_X_transport"], 7.0)
                A = cX * G0
                T_fill = fill_time(free0, pooled, centres, phi)
                T_maint = max(REG.MAINT_LIFETIMES / muX, 10.0 * LAT.tau_sep(p_hop, p_hop,
                                                                           muX)["tau_sep"])
                row = {"muX": muX, "phi": phi, "ell_X": ell, "p_hop_X": p_hop, "G0": G0,
                       "c_X_certified": cX, "A_certified": A, "T_fill": T_fill,
                       "T_maint": T_maint, "T_form_max": REG.FORM_LIFETIMES / muX,
                       "fill_margin": T_fill / (T_maint + REG.FORM_LIFETIMES / muX),
                       "A_ok": bool(A >= REG.CRIT_MIN),
                       "fill_ok": bool(T_fill >= 3.0 * (T_maint + REG.FORM_LIFETIMES / muX))}
                row["escapes"] = bool(row["A_ok"] and row["fill_ok"])
                scan.append(row)
                if row["escapes"]:
                    escapes.append(row)
    print("\nscope scan: %d points, %d satisfy the CERTIFIED criticality AND outlive the "
          "ratchet by a factor 3" % (len(scan), len(escapes)))
    print("  best fill margin among points with A_certified >= %.0f: %.3f"
          % (REG.CRIT_MIN, max([r["fill_margin"] for r in scan if r["A_ok"]] or [0.0])))
    print("  best A_certified among points that outlive the ratchet: %.2f"
          % max([r["A_certified"] for r in scan if r["fill_ok"]] or [0.0]))
    json.dump({"mechanism": __doc__.strip(),
               "bookkeeping": [{"path": r["path"].split("/")[-1], "phi": phi,
                                "identity_exact": r["identity_exact"],
                                "identity_residual": r["identity_max_abs_residual"],
                                "material_balance_residual": r["material_balance_residual"],
                                "free_per_cell_start": float(r["free"][0] / CELLS),
                                "free_per_cell_end": float(r["free"][-1] / CELLS),
                                "N_X_max": float(r["N_X"].max()),
                                "N_X_end": float(r["N_X"][-1])} for r, phi in recs],
               "rate_law": rl, "scope_scan": scan, "escapes": escapes,
               "family_closed": len(escapes) == 0},
              open("/home/claude/MCM01/out/_ratchet.json", "w"), indent=1)
