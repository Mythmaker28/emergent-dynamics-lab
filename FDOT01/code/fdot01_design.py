"""FDOT01 §3 — detection assurance at the frozen N = 160. Computed BEFORE any world is run."""
from __future__ import annotations
import json, datetime
from scipy.stats import binom
REPO="/home/claude/edl"; OUT=f"{REPO}/FDOT01/out"
N=160; THRESH=2
D=json.load(open(f"{OUT}/FDOT01_DEVELOPMENTAL_RECOMPUTE.json"))
def assur(p): return {("K>=%d"%k):float(1.0-binom.cdf(k-1,N,p)) for k in (1,2,3)}
P={
 "STRICT_RULE_one_sided_95_lower":D["FUNCTIONAL_TURNOVER"]["one_sided_95_lower"],
 "STRICT_RULE_point_estimate":D["FUNCTIONAL_TURNOVER"]["rate"],
 "DOTC01_REPORTED_one_sided_95_lower":D["DOTC01_REPORTED"]["functional_one_sided_95_lower"],
 "DOTC01_REPORTED_point_estimate":D["DOTC01_REPORTED"]["functional"]/D["N_DEVELOPMENTAL_B1_WORLDS"],
}
R={"SECTION":"FDOT01 §3 — detection assurance at the frozen N = 160, computed before any world",
 "GENERATED_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "N":N,"REPLICATION_THRESHOLD":THRESH,
 "N_IS_FIXED_BY_THE_LAUNCHER_AND_IS_NOT_ALTERED":True,
 "ADAPTIVE_SAMPLE_SIZE":"forbidden, and not used",
 "DESIGN_INPUTS":P,
 "ASSURANCE":{k:assur(v) for k,v in P.items()},
 "EXPECTED_COUNTS":{k:N*v for k,v in P.items()},
 "THE_PRE_RUN_PROBLEM_STATED_PLAINLY":(
   "the launcher expected P(K >= 2 | N = 160, p_design) to come out near 0.80 using DOTC01's "
   "reported functional rate of 3/44 and its lower bound 0.01884. Recomputing the developmental "
   "input from the parent bytes under the rule FDOT01 §5 MANDATES — ties, splits and merges all "
   "terminate centre identity — gives 1/44, not 3/44, and a lower bound of 0.001165. At that "
   "input the assurance for K >= 2 is far below 0.80. This is reported BEFORE the runs, not "
   "discovered afterwards. N is not changed, because §3 fixes it and adaptive sample size is "
   "forbidden."),
 "WHY_THE_INPUT_MOVED":D["DIFFERENCE_EXPLAINED"],
 "WHICH_RULE_IS_AUTHORITATIVE":(
   "FDOT01 §5 lists 'ties: terminate identity / split: terminate identity / merge: terminate "
   "identity' explicitly, and DOTC01's own written definition says a match that is not mutually "
   "unique ends the interval. DOTC01's audit CODE was more permissive than its own definition. "
   "§1 orders the parent DEFINITION preserved, so the strict rule is used and the discrepancy "
   "is reported rather than resolved in favour of the more convenient number."),
 "CONSEQUENCE_FOR_INTERPRETATION":(
   "a K < 2 outcome must therefore NOT be read as evidence that the phenomenon is absent. At the "
   "conservative input the experiment is underpowered for the K >= 2 threshold by construction. "
   "The rate estimate and its exact interval carry the information in that case, and §4 already "
   "makes rate estimation co-primary descriptive evidence.")}
json.dump(R,open(f"{OUT}/FDOT01_DETECTION_ASSURANCE.json","w"),indent=1)
for k,v in P.items():
    a=assur(v)
    print("  p=%-38s %.8f  E[K]=%6.3f  K>=1 %.4f  K>=2 %.4f  K>=3 %.4f"%(k,v,N*v,a["K>=1"],a["K>=2"],a["K>=3"]))
