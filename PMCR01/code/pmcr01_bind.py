"""PMCR01 §1 — bind the completed seal once, from machine-readable evidence only.

No remembered conversational value is used. Every field is read from the JSON the seal emitted
and cross-checked against the committed blob, and the controlling handoff is hash-verified
against the digest list the seal signed.
"""
from __future__ import annotations

import hashlib
import json
import subprocess

REPO = "/home/claude/edl"
SEAL = "SEAL01/out"
OUT = "/home/claude/PMCR01/out"


def git(*a):
    r = subprocess.run(("git",) + a, cwd=REPO, capture_output=True, text=True)
    return r.stdout, r.returncode


def blob(path):
    o, rc = git("show", "HEAD:%s" % path)
    return o if rc == 0 else None


def seal_tip_check(head, deliv):
    """The seal spent its whole commit budget, so its delivery record was folded into the
    fourth commit by amending it. A record cannot contain the hash of the commit that carries
    it: the in-tree record therefore names the PREDECESSOR head, and says so in its own
    FIXED_POINT_NOTE. This resolves the offset mechanically instead of assuming it."""
    named = deliv["HEAD_AT_THE_TIME_THIS_RECORD_WAS_WRITTEN"]
    subj_head, _ = git("log", "-1", "--format=%s", head)
    subj_named, rc = git("log", "-1", "--format=%s", named)
    named_reachable, _ = git("merge-base", "--is-ancestor", named, head)
    rc_reach = subprocess.run(("git", "merge-base", "--is-ancestor", named, head),
                              cwd=REPO, capture_output=True).returncode
    n_seal, _ = git("log", "--format=%s", "%s..%s"
                    % (deliv["BRANCH"]["base"], head))
    seal_commits = [ln for ln in n_seal.splitlines() if ln.startswith("SEAL ")]
    return {
        "head": head,
        "head_subject": subj_head.strip(),
        "record_names": named,
        "record_subject": subj_named.strip() if rc == 0 else "OBJECT_NOT_PRESENT",
        "record_named_commit_is_an_ancestor_of_head": rc_reach == 0,
        "seal_commits_reachable_from_head": len(seal_commits),
        "fixed_point_note_present": "FIXED_POINT_NOTE" in deliv,
        "VERDICT": bool(subj_head.strip() == subj_named.strip()
                        and rc_reach != 0
                        and len(seal_commits) == 4
                        and "FIXED_POINT_NOTE" in deliv),
        "READING": ("head carries the same subject as the commit the record names, that "
                    "commit is NOT an ancestor of head because it was replaced by the amend, "
                    "exactly four SEAL commits are reachable, and the record itself declares "
                    "the offset. The base is the sealed tip."),
    }


