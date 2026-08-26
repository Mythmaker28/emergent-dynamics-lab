"""CLEA01 — digest verifier.

It does NOT regenerate the artefacts. That is the point of the declaration it carries: seven of the
ten CLEA01 artefacts were produced by inline code that was never committed, which is exactly the
OMLDCT01 failure mode that omldct02_hashes.py was written to prevent, recurring in a mission run by
the person who wrote that module. The checker found it and it is not argued away.

What this file can still do, and does, is make every recorded digest independently checkable: each
artefact carries a *_CONTENT_HASH computed by the parent's committed canonical rule, and this
recomputes all of them from the artefact bytes.
"""
from __future__ import annotations
import json, os, sys
REPO = os.environ.get("CLEA01_REPO", "/home/claude/edl")
sys.path.insert(0, f"{REPO}/OMLDCT02/code")
import omldct02_hashes as H

ARTEFACTS = {
 "CLEA01_PARENT_BINDING.json": "PARENT_BINDING_CONTENT_HASH",
 "CLEA01_IDENTITY_MODELS.json": "IDENTITY_MODELS_CONTENT_HASH",
 "CLEA01_CAUSAL_GRAPH_DEFINITION.json": "CAUSAL_GRAPH_CONTENT_HASH",
 "CLEA01_SPLIT_MANIFEST.json": "SPLIT_MANIFEST_CONTENT_HASH",
 "CLEA01_NONVACUITY_AND_SPECIFICITY.json": "NONVACUITY_CONTENT_HASH",
 "CLEA01_STRUCTURAL_GATES.json": "GATES_CONTENT_HASH",
 "CLEA01_CAUSAL_EMERGENCE_DIAGNOSTIC.json": "CAUSAL_EMERGENCE_CONTENT_HASH",
 # added at C4, after the checker was adjudicated and the disposition written. The two artefacts
 # below did not exist when this file was first committed at C3; they are verified by the same
 # rule, with no exception and no second rule.
 "CLEA01_CHECKER_ADJUDICATION.json": "ADJUDICATION_CONTENT_HASH",
 "CLEA01_FINAL_DISPOSITION.json": "DISPOSITION_CONTENT_HASH",
 # added at C5, the closure. Every one of these has a committed generating script, which is the
 # difference between this batch and the seven the checker found at C3.
 "CLEA01_CHECKER_RETURN_STATUS.json": "RETURN_STATUS_CONTENT_HASH",
 "CLEA01_CHECKER_SCOPE_AUDIT.json": "SCOPE_AUDIT_CONTENT_HASH",
 "CLEA01_PARENT_RECOMPUTATION.json": "PARENT_RECOMPUTATION_CONTENT_HASH",
 "CLEA01_CAUSAL_KERNEL_ADJUDICATION.json": "KERNEL_CONTENT_HASH",
 "CLEA01_HIDDEN_INPUT_AUDIT.json": "HIDDEN_INPUT_CONTENT_HASH",
 "CLEA01_FINAL_NONVACUITY_ADJUDICATION.json": "NONVACUITY_FINAL_CONTENT_HASH",
 "CLEA01_KNOWN_SUCCESS_ADJUDICATION.json": "KNOWN_SUCCESS_CONTENT_HASH",
 "CLEA01_AMBIENT_SPECIFICITY_ADJUDICATION.json": "AMBIENT_SPECIFICITY_CONTENT_HASH",
 "CLEA01_DEVELOPMENT_VALIDATION_CHRONOLOGY.json": "CHRONOLOGY_CONTENT_HASH",
 "CLEA01_IMPLEMENTATION_INDEPENDENCE_ADJUDICATION.json": "IMPLEMENTATION_INDEPENDENCE_CONTENT_HASH",
 "CLEA01_STRUCTURAL_GATES_FINAL.json": "GATES_FINAL_CONTENT_HASH",
 "CLEA01_CAUSAL_EMERGENCE_FINAL_STATUS.json": "CAUSAL_EMERGENCE_FINAL_CONTENT_HASH",
}
GENERATED_BY_COMMITTED_CODE = {
 "CLEA01_MATCHED_PAIR_MODEL_COMPARISON.json": "clea01_assemble.py",
 "CLEA01_MATCHED_PAIR_MODEL_COMPARISON.csv": "clea01_assemble.py",
 "CLEA01_IDENTITY_DISAGREEMENT_LEDGER.csv": "clea01_assemble.py",
 "CLEA01_CHECKER_RETURN_STATUS.json": "clea01_close_checker.py",
 "CLEA01_CHECKER_SCOPE_AUDIT.json": "clea01_close_checker.py",
 "CLEA01_CHECKER_ADJUDICATION.json": "clea01_close_checker.py",
 "CLEA01_CHECKER_ADJUDICATION.md": "clea01_close_checker.py",
 "CLEA01_PARENT_RECOMPUTATION.json": "clea01_close_parent.py",
 "CLEA01_CAUSAL_KERNEL_ADJUDICATION.json": "clea01_close_kernel.py + clea01_close_assemble.py",
 "CLEA01_HIDDEN_INPUT_AUDIT.json": "clea01_close_hidden.py",
 "CLEA01_FINAL_NONVACUITY_ADJUDICATION.json": "clea01_close_witness.py + clea01_close_assemble.py",
 "CLEA01_KNOWN_SUCCESS_ADJUDICATION.json": "clea01_close_witness.py + clea01_close_assemble.py",
 "CLEA01_AMBIENT_SPECIFICITY_ADJUDICATION.json":
     "clea01_close_specificity.py + clea01_close_assemble.py",
 "CLEA01_DEVELOPMENT_VALIDATION_CHRONOLOGY.json": "clea01_close_chronology.py",
 "CLEA01_IMPLEMENTATION_INDEPENDENCE_ADJUDICATION.json": "clea01_close_impl.py",
 "CLEA01_STRUCTURAL_GATES_FINAL.json": "clea01_close_gates.py",
 "CLEA01_CAUSAL_EMERGENCE_FINAL_STATUS.json": "clea01_close_gates.py",
 "CLEA01_FINAL_DISPOSITION.json": "clea01_close_final.py",
 "CLEA01_FINAL_REPORT.md": "clea01_close_final.py",
 "SHA256SUMS": "clea01_close_final.py",
}

