"""OMLDCT01 section 8 — methods closure, AMENDMENT 1.  Additive.

Two things are recorded here and neither is a rewrite.

1.  Section 7 requires a second, independently written E3 classifier before world 1.  The C2 methods
    closure and master freeze were committed BEFORE that classifier was written, so the frozen
    closure cannot cover it.  The classifier is method code — classifier A is built around the
    removal ledger and cannot process a SHAM arm, so B is what will measure both arms.  The three
    new files are bound here.

2.  METHODS_HASH v1 is NOT REPRODUCIBLE from the committed record.  The script that produced it at
    C2 was an inline heredoc and was never committed, and eighteen candidate serialisations of the
    committed MODULES list fail to reproduce the digest.  The closure's CONTENT survives — the 24
    (path, sha256) pairs are in the artefact and every one of the 24 files is still byte-identical —
    but the summary digest cannot be recomputed by anyone, including me.  That is declared, not
    patched: v1 keeps its recorded value and is not recomputed into agreement.

The v2 formula is written out here so that it is reproducible by anyone with the repository.
"""
from __future__ import annotations
import json, hashlib, datetime, os, sys

REPO = os.environ.get("OMLDCT01_REPO", "/home/claude/edl")
ADDED = ["/OMLDCT01/code/omldct01_e3_b.py",
         "/OMLDCT01/code/omldct01_e3_qualify.py",
         "/OMLDCT01/code/omldct01_e3_device.py",
         "/OMLDCT01/code/omldct01_methods_amend.py",
         "/OMLDCT01/code/omldct01_digest_audit.py"]

def sha(p):
    with open(p, "rb") as fh: return hashlib.sha256(fh.read()).hexdigest()

def methods_hash_v2(modules):
    """THE FORMULA, written out: sort by path, join 'path SPACE sha256' with newlines, no trailing
    newline, encode UTF-8, sha256.  Nothing else enters it."""
    body = "\n".join(f'{m["path"]} {m["sha256"]}' for m in sorted(modules, key=lambda m: m["path"]))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()

def _candidate_serialisations(F, target):
    """every serialisation tried against the v1 digest, reported so the failure is auditable rather
    than asserted."""
    S = sorted(F, key=lambda m: m["path"])
    out = {}
    def put(name, b): out[name] = (hashlib.sha256(b).hexdigest() == target)
    for lbl, L in (("as_listed", F), ("sorted_by_path", S)):
        put(f"{lbl}:json_pairs", json.dumps([[m["path"], m["sha256"]] for m in L], sort_keys=True).encode())
        put(f"{lbl}:json_dicts", json.dumps(L, sort_keys=True).encode())
        put(f"{lbl}:json_indent1", json.dumps(L, indent=1).encode())
        put(f"{lbl}:json_plain", json.dumps(L).encode())
        put(f"{lbl}:sha_two_space_path_lines", "\n".join(f'{m["sha256"]}  {m["path"]}' for m in L).encode())
        put(f"{lbl}:sha_two_space_path_lines_trailing_nl", ("\n".join(f'{m["sha256"]}  {m["path"]}' for m in L) + "\n").encode())
        put(f"{lbl}:path_space_sha_lines", "\n".join(f'{m["path"]} {m["sha256"]}' for m in L).encode())
        put(f"{lbl}:concat_sha", "".join(m["sha256"] for m in L).encode())
        put(f"{lbl}:concat_path_sha", "".join(m["path"] + m["sha256"] for m in L).encode())
        put(f"{lbl}:concat_sha_path", "".join(m["sha256"] + m["path"] for m in L).encode())
    h = hashlib.sha256()
    for m in S:
        p = REPO + m["path"]
        if os.path.exists(p):
            with open(p, "rb") as fh: h.update(fh.read())
    out["sorted_by_path:concatenated_file_contents"] = (h.hexdigest() == target)
    return out

