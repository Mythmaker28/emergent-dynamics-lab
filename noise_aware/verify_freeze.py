"""Freeze verification: recompute sha256 of every frozen file and compare to the freeze manifest.
Exit nonzero on any mismatch. Used by CI and before any prospective run."""
import json, hashlib, sys, os
man=json.load(open(os.path.join(os.path.dirname(__file__),"..","docs","noise_aware","NASI_FREEZE_MANIFEST.json")))
bad=0
for f,h in man["frozen_files"].items():
    p=os.path.join(os.path.dirname(__file__),"..",f)
    got=hashlib.sha256(open(p,"rb").read()).hexdigest()
    ok=(got==h); bad+=(not ok)
    print(("OK  " if ok else "FAIL")+f" {f} {got[:16]}")
print("FREEZE VERIFY:", "PASS" if bad==0 else f"FAIL ({bad})")
sys.exit(1 if bad else 0)
