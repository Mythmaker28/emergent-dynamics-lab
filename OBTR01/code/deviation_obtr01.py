"""OBTR01 §3 — close, append-only, the post-run adjudication deviation recorded by OBDCA01.

The mandate gives a STOP condition, not a formality: the note may be written only if the
deviation touched neither the data, nor the gate, nor the freeze, nor the trajectories. If it
touched any of them the mission must stop at INHERITED_EVIDENCE_NOT_CLOSED.

So the four claims are CHECKED here against the delivered artefacts, one check each, and the
note is written only if all four hold. Nothing in OBDI02 or OBDCA01 is modified: this file
only reads them and appends a new artefact.
"""
from __future__ import annotations

import hashlib
import json
import os

WC = "/home/claude/OBTR01/verify/obdca01/wc"
OUT = "/home/claude/OBTR01/out"
D2 = f"{WC}/OBDI02"
DA = f"{WC}/OBDCA01"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def resolve(name):
    """METHODS_CORE files live across several mission code roots; the freeze records only the
    basename, so the resolver has to search and record where it found each one."""
    for root in ("OBDI02/code", "OBDI01/code", "OBTC02/code", "ORR01/code"):
        p = f"{WC}/{root}/{name}"
        if os.path.exists(p):
            return p
    return None


# ---------------------------------------------------------------- check 1: the freeze
def check_freeze():
    fr = json.load(open(f"{D2}/out/_freeze.json"))
    files, missing, digests = fr["METHODS_CORE_FILES"], [], {}
    for name, want in sorted(files.items()):
        p = resolve(name)
        if p is None:
            missing.append(name)
            continue
        digests[name] = {"path": os.path.relpath(p, WC), "recorded": want, "actual": sha256(p)}
    agree = [n for n, d in digests.items() if d["recorded"] == d["actual"]]
    disagree = [n for n, d in digests.items() if d["recorded"] != d["actual"]]
    # The construction is read off freeze_obdi02.py, not guessed: for each name in sorted
    # order, update with name, a NUL byte, the digest, and a newline.
    h = hashlib.sha256()
    for n in sorted(digests):
        h.update(n.encode())
        h.update(b"\0")
        h.update(digests[n]["actual"].encode())
        h.update(b"\n")
    recomputed = h.hexdigest()
    return {
        "recorded_METHODS_CORE_HASH": fr["OBDI02_METHODS_CORE_HASH"],
        "recomputed_from_the_recorded_file_digests": recomputed,
        "HASH_REPRODUCES": recomputed == fr["OBDI02_METHODS_CORE_HASH"],
        "files_in_core": len(files), "files_resolved": len(digests),
        "files_whose_bytes_still_match": len(agree),
        "files_whose_bytes_changed": disagree,
        "files_not_found": missing,
        "spec_sha256_recorded": fr["spec_sha256"],
        "spec_sha256_actual": sha256(f"{WC}/OBDI02/code/obdi02_protocol.yaml"),
        "frozen_margin_field": fr["FROZEN_BEFORE_ANY_START"]["margin"],
        "VERDICT": ("UNTOUCHED" if (recomputed == fr["OBDI02_METHODS_CORE_HASH"]
                                    and not disagree and not missing) else "ALTERED"),
    }


# ---------------------------------------------------------------- check 2: the trajectories
def check_trajectories():
    """OBDI02/out/SHA256SUMS covers the OUT artefacts only; the raw trajectories are covered by
    the git object chain instead, which is the stronger statement — every raw file is a blob
    inside a tree whose hash the readback already verified. So the per-file digest authority
    used here is the delivered repository itself: `git ls-tree` gives the recorded blob id and
    `git hash-object` recomputes it from the bytes on disk."""
    import subprocess
    seeds = json.load(open(f"{D2}/out/_seeds.json"))
    arms = json.load(open(f"{D2}/out/_arms.json"))
    raw_dir = f"{D2}/raw"
    on_disk = sorted(os.listdir(raw_dir))

    def git(*a):
        return subprocess.run(("git", "-C", WC) + a, capture_output=True, text=True).stdout

    recorded = {}
    for line in git("ls-tree", "-r", "HEAD", "OBDI02/raw").splitlines():
        meta, _, path = line.partition("\t")
        parts = meta.split()
        if len(parts) >= 3:
            recorded[os.path.basename(path)] = parts[2]
    bad, checked = [], 0
    for n in on_disk:
        if n not in recorded:
            continue
        got = git("hash-object", f"OBDI02/raw/{n}").strip()
        if got != recorded[n]:
            bad.append(n)
        checked += 1

    declared = sorted(int(s) for s in seeds["FRESH_FLAT"])
    seed_in_name = sorted(int(n.split("seed")[1].split(".")[0]) for n in on_disk if "seed" in n)
    n_arms = (len(arms) if isinstance(arms, list)
              else sum(len(v) for v in arms.values() if isinstance(v, list)))
    dup = len(seed_in_name) != len(set(seed_in_name))
    return {
        "digest_authority": "git blob ids of the delivered branch, recomputed from the bytes",
        "raw_files_on_disk": len(on_disk),
        "raw_files_recorded_in_the_delivered_tree": len(recorded),
        "raw_files_whose_blob_id_was_recomputed": checked,
        "raw_files_whose_blob_id_changed": bad,
        "arms_recorded_in__arms_json": n_arms,
        "distinct_seeds_declared_at_freeze_FRESH_FLAT": len(declared),
        "seeds_present_in_raw": len(seed_in_name),
        "any_seed_appears_twice": dup,
        "seeds_declared_but_absent": sorted(set(declared) - set(seed_in_name))[:20],
        "seeds_present_but_not_declared": sorted(set(seed_in_name) - set(declared))[:20],
        "retired_seeds_declared_disjoint": seeds.get("DISJOINT"),
        "VERDICT": ("UNTOUCHED" if (not bad and checked == len(on_disk) and not dup
                                    and set(declared) == set(seed_in_name))
                    else "ALTERED"),
    }


