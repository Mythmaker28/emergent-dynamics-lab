"""EXP-GT-CONTINUOUS-FINGERPRINT-01 -- DEVELOPMENT. Development data only."""
from __future__ import annotations
import json, math, os, sys, time
import numpy as np
from ..identity import cfingerprint as F0, cfingerprint01 as F1
from ..substrates.ctrans import engine as E, evaluator as V, manifests01 as M

OUT = os.path.join("results", "EXP-GT-CFP01-DEV")
CACHE = os.path.join("results", "_cfp01_cache2")   # V_slow_oos was re-parameterised and the cache is
#                                                     NAME-keyed, so the old entries are stale. Same provenance
#                                                     hazard as the stale .pyc: a cache that can answer a question
#                                                     it was never asked is not a cache, it is a bug.
SAFETY, SEP_FACTOR = 2.0, 3.0          # SAME predeclared rule as v00. Calibrated on the NULL alone.
NONNULL = ("V_silent_dead", "V_silent_sat", "V_noisy", "V_drifty", "V_lowcov", "V_nonsettle", "V_slow_oos")


def channel(spec):
    def measure(probes, T, seeds):
        ok = np.array([p.target not in spec.blocked for p in probes])
        u = np.full((len(probes), T), np.nan)
        idx = [i for i, o in enumerate(ok) if o]
        if idx:
            sub = E.simulate(spec, [probes[i] for i in idx], T, np.asarray(seeds)[idx])["u"]
            for j, i in enumerate(idx):
                u[i] = sub[j]
        return u, ok
    return measure


def cached(spec, arm, seed0, key, cache=CACHE, **kw):
    os.makedirs(cache, exist_ok=True)
    fp = os.path.join(cache, key + ".npz")
    if os.path.exists(fp):
        z = np.load(fp, allow_pickle=True)
        return {k: (z[k].item() if z[k].ndim == 0 else z[k]) for k in z.files}
    a = F0.acquire(channel(spec), arm, seed0, **kw)
    np.savez_compressed(fp, **{k: np.asarray(v, dtype=object) if k == "probes" else np.asarray(v)
                               for k, v in a.items()})
    return a


def say(*a):
    print(*a); sys.stdout.flush()


def agree(c, arm, pv):
    """Construction truth vs the PRIVILEGED path. The privileged evaluator never imports the instrument."""
    v = pv["verdict"]
    if c.category in (M.CONTINUITY, M.FALSE_DIFFERENCE):
        return v == (V.PRIV_EQUIVALENT if c.expect[arm] == M.INDIST else V.PRIV_DIFFERENT)
    if c.category == M.DIFFERENCE:
        return v == V.PRIV_DIFFERENT
    if c.category == M.FALSE_SAMENESS:
        return v == (V.PRIV_EQUIVALENT if arm == "limited" else V.PRIV_DIFFERENT)
    if c.category == M.ABSTAIN:
        L, R = pv["left"], pv["right"]
        if "silent" in c.tags:        return v == V.PRIV_SILENT
        if "noise" in c.tags:         return L["unreadable"] or R["unreadable"]
        if "drift" in c.tags:         return L["nonstationary"] or R["nonstationary"]
        if "coverage" in c.tags:      return bool(L["blocked"]) != bool(R["blocked"])
        if "contract" in c.tags:      return not c.common_channel
        if "out_of_contract" in c.tags or "nonsettling" in c.tags:
            # WORLD-LEVEL: the response genuinely outruns the declared contract. Verified from the noise-free
            # trace, with no reference to the instrument's guard.
            return _tail_truth(c.left)["out_of_contract"]
        if "near_boundary" in c.tags:
            # WORLD-LEVEL: the two systems ARE different, and a MATERIAL share of that difference lies BEYOND the
            # window. Both are properties of the world, computed noise-free, independent of the instrument.
            t = _pair_tail_truth(c.left, c.right)
            return (v == V.PRIV_DIFFERENT) and t["frac_beyond_window"] > 0.02
    return False


