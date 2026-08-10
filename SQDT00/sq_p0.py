"""SQDT00 Section 0-1 -- parent provenance, blob binding, master-freeze hashing.

ZERO numeric loads. This module never opens an npz, a response row, a reader series or a score
vector. It touches only: git metadata resolved on the device, source files (as bytes), and the
freeze documents it hashes.
"""
from __future__ import annotations
import hashlib, json, os, subprocess, sys

OUT = "/home/claude/sweep/SQDT00"
SWEEP = "/home/claude/sweep"
PARENT = f"{SWEEP}/FWL2CF00"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def git_blob_id(path):
    """git blob object id computed locally: sha1('blob <len>\\0' + bytes)."""
    b = open(path, "rb").read()
    h = hashlib.sha1()
    h.update(b"blob " + str(len(b)).encode() + b"\x00")
    h.update(b)
    return h.hexdigest()


# ---------------------------------------------------------------- the chain, resolved on device
CHAIN = [
    ("e912a1004c5b9732d12a8fcc417002bfd1135622", "WSCCRP00"),
    ("f81daf91dd70a05f34372fb85d2c3fba0dd5550b", "WSFSCRP00 closure"),
    ("f9e1e39170a746bc5d8c43a80bc878cf24180714", "FSCMA00"),
    ("f65851c39496f379edac8b665dce87ba7cf1ebfb", "GIMB00"),
    ("0d92b612e051166b84d1a7d08d681ea78f5a512d", "GIMB00 delivery record"),
    ("226b2c93bdc34e5bec2ebc28d0c6066dc3123b14", "WL2SMF00"),
    ("2c9fc97c5e05de2b15ccceeba0c9bc36e327e3b0", "WL2SMF00 delivery record"),
    ("53c3ea7e8f9d4400fad2c998ee0eacc5ab917d2b", "FWL2CF00 commit 1, pre-execution"),
    ("30403fc1b15890f70f2504d454ffb8ea8ef2160c", "FWL2CF00 commit 2, sham reconstruction"),
    ("817c27886e97a90e2d54a410a65d9574654b1dc3", "FWL2CF00 commit 3, raw only"),
    ("09c56ae7e37ef22b08675a57e9ca609474d9c63e", "FWL2CF00 commit 4, decoded analysis"),
    ("e9a06286354284fe06fa15742a128919e3b64fcf", "FWL2CF00 commit 5, delivery repair"),
    ("96c7d295e72106cd949d810fa92807c2514e7449", "FWL2CF00 commit 6, provenance record"),
]

# every arrow verified on the device with `git rev-parse <child>^` and a parent-count check
ARROWS_VERIFIED_ON_DEVICE = 12
ARROWS_OK = 12

