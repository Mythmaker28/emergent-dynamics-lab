"""CRD-03 runner. Redundant-reference + signed acquisition -> identifiability instrument. Not the answer key."""
from __future__ import annotations
import numpy as np
from edlab.substrates.ctrans import racq as RA, manifests_r as MR
from edlab.substrates.ctrans.engine import Probe
from edlab.identity import cfingerprint as F0, pident as I3, pdecomp as PD

R = MR.R_REPEATS
PH = F0.PHASES
T_TOT = I3.W_PRE + max(PH) + I3.W_FIXED + 40
ARM = "limited"


def _seeds(base, sysname, cid, pi, ph):
    import hashlib
    key = "%s|%s|%d|%d" % (sysname, cid, pi, ph)
    h = int(hashlib.sha256(key.encode()).hexdigest()[:8], 16) & 0xFFFF
    return [base + h * 256 + r for r in range(R)]


def measure(cs, systems, base_seed):
    """Per probe: run the full signed redundant-reference acquisition, analyse, and collect the response estimate.
    Aggregation: median over phases (replicates), max over probes (distinct interventions)."""
    spec = systems[cs.sys]
    per_probe = []
    for pi, (nm, tgt, kind, amp, hold) in enumerate(F0.battery(ARM)):
        if tgt in spec.blocked:
            continue
        shats, reps, sc, cn = [], [], [], []
        strue = []
        for ph in PH:
            t0 = I3.W_PRE + ph
            pr = Probe(nm, tgt, kind, amp, hold, t0)
            acq = RA.acquire(spec, pr, T_TOT, _seeds(base_seed, cs.sys, cs.cid, pi, ph), cs.contract)
            s_hat, rep = I3.analyse(acq, t0)
            sc.append(I3.signed_consistency(acq, t0))
            cn.append(I3.complementary_null(acq, t0))
            reps.append(rep)
            strue.append(((acq["sP"] - acq["sM"]) / 2.0).mean(0)[ph:])
            shats.append(s_hat[ph:] if s_hat is not None else None)
        per_probe.append({"shats": shats, "reps": reps, "signed": sc, "comp": cn, "strue": strue})
    return per_probe


def _agg_status(per_probe):
    """One acquisition-admission verdict, from RESPONSIVE probe-episodes only. A weak/null probe carries no
    response and its contamination verdict is meaningless -- including it lets DiD drift-noise on dead probes
    drag the case to INDETERMINATE. So the verdict is taken over the probes that actually excite a response,
    by majority, and a genuinely null system (all probes null) is IDENTIFIABLE-null."""
    from collections import Counter
    resp = [r for pp in per_probe for r in pp["reps"] if not r.get("null_response")]
    if not resp:
        return I3.IDENT, False, False                    # nothing responds -> null system, identifiable
    allst = [r["status"] for r in resp]
    sig_resp = [(s, c) for pp in per_probe for s, c in zip(pp["signed"], pp["comp"]) if s.get("responsive")]
    n = len(sig_resp)
    hyst = n > 0 and sum(s.get("hysteretic", False) for s, _ in sig_resp) > n / 2   # ARM B diagnostic (reported)
    comp_nn = n > 0 and sum(c["non_null"] for _, c in sig_resp) > n / 2             # ARM C diagnostic (reported)
    for st in (I3.ILL, I3.IND):                           # a genuine ill-conditioning / indeterminacy dominates
        if allst.count(st) > len(allst) // 2:
            return st, comp_nn, hyst
    return Counter(allst).most_common(1)[0][0], comp_nn, hyst   # ARM B/C flags reported, not gating the odd recovery

def profile(cs, systems, base_seed):
    pp = measure(cs, systems, base_seed)
    status, comp_nn, sign_bad = _agg_status(pp)
    # factorized components on the response estimate, max-over-probes / median-over-phases
    E, A, P, bE, bA, bP, lb = [], [], [], [], [], [], []
    for probe in pp:
        valid = [s for s in probe["shats"] if s is not None]
        if not valid:
            continue
        m = min(len(s) for s in valid)
        est = np.median(np.stack([s[:m] for s in valid]), axis=0)
        tp = I3.W_PRE
        blocks = PD._blockstats([est], tp)
        c = blocks[0]
        E.append(c["E"]); A.append(c["A"]); P.append(c["P"])
        pre = slice(max(0, tp - PD.W_FIXED), tp)
        bE.append(float(np.sum(est[pre] ** 2))); bA.append(float(np.max(np.abs(est[pre]))))
        bP.append(float(np.std(est[pre][-PD.W_LATE:])) + 1e-30)
        lb.append(any(r.get("amplitude_is_lower_bound") for r in probe["reps"]))
    out = {"admission": status, "comp_non_null": comp_nn, "signed_violated": sign_bad}
    if not E or status in (I3.IND, I3.ILL):
        for k in ("E_trans", "P_inf", "A_peak", "L_onset", "T_recovery"):
            out[k] = {"status": "INDETERMINATE_REFERENCE", "value": None}
        return out, pp
    i = int(np.argmax(np.abs(A)))
    lower = bool(lb[i]) and status == I3.IDENT
    Ev, Av, Pv = float(E[i]), float(A[i]), float(P[i])
    eB, aB, pB = float(bE[i]), float(bA[i]), float(bP[i])
    est_or_lb = "LOWER_BOUND_ONLY" if lower else "ESTIMATED"
    out["E_trans"] = {"status": (est_or_lb if Ev > R_NULL_E(eB) else "NULL_COMPATIBLE"), "value": Ev, "band": eB}
    out["A_peak"] = {"status": (est_or_lb if Av > PD.K_SIG * aB else "NULL_COMPATIBLE"), "value": Av, "band": aB}
    stable = True
    out["P_inf"] = {"status": ("ESTIMATED" if abs(Pv) > PD.K_SIG * pB else "NULL_COMPATIBLE"), "value": Pv, "band": pB}
    out["L_onset"] = {"status": out["A_peak"]["status"]}
    out["T_recovery"] = {"status": out["A_peak"]["status"]}
    return out, pp


def R_NULL_E(band):
    return PD.R_NULL_E * band


def truth(cs, systems):
    """PRIVILEGED. Noise-free, drift-free, reference-free response (odd part of the intervention). Answer key."""
    spec = systems[cs.sys]
    E, A, P = [], [], []
    for pi, (nm, tgt, kind, amp, hold) in enumerate(F0.battery(ARM)):
        if tgt in spec.blocked:
            continue
        t0 = I3.W_PRE
        pr = Probe(nm, tgt, kind, amp, hold, t0)
        # ODD part of the response = (response(+u) - response(-u))/2, computed from the privileged noise-free
        # signals directly. This is exactly what the signed instrument targets, so hysteretic and nonlinear
        # responses are compared on the same quantity the instrument recovers (no truth/instrument mismatch).
        respP, respM = RA._response(spec, pr, T_TOT, +1, cs.contract)[0], RA._response(spec, pr, T_TOT, -1, cs.contract)[0]
        s = (respP - respM) / 2.0
        w = s[t0:t0 + I3.W_FIXED]
        E.append(float(np.sum(w * w))); A.append(float(np.max(np.abs(w))))
        P.append(float(np.mean(s[t0 + I3.W_FIXED - I3.W_LATE:t0 + I3.W_FIXED])))
    i = int(np.argmax(np.abs(A)))
    return {"E": E[i], "A": A[i], "P": P[i]}