def main():
    out = {"MISSION": "CLEA01", "SECTION": "digest verification",
           "THE_RULE": "H.content_digest of the artefact with its OWN hash key removed. "
             "content_digest already strips GENERATED_UTC. Stated here because the first version of "
             "this verifier omitted the key exclusion and reported all seven as unreproducible, and "
             "because three artefacts had been re-digested on documents that still carried their "
             "previous digest. Both defects were mine and both are fixed.",
           "DECLARED_DEFECT": "seven of the ORIGINAL ten artefacts have no committed generating "
             "script, and that is carried forward unchanged rather than retro-fitted: "
             "CLEA01_PARENT_BINDING.json, CLEA01_IDENTITY_MODELS.json, "
             "CLEA01_CAUSAL_GRAPH_DEFINITION.json, CLEA01_SPLIT_MANIFEST.json, "
             "CLEA01_NONVACUITY_AND_SPECIFICITY.json, CLEA01_STRUCTURAL_GATES.json and "
             "CLEA01_CAUSAL_EMERGENCE_DIAGNOSTIC.json. Every artefact produced by the C5 closure "
             "has a committed generator. Original text: seven of the ten artefacts have no "
             "committed generating script. "
             "Declared, not argued away. Their content digests are verifiable; their provenance is "
             "not reproducible from code.",
           "ARTEFACTS_WITH_A_COMMITTED_GENERATOR": GENERATED_BY_COMMITTED_CODE,
           "CHECKS": []}
    ok = True
    for f, key in ARTEFACTS.items():
        p = f"{REPO}/CLEA01/out/{f}"
        d = json.load(open(p))
        rec = d.get(key); got = H.content_digest(d, extra_excluded=(key,))
        good = rec == got
        ok &= good
        out["CHECKS"].append({"artefact": f, "key": key, "recorded": rec, "recomputed": got,
                              "REPRODUCIBLE": good, "file_sha256": H.file_sha256(p)})
    out["N_CHECKED"] = len(ARTEFACTS)
    out["N_REPRODUCIBLE"] = sum(1 for c in out["CHECKS"] if c["REPRODUCIBLE"])
    out["ALL_CONTENT_HASHES_REPRODUCE"] = ok
    json.dump(out, open(f"{REPO}/CLEA01/out/CLEA01_DIGEST_VERIFICATION.json", "w"), indent=1)
    for c in out["CHECKS"]:
        print(("REPRODUCIBLE  " if c["REPRODUCIBLE"] else "NOT REPRODUCIBLE ") + c["artefact"])
    print("ALL_CONTENT_HASHES_REPRODUCE =", ok)
    return ok

if __name__ == "__main__":
    main()
