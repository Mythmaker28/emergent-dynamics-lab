"""EVCS01 C3 — the checker adjudicated, the corrections made, the terminal referred.

Nine MATERIAL findings, zero load-bearing. I accept all twenty-eight in full. Three of them are
corrections to my own C2 commit message, which is immutable and stands wrong; two are corrections
to a parent mission; and one is a correction to what I told the owner in conversation before this
mission existed.
"""
from __future__ import annotations
import datetime as dt, json, os, sys
REPO = os.environ.get("EVCS01_REPO", "/home/claude/edl")
sys.path.insert(0, f"{REPO}/OMLDCT02/code"); sys.path.insert(0, f"{REPO}/EVCS01/code")
import omldct02_hashes as H
import evcs01_sizing as SZ

OUT = f"{REPO}/EVCS01/out"
RAW = f"{REPO}/EVCS01/review/EVCS01_CHECKER_RAW.txt"
TERMINAL = "E3_ENDPOINT_COMPOSITION_MEASURED__DECISION_REFERRED_TO_THE_OWNER"
VOCAB = [TERMINAL, "E3_ENDPOINT_COMPOSITION_NOT_MEASURABLE_FROM_EXISTING_ARCHIVES",
         "EVCS01_TECHNICALLY_INVALID"]

F = [
 (1, "guard (a), method committed before measurement, HOLDS", "NONE", "ACCEPTED",
  "verified from git by the checker: both measurement files byte-identical at C1 and C2, launcher "
  "blob 2af82a18 unchanged, no amend, no earlier EVCS01 object, five dangling blobs all read and "
  "none EVCS01's. Nothing to correct."),
 (2, "the REPORTING code was not pre-committed", "MINOR", "ACCEPTED",
  "true. evcs01_raw_artefact.py arrived at C2, after the numbers, and it decides what a reader "
  "sees. Guard 1 said 'the measurement code' and is weaker than it reads. Nothing was smuggled — "
  "the AFFECTED_ARMS filter is a plain non-zero test — but the guard should have covered reporting "
  "too. Recorded; a future self-issued launcher must say so."),
 (3, "guard (b), inconvenient result named in advance and reported honestly, HOLDS", "NONE",
  "ACCEPTED", "nothing to correct."),
 (4, "guard (c) holds in the instrument and FAILS in the commit prose", "MATERIAL", "ACCEPTED",
  "the C2 subject line and body render exactly the magnitude verdict launcher section 4 "
  "pre-committed not to render. Retracted below. The commit is immutable and stands wrong."),
 (5, "Gate 0 is TRUE, independently re-verified on all 66 arms", "NONE", "ACCEPTED",
  "the checker rebuilt Model A with union-find, integer centroids, forward-only identity and "
  "coordinate sets, and reproduced all four quantities in 66 of 66. Stronger evidence than the "
  "gate itself provided."),
 (6, "Gate 0 is framed as more discriminating than it is", "MINOR", "ACCEPTED",
  "three points all correct: the row count is arithmetically implied by the duration, the "
  "max(a_end, interval_end) guard never bites, and the gate largely compares LDFMA01's classifier "
  "against itself. The launcher's 'no partial credit and no tolerance' rhetoric implied an "
  "independence the test does not have. The genuinely independent verification is the checker's."),
 (7, "the three-class partition is exhaustive and disjoint on real data", "NONE", "ACCEPTED",
  "C + P + N equals the parent's E3_EXPOSURE in 66 of 66, and the checker asserted CERTAIN subset "
  "POSSIBLE at every classified row of every arm rather than arguing it."),
 (8, "the classes are model-relative and the artefacts do not say what they rest on", "MINOR",
  "ACCEPTED",
  "NO_CAUSAL_PATH is only meaningful if the one-step support really is Moore-1. The checker "
  "re-verified that on the exact data walked here: 0 violations over 611,581 row pairs. But no "
  "EVCS01 artefact said the class depends on CLEA01_CAUSAL_KERNEL_ADJUDICATION. Stated below. "
  "Also accepted: row t_m is 100 per cent CERTAIN by construction in every arm."),
 (9, "no threshold in the code or artefacts; one in the prose", "MATERIAL", "ACCEPTED",
  "same defect as finding 4. The sizing self-tests' magnitude bands are authorised by launcher "
  "section 5, are on sampling-yield quantities, and were frozen at C1 — not a back door. The "
  "EXAMPLE_ROWS asymmetry is real and is why finding 21(b) went unnoticed."),
 (10, "nothing monkey-patched, no parent file touched", "NONE", "ACCEPTED", "nothing to correct."),
 (11, "the CERTAIN/POSSIBLE recurrence IS re-specified, contrary to the explicit claim",
  "MATERIAL", "ACCEPTED",
  "true and not arguable. evcs01_measure.py retypes the two lines instead of calling I2.run, while "
  "its docstring and the hashed artefact both say 'imported unchanged, not re-specified'. The "
  "checker verified the retyping is faithful on all four points that could drift and proved "
  "equivalence empirically on 66 of 66 arms — a wrong claim attached to right numbers. The claim "
  "is corrected below; the code is NOT touched, because it is a frozen measurement."),
 (12, "the SELECTIVE degeneracy disclosure was genuinely made in advance", "NONE", "ACCEPTED",
  "the checker tested the mechanism rather than accepting it: 33 of 33 SELECTIVE arms are exactly "
  "one component at t_m+1, and 23 of them later split into 2-4 while staying CERTAIN, which is "
  "what the degeneracy predicts."),
 (13, "the degenerate number is still used to imply the endpoint is clean, in the headline",
  "MATERIAL", "ACCEPTED",
  "the C2 subject line's 'clean in 64 arms' counts all 33 SELECTIVE arms — the very arms I "
  "declared uninformative two paragraphs later. The disclosure was made in the body and undone in "
  "the headline. A subject line is what travels. Retracted below."),
 (14, "the sizing arithmetic holds, independently re-derived", "NONE", "ACCEPTED",
  "the checker's vectorised negative-binomial reproduces the per-draw bootstrap within Monte Carlo "
  "error, and confirmed the instrument is deterministic across re-runs."),
 (15, "the C2 commit message's three sizing numbers contradict the artefact in the same commit",
  "MATERIAL", "ACCEPTED",
  "true, and worse than a typo: 784.8 / 628.8 / 0.078 came from an uncommitted 3000-replicate "
  "development run I did before the artefact existed, and I then quoted it in the permanent "
  "record. The authoritative values are the artefact's. Corrected below; the commit is immutable "
  "and stands wrong."),
 (16, "the ten self-tests are five real tests, two duplicates, two near-unfailable, one tautology",
  "MINOR", "ACCEPTED",
  "the judgement is right, including that test 10 reads a hard-coded literal 110 lines above. The "
  "originals are kept so the C1 freeze is not rewritten, they are marked weak in the code, and "
  "four data-dependent tests that can actually fail are added at C3."),
 (17, "the 95 per cent ceiling is not a 95 per cent ceiling", "MATERIAL", "ACCEPTED",
  "the most substantive finding against this mission. REQUIRED_CEILING conditioned on the "
  "admissible rate being exactly 33/805. Propagating the rate's own posterior, a campaign freezing "
  "785 attains about 85 per cent. I reproduced the checker's numbers independently: 0.8537 against "
  "its 0.8552 at ceiling 785, and 0.1575 against its 0.1611 at ceiling 512. This is, in milder "
  "form, the exact error the instrument exists to prevent. FIXED, not merely disclosed: the "
  "instrument now returns both ceilings and names the rate-uncertain one as the one to freeze."),
 (18, "the COMMON_CAUSE diagnosis is contradicted by both campaigns' own committed records",
  "MATERIAL", "ACCEPTED",
  "the mission's central prescriptive claim and it was wrong. FIMRCC01 ran ZERO worlds — "
  "FRESH_WORLD_COUNT 0, SELECTIVE_ARM_EXECUTED false — and its 0.0165 is the number that STOPPED "
  "it at the precondition gate; its power criterion worked. And OMLDCT02_DESIGN_RECOMPUTED.json, "
  "written before world 1, contains RECOMPUTED_WITH_THE_INSTANCE_CEILING_ALONE with "
  "P_reaching_target 0.9999 — OMLDCT02 DID check its target against its ceiling. 'Frozen "
  "independently and never checked against each other' is false of both. The real common cause is "
  "the one this mission measured: the sizing rate was wrong. Also accepted: calling accrual "
  "probability 'power' put one label over two quantities, which is the failure omldct02_hashes.py "
  "exists to prevent. Corrected below, and the same correction is owed to the owner, who was told "
  "the wrong diagnosis in conversation before this mission existed."),
 (19, "the non-exchangeability evidence is overstated by four orders of magnitude", "MATERIAL",
  "ACCEPTED",
  "the 4.16e-07 binomial tail treats a 256-sample estimate as a known parameter. I recomputed the "
  "proper two-sample comparison myself: Fisher exact p = 0.008710, chi-square with continuity "
  "correction 0.007734 — the published tail overstated by a factor of about 2.1e4. The conclusion "
  "'do not size from that set' survives; the strength does not. Corrected in the instrument."),
 (20, "the checker would select the referral terminal, conditional on five corrections", "NONE",
  "ACCEPTED", "all five corrections are made at C3 and are listed in CORRECTIONS_MADE."),
 (21, "CLEA01's arm count was already exact, and EVCS01's own data refutes CLEA01's stronger "
      "sentence without saying so", "MATERIAL", "ACCEPTED",
  "(a) the novelty was overstated. CLEA01's G4 ran over all 66 arms; the three-row truncation "
  "limited the listing, never the determination, and CLEA01_FINAL_REPORT.md already said 'passes "
  "64 of 66'. The arm fraction is a corollary of the parent's committed result, not a new "
  "measurement. What is genuinely new is the mass and row extent. (b) the correction I held and "
  "did not report: CLEA01 states every cell A carries and C does not was 'never CERTAIN and never "
  "POSSIBLE at any row'. My own data refutes that for 402 SHAM — 525 of its 1221 non-CERTAIN "
  "units, 43 per cent, across 81 of 238 rows, DO have a causal path. CLEA01's sentence held only "
  "on the three rows it republished. Published below as a correction to a closed parent mission."),
 (22, "every artefact has a committed generating script", "NONE", "ACCEPTED",
  "the OMLDCT01 and CLEA01 failure mode is not repeated here."),
 (23, "two provenance gaps in the hashed sizing artefact", "MINOR", "ACCEPTED",
  "the frozen output recorded 'caller-supplied' instead of naming its own ledger, and a "
  "scipy-conditional mutation made SIZING_CONTENT_HASH environment-dependent. Both fixed at C3."),
 (24, "all three content hashes reproduce under the parent's canonical rule", "NONE", "ACCEPTED",
  "the checker re-implemented content_digest from CANONICAL_RULES rather than importing it."),
 (25, "nothing needs the paired p-values and OMLDCT02 is not reinterpreted", "NONE", "ACCEPTED",
  "nothing to correct."),
 (26, "the composition artefact carries none of the claim-ceiling lines", "MINOR", "ACCEPTED",
  "it shows SELECTIVE and SHAM exposure side by side at n = 33 with no ceiling attached. A reader "
  "who opens that file alone gets the arm contrast bare. Fixed at C3."),
 (27, "no forbidden claim, including in denial", "NONE", "ACCEPTED", "nothing to correct."),
 (28, "launcher section 7 says 'no fifth string' over a list of three", "NONE", "ACCEPTED",
  "a leftover from the four-string template of the parent launchers. Harmless, and the checker is "
  "right that it is a tell about how a self-issued launcher gets assembled."),
]

