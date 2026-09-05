"""OBTC02 protocol. Scientific content identical to OBTC01; the additions are technical."""
from __future__ import annotations

import json
import sys
import time

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/OBTC02/code")

import lawspec_v2 as V2          # noqa: E402
import observe as OBS            # noqa: E402

import engine_obtc as EN         # noqa: E402
import gate_obtc02 as GT         # noqa: E402
import guard_obtc as GD          # noqa: E402
import metrics_obtc as M         # noqa: E402
import nulls_obtc as NU          # noqa: E402
import source_operator as OP     # noqa: E402

OUT, RAW = "/home/claude/OBTC02/out", "/home/claude/OBTC02/raw"
SPEC = GT.load()
PT, W = SPEC["point"], SPEC["window"]
CORE_R = float(SPEC["analytic"]["core_radius_cells"])
F = list(OBS.Recorder.FIELDS)
REQUIRED_RAW = ("N_X", "N_Y", "free_at_org", "O_total", "accepted_births_X", "deaths_X")


def spec_for(L=None, immobile_organiser=False):
    d = {k: PT[k] for k in ("CAP", "S0", "phi", "omega", "muX", "muY", "kX", "kY")}
    d["L"] = int(L or PT["L"])
    d["p_hop_X"] = PT["p_hop"]
    d["p_hop_Y"] = 0.0 if immobile_organiser else PT["p_hop"]
    return V2.spec_with(**d)


def n2_envelope(L, nx_grid, draws, seed, sp):
    op = OP.Op(sp)
    q = SPEC["gate"]["MODEL_PREDICTION_COMPATIBILITY"]["quantiles"]
    return {int(nx): {k: [float(np.nanquantile(v, q[0])), float(np.nanquantile(v, q[1]))]
                      for k, v in NU.n2_distribution(draws, seed + int(nx), L, int(nx), op.qX,
                                                     op.qY, op.mu, CORE_R).items()}
            for nx in nx_grid}


def envelope_at(env, N_X):
    keys = sorted(int(k) for k in env)
    k = min(keys, key=lambda z: abs(z - N_X))
    return {s: tuple(v) for s, v in (env[str(k)] if str(k) in env else env[k]).items()}


def source_off_response(series, off_at, tau_analytic):
    """N_X(t) after the intervention, fitted to nothing: the e-folding is read off the data by
    the time at which N_X falls to 1/e of its pre-removal level."""
    NX = series[:, F.index("N_X")]
    if off_at is None or off_at >= len(NX):
        return {}
    base = float(NX[max(off_at - 200, 0):off_at].mean())
    if base <= 0:
        return {"pre_removal_level": base}
    after = NX[off_at:]
    thr = base / np.e
    idx = np.nonzero(after <= thr)[0]
    e_fold = float(idx[0]) if len(idx) else None
    n5 = int(min(len(after) - 1, round(5 * tau_analytic)))
    return {"pre_removal_level": base, "e_folding_steps": e_fold,
            "residual_after_5_e_foldings": float(after[n5] / base) if base > 0 else None,
            "steps_available_after_removal": int(len(after)),
            "final_N_X": float(after[-1])}


