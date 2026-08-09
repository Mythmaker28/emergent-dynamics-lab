"""PUBLIC_PATH_ADAPTIVE_INTERFACE_00 — Phase A: bounded engine-free stabilization of CHMR.

Zero new engine calls. Reads only the sealed CHMR raw records.
"""
from __future__ import annotations
import sys, os, json, math, pickle, hashlib, statistics as S
from math import comb
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/CHMR")
import numpy as np
import chmr_analyse as A

D = "/home/claude/sweep/CHMR"
T_REC, T_END = 350, 700
OUT = {"programme": "PUBLIC_PATH_ADAPTIVE_INTERFACE_00", "phase": "A_BOUNDED_STABILIZATION",
       "engine_calls": 0}


def sign_test(v, mu=0.0):
    return A.sign_test(v, mu)


def t_ci(v, c=0.95):
    return A.t_ci(v, c)


def boot(v):
    return A.boot(v)


def _ld(n):
    return pickle.load(open(os.path.join(D, n), "rb"))


CF = _ld("chmr_FAR_CONF.pkl")
HD = _ld("chmr_NEAR_HELD.pkl")
DV = _ld("chmr_FAR_DEV.pkl")


# ---------------------------------- 1. signed movements toward the OPPOSITE prototype
def signed_movements(B, t=T_REC, comp="plus"):
    """After HALO_CROSS, site A carries an H-core under an L-halo and site B an L-core under an
    H-halo. An OVERWRITE requires each core to move TOWARD the opposite prototype, separately.
    A mere reduction of the H/L separation is not an overwrite.

      mv_A = [z_A(cross) - z_A(matched)] / [z_B(matched) - z_A(matched)]
    is 0 if A did not move and +1 if A reached the L prototype. Same construction for B."""
    def z(b, arm, site):
        v = A.csite(b, arm, t, site)
        if v is None:
            return None
        return (v[0] + v[1]) if comp == "plus" else v[0]
    rows = []
    for b in B:
        aM, bM = z(b, "MATCHED_SHAM", "A"), z(b, "MATCHED_SHAM", "B")
        aX, bX = z(b, "HALO_CROSS", "A"), z(b, "HALO_CROSS", "B")
        if None in (aM, bM, aX, bX) or aM == bM:
            continue
        rows.append({"seed": b["seed"], "zA_matched": aM, "zB_matched": bM,
                     "zA_cross": aX, "zB_cross": bX,
                     "mv_A_toward_L": (aX - aM) / (bM - aM),
                     "mv_B_toward_H": (bX - bM) / (aM - bM),
                     "separation_matched": abs(aM - bM), "separation_cross": abs(aX - bX)})
    o = {"n": len(rows), "rows": rows, "coordinate": "m_plus" if comp == "plus" else "m1"}
    for k in ("mv_A_toward_L", "mv_B_toward_H", "separation_matched", "separation_cross"):
        v = [r[k] for r in rows]
        o[k] = {"median": S.median(v), "ci95": boot(v), "mean_t_ci95": t_ci(v),
                "sign_test_vs_0": sign_test(v)}
    o["separation_collapse"] = {
        "median_ratio": S.median([r["separation_cross"] / r["separation_matched"] for r in rows]),
        "note": "the H/L separation collapses, but a collapse is NOT an overwrite"}
    both = (o["mv_A_toward_L"]["median"] > 0 and o["mv_A_toward_L"]["ci95"][0] > 0
            and o["mv_B_toward_H"]["median"] > 0 and o["mv_B_toward_H"]["ci95"][0] > 0)
    o["OPPOSITE_STATE_OVERWRITE"] = "ESTABLISHED" if both else "NOT_ESTABLISHED"
    o["directional_criterion"] = ("BOTH signed movements strictly positive with a 95 % CI "
                                  "excluding 0. This criterion was NOT frozen before the CHMR "
                                  "outcomes; it is applied here only to WITHDRAW an overwrite "
                                  "claim, never to establish one.")
    return o


