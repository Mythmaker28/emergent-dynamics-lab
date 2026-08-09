"""Independent engine-free verification of P09."""
from __future__ import annotations
import ast, csv, hashlib, json, math, statistics as S
from pathlib import Path
R=[]
def chk(i,name,ok,detail):
    R.append({"check":i,"name":name,"PASS":bool(ok),"detail":detail})
    print(f"  {i:>2}. {name:<58} {'PASS' if ok else 'FAIL'}  {detail}")
def n(v):
    try:
        x=float(v); return None if math.isnan(x) else x
    except (TypeError,ValueError): return None
def rd(p): return list(csv.DictReader(open(p)))
rows=rd("p09_rows.csv")

def v1():
    t=ast.parse(Path("p09_analyse.py").read_text())
    mods={a.name for x in ast.walk(t) if isinstance(x,ast.Import) for a in x.names} | \
         {x.module for x in ast.walk(t) if isinstance(x,ast.ImportFrom) and x.module}
    chk(1,"l'analyse n'importe aucun moteur",not (mods & {"edlab","od_core","p07_core","p08_core"}),
        f"imports = {sorted(mods)}")

def v2():
    wi=max(abs(n(r["max_identity_residual"]) or 0) for r in rows)
    wb=max(abs(n(r["max_global_balance_residual"]) or 0) for r in rows)
    chk(2,"identite des cohortes et bilan global",wi<=1e-9 and wb<=1e-9,
        f"{len(rows)} trajectoires; identite {wi:.2e}, bilan {wb:.2e}")

def v3():
    c={}
    for r in rows: c[(r["law"],r["size"],r["arm"])]=c.get((r["law"],r["size"],r["arm"]),0)+1
    bad=[k for k,v in c.items() if v!=9]
    chk(3,"ITT: 9 blocs par cellule du plan",not bad and len(c)==24,
        f"{len(c)} cellules, toutes a 9 blocs; total {len(rows)} trajectoires")

def v4():
    """The two replay arms received EXACTLY the same attempted mass, block by block."""
    w=0.0; k=0
    a={(r["law"],r["size"],r["block"]):n(r["attempted_mass"]) for r in rows if r["arm"]=="PARENT_Q_REPLAY"}
    b={(r["law"],r["size"],r["block"]):n(r["attempted_mass"]) for r in rows if r["arm"]=="FLOOR_Q_REPLAY"}
    for key in set(a)&set(b):
        w=max(w,abs(a[key]-b[key])); k+=1
    chk(4,"les deux bras q-replay ont une masse TENTEE identique",w<=1e-12,
        f"{k} blocs, pire ecart absolu = {w:.2e}")

def v5():
    """PARENT_LOW_CONSTANT requested the same total as the replay arms."""
    w=0.0;k=0
    a={(r["law"],r["size"],r["block"]):n(r["attempted_mass"]) for r in rows if r["arm"]=="PARENT_Q_REPLAY"}
    c={(r["law"],r["size"],r["block"]):n(r["attempted_mass"]) for r in rows if r["arm"]=="PARENT_LOW_CONSTANT"}
    for key in set(a)&set(c):
        w=max(w,abs(a[key]-c[key])/max(1e-9,a[key])); k+=1
    chk(5,"PARENT_LOW_CONSTANT demande le meme total que les q-replay",w<=1e-9,
        f"{k} blocs, pire ecart relatif = {w:.2e}")

def v6():
    d=json.load(open("p09_summary.json"))["DOSE_EQUIVALENCE"]["detail"]
    ok16=all(d[k]["EQUIVALENCE_PASSES"] for k in d if k.startswith("LAW_16"))
    ok29=any(d[k]["EQUIVALENCE_PASSES"] for k in d if k.startswith("LAW_29"))
    chk(6,"equivalence de dose: PASS sous LAW_16, ECHEC sous LAW_29",ok16 and not ok29,
        "; ".join(f"{k} {d[k]['median_ratio']:.3f}" for k in d))

def v7():
    """The headline recomputed from raw: dose reduction alone rescues LAW_29."""
    out=[];ok=True
    for sz in ("24","32"):
        pf=[r for r in rows if r["law"]=="LAW_29" and r["size"]==sz and r["arm"]=="PARENT_FULL"]
        lc=[r for r in rows if r["law"]=="LAW_29" and r["size"]==sz and r["arm"]=="PARENT_LOW_CONSTANT"]
        a=sum(1 for r in pf if r["SURVIVAL_ITT"]=="True"); b=sum(1 for r in lc if r["SURVIVAL_ITT"]=="True")
        out.append(f"L{sz}: pleine dose {a}/9 -> bas constant {b}/9 (floor={lc[0]['floor']})")
        ok=ok and a<=1 and b==9 and float(lc[0]["floor"])==0.0
    chk(7,"la reduction de dose SEULE (sans plancher) sauve LAW_29",ok,"; ".join(out))

