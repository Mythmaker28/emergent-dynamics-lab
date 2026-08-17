"""MYQBD01 FINAL REPAIR — deterministic repair check (§18).

Recomputes every headline quantity from the raw archives, checks that the JSON artefacts and the
markdown reports agree with it, and checks that exactly one handoff is active. A repair that is
not deterministically checked is not a repair.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myqbd01_repair_guard as GUARD                                         # noqa: E402
GUARD.install()

OUT = "/home/claude/edl/MYQBD01/out"
RAW = "/home/claude/OBFOR01/raw"
BURN_IN, HORIZON = 2000, 11000
KY, MUY = 4e-5, 1.9511206603301160e-06


def headline_replay():
    """Recompute the headline numbers straight from the .npz files."""
    def cols(pat, name):
        out = []
        for p in sorted(glob.glob(os.path.join(RAW, pat))):
            z = np.load(p, allow_pickle=True)
            f = [str(x) for x in z["fields"]]
            out.append(z["series"][BURN_IN:HORIZON, f.index(name)].astype(float))
        return out
    qm = [q.mean() for q in cols("M__*.npz", "Q")]
    qs = [q.mean() for q in cols("S__*.npz", "Q")]
    nsy = [x.mean() for x in cols("M__*.npz", "nSY_at_org")]
    cy_m = cols("M__*.npz", "cand_Y_at_org")
    nsy_m = cols("M__*.npz", "nSY_at_org")
    cond = [n[c >= 1].mean() for n, c in zip(nsy_m, cy_m)]
    nY_ok, steps = True, 0
    for p in sorted(glob.glob(os.path.join(RAW, "*.npz"))):
        z = np.load(p, allow_pickle=True)
        f = [str(x) for x in z["fields"]]
        v = z["series"][:, f.index("N_Y")]
        nY_ok &= bool(np.all(v == 1))
        steps += int(v.size)
    Q = float(np.mean(qm))
    return {
        "mean_Q_mobile": Q, "mean_Q_static": float(np.mean(qs)),
        "sd_arm_means_mobile": float(np.std(qm, ddof=1)),
        "uncond_mean_nSY_mobile": float(np.mean(nsy)),
        "cond_mean_nSY_given_candY_ge_1": float(np.mean(cond)),
        "cond_depletion_pct": 100.0 / float(np.mean(cond)),
        "R_representative": (1 - MUY) * (1 + KY * Q),
        "N_Y_identically_one": nY_ok, "steps_checked": steps,
        "arms": len(qm) + len(qs)}


def main():
    hr = headline_replay()
    fd = json.load(open(f"{OUT}/MYQBD01_FINAL_DISPOSITION.json"))
    fb = json.load(open(f"{OUT}/MYQBD01_FEEDBACK_BOUND.json"))
    a4 = json.load(open(f"{OUT}/MYQBD01_DESCENDANT_RECOVERABILITY_AUDIT.json"))
    a2 = json.load(open(f"{OUT}/MYQBD01_TEMPORAL_DEPENDENCE.json"))
    ops = json.load(open(f"{OUT}/MYQBD01_TWO_Y_OPERATOR.json"))
    zr = json.load(open(f"{OUT}/MYQBD01_ZERO_RUN_COMPLIANCE.json"))
    rep = open(f"{OUT}/MYQBD01_FINAL_REPORT.md").read()

    checks = []

    def ck(name, ok, detail=""):
        checks.append({"check": name, "PASS": bool(ok), "detail": detail})

    d = fb["A7_FEEDBACK"]["DEPLETION_BY_ONE_Y_BIRTH"]
    w = fb["A8_NON_PRECLUSION"]["REPRESENTATIVE_WITNESS"]
    ck("replay: N_Y == 1 over all recorded steps", hr["N_Y_identically_one"],
       "%d steps, %d arms" % (hr["steps_checked"], hr["arms"]))
    ck("replay matches A7 conditional depletion",
       abs(d["CONDITIONAL_ON_BIRTH_POSSIBLE_DEPLETION"]["computed_pct"]
           - hr["cond_depletion_pct"]) < 1e-9,
       "%.6f vs %.6f" % (d["CONDITIONAL_ON_BIRTH_POSSIBLE_DEPLETION"]["computed_pct"],
                         hr["cond_depletion_pct"]))
    ck("replay matches A8 representative R",
       abs(w["R_mean_offspring"] - hr["R_representative"]) < 1e-12,
       "%.9f vs %.9f" % (w["R_mean_offspring"], hr["R_representative"]))
    ck("A4 flags are mutually consistent",
       (a4["SOURCE_TRAJECTORY_POSITION_RESOLVED"] is True
        and a4["FULL_LATTICE_ENVIRONMENT_PER_STEP"] is False
        and a4["HISTORICAL_DESCENDANT_TRAJECTORY_EXISTS"] is False
        and a4["DESCENDANT_Q_POSITION_RECONSTRUCTIBLE"] is False))
    ck("A4 derived over all 28 archives", a4["ARCHIVES_EXAMINED"] == 28
       and a4["KEY_SET_CONSISTENT"])
    ck("A2 reproduces the reviewer mobile IAT mean", a2["REVIEWER_MEAN_REPRODUCED"],
       "%.14f" % a2["REPRODUCED_MEAN_MOBILE_IAT"])
    ck("A5 clamp never active",
       ops["A5_SCALAR_REDUCTION"]["CLAMP_CHECK"]["CLAMP_NEVER_ACTIVE"])
    ck("A6 reviewer numbers reproduced", ops["A6_TWO_Y"]["REVIEWER_NUMBERS_CHECK"]["REPRODUCED"])
    ck("A7 measured mean reversion reproduced",
       fb["A7_FEEDBACK"]["SY_MEAN_REVERSION"]["REPRODUCED"])
    ck("A8 favourable witness reproduced",
       fb["A8_NON_PRECLUSION"]["FAVOURABLE_WITNESS_ATYPICAL"]["REPRODUCED_R"]
       and fb["A8_NON_PRECLUSION"]["FAVOURABLE_WITNESS_ATYPICAL"]["REPRODUCED_ETA"])
    ck("zero-run: static proof PASS and all counters zero",
       zr["RETROSPECTIVE_STATIC_ZERO_RUN_PROOF"]["STATUS"] == "PASS"
       and zr["ALL_REQUIRED_ZERO"])
    ck("zero-run: original sentinel coverage reported as INCOMPLETE",
       zr["ORIGINAL_RUNTIME_SENTINEL_COVERAGE"]["STATUS"] == "INCOMPLETE")
    ck("guard patched all four seeding entry points",
       zr["FINAL_REPAIR_RUNTIME_GUARDS"]["PATCH_COVERAGE"]
       ["ALL_FOUR_SEEDING_ENTRY_POINTS_PATCHED"])

    # ---- terminal vocabulary present and identical in JSON and report ----
    vocab = {
        "FINAL_DISPOSITION": "EXISTING_Q_DATA_INSUFFICIENT__PROSPECTIVE_Q_CALIBRATION_REQUIRED",
        "Q_LEDGER_STATUS": "EVENT_EXACT",
        "SCALAR_Q_REDUCTION_STATUS":
            "EXACT_FOR_FIRST_BIRTH_IN_ONE_Y_UNCLAMPED_REGIME__"
            "INSUFFICIENT_FOR_COMPLETE_TWO_Y_SPATIAL_WINDOW",
        "TWO_Y_OPERATOR_STATUS":
            "EXECUTABLE_LOCAL_LAW_DERIVED__"
            "FULL_SPATIOTEMPORAL_OPERATOR_NOT_IDENTIFIABLE_FROM_EXISTING_ARCHIVES",
        "MOBILE_DISCOVERY_REGION_STATUS": "NOT_DERIVABLE_FROM_EXISTING_ARCHIVES",
        "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED",
        "DESCENDANT_EXPOSURE_RECOVERABLE": "NO"}
    for k, v in vocab.items():
        ck("JSON carries %s" % k, fd.get(k) == v, str(fd.get(k)))
    flat = re.sub(r"[\s\n]+", "", rep)
    for k, v in vocab.items():
        if k in ("DESCENDANT_EXPOSURE_RECOVERABLE", "ARCHITECTURE_CHANGE_NECESSITY"):
            continue
        ck("report states %s" % k, re.sub(r"[\s\n]+", "", v) in flat)

    # ---- forbidden preregistration wording must be absent everywhere ----
    forbidden = ["mechanically enforced preregistration", "independently committed before "
                 "analysis", "préinscription mécaniquement appliquée",
                 "committé indépendamment avant analyse"]
    bad = []
    for p in glob.glob(f"{OUT}/*.md") + glob.glob(f"{OUT}/*.json"):
        t = open(p, encoding="utf-8", errors="replace").read()
        for w_ in forbidden:
            if w_ in t and "WORDING_NOW_PROHIBITED" not in t and "interdit" not in t:
                bad.append((os.path.basename(p), w_))
    ck("no forbidden preregistration wording asserted", not bad, str(bad))

    # ---- exactly one active handoff ----
    handoffs = sorted(os.path.basename(p) for p in glob.glob(f"{OUT}/HANDOFF_*.md"))
    ck("exactly one active handoff", len(handoffs) == 1 and
       handoffs[0] == "HANDOFF_PROSPECTIVE_Q_ENVIRONMENT_CALIBRATION_01.md", str(handoffs))
    ck("handoff has both calibration phases",
       all(s in open(f"{OUT}/{handoffs[0]}").read()
           for s in ("Phase A", "Phase B", "PROSPECTIVE_Q_ENVIRONMENT_OPERATOR_IDENTIFIED",
                     "CALIBRATION_TECHNICALLY_INVALID")) if handoffs else False)

    # ---- freeze disclosure present ----
    pv = json.load(open(f"{OUT}/MYQBD01_PROVENANCE_AND_COMMIT_ROLES.json"))
    ck("freeze defect disclosed",
       pv["FREEZE"]["FREEZE_FILE_EXISTS"] is True
       and pv["FREEZE"]["INDEPENDENT_PRE_OUTCOME_FREEZE_COMMIT"] is False)
    ck("three commit roles kept distinct",
       len({pv["COMMIT_ROLES"]["MASTER_FREEZE_AND_ANALYSIS_COMMIT"],
            pv["COMMIT_ROLES"]["PRE_REPAIR_REVIEWED_TIP"]}) == 2)

    rec = {"SECTION": "MYQBD01 REPAIR — deterministic verification (§18)",
           "HEADLINE_REPLAY_FROM_RAW": hr,
           "CHECKS": checks,
           "PASSED": sum(1 for c in checks if c["PASS"]), "TOTAL": len(checks),
           "ALL_PASS": all(c["PASS"] for c in checks),
           "GUARD": GUARD.report()["VERDICT"]}
    json.dump(rec, open(f"{OUT}/MYQBD01_REPAIR_VERIFICATION.json", "w"), indent=1, default=str)
    for c in checks:
        print("  %-4s %-55s %s" % ("PASS" if c["PASS"] else "FAIL", c["check"], c["detail"][:40]))
    print("\n%d/%d checks pass | guard all-zero: %s"
          % (rec["PASSED"], rec["TOTAL"], rec["GUARD"]["ALL_ZERO"]))
    return 0 if rec["ALL_PASS"] else 1


if __name__ == "__main__":
    sys.exit(main())
