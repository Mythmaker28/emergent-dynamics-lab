"""EXP-GT-FINGERPRINT-00 -- DEVELOPMENT CERTIFICATE.

THE CLAIM UNDER TEST, and nothing wider:

    A frozen, standardized causal-response fingerprint can remain stable under microscopically different but
    behaviourally equivalent implementations, while distinguishing systems that differ in reachable function or in
    genuine hidden state.

Model minimality, architecture discovery and lineage identity are OUTSIDE this claim. The fingerprint never says
SAME: its verdicts are INDISTINGUISHABLE_UNDER_REPERTOIRE / DIFFERENT / INDETERMINATE.

TWO ARMS, and the limited one must qualify on its own. A rich-access pass cannot authorize transfer after a
limited-access failure -- that inference is the exact category of error that retired three observers.
"""

from __future__ import annotations

import json
import os
import pickle

import numpy as np

from ..substrates.boolnet.circuits import build
from ..substrates.boolnet.evaluator import assert_qualified
from ..substrates.boolnet.fpworld import FPWorld, probe_cells, swapped_trajectory
from ..identity.fingerprint import acquire, canonical, distance, compare, COVERAGE_FLOOR

_DISK = ".cache_fp"

# ---------------------------------------------------------------- development systems (id -> build args)
DEV = {
    "AND_direct":    dict(impl="direct", program=(1, 1, 1)),
    "AND_demorgan":  dict(impl="demorgan", program=(1, 1, 1)),
    "AND_nand2":     dict(impl="nand2", program=(1, 1, 1)),
    "AND_xor_or":    dict(impl="xor_or", program=(1, 1, 1)),
    "AND_dup_same":  dict(impl="dup_same", program=(1, 1, 1)),      # 3 taps, 2 causes
    "AND_reg_delay": dict(impl="reg_delay", program=(1, 1, 1)),     # a LATCH in the delay path
    "AND_retimed":   dict(impl="direct", program=(1, 1, 1), extra_delay=3),
    "AND_layout":    dict(impl="direct", program=(1, 1, 1), chan_cols=(8, 23, 36), clk_phase=5),
    "XOR_gate":      dict(impl="xor_gate", program=(1, 1, 1)),
    "XOR_3cell":     dict(impl="xor3", program=(1, 1, 1)),          # the REDUNDANT-LAG system (the D-069 case)
    "OR_bit0":       dict(impl="or_gate", program=(0, 0, 0)),       # OR(clk,0) = clk  -- collides with AND under
    "OR_bit1":       dict(impl="or_gate", program=(1, 1, 1)),       #   the droplet arm; SATURATED (silent) at bit 1
    "AND3":          dict(impl="and3", program=(1, 1, 1)),          # a third cause, unreachable without a clamp
    "STATE_toggle":  dict(impl="toggle", program=(1, 1, 1)),
    "STATE_fsm":     dict(impl="fsm_gate", program=(1, 1, 1)),
    "LAG15_or":      dict(impl="lag15_or", program=(1, 1, 1)),      # byte-identical PASSIVE output to LAG15_xor
    "LAG15_xor":     dict(impl="lag15_xor", program=(1, 1, 1)),
    "LAG8_and":      dict(impl="lag8_and", program=(1, 1, 1)),
    "LAG8_or":       dict(impl="lag8_or", program=(1, 1, 1)),
}


def machine(sid):
    kw = dict(DEV[sid])
    kw.setdefault("chan_cols", (6, 20, 34))
    m = build(**{k: (list(v) if k == "chan_cols" else v) for k, v in kw.items()})
    assert_qualified(m)
    return m


def fp(sid, arm, chan=0):
    os.makedirs(_DISK, exist_ok=True)
    f = os.path.join(_DISK, f"{sid}_{arm}_{chan}.pkl")
    if os.path.exists(f):
        return pickle.load(open(f, "rb"))
    m = machine(sid)
    w = FPWorld(m.net, m.out_cells)
    acq = acquire(w, sid, probe_cells(m, chan, arm), m.out_cells[chan], arm)
    pickle.dump(acq, open(f, "wb"))
    return acq


