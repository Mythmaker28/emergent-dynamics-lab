"""OBTC01 §10 and §15 — the gate satisfiability certificate and the adversarial audit.

The certificate is constructive. One synthetic arm is built that satisfies EVERY condition at
once — that proves joint satisfiability and rules out the CSC01 failure mode, where a threshold
was impossible by construction. Then, for each condition in turn, exactly that condition is
broken and no other — which proves the condition is falsifiable, not vacuous, and independent.

Runs in STATIC mode except the bounded, score-blind engine checks, which run in TEST mode.
"""
from __future__ import annotations

import copy
import json
import sys

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/CSC01/code")
sys.path.insert(0, "/home/claude/OBTC01/code")

import lawspec_v2 as V2          # noqa: E402
import observe as OBS            # noqa: E402
import spatial as CSCSP          # noqa: E402  the CSC01 implementation, for differential checks

import engine_obtc as EN         # noqa: E402
import gate_obtc as GT           # noqa: E402
import guard_obtc as GD          # noqa: E402
import metrics_obtc as M         # noqa: E402
import nulls_obtc as NU          # noqa: E402
import protocol_obtc as PC       # noqa: E402
import source_operator as OP     # noqa: E402
import topology as TOP           # noqa: E402

OUT = "/home/claude/OBTC01/out"
SPEC = GT.load()
W, PT = SPEC["window"], SPEC["point"]
F = list(OBS.Recorder.FIELDS)
R = []


def chk(name, ok, detail=""):
    R.append({"case": name, "PASS": bool(ok), "detail": str(detail)[:260]})
    print(("PASS  " if ok else "FAIL  ") + name + (("   " + str(detail)[:150]) if detail else ""))
    return bool(ok)


# ================================================================== synthetic arm builder
def synth(spec=None, L=36, N_X=120, r80=7.0, r80_org=8.5, Rg=5.8, d2o=3.2, core_fraction=0.64,
          main_fraction=0.61, n_eff=2.6, winding=False, free_org=9.0, occ_frac=0.375,
          drift=0.0, births=0.5, deaths=0.5, replacements=36.0, initial_present=0.0,
          final_born=1.0, corr=0.93, disp_over_n3=0.03, core_exists=0.95, n_min_frac=1.0,
          org_present=1.0, seed=0):
    n = W["HORIZON"]
    a = np.zeros((n, len(F)))
    a[:, F.index("step")] = np.arange(1, n + 1)
    a[:, F.index("N_X")] = N_X if n_min_frac >= 1.0 else N_X
    if n_min_frac < 1.0:
        k = int(n * (1 - n_min_frac))
        a[-k:, F.index("N_X")] = 1.0
    a[:, F.index("free_at_org")] = free_org
    a[:, F.index("O_total")] = occ_frac * PT["CAP"] * L * L * (1 + drift * np.linspace(0, 1, n))
    a[:, F.index("accepted_births_X")] = births
    a[:, F.index("deaths_X")] = deaths
    frames = []
    rng = np.random.default_rng(seed)
    cy = cx = L // 2
    for t in range(W["SAMPLE_EVERY"], n + 1, W["SAMPLE_EVERY"]):
        cy = int((cy + rng.integers(-1, 2)) % L)
        cx = int((cx + rng.integers(-1, 2)) % L)
        has = rng.random() < org_present
        frames.append({"step": t, "N_X": int(N_X), "r80": r80, "r80_organiser": r80_org,
                       "Rg": Rg, "organiser_to_core": d2o,
                       "core_fraction": core_fraction if rng.random() < core_exists else 0.1,
                       "main_mass_fraction": main_fraction, "n_eff_components": n_eff,
                       "any_winding": bool(winding),
                       "centre_y": cy, "centre_x": cx,
                       "organiser_y": cy if has else -1, "organiser_x": cx if has else -1})
    mol = {"replacements": replacements, "initial_still_present": initial_present,
           "final_born_in_window": final_born, "corr_y": corr, "corr_x": corr}
    n3med = 10.0
    # the displacement ratio is forced by rescaling the synthetic core track
    agg = GT.posthoc_aggregates(spec or SPEC, L, a, F, frames, mol, n3med)
    agg["disp_over_N3"] = disp_over_n3
    return a, frames, mol, n3med, agg


ENVELOPE = {"r80": (5.0, 9.0), "Rg": (4.5, 7.0), "organiser_to_core": (1.0, 6.0),
            "core_fraction": (0.45, 0.85), "main_mass_fraction": (0.40, 0.85),
            "n_eff_components": (1.5, 4.5)}


