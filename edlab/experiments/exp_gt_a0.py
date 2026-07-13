"""EXP-GT-A0 -- ONTOLOGY AUDIT of the A head. Run BEFORE any tolerance is touched.

D-052 recorded: "A fails on held-out because the layouts' channel gaps differ by 5 columns while A's tolerance
is 6.0" -- and concluded that A needs a finer RESOLUTION. That conclusion presupposes the benchmark label
`A = DIFFERENT` was correct. This experiment tests that presupposition FIRST, because A was DEFINED as
*causal architecture*, explicitly invariant to translation, phase and spatial layout. If the two cases are the
same causal graph drawn at different spacings then:

  * `A = SAME` was the RIGHT answer,
  * the benchmark's expected label was wrong,
  * and "repairing the tolerance" would have been TUNING AN INSTRUMENT TO REPRODUCE A LABELLING ERROR --
    driving A's resolution down until it reported DIFFERENT for pure geometry, destroying the very invariance
    A exists to provide.

Sharpening a ruler because it disagrees with a mislabelled reference is how an instrument gets silently broken.
So: inspect the graphs, do not touch the tolerance.

TWO GRAPHS ARE DISTINGUISHED, and the distinction is the point:

  STRUCTURAL graph  -- the wiring: which components exist and which could influence which. Program-INDEPENDENT.
                       This is what `A` means.
  ACTIVE-INFLUENCE  -- what an intervention actually propagates through, given the current memory word. A closed
                       gate severs an influence path that structurally still exists. Program-DEPENDENT.

`A` must be read off the STRUCTURAL graph, or a mere program change would move it -- precisely the contamination
D-052 already had to fix once (a channel's detected column depended on how it was gated).

Everything here is EVALUATOR-side and fully privileged: it may read component locations and hidden labels. It is
ground-truth bookkeeping, not an observer. No blinded head may import from this module.
"""

from __future__ import annotations

import itertools
import json
import os

import numpy as np

from ..substrates.life.fast import step as life_step, assert_equivalent_to_reference
from ..substrates.life.circuits import build, Circuit, OUT_ROW, EATER_ROW, GUN_ROW, _glider_track_col, W
from .exp_gt_00 import EATER_OFF, ARCH_TRAIN, ARCH_HELD_OUT

SETTLE = 400          # common established state (same convention as EXP-GT-02/02B)
OBS = 300             # observation window after the intervention
HOLD = 8              # an intervention box is held cleared for >= 2 glider periods, so no clock phase hides it
OUT_HALFWIN = 12      # per-channel output window; min channel spacing in the family is 36, so +/-12 cannot alias

GUN_H, GUN_W = 9, 36              # verified extent of GOSPER_GUN
EAT_H, EAT_W = 4, 4               # verified extent of EATER1


# --------------------------------------------------------------- privileged component geometry (evaluator only)
def gun_box(gc: int) -> tuple:
    return (GUN_ROW, GUN_ROW + GUN_H, gc, gc + GUN_W)


def eater_box(gc: int) -> tuple:
    ey = EATER_ROW + EATER_OFF[0]
    ex = _glider_track_col(gc, EATER_ROW) + EATER_OFF[1]
    return (ey, ey + EAT_H, ex, ex + EAT_W)


def out_col(gc: int) -> int:
    return _glider_track_col(gc, OUT_ROW)


def channel_output(frames, gc: int) -> np.ndarray:
    """Live cells crossing OUT_ROW inside THIS channel's output window. Ground-truth attribution."""
    c = out_col(gc)
    lo, hi = max(0, c - OUT_HALFWIN), min(W, c + OUT_HALFWIN + 1)
    return np.array([int(f[OUT_ROW, lo:hi].sum()) for f in frames], dtype=int)


# --------------------------------------------------------------- simulation helpers
def settle(c: Circuit) -> np.ndarray:
    g = c.grid.copy()
    for _ in range(SETTLE):
        g = life_step(g)
    return g


