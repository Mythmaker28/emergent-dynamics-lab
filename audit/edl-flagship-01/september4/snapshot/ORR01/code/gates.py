"""The ORR01 gate, in TWO independent implementations.

Two missions in a row needed a gate corrected after the freeze. The answer here is not a better
gate but a REDUNDANT one: the classification is computed twice, by two implementations written
against different data structures, and any disagreement is a protocol failure.

  RUNTIME    a streaming implementation. It sees one step at a time, keeps counters only, and
             never stores the trajectory. This is what runs during an arm.
  POSTHOC    an array implementation. It reads the raw series back from disk after the fact and
             recomputes the classification from scratch.

`compare()` runs both and returns agreement. `tests_orr.py` requires agreement on synthetic
traces, on the declared edge cases, on exhaustive tiny traces, and on the eight historical
MCM01 arms.

The criticality term is the one corrected in MCM01 addendum C-1: the condition is a statement
about a MEAN offspring number, so it is tested as mean(c_X over the window) * G0 > 1, and the
per-step fraction is reported as a descriptive intermittency statistic only.
"""
from __future__ import annotations

import numpy as np

CLASSES = ("NO_FORMATION", "TRANSIENT_FORMATION", "MAINTENANCE_ACHIEVED", "MATERIAL_COLLAPSE",
           "ORGANISATION_LOST", "BOUNDARY_ARTEFACT", "OCCUPANCY_RATCHET", "PROTOCOL_VIOLATION",
           "ENGINE_ERROR", "UNCLASSIFIABLE")


class Thresholds:
    def __init__(self, T_FORM_MAX, T_MAINT, N_FORM, U_FORM, K_FORM, N_KEEP, FRAC_MIN, RUN_MAX,
                 G0, FREE_MIN, OCC_TOL):
        self.__dict__.update(locals())
        del self.__dict__["self"]

    def as_dict(self):
        return dict(self.__dict__)


# ==================================================================== implementation 1: runtime
class RuntimeGate:
    """Streaming. Holds counters only; never sees the trajectory as an array."""

    def __init__(self, th):
        self.th = th
        self.t = 0
        self.form_run = 0
        self.formed_at = None
        self.n_win = 0
        self.n_ok = 0
        self.below_run = 0
        self.below_max = 0
        self.ever_zero = False
        self.ever_no_org = False
        self.cx_sum = 0.0
        self.cx_pointwise_ok = 0
        self.free_sum = 0.0
        self.O_first = None
        self.O_last = None
        self.main_ok = True
        self.wrap_ok = True
        self.NX_max = 0.0

    def step(self, N_X, N_Y, u, c_X, free_at_org, O_total):
        th = self.th
        self.t += 1
        self.NX_max = max(self.NX_max, N_X)
        if self.formed_at is None:
            self.form_run = self.form_run + 1 if (N_X >= th.N_FORM and u >= th.U_FORM) else 0
            if self.form_run >= th.K_FORM:
                self.formed_at = self.t
            elif self.t >= th.T_FORM_MAX:
                self.formed_at = -1                      # formation window closed, never formed
            return
        if self.formed_at < 0 or self.n_win >= th.T_MAINT:
            return
        self.n_win += 1
        if self.O_first is None:
            self.O_first = O_total
        self.O_last = O_total
        if N_X <= 0:
            self.ever_zero = True
        if N_Y < 1:
            self.ever_no_org = True
        if N_X >= th.N_KEEP:
            self.n_ok += 1
            self.below_run = 0
        else:
            self.below_run += 1
            self.below_max = max(self.below_max, self.below_run)
        self.cx_sum += c_X
        self.cx_pointwise_ok += 1 if c_X * th.G0 > 1.0 else 0
        self.free_sum += free_at_org

    def sample(self, main_N_X, main_wraps):
        if self.formed_at is not None and self.formed_at > 0 and 0 < self.n_win <= self.th.T_MAINT:
            if main_N_X is None or main_N_X < self.th.N_KEEP * 0.5:
                self.main_ok = False
            if main_wraps:
                self.wrap_ok = False

    def result(self):
        th = self.th
        if self.formed_at is None or self.formed_at < 0:
            return {"formed_at": None, "PASS": False, "checks": {},
                    "classification": "NO_FORMATION" if self.NX_max < 2 else
                                      "TRANSIENT_FORMATION",
                    "stats": {"N_X_max": self.NX_max}}
        if self.n_win < th.T_MAINT:
            return {"formed_at": self.formed_at, "PASS": False,
                    "checks": {"window_complete": False},
                    "classification": "TRANSIENT_FORMATION",
                    "stats": {"window_steps": self.n_win}}
        c = {
            "never_extinct": not self.ever_zero,
            "organiser_present_throughout": not self.ever_no_org,
            "fraction_at_or_above_N_KEEP": self.n_ok / self.n_win,
            "fraction_ok": (self.n_ok / self.n_win) >= th.FRAC_MIN,
            "longest_excursion": self.below_max,
            "excursion_ok": self.below_max <= th.RUN_MAX,
            "mean_c_X": self.cx_sum / self.n_win,
            "mean_c_X_times_G0": (self.cx_sum / self.n_win) * th.G0,
            "criticality_ok": (self.cx_sum / self.n_win) * th.G0 > 1.0,
            "pointwise_fraction_c_X_G0_above_1": self.cx_pointwise_ok / self.n_win,
            "mean_free_at_organiser": self.free_sum / self.n_win,
            "free_capacity_not_collapsed": (self.free_sum / self.n_win) >= th.FREE_MIN,
            "occupancy_drift": abs(self.O_last - self.O_first) / max(self.O_first, 1),
            "occupancy_stable": (abs(self.O_last - self.O_first) / max(self.O_first, 1))
                                <= th.OCC_TOL,
            "main_component_carries_the_mass": self.main_ok,
            "no_wrap_around_contact": self.wrap_ok,
        }
        hard = ("never_extinct", "organiser_present_throughout", "fraction_ok", "excursion_ok",
                "criticality_ok", "free_capacity_not_collapsed", "occupancy_stable",
                "main_component_carries_the_mass", "no_wrap_around_contact")
        return {"formed_at": self.formed_at, "PASS": all(c[k] for k in hard), "checks": c,
                "classification": classify(c), "stats": {"N_X_max": self.NX_max}}


