"""CRD-01 ACQUISITION-CONTRACT MANIFEST. Committed BEFORE any fitting, any frontier, any prospective system.

The dev/prospective split is NEW. It has to be: CRD-01 changes WHAT IS ACQUIRED, so a split earned under CRD-00's
acquisition would be a split earned under a different instrument.
"""

from __future__ import annotations

from dataclasses import dataclass

from .cmacq import CMContract
from .manifests_crd import dev_systems, pro_systems

DEV_SEED, PRO_SEED = 800_000, 900_000
R_REPEATS = 16


# ---- THE THREE CANDIDATE ACQUISITION CONTRACTS, declared before selection. --------------------------------
CONTRACTS = {
    # A -- SIMULTANEOUS. Active and control(s) recorded at the same time, so they see ONE drift realization.
    #      Cost: needs simultaneous channels. Assumption: the channels couple to the drift with similar gain/lag.
    "A": dict(name="A_simultaneous", note="active + 2 controls + sham, recorded together, one shared d"),
    # B -- ABBA INTERLEAVED. One channel, episodes alternated A-B-B-A so the drift's LINEAR component cancels.
    #      Cost: none (single channel). Assumption: drift is locally linear over the block -- FALSE for fast drift.
    "B": dict(name="B_abba", note="single channel, ABBA order, cancels drift's linear trend only"),
    # C -- INTERVENTION REVERSAL. Record +u and -u sharing one drift. causal = (y+ - y-)/2 cancels d EXACTLY,
    #      with NO control channel at all.  Assumption: THE RESPONSE IS ODD IN u. False under saturation.
    "C": dict(name="C_reversal", note="+u and -u share d; causal is the odd part, drift the even part"),
}
CONTRACT_SELECTION_RULE = (
    "Select the contract that PASSES ITS OWN ADMISSION TEST on development data, on the case that killed CRD-00 "
    "(Z-17 = K_base vs K_slow_drift). If more than one passes, prefer the one whose stated assumption is weakest. "
    "If NONE passes, return SCOPE FAILURE. The rule is fixed here, before any contract has been run on a case."
)

# ---- THE PARTIAL COMMON-MODE FRONTIER. The axes are declared here; the numbers are measured later. ---------
FRONTIER = {
    "independent_residual_drift": [0.0, 0.1, 0.25, 0.5, 0.75, 1.0, 1.5],   # b_A: the part of the drift NOT shared
    "gain_mismatch": [1.0, 1.05, 1.1, 1.2, 1.4, 1.8],                      # a_C / a_A
    "lag_mismatch": [0, 1, 2, 4, 8, 16, 32],                               # delta_C - delta_A  (LAG_MAX = 12)
    "control_contamination": [0.0, 0.02, 0.05, 0.1, 0.2, 0.4],             # kappa_C: control leaks the response
    "drift_amplitude": [0.0, 5e-6, 2e-5, 8e-5],                            # drift_sigma
}


@dataclass(frozen=True)
class CMCase:
    cid: str
    sysA: str
    sysB: str
    contract: CMContract
    truth: dict          # DECLARED at construction. Cross-checked against the privileged evaluator, never fitted.
    note: str


def _C(**kw):
    return CMContract(**kw)


