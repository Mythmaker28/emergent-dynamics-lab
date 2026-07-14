import os,sys,json,hashlib,numpy as np
sys.path.insert(0,os.path.join(os.path.dirname(__file__),"..","noise_aware"))
import nasi,pointcert,pcgen,pcprospgen,pcregressions
def canon():
    o={}; o["const"]=[pointcert.EPS_Q_REL,pointcert.SNR_FLOOR,pointcert.LORO_TOL,pointcert.FOLD_TOL,pointcert.DROP_R2,pointcert.POINT_INFLATE]
    r=pcregressions.run(verbose=False); o["reg"]=[r["catastrophic_refused"],r["catastrophic_invalid"],r["issued"]]
    cat=fz=pts=setok=0
    for i in range(200):
        cs=pcprospgen.build(i); q=cs["qmag"]
        ctr=nasi.Contract(sign=cs["op_sign"],clean_anchor=cs["op_anchor"],sparsity_s=cs["op_sparsity"])
        rec,base=pointcert.certify(cs["Y"],cs["p"],cs["lam"],ctr,{"sign":"sensor_physics" if cs["op_sign"] else None},rng=np.random.default_rng(pcprospgen.PC_PROSP_SEED+i+7))
        if rec["point_status"] in pointcert.POINT_ISSUED:
            pts+=1
            if pointcert.point_contains(rec,q) is False and rec["point_interval"]:
                a,b=rec["point_interval"]; cat+= (min(abs(q-a),abs(q-b))/(q+1e-9)>0.5)
        if rec["set_wide"]==[0.0,0.0] and cs["nonzero"]: fz+=1
        setok+=(pointcert.set_contains(rec,q) is True)
    o["prosp200"]=[pts,cat,fz,setok]; return o
if __name__=="__main__":
    o=canon(); h=hashlib.sha256(json.dumps(o,sort_keys=True).encode()).hexdigest()
    print(json.dumps(o)); print("PC_CANON_SHA256",h)
