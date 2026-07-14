"""CRD-01 runner. Common-mode acquisition -> factorized decomposition. Instrument code, NOT the answer key."""
from __future__ import annotations
import numpy as np
from edlab.substrates.ctrans import cmacq as CM, manifests_cm as MM, manifests_crd as MC
from edlab.substrates.ctrans.engine import Probe, DRIVE
from edlab.identity import cfingerprint as F0, crdecomp01 as I1

R = MM.R_REPEATS
PH = F0.PHASES
T_TOT = I1.W_PRE + max(PH) + I1.W_FIXED + 8
ARM = "limited"


def _seeds(base, sysname, pi, ph):
    h = (hash((sysname, pi, ph)) & 0xFFFF)
    return [base + h * 64 + r for r in range(R)]


def measure(spec, sysname, C, base_seed, sign=+1):
    """Returns corrected deviation & sham traces per probe (aligned so index W_PRE is the probe onset),
    the admission verdicts, and the raw control ensembles for the contamination detector."""
    dev, shm, adm, yc = {}, {}, [], []
    for pi, (nm, tgt, kind, amp, hold) in enumerate(F0.battery(ARM)):
        if tgt in spec.blocked:
            continue
        dev[pi], shm[pi] = [], []
        for ph in PH:
            t0 = I1.W_PRE + ph
            pr = Probe(nm, tgt, kind, amp, hold, t0)
            yA, yC, yD, yS, _ = CM.acquire(spec, pr, T_TOT, _seeds(base_seed, sysname, pi, ph), C, sign)
            A, S, rep = I1.correct(yA, yC, yD, yS, t0)
            adm.append(rep)
            dev[pi].append(A.mean(axis=0)[ph:])          # align: index W_PRE == probe onset
            shm[pi].append(S.mean(axis=0)[ph:])
    return dev, shm, adm, I1.contamination(shm, I1.W_PRE)


def truth(a, b, C):
    """PRIVILEGED. Noise-free, drift-free, no sham, no threshold, no estimator. The answer key."""
    E, P, A = [], [], []
    for pi, (nm, tgt, kind, amp, hold) in enumerate(F0.battery(ARM)):
        if tgt in a.blocked or tgt in b.blocked:
            continue
        t0 = I1.W_PRE
        pr = Probe(nm, tgt, kind, amp, hold, t0)
        sAa, sCa = CM.signals(a, pr, T_TOT)
        sAb, sCb = CM.signals(b, pr, T_TOT)
        d = (sAb - sCb) - (sAa - sCa)                     # the causal-response DIFFERENCE. Exact.
        c = I1._components(d, t0)
        E.append(c["E"]); P.append(c["P"]); A.append(c["A"])
    i = int(np.argmax(np.abs(A)))
    return {"E": E[i], "P": P[i], "A": A[i]}


def run_case(cs, systems, base_seed):
    a, b = systems[cs.sysA], systems[cs.sysB]
    dA, sA_, adA, ctA = measure(a, cs.sysA, cs.contract, base_seed)
    dB, sB_, adB, ctB = measure(b, cs.sysB, cs.contract, base_seed + 1)
    contaminated = ctA["contaminated"] or ctB["contaminated"]
    verdict, agg = I1.admit_pooled(adA + adB, contaminated)     # ONE verdict, pooled. Not the worst of 64.
    ks = sorted(set(dA) & set(dB))
    dev = {k: [dB[k][j] - dA[k][j] for j in range(len(PH))] for k in ks}
    shm = {k: [sB_[k][j] - sA_[k][j] for j in range(len(PH))] for k in ks}
    prof = I1.profile(dev, shm, I1.W_PRE, verdict)
    prof["adm_detail"] = agg
    return prof, truth(a, b, cs.contract), {"A": ctA, "B": ctB}
