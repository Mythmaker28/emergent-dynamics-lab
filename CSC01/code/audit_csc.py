"""CSC01 §15 — adversarial audit of the protocol and the gate. Eighteen declared cases.

Every case is an attempt to make the gate say something it should not, or to show that a number
lives somewhere other than the yaml. Runs in STATIC mode except for the four bounded,
score-blind engine cases, which run in TEST mode under the harness step budget. No start of any
scientific class is opened.
"""
from __future__ import annotations

import copy
import json
import sys

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/CSC01/code")

import observe as OBS            # noqa: E402

import gatelib as GL             # noqa: E402
import guard_csc as GC           # noqa: E402
import lawspec_v2 as V2          # noqa: E402
import lawspec_v3 as V3          # noqa: E402
import protocol_csc as PC        # noqa: E402
import spatial as SP             # noqa: E402

OUT = "/home/claude/CSC01/out"
SPEC = PC.SPEC
F = list(OBS.Recorder.FIELDS)
W = SPEC["window"]
RESULTS = []
N1TAB = GL.n1_table(SPEC)


def check(name, ok, detail=""):
    RESULTS.append({"case": name, "PASS": bool(ok), "detail": str(detail)[:260]})
    print(("PASS  " if ok else "FAIL  ") + name + (("   " + str(detail)[:150]) if detail else ""))
    return bool(ok)


# ------------------------------------------------------------------ synthetic trace builder
def synth(n=None, N_X=120, deaths=None, births=None, N_Y=1, free_org=9.0, O=7781,
          drift=0.0, r80=3.0, core_fraction=0.9, wraps=False, core_free=6.0,
          org_walk=True, seed=0, spread=None):
    """A full (series, frames) pair with every quantity under explicit control."""
    n = int(n or W["HORIZON"])
    rng = np.random.default_rng(seed)
    a = np.zeros((n, len(F)))
    a[:, F.index("step")] = np.arange(1, n + 1)
    a[:, F.index("N_X")] = N_X
    a[:, F.index("N_Y")] = N_Y
    a[:, F.index("u_nX_at_org")] = 4.0
    a[:, F.index("free_at_org")] = free_org
    a[:, F.index("O_total")] = O * (1.0 + drift * np.linspace(0, 1, n))
    a[:, F.index("deaths_X")] = deaths if deaths is not None else N_X * 0.004
    a[:, F.index("accepted_births_X")] = births if births is not None else N_X * 0.004
    frames = []
    L = SPEC["geometry"]["L"]
    oy, ox = 18, 18
    for t in range(W["SAMPLE_EVERY"], n + 1, W["SAMPLE_EVERY"]):
        if org_walk:
            oy = int((oy + rng.integers(-1, 2)) % L)
            ox = int((ox + rng.integers(-1, 2)) % L)
        frames.append({"step": t, "N_X": int(np.atleast_1d(N_X)[0] if np.ndim(N_X) else N_X),
                       "r80": float(r80(t) if callable(r80) else r80),
                       "core_fraction": float(core_fraction), "any_component_wraps": bool(wraps),
                       "organiser_y": oy, "organiser_x": ox, "core_free_mean": float(core_free)})
    n1thr = {f["step"]: GL.n1_q01_r80(N1TAB, f["N_X"]) for f in frames}
    cfree = {f["step"]: f["core_free_mean"] for f in frames}
    return a, frames, n1thr, cfree


def run_both(a, frames, n1thr, cfree, seed=1, no_score=True):
    on = GL.OnlineGate(SPEC, seed, no_score_reading=no_score)
    by = {f["step"]: f for f in frames}
    for i in range(len(a)):
        on.step(a[i, F.index("N_X")], a[i, F.index("N_Y")], a[i, F.index("u_nX_at_org")],
                a[i, F.index("free_at_org")], a[i, F.index("O_total")],
                a[i, F.index("deaths_X")], a[i, F.index("accepted_births_X")])
        st = int(a[i, F.index("step")])
        if st in by:
            on.frame(by[st], n1thr[st], cfree[st])
    r_on = on.result()
    r_ph = GL.posthoc_gate(SPEC, a, F, frames, n1thr, cfree, seed, no_score_reading=no_score)
    return r_on, r_ph, GL.compare(r_on, r_ph)


