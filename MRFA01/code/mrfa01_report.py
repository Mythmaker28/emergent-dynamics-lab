"""MRFA01 §16, §19 — terminal disposition and the written deliverables."""
from __future__ import annotations
import json, os, io, math, statistics, datetime, hashlib
REPO="/home/claude/edl"; OUT=f"{REPO}/MRFA01/out"
L=lambda n: json.load(open(f"{OUT}/{n}"))
BD=L("MRFA01_PARENT_BINDING.json"); R1=L("MRFA01_R1_RECOMPUTATION.json")
DA=L("MRFA01_CRITERION_D_AUDIT.json"); SH=L("_sham_falsification.json")
DC=L("MRFA01_THREE_ARM_CAUSAL_DECOMPOSITION.json"); IX=L("MRFA01_CAUSAL_AUTONOMY_INDICES.json")
MX=L("MRFA01_DAUGHTER_INDEPENDENCE_CRITERION_MATRIX.json"); OA=L("MRFA01_OPERATOR_REFERENCE_AUDIT.json")
PT=L("MRFA01_R2_FAILURE_PARTITION.json"); PC=L("MRFA01_POPULATION_VS_CONDITIONAL_ANALYSIS.json")
DG=L("MRFA01_POST_OUTCOME_CRITERION_DIAGNOSTICS.json"); PV=L("MRFA01_FMRT01_PROVENANCE_ADJUDICATION.json")
IC=L("MRFA01_INDEPENDENT_CHECK.json"); PW=L("MRFA01_POWER_ANALYSIS.json"); SF=L("_scale_finding.json")
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat()

DISP=("DAUGHTER_AUTONOMY_CRITERION_NOT_IDENTIFIABLE__EXACT_MISSING_OBJECT_NAMED"
      if not PW["FRESH_TEST_ELIGIBLE"] else
      "FROZEN_R2_CRITERION_MISALIGNED_WITH_LOCAL_AUTONOMY__FRESH_CAUSAL_RETEST_JUSTIFIED")

def disposition():
    D={"PROGRAMME":"MRFA01 — MINIMAL-REPRODUCTION-FAILURE-AUTOPSY-01",
     "GENERATED_UTC":NOW,
     "PARENT":BD["PARENT_PROGRAM_FULL_NAME"],"PARENT_TIP":BD["PARENT_TIP_RESOLVED_FROM_THE_SURVIVING_RECORDS"],
     "PARENT_REPORTED_RESULT":"MINIMAL_REPRODUCTION_NOT_QUALIFIED__DAUGHTER_INDEPENDENCE_NOT_ESTABLISHED",
     "NEW_SCIENTIFIC_RUNS_USED":0,"NEW_SEEDS":0,"NEW_WORLDS":0,"NEW_TRAJECTORIES":0,
     "RECONSTRUCTION":"TECHNICAL_PROVENANCE_RECONSTRUCTION, 22/22 bit-exact against every archived hash and scalar",
     "FORK_IDENTITY_GATE":BD["PRE_INTERVENTION_FORK_IDENTITY"]["GATE"],
     "CRITERION_D_CLASSIFICATION":DA["CLASSIFICATION"],
     "SHAM_FALSIFICATION_CONCLUSION":SH["CONCLUSION"],
     "OPERATOR_REFERENCE":OA["VERDICT"],
     "PREFERRED_DEFINITION":MX["PREFERRED"],
     "SEVEN_CONDITIONS_MET":PW["N_MET"],"OF":7,"FRESH_TEST_ELIGIBLE":PW["FRESH_TEST_ELIGIBLE"],
     "THE_EXACT_MISSING_OBJECT":MX["THE_EXACT_MISSING_OBJECT"],
     "FINAL_DISPOSITION":DISP,
     "FMRT01_FROZEN_RESULT_IS_UNCHANGED":True,
     "RETROACTIVE_FMRT01_SUCCESS":"NOT_CLAIMED_AND_NOT_POSSIBLE",
     "MINIMAL_REPRODUCTION_STATUS":"NOT_ESTABLISHED",
     "STRONG_SELF_REPRODUCTION_STATUS":"NOT_TESTED","HEREDITY_STATUS":"NOT_TESTED",
     "R3_STATUS":"NOT_TESTED","H3_STATUS":"NOT_TESTED","REPRODUCTION_STATUS":"NOT_TESTED",
     "AUTONOMOUS_COHESION_STATUS":"NOT_ESTABLISHED","X_LAWSPEC_BASELINE":"UNCHANGED",
     "ARCHITECTURE_CHANGE_NECESSITY":"NOT_ESTABLISHED",
     "CONDITIONAL_HANDOFF":"NONE — §14 authorises HANDOFF_FRESH_LOCAL_DAUGHTER_AUTONOMY_TEST_01 only if a fresh test is justified. It is not.",
     "WHAT_WOULD_MAKE_A_SUCCESSOR_ELIGIBLE":[
       "a daughter centre with internal state, so that centre persistence is not one molecule's survival",
       "a hold window matched to the organiser timescale rather than to the X relaxation timescale",
       "and only then a paired SELECTIVE vs GLOBAL_OFF endpoint under matched-pair exchangeability"],
     "PARAMETER_POINT":"B1, unchanged. No parameter search, no substrate change, no architecture change proposed."}
    json.dump(D,open(f"{OUT}/MRFA01_FINAL_DISPOSITION.json","w"),indent=2)
    return D

