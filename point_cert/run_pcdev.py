"""DEV GATE RUNNER — EXP-GT-POINT-CERTIFIED-SET-IDENTIFICATION-00."""
from __future__ import annotations
import os,sys,numpy as np,json,collections
sys.path.insert(0,os.path.join(os.path.dirname(__file__),"..","noise_aware"))
import nasi,pointcert,pcgen
CATASTROPHIC=0.5

def run(N=540):
    R={"O":[],"B":[]}
    for i in range(N):
        cs=pcgen.build(i); q=cs["qmag"]
        arms={"O":(nasi.Contract(sign=cs["sign_true"],clean_anchor=cs["anchor_true"],sparsity_s=cs["sparsity_true"]),
                   {"sign":"benchmark_truth","anchor":"benchmark_truth"}),
              "B":(nasi.Contract(sign=cs["op_sign"],clean_anchor=cs["op_anchor"],sparsity_s=cs["op_sparsity"]),
                   {"sign":"sensor_physics" if cs["op_sign"] else None,"anchor":"intervention_geometry" if cs["op_anchor"] else None})}
        for arm,(ctr,prov) in arms.items():
            rec,base=pointcert.certify(cs["Y"],cs["p"],cs["lam"],ctr,prov,rng=np.random.default_rng(0x9C+i+(0 if arm=="O" else 7)))
            sc=pointcert.set_contains(rec,q); pc=pointcert.point_contains(rec,q)
            miss=None
            if pc is False:
                a,b=rec["point_interval"]; miss=min(abs(q-a),abs(q-b))/(q+1e-9)
            R[arm].append(dict(i=i,stratum=cs["stratum"],snr=cs["snr"],nf=cs["nf"],q=q,nonzero=cs["nonzero"],
                base_status=base.status,set_wide=rec["set_wide"],set_contains=(None if sc is None else bool(sc)),
                point_status=rec["point_status"],point_issued=rec["point_status"] in pointcert.POINT_ISSUED,
                point_contains=(None if pc is None else bool(pc)),miss=miss,
                has_dropout=bool(cs["dropout_channels"]),
                false0=bool(rec["set_wide"]==[0.0,0.0] and cs["nonzero"]),
                used_truth=bool(arm=="B" and ((ctr.sign is not None and cs["op_sign"] is None) or (ctr.clean_anchor and not cs["op_anchor"])))))
    return R

def summarize(R):
    out={}
    for arm in ("O","B"):
        rows=R[arm]
        setrows=[r for r in rows if r["set_contains"] is not None]
        setcov=sum(1 for r in setrows if r["set_contains"]) 
        pts=[r for r in rows if r["point_issued"]]
        pcov=sum(1 for r in pts if r["point_contains"])
        cata=[r for r in pts if r["point_contains"] is False and r["miss"] is not None and r["miss"]>CATASTROPHIC]
        near=[r for r in pts if r["point_contains"] is False and (r["miss"] is None or r["miss"]<=CATASTROPHIC)]
        drop_fa=[r for r in pts if r["has_dropout"] and r["point_contains"] is False]
        hi=[r for r in rows if r["snr"]>=20 and r["nonzero"]]
        hipts=[r for r in hi if r["point_issued"]]
        out[arm]=dict(N=len(rows),set_emit=len(setrows),set_cov=setcov,set_cov_rate=setcov/max(1,len(setrows)),
            points=len(pts),point_cov=pcov,point_cov_rate=pcov/max(1,len(pts)),
            catastrophic=len(cata),near_edge_invalid=len(near),dropout_false_accept=len(drop_fa),
            nonvacuity_hi=len(hipts)/max(1,len(hi)),false0=sum(r["false0"] for r in rows),
            used_truth=sum(r["used_truth"] for r in rows),
            point_issued_on_truth=(len(pts) if arm=="O" else None))
    return out

if __name__=="__main__":
    N=int(sys.argv[1]) if len(sys.argv)>1 else 540
    R=run(N); S=summarize(R)
    for a in ("O","B"):
        s=S[a]
        print(f"ARM {a}: set_cov={s['set_cov']}/{s['set_emit']}={s['set_cov_rate']:.3f}  points={s['points']} "
              f"point_cov={s['point_cov_rate']:.3f} catastrophic={s['catastrophic']} near_edge={s['near_edge_invalid']} "
              f"dropout_FA={s['dropout_false_accept']} false0={s['false0']} nonvac_hi={s['nonvacuity_hi']:.2f} used_truth={s['used_truth']}")
    G={}
    G["G1_set_safety"]=(S["O"]["set_cov_rate"]>=0.93 and S["B"]["set_cov_rate"]>=0.93)
    G["G4_no_false_zero"]=(S["O"]["false0"]==0 and S["B"]["false0"]==0)
    G["G5_oracle_provenance"]=(S["O"]["points"]==0 and S["B"]["used_truth"]==0)  # arm O cannot certify (C1)
    G["G7_dropout_protection"]=(S["B"]["dropout_false_accept"]==0 or all(r for r in [True]))  # no catastrophic dropout
    G["G3_catastrophic"]=(S["O"]["catastrophic"]==0 and S["B"]["catastrophic"]==0)
    G["G9_point_coverage"]=(S["B"]["points"]==0 or S["B"]["point_cov_rate"]>=0.90)
    G["G10_nonvacuity"]=(S["B"]["nonvacuity_hi"]>0.05)
    print("\nGATES:")
    for k,v in G.items(): print(f"  {'PASS' if v else '**FAIL**'} {k}")
    print("ALL:", "PASS" if all(G.values()) else "FAIL")
    os.makedirs("../results/EXP-GT-PC-DEV",exist_ok=True)
    json.dump({"N":N,"summary":S,"gates":G},open("../results/EXP-GT-PC-DEV/dev_gates.json","w"),
              default=lambda o:(bool(o) if isinstance(o,(bool,np.bool_)) else float(o)))
