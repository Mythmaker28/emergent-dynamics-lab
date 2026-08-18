"""FLCR01 §2 — the single retrospective correction of the PQEC01 record.

No history is rewritten. Every number is COMPUTED from the raw archives or from Git objects;
nothing is asserted. The pre-fix analyser is recovered from commit 7d97205 and re-run on the
identical raw data, so the chronology is reproducible rather than argued.
"""
from __future__ import annotations
import glob, hashlib, json, os, subprocess, sys
from collections import Counter
import numpy as np

REPO = "/home/claude/edl"
PQ = f"{REPO}/PQEC01/out"
OUT = f"{REPO}/FLCR01/out"
RAW = "/home/claude/PQEC01/raw"
PRE = f"{REPO}/FLCR01/prefix_outputs"   # committed, so the addendum is regenerable
BURN_IN, T_HORIZON = 2000, 11000
C3, C4 = "7d97205818ae723683280053512a27f1872db375", "d61e9a34367b42bd7534647ad9802a9892639f31"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def git(*a):
    return subprocess.run(("git",) + a, cwd=REPO, capture_output=True, text=True).stdout.strip()


# ------------------------------------------------------------------ A. provenance
def provenance():
    blob = lambda rev, p: subprocess.run(("git", "show", "%s:%s" % (rev, p)), cwd=REPO,
                                         capture_output=True).stdout
    freeze_files = git("show", "--name-only", "--format=", "0bba579").split()
    c1_code = git("ls-tree", "--name-only", "0c8ed48", "PQEC01/code/").split()
    exec_inputs = ["PQEC01/code/pqec01_run.py", "PQEC01/code/pqec01_observer.py",
                   "PQEC01/out/PQEC01_MASTER_FREEZE.json"]
    engine = ["/home/claude/ORR01/code/kinetics.py", "/home/claude/ORR01/code/observe.py",
              "/home/claude/ORR01/code/lawspec_v2.py", "/home/claude/OBTC02/code/engine_obtc.py",
              "/home/claude/OBTC02/code/protocol_obtc02.py",
              "/home/claude/OBTC02/code/obtc02_protocol.yaml"]
    h = hashlib.sha256()
    parts = []
    for p in exec_inputs:
        b = blob(C3, p)
        h.update(p.encode()); h.update(b)
        parts.append({"path": p, "source": "git blob at C3",
                      "sha256": hashlib.sha256(b).hexdigest()})
    for p in engine:
        b = open(p, "rb").read()
        h.update(os.path.basename(p).encode()); h.update(b)
        parts.append({"path": p, "source": "working tree (frozen engine, unchanged)",
                      "sha256": hashlib.sha256(b).hexdigest()})
    man = blob(C3, "PQEC01/out/PQEC01_RAW_MANIFEST.json")
    h.update(b"RAW_MANIFEST"); h.update(man)
    parts.append({"path": "PQEC01/out/PQEC01_RAW_MANIFEST.json", "source": "git blob at C3",
                  "sha256": hashlib.sha256(man).hexdigest()})

    pre = json.load(open(f"{PRE}/PQEC01_INTERNAL_VALIDATION.json"))
    post = json.load(open(f"{PQ}/PQEC01_INTERNAL_VALIDATION.json"))
    side = {}
    for lab in pre:
        side[lab] = {t: {"PRE_FIX": {"z": pre[lab][t]["z"], "PASS": pre[lab][t]["PASS"]},
                         "POST_FIX": {"z": post[lab][t]["z"], "PASS": post[lab][t]["PASS"]},
                         "CHANGED": pre[lab][t]["PASS"] != post[lab][t]["PASS"]}
                    for t in ("TEST_1_first_birth", "TEST_2_two_plus_Y_step_fraction",
                              "TEST_3_founder_survival")}
        side[lab]["ALL_PASS"] = {"PRE_FIX": pre[lab]["ALL_PASS"],
                                 "POST_FIX": post[lab]["ALL_PASS"]}
    dpre = json.load(open(f"{PRE}/PQEC01_FINAL_DISPOSITION.json"))
    dpost = json.load(open(f"{PQ}/PQEC01_FINAL_DISPOSITION.json"))
    return {
        "METHODS_HASH_SCOPE": {
            "COVERED": sorted(os.path.basename(x) for x in c1_code) + ["pqec01_freeze.py"],
            "NOT_COVERED": ["pqec01_run.py (the runner)", "pqec01_analyse.py (the analyser)",
                            "pqec01_manifest.py", "pqec01_repair.py"],
            "STATEMENT": ("PQEC01_METHODS_HASH covered the DESIGN and the OBSERVER code only. "
                          "The runner was NOT included in the pre-run methods hash, and neither "
                          "was the analyser. Any reading of that hash as binding the whole "
                          "method is withdrawn."),
            "FREEZE_COMMIT_CONTENTS": freeze_files},
        "RETROSPECTIVE_EXECUTION_HASH": {
            "VALUE": h.hexdigest(),
            "INPUTS": parts,
            "WHAT_IT_PROVES": ("that these exact bytes are what the delivery contains today"),
            "WHAT_IT_DOES_NOT_PROVE": ("it is computed AFTER the runs. It cannot establish that "
                                       "the runner was fixed before the first start. Only the "
                                       "Git history can, and it shows the runner first appearing "
                                       "in C3, i.e. in the same commit as the outputs it "
                                       "produced -- not before them.")},
        "CHRONOLOGY": {
            "C2_freeze_alone": {"commit": "0bba579f46895248364f3c74cd3c0e798c26eb4a",
                                "date": git("log", "-1", "--format=%ad", "--date=iso",
                                            "0bba579")},
            "C3_runner_and_all_outputs": {"commit": C3,
                                          "date": git("log", "-1", "--format=%ad", "--date=iso",
                                                      C3)},
            "C4_analyser_fixes": {"commit": C4,
                                  "date": git("log", "-1", "--format=%ad", "--date=iso", C4)},
            "STATEMENT": ("a complete analysis run, INCLUDING PQEC01_INTERNAL_VALIDATION.json, "
                          "existed before the two analysis corrections were made. The operator "
                          "therefore saw validation output before editing analysis code."),
            "REPRODUCIBILITY": ("the pre-fix analyser was recovered from commit %s and re-run on "
                                "the identical 128 raw archives; the pre-fix outputs below are "
                                "regenerated, not remembered." % C3[:7]),
            "PRE_FIX_ANALYSER_SHA256": sha(f"{REPO}/FLCR01/code/pqec01_analyse_PREFIX.py"),
            "PRE_FIX_ANALYSER_AND_OUTPUTS_ARE_COMMITTED": (
                "the analyser recovered from commit 7d97205 and the outputs it produced are "
                "both committed under FLCR01/, so this addendum regenerates from the repository "
                "alone and depends on no scratch directory"),
            "POST_FIX_ANALYSER_SHA256": sha(f"{REPO}/PQEC01/code/pqec01_analyse.py")},
        "PRE_FIX_VS_POST_FIX_VALIDATION": side,
        "THE_B1_TEST_CHANGE": {
            "test": "B1 TEST_2_two_plus_Y_step_fraction",
            "before": {"z": pre["B1"]["TEST_2_two_plus_Y_step_fraction"]["z"],
                       "verdict": "FAIL"},
            "after": {"z": post["B1"]["TEST_2_two_plus_Y_step_fraction"]["z"],
                      "verdict": "PASS"},
            "ASSESSMENT": ("a test moved from FAIL to PASS after its failure was visible. That "
                           "is the shape of a post-hoc rescue. The defence -- that the fix "
                           "restores a rule the freeze states verbatim (the unit is the world; "
                           "frame pseudoreplication is forbidden) -- is a defence, not a proof.")},
        "DISPOSITION_UNCHANGED": {
            "PRE_FIX": dpre["CANDIDATE_DISPOSITION"], "POST_FIX": dpost["CANDIDATE_DISPOSITION"],
            "IDENTICAL": dpre["CANDIDATE_DISPOSITION"] == dpost["CANDIDATE_DISPOSITION"],
            "gates_passed_pre": sum(1 for v in dpre["DECISION_GATES"].values() if v),
            "gates_passed_post": sum(1 for v in dpost["DECISION_GATES"].values() if v)},
    }