def d_audit_md():
    b=io.StringIO(); w=b.write
    w("# MRFA01 — CRITERION D, AUDITED FROM ITS DEFINITION\n\n")
    w("## The formula\n\n```\n%s\n```\n\n"%DA["EXACT_FORMULA"])
    w("Source: `%s`.\n\n"%DA["SOURCE"])
    w("## Every symbol, with its scope\n\n")
    w("| Symbol | Quantity | Spatial scope | Temporal scope | Independent unit |\n|---|---|---|---|---|\n")
    for s in DA["SYMBOL_TABLE"]:
        w("| `%s` | %s | %s | %s | %s |\n"%(s["symbol"],s["quantity"],s["spatial_scope"],s["temporal_scope"],s["independent_unit"]))
    w("\n### Why each was chosen\n\n")
    for s in DA["SYMBOL_TABLE"]: w("- **`%s`** — %s\n"%(s["symbol"],s["why_chosen"]))
    w("\n## What D actually compares\n\n")
    for k,v in DA["WHAT_D_COMPARES"].items(): w("- **%s**: %s\n"%(k,v))
    w("\nThe disc is **%d of %d cells, %.4f of the lattice**. The reference is computed on all of it.\n\n"
      %(DA["DISC_CELLS"],DA["LATTICE_CELLS"],DA["DISC_FRACTION_OF_LATTICE"]))
    Q=DA["QUANTITATIVE_CONSEQUENCES"]
    w("## What that costs, in molecules\n\n| | |\n|---|---|\n")
    w("| Median bound D demands | %s |\n"%Q["median_bound"])
    w("| Median daughter mass at the moment of intervention | %s |\n"%Q["median_daughter_mass_at_intervention"])
    w("| Blocks where the bound exceeds the daughter's **entire** mass | %d of %d |\n"%(Q["blocks_where_the_bound_EXCEEDS_the_daughters_entire_mass_at_intervention"],Q["of_blocks"]))
    w("| Median excess | +%s |\n"%Q["median_excess"])
    w("| Bound as a multiple of the daughter's own decayed stock | %.3f |\n"%Q["bound_as_multiple_of_the_daughters_own_decayed_stock"])
    w("| Measured old material in the fixed disc (GLOBAL arm), median | %s |\n"%Q["measured_old_material_in_the_fixed_disc_GLOBAL_arm_median"])
    w("| Analytic bound / measured old material | %.2f |\n\n"%Q["analytic_bound_over_measured_old_material"])
    w("> %s\n\n"%Q["reading"])
    w("## The decisive property: D is not invariant to world size\n\n")
    w("| World X scaled by | Median bound | SELECTIVE passes | SHAM passes |\n|---|---|---|---|\n")
    for k,v in DA["WORLD_SIZE_SENSITIVITY"].items():
        w("| %s | %s | %s/22 | %s/22 |\n"%(k.replace("world_X_",""),v["median_bound"],v["SELECTIVE_passes"],v["SHAM_passes"]))
    w("\n%s\n\n"%DA["WORLD_SIZE_ARGUMENT"])
    w("## Is D alpha-valid?\n\nYes. %s\n\n"%DA["ALPHA_VALIDITY_IS_NOT_ENOUGH"])
    w("## Classification\n\n```\n%s\n```\n\n%s\n\n"%(DA["CLASSIFICATION"],DA["CLASSIFICATION_BASIS"]))
    w("## What D would have needed\n\n%s\n\n"%DA["WHAT_D_WOULD_HAVE_NEEDED"])
    w("---\n\n## §4 — the SHAM arm as a mechanistic falsification test\n\n")
    R=SH["RECOMPUTED_FROM_BYTES"]
    w("| | |\n|---|---|\n")
    w("| SHAM daughter survives | %d/%d |\n"%(R["SHAM_daughter_survives"],R["of"]))
    w("| SHAM produces X in the fixed daughter disc | %d/%d |\n"%(R["SHAM_produces_X_in_the_fixed_daughter_disc"],R["of"]))
    w("| SHAM Y removed | %d |\n"%R["SHAM_removed_total"])
    w("| SHAM passes criterion D | %d/%d |\n"%(R["SHAM_criterion_D"],R["of"]))
    w("| SHAM **fails** criterion D | %d/%d |\n"%(R["SHAM_criterion_D_fails"],R["of"]))
    w("| Agrees with FMRT01's reported 8/22 | %s |\n\n"%R["AGREES"])
    for k,v in SH["HYPOTHESES"].items():
        w("**%s** → `%s`\n\n%s\n\n"%(k,v["verdict"],v["why"]))
    w("### The physical reason\n\n%s\n"%SH["THE_PHYSICAL_REASON"])
    open(f"{OUT}/MRFA01_CRITERION_D_AUDIT.md","w").write(b.getvalue())

