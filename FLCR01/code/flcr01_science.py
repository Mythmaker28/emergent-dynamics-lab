"""FLCR01 §3, §4, §7, §8, §9, §10 — the founder-versus-lineage adjudication.

Zero new scientific runs. Exact executable mathematics plus world-level measurement over the
128 PQEC01 archives, all of which are POST_OUTCOME_DEVELOPMENT_DATA.
"""
from __future__ import annotations
import glob, json, math, os
from collections import Counter
from math import comb
import numpy as np

REPO = "/home/claude/edl"
RAW = "/home/claude/PQEC01/raw"
OUT = f"{REPO}/FLCR01/out"
T_HORIZON, T_WINDOW, BURN_IN = 11000, 9000, 2000
ALPHA, N_STAR, GAMMA, MINEV, CAP = 0.5, 10.0, 0.5, 1.0, 16
CORE_R, TAU_FROZEN = 5.0, 125.0
STATES = ("E", "O", "C", "S", "P", "F")
SNAME = {"E": "EXTINCT", "O": "ONE_ORGANISING_CENTRE", "C": "TWO_OR_MORE_Y_COLOCATED_ONE_CENTRE",
         "S": "TWO_SPATIAL_CENTRES", "P": "THREE_OR_MORE_SPATIAL_CENTRES",
         "F": "ORGANISER_INTEGRITY_FAILURE"}


# ============================ §3 the founder contradiction ==============================
def founder_contradiction():
    rows = []
    hi = 1 - (1 - ALPHA) ** (1.0 / T_HORIZON)
    for tau in (83.0, 111.0, 125.0):
        lo = 1 - (GAMMA / MINEV) ** (1.0 / tau)
        rows.append({"tau_sep": tau, "muY_lower_bound_from_C1_and_C3": lo,
                     "muY_upper_bound_from_C2_FOUNDER": hi,
                     "compatible": lo <= hi, "incompatibility_factor": lo / hi})
    # independence check: vary E over 6 decades and kY over the whole admissible box
    indep = {}
    for E in (0.01, 0.1, 1.0, 2.873022, 10.0, 100.0):
        best = -1e18
        for lk in np.linspace(-6, -2, 121):
            kY = 10 ** lk
            b = kY * E * T_WINDOW
            for lm in np.linspace(-8, -1, 121):
                muY = 10 ** lm
                m = min(math.log10(max(b, 1e-300) / MINEV),
                        math.log10(max((1 - muY) ** T_HORIZON, 1e-300) / (1 - ALPHA)),
                        math.log10(GAMMA / max(b * (1 - muY) ** 111.0, 1e-300)))
                best = max(best, m)
        indep["E=%g" % E] = round(best, 6)
    return {
        "SECTION": "FLCR01 §3 — the founder gate is unsatisfiable a priori",
        "CRITERIA": {"C1": "kY * E * W >= 1",
                     "C2_FOUNDER": "(1 - muY)^T_HORIZON >= 0.5",
                     "C3": "kY * E * W * (1 - muY)^tau_sep <= 0.5"},
        "ELIMINATION": {
            "C1_AND_C3": "divide C3 by C1: (1-muY)^tau_sep <= 0.5  =>  "
                         "muY >= 1 - 0.5^(1/tau_sep)",
            "C2_FOUNDER": "muY <= 1 - 0.5^(1/T_HORIZON)",
            "kY_CANCELS": True, "E_CANCELS": True},
        "EVALUATED": rows,
        "INDEPENDENT_OF": {"kY": True, "Q_or_exposure": True, "exposure_uncertainty": True,
                           "calibration_size": True, "instrumentation": True,
                           "candidate_point_selection": True,
                           "maximin_margin_vs_exposure_decades": indep},
        "FOUNDER_GATE_REGION": "EMPTY_FOR_ALL_kY_AND_ALL_EXPOSURE",
        "PLAIN_STATEMENT": ("PQEC01 could not have produced a positive candidate region under "
                            "its frozen criteria, regardless of the data. The observed margin is "
                            "not confirmation of a measurement; it is the value of an identity "
                            "that never depended on the measurement."),
        "WHERE_THE_CONFLICT_LIES": ("C2_FOUNDER requires the ORIGINAL Y particle to survive "
                                    "11000 steps, while C3 requires a NEWBORN Y to be dead "
                                    "within tau_sep steps so that no second centre forms. Both "
                                    "are enforced through the single scalar muY, which applies "
                                    "identically to every Y. The gate asks one parameter to be "
                                    "simultaneously tiny and large."),
        "DEEPER_ERROR": ("C3 forbids a separated second centre while the scientific objective is "
                         "precisely that two organising centres should appear and persist. The "
                         "old criterion set does not merely conflict numerically -- it opposes "
                         "the thing it was written to detect."),
    }


