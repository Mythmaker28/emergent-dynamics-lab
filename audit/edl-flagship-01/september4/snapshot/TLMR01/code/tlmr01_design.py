"""TLMR01 §6 §7 §8 — the measurement objects, the uncertainty and support rules, the selection
rule, the power rule, the terminal vocabulary and the disposition logic.

EVERYTHING HERE IS FROZEN BEFORE WORLD 1 AND IS PURE ARITHMETIC. Not one number below is read
from a TLMR01 world, a TLMR01 fixture, or any TLMR01 observation. The only empirical figures that
appear are INHERITED and already published in committed parent artefacts, and each is cited to
the artefact that published it. That is what makes the threshold non-circular: it is not taken
from the outcomes it judges.
"""
from __future__ import annotations
import json, math, datetime, os, hashlib
from scipy.stats import beta, binom
REPO="/home/claude/edl"; OUT=f"{REPO}/TLMR01/out"
U=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
NEED=250; F_PRIMARY=1.0-1.0/math.e; LATEST=6500; T_HORIZON=11000; sI=5
N={"LAW_A_B1":128,"LAW_B_POINT_D10":128,"LAW_C_MCTT01":256}
MIN_WORLDS=10; MIN_EVENTS=30
K_MIN=2                      # a single event is not a replicate
CONFIRMATION_CEILING=1024    # worlds; beyond this the successor is not affordable and is refused

def ci(k,n):
    return [0.0 if k==0 else float(beta.ppf(0.025,k,n-k+1)),
            1.0 if k==n else float(beta.ppf(0.975,k+1,n-k))]
def lo95(k,n): return 0.0 if k==0 else float(beta.ppf(0.05,k,n-k+1))
def up95(k,n): return 1.0 if k==n else float(beta.ppf(0.95,k+1,n-k))

def p_star(n,kmin=K_MIN,power=0.80):
    """smallest per-world rate at which the design sees at least kmin events with probability
    >= power. Bisection on an exactly evaluated binomial survivor."""
    f=lambda p: 1.0-binom.cdf(kmin-1,n,p)
    lo,hi=0.0,1.0
    for _ in range(200):
        m=(lo+hi)/2
        if f(m)<power: lo=m
        else: hi=m
    return hi

def confirmation_n(p_alt,floor,alpha=0.05,power=0.80,ceiling=CONFIRMATION_CEILING):
    """smallest n at which a one-sided exact binomial test of H0: p <= floor has power >= `power`
    against p = p_alt. Returns None when the ceiling is exceeded."""
    if p_alt<=floor: return None
    for n in range(8,ceiling+1):
        k=int(binom.ppf(1-alpha,n,floor))+1          # smallest k rejecting H0 at level alpha
        if k>n: continue
        if 1.0-binom.cdf(k-1,n,p_alt)>=power: return n
    return None