# ------------------------------------------------------------------ the cases
def a01_frozen_crystal():
    a, fr, t1, cf = synth(deaths=0.0, births=0.0, r80=2.0, core_fraction=0.99, seed=1)
    on, ph, cmp_ = run_both(a, fr, t1, cf)
    return check("A01 a compact cluster with NO turnover is not COHESION_ACHIEVED",
                 ph["classification"] == "FROZEN_AGGREGATE" and cmp_["AGREE"],
                 f"{ph['classification']} turnover={ph['checks']['material_turnover']:.3f}")


def a02_jammed_lump():
    a, fr, t1, cf = synth(r80=2.0, core_fraction=0.99, core_free=0.0, seed=2)
    on, ph, cmp_ = run_both(a, fr, t1, cf)
    return check("A02 a compact cluster with NO free capacity inside the core is a jammed lump",
                 ph["classification"] == "FROZEN_AGGREGATE" and cmp_["AGREE"],
                 f"{ph['classification']} core_free={ph['checks']['core_free_capacity_mean']:.2f}")


def a03_wall_confined():
    a, fr, t1, cf = synth(r80=2.0, core_fraction=0.99, wraps=True, seed=3)
    on, ph, cmp_ = run_both(a, fr, t1, cf)
    return check("A03 a population that truly winds around the torus is a BOUNDARY_ARTEFACT",
                 ph["classification"] == "BOUNDARY_ARTEFACT" and cmp_["AGREE"],
                 ph["classification"])


def a04_occupancy_ratchet():
    a, fr, t1, cf = synth(r80=2.0, core_fraction=0.99, drift=0.5, seed=4)
    on, ph, cmp_ = run_both(a, fr, t1, cf)
    return check("A04 an occupancy drift above the declared tolerance is an OCCUPANCY_RATCHET",
                 ph["classification"] == "OCCUPANCY_RATCHET" and cmp_["AGREE"],
                 f"{ph['classification']} drift={ph['checks']['occupancy_drift']:.3f}")


def a05_extinction():
    a, fr, t1, cf = synth(r80=2.0, core_fraction=0.99, seed=5)
    a[6000:, F.index("N_X")] = 0.0
    on, ph, cmp_ = run_both(a, fr, t1, cf)
    return check("A05 extinction inside the window is MATERIAL_COLLAPSE",
                 ph["classification"] == "MATERIAL_COLLAPSE" and cmp_["AGREE"],
                 ph["classification"])


def a06_organiser_lost():
    a, fr, t1, cf = synth(r80=2.0, core_fraction=0.99, seed=6)
    a[7000:, F.index("N_Y")] = 0.0
    on, ph, cmp_ = run_both(a, fr, t1, cf)
    return check("A06 the loss of the organiser is ORGANISATION_LOST",
                 ph["classification"] == "ORGANISATION_LOST" and cmp_["AGREE"],
                 ph["classification"])


def a07_delocalised():
    a, fr, t1, cf = synth(r80=17.0, core_fraction=0.05, seed=7)
    on, ph, cmp_ = run_both(a, fr, t1, cf)
    return check("A07 a population as spread as complete spatial randomness is DELOCALISED",
                 ph["classification"] == "DELOCALISED" and cmp_["AGREE"],
                 f"{ph['classification']} compact_frac="
                 f"{ph['checks']['compact_vs_N1_fraction']:.2f} core_frac="
                 f"{ph['checks']['core_exists_fraction']:.2f}")


