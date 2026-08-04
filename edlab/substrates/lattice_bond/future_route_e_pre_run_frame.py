"""Route E pre-run closure: thresholds, draw machinery, sampler gate, break cause,
estimand ceiling and the fail-closed scientific entry point.

This module closes the six obligations carried forward by the accepted human review
``FUTURE_PROSPECTIVE_AXIS_CONVENTION_AND_FRAME_CLOSURE_01S_HUMAN_REVIEW.md``
(commit ``00afcdd1aacbdf32bb030d85ced735a2920421f6``).  It closes **nothing else**.

WHAT THIS MODULE IS NOT
-----------------------
It is not an experiment, a family, a runner or a result.  It creates no scientific
seed, no namespace, no ``LatticeBondSpec`` for any of the 67 draws, no initial
condition and no world.  Every function here is either a pure declaration, a pure
predicate, or a fail-closed refusal.  ``scientific_run_authorized`` is ``False`` and
this module contains no code path that can set it to ``True``.

WHAT IS FROZEN AND IS NOT RE-DERIVED HERE
-----------------------------------------
The 01S design is frozen and is restated verbatim, never recomputed: 67 law draws,
2 initial conditions per law, 134 worlds, square lattices in {16, 24, 32}, horizon
1024 steps, cadence 16 steps, POSITIVE at ``k >= 42``, NEGATIVE at ``k <= 9``,
INDETERMINATE otherwise, indifference region [0.25, 0.50], and the
``cohort_residual_fraction`` sensitivity set {0.01, 0.05, 0.20}.

THE STATISTICAL UNIT IS FROZEN
------------------------------
``Y_i = 1{D(law_i, L_i, X_i1) = 1}`` for ``i = 1..67`` and ``k = sum_i Y_i``.  The
FIRST initial condition serves the primary.  The SECOND serves the initial-condition
dependence discriminator ONLY.  The 134 worlds are an execution cost; they are never
134 observations.  Nothing in this module turns ``X_i2`` into a replication, an
exclusion ground, a substitute for ``X_i1``, or a best-of-two selector.

LIMITATION REGISTER
-------------------
RE-L1  The inter-initial-condition discriminator does NOT meet the package's own
       precision principle at the frozen ``n = 67``: its indifference width is 0.125,
       so the principle would require a worst-case 95% Clopper-Pearson half-width of
       at most 0.0625, and the achievable worst case at ``n = 67`` is 0.124721.  The
       sample size is frozen and may not be changed here.  The discriminator is
       therefore under-powered by that principle.  It is secondary, it never governs
       ``POSITIVE / NEGATIVE / INDETERMINATE``, and this limitation is declared rather
       than repaired.
RE-L2  ``run_owned_future_pipeline`` has no authorisation parameter and cannot be
       given one without modifying an accepted source, which the frozen allowlist
       forbids.  It is therefore DECLARED OUT OF PROTOCOL as a direct scientific
       entry point (the alternative closure the frozen PRB-5 text explicitly allows),
       and the refusal pinned by test is a refusal of the real public function before
       any effect, not an in-function authorisation check.
RE-L3  The equivalence between the engine's admissibility check and (B1) AND (B2) is
       exact in real arithmetic.  In IEEE-754 it can differ by at most the rounding of
       ``exp`` and the products near the boundary.  This module never gates on the
       algebraic predicate: the gate is the engine's own construction.  The algebraic
       predicate is computed only as a reported agreement statistic.
RE-L4  ``ASSOCIATION_GATE_TRACK_BREAK`` is a *cause label* attached to a terminal
       record.  It does not add a sixth lifecycle terminal state, it does not change
       any outcome, and it never removes a draw from the denominator.
RE-L5  The horizon-censoring attribution threshold is an attribution rule for a null.
       It does NOT change the ternary decision, whose cut points remain frozen.
RE-L6  The beacon round is specified as a rule over a future instant.  This module
       performs no network access whatsoever; the beacon bytes are an argument.
RE-L7  Closing the six obligations of this mission does NOT close the six frozen
       infrastructure blockers PRB-1..PRB-6 of the 01S decision.  Only PRB-5 is
       touched, and only by the refusal test of PRB-F.  PRB-1, PRB-2, PRB-3, PRB-4
       and PRB-6 remain open.
"""

from __future__ import annotations

import hashlib
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .engine import AdmissibilityError, LatticeBondSpec
from .instrumentation import AssociationEdge, TrackerSpec, TrackEvent, TrackingResult

__all__ = [
    "CLOSURE_VERSION",
    "SCHEMA_VERSION",
    # frozen 01S design
    "N_LAW_DRAWS",
    "INITIAL_CONDITIONS_PER_LAW",
    "WORLD_COUNT",
    "LATTICE_SIZES",
    "HORIZON_STEPS",
    "CADENCE_STEPS",
    "POSITIVE_MIN_K",
    "NEGATIVE_MAX_K",
    "DELTA_0",
    "DELTA_1",
    "COHORT_RESIDUAL_SENSITIVITY_SET",
    # PRB-A
    "HORIZON_CENSORING_ATTRIBUTION",
    "IC_DISCORDANCE",
    "ThresholdSpec",
    "clopper_pearson",
    "attribute_horizon_censoring",
    "classify_ic_dependence",
    # PRB-B
    "DRAW_GENERATOR",
    "BEACON_SOURCE",
    "DrawPlan",
    "derive_seed_root",
    "draw_block",
    "draw_uniform",
    "beacon_round_at_or_after",
    "build_draw_plan",
    # PRB-C
    "PROPOSAL_BOX",
    "propose_law_fields",
    "in_proposal_box",
    "engine_accepts",
    "algebraic_b1_b2",
    "sample_law_indices",
    # PRB-D
    "ASSOCIATION_GATE_BREAK_REASONS",
    "TrackTermination",
    "classify_track_terminations",
    # PRB-E
    "DELTA_DEFINITION",
    "CLAIM_CEILING",
    "FORBIDDEN_INFERENCES",
    "check_claim_within_ceiling",
    # PRB-F
    "OUT_OF_PROTOCOL_ENTRY_POINTS",
    "RouteEAuthorisation",
    "RouteEAuthorisationError",
    "open_route_e_scientific_run",
    "SCIENTIFIC_RUN_AUTHORIZED",
]

