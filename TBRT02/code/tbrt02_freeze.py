"""TBRT02 C2 — the master freeze. Committed ALONE, and it is what opens the execution gate."""
from __future__ import annotations
import datetime as dt, json, os, subprocess, sys

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
for p in ("TBRT02/code", "OMLDCT02/code"):
    sys.path.insert(0, os.path.join(REPO, p))
import omldct02_hashes as H          # noqa: E402
import tbrt02_run as R               # noqa: E402
import tbrt02_fork as F              # noqa: E402
import tbrt02_displace as D          # noqa: E402

METHODS = ["TBRT02/code/tbrt02_seeds.py", "TBRT02/code/tbrt02_guard.py",
           "TBRT02/code/tbrt02_displace.py", "TBRT02/code/tbrt02_fixtures.py",
           "TBRT02/code/tbrt02_fork.py", "TBRT02/code/tbrt02_run.py",
           "TBRT02/code/tbrt02_freeze.py",
           "OMLDCT02/code/omldct02_fork.py", "OMLDCT02/code/omldct02_hashes.py",
           "ORR01/code/kinetics.py", "ORR01/code/lawspec_v2.py",
           "OBTC02/code/engine_obtc.py", "PQEC01/code/pqec01_observer.py",
           "TLMR01/code/tlmr01_world.py", "TLMR01/code/tlmr01_laws.py",
           "FMRCT01/code/fmrct01_world.py", "FMRCT01/code/fmrct01_track.py"]


