"""WSFSCRP00: candidate queue, admissibility, balanced role allocation, and the Q0 oracle.

Frozen BEFORE the first candidate is generated, in this file, top to bottom. The allocation
utility emits only admissibility, ancestry-cluster id, canonical-geometry id and an opaque
founder id -- no arrays, masks, descriptors or outcome proxies.
"""
from __future__ import annotations
import sys, os, json, hashlib
sys.path.insert(0, "/home/claude/sweep/WSFSCRP00")
import numpy as np
import wsfscrp_core as Z

OUT = "/home/claude/sweep/WSFSCRP00"
CKD = f"{OUT}/checkpoints"
os.makedirs(CKD, exist_ok=True)
STARTS = {"n": 0, "log": []}


def start(tag):
    STARTS["n"] += 1
    STARTS["log"].append(tag)


# ---------------------------------------------------------------- FROZEN candidate queue
# Fresh seeds, disjoint from every project namespace already used or reserved:
#   61000-61009 ETPC/WSC exposed DEV, 62000-62009 ETPC project held-out, 63xxx reserved.
QUEUE = [(64000 + i, "FAR" if i % 2 == 0 else "NEAR") for i in range(16)]
ALLOC_SALT = "WSFSCRP00-balanced-role-allocation-v1"

FREEZE = {
    "programme": "WARPED_SCALE_FIXED_SUPPORT_CAUSAL_RESPONSE_PILOT_00",
    "parent_commit": "e912a1004c5b9732d12a8fcc417002bfd1135622",
    "parent_bundle_sha256": "f8cc3df772e55c83b9179f1281f0eb0ba30845c14aa02b2139899293f019e62b",
    "grandparent_commit": "7cc1ffa0a782a34774a57094189ed19f6bd2b761",
    "candidate_queue": [[s, g] for s, g in QUEUE],
    "queue_len": len(QUEUE), "max_used": 12,
    "namespace_note": "64000+ is disjoint from 61000-61009 (exposed DEV), 62000-62009 (project "
                      "held-out, never touched) and 63xxx (reserved).",
    "geometry_classes": ["FAR", "NEAR"],
    "geometry_note": "NEAR is used as a GEOMETRY CLASS with fresh seeds. The project held-out "
                     "SEEDS 62000-62009 are not used and not read.",
    "admissibility": "exactly two components of {rho > 0.30} with at least 12 sites, on the "
                     "periodic 4-connected lattice, at t0. Zero, one or more than two -> reject "
                     "and take the next queue entry. Never select the convenient largest pair.",
    "ancestry_cluster": "one per distinct generator seed: seed_state(...) is drawn independently "
                        "per seed, so two seeds share no pre-t0 state that could correlate their "
                        "scored futures. Sharing only the LawSpec is NOT one cluster.",
    "role_allocation": "deterministic balanced hash rule on the OPAQUE founder id; roles are "
                       "assigned without inspecting any candidate's state beyond admissibility, "
                       "ancestry id and canonical geometry id.",
    "alloc_salt": ALLOC_SALT,
    "endpoint": "two-channel fixed-t0-support integrated-rho response; see the endpoint spec",
    "H_grid_native_steps": Z.H_GRID,
    "physical_times": [str(p) for p in Z.PHYS],
    "trapezoid_weights": [str(w) for w in Z.W],
    "detector": {"threshold": Z.RHO_THRESHOLD, "strict": ">", "min_sites": Z.MIN_SITES,
                 "connectivity": "4-connected, periodic", "pair": "unordered, canonicalised by "
                                                                 "sorted immutable site-id lists"},
    "superfamilies": {
        "TRAIN_SUPERFAMILY_1": "CONSERVATIVE_CARRIER_REDISTRIBUTION",
        "TRAIN_SUPERFAMILY_2": "NONCONSERVATIVE_CARRIER_TRANSFORMATION",
        "LOCKED_SUPERFAMILY_1": "ENVIRONMENTAL_FIELD_PERTURBATION"},
    "family_evidence_level": "RESPONSE_INFORMED_HELD_OUT_SINGLE_SUPERFAMILY_TRANSFER",
    "STRICT_PROSPECTIVE_OUT_OF_FAMILY": False,
    "FULL_MULTI_SUPERFAMILY_TRANSFER_PASS_ELIGIBLE": False,
    "budget": {"qualification": 48, "post_gate": 144, "total": 192},
}
json.dump(FREEZE, open(f"{OUT}/WSFSCRP00_FREEZE_PRE_GENERATION.json", "w"), indent=1)
print("pre-generation freeze sha:",
      hashlib.sha256(open(f"{OUT}/WSFSCRP00_FREEZE_PRE_GENERATION.json", "rb").read()).hexdigest()[:16])


def opaque_id(seed, geom):
    return hashlib.sha256(f"{ALLOC_SALT}|{seed}|{geom}".encode()).hexdigest()[:16]


