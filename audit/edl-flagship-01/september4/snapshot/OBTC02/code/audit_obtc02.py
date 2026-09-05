"""OBTC02 §7, §8, §13 — frame transport, third boundaries, online/post-hoc agreement, and the
constructive satisfiability certificate over all TWELVE conditions.

The ten per-arm conditions and the two cross-arm ones are certified. OBTC01 grouped them as
"ten per-arm plus two cross-arm"; the grouping convention is stated explicitly here and both
groups are exercised.
"""
from __future__ import annotations

import copy
import json
import sys

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/CSC01/code")
sys.path.insert(0, "/home/claude/OBTC02/code")

import lawspec_v2 as V2          # noqa: E402
import observe as OBS            # noqa: E402

import engine_obtc as EN         # noqa: E402
import gate_obtc02 as GT         # noqa: E402
import guard_obtc as GD          # noqa: E402
import protocol_obtc02 as PC     # noqa: E402
import source_operator as OP     # noqa: E402
import topology as TOP           # noqa: E402
import metrics_obtc as M         # noqa: E402

OUT = "/home/claude/OBTC02/out"
SPEC = GT.load()
W, PT = SPEC["window"], SPEC["point"]
F = list(OBS.Recorder.FIELDS)
R = []
ANALYTIC = OP.Op(PC.spec_for()).predictions()


def chk(name, ok, detail=""):
    R.append({"case": name, "PASS": bool(ok), "detail": str(detail)[:300]})
    print(("PASS  " if ok else "FAIL  ") + name + (("   " + str(detail)[:160]) if detail else ""))
    return bool(ok)


# ================================================================== synthetic arm
def synth(spec=None, L=36, N_X=120, r80=7.0, r80_org=8.5, Rg=5.8, d2o=3.2, core_fraction=0.64,
          main_fraction=0.61, n_eff=2.6, winding=False, free_org=9.0, occ_frac=0.375,
          drift=0.0, births=0.5, deaths=0.5, replacements=36.0, initial_present=0.0,
          final_born=1.0, corr=0.93, disp_over_n3=0.03, core_exists=0.95, n_min_frac=1.0,
          org_present=1.0, seed=0, drop=(), duplicate=(), shift=0):
    sp = spec or SPEC
    n = W["HORIZON"]
    a = np.zeros((n, len(F)))
    a[:, F.index("step")] = np.arange(1, n + 1)
    a[:, F.index("N_X")] = N_X
    if n_min_frac < 1.0:
        a[-int(n * (1 - n_min_frac)):, F.index("N_X")] = 1.0
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
                       "any_winding": bool(winding), "centre_y": cy, "centre_x": cx,
                       "organiser_y": cy if has else -1, "organiser_x": cx if has else -1})
    mol = {"replacements": replacements, "initial_still_present": initial_present,
           "final_born_in_window": final_born, "corr_y": corr, "corr_x": corr}
    return sp, a, frames, mol, 10.0, disp_over_n3


def run_both(sp, a, frames, mol, n3, dispn3, L=36, drop=(), duplicate=(), shift=0,
             skip_all=False):
    on = GT.OnlineGate(sp, L, W["BURN_IN"])
    by = {f["step"]: f for f in frames}
    seen = []
    for j in range(len(a)):
        occ = a[j, F.index("O_total")] / (PT["CAP"] * L * L)
        on.step(a[j, F.index("N_X")], a[j, F.index("free_at_org")], a[j, F.index("O_total")],
                occ, a[j, F.index("accepted_births_X")], a[j, F.index("deaths_X")])
        st = int(a[j, F.index("step")])
        if st not in by or skip_all:
            continue
        k = len([f for f in frames if f["step"] <= st]) - 1
        if k in drop:
            continue
        fr = by[st]
        if shift and k > 0:
            fr = frames[max(0, k - shift)]
        on.frame(fr)
        if fr["step"] > W["BURN_IN"]:
            seen.append(fr)
        if k in duplicate:
            on.frame(fr)
            if fr["step"] > W["BURN_IN"]:
                seen.append(fr)
    on.finish_payload(seen)
    tbl = [f for f in frames if f["step"] > W["BURN_IN"]]
    table = {"steps": [int(f["step"]) for f in tbl],
             "index_sha256": GT.frame_index_sha256([f["step"] for f in tbl]),
             "payload_sha256": GT.frame_payload_sha256(tbl)}
    agg_on = on.aggregates(mol, n3)
    agg_on["disp_over_N3"] = dispn3
    agg_ph = GT.posthoc_aggregates(sp, L, a, F, frames, mol, n3)
    agg_ph["disp_over_N3"] = dispn3
    cm = GT.compare(agg_on, agg_ph)
    tech = GT.technical_validity(sp, on.transport(), table, True, True, True, True, cm["AGREE"])
    return on, agg_on, agg_ph, cm, tech


