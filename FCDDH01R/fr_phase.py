"""FCDDH01R real-phase driver: builds a frozen plan, launches the durable supervisor, and
finalizes a completed phase into the byte-identical scientific drivers' expected layout.
Engineering only; it computes no scientific quantity."""
from __future__ import annotations
import hashlib, json, os, subprocess, sys, time
import numpy as np
H=os.path.dirname(os.path.abspath(__file__)); W=H+"/_work"
sys.path.insert(0,H); import fr_plan, EXACT_ONCE_PHASE_STATE_MACHINE as SM
sha=lambda p: hashlib.sha256(open(p,'rb').read()).hexdigest()
Q=json.load(open(H+"/FCDDH01R_NAMESPACE_AND_ROLE_QUEUES.json"))
RA=json.load(open(H+"/FCDDH01R_RANDOMIZATION_SEED_AND_ASSIGNMENT_MANIFEST.json"))
CW=W+"/fh_cworker.py"; AW=W+"/fh_aworker.py"
EXPECT={"SHAM":"identity_copy","CARRIER_1":"etcmnfc_core.transpose(st, I, J)",
        "CARRIER_2":"ppai_core.state_cross(st)"}
def root(role,ph): return "%s/_ledger/%s_%s"%(H,role,ph)
def launch(plan,logd):
    subprocess.run([H+"/fr_launch.sh",plan,logd],check=True,capture_output=True,text=True)

def plan_construct(role):
    tgt=12 if role=="DISCOVERY" else 16; mx=96 if role=="DISCOVERY" else 128
    panel="%s/_work/%s_PANEL"%(H,role); tmpd="%s/_tmp/%s_construct"%(H,role)
    os.makedirs(panel,exist_ok=True); os.makedirs(tmpd,exist_ok=True)
    oph=sha(CW); rows=[]; ordn=0
    for idx,seed in enumerate(Q[role+"_CANDIDATE_QUEUE"]):
        a=RA[role][str(idx)]
        for k in a["descendant_run_order"]:
            c=a["cells"][k]; g,al=c["geometry"],c["allocation"]; did="%d_%s_a%d"%(seed,g,al)
            rows.append({**fr_plan.row("C_"+did,ordn,
                [CW,str(seed),g,str(al),"%s/d_%s.npz"%(tmpd,did),"%s/m_%s.npz"%(tmpd,did)],
                [["%s/d_%s.npz"%(tmpd,did),"%s/d_%s.npz"%(panel,did)],
                 ["%s/m_%s.npz"%(tmpd,did),"%s/m_%s.npz"%(panel,did)]],
                oph,["upstream:%d"%seed,"geom:%s"%g,"alloc:%d"%al],"%d.%d"%(idx,k),cwd=W),
                "candidate":idx})
            ordn+=1
    p="%s/_plans/%s_construct.json"%(H,role)
    fr_plan.build(p,"FCDDH01R",role+"_CONSTRUCTION",root(role,"construct"),rows,mx)
    pl=json.load(open(p)); pl["stop_after_accepted_candidates"]=tgt
    pl["operations_per_candidate"]=4
    pl["plan_sha256"]=hashlib.sha256(json.dumps({k:v for k,v in pl.items()
        if k!="plan_sha256"},sort_keys=True).encode()).hexdigest()
    SM.write_fsync(p,json.dumps(pl,sort_keys=True,indent=1).encode()); return p

def finalize_construct(role):
    tgt=12 if role=="DISCOVERY" else 16
    r=json.load(open(root(role,"construct")+"/status/PHASE_RESULT.json"))
    st=root(role,"construct")+"/status"; panel="%s/_work/%s_PANEL"%(H,role)
    acc=r["accepted_candidates"]; blocks=[]
    for idx in acc[:tgt]:
        seed=Q[role+"_CANDIDATE_QUEUE"][idx]; a=RA[role][str(idx)]; ds=[]; pre=set()
        for k in range(4):
            c=a["cells"][k]; g,al=c["geometry"],c["allocation"]; did="%d_%s_a%d"%(seed,g,al)
            rid=[x["run_id"] for x in r["results"] if x["tag"]=="C_"+did][0]
            pay=json.load(open("%s/row-%s.payload.json"%(st,rid)))
            pre.add(pay["precursor_sha256"])
            ds.append({"did":did,"slot":c["slot"],"serializer_member":c["serializer_member"],
                       **{kk:pay[kk] for kk in ("geometry","allocation","checkpoint_state_sha",
                          "mask_sha","n_A","n_B","B_exact","production_reference_mask_agreement",
                          "rho_finite","g1_precursor_mask_identity","blob_sha256",
                          "forcing_trace_sha256","engine_steps")},
                       "checkpoint_file_sha256":sha("%s/d_%s.npz"%(panel,did)),
                       "mask_file_sha256":sha("%s/m_%s.npz"%(panel,did))})
        assert len(pre)==1, "block %d: precursor bytes not identical"%seed
        blocks.append({"candidate_index":idx,"upstream_seed":seed,
                       "geometry_coin":a["geometry_coin"],"precursor_sha256":list(pre)[0],
                       "descendants":ds})
    lock={"role":role,"target_blocks":tgt,"accepted_blocks":len(blocks),
          "PANEL_COMPLETE":len(blocks)>=tgt,
          role+"_CONSTRUCTION_STATUS":"COMPLETE" if len(blocks)>=tgt else "INCOMPLETE",
          "independent_ancestry_blocks":len(blocks),"descendants_per_block":4,"blocks":blocks,
          "start_ledger":{"charged_total":r["charged_rows"],
                          "raw_advance_total":r["charged_rows"],
                          "budget_charge":r["charged_rows"]},
          "burned_candidates":r["burned_candidates"],"attempts":len(r["results"])}
    json.dump(lock,open("%s/FCDDH00_%s_PANEL_LOCK.json"%(W,role),"w"),indent=1)
    json.dump(lock,open("%s/FCDDH01R_%s_PANEL_LOCK.json"%(H,role),"w"),indent=1)
    print(role,"construction blocks",len(blocks),"/",tgt,"charged",r["charged_rows"])
    return lock

