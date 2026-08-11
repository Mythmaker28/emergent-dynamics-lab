"""FSQBT00 Section 1-2 -- provenance binding and freeze hashing. ZERO numeric science loads.
Binds git metadata, source files (as bytes) and the serialized basis object by blob id only."""
from __future__ import annotations
import hashlib, json, os
OUT = "/home/claude/sweep/FSQBT00"
SWEEP = "/home/claude/sweep"
SQDT = f"{SWEEP}/SQDT00"
FWL2 = "/tmp/ctree/FWL2CF00"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
def blob(p):
    b = open(p, "rb").read(); h = hashlib.sha1(); h.update(b"blob " + str(len(b)).encode() + b"\x00"); h.update(b); return h.hexdigest()

CHAIN = [
    ("16717582e7f0dfd371f21c56465e11113d8b6675", "SQDT00 commit 3 (provenance)"),
    ("0ebab0d8f3ca049325aaf74f76a9112b4c280460", "SQDT00 commit 2 (offline programme)"),
    ("740c025d39ab7f4718bd956e59a57f2a2b483c00", "SQDT00 commit 1 (master freeze)"),
    ("96c7d295e72106cd949d810fa92807c2514e7449", "FWL2CF00 commit 6 (science parent)"),
]
# arrows verified on the device: 16717582^=0ebab0d8, 0ebab0d8^=740c025d, 740c025d^=96c7d295
ARROWS_OK = 3

# serialized basis object, bound by committed git blob id (verified equal on device + locally)
BASIS_BLOBS = {
    "SQDT00/FWL2_RELATIVE_QUOTIENT_BASIS_V1.json": "07c9cf7e4eb3646bfbd32799de2618435f6e0353",
    "SQDT00/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz": "8f848411cd5a8ab4a483c217cd6b22c752ae8479",
    "SQDT00/sq_exact.py": "2b87da5341539b03fbad36e017d4bd6eb01a37da",
    "SQDT00/sq_offline.py": "3b8f9c2d42bda488262043ecdf03786a521af32f",
    "SQDT00/SQDT00_OFFLINE_REDERIVATION_AND_BASIS_CERTIFICATE.json":
        "1ad53803e1f66aee6394daa3ae9aab96fe3df2a7",
    "SQDT00/SQDT00_MASTER_FREEZE.md": "4fd5e9e35831f13616a0362d740fb6b66db3a168",
}
binding, mism = {}, []
for rel, committed in BASIS_BLOBS.items():
    p = f"{SWEEP}/{rel}"
    r = blob(p) if os.path.exists(p) else None
    binding[rel] = {"committed": committed, "recomputed": r, "match": r == committed}
    if r != committed:
        mism.append(rel)

prov = {
    "chain": [c for c, _ in CHAIN],
    "chain_labels": {c: l for c, l in CHAIN},
    "arrows_single_direct_parent_verified_on_device": ARROWS_OK,
    "parent_tip": "16717582e7f0dfd371f21c56465e11113d8b6675",
    "parent_branch": "dev/serialized-quotient-dose-transfer-00",
    "science_parent_FWL2CF00": "96c7d295e72106cd949d810fa92807c2514e7449",
    "owner_main": "f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77",
    "owner_main_untouched": True,
    "SQDT00_subtree": "2a68162bcbd2881267afbb7adbf19a03b7c028ba",
    "SQDT00_bundle": {"name": "SQDT00_tip_16717582.bundle", "verify": "okay",
                      "requires_prerequisite": "96c7d295e72106cd949d810fa92807c2514e7449"},
    "SQDT00_SHA256SUMS_from_committed_tree": "25 of 25 verified (24 entries + SHA256SUMS itself), "
                                             "cross-version subtree id 2a68162b agrees git 2.34.1/2.43.0",
    "FWL2CF00_subtree": "159577eeb703d5878b2efe37737b535fddc29046",
    "FWL2CF00_SHA256SUMS": "198 of 198 verified from the committed tree (inherited)",
    "serialized_basis_blob_binding": binding,
    "n_mismatch": len(mism), "mismatches": mism,
    "reserved_namespaces": {"62000-62009": "RESERVED_AND_UNREAD__NEVER_GENERATED_OR_OPENED",
                            "64000-64011": "EXPOSED__UNAVAILABLE_FOR_A_FRESH_ROLE",
                            "65000-65007": "HISTORICAL__UNAVAILABLE",
                            "66000-66015": "SQDT00 frozen (never constructed)__UNAVAILABLE"},
    "inherited_deviations": ["D0", "D1", "D2"],
    "sqdt00_lobo_finding": "SQDT00 stability used leave-one-DESCENDANT-out (dleft in range(16), "
                           "D_OF maps rows to descendants); the correct unit is the ancestry block. "
                           "Corrected here without mutating the V1 object.",
}
json.dump(prov, open(f"{OUT}/PARENT_PROVENANCE_BINDING.json", "w"), indent=1)

