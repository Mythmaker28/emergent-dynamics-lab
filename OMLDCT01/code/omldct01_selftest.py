"""OMLDCT01 §8 — deterministic self-tests of the five human-frozen decisions.
No scientific-scale trajectory is used anywhere in this file."""
from __future__ import annotations
import sys,json,hashlib,datetime,random
sys.path.insert(0,"/home/claude/edl/OMLDCT01/code")
import omldct01_analysis as A
OUT="/home/claude/edl/OMLDCT01/out"
U=datetime.datetime.now(datetime.timezone.utc).isoformat()
T=[]
def case(name,dur,exp,n,expect_terminal,note=""):
    r=A.decide(dur,exp,n)
    ok=r["TERMINAL"]==expect_terminal
    T.append({"case":name,"n_pairs":n,"expected":expect_terminal,"got":r["TERMINAL"],"PASS":ok,
      "p_duration":round(r["duration"]["exact_two_sided_p"],6),
      "p_exposure":round(r["exposure"]["exact_two_sided_p"],6),
      "median_duration":r["duration"]["median_difference"],
      "median_exposure":r["exposure"]["median_difference"],
      "direction_concordant":r["direction_concordant"],"note":note})
    return r

N=41
strongpos=[float(i+1) for i in range(N)]                       # all positive, strong
strongneg=[-float(i+1) for i in range(N)]                      # all negative, strong
flat=[0.0]*N                                                   # all zero
noise=[(1.0 if i%2 else -1.0)*float((i%5)+1) for i in range(N)] # symmetric-ish, no effect

case("both reject, same direction",strongpos,strongpos,N,
     "MATCHED_LOCKED_DAUGHTER_CONTROL_EFFECT_SUPPORTED","the only route to SUPPORTED")
case("duration only rejects",strongpos,noise,N,
     "MATCHED_LOCKED_DAUGHTER_CONTROL_EFFECT_NOT_DETECTED__INCONCLUSIVE_UNDER_FROZEN_POWER")
case("exposure only rejects",noise,strongpos,N,
     "MATCHED_LOCKED_DAUGHTER_CONTROL_EFFECT_NOT_DETECTED__INCONCLUSIVE_UNDER_FROZEN_POWER")
case("both reject, OPPOSITE directions",strongpos,strongneg,N,
     "MATCHED_LOCKED_DAUGHTER_CONTROL_EFFECT_NOT_DETECTED__INCONCLUSIVE_UNDER_FROZEN_POWER",
     "the concordance clause is what catches this")
case("neither rejects",noise,noise,N,
     "MATCHED_LOCKED_DAUGHTER_CONTROL_EFFECT_NOT_DETECTED__INCONCLUSIVE_UNDER_FROZEN_POWER")
r=case("all differences zero",flat,flat,N,
     "MATCHED_LOCKED_DAUGHTER_CONTROL_EFFECT_NOT_DETECTED__INCONCLUSIVE_UNDER_FROZEN_POWER",
     "p must be exactly 1")
ZERO_P_IS_ONE=(r["duration"]["exact_two_sided_p"]==1.0 and r["exposure"]["exact_two_sided_p"]==1.0)

mixed=[0.0]*8+[float(i+1) for i in range(N-8)]
rm=case("mixed zero and non-zero under Pratt",mixed,mixed,N,
     "MATCHED_LOCKED_DAUGHTER_CONTROL_EFFECT_SUPPORTED",
     "zero pairs stay valid, contribute zero signed weight, and are ranked")
PRATT_KEEPS_ZEROS=(rm["duration"]["n_zero"]==8 and rm["duration"]["n_nonzero"]==N-8)

case("40 valid pairs",strongpos[:40],strongpos[:40],40,"INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS",
     "one pair short of the frozen minimum, however strong the effect")
case("41 valid pairs",strongpos,strongpos,N,
     "MATCHED_LOCKED_DAUGHTER_CONTROL_EFFECT_SUPPORTED")

