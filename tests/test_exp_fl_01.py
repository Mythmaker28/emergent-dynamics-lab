"""EXP_FL_01 minimal validation: deterministic blind sampler + screen record shape."""

from __future__ import annotations

from edlab.experiments.exp_fl_01 import EXPFL01Config, flow_lenia_law_from_halton, screen_one


def test_sampler_deterministic_and_in_range():
    a = flow_lenia_law_from_halton(7); b = flow_lenia_law_from_halton(7)
    assert a == b
    assert 0.35 <= a.kernel_mu <= 0.65 and 0.08 <= a.growth_mu <= 0.26 and 0.20 <= a.dt <= 0.50


def test_screen_one_runs_and_reports_separate_P_and_M():
    r = screen_one(EXPFL01Config(steps=120), 0, 8001)
    assert "mean_P" in r and "mean_M" in r and "probe_count" in r and "eligible_seed" in r
    assert r["n_tracks"] >= 0
