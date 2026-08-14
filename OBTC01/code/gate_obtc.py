"""OBTC01 gate, two implementations, both driven by organizer_bound_cloud_protocol.yaml.

ONLINE   streaming counters, one step at a time, never holds the trajectory.
POSTHOC  array implementation, rebuilt from the stored series and frames.

The cross-arm conditions (DOMAIN_SIZE_INVARIANCE, CAUSAL_SOURCE_DEPENDENCE) are evaluated by
`cross_arm()` after all arms are run; they are not per-arm and are marked as such.

NO NUMBER IS WRITTEN IN THIS FILE.
"""
from __future__ import annotations

import hashlib
import os

import numpy as np
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC_PATH = os.path.join(HERE, "organizer_bound_cloud_protocol.yaml")

PER_ARM = ("POPULATION_STATIONARY", "RELATIVE_LOCALIZATION", "SOURCE_ATTACHMENT",
           "CORE_CONTINUITY", "MATERIAL_TURNOVER", "FREE_CAPACITY_PRESERVED",
           "NO_GLOBAL_FILLING", "NO_TRUE_WINDING", "NO_KINETIC_FREEZE",
           "MODEL_PREDICTION_COMPATIBILITY")
CROSS_ARM = ("DOMAIN_SIZE_INVARIANCE", "CAUSAL_SOURCE_DEPENDENCE")


def load(path=SPEC_PATH):
    with open(path) as f:
        return yaml.safe_load(f)