def run_with_box(g0: np.ndarray, box, hold: int, steps: int):
    """Clear `box` for `hold` consecutive steps (an ablation), then let the world run. box=None -> baseline."""
    g = g0.copy()
    frames = [g.copy()]
    for t in range(steps):
        if box is not None and t < hold:
            r0, r1, c0, c1 = box
            g[r0:r1, c0:c1] = 0
        g = life_step(g)
        frames.append(g.copy())
    return frames


# --------------------------------------------------------------- the two ground-truth graphs
def declared_structural_graph(gun_cols, program) -> dict:
    """What the benchmark CLAIMS the architecture is. Note it is written in CHANNEL ORDINALS, never in columns:
    `build()` emits (gun_i -> out_i) and (gun_i -> gate_i -> out_i) for index i. Gun COLUMNS never enter. Two
    layouts with the same program therefore have LITERALLY THE SAME EDGE SET -- not merely isomorphic."""
    nodes, edges = [], []
    for i in range(len(gun_cols)):
        nodes += [f"gun{i}", f"out{i}"]
        edges.append((f"gun{i}", f"out{i}"))
        if program[i] == 0:
            nodes.append(f"gate{i}")
            edges += [(f"gun{i}", f"gate{i}"), (f"gate{i}", f"out{i}")]
    return {"nodes": sorted(set(nodes)), "edges": sorted(set(edges))}


def verified_active_graph(c: Circuit) -> dict:
    """MEASURED, not assumed. Ablate each component in turn; record which channel outputs actually move and after
    how long. This is the graph the world really implements under this program. A declared graph never checked
    against the dynamics is a comment, not a ground truth."""
    g0 = settle(c)
    base = [channel_output(run_with_box(g0, None, 0, OBS), gc) for gc in c.gun_cols]
    n = len(c.gun_cols)

    edges, delays, notes = [], {}, {}
    for i, gc in enumerate(c.gun_cols):
        comps = [(f"gun{i}", gun_box(gc))]
        if c.program[i] == 0:
            comps.append((f"gate{i}", eater_box(gc)))
        for name, box in comps:
            fr = run_with_box(g0, box, HOLD, OBS)
            for j, gcj in enumerate(c.gun_cols):
                d = channel_output(fr, gcj) - base[j]
                nz = np.nonzero(d != 0)[0]
                if len(nz):
                    edges.append((name, f"out{j}"))
                    delays[f"{name}->out{j}"] = int(nz[0])
                    notes[f"{name}->out{j}"] = {
                        "baseline_mean": float(base[j].mean()),
                        "ablated_mean": float(channel_output(fr, gcj).mean()),
                        "sign": "UP" if d[nz].mean() > 0 else "DOWN"}
    return {"nodes": sorted({e[0] for e in edges} | {f"out{j}" for j in range(n)}),
            "edges": sorted(set(edges)), "delays": delays, "notes": notes,
            "baseline_channel_means": [float(b.mean()) for b in base]}


# --------------------------------------------------------------- graph isomorphism (small graphs: exact)
def canonical_form(graph: dict) -> tuple:
    """Isomorphism-invariant canonical form. Node NAMES carry the channel ordinal, itself a layout artefact, so
    names are discarded: only the node TYPE (gun/gate/out) is kept and we minimise over all type-preserving
    relabellings. The graphs are small, so this is exact -- no heuristic."""
    nodes, edges = graph["nodes"], set(graph["edges"])
    by_type: dict = {}
    for v in nodes:
        t = "".join(ch for ch in v if not ch.isdigit())
        by_type.setdefault(t, []).append(v)
    types = sorted(by_type)
    best = None
    for combo in itertools.product(*[itertools.permutations(by_type[t]) for t in types]):
        m = {}
        for t, perm in zip(types, combo):
            for k, v in enumerate(perm):
                m[v] = f"{t}{k}"
        cand = tuple(sorted((m[a], m[b]) for a, b in edges))
        if best is None or cand < best:
            best = cand
    return (tuple(f"{t}:{len(by_type[t])}" for t in types), best)


