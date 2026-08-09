"""ETPC core: exact checkpoints, independent forks, the reciprocal z operator, the four arms.

The model is FULLY DETERMINISTIC (Phase A determinism audit: no random draw anywhere in the
engine step). Exogenous "noise" is therefore not a tape but the empty set: after the branch point
no variate is ever drawn, so branch-independence is exact by construction and twins are exact by
determinism. This is discharged as an audit, not simulated with artificial noise.
"""
from __future__ import annotations
import sys, os, io, json, hashlib
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/PPAI")
import numpy as np
import domc_core as K
import ppai_core as P
from ppai_engine import PPAIEngine, PPAIParams, kappa
from edlab.experiments.sc_mcm import config as C
from edlab.experiments.sc_iom.engine import IOMState

FIELDS = ("rho", "U", "V", "c", "N", "C", "uptake", "Mf")
PUBLIC_FIELDS = ("rho", "U", "V", "c", "N", "C", "uptake")   # everything except the z carrier
GAIN_ON = 1.0 / 3.0
T_EARLY = 40         # instantaneous constitutive window, excluded from the mediator
T_MED = 200          # delayed public mediator readout
T_RESP = 200         # the delayed response challenge is launched here (>= D_LATE = 120)
SWAP_FRACTION_RULE = "mass-matched: exchange exactly the common material measure min(M_A, M_B)"


# ------------------------------------------------------------------ hashing and checkpoints
def array_hash(name, a):
    a = np.ascontiguousarray(a)
    h = hashlib.sha256()
    h.update(name.encode()); h.update(str(a.shape).encode())
    h.update(str(a.dtype.str).encode())          # includes byte order
    h.update(a.tobytes(order="C"))
    return h.hexdigest()


def logical_hash(st, meta=None):
    """Hash over every canonical array WITH its name, shape, dtype, endianness and raw bytes,
    plus the scalar step counter and the declared LawSpec/runtime identity."""
    parts = {f: array_hash(f, getattr(st, f)) for f in FIELDS}
    parts["step"] = hashlib.sha256(str(int(st.step)).encode()).hexdigest()
    if meta:
        parts["meta"] = hashlib.sha256(json.dumps(meta, sort_keys=True).encode()).hexdigest()
    h = hashlib.sha256()
    for k in sorted(parts):
        h.update(k.encode()); h.update(parts[k].encode())
    return h.hexdigest(), parts


def public_hash(st):
    h = hashlib.sha256()
    for f in sorted(PUBLIC_FIELDS):
        h.update(array_hash(f, getattr(st, f)).encode())
    return h.hexdigest()


def save(st, path, meta=None):
    np.savez(path, **{f: np.ascontiguousarray(getattr(st, f)) for f in FIELDS},
             step=np.array([st.step], dtype=np.int64))
    lh, parts = logical_hash(st, meta)
    json.dump({"logical_hash": lh, "arrays": parts, "meta": meta or {},
               "archive_sha256": hashlib.sha256(open(path, "rb").read()).hexdigest()},
              open(path + ".hash.json", "w"), indent=1)
    return lh


def load(path):
    """FORK BY INDEPENDENT RELOAD, never by shallow copy."""
    d = np.load(path)
    return IOMState(*(np.array(d[f], copy=True) for f in FIELDS), int(d["step"][0]))


# ------------------------------------------------------------------ the frozen state schema
STATE_SCHEMA = {
    "material_fields": ["rho (scaffold density)", "U, V (internal bistable species, extensive)"],
    "internal_coordinates": ["Mf[0] = rho*z, the extensive content of z = m1",
                             "Mf[1] = rho*m2, the second memory component (untouched)"],
    "public_bath_fields": ["c (attractant)", "N (nutrient)"],
    "provenance": ["C (cohort tracer), auditor-only, never read by dynamics or readers"],
    "derived_last_step": ["uptake (per-cell nutrient consumed last step)"],
    "counters": ["step"],
    "integrator_or_event_state": "ABSENT: the engine is a single explicit forward map with no "
                                 "integrator memory, no event queue and no adaptive step.",
    "external_forcing_schedule": "ABSENT after the founding histories: no forcing remains at or "
                                 "after the intervention checkpoint.",
    "reader_accumulators": "ABSENT: every reader is a pure function of the current state.",
    "non_reconstructible_caches": "ABSENT: kappa is recomputed from Mf and rho inside every step.",
    "lineage": "prospective, reconstructed from the state by the frozen detector; not a dynamical "
               "variable and never fed back into the dynamics.",
    "lawspec_and_parameters": "ScaffoldSpec(exp_sc_00, beta=0.10) + PPAIParams(gain, z_index=0)",
    "noise_provider": "NONE. The model is deterministic; see the Phase A determinism audit.",
}


def runtime_manifest():
    import platform
    return {"python": sys.version.split()[0], "numpy": np.__version__,
            "platform": platform.platform(), "machine": platform.machine(),
            "byteorder": sys.byteorder, "float_dtype": str(np.zeros(1).dtype)}


# -------------------------------------------------------------------- membership and z summaries
def members(st):
    """Prospectively tracked A/B membership: the frozen-site reader of the parent line. Never
    largest(st), never a dynamic rank."""
    pick, dist, n = K.read_sites(st)
    out = {}
    for nm in ("A", "B"):
        e = pick[nm]
        out[nm] = None if e is None else (e.cells[:, 0].copy(), e.cells[:, 1].copy())
    return out, n


