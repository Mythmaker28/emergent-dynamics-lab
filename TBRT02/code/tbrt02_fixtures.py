"""TBRT02 — fixture-scale validation of the DISPLACED intervention.

Every world built here is certified NON-SCIENTIFIC by the mission's own scale guard, imported rather
than reimplemented: L <= 5, horizon < 250, seeds from a range disjoint from every manifest. The
guard's rule is printed with the results so the certification can be checked rather than trusted.

Proved on real engine objects, not in argument:
  1. total Y mass conserved EXACTLY, unlike removal which sends Y to WY
  2. NO random number consumed — the RNG state is bit-identical before and after
  3. the daughter's cells untouched, bit for bit
  4. the destination beyond one-step reach of every daughter cell
  5. displacement and removal produce DIFFERENT physical states, differing only in Y and WY
  6. the destination choice is deterministic and reproducible
  7. capacity is respected, and an impossible displacement raises instead of truncating
"""
from __future__ import annotations
import json, os, sys
import numpy as np

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
for p in ("TBRT02/code", "FMRCT01/code", "OMLDCT02/code", "ORR01/code", "OBTC02/code",
          "PQEC01/code", "TLMR01/code"):
    sys.path.insert(0, os.path.join(REPO, p))
import tbrt02_displace as D          # noqa: E402
import tbrt02_guard as G             # noqa: E402
import fmrct01_world as FMW          # noqa: E402
import pqec01_observer as O          # noqa: E402

FIXTURE_L = 5
FIXTURE_HORIZON = 40
FIXTURE_SEEDS = [910000001, 910000002, 910000003]
LAW = dict(kY=0.001004754572603833, muY=0.000740894982503035, p_hop_Y=0.10263340389897246)


def certify(seed):
    return {"seed": seed, "L": FIXTURE_L, "horizon": FIXTURE_HORIZON,
            "seed_in_a_manifest": seed in G.manifest_seeds(),
            "SCIENTIFIC_SCALE": G.is_scientific_scale(FIXTURE_L, FIXTURE_HORIZON, seed)}


def tiny(seed):
    w, rec, sp = O.build_world(seed, LAW["kY"], LAW["muY"], L=FIXTURE_L,
                               horizon=FIXTURE_HORIZON, instrumented=True,
                               record_fields=False, p_hop_Y=LAW["p_hop_Y"])
    return w


def snapshot(w):
    return {s: w.n[s].copy() for s in O.SPECIES}