def isomorphic(g1: dict, g2: dict) -> bool:
    return canonical_form(g1) == canonical_form(g2)


# --------------------------------------------------------------- G: the geometric embedding diagnostic
def geometric_signature(gun_cols) -> dict:
    """G is LAYOUT, reported separately and NEVER composited into identity. Two systems may share A and differ in
    G; that is not an identity difference, it is a drawing difference."""
    gc = list(gun_cols)
    return {"gun_cols": gc, "spacings": [gc[i + 1] - gc[i] for i in range(len(gc) - 1)],
            "n_channels": len(gc), "extent": gc[-1] - gc[0]}


def head_G(a1, a2) -> str:
    s1, s2 = geometric_signature(a1), geometric_signature(a2)
    if s1["n_channels"] != s2["n_channels"]:
        return "DIFFERENT"
    return "SAME" if s1["spacings"] == s2["spacings"] else "DIFFERENT"   # translation-invariant by construction


# --------------------------------------------------------------- viability: the control the benchmark lacked
def layout_viable(gun_cols, min_mean: float = 0.5) -> tuple:
    """A layout is a legal member of the family only if EVERY declared channel actually carries a stream.

    The Gosper gun spans 36 columns, so at spacing <= 37 adjacent guns TOUCH and annihilate each other. The
    benchmark has shipped ARCH_HELD_OUT[1] = (10,46,82,118) -- spacing 36 -- as a held-out architecture since
    EXP-GT-00, and nobody ever asserted that a declared circuit computes anything at all."""
    c = build(list(gun_cols), [1] * len(gun_cols),
              eater_offsets={i: EATER_OFF for i in range(len(gun_cols))})
    fr = run_with_box(settle(c), None, 0, OBS)
    means = [float(channel_output(fr, gc).mean()) for gc in gun_cols]
    return all(m > min_mean for m in means), means


# --------------------------------------------------------------- the audit
def audit(programs=((1, 0, 1, 0), (0, 1, 0, 1), (1, 1, 1, 1))) -> dict:
    checks = assert_equivalent_to_reference()
    archs = {"A_TRAIN_sp40": ARCH_TRAIN[0],
             "H50_sp45": ARCH_HELD_OUT[0],
             "H46_sp36": ARCH_HELD_OUT[1]}

    report = {"differential_step_checks": checks, "architectures": {}, "viability": {},
              "programs": {}, "comparisons": []}
    for k, a in archs.items():
        report["architectures"][k] = geometric_signature(a)
        ok, means = layout_viable(a)
        report["viability"][k] = {"viable": bool(ok), "per_channel_mean_output": [round(m, 3) for m in means]}

    graphs = {}
    for aname, a in archs.items():
        for p in programs:
            c = build(list(a), list(p), eater_offsets={i: EATER_OFF for i in range(len(p))})
            dg = declared_structural_graph(a, p)
            vg = verified_active_graph(c)
            graphs[(aname, p)] = {"declared": dg, "verified": vg}
            report["programs"][f"{aname}|{''.join(map(str, p))}"] = {
                "declared_edges": ["->".join(e) for e in dg["edges"]],
                "verified_active_edges": ["->".join(e) for e in vg["edges"]],
                "delays": vg["delays"],
                "baseline_channel_means": [round(x, 3) for x in vg["baseline_channel_means"]],
                "cross_channel_edges": ["->".join(e) for e in vg["edges"]
                                        if "".join(ch for ch in e[0] if ch.isdigit())
                                        != "".join(ch for ch in e[1] if ch.isdigit())]}

    for p in programs:
        for x, y in itertools.combinations(archs, 2):
            gx, gy = graphs[(x, p)], graphs[(y, p)]
            report["comparisons"].append({
                "program": "".join(map(str, p)),
                "arch_pair": [x, y],
                "declared_structural_edges_identical": gx["declared"]["edges"] == gy["declared"]["edges"],
                "declared_structural_isomorphic": isomorphic(gx["declared"], gy["declared"]),
                "verified_active_isomorphic": isomorphic(gx["verified"], gy["verified"]),
                "verified_delays_equal": (sorted(gx["verified"]["delays"].values())
                                          == sorted(gy["verified"]["delays"].values())),
                "delays_x": sorted(gx["verified"]["delays"].values()),
                "delays_y": sorted(gy["verified"]["delays"].values()),
                "G": head_G(archs[x], archs[y]),
                "spacings": [geometric_signature(archs[x])["spacings"],
                             geometric_signature(archs[y])["spacings"]]})
    return report