def classify(c):
    """Exhaustive, mutually exclusive, fixed order."""
    if not c:
        return "UNCLASSIFIABLE"
    hard = ("never_extinct", "organiser_present_throughout", "fraction_ok", "excursion_ok",
            "criticality_ok", "free_capacity_not_collapsed", "occupancy_stable",
            "main_component_carries_the_mass", "no_wrap_around_contact")
    if all(c.get(k, False) for k in hard):
        return "MAINTENANCE_ACHIEVED"
    if not c.get("no_wrap_around_contact", True):
        return "BOUNDARY_ARTEFACT"
    if not c.get("occupancy_stable", True) or not c.get("free_capacity_not_collapsed", True):
        return "OCCUPANCY_RATCHET"
    if not c.get("organiser_present_throughout", True):
        return "ORGANISATION_LOST"
    if not c.get("never_extinct", True):
        return "MATERIAL_COLLAPSE"
    if not c.get("main_component_carries_the_mass", True):
        return "ORGANISATION_LOST"
    if not (c.get("fraction_ok", True) and c.get("excursion_ok", True)):
        return "TRANSIENT_FORMATION"
    if not c.get("criticality_ok", True):
        return "MATERIAL_COLLAPSE"
    return "UNCLASSIFIABLE"


# ==================================================================== implementation 2: posthoc
def posthoc_gate(arr, F, th, comp_samples):
    """Array implementation, written independently of RuntimeGate."""
    col = lambda k: arr[:, F.index(k)]
    NX, NY, U, CX = col("N_X"), col("N_Y"), col("u_nX_at_org"), col("c_X_per_org")
    FR, O = col("free_at_org"), col("O_total")
    ok = (NX >= th.N_FORM) & (U >= th.U_FORM)
    formed = None
    run = 0
    for i in range(min(len(ok), int(th.T_FORM_MAX))):
        run = run + 1 if ok[i] else 0
        if run >= th.K_FORM:
            formed = i + 1
            break
    if formed is None:
        return {"formed_at": None, "PASS": False, "checks": {},
                "classification": "NO_FORMATION" if NX.max() < 2 else "TRANSIENT_FORMATION",
                "stats": {"N_X_max": float(NX.max())}}
    lo, hi = formed, formed + int(th.T_MAINT)
    if len(arr) < hi:
        return {"formed_at": formed, "PASS": False, "checks": {"window_complete": False},
                "classification": "TRANSIENT_FORMATION",
                "stats": {"window_steps": len(arr) - lo}}
    nx, ny, cx, fr, o = NX[lo:hi], NY[lo:hi], CX[lo:hi], FR[lo:hi], O[lo:hi]
    below = nx < th.N_KEEP
    longest = run = 0
    for b in below:
        run = run + 1 if b else 0
        longest = max(longest, run)
    sm = [s for s in comp_samples if lo <= s["step"] < hi]
    c = {
        "never_extinct": bool((nx > 0).all()),
        "organiser_present_throughout": bool((ny >= 1).all()),
        "fraction_at_or_above_N_KEEP": float((~below).mean()),
        "fraction_ok": bool((~below).mean() >= th.FRAC_MIN),
        "longest_excursion": int(longest),
        "excursion_ok": bool(longest <= th.RUN_MAX),
        "mean_c_X": float(cx.mean()),
        "mean_c_X_times_G0": float(cx.mean() * th.G0),
        "criticality_ok": bool(cx.mean() * th.G0 > 1.0),
        "pointwise_fraction_c_X_G0_above_1": float((cx * th.G0 > 1.0).mean()),
        "mean_free_at_organiser": float(fr.mean()),
        "free_capacity_not_collapsed": bool(fr.mean() >= th.FREE_MIN),
        "occupancy_drift": float(abs(o[-1] - o[0]) / max(o[0], 1)),
        "occupancy_stable": bool(abs(o[-1] - o[0]) / max(o[0], 1) <= th.OCC_TOL),
        "main_component_carries_the_mass": bool(
            all(s["main"] is not None and s["main"]["N_X"] >= th.N_KEEP * 0.5 for s in sm)),
        "no_wrap_around_contact": bool(all(not (s["main"] or {}).get("wraps", True)
                                           for s in sm)),
    }
    hard = ("never_extinct", "organiser_present_throughout", "fraction_ok", "excursion_ok",
            "criticality_ok", "free_capacity_not_collapsed", "occupancy_stable",
            "main_component_carries_the_mass", "no_wrap_around_contact")
    return {"formed_at": formed, "PASS": bool(all(c[k] for k in hard)), "checks": c,
            "classification": classify(c),
            "stats": {"N_X_min": float(nx.min()), "N_X_median": float(np.median(nx)),
                      "N_X_mean": float(nx.mean()), "N_X_max": float(NX.max()),
                      "c_X_min": float(cx.min()), "c_X_q05": float(np.quantile(cx, 0.05)),
                      "c_X_median": float(np.median(cx)), "c_X_mean": float(cx.mean()),
                      "free_at_org_mean": float(fr.mean()),
                      "O_first": float(o[0]), "O_last": float(o[-1])}}


def replay_runtime(arr, F, th, comp_samples):
    """Feed a stored series through the STREAMING gate, one step at a time, so the two
    implementations can be compared on the same data."""
    g = RuntimeGate(th)
    col = {k: arr[:, F.index(k)] for k in ("N_X", "N_Y", "u_nX_at_org", "c_X_per_org",
                                           "free_at_org", "O_total")}
    by_step = {int(s["step"]): s for s in comp_samples}
    for i in range(len(arr)):
        g.step(col["N_X"][i], col["N_Y"][i], col["u_nX_at_org"][i], col["c_X_per_org"][i],
               col["free_at_org"][i], col["O_total"][i])
        s = by_step.get(int(arr[i, F.index("step")]))
        if s is not None:
            g.sample((s["main"] or {}).get("N_X"), (s["main"] or {}).get("wraps", True))
    return g.result()


def compare(arr, F, th, comp_samples):
    a = replay_runtime(arr, F, th, comp_samples)
    b = posthoc_gate(arr, F, th, comp_samples)
    agree = (a["classification"] == b["classification"] and a["PASS"] == b["PASS"]
             and a["formed_at"] == b["formed_at"])
    return {"runtime": a, "posthoc": b, "AGREE": bool(agree)}
