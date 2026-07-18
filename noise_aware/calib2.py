import numpy as np, sys, itertools
import calib
if __name__=="__main__":
    N=int(sys.argv[1]) if len(sys.argv)>1 else 800
    print(f"{'order':5} {'block':6} {'infl':5} | {'cov':6} {'minfam':6} {'weak':6} {'pts':4} {'1sd':4} {'medw':7}  famcov")
    for order,block,infl in itertools.product([1],[0.20,0.25],[1.05,1.08,1.12]):
        m=calib.evaluate(N,order,block,infl)
        print(f"{order:5} {block:6} {infl:5} | {m['cov']:.3f}  {m['minfam']:.3f}  {m['weak']:.3f}  {m['pts']:4} {m['oned']:4} {str(round(m['medw'],2)):7}  {m['famcov']}")