# ------------------------------------------------------------------ B. counts from raw
def counts():
    tot = Counter()
    disc = Counter()
    worlds = 0
    for p in sorted(glob.glob(f"{RAW}/B_*.npz")):
        z = np.load(p, allow_pickle=True)
        m = json.loads(str(z["meta"][0]))
        nm = [str(x) for x in z["scalar_names"]]
        s = z["scalars"]
        nY = s[:, nm.index("N_Y")].astype(int)
        nc = s[:, nm.index("n_centres")].astype(int)
        yb = z["ybirth"]
        worlds += 1
        colo = int(((nY >= 2) & (nc == 1)).sum())
        sep2 = int((nc == 2).sum())          # state S: EXACTLY two spatial centres
        sep_ge = int((nc >= 2).sum())        # two OR MORE centres (includes state P)
        sep = sep2
        tot["worlds"] += 1
        tot["births"] += int(yb[:, 3].sum()) if yb.size else 0
        tot["colo_one_centre"] += colo
        tot["two_centre_steps"] += sep2
        tot["two_or_more_centre_steps"] += sep_ge
        tot["worlds_two_centres"] += int(sep_ge > 0)
        if m["split"] == "DISCOVERY":
            disc["colo"] += colo
            disc["sep"] += sep2
            disc["sep_ge"] += sep_ge
    return {
        "VERIFIED_FROM_RAW_ARCHIVES": True,
        "TOTAL_PHASE_B_WORLDS": tot["worlds"],
        "TOTAL_Y_BIRTHS": tot["births"],
        "WORLDS_REACHING_TWO_CENTRES": tot["worlds_two_centres"],
        "DISCOVERY_TWO_Y_COLOCATED_STEPS": disc["colo"],
        "DISCOVERY_TWO_Y_SEPARATED_STEPS": disc["sep"],
        "ALL_WORLD_COLOCATED_ONE_CENTRE_STEPS": tot["colo_one_centre"],
        "ALL_WORLD_TWO_Y_SEPARATED_STEPS": tot["two_centre_steps"],
        "DEFINITIONS": {
            "TWO_Y_SEPARATED (state S)": "n_centres == 2 exactly",
            "two_or_more_centres": "n_centres >= 2, which also counts state P steps",
            "DISCOVERY_two_or_more_centre_steps": disc["sep_ge"],
            "ALL_WORLD_two_or_more_centre_steps": tot["two_or_more_centre_steps"],
            "NOTE": ("the two differ by the steps spent in three-or-more centres. Reporting "
                     "n_centres >= 2 as 'separated' silently folds state P into state S; the "
                     "state-S figures above use n_centres == 2 exactly.")},
        "WITHDRAWN_FIGURE": {
            "value": 16474,
            "where": "an interim progress message reported 16474 co-located steps",
            "correct_value": tot["colo_one_centre"],
            "STATEMENT": ("16474 is unsupported and is withdrawn. It appears to have been formed "
                          "by mixing a discovery-only separated-state count into an all-world "
                          "co-location count. The correct all-world co-located figure is %d and "
                          "the correct discovery-only co-located figure is %d."
                          % (tot["colo_one_centre"], disc["colo"]))},
        "DENOMINATORS_ARE_EXPLICIT": ("every count above names whether it is over all 88 Phase-B "
                                      "worlds or over the discovery subset only"),
    }


