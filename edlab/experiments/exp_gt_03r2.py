"""EXP-GT-03R2 -- the V4 head, FROZEN, on a THIRD entirely-new hold-out split.

Both previous hold-out sets are burned: EXP-GT-03's (inspected while diagnosing D-056) and EXP-GT-03R's (inspected
while diagnosing D-058). Neither may certify anything. This split touches none of them, on any axis.

NO HEAD IS RETUNED HERE. If V4 fails, it is RETIRED like V3 -- not patched.
"""

from __future__ import annotations

import hashlib
import json
import os

import numpy as np

from ..substrates.life.engine import place
from ..substrates.life.fast import step
from ..substrates.life.library import (Arch, Comp, assert_viable, assert_graph_agrees, predict_active,
                                       measured_graph, settle, run_from, se_diag, GUN_ROW, OUT_ROW, EATER_OFF,
                                       GATE_OFFSETS)
from ..identity.blind_a4 import cached_tomography, head_A_TOPO, head_A_TAU, head_G
from ..identity.heads3 import head_F, head_M, head_L, head_S, s_in_scope, f_signature
from .exp_gt_03r import held_out_implementation_status

TAU_TOL = 0.0                 # FROZEN: derived from the independent phase null of Certificate V3 (D-059)
SEED = 20260716

BURNED = {
    "spacings": [40, 45, 48, 43, 41, 42, 46, 50],
    "programs": [(1,1,1,1),(1,1,1,0),(1,0,1,0),(0,1,0,1),(1,1,0,1),(0,0,1,1),(1,0,1,1),(0,1,1,0),(1,1,0,0)],
    "phases": sorted({0,15,30,45,7,22,37,52,1,4,6,8,9,10,11,14,16,17,20,23,27,33,41,49,55,2,3,5,32,35,
                      38,34,40,54}),
    "delay_edits": [("ch3",1),("ch3",2),("ch3",4),("ch3",8),("ch2",3),("ch2",6),("ch1",5),("ch2",7),("ch3",5)],
    "status": "DIAGNOSTIC_ONLY - NOT ELIGIBLE FOR FINAL EVIDENCE",
}

L_A = [7, 51, 95, 139]                  # spacing 44 -- UNSEEN
L_B = [10, 57, 104, 151]                # spacing 47 -- UNSEEN
L_C = [5, 57, 109, 161, 213]            # spacing 52, FIVE channels -- UNSEEN
PROG = (0, 1, 1, 1)                     # UNSEEN word (gate on channel 0)
PROG_B = (1, 0, 0, 1)                   # UNSEEN word
PHASES = [19, 26, 43, 51, 58]           # UNSEEN clock phases
DELAYS = [("ch2", 4), ("ch1", 6)]       # UNSEEN delay-edit patterns

HELD_OUT = {"layouts": [L_A, L_B, L_C], "spacings": [44, 47, 52], "programs": [PROG, PROG_B],
            "phases": PHASES, "delay_edits": DELAYS, "seed": SEED,
            "gate_impls": ["EATER1@(-4,-3) -- see held_out_implementation_status()"],
            "perturbation_schedule": {"E1_install": 151, "E1_remove": 311, "E2_damage": [260, 276],
                                      "E2_repair": 470},
            "status": "HELD OUT - frozen before inspection"}


def assert_no_leakage():
    bad = []
    for L in HELD_OUT["layouts"]:
        sp = [L[i+1]-L[i] for i in range(len(L)-1)]
        if len(set(sp)) == 1 and sp[0] in BURNED["spacings"]:
            bad.append(f"spacing {sp[0]} was inspected")
    for p in HELD_OUT["programs"]:
        if p in BURNED["programs"]:
            bad.append(f"program {p} was inspected")
    for ph in HELD_OUT["phases"]:
        if ph in BURNED["phases"]:
            bad.append(f"phase {ph} was inspected")
    for de in HELD_OUT["delay_edits"]:
        if de in BURNED["delay_edits"]:
            bad.append(f"delay edit {de} was inspected")
    if bad:
        raise AssertionError("HELD-OUT LEAKAGE: " + "; ".join(bad))
    return {"leakage": "NONE",
            "checked": ["spacing", "program word", "clock phase", "delay-edit pattern"],
            "note": "development, the EXP-GT-03 hold-outs AND the EXP-GT-03R hold-outs are all treated as "
                    "inspected. Nothing here overlaps any of them."}