def run():
    out = {"MISSION": "TBRT02", "GUARD_RULE": G.SCALE_RULE, "MAX_FIXTURE_L": G.MAX_FIXTURE_L,
           "NEED": G.NEED, "CERTIFICATION": [certify(s) for s in FIXTURE_SEEDS], "FIXTURES": []}
    out["ALL_FIXTURES_ARE_NON_SCIENTIFIC"] = not any(c["SCIENTIFIC_SCALE"]
                                                     for c in out["CERTIFICATION"])
    for seed in FIXTURE_SEEDS:
        L = FIXTURE_L
        w = tiny(seed); w.n["Y"][:] = 0; w.n["Y"][0, 0] = 2; w.n["Y"][1, 1] = 1
        parent = [(0, 0)]; daughter = [(1, 1)]
        rng0 = FMW.rng_hash(w); phys0 = FMW.phys_hash(w)
        y0 = int(w.n["Y"].sum()); before = snapshot(w)

        wr = tiny(seed); wr.n["Y"][:] = 0; wr.n["Y"][0, 0] = 2; wr.n["Y"][1, 1] = 1
        removed = FMW.intervene(wr, parent)
        rem = {"removed": removed, "Y_after": int(wr.n["Y"].sum()),
               "WY_after": int(wr.n["WY"].sum()), "rng_unchanged": FMW.rng_hash(wr) == rng0}

        audit = D.displace(w, parent, daughter)
        dest = tuple(audit["destination"]) if audit["destination"] else None
        after = snapshot(w)
        f = {"seed": seed, "parent_cells": parent, "daughter_cells": daughter,
             "Y_total_before": y0, "Y_total_after": int(w.n["Y"].sum()),
             "1_Y_MASS_CONSERVED_EXACTLY": int(w.n["Y"].sum()) == y0,
             "removal_sends_Y_to_WY_instead": rem,
             "2_NO_RANDOM_CONSUMED": FMW.rng_hash(w) == rng0,
             "3_DAUGHTER_UNTOUCHED": int(after["Y"][1, 1]) == 1,
             "destination": audit["destination"],
             "antipode_of_the_daughter": audit["antipode_of_the_daughter"],
             "search_radius_used": audit["search_radius_used"],
             "4_DESTINATION_BEYOND_ONE_STEP_OF_EVERY_DAUGHTER_CELL":
                 all(D.cheb(dest, d, L) > 1 for d in daughter) if dest else None,
             "chebyshev_destination_to_daughter":
                 [D.cheb(dest, d, L) for d in daughter] if dest else None,
             "5_DIFFERENT_FROM_REMOVAL": FMW.phys_hash(w) != FMW.phys_hash(wr),
             "5b_ONLY_Y_AND_WY_DIFFER_FROM_THE_UNTREATED_STATE":
                 all(np.array_equal(before[s], after[s]) for s in O.SPECIES if s not in ("Y", "WY")),
             "5c_WY_UNTOUCHED_BY_DISPLACEMENT":
                 int(after["WY"].sum()) == int(before["WY"].sum()),
             "phys_hash_untreated": phys0, "phys_hash_displaced": FMW.phys_hash(w),
             "phys_hash_removed": FMW.phys_hash(wr), "audit": audit}
        w2 = tiny(seed); w2.n["Y"][:] = 0; w2.n["Y"][0, 0] = 2; w2.n["Y"][1, 1] = 1
        a2 = D.displace(w2, parent, daughter)
        f["6_DETERMINISTIC"] = (a2["destination"] == audit["destination"]
                                and FMW.phys_hash(w2) == FMW.phys_hash(w))
        w3 = tiny(seed); w3.n["Y"][:] = 0; w3.n["Y"][0, 0] = 2
        w3.n["SX"][:] = w3.sp.CAP; w3.n["SY"][:] = 0; w3.n["WX"][:] = 0; w3.n["WY"][:] = 0
        try:
            D.displace(w3, [(0, 0)], [(1, 1)])
            f["7_REFUSES_WHEN_CAPACITY_IS_ABSENT"] = False
        except RuntimeError:
            f["7_REFUSES_WHEN_CAPACITY_IS_ABSENT"] = True
        checks = [k for k in f if k[0].isdigit()]
        f["ALL_CHECKS_PASS"] = all(bool(f[k]) for k in checks)
        out["FIXTURES"].append(f)
    out["N_FIXTURES"] = len(out["FIXTURES"])
    out["ALL_PASS"] = all(x["ALL_CHECKS_PASS"] for x in out["FIXTURES"])
    return out


if __name__ == "__main__":
    r = run()
    print("all fixtures certified NON-scientific:", r["ALL_FIXTURES_ARE_NON_SCIENTIFIC"])
    for f in r["FIXTURES"]:
        print(f"\nseed {f['seed']}  parent {f['parent_cells']} -> {f['destination']} "
              f"(antipode of the daughter {f['antipode_of_the_daughter']}, "
              f"radius {f['search_radius_used']})")
        for k in sorted(k for k in f if k[0].isdigit()):
            print(f"    {'PASS' if f[k] else 'FAIL'}  {k}")
    print("\nALL_PASS =", r["ALL_PASS"])
    json.dump(r, open(f"{REPO}/TBRT02/out/TBRT02_FIXTURES.json", "w"), indent=1, default=str)