# ---------------------------------------------------------------- the frozen challenge matrix
#
# A BENCHMARK-LABEL CORRECTION, MADE ON DEVELOPMENT, BEFORE THE FREEZE, WITH A STATED PRINCIPLE.
#
# I first declared (XOR_gate, XOR_3cell) and (STATE_toggle, STATE_fsm) to be CONTINUITY pairs in BOTH arms. Under
# the rich arm the fingerprint separated them, and it was RIGHT to:
#   * toggle IGNORES its register; fsm_gate's write-enable is GATED by it. Step the register and one freezes and
#     the other does not. That is a real cause that one system has and the other lacks.
#   * xor3's reconvergent paths reach its output gate ONE STEP APART, so stepping the register produces a GLITCH
#     that a single-cell XOR cannot produce. The redundant lag is not behaviourally silent -- it is silent only to
#     probes that cannot step the register.
# Neither difference comes from a label. Both are MEASURED RESPONSES. The benchmark was wrong, not the measurement.
#
# THE PRINCIPLE: a pair is a CONTINUITY pair FOR AN ARM iff every probe IN THAT ARM'S BATTERY elicits an identical
# response. Where an arm's probes reach a cause one system has and the other lacks, the pair belongs in that arm's
# DIFFERENCE set. Equivalence is relative to a repertoire, and always was.
CONTINUITY = [                       # INDISTINGUISHABLE in BOTH arms: same reachable behaviour, different insides
    ("AND_direct", "AND_demorgan", "different microscopic implementation"),
    ("AND_direct", "AND_nand2", "different microscopic implementation"),
    ("AND_direct", "AND_xor_or", "reconvergent implementation"),
    ("AND_direct", "AND_dup_same", "REDUNDANT DUPLICATED TAP: three boundary taps, two causes"),
    ("AND_direct", "AND_reg_delay", "compensated internal retiming: a LATCH in the delay path"),
    ("AND_direct", "AND_retimed", "retimed channel (detour)"),
    ("AND_direct", "AND_layout", "different layout AND different clock phase"),
]
DIFFERENCE = [                       # DIFFERENT in BOTH arms
    ("AND_direct", "XOR_gate", "different reachable truth table"),
    ("AND_direct", "STATE_toggle", "combinational vs true hidden state"),
    ("AND_reg_delay", "STATE_toggle", "a LATCH is not a state machine: same parts, different behaviour"),
    ("AND_reg_delay", "STATE_fsm", "different recovery dynamics"),
    ("LAG15_or", "LAG15_xor", "BYTE-IDENTICAL passive output; separated only by a probe"),
]
COLLIDE = [                          # DIFFERENT under RICH access, INDISTINGUISHABLE under the DROPLET repertoire
    ("AND_direct", "OR_bit0", "OR(clk,0) = AND(clk,1) = clk. The register cannot be clamped in a droplet."),
    ("AND_direct", "AND3", "a third cause exists and no admissible droplet probe can reach it."),
    ("XOR_gate", "XOR_3cell", "the D-069 REDUNDANT LAG: it glitches on a register step, and a droplet has no "
                              "register step. Indistinguishable under the droplet repertoire."),
    ("STATE_toggle", "STATE_fsm", "one state machine is gated by its register and the other is not; only a "
                                  "register step reveals it."),
]
SILENT = [("OR_bit1", "AND_direct", "a SATURATED gate answers nothing. Silence is not a fingerprint.")]


def radii(dev_d):
    """Thresholds are DERIVED FROM DEVELOPMENT and then frozen. They are never moved afterwards."""
    max_c = max(d for _, _, d in dev_d["continuity"])
    min_d = min(d for _, _, d in dev_d["difference"])
    gap = min_d - max_c
    return {"r_continuity": round(max_c + 0.25 * gap, 4), "r_separation": round(max_c + 0.75 * gap, 4),
            "max_continuity_distance": max_c, "min_difference_distance": min_d, "gap": gap}


