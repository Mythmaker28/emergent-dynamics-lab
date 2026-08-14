"""OBTC01 protocol. Every threshold is read from the yaml; none is written here."""
from __future__ import annotations

import json
import sys
import time

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/OBTC01/code")

import lawspec_v2 as V2          # noqa: E402
import observe as OBS            # noqa: E402

import engine_obtc as EN         # noqa: E402
import gate_obtc as GT           # noqa: E402
import guard_obtc as GD          # noqa: E402
import metrics_obtc as M         # noqa: E402
import nulls_obtc as NU          # noqa: E402
import source_operator as OP     # noqa: E402

OUT, RAW = "/home/claude/OBTC01/out", "/home/claude/OBTC01/raw"
SPEC = GT.load()
PT = SPEC["point"]
W = SPEC["window"]
CORE_R = float(SPEC["analytic"]["core_radius_cells"])
F = list(OBS.Recorder.FIELDS)


def spec_for(L=None, immobile_organiser=False):
    d = {k: PT[k] for k in ("CAP", "S0", "phi", "omega", "muX", "muY", "kX", "kY")}
    d["L"] = int(L or PT["L"])
    d["p_hop_X"] = PT["p_hop"]
    d["p_hop_Y"] = 0.0 if immobile_organiser else PT["p_hop"]
    return V2.spec_with(**d)


# ------------------------------------------------------------------ the N2 envelope
def n2_envelope(L, nx_grid, draws, seed, sp):
    op = OP.Op(sp)
    q = SPEC["gate"]["MODEL_PREDICTION_COMPATIBILITY"]["quantiles"]
    out = {}
    for nx in nx_grid:
        d = NU.n2_distribution(draws, seed + int(nx), L, int(nx), op.qX, op.qY, op.mu, CORE_R)
        out[int(nx)] = {k: [float(np.nanquantile(v, q[0])), float(np.nanquantile(v, q[1]))]
                        for k, v in d.items()}
    return out


def envelope_at(env, N_X):
    keys = sorted(int(k) for k in env)
    k = min(keys, key=lambda z: abs(z - N_X))
    return {s: tuple(v) for s, v in env[str(k) if str(k) in env else k].items()}


