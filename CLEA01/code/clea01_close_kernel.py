"""CLEA01 closure §5 — adjudicate the transport kernel, measured on the archives.

No world is constructed and no engine is run: NEW_WORLD_CONSTRUCTIONS = 0 and
NEW_SCIENTIFIC_ENGINE_RUNS = 0 are absolute. The kernel is therefore established two ways, both
of which use only the engine SOURCE and the archives that already exist.

  LOWER BOUND (the kernel is not too narrow). If the true one-step support were wider than
  Moore-1, some occupied cell on row t+1 would have no Moore-1 predecessor on row t. Every such
  cell is counted, over every consecutive row pair of every arm.

  UPPER BOUND (the kernel is not too wide). On rows where the previous row's Y support is a single
  cell, every occupied cell of the next row is a direct observation of a reachable displacement.
  Collecting those offsets over all arms measures the reachable set from the data instead of
  assuming it. If the observed set is exactly the nine Moore-1 offsets and never exceeds them, the
  kernel is tight in both directions.

Cell-locality of births is read from the engine source, not from the archives, and is reported
separately.
"""
from __future__ import annotations
import ast, datetime as dt, json, os, sys
import numpy as np
REPO = os.environ.get("CLEA01_REPO", "/home/claude/edl")
sys.path.insert(0, f"{REPO}/OMLDCT02/code"); sys.path.insert(0, f"{REPO}/CLEA01/code")
import omldct02_hashes as H
import clea01_lineage_i2 as I2

L = 36