def spec_sha256(path=SPEC_PATH):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ------------------------------------------------------------------ shared evaluation
def evaluate(spec, agg, envelope):
    """`agg` holds the aggregated observables of ONE arm. Both implementations produce the same
    `agg` by different routes, and this function turns it into the verdict."""
    g = spec["gate"]
    c = {}

    p = g["POPULATION_STATIONARY"]
    c["never_zero"] = bool(agg["N_X_min"] > 0)
    c["fraction_above_N_X_min"] = agg["fraction_above_N_min"]
    c["population_level_ok"] = bool(agg["fraction_above_N_min"] >= p["fraction_above_N_X_min"])
    c["relative_drift"] = agg["drift_thirds"]
    c["drift_ok"] = bool(agg["drift_thirds"] <= p["max_relative_drift_first_to_last_third"])
    c["POPULATION_STATIONARY"] = bool(c["never_zero"] and c["population_level_ok"]
                                      and c["drift_ok"])

    r = g["RELATIVE_LOCALIZATION"]
    bound = min(r["absolute_bound"], r["domain_fraction_bound"] * agg["L"])
    c["r80_organiser_frame_bound"] = float(bound)
    c["fraction_r80_org_within_bound"] = agg["frac_r80_org_ok"]
    c["RELATIVE_LOCALIZATION"] = bool(agg["frac_r80_org_ok"] >= r["fraction_of_frames_required"])

    s = g["SOURCE_ATTACHMENT"]
    c["median_core_to_organiser"] = agg["median_core_to_org"]
    c["unwrapped_correlation_y"] = agg["corr_y"]
    c["unwrapped_correlation_x"] = agg["corr_x"]
    c["fraction_frames_with_organiser"] = agg["frac_with_org"]
    c["SOURCE_ATTACHMENT"] = bool(
        agg["median_core_to_org"] <= s["median_core_to_organiser_max"]
        and min(agg["corr_y"], agg["corr_x"]) >= s["unwrapped_position_correlation_min"]
        and agg["frac_with_org"] >= s["fraction_of_frames_with_an_organiser"])

    k = g["CORE_CONTINUITY"]
    c["core_exists_fraction"] = agg["core_exists_frac"]
    c["median_step_displacement_over_N3"] = agg["disp_over_N3"]
    c["CORE_CONTINUITY"] = bool(agg["core_exists_frac"] >= k["core_exists_fraction_min"]
                                and agg["disp_over_N3"] <= k["max_median_step_displacement_over_N3"])

    t = g["MATERIAL_TURNOVER"]
    c["replacements"] = agg["replacements"]
    c["initial_units_still_present"] = agg["initial_still_present"]
    c["final_units_born_in_window"] = agg["final_born_in_window"]
    c["MATERIAL_TURNOVER"] = bool(
        agg["replacements"] >= t["replacements_min"]
        and agg["initial_still_present"] <= t["fraction_of_initial_units_still_present_max"]
        and agg["final_born_in_window"] >= t["fraction_of_final_units_born_in_window_min"])

    c["mean_free_at_organiser"] = agg["mean_free_org"]
    c["FREE_CAPACITY_PRESERVED"] = bool(
        agg["mean_free_org"] >= g["FREE_CAPACITY_PRESERVED"]["mean_free_at_organiser_min"])

    f = g["NO_GLOBAL_FILLING"]
    c["mean_occupancy_fraction"] = agg["occ_fraction"]
    c["occupancy_drift"] = agg["occ_drift"]
    c["NO_GLOBAL_FILLING"] = bool(agg["occ_fraction"] <= f["mean_occupancy_fraction_max"]
                                  and agg["occ_drift"] <= f["occupancy_drift_max"])

    c["frames_with_real_winding"] = agg["n_winding"]
    c["NO_TRUE_WINDING"] = bool(agg["n_winding"] <= g["NO_TRUE_WINDING"]
                                ["frames_with_real_winding_max"])

    kf = g["NO_KINETIC_FREEZE"]
    c["mean_births_per_step"] = agg["births_per_step"]
    c["mean_deaths_per_step"] = agg["deaths_per_step"]
    c["NO_KINETIC_FREEZE"] = bool(agg["births_per_step"] >= kf["mean_births_per_step_min"]
                                  and agg["deaths_per_step"] >= kf["mean_deaths_per_step_min"])

    m = g["MODEL_PREDICTION_COMPATIBILITY"]
    inside, detail = 0, {}
    for st in m["statistics"]:
        lo, hi = envelope.get(st, (None, None))
        v = agg["model"][st]
        ok = bool(lo is not None and np.isfinite(v) and lo <= v <= hi)
        detail[st] = {"observed": v, "envelope": [lo, hi], "inside": ok}
        inside += int(ok)
    c["model_statistics_inside_envelope"] = inside
    c["model_detail"] = detail
    c["MODEL_PREDICTION_COMPATIBILITY"] = bool(inside >= m["min_statistics_inside_envelope"])

    c["PER_ARM_PASS"] = bool(all(c[k_] for k_ in PER_ARM))
    return c


def classify(c):
    if c["PER_ARM_PASS"]:
        return "ORGANIZER_BOUND_CLOUD_ARM_PASS"
    if not c["never_zero"]:
        return "EXTINCT"
    if not c["NO_TRUE_WINDING"]:
        return "TRUE_WINDING"
    if not c["NO_GLOBAL_FILLING"]:
        return "GLOBAL_FILLING"
    if not c["NO_KINETIC_FREEZE"]:
        return "KINETIC_FREEZE"
    if not c["RELATIVE_LOCALIZATION"]:
        return "NOT_BOUNDED_RELATIVE_TO_THE_SOURCE"
    if not c["SOURCE_ATTACHMENT"]:
        return "SOURCE_DETACHED"
    if not c["MATERIAL_TURNOVER"]:
        return "NO_TURNOVER"
    if not c["CORE_CONTINUITY"]:
        return "CORE_DISCONTINUOUS"
    if not c["POPULATION_STATIONARY"]:
        return "POPULATION_NOT_STATIONARY"
    if not c["FREE_CAPACITY_PRESERVED"]:
        return "FREE_CAPACITY_COLLAPSED"
    if not c["MODEL_PREDICTION_COMPATIBILITY"]:
        return "MODEL_INCOMPATIBLE"
    return "UNCLASSIFIABLE"