def a08_source_tethered_halo():
    """THE discriminating case: a cloud that is compact, durable and renewed, but no more
    compact than the no-interaction null. It must NOT be called cohesive."""
    a, fr, t1, cf = synth(r80=6.6, core_fraction=0.66, seed=8)
    on, ph, cmp_ = run_both(a, fr, t1, cf)
    return check("A08 a compact, durable, renewed, SOURCE-TETHERED halo is "
                 "LOCALISED_BUT_NOT_COHESIVE, never COHESION_ACHIEVED",
                 ph["classification"] == "LOCALISED_BUT_NOT_COHESIVE" and cmp_["AGREE"],
                 f"{ph['classification']} cohesion_frac="
                 f"{ph['checks']['cohesive_vs_N3b_fraction']:.2f}")


def a09_genuinely_cohesive():
    a, fr, t1, cf = synth(r80=1.5, core_fraction=0.99, seed=9)
    on, ph, cmp_ = run_both(a, fr, t1, cf)
    return check("A09 a cloud far more compact than the no-interaction null IS "
                 "COHESION_ACHIEVED, so the gate is not unpassable",
                 ph["classification"] == "COHESION_ACHIEVED" and ph["PASS"] and cmp_["AGREE"],
                 f"{ph['classification']} cohesion_frac="
                 f"{ph['checks']['cohesive_vs_N3b_fraction']:.2f}")


def a10_score_reading():
    a, fr, t1, cf = synth(r80=1.5, core_fraction=0.99, seed=10)
    on, ph, cmp_ = run_both(a, fr, t1, cf, no_score=False)
    return check("A10 an operator that reads a score is a PROTOCOL_VIOLATION even when every "
                 "other axis passes", ph["classification"] == "PROTOCOL_VIOLATION" and
                 not ph["PASS"] and cmp_["AGREE"], ph["classification"])


def a11_online_posthoc_agreement():
    rng = np.random.default_rng(11)
    bad = None
    for k in range(24):
        a, fr, t1, cf = synth(N_X=float(rng.integers(5, 260)),
                              deaths=float(rng.uniform(0, 1.5)),
                              births=float(rng.uniform(0, 1.5)),
                              free_org=float(rng.uniform(0, 12)),
                              drift=float(rng.uniform(0, 0.2)),
                              r80=float(rng.uniform(1, 18)),
                              core_fraction=float(rng.uniform(0, 1)),
                              wraps=bool(rng.integers(0, 2)),
                              core_free=float(rng.uniform(0, 10)), seed=100 + k)
        on, ph, cmp_ = run_both(a, fr, t1, cf, seed=100 + k)
        if not cmp_["AGREE"]:
            bad = {"trial": k, "diff": cmp_["differences"]}
            break
    return check("A11 the streaming gate and the array gate agree on 24 random synthetic "
                 "traces, field by field", bad is None, bad or "")


def a12_thresholds_live_only_in_the_yaml():
    """Perturb a yaml threshold; the verdict must follow it. If a number were hard-coded in the
    code, the verdict would not move."""
    a, fr, t1, cf = synth(r80=1.5, core_fraction=0.99, seed=12)
    base = GL.posthoc_gate(SPEC, a, F, fr, t1, cf, 12)
    moved = []
    for path, val, expect_change in (
            (("axes", "axis_3_live_not_frozen", "material_turnover_min"), 1e9, True),
            (("axes", "axis_2_durable", "core_exists_fraction_min"), 1.01, True),
            (("axes", "axis_1_compact_and_cohesive", "cohesive_vs_N3b", "threshold"), 1.01, True),
            (("axes", "axis_4_not_an_artefact", "occupancy_drift_max"), -1.0, True)):
        s2 = copy.deepcopy(SPEC)
        d = s2
        for k in path[:-1]:
            d = d[k]
        d[path[-1]] = val
        r = GL.posthoc_gate(s2, a, F, fr, t1, cf, 12)
        moved.append(bool(r["PASS"] != base["PASS"]) == expect_change)
    return check("A12 moving a threshold in the yaml moves the verdict, for all four axes: no "
                 "threshold is hard-coded", all(moved) and base["PASS"], str(moved))


