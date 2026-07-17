"""Tests for the ACCESS-STRUCTURE-00 Phase 0.6B no-transplant primitives.

Fast: one shallow post-history world fixture (``to_S0``); short horizons.  These
lock the properties the design relies on: byte-identity when disabled, BIT-EXACT
core isolation under a width-2 clamp, spatially clean in-place memory
standardization, and the DEV-seed guard.  They never compute a feeding contrast.
"""
from __future__ import annotations

import numpy as np
import pytest

from edlab.experiments.sc_mcm import config as MCM_CONFIG
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine
from experiments.individuation import turnover_dev_diagnostics as tdd
from experiments.individuation import access_structure_noswap_operators as ns


@pytest.fixture(scope="module")
def world():
    base = tdd.to_S0(50002)
    S = base["S0"]
    cents = base["cents"]
    return {"S": S, "center": cents[0], "mem": tdd.MEM}


def _engine(driver=None, up_ref_zero=False):
    return ns.NoSwapClampEngine(MCM_CONFIG.SPEC, tdd.MEM, MCM_CONFIG.TRACER,
                                driver=driver, up_ref_zero=up_ref_zero)


def test_require_dev_seed():
    for s in ns.DEV_SEEDS:
        assert ns.require_dev_seed(s) == s
    for bad in (54001, 33000, 49999, 50011, 0):
        with pytest.raises(ValueError):
            ns.require_dev_seed(bad)


def test_byte_identity_when_disabled(world):
    """driver=None and both flags False => bit-identical to the frozen base engine."""
    base_eng = MultiChannelMemoryEngine(MCM_CONFIG.SPEC, tdd.MEM, MCM_CONFIG.TRACER)
    ns_eng = _engine(driver=None)
    a = world["S"].copy(); b = world["S"].copy()
    for _ in range(25):
        a = base_eng.step(a); b = ns_eng.step(b)
    err = max(float(np.max(np.abs(getattr(a, f) - getattr(b, f)))) for f in ns.STATE_FIELDS)
    assert err == 0.0


def test_clamp_is_applied_and_overwrites_ring(world):
    """The driver must actually overwrite the barrier ring (not silently no-op)."""
    S = world["S"]
    part, core, barrier = ns.core_and_collar(S.rho.shape, world["center"])
    frames = [{f: (np.full(int(barrier.sum()), 7.0) if getattr(S, f).ndim == 2
                   else np.full((getattr(S, f).shape[0], int(barrier.sum())), 7.0))
               for f in ns.STATE_FIELDS}]
    drv = ns.BoundaryDriver(ring=barrier, frames=frames)
    eng = _engine(driver=drv)
    out = eng.step(S.copy())
    assert np.allclose(out.rho[barrier], 7.0)
    assert np.allclose(out.c[barrier], 7.0)


def test_exact_isolation_width2(world):
    """Perturbing the far environment must leave the core BIT-IDENTICAL under a
    width-2 clamp with the global channel ablated (up_ref_zero)."""
    S = world["S"]
    part, core, barrier = ns.core_and_collar(S.rho.shape, world["center"])  # width 2
    horizon = 12
    drv = ns.record_boundary(S, _engine(up_ref_zero=True), barrier, horizon, shift=(0, 0))
    e1 = _engine(driver=ns.BoundaryDriver(drv.ring, drv.frames), up_ref_zero=True)
    e2 = _engine(driver=ns.BoundaryDriver(drv.ring, drv.frames), up_ref_zero=True)
    outside = part.distance > (ns.CORE_RADIUS + ns.BARRIER_WIDTH + 1)
    s1 = S.copy(); s2 = S.copy()
    s2.c[outside] += 0.1; s2.N[outside] += 0.1
    for _ in range(horizon):
        s1 = e1.step(s1); s2 = e2.step(s2)
    core_diff = max(float(np.max(np.abs(getattr(s1, f)[..., core] - getattr(s2, f)[..., core])))
                    for f in ns.STATE_FIELDS)
    env_diff = float(np.max(np.abs(s1.c[outside] - s2.c[outside])))
    assert env_diff > 0.0          # the environment really was perturbed
    assert core_diff == 0.0        # yet the core is bit-identical


