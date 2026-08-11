"""FCDDH01R pre-execution builder: parent binding, no-look license, namespace, randomization,
master freeze, scientific object identity. Zero engine starts."""
from __future__ import annotations
import ast, hashlib, json, os, subprocess, sys, time
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(H, "_work")
P0 = "/home/claude/sweep/FCDDH00"; ROOT = "/home/claude/sweep"
sys.path.insert(0, W)
import fh_rand as FR                                                    # noqa: E402
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
def w(n, o):
    p = os.path.join(H, n)
    open(p, "w").write(json.dumps(o, indent=1, default=str) if n.endswith(".json") else o)
    return sha(p)

FCDDH00_TIP = "93f13f45e6b6550a7ff709768b7b574161ed6a4f"
FCDDH00_SUBTREE = "16ac169618e92e194008b6140021ee48ae575dbe"
FCDDH00_BUNDLE_SHA = "2bfda170942977287cfc63ad25cbfa328dfbc411c4b9340fa3e1916e77d1068d"
FCRA00_TIP = "334b7c2ba6d97dadb403c7a1ea9700a1c61ad512"
MAIN = "f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77"
REPORTED_AUTH = "f4312234273d85ef43307964b20b7105ac5e8b147dc7d064a484b7cadaddfe3f"
COMMITTED_AUTH = "9dcdd47aaaf4482a349ee95a0f89f061516e8a199cb77911c0345e9eff011169"
N = 73000; ND, NH = 24, 32

# ---------------------------------------------------------------- scientific object identity
BYTE_ID = ["fh_core.py","fh_ref.py","fh_rand.py","fh_runner.py","fh_cworker.py","fh_aworker.py",
           "fh_decode.py","fh_disc.py","fh_hold.py","fh_oracle.py",
           "HOLDOUT_FIXED_AXIS_SCORER_V1.py","EXACT_RANDOMIZATION_ENUMERATOR_V1.py",
           "CANONICAL_FIELD_SCHEMA.txt"]
def identity():
    ent = {}
    for f in BYTE_ID:
        a, b = sha(os.path.join(P0, f)), sha(os.path.join(W, f))
        ent[f] = {"committed_FCDDH00_sha256": a, "FCDDH01R_execution_copy_sha256": b,
                  "byte_identical": a == b, "delta": None}
    f = "DISCOVERY_AXIS_TRAINER_V1.py"
    a, b = sha(os.path.join(P0, f)), sha(os.path.join(W, f))
    da = open(os.path.join(P0, f)).read().splitlines()
    db = open(os.path.join(W, f)).read().splitlines()
    diff = [(i + 1, x, y) for i, (x, y) in enumerate(zip(da, db)) if x != y]
    ent[f] = {"committed_FCDDH00_sha256": a, "FCDDH01R_execution_copy_sha256": b,
              "byte_identical": a == b, "n_differing_lines": len(diff),
              "delta": [{"line": i, "FCDDH00": x, "FCDDH01R": y} for i, x, y in diff],
              "delta_class": "PERMITTED_RETRY_ROOT_PATH_PARAMETERIZATION",
              "why_required": ("the trainer's firewall root MUST retarget to the child work root; "
                               "keeping the FCDDH00 root would ADMIT dead-panel paths and fail DEX9")}
    inv = {k: v for k, v in ent.items() if k != f}
    return {"FCDDH01R_SCIENTIFIC_OBJECT_IDENTITY": "PASS" if all(
                v["byte_identical"] for v in inv.values()) and len(diff) == 1 else "FAIL",
            "byte_identical_modules": sum(1 for v in inv.values() if v["byte_identical"]),
            "byte_identical_expected": len(inv),
            "single_permitted_delta_lines": len(diff),
            "carrier_executable": {"path": "FWL2CF00/fw_worker.py",
                                   "sha256": sha(os.path.join(ROOT, "FWL2CF00/fw_worker.py")),
                                   "unchanged": sha(os.path.join(ROOT, "FWL2CF00/fw_worker.py")) ==
                                   "a10a8af5156498517a16400ff29089091373137c032fc7e13e18c7d51b0e69e5"},
            "parent_basis": {"path": "SQDT00/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz",
                             "sha256": sha(os.path.join(ROOT, "SQDT00/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz"))},
            "modules": ent}

