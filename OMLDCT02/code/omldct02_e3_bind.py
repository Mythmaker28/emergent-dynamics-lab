"""OMLDCT02 — PRE_RUN_E3_QUALIFICATION, assembled from the fixture layer and the dual-classifier
world layer. Both classifiers are REBOUND here, not inherited by reference: each was re-run in this
mission over the same archives, and the world layer compares A against B directly rather than
against a stored number."""
from __future__ import annotations
import json, os, sys, datetime, ast, io, tokenize

REPO = os.environ.get("OMLDCT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "OMLDCT02", "code"))
import omldct02_hashes as H

FIELDS = ("t_m", "interval_end", "E3_DURATION", "E3_EXPOSURE", "identity_termination_type",
          "min_nY", "max_nY", "nY_histogram")

def independence(path, banned):
    """token-level scan: comments and string literals removed first. The naive scan over raw text
    reports a module that PROMISES not to use a name as if it used it — the same false-positive
    class as a bare 'ties' matching inside 'identities'."""
    src = open(path).read()
    toks = [t.string for t in tokenize.generate_tokens(io.StringIO(src).readline)
            if t.type not in (tokenize.COMMENT, tokenize.STRING)]
    code = " ".join(toks)
    imports = set()
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Import):
            for a in n.names: imports.add(a.name)
        elif isinstance(n, ast.ImportFrom): imports.add(n.module or "")
    return {"file": os.path.relpath(path, REPO), "imports": sorted(imports),
            "banned_in_executable_code": {b: (b in code) for b in banned},
            "banned_anywhere_including_prose": {b: (b in src) for b in banned},
            "scan_method": "tokenised; comments and string literals removed"}

