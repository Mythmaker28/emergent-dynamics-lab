"""Particle state containers. IDs are diagnostic data, never physics inputs."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class ParticleState:
    positions: np.ndarray
    velocities: np.ndarray
    types: np.ndarray
    ids: np.ndarray

    def __post_init__(self) -> None:
        self.positions = np.asarray(self.positions, dtype=np.float64)
        self.velocities = np.asarray(self.velocities, dtype=np.float64)
        self.types = np.asarray(self.types, dtype=np.int64)
        self.ids = np.asarray(self.ids, dtype=np.int64)
        n = self.positions.shape[0]
        if self.positions.shape != (n, 2) or self.velocities.shape != (n, 2):
            raise ValueError("positions and velocities must have shape (n, 2)")
        if self.types.shape != (n,) or self.ids.shape != (n,):
            raise ValueError("types and ids must have shape (n,)")
        if len(np.unique(self.ids)) != n:
            raise ValueError("diagnostic particle IDs must be unique")
        if not np.isfinite(self.positions).all() or not np.isfinite(self.velocities).all():
            raise ValueError("physical state must be finite")

    def copy(self) -> "ParticleState":
        return ParticleState(
            self.positions.copy(),
            self.velocities.copy(),
            self.types.copy(),
            self.ids.copy(),
        )

    def physical_arrays(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return physical arrays only; intentionally excludes IDs."""

        return self.positions, self.velocities, self.types

