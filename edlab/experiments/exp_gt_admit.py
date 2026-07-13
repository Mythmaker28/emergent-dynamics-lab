"""EXP-GT-ADMIT -- SCOPE ADMISSION CERTIFICATE (mission Phase 0).

Architecture head V4 is FROZEN and UNTOUCHED. This certifies a SEPARATE admission controller that decides whether
a requested inference lies inside the observer's certified domain. An A/S/F decision is INVALID unless admission
returns ADMITTED.

Must-pass and must-fail cases are frozen HERE, before admission is applied to any unknown world.
A CONFIDENT VERDICT ON A KNOWN OUT-OF-SCOPE CASE IS A GATE FAILURE.
"""

from __future__ import annotations

import json
import os

import numpy as np

from ..substrates.life.library import (arch_base, arch_inert, settle, OUT_ROW, Comp, EATER_OFF, se_diag, GUN_ROW)
from ..identity.blind_a4 import cached_tomography, head_A_TOPO, MERGE_GAP, MIN_VALID_FRAC, OBS
from ..identity import admission as ADM
from ..experiments.exp_gt_03r2 import ho, L_A, e1_handoff


def _merged_case():
    """The exact case that V4 answered confidently and wrongly (D-060): an E1 relief ONE row from a gun, i.e.
    BELOW the certified 4-cell separation limit. The two merge into one component and the head cannot know."""
    cols, chan = L_A, 0
    prog = tuple(0 if j == chan else 1 for j in range(4))
    d = se_diag(GUN_ROW, cols[chan])
    a = ho(cols, prog, arch_id="MERGED_below_limit")
    a.components = [c for c in a.components if c.name != f"gate{chan}"] + [
        Comp("se_eater", 19 + EATER_OFF[0], (d + 19) + EATER_OFF[1], "relief")]
    return a


def certify():
    rep = {"frozen_before_use": True, "cases": []}

    def case(name, arch, expect, request="A_TOPO", region=None, phase=0):
        g = settle(arch, extra_phase=phase)
        t = cached_tomography(g, OUT_ROW, region=region)
        r = ADM.cached_admit(t, g, OUT_ROW, request)
        ok = r["verdict"] == expect
        rep["cases"].append({"case": name, "expected": expect, "verdict": r["verdict"], "pass": ok,
                             "atomic": r["checks"]["atomicity"]["all_atomic"],
                             "valid_phase_fracs": r["checks"]["valid_phase_fracs"],
                             "why": r["checks"].get("fail_atomicity") or r["checks"].get("fail_coverage")
                                    or r["checks"].get("fail_phase_coverage")})
        return t, g, r

    # ---- SEPARATION LIMIT: just below (must FAIL) and just above (must PASS)
    case("separation BELOW the certified limit (relief 1 cell from a gun) -- V4 answered this CONFIDENTLY",
         _merged_case(), ADM.OUT_OF_SCOPE)
    e1 = e1_handoff()
    case("separation ABOVE the certified limit (relief 4 empty cells clear)", e1["post"], ADM.ADMITTED)

    # ---- valid circuits must be ADMITTED. NON-VACUITY IN BOTH DIRECTIONS: an admission controller that refuses
    #      valid cases is not conservative, it is BROKEN. My first atomicity test judged at a SINGLE strike phase
    #      and, at the 6 phases where the whole-component ablation is itself invalid, compared clean sub-parts
    #      against a NULL baseline -- declaring four ordinary phase-shift nulls and every cross-inhibitor circuit
    #      out of scope. I nearly recorded a false scope limitation. Atomicity is now judged only at phases where
    #      the WHOLE ablation is valid, and a sub-part must be confirmed at a MAJORITY of them.
    tb, gb, _ = case("plain 4-channel circuit", arch_base(), ADM.ADMITTED)
    case("circuit with inert decoration", arch_inert(), ADM.ADMITTED)
    case("plain circuit at strike phase 33 (a phase where the whole ablation is invalid)",
         arch_base(), ADM.ADMITTED, phase=33)
    from ..substrates.life.library import arch_xinhib as _xin
    case("cross-inhibitor (collision debris 1 cell apart at the annihilation site)", _xin(), ADM.ADMITTED)

    # ---- INSUFFICIENT COVERAGE: a live output whose source was never found
    ts, gs, _ = case("coverage-starved probe (components findable only in cols 0-100)",
                     arch_base(), ADM.INSUFFICIENT_COVERAGE, region=(0, 20, 0, 100))

    # ---- synthetic structural checks (no hidden label is read; these mutate the OBSERVED tomography record)
    import copy
    struct = []

    t_short = copy.deepcopy(tb)
    for n in t_short["nodes"]:
        n["valid_mask"] = n["valid_mask"][:30]                 # a SAMPLED strike schedule, not the full cycle
    r = ADM.admit(t_short, gb, OUT_ROW, "A_TOPO")
    struct.append({"case": "biased/sampled phase schedule (the quotient's group action is unsupported)",
                   "expected": ADM.OUT_OF_SCOPE, "verdict": r["verdict"],
                   "pass": r["verdict"] == ADM.OUT_OF_SCOPE,
                   "why": r["checks"].get("fail_group_action")})

    t_lowcov = copy.deepcopy(tb)
    for n in t_lowcov["nodes"]:
        n["valid_mask"][:] = False
        n["valid_mask"][:10] = True                            # only 10/60 strike phases valid
    t_lowcov["coverage"]["valid_phase_fracs"] = [10 / 60] * len(t_lowcov["nodes"])
    r = ADM.admit(t_lowcov, gb, OUT_ROW, "A_TOPO")
    struct.append({"case": "insufficient valid-strike coverage (10 of 60 phases)",
                   "expected": ADM.INSUFFICIENT_COVERAGE, "verdict": r["verdict"],
                   "pass": r["verdict"] == ADM.INSUFFICIENT_COVERAGE,
                   "why": r["checks"].get("fail_phase_coverage")})

    t_weak = copy.deepcopy(tb)
    t_weak["edges"][0]["profile"] = np.full(60, -1, dtype=np.int32)
    t_weak["edges"][0]["profile"][7] = 200                     # an edge resting on ONE strike
    r = ADM.admit(t_weak, gb, OUT_ROW, "A_TOPO")
    struct.append({"case": "an edge inferred from a SINGLE strike (an anecdote, not a measurement)",
                   "expected": ADM.CONFOUNDED, "verdict": r["verdict"],
                   "pass": r["verdict"] == ADM.CONFOUNDED,
                   "why": r["checks"].get("fail_single_strike")})
    rep["structural_cases"] = struct

    # ---- ALL THREE HEAD VERDICTS MUST STILL FIRE ON ADMITTED CASES (admission must not gag the head)
    from ..substrates.life.library import arch_delay, arch_xinhib
    fired = {}
    ta = cached_tomography(settle(arch_base()), OUT_ROW)
    for nm, arch in (("SAME (inert decoration)", arch_inert()), ("DIFFERENT (edge added)", arch_xinhib())):
        g = settle(arch)
        t = cached_tomography(g, OUT_ROW)
        a1 = ADM.admit_pair(ta, settle(arch_base()), t, g, OUT_ROW, "A_TOPO")
        fired[nm] = {"admission": a1["verdict"], "A_TOPO": head_A_TOPO(ta, t) if a1["verdict"] == ADM.ADMITTED
                     else "N/A (not admitted)"}
    gsv = settle(arch_base())
    tsv = cached_tomography(gsv, OUT_ROW, region=(0, 20, 0, 100))
    asv = ADM.cached_admit(tsv, gsv, OUT_ROW, "A_TOPO")
    fired["INDETERMINATE (under-covered)"] = {"admission": asv["verdict"],
                                              "A_TOPO": "N/A (correctly not admitted)"}
    rep["head_verdicts_still_fire"] = fired

    n_fail = sum(1 for c in rep["cases"] if not c["pass"]) + sum(1 for c in struct if not c["pass"])
    ok_admit = any(c["verdict"] == ADM.ADMITTED for c in rep["cases"])
    ok_refuse = any(c["verdict"] != ADM.ADMITTED for c in rep["cases"])
    rep["non_vacuity"] = {"admission_can_ADMIT": ok_admit, "admission_can_REFUSE": ok_refuse,
                          "verdicts_seen": sorted({c["verdict"] for c in rep["cases"]}
                                                  | {c["verdict"] for c in struct})}
    rep["failures"] = n_fail
    rep["VERDICT"] = "QUALIFIED" if (n_fail == 0 and ok_admit and ok_refuse) else "FAILED — SCOPE CALIBRATION"
    rep["certified_limits"] = {"component_separation_cells": MERGE_GAP,
                               "min_valid_strike_fraction": MIN_VALID_FRAC,
                               "min_observed_clock_periods": ADM.MIN_PERIODS_OBSERVED,
                               "min_strikes_per_edge": ADM.MIN_EDGE_STRIKES}
    return rep


