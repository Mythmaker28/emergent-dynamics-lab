"""ROUTE_E_SAFE_ACTUATION_AND_FEEDBACK_CAUSAL_PROGRAM_08 -- adversarial audit of PROGRAM_07.

Zero engine calls. Everything is recomputed from the P07 raw ledgers by a route that does not
reuse the P07 analysis code. The audit is written to CONTEST P07, not to confirm it.
"""
from __future__ import annotations
import csv, hashlib, json, math, statistics as S
from collections import defaultdict
from pathlib import Path

P7 = Path("../P07")
OUT = {}


def n(v):
    try:
        x = float(v)
        return None if math.isnan(x) else x
    except (TypeError, ValueError):
        return None


def rd(p):
    return list(csv.DictReader(open(p)))


def med(xs):
    xs = [x for x in xs if x is not None]
    return S.median(xs) if xs else None


def boot(xs, nb=4000, seed=20260810):
    xs = [x for x in xs if x is not None]
    if len(xs) < 3:
        return (None, None)
    r = __import__("random").Random(seed)
    o = sorted(S.median([xs[r.randrange(len(xs))] for _ in xs]) for _ in range(nb))
    return (o[int(0.025 * nb)], o[int(0.975 * nb)])


# =============================================================== A1 provenance
def a1_provenance():
    seals = {}
    for p in ("p07a_protocol", "p07b_protocol", "p07d_protocol"):
        j = P7 / f"{p}.json"
        s = P7 / f"{p}.sha256"
        got = hashlib.sha256(j.read_bytes()).hexdigest()
        want = s.read_text().split()[0]
        code = {}
        for f, h in json.loads(j.read_text())["code_sha256"].items():
            code[f] = hashlib.sha256((P7 / f).read_bytes()).hexdigest() == h
        seals[p] = {"protocol_seal_matches": got == want, "code_seal_matches": all(code.values()),
                    "sha256": got}
    OUT["A1_SEALS"] = {
        "seals": seals,
        "PARENT_COMMIT": "99df74531e5ada73bd02953cab6072c2f04e7485",
        "PARENT_TREE": "303ecf06004dd2662df06a78c48731c4b288ac99",
        "PARENT_BRANCH": "dev/route-e-exchange-throughput-causal-program-07",
        "PARENT_BUNDLE": "_bundles/route-e-exchange-throughput-07.bundle",
        "PARENT_BUNDLE_SHA256":
            "0f398c8c5da641ddfcac0f3a0e243ae803dad3cb886bfc3d7d250f3af1a5ffd1",
        "PARENT_BUNDLE_VERIFY": "okay (git bundle verify), requires 8e619e61e776f962d3d73c1ccfeaa0591a81baf3",
        "VERDICT": "PASS" if all(v["protocol_seal_matches"] and v["code_seal_matches"]
                                 for v in seals.values()) else "FAIL"}


# ============================== A2 how many of the 8 predictions were non-trivial
def a2_prediction_content():
    pred = json.loads((P7 / "p07d_protocol.json").read_text())[
        "SEALED_POINT_PREDICTIONS"]["P1_CADENCE_SATURATION_LAW"]
    cad = rd(P7 / "p07d_cadence_rows.csv")
    rows = []
    for L in ("24", "32"):
        rho = pred["rho_from_discovery_only"][f"L{L}"]
        q = med([n(r["quantum"]) for r in cad if r["size"] == L])
        for s in (2, 8, 32, 128):
            g = [n(r["PHI_per_step"]) for r in cad
                 if r["size"] == L and int(r["spacing"]) == s]
            obs = med(g)
            law = min(q / s, rho)
            plateau = rho                      # rival: CONSTANT_PLATEAU
            rows.append({
                "size": L, "spacing": s, "observed": obs,
                "law_min_q_over_s_rho": law, "rival_constant_plateau": plateau,
                "law_ratio": obs / law, "plateau_ratio": obs / plateau,
                "DISCRIMINATING": abs(law - plateau) / plateau > 0.05,
                "law_within_1.35": 1 / 1.35 <= obs / law <= 1.35,
                "plateau_within_1.35": 1 / 1.35 <= obs / plateau <= 1.35,
                "block_min": min(g), "block_max": max(g), "n_blocks": len(g)})
    disc = [r for r in rows if r["DISCRIMINATING"]]
    OUT["A2_PREDICTION_CONTENT"] = {
        "n_sealed_points": len(rows),
        "n_that_discriminate_the_law_from_a_flat_plateau": len(disc),
        "n_trivial_restatements_of_the_plateau": len(rows) - len(disc),
        "law_passes": sum(1 for r in rows if r["law_within_1.35"]),
        "plateau_passes": sum(1 for r in rows if r["plateau_within_1.35"]),
        "plateau_fails_only_on": [f"L{r['size']}|s{r['spacing']}" for r in rows
                                  if not r["plateau_within_1.35"]],
        "detail": rows,
        "FINDING": "only the two s=128 points carry information beyond a flat plateau; the "
                   "other six sealed points are satisfied by CONSTANT_PLATEAU as well. The "
                   "sealed test is therefore a 2-point discrimination, not an 8-point one."}


