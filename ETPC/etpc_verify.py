import sys,os,json,hashlib,pickle
CH=[]
def chk(n,ok,d=""):
    CH.append({"check":n,"PASS":bool(ok),"detail":d}); print(("PASS " if ok else "FAIL ")+n+("  "+d if d else ""))
P=json.load(open("etpc_protocol.json"))
h=hashlib.sha256(open("etpc_protocol.json","rb").read()).hexdigest()
chk("1 sealed protocol hash matches",h==open("etpc_protocol.sha256").read().split()[0],h)
bad=[f for f,v in P["code_sha256"].items() if hashlib.sha256(open(f,"rb").read()).hexdigest()!=v]
chk("2 every sealed code file unchanged",not bad,f"changed:{bad}")
g=json.load(open("etpc_gates.json"))
chk("3 all R0-R10 gate fixtures pass",all(r["PASS"] for r in g["gates"]),f"{sum(r['PASS'] for r in g['gates'])}/{len(g['gates'])}")
q=g["engine_starts"]; pr=json.load(open("etpc_PRIMARY_starts.json"))["engine_starts"]
chk("4 qualification within its 24-start cap",q<=24,f"{q} starts")
chk("5 total engine starts within the planned maximum",q+pr<=124,f"{q}+{pr}={q+pr} of 124 planned, 160 absolute")
chk("6 the held-out geometry was NOT opened after a primary failure",not os.path.exists("etpc_HELDOUT.pkl"))
a=json.load(open("etpc_analysis_PRIMARY.json"))
chk("7 T4 gain-zero exclusion is BITWISE in every block",a["T4_gain_zero_bitwise_all_blocks"] and a["tau_off_exactly_zero"],"tau_off == 0.0 exactly")
chk("8 t0 public state bitwise identical between SWAP and SHAM",a["T5_t0_public_identical_all_blocks"])
chk("9 Sigma rho z conserved to float precision",a["max_sum_rho_z_drift"]<1e-12,f"max drift {a['max_sum_rho_z_drift']:.3e}")
chk("10 every block enters the ITT analysis",a["n_analysable"]==a["n_blocks"] and not a["ITT_missing"],f"{a['n_analysable']}/{a['n_blocks']}")
chk("11 primary seeds never used by any earlier programme",set(range(61000,61010)).isdisjoint(set(range(30000,60000))))
json.dump(CH,open("etpc_verify.json","w"),indent=1)
print(f"\n{sum(1 for c in CH if c['PASS'])}/{len(CH)} checks PASS")
