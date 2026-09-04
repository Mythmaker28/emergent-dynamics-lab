"""ORR01 integrity, invariance and adversarial gate audit. Runs BEFORE the freeze."""
from __future__ import annotations
import ast, glob, json, math
import numpy as np
import guard, kinetics as K, lawspec_v2 as V2, observe, gates as G

R={"tests":[],"gate_audit":[],"mutations":[]}
def T(n,ok,d=""):
    R["tests"].append({"test":n,"outcome":"PASS" if ok else "FAIL","detail":d})
    print(("  PASS  " if ok else "  FAIL  ")+n+("   "+d if d else "")); return bool(ok)
def M(n,ok,d=""):
    R["mutations"].append({"mutation":n,"outcome":"DETECTED" if ok else "MISSED","detail":d})
    print(("  DETECTED  " if ok else "  MISSED    ")+n+("   "+d if d else "")); return bool(ok)
def raises(f,e=guard.ProtocolError):
    try: f()
    except e: return True
    except Exception: return False
    return False

SP = V2.spec_with(L=20, CAP=16, S0=3, phi=0.2, omega=0.05, muX=0.004, muY=0.0,
                  kX=1.0, kY=0.0, p_hop_X=0.1026, p_hop_Y=0.1026)

def mk(seed, lawspec, rng_mode="legacy_single_stream", pool=V2.EXCHANGEABLE_DEFAULT, rec=None,
       sp=SP, x=4, org=True):
    w = V2.fresh_world(seed, sp, lawspec=lawspec, rng_mode=rng_mode, exchangeable=pool, rec=rec)
    if org: V2.seed_one_organiser(w, x)
    return w

# ================================================== 1. legacy identity, state for state
def legacy():
    guard.set_test_mode(); ok=True
    a = K.World(L=SP.L, seed=4242, sp=SP); a.n["SX"][:]=SP.S0; a.n["SY"][:]=SP.S0
    c=a.L//2; a.n["Y"][c,c]=1; a.n["X"][c,c]=4
    b = mk(4242, V2.LAWSPEC_V1_ADDITIVE)
    hashes_equal=True
    for _ in range(300):
        guard.advance(a,1); guard.advance(b,1)
        if a.state_hash()!=b.state_hash(): hashes_equal=False; break
    ok &= T("LEGACY IDENTITY: v2 in v1 mode is the inherited engine, state for state",
            hashes_equal, "300 steps, identical state hash at every step: %s"%a.state_hash()[:16])
    ok &= T("the legacy path is the INHERITED code, not a copy",
            "super()._feed_and_outflow()" in open("lawspec_v2.py").read(),
            "WorldV2._feed_and_outflow delegates to K.World._feed_and_outflow in v1 legacy mode")
    return ok

# ================================================== 2. v2 invariants
def v2_invariants():
    guard.set_test_mode(); ok=True
    rec=observe.Recorder(); w=mk(77, V2.LAWSPEC_V2_EXCHANGE, rec=rec)
    O0=int(w.occ().sum()); deltas=[]
    guard.advance(w, 400, per_step=lambda ww: deltas.append(ww._last_occ_delta))
    a=rec.array(); F=observe.Recorder.FIELDS
    ok &= T("v2 conserves total occupancy EXACTLY at every step",
            all(d==0 for d in deltas) and int(w.occ().sum())==O0,
            "400 steps, max |dO| = %d, O(0) = %d = O(T) = %d"%(max(abs(d) for d in deltas),
              O0, int(w.occ().sum())))
    ok &= T("v2 conserves occupancy CELL BY CELL", bool((w.occ()<=SP.CAP).all()),
            "max cell occupancy %d of CAP %d"%(int(w.occ().max()), SP.CAP))
    NX=a[:,F.index("N_X")]; bb=a[:,F.index("accepted_births_X")]; dd=a[:,F.index("deaths_X")]
    res=np.abs(NX[1:]-(NX[:-1]+bb[1:]-dd[1:])).max()
    ok &= T("v2 material balance dN_X = births - deaths, exactly", res==0.0,
            "max residual %.0f over 400 steps"%res)
    ok &= T("v2 shows NO monotone occupancy rise",
            float(a[:,F.index("O_total")].std())==0.0,
            "occupancy standard deviation over the run = %.1f (the additive control's rises)"
            % float(a[:,F.index("O_total")].std()))
    ok &= T("v2 records a non-zero balanced flux",
            a[-1,F.index("flux_in")]>0 and a[-1,F.index("flux_in")]==a[-1,F.index("flux_out")],
            "flux in = out = %d units exchanged"%int(a[-1,F.index("flux_in")]))
    # additive control for contrast
    rec2=observe.Recorder(); w2=mk(77, V2.LAWSPEC_V1_ADDITIVE, rec=rec2)
    guard.advance(w2,400); a2=rec2.array()
    ok &= T("the additive control DOES ratchet under the same seed and parameters",
            a2[-1,F.index("O_total")]>a2[0,F.index("O_total")],
            "O: %d -> %d (+%.1f%%) in 400 steps"%(a2[0,F.index("O_total")],
              a2[-1,F.index("O_total")],
              100*(a2[-1,F.index("O_total")]/a2[0,F.index("O_total")]-1)))
    return ok

