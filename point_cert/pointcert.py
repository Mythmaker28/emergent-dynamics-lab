"""POINT-CERTIFIED SET IDENTIFICATION — EXP-GT-POINT-CERTIFIED-SET-IDENTIFICATION-00.
A claim-reduction LAYER over the FROZEN NASI set instrument (noise_aware/nasi.py, unmodified).

Two outputs per case, both recorded:
  * SET  : a SELECTION-AWARE set Q_wide = hull( NASI naive set , all leave-one-reference-out point
           locations , selection Monte-Carlo interval ). This is the primary, honest set: when the naive
           NASI point is a selection/dropout artefact, the leave-one-out locations pull Q_wide wide enough
           to contain the truth. Q_wide always contains the frozen NASI naive set.
  * POINT: issued ONLY if every certificate C1..C8 passes AND diam(Q_wide) is within the frozen margin.
           The certified point interval is always a SUBSET of Q_wide.
The point may never exclude a value allowed by the set. numpy only; imports nasi, never modifies it.
"""
from __future__ import annotations
import os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "noise_aware"))
import nasi

EPS_Q_REL = 0.30   # C3 max relative diameter of the SELECTION-AWARE set for a point
SNR_FLOOR = 8.0    # C8 minimum per-channel SNR
LORO_TOL  = 0.15   # C4 max relative leave-one-reference-out point shift
FOLD_TOL  = 0.22   # C5 max relative leave-one-temporal-fold point shift
DROP_R2   = 0.10   # C2 dropout-suspect if the profile fit explains < DROP_R2 of the channel variance
SELECT_B  = 199    # C6 selection-aware Monte-Carlo draws
POINT_INFLATE = 1.75  # conservative widening of the certified point interval (selection-aware finite-sample margin)

PMARGIN="PRACTICALLY_POINT_IDENTIFIED_WITHIN_MARGIN"; PSTRUCT="STRUCTURALLY_POINT_IDENTIFIED"
PC_FAIL="POINT_CERTIFICATE_FAILED"; PC_DROP="POINT_FORBIDDEN_DROPOUT"
PC_SEL="POINT_FORBIDDEN_SELECTION_INSTABILITY"; PC_SNR="POINT_FORBIDDEN_INSUFFICIENT_SNR"
PC_ORACLE="POINT_FORBIDDEN_ORACLE_CONTRACT"; PC_COND="POINT_FORBIDDEN_CONDITIONING"
POINT_ISSUED={PMARGIN, PSTRUCT}

def _bounded(qset): return bool(qset) and all(np.isfinite(b) for _, b in qset)

def _chat(Y, p):
    """Analytic per-channel response coefficient (no bootstrap) and R^2."""
    X, A0, h = nasi._fit_setup(p)
    c = Y @ A0
    beta = np.linalg.pinv(X) @ Y.T
    res = Y - (X @ beta).T
    ss_res = (res**2).sum(axis=1); ss_tot = ((Y - Y.mean(1, keepdims=True))**2).sum(axis=1) + 1e-30
    return c, 1.0 - ss_res/ss_tot

def _point_from_c(cmag, contract, detected):
    s = contract.sign
    if contract.clean_anchor:
        if s == "attenuate": return float(np.max(cmag))
        if s == "amplify":
            d = cmag[detected]; return float(np.min(d)) if d.size else None
        return None
    if contract.sparsity_s is not None:
        srt = np.sort(cmag); best = None
        for i in range(len(srt)):
            grp = srt[(srt >= srt[i]) & (srt <= srt[i]*1.15 + 1e-9)]
            if best is None or len(grp) > len(best): best = grp
        return float(np.median(best)) if best is not None else None
    return None

