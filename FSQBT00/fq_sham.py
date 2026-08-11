"""FSQBT00 Section 6 -- twin shams and prospective weighted-L2 thresholds.
Two identity continuations per sealed descendant in separate fresh processes (reusing the parent's
committed write-only worker fw_worker.py), full X_A/X_B series persisted, twin identity required
over the full horizon, and TAU_b computed by the exact qualified WL2 rule with an independent
reference. 24 sham starts."""
from __future__ import annotations
import json, hashlib, os, sys, subprocess, math, time
from fractions import Fraction as Fr
import numpy as np
for p in ("/home/claude/sweep", "/home/claude/sweep/PPAI", "/home/claude/sweep/DOMC",
          "/home/claude/sweep/ETPC", "/home/claude/sweep/WSFSCRP00", "/home/claude/sweep/WL2SMF00",
          "/home/claude/sweep/FWL2CF00"):
    sys.path.insert(0, p)
import wsfscrp_core as Z
import wl2_prod as P
import wl2_ref as Rf
OUT = "/home/claude/sweep/FSQBT00"
PANEL = f"{OUT}/panel"
SRAW = f"{OUT}/sham_raw_full"
os.makedirs(SRAW, exist_ok=True)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
t0 = time.time()

FRZ = json.load(open(f"{OUT}/FSQBT00_MASTER_FREEZE_HASHES.json"))
assert sha(f"{OUT}/FSQBT00_MASTER_FREEZE.md") == FRZ["hashes"]["FSQBT00_MASTER_FREEZE.md"], "freeze mutated"
MAN = json.load(open(f"{OUT}/FRESH_PANEL_MANIFEST.json"))
WORKER = "/home/claude/sweep/FWL2CF00/fw_worker.py"

START_LOG = open(f"{OUT}/START_AND_ACCESS_LEDGER.jsonl", "a")
def start_enter(kind, tag):
    START_LOG.write(json.dumps({"kind": kind, "tag": tag}) + "\n"); START_LOG.flush()
    os.fsync(START_LOG.fileno())


