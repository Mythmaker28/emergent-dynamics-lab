"""HASH-GATED PROSPECTIVE RUNNER (chunk) — EXP-GT-PC-00. Usage: run_pcprosp.py START END"""
from __future__ import annotations
import os,sys,json,hashlib,numpy as np
sys.path.insert(0,os.path.join(os.path.dirname(__file__),"..","noise_aware"))
import nasi,pointcert,pcprospgen
FREEZE=os.path.join(os.path.dirname(__file__),"..","docs","point_cert","POINT_CERT_FREEZE_MANIFEST.json")
CATA=0.5
def hash_gate():
    m=json.load(open(FREEZE))
    for f,h in m["frozen_files"].items():
        got=hashlib.sha256(open(os.path.join(os.path.dirname(__file__),"..",f),"rb").read()).hexdigest()
        assert got==h, f"HASH GATE FAIL {f}"
    assert hashlib.sha256(open(os.path.join(os.path.dirname(__file__),"..","noise_aware","nasi.py"),"rb").read()).hexdigest()==m["nasi_dependency_hash"], "NASI changed!"
    return m
def run(a,b):
    hash_gate(); rows=[]
    for i in range(a,b):
        cs=pcprospgen.build(i); q=cs["qmag"]
        for arm,(ctr,prov) in (("O",(nasi.Contract(sign=cs["sign_true"],clean_anchor=cs["anchor_true"],sparsity_s=cs["sparsity_true"]),{"sign":"benchmark_truth","anchor":"benchmark_truth"})),
                               ("B",(nasi.Contract(sign=cs["op_sign"],clean_anchor=cs["op_anchor"],sparsity_s=cs["op_sparsity"]),{"sign":"sensor_physics" if cs["op_sign"] else None,"anchor":"intervention_geometry" if cs["op_anchor"] else None}))):
            rec,base=pointcert.certify(cs["Y"],cs["p"],cs["lam"],ctr,prov,rng=np.random.default_rng(pcprospgen.PC_PROSP_SEED+i+(0 if arm=="O" else 7)))
            sc=pointcert.set_contains(rec,q); pc=pointcert.point_contains(rec,q); miss=None
            if pc is False:
                x,y=rec["point_interval"]; miss=float(min(abs(q-x),abs(q-y))/(q+1e-9))
            rows.append(dict(i=i,arm=arm,stratum=cs["stratum"],snr=round(float(cs["snr"]),3),nf=cs["nf"],m=int(cs["m"]),
                q=float(q),nonzero=bool(cs["nonzero"]),is_dropsparse=bool(cs["is_dropsparse"]),has_dropout=bool(cs["dropout_channels"]),
                base_status=base.status,set_contains=(None if sc is None else bool(sc)),
                point_status=rec["point_status"],point_issued=rec["point_status"] in pointcert.POINT_ISSUED,
                point_contains=(None if pc is None else bool(pc)),miss=miss,
                catastrophic=bool(miss is not None and miss>CATA),
                false0=bool(rec["set_wide"]==[0.0,0.0] and cs["nonzero"]),
                used_truth=bool(arm=="B" and ((ctr.sign is not None and cs["op_sign"] is None) or (ctr.clean_anchor and not cs["op_anchor"])))))
    return rows
if __name__=="__main__":
    a,b=int(sys.argv[1]),int(sys.argv[2]); rows=run(a,b)
    os.makedirs("../results/EXP-GT-PC-PROSPECTIVE",exist_ok=True)
    out=f"../results/EXP-GT-PC-PROSPECTIVE/rows_{a}_{b}.json"; json.dump(rows,open(out,"w"))
    cat=sum(r["catastrophic"] for r in rows); f0=sum(r["false0"] and r["nonzero"] for r in rows); pts=sum(r["point_issued"] for r in rows)
    print(f"chunk [{a},{b}) rows={len(rows)} points={pts} CATASTROPHIC={cat} false0={f0} -> {out}")