# ------------------------------------------------------------------ inherited published figures
INHERITED={
 "FDOT01_functional_complete_turnover_at_B1":{"k":7,"n":160,
   "source":"FDOT01/out/FDOT01_PRIMARY_ANALYSIS.json","endpoint":"FUNCTIONAL_COMPLETE_TURNOVER, "
   "no trigger, no intervention"},
 "BPRTC01_integrated_chain_at_POINT_D10":{"n":256,"triggered":35,"removals_applied":34,
   "complete_turnovers":3,"functional":3,"k":3,
   "source":"BPRTC01/out/BPRTC01_ANALYSIS.json STATS_FOR_THE_FROZEN_GATES",
   "endpoint":"trigger, then SELECTIVE_PARENT_REMOVAL, then a post-removal FUNCTIONAL COMPLETE "
     "TURNOVER — the same chain M5 measures, at one of the three laws measured here"},
 "MCTT01_trigger_rate_at_the_MCTT01_law":{"k":6,"n":64,
   "source":"MCTT01/out/MCTT01_STAGE_A_QUALIFICATION.json","endpoint":"frozen functional trigger"},
 "MCTT01_removal_applied_of_triggered":{"k":3,"n":6,
   "source":"MCTT01/out/MCTT01_STAGE_A_QUALIFICATION.json TERMINAL_LABEL_COUNTS_DIAGNOSTIC_ONLY",
   "note":"of 6 triggers, 2 were TRIGGER_DESCENT_AMBIGUOUS and 1 REMOVAL_NOT_APPLIED"},
 "PTOPD01_maturation_by_occupancy_pooled":{
   "source":"PTOPD01/out/PTOPD01_SUPPORT_EXTRAPOLATION_GATE.json",
   "note":"zero of 3602 episodes above occupancy 3 matured at B1 mobility; the entire n > 5 "
          "regime of e(n) is unobserved, which is what this mission measures"},
}
# The floor is chosen by a PRINCIPLE, stated before any number: it must be the published lower
# bound of the endpoint that MATCHES M5 in kind. M5 is an INTEGRATED chain -- trigger, then the
# selective parent removal, then a post-removal functional complete turnover. Exactly one parent
# corpus published that chain end to end: BPRTC01 at POINT_D10, 256 worlds, 35 triggered, 34
# removals applied, 3 functional complete turnovers. FDOT01's 7 of 160 is a STRICTLY EASIER
# endpoint -- no trigger, no removal -- so using it as the gate would compare M5 against a bar it
# was never asked to clear. It is therefore reported as a stronger reference, never as the gate.
FLOOR={"value":float(lo95(3,256)),
 "name":"F_INTEGRATED",
 "definition":"the exact one-sided lower 95 per cent bound on BPRTC01's published 3 of 256 "
   "post-removal FUNCTIONAL COMPLETE TURNOVERS at POINT_D10 — the only endpoint any parent "
   "corpus published that matches M5 in kind",
 "k":3,"n":256,
 "principle":"match the endpoint kind. Stated before the value was computed, and it is the reason "
   "FDOT01's easier 7 of 160 is not the gate.",
 "why_it_is_not_circular":"it is computed from a COMMITTED PARENT corpus, a different mission and "
   "a different sample. No TLMR01 outcome enters it, and it is fixed here before world 1 runs.",
 "source":"BPRTC01/out/BPRTC01_ANALYSIS.json STATS_FOR_THE_FROZEN_GATES"}
STRONGER_REFERENCE={"value":float(lo95(7,160)),"name":"F_TURNOVER","k":7,"n":160,
 "definition":"the exact one-sided lower 95 per cent bound on FDOT01's 7 of 160 functional "
   "complete turnovers at B1, an endpoint with no trigger and no intervention",
 "role":"REPORTED, NEVER A GATE. A law that also clears it is flagged "
   "CLEARS_THE_STRONGER_TURNOVER_REFERENCE so that no reader can suppose the bar was quietly "
   "lowered.",
 "source":"FDOT01/out/FDOT01_PRIMARY_ANALYSIS.json ONE_SIDED_LOWER_95"}

def k_threshold(n,floor):
    for K in range(0,n+1):
        if lo95(K,n)>floor: return K
    return None
def k_for_confirmable(n,floor,ceiling=CONFIRMATION_CEILING):
    for K in range(0,n+1):
        if confirmation_n(lo95(K,n),floor,ceiling=ceiling) is not None: return K
    return None

