"""FMRT01 — the paired common-seed runner.

DESIGN. One trajectory per seed block is evolved under the exact frozen B1 law. At the frozen
trigger boundary it is FORKED into three arms by deep copy, so the three arms are bit-identical
immediately before the intervention BY CONSTRUCTION, and that identity is still verified.

    A  SELECTIVE_PARENT_OFF   selective_y_off(parent mask)
    B  SHAM                   selective_y_off(empty mask) — identical branch and audit record
    C  GLOBAL_ORGANISER_OFF   selective_y_off(all-true mask) — proven state-identical to the
                              historical organiser_off_at path by a frozen fixture

POST-INTERVENTION WINDOW. Exactly T_HOLD steps, with NO early stop. Extinction and third-centre
events are RECORDED AS OUTCOMES, not used as stops, because arm C removes all Y by design and
must still be observed decaying. This is frozen here, before any world exists.

FIREWALL. The live channel and ledger carry only an opaque block token, arm completion, a
predeclared technical-failure flag and a checksum flag.
"""
from __future__ import annotations
import copy, hashlib, json, os, sys
import numpy as np
REPO="/home/claude/edl"; OUT=f"{REPO}/FMRT01/out"; RAW="/home/claude/FMRT01/raw"
for _p in (f"{REPO}/FMRT01/code", f"{REPO}/PQEC01/code", "/home/claude/ORR01/code", "/home/claude/OBTC02/code"):
    if _p not in sys.path: sys.path.insert(0,_p)
import pqec01_observer as O
import fmrt01_engine as FE
O.PQECWorld = FE.FMRTWorld
import pqec01_run as PR
import fmrt01_identity as ID
import fmrt01_endpoint as EP

FREEZE=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))
B1=FREEZE["PHASE_B"]["POINT_B1"]
C=FREEZE["INHERITED_FROZEN_CONSTANTS"]; N_STAR=int(C["N_STAR"])
ARMS=("SELECTIVE","SHAM","GLOBAL")

def phys_hash(w):
    h=hashlib.sha256()
    for s in O.SPECIES: h.update(np.ascontiguousarray(w.n[s]).tobytes())
    return h.hexdigest()

def xplane(w): return w.n["X"].astype(np.int64)

def centres_now(w):
    ys,xs=np.nonzero(w.n["Y"]); cells=list(zip(ys.tolist(),xs.tolist()))
    return cells, ID.components(cells)

