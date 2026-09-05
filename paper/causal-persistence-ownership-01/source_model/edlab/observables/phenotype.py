"""ID-independent mesoscopic phenotype descriptors and similarity P(tau)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..specs import PhenotypeSpec, WorldSpec
from ..state import ParticleState
from ..substrates.particle_dynamics.engine import minimum_image


@dataclass(frozen=True)
class Phenotype:
    feature_names: tuple[str, ...]
    vector: np.ndarray
    raw: dict[str, float | list[float]]

    def __post_init__(self) -> None:
        vector = np.array(self.vector, dtype=np.float64, copy=True)
        if vector.shape != (len(self.feature_names),):
            raise ValueError("feature names and vector length disagree")
        if not np.isfinite(vector).all():
            raise ValueError("phenotype vector must be finite")
        vector.setflags(write=False)
        object.__setattr__(self, "vector", vector)


def compute_phenotype(
    state: ParticleState,
    indices: np.ndarray,
    *,
    centroid: np.ndarray,
    world: WorldSpec,
    spec: PhenotypeSpec,
) -> Phenotype:
    """Compute a compact dimensionless descriptor panel.

    The panel contains particle count fraction, type fractions, periodic shape
    statistics, center velocity, velocity dispersion, and signed internal
    circulation. It is invariant to particle IDs and global translation. It is
    not claimed to be invariant to rotation because center velocity components
    are retained explicitly.
    """

    relative = minimum_image(state.positions[indices] - centroid, world.box_size)
    velocities = state.velocities[indices]
    count = len(indices)
    count_fraction = count / world.n_particles

    type_counts = np.bincount(state.types[indices], minlength=world.n_types).astype(float)
    type_fractions = type_counts / count

    covariance = (relative.T @ relative) / count
    eigenvalues = np.maximum(np.linalg.eigvalsh(covariance), 0.0)
    radius_gyration = float(np.sqrt(eigenvalues.sum()))
    anisotropy = float((eigenvalues[-1] - eigenvalues[0]) / (eigenvalues.sum() + 1e-15))
    radii = np.sqrt(np.sum(relative * relative, axis=1))
    radial_quantiles = np.quantile(radii, [0.25, 0.5, 0.75])

    center_velocity = velocities.mean(axis=0)
    relative_velocity = velocities - center_velocity
    velocity_dispersion = float(np.sqrt(np.mean(np.sum(relative_velocity**2, axis=1))))
    circulation = float(
        np.mean(relative[:, 0] * relative_velocity[:, 1] - relative[:, 1] * relative_velocity[:, 0])
        / (spec.length_scale * spec.speed_scale)
    )

    names = (
        "count_fraction",
        *(f"type_fraction_{index}" for index in range(world.n_types)),
        "radius_gyration_scaled",
        "anisotropy",
        "radial_q25_scaled",
        "radial_q50_scaled",
        "radial_q75_scaled",
        "center_velocity_x_scaled",
        "center_velocity_y_scaled",
        "velocity_dispersion_scaled",
        "internal_circulation_scaled",
    )
    vector = np.array(
        [
            count_fraction,
            *type_fractions.tolist(),
            radius_gyration / spec.length_scale,
            anisotropy,
            *(radial_quantiles / spec.length_scale).tolist(),
            *(center_velocity / spec.speed_scale).tolist(),
            velocity_dispersion / spec.speed_scale,
            circulation,
        ],
        dtype=np.float64,
    )
    raw: dict[str, float | list[float]] = {
        "particle_count": float(count),
        "type_counts": type_counts.tolist(),
        "radius_gyration": radius_gyration,
        "covariance_eigenvalues": eigenvalues.tolist(),
        "anisotropy": anisotropy,
        "radial_quantiles": radial_quantiles.tolist(),
        "center_velocity": center_velocity.tolist(),
        "velocity_dispersion": velocity_dispersion,
        "internal_circulation": circulation,
    }
    return Phenotype(names, vector, raw)


def phenotype_similarity(left: Phenotype, right: Phenotype) -> float:
    """Dimensionless RMS-kernel similarity P in (0, 1]."""

    if left.feature_names != right.feature_names:
        raise ValueError("phenotype schemas differ")
    rms_distance = float(np.sqrt(np.mean((left.vector - right.vector) ** 2)))
    return float(np.exp(-rms_distance))

