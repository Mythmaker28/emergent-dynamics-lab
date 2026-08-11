"""FCDDH01R exactly-once phase state machine.

Engineering only. This module contains NO scientific formula, NO estimand, NO threshold and NO
reader; it never imports a project engine. It provides the four-part durability contract:

    EXACTLY_ONCE_LAUNCH_AUTHORIZATION
    AT_MOST_ONCE_ENGINE_ADVANCE
    EXACTLY_ONCE_OPAQUE_RAW_PUBLICATION
    NO_REPLAY_AFTER_UNCERTAIN_OR_INCOMPLETE_BILLED_LAUNCH

It does NOT claim that every launched row completes: without an engine that can atomically commit
its internal advance together with the ledger, an arbitrary SIGKILL cannot guarantee that.

The authoritative WAL is an append-only DIRECTORY of individually published atomic records.
Each record is written to a temporary path, fsynced, published by an exclusive link that fails if
the name exists, and then the parent directory is fsynced. Nothing is ever overwritten. A mutable
heartbeat file exists but is explicitly non-evidentiary.
"""
from __future__ import annotations

import errno
import fcntl
import hashlib
import json
import os
import time

STATES = ("PLANNED", "DISPATCH_INTENT", "WRAPPER_ACK", "START_GATE", "ENGINE_OPENED",
          "ADVANCE_STARTED", "ENGINE_EXIT_OK", "RAW_SEALED", "RAW_PUBLISHED", "VERIFIED")
BILLED_FROM = "START_GATE"
ORDER = {s: i for i, s in enumerate(STATES)}

EXECUTION_CLASS_REAL = "REAL"
EXECUTION_CLASS_DUMMY = "DEX_DUMMY"


# ------------------------------------------------------------------ durable primitives
def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_fsync(path, data: bytes):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)


def publish_exclusive(tmp, final):
    """Atomic, non-overwriting publication. Raises FileExistsError if `final` exists."""
    os.link(tmp, final)
    os.unlink(tmp)
    fsync_dir(os.path.dirname(final) or ".")


def boot_id():
    try:
        return open("/proc/sys/kernel/random/boot_id").read().strip()
    except Exception:
        return "UNKNOWN_BOOT_ID"


def proc_start_ticks(pid):
    try:
        with open("/proc/%d/stat" % pid, "rb") as f:
            raw = f.read()
        return int(raw[raw.rindex(b")") + 2:].split()[19])
    except Exception:
        return None


def proc_alive(pid, start_ticks):
    """Identity-checked liveness. A matching PID with a different start time is NOT the worker."""
    if pid is None:
        return False
    try:
        os.kill(pid, 0)
    except OSError as e:
        if e.errno == errno.ESRCH:
            return False
        if e.errno != errno.EPERM:
            return False
    cur = proc_start_ticks(pid)
    if cur is None or start_ticks is None:
        return False
    return int(cur) == int(start_ticks)


