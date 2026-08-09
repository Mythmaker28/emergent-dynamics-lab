"""CHMR independent verification."""
from __future__ import annotations
import sys, os, json, hashlib, pickle, statistics as S
sys.path.insert(0, "/home/claude/sweep")
import numpy as np
CH = []


def chk(n, ok, d=""):
    CH.append({"check": n, "PASS": bool(ok), "detail": d})
    print(("PASS " if ok else "FAIL ") + n + ("  " + d if d else ""), flush=True)


P = json.load(open("chmr_protocol.json"))
h = hashlib.sha256(open("chmr_protocol.json", "rb").read()).hexdigest()
chk("1 sealed protocol hash matches", h == open("chmr_protocol.sha256").read().split()[0], h)
bad = [f for f, v in P["code_sha256"].items()
       if hashlib.sha256(open(f, "rb").read()).hexdigest() != v]
chk("2 every sealed code file is unchanged since sealing", not bad, f"changed: {bad}")

FILES = {}
tot = 0
for fn in sorted(os.listdir(".")):
    if fn.startswith("chmr_") and fn.endswith(".pkl"):
        B = pickle.load(open(fn, "rb"))
        n = sum(len(b["arms"]) for b in B)
        FILES[fn] = {"blocks": len(B), "trajectories": n, "seeds": sorted(b["seed"] for b in B)}
        tot += n
chk("3 the hard maximum of 320 new trajectories is respected", tot <= 320,
    f"{tot}: " + ", ".join(f"{k}={v['trajectories']}" for k, v in FILES.items()))

sets = {k: set(v["seeds"]) for k, v in FILES.items()}
dev = set().union(*[v for k, v in sets.items() if "_DEV" in k]) if sets else set()
oth = set().union(*[v for k, v in sets.items() if "_DEV" not in k]) if sets else set()
chk("4 DEV blocks are disjoint from every confirmatory block", not (dev & oth),
    f"dev={sorted(dev)}  conf/held={sorted(oth)[:4]}...")
prev = set(range(30000, 36000))
chk("5 no founding block of any earlier programme is reused",
    not ((dev | oth) & prev), f"overlap = {sorted((dev | oth) & prev)}")

for fn, B in ((k, pickle.load(open(k, "rb"))) for k in FILES):
    tag = fn.replace("chmr_", "").replace(".pkl", "")
    # every arm present in every block: no conditioning on success
    narms = {len(b["arms"]) for b in B}
    chk(f"6[{tag}] every block carries all 8 arms (no conditioning on survival or surgery)",
        narms == {8}, f"arm counts = {narms}")
    # ITT: no block dropped
    chk(f"7[{tag}] lineage is continuous: zero splits, zero fusions, zero disappearances",
        all(v["lineage"]["n_splits"] == 0 and v["lineage"]["n_fusions"] == 0
            and v["lineage"]["n_disappearances"] == 0 for b in B for v in b["arms"].values()))
    # surgery exactness, from the immediate ledgers
    okc = all(b["arms"]["HALO_CROSS"]["ledger"]["c"]["multiset_preserved"]
              and b["arms"]["HALO_CROSS"]["ledger"]["N"]["multiset_preserved"]
              and not b["arms"]["HALO_CROSS"]["ledger"]["Mf"]["changed"]
              and not b["arms"]["HALO_CROSS"]["ledger"]["rho"]["changed"] for b in B)
    chk(f"8[{tag}] HALO_CROSS permutes c and N exactly and leaves Mf and rho bit-identical", okc)
    okm = all(b["arms"]["CORE_CROSS"]["ledger"]["Mf"]["multiset_preserved"]
              and not b["arms"]["CORE_CROSS"]["ledger"]["c"]["changed"]
              and not b["arms"]["CORE_CROSS"]["ledger"]["N"]["changed"]
              and not b["arms"]["CORE_CROSS"]["ledger"]["rho"]["changed"] for b in B)
    chk(f"9[{tag}] CORE_CROSS permutes Mf exactly and leaves c, N and rho bit-identical", okm)
    oks = all(not b["arms"]["MATCHED_SHAM"]["ledger"][f]["changed"]
              for b in B for f in ("rho", "U", "V", "C", "Mf", "c", "N"))
    chk(f"10[{tag}] MATCHED_SHAM is a bit-exact no-op on the whole state", oks)
    oko = all(b["arms"]["ORPHAN_HALO"]["ledger"]["rho"]["sum_after"] == 0.0
              and not b["arms"]["ORPHAN_HALO"]["ledger"]["c"]["changed"]
              and not b["arms"]["ORPHAN_HALO"]["ledger"]["N"]["changed"] for b in B)
    chk(f"11[{tag}] ORPHAN_HALO removes all matter and preserves c and N exactly", oko)
    # realized global quantities recorded and conserved by the permutations
    dc = [abs(b["arms"]["HALO_CROSS"]["ledger"]["realized_global_c_after"]
              - b["arms"]["HALO_CROSS"]["ledger"]["realized_global_c_before"]) for b in B]
    chk(f"12[{tag}] the halo permutation conserves the REALIZED global c (recorded, not assumed)",
        max(dc) < 1e-9, f"max |d sum c| = {max(dc):.3e}")
    # turnover on the frozen criterion, lineage-resolved
    M = [d["M_final"] for b in B for v in b["arms"].values() if "turnover" in v
         for d in v["turnover"]["M_by_lineage"].values() if d["M_final"] is not None]
    chk(f"13[{tag}] frozen turnover criterion met inside a continuous lineage",
        S.median(M) <= 0.35 and max(M) <= 0.35,
        f"median M = {S.median(M):.4f}, max = {max(M):.4f}, n = {len(M)}")

json.dump(CH, open("chmr_verify.json", "w"), indent=1, default=str)
n = sum(1 for c in CH if c["PASS"])
print(f"\n{n}/{len(CH)} checks PASS")