def main():
    seeds = json.load(open(f"{REPO}/TBRT02/out/TBRT02_SEED_MANIFEST.json"))
    forb = json.load(open(f"{REPO}/TBRT02/out/TBRT02_FORBIDDEN_SEEDS.json"))
    fx = json.load(open(f"{REPO}/TBRT02/out/TBRT02_FIXTURES.json"))
    files = {p: H.file_sha256(f"{REPO}/{p}") for p in METHODS}
    tip = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"],
                         capture_output=True, text=True).stdout.strip()
    d = {
        "MISSION": "TBRT02", "SECTION": "master freeze",
        "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
        "PARENT_TIP_AT_FREEZE": tip,
        "SUPERSEDES": "TBRT01, which cannot be resumed: the ninth container rollback destroyed all "
                      "eight of its own method files, so its METHODS_HASH can never be verified "
                      "again. See TBRT01/out/TBRT01_ROLLBACK_RECOVERY_09.json.",
        "WHAT_TBRT01_STILL_CONTRIBUTES": "a validated PILOT of the DISPLACED intervention — 114 "
            "seeds, 9 admissible triples, every intervention check passing on every one, and the "
            "design flaw its fixtures caught before any world was spent: the destination pole must "
            "be the DAUGHTER's, not the parent's. That correction is inherited here.",
        "THE_QUESTION": "after the parent's influence is removed, AND in the presence of a matched "
                        "competing Y source it could wrongly absorb, does an organisation issued "
                        "from the daughter retain an ancestry of its own?",
        "ARMS": list(F.ARMS),
        "ARM_DEFINITIONS": {
            "SHAM": "nothing happens; the control",
            "SELECTIVE": "the parent's Y is removed through the engine's decay channel, Y -> WY; "
                         "the OMLDCT02 treatment, kept for comparability",
            "DISPLACED": "the parent's Y is removed from its cells and the SAME mass is placed at "
                         "the toroidal antipode of the DAUGHTER's centroid, at Chebyshev >= "
                         f"{D.MIN_SEPARATION_FROM_THE_DAUGHTER} from every daughter cell",
        },
        "DISPLACEMENT_IS_MORE_INVASIVE_THAN_REMOVAL":
            "removal uses the engine's own decay channel. Displacement is a teleport: no engine "
            "channel moves mass across the lattice in one step. Two things bound it and both are "
            "verified on real engine objects in TBRT02_FIXTURES.json — total Y mass is conserved "
            "exactly, and no random number is consumed.",
        "THE_REFUTATION_CONDITION_FROZEN_BEFORE_ANY_WORLD":
            "if the CERTAIN set of the daughter's lineage ever absorbs a descendant of the "
            "displaced mass, Model C is REFUTED. One absorption suffices. No threshold, no "
            "magnitude judgement, checkable by enumeration.",
        "LAW": {"name": "LAW_C_MCTT01", **F.LAW,
                "kY_hex": float.hex(F.LAW["kY"]), "muY_hex": float.hex(F.LAW["muY"]),
                "p_hop_Y_hex": float.hex(F.LAW["p_hop_Y"])},
        "FROZEN_PHYSICS": {"L": F.L_GRID, "T_HORIZON": F.T_HORIZON, "CAP": 16, "S0": 3,
                           "phi": 0.2, "omega": 0.05, "muX": 0.004, "kX": 1.0, "X_SEED": 4,
                           "CORE_R": 5.0, "NEED": 250, "LATEST_ALLOWED_TRIGGER": 6500},
        "TARGET_VALID_TRIPLES": R.TARGET_VALID_TRIPLES,
        "MAX_ARM_INSTANCES": R.MAX_ARM_INSTANCES,
        "CEILING_IS_NOT_A_STOPPING_RULE": R.CEILING_IS_NOT_A_STOPPING_RULE,
        "HOW_THE_CEILING_WAS_SIZED":
            "EVCS01's corrected instrument, on OMLDCT02's PROSPECTIVE 805-seed ledger, with the "
            "admissible rate drawn from its own Jeffreys posterior rather than held at the point "
            "estimate. 926 is the 95th percentile for 41 triples. A rate-known calculation would "
            "have said 821 and attained about 85 per cent — the error EVCS01 found in its own "
            "instrument and fixed. The TLMR01 developmental rate 22/256 is NOT used.",
        "SHARDS": R.N_SHARDS,
        "N_BASE_SEEDS": seeds["N_BASE"], "N_RESERVE_SEEDS": seeds["N_RESERVE"],
        "SEED_SET_HASH": seeds["SEED_SET_HASH"],
        "SEED_MANIFEST_CONTENT_HASH": seeds["SEED_MANIFEST_CONTENT_HASH"],
        "FORBIDDEN_SET_HASH": forb["FORBIDDEN_SET_HASH"], "N_FORBIDDEN": forb["N_FORBIDDEN"],
        "SEEDS_DISJOINT_FROM_EVERYTHING_RUN_BEFORE": seeds["DISJOINT_FROM_THE_FORBIDDEN_SET"],
        "TBRT01_AND_OMLDCT02_SEEDS_ARE_INSIDE_THE_FORBIDDEN_SET": True,
        "METHODS_FILES": files, "N_METHODS_FILES": len(files),
        "METHODS_HASH": H.canonical_digest(files),
        "METHODS_EXTERNALISED_TO_WINDOWS_BEFORE_ANY_WORLD": True,
        "WHY_THAT_LINE_EXISTS": "TBRT01 died because its method files lived only in a git history "
            "that lived only in this container. A commit is not durability here. TBRT02's methods "
            "go to Windows at C1, before the gate opens.",
        "FIXTURES_ALL_PASS": fx["ALL_PASS"],
        "FIXTURES_ARE_NON_SCIENTIFIC": fx["ALL_FIXTURES_ARE_NON_SCIENTIFIC"],
        "WORLDS_RUN_AT_SCIENTIFIC_SCALE_BEFORE_THIS_FREEZE": 0,
        "WHAT_WOULD_INVALIDATE_TBRT02": [
            "a scientific-scale world before this freeze is committed",
            "a seed reused from any earlier manifest",
            "a threshold adjusted after results",
            "the refutation condition modified after the first world",
            "an outcome-driven seed replacement",
            "a destination inside the daughter's one-step reach",
        ],
        "H3_STATUS": "NOT_TESTED", "REPRODUCTION_STATUS": "NOT_TESTED",
        "HEREDITY_STATUS": "NOT_TESTED", "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED",
        "X_LAWSPEC_BASELINE": "UNCHANGED", "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED",
        "COMPANION_PAPER_V1_1_STATUS": "UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED",
        "OMLDCT02_STATUS": "INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED",
        "CLEA01_STATUS": "CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED",
    }
    d["FREEZE_CONTENT_HASH"] = H.content_digest(d, extra_excluded=("FREEZE_CONTENT_HASH",))
    p = f"{REPO}/TBRT02/out/TBRT02_MASTER_FREEZE.json"
    json.dump(d, open(p, "w"), indent=1)
    print("FREEZE_CONTENT_HASH =", d["FREEZE_CONTENT_HASH"])
    print("FREEZE_FILE_SHA256  =", H.file_sha256(p))
    print("METHODS_HASH        =", d["METHODS_HASH"], f"({d['N_METHODS_FILES']} files)")
    return d


if __name__ == "__main__":
    main()
