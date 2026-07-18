"""PHASE 0 - substrate capability audit + cohort-tracer passivity report.

Determines whether the FROZEN scaffold substrate can support the phenomenon BEFORE any thresholds are
set. Emits, if warranted:
    SUBSTRATE LACKS MESOSCOPIC ENTITY
    SUBSTRATE LACKS MATERIAL TURNOVER
Material turnover is measured by a passive pulse-chase (real mass exchange), never by relabelling.
"""
from __future__ import annotations

import json
import sys

import numpy as np

from . import config as C
from . import harness as H
from . import interventions as I


def _occupancy(st) -> float:
    return float((st.rho > C.DET.threshold * C.SPEC.rho_max).mean())


def audit_seed(seed: int) -> dict:
    r: dict = {"seed": seed}
    # --- Q1 localized mesoscopic entity forms -------------------------------------------------
    st = H.warmup(seed)
    e0 = H.largest_entity(st)
    r["Q1_entity"] = None if e0 is None else {"size": int(e0.size), "rg": float(e0.rg),
                                              "mass": float(e0.mass), "n_entities": len(H.entities(st))}
    if e0 is None:
        r["entity_ok"] = False
        return r
    r["entity_ok"] = bool(e0.size >= C.DET.min_cells and e0.rg <= 8.0)

    # --- Q4 + passivity: tracer choice cannot change physics ----------------------------------
    st_norm = st.copy()                       # 32-bin frozen tracer
    st_pc = H.relabel_pulse_chase(st)         # 2-bin pulse-chase
    eng_norm = H.frozen_engine()
    eng_pc = H.pulse_chase_engine()
    a, b = st_norm, st_pc
    max_dev = 0.0
    for _ in range(200):
        a = eng_norm.step(a)
        b = eng_pc.step(b)
        for fld in ("rho", "U", "V", "c", "N", "uptake"):
            max_dev = max(max_dev, float(np.max(np.abs(getattr(a, fld) - getattr(b, fld)))))
    r["Q4_tracer_passive_max_physics_dev"] = max_dev
    r["tracer_passive"] = bool(max_dev == 0.0)

    # --- Q3/Q5 pulse-chase material turnover --------------------------------------------------
    st0 = H.relabel_pulse_chase(st)
    eng = H.pulse_chase_engine()
    cur = st0
    m_curve, lab_curve, new_curve, mass_curve = [], [], [], []
    prev = 0
    for t in C.TURNOVER_PROBE_STEPS:
        cur = H.advance(eng, cur, t - prev); prev = t
        e = H.largest_entity(cur)
        if e is None:
            m_curve.append(None); lab_curve.append(None); new_curve.append(None); mass_curve.append(None)
            continue
        lab, new = H.labelled_unlabelled(e)
        m_curve.append(H.material_continuity(e)); lab_curve.append(lab)
        new_curve.append(new); mass_curve.append(float(e.mass))
    r["Q3_M_curve"] = list(zip(C.TURNOVER_PROBE_STEPS, m_curve))
    r["Q3_labelled_leaving"] = lab_curve
    r["Q3_new_entering"] = new_curve
    r["Q3_entity_mass"] = mass_curve
    valid_m = [m for m in m_curve if m is not None]
    r["material_turnover"] = bool(len(valid_m) >= 2 and valid_m[-1] <= C.M_LOW and valid_m[0] > valid_m[-1])

    # boundary / partition dependence of M at the last probe (Q3 uncertainty)
    if H.largest_entity(cur) is not None:
        alt = {}
        for thr in (0.25, 0.30, 0.35):
            from ...substrates.scaffold.observables import SCDetectionSpec, detect
            es = detect(cur, SCDetectionSpec(threshold=thr), C.SPEC.rho_max)
            if es:
                big = max(es, key=lambda z: z.size)
                alt[thr] = H.material_continuity(big)
        r["Q3_M_partition_dependence"] = alt

    # --- Q2 stability over the whole checkpoint window ----------------------------------------
    chk = H.advance(H.pulse_chase_engine(), st0, C.CHECKPOINT)
    e_chk = H.largest_entity(chk)
    r["Q2_alive_at_checkpoint"] = bool(e_chk is not None and e_chk.size >= C.DET.min_cells)

    # --- Q6 external handles perturb without immediate destruction -----------------------------
    surv = {}
    for name, p in C.INTERVENTIONS:
        pert = I._perturb(chk if e_chk is not None else st0, p["field"], p["op"], p["amp"])
        pert = H.advance(H.pulse_chase_engine(), pert, 40)
        ep = H.largest_entity(pert)
        surv[name] = bool(ep is not None and ep.size >= C.DET.min_cells)
    r["Q6_survives_perturbation"] = surv
    r["perturbable"] = bool(all(surv.values()))

    # --- Q7 coexistence without filling grid ---------------------------------------------------
    r["Q7_occupancy_at_checkpoint"] = _occupancy(chk)
    r["Q7_n_entities_at_checkpoint"] = len(H.entities(chk))
    r["coexist_ok"] = bool(_occupancy(chk) < 0.5)

    # --- Q8 segmentation without historical tracker IDs (structural: detect uses rho only) -----
    r["Q8_segmentation_id_free"] = True  # detect() thresholds rho + periodic connected components; no IDs

    # --- Q9 internal U,V persistent + functionally relevant -----------------------------------
    if e_chk is not None:
        r["Q9_interior_heterogeneity"] = float(e_chk.phenotype[0])
        r["Q9_mean_sig"] = float(e_chk.mean_sig)
        r["internal_structured"] = bool(e_chk.phenotype[0] > 1e-4)
    else:
        r["internal_structured"] = False

    # --- Q10 recovery after a bounded perturbation --------------------------------------------
    if e_chk is not None:
        base = I._features(chk)
        pert = I._perturb(chk, "N", "mul", 0.30)
        eng2 = H.pulse_chase_engine()
        peak_dev, cur2 = 0.0, pert
        for t in range(1, C.RECOVERY_HORIZON + 1):
            cur2 = eng2.step(cur2)
            if t == C.PULSE_STEPS:
                peak_dev = float(np.linalg.norm(I._features(cur2) - base) + 1e-9)
        end_dev = float(np.linalg.norm(I._features(cur2) - base))
        r["Q10_peak_dev"] = peak_dev
        r["Q10_end_dev"] = end_dev
        r["recovery_ok"] = bool(end_dev < 0.6 * peak_dev)
    else:
        r["recovery_ok"] = False
    return r