# ------------------------------------------------------------------ one arm
def run_arm(cls, tag, cond, seed, envelope, horizon=None):
    L = int(cond.get("L", PT["L"]))
    sp = spec_for(L, immobile_organiser=(cond["key"] == "S"))
    rec = OBS.Recorder()
    off = W["SOURCE_OFF_AT"] if cond["key"] == "R" else None
    w = EN.fresh_world(seed, sp, lawspec=V2.LAWSPEC_V2_EXCHANGE, rng_mode="split_feed_stream",
                       exchangeable=V2.EXCHANGEABLE_DEFAULT, insert_mode="reservoir", rec=rec,
                       track=True, organiser_off_at=off)
    if cond["key"] != "N":
        EN.seed_one_organiser(w, PT["X_SEED"])
    rng0 = json.loads(json.dumps(w.rng.bit_generator.state, default=str))
    online = GT.OnlineGate(SPEC, L, W["BURN_IN"])
    frames, labels, ids_at = [], [], {}
    H = int(horizon or W["HORIZON"])
    cap = sp.CAP

    def per_step(ww):
        r = rec.rows[-1]
        occ = float(r[F.index("O_total")]) / (cap * L * L)
        online.step(r[F.index("N_X")], r[F.index("free_at_org")], r[F.index("O_total")], occ,
                    r[F.index("accepted_births_X")], r[F.index("deaths_X")])
        if ww.step % W["SAMPLE_EVERY"]:
            return
        fr, lab = M.frame(ww.n["X"], ww.n["Y"], CORE_R)
        fr["step"] = int(ww.step)
        if fr["organiser_y"] >= 0 and fr["N_X"] > 0:
            fr["r80_organiser"] = M.radii(ww.n["X"], fr["organiser_y"],
                                          fr["organiser_x"])[0.8]
        else:
            fr["r80_organiser"] = float("nan")
        frames.append(fr)
        online.frame(fr)                 # BUG D-2 of this mission: this call was missing, so
        labels.append(lab.astype(np.int16))   # the streaming gate saw zero spatial frames
        ids_at[int(ww.step)] = ww.tracker.id.copy()

    t0 = time.time()
    with GD.start(cls, tag, H):
        GD.advance(w, H, per_step=per_step)
    wall = time.time() - t0
    arr = rec.array()

    # ---------------- molecular ledger
    tr = w.tracker
    burn = W["BURN_IN"]
    ids_burn = set(ids_at.get(min(k for k in ids_at if k >= burn), np.zeros(0)).tolist())
    ids_end = set(ids_at.get(max(ids_at), np.zeros(0)).tolist())
    born_in_window = set()
    for i, b in zip(tr.id, tr.birth_step):
        if b > burn:
            born_in_window.add(int(i))
    for d in tr.dead:
        if d[1] > burn:
            born_in_window.add(int(d[0]))
    NXw = arr[burn:, F.index("N_X")]
    deaths_w = arr[burn:, F.index("deaths_X")].sum()
    molecular = {
        "n_ids_created": int(tr.next_id),
        "n_alive_at_end": int(len(tr.y)),
        "n_dead_recorded": int(len(tr.dead)),
        "tracker_consistent_with_counts": bool(tr.consistent_with(w.n["X"])),
        "replacements": float(deaths_w / max(NXw.mean(), 1e-9)),
        "initial_still_present": (len(ids_burn & ids_end) / max(len(ids_burn), 1)),
        "final_born_in_window": (len(ids_end & born_in_window) / max(len(ids_end), 1)),
        "median_lifetime_steps": float(np.median([d[4] - d[1] for d in tr.dead]))
        if tr.dead else float("nan"),
        "mean_lifetime_steps": float(np.mean([d[4] - d[1] for d in tr.dead]))
        if tr.dead else float("nan"),
    }
    # ---------------- core / organiser tracks
    win = [f for f in frames if f["step"] > burn]
    cen = [(f["centre_y"], f["centre_x"]) for f in win if f["centre_y"] >= 0]
    org = [(f["organiser_y"], f["organiser_x"]) for f in win if f["organiser_y"] >= 0]
    lagres = {"best": None, "zero_lag_position_correlation": {"y": float("nan"),
                                                              "x": float("nan")}}
    if len(cen) > 20 and len(org) == len(cen):
        lagres = M.lagged_correlation(cen, org, L, 1200, W["SAMPLE_EVERY"])
    molecular["corr_y"] = lagres["zero_lag_position_correlation"]["y"]
    molecular["corr_x"] = lagres["zero_lag_position_correlation"]["x"]
    molecular["lag"] = lagres["best"]
    rng = np.random.default_rng(seed + 4242)
    n3 = NU.n3_decorrelated(rng, cen, L) if len(cen) > 5 else np.zeros(0)
    n3_median = float(np.median(n3)) if n3.size else float("nan")

    env = envelope_at(envelope, float(np.nanmedian([f["N_X"] for f in win])) if win else 0.0)
    agg_on = online.aggregates(molecular, n3_median, None)
    agg_ph = GT.posthoc_aggregates(SPEC, L, arr, F, frames, molecular, n3_median)
    cmp_ = GT.compare(agg_on, agg_ph)
    c_on = GT.evaluate(SPEC, agg_on, env)
    c_ph = GT.evaluate(SPEC, agg_ph, env)
    agree = cmp_["AGREE"] and c_on["PER_ARM_PASS"] == c_ph["PER_ARM_PASS"] and \
        GT.classify(c_on) == GT.classify(c_ph)

    np.savez_compressed("%s/%s.npz" % (RAW, tag.replace("/", "__")), series=arr,
                        fields=np.array(F), nX_final=w.n["X"], nY_final=w.n["Y"],
                        nSX_final=w.n["SX"], nSY_final=w.n["SY"], nWX_final=w.n["WX"],
                        nWY_final=w.n["WY"],
                        molecule_births=np.array([[i, b, y, x] for i, b, y, x in
                                                  zip(tr.id, tr.birth_step, tr.birth_y,
                                                      tr.birth_x)], dtype=np.int64)
                        if len(tr.id) else np.zeros((0, 4), np.int64),
                        molecule_deaths=np.array([[d[0], d[1], d[2], d[3], d[4]]
                                                  for d in tr.dead], dtype=np.int64)
                        if tr.dead else np.zeros((0, 5), np.int64),
                        frames=np.array([json.dumps(f) for f in frames]),
                        birth_offsets=np.array(w.birth_offsets, dtype=np.int64)
                        if w.birth_offsets else np.zeros((0, 4), np.int64))

    o = arr[:, F.index("O_total")]
    return {"class": cls, "tag": tag, "condition": cond["key"], "seed": seed, "L": L,
            "spec": sp.as_dict(), "wall_seconds": wall, "steps": int(w.step),
            "raw_npz": tag.replace("/", "__") + ".npz",
            "rng_state_initial": rng0,
            "rng_state_final": json.loads(json.dumps(w.rng.bit_generator.state, default=str)),
            "state_hash_final": w.state_hash(),
            "hops_offered": dict(w.hops_offered), "hops_blocked": dict(w.hops_blocked),
            "blocked_fraction": {k: (w.hops_blocked[k] / max(w.hops_offered[k], 1))
                                 for k in w.hops_offered},
            "organiser_removed_at": w.organiser_removed_at,
            "occupancy": {"O_first": float(o[0]), "O_last": float(o[-1]),
                          "drift": float(abs(o[-1] - o[0]) / max(o[0], 1)),
                          "exactly_constant": bool(o.std() == 0.0)},
            "N_X": {"max": float(arr[:, F.index("N_X")].max()),
                    "final": float(arr[-1, F.index("N_X")]),
                    "window_mean": float(arr[W["BURN_IN"]:, F.index("N_X")].mean())},
            "molecular": molecular, "lag": lagres["best"], "n3_median_displacement": n3_median,
            "envelope_used": {k: list(v) for k, v in env.items()},
            "aggregates": agg_ph, "gate_online": c_on, "gate_posthoc": c_ph,
            "GATES_AGREE": bool(agree), "gate_differences": cmp_["differences"],
            "classification": GT.classify(c_ph), "PASS": bool(c_ph["PER_ARM_PASS"]),
            "frames": frames}
