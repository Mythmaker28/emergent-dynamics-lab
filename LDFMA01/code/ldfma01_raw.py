"""LDFMA01 Section 2 — THE THIRD RECONSTRUCTION, written from the archive schema alone.

It imports neither tlmr01_offline (TLMR01's online-id-consuming classifier) nor any fimrcc01_*
module (FIMRCC01's daughter-verdict implementation). It opens the .npz and reads the raw arrays
declared by TLMR01-ARCHIVE-1, takes the frozen constants from the PQEC01 and BPRTC01 freeze JSONs,
and rebuilds everything from their written definitions.

Deliberately different implementation choices, so that agreement is evidence rather than shared
provenance:
  * components by BFS flood-fill over an explicit adjacency list, not union-find (FDOT01's choice)
    and not label propagation (FIMRCC01's choice);
  * the state machine, the link rule, the descent rule, the maturation run detector, the gates,
    the identity intervals and the turnover predicate all re-derived from their written statements.

ONE DECLARED DEPENDENCY, unchanged and unavoidable: the local X disc mass k_xd. The archive stores
the X field only on Y-occupied cells while the frozen gate sums X over an 81-cell disc, so k_xd
cannot be recomputed. It is read from the component rows and attached by a PHYSICAL match on
(ncells, nY, exact centroid); no component id is ever used to make that match.
"""
from __future__ import annotations
import numpy as np, json, math, os
from collections import deque

REPO=os.environ.get("LDFMA01_REPO","/home/claude/edl")

def _constants(repo=None):
    r=repo or REPO
    pq=json.load(open(os.path.join(r,"PQEC01/out/PQEC01_MASTER_FREEZE.json")))
    bp=json.load(open(os.path.join(r,"BPRTC01/out/BPRTC01_MASTER_FREEZE.json")))
    def find(d,key):
        if isinstance(d,dict):
            if key in d: return d[key]
            for v in d.values():
                x=find(v,key)
                if x is not None: return x
        elif isinstance(d,list):
            for v in d:
                x=find(v,key)
                if x is not None: return x
        return None
    C=find(pq,"INHERITED_FROZEN_CONSTANTS") or {}
    T=bp["TRIGGER"]
    return (int(C["L"]),float(C["CORE_R"]),int(T["NEED"]),float(T["F_PRIMARY"]),
            int(T["LATEST_ALLOWED_TRIGGER"]))

L,CORE_R,NEED,F_PRIMARY,LATEST=_constants()
R2=CORE_R*CORE_R

# ------------------------------------------------------------------ geometry
def tdist2(y1,x1,y2,x2):
    dy=abs(y1-y2); dy=min(dy,L-dy); dx=abs(x1-x2); dx=min(dx,L-dx)
    return dy*dy+dx*dx

def tdist(a,b):
    dy=abs(a[0]-b[0]); dy=min(dy,L-dy); dx=abs(a[1]-b[1]); dx=min(dx,L-dx)
    return math.hypot(dy,dx)

def components_bfs(ys,xs):
    """toroidal single-linkage at CORE_R by BFS flood-fill. The frontier expansion is the
    algorithm; the neighbour lookup is vectorised so that the O(n^2) adjacency test does not run
    in the interpreter. Groups are returned sorted ascending and ordered by their smallest member.
    `_components_bfs_reference` below is the same BFS with an interpreted adjacency list, kept as
    the slow obviously-correct version the fast path is checked against."""
    n=len(ys)
    if n==0: return []
    if n==1: return [[0]]
    ya=np.asarray(ys,np.int64); xa=np.asarray(xs,np.int64)
    dy=np.abs(ya[:,None]-ya[None,:]); dy=np.minimum(dy,L-dy)
    dx=np.abs(xa[:,None]-xa[None,:]); dx=np.minimum(dx,L-dx)
    adj=(dy*dy+dx*dx)<=R2
    np.fill_diagonal(adj,False)
    seen=np.zeros(n,bool); out=[]
    for s0 in range(n):
        if seen[s0]: continue
        seen[s0]=True; q=deque([s0]); g=[s0]
        while q:
            u=q.popleft()
            nb=np.flatnonzero(adj[u]&~seen)
            if nb.size:
                seen[nb]=True
                l=nb.tolist(); g.extend(l); q.extend(l)
        out.append(sorted(g))
    out.sort(key=lambda gg:gg[0])
    return out