def run_worker(ckpt, mask, op, out, exp_sha, expect):
    start_enter("sham", os.path.basename(out))
    r = subprocess.run([sys.executable, WORKER, ckpt, mask, op, out, exp_sha, expect],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("sham worker failed: " + r.stderr[-800:])
    return json.loads(r.stdout.strip())


SHAM = {"n": 0, "log": []}
sham_series = {}
twin = []
rows = []
for blk in MAN["blocks"]:
    did = blk["did"]
    ck = f"{PANEL}/d_{did}.npz"; mk = f"{PANEL}/m_{did}.npz"
    st0 = Z.load(ck); exp_sha = Z.full_sha(st0)
    assert exp_sha == blk["checkpoint_sha"], "checkpoint hash mismatch"
    o0 = f"{SRAW}/SHAM_0_{did}.npz"; o1 = f"{SRAW}/SHAM_1_{did}.npz"
    for o in (o0, o1):
        if os.path.exists(o):
            os.remove(o)
        if os.path.exists(o + ".meta.json"):
            os.remove(o + ".meta.json")
    m0 = run_worker(ck, mk, "SHAM", o0, exp_sha, "identity_copy"); SHAM["n"] += 1
    m1 = run_worker(ck, mk, "SHAM", o1, exp_sha, "identity_copy"); SHAM["n"] += 1
    SHAM["log"] += [f"SHAM_0_{did}", f"SHAM_1_{did}"]
    j0 = json.load(open(o0 + ".meta.json")); j1 = json.load(open(o1 + ".meta.json"))
    # reader series from the raw full-field archive
    def series(npz):
        d = np.load(npz); rho = d["rho"]; MA = d["MA"]; MB = d["MB"]
        sel = np.nonzero(MA | MB); B = Z.dsum(st0.rho[sel])
        XA, XB = [], []
        for k in range(rho.shape[0]):
            a = Z.dsum(rho[k][np.nonzero(MA)]) / B
            b = Z.dsum(rho[k][np.nonzero(MB)]) / B
            XA.append(a); XB.append(b)
        return XA, XB, B
    XA0s, XB0s, B0 = series(o0)
    XA1s, XB1s, B1 = series(o1)
    twin_ok = (j0["per_time_state_sha"] == j1["per_time_state_sha"]
               and j0["terminal_state_sha"] == j1["terminal_state_sha"]
               and [str(x) for x in XA0s] == [str(x) for x in XA1s]
               and [str(x) for x in XB0s] == [str(x) for x in XB1s])
    twin.append({"did": did, "twin_identity_full_horizon": bool(twin_ok),
                 "terminal_hash_identical": j0["terminal_state_sha"] == j1["terminal_state_sha"]})
    # thresholds from SHAM_0 (production + independent reference)
    XA0, XB0 = XA0s[0], XB0s[0]
    XA, XB = XA0s[1:], XB0s[1:]
    B = B0
    sel = np.nonzero(np.load(mk)["MA"] | np.load(mk)["MB"])
    rho_sup = [float(x) for x in st0.rho[sel]]
    med = P.exact_median(rho_sup)
    dyn_sq = P.tau_dynamic_sq(XA, XB, XA0, XB0)
    site_sq = (P.COEFF * med / B) ** 2 * P.W_POST
    tau_sq = P.tau_material_sq(Fr(0), dyn_sq, site_sq)
    r_dyn = Rf.tau_dynamic_sq(XA, XB, XA0, XB0)
    r_med = Rf.median(rho_sup)
    r_site = (Fr(1, 100) * r_med / B) ** 2 * sum(Rf.WR, Fr(0))
    r_tau = Rf.tau_material_sq(Fr(0), r_dyn, r_site)
    dom = ("ETA_ORACLE_L2" if 0 >= max(dyn_sq, site_sq)
           else ("TAU_DYNAMIC_L2" if dyn_sq >= site_sq else "TAU_SITE_L2"))
    rows.append({"did": did, "seed": blk["seed"], "geometry": blk["geometry"], "alloc": blk["alloc"],
                 "B": str(B), "RHO_MED": str(med), "n_support": len(rho_sup),
                 "TAU_DYNAMIC_L2": math.sqrt(float(dyn_sq)), "TAU_SITE_L2": math.sqrt(float(site_sq)),
                 "ETA_ORACLE_L2": 0.0, "TAU_MATERIAL_L2": math.sqrt(float(tau_sq)),
                 "TAU_MATERIAL_L2_sq_exact": str(tau_sq), "dominant_term": dom,
                 "reference_agrees_tau": bool(r_tau == tau_sq),
                 "tau_positive_finite": bool(tau_sq > 0 and math.isfinite(float(tau_sq)))})
    sham_series[did] = {"XA": [str(x) for x in XA0s], "XB": [str(x) for x in XB0s], "B": str(B0),
                        "terminal_state_sha": j0["terminal_state_sha"],
                        "sham0_output_sha256": m0["sha"], "sham1_output_sha256": m1["sha"]}
    print("  %s TAU=%.4e dom=%s twin_ok=%s refok=%s [%.0fs]"
          % (did, rows[-1]["TAU_MATERIAL_L2"], dom, twin_ok, rows[-1]["reference_agrees_tau"], time.time() - t0), flush=True)

TWIN_ALL = all(t["twin_identity_full_horizon"] for t in twin)
TAU_ALL_OK = all(r["tau_positive_finite"] and r["reference_agrees_tau"] for r in rows)
# E_TAU_FRESH = sum_b TAU_b^2 / 12 (exact), alpha per row 1/24
E_TAU = sum((Fr(r["TAU_MATERIAL_L2_sq_exact"]) for r in rows), Fr(0)) / 12
A_TAU = math.sqrt(float(E_TAU))
json.dump({"twin_identity_all_12": TWIN_ALL, "twins": twin, "thresholds": rows,
           "E_TAU_FRESH_exact": str(E_TAU), "A_TAU_FRESH": A_TAU,
           "alpha_per_row": "1/24", "block_weight": "1/12",
           "TAU_range": [min(r["TAU_MATERIAL_L2"] for r in rows), max(r["TAU_MATERIAL_L2"] for r in rows)],
           "eta_oracle_L2": "0 exact on every descendant (exact scoring path)",
           "sham_starts": SHAM["n"], "all_tau_positive_finite_ref_agree": TAU_ALL_OK},
          open(f"{OUT}/FRESH_WEIGHTED_L2_THRESHOLDS.json", "w"), indent=1)
json.dump(sham_series, open(f"{OUT}/FRESH_SHAM_SERIES_AND_HASHES.json", "w"), indent=1)
print("\nsham starts %d/24 | twin identity 12/12=%s | TAU pos/finite+ref-agree=%s"
      % (SHAM["n"], TWIN_ALL, TAU_ALL_OK))
print("E_TAU_FRESH=%s  A_TAU=%.6e  TAU range %.4e..%.4e"
      % (str(E_TAU)[:20] + "...", A_TAU, min(r["TAU_MATERIAL_L2"] for r in rows), max(r["TAU_MATERIAL_L2"] for r in rows)))