# ------------------------------------------------------------------ implementation 1: online
class OnlineGate:
    """Streaming. Keeps counters and the small per-frame summaries the aggregates need."""

    def __init__(self, spec, L, burn_in):
        self.s = spec
        self.L = int(L)
        self.burn = int(burn_in)
        self.t = 0
        self.n = 0
        self.nx_sum = self.nx_min = None
        self.nx_above = 0
        self.thirds = [[], [], []]
        self.free_sum = 0.0
        self.occ_sum = 0.0
        self.O_first = self.O_last = None
        self.births = 0.0
        self.deaths = 0.0
        self.frames = []

    def step(self, N_X, free_org, O_total, occ_frac, births, deaths):
        self.t += 1
        if self.t <= self.burn:
            return
        self.n += 1
        self.nx_sum = (self.nx_sum or 0.0) + N_X
        self.nx_min = N_X if self.nx_min is None else min(self.nx_min, N_X)
        self.nx_above += int(N_X >= self.s["gate"]["POPULATION_STATIONARY"]["N_X_min"])
        # BUG D-3 of this mission: the index must be 0-based, exactly as the array
        # implementation's n//3 split is, or the two disagree on the bucket boundaries
        self.thirds[min(2, (self.t - self.burn - 1) * 3 // max(
            self.s["window"]["T_WINDOW"], 1))].append(N_X)
        self.free_sum += free_org
        self.occ_sum += occ_frac
        if self.O_first is None:
            self.O_first = O_total
        self.O_last = O_total
        self.births += births
        self.deaths += deaths

    def frame(self, fr):
        if fr["step"] > self.burn:
            self.frames.append(fr)

    def aggregates(self, molecular, n3_median, envelope_nx):
        return _aggregates(self.s, self.L, self.n, self.nx_sum, self.nx_min, self.nx_above,
                           self.thirds, self.free_sum, self.occ_sum, self.O_first, self.O_last,
                           self.births, self.deaths, self.frames, molecular, n3_median)


# ------------------------------------------------------------------ implementation 2: posthoc
def posthoc_aggregates(spec, L, series, F, frames, molecular, n3_median):
    burn = int(spec["window"]["BURN_IN"])
    col = lambda k: series[:, F.index(k)]
    NX = col("N_X")[burn:]
    FR = col("free_at_org")[burn:]
    O = col("O_total")[burn:]
    BI = col("accepted_births_X")[burn:]
    DE = col("deaths_X")[burn:]
    cap = spec["point"]["CAP"]
    occf = O / (cap * L * L)
    n = len(NX)
    third = n // 3
    thirds = [list(NX[:third]), list(NX[third:2 * third]), list(NX[2 * third:])]
    win = [f for f in frames if f["step"] > burn]
    return _aggregates(spec, L, n, float(NX.sum()), float(NX.min()),
                       int((NX >= spec["gate"]["POPULATION_STATIONARY"]["N_X_min"]).sum()),
                       thirds, float(FR.sum()), float(occf.sum()), float(O[0]), float(O[-1]),
                       float(BI.sum()), float(DE.sum()), win, molecular, n3_median)


