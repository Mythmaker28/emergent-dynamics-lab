"""Deterministic one-command reproduction of the NASI core claims. Content-addressed seeds -> identical
outputs on every run. Prints a single canonical SHA over all key numbers for determinism checking.
"""
from __future__ import annotations
import numpy as np, hashlib, json, sys
import nasi, devgen, regressions, prospgen

def canon():
    out={}
    # 1) frozen constants
    out["constants"]=[nasi.DIVERSITY_FLOOR,nasi.POINT_HALFWIDTH,nasi.BOOT_B,nasi.BLOCK_FRAC,nasi.DRIFT_ORDER,nasi.SIMUL_INFLATE]
    # 2) historical regressions
    reg=regressions.run_all(verbose=False)
    out["reg_ok"]=sum(r["ok"] for r in reg); out["reg_false0"]=sum(r.get("false_exact_zero",False) for r in reg)
    # 3) dev battery (fixed N=300, ARM O) -> coverage + false0
    emit=cov=f0=0
    for i in range(300):
        cs=devgen.build(i); q=cs["qmag"]
        r=nasi.identify(cs["Y"],cs["p"],cs["lam"],
            nasi.Contract(sign=cs["sign_true"],clean_anchor=cs["anchor_true"],sparsity_s=cs["sparsity_true"]),
            alpha=0.05,rng=np.random.default_rng(0xA11CE+i))
        if r.status in nasi.EMITTING:
            emit+=1; cov+=(r.contains(q) is True)
        if r.qset==[(0.0,0.0)] and q>1e-9: f0+=1
    out["dev300"]=[emit,cov,f0]
    # 4) prospective sample (fixed first 300, ARM O) -> false0 + invalid points
    pf0=ipn=0
    for i in range(300):
        cs=prospgen.build(i); q=cs["qmag"]
        r=nasi.identify(cs["Y"],cs["p"],cs["lam"],
            nasi.Contract(sign=cs["sign_true"],clean_anchor=cs["anchor_true"],sparsity_s=cs["sparsity_true"]),
            alpha=0.05,rng=np.random.default_rng(prospgen.PROSP_SEED_BASE+i))
        if r.qset==[(0.0,0.0)] and q>1e-9: pf0+=1
        if r.status==nasi.POINT and r.contains(q) is False: ipn+=1
    out["prosp300"]=[pf0,ipn]
    return out

if __name__=="__main__":
    out=canon()
    blob=json.dumps(out,sort_keys=True).encode()
    h=hashlib.sha256(blob).hexdigest()
    print(json.dumps(out))
    print("CANON_SHA256",h)