# ------------------------------------------------------------------ §6 measurement objects
def measurement_objects():
    return {"MISSION":"TLMR01","SECTION":"6 — the five measurement objects","GENERATED_UTC":U(),
     "THE_UNIT_OF_EACH_OBJECT_IS_DECLARED":True,
     "THE_ONE_EXACT_SCIENTIFIC_QUESTION":
       "At the three exact executable laws, what are the fork hazard e(n) ABOVE the occupation "
       "support ceiling n = 5, the occupation-resolved maturation law s(n), P(trigger | matured), "
       "the single-centre time exposure, and the integrated trigger-to-turnover rate — measured "
       "directly, never modelled?",
     "PRIMARY_ESTIMAND":{
       "object":"M1 restricted to n > 5 — the fork hazard above PTOPD01's occupation support "
         "ceiling sI = 5, published stratum by stratum with its world-clustered uncertainty",
       "why_this_one":"it is the single object whose absence made PTOPD01's route "
         "NOT_IDENTIFIABLE. Its support-extrapolation gate had to stop at sI = 5 because no "
         "archive anywhere recorded the SINGLE-CENTRE EXPOSURE above that occupancy. Everything "
         "else this mission measures is either an input to it or a consequence of it.",
       "SUCCESS_CRITERION_IS_SUPPORT_NOT_A_VALUE":
         "the pre-registered criterion is whether e(n) becomes DIRECTLY_MEASURED — at least 10 "
         "distinct worlds and at least 30 single-centre steps of exposure — in at least one "
         "stratum with n > 5. There is deliberately NO threshold on the VALUE of e(n), because a "
         "measurement programme that set one would be taking a threshold from the outcomes it "
         "judges.",
       "why_the_numerator_is_already_known_to_be_nonzero":
         "PTOPD01's pooled occupation-resolved table records episodes BEGINNING at occupancy 6 "
         "(77), 7 (77), 8 (69), 9 (45), 10 (44) and on up past 36 across the three executed "
         "corpora. Every one of those is a fork that happened above n = 5. What no archive "
         "recorded is the denominator — the single-centre exposure at those occupancies — which "
         "this mission's schema records by construction, one row per component per step.",
       "source_of_that_inherited_count":"PTOPD01/out/PTOPD01_SUPPORT_EXTRAPOLATION_GATE.json "
         "MATURATION_BY_OCCUPANCY_POOLED"},
     "SELECTION_STATISTIC":{
       "object":"M5, the integrated trigger-to-turnover rate per world",
       "role":"it orders the laws for the selection rule of §8. It is NOT the primary estimand, "
         "and the two roles are kept apart on purpose: the primary is what the mission exists to "
         "measure, the selection statistic is what a later disjoint confirmation would have to be "
         "powered on.",
       "why_it_can_carry_that_role":"its unit is the WORLD, one seed each, so it needs no "
         "clustering correction and its exact interval is the honest one."},
     "M1":{"name":"e(n) — the fork hazard, resolved by single-centre occupancy",
       "why":"PTOPD01 could not obtain it above the occupation support n = 5 and named it missing",
       "definition":"e(n) = P(the world holds two or more centres at step t+1 | at step t it "
         "holds EXACTLY ONE centre whose Y occupancy is n). One step is one unit.",
       "exposure":"the single-centre step count at occupancy n, which is M4",
       "primary_regime":"n > 5, above PTOPD01's declared support ceiling sI = 5",
       "also_recorded":"the FULL transition table n_components(t) -> n_components(t+1) by n, so "
         "no later definition of a fork needs a re-run",
       "unit":"step","clustering":"steps within a world are not independent; reported per law with "
         "the world-clustered check of §7"},
     "M2":{"name":"s(n) — the occupation-resolved episode maturation law",
       "definition":"an EPISODE is a maximal run of the frozen FDFLT01 state S (exactly two "
         "centres, Y occupancy at least two, integrity intact, no third centre). n is the world Y "
         "occupancy at the FIRST step of the run, which is PTOPD01's convention. s(n) = P(the run "
         "reaches NEED = 250 consecutive S steps | the run began at occupancy n).",
       "outcomes":["MATURED_TO_FUNCTIONAL_MATURITY","MERGED_TO_ONE_CENTRE","FORMED_A_THIRD_CENTRE",
         "LOST_A_CENTRE_TO_A_SINGLE_Y","Y_EXTINCT","REACHED_THE_WINDOW_HORIZON","IDENTITY_AMBIGUOUS"],
       "outcomes_inherited_verbatim_from":"PTOPD01 §3 occupation-resolved episode operator",
       "IDENTITY_AMBIGUOUS_is_counted_not_assumed_zero":"PTOPD01 observed it zero times in three "
         "corpora. It is measured here, with its count published whatever it is.",
       "unit":"episode","clustering":"episodes within a world are not independent"},
     "M3":{"name":"P(trigger | matured)",
       "definition":"of the maturation candidates offered at exactly run_start + NEED - 1, the "
         "fraction that also satisfy every frozen FMRCT01 gate: the candidate step is at most "
         "LATEST_ALLOWED_TRIGGER = 6500, exactly two centres are present, and the weaker centre's "
         "local X mass over the frozen CORE_R disc is at least F_PRIMARY = 1 - 1/e of the "
         "stronger's.",
       "failure_modes_reported_separately":["deadline","not_exactly_two_centres","local_x_ratio"],
       "unit":"maturation candidate",
       "note":"the frozen watcher offers ONE candidate per episode, so the denominator is exactly "
         "the matured-episode count of M2"},
     "M4":{"name":"the single-centre time exposure",
       "definition":"the number of steps at which the world holds exactly one centre, resolved by "
         "that centre's Y occupancy n. Reported per world and per law, with the occupancy "
         "histogram, the fraction of the horizon, and the exposure above sI = 5.",
       "unit":"step",
       "why":"it is both the denominator of M1 and an object PTOPD01 named as missing in its own "
         "right"},
     "M5":{"name":"the integrated trigger-to-turnover rate — THE SELECTION STATISTIC",
       "definition":"the per-world probability that the whole frozen chain completes: A a "
         "maturation candidate is reached; B the frozen trigger fires; C the identity is carried "
         "to maturation so a parent and a daughter are named and the exact inherited "
         "SELECTIVE_PARENT_REMOVAL is applied; D after that removal a surviving identity interval "
         "shows a COMPLETE_TURNOVER that is FUNCTIONAL under the frozen DOTC01 rules.",
       "unit":"WORLD — independent by construction, one seed each",
       "why_it_carries_the_selection":"it is the only object among the five whose unit is the "
         "world, so it needs no clustering correction; and it is exactly the quantity a later "
         "disjoint causal confirmation would have to be powered on.",
       "one_parent_corpus_already_measured_this_exact_chain":"BPRTC01 at POINT_D10: 256 worlds, "
         "35 triggered, 34 removals applied, 3 functional complete turnovers. That published "
         "figure is the floor of §8 and is the reason the floor is not circular.",
       "decomposition_reported":["P(A)","P(B|A)","P(C|B)","P(D|C)"],
       "claim_ceiling":"a rate at which the frozen chain completes. It is NOT reproduction, NOT "
         "heredity, NOT autonomous cohesion and NOT life, and it qualifies no point by itself."},
     "WHAT_IS_FORBIDDEN":["interpolation","a response surface","a fitted curve of any kind",
       "smoothing across strata","pooling laws inside any gate","a threshold read from these "
       "outcomes","adaptive sample size","adaptive parameter retuning","a second measurement "
       "campaign","selecting a law that was not executed here"],
     "STRATA_WITH_NO_EXPOSURE":"reported as NO_EXPOSURE. Never as zero, and never filled in."}

