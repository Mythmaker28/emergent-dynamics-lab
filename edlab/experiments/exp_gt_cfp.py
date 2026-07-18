"""EXP-GT-CONTINUOUS-FINGERPRINT-00 -- DEVELOPMENT.

Calibration, representation selection, the development challenge matrix, and the eight must-fail controls.
DEVELOPMENT DATA ONLY. The prospective systems are never touched here.

The tolerance is calibrated on the NULL -- repeated independent measurement of the SAME system -- and on nothing
else. No difference pair and no label is ever consulted to set a radius. That rule (SAFETY=2.0, SEP_FACTOR=3.0)
was frozen in docs/CONTINUOUS_FINGERPRINT_PROTOCOL.md before this file existed, and is not revisited.
"""

from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

from ..identity import cfingerprint as F
from ..substrates.ctrans import engine as E, evaluator as V, manifests as M

OUT = os.path.join("results", "EXP-GT-CFP-DEV")
SAFETY = 2.0
SEP_FACTOR = 3.0
NONNULL = ("D_silent_dead", "D_silent_sat", "D_noisy", "D_drifty", "D_lowcov")


def channel(spec):
    """THE MEASUREMENT CHANNEL -- the only thing the instrument is ever given. It closes over the spec, so the
    instrument cannot reach inside it: no topology, no hidden state, no label, no parameter. A probe aimed at an
    address this system refuses returns ok=False: MISSING, not zero."""
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


def say(*a):
    print(*a)
    sys.stdout.flush()


CACHE = os.path.join("results", "_cfp_cache3")


def cached_acquire(spec, arm, seed0, key, **kw):
    """Memoised on disk. The acquisition is a deterministic function of (spec, arm, seed, battery), so the cache
    changes nothing scientific: it is the same number, computed once. It exists because the sandbox kills a run
    between invocations and a benchmark that cannot be resumed cannot be audited either."""
    os.makedirs(CACHE, exist_ok=True)
    fp = os.path.join(CACHE, key + ".npz")
    if os.path.exists(fp):
        z = np.load(fp, allow_pickle=True)
        return {k: (z[k].item() if z[k].ndim == 0 else z[k]) for k in z.files}
    a = F.acquire(channel(spec), arm, seed0, **kw)
    np.savez_compressed(fp, **{k: np.asarray(v, dtype=object) if k == "probes" else np.asarray(v)
                               for k, v in a.items()})
    return a


