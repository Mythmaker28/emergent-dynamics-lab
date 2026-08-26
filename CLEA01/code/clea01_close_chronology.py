"""CLEA01 closure §10 — split chronology and validation isolation, with the evidence that survives.

Two things must be separated, and the audit did not separate them.

  CONTENT. The split is a deterministic function of the parent tip, a constant string and the base
  seed. Anyone can recompute it. This file does, from scratch, and then checks that the DEVELOPMENT
  and VALIDATION index sets recorded in the manifest are exactly the sets that the 20:04 and 20:22
  result files were actually computed over. That check is independent of every timestamp.

  ORDERING. Whether the manifest existed before the per-pair evaluation. Here the record is weaker
  than it was, and the reason is mine: re-digesting four artefacts at 21:08 under the corrected hash
  rule overwrote their mtimes. The original mtimes were observed by the independent checker at 21:06
  and survive only inside its verbatim return, which was written and hashed before the overwrite.
  That is stated rather than glossed. A structural argument that does NOT depend on any mtime is
  given alongside it.
"""
from __future__ import annotations
import datetime as dt, hashlib, json, os, subprocess, sys
REPO = os.environ.get("CLEA01_REPO", "/home/claude/edl")
sys.path.insert(0, f"{REPO}/OMLDCT02/code")
import omldct02_hashes as H

TIP = "84000ff3a67fd4e550934313019decda05219da0"


def recompute_split(tip, seeds_by_index, n_dev):
    rows = []
    for idx, seed in sorted(seeds_by_index.items()):
        d = hashlib.sha256(f"{tip}|CLEA01|{seed}".encode()).hexdigest()
        rows.append({"index": idx, "seed": seed, "digest": d, "key": int(d[:16], 16)})
    rows.sort(key=lambda r: (r["key"], r["index"]))
    for i, r in enumerate(rows):
        r["SPLIT"] = "DEVELOPMENT" if i < n_dev else "VALIDATION"
    return {r["index"]: r for r in rows}


