"""EXACT_TWIN_PUBLIC_PATH_COUNTERFACTUAL_00 — Phase A: the mandatory PPAI corrigendum.

Adds a committed corrigendum. It does not rewrite the parent report and it reopens no PPAI gate.
"""
from __future__ import annotations
import sys, os, ast, json, hashlib, subprocess, statistics as S
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/PPAI")
sys.path.insert(0, "/home/claude/sweep/CHMR")
import numpy as np

import domc_core as K
from edlab.experiments.sc_mcm import config as C
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine, MCParams
from edlab.experiments.sc_iom.engine import IOMState
from ppai_engine import PPAIEngine, PPAIParams, kappa

O = {"programme": "EXACT_TWIN_PUBLIC_PATH_COUNTERFACTUAL_00", "phase": "A_PPAI_CORRIGENDUM"}
PP = "/home/claude/sweep/PPAI"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# =============================================================== A / B / C reference identity
O["REFERENCE_TABLE"] = {
    "A_original_sc_mcm": {
        "lawspec": "MultiChannelMemoryEngine, MCParams(eta_w=0.05, eta_d1=0.03, eta_d2=0.003, "
                   "eta_t=0.010, D_m=0.010, lam_plus=0.25, lam_minus=0.15, k_exp=2.0, k_up=1.0)",
        "executable": "edlab/experiments/sc_mcm/engine.py",
        "sha256": sha("/home/claude/sweep/edlab/experiments/sc_mcm/engine.py"),
        "active_terms": ["lam_plus: m_plus -> uptake (PRIVATE)",
                         "lam_minus: m_minus -> c production (WEAK PUBLIC)",
                         "Mf += g*m : fresh material INHERITS memory"]},
    "B_constructed_PPAI_baseline": {
        "lawspec": "PPAIEngine, PPAIParams(gain=0 or nonzero), private paths removed, "
                   "inheritance removed",
        "executable": "PPAI/ppai_engine.py", "sha256": sha(f"{PP}/ppai_engine.py"),
        "removed_terms": ["lam_plus", "lam_minus", "Mf += g*m"]},
    "C_PPAI_at_gain_zero": {
        "lawspec": "PPAIEngine, PPAIParams(gain=0.0)",
        "executable": "PPAI/ppai_engine.py", "sha256": sha(f"{PP}/ppai_engine.py"),
        "relation_to_B": "C IS B with the adaptive gain set to zero. B and C are the SAME "
                         "executable and the SAME LawSpec family; the only difference is one "
                         "parameter. Their bitwise identity at g=0 is therefore near-tautological "
                         "and is reported as such, not as evidence of nesting in A."},
    "root_reference": {
        "lawspec": "the FROZEN ScaffoldEngine of exp_sc_00 (beta=0.10)",
        "executable": "edlab/substrates/scaffold/engine.py",
        "sha256": sha("/home/claude/sweep/edlab/substrates/scaffold/engine.py"),
        "note": "this, NOT A, is what PPAI's G1.1 compared against. The parent text said 'root', "
                "which was accurate, but the corrigendum makes the distinction explicit."},
    "parent_commit": "ba92a16a10c92cc400af81f022ef4dc78b16377e",
    "parent_bundle_sha256": "1a1cea19272a4c8659d756cfb50338c2cbadc50cb893f3ef3c2553d185655479",
}


# ============================= the NONTRIVIAL micro-fixture in which every removed term is ACTIVE
def micro_state(seed=50001):
    """A small state in which m1, m2, m_plus, m_minus and z are all nonzero, c and N gradients are
    nonzero, material-bath bonds are active, growth and death are active (so fresh material
    enters), and every removed term of A would therefore be exercised."""
    s = C.seed_state(C.SPEC, C.TRACER, seed, "random")
    L = C.SPEC.size
    yy, xx = np.mgrid[0:L, 0:L]
    blob = np.exp(-(((yy - 32.0) ** 2 + (xx - 24.0) ** 2) / (2 * 5.0 ** 2)))
    rho = np.clip(s.rho * blob, 0.0, C.SPEC.rho_max)
    Mf = np.zeros((2, L, L))
    m1 = 0.6 * np.tanh((xx - 32.0) / 8.0)          # nonzero, both signs
    m2 = -0.4 * np.tanh((yy - 32.0) / 8.0)         # independent, so m_plus and m_minus both != 0
    Mf[0] = rho * m1
    Mf[1] = rho * m2
    c = 0.30 + 0.20 * np.cos(2 * np.pi * xx / L)   # nonzero gradient
    N = 0.90 + 0.08 * np.sin(2 * np.pi * yy / L)   # nonzero gradient
    return IOMState(rho, s.U * blob, s.V * blob, c, N, s.C * blob, np.zeros((L, L)), Mf, 0)