# ------------------------------------------------------------------ C. data flow
def data_flow():
    reg_src = open(f"{REPO}/PQEC01/code/pqec01_analyse.py").read()
    uses_all_A = "files = sorted(glob.glob(f\"{RAW}/A_*.npz\"))" in reg_src
    reg = json.load(open(f"{PQ}/PQEC01_CANDIDATE_REGION.json"))
    return {
        "PHASE_A_SPLIT_NOT_RESPECTED": {
            "FACT": uses_all_A,
            "STATEMENT": ("phase_a() globs every A_*.npz and the region's exposure lower "
                          "confidence bound is computed over ALL 40 Phase-A worlds. The frozen "
                          "discovery/validation split (31/9) was never applied to Phase A."),
            "phase_A_worlds_used_in_region": reg["MEASURED_INPUTS"]["phase_A_worlds"]},
        "PHASE_B_VALIDATION_ENTERED_THE_REGION": {
            "FACT": True,
            "STATEMENT": ("the region's separation statistics -- worlds reaching two centres, "
                          "the median separation delay tau used as a criterion input -- were "
                          "pooled over all 88 Phase-B worlds, validation included."),
            "phase_B_worlds_used_in_region": reg["MEASURED_INPUTS"]["phase_B_worlds"]},
        "HARDCODED_LITERALS_WITHDRAWN": [
            {"key": "NO_REFIT_AFTER_VIEWING_VALIDATION", "was": True,
             "now": "WITHDRAWN — it is contradicted by the reproduced chronology above"},
            {"key": "NO_OUTCOME_DRIVEN_REPLACEMENT", "was": True,
             "now": "RECOMPUTED from the run ledger and the manifest (see COMPUTED_GATES)"},
            {"key": "NO_FRAME_PSEUDOREPLICATION", "was": True,
             "now": "WITHDRAWN as a literal; the pre-fix analyser demonstrably violated it"},
            {"key": "FEEDBACK_CONTROLLED_OR_EXPLICITLY_MODELLED", "was": True,
             "now": "already flipped to False in the PQEC01 repair round"}],
        "ALL_128_WORLDS_RELABELLED": {
            "PQEC01_RAW_EXPERIMENT_STATUS": "VALID_DEVELOPMENTAL_CALIBRATION_DATA",
            "PQEC01_PROSPECTIVE_CONFIRMATORY_STATUS": "NOT_ESTABLISHED",
            "PQEC01_OBSERVER_PHYSICS_STATUS": "INERTNESS_CONFIRMED",
            "PQEC01_DESCENDANT_DATA_STATUS": "REAL_AND_EVENT_ALIGNED",
            "PQEC01_OPERATOR_IDENTIFICATION_STATUS": "NOT_CONFIRMED",
            "STATEMENT": ("all 128 worlds are POST_OUTCOME_DEVELOPMENT_DATA from this point on. "
                          "No untouched holdout is reconstructed; the historical "
                          "DISCOVERY/VALIDATION labels are retained only as a descriptive "
                          "stability diagnostic and are never again called held-out.")},
    }


