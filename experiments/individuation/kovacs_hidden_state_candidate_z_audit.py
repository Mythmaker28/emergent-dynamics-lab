"""KOVACS-HIDDEN-STATE-00 Phase-0 candidate-Z audit (already-open DEV data only).

Reads the frozen COUNTERFACTUAL-HISTORY-CORE-00 DEV results (worlds 57001-57024,
17 complete blocks) and mechanically characterises candidate macro-observables Z
for the Kovacs match. It computes, per candidate: interpretability, whether the
readout is tracker-dependent, the frozen dose contrast (history controllability),
and — for the leading mass candidate — how much of the *other* observables' history
variation SURVIVES a match on that candidate (non-collinearity → hidden DOF).

No engine is initialised; no new seed; no outcome is selected. This is a read-only
audit of already-open DEV data, used to SELECT (not tune) one primary Z on
mechanical criteria before any response is inspected.
"""
import json, math, statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DEV = REPO / "docs" / "individuation" / "COUNTERFACTUAL_HISTORY_CORE_00_DEV_RESULTS.json"
OUT = REPO / "docs" / "individuation" / "KOVACS_HIDDEN_STATE_00_CANDIDATE_Z_AUDIT.json"

HIST = ["H_L_EARLY", "H_L_LATE", "H_H_EARLY", "H_H_LATE"]
# candidate -> (first_stage key, interpretable, tracker_dependent_endpoint, note)
CANDS = {
    "body_mass":      ("body_mass",      True,  True,  "total rho over bijectively-tracked focal body"),
    "core_rho_mass":  ("core_rho_mass",  True,  False, "rho over frozen radius-10 checkpoint-centred core mask"),
    "body_size":      ("body_size",      True,  True,  "occupied cell count (area); integer, coarse crossing"),
    "body_rg":        ("body_rg",        True,  True,  "radius of gyration (shape/spread), not a conserved amount"),
    "mplus_mean":     ("mplus_mean",     False, True,  "internal uptake-memory readout; this IS a hidden coordinate"),
    "mminus_mean":    ("mminus_mean",    False, True,  "internal order-memory readout; this IS a hidden coordinate"),
    "world_rho_mass": ("world_rho_mass", True,  False, "whole-grid mass; environment-level, not the individual"),
    "world_up_ref":   ("world_up_ref",   True,  False, "mean uptake over alive cells; environment driver, not organism macrostate"),
}

def corr(xs, ys):
    n = len(xs)
    if n < 3: return float("nan")
    mx = sum(xs) / n; my = sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs); syy = sum((y - my) ** 2 for y in ys)
    return sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else float("nan")

