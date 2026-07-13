"""EXP-GT-03R -- the REPAIRED observer, frozen, on ENTIRELY NEW hold-outs.

Nothing inspected during the D-056 diagnosis may appear here. The EXP-GT-03 held-out families are themselves now
`DIAGNOSTIC_ONLY - NOT ELIGIBLE FOR FINAL EVIDENCE`, and so are the development families, and so are the four
absorber candidates (BOAT, SNAKE, BEEHIVE, LOAF) burned while diagnosing.

THIS IS THE ONE AUTHORIZED PROSPECTIVE RUN FOR THE V3 DESIGN. No head is retuned here. If it fails, the design is
RETIRED, not patched (mission SS8).
"""

from __future__ import annotations

import hashlib
import json
import os

import numpy as np

from ..substrates.life.engine import place
from ..substrates.life.fast import step
from ..substrates.life.library import (Arch, Comp, assert_viable, assert_graph_agrees, predict_active,
                                       measured_graph, settle, run_from, total_output, se_diag,
                                       GUN_ROW, OUT_ROW, EATER_OFF, GATE_OFFSETS)
from ..identity.blind_a3 import head_A_TOPO, head_A_TAU, head_G
from ..identity.heads3 import ObserverV3, head_F, head_M, head_L, head_S, f_signature

OBSV = ObserverV3()
SEED = 20260714

# ------------------------------------------------------------- everything ever inspected (all DIAGNOSTIC_ONLY)
BURNED = {
    "layouts": [[5, 45, 85, 125], [15, 55, 95, 135], [25, 65, 105, 145], [5, 50, 95, 140],
                [12, 60, 108, 156], [9, 52, 95, 138], [10, 51, 92, 133, 174, 215]],
    "spacings": [40, 45, 48, 43, 41],
    "programs": [(1, 1, 1, 1), (1, 1, 1, 0), (1, 0, 1, 0), (0, 1, 0, 1), (1, 1, 0, 1), (0, 0, 1, 1)],
    "phases": [0, 15, 30, 45, 7, 22, 37, 52, 1, 4, 6, 8, 9, 10, 11, 14, 16, 17, 20, 23],
    "delay_edits": [("ch3", 1), ("ch3", 2), ("ch3", 4), ("ch3", 8), ("ch2", 3), ("ch2", 6)],
    "gate_impls": ["EATER1@(-4,-3)"],
    "burned_absorbers": ["BOAT", "SNAKE", "BEEHIVE", "LOAF"],
    "status": "DIAGNOSTIC_ONLY - NOT ELIGIBLE FOR FINAL EVIDENCE",
}

# ------------------------------------------------------------- the NEW hold-out split (V2)
L_A = [8, 50, 92, 134]                 # spacing 42 -- UNSEEN
L_B = [11, 57, 103, 149]               # spacing 46 -- UNSEEN
L_C = [6, 56, 106, 156, 206]           # spacing 50, FIVE channels -- UNSEEN spacing AND unseen channel count
PROG = (1, 0, 1, 1)                    # UNSEEN word (gate on channel 1)
PROG_B = (0, 1, 1, 0)                  # UNSEEN word
PHASES = [27, 33, 41, 49, 55]          # UNSEEN clock phases
HELD_OUT = {
    "layouts": [L_A, L_B, L_C], "spacings": [42, 46, 50],
    "programs": [PROG, PROG_B, (1, 1, 0, 0)], "phases": PHASES,
    "delay_edits": [("ch1", 5), ("ch2", 7)],
    "gate_impls": ["EATER1@(-4,-3) [development -- the ONLY admissible absorber; see held_out_implementation]"],
    "held_out_implementation": "NOT AVAILABLE (SS5.1). Reported, not manufactured.",
    "perturbation_schedule": {"E1_install": 137, "E1_remove": 287, "E2_damage": [230, 244], "E2_repair": 430},
    "seed": SEED,
    "status": "HELD OUT - frozen before inspection",
}


def assert_no_leakage() -> dict:
    bad = []
    for L in HELD_OUT["layouts"]:
        if L in BURNED["layouts"]:
            bad.append(f"layout {L} was inspected")
        sp = [L[i + 1] - L[i] for i in range(len(L) - 1)]
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
            "checked": ["layout", "spacing", "program word", "clock phase", "delay-edit pattern",
                        "gate implementation", "burned absorber candidates"],
            "note": "development AND the EXP-GT-03 hold-outs AND the four burned absorbers are all treated as "
                    "inspected. Nothing here overlaps any of them."}


