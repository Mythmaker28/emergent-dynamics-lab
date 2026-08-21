"""MRFA01 §5 — TECHNICAL PROVENANCE RECONSTRUCTION, not a new experiment.

WHY THIS EXISTS. FMRT01's raw archives store, per arm, only WORLD-level X and Y totals sampled
every 25 steps plus endpoint scalars. They do NOT store any daughter-LOCAL trajectory, and they
store the GLOBAL arm's daughter-local mass as null because that code path required a surviving Y
component to locate the disc. §5 of MRFA01 requires a daughter-centred local response per step in
all three arms under identical geometry. That object does not exist in the bytes.

WHAT THIS IS. A bit-exact deterministic replay of the 22 ALREADY EXECUTED frozen seeds. It adds
observation only: every recorded quantity is a pure read of w.n["X"] or of the inert tracker, and
no code path consumes a single random number that the original run did not consume. The replay is
accepted only if it reproduces, exactly:
    pre_intervention_state_hash, pre_intervention_rng, t_m, phase1_stop, identity_level,
    NX_world_at_intervention, parent_mass_tm, daughter_mass_tm, and for all three arms
    removed, final_NY, final_NX, NX_series_every_25, NY_series_every_25, daughter_mass_post,
    criterion_E, third_centre_in_window, integrity_ok_post.
Any mismatch is a hard failure of the reconstruction, not something to be tolerated.

STATUS OF EVERY NUMBER IT PRODUCES: TECHNICAL_PROVENANCE_RECONSTRUCTION.
NEW_SEEDS = 0. NEW_WORLDS = 0. NEW_TRAJECTORIES = 0. NEW_SCIENTIFIC_RUNS = 0.
No replayed quantity may enter a denominator, a confidence interval, a success rate, or any
claim about FMRT01's frozen primary result.
"""
from __future__ import annotations
import copy, hashlib, json, os, sys
import numpy as np
REPO="/home/claude/edl"; RAW=f"{REPO}/FMRT01/raw"; OUT=f"{REPO}/MRFA01/out"
REPLAY=f"{REPO}/MRFA01/replay"
for _p in (f"{REPO}/FMRT01/code", f"{REPO}/PQEC01/code", "/home/claude/ORR01/code", "/home/claude/OBTC02/code"):
    if _p not in sys.path: sys.path.insert(0,_p)
import pqec01_observer as O
import fmrt01_engine as FE
O.PQECWorld = FE.FMRTWorld
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

