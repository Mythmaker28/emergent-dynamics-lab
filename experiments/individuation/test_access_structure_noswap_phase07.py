"""Tests for the ACCESS-STRUCTURE-00 Phase 0.7 CORE-SUFFICIENCY pilot primitives.

Fast: uses one shallow post-history state fixture. Locks the M interventions'
spatial cleanliness and the probe-aligned reference recorder's shape. Does not
run the full factorial (covered by a determinism check in the run journal).
"""
from __future__ import annotations

import numpy as np
import pytest

from edlab.experiments.sc_mcm import config as MCM_CONFIG
from experiments.individuation import turnover_dev_diagnostics as tdd
from experiments.individuation import access_structure_noswap_operators as ns
from experiments.individuation import access_structure_noswap_phase07_pilot as p07


@pytest.fixture(scope="module")
def fx():
    base = tdd.to_S0(50002)
    S = base["S0"]
    cents = base["cents"]
    center = cents[0]
    part, core, barrier = ns.core_and_collar(S.rho.shape, center)
    twin = S.copy()
    twin.Mf = twin.Mf * 0.5 + 0.1     # a distinct, nonzero "twin" memory field
    return {"S": S, "twin": twin, "core": core, "barrier": barrier, "center": center}


def test_m_std_changes_only_core_Mf(fx):
    S, twin, core = fx["S"], fx["twin"], fx["core"]
    out = p07.m_std_intensive(S, core, twin, shift=(0, 0))
    # only Mf changes
    for f in ("rho", "U", "V", "c", "N", "C", "uptake"):
        assert np.array_equal(getattr(out, f), getattr(S, f))
    # Mf unchanged outside the core
    assert np.array_equal(out.Mf[:, ~core], S.Mf[:, ~core])
    # body/rho preserved exactly
    assert np.array_equal(out.rho, S.rho)


def test_m_std_intensive_matches_twin_intensive_on_core(fx):
    """With shift 0, the standardized intensive memory on the core equals the twin's."""
    S, twin, core = fx["S"], fx["twin"], fx["core"]
    out = p07.m_std_intensive(S, core, twin, shift=(0, 0))
    eps = 1e-12
    m_out = out.Mf / np.maximum(out.rho, eps)[None]
    m_twin = twin.Mf / np.maximum(twin.rho, eps)[None]
    # where the target body exists, intensive memory should match the twin's
    body = S.rho > 0.30
    sel = body & core
    assert np.allclose(m_out[:, sel], m_twin[:, sel], atol=1e-9)


def test_m_erase_zeroes_core_only(fx):
    S, core = fx["S"], fx["core"]
    out = p07.m_erase(S, core)
    assert np.allclose(out.Mf[:, core], 0.0)
    assert np.array_equal(out.Mf[:, ~core], S.Mf[:, ~core])
    assert np.array_equal(out.rho, S.rho)


def test_reference_recorder_frame_count(fx):
    S, twin, barrier = fx["S"], fx["twin"], fx["barrier"]
    drv = p07.record_reference_barrier(twin, barrier, (0, 0), p07.MEM, up_ref_zero=False)
    assert len(drv.frames) == p07.SETTLE_STD + p07.HORIZON     # 80
    n_ring = int(barrier.sum())
    assert drv.frames[0]["rho"].shape == (n_ring,)
    assert drv.frames[0]["Mf"].shape == (2, n_ring)


def test_Y_returns_valid_structure(fx):
    S = fx["S"]
    base = tdd.to_S0(50002)
    cents = base["cents"]
    eng = p07.coupled_engine(p07.MEM, up_ref_zero=False)
    y = p07.Y(S, cents, eng, 0)
    assert set(("tracked", "fixed", "branch_valid", "status", "max_cov")).issubset(y)
    assert np.isfinite(y["tracked"])


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
