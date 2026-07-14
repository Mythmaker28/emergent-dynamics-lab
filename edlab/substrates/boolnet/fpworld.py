"""The world interface used by the causal-response fingerprint, and the E1 mid-trajectory replacement.

`hier.World` is hashed into three retired freeze manifests and is not touched. This is a separate, additive
interface with the one primitive the fingerprint battery needs -- a clamp held over a WINDOW, not over a prefix.

It also carries the Ship-of-Theseus arm: a single continuous trajectory in which the gate's IMPLEMENTATION is
replaced part-way through, function and latency preserved, and the observed behaviour must not be interrupted.
That is the closest structural analogue this substrate has to a droplet replacing its own material while it goes
on eating.
"""

from __future__ import annotations

import numpy as np

from .engine import step
from .circuits import Machine, SETTLE, settled


class FPWorld:
    """Observation is restricted to the DECLARED BEHAVIOURAL OUTPUT. The fingerprint never reads an internal cell:
    in the droplet you can image `uptake`, and you cannot ask a droplet what its gate is doing."""

    def __init__(self, net, out_cells):
        self._net = net
        self.out_cells = tuple(out_cells)
        self._s0 = None
        self.n_interventions = 0

    def _settled(self):
        if self._s0 is None:
            cur = self._net
            for k in range(SETTLE):
                cur = step(cur, k)
            self._s0 = cur
        return self._s0

    def trace(self, clamp=None, hold=0, steps=0):
        if clamp:
            self.n_interventions += 1
        cur = self._settled()
        grids, outs = [], []
        for k in range(steps):
            cl = clamp if (clamp and k < hold) else None
            cur = step(cur, SETTLE + k, cl)
            grids.append(cur.state.copy())
            outs.append(tuple(int(cur.state[r, c]) for (r, c) in self.out_cells))
        return np.stack(grids), outs

    def pulse_at(self, cell, value, at_step, steps, bg=None):
        self.n_interventions += 1
        cur = self._settled()
        grids = []
        for k in range(steps):
            cl = dict(bg) if bg else {}
            if k == at_step:
                cl[cell] = value
            cur = step(cur, SETTLE + k, cl or None)
            grids.append(cur.state.copy())
        return np.stack(grids)

    def window_clamp(self, cell, value, at, hold, steps):
        """A clamp active for steps in [at, at + hold). The battery's sustained probe: it begins when the battery
        says it begins, for every system alike."""
        self.n_interventions += 1
        cur = self._settled()
        grids = []
        for k in range(steps):
            cl = {cell: value} if (at <= k < at + hold) else None
            cur = step(cur, SETTLE + k, cl)
            grids.append(cur.state.copy())
        return np.stack(grids)


def probe_cells(m: Machine, chan: int, arm: str) -> dict:
    """The ADDRESSES the arm may touch. Not identities, not labels, not ground truth -- addresses.

    drive     the single exogenous driver of the whole machine   (droplet: the external nutrient / attractant field)
    supply    the drive line at this entity's own column         (droplet: a locally applied bolus)
    internal  the machine's internal state variables             (droplet: rho, U, V -- NO NON-DESTRUCTIVE ACCESS,
              so this list is EMPTY in the droplet arm, and that emptiness is the entire point of the arm)
    """
    cc = m.meta["chan_cols"][chan]
    cells = {"drive": (1, 1), "supply": (1, cc)}
    # THE ADDRESSES ARE FIXED BY THE LAYOUT, NOT BY WHICH COMPONENTS EXIST. My first version listed the machine's
    # ACTUAL registers, so a system with a second register received a longer battery than one without -- a
    # coordinate system whose number of axes depended on the thing being measured. Two such fingerprints are not
    # comparable, and comparing them anyway is how a measurement becomes an opinion.
    #
    # These three slots exist in every layout. Clamping a slot that happens to hold nothing is a perfectly legal
    # intervention that produces no response, and "no response" is a comparable coordinate.
    if arm == "rich":
        cells["internal"] = [(4, cc + 2), (4, cc + 3), (20, 1)]     # register slot, second-register slot, write-enable
    else:
        cells["internal"] = []                                       # NO non-destructive internal access in a droplet
    return cells


# ---------------------------------------------------------------- E1: replacement during one trajectory
def swapped_trajectory(m_a: Machine, m_b: Machine, t_swap: int, steps: int) -> dict:
    """ONE continuous trajectory. Configuration A runs to `t_swap`; the machine's OPERATIONS are then replaced by
    B's, carrying the state forward; the trajectory continues. Function and latency are preserved by construction
    (A and B compute the same thing with the same delay out of different parts).

    The behavioural output is compared against the un-swapped A trajectory and against B's own settled behaviour.
    A transient at the seam is expected and is MEASURED, not assumed away: the claim is
    'function-preserving replacement with observed behaviour uninterrupted after a bounded transient of k steps',
    and k is reported.
    """
    cur = settled(m_a)
    out_a_only, out_swap = [], []
    ref = settled(m_a)
    for k in range(steps):                      # the un-swapped reference
        ref = step(ref, SETTLE + k)
        out_a_only.append(tuple(int(ref.state[r, c]) for (r, c) in m_a.out_cells))
    for k in range(steps):
        if k == t_swap:
            nxt = m_b.net.copy()                # the OPERATIONS are replaced; the STATE is carried across
            nxt.state = cur.state.copy()
            cur = nxt
        cur = step(cur, SETTLE + k)
        out_swap.append(tuple(int(cur.state[r, c]) for (r, c) in m_a.out_cells))
    a = np.array(out_a_only)
    s = np.array(out_swap)
    diff = np.nonzero((a != s).any(axis=1))[0]
    post = diff[diff >= t_swap]
    transient = int(post.max() - t_swap + 1) if len(post) else 0
    return {"out_reference": a, "out_swapped": s, "t_swap": t_swap,
            "transient_steps": transient,
            "uninterrupted_after": t_swap + transient,
            "identical_before_swap": bool(np.array_equal(a[:t_swap], s[:t_swap]))}