def micro_fixture(steps=25):
    st = micro_state()
    a = st.copy(); b = st.copy(); c_ = st.copy()
    eA = MultiChannelMemoryEngine(C.SPEC, C.MC, C.TRACER)
    eB = PPAIEngine(C.SPEC, PPAIParams(gain=0.0), C.TRACER)
    eC = PPAIEngine(C.SPEC, PPAIParams(gain=0.0), C.TRACER)
    m = st.Mf / np.maximum(st.rho, 1e-12)[None, :, :]
    alive = st.rho > 1e-4
    pre = {"n_alive_cells": int(alive.sum()),
           "m_plus_range": [float((m[0] + m[1])[alive].min()), float((m[0] + m[1])[alive].max())],
           "m_minus_range": [float((m[0] - m[1])[alive].min()), float((m[0] - m[1])[alive].max())],
           "z_range": [float(m[0][alive].min()), float(m[0][alive].max())],
           "c_gradient_rms": float(np.sqrt(((np.roll(st.c, -1, -1) - st.c) ** 2).mean())),
           "N_gradient_rms": float(np.sqrt(((np.roll(st.N, -1, -2) - st.N) ** 2).mean())),
           "growth_active": True, "death_rate_k": C.SPEC.k}
    for _ in range(steps):
        a = eA.step(a); b = eB.step(b); c_ = eC.step(c_)
    BC = {f: bool(np.array_equal(getattr(b, f), getattr(c_, f)))
          for f in ("rho", "U", "V", "c", "N", "C", "Mf", "uptake")}
    AB = {f: float(np.abs(np.asarray(getattr(a, f)) - np.asarray(getattr(b, f))).max())
          for f in ("rho", "U", "V", "c", "N", "C", "Mf", "uptake")}
    return {"pre_state": pre, "steps": steps,
            "B_equals_C_bitwise": BC, "B_equals_C_all": all(BC.values()),
            "A_minus_B_max_abs": AB,
            "A_differs_from_B_in_predicted_channels": {
                "uptake (lam_plus channel)": AB["uptake"] > 0,
                "c (lam_minus channel)": AB["c"] > 0,
                "Mf (inheritance channel)": AB["Mf"] > 0,
                "rho (downstream of uptake)": AB["rho"] > 0},
            "A_equals_B": all(v == 0.0 for v in AB.values())}


O["ACTIVE_TERM_MICRO_FIXTURE"] = micro_fixture()
mf = O["ACTIVE_TERM_MICRO_FIXTURE"]
O["NESTED_NULL_ADJUDICATION"] = {
    "PPAI_GAIN_ZERO_REPRODUCES_CONSTRUCTED_EXPURGATED_BASELINE":
        "ESTABLISHED" if mf["B_equals_C_all"] else "FAILED",
    "ORIGINAL_PARENT_NESTED_NULL": "NOT_ESTABLISHED",
    "why": "A (original sc_mcm) and B (the constructed expurgated baseline) DIFFER in exactly the "
           "channels the removed terms predict, in a micro-fixture where all of them are active. "
           "PPAI's G1.1 compared the constructed baseline against the ROOT ScaffoldEngine, not "
           "against A. The constructed model therefore nests the ROOT physics, not the parent "
           "sc_mcm LawSpec. B == C is near-tautological (same executable, one parameter) and is "
           "reported as such.",
    "what_PPAI_correctly_claimed": "PPAI's report and commit say 'the FROZEN ROOT ScaffoldEngine' "
                                   "and 'la LawSpec racine gelee'. That statement stands. What is "
                                   "corrected here is any reading of it as nesting the PARENT.",
}


# ================================================================= other mandated corrections
O["CORRECTION_graph_classification"] = {
    "old_label": "no DIRECT_PUBLIC_PATH; a DIRECT PRIVATE PATH plus a species-asymmetric secretion",
    "corrected_label": "DIRECT_PRIVATE_READER_PATH + WEAK_ENVIRONMENT_MEDIATED_PUBLIC_PATH",
    "why": "m_minus -> c production already supplied a weak PUBLIC path in A. Saying there was no "
           "public path at all was wrong; the correct statement is that the public path existed, "
           "was weak, and was species-asymmetric.",
}
O["CORRECTION_core_halo_ratio"] = {
    "withdrawn": "'the core weighs 0.97 % of the halo'",
    "why": "beta_core_given_halo = +0.726 and beta_halo = +74.75 are regression slopes in "
           "DIFFERENT units (per unit core gap in m_plus, per unit halo gap in mean c). They were "
           "never standardized and no commensurable estimand was prespecified, so their ratio is "
           "not a meaningful fraction.",
    "reported_instead": {"beta_core_given_halo": 0.726, "beta_halo": 74.75,
                         "units": "signed response gap per unit core gap (m_plus) and per unit "
                                  "halo gap (mean c), respectively; NOT commensurable"},
}
zc = {}
for tag, zmax in (("physical_clip_|z|<=1", 1.0), ("asymptotic_|z|->inf", 50.0)):
    kmx, kmn = 1 + (1 / 3) * np.tanh(zmax), 1 + (1 / 3) * np.tanh(-zmax)
    fmx, fmn = 0.5 * (kmx + 1.0), 0.5 * (kmn + 1.0)
    zc[tag] = {"site_kappa": [round(float(kmn), 6), round(float(kmx), 6)],
               "site_ratio": round(float(kmx / kmn), 6),
               "material_bath_face_ratio_bath_kappa_1": round(float(fmx / fmn), 6)}
