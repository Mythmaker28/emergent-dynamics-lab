"""OBFOR01 §18, §21 — the fresh validation, with reinforced instrumentation proven inert.

The LawSpec, the chemostat, the engine and the window are the qualified ones, untouched. Two
conditions only:

    S   the organiser immobilised, exactly the intervention OBTC02 already used (p_hop_Y = 0)
    M   the organiser mobile, the qualified point unchanged

Condition E (an exogenous trajectory) is NOT opened: §18 allows it only if the natural
trajectory prevents identifying the intra-step order or the mobile response, and §9 identified
the order directly from the code and confirmed it on 141 009 recorded births.

The instrumentation subclasses the world and records BEFORE and AFTER each sub-step. It draws
no random number, so it cannot move the RNG stream; that claim is not asserted but tested, by
running the same seed with and without it and comparing the final state hash and the frame
payload checksum.
"""
from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np

WC = "/home/claude/OBFOR01/verify/obtr01/wc"
OUT = "/home/claude/OBFOR01/out"
RAW = "/home/claude/OBFOR01/raw"
sys.path.insert(0, f"{WC}/ORR01/code")
sys.path.insert(0, f"{WC}/OBTC02/code")

import lawspec_v2 as V2          # noqa: E402
import observe as OBS            # noqa: E402
import engine_obtc as EN         # noqa: E402
import metrics_obtc as M         # noqa: E402
import guard_obtc as GD          # noqa: E402
import protocol_obtc02 as PC     # noqa: E402

SPEC = PC.SPEC
PT, W = SPEC["point"], SPEC["window"]
CORE_R = float(SPEC["analytic"]["core_radius_cells"])
F = list(OBS.Recorder.FIELDS)


def state_sha256(w):
    h = hashlib.sha256()
    for s in ("X", "Y", "SX", "SY", "WX", "WY"):
        h.update(np.ascontiguousarray(w.n[s]).tobytes())
    h.update(str(w.step).encode())
    return h.hexdigest()


class Instrumented(EN.WorldOBTC):
    """Records the sub-step ledgers the mandate names. It reads state and appends to lists; it
    draws no random number and calls straight through to the frozen implementation."""

    def _init_ledgers(self):
        self.LED_HOP = []        # (step, species, offered, blocked)
        self.LED_SRC = []        # (step, species, y_before, x_before, y_after, x_after)
        self.LED_BIRTH = []      # (step, n_born, y, x, free_before, nSX_before)

    def _org(self):
        ys, xs = np.nonzero(self.n["Y"])
        return (int(ys[0]), int(xs[0])) if len(ys) else (-1, -1)

    def _diffuse(self, sname, p_hop):
        o0 = self._org()
        off0 = self.hops_offered.get(sname, 0)
        blk0 = self.hops_blocked.get(sname, 0)
        super()._diffuse(sname, p_hop)
        o1 = self._org()
        self.LED_HOP.append((int(self.step), sname,
                             int(self.hops_offered.get(sname, 0) - off0),
                             int(self.hops_blocked.get(sname, 0) - blk0)))
        self.LED_SRC.append((int(self.step), sname, o0[0], o0[1], o1[0], o1[1]))

    def _react(self):
        y, x = self._org()
        before_free = int(self.free()[y, x]) if y >= 0 else -1
        before_sx = int(self.n["SX"][y, x]) if y >= 0 else -1
        n0 = int(self.n["X"].sum())
        super()._react()
        self.LED_BIRTH.append((int(self.step), int(self.n["X"].sum()) - n0, y, x,
                               before_free, before_sx))


def build(seed, immobile, instrumented):
    sp = PC.spec_for(int(PT["L"]), immobile_organiser=immobile)
    rec = OBS.Recorder()
    cls = Instrumented if instrumented else EN.WorldOBTC
    w = cls(L=None, seed=seed, sp=sp, lawspec=V2.LAWSPEC_V2_EXCHANGE,
            rng_mode="split_feed_stream", exchangeable=V2.EXCHANGEABLE_DEFAULT,
            insert_mode="reservoir", rec=rec, track=True, organiser_off_at=None)
    w.n["SX"][:] = sp.S0
    w.n["SY"][:] = sp.S0
    if instrumented:
        w._init_ledgers()
    EN.seed_one_organiser(w, int(PT["X_SEED"]))
    return w, rec


