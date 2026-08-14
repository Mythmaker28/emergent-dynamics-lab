"""CSC01 gate, in TWO implementations, both driven by `localization_gate.yaml`.

  ONLINE    streaming. Sees one step at a time and keeps counters. Never holds the trajectory
            as an array. This is what runs during an arm.
  POSTHOC   array. Reads the stored series and the stored frames back and recomputes the whole
            classification from scratch.

WHAT IS AND IS NOT INDEPENDENT — stated plainly rather than claimed. Axes 2, 3 and 4 and the
classification are written twice, against different data structures, and must agree. The
cohesion sub-test of axis 1 is by construction NOT streamable: it needs the whole birth history
and the whole organiser trajectory before it can draw a single null. Both implementations
therefore call the SAME function for it, with the same deterministic null seed, and that
sub-test is covered by the integrity tests rather than by redundancy.

NO THRESHOLD IS WRITTEN IN THIS FILE. Every number comes from the yaml.
"""
from __future__ import annotations

import os

import numpy as np
import yaml

import null_n3b as NB
import nulls as NU

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SPEC = os.path.join(HERE, "localization_gate.yaml")


def load(path=DEFAULT_SPEC):
    with open(path) as f:
        return yaml.safe_load(f)


def spec_sha256(path=DEFAULT_SPEC):
    import hashlib
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ==================================================================== shared sub-tests
N1_GRID = (2, 5, 10, 20, 40, 60, 80, 100, 130, 170, 220, 300, 400, 600)
N1_DRAWS = 300
N1_SEED = 20260814
N1_CACHE = os.path.join(HERE, "_n1_table.json")


def n1_table(spec, path=N1_CACHE):
    """q01 of r80 under complete spatial randomness, as a function of N_X.

    Computed ONCE on a declared grid with a declared seed, cached, and shared by both gate
    implementations so that neither can drift from the other. Linear interpolation between grid
    points; constant extrapolation outside."""
    import json
    if os.path.exists(path):
        d = json.load(open(path))
        if d.get("grid") == list(N1_GRID) and d.get("draws") == N1_DRAWS \
                and d.get("seed") == N1_SEED and d.get("L") == spec["geometry"]["L"]:
            return d
    g = spec["geometry"]
    q = spec["axes"]["axis_1_compact_and_cohesive"]["compact_vs_N1"]["null_quantile"]
    vals = []
    for i, n in enumerate(N1_GRID):
        d = NU.null_distribution("N1", N1_DRAWS, N1_SEED + i, g["L"], g["ell_X_reference"],
                                 N_X=int(n), cap=g["CAP"])
        v = d["r80"][np.isfinite(d["r80"])]
        vals.append(float(np.quantile(v, q)))
    out = {"grid": list(N1_GRID), "q01_r80": vals, "draws": N1_DRAWS, "seed": N1_SEED,
           "L": g["L"], "quantile": q}
    json.dump(out, open(path, "w"), indent=1)
    return out


def n1_q01_r80(table, N_X):
    return float(np.interp(float(N_X), table["grid"], table["q01_r80"]))


def cohesion_subtest(spec, frames, births, seed, mu):
    """Axis 1, cohesion limb. Identical code for both implementations, by construction."""
    g = spec["geometry"]
    a1 = spec["axes"]["axis_1_compact_and_cohesive"]
    cfg, n3b = a1["cohesive_vs_N3b"], a1["n3b"]
    ft = [f for f in frames if f["organiser_y"] >= 0 and f["N_X"] > 0]
    if len(ft) < n3b["instants"]:
        return {"applicable": False, "fraction_below_null_q": 0.0, "instants": 0,
                "per_instant": []}
    org_steps = np.array([f["step"] for f in ft], dtype=np.int64)
    org_traj = np.array([[f["organiser_y"], f["organiser_x"]] for f in ft], dtype=np.int64)
    idxs = np.linspace(0, len(ft) - 1, n3b["instants"]).astype(int)
    rng_base = int(seed) * 7919
    below, per = 0, []
    for j, i in enumerate(idxs):
        f = ft[i]
        dist = NB.n3b_distribution(n3b["draws"], rng_base + j, g["L"], g["ell_X_reference"],
                                   N_X=int(f["N_X"]), t=int(f["step"]), births=births,
                                   org_traj=org_traj, org_steps=org_steps,
                                   p_hop=spec["_p_hop"], mu=mu)
        if not dist:
            continue
        v = dist["r80"][np.isfinite(dist["r80"])]
        if v.size == 0:
            continue
        q = float(np.quantile(v, cfg["null_quantile"]))
        ok = bool(f["r80"] < q)
        below += int(ok)
        per.append({"step": int(f["step"]), "N_X": int(f["N_X"]), "r80": float(f["r80"]),
                    "null_q": q, "null_median": float(np.median(v)),
                    "observed_position": float((v <= f["r80"]).mean()), "below": ok})
    n = len(per)
    return {"applicable": n > 0, "instants": n,
            "fraction_below_null_q": (below / n) if n else 0.0, "per_instant": per}