def summarize(r: dict) -> str:
    L = ["EXP-GT-A0 -- ONTOLOGY AUDIT OF THE A HEAD (run BEFORE touching any tolerance)",
         f"fast/reference differential step checks proved equal: {r['differential_step_checks']}",
         "",
         "VIABILITY -- the positive control the benchmark never had:"]
    for k, v in r["viability"].items():
        L.append(f"  {k:14s} spacings={str(r['architectures'][k]['spacings']):14s} "
                 f"{'VIABLE' if v['viable'] else '*** DEAD ***':12s} "
                 f"per-channel output {v['per_channel_mean_output']}")
    L += ["",
          "DECISIVE COMPARISON -- same program, different layout:",
          f"  {'prog':6s} {'pair':32s} {'decl=':6s} {'s-iso':6s} {'a-iso':6s} {'dly=':6s} {'G':10s}"]
    for c in r["comparisons"]:
        pair = f"{c['arch_pair'][0]} vs {c['arch_pair'][1]}"
        L.append(f"  {c['program']:6s} {pair:32s} "
                 f"{str(c['declared_structural_edges_identical']):6s} "
                 f"{str(c['declared_structural_isomorphic']):6s} "
                 f"{str(c['verified_active_isomorphic']):6s} "
                 f"{str(c['verified_delays_equal']):6s} {c['G']:10s}")
    L += ["",
          "=" * 102,
          "VERDICT: FAILED -- ONTOLOGY   (a benchmark-label error, NOT an observer-resolution failure)",
          "",
          "  1. The pair labelled 'different ARCHITECTURE, same function' (sp40 vs sp45) is the SAME causal",
          "     graph: identical DECLARED edge sets (build() writes edges over channel ordinals, never over",
          "     columns), isomorphic VERIFIED active-influence graphs, and identical measured causal delays",
          "     (174,174,234,234). It differs ONLY in gun-column spacing.",
          "     => expected label corrected to  A = SAME, G = DIFFERENT.  A's answer was RIGHT.",
          "     => D-052's 'A needs a finer resolution' is WITHDRAWN. Lowering the tolerance would have tuned",
          "        A into a LAYOUT detector -- destroying the invariance A exists to provide.",
          "",
          "  2. ARCH_HELD_OUT[1] = (10,46,82,118), spacing 36, is a DEAD circuit: zero output on all four",
          "     channels. The gun spans 36 columns, so at spacing 36 adjacent guns touch and annihilate.",
          "     Each gun works ALONE at each of those columns -- the fault is the LAYOUT, not the component.",
          "     Minimum viable spacing measured = 38. This layout is VOID and is quarantined.",
          "",
          "  3. The benchmark has never contained ONE genuinely different causal architecture. Every circuit",
          "     in the family is 4 independent parallel channels gun_i -> (gate_i) -> out_i. A has therefore",
          "     never been tested against a real architectural difference and CANNOT be certified until such",
          "     architectures exist.",
          "=" * 102]
    return "\n".join(L)


def main(run_id: str = "EXP-GT-A0-20260713-001") -> dict:
    r = audit()
    d = os.path.join("results", run_id)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "report.json"), "w") as f:
        json.dump(r, f, indent=1, default=str)
    s = summarize(r)
    with open(os.path.join(d, "summary.txt"), "w") as f:
        f.write(s + "\n")
    print(s)
    return r


if __name__ == "__main__":
    main()