# committed top-level blob ids, read from the device object database with `git ls-tree`
DEVICE_TOPLEVEL = {
    "ACTIVE_ANALYSIS_PLAN.md": "11162a2e145805537cc662f851b8729a97b1f706",
    "ACTIVE_DISK_READBACK_CERTIFICATE.json": "4c86ee5bed3882a00ab566582a62f1df17dc0fe6",
    "ACTIVE_EXECUTION_AND_ACCESS_LEDGER.json": "9c8005d83aacda1520b7294e16ae45bc97965139",
    "ACTIVE_PHYSICAL_RUNTIME_ORACLE.json": "d91045b9275612f60eead3d7bf0ad5ef03b508a0",
    "CELL_WEIGHTED_L2_MATERIALITY_RESULTS.json": "c689ba560be1a95b917c77e9910297df4a2b312a",
    "EXACT_RESPONSE_AND_GAUGE_ORACLE.json": "53e37cc2d7b58657c6b882bb21a33fcfbd03c353",
    "FRESH_ACTIVE_CARRIER_RAW_MANIFEST.json": "d9cbeb4b69d683289fe5281566add67cfeaacee1",
    "FRESH_QUOTIENT_CERTIFICATE.json": "1d6e797c015868872d1d286d6310c0a67dde9043",
    "FROZEN_STRATUM_TRANSFER_REPORT.json": "850dd028b08743bf6fc1260f38b8a06e0fc666b2",
    "FWL2CF00_ACTIVE_PANEL_LOCK.json": "cdfdfcf8135d9a5e569efc887a98a584edc6779a",
    "FWL2CF00_ACTIVE_RAW_PANEL_LOCK.json": "498bf97d2c639ae906a4daf6db1733a6bfbe782e",
    "FWL2CF00_CANONICAL_SHAM_SERIES_LOCK.json": "2ccccdb550a0b3f0a02edb7f159713cec59d3ba1",
    "FWL2CF00_FINAL_DISPOSITION.json": "295ee9a3637214e77fe168462de2c8149482cf87",
    "FWL2CF00_FINAL_REPORT.md": "6d2c51dedc5b0a5709bd661dcb58c4f7c293c8e9",
    "FWL2CF00_MASTER_FREEZE.md": "e968d303b439b17c11c6d354529acb0e036ce7e6",
    "FWL2CF00_MASTER_FREEZE_HASHES.json": "6323cf93578855ea570c9da968b5cb93455255b7",
    "FWL2CF00_SHAM_RECONSTRUCTION_LOCK.json": "a6ff77fb090647a127106105be92c73181f1aece",
    "G1_H3_FACTORIAL_ATTRIBUTION_REPORT.json": "58ad99b4b0ddc35b006434d920dcc4d01d6ed439",
    "GIT_PROVENANCE_AND_FRESH_CLONE_VERIFICATION.md": "8060ad3750e01bb41f4d766b55ee4e3deef8c420",
    "INDEPENDENT_UNIT_AND_RANDOMIZATION_REPORT.md": "33ba9e7595c623d6ab4d4c77b3a4e5033d27673f",
    "PARENT_AND_FWL2CF00_CLAIM_LEDGER.md": "602ab774b38b9af09cef502b1e553e9aa489fa34",
    "PARENT_LOCK_AND_ARM_BINDING_MANIFEST.json": "fc34c75394c832d05cb346d3c7e4cb9af3bbb53d",
    "PREEXECUTION_NONVACUOUS_ORACLE_REPORT.json": "fced1f2acaac9041c7c5f0ed4be90e0e458c3ea3",
    "PROTOCOL_DEVIATIONS.md": "ba9d61c23b22fc668c6b69e7811e66827d4f26db",
    "SHA256SUMS": "2e54dbe0d7892cb5bd880d22fcd5521b149ad5b7",
    "SHAM_0_RECONSTRUCTED_RAW_MANIFEST.json": "82dbe10614419fd56b0b6114f0bb16d5cbbfcd88",
    "SHAM_DISK_READBACK_CERTIFICATE.json": "fc8a4f02ee596f91d5ebaae22aa0293a07ce83ef",
    "SHAM_RECONSTRUCTION_EXACT_ORACLE.json": "e9960ce8fe37336e5f73908ecad060a78c66e0ec",
    "UNCOMMITTED_FULL_FIELD_ARCHIVE_DIGESTS.json": "75166752ce940d1801d93101d4deba2c728f2572",
    "_analysis_core.json": "b5298b9e9e7163c69de80accfdffd45ffbac2e85",
    "_device_blobs.json": "8587394423f7a6652005127d1a3c20a2aa2a6dc8",
    "_eps.npy": "cc36f0a35caed17eb0f7d725365b7197ce64ca29",
    "_factor.json": "4edc3989d3224a5b9351183e48bace7e2cb38c12",
    "_provenance_raw.json": "5d942eec8e8dd122c3e2abd74cc4323fff641270",
    "_rows.json": "a6b848616eff2f975d7c3d485e93da95fee00135",
    "active_series.json": "e6c534ddfba665b14e2cecf84e8a128573c67887",
    "fw_active_driver.py": "73f8912495d6cefaef68568c8c9c0a7ecb038b80",
    "fw_analysis.py": "8edc15b7321cb5be5536de1c2699548e09aa68b3",
    "fw_compact.py": "0110e20d7d98632812b32b01e0b37065851d0380",
    "fw_factor.py": "da3a45d4ffe9f3d8bb0570f1425ba198f1bd6526",
    "fw_locks2.py": "978d3223c2e97743ed112a2f39dfddcaaff41001",
    "fw_oracle.py": "0e407573387582309a66dea91c4a4d5d9a176f78",
    "fw_p0.py": "9ef9d3fbdddac824a92180f1c82c0ac461858aad",
    "fw_prod.py": "d99e943c2a95c45f88989b6d216835728f827281",
    "fw_readback.py": "ac865e353c6268b73fce10415d94cfcdbd495fa1",
    "fw_ref.py": "7b1ad8410c35d5ca6b552aec2c528505b4d89ceb",
    "fw_sham_driver.py": "e7c254acfbff39548156b272a00dd339e26fa40f",
    "fw_sham_oracle.py": "3737b44dc3c32f3e7981986af664cbadc7e5099b",
    "fw_shamlock.py": "a9dfdb39e976d8a7de1f184cabbc48ab84a0c0c1",
    "fw_worker.py": "e640455ed7c0ef3fa4e34db7ea086997d33e28ab",
    "sham_series.json": "21c07776509366e295a2a1a31f9665b8226ae838",
}

DEVICE_SUBTREES = {
    "FWL2CF00": "159577eeb703d5878b2efe37737b535fddc29046",
    "WL2SMF00": "8b002dc2a86974af0beb442a1013895ef5b47e36",
    "GIMB00": "bc56bfb17107114048416e27287ee27901f94a57",
    "FSCMA00": "27a62919b9664ab8fdb114f17e51016cfc3ccb46",
}