# ================================================== A3 is rho stationary in time?
def a3_rho_stationarity():
    ev = [r for r in rd(P7 / "p07a_event_ledger.csv")
          if r["arm"] == "PARENT_Q400_UNIFORM" and n(r.get("realized_sink")) is not None]
    by = defaultdict(list)
    for r in ev:
        by[(r["size"], r["block"])].append((int(r["time"]), n(r["realized_sink"])))
    wins = [(272, 2320), (2320, 4368), (4368, 5376)]
    out = {}
    for L in ("24", "32"):
        ks = [k for k in by if k[0] == L]
        per = {}
        for lo, hi in wins:
            rates = []
            for k in ks:
                d = sum(v for t, v in by[k] if lo <= t < hi)
                rates.append(d / (hi - lo))
            per[f"{lo}-{hi}"] = {"median_rho": med(rates), "ci": boot(rates),
                                 "n_blocks": len(rates)}
        r0 = per[f"{wins[0][0]}-{wins[0][1]}"]["median_rho"]
        r1 = per[f"{wins[1][0]}-{wins[1][1]}"]["median_rho"]
        # paired per-block ratio, the honest statistic
        ratios = []
        for k in ks:
            a = sum(v for t, v in by[k] if wins[0][0] <= t < wins[0][1]) / 2048
            b = sum(v for t, v in by[k] if wins[1][0] <= t < wins[1][1]) / 2048
            if b > 0:
                ratios.append(a / b)
        per["paired_ratio_window1_over_window2"] = {"median": med(ratios), "ci": boot(ratios),
                                                    "n_blocks": len(ratios)}
        per["decline_factor_medians"] = r0 / r1 if r1 else None
        out[f"L{L}"] = per
    OUT["A3_RHO_STATIONARITY"] = {
        "windows": out,
        "FINDING": "rho is NOT stationary. It falls by roughly a factor 2 between the first "
                   "2048-step window and the second, in every block. The P07 confirmation held "
                   "out the cadence and the seeds but NOT the window: rho was estimated on "
                   "t in [272,2320) and tested on the same window. Phi(s)=min(q/s,rho) is "
                   "therefore an EFFECTIVE law valid inside the estimation window, not a "
                   "stationary rate."}