CLOSURE_VERSION = "1.0.0"
SCHEMA_VERSION = "future-route-e-pre-run-frame/v1"

# --------------------------------------------------------------------------------------
# Frozen 01S design.  Restated, never recomputed.  Changing any of these is out of scope
# for this mission and for the preregistration that follows it.
# --------------------------------------------------------------------------------------

N_LAW_DRAWS = 67
INITIAL_CONDITIONS_PER_LAW = 2
WORLD_COUNT = 134
LATTICE_SIZES: tuple[int, ...] = (16, 24, 32)
HORIZON_STEPS = 1024
CADENCE_STEPS = 16
POSITIVE_MIN_K = 42
NEGATIVE_MAX_K = 9
DELTA_0 = 0.50
DELTA_1 = 0.25
COHORT_RESIDUAL_SENSITIVITY_SET: tuple[float, ...] = (0.01, 0.05, 0.20)

SCIENTIFIC_RUN_AUTHORIZED = False


class RouteEAuthorisationError(RuntimeError):
    """Raised by the fail-closed scientific entry point.  Never caught internally."""


# --------------------------------------------------------------------------------------
# Exact Clopper-Pearson, dependency-free and deterministic.
#
# Implemented by bisecting the exact binomial tail computed from ``math.comb``, so the
# result does not depend on any third-party library being installed or on its version.
# --------------------------------------------------------------------------------------


def _binom_sf(k: int, n: int, p: float) -> float:
    """P(X >= k) for X ~ Binomial(n, p), exact terms, ascending summation."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    total = 0.0
    for i in range(k, n + 1):
        total += math.comb(n, i) * (p**i) * ((1.0 - p) ** (n - i))
    return min(1.0, total)


def _binom_cdf(k: int, n: int, p: float) -> float:
    """P(X <= k) for X ~ Binomial(n, p)."""
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    total = 0.0
    for i in range(0, k + 1):
        total += math.comb(n, i) * (p**i) * ((1.0 - p) ** (n - i))
    return min(1.0, total)


def _bisect(predicate: Callable[[float], bool], lo: float, hi: float) -> float:
    """Smallest p in [lo, hi] with ``predicate(p)`` true, by 200 halvings."""
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if predicate(mid):
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Exact two-sided ``1 - alpha`` Clopper-Pearson interval for ``k`` of ``n``.

    Fail-closed on every malformed input: no clamping, no silent default.
    """
    if not isinstance(k, int) or isinstance(k, bool):
        raise TypeError("k must be a plain int")
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("n must be a plain int")
    if n <= 0:
        raise ValueError("n must be positive")
    if not 0 <= k <= n:
        raise ValueError("k must lie in [0, n]")
    if not math.isfinite(alpha) or not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be finite and in (0,1)")
    half = 0.5 * alpha
    lower = 0.0 if k == 0 else _bisect(lambda p: _binom_sf(k, n, p) >= half, 0.0, 1.0)
    upper = 1.0 if k == n else _bisect(lambda p: _binom_cdf(k, n, p) <= half, 0.0, 1.0)
    return lower, upper


