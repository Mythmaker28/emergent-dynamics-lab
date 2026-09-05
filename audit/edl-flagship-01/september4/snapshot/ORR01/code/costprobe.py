import json, time
import guard, lawspec_v2 as V2, observe, protocol as P
out={"note":"timing on n[Y] == 0, where both birth probabilities are identically zero, so no "
            "information about maintenance can be extracted","measurements":[]}
for name, ls in (("v1_additive", V2.LAWSPEC_V1_ADDITIVE), ("v2_exchange", V2.LAWSPEC_V2_EXCHANGE)):
    sp=P.spec_for(); rec=observe.Recorder()
    w=V2.fresh_world(999, sp, lawspec=ls, rng_mode="split_feed_stream", rec=rec)
    w.n["X"][:]=2
    assert int(w.n["Y"].sum())==0
    N=300; t0=time.time()
    with guard.start("cost_probe","cost_probe/"+name,N):
        guard.advance(w,N,per_step=lambda ww: observe.component_report(ww)
                      if ww.step%P.SAMPLE_EVERY==0 else None)
    dt=time.time()-t0
    out["measurements"].append({"lawspec":name,"steps":N,"ms_per_step":1000*dt/N,
                                "N_Y_end":int(w.n["Y"].sum())})
    print("%-12s %.3f ms/step" % (name, 1000*dt/N))
ms=max(m["ms_per_step"] for m in out["measurements"])
tot=(guard.CAPS["confirmation"]+guard.CAPS["control"])*P.HORIZON*ms/1000
out["projection_seconds_worst_case"]=tot
out["ledger"]=guard.audit()
json.dump(out,open("/home/claude/ORR01/out/_costprobe.json","w"),indent=1,default=str)
print("worst case for %d arms x %d steps: %.0f s" % (guard.CAPS["confirmation"]+guard.CAPS["control"], P.HORIZON, tot))
