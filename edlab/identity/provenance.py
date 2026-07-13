"""TEMPORAL PROVENANCE. Written BEFORE the observer that will depend on it, because the last observer died of this.

WHAT KILLED D-067. The manifold harvester labelled each sample's source history with `g[t - d]`. When the lag `d`
exceeded `t`, the index was negative, numpy read from the END of the array, and the row was labelled with a source
history from a completely different time -- a state the world never produced. The consistency check then worked
perfectly: it found the contradiction and concluded the module had hidden internal state. The thing hiding state
was the array index.

The assertion that was supposed to prevent this checked that every row had a GENERATED OUTPUT. It did. It never
checked that the row was LABELLED WITH THE HISTORY THAT PRODUCED IT. It guarded the wrong side of the pair.

    A FEATURE IS NOT A NUMBER. It is a CLAIM: "at time t-d, in episode e, source s held value v."
    Every such claim is recorded, and every recorded claim is RE-READ FROM THE EPISODE AND COMPARED.

Nothing here relies on array semantics. Negative indices, implicit wrapping, padding from future samples and silent
truncation are forbidden by explicit assertion, not by convention. `_idx` refuses a negative index rather than
returning the end of the array, because that is the entire lesson of D-067 in one function.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


class ProvenanceError(AssertionError):
    """Raised LOUDLY. A provenance failure is never a warning and never a dropped row without a count."""


def _idx(t: int, d: int, T: int) -> int:
    """The only place a lagged index is ever computed. It REFUSES rather than wraps."""
    i = t - d
    if i < 0:
        raise ProvenanceError(
            f"NEGATIVE TEMPORAL INDEX: t={t}, lag={d}, t-d={i}. The required history is BEFORE the start of the "
            f"episode. numpy would silently return sample {T + i}, from the far end of the trajectory. "
            f"That fabricated history is what retired the previous observer (D-067).")
    if i >= T:
        raise ProvenanceError(f"index {i} beyond the episode (T={T}): a sample from the future is not a history")
    return i


@dataclass
class Episode:
    """ONE generating trajectory. Every sample the observer ever uses belongs to exactly one of these, and carries
    its identity. A row may never mix episodes, worlds or branches -- concatenated storage is not a timeline."""
    world_id: str
    episode_id: str
    clamp: dict                      # the intervention: {cell: value}, held for `hold` steps
    hold: int
    T: int                           # the observation window: samples 0 .. T-1
    grid: np.ndarray                 # (T, H, W)
    context: tuple = ()
    kind: str = "sustained"          # "sustained" | "pulse" | "baseline"
    pulse_at: int = -1

    def sample(self, cell, t) -> int:
        if not (0 <= t < self.T):
            raise ProvenanceError(f"timestamp {t} outside episode {self.episode_id} (T={self.T})")
        return int(self.grid[t, cell[0], cell[1]])


@dataclass
class Row:
    """One provenance-complete observation. Everything the contract requires, carried with the number itself."""
    world_id: str
    episode_id: str
    sources: tuple                   # ((cell, lag, source_timestamp, value), ...)
    out_cell: tuple
    out_t: int
    out_value: int
    window: tuple                    # (0, T)
    context: tuple
    valid: bool
    key: tuple = field(default=())   # the feature vector, in the frozen feature order


# ------------------------------------------------------------------ running episodes
def run_episode(world, world_id, episode_id, clamp, T, context=()) -> Episode:
    """A SUSTAINED regime. The window is requested explicitly and honoured explicitly."""
    g, _ = world.trace(clamp or None, hold=T, steps=T)
    if g.shape[0] != T:
        raise ProvenanceError(f"episode {episode_id}: asked for {T} samples, received {g.shape[0]}. "
                              f"A window that silently truncates is a window that fabricates history.")
    ep = Episode(world_id, episode_id, dict(clamp or {}), T, T, g, tuple(context), "sustained")
    for c, v in (clamp or {}).items():                 # NON-VACUITY: the clamp must actually have taken
        held = g[:, c[0], c[1]]
        if not np.all(held == v):
            raise ProvenanceError(f"episode {episode_id}: clamp {c} -> {v} DID NOT TAKE "
                                  f"(observed {sorted(set(held.tolist()))}). An intervention that did not happen "
                                  f"is not evidence.")
    return ep


def pulse_episode(world, world_id, episode_id, cell, value, at, T, bg=None) -> Episode:
    g = world.pulse_at(cell, value, at, T, bg=bg or None)
    if g.shape[0] != T:
        raise ProvenanceError(f"pulse episode {episode_id}: asked for {T} samples, received {g.shape[0]}")
    if int(g[at, cell[0], cell[1]]) != value:
        raise ProvenanceError(f"pulse episode {episode_id}: the pulse on {cell} did not take")
    return Episode(world_id, episode_id, {cell: value}, 1, T, g, (), "pulse", at)


def required_window(max_lag: int, period: int, settle_margin: int, response: int = 0) -> int:
    """The window must be long enough for the LONGEST inferred lag, plus settle, plus response, plus at least one
    full period of samples that are actually usable. D-067's window was fixed at 96 with a settle margin of 32,
    while the clock's lag to the far channel was 47: fifteen of every sixty-four sampled steps had no history at
    all, and were given one anyway."""
    return int(settle_margin + max_lag + response + 2 * period + 4)


# ------------------------------------------------------------------ extraction, with the pairing verified
def extract(ep: Episode, feats, out_cell, t_lo: int, t_hi: int) -> dict:
    """Build provenance-complete rows. A row whose history does not exist inside THIS episode is EXCLUDED and
    COUNTED -- never padded, never wrapped, never quietly dropped."""
    rows, n_excluded = [], 0
    for t in range(t_lo, min(t_hi, ep.T)):
        ok = all((t - d) >= 0 and (t - d) < ep.T for (_s, d) in feats)
        if not ok:
            n_excluded += 1
            continue
        srcs, key = [], []
        for (s, d) in feats:
            i = _idx(t, d, ep.T)                       # refuses rather than wraps
            v = ep.sample(s, i)
            srcs.append((s, d, i, v))
            key.append(v)
        rows.append(Row(ep.world_id, ep.episode_id, tuple(srcs), tuple(out_cell), t,
                        ep.sample(out_cell, t), (0, ep.T), ep.context, True, tuple(key)))
    return {"rows": rows, "n_excluded": n_excluded, "n_total": max(0, min(t_hi, ep.T) - t_lo)}


def assert_rows_valid(rows, episodes: dict):
    """THE ASSERTION THAT WAS MISSING. Re-read every claimed source sample FROM THE EPISODE, at the exact timestamp
    the row says it came from, and require byte-equality. Also re-read the output. The pair is verified, not the
    output alone."""
    for r in rows:
        ep = episodes[r.episode_id]
        if ep.world_id != r.world_id:
            raise ProvenanceError(f"row crosses worlds: {r.world_id} vs {ep.world_id}")
        for (s, d, ts, v) in r.sources:
            if ts != r.out_t - d:
                raise ProvenanceError(f"row claims source timestamp {ts} for lag {d} at output time {r.out_t}; "
                                      f"the arithmetic does not close")
            if not (0 <= ts < ep.T):
                raise ProvenanceError(f"source timestamp {ts} outside its own episode (T={ep.T})")
            if ep.sample(s, ts) != v:
                raise ProvenanceError(
                    f"FABRICATED HISTORY: row says source {s} held {v} at t={ts} in episode {r.episode_id}, "
                    f"but the episode says {ep.sample(s, ts)}. This is the D-067 defect, caught.")
        if ep.sample(r.out_cell, r.out_t) != r.out_value:
            raise ProvenanceError(f"output value does not match its own episode at t={r.out_t}")
    return True


def coverage_report(rows, n_feats) -> dict:
    seen = {}
    for r in rows:
        seen.setdefault(r.key, set()).add(r.out_value)
    return {"observed": seen, "n_observed": len(seen), "n_possible": 1 << n_feats,
            "coverage": len(seen) / (1 << n_feats),
            "ambiguous": {k: v for k, v in seen.items() if len(v) > 1}}
