"""CRD-03 SPLIT + CASE MANIFEST. Committed BEFORE any fitting.

New split (dev 13xx / prospective 14xx). CRD-03 changes the acquisition again (redundant references + signed
interventions), so a split earned under CRD-02 was earned under a different instrument. Dev systems reuse CRD-02
topologies ONLY as historical regressions; the decisive prospective systems reserve unseen combinations.
"""
from __future__ import annotations
from dataclasses import dataclass

from . import decomp as D, decomp2 as D2
from .racq import RContract
from .systems import silent_dead

DEV_SEED, PRO_SEED = 1_300_000, 1_400_000
R_REPEATS = 24
COUP = (0.8, 1.5, 1.15)          # the THREE declared reference drift couplings (distinct -> identifiable)


def dev_systems():
    b = D.base("R_base")
    return {
        "R_base": b,
        "R_slow": D.plus_path("R_slow", b, w=0.5, Tx=35.0),          # Z-17 response
        "R_persist": D.plus_path("R_persist", b, w=1.0, Tx=60.0, persistent=True),
        "R_spike": D.plus_spike("R_spike", b, w=1.0, Tf=1.0, Ts=3.0),
        "R_broadE": D.plus_broad("R_broadE", b, w=0.464, T1=30.0, T2=30.0),
        "R_broadA": D.plus_broad("R_broadA", b, w=1.319, T1=30.0, T2=30.0),
        "R_hidden": D2.plus_hidden("R_hidden", b, w=0.6),
        "R_transient": D.plus_path("R_transient", b, w=0.8, Tx=8.0),
        "R_silent": silent_dead("R_silent"),
    }


def pro_systems():
    b = D.base("S_base")
    return {
        "S_base": b,
        "S_cascade3": D2.plus_cascade3("S_cascade3", b, w=1.0),      # unseen
        "S_underdamped": D2.plus_underdamped("S_underdamped", b, w=1.0),
        "S_multiscale": D2.plus_multiscale("S_multiscale", b, w=1.0),
        "S_feedback": D2.plus_feedback("S_feedback", b, w=1.0),
        "S_persist": D.plus_path("S_persist", b, w=1.0, Tx=60.0, persistent=True),
        "S_slow": D.plus_path("S_slow", b, w=0.5, Tx=35.0),
        "S_spike": D.plus_spike("S_spike", b, w=1.0, Tf=1.0, Ts=3.0),
        "S_silent": silent_dead("S_silent"),
    }


HEAVY = dict(drift_sigma=2.0e-5, f_fast=0.35)


@dataclass
class RCase:
    cid: str
    sys: str
    contract: RContract
    truth: dict
    note: str


def _C(kappa=(0., 0., 0.), couplings=COUP, **kw):
    p = dict(HEAVY); p.update(kw)
    return RContract(couplings=couplings, kappa=kappa, **p)


