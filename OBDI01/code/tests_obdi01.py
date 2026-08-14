"""OBDI01 — instrument tests. Run in TEST mode, which consumes no start from the ledger.

The decisive ones are T1 (the passive observer cannot change the process) and T5 (the frozen
acceptance region can be both passed and failed — a gate that cannot fail proves nothing).
"""
from __future__ import annotations

import json
import sys

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/OBDI01/code")

import lawspec_v2 as V2            # noqa: E402
import observe as OBS              # noqa: E402

import engine_obtc as EN           # noqa: E402
import gate_obdi01 as GT           # noqa: E402
import gate_obtc02 as G2           # noqa: E402
import guard_obtc as GD            # noqa: E402
import metrics_obtc as M           # noqa: E402
import protocol_obdi01 as PR       # noqa: E402
import protocol_obtc02 as PC       # noqa: E402

OUT = "/home/claude/OBDI01/out"
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append({"test": name, "PASS": bool(ok), "detail": str(detail)})
    print("  %-52s %s   %s" % (name, "PASS" if ok else "FAIL", detail))
    return bool(ok)


# ------------------------------------------------------------------ T1 observer inertness
def short_world(seed, L, steps, observe):
    rec = OBS.Recorder()
    sp = PC.spec_for(L)
    w = EN.fresh_world(seed, sp, lawspec=V2.LAWSPEC_V2_EXCHANGE, rng_mode="split_feed_stream",
                       exchangeable=V2.EXCHANGEABLE_DEFAULT, insert_mode="reservoir", rec=rec,
                       track=True, organiser_off_at=None)
    EN.seed_one_organiser(w, PC.PT["X_SEED"])
    frames = []

    def per_step(ww):
        if ww.step % 50:
            return
        fr, _ = M.frame(ww.n["X"], ww.n["Y"], 3.0)
        fr["step"] = int(ww.step)
        fr["r80_organiser"] = (M.radii(ww.n["X"], fr["organiser_y"], fr["organiser_x"])[0.8]
                               if (fr["organiser_y"] >= 0 and fr["N_X"] > 0) else float("nan"))
        frames.append(fr)

    if observe:
        PR.install_observer(list(range(16)))
        PR.reset_observer()
    else:
        PR.remove_observer()
    GD.advance(w, steps, per_step=per_step)
    PR.remove_observer()
    return (w.state_hash(), G2.frame_payload_sha256(frames), len(frames),
            int(w.n["X"].sum()), len(PR._ACC["rows"]) if observe else 0)


def t1():
    a = short_world(4242, 36, 600, observe=False)
    b = short_world(4242, 36, 600, observe=True)
    check("T1a observer leaves the engine state hash identical", a[0] == b[0],
          "%s vs %s" % (a[0][:16], b[0][:16]))
    check("T1b observer leaves the frame payload checksum identical", a[1] == b[1],
          "%s vs %s" % (a[1][:16], b[1][:16]))
    check("T1c observer leaves the population identical", a[3] == b[3], "%d vs %d" % (a[3], b[3]))
    check("T1d observer saw exactly one row per frame", b[4] == b[2],
          "%d rows, %d frames" % (b[4], b[2]))


# ------------------------------------------------------------------ T2-T4 measurement algebra
def t2():
    rng = np.random.default_rng(7)
    L, edges = 24, list(range(16))
    f = rng.integers(0, 3, (L, L))
    oy, ox = 5, 19
    h = GT.empirical_radial(f, oy, ox, edges)
    # brute force
    tot = np.zeros(len(edges))
    for y in range(L):
        for x in range(L):
            dy = min(abs(y - oy), L - abs(y - oy))
            dx = min(abs(x - ox), L - abs(x - ox))
            d = np.hypot(dy, dx)
            b = min(int(np.searchsorted(edges, d, side="right") - 1), len(edges) - 1)
            tot[max(b, 0)] += f[y, x]
    tot = tot / tot.sum()
    check("T2a empirical radial matches a brute-force recomputation",
          np.allclose(h, tot), "max |diff| = %.3e" % np.abs(h - tot).max())
    check("T2b empirical radial is a probability vector", abs(h.sum() - 1) < 1e-12)


