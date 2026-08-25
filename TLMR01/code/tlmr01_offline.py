"""TLMR01 §4 §6 — the offline reconstruction and the five measurement objects M1-M5.

INDEPENDENCE. Every DECISION here is reimplemented from the frozen written rules; this module
imports no online trigger, no online endpoint and no online centre classifier. The frozen
constants are read from the same freeze the engine reads, and the toroidal distance and the
identity link are rewritten here in full. That is deliberate: the agreement between this module
and the online record is then a genuine two-implementation check, and tlmr01_paths qualifies it
before world 1. Where a value cannot be recomputed independently -- the component MEMBERSHIP,
which the archive stores as comp_id -- the archive's own reconstruction gate (§5) is what
guarantees it, and that dependence is declared here rather than hidden.

THE ARCHIVE IS THE ONLY INPUT. No function below takes a world object.
"""
from __future__ import annotations
import json, math, sys
import numpy as np
REPO="/home/claude/edl"
_C=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))["INHERITED_FROZEN_CONSTANTS"]
L=int(_C["L"]); CORE_R=float(_C["CORE_R"]); T_HORIZON=int(_C["T_HORIZON"])
NEED=250                      # the frozen FDFLT01 maturation length
F_PRIMARY=1.0-1.0/math.e      # the frozen FDFLT01 local-X mass ratio
LATEST_ALLOWED_TRIGGER=6500   # the frozen FMRCT01 deadline
sI=5                          # PTOPD01's declared occupation support ceiling

# ------------------------------------------------------------------ geometry, rewritten
def tdist(a,b):
    dy=abs(a[0]-b[0]); dy=min(dy,L-dy); dx=abs(a[1]-b[1]); dx=min(dx,L-dx)
    return math.hypot(dy,dx)

def link(prev,cur):
    """the frozen DOTC01 identity rule, rewritten: a link survives only when the previous centre
    has exactly one candidate within CORE_R and the current centre has exactly one. Split, merge
    and tie all terminate; none is ever resolved by preference."""
    if not prev or not cur: return {}
    fwd={i:[j for j,c in enumerate(cur) if tdist(p,c)<=CORE_R] for i,p in enumerate(prev)}
    bwd={j:[i for i,p in enumerate(prev) if tdist(p,c)<=CORE_R] for j,c in enumerate(cur)}
    return {i:js[0] for i,js in fwd.items() if len(js)==1 and len(bwd[js[0]])==1}

def link_reason(prev,cur):
    """why each previous centre did or did not continue. SPLIT / MERGE / OUT_OF_RANGE / CONTINUED."""
    out={}
    if not prev or not cur:
        return {i:"NO_PARTNER" for i in range(len(prev))}
    fwd={i:[j for j,c in enumerate(cur) if tdist(p,c)<=CORE_R] for i,p in enumerate(prev)}
    bwd={j:[i for i,p in enumerate(prev) if tdist(p,c)<=CORE_R] for j,c in enumerate(cur)}
    for i,js in fwd.items():
        if len(js)==0: out[i]="OUT_OF_RANGE"
        elif len(js)>1: out[i]="SPLIT_OR_TIE"
        elif len(bwd[js[0]])>1: out[i]="MERGE"
        else: out[i]="CONTINUED"
    return out

def centroid_component(a0,s,m):
    """the frozen centroid, recomputed in the SAME expression order as fdot01_centres.centroid:
    (a0 + sum(offsets)/m) % L. Every intermediate is exactly representable, so this is bit-equal
    to the online value rather than approximately equal. §5 proves it step by step."""
    return (a0+float(s)/m)%L

# ------------------------------------------------------------------ the frozen state machine
def state_of(nY,ncen,integrity_ok):
    """FDFLT01's frozen classifier, rewritten from its written definition.
       F integrity fault | E extinct | P premature third centre | O single Y | S two centres | C other"""
    if not integrity_ok: return "F"
    if nY==0: return "E"
    if ncen>=3: return "P"
    if nY==1: return "O"
    return "S" if ncen==2 else "C"

def f5_ratio(vals):
    hi=max(vals) if vals else 0.0
    return (min(vals)/hi) if hi>0 else 0.0

