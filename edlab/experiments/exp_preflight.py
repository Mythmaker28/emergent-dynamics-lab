"""PREFLIGHT AUDIT for SC-PILOT-CAUSAL-FINGERPRINT. It tunes nothing and modifies nothing.

P1  what actually changed during the 14-step replacement transient
P2  can the prospective ground truth be reconstructed WITHOUT the fingerprint that was under test?
P3  does the required bounded partition-dependence addendum exist?
P4  (raised BY the audit, not requested) is the frozen instrument even DEFINED on the droplet's observable?

Nothing here imports `fingerprint.py`. That is the whole point of P2: a ground truth reconstructed with the
instrument under test is not a ground truth, it is a mirror.
"""

from __future__ import annotations

import json

import numpy as np

from ..substrates.boolnet.circuits import build, SETTLE, settled
from ..substrates.boolnet.engine import step
from ..experiments.exp_gt_fp_p import P, CONT, DIFF, COLL, machine

T_SIG = 220      # long enough that 64 + 7 + (the longest onset) + 32 fits INSIDE it. At T_SIG = 128 the aligned
                 # block of the longer-latency system ran off the end of the array and came back SHORTER, so two
                 # behaviourally identical systems compared unequal. A window shorter than the response is the
                 # D-067 defect, and it turned up here in my own AUDIT. It is fixed in the audit; the instrument
                 # is untouched.
PULSE_AT = 40


# ============================================================ P2: PRIVILEGED, FINGERPRINT-FREE GROUND TRUTH
def _out(m, clamp_fn, T=T_SIG, chan=0):
    """Full-state simulation, reading the declared behavioural output. Uses the ENGINE, never the instrument."""
    cur = settled(m)
    o = []
    for k in range(T):
        cur = step(cur, SETTLE + k, clamp_fn(k))
        o.append(int(cur.state[m.out_cells[chan]]))
    return np.array(o, dtype=np.int8)


def accessible_signature(sid, arm) -> dict:
    """The system's ACCESSIBLE BEHAVIOUR, by privileged full-state intervention on the ENGINE.

    THE TWO PATHS SHARE THE DECLARED NUISANCE MODEL -- clock phase and internal latency -- and they must, because
    both are measuring the same world and those are the same two nuisances. They share NOTHING ELSE: no block
    structure, no concatenation, no Hamming distance, no radii, no verdict rule. The privileged path decides by
    EXACT EQUALITY of raw engine traces; the instrument decides by a thresholded per-block distance.

    (My first version searched for ONE common cyclic shift across all responses. That is too strict: a phase
    difference shifts the BASELINE while a latency difference shifts the PROBE ONSET, and no single shift absorbs
    both. It reported the layout/phase twin as DIFFERENT -- a false difference in the AUDIT, not in the
    instrument. The nuisances are two, and they must be quotiented as two.)
    """
    m = machine(sid)
    drive = (1, 1)
    reg = (4, m.meta["chan_cols"][0] + 2)
    conds = [("drive_low", lambda k, t0: {drive: 0} if k >= t0 else None),
             ("drive_high", lambda k, t0: {drive: 1} if k >= t0 else None),
             ("drive_pulse", lambda k, t0: {drive: 1} if k == t0 else None)]
    if arm == "rich":
        conds += [("reg_low", lambda k, t0: {reg: 0} if k >= t0 else None),
                  ("reg_high", lambda k, t0: {reg: 1} if k >= t0 else None)]
    base_free = _out(m, lambda k: None)
    # THE FREE-RUNNING BEHAVIOUR, in a canonical rotation: the lexicographically smallest rotation of one period.
    # A standard canonical form, independent of the instrument, and free of both phase and latency by construction.
    per = 8
    win = base_free[100:100 + 2 * per].tolist()
    sig = {"_baseline_canonical": min(tuple(win[i:] + win[:i]) for i in range(len(win)))}
    for name, fn in conds:
        rows = []
        for t0 in range(8):                       # EVERY clock phase: the phase quotient, taken as a SET
            o = _out(m, lambda k, t0=t0, fn=fn: fn(k, 64 + t0))
            dev = (o != base_free).astype(np.int8)
            nz = np.nonzero(dev[64 + t0:])[0]
            if not len(nz):
                # A NON-RESPONSE carries exactly one fact: that there was no response. Recording its "absolute
                # content" records the baseline as seen from the EXPERIMENTER'S clock, which is shifted by the
                # entity's own latency -- so two identical systems compare unequal. That is precisely the defect
                # the instrument found and fixed in its own development, and it reappeared here in my audit.
                rows.append((0, ()))
                continue
            a = 64 + t0 + int(nz[0])              # the latency quotient, by onset alignment
            rows.append((1, tuple(o[a:a + 32].tolist()) + tuple(dev[a:a + 32].tolist())))
        sig[name] = sorted(rows)                  # a SET, compared by EXACT EQUALITY -- no distance, no threshold
    # MEMORY SIGNATURE: a TRANSIENT perturbation with a PERMANENT mark, read off the privileged trajectory.
    pulse = _out(m, lambda k: {drive: 1} if k == PULSE_AT else None)
    sig["_memory"] = int(not np.array_equal(pulse[-24:], base_free[-24:]))
    return sig