def dev_cases():
    """DEVELOPMENT cases. Every one of them exists to be able to FAIL."""
    return [
        CMCase("CM-01", "K_base", "K_base", _C(),
               {"E": "zero", "P": "zero", "A": "zero", "adm": "ADMISSIBLE"},
               "shared drift, NO response: the instrument must not manufacture one out of the drift"),
        CMCase("CM-02", "K_base", "K_slow_drift", _C(),
               {"E": "nonzero", "P": "zero", "A": "nonzero", "adm": "ADMISSIBLE"},
               "*** Z-17 REGRESSION *** the exact pair CRD-00 got wrong (E overstated 7.1x, A 422.7 vs ~97)"),
        CMCase("CM-03", "K_base", "K_slow_drift", _C(a_C=0.0, b_C=1.0),
               {"adm": "NOT_ESTABLISHED"},
               "INDEPENDENT drift masquerading as a control -- CRD-00's sham. Must be REFUSED, not corrected."),
        CMCase("CM-04", "K_base", "K_slow_drift", _C(b_A=0.25),
               {"adm": "PARTIAL_OR_ADMISSIBLE"}, "partial common mode: 25% of the drift is not shared"),
        CMCase("CM-05", "K_base", "K_slow_drift", _C(b_A=1.0),
               {"adm": "NOT_ESTABLISHED"}, "partial common mode: the shared part no longer dominates"),
        CMCase("CM-06", "K_base", "K_slow_drift", _C(kappa_C=0.30),
               {"adm": "CONTAMINATED"}, "CONTROL CONTAMINATION: the control leaks 30% of the response"),
        CMCase("CM-07", "K_base", "K_persist", _C(),
               {"E": "nonzero", "P": "nonzero", "A": "nonzero", "adm": "ADMISSIBLE"},
               "PERSISTENT causal offset under shared drift -- must NOT be confused with a drift offset"),
        CMCase("CM-08", "K_base", "K_base", _C(drift_sigma=8e-5),
               {"E": "zero", "P": "zero", "A": "zero", "adm": "ADMISSIBLE"},
               "DRIFT-ONLY, heavy: a wandering baseline is not a persistent causal response"),
        CMCase("CM-09", "K_base", "K_spike", _C(),
               {"E": "nonzero", "P": "zero", "A": "nonzero", "adm": "ADMISSIBLE"},
               "pure TRANSIENT under shared drift"),
        CMCase("CM-10", "K_base", "K_slow_drift", _C(a_C=1.20, delta_C=8),
               {"E": "nonzero", "P": "zero", "A": "nonzero", "adm": "ADMISSIBLE"},
               "gain AND lag mismatch, both inside the declared model -- correction must still close"),
        CMCase("CM-11", "K_base", "K_base", _C(drift_sigma=0.0),
               {"E": "zero", "P": "zero", "A": "zero", "adm": "DRIFT_ABSENT"},
               "no drift: the correction must switch ITSELF OFF, not inject proxy noise"),
        CMCase("CM-12", "K_silent", "K_base", _C(),
               {"adm": "ADMISSIBLE"}, "a SILENT system is not a drift artefact and must not score responses"),
    ]


def pro_cases():
    """PROSPECTIVE. Seeds 9xx. Touched EXACTLY ONCE, after the freeze."""
    return [
        CMCase("P-01", "Q_base", "Q_base", _C(), {"E": "zero", "P": "zero", "A": "zero"}, "null under shared drift"),
        CMCase("P-02", "Q_base", "Q_slow_drift", _C(), {"E": "nonzero", "P": "zero", "A": "nonzero"}, "slow + drift"),
        CMCase("P-03", "Q_base", "Q_persist", _C(), {"E": "nonzero", "P": "nonzero", "A": "nonzero"}, "persistent"),
        CMCase("P-04", "Q_base", "Q_spike", _C(), {"E": "nonzero", "P": "zero", "A": "nonzero"}, "transient"),
        CMCase("P-05", "Q_base", "Q_slow_drift", _C(a_C=0.0, b_C=1.0), {}, "independent control -> must refuse"),
        CMCase("P-06", "Q_base", "Q_slow_drift", _C(b_A=1.0), {}, "partial -> must refuse"),
        CMCase("P-07", "Q_base", "Q_slow_drift", _C(kappa_C=0.30), {}, "contaminated -> must flag"),
        CMCase("P-08", "Q_base", "Q_base", _C(drift_sigma=8e-5), {"E": "zero", "P": "zero", "A": "zero"}, "heavy drift null"),
    ]
