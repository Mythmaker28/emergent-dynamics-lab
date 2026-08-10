"""WL2SMF00 Sections 6-7 -- static H/G route audit, constructor refactor with byte-equivalence,
frozen queue, target-panel construction, and the PANEL LOCK. No post-t0 advance happens here.

START CONVENTION, inherited from WSFSCRP00 unchanged: one constructed descendant state = 1 start.
A precursor shared by an allocation pair is an internal sub-step of that pair, exactly as
`make_founder` (found + advance + history + advance) was a single start in the parent. The raw
count of engine advance sequences is logged separately for transparency.
"""
from __future__ import annotations
import sys, os, json, hashlib, time
from fractions import Fraction as Fr
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/PPAI")
sys.path.insert(0, "/home/claude/sweep/ETPC")
sys.path.insert(0, "/home/claude/sweep/WSFSCRP00")
import numpy as np
import wsfscrp_core as Z
import domc_core as K
import ppai_core as PC
from edlab.experiments.sc_mcm import config as C

OUT = "/home/claude/sweep/WL2SMF00"
CK = f"{OUT}/checkpoints"
os.makedirs(CK, exist_ok=True)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
FZ = json.load(open(f"{OUT}/WL2SMF00_MASTER_FREEZE_HASHES.json"))
for f, h in FZ["hashes"].items():
    assert sha(f"{OUT}/{f}") == h, "freeze mutated"
QUEUE = FZ["namespace_queue"]
LEDGER = {"C_SETUP": 0, "construction": 0, "raw_advance_sequences": 0, "log": []}


def start(tag, kind):
    LEDGER[kind] += 1
    LEDGER["log"].append({"tag": tag, "kind": kind})
    assert LEDGER["C_SETUP"] + LEDGER["construction"] <= 32, "construction budget exceeded"


# =====================================================================================
# 6. STATIC HISTORY / GEOMETRY ROUTE AUDIT  (zero starts: no engine step here)
# =====================================================================================
audit = {}
# ---- is the upstream RNG precursor geometry-independent? -------------------------------
def seedfield_sha(seed):
    s = C.seed_state(C.SPEC, C.TRACER, seed, "random")
    h = hashlib.sha256()
    for nm in ("rho", "U", "V", "c", "N", "C", "uptake"):
        a = np.ascontiguousarray(np.asarray(getattr(s, nm)))
        h.update(nm.encode()); h.update(a.tobytes())
    return h.hexdigest()


K.set_geometry("FAR")
sf_far = seedfield_sha(QUEUE[0])
K.set_geometry("NEAR")
sf_near = seedfield_sha(QUEUE[0])
audit["G_route"] = {
    "upstream_rng_precursor_is_geometry_independent": sf_far == sf_near,
    "evidence": "domc_core.found(seed) = C.seed_state(SPEC,TRACER,seed,'random') * _blob(); the "
                "RNG draw takes no geometry argument, and geometry enters only through the "
                "multiplicative blob mask built from SITE_A/SITE_B. Hashing the seed_state under "
                "both geometry settings gives the same digest.",
    "geometry_is_an_explicit_constructor_argument": True,
    "route": "G1" if sf_far == sf_near else "G2",
    "geometry_definition": "the inherited exchange-invariant frozen geometry classes "
                           "FAR = ((32,16),(32,48)) and NEAR = ((32,24),(32,40)), both symmetric "
                           "about x = L/2 so the same reflection exchanges the two sites in both. "
                           "Geometry is ASSIGNED here, not classified, so no threshold is tuned.",
}
# ---- history route -----------------------------------------------------------------------
src = open("/home/claude/sweep/DOMC/domc_core.py").read()
audit["H_route"] = {
    "H1_global_temporal_order": {
        "eligible": False,
        "why": "apply_dual_history delivers hA to HALF_A and hB to HALF_B IN LOCKSTEP; its own "
               "docstring proves the GLOBAL forcing time series is identical between the two "
               "assignments. There is no H-then-L versus L-then-H global sequence to contrast."},
    "H2_prehistory_physical_anchor": {
        "eligible": False,
        "why": "no anchor formula was uniquely designated in committed pre-outcome artifacts "
               "before FSCMA00 outcomes. Seed parity, serialized A/B, site id, queue position and "
               "filename are excluded by rule, and nominating a new state feature now would be "
               "response-informed."},
    "H3_complementary_allocation_orbit": {
        "eligible": True,
        "why": "both allocations are executable from IDENTICAL precursor bytes: "
               "apply_dual_history(eng, f, hA, hB) takes the two histories as arguments and the "
               "precursor f is the same object for both branches.",
        "branch_names": "neutral a = 0, 1; the serializer is scientifically meaningless",
        "signed_contrast": "NOT_DEFINED"},
    "selected": "H3",
    "lockstep_assert_present": "assert na == nb" in src,
    "half_planes": "HALF_A = x in [0,32), HALF_B = x in [32,64); geometry-independent",
}
audit["HISTORY_FACTOR_ROUTE"] = "H3"
audit["TARGET_PANEL_ROUTE"] = audit["G_route"]["route"]
assert audit["TARGET_PANEL_ROUTE"] == "G1"


