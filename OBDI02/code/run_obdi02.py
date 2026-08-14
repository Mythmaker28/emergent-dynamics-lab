"""OBDI02 §16 — execute the frozen plan.

Every frozen arm is run. There is no early scientific stopping and no interim analysis: the
driver launches workers, collects their records, and evaluates the frozen gate exactly once,
after the last arm. Results are masked until then — the driver never inspects a summary while
arms remain.

Two workers are used because the machine has two CPUs and a measurement showed the speed-up is
essentially linear. The arm order is the frozen order; only the dispatch is concurrent.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

sys.path.insert(0, "/home/claude/OBDI02/code")

import gate_obdi02 as GT           # noqa: E402

OUT = "/home/claude/OBDI02/out"
ARMDIR = "/home/claude/OBDI02/arms"
WORKERS = 2


def main():
    spec = GT.load()
    frz = json.load(open(f"{OUT}/_freeze.json"))
    assert frz["spec_sha256"] == GT.spec_sha256(), "the frozen spec changed since the freeze"
    assert frz["SCIENTIFIC_RUNS_USED_AT_FREEZE"] == 0
    assert spec["stopping"]["EARLY_SCIENTIFIC_STOPPING"] == "FORBIDDEN"
    os.makedirs(ARMDIR, exist_ok=True)

    sizes = [int(x) for x in spec["domain"]["SIZES"]]
    seeds = {int(k): list(v) for k, v in spec["domain"]["SEEDS"].items()}
    plan = [(L, s) for L in sizes for s in seeds[L]]
    assert len(plan) == int(spec["domain"]["TOTAL_ARMS"]) <= int(
        spec["stopping"]["hard_cap_total_arms"])

    t0 = time.time()
    todo = list(plan)
    running = []
    done = 0
    log = open(f"{OUT}/_run.log", "a", buffering=1)
    while todo or running:
        while todo and len(running) < WORKERS:
            L, s = todo.pop(0)
            p = subprocess.Popen([sys.executable, "/home/claude/OBDI02/code/worker_obdi02.py",
                                  str(L), str(s), ARMDIR],
                                 stdout=log, stderr=subprocess.STDOUT)
            running.append((p, L, s))
        time.sleep(1.0)
        for e in list(running):
            if e[0].poll() is not None:
                running.remove(e)
                done += 1
                if e[0].returncode != 0:
                    log.write("WORKER FAILED L=%d seed=%d rc=%d\n"
                              % (e[1], e[2], e[0].returncode))
                if done % 6 == 0 or not (todo or running):
                    el = time.time() - t0
                    log.write("PROGRESS %d/%d  elapsed %.0f s  eta %.0f s\n"
                              % (done, len(plan), el, el / max(done, 1)
                                 * (len(plan) - done)))
    wall = time.time() - t0

    # ---------------------------------------------------------------- collect, then evaluate
    arms = []
    for L, s in plan:
        p = os.path.join(ARMDIR, "arm_%d_%d.json" % (L, s))
        if not os.path.exists(p):
            raise RuntimeError("missing arm record %s — the plan did not complete" % p)
        arms.append(json.load(open(p)))

    tech_bad = [a["tag"] for a in arms if not a["RUN_TECHNICALLY_VALID"]]
    disagree = [a["tag"] for a in arms if not a["GATES_AGREE"]]

    by_L = {}
    for L in sizes:
        aa = [a for a in arms if a["L"] == L]
        by_L[L] = {
            "summary_CY": [a["summary"]["organiser_to_core"] for a in aa],
            "summary_Rg": [a["summary"]["Rg"] for a in aa],
            "summary_r80": [a["summary"]["r80"] for a in aa],
            "density": [a["summary"]["density"] for a in aa],
            "tags": [a["tag"] for a in aa],
            "extinct": [a["tag"] for a in aa if a["EXTINCT"]],
        }

    res = {
        "OBDI02_METHODS_CORE_HASH": frz["OBDI02_METHODS_CORE_HASH"],
        "spec_sha256": frz["spec_sha256"],
        "planned_arms": len(plan), "arms_run": len(arms), "wall_seconds": wall,
        "workers": WORKERS,
        "all_planned_arms_run": len(arms) == len(plan),
        "technically_valid": len(arms) - len(tech_bad),
        "technically_invalid": tech_bad,
        "gates_agree": len(arms) - len(disagree), "gates_disagree": disagree,
        "extinctions_by_L": {str(L): len(by_L[L]["extinct"]) for L in sizes},
        "extinct_tags": {str(L): by_L[L]["extinct"] for L in sizes},
        "by_L_raw": {str(L): by_L[L] for L in sizes},
    }
    if tech_bad or disagree:
        res["HALTED"] = ("TECHNICAL: %s" % (tech_bad or disagree))
        res["PRIMARY"] = {"NOT_EVALUATED": "a technical defect stops the mission"}
    else:
        res["HALTED"] = None
        res["PRIMARY"] = GT.evaluate_primary(spec, by_L)
        res["POPULATION_SUPPORT"] = GT.evaluate_support(spec, by_L)
        res["EXTINCTION_SENSITIVITY"] = GT.extinction_sensitivity(spec, by_L)
        res["SECONDARY"] = GT.evaluate_secondary(spec, by_L, arms)

    # consolidated start register
    reg = []
    for a in arms:
        e = a["ledger"]["log"][-1] if a["ledger"]["log"] else {}
        reg.append({"tag": a["tag"], "L": a["L"], "seed": a["seed"], "class": e.get("class"),
                    "planned_steps": e.get("planned_steps"), "steps_used": e.get("steps_used"),
                    "valid": e.get("valid"), "scientific": e.get("scientific"),
                    "wall_seconds": a["wall_seconds"], "state_hash_final": a["state_hash_final"]})
    res["CONSOLIDATED_START_REGISTER"] = {
        "starts": reg, "n_starts": len(reg),
        "by_class": {"confirmation": sum(1 for r in reg if r["class"] == "confirmation")},
        "invalid": sum(1 for r in reg if not r["valid"]),
        "SCIENTIFIC_RUNS_USED": sum(1 for r in reg if r["scientific"]),
        "note": ("each arm ran in its own process, so each opened exactly one start in its own "
                 "ledger; the entries are consolidated here into a single register")}
    res["SCIENTIFIC_RUNS_USED"] = res["CONSOLIDATED_START_REGISTER"]["SCIENTIFIC_RUNS_USED"]

    json.dump(res, open(f"{OUT}/_results.json", "w"), indent=1, default=str)
    slim = [{k: a[k] for k in a if k not in ("r80_organiser_frames",)} for a in arms]
    json.dump(slim, open(f"{OUT}/_arms.json", "w"), indent=1, default=str)
    json.dump({a["tag"]: a["r80_organiser_frames"] for a in arms},
              open(f"{OUT}/_r80_org_frames.json", "w"), default=str)

    print("\narms %d/%d  wall %.0f s  technically valid %d  evaluators agree %d"
          % (res["arms_run"], res["planned_arms"], wall, res["technically_valid"],
             res["gates_agree"]))
    print("extinctions by L:", res["extinctions_by_L"])
    if res["HALTED"] is None:
        P = res["PRIMARY"]
        print("PRIMARY  beta=%+.5f  se=%.5f  interval [%+.5f, %+.5f]  achieved bound %.5f  "
              "margin %.3f  -> %s"
              % (P["beta"], P["se"], P["interval"][0], P["interval"][1],
                 P["achieved_equivalence_bound"], P["equivalence_margin"], P["PASS"]))
        print("STRINGENT 0.042 reference -> %s (pre-declared underpowered)"
              % P["STRINGENT_REFERENCE"]["PASS"])
        print("SUPPORT  %s -> %s" % ({k: v["notation"] for k, v in
                                      res["POPULATION_SUPPORT"]["per_L"].items()},
                                     res["POPULATION_SUPPORT"]["PASS"]))
        print("SENSITIVITY robust:", res["EXTINCTION_SENSITIVITY"]["ROBUST"])
        print("SECONDARY material contradiction:",
              res["SECONDARY"]["ANY_MATERIAL_CONTRADICTION"])
    print("SCIENTIFIC_RUNS_USED = %d" % res["SCIENTIFIC_RUNS_USED"])


if __name__ == "__main__":
    main()