def main():
    adj = json.loads(blob(f"{SEAL}/_seal_adjudication.json"))
    flow = json.loads(blob(f"{SEAL}/OBFOR01_PREDICTION_INFORMATION_FLOW.json"))
    prov = json.loads(blob(f"{SEAL}/_seal_provenance.json"))
    deliv = json.loads(blob(f"{SEAL}/_seal_delivery.json"))
    rep = json.loads(blob(f"{SEAL}/OBFOR01_SEAL_REPAIR_EVIDENCE.json"))

    handoff_text = blob(f"{SEAL}/PROSPECTIVE_MINORITY_CHANNEL_REACHABILITY_01_HANDOFF.md")
    handoff_sha = hashlib.sha256(handoff_text.encode()).hexdigest()
    sums = blob(f"{SEAL}/SEAL01_SHA256SUMS")
    signed = {ln.split("  ", 1)[1].strip(): ln.split("  ", 1)[0]
              for ln in sums.splitlines() if "  " in ln}
    key = "./out/PROSPECTIVE_MINORITY_CHANNEL_REACHABILITY_01_HANDOFF.md"
    handoff_ok = signed.get(key) == handoff_sha

    head, _ = git("rev-parse", "HEAD")
    parent, _ = git("rev-parse", "HEAD~0")
    branch, _ = git("rev-parse", "--abbrev-ref", "HEAD")

    bound = {
        "SECTION": "PMCR01 §1 parent-seal binding",
        "SOURCE": "machine-readable seal artefacts read from the committed tree via git show",
        "FINAL_SEAL_DISPOSITION": adj["FINAL_DISPOSITION"],
        "ORIGINAL_ZERO_RUN_MISSION_COMPLIANCE":
            adj["ZERO_RUN_COMPLIANCE"]["ORIGINAL_ZERO_RUN_MISSION_COMPLIANCE"],
        "FRESH_SUBSTUDY_PROSPECTIVITY": adj["PROSPECTIVITY"]["FRESH_SUBSTUDY_PROSPECTIVITY"],
        "PREDICTION_MODE": adj["PREDICTION_MODE"],
        "MAXIMAL_AUTHORIZED_CLAIM": adj["MAXIMAL_AUTHORIZED_CLAIM"],
        "NEXT_SCIENTIFIC_ELIGIBILITY": adj["NEXT_SCIENTIFIC_ELIGIBILITY"],
        "OBFOR01_FINAL_TIP": prov["TIPS"]["OBFOR01_FINAL_TIP"]["actual"],
        "SEAL01_FINAL_TIP": head.strip(),
        "PMCR01_BRANCH": branch.strip(),
        "PMCR01_BASE": head.strip(),
        "BASE_IS_THE_SEALED_TIP": seal_tip_check(head.strip(), deliv),
        "CONTROLLING_HANDOFF": {
            "path": f"{SEAL}/PROSPECTIVE_MINORITY_CHANNEL_REACHABILITY_01_HANDOFF.md",
            "sha256_recomputed": handoff_sha,
            "sha256_signed_by_the_seal": signed.get(key),
            "HASH_VERIFIED": handoff_ok},
        "LIMITS_INHERITED_VERBATIM": adj["LIMITS_THAT_TRAVEL_WITH_THE_CLAIM"],
        "PHRASES_RETIRED_BY_THE_SEAL": [p["phrase"] for p in adj["OVERBROAD_PHRASES_TO_RETIRE"]],
        "WHY_NOT_UNCONDITIONAL": flow["WHY_NOT_UNCONDITIONAL"],
        "INHERITED_SOURCE_INTENSITY_INVARIANCE": {
            "effect_per_doubling_pp": rep["R2_SOURCE_INTENSITY_SENSITIVITY"][
                "effect_per_doubling_pp"],
            "se_pp": rep["R2_SOURCE_INTENSITY_SENSITIVITY"]["se_pp"],
            "why_it_matters_here": ("the inherited prediction is conditional on a MEASURED "
                                    "birth-flux law. PMCR01 may not treat any realized "
                                    "trajectory or measured flux as a pre-run known input.")},
        "EVIDENTIARY_ORDER": [
            "1 final repaired machine-readable seal adjudication",
            "2 final seal report",
            "3 prospective minority-channel handoff",
            "4 the execution launcher"],
        "GATE": None,
    }
    bound["GATE"] = (
        "PROCEED" if (bound["NEXT_SCIENTIFIC_ELIGIBILITY"]
                      == "PROSPECTIVE_MINORITY_CHANNEL_REACHABILITY_01"
                      and handoff_ok and bound["BASE_IS_THE_SEALED_TIP"]["VERDICT"])
        else "STOP")
    json.dump(bound, open(f"{OUT}/PMCR01_PARENT_SEAL_BINDING.json", "w"), indent=1,
              default=str)
    for k in ("FINAL_SEAL_DISPOSITION", "ORIGINAL_ZERO_RUN_MISSION_COMPLIANCE",
              "FRESH_SUBSTUDY_PROSPECTIVITY", "PREDICTION_MODE", "NEXT_SCIENTIFIC_ELIGIBILITY",
              "OBFOR01_FINAL_TIP", "SEAL01_FINAL_TIP", "PMCR01_BASE",
              "BASE_IS_THE_SEALED_TIP", "GATE"):
        print("%-38s %s" % (k, bound[k]))
    print("%-38s %s" % ("HANDOFF_HASH_VERIFIED",
                        bound["CONTROLLING_HANDOFF"]["HASH_VERIFIED"]))


if __name__ == "__main__":
    main()