def binding_md():
    b=io.StringIO(); w=b.write
    w("# MRFA01 — PARENT BINDING\n\n")
    w("Parent programme: **%s**\nTip: `%s`\n\n"%(BD["PARENT_PROGRAM_FULL_NAME"],BD["PARENT_TIP_RESOLVED_FROM_THE_SURVIVING_RECORDS"]))
    w("## The sixth container rollback\n\n> %s\n\n"%BD["CONTAINER_INCIDENT"])
    V=BD["RESTORATION_VERIFICATION"]
    w("| Restored set | Entries | Bad |\n|---|---|---|\n")
    w("| `FMRT01_SHA256SUMS` | %d | %d |\n"%(V["FMRT01_SHA256SUMS_entries"],len(V["FMRT01_SHA256SUMS_bad"])))
    w("| `FMRT01_RAW_SHA256SUMS` | %d | %d |\n"%(V["FMRT01_RAW_SHA256SUMS_entries"],len(V["FMRT01_RAW_SHA256SUMS_bad"])))
    w("| frozen methods closure | %d | %d |\n\n"%(V["METHODS_CLOSURE_entries"],len(V["METHODS_CLOSURE_bad"])))
    w("Engine `%s`, matches the frozen value: **%s**.\n\n"%(V["ENGINE_SHA256"][:16]+"…",V["ENGINE_MATCHES_FROZEN"]))
    w("## Exact accounting, recomputed from bytes\n\n| | |\n|---|---|\n")
    for k,v in BD["EXACT_ACCOUNTING"].items():
        if k!="note": w("| %s | %s |\n"%(k.replace("_"," "),v))
    w("\n> %s\n\n"%BD["EXACT_ACCOUNTING"]["note"])
    F=BD["PRE_INTERVENTION_FORK_IDENTITY"]
    w("## The §1 gate\n\n%s\n\n```\nPRE_INTERVENTION_PHYSICAL_STATE_IDENTICAL = %s\nPRE_INTERVENTION_RNG_STATE_IDENTICAL      = %s\n```\n\n"
      %(F["METHOD"],F["PRE_INTERVENTION_PHYSICAL_STATE_IDENTICAL"],F["PRE_INTERVENTION_RNG_STATE_IDENTICAL"]))
    w("Reconstructed hash matches the archived one in %s triads; all 22 triads are mutually distinct: %s.\n\n"
      %(F["RECONSTRUCTED_HASH_MATCHES_THE_ARCHIVED_ONE"],F["ALL_22_TRIADS_MUTUALLY_DISTINCT"]))
    w("**%s**\n\n"%F["GATE"])
    R=BD["RECONSTRUCTION"]
    w("## The reconstruction\n\n`STATUS = %s`, bit-exact in %d of %d triads.\n\n"%(R["STATUS"],R["bit_exact_triads"],R["of"]))
    w("`NEW_SEEDS = %d`, `NEW_WORLDS = %d`, `NEW_TRAJECTORIES = %d`, `NEW_SCIENTIFIC_RUNS = %d`.\n\n"
      %(R["NEW_SEEDS"],R["NEW_WORLDS"],R["NEW_TRAJECTORIES"],R["NEW_SCIENTIFIC_RUNS"]))
    w("Verified against: %s.\n"%", ".join("`%s`"%x for x in R["verified_against"]))
    open(f"{OUT}/MRFA01_PARENT_BINDING.md","w").write(b.getvalue())