def certificate() -> dict:
    cases, out = [], {}

    def case(name, ok, detail=""):
        cases.append({"case": name, "PASS": bool(ok), "detail": detail})

    for arm in ("rich", "droplet"):
        F = {sid: canonical(fp(sid, arm)) for sid in DEV}
        cont = [(a, b, distance(F[a], F[b])) for a, b, _ in CONTINUITY]
        diff = [(a, b, distance(F[a], F[b])) for a, b, _ in DIFFERENCE]
        coll = [(a, b, distance(F[a], F[b])) for a, b, _ in COLLIDE]
        R = radii({"continuity": cont, "difference": diff})
        out[arm] = {"F": F, "cont": cont, "diff": diff, "coll": coll, "radii": R}

        cw = [compare(F[a], F[b], R["r_continuity"], R["r_separation"]) for a, b, _ in CONTINUITY]
        dw = [compare(F[a], F[b], R["r_continuity"], R["r_separation"]) for a, b, _ in DIFFERENCE]
        clw = [compare(F[a], F[b], R["r_continuity"], R["r_separation"]) for a, b, _ in COLLIDE]

        case(f"[{arm}] CONTINUITY: behaviourally equivalent systems are never called DIFFERENT",
             all(v["verdict"] == "INDISTINGUISHABLE_UNDER_REPERTOIRE" for v in cw),
             f"{len(cw)} pairs, max distance {max(d for *_ , d in cont):.4f}; "
             f"verdicts {sorted({v['verdict'] for v in cw})}")
        case(f"[{arm}] DIFFERENCE: systems with different function or hidden state SEPARATE",
             all(v["verdict"] == "DIFFERENT" for v in dw),
             f"{len(dw)} pairs, min distance {min(d for *_ , d in diff):.4f}; "
             f"verdicts {sorted({v['verdict'] for v in dw})}")
        case(f"[{arm}] the continuity and difference regions do not overlap (a real gap)",
             R["gap"] > 0,
             f"max continuity {R['max_continuity_distance']:.4f} < min difference "
             f"{R['min_difference_distance']:.4f}; radii r_c={R['r_continuity']}, r_s={R['r_separation']}")
        case(f"[{arm}] a REDUNDANT TAP creates no fingerprint difference (three taps, two causes)",
             distance(F["AND_direct"], F["AND_dup_same"]) <= R["r_continuity"],
             f"AND_direct vs AND_dup_same: d={distance(F['AND_direct'], F['AND_dup_same']):.4f}")
        case(f"[{arm}] hidden state is separated from a LATCH (same parts, different behaviour)",
             compare(F["AND_reg_delay"], F["STATE_toggle"], R["r_continuity"],
                     R["r_separation"])["verdict"] == "DIFFERENT",
             f"reg_delay CONTAINS a register and is not a state machine; toggle is. "
             f"d={distance(F['AND_reg_delay'], F['STATE_toggle']):.4f}")
        if arm == "droplet":
            case("[droplet] a SILENT system is INDETERMINATE, never matched",
                 compare(F["OR_bit1"], F["AND_direct"], R["r_continuity"],
                         R["r_separation"])["verdict"] == "INDETERMINATE",
                 f"OR_bit1 responsiveness = {F['OR_bit1']['responsive']:.2f}: a saturated gate answers nothing "
                 f"to any admissible droplet probe")
        else:
            case("[rich] RICH access RESCUES a system the droplet repertoire cannot interrogate at all",
                 F["OR_bit1"]["responsive"] > 0.0
                 and compare(F["OR_bit1"], F["AND_direct"], R["r_continuity"],
                             R["r_separation"])["verdict"] == "DIFFERENT",
                 f"OR_bit1 responsiveness = {F['OR_bit1']['responsive']:.2f} under rich access "
                 f"(0.00 under the droplet repertoire): unclamping its register makes it speak")

    # ---------------------------------------------------------------- rich vs limited: the collisions
    Rr, Rd = out["rich"]["radii"], out["droplet"]["radii"]
    rich_sep = [compare(out["rich"]["F"][a], out["rich"]["F"][b], Rr["r_continuity"], Rr["r_separation"])["verdict"]
                for a, b, _ in COLLIDE]
    drop_sep = [compare(out["droplet"]["F"][a], out["droplet"]["F"][b], Rd["r_continuity"],
                        Rd["r_separation"])["verdict"] for a, b, _ in COLLIDE]
    case("C1 systems distinguishable under RICH access are INDISTINGUISHABLE under the droplet repertoire",
         all(v == "DIFFERENT" for v in rich_sep)
         and all(v == "INDISTINGUISHABLE_UNDER_REPERTOIRE" for v in drop_sep),
         f"rich={rich_sep}  droplet={drop_sep}  -- and the droplet arm reports them as an EQUIVALENCE CLASS, "
         f"not as the same system")
    case("C2 FALSE SAMENESS INCREASES as experimental access gets poorer (measured, not assumed)",
         sum(v == "INDISTINGUISHABLE_UNDER_REPERTOIRE" for v in drop_sep) >
         sum(v == "INDISTINGUISHABLE_UNDER_REPERTOIRE" for v in rich_sep),
         f"collisions: rich {sum(v == 'INDISTINGUISHABLE_UNDER_REPERTOIRE' for v in rich_sep)}/{len(COLLIDE)}, "
         f"droplet {sum(v == 'INDISTINGUISHABLE_UNDER_REPERTOIRE' for v in drop_sep)}/{len(COLLIDE)}")

    # ---------------------------------------------------------------- E1: replacement during one trajectory
    ma, mb = machine("AND_demorgan"), machine("AND_nand2")
    sw = swapped_trajectory(ma, mb, t_swap=40, steps=140)
    e1d = distance(out["droplet"]["F"]["AND_demorgan"], out["droplet"]["F"]["AND_nand2"])
    case("E1 function-preserving REPLACEMENT during one continuous trajectory: behaviour uninterrupted",
         sw["identical_before_swap"] and sw["transient_steps"] <= 20,
         f"identical before the swap; a bounded transient of {sw['transient_steps']} steps; "
         f"uninterrupted from t={sw['uninterrupted_after']}")
    case("E1 the fingerprint SURVIVES the replacement (pre/post distance inside the continuity radius)",
         e1d <= Rd["r_continuity"],
         f"pre-replacement vs post-replacement fingerprint distance = {e1d:.4f} "
         f"(continuity radius {Rd['r_continuity']})")

    # ---------------------------------------------------------------- LOAD-BEARING CONTROL 1 (must-fail)
    a_c = canonical(fp("XOR_gate", "droplet"), contaminant={"class": "DELAYED_STATIC", "lags": [12]})
    b_c = canonical(fp("XOR_3cell", "droplet"), contaminant={"class": "FINITE_HISTORY", "lags": [14, 16]})
    d_clean = distance(out["droplet"]["F"]["XOR_gate"], out["droplet"]["F"]["XOR_3cell"])
    d_cont = distance(a_c, b_c)
    case("L1 MUST-FAIL: re-adding the class label and lag set RECREATES the false difference (D-069)",
         d_clean <= Rd["r_continuity"] and d_cont >= Rd["r_separation"],
         f"clean d={d_clean:.4f} (INDISTINGUISHABLE) -> contaminated d={d_cont:.4f} (DIFFERENT). "
         f"The exclusion of description-level quantities is LOAD-BEARING, not decoration.")

    # ---------------------------------------------------------------- LOAD-BEARING CONTROL 2 (probe adequacy)
    # REMOVE THE DISCRIMINATING PROBE AND WATCH TWO GENUINELY DIFFERENT SYSTEMS COLLAPSE INTO ONE FINGERPRINT.
    # The rich battery separates XOR_gate from XOR_3cell -- the D-069 redundant-lag system -- because stepping the
    # register makes the reconvergent implementation GLITCH. Delete exactly that probe and the two become one.
    # (My first version deleted only the drive CLAMPS and the drive PULSES still separated the pair: d fell to
    #  0.0401, an INDETERMINATE, not a collapse. A control that half-fires proves half of nothing.)
    def without(sid, drop):
        acq = dict(fp(sid, "rich"))
        acq["probes"] = [p for p in acq["probes"] if p not in drop]
        return canonical(acq)
    drop = tuple(n for n in fp("XOR_gate", "rich")["probes"] if n.startswith("internal"))
    d_full = distance(out["rich"]["F"]["XOR_gate"], out["rich"]["F"]["XOR_3cell"])
    d_poor = distance(without("XOR_gate", drop), without("XOR_3cell", drop))
    case("L2 MUST-FAIL: removing the discriminating probe COLLAPSES two different systems into one fingerprint",
         d_full >= Rr["r_separation"] and d_poor <= Rd["r_continuity"],
         f"with the register step d={d_full:.4f} (DIFFERENT under rich) -> without it d={d_poor:.4f} "
         f"(INDISTINGUISHABLE). PROBE-REPERTOIRE ADEQUACY IS LOAD-BEARING: the difference was real and the "
         f"poorer repertoire cannot see it.")

    n = sum(c["PASS"] for c in cases)
    return {"cases": cases, "n_pass": n, "n": len(cases), "QUALIFIED": n == len(cases),
            "radii": {"rich": Rr, "droplet": Rd},
            "distances": {arm: {"continuity": [(a, b, round(d, 4)) for a, b, d in out[arm]["cont"]],
                                "difference": [(a, b, round(d, 4)) for a, b, d in out[arm]["diff"]],
                                "collision": [(a, b, round(d, 4)) for a, b, d in out[arm]["coll"]]}
                          for arm in ("rich", "droplet")},
            "e1": {k: (int(v) if isinstance(v, (bool, np.integer)) else v)
                   for k, v in sw.items() if k not in ("out_reference", "out_swapped")},
            "e1_fingerprint_distance": round(e1d, 4)}


def main():
    c = certificate()
    print("EXP-GT-FINGERPRINT-00 -- DEVELOPMENT CERTIFICATE")
    print("=" * 110)
    for x in c["cases"]:
        print(f"  [{'PASS' if x['PASS'] else 'FAIL'}] {x['case']}")
        print(f"         {x['detail']}")
    print("=" * 110)
    print(f"  {c['n_pass']}/{c['n']}   QUALIFIED = {c['QUALIFIED']}")
    print(f"  FROZEN RADII: rich {c['radii']['rich']}   droplet {c['radii']['droplet']}")
    json.dump(c, open("docs/FINGERPRINT_DEV_RAW.json", "w"), indent=1, default=str)
    return c


if __name__ == "__main__":
    main()