# ==================================================================== classification
def classify(spec, flags):
    for key, cls in spec["classification_order"]:
        if key == "otherwise":
            return cls
        if flags.get(key, False):
            return cls
    return "UNCLASSIFIABLE"


def build_flags(spec, c):
    """Turn the raw checks into the exclusive predicates the classification order consumes."""
    a2 = spec["axes"]["axis_2_durable"]
    del a2
    axes_ok = all(c["axis_%d" % i] for i in (1, 2, 3, 4))
    return {
        "no_formation": c.get("no_formation", False),
        "transient_no_window": c.get("window_truncated", False),
        "all_axes": axes_ok,
        "score_reading": not c["no_score_reading"],
        "winding": not c["no_true_winding"],
        "occupancy": (not c["occupancy_stable"]) or (not c["free_capacity_at_organiser_ok"]),
        "no_organiser": not c["organiser_present_throughout"],
        "extinct": not c["never_extinct"],
        "not_durable": not (c["fraction_ok"] and c["excursion_ok"] and c["core_exists_ok"]),
        "not_live": not (c["turnover_ok"] and c["core_free_capacity_ok"]),
        "not_compact": not c["compact_vs_N1_ok"],
        "not_cohesive": not c["cohesive_vs_N3b_ok"],
    }


def assemble(spec, c):
    a1 = spec["axes"]["axis_1_compact_and_cohesive"]
    c["axis_1"] = bool(c["compact_vs_N1_ok"] and c["cohesive_vs_N3b_ok"])
    c["axis_2"] = bool(c["never_extinct"] and c["organiser_present_throughout"] and
                       c["fraction_ok"] and c["excursion_ok"] and c["core_exists_ok"])
    c["axis_3"] = bool(c["turnover_ok"] and c["core_free_capacity_ok"])
    c["axis_4"] = bool(c["no_true_winding"] and c["occupancy_stable"] and
                       c["free_capacity_at_organiser_ok"] and c["no_score_reading"])
    del a1
    flags = build_flags(spec, c)
    return {"PASS": bool(c["axis_1"] and c["axis_2"] and c["axis_3"] and c["axis_4"]),
            "classification": classify(spec, flags), "checks": c, "flags": flags}


