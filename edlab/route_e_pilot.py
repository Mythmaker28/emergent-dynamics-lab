"""ROUTE_E_PILOT_READINESS_AND_FEASIBILITY_00 -- pilot protocol.

WHAT THIS IS, AND WHAT IT IS NOT
--------------------------------
This module freezes an EXPLORATORY, NON-CONFIRMATORY pilot.  Its purpose is to find
out whether the frozen Route E instrument can produce an answer at all, BEFORE the
confirmatory ``67 x 2`` design is preregistered.  It answers six questions:

  1. how often, and why, a draw carries no eligible component;
  2. what the residual distribution actually looks like;
  3. whether the frozen conventions ``{0.01, 0.05, 0.20}`` are reachable;
  4. how the lattice size changes the answer;
  5. how much the answer depends on the initial condition;
  6. how much the UNION cohort differs from a component-FOCAL cohort.

It CANNOT produce ``k``, cannot evaluate the ``42 / 9`` thresholds, cannot conclude
POSITIVE or NEGATIVE, and cannot contribute one unit to any confirmatory dataset.
Those are mechanical properties enforced here and tested in
``tests/test_route_e_pilot_readiness_00.py``, not promises.

THE PILOT IS NOT A CONFIRMATORY RUN IN MINIATURE
------------------------------------------------
The confirmatory design draws the lattice size at random per law.  The pilot ASSIGNS
it, eight laws per size, so that the size effect is measurable at all with 24 laws.
That makes the pilot total NOT a single binomial sample: the strata may have
different success probabilities and the stratum sizes are fixed by design, not drawn.
Raw counts per stratum are therefore the primary report, and any pooled figure is a
descriptive summary with no coverage guarantee.  This is stated here so that no later
reader can mistake the pilot for a small confirmatory family.

NO BEACON, AND WHY THAT IS SOUND HERE
-------------------------------------
The public randomness beacon exists to prove that the seed could not have been chosen
after seeing an outcome.  A pilot that can produce no claim has no outcome to choose
between, so the beacon protects nothing here.  What DOES protect the pilot is the
no-reroll rule below: the manifest and the exact 48-world inventory are written and
hashed BEFORE the first world, the seed is a pure function of that hash, and every
result -- ugly, null or broken -- is kept.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .substrates.lattice_bond import future_route_e_pre_run_frame as _frame

__all__ = [
    "PILOT_MISSION",
    "PILOT_LABEL",
    "PILOT_NAMESPACE_PREFIX",
    "PILOT_MANIFEST_KIND",
    "PILOT_PROVENANCE_KIND",
    "PILOT_PROVENANCE_TAG",
    "PILOT_PRE_RUN_DOMAIN",
    "PILOT_SEED_DOMAIN",
    "PILOT_LAWS",
    "PILOT_INITIAL_CONDITIONS_PER_LAW",
    "PILOT_WORLDS",
    "PILOT_LAWS_PER_SIZE",
    "PILOT_LATTICE_SIZES",
    "PILOT_DISPOSITIONS",
    "FORBIDDEN_PILOT_FIELDS",
    "PilotRefusal",
    "PilotWorld",
    "PilotPlan",
    "canonical_bytes",
    "sha256_hex",
    "build_pilot_manifest",
    "pilot_pre_run_root",
    "pilot_seed_root",
    "build_pilot_plan",
    "check_pilot_manifest",
]

PILOT_MISSION = "ROUTE_E_PILOT_READINESS_AND_FEASIBILITY_00"
PILOT_LABEL = "ROUTE_E_PILOT_FEASIBILITY_00"
PILOT_NAMESPACE_PREFIX = "PILOT-"
PILOT_MANIFEST_KIND = "route-e-pilot-manifest/v1"
PILOT_PROVENANCE_KIND = "route-e-pilot-provenance/v1"
PILOT_PROVENANCE_TAG = "ROUTE_E_PILOT_EXPLORATORY/v1"

PILOT_PRE_RUN_DOMAIN = b"EDLAB/ROUTE-E/PILOT-PRE-RUN/v1\x00"
PILOT_SEED_DOMAIN = b"EDLAB/ROUTE-E/PILOT-SEED/v1\x00"

#: 24 laws, two independent initial conditions each, 48 worlds, eight laws per size.
#: 24 is not a statistical accident.  A pilot of 12 has a worst-case two-sided 95%
#: Clopper-Pearson half-width of 0.289, which cannot separate an ineligibility fraction
#: near 0.5 from one near 0.2; at 24 the worst case is 0.209.  It is still DESCRIPTIVE:
#: 13/24 does NOT establish p > 0.50 (18/24 would), and no decision rule is attached.
PILOT_LAWS = 24
PILOT_INITIAL_CONDITIONS_PER_LAW = 2
PILOT_WORLDS = PILOT_LAWS * PILOT_INITIAL_CONDITIONS_PER_LAW
PILOT_LATTICE_SIZES: tuple[int, ...] = _frame.LATTICE_SIZES
PILOT_LAWS_PER_SIZE = PILOT_LAWS // len(PILOT_LATTICE_SIZES)

#: The ONLY dispositions a pilot may reach.  POSITIVE and NEGATIVE are absent by
#: construction, not by convention.
PILOT_DISPOSITIONS: tuple[str, ...] = (
    "PILOT_INSTRUMENT_RESPONSIVE",
    "PILOT_DESIGN_RISK_OBSERVED",
    "PILOT_INCONCLUSIVE",
    "PILOT_TECHNICAL_LIMITED",
    "PILOT_TECHNICAL_INVALID",
)

#: Anything that would make the pilot a claim.  Refused as a key name and as a string
#: value, at any depth of the manifest.
FORBIDDEN_PILOT_FIELDS: frozenset[str] = frozenset(
    {
        "k",
        "confirmatory",
        "confirmatory_k",
        "positive",
        "negative",
        "verdict",
        "result",
        "outcome",
        "y",
        "Y",
        "threshold_42",
        "threshold_9",
        "beacon",
        "randomness",
        "round",
        "preregistration",
        "seed",
        "seed_root",
        "draw_plan",
        "law_fields",
        "initial_conditions",
        "measurement_root",
        "join_digest",
    }
)


class PilotRefusal(ValueError):
    """A refusal carrying a reason code.  Never a bare KeyError or ValueError."""

    def __init__(self, message: str, *, reason_code: str) -> None:
        super().__init__(f"[{reason_code}] {message}")
        self.reason_code = reason_code


def canonical_bytes(value: Any) -> bytes:
    """The one canonical encoding, byte-identical to the Route E protocol's."""
    return json.dumps(
        value, allow_nan=False, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("ascii")


def sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class PilotWorld:
    """One world of the frozen inventory.  Written before the first engine step."""

    ordinal: int
    law_ordinal: int
    ic_ordinal: int
    lattice_size: int
    proposal_index: int
    ic_index: int

    def as_document(self) -> dict[str, Any]:
        return {
            "ic_index": int(self.ic_index),
            "ic_ordinal": int(self.ic_ordinal),
            "lattice_size": int(self.lattice_size),
            "law_ordinal": int(self.law_ordinal),
            "ordinal": int(self.ordinal),
            "proposal_index": int(self.proposal_index),
        }


@dataclass(frozen=True)
class PilotPlan:
    seed_root_sha256: str
    law_fields: tuple[Mapping[str, float], ...]
    proposal_indices: tuple[int, ...]
    proposals_consumed: int
    worlds: tuple[PilotWorld, ...]

    def inventory_document(self) -> dict[str, Any]:
        return {
            "kind": "route-e-pilot-inventory/v1",
            "proposals_consumed": int(self.proposals_consumed),
            "seed_root_sha256": self.seed_root_sha256,
            "worlds": [world.as_document() for world in self.worlds],
        }


def _scan_forbidden(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key) in FORBIDDEN_PILOT_FIELDS:
                raise PilotRefusal(
                    f"{path}.{key} is a forbidden pilot field: a pilot manifest may not "
                    "carry an answer, a seed, or any confirmatory term",
                    reason_code="PILOT_MANIFEST_FORBIDDEN_FIELD",
                )
            _scan_forbidden(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _scan_forbidden(item, f"{path}[{index}]")
    elif isinstance(value, str) and value in FORBIDDEN_PILOT_FIELDS:
        raise PilotRefusal(
            f"{path} carries the forbidden term {value!r} as a value",
            reason_code="PILOT_MANIFEST_FORBIDDEN_FIELD",
        )


#: The exact key set of a pilot manifest.  An unknown key is refused; a missing key is
#: refused.  There is no "at least these keys".
PILOT_MANIFEST_KEYS: frozenset[str] = frozenset(
    {
        "cadence_steps",
        "cohort_residual_conventions",
        "detector_and_tracker",
        "draw_uniform_mapping_version",
        "fixture_class",
        "horizon_steps",
        "initial_conditions_per_law",
        "kind",
        "label",
        "lattice_sizes",
        "laws",
        "laws_per_size",
        "mission",
        "no_reroll_policy",
        "output_namespace",
        "stratification",
        "worlds",
    }
)


def build_pilot_manifest(namespace: str) -> dict[str, Any]:
    """The complete pre-run manifest.  It binds no seed and no outcome, by construction."""
    if not isinstance(namespace, str) or not namespace.startswith(PILOT_NAMESPACE_PREFIX):
        raise PilotRefusal(
            f"the pilot namespace must start with {PILOT_NAMESPACE_PREFIX!r}",
            reason_code="PILOT_NAMESPACE_PREFIX",
        )
    manifest = {
        "cadence_steps": int(_frame.CADENCE_STEPS),
        "cohort_residual_conventions": [0.01, 0.05, 0.2],
        "detector_and_tracker": {
            "dilation_radius": 1,
            "matter_threshold": 0.45,
            "max_area_ratio": 3.0,
            "max_centroid_displacement": 3.0,
            "min_cells": 3,
            "unique_score_margin": 1e-12,
        },
        "draw_uniform_mapping_version": _frame.DRAW_UNIFORM_MAPPING_VERSION,
        "fixture_class": "PILOT_EXPLORATORY_NON_CONFIRMATORY",
        "horizon_steps": int(_frame.HORIZON_STEPS),
        "initial_conditions_per_law": PILOT_INITIAL_CONDITIONS_PER_LAW,
        "kind": PILOT_MANIFEST_KIND,
        "label": PILOT_LABEL,
        "lattice_sizes": [int(size) for size in PILOT_LATTICE_SIZES],
        "laws": PILOT_LAWS,
        "laws_per_size": PILOT_LAWS_PER_SIZE,
        "mission": PILOT_MISSION,
        "no_reroll_policy": (
            "the inventory of 48 worlds is written and hashed before the first engine "
            "step; no replacement, no retry, no top-up and no second seed is permitted; "
            "every result is kept, including empty, degenerate and crashed ones"
        ),
        "output_namespace": namespace,
        "stratification": (
            "lattice size is ASSIGNED, eight laws per size, not drawn; the pilot total "
            "is therefore not a single binomial sample and per-stratum raw counts are "
            "the primary report"
        ),
        "worlds": PILOT_WORLDS,
    }
    check_pilot_manifest(manifest)
    return manifest


def check_pilot_manifest(manifest: Mapping[str, Any]) -> None:
    """Exact key set, correct kind, forbidden-term scan, frozen shape."""
    if not isinstance(manifest, Mapping):
        raise PilotRefusal("the manifest is not a mapping", reason_code="PILOT_MANIFEST_SHAPE")
    observed = frozenset(str(key) for key in manifest)
    if observed != PILOT_MANIFEST_KEYS:
        missing = sorted(PILOT_MANIFEST_KEYS - observed)
        extra = sorted(observed - PILOT_MANIFEST_KEYS)
        raise PilotRefusal(
            f"manifest key set is wrong; missing {missing}, unexpected {extra}",
            reason_code="PILOT_MANIFEST_SHAPE",
        )
    if manifest["kind"] != PILOT_MANIFEST_KIND:
        raise PilotRefusal("manifest kind is not the pilot kind", reason_code="PILOT_MANIFEST_KIND")
    if manifest["draw_uniform_mapping_version"] != _frame.DRAW_UNIFORM_MAPPING_VERSION:
        raise PilotRefusal(
            "the manifest names a draw mapping version this build does not implement; "
            "no artefact is ever reinterpreted under a different mapping",
            reason_code="PILOT_MAPPING_VERSION",
        )
    if int(manifest["laws"]) != PILOT_LAWS or int(manifest["worlds"]) != PILOT_WORLDS:
        raise PilotRefusal("the pilot shape is frozen at 24 laws / 48 worlds",
                           reason_code="PILOT_SHAPE")
    if int(manifest["laws"]) == 67 or int(manifest["worlds"]) == 134:
        raise PilotRefusal("a pilot is never the confirmatory shape", reason_code="PILOT_SHAPE")
    namespace = manifest["output_namespace"]
    if not isinstance(namespace, str) or not namespace.startswith(PILOT_NAMESPACE_PREFIX):
        raise PilotRefusal(
            f"the pilot namespace must start with {PILOT_NAMESPACE_PREFIX!r}",
            reason_code="PILOT_NAMESPACE_PREFIX",
        )
    _scan_forbidden(manifest)


def pilot_pre_run_root(manifest: Mapping[str, Any]) -> str:
    """``P_pilot = SHA-256(domain || canonical_json(manifest))``.  No outcome enters it."""
    check_pilot_manifest(manifest)
    return sha256_hex(PILOT_PRE_RUN_DOMAIN + canonical_bytes(dict(manifest)))


def pilot_seed_root(pre_run_root: str, *, label: str = PILOT_LABEL) -> bytes:
    """``seed = SHA-256(domain || label || P_pilot)``.  A pure function of the manifest.

    No beacon, no wall clock, no caller-supplied entropy: there is nothing an operator
    could vary between two attempts without changing the manifest hash, and the manifest
    hash is committed before the first world.
    """
    if not isinstance(pre_run_root, str) or len(pre_run_root) != 64:
        raise PilotRefusal("pre_run_root must be a 64-character hex digest",
                           reason_code="PILOT_ROOT_SHAPE")
    bytes.fromhex(pre_run_root)
    if label != PILOT_LABEL:
        raise PilotRefusal("the pilot label is frozen", reason_code="PILOT_LABEL")
    return hashlib.sha256(
        PILOT_SEED_DOMAIN + label.encode("ascii") + b"\x00" + bytes.fromhex(pre_run_root)
    ).digest()


def build_pilot_plan(seed_root: bytes, *, laws: int = PILOT_LAWS) -> PilotPlan:
    """The complete 48-world inventory.  No engine step, no world, no outcome.

    Law proposals come from the SAME frozen sampler the confirmatory design uses --
    ``propose_law_fields`` gated by the design box and by the ENGINE's own construction --
    so the pilot samples the same population.  Only the seed domain differs, which is
    exactly what keeps the pilot's stream disjoint from any confirmatory stream.
    """
    if isinstance(laws, bool) or not isinstance(laws, int) or laws <= 0:
        raise PilotRefusal("laws must be a positive plain int", reason_code="PILOT_SHAPE")
    if laws % len(PILOT_LATTICE_SIZES) != 0:
        raise PilotRefusal(
            "the law count must divide evenly across the lattice sizes",
            reason_code="PILOT_STRATIFICATION",
        )
    indices, consumed = _frame.sample_law_indices(seed_root, laws)
    fields = tuple(_frame.propose_law_fields(seed_root, index) for index in indices)
    per_size = laws // len(PILOT_LATTICE_SIZES)
    worlds: list[PilotWorld] = []
    ordinal = 0
    for law_ordinal in range(laws):
        size = PILOT_LATTICE_SIZES[law_ordinal // per_size]
        for ic_ordinal in range(PILOT_INITIAL_CONDITIONS_PER_LAW):
            worlds.append(
                PilotWorld(
                    ordinal=ordinal,
                    law_ordinal=law_ordinal,
                    ic_ordinal=ic_ordinal,
                    lattice_size=int(size),
                    proposal_index=int(indices[law_ordinal]),
                    ic_index=2 * law_ordinal + ic_ordinal,
                )
            )
            ordinal += 1
    return PilotPlan(
        seed_root_sha256=sha256_hex(bytes(seed_root)),
        law_fields=fields,
        proposal_indices=indices,
        proposals_consumed=int(consumed),
        worlds=tuple(worlds),
    )


def schedule(horizon: int | None = None, cadence: int | None = None) -> tuple[int, ...]:
    """The frozen sampled-frame schedule, identical to the confirmatory one."""
    h = int(_frame.HORIZON_STEPS if horizon is None else horizon)
    c = int(_frame.CADENCE_STEPS if cadence is None else cadence)
    return tuple(range(0, h + 1, c))


def confirmatory_shape_refused(laws: int, worlds: int) -> bool:
    """True iff this shape is the confirmatory one, which a pilot may never adopt."""
    return int(laws) == 67 or int(worlds) == 134


def stratum_of(world: PilotWorld) -> str:
    return f"L{int(world.lattice_size)}"


def worlds_by_stratum(plan: PilotPlan) -> dict[str, tuple[int, ...]]:
    out: dict[str, list[int]] = {}
    for world in plan.worlds:
        out.setdefault(stratum_of(world), []).append(world.ordinal)
    return {key: tuple(value) for key, value in sorted(out.items())}


def declared_sequence(values: Sequence[float]) -> tuple[float, ...]:
    return tuple(float(value) for value in values)
