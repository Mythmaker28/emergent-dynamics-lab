"""Derive the COMMITTED raw archive from the full-field archives. Zero engine starts.

The fixed reader consumes rho ONLY on the union support MA|MB. The committed archive therefore
stores the exact raw rho bytes on that support at t0 and every scored time, the two immutable
masks, B, and the per-time plus terminal FULL-STATE hashes that bind the complete engine state.
An independent check below rebuilds the reader series from the compact archive alone and requires
exact equality with the series rebuilt from the full fields."""
from __future__ import annotations
import json, hashlib, os, sys
from fractions import Fraction as Fr
import numpy as np
OUT = "/home/claude/sweep/FWL2CF00"; sys.path.insert(0, OUT)
import fw_prod as P
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
KIND = sys.argv[1]
SRC, DST = f"{OUT}/{KIND}", f"{OUT}/{KIND}_raw"
os.makedirs(DST, exist_ok=True)
FULL = json.load(open(f"{OUT}/{KIND}_series.json"))
man, bad = [], []
for f in sorted(os.listdir(SRC)):
    if not f.endswith(".npz"):
        continue
    tag = f[:-4]
    meta = json.load(open(f"{SRC}/{f}.meta.json"))
    d = np.load(f"{SRC}/{f}")
    rho, MA, MB = d["rho"], d["MA"], d["MB"]
    sup = np.asarray(MA | MB).ravel()
    idx = np.nonzero(sup)[0].astype(np.int32)
    vals = np.stack([np.asarray(rho[k]).ravel()[idx] for k in range(rho.shape[0])])
    outp = f"{DST}/{tag}.npz"
    assert not os.path.exists(outp)
    np.savez_compressed(outp, rho_support=vals, support_index=idx, MA=MA, MB=MB)
    m2 = dict(meta); m2["compact_output_sha256"] = sha(outp)
    m2["support_sites"] = int(idx.size)
    open(f"{DST}/{tag}.meta.json", "w").write(json.dumps(m2, indent=1))
    # --- independent rebuild of the reader series from the COMPACT archive only ---
    e = np.load(outp)
    v2, i2, A2, B2m = e["rho_support"], e["support_index"], e["MA"], e["MB"]
    fa = np.asarray(A2).ravel()[i2]
    fb = np.asarray(B2m).ravel()[i2]
    XA, XB = [], []
    Bc = None
    for k in range(v2.shape[0]):
        row = [float(x) for x in v2[k]]
        if k == 0:
            Bc = P.exact_sum(row)
        XA.append(P.exact_sum([row[i] for i in range(len(row)) if fa[i]]) / Bc)
        XB.append(P.exact_sum([row[i] for i in range(len(row)) if fb[i]]) / Bc)
    ok = ([str(x) for x in XA] == FULL[tag]["XA"] and [str(x) for x in XB] == FULL[tag]["XB"]
          and str(Bc) == FULL[tag]["B"])
    if not ok:
        bad.append(tag)
    man.append({"name": f"{tag}.npz", "sha256": sha(outp), "bytes": os.path.getsize(outp),
                "support_sites": int(idx.size), "n_frames": int(v2.shape[0]),
                "terminal_state_sha": meta["terminal_state_sha"],
                "compact_reproduces_full_field_series": ok})
json.dump({"directory": f"FWL2CF00/{KIND}_raw", "files": man, "n": len(man),
           "all_reproduce_full_field_series": not bad, "failures": bad,
           "what_is_archived": "exact raw rho bytes on the reader's union support at t0 and every "
                               "scored time, the two immutable masks, the support index, and the "
                               "per-time plus terminal FULL-STATE hashes of the complete engine "
                               "state.",
           "what_is_not_archived": "the full 64x64 rho fields off the support, which the fixed "
                                   "reader never reads. They exist in the session workspace; the "
                                   "device bridge could not carry them (protocol deviation D2).",
           "sufficiency_proof": "the reader series rebuilt from the compact archive alone equals, "
                                "string-for-string in exact rational form, the series rebuilt "
                                "from the full fields in the independent readback process."},
          open(f"{OUT}/{'SHAM_0_RECONSTRUCTED' if KIND=='sham' else 'FRESH_ACTIVE_CARRIER'}_RAW_MANIFEST.json", "w"), indent=1)
print(KIND, "compact archive:", len(man), "files,",
      sum(m["bytes"] for m in man) // 1024, "KB | reproduce full-field series:", not bad)