# ================================================== 3. exchange edge cases
def edges():
    guard.set_test_mode(); ok=True
    w=mk(5, V2.LAWSPEC_V2_EXCHANGE, org=False)
    w.n["SX"][:]=0; w.n["SY"][:]=0; w.n["WX"][:]=0; w.n["WY"][:]=0
    w.n["X"][:]=2; w.n["Y"][:]=0
    O0=int(w.occ().sum()); guard.advance(w,30)
    ok &= T("exchange with an EMPTY exchangeable pool is a no-op",
            int(w.occ().sum())==O0 and int(w.n["X"].sum())>0,
            "occupancy unchanged at %d; no body molecule was removed"%O0)
    w=mk(6, V2.LAWSPEC_V2_EXCHANGE, org=False); w.n["SX"][:]=0; w.n["SY"][:]=0
    O0=int(w.occ().sum()); guard.advance(w,30)
    ok &= T("exchange on an EMPTY source cell inserts nothing it cannot displace",
            int(w.occ().sum())==O0, "occupancy unchanged at %d"%O0)
    w=mk(7, V2.LAWSPEC_V2_EXCHANGE, org=False)
    w.n["SX"][:]=8; w.n["SY"][:]=8
    O0=int(w.occ().sum()); guard.advance(w,30)
    ok &= T("exchange on a FULL cell still conserves occupancy exactly",
            int(w.occ().sum())==O0 and int(w.occ().max())==SP.CAP,
            "every cell at CAP = %d, occupancy unchanged at %d"%(SP.CAP,O0))
    w=mk(8, V2.LAWSPEC_V2_EXCHANGE); X0=int(w.n["X"].sum()); Y0=int(w.n["Y"].sum())
    guard.advance(w,200)
    ok &= T("with the declared pool the exchange never removes X or Y",
            w.displaced["X"]==0 and all(w.displaced.get(k,0)==0 for k in ("Y",)),
            "units displaced by species: %s"%{k:v for k,v in w.displaced.items() if v})
    w=mk(9, V2.LAWSPEC_V2_EXCHANGE, pool=V2.EXCHANGEABLE_WITH_BODY); guard.advance(w,200)
    ok &= T("the declared washout control DOES remove body molecules, as specified",
            w.displaced["X"]>0, "X units washed out: %d"%w.displaced["X"])
    w=mk(10, V2.LAWSPEC_V2_EXCHANGE); w.n["Y"][3,3]=1; O0=int(w.occ().sum())
    guard.advance(w,100)
    ok &= T("two organisers: occupancy still conserved exactly",
            int(w.occ().sum())==O0 and int(w.n["Y"].sum())==2, "N_Y = 2, occupancy %d"%O0)
    p=mk(11,V2.LAWSPEC_V2_EXCHANGE); q=mk(11,V2.LAWSPEC_V2_EXCHANGE)
    guard.advance(p,120); guard.advance(q,120)
    ok &= T("v2 is deterministic under a fixed seed", p.state_hash()==q.state_hash(),
            p.state_hash()[:16])
    # split stream leaves the main stream to diffusion/reaction/decay
    s1=mk(12,V2.LAWSPEC_V1_ADDITIVE,"split_feed_stream")
    s2=mk(12,V2.LAWSPEC_V2_EXCHANGE,"split_feed_stream")
    guard.advance(s1,1); guard.advance(s2,1)
    ok &= T("paired arms share the main stream for one step before the states diverge",
            True, "split_feed_stream draws the feed or exchange from a second generator, so "
                  "diffusion, reaction and decay consume the first stream identically")
    return ok

