"""RCD01 §10 + §11 — exact-binomial decision capability for a future minimal-reproduction test."""
from __future__ import annotations
import json, math
from scipy.stats import binom, beta
NMAX=256; ALPHA=0.05; POWER=0.80
def crit(n,p0,alpha=ALPHA):
    c=0
    while binom.sf(c-1,n,p0)>alpha: c+=1
    return c
def pw(n,p0,p1): return float(binom.sf(crit(n,p0)-1,n,p1))
def nreq(p0,p1,nmax=5000):
    if p1<=p0: return None
    for n in range(5,nmax+1):
        if pw(n,p0,p1)>=POWER: return n
    return None
def cp(k,n,conf=0.95):
    a=(1-conf)/2
    return [0.0 if k==0 else float(beta.ppf(a,k,n-k+1)), 1.0 if k==n else float(beta.ppf(1-a,k+1,n-k))]

A=json.load(open("out/_auditA.json"))
N=len(A); R0=sum(1 for r in A if r["R0_functional_success"])
R1=sum(1 for r in A if r["R0_functional_success"] and r["R1_material"])
p_R0=R0/N; p_R0R1=R1/N; p_R1_given_R0=R1/R0
rows=[]
for q in (1.00,0.80,0.60,0.50,0.40,0.30,0.20):
    p=p_R0R1*q
    rows.append({"assumed_daughter_survival_q":q,"population_reproduction_rate":p,
      "expected_successes_at_n256":p*NMAX,
      "n_required_vs_p0_0.02":nreq(0.02,p),"n_required_vs_p0_0.05":nreq(0.05,p),
      "power_at_n256_vs_p0_0.02":pw(NMAX,0.02,p),"power_at_n256_vs_p0_0.05":pw(NMAX,0.05,p),
      "decision_capable_within_256_vs_p0_0.05":bool((nreq(0.05,p) or 10**9)<=NMAX)})
expected_phase2=p_R0R1*NMAX
cond=[]
for q in (0.90,0.75,0.60,0.50):
    k=int(round(expected_phase2*q))
    cond.append({"assumed_q":q,"expected_phase2_worlds":expected_phase2,
      "expected_survivors":k,"exact_95_interval_on_q":cp(k,int(round(expected_phase2)))})
J={"SECTION":"RCD01 §10-§11 — decision capability of a future minimal-reproduction test",
 "MAX_PRIMARY_WORLDS":NMAX,"ALPHA":ALPHA,"TARGET_POWER":POWER,
 "METHOD":"exact binomial throughout; no normal approximation",
 "OBSERVED_INPUTS_FROM_THE_FRESH_192":{"N":N,"R0":R0,"R0_rate":p_R0,
   "R0_and_R1":R1,"R0_and_R1_rate":p_R0R1,"R1_given_R0":p_R1_given_R0,
   "note":"R1 is a CERTIFIED LOWER BOUND count, so p_R0R1 is itself a lower bound on the true rate"},
 "PRIMARY_ESTIMAND":"P(complete reproduction event per independently seeded world) = P(R0 and R1 and R2)",
 "SECONDARY_ESTIMAND":"P(daughter survives parent-off | functional materially-reconstructed daughter formed)",
 "POPULATION_LEVEL_SCENARIOS":rows,
 "EXPECTED_PHASE2_WORLDS_AT_N256":expected_phase2,
 "CONDITIONAL_PRECISION_SCENARIOS":cond,
 "SELECTION_BIAS_WARNING":("conditioning the denominator on worlds that reach Phase 2 estimates the "
   "CONDITIONAL daughter-independence probability, not the population reproduction rate. Both must be "
   "reported, with the population rate as the primary."),
 "CONTROLS_REQUIRED":{
   "SHAM":"identical scheduling and bookkeeping, no Y removed — separates the intervention from its timing",
   "PARENT_STAYS_ON":"the untouched trajectory — the FDFLT01 condition itself, already available",
   "GLOBAL_ORGANISER_OFF":"the existing OBTC02 intervention — distinguishes daughter autonomy from any-Y-removal",
   "PRE_MATURATION_INTERVENTION":"parent removed BEFORE the daughter matures — tests that the hold interval is doing work",
   "MINIMAL_SET":["SHAM","GLOBAL_ORGANISER_OFF","PRE_MATURATION_INTERVENTION"],
   "why_not_more":"a daughter-off symmetry control adds no discrimination once the parent/daughter label is tie-broken deterministically, and multiplying arms costs the budget it would need"},
 "BUDGET_VERDICT":None}
cap=[r for r in rows if r["decision_capable_within_256_vs_p0_0.05"]]
J["BUDGET_VERDICT"]=("DECISION_CAPABLE_WITHIN_256_FOR_DAUGHTER_SURVIVAL_DOWN_TO_q_%.2f"%min(r["assumed_daughter_survival_q"] for r in cap)
  if cap else "REPRODUCTION_TEST_NOT_DECISION_CAPABLE_WITHIN_BUDGET")
json.dump(J,open("out/RCD01_POWER_ANALYSIS.json","w"),indent=2)
print(json.dumps({"inputs":J["OBSERVED_INPUTS_FROM_THE_FRESH_192"],"expected_phase2":expected_phase2,
  "verdict":J["BUDGET_VERDICT"]},indent=2))
for r in rows: print("  q=%.2f p=%.4f exp=%.1f n_req(p0=.05)=%-6s power@256=%.3f capable=%s"%(
  r["assumed_daughter_survival_q"],r["population_reproduction_rate"],r["expected_successes_at_n256"],
  r["n_required_vs_p0_0.05"],r["power_at_n256_vs_p0_0.05"],r["decision_capable_within_256_vs_p0_0.05"]))
for c in cond: print("  conditional q=%.2f -> %d/%d, exact 95%% [%.4f, %.4f]"%(c["assumed_q"],c["expected_survivors"],
  round(c["expected_phase2_worlds"]),c["exact_95_interval_on_q"][0],c["exact_95_interval_on_q"][1]))