def a13_v3_without_mechanism_is_v2():
    GC.set_test_mode()
    sp = PC.spec_for()
    hashes = []
    for cls in (V2.WorldV2, V3.WorldV3):
        kw = dict(lawspec=V2.LAWSPEC_V2_EXCHANGE, rng_mode="split_feed_stream",
                  exchangeable=V2.EXCHANGEABLE_DEFAULT, insert_mode="reservoir")
        if cls is V3.WorldV3:
            kw.update(cohesion=None, lam=0.0)
        w = cls(L=None, seed=424242, sp=sp, **kw)
        w.n["SX"][:] = sp.S0
        w.n["SY"][:] = sp.S0
        c = w.L // 2
        w.n["Y"][c, c] = 1
        w.n["X"][c, c] = PC.X_SEED
        GC.advance(w, 1500)
        hashes.append(w.state_hash())
    GC.set_static_mode()
    return check("A13 LawSpec v3 with no mechanism is state-for-state identical to v2 over "
                 "1500 steps", hashes[0] == hashes[1], hashes[0][:16] + " vs " + hashes[1][:16])


def a14_lambda_zero_is_no_mechanism():
    GC.set_test_mode()
    sp = PC.spec_for()
    hashes = []
    for coh, lam in ((None, 0.0), (V3.C3, 0.0)):
        w = V3.WorldV3(L=None, seed=515151, sp=sp, lawspec=V2.LAWSPEC_V2_EXCHANGE,
                       rng_mode="split_feed_stream", exchangeable=V2.EXCHANGEABLE_DEFAULT,
                       insert_mode="reservoir", cohesion=coh, lam=lam)
        w.n["SX"][:] = sp.S0
        w.n["SY"][:] = sp.S0
        c = w.L // 2
        w.n["Y"][c, c] = 1
        w.n["X"][c, c] = PC.X_SEED
        GC.advance(w, 1500)
        hashes.append(w.state_hash())
    GC.set_static_mode()
    return check("A14 the mechanism switched off by lambda = 0 reproduces the reference arm "
                 "state for state", hashes[0] == hashes[1],
                 hashes[0][:16] + " vs " + hashes[1][:16])


def a15_mechanism_only_lowers_death():
    lam = json.load(open(f"{OUT}/_calibration.json"))["lambda"]
    m = np.arange(0, 200)
    mu = PC.POINT["muX"] * (1 - lam) ** m
    ok = bool((mu <= PC.POINT["muX"] + 1e-15).all() and (mu >= 0).all() and
              abs(mu[0] - PC.POINT["muX"]) < 1e-15 and (np.diff(mu) <= 0).all())
    return check("A15 the mechanism can only LOWER a death probability: mu_eff(m) is "
                 "non-increasing, equals mu_X at m = 0 and never exceeds it", ok,
                 f"lambda={lam:.6f} mu(0)={mu[0]:.6f} mu(5)={mu[5]:.6f} mu(50)={mu[50]:.3e}")


def a16_locality():
    L = SPEC["geometry"]["L"]
    nX = np.zeros((L, L), np.int64)
    nX[10, 10] = 7
    m = V3.neighbour_count(nX)
    expect = np.zeros((L, L), np.int64)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        expect[(10 + dy) % L, (10 + dx) % L] = 7
    ok = bool(np.array_equal(m, expect)) and int(m[10, 10]) == 0
    return check("A16 the neighbour count reads EXACTLY the four neighbouring cells and not the "
                 "cell itself, and no global reduction enters it", ok,
                 f"nonzero cells = {int((m>0).sum())}")