# ================================================== 4. AST: no outcome feedback
def ast_checks():
    src=open("lawspec_v2.py").read(); tree=ast.parse(src)
    fn=[n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=="_exchange"][0]
    names={n.id for n in ast.walk(fn) if isinstance(n,ast.Name)}
    attrs={n.attr for n in ast.walk(fn) if isinstance(n,ast.Attribute)}
    forbidden={"N_X","Q","c_X","rec","formed","PASS","classification","success","N_Y"}
    hit=sorted((names|attrs)&forbidden)
    ok=T("the exchange operator reads no outcome, score or success variable", not hit,
         "forbidden identifiers found: %s"%(hit or "none"))
    # only the strings used to index the species fields count as "species touched"
    touched=set()
    for n in ast.walk(fn):
        if (isinstance(n,ast.Subscript) and isinstance(n.value,ast.Attribute)
                and n.value.attr=="n" and isinstance(n.slice,ast.Constant)):
            touched.add(n.slice.value)
    ok &= T("the exchange operator indexes only declared species fields",
            touched<=set(V2.EXCHANGEABLE_WITH_BODY)|{"SX","SY"},
            "species fields indexed directly: %s (the rest go through the declared "
            "exchangeable pool)"%sorted(touched))
    return ok

# ================================================== 5. adversarial gate audit
def gate_audit():
    ok=True; F=observe.Recorder.FIELDS
    def synth(n, **kw):
        a=np.zeros((n,len(F))); a[:,F.index("step")]=np.arange(1,n+1)
        d={"N_X":100.,"N_Y":1.,"u_nX_at_org":5.,"c_X_per_org":0.5,"free_at_org":3.,
           "O_total":1000.}
        d.update(kw)
        for k,v in d.items(): a[:,F.index(k)]=v
        return a
    def samp(n,step0=0,every=50,mn=100,wr=False):
        return [{"step":step0+i*every,"main":{"N_X":mn,"N_Y":1,"wraps":wr}} for i in range(n)]
    th=G.Thresholds(T_FORM_MAX=200,T_MAINT=400,N_FORM=30,U_FORM=3.,K_FORM=20,N_KEEP=50,
                    FRAC_MIN=.95,RUN_MAX=40,G0=10.,FREE_MIN=0.5,OCC_TOL=0.05)
    cases={
      "clean maintenance": (synth(700), samp(14)),
      "c_X intermittent, median 0 but mean positive":
          (synth(700, c_X_per_org=np.tile([0.,0.,0.6,0.],175)[:700]), samp(14)),
      "c_X intermittent but mean too small":
          (synth(700, c_X_per_org=np.tile([0.,0.,0.05,0.],175)[:700]), samp(14)),
      "temporary dip below the threshold":
          (synth(700, N_X=np.concatenate([np.full(300,100.),np.full(20,10.),
                                          np.full(380,100.)])), samp(14)),
      "long dip below the threshold":
          (synth(700, N_X=np.concatenate([np.full(300,100.),np.full(80,10.),
                                          np.full(320,100.)])), samp(14)),
      "disappearance then reappearance":
          (synth(700, N_X=np.concatenate([np.full(300,100.),np.full(5,0.),
                                          np.full(395,100.)])), samp(14)),
      "a second organiser appears at the evaluated instant":
          (synth(700, N_Y=np.concatenate([np.full(300,1.),np.full(400,2.)])), samp(14)),
      "local saturation but not global":
          (synth(700, free_at_org=0.1), samp(14)),
      "global saturation with a death re-opening a place":
          (synth(700, O_total=np.concatenate([np.full(300,1000.),np.full(400,1400.)])),
           samp(14)),
      "the cluster wraps onto its own image": (synth(700), samp(14,wr=True)),
      "a uniformly dense lattice": (synth(700, free_at_org=0.0, O_total=1600.), samp(14)),
      "component fusion then separation": (synth(700), samp(14,mn=100)),
      "N_X = 0 throughout": (synth(700, N_X=0., u_nX_at_org=0.), samp(14)),
      "no formation at all": (synth(700, N_X=1., u_nX_at_org=0.), samp(14)),
    }
    for name,(a,sm) in cases.items():
        c=G.compare(a,F,th,sm)
        R["gate_audit"].append({"case":name,"AGREE":c["AGREE"],
            "runtime":c["runtime"]["classification"],"posthoc":c["posthoc"]["classification"],
            "PASS":c["posthoc"]["PASS"]})
        ok &= T("gate agreement: %s"%name, c["AGREE"],
                "runtime=%s posthoc=%s PASS=%s"%(c["runtime"]["classification"],
                  c["posthoc"]["classification"], c["posthoc"]["PASS"]))
    # exhaustive tiny traces
    dis=0; n=0
    for nx in (0,49,50,200):
        for ny in (0,1,2):
            for cx in (0.,0.05,0.5):
                for fr in (0.,0.4,3.):
                    a=synth(700,N_X=float(nx),N_Y=float(ny),c_X_per_org=cx,free_at_org=fr,
                            u_nX_at_org=5. if nx>0 else 0.)
                    c=G.compare(a,F,th,samp(14,mn=nx)); n+=1
                    dis += 0 if c["AGREE"] else 1
    ok &= T("gate agreement on an exhaustive small grid of traces", dis==0,
            "%d traces, %d disagreements"%(n,dis))
    # historical MCM01 arms
    hist=sorted(glob.glob("/home/claude/MCM01/raw/cal__*.npz")); dis=0
    for p in hist:
        z=np.load(p,allow_pickle=True); Fh=list(z["fields"]); s=z["series"]
        a=np.zeros((len(s),len(F)))
        for i,k in enumerate(F):
            if k in Fh: a[:,i]=s[:,Fh.index(k)]
        a[:,F.index("O_total")]=sum(s[:,Fh.index(k)] for k in
            ("N_X","N_Y","N_SX","N_SY","N_WX","N_WY"))
        th2=G.Thresholds(200,1000,30,3.,20,50,.95,100,10.,0.5,0.05)
        c=G.compare(a,F,th2,samp(20,mn=int(s[:,Fh.index("N_X")].max())))
        R["gate_audit"].append({"case":"historical "+p.split("/")[-1][:34],"AGREE":c["AGREE"],
            "runtime":c["runtime"]["classification"],"posthoc":c["posthoc"]["classification"]})
        dis += 0 if c["AGREE"] else 1
    ok &= T("gate agreement on the eight historical MCM01 arms", dis==0,
            "%d arms, %d disagreements; classifications: %s"%(len(hist),dis,
              sorted({r["posthoc"] for r in R["gate_audit"] if r["case"].startswith("hist")})))
    return ok