# ------------------------------------------------------------------ the archive
class Archive:
    """one world, read from its .npz, with no engine and no world object anywhere."""
    def __init__(self,path):
        z=np.load(path,allow_pickle=True)
        self.meta=json.loads(str(z["meta"][0]))
        self.schema=json.loads(str(z["schema"][0]))
        self.s=z["s"]                                    # (T,8)
        self.c={k:z["c_"+k] for k in ("t","y","x","nY","nX","nSY","free","cand","cid")}
        self.k={k:z["k_"+k] for k in ("t","id","ncells","nY","a0y","a0x","soy","sox","xd")}
        self.ybirth=z["ybirth"]; self.ydeath=z["ydeath"]; self.xbirth=z["xbirth"]
        self.T=int(self.meta["steps_executed"])
        self.integrity_ok=bool(self.meta["integrity_ok"])
        self._index()
    def _index(self):
        self.ncomp=np.zeros(self.T,np.int32); self.nY=np.zeros(self.T,np.int64)
        st=self.s
        for r in st:
            t=int(r[0])
            if t<self.T: self.ncomp[t]=int(r[7]); self.nY[t]=int(r[1])
        self.comps={}                                    # t -> list of dicts in comp_id order
        kt=self.k["t"]
        order=np.argsort(kt,kind="stable")
        cur=-1
        for i in order:
            t=int(kt[i])
            if t!=cur: cur=t; self.comps[t]=[]
            m=int(self.k["ncells"][i])
            self.comps[t].append({"id":int(self.k["id"][i]),"ncells":m,
                                  "nY":int(self.k["nY"][i]),
                                  "cy":centroid_component(int(self.k["a0y"][i]),int(self.k["soy"][i]),m),
                                  "cx":centroid_component(int(self.k["a0x"][i]),int(self.k["sox"][i]),m),
                                  "xd":int(self.k["xd"][i])})
        for t in self.comps: self.comps[t].sort(key=lambda d:d["id"])
        self.cells={}                                    # t -> list of (y,x,nY,cid) in row order
        ct=self.c["t"]; o2=np.argsort(ct,kind="stable"); cur=-1
        for i in o2:
            t=int(ct[i])
            if t!=cur: cur=t; self.cells[t]=[]
            self.cells[t].append((int(self.c["y"][i]),int(self.c["x"][i]),
                                  int(self.c["nY"][i]),int(self.c["cid"][i])))
    def cens(self,t):
        return [(d["cy"],d["cx"]) for d in self.comps.get(t,[])]
    def states(self):
        return [state_of(int(self.nY[t]),int(self.ncomp[t]),self.integrity_ok) for t in range(self.T)]

# ------------------------------------------------------------------ M1  fork hazard e(n)
def M1_fork_hazard(A):
    """e(n) = P(the world holds two or more centres at t+1 | it holds exactly ONE centre of
    occupancy n at t). The exposure is the single-centre step count at occupancy n, which is M4.
    The FULL transition table is recorded too, so no later definition needs a re-run."""
    expo={}; fork2={}; forkge2={}; trans={}
    for t in range(A.T-1):
        if A.ncomp[t]!=1: continue
        cl=A.comps.get(t)
        if not cl: continue
        n=int(cl[0]["nY"]); m=int(A.ncomp[t+1])
        expo[n]=expo.get(n,0)+1
        trans.setdefault(n,{}).setdefault(m,0)
        trans[n][m]+=1
        if m>=2: forkge2[n]=forkge2.get(n,0)+1
        if m==2: fork2[n]=fork2.get(n,0)+1
    return {"exposure_by_n":expo,"fork_to_two_or_more_by_n":forkge2,
            "fork_to_exactly_two_by_n":fork2,"transition_table_by_n":trans}