# ------------------------------------------------------------------ the common aggregator
def _aggregates(spec, L, n, nx_sum, nx_min, nx_above, thirds, free_sum, occ_sum,
                O_first, O_last, births, deaths, frames, molecular, n3_median):
    g = spec["gate"]
    r = g["RELATIVE_LOCALIZATION"]
    bound = min(r["absolute_bound"], r["domain_fraction_bound"] * L)
    n = max(n, 1)
    mean_nx = nx_sum / n
    t1 = float(np.mean(thirds[0])) if thirds[0] else float("nan")
    t3 = float(np.mean(thirds[2])) if thirds[2] else float("nan")
    drift = abs(t3 - t1) / max(t1, 1e-9)
    r80o = np.array([f["r80_organiser"] for f in frames], float)
    r80c = np.array([f["r80"] for f in frames], float)
    rg = np.array([f["Rg"] for f in frames], float)
    d2o = np.array([f["organiser_to_core"] for f in frames], float)
    cf = np.array([f["core_fraction"] for f in frames], float)
    mf = np.array([f["main_mass_fraction"] for f in frames], float)
    ne = np.array([f["n_eff_components"] for f in frames], float)
    wd = np.array([bool(f["any_winding"]) for f in frames])
    has_org = np.array([f["organiser_y"] >= 0 for f in frames])
    cen = [(f["centre_y"], f["centre_x"]) for f in frames if f["centre_y"] >= 0]
    disp = []
    for a, b in zip(cen, cen[1:]):
        dy = min(abs(a[0] - b[0]) % L, L - abs(a[0] - b[0]) % L)
        dx = min(abs(a[1] - b[1]) % L, L - abs(a[1] - b[1]) % L)
        disp.append(float(np.hypot(dy, dx)))
    med_disp = float(np.median(disp)) if disp else float("nan")
    return {
        "L": L, "n_steps": n, "N_X_mean": mean_nx, "N_X_min": nx_min,
        "fraction_above_N_min": nx_above / n, "drift_thirds": drift,
        "third_means": [t1, float(np.mean(thirds[1])) if thirds[1] else float("nan"), t3],
        "frac_r80_org_ok": float(np.mean(r80o <= bound)) if len(r80o) else 0.0,
        "median_core_to_org": float(np.nanmedian(d2o)) if len(d2o) else float("nan"),
        "corr_y": molecular.get("corr_y", float("nan")),
        "corr_x": molecular.get("corr_x", float("nan")),
        "frac_with_org": float(np.mean(has_org)) if len(has_org) else 0.0,
        "core_exists_frac": float(np.mean(cf >= 0.5)) if len(cf) else 0.0,
        "median_step_displacement": med_disp,
        "disp_over_N3": (med_disp / n3_median) if (n3_median and n3_median > 0) else float("nan"),
        "replacements": molecular.get("replacements", float("nan")),
        "initial_still_present": molecular.get("initial_still_present", float("nan")),
        "final_born_in_window": molecular.get("final_born_in_window", float("nan")),
        "mean_free_org": free_sum / n, "occ_fraction": occ_sum / n,
        "occ_drift": abs(O_last - O_first) / max(O_first, 1),
        "n_winding": int(wd.sum()) if len(wd) else 0,
        "births_per_step": births / n, "deaths_per_step": deaths / n,
        "model": {"r80": float(np.nanmedian(r80c)) if len(r80c) else float("nan"),
                  "Rg": float(np.nanmedian(rg)) if len(rg) else float("nan"),
                  "organiser_to_core": float(np.nanmedian(d2o)) if len(d2o) else float("nan"),
                  "core_fraction": float(np.nanmedian(cf)) if len(cf) else float("nan"),
                  "main_mass_fraction": float(np.nanmedian(mf)) if len(mf) else float("nan"),
                  "n_eff_components": float(np.nanmedian(ne)) if len(ne) else float("nan")},
    }


def compare(a, b):
    d = {}
    for k in sorted(set(a) | set(b)):
        x, y = a.get(k), b.get(k)
        if isinstance(x, dict) or isinstance(y, dict):
            continue
        same = (abs(x - y) < 1e-9) if (isinstance(x, (int, float))
                                       and isinstance(y, (int, float))
                                       and np.isfinite(x) and np.isfinite(y)) else (x == y)
        if isinstance(x, float) and isinstance(y, float) and np.isnan(x) and np.isnan(y):
            same = True
        if not same:
            d[k] = {"online": x, "posthoc": y}
    return {"AGREE": len(d) == 0, "differences": d}
