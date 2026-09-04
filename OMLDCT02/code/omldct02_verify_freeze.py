"""OMLDCT02 — independent verification that every frozen digest is recalculable.

Run this in a fresh clone. It reads only committed artefacts and committed generator code, recomputes
all four digests from first principles, and reports each as reproducible or not. This is the check
OMLDCT01 could not pass.
"""
from __future__ import annotations
import json, os, sys, datetime

REPO = os.environ.get("OMLDCT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "OMLDCT02", "code"))
import omldct02_hashes as H

def main(write=True):
    OUT = f"{REPO}/OMLDCT02/out"
    fz = json.load(open(f"{OUT}/OMLDCT02_MASTER_FREEZE.json"))
    side = json.load(open(f"{OUT}/OMLDCT02_MASTER_FREEZE.sha256.json"))
    seeds = json.load(open(f"{OUT}/OMLDCT02_SEED_MANIFEST.json"))
    meth = json.load(open(f"{OUT}/OMLDCT02_METHODS_MANIFEST.json"))
    forb = json.load(open(f"{OUT}/OMLDCT02_FORBIDDEN_SEEDS.json"))

    checks = []
    def chk(label, recorded, recomputed, how):
        checks.append({"label": label, "recorded": recorded, "recomputed": recomputed,
                       "REPRODUCIBLE": recorded == recomputed, "how": how})

    chk("FREEZE_CONTENT_HASH", fz["FREEZE_CONTENT_HASH"], H.content_digest(fz),
        "H.content_digest over the freeze with its digest fields and GENERATED_UTC removed")
    chk("FREEZE_FILE_SHA256", side["FREEZE_FILE_SHA256"],
        H.file_sha256(f"{OUT}/OMLDCT02_MASTER_FREEZE.json"), "sha256 of the freeze file's bytes")
    chk("METHODS_HASH", meth["METHODS_HASH"], H.methods_hash(meth["MODULES"]),
        "H.methods_hash over the recorded [path, sha256] list")
    chk("SEED_SET_HASH", seeds["SEED_SET_HASH"],
        H.seed_set_hash(seeds["BASE_SEEDS"] + seeds["RESERVE_SEEDS"]),
        "H.seed_set_hash over base then reserve in index order")
    chk("FORBIDDEN_SET_HASH", forb["FORBIDDEN_SET_HASH"], H.canonical_digest(forb["FORBIDDEN_SEEDS"]),
        "H.canonical_digest over the ascending forbidden list")

    # cross-checks that the freeze quotes the manifests it claims to bind
    cross = {
     "freeze_quotes_the_seed_manifest_hash": fz["SEED_SET_HASH"] == seeds["SEED_SET_HASH"],
     "freeze_quotes_the_methods_hash": fz["METHODS_HASH"] == meth["METHODS_HASH"],
     "freeze_quotes_the_forbidden_hash": fz["FORBIDDEN_SET_HASH"] == forb["FORBIDDEN_SET_HASH"],
     "sidecar_quotes_the_same_content_hash": side["FREEZE_CONTENT_HASH"] == fz["FREEZE_CONTENT_HASH"],
     "n_base_matches": fz["N_BASE_SEEDS"] == seeds["N_BASE"] == len(seeds["BASE_SEEDS"]),
     "n_reserve_matches": fz["N_RESERVE_SEEDS"] == seeds["N_RESERVE"] == len(seeds["RESERVE_SEEDS"]),
     "n_methods_matches": fz["N_METHODS_FILES"] == meth["N_FILES"] == len(meth["MODULES"]),
    }
    # every bound method file still byte-identical
    drift = [m["path"] for m in meth["MODULES"]
             if not os.path.exists(REPO + m["path"]) or H.file_sha256(REPO + m["path"]) != m["sha256"]]
    # every terminal string present
    terms = ["MATCHED_LOCKED_DAUGHTER_CONTROL_EFFECT_SUPPORTED",
             "MATCHED_LOCKED_DAUGHTER_CONTROL_EFFECT_NOT_DETECTED__INCONCLUSIVE_UNDER_FROZEN_POWER",
             "INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS", "OMLDCT02_TECHNICALLY_INVALID"]
    ok = (all(c["REPRODUCIBLE"] for c in checks) and all(cross.values()) and not drift
          and fz["TERMINAL_VOCABULARY"] == terms)
    doc = {"MISSION": "OMLDCT02", "SECTION": "freeze verification",
           "GENERATED_UTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "VERIFIER": "OMLDCT02/code/omldct02_verify_freeze.py — committed",
           "DIGEST_CHECKS": checks, "CROSS_CHECKS": cross,
           "BOUND_METHOD_FILES_BYTE_IDENTICAL": not drift, "DRIFTED": drift,
           "TERMINAL_VOCABULARY_EXACT": fz["TERMINAL_VOCABULARY"] == terms,
           "N_DIGESTS": len(checks),
           "N_REPRODUCIBLE": sum(1 for c in checks if c["REPRODUCIBLE"]),
           "ALL_HASHES_RECALCULABLE_FROM_FRESH_CLONE": all(c["REPRODUCIBLE"] for c in checks),
           "HASH_RECIPES_COMMITTED": True,
           "FREEZE_VERIFICATION": "PASS" if ok else "FAIL"}
    if write:
        json.dump(doc, open(f"{OUT}/OMLDCT02_FREEZE_VERIFICATION.json", "w"), indent=1)
    for c in checks:
        print(("REPRODUCIBLE  " if c["REPRODUCIBLE"] else "NOT REPRODUCIBLE ") + c["label"])
    print("cross checks:", all(cross.values()), "| method drift:", drift or "none")
    print("FREEZE_VERIFICATION =", doc["FREEZE_VERIFICATION"])
    return doc

if __name__ == "__main__":
    main()