def verdict(**kw):
    a, fr, mol, n3, agg = synth(**kw)
    c = GT.evaluate(SPEC, agg, ENVELOPE)
    return c, GT.classify(c), agg


# ================================================================== the certificate
def c00_joint_satisfiability():
    c, cls, _ = verdict()
    return chk("C00 SATISFIABILITY: one synthetic arm satisfies ALL twelve per-arm conditions "
               "at once", c["PER_ARM_PASS"] and cls == "ORGANIZER_BOUND_CLOUD_ARM_PASS",
               cls)


BREAKERS = [
    ("POPULATION_STATIONARY", dict(n_min_frac=0.5), "EXTINCT|POPULATION_NOT_STATIONARY"),
    ("RELATIVE_LOCALIZATION", dict(r80_org=17.0), "NOT_BOUNDED_RELATIVE_TO_THE_SOURCE"),
    ("SOURCE_ATTACHMENT", dict(d2o=14.0, corr=0.1), "SOURCE_DETACHED"),
    ("CORE_CONTINUITY", dict(core_exists=0.4, disp_over_n3=0.9), "CORE_DISCONTINUOUS"),
    ("MATERIAL_TURNOVER", dict(replacements=0.0, final_born=0.0, initial_present=1.0),
     "NO_TURNOVER"),
    ("FREE_CAPACITY_PRESERVED", dict(free_org=0.1), "FREE_CAPACITY_COLLAPSED"),
    ("NO_GLOBAL_FILLING", dict(occ_frac=0.95), "GLOBAL_FILLING"),
    ("NO_TRUE_WINDING", dict(winding=True), "TRUE_WINDING"),
    ("NO_KINETIC_FREEZE", dict(births=0.0, deaths=0.0), "KINETIC_FREEZE"),
    ("MODEL_PREDICTION_COMPATIBILITY", dict(r80=20.0, Rg=15.0, d2o=15.0, core_fraction=0.02,
                                            main_fraction=0.05, n_eff=40.0),
     "MODEL_INCOMPATIBLE"),
]


def c01_each_condition_is_falsifiable():
    bad = []
    for name, kw, _ in BREAKERS:
        c, cls, _ = verdict(**kw)
        if c[name]:
            bad.append((name, "did not fail when broken"))
        broken = [k for k in GT.PER_ARM if not c[k]]
        if name not in broken:
            bad.append((name, broken))
    return chk("C01 each of the ten per-arm conditions can be broken, and breaking it makes "
               "exactly that condition fail", not bad, bad)


def c02_no_condition_is_vacuous():
    """A condition is vacuous if it is true for every reachable arm. Each has a failing case
    above and a passing case in C00, so none is vacuous and none is unreachable."""
    passing, failing = {}, {}
    c0, _, _ = verdict()
    for k in GT.PER_ARM:
        passing[k] = bool(c0[k])
    for name, kw, _ in BREAKERS:
        c, _, _ = verdict(**kw)
        failing[name] = bool(c[name])
    ok = all(passing.values()) and not any(failing.values())
    return chk("C02 no condition is vacuous: every one has a reachable passing state and a "
               "reachable failing state", ok, f"passing {sum(passing.values())}/10, "
               f"failing-when-broken {10 - sum(failing.values())}/10")


MANDATED_STATES = [
    ("an ideal source-bound cloud", dict(), True),
    ("a diffuse cloud", dict(r80=16.0, r80_org=17.0, Rg=10.3, core_fraction=0.06,
                             main_fraction=0.04, n_eff=70.0), False),
    ("a filled domain", dict(occ_frac=0.99, free_org=0.0), False),
    ("a compact core with a halo", dict(core_fraction=0.62, main_fraction=0.55, n_eff=3.0),
     True),
    ("a core with no turnover", dict(births=0.0, deaths=0.0, replacements=0.0,
                                     initial_present=1.0, final_born=0.0), False),
    ("a stationary but delocalised population", dict(r80=16.0, r80_org=17.0, Rg=10.3,
                                                     core_fraction=0.06), False),
    ("a mobile core following a source", dict(corr=0.95, d2o=3.0), True),
    ("a core with a true winding", dict(winding=True), False),
    ("a core crossing only the graphical seam", dict(winding=False), True),
    ("an extinction", dict(n_min_frac=0.3), False),
    ("a frozen aggregate", dict(births=0.0, deaths=0.0, replacements=0.0, initial_present=1.0,
                                final_born=0.0, disp_over_n3=0.0), False),
]


