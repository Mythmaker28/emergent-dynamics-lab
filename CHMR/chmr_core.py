"""CORE_HALO_MISMATCH_RECOVERY_00 — core.

NEW_LAWSPEC_AUTHORIZED = false. The LawSpec is the frozen sc_mcm
`MultiChannelMemoryEngine` with `MCParams(lam_plus=0.25, lam_minus=0.15)`, imported and never
edited. The founding, the frozen sites, the half-plane driving, the frozen detector and the
reciprocal permutation are inherited unchanged from DOMC (`domc_core`), whose file hash is
recorded in the DOMC seal.

TWO LAYERS, MEASURED SEPARATELY AND NEVER COMBINED INTO ONE SCORE:

  CORE  : the memory field Mf. Its frozen marker vector is the mass-weighted (m1, m2) over the
          component the site reader selects. Nothing else enters the core vector.
  HALO  : the two external handles c and N. Its frozen vector is (mean c, mean N) over the
          frozen HALO SUPPORT, a disc of radius R_HALO = 8 around the frozen site. Nothing
          else enters the halo vector.

The only mechanism-touching operation is WRITER_OFF, which sets `lam_minus` to exactly 0 during
recovery. That is a zero-versus-sham ablation of a term ALREADY PRESENT in the frozen LawSpec --
`c += dt (D_c lap c + s rho (1 + lam_minus m_minus) - delta c)` -- and it is the only place in
the frozen engine where the core writes the halo. It creates nothing and tunes nothing.
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
import numpy as np

import domc_core as K
import chmr_lineage as LG
from edlab.experiments.sc_mcm import harness as H, config as C
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine, MCParams
from edlab.experiments.sc_hmc.harness import PulseChaseTracer

L = K.L
R_HALO = 8.0                    # frozen halo support radius
CAD_LINEAGE = 25                # frozen lineage checkpoint cadence (validated in Phase L)
T_PREFIX = K.T_FOUND + 2 * K.T_PHASE + K.SETTLE      # 150 + 120 + 120 = 390
HIST_H, HIST_L = "cc", "00"     # inherited from the DOMC Phase C selection; no new history pair
T_TURN = K.T_TURN               # 700, frozen parent horizon
OBS_TIMES = (0, 25, 50, 100, 150, 200, 250, 300, 350, 400)   # sealed observation times


# --------------------------------------------------------------------------- supports
def _disc(site, r=R_HALO):
    yy, xx = np.mgrid[0:L, 0:L]
    return K._pd2(yy, xx, site[0], site[1]) <= r * r


def halo_supports():
    return {"A": _disc(K.SITE_A), "B": _disc(K.SITE_B)}


# ------------------------------------------------------------------ the two layer vectors
def core_vector(st):
    """FROZEN core marker vector: mass-weighted (m1, m2) over the component at each site.
    Reads Mf and rho only. Never reads c, N or provenance."""
    pick, _, _ = K.read_sites(st)
    out = {}
    m = st.Mf / np.maximum(st.rho, 1e-12)[None, :, :]
    for nm in ("A", "B"):
        e = pick[nm]
        if e is None:
            out[nm] = None
            continue
        ys, xs = e.cells[:, 0], e.cells[:, 1]
        w = st.rho[ys, xs]
        out[nm] = [float(np.average(m[0][ys, xs], weights=w)),
                   float(np.average(m[1][ys, xs], weights=w))]
    return out


def halo_vector(st, sup=None):
    """FROZEN halo vector: (mean c, mean N) over the frozen halo support disc. Reads c and N
    only. Never reads Mf, rho or provenance. It does not depend on whether a component is alive,
    so it is defined for ORPHAN_HALO too."""
    sup = sup or halo_supports()
    return {nm: [float(st.c[sup[nm]].mean()), float(st.N[sup[nm]].mean())] for nm in ("A", "B")}


def geometry_vector(st):
    pick, dist, n = K.read_sites(st)
    out = {"n_components": n}
    for nm in ("A", "B"):
        e = pick[nm]
        out[nm] = None if e is None else {"size": int(e.size), "mass": float(e.mass),
                                          "rg": float(e.rg), "d_site": round(dist[nm], 3),
                                          "mean_sig": float(e.mean_sig),
                                          "specific_uptake": float(e.specific_uptake)}
    return out


# ------------------------------------------------------------------------- interventions
def halo_cross(st):
    """Reciprocal permutation of c and N only. Cores stay BIT-IDENTICAL."""
    out = st.copy()
    out.c = out.c[:, K.REFLECT_IX]
    out.N = out.N[:, K.REFLECT_IX]
    return out


def core_cross(st):
    """Reciprocal permutation of the frozen internal marker field Mf only."""
    out = st.copy()
    out.Mf = out.Mf[:, :, K.REFLECT_IX]
    return out


def double_cross(st):
    """Core and halo crossed together: the matched relationship is preserved, the two matched
    pairs simply change site."""
    return halo_cross(core_cross(st))


def core_erase(st):
    """Mf <- 0 everywhere. The necessity test for the internal state."""
    out = st.copy()
    out.Mf[:] = 0.0
    return out


def orphan_halo(st):
    """The core is removed while the initial c/N field is preserved exactly: rho, U, V, C and Mf
    are zeroed, c and N are untouched. This is the passive halo relaxation reader."""
    out = st.copy()
    out.rho[:] = 0.0
    out.U[:] = 0.0
    out.V[:] = 0.0
    out.C[:] = 0.0
    out.Mf[:] = 0.0
    out.uptake[:] = 0.0
    return out


def matched_sham(st):
    return st.copy()


# ------------------------------------------------------------------------------- engines
def engine(writer_off=False, pulse_chase=False):
    mc = MCParams(lam_plus=C.MC.lam_plus, lam_minus=(0.0 if writer_off else C.MC.lam_minus))
    tr = PulseChaseTracer() if pulse_chase else C.TRACER
    return MultiChannelMemoryEngine(C.SPEC, mc, tr)


# ------------------------------------------------------------------------- the challenge
def challenge(eng, st):
    """The frozen DOMC probe, unchanged: a global nutrient challenge, read at each frozen site as
    perturbed minus a matched unperturbed control fork."""
    return K.response_at_sites(eng, st)


# ---------------------------------------------------------------- intervention verification
def ledger(before, after, name):
    """Immediate verification of every mandated quantity for one intervention."""
    sup = halo_supports()
    d = {"intervention": name}
    for f in ("rho", "U", "V", "C", "Mf", "c", "N"):
        a, b = getattr(before, f), getattr(after, f)
        d[f] = {"changed": bool(not np.array_equal(a, b)),
                "sum_before": float(np.asarray(a, float).sum()),
                "sum_after": float(np.asarray(b, float).sum()),
                "multiset_preserved": bool(np.array_equal(np.sort(np.asarray(a).ravel()),
                                                          np.sort(np.asarray(b).ravel()))),
                "n_sites_changed": int((np.asarray(a) != np.asarray(b)).sum())}
    d["core_geometry_unchanged"] = bool(np.array_equal(before.rho, after.rho))
    d["halo_hist_c_before"] = np.histogram(before.c, bins=12, range=(0, 3))[0].tolist()
    d["halo_hist_c_after"] = np.histogram(after.c, bins=12, range=(0, 3))[0].tolist()
    d["halo_hist_N_before"] = np.histogram(before.N, bins=12, range=(0, 2))[0].tolist()
    d["halo_hist_N_after"] = np.histogram(after.N, bins=12, range=(0, 2))[0].tolist()
    mb = before.Mf / np.maximum(before.rho, 1e-12)[None, :, :]
    ma = after.Mf / np.maximum(after.rho, 1e-12)[None, :, :]
    d["marker_hist_before"] = np.histogram(mb, bins=12, range=(-1, 1))[0].tolist()
    d["marker_hist_after"] = np.histogram(ma, bins=12, range=(-1, 1))[0].tolist()
    d["halo_support_means_before"] = halo_vector(before, sup)
    d["halo_support_means_after"] = halo_vector(after, sup)
    d["global_mass_before"] = float(before.rho.sum())
    d["global_mass_after"] = float(after.rho.sum())
    d["realized_global_c_before"] = float(before.c.sum())
    d["realized_global_c_after"] = float(after.c.sum())
    d["realized_global_N_before"] = float(before.N.sum())
    d["realized_global_N_after"] = float(after.N.sum())
    return d


INTERVENTIONS = {
    "MATCHED_SHAM": matched_sham,
    "HALO_CROSS": halo_cross,
    "CORE_CROSS": core_cross,
    "DOUBLE_CROSS": double_cross,
    "HALO_CROSS_CORE_ERASE": lambda s: core_erase(halo_cross(s)),
    "HALO_CROSS_WRITER_OFF": halo_cross,          # the ablation is in the ENGINE, not the state
    "ORPHAN_HALO": orphan_halo,
    "HALO_PULSE_RESTORE": halo_cross,             # restored later, inside the run
}
ARMS = tuple(INTERVENTIONS)
WRITER_OFF_ARMS = {"HALO_CROSS_WRITER_OFF"}
PULSE_ARMS = {"HALO_PULSE_RESTORE"}
TURNOVER_ARMS = {"MATCHED_SHAM", "HALO_CROSS", "HALO_CROSS_CORE_ERASE"}
