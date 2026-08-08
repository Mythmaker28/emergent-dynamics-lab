"""ROUTE_E_DYNAMIC_SOURCE_CAPTURE_DEV_04 -- prospective DEV run.

Refuses to touch the engine unless dynamic_source_capture_protocol.json matches its sealed
SHA-256 (PRESEAL_GUARD). Production engine, detector and advance_passive_tracer unchanged.
"""
from __future__ import annotations
import csv, hashlib, json, math, sys, time
from pathlib import Path
import numpy as np

from od_core import *
from dsc_core import (Provenance, Causal, build_masks_04, coupled_event, outer_shell,
                      CONS_TOL, NUM_TOL_REL, THRESH, MMAX)
from bridge00_harness import law_arms
from morph02_ic import ic_single_disc

CAD = 16
T_B, T_F, T_E = 256, 1536, 2048
P = 0.35
SIZES = (24, 32)
SEEDS_PER = 9
AXORD = ("+x", "-x", "+y", "-y")
SMOOTH = [272 + 16 * (e - 1) for e in range(1, 81)]
SEED_BASE = 980000                      # DEV_DYNAMIC_SOURCE_CAPTURE_04, never reused

# arm -> (gd_source, redesigned_filter, dose_fraction, mode)
ARMS = {
    "SHAM":                     (2, True,  0.00, "SHAM"),
    "D1_LEGACY_Q005":           (1, False, 0.05, "COUPLED"),
    "D1_REDESIGNED_Q005":       (1, True,  0.05, "COUPLED"),
    "D2_REDESIGNED_Q005":       (2, True,  0.05, "COUPLED"),
    "D2_REDESIGNED_Q020":       (2, True,  0.20, "COUPLED"),
    "D2_REDESIGNED_Q050":       (2, True,  0.50, "COUPLED"),
    "D2_REDESIGNED_Q100":       (2, True,  1.00, "COUPLED"),
    "DIRECT_INTERFACE_Q100":    (2, True,  1.00, "DIRECT_INTERFACE"),
}
ARM_ORDER = list(ARMS)
PROTOCOL = "dynamic_source_capture_protocol.json"
SEAL = "dynamic_source_capture_protocol.sha256"


# ------------------------------------------------------------------ preseal guard
def preseal_guard():
    p, s = Path(PROTOCOL), Path(SEAL)
    if not p.exists() or not s.exists():
        sys.exit("PRESEAL_GUARD: protocol or seal missing -- no engine call permitted.")
    got = hashlib.sha256(p.read_bytes()).hexdigest()
    want = s.read_text().split()[0].strip()
    if got != want:
        sys.exit(f"PRESEAL_GUARD: protocol hash mismatch\n  sealed={want}\n  actual={got}")
    for f in ("dsc_core.py", "dsc_harness.py"):
        h = hashlib.sha256(Path(f).read_bytes()).hexdigest()
        rec = json.loads(p.read_text())["code_sha256"].get(f)
        if rec and rec != h:
            sys.exit(f"PRESEAL_GUARD: {f} changed after seal\n  sealed={rec}\n  actual={h}")
    return got


def prephase(law, m, L):
    eng = LatticeBondEngine(law)
    st = LatticeBondState(m.copy(), np.full((L, L), 0.8), np.zeros((2, L, L)), 0)
    while int(st.step) < T_B:
        st = eng.step(st).state
    return st


def label_map(state, track_cells):
    """cell -> component index, for every detected component EXCEPT the track."""
    out = {}
    for c in comps(state):
        cs = cells_of(c)
        if cs == track_cells:
            continue
        for i in cs:
            out[i] = c.index
    return out


