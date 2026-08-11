"""FCRA00 Commit 1 -- provenance binding and freeze hashing. ZERO decoded numerical arrays.
Binds git metadata and source/object hashes only; opaque candidate bytes hashed only to locate
byte-identical files (no scientific statistic inspected)."""
from __future__ import annotations
import hashlib, json, os
OUT = "/home/claude/sweep/FCRA00"
SWEEP = "/home/claude/sweep"
FSQ = f"{SWEEP}/FSQBT00"
SQDT = f"{SWEEP}/SQDT00"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
def blob(p):
    b = open(p, "rb").read(); h = hashlib.sha1(); h.update(b"blob " + str(len(b)).encode() + b"\x00"); h.update(b); return h.hexdigest()

CHAIN = [
    ("b3f45ac7781e0dd48f34886b7c63840af520d502", "FSQBT00 commit 7 (delivery)"),
    ("e3468aa135502e64a6034f88289cd1331ac2ac97", "FSQBT00 commit 6 (decoded analysis)"),
    ("90b8bb97f0af53bba8f8ee0c637fcb2face36199", "FSQBT00 commit 5 (active raw-only)"),
    ("93c62fc7a25552135766b70fd006a34776fdc18e", "FSQBT00 commit 4 (shams/thresholds/preactive)"),
    ("1af85af9e5e0ba44766a57b4754e9d6780152f08", "FSQBT00 commit 3 (sealed panel)"),
    ("6df18dad0fac6b2c5a262b2d4175eea252ec7dd8", "FSQBT00 commit 2 (LOBO audit)"),
    ("b9f25a230a7302b9b4358340ac27bfb152feb45e", "FSQBT00 commit 1 (master freeze)"),
    ("16717582e7f0dfd371f21c56465e11113d8b6675", "SQDT00 commit 3"),
    ("96c7d295e72106cd949d810fa92807c2514e7449", "FWL2CF00 commit 6"),
]
# arrows verified single-direct-parent on the device (b3f45ac7^=e3468aa1, ..., b9f25a2^=16717582)
ARROWS_OK = 7

BASIS_BLOBS = {
    "SQDT00/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz": "8f848411cd5a8ab4a483c217cd6b22c752ae8479",
    "SQDT00/FWL2_RELATIVE_QUOTIENT_BASIS_V1.json": "07c9cf7e4eb3646bfbd32799de2618435f6e0353",
}
binding, mism = {}, []
for rel, committed in BASIS_BLOBS.items():
    p = f"{SWEEP}/{rel}"
    r = blob(p) if os.path.exists(p) else None
    binding[rel] = {"committed": committed, "recomputed": r, "match": r == committed}
    if r != committed:
        mism.append(rel)

# checkpoint/mask byte recoverability (opaque hashing vs committed digests -- allowed pre-freeze)
DIG = json.load(open(f"{FSQ}/FRESH_CHECKPOINT_FULL_FIELD_DIGESTS.json"))
ck_match = sum(1 for f, m in DIG["checkpoints"].items() if os.path.exists(f"{FSQ}/panel/{f}") and sha(f"{FSQ}/panel/{f}") == m["sha256"])
mk_match = sum(1 for f, m in DIG["masks"].items() if os.path.exists(f"{FSQ}/panel/{f}") and sha(f"{FSQ}/panel/{f}") == m["sha256"])

prov = {
    "chain": [c for c, _ in CHAIN], "chain_labels": {c: l for c, l in CHAIN},
    "arrows_single_direct_parent_verified_on_device": ARROWS_OK,
    "parent_tip": "b3f45ac7781e0dd48f34886b7c63840af520d502",
    "parent_subtree": "ab11f2c0187b645f4793cb2b08dfa599fe506d4f",
    "parent_bundle": "FSQBT00_tip_b3f45ac7.bundle (sha256 0a7ce1e2fd8a955eab268ee7908686445a84b33808be6b1fe4ec9808469b3038)",
    "sqdt00_tip": "16717582e7f0dfd371f21c56465e11113d8b6675",
    "fwl2cf00_source": "96c7d295e72106cd949d810fa92807c2514e7449",
    "owner_main": "f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77", "owner_main_untouched": True,
    "immutable_object_blob_binding": binding, "n_object_mismatch": len(mism),
    "checkpoint_bytes_match_committed_digests": f"{ck_match}/12",
    "mask_bytes_match_committed_digests": f"{mk_match}/12",
    "checkpoint_recovery_possible": ck_match == 12,
    "full_field_trajectories_present": {"sham_npz": 24, "active_npz": 24},
    "consumed_seed_namespaces": {"65100-65123": "FSQBT00 exposed queue (12 accepted 65100-65111)",
                                 "70000": "diagnostic probe -- consumed",
                                 "62000-62009": "reserved unread", "64000-64011": "exposed",
                                 "65000-65007/66000-66015": "historical/frozen"},
}
json.dump(prov, open(f"{OUT}/PARENT_PROVENANCE_BINDING.json", "w"), indent=1)

FREEZE = {
    "frozen_before_any_numerical_array_decode": True,
    "hashes": {"FCRA00_MASTER_FREEZE.md": sha(f"{OUT}/FCRA00_MASTER_FREEZE.md")},
    "immutable_object": {"npz_sha256": sha(f"{SQDT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz"),
                         "json_sha256": sha(f"{SQDT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.json"),
                         "TUBE_P2_LOBO": "1.2166510017869535e-07"},
    "engine_starts_authorized": 0, "checkpoint_regeneration_authorized": False,
    "order_statistic": {"P_K0": "1/4", "E_K": "12/5", "P_K3": "11/91", "P_Kge3": "11/28",
                        "formula": "C(15-k,3)/C(16,4)"},
    "e2_sign_combinatorial": {"one_sided_k_ge_10_of_12": "79/4096", "two_sided": "79/2048"},
    "nuisance_2x2": {"P_all3_in_NEAR": "1/11", "fisher_two_sided": "2/11"},
    "direction_floor": "A_DELTA_TAU = (sqrt2/6) sum_b TAU_b ; E_DELTA_TAU = (sum TAU_b)^2/144",
    "commit_order": ["freeze", "audit+recovery+corrigendum_intent", "firewall+oracle+rule_freeze+readback",
                     "primary_recomputation+corrigendum", "residual_anatomy+nuisance",
                     "direction_arbitration+optional_axis", "report+closure"],
}
json.dump(FREEZE, open(f"{OUT}/FCRA00_MASTER_FREEZE_HASHES.json", "w"), indent=1)
print("provenance: arrows %d/7 | object blobs %d match | checkpoints %d/12 recoverable | masks %d/12"
      % (ARROWS_OK, len(binding) - len(mism), ck_match, mk_match))
print("freeze sha:", FREEZE["hashes"]["FCRA00_MASTER_FREEZE.md"])