# =====================================================================================
# CONSTRUCTOR REFACTOR -- explicit (geometry, allocation) arguments, semantics preserved
# =====================================================================================
def precursor(seed, geom):
    """found + relaxation. Shared by both allocations of this (seed, geometry)."""
    K.set_geometry(geom)
    e = Z.engine()
    LEDGER["raw_advance_sequences"] += 1
    return e, K.advance(e, K.found(seed), K.T_FOUND)


def branch(e, f, alloc):
    """apply the allocation and settle. alloc 0 = (HIST_H on half A), alloc 1 = complementary."""
    hA, hB = (PC.HIST_H, PC.HIST_L) if alloc == 0 else (PC.HIST_L, PC.HIST_H)
    LEDGER["raw_advance_sequences"] += 1
    return K.advance(e, K.apply_dual_history(e, f, hA, hB), K.SETTLE)


def legacy_alloc(seed):
    """the allocation the OLD parity-selected constructor would have chosen."""
    return 0 if seed % 2 == 0 else 1


# ---- byte-equivalence replay against two old descendants, one per parity branch ---------
OLDLED = json.load(open("/home/claude/sweep/WSFSCRP00/WSFSCRP00_CANDIDATE_QUEUE_AND_ACCEPTANCE_LEDGER.json"))
OLDSHA = {(r["seed"], r["geometry"]): r["checkpoint_sha"]
          for r in OLDLED["ledger"] if r.get("status") == "ADMISSIBLE"}
equiv = []
t0 = time.time()
for seed, geom in ((64000, "FAR"), (64001, "NEAR")):
    start(f"EQUIV_{seed}_{geom}", "C_SETUP")
    e, f = precursor(seed, geom)
    st = branch(e, f, legacy_alloc(seed))
    equiv.append({"seed": seed, "geometry": geom, "legacy_alloc": legacy_alloc(seed),
                  "recomputed_full_sha": Z.full_sha(st),
                  "committed_checkpoint_sha": OLDSHA[(seed, geom)],
                  "byte_identical": Z.full_sha(st) == OLDSHA[(seed, geom)]})
    print("  equivalence %d %s alloc=%d -> %s [%.0fs]"
          % (seed, geom, legacy_alloc(seed), equiv[-1]["byte_identical"], time.time() - t0), flush=True)
audit["EXPLICIT_FACTOR_REFACTOR"] = {
    "checks": equiv, "both_parity_branches_covered": True,
    "SEMANTICS_PRESERVING": all(x["byte_identical"] for x in equiv),
    "note": "the refactor only exposes geometry and allocation as explicit arguments. It changes "
            "no equation, history value, duration, state, detector, checkpoint, reader or horizon. "
            "Re-running the two old descendants is an equivalence replay, not a reuse of an "
            "exposed seed in a fresh role."}
assert audit["EXPLICIT_FACTOR_REFACTOR"]["SEMANTICS_PRESERVING"], \
    "EXPLICIT_FACTOR_REFACTOR_NOT_SEMANTICS_PRESERVING"

# =====================================================================================
# 7. CONSTRUCT THE TARGET PANEL, first-eligible in frozen queue order
# =====================================================================================
C_ATTEMPT_MAX = 4
N_ATTEMPT_MAX = (32 - LEDGER["C_SETUP"]) // C_ATTEMPT_MAX
audit["budget"] = {"C_SETUP": LEDGER["C_SETUP"], "C_ATTEMPT_MAX": C_ATTEMPT_MAX,
                   "N_ATTEMPT_MAX": N_ATTEMPT_MAX, "G1_MINIMUM": 4,
                   "sufficient": N_ATTEMPT_MAX >= 4}
assert audit["budget"]["sufficient"], "TARGET_PANEL_CONSTRUCTION_BUDGET_INSUFFICIENT"

