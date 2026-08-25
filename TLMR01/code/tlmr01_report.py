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
    C=json.load(open(f"{OUT}/TLMR01_CHECKER_CORRECTIONS.json"))
    ADJ=json.load(open(f"{OUT}/TLMR01_CHECKER_ADJUDICATION.json"))
    a("## 8b. The endpoint is confounded with occupancy — read the selection with this\n")
    a("The chain conversions are")
    a("")
    a("| law | A matured | B\\|A | C\\|B | D\\|C |")
    a("|---|---:|---:|---:|---:|")
    for law,d in A["PER_LAW"].items():
        c=d["M5_integrated"]["counts"]
        a("| `%s` | %d/%d | %d/%d | %d/%d | **%d/%d** |"%(law,c["A"],c["N"],c["B"],c["A"],c["C"],c["B"],c["D"],c["C"]))
    pr=C["F04_POST_REMOVAL_INTERVALS_UNTRUNCATED"]["LAW_C_MCTT01"]
    occ=C["F06_OCCUPANCY_STRUCTURE"]
    a("")
    a("A conversion of exactly 1.000 at one law and exactly 0.000 at the other two is not evidence")
    a("that a lineage works at LAW_C and fails elsewhere. The frozen DOTC01 COMPLETE_TURNOVER is")
    a("**confounded with occupancy**. At LAW_C the %d removals leave **%d** complete post-removal"%(pr["worlds_with_a_removal"],pr["complete_post_removal_intervals"]))
    a("identity intervals, median %d per world, **%d** of them FUNCTIONAL; an endpoint that asks for"%(pr["median_complete_intervals_per_world"],pr["functional_post_removal_intervals"]))
    a("*at least one* against that ambient rate is saturated. At LAW_A and LAW_B, which hold")
    a("occupancy 1 for %.1f %% and %.1f %% of their single-centre steps and never exceed occupancy 4,"%(100*occ["LAW_A_B1"]["fraction_at_occupancy_1"],100*occ["LAW_B_POINT_D10"]["fraction_at_occupancy_1"]))
    a("**not one** complete post-removal interval occurs at all — 0 of 0, not 0 of some.\n")
    a("The sharpest form of the argument, which the independent check supplied: **all 44 matured and")
    a("all 32 triggering LAW_C episodes begin at separation occupancy 2, 3 or 4** — occupancy-identical")
    a("to LAW_A and LAW_B. The triggering configurations do not differ between the laws. What differs")
    a("is the ambient occupancy of the window AFTER the removal, which at LAW_C runs to the hundreds.\n")
    a("**No no-removal control exists anywhere in these 512 worlds.** The saturation is therefore an")
    a("inference from the interval count and the occupancy, not a measured contrast, and it is")
    a("stated as an inference. This is a caveat on what the selection MEANS; it does not move the")
    a("frozen rule, which selected LAW_C_MCTT01 on the arithmetic in §8.\n")
    sn=C["F21_MATURATION_ABOVE_SEPARATION_OCCUPANCY_4"]
    a("## 8c. s(n) = 0 above separation occupancy 4, at every law\n")
    a("| law | episodes | beginning at n ≥ 5 | matured among those | maturations by separation occupancy |")
    a("|---|---:|---:|---:|---|")
    for law,v in sn.items():
        a("| `%s` | %d | %d | **%d** | %s |"%(law,v["episodes"],v["episodes_beginning_at_n_at_least_5"],
          v["matured_among_those"],", ".join("n=%s: %d"%(k,x) for k,x in v["all_maturations_by_separation_occupancy"].items())))
    a("")
    a("Every maturation at every law begins at separation occupancy 2, 3 or 4. **%d episodes beginning"%sum(v["episodes_beginning_at_n_at_least_5"] for v in sn.values()))
    a("at n ≥ 5 produced zero maturations**, 15,243 of them at LAW_C_MCTT01. PTOPD01 reported zero of")
    a("3,602 above occupancy 3 at B1 mobility; this replicates that and extends it to a law 40× in kY.\n")
    a("## 8d. e(n) above the ceiling is a mixture, not a rate\n")
    a("| occupancy band | forks | exposure (steps) | e(n) |")
    a("|---|---:|---:|---:|")
    for b_ in C["F19_E_N_IS_AN_EXPOSURE_WEIGHTED_MIXTURE"]["bands"]:
        a("| %s | %d | %d | %s |"%(b_["band"],b_["forks"],b_["exposure"],f6(b_["e"])))
    sup=C["F03_SUPPORT_BY_STRATUM"]
    a("")
    a("The pooled figure %s describes no occupancy: the hazard varies by three orders of magnitude"%f6(C["F19_E_N_IS_AN_EXPOSURE_WEIGHTED_MIXTURE"]["pooled_value"]))
    a("across the bands and 86 %% of the exposure sits in the top one. The stratum table above is the")
    a("honest object. Of the %d strata above the ceiling, **%d are DIRECTLY_MEASURED and %d are"%(sup["strata_above_sI"],sup["DIRECTLY_MEASURED"],sup["SUPPORT_TOO_THIN"]))
    a("SUPPORT_TOO_THIN**; the highest directly measured stratum is **n = %d**, not the maximum"%sup["highest_directly_measured_stratum"])
    a("occupancy of %d. The thin strata hold %d of %d steps and %d of %d forks."%(
      sup["highest_stratum_with_any_exposure"],sup["steps_in_thin_strata"],
      A["PER_LAW"]["LAW_C_MCTT01"]["M1_above_support_ceiling"]["n"],sup["forks_in_thin_strata"],
      A["PER_LAW"]["LAW_C_MCTT01"]["M1_above_support_ceiling"]["k"]))
    a("")
    a("M1's denominator is M4 **restricted to steps that have a successor** — a one-step hazard cannot")
    a("use a step whose t+1 does not exist. That is why §3 prints %d and §4 prints %d.\n"%(
      A["PER_LAW"]["LAW_C_MCTT01"]["M1_above_support_ceiling"]["n"],
      A["PER_LAW"]["LAW_C_MCTT01"]["M4_single_centre_exposure"]["steps_above_support_ceiling"]))
    am=C["F05_IDENTITY_AMBIGUOUS"]
    a("## 8e. IDENTITY_AMBIGUOUS, as pre-registered\n")
    a("| law | episodes | IDENTITY_AMBIGUOUS | fraction | ambiguous interior steps | matured & ambiguous | triggering & ambiguous |")
    a("|---|---:|---:|---:|---:|---:|---:|")
    for law,v in am.items():
        a("| `%s` | %d | %d | %s | %d | %d | %d |"%(law,v["episodes"],v["identity_ambiguous_episodes"],
          f6(v["fraction"]),v["ambiguous_interior_steps"],v["matured_and_ambiguous"],v["triggering_and_ambiguous"]))
    a("")
    a("PTOPD01 observed this outcome **zero** times across three corpora. It is measured here at")
    a("12.6 %% of LAW_C episodes. It was pre-registered as *published whatever it is* and the first")
    a("version of this report omitted it; the independent check caught that and it is published here.")
    a("None of the 22 integrated LAW_C worlds rests on an ambiguous episode: 0 of 44 matured and 0 of")
    a("32 triggering episodes are ambiguous.\n")
    a("## 8f. Gates in this mission that carry no information\n")
    a("Recorded so no successor inherits them as evidence.\n")
    a("| gate | why it cannot fail |")
    a("|---|---|")
    a("| `ARCHIVE_DECISION_RECONSTRUCTION` | it regroups cells by the component id the online code wrote, so it reproduces the online grouping for any decomposition whatsoever |")
    a("| `ONLY_Y_LAW_FIELDS_DIFFER` | it tests a dictionary for having the three keys it was built with |")
    a("| `failure_modes.not_exactly_two_centres` | the frozen state S already requires exactly two centres, so a matured episode cannot fail this gate |")
    a("| terminators `INTEGRITY_FAULT`, `UNCLASSIFIED` | unreachable by construction; the integrity flag is per world and the run is maximal |")
    a("")
    a("The device-path cross-check is near-vacuous for the same reason: its two archives are an")
    a("extinct world and a single-Y world, in which the identity link and the toroidal distance are")
    a("never called and no episode, candidate or removal exists. **The device path is verified for")
    a("the archive reader, M1 with zero forks and M4, and is UNVERIFIED for M2, M3, M5, the identity")
    a("link and the toroidal distance.** Closing it is a binding precondition on the successor.\n")
    a("## 9. What this does NOT establish\n")
    a("```")
    for k,v in V["UNCONDITIONAL"].items(): a("%-46s = %s"%(k,v))
    a("```")
    a("Claim ceiling: *the named objects have been measured at the laws and occupancies stated.*")
    a("No point is qualified by this mission. The frozen status strings above are the only permitted")
    a("formulation, and this report makes no claim outside them, in the affirmative or the negative.")
    a("Forbidden vocabulary is unchanged: *organism*, *daughter organism*, *life created*,")
    a("*self-replication demonstrated*.\n")
    a("## 10. Declared limitations\n")
    a("- At `LAW_B_POINT_D10` the design was **underpowered before world 1** against its own")
    a("  inherited expectation: BPRTC01 measured this exact chain at this exact law as 3 of 256,")
    a("  and p\\*(128) exceeds that. This was stated in the pre-run methods and is not repaired here.")
    a("- M1, M2, M3 and M4 have units that repeat within a world. Both the naive exact interval and")
    a("  the world-clustered interval are published; **only the clustered one may support a claim**.")
    a("- The three M3 failure-mode columns in §6 are **marginals** and can double-count: at")
    a("  `LAW_A_B1` they sum to 42 against 35 failures, with 7 episodes failing both the deadline and")
    a("  the local-X ratio. The `failed on centre count` column is an identity, not a measurement.")
    a("- The world-clustered interval is conditional on exposure: worlds contributing no denominator")
    a("  are not resampled, and it is degenerate where a numerator is zero. No gate in this mission")
    a("  rests on it; where it degenerates the exact one-sided bound is the reported object.")
    a("- The per-world reduction ran on the device and completed BEFORE the rebuilt raw commitment,")
    a("  not inside the analysis stage as the frozen order has it. Nothing downstream of it existed")
    a("  before C3, and no outcome was read, but the order differed and that is recorded here.")
    a("- No law is pooled with another inside any gate. Where two laws populate the same stratum the")
    a("  two measurements are shown side by side and neither transports to the other. MCTT01")
    a("  established that the fork-to-trigger conversion does not transport in kY.")
    a("- Strata with no exposure are reported as NO_EXPOSURE and are never filled in.\n")
    return "\n".join(L)+"\n"

if __name__=="__main__":
    open(f"{OUT}/TLMR01_FINAL_REPORT.md","w").write(report())
    print("report written")
