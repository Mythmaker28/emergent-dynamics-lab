"""RESULTS MANIFEST. No freeze 2 was taken: the frozen sequential rule stopped the mission at
item 3, before any confirmation seed, so there was no selected point to freeze."""
import hashlib, json, os, sys
B="/home/claude/MCM01"; sys.path.insert(0,B+"/code")
import guard
h=lambda p: hashlib.sha256(open(p,"rb").read()).hexdigest()
files={}
for d in ("code","out","raw"):
    for f in sorted(os.listdir(os.path.join(B,d))):
        p=os.path.join(B,d,f)
        if os.path.isfile(p): files["%s/%s"%(d,f)]=h(p)
sel=json.load(open(B+"/out/_selection.json"))
rat=json.load(open(B+"/out/_ratchet.json"))
cal=json.load(open(B+"/out/_calibration.json"))
rec={"FREEZE_2":"NOT_TAKEN",
     "reason":"the frozen sequential stopping rule fired at item 3 (no point survives the "
              "frozen selection rule with the MEASURED c_X), so no point was selected, no "
              "confirmation seed was run, and no second freeze was possible",
     "disposition":"MINCORE_CLOUD_MAINTENANCE_FAIL",
     "scope":"not local: closes the family under the frozen thresholds",
     "survivors_frozen_rule":sel["survivors_frozen_rule"],
     "survivors_mean_variant":sel["survivors_mean_variant"],
     "family_closed_by_scope_scan":rat["family_closed"],
     "n_scope_scan_points":len(rat["scope_scan"]),
     "ledger":cal["ledger"],
     "file_sha256":files,
     "n_files":len(files)}
json.dump(rec,open(B+"/out/_results_manifest.json","w"),indent=1)
print("disposition:",rec["disposition"]); print("files hashed:",len(files))
print("ledger:",json.dumps(cal["ledger"]["by_class"]))
