"""FMRT01 — the frozen endpoint: trigger, R1 exact, R2 exact. Frozen before the first world."""
from __future__ import annotations
import json, math, sys
import numpy as np, yaml
from scipy.stats import binom
REPO="/home/claude/edl"
sys.path.insert(0,f"{REPO}/FMRT01/code"); sys.path.insert(0,f"{REPO}/FDFLT01/code")
import fmrt01_identity as ID
import fdflt01_endpoint as FD                    # the frozen FDFLT01 maturation criterion
P=yaml.safe_load(open(f"{REPO}/OBTC02/code/obtc02_protocol.yaml"))
L=ID.L; CORE_R=ID.CORE_R; MUX=float(P["point"]["muX"])
NEED=FD.STEPS["T_primary"]                       # 250
F_PRIMARY=FD.F_PRIMARY
T_HOLD=NEED                                      # 250, one e-folding of the slowest X mode
TOTAL_HORIZON=11000
LATEST_ALLOWED_TRIGGER=TOTAL_HORIZON-T_HOLD      # 10750
SURV_HOLD=(1.0-MUX)**T_HOLD

def survivor_upper(N,conf=0.95):
    return 0 if N<=0 else int(binom.ppf(conf,N,SURV_HOLD))

def state_of(nY,ncen,integrity_ok):
    if not integrity_ok: return "F"
    if nY==0: return "E"
    if ncen>=3: return "P"
    if nY==1: return "O"
    return "S" if ncen==2 else "C"

class TriggerWatcher:
    """Detects the FIRST FDFLT01 functional maturation event, online, during phase 1.

    The trigger is the frozen FDFLT01 criterion: a maximal run of exactly two spatial centres
    lasting at least NEED steps, with no third centre inside the window, and the weaker
    centre's local X mass at the event at least F_PRIMARY of the stronger's. R1 is NOT part
    of the trigger; it is classified separately at t_m so the intervention can never be
    delayed until a favourable provenance state appears.
    """
    def __init__(self):
        self.run_start=None; self.saw_P_in_run=False; self.fired=False; self.t_m=None
    def observe(self,t,st):
        if self.fired: return False
        if st=="S":
            if self.run_start is None: self.run_start=t; self.saw_P_in_run=False
            # the frozen FDFLT01 semantics: the maturation event of an episode is at EXACTLY
            # run_start + NEED - 1, not at every later step of a long run.
            if (t-self.run_start+1)==NEED and not self.saw_P_in_run:
                return True
            return False
        if st=="P" and self.run_start is not None: self.saw_P_in_run=True
        self.run_start=None
        return False

def local_x_masses(Xplane,cells,comps):
    vals=[float(Xplane[ID.disc_mask(*[int(round(v))%L for v in ID.centroid(cells,g)])].sum()) for g in comps]
    return vals

def f5_ratio(vals):
    hi=max(vals) if vals else 0.0
    return (min(vals)/hi) if hi>0 else 0.0
