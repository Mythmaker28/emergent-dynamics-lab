"""HISTORY-TRANSPORT-00 DEV-only audit gate.

This module deliberately does *not* implement or execute the proposed feeding
intervention.  The mission requires a defensible, prospectively assigned H_A
versus H_B contrast before implementation.  The historical C1c protocol used
continuous amplitude pairs, not categorical A/B assignments.  This audit
reconstructs only pre-probe states and reads only outcome-independent fields
from already-open DEV artefacts (seeds 50001-50010).

If the assignment gate fails, all causal estimands are emitted as unavailable
and the decision is STOP-HISTORY-CONTRAST.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from edlab.experiments.sc_mcm import config as MCM_CONFIG
from edlab.substrates.scaffold.observables import detect
from experiments.individuation import causal_confirm as cc


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW_PATH = HERE / "turnover_dev_raw.json"
DEEP_DIAGNOSTICS_PATH = HERE / "turnover_dev_diagnostics_raw.json"
EXPECTED_PARENT = "8a690f64e31647e949a8cb74fbf7457f706cd437"
DEV_SEEDS = tuple(range(50001, 50011))
DOSE_MIDPOINT = cc.AMP_LO + cc.AMP_HI  # midpoint of [2*AMP_LO, 2*AMP_HI)
NUMERIC_ATOL = 1e-12
NUMERIC_RTOL = 1e-10


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return safe(value.tolist())
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, (np.floating, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    return value


def validate_dev_seeds(seeds: Iterable[int]) -> tuple[int, ...]:
    selected = tuple(int(seed) for seed in seeds)
    if not selected:
        raise ValueError("at least one DEV seed is required")
    if len(set(selected)) != len(selected):
        raise ValueError("duplicate DEV seed")
    invalid = sorted(set(selected) - set(DEV_SEEDS))
    if invalid:
        raise ValueError(f"REFUSED: only already-open DEV seeds 50001-50010; got {invalid}")
    return selected


def assigned_histories(seed: int) -> list[tuple[float, float]]:
    """Reproduce the historical six continuous draws; no outcome is inspected."""
    validate_dev_seeds([seed])
    rng = np.random.default_rng(seed)
    return [
        (
            float(rng.uniform(cc.AMP_LO, cc.AMP_HI)),
            float(rng.uniform(cc.AMP_LO, cc.AMP_HI)),
        )
        for _ in range(cc.K)
    ]


def assignment_kind() -> dict[str, Any]:
    return {
        "implemented": (
            "six sequential np.random.default_rng(world_seed) uniform draws; "
            "one (a1,a2) pair per target"
        ),
        "conditions": "continuous target-specific amplitude pairs; no categorical H_A/H_B labels",
        "phase_duration_steps": int(cc.PHASE),
        "amplitude_interval": [float(cc.AMP_LO), float(cc.AMP_HI)],
        "derived_coordinates": {
            "dose_primary": "a1+a2",
            "order_secondary": "a2-a1",
        },
        "outcome_independent": True,
        "categorical_randomization": False,
        "separate_randomization_namespace": False,
        "spatial_blocking_or_latin_square_implemented": False,
        "preregistration_discrepancy": (
            "PREREGISTRATION.md states a balanced Latin-square assignment, but "
            "exp1_prospective.py, causal_confirm.py, turnover_dev_runner.py and "
            "turnover_engine_03g.py all implement unblocked sequential continuous draws."
        ),
    }


def _mask(entity) -> np.ndarray:
    return cc.mask(entity)


def _rms(delta: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(delta, dtype=np.float64) ** 2)))


def _field_delta(history_state, control_state, support: np.ndarray) -> dict[str, dict[str, float]]:
    fields = {
        "rho": (history_state.rho, control_state.rho),
        "U": (history_state.U, control_state.U),
        "V": (history_state.V, control_state.V),
        "c": (history_state.c, control_state.c),
        "N": (history_state.N, control_state.N),
    }
    out: dict[str, dict[str, float]] = {}
    for name, (observed, reference) in fields.items():
        delta = observed[support] - reference[support]
        out[name] = {
            "mean": float(delta.mean()),
            "rms": _rms(delta),
            "max_abs": float(np.max(np.abs(delta))),
        }
    mf_delta = history_state.Mf[:, support] - control_state.Mf[:, support]
    out["Mf_complete_two_channel"] = {
        "mean": float(mf_delta.mean()),
        "rms": _rms(mf_delta),
        "max_abs": float(np.max(np.abs(mf_delta))),
    }
    return out


def reconstruct_preprobe_confound(seed: int) -> dict[str, Any]:
    """Compare post-history S0 with the same-seed, same-time no-drive world.

    No nutrient standardization, feeding probe, ablation, clamp, or future
    outcome is run.  This establishes whether the historical treatment changed
    non-memory body/geometry/physical state before HISTORY-TRANSPORT could begin.
    """
    histories = assigned_histories(seed)
    engine = cc.build(cc.MEM_INTACT)
    warm = cc.seed_world(seed)
    for _ in range(cc.WARM):
        warm = engine.step(warm)
    targets = cc.pick(sorted(detect(warm, MCM_CONFIG.DET), key=lambda entity: -entity.size))
    if len(targets) < cc.K:
        return {"eligible": False, "reason": "fewer_than_K_eligible"}

    centers = [entity.centroid for entity in targets]
    sigmas = [max(3.0, entity.rg * 0.8) for entity in targets]
    patches = [cc.patch(*centers[index], sigmas[index]) for index in range(cc.K)]
    history_state = warm.copy()
    for phase in (0, 1):
        for _ in range(cc.PHASE):
            for index in range(cc.K):
                history_state.N = (
                    history_state.N + histories[index][phase] * patches[index]
                )
            history_state = engine.step(history_state)
    for _ in range(cc.SETTLE):
        history_state = engine.step(history_state)

    control_state = warm.copy()
    for _ in range(2 * cc.PHASE + cc.SETTLE):
        control_state = engine.step(control_state)

    history_entities = sorted(detect(history_state, MCM_CONFIG.DET), key=lambda entity: -entity.size)
    control_entities = sorted(detect(control_state, MCM_CONFIG.DET), key=lambda entity: -entity.size)
    rows = []
    for index in range(cc.K):
        observed = cc.nearest(centers[index], history_entities)
        reference = cc.nearest(centers[index], control_entities)
        observed_mask = _mask(observed)
        reference_mask = _mask(reference)
        support = observed_mask | reference_mask
        a1, a2 = histories[index]
        fields = _field_delta(history_state, control_state, support)
        nonmemory_names = ("rho", "U", "V", "c", "N")
        nonmemory_changed = any(
            fields[name]["max_abs"]
            > NUMERIC_ATOL
            + NUMERIC_RTOL
            * float(np.max(np.abs(getattr(control_state, name)[support])))
            for name in nonmemory_names
        )
        rows.append(
            {
                "target": index,
                "a1": a1,
                "a2": a2,
                "dose": a1 + a2,
                "order": a2 - a1,
                "programmed_center_N_injection": float(cc.PHASE * (a1 + a2)),
                "programmed_total_N_injection": float(
                    cc.PHASE * (a1 + a2) * patches[index].sum()
                ),
                "body_geometry_history_minus_no_drive": {
                    "size": int(observed.size) - int(reference.size),
                    "mass": float(observed.mass) - float(reference.mass),
                    "rg": float(observed.rg) - float(reference.rg),
                    "centroid_distance": cc.pdist(observed.centroid, reference.centroid),
                    "mask_iou": float(
                        (observed_mask & reference_mask).sum()
                        / max(1, (observed_mask | reference_mask).sum())
                    ),
                },
                "local_state_history_minus_no_drive": fields,
                "nonmemory_state_changed": bool(nonmemory_changed),
            }
        )
    return {
        "eligible": True,
        "comparison_time": int(2 * cc.PHASE + cc.SETTLE),
        "comparison": "post-history S0 minus same-seed same-time no-drive counterfactual",
        "targets": rows,
    }


def _candidate_label_audits(targets: list[dict[str, Any]]) -> dict[str, Any]:
    midpoint = ["A" if row["dose"] >= DOSE_MIDPOINT else "B" for row in targets]
    order_sign = ["A" if row["order"] >= 0.0 else "B" for row in targets]
    ranked = sorted(range(len(targets)), key=lambda index: (targets[index]["dose"], index))
    return {
        "dose_midpoint": {
            "rule": f"A iff dose >= protocol-range midpoint {DOSE_MIDPOINT:.6f}",
            "labels": midpoint,
            "counts": {label: midpoint.count(label) for label in ("A", "B")},
            "status": "REJECTED_RETROACTIVE_DICHOTOMIZATION_NOT_ASSIGNED",
        },
        "order_sign": {
            "rule": "A iff order=a2-a1 >= 0",
            "labels": order_sign,
            "counts": {label: order_sign.count(label) for label in ("A", "B")},
            "status": "REJECTED_RETROACTIVE_DICHOTOMIZATION_NOT_ASSIGNED",
        },
        "within_world_extremes": {
            "rule": "A=max dose, B=min dose, omit middle target",
            "A_target": ranked[-1],
            "B_target": ranked[0],
            "omitted_target": ranked[1],
            "status": "REJECTED_POST_ASSIGNMENT_SELECTION_AND_INCOMPLETE_TARGET_USE",
        },
    }


def _world_row(raw: dict[str, Any], confound: dict[str, Any]) -> dict[str, Any]:
    seed = int(raw["seed"])
    eligible = bool(raw.get("eligible", False))
    row: dict[str, Any] = {
        "seed": seed,
        "initial_geometry_eligible": eligible,
        "deep_turnover_valid": bool(raw.get("feasible", False)),
        "deep_step": int(raw["deep"]["step"]) if raw.get("feasible") else None,
        "initial_exclusion": None if eligible else raw.get("reason", "not_eligible"),
        "deep_exclusion": (
            str(raw.get("deep_reason"))
            if eligible and not raw.get("feasible", False)
            else None
        ),
    }
    if not eligible:
        row["assignment"] = None
        row["preprobe_confound"] = confound
        return row

    histories = assigned_histories(seed)
    recorded = [tuple(float(value) for value in pair) for pair in raw["hist"]]
    if not np.array_equal(np.asarray(histories), np.asarray(recorded)):
        raise RuntimeError(f"history regeneration mismatch for seed {seed}")
    targets = []
    for index, (a1, a2) in enumerate(histories):
        targets.append(
            {
                "target": index,
                "initial_centroid": [float(value) for value in raw["cents"][index]],
                "initial_size": int(raw["sizes"][index]),
                "a1": a1,
                "a2": a2,
                "dose": a1 + a2,
                "order": a2 - a1,
            }
        )
    row["assignment"] = {
        "targets": targets,
        "candidate_labels_audit_only": _candidate_label_audits(targets),
        "recorded_history_exactly_regenerated": True,
    }
    row["preprobe_confound"] = confound
    return row


def _deep_diagnostics(
    worlds: list[dict[str, Any]], diagnostics: list[dict[str, Any]]
) -> dict[str, Any]:
    by_seed = {int(row["seed"]): row for row in diagnostics if row.get("feasible")}
    rows = []
    midpoint_diffs = []
    order_diffs = []
    for world in worlds:
        if not world["deep_turnover_valid"]:
            continue
        seed = int(world["seed"])
        diag = by_seed[seed]
        targets = world["assignment"]["targets"]
        mplus = [float(value) for value in diag["mplus_intact"]]
        dose_labels = ["A" if target["dose"] >= DOSE_MIDPOINT else "B" for target in targets]
        order_labels = ["A" if target["order"] >= 0.0 else "B" for target in targets]

        def diff(labels: list[str]) -> float | None:
            a = [value for value, label in zip(mplus, labels) if label == "A"]
            b = [value for value, label in zip(mplus, labels) if label == "B"]
            return float(np.mean(a) - np.mean(b)) if a and b else None

        midpoint = diff(dose_labels)
        order = diff(order_labels)
        if midpoint is not None:
            midpoint_diffs.append(midpoint)
        if order is not None:
            order_diffs.append(order)
        rows.append(
            {
                "seed": seed,
                "deep_step": int(diag["dstep"]),
                "dose": [target["dose"] for target in targets],
                "order": [target["order"] for target in targets],
                "mplus": mplus,
                "material_retention_M": [float(value) for value in diag["M_intact"]],
                "retroactive_midpoint_mplus_A_minus_B": midpoint,
                "retroactive_order_sign_mplus_A_minus_B": order,
            }
        )
    return {
        "categorical_H_A_vs_H_B_first_stage": None,
        "reason": "no categorical histories were assigned",
        "protocol_native_continuous_coordinate": (
            "own cumulative dose is primary; order is secondary and was not expected to survive long washout"
        ),
        "audit_only_retroactive_dichotomies_not_estimands": {
            "worlds": rows,
            "dose_midpoint_differences": midpoint_diffs,
            "dose_midpoint_same_sign": bool(midpoint_diffs)
            and all(value > 0 for value in midpoint_diffs)
            or all(value < 0 for value in midpoint_diffs),
            "order_sign_differences": order_diffs,
            "order_sign_worlds_available": len(order_diffs),
        },
        "complete_Mf_and_frozen_11D_H_A_vs_H_B": None,
        "body_geometry_nutrient_H_A_vs_H_B": None,
        "interpretation": (
            "These descriptive values cannot repair the missing randomization. "
            "They also do not show a stable protocol-predicted binary first stage."
        ),
    }


def build_results(
    raw_records: list[dict[str, Any]],
    deep_diagnostics: list[dict[str, Any]],
    seeds: Iterable[int],
    reconstruct_confounds: bool = True,
) -> dict[str, Any]:
    selected = validate_dev_seeds(seeds)
    raw_by_seed = {int(row["seed"]): row for row in raw_records}
    missing = sorted(set(selected) - set(raw_by_seed))
    if missing:
        raise ValueError(f"missing already-open raw records: {missing}")
    worlds = []
    for seed in selected:
        confound = (
            reconstruct_preprobe_confound(seed)
            if reconstruct_confounds
            else {"not_reconstructed": True}
        )
        worlds.append(_world_row(raw_by_seed[seed], confound))

    eligible = [world for world in worlds if world["initial_geometry_eligible"]]
    valid = [world for world in worlds if world["deep_turnover_valid"]]
    all_target_rows = [
        target for world in eligible for target in world["assignment"]["targets"]
    ]
    by_index = {}
    for index in range(cc.K):
        rows = [row for row in all_target_rows if row["target"] == index]
        by_index[str(index)] = {
            "n": len(rows),
            "mean_dose": float(np.mean([row["dose"] for row in rows])),
            "dose_midpoint_A_count": sum(row["dose"] >= DOSE_MIDPOINT for row in rows),
            "order_nonnegative_count": sum(row["order"] >= 0.0 for row in rows),
        }

    nonmemory_targets = [
        target
        for world in eligible
        for target in world["preprobe_confound"].get("targets", [])
    ]
    nonmemory_changed = sum(target["nonmemory_state_changed"] for target in nonmemory_targets)
    midpoint_both = sum(
        all(
            count > 0
            for count in world["assignment"]["candidate_labels_audit_only"]["dose_midpoint"][
                "counts"
            ].values()
        )
        for world in eligible
    )
    order_both = sum(
        all(
            count > 0
            for count in world["assignment"]["candidate_labels_audit_only"]["order_sign"][
                "counts"
            ].values()
        )
        for world in eligible
    )

    return safe(
        {
            "schema": "HISTORY-TRANSPORT-00-DEV-AUDIT-v1",
            "mode": "DEV_ONLY_AUDIT_GATE",
            "decision": "STOP-HISTORY-CONTRAST",
            "canonical_parent": EXPECTED_PARENT,
            "seeds_requested": list(selected),
            "feeding_probe_executed": False,
            "clamp_or_global_variant_executed": False,
            "future_feeding_fields_accessed": False,
            "raw_files_contain_future_feeding_fields": True,
            "outcome_blind_access_rule": (
                "the audit accesses only seed, eligibility/feasibility, deep step, histories, centroids, "
                "sizes, passive material retention and pre-probe memory diagnostics; no beh/rest_beh/own "
                "field is accessed or used"
            ),
            "assignment": assignment_kind(),
            "audit_gate": {
                "exact_history_conditions_recovered": True,
                "continuous_draws_outcome_independent": True,
                "prospective_categorical_A_B_assignment": False,
                "both_assigned_conditions_within_world": False,
                "targets_per_assigned_condition_and_world": None,
                "spatially_balanced_assignment": False,
                "protocol_predicted_binary_direction": None,
                "labels_recoverable_without_future_feeding": (
                    "continuous a1,a2,dose,order yes; categorical H_A/H_B no because none exist"
                ),
                "gate_pass": False,
                "failure_reason": (
                    "The implemented protocol has no assigned H_A/H_B conditions and no implemented Latin-square "
                    "or blocked allocation. Any binary labels would be retrospective relabelling or target selection."
                ),
            },
            "counts": {
                "worlds_requested": len(selected),
                "initial_geometry_eligible": len(eligible),
                "initial_geometry_ineligible": len(worlds) - len(eligible),
                "deep_turnover_valid": len(valid),
                "targets_with_continuous_histories": len(all_target_rows),
                "targets_with_preprobe_nonmemory_change": nonmemory_changed,
                "eligible_worlds_with_both_retroactive_dose_midpoint_classes": midpoint_both,
                "eligible_worlds_with_both_retroactive_order_sign_classes": order_both,
            },
            "spatial_balance_audit": {
                "allocation": "unblocked sequential draws assigned to target indices sorted by size",
                "implemented_latin_square": False,
                "target_index_descriptives": by_index,
                "conclusion": (
                    "No design-based spatial balance guarantee exists. Approximate realized balance cannot "
                    "substitute for the preregistered but unimplemented Latin square."
                ),
            },
            "preprobe_confound_audit": {
                "comparison": "post-history S0 versus same-seed same-time no-drive; no feeding probe",
                "nonmemory_targets_changed": nonmemory_changed,
                "n_targets_compared": len(nonmemory_targets),
                "conclusion": (
                    "The nutrient history is not memory-only: before the proposed intervention it changes "
                    "body/geometry and at least one of rho/U/V/c/N in the compared targets."
                ),
            },
            "first_stage": _deep_diagnostics(valid, deep_diagnostics),
            "worlds": worlds,
            "causal_estimands": {
                "delta_coupled": None,
                "delta_isolated": None,
                "transport_difference": None,
                "retention_ratio": None,
                "reason": "assignment gate failed before intervention implementation or execution",
                "statistical_unit": "original world",
            },
            "boundary_reference_audit": {
                "executed_here": False,
                "qualified_prior_mechanical_reference": (
                    "two-cell replay of the same-seed no-history trajectory; outcome-independent and on-manifold"
                ),
                "matched_sham_only": (
                    "own-trajectory replay is an exact manipulation sham but may carry the target history and "
                    "is not a common history-independent isolation reference"
                ),
                "second_independent_reference": None,
                "conclusion": (
                    "No second qualified on-manifold, history-independent boundary construction is currently available."
                ),
            },
            "global_channel_audit": {
                "executed_here": False,
                "technically_defensible_variants": [
                    {
                        "variant": "predefined no-history up_ref trajectory",
                        "identification": "history-independent and time-varying",
                        "physical_validity": "on-manifold if replayed from the matched no-history world",
                    },
                    {
                        "variant": "predefined no-history constant up_ref",
                        "identification": "history-independent",
                        "physical_validity": "requires a frozen source/time rule and continuity qualification",
                    },
                    {
                        "variant": "up_ref=0 ablation",
                        "identification": "removes global history information",
                        "physical_validity": "engine-valid and previously viable, but a mechanistic ablation rather than ordinary coupling",
                    },
                ],
                "ordinary_dynamic_up_ref": "invalid for local-sufficiency identification if it carries assigned history",
                "prospective_selection": None,
            },
            "mediation": {
                "lam_plus_zero_executed_here": False,
                "result": None,
                "reason": "no valid randomized-history effect exists to mediate",
            },
            "hypothesis_H_RELATIVE": {
                "status": "NOT_TESTED_BY_CAUSAL_CONTRAST",
                "available_dev_observations": (
                    "ambient memory and null-reference reversal motivate the hypothesis, while continuous history "
                    "coordinates remain recoverable; neither fact establishes relative storage"
                ),
                "distinctive_randomized_history_prediction": "not testable without an assigned H_A/H_B first stage",
            },
            "provenance": {
                "raw_source": str(RAW_PATH.relative_to(ROOT)).replace("\\", "/"),
                "raw_sha256": sha256_file(RAW_PATH),
                "deep_diagnostics_source": str(DEEP_DIAGNOSTICS_PATH.relative_to(ROOT)).replace("\\", "/"),
                "deep_diagnostics_sha256": sha256_file(DEEP_DIAGNOSTICS_PATH),
                "assignment_source_files": [
                    "experiments/individuation/exp1_prospective.py",
                    "experiments/individuation/causal_confirm.py",
                    "experiments/individuation/turnover_dev_runner.py",
                    "experiments/individuation/turnover_engine_03g.py",
                ],
            },
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="+", default=list(DEV_SEEDS))
    parser.add_argument(
        "--skip-confound-reconstruction",
        action="store_true",
        help="tests only; the complete DEV audit reconstructs all pre-probe confounds",
    )
    args = parser.parse_args()
    seeds = validate_dev_seeds(args.seeds)
    raw_records = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    diagnostics = json.loads(DEEP_DIAGNOSTICS_PATH.read_text(encoding="utf-8"))
    result = build_results(
        raw_records,
        diagnostics,
        seeds,
        reconstruct_confounds=not args.skip_confound_reconstruction,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"decision": result["decision"], "output": str(args.output)}))


if __name__ == "__main__":
    main()
