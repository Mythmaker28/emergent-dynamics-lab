"""PPAI Phase B — structural causal audit, plus the terminal wash diagnostic.

Engine-free apart from reading already-produced records.
"""
from __future__ import annotations
import sys, os, json, math, pickle, statistics as S
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/CHMR")
import numpy as np
import chmr_analyse as A

CH = "/home/claude/sweep/CHMR"
K = ("c", "N", "flux_c", "mass", "size", "rg")
O = {"programme": "PUBLIC_PATH_ADAPTIVE_INTERFACE_00", "phase": "B_STRUCTURAL_CAUSAL_AUDIT"}


# ---------------------------------------------------- 1-3 : the dependency graph, from the code
O["DEPENDENCY_GRAPH_PARENT_sc_mcm"] = {
    "edges": [
        ["N,c,uptake", "Psi", "Psi = tanh(k_exp*(N-c) + k_up*(uptake - up_ref))  [engine l.154]"],
        ["Psi", "m1,m2", "dmk = eta_w*Psi - eta_d[k]*mk + eta_t*(tmean-mk) + D_m*lap(mk)"],
        ["m1,m2", "m_plus", "m_plus = m1 + m2"],
        ["m1,m2", "m_minus", "m_minus = m1 - m2"],
        ["m_plus", "uptake", "PRIVATE: g = ... * (1 + lam_plus*tanh(m_plus))   [engine l.79]"],
        ["m_minus", "c", "PRIVATE: c += dt*(... + s*rho*(1 + lam_minus*m_minus) - delta*c) [l.116]"],
        ["uptake", "rho", "rho += g"],
        ["rho", "c", "c += dt*s*rho"],
        ["c", "rho", "chemotactic flux chi(c)*grad(c)"],
        ["rho,U,V,c", "challenge response", "the reader is [size, rg, specific_uptake, mass, c]"],
        ["m_plus", "specific_uptake -> RESPONSE", "DIRECT PRIVATE PATH, one hop, bypasses the bath"],
    ],
    "directed_paths_from_memory_to_response": [
        "m_plus -> uptake -> specific_uptake  : DIRECT, PRIVATE, 1 hop",
        "m_plus -> uptake -> rho -> size/mass : DIRECT, PRIVATE, 2 hops",
        "m_minus -> c production -> c -> chemotaxis -> rho : PUBLIC but species-asymmetric, and "
        "it encodes one state as secretion of one species",
        "m1/m2 -> (nothing else)",
    ],
    "classification": "DIRECT_PUBLIC_PATH is absent; what exists is a DIRECT PRIVATE PATH "
                      "(lam_plus) plus a species-asymmetric secretion path (lam_minus). Neither "
                      "matches the permitted graph.",
}
O["DEPENDENCY_GRAPH_PPAI"] = {
    "edges": [
        ["N,c,uptake", "Psi", "unchanged writer"],
        ["Psi", "m1,m2", "unchanged writer"],
        ["m1 = z", "kappa", "kappa = 1 + g*tanh(z), bounded, odd, centred"],
        ["kappa", "public c,N transport", "face permeability 0.5*(kappa_i + kappa_j) on BOTH c and N"],
        ["public c,N", "rho", "chemotaxis and uptake, unchanged frozen physics"],
        ["rho,U,V,c", "challenge response", "unchanged frozen reader"],
    ],
    "removed": ["lam_plus (m_plus -> uptake)", "lam_minus (m_minus -> c production)",
                "Mf += g*m (memory inheritance by fresh matter)"],
    "directed_paths_from_z_to_response": [
        "z -> kappa -> public c,N -> rho/geometry -> response   : PUBLIC, >= 3 hops",
    ],
    "forbidden_edges_absent": ["z -> response", "z -> force", "z -> survival",
                               "z -> challenge reader", "z -> component identity"],
    "classification": "DIRECT_PUBLIC_PATH by construction, and no private path of any kind.",
}


