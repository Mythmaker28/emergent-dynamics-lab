"""CLEA01 closure §1, §2 and §3 — preserve, scope-audit and adjudicate the one checker.

The checker return already existed at CLEA01/review/CLEA01_CHECKER_RAW.txt, written and hashed
before any finding was acted on, and committed at C3. Nothing here rewrites it: this file parses it,
structures it, audits what the checker did, and adjudicates each numbered finding exactly once.

One thing this file corrects about my own earlier record. The C3 adjudication reported TEN accepted
corrections. The checker returned SEVENTEEN numbered findings. The ten covered the corrective
content of eight of them, but four items were never adjudicated in writing at all — including one
MATERIAL finding, number 15. Under-counting a finding list is exactly the failure the closure
launcher asks to be fixed, so all seventeen are adjudicated here and the discrepancy is recorded
rather than quietly absorbed.
"""
from __future__ import annotations
import datetime as dt, json, os, re, subprocess, sys
REPO = os.environ.get("CLEA01_REPO", "/home/claude/edl")
sys.path.insert(0, f"{REPO}/OMLDCT02/code")
import omldct02_hashes as H

RAW = f"{REPO}/CLEA01/review/CLEA01_CHECKER_RAW.txt"
OUT = f"{REPO}/CLEA01/out"
REV = f"{REPO}/CLEA01/review"

TWELVE_MANDATED = ["parent binding", "the A/B/C definitions", "causal-edge validity",
                   "absence of hidden online IDs", "non-vacuity",
                   "ambient false-positive rejection", "known-success preservation",
                   "split manifest chronology", "validation-set isolation",
                   "two independent implementations", "causal-emergence estimator",
                   "terminal disposition"]

AREAS = ["parent binding", "Models A/B/C", "transport kernel", "causal-edge validity",
         "hidden-ID exclusion", "non-vacuity", "ambient specificity",
         "known-success preservation", "split chronology", "validation isolation",
         "implementation independence", "structural gates", "terminal disposition"]

NONE = "no effect"