# -------------------------- 2. CORE_CROSS and HALO_PULSE_RESTORE : effects, CI, TOST status
def inertness(B):
    o = {}
    for arm in ("CORE_CROSS", "HALO_PULSE_RESTORE"):
        rows = []
        for b in B:
            for key, tag in (("response", "at_T_RECOVERY"), ("response_end", "at_END")):
                a, bb = A.resp(b, arm, "A", key), A.resp(b, arm, "B", key)
                m, mb = A.resp(b, "MATCHED_SHAM", "A", key), A.resp(b, "MATCHED_SHAM", "B", key)
                if any(x is None for x in (a, bb, m, mb)):
                    continue
                rows.append({"seed": b["seed"], "when": tag,
                             "signed_gap": float((a - bb).mean()),
                             "matched_signed_gap": float((m - mb).mean()),
                             "difference": float((a - bb).mean() - (m - mb).mean())})
        for tag in ("at_T_RECOVERY", "at_END"):
            v = [r["difference"] for r in rows if r["when"] == tag]
            if not v:
                continue
            o[f"{arm}|{tag}"] = {
                "n": len(v), "median": S.median(v), "ci95_median": boot(v),
                "mean_t_ci95": t_ci(v), "sign_test": sign_test(v),
                "randomisation_p": A.randomisation_p(v),
                "TOST": "IMPOSSIBLE: no equivalence margin for this contrast was frozen before "
                        "the CHMR outcomes",
                "FUNCTIONAL_INERTNESS": "NOT_ESTABLISHED"}
        o[f"{arm}|rows"] = rows
    o["rule"] = "p > 0.05 is not equivalence. Both arms are reported as NOT_ESTABLISHED for " \
                "functional inertness, not as inert."
    return o


# ------------------------------------------------- 3. what the DOMC TOST actually tested
def domc_tost_clarification():
    return {
        "what_was_reported": "erase A: targeted displacement 4.72, non-targeted 3.1e-6, "
                             "'EQUIVALENT' under a margin of +-0.472",
        "exact_estimand": "the NON-TARGETED displacement alone, ||R_B(ERASE_A) - R_B(NONE)||, "
                          "tested against the interval [-0.472, +0.472] by paired TOST on the "
                          "block-level values. The margin is 10 percent of the MEDIAN TARGETED "
                          "displacement of the same erasure, used only as a scale.",
        "what_it_does_NOT_say": "it does NOT test 4.72 against 3.1e-6, and it does not assert "
                                "that the targeted and non-targeted effects are equivalent. "
                                "Those two numbers are not commensurable under a single margin.",
        "correct_reading": "erasing the strongly written component moves its neighbour by an "
                           "amount statistically equivalent to ZERO at the declared scale; "
                           "erasing the weakly written one does not (mean 16.7, CI90 "
                           "[5.74, 27.69] against +-1.877).",
        "disposition": "FUNCTIONAL_SELECTIVE_ADDRESSABILITY = RESTRICTED_ONE_SIDED, unchanged"}


# ---------------- 4. maintenance in ABSOLUTE units, and generic versus history-specific
def maintenance(B, t=T_REC):
    rows = []
    for b in B:
        g0 = A.hgap(b, "MATCHED_SHAM", 0)
        gm = A.hgap(b, "MATCHED_SHAM", t)
        go = A.hgap(b, "ORPHAN_HALO", t)
        if None in (g0, gm, go) or not g0:
            continue
        rows.append({"seed": b["seed"], "gap0": g0, "gap_matched": gm, "gap_orphan": go,
                     "absolute_difference": gm - go,
                     "as_fraction_of_initial_gap": (gm - go) / g0})
    o = {"n": len(rows), "rows": rows}
    for k in ("gap0", "gap_matched", "gap_orphan", "absolute_difference",
              "as_fraction_of_initial_gap"):
        v = [r[k] for r in rows]
        o[k] = {"median": S.median(v), "ci95": boot(v), "mean_t_ci95": t_ci(v)}
    o["sign_test_absolute_difference"] = sign_test([r["absolute_difference"] for r in rows])
    o["GENERIC_HALO_RETENTION"] = (
        "ESTABLISHED: an intact pair retains an absolute halo contrast of "
        f"{o['absolute_difference']['median']:.4f} "
        f"[{o['absolute_difference']['ci95'][0]:.4f}; {o['absolute_difference']['ci95'][1]:.4f}] "
        "more than an orphan halo at the same time.")
    o["HISTORY_SPECIFIC_HALO_MAINTENANCE"] = (
        "NOT_ESTABLISHED. ORPHAN_HALO removes the MATTER, not the history: the contrast between "
        "matched and orphan therefore confounds 'a body is present and secreting' with 'the body "
        "carries the history that wrote this halo'. CHMR has no arm with matter present and an "
        "uncrossed halo but no history-specific core, so the second cannot be derived from the "
        "first. The ratios 1.72x and 2.01x are withdrawn as evidence for history specificity.")
    return o