# ------------------------------------------------------------------ D. firewall
def firewall():
    led = [json.loads(l) for l in open(f"{PQ}/PQEC01_RUN_LEDGER.jsonl")]
    man = json.load(open(f"{PQ}/PQEC01_RAW_MANIFEST.json"))
    by = {r["seed"]: r for r in man["ARCHIVES"]}
    stops, sizes = [], []
    for p in sorted(glob.glob(f"{RAW}/B_*.npz")):
        z = np.load(p, allow_pickle=True)
        m = json.loads(str(z["meta"][0]))
        stops.append(m["stop"])
        sizes.append((os.path.getsize(p), m["steps_recorded"], m["stop"]))
    ended_early = [s for s in sizes if s[2] != "HORIZON"]
    full = [s for s in sizes if s[2] == "HORIZON"]
    corr = float(np.corrcoef([s[0] for s in sizes], [s[1] for s in sizes])[0, 1])
    return {
        "LEAK_ACKNOWLEDGED": True,
        "STATEMENT": ("file size, runtime and steps_recorded are all monotone in how long a "
                      "world ran, and a world's run length IS its stop outcome. These three "
                      "quantities were visible in the live run log, so outcome-dependent stop "
                      "time leaked through the firewall during execution."),
        "EVIDENCE": {"corr_bytes_vs_steps_recorded": corr,
                     "median_bytes_early_stop": float(np.median([s[0] for s in ended_early]))
                     if ended_early else None,
                     "median_bytes_full_horizon": float(np.median([s[0] for s in full])),
                     "n_early": len(ended_early), "n_full": len(full)},
        "WHY_IT_DID_NOT_CAUSE_AN_ADAPTIVE_CHANGE": {
            "no_world_was_replaced": len(led) == len(set(r["seed"] for r in led)) == 128,
            "no_reserve_seed_used": all(r["seed"] in by for r in led),
            "all_128_frozen_starts_executed_exactly_once":
                sorted(r["seed"] for r in led) == sorted(by),
            "STATEMENT": ("the leak is real but inert: the schedule was fixed by the freeze, "
                          "every frozen seed ran exactly once, no reserve was drawn and no world "
                          "was replaced or re-run. Nothing in the execution could have adapted "
                          "to what leaked.")},
        "SUCCESSOR_REQUIREMENT": ("a firewall must not expose any variable monotone in run "
                                  "length. Report only a completion flag and a checksum.")}


