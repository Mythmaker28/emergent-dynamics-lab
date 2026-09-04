"""OBTC02 gate. The scientific logic of OBTC01 is imported UNCHANGED; what is added is:

  1. a TECHNICAL VALIDITY layer, evaluated before any scientific criterion;
  2. frame-transport invariants — counts and checksums on both sides;
  3. a post-hoc aggregator written INDEPENDENTLY of the streaming one. OBTC01's two evaluators
     shared `_aggregates`, which the OBTC02 mandate rules insufficient. Here the array
     implementation computes every aggregate by its own route, from the stored arrays only, and
     shares with the streaming one nothing but the threshold spec and the final `evaluate`
     function that turns aggregates into a verdict;
  4. the cross-arm conditions DOMAIN_SIZE_INVARIANCE and CAUSAL_SOURCE_DEPENDENCE, which OBTC01
     declared in its frozen yaml with their thresholds but never reached. Implementing them
     from those already-frozen numbers is instrumentation, not redesign;
  5. the corrected third-boundary index, which reproduces the array split n//3 EXACTLY for every
     horizon rather than only for horizons divisible by three.

NO SCIENTIFIC THRESHOLD IS WRITTEN IN THIS FILE.
"""
from __future__ import annotations

import hashlib
import os

import numpy as np
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC_PATH = os.path.join(HERE, "obtc02_protocol.yaml")

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


