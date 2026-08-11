"""FCDDH00 acquisition launcher (sham and active).

This file adds NOTHING to the physics. It writes the two write-ahead markers required by the
FCDDH00 charging contract and then `os.execv`s into the UNCHANGED, COMMITTED parent worker
`FWL2CF00/fw_worker.py`, replacing its own process image. There is therefore exactly ONE fresh
process per start, running the committed carrier executable path byte-for-byte, and the markers
were written by that same process before any engine existed.

The ADVANCE marker is written before the exec, i.e. slightly earlier than the committed worker's
own pre-flight hash checks. That is deliberately CONSERVATIVE: it can only over-charge a
deterministic pre-flight failure, never under-charge an engine advance.

Usage:
    python3 -B fh_aworker.py <ckpt.npz> <mask.npz> <SHAM|CARRIER_1|CARRIER_2> <out.npz>
                             <expected_ckpt_sha> <expected_callable> --ack <a> --advance <b>
"""
from __future__ import annotations

import hashlib
import os
import sys

ARGV = list(sys.argv)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fh_runner                                                   # noqa: E402

FW_WORKER = "/home/claude/sweep/FWL2CF00/fw_worker.py"
FW_WORKER_GIT_BLOB = "e640455ed7c0ef3fa4e34db7ea086997d33e28ab"     # 334b7c2b:FWL2CF00/fw_worker.py
FW_WORKER_SHA256 = "a10a8af5156498517a16400ff29089091373137c032fc7e13e18c7d51b0e69e5"

fh_runner.child_ack(ARGV)

ck, mk, op, out, exp_sha, exp_call = ARGV[1:7]
assert op in ("SHAM", "CARRIER_1", "CARRIER_2"), "unknown operator"
assert os.path.isfile(FW_WORKER), "committed parent worker missing"
_b = open(FW_WORKER, "rb").read()
assert hashlib.sha256(_b).hexdigest() == FW_WORKER_SHA256, "carrier executable path mutated"
assert hashlib.sha1(b"blob %d\x00" % len(_b) + _b).hexdigest() == FW_WORKER_GIT_BLOB, \
    "carrier executable is not the committed parent blob"

fh_runner.child_advance(ARGV, "exec into committed fw_worker.py op=%s out=%s" % (op, os.path.basename(out)))

os.execv(sys.executable, [sys.executable, "-B", FW_WORKER, ck, mk, op, out, exp_sha, exp_call])
