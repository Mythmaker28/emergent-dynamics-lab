"""CRD-02 SPLIT + CASE MANIFEST. Committed BEFORE any fitting.

NEW split -- the CRD-01 hold-out is burned, and CRD-02 changes the acquisition again (paired episodes with
per-episode references), so a split earned under CRD-01 was earned under a different instrument.

Development systems reuse the historical CRD-00/01 response constructions (so the Z-17 regression is EXACT) plus
the CRD-02 topologies. Prospective systems reserve UNSEEN combinations: third-order, underdamped, hidden state,
sign flip, multiscale, feedback -- crossed with acquisition stressors the dev split never pairs them with.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import decomp as D, decomp2 as D2
from .pacq import PContract
from .systems import silent_dead

DEV_SEED, PRO_SEED = 1_100_000, 1_200_000
R_REPEATS = 16

# equal-energy / equal-peak SPIKE vs BROAD weights (historical, from manifests_crd)
W_EQ_ENERGY = 0.464
W_EQ_PEAK = 1.319


def dev_systems():
    b = D.base("P_base")
    return {
        "P_base": b,
        "P_slowresp": D.plus_path("P_slowresp", b, w=0.5, Tx=35.0),            # D1 Z-17: the slow response
        "P_persist": D.plus_path("P_persist", b, w=1.0, Tx=60.0, persistent=True),
        "P_spike": D.plus_spike("P_spike", b, w=1.0, Tf=1.0, Ts=3.0),
        "P_broadE": D.plus_broad("P_broadE", b, w=W_EQ_ENERGY, T1=30.0, T2=30.0),  # equal ENERGY to spike
        "P_broadA": D.plus_broad("P_broadA", b, w=W_EQ_PEAK, T1=30.0, T2=30.0),    # equal PEAK   to spike
        "P_hidden": D2.plus_hidden("P_hidden", b, w=0.6),
        "P_silent": silent_dead("P_silent"),
        "P_transient": D.plus_path("P_transient", b, w=0.8, Tx=8.0),
        "P_replace": D.plus_path("P_replace", b, w=0.7, Tx=10.0),              # transient history, recovers
    }


def pro_systems():
    b = D.base("Q_base")
    return {
        "Q_base": b,
        "Q_cascade3": D2.plus_cascade3("Q_cascade3", b, w=1.0),                # UNSEEN: third order
        "Q_underdamped": D2.plus_underdamped("Q_underdamped", b, w=1.0),       # UNSEEN: ringing
        "Q_hidden": D2.plus_hidden("Q_hidden", b, w=0.6),
        "Q_signflip": D2.plus_signflip("Q_signflip", b, w=1.0),               # UNSEEN: sign inversion
        "Q_multiscale": D2.plus_multiscale("Q_multiscale", b, w=1.0),          # UNSEEN: two timescales
        "Q_feedback": D2.plus_feedback("Q_feedback", b, w=1.0),               # UNSEEN: feedback
        "Q_persist": D.plus_path("Q_persist", b, w=1.0, Tx=60.0, persistent=True),
        "Q_slowresp": D.plus_path("Q_slowresp", b, w=0.5, Tx=35.0),
        "Q_silent": silent_dead("Q_silent"),
    }


HEAVY = dict(drift_sigma=2.0e-5, f_fast=0.35)          # the regime that killed CRD-00


@dataclass
class PCase:
    cid: str
    sysA: str          # reference system (the "base" arm)
    sysB: str          # responding system (the "active" arm carries sysB's response)
    contract: PContract
    truth: dict
    note: str


def _C(**kw):
    p = dict(HEAVY); p.update(kw)
    return PContract(**p)


def dev_cases():
    return [
        PCase("D1", "P_base", "P_slowresp", _C(),
              {"E": "nonzero", "P": "zero", "A": "nonzero", "adm": "ADM"},
              "*** Z-17 REGRESSION *** slow response under heavy drift, NO oracle twin, per-episode references"),
        PCase("D2", "P_base", "P_slowresp", _C(delta_A=3, delta_S=7),
              {"E": "nonzero", "P": "zero", "A": "nonzero", "adm": "ADM"},
              "different drift realizations AND different coupling delays across episodes -- must still recover"),
        PCase("D3", "P_base", "P_slowresp", _C(no_reference=True),
              {"adm": "REJECT"}, "CRD-00 design: no per-episode reference. Must fail admission (must-fail #1)"),
        PCase("D4", "P_base", "P_slowresp", _C(kap_A=0.12),
              {"adm": "CONTAM"}, "reference contamination: r_A leaks 12% of the causal response. Detect/abstain"),
        PCase("D5a", "P_base", "P_slowresp", _C(b_A=1.4),
              {"adm": "ADM"}, "reference gain mismatch, INSIDE the declared correction range"),
        PCase("D5b", "P_base", "P_slowresp", _C(b_A=3.0),
              {"adm": "ADM_OR_REJECT"}, "reference gain mismatch, boundary"),
        PCase("D6a", "P_base", "P_slowresp", _C(eta_A=8),
              {"adm": "ADM"}, "reference lag mismatch, inside the declared lag range"),
        PCase("D6b", "P_base", "P_slowresp", _C(eta_A=24),
              {"adm": "REJECT"}, "reference lag mismatch, OUTSIDE the lag range -- must reject"),
        PCase("D7", "P_base", "P_slowresp", _C(ref_fast_gain=0.0),
              {"adm": "ADM_OR_REJECT"}, "reference misses the fast drift entirely (bandwidth). Abstain or expose U"),
        PCase("D8", "P_base", "P_slowresp", _C(loc_A=1.5),
              {"adm": "REJECT"}, "local unshared drift on y not r -- the frontier where response is unidentifiable"),
        PCase("D9", "P_base", "P_base", _C(base_A=0.0, base_S=8.0e-4),
              {"E": "zero", "P": "zero", "A": "zero", "adm": "ADM"},
              "baseline mismatch ONLY, no causal response -- all causal axes must be zero-compatible"),
        PCase("D10", "P_base", "P_persist", _C(base_S=8.0e-4),
              {"E": "nonzero", "P": "nonzero", "A": "nonzero", "adm": "ADM"},
              "persistent causal response ON TOP of baseline mismatch -- persistence must survive"),
        PCase("D11", "P_base", "P_transient", _C(),
              {"E": "nonzero", "P": "zero", "A": "nonzero", "adm": "ADM"}, "pure transient plus drift"),
        PCase("D12", "P_base", "P_replace", _C(),
              {"E": "nonzero", "P": "zero", "A": "nonzero", "adm": "ADM"},
              "replacement/recovery: nonzero transient history, zero-compatible persistence after recovery"),
        PCase("D13", "P_base", "P_hidden", _C(),
              {"E": "nonzero", "P": "nonzero", "A": "nonzero", "adm": "ADM"},
              "hidden state: the persistent difference lives in a variable never read out"),
        PCase("D14a", "P_spike", "P_broadE", _C(),
              {"peak_ratio": ">1", "adm": "ADM"}, "equal ENERGY, different PEAK -- factorization control"),
        PCase("D14b", "P_spike", "P_broadA", _C(),
              {"energy_ratio": ">1", "adm": "ADM"}, "equal PEAK, different ENERGY -- factorization control"),
        PCase("D15", "P_base", "P_slowresp", _C(),
              {"adm": "ADM"}, "limited-access collision handled as EQUIVALENCE_CLASS_ONLY at report time"),
    ]


def pro_cases():
    return [
        PCase("Q1", "Q_base", "Q_slowresp", _C(), {"E": "nonzero", "P": "zero", "A": "nonzero"}, "slow + drift"),
        PCase("Q2", "Q_base", "Q_cascade3", _C(), {"E": "nonzero", "P": "zero", "A": "nonzero"}, "third order + drift"),
        PCase("Q3", "Q_base", "Q_underdamped", _C(), {"E": "nonzero", "P": "zero", "A": "nonzero"}, "ringing + drift"),
        PCase("Q4", "Q_base", "Q_hidden", _C(), {"E": "nonzero", "P": "nonzero", "A": "nonzero"}, "hidden persistent"),
        PCase("Q5", "Q_base", "Q_signflip", _C(), {"E": "nonzero", "P": "zero", "A": "nonzero"}, "sign inversion"),
        PCase("Q6", "Q_base", "Q_multiscale", _C(), {"E": "nonzero", "P": "zero", "A": "nonzero"}, "two timescales"),
        PCase("Q7", "Q_base", "Q_feedback", _C(), {"E": "nonzero", "P": "zero", "A": "nonzero"}, "feedback"),
        PCase("Q8", "Q_base", "Q_persist", _C(base_S=8.0e-4), {"E": "nonzero", "P": "nonzero", "A": "nonzero"}, "persist+baseline"),
        PCase("Q9", "Q_base", "Q_base", _C(base_S=8.0e-4), {"E": "zero", "P": "zero", "A": "zero"}, "baseline-only null"),
        PCase("Q10", "Q_base", "Q_slowresp", _C(no_reference=True), {"adm": "REJECT"}, "no reference -> reject"),
        PCase("Q11", "Q_base", "Q_slowresp", _C(kap_A=0.12), {"adm": "CONTAM"}, "contaminated ref -> reject"),
        PCase("Q12", "Q_base", "Q_slowresp", _C(loc_A=1.5), {"adm": "REJECT"}, "local drift -> reject before false decomposition"),
    ]
