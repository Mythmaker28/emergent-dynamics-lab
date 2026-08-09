"""PPAI harness: founding, mirrored histories, wash, arms, readers, ledgers."""
from __future__ import annotations
import sys
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/CHMR")
import numpy as np
import domc_core as K
import chmr_lineage as LG
from edlab.experiments.sc_mcm import config as C
from edlab.experiments.sc_hmc.harness import PulseChaseTracer
from ppai_engine import PPAIEngine, PPAIParams, GAIN_CLASSES, kappa, z_field
from edlab.experiments.sc_iom.engine import IOMState

L = K.L
R_HALO = 8.0
CAD = 25
HIST_H, HIST_L = "cc", "00"
T_FOUND, SETTLE = K.T_FOUND, K.SETTLE
T_TURN = K.T_TURN
D_LATE = 120          # the DELAY between intervention and the late response reader


def engine(gain=0.0, pulse_chase=False):
    return PPAIEngine(C.SPEC, PPAIParams(gain=gain),
                      PulseChaseTracer() if pulse_chase else C.TRACER)


def found(seed):
    return K.found(seed)


def advance(eng, st, n):
    cur = st.copy()
    for _ in range(n):
        cur = eng.step(cur)
    return cur


def halo_sup():
    yy, xx = np.mgrid[0:L, 0:L]
    return {"A": K._pd2(yy, xx, *K.SITE_A) <= R_HALO ** 2,
            "B": K._pd2(yy, xx, *K.SITE_B) <= R_HALO ** 2}


# ---------------------------------------------------------------- readers (all z-blind but one)
def public_vector(st, sup):
    """PUBLIC dictionary: everything an observer of the bath and the bodies can see. Contains no
    z, no history label, no provenance, no component id."""
    pick, dist, n = K.read_sites(st)
    out = {"n_components": n}
    for nm in ("A", "B"):
        e = pick[nm]
        d = {"c": float(st.c[sup[nm]].mean()), "N": float(st.N[sup[nm]].mean()),
             "flux_c": float(np.abs(np.diff(st.c[sup[nm]])).mean()) if sup[nm].sum() > 1 else 0.0,
             "d_site": round(dist[nm], 3)}
        if e is not None:
            ys, xs = e.cells[:, 0], e.cells[:, 1]
            d.update({"mass": float(e.mass), "size": int(e.size), "rg": float(e.rg),
                      "perimeter": int(e.size), "mean_sig": float(e.mean_sig),
                      "specific_uptake": float(e.specific_uptake),
                      "cy": float(e.centroid[0]), "cx": float(e.centroid[1])})
        else:
            d.update({"mass": 0.0, "size": 0, "rg": 0.0, "perimeter": 0, "mean_sig": 0.0,
                      "specific_uptake": 0.0, "cy": None, "cx": None})
        out[nm] = d
    return out


def z_vector(st):
    """PRIVILEGED auditor diagnostic. Never enters a policy, a reader or the dynamics."""
    pick, _, _ = K.read_sites(st)
    zf = z_field(st)
    out = {}
    for nm in ("A", "B"):
        e = pick[nm]
        if e is None:
            out[nm] = None
            continue
        ys, xs = e.cells[:, 0], e.cells[:, 1]
        w = st.rho[ys, xs]
        out[nm] = float(np.average(zf[ys, xs], weights=w))
    return out


def challenge(eng, st):
    """the frozen DOMC probe, unchanged and blind to z, history, provenance and labels."""
    return K.response_at_sites(eng, st)


# --------------------------------------------------------------------------- interventions
def state_cross(st):
    """The reciprocal conservative permutation of z.

    z is the INTENSIVE coordinate m = Mf / rho, so the permutation is applied to the intensive
    field and the extensive field is rebuilt from the LOCAL rho:  Mf <- rho * m[reflected].
    Permuting Mf directly would NOT conserve z, because Mf/rho would then be read against a
    different local density.

    Exactly conserved: the multiset of intensive values over the lattice, hence the global z
    histogram over the lattice, bit-for-bit. rho, U, V, c, N and C are bit-identical, so the
    bodies do not move. The EFFECTIVE z, which the engine masks by the live support, is conserved
    on the intersection of the support with its mirror image; the residual is measured in the
    ledger rather than assumed away, because the two bodies are mirror-placed but not
    mirror-shaped."""
    o = st.copy()
    r = np.maximum(st.rho, 1e-12)
    m = st.Mf / r[None, :, :]
    o.Mf = st.rho[None, :, :] * m[:, :, K.REFLECT_IX]
    return o


def intensive_z(st):
    return (st.Mf / np.maximum(st.rho, 1e-12)[None, :, :])[0]


def erase(st, half):
    o = st.copy()
    o.Mf[:, :, (K.HALF_A if half == "A" else K.HALF_B)] = 0.0
    return o


def erase_all(st):
    o = st.copy()
    o.Mf[:] = 0.0
    return o


def sham(st):
    return st.copy()


def ledger(before, after, name):
    d = {"intervention": name}
    for f in ("rho", "U", "V", "C", "Mf", "c", "N"):
        a, b = np.asarray(getattr(before, f)), np.asarray(getattr(after, f))
        d[f] = {"changed": bool(not np.array_equal(a, b)),
                "sum_before": float(a.sum()), "sum_after": float(b.sum()),
                "multiset_preserved": bool(np.array_equal(np.sort(a.ravel()),
                                                          np.sort(b.ravel()))),
                "n_sites_changed": int((a != b).sum())}
    zb, za = z_field(before), z_field(after)
    ib = intensive_z(before); ia = intensive_z(after)
    d["intensive_z_multiset_preserved"] = bool(np.array_equal(np.sort(ib.ravel()),
                                                              np.sort(ia.ravel())))
    d["effective_z_hist_residual"] = float(np.abs(
        np.histogram(zb, bins=16, range=(-1, 1))[0]
        - np.histogram(za, bins=16, range=(-1, 1))[0]).sum())
    d["z_hist_before"] = np.histogram(zb, bins=16, range=(-1, 1))[0].tolist()
    d["z_hist_after"] = np.histogram(za, bins=16, range=(-1, 1))[0].tolist()
    d["z_hist_preserved"] = d["z_hist_before"] == d["z_hist_after"]
    d["c_hist_before"] = np.histogram(before.c, bins=12, range=(0, 3))[0].tolist()
    d["c_hist_after"] = np.histogram(after.c, bins=12, range=(0, 3))[0].tolist()
    d["N_hist_before"] = np.histogram(before.N, bins=12, range=(0, 2))[0].tolist()
    d["N_hist_after"] = np.histogram(after.N, bins=12, range=(0, 2))[0].tolist()
    d["mass_before"] = float(before.rho.sum()); d["mass_after"] = float(after.rho.sum())
    d["realized_c_before"] = float(before.c.sum()); d["realized_c_after"] = float(after.c.sum())
    d["realized_N_before"] = float(before.N.sum()); d["realized_N_after"] = float(after.N.sum())
    # dissipation bookkeeping: the death sink and the bath relaxation sinks over one state
    d["death_sink_rate"] = float(C.SPEC.k * before.rho.sum())
    d["c_relax_sink"] = float(C.SPEC.delta * before.c.sum())
    d["N_relax_source"] = float(C.SPEC.F * (C.SPEC.N0 * before.N.size - before.N.sum()))
    return d