# ------------------------------------------------------------------ §7 uncertainty and support
def uncertainty_rules():
    return {"MISSION":"TLMR01","SECTION":"7 — uncertainty and support","GENERATED_UTC":U(),
     "EVERY_PROPORTION_CARRIES":["the exact numerator and denominator","the exact Clopper-Pearson "
       "95 per cent interval","the exact one-sided lower 95 per cent bound"],
     "ZERO_NUMERATORS":"reported with the exact one-sided upper 95 per cent bound from the beta "
       "quantile. The rule of three is NOT used anywhere.",
     "DIRECTLY_MEASURED":{"rule":"a quantity is DIRECTLY_MEASURED at a law only if its denominator "
        "draws on at least %d distinct worlds AND contains at least %d elementary units of its "
        "own declared unit."%(MIN_WORLDS,MIN_EVENTS),
       "MIN_WORLDS":MIN_WORLDS,"MIN_EVENTS":MIN_EVENTS,
       "otherwise":"SUPPORT_TOO_THIN__NOT_DIRECTLY_MEASURED — published with its exact counts and "
         "interval, and forbidden from entering any gate or any selection."},
     "CLUSTERING":{"problem":"M1, M2, M3 and M4 have units (steps, episodes, candidates) that "
        "repeat within a world, so a naive binomial interval understates the uncertainty.",
       "rule":"each is published TWICE: the naive exact interval over the elementary unit, and a "
         "WORLD-CLUSTERED interval obtained by treating the world as the sampling unit and "
         "bootstrapping over worlds with the per-world numerators and denominators intact.",
       "which_one_gates":"only the world-clustered interval may support a claim; the naive one is "
         "descriptive.",
       "M5_needs_no_correction":"its unit IS the world."},
     "NO_LAW_IS_POOLED_WITH_ANOTHER_INSIDE_ANY_GATE":True,
     "OVERLAP_COMPARISON_IS_DESCRIPTIVE_ONLY":"where two laws populate the same occupancy stratum "
       "the two measurements are shown side by side. Agreement is not asserted, disagreement is "
       "not repaired, and neither is used to transport a quantity from one law to another. "
       "MCTT01 established that the fork-to-trigger conversion does not transport in kY; nothing "
       "here assumes any other quantity does.",
     "TECHNICAL_FAILURES":"a world with an engine invariant failure, a crashed process or a "
       "missing or corrupt archive is TECHNICAL. It may be replaced from the reserve band, at "
       "most %d times for the whole mission. A short denominator or any unreplaced technical "
       "failure makes the affected law TECHNICALLY_INVALID; it is never repaired scientifically."%6,
     "MAX_POST_OUTCOME_SCIENTIFIC_REPAIRS":0}

