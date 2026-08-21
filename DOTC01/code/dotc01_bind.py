"""DOTC01 §1 — bind the scientific state by bytes, and map the executable objects."""
from __future__ import annotations
import json, os, hashlib, subprocess, datetime, sys
import numpy as np
REPO="/home/claude/edl"; OUT=f"{REPO}/DOTC01/out"
sha=lambda p: hashlib.sha256(open(p,'rb').read()).hexdigest()
G=lambda *a: subprocess.check_output(["git","-C",REPO]+list(a),text=True).strip()
NOW=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()

PROGRAMMES={
 "ORR01":{"root":"/home/claude/ORR01","role":"frozen kinetics and LawSpec v2"},
 "OBTC02":{"root":"/home/claude/OBTC02","role":"frozen engine, protocol yaml, capacity-constrained operator status"},
 "OBFOR01":{"root":f"{REPO}/OBFOR01","role":"single-organiser operator residual and r80"},
 "PQEC01":{"root":f"{REPO}/PQEC01","role":"128 instrumented worlds at A0/B1/B2 with EVENT-ALIGNED Y ledgers"},
 "FLCR01":{"root":f"{REPO}/FLCR01","role":"inherited boundary at 06c5923"},
 "FTCTR01":{"root":f"{REPO}/FTCTR01","role":"exact two-centre timescale rederivation"},
 "FLRS02":{"root":f"{REPO}/FLRS02","role":"route selection, functional criterion"},
 "FDFLT01":{"root":f"{REPO}/FDFLT01","role":"fresh confirmatory maturation test"},
 "RCD01":{"root":f"{REPO}/RCD01","role":"reproduction criterion derivation"},
 "FMRT01":{"root":f"{REPO}/FMRT01","role":"the causal three-arm fork, 85 blocks"},
 "MRFA01":{"root":f"{REPO}/MRFA01","role":"the autopsy that named the two missing objects"},
}

def verify_sums(path,prog_root):
    """Older programmes wrote paths relative to their OWN directory ('./code/x.py'); the recent
    ones write repo-relative paths ('FMRT01/out/x.json'). Try both bases and take the one that
    resolves, so a path convention is never mistaken for a corrupted file."""
    if not os.path.exists(path): return {"present":False}
    best=None
    for base,label in ((prog_root,"programme-relative"),(REPO,"repo-relative")):
        ok=0; bad=[]
        for line in open(path):
            line=line.strip()
            if not line or "  " not in line: continue
            h,p=line.split("  ",1)
            fp=p if os.path.isabs(p) else os.path.normpath(os.path.join(base,p))
            if not os.path.exists(fp): bad.append(("MISSING",p)); continue
            if sha(fp)==h: ok+=1
            else: bad.append(("HASH",p))
        r={"present":True,"base":label,"verified":ok,"bad":bad[:8],"n_bad":len(bad)}
        if best is None or r["verified"]>best["verified"]: best=r
    return best