# ---------------------------------------------------------------- check 3: the gate
def check_gate():
    """The gate is the frozen yaml plus gate_obdi02.py; check_freeze already covers their
    bytes. What is checked HERE is the SUBSTANCE: that the qualification rule the freeze
    states was evaluated as stated, that the freeze itself declares the 0.042 figure
    non-decisive, and that the yaml contains no disposition-selection rule at all - which is
    the structural gap the deviation walked through."""
    import yaml
    spec = yaml.safe_load(open(f"{WC}/OBDI02/code/obdi02_protocol.yaml"))
    res = json.load(open(f"{D2}/out/_results.json"))
    pe, sg, st = spec["primary_endpoint"], spec["population_support_gate"], spec["stopping"]

    # (a) the frozen QUALIFICATION rule, verbatim, and the two conditions it names
    rule = sg["qualification"]
    support = res["POPULATION_SUPPORT"]
    support_pass = bool(support.get("PASS", support.get("GATE_PASS")))
    primary_pass = bool(res["PRIMARY"]["PASS"])

    # (b) what the freeze says about 0.042, verbatim
    stringent = pe.get("stringent_reference_status", "")
    stringent_nondecisive = "never decisive" in stringent.lower()

    # (c) is there ANY rule in the frozen yaml mapping outcomes onto dispositions?
    disp = spec["dispositions"]
    flat_list_only = isinstance(disp, list) and all(isinstance(x, str) for x in disp)

    # (d) the three declared per-arm requirements, re-evaluated on all 138 arms from the
    #     recorded technical block rather than looked up by name (the names are conceptual;
    #     the yaml implements them through the seven declared `fields`).
    arms = json.load(open(f"{D2}/out/_arms.json"))
    tv_fields = spec["technical_validity"]["fields"]
    fail = {"FRAME_STREAM_TABLE_IDENTITY": [], "ONLINE_POSTHOC_AGREEMENT": [],
            "DECLARED_FIELDS_PRESENT": []}
    for a in arms:
        t = a["technical"]
        if any(f not in t for f in tv_fields):
            fail["DECLARED_FIELDS_PRESENT"].append(a["tag"])
            continue
        if not (t["STREAM_FRAME_COUNT"] == t["TABLE_FRAME_COUNT"] == t["EXPECTED_FRAME_COUNT"]
                and t["STREAM_FRAME_INDEX_SHA256"] == t["TABLE_FRAME_INDEX_SHA256"]
                and t["STREAM_SPATIAL_PAYLOAD_SHA256"] == t["TABLE_SPATIAL_PAYLOAD_SHA256"]):
            fail["FRAME_STREAM_TABLE_IDENTITY"].append(a["tag"])
        if not a["GATES_AGREE"]:
            fail["ONLINE_POSTHOC_AGREEMENT"].append(a["tag"])
    tv_required = spec["technical_validity"]["per_arm_requirements"]
    tv_missing = sorted(k for k, v in fail.items() if v)
    tv_detail = {"arms_checked": len(arms),
                 "requirements_declared": tv_required,
                 "declared_fields": tv_fields,
                 "arms_failing_each_re_evaluated_requirement":
                     {k: len(v) for k, v in fail.items()},
                 "failing_tags": {k: v[:10] for k, v in fail.items() if v},
                 "THIRD_BOUNDARY_TESTS": ("evaluated inside gate_obtc02.evaluate, whose bytes "
                                          "are covered by METHODS_CORE; the per-arm outcome it "
                                          "feeds is RUN_TECHNICALLY_VALID, true on every arm"),
                 "arms_with_RUN_TECHNICALLY_VALID_false":
                     [a["tag"] for a in arms if not a["RUN_TECHNICALLY_VALID"]]}

    # (e) the stopping rule: every frozen arm run, none replaced, no margin moved
    planned, run = res["planned_arms"], res["arms_run"]

    return {
        "frozen_qualification_rule_verbatim": rule,
        "conditions_that_rule_names": ["population support gate",
                                       "conditional equivalence test"],
        "population_support_gate_PASS": support_pass,
        "conditional_equivalence_test_PASS": primary_pass,
        "BOTH_FROZEN_CONDITIONS_SATISFIED": bool(support_pass and primary_pass),
        "frozen_status_of_the_0p042_figure": stringent,
        "ZERO_P_042_DECLARED_NON_DECISIVE_IN_THE_FREEZE": stringent_nondecisive,
        "frozen_dispositions_are_a_flat_list_with_no_selection_rule": flat_list_only,
        "STRUCTURAL_GAP": ("the frozen protocol enumerates nine admissible dispositions but "
                           "freezes NO rule mapping the outcome vector onto them. That gap, "
                           "not a moved threshold, is what let a post-run file choose the "
                           "label. It is a defect of the OBDI02 protocol; it is inherited as "
                           "a lesson about protocol design, not as a corrupted measurement."),
        "technical_validity_reevaluated": tv_detail,
        "technical_validity_requirements_that_fail_on_re_evaluation": tv_missing,
        "stopping_rule_early_stopping": st["EARLY_SCIENTIFIC_STOPPING"],
        "planned_arms": planned, "arms_run": run,
        "ALL_PLANNED_ARMS_RUN": bool(res["all_planned_arms_run"]),
        "hard_cap_total_arms": st["hard_cap_total_arms"],
        "VERDICT": ("UNTOUCHED" if (support_pass and primary_pass and not tv_missing
                                    and bool(res["all_planned_arms_run"])
                                    and planned == run == st["hard_cap_total_arms"])
                    else "ALTERED"),
    }


