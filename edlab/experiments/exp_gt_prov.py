"""EXP-GT-PROV -- the TEMPORAL PROVENANCE CERTIFICATE. It must pass before any new observer may exist.

Every case below is a boundary the D-067 defect walked through unchallenged. The suite proves two things and
refuses to proceed without both: that VALID features are accepted, and that INVALID features FAIL LOUDLY. An
assertion that cannot fire is not an assertion; it is a comment with a function call.
"""

from __future__ import annotations

import numpy as np

from ..substrates.boolnet.circuits import build
from ..identity.hier import World
from ..identity.provenance import (Episode, Row, ProvenanceError, _idx, run_episode, pulse_episode,
                                   extract, assert_rows_valid, required_window, coverage_report)


def _ep(T=40, world_id="W", eid="E"):
    m = build(program=(1, 1, 1), impl="direct")
    w = World(m.net, m.out_cells)
    return run_episode(w, world_id, eid, {}, T), m, w


def certificate() -> dict:
    cases = []

    def case(name, ok, detail=""):
        cases.append({"case": name, "PASS": bool(ok), "detail": detail})

    def must_raise(name, fn, detail=""):
        try:
            fn()
        except ProvenanceError as e:
            cases.append({"case": name, "PASS": True, "detail": f"raised: {str(e).splitlines()[0][:88]}"})
            return
        cases.append({"case": name, "PASS": False, "detail": f"DID NOT RAISE -- {detail}"})

    ep, m, w = _ep(T=40)
    clk, reg = (1, 1), (4, 8)
    out = (8, 6)

    # ---------------------------------------------------------------- the index boundary itself
    case("P1  d < t   is valid", _idx(10, 3, 40) == 7, "t=10 d=3 -> 7")
    case("P2  d = t   is valid (index 0 is the first sample, not the last)", _idx(10, 10, 40) == 0, "t=10 d=10 -> 0")
    must_raise("P3  d = t+1  MUST RAISE (numpy would return the LAST sample)",
               lambda: _idx(10, 11, 40), "this is the exact D-067 arithmetic")
    must_raise("P4  a very long delay beyond the window MUST RAISE",
               lambda: _idx(5, 60, 40))
    must_raise("P5  a sample from the FUTURE is not a history",
               lambda: _idx(39, -2, 40))

    # numpy's behaviour, stated explicitly, so the danger is on the record and not in folklore
    arr = np.arange(40)
    case("P6  numpy DOES silently wrap a negative index (this is what was trusted)",
         arr[10 - 11] == 39, f"arr[10-11] = arr[-1] = {arr[10-11]}, not an error")

    # ---------------------------------------------------------------- extraction: valid rows fire
    feats = [(clk, 12), (reg, 1)]
    ex = extract(ep, feats, out, t_lo=0, t_hi=40)
    case("P7  rows whose history exists are extracted",
         len(ex["rows"]) == 40 - 12 and ex["n_excluded"] == 12,
         f"{len(ex['rows'])} rows kept, {ex['n_excluded']} excluded for missing history (t < 12)")
    case("P8  every extracted row is provenance-valid (source samples RE-READ and compared)",
         assert_rows_valid(ex["rows"], {ep.episode_id: ep}),
         f"{len(ex['rows'])} rows re-read from the episode at their own timestamps; all byte-equal")

    # ---------------------------------------------------------------- the poisoned row: it must be caught
    bad = ex["rows"][0]
    poisoned = Row(bad.world_id, bad.episode_id,
                   tuple((s, d, ts, 1 - v) for (s, d, ts, v) in bad.sources),   # a value the episode never held
                   bad.out_cell, bad.out_t, bad.out_value, bad.window, bad.context, True, bad.key)
    must_raise("P9  a FABRICATED source value is caught by re-reading the episode",
               lambda: assert_rows_valid([poisoned], {ep.episode_id: ep}),
               "the row claims a value the episode does not contain")

    wrapped = Row(bad.world_id, bad.episode_id,
                  tuple((s, d, (bad.out_t - d) % 40, v) for (s, d, _ts, v) in bad.sources),
                  bad.out_cell, bad.out_t, bad.out_value, bad.window, bad.context, True, bad.key)
    # exactly the D-067 defect, injected: a row labelled with a WRAPPED timestamp
    poison_t = 3
    dev = extract(ep, feats, out, t_lo=poison_t, t_hi=poison_t + 1)
    case("P10 the D-067 defect INJECTED: t=3, lag=12 -> the row is EXCLUDED, not wrapped",
         len(dev["rows"]) == 0 and dev["n_excluded"] == 1,
         "numpy would have labelled it with sample 31; the extractor excludes it and counts it")

    d067 = Row("W", "E", ((clk, 12, (3 - 12) % 40, int(ep.grid[(3 - 12) % 40, 1, 1])), (reg, 1, 2, int(ep.grid[2, 4, 8]))),
               out, 3, int(ep.grid[3, 8, 6]), (0, 40), (), True, ())
    must_raise("P11 a row carrying a WRAPPED timestamp is caught by the arithmetic check",
               lambda: assert_rows_valid([d067], {"E": ep}),
               "t-d = -9 was stored as 31; out_t - d != ts")

    # ---------------------------------------------------------------- windows: short and long channels
    # SAMPLING MUST BEGIN AT max(settle_margin, max_lag) -- NOT at a fixed margin. D-067's harvester started at a
    # fixed t=32 while the far channel's lag was 47, so its first fifteen rows had no history at all and were given
    # one anyway. The start of the usable region is a function of the LAG, not a constant chosen in advance.
    for name, lag in (("short channel (lag 12)", 12), ("long channel (lag 47)", 47)):
        T = required_window(lag, 8, 32)
        t_lo = max(32, lag)
        e2 = run_episode(w, "W", f"E{lag}", {}, T)
        ex2 = extract(e2, [(clk, lag), (reg, 1)], out, t_lo=t_lo, t_hi=T)
        usable = len(ex2["rows"])
        case(f"P12 {name}: window EXTENDED to fit the lag; sampling starts at max(margin, lag)",
             usable > 0 and ex2["n_excluded"] == 0 and T >= t_lo + 2 * 8,
             f"required window T={T}; sampling from t>={t_lo}; {usable} usable rows; "
             f"{ex2['n_excluded']} excluded (must be 0)")
        # and the SAME extraction started too early must exclude, loudly and countably
        bad = extract(e2, [(clk, lag), (reg, 1)], out, t_lo=0, t_hi=T)
        case(f"P12b {name}: starting before the history exists EXCLUDES and COUNTS, never fabricates",
             bad["n_excluded"] == lag and len(bad["rows"]) == T - lag,
             f"{bad['n_excluded']} rows excluded (= the lag), {len(bad['rows'])} kept")

    # a window that is TOO SHORT must exclude, not fabricate
    e3 = run_episode(w, "W", "Eshort", {}, 40)
    ex3 = extract(e3, [(clk, 47), (reg, 1)], out, t_lo=32, t_hi=40)
    case("P13 a window shorter than the lag yields ZERO rows and an honest count -- never a fabricated one",
         len(ex3["rows"]) == 0 and ex3["n_excluded"] == 8,
         f"{ex3['n_excluded']}/{ex3['n_total']} steps excluded: the history does not exist and is not invented")

    # ---------------------------------------------------------------- history exactly at the left boundary
    ex4 = extract(ep, [(clk, 12), (reg, 1)], out, t_lo=12, t_hi=13)
    case("P14 a history landing EXACTLY on the left boundary (t == d, index 0) is VALID and is kept",
         len(ex4["rows"]) == 1 and ex4["rows"][0].sources[0][2] == 0,
         "t=12, lag=12 -> source timestamp 0: the first sample of the episode, and a real one")

    # ---------------------------------------------------------------- episodes must not be mixed
    epA = run_episode(w, "W", "A", {}, 40)
    epB = run_episode(w, "W", "B", {reg: 0}, 40)
    rA = extract(epA, feats, out, 12, 40)["rows"][0]
    must_raise("P15 a row may not be validated against a DIFFERENT episode (concatenated storage is not a timeline)",
               lambda: assert_rows_valid([Row(rA.world_id, "B", rA.sources, rA.out_cell, rA.out_t,
                                              rA.out_value, rA.window, rA.context, True, rA.key)],
                                         {"B": epB}),
               "the samples belong to episode A; episode B holds different values")

    must_raise("P16 a row may not cross WORLDS",
               lambda: assert_rows_valid([Row("OTHER", "A", rA.sources, rA.out_cell, rA.out_t,
                                              rA.out_value, rA.window, rA.context, True, rA.key)],
                                         {"A": epA}))

    # ---------------------------------------------------------------- non-vacuity of the intervention itself
    must_raise("P17 a clamp that DID NOT TAKE is not evidence",
               lambda: Episode("W", "X", {clk: 1}, 40, 40, epA.grid, (), "sustained")
               and run_episode(_Deaf(), "W", "X", {clk: 1}, 40))

    n = sum(c["PASS"] for c in cases)
    return {"cases": cases, "n_pass": n, "n": len(cases), "QUALIFIED": n == len(cases)}


class _Deaf:
    """a world that ignores its clamps. The contract must notice."""
    def trace(self, clamp=None, hold=0, steps=0):
        return np.zeros((steps, 24, 64), dtype=np.uint8), None


def main():
    c = certificate()
    print("EXP-GT-PROV -- TEMPORAL PROVENANCE CERTIFICATE")
    print("=" * 104)
    for x in c["cases"]:
        print(f"  [{'PASS' if x['PASS'] else 'FAIL'}] {x['case']}")
        print(f"         {x['detail']}")
    print("=" * 104)
    print(f"  {c['n_pass']}/{c['n']}   QUALIFIED = {c['QUALIFIED']}")
    return c


if __name__ == "__main__":
    main()