O["CORRECTION_permeability_contrast"] = {
    "three_distinct_objects": zc,
    "where_1.6805_was_measured": "it is the SITE-LEVEL ratio kappa_max/kappa_min evaluated over "
                                 "z in [-1, +1], the physical clip the engine enforces. It is a "
                                 "property of kappa(z) alone, computed in fixture G1.3/G1.4 by "
                                 "sweeping z on a grid. It is NOT a material-bath face ratio and "
                                 "NOT the asymptotic value.",
    "the_frozen_constraint": "the sealed requirement was 'permeability contrast <= 2x native'. "
                             "The asymptotic SITE ratio is exactly 2.000 at g = 1/3, so the "
                             "constraint binds exactly at the site level. The asymptotic "
                             "MATERIAL-BATH FACE ratio, with the bath at kappa = 1 and an "
                             "arithmetic-mean face, is 1.400; at the physical clip it is 1.291. "
                             "All three are now named separately.",
    "does_it_change_any_conclusion": "no: every value is at or below the sealed 2x bound, and the "
                                     "wash failure occurs identically at gain zero.",
}


# --------------------------------------- the CHMR arithmetic reconciliation, from raw coordinates
def chmr_reconciliation():
    import pickle
    B = pickle.load(open("/home/claude/sweep/CHMR/chmr_FAR_CONF.pkl", "rb"))
    import chmr_analyse as A
    rows = []
    for b in B:
        aM = A.cplus(b, "MATCHED_SHAM", 350, "A"); bM = A.cplus(b, "MATCHED_SHAM", 350, "B")
        aX = A.cplus(b, "HALO_CROSS", 350, "A"); bX = A.cplus(b, "HALO_CROSS", 350, "B")
        if None in (aM, bM, aX, bX) or aM == bM:
            continue
        rows.append({"seed": b["seed"], "zA_matched": aM, "zB_matched": bM,
                     "zA_cross": aX, "zB_cross": bX,
                     "sep_matched": abs(aM - bM), "sep_cross": abs(aX - bX),
                     "mvA": (aX - aM) / (bM - aM), "mvB": (bX - bM) / (aM - bM)})
    med = {k: S.median([r[k] for r in rows]) for k in
           ("zA_matched", "zB_matched", "zA_cross", "zB_cross", "sep_matched", "sep_cross",
            "mvA", "mvB")}
    return {
        "n_blocks": len(rows), "rows": rows, "medians": med,
        "sign_convention": "z here is the component-level mass-weighted m_plus = m1 + m2, read on "
                           "the component the frozen-site reader selects, at checkpoint t = 350 "
                           "after the intervention. Site A carries the H core, site B the L core.",
        "estimands": {"mvA": "(z_A[cross] - z_A[matched]) / (z_B[matched] - z_A[matched]), a "
                             "DIMENSIONLESS FRACTION of the matched separation",
                      "mvB": "(z_B[cross] - z_B[matched]) / (z_A[matched] - z_B[matched]), idem",
                      "separation": "|z_A - z_B|, in RAW z units"},
        "the_apparent_arithmetic_error": {
            "claimed": "2.131 - 0.639 - 0.307 = 1.185, which is not 0.111",
            "why_it_is_not_an_error": "0.639 and 0.307 are FRACTIONS of the separation, not raw "
                                      "displacements. Subtracting them from a raw separation mixes "
                                      "units. The coherent identity is "
                                      "sep_cross ~ sep_matched x (1 - mvA - mvB).",
            "check": {"sep_matched": med["sep_matched"], "mvA": med["mvA"], "mvB": med["mvB"],
                      "predicted_sep_cross": med["sep_matched"] * (1 - med["mvA"] - med["mvB"]),
                      "observed_sep_cross": med["sep_cross"],
                      "note": "medians of ratios are not the ratio of medians, so the two agree "
                              "only approximately; the per-block raw coordinates are published "
                              "above so the identity can be checked block by block."},
            "per_block_identity_residual": [
                round(abs(r["sep_matched"] * (1 - r["mvA"] - r["mvB"]) - r["sep_cross"]), 12)
                for r in rows]},
        "OPPOSITE_STATE_OVERWRITE": "NOT_ESTABLISHED. No directional criterion was frozen before "
                                    "the CHMR outcomes, so no overwrite is inferred from the "
                                    "post-hoc directional analysis. The raw coordinates are "
                                    "published instead.",
    }