CORRECTIONS = [
 {"id": "C3-1", "from_finding": [4, 13],
  "RETRACTED": "the C2 commit subject line 'the endpoint is clean in 64 arms and materially "
               "foreign in one', and the body sentence '4.4 per cent across 33 SHAM arms is not "
               "that'.",
  "WHY": "both render a magnitude verdict launcher section 4 pre-committed not to render, and the "
         "64 folds in 33 arms I had myself declared uninformative.",
  "REPLACED_BY": "31 of 33 SHAM arms carry no non-CERTAIN mass. 2 of 33 do. The 33 SELECTIVE arms "
                 "are uninformative by construction and are evidence of nothing. The SHAM "
                 "distribution is published; what counts as substantial is the reader's to decide.",
  "THE_COMMIT_IS_IMMUTABLE_AND_STANDS_WRONG": True},
 {"id": "C3-2", "from_finding": [15],
  "RETRACTED": "the C2 commit message's sizing triple 784.8 / 628.8 / 0.078.",
  "WHY": "it came from an uncommitted 3000-replicate development run, not from the artefact "
         "committed in the same commit.",
  "REPLACED_BY": "the artefact's values at the committed default of 20000 replicates: 95 per cent "
                 "ceiling 785.146 conditional on a known rate, median 629.013, P(41 | 512) "
                 "0.07495. And, after the C3 correction, the ceiling a successor should actually "
                 "freeze is the rate-uncertain one.",
  "THE_COMMIT_IS_IMMUTABLE_AND_STANDS_WRONG": True},
 {"id": "C3-3", "from_finding": [11],
  "RETRACTED": "'the operator is imported unchanged from clea01_lineage_i2 and not re-specified "
               "here', in the evcs01_measure.py docstring and in "
               "OPERATOR_IMPORTED_UNCHANGED_FROM.",
  "WHY": "the two recurrence lines are retyped, not called.",
  "REPLACED_BY": "the dilation primitive and the Model A reconstruction are imported and called "
                 "unchanged; the two-line CERTAIN/POSSIBLE recurrence is RE-TYPED from CLEA01's "
                 "and was verified faithful by the checker line by line and empirically on 66 of "
                 "66 arms. The measurement code itself is not touched at C3.",
  "THE_COMMIT_IS_IMMUTABLE_AND_STANDS_WRONG": True},
 {"id": "C3-4", "from_finding": [17],
  "RETRACTED": "REQUIRED_CEILING as a 95 per cent ceiling.",
  "WHY": "it conditioned on the admissible rate being exactly 33/805 and ignored that rate's own "
         "sampling uncertainty — in milder form the exact error the instrument exists to prevent.",
  "REPLACED_BY": "the instrument now returns both. Freezing the old value attains about 85 per "
                 "cent, not 95, which I reproduced independently at 0.8537.",
  "FIXED_IN_CODE_NOT_ONLY_DISCLOSED": True},
 {"id": "C3-5", "from_finding": [18],
  "RETRACTED": "'in both, a pair target and a cost ceiling were frozen independently and never "
               "checked against each other', wherever it appears — the sizing docstring, launcher "
               "section 1, both commit messages, the artefact's COMMON_CAUSE field, and what I "
               "told the owner in conversation before this mission existed.",
  "WHY": "contradicted by both campaigns' own committed records. FIMRCC01 ran zero worlds and its "
         "0.0165 stopped it at the gate; OMLDCT02's pre-run design file records P_reaching_target "
         "0.9999 against the 512 ceiling. Both checked. A successor taking the stated lesson would "
         "do exactly what OMLDCT02 already did and fail the same way.",
  "REPLACED_BY": "the check was performed in both campaigns. What failed is the RATE the check was "
                 "performed at: OMLDCT02 checked its target against its ceiling at 22/256 and got "
                 "0.9999; at the realised 33/805 the same check gives 0.075. The lesson is not "
                 "'check the target against the ceiling' — they did — it is 'the yield estimate is "
                 "the fragile input, and a check conditioned on a point estimate inherits its "
                 "bias'. That is also why C3-4 matters.",
  "THIS_CORRECTION_IS_ALSO_OWED_TO_THE_OWNER_IN_CONVERSATION": True},
 {"id": "C3-6", "from_finding": [19],
  "RETRACTED": "the binomial tail 4.16e-07 as the evidence for non-exchangeability.",
  "WHY": "it treats a 256-sample estimate as a known parameter.",
  "REPLACED_BY": "Fisher exact p = 0.008710 on [[22, 234], [33, 772]], chi-square with continuity "
                 "correction 0.007734, Wilson intervals 0.0574-0.1267 against 0.0293-0.0570. The "
                 "conclusion survives; the strength was overstated by about 2.1e4."},
 {"id": "C3-7", "from_finding": [21],
  "RETRACTED": "'CLEA01's floor of at least 2 arms is now a measurement: exactly 2 of 66', and the "
               "launcher's claim that the arm fraction 'was never measured'.",
  "WHY": "CLEA01's G4 covered all 66 arms and its final report already stated 64 of 66.",
  "REPLACED_BY": "the arm count was already exact in the parent. What EVCS01 adds is the mass and "
                 "row extent: 735 NO_CAUSAL_PATH and 525 POSSIBLE_ONLY units over 182 rows, 13 "
                 "rows of zero CERTAIN mass, first foreign row 1153 against t_m 1106."},
 {"id": "C3-8", "from_finding": [21],
  "A_CORRECTION_TO_A_CLOSED_PARENT_MISSION": True,
  "TARGET": "CLEA01_FINAL_REPORT.md and CLEA01_KNOWN_SUCCESS_ADJUDICATION.json",
  "WHAT_CLEA01_SAYS": "every cell Model A carries and Model C does not was never CERTAIN and never "
                      "POSSIBLE at any row. Not ambiguous origin — no causal path at all.",
  "WHAT_THIS_MISSION_MEASURED": "in 402 SHAM, 525 of the 1221 non-CERTAIN units — 43 per cent, "
                                "across 81 of 238 interval rows — ARE POSSIBLE. They do have a "
                                "causal path to the daughter; it is simply not exclusive. CLEA01's "
                                "sentence held only on the three rows it republished (1153-1155, "
                                "where POSSIBLE_ONLY is zero) and does not hold over the interval.",
  "WHAT_IS_UNAFFECTED": "518 SHAM, where POSSIBLE_ONLY is 0 and CLEA01's sentence holds exactly; "
                        "the G4 verdict of 64 of 66; CLEA01's terminal disposition; and every "
                        "OMLDCT02 number.",
  "WHY_I_DID_NOT_NOTICE": "the EXAMPLE_ROWS cap in the frozen measurement fires only on rows "
                          "carrying NO_CAUSAL_PATH mass, so no POSSIBLE_ONLY row ever reached the "
                          "published artefact. The cap was frozen at C1 before I knew "
                          "POSSIBLE_ONLY mass would exist, so it is honest — and it still made the "
                          "exemplars one-sided in exactly the direction I was looking.",
  "CLEA01_IS_NOT_REOPENED": "no CLEA01 file is modified. The correction is recorded here, in the "
                            "mission that measured it."},
 {"id": "C3-9", "from_finding": [8, 26],
  "ADDED": "the composition artefact now states that NO_CAUSAL_PATH is meaningful only if the "
           "one-step support is Moore-1, names CLEA01_CAUSAL_KERNEL_ADJUDICATION as what "
           "establishes that, notes that row t_m is 100 per cent CERTAIN by construction, and "
           "carries the claim-ceiling lines it was missing."},
 {"id": "C3-10", "from_finding": [16, 23],
  "ADDED": "four data-dependent self-tests that can fail; the four the checker judged weak are "
           "marked as such in the code; the frozen output now names its own ledger; and the "
           "scipy-conditional mutation that made the content hash environment-dependent is gone. "
           "One consequence is disclosed rather than hidden: renaming REQUIRED_CEILING to the "
           "rate-uncertain quantity silently changed what frozen self-test 5 asserts. It still "
           "passes, on a different quantity; the original quantity is covered by new test 12."},
]