# --------------------------------------------------------------------------------------
# PRB-A.  The two thresholds Route E left unquantified.
#
# The accepted human review names them literally, in limitation A16 / B16:
#   "Deux seuils de Route E ne sont pas chiffres : la fraction de censure et la
#    concordance inter-CI.  Ils ne gouvernent PAS la decision POSITIF/NEGATIF/
#    INDETERMINE mais l'attribution de cause d'un nul, et les deux fractions
#    concernees sont co-primaires obligatoires.  De plus le repere de concordance
#    propose est biaise au sens de Jensen vers 'pas de dependance aux CI'."
#
# Neither value below consults any closed scientific result.  Each is derived either
# from frozen arithmetic already in the design, or from the design's own declared
# midpoint-of-identifiability convention applied to the discriminator's own range.
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class ThresholdSpec:
    """A prospective threshold, complete enough that it cannot be re-argued later."""

    name: str
    role: str
    quantity: str
    unit: str
    domain: tuple[float, float]
    value: float
    comparison: str  # "strictly_greater" | "strictly_less"
    boundary_behaviour: str
    non_finite_behaviour: str
    derivation: str
    governs_ternary_decision: bool

    def __post_init__(self) -> None:
        if not math.isfinite(self.value):
            raise ValueError("threshold value must be finite")
        low, high = self.domain
        if not (math.isfinite(low) and math.isfinite(high)) or not low < high:
            raise ValueError("threshold domain must be a finite non-degenerate interval")
        if not low <= self.value <= high:
            raise ValueError("threshold value must lie in its declared domain")
        if self.comparison not in ("strictly_greater", "strictly_less"):
            raise ValueError("comparison must be strictly_greater or strictly_less")
        if self.governs_ternary_decision:
            raise ValueError(
                "no threshold introduced by this closure may govern the frozen ternary decision"
            )

    def digest(self) -> str:
        payload = "|".join(
            (
                self.name,
                self.quantity,
                self.unit,
                repr(self.domain),
                repr(self.value),
                self.comparison,
                self.boundary_behaviour,
                self.non_finite_behaviour,
            )
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# --- Threshold 1: the censoring fraction ------------------------------------------------
#
# Derivation, purely arithmetic, from the FROZEN positive cut:
#   A draw that never reaches verified replacement before the horizon scores 0.
#   With C such draws among n = 67, necessarily k <= 67 - C.
#   POSITIVE requires k >= 42.  POSITIVE is therefore arithmetically unreachable
#   exactly when 67 - C < 42, i.e. C > 25, i.e. C >= 26, i.e. C/67 > 25/67.
#   Nothing else enters.  No scientific observation is consulted.

HORIZON_CENSORING_ATTRIBUTION = ThresholdSpec(
    name="HORIZON_CENSORING_ATTRIBUTION",
    role=(
        "attribution of cause for a null result; reported unconditionally as a mandatory "
        "co-primary; never an exclusion and never a decision cut"
    ),
    quantity=(
        "fraction of the 67 primary draws whose eligible component never reaches verified "
        "material replacement before step 1024 (right-censored on turnover)"
    ),
    unit="dimensionless fraction, count of censored primary draws divided by 67",
    domain=(0.0, 1.0),
    value=25.0 / 67.0,
    comparison="strictly_greater",
    boundary_behaviour=(
        "STRICT.  A fraction exactly equal to 25/67 is NOT attributed: at C = 25 the "
        "POSITIVE arm remains arithmetically reachable at k = 42."
    ),
    non_finite_behaviour=(
        "fail-closed.  NaN, +inf, -inf, a negative count, a non-integer count or a count "
        "above 67 raises; no value is clamped, defaulted or silently coerced."
    ),
    derivation=(
        "k <= 67 - C and POSITIVE requires k >= 42, so POSITIVE is unreachable iff C > 25. "
        "Uses only the frozen n = 67 and the frozen cut k >= 42."
    ),
    governs_ternary_decision=False,
)

# --- Threshold 2: the inter-initial-condition discriminator ------------------------------
#
# The Jensen bias A16 identifies comes from comparing observed concordance against a
# benchmark built by plugging the MARGINAL estimate into pi^2 + (1-pi)^2, because
# E[pi^2 + (1-pi)^2] >= Delta^2 + (1-Delta)^2 by convexity.  The repair is to stop using a
# benchmark at all and to estimate the discordance probability DIRECTLY:
#
#   psi = P(Y_i1 != Y_i2) = E[ 2 pi_i (1 - pi_i) ],   psi in [0, 1/2]
#
# d / 67, with d the number of discordant law-pairs, is an exactly unbiased estimator of
# psi under the declared draw distribution.  No convexity step is taken, so no Jensen bias
# survives.  psi = 0 means the outcome is a function of (law, size) alone; psi = 1/2 is
# maximal within-law initial-condition noise (pi identically 1/2).
#
# Boundaries: the SAME declared midpoint-of-identifiability convention the package already
# froze for Delta, applied to psi's own identifiable range [0, 1/2]:
#   psi_0 = midpoint of [0, 1/2]   = 1/4     (material initial-condition dependence)
#   psi_1 = midpoint of [0, 1/4]   = 1/8     (negligible initial-condition dependence)

IC_DISCORDANCE = ThresholdSpec(
    name="IC_DISCORDANCE",
    role=(
        "attribution of cause for a null result: whether the outcome depends on the "
        "initial condition within a law; never a decision cut and never an exclusion"
    ),
    quantity=(
        "psi = P(Y_i1 != Y_i2), the probability that a law's two independent initial "
        "conditions disagree; estimated without bias by d/67 where d counts discordant "
        "law-pairs"
    ),
    unit="dimensionless probability",
    domain=(0.0, 0.5),
    value=0.25,
    comparison="strictly_greater",
    boundary_behaviour=(
        "STRICT on the exact 95% Clopper-Pearson bounds.  MATERIAL iff CP lower(d,67) > "
        "0.25; NEGLIGIBLE iff CP upper(d,67) < 0.125; INDETERMINATE otherwise.  A bound "
        "landing exactly on 0.25 or on 0.125 falls to INDETERMINATE."
    ),
    non_finite_behaviour=(
        "fail-closed.  d must be a plain int in [0, 67]; anything else raises."
    ),
    derivation=(
        "psi ranges over [0, 1/2] by construction (2 pi (1-pi) is maximised at pi = 1/2). "
        "The frozen midpoint-of-identifiability convention gives psi_0 = 1/4 and, applied "
        "again to [0, 1/4], psi_1 = 1/8.  No scientific observation is consulted."
    ),
    governs_ternary_decision=False,
)

IC_DISCORDANCE_NEGLIGIBLE_BOUND = 0.125


def attribute_horizon_censoring(censored_draws: int) -> str:
    """Attribute (or refuse to attribute) a null to horizon censoring.

    Returns ``HORIZON_CENSORING_SUFFICIENT`` when censoring alone already forecloses the
    POSITIVE arm, ``HORIZON_CENSORING_NOT_SUFFICIENT`` otherwise.  Never returns a
    decision; the ternary decision is frozen and is computed elsewhere from ``k``.
    """
    if isinstance(censored_draws, bool) or not isinstance(censored_draws, int):
        raise TypeError("censored_draws must be a plain int")
    if not 0 <= censored_draws <= N_LAW_DRAWS:
        raise ValueError("censored_draws must lie in [0, 67]")
    fraction = censored_draws / N_LAW_DRAWS
    if not math.isfinite(fraction):  # unreachable by construction; kept fail-closed
        raise ValueError("censoring fraction must be finite")
    if fraction > HORIZON_CENSORING_ATTRIBUTION.value:
        return "HORIZON_CENSORING_SUFFICIENT"
    return "HORIZON_CENSORING_NOT_SUFFICIENT"


def classify_ic_dependence(discordant_pairs: int) -> str:
    """Ternary attribution for the inter-initial-condition discriminator.

    One of ``IC_DEPENDENCE_MATERIAL``, ``IC_DEPENDENCE_NEGLIGIBLE``,
    ``IC_DEPENDENCE_INDETERMINATE``.  Never touches ``k`` and never removes a law from
    the denominator: a law is in the denominator because of ``X_i1``, and ``X_i2``
    cannot take it out.
    """
    if isinstance(discordant_pairs, bool) or not isinstance(discordant_pairs, int):
        raise TypeError("discordant_pairs must be a plain int")
    if not 0 <= discordant_pairs <= N_LAW_DRAWS:
        raise ValueError("discordant_pairs must lie in [0, 67]")
    lower, upper = clopper_pearson(discordant_pairs, N_LAW_DRAWS)
    if lower > IC_DISCORDANCE.value:
        return "IC_DEPENDENCE_MATERIAL"
    if upper < IC_DISCORDANCE_NEGLIGIBLE_BOUND:
        return "IC_DEPENDENCE_NEGLIGIBLE"
    return "IC_DEPENDENCE_INDETERMINATE"


# --------------------------------------------------------------------------------------
# PRB-B.  External generator, canonical draw order, seed strategy.
#
# Nothing here creates a scientific seed.  ``derive_seed_root`` is a pure function of
# arguments the caller must supply; the preregistration supplies them once, after the
# beacon round is published, and records the derivation before the first engine call.
# --------------------------------------------------------------------------------------

DRAW_GENERATOR: Mapping[str, Any] = {
    "algorithm": "SHA-256 counter mode",
    "specification": "FIPS 180-4",
    "implementation": "hashlib.sha256 from the Python standard library",
    "version_label": "EDLAB-ROUTE-E-DRAW/v1",
    "version_independence": (
        "SHA-256 output is fixed by FIPS 180-4, so no library version, platform or "
        "numpy build can change a single derived byte."
    ),
    "block": (
        "block(seed_root, domain, index) = sha256(seed_root || b'\\x00' || domain || "
        "b'\\x00' || uint64_be(index))"
    ),
    "uniform": (
        "u = int.from_bytes(block[0:8], 'big') / 2**64, a dyadic rational in [0, 1) with "
        "exactly 64 bits of resolution; the mapping is documented, deterministic and "
        "never re-scaled after a rejection"
    ),
    "endianness": "big-endian for every integer that enters a hash input or a uniform",
    "serialisation": "raw bytes only; no JSON, no locale, no float formatting anywhere",
}

BEACON_SOURCE: Mapping[str, Any] = {
    "name": "drand League of Entropy, quicknet chain",
    "chain_hash": "52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971",
    "scheme": "bls-unchained-g1-rfc9380",
    "period_seconds": 3,
    "genesis_time_unix": 1692803367,
    "public_key": (
        "83cf0f2896adee7eb8b5f01fcad3912212c437e0073e911fb90022d3e760183c8c4b450b6a0a6c"
        "3ac6a5776a2d1064510d1fec758c921cc22b0e17e63aaf4bcb5ed66304de9cf809bd274ca73bab"
        "4af5a6e9c76a4bc09e76eae8991ef5ece45a"
    ),
    "round_rule": (
        "the FIRST round whose beacon time is at or after T, where T is the committer "
        "timestamp of the accepted preregistration commit plus 86400 seconds"
    ),
    "why_it_cannot_be_known_today": (
        "the beacon value for that round does not exist until the round is emitted, which "
        "is strictly after the preregistration commit is written and anchored"
    ),
    "public_verifiability": (
        "the round signature verifies against the fixed chain public key with BLS on G1 "
        "(RFC 9380) and the randomness is sha256(signature); verification needs no secret"
    ),
    "network_access_in_this_module": "none; the beacon bytes are an argument",
}

_DOMAIN_LAW = b"LAW"
_DOMAIN_SIZE = b"SIZE"
_DOMAIN_IC = b"IC"
_SEED_ROOT_PREFIX = b"EDLAB/ROUTE_E/v1"


def beacon_round_at_or_after(instant_unix: int) -> int:
    """First quicknet round whose beacon time is at or after ``instant_unix``.

    ``t(r) = genesis_time + (r - 1) * period``, so the first ``r`` with ``t(r) >= T`` is
    ``1 + ceil((T - genesis_time) / period)``.
    """
    if isinstance(instant_unix, bool) or not isinstance(instant_unix, int):
        raise TypeError("instant_unix must be a plain int")
    genesis = int(BEACON_SOURCE["genesis_time_unix"])
    period = int(BEACON_SOURCE["period_seconds"])
    if instant_unix <= genesis:
        raise ValueError("instant must be strictly after the chain genesis")
    return 1 + -((genesis - instant_unix) // period)


def derive_seed_root(
    *,
    beacon_randomness: bytes,
    beacon_round: int,
    preregistration_commit_sha1: bytes,
) -> bytes:
    """The one and only seed derivation.  Pure, fail-closed, no network.

    Binding the preregistration commit hash makes a reroll detectable: any change to the
    preregistration changes the commit, therefore the seed root, therefore every draw.
    """
    if not isinstance(beacon_randomness, (bytes, bytearray)) or len(beacon_randomness) != 32:
        raise ValueError("beacon_randomness must be exactly 32 bytes")
    if isinstance(beacon_round, bool) or not isinstance(beacon_round, int) or beacon_round <= 0:
        raise ValueError("beacon_round must be a positive plain int")
    if (
        not isinstance(preregistration_commit_sha1, (bytes, bytearray))
        or len(preregistration_commit_sha1) != 20
    ):
        raise ValueError("preregistration_commit_sha1 must be exactly 20 bytes")
    payload = (
        _SEED_ROOT_PREFIX
        + b"\x00"
        + bytes.fromhex(str(BEACON_SOURCE["chain_hash"]))
        + beacon_round.to_bytes(8, "big")
        + bytes(beacon_randomness)
        + bytes(preregistration_commit_sha1)
    )
    return hashlib.sha256(payload).digest()


def draw_block(seed_root: bytes, domain: bytes, index: int) -> bytes:
    """One 32-byte stream block.  Deterministic, order-free, replayable."""
    if not isinstance(seed_root, (bytes, bytearray)) or len(seed_root) != 32:
        raise ValueError("seed_root must be exactly 32 bytes")
    if not isinstance(domain, (bytes, bytearray)) or not domain:
        raise ValueError("domain must be non-empty bytes")
    if isinstance(index, bool) or not isinstance(index, int) or index < 0:
        raise ValueError("index must be a non-negative plain int")
    if index >= 2**64:
        raise ValueError("index must fit in uint64")
    return hashlib.sha256(
        bytes(seed_root) + b"\x00" + bytes(domain) + b"\x00" + index.to_bytes(8, "big")
    ).digest()


def draw_uniform(seed_root: bytes, domain: bytes, index: int) -> float:
    """A uniform in [0, 1) with exactly 64 bits of resolution."""
    return int.from_bytes(draw_block(seed_root, domain, index)[0:8], "big") / float(2**64)


@dataclass(frozen=True)
class DrawPlan:
    """The complete canonical order, computed before any engine step exists.

    ``law_fields`` are the nine dimensionless groups of each accepted proposal, in the
    order laws are accepted.  ``proposal_indices`` records which stream index produced
    each accepted law, so the rejection history is replayable exactly.
    """

    seed_root_sha256: str
    law_fields: tuple[Mapping[str, float], ...]
    proposal_indices: tuple[int, ...]
    proposals_consumed: int
    lattice_sizes: tuple[int, ...]
    ic_indices: tuple[tuple[int, int], ...]
    world_order: tuple[tuple[int, int], ...]

    def digest(self) -> str:
        parts = [self.seed_root_sha256, str(self.proposals_consumed)]
        for fields, index, size, ics in zip(
            self.law_fields,
            self.proposal_indices,
            self.lattice_sizes,
            self.ic_indices,
            strict=True,
        ):
            parts.append(str(index))
            parts.append(str(size))
            parts.append(f"{ics[0]}:{ics[1]}")
            parts.extend(f"{name}={value!r}" for name, value in sorted(fields.items()))
        return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


CANONICAL_DRAW_ORDER = (
    "1. laws:   for i = 0..66, consume proposals from domain b'LAW' at strictly increasing "
    "indices j = 0, 1, 2, ...; the proposal counter is NEVER reset and rejected proposals "
    "are consumed, never reordered; law i is the i-th ACCEPTED proposal.",
    "2. sizes:  L_i = LATTICE_SIZES[floor(3 * u(b'SIZE', i))], u uniform in [0,1).",
    "3. ics:    the two initial-condition stream indices of law i are 2i and 2i+1; index 2i "
    "is X_i1 and serves the primary, index 2i+1 is X_i2 and serves the discriminator only.",
    "4. worlds: executed in lexicographic (law index, initial-condition ordinal) order, "
    "so (0,0), (0,1), (1,0), (1,1), ..., (66,0), (66,1) -- 134 worlds.",
)

ANTI_REROLL = (
    "The seed root binds the preregistration commit hash and a beacon round that does not "
    "exist when that commit is written.  Exactly one derivation is permitted, and it must "
    "be recorded in the family manifest before the first engine step.  Any reroll changes "
    "either the commit or the round, both of which are public and both of which change "
    "every derived byte.  There is no code path in this module that derives a second root.",
)

ORDER_INDEPENDENCE = (
    "build_draw_plan takes only (seed_root, engine admissibility).  It calls no engine "
    "step, reads no world, and receives no outcome.  Admissibility is a pure predicate on "
    "a proposal, evaluated before any simulation exists.  Therefore no Y_i, no k, no "
    "terminal state and no measurement can influence which law, which size or which "
    "initial condition is drawn, or in what order.",
)


# --------------------------------------------------------------------------------------
# PRB-C.  The sampler's acceptance predicate IS the engine's own construction.
#
# There is deliberately no parallel implementation of (B1) AND (B2) on the accept path.
# ``algebraic_b1_b2`` exists only so the closure can REPORT an agreement statistic; it is
# never consulted by ``engine_accepts`` and never by ``build_draw_plan``.
# --------------------------------------------------------------------------------------

PROPOSAL_BOX: Mapping[str, Any] = {
    "scales": {"dt": 1.0, "m_max": 1.0, "n_max": 1.0},
    "rate_interval": (1.0 / 1024.0, 1.0 / 16.0),
    "rate_fields": ("kappa_m", "resource_diffusivity", "k_on", "k_off", "k_tension"),
    "affinity_sum_cap": 2.0 * math.log(1024.0 / 4.0),
    "epsilon_b_interval": (0.0, 1.0),
    "resource_leak_floor_interval": (0.0, 1.0),
    "note": (
        "restated from the frozen 01S box; this closure does not re-derive it and does "
        "not widen it"
    ),
}

_RATE_LOW, _RATE_HIGH = PROPOSAL_BOX["rate_interval"]
_AFFINITY_CAP = float(PROPOSAL_BOX["affinity_sum_cap"])


def propose_law_fields(seed_root: bytes, proposal_index: int) -> dict[str, float]:
    """One proposal from the declared PRODUCT proposal box.  Says nothing about A.

    Every coordinate is drawn INDEPENDENTLY and UNIFORMLY on its own interval, so the
    proposal measure is uniform on the product box.  The triangular affinity cap is NOT
    imposed by a conditional draw -- a conditional draw would make the density on the
    triangle proportional to 1/(cap - theta_m) and would silently change the frozen law
    distribution.  It is imposed by rejection, in ``in_proposal_box``, which preserves
    uniformity on the accepted region exactly.
    """
    if isinstance(proposal_index, bool) or not isinstance(proposal_index, int):
        raise TypeError("proposal_index must be a plain int")
    if proposal_index < 0:
        raise ValueError("proposal_index must be non-negative")
    base = proposal_index * 9
    u = [draw_uniform(seed_root, _DOMAIN_LAW, base + offset) for offset in range(9)]
    rate = lambda value: _RATE_LOW + value * (_RATE_HIGH - _RATE_LOW)  # noqa: E731
    return {
        "dt": 1.0,
        "m_max": 1.0,
        "n_max": 1.0,
        "kappa_m": rate(u[0]),
        "resource_diffusivity": rate(u[1]),
        "k_on": rate(u[2]),
        "k_off": rate(u[3]),
        "k_tension": rate(u[4]),
        "theta_m": u[5] * _AFFINITY_CAP,
        "theta_n": u[6] * _AFFINITY_CAP,
        "epsilon_b": u[7],
        "resource_leak_floor": u[8],
    }


def in_proposal_box(fields: Mapping[str, float]) -> bool:
    """The DECLARED DESIGN membership test for the 01S box.

    This is deliberately separate from admissibility.  The engine knows nothing about
    the design box -- the affinity cap ``theta_m_hat + theta_n_hat < 2 ln(H/4)`` is a
    resolvability constraint declared by the design, not a source bound -- so the
    sampler must test it.  It contains NO reimplementation of (B1) or (B2): those are
    the engine's business and only the engine's.
    """
    try:
        theta_m = float(fields["theta_m"])
        theta_n = float(fields["theta_n"])
        epsilon_b = float(fields["epsilon_b"])
        leak = float(fields["resource_leak_floor"])
        rates = [float(fields[name]) for name in PROPOSAL_BOX["rate_fields"]]
    except (KeyError, TypeError, ValueError):
        return False
    values = [theta_m, theta_n, epsilon_b, leak, *rates]
    if not all(math.isfinite(value) for value in values):
        return False
    if not all(_RATE_LOW <= rate <= _RATE_HIGH for rate in rates):
        return False
    if theta_m < 0.0 or theta_n < 0.0 or theta_m + theta_n >= _AFFINITY_CAP:
        return False
    if not 0.0 <= epsilon_b <= 1.0 or not 0.0 <= leak <= 1.0:
        return False
    return True


def engine_accepts(fields: Mapping[str, float]) -> tuple[bool, str]:
    """THE accept predicate.  Acceptance is the engine building its own object.

    Returns ``(accepted, reason)``.  Every failure mode is a refusal:
    ``AdmissibilityError``, ``ValueError`` (non-finite, negative, out-of-range),
    ``TypeError`` (unknown or missing field), ``OverflowError``, ``ArithmeticError``.
    No exception escapes as an acceptance and no exception is swallowed into a default.
    """
    try:
        spec = LatticeBondSpec(**dict(fields))
    except AdmissibilityError as exc:
        return False, f"AdmissibilityError: {exc}"
    except TypeError as exc:
        return False, f"TypeError: {exc}"
    except OverflowError as exc:
        return False, f"OverflowError: {exc}"
    except ValueError as exc:
        return False, f"ValueError: {exc}"
    except ArithmeticError as exc:
        return False, f"ArithmeticError: {exc}"
    if not math.isfinite(spec.admissible_dt_limit):
        # A degenerate law with no finite bound is refused rather than silently kept.
        return False, "NonFiniteBound: admissible_dt_limit is not finite"
    return True, "EngineConstructed"


def algebraic_b1_b2(fields: Mapping[str, float]) -> bool:
    """Complementary predicate, REPORTED ONLY.  Never on the accept path.

    (B1) kappa_hat < (1/4) exp(-(theta_m_hat + theta_n_hat)/2)
    (B2) 4 D_hat + 2 eps_b_hat k_on_hat < 1
    """
    try:
        kappa = float(fields["kappa_m"])
        theta_m = float(fields["theta_m"])
        theta_n = float(fields["theta_n"])
        diffusivity = float(fields["resource_diffusivity"])
        epsilon_b = float(fields["epsilon_b"])
        k_on = float(fields["k_on"])
    except (KeyError, TypeError, ValueError):
        return False
    values = (kappa, theta_m, theta_n, diffusivity, epsilon_b, k_on)
    if not all(math.isfinite(value) for value in values):
        return False
    b1 = kappa < 0.25 * math.exp(-0.5 * (theta_m + theta_n))
    b2 = 4.0 * diffusivity + 2.0 * epsilon_b * k_on < 1.0
    return b1 and b2


def sample_law_indices(seed_root: bytes, count: int, *, max_proposals: int = 1_000_000) -> tuple[
    tuple[int, ...], int
]:
    """Accepted proposal indices, in canonical order, gated only by the engine."""
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        raise ValueError("count must be a positive plain int")
    accepted: list[int] = []
    index = 0
    while len(accepted) < count:
        if index >= max_proposals:
            raise RuntimeError("proposal budget exhausted before the frozen law count")
        fields = propose_law_fields(seed_root, index)
        # Two independent conjuncts, in this order and no other:
        #   1. membership in the DECLARED DESIGN box (the engine knows nothing of it);
        #   2. the ENGINE's own fail-closed construction, which is the sole authority
        #      on (B1) AND (B2).  There is no parallel implementation on this path.
        if in_proposal_box(fields) and engine_accepts(fields)[0]:
            accepted.append(index)
        index += 1
    return tuple(accepted), index


def build_draw_plan(seed_root: bytes, *, count: int = N_LAW_DRAWS) -> DrawPlan:
    """The complete canonical draw order.  No engine step, no world, no outcome."""
    indices, consumed = sample_law_indices(seed_root, count)
    fields = tuple(propose_law_fields(seed_root, index) for index in indices)
    sizes = tuple(
        LATTICE_SIZES[min(len(LATTICE_SIZES) - 1, int(draw_uniform(seed_root, _DOMAIN_SIZE, i) * len(LATTICE_SIZES)))]
        for i in range(count)
    )
    ic_indices = tuple((2 * i, 2 * i + 1) for i in range(count))
    world_order = tuple((i, c) for i in range(count) for c in range(INITIAL_CONDITIONS_PER_LAW))
    return DrawPlan(
        seed_root_sha256=hashlib.sha256(bytes(seed_root)).hexdigest(),
        law_fields=fields,
        proposal_indices=indices,
        proposals_consumed=consumed,
        lattice_sizes=sizes,
        ic_indices=ic_indices,
        world_order=world_order,
    )


# --------------------------------------------------------------------------------------
# PRB-D.  Association-gate track break.
#
# Mechanism, established from the accepted tracker source: when every candidate edge out
# of a left component is refused by the association gate, that component's track receives
# a DISSOLUTION event at the right frame while the surviving matter is re-enrolled as a
# brand new APPEARANCE track.  The terminal state is DISSOLVED_DETECTED_TRACK even though
# no matter vanished.  The discriminating evidence is the refused edge itself.
# --------------------------------------------------------------------------------------

ASSOCIATION_GATE_BREAK_REASONS: frozenset[str] = frozenset(
    {"REJECT_CENTROID_DISTANCE", "REJECT_AREA_RATIO"}
)


@dataclass(frozen=True)
class TrackTermination:
    """One track's terminal record plus its prospective, non-null cause."""

    track_id: int
    frame: int
    terminal_state: str
    cause: str
    refused_reasons: tuple[str, ...]
    scores_one: bool

    def __post_init__(self) -> None:
        if self.scores_one:
            raise ValueError(
                "no cause produced by this closure may score 1; only "
                "RIGHT_CENSORED_AT_HORIZON with verified replacement can"
            )


_TERMINAL_BY_EVENT = {
    "DISSOLUTION": "DISSOLVED_DETECTED_TRACK",
    "SPLIT": "SPLIT_INTO_TRACKS",
    "MERGE": "MERGED_INTO_TRACK",
    "TRACKING_UNRESOLVED": "UNRESOLVED_HANDOFF",
}


def classify_track_terminations(tracking: TrackingResult) -> tuple[TrackTermination, ...]:
    """Attach ``ASSOCIATION_GATE_TRACK_BREAK`` where the gate, not the matter, ended a track.

    A track is classified ``ASSOCIATION_GATE_TRACK_BREAK`` iff ALL of:
      1. its terminal event is ``DISSOLUTION`` at frame ``f``;
      2. at least one candidate edge out of the dissolving component was refused with a
         reason in ``ASSOCIATION_GATE_BREAK_REASONS`` -- geometric support existed and the
         GATE refused it, as opposed to ``REJECT_NO_GEOMETRIC_SUPPORT`` or no candidate
         at all, which are genuine disappearances;
      3. the refused edge's target is a component of frame ``f`` that opened a new track
         with an ``APPEARANCE`` event at ``f``.

    The break scores 0, exactly like any other non-``RIGHT_CENSORED_AT_HORIZON`` outcome.
    It stays in the denominator.  It is never reclassified after observation: the rule
    above is a pure function of the tracking artefact, computed once.
    """
    if not isinstance(tracking, TrackingResult):
        raise TypeError("tracking must be a TrackingResult")

    appeared_at: dict[tuple[int, int], int] = {}
    for event in tracking.events:
        if event.kind == "APPEARANCE":
            for key in event.target_components:
                appeared_at[tuple(key)] = event.frame

    refused_by_source: dict[tuple[int, int], list[AssociationEdge]] = {}
    for edge in tracking.edges:
        if not edge.qualified and edge.qualification_reason in ASSOCIATION_GATE_BREAK_REASONS:
            refused_by_source.setdefault(tuple(edge.source), []).append(edge)

    results: list[TrackTermination] = []
    for event in tracking.events:
        terminal_state = _TERMINAL_BY_EVENT.get(event.kind)
        if terminal_state is None:
            continue
        for position, track_id in enumerate(event.source_track_ids):
            source_key = (
                tuple(event.source_components[position])
                if position < len(event.source_components)
                else None
            )
            reasons: tuple[str, ...] = ()
            cause = terminal_state
            if event.kind == "DISSOLUTION" and source_key is not None:
                gate_edges = [
                    edge
                    for edge in refused_by_source.get(source_key, ())
                    if appeared_at.get(tuple(edge.target)) == event.frame
                ]
                if gate_edges:
                    cause = "ASSOCIATION_GATE_TRACK_BREAK"
                    reasons = tuple(sorted({edge.qualification_reason for edge in gate_edges}))
            results.append(
                TrackTermination(
                    track_id=int(track_id),
                    frame=int(event.frame),
                    terminal_state=terminal_state,
                    cause=cause,
                    refused_reasons=reasons,
                    scores_one=False,
                )
            )
    return tuple(results)


# --------------------------------------------------------------------------------------
# PRB-E.  What Delta means, exactly, and the ceiling on what it can ever license.
# --------------------------------------------------------------------------------------

DELTA_DEFINITION: Mapping[str, Any] = {
    "symbol": "Delta(f)",
    "compares": (
        "the proportion of draws in which the declared binary criterion holds, against "
        "the two frozen boundaries Delta_0 = 0.50 and Delta_1 = 0.25; it compares NOTHING "
        "to a control group, to a historical family, or to any other route"
    ),
    "level": (
        "the DRAW, i.e. one triple (law_i, L_i, X_i1); never the entity, never the "
        "component, never the track, never the cell"
    ),
    "criterion": (
        "at least one eligible component of the world satisfies persistence "
        "(RIGHT_CENSORED_AT_HORIZON, observed continuously to step 1024) AND verified "
        "material replacement (cohort_residual <= f)"
    ),
    "sign": (
        "non-negative by construction: Delta(f) is a probability in [0, 1]; it has no "
        "direction and is not a difference of two quantities"
    ),
    "unit": "dimensionless probability",
    "aggregation": (
        "one Bernoulli per law, k = sum of 67 indicators, estimated by k/67 with an exact "
        "two-sided 95% Clopper-Pearson interval; the second initial condition contributes "
        "NOTHING to k"
    ),
    "parameter_f": (
        "f is cohort_residual_fraction, a declared measurement convention with sensitivity "
        "set {0.01, 0.05, 0.20}.  Delta is monotone non-decreasing in f, so the POSITIVE "
        "arm is bound by Delta(0.01) and the NEGATIVE arm by Delta(0.20).  A conclusion "
        "must hold at all three values or the family reports "
        "INDETERMINATE - REPLACEMENT_CONVENTION."
    ),
    "which_delta_the_ceiling_speaks_of": (
        "POSITIVE licenses a statement about Delta(0.01); NEGATIVE licenses a statement "
        "about Delta(0.20); no single unqualified 'Delta' may be quoted."
    ),
    "link_to_second_ic_discriminator": (
        "the second initial condition produces psi = P(Y_i1 != Y_i2), a SEPARATE quantity "
        "with its own ternary attribution.  psi never enters Delta, never enters k, and "
        "can never remove a law from the denominator.  A material psi does not invalidate "
        "Delta; it caps the interpretation of Delta to the marginal over initial "
        "conditions, which is what Delta already is."
    ),
    "estimand_is_marginal_over_size": (
        "L is drawn uniformly on {16, 24, 32}, so Delta is marginal over lattice size; a "
        "fixed allocation would not estimate the same quantity"
    ),
}

CLAIM_CEILING: Mapping[str, Any] = {
    "licenses": (
        "In the declared frame -- square periodic lattices of {16, 24, 32}, scales "
        "dt = m_max = n_max = 1, laws uniform on A = Box AND (B1) AND (B2) with "
        "epsilon_b_hat <= 1, initial conditions i.i.d. U[0,1] with b == 0, horizon 1024, "
        "cadence 16 -- the conjunction persistence AND verified material replacement is "
        "instantiated in a proportion Delta(f) of draws, with the stated exact interval."
    ),
    "level": "the draw, never the entity",
    "ladder_position": (
        "below rung 3: Route E measures no state variable and inspects nothing internal "
        "to a component"
    ),
    "relation_to_the_published_paper": (
        "the first paper already established causal persistence through material turnover "
        "without evidence of local ownership.  Route E measures how OFTEN that conjunction "
        "occurs across a declared law distribution.  A frequency is not a mechanism."
    ),
}

FORBIDDEN_INFERENCES: tuple[str, ...] = (
    "ownership",
    "local ownership",
    "autonomy",
    "individuality",
    "individual",
    "reconstruction",
    "self-repair",
    "reproduction",
    "division",
    "heredity",
    "inheritance",
    "agency",
    "goal",
    "robust effect",
    "robustly",
)


def check_claim_within_ceiling(claim: str) -> tuple[bool, tuple[str, ...]]:
    """Refuse a claim sentence that reaches past the ceiling.

    Returns ``(within_ceiling, offending_terms)``.  A vague formulation such as
    "robust effect" without an estimand and a domain is refused by construction, because
    the vague terms are themselves in the forbidden list.
    """
    if not isinstance(claim, str):
        raise TypeError("claim must be a str")
    lowered = claim.lower()
    hits = tuple(term for term in FORBIDDEN_INFERENCES if term in lowered)
    return (not hits), hits


# --------------------------------------------------------------------------------------
# PRB-F.  The fail-closed scientific entry point, and the out-of-protocol declaration.
# --------------------------------------------------------------------------------------

OUT_OF_PROTOCOL_ENTRY_POINTS: Mapping[str, str] = {
    "run_owned_future_pipeline": (
        "DECLARED OUT OF PROTOCOL as a direct Route E scientific entry point.  It has no "
        "authorisation parameter and cannot be given one without modifying an accepted "
        "source, which the frozen allowlist forbids.  Invoked directly in an unauthorised "
        "Route E context it refuses at its first check, before creating the acquisition "
        "frame directory, before invoking the acquisition source, before any engine call "
        "and before writing any byte.  See RE-L2."
    ),
    "open_owned_analysis_access": (
        "lower-level analysis path; in protocol only through the measurement bridge's "
        "anchor-gated open_measured_analysis_access"
    ),
    "future_lifecycle_runner.open_analysis_access": "same",
    "publish_future_family_completion": "same",
    "qualify_and_write_lifecycle_contract": "same",
}


@dataclass(frozen=True)
class RouteEAuthorisation:
    """A scientific-run authorisation.  Construction alone grants nothing."""

    preregistration_commit_sha1: str
    human_review_commit_sha1: str
    beacon_round: int
    seed_root_sha256: str
    granted: bool = False

    def is_valid(self) -> bool:
        if not self.granted:
            return False
        for value in (self.preregistration_commit_sha1, self.human_review_commit_sha1):
            if not isinstance(value, str) or len(value) != 40:
                return False
            try:
                int(value, 16)
            except ValueError:
                return False
        if isinstance(self.beacon_round, bool) or not isinstance(self.beacon_round, int):
            return False
        if self.beacon_round <= 0:
            return False
        if not isinstance(self.seed_root_sha256, str) or len(self.seed_root_sha256) != 64:
            return False
        try:
            int(self.seed_root_sha256, 16)
        except ValueError:
            return False
        return True


def open_route_e_scientific_run(
    run_directory: str | os.PathLike[str],
    *,
    authorisation: RouteEAuthorisation | None,
) -> None:
    """The single in-protocol Route E scientific entry point.  It always refuses here.

    ``scientific_run_authorized`` is ``False`` for this mission, so this function refuses
    unconditionally, and it refuses BEFORE touching the filesystem, before constructing a
    law, before creating a namespace and before any engine call.  There is no branch in
    this module that can reach an execution path.
    """
    if authorisation is None or not isinstance(authorisation, RouteEAuthorisation):
        raise RouteEAuthorisationError(
            "refused: no Route E scientific authorisation was presented"
        )
    if not authorisation.is_valid():
        raise RouteEAuthorisationError("refused: the presented authorisation is not valid")
    if not SCIENTIFIC_RUN_AUTHORIZED:
        raise RouteEAuthorisationError(
            "refused: scientific_run_authorized is False; the six frozen PRE_RUN_BLOCKERs "
            "PRB-1..PRB-6 are not closed, no preregistration exists, and no human review "
            "has authorised execution"
        )
    raise RouteEAuthorisationError(  # pragma: no cover - unreachable by construction
        "refused: unreachable"
    )


SECOND_IC_CONTROL: Mapping[str, Any] = {
    "discriminator_output": "psi_hat = d / 67, with d the count of discordant law-pairs",
    "possible_states": (
        "IC_DEPENDENCE_MATERIAL",
        "IC_DEPENDENCE_NEGLIGIBLE",
        "IC_DEPENDENCE_INDETERMINATE",
    ),
    "consequence_of_discordance": (
        "a discordance between X_i1 and X_i2 is EVIDENCE about psi and nothing else.  It "
        "does not change Y_i, does not change k, does not change Delta, and does not "
        "change the ternary decision."
    ),
    "effect_on_interpretation_ceiling": (
        "IC_DEPENDENCE_MATERIAL caps the reading of Delta: it forbids restating Delta as "
        "a statement about laws ('the fraction of laws that reproduce') and confines it to "
        "the marginal over initial conditions, which is what Delta already is.  It never "
        "invalidates the primary."
    ),
    "absolute_prohibition": (
        "no law may EVER leave the denominator because of X_i2.  Enrolment is fixed by "
        "X_i1 at the draw, and the frozen rule is: no replacement, no re-draw, no "
        "supplement."
    ),
    "status": "fully specifiable at preregistration; no ambiguity remains open",
}
