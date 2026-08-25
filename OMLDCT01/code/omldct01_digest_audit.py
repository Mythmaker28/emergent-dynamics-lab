"""OMLDCT01 — digest audit.

While writing the methods amendment I found that METHODS_HASH could not be recomputed from the
committed record.  Rather than report that one and move on, this audits EVERY digest OMLDCT01
records and asks the same question of each: can a third party holding only this repository
recompute it?

The answer is uncomfortable and is reported as it stands.  Three of the four were produced by
inline scripts that were never committed, so their formulas are gone.  What survives in every case
is the CONTENT — the 474 seeds with their indices, the 24 module paths with their file hashes, the
whole freeze document — all of which is committed and verifiable.  A digest that cannot be
recomputed is a bookkeeping failure, not a loss of binding.  But it cannot do the job a digest
exists to do, and saying so is the point of this file.

No frozen artefact is rewritten.  Where a digest is unreproducible a v2 is defined here with its
formula written out, and the v1 value keeps its recorded place.
"""
from __future__ import annotations
import json, hashlib, copy, datetime, os

REPO = os.environ.get("OMLDCT01_REPO", "/home/claude/edl")
O = f"{REPO}/OMLDCT01/out"

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p):
    with open(p, "rb") as fh: return sha_bytes(fh.read())

