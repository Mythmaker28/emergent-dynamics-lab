"""DOMC independent verification. Recomputes, from the raw records and from the sealed protocol,
things the analysis asserts. A failure here is a finding, not a nuisance."""
from __future__ import annotations
import sys, os, json, hashlib, pickle, statistics as S
sys.path.insert(0, "/home/claude/sweep")
import numpy as np

CH = []


def chk(n, ok, d=""):
    CH.append({"check": n, "PASS": bool(ok), "detail": d})
    print(("PASS " if ok else "FAIL ") + n + ("  " + d if d else ""), flush=True)


P = json.load(open("domc_protocol.json"))

# 1 ---------------------------------------------------------------- the seal is intact
h = hashlib.sha256(open("domc_protocol.json", "rb").read()).hexdigest()
want = open("domc_protocol.sha256").read().split()[0]
chk("1 the sealed protocol hash matches", h == want, h)
bad = [f for f, v in P["code_sha256"].items()
       if hashlib.sha256(open(f, "rb").read()).hexdigest() != v]
chk("2 every sealed code file is unchanged since sealing", not bad, f"changed: {bad}")

# 3 ---------------------------------------------------------------- fixtures all passed
fx = json.load(open("domc_fixtures.json"))
chk("3 every mechanical fixture passes", all(r["PASS"] for r in fx),
    f"{sum(r['PASS'] for r in fx)}/{len(fx)}")

# 4 ---------------------------------------------------------- trajectory budget respected
COUNT = {}
tot = 0
for fn in sorted(os.listdir(".")):
    if fn.startswith("domc_") and fn.endswith(".pkl"):
        B = pickle.load(open(fn, "rb"))
        n = sum(len(b["arms"]) for b in B)
        COUNT[fn] = {"blocks": len(B), "trajectories": n}
        tot += n
chk("4 the hard maximum of 384 trajectories is respected", tot <= 384,
    f"{tot} trajectories: " + ", ".join(f"{k}={v['trajectories']}" for k, v in COUNT.items()))

# 5 ------------------------------------------------- dev and prospective seeds are disjoint
seeds = {}
for fn, _ in COUNT.items():
    B = pickle.load(open(fn, "rb"))
    seeds[fn] = {b["seed"] for b in B}
dev = set().union(*[v for k, v in seeds.items() if "_DEV_" in k]) if seeds else set()
pro = set().union(*[v for k, v in seeds.items() if "_PROSP_" in k]) if seeds else set()
chk("5 development and prospective founding blocks are disjoint", not (dev & pro),
    f"dev={sorted(dev)[:3]}...  prosp={sorted(pro)[:3]}...  overlap={sorted(dev & pro)}")

# 6 --------------------------------------- the exchange really is conservative in the records
B = pickle.load(open("domc_FAR_PROSP_cc-00.pkl", "rb")) if \
    os.path.exists("domc_FAR_PROSP_cc-00.pkl") else []
if B:
    res = []
    for b in B:
        a = b["arms"].get("AB|NONE"); c = b["arms"].get("AB|CROSS")
        if a and c:
            res.append(abs(c["t0"]["sum_Mf"] - a["t0"]["sum_Mf"]))
    chk("6 sum(Mf) is unchanged by the reciprocal permutation, to float summation order",
        max(res) < 1e-9, f"max |d sum Mf| = {max(res):.3e} over {len(res)} blocks")
    # 7 --- the exchange left the bodies alone: same sizes at t0 in NONE and CROSS
    d = []
    for b in B:
        a = b["arms"].get("AB|NONE"); c = b["arms"].get("AB|CROSS")
        if a and c and a["t0"]["scalars"]["A"] and c["t0"]["scalars"]["A"]:
            d.append(abs(a["t0"]["scalars"]["A"]["size"] - c["t0"]["scalars"]["A"]["size"]))
            d.append(abs(a["t0"]["scalars"]["B"]["size"] - c["t0"]["scalars"]["B"]["size"]))
    chk("7 the reciprocal permutation does not move or resize the material bodies",
        max(d) == 0, f"max |d size| = {max(d)}")
    # 8 --- ERASE really zeroed the addressed side and only that side
    ok = True; det = []
    for b in B:
        e = b["arms"].get("AB|ERASE_A")
        n = b["arms"].get("AB|NONE")
        if e and n:
            ok &= (abs(e["t0"]["scalars"]["A"]["m_plus"]) == 0.0
                   and e["t0"]["scalars"]["B"]["m_plus"] == n["t0"]["scalars"]["B"]["m_plus"])
    chk("8 ERASE_A zeroes site A's memory and leaves site B's bit-identical", ok)
    # 9 --- the turnover criterion is met on the frozen threshold
    M = [v["turn"][f"M_{s}"] for b in B for v in b["arms"].values()
         for s in ("A", "B") if v["turn"][f"M_{s}"] is not None]
    chk("9 the frozen material-turnover criterion M <= 0.35 is met at the readout",
        S.median(M) <= 0.35,
        f"median M = {S.median(M):.4f}, max = {max(M):.4f}, "
        f"{100*sum(1 for x in M if x <= 0.35)/len(M):.1f}% of readouts below")
    # 10 -- no analysis is conditioned on survival
    tot_arm = sum(len(b["arms"]) for b in B)
    alive = sum(1 for b in B for v in b["arms"].values()
                if v["turn"]["alive_A"] and v["turn"]["alive_B"])
    chk("10 every block enters every analysis: no arm was dropped for survival",
        alive == tot_arm, f"{alive}/{tot_arm} arm-readouts have both sites occupied")

json.dump(CH, open("domc_verify.json", "w"), indent=1)
n = sum(1 for c in CH if c["PASS"])
print(f"\n{n}/{len(CH)} checks PASS")