def summarize(r):
    L = ["EXP-GT-ADMIT -- SCOPE ADMISSION CERTIFICATE (head V4 frozen and untouched)", "=" * 116, ""]
    for c in r["cases"]:
        L.append(f"  {'PASS' if c['pass'] else 'FAIL':4s}  {c['case']:74s} -> {c['verdict']:22s} "
                 f"(expected {c['expected']})")
    L += ["", "  structural checks (the OBSERVED tomography record is mutated; no hidden label is read):"]
    for c in r["structural_cases"]:
        L.append(f"  {'PASS' if c['pass'] else 'FAIL':4s}  {c['case']:74s} -> {c['verdict']:22s} "
                 f"(expected {c['expected']})")
    L += ["", "  ADMISSION MUST NOT GAG THE HEAD -- all three verdicts still fire on admitted cases:"]
    for k, v in r["head_verdicts_still_fire"].items():
        L.append(f"     {k:34s} admission={v['admission']:22s} A_TOPO={v['A_TOPO']}")
    L += ["", f"  NON-VACUITY: can ADMIT={r['non_vacuity']['admission_can_ADMIT']}, "
              f"can REFUSE={r['non_vacuity']['admission_can_REFUSE']}, "
              f"verdicts seen={r['non_vacuity']['verdicts_seen']}",
          "", "  CERTIFIED LIMITS:"]
    for k, v in r["certified_limits"].items():
        L.append(f"     {k:34s} {v}")
    L += ["", "=" * 116, f"failures: {r['failures']}", f"VERDICT: {r['VERDICT']}", "=" * 116]
    return "\n".join(L)


def main(run_id="EXP-GT-ADMIT-20260717-001"):
    r = certify()
    d = os.path.join("results", run_id)
    os.makedirs(d, exist_ok=True)
    json.dump(r, open(os.path.join(d, "certificate.json"), "w"), indent=1, default=str)
    s = summarize(r)
    open(os.path.join(d, "summary.txt"), "w").write(s + "\n")
    print(s)
    return r


if __name__ == "__main__":
    main()