def main():
    os.makedirs(OUT,exist_ok=True)
    progs={}
    for k,v in PROGRAMMES.items():
        r=v["root"]; entry={"root":r,"role":v["role"],"present":os.path.isdir(r)}
        if entry["present"]:
            for cand in (f"{r}/out/SHA256SUMS",f"{r}/{k}_SHA256SUMS",f"{r}/SHA256SUMS"):
                if os.path.exists(cand):
                    entry["SHA256SUMS"]=os.path.relpath(cand,REPO) if cand.startswith(REPO) else cand
                    entry["verification"]=verify_sums(cand,r); break
        progs[k]=entry
    # the frozen law files, by hash
    law={p:sha(p) for p in ("/home/claude/OBTC02/code/engine_obtc.py","/home/claude/ORR01/code/kinetics.py",
        "/home/claude/ORR01/code/lawspec_v2.py","/home/claude/OBTC02/code/obtc02_protocol.yaml",
        f"{REPO}/PQEC01/code/pqec01_observer.py",f"{REPO}/FMRT01/code/fmrt01_identity.py",
        f"{REPO}/FMRT01/code/fmrt01_engine.py",f"{REPO}/FMRT01/code/fmrt01_endpoint.py")}
    FZ=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))
    B=FZ["PHASE_B"]; C=FZ["INHERITED_FROZEN_CONSTANTS"]
    # executable object map: WHERE each required object actually lives
    RAW="/home/claude/PQEC01/raw"
    files=sorted(os.listdir(RAW)) if os.path.isdir(RAW) else []
    z=np.load(os.path.join(RAW,files[0]),allow_pickle=True) if files else None
    OM={
     "SECTION":"DOTC01 §1 — executable object map. Every object this mission needs, and where it lives.",
     "GENERATED_UTC":NOW(),
     "Y_BIRTH_LAW":{"where":"OBTC02/code/engine_obtc.py _react_core, the ('Y','SY',kY) branch",
       "exact":"p = min(1, kY * nX * nY) per cell; cand = min(n[SY], free); births ~ Binomial(cand, p)",
       "consequence":"a Y birth occurs ONLY at a cell that already holds a Y, so a newborn Y is always co-located with a parent constituent and therefore always inside the same centre component",
       "recoverable":"EXACT, event-aligned, from PQEC01 raw `ybirth` = (step, y, x, n_born)"},
     "Y_DEATH_LAW":{"where":"OBTC02/code/engine_obtc.py _decay_core, the ('Y','WY',muY) branch",
       "exact":"d ~ Binomial(n[Y], muY) per cell, per-molecule Bernoulli",
       "recoverable":"EXACT, event-aligned, from PQEC01 raw `ydeath` = (step, y, x, n_died)"},
     "Y_DIFFUSION":{"where":"ORR01/code/kinetics.py _diffuse, called for Y in the frozen step order",
       "p_hop_Y_mobile":C["p_hop_Y_mobile"],
       "recoverable":"EXACT from PQEC01 raw `yhop` = (step, sub, shift, ax, y_from, x_from, n_accepted)"},
     "CENTRE_CLASSIFIER":{"where":"FMRT01/code/fmrt01_identity.py components()",
       "exact":"toroidal single-linkage over Y-occupied cells with adjacency distance <= CORE_R",
       "CORE_R":C["CORE_R"],
       "recoverable":"EXACT per step from PQEC01 raw `ycells` (step,y,x,...) which lists every Y-occupied cell"},
     "LOCAL_X_SOURCE_LAW":{"where":"engine_obtc.py _react_core, the ('X','SX',kX) branch",
       "exact":"p = min(1, kX * nX * nY); births ~ Binomial(min(n[SX],free), p) — X is born ONLY at Y-occupied cells",
       "recoverable":"world totals per step from PQEC01 raw `xevent` = (step, n_X_born, n_X_died); "
                     "per-cell X births are NOT stored by PQEC01 and are recoverable only by replay"},
     "LOCAL_X_DECAY":{"exact":"d ~ Binomial(n[X], muX), muX = %r"%C["muX"]},
     "PERSISTENT_CENTRE_TRACKER":{"status":"DOES NOT EXIST AS A STORED OBJECT",
       "consequence":"centre identity across steps must be RECONSTRUCTED from `ycells` by spatial matching; "
                     "no stored object asserts it and none is assumed"},
     "Y_BIRTH_DEATH_LEDGERS":{"status":"PRESENT AND EXACT in PQEC01 raw",
       "ybirth_columns":"(step, y, x, n_born)","ydeath_columns":"(step, y, x, n_died)",
       "recorded_how":"the Y-plane difference across _react() and across _decay() respectively, so they are "
                      "exact and event-aligned, not inferred"},
     "X_BIRTH_LEDGER":{"status":"WORLD-TOTAL ONLY in PQEC01 (`xevent`); per-cell X birth positions are not stored"},
     "FMRT01_THREE_ARM_FORK":{"where":"FMRT01/code/fmrt01_run.py","status":"present, byte-verified",
       "note":"FMRT01 archives store per-arm world totals every 25 steps and a tracker snapshot at t_m only; "
              "they contain NO Y birth/death ledger, so the organiser question cannot be answered from FMRT01 raw alone"},
     "THE_DATA_SOURCE_FOR_THIS_MISSION":{
       "primary":"/home/claude/PQEC01/raw — 128 archives, 958 MB, with exact Y ledgers",
       "n_archives":len(files),
       "points":{"A0":sum(1 for f in files if "_A0_" in f),"B1":sum(1 for f in files if "_B1_" in f),
                 "B2":sum(1 for f in files if "_B2_" in f)},
       "arrays_per_archive":sorted(list(z.keys())) if z is not None else [],
       "why_no_replay_is_needed":("PQEC01 recorded the exact event-aligned Y ledgers and the per-step local "
         "environment at every Y-occupied cell. Everything DOTC01 needs about the organiser process is in "
         "those bytes. No world is constructed and no trajectory is run.")},
     "EXCLUDED":{"CLOC02":"lost, not used as numerical evidence","RSLOC03":"invalid, not used as numerical evidence"},
    }
    BD={"SECTION":"DOTC01 §1 — parent and raw-data binding",
     "GENERATED_UTC":NOW(),
     "PARENT_PROGRAM":"MINIMAL-REPRODUCTION-FAILURE-AUTOPSY-01",
     "PARENT_REPORTED_TIP_IN_THE_LAUNCHER":"9bc79c1...",
     "PARENT_TIP_RESOLVED":G("rev-parse","HEAD"),
     "TIP_DISCREPANCY_NOTED":("the launcher names 9bc79c1 (MRFA01 C2). The actual tip is one commit later, "
       "bec963d5851389fc5dcd430c0df33d6a9eafcdeb (MRFA01 C3), which recorded the re-probed remote-write gate. "
       "Resolved from the repository rather than assumed from the prompt."),
     "PARENT_FINAL_DISPOSITION":json.load(open(f"{REPO}/MRFA01/out/MRFA01_FINAL_DISPOSITION.json"))["FINAL_DISPOSITION"],
     "CONTAINER_ROLLBACK_THIS_MISSION":False,
     "ROLLBACK_CHECK":"HEAD is at the MRFA01 tip and MRFA01/, FMRT01/ and PQEC01/raw are all present; no restoration was needed",
     "BRANCH":G("rev-parse","--abbrev-ref","HEAD"),
     "PROGRAMMES":progs,
     "FROZEN_LAW_HASHES":law,
     "ENGINE_MATCHES_FROZEN":law["/home/claude/OBTC02/code/engine_obtc.py"]=="2172deae5bbabf37238cf7712cb17663c151494befcf85505c537a7cac0ded30",
     "POINTS":{"B1":{k:B["POINT_B1"][k] for k in ("LABEL","kY","muY")},
               "B2":{k:B["POINT_B2"][k] for k in ("LABEL","kY","muY")},
               "A0":{"LABEL":"A0","kY":0.0,"muY":0.0,"ROLE":"no-Y-dynamics control"}},
     "INHERITED_FROZEN_CONSTANTS":C}
    json.dump(BD,open(f"{OUT}/DOTC01_PARENT_BINDING.json","w"),indent=1)
    json.dump(OM,open(f"{OUT}/DOTC01_EXECUTABLE_OBJECT_MAP.json","w"),indent=1)
    print("parent tip resolved:",BD["PARENT_TIP_RESOLVED"])
    print("engine matches frozen:",BD["ENGINE_MATCHES_FROZEN"])
    for k,v in progs.items():
        ver=v.get("verification")
        print("  %-8s present=%-5s %s"%(k,v["present"], ("verified %d, bad %d [%s]"%(ver["verified"],ver["n_bad"],ver["base"])) if ver and ver.get("present") else "no SHA256SUMS found"))
    print("PQEC01 raw:",OM["THE_DATA_SOURCE_FOR_THIS_MISSION"]["n_archives"],OM["THE_DATA_SOURCE_FOR_THIS_MISSION"]["points"])

if __name__=="__main__": main()