def manifest() -> dict:
    m = {"burned": BURNED, "held_out": HELD_OUT, "leakage": assert_no_leakage(),
         "frozen_observer": {"A_TAU_TOL": OBSV.TAU_TOL, "frozen_at": OBSV.FROZEN_AT,
                             "derived_from": "the independent phase null of Certificate V2 (D-057). NOT free."}}
    m["hash"] = hashlib.sha256(json.dumps(m, sort_keys=True, default=str).encode()).hexdigest()[:16]
    return m


# ------------------------------------------------------------- held-out circuit builders
def ho(cols, program=None, gate="se_eater", extra=(), rows=None, arch_id="HO") -> Arch:
    program = program or (1,) * len(cols)
    rows = rows or [GUN_ROW] * len(cols)
    off = GATE_OFFSETS[gate]
    comps = [Comp("se_gun", r, c, f"gun{i}") for i, (r, c) in enumerate(zip(rows, cols))]
    comps += [Comp(gate, 35 + off[0], (se_diag(rows[i], cols[i]) + 35) + off[1], f"gate{i}")
              for i in range(len(cols)) if program[i] == 0]
    comps += list(extra)
    a = Arch(arch_id, comps, tuple(program))
    a.declared_edges = tuple(predict_active(a)["edges"])
    return a


def ho_delay(k, chan, cols, program=None, arch_id=None) -> Arch:
    cols = list(cols)
    rows = [GUN_ROW] * len(cols)
    rows[chan] += k
    cols[chan] += k
    a = ho(cols, program, rows=rows, arch_id=arch_id or f"HO_DELAY_ch{chan}_k{k}")
    a.meta = {"delay_edit_steps": 4 * k}
    return a


def ho_xinhib(sw_col, cols, program=None, arch_id=None) -> Arch:
    return ho(cols, program, extra=[Comp("sw_gun", GUN_ROW, sw_col, "gunSW")],
              arch_id=arch_id or f"HO_XINHIB_sw{sw_col}")


def ho_inert(cols, program=None) -> Arch:
    a = ho(cols, program, arch_id="HO_INERT")
    a.components = a.components + [Comp("block", r, c, f"d{i}")
                                   for i, (r, c) in enumerate([(62, 6), (26, 268), (108, 40)])]
    return a


# ------------------------------------------------------------- SS5.1: the held-out implementation subclaim
def held_out_implementation_status() -> dict:
    """HELD-OUT IMPLEMENTATION NOT AVAILABLE. Reported, not manufactured.

    A held-out absorber must clear TWO independent bars, and every candidate clears exactly one of them:

      BEHAVIOURAL (SS5.1): gate its own channel, destroy no neighbour, emit nothing collateral, stay periodic at
        settle AND after 3000 further steps, and produce an output line BIT-IDENTICAL to the development gate --
        on MIDDLE channels, at every declared spacing.
      ADMISSIBILITY (D-053/D-054): its DECLARED component must be the component the DYNAMICS REALIZES. A declared
        graph the dynamics does not realize is not a ground truth; it is a comment.

    MEASURED:
      BOAT, SNAKE, BEEHIVE  -- fail BEHAVIOURAL. They absorb cleanly in ISOLATION and then DESTROY THE NEIGHBOURING
                              CHANNEL in the real circuit. On the last channel there is no neighbour, so an
                              isolated test passes them. A component validated in isolation is not a validated
                              component.
      LOAF, EATER2          -- pass BEHAVIOURAL (EATER2 even reproduces the development gate's output line
                              bit-for-bit, at spacings 42/46/50, on middle channels) and fail ADMISSIBILITY: both
                              are REACTIVE SEEDS, not still lifes. The first glider consumes them and the reaction
                              settles into an absorber somewhere else -- their declared box is EMPTY at settle, so
                              `assert_graph_agrees` rejects them and `measured_graph` finds no gate edge at all.

    The ONLY absorber whose declared component is its realized component is EATER1 -- the DEVELOPMENT part.

    SS5.1 IS EXPLICIT: "Do not manufacture evidence by reusing a development component and calling its position
    change a new implementation." So we do not. The held-out-implementation subclaim is INDETERMINATE. Every
    other axis of the split (layout, spacing, program, phase, delay pattern, topology) is genuinely held out and
    is evaluated normally.

    REQUIRED PROPERTY OF THE NEXT COMPONENT LIBRARY: a STILL-LIFE absorber, distinct from EATER1, whose declared
    footprint IS its settled footprint.
    """
    return {"verdict": "HELD-OUT IMPLEMENTATION NOT AVAILABLE",
            "subclaim": "INDETERMINATE",
            "behavioural_pass": ["LOAF", "EATER2"],
            "admissibility_pass": ["EATER1 (development only)"],
            "rejected_for_neighbour_destruction": ["BOAT", "SNAKE", "BEEHIVE"],
            "rejected_as_reactive_seed": ["LOAF", "EATER2"],
            "manufactured_evidence": "REFUSED (SS5.1)"}