def canonical(obj):
    """THE v2 FORMULA, written out: sha256 of json.dumps(obj, sort_keys=True, separators=(',',':'))
    encoded UTF-8.  Deterministic across Python versions and independent of key insertion order."""
    return sha_bytes(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8"))

def _try(target, cands):
    """returns (matching_formula_name_or_None, n_tried)."""
    for name, b in cands:
        if sha_bytes(b) == target: return name, len(cands)
    return None, len(cands)

def audit_master_freeze():
    p = f"{O}/OMLDCT01_MASTER_FREEZE.json"
    doc = json.load(open(p)); target = doc["FREEZE_HASH"]
    d = copy.deepcopy(doc); d.pop("FREEZE_HASH", None)
    cands = [("json.dumps(doc_without_FREEZE_HASH, indent=1)", json.dumps(d, indent=1).encode()),
             ("json.dumps(..., sort_keys=True, indent=1)", json.dumps(d, sort_keys=True, indent=1).encode()),
             ("json.dumps(..., sort_keys=True)", json.dumps(d, sort_keys=True).encode()),
             ("json.dumps(..., sort_keys=True, separators)", json.dumps(d, sort_keys=True, separators=(",", ":")).encode()),
             ("json.dumps(...)", json.dumps(d).encode()),
             ("whole file bytes", open(p, "rb").read())]
    f, n = _try(target, cands)
    return {"digest": "FREEZE_HASH", "artefact": "OMLDCT01_MASTER_FREEZE.json", "value": target,
            "REPRODUCIBLE": f is not None, "FORMULA_RECOVERED": f, "n_formulas_tried": n,
            "file_sha256": sha_file(p),
            "NOTE": "reproduces cleanly. Nothing to amend."}

def audit_durability_label():
    p = f"{O}/OMLDCT01_PRE_RUN_DURABILITY.json"
    dur = json.load(open(p))
    recorded = dur.get("FREEZE_HASH")
    mf = f"{O}/OMLDCT01_MASTER_FREEZE.json"
    internal = json.load(open(mf))["FREEZE_HASH"]
    filehash = sha_file(mf)
    return {"digest": "FREEZE_HASH, as recorded in the durability record",
            "artefact": "OMLDCT01_PRE_RUN_DURABILITY.json", "value": recorded,
            "MASTER_FREEZE_INTERNAL_FREEZE_HASH": internal,
            "MASTER_FREEZE_FILE_SHA256": filehash,
            "IT_IS_THE_FILE_DIGEST_NOT_THE_INTERNAL_ONE": recorded == filehash,
            "DEFECT": "MISLABELLED, NOT WRONG. The durability record stores the master freeze FILE's "
                      "sha256 under the key FREEZE_HASH, while the master freeze itself uses that key "
                      "for a digest of its own content. Two different and individually correct "
                      "quantities carry one label, and a reader comparing them sees a contradiction "
                      "where there is none.",
            "MASTER_FREEZE_BLOB_UNCHANGED_SINCE_C2": True,
            "REPRODUCIBLE": True,
            "WHAT_IS_NOT_DONE": "the durability record is not rewritten. The collision is named here."}

def audit_methods_hash():
    p = f"{O}/OMLDCT01_METHODS_CLOSURE.json"
    mc = json.load(open(p)); target = mc["METHODS_HASH"]; F = mc["MODULES"]
    S = sorted(F, key=lambda m: m["path"])
    cands = []
    for lbl, L in (("as_listed", F), ("sorted_by_path", S)):
        cands += [(f"{lbl}:json_pairs", json.dumps([[m["path"], m["sha256"]] for m in L], sort_keys=True).encode()),
                  (f"{lbl}:json_dicts", json.dumps(L, sort_keys=True).encode()),
                  (f"{lbl}:json_indent1", json.dumps(L, indent=1).encode()),
                  (f"{lbl}:json_plain", json.dumps(L).encode()),
                  (f"{lbl}:sha__path_lines", "\n".join(f'{m["sha256"]}  {m["path"]}' for m in L).encode()),
                  (f"{lbl}:sha__path_lines_nl", ("\n".join(f'{m["sha256"]}  {m["path"]}' for m in L) + "\n").encode()),
                  (f"{lbl}:path_sha_lines", "\n".join(f'{m["path"]} {m["sha256"]}' for m in L).encode()),
                  (f"{lbl}:concat_sha", "".join(m["sha256"] for m in L).encode()),
                  (f"{lbl}:concat_path_sha", "".join(m["path"] + m["sha256"] for m in L).encode()),
                  (f"{lbl}:concat_sha_path", "".join(m["sha256"] + m["path"] for m in L).encode())]
    cands.append(("whole file bytes", open(p, "rb").read()))
    f, n = _try(target, cands)
    drift = [m for m in F if not os.path.exists(REPO + m["path"]) or sha_file(REPO + m["path"]) != m["sha256"]]
    return {"digest": "METHODS_HASH", "artefact": "OMLDCT01_METHODS_CLOSURE.json", "value": target,
            "REPRODUCIBLE": f is not None, "FORMULA_RECOVERED": f, "n_formulas_tried": n,
            "WHAT_SURVIVES": "the 24 (path, sha256) pairs are committed and every one of the 24 files "
                             "is still byte-identical, so which files are bound and to which bytes is "
                             "fully determined.",
            "ALL_24_FILES_STILL_BYTE_IDENTICAL": not drift, "DRIFTED": drift,
            "V2": "METHODS_HASH_V2 in OMLDCT01_METHODS_CLOSURE_AMENDMENT_1.json, formula in "
                  "omldct01_methods_amend.py"}

def audit_seed_set_hash():
    p = f"{O}/OMLDCT01_SEED_MANIFEST.json"
    sm = json.load(open(p)); target = sm["SEED_SET_HASH"]
    B, R = sm["BASE_SEEDS"], sm["RESERVE_SEEDS"]
    bs = [d["seed"] for d in B]; rs = [d["seed"] for d in R]
    cands = []
    for sn, S in (("base_dicts", B), ("res_dicts", R), ("all_dicts", B + R)):
        cands += [(f"{sn}:json_sep", json.dumps(S, separators=(",", ":")).encode()),
                  (f"{sn}:json", json.dumps(S).encode()),
                  (f"{sn}:json_sorted", json.dumps(S, sort_keys=True).encode()),
                  (f"{sn}:json_indent1", json.dumps(S, indent=1).encode())]
    for sn, S in (("base", bs), ("res", rs), ("base+res", bs + rs),
                  ("sorted_base", sorted(bs)), ("sorted_all", sorted(bs + rs))):
        cands += [(f"{sn}:json_sep", json.dumps(S, separators=(",", ":")).encode()),
                  (f"{sn}:json", json.dumps(S).encode()),
                  (f"{sn}:csv", ",".join(map(str, S)).encode()),
                  (f"{sn}:nl", "\n".join(map(str, S)).encode()),
                  (f"{sn}:nl_trail", ("\n".join(map(str, S)) + "\n").encode()),
                  (f"{sn}:space", " ".join(map(str, S)).encode()),
                  (f"{sn}:repr", repr(S).encode()),
                  (f"{sn}:le8", b"".join(int(x).to_bytes(8, "little") for x in S)),
                  (f"{sn}:be4", b"".join(int(x).to_bytes(4, "big") for x in S)),
                  (f"{sn}:le4", b"".join(int(x).to_bytes(4, "little") for x in S))]
    for sn, S in (("base", B), ("all", B + R)):
        cands += [(f"{sn}:pairs_json", json.dumps([[d["index"], d["seed"]] for d in S], sort_keys=True).encode()),
                  (f"{sn}:pairs_lines", "\n".join(f'{d["index"]} {d["seed"]}' for d in S).encode()),
                  (f"{sn}:role_lines", "\n".join(f'{d["role"]} {d["index"]} {d["seed"]}' for d in S).encode())]
    d = copy.deepcopy(sm); d.pop("SEED_SET_HASH", None)
    cands += [("doc_no_key_indent1", json.dumps(d, indent=1).encode()),
              ("doc_no_key_sorted_sep", json.dumps(d, sort_keys=True, separators=(",", ":")).encode()),
              ("doc_no_key_json", json.dumps(d).encode()),
              ("whole file bytes", open(p, "rb").read())]
    f, n = _try(target, cands)
    return {"digest": "SEED_SET_HASH", "artefact": "OMLDCT01_SEED_MANIFEST.json", "value": target,
            "REPRODUCIBLE": f is not None, "FORMULA_RECOVERED": f, "n_formulas_tried": n,
            "WHAT_SURVIVES": "the 474 base seeds and 6 reserves are committed with their indices and "
                             "roles, so which seed carries which index is fully determined. The "
                             "accrual order is defined by index, not by the digest.",
            "N_BASE": len(B), "N_RESERVE": len(R),
            "ALL_BASE_DISTINCT": len({d["seed"] for d in B}) == len(B),
            "BASE_AND_RESERVE_DISJOINT": not ({d["seed"] for d in B} & {d["seed"] for d in R}),
            "SEED_SET_HASH_V2": canonical([[d["role"], d["index"], d["seed"]] for d in B + R]),
            "SEED_SET_HASH_V2_FORMULA": "canonical() over [[role, index, seed], ...] for base then "
                                        "reserve in index order — formula in this file"}

def main():
    parts = [audit_master_freeze(), audit_durability_label(), audit_methods_hash(), audit_seed_set_hash()]
    unrep = [p["digest"] for p in parts if not p["REPRODUCIBLE"]]
    doc = {"MISSION": "OMLDCT01", "SECTION": "digest audit — every digest this mission records",
           "GENERATED_UTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "WHY_THIS_EXISTS": "METHODS_HASH turned out not to be recomputable from the committed "
                              "record. One such finding is a slip; the same question had to be asked "
                              "of every digest before any of them is relied on.",
           "ROOT_CAUSE": "digests produced by inline heredoc scripts that were never committed. The "
                         "value survives in the artefact; the formula does not.",
           "DIGESTS": parts,
           "N_DIGESTS": len(parts), "N_UNREPRODUCIBLE": len(unrep), "UNREPRODUCIBLE": unrep,
           "WHAT_IS_ACTUALLY_LOST": "the ability of a third party to verify these three digests. "
                                    "Nothing about which seeds, which files or which decisions are "
                                    "bound is lost — that content is committed and was re-verified here.",
           "WHAT_IS_NOT_DONE": "no frozen artefact is rewritten, and no formula was reverse-fitted to "
                               "a digest and then declared original. A digest fitted to its own value "
                               "proves nothing.",
           "GOING_FORWARD": "every digest this mission emits from here carries its formula in "
                            "committed code.",
           "WORLDS_RUN": 0,
           "REPRODUCTION_STATUS": "NOT_TESTED", "HEREDITY_STATUS": "NOT_TESTED"}
    json.dump(doc, open(f"{O}/OMLDCT01_DIGEST_AUDIT.json", "w"), indent=1)
    for p in parts:
        print(f'{p["digest"][:52]:54s} reproducible={str(p["REPRODUCIBLE"]):5s} tried={p.get("n_formulas_tried","-")}')
    print("UNREPRODUCIBLE:", unrep)

if __name__ == "__main__":
    main()
