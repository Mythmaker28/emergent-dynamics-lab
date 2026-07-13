"""Locks for the blind A head and its resolution certificate (D-055). The head sees ONLY raw frames, its own
interventions, and the declared output line -- never a label, a position, a program bit or a hidden edge."""

from __future__ import annotations

import numpy as np
import pytest

from edlab.substrates.life.library import (arch_base, arch_delay, arch_xinhib, arch_5chan, arch_inert,
                                           arch_decoy, arch_direct, arch_redundant, settle, OUT_ROW,
                                           measured_graph, total_output, run_from, BASE_COLS)
from edlab.identity.blind_a import blind_tomography, head_A, head_G, PHASES, MERGE_GAP

TOL = 0          # CERTIFIED from the development null (EXP-GT-A-CERT): zero deviation across all 8 nulls


def T(a, phase=0, region=None):
    return blind_tomography(settle(a, extra_phase=phase), OUT_ROW, region=region)


def _blind_edges(t):
    return sorted((e["src"], e["dst"], e["kind"], e["delay"]) for e in t["edges"])


def test_blind_head_recovers_the_hidden_graph_of_the_base_circuit():
    t = T(arch_base())
    assert t["n_components"] == 4 and t["n_out"] == 4
    assert _blind_edges(t) == [(i, i, "PERSISTENT_DOWN", 214) for i in range(4)]


def test_blind_head_finds_the_EMERGENT_shielding_edge_nobody_declared():
    """XINHIB's SW stream is consumed by channel 3, shielding channel 2. Ablate gun3 and the freed stream kills
    channel 2. The blind head must find gun3 -> out2, an edge the naive wiring diagram does not contain."""
    t = T(arch_xinhib())
    e = {(x[0], x[1], x[2]) for x in _blind_edges(t)}
    assert (3, 2, "PERSISTENT_DOWN") in e, f"emergent shielding edge missing: {e}"   # gun3 shields channel 2
    assert (4, 3, "PERSISTENT_UP") in e, f"inhibitor edge missing: {e}"               # the SW gun inhibits ch3
    assert (3, 3, "PERSISTENT_DOWN") not in e, "channel 3 is inhibited; its own gun cannot drive its output"
    truth = {"->".join(x) for x in measured_graph(arch_xinhib())["edges"]}
    assert "gun3->out[93]" in truth and "gunSW->out[133]" in truth      # the head agrees with the evaluator


def test_A_is_invariant_to_phase_translation_spacing_decoration_and_decoys():
    """The measured NOISE FLOOR. Every one of these changes the picture and none changes the graph."""
    base = T(arch_base())
    for ph in PHASES:
        assert head_A(base, T(arch_base(), phase=ph), TOL) == "SAME"
    for cols in ([c + 10 for c in BASE_COLS], [c + 20 for c in BASE_COLS], [5, 50, 95, 140]):
        assert head_A(base, T(arch_base(cols=cols, arch_id="X")), TOL) == "SAME"
    assert head_A(base, T(arch_inert()), TOL) == "SAME"
    assert head_A(base, T(arch_decoy()), TOL) == "SAME"


def test_G_moves_on_layout_where_A_does_not_and_is_never_composited():
    base, sp45 = T(arch_base()), T(arch_base(cols=[5, 50, 95, 140], arch_id="SP45"))
    assert head_A(base, sp45, TOL) == "SAME"          # D-053: this is the case the old benchmark mislabelled
    assert head_G(base, sp45) == "DIFFERENT"          # the layout difference is REAL -- and it lives in G
    assert head_G(base, T(arch_base(cols=[c + 10 for c in BASE_COLS], arch_id="T"))) == "SAME"   # translation


@pytest.mark.parametrize("k,steps", [(1, 4), (2, 8), (4, 16), (8, 32)])
def test_A_resolves_the_finest_delay_edit_the_substrate_admits(k, steps):
    """CERTIFIED RESOLUTION: 4 steps. The null tolerance is 0 because the delay estimator is phase-invariant
    (earliest onset over a full cycle of strike phases). A naive first-change estimator swung by 15 steps."""
    assert head_A(T(arch_base()), T(arch_delay(k)), TOL) == "DIFFERENT"


def test_A_detects_one_added_edge_one_added_node_and_a_redundancy_change():
    base = T(arch_base())
    assert head_A(base, T(arch_xinhib()), TOL) == "DIFFERENT"        # +1 edge
    assert head_A(base, T(arch_5chan()), TOL) == "DIFFERENT"         # +1 node
    assert head_A(T(arch_direct()), T(arch_redundant()), TOL) == "DIFFERENT"   # 1-path vs 2-path


def test_the_crown_case_same_function_different_mechanism():
    """GATE3 and XINHIB emit a BIT-IDENTICAL output series. F cannot separate them. A must."""
    g3, xi = arch_base(program=(1, 1, 1, 0), arch_id="GATE3"), arch_xinhib()
    assert np.array_equal(total_output(run_from(settle(g3), 600)), total_output(run_from(settle(xi), 600)))
    assert head_A(T(g3), T(xi), TOL) == "DIFFERENT"


def test_INDETERMINATE_fires_when_coverage_is_insufficient():
    """A criterion that cannot abstain cannot be trusted when it doesn't. Starve the probe of coverage and A
    must say it does not know -- not SAME."""
    starved = T(arch_base(), region=(0, 20, 0, 100))
    assert starved["uncovered_outputs"], "the starvation must actually starve something"
    assert head_A(T(arch_base()), starved, TOL) == "INDETERMINATE"


def test_all_three_verdicts_can_fire():
    base = T(arch_base())
    assert head_A(base, T(arch_inert()), TOL) == "SAME"
    assert head_A(base, T(arch_5chan()), TOL) == "DIFFERENT"
    assert head_A(base, T(arch_base(), region=(0, 20, 0, 100)), TOL) == "INDETERMINATE"


def test_program_invariance_is_NOT_certifiable_here_and_the_test_says_so():
    """D-055. In this family a memory bit of 0 is implemented by ADDING an eater: the program IS the
    architecture. So A *correctly* reports DIFFERENT, and 'A ignores the program' CANNOT be tested here.
    This test exists to make the vacuity explicit and to fail loudly if someone later 'fixes' it by
    weakening A."""
    a = head_A(T(arch_base(program=(1, 1, 1, 1))), T(arch_base(program=(1, 1, 1, 0), arch_id="G3")), TOL)
    assert a == "DIFFERENT", ("If this ever returns SAME, A has been blinded to a genuine node+edge change. "
                              "Program-invariance must be certified on a substrate with STATE-based memory, "
                              "not by making A stop seeing structure.")