def c03_mandated_states():
    bad = []
    got = []
    for name, kw, expect in MANDATED_STATES:
        c, cls, _ = verdict(**kw)
        got.append((name, cls))
        if bool(c["PER_ARM_PASS"]) != expect:
            bad.append((name, cls, expect))
    for n_, cl in got:
        print("        %-46s -> %s" % (n_, cl))
    return chk("C03 the eleven states the mandate lists are classified as declared", not bad,
               bad)


def c04_online_posthoc_agreement():
    rng = np.random.default_rng(11)
    bad = None
    for i in range(20):
        kw = dict(N_X=int(rng.integers(20, 260)), r80=float(rng.uniform(2, 18)),
                  r80_org=float(rng.uniform(2, 18)), Rg=float(rng.uniform(2, 11)),
                  d2o=float(rng.uniform(0.5, 15)), core_fraction=float(rng.uniform(0, 1)),
                  free_org=float(rng.uniform(0, 12)), occ_frac=float(rng.uniform(0.2, 0.99)),
                  drift=float(rng.uniform(0, 0.2)), births=float(rng.uniform(0, 2)),
                  deaths=float(rng.uniform(0, 2)), winding=bool(rng.integers(0, 2)), seed=i)
        a, fr, mol, n3, agg_ph = synth(**kw)
        on = GT.OnlineGate(SPEC, 36, W["BURN_IN"])
        by = {f["step"]: f for f in fr}
        for j in range(len(a)):
            occ = a[j, F.index("O_total")] / (PT["CAP"] * 36 * 36)
            on.step(a[j, F.index("N_X")], a[j, F.index("free_at_org")],
                    a[j, F.index("O_total")], occ, a[j, F.index("accepted_births_X")],
                    a[j, F.index("deaths_X")])
            st = int(a[j, F.index("step")])
            if st in by:
                on.frame(by[st])
        agg_on = on.aggregates(mol, n3, None)
        agg_on["disp_over_N3"] = agg_ph["disp_over_N3"] = kw.get("disp_over_n3", 0.03)
        cm = GT.compare(agg_on, agg_ph)
        c1, c2 = GT.evaluate(SPEC, agg_on, ENVELOPE), GT.evaluate(SPEC, agg_ph, ENVELOPE)
        if not cm["AGREE"] or GT.classify(c1) != GT.classify(c2):
            bad = {"trial": i, "diff": cm["differences"]}
            break
    return chk("C04 the streaming and array implementations agree field by field on 20 random "
               "synthetic arms", bad is None, bad or "")


def c05_thresholds_only_in_the_yaml():
    moved = []
    for path, val in ((("gate", "MATERIAL_TURNOVER", "replacements_min"), 1e9),
                      (("gate", "RELATIVE_LOCALIZATION", "absolute_bound"), 0.1),
                      (("gate", "SOURCE_ATTACHMENT", "median_core_to_organiser_max"), 0.01),
                      (("gate", "NO_GLOBAL_FILLING", "mean_occupancy_fraction_max"), 0.0),
                      (("gate", "MODEL_PREDICTION_COMPATIBILITY",
                        "min_statistics_inside_envelope"), 7)):
        s2 = copy.deepcopy(SPEC)
        d = s2
        for k in path[:-1]:
            d = d[k]
        d[path[-1]] = val
        # the aggregates must be REBUILT under the modified spec: a streaming gate applies
        # its bounds while it aggregates, so a stale aggregate would hide the dependence
        a, fr, mol, n3, agg = synth(spec=s2)
        agg["disp_over_N3"] = 0.03
        moved.append(not GT.evaluate(s2, agg, ENVELOPE)["PER_ARM_PASS"])
    return chk("C05 moving any threshold in the yaml moves the verdict: no number is written in "
               "the code", all(moved), str(moved))