def run(seeds=None) -> dict:
    seeds = list(C.DEV_SEEDS[:4]) if seeds is None else list(seeds)
    per = [audit_seed(s) for s in seeds]
    ok = [p for p in per if p.get("entity_ok")]

    def frac(key):
        vals = [bool(p.get(key)) for p in ok]
        return (sum(vals), len(vals))

    summary = {
        "seeds": seeds,
        "entity_forms": frac("entity_ok"),
        "tracer_passive": frac("tracer_passive"),
        "material_turnover": frac("material_turnover"),
        "alive_at_checkpoint": frac("Q2_alive_at_checkpoint"),
        "perturbable": frac("perturbable"),
        "coexist_ok": frac("coexist_ok"),
        "internal_structured": frac("internal_structured"),
        "recovery_ok": frac("recovery_ok"),
    }
    # verdict codes
    n_entity = sum(1 for p in per if p.get("entity_ok"))
    n_turn = sum(1 for p in ok if p.get("material_turnover"))
    code = "SUBSTRATE_OK"
    if n_entity == 0:
        code = "SUBSTRATE LACKS MESOSCOPIC ENTITY"
    elif n_turn == 0:
        code = "SUBSTRATE LACKS MATERIAL TURNOVER"
    summary["verdict"] = code
    return {"summary": summary, "per_seed": per}


if __name__ == "__main__":
    out = run()
    with open("results/sc_hmc/capability.json", "w") as f:
        json.dump(out, f, indent=2, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    s = out["summary"]
    print("=== PHASE 0 CAPABILITY AUDIT ===")
    for k, v in s.items():
        print(f"  {k}: {v}")
    sys.exit(0)
