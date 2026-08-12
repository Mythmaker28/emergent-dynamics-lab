"""Apply the FROZEN selection rule with the MEASURED c_X. No new start."""
import json
import numpy as np
import region as REG, protocol as P

cal = json.load(open("/home/claude/MCM01/out/_calibration.json"))
rows = REG.grid()
_, cand = REG.select(rows)
pts = sorted(cand, key=REG.selection_key)[:P.N_CANDIDATES]

# frozen pooling: min over calibration seeds of the median over the measurement window
pooled, detail = {}, []
for p in pts:
    key = tuple(round(p[k], 12) for k in REG.TIE_BREAK)
    meds = [a["c_X_stats"]["median"] for a in cal["arms"]
            if abs(a["point"]["muX"]-p["muX"])<1e-12 and abs(a["point"]["phi"]-p["phi"])<1e-12
            and abs(a["point"]["ell_X"]-p["ell_X"])<1e-12 and a["c_X_stats"]]
    means = [a["c_X_stats"]["mean"] for a in cal["arms"]
             if abs(a["point"]["muX"]-p["muX"])<1e-12 and abs(a["point"]["phi"]-p["phi"])<1e-12
             and abs(a["point"]["ell_X"]-p["ell_X"])<1e-12 and a["c_X_stats"]]
    pooled[key] = min(meds)
    detail.append({"point": {k: p[k] for k in REG.TIE_BREAK},
                   "c_X_certified": p["c_X_certified"], "A_certified": p["criticality_A"],
                   "medians": meds, "means": means,
                   "c_X_pooled_frozen_rule": min(meds),
                   "A_pooled_frozen_rule": min(meds)*p["G0_relative"],
                   "c_X_pooled_mean_variant": min(means),
                   "A_mean_variant": min(means)*p["G0_relative"],
                   "measured_over_certified_mean_variant": min(means)/p["c_X_certified"]})

best, surv = REG.select(rows, c_X_measured=pooled)
print("FROZEN RULE, pooled as declared (min over seeds of the MEDIAN):")
for d in detail:
    print("  mu=%-7.4g phi=%-5.2f ell=%-4.1f | c_X cert %-7.4f -> pooled %-7.4f | A cert %-6.2f"
          " -> pooled %-6.2f | (mean variant: c_X %-7.4f A %-5.2f ratio %.2f)"
          % (d["point"]["muX"], d["point"]["phi"], d["point"]["ell_X"], d["c_X_certified"],
             d["c_X_pooled_frozen_rule"], d["A_certified"], d["A_pooled_frozen_rule"],
             d["c_X_pooled_mean_variant"], d["A_mean_variant"],
             d["measured_over_certified_mean_variant"]))
print("\nsurvivors under the frozen rule: %d" % len(surv))
print("winner:", best)

# the same rule with the MEAN variant, reported for completeness, NOT used to decide
pooled_mean = {tuple(round(p[k],12) for k in REG.TIE_BREAK):
               min(a["c_X_stats"]["mean"] for a in cal["arms"]
                   if abs(a["point"]["muX"]-p["muX"])<1e-12
                   and abs(a["point"]["phi"]-p["phi"])<1e-12
                   and abs(a["point"]["ell_X"]-p["ell_X"])<1e-12 and a["c_X_stats"])
               for p in pts}
b2, s2 = REG.select(rows, c_X_measured=pooled_mean)
print("survivors if the MEAN were used instead of the median (reported, not decisive): %d" % len(s2))

json.dump({"pooling_declared": "min over calibration seeds of the median over the window",
           "detail": detail, "survivors_frozen_rule": len(surv), "winner": best,
           "survivors_mean_variant": len(s2), "CRIT_MIN": REG.CRIT_MIN, "N_MIN": REG.N_MIN,
           "sequential_rule_fired": "3 no point survives the frozen rule with the measured c_X"
                                    " -> STOP" if best is None else None},
          open("/home/claude/MCM01/out/_selection.json","w"), indent=1, default=str)
