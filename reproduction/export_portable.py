"""Export committed raw results to safe, portable formats (CSV/JSON/NPZ). No new computation, no physics.
Pickles are retained in-repo for provenance; this makes the numbers readable without unpickling.

Usage: python -m reproduction.export_portable
"""
from __future__ import annotations
import os, json, pickle, hashlib, csv
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "release", "data")
RAW = {
    "holdout": "results/observer/tca_holdout_raw.pkl",
    "causal_transplant": "results/wd01_phasec/phasec_causal_transplant_raw.pkl",
    "causal_inplace": "results/wd01_phasec/phasec_causal_inplace_raw.pkl",
    "h2cert_sealed": "results/h2cert/h2cert_sealed_raw.pkl",
}
FEAT_NAMES = ["mean_m1","std_m1","p10_m1","p50_m1","p90_m1","mean_m2","std_m2","p10_m2","p50_m2","p90_m2"]


def _sha(p):
    h=hashlib.sha256(); h.update(open(p,"rb").read()); return h.hexdigest()


def export_holdout():
    recs = pickle.load(open(os.path.join(ROOT, RAW["holdout"]), "rb"))
    steps = sorted(recs[0]["ck"].keys())
    # long-format per (record, checkpoint)
    with open(os.path.join(OUT, "holdout_longitudinal.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["seed","history","h1_true","h2_true","step","M","size","mminus_std"] + FEAT_NAMES)
        for r in recs:
            for s in steps:
                lo = r["ck"][s]["long"]
                w.writerow([r["seed"], r["hi"], r["h1"], r["h2"], s, lo[1], lo[2], lo[3]] + list(lo[0]))
    # NPZ deep arrays
    deep = 800
    X = np.array([list(r["ck"][deep]["long"][0]) + [r["ck"][deep]["long"][3]] for r in recs])
    np.savez(os.path.join(OUT, "holdout_deep_arrays.npz"),
             features=X, h1_true=np.array([r["h1"] for r in recs]),
             h2_true=np.array([r["h2"] for r in recs]),
             history=np.array([r["hi"] for r in recs]), seed=np.array([r["seed"] for r in recs]),
             feature_names=np.array(FEAT_NAMES + ["mminus_std"]))
    return len(recs), steps


def export_causal():
    tr = pickle.load(open(os.path.join(ROOT, RAW["causal_transplant"]), "rb"))
    with open(os.path.join(OUT, "causal_transplant.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["history","seed","h1_true","h2_true","|R_full|","|R_both0|","|R_erase|"])
        for r in tr:
            nrm = lambda k: float(np.linalg.norm(np.asarray(r[k], float)))
            w.writerow([r["hi"], r["seed"], r["h1"], r["h2"], nrm("R_full"), nrm("R_both0"), nrm("R_erase")])
    ip = pickle.load(open(os.path.join(ROOT, RAW["causal_inplace"]), "rb"))
    with open(os.path.join(OUT, "causal_inplace.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["history","seed","h1_true","h2_true","|Rfull|","|Rboth0|"])
        for r in ip:
            nrm = lambda k: float(np.linalg.norm(np.asarray(r[k], float)))
            w.writerow([r["hi"], r["seed"], r["h1"], r["h2"], nrm("Rfull"), nrm("Rboth0")])
    return len(tr), len(ip)


def main():
    os.makedirs(OUT, exist_ok=True)
    n_hold, steps = export_holdout()
    n_tr, n_ip = export_causal()
    manifest = dict(
        note="Portable exports of committed raw results. Pickles retained for provenance.",
        raw_inputs={k: {"path": v, "sha256": _sha(os.path.join(ROOT, v))} for k, v in RAW.items()},
        holdout={"records": n_hold, "checkpoints": steps, "seeds": [38502, 38503, 38504], "histories": 12},
        exports=["holdout_longitudinal.csv", "holdout_deep_arrays.npz",
                 "causal_transplant.csv", "causal_inplace.csv"],
    )
    json.dump(manifest, open(os.path.join(OUT, "data_manifest.json"), "w"), indent=2)
    print("exported to release/data:")
    for fn in os.listdir(OUT):
        p = os.path.join(OUT, fn); print("  %-28s %6d bytes  sha256=%s" % (fn, os.path.getsize(p), _sha(p)[:12]))


if __name__ == "__main__":
    main()