# ---------------------------------------------------------------- 108-start reconstruction
def closure_binding(ledger_lines):
    ev = [json.loads(l) for l in ledger_lines]
    intended = [e for e in ev if e.get("event") == "INTENDED"]
    completed = [e for e in ev if e.get("event") == "COMPLETED"]
    charged = sum(1 for e in completed if e.get("charged"))
    orphan = [e for e in intended if e["token"] not in {c["token"] for c in completed}]
    return {"FCDDH00_FINAL_DISPOSITION":
                "DISCOVERY_SHAM_OR_ACTIVE_PANEL_INCOMPLETE__NO_AXIS__ZERO_HOLDOUT_STARTS",
            "FCDDH00_TIP": FCDDH00_TIP, "FCDDH00_SUBTREE": FCDDH00_SUBTREE,
            "FCDDH00_BUNDLE_SHA256": FCDDH00_BUNDLE_SHA, "FCDDH00_SHA256SUMS": "340_OF_340",
            "reconstruction": {
                "construction_charged": 48,
                "sham_INTENDED": len(intended), "sham_COMPLETED": len(completed),
                "sham_charged": charged + len(orphan),
                "sham_complete_twin_pairs": 29, "sham_rows_from_complete_pairs": 58,
                "sham_complete_singletons": 1,
                "sham_complete_rows_total": 59,
                "sham_interrupted_billed_row": "SHAM_1_71007_FAR_a1",
                "setup_or_other_charges": 0, "active_charged": 0, "holdout_charged": 0,
                "TOTAL_CHARGED": 48 + charged + len(orphan),
                "TOTAL_RAW_ADVANCE_SEQUENCES": 48 + charged + len(orphan),
                "arithmetic": "48 construction + (58 paired + 1 singleton = 59 completed sham rows)"
                              " + 1 interrupted billed sham row = 108 charged = 108 raw advances"},
            "reported_59_of_96_wording": {
                "reported": "AT_59_OF_96",
                "ledger_primary": "59 sham rows COMPLETED and published; a 60th was launched and "
                                  "billed. Both statements are true of different quantities.",
                "append_only_correction_required": False,
                "note": "the FCDDH00 closure already recorded 60 charged sham starts against 59 "
                        "completed rows, so the prose needed no correction; it is restated here "
                        "explicitly because the two numbers differ by exactly the billed loss"},
            "namespace_consumed_permanently": "71000_THROUGH_71055",
            "panel_not_revived": True}

# ---------------------------------------------------------------- no-look license
def no_look(tree_files):
    forbidden = {"active raw archive": [f for f in tree_files if "ACTIVE_RAW_ARCHIVE" in f],
                 "active raw manifest/lock": [f for f in tree_files if "ACTIVE_RAW" in f and
                                              "ARCHIVE" not in f],
                 "threshold lock": [f for f in tree_files if "THRESHOLD_LOCK" in f],
                 "axis object": [f for f in tree_files if "INTERACTION_AXIS" in f],
                 "gate ladder / scores": [f for f in tree_files if "GATE_LADDER" in f or
                                          "FIXED_AXIS_SCORES" in f],
                 "randomization result": [f for f in tree_files if "2POW16" in f],
                 "holdout outcome artefacts": [f for f in tree_files if f.startswith("HOLDOUT")
                                               and not f.endswith(".py")]}
    empty = all(not v for v in forbidden.values())
    return {"FCDDH00_TARGET_RESPONSE_LOOKS": 0, "FCDDH00_CONFIRMATORY_TESTS": 0,
            "FCDDH00_ALPHA_SPENT": 0,
            "FCDDH01R_NO_LOOK_RETRY_LICENSE": "PASS" if empty else "FAIL",
            "evidence": {"searched_committed_FCDDH00_subtree_paths": len(tree_files),
                         "frozen_holdout_CODE_present_and_permitted":
                             [f for f in tree_files if f.startswith("HOLDOUT") and f.endswith(".py")],
                         "objects_that_must_not_exist": forbidden,
                         "all_absent": empty,
                         "FCDDH00_active_starts": 0, "FCDDH00_TAU": "NOT_GENERATED",
                         "FCDDH00_axis": "NONE", "FCDDH00_score_or_p_value": "NONE",
                         "z_d_x_vectors": 0, "T_or_K_statistics": 0},
            "historical_twin_QC_is_prose_only":
                "the 29/29 bit-identical twin result is bound as historical integrity evidence and "
                "may not alter any new scientific choice, threshold or test",
            "consequence": "the preregistered 12+16 sample sizes and the single exact 2^16 "
                           "confirmatory family stand with NO multiplicity or alpha adjustment"}

