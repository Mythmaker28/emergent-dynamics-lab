"""EXP-GT-00 circuit hierarchy: glider/channel -> inhibit gate -> memory bit -> tiny FSM.

GROUND TRUTH (evaluator only, NEVER shown to the discovery observer):
  component locations, causal graph, memory contents (the program word), inputs, outputs, program identity.
The DISCOVERY OBSERVER receives ONLY the raw cell-state trajectory.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .engine import blank, place, run, GLIDER_SE, EATER1, GOSPER_GUN

H, W = 120, 300
GUN_ROW = 5
OUT_ROW = 70                      # the output line the FUNCTION is read from
EATER_ROW = 35                    # memory bits sit on this row of each channel
STEPS = 700                       # gliders move at c/4: ONE cell per FOUR steps. Reaching row 70 from row ~13
READ_FROM = 420                   # takes 4*57 = 228 steps, plus emission phase -> read only after the transient.


@dataclass
class Circuit:
    grid: np.ndarray
    # ---- GROUND TRUTH (hidden from the observer) ----
    gun_cols: tuple                       # ARCHITECTURE (layout)
    program: tuple                        # MEMORY: bit i = 1 -> channel open; 0 -> eater absorbs (inhibit gate)
    eater_sites: tuple = ()               # component locations
    causal_graph: tuple = ()              # (gun_i -> eater_i -> output_i) edges that exist
    arch_id: str = ""
    program_id: str = ""
    meta: dict = field(default_factory=dict)

    @property
    def identity(self) -> str:
        return f"{self.arch_id}|{self.program_id}"


def _glider_track_col(gun_col: int, row: int) -> int:
    """EMPIRICALLY calibrated (verified in tests/test_life.py): the stream crosses `row` at this column.
    My first draft used +17 and was wrong by 9; the error was invisible because nothing reached the output
    line at all, so the calibration criterion could not fire. Positive controls are now mandatory."""
    return gun_col + 8 + row


def build(gun_cols, program, eater_offsets=None) -> Circuit:
    g = blank(H, W)
    sites = []
    edges = []
    for i, gc in enumerate(gun_cols):
        place(g, GOSPER_GUN, GUN_ROW, gc)
        edges.append((f"gun{i}", f"out{i}"))
        if program[i] == 0:                        # memory bit 0 -> place an EATER (inhibit gate)
            dy, dx = (eater_offsets or {}).get(i, (0, 0))
            ey = EATER_ROW + dy
            ex = _glider_track_col(gc, EATER_ROW) + dx
            place(g, EATER1, ey, ex)
            sites.append((i, ey, ex))
            edges.append((f"gun{i}", f"eater{i}"))
            edges.append((f"eater{i}", f"out{i}"))
    return Circuit(g, tuple(gun_cols), tuple(program), tuple(sites), tuple(edges),
                   arch_id="A" + "-".join(str(c) for c in gun_cols),
                   program_id="".join(str(b) for b in program))


def output_series(frames) -> np.ndarray:
    """The FUNCTION, as an external observer of the OUTPUT LINE would see it: live cells crossing OUT_ROW."""
    return np.array([int(f[OUT_ROW].sum()) for f in frames], dtype=float)


def simulate(c: Circuit, steps: int = STEPS):
    return run(c.grid, steps)
