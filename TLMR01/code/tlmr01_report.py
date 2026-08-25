"""TLMR01 §18 §19 — the final report and the conditional handoff, generated FROM the artefacts.

Nothing is retyped by hand: every figure below is read from TLMR01_ANALYSIS.json and the frozen
rules. The handoff is CONDITIONAL and its gate is the FIRST statement in it, because FOTSEA01's
independent check found a handoff that described itself as conditional and never read the gate.
"""
from __future__ import annotations
import json, os, sys, datetime
REPO="/home/claude/edl"; OUT=f"{REPO}/TLMR01/out"
sys.path.insert(0,f"{REPO}/TLMR01/code")
import tlmr01_design as DZ
def g(x,d="—"): return d if x is None else x
def f6(x): return "—" if x is None else "%.6g"%x
def pct(k,n): return "—" if not n else "%d/%d = %.5f"%(k,n,k/n)

def report():
    A=json.load(open(f"{OUT}/TLMR01_ANALYSIS.json"))
    FZ=json.load(open(f"{OUT}/TLMR01_MASTER_FREEZE.json"))
    V=json.load(open(f"{OUT}/TLMR01_TERMINAL_VOCABULARY.json"))
    L=[];a=L.append
    a("# TLMR01 — FINAL SCIENTIFIC REPORT\n")
    a("`TARGETED-LINEAGE-MEASUREMENT-FOR-REPRODUCTION-01`. Master freeze `%s`, taken alone before"%FZ["FREEZE_HASH"][:16])
    a("world 1. Every rule, threshold, unit and ordering below was fixed before any world ran.\n")
    a("## 1. Disposition\n")
    a("```")
    a("DISPOSITION  = %s"%A["DISPOSITION"])
    a("SELECTED_LAW = %s"%g(A["SELECTED_LAW"],"NONE"))
    a("```\n")
    a("## 2. What was executed\n")
    a("| law | planned | read | technical failures |")
    a("|---|---:|---:|---:|")
    for law,n in A["PLANNED_PER_LAW"].items():
        a("| `%s` | %d | %d | %d |"%(law,n,A["READ_PER_LAW"].get(law,0),
                                     A["TECHNICAL_FAILURES_PER_LAW"].get(law,0)))
    a("")
    a("Short denominators: %s. Full horizon, no scientific early stop of any kind.\n"%(
      ", ".join(A["SHORT_DENOMINATORS"]) or "none"))
    a("## 3. The primary estimand — e(n) above the occupation support ceiling n = 5\n")
    a("The success criterion frozen before world 1 is SUPPORT, not a value.")
    a("`PRIMARY_ESTIMAND_SUPPORT_REACHED = %s`\n"%A["PRIMARY_ESTIMAND_SUPPORT_REACHED"])
    a("| law | strata above n=5 | forks | exposure (steps) | worlds | rate | exact 95 % CI | world-clustered 95 % CI | directly measured |")
    a("|---|---|---:|---:|---:|---:|---|---|---|")
    for law,d in A["PER_LAW"].items():
        m=d["M1_above_support_ceiling"]
        if not m: a("| `%s` | none | — | 0 | 0 | — | — | — | NO_EXPOSURE |"%law); continue
        a("| `%s` | %s | %d | %d | %d | %s | [%s, %s] | [%s, %s] | %s |"%(law,
          ",".join(str(x) for x in m["strata"][:12])+("…" if len(m["strata"])>12 else ""),
          m["k"],m["n"],m["contributing_worlds"],f6(m["rate"]),
          f6(m["exact_95_CI"][0]),f6(m["exact_95_CI"][1]),
          f6(m["world_clustered_95_CI"][0]),f6(m["world_clustered_95_CI"][1]),
          m.get("DIRECTLY_MEASURED")))
    a("\nPTOPD01 could not obtain this object above n = 5 at all: its numerators were visible in the")
    a("pooled episode table — hundreds of episodes beginning above occupancy 5 — but no archive")
    a("anywhere recorded the single-centre EXPOSURE that is its denominator. That denominator is")
    a("M4 below, and it is recorded here by construction.\n")
    a("### e(n), stratum by stratum\n")
    for law,d in A["PER_LAW"].items():
        a("**`%s`**\n"%law)
        a("| n | forks | exposure | worlds | e(n) | exact 95 % CI | world-clustered | support |")
        a("|---:|---:|---:|---:|---:|---|---|---|")
        for n_,v in sorted(d["M1_by_occupancy"].items(),key=lambda kv:int(kv[0])):
            a("| %s | %d | %d | %d | %s | [%s, %s] | [%s, %s] | %s |"%(n_,v["k"],v["n"],
              v["contributing_worlds"],f6(v["rate"]),f6(v["exact_95_CI"][0]),f6(v["exact_95_CI"][1]),
              f6(v["world_clustered_95_CI"][0]),f6(v["world_clustered_95_CI"][1]),
              "DIRECT" if v.get("DIRECTLY_MEASURED") else "THIN"))
        a("")
    a("## 4. M4 — the single-centre time exposure\n")
    a("| law | single-centre steps | above n=5 | worlds with exposure above n=5 | max occupancy | median horizon fraction |")
    a("|---|---:|---:|---:|---:|---:|")
    for law,d in A["PER_LAW"].items():
        m=d["M4_single_centre_exposure"]
        a("| `%s` | %d | %d | %d | %d | %s |"%(law,m["single_centre_steps_total"],
          m["steps_above_support_ceiling"],m["worlds_with_exposure_above_the_ceiling"],
          m["max_single_centre_occupancy"],f6(m["median_horizon_fraction_single_centre"])))
    a("")
    a("## 5. M2 — the occupation-resolved maturation law s(n)\n")
    for law,d in A["PER_LAW"].items():
        a("**`%s`**\n"%law)
        a("| n at separation | matured | episodes | worlds | s(n) | exact 95 % CI | world-clustered | support |")
        a("|---:|---:|---:|---:|---:|---|---|---|")
        for n_,v in sorted(d["M2_by_occupancy_at_separation"].items(),key=lambda kv:int(kv[0])):
            a("| %s | %d | %d | %d | %s | [%s, %s] | [%s, %s] | %s |"%(n_,v["k"],v["n"],
              v["contributing_worlds"],f6(v["rate"]),f6(v["exact_95_CI"][0]),f6(v["exact_95_CI"][1]),
              f6(v["world_clustered_95_CI"][0]),f6(v["world_clustered_95_CI"][1]),
              "DIRECT" if v.get("DIRECTLY_MEASURED") else "THIN"))
        a("")
    a("## 6. M3 — P(trigger | matured)\n")
    a("| law | triggered | matured | rate | exact 95 % CI | world-clustered | failed on the deadline | failed on centre count | failed on the local-X ratio |")
    a("|---|---:|---:|---:|---|---|---:|---:|---:|")
    for law,d in A["PER_LAW"].items():
        m=d["M3_trigger_given_matured"]; fm=m["failure_modes"]
        a("| `%s` | %d | %d | %s | [%s, %s] | [%s, %s] | %d | %d | %d |"%(law,m["k"],m["n"],
          f6(m["rate"]),f6(m["exact_95_CI"][0]),f6(m["exact_95_CI"][1]),
          f6(m["world_clustered_95_CI"][0]),f6(m["world_clustered_95_CI"][1]),
          fm.get("deadline",0),fm.get("not_exactly_two_centres",0),fm.get("local_x_ratio",0)))
    a("")
    a("## 7. M5 — the integrated trigger-to-turnover rate, the selection statistic\n")
    a("| law | A matured | B triggered | C removal applied | D functional turnover | M5 = D/N | exact 95 % CI | one-sided lower 95 % |")
    a("|---|---:|---:|---:|---:|---:|---|---:|")
    for law,d in A["PER_LAW"].items():
        m=d["M5_integrated"]; c=m["counts"]; p=m["per_world"]
        a("| `%s` | %d | %d | %d | %d | %s | [%s, %s] | %s |"%(law,c["A"],c["B"],c["C"],c["D"],
          pct(p["k"],p["n"]),f6(p["exact_95_CI"][0]),f6(p["exact_95_CI"][1]),
          f6(p["one_sided_lower_95"])))
    a("")
    a("## 8. Eligibility for a later disjoint causal confirmation\n")
    a("Floor `F_INTEGRATED = %.17g`, the exact one-sided lower 95 %% bound on BPRTC01's published"%DZ.FLOOR["value"])
    a("3 of 256 post-removal functional complete turnovers at POINT_D10 — the only parent endpoint")
    a("matching M5 in kind, chosen by that stated principle before its value was computed.\n")
    a("| law | K | n | lower 95 % | E1 | E2 | E3 | E4 | E5 | E6 | eligible | confirmation n | clears the stronger reference |")
    a("|---|---:|---:|---:|---|---|---|---|---|---|---|---:|---|")
    for law,e in A["ELIGIBILITY"].items():
        c=list(e["CLAUSES"].values())
        a("| `%s` | %d | %d | %s | %s | %s | %s | %s | %s | %s | **%s** | %s | %s |"%(law,e["K"],
          e["n"],f6(e["lower_95"]),*["✓" if x else "✗" for x in c],e["ELIGIBLE"],
          g(e["confirmation_n_required"]),e["CLEARS_THE_STRONGER_TURNOVER_REFERENCE"]))
    a("")
    a("## 9. What this does NOT establish\n")
    a("```")
    for k,v in V["UNCONDITIONAL"].items(): a("%-46s = %s"%(k,v))
    a("```")
    a("Claim ceiling: *the named objects have been measured at the laws and occupancies stated.*")
    a("Nothing about reproduction, heredity, autonomous cohesion or life follows from any number")
    a("above, and no point is qualified by this mission. Forbidden vocabulary is unchanged:")
    a("*organism*, *daughter organism*, *life created*, *self-replication demonstrated*.\n")
    a("## 10. Declared limitations\n")
    a("- At `LAW_B_POINT_D10` the design was **underpowered before world 1** against its own")
    a("  inherited expectation: BPRTC01 measured this exact chain at this exact law as 3 of 256,")
    a("  and p\\*(128) exceeds that. This was stated in the pre-run methods and is not repaired here.")
    a("- M1, M2, M3 and M4 have units that repeat within a world. Both the naive exact interval and")
    a("  the world-clustered interval are published; **only the clustered one may support a claim**.")
    a("- No law is pooled with another inside any gate. Where two laws populate the same stratum the")
    a("  two measurements are shown side by side and neither transports to the other. MCTT01")
    a("  established that the fork-to-trigger conversion does not transport in kY.")
    a("- Strata with no exposure are reported as NO_EXPOSURE and are never filled in.\n")
    return "\n".join(L)+"\n"

if __name__=="__main__":
    open(f"{OUT}/TLMR01_FINAL_REPORT.md","w").write(report())
    print("report written")