CODE = {
    "WSFSCRP00/wsfscrp_core.py": f"{SWEEP}/WSFSCRP00/wsfscrp_core.py",
    "ETCMNFC/etcmnfc_core.py": f"{SWEEP}/ETCMNFC/etcmnfc_core.py",
    "PPAI/ppai_core.py": f"{SWEEP}/PPAI/ppai_core.py",
    "PPAI/ppai_engine.py": f"{SWEEP}/PPAI/ppai_engine.py",
    "DOMC/domc_core.py": f"{SWEEP}/DOMC/domc_core.py",
    "SQDT00/sq_exact.py": f"{SQDT}/sq_exact.py",
}
FREEZE = {
    "frozen_before_any_parent_numeric_load": True,
    "hashes": {"FSQBT00_MASTER_FREEZE.md": sha(f"{OUT}/FSQBT00_MASTER_FREEZE.md")},
    "inherited_code_sha256": {k: sha(v) for k, v in CODE.items()},
    "H_GRID": [40 * i for i in range(1, 11)], "dt": "1/10",
    "weights": ["1/18"] + ["1/9"] * 8 + ["1/18"], "W_POST": "1",
    "materiality_coefficient": "0.01",
    "gauge": "one optional A/B exchange per ancestry block, shared across carriers, all scored "
             "times and all transfer/quotient calculations",
    "alpha_fresh": "1/24", "E_TAU_FRESH": "sum_b TAU_b^2 / 12",
    "corrected_lobo": {"folds": 4, "removed_unit": "one complete ancestry block (4 descendants, 8 rows)",
                       "blocks": [65000, 65001, 65002, 65003],
                       "gates": ["S0", "S1", "S2", "S3", "S4>0.80", "S5>0.64", "S6<0.50", "S7"],
                       "P2_license": "S0&S1&S2&S4&S6&S7", "E2_license": "P2&S3&S5&S6"},
    "fresh_seed_namespace_rule": "smallest N>=65000 div 100 with N..N+23 disjoint from all prior "
                                 "use and not in 62000-62009 or 64000-64011",
    "start_budget": {"panel": 24, "sham": 24, "active": 24, "other": 0, "total": 72,
                     "retries_after_panel_lock": 0, "unused_repurposable": False},
    "stop_precedence": ["parent_provenance", "freeze_before_load", "block_map",
                        "S4_P2_license", "oracle_firewall", "panel_incomplete",
                        "sham_threshold", "preactive_lock", "active_incomplete",
                        "runtime_readback", "delivery"],
}
json.dump(FREEZE, open(f"{OUT}/FSQBT00_MASTER_FREEZE_HASHES.json", "w"), indent=1)
print("provenance: arrows %d/3 ok | basis blobs bound %d, mismatches %d"
      % (ARROWS_OK, len(binding), len(mism)))
print("freeze sha:", FREEZE["hashes"]["FSQBT00_MASTER_FREEZE.md"])
if mism:
    print("MISMATCHES:", mism)
