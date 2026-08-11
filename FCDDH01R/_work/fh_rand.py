"""FCDDH00 frozen randomization scheduler.

One 256-bit OS seed, drawn exactly once, fsynced before any derivation and committed before
construction. All assignment bits are derived by SHAKE256 with domain-separated inputs. No other
PRNG, no other library, no re-derivation from a different implementation.

Frozen conventions (bound by the master freeze and by known-answer fixtures):
  * "first bit" means the MOST SIGNIFICANT bit of the first output byte:  digest[0] >> 7
  * geometry   : SHAKE256(b"FCDDH00|geometry|<role>|<idx>|"          + seed)
  * allocation : SHAKE256(b"FCDDH00|allocation|<role>|<idx>|<g>|"    + seed)
  * run order  : SHAKE256(b"FCDDH00|run_order|<role>|<idx>|"         + seed) as a byte stream,
                 consumed by Fisher-Yates with REJECTION SAMPLING (never modulo reduction)
  * each geometry bit is used directly, once
"""
from __future__ import annotations

import hashlib

DOMAIN_GEOMETRY = b"FCDDH00|geometry|"
DOMAIN_ALLOCATION = b"FCDDH00|allocation|"
DOMAIN_RUN_ORDER = b"FCDDH00|run_order|"


def _shake(prefix: bytes, seed: bytes, nbytes: int) -> bytes:
    return hashlib.shake_256(prefix + seed).digest(nbytes)


def geometry_bit(seed: bytes, role: str, candidate_index: int) -> int:
    pre = DOMAIN_GEOMETRY + role.encode("ascii") + b"|" + str(candidate_index).encode("ascii") + b"|"
    return _shake(pre, seed, 1)[0] >> 7


def allocation_bit(seed: bytes, role: str, candidate_index: int, g: str) -> int:
    pre = (DOMAIN_ALLOCATION + role.encode("ascii") + b"|" + str(candidate_index).encode("ascii")
           + b"|" + g.encode("ascii") + b"|")
    return _shake(pre, seed, 1)[0] >> 7


class _Stream:
    """Deterministic SHAKE256 byte stream with rejection sampling."""

    def __init__(self, prefix: bytes, seed: bytes):
        self.prefix = prefix
        self.seed = seed
        self.buf = b""
        self.pos = 0
        self.drawn = 0

    def _need(self, n):
        while len(self.buf) - self.pos < n:
            self.drawn += 64
            self.buf = _shake(self.prefix, self.seed, self.drawn)
        # buf is a prefix-stable SHAKE stream: extending the digest never changes earlier bytes

    def bytes(self, n):
        self._need(n)
        out = self.buf[self.pos:self.pos + n]
        self.pos += n
        return out

    def below(self, m: int) -> int:
        """uniform integer in [0, m) by rejection sampling; never a modulo reduction"""
        assert m >= 1
        if m == 1:
            return 0
        k = 1
        while (1 << (8 * k)) < m:
            k += 1
        limit = ((1 << (8 * k)) // m) * m
        while True:
            v = int.from_bytes(self.bytes(k), "big")
            if v < limit:
                return v % m


def run_order(seed: bytes, role: str, candidate_index: int, items):
    """Fisher-Yates over a copy of `items`, consuming the frozen stream."""
    pre = DOMAIN_RUN_ORDER + role.encode("ascii") + b"|" + str(candidate_index).encode("ascii") + b"|"
    st = _Stream(pre, seed)
    arr = list(items)
    for i in range(len(arr) - 1, 0, -1):
        j = st.below(i + 1)
        arr[i], arr[j] = arr[j], arr[i]
    return arr


def block_assignment(seed: bytes, role: str, candidate_index: int):
    """The complete frozen assignment for one candidate ancestry block.

    * geometry coin c: c = 0 -> (slot0, slot1) = (NEAR, FAR); c = 1 -> (FAR, NEAR).
      ONE fair block-level coin maps NEAR/FAR jointly across BOTH allocation members onto the
      two otherwise neutral branch slots. This gives exactly one sign-flip unit per ancestry.
    * allocation serializer exchange bit per geometry: execution blinding only; the analysis is
      invariant to it because the allocation orbit is averaged (x) or minimised over all four
      cross-orbit pairings (J).
    * run order over the four descendants and, inside each descendant, over the two carriers.
    """
    c = geometry_bit(seed, role, candidate_index)
    slots = [("SLOT_0", "NEAR"), ("SLOT_1", "FAR")] if c == 0 else [("SLOT_0", "FAR"), ("SLOT_1", "NEAR")]
    alloc_swap = {g: allocation_bit(seed, role, candidate_index, g) for _, g in slots}
    cells = []
    for slot, g in slots:
        for member in (0, 1):
            a = member ^ alloc_swap[g]          # serializer label exchange, execution blinding only
            cells.append({"slot": slot, "geometry": g, "serializer_member": member, "allocation": a})
    order = run_order(seed, role, candidate_index, list(range(4)))
    carrier_order = {}
    for k in range(4):
        co = run_order(seed, role, candidate_index * 100 + 10 + k, ["CARRIER_1", "CARRIER_2"])
        carrier_order[k] = co
    return {"geometry_coin": c, "cells": cells, "descendant_run_order": order,
            "carrier_run_order": {str(k): v for k, v in carrier_order.items()},
            "allocation_serializer_swap": alloc_swap}


def known_answer_fixtures(seed: bytes):
    """Byte-exact fixtures persisted with the manifest so the schedule can never be regenerated
    from a different library or PRNG without detection."""
    return {
        "shake256_geometry_DISCOVERY_0_first8":
            _shake(DOMAIN_GEOMETRY + b"DISCOVERY|0|", seed, 8).hex(),
        "shake256_allocation_DISCOVERY_0_NEAR_first8":
            _shake(DOMAIN_ALLOCATION + b"DISCOVERY|0|NEAR|", seed, 8).hex(),
        "shake256_run_order_DISCOVERY_0_first8":
            _shake(DOMAIN_RUN_ORDER + b"DISCOVERY|0|", seed, 8).hex(),
        "shake256_geometry_HOLDOUT_0_first8":
            _shake(DOMAIN_GEOMETRY + b"HOLDOUT|0|", seed, 8).hex(),
        "empty_domain_zero_seed_check":
            hashlib.shake_256(b"FCDDH00|selftest|").digest(8).hex(),
    }