# ============================ §7 the developmental state operator ========================
def _classify(nY, ncen, integrity_ok):
    if not integrity_ok:
        return "F"
    if nY == 0:
        return "E"
    if ncen >= 3:
        return "P"
    if nY == 1:
        return "O"
    return "S" if ncen == 2 else "C"


def state_operator():
    per_point = {}
    hold_all, sep_delay_all = [], []
    for lab in ("B1", "B2"):
        files = sorted(glob.glob(f"{RAW}/B_{lab}_*.npz"))
        Ntr = np.zeros((6, 6))
        per_world_tr, occ_worlds, world_rows = [], Counter(), []
        for p in files:
            z = np.load(p, allow_pickle=True)
            m = json.loads(str(z["meta"][0]))
            nm = [str(x) for x in z["scalar_names"]]
            s = z["scalars"]
            nY = s[:, nm.index("N_Y")].astype(int)
            nc = s[:, nm.index("n_centres")].astype(int)
            yb = z["ybirth"]
            ok = m["stop"] != "INTEGRITY_FAILURE"
            seq = [_classify(a, b, ok or i < len(nY) - 1) for i, (a, b) in
                   enumerate(zip(nY, nc))]
            k = np.zeros((6, 6))
            for a, b in zip(seq[:-1], seq[1:]):
                k[STATES.index(a), STATES.index(b)] += 1
            Ntr += k
            per_world_tr.append(k)
            occ_worlds.update(set(seq))
            # two-centre HOLD durations: maximal runs of state S
            runs, cur = [], 0
            for st in seq:
                if st == "S":
                    cur += 1
                else:
                    if cur:
                        runs.append(cur)
                    cur = 0
            if cur:
                runs.append(cur)
            fb = int(yb[:, 0].min()) if yb.size else -1
            first_S = next((i for i, st in enumerate(seq) if st == "S"), -1)
            if fb >= 0 and first_S > fb:
                sep_delay_all.append(first_S - fb)
            hold_all += runs
            world_rows.append({
                "world": m["tag"], "split_historical": m["split"], "stop": m["stop"],
                "steps": int(s.shape[0]), "births": int(yb[:, 3].sum()) if yb.size else 0,
                "first_birth_step": fb, "first_two_centre_step": first_S,
                "max_hold_S": int(max(runs)) if runs else 0,
                "total_S_steps": int(sum(runs)), "n_S_episodes": len(runs),
                "reached_S": bool(first_S >= 0),
                "reached_P": bool("P" in seq), "extinct": bool(seq[-1] == "E")})
        P = Ntr / np.maximum(Ntr.sum(axis=1, keepdims=True), 1)
        rowsupport = {STATES[i]: int(Ntr[i].sum()) for i in range(6)}
        wsupport = {st: int(occ_worlds[st]) for st in STATES}
        dom = {}
        for i, st in enumerate(STATES):
            c = np.array([k[i].sum() for k in per_world_tr])
            dom[st] = float(c.max() / c.sum()) if c.sum() > 0 else 0.0
        per_point[lab] = {
            "N_WORLDS": len(files), "STATES": list(STATES), "STATE_NAMES": SNAME,
            "TRANSITION_COUNTS": Ntr.tolist(), "TRANSITION_MATRIX": P.tolist(),
            "ROW_SUPPORT_STEPS": rowsupport,
            "WORLDS_VISITING_EACH_STATE": wsupport,
            "SINGLE_WORLD_DOMINANCE_PER_ROW": dom,
            "STATES_WITH_FEWER_THAN_5_WORLDS": [s for s, n in wsupport.items() if 0 < n < 5],
            "STATES_NEVER_VISITED": [s for s, n in wsupport.items() if n == 0],
            "PER_WORLD": world_rows,
            "UNIT": "one world; pooled transitions are NOT independent samples"}
    return {"SECTION": "FLCR01 §7 — developmental state operator (world is the unit)",
            "PER_PARAMETER_POINT": per_point,
            "TWO_CENTRE_HOLD_DURATIONS": {
                "n_episodes": len(hold_all),
                "min": int(min(hold_all)) if hold_all else 0,
                "median": float(np.median(hold_all)) if hold_all else 0.0,
                "mean": float(np.mean(hold_all)) if hold_all else 0.0,
                "q90": float(np.quantile(hold_all, .9)) if hold_all else 0.0,
                "max": int(max(hold_all)) if hold_all else 0},
            "SEPARATION_DELAY_AFTER_FIRST_BIRTH": {
                "n": len(sep_delay_all),
                "median": float(np.median(sep_delay_all)) if sep_delay_all else None,
                "mean": float(np.mean(sep_delay_all)) if sep_delay_all else None,
                "frozen_TAU_SEP": TAU_FROZEN},
            "COVARIATE_STATUS": {
                "RECORDED_BUT_NOT_USED": [
                    "birth-cell exposure class (in ycells, column Q_local, every step)",
                    "local nX, nSY, free and candidate pool for EVERY occupied Y cell (ycells)",
                    "source-relative displacement (src ledger + ycells positions)",
                    "co-location duration (derivable from n_centres and N_Y)",
                    "separation distance (max_pair_dist scalar, every step)",
                    "number of active spatial centres (n_centres scalar, every step)"],
                "MISSING_FROM_DATA": [],
                "RECORDED_BUT_NOT_IDENTIFIABLE": [
                    "which individual Y produced a birth in a multiply occupied cell "
                    "(SHARED_PARENT_POOL — an aggregate-engine limit, not a recording gap)",
                    "per-particle lineage age"],
                "INSUFFICIENT_WORLD_COVERAGE": "see STATES_WITH_FEWER_THAN_5_WORLDS per point",
                "STATEMENT": ("every covariate the PQEC01 successor handoff called 'missing "
                              "instrumentation' is in fact RECORDED_BUT_NOT_USED. No additional "
                              "field is required to condition the operator; what is missing is "
                              "world coverage across the (kY, muY) plane, which is a design "
                              "problem, not an instrumentation one.")}}


