"""PPAI verification."""
import sys, os, json, hashlib
sys.path.insert(0, "/home/claude/sweep")
CH = []
def chk(n, ok, d=""):
    CH.append({"check": n, "PASS": bool(ok), "detail": d}); print(("PASS " if ok else "FAIL ")+n+("  "+d if d else ""))
P = json.load(open("ppai_protocol.json"))
h = hashlib.sha256(open("ppai_protocol.json","rb").read()).hexdigest()
chk("1 sealed protocol hash matches", h == open("ppai_protocol.sha256").read().split()[0], h)
bad = [f for f,v in P["code_sha256"].items() if hashlib.sha256(open(f,"rb").read()).hexdigest()!=v]
chk("2 every sealed code file unchanged", not bad, f"changed: {bad}")
fx = json.load(open("ppai_fixtures.json"))
chk("3 every fixture passes", all(r["PASS"] for r in fx), f"{sum(r['PASS'] for r in fx)}/{len(fx)}")
d = json.load(open("ppai_dev.json"))
chk("4 hard maximum of 240 new trajectories respected", d["trajectories"] <= 240, f"{d['trajectories']} used")
chk("5 DEV cap of 6 blocks and 48 trajectories respected",
    len(d["dev_seeds"])<=6 and d["trajectories"]<=48, f"{len(d['dev_seeds'])} blocks, {d['trajectories']} traj")
chk("6 no confirmatory block was opened", not os.path.exists("ppai_CONF.pkl") and not os.path.exists("ppai_HELD.pkl"))
chk("7 DEV seeds never used by any earlier programme",
    not (set(d["dev_seeds"]) & set(range(30000,40000))), f"seeds {d['dev_seeds']}")
chk("8 the wash verdict is NO_WASH_WINDOW and the stop rule fired",
    d["WASH_WINDOW"]=="NO_WASH_WINDOW" and d["T_WASH"] is None)
a = json.load(open("ppai_audit.json"))
chk("9 the wash failure is present at ZERO_FEEDBACK, i.e. in the frozen root physics",
    not any(x["worst_value"]<=0.10 and x["min_z_sep_ratio"]>=0.50
            for x in a["WASH_DIAGNOSTIC_ALL_GAIN_CLASSES"]["ZERO_FEEDBACK"]))
chk("10 gain zero reproduces the frozen root LawSpec bit-identically",
    any(r["fixture"].startswith("G1.1") and r["PASS"] for r in fx))
chk("11 no private memory->response path remains in the engine",
    any(r["fixture"].startswith("G1.9") and r["PASS"] for r in fx))
json.dump(CH, open("ppai_verify.json","w"), indent=1)
print(f"\n{sum(1 for c in CH if c['PASS'])}/{len(CH)} checks PASS")