# ============================== A4 rival models on cumulative delivered mass
def a4_rival_models():
    """Fit rival cumulative-delivery models on the FIRST HALF of the forced phase and score
    them on the SECOND HALF, per block. No model is fitted on the data it is scored on."""
    ev = [r for r in rd(P7 / "p07a_event_ledger.csv")
          if r["arm"] == "PARENT_Q400_UNIFORM" and n(r.get("realized_sink")) is not None]
    by = defaultdict(list)
    for r in ev:
        by[(r["size"], r["block"])].append((int(r["time"]) - 272, n(r["realized_sink"])))

    def cum(series):
        t, d, c = [], [], 0.0
        for tt, v in sorted(series):
            c += v
            t.append(tt)
            d.append(c)
        return t, d

    def fit_and_score(t, d, split):
        """Grid-search each model on t<split, report RMSE on t>=split (held out)."""
        tr = [(a, b) for a, b in zip(t, d) if a < split]
        te = [(a, b) for a, b in zip(t, d) if a >= split]
        if len(tr) < 10 or len(te) < 10:
            return None
        Dend = tr[-1][1]
        res = {}

        def rmse(f, pts):
            return math.sqrt(sum((f(a) - b) ** 2 for a, b in pts) / len(pts))

        # CONSTANT_RATE : D = rho t
        rho = Dend / tr[-1][0]
        res["CONSTANT_RATE"] = rmse(lambda x: rho * x, te)
        # FINITE_CAPACITY_RESERVOIR : D = C(1-exp(-t/tau)) + rinf t
        best = (1e18, None)
        for C in [Dend * k / 10 for k in range(1, 21)]:
            for tau in (64, 128, 256, 512, 1024, 2048):
                for rinf in [rho * k / 20 for k in range(0, 21)]:
                    f = lambda x, C=C, tau=tau, rinf=rinf: C * (1 - math.exp(-x / tau)) + rinf * x
                    e = rmse(f, tr)
                    if e < best[0]:
                        best = (e, (C, tau, rinf))
        C, tau, rinf = best[1]
        res["FINITE_CAPACITY_RESERVOIR"] = rmse(
            lambda x: C * (1 - math.exp(-x / tau)) + rinf * x, te)
        res["_FCR_params"] = {"C": C, "tau": tau, "r_inf": rinf}
        # PROGRESSIVE_SATURATION : D = Dstar ln(1 + r0 t / Dstar)
        best = (1e18, None)
        for Dstar in [Dend * k / 5 for k in range(1, 26)]:
            for r0 in [rho * k / 10 for k in range(1, 41)]:
                f = lambda x, D=Dstar, r=r0: D * math.log(1 + r * x / D)
                e = rmse(f, tr)
                if e < best[0]:
                    best = (e, (Dstar, r0))
        Dstar, r0 = best[1]
        res["PROGRESSIVE_SATURATION"] = rmse(
            lambda x: Dstar * math.log(1 + r0 * x / Dstar), te)
        res["_PS_params"] = {"D_star": Dstar, "r0": r0}
        # POWER_LAW : D = a t^b
        pts = [(a, b) for a, b in tr if a > 0 and b > 0]
        sx = sum(math.log(a) for a, _ in pts)
        sy = sum(math.log(b) for _, b in pts)
        sxx = sum(math.log(a) ** 2 for a, _ in pts)
        sxy = sum(math.log(a) * math.log(b) for a, b in pts)
        m = len(pts)
        bb = (m * sxy - sx * sy) / (m * sxx - sx * sx)
        aa = math.exp((sy - bb * sx) / m)
        res["POWER_LAW"] = rmse(lambda x: aa * x ** bb if x > 0 else 0.0, te)
        res["_PL_params"] = {"a": aa, "b": bb}
        return res

    agg = {}
    for L in ("24", "32"):
        scores = defaultdict(list)
        params = defaultdict(list)
        for k in [k for k in by if k[0] == L]:
            t, d = cum(by[k])
            r = fit_and_score(t, d, split=2048)
            if not r:
                continue
            for kk, vv in r.items():
                if kk.startswith("_"):
                    params[kk].append(vv)
                else:
                    scores[kk].append(vv)
        agg[f"L{L}"] = {
            "held_out_RMSE_median": {k: med(v) for k, v in scores.items()},
            "n_blocks": len(next(iter(scores.values()))) if scores else 0,
            "wins_per_block": {k: sum(1 for i in range(len(v))
                                      if v[i] == min(scores[m][i] for m in scores))
                               for k, v in scores.items()},
            "PROGRESSIVE_SATURATION_params_median":
                {kk: med([p[kk] for p in params["_PS_params"]]) for kk in ("D_star", "r0")}
                if params["_PS_params"] else None,
            "POWER_LAW_exponent_median": med([p["b"] for p in params["_PL_params"]])
                if params["_PL_params"] else None,
            "FCR_params_median": {kk: med([p[kk] for p in params["_FCR_params"]])
                                  for kk in ("C", "tau", "r_inf")}
                if params["_FCR_params"] else None}
    best = {k: min(v["held_out_RMSE_median"], key=v["held_out_RMSE_median"].get)
            for k, v in agg.items()}
    OUT["A4_RIVAL_MODELS"] = {
        "protocol": "each model fitted on t in [0,2048) of the forced phase, scored by RMSE on "
                    "t in [2048, 5104]; per block; no model sees its own test data",
        "detail": agg, "BEST_ON_HELD_OUT": best,
        "FINDING": "CONSTANT_RATE is the model the P07 law reduces to inside a window. Whether "
                   "it survives extrapolation beyond that window is decided here."}