blocks, attempts = [], []
for seed in QUEUE:
    if len(blocks) >= 4 or len(attempts) >= N_ATTEMPT_MAX:
        attempts.append({"seed": seed, "status": "NOT_REACHED"})
        continue
    desc, ok = [], True
    for geom in ("FAR", "NEAR"):
        e, f = precursor(seed, geom)
        for alloc in (0, 1):
            start(f"CONSTRUCT_{seed}_{geom}_a{alloc}", "construction")
            st = branch(e, f, alloc)
            masks, meta = Z.t0_masks(st)
            if masks is None:
                desc.append({"seed": seed, "geometry": geom, "alloc": alloc,
                             "status": "REJECTED__NOT_EXACTLY_TWO_ELIGIBLE_COMPONENTS", **meta})
                ok = False
                continue
            MA, MB = masks
            ref = Z.reference_masks(st)
            prod = tuple(sorted((tuple(meta["ids_A"]), tuple(meta["ids_B"]))))
            B = Z.B_of(st, MA, MB)
            did = f"{seed}_{geom}_a{alloc}"
            csha = Z.save(st, f"{CK}/d_{did}.npz")
            np.savez(f"{CK}/m_{did}.npz", MA=MA, MB=MB)
            desc.append({"descendant_id": did, "seed": seed, "geometry": geom, "alloc": alloc,
                         "status": "ADMISSIBLE", "n_A": meta["n_A"], "n_B": meta["n_B"],
                         "mask_sha": meta["mask_sha"], "checkpoint_sha": csha,
                         "B": str(B), "B_positive": B > 0,
                         "production_reference_mask_agreement": bool(ref == prod),
                         "rho_finite": bool(np.isfinite(st.rho).all())})
            if not (B > 0 and ref == prod and np.isfinite(st.rho).all()):
                ok = False
    accepted = ok and all(d["status"] == "ADMISSIBLE" for d in desc) and len(desc) == 4
    attempts.append({"seed": seed, "descendants": desc,
                     "status": "ACCEPTED" if accepted else "BLOCK_REJECTED"})
    if accepted:
        blocks.append({"block_seed": seed, "descendants": desc})
    print("  block %d: %s (%d/4 admissible) [%.0fs]"
          % (seed, attempts[-1]["status"],
             sum(1 for d in desc if d["status"] == "ADMISSIBLE"), time.time() - t0), flush=True)

PANEL_COMPLETE = len(blocks) == 4
assert PANEL_COMPLETE, "INSUFFICIENT_JOINTLY_ELIGIBLE_TARGET_BLOCKS"
DESC = [d for b in blocks for d in b["descendants"]]
assert len(DESC) == 16

# ---- reader/geometry mechanical-confound audit ------------------------------------------
byg = {}
for d in DESC:
    byg.setdefault(d["geometry"], []).append(d)
audit["reader_geometry_confound"] = {
    g: {"support_sizes": sorted(x["n_A"] + x["n_B"] for x in v),
        "B_range": [min(float(Fr(x["B"])) for x in v), max(float(Fr(x["B"])) for x in v)]}
    for g, v in byg.items()}
audit["reader_geometry_confound"]["status"] = (
    "RECORDED_NOT_ADJUDICATED -- this programme makes no geometry claim. The support sizes and "
    "normalizers are logged so a future active programme can test whether a geometry contrast "
    "could be a mechanical reader difference rather than a response difference.")

json.dump(audit, open(f"{OUT}/STATIC_HISTORY_GEOMETRY_ROUTE_AUDIT.json", "w"), indent=1, default=str)
json.dump({"namespace_queue": QUEUE, "attempts": attempts,
           "accepted_blocks": [b["block_seed"] for b in blocks],
           "ancestry_graph": {str(b["block_seed"]): [d["descendant_id"] for d in b["descendants"]]
                              for b in blocks},
           "independent_ancestry_blocks": len(blocks),
           "descendants": len(DESC),
           "independent_unit_note": "4 upstream ancestry blocks. 16 descendants, 2 sham twins each "
                                    "and 2 future carrier sentinels each are repeated conditions, "
                                    "never replications.",
           "excluded_namespaces": {"62000-62009": "RESERVED_AND_UNREAD",
                                   "61000-61009 / 63xxx / 64000-64011": "EXPOSED_OR_RESERVED"}},
          open(f"{OUT}/TARGET_PANEL_QUEUE_AND_ANCESTRY_GRAPH.json", "w"), indent=1)

