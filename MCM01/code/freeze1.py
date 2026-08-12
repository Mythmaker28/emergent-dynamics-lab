"""FREEZE 1. Hashes the tested bytes and the pre-freeze plan before the first calibration start."""
import hashlib, json, os, sys
B = "/home/claude/MCM01"
CODE = ["lattice.py", "audit.py", "kinetics.py", "guard.py", "mcm.py", "region.py",
        "protocol.py", "tests_mcm.py", "costprobe.py"]
DOCS = ["MCM01_PREFREEZE_ANALYSIS_PLAN.md", "_audit.json", "_region.json", "_integrity.json",
        "_costprobe.json"]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
code = {f: h(os.path.join(B, "code", f)) for f in CODE}
docs = {f: h(os.path.join(B, "out", f)) for f in DOCS}
core = hashlib.sha256()
for d in (code, docs):
    for k in sorted(d):
        core.update(k.encode()); core.update(d[k].encode())
sys.path.insert(0, B + "/code")
import protocol as P, region as REG, guard
rows = REG.grid()
best, cand = REG.select(rows)
order = sorted(cand, key=REG.selection_key)[:P.N_CANDIDATES]
integ = json.load(open(B + "/out/_integrity.json"))
audit = json.load(open(B + "/out/_audit.json"))
rec = {
 "FREEZE": 1, "frozen_before": "the first calibration start",
 "code_sha256": code, "doc_sha256": docs,
 "METHODS_CORE_HASH": core.hexdigest(),
 "protocol": P.constants(),
 "region": {"n_grid": len(rows), "n_admissible": len(cand),
            "thresholds": {"CRIT_MIN": REG.CRIT_MIN, "N_MIN": REG.N_MIN,
                           "TAU_SEP_MAX": REG.TAU_SEP_MAX, "T_RUN_MAX": REG.T_RUN_MAX,
                           "Q_MAX_EXACT": REG.Q_MAX_EXACT},
            "pinned": {"S0": REG.S0_PIN, "CAP": REG.CAP_PIN, "omega": REG.OMEGA_PIN,
                       "L": REG.L_PIN},
            "tie_break": list(REG.TIE_BREAK)},
 "calibration_points_in_frozen_order": [
     {k: p[k] for k in ("muX", "phi", "ell_X", "rho_Y", "p_hop_X", "p_hop_Y", "G0_relative",
                        "c_X_certified", "criticality_A", "u_star", "N_X_predicted",
                        "tau_sep", "T_run", "kY_future", "muY_future")} for p in order],
 "analytic_winner_before_calibration": {k: best[k] for k in
     ("muX", "phi", "ell_X", "rho_Y", "criticality_A", "N_X_predicted", "T_run")},
 "integrity": {"ALL_PASS": integ["ALL_PASS"], "tests": len(integ["tests"]),
               "mutations": len(integ["mutations"]),
               "test_steps": integ["ledger_after_harness"]["test_steps_used"],
               "starts_consumed_by_harness": integ["ledger_after_harness"]["total"]},
 "audit_summary": audit["summary"],
 "divergence_1519_vs_190": [c for c in audit["claims"]
                            if c["claim"].startswith("resolution of 1519")][0],
 "starts_before_this_freeze": {"cost_probe": guard.used("cost_probe"),
                               "calibration": 0, "confirmation": 0, "control": 0,
                               "note": "the only engine advances before this freeze are the "
                                       "bounded score-blind harness steps and the cost probes "
                                       "on the manifold n[Y] == 0, where both birth "
                                       "probabilities are identically zero"},
}
json.dump(rec, open(B + "/out/_freeze1.json", "w"), indent=1)
print("METHODS_CORE_HASH =", rec["METHODS_CORE_HASH"])
print("calibration points, in the frozen order:")
for p in rec["calibration_points_in_frozen_order"]:
    print("  muX=%-7.4g phi=%-5.2f ell=%-4.1f  A=%-6.2f N*=%-6.0f T_run=%-6.0f"
          % (p["muX"], p["phi"], p["ell_X"], p["criticality_A"], p["N_X_predicted"], p["T_run"]))