ENV = {"r80": (5.0, 9.0), "Rg": (4.5, 7.0), "organiser_to_core": (1.0, 6.0),
       "core_fraction": (0.45, 0.85), "main_mass_fraction": (0.40, 0.85),
       "n_eff_components": (1.5, 4.5)}


def verdict(**kw):
    sp, a, fr, mol, n3, d = synth(**kw)
    on, ag_on, ag_ph, cm, tech = run_both(sp, a, fr, mol, n3, d, L=kw.get("L", 36))
    c = GT.evaluate(sp, ag_ph, ENV)
    return c, GT.classify(c), ag_ph, cm, tech


# ================================================================== frame transport
def t01_frame_transport_identity():
    _, _, _, cm, tech = verdict()
    ok = (tech["RUN_TECHNICALLY_VALID"]
          and tech["STREAM_FRAME_COUNT"] == tech["TABLE_FRAME_COUNT"] == tech["EXPECTED_FRAME_COUNT"]
          and tech["STREAM_FRAME_INDEX_SHA256"] == tech["TABLE_FRAME_INDEX_SHA256"]
          and tech["STREAM_SPATIAL_PAYLOAD_SHA256"] == tech["TABLE_SPATIAL_PAYLOAD_SHA256"]
          and cm["AGREE"])
    return chk("T01 FRAME_STREAM_TABLE_IDENTITY on a clean run: counts, index checksum and "
               "payload checksum all match", ok,
               "expected %d, stream %d, table %d" % (tech["EXPECTED_FRAME_COUNT"],
                                                     tech["STREAM_FRAME_COUNT"],
                                                     tech["TABLE_FRAME_COUNT"]))


TRANSPORT_FAULTS = [
    ("no call at all", dict(skip_all=True), "zero spatial frames received by the stream"),
    ("the last frame omitted", dict(drop=(219,)), "stream frame count"),
    ("the first eligible frame omitted", dict(drop=(40,)), "stream frame count"),
    ("a middle frame duplicated", dict(duplicate=(120,)), "duplicated frame in the stream"),
    ("the first frame duplicated", dict(duplicate=(41,)), "duplicated frame in the stream"),
    ("every call shifted by one frame", dict(shift=1), "frame index"),
]


def t02_transport_faults_are_caught():
    bad = []
    for name, kw, expect in TRANSPORT_FAULTS:
        sp, a, fr, mol, n3, d = synth()
        on, ag_on, ag_ph, cm, tech = run_both(sp, a, fr, mol, n3, d, **kw)
        caught = (not tech["RUN_TECHNICALLY_VALID"]) and \
            any(expect in r for r in tech["reasons"])
        print("        %-34s -> valid=%-5s reasons=%s"
              % (name, tech["RUN_TECHNICALLY_VALID"], tech["reasons"][:2]))
        if not caught:
            bad.append((name, tech["reasons"]))
    return chk("T02 every declared transport fault is caught by the technical layer", not bad,
               bad)