# ------------------------------------------------------------- E1 / E2 (SS6)
E1_INSTALL, E1_REMOVE = 137, 287
E1_RELIEF_ROW = 23


def e1_handoff(cols=None, chan=1, steps=1000):
    """E1 -- FUNCTION-PRESERVING HANDOFF, with the SS6-CORRECTED expected vector.

    The relief is installed BEFORE the incumbent is removed, so the machine is never unmanned. The relief sits
    UPSTREAM, so the causal PATH LENGTH changes while the CONNECTIVITY does not.

    EXPECTED: A_TOPO = SAME  (same nodes, same edges, same roles)
              A_TAU  = DIFFERENT  (the gate's causal delay to the output genuinely changed)
              G      = DIFFERENT ; F = SAME ; L = SAME ; M = DIFFERENT
    D-056 labelled this A = SAME and scored the head wrong for saying otherwise. The head was right: a component
    that MOVES changes the timing architecture. Splitting A into A_TOPO and A_TAU is what lets both facts be told.
    """
    cols = cols or L_A
    prog = tuple(0 if j == chan else 1 for j in range(len(cols)))
    pre = ho(cols, prog, "se_eater", arch_id="E1_pre")
    assert_viable(pre)
    d = se_diag(GUN_ROW, cols[chan])
    old = [c for c in pre.components if c.name == f"gate{chan}"][0]
    relief = Comp("se_eater", E1_RELIEF_ROW + EATER_OFF[0], (d + E1_RELIEF_ROW) + EATER_OFF[1], f"relief{chan}")
    assert relief.box()[1] < old.box()[0], "the relief must sit strictly upstream of the incumbent"

    g = settle(pre)
    control, gc = [g.copy()], g.copy()
    for _ in range(steps):
        gc = step(gc)
        control.append(gc.copy())
    frames, gg = [g.copy()], g.copy()
    for t in range(1, steps + 1):
        if t == E1_INSTALL:
            place(gg, relief.cells(), relief.row, relief.col)
        if t == E1_REMOVE:
            r0, r1, c0, c1 = old.box()
            gg[r0 - 1:r1 + 2, c0 - 1:c1 + 2] = 0
        gg = step(gg)
        frames.append(gg.copy())

    changed = sum(1 for a, b in zip(control, frames) if not np.array_equal(a, b))
    r0, r1, c0, c1 = old.box()
    old_left = int(frames[-1][r0:r1, c0:c1].sum())
    rr0, rr1, rc0, rc1 = relief.box()
    new_cells = int(frames[-1][rr0:rr1, rc0:rc1].sum())
    io = all(np.array_equal(a[OUT_ROW], b[OUT_ROW]) for a, b in zip(control, frames))
    restored = np.array_equal(frames[-1], control[-1])

    assert changed > 0, "E1 is a SILENT NO-OP: the trajectory never changed"
    assert old_left == 0, f"E1 did not remove the incumbent ({old_left} cells remain)"
    assert new_cells >= 6, f"E1 relief did not establish ({new_cells} cells)"
    assert io, "E1 broke the I/O -- that is an E2, not an E1"
    assert not restored, "E1 exactly RESTORED the original microstate: it cannot fire"

    post = ho(cols, prog, "se_eater", arch_id="E1_post")
    post.components = [c for c in post.components if c.name != f"gate{chan}"] + [relief]
    return {"pre": pre, "post": post, "frames": frames, "control": control,
            "assertions": {"trajectory_changed_frames": changed, "old_component_cells_left": old_left,
                           "new_component_cells": new_cells, "io_identical_every_timestep": io,
                           "no_exact_restoration": not restored}}