def run_arm(cls, tag, cond, seed, envelope, analytic):
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
    frames, ids_at, stream_seen = [], {}, []
    H = int(W["HORIZON"])
    cap = sp.CAP

    def per_step(ww):
        r = rec.rows[-1]
        online.step(r[F.index("N_X")], r[F.index("free_at_org")], r[F.index("O_total")],
                    float(r[F.index("O_total")]) / (cap * L * L),
                    r[F.index("accepted_births_X")], r[F.index("deaths_X")])
        if ww.step % W["SAMPLE_EVERY"]:
            return
        fr, _ = M.frame(ww.n["X"], ww.n["Y"], CORE_R)
        fr["step"] = int(ww.step)
        fr["r80_organiser"] = (M.radii(ww.n["X"], fr["organiser_y"], fr["organiser_x"])[0.8]
                               if (fr["organiser_y"] >= 0 and fr["N_X"] > 0) else float("nan"))
        # FRAME CONTRACT: the frame is fully built here, handed to the stream exactly once, and
        # only then appended to the table. Same object, same identifier, one call.
        frames.append(fr)
        online.frame(fr)
        if fr["step"] > W["BURN_IN"]:
            stream_seen.append(fr)
        ids_at[int(ww.step)] = ww.tracker.id.copy()

    t0 = time.time()
    with GD.start(cls, tag, H):
        used = GD.advance(w, H, per_step=per_step)
    wall = time.time() - t0
    arr = rec.array()
    online.finish_payload(stream_seen)

    burn = W["BURN_IN"]
    tbl = [f for f in frames if f["step"] > burn]
    table_rec = {"steps": [int(f["step"]) for f in tbl],
                 "index_sha256": GT.frame_index_sha256([f["step"] for f in tbl]),
                 "payload_sha256": GT.frame_payload_sha256(tbl)}
    stream_rec = online.transport()

    tr = w.tracker
    ids_burn = set(ids_at.get(min(k for k in ids_at if k >= burn), np.zeros(0)).tolist())
    ids_end = set(ids_at.get(max(ids_at), np.zeros(0)).tolist())
    born = {int(i) for i, b in zip(tr.id, tr.birth_step) if b > burn}
    born |= {int(d[0]) for d in tr.dead if d[1] > burn}
    NXw = arr[burn:, F.index("N_X")]
    molecular = {
        "n_ids_created": int(tr.next_id), "n_alive_at_end": int(len(tr.y)),
        "n_dead_recorded": int(len(tr.dead)),
        "tracker_consistent_with_counts": bool(tr.consistent_with(w.n["X"])),
        "replacements": float(arr[burn:, F.index("deaths_X")].sum() / max(NXw.mean(), 1e-9)),
        "initial_still_present": len(ids_burn & ids_end) / max(len(ids_burn), 1),
        "final_born_in_window": len(ids_end & born) / max(len(ids_end), 1),
        "mean_lifetime_steps": float(np.mean([d[4] - d[1] for d in tr.dead]))
        if tr.dead else float("nan")}
    cen = [(f["centre_y"], f["centre_x"]) for f in tbl if f["centre_y"] >= 0]
    org = [(f["organiser_y"], f["organiser_x"]) for f in tbl if f["organiser_y"] >= 0]
    lag = {"best": None, "zero_lag_position_correlation": {"y": float("nan"), "x": float("nan")}}
    if len(cen) > 20 and len(org) == len(cen):
        lag = M.lagged_correlation(cen, org, L, 1200, W["SAMPLE_EVERY"])
    molecular["corr_y"] = lag["zero_lag_position_correlation"]["y"]
    molecular["corr_x"] = lag["zero_lag_position_correlation"]["x"]
    n3 = NU.n3_decorrelated(np.random.default_rng(seed + 4242), cen, L) if len(cen) > 5 \
        else np.zeros(0)
    n3m = float(np.median(n3)) if n3.size else float("nan")

    env = envelope_at(envelope, float(np.nanmedian([f["N_X"] for f in tbl])) if tbl else 0.0)
    agg_on = online.aggregates(molecular, n3m)
    agg_ph = GT.posthoc_aggregates(SPEC, L, arr, F, frames, molecular, n3m)
    cmp_ = GT.compare(agg_on, agg_ph)

    tech = GT.technical_validity(
        SPEC, stream_rec, table_rec,
        required_raw_present=all(k in F for k in REQUIRED_RAW),
        rng_state_present=bool(rng0),
        run_complete=(used == H and int(w.step) == H),
        start_counter_ok=(GD.LEDGER["log"][-1]["steps_used"] == H),
        gates_agree=cmp_["AGREE"])

    c_on = GT.evaluate(SPEC, agg_on, env)
    c_ph = GT.evaluate(SPEC, agg_ph, env)
    verdict_agree = (c_on["PER_ARM_PASS"] == c_ph["PER_ARM_PASS"]
                     and GT.classify(c_on) == GT.classify(c_ph))

    np.savez_compressed("%s/%s.npz" % (RAW, tag.replace("/", "__")), series=arr,
                        fields=np.array(F), nX_final=w.n["X"], nY_final=w.n["Y"],
                        nSX_final=w.n["SX"], nSY_final=w.n["SY"], nWX_final=w.n["WX"],
                        nWY_final=w.n["WY"],
                        molecule_births=np.array([[i, b, y, x] for i, b, y, x in
                                                  zip(tr.id, tr.birth_step, tr.birth_y,
                                                      tr.birth_x)], dtype=np.int64)
                        if len(tr.id) else np.zeros((0, 4), np.int64),
                        molecule_deaths=np.array([list(d[:5]) for d in tr.dead], dtype=np.int64)
                        if tr.dead else np.zeros((0, 5), np.int64),
                        frames=np.array([json.dumps(f) for f in frames]),
                        birth_offsets=np.array(w.birth_offsets, dtype=np.int64)
                        if w.birth_offsets else np.zeros((0, 4), np.int64))

    o = arr[:, F.index("O_total")]
    return {"class": cls, "tag": tag, "condition": cond["key"], "seed": seed, "L": L,
            "wall_seconds": wall, "steps": int(w.step),
            "raw_npz": tag.replace("/", "__") + ".npz",
            "rng_state_initial": rng0, "state_hash_final": w.state_hash(),
            "hops_offered": dict(w.hops_offered), "hops_blocked": dict(w.hops_blocked),
            "blocked_fraction": {k: w.hops_blocked[k] / max(w.hops_offered[k], 1)
                                 for k in w.hops_offered},
            "organiser_removed_at": w.organiser_removed_at,
            "source_off": source_off_response(arr, w.organiser_removed_at,
                                              analytic["source_off"]["e_folding_steps"]),
            "occupancy": {"O_first": float(o[0]), "O_last": float(o[-1]),
                          "drift": float(abs(o[-1] - o[0]) / max(o[0], 1)),
                          "exactly_constant": bool(o.std() == 0.0)},
            "N_X": {"max": float(arr[:, F.index("N_X")].max()),
                    "final": float(arr[-1, F.index("N_X")]),
                    "window_mean": float(arr[burn:, F.index("N_X")].mean())},
            "molecular": molecular, "lag": lag["best"], "n3_median_displacement": n3m,
            "envelope_used": {k: list(v) for k, v in env.items()},
            "technical": tech, "RUN_TECHNICALLY_VALID": tech["RUN_TECHNICALLY_VALID"],
            "aggregates": agg_ph, "gate_online": c_on, "gate_posthoc": c_ph,
            "GATES_AGREE": bool(cmp_["AGREE"] and verdict_agree),
            "gate_differences": cmp_["differences"],
            "classification": GT.classify(c_ph) if tech["RUN_TECHNICALLY_VALID"]
            else "TECHNICALLY_INVALID",
            "PASS": bool(tech["RUN_TECHNICALLY_VALID"] and c_ph["PER_ARM_PASS"]),
            "frames": frames}
