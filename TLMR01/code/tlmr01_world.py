"""TLMR01 §3 §4 — the developmental world: the exact inherited protocol with LOSSLESS
instrumentation, so every measurement object M1-M5 is reconstructable offline WITHOUT importing
the online trigger or endpoint implementation.

INERTNESS. This subclasses FDOT01's FDOTWorld, which subclasses PQEC01's observer, both reused
byte-unchanged. The additions are read-only buffers: they read engine arrays and append to their
own lists, drawing no number from any engine generator and mutating no engine array. The claim is
NOT asserted — tlmr01_fixtures.py tests it bit-for-bit against a plain world on all three laws.

PROTOCOL. Every world runs the full frozen horizon T_HORIZON = 11000 with no scientific early
stop. Before the frozen functional-daughter trigger the trajectory is endogenous and unmodified.
At the trigger the exact inherited SELECTIVE_PARENT_REMOVAL is applied to the parent cells only,
the daughter state is left physically untouched, and the same world continues to the horizon. If
no trigger occurs, no intervention is applied and the world still runs to the horizon.
"""
from __future__ import annotations
import sys, json, hashlib
import numpy as np
REPO="/home/claude/edl"
for _p in (f"{REPO}/FMRCT01/code", f"{REPO}/FDOT01/code", f"{REPO}/PQEC01/code",
           f"{REPO}/MRCI01/code", f"{REPO}/FMRT01/code", f"{REPO}/FDFLT01/code",
           "/home/claude/ORR01/code", "/home/claude/OBTC02/code"):
    if _p not in sys.path: sys.path.insert(0,_p)
import pqec01_observer as O           # byte-unchanged
import fdot01_world as FW             # byte-unchanged
import fdot01_centres as CC           # byte-unchanged: the frozen centre classifier
import fmrct01_world as FMW           # byte-unchanged: intervene / phys_hash / rng_hash
import fmrct01_track as TR            # byte-unchanged: the frozen trigger
import fmrt01_identity as ID          # byte-unchanged: the frozen local-X disc and centroid
import fmrt01_endpoint as EP          # byte-unchanged: state_of / local_x_masses / f5_ratio
SPECIES=O.SPECIES
L=CC.L; CORE_R=CC.CORE_R
NEED=TR.NEED; LATEST=TR.LATEST_ALLOWED_TRIGGER; T_HORIZON=TR.T_HORIZON
F_PRIMARY=TR.F_PRIMARY
# The two frozen geometry modules read their constants from DIFFERENT files - fdot01_centres from
# PQEC01's freeze, fmrt01_identity from the OBTC02 protocol YAML. If they ever disagreed, the
# centre classifier and the local-X disc would be measuring different worlds. Asserted, not assumed.
assert int(ID.L)==int(CC.L) and float(ID.CORE_R)==float(CC.CORE_R), \
    "fmrt01_identity and fdot01_centres disagree on L or CORE_R"

# The frozen local-X mass is the sum of X over ID.disc_mask(round(cy)%L, round(cx)%L). Rebuilding
# that (L,L) boolean for every component at every step is the dominant instrumentation cost, so the
# disc is stored ONCE as offsets taken FROM ID.disc_mask itself and translated. The equality of the
# two routes is proved for all L*L centres by tlmr01_paths.disc_equivalence, never assumed.
_DOY,_DOX=np.nonzero(ID.disc_mask(0,0))
_DOY=_DOY.astype(np.int64); _DOX=_DOX.astype(np.int64)
def x_disc_mass(nX,cy,cx):
    return int(nX[(_DOY+int(cy))%L,(_DOX+int(cx))%L].sum())