def _components_bfs_reference(ys,xs):
    n=len(ys)
    if n==0: return []
    adj=[[] for _ in range(n)]
    for i in range(n):
        yi=ys[i]; xi=xs[i]
        for j in range(i+1,n):
            if tdist2(yi,xi,ys[j],xs[j])<=R2:
                adj[i].append(j); adj[j].append(i)
    seen=[False]*n; out=[]
    for s0 in range(n):
        if seen[s0]: continue
        seen[s0]=True; q=deque([s0]); g=[s0]
        while q:
            u=q.popleft()
            for v in adj[u]:
                if not seen[v]: seen[v]=True; g.append(v); q.append(v)
        out.append(sorted(g))
    out.sort(key=lambda gg:gg[0])
    return out

def centroid(ys,xs,idx):
    """the frozen centroid: anchor on the FIRST member, wrap each offset into [-L/2, L/2),
    average, wrap back. Written out rather than imported. Summation is left-to-right in index
    order, matching the parent's list comprehension exactly."""
    ay=ys[idx[0]]; ax=xs[idx[0]]
    if len(idx)==1: return (float(ay)%L,float(ax)%L)
    sy=0.0; sx=0.0
    for i in idx:
        sy+=((ys[i]-ay+L/2)%L)-L/2
        sx+=((xs[i]-ax+L/2)%L)-L/2
    m=len(idx)
    return ((ay+sy/m)%L,(ax+sx/m)%L)

def link(prev,cur):
    """the frozen identity rule: a link survives only when the previous centre has exactly one
    candidate within CORE_R and that candidate has exactly one candidate back. Split, merge and
    tie all terminate; none is resolved by preference."""
    if not prev or not cur: return {}
    fwd={}; bwd={j:[] for j in range(len(cur))}
    for i,p in enumerate(prev):
        c=[j for j,q in enumerate(cur) if tdist(p,q)<=CORE_R]
        fwd[i]=c
        for j in c: bwd[j].append(i)
    return {i:c[0] for i,c in fwd.items() if len(c)==1 and len(bwd[c[0]])==1}

def link_reason(prev,cur):
    if not prev or not cur: return {i:"NO_PARTNER" for i in range(len(prev))}
    fwd={}; bwd={j:[] for j in range(len(cur))}
    for i,p in enumerate(prev):
        c=[j for j,q in enumerate(cur) if tdist(p,q)<=CORE_R]
        fwd[i]=c
        for j in c: bwd[j].append(i)
    out={}
    for i,c in fwd.items():
        if len(c)==0: out[i]="OUT_OF_RANGE"
        elif len(c)>1: out[i]="SPLIT_OR_TIE"
        elif len(bwd[c[0]])>1: out[i]="MERGE"
        else: out[i]="CONTINUED"
    return out

def descent(pys,pxs,pidx,ys,xs,groups):
    """the frozen FMRCT01 organisational descent rule, written out."""
    if len(groups)!=2: return None,None,"DESCENT_AMBIGUOUS_NOT_EXACTLY_TWO_COMPONENTS"
    pc=centroid(pys,pxs,pidx)
    d=[tdist(pc,centroid(ys,xs,g)) for g in groups]
    if d[0]==d[1]: return None,None,"DESCENT_AMBIGUOUS_EXACT_TIE"
    p=0 if d[0]<d[1] else 1
    if d[p]>CORE_R: return None,None,"DESCENT_AMBIGUOUS_PARENT_NOT_CONTINUOUS"
    return p,1-p,"PARENT_CONTINUED_UNIQUELY"

