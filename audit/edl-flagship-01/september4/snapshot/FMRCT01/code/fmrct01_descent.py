"""FMRCT01 §3 — the frozen organisational descent rule, and why it is stated this way.

MRCI01 clause 4 reads: "exactly ONE resulting component continues the previously established
parent identity, i.e. it is the unique component whose centroid lies within CORE_R of the
parent's last centroid."

Applied literally that requires the DAUGHTER to be OUTSIDE CORE_R of the parent's last centroid.
A separation in this architecture is gradual — a Y birth is Y-gated, so the newborn appears at the
occupied cell and the two constituents drift apart one hop at a time — so at the step where the
components first separate, the previous single component's centroid lies BETWEEN them and both are
typically inside CORE_R. Measured on FDOT01's 160 committed archives, the literal reading resolves
14 of 652 separations (2.1 %) and finds a daughter in 6 of 160 worlds. MRCI01's own design
arithmetic used 59 daughter-forming worlds, so its rate calculation and its descent code are not
consistent with each other. MRCI01's six synthetic cases cannot expose this: none of them places
both children inside CORE_R at different distances, which is the configuration the dynamics
actually produce.

THE FROZEN FMRCT01 RULE keeps every clause of MRCI01's definition that can bind, and drops only
the implicit requirement that the daughter be far away:

  1. exactly TWO components, else DESCENT_AMBIGUOUS_NOT_EXACTLY_TWO_COMPONENTS
  2. d_i = toroidal centroid distance from the parent's last centroid to component i
  3. exact tie d_0 == d_1               -> DESCENT_AMBIGUOUS_EXACT_TIE
  4. the parent is argmin d_i           -- continuity, not size, not age, not X mass
  5. min d_i must be <= CORE_R          -> else DESCENT_AMBIGUOUS_PARENT_NOT_CONTINUOUS
  6. the other component is the DAUGHTER
  7. both identities must survive under the strict FDOT01 link rule from the separation to
     maturation, else DESCENT_IDENTITY_NOT_CARRIED_TO_MATURATION

Clause 4 is FMRT01's frozen level 1, which is distance-based. §3's prohibitions are respected in
full: the larger component is not the parent, the older-looking component is not the parent, the
component with more X is not the parent, and nothing is assigned by hand after an outcome.
Clause 7 is STRICTER than anything MRCI01 required.

The literal reading is not discarded quietly: every block is classified under BOTH rules and both
counts are reported next to K.
"""
from __future__ import annotations
import sys
REPO="/home/claude/edl"
for _p in (f"{REPO}/FDOT01/code",):
    if _p not in sys.path: sys.path.insert(0,_p)
import fdot01_centres as CC
CORE_R=CC.CORE_R; L=CC.L

def distances(prev_cells,prev_comp,cur_cells,cur_comps):
    pc=CC.centroid(prev_cells,prev_comp)
    return [CC.tdist(pc,CC.centroid(cur_cells,g)) for g in cur_comps]

def descent(prev_cells,prev_comp,cur_cells,cur_comps):
    """FROZEN FMRCT01 rule. Returns (parent_index, daughter_index, verdict)."""
    if len(cur_comps)!=2:
        return None,None,"DESCENT_AMBIGUOUS_NOT_EXACTLY_TWO_COMPONENTS"
    d=distances(prev_cells,prev_comp,cur_cells,cur_comps)
    if d[0]==d[1]:
        return None,None,"DESCENT_AMBIGUOUS_EXACT_TIE"
    p=0 if d[0]<d[1] else 1
    if d[p]>CORE_R:
        return None,None,"DESCENT_AMBIGUOUS_PARENT_NOT_CONTINUOUS"
    return p,1-p,"PARENT_CONTINUED_UNIQUELY"

def descent_literal_mrci01(prev_cells,prev_comp,cur_cells,cur_comps):
    """the literal MRCI01 clause 4, kept for reporting alongside every block."""
    if len(cur_comps)!=2:
        return None,None,"DESCENT_AMBIGUOUS_NOT_EXACTLY_TWO_COMPONENTS"
    d=distances(prev_cells,prev_comp,cur_cells,cur_comps)
    cand=[i for i,x in enumerate(d) if x<=CORE_R]
    if len(cand)!=1:
        return None,None,("DESCENT_AMBIGUOUS_BOTH_INSIDE_CORE_R" if len(cand)==2
                          else "DESCENT_AMBIGUOUS_NONE_INSIDE_CORE_R")
    return cand[0],1-cand[0],"PARENT_CONTINUED_UNIQUELY"