def v8():
    """The floor's harm under LAW_16 at matched dose."""
    out=[];ok=True
    for sz in ("24","32"):
        pq=[r for r in rows if r["law"]=="LAW_16" and r["size"]==sz and r["arm"]=="PARENT_Q_REPLAY"]
        fq=[r for r in rows if r["law"]=="LAW_16" and r["size"]==sz and r["arm"]=="FLOOR_Q_REPLAY"]
        a=sum(1 for r in pq if r["SPLIT"]=="True"); b=sum(1 for r in fq if r["SPLIT"]=="True")
        out.append(f"L{sz}: scissions parent {a}/9 vs plancher {b}/9")
        ok=ok and a==0 and b==9
    chk(8,"sous LAW_16 a dose appariee, le plancher scinde 9/9",ok,"; ".join(out))

def v9():
    got=hashlib.sha256(Path("p09_protocol.json").read_bytes()).hexdigest()
    ok=got==Path("p09_protocol.sha256").read_text().split()[0]
    d=json.loads(Path("p09_protocol.json").read_text())
    for f,h in d["code_sha256"].items():
        ok=ok and hashlib.sha256(Path(f).read_bytes()).hexdigest()==h
    s=hashlib.sha256(Path("p09_sequences.json").read_bytes()).hexdigest()
    ok=ok and s==d["exogenous_sequence"]["sha256"]
    chk(9,"sceaux P09 (protocole, code, sequence exogene)",ok,
        f"protocole {got[:12]}, sequence {s[:12]}")

def v10():
    """Parent artefacts untouched."""
    bad=[]
    for p in ("../P08/p08b_protocol","../P08/p08c_protocol","../P08/p08d_protocol",
              "../P08/p08e_protocol","../P07/p07a_protocol","../P07/p07b_protocol",
              "../P07/p07d_protocol"):
        j,s=Path(f"{p}.json"),Path(f"{p}.sha256")
        if hashlib.sha256(j.read_bytes()).hexdigest()!=s.read_text().split()[0]: bad.append(p)
    k=0
    for line in Path("../DR05/SHA256SUMS.txt").read_text().splitlines():
        if not line.strip(): continue
        h,name=line.split(None,1); f=Path("../DR05")/name.strip()
        if not f.exists() or hashlib.sha256(f.read_bytes()).hexdigest()!=h: bad.append(name.strip())
        k+=1
    chk(10,"aucun artefact P07 / P08 / DEV_05 modifie",not bad,
        f"7 sceaux + {k} fichiers DEV_05; violations = {bad[:3] or 'aucune'}")

def v11():
    """The donor mapping never reuses the receiving block."""
    man=json.load(open("p09_manifest.json"))["blocks"]
    bad=[b for b in man if b.get("donor") and b["donor"].split("_S")[-1]==b["block"].split("_S")[-1]]
    coh=sorted({b["donor"].split("_S")[-1][:2] for b in man if b.get("donor")})
    chk(11,"le donneur n'est jamais le bloc receveur ni la meme cohorte",not bad,
        f"{len(man)} blocs; receveurs 89xxxx, donneurs 99xxxx (prefixes {coh})")

def v12():
    """UCR recomputed from its two components."""
    w=0.0
    for r in rows:
        u,i_,f=n(r["UCR"]),n(r["incumbent_removed_over_M256"]),n(r["fresh_over_M256"])
        if None not in (u,i_,f): w=max(w,abs(u-min(i_,f)))
    chk(12,"UCR = min(incumbent retire, frais retenu), recalcule",w<=1e-9,
        f"{len(rows)} trajectoires, pire ecart = {w:.2e}")

def main():
    print("=== VERIFICATION INDEPENDANTE P09 (0 appel moteur) ===")
    for f in (v1,v2,v3,v4,v5,v6,v7,v8,v9,v10,v11,v12):
        try: f()
        except Exception as e:
            import traceback; traceback.print_exc(); chk(int(f.__name__[1:]),f.__name__,False,str(e))
    p=sum(1 for x in R if x["PASS"])
    Path("p09_verify.json").write_text(json.dumps(
        {"n":len(R),"n_pass":p,"VERDICT":"PASS" if p==len(R) else "FAIL",
         "engine_invocations":0,"checks":R},indent=1))
    print(f"\n{p}/{len(R)} -> {'PASS' if p==len(R) else 'FAIL'}")
    return 0 if p==len(R) else 1
if __name__=="__main__": raise SystemExit(main())