# ------------------------------------------------------------------ M2  maturation law s(n)
def episodes(A):
    """A maximal run of the frozen state S. n at separation is the world Y occupancy at the first
    step of the run, matching PTOPD01's convention exactly. The seven declared outcomes are
    inherited verbatim and the terminator is read from the state that ENDED the run."""
    st=A.states(); out=[]; i=0
    while i<A.T:
        if st[i]!="S": i+=1; continue
        j=i
        while j+1<A.T and st[j+1]=="S": j+=1
        n=int(A.nY[i]); ln=j-i+1
        if j+1>=A.T: term="REACHED_THE_WINDOW_HORIZON"
        else:
            nx=st[j+1]
            term={"E":"Y_EXTINCT","P":"FORMED_A_THIRD_CENTRE","O":"LOST_A_CENTRE_TO_A_SINGLE_Y",
                  "C":"MERGED_TO_ONE_CENTRE","F":"INTEGRITY_FAULT"}.get(nx,"UNCLASSIFIED")
        # IDENTITY_AMBIGUOUS: the two identities did not both continue cleanly at some interior
        # step although the count stayed at two. Declared and counted, never assumed zero.
        amb=0
        for t in range(i,j):
            m=link(A.cens(t),A.cens(t+1))
            if len(m)!=2: amb+=1
        matured=ln>=NEED
        cand=(i+NEED-1) if matured else None
        e={"start":i,"end":j,"length":ln,"n_at_separation":n,"terminator":term,
           "interior_ambiguous_steps":amb,"IDENTITY_AMBIGUOUS":amb>0,
           "MATURED":bool(matured),"candidate_step":cand}
        if matured:
            e.update(_candidate_gates(A,cand))
        out.append(e); i=j+1
    return out

def _candidate_gates(A,t):
    """the frozen FMRCT01 gates applied to one maturation candidate, rewritten."""
    cl=A.comps.get(t,[])
    xd=[d["xd"] for d in cl]
    r=f5_ratio(xd)
    return {"candidate_ncen":len(cl),"candidate_x_disc":xd,"candidate_f5_ratio":r,
            "GATE_deadline":bool(t<=LATEST_ALLOWED_TRIGGER),
            "GATE_exactly_two_centres":bool(len(cl)==2),
            "GATE_local_x_ratio":bool(r>=F_PRIMARY),
            "TRIGGERS":bool(t<=LATEST_ALLOWED_TRIGGER and len(cl)==2 and r>=F_PRIMARY)}

def M2_maturation(eps):
    by={}
    for e in eps:
        n=e["n_at_separation"]; d=by.setdefault(n,{"episodes":0,"matured":0,"terminators":{}})
        d["episodes"]+=1; d["matured"]+=int(e["MATURED"])
        d["terminators"][e["terminator"]]=d["terminators"].get(e["terminator"],0)+1
    return by

# ------------------------------------------------------------------ M3  P(trigger | matured)
def M3_trigger_given_matured(eps):
    m=[e for e in eps if e["MATURED"]]
    fired=[e for e in m if e["TRIGGERS"]]
    fail={"deadline":sum(1 for e in m if not e["GATE_deadline"]),
          "not_exactly_two_centres":sum(1 for e in m if not e["GATE_exactly_two_centres"]),
          "local_x_ratio":sum(1 for e in m if not e["GATE_local_x_ratio"])}
    return {"n_matured":len(m),"n_triggered":len(fired),"failure_modes":fail,
            "first_trigger_step":min([e["candidate_step"] for e in fired],default=None),
            "candidate_steps":[e["candidate_step"] for e in m]}

# ------------------------------------------------------------------ M4  single-centre exposure
def M4_exposure(A):
    by={}; tot=0
    for t in range(A.T):
        if A.ncomp[t]!=1: continue
        cl=A.comps.get(t)
        if not cl: continue
        n=int(cl[0]["nY"]); by[n]=by.get(n,0)+1; tot+=1
    above=sum(v for n,v in by.items() if n>sI)
    return {"single_centre_steps":tot,"by_occupancy":by,
            "steps_above_support_ceiling":above,"support_ceiling_sI":sI,
            "fraction_of_horizon_single_centre":(tot/A.T if A.T else 0.0),
            "max_single_centre_occupancy":(max(by) if by else 0)}