# ------------------------------------------------------------------ §8 selection and power
def power_rule():
    F=FLOOR["value"]
    ps={str(n):p_star(n) for n in (128,256,512)}
    per={}
    for law,n in N.items():
        kE3=k_threshold(n,F); kE6=k_for_confirmable(n,F)
        per[law]={"n":n,"p_star_for_K_at_least_2":p_star(n),
          "K_required_by_E3_lower_bound_exceeds_F":kE3,
          "lower95_at_that_K":lo95(kE3,n) if kE3 is not None else None,
          "K_required_by_E6_confirmation_affordable":kE6,
          "confirmation_n_at_that_K":(confirmation_n(lo95(kE6,n),F) if kE6 is not None else None),
          "BINDING_K":max([k for k in (K_MIN,kE3,kE6) if k is not None]),
          "K_also_clearing_the_stronger_reference":k_threshold(n,STRONGER_REFERENCE["value"])}
    return {"MISSION":"TLMR01","SECTION":"8 — the power rule","GENERATED_UTC":U(),
     "TWO_SEPARATE_QUESTIONS":"the primary estimand and the selection statistic are powered "
       "differently and are reported separately. Merging them would let a favourable figure for "
       "one stand in for the other.",
     "PART_A_PRIMARY_ESTIMAND_SUPPORT":{
       "estimand":"e(n) for n > 5",
       "criterion":"DIRECTLY_MEASURED in at least one stratum above sI = 5: at least %d distinct "
         "worlds and at least %d single-centre steps of exposure in that stratum"%(MIN_WORLDS,MIN_EVENTS),
       "why_no_prospective_power_curve_is_given":"the exposure denominator is precisely the "
         "quantity no archive ever recorded, so any prospective figure for it would be a model, "
         "and a model is what this programme exists to replace. The support achieved is reported, "
         "whatever it is, and a shortfall returns "
         "MEASUREMENT_INCOMPLETE__PRIMARY_REGIME_UNREACHED rather than an estimate.",
       "what_inherited_evidence_does_say":"forks above occupancy 5 are common in the executed "
         "corpora — PTOPD01's pooled table shows 77 episodes beginning at occupancy 6, 77 at 7, "
         "69 at 8 and hundreds more above — and LAW_C_MCTT01 is the highest-occupation law of the "
         "three, with a published median maximum Y occupancy of 231. That is why 256 of the 512 "
         "worlds are allocated to it.",
       "allocation_and_its_reason":{law:{"n":n} for law,n in N.items()},
       "ALLOCATION_IS_DRIVEN_BY_THE_PRIMARY_NOT_BY_THE_SELECTION_STATISTIC":True},
     "PART_B_SELECTION_STATISTIC_POWER":{
       "estimand":"M5, per world","K_MIN":K_MIN,
       "RULE":"p*(n) is the smallest per-world rate at which the design observes at least K_MIN = "
         "%d events with probability at least 0.80, computed exactly from the binomial with no "
         "normal approximation."%K_MIN,
       "K_MIN_IS_TWO_BECAUSE":"one event is not a replicate. The inherited house rule across "
         "FDOT01, BPRTC01 and PTOPD01 is that a design must be able to see the event twice.",
       "p_star":ps,
       "PER_LAW":per,
       "POOLED_512_IS_NOT_THE_DESIGNS_ASSURANCE":{"p_star_512":ps["512"],
         "why":"the three laws are different physics and are never pooled inside a gate. The "
           "pooled figure is shown only so a reader can see how much assurance would come from "
           "aggregation, and it is not used."},
       "FLOOR":FLOOR,"STRONGER_REFERENCE":STRONGER_REFERENCE,
       "CONFIRMATION_CEILING_WORLDS":CONFIRMATION_CEILING},
     "INHERITED_REFERENCE_RATES_FOR_M5":INHERITED,
     "WHAT_THIS_DESIGN_CAN_AND_CANNOT_SEE":{
       "LAW_C_MCTT01":"n = 256 gives p* = %.6g. MCTT01 published 6 of 64 triggers at this exact "
         "law with 3 of those 6 reaching an applied removal, so the plausible range for M5 sits "
         "above p*. The design has assurance here."%p_star(256),
       "LAW_B_POINT_D10":"n = 128 gives p* = %.6g, while BPRTC01 measured this exact chain at "
         "this exact law as 3 of 256 = %.6g. The design is therefore UNDERPOWERED at LAW_B "
         "relative to its own inherited expectation: at that rate it sees two or more events only "
         "about %.0f per cent of the time. This is stated as a declared limitation before world 1 "
         "and is NOT repaired by pooling or by moving worlds after the fact."%(
           p_star(128),3/256,100*(1.0-binom.cdf(1,128,3/256))),
       "LAW_A_B1":"n = 128 gives p* = %.6g. No parent corpus measured this chain at B1 — FDOT01's "
         "7 of 160 is a strictly easier endpoint with no trigger and no removal — so no honest "
         "prospective statement is available and none is invented."%p_star(128)},
     "NO_ADAPTIVE_SAMPLE_SIZE":True,"NO_INTERIM_ANALYSIS":True,
     "NO_WORLD_IS_MOVED_BETWEEN_LAWS_AFTER_THE_BUDGET_IS_FROZEN":True,
     "THE_BUDGET_IS_FIXED_AT_512_PRIMARY_WORLDS_BEFORE_WORLD_1":True}