def third_bucket(i, T):
    """0-based index of the post-burn-in step -> its third.

    This mirrors the array split literally, including its degenerate case: the array
    implementation uses third = T // 3 and the slices [0, third), [third, 2*third),
    [2*third, T), so when T < 3 the first two slices are empty and everything lands in the last
    bucket. Reproducing that exactly, rather than approximately, is what makes the two
    implementations identical BY CONSTRUCTION for every horizon instead of only for horizons
    divisible by three."""
    q = T // 3
    if q == 0:
        return 2
    return min(2, i // q)


def frame_index_sha256(steps):
    h = hashlib.sha256()
    for s in steps:
        h.update(str(int(s)).encode())
        h.update(b",")
    return h.hexdigest()


def frame_payload_sha256(frames, keys=("step", "N_X", "r80", "r80_organiser", "Rg",
                                       "organiser_to_core", "core_fraction",
                                       "main_mass_fraction", "n_eff_components",
                                       "any_winding", "centre_y", "centre_x",
                                       "organiser_y", "organiser_x")):
    h = hashlib.sha256()
    for f in frames:
        for k in keys:
            v = f.get(k)
            h.update(("%s=%.12g;" % (k, float(v)) if isinstance(v, (int, float, np.floating))
                      and not isinstance(v, bool) else "%s=%s;" % (k, v)).encode())
        h.update(b"|")
    return h.hexdigest()


# ================================================================== technical validity
def technical_validity(spec, stream, table, required_raw_present, rng_state_present,
                       run_complete, start_counter_ok, gates_agree):
    w = spec["window"]
    expected = (w["HORIZON"] - w["BURN_IN"]) // w["SAMPLE_EVERY"]
    steps_s = list(stream["steps"])
    steps_t = list(table["steps"])
    reasons = []
    if len(steps_s) == 0:
        reasons.append("zero spatial frames received by the stream")
    if len(steps_s) != expected:
        reasons.append("stream frame count %d differs from the expected %d"
                       % (len(steps_s), expected))
    if len(steps_t) != expected:
        reasons.append("table frame count %d differs from the expected %d"
                       % (len(steps_t), expected))
    if steps_s != steps_t:
        reasons.append("frame indices differ between stream and table")
    if stream["index_sha256"] != table["index_sha256"]:
        reasons.append("frame index checksum differs")
    if stream["payload_sha256"] != table["payload_sha256"]:
        reasons.append("frame payload checksum differs")
    if len(set(steps_s)) != len(steps_s):
        reasons.append("duplicated frame in the stream")
    if any(b <= a for a, b in zip(steps_s, steps_s[1:])):
        reasons.append("stream frame indices not strictly increasing")
    if not required_raw_present:
        reasons.append("a required raw field is absent")
    if not rng_state_present:
        reasons.append("RNG state absent")
    if not run_complete:
        reasons.append("run ended incomplete")
    if not start_counter_ok:
        reasons.append("start counter inconsistent")
    if not gates_agree:
        reasons.append("online and post hoc disagree")
    return {"EXPECTED_FRAME_COUNT": expected,
            "STREAM_FRAME_COUNT": len(steps_s), "TABLE_FRAME_COUNT": len(steps_t),
            "STREAM_FRAME_INDEX_SHA256": stream["index_sha256"],
            "TABLE_FRAME_INDEX_SHA256": table["index_sha256"],
            "STREAM_SPATIAL_PAYLOAD_SHA256": stream["payload_sha256"],
            "TABLE_SPATIAL_PAYLOAD_SHA256": table["payload_sha256"],
            "RUN_TECHNICALLY_VALID": len(reasons) == 0, "reasons": reasons}


# ================================================================== the scientific verdict
def evaluate(spec, agg, envelope):
    """Unchanged from OBTC01, formula for formula. Shared by both evaluators by design: the
    independence the mandate requires is in the AGGREGATION, not in the final comparison."""
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
    c["r80_organiser_frame_bound"] = float(min(r["absolute_bound"],
                                               r["domain_fraction_bound"] * agg["L"]))
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
    c["CORE_CONTINUITY"] = bool(
        agg["core_exists_frac"] >= k["core_exists_fraction_min"]
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
    c["NO_TRUE_WINDING"] = bool(
        agg["n_frames"] > 0
        and agg["n_winding"] <= g["NO_TRUE_WINDING"]["frames_with_real_winding_max"])
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
    c["PER_ARM_PASS"] = bool(all(c[x] for x in PER_ARM))
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


# ================================================================== implementation 1: STREAMING
class OnlineGate:
    """Counters only. It never holds the trajectory, and it never sees an array."""

    def __init__(self, spec, L, burn_in):
        self.s, self.L, self.burn = spec, int(L), int(burn_in)
        self.T = int(spec["window"]["T_WINDOW"])
        self.t = self.n = 0
        self.nx_sum = 0.0
        self.nx_min = None
        self.nx_above = 0
        self.third_sum = [0.0, 0.0, 0.0]
        self.third_n = [0, 0, 0]
        self.free_sum = self.occ_sum = 0.0
        self.O_first = self.O_last = None
        self.births = self.deaths = 0.0
        # frame-side counters
        self.nf = 0
        self.n_r80ok = self.n_core = self.n_wind = self.n_org = 0
        self.d2o = []
        self.r80c = []
        self.rg = []
        self.cf = []
        self.mf = []
        self.ne = []
        self.disp = []
        self._prev_centre = None
        self.frame_steps = []
        self._payload = hashlib.sha256()
        self._index = hashlib.sha256()

    def step(self, N_X, free_org, O_total, occ_frac, births, deaths):
        self.t += 1
        if self.t <= self.burn:
            return
        i = self.t - self.burn - 1
        self.n += 1
        self.nx_sum += N_X
        self.nx_min = N_X if self.nx_min is None else min(self.nx_min, N_X)
        self.nx_above += int(N_X >= self.s["gate"]["POPULATION_STATIONARY"]["N_X_min"])
        b = third_bucket(i, self.T)
        self.third_sum[b] += N_X
        self.third_n[b] += 1
        self.free_sum += free_org
        self.occ_sum += occ_frac
        if self.O_first is None:
            self.O_first = O_total
        self.O_last = O_total
        self.births += births
        self.deaths += deaths

    def frame(self, fr):
        if fr["step"] <= self.burn:
            return
        self.nf += 1
        self.frame_steps.append(int(fr["step"]))
        self._index.update(str(int(fr["step"])).encode()); self._index.update(b",")
        bound = min(self.s["gate"]["RELATIVE_LOCALIZATION"]["absolute_bound"],
                    self.s["gate"]["RELATIVE_LOCALIZATION"]["domain_fraction_bound"] * self.L)
        if np.isfinite(fr["r80_organiser"]) and fr["r80_organiser"] <= bound:
            self.n_r80ok += 1
        if np.isfinite(fr["core_fraction"]) and fr["core_fraction"] >= 0.5:
            self.n_core += 1
        if fr["any_winding"]:
            self.n_wind += 1
        if fr["organiser_y"] >= 0:
            self.n_org += 1
        for lst, key in ((self.d2o, "organiser_to_core"), (self.r80c, "r80"), (self.rg, "Rg"),
                         (self.cf, "core_fraction"), (self.mf, "main_mass_fraction"),
                         (self.ne, "n_eff_components")):
            lst.append(fr[key])
        if fr["centre_y"] >= 0:
            if self._prev_centre is not None:
                dy = min(abs(fr["centre_y"] - self._prev_centre[0]) % self.L,
                         self.L - abs(fr["centre_y"] - self._prev_centre[0]) % self.L)
                dx = min(abs(fr["centre_x"] - self._prev_centre[1]) % self.L,
                         self.L - abs(fr["centre_x"] - self._prev_centre[1]) % self.L)
                self.disp.append(float(np.hypot(dy, dx)))
            self._prev_centre = (fr["centre_y"], fr["centre_x"])

    def transport(self):
        return {"steps": list(self.frame_steps), "index_sha256": self._index.hexdigest(),
                "payload_sha256": self._payload_hex}

    def finish_payload(self, frames_seen):
        self._payload_hex = frame_payload_sha256(frames_seen)

    def aggregates(self, molecular, n3_median):
        n = max(self.n, 1)
        t1 = self.third_sum[0] / max(self.third_n[0], 1)
        t3 = self.third_sum[2] / max(self.third_n[2], 1)
        nf = max(self.nf, 1)
        med_disp = float(np.median(self.disp)) if self.disp else float("nan")
        return {
            "L": self.L, "n_steps": self.n, "n_frames": self.nf,
            "N_X_mean": self.nx_sum / n, "N_X_min": self.nx_min,
            "fraction_above_N_min": self.nx_above / n,
            "drift_thirds": abs(t3 - t1) / max(t1, 1e-9),
            "third_means": [t1, self.third_sum[1] / max(self.third_n[1], 1), t3],
            "frac_r80_org_ok": self.n_r80ok / nf if self.nf else 0.0,
            "median_core_to_org": float(np.nanmedian(self.d2o)) if self.d2o else float("nan"),
            "corr_y": molecular.get("corr_y", float("nan")),
            "corr_x": molecular.get("corr_x", float("nan")),
            "frac_with_org": self.n_org / nf if self.nf else 0.0,
            "core_exists_frac": self.n_core / nf if self.nf else 0.0,
            "median_step_displacement": med_disp,
            "disp_over_N3": (med_disp / n3_median) if (n3_median and n3_median > 0)
            else float("nan"),
            "replacements": molecular.get("replacements", float("nan")),
            "initial_still_present": molecular.get("initial_still_present", float("nan")),
            "final_born_in_window": molecular.get("final_born_in_window", float("nan")),
            "mean_free_org": self.free_sum / n, "occ_fraction": self.occ_sum / n,
            "occ_drift": abs(self.O_last - self.O_first) / max(self.O_first, 1),
            "n_winding": self.n_wind,
            "births_per_step": self.births / n, "deaths_per_step": self.deaths / n,
            "model": {"r80": float(np.nanmedian(self.r80c)) if self.r80c else float("nan"),
                      "Rg": float(np.nanmedian(self.rg)) if self.rg else float("nan"),
                      "organiser_to_core": float(np.nanmedian(self.d2o)) if self.d2o
                      else float("nan"),
                      "core_fraction": float(np.nanmedian(self.cf)) if self.cf else float("nan"),
                      "main_mass_fraction": float(np.nanmedian(self.mf)) if self.mf
                      else float("nan"),
                      "n_eff_components": float(np.nanmedian(self.ne)) if self.ne
                      else float("nan")},
        }


# ================================================================== implementation 2: ARRAY
def posthoc_aggregates(spec, L, series, F, frames, molecular, n3_median):
    """Written independently of OnlineGate: it builds every aggregate from whole arrays with
    numpy reductions, and shares no accumulator, no loop and no helper with the streaming side."""
    w = spec["window"]
    burn, T = int(w["BURN_IN"]), int(w["T_WINDOW"])
    idx = {k: F.index(k) for k in ("N_X", "free_at_org", "O_total", "accepted_births_X",
                                   "deaths_X")}
    A = series[burn:]
    NX = A[:, idx["N_X"]]
    n = len(NX)
    q = max(T // 3, 1)
    bucket = np.minimum(2, np.arange(n) // q)
    tm = [float(NX[bucket == b].mean()) if (bucket == b).any() else float("nan")
          for b in range(3)]
    O = A[:, idx["O_total"]]
    cap = spec["point"]["CAP"]
    win = [f for f in frames if f["step"] > burn]
    nf = len(win)
    def col(key):
        return np.array([f[key] for f in win], dtype=float) if nf else np.zeros(0)
    r80o, r80c, rg = col("r80_organiser"), col("r80"), col("Rg")
    d2o, cf, mf, ne = col("organiser_to_core"), col("core_fraction"), \
        col("main_mass_fraction"), col("n_eff_components")
    wd = np.array([bool(f["any_winding"]) for f in win]) if nf else np.zeros(0, bool)
    org = np.array([f["organiser_y"] >= 0 for f in win]) if nf else np.zeros(0, bool)
    bound = min(spec["gate"]["RELATIVE_LOCALIZATION"]["absolute_bound"],
                spec["gate"]["RELATIVE_LOCALIZATION"]["domain_fraction_bound"] * L)
    cy = np.array([f["centre_y"] for f in win if f["centre_y"] >= 0], dtype=float)
    cx = np.array([f["centre_x"] for f in win if f["centre_x"] >= 0], dtype=float)
    if len(cy) > 1:
        dy = np.abs(np.diff(cy)) % L
        dx = np.abs(np.diff(cx)) % L
        d = np.hypot(np.minimum(dy, L - dy), np.minimum(dx, L - dx))
        med_disp = float(np.median(d))
    else:
        med_disp = float("nan")
    return {
        "L": L, "n_steps": n, "n_frames": nf,
        "N_X_mean": float(NX.mean()), "N_X_min": float(NX.min()),
        "fraction_above_N_min": float(
            (NX >= spec["gate"]["POPULATION_STATIONARY"]["N_X_min"]).mean()),
        "drift_thirds": float(abs(tm[2] - tm[0]) / max(tm[0], 1e-9)),
        "third_means": tm,
        "frac_r80_org_ok": float(np.mean(np.nan_to_num(r80o, nan=np.inf) <= bound)) if nf else 0.0,
        "median_core_to_org": float(np.nanmedian(d2o)) if nf else float("nan"),
        "corr_y": molecular.get("corr_y", float("nan")),
        "corr_x": molecular.get("corr_x", float("nan")),
        "frac_with_org": float(org.mean()) if nf else 0.0,
        "core_exists_frac": float(np.mean(np.nan_to_num(cf, nan=-1.0) >= 0.5)) if nf else 0.0,
        "median_step_displacement": med_disp,
        "disp_over_N3": (med_disp / n3_median) if (n3_median and n3_median > 0) else float("nan"),
        "replacements": molecular.get("replacements", float("nan")),
        "initial_still_present": molecular.get("initial_still_present", float("nan")),
        "final_born_in_window": molecular.get("final_born_in_window", float("nan")),
        "mean_free_org": float(A[:, idx["free_at_org"]].mean()),
        "occ_fraction": float((O / (cap * L * L)).mean()),
        "occ_drift": float(abs(O[-1] - O[0]) / max(O[0], 1)),
        "n_winding": int(wd.sum()) if nf else 0,
        "births_per_step": float(A[:, idx["accepted_births_X"]].mean()),
        "deaths_per_step": float(A[:, idx["deaths_X"]].mean()),
        "model": {"r80": float(np.nanmedian(r80c)) if nf else float("nan"),
                  "Rg": float(np.nanmedian(rg)) if nf else float("nan"),
                  "organiser_to_core": float(np.nanmedian(d2o)) if nf else float("nan"),
                  "core_fraction": float(np.nanmedian(cf)) if nf else float("nan"),
                  "main_mass_fraction": float(np.nanmedian(mf)) if nf else float("nan"),
                  "n_eff_components": float(np.nanmedian(ne)) if nf else float("nan")},
    }


def compare(a, b, tol=1e-9):
    d = {}
    for k in sorted(set(a) | set(b)):
        x, y = a.get(k), b.get(k)
        if isinstance(x, dict) and isinstance(y, dict):
            for kk in sorted(set(x) | set(y)):
                u, v = x.get(kk), y.get(kk)
                if isinstance(u, float) and isinstance(v, float) and np.isnan(u) and np.isnan(v):
                    continue
                if isinstance(u, (int, float)) and isinstance(v, (int, float)):
                    if not (abs(u - v) <= tol):
                        d["%s.%s" % (k, kk)] = {"online": u, "posthoc": v}
                elif u != v:
                    d["%s.%s" % (k, kk)] = {"online": u, "posthoc": v}
            continue
        if isinstance(x, list) and isinstance(y, list):
            if len(x) != len(y) or any(
                    not (abs(u - v) <= tol) for u, v in zip(x, y)
                    if not (isinstance(u, float) and np.isnan(u)
                            and isinstance(v, float) and np.isnan(v))):
                d[k] = {"online": x, "posthoc": y}
            continue
        if isinstance(x, float) and isinstance(y, float) and np.isnan(x) and np.isnan(y):
            continue
        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
            if not (abs(x - y) <= tol):
                d[k] = {"online": x, "posthoc": y}
        elif x != y:
            d[k] = {"online": x, "posthoc": y}
    return {"AGREE": len(d) == 0, "differences": d}


# ================================================================== cross-arm conditions
def cross_arm(spec, arms, analytic):
    """DOMAIN_SIZE_INVARIANCE and CAUSAL_SOURCE_DEPENDENCE, from the thresholds OBTC01 froze."""
    g = spec["gate"]
    by = {}
    for a in arms:
        by.setdefault(a["condition"], []).append(a)
    out = {}

    d = g["DOMAIN_SIZE_INVARIANCE"]
    P, D = by.get("P", []), by.get("D", [])
    if P and D:
        r_small = float(np.median([a["aggregates"]["model"]["r80"] for a in P]))
        r_large = float(np.median([a["aggregates"]["model"]["r80"] for a in D]))
        rel = abs(r_large - r_small) / max(r_small, 1e-9)
        out["DOMAIN_SIZE_INVARIANCE"] = {
            "r80_small_domain": r_small, "r80_large_domain": r_large,
            "relative_difference": rel,
            "threshold": d["max_relative_difference_between_domains"],
            "rejected_alternative_value": 1.0,
            "PASS": bool(rel <= d["max_relative_difference_between_domains"])}
    else:
        out["DOMAIN_SIZE_INVARIANCE"] = {"PASS": False, "reason": "arms missing"}

    c = g["CAUSAL_SOURCE_DEPENDENCE"]
    Rr, Nn = by.get("R", []), by.get("N", [])
    lo, hi = c["source_off_e_folding_window"]
    tau = float(analytic["source_off"]["e_folding_steps"])
    rows = []
    for a in Rr:
        e = a.get("source_off", {})
        ok = (e.get("e_folding_steps") is not None
              and lo * tau <= e["e_folding_steps"] <= hi * tau
              and e.get("residual_after_5_e_foldings", 1.0) <= c["source_off_residual_max"])
        rows.append({"tag": a["tag"], **e, "PASS": bool(ok)})
    nrows = [{"tag": a["tag"], "N_X_max": a["N_X"]["max"], "N_X_final": a["N_X"]["final"],
              "PASS": bool(a["N_X"]["final"] <= 0)} for a in Nn]
    need_r = spec["protocol"]["qualification_requires"]["R_arms_showing_the_predicted_decay"]
    need_n = spec["protocol"]["qualification_requires"]["N_arms_not_maintaining"]
    out["CAUSAL_SOURCE_DEPENDENCE"] = {
        "analytic_e_folding_steps": tau, "window": [lo * tau, hi * tau],
        "R_arms": rows, "N_arms": nrows,
        "R_passing": sum(1 for r in rows if r["PASS"]), "R_required": need_r,
        "N_passing": sum(1 for r in nrows if r["PASS"]), "N_required": need_n,
        "PASS": bool(sum(1 for r in rows if r["PASS"]) >= need_r
                     and sum(1 for r in nrows if r["PASS"]) >= need_n)}
    out["CROSS_ARM_PASS"] = bool(all(out[k]["PASS"] for k in CROSS_ARM))
    return out