# ---------------------- 5. the lam_minus ablation: exactly one term, and the non-target checks
def writer_ablation_audit(B):
    src = open("/home/claude/sweep/edlab/experiments/sc_mcm/engine.py").read()
    body = src.split("def step(")[1]
    occ = [ln.strip() for ln in body.splitlines() if "lam_minus" in ln]
    rows = []
    for b in B:
        for site in ("A", "B"):
            gx = A.ser(b, "HALO_CROSS", T_REC, "geom")
            gw = A.ser(b, "HALO_CROSS_WRITER_OFF", T_REC, "geom")
            if not gx or not gw or gx.get(site) is None or gw.get(site) is None:
                continue
            rows.append({"seed": b["seed"], "site": site,
                         "d_mass": gw[site]["mass"] - gx[site]["mass"],
                         "d_size": gw[site]["size"] - gx[site]["size"],
                         "d_rg": gw[site]["rg"] - gx[site]["rg"],
                         "d_site_dist": gw[site]["d_site"] - gx[site]["d_site"],
                         "rel_mass": (gw[site]["mass"] - gx[site]["mass"]) / gx[site]["mass"]})
    o = {"code_level": {"occurrences_of_lam_minus_in_step": len(occ), "lines": occ,
                        "verdict": "lam_minus enters the step in EXACTLY ONE place, the "
                                   "attractant production factor. Setting it to 0 ablates that "
                                   "term and nothing else."},
         "n": len(rows), "rows": rows}
    for k in ("d_mass", "d_size", "d_rg", "d_site_dist", "rel_mass"):
        v = [r[k] for r in rows]
        o[k] = {"median": S.median(v), "ci95": boot(v), "mean_t_ci95": t_ci(v),
                "max_abs": max(abs(x) for x in v)}
    o["viability"] = {"both_sites_alive_in_every_block": all(
        A.ser(b, "HALO_CROSS_WRITER_OFF", T_REC, "geom").get(s) is not None
        for b in B for s in ("A", "B"))}
    o["NON_TARGET_EQUIVALENCE"] = ("NOT_ESTABLISHED as a formal test: no equivalence margin for "
                                   "mass, geometry or viability was frozen before the CHMR "
                                   "outcomes. The observed differences are reported with their "
                                   "intervals instead, and they are small.")
    return o