# ---------------------------------------------------------------- bind blobs from local bytes
binding, mismatch = {}, []
for name, oid in sorted(DEVICE_TOPLEVEL.items()):
    p = f"{PARENT}/{name}"
    if not os.path.exists(p):
        binding[name] = {"committed": oid, "recomputed": None, "match": False,
                         "note": "absent from the working copy"}
        mismatch.append(name)
        continue
    r = git_blob_id(p)
    binding[name] = {"committed": oid, "recomputed": r, "match": r == oid,
                     "sha256": sha(p), "bytes": os.path.getsize(p)}
    if r != oid:
        mismatch.append(name)

# ---------------------------------------------------------------- the verified extraction
EXTRACTION = {
    "method": "git archive <commit> FWL2CF00 extracted into a temporary directory that had never "
              "been written by hand, on the device, straight out of the object database",
    "archive_sha256": "3314408308eea8b2a0bc8fa65a43c8cd2cf121d14aaac54b3c900c689c75b827",
    "archive_bytes": 1003520,
    "SHA256SUMS_entries": 198,
    "files_in_extracted_tree": 199,
    "verified_ok": 198, "failed": 0,
    "committed_SHA256SUMS_content_sha256":
        "051d3bdd2c502819d60535b30b48839bd65d490d7c10aea36605b31c5d363d95",
    "cloud_SHA256SUMS_content_sha256":
        "051d3bdd2c502819d60535b30b48839bd65d490d7c10aea36605b31c5d363d95",
    "cloud_container_verified_ok": 198, "cloud_container_failed": 0,
    "cross_implementation_subtree_id": {
        "device_git_2.34.1_from_object_database": "159577eeb703d5878b2efe37737b535fddc29046",
        "cloud_git_2.43.0_from_independently_held_bytes":
            "159577eeb703d5878b2efe37737b535fddc29046",
        "agree": True,
        "why_this_is_strong": "a git tree id is a pure content hash with no history dependence, "
                              "so agreement across two implementations on separately transferred "
                              "bytes certifies every blob id recursively, not just the 51 "
                              "top-level entries bound explicitly above",
    },
    "full_clone_attempted": True,
    "full_clone_outcome": "the device repository lives on a network mount; `git clone` and a "
                          "depth-14 `git fetch` both exceeded the 45 s bridge call limit. The "
                          "object-database extraction above plus the independent-container tree "
                          "recomputation is substituted, and is strictly stronger on content "
                          "while weaker only on object-graph traversal, which `git bundle "
                          "verify` supplies separately. Recorded as deviation D1.",
}

BUNDLE = {
    "path": "FWL2CF00.bundle (beside the FSCMA00, GIMB00 and WL2SMF00 bundles)",
    "git_bundle_verify": "ok",
    "contains_ref": "96c7d295e72106cd949d810fa92807c2514e7449 "
                    "refs/heads/dev/fresh-weighted-l2-carrier-factorial-00",
    "requires_prerequisite": "2c9fc97c5e05de2b15ccceeba0c9bc36e327e3b0",
    "sha256_on_disk_now": "012ccb1b85bf5bb276240a7328d50ab821c1f94729b32e51d0c091dcce502a6d",
    "sha256_recorded_in_parent_commit_6_text":
        "ef96b306a0b0541e7e8d9fd617b113a419c6b31203374c083d39d7754a6a3fe7",
    "digests_agree": False,
    "INHERITED_DISCREPANCY": "PARENT_BUNDLE_DIGEST_RECORD_IS_STALE_BY_ONE_APPEND_ONLY_COMMIT",
    "adjudication":
        "the digest recorded inside FWL2CF00 commit 6 was computed for the bundle as it stood "
        "before commit 6 existed, i.e. over tip e9a06286; the bundle was then rebuilt over the "
        "new tip 96c7d295 during delivery. The bundle now on disk verifies, carries the true "
        "branch tip and declares the correct single prerequisite, so provenance is sound. The "
        "parent record is NOT rewritten -- corrigenda are append-only -- and the discrepancy is "
        "carried forward here as an inherited, explained, non-blocking finding.",
}