def matrix_md():
    b=io.StringIO(); w=b.write
    w("# MRFA01 — WHAT DAUGHTER INDEPENDENCE SHOULD MEAN\n\n")
    w("Target concept: *%s*.\n\n"%MX["TARGET_CONCEPT"])
    w("Explicitly excluded: %s.\n\n"%", ".join(MX["EXPLICITLY_EXCLUDED"]))
    w("| | I absolute mass | II production | III operator-qualified | IV causal autonomy |\n|---|---|---|---|---|\n")
    keys=[("necessary_for_minimal_reproduction","necessary"),("sufficient","sufficient"),
          ("too_weak","too weak"),("too_strong","too strong"),("measurable_from_FMRT01","measurable from FMRT01"),
          ("invariant_to_world_size","invariant to world size"),
          ("invariant_to_unrelated_X_elsewhere","invariant to unrelated X"),
          ("depends_on_arbitrary_threshold","needs an arbitrary threshold")]
    for k,lab in keys:
        w("| %s | %s | %s | %s | %s |\n"%(lab,*[MX["DEFINITIONS"][i][k] for i in range(4)]))
    w("\n")
    for d in MX["DEFINITIONS"]:
        w("### %s — %s\n\n*%s*\n\n%s\n\n"%(d["id"],d["name"],d["statement"],d["verdict"]))
    w("## Preferred: %s\n\n"%MX["PREFERRED"])
    w("And still not a test at the available scale. %s\n\n"%MX["WHY"])
    D=MX["DEVELOPMENTAL_COUNT_UNDER_IV"]
    w("Developmentally, Definition IV holds in **%d of %d** FMRT01 triggered blocks "
      "(exact one-sided 95%% lower bound %.6f). `STATUS = %s`.\n\n"%(D["k"],D["n"],D["exact_one_sided_95_lower"],D["STATUS"]))
    w("## The exact missing object\n\n")
    for o in MX["THE_EXACT_MISSING_OBJECT"]:
        w("### %s\n\n%s\n\n"%(o["object"],o["why"]))
    open(f"{OUT}/MRFA01_DAUGHTER_INDEPENDENCE_CRITERION_MATRIX.md","w").write(b.getvalue())

if __name__=="__main__":
    D=disposition(); d_audit_md(); binding_md(); matrix_md()
    print("FINAL_DISPOSITION:",D["FINAL_DISPOSITION"])
    print("conditions met: %d/7"%D["SEVEN_CONDITIONS_MET"])