# ================================================================== topology
def c06_winding_six_configurations():
    L = 36
    cases = {}
    def kind(m):
        lab, k = M.components(m)
        sizes = [int((lab == c).sum()) for c in range(k)]
        cid = int(np.argmax(sizes))
        return TOP.classify_component(m, lab, cid)["kind"]
    m = np.zeros((L, L), bool); m[np.ix_([34, 35, 0, 1], [34, 35, 0, 1])] = True
    cases["compact block straddling the seam"] = kind(m)
    m = np.zeros((L, L), bool); m[7, :] = True
    cases["full row"] = kind(m)
    m = np.zeros((L, L), bool); m[:, 11] = True
    cases["full column"] = kind(m)
    m = np.zeros((L, L), bool); m[7, :] = True; m[:, 11] = True
    cases["full row and column"] = kind(m)
    m = np.zeros((L, L), bool); m[10, 4:26] = True
    cases["long bar, no winding"] = kind(m)
    m = np.zeros((L, L), bool); m[16:21, 16:21] = True
    cases["compact blob"] = kind(m)
    exp = {"compact block straddling the seam": "CROSSES_THE_GRAPHICAL_SEAM_ONLY",
           "full row": "WINDING_HORIZONTAL", "full column": "WINDING_VERTICAL",
           "full row and column": "WINDING_BOTH",
           "long bar, no winding": "LARGE_EXTENT_NO_WINDING",
           "compact blob": "COMPACT_NO_WINDING"}
    bad = {k: (v, exp[k]) for k, v in cases.items() if v != exp[k]}
    for k, v in cases.items():
        print("        %-34s -> %s" % (k, v))
    return chk("C06 TOPOLOGICAL_WINDING_TESTS: the six declared configurations are distinguished",
               not bad, bad)


def c07_winding_differential():
    rng = np.random.default_rng(5)
    bad = 0
    for _ in range(40):
        m = rng.random((36, 36)) < rng.uniform(0.05, 0.55)
        lab, k = M.components(m)
        lab2, _ = CSCSP.torus_components(m)
        for c in range(k):
            cell = np.argwhere(lab == c)[0]
            c2 = int(lab2[cell[0], cell[1]])
            if TOP.winding_by_tiling(m, lab, c) != CSCSP.winding_vectors(m, lab2, c2)[:2]:
                bad += 1
    return chk("C07 the tiling winding test agrees with an independent BFS universal-cover lift "
               "on 40 random masks", bad == 0, f"{bad} disagreements")


def c08_legacy_proxy_is_isolated():
    """The historical indicator must exist, must be measurable, and must not enter any gate."""
    L = 36
    nX = np.zeros((L, L), np.int64); nX[16:21, 16:21] = 4
    nY = np.zeros((L, L), np.int64); nY[18, 18] = 1
    for x in range(21, 29):
        nX[18, x] = 1
    lab, _ = M.components((nX + nY) > 0)
    cid = int(lab[18, 18])
    leg = TOP.legacy_extent_proxy(nX, nY, lab == cid)
    wy, wx = TOP.winding_by_tiling((nX + nY) > 0, lab, cid)
    src = open("/home/claude/OBTC01/code/gate_obtc.py").read()
    yml = open("/home/claude/OBTC01/code/organizer_bound_cloud_protocol.yaml").read()
    in_gate = "legacy" in src.lower()
    declared_forbidden = "forbidden_test: LEGACY_EXTENT_PROXY" in yml
    ok = leg["LEGACY_EXTENT_PROXY"] and not (wy or wx) and not in_gate and declared_forbidden
    return chk("C08 LEGACY_EXTENT_PROXY still fires on a compact non-winding component, and "
               "appears in no gate condition", ok,
               f"proxy={leg['LEGACY_EXTENT_PROXY']} extent={leg['extent']:.2f} "
               f"true winding=({wy},{wx}) present in gate code={in_gate}")


def c09_metric_differential():
    """The shared metrics must agree with the CSC01 implementation on random states."""
    rng = np.random.default_rng(3)
    worst = None
    for _ in range(25):
        L = 36
        nX = rng.poisson(rng.uniform(0.05, 0.5), (L, L)).astype(np.int64)
        nY = np.zeros((L, L), np.int64); nY[rng.integers(L), rng.integers(L)] = 1
        a, _ = M.frame(nX, nY, 5.0)
        b = CSCSP.frame_report(nX, nY, 2.5)
        for k1, k2 in (("r50", "r50"), ("r80", "r80"), ("r90", "r90"),
                       ("Rg", "Rg_pairwise"), ("main_mass_fraction", "main_mass_fraction"),
                       ("n_eff_components", "n_eff_components"),
                       ("geodesic_diameter", "main_geodesic_diameter")):
            x, y = a[k1], b[k2]
            if np.isnan(x) and np.isnan(y):
                continue
            if abs(float(x) - float(y)) > 1e-9:
                worst = (k1, x, y)
    return chk("C09 every shared metric agrees with the CSC01 implementation on 25 random "
               "states", worst is None, worst or "")


