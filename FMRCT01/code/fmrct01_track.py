"""FMRCT01 — the frozen trigger, and identity/descent tracking (implementation A).

NOTHING HERE IS NEW SCIENCE. The pieces are imported byte-unchanged:
  centres, centroid, toroidal distance, strict identity link  -> fdot01_centres
  organisational descent                                      -> mrci01_descent
  functional maturation state machine and mass ratio          -> fmrt01_endpoint / fdflt01_endpoint
The only frozen FMRCT01 choices are LATEST_ALLOWED_TRIGGER = 6500 and the full-horizon policy.
"""
from __future__ import annotations
import sys, json
import numpy as np
REPO="/home/claude/edl"
for _p in (f"{REPO}/FDOT01/code", f"{REPO}/MRCI01/code", f"{REPO}/FMRT01/code",
           f"{REPO}/FDFLT01/code", f"{REPO}/PQEC01/code"):
    if _p not in sys.path: sys.path.insert(0,_p)
import fdot01_centres as CC
import fmrct01_descent as DS   # the FROZEN FMRCT01 rule; see its docstring for why the literal MRCI01 clause 4 is degenerate here
import fmrt01_endpoint as EP
import fmrt01_identity as ID
L=CC.L; CORE_R=CC.CORE_R
NEED=EP.NEED                      # 250, the frozen FDFLT01 maturation length
F_PRIMARY=EP.F_PRIMARY            # 1 - 1/e
T_HORIZON=11000
LATEST_ALLOWED_TRIGGER=6500       # FMRCT01 frozen; FMRT01 used 10750
POST_TRIGGER_WINDOW=T_HORIZON-LATEST_ALLOWED_TRIGGER   # 4500

def centres_now(w):
    ys,xs=np.nonzero(w.n["Y"])
    cells=[(int(y),int(x)) for y,x in zip(ys,xs)]
    return cells,CC.components(cells)

def xplane(w): return w.n["X"]

class Trigger:
    """the frozen FDFLT01 functional-maturation event, online, with the FMRCT01 latest-trigger rule,
    plus ONLINE identity tracking so that organisational descent is evaluated AT THE SEPARATION and
    then carried forward under the strict identity rule.

    Evaluating descent at t_m instead would be wrong: 250 steps after a clean separation both
    components can have drifted beyond CORE_R of the parent's last single-component centroid, and a
    clean descent would be misread as ambiguous. The rule is applied where it is defined.

    The world is NEVER stopped by this class. It only reports.
    """
    def __init__(self):
        self.w=EP.TriggerWatcher(); self.t_m=None
        self.cells_tm=None; self.parent_comp=None; self.daughter_comp=None
        self.descent_level="DESCENT_NEVER_ATTEMPTED"; self.descent_step=None
        self.descent_literal="DESCENT_NEVER_ATTEMPTED"; self.descent_distances=None
        self.parent_id=None; self.daughter_id=None
        self._prev=None; self._prev_ids=[]; self._next=0
        self.n_descent_attempts=0

    def _ids_for(self,cens):
        if self._prev is None:
            ids=[]
            for _ in cens:
                ids.append(self._next); self._next+=1
            return ids
        m=CC.link(self._prev[0],cens)
        ids=[]
        for j in range(len(cens)):
            src=[i for i,jj in m.items() if jj==j]
            if len(src)==1 and src[0]<len(self._prev_ids):
                ids.append(self._prev_ids[src[0]])
            else:
                ids.append(self._next); self._next+=1
        return ids

    def observe(self,t,w,cells,comps,integ):
        cens=[CC.centroid(cells,g) for g in comps] if comps else []
        ids=self._ids_for(cens)
        # --- organisational descent, evaluated at the 1 -> 2 transition ---
        if self._prev is not None and len(self._prev_ids)==1 and len(comps)==2:
            self.n_descent_attempts+=1
            pcells,pcomps=self._prev[1],self._prev[2]
            pi,di,lvl=DS.descent(pcells,pcomps[0],cells,comps)
            _,_,lit=DS.descent_literal_mrci01(pcells,pcomps[0],cells,comps)
            self.descent_level=lvl; self.descent_step=t
            self.descent_literal=lit
            self.descent_distances=[round(x,4) for x in DS.distances(pcells,pcomps[0],cells,comps)]
            if pi is not None:
                self.parent_id=ids[pi]; self.daughter_id=ids[di]
            else:
                self.parent_id=self.daughter_id=None
        self._prev=(cens,list(cells),[list(g) for g in comps]); self._prev_ids=ids
        if self.t_m is not None: return False
        NY=int(w.n["Y"].sum()); ncen=len(comps)
        st=EP.state_of(NY,ncen,integ)
        cand=self.w.observe(t,st)
        if not cand: return False
        if t>LATEST_ALLOWED_TRIGGER or ncen!=2: return False
        vals=EP.local_x_masses(xplane(w),cells,comps)
        if EP.f5_ratio(vals)<F_PRIMARY: return False
        self.w.fired=True; self.t_m=t; self.cells_tm=list(cells)
        # the two identities present at maturation must be exactly the pair named at separation
        if (self.parent_id is not None and self.daughter_id is not None
                and set(ids)=={self.parent_id,self.daughter_id}):
            self.parent_comp=[int(i) for i in comps[ids.index(self.parent_id)]]
            self.daughter_comp=[int(i) for i in comps[ids.index(self.daughter_id)]]
        else:
            self.parent_comp=self.daughter_comp=None
            if self.descent_level.startswith("PARENT"):
                self.descent_level="DESCENT_IDENTITY_NOT_CARRIED_TO_MATURATION"
        return True

