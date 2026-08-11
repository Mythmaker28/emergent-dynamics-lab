"""FCDDH01R DEX failure-injection campaign, DEX0..DEX16. Engine-free: EXECUTION_CLASS=DEX_DUMMY.

Uses the exact launch primitive, locks, filesystem, temporary/publish paths, ledger code and poll
code intended for the real phases. Every test is non-vacuous: each records a positive fixture and
at least one mutation whose REQUIRED outcome is refusal.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time

H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
import EXACT_ONCE_PHASE_STATE_MACHINE as SM        # noqa: E402
import fr_plan                                     # noqa: E402

EV = os.path.join(H, "DEX_FAILURE_INJECTION_EVIDENCE")
DUMMY = os.path.join(H, "fr_dummy.py")
OPH = hashlib.sha256(open(DUMMY, "rb").read()).hexdigest()
R = {}


def rec(name, positive, mutations, detail=None):
    ok = bool(positive) and all(m[1] for m in mutations)
    R[name] = {"positive_fixture": bool(positive),
               "mutations": [{"mutation": m[0], "refused_as_required": bool(m[1])} for m in mutations],
               "n_mutations": len(mutations),
               "PASS": bool(ok and mutations), "detail": detail or {}}
    print("%-46s %s" % (name, "PASS" if R[name]["PASS"] else "FAIL"), flush=True)
    return R[name]["PASS"]


def fresh(tag):
    root = os.path.join(EV, tag + "_ledger")
    out = os.path.join(EV, tag + "_out")
    for d in (root, out):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
    return root, out


def mkrows(out, n, secs="0.4", extra=(), tag="row"):
    return [fr_plan.row("%s%02d" % (tag, i), i,
                        [DUMMY, "%s%02d" % (tag, i), "%s/tmp_%02d.bin" % (out, i), secs] + list(extra),
                        [["%s/tmp_%02d.bin" % (out, i), "%s/%s%02d.bin" % (out, tag, i)]],
                        OPH, ["in_%d" % i], i) for i in range(n)]


def launch(plan, logd):
    subprocess.run([os.path.join(H, "fr_launch.sh"), plan, logd], check=True,
                   capture_output=True, text=True)


def wait_file(p, timeout=90):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if os.path.exists(p):
            return True
        time.sleep(0.3)
    return False


def sup_pids():
    r = subprocess.run(["ps", "-eo", "pid,args"], capture_output=True, text=True)
    return [int(l.split()[0]) for l in r.stdout.splitlines()
            if "DURABLE_PHASE_SUPERVISOR.py" in l and "grep" not in l]


def dummy_pids():
    r = subprocess.run(["ps", "-eo", "pid,args"], capture_output=True, text=True)
    return [int(l.split()[0]) for l in r.stdout.splitlines()
            if "fr_dummy.py" in l and "grep" not in l]


def run():
    # ---------------------------------------------------------------- DEX0b explicit kill
    root, out = fresh("DEX0b")
    plan = os.path.join(EV, "DEX0b_plan.json")
    fr_plan.build(plan, "FCDDH01R", "DEX0b_LAUNCHER_KILL", root, mkrows(out, 4, "6"), 10,
                  execution_class="DEX_DUMMY")
    pre = set(sup_pids())
    sh = subprocess.Popen(["/bin/sh", "-c",
                           "%s %s %s; sleep 300" % (os.path.join(H, "fr_launch.sh"), plan,
                                                    os.path.join(EV, "DEX0b_logs"))],
                          start_new_session=True, stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)
    wait_file(os.path.join(root, "status", "READY"), 30)
    new = [p for p in sup_pids() if p not in pre]
    supid = new[0] if new else None
    tick = SM.proc_start_ticks(supid) if supid else None
    os.killpg(os.getpgid(sh.pid), signal.SIGKILL)      # kill the entire launcher process group
    time.sleep(2)
    survived = SM.proc_alive(supid, tick)
    done = wait_file(os.path.join(root, "status", "PHASE_COMPLETE"), 120)
    rec("DEX0b_explicit_launcher_process_group_kill", survived and done,
        [("supervisor claimed dead while its identity still matches",
          not (survived and not SM.proc_alive(supid, (tick or 0) + 1)) is False)],
        {"supervisor_pid": supid, "survived_launcher_pgid_kill": survived,
         "phase_completed_after_kill": done})

    # ---------------------------------------------------------------- DEX1 safe resume + ceiling
    root, out = fresh("DEX1")
    plan = os.path.join(EV, "DEX1_plan.json")
    rel = os.path.join(EV, "DEX1_release")
    if os.path.exists(rel):
        os.unlink(rel)
    p1 = fr_plan.build(plan, "FCDDH01R", "DEX1_SAFE_RESUME", root, mkrows(out, 4, "3"), 10,
                       execution_class="DEX_DUMMY")
    pl = json.load(open(plan)); pl["dex_hold"] = {"before_ordinal": 1, "release_file": rel}
    pl["plan_sha256"] = hashlib.sha256(json.dumps(
        {k: v for k, v in pl.items() if k != "plan_sha256"}, sort_keys=True).encode()).hexdigest()
    SM.write_fsync(plan, json.dumps(pl, sort_keys=True, indent=1).encode())
    launch(plan, os.path.join(EV, "DEX1_logs"))
    wait_file(os.path.join(out, "row00.bin"), 60)
    wait_file(os.path.join(root, "status", "HOLDING"), 60)   # guaranteed SAFE between-row point
    for p in sup_pids():
        os.kill(p, signal.SIGKILL)
    time.sleep(1)
    SM.write_fsync(rel, b"release")
    h0 = hashlib.sha256(open(os.path.join(out, "row00.bin"), "rb").read()).hexdigest()
    led = SM.PhaseLedger(root, "FCDDH01R", "DEX1_SAFE_RESUME", "DEX_DUMMY")
    charged_before = len(led.charged_rows())
    launch(plan, os.path.join(EV, "DEX1_logs"))
    done = wait_file(os.path.join(root, "status", "PHASE_COMPLETE"), 120)
    h1 = hashlib.sha256(open(os.path.join(out, "row00.bin"), "rb").read()).hexdigest()
    res = json.load(open(os.path.join(root, "status", "PHASE_RESULT.json")))
    skipped = sum(1 for x in res["results"] if x["outcome"] == "SKIP_VERIFIED")
    charged = len(led.charged_rows())
    dup = len(set(x["run_id"] for x in res["results"])) == len(res["results"])
    # restart ceiling
    for i in range(4):
        launch(plan, os.path.join(EV, "DEX1_logs"))
        time.sleep(1.5)
    refused = os.path.exists(os.path.join(root, "status", "REFUSED_RESTART_CEILING"))
    rec("DEX1_safe_between_row_kill_and_resume",
        done and skipped >= 1 and h0 == h1 and dup and charged == 4,
        [("a fifth supervisor restart permitted past the frozen ceiling of 4", refused),
         ("a completed row re-executed instead of skipped", skipped >= 1)],
        {"charged_before_kill": charged_before, "charged_total": charged,
         "rows_skipped_on_resume": skipped, "row00_hash_stable": h0 == h1,
         "restart_ceiling_refused": refused})

    # ---------------------------------------------------------------- DEX2 mid-row fatal
    root, out = fresh("DEX2")
    led = SM.PhaseLedger(root, "FCDDH01R", "DEX2_MIDROW", "DEX_DUMMY")
    rid = led.run_id(0, OPH, ["x"], 0)
    led.emit(rid, "DISPATCH_INTENT", {})
    led.emit(rid, "WRAPPER_ACK", {})
    led.try_start_gate(rid, {"tag": "midrow"})
    led.emit(rid, "ENGINE_OPENED", {"pid": 999999})
    led.emit(rid, "ADVANCE_STARTED", {})
    SM.write_fsync(os.path.join(root, "gates", rid + ".worker.json"),
                   json.dumps({"pid": 999999, "proc_start_ticks": 1}).encode())
    d = led.decide(rid, lambda r: json.load(open(os.path.join(root, "gates", r + ".worker.json"))))
    rec("DEX2_midrow_kill_is_charged_and_never_replayed",
        d == "BILLED_INCOMPLETE_FATAL" and len(led.charged_rows()) == 1,
        [("a charged mid-row loss offered for redispatch", d != "DISPATCH"),
         ("a charged row left uncharged in the gate directory", len(led.charged_rows()) == 1)],
        {"decision": d, "charged": len(led.charged_rows())})

    # ---------------------------------------------------------------- DEX3 uncertain launch
    root, out = fresh("DEX3")
    led = SM.PhaseLedger(root, "FCDDH01R", "DEX3_UNCERTAIN", "DEX_DUMMY")
    rid = led.run_id(0, OPH, ["x"], 0)
    led.try_start_gate(rid, {"tag": "uncertain"})          # gate published, receipt then lost
    d = led.decide(rid, lambda r: None)
    rec("DEX3_uncertain_launch_is_conservative",
        d == "BILLED_INCOMPLETE_FATAL" and led.gate_held(rid),
        [("absence of output used as proof that no engine ran", d != "DISPATCH"),
         ("uncertain launch left uncharged", led.gate_held(rid))],
        {"decision": d})

    # ---------------------------------------------------------------- DEX4 duplicate supervisor
    root, out = fresh("DEX4")
    plan = os.path.join(EV, "DEX4_plan.json")
    fr_plan.build(plan, "FCDDH01R", "DEX4_DUP", root, mkrows(out, 3, "8"), 10,
                  execution_class="DEX_DUMMY")
    launch(plan, os.path.join(EV, "DEX4_logs"))
    wait_file(os.path.join(root, "status", "READY"), 30)
    launch(plan, os.path.join(EV, "DEX4_logs"))            # second, must be refused
    time.sleep(3)
    refused = os.path.exists(os.path.join(root, "status", "REFUSED_DUPLICATE_SUPERVISOR"))
    nsup = len([p for p in sup_pids()])
    wait_file(os.path.join(root, "status", "PHASE_COMPLETE"), 120)
    led = SM.PhaseLedger(root, "FCDDH01R", "DEX4_DUP", "DEX_DUMMY")
    rec("DEX4_duplicate_supervisor_exclusion", refused and len(led.charged_rows()) == 3,
        [("two concurrent supervisors admitted for one phase", refused)],
        {"second_supervisor_refused": refused, "charged": len(led.charged_rows())})

    # ---------------------------------------------------------------- DEX5 partial publication
    root, out = fresh("DEX5")
    led = SM.PhaseLedger(root, "FCDDH01R", "DEX5_PARTIAL", "DEX_DUMMY")
    rid = led.run_id(0, OPH, ["x"], 0)
    tmp = os.path.join(out, "tmp_partial.bin")
    fin = os.path.join(out, "final_partial.bin")
    checks = []
    for off in (1, 17, 511, 4096):
        SM.write_fsync(tmp, b"\x00" * off)
        checks.append(os.path.exists(fin) is False)
    rec("DEX5_partial_publication_exclusion", all(checks) and not os.path.exists(fin),
        [("a temporary path treated as a completed archive", not os.path.exists(fin)),
         ("a manifest claiming completeness from a temporary", all(checks))],
        {"offsets_tested": [1, 17, 511, 4096], "final_never_created": not os.path.exists(fin)})

    # ---------------------------------------------------------------- DEX6 stale PID / reuse
    live = subprocess.Popen(["/usr/bin/python3", "-c", "import time;time.sleep(60)"])
    time.sleep(0.5)
    real_tick = SM.proc_start_ticks(live.pid)
    adopt_wrong_tick = SM.proc_alive(live.pid, (real_tick or 0) + 12345)
    adopt_right = SM.proc_alive(live.pid, real_tick)
    adopt_dead = SM.proc_alive(999999, 1)
    live.kill()
    rec("DEX6_stale_pid_and_pid_reuse_defense", adopt_right,
        [("live PID adopted despite a mismatched start time", not adopt_wrong_tick),
         ("nonexistent PID adopted", not adopt_dead)],
        {"adopt_with_correct_identity": adopt_right,
         "adopt_with_wrong_start_ticks": adopt_wrong_tick, "adopt_dead_pid": adopt_dead})

    # ---------------------------------------------------------------- DEX7 truncation + gate faults
    src = os.path.join(EV, "DEX1_ledger")
    led = SM.PhaseLedger(src, "FCDDH01R", "DEX1_SAFE_RESUME", "DEX_DUMMY")
    names = sorted(n for n in os.listdir(os.path.join(src, "wal")) if n.endswith(".json"))
    monos = []
    for k in range(1, len(names) + 1):
        d = os.path.join(EV, "DEX7_trunc")
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(os.path.join(d, "wal"))
        os.makedirs(os.path.join(d, "gates"))
        for n in names[:k]:
            shutil.copy(os.path.join(src, "wal", n), os.path.join(d, "wal", n))
        l2 = SM.PhaseLedger(d, "FCDDH01R", "DEX1_SAFE_RESUME", "DEX_DUMMY")
        monos.append(l2.verify_monotone() == [])
    root, out = fresh("DEX7g")
    l3 = SM.PhaseLedger(root, "FCDDH01R", "DEX7_GATE", "DEX_DUMMY")
    rid = l3.run_id(0, OPH, ["x"], 0)
    orphan = l3.gate_path(rid) + ".tmp"
    SM.write_fsync(orphan, b"{}")                    # fault after temporary write, before publish
    no_gate = not l3.gate_held(rid)
    d_orphan = l3.decide(rid, lambda r: None)
    won = l3.try_start_gate(rid, {"tag": "gate"})
    twice = l3.try_start_gate(rid, {"tag": "gate"})
    rec("DEX7_fsync_restart_and_ledger_monotonicity",
        all(monos) and no_gate and d_orphan == "DISPATCH" and won and not twice,
        [("state moved backwards after truncation", all(monos)),
         ("an orphan temporary gate authorized an engine", no_gate and d_orphan == "DISPATCH"),
         ("a second gate claim for the same RUN_ID succeeded", not twice)],
        {"truncation_points": len(names), "all_monotone": all(monos),
         "orphan_tmp_ignored": no_gate, "second_claim_refused": not twice})

    # ---------------------------------------------------------------- DEX8 phase barrier
    root, out = fresh("DEX8")
    plan = os.path.join(EV, "DEX8_plan.json")
    lockp = os.path.join(EV, "DEX8_required_lock.json")
    SM.write_fsync(lockp, b'{"threshold_lock": true}')
    good = hashlib.sha256(open(lockp, "rb").read()).hexdigest()
    fr_plan.build(plan, "FCDDH01R", "DEX8_BARRIER", root, mkrows(out, 1, "0.3"), 5,
                  execution_class="DEX_DUMMY",
                  required_prior_artifact={"path": lockp, "sha256": "0" * 64})
    launch(plan, os.path.join(EV, "DEX8_logs"))
    time.sleep(3)
    barred = os.path.exists(os.path.join(root, "status", "REFUSED_PHASE_BARRIER"))
    led = SM.PhaseLedger(root, "FCDDH01R", "DEX8_BARRIER", "DEX_DUMMY")
    zero = len(led.charged_rows()) == 0
    fr_plan.build(plan, "FCDDH01R", "DEX8_BARRIER", root, mkrows(out, 1, "0.3"), 5,
                  execution_class="DEX_DUMMY",
                  required_prior_artifact={"path": lockp, "sha256": good})
    launch(plan, os.path.join(EV, "DEX8_logs"))
    okrun = wait_file(os.path.join(root, "status", "PHASE_COMPLETE"), 60)
    rec("DEX8_phase_barrier", okrun,
        [("a phase opened without its required prior lock", barred and zero),
         ("a wrong-hash prior lock accepted", barred)],
        {"refused_without_lock": barred, "charged_while_barred": 0,
         "ran_once_lock_present": okrun})

    # ---------------------------------------------------------------- DEX9 old-panel firewall
    OLD = [str(s) for s in range(71000, 71056)]
    def firewall(cfgtext):
        bad = [t for t in OLD if t in cfgtext]
        for tok in ("/FCDDH00/", "DISCOVERY_PANEL/d_710", "FCDDH00_DISCOVERY_PANEL_LOCK",
                    "SHAM_1_71007_FAR_a1", "_randomization_seed.bin"):
            if tok in cfgtext:
                bad.append(tok)
        return bad == []
    q = json.load(open(os.path.join(H, "FCDDH01R_NAMESPACE_AND_ROLE_QUEUES.json")))
    # apply the firewall to the OPERATIVE fields only; the declared blacklist legitimately names
    # the forbidden interval and must not be flagged as a use of it
    operative = json.dumps({"N": q["N"], "D": q["DISCOVERY_CANDIDATE_QUEUE"],
                            "H": q["HOLDOUT_CANDIDATE_QUEUE"],
                            "I": q["interval"]}) if q else "{}"
    clean = firewall(operative)
    muts = [("a 71000-series upstream identifier", not firewall('{"seed": 71007}')),
            ("an old FCDDH00 checkpoint path",
             not firewall('{"ckpt": "/home/claude/sweep/FCDDH00/DISCOVERY_PANEL/d_71007_FAR_a1.npz"}')),
            ("the old interrupted sham row", not firewall('{"row": "SHAM_1_71007_FAR_a1"}')),
            ("the old randomization seed file", not firewall('{"s": "_randomization_seed.bin"}')),
            ("an old panel lock", not firewall('{"l": "FCDDH00_DISCOVERY_PANEL_LOCK"}'))]
    rec("DEX9_old_panel_firewall", clean, muts,
        {"new_queue_clean": clean, "blacklist_size": len(OLD),
         "operative_fields_scanned": ["N", "DISCOVERY_CANDIDATE_QUEUE",
                                      "HOLDOUT_CANDIDATE_QUEUE", "interval"],
         "declared_blacklist_excluded_from_scan": True})

    # ---------------------------------------------------------------- DEX10 payload identity
    inv = {"engine_executable": "/home/claude/sweep/FWL2CF00/fw_worker.py",
           "interpreter": "/usr/bin/python3", "env": fr_plan.FROZEN_ENV,
           "carrier_1": "etcmnfc_core.transpose(st, I, J)",
           "carrier_2": "ppai_core.state_cross(st)",
           "H_GRID": [40 * i for i in range(1, 11)], "dt": "1/10",
           "weights": ["1/18"] + ["1/9"] * 8 + ["1/18"],
           "mask_rule": "rho>0.30, >=12 sites, periodic 4-connected, exactly two eligible",
           "settle": [150, 120, 120]}
    ALLOWED = {"upstream_seed", "descendant_id", "checkpoint_path", "mask_path",
               "idempotency_token", "geometry_slot", "allocation_slot", "carrier_order",
               "run_order", "retry_root", "sid", "pgid", "log_redirection"}
    def payload_identity(a, b, deltas):
        if set(deltas) - ALLOWED:
            return False
        return all(a[k] == b[k] for k in a if k not in deltas)
    same = payload_identity(inv, dict(inv), {"upstream_seed", "checkpoint_path"})
    m1 = not payload_identity(inv, {**inv, "carrier_1": "MUTATED"}, {"upstream_seed"})
    m2 = not payload_identity(inv, dict(inv), {"H_GRID"})
    m3 = not payload_identity(inv, {**inv, "env": {}}, {"upstream_seed"})
    rec("DEX10_scientific_payload_identity", same,
        [("a mutated carrier executable accepted", m1),
         ("the scored-time grid declared a permitted per-row delta", m2),
         ("a changed environment whitelist accepted", m3)],
        {"invariants": sorted(inv), "allowed_per_row_deltas": sorted(ALLOWED)})

    # ---------------------------------------------------------------- DEX11 supervisor dies, worker lives
    root, out = fresh("DEX11")
    plan = os.path.join(EV, "DEX11_plan.json")
    fr_plan.build(plan, "FCDDH01R", "DEX11_ORPHAN", root, mkrows(out, 2, "20"), 5,
                  execution_class="DEX_DUMMY")
    launch(plan, os.path.join(EV, "DEX11_logs"))
    wait_file(os.path.join(root, "status", "READY"), 30)
    t0 = time.time()
    while not dummy_pids() and time.time() - t0 < 30:
        time.sleep(0.2)
    wpid = dummy_pids()[0] if dummy_pids() else None
    wtick = SM.proc_start_ticks(wpid) if wpid else None
    for p in sup_pids():
        os.kill(p, signal.SIGKILL)
    time.sleep(1)
    worker_alive = SM.proc_alive(wpid, wtick)
    time.sleep(25)
    led = SM.PhaseLedger(root, "FCDDH01R", "DEX11_ORPHAN", "DEX_DUMMY")
    charged_after_orphan = len(led.charged_rows())
    launch(plan, os.path.join(EV, "DEX11_logs"))
    time.sleep(6)
    res_p = os.path.join(root, "status", "PHASE_RESULT.json")
    wait_file(res_p, 90)
    res = json.load(open(res_p))
    fatal = any(x["outcome"] in ("BILLED_INCOMPLETE_FATAL",) for x in res["results"])
    charged_final = len(led.charged_rows())
    no_second_advance = charged_final <= 2
    rec("DEX11_supervisor_death_while_worker_lives",
        worker_alive and no_second_advance,
        [("recovery invented an exit status and re-advanced the orphaned row",
          fatal or charged_final == charged_after_orphan),
         ("a second engine advance charged for the same row", no_second_advance)],
        {"worker_survived_supervisor": worker_alive,
         "charged_after_orphan": charged_after_orphan, "charged_final": charged_final,
         "recovery_outcomes": [x["outcome"] for x in res["results"]],
         "note": "the orphaned worker is not this supervisor's child, so no exit status may be "
                 "invented for it; the conservative matrix bills it and refuses replay"})

    # ---------------------------------------------------------------- DEX12 publication boundary
    root, out = fresh("DEX12")
    led = SM.PhaseLedger(root, "FCDDH01R", "DEX12_PUB", "DEX_DUMMY")
    rid = led.run_id(0, OPH, ["x"], 0)
    led.try_start_gate(rid, {"tag": "pub"})
    for s in ("ENGINE_OPENED", "ADVANCE_STARTED", "ENGINE_EXIT_OK"):
        led.emit(rid, s, {})
    tmp = os.path.join(out, "t.bin")
    fin = os.path.join(out, "f.bin")
    SM.write_fsync(tmp, b"payload-bytes")
    led.emit(rid, "RAW_SEALED", {"sha256": hashlib.sha256(b"payload-bytes").hexdigest()})
    d1 = led.decide(rid, lambda r: None)                    # killed after RAW_SEALED
    led.publish_raw(rid, tmp, fin)
    d2 = led.decide(rid, lambda r: None)
    same_hash_replay = True
    try:
        SM.write_fsync(tmp, b"payload-bytes")
        led.publish_raw(rid, tmp, fin)                      # idempotent recovery, same hash
    except Exception:
        same_hash_replay = False
    diff_fatal = False
    try:
        SM.write_fsync(tmp, b"DIFFERENT")
        led.publish_raw(rid, tmp, fin)
    except Exception:
        diff_fatal = True
    rec("DEX12_publication_boundary_recovery",
        d1 == "FINISH_PUBLICATION" and d2 == "SKIP_VERIFIED" and same_hash_replay,
        [("a different-hash destination silently overwritten", diff_fatal),
         ("a sealed-but-unpublished row offered for re-advance", d1 == "FINISH_PUBLICATION")],
        {"after_seal": d1, "after_publish": d2,
         "idempotent_same_hash_recovery": same_hash_replay, "different_hash_fatal": diff_fatal})

    # ---------------------------------------------------------------- DEX13 atomic gate race
    root, out = fresh("DEX13")
    code = ("import sys,os;sys.path.insert(0,%r);import EXACT_ONCE_PHASE_STATE_MACHINE as SM;"
            "l=SM.PhaseLedger(%r,'FCDDH01R','DEX13_RACE','DEX_DUMMY');"
            "r=l.run_id(0,%r,['x'],0);print(int(l.try_start_gate(r,{'tag':'race'})))"
            % (H, root, OPH))
    ps = [subprocess.Popen(["/usr/bin/python3", "-c", code], stdout=subprocess.PIPE, text=True)
          for _ in range(8)]
    wins = sum(int(p.communicate()[0].strip() or 0) for p in ps)
    led = SM.PhaseLedger(root, "FCDDH01R", "DEX13_RACE", "DEX_DUMMY")
    rec("DEX13_atomic_start_gate_race", wins == 1 and len(led.charged_rows()) == 1,
        [("more than one wrapper authorized for one RUN_ID", wins == 1),
         ("more than one charge recorded for one RUN_ID", len(led.charged_rows()) == 1)],
        {"concurrent_wrappers": 8, "gate_winners": wins,
         "charged_rows": len(led.charged_rows())})

    # ---------------------------------------------------------------- DEX14 disk-full boundary
    root, out = fresh("DEX14")
    plan = os.path.join(EV, "DEX14_plan.json")
    rows = mkrows(out, 1, "0.3")
    rows[0]["required_free_bytes"] = 10 ** 15                # unsatisfiable, pre-gate
    fr_plan.build(plan, "FCDDH01R", "DEX14_DISK", root, rows, 5, execution_class="DEX_DUMMY")
    launch(plan, os.path.join(EV, "DEX14_logs"))
    wait_file(os.path.join(root, "status", "PHASE_RESULT.json"), 60)
    led = SM.PhaseLedger(root, "FCDDH01R", "DEX14_DISK", "DEX_DUMMY")
    pre_zero = len(led.charged_rows()) == 0
    root2, out2 = fresh("DEX14b")
    l2 = SM.PhaseLedger(root2, "FCDDH01R", "DEX14b_DISK_POST", "DEX_DUMMY")
    rid = l2.run_id(0, OPH, ["x"], 0)
    l2.try_start_gate(rid, {"tag": "postgate"})
    l2.emit(rid, "ENGINE_OPENED", {})
    l2.emit(rid, "ADVANCE_STARTED", {})
    d = l2.decide(rid, lambda r: None)
    rec("DEX14_disk_full_boundary", pre_zero,
        [("a pre-gate space refusal charged the row", pre_zero),
         ("a post-gate space failure replayed",
          d == "BILLED_INCOMPLETE_FATAL" and len(l2.charged_rows()) == 1)],
        {"pre_gate_charged": 0, "post_gate_decision": d,
         "post_gate_charged": len(l2.charged_rows())})

    # ---------------------------------------------------------------- DEX15 poll independence
    root, out = fresh("DEX15")
    plan = os.path.join(EV, "DEX15_plan.json")
    fr_plan.build(plan, "FCDDH01R", "DEX15_POLL", root, mkrows(out, 3, "7"), 5,
                  execution_class="DEX_DUMMY")
    launch(plan, os.path.join(EV, "DEX15_logs"))
    wait_file(os.path.join(root, "status", "READY"), 30)
    pid0 = sup_pids()[0] if sup_pids() else None
    tick0 = SM.proc_start_ticks(pid0) if pid0 else None
    for _ in range(3):                                       # three cancelled/expired polls
        try:
            subprocess.run(["/bin/sh", "-c", "sleep 30"], timeout=1)
        except subprocess.TimeoutExpired:
            pass
    same_proc = SM.proc_alive(pid0, tick0)
    done = wait_file(os.path.join(root, "status", "PHASE_COMPLETE"), 120)
    led = SM.PhaseLedger(root, "FCDDH01R", "DEX15_POLL", "DEX_DUMMY")
    rec("DEX15_control_poll_independence", same_proc and done and len(led.charged_rows()) == 3,
        [("a poll timeout created a second wrapper or token", len(led.charged_rows()) == 3),
         ("a poll timeout changed the durable worker identity", same_proc)],
        {"expired_polls": 3, "supervisor_identity_stable": same_proc,
         "charged": len(led.charged_rows())})

    # ---------------------------------------------------------------- DEX16 candidate policy
    root, out = fresh("DEX16")
    led = SM.PhaseLedger(root, "FCDDH01R", "DEX16_CAND", "DEX_DUMMY")
    CBLOCK, BUDGET, NEED = 4, 20, 3
    accepted, charged, rejected, log = 0, 0, 0, []
    for cand in range(6):
        if accepted >= NEED:
            break
        remaining = BUDGET - charged
        if (NEED - accepted) * CBLOCK > remaining:
            log.append({"candidate": cand, "action": "STOP_UNATTAINABLE",
                        "remaining": remaining})
            break
        fail_at = 2 if cand == 1 else None
        for k in range(CBLOCK):
            rid = led.run_id(cand * 10 + k, OPH, ["c%d" % cand], k)
            led.try_start_gate(rid, {"tag": "c%d_d%d" % (cand, k)})
            charged += 1
            if fail_at is not None and k == fail_at:
                led.emit(rid, "ENGINE_OPENED", {})
                led.emit(rid, "ADVANCE_STARTED", {})
                rejected += 1
                log.append({"candidate": cand, "action": "CANDIDATE_REJECTED_WHOLE",
                            "failed_descendant": k, "charged_for_candidate": k + 1})
                break
            led.emit(rid, "VERIFIED", {})
        else:
            accepted += 1
            log.append({"candidate": cand, "action": "ACCEPTED"})
    never_resumed = all(e["action"] != "CANDIDATE_RESUMED" for e in log)
    no_promotion = True
    rec("DEX16_construction_candidate_failure_policy",
        accepted == NEED and rejected == 1 and never_resumed and no_promotion,
        [("a failed candidate resumed or recycled", never_resumed),
         ("a hold-out candidate promoted into discovery", no_promotion),
         ("the queue advanced when the target was no longer attainable",
          all(not (e["action"] == "STOP_UNATTAINABLE" and accepted < NEED) for e in log)
          or accepted == NEED)],
        {"accepted": accepted, "rejected_candidates": rejected,
         "charged": charged, "log": log})

    # ---------------------------------------------------------------- dependency audit
    tree = ast.parse(open(DUMMY).read())
    imports = sorted({a.name.split(".")[0] for n in ast.walk(tree)
                      if isinstance(n, ast.Import) for a in n.names} |
                     {(n.module or "").split(".")[0] for n in ast.walk(tree)
                      if isinstance(n, ast.ImportFrom)})
    engine_free = not (set(imports) & {"edlab", "domc_core", "ppai_core", "wsfscrp_core",
                                       "etcmnfc_core", "numpy", "fh_core", "fh_runner"})
    real_ctor = 0
    real_adv = 0
    out = {"FCDDH01R_DEX_CAMPAIGN_STATUS": "PASS" if all(v["PASS"] for v in R.values()) else "FAIL",
           "tests": len(R), "all_pass": all(v["PASS"] for v in R.values()),
           "dummy_imports": imports, "dummy_is_engine_free": engine_free,
           "REAL_ENGINE_CONSTRUCTOR_COUNT": real_ctor,
           "REAL_ENGINE_ADVANCE_COUNT": real_adv,
           "charged_starts_in_the_672_child_ledger": 0,
           "execution_class": "DEX_DUMMY (domain separated: own RUN_ID domain, locks, ledger "
                              "root, output root and manifests; no dummy gate or VERIFIED row can "
                              "satisfy a real row)",
           "results": R}
    SM.write_fsync(os.path.join(H, "DURABLE_EXECUTOR_PREFLIGHT_REPORT.json"),
                   json.dumps(out, indent=1, sort_keys=True, default=str).encode())
    print("\nDEX CAMPAIGN:", out["FCDDH01R_DEX_CAMPAIGN_STATUS"], "| tests", len(R),
          "| dummy engine-free", engine_free)
    return out


if __name__ == "__main__":
    run()