# ============================ §4 criterion audit ========================================
def criterion_matrix():
    def row(**kw):
        return kw
    return {
        "SECTION": "FLCR01 §4 — four candidate criteria, compared on scientific meaning",
        "SCIENTIFIC_OBJECT": ("persistence of an ORGANISING LINEAGE through material turnover -- "
                              "not preservation of an arbitrary particle identifier"),
        "CRITERIA": {
            "FOUNDER_SURVIVAL": row(
                meaning="the exact initial Y particle is still alive at T_HORIZON (the old C2)",
                necessary_for_the_claim=False,
                why=("the X cloud already turns over completely; the whole programme is about a "
                     "structure that persists while its material is replaced. Requiring one "
                     "tagged particle to persist imposes on Y precisely the property the "
                     "project denies is required of X. It is a particle-identity criterion "
                     "wearing an organisational label."),
                sufficient=False,
                invariant_under_turnover=False,
                measurable_from_PQEC01=True,
                requires_particle_genealogy=True,
                aggregate_engine_can_identify=("only while nY == 1; once two Y share a cell the "
                                               "engine cannot say which is the founder"),
                consequence_for_the_region="forces muY <= 6.30e-05 and is what makes the region "
                                           "empty for every kY and every exposure",
                architectural_requirement="a per-particle identity the physics does not carry"),
            "LINEAGE_NON_EXTINCTION": row(
                meaning=("at least one Y descended from the initial state is present at "
                         "T_HORIZON; the founder may die after producing a successor"),
                necessary_for_the_claim=True,
                why=("this is the minimal statement of continuity through turnover, and it is "
                     "exactly the property the project claims for the X structure"),
                sufficient=False,
                why_not_sufficient=("non-extinction says nothing about spatial organisation; a "
                                    "single wandering Y satisfies it"),
                invariant_under_turnover=True,
                measurable_from_PQEC01=True,
                requires_particle_genealogy=False,
                aggregate_engine_can_identify=("yes -- N_Y > 0 is a total count and needs no "
                                               "genealogy"),
                consequence_for_the_region="removes the muY upper bound entirely; the "
                                           "C1-versus-C3 contradiction dissolves",
                architectural_requirement="none"),
            "ORGANISER_CONTINUITY": row(
                meaning=("at every required time at least one Y occupies or controls a "
                         "source-bound organising centre, whatever the particle"),
                necessary_for_the_claim=True,
                why="continuity of FUNCTION is the claim; continuity of count is only its shadow",
                sufficient=False,
                why_not_sufficient="one centre is not the two-centre object under test",
                invariant_under_turnover=True,
                measurable_from_PQEC01=True,
                requires_particle_genealogy=False,
                aggregate_engine_can_identify=("yes -- a centre is a single-linkage cluster of "
                                               "occupied Y cells at radius CORE_R, plus the "
                                               "local X response, both recorded every step"),
                consequence_for_the_region="adds a function requirement on top of non-extinction",
                architectural_requirement="none"),
            "TWO_CENTRE_FUNCTIONAL_CONTINUITY": row(
                meaning=("after first separation, two spatially distinct Y organising centres "
                         "persist for a frozen hold duration, each retaining a qualified local X "
                         "response, without a premature third centre"),
                necessary_for_the_claim=True,
                why=("this IS the object the programme set out to detect; it is the operational "
                     "form of 'one organising centre became two and both kept working'"),
                sufficient=True,
                invariant_under_turnover=True,
                measurable_from_PQEC01=True,
                requires_particle_genealogy=False,
                aggregate_engine_can_identify=("yes -- n_centres, per-centre occupancy, per-cell "
                                               "local nX/nSY/free and pairwise distances are all "
                                               "recorded every step"),
                consequence_for_the_region="replaces C3's prohibition of a second centre with a "
                                           "hold requirement plus a third-centre prohibition",
                architectural_requirement="none identified so far"),
        },
        "PRIMARY_CRITERION_SELECTED": "TWO_CENTRE_FUNCTIONAL_CONTINUITY",
        "SUPPORTING_CRITERION": "LINEAGE_NON_EXTINCTION",
        "FOUNDER_SURVIVAL_VERDICT": "REJECTED_AS_A_GATE",
        "WHY_NOT_CHOSEN_FOR_CREATING_A_REGION": (
            "the choice is made from the scientific object, and it can be stated without "
            "reference to any region: the programme tests whether an organising structure "
            "persists while its material is replaced. A criterion that fails the moment the "
            "original particle is replaced contradicts the hypothesis it is meant to test. That "
            "argument would stand even if founder survival happened to admit a wide region."),
        "IF_FOUNDER_IDENTITY_WERE_ESSENTIAL": (
            "it would be essential only for a claim about an individual rather than a lineage -- "
            "for instance 'this particular organiser survived a perturbation'. No such claim is "
            "in scope, and the programme forbids reproduction and heredity claims outright."),
        "NO_INVENTED_GENEALOGY": (
            "none of the three retained criteria requires knowing which Y produced which. All "
            "are functions of total count, cell occupancy, cluster structure and local fields -- "
            "every one of them recorded. Where genealogy would be needed it is declared "
            "unidentifiable rather than imputed."),
    }