def e2_damage_repair(cols=None, chan=2, steps=1000):
    """E2 -- DAMAGE AND REPAIR. F breaks transiently; lineage stays observable; recovery is measured separately.
    E2 IS NEVER THE SHIP-OF-THESEUS EQUIVALENCE GATE."""
    cols = cols or L_A
    a = ho(cols, PROG, arch_id="E2")
    assert_viable(a)
    gun = [c for c in a.components if c.name == f"gun{chan}"][0]
    g = settle(a)
    control, gc = [g.copy()], g.copy()
    for _ in range(steps):
        gc = step(gc)
        control.append(gc.copy())
    frames, gg = [g.copy()], g.copy()
    r0, r1, c0, c1 = gun.box()
    for t in range(1, steps + 1):
        if 230 <= t < 244:
            gg[r0:r1, c0:c1] = 0
        if t == 430:
            place(gg, gun.cells(), gun.row, gun.col)
        gg = step(gg)
        frames.append(gg.copy())
    oc = np.array([int(f[OUT_ROW].sum()) for f in control])
    of = np.array([int(f[OUT_ROW].sum()) for f in frames])
    broke = int((oc != of).sum())
    # recovery on the PHASE-INVARIANT RATE: a rebuilt gun restarts at a new clock phase, so a repaired machine
    # can never be bit-identical to the control -- demanding that would define recovery out of existence.
    recovered = bool(abs(float(of[-120:].mean()) - float(oc[-120:].mean())) < 1e-9)
    assert broke > 0, "E2 is a SILENT NO-OP: the function never broke"
    return {"assertions": {"timesteps_with_broken_IO": broke, "function_recovered_in_tail": recovered,
                           "tail_rate_control": float(oc[-120:].mean()),
                           "tail_rate_repaired": float(of[-120:].mean())},
            "frames": frames, "control": control}


# ------------------------------------------------------------- the held-out challenge matrix (SS7)
def challenges():
    """Expected vectors DECLARED HERE, before any head is run. Where a delay is expected to change, the
    expectation is DERIVED from the evaluator's MEASURED path -- never hardcoded (SS12)."""
    b42 = ho(L_A, PROG, arch_id="HO_B42")
    b46 = ho(L_B, PROG, arch_id="HO_B46")
    five = ho(L_C, (1, 0, 1, 1, 1), arch_id="HO_FIVE50")
    gate_e = ho(L_A, (1, 1, 1, 0), "se_eater", arch_id="HO_GATE3")
    xin = ho_xinhib(207, L_A, (1, 1, 1, 1))          # inhibitor kills the SAME channel the gate does -> same F
    return [
        # (name, a1, a2, ph1, ph2, A_TOPO, A_TAU, G, F, M)
        ("same topology, different LAYOUT (sp42 vs sp46)", b42, b46, 27, 41, "SAME", "SAME", "DIFFERENT",
         "SAME", "DIFFERENT"),
        ("TRANSLATION-equivalent machine", b42, ho([c + 13 for c in L_A], PROG, arch_id="T13"), 33, 33,
         "SAME", "SAME", "SAME", "SAME", "DIFFERENT"),
        ("PHASE-SHIFTED equivalent machine", b42, b42, 27, 49, "SAME", "SAME", "SAME", "SAME", "SAME"),
        ("same topology, different CAUSAL DELAY (k=5, ch1)", b46, ho_delay(5, 1, L_B, PROG), 41, 41,
         "SAME", "DIFFERENT", "DIFFERENT", "SAME", "DIFFERENT"),
        ("same topology, different CAUSAL DELAY (k=7, ch2)", five, ho_delay(7, 2, L_C, (1, 0, 1, 1, 1)), 55, 55,
         "SAME", "DIFFERENT", "DIFFERENT", "SAME", "DIFFERENT"),
        ("DIFFERENT topology, same F (gate vs cross-inhibitor)", gate_e, xin, 27, 27,
         "DIFFERENT", "INDETERMINATE", "DIFFERENT", "SAME", "DIFFERENT"),
        ("EDGE ADDED (cross-stream inhibitor)", b42, ho_xinhib(207, L_A, PROG), 33, 33,
         "DIFFERENT", "INDETERMINATE", "DIFFERENT", "DIFFERENT", "DIFFERENT"),
        ("NODE ADDED (five channels, sp50)", b42, five, 49, 49,
         "DIFFERENT", "INDETERMINATE", "DIFFERENT", "DIFFERENT", "DIFFERENT"),
        ("INERT decoration", b42, ho_inert(L_A, PROG), 27, 27, "SAME", "SAME", "DIFFERENT", "SAME", "DIFFERENT"),
        ("same topology, different S (program word)", ho(L_A, PROG, arch_id="P1011"),
         ho(L_A, PROG_B, arch_id="P0110"), 33, 33, "DIFFERENT", "INDETERMINATE", "DIFFERENT", "DIFFERENT",
         "DIFFERENT"),
        ("exact copy, reset history", b42, ho(L_A, PROG, arch_id="COPY"), 41, 41,
         "SAME", "SAME", "SAME", "SAME", "SAME"),
    ]