F = [
 dict(id=1, title="PARENT BINDING", severity="NONE", verdict="ACCEPTED",
      arith="805 ledger rows with next_index 805; 33 ADMISSIBLE; TARGET_VALID_PAIRED_BLOCKS = 41; "
            "round(running + cost, 5) accumulation reproducing 510.56902 exactly, naive float sum "
            "510.56902000000395, exact rational 510569/1000; MAX_PRIMARY_ARM_INSTANCES = 512; no "
            "row with technical_failure; 13 adjudication items with LOAD_BEARING_DEFECT_COUNT 0; "
            "66 of 66 archive hashes matching the sealed record.",
      effect={"parent binding": "confirms it"}, minimum="none",
      taken="re-verified independently in section 4 of this closure. All six numbers reproduce "
            "from the sealed ledger and the runner AST, without reading an OMLDCT02 summary."),
 dict(id=2, title="THE A/B/C DEFINITIONS", severity="NONE", verdict="ACCEPTED",
      arith="B_exposure minus C_possible_exposure ranges 2 to 1,891,199 over 66 arms, so POSSIBLE "
            "never equals B and the bracket is not vacuous.",
      effect={"Models A/B/C": "confirms three distinct objects; B is not a straw man"},
      minimum="none", taken="recorded. The finding that B is defined generously against my own "
                            "hypothesis is carried into the report."),
 dict(id=3, title="CAUSAL-EDGE VALIDITY", severity="NONE", verdict="ACCEPTED",
      arith="net displacement (a-b, c-d) with a,b,c,d in {0,1} over the four frozen sub-shifts; "
            "0 archive invariant violations; row cadence one tl_record per _one_step; event label "
            "t+1 for the transition t to t+1; pair = nX * nY elementwise.",
      effect={"transport kernel": "confirms it in both directions",
              "causal-edge validity": "confirms it",
              "non-vacuity": "supplies the soundness of CERTAIN, which I had not stated"},
      minimum="state the soundness consequence, which is load-bearing and which I omitted",
      taken="stated in C3 and re-established here mechanically in section 5: the displacement set "
            "is DERIVED from the sub-shifts by subset sum and equals Moore-1 exactly, and it is "
            "MEASURED from 25,577 single-source archive rows as exactly nine offsets with maximum "
            "Chebyshev 1."),
 dict(id=4, title="ABSENCE OF HIDDEN ONLINE IDs — evidence overstated", severity="MATERIAL",
      verdict="ACCEPTED",
      arith="the G7 scan covered 2 of 7 scripts; stripping string literals makes a dict field "
            "access invisible, so clea01_assemble.py reported 'executable-code hits: []' while "
            "containing [\"E3_DURATION\"], [\"E3_EXPOSURE\"], [\"identity_termination_type\"] and "
            "[\"PAIR_MEASUREMENTS\"].",
      effect={"hidden-ID exclusion": "the conclusion stands; the stated basis did not support it",
              "structural gates": "G7's BASIS rewritten; verdict unchanged"},
      minimum="replace the scan with one that treats string literals as USE, over every script",
      taken="section 6 of this closure replaces it entirely: an AST scan over all scripts where "
            "string literals COUNT as use and only docstrings count as mention, plus a runtime "
            "probe that wraps numpy.load and records the archive keys each implementation actually "
            "requests. Both implementations touch exactly c_t, c_y, c_x, c_nY, meta, ybirth, "
            "ydeath, xbirth — zero forbidden keys."),
 dict(id=5, title="NON-VACUITY — confirmed; G3 argued by magnitude", severity="MATERIAL (wording)",
      verdict="ACCEPTED",
      arith="33 of 33 SELECTIVE arms have exactly 2 components at t_m with 'other' mass 0; "
            "C_minus_B_exposure equals minus the parent's fork-row mass in 33 of 33; C's CERTAIN "
            "duration equals B's duration in 33 of 33; row-walking six pairs gives CERTAIN equal to "
            "the full occupied set on 100.0% of post-fork rows (10,247 / 10,218 / 10,125 / 9,893 / "
            "9,730 / 10,444) against 0.0% in the same six SHAM arms.",
      effect={"non-vacuity": "strengthened", "structural gates": "G3's basis restated without a "
              "magnitude judgement", "terminal disposition": "unchanged"},
      minimum="restate G3's FAIL in threshold-free terms",
      taken="done in C3 and carried here. G3 now fails on the set identity, not on a particle "
            "count. Section 7 additionally supplies the qualitative structural exhibit the closure "
            "launcher requires, so non-vacuity versus A no longer rests on a ratio either."),
 dict(id=6, title="AMBIENT FALSE-POSITIVE REJECTION", severity="NONE", verdict="ACCEPTED",
      arith="POST_A_CLAIM_FRACTION re-implemented from scratch, 0 disagreements on 66 arms; "
            "exactly 1.0 in exactly 31 SELECTIVE arms, undefined in 2 (450, 482) where post-A world "
            "mass is zero; parent_emptied and daughter_untouched true 33/33; SHAM median 0.00745.",
      effect={"ambient specificity": "confirms PASS_ON_SHAM / NOT_TESTABLE_ON_SELECTIVE"},
      minimum="none",
      taken="section 9 of this closure adds the interval accounting the launcher asks for and does "
            "not stop the walk when POSSIBLE empties, so rejected ambient mass is counted rather "
            "than truncated."),
 dict(id=7, title="KNOWN-SUCCESS PRESERVATION — my explanation understated it", severity="MATERIAL",
      verdict="ACCEPTED",
      arith="402 SHAM rows 1153-1155, cells (8,27), (11/12,29), (14,32), (16,31); 518 SHAM rows "
            "1521-1526, cells (30,17/18), (32,17), (33,17). Each has |S| = 1, its single source is "
            "non-CERTAIN, and it was never CERTAIN and never POSSIBLE at any earlier row.",
      effect={"known-success preservation": "G4 FAIL confirmed and its meaning escalated",
              "Models A/B/C": "Model A's CORE_R centroid rule absorbs mass with no causal path",
              "parent binding": "a finding against OMLDCT02's E3 component, recorded, changing no "
                                "OMLDCT02 number"},
      minimum="state that the cells have NO causal path, not merely uncertain origin, and escalate "
              "it beyond a gate footnote",
      taken="done in C3; and section 8 of this closure republishes both arms row by row and "
            "recomputes, for every missing cell, whether it was EVER CERTAIN or EVER POSSIBLE at "
            "any row. All are false, independently reproducing the checker."),
 dict(id="7b", title="clea01_g4_containment.py written after the development sweep",
      severity="MINOR", verdict="ACCEPTED",
      arith="code mtime 20:19:47, development sweep 20:04:11, validation opened 20:22:31.",
      effect={"known-success preservation": "the strong containment form is post-hoc",
              "validation isolation": "written before validation opened, so the rule holds"},
      minimum="declare it",
      taken="declared in section 10 of this closure, with the direction noted: the test cost me two "
            "gate failures, so it is post-hoc but not self-serving. NOT adjudicated in the C3 "
            "record — that omission is recorded below."),
 dict(id=8, title="SPLIT MANIFEST CHRONOLOGY", severity="NONE", verdict="ACCEPTED",
      arith="SHA256(tip + '|CLEA01|' + str(seed)) reproduces 33 of 33 digest prefixes; sorting by "
            "the first 64 bits with index tie-break and cutting at 22 reproduces the assignment "
            "with zero disagreements. Under 4 of 6 alternative encodings index 402 lands in "
            "DEVELOPMENT, which would have made G8 a clean PASS; the encoding used is one of the "
            "two that puts the contradiction in VALIDATION.",
      effect={"split chronology": "confirms it; the encoding choice went against me"},
      minimum="none",
      taken="section 10 recomputes the split from scratch: 33 of 33 prefixes and 0 assignment "
            "disagreements, plus a content check that needs no timestamp at all."),
 dict(id=9, title="VALIDATION-SET ISOLATION — two audit-trail gaps", severity="MATERIAL",
      verdict="ACCEPTED",
      arith="mtime chain 19:52 binding, 19:54:34 models, 19:54:55 split, 19:55 i2, 19:56 i1, "
            "19:57 run, 19:57:27 graph, 20:04 dev sweep, 20:12 specificity code, 20:13 dev spec, "
            "20:19 fixtures and G4 code, 20:22-20:23 validation opened. git status reported '?? "
            "CLEA01/' — the whole mission uncommitted.",
      effect={"validation isolation": "substance intact, audit trail absent",
              "split chronology": "ordering rested on mtimes I control"},
      minimum="externalise the post-hoc disclosure; commit the mission",
      taken="both done. The disclosure is in the artefacts since C2 and is restated in section 10. "
            "The mission is committed C1-C4 and this closure adds a fifth. A NEW cost is recorded "
            "in section 10: re-digesting four artefacts at 21:08 overwrote their original mtimes, "
            "so that evidence now survives only inside the checker's pre-overwrite return."),
 dict(id=10, title="TWO IMPLEMENTATIONS — independence overstated", severity="MATERIAL",
      verdict="ACCEPTED",
      arith="i1 and i2 share 28 non-trivial identical source lines by the checker's count, 35 by "
            "the difflib measure in section 11: led(), the _n_groups flood-fill body, the archive "
            "extraction lines, the loop skeleton, break conditions, duration and exposure "
            "accounting and the output dictionary. A third implementation written from the rule "
            "text by neighbour counting agrees on all 13 quantities on all 66 arms.",
      effect={"implementation independence": "G2 tests the propagation operator only",
              "structural gates": "G2 verdict unchanged, scope narrowed"},
      minimum="withdraw the 'no code' claim and state what G2 actually tests",
      taken="withdrawn in C3. Section 11 measures the overlap instead of asserting anything, and "
            "records SCIENTIFICALLY_INDEPENDENT = false, EQUIVALENT_ENCODINGS = true."),
 dict(id="10b", title="the equivalence proof omits its precondition", severity="MINOR",
      verdict="ACCEPTED",
      arith="4000 random configurations: 0 mismatches between the literal rule text, i1, i2 and a "
            "counting route. 2000 configurations with CERTAIN not contained in occ_prev: the "
            "checker got 2000 of 2000 mismatching; my own generator, which breaks the precondition "
            "only probabilistically, gets 1721 of 2000. Both show the identity is conditional.",
      effect={"implementation independence": "the equivalence holds only under CERTAIN subset occ"},
      minimum="state the precondition with the proof",
      taken="stated in section 11, with my own 1721/2000 reported rather than the checker's cleaner "
            "number, because my generator is the one I ran. NOT adjudicated in the C3 record."),
 dict(id=11, title="CAUSAL-EMERGENCE ESTIMATOR NOT COMPUTED", severity="NONE", verdict="ACCEPTED",
      arith="in the SELECTIVE arm the lineage and ambient macrostates are the same partition on "
            "every post-fork row, so the comparison is degenerate in the treated arm.",
      effect={"structural gates": "the substantive reason is stronger than the procedural one"},
      minimum="give the substantive reason as well as the procedural one",
      taken="both are given, in C3 and in CLEA01_CAUSAL_EMERGENCE_FINAL_STATUS.json."),
 dict(id=12, title="TERMINAL DISPOSITION — selection correct", severity="NONE", verdict="ACCEPTED",
      arith="terminal 2 names the LOCKED COMPONENT; C differs from A in 62 of 66 arms by a median "
            "duration factor of 22.8 and a maximum of 10,667, and in 2 arms A is not contained in "
            "C. C's failure is against B, not against A.",
      effect={"terminal disposition": "confirms the third string"},
      minimum="none", taken="the terminal is unchanged by this closure."),
 dict(id="12b", title="the gate scoring is softer than it reads", severity="MINOR",
      verdict="ACCEPTED",
      arith="scored literally G3 would PASS, since C differs from B numerically in 66 of 66; and "
            "G5 sits inside N_PASS = 6 while being untestable on the arm that matters, which is "
            "what G9 is failed for.",
      effect={"structural gates": "the headline 'six pass, three fail' overstates the pass side"},
      minimum="say so where the gates are scored",
      taken="CLEA01_STRUCTURAL_GATES_FINAL.json now reports N_UNQUALIFIED_PASS separately from "
            "N_PASS and marks G5 as NOT_IDENTIFIABLE on the treated arm rather than counting it "
            "whole. G3's FAIL is restated on the set identity so that it no longer depends on a "
            "magnitude reading. NOT adjudicated in the C3 record."),
 dict(id=13, title="TEST_1's explanatory note is factually wrong", severity="MATERIAL",
      verdict="ACCEPTED",
      arith="(10, SHAM): C ends at 951 while B runs 10,247 with exposure 1,172,068. (471, SHAM): C "
            "ends at 119 while B runs 1,028. Only (450, SELECTIVE) and (482, SELECTIVE) fit the "
            "note. C_equals_B is False for all 66 arms.",
      effect={"non-vacuity": "the 62/66 verdict stands; the attached explanation was wrong for two "
                             "of the four cases it explained"},
      minimum="correct the note and publish the four rows",
      taken="corrected in C2/C3 with all four rows published in "
            "CLEA01_NONVACUITY_AND_SPECIFICITY.json."),
 dict(id=14, title="seven of ten artefacts have no generating script", severity="MATERIAL",
      verdict="ACCEPTED",
      arith="only CLEA01_MATCHED_PAIR_MODEL_COMPARISON.{json,csv} and "
            "CLEA01_IDENTITY_DISAGREEMENT_LEDGER.csv came from committed code. All seven "
            "*_CONTENT_HASH fields nevertheless reproduce under the parent's canonical rule.",
      effect={"validation isolation": "provenance not reproducible from code",
              "structural gates": "no gate number is wrong"},
      minimum="declare it; do not let it recur",
      taken="declared at C3 and carried forward unchanged — the seven original artefacts still have "
            "no generating script and that is not retro-fitted. Every artefact produced by this "
            "closure has one: nine committed scripts produce all of them."),
 dict(id=15, title="the launcher is absent from the repository", severity="MATERIAL",
      verdict="ACCEPTED",
      arith="no CLEA01 launcher, handoff or section text anywhere in /home/claude/edl or "
            "/home/claude. The ten gates, the section-8 gating rule and the four terminal strings "
            "existed only in the operator's prose.",
      effect={"structural gates": "unverifiable by any checker",
              "terminal disposition": "the permitted vocabulary was unverifiable"},
      minimum="put the launcher under version control",
      taken="CLOSED. Both launchers are committed at CLEA01/launcher/ — the audit launcher verbatim "
            "and the closure launcher transcribed with a transcription note. A reader can now check "
            "the gate list, the gating rule and the four terminal strings against the source. This "
            "finding was NOT adjudicated in the C3 record; it is the one MATERIAL finding the ten "
            "corrections missed."),
 dict(id=16, title="G6's headline is dominated by the degenerate arm", severity="MINOR",
      verdict="ACCEPTED",
      arith="checker's partition by ARM: 288,398 of 373,987 split rows (77%) and 35,476 of 42,593 "
            "replacements (83%) come from SELECTIVE; the SHAM remainder is 85,589 rows across 28 "
            "arms and 7,117 replacements across 27. My partition by SATURATION: 335,930 split rows "
            "and 41,189 replacements come from the 36 arms with claim fraction 1.0, leaving 37,944 "
            "rows across 23 arms and 1,404 replacements across 22 in non-saturating SHAM arms. "
            "Both partitions are exact and sum to the same totals; mine is the stricter one because "
            "it also removes the five saturating SHAM arms.",
      effect={"structural gates": "G6 PASS survives on either partition; the headline was inflated"},
      minimum="report the non-degenerate figures",
      taken="reported since C2. The two partitions are reconciled explicitly here so the difference "
            "between my number and the checker's is not mistaken for a disagreement."),
 dict(id=17, title="'downstream X production' overstates the attribution", severity="MINOR",
      verdict="ACCEPTED",
      arith="an accepted X birth at d requires nX(d) > 0 and nSX(d) > 0 as well as nY(d) > 0, and "
            "X diffuses at p_hop_X = 1.0.",
      effect={"ambient specificity": "the number is right, the wording claimed more"},
      minimum="reword",
      taken="reworded at C2/C3: the quantity measures X births CATALYSED AT CELLS whose Y is "
            "certainly lineage."),
]

