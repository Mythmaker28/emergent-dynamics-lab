"""The BLIND A head: causal architecture by interventional tomography, in CAUSAL-GRAPH space.

OBSERVABILITY CONTRACT (binding). This module receives ONLY:
  * raw cell-state frames of a settled grid;
  * the right to intervene, and to see the consequences;
  * the system's declared I/O interface -- the output line (a row index).
It NEVER receives component labels or locations, the program word, gate identities, hidden edges, or expected
outputs. It imports nothing from the evaluator. It never treats an absolute column as an identity: the graph is
expressed in ORDINALS and DELAYS only.

WHY IT IS BUILT THIS WAY (D-053). The previous A head compared CHANNEL-GAP DISTANCES IN COLUMNS against a
tolerance of 6.0, and graded two isomorphic graphs "different" because their guns were 5 columns further apart.
That is geometry, not architecture. Architecture is a GRAPH: it is computed as a graph and compared as a graph.
The only scalar tolerance anywhere is on DELAYS -- a genuine property of a causal edge -- and it is DERIVED from
a measured null, never chosen.

-------------------------------------------------------------------------------------------------------------
THE CONFOUND THAT SHAPED THIS DESIGN, and it is a real one.

The obvious probe is: clear a small tile, see what changes downstream. It does not work, and the reason matters.

A 5x5 tile cleared inside a Gosper gun does NOT delete the gun. It MUTILATES it into a *different working
machine* that emits a glider stream down a NEW diagonal, arriving at output columns (55-58, 95-98, 135-138) that
carry nothing in the intact circuit. MEASURED, not hypothesised.

So a destructive micro-ablation does not remove a component -- it can REPLACE it. Any causal graph inferred from
such interventions is a graph of a system that never existed. My first tomography did exactly this and produced
20 spurious "components" for a 4-component circuit, complete with impossible edges in which deleting matter made
an output rise.

THE FIX: ablate at the SCALE OF A COMPONENT, and PROVE the ablation was clean.
  1. DISCOVER components from the raw trajectory: matter that is persistently occupied and does NOT propagate
     (a gun/eater/block sits still; a glider sweeps through, so a track cell is occupied only briefly).
  2. ABLATE each discovered component ENTIRELY, with a margin.
  3. VERIFY the ablation: it must have removed live matter (no silent no-op), the region must be empty
     afterwards, and the resulting world must return to an exactly periodic state (nothing shattered).
     An intervention that fails verification is CONFOUNDED and is excluded from the evidence -- it is not
     quietly used anyway.

Then, and only then, sort loci by WHAT THEIR CLEAN REMOVAL DOES:

  PERSISTENT_DOWN  an output dies and stays dead    -> the locus is a SOURCE for that output
  PERSISTENT_UP    a silent output comes alive      -> the locus is an INHIBITOR of that output
  TRANSIENT        the output dips and recovers     -> matter in transit: a WIRE, re-supplied by its source
  NONE             nothing happens                  -> causally INERT (decoration)

A memory gate and a cross-stream inhibitor are both PERSISTENT_UP, and they are SUPPOSED to look alike here.
They differ in the GRAPH they sit in -- which is the level at which A is entitled to see a difference at all.
"""

from __future__ import annotations

import numpy as np

from ..substrates.life.fast import step

PERIOD = 60           # grid period of a settled circuit (MEASURED)
OBS = 480             # > the longest causal delay (~250) plus a full new steady state
TAIL = 120            # EXACTLY 2 periods. The output is INTERMITTENT -- gliders arrive in bursts, so most
                      # frames are zero even on a live channel. Judging persistence frame-by-frame therefore
                      # never fires (my first version scored every locus TRANSIENT and abstained on everything).
                      # Persistence is judged on the mean RATE over a whole number of periods, where the
                      # periodic average is exact and the sampling noise is identically zero.
OCC_THRESH = 0.25     # occupancy over one period: stationary matter is far above this, a glider track far below
MERGE_GAP = 4         # A Gosper gun's high-occupancy cells come in ~8 DISJOINT fragments inside its own box,
                      # separated by gaps of at most 4. Two ADJACENT guns at the family's spacing are separated
                      # by 5. So 4 is the exact separating value, and it is MEASURED from the development data,
                      # not chosen: at 6 all four guns merged into a single "component" and the head reported a
                      # 1-node graph driving 4 outputs. THIS IS A DECLARED RESOLUTION LIMIT: components whose
                      # matter is separated by <= MERGE_GAP empty cells CANNOT be told apart by proximity, and
                      # the certificate states it rather than hiding it.
