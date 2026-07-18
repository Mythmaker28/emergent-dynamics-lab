"""EXP-GT-CONTINUOUS-FINGERPRINT-00 -- THE SINGLE PROSPECTIVE RUN.

THIS FILE REFUSES TO RUN IF THE INSTRUMENT HAS CHANGED BY ONE BYTE since the freeze. That check is the only thing
standing between a prospective qualification and a retrospective one, and it is not a comment -- it is an assert.

The gates G1-G10, the radii, the battery, the representation, the noise model and the verdict logic were all fixed
before any prospective system was ever simulated. Nothing here is tuned. If it fails, it fails, and the version is
RETIRED rather than repaired.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time

import numpy as np

from ..identity import cfingerprint as F
from ..substrates.ctrans import evaluator as V, manifests as M
from .exp_gt_cfp import CACHE, channel, cached_acquire, _agree

FREEZE = "docs/CONTINUOUS_FINGERPRINT_FREEZE_MANIFEST.json"
OUT = os.path.join("results", "EXP-GT-CFP-PROSPECTIVE")
PCACHE = os.path.join("results", "_cfp_cache_p")


def verify_freeze():
    man = json.load(open(FREEZE))
    bad = []
    for f, h in man["hashes"].items():
        got = hashlib.sha256(open(f, "rb").read()).hexdigest()
        if got != h:
            bad.append((f, h[:12], got[:12]))
    if bad:
        for f, want, got in bad:
            print("HASH MISMATCH %s frozen=%s ondisk=%s" % (f, want, got))
        raise SystemExit("REFUSING TO RUN. The instrument is not the one that was frozen. A prospective run "
                         "against a modified instrument is not a prospective run.")
    print("freeze verified: %d files match their frozen sha256" % len(man["hashes"]))
    return man


def acq_p(spec, arm, seed0, key):
    os.makedirs(PCACHE, exist_ok=True)
    fp = os.path.join(PCACHE, key + ".npz")
    if os.path.exists(fp):
        z = np.load(fp, allow_pickle=True)
        return {k: (z[k].item() if z[k].ndim == 0 else z[k]) for k in z.files}
    a = F.acquire(channel(spec), arm, seed0)
    np.savez_compressed(fp, **{k: np.asarray(v, dtype=object) if k == "probes" else np.asarray(v)
                               for k, v in a.items()})
    return a


def main(budget=1e9):
    man = verify_freeze()
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    rad = man["FROZEN_metric"]["radii"]
    pro = M.prospective_systems()
    idx = {nm: i for i, nm in enumerate(pro)}

    # ---- STEP 1: BENCHMARK VALIDATION FIRST. A case whose two truth paths disagree is REJECTED BEFORE SCORING.
    PV = os.path.join(OUT, "priv_prospective.json")
    pv_all = json.load(open(PV)) if os.path.exists(PV) else {}
    for c in M.PROSPECTIVE_CASES:
        for arm in ("limited", "rich"):
            k = "%s|%s" % (c.cid, arm)
            if k in pv_all or time.time() - t0 > budget:
                continue
            pv = V.privileged_compare(pro[c.left], pro[c.right], arm)
            pv_all[k] = {"verdict": pv["verdict"], "residual": pv["residual"],
                         "agree": bool(_agree(c, arm, pv)), "category": c.category}
    json.dump(pv_all, open(PV, "w"), indent=1)
    if len(pv_all) < 2 * len(M.PROSPECTIVE_CASES):
        print("privileged validation %d/%d -- rerun to continue" % (len(pv_all), 2 * len(M.PROSPECTIVE_CASES)))
        return None
    rejected = sorted({k.split("|")[0] for k, v in pv_all.items() if not v["agree"]})
    print("BENCHMARK VALIDATION: %d/%d agree; REJECTED cases: %s"
          % (sum(v["agree"] for v in pv_all.values()), len(pv_all), rejected or "none"))
    if len(rejected) > 2:
        json.dump({"BENCHMARK_INVALID": True, "rejected": rejected}, open(os.path.join(OUT, "result.json"), "w"))
        print("EXP-GT-CONTINUOUS-FINGERPRINT-00: BENCHMARK_INVALID")
        return None

    # ---- STEP 2: acquire (frozen battery), then score against the FROZEN radii
    acq = {}
    for arm in ("limited", "rich"):
        b = 0 if arm == "limited" else 5_000_000
        for nm, s in pro.items():
            for k in (0, 1):
                acq[(nm, arm, k)] = acq_p(s, arm, M.PROSP_SEED_BASE + b + 3000 * idx[nm] + 1500 * k,
                                          "p_%s_%s_%d" % (nm, arm, k))
    print("acquisitions: %d (%.0fs)" % (len(acq), time.time() - t0))

    rows, dist = [], {"limited": {"indist": [], "diff": []}, "rich": {"indist": [], "diff": []}}
    print("")
    print("%-9s %-17s %-27s %-8s %10s  %-34s %s" % ("case", "category", "pair", "arm", "distance", "verdict", ""))
    for c in M.PROSPECTIVE_CASES:
        if c.cid in rejected:
            continue
        for arm in ("limited", "rich"):
            r = F.compare(acq[(c.left, arm, 0)], acq[(c.right, arm, 1)],
                          rad[arm]["r_continuity"], rad[arm]["r_separation"], common_channel=c.common_channel)
            ok = (r["verdict"] == c.expect[arm])
            rows.append({"cid": c.cid, "category": c.category, "arm": arm, "left": c.left, "right": c.right,
                         "distance": r["distance"], "verdict": r["verdict"], "expected": c.expect[arm],
                         "admitted": r["admitted"], "coverage": r["coverage"], "ok": bool(ok),
                         "tags": list(c.tags), "why": r["why"]})
            if r["admitted"]:
                if c.expect[arm] == M.INDIST:
                    dist[arm]["indist"].append(r["distance"])
                elif c.expect[arm] == M.DIFFERENT:
                    dist[arm]["diff"].append(r["distance"])
            print("%-9s %-17s %-27s %-8s %10.3f  %-34s %s"
                  % (c.cid, c.category, c.left + "|" + c.right, arm, r["distance"], r["verdict"],
                     "OK" if ok else "** FAIL (expected %s)" % c.expect[arm]))

    # ---- STEP 3: THE PREDECLARED GATES
    G, by = {}, lambda cat: [r for r in rows if r["category"] == cat]
    G["G1_continuity_not_called_different"] = all(
        r["verdict"] != M.DIFFERENT for r in rows
        if r["category"] in (M.CONTINUITY, M.FALSE_DIFFERENCE) and r["expected"] == M.INDIST)
    G["G2_difference_pairs_separate"] = all(r["ok"] for r in by(M.DIFFERENCE))
    gaps = {}
    for arm in ("limited", "rich"):
        hi = max(dist[arm]["indist"]) if dist[arm]["indist"] else float("nan")
        lo = min(dist[arm]["diff"]) if dist[arm]["diff"] else float("nan")
        gaps[arm] = {"max_indist": hi, "min_diff": lo, "gap": lo - hi}
    G["G3_strict_non_overlap"] = all(gaps[a]["gap"] > 0 for a in gaps)
    G["G4_abstain_cases_indeterminate"] = all(r["ok"] for r in by(M.ABSTAIN))
    fs = {r["arm"]: r for r in by(M.FALSE_SAMENESS)}
    G["G5_false_sameness_equivalence_class_only"] = (
        fs.get("limited", {}).get("verdict") == M.INDIST and fs.get("rich", {}).get("verdict") == M.DIFFERENT)
    # G6 -- EXACT unit invariance: same seeds, affine readout, standardized fingerprints must coincide
    a1 = F.acquire(channel(pro["P_leak"]), "limited", 987654)
    a2 = F.acquire(channel(pro["P_leak_units"]), "limited", 987654)
    du = float(np.nanmax(np.abs(a1["Z"] - a2["Z"])) / max(np.nanmax(np.abs(a1["Z"])), 1e-300))
    G["G6_unit_invariance_exact"] = du <= 1e-9
    G["G6_max_relative_deviation"] = du
    G["G7_continuity_survives_unseen_noise"] = all(
        r["verdict"] != M.DIFFERENT for r in rows if r["cid"] == "C-P-08")
    G["G8_hidden_state_detected"] = any(
        r["verdict"] == M.DIFFERENT for r in rows if r["cid"] == "C-P-16")
    nd = sum(r["verdict"] == M.DIFFERENT for r in rows if r["arm"] == "limited")
    ni = sum(r["verdict"] == M.INDIST for r in rows if r["arm"] == "limited")
    G["G9_non_vacuous"] = (nd >= 4 and ni >= 4)
    G["G9_counts"] = {"DIFFERENT": nd, "INDISTINGUISHABLE": ni}
    G["G10_two_paths_agree"] = (len(rejected) == 0)

    npass = sum(r["ok"] for r in rows)
    hard = [k for k, v in G.items() if k.startswith("G") and isinstance(v, bool) and not v]
    verdict = "PASS" if not hard else "FAIL"
    print("")
    print("=" * 110)
    print("PROSPECTIVE MATRIX: %d / %d" % (npass, len(rows)))
    for arm in ("limited", "rich"):
        print("  %-8s max(indist)=%8.3f  min(diff)=%9.3f  GAP=%9.3f   [r_cont=%.3f r_sep=%.3f]"
              % (arm, gaps[arm]["max_indist"], gaps[arm]["min_diff"], gaps[arm]["gap"],
                 rad[arm]["r_continuity"], rad[arm]["r_separation"]))
    print("")
    for k in sorted(G):
        if isinstance(G[k], bool):
            print("  %-45s %s" % (k, "PASS" if G[k] else "** FAIL **"))
    print("")
    print("EXP-GT-CONTINUOUS-FINGERPRINT-00: %s" % verdict)

    res = {"protocol": "EXP-GT-CONTINUOUS-FINGERPRINT-00", "phase": "PROSPECTIVE", "verdict": verdict,
           "matrix": "%d/%d" % (npass, len(rows)), "gates": G, "gaps": gaps, "radii": rad,
           "rejected_cases": rejected, "rows": rows, "privileged": pv_all,
           "freeze_hashes": man["hashes"]}
    json.dump(res, open(os.path.join(OUT, "prospective_raw.json"), "w"), indent=1, default=float)
    print("wrote %s" % os.path.join(OUT, "prospective_raw.json"))
    return res


if __name__ == "__main__":
    main(budget=float(sys.argv[1]) if len(sys.argv) > 1 else 1e9)