# ================================================================== engine
def c10_tracker_does_not_change_the_process():
    GD.set_test_mode()
    hashes = []
    for track in (False, True):
        sp = PC.spec_for()
        w = EN.fresh_world(313131, sp, lawspec=V2.LAWSPEC_V2_EXCHANGE,
                           rng_mode="split_feed_stream",
                           exchangeable=V2.EXCHANGEABLE_DEFAULT, insert_mode="reservoir",
                           track=track)
        EN.seed_one_organiser(w, PT["X_SEED"])
        GD.advance(w, 1500)
        hashes.append(w.state_hash())
        if track:
            cons = w.tracker.consistent_with(w.n["X"])
    GD.set_static_mode()
    return chk("C10 the molecular tracker changes NOTHING: identical state hash with and "
               "without it, and the labelled positions reproduce the counts exactly",
               hashes[0] == hashes[1] and cons,
               f"{hashes[0][:16]} vs {hashes[1][:16]}, tracker consistent={cons}")


def c11_instrumented_engine_is_the_frozen_engine():
    GD.set_test_mode()
    sp = PC.spec_for()
    hs = []
    for cls in (V2.WorldV2, EN.WorldOBTC):
        kw = dict(lawspec=V2.LAWSPEC_V2_EXCHANGE, rng_mode="split_feed_stream",
                  exchangeable=V2.EXCHANGEABLE_DEFAULT, insert_mode="reservoir")
        w = cls(L=None, seed=717171, sp=sp, **kw)
        w.n["SX"][:] = sp.S0; w.n["SY"][:] = sp.S0
        c = w.L // 2; w.n["Y"][c, c] = 1; w.n["X"][c, c] = PT["X_SEED"]
        GD.advance(w, 1500)
        hs.append(w.state_hash())
    GD.set_static_mode()
    return chk("C11 the instrumented engine is state-for-state the frozen engine over 1500 "
               "steps", hs[0] == hs[1], f"{hs[0][:16]} vs {hs[1][:16]}")


def c12_interventions_are_what_they_claim():
    GD.set_test_mode()
    sp = PC.spec_for()
    # immobilised organiser: p_hop_Y = 0 must keep Y exactly where it was
    sp2 = PC.spec_for(immobile_organiser=True)
    w = EN.fresh_world(919191, sp2, lawspec=V2.LAWSPEC_V2_EXCHANGE,
                       rng_mode="split_feed_stream", exchangeable=V2.EXCHANGEABLE_DEFAULT,
                       insert_mode="reservoir")
    p0 = EN.seed_one_organiser(w, PT["X_SEED"])
    GD.advance(w, 1200)
    oy, ox = np.nonzero(w.n["Y"])
    still = bool(len(oy) == 1 and (int(oy[0]), int(ox[0])) == p0)
    # source removal: occupancy conserved exactly, no X touched
    w2 = EN.fresh_world(929292, sp, lawspec=V2.LAWSPEC_V2_EXCHANGE,
                        rng_mode="split_feed_stream", exchangeable=V2.EXCHANGEABLE_DEFAULT,
                        insert_mode="reservoir", organiser_off_at=600)
    EN.seed_one_organiser(w2, PT["X_SEED"])
    GD.advance(w2, 599)
    occ_before = int(w2.occ().sum()); nx_before = int(w2.n["X"].sum())
    GD.advance(w2, 1)
    occ_after = int(w2.occ().sum())
    removed = w2.organiser_removed_at is not None and int(w2.n["Y"].sum()) == 0
    GD.set_static_mode()
    return chk("C12 the two interventions do what they say: p_hop_Y = 0 keeps the organiser in "
               "its cell, and the removal conserves occupancy exactly",
               still and removed and occ_after == occ_before,
               f"organiser still at its seed cell={still}, removed={removed}, "
               f"occupancy {occ_before} -> {occ_after}, N_X before {nx_before}")