def main():
    sm = json.load(open(f"{REPO}/CLEA01/out/CLEA01_SPLIT_MANIFEST.json"))
    pairs = {p["index"]: p for p in sm["PAIRS"]}
    led = [json.loads(l) for l in open(f"{REPO}/OMLDCT02/work/OMLDCT02_SEALED_LEDGER.jsonl") if l.strip()]
    adm = {r["index"]: r for r in led if r.get("ADMISSIBLE")}
    seeds = {i: r["seed"] for i, r in adm.items()}
    n_dev = sum(1 for p in sm["PAIRS"] if p["SPLIT"] == "DEVELOPMENT")

    rec = recompute_split(TIP, seeds, n_dev)
    disagree = [i for i in pairs if pairs[i]["SPLIT"] != rec[i]["SPLIT"]]
    dig_ok = sum(1 for i in pairs
                 if str(pairs[i].get("split_digest_first16", "")) == rec[i]["digest"][:16])

    dev_res = set(int(k) for k in json.load(open(f"{REPO}/CLEA01/work/dev_results.json")))
    val_res = set(int(k) for k in json.load(open(f"{REPO}/CLEA01/work/val_results.json")))
    man_dev = {i for i in pairs if pairs[i]["SPLIT"] == "DEVELOPMENT"}
    man_val = {i for i in pairs if pairs[i]["SPLIT"] == "VALIDATION"}

    def mt(p):
        try:
            return dt.datetime.fromtimestamp(os.path.getmtime(p), dt.timezone.utc).isoformat()
        except OSError:
            return None
    watch = ["code/clea01_lineage_i2.py", "code/clea01_lineage_i1.py", "code/clea01_run.py",
             "work/dev_results.json", "code/clea01_specificity.py", "work/dev_spec.json",
             "code/clea01_fixtures.py", "code/clea01_g4_containment.py",
             "work/val_results.json", "work/val_spec.json", "work/dev_g4.json", "work/val_g4.json",
             "code/clea01_assemble.py", "out/CLEA01_SPLIT_MANIFEST.json",
             "out/CLEA01_PARENT_BINDING.json", "out/CLEA01_IDENTITY_MODELS.json",
             "out/CLEA01_CAUSAL_GRAPH_DEFINITION.json", "review/CLEA01_CHECKER_RAW.txt"]
    mtimes = {w: mt(f"{REPO}/CLEA01/{w}") for w in watch}

    gl = subprocess.run(["git", "-C", REPO, "log", "--format=%H|%ad|%s", "--date=iso-strict",
                         "--", "CLEA01"], capture_output=True, text=True).stdout.strip().splitlines()

    doc = {
        "MISSION": "CLEA01", "SECTION": "10 — split chronology and validation isolation",
        "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
        "RECIPE": 'SHA256(f"{OMLDCT02_TIP}|CLEA01|{base_seed}") — sort ascending by the first 64 '
                  'bits with the pair index as tie-break, first 22 are DEVELOPMENT.',
        "OMLDCT02_TIP_USED": TIP,
        "N_PAIRS": len(pairs), "N_DEVELOPMENT": len(man_dev), "N_VALIDATION": len(man_val),
        "RECOMPUTED_FROM_SCRATCH": True,
        "DIGEST_PREFIXES_MATCHING": dig_ok, "OF": len(pairs),
        "ASSIGNMENT_DISAGREEMENTS": disagree,
        "ASSIGNMENT_REPRODUCES": not disagree,
        "CONTENT_CHECK_INDEPENDENT_OF_ANY_TIMESTAMP": {
            "what": "the manifest's DEVELOPMENT and VALIDATION index sets are compared with the "
                    "index sets the two sweeps were actually run over. If the manifest had been "
                    "rewritten after the outcomes were known, these would no longer coincide.",
            "dev_results_indices_equal_manifest_DEVELOPMENT": dev_res == man_dev,
            "val_results_indices_equal_manifest_VALIDATION": val_res == man_val,
            "n_dev_results": len(dev_res), "n_val_results": len(val_res),
        },
        "ORDERING_EVIDENCE": {
            "SURVIVING_MTIMES": mtimes,
            "WHAT_I_DESTROYED": "CLEA01_PARENT_BINDING.json, CLEA01_IDENTITY_MODELS.json, "
                "CLEA01_CAUSAL_GRAPH_DEFINITION.json and CLEA01_SPLIT_MANIFEST.json all now carry "
                "mtime 21:08:50, because I re-digested them at 21:08 under the corrected hash rule. "
                "Their original mtimes are gone from the filesystem. This is my doing, not an "
                "accident of the environment, and it is recorded rather than worked around.",
            "WHAT_PRESERVES_THEM": "the independent checker read those mtimes at 21:06, before the "
                "overwrite, and its verbatim return records them: parent binding 19:52, identity "
                "models 19:54:34, split manifest 19:54:55, graph definition 19:57:27. That return "
                "was written, hashed and externalised before any finding was acted on. The evidence "
                "is therefore second-hand but its custody is intact.",
            "CHECKER_RETURN_SHA256": H.file_sha256(f"{REPO}/CLEA01/review/CLEA01_CHECKER_RAW.txt"),
            "A_STRUCTURAL_ARGUMENT_THAT_USES_NO_MTIME":
                "clea01_run.py cannot select the DEVELOPMENT indices without reading the split "
                "manifest; dev_results.json is its output and contains exactly the manifest's 22 "
                "DEVELOPMENT indices. So the manifest, with this assignment, existed before the "
                "first per-pair evaluation completed. The same holds for the validation sweep.",
            "GIT_CANNOT_CORROBORATE_THE_WITHIN_MISSION_ORDER":
                "all four CLEA01 commits were authored between 21:11 and 21:15, after the analysis. "
                "The mission was uncommitted while it ran — the checker's finding 9, accepted. Git "
                "attests to the content from C1 onward and to nothing before it.",
            "GIT_LOG": gl,
        },
        "INDEX_664": {
            "known_before_CLEA01": True,
            "SPLIT": pairs[664]["SPLIT"] if 664 in pairs else None,
            "ADJUDICATION": "it carries no distinguishing information. Its Model A duration is 0 in "
                            "both arms (terminal MERGE at the fork), so no split assignment of it "
                            "could move a gate. The checker tested six alternative encodings and "
                            "found 664 would have been VALIDATION under three of them, with no "
                            "effect. Prior knowledge of it is therefore not a leak that matters, "
                            "and it is disclosed rather than defended.",
        },
        "POST_A_CLAIM_FRACTION": {
            "added": "after the first development sweep (20:04) and before the validation set was "
                     "opened (20:22). Code mtime 20:12:43.",
            "introduces_a_rule_constant_or_threshold": False,
            "what_it_is": "a ratio of two sums under rules already frozen.",
            "why_it_was_added": "an ambient-inheritance test was required and the first sweep did "
                                "not record one.",
            "DOES_IT_CARRY_A_LOAD_BEARING_GATE_ALONE": False,
            "WHY_NOT": "G9's content does not depend on it. The same fact — that in the treated arm "
                       "CERTAIN equals the occupied set on every post-fork row — follows from "
                       "C_minus_B_exposure, which the FIRST development sweep recorded, and the "
                       "checker reproduced it by row-walking six pairs independently.",
            "DISCLOSURE_GAP_FOUND_BY_THE_CHECKER": "until the checker said so, the post-hoc status "
                       "lived only in a source docstring and in no externalised artefact.",
            "CLASSIFICATION": "POST_DEVELOPMENT_DIAGNOSTIC__DECLARED__NOT_LOAD_BEARING",
        },
        "G4_STRONG_CONTAINMENT_FORM": {
            "code_mtime": mtimes["code/clea01_g4_containment.py"],
            "written_after_the_development_sweep": True,
            "written_before_validation_opened": True,
            "direction": "it goes AGAINST the operator's own model — it is the test that produced "
                         "the two G4 failures. A post-hoc strengthening that costs the author is "
                         "not self-serving, but it is still post-hoc and is declared here.",
        },
        "VALIDATION_ISOLATION_VERDICT":
            "the content check passes with no timestamp involved, and every piece of code that "
            "touches the validation set has an mtime earlier than the validation sweep. The "
            "ordering rests partly on the checker's pre-overwrite observation rather than on the "
            "filesystem, and that weakening is mine.",
    }
    doc["CHRONOLOGY_CONTENT_HASH"] = H.content_digest(doc, extra_excluded=("CHRONOLOGY_CONTENT_HASH",))
    json.dump(doc, open(f"{REPO}/CLEA01/out/CLEA01_DEVELOPMENT_VALIDATION_CHRONOLOGY.json", "w"), indent=1)
    print("digest prefixes matching:", dig_ok, "/", len(pairs))
    print("assignment reproduces:", doc["ASSIGNMENT_REPRODUCES"], "disagreements:", disagree)
    print("dev indices == manifest DEVELOPMENT:", dev_res == man_dev, f"({len(dev_res)})")
    print("val indices == manifest VALIDATION:", val_res == man_val, f"({len(val_res)})")
    print("664 split:", doc["INDEX_664"]["SPLIT"])
    return doc


if __name__ == "__main__":
    main()