def branch(law, st0, masks, arm, L, M256, cells256):
    gd_src, redesigned, dose_frac, mode = ARMS[arm]
    eng = LatticeBondEngine(law)
    st = st0.copy()
    prov = Provenance(st, cells256)
    cz = Causal(st.m.shape, CAD)
    total0 = float(st.m.sum())
    Q = dose_frac * M256
    qe = Q / len(SMOOTH) if Q > 0 else 0.0
    S = set(SMOOTH)

    realized_src = realized_sink = 0.0
    inc_egress = fre_to_sink = 0.0
    direct_insert = 0.0
    flux_deficit = 0.0
    reject_counts = {}
    alg_err = 0.0
    first = None; ftype = "NONE"; prev = None
    snap = {}
    t = int(st.step)
    while t < T_E:
        if t in S and mode != "SHAM":
            c = largest_bounded(st)
            track = cells_of(c) if c is not None else set()
            if track:
                r = coupled_event(st, prov, masks, track, L, qe, mode, redesigned)
                realized_sink += r["removed"]; realized_src += r["injected"]
                inc_egress += r["inc_to_sink"]; fre_to_sink += r.get("fre_to_sink", 0.0)
                direct_insert += r.get("direct_insertion", 0.0)
                flux_deficit += r["flux_deficit"]
                for k, v in r["reject_counts"].items():
                    reject_counts[k] = reject_counts.get(k, 0) + v
                # transit is credited only where continuously-resident fresh existed
                if cz.window_min(16) > 1e-12:
                    cz.transit += r.get("fre_to_sink", 0.0)
                cz.transit_raw += r.get("fre_to_sink", 0.0)
                cz.direct_insertion += r.get("direct_insertion", 0.0)
                alg_err = max(alg_err, prov.balance_error(st))
                # HARD PROHIBITION: the operator must never make a halo site supra-threshold
                if mode == "COUPLED":
                    fm = st.m.reshape(-1)
                    for s_, tag in r.get("sites", []):
                        if tag == "ACCEPTED_SUBTHRESHOLD_ADJACENT" and fm[s_] >= THRESH:
                            raise AssertionError("DIRECT_CONNECTION_CREATED_BY_OPERATOR")
        elif t in S:
            flux_deficit += qe
        pre = st
        o = eng.step(pre)
        prov.advance(pre.m, o.ledger, o.state.m, law.dt)
        st = o.state
        t = int(st.step)
        alg_err = max(alg_err, prov.balance_error(st))
        if t % CAD == 0:
            c = largest_bounded(st)
            cells = cells_of(c) if c is not None else None
            labels = label_map(st, cells) if cells is not None else None
            cz.update(st, prov, cells, labels, L, t)
            bad = None
            if c is None:
                bad = "TRACK_LOST_OR_DISSOLVED"
            elif c.wraps_x or c.wraps_y:
                bad = "WRAPPING"
            elif prev is not None:
                d = math.hypot(c.centroid_y - prev[0], c.centroid_x - prev[1])
                ar = c.area / max(1, prev[2])
                if d > 3.0 or not (1 / 3.0 <= ar <= 3.0):
                    bad = "TRACK_LOSS"
            if bad and first is None:
                first, ftype = t, bad
            if c is not None:
                prev = (c.centroid_y, c.centroid_x, c.area)
            if t in (T_F, T_F + CAD, T_E):
                fm = st.m.reshape(-1)
                ci, cf = prov.inc.reshape(-1), prov.fre.reshape(-1)
                if cells:
                    mass = float(sum(fm[i] for i in cells))
                    inc = float(sum(ci[i] for i in cells))
                    fre = float(sum(cf[i] for i in cells))
                else:
                    mass = inc = fre = float("nan")
                snap[t] = {"mass": mass, "inc": inc, "fre": fre,
                           "area": (c.area if c is not None else 0),
                           "track": cells is not None,
                           "wrap": bool(c is not None and (c.wraps_x or c.wraps_y))}

    sys_err = prov.system_error(st, total0)

    def alive(H):
        return first is None or first > H

    def get(H, k):
        s = snap.get(H)
        return s[k] if (s and s["track"] and alive(H)) else None

    post = T_F + CAD            # first readout after a full engine interval past the last event
    row = {
        "arm": arm, "L": L, "M256": M256, "gd_source": gd_src,
        "filter": "REDESIGNED_P2PRIME" if redesigned else "LEGACY_P2",
        "mode": mode, "dose_fraction": dose_frac, "planned_dose": Q, "q_per_event": qe,
        "realized_source_injection": realized_src, "realized_sink_removal": realized_sink,
        "flux_deficit": flux_deficit,
        "unique_contact": cz.contact,
        "unique_capture_transport": cz.capture_transport,
        "capture_engulfment": cz.capture_engulf,
        "capture_by_merger": cz.capture_by_merger,
        "direct_operator_insertion": cz.direct_insertion,
        "incorporation_16": cz.incorporation_16,
        "durable_incorporation_128": cz.durable_128,
        "unique_incumbent_egress_to_sink": inc_egress,
        "directional_transit": cz.transit,
        "directional_transit_raw": cz.transit_raw,
        "algebraic_ledger_error": alg_err,
        "total_system_balance_error": sys_err,
        "survival_1536": alive(T_F), "survival_2048": alive(T_E),
        "coast_survival": alive(T_E),
        "first_failure_time": first, "first_failure_type": ftype,
        "reject_counts": json.dumps(reject_counts, sort_keys=True),
    }
    for tag, H in (("postforce", post), ("2048", T_E)):
        mass, inc, fre = get(H, "mass"), get(H, "inc"), get(H, "fre")
        row[f"tracked_mass_{tag}"] = mass
        row[f"incumbent_absolute_residual_{tag}"] = (inc / M256) if inc is not None else None
        row[f"incumbent_current_fraction_{tag}"] = (inc / mass) if (inc is not None and mass) else None
        row[f"fresh_current_fraction_{tag}"] = (fre / mass) if (fre is not None and mass) else None
        row[f"fresh_retention_{tag}"] = (fre / M256) if fre is not None else None
        row[f"incumbent_loss_{tag}"] = ((M256 - inc) / M256) if inc is not None else None
        row[f"mass_ratio_{tag}"] = (mass / M256) if mass is not None else None
        if inc is not None and fre is not None:
            row[f"matched_replacement_{tag}"] = min(M256 - inc, fre) / M256
            row[f"replacement_mismatch_{tag}"] = abs((M256 - inc) - fre) / M256
            row[f"sink_matched_replacement_{tag}"] = min(inc_egress, fre) / M256
        else:
            row[f"matched_replacement_{tag}"] = None
            row[f"replacement_mismatch_{tag}"] = None
            row[f"sink_matched_replacement_{tag}"] = None
    fr_post, fr_end = row["fresh_retention_postforce"], row["fresh_retention_2048"]
    row["coast_retention_ratio"] = (fr_end / fr_post) if (fr_post and fr_end is not None) else None
    row["endpoint_defined"] = bool(row["tracked_mass_2048"] is not None)
    return row