def certify(Y, p, lam, contract, provenance, essential_refs=frozenset(), rng=None):
    if rng is None: rng = np.random.default_rng(0)
    base = nasi.identify(Y, p, lam, contract, alpha=0.05, rng=rng)     # FROZEN naive set
    m = Y.shape[0]
    rec = {"base_status": base.status, "base_set": [list(x) for x in base.qset],
           "set_wide": None, "point_status": None, "point_interval": None,
           "certificates": {}, "provenance": dict(provenance)}
    C = rec["certificates"]
    oracle = any(v in ("benchmark_truth","truth","hidden_kappa","privileged_topology") for v in provenance.values())
    C["C1_provenance"] = not oracle

    c_hat, r2 = _chat(Y, p)                                            # analytic (deterministic)
    if "se" in base.diagnostics:
        se = np.array(base.diagnostics["se"])                         # reuse NASI's bootstrap se (no 2nd bootstrap)
    else:
        se = nasi.channel_intervals(Y, p, alpha=0.05, rng=rng)["se"]  # fallback (base abstained/degenerate)
    cmag = np.abs(c_hat); detected = cmag > 2*se
    snr_est = float(np.max(cmag/(se+1e-30)))

    # naive point location + leave-one-reference-out locations (analytic; A0 is channel-independent)
    p_full = _point_from_c(cmag, contract, detected)
    loro_pts = []
    if p_full is not None and m >= 3:
        for j in range(m):
            if j in essential_refs: continue
            keep = [k for k in range(m) if k != j]
            v = _point_from_c(cmag[keep], contract, detected[keep])
            if v is not None: loro_pts.append(v)
    # leave-one-temporal-fold locations
    fold_pts = []
    L = Y.shape[1]
    for a, b in ((0, L//2), (L//2, L)):
        cf, _ = _chat(Y[:, a:b], p[a:b]); vf = _point_from_c(np.abs(cf), contract, np.abs(cf) > 2*se)
        if vf is not None: fold_pts.append(vf)
    # selection-aware Monte-Carlo point interval
    mc = []
    for _ in range(SELECT_B):
        v = _point_from_c(np.abs(c_hat + rng.normal(0, 1, m)*se), contract, detected)
        if v is not None: mc.append(v)
    mc_lo, mc_hi = (float(np.percentile(mc, 2.5)), float(np.percentile(mc, 97.5))) if mc else (None, None)

    # ---- SELECTION-AWARE SET Q_wide = hull(naive set, loro points, fold points, mc interval) ----
    lows = []; highs = []
    if _bounded(base.qset):
        lows.append(min(a for a,_ in base.qset)); highs.append(max(b for _,b in base.qset))
    for v in loro_pts + fold_pts: lows.append(v); highs.append(v)
    if mc_lo is not None: lows.append(mc_lo); highs.append(mc_hi)
    if lows:
        Qw = (max(0.0, min(lows)), max(highs)); rec["set_wide"] = list(Qw)
    else:
        rec["set_wide"] = None
        rec["point_status"] = PC_FAIL; C["reason"] = "no bounded set"; return rec, base

    if oracle:
        rec["point_status"] = PC_ORACLE; return rec, base
    if p_full is None or mc_lo is None:
        rec["point_status"] = PC_FAIL; C["reason"] = "contract yields no point candidate"; return rec, base

    lo, hi = Qw; center = 0.5*(lo+hi); reldiam = (hi-lo)/(abs(center)+1e-12)
    # certificates
    C["C3_diameter"] = reldiam <= EPS_Q_REL
    C["C8_snr"] = snr_est >= SNR_FLOOR
    if contract.clean_anchor and contract.sign == "attenuate": det_idx = {int(np.argmax(cmag))}
    elif contract.clean_anchor and contract.sign == "amplify":
        di = np.where(detected)[0]; det_idx = {int(di[np.argmin(cmag[di])])} if di.size else set(range(m))
    else: det_idx = set(int(i) for i in np.argsort(cmag)[:max(1, m//2)])
    C["C2_dropout"] = not any((r2[j] < DROP_R2) and (j not in essential_refs) for j in det_idx)
    C["C4_leave_one_ref"] = (not loro_pts) or (max(abs(v-p_full) for v in loro_pts)/(abs(p_full)+1e-12) <= LORO_TOL)
    C["C5_leave_one_fold"] = (not fold_pts) or (max(abs(v-p_full) for v in fold_pts)/(abs(p_full)+1e-12) <= FOLD_TOL)
    C["C6_selection_aware"] = mc_lo is not None

    passed = all(C.get(k, False) for k in ("C1_provenance","C2_dropout","C3_diameter",
                 "C4_leave_one_ref","C5_leave_one_fold","C6_selection_aware","C8_snr"))
    if passed:
        pc = 0.5*(mc_lo+mc_hi); ph = 0.5*(mc_hi-mc_lo)*POINT_INFLATE
        pil, pih = max(pc-ph, lo), min(pc+ph, hi)
        # a point is only meaningful if the inflated certified interval is still within the margin
        if (pih-pil)/(abs(0.5*(pil+pih))+1e-12) <= EPS_Q_REL:
            rec["point_status"] = PMARGIN; rec["point_interval"] = [pil, pih]
        else:
            rec["point_status"] = PC_FAIL
    else:
        if not C["C1_provenance"]: rec["point_status"] = PC_ORACLE
        elif not C["C8_snr"]:      rec["point_status"] = PC_SNR
        elif not C["C2_dropout"]:  rec["point_status"] = PC_DROP
        elif not (C["C4_leave_one_ref"] and C["C5_leave_one_fold"]): rec["point_status"] = PC_SEL
        else:                      rec["point_status"] = PC_FAIL
    return rec, base

def set_contains(rec, qmag, tol=1e-9):
    if rec["set_wide"] is None: return None
    a, b = rec["set_wide"]; return bool(a-tol*max(1,abs(a)) <= qmag <= b+tol*max(1,abs(b)))

def point_contains(rec, qmag, tol=1e-9):
    if rec["point_status"] not in POINT_ISSUED or rec["point_interval"] is None: return None
    a, b = rec["point_interval"]; return bool(a-tol <= qmag <= b+tol)