def plan_acquire(role,phase):
    mx=96 if role=="DISCOVERY" else 128
    lock=json.load(open("%s/FCDDH00_%s_PANEL_LOCK.json"%(W,role)))
    panel="%s/_work/%s_PANEL"%(H,role)
    full="%s/_full/%s_%s"%(H,role,phase); tmpd="%s/_tmp/%s_%s"%(H,role,phase)
    os.makedirs(full,exist_ok=True); os.makedirs(tmpd,exist_ok=True)
    oph=sha(AW); rows=[]; ordn=0
    for b in lock["blocks"]:
        idx=str(b["candidate_index"])
        for k,d in enumerate(b["descendants"]):
            did=d["did"]; ck="%s/d_%s.npz"%(panel,did); mk="%s/m_%s.npz"%(panel,did)
            ops=[("SHAM","SHAM_0"),("SHAM","SHAM_1")] if phase=="sham" else \
                [(o,o) for o in RA[role][idx]["carrier_run_order"][str(k)]]
            for op,tag in ops:
                nm="%s_%s"%(tag,did)
                rows.append({**fr_plan.row("A_"+nm,ordn,
                    [AW,ck,mk,op,"%s/%s.npz"%(tmpd,nm),d["checkpoint_state_sha"],EXPECT[op]],
                    [["%s/%s.npz"%(tmpd,nm),"%s/%s.npz"%(full,nm)],
                     ["%s/%s.npz.meta.json"%(tmpd,nm),"%s/%s.npz.meta.json"%(full,nm)]],
                    oph,["ckpt:"+d["checkpoint_state_sha"],"op:"+op],"%s.%d.%s"%(idx,k,tag),cwd=W),
                    "candidate":None}); ordn+=1
    p="%s/_plans/%s_%s.json"%(H,role,phase)
    req=None
    if phase=="active":
        tl="%s/FCDDH00_%s_THRESHOLD_LOCK.json"%(W,role)
        req={"path":tl,"sha256":sha(tl)}
    fr_plan.build(p,"FCDDH01R","%s_%s"%(role,phase.upper()),root(role,phase),rows,mx,
                  required_prior_artifact=req)
    return p

def finalize_acquire(role,phase):
    r=json.load(open(root(role,phase)+"/status/PHASE_RESULT.json"))
    full="%s/_full/%s_%s"%(H,role,phase)
    arch="%s/_work/%s_%s_RAW_ARCHIVE"%(H,role,"SHAM" if phase=="sham" else "ACTIVE")
    os.makedirs(arch,exist_ok=True); man=[]
    for f in sorted(os.listdir(full)):
        if not f.endswith(".npz"): continue
        nm=f[:-4]; m=json.load(open("%s/%s.meta.json"%(full,f)))
        d=np.load("%s/%s"%(full,f)); rho,MA,MB=d["rho"],d["MA"],d["MB"]
        idx=np.nonzero(np.asarray(MA|MB).ravel())[0].astype(np.int32)
        vals=np.stack([np.asarray(rho[k]).ravel()[idx] for k in range(rho.shape[0])])
        op_=arch+"/"+f
        if not os.path.exists(op_): np.savez_compressed(op_,rho_support=vals,support_index=idx,MA=MA,MB=MB)
        man.append({"name":nm,"did":nm.split("_",2)[2],"op":m["op"],
                    "compact_sha256":sha(op_),"full_field_sha256":m["output_sha256"],
                    "terminal_state_sha":m["terminal_state_sha"],
                    "per_time_state_sha":m["per_time_state_sha"],"n_frames":m["n_frames"],
                    "scored_times":m["scored_times"],"touched_fields_at_t0":m["touched_fields_at_t0"],
                    "touch_set_ok":m["touch_set_ok"],"input_unchanged":m["input_unchanged"],
                    "rho_untouched_at_t0":m["rho_untouched_at_t0"],"rho_finite":m["rho_finite"],
                    "B_exact":m["B_exact"],"mask_sha":m["mask_sha"],
                    "expected_callable":m["expected_callable"]})
    exp=8*len(json.load(open("%s/FCDDH00_%s_PANEL_LOCK.json"%(W,role)))["blocks"])
    out={"role":role,"phase":phase,"rows":len(man),"expected_rows":exp,
         "COMPLETE":len(man)==exp,"labels_decoded":False,"scores_computed":False,
         "start_ledger":{"charged_total":r["charged_rows"]},"manifest":man}
    json.dump(out,open("%s/%s_%s_RAW_MANIFEST.json"%(W,role,"SHAM" if phase=="sham" else "ACTIVE"),"w"),indent=1)
    json.dump(out,open("%s/FCDDH01R_%s_%s_RAW_MANIFEST.json"%(H,role,phase.upper()),"w"),indent=1)
    print(role,phase,len(man),"/",exp,"COMPLETE",out["COMPLETE"],"charged",r["charged_rows"])
    return out

if __name__=="__main__":
    cmd,role=sys.argv[1],sys.argv[2]
    if cmd=="construct": launch(plan_construct(role),"%s/_logs/%s_construct"%(H,role))
    elif cmd=="fin_construct": finalize_construct(role)
    elif cmd in ("sham","active"): launch(plan_acquire(role,cmd),"%s/_logs/%s_%s"%(H,role,cmd))
    elif cmd.startswith("fin_"): finalize_acquire(role,cmd[4:])
    print("done",cmd,role)
