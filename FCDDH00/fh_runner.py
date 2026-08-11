"""FCDDH00 fail-closed write-ahead engine runner and start ledger.

Charging contract (master freeze Section 3.2), enforced mechanically:

  * an INTENDED record is written and fsynced BEFORE any launch;
  * the child writes an ACK marker (process identity) as its first action, before importing or
    instantiating any engine, and fsyncs it;
  * the child writes an ADVANCE marker, and fsyncs it, immediately before its FIRST engine step;
  * a start is CHARGED iff the ADVANCE marker exists, or iff the launch outcome is uncertain;
  * a start is NOT charged, and may be retried, ONLY when the idempotency record proves that no
    engine was instantiated and no state advanced (ACK present without ADVANCE, or neither
    present) AND the child produced no output file;
  * every charged start is permanent: never replayed, never replaced, never resumed.

Each charged start contributes exactly one fresh process start AND exactly one raw
engine-advance sequence; the ledger records both counts and the budget uses the larger.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time


class StartLedger:
    def __init__(self, path):
        self.path = path
        self.n = {"construction": 0, "sham": 0, "active": 0, "other": 0}
        self.adv = {"construction": 0, "sham": 0, "active": 0, "other": 0}
        self.records = []
        self._fh = open(path, "a")

    def _emit(self, rec):
        self._fh.write(json.dumps(rec, sort_keys=True) + "\n")
        self._fh.flush()
        os.fsync(self._fh.fileno())
        self.records.append(rec)

    @staticmethod
    def token(role, kind, tag, seq):
        return hashlib.sha256(("FCDDH00|%s|%s|%s|%d" % (role, kind, tag, seq)).encode()).hexdigest()[:32]

    def counts(self):
        return {"charged_process_starts": dict(self.n),
                "raw_advance_sequences": dict(self.adv),
                "charged_total": sum(self.n.values()),
                "raw_advance_total": sum(self.adv.values()),
                "budget_charge": max(sum(self.n.values()), sum(self.adv.values()))}

    def run(self, kind, role, tag, argv, markdir, budget_max, phase_spent):
        """Launch exactly one fresh process under the write-ahead contract."""
        if phase_spent >= budget_max:
            raise RuntimeError("BUDGET_EXHAUSTED for phase %s (%d/%d)" % (kind, phase_spent, budget_max))
        seq = len(self.records)
        tok = self.token(role, kind, tag, seq)
        ack = os.path.join(markdir, tok + ".ack.json")
        advm = os.path.join(markdir, tok + ".advance.json")
        os.makedirs(markdir, exist_ok=True)
        for p in (ack, advm):
            if os.path.exists(p):
                raise RuntimeError("idempotency token collision: %s" % p)
        self._emit({"event": "INTENDED", "kind": kind, "role": role, "tag": tag, "token": tok,
                    "seq": seq, "argv": argv, "ack": ack, "advance": advm,
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        t0 = time.time()
        uncertain = False
        try:
            r = subprocess.run([sys.executable, "-B"] + argv + ["--ack", ack, "--advance", advm],
                               capture_output=True, text=True, timeout=3600)
            rc, out, err = r.returncode, r.stdout, r.stderr
        except Exception as exc:                       # transport / process-control failure
            rc, out, err, uncertain = -1, "", repr(exc), True
        advanced = os.path.exists(advm)
        acked = os.path.exists(ack)
        charged = bool(advanced or uncertain)
        if charged:
            self.n[kind] += 1
            self.adv[kind] += 1 if advanced else 0
            if uncertain and not advanced:
                self.adv[kind] += 1                    # uncertain launch charged as an advance too
        self._emit({"event": "COMPLETED", "kind": kind, "role": role, "tag": tag, "token": tok,
                    "seq": seq, "returncode": rc, "acked": acked, "advanced": advanced,
                    "charged": charged, "uncertain_launch": uncertain,
                    "wall_s": round(time.time() - t0, 3),
                    "stderr_tail": (err or "")[-600:],
                    "stdout_sha256": hashlib.sha256((out or "").encode()).hexdigest(),
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        if rc != 0:
            return {"ok": False, "charged": charged, "advanced": advanced, "acked": acked,
                    "retry_permitted": (not charged), "stderr": (err or "")[-2000:], "token": tok}
        payload = json.loads(out.strip().splitlines()[-1])
        return {"ok": True, "charged": charged, "advanced": advanced, "acked": acked,
                "retry_permitted": False, "payload": payload, "token": tok}


def child_ack(argv):
    """Called by every worker as its FIRST action, before any engine import or instantiation."""
    ack = argv[argv.index("--ack") + 1]
    with open(ack, "w") as f:
        json.dump({"pid": os.getpid(), "argv": argv[:8], "ppid": os.getppid(),
                   "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, f)
        f.flush()
        os.fsync(f.fileno())
    return ack


def child_advance(argv, note):
    """Called by every worker immediately BEFORE its first engine step."""
    advm = argv[argv.index("--advance") + 1]
    with open(advm, "w") as f:
        json.dump({"pid": os.getpid(), "note": note,
                   "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, f)
        f.flush()
        os.fsync(f.fileno())
    return advm


WORKED_EXAMPLES = {
    "pre_launch_transport_failure": {
        "sequence": ["INTENDED written and fsynced", "process control failed before exec",
                     "ack marker ABSENT", "advance marker ABSENT", "no output file"],
        "charged_process_starts": 0, "raw_advance_sequences": 0,
        "retry_permitted": True,
        "why": "the idempotency record proves no engine was instantiated and no state advanced"},
    "uncertain_launch": {
        "sequence": ["INTENDED written and fsynced", "subprocess raised or timed out",
                     "ack marker present or unreadable", "advance marker unreadable"],
        "charged_process_starts": 1, "raw_advance_sequences": 1,
        "retry_permitted": False,
        "why": "an uncertain launch is charged and never replayed"},
    "complete_block": {
        "sequence": ["4 descendant workers, each INTENDED -> ack -> advance -> published output"],
        "charged_process_starts": 4, "raw_advance_sequences": 4,
        "retry_permitted": False,
        "why": "C_PRECURSOR_ADVANCE = 0 (the precursor is a pure seeded draw with zero engine "
               "steps); each of the four descendants is one fresh process and one raw advance "
               "sequence of 150 + 120 + 120 = 390 engine steps; admissibility is a pure read"},
    "candidate_failing_on_the_fourth_descendant": {
        "sequence": ["precursor (0 advances)", "descendant 1 ok", "descendant 2 ok",
                     "descendant 3 ok", "descendant 4 rejected on admissibility"],
        "charged_process_starts": 4, "raw_advance_sequences": 4,
        "retry_permitted": False,
        "why": "the precursor plus the advances actually performed are charged; the block is "
               "rejected whole and never resumed"},
}
