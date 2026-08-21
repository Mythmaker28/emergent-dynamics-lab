"""FDFLT01 §9 — deterministic fresh seeds with a proven-disjoint domain."""
from __future__ import annotations
import hashlib, json, glob, re, os

PARENT_TIP = "ba72111f9f6fc28f2158e2d3e2e399f4987874c1"     # resolved from the Windows increment
PROGRAM, POINT = "FDFLT01", "B1"
BAND_LO, BAND_HI = 940000000, 989999999
SPAN = BAND_HI - BAND_LO + 1
N_PRIMARY, N_RESERVE = 192, 6

def _raw(kind, index, bump=0):
    key = "%s|%s|%s|%s|%d" % (PARENT_TIP, PROGRAM, POINT, kind, index + 10000 * bump)
    return int(hashlib.sha256(key.encode()).hexdigest()[:12], 16)

def known_seeds():
    """Every seed already spent by a scientific programme in this repository."""
    S = set()
    F = json.load(open("/home/claude/edl/PQEC01/out/PQEC01_MASTER_FREEZE.json"))
    for lab, rows in F["SEED_RULE"]["SEEDS"].items():
        S |= {int(r["seed"]) for r in rows}
    for lab, rows in F["SEED_RULE"]["RESERVE_SEEDS_ORDERED"].items():
        S |= {int(r["seed"]) for r in rows}
    for p in glob.glob("/home/claude/PQEC01/raw/*.npz"):
        m = re.search(r"_s(\d+)\.npz$", os.path.basename(p))
        if m: S.add(int(m.group(1)))
    for pat in ("/home/claude/edl/OBFOR01/out/*.json", "/home/claude/edl/OBTC02/out/*.json",
                "/home/claude/edl/ORR01/out/*.json", "/home/claude/edl/OBDI02/out/*.json"):
        for p in glob.glob(pat):
            t = open(p, errors="ignore").read()
            for m in re.finditer(r'"seed"\s*:\s*(\d+)', t): S.add(int(m.group(1)))
            for m in re.finditer(r'seed(\d{4,})', t): S.add(int(m.group(1)))
    return S

def build():
    known = known_seeds()
    used, out = set(), {"PRIMARY": [], "RESERVE": []}
    for kind, n in (("PRIMARY", N_PRIMARY), ("RESERVE", N_RESERVE)):
        for i in range(n):
            bump = 0
            while True:
                s = BAND_LO + (_raw(kind, i, bump) % SPAN)
                if s not in known and s not in used: break
                bump += 1
            used.add(s)
            out[kind].append({"index": i, "seed": s, "bumps": bump})
    return out, known

if __name__ == "__main__":
    seeds, known = build()
    alls = [r["seed"] for r in seeds["PRIMARY"]] + [r["seed"] for r in seeds["RESERVE"]]
    J = {"SECTION": "FDFLT01 §9 — fresh seed manifest, published before the first run",
         "FORMULA": "seed = 940000000 + int(SHA256(parent_tip|FDFLT01|B1|kind|index + 10000*bump)[:12],16) mod 50000000",
         "PARENT_TIP": PARENT_TIP, "BAND": [BAND_LO, BAND_HI],
         "COLLISION_RESOLUTION": "deterministic re-hash with index + 10000*bump; never manual",
         "N_PRIMARY": N_PRIMARY, "N_RESERVE": N_RESERVE,
         "KNOWN_SEED_REGISTRY_SIZE": len(known),
         "DISJOINT_FROM_KNOWN": len(set(alls) & known) == 0,
         "ALL_UNIQUE": len(set(alls)) == len(alls),
         "TOTAL_BUMPS": sum(r["bumps"] for r in seeds["PRIMARY"] + seeds["RESERVE"]),
         "NO_SEED_MAY_CHANGE_AFTER_OUTCOMES_ARE_OPENED": True,
         "SEEDS": seeds}
    json.dump(J, open("/home/claude/edl/FDFLT01/out/FDFLT01_SEED_MANIFEST.json", "w"), indent=2)
    print(json.dumps({k: J[k] for k in ("KNOWN_SEED_REGISTRY_SIZE", "DISJOINT_FROM_KNOWN",
                                        "ALL_UNIQUE", "TOTAL_BUMPS")}, indent=2))
    print("first 5 primary:", [r["seed"] for r in seeds["PRIMARY"][:5]])
    print("reserves:", [r["seed"] for r in seeds["RESERVE"]])