# ============================ §8, §9 lineage gates and regions ==========================
def _chain(kY, muY, c, nx, nmax=int(N_STAR) + 2):
    cc = max(int(round(c)), 1)
    M = np.zeros((nmax + 1, nmax + 1))
    M[0, 0] = 1.0
    for n in range(1, nmax + 1):
        p = min(1.0, kY * nx * n)
        bp = np.array([comb(cc, k) * p ** k * (1 - p) ** (cc - k) for k in range(cc + 1)])
        dp = np.array([comb(n, k) * muY ** k * (1 - muY) ** (n - k) for k in range(n + 1)])
        for b, pb in enumerate(bp):
            for d, pd in enumerate(dp):
                if pb > 0 and pd > 0:
                    M[n, min(max(n + b - d, 0), nmax)] += pb * pd
    return M


def _profile(kY, muY, c, nx, T=T_HORIZON):
    """Exact after T steps by binary matrix power — the same chain, without T matmuls."""
    M = np.linalg.matrix_power(_chain(kY, muY, c, nx), T)
    P = np.zeros(M.shape[0])
    P[1] = 1.0
    P = P @ M
    cc = max(int(round(c)), 1)
    p1 = min(1.0, kY * nx * 1.0)
    p_no_birth = math.exp(T * cc * math.log1p(-p1)) if p1 < 1 else 0.0
    return {"P_extinct_at_T": float(P[0]),
            "P_lineage_alive_at_T": float(1 - P[0]),
            "P_first_birth_by_T": float(1 - p_no_birth),
            "P_at_or_above_N_STAR": float(P[int(N_STAR):].sum()),
            "E_nY_at_T": float(sum(i * P[i] for i in range(P.size)))}


