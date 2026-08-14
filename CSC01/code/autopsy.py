"""CSC01 étape A — raw-only autopsy of the ORR01 arms.

One bit-exact replay per arm. From it:
  1. the 102 ORR01-cadence component reports are regenerated with the ORR01 function itself, the
     frozen post-hoc gate is recomputed from them, and every field is compared with the value
     recorded in _results.json / _results2.json. This is a stronger replay test than equality of
     the scalar series, because it also reproduces the SPATIAL observables ORR01 discarded;
  2. a dense spatial trace at TRACK_EVERY = 10 steps, with the correct toroidal geometry;
  3. component tracking by cell overlap, giving core identity continuity, satellite lifetimes,
     and the halo / fragmentation separation;
  4. the four axes A1..A4 of the pre-plan, and the three persistences, kept separate.
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/CSC01/code")

import gates as G                # noqa: E402
import observe as OBS            # noqa: E402
import protocol as P             # noqa: E402
import lawspec_v2 as V2          # noqa: E402

import guard_csc as GC           # noqa: E402
import nulls as NU               # noqa: E402
import spatial as SP             # noqa: E402
import replay as RP              # noqa: E402

OUT = "/home/claude/CSC01/out"
TRACK_EVERY = 10
NULL_DRAWS = 200
N_NULL_INSTANTS = 9

ELL_X = 2.5                      # sqrt(D_X / muX) at the frozen point, exactly
CAP = P.POINT["CAP"]
L = P.POINT["L"]
P_HOP = P.POINT["p_hop_X"]
MU_X = P.POINT["muX"]


# ------------------------------------------------------------------ the replay with two traces
def trace_arm(tag):
    name, seed, cfg = RP._cfg_for(tag)
    sp = P.spec_for(**({"phi": cfg["phi"]} if "phi" in cfg else {}))
    rec = OBS.Recorder()
    w = V2.fresh_world(seed, sp, lawspec=cfg["lawspec"], rng_mode=cfg["rng_mode"],
                       exchangeable=cfg["exchangeable"], insert_mode=cfg["insert_mode"], rec=rec)
    if cfg["organiser"]:
        V2.seed_one_organiser(w, P.X_SEED)

    orr_samples, frames, labels, xfields, snaps = [], [], [], [], {}

    def per_step(ww):
        if ww.step % P.SAMPLE_EVERY == 0:
            orr_samples.append(OBS.component_report(ww))         # the ORR01 function, unchanged
        if ww.step % TRACK_EVERY == 0:
            fr = SP.frame_report(ww.n["X"], ww.n["Y"], ELL_X, occ=ww.occ(), cap=ww.sp.CAP)
            labels.append(fr.pop("_labels").astype(np.int16))
            fr.pop("_comp")
            fr["step"] = int(ww.step)
            frames.append(fr)
            xfields.append(ww.n["X"].astype(np.int16))
        if ww.step % 1000 == 0:
            snaps[int(ww.step)] = ww.n["X"].copy()

    t0 = time.time()
    with GC.start("raw_replay", tag, P.HORIZON):
        GC.advance(w, P.HORIZON, per_step=per_step)
    return {"series": rec.array(), "final": {s: w.n[s].copy() for s in RP.SPECIES},
            "orr_samples": orr_samples, "frames": frames, "labels": labels,
            "xfields": xfields, "snaps": snaps,
            "seed": seed, "arm": name, "wall": time.time() - t0}


# ------------------------------------------------------------------ 1. replay fidelity
def replay_fidelity(tag, tr):
    ref = RP.recorded(tag)
    series_eq = bool(np.array_equal(tr["series"], ref["series"]))
    fields_eq = {s: bool(np.array_equal(tr["final"][s], ref["final"][s])) for s in RP.SPECIES}
    ph = G.posthoc_gate(tr["series"], list(OBS.Recorder.FIELDS), P.TH, tr["orr_samples"])
    return series_eq, fields_eq, ph


def gate_field_by_field(recorded_gate, recomputed):
    diffs = {}
    keys = set(recorded_gate.get("checks", {})) | set(recomputed.get("checks", {}))
    for k in sorted(keys):
        a = recorded_gate.get("checks", {}).get(k)
        b = recomputed.get("checks", {}).get(k)
        same = (a == b) if not (isinstance(a, float) and isinstance(b, float)) \
            else abs(a - b) < 1e-12
        if not same:
            diffs[k] = {"recorded": a, "recomputed": b}
    for k in ("formed_at", "PASS", "classification"):
        if recorded_gate.get(k) != recomputed.get(k):
            diffs[k] = {"recorded": recorded_gate.get(k), "recomputed": recomputed.get(k)}
    return diffs


# ------------------------------------------------------------------ 2. component tracking
def track(labels, frames, lo_idx, hi_idx):
    """Link components between consecutive tracked frames by cell overlap.
    Returns per-track records and the main-component continuity statistics."""
    n = len(labels)
    tracks = {}                      # track id -> dict
    prev_map = {}                    # cid at frame i-1 -> track id
    cid_to_tid = []                  # per frame: cid -> track id
    next_tid = 0
    per_frame_main_track = []
    continuity_breaks = 0
    for i in range(n):
        lab = labels[i]
        k = int(lab.max()) + 1
        cur_cells = {c: (lab == c) for c in range(k)}
        cur_map = {}
        for c in range(k):
            best, best_ov = None, 0
            if i > 0:
                pl = labels[i - 1]
                ov_ids, ov_cnt = np.unique(pl[cur_cells[c] & (pl >= 0)], return_counts=True)
                if len(ov_ids):
                    j = int(np.argmax(ov_cnt))
                    best, best_ov = int(ov_ids[j]), int(ov_cnt[j])
            if best is not None and best_ov > 0 and best in prev_map:
                tid = prev_map[best]
            else:
                tid = next_tid
                next_tid += 1
                tracks[tid] = {"first": i, "last": i, "n_frames": 0, "max_mass": 0.0}
            cur_map[c] = tid
            t = tracks[tid]
            t["last"] = i
            t["n_frames"] += 1
        # main component of this frame: the SAME definition as spatial.frame_report, i.e. the
        # component of largest (X + Y) mass, so the two never disagree
        mc = frames[i]["main_cid"]
        per_frame_main_track.append(cur_map.get(mc, -1) if k > 0 else -1)
        prev_map = cur_map
        cid_to_tid.append(dict(cur_map))
    # continuity of the main component inside the window
    seg = per_frame_main_track[lo_idx:hi_idx]
    for a, b in zip(seg, seg[1:]):
        if a != b:
            continuity_breaks += 1
    longest, run = 0, 1
    for a, b in zip(seg, seg[1:]):
        run = run + 1 if a == b else 1
        longest = max(longest, run)
    # modal coverage: the share of window frames whose main component belongs to the single
    # most frequent track. Reported ALONGSIDE the declared unbroken-run measure, never instead.
    modal_cover = 0.0
    if seg:
        vals, cnts = np.unique(np.array(seg), return_counts=True)
        modal_cover = float(cnts.max() / len(seg))
    return {"n_tracks": next_tid, "tracks": tracks, "cid_to_tid": cid_to_tid,
            "main_track_per_frame": per_frame_main_track,
            "main_identity_breaks_in_window": int(continuity_breaks),
            "longest_unbroken_main_run_frames": int(longest),
            "modal_main_track_coverage": modal_cover,
            "window_frames": int(hi_idx - lo_idx)}


def halo_vs_fragment(labels, frames, lo_idx, hi_idx, trk, xfields):
    """Every component that is not the main one, at every tracked frame in the window, is
    followed as a track. A track is HALO if it lives less than 1/muX = 250 steps AND never gets
    further than 4*ell_X = 10 from the core centre; FRAGMENT if it does either. Nothing is
    assumed: lifetimes and distances are measured from the tracking graph."""
    Lg = labels[0].shape[0]
    life = {tid: (t["n_frames"] - 1) * TRACK_EVERY for tid, t in trk["tracks"].items()}
    maxd = {tid: 0.0 for tid in trk["tracks"]}
    massmax = {tid: 0.0 for tid in trk["tracks"]}
    sat_mass_frac, sat_count = [], []
    tid_of = trk["cid_to_tid"]
    for i in range(lo_idx, hi_idx):
        lab, fr, xf = labels[i], frames[i], xfields[i]
        k = int(lab.max()) + 1
        if k <= 0 or not isinstance(fr["centre_y"], (int, np.integer)):
            continue
        cy, cx = fr["centre_y"], fr["centre_x"]
        main_c = int(fr["main_cid"])
        xm = np.array([float(xf[lab == c].sum()) for c in range(k)])
        tot = float(xm.sum())
        sat_mass_frac.append(float(tot - xm[main_c]) / tot if tot else np.nan)
        sat_count.append(k - 1)
        for c in range(k):
            if c == main_c:
                continue
            tid = tid_of[i].get(c)
            if tid is None:
                continue
            cells = np.argwhere(lab == c)
            gy = SP.wrapped_abs(cells[:, 0] - cy, Lg).mean()
            gx = SP.wrapped_abs(cells[:, 1] - cx, Lg).mean()
            maxd[tid] = max(maxd[tid], float(np.hypot(gy, gx)))
            massmax[tid] = max(massmax[tid], float(xm[c]))

    main_tids = set(trk["main_track_per_frame"][lo_idx:hi_idx])
    halo, frag, frag_examples, lives = 0, 0, [], []
    long_lived, far_but_short = 0, 0
    for tid, t in trk["tracks"].items():
        if tid in main_tids or t["last"] < lo_idx or t["first"] >= hi_idx:
            continue
        lives.append(life[tid])
        if life[tid] >= 1.0 / MU_X:
            long_lived += 1
        elif maxd[tid] > 4.0 * ELL_X:
            far_but_short += 1
        if life[tid] < 1.0 / MU_X and maxd[tid] <= 4.0 * ELL_X:
            halo += 1
        else:
            frag += 1
            if len(frag_examples) < 8:
                frag_examples.append({"track": int(tid), "life_steps": int(life[tid]),
                                      "max_distance_to_core": round(maxd[tid], 3),
                                      "max_N_X": massmax[tid]})
    return {"n_satellite_tracks": halo + frag, "n_halo_tracks": halo, "n_fragment_tracks": frag,
            "n_long_lived_satellites_ge_tau_death": long_lived,
            "n_short_lived_but_far_satellites": far_but_short,
            "fraction_long_lived": (long_lived / (halo + frag)) if (halo + frag) else float("nan"),
            "halo_fraction_of_satellites": (halo / (halo + frag)) if (halo + frag) else float("nan"),
            "satellite_lifetime_median_steps": float(np.median(lives)) if lives else float("nan"),
            "satellite_lifetime_q90_steps": float(np.quantile(lives, 0.9)) if lives else float("nan"),
            "satellite_lifetime_max_steps": float(max(lives)) if lives else float("nan"),
            "mean_satellite_X_mass_fraction": float(np.nanmean(sat_mass_frac)) if sat_mass_frac else float("nan"),
            "mean_n_satellites_per_frame": float(np.mean(sat_count)) if sat_count else float("nan"),
            "fragment_examples": frag_examples,
            "halo_criterion": "life < 1/muX = %d steps AND max distance to core <= 4*ell_X = %.1f"
                              % (int(1 / MU_X), 4 * ELL_X)}


# ------------------------------------------------------------------ 3. the four axes
def axes(frames, series, lo, hi, lo_idx, hi_idx, null_q):
    F = list(OBS.Recorder.FIELDS)
    seg = series[lo:hi]
    NX = seg[:, F.index("N_X")]
    deaths = seg[:, F.index("deaths_X")]
    win = frames[lo_idx:hi_idx]

    r50 = np.array([f["r50"] for f in win], dtype=float)
    r80 = np.array([f["r80"] for f in win], dtype=float)
    core_frac = np.array([f["core_fraction_within_2ellX"] for f in win], dtype=float)
    wraps = np.array([bool(f["any_component_wraps"]) for f in win])
    mainfrac = np.array([f["main_mass_fraction"] for f in win], dtype=float)
    neff = np.array([f["n_eff_components"] for f in win], dtype=float)
    rg = np.array([f["Rg_pairwise"] for f in win], dtype=float)
    org_c = np.array([f["organiser_to_centre"] for f in win], dtype=float)
    gd = np.array([f["main_geodesic_diameter"] for f in win], dtype=float)
    cen = [(f["centre_y"], f["centre_x"]) for f in win
           if isinstance(f["centre_y"], (int, np.integer))]

    n1q01 = null_q["N1"]["r80"]["0.01"]
    cond_vs_null = r80 <= n1q01
    cond_absolute = r80 <= L / 6.0
    a1_frac = float(np.mean(cond_vs_null & cond_absolute))
    a2_core_frac = float(np.mean(core_frac >= 0.5))
    turnover = float(deaths.sum() / max(NX.mean(), 1e-9))

    return {
        "A1_compactness_fraction_of_frames": a1_frac,
        "A1_PASS": bool(a1_frac >= 0.95),
        "A1_decomposition": {
            "fraction_r80_below_N1_q01": float(np.mean(cond_vs_null)),
            "N1_q01_r80": float(n1q01),
            "fraction_r80_below_L_over_6": float(np.mean(cond_absolute)),
            "L_over_6": L / 6.0,
            "binding_condition": ("absolute L/6" if np.mean(cond_absolute) <
                                  np.mean(cond_vs_null) else "vs N1 null")},
        "r50": {"mean": float(np.nanmean(r50)), "median": float(np.nanmedian(r50)),
                "q95": float(np.nanquantile(r50, 0.95))},
        "main_geodesic_diameter": {"mean": float(np.nanmean(gd)),
                                   "median": float(np.nanmedian(gd)),
                                   "max": float(np.nanmax(gd))},
        "A2_core_exists_fraction_of_frames": a2_core_frac,
        "A3_material_turnover_replacements": turnover,
        "A3_PASS": bool(turnover >= 10.0),
        "A4_no_wrap_all_frames": bool(not wraps.any()),
        "A4_frames_with_wrap": int(wraps.sum()),
        "r80": {"mean": float(np.nanmean(r80)), "median": float(np.nanmedian(r80)),
                "q05": float(np.nanquantile(r80, 0.05)), "q95": float(np.nanquantile(r80, 0.95)),
                "max": float(np.nanmax(r80))},
        "Rg_pairwise": {"mean": float(np.nanmean(rg)), "median": float(np.nanmedian(rg)),
                        "q95": float(np.nanquantile(rg, 0.95)), "max": float(np.nanmax(rg))},
        "core_fraction_within_2ellX": {"mean": float(np.nanmean(core_frac)),
                                       "median": float(np.nanmedian(core_frac)),
                                       "min": float(np.nanmin(core_frac))},
        "main_mass_fraction": {"mean": float(np.nanmean(mainfrac)),
                               "median": float(np.nanmedian(mainfrac)),
                               "min": float(np.nanmin(mainfrac))},
        "n_eff_components": {"mean": float(np.nanmean(neff)),
                             "median": float(np.nanmedian(neff)),
                             "max": float(np.nanmax(neff))},
        "organiser_to_centre": {"mean": float(np.nanmean(org_c)),
                                "median": float(np.nanmedian(org_c)),
                                "q95": float(np.nanquantile(org_c, 0.95))},
        "POPULATION_PERSISTENCE": {"never_zero": bool((NX > 0).all()),
                                   "N_X_min": float(NX.min()), "N_X_mean": float(NX.mean()),
                                   "N_X_median": float(np.median(NX)),
                                   "N_X_max": float(NX.max())},
        "MATERIAL_TURNOVER": {"cumulative_deaths_X": float(deaths.sum()),
                              "mean_standing_N_X": float(NX.mean()),
                              "replacements": turnover,
                              "PASS": bool(turnover >= 10.0)},
        "_centres": cen,
    }


# ------------------------------------------------------------------ 4. nulls at chosen instants
METRICS = ("r50", "r80", "Rg_pairwise", "main_mass_fraction", "n_eff_components",
           "core_fraction_within_2ellX")
MORE_COMPACT_IS = {"r50": "smaller", "r80": "smaller", "Rg_pairwise": "smaller",
                   "main_mass_fraction": "larger", "n_eff_components": "smaller",
                   "core_fraction_within_2ellX": "larger"}


def run_nulls(tr, frames, lo_idx, hi_idx, seed):
    """At N_NULL_INSTANTS instants of the window, draw each null NULL_DRAWS times and place the
    OBSERVED value inside the null distribution. The reported quantity is the observed value's
    position in the null, per instant, so that the comparison is never made against a pooled
    distribution that mixes instants of different N_X."""
    idxs = np.linspace(lo_idx, hi_idx - 1, N_NULL_INSTANTS).astype(int)
    prof = NU.n3_profile(L, P_HOP, MU_X)
    per_instant = []
    agg = {k: {m: [] for m in METRICS} for k in ("N1", "N2", "N3", "N4")}
    beat = {k: {m: [] for m in METRICS} for k in ("N1", "N2", "N3", "N4")}
    pos = {k: {m: [] for m in METRICS} for k in ("N1", "N2", "N3", "N4")}
    for j, i in enumerate(idxs):
        f = frames[i]
        step = int(f["step"])
        N_X = int(f["N_X"])
        if N_X <= 0:
            continue
        nX = tr["xfields"][i].astype(np.int64)
        obs = NU.light_report(nX, ELL_X)
        cy, cx = f["organiser_y"], f["organiser_x"]
        if cy < 0:
            cy, cx = f["centre_y"], f["centre_x"]
        rec = {"frame_index": int(i), "step": step, "N_X": N_X,
               "observed": {m: (None if not np.isfinite(obs[m]) else float(obs[m]))
                            for m in METRICS}}
        for kind in ("N1", "N2", "N3", "N4"):
            kw = {"N_X": N_X}
            if kind == "N2":
                kw.update({"cy": cy, "cx": cx, "T": int(1.0 / MU_X), "p_hop": P_HOP})
            if kind == "N3":
                kw.update({"cy": cy, "cx": cx, "prof": prof})
            if kind == "N4":
                kw.update({"nX": nX})
            d = NU.null_distribution(kind, NULL_DRAWS, seed * 1000 + j * 10 + len(kind) + ord(kind[1]),
                                     L, ELL_X, **kw)
            rec[kind] = {m: NU.quantiles(v) for m, v in d.items() if m in METRICS}
            rec[kind + "_observed_position"] = {}
            for m in METRICS:
                v = d[m][np.isfinite(d[m])]
                o = obs[m]
                if v.size == 0 or not np.isfinite(o):
                    continue
                agg[kind][m].extend(v.tolist())
                p = float((v <= o).mean())                     # quantile of the observation
                pos[kind][m].append(p)
                more = (p <= 0.01) if MORE_COMPACT_IS[m] == "smaller" else (p >= 0.99)
                beat[kind][m].append(bool(more))
                rec[kind + "_observed_position"][m] = p
        per_instant.append(rec)
    pooled = {k: {m: NU.quantiles(np.array(v)) for m, v in dd.items() if v}
              for k, dd in agg.items()}
    summary = {k: {m: {"mean_observed_quantile_in_null":
                       (float(np.mean(pos[k][m])) if pos[k][m] else None),
                       "instants_beating_null_q01_or_q99":
                       (int(np.sum(beat[k][m])) if beat[k][m] else 0),
                       "n_instants": len(pos[k][m])}
                   for m in METRICS} for k in ("N1", "N2", "N3", "N4")}
    return {"per_instant": per_instant, "pooled": pooled, "summary": summary,
            "more_compact_direction": MORE_COMPACT_IS,
            "N2_note": "release at the organiser, diffuse for 1/muX = %d steps" % int(1 / MU_X),
            "N3_note": "exact stationary point-source profile, ell_X = %.4f" % ELL_X,
            "reading": "an observed quantile near 0 for r50/r80/Rg means the observation is MORE "
                       "compact than the null; near 1 means less compact. For "
                       "main_mass_fraction and core_fraction the direction is reversed."}


# ------------------------------------------------------------------ 5. core motion, and N5
def core_motion(frames, lo_idx, hi_idx, seed):
    win = frames[lo_idx:hi_idx]
    cen = [(f["centre_y"], f["centre_x"]) for f in win
           if isinstance(f["centre_y"], (int, np.integer))]
    org = [(f["organiser_y"], f["organiser_x"]) for f in win if f["organiser_y"] >= 0]
    if len(cen) < 3:
        return {"defined": False}
    c = np.array(cen)
    dy = SP.wrapped_abs(np.diff(c[:, 0]), L)
    dx = SP.wrapped_abs(np.diff(c[:, 1]), L)
    step_disp = np.hypot(dy, dx)
    # unwrapped trajectory, to separate net drift from local jitter
    sy = np.cumsum(np.concatenate([[0], ((np.diff(c[:, 0]) + L // 2) % L) - L // 2]))
    sx = np.cumsum(np.concatenate([[0], ((np.diff(c[:, 1]) + L // 2) % L) - L // 2]))
    net = float(np.hypot(sy[-1] - sy[0], sx[-1] - sx[0]))
    path = float(step_disp.sum())
    rng = np.random.default_rng(seed + 991)
    n5 = NU.n5_decorrelated_steps(rng, cen, L)
    out = {"defined": True, "n_frames": len(cen),
           "consecutive_displacement": {"mean": float(step_disp.mean()),
                                        "median": float(np.median(step_disp)),
                                        "q95": float(np.quantile(step_disp, 0.95)),
                                        "max": float(step_disp.max())},
           "N5_decorrelated_displacement": {"mean": float(n5.mean()),
                                            "median": float(np.median(n5)),
                                            "q05": float(np.quantile(n5, 0.05))},
           "N5_separation": float(n5.mean() / max(step_disp.mean(), 1e-9)),
           "net_displacement_unwrapped": net, "path_length": path,
           "net_over_path": net / max(path, 1e-9),
           "rms_unwrapped_displacement": float(np.sqrt(((sy - sy[0]) ** 2 +
                                                        (sx - sx[0]) ** 2).mean()))}
    if len(org) == len(cen):
        o = np.array(org)
        gy = SP.wrapped_abs(c[:, 0] - o[:, 0], L)
        gx = SP.wrapped_abs(c[:, 1] - o[:, 1], L)
        d = np.hypot(gy, gx)
        oy = np.cumsum(np.concatenate([[0], ((np.diff(o[:, 0]) + L // 2) % L) - L // 2]))
        ox = np.cumsum(np.concatenate([[0], ((np.diff(o[:, 1]) + L // 2) % L) - L // 2]))
        out["core_to_organiser"] = {"mean": float(d.mean()), "median": float(np.median(d)),
                                    "q95": float(np.quantile(d, 0.95)), "max": float(d.max())}
        out["organiser_net_displacement_unwrapped"] = float(
            np.hypot(oy[-1] - oy[0], ox[-1] - ox[0]))
        out["core_follows_organiser_corr"] = {
            "y": float(np.corrcoef(sy, oy)[0, 1]) if np.std(oy) > 0 else float("nan"),
            "x": float(np.corrcoef(sx, ox)[0, 1]) if np.std(ox) > 0 else float("nan")}
    return out