def identity_record(tag):
    pid = os.getpid()
    return {"tag": tag, "pid": pid, "pgid": os.getpgid(0), "sid": os.getsid(0),
            "ppid": os.getppid(), "host": os.uname().nodename, "boot_id": boot_id(),
            "proc_start_ticks": proc_start_ticks(pid), "argv0": os.sys.argv[0],
            "cwd": os.getcwd(), "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


# ------------------------------------------------------------------ the ledger
class PhaseLedger:
    def __init__(self, root, programme, phase, execution_class=EXECUTION_CLASS_REAL):
        assert execution_class in (EXECUTION_CLASS_REAL, EXECUTION_CLASS_DUMMY)
        self.root = root
        self.programme = programme
        self.phase = phase
        self.cls = execution_class
        self.wal = os.path.join(root, "wal")
        self.gates = os.path.join(root, "gates")
        for d in (root, self.wal, self.gates):
            os.makedirs(d, exist_ok=True)
        fsync_dir(root)

    # -- identity ---------------------------------------------------------------------
    def run_id(self, ordinal, operator_hash, input_hashes, schedule_position):
        h = hashlib.sha256()
        for part in (self.programme, self.phase, self.cls, str(ordinal), operator_hash,
                     "|".join(input_hashes), str(schedule_position)):
            h.update(part.encode())
            h.update(b"\x1f")
        return h.hexdigest()[:32]

    # -- WAL --------------------------------------------------------------------------
    def _seq(self):
        return len([n for n in os.listdir(self.wal) if n.endswith(".json")])

    def emit(self, run_id, state, payload=None):
        assert state in STATES, state
        rec = {"programme": self.programme, "phase": self.phase, "execution_class": self.cls,
               "run_id": run_id, "state": state, "payload": payload or {},
               "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "monotonic": time.monotonic(), "writer_pid": os.getpid()}
        body = json.dumps(rec, sort_keys=True).encode()
        rec["checksum"] = hashlib.sha256(body).hexdigest()
        body = json.dumps(rec, sort_keys=True).encode()
        for attempt in range(4096):
            seq = self._seq() + attempt
            name = "%08d-%s-%s.json" % (seq, run_id, state)
            tmp = os.path.join(self.wal, "." + name + ".tmp")
            final = os.path.join(self.wal, name)
            write_fsync(tmp, body)
            try:
                publish_exclusive(tmp, final)
                return final
            except FileExistsError:
                os.unlink(tmp)
                continue
        raise RuntimeError("WAL sequence exhausted")

    def events(self, run_id=None):
        out = []
        for n in sorted(os.listdir(self.wal)):
            if not n.endswith(".json") or n.startswith("."):
                continue
            try:
                r = json.load(open(os.path.join(self.wal, n)))
            except Exception:
                continue
            if run_id is None or r.get("run_id") == run_id:
                out.append(r)
        return out

    def states_of(self, run_id):
        return [r["state"] for r in self.events(run_id)]

    def verify_monotone(self):
        """No row may move backwards through the state order."""
        seen = {}
        bad = []
        for r in self.events():
            rid, st = r["run_id"], r["state"]
            if rid in seen and ORDER[st] < ORDER[seen[rid]]:
                bad.append((rid, seen[rid], st))
            seen[rid] = st
        return bad

    # -- the charging gate --------------------------------------------------------------
    def gate_path(self, run_id):
        return os.path.join(self.gates, run_id + ".gate")

    def try_start_gate(self, run_id, payload):
        """One exclusive atomic filesystem claim. Its winner, and only its winner, may
        instantiate or advance the engine. Publication of this record CHARGES the row."""
        p = self.gate_path(run_id)
        # The temporary MUST be unique per claimant: concurrent wrappers may not race on the
        # temporary itself, only on the exclusive link that publishes it. (Found by DEX13.)
        tmp = "%s.%d.%d.tmp" % (p, os.getpid(), time.monotonic_ns())
        body = json.dumps({"run_id": run_id, **payload, **identity_record("START_GATE")},
                          sort_keys=True).encode()
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.write(fd, body)
            os.fsync(fd)
        finally:
            os.close(fd)
        try:
            publish_exclusive(tmp, p)          # exclusive: FileExistsError if already claimed
        except FileExistsError:
            os.unlink(tmp)
            return False
        self.emit(run_id, "START_GATE", payload)
        return True

    def gate_held(self, run_id):
        return os.path.exists(self.gate_path(run_id))

    def charged_rows(self):
        return sorted(n[:-5] for n in os.listdir(self.gates) if n.endswith(".gate"))

    # -- opaque publication ---------------------------------------------------------------
    def publish_raw(self, run_id, tmp_path, final_path, expect_sha256=None):
        """Seal, publish without overwrite, verify. os.replace is never used on a final raw path."""
        with open(tmp_path, "rb") as f:
            os.fsync(f.fileno())
        digest = hashlib.sha256(open(tmp_path, "rb").read()).hexdigest()
        size = os.path.getsize(tmp_path)
        if expect_sha256 and digest != expect_sha256:
            raise RuntimeError("sealed digest mismatch")
        self.emit(run_id, "RAW_SEALED", {"sha256": digest, "bytes": size,
                                         "tmp": os.path.basename(tmp_path)})
        if os.path.exists(final_path):
            have = hashlib.sha256(open(final_path, "rb").read()).hexdigest()
            if have != digest:
                raise RuntimeError("destination exists with a DIFFERENT hash: fatal")
            os.unlink(tmp_path)
            self.emit(run_id, "RAW_PUBLISHED", {"sha256": digest, "idempotent_recovery": True})
        else:
            publish_exclusive(tmp_path, final_path)
            self.emit(run_id, "RAW_PUBLISHED", {"sha256": digest, "idempotent_recovery": False})
        again = hashlib.sha256(open(final_path, "rb").read()).hexdigest()
        if again != digest:
            raise RuntimeError("published digest mismatch")
        self.emit(run_id, "VERIFIED", {"sha256": again, "bytes": size})
        return digest

    # -- recovery -------------------------------------------------------------------------
    def decide(self, run_id, worker_identity_getter):
        """The conservative recovery matrix. Returns one of:
        DISPATCH | ADOPT_AND_WAIT | FINISH_PUBLICATION | SKIP_VERIFIED | BILLED_INCOMPLETE_FATAL
        | INVARIANT_FAILURE_FATAL
        """
        st = set(self.states_of(run_id))
        gate = self.gate_held(run_id)
        ident = worker_identity_getter(run_id)
        live = bool(ident) and proc_alive(ident.get("pid"), ident.get("proc_start_ticks"))
        if "VERIFIED" in st:
            return "SKIP_VERIFIED"
        if not gate:
            if any(s in st for s in ("ENGINE_OPENED", "ADVANCE_STARTED", "ENGINE_EXIT_OK",
                                     "RAW_SEALED", "RAW_PUBLISHED")):
                return "INVARIANT_FAILURE_FATAL"      # engine evidence without a charge
            if live:
                return "ADOPT_AND_WAIT"
            return "DISPATCH"
        if live:
            return "ADOPT_AND_WAIT"
        if "RAW_PUBLISHED" in st:
            return "FINISH_PUBLICATION"
        if "RAW_SEALED" in st:
            need = ("ENGINE_OPENED", "ADVANCE_STARTED", "ENGINE_EXIT_OK")
            if all(s in st for s in need):
                return "FINISH_PUBLICATION"
            return "BILLED_INCOMPLETE_FATAL"          # RAW_SEALED alone / broken prefix
        return "BILLED_INCOMPLETE_FATAL"


# ------------------------------------------------------------------ exclusive phase lock
class PhaseLock:
    def __init__(self, path):
        self.path = path
        self.fd = None

    def acquire(self):
        self.fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            os.close(self.fd)
            self.fd = None
            return False
        os.ftruncate(self.fd, 0)
        os.write(self.fd, json.dumps(identity_record("PHASE_LOCK"), sort_keys=True).encode())
        os.fsync(self.fd)
        return True

    def release(self):
        if self.fd is not None:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            os.close(self.fd)
            self.fd = None