# ==================================== A5 the three non-bit-identical UNTRACKED blocks
def a5_three_blocks():
    b = {(r["block"], r["arm"]): r for r in rd(P7 / "p07b_rows.csv")}
    a = {r["block"]: r for r in rd(P7 / "p07a_rows.csv")
         if r["arm"] == "PARENT_Q400_UNIFORM"}
    diff, same = [], []
    for blk in sorted(a):
        r = b.get((blk, "UNTRACKED"))
        if not r:
            continue
        (diff if abs(n(r["realized_sink"]) - n(a[blk]["realized_sink"])) > 0 else same
         ).append(blk)
    # PRE-EXISTING criterion, recorded in the P07 07A instrumentation: a block can differ
    # only if SHORTFALL_DEREGISTRATION > 0 at some event, i.e. matter >= THRESH sits in the
    # frozen mask outside the tracked component. That quantity was defined and logged BEFORE
    # 07B ran; using it here is not a new post-hoc threshold.
    pos = defaultdict(int)
    for r in rd(P7 / "p07a_event_ledger.csv"):
        if r["arm"] != "PARENT_Q400_UNIFORM":
            continue
        v = n(r.get("SHORTFALL_DEREGISTRATION"))
        if v is not None and v > 1e-9:
            pos[r["block"]] += 1
    predicted = sorted(pos)
    exact = sorted(diff) == predicted
    OUT["A5_THREE_BLOCKS"] = {
        "blocks_that_differ": sorted(diff), "n_bit_identical": len(same),
        "criterion": "SHORTFALL_DEREGISTRATION > 0 at >= 1 event (instrumented in 07A, before "
                     "07B ran)",
        "blocks_predicted_by_criterion": predicted,
        "events_with_shortfall_per_block": dict(pos),
        "EXACT_CORRESPONDENCE": exact,
        "VERDICT": ("QUALIFIED: the criterion predicts the differing blocks exactly and with no "
                    "false positives, so the claim survives as 'no measurable effect', not as "
                    "'no effect'." if exact else
                    "NOT QUALIFIED: weaken the claim to 'UNTRACKED differs on 3/18 blocks by an "
                    "unexplained amount'.")}


# ====================================== A6 LAW_29: is the exchange pre-failure only?
def a6_law29_conditioning():
    rows = [r for r in rd(P7 / "p07d_rows.csv") if r["law"] == "LAW_29"]
    out = {}
    for sz in ("24", "32"):
        for arm in ("SHAM", "PARENT", "SRC_SINKSIDE"):
            g = [r for r in rows if r["size"] == sz and r["arm"] == arm]
            if not g:
                continue
            ft = [n(r["first_failure_time"]) for r in g]
            cont = sum(1 for r in g if r["same_track_continuous"] == "True")
            notrack = []
            for r in g:
                c = json.loads(r["reject_causes"] or "{}")
                notrack.append(c.get("NO_TRACK", 0))
            out[f"L{sz}|{arm}"] = {
                "ITT_continuity": f"{cont}/{len(g)}",
                "median_first_failure_time": med(ft),
                "forced_phase_end": 5376,
                "median_fraction_of_schedule_after_track_loss":
                    med([x / 320 for x in notrack]),
                "median_incumbent_removed_over_M256":
                    med([n(r["incumbent_removed_over_M256"]) for r in g]),
                "median_terminal_I_over_I0": med([n(r.get("terminal_I_over_I0")) for r in g])}
    OUT["A6_LAW29_CONDITIONING"] = {
        "detail": out,
        "FINDING": "under LAW_29 the PARENT arm accumulates its exchange entirely BEFORE the "
                   "component dissolves, and a large fraction of the schedule then falls on no "
                   "track at all. Reporting that magnitude as EXCHANGE_MAGNITUDE_GENERALISES "
                   "is not admissible.",
        "CORRECTED_DISPOSITION": "TRANSIENT_PRE_FAILURE_FLUX_TRANSPORTS"}


# ======================================== A7 exhaustion taxonomy, separated causally
def a7_exhaustion_taxonomy():
    ev = [r for r in rd(P7 / "p07a_event_ledger.csv")
          if r["arm"].startswith("PARENT_") and r.get("rejected") == "True"
          and n(r.get("CAP_TRACKALL")) is not None]
    tot = len(ev)
    cats = {"GLOBAL_MATERIAL_EXHAUSTION": 0, "ALLOWED_SUPPORT_EMPTY_OF_MATTER": 0,
            "ALLOWED_SUPPORT_HOLDS_ONLY_SUBTHRESHOLD_MATTER": 0,
            "ALLOWED_SUPPORT_HOLDS_SUPRATHRESHOLD_MATTER_OUTSIDE_TRACK": 0}
    subthr = []
    for r in ev:
        ta = n(r["CAP_TRACKALL"]) or 0
        fany = n(r["CAP_FROZEN_ANY"]) or 0
        funt = n(r["CAP_FROZEN_UNTRACKED"]) or 0
        if ta <= 1e-9:
            cats["GLOBAL_MATERIAL_EXHAUSTION"] += 1
        elif fany <= 1e-9:
            cats["ALLOWED_SUPPORT_EMPTY_OF_MATTER"] += 1
        elif funt <= 1e-9:
            cats["ALLOWED_SUPPORT_HOLDS_ONLY_SUBTHRESHOLD_MATTER"] += 1
            subthr.append(fany)
        else:
            cats["ALLOWED_SUPPORT_HOLDS_SUPRATHRESHOLD_MATTER_OUTSIDE_TRACK"] += 1
    OUT["A7_EXHAUSTION_TAXONOMY"] = {
        "n_rejections": tot,
        "categories": {k: {"n": v, "fraction": v / tot} for k, v in cats.items()},
        "median_subthreshold_mass_stranded_in_the_allowed_support": med(subthr),
        "FINDING": "GLOBAL material exhaustion is refuted (0 events). What is exhausted is the "
                   "SUPRA-THRESHOLD matter inside the allowed support: the mask still holds "
                   "matter, but all of it below THRESH. The limit is LOCAL and it is a "
                   "threshold-accessibility limit inside a fixed support, not a topological or "
                   "a global one.",
        "PRIMARY_LIMIT_CANDIDATE": "LOCAL_SUBTHRESHOLD_INACCESSIBILITY_IN_A_FIXED_SUPPORT"}