def t03_third_boundaries():
    cases = []
    for T in (9000, 9001, 8999, 3, 4, 5, 300, 1):
        n = T
        q = max(T // 3, 1)
        stream = np.array([GT.third_bucket(i, T) for i in range(n)])
        third = n // 3
        arr = np.zeros(n, int)
        arr[third:2 * third] = 1
        arr[2 * third:] = 2
        cases.append({"T": T, "match": bool(np.array_equal(stream, arr)),
                      "sizes_stream": [int((stream == b).sum()) for b in range(3)],
                      "sizes_array": [int((arr == b).sum()) for b in range(3)],
                      "first": [int(stream[0]), int(arr[0])],
                      "last": [int(stream[-1]), int(arr[-1])]})
        del q
    bad = [c for c in cases if not c["match"]]
    for c in cases:
        print("        T=%-5d match=%-5s stream %s array %s" % (c["T"], c["match"],
                                                                c["sizes_stream"],
                                                                c["sizes_array"]))
    return chk("T03 THIRD_BOUNDARY_TESTS: the streaming bucket index reproduces the array split "
               "n//3 EXACTLY, for horizons divisible and not divisible by three, down to the "
               "minimum window", not bad, bad)


def t04_online_posthoc_random():
    rng = np.random.default_rng(7)
    bad = None
    for i in range(24):
        kw = dict(N_X=int(rng.integers(20, 260)), r80=float(rng.uniform(2, 18)),
                  r80_org=float(rng.uniform(2, 18)), Rg=float(rng.uniform(2, 11)),
                  d2o=float(rng.uniform(0.5, 15)), core_fraction=float(rng.uniform(0, 1)),
                  free_org=float(rng.uniform(0, 12)), occ_frac=float(rng.uniform(0.2, 0.99)),
                  drift=float(rng.uniform(0, 0.3)), births=float(rng.uniform(0, 2)),
                  deaths=float(rng.uniform(0, 2)), winding=bool(rng.integers(0, 2)),
                  core_exists=float(rng.uniform(0, 1)), org_present=float(rng.uniform(0.5, 1)),
                  seed=100 + i)
        c, cls, ag, cm, tech = verdict(**kw)
        if not cm["AGREE"]:
            bad = {"trial": i, "diff": cm["differences"]}
            break
    return chk("T04 ONLINE_POSTHOC_SYNTHETIC_AGREEMENT on 24 random arms, with the two "
               "aggregators written independently", bad is None, bad or "")


def t05_historical_agreement():
    """The array aggregator is run against real historical series; the streaming one is fed the
    same rows one at a time. Reading stored data is not a start."""
    import glob
    bad = []
    n = 0
    for path in sorted(glob.glob("/home/claude/CSC01/raw/conf__*.npz"))[:4] + \
            sorted(glob.glob("/home/claude/ORR01/raw/conf__REPAIRED*.npz"))[:4]:
        d = np.load(path, allow_pickle=True)
        arr = d["series"]
        fl = [str(x) for x in d["fields"]]
        L = 36
        frames = [{"step": t, "N_X": int(arr[t - 1, fl.index("N_X")]), "r80": 7.0,
                   "r80_organiser": 8.0, "Rg": 5.8, "organiser_to_core": 3.0,
                   "core_fraction": 0.64, "main_mass_fraction": 0.61, "n_eff_components": 2.6,
                   "any_winding": False, "centre_y": 18, "centre_x": 18,
                   "organiser_y": 18, "organiser_x": 18}
                  for t in range(W["SAMPLE_EVERY"], len(arr) + 1, W["SAMPLE_EVERY"])]
        mol = {"replacements": 36.0, "initial_still_present": 0.0, "final_born_in_window": 1.0,
               "corr_y": 0.9, "corr_x": 0.9}
        on = GT.OnlineGate(SPEC, L, W["BURN_IN"])
        by = {f["step"]: f for f in frames}
        seen = []
        for j in range(len(arr)):
            occ = arr[j, fl.index("O_total")] / (PT["CAP"] * L * L)
            on.step(arr[j, fl.index("N_X")], arr[j, fl.index("free_at_org")],
                    arr[j, fl.index("O_total")], occ, arr[j, fl.index("accepted_births_X")],
                    arr[j, fl.index("deaths_X")])
            st = int(arr[j, fl.index("step")])
            if st in by:
                on.frame(by[st])
                if st > W["BURN_IN"]:
                    seen.append(by[st])
        on.finish_payload(seen)
        a1 = on.aggregates(mol, 8.0)
        a2 = GT.posthoc_aggregates(SPEC, L, arr, fl, frames, mol, 8.0)
        cm = GT.compare(a1, a2)
        n += 1
        if not cm["AGREE"]:
            bad.append({"file": path.split("/")[-1], "diff": cm["differences"]})
    return chk("T05 ONLINE_POSTHOC_HISTORICAL_AGREEMENT on %d stored ORR01 and CSC01 series" % n,
               not bad, bad)


def t06_8101_agreement_after_patch():
    d = np.load("/home/claude/OBTC02/verify/obtc01/wc/OBTC01/raw/P__seed8101.npz",
                allow_pickle=True)
    arr = d["series"]
    fl = [str(x) for x in d["fields"]]
    frames = [json.loads(x) for x in d["frames"]]
    res = json.load(open("/home/claude/OBTC02/verify/obtc01/wc/OBTC01/out/_results.json"))
    a0 = res["arms"][0]
    mol = a0["molecular"]
    on = GT.OnlineGate(SPEC, 36, W["BURN_IN"])
    by = {f["step"]: f for f in frames}
    seen = []
    for j in range(len(arr)):
        occ = arr[j, fl.index("O_total")] / (PT["CAP"] * 36 * 36)
        on.step(arr[j, fl.index("N_X")], arr[j, fl.index("free_at_org")],
                arr[j, fl.index("O_total")], occ, arr[j, fl.index("accepted_births_X")],
                arr[j, fl.index("deaths_X")])
        st = int(arr[j, fl.index("step")])
        if st in by:
            on.frame(by[st])
            if st > W["BURN_IN"]:
                seen.append(by[st])
    on.finish_payload(seen)
    a1 = on.aggregates(mol, a0["n3_median_displacement"])
    a2 = GT.posthoc_aggregates(SPEC, 36, arr, fl, frames, mol, a0["n3_median_displacement"])
    cm = GT.compare(a1, a2)
    tbl = [f for f in frames if f["step"] > W["BURN_IN"]]
    tech = GT.technical_validity(
        SPEC, on.transport(),
        {"steps": [int(f["step"]) for f in tbl],
         "index_sha256": GT.frame_index_sha256([f["step"] for f in tbl]),
         "payload_sha256": GT.frame_payload_sha256(tbl)},
        True, True, True, True, cm["AGREE"])
    json.dump({"reclassification": "DIAGNOSTIC_ONLY, never confirmation",
               "AGREE_after_patch": cm["AGREE"], "differences": cm["differences"],
               "technical": tech,
               "aggregates_stream": a1, "aggregates_table": a2},
              open(f"{OUT}/_8101_replay.json", "w"), indent=1, default=str)
    return chk("T06 ONLINE_POSTHOC_8101_AGREEMENT_AFTER_PATCH, on the stored raw of the burnt "
               "seed; the reclassification stays DIAGNOSTIC_ONLY",
               cm["AGREE"] and tech["RUN_TECHNICALLY_VALID"],
               "stream %d frames, table %d frames"
               % (tech["STREAM_FRAME_COUNT"], tech["TABLE_FRAME_COUNT"]))


# ================================================================== satisfiability, 12 conditions
BREAKERS = [
    ("POPULATION_STATIONARY", dict(n_min_frac=0.5)),
    ("RELATIVE_LOCALIZATION", dict(r80_org=17.0)),
    ("SOURCE_ATTACHMENT", dict(d2o=14.0, corr=0.1)),
    ("CORE_CONTINUITY", dict(core_exists=0.4, disp_over_n3=0.9)),
    ("MATERIAL_TURNOVER", dict(replacements=0.0, final_born=0.0, initial_present=1.0)),
    ("FREE_CAPACITY_PRESERVED", dict(free_org=0.1)),
    ("NO_GLOBAL_FILLING", dict(occ_frac=0.95)),
    ("NO_TRUE_WINDING", dict(winding=True)),
    ("NO_KINETIC_FREEZE", dict(births=0.0, deaths=0.0)),
    # only statistics that enter NO other condition are moved, so that exactly this one breaks
    ("MODEL_PREDICTION_COMPATIBILITY", dict(Rg=12.0, n_eff=40.0, main_fraction=0.05)),
]


def t07_joint_and_individual():
    c, cls, _, _, _ = verdict()
    joint = c["PER_ARM_PASS"] and cls == "ORGANIZER_BOUND_CLOUD_ARM_PASS"
    bad = []
    for name, kw in BREAKERS:
        c2, _, _, _, _ = verdict(**kw)
        broken = [k for k in GT.PER_ARM if not c2[k]]
        if broken != [name]:
            bad.append((name, broken))
    return chk("T07 GATE_SATISFIABILITY: one arm satisfies all ten per-arm conditions at once, "
               "and breaking each one in turn breaks exactly that one", joint and not bad,
               bad or "joint pass = %s" % joint)


def _fake_arm(cond, L, r80, seed=0, e_fold=None, resid=None, nx_final=0.0):
    return {"tag": "%s/seed%d" % (cond, seed), "condition": cond, "L": L,
            "aggregates": {"model": {"r80": r80}},
            "source_off": ({} if e_fold is None else
                           {"e_folding_steps": e_fold, "residual_after_5_e_foldings": resid}),
            "N_X": {"max": 100.0, "final": nx_final}}


def t08_cross_arm_conditions():
    tau = ANALYTIC["source_off"]["e_folding_steps"]
    good = ([_fake_arm("P", 36, 7.0, i) for i in range(6)]
            + [_fake_arm("D", 72, 7.1, i) for i in range(3)]
            + [_fake_arm("R", 36, 7.0, i, e_fold=tau, resid=0.005) for i in range(3)]
            + [_fake_arm("N", 36, float("nan"), i, nx_final=0.0) for i in range(2)])
    ok = GT.cross_arm(SPEC, good, ANALYTIC)
    bad_dom = ([_fake_arm("P", 36, 7.0, i) for i in range(6)]
               + [_fake_arm("D", 72, 14.0, i) for i in range(3)]
               + [_fake_arm("R", 36, 7.0, i, e_fold=tau, resid=0.005) for i in range(3)]
               + [_fake_arm("N", 36, float("nan"), i, nx_final=0.0) for i in range(2)])
    kd = GT.cross_arm(SPEC, bad_dom, ANALYTIC)
    bad_cau = ([_fake_arm("P", 36, 7.0, i) for i in range(6)]
               + [_fake_arm("D", 72, 7.1, i) for i in range(3)]
               + [_fake_arm("R", 36, 7.0, i, e_fold=5.0, resid=0.9) for i in range(3)]
               + [_fake_arm("N", 36, float("nan"), i, nx_final=90.0) for i in range(2)])
    kc = GT.cross_arm(SPEC, bad_cau, ANALYTIC)
    res = (ok["CROSS_ARM_PASS"]
           and (not kd["DOMAIN_SIZE_INVARIANCE"]["PASS"]) and kd["CAUSAL_SOURCE_DEPENDENCE"]["PASS"]
           and kc["DOMAIN_SIZE_INVARIANCE"]["PASS"] and (not kc["CAUSAL_SOURCE_DEPENDENCE"]["PASS"]))
    print("        good arms   -> domain %s causal %s" % (ok["DOMAIN_SIZE_INVARIANCE"]["PASS"],
                                                          ok["CAUSAL_SOURCE_DEPENDENCE"]["PASS"]))
    print("        r80 doubles -> domain %s causal %s" % (kd["DOMAIN_SIZE_INVARIANCE"]["PASS"],
                                                          kd["CAUSAL_SOURCE_DEPENDENCE"]["PASS"]))
    print("        no decay    -> domain %s causal %s" % (kc["DOMAIN_SIZE_INVARIANCE"]["PASS"],
                                                          kc["CAUSAL_SOURCE_DEPENDENCE"]["PASS"]))
    return chk("T08 the two CROSS-ARM conditions each pass on a good set and each fail alone "
               "when broken", res)


def t09_thresholds_only_in_the_yaml():
    moved = []
    for path, val in ((("gate", "MATERIAL_TURNOVER", "replacements_min"), 1e9),
                      (("gate", "RELATIVE_LOCALIZATION", "absolute_bound"), 0.1),
                      (("gate", "SOURCE_ATTACHMENT", "median_core_to_organiser_max"), 0.01),
                      (("gate", "NO_GLOBAL_FILLING", "mean_occupancy_fraction_max"), 0.0),
                      (("gate", "CORE_CONTINUITY", "core_exists_fraction_min"), 1.01)):
        s2 = copy.deepcopy(SPEC)
        d = s2
        for k in path[:-1]:
            d = d[k]
        d[path[-1]] = val
        c, _, _, _, _ = verdict(spec=s2)
        moved.append(not c["PER_ARM_PASS"])
    return chk("T09 moving any threshold in the yaml moves the verdict", all(moved), str(moved))


def t10_engine_unchanged():
    GD.set_test_mode()
    hs = []
    for cls in (V2.WorldV2, EN.WorldOBTC):
        sp = PC.spec_for()
        kw = dict(lawspec=V2.LAWSPEC_V2_EXCHANGE, rng_mode="split_feed_stream",
                  exchangeable=V2.EXCHANGEABLE_DEFAULT, insert_mode="reservoir")
        w = cls(L=None, seed=161616, sp=sp, **kw)
        w.n["SX"][:] = sp.S0; w.n["SY"][:] = sp.S0
        c = w.L // 2; w.n["Y"][c, c] = 1; w.n["X"][c, c] = PT["X_SEED"]
        GD.advance(w, 1200)
        hs.append(w.state_hash())
    GD.set_static_mode()
    return chk("T10 the engine is still state-for-state the frozen engine", hs[0] == hs[1],
               "%s vs %s" % (hs[0][:16], hs[1][:16]))


def t11_winding_and_metrics_unchanged():
    L = 36
    ok = True
    m = np.zeros((L, L), bool); m[7, :] = True
    lab, _ = M.components(m)
    ok &= TOP.classify_component(m, lab, 0)["kind"] == "WINDING_HORIZONTAL"
    m = np.zeros((L, L), bool); m[np.ix_([34, 35, 0, 1], [34, 35, 0, 1])] = True
    lab, _ = M.components(m)
    ok &= TOP.classify_component(m, lab, 0)["kind"] == "CROSSES_THE_GRAPHICAL_SEAM_ONLY"
    src = open("/home/claude/OBTC02/code/gate_obtc02.py").read()
    ok &= "legacy" not in src.lower()
    return chk("T11 the topological winding test is unchanged and LEGACY_EXTENT_PROXY enters no "
               "gate condition", ok)


CASES = [t01_frame_transport_identity, t02_transport_faults_are_caught, t03_third_boundaries,
         t04_online_posthoc_random, t05_historical_agreement, t06_8101_agreement_after_patch,
         t07_joint_and_individual, t08_cross_arm_conditions, t09_thresholds_only_in_the_yaml,
         t10_engine_unchanged, t11_winding_and_metrics_unchanged]


def main():
    GD.set_static_mode()
    for c in CASES:
        c()
    allp = all(r["PASS"] for r in R)
    g = lambda p: next(r["PASS"] for r in R if r["case"].startswith(p))
    out = {"cases": R, "n_cases": len(R),
           "FRAME_STREAM_TABLE_IDENTITY": "PASS" if (g("T01") and g("T02")) else "FAIL",
           "THIRD_BOUNDARY_TESTS": "PASS" if g("T03") else "FAIL",
           "ONLINE_POSTHOC_SYNTHETIC_AGREEMENT": "PASS" if g("T04") else "FAIL",
           "ONLINE_POSTHOC_HISTORICAL_AGREEMENT": "PASS" if g("T05") else "FAIL",
           "ONLINE_POSTHOC_8101_AGREEMENT_AFTER_PATCH": "PASS" if g("T06") else "FAIL",
           "GATE_SATISFIABILITY": "PASS" if (g("T07") and g("T08")) else "FAIL",
           "PROTOCOL_ADVERSARIAL_AUDIT": "PASS" if allp else "FAIL",
           "grouping_convention": (
               "OBTC01 declared twelve gate conditions: ten evaluated PER ARM and two evaluated "
               "ACROSS ARMS, because a single arm cannot exhibit either domain-size invariance "
               "or the response to removing the source. T07 certifies the ten; T08 certifies "
               "the two."),
           "spec_sha256": GT.spec_sha256(), "ledger": GD.audit()}
    json.dump(out, open(f"{OUT}/_audit.json", "w"), indent=1, default=str)
    print()
    for k in ("FRAME_STREAM_TABLE_IDENTITY", "THIRD_BOUNDARY_TESTS",
              "ONLINE_POSTHOC_SYNTHETIC_AGREEMENT", "ONLINE_POSTHOC_HISTORICAL_AGREEMENT",
              "ONLINE_POSTHOC_8101_AGREEMENT_AFTER_PATCH", "GATE_SATISFIABILITY",
              "PROTOCOL_ADVERSARIAL_AUDIT"):
        print("%-46s = %s" % (k, out[k]))
    print("SCIENTIFIC_RUNS_USED %d" % GD.scientific_runs_used())
    return 0 if allp else 1


if __name__ == "__main__":
    sys.exit(main())
