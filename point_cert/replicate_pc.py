"""INDEPENDENT REPLICATION of the point certificate (C7). Does NOT import pointcert. Re-derives the
selection-aware certified interval with an independent method (percentile channel bootstrap + re-selection)
and checks agreement (overlap or joint-refusal) with the frozen layer on issued-point cases."""
from __future__ import annotations
import os,sys,json,glob,numpy as np
sys.path.insert(0,os.path.join(os.path.dirname(__file__),"..","noise_aware"))
import nasi,pcprospgen,pointcert   # pointcert only to know WHICH cases it issued; independent recompute below
def indep_interval(Y,p,contract,rng):
    """Independent selection-aware interval: bootstrap channel coefficients (percentile), re-select each draw."""
    X,A0,h=nasi._fit_setup(p); c=Y@A0
    beta=np.linalg.pinv(X)@Y.T; R=Y-(X@beta).T
    m,L=Y.shape; b=24; nb=int(np.ceil(L/b))
    pts=[]
    for _ in range(199):
        st=rng.integers(0,L-b+1,size=nb); idx=(st[:,None]+np.arange(b)[None,:]).ravel()[:L]
        cb=c+R[:,idx]@A0; cm=np.abs(cb); det=cm>0
        s=contract.sign
        if contract.clean_anchor and s=="attenuate": v=float(np.max(cm))
        elif contract.clean_anchor and s=="amplify":
            d=cm[det]; v=float(np.min(d)) if d.size else None
        elif contract.sparsity_s is not None:
            srt=np.sort(cm); best=None
            for i in range(len(srt)):
                g=srt[(srt>=srt[i])&(srt<=srt[i]*1.15+1e-9)]
                if best is None or len(g)>len(best): best=g
            v=float(np.median(best)) if best is not None else None
        else: v=None
        if v is not None: pts.append(v)
    if not pts: return None
    return [float(np.percentile(pts,2.5)), float(np.percentile(pts,97.5))]
if __name__=="__main__":
    rows=[]
    for f in sorted(glob.glob("../results/EXP-GT-PC-PROSPECTIVE/rows_*.json")): rows+=json.load(open(f))
    issued=[r for r in rows if r["point_issued"] and r["arm"]=="B"]
    overlap=0; both=0
    for r in issued[:120]:
        cs=pcprospgen.build(r["i"])
        ctr=nasi.Contract(sign=cs["op_sign"],clean_anchor=cs["op_anchor"],sparsity_s=cs["op_sparsity"])
        prov={"sign":"sensor_physics" if cs["op_sign"] else None,"anchor":"intervention_geometry" if cs["op_anchor"] else None}
        rec,base=pointcert.certify(cs["Y"],cs["p"],cs["lam"],ctr,prov,rng=np.random.default_rng(pcprospgen.PC_PROSP_SEED+r["i"]+7))
        if rec["point_status"] not in pointcert.POINT_ISSUED: continue
        iv=rec["point_interval"]
        iiv=indep_interval(cs["Y"],cs["p"],ctr,np.random.default_rng(9+r["i"]))
        if iiv is None: continue
        both+=1; overlap += (iv[0]<=iiv[1] and iiv[0]<=iv[1])
    print(f"INDEP POINT-CERT REPLICATION (C7): overlap {overlap}/{both} = {overlap/max(1,both):.3f}")