prov = {
    "chain": [c for c, _ in CHAIN],
    "chain_labels": {c: lab for c, lab in CHAIN},
    "arrows_checked": ARROWS_VERIFIED_ON_DEVICE,
    "arrows_ok": ARROWS_OK,
    "every_arrow_is_a_single_direct_parent": ARROWS_OK == ARROWS_VERIFIED_ON_DEVICE,
    "parent_commit": "96c7d295e72106cd949d810fa92807c2514e7449",
    "parent_branch": "dev/fresh-weighted-l2-carrier-factorial-00",
    "owner_main_untouched": "f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77",
    "subtrees": DEVICE_SUBTREES,
    "extraction": EXTRACTION,
    "bundle": BUNDLE,
    "blob_binding": binding,
    "n_bound": len(binding),
    "n_mismatch": len(mismatch),
    "mismatches": mismatch,
    "support_restricted_sufficiency_certificate":
        "DEFERRED_TO_SECTION_2 -- verifying it requires reading the committed raw npz, which is a "
        "parent numeric load and is therefore forbidden until this freeze is committed.",
}
json.dump(prov, open(f"{OUT}/SQDT00_PARENT_ARTIFACT_BLOB_BINDING.json", "w"), indent=1)

# ---------------------------------------------------------------- freeze hashes
CODE = {
    "WSFSCRP00/wsfscrp_core.py": f"{SWEEP}/WSFSCRP00/wsfscrp_core.py",
    "ETCMNFC/etcmnfc_core.py": f"{SWEEP}/ETCMNFC/etcmnfc_core.py",
    "PPAI/ppai_core.py": f"{SWEEP}/PPAI/ppai_core.py",
    "PPAI/ppai_engine.py": f"{SWEEP}/PPAI/ppai_engine.py",
    "DOMC/domc_core.py": f"{SWEEP}/DOMC/domc_core.py",
    "FWL2CF00/fw_prod.py": f"{PARENT}/fw_prod.py",
    "FWL2CF00/fw_ref.py": f"{PARENT}/fw_ref.py",
    "FWL2CF00/fw_analysis.py": f"{PARENT}/fw_analysis.py",
    "FWL2CF00/fw_worker.py": f"{PARENT}/fw_worker.py",
}
FREEZE = {
    "frozen_before_any_parent_numeric_load": True,
    "hashes": {"SQDT00_MASTER_FREEZE.md": sha(f"{OUT}/SQDT00_MASTER_FREEZE.md")},
    "inherited_code_sha256": {k: sha(v) for k, v in CODE.items()},
    "H_GRID": [40 * i for i in range(1, 11)],
    "dt": "1/10",
    "weights": ["1/18"] + ["1/9"] * 8 + ["1/18"],
    "W_POST": "1",
    "materiality_coefficient": "0.01",
    "gauge": "exactly one A/B exchange per descendant, shared across all scored times, all arms "
             "and all doses",
    "gamma_low": 1, "gamma_high": 2, "third_dose_or_arm": False,
    "seed_namespace": {"queue": {
        "NEAR_a0": [66000, 66001, 66008, 66009],
        "NEAR_a1": [66002, 66003, 66010, 66011],
        "FAR_a0": [66004, 66005, 66012, 66013],
        "FAR_a1": [66006, 66007, 66014, 66015]},
        "disjoint_from": ["61000-61009", "62000-62009 RESERVED_AND_UNREAD", "63xxx",
                          "64000-64011", "65000-65007"],
        "never_generated_or_opened": "62000-62009"},
    "start_budget": {"panel": 16, "sham": 16, "active": 32, "total": 64, "other_or_diagnostic": 0,
                     "retries_or_replacements_after_panel_lock": 0},
    "forbidden_aliases": ["GIMB00_STRATUM_AXIS", "PARENT_FOUNDER_STRATUM",
                          "RECOVERED_PARENT_MODE", "HISTORICAL_SECOND_MODE"],
    "stop_precedence": ["S1 PARENT_PROVENANCE_UNRESOLVED",
                        "S2 OFFLINE_REDERIVATION_MISMATCH",
                        "S3 NO_P2_TRANSFER_LICENSE",
                        "S4 PARENT_DOSE_MULTIPLIER_NOT_BELOW_2__NO_FRESH_PANEL_LICENSE",
                        "S5 DOSE_2X_STATICALLY_INADMISSIBLE_OR_UNRESOLVED",
                        "S6 VACUOUS_ORACLE",
                        "S7 INSUFFICIENT_JOINTLY_ELIGIBLE_TARGET_BLOCKS"],
    "engine_starts_spent_at_freeze_time": 0,
}
json.dump(FREEZE, open(f"{OUT}/SQDT00_MASTER_FREEZE_HASHES.json", "w"), indent=1)

print("provenance : arrows %d/%d ok | blobs bound %d, mismatches %d"
      % (ARROWS_OK, ARROWS_VERIFIED_ON_DEVICE, len(binding), len(mismatch)))
print("extraction : 198/198 on device, 198/198 in cloud, subtree ids agree across git 2.34.1/2.43.0")
print("bundle     : verifies; digest record stale by one append-only commit (carried forward)")
print("freeze sha : " + FREEZE["hashes"]["SQDT00_MASTER_FREEZE.md"])
if mismatch:
    print("MISMATCHES:", mismatch)