def main():
    comp = json.load(open(f"{OUT}/EVCS01_E3_COMPOSITION_RAW.json"))
    gate = json.load(open(f"{OUT}/EVCS01_GATE0_RECONSTRUCTION_IDENTITY.json"))
    sha = H.file_sha256(RAW)
    s, tests = SZ.run_self_tests()

    siz = {
        "MISSION": "EVCS01", "SECTION": "5 — the campaign sizing instrument, corrected at C3",
        "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
        "INSTRUMENT": "EVCS01/code/evcs01_sizing.py",
        "SUPERSEDES": "the C1/C2 version, preserved in git at 2c80d6d and db4b60d. Nothing is "
                      "rewritten; both corrections came from the checker.",
        "DETERMINISTIC": True, "BOOTSTRAP_SEED": SZ.BOOTSTRAP_SEED,
        "FROZEN_OUTPUT": {k: v for k, v in s.items() if not k.startswith("_")},
        "P_41_PAIRS_AT_THE_OMLDCT02_CEILING_512": s["_p512"],
        "P_41_PAIRS_AT_THE_RATE_KNOWN_CEILING_ONCE_THE_RATE_IS_UNCERTAIN":
            s["_p_at_known_ceiling_rate_uncertain"],
        "THE_INSTRUMENT_REFUSES_512": s["_refuse512"],
        "SELF_TESTS": tests, "N_SELF_TESTS": len(tests),
        "ALL_SELF_TESTS_PASS": all(t["PASS"] for t in tests),
        "FOUR_OF_THE_ORIGINAL_TEN_ARE_WEAK_AND_THE_CHECKER_WAS_RIGHT":
            SZ.WEAK_TESTS_PER_THE_CHECKER,
        "TLMR01_DEVELOPMENTAL_SIZING": SZ.TLMR01_DEVELOPMENTAL_SIZING,
        "WHAT_ACTUALLY_WENT_WRONG_IN_THE_PARENT_CAMPAIGNS": {
            "THE_C2_DIAGNOSIS_WAS_WRONG": "I wrote that a target and a ceiling were frozen "
                "independently and never checked against each other. Both campaigns checked.",
            "FIMRCC01": "ran ZERO worlds. FRESH_WORLD_COUNT 0, SELECTIVE_ARM_EXECUTED false. Its "
                        "0.0165 is the number that STOPPED it at the precondition gate, and its "
                        "pre-registration carried an explicit 80 per cent power criterion. Its "
                        "sizing discipline worked.",
            "OMLDCT02": "checked. OMLDCT02_DESIGN_RECOMPUTED.json, written before world 1, records "
                        "RECOMPUTED_WITH_THE_INSTANCE_CEILING_ALONE with P_reaching_target 0.9999.",
            "THE_REAL_COMMON_CAUSE": "the RATE the check was performed at. OMLDCT02 checked its "
                "41-pair target against its 512-instance ceiling at 22/256 and got 0.9999. At the "
                "realised 33/805 the identical check gives 0.075. The fragile input is the yield "
                "estimate, and a check conditioned on a point estimate inherits that estimate's "
                "bias — which is why this instrument now propagates the rate's own uncertainty.",
            "TWO_LABELS_OVER_ONE_WORD": "FIMRCC01's 0.0165 is a detection probability for a k>=2 "
                "rule; OMLDCT02's 0.075 is the probability of ACCRUING the sample and says nothing "
                "about rejecting anything. Calling both 'power' put one label over two quantities.",
        },
        "THESE_ARE_SAMPLING_YIELD_QUANTITIES_NOT_THE_PAIRED_ENDPOINTS": True,
        "OMLDCT02_STATUS": "INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED",
        "OMLDCT02_PAIRED_STATISTICS": "DESCRIPTIVE_ONLY__NO_INFERENTIAL_WEIGHT",
    }
    siz["SIZING_CONTENT_HASH"] = H.content_digest(siz, extra_excluded=("SIZING_CONTENT_HASH",))
    json.dump(siz, open(f"{OUT}/EVCS01_SIZING_INSTRUMENT.json", "w"), indent=1)

    comp["C3_ADDITIONS_AFTER_THE_CHECKER"] = {
        "WHAT_NO_CAUSAL_PATH_RESTS_ON": "it is meaningful only if the true one-step support is the "
            "toroidal Moore-1 neighbourhood. That is established in "
            "CLEA01_CAUSAL_KERNEL_ADJUDICATION.json and is NOT re-established here. The checker "
            "re-verified it on exactly this data: 0 cells without a Moore-1 predecessor over "
            "611,581 row pairs.",
        "ROW_t_m_IS_UNINFORMATIVE_BY_CONSTRUCTION": "CERTAIN(t_m) = root and occ, and Gate 0 "
            "requires A's component at t_m to be the daughter cell set, so one row per interval is "
            "100 per cent CERTAIN by definition.",
        "THE_OPERATOR_IS_RE_TYPED_NOT_CALLED": "corrected claim. The dilation primitive and the "
            "Model A reconstruction are imported and called unchanged; the two-line "
            "CERTAIN/POSSIBLE recurrence is re-typed from CLEA01's and was verified faithful by "
            "the checker line by line and empirically on all 66 arms.",
        "THE_EXEMPLARS_ARE_ONE_SIDED": "EXAMPLE_ROWS fires only on rows carrying NO_CAUSAL_PATH "
            "mass, so no POSSIBLE_ONLY row is shown. That cap was frozen at C1 before I knew "
            "POSSIBLE_ONLY mass would exist, and it is why the correction to CLEA01 in "
            "EVCS01_CHECKER_ADJUDICATION.json C3-8 went unnoticed until the checker found it.",
        "THE_HEADLINE_I_RETRACTED": "'clean in 64 arms' counted the 33 uninformative SELECTIVE "
            "arms. The honest statement is 31 of 33 SHAM arms carry no non-CERTAIN mass and 2 do.",
        "OMLDCT02_STATUS": "INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED",
        "OMLDCT02_PAIRED_STATISTICS": "DESCRIPTIVE_ONLY__NO_INFERENTIAL_WEIGHT",
        "THE_TWO_ARMS_ARE_NOT_CONTRASTED_INFERENTIALLY_HERE": True,
        "H3_STATUS": "NOT_TESTED", "REPRODUCTION_STATUS": "NOT_TESTED",
        "HEREDITY_STATUS": "NOT_TESTED", "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED",
    }
    comp["COMPOSITION_CONTENT_HASH"] = H.content_digest(
        comp, extra_excluded=("COMPOSITION_CONTENT_HASH",))
    json.dump(comp, open(f"{OUT}/EVCS01_E3_COMPOSITION_RAW.json", "w"), indent=1)

    adj = {
        "MISSION": "EVCS01", "SECTION": "6 — checker adjudication",
        "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
        "MAX_INDEPENDENT_CHECKERS": 1, "CHECKERS_DISPATCHED": 1, "REVIEW_CASCADE": "none",
        "CHECKER_RETURN": "EVCS01/review/EVCS01_CHECKER_RAW.txt",
        "CHECKER_RETURN_SHA256": sha,
        "WRITTEN_AND_HASHED_BEFORE_ANY_FINDING_WAS_ACTED_ON": True,
        "LOAD_BEARING_DEFECT_COUNT": 0,
        "I_ACCEPT_THE_CHECKER_IN_FULL": True,
        "N_FINDINGS": len(F),
        "N_MATERIAL": sum(1 for f in F if f[2] == "MATERIAL"),
        "N_MINOR": sum(1 for f in F if f[2] == "MINOR"),
        "ITEMS": [{"id": i, "finding": t, "checker_severity": sev, "verdict": v, "action": act}
                  for i, t, sev, v, act in F],
        "EACH_ADJUDICATED_EXACTLY_ONCE": len({f[0] for f in F}) == len(F),
        "CORRECTIONS_MADE": CORRECTIONS,
        "THREE_CLAIMS_I_RE_VERIFIED_MYSELF_RATHER_THAN_ACCEPTING": {
            "finding 17": "P(41 | 785) with the rate uncertain: checker 0.8552, mine 0.8537. "
                          "P(41 | 512): checker 0.1611, mine 0.1575.",
            "finding 19": "Fisher exact on [[22,234],[33,772]]: checker 0.0087, mine 0.008710. "
                          "chi-square with continuity correction: checker 0.0077, mine 0.007734.",
            "finding 21b": "402 SHAM composition from my own committed raw: C 859, P 525, N 696, "
                           "sum 2080 equal to the recorded E3_EXPOSURE. 525 of 1221 non-CERTAIN "
                           "units, 43.0 per cent, are POSSIBLE. CLEA01's sentence is refuted for "
                           "this arm by my own data.",
        },
        "NO_LOAD_BEARING_FINDING_WAS_DOWNGRADED": True,
        "NO_MATERIAL_FINDING_WAS_PROMOTED_TO_MANUFACTURE_INVALIDITY": True,
        "WHY_NOT_TECHNICALLY_INVALID": "the checker argued that case first and at full strength, "
            "and I considered it. Launcher section 6 reserves that terminal for a confirmed "
            "load-bearing defect and there is none: every recorded number reproduces under a fully "
            "independent re-implementation. All three guard breaches are in prose a third commit "
            "can correct without touching a digit. And the checker's own observation applies — a "
            "self-issued mission that declares itself invalid escapes its own findings, so "
            "reaching for it here would be self-serving in the other direction.",
        "WHY_NOT_NOT_MEASURABLE": "the composition was measured, exactly and reproducibly, and "
            "independently confirmed on all 66 arms. Degenerate is not unmeasurable, and the "
            "degeneracy was pre-declared rather than discovered. Choosing that string would erase "
            "735 units of foreign mass and 525 of ambiguous mass across 182 rows of the control "
            "arm.",
        "FINAL_DISPOSITION": TERMINAL,
    }
    adj["ADJUDICATION_CONTENT_HASH"] = H.content_digest(
        adj, extra_excluded=("ADJUDICATION_CONTENT_HASH",))
    json.dump(adj, open(f"{OUT}/EVCS01_CHECKER_ADJUDICATION.json", "w"), indent=1)

    sham = comp["SHAM"]
    sel = comp["SELECTIVE"]
    disp = {
        "MISSION": "EVCS01", "SECTION": "final disposition",
        "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
        "FINAL_DISPOSITION": TERMINAL, "TERMINAL_VOCABULARY": VOCAB,
        "NO_STRING_OUTSIDE_THE_VOCABULARY_WAS_INVENTED": True,
        "LAUNCHER_WAS_SELF_ISSUED": True,
        "THE_THREE_GUARDS": {
            "guard_1_method_committed_before_measurement": "HELD, verified from git by the checker",
            "guard_2_inconvenient_result_named_in_advance": "HELD, and it did not occur, and that "
                                                            "was reported",
            "guard_3_no_threshold_no_verdict_on_the_science":
                "HELD in the instrument, BREACHED in the C2 commit prose. Retracted at C3.",
        },
        "GATE0_PASS": gate["GATE0_PASS"], "GATE0_ARMS": gate["N_ARMS"],
        "SHAM_COMPOSITION": {k: sham[k] for k in
                             ("E3_EXPOSURE_TOTAL", "CERTAIN", "POSSIBLE_ONLY", "NO_CAUSAL_PATH",
                              "CERTAIN_fraction", "POSSIBLE_ONLY_fraction",
                              "NO_CAUSAL_PATH_fraction", "arms_with_any_NO_CAUSAL_PATH_mass",
                              "interval_rows_carrying_zero_CERTAIN_mass")},
        "SELECTIVE_COMPOSITION_IS_UNINFORMATIVE_BY_CONSTRUCTION": True,
        "SELECTIVE_E3_EXPOSURE_TOTAL": sel["E3_EXPOSURE_TOTAL"],
        "WHAT_IS_REFERRED_TO_THE_OWNER": [
            "whether 4.4 per cent of control-arm E3_EXPOSURE with no causal path to the daughter, "
            "concentrated in 2 of 33 arms with one at 33.5 per cent, is acceptable in an endpoint "
            "a successor campaign would reuse",
            "whether 13 interval rows counted in E3_DURATION that contain no daughter-descended "
            "mass at all are acceptable",
            "whether a successor should keep this endpoint, tighten the CORE_R linkage rule, or "
            "add a provenance filter to it",
            "what pair target and ceiling to freeze, given the instrument now returns a "
            "rate-uncertain ceiling of about 890 for 41 pairs rather than the 785 it returned "
            "before the checker",
        ],
        "NO_THRESHOLD_SEPARATES_ACCEPTABLE_FROM_UNACCEPTABLE_AND_THIS_MISSION_DOES_NOT_SUPPLY_ONE": True,
        "CHECKERS_DISPATCHED": 1, "LOAD_BEARING_DEFECT_COUNT": 0,
        "N_FINDINGS_ADJUDICATED": len(F), "N_CORRECTIONS_MADE": len(CORRECTIONS),
        "CORRECTIONS_TO_A_PARENT_MISSION": 1,
        "CORRECTIONS_TO_WHAT_THE_OWNER_WAS_TOLD_IN_CONVERSATION": 1,
        "NEW_SCIENTIFIC_ENGINE_RUNS": 0, "NEW_WORLD_CONSTRUCTIONS": 0, "NEW_SEEDS": 0,
        "NEW_TRAJECTORIES": 0, "NEW_SCIENTIFIC_WORLDS_USED": 0,
        "CLEA01_STATUS": "CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED",
        "OMLDCT02_STATUS": "INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED",
        "OMLDCT02_PAIRED_STATISTICS": "DESCRIPTIVE_ONLY__NO_INFERENTIAL_WEIGHT",
        "H3_STATUS": "NOT_TESTED", "REPRODUCTION_STATUS": "NOT_TESTED",
        "HEREDITY_STATUS": "NOT_TESTED", "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED",
        "X_LAWSPEC_BASELINE": "UNCHANGED", "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED",
        "COMPANION_PAPER_V1_1_STATUS": "UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED",
    }
    disp["DISPOSITION_CONTENT_HASH"] = H.content_digest(
        disp, extra_excluded=("DISPOSITION_CONTENT_HASH",))
    json.dump(disp, open(f"{OUT}/EVCS01_FINAL_DISPOSITION.json", "w"), indent=1)

    print("checker sha256:", sha)
    print("findings adjudicated:", len(F), " MATERIAL:", adj["N_MATERIAL"], " MINOR:", adj["N_MINOR"])
    print("corrections made:", len(CORRECTIONS))
    print("self-tests:", len(tests), "all pass:", siz["ALL_SELF_TESTS_PASS"])
    print("rate-known ceiling :", s["REQUIRED_CEILING_IF_THE_RATE_WERE_KNOWN_EXACTLY"])
    print("rate-uncertain ceiling (freeze this one):", s["REQUIRED_CEILING"])
    R = f"""# EVCS01 — FINAL REPORT

```
FINAL_DISPOSITION = {TERMINAL}
LOAD_BEARING_DEFECT_COUNT = 0
NEW_SCIENTIFIC_WORLDS_USED = 0
LAUNCHER = SELF_ISSUED
```

## What this mission was for

CLEA01 closed with a finding aimed at its parent: the qualified OMLDCT02 E3 component contains Y
mass with no causal path to the daughter. `E3_DURATION` and `E3_EXPOSURE` are not OMLDCT02's
endpoints alone — they are the programme's measuring instrument, and any successor reuses them.
This mission measured what that instrument actually contains, and turned the accrual arithmetic
into committed code. Zero worlds, zero seeds.

## The launcher was mine, and that is the first thing to distrust

The owner authorised the choice of mission, not its content. An operator who writes his own mandate
can write one he is guaranteed to pass. Three guards were declared in advance:

| guard | outcome |
|---|---|
| method committed before any measurement | **HELD** — verified from git by the checker, not from my prose |
| an inconvenient result named in advance | **HELD** — and it did **not** occur, and that was reported |
| no threshold, no verdict on the science | **HELD in the code, BREACHED in my C2 commit prose** |

The third breach is real and the checker was right to press it. My C2 subject line said *"the
endpoint is clean in 64 arms and materially foreign in one"* — a magnitude verdict I had
pre-committed not to render, on a tally that folded in the 33 arms I had myself declared
uninformative. Retracted at C3. The commit is immutable and stands wrong.

## Gate 0

Model A reconstructed from LDFMA01's frozen classifier reproduces the parent's own `E3_DURATION`,
`E3_EXPOSURE` and interval row count **exactly in 66 of 66 arms**. The checker did not take that on
trust: it rebuilt Model A with a different component algorithm, integer centroids, forward-only
identity tracking and coordinate sets, and reproduced all four quantities in all 66. That
independent verification is the checker's, not mine.

## What E3_EXPOSURE is made of

```
SHAM        16765 units    CERTAIN 15505 (0.9248)   POSSIBLE_ONLY 525 (0.0313)   NO_CAUSAL_PATH 735 (0.0438)
SELECTIVE   18204 units    CERTAIN 18204 (1.0000)   POSSIBLE_ONLY   0            NO_CAUSAL_PATH   0
```

**The SELECTIVE column is uninformative by construction and is evidence of nothing.** After the
intervention the daughter is the world's only Y source, so everything descends from it. The launcher
said so before the number existed; the checker verified the mechanism independently (33 of 33 arms
are exactly one component at `t_m+1`, and the 23 that later split stay CERTAIN).

In the control arm, the foreign mass concentrates:

```
402 SHAM   2080 = 859 CERTAIN + 525 POSSIBLE_ONLY + 696 NO_CAUSAL_PATH    33.5% of that arm
518 SHAM   1669 = 1630 + 0 + 39                                            2.3%
31 of 33 SHAM arms carry no non-CERTAIN mass at all
13 interval rows counted in E3_DURATION contain no daughter-descended mass whatever
```

Whether that is acceptable in an endpoint a successor would reuse is **not decided here**. No
threshold separates acceptable from unacceptable, this mission does not supply one, and a
self-issued mandate has no standing to decide it. It is referred to the owner.

## A correction to a closed parent mission

CLEA01 states that every cell Model A carries and Model C does not was *"never CERTAIN and never
POSSIBLE at any row. Not ambiguous origin — no causal path at all."*

My own measurement refutes that for 402 SHAM. **525 of that arm's 1221 non-CERTAIN units — 43 %,
across 81 of 238 interval rows — are POSSIBLE.** They do have a causal path to the daughter; it is
simply not exclusive. CLEA01's sentence held only on the three rows it republished. 518 SHAM is
unaffected, the G4 verdict of 64 of 66 is unaffected, CLEA01's terminal is unaffected, and no
OMLDCT02 number moves. No CLEA01 file is modified — the correction is recorded in the mission that
measured it.

I held this in hand and did not report it. The reason is instructive rather than exculpating: the
`EXAMPLE_ROWS` cap fires only on rows carrying NO_CAUSAL_PATH mass, so no POSSIBLE_ONLY row ever
reached the published artefact. The cap was frozen at C1 before I knew POSSIBLE_ONLY mass would
exist — honest, and still one-sided in exactly the direction I was looking.

## The sizing instrument, and the diagnosis I got wrong

I wrote, in C2 and to the owner in conversation, that two campaigns failed because *"a pair target
and a cost ceiling were frozen independently and never checked against each other."* **That is false
of both, and their own committed records say so.** FIMRCC01 ran **zero** worlds — its 0.0165 is the
number that *stopped* it at the precondition gate, and its pre-registration carried an explicit 80 %
power criterion. OMLDCT02's pre-run design file records `P_reaching_target = 0.9999` against the 512
ceiling. Both checked.

The real common cause is narrower and sharper: **the rate the check was performed at.** OMLDCT02
checked its 41-pair target against its 512-instance ceiling at 22/256 and got 0.9999. At the
realised 33/805 the identical check gives 0.075. The fragile input is the yield estimate, and a
check conditioned on a point estimate inherits that estimate's bias.

Which is exactly the error the checker then found in my own instrument. `REQUIRED_CEILING` was the
95th percentile **conditional on the rate being exactly 33/805**. Propagating the rate's own
posterior, a campaign freezing that value attains about **85 %**, not 95 — I reproduced the
checker's number independently at 0.8537. Fixed in code, not merely disclosed:

```
41 pairs at 95%, rate treated as known    785.1     <- what C1/C2 returned; optimistic
41 pairs at 95%, rate uncertain           887.1     <- freeze this one
OMLDCT02's frozen ceiling                 512       <- the instrument REFUSES it
```

The non-exchangeability of the TLMR01 developmental sizing set survives, but its evidence was
overstated by about 2.1e4: the published binomial tail of 4.16e-07 treated a 256-sample estimate as
a known parameter. The correct two-sample comparison gives **Fisher exact p = 0.008710**.

## The checker

One checker, no cascade. Verbatim return hashed before any finding was acted on. **28 findings, 9
MATERIAL, 6 MINOR, zero load-bearing** — and every MATERIAL one is prose or framing attached to a
right number. Its own summary of the pattern is the fairest description of this mission: *more
careful in its instruments than in its narration.* Ten corrections made, three of them to my own
immutable commit message, one to a closed parent mission, one to what the owner was told before this
mission existed.

## Claim ceiling

```
CLEA01_STATUS                 = CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED
OMLDCT02_STATUS               = INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED
OMLDCT02_PAIRED_STATISTICS    = DESCRIPTIVE_ONLY__NO_INFERENTIAL_WEIGHT
H3_STATUS                     = NOT_TESTED
REPRODUCTION_STATUS           = NOT_TESTED
HEREDITY_STATUS               = NOT_TESTED
AUTONOMOUS_COHESION_STATUS    = NOT_ESTABLISHED
X_LAWSPEC_BASELINE            = UNCHANGED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
COMPANION_PAPER_V1_1_STATUS   = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED
```

Nothing measured here establishes anything about reproduction, authorises a successor campaign, or
reopens CLEA01.
"""
    open(f"{OUT}/EVCS01_FINAL_REPORT.md", "w").write(R)
    names = sorted(n for n in os.listdir(OUT) if n != "SHA256SUMS")
    with open(f"{OUT}/SHA256SUMS", "w", newline="\n") as fh:
        for n in names:
            fh.write(f"{H.file_sha256(f'{OUT}/{n}')}  {n}\n")
    print("artefacts:", len(names) + 1)
    print("FINAL_DISPOSITION =", TERMINAL)


if __name__ == "__main__":
    main()