# ==================================================================== implementation 1: online
class OnlineGate:
    """Streaming. Counters only for axes 2, 3, 4; a small buffer for the axis-1 sub-tests."""

    def __init__(self, spec, seed, no_score_reading=True):
        self.s = spec
        self.seed = int(seed)
        self.no_score_reading = bool(no_score_reading)
        w = spec["window"]
        self.T_FORM_MAX, self.N_FORM = w["T_FORM_MAX"], w["N_FORM"]
        self.U_FORM, self.K_FORM = w["U_FORM"], w["K_FORM"]
        self.T_MAINT = w["T_MAINT"]
        a2 = spec["axes"]["axis_2_durable"]
        self.N_KEEP, self.FRAC_MIN, self.RUN_MAX = a2["N_KEEP"], a2["FRAC_MIN"], a2["RUN_MAX"]
        self.t = 0
        self.form_run = 0
        self.formed_at = None
        self.n_win = 0
        self.n_ok = 0
        self.below_run = self.below_max = 0
        self.ever_zero = self.ever_no_org = False
        self.NX_max = 0.0
        self.O_first = self.O_last = None
        self.free_org_sum = 0.0
        self.deaths = 0.0
        self.NX_sum = 0.0
        self.frames = []
        self.births = []
        self.n_frames = 0
        self.n_frames_compact = 0
        self.n_frames_core = 0
        self.n_frames_wind = 0
        self.core_free_sum = 0.0
        self.core_free_n = 0

    def step(self, N_X, N_Y, u, free_at_org, O_total, deaths_X, births_X):
        self.t += 1
        self.births.append(float(births_X))
        self.NX_max = max(self.NX_max, N_X)
        if self.formed_at is None:
            self.form_run = self.form_run + 1 if (N_X >= self.N_FORM and u >= self.U_FORM) else 0
            if self.form_run >= self.K_FORM:
                self.formed_at = self.t
            elif self.t >= self.T_FORM_MAX:
                self.formed_at = -1
            return
        if self.formed_at < 0 or self.n_win >= self.T_MAINT:
            return
        self.n_win += 1
        if self.O_first is None:
            self.O_first = O_total
        self.O_last = O_total
        self.ever_zero |= (N_X <= 0)
        self.ever_no_org |= (N_Y < 1)
        if N_X >= self.N_KEEP:
            self.n_ok += 1
            self.below_run = 0
        else:
            self.below_run += 1
            self.below_max = max(self.below_max, self.below_run)
        self.free_org_sum += free_at_org
        self.deaths += float(deaths_X)
        self.NX_sum += float(N_X)

    def frame(self, fr, n1_thr, core_free_mean):
        """One spatial frame. `n1_thr` is the N1 r80 threshold for this frame's N_X."""
        if self.formed_at is None or self.formed_at < 0:
            return
        # the window is [formed_at, formed_at + T_MAINT), by step number: exactly the bound the
        # array implementation applies. Counting by the streaming n_win counter instead would
        # keep counting frames after the window has closed (adversarial case A11).
        if not (self.formed_at <= fr["step"] < self.formed_at + self.T_MAINT):
            return
        self.n_frames += 1
        if np.isfinite(fr["r80"]) and fr["r80"] <= n1_thr:
            self.n_frames_compact += 1
        cm = self.s["axes"]["axis_2_durable"]["core_mass_fraction_min"]
        if np.isfinite(fr["core_fraction"]) and fr["core_fraction"] >= cm:
            self.n_frames_core += 1
        if fr["any_component_wraps"]:
            self.n_frames_wind += 1
        if np.isfinite(core_free_mean):
            self.core_free_sum += core_free_mean
            self.core_free_n += 1
        self.frames.append(fr)

    def result(self):
        s, a2 = self.s, self.s["axes"]["axis_2_durable"]
        a3, a4 = s["axes"]["axis_3_live_not_frozen"], s["axes"]["axis_4_not_an_artefact"]
        a1 = s["axes"]["axis_1_compact_and_cohesive"]
        if self.formed_at is None or self.formed_at < 0:
            c = {"no_formation": self.NX_max < 2, "window_truncated": self.NX_max >= 2}
            return {"formed_at": None, "PASS": False, "checks": c,
                    "classification": "NO_FORMATION" if self.NX_max < 2 else
                                      "TRANSIENT_FORMATION",
                    "stats": {"N_X_max": self.NX_max}}
        if self.n_win < self.T_MAINT:
            return {"formed_at": self.formed_at, "PASS": False,
                    "checks": {"window_truncated": True},
                    "classification": "TRANSIENT_FORMATION",
                    "stats": {"window_steps": self.n_win}}
        mean_NX = self.NX_sum / self.n_win
        turnover = self.deaths / max(mean_NX, 1e-9)
        mu_obs = self.deaths / max(self.NX_sum, 1e-9)
        coh = cohesion_subtest(s, self.frames, np.array(self.births), self.seed, mu_obs)
        drift = abs(self.O_last - self.O_first) / max(self.O_first, 1)
        core_free = self.core_free_sum / max(self.core_free_n, 1)
        c = {
            "never_extinct": not self.ever_zero,
            "organiser_present_throughout": not self.ever_no_org,
            "fraction_at_or_above_N_KEEP": self.n_ok / self.n_win,
            "fraction_ok": (self.n_ok / self.n_win) >= self.FRAC_MIN,
            "longest_excursion": self.below_max,
            "excursion_ok": self.below_max <= self.RUN_MAX,
            "core_exists_fraction": self.n_frames_core / max(self.n_frames, 1),
            "core_exists_ok": (self.n_frames_core / max(self.n_frames, 1))
                              >= a2["core_exists_fraction_min"],
            "compact_vs_N1_fraction": self.n_frames_compact / max(self.n_frames, 1),
            "compact_vs_N1_ok": (self.n_frames_compact / max(self.n_frames, 1))
                                >= a1["compact_vs_N1"]["threshold"],
            "cohesive_vs_N3b_fraction": coh["fraction_below_null_q"],
            "cohesive_vs_N3b_ok": coh["fraction_below_null_q"]
                                  >= a1["cohesive_vs_N3b"]["threshold"],
            "material_turnover": turnover,
            "turnover_ok": turnover >= a3["material_turnover_min"],
            "core_free_capacity_mean": core_free,
            "core_free_capacity_ok": core_free >= a3["core_free_capacity_min"],
            "frames_with_true_winding": self.n_frames_wind,
            "no_true_winding": self.n_frames_wind == 0,
            "occupancy_drift": drift,
            "occupancy_stable": drift <= a4["occupancy_drift_max"],
            "mean_free_at_organiser": self.free_org_sum / self.n_win,
            "free_capacity_at_organiser_ok": (self.free_org_sum / self.n_win)
                                             >= a4["free_capacity_at_organiser_min"],
            "no_score_reading": self.no_score_reading,
            "n_frames_in_window": self.n_frames,
        }
        out = assemble(s, c)
        out["formed_at"] = self.formed_at
        out["cohesion_subtest"] = coh
        out["stats"] = {"N_X_max": self.NX_max, "N_X_mean": mean_NX,
                        "cumulative_deaths_X": self.deaths, "mu_effective_observed": mu_obs}
        return out