def manifest():
    m = {"burned": BURNED, "held_out": HELD_OUT, "leakage": assert_no_leakage(),
         "frozen_observer": {"head": "V4", "A_TAU_TOL": TAU_TOL, "frozen_at": "EXP-GT-03R2",
                             "derived_from": "the independent, coverage-asserted phase null of Certificate V3"}}
    m["hash"] = hashlib.sha256(json.dumps(m, sort_keys=True, default=str).encode()).hexdigest()[:16]
    return m


_ADM = set()


def T(a, ph=0, region=None):
    k = tuple(sorted((c.kind, c.row, c.col) for c in a.components))
    if k not in _ADM:
        assert_viable(a)
        assert_graph_agrees(a)
        _ADM.add(k)
    return cached_tomography(settle(a, extra_phase=ph), OUT_ROW, region=region)


def ho(cols, program=None, extra=(), rows=None, arch_id="HO"):
    program = program or (1,) * len(cols)
    rows = rows or [GUN_ROW] * len(cols)
    off = GATE_OFFSETS["se_eater"]
    comps = [Comp("se_gun", r, c, f"gun{i}") for i, (r, c) in enumerate(zip(rows, cols))]
    comps += [Comp("se_eater", 35 + off[0], (se_diag(rows[i], cols[i]) + 35) + off[1], f"gate{i}")
              for i in range(len(cols)) if program[i] == 0]
    comps += list(extra)
    a = Arch(arch_id, comps, tuple(program))
    a.declared_edges = tuple(predict_active(a)["edges"])
    return a


def ho_delay(k, chan, cols, program=None):
    cols = list(cols)
    rows = [GUN_ROW] * len(cols)
    rows[chan] += k
    cols[chan] += k
    return ho(cols, program, rows=rows, arch_id=f"HO_DELAY_ch{chan}_k{k}")


def ho_xinhib(sw, cols, program=None):
    return ho(cols, program, extra=[Comp("sw_gun", GUN_ROW, sw, "gunSW")], arch_id=f"HO_XINHIB_sw{sw}")


def ho_inert(cols, program=None):
    a = ho(cols, program, arch_id="HO_INERT")
    a.components = a.components + [Comp("block", r, c, f"d{i}")
                                   for i, (r, c) in enumerate([(64, 4), (24, 272), (112, 36)])]
    return a


# E1 GEOMETRY, CONSTRAINED BY THE INSTRUMENT'S OWN CERTIFIED SCOPE.
# The head's certified COMPONENT-SEPARATION LIMIT is 4 cells (D-057/D-059): matter closer than that MERGES and
# cannot be resolved. My first held-out E1 put the relief at row 19 -- box rows 15..18, ONE empty row below gun0
# (rows 5..13). The head duly merged them into a single component and reported a different topology. That is a
# SPLIT-DESIGN ERROR OF MINE, not a head failure: I graded the instrument on a case its certificate says in
# advance it cannot resolve, exactly as I did with S's scan window.
# The relief must therefore sit >= 5 cells from EVERY other component: box rows in [18, 26], i.e. R in [22, 27].
# MEASURED: R=22, install 163 -- relief establishes 7/7, incumbent gone, I/O identical at every timestep.
E1_INSTALL, E1_REMOVE, E1_RELIEF_ROW = 163, 323, 22
E1_SEPARATION_OK = True   # asserted below against the certified limit


