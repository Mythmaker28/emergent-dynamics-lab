"""PRE-RESULT FREEZE. Hashes the tested bytes and the preplan before the first start."""
import hashlib, json, os, subprocess, sys
BASE = "/home/claude/MTW01"
CODE = ["window.py", "mtw.py", "guard.py", "observe.py", "blocks.py", "tests_mtw.py",
        "withdrawal_counterexample.py", "bench_primitives.py"]
DOCS = ["MINCORE_SCOPE_CORRECTION_ADDENDUM.md", "MINCORE_TIMESCALE_WINDOW_PREPLAN.md",
        "_window.json", "_integrity.json", "_withdrawal_counterexample.json"]

def h(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

code = {f: h(os.path.join(BASE, "code", f)) for f in CODE}
docs = {f: h(os.path.join(BASE, "out", f)) for f in DOCS}
core = hashlib.sha256()
for f in sorted(code):
    core.update(f.encode()); core.update(code[f].encode())
for f in sorted(docs):
    core.update(f.encode()); core.update(docs[f].encode())
integ = json.load(open(os.path.join(BASE, "out", "_integrity.json")))
win = json.load(open(os.path.join(BASE, "out", "_window.json")))
sys.path.insert(0, os.path.join(BASE, "code"))
import blocks as B
rec = {
 "PRE_RESULT_FREEZE": True,
 "frozen_before": "the first arm of block 1",
 "code_sha256": code, "doc_sha256": docs,
 "METHODS_CORE_HASH": core.hexdigest(),
 "adjudication": win["adjudication"],
 "window_design_point": {k: win["design_point"][k] for k in
    ("D_X","D_Y","a_X","a_Y","cluster","Delta_sep","tau_sep","tau_sep_kk_convention",
     "tau_sep_design","window_lower_R_Y","window_upper_R_Y_diffusive",
     "window_upper_R_Y_KK_packed","window_upper_R_Y_binding","emptiness_lhs",
     "window_non_empty","R_Y_at_Q_min","R_Y_at_Q_max","margin_lower","margin_upper",
     "whole_reachable_band_inside","coherence_chi","power")},
 "window_frozen_mincore_point": {k: win["frozen_point"][k] for k in
    ("cluster","tau_sep","window_lower_R_Y","window_upper_R_Y_diffusive",
     "window_upper_R_Y_KK_packed","emptiness_lhs","window_non_empty",
     "R_Y_at_Q_min","R_Y_at_Q_max")},
 "protocol": B.protocol_constants(),
 "integrity_all_pass": integ["ALL_PASS"],
 "integrity_counts": {"tests": len(integ["tests"]), "mutations": len(integ["mutations"]),
   "test_steps_used": integ["ledger_after_harness"]["test_steps_used"],
   "max_test_steps": integ["ledger_after_harness"]["max_test_steps"],
   "starts_consumed_by_harness": integ["ledger_after_harness"]["count"]},
 "declared_out_of_plan_outcome_informative_starts": {"count": 0, "items": [],
   "note": "no engine trajectory of any kind has been produced before this freeze. The only "
           "advances so far are the 721 bounded, score-blind steps of the integrity harness, "
           "which guard.py caps at 3000 and in which no start can be opened and no scoring "
           "function can be called. A primitive-level microbenchmark (bench_primitives.py) "
           "timed numpy Generator calls on bare arrays; it builds no World and advances "
           "nothing."},
 "start_formula": "4 blocks x 4 arms = 16 <= MAX_NEW_OUTCOME_INFORMATIVE_STARTS = 16; "
                  "TECHNICAL_RESERVE = 0",
 "prohibition": "no stochastic probe of any kind was used to establish the window; the "
                "adjudication in code/window.py is closed-form algebra",
}
json.dump(rec, open(os.path.join(BASE, "out", "_freeze.json"), "w"), indent=1)
print("METHODS_CORE_HASH =", rec["METHODS_CORE_HASH"])
print("adjudication      =", rec["adjudication"])
print("integrity ALL_PASS=", rec["integrity_all_pass"], rec["integrity_counts"])
