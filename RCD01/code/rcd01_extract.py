"""RCD01 §2 — deterministic, lossless-for-selected-content extraction of the
reproduction-relevant evidence from the FULL six-plane FDFLT01 archives.

This capsule is a SUPPLEMENT to the 92 MB result-bearing core already durable on Tommy's
disk (sha256 936fac7c7d61df1a1bedf2d94e5e933930aa55f66de2e057e41202b467f04467), which
already carries scalars, ycells, ybirth, ydeath, yhop, xevent, capacity, exchange, src,
final, meta and the X plane at every step. What the core lacks, and what reproduction
questions need, is the SOURCE-CELL STATE: the SX/SY/WX/WY occupancy at every Y-occupied
cell at every step. Without it neither the X birth probability min(1, kX*nX*nY) nor the
X candidate pool min(nSX, free) can be evaluated at the cells where X is actually born.

Together the core and this supplement are analysis-sufficient for RCD01 and its successor.
"""
from __future__ import annotations
import hashlib, io, json, os, sys, tarfile, time
import numpy as np, yaml
import zstandard as zstd

REPO="/home/claude/edl"; RAW="/home/claude/FDFLT01/raw"; OUT=f"{REPO}/RCD01/out"
P=yaml.safe_load(open(f"{REPO}/OBTC02/code/obtc02_protocol.yaml"))
L=int(P["point"]["L"]); CORE_R=float(P["analytic"]["core_radius_cells"])
CAP=int(P["point"]["CAP"]); KX=float(P["point"]["kX"])
SPECIES=("X","Y","SX","SY","WX","WY")          # plane order, from pqec01_observer.SPECIES
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda: f.read(1<<20), b""): h.update(b)
    return h.hexdigest()

