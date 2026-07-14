"""DEV-ONLY calibration sweep for the frozen uncertainty constants. Arm O (truth contracts)."""
import numpy as np, collections, itertools, sys
import nasi, devgen

def snr_band(s): return "<=5" if s<=5 else ("5-10" if s<=10 else ("10-30" if s<=30 else ">30"))

def evaluate(N, order, block, inflate):
    nasi.DRIFT_ORDER=order; nasi.BLOCK_FRAC=block; nasi.SIMUL_INFLATE=inflate
    emit=cov=0; widths=[]; pts=0; oned=0
    byf=collections.defaultdict(lambda:[0,0]); byw=collections.defaultdict(lambda:[0,0])
    for i in range(N):
        cs=devgen.build(i); q=cs["qmag"]
        ctr=nasi.Contract(sign=cs["sign_true"], clean_anchor=cs["anchor_true"], sparsity_s=cs["sparsity_true"])
        r=nasi.identify(cs["Y"],cs["p"],cs["lam"],ctr,alpha=0.05,rng=np.random.default_rng(0xA11CE+i))
        if r.status in nasi.EMITTING:
            emit+=1; c=r.contains(q); cov+=(c is True)
            byf[cs["nf"]][1]+=1; byf[cs["nf"]][0]+=(c is True)
            if q>1e-9: byw[snr_band(cs["snr"])][1]+=1; byw[snr_band(cs["snr"])][0]+=(c is True)
            w=r.width_rel(q)
            if w is not None: widths.append(w)
            if r.status==nasi.POINT: pts+=1
            if r.status in (nasi.LOWER,nasi.UPPER,nasi.BELOWDET): oned+=1
    minfam=min((a/b if b else 1.0) for a,b in byf.values())
    weak=byw.get("<=5",[0,1]); weakr=weak[0]/max(1,weak[1])
    return dict(cov=cov/max(1,emit), emit=emit, minfam=minfam, weak=weakr, pts=pts, oned=oned,
                medw=float(np.median(widths)) if widths else None,
                famcov={k:round(a/b,3) for k,(a,b) in sorted(byf.items())})

if __name__=="__main__":
    N=int(sys.argv[1]) if len(sys.argv)>1 else 600
    print(f"{'order':5} {'block':6} {'infl':5} | {'cov':6} {'minfam':6} {'weak':6} {'pts':4} {'1sd':4} {'medw':7}")
    for order,block,infl in itertools.product([1,2],[0.20,0.30,0.40],[1.05]):
        m=evaluate(N,order,block,infl)
        print(f"{order:5} {block:6} {infl:5} | {m['cov']:.3f}  {m['minfam']:.3f}  {m['weak']:.3f}  {m['pts']:4} {m['oned']:4} {str(round(m['medw'],2) if m['medw'] else None):7}   {m['famcov']}")