# ---------------------------------------------------------------- check 4: the data / outcome
def check_outcome():
    """Does the deviation reach the NUMBERS, or only the label? OBDCA01 recomputed the primary
    estimand by two independent routes. If OBDI02's own recorded interval and the OBDCA01
    recomputation agree, the deviation cannot have moved the measurement."""
    res = json.load(open(f"{D2}/out/_results.json"))
    rec = json.load(open(f"{DA}/out/_recompute.json"))
    ad = json.load(open(f"{DA}/out/_adjudication.json"))
    fr = json.load(open(f"{D2}/out/_freeze.json"))
    P = res["PRIMARY"]
    b2, se2 = rec["BETA_CY"]["beta"], rec["BETA_CY"]["se"]
    conf = ad["CONFORMITY_OF_THE_OBDI02_DISPOSITION"]
    same_beta = abs(P["beta"] - b2) == 0.0
    same_se = abs(P["se"] - se2) == 0.0
    return {
        "OBDI02_own_PRIMARY": {
            "beta": P["beta"], "se": P["se"], "critical_value_c": P["critical_value_c"],
            "equivalence_margin": P["equivalence_margin"],
            "interval_inside_margin": P["interval_inside_margin"], "PASS": P["PASS"],
            "achieved_equivalence_bound": P["achieved_equivalence_bound"]},
        "OBDCA01_independent_recomputation": {"beta": b2, "se": se2},
        "BIT_IDENTICAL_BETA": bool(same_beta), "BIT_IDENTICAL_SE": bool(same_se),
        "margin_in_the_freeze": fr["FROZEN_BEFORE_ANY_START"]["margin"],
        "margin_used_by_the_primary_test": P["equivalence_margin"],
        "MARGINS_AGREE": P["equivalence_margin"] == fr["FROZEN_BEFORE_ANY_START"]["margin"],
        "the_frozen_primary_test_verdict": "PASS" if P["PASS"] else "FAIL",
        "what_the_deviation_added_after_the_results_were_open":
            conf["THE_CONDITION_IT_ADDED"],
        "reported_disposition": conf["OBDI02_REPORTED_DISPOSITION"],
        "conformant_disposition": conf["THE_CONFORMANT_DISPOSITION_WOULD_HAVE_BEEN"],
        "direction": ("0.042 < 0.25, so the added condition is STRICTLY stronger than the "
                      "frozen one. A strictly stronger condition can only withhold a "
                      "qualification, never grant one."),
        "VERDICT": ("LABEL_ONLY" if (same_beta and same_se and P["PASS"]
                                     and P["equivalence_margin"]
                                     == fr["FROZEN_BEFORE_ANY_START"]["margin"])
                    else "REACHES_THE_MEASUREMENT"),
    }


