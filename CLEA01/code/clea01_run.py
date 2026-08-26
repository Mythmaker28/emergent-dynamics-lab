"""CLEA01 — run both Model C implementations, plus Model B, over a chosen split. Model A is read
from the OMLDCT02 pair measurements, which were computed and qualified in the parent mission."""
from __future__ import annotations
import json, os, sys, time
import numpy as np
REPO = os.environ.get("CLEA01_REPO", "/home/claude/edl")
sys.path.insert(0, f"{REPO}/CLEA01/code")
import clea01_lineage_i1 as I1, clea01_lineage_i2 as I2

def model_b(path, t_m):
    """AMBIENT_POPULATION: every Y-organising component after the intervention. Duration runs to Y
    extinction or the horizon; exposure is the sum of world nY over the same window."""
    z = np.load(path, allow_pickle=True)
    meta = json.loads(str(z["meta"][0])); T = int(meta["steps_executed"])
    s = z["s"]; z.close()
    nY = np.zeros(T, np.int64); ncomp = np.zeros(T, np.int64)
    for r in s:
        t = int(r[0])
        if t < T: nY[t] = int(r[1]); ncomp[t] = int(r[7])
    w = np.arange(t_m, T)
    live = nY[w] > 0
    end = int(w[live][-1]) if live.any() else t_m
    return {"AMBIENT_duration": end - t_m, "AMBIENT_exposure": int(nY[t_m:end + 1].sum()),
            "AMBIENT_mean_components": float(ncomp[t_m:end + 1].mean()) if end >= t_m else 0.0,
            "AMBIENT_terminal": "Y_EXTINCT" if end < T - 1 else "REACHED_THE_HORIZON"}

def main(split_name, out_path):
    led = [json.loads(l) for l in open(f"{REPO}/OMLDCT02/work/OMLDCT02_SEALED_LEDGER.jsonl") if l.strip()]
    by_idx = {r["index"]: r for r in led if r.get("ADMISSIBLE")}
    sm = json.load(open(f"{REPO}/CLEA01/out/CLEA01_SPLIT_MANIFEST.json"))
    want = [p["index"] for p in sm["PAIRS"] if p["SPLIT"] == split_name]
    done = {}
    if os.path.exists(out_path):
        done = {int(k): v for k, v in json.load(open(out_path)).items()}
    for i in want:
        if i in done: continue
        r = by_idx[i]; tm = r["t_m"]; dc = r["FORK"]["locked_daughter_cells"]
        rec = {"index": i, "seed": r["seed"], "t_m": tm, "root_size": len(dc)}
        for arm in ("SELECTIVE", "SHAM"):
            p = r["ARCHIVES"][arm]["path"]
            t0 = time.time(); a = I1.run(p, tm, dc); t1 = time.time(); b = I2.run(p, tm, dc); t2 = time.time()
            keys = ("CERTAIN_duration", "CERTAIN_exposure", "POSSIBLE_duration", "POSSIBLE_exposure",
                    "certain_split_rows", "yb_certain", "yb_possible", "yd_certain", "yd_possible",
                    "xb_certain", "xb_possible", "n_invariant_violations",
                    "root_all_occupied_at_t_m")
            rec[arm] = {"C_impl1": {k: a[k] for k in keys}, "C_impl2": {k: b[k] for k in keys},
                        "IMPLEMENTATIONS_AGREE": all(a[k] == b[k] for k in keys),
                        "disagreeing_keys": [k for k in keys if a[k] != b[k]],
                        "B": model_b(p, tm),
                        "seconds": {"impl1": round(t1 - t0, 1), "impl2": round(t2 - t1, 1)}}
        done[i] = rec
        tmp = out_path + ".part"
        with open(tmp, "w") as fh: json.dump(done, fh)
        os.replace(tmp, out_path)
        print(f"index {i}: agree S={rec['SELECTIVE']['IMPLEMENTATIONS_AGREE']} "
              f"H={rec['SHAM']['IMPLEMENTATIONS_AGREE']}", flush=True)
    print("done", len(done), "of", len(want))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