class TLMRWorld(FW.FDOTWorld):
    def tlmr_init(self):
        self.fdot_init()
        self.tl_step=[]      # (t, nY_total, nX_total, nSY_total, nSX_total, free_min, n_cells, n_comps)
        self.tl_cells=[]     # (t, y, x, nY, nX, nSY, free, cand_Y, comp_id)   LOSSLESS per occupied Y cell
        self.tl_comp=[]      # (t, comp_id, n_cells, nY_in_comp, a0y, a0x, soy, sox, x_disc)
        # a0/soy/sox are the EXACT centroid inputs, not a rounded centroid: the frozen centroid is
        # (a0 + sum(offsets)/m) % L, and storing a rounded value would let an offline identity link
        # flip at a distance within rounding of CORE_R. The offline reader recomputes the frozen
        # expression in the same order and is therefore bit-identical, which §5 proves per step.
        return self
    def tl_record(self,t):
        nY=self.n["Y"]; nX=self.n["X"]; nSY=self.n["SY"]
        occ=sum(self.n[s] for s in SPECIES)
        free=self.sp.CAP-occ
        ys,xs=np.nonzero(nY)
        cells=[(int(y),int(x)) for y,x in zip(ys,xs)]
        comps=CC.components(cells) if cells else []
        cid={}
        for k,g in enumerate(comps):
            for i in g: cid[cells[i]]=k
        for i,(y,x) in enumerate(cells):
            # cand_Y is the frozen local birth propensity input: kY * nX * nY at this cell.
            self.tl_cells.append((t,y,x,int(nY[y,x]),int(nX[y,x]),int(nSY[y,x]),
                                  int(free[y,x]),
                                  int(round(1e6*min(1.0,self.sp.kY*float(nX[y,x])*float(nY[y,x])))),
                                  cid.get((y,x),-1)))
        for k,g in enumerate(comps):
            a0=cells[g[0]]
            soy=int(sum(((cells[i][0]-a0[0]+L/2)%L)-L/2 for i in g))
            sox=int(sum(((cells[i][1]-a0[1]+L/2)%L)-L/2 for i in g))
            cy,cx=CC.centroid(cells,g)
            # x_disc is the EXACT input to the frozen f5 ratio: the sum of X over the CORE_R disc
            # at the rounded centroid. Without it, P(trigger | matured) cannot be reconstructed
            # from the archive at all, because that disc covers cells carrying no Y and no other
            # recorded row sees them. Found while deriving M3. The schema is widened before world
            # 1, never after.
            self.tl_comp.append((t,k,len(g),int(sum(nY[cells[i]] for i in g)),
                                 int(a0[0]),int(a0[1]),soy,sox,
                                 x_disc_mass(nX,int(round(cy))%L,int(round(cx))%L)))
        self.tl_step.append((t,int(nY.sum()),int(nX.sum()),int(nSY.sum()),int(self.n["SX"].sum()),
                             int(free.min()),len(cells),len(comps)))
        return cells,comps

def build(seed,kY,muY,p_hop_Y,horizon=T_HORIZON):
    _cls=O.PQECWorld
    O.PQECWorld=TLMRWorld
    try:
        w,rec,sp=O.build_world(seed,kY,muY,L=None,horizon=horizon,instrumented=True,
                               record_fields=False,p_hop_Y=float(p_hop_Y))
    finally:
        O.PQECWorld=_cls
    w.tlmr_init()
    assert float(sp.p_hop_Y)==float(p_hop_Y), "p_hop_Y did not reach the spec"
    assert float(sp.kY)==float(kY) and float(sp.muY)==float(muY), "Y law did not reach the spec"
    return w,rec,sp