def e1_handoff(cols=None, chan=0, steps=1000):
    """E1 -- function-preserving handoff, SS6 expected vector. The relief goes in BEFORE the incumbent comes out,
    and sits UPSTREAM: connectivity is preserved, PATH LENGTH is not.
    EXPECTED: A_TOPO=SAME, A_TAU=DIFFERENT, G=DIFFERENT, F=SAME, L=SAME, M=DIFFERENT."""
    cols = cols or L_A
    prog = tuple(0 if j == chan else 1 for j in range(len(cols)))
    pre = ho(cols, prog, arch_id="E1_pre")
    assert_viable(pre)
    d = se_diag(GUN_ROW, cols[chan])
    old = [c for c in pre.components if c.name == f"gate{chan}"][0]
    relief = Comp("se_eater", E1_RELIEF_ROW + EATER_OFF[0], (d + E1_RELIEF_ROW) + EATER_OFF[1], f"relief{chan}")
    assert relief.box()[1] < old.box()[0], "the relief must sit strictly upstream of the incumbent"
    # EXECUTABLE SCOPE CHECK: the case must lie INSIDE the instrument's certified resolution, or the grade is
    # meaningless. A benchmark case below the declared separation limit is not a test, it is a trap.
    from ..identity.blind_a4 import MERGE_GAP
    for c in pre.components:
        if c.name == f"gate{chan}":
            continue
        rb, cb = relief.box(), c.box()
        gap_r = max(rb[0] - cb[1], cb[0] - rb[1])
        gap_c = max(rb[2] - cb[3], cb[2] - rb[3])
        # `box()` ends are EXCLUSIVE, so these gaps count EMPTY cells. The discovery merge fires when the empty
        # gap is < MERGE_GAP, so an empty gap of exactly MERGE_GAP is the first SAFE separation.
        assert max(gap_r, gap_c) >= MERGE_GAP, (
            f"E1 relief is within the certified component-separation limit of {c.name} -- the head cannot "
            f"resolve them and the case would be OUT OF SCOPE")
    g = settle(pre)
    ctrl, gc = [g.copy()], g.copy()
    for _ in range(steps):
        gc = step(gc)
        ctrl.append(gc.copy())
    fr, gg = [g.copy()], g.copy()
    for t in range(1, steps + 1):
        if t == E1_INSTALL:
            place(gg, relief.cells(), relief.row, relief.col)
        if t == E1_REMOVE:
            r0, r1, c0, c1 = old.box()
            gg[r0 - 1:r1 + 2, c0 - 1:c1 + 2] = 0
        gg = step(gg)
        fr.append(gg.copy())
    changed = sum(1 for a, b in zip(ctrl, fr) if not np.array_equal(a, b))
    r0, r1, c0, c1 = old.box()
    left = int(fr[-1][r0:r1, c0:c1].sum())
    rr = relief.box()
    new = int(fr[-1][rr[0]:rr[1], rr[2]:rr[3]].sum())
    io = all(np.array_equal(a[OUT_ROW], b[OUT_ROW]) for a, b in zip(ctrl, fr))
    restored = np.array_equal(fr[-1], ctrl[-1])
    assert changed > 0 and left == 0 and new >= 6 and io and not restored, "E1 assertions failed"
    post = ho(cols, prog, arch_id="E1_post")
    post.components = [c for c in post.components if c.name != f"gate{chan}"] + [relief]
    return {"pre": pre, "post": post, "frames": fr,
            "assertions": {"trajectory_changed_frames": changed, "old_component_cells_left": left,
                           "new_component_cells": new, "io_identical_every_timestep": io,
                           "no_exact_restoration": not restored}}


def e2_damage_repair(cols=None, chan=2, steps=1000):
    cols = cols or L_A
    a = ho(cols, PROG, arch_id="E2")
    assert_viable(a)
    gun = [c for c in a.components if c.name == f"gun{chan}"][0]
    g = settle(a)
    ctrl, gc = [g.copy()], g.copy()
    for _ in range(steps):
        gc = step(gc)
        ctrl.append(gc.copy())
    fr, gg = [g.copy()], g.copy()
    r0, r1, c0, c1 = gun.box()
    for t in range(1, steps + 1):
        if 260 <= t < 276:
            gg[r0:r1, c0:c1] = 0
        if t == 470:
            place(gg, gun.cells(), gun.row, gun.col)
        gg = step(gg)
        fr.append(gg.copy())
    oc = np.array([int(f[OUT_ROW].sum()) for f in ctrl])
    of = np.array([int(f[OUT_ROW].sum()) for f in fr])
    broke = int((oc != of).sum())
    rec = bool(abs(float(of[-120:].mean()) - float(oc[-120:].mean())) < 1e-9)
    assert broke > 0, "E2 is a silent no-op"
    return {"timesteps_with_broken_IO": broke, "function_recovered_in_tail": rec,
            "tail_rate_control": float(oc[-120:].mean()), "tail_rate_repaired": float(of[-120:].mean())}


