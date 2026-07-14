"""EXP-GT-CAUSAL-RESPONSE-DECOMPOSITION-00 -- development / prospective split. Committed BEFORE the instrument.

The historical continuous-fingerprint hold-out is NOT used here. It stays sealed as a historical asset. This
programme has its own split, its own seeds (6xx dev / 7xx prospective, disjoint from every previous namespace) and
its own claim.

EVERY CASE IS `base` VERSUS `base + ONE EXTRA PATH`, so the accessible DIFFERENCE TRACE is EXACTLY that path's
response and the ground-truth profile is a DESIGN PARAMETER rather than an accident of subtraction.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from . import decomp as D
from . import systems as S
from .systems import SIG0

DEV_SEED, PRO_SEED = 600_000, 700_000
SG = SIG0

ESTIMATED, LOWER_BOUND_ONLY, INDETERMINATE, OUT_OF_SCOPE = \
    "ESTIMATED", "LOWER_BOUND_ONLY", "INDETERMINATE", "OUT_OF_SCOPE"
EQUIVALENCE_CLASS_ONLY = "EQUIVALENCE_CLASS_ONLY"


@dataclass
class Case:
    cid: str
    left: str
    right: str
    expect: dict            # per-axis ground-truth expectation: "zero" | "nonzero" | "any"
    why: str
    common_channel: bool = True
    tags: tuple = field(default_factory=tuple)


# ---- weights solved on the PRIVILEGED noise-free traces so the two targeted controls are EXACT by construction
W_EQ_ENERGY = 0.464     # BROAD weight that equalises transient ENERGY with SPIKE(1,3) -> peaks then differ 2.9x
W_EQ_PEAK = 1.319       # BROAD weight that equalises PEAK with SPIKE(1,3)             -> energies differ 8.1x


def dev_systems() -> dict:
    b = D.base("K_base", T=8.0, gain=1.0, sigma=SG)
    return {
        "K_base": b,
        # --- pure axes
        "K_trans": D.plus_path("K_trans", b, w=1.0, Tx=8.0),                       # transient only, P=0
        "K_trans2": D.plus_path("K_trans2", b, w=1.0, Tx=20.0),                    # slower transient, P=0
        "K_persist": D.plus_path("K_persist", b, w=1.0, Tx=60.0, persistent=True),  # INTEGRATOR -> P != 0
        "K_persist_s": D.plus_path("K_persist_s", b, w=0.35, Tx=60.0, persistent=True),
        "K_latency": D.plus_path("K_latency", b, w=1.0, Tx=8.0, delay=25),         # same shape, later
        # --- the peak/energy dissociation controls
        "K_spike": D.plus_spike("K_spike", b, w=1.0, Tf=1.0, Ts=3.0),
        "K_broad_E": D.plus_broad("K_broad_E", b, w=W_EQ_ENERGY, T1=30.0, T2=30.0),  # EQUAL ENERGY to K_spike
        "K_broad_A": D.plus_broad("K_broad_A", b, w=W_EQ_PEAK, T1=30.0, T2=30.0),    # EQUAL PEAK   to K_spike
        # --- functional axes (preserved from the old programme's ontology, re-qualified here)
        "K_gain": D.base("K_gain", T=8.0, gain=2.0, sigma=SG),
        "K_sign": D.base("K_sign", T=8.0, gain=-1.0, sigma=SG),
        "K_mem_p": S.memory("K_mem_p", mem0=+1.0, T=8.0, Tm=5.0, gain=1.0, k_out=1.2, sigma=SG),
        "K_mem_m": S.memory("K_mem_m", mem0=-1.0, T=8.0, Tm=5.0, gain=1.0, k_out=1.2, sigma=SG),
        "K_hidden": S.hidden_mode("K_hidden", b, c_h=1.2, T=9.0),                  # limited-access collision
        # --- continuity
        "K_dead": S.dead_site("K_dead", b, x0_5=0.6),
        "K_units": S.with_units("K_units", b, a=700.0, b=0.25),
        "K_fine": S.with_refined_solver("K_fine", b),
        # --- noise / drift discrimination
        "K_drift": D.with_drift("K_drift", b, frac=8.0),                            # DRIFT, no extra response
        "K_slowresp": D.with_drift("K_slow0", D.plus_path("K_slowresp", b, w=0.5, Tx=35.0), frac=0.0),
        "K_slow_drift": D.with_drift("K_slow_drift", D.plus_path("K_sd", b, w=0.5, Tx=35.0), frac=8.0),
        # --- abstention
        "K_silent": S.silent_dead("K_silent", sigma=SG),
        "K_noisy": D.with_noise("K_noisy", b, mult=250.0),
        "K_lowcov": S.access_restricted("K_lowcov", S.supply_cause("K_lc", b, w_s=0.9, site=3, T=7.0, gain=0.8),
                                        blocked=(S.DRIVE,)),
    }


DEV_CASES = [
    Case("Z-01", "K_base", "K_base", {"P": "zero", "E": "zero", "A": "zero"},
         "THE NULL. No causal difference at all.", tags=("null",)),
    Case("Z-02", "K_base", "K_trans", {"P": "zero", "E": "nonzero", "A": "nonzero"},
         "PURE TRANSIENT: a bounded discrepancy with an IDENTICAL asymptote. The old RMS scalar sent this to zero "
         "as the window grew; an INTEGRAL must not.", tags=("transient", "G2")),
    Case("Z-03", "K_base", "K_persist", {"P": "nonzero", "E": "nonzero", "A": "nonzero"},
         "PURE PERSISTENT: an integrator path, so a bounded probe leaves a PERMANENT step.",
         tags=("persistent", "G3")),
    Case("Z-04", "K_base", "K_latency", {"P": "zero", "E": "nonzero", "A": "nonzero", "L": "nonzero"},
         "SAME SHAPE, LATER. Only the latency axis may move.", tags=("latency", "G4")),
    Case("Z-05", "K_base", "K_spike", {"P": "zero", "E": "nonzero", "A": "nonzero"},
         "TALL AND BRIEF.", tags=("peak_energy",)),
    Case("Z-06", "K_base", "K_broad_E", {"P": "zero", "E": "nonzero", "A": "nonzero"},
         "EQUAL TRANSIENT ENERGY to Z-05 BY CONSTRUCTION, and a peak 2.9x smaller. G5 lives here.",
         tags=("peak_energy", "G5_equal_energy")),
    Case("Z-07", "K_base", "K_broad_A", {"P": "zero", "E": "nonzero", "A": "nonzero"},
         "EQUAL PEAK to Z-05 BY CONSTRUCTION, and 8.1x the transient energy. G5 lives here too.",
         tags=("peak_energy", "G5_equal_peak")),
    Case("Z-08", "K_base", "K_gain", {"P": "zero", "E": "nonzero", "A": "nonzero"},
         "gain x2 -- a functional difference that is nevertheless purely transient here", tags=("gain",)),
    Case("Z-09", "K_base", "K_sign", {"P": "zero", "E": "nonzero", "A": "nonzero"},
         "sign inversion", tags=("sign",)),
    Case("Z-10", "K_mem_p", "K_mem_m", {"P": "nonzero", "E": "nonzero", "A": "nonzero"},
         "HIDDEN STATE: a transient intervention leaves a persistent change. The persistent axis must separate.",
         tags=("hidden_state", "G3")),
    Case("Z-11", "K_base", "K_hidden", {"P": "zero", "E": "zero", "A": "zero"},
         "LIMITED-ACCESS COLLISION: bit-for-bit identical under the limited repertoire, separable under rich. "
         "EQUIVALENCE_CLASS_ONLY -- never an identity claim.", tags=("collision", "G11")),
    Case("Z-12", "K_base", "K_dead", {"P": "zero", "E": "zero", "A": "zero"},
         "an extra internal degree of freedom, invisible in both arms", tags=("continuity",)),
    Case("Z-13", "K_base", "K_units", {"P": "zero", "E": "zero", "A": "zero"},
         "u -> 700u + 0.25. A change of units is not a causal difference.", tags=("units", "G12")),
    Case("Z-14", "K_base", "K_fine", {"P": "zero", "E": "zero", "A": "zero"},
         "solver refinement", tags=("solver",)),
    Case("Z-15", "K_drift", "K_drift", {"P": "zero", "E": "zero", "A": "zero"},
         "DRIFT WITHOUT RESPONSE, compared with itself. Drift must NOT become a persistent causal difference.",
         tags=("drift_only", "G8")),
    Case("Z-16", "K_base", "K_slowresp", {"P": "zero", "E": "nonzero", "A": "nonzero"},
         "A SLOW CAUSAL RESPONSE WITHOUT DRIFT. It must NOT be mistaken for drift and removed.",
         tags=("slow_response", "G8")),
    Case("Z-17", "K_base", "K_slow_drift", {"P": "zero", "E": "nonzero", "A": "nonzero"},
         "A SLOW CAUSAL RESPONSE **AND** HEAVY DRIFT TOGETHER. Distinguish them, or abstain -- but do not silently "
         "call the response drift, nor the drift a response.", tags=("slow_and_drift", "G8")),
    Case("Z-18", "K_silent", "K_base", {"P": "any", "E": "any", "A": "any"},
         "silent system: no responsiveness", tags=("silent",)),
    Case("Z-19", "K_noisy", "K_base", {"P": "any", "E": "any", "A": "any"},
         "below its own noise floor", tags=("noise", "G7")),
    Case("Z-20", "K_lowcov", "K_base", {"P": "any", "E": "any", "A": "any"},
         "drive line unreachable: coverage below floor", tags=("coverage",)),
]


def pro_systems() -> dict:
    """PROSPECTIVE -- RESERVED, NOT INSPECTED. Disjoint parameter grid on every axis.

        base T   dev 8      -> prospective 11
        Tx       dev {8,20,60,35}  -> prospective {5,13,28,45,50}
        spike    dev (1,3)  -> prospective (1.5,4.5)
        broad    dev (30,30)-> prospective (26,26)
        delay    dev 25     -> prospective 35
        gain     dev {2,-1} -> prospective {2.6,-1.5}
        sigma    dev 1e-5   -> prospective {1.4e-5}   UNSEEN
        RESERVED TOPOLOGY: a THIRD-ORDER cascade extra path -- development never sees one.
    """
    SGP = 1.4e-5
    b = D.base("Q_base", T=11.0, gain=1.0, sigma=SGP)
    # weights re-solved for the prospective spike/broad geometry (privileged, see the split manifest)
    return {
        "Q_base": b,
        "Q_trans": D.plus_path("Q_trans", b, w=1.0, Tx=13.0),
        "Q_persist": D.plus_path("Q_persist", b, w=1.0, Tx=45.0, persistent=True),
        "Q_latency": D.plus_path("Q_latency", b, w=1.0, Tx=13.0, delay=35),
        "Q_spike": D.plus_spike("Q_spike", b, w=1.0, Tf=1.5, Ts=4.5),
        "Q_broad_E": D.plus_broad("Q_broad_E", b, w=1.0, T1=26.0, T2=26.0),   # weight fixed at freeze
        "Q_broad_A": D.plus_broad("Q_broad_A", b, w=1.0, T1=26.0, T2=26.0),   # weight fixed at freeze
        "Q_casc3": D.plus_broad("Q_casc3", b, w=1.0, T1=5.0, T2=28.0),        # RESERVED: unseen geometry
        "Q_gain": D.base("Q_gain", T=11.0, gain=2.6, sigma=SGP),
        "Q_sign": D.base("Q_sign", T=11.0, gain=-1.5, sigma=SGP),
        "Q_mem_p": S.memory("Q_mem_p", mem0=+1.0, T=11.0, Tm=6.0, gain=1.0, k_out=1.3, sigma=SGP),
        "Q_mem_m": S.memory("Q_mem_m", mem0=-1.0, T=11.0, Tm=6.0, gain=1.0, k_out=1.3, sigma=SGP),
        "Q_hidden": S.hidden_mode("Q_hidden", b, c_h=0.9, T=13.0),
        "Q_dead": S.dead_site("Q_dead", b, x0_5=-0.4),
        "Q_units": S.with_units("Q_units", b, a=150.0, b=-0.07),
        "Q_fine": S.with_refined_solver("Q_fine", b),
        "Q_drift": D.with_drift("Q_drift", b, frac=9.0),
        "Q_slowresp": D.with_drift("Q_s0", D.plus_path("Q_slowresp", b, w=0.5, Tx=50.0), frac=0.0),
        "Q_slow_drift": D.with_drift("Q_slow_drift", D.plus_path("Q_sd", b, w=0.5, Tx=50.0), frac=9.0),
        "Q_silent": S.silent_dead("Q_silent", sigma=SGP),
        "Q_noisy": D.with_noise("Q_noisy", b, mult=300.0),
        "Q_lowcov": S.access_restricted("Q_lowcov", S.supply_cause("Q_lc", b, w_s=1.1, site=3, T=13.0, gain=0.9),
                                        blocked=(S.DRIVE,)),
    }