def selection_rule():
    F=FLOOR["value"]
    per={law:{"n":n,"K_required":max([k for k in (K_MIN,k_threshold(n,F),
                                                  k_for_confirmable(n,F)) if k is not None]),
              "which_clause_binds":("E6" if (k_for_confirmable(n,F) or 0)>=max(K_MIN,k_threshold(n,F) or 0)
                                    else "E3")}
         for law,n in N.items()}
    return {"MISSION":"TLMR01","SECTION":"8 — the selection rule","GENERATED_UTC":U(),
     "WHAT_IS_SELECTED":"at most ONE law, from the three EXECUTED here, for a later DISJOINT "
       "causal confirmation. Selecting zero is a permitted and honourable outcome.",
     "MAX_SELECTED_CONFIRMATION_LAWS":1,
     "UNEXECUTED_LAW_SELECTION":"FORBIDDEN. Only a law measured in this mission may be selected.",
     "POST_OUTCOME_NEW_LAW_SELECTION":"FORBIDDEN.",
     "ORDERING_STATISTIC":"the exact one-sided lower 95 per cent bound on M5 at that law",
     "FLOOR":FLOOR,"STRONGER_REFERENCE":STRONGER_REFERENCE,
     "ELIGIBILITY_ALL_MUST_HOLD":{
       "E1":"the law ran its full planned n with a complete denominator and no unreplaced "
            "technical failure",
       "E2":"M5 numerator K >= %d at that law"%K_MIN,
       "E3":"the exact one-sided lower 95 per cent bound on M5 at that law exceeds the floor "
            "F_INTEGRATED = %.17g"%F,
       "E4":"M2 is DIRECTLY_MEASURED in at least one occupancy stratum in which maturation was "
            "observed",
       "E5":"M3 is directly measured — at least one matured episode, and the denominator is the "
            "measured matured count and never a modelled one",
       "E6":"a later disjoint confirmation is affordable: the exact n needed to reject "
            "p <= F_INTEGRATED at one-sided 95 per cent with 80 per cent power, evaluated at the "
            "law's own measured lower bound, is at most %d worlds"%CONFIRMATION_CEILING},
     "PRECOMPUTED_SO_ELIGIBILITY_IS_CHECKABLE_BEFORE_WORLD_1":per,
     "TIES":"an exact tie on the ordering statistic selects NOTHING and is reported as a tie. It "
       "is never resolved by preference — the same rule the frozen identity link uses for a tie "
       "between centres.",
     "IF_NONE_IS_ELIGIBLE":"NO_LAW_SELECTED. The measurement still stands; the confirmation is "
       "simply not authorised by this mission.",
     "THE_RULE_IS_FIXED_BEFORE_WORLD_1":True,
     "NO_THRESHOLD_IS_TAKEN_FROM_THE_OUTCOMES_IT_JUDGES":True,
     "THE_FLOOR_WAS_CHOSEN_BY_A_STATED_PRINCIPLE_NOT_BY_ITS_VALUE":FLOOR["principle"]}

