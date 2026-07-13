"""Every architecture admitted to the benchmark must be VIABLE, NON-OVERLAPPING, and have a causal graph on
which two INDEPENDENT paths (geometry and intervention) agree. D-053/D-054."""

from __future__ import annotations

import numpy as np
import pytest

from edlab.substrates.life.library import (
    arch_base, arch_delay, arch_xinhib, arch_5chan, arch_inert, arch_decoy, arch_direct, arch_redundant,
    assert_viable, assert_graph_agrees, assert_no_overlap, measured_graph, predict_active,
    settle, run_from, total_output, Arch, Comp, se_diag, MIN_GUN_SPACING, PERIOD, SETTLE)

ALL = {
    "BASE": arch_base(),
    "TRANSLATE": arch_base(cols=[15, 55, 95, 135], arch_id="TRANSLATE"),
    "SPACING45": arch_base(cols=[5, 50, 95, 140], arch_id="SPACING45"),
    "INERT": arch_inert(),
    "DECOY": arch_decoy(),
    "GATE3": arch_base(program=(1, 1, 1, 0), arch_id="GATE3"),
    "DELAY1": arch_delay(1), "DELAY2": arch_delay(2), "DELAY4": arch_delay(4), "DELAY8": arch_delay(8),
    "XINHIB": arch_xinhib(), "FIVE": arch_5chan(),
    "DIRECT": arch_direct(), "REDUNDANT": arch_redundant(),
}


@pytest.mark.parametrize("name", sorted(ALL))
def test_every_architecture_is_admissible(name):
    """Viable (periodic AND actually computing), no overlapping component boxes, and the geometric prediction
    agrees edge-for-edge with the interventional measurement."""
    a = ALL[name]
    assert_viable(a)
    assert_graph_agrees(a)


def test_settle_400_was_NOT_settled():
    """EXP-GT-02/02B settled for 400 steps and called it 'a common established state'. It is not: the circuit
    is still transient at t=400 and only becomes exactly periodic (period 60) from ~700. Disclosed in D-054."""
    a = arch_base()
    g = a.grid()
    from edlab.substrates.life.fast import step
    for _ in range(400):
        g = step(g)
    g400 = g.copy()
    for _ in range(PERIOD):
        g = step(g)
    assert not np.array_equal(g, g400), "if this passes, t=400 IS periodic and the disclosure is wrong"
    assert SETTLE >= 700 and SETTLE % PERIOD == 0


def test_same_function_different_mechanism_is_bit_identical():
    """The crown case: a channel closed by a MEMORY GATE and a channel closed by a CROSS-STREAM INHIBITOR
    produce a frame-for-frame IDENTICAL output series. F cannot separate them; only A can."""
    o1 = total_output(run_from(settle(ALL["GATE3"]), 600))
    o2 = total_output(run_from(settle(ALL["XINHIB"]), 600))
    assert np.array_equal(o1, o2)
    e1 = {"->".join(e) for e in measured_graph(ALL["GATE3"])["edges"]}
    e2 = {"->".join(e) for e in measured_graph(ALL["XINHIB"])["edges"]}
    assert e1 != e2, "same F must come from DIFFERENT causal graphs, or the case is vacuous"


def test_inert_and_decoy_parts_are_causally_silent():
    """A causally inert part must leave the output BIT-IDENTICAL despite changing the cell count.
    DECOY has gate-like eaters (same density as a real gate) placed off-track: the appearance trap."""
    ob = total_output(run_from(settle(ALL["BASE"]), 600))
    for k in ("INERT", "DECOY"):
        assert np.array_equal(ob, total_output(run_from(settle(ALL[k]), 600)))
        assert ALL[k].geometric_signature()["n_cells"] > 144      # it really did add matter


def test_delay_edit_is_exactly_4k_with_topology_and_track_fixed():
    """A gun moved by (k,k) keeps its diagonal (same output column) and arrives exactly 4k steps earlier."""
    base = measured_graph(ALL["BASE"])["delays"]["gun3->out[133]"]
    for k, arch in ((1, ALL["DELAY1"]), (2, ALL["DELAY2"]), (4, ALL["DELAY4"]), (8, ALL["DELAY8"])):
        d = measured_graph(arch)["delays"]["gun3->out[133]"]
        assert d == base - 4 * k, f"k={k}: expected {base - 4*k}, measured {d}"


def test_emergent_shielding_edge_exists_and_is_not_declared_by_naive_wiring():
    """XINHIB's SW stream is CONSUMED by channel 3. Ablate gun3 and the freed stream travels on and kills
    channel 2. gun3 -> out[93] is a REAL edge that a naive declared graph would miss."""
    e = {"->".join(x) for x in measured_graph(ALL["XINHIB"])["edges"]}
    assert "gunSW->out[133]" in e
    assert "gun3->out[93]" in e


def test_overlap_assertion_fires():
    """A criterion that cannot fire is not a criterion. An SW gun at col 150 overlaps gun3 (cols 125-160)."""
    bad = arch_base()
    bad.components = bad.components + [Comp("sw_gun", 5, 150, "gunSW")]
    with pytest.raises(AssertionError, match="OVERLAP"):
        assert_no_overlap(bad)
    assert_no_overlap(ALL["XINHIB"])                              # ... and passes on the fixed one


def test_viability_assertion_fires_on_a_dead_circuit():
    """Shifting an INTERIOR channel's gun right closes the 4-column gap to its neighbour and the guns
    annihilate. A dead grid is still 'periodic', so periodicity alone would have let it through."""
    with pytest.raises(AssertionError):
        assert_viable(arch_delay(3, chan=2))
