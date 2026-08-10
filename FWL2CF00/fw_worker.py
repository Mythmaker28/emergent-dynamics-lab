"""FWL2CF00 acquisition worker. ONE continuation per fresh process.

Write-only with respect to science: it serialises and hashes raw bytes. It never computes, prints,
ranks or opens M2, TAU, quotient, transfer or factor scores. Usage:

    python3 fw_worker.py <ckpt.npz> <mask.npz> <OP> <out.npz> <expected_ckpt_sha> <expected_callable>
"""
from __future__ import annotations
import sys, os, json, hashlib
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/PPAI")
sys.path.insert(0, "/home/claude/sweep/ETPC")
sys.path.insert(0, "/home/claude/sweep/ETCMNFC")
sys.path.insert(0, "/home/claude/sweep/WSFSCRP00")
import numpy as np
import wsfscrp_core as Z

CKPT, MASK, OP, OUTP, EXP_SHA, EXPECT_CALLABLE = sys.argv[1:7]
assert not os.path.exists(OUTP), "output path already exists; overwrite mode is forbidden"

st0 = Z.load(CKPT)
src_sha = Z.full_sha(st0)
assert src_sha == EXP_SHA, "input checkpoint hash mismatch"
mk = np.load(MASK)
MA, MB = mk["MA"], mk["MB"]
mask_sha = hashlib.sha256(MA.tobytes() + MB.tobytes()).hexdigest()
B = Z.B_of(st0, MA, MB)

# ---- resolve the operator by an explicit allowlist. No getattr dispatch, no eval, no
# ---- string-to-call resolution. Exactly one call site per branch.
if OP == "SHAM":
    EXPECT = "identity_copy"
    def op(s):
        return s.copy()
    touch_expected = []
elif OP == "CARRIER_1":
    import etcmnfc_core as EC
    EXPECT = "etcmnfc_core.transpose(st, I, J)"
    mem = {"A": np.nonzero(MA), "B": np.nonzero(MB)}
    ok = EC.eligible_edges(st0, mem)
    ida = np.asarray(mem["A"][0]) * Z.L + np.asarray(mem["A"][1])
    idb = np.asarray(mem["B"][0]) * Z.L + np.asarray(mem["B"][1])
    M, pairs = EC.frozen_matching(ok, ida, idb)
    I = [(int(mem["A"][0][i]), int(mem["A"][1][i])) for (_, _, i, j) in pairs]
    J = [(int(mem["B"][0][j]), int(mem["B"][1][j])) for (_, _, i, j) in pairs]
    def op(s):
        return EC.transpose(s, I, J)
    touch_expected = ["Mf"]
elif OP == "CARRIER_2":
    import ppai_core as PC
    EXPECT = "ppai_core.state_cross(st)"
    def op(s):
        return PC.state_cross(s)
    touch_expected = ["Mf"]
else:
    raise SystemExit("unknown operator")
assert EXPECT == EXPECT_CALLABLE, "operator identity guard failed"

# ---- touch-set / domain guard at t0, before any step -------------------------------------
pre, post = st0.copy(), op(st0.copy())
touched = sorted({f for f in Z.FIELDS
                  if not np.array_equal(
                      np.ascontiguousarray(np.asarray(getattr(pre, f))).tobytes(),
                      np.ascontiguousarray(np.asarray(getattr(post, f))).tobytes())})
rho_untouched = np.array_equal(np.ascontiguousarray(pre.rho).tobytes(),
                               np.ascontiguousarray(post.rho).tobytes())

# ---- run, persisting the raw rho at t0 and at every scored time ----------------------------
e = Z.engine()
cur = op(st0.copy())
rho_series = [np.ascontiguousarray(cur.rho).copy()]
state_sha = [Z.full_sha(cur)]
for t in range(1, max(Z.H_GRID) + 1):
    cur = e.step(cur)
    if t in Z.H_GRID:
        rho_series.append(np.ascontiguousarray(cur.rho).copy())
        state_sha.append(Z.full_sha(cur))
end_sha = Z.full_sha(cur)
src_after = Z.full_sha(st0)

np.savez_compressed(OUTP, rho=np.stack(rho_series), MA=MA, MB=MB)
meta = {"op": OP, "expected_callable": EXPECT, "checkpoint": os.path.basename(CKPT),
        "input_sha_before": src_sha, "input_sha_after": src_after,
        "input_unchanged": src_sha == src_after,
        "mask_sha": mask_sha, "B_exact": str(B),
        "touched_fields_at_t0": touched, "touch_expected": touch_expected,
        "touch_set_ok": touched == touch_expected,
        "rho_untouched_at_t0": bool(rho_untouched),
        "scored_times": [0] + list(Z.H_GRID),
        "n_frames": len(rho_series),
        "per_time_state_sha": state_sha, "terminal_state_sha": end_sha,
        "rho_finite": bool(all(np.isfinite(r).all() for r in rho_series)),
        "output_sha256": hashlib.sha256(open(OUTP, "rb").read()).hexdigest()}
open(OUTP + ".meta.json", "w").write(json.dumps(meta, indent=1))
print(json.dumps({"ok": True, "out": OUTP, "sha": meta["output_sha256"],
                  "terminal": end_sha, "touch": touched}))