def main():
    seal = preseal_guard()
    print(f"PRESEAL_GUARD OK  protocol sha256 = {seal}")
    law = law_arms()["LAW_16"]
    rows, manifest = [], []
    engine_calls = 0
    t0 = time.time()
    for li, L in enumerate(SIZES):
        for k in range(SEEDS_PER):
            seed = SEED_BASE + li * 100 + k
            m = np.ascontiguousarray(ic_single_disc(np.random.default_rng(seed), L, P),
                                     dtype=np.float64)
            h0 = fhash(m, np.full((L, L), 0.8), np.zeros((2, L, L)))
            st = prephase(law, m, L); engine_calls += 1
            c = largest_bounded(st)
            n_comp = len(comps(st))
            if c is None:
                status = "T256_DISSOLVED" if n_comp == 0 else "T256_TRACK_LOST"
            elif c.wraps_x or c.wraps_y:
                status = "T256_WRAPPING"
            else:
                status = "T256_VALID_TRACK"
            if status != "T256_VALID_TRACK":
                manifest.append({"L": L, "seed": seed, "t256_status": status, "t0_sha256": h0})
                for a in ARM_ORDER:
                    rows.append({"L": L, "seed": seed, "arm": a, "t256_status": status,
                                 "t0_sha256": h0, "endpoint_defined": False})
                continue
            cells = cells_of(c)
            M256 = float(sum(st.m.reshape(-1)[i] for i in cells))
            axis = AXORD[k % 4]
            hb = fhash(st.m, st.n, st.b)
            masks = {g: build_masks_04(cells, L, c.centroid_y, c.centroid_x, axis, g)
                     for g in (1, 2)}
            manifest.append({"L": L, "seed": seed, "axis": axis, "t256_status": status,
                             "t0_sha256": h0, "t256_checkpoint_sha256": hb, "M256": M256,
                             "area256": c.area, "n_components_t256": n_comp,
                             "mask_sizes": {f"gd{g}": {"sink": len(masks[g]["sink"]),
                                                       "source": len(masks[g]["source"]),
                                                       "interface": len(masks[g]["source_interface"])}
                                            for g in (1, 2)}})
            copies = {a: st.copy() for a in ARM_ORDER}
            ref = copies[ARM_ORDER[0]]
            for a in ARM_ORDER:
                assert np.array_equal(ref.m, copies[a].m)
                assert np.array_equal(ref.n, copies[a].n)
                assert np.array_equal(ref.b, copies[a].b)
                assert fhash(copies[a].m, copies[a].n, copies[a].b) == hb
            for a in ARM_ORDER:
                gd = ARMS[a][0]
                r = branch(law, copies[a], masks[gd], a, L, M256, cells)
                engine_calls += 1
                r.update(seed=seed, axis=axis, t0_sha256=h0, t256_checkpoint_sha256=hb,
                         t256_status=status, area256=c.area)
                rows.append(r)
            print(f"  L={L} seed={seed} ({len(rows)}/{18*8}, {time.time()-t0:.0f}s)", flush=True)
    Path("t256_branch_manifest.json").write_text(json.dumps(
        {"mission": "ROUTE_E_DYNAMIC_SOURCE_CAPTURE_DEV_04",
         "protocol_sha256": seal, "blocks": manifest,
         "engine_invocations": engine_calls}, indent=1))
    fields = sorted({k for r in rows for k in r})
    with Path("dynamic_source_capture_rows.csv").open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(f"\n{len(rows)} trajectoires, {engine_calls} appels moteur ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