def replay_block(idx,seed,ref):
    tag="M_B1_b%03d_s%d"%(idx,seed)
    w,_,sp=O.build_world(seed,B1["kY"],B1["muY"],L=None,horizon=EP.TOTAL_HORIZON,instrumented=True)
    w.fmrt_init()
    tw=EP.TriggerWatcher(); last_one_centre=[]
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
    assert t_m is not None, tag
    NX_world=int(w.n["X"].sum())
    dcen=ID.centroid(cells_tm,daughter_comp); pcen=ID.centroid(cells_tm,parent_comp)
    vals=EP.local_x_masses(xplane(w),cells_tm,[parent_comp,daughter_comp])
    pre_hash=phys_hash(w); pre_rng=FE.rng_fingerprint(w)
    # FIXED geometry, tied to the t_m centres and never moved again
    DFIX=ID.disc_mask(int(round(dcen[0]))%ID.L,int(round(dcen[1]))%ID.L)
    PFIX=ID.disc_mask(int(round(pcen[0]))%ID.L,int(round(pcen[1]))%ID.L)
    chk={"t_m":t_m,"phase1_stop":stop,"identity_level":id_level,
         "NX_world_at_intervention":NX_world,"parent_mass_tm":vals[0],"daughter_mass_tm":vals[1],
         "pre_intervention_state_hash":pre_hash,"pre_intervention_rng":pre_rng}
    # ---- fork: the three pre-intervention hashes, RECOMPUTED, one per arm ----
    arms={}; three_hashes={}; three_rng={}
    for a in ARMS:
        wa=copy.deepcopy(w)
        three_hashes[a]=phys_hash(wa); three_rng[a]=FE.rng_fingerprint(wa)
        arms[a]={"w":wa}
    allmask=np.ones_like(w.n["Y"],dtype=bool)
    pmask=ID.mask_for(cells_tm,parent_comp)
    arms["SELECTIVE"]["removed"]=arms["SELECTIVE"]["w"].selective_y_off(pmask)
    arms["SHAM"]["removed"]=arms["SHAM"]["w"].selective_y_off(np.zeros_like(allmask))
    arms["GLOBAL"]["removed"]=arms["GLOBAL"]["w"].selective_y_off(allmask)
    out={}
    for a in ARMS:
        wa=arms[a]["w"]
        dfix=[]; pfix=[]; bfix=[]; ny=[]; nx=[]; nc=[]
        thirdP=False; integ2=True
        for k in range(EP.T_HOLD):
            wa._one_step()
            free=sp.CAP-sum(wa.n[s] for s in O.SPECIES)
            if free.min()<0 or max(wa.n[s].max() for s in O.SPECIES)>sp.CAP: integ2=False
            cells2,comps2=centres_now(wa)
            if len(comps2)>=3: thirdP=True
            X=wa.n["X"]
            dfix.append(int(X[DFIX].sum())); pfix.append(int(X[PFIX].sum()))
            b=wa.last_births
            bfix.append(int(b[DFIX].sum()) if b is not None else 0)
            ny.append(int(wa.n["Y"].sum())); nx.append(int(X.sum())); nc.append(len(comps2))
        # reproduce the archive's own moving-disc endpoint measurement
        cells2,comps2=centres_now(wa); dmass=None; dexists=False; post_born=0
        if comps2:
            best=min(range(len(comps2)),key=lambda j: ID.tdist(ID.centroid(cells2,comps2[j]),dcen))
            if ID.tdist(ID.centroid(cells2,comps2[best]),dcen)<=3*ID.CORE_R:
                dexists=True
                dmass=float(xplane(wa)[ID.disc_mask(*[int(round(v))%ID.L for v in ID.centroid(cells2,comps2[best])])].sum())
                sn=FE.tracker_snapshot(wa); cy,cx=ID.centroid(cells2,comps2[best])
                dm=ID.disc_mask(int(round(cy))%ID.L,int(round(cx))%ID.L)
                inside=dm[sn["y"],sn["x"]]
                post_born=int((inside & (sn["birth_step"]>t_m)).sum())
        out[a]={"removed":arms[a]["removed"],"daughter_exists":dexists,"daughter_mass_post":dmass,
                "criterion_E_post_intervention_births_in_daughter":post_born,
                "third_centre_in_window":thirdP,"integrity_ok_post":bool(integ2),
                "final_NY":ny[-1],"final_NX":nx[-1],
                "NX_series_every_25":[nx[i] for i in range(0,EP.T_HOLD,25)],
                "NY_series_every_25":[ny[i] for i in range(0,EP.T_HOLD,25)],
                "_fixed_daughter_mass":dfix,"_fixed_parent_mass":pfix,
                "_fixed_daughter_births":bfix,"_ncen":nc}
    return {"block":idx,"seed":seed,"tag":tag,"chk":chk,
            "three_pre_hashes":three_hashes,"three_pre_rng":three_rng,
            "daughter_centroid":[round(v,4) for v in dcen],
            "parent_centroid":[round(v,4) for v in pcen],
            "ARMS":out}

def main():
    os.makedirs(REPLAY,exist_ok=True)
    A=json.load(open(f"{OUT}/_calcA_rows.json"))
    T=[r for r in A["rows"] if r["triggered"]]
    mismatches=[]; done=[]
    for r in sorted(T,key=lambda x:x["block"]):
        R=replay_block(int(r["block"]),int(r["seed"]),r)
        bad=[]
        for k,v in R["chk"].items():
            if r[k]!=v: bad.append((k,r[k],v))
        for a in ARMS:
            for k in ("removed","daughter_exists","daughter_mass_post","final_NY","final_NX",
                      "criterion_E_post_intervention_births_in_daughter","third_centre_in_window",
                      "integrity_ok_post","NX_series_every_25","NY_series_every_25"):
                if r["ARMS"][a][k]!=R["ARMS"][a][k]: bad.append((a+"."+k,r["ARMS"][a][k],R["ARMS"][a][k]))
        R["BIT_EXACT"]=not bad; R["MISMATCH"]=bad
        if bad: mismatches.append((R["tag"],bad[:4]))
        json.dump(R,open(f"{REPLAY}/{R['tag']}.json","w"))
        done.append(R["tag"])
        print("  [%2d/22] %s bit_exact=%s"%(len(done),R["tag"],R["BIT_EXACT"]),flush=True)
    print("\nBIT_EXACT: %d / %d"%(sum(1 for t in done)-len(mismatches),len(done)))
    if mismatches:
        print("MISMATCHES:"); [print("  ",m) for m in mismatches[:6]]

if __name__=="__main__": main()