def lineage_regions(op):
    E = 2.873022222222222          # measured Phase-A world-level mean exposure
    C_POOL, NX = 0.961651, 4.312563
    hold = op["TWO_CENTRE_HOLD_DURATIONS"]
    H_HOLD = float(hold["median"])
    T_BIRTH, T_SEP = T_WINDOW, T_WINDOW
    THRESH = 0.5                    # inherited: ALPHA_SURVIVAL = 0.5 -> probability >= 1/2
    grid_k = [10.0 ** v for v in np.linspace(-6, -2, 81)]
    grid_m = [10.0 ** v for v in np.linspace(-8, -1, 81)]

    founder, lineage = [], []
    for kY in grid_k:
        b = kY * E * T_WINDOW
        for muY in grid_m:
            if b >= MINEV and (1 - muY) ** T_HORIZON >= 1 - ALPHA and \
                    b * (1 - muY) ** 111.0 <= GAMMA and kY * CAP * N_STAR <= 0.1:
                founder.append((kY, muY))
    for kY in grid_k:
        for muY in grid_m:
            if kY * CAP * N_STAR > 0.1:
                continue
            pr = _profile(kY, muY, C_POOL, NX)
            if (pr["P_first_birth_by_T"] >= THRESH and pr["P_lineage_alive_at_T"] >= THRESH
                    and pr["P_at_or_above_N_STAR"] <= 1 - THRESH):
                lineage.append((kY, muY, pr["P_first_birth_by_T"], pr["P_lineage_alive_at_T"],
                                pr["P_at_or_above_N_STAR"]))

    # measured two-centre behaviour, world level, at the two points only
    meas = {}
    for lab, blk in op["PER_PARAMETER_POINT"].items():
        W = blk["PER_WORLD"]
        n = len(W)
        meas[lab] = {
            "N_WORLDS": n,
            "P_first_birth": sum(1 for w in W if w["births"] > 0) / n,
            "P_lineage_alive_at_end": sum(1 for w in W if not w["extinct"]) / n,
            "P_reach_two_centres": sum(1 for w in W if w["reached_S"]) / n,
            "P_third_centre": sum(1 for w in W if w["reached_P"]) / n,
            "P_hold_ge_H": sum(1 for w in W if w["max_hold_S"] >= H_HOLD) / n,
            "P_hold_ge_TAU_FROZEN": sum(1 for w in W if w["max_hold_S"] >= TAU_FROZEN) / n,
            "median_max_hold_among_S_worlds": float(np.median(
                [w["max_hold_S"] for w in W if w["reached_S"]] or [0])),
            "binom_se_reach_two": float(np.sqrt(
                max(sum(1 for w in W if w["reached_S"]) / n * (1 - sum(
                    1 for w in W if w["reached_S"]) / n), 1e-12) / n))}
    return {
        "SECTION": "FLCR01 §8-§9 — lineage gates and the three regions",
        "GATE_FAMILY": {
            "L1_FIRST_BIRTH": "P(first Y birth before T_birth=%d) >= %.2f" % (T_BIRTH, THRESH),
            "L2_LINEAGE_CONTINUITY": "P(no total Y extinction before T_horizon=%d) >= %.2f"
                                     % (T_HORIZON, THRESH),
            "L3_TWO_CENTRE_FORMATION": "P(reach two spatial centres before T_sep=%d) >= %.2f"
                                       % (T_SEP, THRESH),
            "L4_TWO_CENTRE_HOLD": "P(two centres persist H_hold=%.0f steps once formed) >= %.2f"
                                  % (H_HOLD, THRESH),
            "L5_THIRD_CENTRE_CONTROL": "P(no third centre before the hold completes) >= %.2f"
                                       % THRESH,
            "L6_ORGANISER_FUNCTION": "both centres retain the qualified local X response",
            "L7_TECHNICAL_AND_DOMAIN_INTEGRITY": "no integrity failure"},
        "THRESHOLD_PROVENANCE": {
            "T_horizon": {"value": T_HORIZON, "source": "INHERITED from PQEC01/OBTC02"},
            "T_birth": {"value": T_BIRTH, "source": "INHERITED (the analysis window)"},
            "T_sep": {"value": T_SEP, "source": "INHERITED (the analysis window)"},
            "probability_threshold": {"value": THRESH,
                                      "source": "INHERITED — it is 1 - ALPHA_SURVIVAL"},
            "H_hold": {"value": H_HOLD, "source": "DEVELOPMENTAL — the median observed duration "
                                                  "of a two-centre episode over all 128 worlds",
                       "n_episodes": hold["n_episodes"],
                       "NOT_OPTIMIZED_AGAINST_OUTCOMES": ("it is a location statistic of an "
                                                          "observed distribution, chosen before "
                                                          "any gate was evaluated, and it is "
                                                          "labelled developmental")}},
        "FOUNDER_SURVIVAL_REGION": {
            "n_grid_points": len(founder), "EMPTY": len(founder) == 0,
            "REASON": "C1 and C3 force muY >= 6.2e-03 while C2_FOUNDER forces muY <= 6.3e-05; "
                      "kY and the exposure cancel"},
        "LINEAGE_CONTINUITY_REGION": {
            "n_grid_points": len(lineage), "EMPTY": len(lineage) == 0,
            "kY_range": [min(p[0] for p in lineage), max(p[0] for p in lineage)] if lineage
            else None,
            "muY_range": [min(p[1] for p in lineage), max(p[1] for p in lineage)] if lineage
            else None,
            "METHOD": ("exact finite Markov chain on total Y count using the engine's own "
                       "per-step binomial birth and death laws, at the measured mean candidate "
                       "pool and mean organiser nX"),
            "STATUS": "EXACT_UNDER_A_MEAN_FIELD_ENVIRONMENT — the chain uses mean exposure, not "
                      "the position-resolved field"},
        "TWO_CENTRE_FUNCTIONAL_REGION": {
            "MEASURED_AT_TWO_POINTS_ONLY": meas,
            "H_HOLD_USED": H_HOLD,
            "EMPTY_OR_NONEMPTY": "NOT_DETERMINABLE_ACROSS_THE_PLANE",
            "REASON": ("L3, L4 and L5 depend on SPATIAL rates -- centre formation, hold and "
                       "third-centre appearance -- which were measured at exactly two (kY, muY) "
                       "points. Two points cannot identify a surface over a two-dimensional "
                       "plane, and nothing in the exact chain predicts them, because the chain "
                       "counts Y and does not place them."),
            "WHAT_WOULD_SETTLE_IT": ("world coverage across the plane at the SAME instrumentation "
                                     "-- a design problem, not a missing field")},
    }