def z_summary(st, mem):
    r = np.maximum(st.rho, 1e-12)
    z = st.Mf[0] / r
    out = {}
    for nm in ("A", "B"):
        if mem[nm] is None:
            out[nm] = None
            continue
        ys, xs = mem[nm]
        M = float(st.rho[ys, xs].sum())
        out[nm] = {"mass": M,
                   "zbar": float(np.average(z[ys, xs], weights=st.rho[ys, xs])),
                   "sum_rho_z": float(st.Mf[0][ys, xs].sum()),
                   "n_cells": int(len(ys))}
    return out


def invariant_ledger(st, mem):
    r = np.maximum(st.rho, 1e-12)
    z = st.Mf[0] / r
    alive = st.rho > 1e-4
    zz = z[alive]
    cov = float(np.cov(np.stack([st.rho[alive], zz]))[0, 1]) if alive.sum() > 1 else 0.0
    bnd = np.zeros_like(alive)
    for ax in (-2, -1):
        for s in (1, -1):
            bnd |= alive & ~np.roll(alive, s, ax)
    return {"raw_z_multiset_sha256": array_hash("z_sorted", np.sort(z.ravel())),
            "sum_z": float(z.sum()), "sum_rho_z": float(st.Mf[0].sum()),
            "z_histogram": np.histogram(z, bins=32, range=(-1, 1))[0].tolist(),
            "rho_z_covariance": cov,
            "z_exposure_at_material_bath_boundary": float(z[bnd].sum()) if bnd.any() else 0.0,
            "n_boundary_cells": int(bnd.sum()),
            "components": z_summary(st, mem),
            "material_mass": float(st.rho.sum()),
            "c_sum": float(st.c.sum()), "N_sum": float(st.N.sum()),
            "c_histogram": np.histogram(st.c, bins=16, range=(0, 3))[0].tolist(),
            "N_histogram": np.histogram(st.N, bins=16, range=(0, 2))[0].tolist()}


# ------------------------------------------------- the reciprocal operator P, frozen algorithm
def build_operator(st):
    """Deterministic, built from the PRE-INTERVENTION checkpoint only. Reads canonical state and
    prospective A/B membership. Reads no future value, no response, no branch label, no held-out
    result and no dynamic largest(st).

    z is an INTENSIVE material-carried concentration; its extensive content is rho*z = Mf[0].
    The physically relevant global measure is therefore Sigma rho z, and the operator conserves it
    EXACTLY by construction:

        m* = min(M_A, M_B)                      the common exchangeable material measure
        a  = m*/M_A ,  b = m*/M_B               (one of them is exactly 1)
        z_A <- z_A + a (zbar_B - zbar_A)
        z_B <- z_B + b (zbar_A - zbar_B)

    extensive change = M_A a (zbar_B - zbar_A) + M_B b (zbar_A - zbar_B)
                     = m*(zbar_B - zbar_A) + m*(zbar_A - zbar_B) = 0, exactly.

    The lighter component exchanges its whole mean; the heavier one exchanges only the
    mass-matched share, so the excess material is left unchanged. The transferred fraction is
    published and is fixed by the masses alone -- never chosen to maximise anything."""
    mem, _ = members(st)
    zs = z_summary(st, mem)
    if zs["A"] is None or zs["B"] is None:
        return None
    MA, MB = zs["A"]["mass"], zs["B"]["mass"]
    zA, zB = zs["A"]["zbar"], zs["B"]["zbar"]
    mstar = min(MA, MB)
    a, b = mstar / MA, mstar / MB
    op = {"dzA": a * (zB - zA), "dzB": b * (zA - zB),
          "a": a, "b": b, "m_star": mstar, "M_A": MA, "M_B": MB,
          "zbar_A": zA, "zbar_B": zB,
          "transferred_fraction_A": a, "transferred_fraction_B": b,
          "involutive": bool(abs(a - 1.0) < 1e-15 and abs(b - 1.0) < 1e-15),
          "rule": SWAP_FRACTION_RULE}
    op["hash"] = hashlib.sha256(json.dumps(
        {k: op[k] for k in sorted(op) if k != "hash"}, sort_keys=True).encode()).hexdigest()
    return op


def apply_operator(st, mem, op, inverse=False, identity=False):
    """Applied THROUGH A BUFFER, never destructively in place. Identity outside the declared
    target. Touches Mf[0] on A and B cells only."""
    out = st.copy()
    if identity or op is None:
        return out
    s = -1.0 if inverse else 1.0
    buf = out.Mf[0].copy()
    for nm, d in (("A", op["dzA"]), ("B", op["dzB"])):
        if mem[nm] is None:
            continue
        ys, xs = mem[nm]
        buf[ys, xs] = buf[ys, xs] + s * d * out.rho[ys, xs]
    out.Mf = out.Mf.copy()
    out.Mf[0] = buf
    return out


def touchset(before, after):
    d = {}
    for f in FIELDS:
        a, b = np.asarray(getattr(before, f)), np.asarray(getattr(after, f))
        d[f] = {"changed": bool(not np.array_equal(a, b)),
                "n_sites_changed": int((a != b).sum())}
    d["Mf1_unchanged"] = bool(np.array_equal(before.Mf[1], after.Mf[1]))
    return d


# ---------------------------------------------------------------------------------- engines
def engine(gain):
    return PPAIEngine(C.SPEC, PPAIParams(gain=gain), C.TRACER)


ARMS = {"ON_SHAM": (GAIN_ON, False), "ON_SWAP": (GAIN_ON, True),
        "OFF_SHAM": (0.0, False), "OFF_SWAP": (0.0, True)}
