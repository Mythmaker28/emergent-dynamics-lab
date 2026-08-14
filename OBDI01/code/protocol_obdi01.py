"""OBDI01 §17-§19 — arm production.

IDENTITY BY CONSTRUCTION. This file does not reimplement the preparation, the engine loop, the
molecular tracker or the technical-validity layer. It CALLS OBTC02's own `run_arm`, unmodified,
with OBTC02's own spec object. What differs between an OBDI01 arm and an OBTC02 P arm is
exactly three things, all of them declared:

    the domain size L, the seed, and the directory the raw archive is written to.

Everything else — LawSpec, chemostat, insertion mode, RNG mode, recorder fields, frame
contract, online/post-hoc double evaluation, checksums — is the same code path. That is why
LAWSPEC_DIFF_FROM_OBTC02 = NONE is a fact about the call graph rather than an assurance.

THE ONE ADDED MEASUREMENT, AND WHY IT CANNOT CHANGE THE PROCESS
--------------------------------------------------------------
The principal outcome needs the radial mass distribution about the organiser, which the frozen
frame record does not carry (it stores radii, not the profile). Rather than edit `run_arm` — an
edit that would destroy the identity above — a PASSIVE OBSERVER is installed on `metrics_obtc.
frame`. The observer:

    * calls the original function and returns its result unchanged, object for object;
    * reads `n_X` and the organiser position; writes nothing;
    * draws no random number, so the stream feeding the engine is untouched.

`tests_obdi01.py` proves this empirically in TEST mode — which consumes no start from the
ledger — by running the same world with and without the observer and comparing the engine's
state hash and the frame payload checksum.
"""
from __future__ import annotations

import sys

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/OBDI01/code")

import gate_obdi01 as GT           # noqa: E402
import metrics_obtc as M           # noqa: E402
import protocol_obtc02 as PC       # noqa: E402
import source_operator as OP       # noqa: E402

RAW = "/home/claude/OBDI01/raw"
PC.RAW = RAW                       # the only redirection: where the .npz archive is written

_ORIGINAL_FRAME = M.frame
_ACC = {"rows": [], "edges": None, "on": False}


def install_observer(edges):
    """Wrap `metrics_obtc.frame` with a read-only accumulator. Idempotent."""
    _ACC["edges"] = list(edges)
    if _ACC["on"]:
        return

    def observed(nX, nY, core_radius):
        fr, labels = _ORIGINAL_FRAME(nX, nY, core_radius)
        if fr["organiser_y"] >= 0 and fr["N_X"] > 0:
            h = GT.empirical_radial(nX, int(fr["organiser_y"]), int(fr["organiser_x"]),
                                    _ACC["edges"])
            _ACC["rows"].append((int(fr["N_X"]), h))
        else:
            _ACC["rows"].append((0, np.zeros(len(_ACC["edges"]))))
        return fr, labels

    M.frame = observed
    _ACC["on"] = True


def remove_observer():
    M.frame = _ORIGINAL_FRAME
    _ACC["on"] = False


def reset_observer():
    _ACC["rows"] = []


def arm_conditions(L):
    """An OBDI01 arm is an OBTC02 P arm at a given L: no intervention of any kind."""
    return {"key": "P", "L": int(L)}


def run_one(tag, L, seed, envelope, analytic, spec01):
    """Produce one arm and reduce it to the summaries the principal outcome consumes."""
    edges = list(spec01["principal_outcome"]["components"]["D_profile_compatibility"][
        "radial_bin_edges"])
    install_observer(edges)
    reset_observer()
    a = PC.run_arm("confirmation", tag, arm_conditions(L), seed, envelope, analytic)
    rows = list(_ACC["rows"])

    frames = a["frames"]
    burn = int(spec01["window"]["BURN_IN"])
    if len(rows) != len(frames):
        raise RuntimeError("observer saw %d frames, the run recorded %d" % (len(rows),
                                                                           len(frames)))
    win_idx = [i for i, f in enumerate(frames) if f["step"] > burn]
    win = [frames[i] for i in win_idx]

    acc = np.zeros(len(edges))
    for i in win_idx:
        n, h = rows[i]
        acc += h * n
    pred = GT.predicted_radial(OP.Op(PC.spec_for(L)).relative_profile(L), edges)
    tv = GT.total_variation(acc / acc.sum(), pred) if acc.sum() > 0 else float("nan")

    def med(key):
        v = np.array([f.get(key, np.nan) for f in win], float)
        v = v[np.isfinite(v)]
        return float(np.median(v)) if len(v) else float("nan")

    a["window_frames"] = len(win)
    a["summary"] = {"Rg": med("Rg"), "r80": med("r80"), "r50": med("r50"), "r90": med("r90"),
                    "organiser_to_core": med("organiser_to_core"),
                    "r80_organiser": med("r80_organiser"),
                    "core_fraction": med("core_fraction"),
                    "main_mass_fraction": med("main_mass_fraction"),
                    "N_X_mean": float(np.mean([f["N_X"] for f in win])) if win else float("nan")}
    a["summary"]["density"] = a["summary"]["N_X_mean"] / float(L * L)
    a["winding_frames"] = int(sum(1 for f in win if f["any_winding"]))
    a["r80_organiser_frames"] = [float(f.get("r80_organiser", np.nan)) for f in win]
    a["profile_TV"] = tv
    a["radial_observed"] = [float(x) for x in (acc / acc.sum() if acc.sum() > 0 else acc)]
    a["radial_predicted"] = [float(x) for x in pred]
    return a


def analytic_for():
    return OP.Op(PC.spec_for()).predictions()