# ------------------------------------------------------------------ M5  integrated rate
def identity_intervals(A,since=0):
    """persistent identities under the frozen strict rule, rebuilt offline, with the event content
    of each interval taken from the recorded ledgers and the interval's OWN cells."""
    yb={}; yd={}; xb={}
    for arr,d in ((A.ybirth,yb),(A.ydeath,yd),(A.xbirth,xb)):
        for r in arr:
            d.setdefault(int(r[0]),[]).append(((int(r[1]),int(r[2])),int(r[3])))
    nxt=0; prev_c=None; prev_ids=[]; ev={}
    for t in range(A.T):
        cl=A.comps.get(t)
        if not cl: prev_c=None; prev_ids=[]; continue
        cens=[(d["cy"],d["cx"]) for d in cl]
        m=link(prev_c,cens) if prev_c is not None else {}
        ids=[]
        sets={}
        for (y,x,n,cid) in A.cells.get(t,()): sets.setdefault(cid,set()).add((y,x))
        for j in range(len(cl)):
            src=[i for i,jj in m.items() if jj==j]
            if len(src)==1 and src[0]<len(prev_ids): i=prev_ids[src[0]]
            else:
                i=nxt; nxt+=1
                ev[i]={"start":t,"end":t,"ybirth":[],"ydeath":[],"xbirth":[],"minNY":10**9,"steps":0}
            ids.append(i); e=ev[i]; e["end"]=t; e["steps"]+=1
            S=sets.get(cl[j]["id"],set())
            e["minNY"]=min(e["minNY"],cl[j]["nY"])
            for c,k in yb.get(t,()):
                if c in S: e["ybirth"].append(t)
            for c,k in yd.get(t,()):
                if c in S: e["ydeath"].append(t)
            for c,k in xb.get(t,()):
                if c in S: e["xbirth"].append(t)
        prev_c=cens; prev_ids=ids
    return ev

def turnover_in(ev,after):
    """the frozen DOTC01 COMPLETE_TURNOVER and its FUNCTIONAL qualification, restricted to
    identity intervals live strictly after `after`."""
    out=[]
    for i,e in ev.items():
        if e["end"]<=after: continue
        yb=[t for t in e["ybirth"] if t>after]; yd=[t for t in e["ydeath"] if t>after]
        xb=[t for t in e["xbirth"] if t>after]
        if not (yb and yd and e["minNY"]>=1): continue
        fd=min(yd)
        pre=sum(1 for t in xb if t<fd); post=sum(1 for t in xb if t>fd)
        dur=e["end"]-fd
        out.append({"id":i,"start":e["start"],"end":e["end"],"n_steps":e["steps"],
                    "first_y_death":fd,"y_births":len(yb),"y_deaths":len(yd),
                    "x_before":pre,"x_after":post,"post_duration":dur,
                    "COMPLETE":True,"FUNCTIONAL":bool(pre>0 and post>0 and dur>0)})
    return out

def M5_world_chain(A,eps):
    """the per-world integrated chain, entirely from the archive."""
    m3=M3_trigger_given_matured(eps)
    A_stage=m3["n_matured"]>0
    B_stage=m3["n_triggered"]>0
    iv=A.meta.get("intervention",{})
    C_stage=bool(iv.get("applied"))
    D=[]
    if C_stage:
        ev=identity_intervals(A)
        D=turnover_in(ev,int(iv["step"]))
    D_stage=any(d["FUNCTIONAL"] for d in D)
    return {"A_maturation_reached":bool(A_stage),"B_trigger_fired":bool(B_stage),
            "C_selective_removal_applied":C_stage,
            "D_post_removal_functional_complete_turnover":bool(D_stage),
            "n_post_removal_complete_intervals":len(D),
            "n_post_removal_functional_intervals":sum(1 for d in D if d["FUNCTIONAL"]),
            "INTEGRATED":bool(A_stage and B_stage and C_stage and D_stage),
            "post_removal_intervals":D[:20]}

def measure_world(path):
    A=Archive(path)
    eps=episodes(A)
    return {"tag":A.meta["tag"],"law":A.meta["law"],"seed":A.meta["seed"],
            "steps_executed":A.T,"integrity_ok":A.integrity_ok,
            "TERMINAL_LABEL":A.meta["TERMINAL_LABEL"],
            "online_t_m":A.meta.get("t_m"),
            "M1":M1_fork_hazard(A),"M2_episodes":eps,"M2":M2_maturation(eps),
            "M3":M3_trigger_given_matured(eps),"M4":M4_exposure(A),
            "M5":M5_world_chain(A,eps)}
