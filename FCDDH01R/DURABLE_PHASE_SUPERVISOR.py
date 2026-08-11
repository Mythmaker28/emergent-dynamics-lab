"""FCDDH01R durable phase supervisor.

Engineering only: no scientific formula, no estimand, no threshold, no reader. It never decodes
science and never crosses a scientific phase barrier automatically.

Invocation (the frozen launch template, see DURABLE_EXECUTOR_SPEC.md):

    nohup setsid -f /usr/bin/python3 -u DURABLE_PHASE_SUPERVISOR.py <planfile> \
        </dev/null >>ph.log 2>>ph.err &

The plan file is a frozen JSON queue produced BEFORE launch. The supervisor:
  * detaches into its own session so no bounded launcher call can reap it;
  * holds an exclusive flock for the exact phase;
  * runs at most one billed row at a time;
  * heartbeats to a durable file every HEARTBEAT_PERIOD_SECONDS;
  * applies the conservative recovery matrix per row;
  * exits at the phase barrier.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import EXACT_ONCE_PHASE_STATE_MACHINE as SM                      # noqa: E402

HEARTBEAT_PERIOD_SECONDS = 5
MAX_SAFE_SUPERVISOR_RESTARTS_PER_PHASE = 4
AUTO_REPLAY = False
AUTO_REPLACEMENT = False
ENGINE_ROW_WALLCLOCK_TIMEOUT = None          # never; runtime may depend on state or condition


class Supervisor:
    def __init__(self, plan_path):
        self.plan = json.load(open(plan_path))
        self.root = self.plan["ledger_root"]
        self.programme = self.plan["programme"]
        self.phase = self.plan["phase"]
        self.cls = self.plan.get("execution_class", SM.EXECUTION_CLASS_REAL)
        self.max_starts = int(self.plan["phase_max_charged_starts"])
        self.led = SM.PhaseLedger(self.root, self.programme, self.phase, self.cls)
        self.status = os.path.join(self.root, "status")
        os.makedirs(self.status, exist_ok=True)
        self.hb = os.path.join(self.status, "heartbeat.json")
        self.stop = threading.Event()
        self.lock = SM.PhaseLock(os.path.join(self.root, "phase.lock"))

    # -------------------------------------------------------------- durable identity
    def _restart_count(self):
        return len([n for n in os.listdir(self.status) if n.startswith("supervisor-")])

    def announce(self):
        n = self._restart_count()
        rec = {**SM.identity_record("PHASE_SUPERVISOR"), "restart_index": n,
               "plan_sha256": self.plan["plan_sha256"],
               "code_sha256": self.plan["code_sha256"],
               "phase": self.phase, "programme": self.programme,
               "execution_class": self.cls,
               "interpreter": sys.executable, "argv": sys.argv}
        SM.write_fsync(os.path.join(self.status, "supervisor-%03d.json" % n),
                       json.dumps(rec, sort_keys=True).encode())
        SM.fsync_dir(self.status)
        SM.write_fsync(os.path.join(self.status, "READY"),
                       json.dumps(rec, sort_keys=True).encode())
        SM.fsync_dir(self.status)
        return n

    def heartbeat_loop(self):
        while not self.stop.wait(HEARTBEAT_PERIOD_SECONDS):
            try:
                SM.write_fsync(self.hb, json.dumps(
                    {"pid": os.getpid(), "phase": self.phase,
                     "proc_start_ticks": SM.proc_start_ticks(os.getpid()),
                     "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                     "note": "LIVENESS_METADATA_ONLY__NOT_EVIDENCE_OF_ROW_COMPLETION"},
                    sort_keys=True).encode())
            except Exception:
                pass

    # -------------------------------------------------------------- worker identity
    def worker_ident_path(self, run_id):
        return os.path.join(self.root, "gates", run_id + ".worker.json")

    def worker_ident(self, run_id):
        p = self.worker_ident_path(run_id)
        if not os.path.exists(p):
            return None
        try:
            return json.load(open(p))
        except Exception:
            return None

    # -------------------------------------------------------------- one row
    def run_row(self, row):
        rid = self.led.run_id(row["ordinal"], row["operator_hash"],
                              row["input_hashes"], row["schedule_position"])
        decision = self.led.decide(rid, self.worker_ident)
        if decision == "SKIP_VERIFIED":
            return "SKIP_VERIFIED", rid
        if decision in ("BILLED_INCOMPLETE_FATAL", "INVARIANT_FAILURE_FATAL"):
            return decision, rid
        if decision == "FINISH_PUBLICATION":
            self._publish_all(rid, row)
            return "FINISHED_PUBLICATION", rid
        if decision == "ADOPT_AND_WAIT":
            ident = self.worker_ident(rid)
            while SM.proc_alive(ident.get("pid"), ident.get("proc_start_ticks")):
                time.sleep(1.0)
            return self.run_row(row)          # re-evaluate with the same conservative matrix
        # ---- DISPATCH -------------------------------------------------------------
        hold = self.plan.get("dex_hold")
        if hold and row["ordinal"] == hold["before_ordinal"]:
            # DEX-only deterministic between-row barrier. Refused outright in a REAL phase, so it
            # can never influence scientific execution.
            assert self.cls == SM.EXECUTION_CLASS_DUMMY, "dex_hold is forbidden in a REAL phase"
            SM.write_fsync(os.path.join(self.status, "HOLDING"), b"{}")
            while not os.path.exists(hold["release_file"]):
                time.sleep(0.2)
        if len(self.led.charged_rows()) >= self.max_starts:
            return "PHASE_BUDGET_EXHAUSTED", rid
        self.led.emit(rid, "DISPATCH_INTENT", {"tag": row["tag"]})
        for tmp, fin in row["outputs"]:
            for p in (tmp, fin):
                d = os.path.dirname(p)
                if d:
                    os.makedirs(d, exist_ok=True)
            if os.path.exists(tmp):
                os.unlink(tmp)          # stale temporary from a NON-charged attempt; pre-gate only
        # pure pre-gate checks only; nothing here may instantiate physics
        st = os.statvfs(os.path.dirname(row["outputs"][0][0]) or ".")
        free = st.f_bavail * st.f_frsize
        if free < int(row.get("required_free_bytes", 0)):
            self.led.emit(rid, "WRAPPER_ACK", {"refused": "INSUFFICIENT_FREE_SPACE",
                                               "free_bytes": free})
            return "PRE_GATE_REFUSED_NO_SPACE", rid
        self.led.emit(rid, "WRAPPER_ACK", {"free_bytes": free})
        if not self.led.try_start_gate(rid, {"tag": row["tag"], "argv": row["argv"]}):
            return self.run_row(row)
        # ---- charged from here; the engine may now be opened exactly once ----------
        argv = [row["interpreter"], "-B"] + row["argv"] + [
            "--ack", os.path.join(self.root, "gates", rid + ".ack.json"),
            "--advance", os.path.join(self.root, "gates", rid + ".advance.json")]
        env = {k: v for k, v in os.environ.items() if k in row.get("env_whitelist", [])}
        env.update(row.get("env", {}))
        out_log = open(os.path.join(self.status, "row-%s.out" % rid), "ab", buffering=0)
        err_log = open(os.path.join(self.status, "row-%s.err" % rid), "ab", buffering=0)
        devnull = open(os.devnull, "rb")
        proc = subprocess.Popen(argv, stdin=devnull, stdout=subprocess.PIPE, stderr=err_log,
                                env=env, cwd=row.get("cwd", HERE), close_fds=True)
        SM.write_fsync(self.worker_ident_path(rid), json.dumps(
            {"pid": proc.pid, "proc_start_ticks": SM.proc_start_ticks(proc.pid),
             "boot_id": SM.boot_id(), "argv": argv,
             "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, sort_keys=True).encode())
        SM.fsync_dir(os.path.dirname(self.worker_ident_path(rid)))
        self.led.emit(rid, "ENGINE_OPENED", {"pid": proc.pid})
        stdout, _ = proc.communicate()          # no wall-clock timeout, by design
        out_log.write(stdout or b"")
        out_log.close()
        err_log.close()
        devnull.close()
        adv = os.path.join(self.root, "gates", rid + ".advance.json")
        if os.path.exists(adv):
            self.led.emit(rid, "ADVANCE_STARTED", {"marker": os.path.basename(adv)})
        if proc.returncode != 0:
            self.led.emit(rid, "ENGINE_OPENED", {"returncode": proc.returncode,
                                                 "note": "NON_ZERO_EXIT"})
            return "BILLED_INCOMPLETE_FATAL", rid
        self.led.emit(rid, "ENGINE_EXIT_OK", {"returncode": 0,
                                              "stdout_sha256": SM.hashlib.sha256(
                                                  stdout or b"").hexdigest()})
        payload = json.loads((stdout or b"{}").decode().strip().splitlines()[-1])
        SM.write_fsync(os.path.join(self.status, "row-%s.payload.json" % rid),
                       json.dumps(payload, sort_keys=True).encode())
        try:
            self._publish_all(rid, row)
        except Exception as exc:
            self.led.emit(rid, "ENGINE_EXIT_OK", {"publication_error": repr(exc)})
            return "BILLED_INCOMPLETE_FATAL", rid
        return "VERIFIED", rid

    def _publish_all(self, rid, row):
        """Seal then publish every declared output without overwrite, then verify."""
        digests = {}
        for tmp, fin in row["outputs"]:
            if os.path.exists(fin) and not os.path.exists(tmp):
                digests[os.path.basename(fin)] = SM.hashlib.sha256(
                    open(fin, "rb").read()).hexdigest()
                continue
            if not os.path.exists(tmp):
                raise RuntimeError("declared output missing: %s" % tmp)
            digests[os.path.basename(fin)] = self.led.publish_raw(rid, tmp, fin)
        self.led.emit(rid, "VERIFIED", {"outputs": digests})
        return digests

    # -------------------------------------------------------------- the phase
    def run(self):
        if not self.lock.acquire():
            SM.write_fsync(os.path.join(self.status, "REFUSED_DUPLICATE_SUPERVISOR"),
                           json.dumps(SM.identity_record("REFUSED"), sort_keys=True).encode())
            return 3
        req = self.plan.get("required_prior_artifact")
        if req:
            p, want = req["path"], req["sha256"]
            got = (SM.hashlib.sha256(open(p, "rb").read()).hexdigest()
                   if os.path.isfile(p) else None)
            if got != want:
                SM.write_fsync(os.path.join(self.status, "REFUSED_PHASE_BARRIER"),
                               json.dumps({"required": req, "found_sha256": got},
                                          sort_keys=True).encode())
                self.lock.release()
                return 6
        n = self.announce()
        if n >= MAX_SAFE_SUPERVISOR_RESTARTS_PER_PHASE + 1:
            SM.write_fsync(os.path.join(self.status, "REFUSED_RESTART_CEILING"),
                           json.dumps({"restart_index": n,
                                       "ceiling": MAX_SAFE_SUPERVISOR_RESTARTS_PER_PHASE},
                                      sort_keys=True).encode())
            self.lock.release()
            return 4
        t = threading.Thread(target=self.heartbeat_loop, daemon=True)
        t.start()
        results = []
        rc = 0
        accepted, burned = set(), set()
        target = self.plan.get("stop_after_accepted_candidates")
        cblock = int(self.plan.get("operations_per_candidate", 1))
        for row in self.plan["rows"]:
            cand = row.get("candidate")
            if target is not None:
                if len(accepted) >= target:
                    break
                if cand in burned:
                    continue                      # whole candidate rejected; never resumed
                remaining = self.max_starts - len(self.led.charged_rows())
                if (target - len(accepted)) * cblock > remaining and cand not in accepted:
                    results.append({"tag": row["tag"], "run_id": None,
                                    "outcome": "STOP_TARGET_NO_LONGER_ATTAINABLE"})
                    rc = 7
                    break
            outcome, rid = self.run_row(row)
            results.append({"tag": row["tag"], "run_id": rid, "outcome": outcome,
                            "candidate": row.get("candidate")})
            SM.write_fsync(os.path.join(self.status, "progress.json"), json.dumps(
                {"done": len(results), "total": len(self.plan["rows"]),
                 "charged": len(self.led.charged_rows()),
                 "last": results[-1]}, sort_keys=True).encode())
            if target is not None:
                if outcome in ("VERIFIED", "SKIP_VERIFIED", "FINISHED_PUBLICATION"):
                    ok = json.load(open(os.path.join(
                        self.status, "row-%s.payload.json" % rid))) if os.path.exists(
                        os.path.join(self.status, "row-%s.payload.json" % rid)) else {}
                    if ok.get("accepted") is False:
                        burned.add(cand)
                        continue
                    if sum(1 for r in results if r.get("candidate") == cand
                           and r["outcome"] in ("VERIFIED", "SKIP_VERIFIED",
                                                "FINISHED_PUBLICATION")) == cblock:
                        accepted.add(cand)
                    continue
                if outcome in ("BILLED_INCOMPLETE_FATAL", "INVARIANT_FAILURE_FATAL"):
                    burned.add(cand)              # burn the whole candidate, never resume
                    continue
            if outcome in ("BILLED_INCOMPLETE_FATAL", "INVARIANT_FAILURE_FATAL",
                           "PHASE_BUDGET_EXHAUSTED", "PRE_GATE_REFUSED_NO_SPACE"):
                rc = 5
                break
        final = {"accepted_candidates": sorted(accepted), "burned_candidates": sorted(burned),
                 "phase": self.phase, "programme": self.programme,
                 "execution_class": self.cls, "results": results,
                 "charged_rows": len(self.led.charged_rows()),
                 "expected_rows": len(self.plan["rows"]),
                 "wal_monotone_violations": self.led.verify_monotone(),
                 "PHASE_COMPLETE": (rc == 0 and (len(accepted) >= target if target is not None
                                                 else len(results) == len(self.plan["rows"]))),
                 "rc": rc, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        SM.write_fsync(os.path.join(self.status, "PHASE_RESULT.json"),
                       json.dumps(final, sort_keys=True, default=str).encode())
        if final["PHASE_COMPLETE"]:
            SM.write_fsync(os.path.join(self.status, "PHASE_COMPLETE"),
                           json.dumps(final, sort_keys=True, default=str).encode())
        SM.fsync_dir(self.status)
        self.stop.set()
        self.lock.release()
        return rc


if __name__ == "__main__":
    sys.exit(Supervisor(sys.argv[1]).run())
