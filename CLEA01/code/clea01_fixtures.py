"""CLEA01 §4 items 5 and 6 — causal witnesses and deterministic mutation fixtures.

Item 5 requires every inherited claim to carry a machine-readable causal witness. Under the frozen
rule the witness for "cell d is CERTAIN on row t+1" is exactly the pair (S(d,t+1), CERTAIN(t)) with
S non-empty and contained in CERTAIN(t). That is enumerable and checkable, and it is what these
fixtures check.

Item 6 requires that removing one required causal edge destroys the corresponding inheritance
claim. The fixtures below are hand-built occupancy sequences with the answer written out by hand;
each mutation deletes exactly one occupied source cell or one lineage membership and asserts that
the dependent CERTAIN claim disappears.

No archive is read. No world is run.
"""
from __future__ import annotations
import numpy as np, sys, os
REPO = os.environ.get("CLEA01_REPO", "/home/claude/edl")
sys.path.insert(0, f"{REPO}/CLEA01/code")
import clea01_lineage_i2 as I2
import clea01_lineage_i1 as I1

L = I2.L

def step_i2(occ_prev, certain_prev, occ_now):
    dil_c = I2.dilate(certain_prev); dil_nc = I2.dilate(occ_prev & ~certain_prev)
    return occ_now & dil_c & ~dil_nc

def step_i1(occ_prev_cells, certain_prev_cells, occ_now_cells):
    prev = {c: 1 for c in occ_prev_cells}
    out = set()
    for d in occ_now_cells:
        S = I1.sources(d, prev)
        if S and S <= set(certain_prev_cells): out.add(d)
    return out

def grid(cells):
    g = np.zeros((L, L), bool)
    for y, x in cells: g[y, x] = True
    return g

CASES = [
 {"name": "lone lineage cell persists",
  "occ_prev": [(10, 10)], "certain_prev": [(10, 10)], "occ_now": [(10, 10)],
  "expect": [(10, 10)], "why": "the only admissible source is the lineage cell itself"},
 {"name": "lineage cell hops one step",
  "occ_prev": [(10, 10)], "certain_prev": [(10, 10)], "occ_now": [(10, 11)],
  "expect": [(10, 11)], "why": "Moore-1 reachable and the only source is lineage"},
 {"name": "diagonal hop is reachable in one step",
  "occ_prev": [(10, 10)], "certain_prev": [(10, 10)], "occ_now": [(11, 11)],
  "expect": [(11, 11)],
  "why": "the +y pass and the +x pass both act within one step, so a diagonal net displacement is "
         "reachable. A von Neumann kernel would wrongly call this unreachable."},
 {"name": "two cells away is NOT reachable",
  "occ_prev": [(10, 10)], "certain_prev": [(10, 10)], "occ_now": [(10, 12)],
  "expect": [], "why": "net displacement 2 is outside {-1,0,1}^2; S is empty and the invariant flags it"},
 {"name": "an adjacent non-lineage source destroys certainty",
  "occ_prev": [(10, 10), (10, 12)], "certain_prev": [(10, 10)], "occ_now": [(10, 11)],
  "expect": [],
  "why": "(10,11) is Moore-1 of both (10,10) and (10,12); the second is not lineage, so the mass "
         "could have come from outside. This is the ambient-succession rejection in miniature."},
 {"name": "a distant non-lineage source does not destroy certainty",
  "occ_prev": [(10, 10), (10, 20)], "certain_prev": [(10, 10)], "occ_now": [(10, 11)],
  "expect": [(10, 11)], "why": "(10,20) is not Moore-1 of (10,11), so it is not an admissible source"},
 {"name": "split into two branches, both certain",
  "occ_prev": [(10, 10)], "certain_prev": [(10, 10)], "occ_now": [(10, 9), (10, 11)],
  "expect": [(10, 9), (10, 11)], "why": "one-to-many transport; a split does not terminate Model C"},
 {"name": "merge of two lineage branches stays certain",
  "occ_prev": [(10, 9), (10, 11)], "certain_prev": [(10, 9), (10, 11)], "occ_now": [(10, 10)],
  "expect": [(10, 10)], "why": "every contributing branch is lineage"},
 {"name": "merge of a lineage and a non-lineage branch is not certain",
  "occ_prev": [(10, 9), (10, 11)], "certain_prev": [(10, 9)], "occ_now": [(10, 10)],
  "expect": [], "why": "provenance from every contributor is required; one contributor is outside"},
 {"name": "toroidal wrap in x",
  "occ_prev": [(0, 0)], "certain_prev": [(0, 0)], "occ_now": [(0, L - 1)],
  "expect": [(0, L - 1)], "why": "the lattice is a torus; column L-1 is Moore-1 of column 0"},
 {"name": "toroidal wrap on the diagonal corner",
  "occ_prev": [(0, 0)], "certain_prev": [(0, 0)], "occ_now": [(L - 1, L - 1)],
  "expect": [(L - 1, L - 1)], "why": "both axes wrap in the same step"},
 {"name": "empty lineage cannot revive",
  "occ_prev": [(10, 10)], "certain_prev": [], "occ_now": [(10, 10)],
  "expect": [], "why": "a cell can only enter CERTAIN through a source already in CERTAIN"},
]