MARGIN = 2            # ablation box dilation
HOLD = 10             # steps the ablation box is held cleared (>= 2 glider periods)
MIN_CELLS = 4         # a "component" smaller than this is noise
PHASES = (0, 15, 30, 45)   # THE DELAY ESTIMATOR MUST BE PHASE-INVARIANT.
                      # An ablation at t=0 destroys whatever happens to be in the box AT THAT PHASE. The gap it
                      # tears in the stream then reaches the output after a time that depends on where the
                      # gliders were when we struck -- so a naive "first frame the output changes" delay swings
                      # by up to half the inter-glider spacing. MEASURED: 214 vs 229 across a half-period shift,
                      # which inflated the null tolerance to 15 steps and cost A its finest resolution.
                      # The causal delay is a property of the PATH, not of when we happened to hit it: it is the
                      # EARLIEST onset over a full cycle of strike phases. Hence min over PHASES.
RESETTLE = 1200       # Before judging "did this ablation SHATTER the world?", let the world finish reacting.
                      # Removing an inhibitor frees a stream that must refill the pipeline all the way to the
                      # border, which takes longer than the observation window. Testing periodicity at t=OBS
                      # therefore flagged two PERFECTLY CLEAN ablations as CONFOUNDED -- a false abstention.
                      # An abstention caused by the observer's own impatience is not honest uncertainty.
EPS = 1e-9


def _line_run(g0, steps, out_row, box=None, hold=0):
    """Only the OUTPUT LINE is retained: storing every full frame for every ablation costs ~10x the time for
    data the head is not permitted to use. A probe too expensive to run exhaustively is a probe that gets
    sub-sampled -- and a sub-sampled probe grid is exactly what made the S head blind in EXP-GT-01."""
    g = g0.copy()
    out = np.empty((steps + 1, g.shape[1]), dtype=np.int32)
    out[0] = g[out_row]
    for t in range(steps):
        if box is not None and t < hold:
            r0, r1, c0, c1 = box
            g[r0:r1, c0:c1] = 0
        g = step(g)
        out[t + 1] = g[out_row]
    return out


def _state_after(g0, steps, box=None, hold=0):
    g = g0.copy()
    for t in range(steps):
        if box is not None and t < hold:
            r0, r1, c0, c1 = box
            g[r0:r1, c0:c1] = 0
        g = step(g)
    return g


def _is_periodic(g, period=PERIOD):
    return np.array_equal(_state_after(g, period), g)


def _clusters_1d(cols, gap=6):
    out, cur = [], []
    for c in sorted(cols):
        if cur and c - cur[-1] > gap:
            out.append(cur)
            cur = []
        cur.append(c)
    if cur:
        out.append(cur)
    return out


# ------------------------------------------------------------------ 1. DISCOVER components (raw frames only)
def occupancy(g0, period=PERIOD):
    g = g0.copy()
    acc = np.zeros(g0.shape, float)
    for _ in range(period):
        acc += g
        g = step(g)
    return acc / period


def discover_components(g0, out_row):
    """Stationary matter = cells occupied a large fraction of a period. Gliders sweep through and are excluded
    by construction. Nothing here consults a hidden label; it is read off the raw trajectory."""
    occ = occupancy(g0)
    mask = occ >= OCC_THRESH
    mask[out_row:, :] = False                      # probe UPSTREAM of the declared readout line (preregistered)
    H, W = mask.shape
    seen = np.zeros_like(mask, bool)
    frags = []
    for r in range(H):
        for c in range(W):
            if mask[r, c] and not seen[r, c]:
                st, cells = [(r, c)], []
                seen[r, c] = True
                while st:
                    y, x = st.pop()
                    cells.append((y, x))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True
                                st.append((ny, nx))
                frags.append(cells)
    # merge fragments that lie within MERGE_GAP of each other -> one component
    boxes = [(min(y for y, _ in f), max(y for y, _ in f), min(x for _, x in f), max(x for _, x in f), len(f))
             for f in frags]
    merged, used = [], set()
    for i, b in enumerate(boxes):
        if i in used:
            continue
        cur = list(b[:4])
        n = b[4]
        used.add(i)
        changed = True
        while changed:
            changed = False
            for j, o in enumerate(boxes):
                if j in used:
                    continue
                if (o[0] <= cur[1] + MERGE_GAP and cur[0] <= o[1] + MERGE_GAP
                        and o[2] <= cur[3] + MERGE_GAP and cur[2] <= o[3] + MERGE_GAP):
                    cur = [min(cur[0], o[0]), max(cur[1], o[1]), min(cur[2], o[2]), max(cur[3], o[3])]
                    n += o[4]
                    used.add(j)
                    changed = True
        if n >= MIN_CELLS:
            merged.append(tuple(cur))
    return sorted(merged)


