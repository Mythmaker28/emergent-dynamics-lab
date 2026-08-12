import json, sys
import guard, protocol as P, region as REG
guard.set_experiment_mode()
rows = REG.grid()
best, cand = REG.select(rows)
pts = sorted(cand, key=REG.selection_key)[:P.N_CANDIDATES]
res = {"arms": [], "points": [{k: p[k] for k in ("muX","phi","ell_X","rho_Y","criticality_A",
       "c_X_certified","N_X_predicted","G0_relative","T_run")} for p in pts]}
for i, p in enumerate(pts):
    for s in P.SEEDS["calibration"]:
        tag = "cal/p%d_mu%g_phi%g_ell%g/seed%d" % (i, p["muX"], p["phi"], p["ell_X"], s)
        a = P.run_arm("calibration", tag, p, s, "calibration")
        res["arms"].append(a)
        st = a["c_X_stats"]
        print("p%d mu=%-7.4g phi=%-4.2f ell=%-4.1f seed=%d  %-12s formed@%-6s "
              "c_X med=%-7.4f min=%-7.4f  A_meas=%-6.2f  N_X=%-6.0f  u=%-5.2f  %.1fs"
              % (i, p["muX"], p["phi"], p["ell_X"], s, a["outcome"], a["formed_at"],
                 st["median"] if st else float("nan"), st["min"] if st else float("nan"),
                 (st["median"]*p["G0_relative"]) if st else float("nan"),
                 st["N_X_mean"] if st else float("nan"), st["u_mean"] if st else float("nan"),
                 a["wall_seconds"]), flush=True)
res["ledger"] = guard.audit()
json.dump(res, open("/home/claude/MCM01/out/_calibration.json","w"), indent=1, default=str)
print("\nstarts:", json.dumps(res["ledger"]["by_class"]))