# ==================================================================== implementation 2: posthoc
def posthoc_gate(spec, arr, F, frames, n1_thresholds, core_free, seed,
                 no_score_reading=True):
    """Array implementation, written against different data structures."""
    w, a1 = spec["window"], spec["axes"]["axis_1_compact_and_cohesive"]
    a2, a3 = spec["axes"]["axis_2_durable"], spec["axes"]["axis_3_live_not_frozen"]
    a4 = spec["axes"]["axis_4_not_an_artefact"]
    col = lambda k: arr[:, F.index(k)]
    NX, NY, U = col("N_X"), col("N_Y"), col("u_nX_at_org")
    FR, O = col("free_at_org"), col("O_total")
    DE, BI = col("deaths_X"), col("accepted_births_X")
    ok = (NX >= w["N_FORM"]) & (U >= w["U_FORM"])
    formed, run = None, 0
    for i in range(min(len(ok), int(w["T_FORM_MAX"]))):
        run = run + 1 if ok[i] else 0
        if run >= w["K_FORM"]:
            formed = i + 1
            break
    if formed is None:
        return {"formed_at": None, "PASS": False,
                "checks": {"no_formation": bool(NX.max() < 2),
                           "window_truncated": bool(NX.max() >= 2)},
                "classification": "NO_FORMATION" if NX.max() < 2 else "TRANSIENT_FORMATION",
                "stats": {"N_X_max": float(NX.max())}}
    lo, hi = formed, formed + int(w["T_MAINT"])
    if len(arr) < hi:
        return {"formed_at": formed, "PASS": False, "checks": {"window_truncated": True},
                "classification": "TRANSIENT_FORMATION",
                "stats": {"window_steps": len(arr) - lo}}
    nx, ny, fr_, o = NX[lo:hi], NY[lo:hi], FR[lo:hi], O[lo:hi]
    de = DE[lo:hi]
    below = nx < a2["N_KEEP"]
    longest = run = 0
    for b in below:
        run = run + 1 if b else 0
        longest = max(longest, run)
    win = [f for f in frames if lo <= f["step"] < hi]
    n = len(win)
    r80 = np.array([f["r80"] for f in win], dtype=float)
    thr = np.array([n1_thresholds[f["step"]] for f in win], dtype=float)
    cf = np.array([f["core_fraction"] for f in win], dtype=float)
    wr = np.array([bool(f["any_component_wraps"]) for f in win])
    cfree = np.array([core_free[f["step"]] for f in win], dtype=float)
    mean_NX = float(nx.mean())
    turnover = float(de.sum() / max(mean_NX, 1e-9))
    mu_obs = float(de.sum() / max(nx.sum(), 1e-9))
    coh = cohesion_subtest(spec, win, BI, seed, mu_obs)
    drift = float(abs(o[-1] - o[0]) / max(o[0], 1))
    c = {
        "never_extinct": bool((nx > 0).all()),
        "organiser_present_throughout": bool((ny >= 1).all()),
        "fraction_at_or_above_N_KEEP": float((~below).mean()),
        "fraction_ok": bool((~below).mean() >= a2["FRAC_MIN"]),
        "longest_excursion": int(longest),
        "excursion_ok": bool(longest <= a2["RUN_MAX"]),
        "core_exists_fraction": float(np.mean(cf >= a2["core_mass_fraction_min"])) if n else 0.0,
        "core_exists_ok": bool((np.mean(cf >= a2["core_mass_fraction_min"]) if n else 0.0)
                               >= a2["core_exists_fraction_min"]),
        "compact_vs_N1_fraction": float(np.mean(r80 <= thr)) if n else 0.0,
        "compact_vs_N1_ok": bool((np.mean(r80 <= thr) if n else 0.0)
                                 >= a1["compact_vs_N1"]["threshold"]),
        "cohesive_vs_N3b_fraction": coh["fraction_below_null_q"],
        "cohesive_vs_N3b_ok": bool(coh["fraction_below_null_q"]
                                   >= a1["cohesive_vs_N3b"]["threshold"]),
        "material_turnover": turnover,
        "turnover_ok": bool(turnover >= a3["material_turnover_min"]),
        "core_free_capacity_mean": float(np.nanmean(cfree)) if n else 0.0,
        "core_free_capacity_ok": bool((np.nanmean(cfree) if n else 0.0)
                                      >= a3["core_free_capacity_min"]),
        "frames_with_true_winding": int(wr.sum()),
        "no_true_winding": bool(wr.sum() == 0),
        "occupancy_drift": drift,
        "occupancy_stable": bool(drift <= a4["occupancy_drift_max"]),
        "mean_free_at_organiser": float(fr_.mean()),
        "free_capacity_at_organiser_ok": bool(fr_.mean() >= a4["free_capacity_at_organiser_min"]),
        "no_score_reading": bool(no_score_reading),
        "n_frames_in_window": n,
    }
    out = assemble(spec, c)
    out["formed_at"] = formed
    out["cohesion_subtest"] = coh
    out["stats"] = {"N_X_max": float(NX.max()), "N_X_mean": mean_NX,
                    "N_X_min": float(nx.min()), "N_X_median": float(np.median(nx)),
                    "cumulative_deaths_X": float(de.sum()), "mu_effective_observed": mu_obs}
    return out


def compare(a, b):
    keys = set(a.get("checks", {})) | set(b.get("checks", {}))
    diffs = {}
    for k in sorted(keys):
        x, y = a["checks"].get(k), b["checks"].get(k)
        same = (abs(x - y) < 1e-9) if (isinstance(x, float) and isinstance(y, float)) \
            else (x == y)
        if not same:
            diffs[k] = {"online": x, "posthoc": y}
    for k in ("formed_at", "PASS", "classification"):
        if a.get(k) != b.get(k):
            diffs[k] = {"online": a.get(k), "posthoc": b.get(k)}
    return {"AGREE": len(diffs) == 0, "differences": diffs}