def terminal_vocabulary():
    return {"MISSION":"TLMR01","SECTION":"8 — terminal vocabulary","GENERATED_UTC":U(),
     "UNCONDITIONAL":{
       "H3_STATUS":"NOT_TESTED","REPRODUCTION_STATUS":"NOT_TESTED","HEREDITY_STATUS":"NOT_TESTED",
       "AUTONOMOUS_COHESION_STATUS":"NOT_ESTABLISHED","X_LAWSPEC_BASELINE":"UNCHANGED",
       "ARCHITECTURE_CHANGE_NECESSITY":"NOT_ESTABLISHED",
       "COMPANION_PAPER_V1_1_STATUS":"UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED",
       "PTOPD01_LINEAGE_POINT_ROUTE_STATUS":"PAUSED",
       "OLD_ROUTE_A_STATUS":"REJECTED__NOT_AUTHORISED",
       "FINITE_SIZE_RELEVANCE":"NOT_SUPPORTED"},
     "FORBIDDEN_VOCABULARY":["organism","daughter organism","life created",
       "self-replication demonstrated"],
     "FORBIDDEN_CLAIMS_INCLUDING_IN_DENIAL":["reproduction","heredity","life",
       "autonomous cohesion","H3 confirmation","Kamimura-Kaneko validation","a minority window"],
     "CLAIM_CEILING":"the named objects have been measured at the laws and occupancies stated. "
       "Nothing more is claimed, and no point is qualified by this mission.",
     "INHERITED_CLAUSES_RE_EMITTED_VERBATIM":{
       "MEASUREMENT_NOT_POINT_SEARCH":"true",
       "ONE_ZERO_RUN_DETOUR_ONLY":"spent — no further finite-size mission",
       "SECOND_FINITE_SIZE_EXTENSION":"forbidden","NEW_SIZE_LADDER":"forbidden",
       "POST_OUTCOME_SIZE_RETUNING":"forbidden","NEW_PARAMETER_SWEEP":"forbidden",
       "GENERIC_CALIBRATION_SUCCESSOR":"forbidden","INTERPOLATION":"forbidden",
       "RESPONSE_SURFACE":"forbidden","EVERY_SUCCESSOR_MUST_RE_EMIT_THESE_CLAUSES":"true",
       "REOPENING_FINITE_SIZE_REQUIRES_EXPLICIT_HUMAN_AUTHORISATION":"true",
       "MAX_INDEPENDENT_CHECKERS":"1","MAX_REVIEW_CASCADES":"0",
       "CHECKER_RETURN_WRITTEN_BEFORE_ANY_FINDING_IS_ACTED_ON":"mandatory"}}

