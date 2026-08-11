"""FCDDH00 G1 construction worker. ONE descendant per fresh process.

Usage:
    python3 -B fh_cworker.py <upstream_seed> <geometry> <allocation> <out_ckpt.npz>
                             <out_mask.npz> --ack <ack> --advance <adv>

It runs the ALREADY-COMMITTED explicit form of the inherited constructor, unchanged:

    domc_core.set_geometry(g)                       # explicit geometry argument
    e  = wsfscrp_core.engine()
    f0 = domc_core.found(S)                         # PRECURSOR(S) x _blob(g); ZERO advances
    f  = domc_core.advance(e, f0, domc_core.T_FOUND)
    hA, hB = (HIST_H, HIST_L) if a == 0 else (HIST_L, HIST_H)
    st = domc_core.advance(e, domc_core.apply_dual_history(e, f, hA, hB), domc_core.SETTLE)

The only change relative to FSQBT00 is that the upstream seed S is COMMON to the four cells of a
block and (g, a) are crossed within S, instead of (g, a) being selected by S mod 4.

It writes no score, no threshold, no response and no decoded label. It reports only structural
admissibility metadata and hashes.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

ARGV = list(sys.argv)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fh_runner                                                   # noqa: E402

fh_runner.child_ack(ARGV)                                          # FIRST action, pre-engine

for _p in ("/home/claude/sweep", "/home/claude/sweep/DOMC", "/home/claude/sweep/PPAI",
           "/home/claude/sweep/ETPC", "/home/claude/sweep/ETCMNFC",
           "/home/claude/sweep/WSFSCRP00"):
    sys.path.insert(0, _p)

import numpy as np                                                 # noqa: E402
import domc_core as K                                              # noqa: E402
import ppai_core as P                                              # noqa: E402
import wsfscrp_core as Z                                           # noqa: E402
from edlab.experiments.sc_mcm import config as C                   # noqa: E402

SEED = int(ARGV[1])
GEOM = ARGV[2]
ALLOC = int(ARGV[3])
OUT_CK = ARGV[4]
OUT_MK = ARGV[5]
assert GEOM in ("NEAR", "FAR")
assert ALLOC in (0, 1)
assert not os.path.exists(OUT_CK), "overwrite mode is forbidden"
assert not os.path.exists(OUT_MK), "overwrite mode is forbidden"

FIELDS_SC = ("rho", "U", "V", "c", "N", "C", "uptake", "step")


def _hash_state(obj):
    """Explicit field list, no getattr dispatch, no vars(), no string-to-attribute resolution."""
    items = [("rho", obj.rho), ("U", obj.U), ("V", obj.V), ("c", obj.c),
             ("N", obj.N), ("C", obj.C), ("uptake", obj.uptake), ("step", obj.step)]
    h = hashlib.sha256()
    for k, v in items:
        a = np.ascontiguousarray(v) if isinstance(v, np.ndarray) else np.array([v])
        h.update(k.encode())
        h.update(str(a.shape).encode())
        h.update(str(a.dtype.str).encode())
        h.update(a.tobytes(order="C"))
    return h.hexdigest()


# ---- the common upstream precursor: a PURE function of the seed, ZERO engine advances --------
precursor = C.seed_state(C.SPEC, C.TRACER, SEED, "random")
precursor_sha = _hash_state(precursor)

# ---- geometry set by the explicit argument, applied to that identical precursor ---------------
K.set_geometry(GEOM)
f0 = K.found(SEED)                                   # zero advances
blob = K._blob()                                     # the explicit geometry mask
g1_mask_ok = bool(
    np.array_equal(np.ascontiguousarray(f0.rho), np.ascontiguousarray(precursor.rho * blob))
    and np.array_equal(np.ascontiguousarray(f0.U), np.ascontiguousarray(precursor.U * blob))
    and np.array_equal(np.ascontiguousarray(f0.V), np.ascontiguousarray(precursor.V * blob))
    and np.array_equal(np.ascontiguousarray(f0.c), np.ascontiguousarray(precursor.c))
    and np.array_equal(np.ascontiguousarray(f0.N), np.ascontiguousarray(precursor.N))
    and np.array_equal(np.ascontiguousarray(f0.C), np.ascontiguousarray(precursor.C * blob)))
blob_sha = hashlib.sha256(np.ascontiguousarray(blob).tobytes()).hexdigest()

hA, hB = (P.HIST_H, P.HIST_L) if ALLOC == 0 else (P.HIST_L, P.HIST_H)
forcing_trace = K.global_forcing_trace(hA, hB)
forcing_sha = hashlib.sha256(json.dumps(forcing_trace).encode()).hexdigest()

e = Z.engine()                                       # instantiated, not yet advanced
fh_runner.child_advance(ARGV, "about to advance T_FOUND=%d for %d_%s_a%d" % (K.T_FOUND, SEED, GEOM, ALLOC))

f = K.advance(e, f0, K.T_FOUND)
st = K.advance(e, K.apply_dual_history(e, f, hA, hB), K.SETTLE)

# ---- pre-outcome, response-blind admissibility (unchanged inherited rule) ---------------------
masks, meta = Z.t0_masks(st)
if masks is None:
    print(json.dumps({"ok": True, "accepted": False,
                      "reason": "REJECTED__NOT_EXACTLY_TWO_ELIGIBLE",
                      "seed": SEED, "geometry": GEOM, "allocation": ALLOC,
                      "precursor_sha256": precursor_sha, "blob_sha256": blob_sha,
                      "g1_precursor_mask_identity": g1_mask_ok,
                      "forcing_trace_sha256": forcing_sha,
                      "n_eligible": meta.get("n_eligible"), "sizes": meta.get("sizes")}))
    raise SystemExit(0)

MA, MB = masks
ref = Z.reference_masks(st)
prod = tuple(sorted((tuple(meta["ids_A"]), tuple(meta["ids_B"]))))
agree = bool(ref == prod)
B = Z.B_of(st, MA, MB)
finite = bool(np.isfinite(st.rho).all())
accepted = bool(B > 0 and agree and finite and g1_mask_ok)

ck_sha = Z.save(st, OUT_CK)
np.savez(OUT_MK, MA=MA, MB=MB)
fsha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()

print(json.dumps({
    "ok": True, "accepted": accepted,
    "reason": "ACCEPTED" if accepted else "REJECTED__ADMISSIBILITY",
    "seed": SEED, "geometry": GEOM, "allocation": ALLOC,
    "precursor_sha256": precursor_sha, "blob_sha256": blob_sha,
    "g1_precursor_mask_identity": g1_mask_ok,
    "forcing_trace_sha256": forcing_sha,
    "checkpoint_state_sha": ck_sha, "mask_sha": meta["mask_sha"],
    "n_A": int(meta["n_A"]), "n_B": int(meta["n_B"]),
    "B_exact": str(B), "B_positive": bool(B > 0),
    "production_reference_mask_agreement": agree, "rho_finite": finite,
    "checkpoint_file_sha256": fsha(OUT_CK), "mask_file_sha256": fsha(OUT_MK),
    "engine_steps": int(K.T_FOUND + 2 * 60 + K.SETTLE),
}))
