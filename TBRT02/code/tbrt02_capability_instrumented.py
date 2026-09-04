"""F10 verified independently: does the frozen branch's CERTAIN set actually meet DESC?"""
import sys, os, json, random
sys.path.insert(0, "/home/claude/edl/CLEA01/code")
import clea01_lineage_i1 as MC
L, sources, OFFSETS = MC.L, MC.sources, MC.OFFSETS
SEP = 2
def cheb(a,b):
    return max(min((a[0]-b[0])%L,(b[0]-a[0])%L), min((a[1]-b[1])%L,(b[1]-a[1])%L))
def nbrs(c):
    return {((c[0]+dy)%L,(c[1]+dx)%L) for dy,dx in OFFSETS}
rng=random.Random(20260828)
both=0; adjrows=0; adjworlds=0; surv=[]; maxsz=[]
for _ in range(4000):
    d_root=(rng.randrange(L),rng.randrange(L))
    while True:
        c_root=(rng.randrange(L),rng.randrange(L))
        if cheb(c_root,d_root)>=SEP: break
    prev={d_root:1,c_root:1}; daughter={d_root}; desc={c_root}
    alive=0; mx=1; adj_here=0
    for t in range(60):
        n=max(1,int(0.02*L*L)); cur={}
        seeds=list(daughter|desc) or [d_root,c_root]
        for _ in range(n):
            sy,sx=seeds[rng.randrange(len(seeds))]
            cur[((sy+rng.randint(-1,1))%L,(sx+rng.randint(-1,1))%L)]=1
        nd,nc=set(),set()
        for cell in cur:
            S=sources(cell,prev)
            if not S: continue
            if daughter and S<=daughter: nd.add(cell)
            if S&desc: nc.add(cell)
        daughter,desc=nd,nc
        if daughter and desc:
            both+=1
            mx=max(mx,len(daughter))
            if any(nbrs(c)&desc for c in daughter): adjrows+=1; adj_here+=1
        if daughter: alive=t+1
        if not daughter and not desc: break
        prev=cur
    surv.append(alive); maxsz.append(mx)
    if adj_here: adjworlds+=1
surv.sort(); maxsz.sort()
print(json.dumps({"rows_both_sets_alive":both,"rows_CERTAIN_adjacent_to_DESC":adjrows,
 "worlds_with_adjacency":adjworlds,"CERTAIN_survival_steps_median":surv[len(surv)//2],
 "CERTAIN_survival_steps_mean":round(sum(surv)/len(surv),1),
 "CERTAIN_max_size_median":maxsz[len(maxsz)//2]},indent=1))