def test_width1_barrier_leaks_but_width2_exact(world):
    """Documents WHY the barrier is two cells: a one-cell overwrite leaks at machine
    epsilon once a front arrives; two cells is exact."""
    S = world["S"]
    horizon = 12
    results = {}
    for bw in (1, 2):
        part, core, barrier = ns.core_and_collar(S.rho.shape, world["center"], barrier_width=bw)
        drv = ns.record_boundary(S, _engine(up_ref_zero=True), barrier, horizon, shift=(0, 0))
        e1 = _engine(driver=ns.BoundaryDriver(drv.ring, drv.frames), up_ref_zero=True)
        e2 = _engine(driver=ns.BoundaryDriver(drv.ring, drv.frames), up_ref_zero=True)
        outside = part.distance > (ns.CORE_RADIUS + bw + 1)
        s1 = S.copy(); s2 = S.copy(); s2.c[outside] += 0.1
        for _ in range(horizon):
            s1 = e1.step(s1); s2 = e2.step(s2)
        results[bw] = max(float(np.max(np.abs(getattr(s1, f)[..., core] - getattr(s2, f)[..., core])))
                          for f in ns.STATE_FIELDS)
    assert results[2] == 0.0
    assert results[2] <= results[1]


def test_standardize_core_memory_is_spatially_clean(world):
    """In-place memory standardization changes ONLY Mf, and ONLY on the core."""
    S = world["S"]
    part, core, barrier = ns.core_and_collar(S.rho.shape, world["center"])
    ref = S.copy()
    ref.Mf = ref.Mf + 0.3               # a distinct reference memory field
    out = ns.standardize_core_memory(S, core, ref, shift=(0, 0))
    # non-memory fields unchanged everywhere
    for f in ("rho", "U", "V", "c", "N", "C", "uptake"):
        assert np.array_equal(getattr(out, f), getattr(S, f))
    # Mf unchanged OUTSIDE the core
    assert np.array_equal(out.Mf[:, ~core], S.Mf[:, ~core])
    # Mf equals the reference ON the core
    assert np.allclose(out.Mf[:, core], ref.Mf[:, core])


def test_erase_core_memory_zeroes_core_only(world):
    S = world["S"]
    part, core, barrier = ns.core_and_collar(S.rho.shape, world["center"])
    out = ns.erase_core_memory(S, core)
    assert np.allclose(out.Mf[:, core], 0.0)
    assert np.array_equal(out.Mf[:, ~core], S.Mf[:, ~core])
    assert np.array_equal(out.rho, S.rho)


def test_record_boundary_frame_count_and_shape(world):
    S = world["S"]
    part, core, barrier = ns.core_and_collar(S.rho.shape, world["center"])
    drv = ns.record_boundary(S, _engine(), barrier, 8, shift=(0, 0))
    assert len(drv.frames) == 8
    n_ring = int(barrier.sum())
    assert drv.frames[0]["rho"].shape == (n_ring,)
    assert drv.frames[0]["Mf"].shape == (2, n_ring)


def test_comoving_halo_inside_core(world):
    """The perturbation-decay halo is a small interaction length, well inside the
    radius-10 core (feeding-blind H_HALO definition)."""
    eng = MultiChannelMemoryEngine(MCM_CONFIG.SPEC, tdd.MEM, MCM_CONFIG.TRACER)
    halo = ns.measure_causal_horizon(world["S"], eng, world["center"], nsteps=20)
    assert 0 < halo["influence_decay_halo_radius"] <= ns.CORE_RADIUS
    assert "static_footprint" in halo


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