# ------------------------------------------------------------------ E. feedback, four ways
def feedback():
    A = []
    for p in sorted(glob.glob(f"{RAW}/A_*.npz")):
        z = np.load(p, allow_pickle=True)
        nm = [str(x) for x in z["scalar_names"]]
        s = z["scalars"]
        A.append({"nX": s[:, nm.index("N_X")], "nSY": s[:, nm.index("mean_nSY")],
                  "free": s[:, nm.index("mean_free")], "n": s.shape[0]})
    B = {}
    for lab in ("B1", "B2"):
        rows = []
        for p in sorted(glob.glob(f"{RAW}/B_{lab}_*.npz")):
            z = np.load(p, allow_pickle=True)
            m = json.loads(str(z["meta"][0]))
            nm = [str(x) for x in z["scalar_names"]]
            s = z["scalars"]
            yb = z["ybirth"]
            rows.append({"nX": s[:, nm.index("N_X")], "nSY": s[:, nm.index("mean_nSY")],
                         "n": s.shape[0], "stop": m["stop"],
                         "births": int(yb[:, 3].sum()) if yb.size else 0,
                         "max_centres": int(s[:, nm.index("n_centres")].max())})
        B[lab] = rows

    def cmp(a_vals, b_vals, label):
        a, b = np.array(a_vals), np.array(b_vals)
        if a.size < 2 or b.size < 2:
            return {"comparison": label, "n_A": int(a.size), "n_B": int(b.size),
                    "INSUFFICIENT": True}
        se = float(np.sqrt(a.var(ddof=1) / a.size + b.var(ddof=1) / b.size))
        return {"comparison": label, "n_A": int(a.size), "n_B": int(b.size),
                "A_mean": float(a.mean()), "B_mean": float(b.mean()),
                "delta": float(b.mean() - a.mean()),
                "relative_delta": float((b.mean() - a.mean()) / a.mean()),
                "se": se, "z": float((b.mean() - a.mean()) / se) if se > 0 else 0.0,
                "significant_at_2se": bool(abs(b.mean() - a.mean()) > 2 * se)}

    out = {}
    for lab, rows in B.items():
        wA_full = [w["nX"][BURN_IN:].mean() for w in A]
        res = {}
        res["pooled"] = cmp(wA_full, [w["nX"][BURN_IN:w["n"]].mean() for w in rows
                                      if w["n"] > BURN_IN], "pooled, all Phase-B worlds")
        res["birth_worlds"] = cmp(wA_full, [w["nX"][BURN_IN:w["n"]].mean() for w in rows
                                            if w["births"] > 0 and w["n"] > BURN_IN],
                                  "stratified: worlds with >= 1 Y birth")
        res["no_birth_worlds"] = cmp(wA_full, [w["nX"][BURN_IN:w["n"]].mean() for w in rows
                                               if w["births"] == 0 and w["n"] > BURN_IN],
                                     "stratified: worlds with no Y birth")
        res["horizon_matched"] = cmp(wA_full, [w["nX"][BURN_IN:w["n"]].mean() for w in rows
                                               if w["stop"] == "HORIZON"],
                                     "only Phase-B worlds that ran the full horizon")
        # Matched time window. Taking the MINIMUM steps_recorded across worlds collapses to a
        # single step whenever one world dies early (B1's shortest world ran 270 steps), which
        # is not a comparison at all. A FIXED window is used instead, with the survivorship
        # stated explicitly rather than hidden.
        lo, hi = BURN_IN, BURN_IN + 2000
        inc = [w for w in rows if w["n"] >= hi]
        res["matched_time_window"] = cmp([w["nX"][lo:hi].mean() for w in A],
                                         [w["nX"][lo:hi].mean() for w in inc],
                                         "fixed identical step window [%d, %d)" % (lo, hi))
        res["matched_window_bounds"] = [lo, hi]
        res["matched_window_survivorship"] = {
            "phase_B_worlds_covering_the_window": len(inc), "of": len(rows),
            "excluded_because_they_stopped_earlier": len(rows) - len(inc),
            "WARNING": ("this comparison is itself survivorship-biased: only worlds that lived "
                        "past step %d can contribute, and living that long is an outcome. It "
                        "removes the unequal-window confound and introduces a selection one; it "
                        "is reported as a bound on the confound, not as a clean estimate."
                        % hi)}
        naive_m = min([w["n"] for w in rows] + [w["n"] for w in A])
        res["naive_min_window_rejected"] = {
            "window_would_be": [min(BURN_IN, max(naive_m - 1, 0)), naive_m],
            "width": max(naive_m - min(BURN_IN, max(naive_m - 1, 0)), 0),
            "REJECTED_BECAUSE": ("the shortest world sets the window; at B1 this gives a width "
                                 "of one step, which cannot support any comparison")}
        res["nSY_birth_worlds"] = cmp([w["nSY"][BURN_IN:].mean() for w in A],
                                      [w["nSY"][BURN_IN:w["n"]].mean() for w in rows
                                       if w["births"] > 0 and w["n"] > BURN_IN],
                                      "nSY, worlds with >= 1 Y birth")
        out[lab] = res
    return {
        "WITHDRAWN_CLAIM": {
            "text": "feedback not significant",
            "STATUS": "WITHDRAWN",
            "WHY": ("the published pooled comparison is confounded four ways at once: it "
                    "conditions on nothing while the effect exists only where a birth occurred; "
                    "worlds stop at outcome-dependent times; the analysis windows are therefore "
                    "unequal; and the number of active X sources is itself the mechanism under "
                    "test.")},
        "FOUR_COMPARISONS": out,
        "CAUSAL_WARNING": ("NONE of these comparisons identifies a causal effect. Whether a "
                           "birth occurred is not randomised -- it is itself an outcome of the "
                           "same exposure that drives X production, so birth-worlds are selected "
                           "for high exposure. Stopping is outcome-dependent. PQEC01 cannot "
                           "estimate this feedback cleanly and no causal number is claimed."),
        "PRESERVED_DEVELOPMENTAL_CLUE": ("Y birth, and the appearance of multiple Y centres, may "
                                         "substantially increase X production. The mechanism is "
                                         "architecturally plausible: kX = 1.0 makes p_X = 1 "
                                         "wherever nX*nY >= 1, so a second Y at a different cell "
                                         "adds a saturated X source rather than competing for "
                                         "the first. This is a clue for the next design, not a "
                                         "measured effect."),
    }


