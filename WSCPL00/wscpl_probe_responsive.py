"""WSCPL00 Phase B1, decisive probe: is the candidate macro branch INTERVENTION-RESPONSIVE?

A branch endpoint that no admissible intervention can move has zero label variance under
intervention, and there is nothing for a causal multiscale representation to predict. This
probe applies the STRONGEST already-implemented admissible operators -- including total carrier
ablation, which is the maximum possible intervention on Mf -- and asks whether the branch label
ever differs from its sham twin.

FORMULATION_TRAIN role only. Development blocks only.
"""
from __future__ import annotations
import sys, json
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/PPAI")
sys.path.insert(0, "/home/claude/sweep/ETPC")
sys.path.insert(0, "/home/claude/sweep/ETCMNFC")
import numpy as np
import domc_core as K, ppai_core as P, etpc_core as E, etcmnfc_core as Z

CK = "/home/claude/sweep/ETNBFC/checkpoints"
FORM = (61000, 61001)
H = 400
STARTS = {"n": 0, "log": []}
K.set_geometry("FAR")


def branch(st):
    pick, _, n = K.read_sites(st)
    if pick["A"] is None or pick["B"] is None:
        return None, None, None
    mA = float(st.rho[pick["A"].cells[:, 0], pick["A"].cells[:, 1]].sum())
    mB = float(st.rho[pick["B"].cells[:, 0], pick["B"].cells[:, 1]].sum())
    return int(np.sign(mA - mB)), mA, mB


def arms(st0, mem):
    man, I, J = Z.manifest(st0, mem)
    return {
        "SHAM": lambda s: s.copy(),
        "CARRIER_TRANSPOSITION": lambda s: Z.transpose(s, I, J),
        "INTENSIVE_REFLECTION": lambda s: P.state_cross(s),
        "EXTENSIVE_REFLECTION": lambda s: K.reciprocal_cross(s),
        "TOTAL_CARRIER_ABLATION": lambda s: P.erase_all(s),
        "ENVIRONMENT_PERTURBATION": lambda s: K._perturb_N(s, 0.5),
    }


rows = []
for sd in FORM:
    st0 = E.load(f"{CK}/dev_FAR_{sd}.npz")
    mem, _ = E.members(st0)
    b0, m0a, m0b = branch(st0)
    res = {}
    for nm, op in arms(st0, mem).items():
        s = op(st0.copy())
        eng = Z.engine(Z.GAIN_ON)
        STARTS["n"] += 1
        STARTS["log"].append(f"FORM_RESP_{sd}_{nm}")
        cur = s.copy()
        traj = []
        for t in range(H):
            cur = eng.step(cur)
            if (t + 1) % 40 == 0:
                bb, ma, mb = branch(cur)
                traj.append({"t": t + 1, "branch": bb,
                             "dm": (ma - mb) if ma is not None else None})
        bb, ma, mb = branch(cur)
        res[nm] = {"branch_at_H": bb, "mass_diff_at_H": (ma - mb) if ma is not None else None,
                   "traj": traj}
        print(f"  {sd} {nm:<26} branch={bb} dm={res[nm]['mass_diff_at_H']}", flush=True)
    sham = res["SHAM"]["branch_at_H"]
    flipped = [k for k, v in res.items() if k != "SHAM" and v["branch_at_H"] != sham]
    rows.append({"seed": sd, "branch_at_t0": b0, "sham_branch_at_H": sham,
                 "arms": res, "arms_that_flipped_the_branch": flipped,
                 "any_flip": bool(flipped)})
    print(f"seed {sd}: sham branch={sham}; arms that FLIPPED it = {flipped or 'NONE'}\n", flush=True)

out = {"role": "FORMULATION_TRAIN", "horizon": H, "engine_starts": STARTS, "blocks": rows,
       "any_intervention_moved_the_branch": any(r["any_flip"] for r in rows)}
json.dump(out, open("/home/claude/sweep/WSCPL00/wscpl_probe_responsive.json", "w"), indent=1)
print("ANY INTERVENTION MOVED THE BRANCH:", out["any_intervention_moved_the_branch"])
print("STARTS:", STARTS["n"])
