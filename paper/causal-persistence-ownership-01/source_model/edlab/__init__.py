"""Emergent Dynamics Lab: falsifiable mesoscopic regime discovery."""

from .specs import DetectionSpec, LawSpec, PhenotypeSpec, RunSpec, TrackerSpec, WorldSpec
from .state import ParticleState

__all__ = [
    "DetectionSpec",
    "LawSpec",
    "ParticleState",
    "PhenotypeSpec",
    "RunSpec",
    "TrackerSpec",
    "WorldSpec",
]

__version__ = "0.1.0"

