"""Minimal genuinely OPEN motile polar-field substrate (EXP-MO-00).

Fields on a periodic LxL lattice:
  rho     active material density
  p=(py,px) INTERNAL VECTOR POLARITY FIELD -- it causally DRIVES transport: v = v0 * p
  R       nutrient, fed spatially homogeneously
  C       passive origin cohorts partitioning rho (sum_c C == rho, exactly, at every step)

Openness: nutrient is fed homogeneously (F*(R0-R)); active material is created by local growth g0*rho*R
(consuming R) and destroyed by homogeneous removal k*rho. Both feed and removal are spatially homogeneous in form
and DETECTOR-INDEPENDENT: no term anywhere references a detected entity.

Exact controlled (closed) limit: F = g0 = k = 0  ->  total rho is conserved (advection and diffusion are
mass-conserving), i.e. no source and no sink.

Passive tracers: C is transported by exactly the same operators as rho and NEVER influences rho, p or R.

WHY ALIGNMENT (J) IS ZERO -- this is a REMOVAL, not a rescue.
A Vicsek-like local alignment term REGENERATES coherent polarity from a disordered state. A substrate that
re-creates the organization on its own makes GATE-0 untestable by construction: a scrambled cargo simply re-coheres
and behaves like the intact one (measured directly during qualification: an incoherent seed recovered polar order
0.71 within the run). We therefore FREEZE J = 0. Polarity is then transported with the material and its MAGNITUDE
relaxes to sqrt(a/b) along whatever direction is already there -- the Landau term is direction-neutral (p = 0 stays
p = 0 exactly), so it can amplify an existing orientation but can never create one. Coherent orientation becomes a
quantity that can only be inherited or destroyed, never spontaneously rebuilt. That is precisely what "load-bearing
organization" requires, and it is achieved by taking a mechanism AWAY.

Consequence, which is the point of the whole substrate: material entering by growth carries no orientation of its
own; it is diluted into the local polarity and then re-amplified along the existing direction. New constituents
INHERIT the structure's orientation. Organization persists across complete constituent turnover -- or it does not,
and the substrate dies at GATE-0.

No evolution. No parameter localization. No rescue mechanisms.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..reaction_diffusion.engine import TracerSpec


@dataclass(frozen=True)
class MotilePolarSpec:
    size: int = 64
    dt: float = 1.0
    D_rho: float = 0.06       # active-material diffusion
    D_R: float = 0.20         # nutrient diffusion (explicit 5-point stability: D*dt <= 0.25)
    v0: float = 0.55          # polarity -> velocity coupling (transport is DRIVEN by p)
    J: float = 0.00           # polar ALIGNMENT. FROZEN AT ZERO -- see note below.
    a: float = 0.50           # |p| -> sqrt(a/b) (self-propulsion magnitude)
    b: float = 0.50
    F: float = 0.030          # HOMOGENEOUS nutrient feed
    R0: float = 1.0
    g0: float = 0.25          # growth: rho gains g0*rho*R, consuming R
    k: float = 0.060          # HOMOGENEOUS removal of rho

    @property
    def is_closed(self) -> bool:
        return self.F == 0.0 and self.g0 == 0.0 and self.k == 0.0


@dataclass
class MPState:
    rho: np.ndarray          # (H,W)
    py: np.ndarray           # (H,W)
    px: np.ndarray           # (H,W)
    R: np.ndarray            # (H,W)
    C: np.ndarray            # (n_cohorts,H,W), sum over axis 0 == rho
    step: int = 0

    def copy(self) -> "MPState":
        return MPState(self.rho.copy(), self.py.copy(), self.px.copy(), self.R.copy(), self.C.copy(), self.step)


def laplacian(X: np.ndarray) -> np.ndarray:
    return (np.roll(X, 1, -2) + np.roll(X, -1, -2) + np.roll(X, 1, -1) + np.roll(X, -1, -1) - 4.0 * X)


def _box_smooth(X: np.ndarray) -> np.ndarray:
    out = np.zeros_like(X)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            out += np.roll(np.roll(X, dy, -2), dx, -1)
    return out / 9.0


def advect(fields: np.ndarray, vy: np.ndarray, vx: np.ndarray, dt: float) -> np.ndarray:
    """Mass-conserving forward-bilinear scatter. IDENTICAL weights for every field in `fields` (K,H,W),
    so rho, all passive cohorts and the polar momentum are transported by exactly the same operator."""
    n = fields.shape[-1]
    ys, xs = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    ty = ys + vy * dt
    tx = xs + vx * dt
    y0 = np.floor(ty).astype(np.int64)
    x0 = np.floor(tx).astype(np.int64)
    fy = ty - y0
    fx = tx - x0
    out = np.zeros_like(fields)
    for dy, wy in ((0, 1.0 - fy), (1, fy)):
        for dx, wx in ((0, 1.0 - fx), (1, fx)):
            w = wy * wx
            yy = (y0 + dy) % n
            xx = (x0 + dx) % n
            np.add.at(out, (slice(None), yy, xx), fields * w[None, :, :])
    return out


class MotilePolarEngine:
    def __init__(self, spec: MotilePolarSpec, tracer: TracerSpec):
        self.spec = spec
        self.tracer = tracer

    def step(self, s: MPState) -> MPState:
        sp = self.spec
        dt = sp.dt
        eps = 1e-12
        rho, py, px, R, C = s.rho, s.py, s.px, s.R, s.C

        # (1) POLARITY: local alignment + Landau relaxation to |p| = sqrt(a/b). Depends on rho and p only.
        wsum = _box_smooth(rho) + eps
        pby = _box_smooth(rho * py) / wsum
        pbx = _box_smooth(rho * px) / wsum
        p2 = py * py + px * px
        py = py + dt * (sp.J * (pby - py) + (sp.a - sp.b * p2) * py)
        px = px + dt * (sp.J * (pbx - px) + (sp.a - sp.b * p2) * px)
        alive = rho > 1e-6
        py = np.where(alive, py, 0.0)
        px = np.where(alive, px, 0.0)

        # (2) TRANSPORT DRIVEN BY POLARITY: v = v0 * p. rho, ALL cohorts and momentum share the same weights.
        vy = sp.v0 * py
        vx = sp.v0 * px
        stack = np.concatenate([rho[None], C, (rho * py)[None], (rho * px)[None]], axis=0)
        adv = advect(stack, vy, vx, dt)
        rho = adv[0]
        C = adv[1:1 + C.shape[0]]
        my, mx = adv[-2], adv[-1]
        safe = rho > 1e-9
        py = np.where(safe, my / np.where(safe, rho, 1.0), 0.0)
        px = np.where(safe, mx / np.where(safe, rho, 1.0), 0.0)

        # (3) DIFFUSION: identical operator on rho and every cohort (keeps sum_c C == rho exactly).
        lap_rho = laplacian(rho)
        rho = rho + dt * sp.D_rho * lap_rho
        C = C + dt * sp.D_rho * laplacian(C)
        R = R + dt * sp.D_R * laplacian(R)

        # (4) GROWTH from nutrient -> new mass enters the ACTIVE TEMPORAL COHORT (pulse-chase).
        g = np.clip(dt * sp.g0 * rho * R, 0.0, np.maximum(R, 0.0))
        R = R - g
        rho = rho + g
        C[self.tracer.active_feed_cohort(s.step)] += g

        # (5) HOMOGENEOUS REMOVAL: removes LOCAL cohort proportions (scales every cohort equally).
        keep = 1.0 - dt * sp.k
        rho = rho * keep
        C = C * keep

        # (6) HOMOGENEOUS NUTRIENT FEED (detector-independent, spatially uniform in form).
        R = R + dt * sp.F * (sp.R0 - R)

        return MPState(rho, py, px, R, C, s.step + 1)

    def simulate(self, s: MPState, steps: int, cadence: int) -> list[MPState]:
        out = [s.copy()]
        cur = s
        for t in range(1, steps + 1):
            cur = self.step(cur)
            if t % cadence == 0:
                out.append(cur.copy())
        return out
