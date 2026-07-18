"""SECOND CONTINUOUS SUBSTRATE -- an excitable FitzHugh-Nagumo network. Genuinely different dynamics from ctrans
(nonlinear, excitable, hidden recovery variable), used to test whether the CRD-03 METHOD transfers or is
ctrans-specific. No ctrans code, no historical instrument code.

Node dynamics (Euler):
    dv = v - v^3/3 - w + I(t) + coupling ;   dw = eps*(v + a - b*w)
v = fast (observed via a readout), w = HIDDEN recovery variable. A probe injects current I; the RESPONSE is the
excitable deflection. Environmental DRIFT modulates the shared input baseline. References read linear mixtures of
the shared drift plus (contamination) a fraction of the response.
"""
from __future__ import annotations
import numpy as np

def _step(v,w,I,eps=0.08,a=0.7,b=0.8,K=0.0,dt=0.4):
    vn=v+dt*(v-v**3/3.0-w+I)
    wn=w+dt*(eps*(v+a-b*w))
    return vn,wn

def run(T, I_base, drift, probe, seed, persist=False, hidden_gain=0.0):
    """Returns the observed readout y(t)=v (fast var). probe: additive current pulse (the intervention)."""
    rng=np.random.default_rng(seed)
    v=-1.2+0.01*rng.standard_normal(); w=-0.6+0.01*rng.standard_normal()
    y=np.zeros(T); wtrace=np.zeros(T)
    for t in range(T):
        I = I_base + drift[t] + probe[t]
        v,w=_step(v,w,I)
        if persist and probe[t]!=0: w += hidden_gain*0.0   # (persistence handled by probe shape)
        y[t]=v; wtrace[t]=w
    return y, wtrace

def acquire(T, tp, seed, couplings, kappa, drift_sigma=0.05, drift_tau=60.,
            eps_noise=0.01, R=24, amp=0.35, persist=False):
    """Signed paired episodes with M references. Returns m_plus,m_minus,h_plus,h_minus,q_true (odd response)."""
    def ou(n,sig,tau,rg):
        phi=np.exp(-1/tau);e=rg.normal(0,sig,n);e[0]=0;x=np.zeros(n)
        for t in range(1,n):x[t]=phi*x[t-1]+e[t]
        return x
    M=len(couplings)
    mp=[];mm=[];hp=[];hm=[]; qs=[]
    base=np.full(T,0.0)
    for r in range(R):
        for sign,ML,HL in ((+1,mp,hp),(-1,mm,hm)):
            rg=np.random.default_rng(seed*7919+r*4+(sign>0))
            d=ou(T,drift_sigma,drift_tau,rg)
            probe=np.zeros(T); probe[tp:tp+40]=sign*amp     # signed current pulse
            y,_=run(T,0.0,d,probe,seed*13+r, persist=persist)
            y0,_=run(T,0.0,d,np.zeros(T),seed*13+r)         # baseline (unprobed) for response extraction
            q=y-y0                                          # causal response for this sign
            ML.append(y)
            HL.append(np.stack([couplings[i]*d + kappa[i]*q + rg.normal(0,eps_noise,T) for i in range(M)]))
            if sign>0: qs.append(q)
    return np.array(mp),np.array(mm),np.array(hp),np.array(hm),np.mean(qs,axis=0)
