"""Regression locks for D-053 (EXP-GT-A0). These encode findings that must never silently regress."""

from __future__ import annotations

import pytest

from edlab.substrates.life.fast import assert_equivalent_to_reference
from edlab.experiments.exp_gt_00 import ARCH_TRAIN, ARCH_HELD_OUT
from edlab.experiments.exp_gt_a0 import (declared_structural_graph, verified_active_graph, isomorphic,
                                         layout_viable, head_G, geometric_signature)
from edlab.substrates.life.circuits import build
from edlab.experiments.exp_gt_00 import EATER_OFF

SP40 = ARCH_TRAIN[0]           # (5,45,85,125)
SP45 = ARCH_HELD_OUT[0]        # (5,50,95,140)
SP36 = ARCH_HELD_OUT[1]        # (10,46,82,118)  -- VOID, dead circuit


def _mk(arch, prog):
    return build(list(arch), list(prog), eater_offsets={i: EATER_OFF for i in range(len(prog))})


def test_fast_step_is_bit_exact_with_reference():
    assert assert_equivalent_to_reference() > 0


@pytest.mark.parametrize("prog", [(1, 0, 1, 0), (0, 1, 0, 1), (1, 1, 1, 1)])
def test_sp40_and_sp45_are_THE_SAME_causal_architecture(prog):
    """D-053. The pair the benchmark labelled 'different ARCHITECTURE' is graph-identical.
    If this ever fails, the ontology has drifted -- not the observer."""
    g40 = declared_structural_graph(SP40, prog)
    g45 = declared_structural_graph(SP45, prog)
    assert g40["edges"] == g45["edges"], "declared edge sets must be LITERALLY identical (edges use ordinals)"
    assert isomorphic(g40, g45)


@pytest.mark.parametrize("prog", [(1, 0, 1, 0), (1, 1, 1, 1)])
def test_verified_active_graphs_and_delays_match_across_layouts(prog):
    """The MEASURED graph agrees with the declared one: same topology, same causal delays."""
    v40 = verified_active_graph(_mk(SP40, prog))
    v45 = verified_active_graph(_mk(SP45, prog))
    assert isomorphic(v40, v45)
    assert sorted(v40["delays"].values()) == sorted(v45["delays"].values())
    assert not [e for e in v40["edges"]                       # no cross-channel coupling in this family
                if "".join(c for c in e[0] if c.isdigit()) != "".join(c for c in e[1] if c.isdigit())]


def test_G_separates_layout_without_touching_A():
    """G is the ONLY head allowed to fire on a pure spacing change. It is never composited into identity."""
    assert head_G(SP40, SP45) == "DIFFERENT"
    assert head_G(SP40, SP40) == "SAME"
    shifted = tuple(c + 7 for c in SP40)                      # pure translation
    assert head_G(SP40, shifted) == "SAME", "G must be translation-invariant"
    assert geometric_signature(SP40)["spacings"] == [40, 40, 40]


def test_ARCH_HELD_OUT_1_is_a_dead_circuit_and_stays_quarantined():
    """D-053. (10,46,82,118) produces ZERO output on all four channels: the gun spans 36 columns, so at
    spacing 36 adjacent guns touch and annihilate. It shipped as a 'held-out architecture' since EXP-GT-00."""
    ok, means = layout_viable(SP36)
    assert not ok
    assert all(m == 0.0 for m in means), f"expected a dead circuit, got {means}"


def test_viability_assertion_fires_and_passes_on_the_right_layouts():
    """A criterion that cannot BOTH fire and fail is not a criterion (project norm)."""
    assert layout_viable(SP40)[0] is True                     # must PASS on a live circuit
    assert layout_viable(SP45)[0] is True
    assert layout_viable(SP36)[0] is False                    # must FIRE on a dead one
    assert layout_viable((10, 46, 82, 118))[0] is False
    assert layout_viable((10, 48, 86, 124))[0] is True        # spacing 38 = the measured minimum viable