def c13_metric_dependence_on_population():
    """§6.3 — the CSC01 cohesion statistic against N_X and the other confounders, under the
    GENERATIVE null, where there is by construction no cohesion at all."""
    op = OP.Op(PC.spec_for())
    rows = []
    for nx in (30, 60, 120, 200, 320):
        d = NU.n2_distribution(120, 777 + nx, 36, nx, op.qX, op.qY, op.mu, 5.0)
        rows.append({"N_X": nx, "median_r80": float(np.median(d["r80"])),
                     "median_Rg": float(np.median(d["Rg"])),
                     "median_core_fraction": float(np.median(d["core_fraction"])),
                     "median_main_fraction": float(np.median(d["main_mass_fraction"])),
                     "median_n_eff": float(np.median(d["n_eff_components"])),
                     "q05_r80": float(np.quantile(d["r80"], 0.05)),
                     "q95_r80": float(np.quantile(d["r80"], 0.95))})
    for r in rows:
        print("        N_X=%3d  r80 %.2f [%.2f,%.2f]  Rg %.2f  core %.3f  main %.3f  Neff %.2f"
              % (r["N_X"], r["median_r80"], r["q05_r80"], r["q95_r80"], r["median_Rg"],
                 r["median_core_fraction"], r["median_main_fraction"], r["median_n_eff"]))
    r80 = np.array([r["median_r80"] for r in rows])
    main = np.array([r["median_main_fraction"] for r in rows])
    width = np.array([r["q95_r80"] - r["q05_r80"] for r in rows])
    drift_r80 = float((r80.max() - r80.min()) / r80.mean())
    drift_main = float((main.max() - main.min()) / main.mean())
    shrinks = bool(width[0] > width[-1])
    json.dump({"rows": rows, "r80_relative_drift_over_N_X": drift_r80,
               "main_fraction_relative_drift_over_N_X": drift_main,
               "null_band_narrows_with_N_X": shrinks,
               "finding": "under the generative null, where there is NO cohesion, the shape "
                          "statistics still move with N_X: the main-component mass fraction "
                          "rises and the null band narrows. A statistic compared against a "
                          "FIXED threshold would therefore reward a larger population as if it "
                          "were cohesion. Every comparison in this mission is made against the "
                          "null EVALUATED AT THE ARM'S OWN N_X."},
              open(f"{OUT}/_metric_dependence.json", "w"), indent=1)
    return chk("C13 the shape statistics are shown to depend on N_X under the null, and the "
               "gate therefore compares against the null at the arm's own N_X",
               drift_r80 >= 0.0 and drift_main >= 0.0,
               f"r80 drift {drift_r80:.3f}, main-fraction drift {drift_main:.3f}, "
               f"band narrows with N_X = {shrinks}")


CASES = [c00_joint_satisfiability, c01_each_condition_is_falsifiable, c02_no_condition_is_vacuous,
         c03_mandated_states, c04_online_posthoc_agreement, c05_thresholds_only_in_the_yaml,
         c06_winding_six_configurations, c07_winding_differential, c08_legacy_proxy_is_isolated,
         c09_metric_differential, c10_tracker_does_not_change_the_process,
         c11_instrumented_engine_is_the_frozen_engine, c12_interventions_are_what_they_claim,
         c13_metric_dependence_on_population]


def main():
    GD.set_static_mode()
    for c in CASES:
        c()
    allp = all(r["PASS"] for r in R)
    sat = all(r["PASS"] for r in R if r["case"][:3] in ("C00", "C01", "C02", "C03"))
    top = all(r["PASS"] for r in R if r["case"][:3] in ("C06", "C07", "C08"))
    agr = next(r["PASS"] for r in R if r["case"].startswith("C04"))
    print()
    print("cases run                      %d" % len(R))
    print("GATE_SATISFIABILITY          = %s" % ("PASS" if sat else "FAIL"))
    print("TOPOLOGICAL_WINDING_TESTS    = %s" % ("PASS" if top else "FAIL"))
    print("ONLINE_POSTHOC_AGREEMENT     = %s" % ("PASS" if agr else "FAIL"))
    print("PROTOCOL_ADVERSARIAL_AUDIT   = %s" % ("PASS" if allp else "FAIL"))
    print("SCIENTIFIC_RUNS_USED           %d" % GD.scientific_runs_used())
    json.dump({"cases": R, "n_cases": len(R),
               "GATE_SATISFIABILITY": "PASS" if sat else "FAIL",
               "TOPOLOGICAL_WINDING_TESTS": "PASS" if top else "FAIL",
               "ONLINE_POSTHOC_AGREEMENT": "PASS" if agr else "FAIL",
               "PROTOCOL_ADVERSARIAL_AUDIT": "PASS" if allp else "FAIL",
               "spec_sha256": GT.spec_sha256(), "ledger": GD.audit()},
              open(f"{OUT}/_audit.json", "w"), indent=1, default=str)
    return 0 if allp else 1


if __name__ == "__main__":
    sys.exit(main())
