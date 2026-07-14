"""Large hold-out runner. Instrument is frozen + hash-gated; this harness only feeds it and scores.
NOTE: an earlier version of THIS HARNESS passed a_i where the instrument expects lam_i = g0/g_i = 1/a_i,
which produced spurious invalid sets. The bug was in the harness, not the instrument (signsafe.py unchanged,
hash-gated). Documented in docs/consolidation/HOLDOUT_HARNESS_ERRATUM.md."""
import numpy as np, json, hashlib, pathlib, collections
import holdout_gen as G, signsafe as SS
man=json.load(open('docs/consolidation/SIGNSAFE_FREEZE_MANIFEST.json'))
for f,h in man['files'].items():
    assert hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()==h, "HASH GATE "+f
print("HASH GATE: frozen instrument verified. N=%d, two arms.\n"%G.N_CASES)

def score(st, iset, qm):
    """None = no set emitted (refusal). True/False = emitted set contains / excludes truth."""
    if st in (SS.NONID, SS.ILL): return None
    if st == SS.POINT:
        if iset[0] == 0.0 and qm > 1e-9: return False     # null-response claim against a real response
        return abs(iset[0]-qm) <= 0.12*qm + 1e-9
    if st == SS.INTERVAL: return iset[0]*0.9 <= qm <= iset[1]*1.1
    if st == SS.LOWER:    return iset[0] <= qm*1.06
    if st == SS.UPPER:    return iset[1] >= qm*0.94
    return None

rows={'oracle':[], 'blind':[]}
for i in range(G.N_CASES):
    v, base, prof, tp, q, anch, sign, strat, snr, m = G.build(i)
    lam = 1.0/np.where(np.abs(base) > 1e-9, base, 1e-9)   # lam_i = g0/g_i = 1/a_i  (gy = 1)
    qm  = abs(q)*float(np.std(prof[tp:]))
    for arm,(a,s) in (('oracle',(anch,sign)), ('blind',(False,None))):
        st, iset, rep = SS.identify(v, lam, tp, 120, clean_anchor=a, sign=s)
        sc = score(st, iset, qm)
        w = None
        if iset is not None and np.isfinite(iset[1]) and qm > 0: w = float(iset[1]-iset[0])/qm
        rows[arm].append({'i':i,'stratum':strat,'m':int(m),'snr':float(snr),'status':st,
                          'emitted': sc is not None, 'valid': sc, 'width': w})

print("%-8s %6s %9s %9s %8s %8s"%("arm","N","emitted","INVALID","points","refused"))
summary={}
for arm in ('oracle','blind'):
    R=rows[arm]; emit=[r for r in R if r['emitted']]
    inv=[r for r in emit if r['valid'] is False]
    pts=[r for r in emit if r['status']==SS.POINT]
    ref=len(R)-len(emit)
    summary[arm]={'N':len(R),'emitted':len(emit),'invalid':len(inv),'points':len(pts),'refused':ref}
    print("%-8s %6d %9d %9d %8d %8d"%(arm,len(R),len(emit),len(inv),len(pts),ref))
    if inv[:3]:
        for r in inv[:3]: print("     example invalid:",r)
print()
for arm in ('oracle','blind'):
    e=summary[arm]['emitted']; inv=summary[arm]['invalid']
    if inv==0 and e>0:
        ub=1-(0.05)**(1.0/e)
        print("  %-6s invalid=0/%d  exact one-sided 95%% upper bound on invalid rate = %.5f (%.3f%%)"%(arm,e,ub,100*ub))
    else:
        print("  %-6s invalid=%d/%d  RATE=%.3f"%(arm,inv,e,inv/max(e,1)))
print("\nWorst-family (ORACLE arm): invalid by stratum")
bys=collections.defaultdict(lambda:[0,0])
for r in rows['oracle']:
    if r['emitted']:
        bys[r['stratum']][1]+=1
        if r['valid'] is False: bys[r['stratum']][0]+=1
for k in sorted(bys): print("   %-18s invalid %d / emitted %d"%(k,bys[k][0],bys[k][1]))
json.dump({'summary':summary,'rows':rows}, open('consolidation/HOLDOUT_RESULTS.json','w'), default=lambda o: bool(o) if isinstance(o,(bool,np.bool_)) else float(o))
print("\nraw -> consolidation/HOLDOUT_RESULTS.json")