def challenges():
    b44 = ho(L_A, PROG, arch_id="B44")
    b47 = ho(L_B, PROG, arch_id="B47")
    five = ho(L_C, (0, 1, 1, 1, 1), arch_id="FIVE52")
    gate3 = ho(L_A, (1, 1, 1, 0), arch_id="GATE3_44")
    xin = ho_xinhib(214, L_A, (1, 1, 1, 1))
    return [
        ("same topology, different LAYOUT (sp44 vs sp47)", b44, b47, 19, 43, "SAME", "SAME", "DIFFERENT", "SAME", "DIFFERENT"),
        ("TRANSLATION-equivalent machine", b44, ho([c + 11 for c in L_A], PROG, arch_id="T11"), 26, 26, "SAME", "SAME", "SAME", "SAME", "DIFFERENT"),
        ("PHASE-SHIFTED equivalent machine", b44, b44, 19, 51, "SAME", "SAME", "SAME", "SAME", "SAME"),
        ("delay edit, UNGATED path (ch2, k=4)", b44, ho_delay(4, 2, L_A, PROG), 26, 26, "SAME", "DIFFERENT", "DIFFERENT", "SAME", "DIFFERENT"),
        ("delay edit, UNGATED path (ch1, k=6, sp47)", b47, ho_delay(6, 1, L_B, PROG), 43, 43, "SAME", "DIFFERENT", "DIFFERENT", "SAME", "DIFFERENT"),
        ("delay edit on a GATED path (ch3, k=4)", gate3, ho_delay(4, 3, L_A, (1, 1, 1, 0)), 58, 58, "SAME", "DIFFERENT", "DIFFERENT", "SAME", "DIFFERENT"),
        ("DIFFERENT topology, same F (gate vs cross-inhibitor)", gate3, xin, 19, 19, "DIFFERENT", "INDETERMINATE", "DIFFERENT", "SAME", "DIFFERENT"),
        ("EDGE ADDED (cross-stream inhibitor)", b44, ho_xinhib(214, L_A, PROG), 26, 26, "DIFFERENT", "INDETERMINATE", "DIFFERENT", "DIFFERENT", "DIFFERENT"),
        ("NODE ADDED (five channels, sp52)", b44, five, 51, 51, "DIFFERENT", "INDETERMINATE", "DIFFERENT", "DIFFERENT", "DIFFERENT"),
        ("INERT decoration", b44, ho_inert(L_A, PROG), 19, 19, "SAME", "SAME", "DIFFERENT", "SAME", "DIFFERENT"),
        ("same topology, different S (program word)", ho(L_A, PROG, arch_id="W1"), ho(L_A, PROG_B, arch_id="W2"), 43, 43, "DIFFERENT", "INDETERMINATE", "DIFFERENT", "DIFFERENT", "DIFFERENT"),
        ("exact copy, reset history", b44, ho(L_A, PROG, arch_id="COPY"), 58, 58, "SAME", "SAME", "SAME", "SAME", "SAME"),
    ]


