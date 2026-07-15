"""PRIMARY reproduction: longitudinal certification of the IsingV3 organizational-memory paper.

Deterministic. Reads ONLY committed raw data (results/observer/tca_holdout_raw.pkl). No new physics,
no new simulation. Regenerates: track survival, M trajectory, h1 deep decode + CI (certification),
h2 longitudinal decode + CI (not-established check), the primary figure and the primary table, and a
manifest of input/output SHA-256 hashes.

Usage:
    python -m reproduction.primary            # run and write outputs
    python -m reproduction.primary --check    # also assert outputs match reproduction/EXPECTED.json

Exits non-zero with a clear message if a dependency or data file is missing, or (in --check mode) if a
reproduced value falls outside the announced tolerance.
"""
from __future__ import annotations
import os, sys, json, hashlib, pickle, argparse

THRESHOLD = 0.50                      # certification threshold on held-out R^2
CHECKPOINTS = [(0, "init"), (400, "moderate"), (650, "deep-1"), (800, "deep")]
DEEP_STEP = 800
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(REPO_ROOT, "results", "observer", "tca_holdout_raw.pkl")
OUTDIR = os.environ.get("REPRO_OUT", os.path.join(REPO_ROOT, "reproduction", "outputs"))
TOL_POINT = 0.06                      # tolerance on R^2 point estimates for --check
TOL_CI = 0.08                         # tolerance on CI bounds for --check


def _die(msg, code=2):
    sys.stderr.write("REPRODUCTION FAILURE: " + msg + "\n")
    sys.exit(code)


def _require_deps():
    missing = []
    try:
        import numpy  # noqa
    except Exception:
        missing.append("numpy")
    try:
        import matplotlib  # noqa
    except Exception:
        missing.append("matplotlib")
    if missing:
        _die("missing required dependency/dependencies: " + ", ".join(missing) +
             ". Install from requirements-lock.txt (pip install -r requirements-lock.txt).")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_records():
    if not os.path.isfile(RAW):
        _die("required raw data not found: " + RAW +
             "  (expected committed file results/observer/tca_holdout_raw.pkl).")
    with open(RAW, "rb") as f:
        d = pickle.load(f)
    if not isinstance(d, list) or not d:
        _die("raw data has unexpected structure (expected non-empty list).")
    return d


def build_Xy(records, step, coord):
    import numpy as np
    from .decode import features_from_long
    X, y, g, M = [], [], [], []
    for r in records:
        ck = r["ck"][step]
        X.append(features_from_long(ck["long"]))
        y.append(r[coord]); g.append(r["hi"]); M.append(float(ck["long"][1]))
    return np.asarray(X), np.asarray(y, float), np.asarray(g), float(np.mean(M))


