"""Fresh sign-safe benchmark. Self-contained synthetic acquisition (no ctrans, no historical instrument).
Each case declares: reference couplings a_i, contamination kappa_i, whether a clean anchor exists, and the
independently-known sign contract. The instrument is given ONLY (v_i, lam_i, declared contract) -- never the truth.
"""
from __future__ import annotations
import numpy as np, hashlib

DEV_SEED, PRO_SEED = 5_100_000, 5_200_000

def _ou(T,sig,tau,rng):
    phi=np.exp(-1/tau);e=rng.normal(0,sig,T);e[0]=0;x=np.zeros(T)
    for t in range(1,T):x[t]=phi*x[t-1]+e[t]
    return x

def acquire(couplings, kappa, seed, T=960, tp=480, R=24, qamp=4e-4, gy=1.0, noise=1e-5, drift=2e-5):
    """Signed paired episodes. Returns drift-free channels v_i (m,T), lam_i, and PRIVILEGED q_true, plus meta."""
    rng=np.random.default_rng(seed)
    q0=np.zeros(T); q0[tp:]=qamp*np.exp(-np.arange(T-tp)/60.)
    m=len(couplings)
    mp=[];mm=[];hp=[];hm=[]
    for r in range(R):
        for sign,ML,HL in ((+1,mp,hp),(-1,mm,hm)):
            d=_ou(T,drift,500.,np.random.default_rng(seed*1000+r*2+(sign>0)))
            q=sign*q0
            ML.append(q+gy*d+rng.normal(0,noise,T))
            HL.append(np.stack([couplings[i]*d+kappa[i]*q+rng.normal(0,noise,T) for i in range(m)]))
    mp,mm,hp,hm=map(np.array,(mp,mm,hp,hm))
    # pre-window calibration lam_i = gy/a_i, and drift-free odd channels v_i
    def preslope():
        mv=np.concatenate([mp[:,:tp].ravel(),mm[:,:tp].ravel()]); mv=mv-mv.mean()
        out=[]
        for i in range(m):
            hv=np.concatenate([hp[:,i,:tp].ravel(),hm[:,i,:tp].ravel()]); hv=hv-hv.mean()
            out.append(float(mv@hv/(hv@hv)) if hv@hv>0 else 0.0)
        return np.array(out)
    lam=preslope()
    mo=(mp-mm)/2.; ho=(hp-hm)/2.
    v=np.stack([(mo-lam[i]*ho[:,i,:]).mean(0) for i in range(m)])
    return v, lam, q0, {"m":m,"tp":tp}

def case_hash(cp,kap,anchor,sign):
    return hashlib.sha256(repr((tuple(cp),tuple(kap),anchor,sign)).encode()).hexdigest()[:12]

# ---- DECLARED SPLIT (committed before fitting). anchor/sign are INDEPENDENTLY KNOWN inputs to the instrument. ----
CP3=(0.8,1.5,1.15)
def dev_cases():
    return [
      ("D_clean",      CP3,(0.,0.,0.),          True, None,         "clean, anchor known"),
      ("D_atten_diff", CP3,(0.12,0.,0.),         True, "attenuate",  "single attenuating, anchor known"),
      ("D_amp_diff",   CP3,(-0.12,0.,0.),        True, "amplify",    "single AMPLIFYING, anchor+sign known -> point=min"),
      ("D_mixed_anchor",CP3,(0.12,-0.10,0.),     True, None,         "mixed sign, anchor, NO sign -> interval"),
      ("D_atten_noanch",CP3,(0.10,0.10,0.10),    False,"attenuate",  "all attenuating, no anchor -> lower bound"),
      ("D_amp_noanch", CP3,(-0.10,-0.10,-0.10),  False,"amplify",    "all AMPLIFYING, no anchor -> UPPER bound (not lower!)"),
      ("D_nosign",     CP3,(-0.12,0.,0.),        False,None,         "no anchor, no sign -> NON_IDENTIFIABLE"),
      ("D_commonmode", CP3,(0.1*0.8,0.1*1.5,0.1*1.15),False,None,    "common-mode, no anchor -> NON_IDENTIFIABLE"),
      ("D_negcoupling",(-0.8,1.5,1.15),(0.12,0.,0.),True,"amplify",  "pos kappa but NEG coupling -> amplifies; sign known"),
      ("D_collinear",  (1.0,1.02,1.04),(0.1,0.,0.),True,None,        "near-collinear -> ILL_CONDITIONED"),
    ]
def pro_cases():
    return [
      ("Q_clean",      CP3,(0.,0.,0.),           True, None,        "clean"),
      ("Q_atten",      CP3,(0.15,0.02,0.),        True, "attenuate", "differential attenuating, anchor"),
      ("Q_amp",        CP3,(-0.15,0.,0.),         True, "amplify",   "amplifying, anchor+sign"),
      ("Q_mixed",      CP3,(0.10,-0.14,0.),       True, None,        "mixed, anchor, no sign -> interval"),
      ("Q_amp_noanch", CP3,(-0.12,-0.09,-0.14),   False,"amplify",   "all amplify, no anchor -> UPPER bound"),
      ("Q_atten_noanch",CP3,(0.09,0.13,0.11),     False,"attenuate", "all attenuate, no anchor -> lower bound"),
      ("Q_nosign",     CP3,(-0.13,0.,0.),         False,None,        "no anchor/sign -> NON_IDENTIFIABLE"),
      ("Q_commonmode", CP3,(-0.08*0.8,-0.08*1.5,-0.08*1.15),False,None,"common-mode amplify, no anchor -> NON_IDENT"),
      ("Q_negcoup",    (0.8,-1.5,1.15),(0.,0.12,0.),True,"amplify",  "neg coupling on ref1, sign known"),
      ("Q_sparse4clean",(0.8,1.5,1.15,0.6),(0.,0.,0.18,0.),True,None,"4 refs, 1 contaminated, anchor -> interval/point"),
    ]