# --------------------------------------- 4 : coefficients from the SEALED CHMR time series
def coefficients():
    B = pickle.load(open(os.path.join(CH, "chmr_FAR_CONF.pkl"), "rb"))
    T = [0, 25, 50, 100, 150, 200, 250, 300, 350]
    out = {}

    # K_ENV_TO_CORE : d(core gap)/dt per unit halo gap, in the HALO_CROSS arm where the halo is
    # inverted and the core follows it.
    rows = []
    for b in B:
        for i in range(len(T) - 1):
            t0, t1 = T[i], T[i + 1]
            hg = A.hgap(b, "HALO_CROSS", t0)
            c0 = A.cplus(b, "HALO_CROSS", t0, "A"); c1 = A.cplus(b, "HALO_CROSS", t1, "A")
            d0 = A.cplus(b, "HALO_CROSS", t0, "B"); d1 = A.cplus(b, "HALO_CROSS", t1, "B")
            if None in (hg, c0, c1, d0, d1) or abs(hg) < 1e-9:
                continue
            rows.append(((c1 - d1) - (c0 - d0)) / (t1 - t0) / hg)
    out["K_ENV_TO_CORE"] = {"n": len(rows), "median_per_step": S.median(rows) if rows else None,
                            "ci95": A.boot(rows),
                            "units": "d(core gap)/dt per unit halo gap, per step",
                            "identifiable": True}

    # K_CORE_TO_ENV : the halo gap an intact matched pair maintains ABOVE an orphan halo, per
    # unit core gap, at T_RECOVERY.
    rows = []
    for b in B:
        gm = A.hgap(b, "MATCHED_SHAM", 350); go = A.hgap(b, "ORPHAN_HALO", 350)
        cg = (A.cplus(b, "MATCHED_SHAM", 350, "A") or 0) - (A.cplus(b, "MATCHED_SHAM", 350, "B") or 0)
        if None in (gm, go) or abs(cg) < 1e-9:
            continue
        rows.append((gm - go) / cg)
    out["K_CORE_TO_ENV"] = {"n": len(rows), "median": S.median(rows) if rows else None,
                            "ci95": A.boot(rows),
                            "units": "excess halo gap maintained per unit core gap",
                            "identifiable": True}

    # K_ENV_TO_RESPONSE : the signed response gap per unit halo gap, across arms at T_RECOVERY.
    xs, ys = [], []
    for b in B:
        for arm in ("MATCHED_SHAM", "HALO_CROSS", "HALO_CROSS_CORE_ERASE", "DOUBLE_CROSS",
                    "CORE_CROSS"):
            hg = A.hgap(b, arm, 350)
            a, bb = A.resp(b, arm, "A", "response"), A.resp(b, arm, "B", "response")
            if hg is None or a is None or bb is None:
                continue
            xs.append(hg); ys.append(float((a - bb).mean()))
    if len(xs) > 3:
        sx, sy = np.array(xs), np.array(ys)
        k = float(np.polyfit(sx, sy, 1)[0])
        r = float(np.corrcoef(sx, sy)[0, 1])
        out["K_ENV_TO_RESPONSE"] = {"n": len(xs), "slope": k, "pearson_r": r,
                                    "units": "signed response gap per unit halo gap",
                                    "identifiable": True}

    # K_CORE_TO_RESPONSE_GIVEN_ENV : the residual slope on the core gap after the halo gap is
    # partialled out.
    cs = []
    for b in B:
        for arm in ("MATCHED_SHAM", "HALO_CROSS", "HALO_CROSS_CORE_ERASE", "DOUBLE_CROSS",
                    "CORE_CROSS"):
            hg = A.hgap(b, arm, 350)
            ca, cb = A.cplus(b, arm, 350, "A"), A.cplus(b, arm, 350, "B")
            a, bb = A.resp(b, arm, "A", "response"), A.resp(b, arm, "B", "response")
            if None in (hg, ca, cb) or a is None or bb is None:
                continue
            cs.append((hg, ca - cb, float((a - bb).mean())))
    if len(cs) > 4:
        M = np.array(cs)
        X = np.column_stack([np.ones(len(M)), M[:, 0], M[:, 1]])
        beta, *_ = np.linalg.lstsq(X, M[:, 2], rcond=None)
        out["K_CORE_TO_RESPONSE_GIVEN_ENV"] = {
            "n": len(cs), "beta_core_given_halo": float(beta[2]),
            "beta_halo": float(beta[1]),
            "ratio_core_over_halo": float(abs(beta[2]) / max(abs(beta[1]), 1e-12)),
            "identifiable": True}
    out["transfer_function"] = ("NOT ATTEMPTED. CHMR sampled 12 times on a single relaxation; "
                               "that cannot identify a frequency-domain response. The four "
                               "coefficients above are local slopes, not a transfer function.")
    return out