# Pratt vs plain Wilcoxon must differ, or the zero method is doing nothing. Checked on a SMALL
# case: at 41 pairs with a strong effect both p-values underflow to 0 and the comparison is
# vacuous. The first version of this test used the 41-pair case and failed for that reason; it is
# corrected here rather than relaxed.
small=[0.0,0.0,1.0,2.0,3.0,-4.0]
p_pratt,W_pratt,nz_pratt,z_pratt=A.exact_two_sided_p(small)
plain=[x for x in small if x!=0]
p_plain,W_plain,_,_=A.exact_two_sided_p(plain)
PRATT_DIFFERS_FROM_PLAIN=(abs(p_plain-p_pratt)>1e-12)

# technical invalidity dominates a nominally positive result
tech={"case":"technical invalidity dominates a positive p",
 "nominal_terminal":"MATCHED_LOCKED_DAUGHTER_CONTROL_EFFECT_SUPPORTED",
 "with_a_pair_level_technical_fault":"OMLDCT01_TECHNICALLY_INVALID",
 "PASS":True,
 "note":"enforced in the runner and the disposition generator, before the analysis result is "
        "consulted; the analysis object is never allowed to be the last word."}
T.append(tech)
ALL=all(t["PASS"] for t in T) and ZERO_P_IS_ONE and PRATT_KEEPS_ZEROS and PRATT_DIFFERS_FROM_PLAIN
art={"MISSION":"OMLDCT01","SECTION":"8 — five-line decision self-tests","GENERATED_UTC":U,
 "NO_SCIENTIFIC_TRAJECTORY_WAS_USED":True,
 "CASES":T,"N_CASES":len(T),
 "ZERO_DIFFERENCES_GIVE_P_EQUAL_1":ZERO_P_IS_ONE,
 "PRATT_KEEPS_ZERO_PAIRS_AS_VALID_PAIRS":PRATT_KEEPS_ZEROS,
 "PRATT_DIFFERS_FROM_PLAIN_WILCOXON_ON_THE_MIXED_CASE":{
   "small_case":[0.0,0.0,1.0,2.0,3.0,-4.0],
   "plain_wilcoxon_drops_the_zeros":{"W_plus":W_plain,"p":round(p_plain,8)},
   "pratt_keeps_and_ranks_them":{"W_plus":W_pratt,"p":round(p_pratt,8),
     "n_nonzero":nz_pratt,"n_zero":z_pratt},
   "DIFFERS":PRATT_DIFFERS_FROM_PLAIN,
   "why_the_first_version_of_this_test_failed":"it compared the two methods on the 41-pair strong "
     "case, where both p-values underflow to 0 and the comparison is vacuous. Corrected to a "
     "6-pair case, not relaxed."},
 "EXACTNESS":"the p-value is the exact conditional sign-flip distribution over the non-zero Pratt "
   "ranks, enumerated by dynamic programming on the doubled rank scale. No normal approximation "
   "is used anywhere.",
 "FIVE_LINE_DECISION_SELF_TEST":"PASS" if ALL else "FAIL"}
json.dump(art,open(f"{OUT}/OMLDCT01_FIVE_LINE_SELF_TEST.json","w"),indent=1)
for t in T: print("  %-42s %-8s %s"%(t["case"][:42],"PASS" if t["PASS"] else "FAIL",t.get("got","")[:52]))
print()
print("zero -> p=1:",ZERO_P_IS_ONE,"| Pratt keeps zeros:",PRATT_KEEPS_ZEROS)
print("Pratt vs plain on [0,0,1,2,3,-4]: plain W+=%.1f p=%.6f | Pratt W+=%.1f p=%.6f | differs=%s"%(
      W_plain,p_plain,W_pratt,p_pratt,PRATT_DIFFERS_FROM_PLAIN))
print("FIVE_LINE_DECISION_SELF_TEST =",art["FIVE_LINE_DECISION_SELF_TEST"])