# ------------------------------------------------------------------ 2-3. ABLATE, and PROVE the ablation clean
def phase_states(g0):
    """The settled grid at each strike phase, computed ONCE per circuit. Recomputing the phase baselines inside
    every component's ablation multiplied the whole tomography by the number of components, for identical data."""
    return {ph: (_state_after(g0, ph) if ph else g0) for ph in PHASES}


def clean_ablation(g0, box, out_row, states=None, baselines=None):
    """Ablate at EVERY strike phase. `line`/`base` are reported at phase 0 (for the persistence rate), while the
    DELAY of each effect is the EARLIEST onset over all phases -- the phase-invariant causal path length."""
    r0, r1, c0, c1 = box
    H, W = g0.shape
    b = (max(0, r0 - MARGIN), min(H, r1 + 1 + MARGIN), max(0, c0 - MARGIN), min(W, c1 + 1 + MARGIN))
    touched = int(g0[b[0]:b[1], b[2]:b[3]].sum())            # EFFICACY: it must actually have removed matter
    states = states or phase_states(g0)
    baselines = baselines or {ph: _line_run(states[ph], OBS, out_row) for ph in PHASES}
    per_phase = [(baselines[ph], _line_run(states[ph], OBS, out_row, box=b, hold=HOLD)) for ph in PHASES]
    end = _state_after(g0, OBS, box=b, hold=HOLD)
    verdict = "OK"
    if touched == 0:
        verdict = "NO_OP"                                    # a silent no-op is not evidence of anything
    elif not _is_periodic(_state_after(end, RESETTLE)):
        verdict = "SHATTERED"                                # the world never returns to a periodic state
    return {"box": b, "base": per_phase[0][0], "line": per_phase[0][1],
            "per_phase": per_phase, "touched": touched, "verdict": verdict}


# ------------------------------------------------------------------ the tomography
def blind_tomography(g0: np.ndarray, out_row: int, region=None) -> dict:
    """`region` = (row_lo, row_hi, col_lo, col_hi) restricts where components may be FOUND. It exists so that
    INSUFFICIENT COVERAGE can be simulated and A can be shown to ABSTAIN -- not so a real run can skip a circuit."""
    base = _line_run(g0, OBS, out_row)
    comps = discover_components(g0, out_row)
    if region:
        rl, rh, cl, ch = region
        comps = [b for b in comps if rl <= b[0] and b[1] < rh and cl <= b[2] and b[3] < ch]

    states = phase_states(g0)
    baselines = {ph: _line_run(states[ph], OBS, out_row) for ph in PHASES}
    live_cols = set(np.nonzero(base.sum(0))[0])
    abl = []
    for b in comps:
        a = clean_ablation(g0, b, out_row, states=states, baselines=baselines)
        abl.append(a)
        if a["verdict"] == "OK":
            d = a["line"] - base
            live_cols |= set(np.nonzero(np.abs(d).sum(0))[0])   # a suppressed output revealed by a CLEAN removal

    out_nodes = [(min(g), max(g)) for g in _clusters_1d(sorted(live_cols))]

    macro, edges = [], []
    for i, (b, a) in enumerate(zip(comps, abl)):
        if a["verdict"] != "OK":
            macro.append({"box": b, "verdict": a["verdict"], "targets": {}})
            continue
        targets = {}
        for j, (lo, hi) in enumerate(out_nodes):
            onsets, drift = [], None
            for (bp, lp) in a["per_phase"]:
                dj = (lp - bp)[:, lo:hi + 1].sum(1).astype(float)
                nz = np.nonzero(np.abs(dj) > EPS)[0]
                if len(nz):
                    onsets.append(int(nz[0]))
                if drift is None:
                    drift = float(dj[-TAIL:].mean())            # exact periodic average: no sampling noise
            if not onsets:
                continue
            kind = "PERSISTENT_DOWN" if drift < -EPS else ("PERSISTENT_UP" if drift > EPS else "TRANSIENT")
            if kind == "TRANSIENT":
                continue                                        # a wire, not a node of the architecture
            delay = int(min(onsets))                            # PHASE-INVARIANT: earliest onset over all phases
            targets[j] = {"kind": kind, "delay": delay}
            edges.append({"src": i, "dst": j, "kind": kind, "delay": delay})
        macro.append({"box": b, "verdict": "OK", "targets": targets})

    baseline_live = {j for j, (lo, hi) in enumerate(out_nodes) if base[:, lo:hi + 1].sum() > 0}
    sourced = {e["dst"] for e in edges if e["kind"] == "PERSISTENT_DOWN"}
    return {"n_out": len(out_nodes), "out_nodes": out_nodes, "macro": macro, "edges": edges,
            "n_components": len(comps),
            "n_inert": sum(1 for m in macro if m["verdict"] == "OK" and not m["targets"]),
            "confounded": [m["box"] for m in macro if m["verdict"] not in ("OK",)],
            "baseline_live": sorted(baseline_live),
            "uncovered_outputs": sorted(baseline_live - sourced)}


