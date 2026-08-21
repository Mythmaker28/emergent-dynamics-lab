"""DOTC01 §17 — the single independent zero-run checker.

It imports NOTHING from the primary DOTC01 analysis. Where the primary used union-find and
numpy reduceat, this uses a scipy sparse connected-components routine and explicit per-step
python loops; where the primary used IEEE doubles it uses Decimal; where the primary walked a
forward chain it uses complementary survival products.
"""
from __future__ import annotations
import json, math, os, collections, datetime
from decimal import Decimal, getcontext
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
getcontext().prec=50
REPO="/home/claude/edl"; OUT=f"{REPO}/DOTC01/out"; PRAW="/home/claude/PQEC01/raw"
FZ=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))
PB=FZ["PHASE_B"]; C=FZ["INHERITED_FROZEN_CONSTANTS"]
L=int(C["L"]); CORE_R=float(C["CORE_R"]); HOR=int(C["T_HORIZON"])
PTS={"B1":(PB["POINT_B1"]["kY"],PB["POINT_B1"]["muY"]),"B2":(PB["POINT_B2"]["kY"],PB["POINT_B2"]["muY"])}

def life(muY):
    if muY<=0: return {"e_folding":None,"P_death_11000":0.0,"mean":None,"median":None}
    m=Decimal(repr(muY)); one=Decimal(1)
    return {"e_folding":float(1/(-(one-m).ln())),
            "P_death_11000":float(1-(one-m)**HOR),
            "mean":float((one-m)/m),
            "median":int(math.ceil(math.log(0.5)/math.log(1.0-muY)))-1}

def comps_scipy(cells):
    n=len(cells)
    if n==0: return []
    rows=[];cols=[]
    for i in range(n):
        for j in range(i+1,n):
            dy=abs(cells[i][0]-cells[j][0]); dy=min(dy,L-dy)
            dx=abs(cells[i][1]-cells[j][1]); dx=min(dx,L-dx)
            if math.hypot(dy,dx)<=CORE_R: rows+=[i,j]; cols+=[j,i]
    g=csr_matrix((np.ones(len(rows)),(rows,cols)),shape=(n,n)) if rows else csr_matrix((n,n))
    k,lab=connected_components(g,directed=False)
    out=collections.defaultdict(list)
    for i,l in enumerate(lab): out[int(l)].append(i)
    return [sorted(v) for _,v in sorted(out.items())]

def cen(cells,idx):
    a=cells[idx[0]]
    oy=[((cells[i][0]-a[0]+L/2)%L)-L/2 for i in idx]; ox=[((cells[i][1]-a[1]+L/2)%L)-L/2 for i in idx]
    return ((a[0]+sum(oy)/len(oy))%L,(a[1]+sum(ox)/len(ox))%L)
def td(a,b):
    dy=abs(a[0]-b[0]); dy=min(dy,L-dy); dx=abs(a[1]-b[1]); dx=min(dx,L-dx); return math.hypot(dy,dx)