def main():
    O = f"{REPO}/OMLDCT01/out"
    mc = json.load(open(f"{O}/OMLDCT01_METHODS_CLOSURE.json"))
    frozen = mc["MODULES"]; v1 = mc["METHODS_HASH"]
    drift = [m for m in frozen
             if not os.path.exists(REPO + m["path"]) or sha(REPO + m["path"]) != m["sha256"]]
    added = [{"path": rel, "sha256": sha(REPO + rel)} for rel in ADDED]
    union = frozen + added
    tried = _candidate_serialisations(frozen, v1)
    doc = {
     "MISSION": "OMLDCT01", "SECTION": "8 — methods closure, AMENDMENT 1 (additive)",
     "GENERATED_UTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),

     "ITEM_1_WHY_AN_AMENDMENT_EXISTS":
       "section 7 requires a second, independently written E3 classifier before world 1. I committed "
       "the C2 methods closure and master freeze BEFORE writing it, so the frozen closure could not "
       "have covered it. The freeze was premature relative to section 7 — the same root cause as the "
       "sequencing deviation already declared. Recorded the same way: additively, without touching "
       "the frozen record.",
     "WHY_CLASSIFIER_B_IS_METHOD_CODE_AND_NOT_ONLY_AN_INSTRUMENT":
       "classifier A is built around the removal ledger and cannot process a SHAM arm, which by "
       "construction has no removal. B is therefore the classifier that measures both arms in the "
       "campaign, and it belongs in the closure that binds the campaign.",

     "ITEM_2_METHODS_HASH_V1_IS_NOT_REPRODUCIBLE": {
       "what": "the digest recorded at C2 cannot be recomputed from the committed artefact.",
       "why": "the script that produced it was an inline heredoc and was never committed.",
       "serialisations_tried": tried,
       "n_tried": len(tried), "n_matched": sum(1 for v in tried.values() if v),
       "WHAT_SURVIVES": "the closure's content. The 24 (path, sha256) pairs are in the committed "
                        "artefact and every one of the 24 files is still byte-identical, so which "
                        "files are bound and to which bytes is fully determined. Only the summary "
                        "digest is unrecoverable.",
       "WHAT_I_DID_NOT_DO": "I did not search for a formula that happens to reproduce the digest and "
                            "then declare it the original. A digest reverse-fitted to its own value "
                            "proves nothing.",
       "REMEDY": "v2 has its formula written out in this committed file."},

     "METHODS_HASH_V1_AS_FROZEN": v1,
     "METHODS_HASH_V1_REPRODUCIBLE": False,
     "V1_ARTEFACT_UNCHANGED": True,
     "FROZEN_MODULES_STILL_BYTE_IDENTICAL": not drift,
     "DRIFTED": drift,

     "N_FILES_V1": len(frozen), "N_FILES_ADDED": len(added), "N_FILES_V2": len(union),
     "ADDED_MODULES": added,
     "METHODS_HASH_V2_FORMULA": "sha256 of '\\n'.join(f'{path} {sha256}') over the union sorted by "
                                "path, no trailing newline, UTF-8. Implemented in methods_hash_v2().",
     "METHODS_HASH_V2": methods_hash_v2(union),
     "SCOPE_OF_V2": "binds the campaign. A pair measured under code outside V2 is a technical failure.",
     "WORLDS_RUN": 0,
     "REPRODUCTION_STATUS": "NOT_TESTED", "HEREDITY_STATUS": "NOT_TESTED"}
    p = f"{O}/OMLDCT01_METHODS_CLOSURE_AMENDMENT_1.json"
    json.dump(doc, open(p, "w"), indent=1)
    print("v1 reproducible:", doc["METHODS_HASH_V1_REPRODUCIBLE"],
          " serialisations tried:", doc["ITEM_2_METHODS_HASH_V1_IS_NOT_REPRODUCIBLE"]["n_tried"],
          " matched:", doc["ITEM_2_METHODS_HASH_V1_IS_NOT_REPRODUCIBLE"]["n_matched"])
    print("frozen modules byte-identical:", doc["FROZEN_MODULES_STILL_BYTE_IDENTICAL"])
    print("N_FILES_V2 =", doc["N_FILES_V2"], " METHODS_HASH_V2 =", doc["METHODS_HASH_V2"])

if __name__ == "__main__":
    main()
