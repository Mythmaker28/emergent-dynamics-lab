"""FWL2CF00 -- INDEPENDENT disk readback. A separate process that receives only archive paths,
expected hashes and frozen reader inputs. It rebuilds the reader series from the persisted raw rho
bytes; it never trusts a just-written X_A/X_B value. Zero engine starts."""
from __future__ import annotations
import json, hashlib, os, sys
from fractions import Fraction as Fr
import numpy as np
OUT = "/home/claude/sweep/FWL2CF00"
sys.path.insert(0, OUT)
import fw_prod as P
import fw_ref as R
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
KIND = sys.argv[1]                     # "sham" or "active"
LOCK = json.load(open(f"{OUT}/FWL2CF00_SHAM_RECONSTRUCTION_LOCK.json"))
BIND = json.load(open(f"{OUT}/PARENT_LOCK_AND_ARM_BINDING_MANIFEST.json"))
DIR = f"{OUT}/{KIND}"
rows, series = [], {}
for f in sorted(os.listdir(DIR)):
    if not f.endswith(".npz"):
        continue
    tag = f[:-4]
    meta = json.load(open(f"{DIR}/{f}.meta.json"))
    d = np.load(f"{DIR}/{f}")
    rho, MA, MB = d["rho"], d["MA"], d["MB"]
    did = tag.split("|")[0] if "|" in tag else tag
    lk = LOCK["descendants"][did] if did in LOCK["descendants"] else None
    fa = [bool(x) for x in np.asarray(MA).ravel()]
    fb = [bool(x) for x in np.asarray(MB).ravel()]
    XA, XB, XAr, XBr = [], [], [], []
    Bp = None
    for k in range(rho.shape[0]):
        flat = [float(x) for x in np.asarray(rho[k]).ravel()]
        if k == 0:
            Bp = P.exact_sum([flat[i] for i in range(len(flat)) if fa[i] or fb[i]])
        a, b = P.X_channels(flat, fa, fb, Bp)
        ar, br = R.X_channels(flat, fa, fb, Bp)
        XA.append(a); XB.append(b); XAr.append(ar); XBr.append(br)
    ok_file = sha(f"{DIR}/{f}") == meta["output_sha256"]
    rec = {"tag": tag, "descendant": did, "op": meta["op"],
           "file_sha_matches_meta": ok_file,
           "n_frames": int(rho.shape[0]), "expected_frames": 11,
           "production_equals_reference": XA == XAr and XB == XBr,
           "B_from_disk_equals_meta": str(Bp) == meta["B_exact"],
           "mask_sha_matches": hashlib.sha256(MA.tobytes() + MB.tobytes()).hexdigest() == meta["mask_sha"],
           "input_unchanged": meta["input_unchanged"],
           "touch_set_ok": meta["touch_set_ok"], "rho_finite": meta["rho_finite"],
           "terminal_state_sha": meta["terminal_state_sha"]}
    if lk:
        rec["B_equals_locked"] = str(Bp) == lk["B_exact"]
        sel = np.asarray(MA | MB).ravel()
        supp = [float(x) for i, x in enumerate(np.asarray(rho[0]).ravel()) if sel[i]]
        med = P.exact_median(supp) if hasattr(P, "exact_median") else None
        if med is None:
            s = sorted(Fr(float(x)) for x in supp)
            m = len(s)
            med = s[m // 2] if m % 2 else (s[m // 2 - 1] + s[m // 2]) / 2
        rec["RHO_MED_equals_locked"] = (str(med) == lk["RHO_MED_exact"])
    rows.append(rec)
    series[tag] = {"XA": [str(x) for x in XA], "XB": [str(x) for x in XB],
                   "terminal_state_sha": meta["terminal_state_sha"], "op": meta["op"],
                   "B": str(Bp), "descendant": did}
json.dump({"kind": KIND, "rows": rows, "n": len(rows),
           "all_pass": all(all(v for k, v in r.items() if isinstance(v, bool)) for r in rows)},
          open(f"{OUT}/{KIND.upper()}_DISK_READBACK_CERTIFICATE.json", "w"), indent=1)
json.dump(series, open(f"{OUT}/{KIND}_series.json", "w"), indent=1)
print(KIND, "readback:", len(rows), "archives | all_pass:",
      all(all(v for k, v in r.items() if isinstance(v, bool)) for r in rows))