def centres(cells):
    """Toroidal single-linkage over Y cells, adjacency <= CORE_R. Returns a label per cell."""
    n=len(cells)
    if n==0: return []
    par=list(range(n))
    def f(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    for i in range(n):
        for j in range(i+1,n):
            dy=abs(cells[i][0]-cells[j][0]); dx=abs(cells[i][1]-cells[j][1])
            dy,dx=min(dy,L-dy),min(dx,L-dx)
            if (dy*dy+dx*dx)**0.5<=CORE_R:
                a,b=f(i),f(j)
                if a!=b: par[a]=b
    roots={}
    out=[]
    for i in range(n):
        r=f(i)
        if r not in roots: roots[r]=len(roots)
        out.append(roots[r])
    return out

def extract_world(path):
    """Deterministic extraction. Returns (npz_bytes, provenance_record)."""
    src_sha=sha_file(path)
    z=np.load(path,allow_pickle=True)
    m=json.loads(str(z["meta"][0]))
    f0=z["field0"].astype(np.int32); dd=z["field_delta"]
    T=int(z["scalars"].shape[0])
    # full six-plane reconstruction, exactly as the PQEC01 review code does it
    F=np.empty((dd.shape[0]+1,)+f0.shape,np.int16); F[0]=f0
    np.cumsum(dd.astype(np.int16),axis=0,out=F[1:]); F[1:]+=f0.astype(np.int16)
    occ=F.sum(axis=1).astype(np.int32)                       # total occupancy per cell
    free=CAP-occ
    yc=np.asarray(z["ycells"])
    t=yc[:,0].astype(np.int64); y=yc[:,1].astype(np.int64); x=yc[:,2].astype(np.int64)
    # SOURCE-CELL STATE: every occupied Y cell, every step, all six species plus free
    rows=np.empty((len(t),11),np.int32)
    rows[:,0]=t; rows[:,1]=y; rows[:,2]=x
    for k,s in enumerate(SPECIES):
        rows[:,3+k]=F[t,k,y,x]
    rows[:,9]=np.maximum(free[t,y,x],0)
    # centre label per Y-cell row, from the frozen single-linkage rule
    lab=np.zeros(len(t),np.int32)
    order=np.argsort(t,kind="stable")
    i=0
    while i<len(order):
        j=i
        while j<len(order) and t[order[j]]==t[order[i]]: j+=1
        idx=order[i:j]
        cs=[(int(y[k]),int(x[k])) for k in idx]
        for kk,lb in zip(idx,centres(cs)): lab[kk]=lb
        i=j
    rows[:,10]=lab
    # derived per-cell quantities are NOT stored: they are exact functions of the above
    buf=io.BytesIO()
    np.savez_compressed(buf,
        source_cell_state=rows,
        source_cell_columns=np.array(["step","y","x","nX","nY","nSX","nSY","nWX","nWY","free","centre_label"]),
        xevent=z["xevent"], ybirth=z["ybirth"], ydeath=z["ydeath"],
        n_X_total=F[:,0].sum(axis=(1,2)).astype(np.int64),
        meta=z["meta"])
    b=buf.getvalue()
    prov={"world":m["tag"],"seed":m["seed"],
          "source_raw_archive":os.path.basename(path),
          "source_raw_archive_sha256":src_sha,
          "source_key":["field0","field_delta","ycells","xevent","ybirth","ydeath","scalars","meta"],
          "source_slice_rule":("full six-plane field reconstructed as F[0]=field0, "
            "F[1:]=cumsum(field_delta)+field0 in int16; rows are taken at exactly the "
            "(step,y,x) triples listed in ycells, in ycells order; centre_label is the "
            "frozen toroidal single-linkage partition of the Y-occupied cells of that step"),
          "n_source_cell_rows":int(len(t)),"steps":T,
          "extracted_sha256":sha_bytes(b),"extracted_bytes":len(b)}
    z.close()
    return b,prov

if __name__=="__main__":
    t0=time.time()
    code_sha=sha_file(os.path.abspath(__file__))
    paths=sorted(f"{RAW}/{f}" for f in os.listdir(RAW) if f.endswith(".npz"))
    out=f"/home/claude/RCD01/RCD01_REPRODUCTION_EVIDENCE_CORE.tar.zst"
    os.makedirs("/home/claude/RCD01",exist_ok=True)
    provs=[]
    with open(out,"wb") as fh, zstd.ZstdCompressor(level=10,threads=-1).stream_writer(fh) as z:
        with tarfile.open(fileobj=z,mode="w|") as tf:
            for p in paths:
                b,pr=extract_world(p); pr["extraction_code_sha256"]=code_sha
                ti=tarfile.TarInfo("RCD01/evidence/"+os.path.basename(p)); ti.size=len(b)
                tf.addfile(ti,io.BytesIO(b)); provs.append(pr)
    n=os.path.getsize(out)
    MAN={"SECTION":"RCD01 §2 — reproduction evidence manifest",
     "CAPSULE":"RCD01_REPRODUCTION_EVIDENCE_CORE.tar.zst","bytes":n,"sha256":sha_file(out),
     "N_WORLDS":len(provs),
     "RELATION_TO_THE_EXISTING_CORE":("this is a SUPPLEMENT to FDFLT01_RAW_CORE.tar.zst "
       "(sha256 936fac7c7d61df1a1bedf2d94e5e933930aa55f66de2e057e41202b467f04467, already "
       "durable on the Windows disk), which carries the X plane at every step and every "
       "non-field array. Together they are analysis-sufficient."),
     "WHAT_THIS_ADDS":("the six-species occupancy and the free capacity at EVERY Y-occupied "
       "cell at EVERY step, plus the frozen centre label of that cell. This is what makes the "
       "X birth probability min(1, kX*nX*nY) and the X candidate pool min(nSX, free) evaluable "
       "at the cells where X is actually produced."),
     "EXTRACTION_IS_DETERMINISTIC":True,
     "EXTRACTION_CODE_SHA256":code_sha,
     "NO_FIELD_INVENTED":"every stored column is read directly from the reconstructed archive; no value is modelled or imputed",
     "WORLDS":provs}
    json.dump(MAN,open(f"{OUT}/RCD01_REPRODUCTION_EVIDENCE_MANIFEST.json","w"),indent=2)
    print("capsule %d bytes = %.1f MB in %.0fs  worlds=%d"%(n,n/1e6,time.time()-t0,len(provs)))
    print("sha256:",MAN["sha256"])