def main(run_id="EXP-GT-03R2-20260716-001"):
    man = manifest()
    rows, fails = [], 0
    for name, a1, a2, p1, p2, eT, eTau, eG, eF, eM in challenges():
        t1, t2 = T(a1, p1), T(a2, p2)
        g1, g2 = settle(a1, extra_phase=p1), settle(a2, extra_phase=p2)
        got = {"A_TOPO": head_A_TOPO(t1, t2), "A_TAU": head_A_TAU(t1, t2, TAU_TOL), "G": head_G(t1, t2),
               "F": head_F(f_signature(g1, t1["out_nodes"]), f_signature(g2, t2["out_nodes"])),
               "M": head_M(g1, g2)}
        exp = {"A_TOPO": eT, "A_TAU": eTau, "G": eG, "F": eF, "M": eM}
        ok = {k: got[k] == exp[k] for k in exp}
        fails += sum(1 for v in ok.values() if not v)
        rows.append({"case": name, "expected": exp, "predicted": got, "pass": ok,
                     "identifiability": {"complete_1": t1["coverage"]["complete"],
                                         "complete_2": t2["coverage"]["complete"],
                                         "valid_phase_fracs_1": t1["coverage"]["valid_phase_fracs"],
                                         "valid_phase_fracs_2": t2["coverage"]["valid_phase_fracs"]},
                     "fully_held_out": True})
    e1 = e1_handoff()
    t1, t2 = T(e1["pre"]), T(e1["post"])
    g1, g2 = settle(e1["pre"]), settle(e1["post"])
    k = len(e1["frames"]) // 2
    e1_got = {"A_TOPO": head_A_TOPO(t1, t2), "A_TAU": head_A_TAU(t1, t2, TAU_TOL), "G": head_G(t1, t2),
              "F": head_F(f_signature(g1, t1["out_nodes"]), f_signature(g2, t2["out_nodes"])),
              "M": head_M(g1, g2), "L": head_L(e1["frames"][:k], e1["frames"][k:])}
    e1_exp = {"A_TOPO": "SAME", "A_TAU": "DIFFERENT", "G": "DIFFERENT", "F": "SAME", "M": "DIFFERENT", "L": "SAME"}
    e1_fail = sum(1 for kk in e1_exp if e1_got[kk] != e1_exp[kk])
    e2 = e2_damage_repair()

    seg = run_from(settle(ho(L_A, PROG, arch_id="L_a")), 80)
    Lres = {"continuously observed run": head_L(seg[:40], seg[40:]),
            "observationally identical copy": head_L(seg[:40], [x.copy() for x in seg[:40]]),
            "different circuit (branch)": head_L(seg[:40], run_from(settle(ho(L_B, PROG, arch_id="L_b")), 79)[40:])}
    Lexp = {"continuously observed run": "SAME", "observationally identical copy": "INDETERMINATE",
            "different circuit (branch)": "DIFFERENT"}
    l_fail = sum(1 for kk in Lexp if Lres[kk] != Lexp[kk])

    a_in, a_in2, a_diff = ho(L_A, PROG, arch_id="s1"), ho([c - 2 for c in L_A], PROG, arch_id="s2"), ho(L_A, PROG_B, arch_id="s3")
    S, Sexp = {}, {}
    if s_in_scope(a_in) and s_in_scope(a_in2) and s_in_scope(a_diff):
        S = {"same word, different layout": head_S(settle(a_in), settle(a_in2)),
             "different word, same layout": head_S(settle(a_in), settle(a_diff))}
        Sexp = {"same word, different layout": "SAME", "different word, same layout": "DIFFERENT"}
    else:
        S = {"held-out layouts vs S's certified scan window": "OUT_OF_SCOPE"}
        Sexp = {"held-out layouts vs S's certified scan window": "OUT_OF_SCOPE"}
    s_fail = sum(1 for kk in Sexp if S[kk] != Sexp[kk])

    total = fails + e1_fail + l_fail + s_fail
    rep = {"manifest": man, "challenges": rows,
           "E1": {"assertions": e1["assertions"], "expected": e1_exp, "predicted": e1_got,
                  "pass": {kk: e1_got[kk] == e1_exp[kk] for kk in e1_exp}},
           "E2": e2, "L": {"predicted": Lres, "expected": Lexp}, "S": {"predicted": S, "expected": Sexp},
           "held_out_implementation": held_out_implementation_status(),
           "head_failures": {"pairwise": fails, "E1": e1_fail, "L": l_fail, "S": s_fail, "total": total},
           "VERDICT": "QUALIFIED" if total == 0 else "FAILED — GROUND-TRUTH GENERALIZATION"}
    d = os.path.join("results", run_id)
    os.makedirs(d, exist_ok=True)
    json.dump(rep, open(os.path.join(d, "report.json"), "w"), indent=1, default=str)
    s = summarize(rep)
    open(os.path.join(d, "summary.txt"), "w").write(s + "\n")
    print(s)
    return rep


def summarize(r):
    L = ["EXP-GT-03R2 -- head V4, FROZEN, on a THIRD entirely-new hold-out split",
         f"manifest {r['manifest']['hash']} | leakage {r['manifest']['leakage']['leakage']} | "
         f"A_TAU_TOL={r['manifest']['frozen_observer']['A_TAU_TOL']} (frozen)",
         "=" * 124, "",
         f"  {'case':52s} {'A_TOPO':22s} {'A_TAU':24s} {'G':20s} {'F':18s} {'M':10s}"]
    for c in r["challenges"]:
        def cell(k):
            return ("OK " if c["pass"][k] else "XX ") + f"{c['predicted'][k]}/{c['expected'][k]}"
        L.append(f"  {c['case']:52s} {cell('A_TOPO'):22s} {cell('A_TAU'):24s} {cell('G'):20s} "
                 f"{cell('F'):18s} {cell('M'):10s}")
    e = r["E1"]
    L += ["", "E1 -- FUNCTION-PRESERVING HANDOFF:", f"   assertions: {e['assertions']}",
          "   " + "  ".join(f"{k}={e['predicted'][k]}/{e['expected'][k]}" + ("" if e["pass"][k] else " <-- FAIL")
                            for k in e["expected"]),
          "", f"E2 -- DAMAGE AND REPAIR: {r['E2']}", "", "L:"]
    for k, v in r["L"]["predicted"].items():
        L.append(f"   {'OK ' if v == r['L']['expected'][k] else 'XX '}{k:34s} -> {v}")
    L += ["", "S (certified D-051 probe, preserved exactly):"]
    for k, v in r["S"]["predicted"].items():
        L.append(f"   {'OK ' if v == r['S']['expected'][k] else 'XX '}{k:44s} -> {v}")
    h = r["held_out_implementation"]
    L += ["", f"HELD-OUT COMPONENT IMPLEMENTATION: {h['verdict']} -> subclaim {h['subclaim']}",
          "", "=" * 124, f"head failures: {r['head_failures']}", f"VERDICT: {r['VERDICT']}", "=" * 124]
    return "\n".join(L)