# ---------------------------------------------------------------- generate and screen
ledger = []
admissible = []
for seed, geom in QUEUE:
    if len(admissible) >= 12:
        ledger.append({"seed": seed, "geometry": geom, "status": "NOT_REACHED__QUOTA_FILLED"})
        continue
    start(f"GEN_{seed}_{geom}")
    st = Z.make_founder(seed, geom)
    masks, meta = Z.t0_masks(st)
    oid = opaque_id(seed, geom)
    if masks is None:
        ledger.append({"seed": seed, "geometry": geom, "opaque_id": oid,
                       "status": "REJECTED__NOT_EXACTLY_TWO_ELIGIBLE_COMPONENTS", **meta})
        print(f"  {seed} {geom}: REJECTED n_eligible={meta['n_eligible']} sizes={meta['sizes'][:6]}")
        continue
    MA, MB = masks
    ref = Z.reference_masks(st)
    prod = tuple(sorted((tuple(meta["ids_A"]), tuple(meta["ids_B"]))))
    agree = ref == prod
    path = f"{CKD}/f_{seed}_{geom}.npz"
    sha = Z.save(st, path)
    np.savez(f"{CKD}/m_{seed}_{geom}.npz", MA=MA, MB=MB)
    B = Z.B_of(st, MA, MB)
    rec = {"seed": seed, "geometry": geom, "opaque_id": oid, "status": "ADMISSIBLE",
           "ancestry_cluster": f"seed:{seed}", "canonical_geometry_id": Z.canonical_geometry_id(geom, meta),
           "n_A": meta["n_A"], "n_B": meta["n_B"], "mask_sha": meta["mask_sha"],
           "checkpoint_sha": sha, "B_b": str(B), "B_positive": B > 0,
           "production_reference_mask_agreement": bool(agree)}
    ledger.append(rec)
    admissible.append(rec)
    print(f"  {seed} {geom}: ADMISSIBLE nA={meta['n_A']} nB={meta['n_B']} "
          f"ref_agree={agree} B={float(B):.4f}", flush=True)

# ---------------------------------------------------------------- balanced role allocation
def role_key(rec):
    return int(hashlib.sha256((ALLOC_SALT + "|role|" + rec["opaque_id"]).encode()).hexdigest(), 16)


roles = {"TRAIN_SELECTION": [], "LOCKED_DEV_EVALUATION": []}
for geom in ("FAR", "NEAR"):
    grp = sorted([r for r in admissible if r["geometry"] == geom], key=role_key)
    for i, r in enumerate(grp):
        tgt = "TRAIN_SELECTION" if i % 2 == 0 else "LOCKED_DEV_EVALUATION"
        if len(roles[tgt]) < 6:
            roles[tgt].append(r)
        elif len(roles["TRAIN_SELECTION" if tgt != "TRAIN_SELECTION" else
                       "LOCKED_DEV_EVALUATION"]) < 6:
            roles["TRAIN_SELECTION" if tgt != "TRAIN_SELECTION"
                  else "LOCKED_DEV_EVALUATION"].append(r)
for r in roles["TRAIN_SELECTION"]:
    r["role"] = "TRAIN_SELECTION"
for r in roles["LOCKED_DEV_EVALUATION"]:
    r["role"] = "LOCKED_DEV_EVALUATION"

summary = {"n_candidates_generated": sum(1 for r in ledger if r.get("status") != "NOT_REACHED__QUOTA_FILLED"),
           "n_admissible": len(admissible), "n_used": len(roles["TRAIN_SELECTION"]) + len(roles["LOCKED_DEV_EVALUATION"]),
           "TRAIN_SELECTION": [(r["seed"], r["geometry"]) for r in roles["TRAIN_SELECTION"]],
           "LOCKED_DEV_EVALUATION": [(r["seed"], r["geometry"]) for r in roles["LOCKED_DEV_EVALUATION"]],
           "train_ancestry_clusters": len({r["ancestry_cluster"] for r in roles["TRAIN_SELECTION"]}),
           "locked_ancestry_clusters": len({r["ancestry_cluster"] for r in roles["LOCKED_DEV_EVALUATION"]}),
           "train_geometry_classes": sorted({r["geometry"] for r in roles["TRAIN_SELECTION"]}),
           "locked_geometry_classes": sorted({r["geometry"] for r in roles["LOCKED_DEV_EVALUATION"]}),
           "all_production_reference_agree": all(r["production_reference_mask_agreement"] for r in admissible),
           "all_B_positive": all(r["B_positive"] for r in admissible)}
json.dump({"ledger": ledger, "roles": summary, "engine_starts": STARTS},
          open(f"{OUT}/WSFSCRP00_CANDIDATE_QUEUE_AND_ACCEPTANCE_LEDGER.json", "w"), indent=1)
print("\n", json.dumps(summary, indent=1))
print("STARTS:", STARTS["n"])