def wrap(d):
    return (d + L // 2) % L - L // 2


def arm(path):
    meta, T, data, YB, YD, XB = I2.load_grids(path, 0)
    prev = None
    viol = 0
    rows = 0
    offsets = {}
    single_rows = 0
    maxcheb = 0
    for t in range(T):
        occ, nY = I2.grid_at(data, t)
        if prev is not None and occ.any():
            rows += 1
            if prev.any():
                out = occ & ~I2.dilate(prev)
                v = int(out.sum())
                viol += v
                pc = np.argwhere(prev)
                if len(pc) == 1:
                    single_rows += 1
                    py, px = int(pc[0][0]), int(pc[0][1])
                    for a, b in np.argwhere(occ):
                        dy, dx = wrap(int(a) - py), wrap(int(b) - px)
                        offsets[(dy, dx)] = offsets.get((dy, dx), 0) + 1
                        maxcheb = max(maxcheb, max(abs(dy), abs(dx)))
        prev = occ
        if not occ.any() and prev is not None and t > 0:
            pass
    return dict(rows_compared=rows, violations=viol, single_source_rows=single_rows,
                offsets={f"{k[0]},{k[1]}": v for k, v in sorted(offsets.items())},
                max_chebyshev_from_single_source=maxcheb, horizon=T)


def engine_source_facts():
    """read the frozen chain that actually produced the archives. Nothing is executed.

    omldct02_fork -> tlmr01_world.build -> PQECWorld(pqec01_observer)
                  -> WorldOBTC(engine_obtc) -> WorldV2(lawspec_v2) -> World(kinetics)
    """
    import itertools
    chain = {
        "kinetics (frozen reference)": f"{REPO}/ORR01/code/kinetics.py",
        "lawspec_v2 (WorldV2)": f"{REPO}/ORR01/code/lawspec_v2.py",
        "engine_obtc (WorldOBTC, verbatim copy + counters)": f"{REPO}/OBTC02/code/engine_obtc.py",
        "pqec01_observer (PQECWorld, the class that runs)": f"{REPO}/PQEC01/code/pqec01_observer.py",
    }
    out = {"CHAIN": {k: {"path": v, "sha256": H.file_sha256(v)} for k, v in chain.items()}}

    def body(path, name):
        src = open(path).read()
        if f"def {name}" not in src:
            return None
        seg = src.split(f"def {name}")[1]
        cut = seg.find("\n    def ")
        return seg[:cut if cut > 0 else len(seg)]

    # 1. the four sub-shifts, taken from every place they are written
    subs = {}
    k_diff = body(f"{REPO}/ORR01/code/kinetics.py", "_diffuse")
    for line in k_diff.splitlines():
        if "for shift, ax in" in line:
            subs["kinetics._diffuse (inline tuple)"] = ast.literal_eval(
                line.split("in", 1)[1].split("#")[0].strip().rstrip(":"))
    e_src = open(f"{REPO}/OBTC02/code/engine_obtc.py").read()
    for node in ast.walk(ast.parse(e_src)):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "NEI":
            subs["engine_obtc.NEI"] = ast.literal_eval(node.value)
    o_diff = body(f"{REPO}/PQEC01/code/pqec01_observer.py", "_diffuse")
    out["OBSERVER_ITERATES_EN_NEI"] = "for sub, (shift, ax) in enumerate(EN.NEI)" in o_diff
    out["SUB_SHIFTS"] = {k: [list(x) for x in v] for k, v in subs.items()}
    out["ALL_SOURCES_AGREE_ON_THE_SUB_SHIFTS"] = len({tuple(map(tuple, v)) for v in subs.values()}) == 1

    # 2. the reachable displacement set, DERIVED from those sub-shifts rather than assumed.
    #    each pass moves a binomial subset of current occupancy by at most one cell, so a particle
    #    accepts an arbitrary subset of the four offered moves, in order.
    nei = list(subs["engine_obtc.NEI"])
    disp = set()
    for take in itertools.product([0, 1], repeat=len(nei)):
        dy = dx = 0
        for t, (shift, ax) in zip(take, nei):
            if not t:
                continue
            if ax == 0:
                dy += shift
            else:
                dx += shift
        disp.add((dy, dx))
    out["DERIVED_DISPLACEMENT_SET"] = sorted(list(d) for d in disp)
    out["DERIVED_SET_IS_EXACTLY_MOORE_1"] = disp == {(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1)}
    out["WHY_THE_OPPOSING_PAIR_CANCELS"] = ("the four offered moves are +y, -y, +x, -x. Taking both "
        "moves on one axis returns the particle to its own row or column, so the net displacement "
        "on each axis lies in {-1, 0, +1} and never in {-2, +2}.")

    # 3. occupancy is re-read at the head of every pass — this is what makes each pass move a
    #    subset of CURRENT occupancy rather than of the row's original occupancy.
    out["DIFFUSE_REREADS_OCCUPANCY_EACH_PASS"] = "n = self.n[sname]" in k_diff
    out["DESTINATION_BLOCKING_IS_APPLIED"] = ("dest_free" in k_diff and "np.minimum(movers" in k_diff)
    out["BLOCKING_CAN_ONLY_SHRINK_THE_SUPPORT"] = ("accepted = min(movers, dest_free) <= movers, so "
        "capacity refusal removes displacements and never adds one. A blocked hop leaves the "
        "particle in place, which is (0,0) and already in the kernel.")

    # 4. within-step order
    tree = ast.parse(open(f"{REPO}/ORR01/code/kinetics.py").read())
    fns = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    out["WITHIN_STEP_ORDER"] = [n.func.attr for n in ast.walk(fns["_one_step"])
                                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]

    # 5. cell-locality of both births, from _react
    react = body(f"{REPO}/ORR01/code/kinetics.py", "_react")
    out["REACT_SOURCE"] = "\n".join(l for l in react.splitlines() if l.strip())[:700]
    out["PAIR_IS_ELEMENTWISE"] = "pair = nX * nY" in react
    out["CANDIDATES_ARE_SAME_CELL"] = "cand = np.minimum(self.n[res], free0)" in react
    out["BOTH_BIRTHS_REQUIRE_nY_GT_0_AT_THE_SAME_CELL"] = (
        out["PAIR_IS_ELEMENTWISE"] and out["CANDIDATES_ARE_SAME_CELL"])
    out["WHY"] = ("p = min(1, k * nX * nY) is elementwise, so at a cell with nY = 0 the birth "
                  "probability is exactly 0 for BOTH the X channel and the Y channel. Neither birth "
                  "can occur where there is no Y, and neither can occur at a different cell.")

    # 6. the only other channel that touches counts
    ex = body(f"{REPO}/ORR01/code/lawspec_v2.py", "_exchange") or ""
    out["EXCHANGE_POOL_MENTIONS_Y_COUNTS"] = ('"Y"' in ex)
    out["EXCHANGE_EXCERPT"] = "\n".join(l for l in ex.splitlines() if l.strip())[:500]
    return out


def main(out_path):
    led = [json.loads(l) for l in open(f"{REPO}/OMLDCT02/work/OMLDCT02_SEALED_LEDGER.jsonl") if l.strip()]
    adm = [r for r in led if r.get("ADMISSIBLE")]
    done = json.load(open(out_path)) if os.path.exists(out_path) else {}
    for r in adm:
        for a in ("SELECTIVE", "SHAM"):
            key = f"{r['index']}|{a}"
            if key in done:
                continue
            done[key] = arm(r["ARCHIVES"][a]["path"])
            tmp = out_path + ".part"
            with open(tmp, "w") as fh:
                json.dump(done, fh)
            os.replace(tmp, out_path)
            print(f"{key}: rows={done[key]['rows_compared']} viol={done[key]['violations']} "
                  f"single={done[key]['single_source_rows']}", flush=True)
    print("done", len(done))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--source":
        print(json.dumps(engine_source_facts(), indent=1)[:2500])
    else:
        main(sys.argv[1])
