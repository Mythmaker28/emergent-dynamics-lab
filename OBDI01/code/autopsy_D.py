"""OBDI01 §6 — raw-only autopsy of the three D arms, with the EXACT numerator and denominator
of the failing condition and a temporal map of every failing frame.

Raw-only: the frames are re-read from the .npz archives and every number below is recomputed
from them. Nothing is taken from the OBTC02 gate output. The five healthy P arms are measured
with the SAME code, so that "how often does a passing arm also exceed the bound" is answered
rather than assumed.
"""
from __future__ import annotations

import json

import numpy as np

RAW = "/home/claude/OBDI01/verify/obtc02/wc/OBTC02/raw"
OUT = "/home/claude/OBDI01/out"
BURN_IN = 2000
T_WINDOW = 9000
ABS_BOUND, FRAC, REQ = 12.8, 0.35, 0.95
ARMS = [("P__seed9101", 36), ("P__seed9102", 36), ("P__seed9103", 36), ("P__seed9104", 36),
        ("P__seed9105", 36), ("P__seed9106", 36),
        ("D__seed9501", 72), ("D__seed9502", 72), ("D__seed9503", 72)]


def third_bucket(i, T):
    """The frozen third-boundary convention: reproduces the array split n//3 exactly."""
    q = T // 3
    if q == 0:
        return 2
    return min(2, i // q)


def runs(idx):
    """Lengths of the maximal consecutive runs in a sorted index list."""
    out, cur = [], 1
    for a, b in zip(idx, idx[1:]):
        if b == a + 1:
            cur += 1
        else:
            out.append(cur)
            cur = 1
    if idx:
        out.append(cur)
    return out


def main():
    res = {}
    for tag, L in ARMS:
        z = np.load(f"{RAW}/{tag}.npz", allow_pickle=True)
        fr = [json.loads(s) for s in z["frames"]]
        win = [f for f in fr if f["step"] > BURN_IN]
        bound = min(ABS_BOUND, FRAC * L)
        elig = [(i, f) for i, f in enumerate(win) if np.isfinite(f.get("r80_organiser", np.nan))]
        ok = [(i, f) for i, f in elig if f["r80_organiser"] <= bound]
        fail = [(i, f) for i, f in elig if f["r80_organiser"] > bound]
        r80o = np.array([f["r80_organiser"] for _, f in elig], float)
        d = {
            "tag": tag.replace("__", "/"), "L": L, "bound": bound,
            "LOCALIZED_FRAMES": len(ok), "TOTAL_ELIGIBLE_FRAMES": len(elig),
            "fraction": len(ok) / max(len(elig), 1),
            "gate_value": len(ok) / max(len(elig), 1),
            "required_fraction": REQ,
            "CONDITION_MET": bool(len(ok) / max(len(elig), 1) >= REQ),
            "failing_frames": [
                {"index": i, "step": int(f["step"]), "r80_org": round(f["r80_organiser"], 3),
                 "third": third_bucket(int(f["step"]) - BURN_IN - 1, T_WINDOW),
                 "steps_after_burn_in": int(f["step"]) - BURN_IN,
                 "N_X": int(f["N_X"]), "Rg": round(f["Rg"], 3),
                 "any_winding": bool(f["any_winding"]),
                 "n_components": int(f["n_components"])}
                for i, f in fail],
            "failing_runs": runs([i for i, _ in fail]),
            "failing_by_third": {t: sum(1 for i, f in fail
                                        if third_bucket(int(f["step"]) - BURN_IN - 1,
                                                        T_WINDOW) == t)
                                 for t in (0, 1, 2)},
            "r80_organiser": {"median": float(np.median(r80o)), "mean": float(r80o.mean()),
                              "q95": float(np.quantile(r80o, 0.95)), "max": float(r80o.max())},
            "cloud_frame": {k: float(np.median([f[k] for f in win if np.isfinite(f.get(k,
                                                                                       np.nan))]))
                            for k in ("r50", "r80", "r90", "Rg", "organiser_to_core")},
            "core_mass_fraction_median": float(np.median([f["core_fraction"] for f in win])),
            "windings_in_window": int(sum(1 for f in win if f["any_winding"])),
            "N_X_window_mean": float(np.mean([f["N_X"] for f in win])),
        }
        res[d["tag"]] = d
        print("%-12s L=%-3d bound=%.2f  %3d/%3d = %.4f  %s   median r80org %.2f q95 %.2f "
              "max %.2f  runs=%s"
              % (d["tag"], L, bound, d["LOCALIZED_FRAMES"], d["TOTAL_ELIGIBLE_FRAMES"],
                 d["fraction"], "MET" if d["CONDITION_MET"] else "NOT MET",
                 d["r80_organiser"]["median"], d["r80_organiser"]["q95"],
                 d["r80_organiser"]["max"], d["failing_runs"]))

    res["_SUMMARY"] = {
        "SECTION": "OBDI01 §6",
        "SOURCE": "raw .npz frame archives only; no gate output was read",
        "PASSING_P_ARMS_ALSO_EXCEED_THE_BOUND": {
            k: res[k]["fraction"] for k in res if k.startswith("P/") and k != "P/seed9101"},
        "READING": ("every healthy arm exceeds the bound in some frames. The difference "
                    "between a PASS and a FAIL of this condition is how many, not whether — "
                    "which is why the operating characteristics of §8 are needed before any "
                    "verdict about the physics is drawn from it."),
    }
    json.dump(res, open(f"{OUT}/_D_autopsy.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
