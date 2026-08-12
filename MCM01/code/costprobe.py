"""Cost estimate on the REAL engine, on the provably non-scientific manifold n[Y] == 0.

With no organiser anywhere, `pair = nX*nY == 0`, so both birth probabilities are identically
zero and no body molecule and no organiser can ever be created (audit A4). The X, Y dynamics
are therefore exactly null and no information about cloud maintenance can be extracted. The
resource, waste and diffusion code paths all run at realistic occupancy, so the per-step cost is
representative. Declared and counted as its own start class.
"""
import json, time
import numpy as np
import guard, mcm, region as REG, protocol as P

rows = REG.grid()
best, cand = REG.select(rows)
out = {"note": __doc__.strip(), "measurements": []}
for L in (best["L"], 52):
    sp = P.spec_for(best, **{"L": L})
    rec = mcm.Recorder()
    w = mcm.fresh_world(999, sp, rec=rec)
    w.n["X"][:] = 2                                    # realistic occupancy, no organiser
    assert int(w.n["Y"].sum()) == 0
    N = 400
    t0 = time.time()
    with guard.start("cost_probe", "cost_probe/L%d" % L, N):
        guard.advance(w, N, per_step=lambda ww: mcm.component_report(ww)
                      if ww.step % P.SAMPLE_EVERY == 0 else None)
    dt = time.time() - t0
    out["measurements"].append({"L": L, "steps": N, "seconds": dt, "ms_per_step": 1000 * dt / N,
                                "N_X_end": int(w.n["X"].sum()), "N_Y_end": int(w.n["Y"].sum())})
    print("L=%d  %.3f ms/step  (N_X %d -> %d, N_Y = %d)"
          % (L, 1000 * dt / N, 2 * L * L, int(w.n["X"].sum()), int(w.n["Y"].sum())))

ms = out["measurements"][0]["ms_per_step"]
th = P.thresholds_for(best)
plan = {"per_confirmation_arm_steps": th["T_FORM_MAX"] + th["T_MAINT"],
        "per_calibration_arm_steps": th["T_FORM_MAX"] + th["T_CAL"]}
plan["calibration_seconds"] = guard.CAPS["calibration"] * plan["per_calibration_arm_steps"] * ms / 1000
plan["confirmation_seconds"] = guard.CAPS["confirmation"] * plan["per_confirmation_arm_steps"] * ms / 1000
plan["control_seconds"] = guard.CAPS["control"] * plan["per_confirmation_arm_steps"] * ms / 1000
plan["total_seconds_worst_case"] = (plan["calibration_seconds"] + plan["confirmation_seconds"]
                                    + plan["control_seconds"])
out["projection"] = plan
out["ledger"] = guard.audit()
json.dump(out, open("/home/claude/MCM01/out/_costprobe.json", "w"), indent=1, default=str)
print("\nprojection (worst case, every start of every class used):")
print(json.dumps({k: (round(v, 1) if isinstance(v, float) else v) for k, v in plan.items()}, indent=1))
