"""DUAL_OWNER_MEMORY_COLLISION_00 — core.

The LawSpec is FROZEN and imported, never edited: `edlab.experiments.sc_mcm.engine`
(`MultiChannelMemoryEngine`, `MCParams(lam_plus=0.25, lam_minus=0.15)`) on the frozen
`ScaffoldSpec` of `exp_sc_00` with `beta=0.10`. No parameter of the physics is touched here.
No new field, no new memory channel, no controller, no new detector threshold.

Three things are new, and all three are experimental protocol, not physics:

  1. FOUNDING. The initial support of rho is restricted to two Gaussian caps of width
     `W_FOUND = 3.0` at the frozen sites A=(32,16) and B=(32,48). Everything that rides rho
     (U, V, C) is multiplied by the same mask, so `sum_c C == rho` still holds exactly and the
     internal fields are the frozen seed's. Probe 1 established that this founding yields
     EXACTLY TWO detected components from t=100 to t>=1550 across seeds, each pinned to its site
     within 0.2 lattice cells.

  2. LOCALIZED DRIVING. The frozen history alphabet adds a constant to N or to c. Here the same
     constant is added on ONE HALF-PLANE only: half A is x in [0,32), half B is x in [32,64).
     The two sites sit at the centre of their half, 16 cells from either interface. Nothing else
     changes: same handles, same amplitude, same phase length.

  3. TWO GEOMETRIC OPERATIONS ON THE MEMORY FIELD ALONE.
       - selective erase:  Mf <- 0 on one half-plane;
       - reciprocal core exchange:  Mf <- roll(Mf, 32, x). Because the two sites are exactly
         L/2 apart, this maps half A onto half B and half B onto half A. It is a PERMUTATION of
         lattice sites, so sum(Mf) is preserved exactly and by construction, and applying it
         twice is the identity. It touches Mf and nothing else: rho, U, V, c, N and C are
         untouched, so the material bodies do not move.

The two sites are FROZEN GEOMETRY and are the only addressing information any online operation
uses. Provenance (the cohort field C) is never read by any reader or any operation; it is used
only by the auditor, for the turnover criterion, which is the frozen one (M <= M_LOW = 0.35).
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/home/claude/sweep")
import numpy as np

from edlab.experiments.sc_mcm import harness as H, config as C
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine
from edlab.experiments.sc_iom.engine import IOMState
from edlab.experiments.sc_hmc.harness import PulseChaseTracer

# ----------------------------------------------------------------- frozen geometry & timing
L = C.SPEC.size                     # 64
GEOMETRY = {"FAR": ((32, 16), (32, 48)),     # separation 32 = L/2
            "NEAR": ((32, 24), (32, 40))}    # separation 16
SITE_A, SITE_B = GEOMETRY["FAR"]
DX_AB = 32                          # FAR only: the translation roll(., DX_AB, axis=-1)
REFLECT_IX = (L - np.arange(L)) % L  # x -> (L - x) mod L : an involution fixing x = 0 and 32,
                                     # and exchanging the two sites of EITHER geometry
W_FOUND = 3.0                       # probe 1: the only width giving a stable exact pair
T_FOUND = 150                       # relaxation before any history
R_SITE = 6.0                        # reader radius: a component further than this from its
                                    # frozen site is NOT that site's component (reader gate,
                                    # not a physics threshold; the detector is untouched)
T_PHASE = 60                        # frozen from sc_mcm (T)
AMP = 0.03                          # frozen from sc_mcm (AMP)
SETTLE = C.SETTLE                   # 120, frozen
PROBE = C.PROBE                     # ("N", "add", 0.50, 15), frozen
PROBE_HORIZON = C.PROBE_HORIZON     # 120, frozen
PROBE_CADENCE = C.PROBE_CADENCE     # 30, frozen
RESP_SCALE = np.array(C.RESP_SCALE)  # frozen
M_LOW = C.M_LOW                     # 0.35, frozen
T_TURN = C.TURNOVER_STEPS           # 700, the FROZEN parent turnover horizon; not tuned here

HALF_A = slice(0, L // 2)           # x in [0,32)
HALF_B = slice(L // 2, L)           # x in [32,64)

# FROZEN history alphabet. A history is a 2-character code over the three primitives the frozen
# sc_mcm alphabet already contains: "N" = add AMP to nutrient, "c" = add AMP to attractant,
# "0" = add nothing. Nothing outside this alphabet may be used. "Nc" and "cN" are exactly the
# frozen sc_mcm H1 and H2.
PRIM = {"N": (AMP, 0.0), "c": (0.0, AMP), "0": (0.0, 0.0)}


def mkhist(code):
    return tuple((ch, T_PHASE) + PRIM[ch] for ch in code)


HIST = {"H1": mkhist("Nc"), "H2": mkhist("cN")}   # kept for backward reference

# The eight candidate history PAIRS of Phase C. The selection among them is made on DEV, on the
# frozen scalar dictionary only, and never on any endpoint.
CANDIDATE_PAIRS = (("Nc", "cN"), ("NN", "cc"), ("NN", "00"), ("cc", "00"),
                   ("Nc", "00"), ("N0", "0N"), ("NN", "Nc"), ("cN", "cc"))

# frozen scalar dictionary (Phase C). Measured per site on the settled state, before any probe.
SCALAR_CONFOUND = ("mass", "size", "rg", "mean_sig", "specific_uptake",
                   "local_mean_c", "local_mean_N")
SCALAR_MEMORY = ("m_plus", "m_minus")


# ------------------------------------------------------------------------------- founding
def _pd2(ay, ax, cy, cx, n=L):
    dy = np.abs(ay - cy); dy = np.minimum(dy, n - dy)
    dx = np.abs(ax - cx); dx = np.minimum(dx, n - dx)
    return dy ** 2 + dx ** 2


def set_geometry(name):
    """FROZEN before execution. Two geometries only, both symmetric about x = L/2, so that the
    same reciprocal permutation (the reflection x -> (L-x) mod L) exchanges the two sites in
    both. No third geometry and no additional distance may be added later."""
    global SITE_A, SITE_B
    SITE_A, SITE_B = GEOMETRY[name]
    return name


def _blob(w=W_FOUND):
    ys = np.arange(L)[:, None] * np.ones((1, L))
    xs = np.ones((L, 1)) * np.arange(L)[None, :]
    m = np.zeros((L, L))
    for cy, cx in (SITE_A, SITE_B):
        m = np.maximum(m, np.exp(-_pd2(ys, xs, cy, cx) / (2.0 * w * w)))
    return m


def found(seed, w=W_FOUND):
    s = C.seed_state(C.SPEC, C.TRACER, seed, "random")
    m = _blob(w)
    return IOMState(s.rho * m, s.U * m, s.V * m, s.c.copy(), s.N.copy(), s.C * m,
                    s.uptake.copy(), np.zeros((C.MC.n_comp, L, L)), 0)


def engine():
    return H.mc_engine()


def pc_engine():
    """same LawSpec, pulse-chase cohorts: the frozen turnover instrument."""
    return MultiChannelMemoryEngine(C.SPEC, C.MC, PulseChaseTracer())


def relabel(st):
    out = st.copy()
    out.C = np.stack([out.rho.copy(), np.zeros_like(out.rho)])
    return out


def advance(eng, st, steps):
    cur = st.copy()
    for _ in range(steps):
        cur = eng.step(cur)
    return cur


# ------------------------------------------------------------ provenance-blind site reader
def read_sites(st):
    """For each frozen site, the detected component whose circular centroid is nearest, if it is
    within R_SITE and is not also the other site's component. Uses ONLY the frozen detector and
    the frozen sites. Never reads C, Mf, history labels or any future value."""
    es = H.entities(st)
    pick, dist = {}, {}
    for nm, (cy, cx) in (("A", SITE_A), ("B", SITE_B)):
        best, bd = None, 1e9
        for e in es:
            d = float(np.sqrt(_pd2(np.array(float(e.centroid[0])),
                                   np.array(float(e.centroid[1])), cy, cx)))
            if d < bd:
                best, bd = e, d
        pick[nm] = best if (best is not None and bd <= R_SITE) else None
        dist[nm] = bd
    if pick["A"] is not None and pick["A"] is pick["B"]:
        pick["A"] = pick["B"] = None            # merged: neither site has its own component
    return pick, dist, len(es)


def _feat_site(st, e):
    """The frozen 5-feature vector, read on a GIVEN component instead of on `largest`."""
    if e is None:
        return np.zeros(5)
    ys, xs = e.cells[:, 0], e.cells[:, 1]
    return np.array([e.size, e.rg, e.specific_uptake, e.mass,
                     float(st.c[ys, xs].mean())])


def scalars(st):
    """The frozen scalar dictionary, per site, on the current state."""
    pick, _, _ = read_sites(st)
    out = {}
    for nm in ("A", "B"):
        e = pick[nm]
        if e is None:
            out[nm] = None
            continue
        ys, xs = e.cells[:, 0], e.cells[:, 1]
        w = st.rho[ys, xs]
        m = st.mem()
        m1 = float(np.average(m[0][ys, xs], weights=w))
        m2 = float(np.average(m[1][ys, xs], weights=w))
        out[nm] = {"mass": float(e.mass), "size": float(e.size), "rg": float(e.rg),
                   "mean_sig": float(e.mean_sig),
                   "specific_uptake": float(e.specific_uptake),
                   "local_mean_c": float(st.c[ys, xs].mean()),
                   "local_mean_N": float(st.N[ys, xs].mean()),
                   "m_plus": m1 + m2, "m_minus": m1 - m2}
    return out


def turnover_M(st):
    """The frozen material-turnover criterion, per component: the fraction of a component's mass
    that still belongs to the cohort present at the relabel. Requires a pulse-chase state."""
    pick, _, _ = read_sites(st)
    out = {}
    for nm in ("A", "B"):
        e = pick[nm]
        if e is None:
            out[nm] = None
            continue
        cm = np.asarray(e.cohort_mass, float)
        out[nm] = float(cm[0] / cm.sum()) if cm.sum() > 0 else 1.0
    return out


# --------------------------------------------------------------------- localized histories
def apply_dual_history(eng, st, hA, hB):
    """Apply history hA on half-plane A and hB on half-plane B, in lockstep. Both histories have
    the same phase structure, so at every step exactly one additive constant is delivered to each
    half. The GLOBAL forcing time series (total dN and total dc added per step, summed over the
    lattice) is therefore IDENTICAL between any two assignments built from the same two
    histories -- which is what makes H_GLOBAL testable."""
    a = HIST[hA] if hA in HIST else mkhist(hA)
    b = HIST[hB] if hB in HIST else mkhist(hB)
    assert len(a) == len(b)
    cur = st.copy()
    for ph in range(len(a)):
        _, na, dNa, dca = a[ph]
        _, nb, dNb, dcb = b[ph]
        assert na == nb
        for _ in range(na):
            if dNa:
                cur.N[:, HALF_A] = cur.N[:, HALF_A] + dNa
            if dNb:
                cur.N[:, HALF_B] = cur.N[:, HALF_B] + dNb
            if dca:
                cur.c[:, HALF_A] = cur.c[:, HALF_A] + dca
            if dcb:
                cur.c[:, HALF_B] = cur.c[:, HALF_B] + dcb
            cur = eng.step(cur)
    return cur


def global_forcing_trace(hA, hB):
    """Auditor-side check that two assignments have identical global forcing."""
    a = HIST[hA] if hA in HIST else mkhist(hA)
    b = HIST[hB] if hB in HIST else mkhist(hB)
    tr = []
    half = L * (L // 2)
    for ph in range(len(a)):
        _, na, dNa, dca = a[ph]
        _, _, dNb, dcb = b[ph]
        for _ in range(na):
            tr.append((round((dNa + dNb) * half, 12), round((dca + dcb) * half, 12)))
    return tr


# ------------------------------------------------ geometric operations on the memory field
def erase_half(st, which):
    out = st.copy()
    sl = HALF_A if which == "A" else HALF_B
    out.Mf[:, :, sl] = 0.0
    return out


def erase_sham(st):
    """Identical code path, factor 1.0: verifies the harness itself perturbs nothing."""
    out = st.copy()
    out.Mf[:, :, HALF_A] = out.Mf[:, :, HALF_A] * 1.0
    return out


def reciprocal_cross(st):
    """THE globally conservative reciprocal state permutation: the reflection x -> (L-x) mod L
    applied to the memory field ALONE. It is a permutation of lattice sites, so sum(Mf) is
    preserved exactly and by construction; it is an involution, so applying it twice is the
    identity; it exchanges half A with half B and the two sites of EITHER frozen geometry; and
    rho, U, V, c, N, C are untouched, so the material bodies do not move."""
    out = st.copy()
    out.Mf = out.Mf[:, :, REFLECT_IX]
    return out


def reciprocal_cross_roll(st):
    """FAR geometry only, declared robustness variant: the pure translation by L/2. Same
    conservation properties, but it does NOT mirror the memory pattern inside each body. It
    exists to show that mirroring is not what produces the effect."""
    out = st.copy()
    out.Mf = np.roll(out.Mf, DX_AB, axis=-1)
    return out


def reciprocal_cross_env(st):
    """The SAME reciprocal permutation, applied to the two EXTERNAL HANDLES (the attractant c
    and the nutrient N) instead of to the memory field. It is the preregistered adjudicator for
    H_ENVIRONMENT: if the future responses follow the environment rather than the memory, this
    arm exchanges them and the memory-only arm does not. Mf, rho, U, V and C are untouched."""
    out = st.copy()
    out.c = out.c[:, REFLECT_IX]
    out.N = out.N[:, REFLECT_IX]
    return out


INTERVENTIONS = {
    "NONE": lambda s: s.copy(),
    "ERASE_A": lambda s: erase_half(s, "A"),
    "ERASE_B": lambda s: erase_half(s, "B"),
    "ERASE_SHAM": erase_sham,
    "CROSS": reciprocal_cross,
    "CROSS_ROLL": reciprocal_cross_roll,
    "CROSS_ENV": reciprocal_cross_env,
}


# --------------------------------------------------------------------------- causal readout
def _perturb_N(st, amp):
    out = st.copy()
    out.N = np.clip(out.N + amp * C.SPEC.N0, 0.0, None)
    return out


def response_at_sites(eng, st):
    """The frozen probe, applied GLOBALLY (a common challenge), read at each frozen site as the
    difference between the perturbed fork and a matched unperturbed control fork -- the sc_hmc
    definition of a causal response. Returns a 4x5 = 20-vector per site, scaled by RESP_SCALE."""
    field, op, amp, dur = PROBE
    assert (field, op) == ("N", "add")
    ctrl = st.copy()
    pert = _perturb_N(st, amp)
    cf, pf = [], []
    for t in range(1, PROBE_HORIZON + 1):
        ctrl = eng.step(ctrl)
        if 1 < t <= dur:
            pert = _perturb_N(pert, amp)
        pert = eng.step(pert)
        if t % PROBE_CADENCE == 0:
            pc, _, _ = read_sites(ctrl)
            pp, _, _ = read_sites(pert)
            cf.append([_feat_site(ctrl, pc["A"]), _feat_site(ctrl, pc["B"])])
            pf.append([_feat_site(pert, pp["A"]), _feat_site(pert, pp["B"])])
    cf = np.asarray(cf); pf = np.asarray(pf)             # (4, 2, 5)
    d = (pf - cf) / RESP_SCALE[None, None, :]
    return {"A": d[:, 0, :].ravel(), "B": d[:, 1, :].ravel(),
            "ctrl_A": (cf[:, 0, :] / RESP_SCALE).ravel(),
            "ctrl_B": (cf[:, 1, :] / RESP_SCALE).ravel()}


def dist(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    return float(np.linalg.norm(a - b) / np.sqrt(len(a)))