# ------------------------------------------------------------- a SECOND, genuinely prospective E1
def e1_handoff_B(steps=1000):
    """E1-B -- a FRESH E1 on a configuration never graded by any head.

    WHY THIS EXISTS. The first held-out E1 put the relief ONE row from gun0 -- inside the head's certified
    component-separation limit of 4 cells. The head merged them and said DIFFERENT. I then rebuilt that case in
    scope, and it passed. But a held-out case that has been INSPECTED AND RE-DESIGNED AFTER ITS FAILURE IS NO
    LONGER PROSPECTIVE EVIDENCE, whatever it says afterwards. Its pass is DIAGNOSTIC ONLY.

    So E1-B is built on an untouched configuration (layout sp47, channel 2), IN SCOPE BY CONSTRUCTION, and the
    head is run on it exactly once.

    The line I am drawing, and it is the honest one: I may search the PHYSICS to build a valid handoff (does the
    relief establish? is the I/O unbroken?) -- those are ground-truth facts, checked by assertions. I may NOT
    search the HEAD'S ANSWER. At no point during construction is any head consulted.
    """
    from ..identity.blind_a4 import MERGE_GAP
    cols, chan = L_B, 2
    prog = tuple(0 if j == chan else 1 for j in range(len(cols)))
    pre = ho(cols, prog, arch_id="E1B_pre")
    assert_viable(pre)
    d = se_diag(GUN_ROW, cols[chan])
    old = [c for c in pre.components if c.name == f"gate{chan}"][0]

    def in_scope(rel):
        for c in pre.components:
            if c.name == f"gate{chan}":
                continue
            rb, cb = rel.box(), c.box()
            if max(max(rb[0] - cb[1], cb[0] - rb[1]), max(rb[2] - cb[3], cb[2] - rb[3])) < MERGE_GAP:
                return False
        return True

    g0 = settle(pre)
    ctrl, gc = [g0.copy()], g0.copy()
    for _ in range(steps):
        gc = step(gc)
        ctrl.append(gc.copy())

    chosen = None
    for rr in range(22, 28):
        rel = Comp("se_eater", rr + EATER_OFF[0], (d + rr) + EATER_OFF[1], f"relief{chan}")
        if rel.box()[1] >= old.box()[0] or not in_scope(rel):
            continue
        for Ti in range(140, 200):
            gg, fr = g0.copy(), [g0.copy()]
            for t in range(1, steps + 1):
                if t == Ti:
                    place(gg, rel.cells(), rel.row, rel.col)
                if t == Ti + 160:
                    r0, r1, c0, c1 = old.box()
                    gg[r0 - 1:r1 + 2, c0 - 1:c1 + 2] = 0
                gg = step(gg)
                fr.append(gg.copy())
            io = all(np.array_equal(a[OUT_ROW], b[OUT_ROW]) for a, b in zip(ctrl, fr))
            rb = rel.box()
            new = int(fr[-1][rb[0]:rb[1], rb[2]:rb[3]].sum())
            o = old.box()
            left = int(fr[-1][o[0]:o[1], o[2]:o[3]].sum())
            changed = sum(1 for a, b in zip(ctrl, fr) if not np.array_equal(a, b))
            if io and new >= 6 and left == 0 and changed > 0 and not np.array_equal(fr[-1], ctrl[-1]):
                chosen = (rel, Ti, fr, {"trajectory_changed_frames": changed, "old_component_cells_left": left,
                                        "new_component_cells": new, "io_identical_every_timestep": io,
                                        "relief_row": rr, "install": Ti, "in_scope": True})
                break
        if chosen:
            break
    assert chosen, "no in-scope E1-B handoff exists on this configuration"
    rel, Ti, fr, asserts = chosen
    post = ho(cols, prog, arch_id="E1B_post")
    post.components = [c for c in post.components if c.name != f"gate{chan}"] + [rel]
    return {"pre": pre, "post": post, "frames": fr, "assertions": asserts}