def dev_cases():
    return [
        RCase("D1", "R_slow", _C(), {"E": "nz", "A": "nz", "P": "z", "adm": "IDENT"},
              "*** historical Z-17 *** slow response under heavy drift, clean references"),
        RCase("D2", "R_slow", _C(kappa=(0.12, 0.0, 0.0)), {"adm": "CORR", "exact": True},
              "*** CRD-02 REGRESSION *** kappa=0.12 on ONE reference -- must detect+correct, not attenuate 21%"),
        RCase("D3a", "R_slow", _C(kappa=(0.02, 0.0, 0.0)), {"adm": "CORR_OR_IDENT"}, "kappa=0.02 below CRD-02 floor"),
        RCase("D3b", "R_slow", _C(kappa=(0.05, 0.0, 0.0)), {"adm": "CORR"}, "kappa=0.05"),
        RCase("D3c", "R_slow", _C(kappa=(0.08, 0.0, 0.0)), {"adm": "CORR"}, "kappa=0.08"),
        RCase("D3d", "R_slow", _C(kappa=(0.10, 0.0, 0.0)), {"adm": "CORR"}, "kappa=0.10"),
        RCase("D4", "R_slow", _C(kappa=(0.12, 0.12 * 1.5 / 0.8, 0.12 * 1.15 / 0.8)),
              {"adm": "IDENT", "lower_bound": True},
              "COMMON-MODE: kappa_i proportional to a_i -> undetectable -> lower bound, not confident attenuation"),
        RCase("D5", "R_slow", _C(kappa=(0.12, 0.03, 0.0)), {"adm": "CORR_OR_IND"}, "different kappa on two references"),
        RCase("D6", "R_slow", _C(couplings=(1.00, 1.02, 1.05), kappa=(0.10, 0.0, 0.0)),
              {"adm": "ILL"}, "nearly collinear references -> ill-conditioned -> abstain"),
        RCase("D7", "R_slow", _C(), {"odd": True, "adm": "IDENT"}, "signed LINEAR response -> odd recovered, drift rejected"),
        RCase("D8", "R_slow", _C(even_frac=0.5), {"even": True, "adm": "IDENT"}, "signed NONLINEAR: odd + even parts"),
        RCase("D9", "R_slow", _C(hysteresis=0.4), {"adm": "SIGNV_OR_IDENT"}, "hysteretic: order of +u/-u matters"),
        RCase("D10", "R_slow", _C(comp_kappa=0.0), {"comp_null": True}, "complementary probe truly null"),
        RCase("D11", "R_slow", _C(comp_kappa=0.15), {"comp_non_null": True}, "complementary region responds -> non-null"),
        RCase("D12", "R_slow", _C(loc=1.5), {"adm": "any"}, "local unshared drift: diversity must not manufacture correction"),
        RCase("D13", "R_persist", _C(), {"E": "nz", "A": "nz", "P": "nz", "adm": "IDENT"}, "persistent response preserved"),
        RCase("D14", "R_transient", _C(), {"E": "nz", "A": "nz", "P": "z", "adm": "IDENT"}, "pure transient + recovery"),
        RCase("D15", "R_hidden", _C(), {"E": "nz", "P": "nz", "adm": "IDENT"}, "hidden state persistence"),
        RCase("D16a", "R_spike", _C(), {"adm": "IDENT"}, "peak/energy factorization: spike"),
        RCase("D16b", "R_broadE", _C(), {"adm": "IDENT"}, "peak/energy factorization: equal-energy broad"),
        RCase("D17", "R_silent", _C(), {"adm": "IDENT", "collision": True}, "limited-access collision -> equivalence class only"),
    ]


def pro_cases():
    return [
        RCase("Q1", "S_slow", _C(), {"E": "nz", "A": "nz", "P": "z"}, "slow + drift, clean"),
        RCase("Q2", "S_slow", _C(kappa=(0.12, 0.0, 0.0)), {"adm": "CORR"}, "kappa=0.12 single ref -> correct"),
        RCase("Q3", "S_cascade3", _C(kappa=(0.08, 0.0, 0.0)), {"adm": "CORR"}, "third-order + contamination"),
        RCase("Q4", "S_underdamped", _C(), {"E": "nz", "A": "nz"}, "ringing, clean"),
        RCase("Q5", "S_slow", _C(kappa=(0.10 * 0.8, 0.10 * 1.5, 0.10 * 1.15)), {"adm": "IDENT", "lower_bound": True}, "common-mode -> lower bound"),
        RCase("Q6", "S_multiscale", _C(kappa=(0.10, 0.02, 0.0)), {"adm": "CORR_OR_IND"}, "multiscale + differential contamination"),
        RCase("Q7", "S_feedback", _C(even_frac=0.4), {"even": True}, "feedback + nonlinear signed"),
        RCase("Q8", "S_persist", _C(), {"E": "nz", "P": "nz"}, "persistent, clean"),
        RCase("Q9", "S_slow", _C(couplings=(1.0, 1.03, 1.06), kappa=(0.1, 0., 0.)), {"adm": "ILL"}, "collinear refs -> abstain"),
        RCase("Q10", "S_spike", _C(), {"E": "nz", "A": "nz", "P": "z"}, "transient, clean"),
        RCase("Q11", "S_slow", _C(hysteresis=0.4), {"adm": "SIGNV_OR_IDENT"}, "hysteresis"),
        RCase("Q12", "S_silent", _C(), {"collision": True}, "silent -> equivalence class"),
    ]
