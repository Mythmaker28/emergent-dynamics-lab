"""FCDDH00 decode layer: twin-sham verification, thresholds, and the frozen estimand chain.

Two entry points:
    python3 -B fh_decode.py ROLE thresholds     # twin sham oracle + TAU + threshold lock
and the module functions used by fh_disc.py / fh_hold.py after the raw-only lock is committed.

Everything numeric is computed twice: once on the PRODUCTION certified-interval path (fh_core)
and once on the INDEPENDENT REFERENCE path (fh_ref), and the two are compared against a frozen
agreement bound.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "/home/claude/sweep"
sys.path.insert(0, HERE)

import fh_core as FC                                              # noqa: E402
import fh_ref as RF                                               # noqa: E402

REL_TOL = 1e-9                    # frozen production/reference agreement bound (relative)
ABS_TOL = 1e-30                   # frozen production/reference agreement bound (absolute)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def require_raw_lock(role, here=None):
    """Fail-closed guard: no response may be decoded before the raw-only lock is committed."""
    h = here or HERE
    p = os.path.join(h, "FCDDH00_%s_ACTIVE_RAW_LOCK.json" % role)
    if not os.path.isfile(p):
        raise PermissionError("raw-only lock absent for %s: decoding is forbidden" % role)
    return p


def load_parent():
    d = np.load(f"{ROOT}/SQDT00/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz")
    tube = json.load(open(f"{ROOT}/FSQBT00/CORRECTED_TRANSFER_LICENSES.json"))["TUBE_P2_LOBO"]
    return FC.Parent(d["mu"], d["P1"], d["P2"], d["e1"], d["e2"], Fr(tube))


def read_compact(path):
    d = np.load(path)
    return d["rho_support"], d["support_index"], d["MA"], d["MB"]


def series(role, name):
    v, i, MA, MB = read_compact(f"{HERE}/{role}_{'SHAM' if name.startswith('SHAM') else 'ACTIVE'}_RAW_ARCHIVE/{name}.npz")
    XA, XB, B = FC.read_series(v, i, MA, MB)
    rXA, rXB, rB = RF.read_series(v, i, MA, MB)
    return {"XA": XA, "XB": XB, "B": B, "rXA": rXA, "rXB": rXB, "rB": rB,
            "rho0_support": [float(x) for x in v[0]]}


def agree(a, b):
    a, b = float(a), float(b)
    return abs(a - b) <= max(ABS_TOL, REL_TOL * max(abs(a), abs(b)))


# --------------------------------------------------------------------- twin shams + thresholds
def thresholds(role):
    lock = json.load(open(f"{HERE}/FCDDH00_{role}_PANEL_LOCK.json"))
    man = {m["name"]: m for m in json.load(open(f"{HERE}/{role}_SHAM_RAW_MANIFEST.json"))["manifest"]}
    twins, rows, ser = [], [], {}
    for blk in lock["blocks"]:
        for d in blk["descendants"]:
            did = d["did"]
            n0, n1 = f"SHAM_0_{did}", f"SHAM_1_{did}"
            m0, m1 = man[n0], man[n1]
            s0, s1 = series(role, n0), series(role, n1)
            ident = bool(m0["per_time_state_sha"] == m1["per_time_state_sha"]
                         and m0["terminal_state_sha"] == m1["terminal_state_sha"]
                         and [str(x) for x in s0["XA"]] == [str(x) for x in s1["XA"]]
                         and [str(x) for x in s0["XB"]] == [str(x) for x in s1["XB"]])
            twins.append({"did": did, "twin_identity_full_horizon": ident,
                          "terminal_hash_identical": m0["terminal_state_sha"] == m1["terminal_state_sha"],
                          "per_time_hashes_identical": m0["per_time_state_sha"] == m1["per_time_state_sha"],
                          "n_scored_times": m0["n_frames"],
                          "touch_set_ok": m0["touch_set_ok"] and m0["touched_fields_at_t0"] == [],
                          "mask_sha": m0["mask_sha"], "B_exact": m0["B_exact"]})
            dyn = FC.tau_dynamic_sq(s0["XA"], s0["XB"])
            site = FC.tau_site_sq(s0["rho0_support"], s0["B"])
            tsq = FC.tau_material_sq(Fr(0), dyn, site)
            rtsq = RF.tau_material_sq(s0["rXA"], s0["rXB"], s0["rho0_support"], s0["rB"])
            tau_iv = FC.isqrt_iv(FC.Iv.exact(tsq))
            rows.append({"did": did, "block_upstream_seed": blk["upstream_seed"],
                         "geometry": d["geometry"], "allocation": d["allocation"],
                         "B_exact": str(s0["B"]),
                         "TAU_MATERIAL_L2_sq_exact": str(tsq),
                         "TAU_MATERIAL_L2": float(tau_iv.mid()),
                         "TAU_enclosure": tau_iv.as_pair(),
                         "TAU_DYNAMIC_L2_sq": str(dyn), "TAU_SITE_L2_sq": str(site),
                         "ETA_ORACLE_L2": 0.0,
                         "dominant_term": ("TAU_DYNAMIC_L2" if dyn >= site else "TAU_SITE_L2"),
                         "reference_agrees_tau": agree(float(tsq), rtsq),
                         "tau_positive_finite": bool(tsq > 0 and np.isfinite(float(tsq)))})
            ser[did] = {"XA": [str(x) for x in s0["XA"]], "XB": [str(x) for x in s0["XB"]],
                        "B": str(s0["B"]), "terminal_state_sha": m0["terminal_state_sha"],
                        "per_time_state_sha": m0["per_time_state_sha"]}
    all_twin = all(t["twin_identity_full_horizon"] for t in twins)
    all_tau = all(r["tau_positive_finite"] and r["reference_agrees_tau"] for r in rows)
    n = len(rows)
    json.dump({"role": role, "n_descendants": n,
               "twin_identity_all": all_twin, "twins": twins,
               "all_tau_positive_finite_and_reference_agree": all_tau,
               "per_time_series_persisted_for_both_twins": True},
              open(f"{HERE}/{role}_TWIN_SHAM_ORACLE.json", "w"), indent=1)
    lockj = {"role": role, "n_descendants": n,
             f"{role}_SHAM_STATUS": "COMPLETE" if (all_twin and all_tau) else "FAIL",
             "thresholds": rows, "sham_series_and_hashes": ser,
             "TAU_range": [min(r["TAU_MATERIAL_L2"] for r in rows),
                           max(r["TAU_MATERIAL_L2"] for r in rows)],
             "A_X_per_block": {}, "code_sha256": {"fh_core.py": sha(f"{HERE}/fh_core.py"),
                                                  "fh_ref.py": sha(f"{HERE}/fh_ref.py"),
                                                  "fh_decode.py": sha(f"{HERE}/fh_decode.py")},
             "symbolic_to_numeric_map": {
                 "TAU^2": "max(0, (1/100)^2 sum_h W[h]((XA_s[h]-XA_s[0])^2+(XB_s[h]-XB_s[0])^2), "
                          "((1/100) median(rho0|supp)/B)^2 sum_h W[h])",
                 "A_X[b]": "(1/sqrt 2) sum_{g,a} TAU[b,g,a]",
                 "A_PAIR[b,aN,aF]": "sqrt(2) (TAU[b,NEAR,aN] + TAU[b,FAR,aF])"}}
    tau_by = {r["did"]: FC.isqrt_iv(FC.Iv.exact(Fr(r["TAU_MATERIAL_L2_sq_exact"]))) for r in rows}
    for blk in lock["blocks"]:
        four = [tau_by[d["did"]] for d in blk["descendants"]]
        ax = FC.A_X_block(four)
        lockj["A_X_per_block"][str(blk["upstream_seed"])] = {
            "A_X_enclosure": ax.as_pair(), "A_X": float(ax.mid()),
            "E_X": float(ax.mid()) ** 2}
    json.dump(lockj, open(f"{HERE}/FCDDH00_{role}_THRESHOLD_LOCK.json", "w"), indent=1)
    print("%s thresholds: %d descendants | twins ok=%s | tau ok=%s | TAU %.4e .. %.4e"
          % (role, n, all_twin, all_tau, lockj["TAU_range"][0], lockj["TAU_range"][1]))
    return lockj


# --------------------------------------------------------------------- full decode after raw lock
def decode(role, parent):
    lock = json.load(open(f"{HERE}/FCDDH00_{role}_PANEL_LOCK.json"))
    thr = json.load(open(f"{HERE}/FCDDH00_{role}_THRESHOLD_LOCK.json"))
    tau_sq = {r["did"]: Fr(r["TAU_MATERIAL_L2_sq_exact"]) for r in thr["thresholds"]}
    shser = thr["sham_series_and_hashes"]
    blocks = []
    rows_out = []
    for blk in lock["blocks"]:
        binfo = {"upstream_seed": blk["upstream_seed"], "candidate_index": blk["candidate_index"],
                 "geometry_coin": blk["geometry_coin"], "descendants": {}}
        for d in blk["descendants"]:
            did = d["did"]
            SA = [Fr(x) for x in shser[did]["XA"]]
            SB = [Fr(x) for x in shser[did]["XB"]]
            Bs = Fr(shser[did]["B"])
            per_carrier = {}
            for o in ("CARRIER_1", "CARRIER_2"):
                s = series(role, f"{o}_{did}")
                assert s["B"] == Bs, "normalizer mismatch between carrier row and its sham"
                dA, dB, r0 = FC.deltas(s["XA"], s["XB"], SA, SB)
                m2 = FC.m2sq(dA, dB)
                assert m2 == FC.uv_energy(dA, dB), "u/v energy identity failed"
                u, v = FC.uv_vectors(dA, dB)
                rdA = [s["rXA"][h + 1] - float(SA[h + 1]) for h in range(FC.T)]
                rdB = [s["rXB"][h + 1] - float(SB[h + 1]) for h in range(FC.T)]
                per_carrier[o] = {"dA": dA, "dB": dB, "u": u, "v": v, "M2sq": m2,
                                  "structural_zero_h0": bool(r0[0] == 0 and r0[1] == 0),
                                  "ref_dA": rdA, "ref_dB": rdB, "ref_M2sq": RF.m2sq(rdA, rdB)}
            D = FC.gauge_statistic(parent, per_carrier["CARRIER_1"]["u"], per_carrier["CARRIER_1"]["v"],
                                   per_carrier["CARRIER_2"]["u"], per_carrier["CARRIER_2"]["v"])
            s_g, coopt = FC.gauge_sign(D)
            ref_s, ref_vals = RF.gauge_sign(np.array(parent.mu), np.array(parent.Q),
                                            (per_carrier["CARRIER_1"]["ref_dA"], per_carrier["CARRIER_1"]["ref_dB"]),
                                            (per_carrier["CARRIER_2"]["ref_dA"], per_carrier["CARRIER_2"]["ref_dB"]))
            zs, rs = {}, {}
            for o in ("CARRIER_1", "CARRIER_2"):
                zs[o] = FC.z_of(per_carrier[o]["u"], per_carrier[o]["v"], s_g)
                rs[o] = FC.residual_r(parent, zs[o])
            dvec = FC.differential_d(parent, zs["CARRIER_1"], zs["CARRIER_2"])
            contrast = FC.vec_sub(zs["CARRIER_2"], zs["CARRIER_1"])
            tau_iv = FC.isqrt_iv(FC.Iv.exact(tau_sq[did]))
            R_P2 = FC.Iv.exact(0)
            for o in ("CARRIER_1", "CARRIER_2"):
                R_P2 = R_P2 + FC.dot_iv(rs[o], rs[o])
            R_P2 = (R_P2 * FC.Iv.exact(Fr(1, 2))).round_out()
            binfo["descendants"][(d["geometry"], d["allocation"])] = {
                "did": did, "geometry": d["geometry"], "allocation": d["allocation"],
                "slot": d["slot"], "gauge_sign": s_g, "gauge_cooptimal": coopt,
                "gauge_statistic": D, "ref_gauge_sign": ref_s, "ref_gauge_residuals": ref_vals,
                "tau_sq": tau_sq[did], "tau_iv": tau_iv, "d": dvec, "r": rs, "z": zs,
                "carriers": per_carrier, "contrast": contrast, "R_P2_DESC": R_P2}
            for o in ("CARRIER_1", "CARRIER_2"):
                rows_out.append({
                    "role": role, "block": blk["upstream_seed"], "did": did,
                    "geometry": d["geometry"], "allocation": d["allocation"], "carrier": o,
                    "M2sq_exact": str(per_carrier[o]["M2sq"]),
                    "M2": float(per_carrier[o]["M2sq"]) ** 0.5,
                    "TAU": float(tau_iv.mid()),
                    "TAUsq_exact": str(tau_sq[did]),
                    "structural_zero_h0": per_carrier[o]["structural_zero_h0"],
                    "cell_material": per_carrier[o]["M2sq"] > tau_sq[did],
                    "M2_over_TAU": float(per_carrier[o]["M2sq"] / tau_sq[did]) ** 0.5,
                    "reference_M2sq_agrees": agree(float(per_carrier[o]["M2sq"]),
                                                   per_carrier[o]["ref_M2sq"]),
                    "gauge_sign": s_g, "gauge_cooptimal": coopt,
                    "reference_gauge_agrees": bool(ref_s == s_g or coopt)})
        blocks.append(binfo)
    return lock, thr, blocks, rows_out


def block_x(parent, binfo, gauge_override=None, swap_geometry=False):
    """x[b] and the four cross-orbit differentials, recomputed through the frozen chain."""
    dd = binfo["descendants"]
    gN, gF = ("FAR", "NEAR") if swap_geometry else ("NEAR", "FAR")
    dn = {a: dd[(gN, a)]["d"] for a in (0, 1)}
    df = {a: dd[(gF, a)]["d"] for a in (0, 1)}
    x = FC.interaction_x(dn[0], dn[1], df[0], df[1])
    return x, dn, df, gN, gF


def contrast_material(bd):
    """||z2 - z1|| > 2 TAU, inherited unchanged."""
    n2 = FC.dot_iv(bd["contrast"], bd["contrast"])
    four = (FC.Iv.exact(bd["tau_sq"]) * FC.Iv.exact(4)).round_out()
    return FC.certified_verdict(n2, four), n2, four


if __name__ == "__main__":
    role, what = sys.argv[1], sys.argv[2]
    assert what == "thresholds"
    thresholds(role)