def t3():
    import source_operator as OP
    op = OP.Op(PC.spec_for(36))
    p = GT.predicted_radial(op.relative_profile(36), list(range(16)))
    check("T3a predicted radial is a probability vector", abs(p.sum() - 1) < 1e-12)
    check("T3b total variation of a distribution with itself is zero",
          GT.total_variation(p, p) == 0.0)
    q = p.copy()
    q[0] += 0.10
    q[-1] = max(q[-1] - 0.10, 0.0)
    check("T3c total variation is the half L1 distance",
          abs(GT.total_variation(p, q) - 0.5 * np.abs(p - q).sum()) < 1e-15)


def t4():
    x = np.log([36.0, 72.0, 96.0])
    for true_b in (0.0, 0.5, 1.0, -2.0):
        y = true_b * x + 1.234
        b, se = GT.wls_slope(x, y, np.ones(3))
        if not check("T4 wls slope recovers %+0.1f exactly" % true_b, abs(b - true_b) < 1e-10,
                     "beta = %+.12f  se = %.4f" % (b, se)):
            return


# ------------------------------------------------------------------ T5 gate satisfiability
def synth(spec, alpha, dens_exp, wind_frac, tv_mult, n=5, jitter=0.0, seed=1):
    """Arm summaries manufactured under a chosen scaling law, to check that the frozen region
    accepts H_bound and rejects each unbounded alternative."""
    rng = np.random.default_rng(seed)
    sizes = [int(x) for x in spec["domain"]["SIZES"]]
    pred = spec["predictions"]
    env = spec["principal_outcome"]["components"]["D_profile_compatibility"]["envelope_by_L"]
    by_L = {}
    for L in sizes:
        vals = {}
        for s in GT.SHAPE_STATS:
            base = float(pred[str(L)][s])
            if alpha != 0.0:                     # an alternative ignores the finite-size shape
                base = float(pred[str(sizes[0])][s]) * (L / sizes[0]) ** alpha
            vals[s] = list(base * (1.0 + jitter * rng.standard_normal(n)))
        N0 = float(pred[str(sizes[0])]["N_X"])
        NX = N0 * (L / sizes[0]) ** (dens_exp + 2.0)
        by_L[L] = {"values": vals,
                   "density": list((NX / L ** 2) * (1.0 + jitter * rng.standard_normal(n))),
                   "winding": (int(round(wind_frac * n * 180)), n * 180),
                   "profile_TV": [tv_mult * float(env[str(L)]["quantile_value"])] * n}
    return by_L


def t5():
    spec = GT.load()
    cases = [
        ("H_bound", dict(alpha=0.0, dens_exp=-2.0, wind_frac=0.0, tv_mult=0.5), True),
        ("H_linear", dict(alpha=1.0, dens_exp=0.0, wind_frac=0.5, tv_mult=3.0), False),
        ("H_sublinear", dict(alpha=0.5, dens_exp=-1.0, wind_frac=0.0, tv_mult=2.0), False),
        ("H_fill", dict(alpha=1.0, dens_exp=0.0, wind_frac=0.9, tv_mult=5.0), False),
    ]
    for name, kw, expect in cases:
        r = GT.evaluate_principal(spec, synth(spec, jitter=0.01, seed=hash(name) % 9999, **kw))
        got = r["DOMAIN_INVARIANCE_REGION_PASS"]
        check("T5 the region %-12s -> %s" % (name, "PASS" if expect else "FAIL"), got == expect,
              "A=%s B=%s C=%s D=%s" % (r["components"]["A_shape_invariance"]["PASS"],
                                       r["components"]["B_density_exponent"]["PASS"],
                                       r["components"]["C_no_true_winding"]["PASS"],
                                       r["components"]["D_profile_compatibility"]["PASS"]))
    # each component must be individually breakable, or it is decorative
    base = dict(alpha=0.0, dens_exp=-2.0, wind_frac=0.0, tv_mult=0.5)
    for comp, kw in (("A_shape_invariance", dict(base, alpha=0.6)),
                     ("B_density_exponent", dict(base, dens_exp=-1.0)),
                     ("C_no_true_winding", dict(base, wind_frac=0.2)),
                     ("D_profile_compatibility", dict(base, tv_mult=1.5))):
        r = GT.evaluate_principal(spec, synth(spec, jitter=0.01, seed=11, **kw))
        broke = not r["components"][comp]["PASS"]
        check("T5 component %-24s can be broken alone" % comp, broke,
              "region PASS = %s" % r["DOMAIN_INVARIANCE_REGION_PASS"])