# =====================================================================================
# PANEL LOCK -- written BEFORE the first sham
# =====================================================================================
CARRIER_LOCK = {
    "FUTURE_ACTIVE_EXECUTION_AUTHORIZED_IN_WL2SMF00": False,
    "CARRIER_1": {"superfamily": "CONSERVATIVE_CARRIER_REDISTRIBUTION",
                  "instance": "matched_transposition",
                  "callable": "etcmnfc_core.transpose(st, I, J)",
                  "code_sha256": sha("/home/claude/sweep/ETCMNFC/etcmnfc_core.py"),
                  "application_time": "the exact descendant checkpoint t0",
                  "declared_touch_set": ["Mf"], "dose": "none (a permutation)"},
    "CARRIER_2": {"superfamily": "NONCONSERVATIVE_CARRIER_TRANSFORMATION",
                  "instance": "intensive_reflection", "callable": "ppai_core.state_cross(st)",
                  "code_sha256": sha("/home/claude/sweep/PPAI/ppai_core.py"),
                  "application_time": "the exact descendant checkpoint t0",
                  "declared_touch_set": ["Mf"], "dose": "none (a reflection)"},
    "proof_neither_arm_changes_the_reader_or_the_sham":
        "both operate on Mf only and never receive the masks, the normalizer or the scored times; "
        "the reader q_channels depends on rho and the immutable masks alone. The sham is the "
        "identity copy in both cases, so the two future sentinels share the SAME canonical sham.",
    "bound_here_only_to_prevent_arm_shopping_after_thresholds_are_known": True,
}
json.dump(CARRIER_LOCK, open(f"{OUT}/FUTURE_ACTIVE_CARRIER_ARM_LOCK.json", "w"), indent=1)

PANEL_LOCK = {
    "blocks": [b["block_seed"] for b in blocks],
    "descendants": [{k: d[k] for k in ("descendant_id", "seed", "geometry", "alloc", "n_A", "n_B",
                                       "mask_sha", "checkpoint_sha", "B")} for d in DESC],
    "independent_ancestry_blocks": 4, "route": "G1", "history_route": "H3",
    "design_matrix": "seed x {FAR,NEAR} x {alloc 0, alloc 1}; full rank by construction, "
                     "geometry and allocation are independent explicit arguments and neither is "
                     "derived from a seed bit",
    "SHAM_0": "canonical baseline continuation, frozen by serializer order BEFORE either sham runs",
    "SHAM_1": "byte-identical-input twin, identity oracle only; never averaged, never chosen",
    "reader": {"module": "WSFSCRP00/wsfscrp_core.py",
               "sha256": sha("/home/claude/sweep/WSFSCRP00/wsfscrp_core.py"),
               "H_GRID": Z.H_GRID, "weights": [str(w) for w in Z.W],
               "normalizer": "B_of = dsum(rho[MA|MB]), exact rational"},
    "reference_reader": {"module": "WL2SMF00/wl2_ref.py", "sha256": sha(f"{OUT}/wl2_ref.py")},
    "production_pipeline": {"module": "WL2SMF00/wl2_prod.py", "sha256": sha(f"{OUT}/wl2_prod.py")},
    "threshold_formulas": "see WL2SMF00_MASTER_FREEZE.md sections 1-4; all frozen before this lock",
    "alpha_map_G1": "1/4 per block, 1/4 per descendant, 1/2 per sentinel = 1/32 per future row",
    "engine_start_matrix": {"C_SETUP": LEDGER["C_SETUP"], "construction": LEDGER["construction"],
                            "cap": 32, "sham_expected": 32, "total_cap": 64},
    "stop_precedence": "as frozen in the master freeze",
    "future_carrier_arm_lock_sha256": sha(f"{OUT}/FUTURE_ACTIVE_CARRIER_ARM_LOCK.json"),
    "master_freeze_sha256": sha(f"{OUT}/WL2SMF00_MASTER_FREEZE.md"),
}
json.dump(PANEL_LOCK, open(f"{OUT}/WL2SMF00_PANEL_LOCK.json", "w"), indent=1)
json.dump(LEDGER, open(f"{OUT}/TARGET_PANEL_CONSTRUCTION_AND_START_LEDGER.json", "w"), indent=1)
print("\nroute G1 / H3 | blocks accepted:", [b["block_seed"] for b in blocks],
      "| descendants:", len(DESC))
print("starts: C_SETUP=%d construction=%d (cap 32) | raw advance sequences=%d"
      % (LEDGER["C_SETUP"], LEDGER["construction"], LEDGER["raw_advance_sequences"]))
print("PANEL LOCK sha:", sha(f"{OUT}/WL2SMF00_PANEL_LOCK.json")[:16])
