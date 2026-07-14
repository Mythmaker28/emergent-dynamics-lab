"""HISTORICAL REGRESSIONS for the point layer (deliverable 7). The 57 burned NASI point failures replayed
through the certification layer. Required: the 2 catastrophic cases refused; ZERO catastrophic invalid
certificates; near-edge misses count in coverage but are not catastrophic. Dev use only."""
from __future__ import annotations
import os,sys,json,numpy as np,collections
sys.path.insert(0,os.path.join(os.path.dirname(__file__),"..","noise_aware"))
import nasi,prospgen,pointcert
CATA=0.5
def run(verbose=True):
    foren=json.load(open(os.path.join(os.path.dirname(__file__),"..","results","EXP-GT-NASI-PROSPECTIVE","invalid_point_forensics.json")))
    issued=catref=cat=cata_inv=near_inv=setok=0; reasons=collections.Counter()
    for r in foren["points"]:
        cs=prospgen.build(r["i"]); q=cs["qmag"]
        if r["arm"]=="O": ctr=nasi.Contract(sign=cs["sign_true"],clean_anchor=cs["anchor_true"],sparsity_s=cs["sparsity_true"]); prov={"sign":"benchmark_truth"}
        else: ctr=nasi.Contract(sign=cs["op_sign"],clean_anchor=cs["op_anchor"],sparsity_s=cs["op_sparsity"]); prov={"sign":"sensor_physics" if cs["op_sign"] else None,"anchor":"intervention_geometry" if cs["op_anchor"] else None}
        rec,base=pointcert.certify(cs["Y"],cs["p"],cs["lam"],ctr,prov,rng=np.random.default_rng(500+r["i"]))
        setok+=(pointcert.set_contains(rec,q) is True)
        if rec["point_status"] in pointcert.POINT_ISSUED:
            issued+=1; pc=pointcert.point_contains(rec,q)
            if pc is False:
                a,b=rec["point_interval"]; miss=min(abs(q-a),abs(q-b))/(q+1e-9)
                if miss>CATA: cata_inv+=1
                else: near_inv+=1
        else: reasons[rec["point_status"]]+=1
        if r["catastrophic"]: cat+=1; catref+=(rec["point_status"] not in pointcert.POINT_ISSUED)
    res=dict(n=len(foren["points"]),issued=issued,catastrophic_refused=catref,catastrophic_total=cat,
             catastrophic_invalid=cata_inv,near_edge_invalid=near_inv,set_contains=setok,reasons=dict(reasons))
    if verbose: print(json.dumps(res,indent=1))
    ok=(catref==cat) and (cata_inv==0)
    if verbose: print("REGRESSION VERDICT:", "PASS" if ok else "**FAIL**",
                      "(2 catastrophic refused, 0 catastrophic invalid certificates)")
    res["pass"]=ok; return res
if __name__=="__main__": run(True)
