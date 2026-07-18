"""CRD-02 runner. Referenced paired-episode acquisition -> factorized decomposition. Instrument, not answer key."""
from __future__ import annotations
import numpy as np
from edlab.substrates.ctrans import pacq as PA, manifests_p as MP
from edlab.substrates.ctrans.engine import Probe, observe_noise_free
from edlab.identity import cfingerprint as F0, pdecomp as I2

R = MP.R_REPEATS
PH = F0.PHASES
T_TOT = I2.W_PRE + max(PH) + I2.W_FIXED + 40
ARM = "limited"


def _seeds(base, sysA, sysB, pi, ph):
    # DETERMINISTIC across processes. Python's builtin hash() is salted per process (PYTHONHASHSEED), which made
    # the drift realizations -- and therefore the contamination margin and the P_inf status -- vary run to run.
    # A benchmark must be reproducible: use a stable content hash of the identifying tuple.
    import hashlib
    key = "%s|%s|%d|%d" % (sysA, sysB, pi, ph)
    h = int(hashlib.sha256(key.encode()).hexdigest()[:8], 16) & 0xFFFF
    return [base + h * 128 + r for r in range(R)]


def measure(sysA_name, sysB_name, systems, C, base_seed, sign=+1):
    """Active arm carries sysB's response; sham/base arm carries sysA. Both share the paired-episode acquisition.
    Returns s_hat per (probe,phase), per-episode admission reports, reference ensembles for contamination."""
    a, bsys = systems[sysA_name], systems[sysB_name]
    shat, adA, adS, refA, refU, projU = {}, [], [], {}, {}, {}
    for pi, (nm, tgt, kind, amp, hold) in enumerate(F0.battery(ARM)):
        if tgt in a.blocked or tgt in bsys.blocked:
            continue
        shat[pi], refA[pi], refU[pi] = [], [], []
        for ph in PH:
            t0 = I2.W_PRE + ph
            pr = Probe(nm, tgt, kind, amp, hold, t0)
            sd = _seeds(base_seed, sysA_name, sysB_name, pi, ph)
            # FOUR referenced episodes, each SEPARATE in time -> each its own drift realization and reference.
            # DiD: (b_probed - b_unprobed) - (a_probed - a_unprobed). The within-system subtraction removes each
            # system's OWN baseline trajectory (including a non-stationary carrier ramp); the reference removes
            # the environmental drift; the outer difference isolates the added-path response.
            nul = Probe(nm, tgt, "none", 0.0, 0, t0)
            yBp, rBp = PA.acquire_one(bsys, pr,  T_TOT, sd,                     C, "A", sign)
            yBu, rBu = PA.acquire_one(bsys, nul, T_TOT, [s ^ 0x1111 for s in sd], C, "S", sign)
            yAp, rAp = PA.acquire_one(a,    pr,  T_TOT, [s ^ 0x2222 for s in sd], C, "A", sign)
            yAu, rAu = PA.acquire_one(a,    nul, T_TOT, [s ^ 0x3333 for s in sd], C, "S", sign)
            zBp, rp1 = I2.correct_episode(yBp, rBp, t0)
            zBu, rp2 = I2.correct_episode(yBu, rBu, t0)
            zAp, rp3 = I2.correct_episode(yAp, rAp, t0)
            zAu, rp4 = I2.correct_episode(yAu, rAu, t0)
            adA += [rp1["status"], rp3["status"]]       # probed episodes carry the response
            adS += [rp2["status"], rp4["status"]]       # unprobed episodes are the within-system baselines
            if all(z is not None for z in (zBp, zBu, zAp, zAu)):
                did = (zBp - zBu) - (zAp - zAu)
                shat[pi].append(did.mean(axis=0)[ph:])
            refA[pi].append(rBp.mean(axis=0)[ph:])
            refU[pi].append(rBu.mean(axis=0)[ph:])
            if all(z is not None for z in (zBp, zBu, zAp, zAu)):
                sh = ((zBp - zBu) - (zAp - zAu)).mean(axis=0)[ph:]   # ensemble s_hat for this block
                projU.setdefault(pi, []).append(I2.ref_projections(rBp[:, ph:], sh, t0 - ph))
    return shat, adA, adS, refA, refU, projU


def _worst(statuses):
    """Per-episode admission -> ONE verdict. Admission is a property of the CONTRACT; pool by the modal status,
    but any hard-invalid episode dominates (you cannot guess an episode whose reference failed)."""
    from collections import Counter
    hard = {I2.BW, I2.RESID, "NO_REFERENCE", I2.S_INV, I2.A_INV, I2.COV}
    n_hard = sum(s in hard for s in statuses)
    if n_hard > len(statuses) // 2:                 # majority of episodes reference-invalid
        return Counter([s for s in statuses if s in hard]).most_common(1)[0][0]
    return I2.ADM


def truth(sysA_name, sysB_name, systems):
    """PRIVILEGED. Noise-free, drift-free, no reference, no threshold. The answer key."""
    a, bsys = systems[sysA_name], systems[sysB_name]
    E, P, A = [], [], []
    for pi, (nm, tgt, kind, amp, hold) in enumerate(F0.battery(ARM)):
        if tgt in a.blocked or tgt in bsys.blocked:
            continue
        t0 = I2.W_PRE
        pr = Probe(nm, tgt, kind, amp, hold, t0)
        sCa, sAa = PA.signals(a, pr, T_TOT)
        sCb, sAb = PA.signals(bsys, pr, T_TOT)
        d = (sAb - sCb) - (sAa - sCa)          # causal-response difference, exact
        w = d[t0:t0 + I2.W_FIXED]
        E.append(float(np.sum(w * w))); A.append(float(np.max(np.abs(w))))
        P.append(float(np.mean(d[t0 + I2.W_FIXED - I2.W_LATE:t0 + I2.W_FIXED])))
    i = int(np.argmax(np.abs(A)))
    return {"E": E[i], "A": A[i], "P": P[i]}


def run_case(cs, systems, base_seed):
    shat, adA, adS, refA, refU, projU = measure(cs.sysA, cs.sysB, systems, cs.contract, base_seed)
    ct = I2.contamination(projU)
    vA, vS = _worst(adA), _worst(adS)
    prof = I2.profile(shat, vA, vS, ct["contaminated"], I2.W_PRE, suspect=ct.get("suspect", False))
    return prof, truth(cs.sysA, cs.sysB, systems), ct


def shat_estimate(cs, systems, base_seed):
    """The worst-probe s_hat and privileged causal, for quantitative relerr."""
    shat = measure(cs.sysA, cs.sysB, systems, cs.contract, base_seed)[0]
    a, bsys = systems[cs.sysA], systems[cs.sysB]
    best = None
    for pi in shat:
        if not shat[pi]:
            continue
        est = np.median(np.stack(shat[pi]), axis=0)
        A = np.max(np.abs(est[I2.W_PRE:I2.W_PRE + I2.W_FIXED]))
        if best is None or A > best[0]:
            best = (A, est, pi)
    return best