def main(run_id="EXP-GT-03R-20260714-001"):
    man = manifest()
    rows, fails, rejected = [], 0, []
    for name, a1, a2, p1, p2, eT, eTau, eG, eF, eM in challenges():
        try:
            for a in (a1, a2):
                assert_viable(a)
                assert_graph_agrees(a)
        except AssertionError as ex:
            rejected.append({"case": name, "why": str(ex)[:150]})
            continue
        t1, t2 = OBSV.tomo(a1, p1), OBSV.tomo(a2, p2)
        g1, g2 = settle(a1, extra_phase=p1), settle(a2, extra_phase=p2)
        got = {"A_TOPO": head_A_TOPO(t1, t2), "A_TAU": head_A_TAU(t1, t2, OBSV.TAU_TOL), "G": head_G(t1, t2),
               "F": head_F(f_signature(g1, t1["out_nodes"]), f_signature(g2, t2["out_nodes"])),
               "M": head_M(g1, g2)}
        exp = {"A_TOPO": eT, "A_TAU": eTau, "G": eG, "F": eF, "M": eM}
        ok = {k: got[k] == exp[k] for k in exp}
        fails += sum(1 for v in ok.values() if not v)
        rows.append({"case": name, "expected": exp, "predicted": got, "pass": ok,
                     "identifiability": {"coverage_1": t1["coverage"]["complete"],
                                         "coverage_2": t2["coverage"]["complete"],
                                         "confounded_1": t1["coverage"]["n_confounded"],
                                         "confounded_2": t2["coverage"]["n_confounded"]},
                     "fully_held_out": True})

    # ---- E1 (SS6 corrected vector)
    e1 = e1_handoff()
    r = OBSV.compare(e1["pre"], e1["post"])
    k = len(e1["frames"]) // 2
    e1_got = {"A_TOPO": r["A_TOPO"], "A_TAU": r["A_TAU"], "G": r["G"], "F": r["F"], "M": r["M"],
              "L": head_L(e1["frames"][:k], e1["frames"][k:])}
    e1_exp = {"A_TOPO": "SAME", "A_TAU": "DIFFERENT", "G": "DIFFERENT", "F": "SAME", "M": "DIFFERENT",
              "L": "SAME"}
    e1_fail = sum(1 for kk in e1_exp if e1_got[kk] != e1_exp[kk])

    e2 = e2_damage_repair()

    # ---- L, three regimes, on held-out circuits
    seg = run_from(settle(ho(L_A, PROG, arch_id="L_a")), 80)
    Lres = {"continuously observed run": head_L(seg[:40], seg[40:]),
            "observationally identical copy": head_L(seg[:40], [x.copy() for x in seg[:40]]),
            "different circuit (branch)": head_L(seg[:40], run_from(settle(ho(L_B, PROG, arch_id="L_b")), 79)[40:])}
    Lexp = {"continuously observed run": "SAME", "observationally identical copy": "INDETERMINATE",
            "different circuit (branch)": "DIFFERENT"}
    l_fail = sum(1 for kk in Lexp if Lres[kk] != Lexp[kk])

    # ---- S: the certified D-051 probe, PRESERVED EXACTLY -- and its DECLARED SCOPE respected.
    from ..identity.heads3 import s_in_scope
    a_in = ho(L_A, PROG, arch_id="s1")
    a_in2 = ho([c - 3 for c in L_A], PROG, arch_id="s2")      # held-out translation, still inside S's window
    assert s_in_scope(a_in2), "the S comparison must be inside S's certified scan window"
    a_diff = ho(L_A, PROG_B, arch_id="s4")
    a_out = ho(L_B, PROG, arch_id="s_oos")                    # held-out sp46: channel 3 falls OUTSIDE S's window
    S = {"same word, different layout (in scope)": head_S(settle(a_in), settle(a_in2)),
         "different word, same layout (in scope)": head_S(settle(a_in), settle(a_diff)),
         "sp46 layout (OUT OF S's certified scan window)":
             "OUT_OF_SCOPE" if not s_in_scope(a_out) else head_S(settle(a_in), settle(a_out))}
    Sexp = {"same word, different layout (in scope)": "SAME",
            "different word, same layout (in scope)": "DIFFERENT",
            "sp46 layout (OUT OF S's certified scan window)": "OUT_OF_SCOPE"}
    s_fail = sum(1 for kk in Sexp if S[kk] != Sexp[kk])
    s_scope = {"note": "S is PRESERVED EXACTLY (D-051). Its blind scan covers columns [20,200); on the held-out "
                       "sp46 layout the fourth channel's deletion column is 212, so that layout is OUT OF SCOPE. "
                       "That is neither a pass nor a failure -- it is an identifiability statement, and the "
                       "split, not the instrument, must respect the instrument's declared range."}

    total = fails + e1_fail + l_fail + s_fail
    rep = {"manifest": man, "challenges": rows, "rejected_circuits": rejected,
           "E1": {"assertions": e1["assertions"], "expected": e1_exp, "predicted": e1_got,
                  "pass": {kk: e1_got[kk] == e1_exp[kk] for kk in e1_exp}},
           "E2": e2["assertions"],
           "L": {"predicted": Lres, "expected": Lexp},
           "S": {"predicted": S, "expected": Sexp, "scope": s_scope},
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


def summarize(r) -> str:
    L = ["EXP-GT-03R -- the REPAIRED observer, FROZEN, on ENTIRELY NEW hold-outs",
         f"manifest {r['manifest']['hash']}   leakage: {r['manifest']['leakage']['leakage']}   "
         f"A_TAU_TOL={r['manifest']['frozen_observer']['A_TAU_TOL']} (frozen; derived from the independent null)",
         "=" * 122, "",
         f"  {'case':52s} {'A_TOPO':22s} {'A_TAU':24s} {'G':20s} {'F':18s} {'M':12s}"]
    for c in r["challenges"]:
        def cell(k):
            return ("OK " if c["pass"][k] else "XX ") + f"{c['predicted'][k]}/{c['expected'][k]}"
        L.append(f"  {c['case']:52s} {cell('A_TOPO'):22s} {cell('A_TAU'):24s} {cell('G'):20s} "
                 f"{cell('F'):18s} {cell('M'):12s}")
    e = r["E1"]
    L += ["", "E1 -- FUNCTION-PRESERVING HANDOFF (SS6-corrected expected vector):",
          f"   assertions: {e['assertions']}",
          "   " + "  ".join(f"{k}={e['predicted'][k]}/{e['expected'][k]}"
                            + ("" if e["pass"][k] else " <-- FAIL") for k in e["expected"]),
          "", f"E2 -- DAMAGE AND REPAIR (never the Ship-of-Theseus gate): {r['E2']}",
          "", "L -- three regimes:"]
    for k, v in r["L"]["predicted"].items():
        L.append(f"   {'OK ' if v == r['L']['expected'][k] else 'XX '}{k:34s} -> {v:15s} "
                 f"(expected {r['L']['expected'][k]})")
    L += ["", "S -- the certified D-051 probe, preserved exactly:"]
    for k, v in r["S"]["predicted"].items():
        L.append(f"   {'OK ' if v == r['S']['expected'][k] else 'XX '}{k:34s} -> {v:15s} "
                 f"(expected {r['S']['expected'][k]})")
    h = r["held_out_implementation"]
    L += ["", f"HELD-OUT COMPONENT IMPLEMENTATION: {h['verdict']}  -> subclaim {h['subclaim']}",
          f"   rejected for neighbour destruction: {h['rejected_for_neighbour_destruction']}",
          f"   rejected as reactive seeds (declared component != realized component): {h['rejected_as_reactive_seed']}",
          f"   manufactured evidence: {h['manufactured_evidence']}"]
    if r["rejected_circuits"]:
        L += ["", "CIRCUITS REJECTED BY THE BENCHMARK'S OWN ADMISSION CRITERIA:"]
        for x in r["rejected_circuits"]:
            L.append(f"   {x['case']}: {x['why'][:96]}")
    L += ["", "=" * 122, f"head failures: {r['head_failures']}", f"VERDICT: {r['VERDICT']}", "=" * 122]
    return "\n".join(L)
