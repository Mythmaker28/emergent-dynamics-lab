"""FIMRCC01 §4 — raw daughter-interval event counts after t_m, for the pre-registered candidates
E3 and E4. Runs only on the worlds that received a removal. No new definition: the interval is the
one Precondition A located, and the counts are the interval's own ledger entries after t_m."""
import sys, os, json, builtins, time
BASE=sys.argv[1]; RAW=sys.argv[2]; OUTP=sys.argv[3]
for _d in (os.path.join(BASE,"TLMR01","code"),os.path.join(BASE,"FIMRCC01","code"),BASE):
    if os.path.isdir(_d): sys.path.insert(0,_d)
_open=builtins.open
def _shim(p,*a,**k):
    if isinstance(p,str) and p.startswith("/home/claude/edl/"):
        p=os.path.join(BASE,p[len("/home/claude/edl/"):])
    return _open(p,*a,**k)
builtins.open=_shim
try: import tlmr01_offline as OFF
finally: builtins.open=_open
import fimrcc01_precondition_a as PA

out=[]; t0=time.time()
for f in sorted(os.listdir(RAW)):
    if not (f.startswith("TLMR01_LAW_C_MCTT01_") and f.endswith(".npz")): continue
    A=OFF.Archive(os.path.join(RAW,f))
    iv=A.meta.get("intervention",{})
    if not iv.get("applied"): continue
    tm=int(iv["step"])
    ev,trace=PA.id_trace(A)
    loc=PA.localise(A,tm,iv.get("daughter_cells_after") or [])
    row={"tag":A.meta["tag"],"seed":A.meta["seed"],"t_m":tm,"UNIQUE_EXACT":loc["UNIQUE_EXACT"]}
    if loc["UNIQUE_EXACT"]:
        j=loc["exact_matches"][0]; did=trace[tm][j]; e=ev[did]
        yb=[t for t in e["ybirth"] if t>tm]; yd=[t for t in e["ydeath"] if t>tm]
        xb=[t for t in e["xbirth"] if t>tm]
        row.update({"interval_id":did,"interval_start":e["start"],"interval_end":e["end"],
                    "steps_after_tm":e["end"]-tm,"minNY_over_interval":e["minNY"],
                    "y_births_after_tm":len(yb),"y_deaths_after_tm":len(yd),
                    "x_births_after_tm":len(xb),
                    "E2_COMPLETE":bool(yb and yd and e["minNY"]>=1)})
        if row["E2_COMPLETE"]:
            fd=min(yd)
            pre=sum(1 for t in xb if t<fd); post=sum(1 for t in xb if t>fd)
            row.update({"first_y_death_after_tm":fd,"x_before_first_death":pre,
                        "x_after_first_death":post,"post_duration":e["end"]-fd,
                        "E1_FUNCTIONAL":bool(pre>0 and post>0 and (e["end"]-fd)>0)})
        else:
            row["E1_FUNCTIONAL"]=False
    # E0 / E5 on the same archive
    Dall=OFF.turnover_in(ev,tm)
    row["E5_n_complete_anywhere"]=len(Dall)
    row["E0_FUNCTIONAL_anywhere"]=any(d["FUNCTIONAL"] for d in Dall)
    out.append(row)
with _open(OUTP,"w") as fh: json.dump(out,fh,indent=1)
print("worlds=%d %.0fs"%(len(out),time.time()-t0))