def main():
    fx = json.load(open(f"{REPO}/OMLDCT02/out/OMLDCT02_E3_QUALIFICATION_FIXTURES.json"))
    dual = json.load(open(f"{REPO}/OMLDCT02/work/e3_dual26.json"))
    rows = []; produced = []; refused = []
    for tag in sorted(dual):
        d = dual[tag]; a, b = d["A"], d["B"]
        if a.get("OK") and b.get("OK"):
            eq = {f: (a.get(f) == b.get(f)) for f in FIELDS}
            r = {"tag": tag, "t_m": a.get("t_m"), "A_duration": a["E3_DURATION"],
                 "B_duration": b["E3_DURATION"], "A_exposure": a["E3_EXPOSURE"],
                 "B_exposure": b["E3_EXPOSURE"], "termination": a["identity_termination_type"],
                 "fields_equal": eq, "ALL_EQUAL": all(eq.values()),
                 "A_seconds": d.get("A_seconds"), "B_seconds": d.get("B_seconds")}
            produced.append(r)
        elif (not a.get("OK")) and (not b.get("OK")):
            r = {"tag": tag, "A_refused": a.get("REASON"), "B_refused": b.get("REASON"),
                 "BOTH_REFUSED": True, "ALL_EQUAL": True}
            refused.append(r)
        else:
            r = {"tag": tag, "A_OK": a.get("OK"), "B_OK": b.get("OK"),
                 "ONE_PRODUCED_WHERE_THE_OTHER_REFUSED": True, "ALL_EQUAL": False}
            produced.append(r)
        rows.append(r)
    world_pass = len(produced) == 22 and len(refused) == 4 and all(r["ALL_EQUAL"] for r in rows)
    banned = ["ldfma01", "omldct02_e3_a", "c_cid", "k_id", "TERMINAL_LABEL", "VERDICT",
              "descent_level", "identity_carried"]
    ind_b = independence(f"{REPO}/OMLDCT02/code/omldct02_e3_b.py", banned)
    ind_b["READS_NO_ONLINE_IDENTITY_OR_VERDICT_FIELD"] = not any(
        ind_b["banned_in_executable_code"][k] for k in ("c_cid", "k_id", "TERMINAL_LABEL", "VERDICT",
                                                        "descent_level", "identity_carried"))
    ind_b["SHARES_NO_IMPLEMENTATION_WITH_A"] = not any(
        i.startswith(("ldfma01", "omldct02_e3_a")) for i in ind_b["imports"])
    ind_pass = ind_b["READS_NO_ONLINE_IDENTITY_OR_VERDICT_FIELD"] and ind_b["SHARES_NO_IMPLEMENTATION_WITH_A"]
    st = fx["RANDOM_STRESS"]
    fixture_pass = bool(fx["FIXTURE_LAYER_PASS"] and fx["STRESS_LAYER_PASS"])
    overall = fixture_pass and world_pass and ind_pass
    doc = {
     "MISSION": "OMLDCT02", "SECTION": "PRE_RUN_E3_QUALIFICATION",
     "GENERATED_UTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
     "BOTH_CLASSIFIERS_REBOUND_IN_THIS_MISSION": True,
     "NOT_INHERITED_BY_REFERENCE": "the world layer re-ran BOTH classifiers over the same archives "
       "in this mission and compared them to each other. It does not compare B against a number "
       "stored during LDFMA01.",
     "CLASSIFIER_A": {"implementation": "LDFMA01/code/ldfma01_raw.py",
                      "adapter": "OMLDCT02/code/omldct02_e3_a.py",
                      "sha256_implementation": H.file_sha256(f"{REPO}/LDFMA01/code/ldfma01_raw.py"),
                      "sha256_adapter": H.file_sha256(f"{REPO}/OMLDCT02/code/omldct02_e3_a.py"),
                      "note": "the adapter calls A's components, centroid, link and running-identity "
                              "trace. It reimplements none of them and reads no removal ledger, so "
                              "it works on a SHAM arm."},
     "CLASSIFIER_B": {"implementation": "OMLDCT02/code/omldct02_e3_b.py",
                      "sha256": H.file_sha256(f"{REPO}/OMLDCT02/code/omldct02_e3_b.py")},
     "WHAT_THEY_SHARE": "raw archive inputs, the frozen constants L and CORE_R, and the endpoint "
                        "definition. Nothing else.",
     "WHAT_THEY_DO_NOT_SHARE": [
       "component finding — BFS flood-fill on a dense adjacency matrix against union-find over an "
       "enumerated edge list",
       "centroid accumulation — a Python loop against exact-integer numpy offsets",
       "the link rule — forward and backward candidate dicts against boolean matrix row and column "
       "counts",
       "the range test — math.hypot against squared distance, with every near-boundary comparison "
       "logged",
       "identity — running ids assigned to every component at every step against one identity "
       "chased forward from t_m",
       "exposure — a re-scan of membership after the trace against accumulation during the chase"],
     "INDEPENDENCE_AUDIT_B": ind_b, "INDEPENDENCE_PASS": ind_pass,
     "MANUAL_ANSWER_FIXTURES": {
       "n_component_cases": len([r for r in fx["FIXTURES"] if r["layer"] == "components"]),
       "n_centroid_cases": len([r for r in fx["FIXTURES"] if r["layer"] == "centroid"]),
       "n_link_cases": len([r for r in fx["FIXTURES"] if r["layer"] == "link"]),
       "each_carries_the_answer_written_out_by_hand": True,
       "why": "a case where BOTH implementations are wrong the same way is still caught",
       "PASS": bool(fx["FIXTURE_LAYER_PASS"])},
     "RANDOM_COMPONENT_FIXTURES": {"n": st["n_component_configurations"],
       "disagreements": st["n_component_disagreements"], "PASS": st["n_component_disagreements"] == 0},
     "RANDOM_IDENTITY_LINK_FIXTURES": {"n": st["n_link_configurations"],
       "disagreements": st["n_link_disagreements"], "PASS": st["n_link_disagreements"] == 0},
     "DEVELOPMENTAL_REMOVAL_WORLDS": {"n": len(produced),
       "n_agreeing": sum(1 for r in produced if r["ALL_EQUAL"]),
       "fields_compared": list(FIELDS), "per_world": produced,
       "PASS": len(produced) == 22 and all(r["ALL_EQUAL"] for r in produced)},
     "NEGATIVE_CONTROLS": {"n": len(refused), "detail": refused,
       "what": "LAW_C worlds that triggered but did not carry the identity, so no removal was "
               "applied and no locked-daughter interval exists",
       "why_it_matters": "agreement on 22 productions is weaker than agreement on 22 productions "
                         "and 4 refusals. Neither classifier invents an interval where the other "
                         "produces none.",
       "PASS": len(refused) == 4 and all(r["ALL_EQUAL"] for r in refused)},
     "LOAD_BEARING_DISAGREEMENTS": [r["tag"] for r in rows if not r["ALL_EQUAL"]],
     "PROVEN_BLIND_REGION": {
       "what": "shrinking CORE_R squared by as little as 0.001 is detected; enlarging it by 0.1 is "
               "not.",
       "why": "cell separations are integers, so no squared separation lies in the open interval "
              "(25, 26); centroid separations lie on a quarter-integer squared lattice, so none "
              "lies in (25, 25.25). An enlargement inside those gaps cannot admit a pair and "
              "therefore cannot change any answer.",
       "falsifiable_prediction_made_before_testing": "the link layer stays blind at +0.24 and "
                                                     "becomes sensitive at exactly +0.25",
       "held": True,
       "conclusion": "the blind region is provably empty of realisable configurations. The "
                     "comparison is complete over the reachable space, and it is recorded here "
                     "because a comparison whose limits are unstated is not a qualification.",
       "link_rule_mutation": "resolving a split by preference instead of terminating — the most "
                             "dangerous silent change available — was caught."},
     "PRE_RUN_E3_QUALIFICATION": "PASS" if overall else "FAIL",
     "WORLDS_RUN": 0,
     "WHAT_THIS_DOES_NOT_DO": "it qualifies the instrument, not the hypothesis.",
     "REPRODUCTION_STATUS": "NOT_TESTED", "HEREDITY_STATUS": "NOT_TESTED",
    }
    doc["QUALIFICATION_CONTENT_HASH"] = H.content_digest(doc)
    json.dump(doc, open(f"{REPO}/OMLDCT02/out/OMLDCT02_E3_QUALIFICATION.json", "w"), indent=1)
    print("fixtures", fixture_pass, "| worlds", world_pass, f"({len(produced)} produced, {len(refused)} refused)",
          "| independence", ind_pass)
    print("PRE_RUN_E3_QUALIFICATION =", doc["PRE_RUN_E3_QUALIFICATION"])

if __name__ == "__main__":
    main()
