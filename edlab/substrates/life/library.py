"""Verified Game-of-Life component + ARCHITECTURE library with GENUINE topological contrasts.

WHY THIS EXISTS (D-053). The EXP-GT-00 circuit family contained exactly one causal architecture -- four
independent parallel channels `gun_i -> (gate_i) -> out_i` -- drawn at three different column spacings. Its
"held-out architectures" were the SAME graph with a different gun spacing, and one of them was a dead circuit.
`A` was therefore never once tested against a real architectural difference, and D-052's plan to sharpen A's
tolerance had NOTHING TO RESOLVE.

This module supplies what was missing: architectures that differ in **topology, delay, redundancy and
connectivity** while sharing components, layout family and program -- and architectures that differ in **layout,
decoration and material** while sharing topology. Every primitive below was found and confirmed EMPIRICALLY
(/tmp probes, then locked by tests); none is asserted from GoL folklore.

VERIFIED PRIMITIVES
-------------------
SE gun at (r,c)   -- Gosper gun. Emits an SE glider stream on the DIAGONAL invariant  D = c - r + 13.
                     It crosses OUT_ROW at column  D + OUT_ROW.  Spacing >= 38 or adjacent guns ANNIHILATE
                     (the gun spans 36 columns; at 36 the bounding boxes touch). MEASURED, D-053.
SE eater at ...   -- absorbs an SE stream and survives. This is the MEMORY BIT (program), never architecture.
DELAY SHIFT       -- a gun moved by (k,k) keeps  D  invariant, so the output column is IDENTICAL, but the
                     stream starts k rows lower and arrives EXACTLY 4k steps earlier. This is a pure DELAY
                     edit with the topology and the output track held fixed. Finest edit: k=1 -> 4 steps.
SW gun at (r,c)   -- the column-mirrored Gosper gun. Emits an SW stream on the ANTI-DIAGONAL  K = c + r + 20,
                     crossing OUT_ROW at column  K - OUT_ROW.
CROSS-INHIBITOR   -- an SW stream and an SE stream MUTUALLY ANNIHILATE where they meet. Both are consumed;
                     NOTHING reaches the output row. The SW stream is therefore consumed at the FIRST SE track
                     it meets (smallest crossing row), and shields every SE track behind it. This yields:
                       (i)  a genuine EDGE ADDITION  gunSW -> out_target   (target output falls to zero), and
                       (ii) an EMERGENT SHIELDING EDGE  gun_target -> out_(next one back): ablating the target's
                            gun frees the SW stream, which travels on and kills the NEXT channel. MEASURED.
                     (ii) is exactly the sort of edge a *declared* graph misses and a *measured* one finds.
BLOCK             -- a still life placed off every track: causally INERT (output series bit-identical). MEASURED.
DECOY EATER       -- an eater placed OFF a track: same cell count and visual density as a real gate, ZERO causal
                     effect. The trap for any observer that keys on appearance instead of causation.

SETTLING (a defect inherited from EXP-GT-02/02B and corrected here). Those experiments used SETTLE = 400 and
described it as "a common established state". It is not: these circuits are NOT yet periodic at t = 400. They
become EXACTLY periodic with grid period 60 only after ~700 steps. SETTLE = 720 (a multiple of 60, >= 700).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .engine import blank, place, GOSPER_GUN, EATER1, BLOCK
from .fast import step

H, W = 120, 300
GUN_ROW = 5
OUT_ROW = 70
SETTLE = 720          # MEASURED: exactly periodic (period 60) only from ~700. EXP-GT-02's 400 was transient.
PERIOD = 60           # MEASURED exact grid period of the settled circuit (the gun period is 30).
MIN_GUN_SPACING = 38  # MEASURED: 34-37 annihilate, >= 38 viable.
OUT_HALFWIN = 12

_MAXX = max(x for _, x in GOSPER_GUN)
GUN_SW = [(y, _MAXX - x) for y, x in GOSPER_GUN]      # column-mirrored -> emits SW gliders
_EMAXX = max(x for _, x in EATER1)
EATER_SW = [(y, _EMAXX - x) for y, x in EATER1]       # column-mirrored eater -> absorbs SW gliders
EATER_OFF = (-4, -3)                                  # FROZEN from EXP-GT-00: absorbs an SE stream and survives
EATER_SW_OFF = (-4, -2)                               # MEASURED: absorbs an SW stream and survives


# ------------------------------------------------------------------ intrinsic frames (no lab coordinates)
def se_diag(r: int, c: int) -> int:
    """The DIAGONAL a gun at (r,c) emits along. Invariant under (k,k) translation -- the intrinsic channel id."""
    return c - r + 13


def se_out_col(r: int, c: int) -> int:
    return se_diag(r, c) + OUT_ROW


def sw_anti(r: int, c: int) -> int:
    return c + r + 20


def sw_out_col(r: int, c: int) -> int:
    return sw_anti(r, c) - OUT_ROW


def crossing_row(se_r, se_c, sw_r, sw_c) -> float:
    """Row at which an SE track and an SW track meet. Consumed at the FIRST crossing reached."""
    return (sw_anti(sw_r, sw_c) - se_diag(se_r, se_c)) / 2.0


# ------------------------------------------------------------------ components
@dataclass(frozen=True)
class Comp:
    kind: str            # 'se_gun' | 'sw_gun' | 'se_eater' | 'sw_eater' | 'block'
    row: int
    col: int
    name: str = ""

    def cells(self):
        return {"se_gun": GOSPER_GUN, "sw_gun": GUN_SW, "se_eater": EATER1,
                "sw_eater": EATER_SW, "block": BLOCK}[self.kind]

    def box(self):
        cs = self.cells()
        h = max(y for y, _ in cs) + 1
        w = max(x for _, x in cs) + 1
        return (self.row, self.row + h, self.col, self.col + w)


@dataclass
class Arch:
    """A circuit. `components` is the truth; `declared_edges` is a HYPOTHESIS about what the dynamics realize,
    and it is checked against a MEASURED graph before the architecture may enter the benchmark."""
    arch_id: str
    components: list
    program: tuple = ()                 # memory word, one bit per SE channel (1 = open, 0 = gated)
    declared_edges: tuple = ()
    note: str = ""
    meta: dict = field(default_factory=dict)

    # ---- SE channels are the output nodes, ordered by their intrinsic diagonal (NOT by column)
    def se_guns(self):
        return [c for c in self.components if c.kind == "se_gun"]

    def out_nodes(self):
        """One output node per DISTINCT SE diagonal, ordered by diagonal. Layout-free channel ordinals."""
        return sorted({se_diag(g.row, g.col) for g in self.se_guns()})

    def grid(self) -> np.ndarray:
        g = blank(H, W)
        for c in self.components:
            place(g, c.cells(), c.row, c.col)
        return g

    def geometric_signature(self) -> dict:
        gs = sorted((g.row, g.col) for g in self.se_guns())
        cols = [c for _, c in gs]
        return {"gun_rows_cols": gs, "spacings": [cols[i + 1] - cols[i] for i in range(len(cols) - 1)],
                "n_se_guns": len(gs), "n_components": len(self.components),
                "n_cells": int(self.grid().sum())}


def settle(a: Arch, extra_phase: int = 0) -> np.ndarray:
    g = a.grid()
    for _ in range(SETTLE + extra_phase):
        g = step(g)
    return g


def run_from(g0: np.ndarray, steps: int, box=None, hold: int = 0):
    g = g0.copy()
    frames = [g.copy()]
    for t in range(steps):
        if box is not None and t < hold:
            r0, r1, c0, c1 = box
            g[r0:r1, c0:c1] = 0
        g = step(g)
        frames.append(g.copy())
    return frames


def out_window(diag: int) -> tuple:
    c = diag + OUT_ROW
    return max(0, c - OUT_HALFWIN), min(W, c + OUT_HALFWIN + 1)


def channel_output(frames, diag: int) -> np.ndarray:
    lo, hi = out_window(diag)
    return np.array([int(f[OUT_ROW, lo:hi].sum()) for f in frames], dtype=int)


def total_output(frames) -> np.ndarray:
    return np.array([int(f[OUT_ROW].sum()) for f in frames], dtype=int)


# ================================================================== EVALUATOR (privileged; never seen by a head)
OBS = 360             # >= 6 grid periods (60) after the intervention


def measured_graph(a: Arch) -> dict:
    """The graph the DYNAMICS realizes -- measured by ablating every component in turn and recording which
    output nodes move, and after how long. A declared graph that is never checked against this is a comment."""
    g0 = settle(a)
    outs = a.out_nodes()
    base = {d: channel_output(run_from(g0, OBS), d) for d in outs}
    edges, delays, effects = [], {}, {}
    for comp in a.components:
        if comp.kind == "block":
            pass                                   # blocks are ablated too: an inert part must MEASURE as inert
        fr = run_from(g0, OBS, box=comp.box(), hold=8)
        for d in outs:
            diff = channel_output(fr, d) - base[d]
            nz = np.nonzero(diff != 0)[0]
            if len(nz):
                e = (comp.name, f"out[{d}]")
                edges.append(e)
                delays["->".join(e)] = int(nz[0])
                effects["->".join(e)] = "UP" if diff[nz].mean() > 0 else "DOWN"
    return {"nodes": sorted({c.name for c in a.components} | {f"out[{d}]" for d in outs}),
            "edges": sorted(set(edges)), "delays": delays, "effects": effects,
            "baseline": {f"out[{d}]": float(base[d].mean()) for d in outs},
            "n_out": len(outs)}


def viable(a: Arch) -> tuple:
    """Executable positive control. Every SE channel that the program declares OPEN and that no architectural
    inhibitor targets must actually carry a stream; the settled state must be exactly periodic (no explosion)."""
    g0 = settle(a)
    fr = run_from(g0, OBS)
    means = {d: float(channel_output(fr, d).mean()) for d in a.out_nodes()}
    g = g0.copy()
    for _ in range(PERIOD):
        g = step(g)
    periodic = bool(np.array_equal(g, g0))
    return periodic, means


def stable(a: Arch) -> bool:
    return viable(a)[0]


# ================================================================== EXECUTABLE STRUCTURAL INVARIANTS
def _boxes_overlap(b1, b2) -> bool:
    r0, r1, c0, c1 = b1
    s0, s1, d0, d1 = b2
    return not (r1 <= s0 or s1 <= r0 or c1 <= d0 or d1 <= c0)


def assert_no_overlap(a: Arch) -> None:
    """Two components whose bounding boxes overlap are NOT two components -- they are one merged blob, and
    ablating either one mutilates the other. This assertion caught an SW gun placed on top of gun3 (cols
    150-185 vs 125-160): the causal graph measured on that circuit would have been meaningless."""
    bs = [(c.name, c.box()) for c in a.components]
    bad = [(n1, n2) for i, (n1, b1) in enumerate(bs) for (n2, b2) in bs[i + 1:] if _boxes_overlap(b1, b2)]
    if bad:
        raise AssertionError(f"{a.arch_id}: component boxes OVERLAP {bad} -- ablation cannot isolate them")


def assert_viable(a: Arch) -> dict:
    """A circuit is admissible ONLY if it actually computes. Two conditions, both executable:
      (1) the settled state is EXACTLY periodic (period 60) -- nothing is exploding;
      (2) every output node the architecture predicts is LIVE actually carries a stream.
    (1) alone is NOT enough: an empty grid is perfectly periodic. A dead circuit passed (1) during development
    and would have entered the benchmark as a 'held-out architecture' -- which is exactly how the sp36 layout
    survived since EXP-GT-00."""
    assert_no_overlap(a)
    periodic, means = viable(a)
    if not periodic:
        raise AssertionError(f"{a.arch_id}: settled state is not periodic at lag {PERIOD} -- not settled/stable")
    pred = predict_active(a)
    live = {t for _, t in pred["edges"] if pred["effects"].get(f"{_}->{t}") != "SILENT"}
    dead = [d for d in a.out_nodes() if f"out[{d}]" in pred["live_outputs"] and means[d] <= 0.5]
    if dead:
        raise AssertionError(f"{a.arch_id}: output nodes {dead} are declared LIVE but carry no stream "
                             f"(means={ {k: round(v,2) for k,v in means.items()} })")
    return {"periodic": periodic, "outputs": means}


# ================================================================== PREDICTED ACTIVE GRAPH (path 1 of 2)
def predict_active(a: Arch) -> dict:
    """Predict the ACTIVE-influence graph from GEOMETRY ALONE -- an independent second path to the same answer.

    DIFFERENTIAL VERIFICATION (project norm): `measured_graph` derives the graph by INTERVENTION; this derives it
    by GEOMETRY. They share no code. If they disagree, one of them is wrong and the circuit is rejected. A single
    path to a causal graph is a claim; two independent agreeing paths is a measurement."""
    guns = {c.name: c for c in a.components if c.kind == "se_gun"}
    sws = [c for c in a.components if c.kind == "sw_gun"]
    gates = {c.name: c for c in a.components if c.kind == "se_eater"}
    outs = a.out_nodes()

    # which SE track does each SW stream reach first (and is consumed by)?
    inhibited, shielded = {}, {}
    for sw in sws:
        order = sorted(((crossing_row(g.row, g.col, sw.row, sw.col), se_diag(g.row, g.col), g.name)
                        for g in guns.values() if 0 < crossing_row(g.row, g.col, sw.row, sw.col) < OUT_ROW))
        if order:
            _, d_t, n_t = order[0]
            inhibited[d_t] = (sw.name, n_t)
            if len(order) > 1:                     # ablating the target frees the stream -> it kills the NEXT one
                shielded[d_t] = order[1][1]

    # a gate sits on a track iff its row/col lie on that diagonal (the gate is PROGRAM, never architecture)
    gate_of = {}
    for gn, gc_ in gates.items():
        d = (gc_.col - EATER_OFF[1]) - (gc_.row - EATER_OFF[0]) + 13 - 35 + 35
        d = (gc_.col - EATER_OFF[1]) - 35          # track column at row 35 was (d + 35)
        if d in outs:
            gate_of[d] = gn

    edges, effects, live = [], {}, []
    for gname, g in guns.items():
        d = se_diag(g.row, g.col)
        if d in gate_of:                                       # PROGRAM closes it: the gate is the active cause
            edges.append((gate_of[d], f"out[{d}]"))
            effects[f"{gate_of[d]}->out[{d}]"] = "UP"          # remove the gate -> output APPEARS
        elif d in inhibited:                                   # ARCHITECTURE closes it: an added inhibitor edge
            swname, _ = inhibited[d]
            edges.append((swname, f"out[{d}]"))
            effects[f"{swname}->out[{d}]"] = "UP"              # remove the inhibitor -> output APPEARS
            if d in shielded:                                  # EMERGENT: the target SHIELDS the next channel
                edges.append((gname, f"out[{shielded[d]}]"))
                effects[f"{gname}->out[{shielded[d]}]"] = "DOWN"
        else:
            edges.append((gname, f"out[{d}]"))
            effects[f"{gname}->out[{d}]"] = "DOWN"             # remove the gun -> output DISAPPEARS
            live.append(f"out[{d}]")
    # REDUNDANT PATH: an SW stream that is NOT consumed above the output row lands at column K - OUT_ROW.
    # It feeds output node d iff that column falls inside d's window -- so compare COLUMNS, not diagonals.
    # (My first version compared `sw_out_col - OUT_ROW` against the diagonal, i.e. subtracted OUT_ROW twice.
    #  The geometry/intervention differential check caught it: the measured graph had an edge the geometry
    #  did not predict. A single path to a causal graph would have shipped that bug.)
    for sw in sws:
        if any(sw.name == n for n, _ in inhibited.values()):
            continue                                           # consumed before it ever reaches the output
        land = sw_anti(sw.row, sw.col) - OUT_ROW
        for d in outs:
            lo, hi = out_window(d)
            if lo <= land < hi:
                edges.append((sw.name, f"out[{d}]"))
                effects[f"{sw.name}->out[{d}]"] = "DOWN"
                live.append(f"out[{d}]")
    return {"edges": sorted(set(edges)), "effects": effects, "live_outputs": sorted(set(live)),
            "inhibited": inhibited, "shielded": shielded}


def assert_graph_agrees(a: Arch) -> dict:
    """The two independent paths must agree. Disagreement = a bug, and the circuit is REJECTED, not patched."""
    pred = predict_active(a)
    meas = measured_graph(a)
    p = sorted(set("->".join(e) for e in pred["edges"]))
    m = sorted(set("->".join(e) for e in meas["edges"]))
    if p != m:
        raise AssertionError(f"{a.arch_id}: GEOMETRIC prediction and INTERVENTIONAL measurement DISAGREE.\n"
                             f"  predicted only: {[e for e in p if e not in m]}\n"
                             f"  measured only : {[e for e in m if e not in p]}")
    return meas


# ================================================================== THE ARCHITECTURE SET
BASE_COLS = [5, 45, 85, 125]     # spacing 40, MEASURED viable. Diagonals 13/53/93/133; out cols 83/123/163/203.
SW_COL = 190                     # MEASURED: K=215; first crossing = diag 133 at row 41. Box starts at 190, so it
                                 # does NOT overlap gun3 (cols 125..160). At col 150 it DID -- assertion caught it.
DELAY_CHAN = 3                   # the LAST channel: shifting it right/down only GROWS the gap to its neighbour.
                                 # Shifting an INTERIOR channel right closes the 4-column gap and the guns
                                 # annihilate (k>=3 produced a dead circuit). Assertion caught that too.


def _se(cols, rows=None):
    rows = rows or [GUN_ROW] * len(cols)
    return [Comp("se_gun", r, c, f"gun{i}") for i, (r, c) in enumerate(zip(rows, cols))]


def _gates(cols, program, rows=None):
    rows = rows or [GUN_ROW] * len(cols)
    out = []
    for i, (r, c) in enumerate(zip(rows, cols)):
        if i < len(program) and program[i] == 0:
            d = se_diag(r, c)
            out.append(Comp("se_eater", 35 + EATER_OFF[0], (d + 35) + EATER_OFF[1], f"gate{i}"))
    return out


def arch_base(program=(1, 1, 1, 1), cols=None, rows=None, arch_id="BASE") -> Arch:
    cols = cols or BASE_COLS
    a = Arch(arch_id, _se(cols, rows) + _gates(cols, program, rows), tuple(program), (),
             "N independent parallel channels; gates are PROGRAM, not architecture.")
    a.declared_edges = tuple(predict_active(a)["edges"])
    return a


def arch_delay(k: int, chan: int = DELAY_CHAN, program=(1, 1, 1, 1)) -> Arch:
    """DELAY EDIT with the topology and the output track held EXACTLY fixed. The gun moves by (k,k): the diagonal
    is invariant, so the output column is unchanged, but the stream starts k rows lower and arrives 4k steps
    earlier. The finest architectural edit this substrate admits: k=1 -> 4 steps."""
    cols, rows = list(BASE_COLS), [GUN_ROW] * len(BASE_COLS)
    rows[chan] += k
    cols[chan] += k
    a = arch_base(program, cols, rows, arch_id=f"DELAY_k{k}")
    a.note = f"same graph; channel {chan} arrives {4*k} steps earlier"
    a.meta = {"delay_edit_steps": 4 * k, "k": k, "chan": chan}
    return a


def arch_xinhib(sw_col: int = SW_COL, program=(1, 1, 1, 1)) -> Arch:
    """EDGE ADDITION by a cross-stream inhibitor, plus an EMERGENT shielding edge."""
    a = arch_base(program, arch_id=f"XINHIB")
    a.components = a.components + [Comp("sw_gun", GUN_ROW, sw_col, "gunSW")]
    a.declared_edges = tuple(predict_active(a)["edges"])
    a.note = "cross-stream inhibitor: one added edge + one EMERGENT shielding edge"
    return a


def arch_5chan(program=(1, 1, 1, 1, 1)) -> Arch:
    return arch_base(program, cols=BASE_COLS + [165], arch_id="FIVE_CHAN")


def arch_inert(program=(1, 1, 1, 1)) -> Arch:
    a = arch_base(program, arch_id="INERT_DECOR")
    a.components = a.components + [Comp("block", r, c, f"decor{i}")
                                   for i, (r, c) in enumerate([(100, 20), (100, 250), (25, 250)])]
    a.note = "inert still lifes off every track; MEASURED zero causal effect"
    return a


def arch_decoy(program=(1, 1, 1, 1)) -> Arch:
    """IDENTICAL VISUAL DENSITY, DIFFERENT DEPENDENCY GRAPH: eaters with the same cell count and appearance as
    real gates, placed OFF the tracks. The trap for any observer keying on looks instead of causation."""
    a = arch_base(program, arch_id="DECOY_EATERS")
    a.components = a.components + [Comp("se_eater", 50, 25, "decoy0"), Comp("se_eater", 95, 60, "decoy1")]
    a.note = "eaters off-track: gate-like density, MEASURED zero causal effect"
    return a


def arch_direct() -> Arch:
    d = se_diag(GUN_ROW, 45)
    a = Arch("DIRECT_1PATH", [Comp("se_gun", GUN_ROW, 45, "gunA")], (1,),
             (("gunA", f"out[{d}]"),), "one path into one output node")
    return a


def arch_redundant() -> Arch:
    """REDUNDANT TWO-PATH: an SE gun and an SW gun reach the SAME output window, crossing only BELOW the output
    row, so both paths deliver. Ablating either leaves the output non-zero. DISCLOSED: F differs from the single
    path (the rate doubles) -- a redundant path with a bit-identical output is NOT realizable in this component
    library without a glider reflector, and is not faked."""
    a = Arch("REDUNDANT_2PATH", [Comp("se_gun", GUN_ROW, 45, "gunA"), Comp("sw_gun", GUN_ROW, 178, "gunB")],
             (1,), (), "two independent paths into one output node")
    a.declared_edges = tuple(predict_active(a)["edges"])
    return a