MUTATIONS = [
 {"name": "delete the sole lineage source",
  "base": 1, "mutate": lambda c: {"certain_prev": []},
  "expect_claim_destroyed": True,
  "why": "removing the one required causal edge leaves the claim unsupported"},
 {"name": "add an adjacent non-lineage occupied cell",
  "base": 1, "mutate": lambda c: {"occ_prev": c["occ_prev"] + [(10, 12)]},
  "expect_claim_destroyed": True,
  "why": "a second admissible source that is not lineage removes certainty"},
 {"name": "move the required source out of Moore range",
  "base": 1, "mutate": lambda c: {"occ_prev": [(10, 8)], "certain_prev": [(10, 8)]},
  "expect_claim_destroyed": True, "why": "the causal edge no longer exists at all"},
 {"name": "delete one of two merging lineage branches",
  "base": 7, "mutate": lambda c: {"occ_prev": [(10, 9)], "certain_prev": [(10, 9)]},
  "expect_claim_destroyed": False,
  "why": "the surviving branch still supports the claim on its own — a control showing the "
         "mutation test is not vacuously destructive"},
]

def run():
    rows = []
    for k, c in enumerate(CASES):
        occ_p = grid(c["occ_prev"]); cert_p = grid(c["certain_prev"]); occ_n = grid(c["occ_now"])
        g2 = set(map(tuple, np.argwhere(step_i2(occ_p, cert_p, occ_n))))
        g2 = {(int(a), int(b)) for a, b in g2}
        g1 = step_i1(c["occ_prev"], c["certain_prev"], c["occ_now"])
        exp = set(c["expect"])
        rows.append({"layer": "witness_fixture", "case": c["name"], "expected_by_hand": sorted(exp),
                     "impl1": sorted(g1), "impl2": sorted(g2),
                     "impl1_matches_hand": g1 == exp, "impl2_matches_hand": g2 == exp,
                     "implementations_agree": g1 == g2, "why": c["why"],
                     "PASS": g1 == exp and g2 == exp})
    for m in MUTATIONS:
        base = CASES[m["base"]]
        c = dict(base); c.update(m["mutate"](base))
        occ_p = grid(c["occ_prev"]); cert_p = grid(c["certain_prev"]); occ_n = grid(c["occ_now"])
        g2 = {(int(a), int(b)) for a, b in map(tuple, np.argwhere(step_i2(occ_p, cert_p, occ_n)))}
        g1 = step_i1(c["occ_prev"], c["certain_prev"], c["occ_now"])
        destroyed = (len(g1) == 0)
        ok = (destroyed == m["expect_claim_destroyed"]) and (g1 == g2)
        rows.append({"layer": "mutation_fixture", "case": m["name"],
                     "base_case": base["name"], "claim_destroyed": destroyed,
                     "expected_destroyed": m["expect_claim_destroyed"],
                     "impl1": sorted(g1), "impl2": sorted(g2),
                     "implementations_agree": g1 == g2, "why": m["why"], "PASS": ok})
    return rows, all(r["PASS"] for r in rows)

if __name__ == "__main__":
    rows, ok = run()
    for r in rows: print(("PASS " if r["PASS"] else "FAIL ") + r["case"])
    print("FIXTURES =", "PASS" if ok else "FAIL", f"({len(rows)} cases)")