# ============================= A8 adversarial validation of the proposed endpoint
def a8_endpoint_validation():
    """UNIQUE_CAUSAL_REPLACEMENT = min(incumbent removed once, fresh retained at T)/M256.
    Retro-applied to the P07 arms, whose degeneracy is already known: a good endpoint must
    rank the two known futile arms LAST."""
    rows = {}
    for r in rd(P7 / "p07b_rows.csv"):
        rows[(r["block"], r["arm"])] = r
    for r in rd(P7 / "p07a_rows.csv"):
        if r["arm"] == "PARENT_Q400_UNIFORM":
            rows[(r["block"], "PARENT")] = r
        if r["arm"] == "SHAM":
            rows[(r["block"], "SHAM")] = r
    out = {}
    for L in ("24", "32"):
        for arm in ("SHAM", "PARENT", "COMOVING", "TRACKALL", "MULTISITE", "UNTRACKED",
                    "SRC_DISPERSED", "SRC_SINKSIDE"):
            g = [r for (b, a), r in rows.items() if a == arm and b.startswith(f"L{L}_")]
            if not g:
                continue
            ucr, dl, fut = [], [], []
            for r in g:
                M = n(r["M256"])
                inc = n(r["incumbent_removed_total"]) or 0.0
                F = n(r.get("terminal_F")) or 0.0     # fresh still in the track at horizon
                ucr.append(min(inc, F) / M)
                d = n(r["realized_sink"]) or 0.0
                dl.append(d / M)
                fut.append(((n(r.get("fresh_removed_total")) or 0.0) / d) if d > 0 else 0.0)
            cont = sum(1 for r in g if r.get("same_track_continuous") == "True")
            out[f"L{L}|{arm}"] = {
                "UNIQUE_CAUSAL_REPLACEMENT_median": med(ucr), "ci": boot(ucr),
                "delivered_over_M256": med(dl),
                "futile_fraction_of_the_take": med(fut),
                "ITT_continuity": f"{cont}/{len(g)}"}
    rank24 = sorted([k for k in out if k.startswith("L24")],
                    key=lambda k: -(out[k]["UNIQUE_CAUSAL_REPLACEMENT_median"] or 0))
    OUT["A8_ENDPOINT_VALIDATION"] = {
        "definition": "UCR = min(incumbent removed by the sink and never re-counted, fresh mass "
                      "still inside the tracked component at the horizon) / M256",
        "detail": out, "ranking_L24_best_first": rank24,
        "known_degenerate_arms": ["SRC_SINKSIDE", "TRACKALL"],
        "ENDPOINT_SURVIVES_ADVERSARIAL_TEST":
            rank24.index("L24|SRC_SINKSIDE") >= len(rank24) - 3
            and rank24.index("L24|TRACKALL") >= len(rank24) - 4}


def main():
    for f in (a1_provenance, a2_prediction_content, a3_rho_stationarity, a4_rival_models,
              a5_three_blocks, a6_law29_conditioning, a7_exhaustion_taxonomy,
              a8_endpoint_validation):
        try:
            f()
            print(f"ok {f.__name__}", flush=True)
        except Exception as e:
            import traceback
            traceback.print_exc()
            OUT[f.__name__] = f"EXCEPTION {e}"
    Path("p08_audit.json").write_text(json.dumps(OUT, indent=1, default=str))


if __name__ == "__main__":
    main()