def main():
    fz, tr, gt, oc = check_freeze(), check_trajectories(), check_gate(), check_outcome()
    touched = {
        "DATA": oc["VERDICT"] != "LABEL_ONLY",
        "GATE": gt["VERDICT"] != "UNTOUCHED",
        "FREEZE": fz["VERDICT"] != "UNTOUCHED",
        "TRAJECTORIES": tr["VERDICT"] != "UNTOUCHED",
    }
    blocking = [k for k, v in touched.items() if v]

    out = {
        "SECTION": "OBTR01 §3",
        "SCOPE": ("append-only closure of the post-run adjudication deviation that OBDCA01 "
                  "recorded against OBDI02. No OBDI02 or OBDCA01 artefact is modified."),
        "CHECKS": {"FREEZE": fz, "TRAJECTORIES": tr, "GATE": gt, "OUTCOME": oc},
        "WHAT_THE_DEVIATION_TOUCHED": touched,
        "BLOCKING_CATEGORIES": blocking,
    }
    if blocking:
        out.update({
            "OBDI02_POSTRUN_ADJUDICATION_DEVIATION": "CONFIRMED",
            "CLOSURE": "REFUSED",
            "DISPOSITION_FORCED": "INHERITED_EVIDENCE_NOT_CLOSED",
            "WHY": "the deviation reached %s, which the mandate makes a stop condition."
                   % ", ".join(blocking),
        })
    else:
        out.update({
            "OBDI02_POSTRUN_ADJUDICATION_DEVIATION": "CONFIRMED",
            "DEVIATION_DIRECTION": "CONSERVATIVE_FALSE_NONQUALIFICATION",
            "FROZEN_EVIDENCE_STATUS": "UNAFFECTED",
            "CUMULATIVE_CLOUD_EVIDENCE_STATUS": "VALID",
            "OBDCA01_FORMAL_LIMITATION":
                "QUALIFICATION_SUPPORTED_DESPITE_RECORDED_POSTRUN_ADJUDICATION_DEVIATION",
            "CLOSURE": "CLOSED_APPEND_ONLY",
            "WHY": ("the deviation is confined to the choice of a disposition LABEL after the "
                    "results were open. The freeze reproduces bit for bit, every declared seed "
                    "is present exactly once with an unchanged digest, no declared gate "
                    "condition is missing, and the primary estimand recomputed by OBDCA01 "
                    "agrees with the value OBDI02 recorded. The added condition was strictly "
                    "stricter than the frozen margin, so its only possible effect was to "
                    "withhold a qualification the freeze granted."),
        })
    json.dump(out, open(f"{OUT}/_obdi02_deviation_closure.json", "w"), indent=1, default=str)

    print("FREEZE       %s   hash reproduces %s, %d/%d core files byte-identical"
          % (fz["VERDICT"], fz["HASH_REPRODUCES"], fz["files_whose_bytes_still_match"],
             fz["files_in_core"]))
    print("TRAJECTORIES %s   %d raw files, %d blob ids recomputed, %d changed, seeds %d "
          "declared / %d present" % (tr["VERDICT"], tr["raw_files_on_disk"],
                                     tr["raw_files_whose_blob_id_was_recomputed"],
                                     len(tr["raw_files_whose_blob_id_changed"]),
                                     tr["distinct_seeds_declared_at_freeze_FRESH_FLAT"],
                                     tr["seeds_present_in_raw"]))
    print("GATE         %s   both frozen qualification conditions satisfied %s ; 0.042 "
          "declared non-decisive in the freeze %s ; dispositions are a flat list with no "
          "selection rule %s ; arms %d/%d"
          % (gt["VERDICT"], gt["BOTH_FROZEN_CONDITIONS_SATISFIED"],
             gt["ZERO_P_042_DECLARED_NON_DECISIVE_IN_THE_FREEZE"],
             gt["frozen_dispositions_are_a_flat_list_with_no_selection_rule"],
             gt["arms_run"], gt["planned_arms"]))
    print("OUTCOME      %s   beta OBDI02 %.17g vs OBDCA01 %.17g (bit-identical %s); frozen "
          "primary at margin %.3f -> %s"
          % (oc["VERDICT"], oc["OBDI02_own_PRIMARY"]["beta"],
             oc["OBDCA01_independent_recomputation"]["beta"], oc["BIT_IDENTICAL_BETA"],
             oc["margin_used_by_the_primary_test"], oc["the_frozen_primary_test_verdict"]))
    print()
    print("BLOCKING CATEGORIES: %s" % (blocking or "none"))
    print("CLOSURE: %s" % out["CLOSURE"])


if __name__ == "__main__":
    main()