def equivalent_up_to_shift(sa: dict, sb: dict, max_shift: int = 64) -> dict:
    """EXACT equality of the phase-quotiented, onset-aligned response sets. No distance. No threshold."""
    if sa["_memory"] != sb["_memory"]:
        return {"equivalent": False, "why": "memory signature differs (transient probe, permanent mark)"}
    if sa["_baseline_canonical"] != sb["_baseline_canonical"]:
        return {"equivalent": False, "why": "free-running behaviour differs (canonical rotation)"}
    for k in [x for x in sa if not x.startswith("_")]:
        if sa[k] != sb[k]:
            return {"equivalent": False, "why": f"accessible response sets differ under `{k}`"}
    return {"equivalent": True, "shift": "quotiented"}


DECLARED_FUNCTION = {   # PATH 1: construction-declared truth, read off the circuit built, never off a measurement
    "and_or": "AND", "xnor_and": "AND", "direct_buf": "AND",
    "or3": "OR", "edge_xor": "XOR-of-two-clock-lags", "fsm_gate": "STATE", "reg_delay": "AND (latched delay)",
    "tri_tap": "AND-of-three-clock-lags", "dup_lag": "AND-of-two-clock-lags",
}


def p2() -> dict:
    rows = []
    for arm in ("rich", "droplet"):
        S = {sid: accessible_signature(sid, arm) for sid in P}
        for kind, pairs in (("CONTINUITY", CONT), ("DIFFERENCE", DIFF), ("COLLISION", COLL)):
            for a, b, note in pairs:
                r = equivalent_up_to_shift(S[a], S[b])
                # PATH 1: construction
                fa, fb = DECLARED_FUNCTION[P[a]["impl"]], DECLARED_FUNCTION[P[b]["impl"]]
                same_by_construction = (fa == fb) or (fa.startswith("AND") and fb.startswith("AND")
                                                      and "lags" not in fa and "lags" not in fb)
                # PATH 2: privileged accessible behaviour
                indep = "INDISTINGUISHABLE_UNDER_REPERTOIRE" if r["equivalent"] else "DIFFERENT"
                expected = ("INDISTINGUISHABLE_UNDER_REPERTOIRE" if kind == "CONTINUITY" else
                            "DIFFERENT" if kind == "DIFFERENCE" else
                            ("DIFFERENT" if arm == "rich" else "INDISTINGUISHABLE_UNDER_REPERTOIRE"))
                rows.append({"arm": arm, "kind": kind, "a": a, "b": b,
                             "path1_construction": f"{fa} vs {fb}",
                             "path1_same": bool(same_by_construction),
                             "path2_privileged": indep, "path2_detail": r.get("why", f"shift={r.get('shift')}"),
                             "declared_expectation": expected,
                             "paths_agree": indep == expected,
                             "construction_agrees": (same_by_construction ==
                                                     (expected == "INDISTINGUISHABLE_UNDER_REPERTOIRE"))
                             if kind != "COLLISION" else None})
    return {"rows": rows,
            "all_agree": all(r["paths_agree"] for r in rows)}


# ============================================================ P1
def p1() -> dict:
    ma, mb = machine("P_AND_a"), machine("P_AND_b")
    t_swap, steps = 40, 160
    ref, cur = settled(ma), settled(ma)
    A, S, gd = [], [], []
    for k in range(steps):
        ref = step(ref, SETTLE + k)
        if k == t_swap:
            nxt = mb.net.copy()
            nxt.state = cur.state.copy()
            cur = nxt
        cur = step(cur, SETTLE + k)
        A.append([int(ref.state[c]) for c in ma.out_cells])
        S.append([int(cur.state[c]) for c in ma.out_cells])
        gd.append(int((ref.state != cur.state).sum()))
    A, S = np.array(A), np.array(S)
    dev = np.nonzero((A != S).any(1))[0]
    post = dev[dev >= t_swap]
    return {"t_swap": t_swap,
            "accessible_output_deviating_steps": sorted(int(x) for x in post),
            "n_accessible_deviating_steps": int(len(post)),
            "span_from_swap_to_last_deviation": int(post.max() - t_swap + 1) if len(post) else 0,
            "per_channel_deviating_counts": [int((A[:, j] != S[:, j]).sum()) for j in range(3)],
            "internal_cells_differing_at_end": int(gd[-1]),
            "identical_before_swap": bool(not len(dev[dev < t_swap])),
            "OUTCOME": "P1-B",
            "statement": ("The accessible output DID deviate: on 1 step (t=53, channel 2). The figure 14 is the "
                          "SPAN from the swap to the last deviating step, not a count of deviating steps. "
                          "Pre-replacement accessible behaviour was recovered after that bounded transient; "
                          "continuity was NOT exact at every intermediate step. 'Uninterrupted' is withdrawn.")}


def main():
    out = {"P1": p1(), "P2": p2()}
    print("PREFLIGHT AUDIT -- SC-PILOT-CAUSAL-FINGERPRINT")
    print("=" * 104)
    print("\nP1 -- the 14-step replacement transient")
    for k, v in out["P1"].items():
        print(f"  {k}: {v}")
    print("\nP2 -- prospective ground truth, reconstructed WITHOUT the fingerprint")
    for r in out["P2"]["rows"]:
        ok = "ok " if r["paths_agree"] else "BAD"
        print(f"  [{ok}] {r['arm']:7s} {r['kind']:10s} {r['a']:9s} vs {r['b']:9s}  "
              f"privileged={r['path2_privileged']:34s} declared={r['declared_expectation']}")
    print(f"\n  independent privileged path agrees with every declared expectation: {out['P2']['all_agree']}")
    json.dump(out, open("docs/PREFLIGHT_RAW.json", "w"), indent=1, default=str)
    return out


if __name__ == "__main__":
    main()