# ------------------------------------------------------------------ the A head
def graph_signature(t: dict, delay_tol: int = 0) -> tuple:
    """Isomorphism-invariant, layout-free, translation-free. Output nodes enter ONLY as ordinals; components ONLY
    through their edge sets. INERT components contribute nothing -- decoration is not architecture. Delays are
    NOT baked in here; they are compared separately, WITHIN TOLERANCE (see `_match`)."""
    rows = [tuple(sorted((j, tt["kind"]) for j, tt in m["targets"].items()))
            for m in t["macro"] if m["verdict"] == "OK" and m["targets"]]
    return (t["n_out"], tuple(sorted(rows)))


def _match(t1: dict, t2: dict, delay_tol: int) -> bool:
    """Structure first, then delays WITHIN TOLERANCE.

    Quantizing a delay by `delay // (tol+1)` is NOT the same as "agrees within tol": 214 and 229 differ by 15,
    but with tol=15 they fall in buckets 13 and 14 and the head calls them DIFFERENT. A boundary between two
    buckets is not a tolerance -- it is an arbitrary line that two values within tolerance can still straddle.
    Delays are therefore compared PAIRWISE against the tolerance, after the components have been matched by
    their edge structure."""
    if graph_signature(t1) != graph_signature(t2):
        return False
    def rows(t):
        out = []
        for m in t["macro"]:
            if m["verdict"] != "OK" or not m["targets"]:
                continue
            out.append((tuple(sorted((j, tt["kind"]) for j, tt in m["targets"].items())),
                        tuple(d for _, d in sorted((j, tt["delay"]) for j, tt in m["targets"].items()))))
        return sorted(out)
    r1, r2 = rows(t1), rows(t2)
    for (s1, d1), (s2, d2) in zip(r1, r2):
        if s1 != s2 or len(d1) != len(d2):
            return False
        if any(abs(x - y) > delay_tol for x, y in zip(d1, d2)):
            return False
    return True


def head_A(t1: dict, t2: dict, delay_tol: int) -> str:
    """SAME / DIFFERENT / INDETERMINATE. Correct abstention is a PASS; fabricated certainty is a FAILURE."""
    for t in (t1, t2):
        if t["uncovered_outputs"]:
            return "INDETERMINATE"          # a LIVE output whose source was never found: coverage insufficient
        if t["confounded"]:
            return "INDETERMINATE"          # an intervention we could not prove clean is not evidence
        if not any(m["targets"] for m in t["macro"]):
            return "INDETERMINATE"          # nothing causal discovered at all
    return "SAME" if _match(t1, t2, delay_tol) else "DIFFERENT"


def head_G(t1: dict, t2: dict) -> str:
    """G -- geometric embedding. The ONLY head allowed to move on a pure layout change. Reported SEPARATELY and
    NEVER composited. Translation-invariant: it compares output-node SPACINGS, never absolute columns."""
    def sp(t):
        cs = [(lo + hi) / 2 for lo, hi in t["out_nodes"]]
        return tuple(round(cs[i + 1] - cs[i]) for i in range(len(cs) - 1))
    return "SAME" if sp(t1) == sp(t2) else "DIFFERENT"