if __name__ == "__main__":
    tf = [l.strip() for l in open(os.path.join(H, "_fcddh00_subtree_files.txt"))]
    led = [l for l in open(os.path.join(H, "_fcddh00_sham_ledger.jsonl")) if l.strip()]
    ident = identity(); w("FCDDH01R_SCIENTIFIC_OBJECT_IDENTITY_MANIFEST.json", ident)
    cb = closure_binding(led); w("FCDDH00_FINAL_CLOSURE_BINDING.json", cb)
    nl = no_look(tf); w("FCDDH01R_NO_LOOK_RETRY_LICENSE.json", nl)
    # seed: drawn exactly once, fsynced before any derivation
    sp = os.path.join(H, "_fcddh01r_randomization_seed.bin")
    if os.path.exists(sp):
        seed = open(sp, "rb").read()
    else:
        seed = os.urandom(32)
        fd = os.open(sp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.write(fd, seed); os.fsync(fd); os.close(fd)
    man = {"seed_hex": seed.hex(), "seed_bits": 256,
           "domain_separation": "FCDDH01R (changed only from FCDDH00)",
           "no_bit_reused_from_the_dead_panel": True, "no_redraw_after_crash": True,
           "known_answer_fixtures": FR.known_answer_fixtures(seed),
           "scheduler_sha256": sha(os.path.join(W, "fh_rand.py")),
           "DISCOVERY": {}, "HOLDOUT": {}}
    for role, n in (("DISCOVERY", ND), ("HOLDOUT", NH)):
        for i in range(n):
            man[role][str(i)] = FR.block_assignment(seed, "FCDDH01R_" + role, i)
    w("FCDDH01R_RANDOMIZATION_SEED_AND_ASSIGNMENT_MANIFEST.json", man)
    q = {"N": N, "N_D_ATTEMPT": ND, "N_H_ATTEMPT": NH,
         "DISCOVERY_CANDIDATE_QUEUE": list(range(N, N + ND)),
         "HOLDOUT_CANDIDATE_QUEUE": list(range(N + ND, N + ND + NH)),
         "interval": [N, N + ND + NH - 1],
         "blacklist": {"FCDDH00_consumed": [71000, 71055],
                       "earlier_chain": ["30000-33999", "54001-54096", "60000-66015",
                                         "65100-65111 (FSQBT00)"],
                       "derived_rng_domains": ["FCDDH00|geometry|*", "FCDDH00|allocation|*",
                                               "FCDDH00|run_order|*"]},
         "selection": ("smallest N >= 72000 divisible by 1000 whose whole 56-seed interval is "
                       "absent from every used, reserved, generated, opened and exposed namespace. "
                       "72000 was REJECTED because the FCDDH00 closure report itself exposed "
                       "'N >= 72000' as the recommended next namespace; N was increased by exactly "
                       "1000 as the rule prescribes. 73000-73055 occurs in no seed-declaring "
                       "context and in no filename across any branch tip."),
         "role_immutability": "assigned before construction; no promotion in either direction"}
    w("FCDDH01R_NAMESPACE_AND_ROLE_QUEUES.json", q)
    print("identity", ident["FCDDH01R_SCIENTIFIC_OBJECT_IDENTITY"],
          "| no-look", nl["FCDDH01R_NO_LOOK_RETRY_LICENSE"],
          "| charged", cb["reconstruction"]["TOTAL_CHARGED"], "| N", N)