def disposition_logic():
    return {"MISSION":"TLMR01","SECTION":"8 — disposition logic","GENERATED_UTC":U(),
     "EXACTLY_ONE_DISPOSITION_IS_RETURNED":True,
     "EVALUATED_IN_THIS_ORDER_AND_THE_FIRST_MATCH_WINS":[
      {"1":"TECHNICALLY_INVALID__DENOMINATOR_INCOMPLETE_OR_UNREPLACED_TECHNICAL_FAILURE",
       "when":"any law's primary denominator is short of its planned n, or any technical failure "
              "remains unreplaced after the reserve band is exhausted"},
      {"2":"MEASUREMENT_INCOMPLETE__PRIMARY_REGIME_UNREACHED",
       "when":"no law delivered DIRECTLY_MEASURED support for M1 anywhere above the occupation "
              "support ceiling sI = 5. The mission's own reason for existing was that regime."},
      {"3":"MEASUREMENT_DELIVERED__ONE_LAW_SELECTED_FOR_DISJOINT_CONFIRMATION",
       "when":"M1 to M5 are measured, at least one law satisfies E1 to E6, and the ordering "
              "statistic has a unique maximum"},
      {"4":"MEASUREMENT_DELIVERED__NO_LAW_SELECTED__EXACT_TIE",
       "when":"two or more eligible laws tie exactly on the ordering statistic"},
      {"5":"MEASUREMENT_DELIVERED__NO_LAW_ELIGIBLE__CONFIRMATION_NOT_AUTHORISED",
       "when":"M1 to M5 are measured and no law satisfies E1 to E6"}],
     "MUTUAL_EXCLUSIVITY":"guaranteed by the ordered cascade; the first match returns and no "
       "later branch is evaluated.",
     "EXHAUSTIVENESS":"branch 5 is the complement of 1 to 4 given that the run completed, so the "
       "set covers every reachable state.",
     "NOTHING_IS_REPAIRED_AFTER_THE_OUTCOME":True,
     "MAX_POST_OUTCOME_SCIENTIFIC_REPAIRS":0}

def main():
    arts={"TLMR01_MEASUREMENT_OBJECTS.json":measurement_objects(),
          "TLMR01_UNCERTAINTY_RULES.json":uncertainty_rules(),
          "TLMR01_POWER_RULE.json":power_rule(),
          "TLMR01_SELECTION_RULE.json":selection_rule(),
          "TLMR01_TERMINAL_VOCABULARY.json":terminal_vocabulary(),
          "TLMR01_DISPOSITION_LOGIC.json":disposition_logic()}
    os.makedirs(OUT,exist_ok=True)
    for k,v in arts.items(): json.dump(v,open(f"{OUT}/{k}","w"),indent=1)
    P=arts["TLMR01_POWER_RULE.json"]
    F=FLOOR["value"]
    print("F_INTEGRATED = %.17g   (lower95 of BPRTC01 3/256, endpoint-matched)"%F)
    print("F_TURNOVER   = %.17g   (reported, never a gate)"%STRONGER_REFERENCE["value"])
    for law,n in N.items():
        kE3=k_threshold(n,F); kE6=k_for_confirmable(n,F)
        print("  %-16s n=%3d  p*=%.6g  K needed: E3>=%s E6>=%s -> BINDING K>=%d  (conf n=%s)"%(
          law,n,p_star(n),kE3,kE6,max(K_MIN,kE3 or 0,kE6 or 0),
          confirmation_n(lo95(kE6,n),F) if kE6 else None))
    print("  pooled p*(512) = %.6g  (NOT the design's assurance)"%p_star(512))
    print("artefacts:",", ".join(sorted(arts)))

if __name__=="__main__": main()