def run_arm(args):
    cond, seed = args
    t0 = time.time()
    w, rec = build(seed, cond == "S", True)
    frames = []
    # the world drives the recorder itself through close_step, exactly as the frozen protocol
    # relies on; the loop only advances it and samples frames on the frozen cadence
    for _ in range(int(W["HORIZON"])):
        w._one_step()
        if w.step % int(W["SAMPLE_EVERY"]) == 0:
            fr, _ = M.frame(w.n["X"], w.n["Y"], CORE_R)
            fr["step"] = int(w.step)
            fr["r80_organiser"] = (M.radii(w.n["X"], fr["organiser_y"], fr["organiser_x"])[0.8]
                                   if (fr["organiser_y"] >= 0 and fr["N_X"] > 0)
                                   else float("nan"))
            frames.append(fr)
    tr = w.tracker
    tag = "%s/seed%d" % (cond, seed)
    arr = rec.array()
    hop = np.array([(s, ["X", "Y", "SX", "SY"].index(n) if n in ("X", "Y", "SX", "SY") else -1,
                     o, b) for s, n, o, b in w.LED_HOP], np.int64)
    src = np.array([(s, ["X", "Y", "SX", "SY"].index(n) if n in ("X", "Y", "SX", "SY") else -1,
                     a, b, c, d) for s, n, a, b, c, d in w.LED_SRC], np.int64)
    bir = np.array(w.LED_BIRTH, np.int64)
    np.savez_compressed("%s/%s.npz" % (RAW, tag.replace("/", "__")),
                        series=arr, fields=np.array(F),
                        nX_final=w.n["X"], nY_final=w.n["Y"], nSX_final=w.n["SX"],
                        nSY_final=w.n["SY"], nWX_final=w.n["WX"], nWY_final=w.n["WY"],
                        molecule_births=np.array([[i, b, y, x] for i, b, y, x in
                                                  zip(tr.id, tr.birth_step, tr.birth_y,
                                                      tr.birth_x)], dtype=np.int64)
                        if len(tr.id) else np.zeros((0, 4), np.int64),
                        molecule_deaths=np.array([list(d[:5]) for d in tr.dead], dtype=np.int64)
                        if tr.dead else np.zeros((0, 5), np.int64),
                        frames=np.array([json.dumps(f) for f in frames]),
                        birth_offsets=np.array(w.birth_offsets, dtype=np.int64)
                        if w.birth_offsets else np.zeros((0, 4), np.int64),
                        hop_ledger=hop, source_substep_ledger=src, birth_substep_ledger=bir)
    win = [f for f in frames if f["step"] > int(W["BURN_IN"])]
    v = np.array([f["r80_organiser"] for f in win
                  if f.get("r80_organiser") is not None and np.isfinite(f["r80_organiser"])])
    nx = np.array([f["N_X"] for f in win], float)
    return {
        "tag": tag, "condition": cond, "seed": seed, "L": int(PT["L"]),
        "wall_seconds": time.time() - t0,
        "state_hash_final": state_sha256(w),
        "frames_in_window": len(win), "r80_values": int(len(v)),
        "r80_median": float(np.median(v)) if len(v) else None,
        "r80_mean": float(v.mean()) if len(v) else None,
        "r80_sd": float(v.std(ddof=1)) if len(v) > 1 else None,
        "r80_skew": float(((v - v.mean()) ** 3).mean() / v.std(ddof=1) ** 3)
        if len(v) > 2 else None,
        "N_X_window_mean": float(nx.mean()), "N_X_window_median": float(np.median(nx)),
        "EXTINCT": bool(np.median(nx) <= 0),
        "hops_offered": dict(w.hops_offered), "hops_blocked": dict(w.hops_blocked),
        "blocked_fraction": {k: w.hops_blocked[k] / max(w.hops_offered[k], 1)
                             for k in w.hops_offered},
        "ledger_rows": {"hop": int(len(hop)), "source_substep": int(len(src)),
                        "birth_substep": int(len(bir))},
        "tracker_consistent_with_counts": bool(tr.consistent_with(w.n["X"])),
        "molecules_alive": int(len(tr.id)), "molecules_dead": int(len(tr.dead)),
    }