# ------------------------------------------------------------------ T6 multiplicity
def t6():
    import math
    spec = GT.load()
    m = spec["principal_outcome"]["multiplicity"]
    c, per, K, af = (float(m["critical_value_c"]), float(m["per_test_alpha"]), int(m["K"]),
                     float(m["family_alpha"]))
    two_sided = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(c / math.sqrt(2.0))))
    check("T6a the critical value matches the per-test level", abs(two_sided - per) < 1e-9,
          "%.9f vs %.9f" % (two_sided, per))
    check("T6b the Sidak level reproduces the family level",
          abs((1.0 - (1.0 - per) ** K) - af) < 1e-12, "K = %d" % K)


# ------------------------------------------------------------------ T7 the secondary endpoint
def t7():
    spec = GT.load()
    raws = "/home/claude/OBDI01/verify/obtc02/wc/OBTC02/raw"
    expected = {"D/seed9501": True, "D/seed9502": False, "D/seed9503": False}
    frac_expected = {"D/seed9501": 1.0, "D/seed9502": 168 / 180, "D/seed9503": 168 / 180}
    arms = []
    for tag in expected:
        z = np.load("%s/%s.npz" % (raws, tag.replace("/", "__")), allow_pickle=True)
        fr = [json.loads(s) for s in z["frames"] if json.loads(s)["step"] > 2000]
        arms.append({"tag": tag, "L": 72,
                     "r80_organiser_frames": [f["r80_organiser"] for f in fr]})
    r = GT.evaluate_secondary(spec, arms)
    ok = all(row["PASS"] == expected[row["tag"]] for row in r["per_arm"])
    okf = all(abs(row["fraction"] - frac_expected[row["tag"]]) < 1e-12 for row in r["per_arm"])
    check("T7a the secondary endpoint reproduces OBTC02's verdicts", ok,
          str({row["tag"]: row["PASS"] for row in r["per_arm"]}))
    check("T7b it reproduces OBTC02's exact fractions", okf,
          str({row["tag"]: round(row["fraction"], 4) for row in r["per_arm"]}))


def main():
    GD.set_test_mode()
    print("OBDI01 instrument tests (TEST mode: no start is opened, no ledger entry is made)")
    for f in (t1, t2, t3, t4, t5, t6, t7):
        f()
    n = sum(1 for r in RESULTS if r["PASS"])
    json.dump({"SECTION": "OBDI01 instrument tests", "results": RESULTS,
               "passed": n, "total": len(RESULTS),
               "ALL_PASS": bool(n == len(RESULTS)),
               "ledger_untouched": GD.audit()["total"] == 0,
               "mode": GD.mode()},
              open(f"{OUT}/_tests.json", "w"), indent=1, default=str)
    print("\n%d/%d passed   ledger entries made: %d" % (n, len(RESULTS), GD.audit()["total"]))
    if n != len(RESULTS):
        sys.exit(1)


if __name__ == "__main__":
    main()