def state_of(nY,ncen,ok):
    if not ok: return "F"
    if nY==0: return "E"
    if ncen>=3: return "P"
    if nY==1: return "O"
    return "S" if ncen==2 else "C"

def f5(vals):
    hi=max(vals) if vals else 0
    return (min(vals)/hi) if hi>0 else 0.0

# ------------------------------------------------------------------ the world
class World:
    """everything rebuilt from the raw arrays."""
    def __init__(self,path):
        z=np.load(path,allow_pickle=True)
        self.meta=json.loads(str(z["meta"][0]))
        self.T=int(self.meta["steps_executed"])
        self.ok=bool(self.meta["integrity_ok"])
        s=z["s"]
        self.nY=np.zeros(self.T,np.int64); self.ncomp_online=np.zeros(self.T,np.int32)
        for r in s:
            t=int(r[0])
            if t<self.T: self.nY[t]=int(r[1]); self.ncomp_online[t]=int(r[7])
        ct=z["c_t"]; o=np.argsort(ct,kind="stable")
        self.cy={}; self.cx={}; self.cnY={}
        cy=z["c_y"][o]; cx=z["c_x"][o]; cn=z["c_nY"][o]; ct=ct[o]
        b=np.searchsorted(ct,np.arange(self.T+1))
        for t in range(self.T):
            a,e=int(b[t]),int(b[t+1])
            if e>a:
                self.cy[t]=cy[a:e].astype(np.int64).tolist()
                self.cx[t]=cx[a:e].astype(np.int64).tolist()
                self.cnY[t]=cn[a:e].astype(np.int64).tolist()
        kt=z["k_t"]; ko=np.argsort(kt,kind="stable")
        self.krows={}
        kt2=kt[ko]; kb=np.searchsorted(kt2,np.arange(self.T+1))
        K={k:z["k_"+k][ko] for k in ("ncells","nY","a0y","a0x","soy","sox","xd")}
        for t in range(self.T):
            a,e=int(kb[t]),int(kb[t+1])
            if e>a:
                self.krows[t]=[{"ncells":int(K["ncells"][i]),"nY":int(K["nY"][i]),
                                "cy":(int(K["a0y"][i])+float(int(K["soy"][i]))/int(K["ncells"][i]))%L,
                                "cx":(int(K["a0x"][i])+float(int(K["sox"][i]))/int(K["ncells"][i]))%L,
                                "xd":int(K["xd"][i])} for i in range(a,e)]
        self.ybirth=z["ybirth"]; self.ydeath=z["ydeath"]; self.xbirth=z["xbirth"]
        self._build()

    def _build(self):
        self.groups={}; self.cens={}; self.gnY={}; self.gcells={}; self.gxd={}
        self.xd_bijective=True; self.xd_fail=[]
        for t in self.cy:
            ys=self.cy[t]; xs=self.cx[t]; occ=self.cnY[t]
            gs=components_bfs(ys,xs)
            self.groups[t]=gs
            self.cens[t]=[centroid(ys,xs,g) for g in gs]
            self.gnY[t]=[sum(occ[i] for i in g) for g in gs]
            self.gcells[t]=[frozenset((ys[i],xs[i]) for i in g) for g in gs]
            rows=self.krows.get(t,[]); used=set(); xd=[]
            for j,g in enumerate(gs):
                cyj,cxj=self.cens[t][j]
                hit=[k for k,d in enumerate(rows) if k not in used and d["ncells"]==len(g)
                     and d["nY"]==self.gnY[t][j] and abs(d["cy"]-cyj)<1e-9 and abs(d["cx"]-cxj)<1e-9]
                if len(hit)==1: xd.append(rows[hit[0]]["xd"]); used.add(hit[0])
                else: xd.append(None); self.xd_bijective=False; self.xd_fail.append(t)
            self.gxd[t]=xd
        self.ncen=[len(self.groups.get(t,[])) for t in range(self.T)]
        self.states=[state_of(int(self.nY[t]),self.ncen[t],self.ok) for t in range(self.T)]

    # ---------- identities ----------
    def trace(self):
        """running identity ids under the frozen link rule, plus the descent naming as of each
        step, plus the full interval event content."""
        yb={};yd={};xb={}
        for arr,d in ((self.ybirth,yb),(self.ydeath,yd),(self.xbirth,xb)):
            for r in arr: d.setdefault(int(r[0]),[]).append((int(r[1]),int(r[2])))
        nxt=0; prev=None; prev_ids=[]; ev={}; ids_at={}; named_at={}; lvl_at={}
        pid=did=None; lvl="DESCENT_NEVER_ATTEMPTED"; lstep=None; nattempt=0
        for t in range(self.T):
            gs=self.groups.get(t)
            if not gs: prev=None; prev_ids=[]; continue
            cens=self.cens[t]
            m=link(prev[0],cens) if prev is not None else {}
            ids=[]
            for j in range(len(gs)):
                src=[i for i,jj in m.items() if jj==j]
                if len(src)==1 and src[0]<len(prev_ids): i=prev_ids[src[0]]
                else:
                    i=nxt; nxt+=1
                    ev[i]={"start":t,"end":t,"yb":[],"yd":[],"xb":[],"minNY":10**9,"steps":0}
                ids.append(i); e=ev[i]; e["end"]=t; e["steps"]+=1
                e["minNY"]=min(e["minNY"],self.gnY[t][j])
                S=self.gcells[t][j]
                for c in yb.get(t,()):
                    if c in S: e["yb"].append(t)
                for c in yd.get(t,()):
                    if c in S: e["yd"].append(t)
                for c in xb.get(t,()):
                    if c in S: e["xb"].append(t)
            if prev is not None and len(prev_ids)==1 and len(gs)==2:
                nattempt+=1
                pj,dj,v=descent(prev[1],prev[2],prev[3][0],self.cy[t],self.cx[t],gs)
                lvl=v; lstep=t
                if pj is not None: pid=ids[pj]; did=ids[dj]
                else: pid=did=None
            named_at[t]=(pid,did); lvl_at[t]=(lvl,lstep)
            ids_at[t]=list(ids)
            prev=(cens,self.cy[t],self.cx[t],gs); prev_ids=ids
        return ev,ids_at,named_at,lvl_at,nattempt

    # ---------- maturation ----------
    def episodes(self):
        st=self.states; out=[]; i=0
        while i<self.T:
            if st[i]!="S": i+=1; continue
            j=i
            while j+1<self.T and st[j+1]=="S": j+=1
            n=int(self.nY[i]); ln=j-i+1
            if j+1>=self.T: term="REACHED_THE_WINDOW_HORIZON"
            else:
                term={"E":"Y_EXTINCT","P":"FORMED_A_THIRD_CENTRE","O":"LOST_A_CENTRE_TO_A_SINGLE_Y",
                      "C":"MERGED_TO_ONE_CENTRE","F":"INTEGRITY_FAULT"}.get(st[j+1],"UNCLASSIFIED")
            amb=sum(1 for t in range(i,j) if len(link(self.cens.get(t,[]),self.cens.get(t+1,[])))!=2)
            e={"start":i,"end":j,"length":ln,"n_at_separation":n,"terminator":term,
               "interior_ambiguous_steps":amb,"MATURED":ln>=NEED,
               "candidate_step":(i+NEED-1) if ln>=NEED else None}
            if e["MATURED"]:
                c=e["candidate_step"]; xd=self.gxd.get(c,[])
                r=f5([v for v in xd if v is not None]) if xd and all(v is not None for v in xd) else None
                e.update({"candidate_ncen":len(self.groups.get(c,[])),"candidate_xd":xd,"f5":r,
                          "G_deadline":c<=LATEST,"G_two":len(self.groups.get(c,[]))==2,
                          "G_x":bool(r is not None and r>=F_PRIMARY),
                          "TRIGGERS":bool(c<=LATEST and len(self.groups.get(c,[]))==2
                                          and r is not None and r>=F_PRIMARY)})
            out.append(e); i=j+1
        return out