def a17_invariant_manifolds():
    GC.set_test_mode()
    sp = PC.spec_for()
    lam = json.load(open(f"{OUT}/_calibration.json"))["lambda"]
    w = V3.fresh_world(707070, sp, lawspec=V2.LAWSPEC_V2_EXCHANGE, rng_mode="split_feed_stream",
                       exchangeable=V2.EXCHANGEABLE_DEFAULT, insert_mode="reservoir",
                       cohesion=V3.C3, lam=lam)
    GC.advance(w, 900)
    no_x = int(w.n["X"].sum()) == 0
    w2 = V3.fresh_world(808080, sp, lawspec=V2.LAWSPEC_V2_EXCHANGE, rng_mode="split_feed_stream",
                        exchangeable=V2.EXCHANGEABLE_DEFAULT, insert_mode="reservoir",
                        cohesion=V3.C3, lam=lam)
    c = w2.L // 2
    w2.n["X"][c, c] = 40                       # X present, NO organiser
    GC.advance(w2, 900)
    no_growth = int(w2.n["X"].sum()) <= 40
    GC.set_static_mode()
    return check("A17 under the mechanism, n_X = 0 stays 0 and n_Y = 0 still forbids every X "
                 "birth: the pre-declared controls keep their meaning",
                 no_x and no_growth, f"n_X after 900 steps without an organiser: "
                                     f"{int(w.n['X'].sum())} and {int(w2.n['X'].sum())} from 40")


def a18_no_window_no_pass():
    a, fr, t1, cf = synth(N_X=1.0, r80=1.0, core_fraction=1.0, seed=18)
    a[:, F.index("u_nX_at_org")] = 0.0
    on, ph, cmp_ = run_both(a, fr, t1, cf)
    return check("A18 an arm that never forms cannot pass, whatever its geometry looks like",
                 (not ph["PASS"]) and ph["classification"] in ("NO_FORMATION",
                                                               "TRANSIENT_FORMATION")
                 and cmp_["AGREE"], ph["classification"])


CASES = [a01_frozen_crystal, a02_jammed_lump, a03_wall_confined, a04_occupancy_ratchet,
         a05_extinction, a06_organiser_lost, a07_delocalised, a08_source_tethered_halo,
         a09_genuinely_cohesive, a10_score_reading, a11_online_posthoc_agreement,
         a12_thresholds_live_only_in_the_yaml, a13_v3_without_mechanism_is_v2,
         a14_lambda_zero_is_no_mechanism, a15_mechanism_only_lowers_death, a16_locality,
         a17_invariant_manifolds, a18_no_window_no_pass]


def main():
    GC.set_static_mode()
    for c in CASES:
        c()
    allp = all(r["PASS"] for r in RESULTS)
    ast_audit = PC.audit_no_score_reading()
    print()
    print("cases run                     %d" % len(RESULTS))
    print("AST audit of the operator     %s" % ("PASS" if ast_audit["PASS"] else "FAIL"))
    print("SCIENTIFIC_RUNS_USED          %d" % GC.scientific_runs_used())
    print("PROTOCOL_ADVERSARIAL_AUDIT = %s" % ("PASS" if (allp and ast_audit["PASS"]) else "FAIL"))
    json.dump({"cases": RESULTS, "n_cases": len(RESULTS),
               "ast_audit": ast_audit,
               "GATE_SINGLE_SOURCE_OF_TRUTH": bool(
                   next(r["PASS"] for r in RESULTS if r["case"].startswith("A12"))),
               "ONLINE_POSTHOC_SYNTHETIC_AGREEMENT": bool(
                   next(r["PASS"] for r in RESULTS if r["case"].startswith("A11"))),
               "PROTOCOL_ADVERSARIAL_AUDIT": "PASS" if (allp and ast_audit["PASS"]) else "FAIL",
               "gate_spec_sha256": GL.spec_sha256(),
               "ledger": GC.audit()},
              open(f"{OUT}/_audit.json", "w"), indent=1, default=str)
    return 0 if (allp and ast_audit["PASS"]) else 1


if __name__ == "__main__":
    sys.exit(main())
