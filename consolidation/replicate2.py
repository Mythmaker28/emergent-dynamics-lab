"""SECOND independent clean-room implementation of the sign-safe set-identification rule. Does NOT import
signsafe.py. Written from the SET_IDENTIFICATION_MANUSCRIPT map only. Different code, same math."""
import numpy as np
def identify2(channels, couplings, onset, wlen, has_clean, sign):
    m=len(channels); win=slice(onset,onset+wlen); pre=slice(max(0,onset-wlen),onset)
    inv=1.0/np.where(np.abs(couplings)>1e-9,couplings,1e-9)
    diversity=np.std(inv)/(abs(np.mean(inv))+1e-30)
    if diversity<0.15: return "ILL", None
    mag=np.array([channels[i][win].std() for i in range(m)])
    base=np.array([channels[i][pre].std() for i in range(m)])
    if np.median(mag)<2*np.median(base): return "POINT",(0.,0.)
    lo,hi=mag.min(),mag.max(); rel=(hi-lo)/(0.5*(hi+lo)+1e-30); same=rel<0.045
    if has_clean:
        if same: return "POINT",(0.5*(lo+hi),)*2
        if sign=="attenuate": return "POINT",(hi,hi)
        if sign=="amplify":   return "POINT",(lo,lo)
        return "INTERVAL",(lo,hi)
    if same: return "NONID",None
    if sign=="attenuate": return "LOWER",(hi,np.inf)
    if sign=="amplify":   return "UPPER",(0.,lo)
    return "NONID",None