def main():
    d = json.load(open(DEV))
    W = d["worlds"]
    complete = [w for w in W if w.get("complete_block")]
    # per (seed, hist) absolute candidate values
    table = {}
    for w in complete:
        for h in HIST:
            b = w["branches"].get(h)
            if not b: continue
            fs = b["probe"]["first_stage"]
            table[(w["seed"], h)] = {c: fs.get(key) for c, (key, *_2) in CANDS.items()}
    seeds = sorted({s for (s, h) in table})

    # frozen dose contrast per candidate (from first_stage_contrasts), averaged over worlds
    dose = {c: [] for c in CANDS}
    for w in complete:
        fsc = w.get("first_stage_contrasts", {})
        for c, (key, *_2) in CANDS.items():
            if key in fsc and isinstance(fsc[key], dict) and isinstance(fsc[key].get("dose"), (int, float)):
                dose[c].append(fsc[key]["dose"])

    def summ(vals):
        vals = [v for v in vals if isinstance(v, (int, float))]
        if not vals: return None
        return {"n": len(vals), "mean": round(st.mean(vals), 6),
                "abs_mean": round(st.mean(abs(v) for v in vals), 6)}

    # achievable per-world range (span) of each candidate across the 4 histories
    spans = {c: [] for c in CANDS}
    absvals = {c: [] for c in CANDS}
    for s in seeds:
        for c in CANDS:
            vs = [table[(s, h)][c] for h in HIST if (s, h) in table and isinstance(table[(s, h)][c], (int, float))]
            if len(vs) == 4:
                spans[c].append(max(vs) - min(vs)); absvals[c] += vs

    # NON-COLLINEARITY: within-world-centre every candidate, then for the leading
    # mass candidate compute how much of each OTHER candidate's history variation
    # survives at fixed body_mass (residual SD after linear removal of mass).
    centred = {c: [] for c in CANDS}
    mass_c = []
    for s in seeds:
        grp = {c: [table[(s, h)][c] for h in HIST if (s, h) in table] for c in CANDS}
        if not all(len(grp[c]) == 4 and all(isinstance(x, (int, float)) for x in grp[c]) for c in ("body_mass",)):
            continue
        mm = st.mean(grp["body_mass"])
        for c in CANDS:
            if len(grp[c]) == 4 and all(isinstance(x, (int, float)) for x in grp[c]):
                cmn = st.mean(grp[c])
                centred[c].extend([(x - cmn) for x in grp[c]])
            else:
                centred[c].extend([None] * 4)
        mass_c.extend([x - mm for x in grp["body_mass"]])

    def residual_survival(anchor):
        """Fraction of each candidate's within-world history variation that survives
        a linear match on `anchor` (residual SD after removing the anchor)."""
        av = centred[anchor]
        out = {}
        for c in CANDS:
            if c == anchor: continue
            pairs = [(a, y) for a, y in zip(av, centred[c]) if a is not None and y is not None]
            if len(pairs) < 6: continue
            xs = [a for a, _ in pairs]; ys = [y for _, y in pairs]
            sxx = sum(x * x for x in xs)
            b = sum(x * y for x, y in pairs) / sxx if sxx > 0 else 0.0
            resid = [y - b * x for x, y in pairs]
            sd_y = st.pstdev(ys); sd_r = st.pstdev(resid)
            out[c] = {"corr_with_anchor": round(corr(xs, ys), 4),
                      "sd_history": round(sd_y, 5),
                      "sd_surviving_at_fixed_anchor": round(sd_r, 5),
                      "fraction_surviving": round(sd_r / sd_y, 4) if sd_y > 0 else None}
        return out

    surviving_core = residual_survival("core_rho_mass")   # primary Z is core-region mass
    surviving_body = residual_survival("body_mass")        # secondary reference

    ratios = []
    for (s, h), v in table.items():
        bm = v.get("body_mass"); cm = v.get("core_rho_mass")
        if isinstance(bm, (int, float)) and isinstance(cm, (int, float)) and bm > 0:
            ratios.append(cm / bm)
    ratio_stats = ({"n": len(ratios), "min": round(min(ratios), 3),
                    "median": round(st.median(ratios), 3), "max": round(max(ratios), 3)}
                   if ratios else None)

    report = {
        "schema": "KOVACS-HIDDEN-STATE-00-CANDIDATE-Z-AUDIT-v1",
        "core_region_mass_over_body_mass_ratio": ratio_stats,
        "source_dev_results": str(DEV.relative_to(REPO)),
        "source_note": "read-only audit of already-open DEV worlds 57001-57024; no engine, no new seed, no outcome selected",
        "n_complete_worlds": len(seeds),
        "candidates": {
            c: {"interpretable": CANDS[c][1], "tracker_dependent_endpoint": CANDS[c][2],
                "note": CANDS[c][3],
                "frozen_dose_contrast": summ(dose[c]),
                "per_world_span_median": round(st.median(spans[c]), 5) if spans[c] else None,
                "global_abs_range": ([round(min(absvals[c]), 4), round(max(absvals[c]), 4)] if absvals[c] else None)}
            for c in CANDS
        },
        "non_collinearity_at_fixed_core_mass": surviving_core,
        "non_collinearity_at_fixed_body_mass": surviving_body,
        "note_core_vs_body": (
            "Primary Z is core-region mass (rho over the frozen radius-10 disk), which CONTAINS but is "
            "NOT equal to the tracked focal body mass: core >= body, and in DEV core_rho_mass is ~1.3-2.4x "
            "body_mass. Non-triviality for the design is measured at fixed CORE mass; the body-mass table "
            "is a secondary reference."),
        "interpretation": (
            "Matching the primary Z (core-region mass) leaves a substantial fraction of the history-driven "
            "variation of area (body_size), shape (body_rg) and the internal memory readouts unmatched: "
            "these are hidden DOF w.r.t. the match. This is PRESENCE of hidden DOF, NOT their functional "
            "activity, which only the (Phase-1+) prospective Kovacs excursion can address."),
    }
    OUT.write_text(json.dumps(report, indent=2))
    print("n_complete_worlds:", len(seeds))
    for c in CANDS:
        cc = report["candidates"][c]
        print(f"  {c:14s} interp={cc['interpretable']} tracker_dep={cc['tracker_dependent_endpoint']} "
              f"dose|mean|={ (cc['frozen_dose_contrast'] or {}).get('abs_mean')} span~{cc['per_world_span_median']}")
    print("non-collinearity at fixed CORE mass (primary Z):")
    for c, v in surviving_core.items():
        print(f"  {c:14s} corr={v['corr_with_anchor']} frac_surviving={v['fraction_surviving']}")
    print("non-collinearity at fixed body mass (secondary ref):")
    for c, v in surviving_body.items():
        print(f"  {c:14s} corr={v['corr_with_anchor']} frac_surviving={v['fraction_surviving']}")
    print("WROTE", OUT.relative_to(REPO))

if __name__ == "__main__":
    main()