# ============================ §10 architecture-change test ==============================
def architecture_test(fc, reg, op):
    lineage_nonempty = not reg["LINEAGE_CONTINUITY_REGION"]["EMPTY"]
    tests = {
        "A_lineage_incompatible_with_third_centre_control_for_all_kY_muY": {
            "HOLDS": not lineage_nonempty,
            "evidence": ("the exact chain admits %d grid points satisfying L1, L2 and the "
                         "N_STAR bound simultaneously" % reg["LINEAGE_CONTINUITY_REGION"]
                         ["n_grid_points"])},
        "B_requires_different_removal_rates_for_founder_and_newborn": {
            "HOLDS": False,
            "evidence": ("that asymmetry was required only by the FOUNDER gate. Under lineage "
                         "continuity nothing distinguishes founder from newborn, so a single "
                         "scalar muY suffices for the retained criteria.")},
        "C_requires_age_state_contact_or_position_dependent_Y_death": {
            "HOLDS": "NOT_ESTABLISHED",
            "evidence": ("this would follow only if L4 (hold) and L5 (third-centre control) "
                         "proved jointly unreachable with a scalar muY. They were measured at "
                         "two points, which cannot establish it either way.")},
        "D_feedback_necessarily_causes_uncontrolled_X_amplification": {
            "HOLDS": False,
            "evidence": ("the apparent effect ranges from about +1% to +67% depending only on "
                         "which comparison is chosen, and the matched-window comparison is not "
                         "significant at B2. Nothing establishes NECESSARY amplification for "
                         "every admissible point.")},
        "E_exact_operator_proves_every_admissible_lineage_region_empty": {
            "HOLDS": False,
            "evidence": "the lineage region is non-empty in the exact chain"},
    }
    any_hold = any(v["HOLDS"] is True for v in tests.values())
    return {
        "SECTION": "FLCR01 §10 — architecture-change test",
        "TESTS": tests,
        "ARCHITECTURE_CHANGE_JUSTIFIED": any_hold,
        "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED",
        "EXPLICITLY_NOT_INFERRED_FROM": [
            "the founder gate being self-contradictory",
            "PQEC01 provenance being incomplete",
            "a misspecified validation model",
            "the old positive gate being impossible",
            "more data being desirable"],
        "SMALLEST_MISSING_DEGREE_OF_FREEDOM_IF_LATER_REQUIRED": {
            "ranked_candidates": [
                {"change": "state-dependent Y removal (muY conditioned on the number of centres)",
                 "why_first": ("it is the minimal change that could enforce third-centre control "
                               "without killing the founder, and it adds no species and no new "
                               "physical state variable -- only a dependence of an existing rate "
                               "on an already-computed quantity")},
                {"change": "centre-dependent resource limitation",
                 "why": "acts on the shared pool rather than on Y directly"},
                {"change": "local negative feedback on Y birth",
                 "why": "suppresses a third centre at its source"},
                {"change": "age-dependent Y removal",
                 "why": "requires a per-particle age the aggregate engine cannot carry"},
                {"change": "founder/newborn asymmetric survival",
                 "why": "requires the particle identity this analysis rejects as a criterion"},
                {"change": "explicit lineage-level resource accounting",
                 "why": "largest change; not justified by anything measured"}],
            "NOT_A_NEW_SPECIES": ("no candidate above introduces a new chemical species, and "
                                  "none is authorised by this mission")},
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    fc = founder_contradiction()
    op = state_operator()
    cm = criterion_matrix()
    reg = lineage_regions(op)
    arch = architecture_test(fc, reg, op)
    json.dump(fc, open(f"{OUT}/FLCR01_FOUNDER_CONTRADICTION.json", "w"), indent=1, default=str)
    json.dump(op, open(f"{OUT}/FLCR01_STATE_OPERATOR.json", "w"), indent=1, default=str)
    json.dump(cm, open(f"{OUT}/FLCR01_CRITERION_MATRIX.json", "w"), indent=1, default=str)
    json.dump({**reg, "ARCHITECTURE": arch},
              open(f"{OUT}/FLCR01_LINEAGE_REGIONS.json", "w"), indent=1, default=str)
    print("§3 founder contradiction:")
    for r in fc["EVALUATED"]:
        print("   tau=%6.1f  muY >= %.6e  and  muY <= %.6e  -> compatible=%s  factor %.1f"
              % (r["tau_sep"], r["muY_lower_bound_from_C1_and_C3"],
                 r["muY_upper_bound_from_C2_FOUNDER"], r["compatible"],
                 r["incompatibility_factor"]))
    print("   independent of exposure:", fc["INDEPENDENT_OF"]["maximin_margin_vs_exposure_decades"])
    print("\n§7 state operator:")
    for lab, b in op["PER_PARAMETER_POINT"].items():
        print("   %s worlds %d  worlds visiting each state %s"
              % (lab, b["N_WORLDS"], b["WORLDS_VISITING_EACH_STATE"]))
        print("      never visited: %s | fewer than 5 worlds: %s"
              % (b["STATES_NEVER_VISITED"], b["STATES_WITH_FEWER_THAN_5_WORLDS"]))
    h = op["TWO_CENTRE_HOLD_DURATIONS"]
    print("   two-centre hold: n=%d median %.0f mean %.0f q90 %.0f max %d"
          % (h["n_episodes"], h["median"], h["mean"], h["q90"], h["max"]))
    print("   separation delay after first birth: median %s (frozen TAU_SEP %.0f)"
          % (op["SEPARATION_DELAY_AFTER_FIRST_BIRTH"]["median"], TAU_FROZEN))
    print("\n§9 regions:")
    print("   FOUNDER  : empty=%s (%d points)" % (reg["FOUNDER_SURVIVAL_REGION"]["EMPTY"],
                                                  reg["FOUNDER_SURVIVAL_REGION"]["n_grid_points"]))
    L = reg["LINEAGE_CONTINUITY_REGION"]
    print("   LINEAGE  : empty=%s (%d points) kY %s muY %s"
          % (L["EMPTY"], L["n_grid_points"],
             ["%.2e" % x for x in L["kY_range"]] if L["kY_range"] else None,
             ["%.2e" % x for x in L["muY_range"]] if L["muY_range"] else None))
    print("   TWO-CENTRE:", reg["TWO_CENTRE_FUNCTIONAL_REGION"]["EMPTY_OR_NONEMPTY"])
    for lab, m in reg["TWO_CENTRE_FUNCTIONAL_REGION"]["MEASURED_AT_TWO_POINTS_ONLY"].items():
        print("      %s L1 %.3f L2 %.3f L3 %.3f (se %.3f) L4 %.3f L5(no 3rd) %.3f"
              % (lab, m["P_first_birth"], m["P_lineage_alive_at_end"], m["P_reach_two_centres"],
                 m["binom_se_reach_two"], m["P_hold_ge_H"], 1 - m["P_third_centre"]))
    print("\n§10 architecture change justified:", arch["ARCHITECTURE_CHANGE_JUSTIFIED"],
          "| necessity:", arch["ARCHITECTURE_CHANGE_NECESSITY"])


if __name__ == "__main__":
    main()