C3_TEN = {4, 5, 7, 9, 10, 13, 14, 16, 17}
MISSED_BY_C3 = ["7b", "10b", "12b", 15]


def parse_raw():
    txt = open(RAW, encoding="utf-8").read()
    heads = re.findall(r"\*\*(\d+)\.\s+(.+?)\s+—\s+SEVERITY:\s+([A-Z]+)", txt)
    verdict = txt.split("**CHECKER_VERDICT =", 1)[1].strip().rstrip("*").strip() if \
        "**CHECKER_VERDICT =" in txt else None
    lbd = re.search(r"\*\*LOAD_BEARING_DEFECT_COUNT\s*=\s*(\d+)\*\*", txt)
    return txt, heads, verdict, (int(lbd.group(1)) if lbd else None)


def main():
    txt, heads, verdict, lbd = parse_raw()
    sha = H.file_sha256(RAW)

    status = {
        "MISSION": "CLEA01", "SECTION": "1 — checker return status",
        "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
        "RETURN_PATH": "CLEA01/review/CLEA01_CHECKER_RAW.txt",
        "RETURN_SHA256": sha,
        "RETURN_LINES": txt.count("\n") + 1, "RETURN_BYTES": len(txt.encode()),
        "RECOVERED_VERBATIM": True,
        "WRITTEN_AND_HASHED_BEFORE_ANY_FINDING_WAS_ACTED_ON": True,
        "COMMITTED_AT": subprocess.run(
            ["git", "-C", REPO, "log", "--format=%H", "-1", "--",
             "CLEA01/review/CLEA01_CHECKER_RAW.txt"], capture_output=True, text=True).stdout.strip(),
        "NOTHING_WAS_RECONSTRUCTED_FROM_MEMORY": True,
        "HOW_THAT_IS_KNOWN": "the file has not changed since it was written: its sha256 is the same "
                             "value recorded in the C3 adjudication and in the C4 external "
                             "manifest, and git shows a single commit touching it.",
        "NUMBERED_FINDINGS_PARSED_FROM_THE_RETURN": len(heads),
        "CHECKER_VERDICT_PRESENT": verdict is not None,
        "LOAD_BEARING_DEFECT_COUNT": lbd,
        "RECOMMENDED_TERMINAL_DISPOSITION_SUPPLIED": True,
        "RECOMMENDED_TERMINAL":
            "CAUSAL_LINEAGE_NOT_IDENTIFIABLE_FROM_EXISTING_ARCHIVES__LINEAGE_ROUTE_PAUSED",
    }
    status["RETURN_STATUS_CONTENT_HASH"] = H.content_digest(
        status, extra_excluded=("RETURN_STATUS_CONTENT_HASH",))
    json.dump(status, open(f"{OUT}/CLEA01_CHECKER_RETURN_STATUS.json", "w"), indent=1)

    def touched(a, b):
        r = subprocess.run(["find", REPO, "-path", f"{REPO}/.git", "-prune", "-o",
                            "-type", "f", "-newermt", a, "!", "-newermt", b, "-print"],
                           capture_output=True, text=True).stdout.split()
        return [p.replace(REPO + "/", "") for p in r]

    win = ("2026-08-26 20:37:00", "2026-08-26 21:06:30")
    scope = {
        "MISSION": "CLEA01", "SECTION": "2 — checker scope audit",
        "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
        "WINDOW": {"from": win[0], "to": win[1],
                   "why": "the audit's last artefact is 20:36:59 and the checker return was written "
                          "at 21:06:20. Anything the checker touched in the repository must fall in "
                          "between."},
        "REPOSITORY_FILES_TOUCHED_IN_THE_WINDOW": touched(*win),
        "MODIFIED_NO_REPOSITORY_FILE": True,
        "MODIFIED_NO_REPOSITORY_FILE_QUALIFIED":
            "the only two paths in the window are the checker's own return, which I wrote, and a "
            "__pycache__ .pyc left by re-running clea01_fixtures.py, which the checker reports "
            "doing. A bytecode cache is not a source or artefact modification. No CLEA01 code, no "
            "CLEA01 artefact and no OMLDCT02 file was altered.",
        "CONSTRUCTED_NO_WORLD": False,
        "RAN_NO_ENGINE": False,
        "THE_ONE_SCOPE_EXCESS_AND_WHAT_IT_COSTS":
            "the checker's own return says it ran 4000 randomised single-cell trials under the "
            "frozen spec and 400 full _one_step calls. Those are engine runs and world "
            "constructions, and the mandate said neither. I do not soften that: it is a scope "
            "excess, self-declared by the checker, and it is recorded here rather than omitted "
            "because it flatters no one. What it does NOT do is contaminate the record. No archive "
            "was written anywhere after 20:00 — checked across the whole filesystem — the 66 "
            "OMLDCT02 archives are untouched, no seed from the manifest was drawn, and nothing in "
            "the terminal disposition rests on those trials: section 5 of this closure "
            "re-establishes the same kernel conclusion twice over without running anything, by "
            "deriving the displacement set from the engine source and by measuring it on 25,577 "
            "single-source archive rows.",
        "NO_NEW_ARCHIVE_ANYWHERE_AFTER_20_00": True,
        "OMLDCT02_RAW_ARCHIVES_TOUCHED": 0,
        "DREW_NO_SEED_FROM_THE_MANIFEST": "not independently verifiable from here; the checker "
            "describes the trials as randomised and no seed manifest file was read or written in "
            "the window. Stated as unverified rather than asserted.",
        "WROTE_SCRATCH_ONLY_OUTSIDE_THE_REPOSITORY": True,
        "TWELVE_MANDATED_POINTS": TWELVE_MANDATED,
        "FINDINGS_1_TO_12_MAP_ONTO_THEM_IN_ORDER": True,
        "ALL_TWELVE_ATTACKED": True,
        "EXTRA_FINDINGS_BEYOND_THE_TWELVE": [13, 14, 15, 16, 17],
        "EXACTLY_ONE_VERDICT_RETURNED": True,
        "NO_MISSING_LOAD_BEARING_ATTACK": True,
        "CONSEQUENCE": "no missing attack prevents the terminal disposition from being verified, so "
                       "section 2's CLEA01_TECHNICALLY_INVALID mapping is not triggered.",
    }
    scope["SCOPE_AUDIT_CONTENT_HASH"] = H.content_digest(scope, extra_excluded=("SCOPE_AUDIT_CONTENT_HASH",))
    json.dump(scope, open(f"{OUT}/CLEA01_CHECKER_SCOPE_AUDIT.json", "w"), indent=1)

    structured = {
        "MISSION": "CLEA01", "SECTION": "the checker return, structured",
        "SOURCE": "CLEA01/review/CLEA01_CHECKER_RAW.txt", "SOURCE_SHA256": sha,
        "NOTHING_HERE_REPLACES_THE_RAW_RETURN": True,
        "PARSED_HEADINGS": [{"n": int(a), "title": b, "severity": c} for a, b, c in heads],
        "LOAD_BEARING_DEFECT_COUNT": lbd,
        "CHECKER_VERDICT": verdict,
    }
    json.dump(structured, open(f"{REV}/CLEA01_CHECKER.json", "w"), indent=1)
    with open(f"{REV}/CLEA01_CHECKER.md", "w") as fh:
        fh.write("# CLEA01 — the independent checker, structured\n\n"
                 f"Verbatim return: `CLEA01/review/CLEA01_CHECKER_RAW.txt`, sha256 `{sha}`.\n"
                 "This file is an index into it. It replaces nothing.\n\n"
                 f"`LOAD_BEARING_DEFECT_COUNT = {lbd}`\n\n## Findings\n\n")
        for a, b, c in heads:
            fh.write(f"- **{a}. {b}** — severity {c}\n")
        fh.write(f"\n## Verdict\n\n{verdict}\n")

    adj = {
        "MISSION": "CLEA01", "SECTION": "3 — checker adjudication",
        "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
        "MAX_INDEPENDENT_CHECKERS": 1, "CHECKERS_DISPATCHED": 1, "REVIEW_CASCADE": "none",
        "CHECKER_RETURN_SHA256": sha,
        "LOAD_BEARING_DEFECT_COUNT": lbd,
        "I_ACCEPT_THE_CHECKER_IN_FULL": True,
        "N_ITEMS_ADJUDICATED": len(F),
        "EACH_ADJUDICATED_EXACTLY_ONCE": len({str(f["id"]) for f in F}) == len(F),
        "AREAS": AREAS,
        "ITEMS": [dict(f, effect_full={a: f["effect"].get(a, NONE) for a in AREAS}) for f in F],
        "A_CORRECTION_TO_MY_OWN_EARLIER_RECORD": {
            "what_C3_said": "TEN_CORRECTIONS_I_ACCEPT",
            "what_the_checker_returned": f"{len(heads)} numbered findings, of which eight are "
                                         "MATERIAL and five carry MINOR sub-items",
            "the_ten_covered": sorted(str(x) for x in C3_TEN),
            "never_adjudicated_in_writing_at_C3": [str(x) for x in MISSED_BY_C3],
            "of_those_this_one_is_MATERIAL": "15 — the launcher absent from the repository",
            "why_it_matters": "an under-counted finding list is the same class of error as an "
                              "overstated scan: the record claims more coverage than it had. It is "
                              "corrected here by adjudicating all seventeen, and finding 15 is not "
                              "merely adjudicated but closed — both launchers are now committed.",
            "does_it_change_any_number": False,
            "is_it_load_bearing": False,
        },
        "NO_LOAD_BEARING_FINDING_WAS_DOWNGRADED": True,
        "NO_MATERIAL_FINDING_WAS_PROMOTED_TO_MANUFACTURE_INVALIDITY": True,
        "TERMINAL_UNCHANGED_BY_THE_ADJUDICATION": True,
        "FINAL_DISPOSITION":
            "CAUSAL_LINEAGE_NOT_IDENTIFIABLE_FROM_EXISTING_ARCHIVES__LINEAGE_ROUTE_PAUSED",
    }
    adj["ADJUDICATION_CONTENT_HASH"] = H.content_digest(adj, extra_excluded=("ADJUDICATION_CONTENT_HASH",))
    json.dump(adj, open(f"{OUT}/CLEA01_CHECKER_ADJUDICATION.json", "w"), indent=1)

    with open(f"{OUT}/CLEA01_CHECKER_ADJUDICATION.md", "w") as fh:
        fh.write("# CLEA01 — checker adjudication\n\n"
                 f"One checker. No cascade. Verbatim return sha256 `{sha}`.\n\n"
                 f"`LOAD_BEARING_DEFECT_COUNT = {lbd}` — accepted in full.\n\n"
                 f"{len(F)} items, each adjudicated exactly once.\n\n")
        fh.write("| # | finding | severity | verdict | action taken |\n|---|---|---|---|---|\n")
        for f in F:
            fh.write(f"| {f['id']} | {f['title']} | {f['severity']} | {f['verdict']} | "
                     f"{f['taken'][:180].replace(chr(10), ' ')}… |\n")
        fh.write("\n## A correction to my own earlier record\n\n"
                 "The C3 adjudication reported ten accepted corrections. The checker returned "
                 f"{len(heads)} numbered findings. The ten covered the corrective content of eight "
                 "of them; four items were never adjudicated in writing — 7b, 10b, 12b and, "
                 "materially, **15**, that no launcher existed anywhere in the repository. All "
                 "seventeen are adjudicated above and finding 15 is closed: both launchers are now "
                 "committed under `CLEA01/launcher/`.\n")
    print("findings parsed from the raw return:", len(heads))
    print("items adjudicated:", len(F), " each once:", adj["EACH_ADJUDICATED_EXACTLY_ONCE"])
    print("LOAD_BEARING_DEFECT_COUNT =", lbd)
    print("repo files touched in the checker window:", scope["REPOSITORY_FILES_TOUCHED_IN_THE_WINDOW"])
    print("verdict present:", status["CHECKER_VERDICT_PRESENT"])
    return adj


if __name__ == "__main__":
    main()
