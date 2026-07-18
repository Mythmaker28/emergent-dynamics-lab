"""Deterministic synthetic-only qualification for CAA01 Stage A."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import types

import numpy as np


ROOT = Path(__file__).resolve().parents[2]


def _package(name: str, relative: str) -> None:
    module = types.ModuleType(name)
    module.__path__ = [str(ROOT / relative)]
    module.__package__ = name
    sys.modules[name] = module


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load allowlisted module {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Do not execute edlab/__init__.py or edlab/experiments/__init__.py: the latter
# imports scientific analyzers.  Only exact hash-bound engine files are loaded.
_package("edlab", "edlab")
_package("edlab.substrates", "edlab/substrates")
_package("edlab.substrates.reaction_diffusion", "edlab/substrates/reaction_diffusion")
rd = _load("edlab.substrates.reaction_diffusion.engine", "edlab/substrates/reaction_diffusion/engine.py")
_package("edlab.substrates.scaffold", "edlab/substrates/scaffold")
scaffold = _load("edlab.substrates.scaffold.engine", "edlab/substrates/scaffold/engine.py")
_package("edlab.experiments", "edlab/experiments")
_package("edlab.experiments.sc_iom", "edlab/experiments/sc_iom")
iom = _load("edlab.experiments.sc_iom.engine", "edlab/experiments/sc_iom/engine.py")
_package("edlab.experiments.sc_mcm", "edlab/experiments/sc_mcm")
mcm = _load("edlab.experiments.sc_mcm.engine", "edlab/experiments/sc_mcm/engine.py")
caa = _load("caa_stage_a", "experiments/individuation/causal_addressability_stage_a.py")


class SyntheticTracer:
    def __init__(self, cohorts: int = 3):
        self.cohorts = cohorts

    def active_feed_cohort(self, step: int) -> int:
        return int(step) % self.cohorts


def synthetic_engine(n: int = 8):
    spec = scaffold.ScaffoldSpec(size=n)
    mem = mcm.MCParams()
    return mcm.MultiChannelMemoryEngine(spec, mem, SyntheticTracer())


def synthetic_state(n: int = 8, step: int = 10):
    x, y = np.indices((n, n), dtype=np.float64)
    rho = 0.23 + 0.012 * x + 0.007 * y + 0.003 * ((x + y) % 2)
    U = rho * (0.68 + 0.011 * x - 0.004 * y)
    V = rho * (0.37 + 0.006 * y + 0.002 * x)
    c = 0.19 + 0.013 * x + 0.009 * y + 0.002 * ((2 * x + y) % 3)
    nutrient = 0.71 + 0.004 * x - 0.003 * y + 0.001 * ((x + 2 * y) % 4)
    cohorts = np.stack((0.2 * rho, 0.35 * rho, 0.45 * rho))
    uptake = 0.008 + 0.0007 * x + 0.0003 * y
    m1 = rho * (0.16 + 0.009 * x - 0.003 * y)
    m2 = rho * (-0.07 + 0.004 * y + 0.002 * x)
    memory = np.stack((m1, m2))
    return iom.IOMState(rho, U, V, c, nutrient, cohorts, uptake, memory, step)


def interior_mask(n: int = 8) -> np.ndarray:
    mask = np.zeros((n, n), dtype=bool)
    mask[2:5, 3:6] = True
    return mask


def periodic_mask(n: int = 8) -> np.ndarray:
    mask = np.zeros((n, n), dtype=bool)
    mask[[0, n - 1], :] = True
    mask[:, [0, n - 1]] = True
    return mask


def probes(n: int = 8) -> tuple[np.ndarray, np.ndarray]:
    x, y = np.indices((n, n), dtype=np.float64)
    p0 = 0.012 + 0.0004 * x + 0.0002 * y
    p1 = 0.007 + 0.0001 * x - 0.00015 * y
    return p0, p1


def assert_state_exact(left, right) -> None:
    assert left.step == right.step
    for field in caa.STATE_FIELDS:
        assert np.array_equal(getattr(left, field), getattr(right, field)), field


def _local_uptake_reference(wrapper, state, plan):
    sp = wrapper.frozen.spec
    mp = wrapper.frozen.mem
    dt = sp.dt
    transport, _, _ = wrapper._transport(
        state.rho, state.U, state.V, state.c, state.C, state.Mf, plan, 1
    )
    rho = state.rho + dt * transport["rho"]
    U = state.U + dt * transport["U"]
    V = state.V + dt * transport["V"]
    Mf = state.Mf + dt * transport["Mf"]
    u = U / np.maximum(rho, caa.EPS)
    v = V / np.maximum(rho, caa.EPS)
    sig = (u - v) / (u + v + caa.EPS)
    m = Mf / np.maximum(rho, caa.EPS)[None, :, :]
    m_plus = np.tanh(m[0] + m[1])
    m_plus = np.where(plan.target_mask, 0.0, m_plus)
    qq = np.maximum(0.0, 1.0 - rho / sp.rho_max)
    g = dt * sp.g0 * rho * state.N * qq * (1.0 + sp.beta * sig) * (1.0 + mp.lam_plus * m_plus)
    return np.clip(g, 0.0, np.maximum(state.N, 0.0))


def test_firewall_loads_no_scientific_analyzer():
    forbidden = {
        "edlab.experiments.analyze_streaming",
        "edlab.experiments.baseline",
        "edlab.experiments.streaming",
    }
    assert forbidden.isdisjoint(sys.modules)


def test_open_and_direct_delegation_are_bit_exact_on_heterogeneous_boundaries():
    for mask_factory in (interior_mask, periodic_mask):
        engine = synthetic_engine()
        wrapper = caa.ConservativeAccessEngine(engine)
        source = synthetic_state()
        schedule = probes()
        state = caa.apply_common_probe(source, schedule[0])
        expected = engine.step(state)
        delegated_none = wrapper.step(state, None)
        open_plan = caa.compile_plan(source, mask_factory(), l_available=1, e_available=1, probe_schedule=schedule)
        delegated_open = wrapper.step(state, open_plan)
        assert_state_exact(expected, delegated_none)
        assert_state_exact(expected, delegated_open)
        assert caa.state_sha256(state) == caa.state_sha256(caa.apply_common_probe(source, schedule[0]))


def test_forced_neutral_active_kernels_are_bit_exact_for_two_updates():
    for mask_factory in (interior_mask, periodic_mask):
        engine = synthetic_engine()
        wrapper = caa.ConservativeAccessEngine(engine)
        source = synthetic_state()
        schedule = probes()
        plan = caa.compile_plan(source, mask_factory(), l_available=1, e_available=1, probe_schedule=schedule)
        step0 = caa.apply_common_probe(source, schedule[0])
        expected1 = engine.step(step0)
        active1 = wrapper.step_with_diagnostics(step0, plan, force_active=True)
        assert not active1.diagnostics["parent_delegated"]
        assert active1.diagnostics["active_kernel"]
        assert_state_exact(expected1, active1.state)
        step1 = caa.apply_common_probe(expected1, schedule[1])
        expected2 = engine.step(step1)
        active2 = wrapper.step_with_diagnostics(step1, plan, force_active=True)
        assert_state_exact(expected2, active2.state)


def test_local_port_is_exactly_first_update_target_mplus_to_uptake_only():
    engine = synthetic_engine()
    wrapper = caa.ConservativeAccessEngine(engine)
    source = synthetic_state()
    schedule = probes()
    mask = interior_mask()
    plan = caa.compile_plan(source, mask, l_available=0, e_available=1, probe_schedule=schedule)
    first_input = caa.apply_common_probe(source, schedule[0])
    input_hash = caa.state_sha256(first_input)
    first = wrapper.step_with_diagnostics(first_input, plan)
    expected_uptake = _local_uptake_reference(wrapper, first_input, plan)
    assert np.array_equal(first.state.uptake, expected_uptake)
    frozen = engine.step(first_input)
    assert np.array_equal(first.state.uptake[~mask], frozen.uptake[~mask])
    assert np.any(first.state.uptake[mask] != frozen.uptake[mask])
    assert caa.state_sha256(first_input) == input_hash
    assert first.diagnostics["local_gate_active"]
    assert engine.mem.eta_w == mcm.MCParams().eta_w

    second_input = caa.apply_common_probe(first.state, schedule[1])
    second = wrapper.step_with_diagnostics(second_input, plan)
    assert second.diagnostics["parent_delegated"]
    assert not second.diagnostics["local_gate_active"]
    assert_state_exact(engine.step(second_input), second.state)


def test_compile_is_clone_order_independent_and_polarity_is_availability():
    source = synthetic_state()
    schedule = probes()
    left = caa.compile_four_arms(source, interior_mask(), probe_schedule=schedule, compile_order=("L", "E"))
    right = caa.compile_four_arms(source, interior_mask(), probe_schedule=schedule, compile_order=("E", "L"))
    assert set(left) == {"L0E0", "L1E0", "L0E1", "L1E1"}
    for name, values in caa.ARM_SETTINGS.items():
        assert (left[name].l_available, left[name].e_available) == values
        assert left[name].canonical_plan_hash == right[name].canonical_plan_hash
    clone_a = caa.exact_clone(source)
    clone_b = caa.exact_clone(source)
    clone_a.rho[0, 0] += 1.0
    assert clone_b.rho[0, 0] == source.rho[0, 0]
    assert "K00" not in caa.ARM_SETTINGS


def test_default_and_explicit_probe_schedules_are_immutable():
    source = synthetic_state()
    explicit = caa.compile_plan(
        source, interior_mask(), l_available=1, e_available=1, probe_schedule=probes()
    )
    default = caa.compile_plan(source, interior_mask(), l_available=1, e_available=1)
    assert all(not pulse.flags.writeable for pulse in explicit.probe_schedule)
    assert all(not pulse.flags.writeable for pulse in default.probe_schedule)


def test_environment_preserves_t0_and_first_uptake_but_not_first_returned_state():
    engine = synthetic_engine()
    wrapper = caa.ConservativeAccessEngine(engine)
    source = synthetic_state()
    source_hash = caa.state_sha256(source)
    schedule = probes()
    mask = interior_mask()
    held_plan = caa.compile_plan(source, mask, l_available=1, e_available=0, probe_schedule=schedule)
    open_plan = caa.compile_plan(source, mask, l_available=1, e_available=1, probe_schedule=schedule)
    assert caa.state_sha256(source) == source_hash

    common = caa.apply_common_probe(source, schedule[0])
    held = wrapper.step_with_diagnostics(common, held_plan)
    opened = wrapper.step_with_diagnostics(common, open_plan)
    assert np.array_equal(held.state.uptake, opened.state.uptake)
    differing = [
        field for field in caa.STATE_FIELDS
        if not np.array_equal(getattr(held.state, field), getattr(opened.state, field))
    ]
    assert set(differing).intersection({"U", "V", "Mf", "c", "N"})
    assert caa.state_sha256(common) == caa.state_sha256(caa.apply_common_probe(source, schedule[0]))


def test_uptake_divergence_appears_at_statically_frozen_H_star_two():
    engine = synthetic_engine()
    wrapper = caa.ConservativeAccessEngine(engine)
    source = synthetic_state()
    schedule = probes()
    mask = interior_mask()
    held_plan = caa.compile_plan(source, mask, l_available=1, e_available=0, probe_schedule=schedule)
    open_plan = caa.compile_plan(source, mask, l_available=1, e_available=1, probe_schedule=schedule)
    step0 = caa.apply_common_probe(source, schedule[0])
    held1 = wrapper.step(step0, held_plan)
    open1 = wrapper.step(step0, open_plan)
    assert np.array_equal(held1.uptake, open1.uptake)
    held2 = wrapper.step(caa.apply_common_probe(held1, schedule[1]), held_plan)
    open2 = wrapper.step(caa.apply_common_probe(open1, schedule[1]), open_plan)
    assert caa.H_STAR == 2
    assert np.any(held2.uptake[mask] != open2.uptake[mask])


def test_literal_N_probe_decomposition_exposes_preprobe_up_ref_probe_leak():
    engine = synthetic_engine()
    wrapper = caa.ConservativeAccessEngine(engine)
    source = synthetic_state()
    schedule = probes()
    mask = interior_mask()
    plan = caa.compile_plan(source, mask, l_available=1, e_available=0, probe_schedule=schedule)
    result = wrapper.step_with_diagnostics(caa.apply_common_probe(source, schedule[0]), plan)
    up = result.diagnostics["stage_ledger"]["up_ref"]
    denominator = up["n_A"] + up["n_B0"]
    expected = (up["S_A"] + up["S_B0"]) / denominator if denominator else 0.0
    assert up["selected"] == expected
    assert up["S_B_selected"] == up["S_B0"]
    assert up["n_B_selected"] == up["n_B0"]
    assert up["selected"] != up["frozen"], (
        "E0 freezes external previous-step uptake, so P-induced current external uptake is not common through up_ref"
    )
    nlog = result.diagnostics["stage_ledger"]["N"]
    assert nlog["probe_hash"] == caa._array_hash(schedule[0])
    assert nlog["reference_plus_probe_hash"] == caa._array_hash(source.N + schedule[0])
    assert not nlog["reservoir_gated"]


def test_external_only_probe_is_suppressed_from_E0_up_ref_global_channel():
    engine = synthetic_engine()
    wrapper = caa.ConservativeAccessEngine(engine)
    source = synthetic_state()
    mask = interior_mask()
    external_pulse = np.where(mask, 0.0, 0.08)
    zero = np.zeros_like(external_pulse)
    pulse_plan = caa.compile_plan(
        source, mask, l_available=1, e_available=0, probe_schedule=(external_pulse, zero)
    )
    zero_plan = caa.compile_plan(
        source, mask, l_available=1, e_available=0, probe_schedule=(zero, zero)
    )
    pulsed = wrapper.step_with_diagnostics(caa.apply_common_probe(source, external_pulse), pulse_plan)
    unpulsed = wrapper.step_with_diagnostics(source, zero_plan)
    pulsed_up = pulsed.diagnostics["stage_ledger"]["up_ref"]
    unpulsed_up = unpulsed.diagnostics["stage_ledger"]["up_ref"]
    assert pulsed_up["selected"] == unpulsed_up["selected"]
    assert pulsed_up["frozen"] != unpulsed_up["frozen"]


def test_dynamic_E_stage_coverage_is_exercised_through_H_star():
    engine = synthetic_engine()
    wrapper = caa.ConservativeAccessEngine(engine)
    source = synthetic_state()
    schedule = probes()
    plan = caa.compile_plan(source, periodic_mask(), l_available=1, e_available=0, probe_schedule=schedule)
    first = wrapper.step_with_diagnostics(caa.apply_common_probe(source, schedule[0]), plan)
    ledger1 = first.diagnostics["stage_ledger"]
    assert set(ledger1) == {"transport", "boundary_faces", "toggle", "up_ref", "writer", "c", "N"}
    assert first.diagnostics["target_boundary_face_count"] > 0
    assert any(abs(value) > 0.0 for value in ledger1["toggle"].values())
    assert any(abs(value) > 0.0 for value in ledger1["writer"]["Mf_target_delta"])
    assert abs(ledger1["N"]["target_gate_delta"]) > 0.0

    second_input = caa.apply_common_probe(first.state, schedule[1])
    second = wrapper.step_with_diagnostics(second_input, plan)
    assert any(abs(value) > 0.0 for value in second.diagnostics["stage_ledger"]["transport"].values())


def test_transport_boundary_work_is_exactly_accounted_but_nonzero_at_H_star():
    engine = synthetic_engine()
    wrapper = caa.ConservativeAccessEngine(engine)
    source = synthetic_state()
    schedule = probes()
    plan = caa.compile_plan(source, interior_mask(), l_available=1, e_available=0, probe_schedule=schedule)
    first = wrapper.step(caa.apply_common_probe(source, schedule[0]), plan)
    current = caa.apply_common_probe(first, schedule[1])
    active, ledger, faces = wrapper._transport(current.rho, current.U, current.V, current.c, current.C, current.Mf, plan, 0)
    opened, _, _ = wrapper._transport(current.rho, current.U, current.V, current.c, current.C, current.Mf, plan, 1)
    nonzero = []
    for field in caa.EXTENSIVE_FIELDS:
        direct = float((active[field] - opened[field]).sum(dtype=np.float64))
        tolerance = caa.operation_tolerance((active[field], opened[field]), additions=active[field].size * 2)
        assert abs(direct - ledger[field]) <= tolerance
        face_sum = 0.0
        for face in faces:
            delta = face["fields"][field]["delta"]
            face_sum += float(np.asarray(delta, dtype=np.float64).sum(dtype=np.float64))
        face_tolerance = caa.operation_tolerance((np.array([face_sum]), np.array([ledger[field]])), additions=max(1, len(faces)))
        assert abs(face_sum - ledger[field]) <= face_tolerance
        nonzero.append(abs(ledger[field]) > tolerance)
    assert any(nonzero), "the one-sided target-destination gate should expose nonzero boundary work"


def test_one_sided_environment_gate_breaks_paired_face_conservation_and_triggers_kill_switch():
    engine = synthetic_engine()
    wrapper = caa.ConservativeAccessEngine(engine)
    source = synthetic_state()
    schedule = probes()
    plan = caa.compile_plan(source, interior_mask(), l_available=1, e_available=0, probe_schedule=schedule)
    first = wrapper.step(caa.apply_common_probe(source, schedule[0]), plan)
    current = caa.apply_common_probe(first, schedule[1])
    active, ledger, faces = wrapper._transport(current.rho, current.U, current.V, current.c, current.C, current.Mf, plan, 0)
    opened, _, _ = wrapper._transport(current.rho, current.U, current.V, current.c, current.C, current.Mf, plan, 1)
    # Non-target destination increments are frozen, so any nonzero global
    # selected-minus-open sum is an unpaired one-sided boundary intervention.
    for field in caa.EXTENSIVE_FIELDS:
        values = active[field] - opened[field]
        mask = plan.target_mask if values.ndim == 2 else plan.target_mask[None, ...]
        assert np.array_equal(values[~np.broadcast_to(mask, values.shape)], np.zeros_like(values)[~np.broadcast_to(mask, values.shape)])
    assert any(value != 0.0 for value in ledger.values())
    assert faces
    assert all(set(face) == {"axis", "orientation", "target", "outside_neighbour", "fields"} for face in faces)


def test_state_schema_has_no_reporter_and_inputs_are_never_overwritten():
    engine = synthetic_engine()
    wrapper = caa.ConservativeAccessEngine(engine)
    source = synthetic_state()
    schedule = probes()
    plan = caa.compile_plan(source, interior_mask(), l_available=0, e_available=0, probe_schedule=schedule)
    common = caa.apply_common_probe(source, schedule[0])
    before = caa.state_sha256(common)
    result = wrapper.step_with_diagnostics(common, plan)
    assert caa.state_sha256(common) == before
    assert result.diagnostics["input_state_preserved"]
    assert not result.diagnostics["new_reporter_in_state"]
    assert result.diagnostics["state_schema"] == list(caa.STATE_FIELDS) + ["step"]
    assert set(vars(result.state)) == set(caa.STATE_FIELDS) | {"step"}


def test_operation_tolerance_depends_only_on_terms_and_operation_count():
    terms = (np.array([1.0, -2.0, 3.0]), np.array([4.0, -5.0]))
    bound = caa.operation_tolerance(terms, additions=10)
    expected = (10 * np.finfo(np.float64).eps) / (1.0 - 10 * np.finfo(np.float64).eps) * 15.0
    assert bound == expected
