"""FMRCT01 §12 — runtime verification that every imported load-bearing module matches the freeze.
Called at the start of every runner process. A mismatch is a technical fault, not a scientific one."""
from __future__ import annotations
import hashlib, json, os, sys
REPO="/home/claude/edl"; OUT=f"{REPO}/FMRCT01/out"
def _h(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
def verify(strict=True):
    MF=json.load(open(f"{OUT}/FMRCT01_MASTER_FREEZE.json"))
    frozen={m["path"]:m["sha256"] for m in MF["METHODS_MANIFEST"]}
    byhash=set(frozen.values())
    bad=[]; checked=0
    for p,h in frozen.items():
        f=os.path.join(REPO,p)
        if not os.path.exists(f): bad.append(("MISSING",p,h,None)); continue
        g=_h(f); checked+=1
        if g!=h: bad.append(("MISMATCH",p,h,g))
    # every module actually loaded from disk must be one of the frozen byte sequences
    loaded=[]
    for name,mod in list(sys.modules.items()):
        f=getattr(mod,"__file__",None)
        if not f or not f.endswith(".py"): continue
        if not (f.startswith(REPO) or f.startswith("/home/claude/ORR01") or
                f.startswith("/home/claude/OBTC02")): continue
        g=_h(f); loaded.append((name,f,g))
        if g not in byhash: bad.append(("LOADED_NOT_IN_FREEZE",name,f,g))
    if bad and strict:
        raise RuntimeError("FMRCT01 runtime methods verification failed: %s"%json.dumps(bad)[:800])
    return {"frozen_files":len(frozen),"checked":checked,"loaded_project_modules":len(loaded),"bad":bad}