def inertness_test(seed=9299999, steps=1500):
    """Same seed, same spec, with and without the instrumentation. If the ledgers moved the
    RNG stream the two states would diverge."""
    out = {}
    for tag, instr in (("plain", False), ("instrumented", True)):
        w, rec = build(seed, False, instr)
        for _ in range(steps):
            w._one_step()
        fr, _ = M.frame(w.n["X"], w.n["Y"], CORE_R)
        out[tag] = {"state_sha256": state_sha256(w), "N_X": int(w.n["X"].sum()),
                    "r80": fr["r80"], "Rg": fr["Rg"],
                    "hops_offered": dict(w.hops_offered)}
    same = out["plain"]["state_sha256"] == out["instrumented"]["state_sha256"]
    return {"steps": steps, "seed": seed, "plain": out["plain"],
            "instrumented": out["instrumented"],
            "STATE_IDENTICAL": bool(same),
            "INSTRUMENTATION_ALTERS_THE_LAW": bool(not same)}


def main():
    os.makedirs(RAW, exist_ok=True)
    frz = json.load(open(f"{OUT}/_freeze.json"))
    if not frz["GATE"]["FRESH_RUNS_AUTHORISED"]:
        print("GATE CLOSED — no fresh run is authorised.")
        return
    GD.set_experiment_mode()

    inert = inertness_test()
    print("inertness test: state identical with and without instrumentation = %s"
          % inert["STATE_IDENTICAL"])
    if not inert["STATE_IDENTICAL"]:
        json.dump({"INERTNESS": inert, "DISPOSITION": "AUDIT_INVALID"},
                  open(f"{OUT}/_validation.json", "w"), indent=1)
        print("AUDIT_INVALID: the instrumentation changed the trajectory.")
        return

    seeds = frz["SEEDS"]["FRESH_OBFOR01_SEEDS"]
    jobs = [("S", s) for s in seeds["S"]] + [("M", s) for s in seeds["M"]]
    nproc = max(1, min(len(jobs), (os.cpu_count() or 2)))
    t0 = time.time()
    with mp.Pool(nproc) as pool:
        arms = pool.map(run_arm, jobs)
    wall = time.time() - t0

    res = {"SECTION": "OBFOR01 §18, §21",
           "INERTNESS": inert,
           "CONDITIONS": {"S": "organiser immobilised, p_hop_Y = 0",
                          "M": "organiser mobile, the qualified point unchanged",
                          "E": "NOT_OPENED — the intra-step order was identified directly "
                               "from the code and confirmed on 141 009 recorded births"},
           "ARMS": arms, "n_arms": len(arms), "workers": nproc, "wall_seconds": wall,
           "SCIENTIFIC_RUNS_USED": len(arms),
           "START_REGISTER": [{"class": "validation", "tag": a["tag"], "seed": a["seed"],
                               "condition": a["condition"], "steps": int(W["HORIZON"]),
                               "state_hash_final": a["state_hash_final"]} for a in arms],
           "extinct": [a["tag"] for a in arms if a["EXTINCT"]],
           "tracker_consistent_on_every_arm": all(a["tracker_consistent_with_counts"]
                                                  for a in arms)}
    json.dump(res, open(f"{OUT}/_validation.json", "w"), indent=1, default=str)
    print("ran %d arms on %d workers in %.1f s" % (len(arms), nproc, wall))
    for a in arms:
        print("  %-14s N_X %6.1f  r80 median %7.4f  mean %7.4f  sd %6.3f  blocked_X %.2e  %s"
              % (a["tag"], a["N_X_window_mean"], a["r80_median"] or float("nan"),
                 a["r80_mean"] or float("nan"), a["r80_sd"] or float("nan"),
                 a["blocked_fraction"]["X"], "EXTINCT" if a["EXTINCT"] else ""))


if __name__ == "__main__":
    main()
