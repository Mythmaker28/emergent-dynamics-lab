"""Invariants of the continuous substrate and the continuous fingerprint.

These are the claims the experiment rests on. If one of them breaks, a result computed on top of it is not a
result, and the test suite should say so before a report does.
"""
import numpy as np
import pytest

from edlab.identity import cfingerprint as F
from edlab.substrates.ctrans import engine as E, evaluator as V, manifests as M


def channel(spec):
    def measure(probes, T, seeds):
        ok = np.array([p.target not in spec.blocked for p in probes])
        u = np.full((len(probes), T), np.nan)
        idx = [i for i, o in enumerate(ok) if o]
        if idx:
            sub = E.simulate(spec, [probes[i] for i in idx], T, np.asarray(seeds)[idx])["u"]
            for j, i in enumerate(idx):
                u[i] = sub[j]
        return u, ok
    return measure


@pytest.fixture(scope="module")
def dev():
    return M.dev_systems()


def test_the_two_naive_mappings_both_fail(dev):
    """D-073, reproduced. Neither is a measurement."""
    p = [E.Probe("p", E.DRIVE, "step", 1.8, 24, 128)]
    u1 = E.observe(dev["D_leak"], p, 304, [1])
    u2 = E.observe(dev["D_leak"], p, 304, [2])
    assert np.unique(u1.astype(np.uint8)).tolist() == [0]        # universal false SAMENESS
    assert (u1 != u2).all()                                      # universal false DIFFERENCE, vs ITSELF


def test_solver_refinement_is_a_nuisance_and_it_is_measured(dev):
    """The number that licenses the claim, rather than the claim on its own."""
    for nm in ("D_leak", "D_fb", "D_sat", "D_cascade", "D_mem_p"):
        assert V.solver_convergence(dev[nm]) < V.TOL_REL


def test_false_sameness_is_bit_for_bit_under_the_limited_repertoire(dev):
    """The uncontrollable mode is EXACTLY invisible externally, and EXACTLY visible internally."""
    assert np.abs(V._traces(dev["D_leak"], "limited", 7) - V._traces(dev["D_hidden"], "limited", 7)).max() == 0.0
    assert np.abs(V._traces(dev["D_leak"], "rich", 7) - V._traces(dev["D_hidden"], "rich", 7)).max() > 1e-6


def test_L4_collapse_is_exact_by_construction(dev):
    """Under DRIVE-ONLY probing, supply_cause is identical to leak. Only the supply probes separate them."""
    p = [E.Probe("b", -1, "none", 0, 0, 10 ** 9)] + \
        [E.Probe("d%d" % i, E.DRIVE, "step", a, 24, 128) for i, a in enumerate((0.35, 1.8, -1.8))]
    yl = E.observe_noise_free(dev["D_leak"], p, 304)
    ys = E.observe_noise_free(dev["D_supply"], p, 304)
    assert np.abs((yl[1:] - yl[0]) - (ys[1:] - ys[0])).max() < 1e-15


def test_unit_invariance_is_exact_not_approximate(dev):
    """u -> a*u + b must not move the standardized fingerprint AT ALL. b cancels; a cancels against sigma_hat."""
    a = F.acquire(channel(dev["D_leak"]), "limited", 4242)
    b = F.acquire(channel(dev["D_leak_units"]), "limited", 4242)      # same seeds, affine readout
    rel = np.nanmax(np.abs(a["Z"] - b["Z"])) / np.nanmax(np.abs(a["Z"]))
    assert rel <= 1e-9


def test_gain_survives_the_normalization_that_kills_units(dev):
    """The whole design. Units vanish; gain does not."""
    a = F.acquire(channel(dev["D_leak"]), "limited", 111)
    g = F.acquire(channel(dev["D_leak_gain2"]), "limited", 222)
    n = F.acquire(channel(dev["D_leak"]), "limited", 333)
    assert F.distance(a, n) < 8.0                # null
    assert F.distance(a, g) > 24.0               # a doubled gain is not a change of units


def test_a_silent_system_is_never_matched_to_another_silent_system(dev):
    """Two all-zero fingerprints agree perfectly and mean nothing. Silence is not a fingerprint."""
    a = F.acquire(channel(dev["D_silent_dead"]), "limited", 11)
    b = F.acquire(channel(dev["D_silent_sat"]), "limited", 22)
    assert a["responsive"] == 0.0 and b["responsive"] == 0.0
    r = F.compare(a, b, 7.786, 23.357)
    assert r["verdict"] == F.INDETERMINATE


def test_mismatched_batteries_are_refused_not_intersected(dev):
    """Comparing on the intersection is an adaptive battery wearing a fixed battery's coat."""
    a = F.acquire(channel(dev["D_leak"]), "limited", 11)
    b = F.acquire(channel(dev["D_lowcov"]), "limited", 22)
    assert not F.admit(a, b, True)["ok"]


def test_the_common_channel_refusal_is_load_bearing(dev):
    """L8. Disable it and the same system on a noisier channel is confidently called DIFFERENT."""
    a = F.acquire(channel(dev["D_leak"]), "limited", 11)
    b = F.acquire(channel(dev["D_leak_loud"]), "limited", 22)
    assert F.compare(a, b, 7.786, 23.357, common_channel=False)["verdict"] == F.INDETERMINATE
    assert F.compare(a, b, 7.786, 23.357, common_channel=False,
                     enforce_channel=False)["verdict"] == F.DIFFERENT


def test_memory_is_a_transient_probe_leaving_a_permanent_mark(dev):
    """And the carrier alone never flips it."""
    p = [E.Probe("b", -1, "none", 0, 0, 10 ** 9), E.Probe("s", E.DRIVE, "step", -1.8, 24, 128)]
    y = E.observe_noise_free(dev["D_mem_p"], p, 304)
    r = y[1] - y[0]
    assert abs(r[270:300].mean()) > 0.05 * np.abs(r[128:288]).max()      # permanent
    # The carrier makes the OUTPUT oscillate, so the output is the wrong thing to look at. Look at the bistable
    # SITE itself (privileged): the carrier must never carry it across the separatrix at x = 0.
    hist = E.simulate(dev["D_mem_p"], [p[0]], 304, [0])["hist"]
    assert (hist[:, 0, 4] > 0.5).all()                                   # the well is never left


def test_privileged_path_does_not_import_the_instrument():
    """Structural. The second path to truth cannot be a copy of the first."""
    src = open("edlab/substrates/ctrans/evaluator.py").read()
    imports = [l for l in src.splitlines() if l.startswith(("import ", "from "))]
    assert not any("cfingerprint" in l or "identity" in l for l in imports), imports