_TT = {}


def _resp(name, T=1400):
    s = M.dev_systems()[name]
    p = [E.Probe("b", -1, "none", 0, 0, 10 ** 9), E.Probe("s", E.DRIVE, "step", F0.A_LARGE, F0.D_HOLD, 128)]
    y = E.observe_noise_free(s, p, T)
    return (y[1] - y[0])[128:], s


def _tail_truth(name):
    if name in _TT: return _TT[name]
    r, s = _resp(name)
    W = F0.W_RESP
    e = r - r[-50:].mean()
    Ein, Eout = float((e[:W] ** 2).sum()), float((e[W:] ** 2).sum())
    # implied slowest relaxation, measured on the noise-free trace over the LAST decade of the tail
    a, b = float(np.sqrt((e[W // 2:W] ** 2).mean())), float(np.sqrt((e[W:W + W // 2] ** 2).mean()))
    tau = (W / 2) / math.log(a / b) if (a > b > 0) else float("inf")
    out = {"frac_beyond_window": Eout / max(Ein + Eout, 1e-30), "tau_true": tau,
           "out_of_contract": (not np.isfinite(tau)) or tau > M.TAU_MAX}
    _TT[name] = out
    return out


def _pair_tail_truth(a, b):
    ra, _ = _resp(a); rb, _ = _resp(b)
    d = ra - rb; W = F0.W_RESP
    return {"frac_beyond_window": float((d[W:] ** 2).sum() / max((d ** 2).sum(), 1e-30))}


def main():
    t0 = time.time(); os.makedirs(OUT, exist_ok=True)
    dev = M.dev_systems(); idx = {n: i for i, n in enumerate(dev)}
    acq = {}
    for arm in ("limited", "rich"):
        b = 0 if arm == "limited" else 5_000_000
        for nm, s in dev.items():
            for k in (0, 1):
                acq[(nm, arm, k)] = cached(s, arm, M.DEV_SEED_BASE + b + 3000 * idx[nm] + 1500 * k,
                                           "d_%s_%s_%d" % (nm, arm, k))
    say("acquisitions: %d (%.0fs)" % (len(acq), time.time() - t0))
    log = {"protocol": "EXP-GT-CONTINUOUS-FINGERPRINT-01", "phase": "DEVELOPMENT",
           "contract": {"TAU_MAX": M.TAU_MAX, "D_MAX": M.D_MAX, "L_MAX": F1.L_MAX, "T_TAIL0": F1.T_TAIL0,
                        "LVL_K": F1.LVL_K, "RIP_K": F1.RIP_K, "BOUND_K": F1.BOUND_K,
                        "TAIL_NOISE": F1.TAIL_NOISE},
           "SAFETY": SAFETY, "SEP_FACTOR": SEP_FACTOR}

    # ---------- TAIL_NOISE calibration: NOISE-ONLY blocks. No label is consulted.
    Bs, nfl = [], 0
    for nm in ("V_silent_dead", "V_silent_sat", "V_leak"):
        for arm in ("limited", "rich"):
            ZA, ZB = acq[(nm, arm, 0)]["Z"], acq[(nm, arm, 1)]["Z"]
            for i in range(ZA.shape[0]):
                for j in range(ZA.shape[1]):
                    tb = F1.tail_bound(ZA[i, j] - ZB[i, j])
                    if tb["status"] == F1.IN_FLIGHT:
                        nfl += 1
                    else:
                        Bs.append(tb.get("B", 0.0))
    Bs = np.array(Bs)
    say("")
    say("TAIL calibration on NOISE-ONLY BLOCKS -- the bound's OWN output on blocks that cannot contain a signal.")
    say("  %d blocks; falsely UNBOUNDED: %d (must be 0)" % (len(Bs) + nfl, nfl))
    say("  remaining envelope B: mean=%.2f q99.9=%.2f MAX=%.2f  -> frozen TAIL_NOISE=%.1f (1.2x the max)"
        % (Bs.mean(), np.quantile(Bs, .999), Bs.max(), F1.TAIL_NOISE))
    say("  frozen bars: LVL_K=%.1f RIP_K=%.1f (out-of-contract checks) ; BOUND_K=%.1f (the remainder bound)"
        % (F1.LVL_K, F1.RIP_K, F1.BOUND_K))
    log["tail_noise_calibration"] = {"n_blocks": int(len(Bs) + nfl), "false_unbounded": int(nfl),
                                     "B_mean": float(Bs.mean()), "B_q999": float(np.quantile(Bs, .999)),
                                     "B_max": float(Bs.max()), "TAIL_NOISE": F1.TAIL_NOISE}

    # ---------- radii from the NULL alone
    nn = [n for n in dev if n not in NONNULL]
    rad = {}
    for arm in ("limited", "rich"):
        ns = [F1.distance_bracket(acq[(n, arm, 0)], acq[(n, arm, 1)])["d_obs"] for n in nn]
        ns = [x for x in ns if np.isfinite(x)]
        q = float(np.quantile(ns, 0.999))
        rad[arm] = {"n": len(ns), "mean": float(np.mean(ns)), "max": float(np.max(ns)), "q999": q,
                    "r_continuity": SAFETY * q, "r_separation": SEP_FACTOR * SAFETY * q}
        say("  %-8s null n=%2d mean=%.3f max=%.3f q99.9=%.3f -> r_cont=%.3f r_sep=%.3f"
            % (arm, len(ns), np.mean(ns), np.max(ns), q, SAFETY * q, SEP_FACTOR * SAFETY * q))
    log["null_calibration"] = rad

    # ---------- challenge matrix
    say("")
    say("=" * 118)
    say("%-8s %-16s %-30s %-7s %9s %9s %9s  %-24s %-34s" %
        ("case", "category", "pair", "arm", "d_obs", "D_lo", "D_hi", "tail", "verdict"))
    rows, npass = [], 0
    for c in M.DEV_CASES:
        for arm in ("limited", "rich"):
            r = F1.compare(acq[(c.left, arm, 0)], acq[(c.right, arm, 1)],
                           rad[arm]["r_continuity"], rad[arm]["r_separation"], common_channel=c.common_channel)
            ok = (r["verdict"] == c.expect[arm]); npass += ok
            rows.append({"cid": c.cid, "category": c.category, "arm": arm, "left": c.left, "right": c.right,
                         "d_obs": r["distance"], "D_lo": r["D_lo"], "D_hi": r["D_hi"],
                         "tail_status": r["tail_status"], "verdict": r["verdict"], "expected": c.expect[arm],
                         "ok": bool(ok), "tags": list(c.tags), "why": r["why"]})
            say("%-8s %-16s %-30s %-7s %9.2f %9.2f %9s  %-24s %-34s %s"
                % (c.cid, c.category, c.left + "|" + c.right, arm, r["distance"], r["D_lo"],
                   ("inf" if not np.isfinite(r["D_hi"]) else "%.2f" % r["D_hi"]), r["tail_status"], r["verdict"],
                   "OK" if ok else "** FAIL (want %s)" % c.expect[arm]))
    log["matrix"] = rows; log["passed"] = int(npass); log["total"] = 2 * len(M.DEV_CASES)
    say("  DEVELOPMENT: %d / %d" % (npass, 2 * len(M.DEV_CASES)))
    json.dump(log, open(os.path.join(OUT, "dev_raw.json"), "w"), indent=1, default=float)
    say("wrote %s (%.0fs)" % (os.path.join(OUT, "dev_raw.json"), time.time() - t0))
    return log, acq, rad, dev


if __name__ == "__main__":
    main()