# ------------------------------------------------------------------ offline identity tracking
def ledger_maps(ycells,ybirth,ydeath,xbirth):
    per={}; yb={}; yd={}; xb={}
    for r in ycells: per.setdefault(int(r[0]),[]).append((int(r[1]),int(r[2]),int(r[3])))
    for r in ybirth: yb.setdefault(int(r[0]),[]).append(((int(r[1]),int(r[2])),int(r[3])))
    for r in ydeath: yd.setdefault(int(r[0]),[]).append(((int(r[1]),int(r[2])),int(r[3])))
    for r in xbirth: xb.setdefault(int(r[0]),[]).append(((int(r[1]),int(r[2])),int(r[3])))
    return per,yb,yd,xb

def track(ycells,ybirth,ydeath,xbirth,horizon):
    """One pass with persistent identity ids under the STRICT rule. Returns per-step records:
       step -> {"ids":[...], "cellsets":[...], "cens":[...]} plus the id event ledgers."""
    per,yb,yd,xb=ledger_maps(ycells,ybirth,ydeath,xbirth)
    nxt=0; steps={}; prev_cens=None; prev_ids=[]
    ev={}   # id -> dict of event lists
    def new_id(t):
        nonlocal nxt
        i=nxt; nxt+=1
        ev[i]={"start":t,"end":t,"ybirth":[],"ydeath":[],"xbirth":[],"minNY":10**9,"steps":0,
               "parent_of":None,"born_from":None}
        return i
    for t in range(horizon):
        rows=per.get(t)
        if not rows:
            prev_cens=None; prev_ids=[]; continue
        cells=[(y,x) for y,x,_ in rows]; nmap={(y,x):n for y,x,n in rows}
        gs=CC.components(cells)
        cens=[CC.centroid(cells,g) for g in gs]
        sets=[set(cells[i] for i in g) for g in gs]
        m=CC.link(prev_cens,cens) if prev_cens is not None else {}
        ids=[]
        for j in range(len(gs)):
            src=[i for i,jj in m.items() if jj==j]
            if len(src)==1 and src[0]<len(prev_ids):
                i=prev_ids[src[0]]
            else:
                i=new_id(t)
            ids.append(i)
            e=ev[i]; e["end"]=t; e["steps"]+=1
            S=sets[j]
            e["minNY"]=min(e["minNY"],sum(nmap[c] for c in S))
            for c,k in yb.get(t,()):
                if c in S: e["ybirth"].append((t,k))
            for c,k in yd.get(t,()):
                if c in S: e["ydeath"].append((t,k))
            for c,k in xb.get(t,()):
                if c in S: e["xbirth"].append((t,k))
        steps[t]={"ids":ids,"sets":sets,"cens":cens,"cells":cells}
        prev_cens=cens; prev_ids=ids
    return steps,ev

def first_descent(steps,horizon):
    """the FIRST 1 -> 2 separation that the FROZEN rule resolves. Returns a dict."""
    last=None; attempts=[]
    for t in range(horizon):
        s=steps.get(t)
        if s is None: last=None; continue
        if last is not None and len(last["ids"])==1 and len(s["ids"])==2:
            pc=[last["cells"].index(c) for c in sorted(last["sets"][0])]
            cc=[sorted([s["cells"].index(c) for c in sorted(S)]) for S in s["sets"]]
            p,d,lvl=DS.descent(last["cells"],pc,s["cells"],cc)
            _,_,lit=DS.descent_literal_mrci01(last["cells"],pc,s["cells"],cc)
            dist=[round(x,4) for x in DS.distances(last["cells"],pc,s["cells"],cc)]
            attempts.append({"step":t,"frozen":lvl,"literal":lit,"d":dist})
            if p is not None:
                return {"step":t,"parent_id":s["ids"][p],"daughter_id":s["ids"][d],
                        "frozen":lvl,"literal":lit,"d":dist,"attempts":len(attempts)}
        last=s
    return {"step":None,"parent_id":None,"daughter_id":None,
            "frozen":(attempts[-1]["frozen"] if attempts else "DESCENT_NEVER_ATTEMPTED"),
            "literal":(attempts[-1]["literal"] if attempts else "DESCENT_NEVER_ATTEMPTED"),
            "d":None,"attempts":len(attempts)}

def identity_turnover(ev,idx,t_from,window=None,require_after=None):
    """COMPLETE + FUNCTIONAL turnover inside ONE identity, under the frozen FDOT01 rules.
       require_after: only Y births/removals strictly after this step count toward the event."""
    e=ev.get(idx)
    if e is None: return None
    lo=require_after if require_after is not None else -1
    hi=(t_from+window) if window is not None else 10**9
    yb=[t for t,_ in e["ybirth"] if lo< t<=hi]
    yd=[t for t,_ in e["ydeath"] if lo< t<=hi]
    xb=[t for t,_ in e["xbirth"]]
    out={"id":idx,"start":e["start"],"end":e["end"],"n_steps":e["steps"],
         "minNY":e["minNY"] if e["minNY"]<10**9 else 0,
         "y_births":len(yb),"y_deaths":len(yd),"x_births":len(xb),
         "COMPLETE":False,"FUNCTIONAL":False,"first_y_death":None,
         "x_before":0,"x_after":0,"post_duration":0}
    if yb and yd and out["minNY"]>=1:
        out["COMPLETE"]=True
        fd=min(yd); out["first_y_death"]=fd
        out["x_before"]=sum(1 for t in xb if lo< t<fd)
        out["x_after"]=sum(1 for t in xb if t>fd)
        out["post_duration"]=e["end"]-fd
        out["FUNCTIONAL"]=bool(out["x_before"]>0 and out["x_after"]>0 and out["post_duration"]>0)
    return out
