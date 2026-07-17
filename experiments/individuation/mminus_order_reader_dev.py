"""M_MINUS-ORDER-READER-00 — frozen DEV-only local attractant-production reader.

The module accepts only the already-open complete worlds from 57001-57024.  It
reconstructs their frozen deep states, validates the parent hashes, and applies
one predeclared symmetric gain perturbation to the existing
``m_minus -> attractant production`` term.  No prospective namespace exists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

from edlab.experiments.sc_mcm import config as MCM_CONFIG
from edlab.substrates.scaffold.engine import EPS
from experiments.individuation import access_structure_noswap_operators as ns
from experiments.individuation import balanced_history_isolation_dev as bh
from experiments.individuation import causal_confirm as cc
from experiments.individuation import counterfactual_history_core_dev as parent
from experiments.individuation.access_structure_operators import exact_state_errors, state_sha256
from experiments.individuation.turnover_diag_engine import DiagEngine


SCHEMA = "M_MINUS-ORDER-READER-00-DEV-v1"
SHARD_SCHEMA = "M_MINUS-ORDER-READER-00-WORLD-v1"
MODE = "DEV_ONLY_EXISTING_57001_57024_NO_PROSPECTIVE"
PARENT_COMMIT = "ea6e6a0ab2ccc3e94eba364ddb459088c96d6033"
PARENT_MANIFEST_SHA256 = "298dcc02d391eb8952d3d293fdaf1bcd9ceef2c032d8e521771ee50cce569457"
PARENT_RAW_PERSISTED_SHA256 = "d4e6f2d9cedcc8b459973e10641b1b28d91b3b52315cbba36120640ef9386da6"
PARENT_RAW_GIT_LF_SHA256 = "12a47621d81d2406a369e26aa6175f12beab2a54e653a1e48276377823ca4e29"
PROTOCOL_SHA256 = "d0096f028b9d9e35d6cabb54b73c0e47ca8ee512efb8b0702c8ab8de86cf2ead"

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
DEFAULT_PARENT_RAW = REPO_ROOT / "docs" / "individuation" / "COUNTERFACTUAL_HISTORY_CORE_00_DEV_RESULTS.json"
DEFAULT_MANIFEST = REPO_ROOT / "docs" / "individuation" / "COUNTERFACTUAL_HISTORY_CORE_00_MANIFEST.json"
DEFAULT_PROTOCOL = REPO_ROOT / "docs" / "individuation" / "M_MINUS_ORDER_READER_00_PROTOCOL.md"
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "individuation" / "M_MINUS_ORDER_READER_00_DEV_RESULTS.json"

DEV_SEEDS = tuple(range(57001, 57025))
COMPLETE_SEEDS = (
    57001, 57003, 57006, 57008, 57009, 57010, 57013, 57015, 57016,
    57017, 57018, 57019, 57020, 57021, 57022, 57023, 57024,
)
HISTORY_NAMES = parent.HISTORY_NAMES
EPSILON = 2.0 / 3.0
GAIN_FRACTIONS = (-EPSILON, 0.0, EPSILON)
GAIN_LABELS = ("minus", "sham", "plus")
SETTLE_STEPS = 40
READER_HORIZON = 1
SIGN_FRACTION = 0.75
NUMERIC_ATOL = 1e-12
NUMERIC_RTOL = 1e-10


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_json(path: Path, payload: dict) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(_safe(payload), indent=2, sort_keys=True, allow_nan=False) + "\n"
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(temp, path)
    return sha256_file(path)


def _safe(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, float)):
        result = float(value)
        if not math.isfinite(result):
            raise ValueError("non-finite value")
        return result
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, dict):
        return {str(key): _safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe(item) for item in value]
    return value


def _numeric_close(a: float, b: float) -> bool:
    return bool(np.isclose(float(a), float(b), atol=NUMERIC_ATOL, rtol=NUMERIC_RTOL))


def _array_close(a: np.ndarray, b: np.ndarray) -> bool:
    return bool(np.allclose(np.asarray(a), np.asarray(b), atol=NUMERIC_ATOL, rtol=NUMERIC_RTOL))


def _frame_sha256(frame: dict) -> str:
    digest = hashlib.sha256()
    for field in sorted(frame):
        array = np.ascontiguousarray(frame[field])
        digest.update(field.encode("utf-8"))
        digest.update(str(array.dtype).encode("ascii"))
        digest.update(np.asarray(array.shape, dtype=np.int64).tobytes())
        digest.update(array.tobytes())
    return digest.hexdigest()


def _mask_sha256(mask: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(mask, dtype=np.uint8).tobytes()).hexdigest()


def _parent_raw_bindings(path: Path) -> tuple[dict, dict[int, dict]]:
    raw_bytes = path.read_bytes()
    direct = hashlib.sha256(raw_bytes).hexdigest()
    if direct == PARENT_RAW_PERSISTED_SHA256:
        persisted_binding = True
    elif direct == PARENT_RAW_GIT_LF_SHA256:
        if b"\r\n" in raw_bytes:
            raise RuntimeError("unexpected mixed/newline-normalized parent raw")
        persisted_binding = hashlib.sha256(raw_bytes.replace(b"\n", b"\r\n")).hexdigest() == PARENT_RAW_PERSISTED_SHA256
    else:
        raise RuntimeError(f"parent raw SHA mismatch: {direct}")
    if not persisted_binding:
        raise RuntimeError("parent persisted raw binding failed")
    payload = json.loads(raw_bytes.decode("utf-8"))
    if payload.get("schema") != parent.SCHEMA or payload.get("status") != "COMPLETE":
        raise RuntimeError("parent raw schema/status mismatch")
    if payload.get("manifest_sha256") != PARENT_MANIFEST_SHA256:
        raise RuntimeError("parent raw manifest binding mismatch")
    rows = {int(row["seed"]): row for row in payload.get("worlds", [])}
    if tuple(rows) != DEV_SEEDS:
        raise RuntimeError("parent raw seed order mismatch")
    complete = tuple(seed for seed, row in rows.items() if row.get("complete_block"))
    if complete != COMPLETE_SEEDS:
        raise RuntimeError("parent complete-world membership mismatch")
    return payload, rows


def validate_frozen_inputs(parent_raw: Path = DEFAULT_PARENT_RAW,
                           manifest_path: Path = DEFAULT_MANIFEST,
                           protocol_path: Path = DEFAULT_PROTOCOL) -> tuple[dict, dict[int, dict]]:
    if sha256_file(manifest_path) != PARENT_MANIFEST_SHA256:
        raise RuntimeError("parent manifest SHA mismatch")
    if sha256_file(protocol_path) != PROTOCOL_SHA256:
        raise RuntimeError("reader protocol SHA mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    parent.validate_manifest_payload(manifest)
    payload, rows = _parent_raw_bindings(parent_raw)
    if tuple(int(seed) for seed in payload.get("seeds", ())) != DEV_SEEDS:
        raise RuntimeError("parent top-level seed family mismatch")
    return manifest, rows


class ReaderGainClampEngine(DiagEngine):
    """Qualified engine with a one-step local fractional gain on the existing reader.

    ``gain_fraction=0`` is byte-identical to ``DiagEngine`` followed by the same
    collar driver.  The stored memory field is never edited.  The adjustment is
    applied only to the c-production contribution after the frozen base update
    has computed ``newm`` and before the common collar frame is imposed.
    """

    def __init__(self, spec, mem, tracer, *, support: np.ndarray, gain_fraction: float,
                 driver: ns.BoundaryDriver | None):
        super().__init__(spec, mem, tracer, up_ref_zero=True)
        self.support = np.asarray(support, dtype=bool).copy()
        self.gain_fraction = float(gain_fraction)
        self.driver = driver
        self.last_source_raw = None
        self.last_core_mass = None
        self.last_weighted_mminus = None

    def step(self, st):
        out = super().step(st)
        memory = out.Mf / np.maximum(out.rho, EPS)[None, :, :]
        m_minus = np.tanh(memory[0] - memory[1])
        lam = float(self.mem.lam_minus)
        gain = np.ones_like(st.rho)
        gain[self.support] = 1.0 + self.gain_fraction
        production = self.spec.s * st.rho * (1.0 + lam * gain * m_minus)
        self.last_source_raw = float(self.spec.dt * production[self.support].sum())
        self.last_core_mass = float(st.rho[self.support].sum())
        self.last_weighted_mminus = float((st.rho * m_minus)[self.support].sum())
        if self.gain_fraction != 0.0 and lam != 0.0:
            delta = (self.spec.dt * self.spec.s * st.rho * lam * m_minus * self.gain_fraction)
            out.c = out.c.copy()
            out.c[self.support] += delta[self.support]
        if self.driver is not None:
            out = self.driver.apply(out)
        return out


def _new_driver(template: ns.BoundaryDriver, frames: Sequence[dict], suffix: str) -> ns.BoundaryDriver:
    return ns.BoundaryDriver(template.ring.copy(), list(frames), label=f"{template.label}:{suffix}")


def _record_common_boundary(reference: dict, ring: np.ndarray, shift: tuple[int, int], mem) -> ns.BoundaryDriver:
    source = bh.standardized_probe_start(reference["state"])
    engine = DiagEngine(MCM_CONFIG.SPEC, mem, MCM_CONFIG.TRACER, up_ref_zero=True)
    return ns.record_boundary(
        source, engine, ring, SETTLE_STEPS + READER_HORIZON, shift=shift,
        label=f"same_seed_no_history_no_drive_lamminus_{float(mem.lam_minus):.2f}",
    )


def _settle(deep: dict, core_mask: np.ndarray, driver: ns.BoundaryDriver, mem) -> dict:
    current = bh.standardized_probe_start(deep["state"])
    tracker = parent._new_tracker([deep["region"]], current.step)
    engine = ns.NoSwapClampEngine(
        MCM_CONFIG.SPEC, mem, MCM_CONFIG.TRACER,
        driver=_new_driver(driver, driver.frames[:SETTLE_STEPS], "settle"), up_ref_zero=True,
    )
    events = {}
    max_coverage = 0.0
    for elapsed in range(1, SETTLE_STEPS + 1):
        current = engine.step(current)
        update = parent._tracker_update(tracker, current)
        max_coverage = max(max_coverage, float(update["coverage"]))
        for track_id, status in update["events"].items():
            events.setdefault(str(track_id), {
                "elapsed_step": elapsed, "absolute_step": int(current.step), "status": status,
            })
    alive = parent._focal_alive(tracker, 0)
    region = tracker.tracks[0].mask.copy() if alive else np.zeros_like(core_mask)
    body_inside = bool(alive and not np.any(region & ~core_mask))
    valid = bool(alive and not events and max_coverage < parent.COVER_CAP and body_inside)
    return {
        "valid": valid,
        "state": current,
        "region": region,
        "events": events,
        "max_coverage": max_coverage,
        "body_inside_core": body_inside,
        "state_sha256": state_sha256(current),
        "core_mass": float(current.rho[core_mask].sum()),
        "body_mass": float(current.rho[region].sum()) if alive else None,
        "body_area": int(region.sum()) if alive else None,
    }


def _arm(settled_state, core_mask: np.ndarray, final_frame: dict, ring: np.ndarray,
         mem, label: str, gain_fraction: float) -> tuple[dict, object]:
    driver = ns.BoundaryDriver(ring.copy(), [final_frame], label=f"reader:{label}")
    engine = ReaderGainClampEngine(
        MCM_CONFIG.SPEC, mem, MCM_CONFIG.TRACER, support=core_mask,
        gain_fraction=gain_fraction, driver=driver,
    )
    input_state = settled_state.copy()
    input_hash = state_sha256(input_state)
    output = engine.step(input_state)
    if engine.last_source_raw is None or engine.last_core_mass is None:
        raise RuntimeError("reader engine failed to expose source")
    mass = float(engine.last_core_mass)
    if not mass > 0:
        raise RuntimeError("non-positive reader core mass")
    return {
        "label": label,
        "gain_fraction": float(gain_fraction),
        "effective_local_lam_minus": float(mem.lam_minus * (1.0 + gain_fraction)),
        "input_state_sha256": input_hash,
        "collar_frame_sha256": _frame_sha256(final_frame),
        "Y_attractant_production_raw": float(engine.last_source_raw),
        "Y_per_core_mass": float(engine.last_source_raw / mass),
        "core_mass": mass,
        "weighted_mminus": float(engine.last_weighted_mminus),
        "output_state_sha256": state_sha256(output),
        "output_c_sha256": hashlib.sha256(np.ascontiguousarray(output.c).tobytes()).hexdigest(),
    }, output


def _probe_condition_once(deep: dict, reference: dict, mem) -> dict:
    geometry = parent._geometry(deep)
    if not geometry["valid"]:
        return {"valid": False, "reason": geometry["reason"]}
    core_mask = geometry["core"]
    ring = geometry["ring"]
    if np.any(core_mask & ring):
        raise RuntimeError("core/ring overlap")
    shift = ns._shift(reference["center"], deep["center"])
    boundary = _record_common_boundary(reference, ring, shift, mem)
    settled = _settle(deep, core_mask, boundary, mem)
    if not settled["valid"]:
        return {
            "valid": False, "reason": "standardized_settle_invalid",
            "settle": {key: _safe(value) for key, value in settled.items() if key not in {"state", "region"}},
        }
    final_frame = boundary.frames[SETTLE_STEPS]
    arms = {}
    states = {}
    for label, gain_fraction in zip(GAIN_LABELS, GAIN_FRACTIONS):
        arms[label], states[label] = _arm(
            settled["state"], core_mask, final_frame, ring, mem, label, gain_fraction,
        )

    base_driver = ns.BoundaryDriver(ring.copy(), [final_frame], label="probe_disabled_identity")
    base_engine = ns.NoSwapClampEngine(
        MCM_CONFIG.SPEC, mem, MCM_CONFIG.TRACER, driver=base_driver, up_ref_zero=True,
    )
    base_output = base_engine.step(settled["state"].copy())
    sham_identity = state_sha256(base_output) == arms["sham"]["output_state_sha256"]
    identical_inputs = len({arms[label]["input_state_sha256"] for label in GAIN_LABELS}) == 1
    identical_frames = len({arms[label]["collar_frame_sha256"] for label in GAIN_LABELS}) == 1

    y_minus = arms["minus"]["Y_attractant_production_raw"]
    y_sham = arms["sham"]["Y_attractant_production_raw"]
    y_plus = arms["plus"]["Y_attractant_production_raw"]
    source_symmetric = _numeric_close(y_plus - y_sham, y_sham - y_minus)
    c_symmetric = _array_close(states["plus"].c - states["sham"].c,
                               -(states["minus"].c - states["sham"].c))
    non_c_exact = True
    for field in ns.STATE_FIELDS:
        if field == "c":
            continue
        reference_field = getattr(states["sham"], field)
        non_c_exact = non_c_exact and all(
            np.array_equal(getattr(states[label], field), reference_field) for label in ("minus", "plus")
        )
    non_c_exact = bool(non_c_exact and all(states[label].step == states["sham"].step for label in ("minus", "plus")))
    chi_raw = float((y_plus - y_minus) / (2.0 * EPSILON))
    chi_mass = float(chi_raw / arms["sham"]["core_mass"])
    analytic_chi = float(
        MCM_CONFIG.SPEC.dt * MCM_CONFIG.SPEC.s * mem.lam_minus * arms["sham"]["weighted_mminus"]
    )
    analytic_match = _numeric_close(chi_raw, analytic_chi)
    ablated_exact = True
    if float(mem.lam_minus) == 0.0:
        ablated_exact = bool(
            len({arms[label]["output_state_sha256"] for label in GAIN_LABELS}) == 1
            and _numeric_close(chi_raw, 0.0)
        )
    manipulation_valid = bool(
        identical_inputs and identical_frames and sham_identity and source_symmetric and c_symmetric
        and non_c_exact and analytic_match and ablated_exact
    )
    return {
        "valid": manipulation_valid,
        "reason": None if manipulation_valid else "reader_manipulation_gate_failed",
        "lam_minus": float(mem.lam_minus),
        "up_ref_zero": True,
        "epsilon": EPSILON,
        "duration_steps": 1,
        "horizon_steps": 1,
        "support": {
            "kind": "fixed_radius_10_core",
            "mask_sha256": _mask_sha256(core_mask),
            "cells": int(core_mask.sum()),
            "collar_cells": int(ring.sum()),
        },
        "settle": {key: _safe(value) for key, value in settled.items() if key not in {"state", "region"}},
        "boundary": {
            "label": boundary.label,
            "history_specific_input": False,
            "translation": list(shift),
            "final_frame_sha256": _frame_sha256(final_frame),
        },
        "arms": arms,
        "chi_raw": chi_raw,
        "chi_per_core_mass": chi_mass,
        "analytic_chi": analytic_chi,
        "gates": {
            "identical_pre_divergence_states": identical_inputs,
            "identical_collar_frame": identical_frames,
            "probe_disabled_engine_identity": sham_identity,
            "source_sign_reversal": source_symmetric,
            "c_field_sign_reversal": c_symmetric,
            "only_c_differs_across_reader_arms": non_c_exact,
            "analytic_susceptibility_match": analytic_match,
            "lam_minus_zero_arms_identical": ablated_exact,
            "tracker_independent_primary_readout": True,
        },
    }


def _probe_condition(deep: dict, reference: dict, mem) -> dict:
    first = _probe_condition_once(deep, reference, mem)
    second = _probe_condition_once(deep, reference, mem)
    deterministic = json.dumps(_safe(first), sort_keys=True, separators=(",", ":")) == json.dumps(
        _safe(second), sort_keys=True, separators=(",", ":")
    )
    first["deterministic_rerun_exact"] = deterministic
    first["valid"] = bool(first.get("valid") and deterministic)
    if not deterministic:
        first["reason"] = "deterministic_rerun_mismatch"
    return first


def _factorial(values: dict[str, float]) -> dict[str, float]:
    return {key: float(value) for key, value in parent.factorial_scalar(values).items()}


def scalar_sign_derivation() -> dict:
    dt = float(MCM_CONFIG.SPEC.dt)
    eta_w = float(cc.MEM_INTACT.eta_w)
    delta_input = float(parent.HISTORIES["H_L_EARLY"][0] - parent.HISTORIES["H_L_LATE"][0])
    duration = int(parent.PHASE)
    settle = int(parent.SETTLE)
    values = {}
    for label, eta_d in (("m1", cc.MEM_INTACT.eta_d1), ("m2", cc.MEM_INTACT.eta_d2)):
        q = 1.0 - dt * float(eta_d)
        contrast = -dt * eta_w * delta_input * q**settle * (1.0 - q**duration) ** 2 / (1.0 - q)
        values[label] = {"q": q, "early_minus_late": float(contrast)}
    difference = values["m1"]["early_minus_late"] - values["m2"]["early_minus_late"]
    return {
        "dt": dt,
        "eta_w": eta_w,
        "duration_steps": duration,
        "settle_steps": settle,
        "delta_input": delta_input,
        "components": values,
        "m1_minus_m2_early_minus_late": float(difference),
        "tanh_near_origin_early_minus_late": float(math.tanh(difference)),
        "predicted_sign": "positive" if difference > 0 else "negative" if difference < 0 else "zero",
    }


def run_seed(seed: int, *, parent_raw: Path = DEFAULT_PARENT_RAW,
             manifest_path: Path = DEFAULT_MANIFEST,
             protocol_path: Path = DEFAULT_PROTOCOL) -> dict:
    seed = int(seed)
    if seed not in COMPLETE_SEEDS:
        raise RuntimeError(f"reader execution refused for non-complete seed {seed}")
    manifest, parent_rows = validate_frozen_inputs(parent_raw, manifest_path, protocol_path)
    expected = parent_rows[seed]
    checkpoint = parent.make_checkpoint(seed)
    if checkpoint["focal_id"] is None:
        raise RuntimeError(f"parent-complete seed {seed} has no focal target")
    clone_validation = parent.validate_four_clones(checkpoint)
    if not clone_validation["valid"]:
        raise RuntimeError(f"clone validation failed for {seed}")
    if checkpoint["checkpoint_bundle_sha256"] != expected["clone_checkpoint"]["checkpoint_bundle_sha256"]:
        raise RuntimeError(f"checkpoint hash mismatch for {seed}")
    histories = parent.run_histories(checkpoint, parent.execution_order(seed))
    focal_entity = checkpoint["entities"][checkpoint["focal_id"]]
    deep_states = {}
    deep_features = {}
    deep_hash_matches = {}
    for name in HISTORY_NAMES:
        branch = histories[name]
        if not branch["valid"]:
            raise RuntimeError(f"parent-complete history reconstruction failed {seed} {name}")
        deep = parent.turnover_fixed(branch["state"], branch["focal_region"])
        if not deep["valid"]:
            raise RuntimeError(f"parent-complete deep reconstruction failed {seed} {name}")
        expected_hash = expected["branches"][name]["deep"]["state_sha256"]
        deep_hash_matches[name] = bool(deep["state_sha256"] == expected_hash)
        if not deep_hash_matches[name]:
            raise RuntimeError(f"deep state hash mismatch {seed} {name}")
        feature = parent.first_stage(deep, focal_entity, branch["patch"])
        expected_mminus = expected["branches"][name]["probe"]["first_stage"]["mminus_mean"]
        if not _numeric_close(feature["mminus_mean"], expected_mminus):
            raise RuntimeError(f"deep mminus reproduction mismatch {seed} {name}")
        deep_states[name] = deep
        deep_features[name] = {
            "mminus_mean": float(feature["mminus_mean"]),
            "mplus_mean": float(feature["mplus_mean"]),
            "body_mass": float(feature["body_mass"]),
            "body_size": int(feature["body_size"]),
            "body_rg": float(feature["body_rg"]),
        }
    reference = parent.no_drive_reference(checkpoint)
    if not reference["valid"]:
        raise RuntimeError(f"reference reconstruction failed for {seed}")
    expected_reference = expected["common_boundary_reference"]["state_sha256"]
    if reference["state_sha256"] != expected_reference:
        raise RuntimeError(f"reference state hash mismatch for {seed}")

    mem_intact = cc.MEM_INTACT
    mem_ablate = replace(cc.MEM_INTACT, lam_minus=0.0)
    per_history = {}
    for name in HISTORY_NAMES:
        intact = _probe_condition(deep_states[name], reference, mem_intact)
        ablated = _probe_condition(deep_states[name], reference, mem_ablate)
        per_history[name] = {
            "deep": {
                "state_sha256": deep_states[name]["state_sha256"],
                "parent_state_sha256": expected["branches"][name]["deep"]["state_sha256"],
                "parent_hash_match": deep_hash_matches[name],
                **deep_features[name],
            },
            "intact": intact,
            "lam_minus_zero": ablated,
        }
    if not all(per_history[name][condition]["valid"]
               for name in HISTORY_NAMES for condition in ("intact", "lam_minus_zero")):
        raise RuntimeError(f"reader manipulation invalid for {seed}")

    mminus = _factorial({name: per_history[name]["deep"]["mminus_mean"] for name in HISTORY_NAMES})
    raw = _factorial({name: per_history[name]["intact"]["chi_raw"] for name in HISTORY_NAMES})
    normalized = _factorial({
        name: per_history[name]["intact"]["chi_per_core_mass"] for name in HISTORY_NAMES
    })
    ablated = _factorial({
        name: per_history[name]["lam_minus_zero"]["chi_raw"] for name in HISTORY_NAMES
    })
    ablated_normalized = _factorial({
        name: per_history[name]["lam_minus_zero"]["chi_per_core_mass"] for name in HISTORY_NAMES
    })
    low_order = float(per_history["H_L_EARLY"]["intact"]["chi_raw"]
                      - per_history["H_L_LATE"]["intact"]["chi_raw"])
    high_order = float(per_history["H_H_EARLY"]["intact"]["chi_raw"]
                       - per_history["H_H_LATE"]["intact"]["chi_raw"])
    low_order_normalized = float(per_history["H_L_EARLY"]["intact"]["chi_per_core_mass"]
                                 - per_history["H_L_LATE"]["intact"]["chi_per_core_mass"])
    high_order_normalized = float(per_history["H_H_EARLY"]["intact"]["chi_per_core_mass"]
                                  - per_history["H_H_LATE"]["intact"]["chi_per_core_mass"])
    attenuation = float(1.0 - abs(ablated["order"]) / max(abs(raw["order"]), 1e-300))
    manipulation_valid = bool(
        all(deep_hash_matches.values())
        and all(per_history[name][condition]["valid"]
                for name in HISTORY_NAMES for condition in ("intact", "lam_minus_zero"))
    )
    return {
        "schema": SHARD_SCHEMA,
        "mode": MODE,
        "protocol_sha256": PROTOCOL_SHA256,
        "parent_commit": PARENT_COMMIT,
        "parent_manifest_sha256": PARENT_MANIFEST_SHA256,
        "parent_raw_persisted_sha256": PARENT_RAW_PERSISTED_SHA256,
        "seed": seed,
        "original_world_statistical_unit": True,
        "complete_parent_world": True,
        "clone_validation": clone_validation,
        "reference_state_sha256": reference["state_sha256"],
        "reference_parent_hash_match": True,
        "histories": per_history,
        "contrasts": {
            "deep_mminus": mminus,
            "chi_raw": raw,
            "chi_per_core_mass": normalized,
            "chi_raw_lam_minus_zero": ablated,
            "chi_per_core_mass_lam_minus_zero": ablated_normalized,
            "low_dose_order_raw": low_order,
            "high_dose_order_raw": high_order,
            "low_dose_order_per_core_mass": low_order_normalized,
            "high_dose_order_per_core_mass": high_order_normalized,
            "order_attenuation_fraction": attenuation,
        },
        "manipulation_valid": manipulation_valid,
        "no_new_seed_namespace": True,
    }


def _summary(values: Iterable[float], expected: str | None = None) -> dict:
    return bh._summary(list(values), expected=expected)


def aggregate(worlds: list[dict], parent_rows: dict[int, dict]) -> dict:
    worlds = sorted(worlds, key=lambda row: int(row["seed"]))
    if tuple(int(row["seed"]) for row in worlds) != COMPLETE_SEEDS:
        raise RuntimeError("reader shard set mismatch")
    if not all(row.get("manipulation_valid") for row in worlds):
        classification = "MANIPULATION_INVALID"
    else:
        state = _summary((row["contrasts"]["deep_mminus"]["order"] for row in worlds), expected="positive")
        order_raw = _summary((row["contrasts"]["chi_raw"]["order"] for row in worlds), expected="positive")
        order_norm = _summary((row["contrasts"]["chi_per_core_mass"]["order"] for row in worlds), expected="positive")
        low_raw = _summary((row["contrasts"]["low_dose_order_raw"] for row in worlds), expected="positive")
        high_raw = _summary((row["contrasts"]["high_dose_order_raw"] for row in worlds), expected="positive")
        ablated_order = _summary((row["contrasts"]["chi_raw_lam_minus_zero"]["order"] for row in worlds))
        attenuation = _summary((row["contrasts"]["order_attenuation_fraction"] for row in worlds))
        ablate_ci = ablated_order.get("ci95_t", [None, None])
        ablate_contains_zero = bool(
            ablate_ci[0] is not None and ablate_ci[0] <= 0 <= ablate_ci[1]
        )
        candidate = bool(
            state.get("passes_expected_orientation_and_ci")
            and order_raw.get("passes_expected_orientation_and_ci")
            and low_raw.get("positive", 0) >= low_raw.get("required_same_orientation", 10**9)
            and high_raw.get("positive", 0) >= high_raw.get("required_same_orientation", 10**9)
            and order_norm.get("passes_expected_orientation_and_ci")
            and attenuation.get("mean", -math.inf) >= 0.90
            and ablate_contains_zero
        )
        primary_established = bool(order_raw.get("passes_expected_orientation_and_ci"))
        normalized_reversal = bool(
            order_raw.get("mean", 0.0) > 0 and order_norm.get("mean", 0.0) <= 0
        )
        ablation_persists = bool(
            ablated_order.get("ci95_t", [None, None])[0] is not None
            and (ablated_order["ci95_t"][0] > 0 or ablated_order["ci95_t"][1] < 0)
        )
        if candidate:
            classification = "ORDER_READER_CANDIDATE"
        elif state.get("passes_expected_orientation_and_ci") and not primary_established:
            classification = "ORDER_STATE_WITHOUT_READER_EFFECT"
        elif primary_established and (ablation_persists or normalized_reversal):
            classification = "PHYSICAL_SUSCEPTIBILITY"
        else:
            classification = "UNRESOLVED"

    state = _summary((row["contrasts"]["deep_mminus"]["order"] for row in worlds), expected="positive")
    susceptibility = {
        metric: {
            contrast: _summary(
                (row["contrasts"][metric][contrast] for row in worlds),
                expected="positive" if contrast == "order" and metric in {"chi_raw", "chi_per_core_mass"} else None,
            )
            for contrast in ("dose", "order", "interaction")
        }
        for metric in ("chi_raw", "chi_per_core_mass", "chi_raw_lam_minus_zero",
                       "chi_per_core_mass_lam_minus_zero")
    }
    dose_levels = {
        key: _summary((row["contrasts"][key] for row in worlds), expected="positive")
        for key in (
            "low_dose_order_raw", "high_dose_order_raw",
            "low_dose_order_per_core_mass", "high_dose_order_per_core_mass",
        )
    }
    attenuation = _summary((row["contrasts"]["order_attenuation_fraction"] for row in worlds))
    manipulation_gates = {
        "all_worlds_valid": all(row.get("manipulation_valid") for row in worlds),
        "all_deep_parent_hashes_match": all(
            history["deep"]["parent_hash_match"]
            for row in worlds for history in row["histories"].values()
        ),
        "all_deterministic_reruns_exact": all(
            history[condition]["deterministic_rerun_exact"]
            for row in worlds for history in row["histories"].values()
            for condition in ("intact", "lam_minus_zero")
        ),
        "all_probe_disabled_identities": all(
            history[condition]["gates"]["probe_disabled_engine_identity"]
            for row in worlds for history in row["histories"].values()
            for condition in ("intact", "lam_minus_zero")
        ),
        "all_lam_minus_zero_arms_identical": all(
            history["lam_minus_zero"]["gates"]["lam_minus_zero_arms_identical"]
            for row in worlds for history in row["histories"].values()
        ),
        "tracker_independent_primary_readout": True,
        "no_pseudoreplication": True,
    }
    return {
        "schema": SCHEMA,
        "status": "COMPLETE",
        "mode": MODE,
        "parent_commit": PARENT_COMMIT,
        "parent_manifest_sha256": PARENT_MANIFEST_SHA256,
        "parent_raw_persisted_sha256": PARENT_RAW_PERSISTED_SHA256,
        "parent_raw_git_lf_sha256": PARENT_RAW_GIT_LF_SHA256,
        "protocol_sha256": PROTOCOL_SHA256,
        "seeds_authorized": list(DEV_SEEDS),
        "seeds_with_new_reader_output": list(COMPLETE_SEEDS),
        "parent_incomplete_worlds_not_rerun": [seed for seed in DEV_SEEDS if seed not in COMPLETE_SEEDS],
        "n_original_worlds": len(worlds),
        "statistical_unit": "original source world",
        "counterfactual_branches_or_perturbation_arms_count_toward_n": False,
        "reader": {
            "primary_observable": "one-step integrated local attractant production source",
            "perturbation": "fractional gain of existing local lam_minus*m_minus production term",
            "epsilon": EPSILON,
            "effective_local_lam_minus": {"minus": 0.05, "sham": 0.15, "plus": 0.25},
            "duration_steps": 1,
            "horizon_steps": 1,
            "isolation": "qualified two-cell clamp, up_ref=0, same-seed no-history no-drive boundary",
            "normalization": "per pre-perturbation fixed-core rho mass",
        },
        "deep_mminus_order": state,
        "susceptibility": susceptibility,
        "dose_level_order": dose_levels,
        "lam_minus_mediation": {
            "order_attenuation_fraction": attenuation,
            "required_minimum": 0.90,
        },
        "manipulation_gates": manipulation_gates,
        "classification": classification,
        "sign_theory": "SIGN_THEORY_CORRECTED",
        "permitted_claim": (
            "DEV evidence that temporal order changes a local m_minus-linked attractant-production response "
            "operator under standardized inputs."
            if classification == "ORDER_READER_CANDIDATE" else None
        ),
        "claim_boundary": (
            "No ownership, individual memory, identity, heredity, prospective confirmation, feeding-order effect, "
            "or active reconstruction is established. The parent NO_MEMORY_FIRST_STAGE STOP verdict is unchanged."
        ),
        "parent_world_dispositions": [
            {"seed": seed, "complete_parent_world": bool(parent_rows[seed].get("complete_block")),
             "parent_reason": parent_rows[seed].get("reason")}
            for seed in DEV_SEEDS
        ],
        "worlds": worlds,
    }


def _run_seed_to_path(seed: int, shard_dir: str, parent_raw: str,
                      manifest: str, protocol: str) -> str:
    output = Path(shard_dir) / f"world_{int(seed)}.json"
    result = run_seed(
        int(seed), parent_raw=Path(parent_raw), manifest_path=Path(manifest), protocol_path=Path(protocol),
    )
    _write_json(output, result)
    return str(output)


def run_all(shard_dir: Path, jobs: int, parent_raw: Path, manifest: Path, protocol: Path) -> None:
    validate_frozen_inputs(parent_raw, manifest, protocol)
    shard_dir.mkdir(parents=True, exist_ok=True)
    pending = []
    for seed in COMPLETE_SEEDS:
        path = shard_dir / f"world_{seed}.json"
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("schema") != SHARD_SCHEMA or int(payload.get("seed", -1)) != seed:
                raise RuntimeError(f"incompatible existing shard {path}")
            continue
        pending.append(seed)
    if jobs <= 1:
        for seed in pending:
            _run_seed_to_path(seed, str(shard_dir), str(parent_raw), str(manifest), str(protocol))
    else:
        with ProcessPoolExecutor(max_workers=jobs) as pool:
            futures = [pool.submit(
                _run_seed_to_path, seed, str(shard_dir), str(parent_raw), str(manifest), str(protocol)
            ) for seed in pending]
            for future in futures:
                future.result()


def merge(shard_dir: Path, output: Path, parent_raw: Path, manifest: Path, protocol: Path) -> dict:
    _, parent_rows = validate_frozen_inputs(parent_raw, manifest, protocol)
    worlds = []
    for seed in COMPLETE_SEEDS:
        path = shard_dir / f"world_{seed}.json"
        if not path.exists():
            raise RuntimeError(f"missing reader shard {seed}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema") != SHARD_SCHEMA or int(payload.get("seed", -1)) != seed:
            raise RuntimeError(f"invalid reader shard {seed}")
        worlds.append(payload)
    result = aggregate(worlds, parent_rows)
    _write_json(output, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-raw", type=Path, default=DEFAULT_PARENT_RAW)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--shard-dir", type=Path)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--run-all", action="store_true")
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--merge", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.seed is not None:
        if args.shard_dir is None:
            raise SystemExit("--shard-dir is required with --seed")
        print(_run_seed_to_path(
            args.seed, str(args.shard_dir), str(args.parent_raw), str(args.manifest), str(args.protocol)
        ))
    elif args.run_all:
        if args.shard_dir is None:
            raise SystemExit("--shard-dir is required with --run-all")
        run_all(args.shard_dir, max(1, int(args.jobs)), args.parent_raw, args.manifest, args.protocol)
    elif args.merge:
        if args.shard_dir is None:
            raise SystemExit("--shard-dir is required with --merge")
        result = merge(args.shard_dir, args.output, args.parent_raw, args.manifest, args.protocol)
        print(result["classification"])
    else:
        validate_frozen_inputs(args.parent_raw, args.manifest, args.protocol)
        print(json.dumps({
            "phase_a": "VALID_READER",
            "reader": "local attractant production",
            "sign_theory": "SIGN_THEORY_CORRECTED",
            "protocol_sha256": PROTOCOL_SHA256,
            "new_reader_output_generated": False,
        }, sort_keys=True))


if __name__ == "__main__":
    main()