def run_block(job):
    idx,seed=job
    tag="M_B1_b%03d_s%d"%(idx,seed)
    rec={"block":idx,"seed":seed,"tag":tag}
    try:
        w,_,sp=O.build_world(seed,B1["kY"],B1["muY"],L=None,horizon=EP.TOTAL_HORIZON,instrumented=True)
        w.fmrt_init()
        tw=EP.TriggerWatcher(); prev_cells=[]; last_one_centre=[]
        t_m=None; parent_comp=None; daughter_comp=None; cells_tm=None; id_level=None
        stop="HORIZON"; integ=True
        for t in range(EP.TOTAL_HORIZON):
            w._one_step()
            free=sp.CAP-sum(w.n[s] for s in O.SPECIES)
            if free.min()<0 or max(w.n[s].max() for s in O.SPECIES)>sp.CAP:
                integ=False; stop="INTEGRITY_FAILURE"; break
            cells,comps=centres_now(w)
            NY=int(w.n["Y"].sum()); ncen=len(comps)
            st=EP.state_of(NY,ncen,integ)
            if ncen==1: last_one_centre=list(cells)
            cand=tw.observe(t,st)
            if cand and t<=EP.LATEST_ALLOWED_TRIGGER and len(comps)==2:
                vals=EP.local_x_masses(xplane(w),cells,comps)
                if EP.f5_ratio(vals)>=EP.F_PRIMARY:
                    p,d,lvl=ID.parent_daughter(last_one_centre,cells)
                    if p is not None:
                        tw.fired=True; t_m=t; parent_comp,daughter_comp,id_level=p,d,lvl
                        cells_tm=list(cells); break
            if NY==0: stop="EXTINCT"; break
            if ncen>=3: stop="PREMATURE_THIRD_CENTRE"; break
            if NY>N_STAR: stop="MAX_PERMITTED_Y"; break
            prev_cells=cells
        rec.update({"triggered":t_m is not None,"t_m":t_m,"phase1_stop":stop,
                    "integrity_ok":bool(integ),"identity_level":id_level})
        if t_m is None:
            rec["technical_failure"]=False
            np.savez_compressed(os.path.join(RAW,tag+"_NOTRIG.npz"),
                meta=np.array([json.dumps(rec)]))
            return rec
        # ---- provenance and pre-intervention record at t_m ----
        snap_tm=FE.tracker_snapshot(w)
        NX_world=int(w.n["X"].sum())
        pmask=ID.mask_for(cells_tm,parent_comp); dmask=ID.mask_for(cells_tm,daughter_comp)
        dcen=ID.centroid(cells_tm,daughter_comp); pcen=ID.centroid(cells_tm,parent_comp)
        vals=EP.local_x_masses(xplane(w),cells_tm,[parent_comp,daughter_comp])
        pre_hash=phys_hash(w); pre_rng=FE.rng_fingerprint(w)
        rec.update({"NX_world_at_intervention":NX_world,"parent_mass_tm":vals[0],
                    "daughter_mass_tm":vals[1],"pre_intervention_state_hash":pre_hash,
                    "pre_intervention_rng":pre_rng,
                    "daughter_centroid":[round(v,4) for v in dcen],
                    "parent_centroid":[round(v,4) for v in pcen]})
        # ---- fork ----
        arms={}
        for a in ARMS:
            wa=copy.deepcopy(w)
            arms[a]={"w":wa,"pre_hash":phys_hash(wa),"pre_rng":FE.rng_fingerprint(wa)}
        rec["fork_identity_ok"]=bool(all(arms[a]["pre_hash"]==pre_hash and arms[a]["pre_rng"]==pre_rng for a in ARMS))
        allmask=np.ones_like(w.n["Y"],dtype=bool)
        arms["SELECTIVE"]["removed"]=arms["SELECTIVE"]["w"].selective_y_off(pmask)
        arms["SHAM"]["removed"]=arms["SHAM"]["w"].selective_y_off(np.zeros_like(allmask))
        arms["GLOBAL"]["removed"]=arms["GLOBAL"]["w"].selective_y_off(allmask)
        # ---- post-intervention window: fixed T_HOLD steps, no early stop ----
        out={}
        for a in ARMS:
            wa=arms[a]["w"]; series=[]; thirdP=False; integ2=True
            for k in range(EP.T_HOLD):
                wa._one_step()
                free=sp.CAP-sum(wa.n[s] for s in O.SPECIES)
                if free.min()<0 or max(wa.n[s].max() for s in O.SPECIES)>sp.CAP: integ2=False
                cells2,comps2=centres_now(wa)
                if len(comps2)>=3: thirdP=True
                series.append((int(wa.n["Y"].sum()),int(wa.n["X"].sum()),len(comps2)))
            cells2,comps2=centres_now(wa)
            dmass=None; dexists=False; post_born=0
            if comps2:
                best=min(range(len(comps2)),key=lambda j: ID.tdist(ID.centroid(cells2,comps2[j]),dcen))
                if ID.tdist(ID.centroid(cells2,comps2[best]),dcen)<=3*ID.CORE_R:
                    dexists=True
                    dmass=float(xplane(wa)[ID.disc_mask(*[int(round(v))%ID.L for v in ID.centroid(cells2,comps2[best])])].sum())
                    sn=FE.tracker_snapshot(wa)
                    cy,cx=ID.centroid(cells2,comps2[best])
                    dm=ID.disc_mask(int(round(cy))%ID.L,int(round(cx))%ID.L)
                    inside=dm[sn["y"],sn["x"]]
                    post_born=int((inside & (sn["birth_step"]>t_m)).sum())
            su=EP.survivor_upper(NX_world)
            out[a]={"removed":arms[a]["removed"],"daughter_exists":dexists,
                    "daughter_mass_post":dmass,"survivor_upper_95":su,
                    "criterion_D":bool(dmass is not None and dmass>su),
                    "criterion_E_post_intervention_births_in_daughter":post_born,
                    "third_centre_in_window":thirdP,"integrity_ok_post":bool(integ2),
                    "final_NY":series[-1][0],"final_NX":series[-1][1],
                    "NX_series_every_25":[series[i][1] for i in range(0,EP.T_HOLD,25)],
                    "NY_series_every_25":[series[i][0] for i in range(0,EP.T_HOLD,25)]}
            out[a]["R2_PASS"]=bool(dexists and out[a]["criterion_D"] and post_born>0
                                   and integ2 and not thirdP)
        rec["ARMS"]=out
        rec["technical_failure"]=not rec["fork_identity_ok"]
        np.savez_compressed(os.path.join(RAW,tag+".npz"),
            meta=np.array([json.dumps(rec)]),
            tm_id=snap_tm["id"],tm_y=snap_tm["y"],tm_x=snap_tm["x"],
            tm_birth_step=snap_tm["birth_step"],tm_birth_y=snap_tm["birth_y"],tm_birth_x=snap_tm["birth_x"],
            cells_tm=np.array(cells_tm,np.int32),
            parent_comp=np.array(parent_comp,np.int32),daughter_comp=np.array(daughter_comp,np.int32))
        return rec
    except Exception:
        import traceback
        rec.update({"technical_failure":True,"ERROR":traceback.format_exc()[-500:]})
        return rec

def token(i): return hashlib.sha256(("FMRT01|block|%d"%i).encode()).hexdigest()[:16]

def main():
    os.makedirs(RAW,exist_ok=True)
    SB=json.load(open(f"{OUT}/FMRT01_SEED_BLOCK_MANIFEST.json"))["BLOCKS"]
    jobs=[(b["index"],b["seed"]) for b in SB]
    import multiprocessing as mp
    led=open(f"{OUT}/FMRT01_RUN_LEDGER.jsonl","a")
    seal=open("/home/claude/FMRT01/sealed.jsonl","a")
    done=0
    with mp.Pool(2) as pool:
        for rec in pool.imap_unordered(run_block,jobs):
            done+=1
            pub={"block_token":token(rec["block"]),"completed":"ERROR" not in rec,
                 "technical_failure":bool(rec.get("technical_failure")),
                 "checksum_written":os.path.exists(os.path.join(RAW,rec["tag"]+".npz")) or
                                     os.path.exists(os.path.join(RAW,rec["tag"]+"_NOTRIG.npz"))}
            led.write(json.dumps(pub)+"\n"); led.flush()
            seal.write(json.dumps(rec,default=str)+"\n"); seal.flush()
            print("  [%3d/%3d] block=%s completed=%s technical_failure=%s checksum=%s"%(
                done,len(jobs),pub["block_token"],pub["completed"],pub["technical_failure"],
                pub["checksum_written"]),flush=True)
    led.close(); seal.close()
    print("blocks attempted: %d"%len(jobs))

if __name__=="__main__": main()
