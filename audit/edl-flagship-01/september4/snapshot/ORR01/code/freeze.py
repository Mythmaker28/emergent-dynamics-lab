import hashlib, json, os, sys
B="/home/claude/ORR01"; sys.path.insert(0,B+"/code")
CODE=["exact_chain.py","kinetics.py","lattice.py","lawspec_v2.py","guard.py","observe.py",
      "gates.py","analysis.py","run_theorem.py","protocol.py","tests_orr.py","costprobe.py"]
DOCS=["_provenance.json","_theorem.json","_analysis.json","_integrity.json","_costprobe.json",
      "ORR01_PREFREEZE_PLAN.md"]
h=lambda p: hashlib.sha256(open(p,"rb").read()).hexdigest()
code={f:h(os.path.join(B,"code",f)) for f in CODE}
docs={f:h(os.path.join(B,"out",f)) for f in DOCS}
core=hashlib.sha256()
for d in (code,docs):
    for k in sorted(d): core.update(k.encode()); core.update(d[k].encode())
import protocol as P, guard
integ=json.load(open(B+"/out/_integrity.json")); thm=json.load(open(B+"/out/_theorem.json"))
ana=json.load(open(B+"/out/_analysis.json")); prov=json.load(open(B+"/out/_provenance.json"))
rec={"FREEZE":1,"frozen_before":"the first confirmation start",
 "code_sha256":code,"doc_sha256":docs,"METHODS_CORE_HASH":core.hexdigest(),
 "protocol":P.constants(),
 "PROVENANCE_STATUS":prov["PROVENANCE_STATUS"],
 "theorem_checks":{c["check"]:c["outcome"] for c in thm["checks"]},
 "criticality":ana["criticality"]["verdict"],
 "repair_selected":ana["repairs"]["selected"],
 "repair_ranking":ana["repairs"]["ranking"],
 "PROTOCOL_ADVERSARIAL_AUDIT":integ["PROTOCOL_ADVERSARIAL_AUDIT"],
 "integrity":{"ALL_PASS":integ["ALL_PASS"],"tests":len(integ["tests"]),
   "gate_audit_cases":len(integ["gate_audit"]),"mutations":len(integ["mutations"]),
   "test_steps":integ["ledger_after_harness"]["test_steps_used"],
   "starts_consumed_by_the_harness":integ["ledger_after_harness"]["total"]},
 "starts_before_this_freeze":{"cost_probe":2,"confirmation":0,"control":0,
   "note":"the only engine advances before this freeze are the bounded score-blind harness "
          "steps and two cost probes on the manifold n[Y] == 0"}}
json.dump(rec,open(B+"/out/_freeze.json","w"),indent=1)
print("METHODS_CORE_HASH =",rec["METHODS_CORE_HASH"])
print("repair =",rec["repair_selected"]," gate audit =",rec["PROTOCOL_ADVERSARIAL_AUDIT"])