def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    dev = M.dev_systems()
    idx = {nm: i for i, nm in enumerate(dev)}
    log = {"protocol": "EXP-GT-CONTINUOUS-FINGERPRINT-00", "phase": "DEVELOPMENT",
           "SAFETY": SAFETY, "SEP_FACTOR": SEP_FACTOR,
           "frozen": {"N_REPEAT": F.N_REPEAT, "W_RESP": F.W_RESP, "W_PRE": F.W_PRE, "PHASES": list(F.PHASES),
                      "DETREND": F.DETREND, "REPRESENTATION": F.REPRESENTATION,
                      "PHASE_QUOTIENT": F.PHASE_QUOTIENT, "AGGREGATE": F.AGGREGATE,
                      "SCALE_BAND": F.SCALE_BAND, "Z_DET": F.Z_DET,
                      "COVERAGE_FLOOR": F.COVERAGE_FLOOR, "BASELINE_MAX": F.BASELINE_MAX,
                      "IN_FLIGHT_MAX": F.IN_FLIGHT_MAX}}

    acq = {}
    for arm in ("limited", "rich"):
        b = 0 if arm == "limited" else 5_000_000
        for nm, s in dev.items():
            for k in (0, 1):
                acq[(nm, arm, k)] = cached_acquire(s, arm, M.DEV_SEED_BASE + b + 3000 * idx[nm] + 1500 * k,
                                                   "dev_%s_%s_%d" % (nm, arm, k))
    say("acquisitions: %d in %.0fs" % (len(acq), time.time() - t0))

    # ---------------------------------------------------------------- NULL CALIBRATION -> the radii
    say("")
    say("=" * 110)
    say("NOISE / TOLERANCE CALIBRATION -- from the NULL alone. No label and no difference pair is consulted.")
    nullnames = [nm for nm in dev if nm not in NONNULL]
    nulls = {}
    for arm in ("limited", "rich"):
        ns = [F.distance(acq[(nm, arm, 0)], acq[(nm, arm, 1)]) for nm in nullnames]
        ns = [x for x in ns if np.isfinite(x)]
        q = float(np.quantile(ns, 0.999))
        nulls[arm] = {"n": len(ns), "mean": float(np.mean(ns)), "max": float(np.max(ns)), "q999": q,
                      "r_continuity": SAFETY * q, "r_separation": SEP_FACTOR * SAFETY * q}
        say("  %-8s n=%2d mean=%.3f max=%.3f q99.9=%.3f  ->  r_continuity=%.3f  r_separation=%.3f"
            % (arm, len(ns), np.mean(ns), np.max(ns), q, SAFETY * q, SEP_FACTOR * SAFETY * q))
    log["null_calibration"] = nulls

    # ---------------------------------------------------------------- DEVELOPMENT CHALLENGE MATRIX
    say("")
    say("=" * 110)
    say("DEVELOPMENT CHALLENGE MATRIX")
    say("%-10s %-17s %-27s %-8s %10s  %-34s %s" % ("case", "category", "pair", "arm", "distance", "verdict", ""))
    rows, npass = [], 0
    for c in M.DEV_CASES:
        for arm in ("limited", "rich"):
            r = F.compare(acq[(c.left, arm, 0)], acq[(c.right, arm, 1)],
                          nulls[arm]["r_continuity"], nulls[arm]["r_separation"],
                          common_channel=c.common_channel)
            ok = (r["verdict"] == c.expect[arm])
            npass += ok
            rows.append({"cid": c.cid, "category": c.category, "arm": arm, "left": c.left, "right": c.right,
                         "distance": r["distance"], "verdict": r["verdict"], "expected": c.expect[arm],
                         "admitted": r["admitted"], "coverage": r["coverage"], "ok": bool(ok), "why": r["why"]})
            say("%-10s %-17s %-27s %-8s %10.3f  %-34s %s"
                % (c.cid, c.category, c.left + "|" + c.right, arm, r["distance"], r["verdict"],
                   "OK" if ok else "** FAIL (expected %s)" % c.expect[arm]))
    total = 2 * len(M.DEV_CASES)
    log["development_matrix"] = rows
    log["development_passed"] = int(npass)
    log["development_total"] = total
    say("  DEVELOPMENT: %d / %d" % (npass, total))

    # ---------------------------------------------------------------- MUST-FAIL CONTROLS
    say("")
    say("=" * 110)
    say("MUST-FAIL CONTROLS. Each MUST actually fail. One that still passes was never load-bearing.")
    rc, rs = nulls["limited"]["r_continuity"], nulls["limited"]["r_separation"]
    ctl = []

    def rec(cid, what, expect, observed, fired, detail=""):
        ctl.append({"id": cid, "breaks": what, "expected": expect, "observed": observed, "FIRED": bool(fired),
                    "detail": detail})
        say("  %-4s %-46s %-26s %s" % (cid, what, observed, "FIRED" if fired else "** DID NOT FIRE **"))

    A, Bn = acq[("D_leak", "limited", 0)], acq[("D_leak", "limited", 1)]      # the NULL: a system vs itself
    # L1 exact float inequality
    d1 = F.exact_float_distance(A, Bn)
    rec("L1", "exact float inequality as the metric", "false DIFFERENCE explodes",
        "%.4f of samples differ (system vs ITSELF)" % d1, d1 > 0.99,
        "calibrated metric gives %.3f, well inside r_continuity=%.3f" % (F.distance(A, Bn), rc))
    # L2 integer collapse
    q1 = F.acquire(channel(dev["D_leak"]), "limited", 100000, quantize_uint8=True)
    q2 = F.acquire(channel(dev["D_leak_sign"]), "limited", 700000, quantize_uint8=True)
    d2 = F.distance(q1, q2)
    rec("L2", "uint8 cast with no calibrated scaling", "false SAMENESS explodes",
        "d(leak, SIGN-INVERTED) = %.4f" % d2, d2 <= rc,
        "the calibrated instrument gives %.1f for this pair" % F.distance(A, acq[("D_leak_sign", "limited", 1)]))
    # L3 short window (shorter than the longest development response)
    s1 = F.acquire(channel(dev["D_mem_p"]), "limited", 100000, w_resp=40)
    s2 = F.acquire(channel(dev["D_mem_m"]), "limited", 700000, w_resp=40)
    pers_full = sum(acq[("D_mem_p", "limited", 0)]["persistence"])
    pers_short = sum(s1["persistence"])
    rec("L3", "response window 40 (< the longest response)", "memory/late response misclassified",
        "persistent rows: %d with W=160 -> %d with W=40" % (pers_full, pers_short),
        pers_short != pers_full or s1["in_flight_frac"] > F.IN_FLIGHT_MAX,
        "in_flight_frac rises to %.2f" % s1["in_flight_frac"])
    # L4 remove the discriminating probe (supply)
    def drop_supply(Z):
        Z2 = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in Z.items()}
        Z2["missing"] = Z["missing"].copy()
        Z2["missing"][6, :] = True
        Z2["missing"][7, :] = True
        return Z2
    d4 = F.distance(drop_supply(acq[("D_leak", "limited", 0)]), drop_supply(acq[("D_supply", "limited", 1)]))
    d4full = F.distance(acq[("D_leak", "limited", 0)], acq[("D_supply", "limited", 1)])
    rec("L4", "remove the SUPPLY probes from the battery", "a genuine difference collapses",
        "d(leak, supply_cause): %.2f -> %.2f" % (d4full, d4), d4 <= rc,
        "under drive-only probing the two are identical BY CONSTRUCTION (6.5e-19)")
    # L5 forbidden descriptive coordinate
    d5 = F.distance(acq[("D_leak", "limited", 0)], acq[("D_leak_dead", "limited", 1)],
                    contaminant=("leak", "leak+dead_site"))
    d5c = F.distance(acq[("D_leak", "limited", 0)], acq[("D_leak_dead", "limited", 1)])
    rec("L5", "reintroduce a forbidden topology label", "false DIFFERENCE among equivalent implementations",
        "d(leak, leak+dead_site): %.2f -> %.2f" % (d5c, d5), d5 >= rs,
        "the two are BIT-FOR-BIT identical in accessible behaviour under both arms")
    # L6 lexicographic phase sort
    d6 = F.distance(A, Bn, phase_quotient="lexsort")
    rec("L6", "lexicographic phase sort (Boolean-style quotient)", "false DIFFERENCE from row reordering",
        "NULL distance: %.2f -> %.2f" % (F.distance(A, Bn), d6), d6 > rc,
        "a canonical ordering of CONTINUOUS rows is discontinuous under noise")
    # L7 noise-blind normalization
    g0, g1 = acq[("D_leak", "limited", 0)], acq[("D_leak_gain2", "limited", 1)]
    d7 = F.distance(g0, g1, representation="resp_rms")
    d7n = F.distance(A, Bn, representation="resp_rms")
    rec("L7", "normalize by the response's own RMS, not the noise", "false SAMENESS: gain vanishes",
        "d(gain x2)=%.3f vs NULL=%.3f" % (d7, d7n), d7 <= 3 * d7n,
        "the calibrated instrument gives %.1f for this pair" % F.distance(g0, g1))
    # L8 disable the common-channel refusal
    r8 = F.compare(acq[("D_leak", "limited", 0)], acq[("D_leak_loud", "limited", 1)], rc, rs,
                   common_channel=False, enforce_channel=False)
    rec("L8", "disable the common-noise-channel refusal", "false DIFFERENCE: quieter channel reads as more gain",
        "SAME system, 4x noisier channel -> %s (d=%.2f)" % (r8["verdict"], r8["distance"]),
        r8["verdict"] == F.DIFFERENT, "with the refusal ON the instrument returns INDETERMINATE")
    log["must_fail_controls"] = ctl
    log["controls_fired"] = sum(c["FIRED"] for c in ctl)
    say("  CONTROLS FIRED: %d / %d" % (log["controls_fired"], len(ctl)))

    # ---------------------------------------------------------------- diagnostics
    say("")
    say("=" * 110)
    say("DIAGNOSTICS")
    th = V.theseus_replacement(dev["D_leak"], dev["D_leak_reloc"], t_swap=150)
    log["ship_of_theseus"] = th
    say("  SHIP OF THESEUS (implementation replaced mid-trajectory at t=150):")
    say("    deviating samples = %d ; span from swap to last deviation = %d ; max relative deviation = %.2e"
        % (th["n_deviating_samples"], th["span_from_swap_to_last_deviation"], th["max_relative_deviation"]))
    say("    (these are DIFFERENT QUANTITIES and carry DIFFERENT NAMES. Conflating them is the D-073 error.)")
    conv = {nm: V.solver_convergence(dev[nm]) for nm in ("D_leak", "D_fb", "D_sat", "D_cascade", "D_mem_p")}
    log["solver_convergence"] = conv
    say("  SOLVER CONVERGENCE (h=.25 vs h=.125): " + "  ".join("%s=%.1e" % kv for kv in conv.items()))
    log["coverage_table"] = {nm: {"coverage": acq[(nm, "limited", 0)]["coverage"],
                                  "responsive": acq[(nm, "limited", 0)]["responsive"],
                                  "baseline_stability": acq[(nm, "limited", 0)]["baseline_stability"],
                                  "in_flight_frac": acq[(nm, "limited", 0)]["in_flight_frac"],
                                  "sigma_hat": acq[(nm, "limited", 0)]["sigma_hat"]} for nm in dev}

    # ---------------------------------------------------------------- two-path benchmark validation (DEV)
    say("")
    say("=" * 110)
    say("BENCHMARK VALIDATION -- construction truth vs the PRIVILEGED path (which never imports the instrument)")
    PV = os.path.join(OUT, "priv_dev_v2.json")
    if os.path.exists(PV):
        pv_all = json.load(open(PV))                      # computed in bounded chunks; deterministic and cached
    else:
        pv_all = {}
        for c in M.DEV_CASES:
            for arm in ("limited", "rich"):
                pv = V.privileged_compare(dev[c.left], dev[c.right], arm)
                pv_all["%s|%s" % (c.cid, arm)] = {"verdict": pv["verdict"], "residual": pv["residual"],
                                                  "agree": bool(_agree(c, arm, pv)), "category": c.category}
        json.dump(pv_all, open(PV, "w"), indent=1)
    bad = [{"cid": k, "privileged": v["verdict"], "category": v["category"]}
           for k, v in pv_all.items() if not v["agree"]]
    log["privileged_validation"] = pv_all
    log["benchmark_disagreements"] = bad
    say("  disagreements: %d  (any disagreement REJECTS the case before scoring)" % len(bad))
    for b in bad:
        say("    ** %s [%s] category=%s privileged=%s" % (b["cid"], b["arm"], b["category"], b["privileged"]))

    json.dump(log, open(os.path.join(OUT, "dev_raw.json"), "w"), indent=1, default=float)
    say("")
    say("QUALIFIED ON DEVELOPMENT: %s" % (npass == total and log["controls_fired"] == len(ctl) and not bad))
    say("wrote %s  (%.0fs)" % (os.path.join(OUT, "dev_raw.json"), time.time() - t0))
    return log


def _agree(c, arm, pv):
    """Does the privileged path confirm the construction label? Declared per category."""
    v = pv["verdict"]
    if c.category in (M.CONTINUITY, M.FALSE_DIFFERENCE):
        return v == (V.PRIV_EQUIVALENT if c.expect[arm] == M.INDIST else V.PRIV_DIFFERENT)
    if c.category == M.DIFFERENCE:
        return v == V.PRIV_DIFFERENT
    if c.category == M.FALSE_SAMENESS:
        return v == (V.PRIV_EQUIVALENT if arm == "limited" else V.PRIV_DIFFERENT)
    if c.category == M.ABSTAIN:
        L, R = pv["left"], pv["right"]
        if "silent" in c.tags:
            return v == V.PRIV_SILENT
        if "noise" in c.tags:
            return L["unreadable"] or R["unreadable"]
        if "in_flight" in c.tags:
            return L["in_flight"] or R["in_flight"]
        if "drift" in c.tags:
            return L["nonstationary"] or R["nonstationary"]
        if "coverage" in c.tags:
            return bool(L["blocked"]) != bool(R["blocked"])
        if "contract" in c.tags:
            return not c.common_channel        # a DECLARATION about the channel, not an inference from the world
    return False


if __name__ == "__main__":
    main()