O["COEFFICIENTS"] = coefficients()
O["WHY_SATURATION_ALONE_WOULD_NOT_REPAIR_THE_PATH"] = (
    "The parent writer saturates: Psi = tanh(...) makes N0 and NN store the same m_plus to 1e-4 "
    "(measured in DOMC Phase C). A less saturating writer would widen the DYNAMIC RANGE of the "
    "stored value. It would not create an output edge. In the parent graph the only edges leaving "
    "the memory are lam_plus (private, straight into the response reader) and lam_minus "
    "(species-asymmetric secretion). Desaturating the writer changes how much is written, not "
    "where it can act; a bigger number on a wire that goes nowhere public is still not causal "
    "ownership. That is why this programme adds an OUTPUT edge and removes the private ones, "
    "rather than retuning eta_w or k_exp.")


# ----------------------------------------- the terminal wash diagnostic, all three gain classes
def wash_diagnostic():
    d = json.load(open("ppai_dev.json"))
    out = {}
    for name, g in (("NEGATIVE_FEEDBACK", -1 / 3), ("ZERO_FEEDBACK", 0.0),
                    ("POSITIVE_FEEDBACK", 1 / 3)):
        runs = [r for r in d["runs"] if abs(r["gain"] - g) < 1e-9]
        rows = []
        for t in [x["t"] for x in runs[0]["metrics"]]:
            worst, zs = {}, []
            for r in runs:
                rec = next(y for y in r["series"] if y["t"] == t)
                met = next(y for y in r["metrics"] if y["t"] == t)
                zs.append(met["z_sep_ratio"])
                for k in K:
                    a, b = rec["public"]["A"][k], rec["public"]["B"][k]
                    lvl = 0.5 * (abs(a) + abs(b))
                    worst[k] = max(worst.get(k, 0.0), abs(a - b) / lvl if lvl > 1e-12 else 0.0)
            rows.append({"t": t, "relative_public_difference": worst,
                         "worst_key": max(worst, key=worst.get),
                         "worst_value": max(worst.values()),
                         "min_z_sep_ratio": min(zs)})
        out[name] = rows
    return out


O["WASH_DIAGNOSTIC_ALL_GAIN_CLASSES"] = wash_diagnostic()
_p = O["WASH_DIAGNOSTIC_ALL_GAIN_CLASSES"]
O["WASH_VERDICT"] = {
    "FROZEN_CRITERION_RESULT": "NO_WASH_WINDOW",
    "second_well_posed_normalisation": "NO_WASH_WINDOW",
    "why_the_first_statistic_was_ill_posed": (
        "the frozen criterion normalised each public A-B difference by its own value at the START "
        "of the wash. Mass and size start nearly equal (21 cells against 21), so that denominator "
        "is near zero and the criterion demands a difference that is already ~0 to stay ~0 "
        "forever. It is the same small-denominator trap this programme corrected in DOMC. The "
        "second statistic, |A-B| divided by the mean level, is well posed. NO TARGET OUTCOME had "
        "been computed when the second statistic was introduced: only the wash diagnostic itself."),
    "what_the_well_posed_statistic_shows": (
        "the halo difference falls from 148 % to 48 % of the mean level over 560 steps and never "
        "approaches 10 %, while mass and size DIVERGE from 8 % and 5 % to 46 % and 47 % and stay "
        "there. The public state does not converge; it separates. z separation meanwhile falls "
        "below the 50 % floor at t ~ 480."),
    "is_it_caused_by_the_new_coupling": (
        "NO. The same failure occurs at ZERO_FEEDBACK, where the engine is bit-identical to the "
        "frozen root ScaffoldEngine. The unmatchable public state is inherited from the founding "
        "and history construction of DOMC/CHMR, not created by the adaptive interface."),
    "consequence": "the stop rule NO_WASH_WINDOW fires. No confirmatory arm may be run, because "
                   "every downstream gate is conditioned on a matched public state.",
}
json.dump(O, open("ppai_audit.json", "w"), indent=1, default=str)

for k, v in O["COEFFICIENTS"].items():
    print(k, "=", json.dumps(v, default=str)[:220])
print()
for name in ("NEGATIVE_FEEDBACK", "ZERO_FEEDBACK", "POSITIVE_FEEDBACK"):
    r = O["WASH_DIAGNOSTIC_ALL_GAIN_CLASSES"][name]
    last = r[-1]
    print(f"{name:18s} t=560: worst public relative difference = {last['worst_value']:.3f} "
          f"on '{last['worst_key']}' | z separation = {last['min_z_sep_ratio']:.3f} "
          f"| any time passing 10 %/50 %: "
          f"{any(x['worst_value'] <= 0.10 and x['min_z_sep_ratio'] >= 0.50 for x in r)}")
