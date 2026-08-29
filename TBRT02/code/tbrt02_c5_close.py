"""TBRT02 — C5. Closure."""
from __future__ import annotations
import os, sys, json, subprocess
REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "TBRT02/code"))
import tbrt02_freeze as F
H = F.H
c3 = json.load(open(f"{REPO}/TBRT02/out/TBRT02_C3_RAW_CLOSE.json"))
c4 = json.load(open(f"{REPO}/TBRT02/out/TBRT02_C4_ANALYSIS.json"))
cb = json.load(open(f"{REPO}/TBRT02/out/TBRT02_C4BIS_CHECKER_ADJUDICATION.json"))
frz = json.load(open(f"{REPO}/TBRT02/out/TBRT02_MASTER_FREEZE.json"))

d = {
 "MISSION": "TBRT02", "SECTION": "C5 — closure",
 "GENERATED_UTC": subprocess.run(["date","-u","+%Y-%m-%dT%H:%M:%S+00:00"],capture_output=True,text=True).stdout.strip(),
 "CHAIN": {"C1": "77cc3c7", "C2": "b895ff7", "addendum": "672ccc1", "C3": "ec4f83b",
           "C4": "9bebfda", "checker_return_verbatim": "803457e", "C4_bis": "8a28411"},
 "PARENT_HASHES": {"FREEZE_CONTENT_HASH": frz["FREEZE_CONTENT_HASH"],
                   "C3_CONTENT_HASH": c3["C3_CONTENT_HASH"],
                   "C4_CONTENT_HASH": c4["C4_CONTENT_HASH"],
                   "C4BIS_CONTENT_HASH": cb["C4BIS_CONTENT_HASH"],
                   "METHODS_HASH": frz["METHODS_HASH"]},

 "1_WHAT_THE_MISSION_PRODUCED": {
   "seeds_consumed": c3["SEEDS_CONSUMED"], "seeds_triggered": c3["SEEDS_TRIGGERED"],
   "valid_triples": c3["VALID_TRIPLES"], "target": c3["TARGET_VALID_TRIPLES"],
   "arm_instances_spent": c3["ARM_INSTANCES_SPENT"], "ceiling": c3["MAX_ARM_INSTANCES"],
   "ceiling_bound_the_campaign": c3["CEILING_BOUND_THE_CAMPAIGN"],
   "technical_failures": c3["TECHNICAL_FAILURES"],
   "prefix_integrity_failures": c3["PREFIX_INTEGRITY_FAILURES"],
   "duplicate_indices": c3["DUPLICATE_INDICES"],
   "archives": c3["N_ARCHIVES"],
   "all_archives_sha256_verified": c3["ALL_ARCHIVES_SHA256_VERIFIED_AGAINST_THE_SEALED_LEDGER"],
   "methods_hash_unchanged_end_to_end": c3["METHODS_HASH_UNCHANGED"],
   "no_frozen_value_threshold_or_seed_was_touched": True,
 },
 "2_WHAT_THE_MISSION_ADJUDICATES": {
   "ANSWER": "NOTHING.",
   "why": "the frozen refutation condition was fixed in words and never turned into a procedure. "
     "Under the strict cell-membership reading it cannot fire — proved, and searched over 4000 "
     "adversarial worlds including 7560 rows where the two sets were in direct contact. Under the "
     "body-level reading the checker supplied it fires in 17 of 41. Neither reading was fixed "
     "before the data, so neither adjudicates. The pre-registered sequential bound is inadmissible "
     "for the same reason and is not reported as a finding.",
   "MODEL_C_STATUS": "NOT_REFUTED AND NOT CORROBORATED BY THIS EXPERIMENT",
   "the_falsifiability_claimed_in_tbrt02_displace_py_is_NOT_established": True,
 },
 "3_WHAT_IS_NONETHELESS_ESTABLISHED": {
   "a": "SELECTIVE reproduces CLEA01's degeneracy without exception: in 41 of 41 worlds the "
        "permissive lineage set is identical to the certain one. Removing the parent leaves the "
        "daughter as the only source, so everything descends from her and the object explains "
        "nothing. CLEA01 closed on exactly this; it was not an artefact of that mission.",
   "b": "the displacement does buy ground truth — the competing mass sits at a known cell, its "
        "descendants are labelled by construction, and under variant B it leaves descendants in "
        "41 of 41 worlds. But on the metric that matters it did WORSE than doing nothing: a "
        "non-degenerate lineage object in 17 of 41 treated worlds against 26 of 41 in the "
        "untreated control. Moving the competitor to Chebyshev 17-18 from the daughter made "
        "contact rarer, not commoner.",
   "c": "every duration reported anywhere in this mission is right-censored at the horizon, and "
        "the censoring rate differs by arm (CERTAIN: 8, 29 and 16 of 41 for SHAM, SELECTIVE and "
        "DISPLACED). Declared, not buried.",
   "d": "the raw is intact and reusable: 41 triples, 123 archives, 440 MB, every one verified "
        "against the sha256 sealed in the ledger at the moment it was written.",
 },
 "4_MY_OWN_ERRORS_IN_THIS_MISSION": [
   "seeded the competitor's descendants on the pre-intervention row, which made the displaced mass "
   "appear to die instantly in every world. Found before use.",
   "after fixing that, still lost the three worlds where the quantum hopped on the first step. "
   "Found by cell-by-cell inspection, before use.",
   "gave a root cause for the seeding defect that the data contradict: the parent is never within "
   "one step of a daughter cell, so it could not have been a source. Withdrawn in C4-bis.",
   "claimed the strict reading was the only one the frozen words support. False. The freeze's own "
   "question names a body; I enumerated readings over the objects my instrument happened to "
   "produce. Withdrawn in C4-bis.",
   "withheld the sequential bound for the wrong reason. Right decision, replaced argument.",
   "failed to subtract two numbers I had already reported, and so did not write that the treatment "
   "underperformed its own control. Written in C4-bis.",
 ],
 "5_THE_BEQUEST": {
   "PRIMARY": "a successor's refutation condition must be OPERATIONALISED IN CODE before the first "
     "world, not merely stated in words — and it must ship with a CAPABILITY TEST: an adversarial "
     "search demonstrating that the condition CAN fire, paired with a control that does fire under "
     "a rule known to permit it. A condition that has never been shown capable of firing is not a "
     "test. TBRT02 froze a sentence and not a procedure, and that single omission is the whole "
     "reason it cannot decide anything.",
   "SECONDARY": "the menu of readings must be drawn over the objects the freeze NAMES, not over "
     "the objects the instrument produces. The freeze asked about an organisation and a source it "
     "could absorb — both bodies. I enumerated cells and quanta. The body was already frozen "
     "(FDOT01's component rule) and already in every archive, in a column I had loaded and not "
     "used.",
   "TERTIARY": "a zero-event anytime-valid bound requires the STATISTIC to be fixed before the "
     "data, not merely the admissibility rule. TBRT02's addendum verified the admissibility "
     "condition carefully and never noticed that the statistic itself was undefined.",
   "OPERATIONAL": "durability is not a commit. Over this mission the campaign survived eleven "
     "container rollbacks because every checkpoint wrote to a channel outside the container in the "
     "same turn as the commit. The channel that failed first was the one nobody was watching.",
 },
 "6_WHAT_A_SUCCESSOR_COULD_DO_WITH_THIS_RAW_WITHOUT_A_NEW_WORLD": [
   "pre-register the body-level condition in code, with a capability test, and read it on these "
   "41 triples as a genuine test — the archives already carry c_cid",
   "the core-depletion spot-division mechanism comparison (Reynolds, Ponce-Dawson, Pearson 1997), "
   "measurable on the per-step component and free-capacity series already archived",
 ],

 "H3_STATUS": "NOT_TESTED", "REPRODUCTION_STATUS": "NOT_TESTED", "HEREDITY_STATUS": "NOT_TESTED",
 "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED", "X_LAWSPEC_BASELINE": "UNCHANGED",
 "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED",
 "COMPANION_PAPER_V1_1_STATUS": "UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED",
 "OMLDCT02_STATUS": "INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED",
 "CLEA01_STATUS": "CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED",
 "TBRT02_STATUS": "CLOSED__RAW_COMPLETE__PRIMARY_ADJUDICATION_INCONCLUSIVE_BY_CONSTRUCTION",
 "NOTHING_IN_THIS_MISSION_ESTABLISHES_ANY_CLAIM_ABOUT_LINEAGE_IN_THE_WORLD": True,
}
d["C5_CONTENT_HASH"] = H.content_digest(d, extra_excluded=("C5_CONTENT_HASH",))
open(f"{REPO}/TBRT02/out/TBRT02_C5_CLOSURE.json","w").write(json.dumps(d, indent=1)+"\n")
print("C5_CONTENT_HASH", d["C5_CONTENT_HASH"])
print("TBRT02_STATUS", d["TBRT02_STATUS"])