# ------------------------------------------------------------------ F. operator uncertainty
def operator_uncertainty():
    QMAX = 40
    per_world, occ_worlds = [], Counter()
    for p in sorted(glob.glob(f"{RAW}/A_*.npz")):
        z = np.load(p, allow_pickle=True)
        yc = z["ycells"]
        q = np.clip(np.array([r[8] for r in yc if r[0] >= BURN_IN], int), 0, QMAX)
        k = np.zeros((QMAX + 1, QMAX + 1))
        if q.size > 1:
            np.add.at(k, (q[:-1], q[1:]), 1.0)
        per_world.append(k)
        for st in set(q.tolist()):
            occ_worlds[int(st)] += 1
    K = np.stack(per_world)
    tot = K.sum(axis=0)
    rows = tot.sum(axis=1)
    # world-level uncertainty on P(stay at 0): per-world estimate, then between-world sd
    p00 = np.array([k[0, 0] / k[0].sum() for k in K if k[0].sum() > 0])
    contrib = K[:, 0, :].sum(axis=1)
    dom = float(contrib.max() / contrib.sum()) if contrib.sum() > 0 else 0.0
    states_with_worlds = {int(s): int(n) for s, n in sorted(occ_worlds.items())}
    return {
        "UNIT": "one world; the pooled transition table is NOT a sample of independent draws",
        "N_WORLDS": int(K.shape[0]),
        "P_STAY_AT_ZERO": {"world_level_mean": float(p00.mean()),
                           "world_level_sd": float(p00.std(ddof=1)),
                           "world_level_se": float(p00.std(ddof=1) / np.sqrt(p00.size)),
                           "n_worlds_contributing": int(p00.size),
                           "pooled_value_previously_reported": 0.8208,
                           "NOTE": ("the pooled figure was published without any uncertainty. "
                                    "Its world-level standard error is given here.")},
        "WORLDS_VISITING_EACH_EXPOSURE_STATE": states_with_worlds,
        "STATES_VISITED_BY_FEWER_THAN_5_WORLDS":
            [s for s, n in states_with_worlds.items() if n < 5],
        "SINGLE_WORLD_DOMINANCE_ON_ROW_ZERO": dom,
        "ROW_STOCHASTICITY_WITHDRAWN_AS_A_GATE": (
            "a row-normalised matrix is row-stochastic by construction. Using "
            "`row_stochastic == True` as evidence of identification was tautological and is "
            "withdrawn as a gate."),
        "IDENTIFICATION_CONSEQUENCE": ("with %d of %d exposure states visited by fewer than 5 "
                                       "independent worlds, the upper tail of the kernel is not "
                                       "estimated at world level at all."
                                       % (len([s for s, n in states_with_worlds.items() if n < 5]),
                                          len(states_with_worlds))),
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    rec = {"SECTION": "PQEC01 review correction addendum (issued by FLCR01)",
           "NO_HISTORY_REWRITTEN": True,
           "PQEC01_TIP_CORRECTED": "80735ad5e9775db051954ca4d05e258ee4fdf36a",
           "A_PROVENANCE": provenance(), "B_COUNTS": counts(), "C_DATA_FLOW": data_flow(),
           "D_FIREWALL": firewall(), "E_FEEDBACK": feedback(),
           "F_OPERATOR_UNCERTAINTY": operator_uncertainty()}
    json.dump(rec, open(f"{OUT}/PQEC01_REVIEW_CORRECTION_ADDENDUM.json", "w"), indent=1,
              default=str)
    b, f = rec["B_COUNTS"], rec["D_FIREWALL"]
    print("counts verified from raw:", {k: b[k] for k in
          ("TOTAL_PHASE_B_WORLDS", "TOTAL_Y_BIRTHS", "WORLDS_REACHING_TWO_CENTRES",
           "DISCOVERY_TWO_Y_COLOCATED_STEPS", "DISCOVERY_TWO_Y_SEPARATED_STEPS",
           "ALL_WORLD_COLOCATED_ONE_CENTRE_STEPS", "ALL_WORLD_TWO_Y_SEPARATED_STEPS")})
    print("firewall leak corr(bytes, steps) = %.4f; adaptive change: %s"
          % (f["EVIDENCE"]["corr_bytes_vs_steps_recorded"],
             not f["WHY_IT_DID_NOT_CAUSE_AN_ADAPTIVE_CHANGE"]
             ["all_128_frozen_starts_executed_exactly_once"]))
    for lab, r in rec["E_FEEDBACK"]["FOUR_COMPARISONS"].items():
        for k in ("pooled", "birth_worlds", "no_birth_worlds", "horizon_matched",
                  "matched_time_window"):
            v = r[k]
            if v.get("INSUFFICIENT"):
                print("  %s %-20s INSUFFICIENT" % (lab, k)); continue
            print("  %s %-20s n=%2d  delta %+8.3f (%+6.1f%%)  z %+6.2f  sig %s"
                  % (lab, k, v["n_B"], v["delta"], 100 * v["relative_delta"], v["z"],
                     v["significant_at_2se"]))
    u = rec["F_OPERATOR_UNCERTAINTY"]
    print("kernel P(stay 0) world-level %.4f +- %.4f (se %.4f, pooled was 0.8208)"
          % (u["P_STAY_AT_ZERO"]["world_level_mean"], u["P_STAY_AT_ZERO"]["world_level_sd"],
             u["P_STAY_AT_ZERO"]["world_level_se"]))
    print("exposure states visited by <5 worlds:", u["STATES_VISITED_BY_FEWER_THAN_5_WORLDS"])


if __name__ == "__main__":
    main()
