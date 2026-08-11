"""FCDDH01R DEX dummy worker. EXECUTION_CLASS = DEX_DUMMY.

Deterministic, engine-free. Its ONLY imports are hashlib, json, os, sys, time. It cannot
instantiate or advance any project engine: there is no import path from this file to edlab,
domc_core, ppai_core, wsfscrp_core, etcmnfc_core or fw_worker, and the DEX dependency audit
proves it by AST.

Usage:
  python3 -B fr_dummy.py <tag> <tmp_out> <sleep_s> [--fail-after-advance] [--stall]
                         --ack <ack> --advance <adv>
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

A = list(sys.argv)


def _fsync_write(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)


TAG = A[1]
TMP = A[2]
SLEEP = float(A[3])
FAIL_AFTER_ADVANCE = "--fail-after-advance" in A
STALL = "--stall" in A
ACK = A[A.index("--ack") + 1]
ADV = A[A.index("--advance") + 1]

_fsync_write(ACK, json.dumps({"pid": os.getpid(), "tag": TAG, "execution_class": "DEX_DUMMY",
                              "ts": time.time()}, sort_keys=True).encode())
_fsync_write(ADV, json.dumps({"pid": os.getpid(), "tag": TAG, "execution_class": "DEX_DUMMY",
                              "note": "DUMMY_ADVANCE_NO_ENGINE", "ts": time.time()},
                             sort_keys=True).encode())

if FAIL_AFTER_ADVANCE:
    time.sleep(min(SLEEP, 0.3))
    os._exit(9)
if STALL:
    while True:
        time.sleep(1.0)

time.sleep(SLEEP)
body = hashlib.sha256(("FCDDH01R|DEX_DUMMY|" + TAG).encode()).digest() * 64
_fsync_write(TMP, body)
print(json.dumps({"ok": True, "tag": TAG, "execution_class": "DEX_DUMMY",
                  "sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body)}))