def run_world(seed,kY,muY,p_hop_Y,horizon=T_HORIZON,instrument=True):
    """The complete developmental protocol in ONE trajectory. Returns the world and a record."""
    w,rec,sp=build(seed,kY,muY,p_hop_Y,horizon)
    trig=TR.Trigger()
    interv={"applied":False,"step":None,"parent_cells":None,"removed_Y":0,
            "phys_hash_before":None,"phys_hash_after":None,
            "rng_hash_before":None,"rng_hash_after":None,
            "daughter_cells_before":None,"daughter_cells_after":None,
            "Y_total_before":None,"Y_total_after":None,
            "WY_total_before":None,"WY_total_after":None,
            "parent_Y_after":None,"daughter_Y_before":None,"daughter_Y_after":None}
    # The frozen FMRCT01 trigger keeps OVERWRITING descent_level/descent_step at every later
    # 1 -> 2 transition, so its terminal value is the LAST separation in the trajectory and not
    # the one that named this parent. Found by the §5 path-coverage fixture. The values as of the
    # firing step are therefore snapshotted here; the terminal values are reported separately and
    # neither is allowed to stand in for the other.
    at_trigger=None
    integ=True; stop="HORIZON"; stop_step=horizon
    for t in range(horizon):
        w._one_step()
        free=sp.CAP-sum(w.n[s] for s in SPECIES)
        if free.min()<0 or max(w.n[s].max() for s in SPECIES)>sp.CAP:
            integ=False; stop="INTEGRITY_FAILURE"; stop_step=t; break
        if instrument:
            cells,comps=w.tl_record(t)
        else:
            ys,xs=np.nonzero(w.n["Y"]); cells=[(int(y),int(x)) for y,x in zip(ys,xs)]
            comps=CC.components(cells) if cells else []
        trig.observe(t,w,cells,comps,integ)
        if at_trigger is None and trig.t_m is not None:
            at_trigger={"step":int(trig.t_m),"descent_level":trig.descent_level,
                        "descent_step":trig.descent_step,"descent_literal":trig.descent_literal,
                        "descent_distances":trig.descent_distances,
                        "n_descent_attempts_so_far":int(trig.n_descent_attempts),
                        "identity_carried_to_maturation":trig.parent_comp is not None}
        if (not interv["applied"]) and trig.t_m is not None and t>=trig.t_m:
            pc=trig.parent_comp; dc=trig.daughter_comp
            if pc is not None:
                pcells=[trig.cells_tm[i] for i in pc] if trig.cells_tm else []
                dcells=[trig.cells_tm[i] for i in dc] if (trig.cells_tm and dc is not None) else []
                interv["phys_hash_before"]=FMW.phys_hash(w); interv["rng_hash_before"]=FMW.rng_hash(w)
                interv["daughter_cells_before"]=[[int(a),int(b)] for a,b in dcells]
                removed=int(sum(int(w.n["Y"][y,x]) for y,x in pcells))
                interv["Y_total_before"]=int(w.n["Y"].sum()); interv["WY_total_before"]=int(w.n["WY"].sum())
                interv["daughter_Y_before"]=int(sum(int(w.n["Y"][y,x]) for y,x in dcells))
                FMW.intervene(w,pcells)                      # SELECTIVE_PARENT_REMOVAL, byte-unchanged
                interv.update({"applied":True,"step":t,
                    "parent_cells":[[int(a),int(b)] for a,b in pcells],"removed_Y":removed,
                    "phys_hash_after":FMW.phys_hash(w),"rng_hash_after":FMW.rng_hash(w),
                    "daughter_cells_after":[[int(a),int(b)] for a,b in dcells],
                    "Y_total_after":int(w.n["Y"].sum()),"WY_total_after":int(w.n["WY"].sum()),
                    "parent_Y_after":int(sum(int(w.n["Y"][y,x]) for y,x in pcells)),
                    "daughter_Y_after":int(sum(int(w.n["Y"][y,x]) for y,x in dcells))})
    n_rec=min(stop_step+1,horizon)
    if trig.t_m is None:                        label="NOT_TRIGGERED"
    elif not interv["applied"]:                 label="TRIGGERED_IDENTITY_NOT_CARRIED__NO_REMOVAL"
    else:                                       label="TRIGGERED_AND_SELECTIVE_REMOVAL_APPLIED"
    return w,{"steps_executed":n_rec,"stop":stop,"integrity_ok":bool(integ),
              "TERMINAL_LABEL":label,
              "t_m":trig.t_m,
              "AT_TRIGGER":at_trigger,
              "terminal_descent_level":trig.descent_level,
              "terminal_descent_step":trig.descent_step,
              "descent_level":(at_trigger or {}).get("descent_level","DESCENT_NEVER_ATTEMPTED"),
              "descent_step":(at_trigger or {}).get("descent_step"),
              "n_descent_attempts":trig.n_descent_attempts,
              "intervention":interv,"final_state_hash":FMW.phys_hash(w)}