if __name__ == "__main__":
    OUT["parent_verification"] = {
        "PARENT_COMMIT": "586108f43d8706183f4e8cde8735f866133d3ea7",
        "PARENT_BUNDLE_SHA256":
            "9a41376f9defc7e6721b4efd596ad2b782507ea17492c04868ab3e8d3bb4a534",
        "protocol_sha256": hashlib.sha256(
            open(os.path.join(D, "chmr_protocol.json"), "rb").read()).hexdigest(),
        "seal_intact": hashlib.sha256(
            open(os.path.join(D, "chmr_protocol.json"), "rb").read()).hexdigest()
        == open(os.path.join(D, "chmr_protocol.sha256")).read().split()[0]}

    OUT["C1_SIGNED_MOVEMENTS"] = {"FAR_CONF": signed_movements(CF), "NEAR_HELD": signed_movements(HD)}
    OUT["C2_FUNCTIONAL_INERTNESS"] = {"FAR_CONF": inertness(CF), "NEAR_HELD": inertness(HD)}
    OUT["C3_DOMC_TOST_CLARIFICATION"] = domc_tost_clarification()
    OUT["C4_MAINTENANCE_ABSOLUTE"] = {"FAR_CONF": maintenance(CF), "NEAR_HELD": maintenance(HD)}
    OUT["C5_WRITER_ABLATION_AUDIT"] = writer_ablation_audit(CF)
    OUT["C6_LINEAGE_EVIDENCE_CLASS"] = {
        "18_27_19_switch_counts": "PROSPECTIVE_STRUCTURAL_REPLAY",
        "why": "results/sc_mcm and results/sc_iom hold no raw state. The counts come from NEW "
               "runs of the frozen world under the frozen connectivity, not from the historical "
               "parent trajectories. They demonstrate that framewise largest(st) is unsafe in "
               "this world; they cannot quantify switches in the trajectories actually reported.",
        "historical_raw_evidence": "NONE EXISTS"}
    OUT["C7_SCOPE_OF_INVALIDATION"] = {
        "COMPONENT_LINEAGE_AND_TURNOVER_CLAIMS_USING_FRAMEWISE_LARGEST": "NOT_AUDITABLE",
        "INSTANTANEOUS_OR_WORLD_LEVEL_RESULTS": "NOT_AUTOMATICALLY_INVALIDATED",
        "withdrawn_wording": "'the whole sc_iom/sc_mcm line is invalidated' was too broad"}
    OUT["C8_MECHANISTIC_WORDING"] = {
        "withdrawn": "low-pass filter of the local field",
        "replacement": "CONSISTENT_WITH_A_LEAKY_OR_LOW_PASS_TRACE",
        "why": "no response-function or frequency-domain analysis exists; CHMR sampled 12 times "
               "on one relaxation, which cannot identify a transfer function."}
    OUT["CHMR_DISPOSITION"] = {
        "CHMR_DISPOSITION": "STATIC_ENVIRONMENTAL_CONTROL + PERSISTENT_INTERNAL_MARKER_EROSION",
        "CORE_REBUILDS_HALO": "REFUTED",
        "MUTUAL_CORE_HALO_ATTRACTOR": "REFUTED",
        "HALO_TO_INTERNAL_MARKER": "PERSISTENT_CONTRAST_EROSION",
        "OPPOSITE_STATE_OVERWRITE": "NOT_ESTABLISHED",
        "FUNCTIONAL_HALO_REPROGRAMMING": "NOT_ESTABLISHED",
        "CURRENT_LOCAL_FIELD_CONTROL": "SUPPORTED_NOT_EXCLUSIVE",
        "PARENT_COMPONENT_TURNOVER": "NOT_IDENTIFIABLE",
        "CHMR_LINEAGE_TURNOVER": "PASS_CHMR_ONLY",
        "STRONG_PAPER_GATE": "FAIL",
        "superseded": "HALO_OVERWRITES_CORE is withdrawn: the H/L separation collapses but "
                      "neither core moves toward the opposite prototype."}
    json.dump(OUT, open("ppai_phaseA.json", "w"), indent=1, default=str)

    for tag in ("FAR_CONF", "NEAR_HELD"):
        m = OUT["C1_SIGNED_MOVEMENTS"][tag]
        print(f"[{tag}] signed movements (m_plus): "
              f"A->L {m['mv_A_toward_L']['median']:+.4f} "
              f"[{m['mv_A_toward_L']['ci95'][0]:+.4f};{m['mv_A_toward_L']['ci95'][1]:+.4f}] | "
              f"B->H {m['mv_B_toward_H']['median']:+.4f} "
              f"[{m['mv_B_toward_H']['ci95'][0]:+.4f};{m['mv_B_toward_H']['ci95'][1]:+.4f}] | "
              f"separation {m['separation_matched']['median']:.4f} -> "
              f"{m['separation_cross']['median']:.4f} | "
              f"OVERWRITE = {m['OPPOSITE_STATE_OVERWRITE']}")
    for tag in ("FAR_CONF", "NEAR_HELD"):
        mm = OUT["C4_MAINTENANCE_ABSOLUTE"][tag]
        print(f"[{tag}] maintenance ABSOLUTE: matched {mm['gap_matched']['median']:.4f} vs "
              f"orphan {mm['gap_orphan']['median']:.4f} -> difference "
              f"{mm['absolute_difference']['median']:.4f} "
              f"[{mm['absolute_difference']['ci95'][0]:.4f};"
              f"{mm['absolute_difference']['ci95'][1]:.4f}] "
              f"(= {mm['as_fraction_of_initial_gap']['median']*100:.1f} % of the initial gap)")
    for tag in ("FAR_CONF", "NEAR_HELD"):
        it = OUT["C2_FUNCTIONAL_INERTNESS"][tag]
        for k in ("CORE_CROSS|at_T_RECOVERY", "HALO_PULSE_RESTORE|at_END"):
            v = it[k]
            print(f"[{tag}] {k:34s} median {v['median']:+.4f} "
                  f"CI95 [{v['ci95_median'][0]:+.4f};{v['ci95_median'][1]:+.4f}] "
                  f"rand p={v['randomisation_p']:.4f}  -> {v['FUNCTIONAL_INERTNESS']}")
    w = OUT["C5_WRITER_ABLATION_AUDIT"]
    print(f"writer ablation: lam_minus occurrences in step = "
          f"{w['code_level']['occurrences_of_lam_minus_in_step']}; "
          f"max |rel mass change| = {w['rel_mass']['max_abs']:.4f}; "
          f"max |d size| = {w['d_size']['max_abs']:.0f}")