# ------------------------------------------------------------------ the per-world audit
def audit(path):
    w=World(path)
    ev,ids_at,named_at,lvl_at,nattempt=w.trace()
    eps=w.episodes()
    matured=[e for e in eps if e["MATURED"]]
    fired=[e for e in matured if e["TRIGGERS"]]
    t_m=min([e["candidate_step"] for e in fired],default=None)
    iv=w.meta.get("intervention",{})

    r={"tag":w.meta["tag"],"seed":w.meta["seed"],"T":w.T,
       "ARCHIVE_LABEL_NOT_AN_INPUT":w.meta["TERMINAL_LABEL"],
       "ARCHIVE_t_m_NOT_AN_INPUT":w.meta.get("t_m"),
       "xd_match_bijective":w.xd_bijective,
       "component_count_disagreements_vs_archive_step_array":
          sum(1 for t in range(w.T) if w.ncen[t]!=int(w.ncomp_online[t])),
       "n_episodes":len(eps),"n_matured":len(matured),"n_triggered":len(fired),
       "n_descent_attempts":nattempt,
       "trigger_step":t_m,
       "episode_terminators":{},
       "n_identity_ambiguous_episodes":sum(1 for e in eps if e["interior_ambiguous_steps"]>0)}
    for e in eps: r["episode_terminators"][e["terminator"]]=r["episode_terminators"].get(e["terminator"],0)+1

    if t_m is None:
        r["VERDICT"]="NOT_TRIGGERED"; return r
    pid,did=named_at.get(t_m,(None,None))
    lvl,lstep=lvl_at.get(t_m,("DESCENT_NEVER_ATTEMPTED",None))
    r["descent_level_at_trigger"]=lvl; r["descent_step_at_trigger"]=lstep
    ids=ids_at.get(t_m,[])
    carried=(pid is not None and did is not None and set(ids)=={pid,did})
    r["identity_carried_to_maturation"]=bool(carried)
    if not carried:
        r["VERDICT"]="TRIGGERED_IDENTITY_NOT_CARRIED__NO_REMOVAL"; return r
    r["VERDICT"]="TRIGGERED_AND_SELECTIVE_REMOVAL_APPLIED"
    jd=ids.index(did); jp=ids.index(pid)
    dcells=sorted(w.gcells[t_m][jd]); pcells=sorted(w.gcells[t_m][jp])

    # ---------- A. trigger-time state ----------
    r["A_trigger_time"]={"t_m":t_m,"world_nY_at_t_m":int(w.nY[t_m]),
      "n_centres_at_t_m":len(w.groups[t_m]),
      "episode_start":next(e["start"] for e in fired if e["candidate_step"]==t_m),
      "separation_occupancy":next(e["n_at_separation"] for e in fired if e["candidate_step"]==t_m),
      "episode_interior_ambiguous_steps":next(e["interior_ambiguous_steps"] for e in fired if e["candidate_step"]==t_m),
      "f5_ratio_at_trigger":next(e["f5"] for e in fired if e["candidate_step"]==t_m),
      "n_prior_matured_episodes":sum(1 for e in matured if e["candidate_step"]<t_m),
      "n_prior_episodes":sum(1 for e in eps if e["start"]<t_m)}

    # ---------- B. locked-daughter occupation and geometry ----------
    dcy,dcx=w.cens[t_m][jd]; pcy,pcx=w.cens[t_m][jp]
    r["B_daughter_geometry"]={"daughter_cells":[list(c) for c in dcells],
      "daughter_ncells":len(dcells),"daughter_nY":int(w.gnY[t_m][jd]),
      "daughter_centroid":[dcy,dcx],
      "daughter_mean_Y_per_cell":w.gnY[t_m][jd]/len(dcells),
      "daughter_radius":max((tdist((dcy,dcx),c) for c in dcells),default=0.0)}

    # ---------- C. local X / nSY / free / candidate environment at the trigger ----------
    idxmap={(w.cy[t_m][i],w.cx[t_m][i]):i for i in range(len(w.cy[t_m]))}
    r["C_local_environment"]={"daughter_xd":w.gxd[t_m][jd],"parent_xd":w.gxd[t_m][jp],
      "xd_ratio_daughter_over_parent":(w.gxd[t_m][jd]/w.gxd[t_m][jp]) if w.gxd[t_m][jp] else None,
      "daughter_xd_per_Y":(w.gxd[t_m][jd]/w.gnY[t_m][jd]) if w.gnY[t_m][jd] else None}

    # ---------- D. parent size and distance ----------
    r["D_parent"]={"parent_cells":[list(c) for c in pcells],"parent_ncells":len(pcells),
      "parent_nY":int(w.gnY[t_m][jp]),"parent_centroid":[pcy,pcx],
      "parent_daughter_centroid_distance":tdist((dcy,dcx),(pcy,pcx)),
      "parent_mass_removed_from_the_ledger":int(iv.get("removed_Y") or 0),
      "daughter_over_parent_nY":(w.gnY[t_m][jd]/w.gnY[t_m][jp]) if w.gnY[t_m][jp] else None}

    # ---------- removal fidelity, audited ----------
    r["REMOVAL_FIDELITY"]={
      "ledger_step_equals_reconstructed_t_m":int(iv.get("step",-1))==t_m,
      "ledger_parent_cells_match_reconstruction":
         set(map(tuple,iv.get("parent_cells") or []))==set(pcells),
      "ledger_daughter_cells_match_reconstruction":
         set(map(tuple,iv.get("daughter_cells_after") or []))==set(dcells),
      "Y_conserved":int(iv["Y_total_before"])-int(iv["removed_Y"])==int(iv["Y_total_after"]),
      "WY_gained_equals_Y_removed":int(iv["WY_total_after"])-int(iv["WY_total_before"])==int(iv["removed_Y"]),
      "parent_emptied":int(iv["parent_Y_after"])==0,
      "daughter_untouched":int(iv["daughter_Y_before"])==int(iv["daughter_Y_after"]),
      "rng_unchanged":iv["rng_hash_before"]==iv["rng_hash_after"]}
    r["REMOVAL_FIDELITY"]["ALL_PASS"]=all(r["REMOVAL_FIDELITY"].values())

    # ---------- the locked daughter's own interval ----------
    e=ev[did]
    yb=[t for t in e["yb"] if t>t_m]; yd=[t for t in e["yd"] if t>t_m]; xb=[t for t in e["xb"] if t>t_m]
    life=e["end"]-t_m
    steps=[t for t in range(t_m,w.T) if did in ids_at.get(t,())]
    last=max(steps) if steps else t_m
    if last>=w.T-1: term="REACHED_THE_WINDOW_HORIZON"
    else:
        nx=w.cens.get(last+1)
        if not nx: term="NO_COMPONENT_AT_THE_NEXT_STEP"
        else:
            j=ids_at[last].index(did)
            term=link_reason(w.cens[last],nx).get(j,"UNCLASSIFIED")
    # occupancy trajectory over the interval after t_m: the exposure that a Y decay acts on
    maxnY=0; pstep=0; hist={}
    for t in steps:
        j=ids_at[t].index(did); v=int(w.gnY[t][j])
        maxnY=max(maxnY,v); pstep+=v; hist[v]=hist.get(v,0)+1
    # ---- attribution-window probe -------------------------------------------------
    # The frozen rule attributes a ledger event at step t to the component whose CELL SET AT
    # STEP t contains the event cell. The archive writes cell rows AFTER the step, so a Y decay
    # that empties a cell removes that cell from the step-t rows and the event is attributed to
    # nothing. This probe re-attributes the same ledger rows using the cell set at step t-1 and
    # reports BOTH counts. It changes no frozen definition; it measures what the frozen one sees.
    dsets={}
    for t in steps:
        j=ids_at[t].index(did); dsets[t]=w.gcells[t][j]
    ydl={}; ybl={}
    for arr,dd in ((w.ydeath,ydl),(w.ybirth,ybl)):
        for row in arr:
            tt=int(row[0])
            if tt>t_m: dd.setdefault(tt,[]).append((int(row[1]),int(row[2])))
    yd_prev=[t for t in sorted(ydl) if (t-1) in dsets and any(c in dsets[t-1] for c in ydl[t])]
    yb_prev=[t for t in sorted(ybl) if (t-1) in dsets and any(c in dsets[t-1] for c in ybl[t])]
    complete=bool(yb and yd and e["minNY"]>=1)
    fd=min(yd) if yd else None
    xpre=sum(1 for t in xb if fd is not None and t<fd)
    xpost=sum(1 for t in xb if fd is not None and t>fd)
    functional=bool(complete and xpre>0 and xpost>0 and (e["end"]-fd)>0)
    # third centre / extinction inside the daughter's window
    third=next((t for t in range(t_m,last+1) if w.ncen[t]>=3),None)
    ext=next((t for t in range(t_m,last+1) if int(w.nY[t])==0),None)
    r["E_locked_daughter_interval"]={
      "interval_id":did,"interval_start":e["start"],"interval_end":e["end"],
      "post_removal_identity_lifetime":life,"contiguous":len(steps)==(last-t_m+1),
      "identity_termination_type":term,
      "maximum_locked_daughter_nY_after_t_m":maxnY,
      "minNY_over_the_whole_interval":e["minNY"],
      "first_accepted_Y_birth_after_t_m":(min(yb) if yb else None),
      "first_Y_removal_after_t_m":(min(yd) if yd else None),
      "n_Y_births_after_t_m":len(yb),"n_Y_removals_after_t_m":len(yd),
      "n_X_births_after_t_m":len(xb),
      "COMPLETE_TURNOVER":complete,
      "x_before_first_removal":xpre,"x_after_first_removal":xpost,
      "LOCAL_X_BEFORE_OK":bool(complete and xpre>0),"LOCAL_X_AFTER_OK":bool(complete and xpost>0),
      "FUNCTIONAL":functional,
      "first_third_centre_step_in_window":third,
      "first_extinction_step_in_window":ext,
      "daughter_particle_steps_after_t_m":pstep,
      "daughter_nY_histogram_after_t_m":hist,
      "steps_at_nY_1":hist.get(1,0),"steps_at_nY_ge_2":sum(v for k,v in hist.items() if k>=2),
      "fraction_of_life_at_nY_1":(hist.get(1,0)/len(steps)) if steps else None,
      "ATTRIBUTION_WINDOW_PROBE":{
        "n_Y_removals_attributed_at_step_t_frozen_rule":len(yd),
        "n_Y_removals_attributed_at_step_t_minus_1":len(yd_prev),
        "n_Y_births_attributed_at_step_t_frozen_rule":len(yb),
        "n_Y_births_attributed_at_step_t_minus_1":len(yb_prev),
        "first_removal_at_t_minus_1":(min(yd_prev) if yd_prev else None),
        "WOULD_BE_COMPLETE_UNDER_t_minus_1":bool(yb_prev and yd_prev and e["minNY"]>=1),
        "note":"reported only. The frozen rule is the one used for every verdict in this mission."}}
    # what ended the identity: how many components were within CORE_R of the daughter at the end
    if last<w.T-1 and w.cens.get(last+1):
        j=ids_at[last].index(did); dc=w.cens[last][j]
        r["E_locked_daughter_interval"]["n_successor_candidates_within_CORE_R"]=sum(
            1 for q in w.cens[last+1] if tdist(dc,q)<=CORE_R)
        r["E_locked_daughter_interval"]["n_centres_at_termination_step"]=w.ncen[last]
        r["E_locked_daughter_interval"]["n_centres_at_next_step"]=w.ncen[last+1]
        r["E_locked_daughter_interval"]["world_nY_at_termination"]=int(w.nY[last])

    # ---------- F. ambient population pressure ----------
    after=[i for i,d in ev.items() if d["end"]>t_m]
    comp=[]
    for i in after:
        d=ev[i]
        a=[t for t in d["yb"] if t>t_m]; b=[t for t in d["yd"] if t>t_m]; c=[t for t in d["xb"] if t>t_m]
        if not (a and b and d["minNY"]>=1): continue
        f=min(b); pre=sum(1 for t in c if t<f); post=sum(1 for t in c if t>f)
        comp.append({"id":i,"steps":d["steps"],"start":d["start"],"end":d["end"],
                     "first_removal":f,
                     "FUNCTIONAL":bool(pre>0 and post>0 and (d["end"]-f)>0)})
    ncen_after=[w.ncen[t] for t in range(t_m,w.T)]
    r["F_ambient"]={"n_identity_intervals_total":len(ev),
      "n_identity_intervals_live_after_t_m":len(after),
      "ambient_complete_interval_count":len(comp),
      "ambient_functional_interval_count":sum(1 for c in comp if c["FUNCTIONAL"]),
      "ambient_FUNCTIONAL":any(c["FUNCTIONAL"] for c in comp),
      "mean_centres_after_t_m":sum(ncen_after)/len(ncen_after) if ncen_after else 0,
      "max_centres_after_t_m":max(ncen_after) if ncen_after else 0,
      "mean_world_nY_after_t_m":float(np.mean(w.nY[t_m:])),
      "interval_lifetimes_after_t_m":[ev[i]["steps"] for i in after],
      "interval_start_steps_after_t_m":[ev[i]["start"] for i in after],
      "complete_interval_start_steps":[c["start"] for c in comp],
      "complete_interval_first_removal_steps":[c["first_removal"] for c in comp],
      "world_nY_at_t_m":int(w.nY[t_m]),
      "world_nY_at_daughter_interval_end":int(w.nY[min(e["end"],w.T-1)]),
      "world_nY_quantiles_after_t_m":[float(np.percentile(w.nY[t_m:],q)) for q in (5,25,50,75,95)],
      "first_step_after_t_m_with_world_nY_ge_20":next((t for t in range(t_m,w.T) if int(w.nY[t])>=20),None),
      "n_centres_timeline_after_t_m_mean_by_decile":[float(np.mean(w.ncen[t_m+int((w.T-t_m)*k/10):t_m+int((w.T-t_m)*(k+1)/10)])) for k in range(10)]}

    # ---------- G. competing-event timing ----------
    r["G_competing"]={"first_third_centre_after_t_m":third,
      "first_merge_to_one_after_t_m":next((t for t in range(t_m,w.T) if w.ncen[t]==1),None),
      "steps_to_identity_termination":life,
      "steps_from_t_m_to_horizon":w.T-1-t_m}
    r["WORLD_LEVEL_LOCKED_DAUGHTER_VERDICT"]="LOCKED_DAUGHTER_FUNCTIONAL_COMPLETE_TURNOVER" if functional \
        else "LOCKED_DAUGHTER_NO_FUNCTIONAL_COMPLETE_TURNOVER"
    return r