def main(argv=None):
    _require_deps()
    import numpy as np
    from . import decode as DEC
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="assert outputs match reproduction/EXPECTED.json")
    args = ap.parse_args(argv)

    os.makedirs(OUTDIR, exist_ok=True)
    records = load_records()
    seeds = sorted(set(r["seed"] for r in records))
    histories = sorted(set(r["hi"] for r in records))
    n = len(records)

    # --- track survival / switches / M (raw, fully reproducible) ---
    switches = sum(int(r.get("switch", 0)) for r in records)
    lost = sum(1 for r in records if r.get("lost", False))
    survival = n - lost

    rows = []            # primary table rows
    per_ckpt = {}
    for step, label in CHECKPOINTS:
        rec = {}
        for coord in ("h1", "h2"):
            X, y, g, meanM = build_Xy(records, step, coord)
            point = DEC.decode_r2(X, y, g)
            lo, med, hi = DEC.bootstrap_ci(X, y, g)
            rec[coord] = dict(point=point, ci_lo=lo, ci_hi=hi, meanM=meanM)
        per_ckpt[label] = rec
        rows.append((label, rec["h1"]["meanM"], rec["h1"]["point"], rec["h1"]["ci_lo"], rec["h1"]["ci_hi"],
                     rec["h2"]["point"], rec["h2"]["ci_lo"], rec["h2"]["ci_hi"]))

    deep = per_ckpt["deep"]
    h1_certified = deep["h1"]["ci_lo"] > THRESHOLD
    h2_not_established = not (deep["h2"]["ci_lo"] > THRESHOLD)   # not established unless lower bound clears

    # --- write primary table CSV ---
    csv_path = os.path.join(OUTDIR, "primary_table.csv")
    with open(csv_path, "w") as f:
        f.write("checkpoint,mean_M,h1_R2,h1_ci_lo,h1_ci_hi,h2_R2,h2_ci_lo,h2_ci_hi\n")
        for r in rows:
            f.write("%s,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f\n" % r)

    # --- write NPZ arrays (deep features + coords) ---
    Xd, yd1, gd, _ = build_Xy(records, DEEP_STEP, "h1")
    _, yd2, _, _ = build_Xy(records, DEEP_STEP, "h2")
    npz_path = os.path.join(OUTDIR, "primary_arrays.npz")
    np.savez(npz_path, deep_features=Xd, h1_true=yd1, h2_true=yd2, history=gd,
             seeds=np.array(seeds), checkpoints=np.array([s for s, _ in CHECKPOINTS]))

    # --- figure ---
    fig_path = os.path.join(OUTDIR, "primary_figure.png")
    _make_figure(per_ckpt, fig_path)

    # --- results JSON + manifest (hashes/seeds/gates) ---
    results = dict(
        package="reproduction", version="1.0.0-rc", deterministic=True,
        decoder=dict(kind="grouped-leave-one-history-out ridge", ridge_lambda=DEC.RIDGE_LAMBDA,
                     features="10-D memory order-stats [mean,std,p10,p50,p90] of (m1,m2) + mminus_std",
                     n_boot=DEC.N_BOOT, boot_seed=DEC.BOOT_SEED, ci="donor-level percentile 95%"),
        data=dict(raw=os.path.relpath(RAW, REPO_ROOT), sha256=_sha256(RAW),
                  n_records=n, seeds=seeds, n_histories=len(histories)),
        track_survival=dict(survived=survival, total=n, switches=switches, lost=lost),
        checkpoints=per_ckpt,
        gates=dict(threshold=THRESHOLD,
                   h1_deep_certified=bool(h1_certified),
                   h1_deep=dict(point=deep["h1"]["point"], ci=[deep["h1"]["ci_lo"], deep["h1"]["ci_hi"]]),
                   h2_deep_not_established=bool(h2_not_established),
                   h2_deep=dict(point=deep["h2"]["point"], ci=[deep["h2"]["ci_lo"], deep["h2"]["ci_hi"]])),
    )
    res_path = os.path.join(OUTDIR, "primary_results.json")
    with open(res_path, "w") as f:
        json.dump(results, f, indent=2)

    outputs = {os.path.basename(p): _sha256(p) for p in (csv_path, npz_path, fig_path, res_path)}
    manifest = dict(inputs={os.path.relpath(RAW, REPO_ROOT): _sha256(RAW)},
                    outputs=outputs, gates=results["gates"])
    with open(os.path.join(OUTDIR, "primary_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    # --- report ---
    print("=" * 72)
    print("IsingV3 PRIMARY REPRODUCTION  (deterministic, committed data only)")
    print("=" * 72)
    print("raw: %s\n  sha256=%s" % (os.path.relpath(RAW, REPO_ROOT), manifest["inputs"][os.path.relpath(RAW, REPO_ROOT)][:16] + "..."))
    print("records=%d  seeds=%s  histories=%d" % (n, seeds, len(histories)))
    print("track survival: %d/%d  switches=%d  lost=%d" % (survival, n, switches, lost))
    print("-" * 72)
    print("%-10s %6s | %-26s | %-26s" % ("ckpt", "meanM", "h1 R^2 [95% CI]", "h2 R^2 [95% CI]"))
    for label, _, h1p, h1lo, h1hi, h2p, h2lo, h2hi in rows:
        print("%-10s %6.3f | %+0.3f [%+0.3f,%+0.3f]      | %+0.3f [%+0.3f,%+0.3f]"
              % (label, per_ckpt[label]["h1"]["meanM"], h1p, h1lo, h1hi, h2p, h2lo, h2hi))
    print("-" * 72)
    print("GATE h1 deep-turnover CERTIFIED (CI lower bound > %.2f): %s  (lo=%.3f)"
          % (THRESHOLD, h1_certified, deep["h1"]["ci_lo"]))
    print("GATE h2 deep-turnover NOT ESTABLISHED (CI does not clear %.2f): %s  (point=%.3f, hi=%.3f)"
          % (THRESHOLD, h2_not_established, deep["h2"]["point"], deep["h2"]["ci_hi"]))
    print("outputs -> %s" % os.path.relpath(OUTDIR, REPO_ROOT))
    for k, v in outputs.items():
        print("   %-22s sha256=%s" % (k, v[:16] + "..."))

    # hard scientific guard: the load-bearing conclusions must hold
    if not h1_certified:
        _die("h1 deep-turnover certification did NOT reproduce (CI lower bound <= %.2f)." % THRESHOLD, 3)
    if not h2_not_established:
        _die("h2 deep-turnover unexpectedly cleared the threshold; manuscript says not established.", 3)

    if args.check:
        _run_check(results)
    print("\nPRIMARY REPRODUCTION: OK (conclusions reproduced).")
    return 0


def _make_figure(per_ckpt, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    order = ["init", "moderate", "deep-1", "deep"]
    M = [per_ckpt[k]["h1"]["meanM"] for k in order]
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, coord, title in ((axL, "h1", "$h_1$ (cumulative dose): retained -> CERTIFIED"),
                             (axR, "h2", "$h_2$ (order): deep retention NOT ESTABLISHED")):
        pt = [per_ckpt[k][coord]["point"] for k in order]
        lo = [per_ckpt[k][coord]["ci_lo"] for k in order]
        hi = [per_ckpt[k][coord]["ci_hi"] for k in order]
        import numpy as np
        yerr = np.vstack([np.array(pt) - np.array(lo), np.array(hi) - np.array(pt)])
        col = "#1f6f3d" if coord == "h1" else "#b02418"
        if coord == "h2":
            axR.axhspan(-1.2, THRESHOLD, color="#f2c2c2", alpha=0.35, zorder=0)
        ax.errorbar(M, pt, yerr=yerr, fmt="o-", color=col, lw=2, ms=7, capsize=5)
        ax.axhline(THRESHOLD, ls="--", color="0.4", lw=1.2)
        ax.text(0.62, THRESHOLD + 0.02, "0.50 threshold", color="0.35", fontsize=8)
        ax.set_xlim(1.06, 0.10); ax.set_ylim(-1.2, 1.08)
        ax.set_xlabel("surviving original-material fraction $M$"); ax.set_ylabel("held-out $R^2$")
        ax.set_title(title, fontsize=10.5)
    fig.suptitle("Primary reproduction (deterministic, committed data)", fontsize=11, y=1.0)
    plt.tight_layout(); plt.savefig(path, dpi=150, bbox_inches="tight"); plt.close(fig)


def _run_check(results):
    exp_path = os.path.join(REPO_ROOT, "reproduction", "EXPECTED.json")
    if not os.path.isfile(exp_path):
        _die("--check requested but reproduction/EXPECTED.json is missing.")
    with open(exp_path) as f:
        exp = json.load(f)
    bad = []
    for label, rec in results["checkpoints"].items():
        for coord in ("h1", "h2"):
            e = exp["checkpoints"][label][coord]
            g = rec[coord]
            if abs(g["point"] - e["point"]) > TOL_POINT:
                bad.append("%s/%s point %.3f vs %.3f" % (label, coord, g["point"], e["point"]))
            if abs(g["ci_lo"] - e["ci_lo"]) > TOL_CI or abs(g["ci_hi"] - e["ci_hi"]) > TOL_CI:
                bad.append("%s/%s CI [%.3f,%.3f] vs [%.3f,%.3f]" %
                           (label, coord, g["ci_lo"], g["ci_hi"], e["ci_lo"], e["ci_hi"]))
    if bad:
        _die("--check FAILED (outside tolerance):\n  " + "\n  ".join(bad), 4)
    print("--check: OK (all values within tolerance point=%.2f ci=%.2f)." % (TOL_POINT, TOL_CI))


if __name__ == "__main__":
    sys.exit(main())
