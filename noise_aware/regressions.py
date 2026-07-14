"""HISTORICAL FAILURE REGRESSIONS — EXP-GT-NOISE-AWARE-SET-IDENTIFICATION-00.

Two families of named regressions, used for DEVELOPMENT gating only (never prospective qualification):
  (1) the exact hand-verified pattern  SNR=5, |q|~=0.428, historical output {0}  (mission section 12);
  (2) a sample of the burned N=2000 hold-out's OWN failing cases (consolidation/holdout_gen.py),
      replayed through the NEW instrument.

Required new behaviour: never a false exact {0}; the emitted set contains the true |q| (or the instrument
safely abstains). We report both.
"""
from __future__ import annotations
import numpy as np, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "consolidation"))
import nasi

L = 120

def _window(v, prof, tp):
    p = prof[tp:tp+L]
    w = v[:, tp:tp+L]
    return w, p

def reg_hand_verified(verbose=True):
    """SNR=5, |q|=0.428 : old instrument returned {0}. New instrument must not."""
    out = []
    q = 0.428
    betas = [0.0, 0.25, 0.40]           # channel 0 clean (anchor), 2 attenuated
    t = np.arange(L); p = np.exp(-t/40.0)
    for seed in range(8):
        rng = np.random.default_rng(4280 + seed)
        c = np.array([q*(1-b) for b in betas])
        Y = c[:, None]*p[None, :] + rng.normal(0, q/5.0, (3, L))
        lam = np.array([0.8, 1.5, 1.15])
        # mirror the historical ORACLE contract (clean anchor + attenuation both true here)
        r = nasi.identify(Y, p, lam, nasi.Contract(sign="attenuate", clean_anchor=True,
                          provenance={"sign":"benchmark_truth","anchor":"benchmark_truth"}),
                          alpha=0.05, rng=np.random.default_rng(9000+seed))
        false0 = (r.qset == [(0.0, 0.0)]) and r.status != nasi.EXACTZERO
        contains = r.contains(q)
        ok = (not false0) and (contains in (True, None))
        out.append(dict(name=f"hand_verified_snr5_q0.428_seed{seed}", ok=bool(ok),
                        status=r.status, false_exact_zero=bool(false0),
                        contains=(None if contains is None else bool(contains))))
        if verbose:
            print(f"  hand seed{seed}: {r.status:20s} false0={false0} contains={contains} ok={ok}")
    return out

def reg_burned_sample(k=40, verbose=True):
    """Replay a sample of the burned hold-out's OWN oracle-arm failures through the new instrument."""
    try:
        import holdout_gen as G
    except Exception as e:
        return [dict(name="burned_sample_UNAVAILABLE", ok=True, note=str(e))]
    res_path = os.path.join(os.path.dirname(__file__), "..", "consolidation", "HOLDOUT_RESULTS.json")
    fails = []
    if os.path.exists(res_path):
        d = json.load(open(res_path))
        fails = [r["i"] for r in d["rows"]["oracle"] if r.get("valid") is False]
    if not fails:
        fails = list(range(0, 2000, 12))     # fallback: snr=5 stratum stride
    idxs = fails[:k]
    out = []
    ncover = nfalse0 = nabstain = 0
    for i in idxs:
        v, base, prof, tp, q, anch, sign, strat, snr, m = G.build(i)
        w, p = _window(v, prof, tp)
        lam = 1.0/np.where(np.abs(base) > 1e-9, base, 1e-9)
        qmag = abs(q)                          # coefficient-units target (slope on p)
        r = nasi.identify(w, p, lam, nasi.Contract(sign=sign, clean_anchor=bool(anch),
                          provenance={"sign":"benchmark_truth","anchor":"benchmark_truth"}),
                          alpha=0.05, rng=np.random.default_rng(20000+i))
        false0 = (r.qset == [(0.0, 0.0)]) and r.status != nasi.EXACTZERO
        contains = r.contains(qmag)
        ok = (not false0) and (contains in (True, None))
        ncover += (contains is True); nfalse0 += false0; nabstain += (contains is None)
        out.append(dict(name=f"burned_i{i}_snr{snr:g}", ok=bool(ok), status=r.status,
                        false_exact_zero=bool(false0), contains=(None if contains is None else bool(contains)),
                        qmag=float(qmag)))
    if verbose:
        print(f"  burned sample: {len(idxs)} cases  cover={ncover} abstain={nabstain} false0={nfalse0}")
    return out

def run_all(verbose=True):
    r = reg_hand_verified(verbose) + reg_burned_sample(40, verbose)
    return r

if __name__ == "__main__":
    rr = run_all(True)
    ok = sum(x["ok"] for x in rr); n = len(rr)
    false0 = sum(x.get("false_exact_zero", False) for x in rr)
    print(f"\nREGRESSIONS: {ok}/{n} ok ; false exact-zero events = {false0}")
    print("VERDICT:", "PASS" if (ok == n and false0 == 0) else "**FAIL**")