def audit(path):
    z=np.load(path,allow_pickle=True); meta=json.loads(str(z["meta"][0]))
    yc=z["ycells"]; yb=z["ybirth"]; yd=z["ydeath"]
    if yc.shape[0]==0: return None
    bs=collections.defaultdict(list); ds=collections.defaultdict(list)
    for r in yb: bs[int(r[0])].append(((int(r[1]),int(r[2])),int(r[3])))
    for r in yd: ds[int(r[0])].append(((int(r[1]),int(r[2])),int(r[3])))
    per=collections.defaultdict(list)
    for r in yc: per[int(r[0])].append(((int(r[1]),int(r[2])),int(r[3])))
    prevC=None; prevT=None; tracks=[]
    for t in sorted(per):
        cells=[c for c,_ in per[t]]; nmap=dict(per[t])
        gs=comps_scipy(cells)
        cur=[(cen(cells,g),[cells[i] for i in g]) for g in gs]
        newT={}
        for j,(cj,clj) in enumerate(cur):
            link=None
            if prevC:
                dd=[td(ci_,cj) for ci_,_ in prevC]
                i=min(range(len(dd)),key=lambda z_:dd[z_])
                if dd[i]<=CORE_R and (len(dd)==1 or sorted(dd)[0]<sorted(dd)[1]):
                    back=[td(prevC[i][0],ck) for ck,_ in cur]
                    j2=min(range(len(back)),key=lambda z_:back[z_])
                    if j2==j and (len(back)==1 or sorted(back)[0]<sorted(back)[1]): link=i
            if link is not None and link in prevT: tk=prevT[link]
            else:
                tk={"start":t,"b":0,"d":0,"minNY":10**9,"maxNY":0,"fb":None,"fd":None}; tracks.append(tk)
            tk["end"]=t
            ny=sum(nmap[c] for c in clj); tk["minNY"]=min(tk["minNY"],ny); tk["maxNY"]=max(tk["maxNY"],ny)
            S=set(clj)
            for c,k in bs.get(t,[]):
                if c in S:
                    tk["b"]+=k
                    if tk["fb"] is None: tk["fb"]=t
            for c,k in ds.get(t,[]):
                if c in S:
                    tk["d"]+=k
                    if tk["fd"] is None: tk["fd"]=t
            newT[j]=tk
        prevC=cur; prevT=newT
    comp=[t for t in tracks if t["b"]>0 and t["d"]>0 and t["minNY"]>=1]
    part=[t for t in tracks if (t["b"]>0)!=(t["d"]>0)]
    return {"tag":meta["tag"],"n_tracks":len(tracks),"complete":len(comp),"partial":len(part),
            "persisted_after_removal":[t["end"]-t["fd"] for t in comp],
            "orderings":["BIRTH_THEN_DEATH" if t["fb"]<t["fd"] else ("DEATH_THEN_BIRTH" if t["fd"]<t["fb"] else "SAME_STEP") for t in comp],
            "yb":int(yb[:,3].sum()) if yb.shape[0] else 0,"yd":int(yd[:,3].sum()) if yd.shape[0] else 0}

def haz_survival(pt,T):
    kY,_=PTS[pt]; vals=[]
    for f in sorted(x for x in os.listdir(PRAW) if "_%s_"%pt in x):
        z=np.load(os.path.join(PRAW,f),allow_pickle=True); yc=z["ycells"]
        acc=Decimal(1); cur=None; prod=Decimal(1)
        st=yc[:,0]; nY=yc[:,3]; nX=yc[:,4]; cd=yc[:,7]
        for i in range(len(st)):
            if st[i]>=T: break
            p=min(1.0,kY*float(nX[i])*float(nY[i]))
            acc*= Decimal(repr(1.0-p))**int(cd[i])
        vals.append(float(acc))
    return 1.0-sum(vals)/len(vals)

def main():
    R={"SECTION":"DOTC01 §17 — one independent zero-run checker","GENERATED_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
       "INDEPENDENCE":{"components":"scipy.sparse.csgraph.connected_components vs union-find",
         "identity_matching":"explicit per-step python mutual-best vs the primary implementation",
         "lifetime_arithmetic":"50-digit Decimal vs IEEE double",
         "birth_survival":"complementary Decimal survival product vs numpy log1p reduceat",
         "imports_from_the_primary_analysis":"none"}}
    R["Y_LIFETIME"]={p:life(PTS[p][1]) for p in PTS}
    R["P_AT_LEAST_ONE_LOCAL_Y_BIRTH_BY_HORIZON"]={p:haz_survival(p,HOR) for p in PTS}
    aud={}
    for pt in ("B1","B2"):
        rows=[audit(os.path.join(PRAW,f)) for f in sorted(x for x in os.listdir(PRAW) if "_%s_"%pt in x)]
        rows=[r for r in rows if r]
        aud[pt]={"n_worlds":len(rows),
          "worlds_with_complete_turnover":sum(1 for r in rows if r["complete"]>0),
          "centres_with_complete_turnover":sum(r["complete"] for r in rows),
          "orderings":dict(collections.Counter(o for r in rows for o in r["orderings"])),
          "worlds_with_persistence_after_removal_gt_0":sum(1 for r in rows if any(x>0 for x in r["persisted_after_removal"])),
          "total_Y_births":sum(r["yb"] for r in rows),"total_Y_deaths":sum(r["yd"] for r in rows)}
        print("  %s checked"%pt,flush=True)
    R["TURNOVER_AUDIT"]=aud
    json.dump(R,open(f"{OUT}/_checkB.json","w"),indent=1)
    print(json.dumps({k:v for k,v in R.items() if k!="INDEPENDENCE"},indent=1))

if __name__=="__main__": main()