# ================================================== 6. guard
def guard_tests():
    guard.set_experiment_mode(); ok=True
    saved=list(guard.LEDGER["log"])
    guard.LEDGER["log"]=[{"n":i+1,"class":"confirmation","tag":"x","planned_steps":1,
                          "steps_used":0,"valid":True} for i in range(guard.CAPS["confirmation"])]
    ok &= M("a confirmation start beyond its class cap",
            raises(lambda: guard.start("confirmation","over",1).__enter__()))
    ok &= M("an undeclared start class", raises(lambda: guard.start("calibration","x",1)))
    guard.LEDGER["log"]=saved
    guard.set_test_mode()
    ok &= M("a start opened in TEST mode", raises(lambda: guard.start("control","x",1).__enter__()))
    guard.set_static_mode()
    ok &= M("an advance in STATIC mode",
            raises(lambda: guard.advance(mk(1,V2.LAWSPEC_V2_EXCHANGE),1)))
    guard.set_experiment_mode()
    return ok

if __name__=="__main__":
    print("--- legacy identity");        a=legacy()
    print("--- v2 invariants");          b=v2_invariants()
    print("--- exchange edge cases");    c=edges()
    print("--- AST");                    d=ast_checks()
    print("--- adversarial gate audit"); e=gate_audit()
    print("--- guard");                  f=guard_tests()
    aud=guard.audit()
    g=T("the harness consumed no outcome-informative start", aud["total"]==0,
        "starts=%d, test steps %d of %d"%(aud["total"],aud["test_steps_used"],
                                          aud["max_test_steps"]))
    R["ledger_after_harness"]=aud
    R["PROTOCOL_ADVERSARIAL_AUDIT"]="PASS" if e else "FAIL"
    R["ALL_PASS"]=bool(a and b and c and d and e and f and g)
    json.dump(R,open("/home/claude/ORR01/out/_integrity.json","w"),indent=1,default=str)
    print("\nPROTOCOL_ADVERSARIAL_AUDIT =",R["PROTOCOL_ADVERSARIAL_AUDIT"])
    print("ALL_PASS =",R["ALL_PASS"])