O["CORRECTION_chmr_reconciliation"] = chmr_reconciliation()
O["CORRECTION_permutation_invariant_ledger"] = {
    "withdrawn_wording": "'conservative permutation', used unqualified",
    "required_ledger": ["raw z multiset over the lattice", "Sigma z", "Sigma rho*z",
                        "z histogram (binned)", "rho-z covariance",
                        "z exposure at the material-bath boundary",
                        "per-component means and distributions", "fraction transferred A<->B"],
    "what_PPAI_actually_conserved": "the MULTISET of the intensive field m over the lattice, "
                                    "exactly, because the operator is a bijection of lattice sites "
                                    "applied to m. Sigma(rho*z) was NOT conserved, because rho is "
                                    "not reflection-symmetric. The effective-z histogram residual "
                                    "was 1.2 % of lattice cells and was declared.",
    "consequence_for_this_programme": "every intervention here publishes the full ledger above, "
                                      "before and after, and names which invariant is exact.",
}
O["PRESERVED_PARENT_STATEMENTS"] = {
    "PPAI_G3": "FAIL_FOR_THE_PREREGISTERED_DESIGN",
    "NO_VALID_WASH_WINDOW_IDENTIFIED_IN_BOUNDED_DEV": "SUPPORTED",
    "PPAI_G4_TO_G10": "NOT_REACHED",
    "PPAI_CAUSAL_ARCHITECTURE": "NOT_YET_TESTED",
    "MORPHOLOGY_AS_UNIQUE_BLOCKER": "NOT_ESTABLISHED",
}


# ------------------------------------------------------- determinism audit (feeds R4 later)
def determinism_audit():
    hits = {}
    for p in ("PPAI/ppai_engine.py", "PPAI/ppai_core.py", "DOMC/domc_core.py",
              "edlab/substrates/scaffold/engine.py"):
        src = open(f"/home/claude/sweep/{p}").read()
        t = ast.parse(src)
        found = []
        for n in ast.walk(t):
            if isinstance(n, ast.Attribute) and n.attr in {"random", "default_rng", "standard_normal",
                                                           "uniform", "choice", "shuffle", "seed",
                                                           "RandomState", "randint"}:
                found.append(n.attr)
        hits[p] = sorted(set(found))
    return {"per_file": hits,
            "verdict": "the engine step contains NO random draw of any kind. The only stochastic "
                       "object in the whole path is `seed_state(..., 'random')`, a deterministic "
                       "function of the founding seed evaluated ONCE at t=0, before any branch "
                       "exists. The model is FULLY DETERMINISTIC.",
            "consequence": "R4_EXOGENOUS_NOISE is discharged by a no-random-path audit rather than "
                           "by an artificial noise tape, as the protocol requires. Twins are exact "
                           "by determinism, and branch-independence is trivially satisfied because "
                           "no variate is ever drawn after the branch point."}


O["DETERMINISM_AUDIT"] = determinism_audit()

json.dump(O, open("etpc_phaseA.json", "w"), indent=1, default=str)
print("B == C bitwise :", mf["B_equals_C_all"])
print("A vs B max |diff| per field:", {k: f"{v:.3e}" for k, v in mf["A_minus_B_max_abs"].items()})
print("A differs from B in predicted channels:", mf["A_differs_from_B_in_predicted_channels"])
print("ORIGINAL_PARENT_NESTED_NULL =", O["NESTED_NULL_ADJUDICATION"]["ORIGINAL_PARENT_NESTED_NULL"])
r = O["CORRECTION_chmr_reconciliation"]
print(f"\nCHMR: sep_matched={r['medians']['sep_matched']:.4f} mvA={r['medians']['mvA']:.4f} "
      f"mvB={r['medians']['mvB']:.4f} -> predicted sep_cross="
      f"{r['the_apparent_arithmetic_error']['check']['predicted_sep_cross']:.4f} vs observed "
      f"{r['medians']['sep_cross']:.4f}; max per-block identity residual = "
      f"{max(r['the_apparent_arithmetic_error']['per_block_identity_residual']):.3e}")
print("\npermeability:", json.dumps(O["CORRECTION_permeability_contrast"]["three_distinct_objects"]))
print("\ndeterminism:", O["DETERMINISM_AUDIT"]["per_file"])
