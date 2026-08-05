"""Run ROUTE_E_PILOT_READINESS_AND_FEASIBILITY_00.  Exploratory.  No claim.  No k.

Order is mandatory and enforced by construction:

  1. build the manifest, hash it, derive the seed from that hash, build the 48-world
     inventory, and WRITE both to disk -- before the first engine step;
  2. run every world of the inventory, in order, keeping every result;
  3. admit every world through the engine-free public admission;
  4. verify engine provenance world by world;
  5. write the raw outputs and the report.

There is no retry, no replacement, no top-up and no second seed anywhere in this file.
A crashed world stays in the inventory as a technical incident with ``Y = None``.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from edlab import route_e_pilot as pilot
from edlab import route_e_pilot_acquisition as acq
from edlab import route_e_pilot_admission as adm
from edlab.substrates.lattice_bond import future_route_e_execution as execution
from edlab.substrates.lattice_bond.engine import LatticeBondSpec

SCIENTIFIC_FIXTURE_CLASS = "PILOT_EXPLORATORY_NON_CONFIRMATORY"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--namespace", default="PILOT-ROUTE-E-FEASIBILITY-00")
    parser.add_argument("--laws", type=int, default=pilot.PILOT_LAWS)
    args = parser.parse_args()

    root = Path(args.output)
    root.mkdir(parents=True, exist_ok=False)

    # ---- 1.  PRE-RUN, written before anything is executed ---------------------------
    manifest = pilot.build_pilot_manifest(args.namespace)
    pre_run_root = pilot.pilot_pre_run_root(manifest)
    seed = pilot.pilot_seed_root(pre_run_root)
    plan = pilot.build_pilot_plan(seed, laws=args.laws)
    # CORRECTIVE PASS.  The horizon and the cadence are NOT command-line knobs.  A
    # reviewer showed the same law and the same seed giving Y = 0 at horizon 64 and
    # Y = 1 at horizon 4096, which would have made the no-reroll claim false.  The
    # schedule is derived from the COMMITTED manifest and from nothing else.
    schedule = pilot.schedule(int(manifest["horizon_steps"]), int(manifest["cadence_steps"]))

    (root / "PILOT_MANIFEST.json").write_bytes(pilot.canonical_bytes(manifest))
    (root / "PILOT_INVENTORY.json").write_bytes(
        pilot.canonical_bytes(
            {
                **plan.inventory_document(),
                "pre_run_root": pre_run_root,
                "sampled_frames": [int(v) for v in schedule],
            }
        )
    )
    print(f"pre_run_root = {pre_run_root}")
    print(f"seed_root_sha256 = {plan.seed_root_sha256}")
    print(f"worlds = {len(plan.worlds)}  schedule = {len(schedule)} frames to {schedule[-1]}")
    sys.stdout.flush()

    # ---- 2..4.  every world of the frozen inventory, in order -----------------------
    results: list[dict] = []
    started = time.time()
    for world in plan.worlds:
        directory = root / "worlds" / f"{world.ordinal:06d}"
        entry: dict = {"world": world.as_document()}
        try:
            fields = plan.law_fields[world.law_ordinal]
            law_spec = LatticeBondSpec(
                **{
                    k: float(v)
                    for k, v in fields.items()
                    if k in LatticeBondSpec.__dataclass_fields__
                }
            )
            state = execution._initial_state(seed, world.ic_index, world.lattice_size)
            record = acq.acquire_pilot_world(
                directory,
                law_spec=law_spec,
                initial_state=state,
                sampled_frames=schedule,
                namespace=args.namespace,
                ordinal=world.ordinal,
            )
            entry["acquisition"] = {
                "steps_taken": record.steps_taken,
                "ledger_sha256": dict(record.ledger_digests),
                "provenance_sha256": record.provenance_sha256,
            }
        except Exception as exc:  # noqa: BLE001 - a crash is an incident, kept, never dropped
            entry["acquisition"] = {"crash": f"{type(exc).__name__}: {str(exc)[:300]}"}
            entry["admission"] = {
                "ordinal": world.ordinal,
                "status": adm.TECHNICAL_INVALID,
                "Y_by_f": {"0.01": None, "0.05": None, "0.2": None},
                "incident": f"ACQUISITION_CRASH: {type(exc).__name__}",
                "incident_reason_code": "ACQUISITION_CRASH",
                "lattice_size": world.lattice_size,
            }
            entry["engine_provenance"] = {"verified": False, "reason": "no artefact"}
            results.append(entry)
            print(f"  world {world.ordinal:3d}  CRASH {type(exc).__name__}")
            sys.stdout.flush()
            continue

        verdict = adm.admit_pilot_world(
            directory,
            ordinal=world.ordinal,
            lattice_size=world.lattice_size,
            require_fixture_class=SCIENTIFIC_FIXTURE_CLASS,
            expected_sampled_frames=schedule,
        )
        verified, why = adm.verify_engine_provenance(
            directory, law_spec=law_spec, initial_state=state
        )
        verdict.engine_reexecution_verified = bool(verified)
        entry["admission"] = verdict.as_document()
        entry["engine_provenance"] = {"verified": bool(verified), "reason": why[:200]}
        results.append(entry)

        residual = (
            f"{verdict.eligible_tracks[0].residual_union:.6f}"
            if verdict.eligible_tracks
            else "-"
        )
        print(
            f"  world {world.ordinal:3d}  L={world.lattice_size:2d}  {verdict.status:16s}"
            f"  Y={verdict.Y_by_f}  q_min={residual}  cause={verdict.ineligibility_cause}"
            f"  engine={'ok' if verified else 'FAIL'}"
        )
        sys.stdout.flush()

    elapsed = time.time() - started
    (root / "PILOT_RAW_RESULTS.json").write_bytes(
        pilot.canonical_bytes(
            {
                "kind": "route-e-pilot-raw-results/v1",
                "mission": pilot.PILOT_MISSION,
                "pre_run_root": pre_run_root,
                "results": results,
                "wall_clock_seconds": round(elapsed, 3),
                "worlds_expected": len(plan.worlds),
                "worlds_completed": len(results),
            }
        )
    )
    print(f"\nwall clock {elapsed:.1f}s for {len(results)} worlds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
