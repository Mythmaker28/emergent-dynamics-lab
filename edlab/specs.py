"""Explicit, serializable specifications for CORE V0."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

import numpy as np


@dataclass(frozen=True)
class LawSpec:
    """Local interaction law.

    ``interaction[a, b]`` is the signed response of a receiving particle of
    type ``a`` to a source particle of type ``b``. Positive values attract;
    negative values repel. The matrix may be asymmetric.
    """

    interaction: np.ndarray
    repulsion_strength: float = 1.5
    short_range: float = 0.035
    interaction_range: float = 0.18
    damping: float = 0.8

    def __post_init__(self) -> None:
        matrix = np.array(self.interaction, dtype=np.float64, copy=True)
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise ValueError("interaction must be a square matrix")
        if matrix.shape[0] < 1:
            raise ValueError("interaction must contain at least one type")
        if not np.isfinite(matrix).all():
            raise ValueError("interaction must contain finite values")
        scalar_values = (
            self.repulsion_strength,
            self.short_range,
            self.interaction_range,
            self.damping,
        )
        if not all(math.isfinite(value) for value in scalar_values):
            raise ValueError("LawSpec scalar values must be finite")
        if self.repulsion_strength <= 0:
            raise ValueError("repulsion_strength must be positive")
        if not 0 < self.short_range < self.interaction_range:
            raise ValueError("require 0 < short_range < interaction_range")
        if self.damping < 0:
            raise ValueError("damping must be non-negative")
        matrix.setflags(write=False)
        object.__setattr__(self, "interaction", matrix)

    @property
    def n_types(self) -> int:
        return int(self.interaction.shape[0])

    def as_dict(self) -> dict[str, Any]:
        return {
            "interaction": self.interaction.tolist(),
            "repulsion_strength": self.repulsion_strength,
            "short_range": self.short_range,
            "interaction_range": self.interaction_range,
            "damping": self.damping,
        }


@dataclass(frozen=True)
class WorldSpec:
    n_particles: int = 64
    n_types: int = 3
    box_size: float = 1.0
    initial_speed: float = 0.04

    def __post_init__(self) -> None:
        if not all(math.isfinite(value) for value in (self.box_size, self.initial_speed)):
            raise ValueError("WorldSpec scalar values must be finite")
        if self.n_particles < 2:
            raise ValueError("n_particles must be at least two")
        if self.n_types < 1:
            raise ValueError("n_types must be positive")
        if self.box_size <= 0:
            raise ValueError("box_size must be positive")
        if self.initial_speed < 0:
            raise ValueError("initial_speed must be non-negative")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RunSpec:
    seed: int
    dt: float = 0.02
    steps: int = 600
    snapshot_interval: int = 10
    backend: str = "vectorized"

    def __post_init__(self) -> None:
        if not math.isfinite(self.dt):
            raise ValueError("dt must be finite")
        if self.dt <= 0:
            raise ValueError("dt must be positive")
        if self.steps < 1:
            raise ValueError("steps must be positive")
        if self.snapshot_interval < 1:
            raise ValueError("snapshot_interval must be positive")
        if self.backend not in {"reference", "vectorized"}:
            raise ValueError("backend must be 'reference' or 'vectorized'")

    @property
    def simulated_time(self) -> float:
        return self.steps * self.dt

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["simulated_time"] = self.simulated_time
        return data


@dataclass(frozen=True)
class DetectionSpec:
    connection_radius: float = 0.11
    min_size: int = 4

    def __post_init__(self) -> None:
        if not math.isfinite(self.connection_radius):
            raise ValueError("connection_radius must be finite")
        if self.connection_radius <= 0:
            raise ValueError("connection_radius must be positive")
        if self.min_size < 2:
            raise ValueError("min_size must be at least two")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhenotypeSpec:
    length_scale: float = 0.11
    speed_scale: float = 0.25

    def __post_init__(self) -> None:
        if not all(math.isfinite(value) for value in (self.length_scale, self.speed_scale)):
            raise ValueError("phenotype scales must be finite")
        if self.length_scale <= 0 or self.speed_scale <= 0:
            raise ValueError("phenotype scales must be positive")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TrackerSpec:
    max_centroid_distance: float = 0.16
    min_size_ratio: float = 0.25

    def __post_init__(self) -> None:
        if not all(
            math.isfinite(value)
            for value in (self.max_centroid_distance, self.min_size_ratio)
        ):
            raise ValueError("tracker parameters must be finite")
        if self.max_centroid_distance <= 0:
            raise ValueError("max_centroid_distance must be positive")
        if not 0 <= self.min_size_ratio <= 1:
            raise ValueError("min_size_ratio must lie in [0, 1]")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
