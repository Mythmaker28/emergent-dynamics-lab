"""EXP-GT-CONTINUOUS-FINGERPRINT-01 -- CONTROLS T1..T10. Development data only."""
from __future__ import annotations
import json, math, os
import numpy as np
from ..identity import cfingerprint as F0, cfingerprint01 as F1
from ..substrates.ctrans import manifests01 as M
from .exp_gt_cfp01 import cached, channel, OUT, SAFETY, SEP_FACTOR, NONNULL

def main():
    dev = M.dev_systems(); idx = {n: i for i, n in enumerate(dev)}
    def A(nm, arm="limited", k=0):
        return cached(dev[nm], arm, M.DEV_SEED_BASE + (0 if arm == "limited" else 5_000_000)
                      + 3000 * idx[nm] + 1500 * k, "d_%s_%s_%d" % (nm, arm, k))
    nn = [n for n in dev if n not in NONNULL]
    ns = [F1.distance_bracket(A(n, "limited", 0), A(n, "limited", 1))["d_obs"] for n in nn]
    q = float(np.quantile([x for x in ns if np.isfinite(x)], 0.999))
    rc, rs = SAFETY * q, SEP_FACTOR * SAFETY * q
    out, rows = [], []

    def rec(cid, what, expect, obs, ok, note=""):
        rows.append({"id": cid, "breaks": what, "expected": expect, "observed": obs, "PASS": bool(ok),
                     "note": note})
        print("  %-4s %-44s %-46s %s" % (cid, what, obs, "PASS" if ok else "** FAIL **"))

    print("CONTROLS T1..T10   (r_cont=%.2f  r_sep=%.2f)" % (rc, rs))

    # T1 -- the burned case must classify BY BOUND, never by exception
    r = F1.compare(A("R_leak_burned"), A("R_cascade_burned", k=1), rc, rs)
    rec("T1", "burned case (P_cascade) as regression",
        "classified ONLY if the bound proves it",
        "%s  D_lo=%.1f >= r_sep=%.1f  tail=%s" % (r["verdict"], r["D_lo"], rs, r["tail_status"]),
        r["verdict"] == F1.DIFFERENT and r["D_lo"] >= rs,
        "v00 measured 64.15 vs radius 23.36 and abstained. v01 classifies it because D_lo proves the verdict "
        "cannot change -- no hard-coded exception exists anywhere in the guard.")

    # T2 -- genuinely unresolved: never settles
    r = F1.compare(A("V_nonsettle"), A("V_leak", k=1), rc, rs)
    rec("T2", "genuinely in-flight (never settles)", "must ABSTAIN",
        "%s  tail=%s" % (r["verdict"], r["tail_status"]), r["verdict"] == F1.INDETERMINATE)

    # T3 -- slow but harmless
    r = F1.compare(A("V_multi_strong"), A("V_multi_strong_g2", k=1), rc, rs)
    rec("T3", "slow tail, remainder cannot cross boundary", "must CLASSIFY",
        "%s  bracket [%.1f, %.1f]  tail=%s" % (r["verdict"], r["D_lo"], r["D_hi"], r["tail_status"]),
        r["verdict"] == F1.DIFFERENT and r["tail_status"] == F1.SLOW_TAIL)

    # T4 -- slow tail near the boundary
    r = F1.compare(A("V_multi_strong"), A("V_multi_tailonly", k=1), rc, rs)
    rec("T4", "slow tail NEAR the boundary", "must ABSTAIN",
        "%s  bracket [%.1f, %.1f]  tail=%s" % (r["verdict"], r["D_lo"], r["D_hi"], r["tail_status"]),
        r["verdict"] == F1.INDETERMINATE,
        "THE DECISIVE CONTROL, AND IT FAILS. The remainder is real (~10% of the difference energy lies beyond "
        "the window, per the privileged path) but its envelope measures 8.25 against a bound noise floor of 9.0. "
        "The bound cannot see it, calls the tail SETTLED, and returns a confident DIFFERENT.")

    # T5 -- the delayed-second-component trap
    a, b = A("V_delayed2"), A("V_delayed2_w", k=1)
    br = F1.distance_bracket(a, b)
    top = max(br["blocks"], key=lambda x: x["d"])
    d = a["Z"][top["probe"], top["phase"]] - br["lam"] * b["Z"][top["probe"], (top["phase"] + br["shift"]) % 4]
    naive_says_settled = F1.naive_derivative_settled(d, t_stop=45)     # stop in the PLATEAU, before D_MAX
    r = F1.compare(a, b, rc, rs)
    rec("T5", "misleading flat tail (2nd cause at delay 55)",
        "naive derivative guard FAILS; frozen guard does not",
        "naive(stop@45)=SETTLED:%s  frozen=%s" % (naive_says_settled, r["verdict"]),
        naive_says_settled and r["verdict"] == F1.DIFFERENT,
        "The naive guard stops in the plateau and never hears the second cause. The frozen guard refuses to "
        "assess settling before the declared delay horizon T_TAIL0 = %d." % F1.T_TAIL0)

    # T6 -- noise and drift are not unresolved response
    r1 = F1.compare(A("V_leak"), A("V_leak", k=1), rc, rs)
    r2 = F1.compare(A("V_drifty"), A("V_leak", k=1), rc, rs)
    rec("T6", "noise/drift must not read as in-flight",
        "null SETTLED+INDIST; drift refused as nonstationary",
        "null=%s/%s ; drifty=%s" % (r1["verdict"][:16], r1["tail_status"], r2["verdict"]),
        r1["verdict"] == F1.INDIST and r1["tail_status"] == F1.SETTLED and r2["verdict"] == F1.INDETERMINATE)

    # T7 -- window-extension invariance
    flips = 0
    for nm in ("V_leak_gain2", "V_cascade2", "V_underdamped", "V_multi_weak_g2", "V_delayed"):
        base = F1.compare(A("V_leak"), A(nm, k=1), rc, rs)["verdict"]
        for w in (120, 140):
            aa = F0.acquire(channel(dev["V_leak"]), "limited", M.DEV_SEED_BASE + 99000, w_resp=w)
            bb = F0.acquire(channel(dev[nm]), "limited", M.DEV_SEED_BASE + 99500, w_resp=w)
            v = F1.compare(aa, bb, rc, rs, t_tail0=min(F1.T_TAIL0, w - 30))["verdict"]
            if v != F1.INDETERMINATE and v != base:
                flips += 1
    rec("T7", "verdict stable under window change", "no classified verdict reverses",
        "%d reversals over 5 pairs x 2 windows" % flips, flips == 0)

    # T8 -- short window must increase abstention
    n_full = n_short = 0
    for nm in ("V_cascade2", "V_multi_strong", "V_multi_weak", "V_delayed", "V_underdamped"):
        if F1.compare(A("V_leak"), A(nm, k=1), rc, rs)["verdict"] == F1.INDETERMINATE:
            n_full += 1
        aa = F0.acquire(channel(dev["V_leak"]), "limited", M.DEV_SEED_BASE + 97000, w_resp=110)
        bb = F0.acquire(channel(dev[nm]), "limited", M.DEV_SEED_BASE + 97500, w_resp=110)
        if F1.compare(aa, bb, rc, rs, t_tail0=80)["verdict"] == F1.INDETERMINATE:
            n_short += 1
    rec("T8", "artificially short window", "INDETERMINATEs must increase",
        "abstentions: %d (W=160) -> %d (W=110)" % (n_full, n_short), n_short > n_full)

    # T9 -- remove the guard entirely: a premature verdict must appear
    r_no = F1.compare(A("V_multi_strong"), A("V_multi_tailonly", k=1), rc, rs, guard="none")
    r_oos = F1.compare(A("V_slow_oos"), A("V_leak", k=1), rc, rs, guard="none")
    rn = F1.compare(A("V_nonsettle"), A("V_leak", k=1), rc, rs, guard="none")
    rec("T9", "guard REMOVED", "a premature/false verdict must appear",
        "nonsettling -> %s (guard on: INDETERMINATE)" % rn["verdict"], rn["verdict"] != F1.INDETERMINATE,
        "With no guard the instrument hands a confident verdict to a system whose response never settles.")

    # T10 -- restore version 00's guard: an unnecessary abstention must reappear
    z = A("R_cascade_burned")["Z"]
    v00_flags = sum(F1.v00_guard_in_flight(z[i, k]) for i in range(z.shape[0]) for k in range(z.shape[1]))
    frac = v00_flags / max(sum(np.abs(z[i, k]).max() >= F0.Z_DET for i in range(z.shape[0])
                               for k in range(z.shape[1])), 1)
    r01 = F1.compare(A("R_leak_burned"), A("R_cascade_burned", k=1), rc, rs)
    rec("T10", "version 00's guard restored", "an unnecessary abstention reappears",
        "v00 flags %d rows in flight (frac %.2f > %.2f) -> v00 ABSTAINS; v01 says %s"
        % (v00_flags, frac, F0.IN_FLIGHT_MAX, r01["verdict"]),
        frac > F0.IN_FLIGHT_MAX and r01["verdict"] == F1.DIFFERENT,
        "The burned case, exactly as v00 saw it.")

    npass = sum(r["PASS"] for r in rows)
    print("  CONTROLS: %d / %d" % (npass, len(rows)))
    json.dump({"radii": {"r_continuity": rc, "r_separation": rs}, "controls": rows,
               "passed": npass, "total": len(rows)},
              open(os.path.join(OUT, "controls.json"), "w"), indent=1, default=float)
    return rows


if __name__ == "__main__":
    main()
